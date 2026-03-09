@echo off
setlocal enabledelayedexpansion
set PASS=0
set FAIL=0
set SKIP=0
set BACKEND=http://localhost:8000
set GH=http://localhost:8989

echo.
echo ===================================
echo    open-gpx  --  Test AS-IS
echo ===================================
echo.

:: ── 1. Health check ───────────────────────────────────────────────────────────
echo --- 1. Servizi online ---
echo.

curl -s -o nul -w "%%{http_code}" "%BACKEND%/api/health" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    echo [PASS] Backend online (porta 8000^)
    set /a PASS+=1
) else (
    echo [FAIL] Backend non raggiungibile -- avvia con start.bat
    echo.
    echo ABORT: impossibile continuare senza backend.
    echo.
    goto summary
)

curl -s -o nul -w "%%{http_code}" "%GH%/health" >%TEMP%\opengpx_status.txt 2>nul
set /p GH_STATUS=<%TEMP%\opengpx_status.txt
if "%GH_STATUS%"=="200" (
    echo [PASS] GraphHopper online (porta 8989^)
    set /a PASS+=1
    set GH_UP=1
) else (
    echo [SKIP] GraphHopper non raggiungibile -- test routing saltati
    set /a SKIP+=1
    set GH_UP=0
)

:: ── 2. Geocoding ──────────────────────────────────────────────────────────────
echo.
echo --- 2. Geocoding  GET /api/geocode ---
echo.

curl -s -o %TEMP%\opengpx_body.txt -w "%%{http_code}" "%BACKEND%/api/geocode?q=Milano" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    echo [PASS] q=Milano -- HTTP 200
    set /a PASS+=1
) else (
    echo [FAIL] q=Milano -- HTTP %STATUS%
    set /a FAIL+=1
)

curl -s -o %TEMP%\opengpx_body.txt -w "%%{http_code}" "%BACKEND%/api/geocode?q=Roma" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    echo [PASS] q=Roma -- HTTP 200
    set /a PASS+=1
) else (
    echo [FAIL] q=Roma -- HTTP %STATUS%
    set /a FAIL+=1
)

:: query troppo corta -> 422
curl -s -o nul -w "%%{http_code}" "%BACKEND%/api/geocode?q=a" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="422" (
    echo [PASS] q=a troppo corta -- 422 Unprocessable Entity
    set /a PASS+=1
) else (
    echo [FAIL] q=a troppo corta -- atteso 422, ottenuto %STATUS%
    set /a FAIL+=1
)

:: ── 3. Routing ────────────────────────────────────────────────────────────────
echo.
echo --- 3. Routing  POST /api/route ---
echo.

if "%GH_UP%"=="0" (
    echo [SKIP] standard      -- GraphHopper offline
    echo [SKIP] avoid_tolls   -- GraphHopper offline
    echo [SKIP] scenic        -- GraphHopper offline
    echo [SKIP] 1 waypoint    -- GraphHopper offline
    echo [SKIP] profilo invalido -- GraphHopper offline
    set /a SKIP+=5
    goto export_tests
)

:: standard
set BODY={"waypoints":[{"lat":45.4654,"lng":9.1866},{"lat":41.9028,"lng":12.4964}],"profile":"standard"}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/route" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    echo [PASS] standard  Milano-^>Roma -- HTTP 200
    set /a PASS+=1
) else (
    echo [FAIL] standard -- HTTP %STATUS%
    set /a FAIL+=1
)

:: avoid_tolls
set BODY={"waypoints":[{"lat":45.4654,"lng":9.1866},{"lat":41.9028,"lng":12.4964}],"profile":"avoid_tolls"}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/route" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    echo [PASS] avoid_tolls Milano-^>Roma -- HTTP 200
    set /a PASS+=1
) else (
    echo [FAIL] avoid_tolls -- HTTP %STATUS%
    set /a FAIL+=1
)

:: scenic
set BODY={"waypoints":[{"lat":45.4654,"lng":9.1866},{"lat":41.9028,"lng":12.4964}],"profile":"scenic"}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/route" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    echo [PASS] scenic    Milano-^>Roma -- HTTP 200
    set /a PASS+=1
) else (
    echo [FAIL] scenic -- HTTP %STATUS%
    set /a FAIL+=1
)

