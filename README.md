# RuyiKernal

<p align="center">
  <img src="ruyi-kernel-poster.png" alt="Ruyi Kernel V1 Poster" width="100%">
</p>

Custom GKI kernel for **duchamp** (Poco X6 Pro, MT6897), based on Google's Android Common Kernel `android14-6.1`.

## Features

| | |
|---|---|
| Base | Google ACK `android14-6.1` (6.1.177) |
| Kernel name | `6.1.177-Ruyi-saan` |
| Root | [BakaSU](https://github.com/Baka-SU/BakaSU), pinned to `5b76b884` (git submodule in `KernelSU/`) |
| SUSFS | v2.3.0 kernel patch (`fs/susfs.c`, hooks across `fs/`, `kernel/`, `mm/`, `security/`) |
| LTO | ThinLTO (`CONFIG_LTO_CLANG_THIN=y`) |
| Toolchain | AOSP clang `r487747c` |

BakaSU is pinned because newer versions refuse to build with SUSFS ("suspend susfs build"). Move the pin only after BakaSU and SUSFS are compatible again.

## How it works with your phone

This is a generic GKI kernel. It carries no duchamp device trees or vendor drivers: the stock vendor modules and device tree come from your ROM's `vendor_boot` and `vendor_dlkm`. For those modules to load, the kernel's KMI generation must match your stock kernel (`android14-11`). Check `uname -r` on stock.

## Flash

Back up your stock boot image first.

1. **With recovery or a kernel flasher:** flash the AnyKernel3 zip.
2. **Without recovery:** download the provided `boot.img` and flash it with fastboot:

   ```sh
   fastboot flash boot_ab boot.img
   ```

3. Install the BakaSU manager app. SUSFS also needs its userspace tool or module (`ksu_susfs`), which is not part of this repo.

If the phone does not boot, restore your stock boot image.

## Bypass charging

Bypass charging is controlled with [Duchamp Essential](https://github.com/Chandan977808/Duchamp-Essential), which offers Immediate or 20/40/80/90% thresholds and a Quick Settings tile.

1. Install the Duchamp Essential module ZIP through your root manager, then reboot and enable it. Its README lists KernelSU Next Manager and Magisk; BakaSU Manager is untested.
2. Open Duchamp Essential, go to Charging Control, and turn on bypass charging.

Duchamp Essential needs the battery power-supply directory to expose the `bypass_charging_supported`, `bypass_charging` and `bypass_charging_active` nodes. This kernel does not add them, so they have to come from your ROM's charger driver. See the [bypass charging notes](https://github.com/Chandan977808/Duchamp-Essential/blob/main/docs/BYPASS_CHARGING.md).

## Support

If you like Ruyi Kernel, you can support its development: **[Donate](https://t.me/saan_os/80)**

## Credits

- Google, Android Common Kernel
- chainonyourdoor, LuminaireKernel-6.1
- Baka-SU, BakaSU
- simonpunk, SUSFS
- osm0sis, AnyKernel3
- MiCode, Xiaomi kernel source
- NEESCHAL-3, Rodin Essential

## License

GPL-2.0, like the Linux kernel. See `COPYING`.
