# Observed successful results / Résultats observés (2026-10-17)

- Device: Lenovo Tab M10 3rd Gen TB328FU, Android 12, exact build `TB328FU_S200162_250825_ROW`, slot `_a`.
- Before V9: `ro.boot.flash.locked=1`, `ro.boot.verifiedbootstate=green`.
- V9 USB ending: `timeout reached` / `Transport exit: 1` (does **NOT** independently prove unlock).
- Android Recovery after RAM experiment: `LOG FLAG IS: UNLOCK`, `init_user0_failed`, `NEED TO WIPE USERDATA`; the user accepted a factory reset because no data needed preservation.
- After Android reboot and an **additional normal reboot**: `ro.boot.flash.locked=0`, `ro.boot.verifiedbootstate=orange`, `ro.boot.vbmeta.device_state=unlocked`.
- Stock image from the tested tablet: `boot_a` Android Boot v4, 64 MiB, root Magisk 30.7 image structurally verified, then flashed in active slot A.
- Final live ADB `su -c id`: `uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0`.

**Limitations:** one successful device, no original full hardware-*.log file supplied, no complete Fastboot-flash console log retained, no validated firmware variant or slot-B case, no verified internal TrustOS trace. Binary material may include copyrighted vendor components and remains in the separate PRIVATE archive.
