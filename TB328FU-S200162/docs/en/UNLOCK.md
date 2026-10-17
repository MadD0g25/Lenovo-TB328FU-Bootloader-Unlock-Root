# Persistently unlock the Lenovo TB328FU bootloader — confirmed S200162 field report

**Scope of the confirmed experiment:** one Lenovo Tab M10 3rd Gen **TB328FU**, Unisoc T610 / UMS512, **Android 12 `TB328FU_S200162_250825_ROW`**, eMMC, active slot **A**. Windows 10, Python 3, `spd_dump` branch `main` / SHA1 `d24c21a0c93a545c0130668caa1826d59ceebe48`. Experiment: 17 October 2026. **Not validated on any other unit or firmware.**

> **DANGER:** This is a high-risk physical BootROM exploit followed by execution of an unsigned, modified boot chain in RAM. Although the runner itself does not send an explicit partition-flash command, the RAM-executed cboot may persist changes to `miscdata`, invalidate encryption metadata, cause loss of *all* user data, or brick the device. The successful experiment DID require a **factory data reset**. Ensure all data is backed up and you have a known-good stock S200162 recovery path. Do not erase `splloader`; two historical reads produced entirely zero-filled files and must never be used as recovery images.

## 1. Observed result

| Android property | Before | After V9 and again after an independent reboot |
| --- | --- | --- |
| `ro.boot.flash.locked` | `1` | **`0`** |
| `ro.boot.verifiedbootstate` | `green` | **`orange`** |
| `ro.boot.vbmeta.device_state` | reported locked by stock U-Boot | **`unlocked`** |
| `ro.boot.slot_suffix` | `_a` | **`_a`** |

Note: Lenovo Fastboot reported `unlocked:` with an *empty value* to `fastboot getvar unlocked`. This is not a positive locked state; use the three Android properties after a normal boot instead.

## 2. Materials and Windows layout

- Windows 10 x64 PC, working USB data cable, working Unisoc/Spreadtrum driver (`SPRD U2S Diag (COM3)` during the trial; COM port number can vary).
- Python 3 accessible as `py -3`, Android Platform Tools / `adb.exe` and `fastboot.exe`.
- `spd_dump.exe` matching the known working build **together in the same folder** with `Channel9.dll`, `Channel.ini`, `custom_exec_no_verify_3ee8.bin`. **Do not trust rehosted executables**; verify SHA-256 as below.
- Original S200162 partition dumps, particularly `uboot_a`, `sml_a`, `teecfg_a`, `trustos_a`, `miscdata` and `boot_a`, plus verified stock firmware and a recovery plan.
- The exact V9 source (`tools/v9/sources/tb328fu_v9.py`) and a prebuilt `prepared_current` bundle that matches **all five RAM SHA-256 hashes** in `docs/evidence/SHA256SUMS.txt`. If you do not have permission to redistribute these OEM-derived materials, generate them locally from your **own exact-match firmware/dumps** using the V9 `build` command.

Place the working files as follows:

```text
<repo>/
  tools/v9/sources/tb328fu_v9.py
  scripts/windows/*.cmd
  local/                                  <- ignored by Git
    spd_dump/spd_dump.exe
    spd_dump/Channel9.dll
    spd_dump/Channel.ini
    spd_dump/custom_exec_no_verify_3ee8.bin
    V9/prepared_current/                  <- generated or private bundle
      manifest.json
      fdl1-boot-v9.bin
      cboot-v9-S200162.bin
      teecfg-ram.bin
      trustos-ram.bin
      sml-ram.bin
    backups/                              <- your own stock images
```

The old original user session used a different directory under Downloads; these repo-relative paths are equivalent. The launch source is unchanged.

## 3. Identity pre-check, read only

