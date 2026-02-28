"""
Chrome Tab Monitor using DevTools Protocol
Gets ALL Chrome tabs including background tabs
"""
import requests
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ChromeTabMonitor:
    """Monitor ALL Chrome tabs using Chrome DevTools Protocol"""
    
    def __init__(self, debug_port: int = 9222):
        """
        Initialize Chrome tab monitor.
        
        Args:
            debug_port: Chrome DevTools Protocol port (default: 9222)
        """
        self.debug_port = debug_port
        self.base_url = f"http://localhost:{debug_port}"
        self._available = None
        self._available_checked_at = 0  # timestamp of last check
        self._check_interval = 30  # re-check every 30 seconds
    
    def is_available(self) -> bool:
        """Check if Chrome DevTools Protocol is available (with TTL cache)"""
        import time
        now = time.time()
        
        # Use cached value if within TTL
        if self._available is not None and (now - self._available_checked_at) < self._check_interval:
            return self._available
        
        try:
            response = requests.get(f"{self.base_url}/json/version", timeout=0.5)
            self._available = response.status_code == 200
        except Exception:
            self._available = False
        
        self._available_checked_at = now
        return self._available
    
    def get_all_tabs(self) -> List[Dict]:
        """
        Get all Chrome tabs (including background tabs).
        
        Returns:
            List of tab dictionaries with title, url, domain, type
        """
        if not self.is_available():
            logger.debug("Chrome DevTools Protocol not available")
            return []
        
        try:
            response = requests.get(f"{self.base_url}/json", timeout=2)
            tabs = response.json()
            
            # Filter and enrich tab data
            processed_tabs = []
            for tab in tabs:
                # Skip non-page tabs (extensions, devtools, etc.)
                if tab.get('type') != 'page':
                    continue
                
                url = tab.get('url', '')
                title = tab.get('title', 'Untitled')
                
                # Skip Chrome internal pages
                if url.startswith('chrome://') or url.startswith('chrome-extension://'):
                    continue
                
                # Extract domain
                domain = self._extract_domain(url)
                
                processed_tabs.append({
                    'title': title,
                    'url': url,
                    'domain': domain,
                    'id': tab.get('id'),
                    'type': tab.get('type'),
                })
            
            logger.info(f"Found {len(processed_tabs)} Chrome tabs via DevTools")
            return processed_tabs
        
        except Exception as e:
            logger.error(f"Error getting Chrome tabs: {e}")
            return []
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Remove www. and port
            domain = domain.split(':')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Get main domain (e.g., google.com from docs.google.com)
            parts = domain.split('.')
            if len(parts) > 2:
                domain = '.'.join(parts[-2:])
            
            return domain if domain else None
        except:
            return None
    
    @staticmethod
    def get_chrome_launch_command() -> str:
        """Get command to launch Chrome with DevTools enabled"""
        return 'chrome.exe --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\\Google\\Chrome\\User Data"'


# Global instance
_chrome_monitor = None

def get_chrome_tab_monitor() -> ChromeTabMonitor:
    """Get global Chrome tab monitor instance"""
    global _chrome_monitor
    if _chrome_monitor is None:
        _chrome_monitor = ChromeTabMonitor()
    return _chrome_monitor
