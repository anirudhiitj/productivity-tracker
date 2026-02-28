#!/usr/bin/env python3
"""
FocusRank — One-Click Installer Builder
========================================
Produces a single .exe NSIS installer that bundles:
  1. PyInstaller-packaged Python backend (FastAPI + all deps)
  2. Vite-built React frontend
  3. Electron shell
  4. All data files

Usage:
    python BUILD_INSTALLER.py

Output:
    frontend/dist_electron/FocusRank-Setup-1.0.0.exe
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
BACKEND_DIST = ROOT / "dist" / "tracker-backend"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def banner(msg: str):
    print("\n" + "=" * 60)
    print(f"  {msg}")
    print("=" * 60 + "\n")


def run(cmd, cwd=None, shell=False):
    """Run a command, print it, and check for errors."""
    cwd = cwd or ROOT
    print(f"  $ {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    result = subprocess.run(
        cmd, cwd=str(cwd), shell=shell,
        capture_output=False, text=True
    )
    if result.returncode != 0:
        print(f"\n  ERROR: Command exited with code {result.returncode}")
        sys.exit(1)
    return result


def check_tool(name: str, cmd: list):
    """Verify a required tool is available."""
    try:
        subprocess.run(cmd, capture_output=True, check=True, shell=True)
        print(f"  [OK] {name}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"  [MISSING] {name} — please install it first")
        sys.exit(1)


# ─────────────────────────────────────────────
# Step 0: Pre-flight checks
# ─────────────────────────────────────────────

def preflight():
    banner("Step 0: Pre-flight checks")
    check_tool("Python", [sys.executable, "--version"])
    check_tool("Node.js", ["node", "--version"])
    check_tool("npm", ["npm", "--version"])

    # Check Python dependencies
    missing = []
    for pkg in ["fastapi", "uvicorn", "psutil", "pydantic"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"\n  Missing Python packages: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt")
        sys.exit(1)
    print("  [OK] Python dependencies")

    # Ensure PyInstaller
    try:
        __import__("PyInstaller")
        print("  [OK] PyInstaller")
    except ImportError:
        print("  Installing PyInstaller...")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])


# ─────────────────────────────────────────────
# Step 1: Build Python backend with PyInstaller
# ─────────────────────────────────────────────

def build_backend():
    banner("Step 1: Building Python backend (PyInstaller)")
    run([sys.executable, "build_backend.py"], cwd=ROOT)

    if not (BACKEND_DIST / "tracker-backend.exe").exists():
        print("  ERROR: tracker-backend.exe was not produced!")
        sys.exit(1)

    size_mb = (BACKEND_DIST / "tracker-backend.exe").stat().st_size / (1024 * 1024)
    print(f"  Backend exe: {size_mb:.1f} MB")
    print(f"  Total dir: {sum(f.stat().st_size for f in BACKEND_DIST.rglob('*') if f.is_file()) / (1024*1024):.1f} MB")


# ─────────────────────────────────────────────
# Step 2: Build React frontend with Vite
# ─────────────────────────────────────────────

def build_frontend():
    banner("Step 2: Building React frontend (Vite)")
    
    # Install npm deps if needed
    if not (FRONTEND / "node_modules").exists():
        print("  Installing npm dependencies...")
        run("npm install", cwd=FRONTEND, shell=True)
    
    # Build
    run("npm run build", cwd=FRONTEND, shell=True)

    index = FRONTEND / "dist" / "index.html"
    if not index.exists():
        print("  ERROR: frontend/dist/index.html not found!")
        sys.exit(1)
    print(f"  Frontend built: {index}")


# ─────────────────────────────────────────────
# Step 3: Install Electron deps & build installer
# ─────────────────────────────────────────────

def build_electron():
    banner("Step 3: Building Electron installer (electron-builder)")

    # Install deps if needed
    if not (FRONTEND / "node_modules" / "electron").exists():
        print("  Installing Electron dependencies...")
        run("npm install", cwd=FRONTEND, shell=True)

    # Verify backend dist exists for extraResources
    if not BACKEND_DIST.exists():
        print("  ERROR: Backend dist not found at", BACKEND_DIST)
        sys.exit(1)

    # Remove old output
    out_dir = FRONTEND / "dist_electron"
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)

    # Build the NSIS installer
    run("npx electron-builder -w --publish never", cwd=FRONTEND, shell=True)

    # Find the output
    installers = list(out_dir.glob("FocusRank-Setup-*.exe"))
    if not installers:
        # Also check for any .exe
        installers = list(out_dir.glob("*.exe"))
    
    if installers:
        for inst in installers:
            size = inst.stat().st_size / (1024 * 1024)
            print(f"  Installer: {inst.name} ({size:.1f} MB)")
        return installers[0]
    else:
        print("  WARNING: No installer .exe found in dist_electron/")
        print("  Contents:", [f.name for f in out_dir.iterdir()] if out_dir.exists() else "empty")
        return None


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    start = time.time()
    
    banner("FocusRank Installer Builder")
    print(f"  Project root: {ROOT}")
    print(f"  Python: {sys.version}")
    
    preflight()
    build_backend()
    build_frontend()
    installer = build_electron()

    elapsed = time.time() - start
    
    banner("BUILD COMPLETE")
    print(f"  Time: {elapsed:.0f}s")
    if installer:
        print(f"  Installer: {installer}")
        print(f"  Size: {installer.stat().st_size / (1024*1024):.1f} MB")
        print(f"\n  Share this single .exe file with anyone.")
        print(f"  They install it and run FocusRank — no Python/Node needed!\n")
    else:
        print("  Check frontend/dist_electron/ for output files.\n")


if __name__ == "__main__":
    main()
