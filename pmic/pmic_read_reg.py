"""
--------------------------------------------------------------------------
Octavo Systems - OSD33MP1 Low Volume Production Test - PMIC
--------------------------------------------------------------------------
License:
Copyright 2020 - Octavo Systems LLC

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
This program will:
  - Read all P?MIC registers and print values

  - This library uses the i2cget command

--------------------------------------------------------------------------
"""
import os
import sys
import time
import getopt


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

# Test Name
TESTNAME                = "PMIC Register Test"

# I2C command
I2C_CMD                 = "i2cget -f -y {0} {1} {2}"

# PMIC Register Constants
PMIC_I2C_BUS            = "3"
PMIC_I2C_ADDR           = "0x33"


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------
debug                   = False

column_width            = 75

pmic_i2c_reg            = [
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


# ------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------
def read_registers(bus):
    """Read the registers."""

    print("\n{0}\n".format(TESTNAME))
    print("-" * column_width)
    print("|{0:^10}|{1:^20}|{2:^20}|{3:^20}|".format("Addr", "Name", "Value", "Default"))
    print("-" * column_width)

    for name, rw, default, addr in pmic_i2c_reg:
        if debug:
            print("{0}".format(I2C_CMD.format(bus, PMIC_I2C_ADDR, addr)))

        value = int(os.popen(I2C_CMD.format(bus, PMIC_I2C_ADDR, addr)).read().strip(), 0)

        print_value = "8'b{0:08b}".format(value)
        print_value = print_value[:7] + "_" + print_value[7:]

        print("|{0:^10X}|{1:20}|{2:>20}|{3:>20}|".format(addr, name, print_value, default))

    print("-" * column_width)


# End def

def usage():
    print("python3 pmic_read_reg.py")
    print("  --i2c=\"pmic i2c bus\"    Ex.  \"2\"")
    print("In order to change the behavior of the script, you need to alter portions accordingly")

# End def

def setup():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hiv", ["help", "i2c="])

    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))
        usage()
        sys.exit(2)

    bus = "3"

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--i2c"):
            if a in ["0","1","2","3"]:
                bus = a
            else:
                assert False, "invalid option"

        else:
            assert False, "unhandled option"
    return bus

# End def

def run(bus):
    import contextlib, io


    time.sleep(1)

    try:
        status = False
        f      = io.StringIO()

        # Run the test grabbing all output for log file
        with contextlib.redirect_stderr(sys.stdout):
            with contextlib.redirect_stdout(f):
                read_registers(bus)
                print("\n")
        status = True

        print(f.getvalue())

    except Exception as e:
        print("Please check the I2C bus number used to connect to the PMIC.")

    if status:
        print("PASSED")

    else:
        print("FAILED")

    time.sleep(2)



# End def


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':

    bus = setup()
    run(bus)
