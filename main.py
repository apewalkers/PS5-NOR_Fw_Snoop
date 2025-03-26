import os
import hashlib

DEFAULT_START_OFFSET = 0x82000  
DEFAULT_END_OFFSET = 0x10FFF0  
SEARCH_PATTERN = b'\x00' * 80 + b'\x01'  
SEARCH_BUFFER = 500  
BYTES_AFTER_MARKER = 16  

HW_MODEL_OFFSET = 0x1C7230
PRODUCT_ID_OFFSET = 0x1C73E0
CURRENT_FW_OFFSET = 0x1C8C30
MIN_FW_OFFSET = 0x1C8C20
FIRMWARE_REGION_OFFSET = 0x4000  
FIRMWARE_REGION_SIZE = 0x62E00  

LOG_FILE = 'scan_log.txt'

EXPECTED_HEADER = b'\x53\x4F\x4E\x59\x20\x43\x4F\x4D\x50\x55\x54\x45\x52\x20\x45\x4E' \
                  b'\x54\x45\x52\x54\x41\x49\x4E\x4D\x45\x4E\x54\x20\x49\x4E\x43\x2E'

def translate_version(hex_data):
    if len(hex_data) >= 16:  
        reversed_data = hex_data[::-1]

        major = int.from_bytes(reversed_data[0:2], byteorder='big')  
        minor = int.from_bytes(reversed_data[2:4], byteorder='big')  
        build = int.from_bytes(reversed_data[4:6], byteorder='big')  

        return f"{major:04X} {minor:04X} {build:04X}"
    else:
        return "(Invalid version data)"

def extract_string(file, offset, length):
    file.seek(offset)
    string_bytes = file.read(length)
    return string_bytes.decode('utf-8', errors='ignore').strip('\x00')

def extract_firmware_version(file, offset, length):
    file.seek(offset)
    firmware_bytes = file.read(length)
    
    hex_string = ''.join([f'{b:02X}' for b in firmware_bytes[::-1]]) 
    if len(hex_string) >= 4:
        major_version = int(hex_string[:2], 16)
        minor_version = int(hex_string[2:4], 16)
        return f"{major_version:02X}.{minor_version:02X}"
    return "(Invalid firmware version)"

def compute_firmware_region_md5(file_path):
    with open(file_path, 'rb') as f:
        f.seek(FIRMWARE_REGION_OFFSET)
        firmware_region_bytes = f.read(FIRMWARE_REGION_SIZE)

        md5_hash = hashlib.md5(firmware_region_bytes).hexdigest()
        return md5_hash

def check_for_header(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read(len(EXPECTED_HEADER))
        return file_data == EXPECTED_HEADER

def save_firmware_to_emc(firmware_data, file_name):
    emc_folder = "EMC"
    if not os.path.exists(emc_folder):
        os.makedirs(emc_folder)

    file_path = os.path.join(emc_folder, file_name)

    if os.path.exists(file_path):
        print(f" - {file_path} already exists. Skipping...\n")
        return False

    with open(file_path, 'wb') as f:
        f.write(firmware_data)
        print(f" - Saved firmware to: {file_path}\n")
    return True

def scan_bin_file(file_path, start_offset, end_offset, pattern):
    file_size = os.path.getsize(file_path)
    print(f"File: {file_path}, Size: {file_size} bytes\n")

    if not check_for_header(file_path):
        print(" - Header not found in this file. Skipping...\n")
        return

    with open(file_path, 'rb') as f:
        if file_size < start_offset:  
            print(" - File is too small for the given offset range. Skipping...\n")
            return

        adjusted_start_offset = max(0, start_offset - SEARCH_BUFFER)
        adjusted_end_offset = min(file_size, end_offset + SEARCH_BUFFER)

        f.seek(adjusted_start_offset)
        data = f.read(adjusted_end_offset - adjusted_start_offset)

        print(f" - Searching {hex(adjusted_start_offset)} to {hex(adjusted_end_offset)} ({len(data)} bytes).\n")

        offset = data.find(pattern)
        if offset != -1:
            file_offset = adjusted_start_offset + offset
            start_of_marker = offset + len(pattern) - 1
            marker_offset_in_file = adjusted_start_offset + start_of_marker
            extracted_bytes = data[start_of_marker:start_of_marker + BYTES_AFTER_MARKER]
            version_string = translate_version(extracted_bytes)

            print(f"   Magic pattern found at offset    {hex(file_offset)}.")
            print(f"   `01` start found at offset       {hex(marker_offset_in_file)}.")
            print(f"   following `01`:                  {extracted_bytes.hex()}\n\n")
            print(f"   Translated Version:              {version_string}")

            hw_model = extract_string(f, HW_MODEL_OFFSET, 0x20)
            product_id = extract_string(f, PRODUCT_ID_OFFSET, 0x8)
            current_fw_version = extract_firmware_version(f, CURRENT_FW_OFFSET, 0x8)
            min_fw_version = extract_firmware_version(f, MIN_FW_OFFSET, 0x8)

            print(f"   HW Model:                        {hw_model}")
            print(f"   Product ID:                      {product_id}")
            print(f"   Current Firmware Version:        {current_fw_version}")
            print(f"   Minimum Firmware Version:        {min_fw_version}\n")

            firmware_md5_hash = compute_firmware_region_md5(file_path)
            print(f"   Firmware Region MD5 Hash:        {firmware_md5_hash}\n")

            with open(file_path, 'rb') as f:
                f.seek(FIRMWARE_REGION_OFFSET)
                firmware_data = f.read(FIRMWARE_REGION_SIZE)

            file_name = f"{version_string}_{current_fw_version.replace('.', '')}_{min_fw_version.replace('.', '')}_{hw_model}_{firmware_md5_hash}.bin"

            save_firmware_to_emc(firmware_data, file_name)

            with open(LOG_FILE, 'a') as log:
                log.write(f"{file_path}: {version_string}, {current_fw_version}, {min_fw_version}, {hw_model}, {firmware_md5_hash}\n")
        else:
            print(" - Pattern not found in this file.\n")

def main():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_folder)
    print(f"Current Working Folder: {current_folder}\n")

    start_offset = DEFAULT_START_OFFSET
    end_offset = DEFAULT_END_OFFSET

    print(f"Scanning range: {hex(start_offset)} to {hex(end_offset)} (+/- {SEARCH_BUFFER} bytes for buffer).\n")

    bin_files_found = False
    for file_name in os.listdir(current_folder):
        if file_name.endswith('.bin'):
            bin_files_found = True
            scan_bin_file(file_name, start_offset, end_offset, SEARCH_PATTERN)

    if not bin_files_found:
        print("No .bin files found in the current working folder.")

if __name__ == "__main__":
    main()
