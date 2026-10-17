# Lenovo Tab M10 TB328FU — déverrouillage du bootloader et root Magisk

**Compte rendu technique et procédure reproductible — 17 octobre 2026 — révision 2.0 — dépôt GitHub bilingue**

> **Résultat réellement observé :** sur **un exemplaire** Lenovo Tab M10 (3e génération) TB328FU, firmware `TB328FU_S200162_250825_ROW` (Android 12), une chaîne de démarrage expérimentale **FDL1 / cboot / TEE / SML en RAM** a été suivie d'un **déverrouillage persistant** du bootloader ; l'installation ultérieure de **Magisk 30.7** a obtenu un accès **root** confirmé par `uid=0(root)`. La méthode n'est ni officielle ni garantie sur un autre appareil.

**Avertissement majeur.** Cette procédure exploite une vulnérabilité BootROM, charge du code non signé, peut changer l'état sécurisé de l'appareil et **effacer ou rendre définitivement inaccessibles les données**. Le premier essai réussi a provoqué un passage en Recovery et a nécessité une **réinitialisation d'usine** sur l'exemplaire testé. Risque de blocage de démarrage ou de récupération impossible. Ne pas l'appliquer à une tablette contenant des données irremplaçables, et ne jamais effacer `splloader` à partir de ce guide. Le présent rapport est une observation de laboratoire, pas une promesse de réussite.

## 1. Résultat final et niveau de preuve

| Contrôle | Avant V9 | Après V9, **puis de nouveau après redémarrage** |
|---|---|---|
| `ro.boot.flash.locked` | `1` | **`0`** |
| `ro.boot.verifiedbootstate` | `green` | **`orange`** |
| `ro.boot.vbmeta.device_state` | `locked` d'après U-Boot | **`unlocked`** |
| `ro.boot.slot_suffix` | `_a` | **`_a`** |
| Accès Magisk `su` | absent | **`uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0`** |

**Ce qui est établi :** les propriétés d'état de bootloader ont persisté lors d'un redémarrage Android distinct et un shell Magisk a obtenu l'UID 0. **Ce qui n'est pas établi :** la reproductibilité sur un second appareil, l'origine exacte du `timeout reached`, le détail des opérations internes de TrustOS et la compatibilité d'autres firmwares. `getvar unlocked` était vide dans le Fastboot Lenovo ; **cela ne contredit pas** les autres éléments : la variable n'était simplement pas renseignée.

## 2. Matériel, version et dépendances

| Élément | Valeur observée |
|---|---|
| Modèle | Lenovo Tab M10 3rd Gen **TB328FU** |
| SoC | Unisoc T610 / **UMS512** |
| Build exact | **`TB328FU_S200162_250825_ROW`** |
| Android | 12 |
| Stockage / partitions | eMMC / 84 partitions listées par FDL2 |
| Slot actif testé | **A** (`_a`) |
| Hôte de l'essai | Windows 10 x64, Python 3, Minimal ADB and Fastboot |
| Outil USB | `spd_dump.exe`, `branch:main, sha1:d24c21a0c93a545c0130668caa1826d59ceebe48` |
| BootROM exploit | `exec_addr 0x3ee8` |
| Mode de connexion | Windows : `SPRD U2S Diag (COM3)` lors de l'essai (COM peut changer) |
| Magisk | 30.7 (`30700`), version affichée lors du patch |

**Restriction de compatibilité :** ne pas supposer que la méthode fonctionne sur TB328XU, S200157, d'autres lots TB328FU, d'autres versions Android ou un slot B. Aucun essai n'a confirmé ces variantes.

### 2.1 Préparatifs essentiels

