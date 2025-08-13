#Script to try to create defs for all RX8 ROMs for an immo delete

#Inital Immo Address Start: variable, starts with -0x B5 6E 00 09 60 D0 60 0C 88 00 8D 11
#Immo Patch without RKE Hex Offset: 0x354 bytes starting from byte AFTER last patch byte or 0xF7 from immo start
#Immo Patch ROM specific addresses: 3 of them
                                # 1 - 0x4A from immo Address Start
                                # 2 - 0x4 from #1 start
                                # 3 - 0x38 from #2 start

import argparse
import re

address1_offset = 0x4A
address2_offset = 0x4
address3_offset = 0x38
w_rke_offset = 0xf7 + 0x355

immo_start_pattern ="B56E000960D0600C88008D1100098801"

output_file = "defs.txt"

#Search input bin file for ECU ID
def search_input(input_binary_filename):

    with open(input_binary_filename, 'rb') as file:
        file.seek(0x2000)
        data = file.read(8)
        input_ecu_id = data.decode()
        print("ECU ID Found: %s" %input_ecu_id)

def search_immo_start(input_binary_filename):

    with open(input_binary_filename, 'rb') as file:

        #seek past bootloader, we know it's not there
        file.seek(0x2000)
    
        while True:

            hexdata = file.read(1).hex().upper()

            if re.search(immo_start_pattern[:2], hexdata):
                #print("Potential Start of Immo")
                
                hexdata = file.read(15).hex().upper()
                if re.search(immo_start_pattern[2:32], hexdata):
                    address = hex(file.tell()- 16) 
                    print(f"Start of Immo Found at {address}")
                    return address
            if file.tell() >= (int(0x80000) - 16):
                print("Immo not found or string incorrect")
                break;

def get_immo_patch_addresses(start_address,input_binary_filename):

    address1_address = hex(int(start_address,0) + address1_offset)
    address2_address = hex(int(address1_address,0) + address2_offset)
    address3_address = hex(int(address2_address,0) + address3_offset)
    w_rke_address = hex(int(start_address,0) + w_rke_offset)

    with open(input_binary_filename, 'rb') as file:
        file.seek(int(address1_address,0))
        address1_val = file.read(2).hex().upper()
        #print(address1_val)
        file.seek(int(address2_address,0))
        address2_val = file.read(2).hex().upper()
        #print(address2_val)
        file.seek(int(address3_address,0))
        address3_val = file.read(2).hex().upper()
        #print(address3_val)

        return address1_val, address2_val, address3_val, w_rke_address

def write_immo_patch_defs(start_address,val1,val2,val3,val4,file):

    val1 = val1[:2] + " " + val1[2:4]
    val2 = val2[:2] + " " + val2[2:4]
    val3 = val3[:2] + " " + val3[2:4]

    print("Writing Def file")
    with open(file, "w") as file:   
        file.write(f"<table name=\"Immobilizer Disable - Without RKE Installed\" storageaddress=\"{start_address}\">\n") 
        file.write(f"\t<state name=\"on\" data=\"00 09 00 09 00 09 B3 D5 00 09 00 09 00 09 00 09 00 09 00 09 00 09 00\n \
		            09 00 09 00 09 00 09 00 09 00 09 00 09 00 09 00 09 00 09 00 09 00 09\n \
		            00 09 00 09 00 09 A0 3D 00 09 01 F4 00 FA 55 AA AA CC B5 C4 FF FF FF\n \
		            FF 86 9C 00 03 {val1} 00 03 {val2} FF FF C2 28 FF FF C2 2C FF FF C2 3E\n \
		            FF FF C2 3A FF FF C2 88 FF FF C2 8C 00 01 00 01 55 AA 55 AA 00 00 FF\n \
		            FF FF FF C2 96 FF FF C2 98 00 00 B7 E3 FF FF C2 39 00 03 {val3} B0 BB\n \
		            00 09 A0 11 00 09 B1 CF 00 09 A0 0D 00 09 B2 5B 00 09 A0 09 00 09 B2\n \
		            FD 00 09 A0 05 00 09 B3 4E 00 09 A0 01 00 09 2D E0 DD 30 D2 30 64 20\n \
		            60 4C 88 05 8D 04 64 03 60 43 88 06 8F 10 00 09 D2 2C 63 20 23 38 8F\n \
		            0B 00 09 D1 2B 60 10 20 08 8F 06 00 09 D2 29 E5 01 42 0B 64 D0 A0 01\n \
		            2D 00 2D E0 E3 03 62 D0 62 2C 32 33 8F 0D 00 09 E1 00\"/>\n \
			<state name=\"off\" data=\"B5 6E 00 09 60 D0 60 0C 88 00 8D 11 00 09 88 01 8D 3A 00 09 88 02 8D\n \
					3B 00 09 88 03 8D 3C 00 09 88 04 8D 3D 00 09 88 05 8D 3E 00 09 A0 40\n \
					00 09 B0 8C 00 09 A0 3D 00 09 01 F4 00 FA 55 AA AA CC B5 C4 FF FF FF\n \
					FF 86 9C 00 03 {val1} 00 03 {val2} FF FF C2 28 FF FF C2 2C FF FF C2 3E\n \
					FF FF C2 3A FF FF C2 88 FF FF C2 8C 00 01 00 01 55 AA 55 AA 00 00 FF\n \
					FF FF FF C2 96 FF FF C2 98 00 00 B7 E3 FF FF C2 39 00 03 {val3} B0 BB\n \
					00 09 A0 11 00 09 B1 CF 00 09 A0 0D 00 09 B2 5B 00 09 A0 09 00 09 B2\n \
					FD 00 09 A0 05 00 09 B3 4E 00 09 A0 01 00 09 2D E0 DD 30 D2 30 64 20\n \
					60 4C 88 05 8D 04 64 03 60 43 88 06 8F 10 00 09 D2 2C 63 20 23 38 8F\n \
					0B 00 09 D1 2B 60 10 20 08 8F 06 00 09 D2 29 E5 01 42 0B 64 D0 A0 01\n \
					2D 00 2D E0 E3 03 62 D0 62 2C 32 33 8F 0D 00 09 E1 01\" />\n \
		</table>\n\n")
        file.write(f"<table name=\"Immobilizer Disable - With RKE Installed\" storageaddress=\"{val4}\">\n") 

def main():

    # Setup argument parser for input/output file names
    parser = argparse.ArgumentParser(description="Patch a binary file using S-record data.")
    parser.add_argument("binary_file", help="Path to the input binary file")

    # Parse arguments
    args = parser.parse_args()

    #Check ECU ID
    search_input(args.binary_file)
    immo_start_address = search_immo_start(args.binary_file)
    val1, val2, val3, val4 = get_immo_patch_addresses(immo_start_address,args.binary_file)
    write_immo_patch_defs(immo_start_address,val1, val2, val3, val4, output_file)
    print("File written, copy into ECU Defs XML")
    
if __name__ == "__main__":
    main()