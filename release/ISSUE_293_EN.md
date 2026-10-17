# GitHub issue #293 — proposed update (English)

**Confirmed on one Lenovo Tab M10 3rd Gen TB328FU, Android 12, `TB328FU_S200162_250825_ROW`, Unisoc T610/UMS512, active slot A (October 17, 2026).**

I was able to **unlock the bootloader persistently and then obtain Magisk root**. The tested RAM chain was adapted from the FDL1/cboot method of TomKing062's CVE-2022-38694 project. It used the device's own S200162 U-Boot, and loaded FDL1, cboot, teecfg, trustos, and SML to RAM; it did not explicitly flash cboot to `uboot_a` or erase `splloader`.

The notable part: **`spd_dump` printed `timeout reached` after sending SML, then exited with code 1. The unlock nevertheless succeeded on this device.** The timeout is **not** proof of success and must not be ignored on other devices. This was the observed ending:

```text
SEND ...\fdl1-boot-v9.bin to 0x5500
EXEC FDL1
CHECK_BAUD FAIL
CHECK_BAUD FDL1
SEND ...\cboot-v9-S200162.bin to 0x9efffe00
SEND ...\teecfg-ram.bin to 0x9403fe00
SEND ...\trustos-ram.bin to 0x9405fe00
SEND ...\sml-ram.bin to 0x93fffe00
timeout reached
Transport exit: 1
```

After forcing a restart, Android Recovery displayed `LOG FLAG IS: UNLOCK`, `Can't load Android system`, `init_user0_failed`, and `NEED TO WIPE USERDATA`. `Try again` returned to Recovery. I had no user data to preserve, so I performed a **factory reset**, after which Android booted successfully.

**Unlock verification (repeated after another normal reboot):**

```text
adb shell getprop ro.boot.flash.locked         -> 0
adb shell getprop ro.boot.verifiedbootstate   -> orange
adb shell getprop ro.boot.vbmeta.device_state -> unlocked
```

I then patched a fresh stock `boot_a` image using **Magisk 30.7**, flashed `boot_a` on slot A via Fastboot and confirmed root:

```text
adb shell su -c id
uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0
```

Stock `boot_a` SHA-256: `0d699f4ca7710f4c8f87dbc8c60b94e1621708d2bc5e474fdf0d013a25e89560`. The original boot image is Android Boot v4 with a ramdisk; `init_boot_a` was blank on this device. The ramdisk was patched while the kernel bytes remained identical.

**Five tested RAM file SHA-256 checksums:**

```text
f0b87ca029eec5ddd3cce7d654d733d182996989eb8e5c729f9748f72806964d  fdl1-boot-v9.bin
fd2698c4f19e24840d70b6cae65f46d322918e5ba105795f306b11ad00622025  cboot-v9-S200162.bin
0e47a51ad7596f43597e16373817926f8f5524a0fa7557aa8feb846c8f47ec9b  teecfg-ram.bin
29160f1f0a0e95619dc5a416daf2b2e8b5bc08037baf960cd3dafd5dc9180ed7  trustos-ram.bin
5e0e84e250ecf84dee588a58fde18054ddc8cf4da95c2404f26141868e19a5a5  sml-ram.bin
```

**WARNING:** One-device confirmation only, **not** a guarantee for other firmware revisions. RAM-executed code can make persistent changes, trigger Recovery, invalidate encrypted userdata, or render the device unbootable. Never blindly erase `splloader` or flash patched cboot to `uboot_a`. Ensure complete backups and a recovery path; verify model/build/hashes first. This is an adaptation of TomKing062's research, not a claim of having discovered a new vulnerability.

Full step-by-step instructions, offline checksum verification and a redacted log are available in the accompanying Markdown guide. Thanks to TomKing062 and all project contributors.
