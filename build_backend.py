"""Build the Python backend as a PyInstaller onedir bundle for Electron."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
WORK_DIR = BUILD_DIR / "pyi"
SPEC_DIR = BUILD_DIR / "spec"

BACKEND_OUTPUT_DIR = DIST_DIR / "tracker-backend"
BACKEND_EXE = BACKEND_OUTPUT_DIR / "tracker-backend.exe"


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT_DIR), check=True)


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # type: ignore # noqa: F401
    except ImportError:
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def clean_dirs() -> None:
    for path in [WORK_DIR, SPEC_DIR, BACKEND_OUTPUT_DIR]:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def build_backend() -> None:
    add_data = [
        f"{ROOT_DIR / 'backend'};backend",
        f"{ROOT_DIR / 'client'};client",
        f"{ROOT_DIR / 'data'};data",
    ]

    hidden_imports = [
        # Win32 APIs for window enumeration
        "win32api",
        "win32con",
        "win32process",
        "win32gui",
        # FastAPI / Uvicorn
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "fastapi",
        "pydantic",
        "starlette",
        # psutil for process monitoring
        "psutil",
        # ctypes for window enumeration
        "ctypes",
        "ctypes.wintypes",
        # sqlite3 for website cache
        "sqlite3",
        # Encoding support
        "encodings",
        "encodings.utf_8",
        "encodings.ascii",
        "encodings.latin_1",
        "encodings.cp1252",
    ]

    # Optional: Google Generative AI
    try:
        import google.generativeai  # noqa: F401
        hidden_imports.append("google.generativeai")
    except ImportError:
        pass

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--console",
        "--name",
        "tracker-backend",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(WORK_DIR),
        "--specpath",
        str(SPEC_DIR),
    ]

    for item in add_data:
        cmd.extend(["--add-data", item])
    for item in hidden_imports:
        cmd.extend(["--hidden-import", item])

    cmd.extend(["--collect-all", "pywin32"])
    # Try to collect google-generativeai if it's installed
    try:
        import google.generativeai  # noqa: F401
        cmd.extend(["--collect-all", "google"])
    except ImportError:
        pass
    
    cmd.append("server.py")

    run(cmd)


def verify() -> None:
    if not BACKEND_EXE.exists():
        raise FileNotFoundError(f"Backend executable not found: {BACKEND_EXE}")

    size_mb = BACKEND_EXE.stat().st_size / (1024 * 1024)
    print("=" * 70)
    print("Backend build complete")
    print(f"Executable: {BACKEND_EXE}")
    print(f"Size: {size_mb:.1f} MB")
    print("Test: dist\\tracker-backend\\tracker-backend.exe")
    print("=" * 70)


def main() -> None:
    print("=" * 70)
    print("Building backend bundle for Electron")
    print("=" * 70)
    ensure_pyinstaller()
    clean_dirs()
    build_backend()
    verify()


if __name__ == "__main__":
    main()
