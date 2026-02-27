@echo off
REM Windows Quick Setup - Verify all dependencies
REM Run this first before launching the application

echo.
echo =========================================
echo Productivity Tracker - Quick Setup
echo =========================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Install from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo.
echo =========================================
echo All dependencies installed!
echo=========================================
echo.
echo Next step: Run "launch.bat" to start the application
echo Or: python launcher.py
echo.
pause
