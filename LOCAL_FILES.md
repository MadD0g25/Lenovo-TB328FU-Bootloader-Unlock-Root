# Preparing local files (EN / FR)

**EN — Public source package vs private complete package.** GitHub-ready files intentionally do **not** include Lenovo/Unisoc firmware, exact prebuilt RAM payloads or third-party Windows executables. This is a redistribution/privacy choice, not a claim they are unnecessary. The separate **PRIVATE COMPLETE** ZIP includes the tested V9 snapshot and the two boot images from the tested device; it must not be uploaded unchanged to a public repository. Obtain the original third-party tools from their authors, and build the RAM images locally from your own exact S200162 stock images if you cannot lawfully distribute prebuilt binaries.

**FR — Dépôt public vs archive complète privée.** Le dépôt publiable n'inclut pas les images Lenovo/Unisoc, le chargeur RAM précompilé ni les exécutables Windows tiers. L’archive **PRIVÉE COMPLÈTE** contient la V9 testée et les deux images `boot_a` de l'exemplaire testé ; **ne pas la publier telle quelle**. Utiliser les outils de leurs auteurs et générer localement les images depuis son propre firmware exact S200162.

## Recommended layout / structure

```text
repo/
  tools/v9/sources/tb328fu_v9.py
  local/                              ignored by .gitignore
    spd_dump/
      spd_dump.exe
      Channel9.dll
      Channel.ini
      custom_exec_no_verify_3ee8.bin
    assets/
      fdl1-dl.bin
      fdl2-dl.bin
    backups/
      uboot_a.bin
      sml_a.bin
      teecfg_a.bin
      trustos_a.bin
      boot_a.bin                      your own original stock image
    V9/prepared_current/
      manifest.json
      fdl1-boot-v9.bin
      cboot-v9-S200162.bin
      teecfg-ram.bin
      trustos-ram.bin
      sml-ram.bin
    boot/
      boot_a_stock.bin
      magisk_patched.img              device-specific; DO NOT redistribute
```

## Build exact V9 RAM images / Générer les images V9

From repo root, after placing the **correct** exact-build stock source files:

```bat
py -3 "tools\v9\sources\tb328fu_v9.py" build --backup "local\backups" --assets "local\assets" --output "local\V9\prepared_current"
```

The code verifies known SHA-256 hashes before patching; it refuses unknown images. The target directory **must be new/empty**. Do not override failures; secure images may differ between devices even on similar product names.

## Verify local payloads / Vérifier localement

```bat
py -3 tools\verify\verify_package.py --bundle "local\V9\prepared_current"
```

Files listed and SHA-256 hashes: [evidence/SHA256SUMS.txt](SHA256SUMS.txt).

## Mandatory external tools / Outils externes nécessaires

- `spd_dump` via original upstream `spreadtrum_flash`: https://github.com/TomKing062/spreadtrum_flash
- Physical BootROM exploitation framework: https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader
- `adb` / Fastboot: https://developer.android.com/tools/releases/platform-tools
- Magisk: https://github.com/topjohnwu/Magisk/releases

The original tested `spd_dump.exe` (including its dependency hashes) was checked by the V9 runner. Different binaries **may be rejected**, and this project does not silently disable those safeguards.
