#!/usr/bin/env python3
"""
Quick Start Guide - Setup and Test Productivity Tracker
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def main():
    """Main setup guide."""
    print_header("🚀 PRODUCTIVITY TRACKER - QUICK START GUIDE")

    print("Welcome! This guide will help you set up and run the system.\n")

    print("📊 WHAT IS THIS?")
    print("-" * 60)
    print("A Windows-only real-time process monitoring dashboard:")
    print("  • White UI that shows all active processes")
    print("  • Displays: Process name, category, memory, CPU, runtime")
    print("  • Auto-refreshes every 3 seconds")
    print("  • Categorizes apps: Productive, Gaming, Educational, etc.")
    print()

    print("🏗️  ARCHITECTURE")
    print("-" * 60)
    print("  Backend:  FastAPI server on http://localhost:8000")
    print("  Frontend: React web app on http://localhost:3000")
    print("  All local, no cloud storage, no login required")
    print()

    print("⚙️  SYSTEM REQUIREMENTS")
    print("-" * 60)
    print("  ✓ Windows 10/11")
    print("  ✓ Python 3.10+")
    print("  ✓ Node.js 16+ (for React frontend)")
    print()

    print("🚀 SETUP (First Time Only)")
    print("-" * 60)
    print()

    # Step 1: Install Python packages
    print("Step 1️⃣ : Installing Python packages...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True
        )
        print("  ✅ Python packages installed")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install Python packages: {e}")
        print("  Run: python -m pip install -r requirements.txt")
        return

    # Step 2: Check Node.js
    print()
    print("Step 2️⃣ : Checking Node.js...")
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        print("  ✅ Node.js is installed")
    except FileNotFoundError:
        print("  ⚠️  Node.js not found!")
        print("  Download from: https://nodejs.org/")
        print("  Then restart your terminal and run this script again")
        return

    # Step 3: Test backend
    print()
    print("Step 3️⃣ : Testing backend...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", 
             "from backend.main import app; from backend.process_monitor import ProcessMonitor; "
             "pm = ProcessMonitor(); print(len(pm.get_main_processes()))"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            num_procs = result.stdout.strip().split('\n')[-1]
            print(f"  ✅ Backend working ({num_procs} processes found)")
        else:
            print(f"  ⚠️  Backend test issue: {result.stderr}")
    except Exception as e:
        print(f"  ⚠️  Could not test backend: {e}")

    print()
    print("=" * 60)
    print("✅ SETUP COMPLETE!\n")

    print("🚀 NOW LAUNCH THE APPLICATION")
    print("-" * 60)
    print()
    print("Option 1️⃣ : EASIEST - Use the launcher (recommended):")
    print()
    print("  Windows (Batch File):")
    print("    > launch.bat")
    print()
    print("  Or via Python:")
    print("    > python launcher.py")
    print()
    print("  This will automatically start both backend and frontend!")
    print()

    print("Option 2️⃣ : Manual Start (Two Terminals):")
    print()
    print("  Terminal 1 - Backend:")
    print("    > python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000")
    print()
    print("  Terminal 2 - Frontend:")
    print("    > cd frontend")
    print("    > npm run dev")
    print()

    print("🌐 THEN VISIT")
    print("-" * 60)
    print("  Frontend:  http://localhost:3000  ← Open this in your browser")
    print("  API Docs:  http://localhost:8000/docs")
    print()

    print("📚 NEED HELP?")
    print("-" * 60)
    print("  • Read FULLSTACK_README.md for detailed documentation")
    print("  • Check logs in both terminal windows for errors")
    print("  • Browser console (F12) shows frontend errors")
    print()

    print("🎯 PROCESS FILTERING")
    print("-" * 60)
    print("  The dashboard shows \"main\" processes:")
    print("  • Memory > 100MB  OR  CPU > 1%")
    print("  • Excludes system processes (svchost, dwm, etc.)")
    print()
    print("  Examples of main processes:")
    print("  ✅ Chrome (800MB+)  ✅ Valorant (6GB)  ✅ VSCode (500MB)")
    print("  ❌ explorer.exe (50MB)  ❌ svchost.exe (40MB)")
    print()

    print("=" * 60)
    print("Ready to start? Run: python launcher.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
