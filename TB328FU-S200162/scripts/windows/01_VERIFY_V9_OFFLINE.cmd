@echo off
setlocal
cd /d "%~dp0..\.."
if not exist "local\V9\prepared_current\manifest.json" (
  echo ERROR: missing local\V9\prepared_current. Read LOCAL_FILES.md.
  exit /b 2
)
py -3 "tools\verify\verify_package.py" --bundle "local\V9\prepared_current"
if errorlevel 1 (echo STOP: not the verified V9 bundle. & exit /b 2)
echo Verification only. Tablet untouched.
