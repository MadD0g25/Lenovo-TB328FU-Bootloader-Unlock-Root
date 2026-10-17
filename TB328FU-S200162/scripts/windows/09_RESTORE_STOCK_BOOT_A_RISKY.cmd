@echo off
setlocal
cd /d "%~dp0..\.."
set "FASTBOOT=C:\Program Files (x86)\Minimal ADB and Fastboot\fastboot.exe"
if not exist "local\boot\boot_a_stock.bin" (echo STOP: stock boot image missing & exit /b 2)
"%FASTBOOT%" devices
"%FASTBOOT%" getvar current-slot
if errorlevel 1 (echo STOP: can't query slot & exit /b 2)
echo DANGER: RESTORE STOCK BOOT_A only if firmware and slot A EXACTLY match image.
set /p CONFIRM=After checking, type RESTORE STOCK BOOT_A: 
if /I not "%CONFIRM%"=="RESTORE STOCK BOOT_A" (echo Cancelled & exit /b 2)
"%FASTBOOT%" flash boot_a "local\boot\boot_a_stock.bin"
if errorlevel 1 (echo Flash failed: STOP & exit /b 2)
echo Stock boot restored; reboot manually.
