"""
Process tracker for capturing foreground window and process information.
Uses Windows API to poll the active window every 1 second.
"""

import ctypes
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict
import psutil

logger = logging.getLogger(__name__)

# Windows API constants and functions
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW


class ProcessTracker:
    """Tracks active foreground process and window information on Windows."""

    def __init__(self):
        self.current_process: Optional[Dict] = None
        self.previous_process: Optional[Dict] = None
        self.activity_start_time: Optional[datetime] = None

    def get_foreground_window_pid(self) -> Optional[int]:
        """
        Get the PID of the currently active foreground window.

        Returns:
            PID of foreground window process, or None if unable to determine.
        """
        try:
            hwnd = GetForegroundWindow()
            if not hwnd:
                return None

            pid = ctypes.c_ulong()
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return pid.value if pid.value else None
        except Exception as e:
            logger.error(f"Error getting foreground window PID: {e}")
            return None

    def get_window_title(self) -> Optional[str]:
        """
        Get the title of the currently active foreground window.

        Returns:
            Window title string, or None if unable to determine.
        """
        try:
            hwnd = GetForegroundWindow()
            if not hwnd:
                return None

            # Get buffer size
            length = GetWindowTextLengthW(hwnd)
            if length == 0:
                return None

            # Create buffer and get text
            buffer = ctypes.create_unicode_buffer(length + 1)
            GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        except Exception as e:
            logger.error(f"Error getting window title: {e}")
            return None

    def pid_to_process_name(self, pid: int) -> Optional[str]:
        """
        Convert a process ID to its executable name.

        Args:
            pid: Process ID

        Returns:
            Process executable name (e.g., 'chrome.exe'), or None if unable to determine.
        """
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Error getting process name for PID {pid}: {e}")
            return None

    def get_process_path(self, pid: int) -> Optional[str]:
        """
        Get the full path of a process executable.

        Args:
            pid: Process ID

        Returns:
            Full path to executable, or None if unable to determine.
        """
        try:
            process = psutil.Process(pid)
            return process.exe()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Error getting process path for PID {pid}: {e}")
            return None

    def poll_active_process(self) -> Dict:
        """
        Poll the currently active process and window.

        Returns:
            Dictionary containing:
            - timestamp: Current timestamp
            - pid: Process ID
            - process_name: Executable name
            - window_title: Window title
            - process_path: Full path to executable
        """
        timestamp = datetime.now().isoformat()
        pid = self.get_foreground_window_pid()

        if not pid:
            return {
                "timestamp": timestamp,
                "pid": None,
                "process_name": None,
                "window_title": None,
                "process_path": None,
            }

        process_name = self.pid_to_process_name(pid)
        window_title = self.get_window_title()
        process_path = self.get_process_path(pid)

        return {
            "timestamp": timestamp,
            "pid": pid,
            "process_name": process_name,
            "window_title": window_title,
            "process_path": process_path,
        }

    def detect_activity_change(
        self, previous_snapshot: Optional[Dict], current_snapshot: Dict
    ) -> Tuple[bool, Optional[Dict], Optional[Dict]]:
        """
        Detect if the active process has changed.

        Args:
            previous_snapshot: Previous process snapshot
            current_snapshot: Current process snapshot

        Returns:
            Tuple of (has_changed, previous_activity, current_activity)
        """
        if not previous_snapshot or not current_snapshot:
            return False, None, None

        # Activity changes when PID changes
        if previous_snapshot["pid"] != current_snapshot["pid"]:
            return True, previous_snapshot, current_snapshot

        return False, None, None

    def get_activity_duration(self) -> Optional[int]:
        """
        Get the duration of current activity in milliseconds.

        Returns:
            Duration in milliseconds, or None if activity not started.
        """
        if not self.activity_start_time:
            return None

        duration_ms = int(
            (datetime.now() - self.activity_start_time).total_seconds() * 1000
        )
        return duration_ms

    def update_activity(self, snapshot: Dict) -> None:
        """
        Update current activity tracking.

        Args:
            snapshot: Current process snapshot from poll_active_process()
        """
        self.previous_process = self.current_process
        self.current_process = snapshot
        self.activity_start_time = datetime.now()

    def reset_activity(self) -> None:
        """Reset activity tracking."""
        self.current_process = None
        self.previous_process = None
        self.activity_start_time = None