:: 1 waypoint -> 400
set BODY={"waypoints":[{"lat":45.4654,"lng":9.1866}],"profile":"standard"}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/route" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="400" (
    echo [PASS] 1 waypoint -- 400 Bad Request
    set /a PASS+=1
) else (
    echo [FAIL] 1 waypoint -- atteso 400, ottenuto %STATUS%
    set /a FAIL+=1
)

:: profilo invalido -> 400
set BODY={"waypoints":[{"lat":45.4654,"lng":9.1866},{"lat":41.9028,"lng":12.4964}],"profile":"invalid"}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/route" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="400" (
    echo [PASS] profilo invalido -- 400 Bad Request
    set /a PASS+=1
) else (
    echo [FAIL] profilo invalido -- atteso 400, ottenuto %STATUS%
    set /a FAIL+=1
)

:: ── 4. Export GPX ─────────────────────────────────────────────────────────────
:export_tests
echo.
echo --- 4. Export  POST /api/export/gpx ---
echo.

:: GPX Route (non richiede GraphHopper)
set BODY={"type":"route","route_name":"Test","waypoints":[{"lat":45.4654,"lng":9.1866,"name":"Milano"},{"lat":41.9028,"lng":12.4964,"name":"Roma"}],"geometry":[]}
curl -s -o %TEMP%\opengpx_body.txt -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/export/gpx" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    findstr /C:"<gpx" %TEMP%\opengpx_body.txt >nul 2>&1
    if not errorlevel 1 (
        echo [PASS] GPX Route -- XML valido
        set /a PASS+=1
    ) else (
        echo [FAIL] GPX Route -- risposta non e' XML GPX
        set /a FAIL+=1
    )
) else (
    echo [FAIL] GPX Route -- HTTP %STATUS%
    set /a FAIL+=1
)

:: GPX Track (geometry fittizia)
set BODY={"type":"track","route_name":"Test","waypoints":[],"geometry":[[45.4654,9.1866],[44.0,10.5],[41.9028,12.4964]]}
curl -s -o %TEMP%\opengpx_body.txt -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/export/gpx" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="200" (
    findstr /C:"<gpx" %TEMP%\opengpx_body.txt >nul 2>&1
    if not errorlevel 1 (
        echo [PASS] GPX Track -- XML valido
        set /a PASS+=1
    ) else (
        echo [FAIL] GPX Track -- risposta non e' XML GPX
        set /a FAIL+=1
    )
) else (
    echo [FAIL] GPX Track -- HTTP %STATUS%
    set /a FAIL+=1
)

:: type invalido -> 400
set BODY={"type":"kml","waypoints":[],"geometry":[]}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/export/gpx" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="400" (
    echo [PASS] type=kml invalido -- 400 Bad Request
    set /a PASS+=1
) else (
    echo [FAIL] type=kml invalido -- atteso 400, ottenuto %STATUS%
    set /a FAIL+=1
)

:: track senza geometry -> 400
set BODY={"type":"track","waypoints":[],"geometry":[]}
curl -s -o nul -w "%%{http_code}" -X POST -H "Content-Type: application/json" -d "%BODY%" "%BACKEND%/api/export/gpx" >%TEMP%\opengpx_status.txt 2>nul
set /p STATUS=<%TEMP%\opengpx_status.txt
if "%STATUS%"=="400" (
    echo [PASS] track senza geometry -- 400 Bad Request
    set /a PASS+=1
) else (
    echo [FAIL] track senza geometry -- atteso 400, ottenuto %STATUS%
    set /a FAIL+=1
)

:: ── Riepilogo ─────────────────────────────────────────────────────────────────
:summary
echo.
echo ===================================
echo          RIEPILOGO TEST
echo ===================================
set /a TOTAL=PASS+FAIL+SKIP
echo   Totale : %TOTAL%
echo   PASS   : %PASS%
echo   FAIL   : %FAIL%
echo   SKIP   : %SKIP%
echo.

del %TEMP%\opengpx_status.txt >nul 2>&1
del %TEMP%\opengpx_body.txt   >nul 2>&1

if %FAIL% gtr 0 exit /b 1
exit /b 0
