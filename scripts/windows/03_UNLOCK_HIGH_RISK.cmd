@echo off
setlocal
cd /d "%~dp0..\.."
echo WARNING: high-risk unsigned boot code. EXPECT LOSS OF USER DATA. Possible permanent brick.
echo Only Lenovo TB328FU exact S200162, SLOT A, initial locked state, prior backups.
py -3 "tools\verify\verify_package.py" --bundle "local\V9\prepared_current"
if errorlevel 1 (echo STOP: hashes failed. & exit /b 2)
set "SPD=%CD%\local\spd_dump\spd_dump.exe"
set "ADB=C:\Program Files (x86)\Minimal ADB and Fastboot\adb.exe"
if not exist "%SPD%" (echo Missing %SPD% & exit /b 2)
if not exist "%ADB%" (echo Missing ADB at %ADB% & exit /b 2)
echo Source runner will independently check model, build, slot, hashes and request a risk acknowledgment.
py -3 "tools\v9\sources\tb328fu_v9.py" run --bundle "%CD%\local\V9\prepared_current" --spd "%SPD%" --adb "%ADB%" --execute
set "RC=%ERRORLEVEL%"
echo Runner return code: %RC% . A TIMEOUT IS NOT A SUCCESS FLAG.
echo Do NOT rerun without first checking Android / Recovery and actual bootloader state.
exit /b %RC%
