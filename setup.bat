@echo off
setlocal
REM Windows Quick Setup - Verify all dependencies
REM Run this first before launching the application

echo.
echo =========================================
echo Productivity Tracker - Quick Setup
echo =========================================
echo.

echo Checking Python...
set "PY_CMD="

py -3 --version >nul 2>&1
if not errorlevel 1 set "PY_CMD=py -3"

if not defined PY_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    if defined CONDA_PREFIX (
        if exist "%CONDA_PREFIX%\python.exe" set "PY_CMD=%CONDA_PREFIX%\python.exe"
    )
)

if not defined PY_CMD (
    echo Python not found in current shell. Trying automatic install via winget...
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: winget not available and Python not found.
        echo Install Python 3.10+ from https://www.python.org/downloads/ and check "Add Python to PATH".
        pause
        exit /b 1
    )

    winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements >nul 2>&1

    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3"

    if not defined PY_CMD (
        python --version >nul 2>&1
        if not errorlevel 1 set "PY_CMD=python"
    )
)

if not defined PY_CMD (
    echo ERROR: Python is still unavailable after auto-install attempt.
    echo Please install Python 3.10+ manually from https://www.python.org/downloads/
    echo and relaunch this setup script.
    pause
    exit /b 1
)

%PY_CMD% --version

echo.
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Install from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Checking pip...
%PY_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found. Bootstrapping pip...
    %PY_CMD% -m ensurepip --upgrade
    if errorlevel 1 (
        echo ERROR: Failed to initialize pip
        pause
        exit /b 1
    )
)

echo.
echo Installing Python dependencies...
%PY_CMD% -m pip install --upgrade pip >nul 2>&1
%PY_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo.
echo =========================================
echo All dependencies installed!
echo =========================================
echo.
echo Next step: Run "launch.bat" to start the application
echo Or: %PY_CMD% launcher.py
echo.
pause
