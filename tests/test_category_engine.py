"""
Unit tests for category_engine module.
Tests activity categorization logic.
"""

import pytest
from client.category_engine import CategoryEngine


class TestCategoryEngine:
    """Test cases for CategoryEngine."""

    def test_categorize_by_productive_domain(self):
        """Test categorization of productive domains."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="chrome.exe",
                domain="github.com",
            )
            == "Productive"
        )
        assert (
            CategoryEngine.categorize_activity(
                process_name="firefox.exe",
                domain="stackoverflow.com",
            )
            == "Productive"
        )

    def test_categorize_by_productive_process(self):
        """Test categorization of productive processes."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="code.exe",
                domain=None,
            )
            == "Productive"
        )
        assert (
            CategoryEngine.categorize_activity(
                process_name="devenv.exe",
                domain=None,
            )
            == "Productive"
        )

    def test_categorize_by_gaming_process(self):
        """Test categorization of gaming processes."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="steam.exe",
                domain=None,
            )
            == "Gaming"
        )
        assert (
            CategoryEngine.categorize_activity(
                process_name="valorant.exe",
                domain=None,
            )
            == "Gaming"
        )

    def test_categorize_by_entertainment_domain(self):
        """Test categorization of entertainment domains."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="chrome.exe",
                domain="youtube.com",
            )
            == "Entertainment"
        )
        assert (
            CategoryEngine.categorize_activity(
                process_name="firefox.exe",
                domain="netflix.com",
            )
            == "Entertainment"
        )

    def test_categorize_by_educational_domain(self):
        """Test categorization of educational domains."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="chrome.exe",
                domain="udemy.com",
            )
            == "Educational"
        )

    def test_domain_takes_precedence(self):
        """Test that domain takes precedence over process name."""
        # Gaming process but educational domain should be Educational
        assert (
            CategoryEngine.categorize_activity(
                process_name="steam.exe",
                domain="coursera.org",
            )
            == "Educational"
        )

    def test_categorize_neutral(self):
        """Test categorization of neutral items."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="notepad.exe",
                domain=None,
            )
            == "Neutral"
        )
        assert (
            CategoryEngine.categorize_activity(
                process_name="explorer.exe",
                domain="example.com",
            )
            == "Neutral"
        )

    def test_categorize_with_window_title_fallback(self):
        """Test fallback categorization using window title."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="unknown.exe",
                domain=None,
                window_title="YouTube - Watch Videos",
            )
            == "Entertainment"
        )

    def test_none_inputs(self):
        """Test handling of None inputs."""
        assert (
            CategoryEngine.categorize_activity(
                process_name=None,
                domain=None,
            )
            == "Neutral"
        )

    def test_empty_string_inputs(self):
        """Test handling of empty string inputs."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="",
                domain="",
            )
            == "Neutral"
        )

    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="CHROME.EXE",
                domain="GITHUB.COM",
            )
            == "Productive"
        )
        assert (
            CategoryEngine.categorize_activity(
                process_name="CODE.EXE",
                domain=None,
            )
            == "Productive"
        )

    def test_get_category_weight(self):
        """Test category weight retrieval."""
        assert CategoryEngine.get_category_weight("Productive") > 0
        assert CategoryEngine.get_category_weight("Neutral") > 0
        assert CategoryEngine.get_category_weight("Gaming") < 0
        assert CategoryEngine.get_category_weight("Entertainment") < 0

    def test_is_valid_category(self):
        """Test category validation."""
        assert CategoryEngine.is_valid_category("Productive")
        assert CategoryEngine.is_valid_category("Educational")
        assert CategoryEngine.is_valid_category("Entertainment")
        assert CategoryEngine.is_valid_category("Gaming")
        assert CategoryEngine.is_valid_category("Neutral")
        assert not CategoryEngine.is_valid_category("Invalid")
        assert not CategoryEngine.is_valid_category("")


class TestCategoryEdgeCases:
    """Test edge cases for categorization."""

    def test_partial_domain_match(self):
        """Test that partial domain matches work."""
        # Should match "github" in "github.com"
        assert (
            CategoryEngine.categorize_activity(
                process_name="chrome.exe",
                domain="github",
            )
            == "Productive"
        )

    def test_subdomain_matching(self):
        """Test matching with subdomains."""
        assert (
            CategoryEngine.categorize_activity(
                process_name="chrome.exe",
                domain="api.github.com",
            )
            == "Productive"
        )

    def test_special_characters_in_domain(self):
        """Test handling of special characters in domain."""
        # Should still match github
        assert (
            CategoryEngine.categorize_activity(
                process_name="chrome.exe",
                domain="github-enterprise.com",
            )
            == "Productive"
        )
