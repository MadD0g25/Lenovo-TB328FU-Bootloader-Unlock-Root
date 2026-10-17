# Troubleshooting, stop conditions and recovery

This is a one-device technical account, **not a guarantee** that a damaged second tablet can be recovered. Risk is highest in the boot stages and around encrypted userdata.

| Symptom | What it means / next action |
| --- | --- |
| `adb` is not recognized in Windows CMD | Run the complete path to `adb.exe` or add Platform Tools to `%PATH%`. |
| `Successfully connected to port: 3` then `usb_send failed (0 / 1)` | USB enumeration occurred but the protocol handshake failed. Stop, check proper BootROM state, cable, driver and stale sessions. |
| `Connection failed` | No compatible BootROM session established within 120 seconds; Windows USB connect sounds alone are not proof. |
| `CHECK_BAUD FAIL` then `CHECK_BAUD FDL1` success | An intermediate negotiation failed but subsequently recovered. The tested run proceeded to transfer all components. |
| `timeout reached` immediately after `SEND sml-ram.bin` | No expected response to `exec`. **Could be a successful side effect, a crash, or failure. DO NOT retry automatically.** Check Recovery and actual Android bootloader state after a controlled boot. |
| Blank screen after RAM experiment | Boot-stage transition not verified. Do not flash or erase more partitions. On the tested tablet a long Power hold permitted restart, but that is not guaranteed. |
| Recovery: `LOG FLAG IS: UNLOCK`, `init_user0_failed`, `NEED TO WIPE USERDATA` | Bootloader may have changed state, and encrypted user data is inaccessible. The tested user explicitly had no data to keep and performed Factory data reset. **Factory reset irreversibly deletes user data.** |
| `fastboot getvar unlocked` returns blank | This Fastboot implementation does not provide the value. Check `ro.boot.flash.locked`, `ro.boot.verifiedbootstate`, `ro.boot.vbmeta.device_state` after Android boots. |
| Bootloop after Magisk | If Fastboot works, restore only the **fresh original** `boot_a` image from the identical build/slot A. |
| Saved `splloader.bin` consists only of zeros | **Do not flash it.** This is not a valid restorable SPL image. |

## Recovery principles

1. Preserve original backups, particularly `uboot_a`, `boot_a`, `miscdata`, and *actual* stock S200162 recovery firmware. Do not confuse old 2025-02 U-Boot with 2025-08 S200162 U-Boot.
2. Never rewrite unknown or zero-filled `splloader`; never use arbitrary `w_force`/erases or trust a public claim of a universal unlock command.
3. Magisk rollback is possible via `fastboot flash boot_a ROOT_BACKUP\boot_a.bin` **only if Fastboot is operational and the backup matches the exact active slot/firmware**.
4. A reset after `init_user0_failed` was performed **only** because data loss was accepted. Otherwise, stop and consider professional recovery options before an irreversible wipe.
5. Preserve a console log and list every actual write. A timeout is not a bootloader state indicator.

## Evidence limits

- The shared V9 log is a user-provided terminal transcript, *not* the original bytes of `hardware-*.log`.
- Root was demonstrated by live `su -c id`; the exact Fastboot flash transcript was not retained.
- There is **one** validated successful unit. No claim is made about different builds, warranty, safety of repeated attempts, or exact cryptographic mechanics in TrustOS.
