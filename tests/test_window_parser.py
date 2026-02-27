"""
Unit tests for window_parser module.
Tests domain extraction and window title parsing logic.
"""

import pytest
from client.window_parser import WindowTitleParser


class TestWindowTitleParser:
    """Test cases for WindowTitleParser."""

    def test_browser_detection(self):
        """Test browser process detection."""
        assert WindowTitleParser.is_browser_process("chrome.exe")
        assert WindowTitleParser.is_browser_process("firefox.exe")
        assert WindowTitleParser.is_browser_process("msedge.exe")
        assert not WindowTitleParser.is_browser_process("vscode.exe")
        assert not WindowTitleParser.is_browser_process("code.exe")
        assert not WindowTitleParser.is_browser_process(None)

    def test_extract_domain_from_title_dash_format(self):
        """Test extraction with dash separator."""
        result = WindowTitleParser.extract_domain_from_title(
            "LeetCode - Google Chrome"
        )
        assert result == "leetcode"

    def test_extract_domain_from_title_bracketed(self):
        """Test extraction with bracketed format."""
        result = WindowTitleParser.extract_domain_from_title("[GitHub] Pull Requests")
        assert result == "github"

    def test_extract_domain_from_title_pipe_format(self):
        """Test extraction with pipe separator."""
        result = WindowTitleParser.extract_domain_from_title(
            "Stack Overflow | Questions"
        )
        assert result == "stack"

    def test_extract_domain_from_title_gmail(self):
        """Test extraction with Gmail format."""
        result = WindowTitleParser.extract_domain_from_title(
            "Gmail - Sign in - Mozilla Firefox"
        )
        assert result == "gmail"

    def test_extract_domain_from_title_wikipedia(self):
        """Test extraction with Wikipedia format."""
        result = WindowTitleParser.extract_domain_from_title(
            "Wikipedia, the free encyclopedia"
        )
        # Should handle comma separator
        assert "wikipedia" in result.lower() or "wikipedia" == result

    def test_normalize_domain_clean(self):
        """Test domain normalization."""
        assert WindowTitleParser.normalize_domain("GitHub") == "github"
        assert (
            WindowTitleParser.normalize_domain("Stack Overflow")
            == "stack overflow"
        )

    def test_normalize_domain_remove_chars(self):
        """Test domain normalization with special characters."""
        result = WindowTitleParser.normalize_domain("Test@Domain#123")
        assert "@" not in result
        assert "#" not in result

    def test_normalize_domain_empty(self):
        """Test normalization of empty domain."""
        assert WindowTitleParser.normalize_domain("") is None
        assert WindowTitleParser.normalize_domain(None) is None

    def test_extract_full_domain_url(self):
        """Test full URL extraction."""
        result = WindowTitleParser.extract_full_domain_url(
            "GitHub - www.github.com/user/repo"
        )
        assert result == "github.com"

    def test_categorize_window_title_productive(self):
        """Test categorization of productive titles."""
        assert (
            WindowTitleParser.categorize_window_title("GitHub - Google Chrome")
            == "Productive"
        )
        assert (
            WindowTitleParser.categorize_window_title("[JIRA] PROJ-123")
            == "Productive"
        )

    def test_categorize_window_title_entertainment(self):
        """Test categorization of entertainment titles."""
        assert (
            WindowTitleParser.categorize_window_title("YouTube - Watch Videos")
            == "Entertainment"
        )
        assert (
            WindowTitleParser.categorize_window_title("Netflix - Streaming")
            == "Entertainment"
        )

    def test_categorize_window_title_gaming(self):
        """Test categorization of gaming titles."""
        assert (
            WindowTitleParser.categorize_window_title("Steam Game Store")
            == "Gaming"
        )
        assert (
            WindowTitleParser.categorize_window_title("Valorant - Play", )
            == "Gaming"
        )

    def test_categorize_window_title_neutral(self):
        """Test categorization of neutral titles."""
        assert WindowTitleParser.categorize_window_title("Random Window") == "Neutral"
        assert WindowTitleParser.categorize_window_title("") == "Neutral"


class TestWindowTitleExtraction:
    """Test edge cases for window title extraction."""

    def test_very_long_title(self):
        """Test handling of very long window titles."""
        long_title = "A" * 500
        result = WindowTitleParser.normalize_domain(long_title)
        assert len(result) <= 100  # Should be truncated

    def test_unicode_title(self):
        """Test handling of unicode characters."""
        result = WindowTitleParser.extract_domain_from_title("GitHub — 你好 — Firefox")
        assert result is not None

    def test_empty_title(self):
        """Test handling of empty title."""
        assert WindowTitleParser.extract_domain_from_title("") is None
        assert WindowTitleParser.extract_domain_from_title("   ") is None
