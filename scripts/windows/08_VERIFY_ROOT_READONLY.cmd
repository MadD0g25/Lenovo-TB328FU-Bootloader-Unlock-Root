@echo off
setlocal
set "ADB=C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe"
if not exist "%ADB%" (echo Missing ADB & exit /b 2)
"%ADB%" devices
"%ADB%" shell su -c id
