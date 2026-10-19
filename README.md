# DuchampSaanKernal

Custom GKI kernel for **duchamp** (Poco X6 Pro, MT6897), based on Google's Android Common Kernel `android14-6.1`.

> **Status: work in progress.** The source builds and compiles in static checks, but it has not been boot-tested on a device yet. Flash at your own risk and keep your stock boot image.

## Features

| | |
|---|---|
| Base | Google ACK `android14-6.1` (6.1.177), via [chainonyourdoor/LuminaireKernel-6.1](https://github.com/chainonyourdoor/LuminaireKernel-6.1) |
| Kernel name | `6.1.177-saan` |
| Root | [BakaSU](https://github.com/Baka-SU/BakaSU), pinned to `5b76b884` (git submodule in `KernelSU/`) |
| SUSFS | v2.3.0 kernel patch (`fs/susfs.c`, hooks across `fs/`, `kernel/`, `mm/`, `security/`) |
| LTO | ThinLTO (`CONFIG_LTO_CLANG_THIN=y`) |
| Toolchain | AOSP clang `r487747c` |

BakaSU is pinned because newer versions refuse to build with SUSFS ("suspend susfs build"). Move the pin only after BakaSU and SUSFS are compatible again.

## How it works with your phone

This is a generic GKI kernel. It carries no duchamp device trees or vendor drivers: the stock vendor modules and device tree come from your ROM's `vendor_boot` and `vendor_dlkm`. For those modules to load, the kernel's KMI generation must match your stock kernel (`android14-11`). Check `uname -r` on stock.

## Build

### GitHub Actions (recommended)

1. Open the **Actions** tab, select **Build Kernel**, and tap **Run workflow** on branch `android14-6.1`.
2. Wait about 40 to 90 minutes.
3. Download the artifact `Saan-6.1.177-saan-duchamp-<date>.zip`.

The workflow checks that ThinLTO is on and fails early if it is not. On failure, the **Show first errors** step prints the first errors, and `build-log` is always uploaded.

### Local

```sh
git clone --recurse-submodules https://github.com/Chandan977808/DuchampSaanKernal
cd DuchampSaanKernal
export PATH=/path/to/clang-r487747c/bin:$PATH
make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 gki_defconfig
make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image
```

Build requirements: `bc bison flex libssl-dev libelf-dev cpio lz4 zip dwarves` (`dwarves` provides `pahole`, needed for BTF). The output is `out/arch/arm64/boot/Image`.

## Flash

1. Back up your stock boot image.
2. Flash the AnyKernel3 zip from recovery or a kernel flasher.
3. Install the BakaSU manager app. SUSFS also needs its userspace tool or module (`ksu_susfs`), which is not part of this repo.

If the phone does not boot, restore your stock boot image.

## Credits

- Google, Android Common Kernel
- chainonyourdoor, LuminaireKernel-6.1
- Baka-SU, BakaSU
- simonpunk, SUSFS
- osm0sis, AnyKernel3
- MiCode, Xiaomi kernel source

## License

GPL-2.0, like the Linux kernel. See `COPYING`.
