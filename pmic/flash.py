#!/usr/bin/env python3

import argparse
# from pyftdi import FtdiLogger
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError
# from pyftdi.misc import add_custom_devices

import sys

# TODO: check that pullups are on the pmic i2c bus

def main(url="ftdi://ftdi:232h:FT55S8HU/1"):
    i2c = I2cController()
    i2c.configure(url)
    port = i2c.get_port(0x33) # TODO check pmic address
    try:
        port.read(0)
    except I2cNackError:
        print("Couldn't connect to pmic i2c port.")
        sys.exit(-1)
    
    

if __name__ == "__main__":
    main()