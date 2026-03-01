"""
Process Monitor - Monitors all system processes and filters heavy processes.
Integrates with CategoryEngine for activity categorization and WebsiteCategorizer.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import psutil
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

_PLATFORM = sys.platform  # 'win32', 'linux', 'darwin'

# Add parent directory to path to import from client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.category_engine import CategoryEngine
from client.window_parser import WindowTitleParser
from backend.website_categorizer import get_website_categorizer
from backend.chrome_tab_monitor import get_chrome_tab_monitor

logger = logging.getLogger(__name__)

# Thread pool for async categorization
_executor = ThreadPoolExecutor(max_workers=3)


class ProcessMonitor:
    """Monitor and filter system processes by resource usage."""

    # Thresholds for "main" processes
    MIN_MEMORY_MB = 100  # 100 MB minimum
    MIN_CPU_PERCENT = 1.0  # 1% CPU minimum

    # System processes to exclude (cross-platform)
    if _PLATFORM == 'win32':
        EXCLUDED_PROCESSES = {
            "system", "svchost.exe", "lsass.exe", "csrss.exe",
            "wininit.exe", "services.exe", "lsm.exe", "dwm.exe",
            "searchindexer.exe", "windows.indexing.service",
            "ntoskrnl.exe", "idle", "registry", "smss.exe",
            "conhost.exe", "dllhost.exe", "rundll32.exe",
            "taskhostw.exe", "windowsupdate.exe"
        }
    elif _PLATFORM == 'darwin':
        EXCLUDED_PROCESSES = {
            "kernel_task", "launchd", "syslogd", "mds", "mds_stores",
            "mdworker", "opendirectoryd", "notifyd", "WindowServer",
            "loginwindow", "distnoted", "cfprefsd", "lsd",
            "trustd", "securityd", "coreservicesd", "hidd",
            "coreaudiod", "powerd", "timed", "fseventsd",
        }
    else:  # linux
        EXCLUDED_PROCESSES = {
            "systemd", "kthreadd", "ksoftirqd", "kworker",
            "rcu_sched", "migration", "watchdog", "kswapd",
            "jbd2", "ksmd", "khugepaged", "kcompactd",
            "irq", "dbus-daemon", "polkitd", "accounts-daemon",
            "networkmanager", "gdm3", "gnome-shell",
        }

    def __init__(self):
        """Initialize process monitor."""
        self.process_start_times: Dict[int, datetime] = {}
        self._active_window_cache = None
        self._active_window_cache_time = None
        logger.info("ProcessMonitor initialized")

    def get_all_processes(self) -> List[Dict]:
        """
        Get all running processes with resource info.
        Optimized: avoids slow username lookups and uses minimal attrs.

        Returns:
            List of process dictionaries with full info.
        """
        processes = []

        try:
            # Only request fast attributes - username is VERY slow on Windows
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'create_time']):
                try:
                    info = proc.info
                    mem_info = info.get('memory_info')
                    if not mem_info:
                        continue
                    
                    memory_mb = mem_info.rss / (1024 * 1024)
                    cpu_percent = info.get('cpu_percent') or 0.0
                    
                    process_dict = {
                        'pid': info['pid'],
                        'name': info['name'] or 'Unknown',
                        'memory_mb': round(memory_mb, 2),
                        'memory_percent': 0,  # Will calculate below
                        'cpu_percent': round(cpu_percent, 2),
                        'username': 'User',  # Skip slow username lookup
                        'create_time': info.get('create_time') or 0,
                    }
                    
                    processes.append(process_dict)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.error(f"Error getting all processes: {e}")

        # Calculate memory percentages
        total_memory = psutil.virtual_memory().total / (1024 * 1024)
        for proc in processes:
            proc['memory_percent'] = round((proc['memory_mb'] / total_memory) * 100, 2)

        return processes

    def get_main_processes(self) -> List[Dict]:
        """
        Get filtered "main" processes (heavy RAM/CPU users).
        For browser processes, creates entry for EACH browser tab/window found.

        Criteria:
        - Memory > 100 MB OR CPU > 1%
        - Exclude system processes
        - Browser windows: one entry per browser tab

        Returns:
            Sorted list of main processes with enriched data.
        """
        all_processes = self.get_all_processes()
        main_processes = []

        for proc in all_processes:
            # Skip excluded system processes
            if proc['name'].lower() in self.EXCLUDED_PROCESSES:
                continue

            # Filter by resource usage
            if proc['memory_mb'] >= self.MIN_MEMORY_MB or proc['cpu_percent'] >= self.MIN_CPU_PERCENT:
                main_processes.append(proc)

        # Enrich with category and window title
        main_processes = self._enrich_processes(main_processes)
        
        # Try to get ALL Chrome tabs via DevTools Protocol (includes background tabs)
        chrome_monitor = get_chrome_tab_monitor()
        chrome_devtools_available = chrome_monitor.is_available()
        
        if chrome_devtools_available:
            logger.info("Chrome DevTools Protocol available - getting ALL tabs")
            chrome_tabs_from_devtools = chrome_monitor.get_all_tabs()
        else:
            logger.debug("Chrome DevTools Protocol not available - using window enumeration")
            chrome_tabs_from_devtools = []
        
        # Expand browser processes to show each tab/window as separate entry
        expanded_processes = []
        browser_windows_seen = set()
        
        # Get all browser windows globally (for non-Chrome browsers and fallback)
        all_windows = WindowTitleParser.get_all_browser_windows()
        
        # If Chrome DevTools is available, use it to create Chrome tab entries
        chrome_name = 'chrome.exe' if _PLATFORM == 'win32' else ('google chrome' if _PLATFORM == 'darwin' else 'chrome')
        if chrome_devtools_available and chrome_tabs_from_devtools:
            # Find a Chrome process to use as template for resource info
            chrome_proc_template = None
            for proc in main_processes:
                if proc['name'].lower() == chrome_name:
                    chrome_proc_template = proc
                    break
            
            # Create entry for each Chrome tab from DevTools
            for tab in chrome_tabs_from_devtools:
                tab_title = tab.get('title', 'Untitled')
                tab_url = tab.get('url', '')
                tab_domain = tab.get('domain', 'unknown')
                
                # Skip if already seen
                if tab_title in browser_windows_seen:
                    continue
                browser_windows_seen.add(tab_title)
                
                # Create synthetic process entry
                if chrome_proc_template:
                    tab_proc = chrome_proc_template.copy()
                else:
                    # No Chrome process found, create minimal entry
                    tab_proc = {
                        'pid': 0,
                        'name': chrome_name,
                        'memory_mb': 0,
                        'cpu_percent': 0,
                        'memory_percent': 0,
                        'username': 'User',
                        'create_time': datetime.now().timestamp(),
                    }
                
                tab_proc['window_title'] = tab_title
                tab_proc['domain'] = tab_domain
                tab_proc['url'] = tab_url
                
                # Categorize the tab
                categorizer = get_website_categorizer()
                category_result = categorizer.categorize(tab_domain, tab_title, tab_url)
                tab_proc['category'] = category_result.get('category', 'Neutral')
                tab_proc['categorization_source'] = 'devtools'
                tab_proc['domain_confidence'] = 1.0
                
                expanded_processes.append(tab_proc)
        
        # Handle browser processes (non-Chrome or when DevTools not available)
        for proc in main_processes:
            is_chrome = proc['name'].lower() in ('chrome.exe', 'chrome', 'chromium', 'chromium-browser', 'google chrome')
            
            # Skip Chrome if we already processed it via DevTools
            if is_chrome and chrome_devtools_available and chrome_tabs_from_devtools:
                continue
            
            if WindowTitleParser.is_browser_process(proc['name']):
                # Find all windows for this browser process
                proc_windows = [
                    title for pid, title in all_windows 
                    if pid == proc['pid'] and not WindowTitleParser.is_junk_window(title)
                ]
                
                if len(proc_windows) > 0:
                    # Has windows - create entry for each
                    for window_title in proc_windows:
                        if window_title not in browser_windows_seen:
                            browser_windows_seen.add(window_title)
                            tab_proc = proc.copy()
                            tab_proc['window_title'] = window_title
                            
                            # Extract domain and categorize
                            self._enrich_window(tab_proc, window_title)
                            expanded_processes.append(tab_proc)
                # Skip browser processes with no windows (background processes)
            else:
                # Non-browser process
                expanded_processes.append(proc)
        
        # Handle browser windows from processes not in main_processes
        # (this covers edge cases where a Chrome tab process is light but has visible windows)
        for pid, window_title in all_windows:
            if (not WindowTitleParser.is_junk_window(window_title) and 
                window_title not in browser_windows_seen):
                
                # Check if this is actually a browser process
                try:
                    p = psutil.Process(pid)
                    if not WindowTitleParser.is_browser_process(p.name()):
                        continue  # Skip non-browser processes
                except:
                    continue  # Skip if can't access process
                
                browser_windows_seen.add(window_title)
                
                # Try to find process or create synthetic entry
                try:
                    p = psutil.Process(pid)
                    proc = {
                        'pid': pid,
                        'name': p.name(),
                        'memory_mb': p.memory_info().rss / (1024 * 1024),
                        'cpu_percent': p.cpu_percent() or 0.0,
                        'memory_percent': 0,
                        'username': p.username() if hasattr(p, 'username') else 'System',
                        'create_time': p.create_time(),
                        'window_title': window_title
                    }
                except:
                    # Process may have died, use minimal entry
                    proc = {
                        'pid': pid,
                        'name': 'chrome' if _PLATFORM != 'win32' else 'chrome.exe',
                        'memory_mb': 0,
                        'cpu_percent': 0,
                        'memory_percent': 0,
                        'username': 'User',
                        'create_time': datetime.now().timestamp(),
                        'window_title': window_title
                    }
                
                self._enrich_window(proc, window_title)
                expanded_processes.append(proc)

        # Final filter: Remove any browser processes without window titles
        # (these are background processes like Edge WebView, Chrome GPU process, etc.)
        filtered_processes = []
        for proc in expanded_processes:
            if WindowTitleParser.is_browser_process(proc['name']):
                # Only include browser processes with window titles
                if proc.get('window_title') and proc.get('window_title') != 'N/A':
                    filtered_processes.append(proc)
            else:
                # Always include non-browser processes
                filtered_processes.append(proc)
        
        # Sort by memory usage (descending)
        filtered_processes.sort(key=lambda x: x['memory_mb'], reverse=True)

        return filtered_processes

    def _enrich_processes(self, processes: List[Dict]) -> List[Dict]:
        """
        Enrich processes with category and window information.
        Intelligently focuses on meaningful browser windows and filters out junk.
        Handles multiple windows per process (e.g., Chrome with many tabs).

        Args:
            processes: List of process dictionaries

        Returns:
            Enriched process list.
        """
        categorizer = get_website_categorizer()
        
        # Get all visible browser windows (not junk)
        all_browser_windows = WindowTitleParser.get_all_browser_windows()
        
        # Create a mapping of pid -> list of good window titles
        window_titles_by_pid = {}
        for pid, title in all_browser_windows:
            if not WindowTitleParser.is_junk_window(title):
                if pid not in window_titles_by_pid:
                    window_titles_by_pid[pid] = []
                window_titles_by_pid[pid].append(title)
        
        for proc in processes:
            process_name = proc['name']

            # Initialize fields  
            proc['window_title'] = None
            proc['domain'] = None
            proc['domain_confidence'] = 0.0
            proc['categorization_source'] = "heuristic"
            
            # For browser processes, try to get meaningful window titles
            if WindowTitleParser.is_browser_process(process_name):
                # Check if this process has browser windows
                if proc['pid'] in window_titles_by_pid:
                    windows = window_titles_by_pid[proc['pid']]
                    
                    # Use the longest/most informative window title as primary
                    best_window = max(windows, key=len) if windows else None
                    
                    if best_window:
                        proc['window_title'] = best_window
                        
                        # Extract domain from the best window title
                        domain = WindowTitleParser.extract_domain_from_title(best_window)
                        if domain:
                            proc['domain'] = domain
                            
                            # Use website categorizer for intelligent domain categorization
                            try:
                                result = categorizer.batch_categorize_sync([domain])
                                if domain in result:
                                    refined_category, domain_confidence, categorization_source = result[domain]
                                    proc['category'] = refined_category
                                    proc['domain_confidence'] = domain_confidence
                                    proc['categorization_source'] = categorization_source
                            except Exception as e:
                                logger.debug(f"Error categorizing domain {domain}: {e}")

            # Categorize activity if not already set via domain
            if 'category' not in proc or proc['category'] == 'Neutral':
                category = CategoryEngine.categorize_activity(
                    process_name=process_name,
                    domain=proc.get('domain'),
                    window_title=proc.get('window_title')
                )
                proc['category'] = category

            # Calculate runtime
            try:
                create_time = datetime.fromtimestamp(proc['create_time'])
                runtime = datetime.now() - create_time
                proc['runtime_seconds'] = int(runtime.total_seconds())
            except:
                proc['runtime_seconds'] = 0

        return processes

    def _enrich_window(self, proc: Dict, window_title: str) -> None:
        """
        Enrich a process entry with domain info and categorization from a browser window title.

        Args:
            proc: Process dictionary to enrich
            window_title: Browser window title to parse
        """
        proc['window_title'] = window_title
        
        # Extract domain from window title
        domain = WindowTitleParser.extract_domain_from_title(window_title)
        if domain:
            proc['domain'] = domain
            
            # Categorize the domain
            categorizer = get_website_categorizer()
            try:
                result = categorizer.batch_categorize_sync([domain])
                if domain in result:
                    category, confidence, source = result[domain]
                    proc['category'] = category
                    proc['domain_confidence'] = confidence
                    proc['categorization_source'] = source
            except:
                # Fallback to heuristic
                proc['category'] = CategoryEngine.categorize_activity(
                    domain=domain,
                    window_title=window_title
                )
                proc['domain_confidence'] = 0.5
                proc['categorization_source'] = 'heuristic'
        else:
            proc['category'] = CategoryEngine.categorize_activity(
                process_name=proc.get('name'),
                window_title=window_title
            )

    def get_process_stats(self, main_processes: List[Dict] = None) -> Dict:
        """
        Get aggregate statistics of main processes.
        Accepts pre-fetched processes to avoid double-scan.

        Args:
            main_processes: Optional pre-fetched process list.

        Returns:
            Statistics dictionary.
        """
        if main_processes is None:
            main_processes = self.get_main_processes()

        total_memory = sum(p.get('memory_mb', 0) for p in main_processes)
        total_cpu = sum(p.get('cpu_percent', 0) for p in main_processes)

        return {
            'total_processes': len(main_processes),
            'total_memory_mb': round(total_memory, 2),
            'total_cpu_percent': round(total_cpu, 2),
        }
