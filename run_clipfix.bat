@echo off
cd /d "%~dp0"

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "%~dp0clipfix.py"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0clipfix.py"
    exit /b 0
)

echo Could not find pyw.exe or pythonw.exe on PATH.
echo Install Python for Windows and ensure the launcher is available.
pause
