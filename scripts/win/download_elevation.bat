@echo off
setlocal
set PROJECT=%~dp0..\..\

where python >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato nel PATH.
    pause & exit /b 1
)

cd /d "%PROJECT%"
python scripts\download_elevation.py %*

pause
