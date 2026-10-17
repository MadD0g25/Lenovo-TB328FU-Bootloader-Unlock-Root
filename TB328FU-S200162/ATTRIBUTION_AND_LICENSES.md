# Attribution, licensing and redistribution / Attribution et licences

This repository documents a **device-specific adaptation** of existing CVE-2022-38694 research and one physical-device success. **CVE-2022-38694 was not independently discovered by this project.** The original exploit, reverse-engineering framework and FDL1/cboot methodology are attributed to [TomKing062](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader) and contributors. Related [spreadtrum_flash](https://github.com/TomKing062/spreadtrum_flash) must keep its own license. Magisk is by [topjohnwu](https://github.com/topjohnwu/Magisk).

**English:** The MIT notice included in `tools/v9/LICENSE_TOOLS.txt` covers only the **new Python/script source written in the V9 experimental kit**, not firmware, partition dumps, OEM signing keys, third-party tools, executable releases, or all contents of this repository. The documentation and helper scripts authored for this pack may be reused with attribution, but their inclusion does not convey any third-party redistribution right. Do not publish Lenovo/Unisoc-derived binaries or someone's Magisk-patched boot image without confirming permission. Public logs must exclude serial numbers, Windows usernames, partition userdata, RPMB material and credentials.

**Français :** La licence MIT du kit V9 couvre seulement le code source original de ce kit, pas les firmwares Lenovo/Unisoc, les dumps de partitions, les outils tiers ou les images de boot modifiées. L’archive **PRIVÉE** doit rester personnelle tant que les droits de redistribution des composants n’ont pas été vérifiés. Retirer des journaux publics identifiants USB/ADB, chemins Windows personnels, données de partitions et secrets éventuels.

Sources:
- https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader
- https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/AddSupportToModel
- https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/wiki/patch_do_cboot%E2%80%90FDL1
- https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/issues/293
- https://github.com/topjohnwu/Magisk
