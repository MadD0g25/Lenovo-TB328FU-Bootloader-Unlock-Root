@echo off
setlocal
cd /d "%~dp0..\.."
set "ADB=C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe"
set "STOCK=local\boot\boot_a_stock.bin"
if not exist "%ADB%" (echo ERROR: adb missing & exit /b 2)
if not exist "%STOCK%" (echo ERROR: put YOUR OWN verified fresh stock boot_a image at %STOCK% & exit /b 2)
echo This sends a file to Downloads; it does NOT flash any partition.
"%ADB%" push "%STOCK%" /sdcard/Download/boot_a.img
