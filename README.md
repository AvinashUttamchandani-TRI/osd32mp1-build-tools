# OSD32MP1 Debian SDK: OSD32MP1-build-tools
This repository contains the build tools used for OSD32MP1 Debian SDK.
Forked for TRI's Nervous System compute boards.

See the main [repo](https://github.com/AvinashUttamchandani-TRI/osd32mp1-debian) for more documentation.

# TODOs
## Required
- [*] tf-a compiles
- [*] u-boot compiles
- [*] kernel compiles
- [*] sd image generated
- [ ] verify power voltages are controllable
- [ ] uart4/main serial console
- [ ] m4 processor configuration
  - [ ] fix missing cubemx declarations so appropriate dtsi files can be generated
- [ ] device tree mysteries (possibly due to cubemx misconfig)
  - [ ] pwr_regulator
  - [ ] sram
  - [ ] m4 things
- [ ] update gitignore for cubemx things.

## Nice to Have
- [ ] rename CubeMX files to generate the correct names the first time.
    - [ ] looks like it currently refers to 157 instead of 157c, that could help in general
- [ ] remove osd32mp1-red references (if possible)
- [ ] make rule to switch between boards