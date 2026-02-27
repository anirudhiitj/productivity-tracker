"""
FastAPI Application - Main entry point for the backend server.
Provides real-time process monitoring via REST API.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import processes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown handler."""
    logger.info("=" * 60)
    logger.info("Productivity Tracker Backend Starting")
    logger.info("=" * 60)
    logger.info("API Server running on http://localhost:8000")
    logger.info("Documentation available at http://localhost:8000/docs")
    logger.info("=" * 60)
    yield
    logger.info("Productivity Tracker Backend Shutting Down")


# Create FastAPI app
app = FastAPI(
    title="Productivity Tracker Backend",
    description="Real-time process monitoring and activity tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(processes.router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Productivity Tracker Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "main_processes": "/api/processes/main",
            "all_processes": "/api/processes/all",
            "stats": "/api/processes/stats",
            "by_category": "/api/processes/category/{category}",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # Run development server
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
