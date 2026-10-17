# Publishing to GitHub

1. Unzip **TB328FU_GITHUB_PUBLIC_FR_EN.zip**. It is the **GitHub-ready PUBLIC** tree (source + documentation, no OEM firmware blobs or personal patched boot images).
2. Review every file for private information and check `ATTRIBUTION_AND_LICENSES.md`.
3. Create a public GitHub repository; upload this tree or use `git init`, `git add .`, `git commit` and your repository's own `git remote`.
4. Do **NOT** commit the separate `TB328FU_COMPLETE_PRIVATE_DO_NOT_PUBLISH.zip` unchanged: it contains firmware-derived images and images from the tested tablet; copyrights and device privacy may apply.
5. If you add binary releases, confirm rights and attribution for every third-party component and provide hashes. A third-party `.exe` supplied by unknown mirrors is not trustworthy by default.
6. Share an adapted, evidence-based update in [upstream issue #293](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader/issues/293). A prepared EN post is in `release/ISSUE_293_EN.md`, with a French version alongside.

**No GitHub upload or publication was performed automatically by this pack.**
