# Fedex
# Setup for the code
#############SOME EXPLANATION#############

The setup can be done as follows. Feel free to skip sections if needed.

## [Windows Setup](#windows-setup)

  - [Python Setup](#python-setup)
    - [Python Installation](#python-installation)
    - [Setting up the Python Environment](#setting-up-the-python-environment)
    - [Requirement.txt](#requirementtxt)
  - [Gurobi Setup](#gurobi-setup)
  - [FFMPEG package download](#ffmpeg-package-download)
  - [Code execution](#code-execution)

## [Linux Setup](#linux-setup)
  - [Downloding important packages](#Downloading-the-important-packages)
  - [Setting up the Python Environment](#setting-up-the-python-environment-1)
    - [Setting up the requirement](#Setting-up-the-requirement)
  - [Gurobi Setup](#gurobi-setup-1)
  - [Code execution](#code-execution-1)

## Windows Setup

  - Python Setup
    - Python Installation
     To begin, you need to have Python installed on your Windows system. Follow these steps:

    1. **Download Python**
   - Visit the official Python website: https://www.python.org/downloads/
   - Download the latest version of Python for Windows.
   
    2. **Install Python**
   - Run the installer and make sure to check the box **"Add Python to PATH"** during the installation process.
   - Complete the installation by following the on-screen instructions.

    3. **Verify Python Installation**
   - Open the Command Prompt (`cmd`) and verify the installation by running:
     ```bash
     python --version
     ```
   - You should see the Python version printed in the terminal, indicating a successful installation.

  - ### Setting up the Python Environment

  1. **Create a Virtual Environment**
   It’s recommended to create a virtual environment to manage your project dependencies separately.
    Open the Command Prompt and navigate to your project folder:
     ```bash
     cd path\to\your\project
     ```
    Run the following command to create a virtual environment:
     ```bash
     python -m venv venv
     ```

  2. **Activate the Virtual Environment**
   After creating the virtual environment, activate it by running:
   ```bash
   venv\Scripts\activate
   ```
    - Requirement.txt
    ```bash
    pip install -r requirements.txt
    ```

- ## Gurobi Setup
  Please refer to the following links https://www.youtube.com/watch?v=z7t0p5J9YcQ
- ### FFMPEG package download


FFmpeg is a powerful multimedia framework for handling video, audio, and other multimedia files and streams. This guide will walk you through the steps to download and install FFmpeg on Windows.

## Prerequisites

- A Windows computer (Windows 7 or later is recommended)
- Internet connection

## Steps to Download and Install FFmpeg on Windows

### Step 1: Download FFmpeg

1. Visit the official FFmpeg website:  
   [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

2. Under the **Windows** section, click on the link for **Windows builds by BtbN** (or any other available source like **Gyan.dev**).

3. You will be redirected to a page with download options. Choose the appropriate build based on your system architecture (usually, **"ffmpeg-release-essentials"** is a good option).

4. Click the download link for the latest version to start the download. It will be a ZIP file (e.g., `ffmpeg-<version>-essentials_build.zip`).

### Step 2: Extract FFmpeg

1. Once the download is complete, navigate to the folder where the ZIP file is saved.

2. Right-click the ZIP file and select **Extract All...** to extract the contents to a location of your choice.

3. After extraction, you should have a folder with FFmpeg executables (`ffmpeg.exe`, `ffplay.exe`, and `ffprop.exe`).

### Step 3: Add FFmpeg to System PATH

To use FFmpeg from the command line, you need to add it to the system `PATH`.

1. Open **File Explorer** and navigate to the folder where you extracted FFmpeg.

2. Copy the path to the `bin` folder (e.g., `C:\ffmpeg\bin`).

3. Press `Win + X` and select **System**.

4. Click **Advanced system settings** on the left sidebar.

5. In the **System Properties** window, click the **Environment Variables...** button.

6. Under **System variables**, scroll down and find the `Path` variable. Select it and click **Edit...**.

7. In the **Edit Environment Variable** window, click **New** and paste the copied path to the `bin` folder (e.g., `C:\ffmpeg\bin`).

8. Click **OK** to save the changes.

### Step 4: Verify Installation

1. Open **Command Prompt** (press `Win + R`, type `cmd`, and press Enter).

2. Type the following command and press Enter:

   ```bash
   ffmpeg -version
   ```

- ### Code execution
Give the input file in following format shown in the picture below (only shown top 3 rows)

You need to give the either of two input arguement True or False to file linear_optimizer_controller.py for stablitiy default is considered to be false
```bash
K=5000
U1,224,318,162,2500
U2,224,318,162,2500
U3,244,318,244,2800
U4,244,318,244,2800
U5,244,318,285,3500
U6,244,318,285,3500
P-1,99,53,55,61,Economy,176
P-2,56,99,81,53,Priority,-
P-3,42,101,51,17,Priority,-
P-4,108,75,56,73,Economy,138
P-5,88,58,64,93,Economy,139
```
For Stablity=True
```bash
python3 linear_optimizer_controller.py True
```
For Stablity=False
```bash
python3 linear_optimizer_controller.py False
```

## Linux Setup
  - ### Downloding important packages
      
      ##### For Ubuntu
       ```bash
       sudo apt update
       sudo apt install python3 ffmpeg
       ```
      ##### For Fedora
      ```bash
       sudo dnf update
       sudo dnf install python3 ffmpeg
       ```
      ##### For Arch
      ```bash
       sudo pacman -Syu
       sudo pacman -S python3 ffmpeg
       ```
       You can check if the python install properly by typing the folling command
       ```bash
       python3 --version
       ```

- ### Setting up the Python Environment
    Locate to the folder where source folder is located
    ##### Linux
    ```bash
    virtualenv venv
    source venv/bin/activate
    ```


  - ### Setting up the requirement
    Locate to the folder where source code is their
      ```bash
      pip install -r requirement.txt
      ```

- ### Gurobi Setup
    NOTE :- Download the version 11.0.2 and place the file in which gurobi is installed
    You can also follow the youtube video by offical youtube channel of gurobi https://youtu.be/OYuOKXPJ5PI?si=hiixS1Pi_mqVBulR

    1. Register yourself at https://www.gurobi.com/ with your institute mail ID.
    2. Once logged in, click on Downloads and Licenses at the top. Under Download the Latest Version of Gurobi, click on Gurobi Optimizer.
    3. Scroll down to Current Version and download the appropriate version.
    4. In Linux, you will have downloaded a tar.gz file. Move this file to a folder where you want to install Gurobi. You can move it to /opt for a shared installation across users otherwise, your home directory should also work.
    5. Unzip the file by running the following command - tar xvfz gurobi\<version\>_linux64.tar.gz
    6. This will extract the contents into a new directory named by the Gurobi version, which will contain a sub-directory named linux64 (assuming you have x64 Linux). The full path to the linux64 directory is your \<install-dir\>.
    7. Open your .bashrc file (ls -a in your home directory, and you will find it) in any text editor and add the following lines at the end.
    ```bash
    export GUROBI_HOME=<install-dir>
    export PATH=$GUROBI_HOME/bin:$PATH
    export LD_LIBRARY_PATH=$"{LD_LIBRARY_PATH}:${GUROBI_HOME}/lib

    ```
    8. You need to restart the terminal after you make changes in the .bashrc file for the changes to take effect. Alternatively, you can run the command source ~/.bashrc to allow the changes to become active without needing to restart the terminal. (By restart, I mean, close and relaunch the terminal)
    9. The next step is to create a license. Go back to the Downloads and Licenses page. Scroll down to the Access your Licenses section and click on Your Gurobi Licenses. This will take you to a page listing all your licenses.
    10. On the left, click on Request and choose Named-User Academic and click Generate Now. This should generate the license and give you a grbgetkey command with your specific license details. Names-User Academic licenses are valid for 1 year. You can generate a new license when this one expires if you need to.
    11. Copy this command and run it in the terminal. It will ask for a location to store your license. It is recommended to accept the default location, but in case you want to store it anywhere else, you can do so and then add another line to your .bashrc file which specifies the location.
    ```bash
    export GRB_LICENSE_FILE=<License-File-Location>
    ```
    12. Gurobi should work now. You can test it by running the command gurobi_cl --version
    Some sources in case you are facing any issues
    - https://support.gurobi.com/hc/en-us/articles/4534161999889-How-do-I-install-Gurobi-Optimizer
    - https://support.gurobi.com/hc/en-us/articles/13207658935185-How-do-I-retrieve-an-Academic-Named-User-license
    - https://support.gurobi.com/hc/en-us/articles/360047265972-grbgetkey-command-not-found



- ### Code execution
Give the input file in following format shown in the picture below (only shown top 3 rows)

You need to give the either of two input arguement True or False to file linear_optimizer_controller.py for stablitiy default is considered to be false
```bash
K=5000
U1,224,318,162,2500
U2,224,318,162,2500
U3,244,318,244,2800
U4,244,318,244,2800
U5,244,318,285,3500
U6,244,318,285,3500
P-1,99,53,55,61,Economy,176
P-2,56,99,81,53,Priority,-
P-3,42,101,51,17,Priority,-
P-4,108,75,56,73,Economy,138
P-5,88,58,64,93,Economy,139
```
For Stablity=True
```bash
python3 linear_optimizer_controller.py True
```
For Stablity=False
```bash
python3 linear_optimizer_controller.py False
```