1. Sauvegarder **toutes les données personnelles**. Prévoir le risque que la réinitialisation efface toutes les données et exige à nouveau le compte Google associé (FRP).
2. Disposer de l'image officielle complète **S200162** et d'un moyen de récupération. Conserver les partitions d'origine avant modifications, notamment `uboot_a`, `boot_a`, `miscdata`, `trustos_a`, `sml_a`, `teecfg_a`. Éviter toute restauration « tous azimuts ».
3. Utiliser les **binaires V9 identifiés par SHA-256** (section 3). La V7 précédente a échoué ; les anciennes images cboot/SPL ne sont pas interchangeables.
4. Activer **Débogage USB** et **Déverrouillage OEM** dans Options développeur. Vérifier que `adb devices` affiche `device` (et non `unauthorized`).
5. L'exécutable `spd_dump.exe` doit rester **avec** `Channel9.dll`, `Channel.ini` et `custom_exec_no_verify_3ee8.bin`, sinon son fonctionnement peut échouer. Utiliser de préférence le répertoire où il a déjà fonctionné.
6. Vérifier le modèle et **le build exact**. Arrêter immédiatement si différents.

### 2.2 Organisation Windows recommandée

Créer un répertoire de travail, par exemple `C:\TB328FU\files`. Y placer `spd_dump.exe` et ses dépendances, puis y **extraire** le dossier `TB328FU_V9_RAM` contenu dans l'archive V9 testée.

```text
C:\TB328FU\files\
  spd_dump.exe
  Channel9.dll
  Channel.ini
  custom_exec_no_verify_3ee8.bin
  TB328FU_V9_RAM\
    sources\tb328fu_v9.py
    prepared_current\
      fdl1-boot-v9.bin
      cboot-v9-S200162.bin
      teecfg-ram.bin
      trustos-ram.bin
      sml-ram.bin
```

**Important :** l'archive V9 du dossier personnel est une copie de conservation d'un **outil expérimental** ; les images Lenovo et autres composants tiers ont leurs propres droits de redistribution. `spd_dump.exe`, ses DLL, les sauvegardes privées et les images Magisk propres à l'appareil ne sont **pas** inclus dans le paquet public.

## 3. Empreintes exactes des cinq images RAM de l'essai réussi

Le script de lancement doit utiliser le sous-dossier **`prepared_current`**, pas `prepared_reference` ni les binaires V7. Les tailles et empreintes suivantes ont été recalculées à partir de l'archive V9 auditée qui a servi de base à l'essai :

| Fichier | Taille (octets) | SHA-256 |
|---|---:|---|
| `fdl1-boot-v9.bin` | 60 036 | `f0b87ca029eec5ddd3cce7d654d733d182996989eb8e5c729f9748f72806964d` |
| `cboot-v9-S200162.bin` | 909 188 | `fd2698c4f19e24840d70b6cae65f46d322918e5ba105795f306b11ad00622025` |
| `teecfg-ram.bin` | 124 052 | `0e47a51ad7596f43597e16373817926f8f5524a0fa7557aa8feb846c8f47ec9b` |
| `trustos-ram.bin` | 3 489 348 | `29160f1f0a0e95619dc5a416daf2b2e8b5bc08037baf960cd3dafd5dc9180ed7` |
| `sml-ram.bin` | 68 900 | `5e0e84e250ecf84dee588a58fde18054ddc8cf4da95c2404f26141868e19a5a5` |

Sur Windows, par exemple :

```bat
cd /d C:\TB328FU\files
certutil -hashfile "TB328FU_V9_RAM\prepared_current\fdl1-boot-v9.bin" SHA256
certutil -hashfile "TB328FU_V9_RAM\prepared_current\cboot-v9-S200162.bin" SHA256
```

Vérifier **les cinq** empreintes, manuellement ou à l'aide du programme `VERIFIER_ARCHIVE_ET_BOOT.py` inclus au dossier documentaire. **En cas de différence : arrêter.**

### 3.1 Origine technique du correctif

La méthode est une **adaptation pour TB328FU S200162** des travaux publics de TomKing062 relatifs à CVE-2022-38694 et à la technique `patch_do_cboot-FDL1`. Les étapes visent à charger et exécuter une chaîne de démarrage modifiée directement en RAM grâce au BootROM. Cela ne revient pas à flasher de manière permanente le FDL1 ou les composants TEE.

