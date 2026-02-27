"""
Production launcher for the bundled Python backend.
This script is called by Electron to start the FastAPI server.
"""

import sys
import os
from pathlib import Path

# Ensure correct working directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = Path(sys._MEIPASS)
    os.chdir(bundle_dir)
else:
    # Running as script
    bundle_dir = Path(__file__).parent

print(f"[Backend] Starting from: {bundle_dir}")
print(f"[Backend] Working directory: {os.getcwd()}")

# Import and run the FastAPI app
import uvicorn
from backend.main import app

if __name__ == "__main__":
    print("[Backend] Launching FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )
