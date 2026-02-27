"""
Build script to bundle Python backend into standalone executable using PyInstaller.
This creates a single .exe that includes all dependencies.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
CLIENT_DIR = ROOT_DIR / "client"
DATA_DIR = ROOT_DIR / "data"
DIST_DIR = BACKEND_DIR / "dist"
BUILD_DIR = BACKEND_DIR / "build"

print("=" * 80)
print("Building Python Backend with PyInstaller")
print("=" * 80)

# Check if PyInstaller is installed
try:
    import PyInstaller
    print(f"✓ PyInstaller version: {PyInstaller.__version__}")
except ImportError:
    print("✗ PyInstaller not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller installed")

# Clean previous builds
print("\n[1/4] Cleaning previous builds...")
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
    print("  ✓ Removed dist directory")
if BUILD_DIR.exists():
    shutil.rmtree(BUILD_DIR)
    print("  ✓ Removed build directory")

# Create spec file for PyInstaller
print("\n[2/4] Creating PyInstaller spec file...")

spec_content = """
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Paths
root_dir = Path(SPECPATH).parent
backend_dir = root_dir / "backend"
client_dir = root_dir / "client"
data_dir = root_dir / "data"

# All Python files to include
backend_files = [
    (str(backend_dir), 'backend'),
    (str(client_dir), 'client'),
    (str(data_dir), 'data'),
]

# Hidden imports (packages that PyInstaller might miss)
hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'pydantic',
    'pydantic.dataclasses',
    'starlette',
    'starlette.applications',
    'starlette.middleware',
    'starlette.middleware.cors',
    'psutil',
    'sqlite3',
    'ctypes',
    'ctypes.wintypes',
    'win32api',
    'win32con',
    'win32gui',
    'logging',
    'logging.handlers',
]

a = Analysis(
    [str(backend_dir / 'main.py')],
    pathex=[str(root_dir)],
    binaries=[],
    datas=backend_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging; set False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

spec_file = BACKEND_DIR / "backend.spec"
with open(spec_file, "w") as f:
    f.write(spec_content)
print(f"  ✓ Created {spec_file}")

# Run PyInstaller
print("\n[3/4] Running PyInstaller (this may take a few minutes)...")
print("  This will bundle Python + all dependencies into a single .exe")

cmd = [
    "pyinstaller",
    "--clean",
    "--noconfirm",
    str(spec_file)
]

try:
    result = subprocess.run(cmd, cwd=str(BACKEND_DIR), check=True, capture_output=True, text=True)
    print("  ✓ PyInstaller completed successfully")
except subprocess.CalledProcessError as e:
    print(f"  ✗ PyInstaller failed:")
    print(e.stdout)
    print(e.stderr)
    sys.exit(1)

# Verify output
print("\n[4/4] Verifying build...")
backend_exe = DIST_DIR / "backend.exe"
if backend_exe.exists():
    size_mb = backend_exe.stat().st_size / (1024 * 1024)
    print(f"  ✓ backend.exe created: {size_mb:.1f} MB")
    print(f"  ✓ Location: {backend_exe}")
else:
    print(f"  ✗ backend.exe not found at {backend_exe}")
    sys.exit(1)

# Copy data files to dist
print("\n[5/4] Copying data files...")
dist_data_dir = DIST_DIR / "data"
if dist_data_dir.exists():
    shutil.rmtree(dist_data_dir)
shutil.copytree(DATA_DIR, dist_data_dir)
print(f"  ✓ Copied data files to {dist_data_dir}")

print("\n" + "=" * 80)
print("✓ Backend build complete!")
print("=" * 80)
print(f"\nExecutable: {backend_exe}")
print(f"Size: {size_mb:.1f} MB")
print("\nYou can test it with: backend\\dist\\backend.exe")
print("=" * 80)
