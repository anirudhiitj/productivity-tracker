"""
Window title parser for extracting domain/application context from browser windows.
Intelligently focuses on the active/foreground window and extracts meaningful tab information.
"""

import logging
import re
import sys
import subprocess
import shutil
from typing import Optional, Tuple, Dict, List

_PLATFORM = sys.platform  # 'win32', 'linux', 'darwin'

if _PLATFORM == 'win32':
    import ctypes
    from ctypes import wintypes

logger = logging.getLogger(__name__)


class WindowTitleParser:
    """Parses window titles and focuses on the active/foreground window."""

    # Browser process names (cross-platform)
    if _PLATFORM == 'win32':
        BROWSER_PROCESSES = [
            "chrome.exe", "firefox.exe", "msedge.exe",
            "opera.exe", "brave.exe", "iexplore.exe",
        ]
        EXCLUDED_BROWSER_PROCESSES = [
            "msedgewebview2.exe", "chrome_proxy.exe",
            "chromedriver.exe", "geckodriver.exe",
        ]
    elif _PLATFORM == 'darwin':
        BROWSER_PROCESSES = [
            "google chrome", "firefox", "microsoft edge",
            "opera", "brave browser", "safari",
        ]
        EXCLUDED_BROWSER_PROCESSES = [
            "google chrome helper", "firefox content process",
        ]
    else:  # linux
        BROWSER_PROCESSES = [
            "chrome", "chromium", "chromium-browser", "firefox",
            "microsoft-edge", "opera", "brave-browser",
        ]
        EXCLUDED_BROWSER_PROCESSES = [
            "chromedriver", "geckodriver",
        ]

    @staticmethod
    def is_browser_process(process_name: str) -> bool:
        """Check if a process name is a known browser."""
        return process_name.lower() in WindowTitleParser.BROWSER_PROCESSES

    # System/noise window titles to filter out
    JUNK_WINDOW_TITLES = {
        "msctfime ui",
        "ime\\ mode\\/ indicator",
        "keyboard input method editor",
        "default ime",
        "taskbar",
        "cortana",
        "action center",
        "start",
        "search",
        "start menu",
        "windows powershell",
        "cmd.exe",
        "windows 10",
        "windows 11",
        "system",
        "desktop",
        "search results",
        "explorer"
    }

    # Common window title separators
    SEPARATORS = [" - ", " | ", " :: ", " • ", " — ", " ( ", ") "]

    # Regex patterns for common URL-like extractions
    PATTERNS = {
        "domains": re.compile(
            r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})?)",
            re.IGNORECASE,
        ),
        "bracketed": re.compile(r"\[([^\]]+)\]", re.IGNORECASE),
        "parenthesized": re.compile(r"\(([^)]+)\)", re.IGNORECASE),
    }

    @staticmethod
    def is_browser_process(process_name: Optional[str]) -> bool:
        """
        Check if a process is a browser.

        Args:
            process_name: Name of the process

        Returns:
            True if process is a browser, False otherwise.
        """
        if not process_name:
            return False
        
        proc_lower = process_name.lower()
        
        # Exclude known non-browser processes first
        if proc_lower in WindowTitleParser.EXCLUDED_BROWSER_PROCESSES:
            return False
        
        # Check if it's a known browser
        return proc_lower in WindowTitleParser.BROWSER_PROCESSES

    @staticmethod
    def is_junk_window(title: Optional[str]) -> bool:
        """
        Check if a window title is system junk or internal process.
        
        Args:
            title: Window title to check
            
        Returns:
            True if it's junk, False if it's meaningful
        """
        if not title:
            return True
        
        title_lower = title.lower().strip()
        
        # Check against junk list
        for junk in WindowTitleParser.JUNK_WINDOW_TITLES:
            if junk in title_lower or title_lower in junk:
                return True
        
        # Filter very short titles (likely system)
        if len(title_lower) < 3:
            return True
        
        # Filter titles that are just numbers or special chars
        if not any(c.isalnum() for c in title_lower):
            return True
        
        return False

    @staticmethod
    def get_foreground_window_info() -> Optional[Tuple[str, int]]:
        """
        Get the currently active/foreground window's title and process ID.
        
        Returns:
            Tuple of (window_title, pid) or None if unable to get
        """
        try:
            if _PLATFORM == 'win32':
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if not hwnd:
                    return None
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return None
                buffer = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value
                pid = wintypes.DWORD()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if WindowTitleParser.is_junk_window(title):
                    return None
                return (title, pid.value)

            elif _PLATFORM == 'linux':
                if not shutil.which('xdotool'):
                    return None
                wid = subprocess.check_output(
                    ['xdotool', 'getactivewindow'], stderr=subprocess.DEVNULL
                ).decode().strip()
                title = subprocess.check_output(
                    ['xdotool', 'getactivewindow', 'getwindowname'], stderr=subprocess.DEVNULL
                ).decode().strip()
                pid_str = subprocess.check_output(
                    ['xdotool', 'getwindowpid', wid], stderr=subprocess.DEVNULL
                ).decode().strip()
                pid = int(pid_str) if pid_str else 0
                if WindowTitleParser.is_junk_window(title):
                    return None
                return (title, pid)

            elif _PLATFORM == 'darwin':
                script_pid = 'tell application "System Events" to unix id of first process whose frontmost is true'
                pid_result = subprocess.check_output(
                    ['osascript', '-e', script_pid], stderr=subprocess.DEVNULL
                ).decode().strip()
                script_title = (
                    'tell application "System Events" to get the title of the '
                    'front window of (first process whose frontmost is true)'
                )
                title = subprocess.check_output(
                    ['osascript', '-e', script_title], stderr=subprocess.DEVNULL
                ).decode().strip()
                pid = int(pid_result) if pid_result else 0
                if WindowTitleParser.is_junk_window(title):
                    return None
                return (title, pid)

        except Exception as e:
            logger.debug(f"Error getting foreground window: {e}")
            return None

    @staticmethod
    def get_all_browser_windows() -> List[Tuple[int, str]]:
        """
        Get all visible browser windows (not just foreground).
        
        Returns:
            List of (pid, window_title) tuples for browser processes
        """
        windows = []

        if _PLATFORM == 'win32':
            def enum_windows_callback(hwnd, lParam):
                try:
                    if not ctypes.windll.user32.IsWindowVisible(hwnd):
                        return True
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    if length == 0:
                        return True
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
                    title = buffer.value
                    if WindowTitleParser.is_junk_window(title):
                        return True
                    pid = wintypes.DWORD()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    windows.append((pid.value, title))
                    return True
                except:
                    return True
            try:
                callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                enum_func = callback(enum_windows_callback)
                ctypes.windll.user32.EnumWindows(enum_func, 0)
            except Exception as e:
                logger.debug(f"Error enumerating windows: {e}")

        elif _PLATFORM == 'linux':
            # Use wmctrl to list all windows
            try:
                if shutil.which('wmctrl'):
                    output = subprocess.check_output(
                        ['wmctrl', '-lp'], stderr=subprocess.DEVNULL
                    ).decode(errors='replace')
                    for line in output.strip().splitlines():
                        parts = line.split(None, 4)
                        if len(parts) >= 5:
                            pid = int(parts[2])
                            title = parts[4]
                            if not WindowTitleParser.is_junk_window(title):
                                windows.append((pid, title))
                elif shutil.which('xdotool'):
                    wids = subprocess.check_output(
                        ['xdotool', 'search', '--onlyvisible', '--name', ''],
                        stderr=subprocess.DEVNULL
                    ).decode().strip().splitlines()
                    for wid in wids:
                        try:
                            title = subprocess.check_output(
                                ['xdotool', 'getwindowname', wid], stderr=subprocess.DEVNULL
                            ).decode().strip()
                            pid_str = subprocess.check_output(
                                ['xdotool', 'getwindowpid', wid], stderr=subprocess.DEVNULL
                            ).decode().strip()
                            pid = int(pid_str) if pid_str else 0
                            if not WindowTitleParser.is_junk_window(title):
                                windows.append((pid, title))
                        except Exception:
                            continue
            except Exception as e:
                logger.debug(f"Error enumerating windows on Linux: {e}")

        elif _PLATFORM == 'darwin':
            try:
                script = '''
                    set windowList to {}
                    tell application "System Events"
                        set allProcs to every process whose visible is true
                        repeat with proc in allProcs
                            try
                                set procName to name of proc
                                set procID to unix id of proc
                                set allWindows to every window of proc
                                repeat with w in allWindows
                                    try
                                        set wTitle to name of w
                                        set end of windowList to (procID as text) & "|||" & wTitle
                                    end try
                                end repeat
                            end try
                        end repeat
                    end tell
                    set AppleScript's text item delimiters to "\n"
                    return windowList as text
                '''
                result = subprocess.check_output(
                    ['osascript', '-e', script], stderr=subprocess.DEVNULL
                ).decode(errors='replace').strip()
                for line in result.splitlines():
                    if '|||' in line:
                        pid_str, title = line.split('|||', 1)
                        pid = int(pid_str.strip()) if pid_str.strip().isdigit() else 0
                        if not WindowTitleParser.is_junk_window(title):
                            windows.append((pid, title))
            except Exception as e:
                logger.debug(f"Error enumerating windows on macOS: {e}")

        return windows

    @staticmethod
    def extract_domain_from_title(title: Optional[str]) -> Optional[str]:
        """
        Extract domain or site name from browser window title intelligently.
        Smart extraction that handles complex titles with multiple separators.

        Common formats:
        - "Integer Break - LeetCode - Google Chrome" → "leetcode"
        - "Google Gemini - Google Chrome" → "gemini"  
        - "Gmail - Sign in" → "gmail"
        - "Wikipedia, the free encyclopedia" → "wikipedia"
        - "YouTube - Video Title" → "youtube"

        Args:
            title: Window title string

        Returns:
            Extracted domain or site name, or None if unable to parse.
        """
        if not title or len(title.strip()) == 0:
            return None

        title = title.strip()

        # Step 1: Try to extract actual domain URL patterns (highest confidence)
        url_pattern = re.compile(
            r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)",
            re.IGNORECASE,
        )
        url_match = url_pattern.search(title)
        if url_match:
            domain = url_match.group(1).lower()
            if "." in domain and len(domain) > 3:
                return domain

        # Step 2: Known site keywords to look for (highest priority)
        # Order matters - more specific sites first
        known_sites = {
            "leetcode": r"\bleetcode\b",
            "gemini": r"\bgemini\b",
            "sheets": r"\bsheets\b",
            "github": r"\bgithub\b",
            "gitlab": r"\bgilab\b",
            "gmail": r"\bgmail\b",
            "slack": r"\bslack\b",
            "notion": r"\bnotion\b",
            "youtube": r"\byoutube\b",
            "netflix": r"\bnetflix\b",
            "reddit": r"\breddit\b",
            "twitter": r"\btwitter\b",
            "facebook": r"\bfacebook\b",
            "instagram": r"\binstagram\b",
            "linkedin": r"\blinkedin\b",
            "discord": r"\bdiscord\b",
            "twitch": r"\btwitch\b",
            "amazon": r"\bamazon\b",
            "google": r"\bgoogle\b",
            "docs": r"\bdocs\b",
            "drive": r"\bdrive\b",
            "figma": r"\bfigma\b",
            "stack overflow": r"\bstack\s+overflow\b",
            "wikipedia": r"\bwikipedia\b",
        }
        
        title_lower = title.lower()
        for site_name, pattern in known_sites.items():
            if re.search(pattern, title_lower):
                return site_name

        # Step 3: Try bracketed format [Site]
        bracketed = WindowTitleParser.PATTERNS["bracketed"].search(title)
        if bracketed:
            domain = bracketed.group(1).strip().lower()
            if domain and len(domain) > 2:
                return domain

        # Step 4: Smart separator parsing
        # Remove browser suffixes first to clean up the title
        browser_suffixes = [
            " - Chrome", " - Firefox", " - Edge", " - Opera", " - Brave", " - Explorer",
            " | Chrome", " | Firefox", " | Edge",
            " – Chrome", " – Firefox",
        ]
        clean_title = title
        for suffix in browser_suffixes:
            if clean_title.lower().endswith(suffix.lower()):
                clean_title = clean_title[: -len(suffix)].strip()
                break

        # Now parse the cleaned title
        # Pattern: [Page Title] - [SITE_NAME] or [SITE_NAME] - [Subtitle]
        separators = [" - ", " | ", " — ", " – "]
        
        for separator in separators:
            if separator in clean_title:
                parts = clean_title.split(separator)
                
                # Try to find which part is the site name (usually 1-3 words)
                for i, part in enumerate(parts):
                    part_clean = part.strip().lower()
                    if len(part_clean) > 2 and len(part_clean) < 30:
                        # Filter out number-heavy parts (usually page titles)
                        num_count = sum(1 for c in part_clean if c.isdigit())
                        if num_count < len(part_clean) * 0.3:  # Less than 30% numbers
                            # Take first word if multiple words
                            words = part_clean.split()
                            if words:
                                first_word = words[0]
                                # Return if it's a good-looking word
                                if len(first_word) > 2 and (first_word.isalpha() or "-" in first_word):
                                    return first_word

        # Step 5: Extract with whitespace awareness
        # If title is short enough, try to extract meaningful parts
        if len(clean_title) < 50:
            words = clean_title.lower().split()
            # Return first significant word
            for word in words:
                if len(word) > 3 and word.isalpha():
                    return word

        return None

    @staticmethod
    def normalize_domain(domain: Optional[str]) -> Optional[str]:
        """
        Normalize domain string for consistent categorization.

        Args:
            domain: Raw domain string

        Returns:
            Normalized domain string, or None if empty.
        """
        if not domain:
            return None

        domain = domain.strip()

        # Remove special characters and extra whitespace
        domain = re.sub(r"[^\w\s.-]", "", domain)
        domain = re.sub(r"\s+", " ", domain).strip()

        # Convert to lowercase
        domain = domain.lower()

        # Limit length
        if len(domain) > 100:
            domain = domain[:100]

        # Check if result is empty
        if not domain or domain == "":
            return None

        return domain

    @staticmethod
    def extract_full_domain_url(title: Optional[str]) -> Optional[str]:
        """
        Try to extract full domain URL from title.

        Args:
            title: Window title string

        Returns:
            Domain URL if found, None otherwise.
        """
        if not title:
            return None

        # Look for URL pattern
        url_pattern = re.compile(
            r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)",
            re.IGNORECASE,
        )
        match = url_pattern.search(title)
        if match:
            return match.group(1).lower()

        return None

    @staticmethod
    def categorize_window_title(title: Optional[str]) -> str:
        """
        Quick categorization based on common keywords in title.

        Args:
            title: Window title string

        Returns:
            Category string or 'Neutral'
        """
        if not title:
            return "Neutral"

        title_lower = title.lower()

        # Productive indicators
        productive_keywords = [
            "github",
            "gitlab",
            "jira",
            "confluence",
            "slack",
            "gmail",
            "outlook",
            "drive",
            "docs",
            "sheets",
            "notion",
            "vscode",
            "devenv",
            "pycharm",
            "stack overflow",
        ]
        for keyword in productive_keywords:
            if keyword in title_lower:
                return "Productive"

        # Educational indicators
        educational_keywords = [
            "udemy",
            "coursera",
            "khan academy",
            "edx",
            "skillshare",
            "datacamp",
            "wikipedia",
            "learn",
            "tutorial",
            "course",
        ]
        for keyword in educational_keywords:
            if keyword in title_lower:
                return "Educational"

        # Entertainment indicators
        entertainment_keywords = [
            "youtube",
            "netflix",
            "hulu",
            "twitch",
            "instagram",
            "tiktok",
            "reddit",
            "twitter",
            "facebook",
            "spotify",
            "music",
            "video",
        ]
        for keyword in entertainment_keywords:
            if keyword in title_lower:
                return "Entertainment"

        # Gaming indicators
        gaming_keywords = [
            "steam",
            "epic games",
            "valorant",
            "minecraft",
            "fortnite",
            "roblox",
            "game",
        ]
        for keyword in gaming_keywords:
            if keyword in title_lower:
                return "Gaming"

        return "Neutral"
