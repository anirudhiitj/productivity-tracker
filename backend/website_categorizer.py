import json
import asyncio
import re
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging

from backend.gemini_categorizer import get_gemini_categorizer
from backend.website_cache import get_website_cache

logger = logging.getLogger(__name__)


class WebsiteCategorizer:
    """
    Three-tier website categorization system:
    1. Local Dictionary (instant, 100% reliable)
    2. Gemini API (intelligent, ~1-2s latency)
    3. Heuristic Fallback (instant, pattern-based)
    
    Returns (category, confidence, source) tuple.
    """
    
    # Heuristic patterns for fallback categorization
    KEYWORD_PATTERNS = {
        "Productive": [
            r"(github|gitlab|bitbucket)",
            r"(jira|asana|trello|monday)",
            r"(slack|teams|discord.*work|notion)",
            r"(drive\.google|docs\.google|office\.com|sharepoint)",
            r"(stack.*overflow|github.*code|coding.*help)",
            r"(jenkins|gitlab.*ci|github.*actions)",
            r"(aws|azure|gcp|devops|docker|kubernetes)",
            r"(localhost|127\.0\.0\.1|0\.0\.0\.0)",
            r"mail\.|email",
        ],
        "Gaming": [
            r"(steam|epic.*games|roblox|minecraft)",
            r"(twitch|youtube.*gaming|gaming.*channel)",
            r"(cod|call.*duty|fortnite|leagueof)",
            r"(playstation|xbox|nintendo)",
            r"game\.|games\.",
        ],
        "Educational": [
            r"(udemy|coursera|edx|skillshare|datacamp)",
            r"(leetcode|codeforces|hackerrank)",
            r"(khan.*academy|coursera|linkedin.*learning)",
            r"(w3schools|mdn|developer\.mozilla)",
            r"(github\.io.*blog|medium\.com.*tech)",
            r"tutorial\.|learn\.|course\.",
        ],
        "Entertainment": [
            r"(netflix|hulu|disney|amazon.*prime)",
            r"(youtube(?!.*tutorial)(?!.*learn)|youtu\.be)",
            r"(instagram|tiktok|snapchat)",
            r"(reddit|twitter|facebook)",
            r"(twitch(?!.*dev)(?!.*code)|streamers\.)",
            r"(spotify|soundcloud|apple.*music)",
            r"social\.",
        ],
    }
    
    def __init__(self):
        """Initialize categorizer and load dictionary."""
        self.dictionary = self._load_dictionary()
        self.cache = get_website_cache()
        self.gemini = get_gemini_categorizer()
        logger.info(f"✅ WebsiteCategorizer initialized with {len(self.dictionary)} known domains")
    
    def _load_dictionary(self) -> Dict[str, Dict]:
        """Load website dictionary from JSON file."""
        dict_path = Path(__file__).parent.parent / "data" / "website_dictionary.json"
        
        if not dict_path.exists():
            logger.warning(f"Website dictionary not found at {dict_path}")
            return {}
        
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading website dictionary: {e}")
            return {}
    
    def extract_domain(self, window_title: str) -> Optional[str]:
        """
        Extract domain from window title.
        Handles various formats:
        - "GitHub - user/repo" → "github.com"
        - "Slack | Team" → "slack.com"
        - "https://example.com - Search" → "example.com"
        - etc.
        
        Args:
            window_title: Window title string from browser
            
        Returns:
            Normalized domain or None
        """
        if not window_title:
            return None
        
        # Try direct URL matching
        url_match = re.search(
            r'(?:https?://)?(?:www\.)?([a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.(?:[a-zA-Z]{2,})+)',
            window_title
        )
        if url_match:
            return url_match.group(1).lower()
        
        # Extract domain from title separators (| or -)
        parts = re.split(r'[|-]', window_title)
        if len(parts) > 1:
            potential_domain = parts[-1].strip()
            # Simple heuristic: if it looks like a domain, return it
            if "." in potential_domain and len(potential_domain) > 3:
                return potential_domain.lower()
        
        return None
    
    async def categorize(self, domain: str, window_title: str = "") -> Tuple[str, float, str]:
        """
        Categorize a website using three-tier system.
        
        Args:
            domain: Website domain (e.g., "github.com")
            window_title: Full browser window title (for context)
            
        Returns:
            Tuple of (category, confidence, source)
            - source: "dictionary", "cache", "gemini", or "heuristic"
        """
        if not domain:
            return "Neutral", 0.0, "error"
        
        domain = domain.lower().strip()
        
        # TIER 1: Check local cache (fast, reliable)
        cached = self.cache.get(domain)
        if cached:
            return cached[0], cached[1], "cache"
        
        # TIER 2: Check dictionary (instant, 100% accurate)
        if domain in self.dictionary:
            entry = self.dictionary[domain]
            result = (entry["category"], entry["confidence"], "dictionary")
            # Also cache it
            self.cache.set(domain, entry["category"], entry["confidence"], "dictionary")
            return result
        
        # TIER 3a: Try Gemini API (intelligent but slower)
        if self.gemini.is_available():
            category, confidence = await self.gemini.categorize_website(domain, window_title)
            if confidence > 0:
                # Cache the result
                self.cache.set(domain, category, confidence, "gemini")
                return category, confidence, "gemini"
        
        # TIER 3b: Fallback to heuristics (instant pattern-based)
        category, confidence = self._categorize_by_heuristics(domain, window_title)
        self.cache.set(domain, category, confidence, "heuristic")
        return category, confidence, "heuristic"
    
    def _categorize_by_heuristics(self, domain: str, window_title: str) -> Tuple[str, float]:
        """
        Fast heuristic-based categorization using keyword patterns.
        
        Args:
            domain: Website domain
            window_title: Browser window title
            
        Returns:
            Tuple of (category, confidence)
        """
        search_text = f"{domain} {window_title}".lower()
        
        best_category = "Neutral"
        best_confidence = 0.5
        
        for category, patterns in self.KEYWORD_PATTERNS.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, search_text):
                        # Match found, assign confidence based on pattern specificity
                        confidence = 0.75  # Base heuristic confidence
                        
                        # Higher confidence for specific patterns
                        if len(pattern) > 20:
                            confidence = 0.85
                        if len(pattern) > 30:
                            confidence = 0.9
                        
                        if confidence > best_confidence:
                            best_category = category
                            best_confidence = confidence
                        break
                except re.error:
                    continue
        
        return best_category, best_confidence
    
    def batch_categorize_sync(self, domains: list) -> Dict[str, Tuple[str, float, str]]:
        """
        Synchronous batch categorization (good for initialization).
        
        Args:
            domains: List of domains to categorize
            
        Returns:
            Dict of {domain: (category, confidence, source)}
        """
        results = {}
        for domain in domains:
            # Try cache first
            cached = self.cache.get(domain)
            if cached:
                results[domain] = cached
                continue
            
            # Try dictionary
            if domain in self.dictionary:
                entry = self.dictionary[domain]
                results[domain] = (entry["category"], entry["confidence"], "dictionary")
                continue
            
            # Fallback to heuristics
            category, confidence = self._categorize_by_heuristics(domain, "")
            results[domain] = (category, confidence, "heuristic")
        
        return results


# Global instance
_categorizer_instance: Optional['WebsiteCategorizer'] = None


def get_website_categorizer() -> WebsiteCategorizer:
    """Get or create the global website categorizer instance."""
    global _categorizer_instance
    if _categorizer_instance is None:
        _categorizer_instance = WebsiteCategorizer()
    return _categorizer_instance
