@echo off
setlocal
set "PROJECT_DIR=%~dp0..\.."
cd /d "%PROJECT_DIR%"

:: Avvio senza console: pythonw, poi pyw, infine python in console
where pythonw >nul 2>&1
if not errorlevel 1 (
    start "" pythonw scripts\start.py %*
    exit /b 0
)

where pyw >nul 2>&1
if not errorlevel 1 (
    start "" pyw scripts\start.py %*
    exit /b 0
)

where python >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato nel PATH.
    echo Installa Python 3.12+ da https://python.org
    pause
    exit /b 1
)

python scripts\start.py %*
