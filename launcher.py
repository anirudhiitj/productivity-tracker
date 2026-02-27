#!/usr/bin/env python3
"""
Main launcher - Start both backend (FastAPI) and frontend (React) servers.
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def check_requirements():
    """Check if required packages are installed."""
    logger.info("Checking Python dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import psutil
        logger.info("✅ Python dependencies OK")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing Python dependency: {e}")
        logger.info("Run: pip install -r requirements.txt")
        return False


def start_backend():
    """Start FastAPI backend server."""
    logger.info("=" * 60)
    logger.info("Starting FastAPI Backend Server")
    logger.info("=" * 60)
    
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", 
             "--host", "127.0.0.1", "--port", "8000", "--reload"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        logger.info("Backend process started (PID: %d)", backend_process.pid)
        logger.info("Backend URL: http://localhost:8000")
        logger.info("API Docs: http://localhost:8000/docs")
        
        return backend_process
        
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        return None


def start_frontend():
    """Start React frontend development server."""
    logger.info("=" * 60)
    logger.info("Starting React Frontend Server")
    logger.info("=" * 60)
    
    # Check if node_modules exists
    if not (FRONTEND_DIR / "node_modules").exists():
        logger.info("Installing frontend dependencies (npm install)...")
        try:
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=FRONTEND_DIR,
                capture_output=True,
                timeout=300
            )
            if install_result.returncode != 0:
                logger.warning("npm install had warnings, but continuing...")
        except Exception as e:
            logger.error(f"Failed to install frontend dependencies: {e}")
            logger.info("Make sure Node.js and npm are installed")
            return None
    
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        logger.info("Frontend process started (PID: %d)", frontend_process.pid)
        logger.info("Frontend URL: http://localhost:3000")
        
        return frontend_process
        
    except FileNotFoundError:
        logger.error("npm not found. Make sure Node.js is installed")
        logger.info("Download from: https://nodejs.org/")
        return None
    except Exception as e:
        logger.error(f"Failed to start frontend: {e}")
        return None


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Productivity Tracker - Full Stack Launch")
    logger.info("=" * 60)
    
    # Check Python dependencies
    if not check_requirements():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    time.sleep(2)  # Give backend time to start
    
    # Start frontend
    frontend_process = start_frontend()
    
    if not backend_process and not frontend_process:
        logger.error("Failed to start any servers")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("✅ All servers started successfully!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📊 Frontend:  http://localhost:3000  (React UI)")
    logger.info("⚙️  Backend:   http://localhost:8000 (FastAPI)")
    logger.info("📚 API Docs:  http://localhost:8000/docs")
    logger.info("")
    logger.info("Press Ctrl+C to stop all servers")
    logger.info("=" * 60)
    
    # Keep processes running
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still alive
            if backend_process and backend_process.poll() is not None:
                logger.warning("Backend process terminated")
                break
            
            if frontend_process and frontend_process.poll() is not None:
                logger.warning("Frontend process terminated")
                break
                
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Shutting down servers...")
        logger.info("=" * 60)
        
        # Terminate processes
        if backend_process:
            try:
                backend_process.terminate()
                backend_process.wait(timeout=5)
            except:
                backend_process.kill()
        
        if frontend_process:
            try:
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
            except:
                frontend_process.kill()
        
        logger.info("✅ All servers stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
