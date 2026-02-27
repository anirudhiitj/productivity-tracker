"""
Categorization engine that maps (ProcessName, Domain) → Activity Category.
Uses rule-based logic to classify activities as Productive, Educational, Entertainment, Gaming, or Neutral.
"""

import logging
from typing import Optional
from client.config import AppConfig

logger = logging.getLogger(__name__)


class CategoryEngine:
    """Maps processes and domains to activity categories."""

    CATEGORY_PRODUCTIVE = "Productive"
    CATEGORY_EDUCATIONAL = "Educational"
    CATEGORY_ENTERTAINMENT = "Entertainment"
    CATEGORY_GAMING = "Gaming"
    CATEGORY_NEUTRAL = "Neutral"

    VALID_CATEGORIES = [
        CATEGORY_PRODUCTIVE,
        CATEGORY_EDUCATIONAL,
        CATEGORY_ENTERTAINMENT,
        CATEGORY_GAMING,
        CATEGORY_NEUTRAL,
    ]

    @staticmethod
    def categorize_activity(
        process_name: Optional[str],
        domain: Optional[str],
        window_title: Optional[str] = None,
    ) -> str:
        """
        Categorize activity based on process name and domain.

        Domain takes precedence over process name for browser processes.
        Window title is used as a fallback for quick categorization.

        Args:
            process_name: Name of the active process (e.g., 'chrome.exe')
            domain: Extracted domain from window (e.g., 'github.com')
            window_title: Window title for fallback categorization

        Returns:
            Category string (one of VALID_CATEGORIES)
        """
        # Priority 1: Domain-based categorization (most specific)
        if domain:
            category = CategoryEngine._categorize_by_domain(domain)
            if category != CategoryEngine.CATEGORY_NEUTRAL:
                logger.debug(f"Categorized by domain '{domain}': {category}")
                return category

        # Priority 2: Process name categorization
        if process_name:
            category = CategoryEngine._categorize_by_process(process_name)
            if category != CategoryEngine.CATEGORY_NEUTRAL:
                logger.debug(f"Categorized by process '{process_name}': {category}")
                return category

        # Priority 3: Window title quick categorization (fallback)
        if window_title:
            category = CategoryEngine._quick_categorize_by_title(window_title)
            if category != CategoryEngine.CATEGORY_NEUTRAL:
                logger.debug(f"Categorized by title '{window_title}': {category}")
                return category

        logger.debug(
            f"No specific category for: {process_name}, {domain}, {window_title}"
        )
        return CategoryEngine.CATEGORY_NEUTRAL

    @staticmethod
    def _categorize_by_domain(domain: str) -> str:
        """
        Categorize based on domain name.

        Args:
            domain: Domain string or site name

        Returns:
            Category string
        """
        if not domain:
            return CategoryEngine.CATEGORY_NEUTRAL

        domain_lower = domain.lower()

        # Check productive domains
        if any(
            prod_domain in domain_lower
            for prod_domain in AppConfig.PRODUCTIVE_DOMAINS
        ):
            return CategoryEngine.CATEGORY_PRODUCTIVE

        # Check educational domains
        if any(
            edu_domain in domain_lower for edu_domain in AppConfig.EDUCATIONAL_DOMAINS
        ):
            return CategoryEngine.CATEGORY_EDUCATIONAL

        # Check entertainment domains
        if any(
            ent_domain in domain_lower
            for ent_domain in AppConfig.ENTERTAINMENT_DOMAINS
        ):
            return CategoryEngine.CATEGORY_ENTERTAINMENT

        # Check gaming domains
        if any(
            gam_domain in domain_lower for gam_domain in AppConfig.GAMING_DOMAINS
        ):
            return CategoryEngine.CATEGORY_GAMING

        return CategoryEngine.CATEGORY_NEUTRAL

    @staticmethod
    def _categorize_by_process(process_name: str) -> str:
        """
        Categorize based on executable process name.

        Args:
            process_name: Process name (e.g., 'chrome.exe')

        Returns:
            Category string
        """
        if not process_name:
            return CategoryEngine.CATEGORY_NEUTRAL

        process_lower = process_name.lower()

        # Check productive apps
        if any(
            app in process_lower for app in AppConfig.PRODUCTIVE_APPS
        ):
            return CategoryEngine.CATEGORY_PRODUCTIVE

        # Check gaming apps
        if any(app in process_lower for app in AppConfig.GAMING_APPS):
            return CategoryEngine.CATEGORY_GAMING

        # Check entertainment apps
        if any(app in process_lower for app in AppConfig.ENTERTAINMENT_APPS):
            return CategoryEngine.CATEGORY_ENTERTAINMENT

        return CategoryEngine.CATEGORY_NEUTRAL

    @staticmethod
    def _quick_categorize_by_title(title: str) -> str:
        """
        Quick categorization using keywords in window title.

        Args:
            title: Window title string

        Returns:
            Category string
        """
        if not title:
            return CategoryEngine.CATEGORY_NEUTRAL

        title_lower = title.lower()

        # Productive keywords
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
            "code",
            "develop",
        ]
        if any(keyword in title_lower for keyword in productive_keywords):
            return CategoryEngine.CATEGORY_PRODUCTIVE

        # Educational keywords
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
        if any(keyword in title_lower for keyword in educational_keywords):
            return CategoryEngine.CATEGORY_EDUCATIONAL

        # Entertainment keywords
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
        if any(keyword in title_lower for keyword in entertainment_keywords):
            return CategoryEngine.CATEGORY_ENTERTAINMENT

        # Gaming keywords
        gaming_keywords = [
            "steam",
            "epic games",
            "valorant",
            "minecraft",
            "fortnite",
            "roblox",
            "game",
            "gaming",
        ]
        if any(keyword in title_lower for keyword in gaming_keywords):
            return CategoryEngine.CATEGORY_GAMING

        return CategoryEngine.CATEGORY_NEUTRAL

    @staticmethod
    def get_category_weight(category: str) -> float:
        """
        Get the gamification weight for a category.

        Args:
            category: Category string

        Returns:
            Weight value for scoring.
        """
        return AppConfig.get_category_weight(category)

    @staticmethod
    def is_valid_category(category: str) -> bool:
        """
        Check if a category is valid.

        Args:
            category: Category string to validate

        Returns:
            True if valid, False otherwise.
        """
        return category in CategoryEngine.VALID_CATEGORIES
