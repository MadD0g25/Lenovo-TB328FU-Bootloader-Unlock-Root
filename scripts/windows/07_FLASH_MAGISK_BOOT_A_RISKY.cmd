@echo off
setlocal
cd /d "%~dp0..\.."
set "FASTBOOT=C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe"
if not exist "%FASTBOOT%" (echo Missing Fastboot & exit /b 2)
if not exist "local\boot\boot_a_stock.bin" (echo STOP: stock boot backup missing & exit /b 2)
if not exist "local\boot\magisk_patched.img" (echo STOP: Magisk output missing & exit /b 2)
py -3 "tools\verify\compare_boot.py" --stock "local\boot\boot_a_stock.bin" --patched "local\boot\magisk_patched.img"
if errorlevel 1 (echo STOP: boot structure does not match stock image. & exit /b 2)
echo DANGER: THIS WILL FLASH THE ACTIVE BOOT_A PARTITION.
echo Ensure Fastboot detects the tablet, bootloader is unlocked, current-slot is a.
"%FASTBOOT%" devices
"%FASTBOOT%" getvar current-slot
if errorlevel 1 (echo STOP: cannot query slot & exit /b 2)
set /p CONFIRM=After checking slot A, type FLASH BOOT_A (anything else aborts): 
if /I not "%CONFIRM%"=="FLASH BOOT_A" (echo Cancelled & exit /b 2)
"%FASTBOOT%" flash boot_a "local\boot\magisk_patched.img"
if errorlevel 1 (echo FLASH FAILED: STOP, do not auto reboot & exit /b 2)
echo Flash succeeded. You may now run fastboot reboot manually.
