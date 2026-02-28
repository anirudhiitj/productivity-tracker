"""
Entrypoint used for local runs and PyInstaller builds.
Starts the FastAPI backend server for the desktop app.
"""

import os
import sys
import logging
from pathlib import Path

import uvicorn


if getattr(sys, "frozen", False):
    runtime_dir = Path(sys.executable).resolve().parent
    os.chdir(runtime_dir)
else:
    runtime_dir = Path(__file__).resolve().parent
    os.chdir(runtime_dir)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Configure logging BEFORE importing app
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers = [logging.StreamHandler(sys.stdout)]

log_file_env = os.environ.get("TRACKER_LOG_FILE", "").strip()
if log_file_env:
    log_file_path = Path(log_file_env)
elif getattr(sys, "frozen", False):
    log_file_path = runtime_dir / "agent.log"
else:
    log_file_path = Path(__file__).resolve().parent / "agent.log"

try:
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    handlers.append(logging.FileHandler(log_file_path, encoding='utf-8'))
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file_path}")
logger.info(f"Runtime directory: {runtime_dir}")

try:
    from backend.main import app
    logger.info("FastAPI app loaded successfully")
except Exception as e:
    logger.exception(f"FATAL: Failed to load FastAPI app: {e}")
    sys.exit(1)


if __name__ == "__main__":
    port = int(os.environ.get("TRACKER_BACKEND_PORT", "8000"))
    logger.info(f"Starting backend on http://127.0.0.1:{port}")
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info", access_log=False)
    except Exception as e:
        logger.exception(f"FATAL: Uvicorn failed: {e}")
        sys.exit(1)