With Android booted and ADB USB debugging authorized:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" devices
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.product.model
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.build.display.id
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.boot.slot_suffix
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.boot.flash.locked
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.boot.verifiedbootstate
```

Pre-unlock expected: `TB328FU`, `TB328FU_S200162_250825_ROW`, `_a`, `1`, `green`. **Stop if any differs. Stop if already unlocked.** Enable OEM unlocking in Android developer options before the experiment.

## 4. Exact working binaries and addresses

The five tested RAM files and their exact SHA-256 appear in [SHA256SUMS](../evidence/SHA256SUMS.txt). They must be checked **before** any device action. These are not interchangeable with older SPL/cboot experiments, nor with the V7 images.

| Transfer order | File | Target RAM address |
| ---: | --- | --- |
| 1 | `fdl1-boot-v9.bin` | `0x5500` |
| 2 | `cboot-v9-S200162.bin` | `0x9efffe00` |
| 3 | `teecfg-ram.bin` | `0x9403fe00` |
| 4 | `trustos-ram.bin` | `0x9405fe00` |
| 5 | `sml-ram.bin` | `0x93fffe00` |

Execution begins via BootROM `exec_addr 0x3ee8` using the supplied `custom_exec_no_verify_3ee8.bin` during the initial FDL1 stage. The trailing `exec` is issued after SML, and there is **no explicit `write_part`, `erase_part`, or `splloader` erase** in this runner.

**Source adaptation details:** The original V9 Python source asserts exact SHA-256 hashes of the input S200162 `uboot_a` and FDL1, checks the DHTB payloads for `sml_a`, `teecfg_a`, and `trustos_a`, patches a precise ARM64 hook/cave in U-Boot for `set_lock_status(1)`, and prepares FDL1 for RAM loading. The patched cboot no longer has a valid vendor RSA signature; it is **RAM-only**. The CPU instructions are based on original CVE-2022-38694/FDL1 research, not a newly discovered exploit.

## 5. Build V9 RAM files from EXACT stock dumps (alternative to a private prebuilt bundle)

The source code is provided in `tools/v9/sources/tb328fu_v9.py`. Copy these five **exactly matching, SHA-verified** inputs to `local/backups/`: `uboot_a.bin`, `sml_a.bin`, `teecfg_a.bin`, `trustos_a.bin` and, separately in `local/assets/`, `fdl1-dl.bin`, `fdl2-dl.bin`. The source refuses unknown hashes and incompatible payloads. From the repo root:

```bat
py -3 "tools\v9\sources\tb328fu_v9.py" build --backup "local\backups" --assets "local\assets" --output "local\V9\prepared_current"
```

The output folder must not already contain files. **If any hash or DHTB check fails: stop.** A complete device-specific backup is needed; do not reuse dumps from a different S200162 tablet without understanding per-device differences. A captured `splloader.bin` filled with zero bytes is NOT usable for any recovery action.

## 6. Offline plan — the exact first successful preflight

From the repo root:

```bat
py -3 "tools\v9\sources\tb328fu_v9.py" plan --bundle "local\V9\prepared_current" --spd "%CD%\local\spd_dump\spd_dump.exe"
```

Expected summary:

```text
STATUS: EXPERIMENTAL_NOT_HARDWARE_VALIDATED input completeness: True
... spd_dump.exe --wait 120 exec_addr 0x3ee8 ... sml-ram.bin 0x93fffe00 exec
OFFLINE PLAN ONLY; no process/device invoked.
```

The string `EXPERIMENTAL_NOT_HARDWARE_VALIDATED` is the **historic label embedded in the originally tested runner**. It is not a statement that the *October 17, 2026* success never happened; importantly it also does not turn the code into a tested multi-device release.

## 7. Execute the high-risk RAM experiment

**Only after full backup and your own informed decision to accept data loss and brick risk**, while Android initially runs and ADB sees the correct device:

```bat
py -3 "tools\v9\sources\tb328fu_v9.py" run --bundle "local\V9\prepared_current" --spd "%CD%\local\spd_dump\spd_dump.exe" --adb "C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" --execute
```

The V9 runner verifies the exact firmware, slot and initial locked state before continuing. During the observed run it requested the literal acknowledgment:

```text
AUTORISER V9 PERTE DONNEES
```

It then asked to power the tablet off, disconnect it, and press Enter before listening for the BootROM USB connection. When `Waiting for dl_diag connection (120s)` appears, press and hold **Volume+ and Volume−** on the powered-off tablet and connect USB. The original tablet sometimes entered BootROM after a failed first connection; a Windows USB sound alone is not proof of protocol readiness. The successful connection showed `BSL_REP_VER: "SPRD3\0"`, then FDL1 `Spreadtrum Boot Block version 1.1`.

### EXACT observed console ending: TIMEOUT ≠ FAILURE OR SUCCESS

```text
branch:main, sha1:d24c21a0c93a545c0130668caa1826d59ceebe48
Waiting for dl_diag connection (120s)
Successfully connected to port: 3
CHECK_BAUD bootrom
BSL_REP_VER: "SPRD3\0"
CMD_CONNECT bootrom
current exec_addr is 0x3ee8
SEND ...\fdl1-boot-v9.bin to 0x5500
SEND custom_exec_no_verify_3ee8.bin to 0x3ee8
EXEC FDL1
CHECK_BAUD FAIL
CHECK_BAUD FDL1
BSL_REP_VER: "Spreadtrum Boot Block version 1.1\0"
CMD_CONNECT FDL1
CHANGE_BAUD FDL1 to 921600
KEEP_CHARGE FDL1
SEND ...\cboot-v9-S200162.bin to 0x9efffe00
SEND ...\teecfg-ram.bin to 0x9403fe00
SEND ...\trustos-ram.bin to 0x9405fe00
SEND ...\sml-ram.bin to 0x93fffe00
timeout reached
Transport exit: 1
NO SUCCESS CLAIM. Check stock Android lock state and a fresh miscdata read. No automatic wipe/reset.
```

`CHECK_BAUD FAIL` was followed by `CHECK_BAUD FDL1` success. The later `timeout reached` was accompanied by a nonzero transport exit but, **on this one tested tablet**, the eventual outcome was an unlocked bootloader. Other timeouts can indicate failed execution or a transport issue. The original full `hardware-*.log` file was not uploaded; the available log is the **user-supplied console transcript**, redacted for publication.

## 8. Recovery event and factory reset

After V9 the device initially had a black screen, then on restart Android Recovery showed:

```text
Can't load Android system. Your data may be corrupt.
*****NEED TO WIPE USERDATA*****
REASON IS: (init_user0_failed)
LOG FLAG IS: UNLOCK
```

`Try again` looped back to Recovery. The tablet owner had explicitly stated no important data were stored, then chose **Factory data reset** (irreversibly wipes user data). Android subsequently booted. This can be consistent with changed encryption/security state; the precise internal cause was **not proven**. **Do not factory-reset someone else's device or one containing data that must be recovered.** The Google account originally tied to a device may be requested again after reset (FRP).

## 9. Confirm persistent unlock, not merely a recovery flag

With Android booted and ADB reauthorized:

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.boot.flash.locked
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.boot.verifiedbootstate
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell getprop ro.boot.vbmeta.device_state
```

Observed: **`0`, `orange`, `unlocked`**. The owner **repeated these checks after another normal reboot**, with the same result. This is stronger evidence than the ambiguous Recovery text or `timeout reached`. Do not infer unlock from a single flag alone. The next step, tested separately, was [Magisk root](ROOT.md).

## 10. Attribution and limits

Based on [TomKing062 CVE-2022-38694](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader), [AddSupportToModel](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/AddSupportToModel), [RAM/FDL1 guide](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/patch_do_cboot%E2%80%90FDL1). An independent [TB328FU issue #293](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/issues/293) described similar restrictions; do not confuse that issue author's results with the separately documented success here. We have **no proof** the exact sequence works on all units, other builds, or slot B.
