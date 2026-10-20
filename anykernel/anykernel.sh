### AnyKernel3 Ramdisk Mod Script
## osm0sis @ xda-developers

### AnyKernel setup
# global properties
properties() { '
kernel.string=Ruyi Kernel by @saan9078
do.devicecheck=0
do.modules=0
do.systemless=0
do.cleanup=1
do.cleanuponabort=0
do.check_boot_version=0
device.name1=
device.name2=
device.name3=
device.name4=
device.name5=
supported.versions=
supported.patchlevels=
supported.vendorpatchlevels=
'; } # end properties


### AnyKernel install
## boot shell variables
block=boot;
BLOCK=boot;
is_slot_device=auto;
IS_SLOT_DEVICE=auto;
ramdisk_compression=auto;
RAMDISK_COMPRESSION=auto;
patch_vbmeta_flag=auto;
PATCH_VBMETA_FLAG=auto;
no_magisk_check=1;
NO_MAGISK_CHECK=1;

# import functions/variables and setup patching - see for reference (DO NOT REMOVE)
. tools/ak3-core.sh

# GKI check
kernel_version=$(cat /proc/version | awk -F '-' '{print $1}' | awk '{print $3}')
case $kernel_version in
    5.1*) ksu_supported=true ;;
    6.1*) ksu_supported=true ;;
    6.6*) ksu_supported=true ;;
    *) ksu_supported=false ;;
esac

ui_print " " "  -> Ruyi Kernels Supported: $ksu_supported"
$ksu_supported || abort "  -> Non-GKI device, abort."

# GKI init_boot separation check:
# Devices with init_boot store the ramdisk in init_boot and the raw kernel in boot.
# split_boot + flash_boot avoids unpacking/repacking the non-existent boot ramdisk.
if [ -L "/dev/block/bootdevice/by-name/init_boot_a" -o -L "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot" ]; then
    split_boot;
    flash_boot;
else
    dump_boot;
    write_boot;
fi;

ui_print " ";
ui_print "  Done! Enjoy RUYI kernel";
ui_print "  Reboot your device.";
ui_print " ";

