#!/usr/bin/env python3

import argparse
# from pyftdi import FtdiLogger
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError
# from pyftdi.misc import add_custom_devices

import sys

# TODO: check that pullups are on the pmic i2c bus

from pmic_read_reg import pmic_i2c_reg as pmic_register_table
# from pmic_reprogram_nvm import pmic_i2c_


def main(url="ftdi://ftdi:232h:FT55S8HU/1"):
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
        print("|{0:^10}|{1:^20}|{2:^20}|{3:^20}|{4}".format(addr, name, printable_data, default, printable_data == default))
    sys.exit(0)
    1

if __name__ == "__main__":
    main()