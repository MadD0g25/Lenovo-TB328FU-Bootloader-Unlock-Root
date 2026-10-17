# Retour d'expérience proposé pour le ticket GitHub n°293

**Succès sur un exemplaire Lenovo TB328FU sous Android 12 / `TB328FU_S200162_250825_ROW`, Unisoc T610/UMS512, slot A (17/10/2026).**

Le bootloader a été déverrouillé de façon **persistante**, puis Magisk 30.7 a permis d'obtenir un accès `uid=0(root)`. La chaîne expérimentale V9, adaptée des travaux de TomKing062, a chargé en RAM : FDL1 modifié à `0x5500`, cboot S200162 à `0x9efffe00`, teecfg à `0x9403fe00`, TrustOS à `0x9405fe00`, SML à `0x93fffe00`, puis a appelé `exec`. Le lanceur n'a pas effectué de flash explicite de `uboot_a` ou d'effacement de `splloader`.

**Important :** `spd_dump` a affiché `timeout reached` après SML et a terminé avec `Transport exit: 1`. Après redémarrage, le Recovery affichait `LOG FLAG IS: UNLOCK`, `init_user0_failed` et demandait un effacement de `userdata`. Les données n'étant pas importantes pour cet essai, une réinitialisation d'usine a été faite. Android a ensuite démarré et les commandes ADB ont donné `flash.locked=0`, `verifiedbootstate=orange`, `vbmeta.device_state=unlocked`, encore confirmés après un autre redémarrage.

Magisk a corrigé l'image officielle **`boot_a` Android Boot v4**, tandis que `init_boot_a` était vide. Fastboot a été utilisé pour installer le `boot_a` corrigé. Le résultat final `adb shell su -c id` a été **`uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0`**.

**Ce n'est pas une garantie pour un autre exemplaire.** Le timeout ne prouve ni succès ni échec sans vérification ultérieure. Risques sérieux de perte de données et de brick. Guides FR/EN, empreintes SHA-256, source V9 et journal anonymisé sont inclus dans le dépôt associé. Merci à TomKing062 et aux contributeurs pour l'exploitation BootROM et la méthode FDL1 originale.
