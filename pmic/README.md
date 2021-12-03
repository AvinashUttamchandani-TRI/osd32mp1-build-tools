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

