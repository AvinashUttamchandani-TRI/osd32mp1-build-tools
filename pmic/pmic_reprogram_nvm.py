"""
--------------------------------------------------------------------------
Octavo Systems - OSD33MP1 Low Volume Production Test - PMIC Write NVM
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
  - Write all the NVM registers with the values of a STPMIC1A 
  
  - Program Flow
    - Program runs

  - This program uses:
    - i2cget/i2cset command

  - Values to be changed to your liking (refer to stpmic1 datasheet p. 119 - 125)
    - NVM main control shadow register, NVM_MAIN_CTRL_SHR
    - NVM BUCK rank shadow register, NVM_BUCKS_RANK_SHR
    - NVM LDOs rank shadow registers, NVM_LDOS_RANK_SHRx
    - NVM BUCKs voltage output shadow register, NVM_BUCKS_VOUT_SHR
    - NVM LDOs voltage output shadow registers, NVM_LDOS_VOUT_SHRX


--------------------------------------------------------------------------
"""
import os
import sys
import time
import getopt

# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

# I2C command
I2C_GET_CMD             = "i2cget -f -y {0} {1} {2}"
I2C_SET_CMD             = "i2cset -f -y {0} {1} {2} {3}"

# PMIC Register Constants
# PMIC I2C BUS may be 0, 1, 2, or 3
PMIC_I2C_ADDR           = "0x33"
MAIN_CTRL_VAL           = 0b11011110


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------
debug                   = False

read_column_width       = 64
write_column_width      = 55

pmic_i2c_read_reg       = [
    # Status Registers
    ["VERSION_SR",           "r",  "8'b0010_0001", 0x06],       # Should be version 2.1

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

pmic_i2c_write_nvm      = [
    # NV Memory
    ["NVM_MAIN_CTRL_SHR",    0xF8, 0b11011110],
    ["NVM_BUCKS_RANK_SHR",   0xF9, 0b10010010],
    ["NVM_LDOS_RANK_SHR1",   0xFA, 0b11000000],
    ["NVM_LDOS_RANK_SHR2",   0xFB, 0b00000010],
    ["NVM_BUCKS_VOUT_SHR",   0xFC, 0b11110010],
    ["NVM_LDOS_VOUT_SHR1",   0xFD, 0b10000000],
    ["NVM_LDOS_VOUT_SHR2",   0xFE, 0b00000010]
#    ["NVM_I2C_ADDR_SHR",     0xFF, 0b00110011]     # Do not modify I2C address
]

# NVM commit registers
NVM_SR                  = 0xB8
NVM_CR                  = 0xB9

NVM_PROGRAM             = 0b01


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------
def read_registers(bus):
    """Read the registers."""
    
    print("-" * read_column_width)
    print("|{0:^20}|{1:^20}|{2:^20}|".format("Name", "Value", "Default"))
    print("-" * read_column_width)

    # Read Registers
    for name, rw, default, addr in pmic_i2c_read_reg:
        if debug:
            print("{0}".format(I2C_GET_CMD.format(bus, PMIC_I2C_ADDR, addr)))

        value = int(os.popen(I2C_GET_CMD.format(bus, PMIC_I2C_ADDR, addr)).read().strip(), 0)

        print_value = "8'b{0:08b}".format(value)
        print_value = print_value[:7] + "_" + print_value[7:]

        print("|{0:20}|{1:>20}|{2:>20}|".format(name, print_value, default))

    print("-" * read_column_width)

        
# End def


def write_nvm(bus, ctrl):
    """Write the NVM registers."""
    write_successful = True
    
    print("-" * write_column_width)
    print("|{0:^20}|{1:^10}|{2:^10}|{3:^10}|".format("Name", "Value", "Readback", "Match"))
    print("-" * write_column_width)


    # Write the NVM shadow registers
    for name, addr, value in pmic_i2c_write_nvm:
        if name == "NVM_MAIN_CTRL_SHR":
            value = ctrl
        if debug:
            print("{0}".format(I2C_SET_CMD.format(bus, PMIC_I2C_ADDR, addr, value)))

        os.popen(I2C_SET_CMD.format(bus, PMIC_I2C_ADDR, addr, value)).read().strip()

        read_value = int(os.popen(I2C_GET_CMD.format(bus, PMIC_I2C_ADDR, addr)).read().strip(), 0)

        if read_value == value:
            match            = True
        else:
            match            = False
            write_successful = False

        print("|{0:20}|{1:^10}|{2:^10}|{3:>10}|".format(name, value, read_value, match))

    print("-" * write_column_width)

    # Commit the values to the NV memory if all writes above match
    if write_successful:
        os.popen(I2C_SET_CMD.format(bus, PMIC_I2C_ADDR, NVM_CR, NVM_PROGRAM)).read().strip()

        timeout = 10
        busy    = 1
        start   = time.time()

        while (busy == 1) and ((time.time() - start) < timeout):
            busy = (int(os.popen(I2C_GET_CMD.format(bus, PMIC_I2C_ADDR, addr)).read().strip(), 0) & 0x01)

        if (busy == 1):
            print("\nTimout trying to write to NVM.")
            write_successful = False
        else:
            print("\nValues written to NVM.")

    else:
        print("\nValues not written correctly.  Please debug.")

    
    return write_successful
    
# End def

def setup():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hiv", ["help", "i2c=", "vin_ok="])

    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))
        usage()
        sys.exit(2)

    bus = "3"
    ctrl = 0b11011110

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--i2c"):
            if a in ["0","1","2","3"]:
                bus = a
            else:
                assert False, "invalid option"
        elif o in ("-v", "--vin_ok"):
            if a == "3.5":
                ctrl = 0b11101110
            elif a == "3.3":
                ctrl = 0b11011110
            elif a == "3.1":
                ctrl = 0b11001110
            elif a == "4.0":
                ctrl = 0b11111110
            else:
                assert False, "invalid option"


        else:
            assert False, "unhandled option"
    return (bus, ctrl)

# End def

def usage():
    print("python3 pmic_reprogram_nvm.py")
    print("  --i2c=\"pmic i2c bus\"    Ex.  \"2\"")
    print("  --vin_ok=\"VIN OK Threshold Voltage\"     Ex. \"3.3\"")
    print("In order to change the behavior of the script, you need to alter portions accordingly")

# End def


def run(bus, ctrl):
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
                status = write_nvm(bus,ctrl)
                print("\n")
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

    bus, ctrl = setup()
    run(bus, ctrl)
    