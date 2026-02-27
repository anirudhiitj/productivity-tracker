@echo off
REM Windows batch file to launch the full stack
REM This will start both backend and frontend servers

echo =========================================
echo Productivity Tracker - Full Stack Launch
echo =========================================
echo.

python launcher.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start launcher
    echo Make sure Python 3.10+ is installed
    pause
)
