@echo off
setlocal
cd /d "%~dp0..\.."
py -3 "tools\v9\sources\tb328fu_v9.py" plan --bundle "%CD%\local\V9\prepared_current" --spd "%CD%\local\spd_dump\spd_dump.exe"
if errorlevel 1 (echo STOP: plan failed. & exit /b 2)
echo OFFLINE ONLY: no hardware command was run.
