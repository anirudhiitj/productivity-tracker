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
    
    # Check if port is available before starting
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        logger.error(f"Port {port} is already in use!")
        logger.error("Please close any existing instances or wait a few seconds.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    logger.info(f"Port {port} is available")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
    
    try:
        # For frozen executables, use app instance; for dev, use string path
        if getattr(sys, 'frozen', False):
            logger.info("Running as frozen executable")
            logger.info("Starting uvicorn with app instance...")
            
            # Configure uvicorn with explicit server settings
            config = uvicorn.Config(
                app,
                host="127.0.0.1",
                port=port,
                log_level="info",
                access_log=False,
                loop="asyncio"
            )
            server = uvicorn.Server(config)
            
            logger.info("Uvicorn server configured, starting...")
            server.run()
            logger.info("Uvicorn server.run() returned")
        else:
            logger.info("Running as Python script")
            uvicorn.run(
                "backend.main:app",
                host="127.0.0.1",
                port=port,
                log_level="info",
                access_log=False,
                reload=False
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"FATAL: Uvicorn failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    finally:
        logger.info("Server process complete")