Dans cette version V9, le FDL1 expérimental configure le mode de démarrage et des arguments nécessaires au lancement de SML ; un `cboot` expérimental est généré à partir de l'U-Boot stock S200162, plutôt que d'une ancienne version. **Ce comportement a été analysé hors ligne et le résultat matériel a été observé, mais la séquence exacte exécutée à l'intérieur de TrustOS n'a pas été tracée.** Ne pas écrire `cboot-v9-S200162.bin` dans `uboot_a` : il est destiné à la **RAM**.

## 4. Vérifier les propriétés AVANT le déverrouillage

Sous Android, dans CMD :

```bat
adb devices
adb shell getprop ro.product.model
adb shell getprop ro.build.display.id
adb shell getprop ro.boot.slot_suffix
adb shell getprop ro.boot.flash.locked
adb shell getprop ro.boot.verifiedbootstate
```

**Résultat initial observé :** TB328FU, `TB328FU_S200162_250825_ROW`, `_a`, `1`, `green`. Les commandes Android sont ici des contrôles **en lecture seule**. Ne pas continuer si la tablette est déjà déverrouillée : aucun intérêt à reproduire l'exploit.

## 5. Déverrouillage : séquence V9 reproduisant l'essai du 17/10/2026

**ATTENTION — étape expérimentale susceptible de modifier `miscdata` et de rendre `userdata` illisible.** Même si la commande de transport n'envoie pas de `write_part`, le **code ARM64 exécuté en RAM** peut, lui, effectuer une modification persistante. Aucune garantie de récupération.

### 5.1 Contrôle hors ligne (obligatoire)

Dans CMD, en adaptant seulement le chemin de dossier :

```bat
cd /d C:\TB328FU\files
py -3 "TB328FU_V9_RAM\sources\tb328fu_v9.py" plan --bundle "TB328FU_V9_RAM\prepared_current" --spd "%CD%\spd_dump.exe"
```

Le script doit afficher :

```text
STATUS: EXPERIMENTAL_NOT_HARDWARE_VALIDATED input completeness: True
... spd_dump.exe --wait 120 exec_addr 0x3ee8 ... exec
OFFLINE PLAN ONLY; no process/device invoked.
```

**Interprétation :** le plan est valide hors ligne ; la commande **n'a rien fait sur la tablette**. Une validation de fichiers ne prédit pas un déverrouillage réussi.

### 5.2 Exécution de l'essai RAM (commande effectivement utilisée)

Le programme commence quand la tablette est allumée sur Android, reconnue par ADB. Sous Windows :

```bat
cd /d C:\TB328FU\files
py -3 "TB328FU_V9_RAM\sources\tb328fu_v9.py" run --bundle "TB328FU_V9_RAM\prepared_current" --spd "%CD%\spd_dump.exe" --adb "C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe" --execute
```

Adapter le chemin vers `adb.exe` si nécessaire. L'essai documenté a nécessité la saisie littérale de :

```text
AUTORISER V9 PERTE DONNEES
```

**Le texte n'annule pas les risques ; c'est une confirmation de consentement au risque.** Le programme demande d'éteindre complètement la tablette, de débrancher l'USB, puis d'appuyer sur **Entrée** pour se mettre en attente. Quand `Waiting for dl_diag connection (120s)` apparaît, maintenir **Volume + et Volume −**, brancher la tablette, puis attendre la connexion BootROM. Sur certaines tentatives antérieures, la première connexion échouait ; une activité sur le port COM ne signifie pas que le BootROM répond.

La séquence générée, à garder **dans cet ordre**, est :

