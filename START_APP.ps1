#!/usr/bin/env powershell
<#
.SYNOPSIS
    FocusRank Productivity Tracker - Desktop App Launcher
    
.DESCRIPTION
    Starts the backend server and launches the FocusRank Electron application
#>

Write-Host "`n" -ForegroundColor Cyan
Write-Host "=====================================================`n" -ForegroundColor Cyan
Write-Host "     FocusRank - Productivity Tracker`n" -ForegroundColor Green
Write-Host "=====================================================`n" -ForegroundColor Cyan

# Define paths
$backendPath = "c:\Users\Admin\Desktop\productivity_tracker\dist\tracker-backend\tracker-backend.exe"
$appPath = "c:\Users\Admin\Desktop\productivity_tracker\frontend\dist_electron\FocusRank 1.0.0.exe"

# [1] Start Backend
Write-Host "[1/2] Starting backend server..." -ForegroundColor Yellow
if (Test-Path $backendPath) {
    Start-Process -FilePath $backendPath -WindowStyle Minimized
    Write-Host "    ✅ Backend started: http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "    ❌ Backend executable not found!" -ForegroundColor Red
    Write-Host "    Path: $backendPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# [2] Wait for backend
Write-Host "[2/2] Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "    ✅ Backend ready!" -ForegroundColor Green

Write-Host ""

# [3] Launch App
Write-Host "Launching FocusRank application..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path $appPath) {
    Start-Process -FilePath $appPath
    Write-Host "✅ All systems started!" -ForegroundColor Green
} else {
    Write-Host "❌ App executable not found!" -ForegroundColor Red
    Write-Host "Path: $appPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
