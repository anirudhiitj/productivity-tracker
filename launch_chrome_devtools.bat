@echo off
REM Launch Chrome with DevTools Protocol enabled
REM This allows the productivity tracker to see ALL Chrome tabs (including background tabs)

echo.
echo ========================================
echo  Starting Chrome with DevTools Protocol
echo ========================================
echo.
echo This will:
echo   - Close all existing Chrome instances
echo   - Restart Chrome with debugging enabled
echo   - Allow tracking of ALL tabs (even background ones)
echo.

REM Kill existing Chrome instances
echo Closing existing Chrome instances...
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak >nul

REM Launch Chrome with remote debugging port
echo Starting Chrome with DevTools...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

if errorlevel 1 (
    REM Try alternative Chrome path
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
)

echo.
echo Chrome started with DevTools Protocol on port 9222
echo You can now track ALL Chrome tabs (including background tabs)
echo.
pause
