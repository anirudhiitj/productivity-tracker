"""
FastAPI routes for process monitoring endpoints.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict
import logging

from backend.process_monitor import ProcessMonitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["processes"])

# Initialize process monitor
process_monitor = ProcessMonitor()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "productivity_tracker_backend"
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
        processes = process_monitor.get_main_processes()
        stats = process_monitor.get_process_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "processes": processes,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting main processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/all")
async def get_all_processes():
    """
    Get all running processes (including light processes).

    Warning: May return 200+ processes. Use /processes/main for filtered view.
    """
    try:
        processes = process_monitor.get_all_processes()

        return {
            "timestamp": datetime.now().isoformat(),
            "process_count": len(processes),
            "processes": processes
        }
    except Exception as e:
        logger.error(f"Error getting all processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/stats")
async def get_process_stats():
    """Get aggregate statistics of main processes."""
    try:
        stats = process_monitor.get_process_stats()

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
        all_processes = process_monitor.get_main_processes()

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
