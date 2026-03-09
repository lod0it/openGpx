@echo off
echo.
echo === open-gpx - Arresto servizi ===
echo.

call :kill_port 8989 "GraphHopper"
call :kill_port 8000 "Backend FastAPI"
call :kill_port 5173 "Frontend Vite"

echo.
echo === Tutti i servizi fermati ===
echo.
goto :eof

:kill_port
set PORT=%1
set NAME=%2
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
    echo [STOP] %NAME% (porta %PORT%) - PID %%p
    goto :eof
)
echo [--]   %NAME% non era in esecuzione (porta %PORT%)
goto :eof
