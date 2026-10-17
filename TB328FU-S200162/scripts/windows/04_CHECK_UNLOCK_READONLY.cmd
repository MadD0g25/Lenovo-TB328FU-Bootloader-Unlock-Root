@echo off
setlocal
set "ADB=C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe"
if not exist "%ADB%" (echo ERROR: Missing ADB. & exit /b 2)
"%ADB%" devices
for %%K in (ro.product.model ro.build.display.id ro.boot.slot_suffix ro.boot.flash.locked ro.boot.verifiedbootstate ro.boot.vbmeta.device_state) do (
 echo %%K:
 "%ADB%" shell getprop %%K
)
echo Expected AFTER a successful unlock on tested device: 0 / orange / unlocked.
echo Restart Android and repeat to verify persistence.