```text
spd_dump.exe --wait 120 exec_addr 0x3ee8
    fdl fdl1-boot-v9.bin     0x5500
    fdl cboot-v9-S200162.bin 0x9efffe00
    fdl teecfg-ram.bin      0x9403fe00
    fdl trustos-ram.bin     0x9405fe00
    fdl sml-ram.bin         0x93fffe00
    exec
```

**Ce bloc est une représentation lisible**, pas une commande CMD à recopier avec ces noms abrégés. La commande réellement exécutée avec les chemins absolus est construite par `tb328fu_v9.py` ; ne pas remplacer le lanceur par une ligne reconstituée.

### 5.3 Journal terminal déterminant : `timeout reached` malgré le succès final

Les lignes ci-dessous reprennent **le journal effectivement partagé**, avec les chemins locaux raccourcis pour publication et sans numéro de série :

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
Transport exit: 1 Log: TB328FU_V9_RAM\prepared_current\hardware-20261017-080156.log
NO SUCCESS CLAIM. Check stock Android lock state and a fresh miscdata read. No automatic wipe/reset.
```

**Point crucial pour toute personne reproduisant l'essai :**

- `CHECK_BAUD FAIL` a été **suivi** de `CHECK_BAUD FDL1` réussi. Ce premier échec intermédiaire n'a pas empêché les transferts ultérieurs.
- `timeout reached` et `Transport exit: 1` sont **des informations du transport/protocole**, pas une lecture de l'état persistant du bootloader.
- Sur cet appareil, le **résultat final a bien été le déverrouillage** malgré le timeout. **Cela ne signifie absolument pas que tout timeout = succès**.
- Il ne faut **pas relancer V9 à l'aveugle** en réponse à ce message ; observer d'abord le comportement de l'appareil et l'état Android, afin d'éviter un deuxième changement inutile de l'état sécurisé.
- Le fichier original `hardware-20261017-080156.log` n'a pas été transmis ; le présent journal est la **transcription fournie par le propriétaire**, non une copie binaire de ce fichier.

## 6. Après V9 : écran noir, Recovery, données effacées

Sur cet exemplaire, après le timeout :

1. Écran noir initial. Le propriétaire a tenté un **redémarrage forcé par Power**.
2. Android Recovery a affiché :

```text
Can't load Android system. Your data may be corrupt.
*****NEED TO WIPE USERDATA*****
REASON IS: (init_user0_failed)
LOG FLAG IS: UNLOCK
```

3. L'option **`Try again`** retournait au même Recovery.
4. Le propriétaire a confirmé qu'il n'avait **aucune donnée importante** sur l'appareil. Il a alors effectué **`Factory data reset`** depuis Recovery.
5. Après réinitialisation, Android a démarré.

**Interprétation prudente :** `LOG FLAG IS: UNLOCK` est un indice apparu après l'essai, mais ce texte seul n'est pas une vérification finale. L'erreur `init_user0_failed` est compatible avec une perte d'accès aux données utilisateur chiffrées lors d'un changement de sécurité ; **le mécanisme exact n'a pas été établi**. Ne pas effacer les données d'un autre appareil si elles doivent être récupérées.

## 7. Vérification du véritable déverrouillage persistant

Une fois Android redémarré, reconnecter ADB et exécuter :

```bat
adb shell getprop ro.boot.flash.locked
adb shell getprop ro.boot.verifiedbootstate
adb shell getprop ro.boot.vbmeta.device_state
```

Résultat **rapporté puis répété après un autre redémarrage** :

```text
0
orange
unlocked
```

Un `fastboot getvar unlocked` ultérieur a renvoyé une valeur **vide** (`unlocked:`), ce qui reflète une limitation du Fastboot de cet appareil : ne pas interpréter le champ vide comme `locked`. Le démarrage Android a fourni trois éléments concordants après redémarrage.

**État atteint ici :** bootloader déverrouillé, mais pas encore de droits root avant l'installation séparée de Magisk.

---

Voir aussi [root Magisk](ROOT.md) et [dépannage](DEPANNAGE.md).
