@echo off
echo.
echo === open-gpx - Arresto servizi ===
echo.

:: Chiudi le finestre per titolo (tasklist trova cmd.exe per titolo e lo termina con tutti i figli)
call :close_window "GraphHopper"
call :close_window "Backend FastAPI"
call :close_window "Frontend Vite"

:: Fallback: termina eventuali processi rimasti sulle porte
call :kill_all_on_port 8989 "GraphHopper"
call :kill_all_on_port 8000 "Backend FastAPI"
call :kill_all_on_port 5173 "Frontend Vite"

echo.
echo === Tutti i servizi fermati ===
echo.
goto :eof

:: Trova cmd.exe con il titolo specificato e lo termina con tutti i figli
:close_window
set TITLE=%~1
set FOUND=0
for /f "tokens=2 delims=," %%p in ('tasklist /FI "WINDOWTITLE eq %TITLE%" /FO csv /NH 2^>nul ^| findstr /I "cmd.exe"') do (
    taskkill /PID %%~p /F /T >nul 2>&1
    echo [STOP] Finestra "%TITLE%" chiusa (PID %%~p)
    set FOUND=1
)
if %FOUND%==0 echo [--]   Finestra "%TITLE%" non trovata
goto :eof

:: Termina tutti i PID in ascolto su una porta (watcher + worker)
:kill_all_on_port
set PORT=%1
set NAME=%2
set FOUND=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F /T >nul 2>&1
    echo [STOP] %NAME% porta %PORT% - PID %%p terminato
    set FOUND=1
)
if %FOUND%==0 echo [--]   %NAME% non in esecuzione (porta %PORT%)
goto :eof
