# Root Magisk — Lenovo TB328FU S200162

**Testé sur un seul exemplaire le 17/10/2026.** Les commandes ci-dessous reproduisent le dossier Windows d’origine `C:\TB328FU\files`. Dans ce dépôt, les outils sont dans `tools/v9/` et les fichiers privés dans `local/` : voir `LOCAL_FILES.md`.

## Méthode réellement validée

### Magisk 30.7 sur le firmware Lenovo d'origine

### 8.1 Pourquoi conserver la ROM Lenovo

Le bootloader déverrouillé permet de corriger l'image officielle **`boot_a`**. Changer de ROM n'est pas nécessaire pour obtenir `su` ; une GSI ou une ROM non prévue pour ce modèle aurait complexifié le diagnostic et la récupération.

### 8.2 Images d'origine relevées **après déverrouillage**

Le propriétaire a conservé une copie fraîche de `boot_a` et `init_boot_a` en utilisant le FDL2 standard en lecture seule. Exemple de session de lecture :

```bat
cd /d C:\TB328FU\files
spd_dump.exe --wait 120 exec_addr 0x3ee8 fdl fdl1-dl.bin 0x5500 fdl fdl2-dl.bin 0x9efffe00 exec
```

À `FDL2 >` :

```text
path ROOT_BACKUP
r boot_a
r init_boot_a
```

Après les lectures terminées :

```text
reset
```

Sur l'appareil testé :

| Fichier | Taille | Résultat |
|---|---:|---|
| `ROOT_BACKUP\boot_a.bin` | 67 108 864 octets (64 Mio) | **Android Boot v4**, noyau + ramdisk présents |
| `ROOT_BACKUP\init_boot_a.bin` | 8 388 608 octets (8 Mio) | **entièrement rempli de zéros** ; ne pas patcher |

**SHA-256 de l'image d'origine effectivement patchée :**

```text
0d699f4ca7710f4c8f87dbc8c60b94e1621708d2bc5e474fdf0d013a25e89560  boot_a.bin
```

Cette empreinte a été vérifiée par `certutil` sur Windows **avant** la copie sur la tablette. Conserver cette image stock intacte en plusieurs exemplaires.

### 8.3 Modification du ramdisk dans l'application Magisk

Version observée : **Magisk 30.7 (30700)** téléchargée via la publication officielle : https://github.com/topjohnwu/Magisk/releases

Le dossier `files` ne contenant pas nécessairement `adb.exe` dans le PATH, une commande entièrement qualifiée évite l'erreur « adb n'est pas reconnu » :

```bat
cd /d C:\TB328FU\files
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" devices
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" push "ROOT_BACKUP\boot_a.bin" "/sdcard/Download/boot_a.img"
```

Sur la tablette, dans Magisk : **Installer → Sélectionner et corriger un fichier → `Download/boot_a.img`**. La capture d'écran de l'essai indiquait `Stock boot image detected`, `Patching ramdisk`, `Repacking boot image`, puis **`All done!`**. La sortie est un nom variable de forme `magisk_patched-30700_XXXXX.img`.

Récupération sous Windows :

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell ls -lh /sdcard/Download/magisk_patched*
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" pull "/sdcard/Download/magisk_patched-30700_XXXXX.img" "magisk_patched.img"
```

**Remplacer `XXXXX` par le nom réellement créé**. Ne pas récupérer un patch Magisk réalisé sur un autre appareil.

### 8.4 Contrôle de l'image patchée réellement utilisée

| Propriété | Stock `boot_a.bin` | `magisk_patched.img` |
|---|---|---|
| Taille | 67 108 864 | 67 108 864 |
| Signature d'en-tête | `ANDROID!` | `ANDROID!` |
| Format | Android Boot v4 | Android Boot v4 |
| Taille noyau | 37 632 512 | 37 632 512 |
| SHA-256 noyau | `23dc040a371cfeb45653d3216cee2f313e54e64ab10faba5572aa4151ce3a652` | **identique** |
| Taille ramdisk | 2 353 747 | **2 230 882** |
| SHA-256 du fichier entier | `0d699f4ca7710f4c8f87dbc8c60b94e1621708d2bc5e474fdf0d013a25e89560` | `5c99161ebcd93e0786421608a4dd1950a517db5e5e02229413daf9383c499cfd` |

Ces informations ont été **recalculées directement sur les deux binaires fournis**. La conservation exacte du noyau et la modification du ramdisk sont cohérentes avec la méthode Magisk ; **elles ne prouvent pas à elles seules que l'image démarrera**. Le succès root a été confirmé ensuite sur l'appareil.

### 8.5 Flashage sur le slot A et redémarrage

Dans le dossier où se trouve `magisk_patched.img` :

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" reboot bootloader
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" devices
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" getvar current-slot
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" getvar unlocked
```

Observations de l'essai : le périphérique était détecté, `current-slot: a`, et `unlocked:` **ne renseignait aucune valeur**. L'état déverrouillé avait été confirmé auparavant par Android.

La commande d'installation de l'image Magisk sur **le slot A uniquement** était :

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" flash boot_a magisk_patched.img
```

Après **confirmation de réussite du flash** (aucun message `FAILED`), redémarrage :

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" reboot
```

**Ne pas modifier `init_boot_a`, `vbmeta` ni les autres partitions pour cette méthode. Ne jamais reverrouiller le bootloader avec un `boot_a` modifié.** Le journal Fastboot complet du flash n'a pas été transmis dans la conversation : l'installation est corroborée par le fonctionnement root ensuite, et non par une preuve indépendante de la console de flash.

### 8.6 Preuve finale de root

Après démarrage Android et acceptation éventuelle de l'autorisation Magisk :

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" shell su -c id
```

**Réponse effectivement fournie par l'appareil :**

```text
uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0
```

Le préfixe SELinux `u:r:magisk:s0` et l'UID 0 confirment que le gestionnaire Magisk a accordé les privilèges root au shell ADB.

---

Voir également [dépannage](DEPANNAGE_FR.md) et [déverrouillage](DEVERROUILLAGE_FR.md).
