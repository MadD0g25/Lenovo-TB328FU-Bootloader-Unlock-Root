# Lenovo Tab M10 (3rd Gen) TB328FU — S200162 bootloader unlock & Magisk root

**Languages:** **[English](README.md)** · **[Français](README.fr.md)**

> **Confirmed on one physical tablet, 17 October 2026:** Lenovo TB328FU, Unisoc T610 / UMS512, Android 12, firmware **`TB328FU_S200162_250825_ROW`**, slot **A**. A RAM-only FDL1/cboot/TEE/SML experiment was followed by a **persistent unlocked bootloader**. Stock `boot_a` was then patched with **Magisk 30.7** and **root access succeeded** (`uid=0(root)`). Not an officially supported Lenovo procedure and **not validated on a second device**.

## Verified evidence

| Check | Original | After V9 + reboot |
| --- | --- | --- |
| `ro.boot.flash.locked` | `1` | **`0`** |
| `ro.boot.verifiedbootstate` | `green` | **`orange`** |
| `ro.boot.vbmeta.device_state` | locked | **`unlocked`** |
| `adb shell su -c id` | unavailable | **`uid=0(root) ... context=u:r:magisk:s0`** |

**Unusual but essential:** `spd_dump` printed **`timeout reached`** immediately after sending `sml-ram.bin` and returned exit code 1. Nevertheless, after a Recovery screen displaying `LOG FLAG IS: UNLOCK`, a factory reset (user data loss), and another Android reboot, the three bootloader properties consistently indicated unlocked. **A timeout on another tablet is NOT evidence of success.** Do not repeatedly run the exploit just because you see this message.

### Safety / supported scope

- This is an advanced, **high-risk** experiment using CVE-2022-38694 and unsigned boot-stage code. It can permanently change secure state, invalidate file-based encryption, force a factory reset, or brick the device. Prepare an exact stock firmware and a tested recovery method.
- Verify **TB328FU + exact S200162 build + slot A** and all SHA-256 hashes. **STOP on mismatch.** Do not apply the same offsets to TB328XU, other firmware versions or slot B without independent analysis.
- **Do not erase `splloader`**, do not flash patched cboot into `uboot_a`, do not blindly write `miscdata` and do not relock after installing Magisk.
- **The successful root patch must be made from YOUR OWN fresh stock `boot_a` on YOUR tablet.** Never flash the sample/root image from another device.

## Get started

1. **[Unlock guide (English)](UNLOCK_EN.md)** — exact V9 RAM order, preflight, failure conditions, post-run Recovery and proof.
2. **[Root guide (English)](ROOT_EN.md)** — Magisk 30.7, fresh `boot_a`, slot-A Fastboot and recovery.
3. **[Troubleshooting (English)](TROUBLESHOOTING_EN.md)** — especially how to interpret the timeout.
4. **[Unlock guide (français)](DEVERROUILLAGE_FR.md)** / **[Root guide (français)](ROOT_FR.md)** / **[Dépannage](DEPANNAGE_FR.md)**.
5. **[Exact file SHA-256 and evidence](SHA256SUMS.txt)** / **[Redacted V9 log](V9_UNLOCK_TIMEOUT_REDACTED.log)**.
6. **[Source and licenses](ATTRIBUTION_AND_LICENSES.md)** / **[how to prepare your local binaries](LOCAL_FILES.md)**.

## Repository layout — guides available at the root

```
README.md / README.fr.md
UNLOCK_EN.md / ROOT_EN.md / TROUBLESHOOTING_EN.md
DEVERROUILLAGE_FR.md / ROOT_FR.md / DEPANNAGE_FR.md
SHA256SUMS.txt / V9_UNLOCK_TIMEOUT_REDACTED.log / CONFIRMATIONS.md
tools/v9/sources/     Original V9 Python sources
scripts/windows/      Guarded Windows scripts
local/                Local firmware and utilities (NEVER publish)
```

All guides are linked **from the repository root**, so GitHub links work whether the project is cloned or viewed online. The ZIP itself has **no parent folder**.

This **public repository package intentionally omits** `spd_dump.exe`, its DLLs, stock Lenovo partitions, patched RAM/boot images, personal logs and device identifiers. They may be proprietary or device-specific. A **separate private archive** preserves the exact validated V9 materials. Read [LOCAL_FILES.md](LOCAL_FILES.md) to set it up. The V9 source can rebuild the RAM bundle **only** from verified exact-build inputs; no other versions are claimed compatible.

### Attribution

This is a device-specific adaptation and one-device success report **building on** [TomKing062's CVE-2022-38694 project](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader), its [FDL1 method](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/patch_do_cboot%E2%80%90FDL1) and [AddSupportToModel](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/AddSupportToModel). This report is not a claim to have discovered CVE-2022-38694. Related: [TB328FU issue #293](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/issues/293). Magisk is by topjohnwu; download only from [official releases](https://github.com/topjohnwu/Magisk/releases).
