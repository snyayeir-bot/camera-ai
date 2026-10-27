@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
if exist "..\python311\python.exe" (
  "..\python311\python.exe" -m venv .venv
) else (
  py -3.11 -m venv .venv
)
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m utils.generate_assets
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m utils.download_models
if errorlevel 1 goto failed
echo Setup complete. Run start.bat.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.11 and check the network connection. See README.md.
pause
exit /b 1
