"""
Configuration constants for the productivity tracking system.
"""

from typing import Dict


class AppConfig:
    """Central configuration for the agent."""

    # Polling and aggregation settings
    POLLING_INTERVAL_MS = 1000  # Poll every 1 second
    AGGREGATION_WINDOW_MIN = 5  # Aggregate every 5 minutes
    SYNC_THRESHOLD_LOGS = 100  # Upload when 100+ logs pending
    SYNC_THRESHOLD_MINUTES = 5  # Or after 5 minutes
    RETENTION_DAYS = 30  # Keep logs for 30 days locally

    # Database configuration
    DB_NAME = "activity_logs.db"
    DB_ENCRYPTION_KEY_ID = "productivity_tracker_encryption_key"
    DB_PATH = "./data/"

    # Gamification weights (for future scoring)
    CATEGORY_WEIGHTS: Dict[str, float] = {
        "Productive": 3.0,
        "Educational": 2.5,
        "Neutral": 1.0,
        "Entertainment": -1.0,
        "Gaming": -2.0,
    }

    # Application categorization mappings
    PRODUCTIVE_APPS = [
        "code.exe",
        "devenv.exe",
        "pycharm64.exe",
        "notepad++.exe",
        "explorer.exe",
        "cmd.exe",
        "powershell.exe",
        "git.exe",
        "python.exe",
    ]

    GAMING_APPS = [
        "steam.exe",
        "valorant.exe",
        "csgo.exe",
        "fortnite.exe",
        "minecraft.exe",
    ]

    ENTERTAINMENT_APPS = [
        "vlc.exe",
        "spotify.exe",
        "discord.exe",
        "7zFM.exe",
    ]

    # Domain categorization
    PRODUCTIVE_DOMAINS = [
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "stackoverflow.com",
        "github.dev",
        "jira.atlassian.net",
        "notion.so",
        "drive.google.com",
        "docs.google.com",
        "sheets.google.com",
        "office.com",
        "slack.com",
    ]

    EDUCATIONAL_DOMAINS = [
        "udemy.com",
        "coursera.org",
        "khan academy.com",
        "edx.org",
        "skillshare.com",
        "datacamp.com",
        "pluralsight.com",
        "wikipedia.org",
    ]

    ENTERTAINMENT_DOMAINS = [
        "youtube.com",
        "netflix.com",
        "hulu.com",
        "twitch.tv",
        "instagram.com",
        "tiktok.com",
        "twitter.com",
        "reddit.com",
        "9gag.com",
    ]

    GAMING_DOMAINS = [
        "steampowered.com",
        "epicgames.com",
        "riotgames.com",
        "minecraft.net",
        "fortnite.com",
    ]

    # Browser process names
    BROWSER_PROCESSES = [
        "chrome.exe",
        "firefox.exe",
        "msedge.exe",
        "opera.exe",
        "brave.exe",
    ]

    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "agent.log"

    @classmethod
    def get_category_weight(cls, category: str) -> float:
        """Get weight for a category."""
        return cls.CATEGORY_WEIGHTS.get(category, 0.0)

    @classmethod
    def is_productive_domain(cls, domain: str) -> bool:
        """Check if domain is productive."""
        return any(prod in domain.lower() for prod in cls.PRODUCTIVE_DOMAINS)

    @classmethod
    def is_educational_domain(cls, domain: str) -> bool:
        """Check if domain is educational."""
        return any(edu in domain.lower() for edu in cls.EDUCATIONAL_DOMAINS)

    @classmethod
    def is_entertainment_domain(cls, domain: str) -> bool:
        """Check if domain is entertainment."""
        return any(ent in domain.lower() for ent in cls.ENTERTAINMENT_DOMAINS)

    @classmethod
    def is_gaming_domain(cls, domain: str) -> bool:
        """Check if domain is gaming."""
        return any(gam in domain.lower() for gam in cls.GAMING_DOMAINS)
