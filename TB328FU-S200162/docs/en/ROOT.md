# Magisk root, tested on TB328FU S200162 slot A

**Observed result on 17 October 2026:** Magisk 30.7 root, `adb shell su -c id` returned `uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0`. This is a separate step AFTER the persistent bootloader unlock documented in [UNLOCK.md](UNLOCK.md). It does not require installing a custom ROM.

## 1. Preconditions

- Confirm `ro.build.display.id=TB328FU_S200162_250825_ROW`, `ro.boot.slot_suffix=_a`, `ro.boot.flash.locked=0`, `ro.boot.vbmeta.device_state=unlocked`.
- The device boots stock Lenovo Android 12. ADB and Fastboot work on the PC. Back up all valuable data.
- Obtain a **fresh, exact-build, stock, unpatched** `boot_a` from this device (original firmware or a *read-only* FDL2 partition extraction). Preserve it offline. You must never flash a pre-patched boot image borrowed from another tablet.

## 2. Fresh stock boot backup

Using a known working stock FDL1/FDL2 set in the same directory as the verified `spd_dump.exe`, run:

```bat
spd_dump.exe --wait 120 exec_addr 0x3ee8 fdl fdl1-dl.bin 0x5500 fdl fdl2-dl.bin 0x9efffe00 exec
```

Connect the powered-off device in physical BootROM mode. At `FDL2 >`, type one command at a time:

```text
path ROOT_BACKUP
r boot_a
r init_boot_a
```

After a complete read, `reset` (or restart using Power if the tool's reset does not restart). **These are partition reads only.** The actual tested device produced:

| Partition image | Observed size / nature |
| --- | --- |
| `boot_a.bin` | 67,108,864 B (64 MiB), Android Boot **v4**, kernel + LZ4-compressed ramdisk |
| `init_boot_a.bin` | 8,388,608 B (8 MiB), **all zero** — not the Magisk target |

The tested stock `boot_a` SHA-256 was:

```text
0d699f4ca7710f4c8f87dbc8c60b94e1621708d2bc5e474fdf0d013a25e89560
```

**Use this hash to verify the documented trial, not as permission to reuse a boot image from a different firmware or tablet.** On any different build, STOP until the image is validated for that build.

## 3. Patch boot_a with Magisk on the actual tablet

Download Magisk **from the author**: https://github.com/topjohnwu/Magisk/releases . In the successful test Magisk version **30.7 (30700)** was used. With USB debugging enabled:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" devices
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" push "ROOT_BACKUP\boot_a.bin" /sdcard/Download/boot_a.img
```

In the Magisk app: **Install → Select and Patch a File → Downloads/boot_a.img**. It logged `Stock boot image detected`, `Patching ramdisk`, `Repacking boot image`, `All done!`.

On the tested tablet the resulting filename was `magisk_patched-30700_B3Zyf.img`. **Names vary**. Copy it back using the exact actual name:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell ls -lh /sdcard/Download/magisk_patched*
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" pull "/sdcard/Download/magisk_patched-30700_B3Zyf.img" "magisk_patched.img"
```

The confirmed patched file was 67,108,864 B, SHA-256:

```text
5c99161ebcd93e0786421608a4dd1950a517db5e5e02229413daf9383c499cfd
```

Its Android Boot v4 header was valid, the **Linux kernel SHA-256 matched stock**, and only the ramdisk/AVB footer was rebuilt. The patched ramdisk was **2,230,882 bytes**, compared with **2,353,747 bytes** in the original. Structural validation alone does not prove an image will boot, but this image did boot on the reported device.

## 4. Flash patched boot on slot A only

With the saved **unmodified stock `boot_a.bin` available for rollback**, reboot to bootloader:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" reboot bootloader
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" devices
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" getvar current-slot
```

The successful test saw `current-slot: a`. `fastboot getvar unlocked` returned an empty value on Lenovo; do not treat it as a lock assertion. **STOP if the slot is not A, if the image was not verified, if the stock backup is missing, or if Fastboot cannot talk to the device.**

Only then, **this command writes the active boot partition**:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" flash boot_a magisk_patched.img
```

Proceed only if it reports `OKAY` for send/write. If it reports `FAILED`, stop and save the error. Once successful:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" reboot
```

**Do not flash `init_boot_a`, modify `vbmeta` prophylactically, erase `userdata` as a first reflex, or relock the bootloader.** The complete Fastboot console log was not supplied; the successful boot and root check independently confirm the resulting Magisk integration.

## 5. Verify root

Once Android boots, approve the Magisk superuser request for ADB if asked, then:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell su -c id
```

**Observed**:

```text
uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0
```

## 6. Return to stock boot if Magisk bootloops

If Fastboot remains accessible and you are certain the saved `ROOT_BACKUP\boot_a.bin` belongs to the **currently active S200162 slot A**:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" flash boot_a "ROOT_BACKUP\boot_a.bin"
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" reboot
```

This **removes Magisk modifications from the boot image**, but it **does not re-lock** the bootloader or undo any earlier persistent changes from V9. If Fastboot itself is broken, stop rather than improvising an erase. See [troubleshooting](TROUBLESHOOTING.md).

**Official Magisk documentation:** https://topjohnwu.github.io/Magisk/install.html
