import sqlite3
import json
import os
from typing import Optional, Tuple, Dict
from pathlib import Path
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WebsiteCacheDB:
    """
    SQLite-based cache for website categorizations.
    Stores domain → (category, confidence, timestamp) mappings.
    """
    
    DB_PATH = Path(__file__).parent.parent / "data" / "website_cache.db"
    
    def __init__(self):
        """Initialize database and create table if needed."""
        # Ensure data directory exists
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.DB_PATH), check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()
    
    def _create_table(self):
        """Create website_cache table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS website_cache (
                domain TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                confidence REAL NOT NULL,
                source TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def get(self, domain: str) -> Optional[Tuple[str, float, str]]:
        """
        Get cached categorization for a domain.
        
        Args:
            domain: Website domain
            
        Returns:
            Tuple of (category, confidence, source) or None if not cached
        """
        try:
            self.cursor.execute(
                "SELECT category, confidence, source FROM website_cache WHERE domain = ?",
                (domain,)
            )
            result = self.cursor.fetchone()
            if result:
                logger.debug(f"Cache hit for {domain}: {result[0]} ({result[1]})")
                return result
            return None
        except Exception as e:
            logger.error(f"Error retrieving cache for {domain}: {e}")
            return None
    
    def set(self, domain: str, category: str, confidence: float, source: str = "gemini"):
        """
        Cache a website categorization.
        
        Args:
            domain: Website domain
            category: Assigned category
            confidence: Confidence score (0.0-1.0)
            source: Source of categorization (manual, gemini, heuristic, dictionary)
        """
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO website_cache 
                (domain, category, confidence, source, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (domain, category, confidence, source))
            self.conn.commit()
            logger.debug(f"Cached {domain} → {category}")
        except Exception as e:
            logger.error(f"Error caching {domain}: {e}")
    
    def batch_set(self, items: Dict[str, Tuple[str, float, str]]):
        """
        Bulk insert multiple categorizations.
        
        Args:
            items: Dict of {domain: (category, confidence, source)}
        """
        try:
            items_list = [
                (domain, cat_conf[0], cat_conf[1], cat_conf[2])
                for domain, cat_conf in items.items()
            ]
            self.cursor.executemany("""
                INSERT OR REPLACE INTO website_cache 
                (domain, category, confidence, source, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, items_list)
            self.conn.commit()
            logger.info(f"Batch cached {len(items)} websites")
        except Exception as e:
            logger.error(f"Error batch caching: {e}")
    
    def clear_old_entries(self, days: int = 30):
        """Remove cache entries older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            self.cursor.execute(
                "DELETE FROM website_cache WHERE updated_at < ? AND source = 'gemini'",
                (cutoff_date,)
            )
            deleted = self.cursor.rowcount
            self.conn.commit()
            logger.info(f"Cleared {deleted} old cache entries")
        except Exception as e:
            logger.error(f"Error clearing old entries: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM website_cache")
            total = self.cursor.fetchone()[0]
            
            self.cursor.execute(
                "SELECT source, COUNT(*) FROM website_cache GROUP BY source"
            )
            by_source = dict(self.cursor.fetchall())
            
            return {
                "total_cached": total,
                "by_source": by_source
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.close()


# Global instance
_cache_instance: Optional[WebsiteCacheDB] = None


def get_website_cache() -> WebsiteCacheDB:
    """Get or create the global website cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = WebsiteCacheDB()
    return _cache_instance
