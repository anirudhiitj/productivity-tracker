"""
Pre-build verification script - checks if everything is ready for Electron build
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
ERRORS = []
WARNINGS = []

def check(name, condition, error_msg=None, warning_msg=None):
    """Check a condition and track errors/warnings"""
    if condition:
        print(f"✓ {name}")
        return True
    else:
        if error_msg:
            ERRORS.append(error_msg)
            print(f"✗ {name}: {error_msg}")
        elif warning_msg:
            WARNINGS.append(warning_msg)
            print(f"⚠ {name}: {warning_msg}")
        return False

print("=" * 80)
print("🔍 Pre-Build Verification")
print("=" * 80)

# 1. Check Node.js environment
print("\n[1/6] Node.js Environment")
print("-" * 40)
try:
    node_version = subprocess.check_output(["node", "--version"], text=True).strip()
    check("Node.js installed", True)
    print(f"  Version: {node_version}")
except:
    check("Node.js installed", False, "Node.js not found - install from nodejs.org")

try:
    npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
    check("npm installed", True)
    print(f"  Version: {npm_version}")
except:
    check("npm installed", False, "npm not found")

# 2. Check Python environment
print("\n[2/6] Python Environment")
print("-" * 40)
check("Python 3.x", sys.version_info >= (3, 8), 
      f"Python 3.8+ required, got {sys.version_info.major}.{sys.version_info.minor}")
print(f"  Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Check PyInstaller
try:
    import PyInstaller
    check("PyInstaller installed", True)
    print(f"  Version: {PyInstaller.__version__}")
except ImportError:
    check("PyInstaller installed", False, "Run: pip install pyinstaller")

# Check key dependencies
deps = ['fastapi', 'uvicorn', 'psutil', 'pydantic']
missing = []
for dep in deps:
    try:
        __import__(dep)
        check(f"{dep} installed", True)
    except ImportError:
        missing.append(dep)
        check(f"{dep} installed", False)

if missing:
    ERRORS.append(f"Missing Python packages: {', '.join(missing)}")
    print(f"\n  Install with: pip install {' '.join(missing)}")

# 3. Check project structure
print("\n[3/6] Project Structure")
print("-" * 40)
check("backend/ exists", (ROOT / "backend").exists(), "Missing backend directory")
check("frontend/ exists", (ROOT / "frontend").exists(), "Missing frontend directory")
check("electron/ exists", (ROOT / "electron").exists(), "Missing electron directory")
check("electron/main.js exists", (ROOT / "electron" / "main.js").exists(), 
      "Missing electron/main.js")
check("package.json exists", (ROOT / "package.json").exists(), "Missing package.json")

# 4. Check Node modules
print("\n[4/6] Node Dependencies")
print("-" * 40)
node_modules = ROOT / "node_modules"
if node_modules.exists():
    check("node_modules/ exists", True)
    
    # Check key Electron packages
    electron_path = node_modules / "electron"
    check("electron installed", electron_path.exists(), 
          "Run: npm install")
    
    builder_path = node_modules / "electron-builder"
    check("electron-builder installed", builder_path.exists(), 
          "Run: npm install")
else:
    check("node_modules/ exists", False, "Run: npm install")

frontend_node_modules = ROOT / "frontend" / "node_modules"
check("frontend/node_modules/ exists", frontend_node_modules.exists(),
      "Run: cd frontend && npm install")

# 5. Check builds
print("\n[5/6] Build Artifacts")
print("-" * 40)
frontend_dist = ROOT / "frontend" / "dist"
check("frontend/dist/ exists", frontend_dist.exists(),
      warning_msg="Run: cd frontend && npm run build")

if frontend_dist.exists():
    index_html = frontend_dist / "index.html"
    check("frontend/dist/index.html exists", index_html.exists())

backend_exe = ROOT / "backend" / "dist" / "backend.exe"
check("backend/dist/backend.exe exists", backend_exe.exists(),
      warning_msg="Run: python build_backend.py")

if backend_exe.exists():
    size_mb = backend_exe.stat().st_size / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")

# 6. Check optional files
print("\n[6/6] Optional Files")
print("-" * 40)
check("LICENSE.txt exists", (ROOT / "LICENSE.txt").exists(),
      warning_msg="Create LICENSE.txt for distribution")

icon_file = ROOT / "build" / "icon.ico"
check("build/icon.ico exists", icon_file.exists(),
      warning_msg="Add icon.ico for branded app (optional)")

# Summary
print("\n" + "=" * 80)
print("📊 Verification Summary")
print("=" * 80)

if ERRORS:
    print(f"\n❌ {len(ERRORS)} ERROR(S) - Build will fail:")
    for i, error in enumerate(ERRORS, 1):
        print(f"  {i}. {error}")
    print("\nFix these errors before building!")
    sys.exit(1)

if WARNINGS:
    print(f"\n⚠️  {len(WARNINGS)} WARNING(S) - Build may succeed:")
    for i, warning in enumerate(WARNINGS, 1):
        print(f"  {i}. {warning}")
    print("\nRecommended to fix warnings for complete build.")

if not ERRORS and not WARNINGS:
    print("\n✅ ALL CHECKS PASSED!")
    print("\n🎉 Ready to build! Run: npm run build")
elif not ERRORS:
    print("\n✅ CRITICAL CHECKS PASSED - Can proceed with warnings")
    print("\n📦 You can try: npm run build")

print("=" * 80)
