#!/usr/bin/env python3

import argparse
# from pyftdi import FtdiLogger
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError
# from pyftdi.misc import add_custom_devices

import sys
import time

# TODO: check that pullups are on the pmic i2c bus

# from pmic_read_reg import pmic_i2c_reg as pmic_register_table
from pmic_reprogram_nvm import pmic_i2c_write_nvm, NVM_SR, NVM_CR, NVM_PROGRAM
pmic_register_table = [
    # Status Registers
    ["TURN_ON_SR",           "r",  "8'b000x_xxxx", 0x01],
    ["TURN_OFF_SR",          "r",  "8'b000x_xxxx", 0x02],
    ["OCP_LDOS_SR",          "r",  "8'b00xx_xxxx", 0x03],
    ["OCP_BUCKS_BSW_SR",     "r",  "8'b00xx_xxxx", 0x04],
    ["RESTART_SR",           "r",  "8'b000x_xxxx", 0x05],
    ["VERSION_SR",           "r",  "8'b000x_xxxx", 0x06],

    # Control Registers
    ["MAIN_CR",              "rw", "8'b0000_0000", 0x10],

    # Trim
    ["0xE0 - ???",           "rw", "8'b0000_0000", 0xE0],
    ["0xE1 - ???",           "rw", "8'b0000_0000", 0xE1],
    ["TRIM_BST_01",          "rw", "8'b0000_0010", 0xE2],
    ["TRIM_BST_02",          "rw", "8'b0001_1001", 0xE3],
    ["TRIM_BST_03",          "rw", "8'b1101_0000", 0xE4],
    ["TRIM_OTG",             "rw", "8'b1000_0001", 0xE5],
    ["TRIM_SW",              "rw", "8'b1000_0001", 0xE6],
    ["TRIM_VR_DAC",          "rw", "8'b0000_0000", 0xE7],
    ["TRIM_OSC",             "rw", "8'b0100_0010", 0xE8],
    ["0xE9 - ???",           "rw", "8'b0000_0000", 0xE9],
    ["TRIM_BG",              "rw", "8'b0000_1010", 0xEA],
    ["TRIM_VR1/2",           "rw", "8'b0000_0000", 0xEB],
    ["TRIM_VR3/4",           "rw", "8'b0000_0000", 0xEC],
    ["TRIM_COMM",            "rw", "8'b0000_0001", 0xED],    
    ["TRIM_LDO4/2",          "rw", "8'b0000_0001", 0xEE],
    ["TRIM_LDO1",            "rw", "8'b0000_1000", 0xEF],
    ["TRIM_LDO5",            "rw", "8'b0100_0000", 0xF0],
    ["TRIM_LDO6/4/3",        "rw", "8'b0001_0000", 0xF1],
    ["TRIM_VR1/2_OFFS",      "rw", "8'b0000_0000", 0xF2],
    ["TRIM_VR3/4_OFFS",      "rw", "8'b0001_0001", 0xF3],
    
    # NV Memory
    ["NVM_MAIN_CTRL_SHR",    "rw", "8'b1110_1110", 0xF8],
    ["NVM_BUCKS_RANK_SHR",   "rw", "8'b1001_0010", 0xF9],
    ["NVM_LDOS_RANK_SHR1",   "rw", "8'b1100_0000", 0xFA],
    ["NVM_LDOS_RANK_SHR2",   "rw", "8'b0000_0010", 0xFB],
    ["NVM_BUCKS_VOUT_SHR",   "rw", "8'b1111_0010", 0xFC],
    ["NVM_LDOS_VOUT_SHR1",   "rw", "8'b1000_0000", 0xFD],
    ["NVM_LDOS_VOUT_SHR2",   "rw", "8'b0000_0010", 0xFE],
    ["NVM_I2C_ADDR_SHR",     "rw", "8'b0011_0011", 0xFF]
]


def main(url="ftdi://ftdi:232h:FT55S8HU/1", ro = True):
    i2c = I2cController()
    i2c.configure(url)
    port = i2c.get_port(0x33)
    try:
        port.read(0)
    except I2cNackError:
        print("Couldn't connect to pmic i2c port.")
        sys.exit(-1)
    

    # Read all registers
    column_width=80
    print("-" * column_width)
    print("|{0:^10}|{1:^20}|{2:^20}|{3:^20}|".format("Addr", "Name", "Value", "Default"))
    print("-" * column_width)
    for name, rw, default, addr in pmic_register_table:
        data = port.read_from(addr, 1)
        data = data[0]
        printable_data = "8'b{0:08b}".format(data)
        printable_data = printable_data[:7] + "_" + printable_data[7:]
        # print(addr, name, bin(data), default)
        print("|{0:^10}|{1:^20}|{2:^20}|{3:^20}|{4}".format(hex(addr), name, printable_data, default, printable_data == default))
    if ro:
        sys.exit(0)
    
    print("### Writing Registers ### ")
    incorrect_writes = []
    vin_ok_mapping = {3.5:0b11101110 , 3.3: 0b11011110, 3.1:0b11001110, 4.0:0b11111110}
    vin_ok = 3.3
    if vin_ok not in vin_ok_mapping:
        raise(f"Invalid v_in ok value: {vin_ok}")
    
    for name, addr, value in pmic_i2c_write_nvm:
        if name == "NVM_MAIN_CTRL_SHR":
            value = vin_ok_mapping[vin_ok]
        port.write([addr, value])
        check_value = port.read_from(addr,1)
        check_value = int(check_value[0])
        if value != check_value:
            incorrect_writes.append((name, addr, value, check_value))
    
    if incorrect_writes:
        print("Writing failed on the following addresses.")
        for name, addr, value, check_value in incorrect_writes:
            print(f"  {hex(addr)}: {name} = {check_value}, should be {value} ")
        sys.exit(1)
    print("Writes look good, committing NVM shadow registers.")
    port.write([NVM_CR, NVM_PROGRAM])

    timeout = 10.0
    t0 = time.time()
    busy = True
    while busy:
        value = port.read_from(NVM_SR, 1)
        busy = int(value[0]) & 0x01
        if (time.time()-t0) >= timeout:
            print("!!! Timed out while waiting to see if if the NVM write succeeded !!!")
            sys.exit(1)

    print("Successfully rewrote NVM! Power cycle to check.")

    
    sys.exit(0)

if __name__ == "__main__":
    main(ro=False)