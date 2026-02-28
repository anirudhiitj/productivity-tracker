"""
FastAPI routes for process monitoring endpoints.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict, Optional
import logging
import asyncio
from functools import partial

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["processes"])

# Lazy initialization - ProcessMonitor is heavy and may fail on some systems
process_monitor: Optional['ProcessMonitor'] = None

def get_process_monitor():
    """Lazily initialize ProcessMonitor on first use."""
    global process_monitor
    if process_monitor is None:
        try:
            from backend.process_monitor import ProcessMonitor
            process_monitor = ProcessMonitor()
            logger.info("ProcessMonitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ProcessMonitor: {e}", exc_info=True)
            # Return a dummy object that won't crash the app
            class DummyMonitor:
                def get_main_processes(self): return []
                def get_process_stats(self): return {"total": 0}
            process_monitor = DummyMonitor()
    return process_monitor


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        monitor = get_process_monitor()
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "productivity_tracker_backend",
            "monitor_available": True
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "productivity_tracker_backend",
            "monitor_available": False
        }


@router.get("/processes/main")
async def get_main_processes():
    """
    Get all main (heavy resource) processes.

    Returns filtered processes with:
    - RAM > 100MB OR CPU > 1%
    - Categorized by activity type
    - Sorted by memory usage (descending)
    """
    try:
        monitor = get_process_monitor()
        
        # Run get_main_processes in a thread with timeout to prevent hanging
        loop = asyncio.get_event_loop()
        try:
            processes = await asyncio.wait_for(
                loop.run_in_executor(None, monitor.get_main_processes),
                timeout=15.0  # 15 second timeout
            )
            # Pass pre-fetched processes to stats to avoid double-scan
            stats = monitor.get_process_stats(main_processes=processes)
        except asyncio.TimeoutError:
            logger.error("Timeout getting processes - returning empty result")
            return {
                "timestamp": datetime.now().isoformat(),
                "processes": [],
                "stats": {"total_processes": 0, "total_memory_mb": 0, "total_cpu_percent": 0},
                "error": "Request timed out"
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "processes": processes,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting main processes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/all")
async def get_all_processes():
    """
    Get all running processes (including light processes).

    Warning: May return 200+ processes. Use /processes/main for filtered view.
    """
    try:
        monitor = get_process_monitor()
        
        # Run get_all_processes in a thread with timeout
        loop = asyncio.get_event_loop()
        try:
            processes = await asyncio.wait_for(
                loop.run_in_executor(None, monitor.get_all_processes),
                timeout=10.0  # 10 second timeout
            )
        except asyncio.TimeoutError:
            logger.error("Timeout getting all processes - returning empty result")
            return {
                "timestamp": datetime.now().isoformat(),
                "process_count": 0,
                "processes": [],
                "error": "Request timed out"
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "process_count": len(processes),
            "processes": processes
        }
    except Exception as e:
        logger.error(f"Error getting all processes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/stats")
async def get_process_stats():
    """Get aggregate statistics of main processes."""
    try:
        monitor = get_process_monitor()
        stats = monitor.get_process_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting process stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/category/{category}")
async def get_processes_by_category(category: str):
    """
    Get processes filtered by activity category.

    Category options: Productive, Gaming, Educational, Entertainment, Neutral
    """
    try:
        monitor = get_process_monitor()
        all_processes = monitor.get_main_processes()

        # Filter by category (case-insensitive)
        filtered = [p for p in all_processes if p.get('category', '').lower() == category.lower()]

        return {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "process_count": len(filtered),
            "processes": filtered
        }
    except Exception as e:
        logger.error(f"Error getting processes by category: {e}")
        raise HTTPException(status_code=500, detail=str(e))
