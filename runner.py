from py3dbp import Packer, Bin, Item, Painter
from py3dbp.constants import RotationType, Axis

import time

def pack_items(packed_items, uld):
    print(packed_items)
    # Start timing
    start = time.time()

    # Unpack ULD parameters
    uld_id, uld_l, uld_h, uld_b, uld_weight = uld

    # Initialize the packer and ULD bin
    packer = Packer()
    box = Bin(str(uld_id), (uld_l, uld_h, uld_b), uld_weight, 0, 0)  # Use ULD dimensions and weight
    packer.addBin(box)

    # Add items to the packer
    for item in packed_items[1]:
        # Unpack item attributes
        item_id, length, width, height, weight, item_type, cost = item
        
        # Add item to the packer
        packer.addItem(Item(
            partno=str(item_id),          # Use the string ID directly
            name=f'item_{item_id}',       # Descriptive name based on item ID
            typeof=item_type,             # Use the type field from the item
            WHD=(length, width, height),  # Dimensions of the item
            weight=weight,                # Weight of the item
            level=1,
            loadbear=uld_weight,
            updown=True,
            color='Yellow',
            cost=cost
        ))
    # Perform the packing operation
    packer.pack(
        bigger_first=True,
        distribute_items=False,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.50,
        number_of_decimals=0
    )

    # Assign an order to the packed items
    packer.putOrder()

    # Retrieve the packed bin
    b = packer.bins[0]

    # Initialize storage for coordinates
    coordinates_data = []

    fitted_items=[]
    pcost=0

    # Process the packed items and calculate coordinates
    for item in b.items:
        dimension = item.getDimension()
        x1, y1, z1 = item.position  # Bottom-left corner coordinates
        x2 = x1 + dimension[0]        # Top-right corner coordinates
        y2 = y1 + dimension[1]
        z2 = z1 + dimension[2]
        # Append coordinates as tuples to the list
        coordinates_data.append((float(x1), float(y1), float(z1), float(x2), float(y2), float(z2)))
        fitted_items.append((item.partno, float(item.width), float(item.height),float(item.depth),float(item.weight),item.typeof,float(item.cost)))
        
        pcost+=item.cost

    # Calculate total packed volume
    total_volume = sum([item.width * item.height * item.depth for item in b.items])

    # Display total time taken
    stop = time.time()
    print('Used time : ', stop - start)

    # Return volume and coordinates

    return [total_volume,fitted_items,coordinates_data,pcost]

# Example usage:
if __name__ == "__main__":
    # Example packed_items input
    packed_items = [
        ("P-1",99,53,55,61,"Economy",176),
        ('P-2',56,99,81,53,"Priority",10**9),
        ('P-3',42,101,51,17,"Priority",10**9)
    ]
    
    # Example ULD input
    uld = ["ULD123", 244, 318, 285, 3500]  # [uld_id, l, h, b, weight]

    result = pack_items(packed_items, uld)
    print("Volume Occupied:", result[0])
    print("Diagonal Coordinates:", result[1])
