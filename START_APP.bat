@echo off
REM Quick launcher for FocusRank - Productivity Tracker

REM Resolve paths relative to this script's directory
set "SCRIPT_DIR=%~dp0"

echo =====================================================================
echo      FocusRank - Productivity Tracker Desktop App
echo =====================================================================
echo.

REM Start backend
echo [1/2] Starting backend server...
start "FocusRank Backend" /MIN "%SCRIPT_DIR%dist\tracker-backend\tracker-backend.exe"
echo   Backend: http://localhost:8000
echo.

REM Wait for backend to start
echo [2/2] Waiting for backend to initialize...
timeout /t 3 /nobreak > nul
echo   Backend ready!
echo.

REM Start Electron app
echo Launching FocusRank application...
echo.
start "" "%SCRIPT_DIR%frontend\dist_electron\FocusRank 1.0.0.exe"

echo.
echo ✅ All systems started!
echo.
timeout /t 2 /nobreak > nul
