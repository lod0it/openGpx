@echo off
setlocal
set "PROJECT_DIR=%~dp0..\.."
cd /d "%PROJECT_DIR%"

where python >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato nel PATH.
    echo Installa Python 3.12+ da https://python.org
    pause
    exit /b 1
)

python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installo rich...
    pip install rich --quiet
)

python scripts\start.py %*
