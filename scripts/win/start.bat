@echo off
setlocal
set PROJECT=%~dp0..\..\
set GH_DIR=%PROJECT%graphhopper

echo.
echo === open-gpx - Avvio servizi ===
echo.

:: ── Prerequisiti ──────────────────────────────────────────────────────────────

where java >nul 2>&1
if errorlevel 1 (
    echo [WARN] Java non trovato - GraphHopper non avviato
    goto skip_gh
)

if not exist "%GH_DIR%\graphhopper-web-10.0.jar" (
    echo [WARN] graphhopper-web-10.0.jar non trovato in graphhopper\
    goto skip_gh
)

if not exist "%GH_DIR%\italy-latest.osm.pbf" (
    echo [WARN] italy-latest.osm.pbf non trovato in graphhopper\
    goto skip_gh
)

echo [OK] Avvio GraphHopper (porta 8989)...
start "GraphHopper" cmd /k "cd /d %GH_DIR% && java -jar graphhopper-web-10.0.jar server config.yml"
goto after_gh

:skip_gh
echo [--] GraphHopper saltato

:after_gh

:: ── Backend ───────────────────────────────────────────────────────────────────

if not exist "%PROJECT%backend\.venv\Scripts\activate.bat" (
    echo [SETUP] Virtualenv non trovato - creo ambiente Python...
    cd /d "%PROJECT%backend"
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    deactivate
    echo [OK] Virtualenv creato
)

echo [OK] Avvio Backend FastAPI (porta 8000)...
start "Backend FastAPI" cmd /k "cd /d %PROJECT%backend && .venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

:: ── Frontend ──────────────────────────────────────────────────────────────────

if not exist "%PROJECT%frontend\node_modules" (
    echo [SETUP] node_modules non trovato - eseguo npm install...
    cd /d "%PROJECT%frontend"
    npm install --silent
    echo [OK] Dipendenze installate
)

echo [OK] Avvio Frontend Vite (porta 5173)...
start "Frontend Vite" cmd /k "cd /d %PROJECT%frontend && npm run dev"

:: ── Apri browser ──────────────────────────────────────────────────────────────

echo.
echo Attendo 4 secondi...
timeout /t 4 /nobreak >nul
start http://localhost:5173

echo.
echo === Servizi avviati ===
echo   Frontend  : http://localhost:5173
echo   Backend   : http://localhost:8000/docs
echo   GraphHopper: http://localhost:8989/health
echo.
echo Per testare: test.bat
echo Per fermare: stop.bat
echo.
