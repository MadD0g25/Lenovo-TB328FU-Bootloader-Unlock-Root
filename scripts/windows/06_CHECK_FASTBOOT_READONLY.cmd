@echo off
setlocal
set "ADB=C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe"
set "FASTBOOT=C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe"
if not exist "%ADB%" (echo Missing ADB & exit /b 2)
if not exist "%FASTBOOT%" (echo Missing Fastboot & exit /b 2)
"%ADB%" reboot bootloader
"%FASTBOOT%" devices
"%FASTBOOT%" getvar current-slot
"%FASTBOOT%" getvar unlocked
 echo IMPORTANT: empty getvar unlocked is inconclusive on this Lenovo.
