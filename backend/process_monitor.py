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

# Add parent directory to path to import from client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.category_engine import CategoryEngine
from client.window_parser import WindowTitleParser
from backend.website_categorizer import get_website_categorizer

logger = logging.getLogger(__name__)

# Thread pool for async categorization
_executor = ThreadPoolExecutor(max_workers=3)


class ProcessMonitor:
    """Monitor and filter system processes by resource usage."""

    # Thresholds for "main" processes
    MIN_MEMORY_MB = 100  # 100 MB minimum
    MIN_CPU_PERCENT = 1.0  # 1% CPU minimum

    # System processes to exclude
    EXCLUDED_PROCESSES = {
        "system", "svchost.exe", "lsass.exe", "csrss.exe",
        "wininit.exe", "services.exe", "lsm.exe", "dwm.exe",
        "searchindexer.exe", "windows.indexing.service",
        "ntoskrnl.exe", "idle", "registry", "smss.exe",
        "conhost.exe", "dllhost.exe", "rundll32.exe",
        "taskhostw.exe", "windowsupdate.exe"
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

        Returns:
            List of process dictionaries with full info.
        """
        processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    proc_info = proc.as_dict(attrs=['pid', 'name', 'memory_info', 'cpu_percent', 'username', 'create_time'])
                    
                    memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                    cpu_percent = proc_info['cpu_percent'] if proc_info['cpu_percent'] is not None else 0.0
                    
                    process_dict = {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'memory_mb': round(memory_mb, 2),
                        'memory_percent': 0,  # Will calculate below
                        'cpu_percent': round(cpu_percent, 2),
                        'username': proc_info['username'] if proc_info['username'] else 'System',
                        'create_time': proc_info['create_time'],
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
        
        # Expand browser processes to show each tab/window as separate entry
        expanded_processes = []
        browser_windows_seen = set()
        
        # Get all browser windows globally
        all_windows = WindowTitleParser.get_all_browser_windows()
        
        for proc in main_processes:
            if WindowTitleParser.is_browser_process(proc['name']):
                # Find all windows for this browser process
                proc_windows = [
                    title for pid, title in all_windows 
                    if pid == proc['pid'] and not WindowTitleParser.is_junk_window(title)
                ]
                
                if len(proc_windows) > 1:
                    # Multiple windows - create entry for each
                    for window_title in proc_windows:
                        if window_title not in browser_windows_seen:
                            browser_windows_seen.add(window_title)
                            tab_proc = proc.copy()
                            tab_proc['window_title'] = window_title
                            
                            # Extract domain and categorize
                            self._enrich_window(tab_proc, window_title)
                            expanded_processes.append(tab_proc)
                else:
                    # Single window or none - use original
                    expanded_processes.append(proc)
            else:
                # Non-browser process
                expanded_processes.append(proc)
        
        # Handle browser windows from processes not in main_processes
        # (this covers edge cases where a Chrome tab process is light but has visible windows)
        for pid, window_title in all_windows:
            if (not WindowTitleParser.is_junk_window(window_title) and 
                window_title not in browser_windows_seen):
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
                        'name': 'chrome.exe',
                        'memory_mb': 0,
                        'cpu_percent': 0,
                        'memory_percent': 0,
                        'username': 'User',
                        'create_time': datetime.now().timestamp(),
                        'window_title': window_title
                    }
                
                self._enrich_window(proc, window_title)
                expanded_processes.append(proc)

        # Sort by memory usage (descending)
        expanded_processes.sort(key=lambda x: x['memory_mb'], reverse=True)

        return expanded_processes

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

    def get_process_stats(self) -> Dict:
        """
        Get aggregate statistics of main processes.

        Returns:
            Statistics dictionary.
        """
        main_processes = self.get_main_processes()

        total_memory = sum(p['memory_mb'] for p in main_processes)
        total_cpu = sum(p['cpu_percent'] for p in main_processes)

        return {
            'total_processes': len(main_processes),
            'total_memory_mb': round(total_memory, 2),
            'total_cpu_percent': round(total_cpu, 2),
        }
