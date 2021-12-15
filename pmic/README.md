# Installation 

## First Pass
- ymmv, probably has steps that aren't required.
- Follow these instructions [https://eblot.github.io/pyftdi/installation.html] to get udev rules and groups set up. Then reboot, the `newgrp` command never works for me in Ubuntu.
- Use `venv` for the python stuff. 
```bash
# first time setup
sudo apt install python3-venv python3-libusb1
python3 -m venv ~/src/embedded-venv
cd ~/src/embedded-venv
source ./bin/activate
pip3 install pyftdi

# each time
cd ~/src/embedded-venv
source ./bin/activate

# to find the ftdi url
ftdi_urls.py
Available interfaces:
  ftdi://ftdi:232h:FT55S8HU/1   (C232HM-DDHSL-0)

```

Should be ready to program!

# PMIC Registers

## Critical
- 0x10: `MAIN_CR`:
  - 4: `OCP_OFF_DBG` , leave as zero
  - 3: `PWRCTRL_POL`, 0: AL, 1: AH (DOUBLE CHECK!)
  - 2: `PWRCTRL_ENA`, enables the pwrctrl pin at all
  - 1: `RREQ_ENA`: 0 is probably sanest ( rstn requirements)
  - 0: `SWOFF`: set high to start a power down sequence immediately

- 0x24: `REFDDR_MAIN_CR` : `[7:1] rsvd, [0] = VREF_DDR ENA`
- 0x25 to 0x2A: `LDOx_MAIN_CR` `x \in {1,2,5,6}`
  - `[7] :rsvd, [6:2] : VOUT[4:0], [1]: rsvd, [0]: ena`

  - see Table 9. LDO output voltage settings

- 0xFC: `NVM_BUCKS_VOUT_SHR` : NVM BUCKs voltage output shadow register
  -7:6 : BUCK4 VOUT:  { 2'b00 : 1.15 V, 2'b01: 1.2 V, 2'b10: 1.80 V 2'b11: 3.3 V } 
  -5:4 : BUCK3 VOUT:  { 2'b00 : 1.20 V, 2'b01: 1.8 V, 2'b10: 3.00 V 2'b11: 3.3 V } 
  -3:2 : BUCK2 VOUT:  { 2'b00 : 1.10 V, 2'b01: 1.2 V, 2'b10: 1.35 V 2'b11: 1.5 V } 
  -1:0 : BUCK1 VOUT:  { 2'b00 : 1.10 V, 2'b01: 1.2 V, 2'b10: 1.35 V 2'b11: 1.5 V } 

- 0xFD : `NVM_LDOS_VOUT_SHR1` : NVM BUCKs voltage output shadow register 1
  - 7: 0: PWR_SW doesn't turn off if boost VOP, 1: it does
  - 6: reserved
  - 5:4: LDO3 VOUT: { 2'b00: 1.8V, 2'b01: 2.5V, 2'b10: 3.3V, 2'b11: `VOUT_BUCK2[5:0]/2`}
  - 3:2: LDO2 VOUT: { 2'b00: 1.8V, 2'b01: 2.5V, 2'b10: 2.9V, 2'b11: 3.3V } 
  - 1:0: LDO1 VOUT: { 2'b00: 1.8V, 2'b01: 2.5V, 2'b10: 2.9V, 2'b11: 3.3V } 

- 0xFE : `NVM_LDOS_VOUT_SHR1` : NVM BUCKs voltage output shadow register 1
  - 7:4: reserved
  - 3:2: LDO6 VOUT: { 2'b00: 1.0V, 2'b01: 1.2V, 2'b10: 1.8V, 2'b11: 3.3V } 
  - 1:0: LDO5 VOUT: { 2'b00: 1.8V, 2'b01: 2.5V, 2'b10: 2.9V, 2'b11: 3.3V } 
- 0xFF : i2c address for pmic, don't mess with it.

# References
- [Octavo OSD32MP1 Power System Overview](https://octavosystems.com/app_notes/osd32mp1-power-system-overview/)
- [Octavo OSD32MP1 Non-Volatile Memory Programming Guide](https://octavosystems.com/app_notes/stpmic1-non-volatile-memory-programming-guide/?highlight=pmic)
- [Octavo's STPMIC1 NVM Programming Scripts](https://octavosystems.com/files/osd32mp15x-stpmic1-nvm-programming-scripts/)
- [STPMIC1 Datasheet](https://www.st.com/resource/en/datasheet/stpmic1.pdf)