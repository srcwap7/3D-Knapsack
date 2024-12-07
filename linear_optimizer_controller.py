from gurobipy import Model, GRB
import sys
import pprint
import random
from runner import pack_items
import math
import csv
import re


def calculate_lbh(packed_items):
    lbh_data = []
    for item in packed_items:
        x1, y1, z1, x2, y2, z2 = item
        L = abs(x2 - x1)
        B = abs(y2 - y1)
        H = abs(z2 - z1)
        lbh_data.append((L, B, H))
    return lbh_data

def standardize(values):
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)
    return [(x - mean) / std_dev if std_dev != 0 else 0 for x in values]

def solve_packing(items, box_length, box_width, box_height, box_weight_limit):
    model = Model("3D_Packing")
    cost=0
    n = len(items)
    # Binary variables indicating if an item is selected
    S = model.addVars(n, vtype=GRB.BINARY, name="S")

    # Continuous variables for coordinates and rotated dimensions
    X = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_length, name="X")
    Y = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_width, name="Y")
    Z = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_height, name="Z")
    X_r = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_length, name="X_r")
    Y_r = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_width, name="Y_r")
    Z_r = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_height, name="Z_r")

    # Rotation matrix variables
    T = model.addVars(n, 3, 3, vtype=GRB.BINARY, name="T")

    # Add constraints for the rotation matrix
    for i in range(n):
        for j in range(3):
            model.addConstr(T.sum(i, j, '*') == S[i], f"Row_{i}_{j}")
            model.addConstr(T.sum(i, '*', j) == S[i], f"Col_{i}_{j}")
        # Link rotated dimensions with rotation matrix and coordinates
        model.addConstr(X_r[i] == X[i] + T[i, 0, 0] * items[i][1] +
                                    T[i, 0, 1] * items[i][2] +
                                    T[i, 0, 2] * items[i][3])
        model.addConstr(Y_r[i] == Y[i] + T[i, 1, 0] * items[i][1] +
                                    T[i, 1, 1] * items[i][2] +
                                    T[i, 1, 2] * items[i][3])
        model.addConstr(Z_r[i] == Z[i] + T[i, 2, 0] * items[i][1] +
                                    T[i, 2, 1] * items[i][2] +
                                    T[i, 2, 2] * items[i][3])

        # Enforce boundary constraints
        model.addConstr(X_r[i] <= box_length * S[i])
        model.addConstr(Y_r[i] <= box_width * S[i])
        model.addConstr(Z_r[i] <= box_height * S[i])

    # Add non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            L = model.addVar(vtype=GRB.BINARY, name=f"L_{i}_{j}")
            R = model.addVar(vtype=GRB.BINARY, name=f"R_{i}_{j}")
            F = model.addVar(vtype=GRB.BINARY, name=f"F_{i}_{j}")
            B = model.addVar(vtype=GRB.BINARY, name=f"B_{i}_{j}")
            U = model.addVar(vtype=GRB.BINARY, name=f"U_{i}_{j}")
            O = model.addVar(vtype=GRB.BINARY, name=f"O_{i}_{j}")

            model.addConstr(L + R + F + B + U + O >= S[i] + S[j] - 1)

            model.addConstr(X_r[i] <= X[j] + box_length * (1 - L))
            model.addConstr(X_r[j] <= X[i] + box_length * (1 - R))
            model.addConstr(Y_r[i] <= Y[j] + box_width * (1 - F))
            model.addConstr(Y_r[j] <= Y[i] + box_width * (1 - B))
            model.addConstr(Z_r[i] <= Z[j] + box_height * (1 - U))
            model.addConstr(Z_r[j] <= Z[i] + box_height * (1 - O))

    # Weight constraint
    model.addConstr(sum(S[i] * items[i][3] for i in range(n)) <= box_weight_limit)

    # Objective: Maximize the number of items packed
    model.setObjective(sum(S[i] for i in range(n)), GRB.MAXIMIZE)

    model.setParam('TimeLimit',30)

    # Solve the model
    model.optimize()

    # Save results to CSV
    packed_items = []
    total_volume = 0

    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        for i in range(n):
            if S[i].x > 0.5:
                x_start = X[i].x
                y_start = Y[i].x
                z_start = Z[i].x
                x_end = X_r[i].x
                y_end = Y_r[i].x
                z_end = Z_r[i].x
                cost+=10**9
                
                # Calculate the volume of the item
                item_volume = (x_end-x_start) * (y_end-y_start) * (z_end-z_start)
                total_volume += item_volume

                # Add the packed item to the list with ID, dimensions, weight, and cost
                packed_items.append((
                    items[i][0],  # ID
                    items[i][1],  # Length
                    items[i][2],   # Width
                    items[i][3],  # Height
                    items[i][4],  # Weight
                    items[i][5],  # Item type
                    items[i][6]   # Item cost
                ))

    # Return total volume and packed items list
    return [total_volume, packed_items,cost]

