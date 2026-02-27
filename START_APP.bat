@echo off
REM Quick launcher for Productivity Tracker - Desktop App Version
REM This starts everything needed for the Electron desktop app

echo =====================================================================
echo      PRODUCTIVITY TRACKER - Electron Desktop App Launcher
echo =====================================================================
echo.

REM Check if backend.exe exists
if exist backend\dist\backend.exe (
    echo [Step 1/3] Starting bundled backend.exe...
    start "Productivity Backend" /MIN backend\dist\backend.exe
    set BACKEND_TYPE=Bundled executable
) else (
    echo [Step 1/3] Starting Python backend...
    start "Productivity Backend" /MIN cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
    set BACKEND_TYPE=Python uvicorn
)

echo   Backend type: %BACKEND_TYPE%
echo   Backend URL: http://localhost:8000
echo.

REM Wait for backend to start
echo [Step 2/3] Waiting for backend to initialize...
timeout /t 4 /nobreak > nul
echo   Backend should be ready!
echo.

REM Start Electron
echo [Step 3/3] Launching Electron desktop app...
echo.
call npm run dev:electron

echo.
echo =====================================================================
echo Desktop app closed. Cleaning up...
echo =====================================================================

REM Cleanup
taskkill /F /IM backend.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Productivity Backend*" 2>nul

echo Backend stopped.
echo.
echo Thank you for using Productivity Tracker!
timeout /t 2 /nobreak > nul
