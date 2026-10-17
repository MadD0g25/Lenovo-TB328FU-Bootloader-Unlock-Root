# Lenovo Tab M10 (3e génération) TB328FU — déverrouillage et root Magisk S200162

**Langues :** **[Français](README.fr.md)** · **[English](README.md)**

> **Réussite confirmée sur une seule tablette le 17 octobre 2026 :** Lenovo TB328FU, Unisoc T610 / UMS512, Android 12, firmware **`TB328FU_S200162_250825_ROW`**, slot **A**. La chaîne expérimentale FDL1/cboot/TEE/SML exécutée en RAM a été suivie d’un **bootloader déverrouillé de manière persistante**. L’image officielle `boot_a` a ensuite été corrigée par **Magisk 30.7**, avec **root fonctionnel** (`uid=0(root)`). Ce n’est ni une procédure officielle Lenovo ni une méthode validée sur plusieurs exemplaires.

## Preuves

| Contrôle | Avant | Après V9 et redémarrage |
| --- | --- | --- |
| `ro.boot.flash.locked` | `1` | **`0`** |
| `ro.boot.verifiedbootstate` | `green` | **`orange`** |
| `ro.boot.vbmeta.device_state` | locked | **`unlocked`** |
| `adb shell su -c id` | indisponible | **`uid=0(root) ... context=u:r:magisk:s0`** |

**Point capital :** `spd_dump` a affiché **`timeout reached`** immédiatement après le transfert de `sml-ram.bin`, puis a terminé avec le code 1. Pourtant, après un Recovery indiquant `LOG FLAG IS: UNLOCK`, une **réinitialisation d'usine**, puis un redémarrage Android, l'état déverrouillé a été confirmé. **Le timeout, seul, n'est jamais une preuve de réussite.** Ne pas répéter aveuglément V9.

### Sécurité et compatibilité

- Expérience **très risquée** exploitant CVE-2022-38694 et des étages de démarrage modifiés. Risque de perte de données, réinitialisation, bootloop ou brick. Prévoir firmware stock exact et méthode de récupération.
- Vérifier **TB328FU + S200162 exact + slot A + SHA-256**. Arrêter au moindre écart. Pas de validation pour TB328XU, d'autres versions ou le slot B.
- **Ne pas effacer `splloader`**, ne pas flasher cboot expérimental dans `uboot_a`, ne pas écrire `miscdata` arbitrairement et ne pas reverrouiller après Magisk.
- Le `boot_a` Magisk doit provenir d'un **dump frais de votre propre tablette**. Ne jamais utiliser l'image patchée d'un autre appareil.

## Parcours recommandé

1. **[Déverrouillage détaillé](docs/fr/DEVERROUILLAGE.md)** : matériel, Windows, V9, transfert RAM, Recovery et vérification.
2. **[Root Magisk détaillé](docs/fr/ROOT.md)** : image `boot_a`, Magisk 30.7, Fastboot et retour arrière.
3. **[Dépannage](docs/fr/DEPANNAGE.md)** : timeout, erreur USB, Recovery, restauration.
4. **[Documentation anglaise](docs/en/UNLOCK.md)** et [root](docs/en/ROOT.md).
5. **[Empreintes SHA-256](docs/evidence/SHA256SUMS.txt)** et [journal V9 anonymisé](docs/evidence/V9_UNLOCK_TIMEOUT_REDACTED.log).
6. **[Fichiers à fournir localement](LOCAL_FILES.md)** et [attribution/licences](ATTRIBUTION_AND_LICENSES.md).

## Structure et publication

Le dépôt public contient les guides FR/EN, les sources Python V9, les scripts CMD de contrôle, des preuves anonymisées et des empreintes. Il **n'inclut pas par défaut** les images Lenovo/Unisoc, `spd_dump.exe`, ses DLL, une image Magisk propre à un appareil ni des identifiants personnels. Ces composants peuvent être propriétaires ou spécifiques à l’appareil. L'**archive privée complète** contient les éléments conservés de l'essai réussi ; elle ne doit pas être publiée telle quelle sans vérification des droits et de son contenu.

### Crédits

Adaptation de travaux de **TomKing062** : [CVE-2022-38694](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader), [méthode FDL1](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/patch_do_cboot%E2%80%90FDL1), [nouveaux appareils](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/AddSupportToModel) et [ticket n°293](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/issues/293). Le déverrouillage constaté ne doit pas être présenté comme une découverte indépendante de CVE-2022-38694. Magisk : [dépôt officiel](https://github.com/topjohnwu/Magisk/releases).
