import os
import asyncio
import json
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not installed. Install with: pip install google-generativeai")


class GeminiCategorizer:
    """
    Uses Google's Gemini AI to intelligently categorize websites.
    Falls back gracefully if API key is not configured.
    """
    
    CATEGORIES = ["Productive", "Gaming", "Educational", "Entertainment", "Neutral"]
    
    def __init__(self):
        """Initialize Gemini categorizer with API key from environment."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.initialized = False
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-pro")
                self.initialized = True
                logger.info("✅ Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}")
                self.initialized = False
        elif not GEMINI_AVAILABLE:
            logger.info("⚠️  Gemini API package not installed. Website categorization will use heuristics only.")
        else:
            logger.info("⚠️  GEMINI_API_KEY not set. Website categorization will use heuristics only.")
    
    async def categorize_website(self, domain: str, window_title: str) -> Tuple[str, float]:
        """
        Use Gemini AI to categorize a website.
        Returns (category, confidence) tuple.
        
        Args:
            domain: Website domain (e.g., "github.com")
            window_title: Full window title from browser
            
        Returns:
            Tuple of (category, confidence_score)
        """
        if not self.initialized:
            return "Neutral", 0.0
        
        try:
            prompt = f"""You are an expert at categorizing websites. Given a domain and window title, categorize it into ONE of these categories:
- Productive: Work tools, development, documentation, productivity apps
- Gaming: Games, gaming platforms, gaming content
- Educational: Learning resources, courses, tutorials, documentation
- Entertainment: Social media, video streaming, music, entertainment
- Neutral: General utilities, search engines, news

Domain: {domain}
Window Title: {window_title}

Respond in this EXACT format (one line only):
CATEGORY: <category> | CONFIDENCE: <0.0-1.0>

Examples:
CATEGORY: Educational | CONFIDENCE: 0.95
CATEGORY: Gaming | CONFIDENCE: 0.85
CATEGORY: Neutral | CONFIDENCE: 0.5
"""
            
            # Run in thread pool to avoid blocking
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=50,
                    temperature=0.3,  # Low temperature for consistent results
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract category and confidence
            if "CATEGORY:" in response_text and "CONFIDENCE:" in response_text:
                parts = response_text.split("|")
                category_part = parts[0].split(":")[-1].strip()
                confidence_part = float(parts[1].split(":")[-1].strip())
                
                # Validate category
                if category_part in self.CATEGORIES:
                    logger.info(f"✅ Gemini categorized {domain} → {category_part} ({confidence_part})")
                    return category_part, confidence_part
            
            logger.warning(f"Invalid Gemini response format: {response_text}")
            return "Neutral", 0.0
            
        except Exception as e:
            logger.error(f"Error calling Gemini API for {domain}: {e}")
            return "Neutral", 0.0
    
    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        return self.initialized


# Global instance
_gemini_instance: Optional[GeminiCategorizer] = None


def get_gemini_categorizer() -> GeminiCategorizer:
    """Get or create the global Gemini categorizer instance."""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiCategorizer()
    return _gemini_instance
