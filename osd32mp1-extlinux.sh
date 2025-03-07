#!/bin/bash -e

DEPLOY_DIR=./

while getopts "d:b:" option
do
case "${option}"
in
d) DEPLOY_DIR=${OPTARG};;
b) BOARD_NAME=${OPTARG};;
esac
done


export BOOT_DEVICES_LIST=" \
	mmc0 \
	mmc1 \
"

UBOOT_SPLASH_IMAGE_mmc0="/splash.bmp"
UBOOT_EXTLINUX_TIMEOUT_mmc0=20
UBOOT_EXTLINUX_DEFAULT_LABEL_mmc0=${BOARD_NAME}-sdcard
UBOOT_EXTLINUX_LABEL_mmc0=${BOARD_NAME}-sdcard
UBOOT_EXTLINUX_KERNEL_IMAGE_mmc0="/uImage"
UBOOT_EXTLINUX_FDTDIR_mmc0="/${BOARD_NAME}.dtb"
UBOOT_EXTLINUX_ARGS_mmc0="root=/dev/mmcblk1p6 rootwait rw console=ttySTM0,115200 init=/sbin/init firmware_class.path=/lib/firmware/"

UBOOT_SPLASH_IMAGE_mmc1="/splash.bmp"
UBOOT_EXTLINUX_TIMEOUT_mmc1=20
UBOOT_EXTLINUX_DEFAULT_LABEL_mmc1=${BOARD_NAME}-emmc
UBOOT_EXTLINUX_LABEL_mmc1=${BOARD_NAME}-emmc
UBOOT_EXTLINUX_KERNEL_IMAGE_mmc1="/uImage"
UBOOT_EXTLINUX_FDTDIR_mmc1="${BOARD_NAME}.dtb"
UBOOT_EXTLINUX_ARGS_mmc1="root=/dev/mmcblk2p4 rootwait rw console=ttySTM0,115200 init=/sbin/init firmware_class.path=/lib/firmware/"


for boot_device in ${BOOT_DEVICES_LIST} ; do
	mkdir -p ${DEPLOY_DIR}/${boot_device}_${BOARD_NAME}_extlinux
	UBOOT_SPLASH_IMAGE=UBOOT_SPLASH_IMAGE_$boot_device
	UBOOT_EXTLINUX_TIMEOUT=UBOOT_EXTLINUX_TIMEOUT_$boot_device
	UBOOT_EXTLINUX_DEFAULT_LABEL=UBOOT_EXTLINUX_DEFAULT_LABEL_$boot_device
	UBOOT_EXTLINUX_LABEL=UBOOT_EXTLINUX_LABEL_$boot_device
	UBOOT_EXTLINUX_KERNEL_IMAGE=UBOOT_EXTLINUX_KERNEL_IMAGE_$boot_device
	UBOOT_EXTLINUX_FDTDIR=UBOOT_EXTLINUX_FDTDIR_$boot_device
	UBOOT_EXTLINUX_ARGS=UBOOT_EXTLINUX_ARGS_$boot_device
cat <<EOF >${DEPLOY_DIR}/${boot_device}_${BOARD_NAME}_extlinux/extlinux.conf
# Generic Distro Configuration file generated by Octavo Build System
menu title Select the boot mode
MENU BACKGROUND ${!UBOOT_SPLASH_IMAGE}
TIMEOUT ${!UBOOT_EXTLINUX_TIMEOUT}
DEFAULT ${!UBOOT_EXTLINUX_DEFAULT_LABEL}
LABEL ${!UBOOT_EXTLINUX_LABEL}
	KERNEL ${!UBOOT_EXTLINUX_KERNEL_IMAGE}
	FDT ${!UBOOT_EXTLINUX_FDTDIR}
	APPEND ${!UBOOT_EXTLINUX_ARGS}
EOF
done
