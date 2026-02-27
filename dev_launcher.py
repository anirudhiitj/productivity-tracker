#!/usr/bin/env python3
"""
Quick launcher for development - starts backend and opens the app
"""

import subprocess
import sys
import time
import os
from pathlib import Path

ROOT = Path(__file__).parent

def main():
    print("=" * 80)
    print("🚀 Productivity Tracker - Development Launcher")
    print("=" * 80)
    
    # Check if we're in development or using built executable
    backend_exe = ROOT / "backend" / "dist" / "backend.exe"
    
    if backend_exe.exists():
        print("\n✓ Found bundled backend.exe")
        print("  Starting production backend...")
        backend_proc = subprocess.Popen(
            [str(backend_exe)],
            cwd=str(ROOT),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        print("\n✓ Using development backend (Python)")
        print("  Starting uvicorn...")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", 
             "--host", "127.0.0.1", "--port", "8000", "--reload"],
            cwd=str(ROOT),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    
    print(f"✓ Backend PID: {backend_proc.pid}")
    print("\n⏳ Waiting for backend to start...")
    time.sleep(3)
    
    print("\n✓ Backend should be ready at http://localhost:8000")
    print("\n📖 Instructions:")
    print("  1. Frontend dev server: cd frontend && npm run dev")
    print("  2. Or open http://localhost:3000 if already running")
    print("  3. Or launch Electron: npm run dev:electron")
    print("\nPress Ctrl+C to stop the backend")
    
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        backend_proc.terminate()
        backend_proc.wait()
        print("✓ Backend stopped")

if __name__ == "__main__":
    main()
