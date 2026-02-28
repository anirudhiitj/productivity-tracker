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
import socket
import psutil

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


def cleanup_ports(ports=[8000, 3000]):
    """Kill any existing processes using the specified ports."""
    for port in ports:
        try:
            # Try to find and kill processes using this port
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.net_connections(kind='inet'):
                        if conn.laddr.port == port and conn.status == 'LISTEN':
                            logger.info(f"Killing existing process on port {port} (PID: {proc.pid})")
                            proc.kill()
                            time.sleep(1)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
        except Exception as e:
            logger.warning(f"Could not cleanup port {port}: {e}")


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
        
        # Give it a moment to start
        time.sleep(1)
        
        # Check if it's still running
        poll_result = backend_process.poll()
        if poll_result is not None:
            # Process exited immediately - something went wrong
            _, stderr = backend_process.communicate()
            logger.error(f"Backend process exited immediately with code {poll_result}")
            if stderr:
                logger.error(f"Error output: {stderr[:500]}")
            return None
        
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
                "npm install",
                cwd=FRONTEND_DIR,
                capture_output=True,
                timeout=300,
                shell=True
            )
            if install_result.returncode != 0:
                logger.warning("npm install had warnings, but continuing...")
        except Exception as e:
            logger.error(f"Failed to install frontend dependencies: {e}")
            logger.info("Make sure Node.js and npm are installed")
            return None
    
    try:
        # Use shell=True on Windows to properly resolve npm command in PATH
        frontend_process = subprocess.Popen(
            "npm run dev -- --host 127.0.0.1 --port 3000 --strictPort",
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True
        )
        
        logger.info("Frontend process started (PID: %d)", frontend_process.pid)
        logger.info("Frontend URL: http://localhost:3000")
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if it's still running
        poll_result = frontend_process.poll()
        if poll_result is not None:
            # Process exited immediately - something went wrong
            _, stderr = frontend_process.communicate()
            logger.error(f"Frontend process exited immediately with code {poll_result}")
            if stderr:
                logger.error(f"Error output: {stderr[:500]}")
            return None
        
        return frontend_process
        
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
    
    # Clean up any existing processes on required ports
    logger.info("Cleaning up old processes...")
    cleanup_ports([8000, 3000])
    time.sleep(2)
    
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
