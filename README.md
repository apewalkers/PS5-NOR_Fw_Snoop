# 🐍 EMC Snoop

## 📜 Description
This Python program helps you extract and analyze firmware details from `.BIN` files. It scans the firmware for a specific range of data, extracts EMC (Embedded Metadata Container) details, and stores them in a dedicated `/EMC/` directory.

## 🚀 Getting Started

To run this program, you have two options:

### 1️⃣ **Using `start.cmd`**
- Simply double-click the `start.cmd` file to run the script. 

- The script will check your system's Python version and run the main program accordingly.

### 2️⃣ **Using the Terminal**
- Open the terminal (Command Prompt or PowerShell) and run:
  
    python main.py

# 🔧 How It Works

The program scans all .BIN files in the same directory and extracts the relevant EMC details from the firmware folder. It also extracts the SLB container to the /EMC/ directory.

Example output:
> Current Working Folder: \PS5-NOR_Fw_Snoop
> 
> Scanning range: 0x82000 to 0x10fff0 (+/- 500 bytes for buffer).
> 
> File: xxxx_1216A_69GG.bin, Size: 2097152 bytes
> 
>  - Searching 0x81e0c to 0x1101e4 (582616 bytes).
> 
>    Magic pattern found at offset    0xf3fb0.
>    `01` start found at offset       0xf4000.
>    following `01`:                  0100000000000000000002000a000100
> 
>    Translated Version:              0001 000A 0002
>    HW Model:                        CFI-1216A 01Y
>    Product ID:                      PKG-1766
>    Current Firmware Version:        07.01
>    Minimum Firmware Version:        06.02
> 
>    Firmware Region MD5 Hash:        20d9914eec5ed5eaeaca084b6e5afd88
> 
>  - Saved firmware to: EMC\0001 000A 0002_0701_0602_CFI-1216A 01Y_20d9914eec5ed5eaeaca084b6e5afd88.bin


# 🔑 Requirements
Python 3.x

A working environment with .BIN files to scan and extract data from.

# 📂 Folder Structure
/EMC/ – Contains the extracted SLB container files.

/firmware/ – Your directory with the .BIN files to be processed.

# ⚠️ Troubleshooting
Python Not Installed: If Python is not found, the script will prompt you to install Python 3.x.

No .BIN Files: Ensure that .BIN files are present in the same directory for scanning.
