# Dépannage et restauration — TB328FU S200162

## Récupération, diagnostic et points d’arrêt

diagnostic et points d'arrêt

| Symptôme | Signification plausible | Conduite recommandée |
|---|---|---|
| `adb` n'est pas reconnu | `adb.exe` hors du PATH | Utiliser le chemin complet `"C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe"` |
| `Connection failed` / `usb_send failed` avant FDL1 | Pas de session BootROM exploitable | Vérifier câble, mode de connexion, COM et ne pas relancer de flash |
| `CHECK_BAUD FAIL` **suivi de** `CHECK_BAUD FDL1` réussi | Première négociation infructueuse puis récupération | Lire les lignes suivantes ; ce n'est pas automatiquement fatal |
| `timeout reached` après envoi SML | Le logiciel n'a pas reçu la réponse attendue | **Ne pas interpréter comme réussite ou échec ; vérifier l'état final et ne pas relancer aveuglément** |
| Écran noir après V9 | Exécution / transition incertaine | Arrêt forcé prudent puis vérifier Recovery / démarrage, sans écrire à l'aveugle |
| Recovery `init_user0_failed` | Données utilisateur inaccessibles | **Ne faire `Factory data reset` que si l'effacement est accepté et les données sauvegardées** |
| Bootloop **après Magisk** | Image de démarrage patchée non acceptée, ou autre incident | Restaurer la copie fraîche `boot_a.bin` via Fastboot **si Fastboot est accessible** |
| `fastboot getvar unlocked` vide | Variable non exposée par le Fastboot fourni | Ne pas en déduire que le bootloader est verrouillé |
| `su: not found`, `Permission denied` | Root absent ou refusé par Magisk | Consulter Magisk, vérifier l'image patchée et le slot avant toute nouvelle écriture |

### 9.1 Retour arrière de la seule étape Magisk

**Uniquement si Fastboot reste accessible et que `ROOT_BACKUP\boot_a.bin` correspond exactement au firmware du slot A :**

```bat
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" flash boot_a "ROOT_BACKUP\boot_a.bin"
"C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe" reboot
```

Cela **retire le correctif Magisk du noyau/ramdisk démarré** ; cela **ne reverrouille pas le bootloader** et n'annule pas forcément toutes les modifications persistantes effectuées par V9. Si Fastboot ne répond plus, ne pas inventer de commande de flash forcé. La restauration par FDL2 a été possible lors d'essais antérieurs, mais ne constitue **pas** une garantie de récupération.

### 9.2 Sauvegardes trompeuses à ne jamais utiliser pour restaurer

Pendant la recherche, deux fichiers `splloader.bin` lus avec `r all` étaient **entièrement remplis de zéros**. Ils ne représentent pas une image SPL valide à réécrire. D'autres sauvegardes `BACKUP` / `BACKUP1` contenaient des compilations U-Boot différentes ; seule la copie correspondant à la build actuelle et contrôlée par SHA-256 peut être envisagée pour une restauration ciblée.

### 9.3 Conseils pour garder root fonctionnel

- Conserver Magisk et l'image stock du **même firmware** ; ne pas réutiliser l'image patchée sur une autre tablette.
- Après une mise à jour Android, repatcher l'image **nouvelle** du slot réellement actif. Ne pas flasher aveuglément une ancienne image Magisk.
- Ne jamais sélectionner une option de **reverrouillage OEM / Fastboot** avec un `boot_a` modifié.
- Éviter les modules Magisk inconnus ; des modules peuvent provoquer bootloop, panne Wi-Fi ou perte de données.
- Les applications bancaires et certains services de sécurité peuvent refuser de fonctionner sur un appareil rooté.

**Important :** ne pas flasher un SPL extrait en lecture mais rempli de zéros. `Factory data reset` efface les données.

## Vérification d’état après un timeout

L’exécution V9 **réellement réussie** s’est terminée par `timeout reached` / `Transport exit: 1`. Le succès a été établi seulement après redémarrage par **`0 / orange / unlocked`**. Un timeout isolé peut au contraire refléter un échec ; **ne relancez pas V9 simplement parce que le transport n’a pas répondu**.