def solve_economy_packing(items, box_length, box_width, box_height, box_weight_limit):
    model = Model("3D_Packing")

    n = len(items)
    # Binary variables indicating if an item is selected
    S = model.addVars(n, vtype=GRB.BINARY, name="S")

    # Continuous variables for coordinates and rotated dimensions
    X = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_length, name="X")
    Y = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_width, name="Y")
    Z = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_height, name="Z")
    X_r = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_length, name="X_r")
    Y_r = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_width, name="Y_r")
    Z_r = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=box_height, name="Z_r")

    # Rotation matrix variables
    T = model.addVars(n, 3, 3, vtype=GRB.BINARY, name="T")

    # Add constraints for the rotation matrix
    for i in range(n):
        for j in range(3):
            model.addConstr(T.sum(i, j, '*') == S[i], f"Row_{i}_{j}")
            model.addConstr(T.sum(i, '*', j) == S[i], f"Col_{i}_{j}")
        
        # Link rotated dimensions with rotation matrix and coordinates
        model.addConstr(X_r[i] == X[i] + T[i, 0, 0] * items[i][1] +
                                     T[i, 0, 1] * items[i][2] +
                                     T[i, 0, 2] * items[i][3])
        model.addConstr(Y_r[i] == Y[i] + T[i, 1, 0] * items[i][1] +
                                     T[i, 1, 1] * items[i][2] +
                                     T[i, 1, 2] * items[i][3])
        model.addConstr(Z_r[i] == Z[i] + T[i, 2, 0] * items[i][1] +
                                     T[i, 2, 1] * items[i][2] +
                                     T[i, 2, 2] * items[i][3])

        # Enforce boundary constraints
        model.addConstr(X_r[i] <= box_length * S[i])
        model.addConstr(Y_r[i] <= box_width * S[i])
        model.addConstr(Z_r[i] <= box_height * S[i])

    # Add non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            L = model.addVar(vtype=GRB.BINARY, name=f"L_{i}_{j}")
            R = model.addVar(vtype=GRB.BINARY, name=f"R_{i}_{j}")
            F = model.addVar(vtype=GRB.BINARY, name=f"F_{i}_{j}")
            B = model.addVar(vtype=GRB.BINARY, name=f"B_{i}_{j}")
            U = model.addVar(vtype=GRB.BINARY, name=f"U_{i}_{j}")
            O = model.addVar(vtype=GRB.BINARY, name=f"O_{i}_{j}")

            model.addConstr(L + R + F + B + U + O >= S[i] + S[j] - 1)

            model.addConstr(X_r[i] <= X[j] + box_length * (1 - L))
            model.addConstr(X_r[j] <= X[i] + box_length * (1 - R))
            model.addConstr(Y_r[i] <= Y[j] + box_width * (1 - F))
            model.addConstr(Y_r[j] <= Y[i] + box_width * (1 - B))
            model.addConstr(Z_r[i] <= Z[j] + box_height * (1 - U))
            model.addConstr(Z_r[j] <= Z[i] + box_height * (1 - O))

    # Weight constraint
    model.addConstr(sum(S[i] * items[i][3] for i in range(n)) <= box_weight_limit)

    # Objective: Maximize the number of items packed
    model.setObjective(sum(S[i]*items[i][6] for i in range(n)), GRB.MAXIMIZE)

    model.setParam('TimeLimit',120)

    # Solve the model
    model.optimize()

    packed_items = []
    total_volume = 0
    cost=0

    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        for i in range(n):
            if S[i].x > 0.5:
                x_start = X[i].x
                y_start = Y[i].x
                z_start = Z[i].x
                x_end = X_r[i].x
                y_end = Y_r[i].x
                z_end = Z_r[i].x

                cost+=items[i][6]
        
                # Calculate the dimensions of the item in the packed position
                # Calculate the volume of the item
                item_volume = (x_end-x_start) * (y_end-y_start) * (z_end-z_start)
                total_volume += item_volume

                # Add the packed item to the list with ID, dimensions, weight, and cost
                packed_items.append((
                    items[i][0],  # ID
                    items[i][1],  # Length
                    items[i][2],   # Width
                    items[i][3],  # Height
                    items[i][4],  # Weight
                    items[i][5],  # Item Type
                    items[i][6]   # cost
                ))

    # Save results to CSV
    with open("packed_items.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["ID", "Length", "Width", "Height", "Weight", "Value", "Cost"])  # Header row
        for item in packed_items:
            csvwriter.writerow(item)

    print("Results saved to packed_items.csv")

    # Return total volume and packed items list
    return [total_volume, packed_items,cost]

        
def find_average(items,box):
    sum1=sum2=sum3=sum4=0
    n=len(items)
    for i in range(n):
        sum1+=items[i][0]
        sum2+=items[i][1]
        sum3+=items[i][2]
        sum4+=items[i][3]
    avg1=sum1/n
    avg2=sum2/n
    avg3=sum3/n
    avg4=sum4/n
    volexpected=avg1*avg2*avg3
    boxvol=box[0]*box[1]*box[2]
    print(boxvol/volexpected)
    
def find_metric(items,box):
    volsum=0
    n=len(items)
    for i in range(n):
        volsum+=(items[i][0]*items[i][1]*items[i][2])
    avg=volsum/n
    boxvol=box[0]*box[1]*box[2]
    print(boxvol/avg)
    
def find_weight(items,box):
    weight=0
    n=len(items)
    for i in range(n):
        weight+=items[i][3]
    avg=weight/n
    print(box[3]/avg)
    
    
def main():
    priority_items = []
    sorted_economy_items = []
    uld_list = []
    file_path = "data_file.csv"  # Replace with your file path
    pattern = r"^\s*K\s*=\s*(-?\d+)\s*$"
    # Reading data from the file
    k=0
    data_map={}
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        economy_items = []
        flag=True
        for row in reader:
            if (flag):
                for cell in row:  # Process each cell in the row
                    match = re.search(pattern, cell)
                    if match:
                        k = int(match.group(1))
                        flag=False

            if row[0].startswith("U"):  # ULD data
                uld_list.append([  # Bins as array of arrays
                    row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4])
                ])
            elif row[0].startswith("P"):  # Parcel data
                parcel = (
                    row[0],  # ID
                    int(row[1]),  # Length
                    int(row[2]),  # Width
                    int(row[3]),  # Height
                    int(row[4]),  # Weight
                    row[5],  # Type
                    int(row[6]) if row[6] != "-" else 10**9  # Cost
                )
                if parcel[5] == "Priority":  # Type is Priority
                    priority_items.append(parcel)
                    data_map[row[0]]=[row[1],int(row[2]),int(row[3]),int(row[4]),row[5],10**9]
                elif parcel[5] == "Economy":  # Type is Economy
                    economy_items.append(parcel)
                    data_map[row[0]]=[row[1],int(row[2]),int(row[3]),int(row[4]),row[5],int(row[6])]


    # Extract parameters for standardization
    volumes = [item[1] * item[2] * item[3] for item in economy_items]
    diagonals = [math.sqrt(item[1]**2 + item[2]**2 + item[3]**2) for item in economy_items]
    weights = [item[4] for item in economy_items]
    costs = [1/(item[6]) for item in economy_items]

    # Standardize parameters
    standardized_volumes = standardize(volumes)
    standardized_diagonals = standardize(diagonals)
    standardized_weights = standardize(weights)
    standardized_costs = standardize(costs)

    # Compute the composite metric
    items_with_metric = []
    for i, item in enumerate(economy_items):
        composite_metric = (
            standardized_volumes[i]
            + standardized_diagonals[i]
            + standardized_weights[i]
            + standardized_costs[i]
        ) / 4
        items_with_metric.append((composite_metric, item))

    # Sort by the composite metric
    items_with_metric.sort(key=lambda x: x[0],reverse=True)

    # Remove the metric and keep only the original items
    sorted_economy_items = [item for _, item in items_with_metric]

    uld_volumes=[uld_list[i][1]*uld_list[i][2]*uld_list[i][3] for i in range(len(uld_list))]
    uld_diagonals=[math.sqrt(uld_list[i][1]**2+uld_list[i][2]**2+uld_list[i][3]**2) for i in range(len(uld_list))]
    uld_weights=[uld_list[i][4] for i in range(len(uld_list))]

    standardized_uld_volumes = standardize(uld_volumes)
    standardized_uld_diagonals = standardize(uld_diagonals)
    standardized_uld_weights = standardize(uld_weights)

    # Compute the composite metric

    uld_items_with_metric = []
    for i, item in enumerate(uld_list):
        composite_metric = (
            standardized_uld_volumes[i]
            + standardized_uld_diagonals[i]
            + standardized_uld_weights[i]
        ) / 3
        uld_items_with_metric.append((composite_metric, item))
    
    uld_items_with_metric.sort(key=lambda x: x[0],reverse=True)

    uld_list = [item for _, item in uld_items_with_metric]


    print(uld_items_with_metric)



    i = 0
    incurred_cost=0

    packed_data = {}
    bin_cost={}

    n_p=0

    while (priority_items and i<len(uld_list)):
        n_p+=1
        incurred_cost+=k
        current_bin=i
        current_bin_volume=uld_list[current_bin][1]*uld_list[current_bin][2]*uld_list[current_bin][3]
        temp_items=solve_packing(priority_items,uld_list[current_bin][1],uld_list[current_bin][2],uld_list[current_bin][3],uld_list[current_bin][4])
        packed_items=pack_items([0,temp_items[1]],uld_list[current_bin])
        item_list=[]
        for key in packed_items[1]:
            item_list.append(key)
        volume=packed_items[0]
        cost=packed_items[3]
        cwnd=1
        previous_packing=packed_items[1]
        while (volume<0.80*current_bin_volume):
            # STILL VOLUME IS LEFT IN THE BOX
            cwnd = cwnd * 2
            last_items = sorted_economy_items[-cwnd:]
            item_list.extend(last_items)
            new_packing = pack_items([0, item_list], uld_list[current_bin])
        
            new_volume = new_packing[0]
            new_cost=new_packing[3]
            
            if new_cost > cost:
                packed_items = new_packing
                volume = new_volume
                cost=new_cost
            else:
                break            
            for item in last_items:
                item_list.remove(item)  
        window_size = 0
        ack_count=0
        item_list=[]
        for item in packed_items[1]:
            item_list.append(item)
        
        packed_ids = {item[0] for item in packed_items[1]}
        dropout=[]
        for element in previous_packing:
            if element[0] not in packed_ids:
                dropout.append(element)
        sorted_economy_items.extend(dropout)
        sorted_economy_items = [item for item in sorted_economy_items if item[0] not in packed_ids]

        previous_packing=packed_items[1]

        while (ack_count<5):
            window_size+=1
            last_items = sorted_economy_items[-window_size:]
            item_list.extend(last_items)
            new_packing = pack_items([0, item_list], uld_list[current_bin])
            new_volume = new_packing[0]
            new_cost=new_packing[3]
            if new_cost > cost:
                packed_items = new_packing
                volume = new_volume
                cost=new_cost
                ack_count=0
            else:
                ack_count+=1
            for item in last_items:
                item_list.remove(item)  

        packed_ids={item[0] for item in packed_items[1]}
        dropout=[]
        
        for element in previous_packing:
            if element[0] not in packed_ids:
                dropout.append(element)

        sorted_economy_items.extend(dropout)
        sorted_economy_items = [item for item in sorted_economy_items if item[0] not in packed_ids]


        volume_percentage=volume/current_bin_volume * 100
        with open("outputlog.txt","a") as f:
            f.write(f"Volume Percentage: {volume_percentage}%\n")

        for j in range(len(packed_items[1])):
            key = current_bin 
            value = [
                packed_items[1][j][0],  
                packed_items[1][j][5],  
                packed_items[2][j][0], 
                packed_items[2][j][1],  
                packed_items[2][j][2],  
                packed_items[2][j][3],
                packed_items[2][j][4],
                packed_items[2][j][5]
            ]
            if key not in packed_data:
                packed_data[key] = []
            packed_data[key].append(value)
        priority_items = [item for item in priority_items if item[0] not in packed_ids]  
        bin_cost[current_bin]=cost
        i+=1

    
    if (sorted_economy_items):
        for j in range(i,len(uld_list)):
            current_bin=j
            current_bin_volume=uld_list[current_bin][1]*uld_list[current_bin][2]*uld_list[current_bin][3]
            temp_items=solve_economy_packing(sorted_economy_items,uld_list[current_bin][1],uld_list[current_bin][2],uld_list[current_bin][3],uld_list[current_bin][4])
            packed_items=pack_items([0,temp_items[1]],uld_list[current_bin])
            item_list=[]
            for key in packed_items[1]:
                item_list.append(key)
            volume=packed_items[0]
            cost=packed_items[3]
            cwnd=1
            prev_sorted=sorted_economy_items
            sorted_economy_items=[items for items in sorted_economy_items if items not in packed_items[1]]



            while (volume<0.80*current_bin_volume):
                # STILL VOLUME IS LEFT IN THE BOX
                cwnd = cwnd * 2
                last_items = sorted_economy_items[-cwnd:]

                item_list.extend(last_items)
                new_packing = pack_items([0, item_list], uld_list[current_bin]) 
                print(item_list)


                new_volume = new_packing[0]
                new_cost=new_packing[3]

                if new_cost >= cost:
                    packed_items = new_packing
                    volume = new_volume
                    cost=new_cost
                else:
                    break

                for item in last_items:
                    item_list.remove(item) 


            window_size = 0
            ack_count=0
            item_list=[]
            for item in packed_items[1]:
                item_list.append(item)

            packed_ids = {item[0] for item in packed_items[1]}
            prev_temp=prev_sorted
            prev_sorted = [item for item in prev_sorted if item[0] not in packed_ids]


            while (ack_count<5):
                window_size+=1
                last_items = prev_sorted[-window_size:]
                item_list.extend(last_items)
                new_packing = pack_items([0, item_list], uld_list[current_bin])
                new_volume = new_packing[0]
                new_cost=new_packing[3]
                if new_cost > cost:
                    packed_items = new_packing
                    volume = new_volume
                    cost=new_cost
                    ack_count=0
                else:
                    ack_count+=1
                for item in last_items:
                    item_list.remove(item)  

            packed_ids={item[0] for item in packed_items[1]}
            prev_temp = [item for item in prev_temp if item[0] not in packed_ids]
            sorted_economy_items = prev_temp
            volume_percentage=volume/current_bin_volume * 100
            bin_cost[current_bin]=cost

            with open("outputlog.txt","a") as f:
                f.write(f"Volume Percentage: {volume_percentage}%\n")

            for j in range(len(packed_items[1])):
                key = current_bin  
                value = [
                    packed_items[1][j][0],  
                    packed_items[1][j][5], 
                    packed_items[2][j][0],  
                    packed_items[2][j][1],  
                    packed_items[2][j][2],  
                    packed_items[2][j][3],
                    packed_items[2][j][4],
                    packed_items[2][j][5]
                ]
                if key not in packed_data:
                    packed_data[key] = []
                packed_data[key].append(value)

    
    
    print("Simulated Annealing Phase")
    total_packed_cost=0
    for key in bin_cost:
        total_packed_cost+=bin_cost[key]
    initial_temp=10000
    final_temp=0.001
    cooling_rate=0.96
    temperature=initial_temp
    curr_cost=total_packed_cost
    MAX_EXPONENT = -700
    pprint.pprint(packed_data)

    print("sorted economy items")

    print(len(sorted_economy_items))
    
    cost_arr=[curr_cost]
    while (temperature > final_temp and sorted_economy_items):
        element=random.choice(sorted_economy_items)
        print("***********************Selected ELement*********************************")
        print(element)
        new_packing=[]
        flag=False
        best_bin=5
        new_total_cost=0
        best_till_now=0
        for j in range(len(uld_list)):
            current_bin=j
            total_items=[]
            for item in packed_data[current_bin]:
                it=item[0]
                data=[it,data_map[it][0],data_map[it][1],data_map[it][2],data_map[it][3],data_map[it][4],data_map[it][5]]
                total_items.append(data)
            total_items.append(element)


            packed_items=pack_items([0,total_items],uld_list[current_bin])
            new_cost=packed_items[3]
            
            modified_data = [
                [item1[0], item1[5], item2[0], item2[1], item2[2], item2[3], item2[4], item2[5] ]
                for item1, item2 in zip(packed_items[1], packed_items[2]) 
            ]
            
            pprint.pprint(modified_data)

            if (best_till_now < new_cost):
                best_bin=current_bin
                best_till_now=new_cost
                new_packing=modified_data

        new_total_cost=curr_cost-bin_cost[best_bin]+best_till_now

        cost_arr.append(new_total_cost)

        if (new_total_cost>curr_cost):
            #ACCEPT THE SOLUTION 
            print("**************************************************Got a better pick*****************************************")

            previously_packed_ids=[]
            for items in packed_data[best_bin]:
                previously_packed_ids.append(items[0])
            newly_packed_ids=[]
            for items in new_packing:
                newly_packed_ids.append(items[0])
            dropout=[]
            for items in previously_packed_ids:
                if items not in newly_packed_ids:
                    dropout.append([items,data_map[items][0],data_map[items][1],data_map[items][2],data_map[items][3],data_map[items][4],data_map[items][5]])
            packed_data[best_bin]=new_packing
            bin_cost[best_bin]=best_till_now
            if (element[0] in newly_packed_ids):
                sorted_economy_items.remove(element)
            sorted_economy_items.extend(dropout)
            tot=0
            for key in packed_data:
                tot+=len(packed_data[key])
            packed=tot
            tot+=len(sorted_economy_items)
            unpacked=tot-packed
            if (tot!=400):
                print("Termination")
                print("***************Unequal number of elements*********************")
                print("Packed Items",packed)
                print("Unpacked Items",unpacked)
                print("Current iteration for element:-",element)
                print("Currently in bin no ",best_bin)
                print("Previously packed".previously_packed_ids)
                print([items[0] for items in dropout])
                print([items[0] for items in packed_data[best_bin]])
                break
            curr_cost=new_total_cost

        
        
        elif (random.random() < math.exp(max((new_total_cost-curr_cost),MAX_EXPONENT) / temperature) and abs(curr_cost-new_total_cost)<10**4):
            #ACCEPT THE SOLUTION
            previously_packed_ids=[]
            for items in packed_data[best_bin]:
                previously_packed_ids.append(items[0])
            newly_packed_ids=[]
            for items in new_packing:
                newly_packed_ids.append(items[0])
            dropout=[]
            for items in previously_packed_ids:
                if items not in newly_packed_ids:
                    dropout.append([items,data_map[items][0],data_map[items][1],data_map[items][2],data_map[items][3],data_map[items][4],data_map[items][5]])
            packed_data[best_bin]=new_packing
            bin_cost[best_bin]=best_till_now
            if (element[0] in newly_packed_ids):
                sorted_economy_items.remove(element)
            sorted_economy_items.extend(dropout)
            curr_cost=new_total_cost
            tot=0
            for key in packed_data:
                tot+=len(packed_data[key])
            tot+=len(sorted_economy_items)
            if (tot!=400):
                print("Termination")
                print("***************Unequal number of elements*********************")
                print("Packed Items",packed)
                print("Unpacked Items",unpacked)
                print("Current iteration for element:-",element)
                print("Currently in bin no ",best_bin)
                print("Previously packed",previously_packed_ids)
                print([items[0] for items in dropout])
                print([items[0] for items in packed_data[best_bin]])
                break
        temperature *= cooling_rate
    
    
    
    
            

    

    for items in sorted_economy_items:
        incurred_cost+=items[6]

    
    start=True
    with open("packed_item.csv", "a", newline="") as packed_file:
        packed_writer = csv.writer(packed_file)
        if (start):
            packed_writer.writerow(["Total cost incurred : " ,incurred_cost])
            packed_writer.writerow(["Number of containers with priority items : " ,n_p])
            start=False
        for key, values in packed_data.items():
            for value in values:
                packed_writer.writerow(value + [uld_items_with_metric[key][1][0]])  
        for item in sorted_economy_items:
            packed_writer.writerow([item[0],"None",-1,-1,-1,-1,-1,-1])


    print("***************************************Cost Array**********************************************")
    print(cost)
    print("**************************************Processing Complete**************************************")
    print("Total Cost incurred:",incurred_cost)
    print ("Output saved to packed_items.csv")

    
if __name__ == "__main__":
    main()


