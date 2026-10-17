# Corriger un dépôt GitHub déjà publié

L'erreur `The main branch ... does not contain the path docs/en/UNLOCK.md` provient généralement d'un dossier parent `TB328FU-S200162/` importé dans la racine ou des anciens liens `docs/...`.

Cette archive corrigée contient **directement à sa racine** `README.md`, `README.fr.md`, `UNLOCK_EN.md`, `ROOT_EN.md`, `DEVERROUILLAGE_FR.md`, etc. Il n'y a **pas de dossier enveloppant**.

## Méthode Codespaces (sans installer Git)

1. Ouvrir le dépôt GitHub, **Code → Codespaces**. Entrer dans le Codespace.
2. Uploader l'archive `TB328FU_GITHUB_RACINE_CORRIGEE.zip` dans le dossier racine du dépôt (via l'explorateur de fichiers Codespaces, glisser-déposer).
3. Dans le Terminal Codespaces, exécuter :

```bash
unzip -o TB328FU_GITHUB_RACINE_CORRIGEE.zip
```

4. Vérifier que `ls -l README.md UNLOCK_EN.md DEVERROUILLAGE_FR.md` montre les trois fichiers. **Seulement si l'ancien dossier enveloppant existe et contient bien un duplicata du projet**, enlever celui-ci :

```bash
ls -la TB328FU-S200162
# Si et seulement si ce dossier est l'ancien duplicata :
rm -rf TB328FU-S200162
```

5. Supprimer seulement le ZIP importé dans Codespaces, puis enregistrer :

```bash
rm TB328FU_GITHUB_RACINE_CORRIGEE.zip
git add -A
git commit -m "Fix repository root and bilingual documentation links"
git push
```

Les URL correctes seront : `.../blob/main/UNLOCK_EN.md` et `.../blob/main/DEVERROUILLAGE_FR.md`.

## Alternative sans Codespaces

Extraire l'archive corrigée sur Windows, ouvrir le dépôt GitHub puis **Add file → Upload files**. Téléverser son **contenu**, pas le ZIP et pas un dossier parent. Attention à supprimer ensuite le vieux répertoire doublon.

**Ne pas téléverser l'archive privée contenant des images personnelles et des binaires OEM dont les droits de redistribution n'ont pas été vérifiés.**
