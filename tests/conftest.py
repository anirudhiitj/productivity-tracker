"""
Pytest configuration and shared fixtures for unit tests.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_activity_logs.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)


@pytest.fixture
def sample_activity_log():
    """Provide a sample activity log for testing."""
    return {
        "log_id": "test-log-001",
        "timestamp": "2026-02-27T10:30:45",
        "process_name": "chrome.exe",
        "window_title": "GitHub - Google Chrome",
        "domain": "github.com",
        "category": "Productive",
        "duration_seconds": 300,
        "is_synced": 0,
    }


@pytest.fixture
def sample_process_snapshot():
    """Provide a sample process snapshot."""
    return {
        "timestamp": "2026-02-27T10:30:45",
        "pid": 12345,
        "process_name": "chrome.exe",
        "window_title": "GitHub - Google Chrome",
        "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    }
