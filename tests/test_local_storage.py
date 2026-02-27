"""
Unit tests for local_storage module.
Tests encrypted database operations and key management.
"""

import pytest
import os
from datetime import datetime, timedelta
from client.local_storage import EncryptedStorage, CredentialManager


class TestCredentialManager:
    """Test cases for CredentialManager."""

    @pytest.mark.skip(reason="Requires Windows Credential Manager - manual test")
    def test_store_and_retrieve_key(self):
        """Test storing and retrieving encryption key."""
        test_key = b"test_key_12345"
        app_name = "test_app"

        # Store
        assert CredentialManager.store_key(app_name, test_key)

        # Retrieve
        retrieved_key = CredentialManager.retrieve_key(app_name)
        assert retrieved_key == test_key

        # Cleanup
        CredentialManager.delete_key(app_name)

    def test_retrieve_nonexistent_key(self):
        """Test retrieving non-existent key returns None."""
        result = CredentialManager.retrieve_key("nonexistent_app_xyz")
        assert result is None


class TestEncryptedStorage:
    """Test cases for EncryptedStorage."""

    def test_initialization(self, temp_db_path):
        """Test storage initialization."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")
        assert os.path.exists(temp_db_path)
        assert storage.encryption_key is not None
        storage.close()

    def test_insert_activity_log(self, temp_db_path, sample_activity_log):
        """Test inserting an activity log."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        log_id = storage.insert_activity_log(
            timestamp=sample_activity_log["timestamp"],
            process_name=sample_activity_log["process_name"],
            window_title=sample_activity_log["window_title"],
            domain=sample_activity_log["domain"],
            category=sample_activity_log["category"],
            duration_seconds=sample_activity_log["duration_seconds"],
        )

        assert log_id is not None
        assert len(log_id) > 0
        storage.close()

    def test_get_pending_logs(self, temp_db_path, sample_activity_log):
        """Test retrieving pending logs."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        # Insert test logs
        for i in range(3):
            storage.insert_activity_log(
                timestamp=f"2026-02-27T10:3{i}:45",
                process_name=sample_activity_log["process_name"],
                window_title=sample_activity_log["window_title"],
                domain=sample_activity_log["domain"],
                category=sample_activity_log["category"],
                duration_seconds=sample_activity_log["duration_seconds"],
            )

        # Get pending
        pending = storage.get_pending_logs()
        assert len(pending) >= 3
        storage.close()

    def test_mark_synced(self, temp_db_path, sample_activity_log):
        """Test marking logs as synced."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        # Insert test log
        log_id = storage.insert_activity_log(
            timestamp=sample_activity_log["timestamp"],
            process_name=sample_activity_log["process_name"],
            window_title=sample_activity_log["window_title"],
            domain=sample_activity_log["domain"],
            category=sample_activity_log["category"],
            duration_seconds=sample_activity_log["duration_seconds"],
        )

        # Mark as synced
        assert storage.mark_synced([log_id])

        # Verify
        pending = storage.get_pending_logs()
        assert log_id not in [log["log_id"] for log in pending]
        storage.close()

    def test_cleanup_old_logs(self, temp_db_path, sample_activity_log):
        """Test cleaning up old logs."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        # Insert old log
        old_timestamp = (datetime.now() - timedelta(days=40)).isoformat()
        log_id = storage.insert_activity_log(
            timestamp=old_timestamp,
            process_name=sample_activity_log["process_name"],
            window_title=sample_activity_log["window_title"],
            domain=sample_activity_log["domain"],
            category=sample_activity_log["category"],
            duration_seconds=sample_activity_log["duration_seconds"],
        )

        # Mark as synced first
        storage.mark_synced([log_id])

        # Cleanup
        deleted = storage.cleanup_old_logs(days=30)
        assert deleted >= 1

        storage.close()

    def test_get_statistics(self, temp_db_path, sample_activity_log):
        """Test getting storage statistics."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        # Insert test logs
        for i in range(5):
            storage.insert_activity_log(
                timestamp=f"2026-02-27T10:{i:02d}:45",
                process_name=sample_activity_log["process_name"],
                window_title=sample_activity_log["window_title"],
                domain=sample_activity_log["domain"],
                category=sample_activity_log["category"],
                duration_seconds=sample_activity_log["duration_seconds"],
            )

        stats = storage.get_statistics()
        assert "total_logs" in stats
        assert "pending_logs" in stats
        assert "unique_processes" in stats
        assert stats["total_logs"] >= 5

        storage.close()

    def test_duplicate_prevention(self, temp_db_path, sample_activity_log):
        """Test that duplicate entries are prevented."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        # Insert same log twice
        log_id1 = storage.insert_activity_log(
            timestamp=sample_activity_log["timestamp"],
            process_name=sample_activity_log["process_name"],
            window_title=sample_activity_log["window_title"],
            domain=sample_activity_log["domain"],
            category=sample_activity_log["category"],
            duration_seconds=sample_activity_log["duration_seconds"],
        )

        log_id2 = storage.insert_activity_log(
            timestamp=sample_activity_log["timestamp"],
            process_name=sample_activity_log["process_name"],
            window_title=sample_activity_log["window_title"],
            domain=sample_activity_log["domain"],
            category=sample_activity_log["category"],
            duration_seconds=sample_activity_log["duration_seconds"],
        )

        # Second insert should be ignored
        assert log_id1 is not None
        assert log_id2 is None

        storage.close()

    def test_export_pending_logs(self, temp_db_path, sample_activity_log):
        """Test exporting pending logs as encrypted payload."""
        storage = EncryptedStorage(db_path=temp_db_path, app_name="test_storage")

        # Insert test log
        storage.insert_activity_log(
            timestamp=sample_activity_log["timestamp"],
            process_name=sample_activity_log["process_name"],
            window_title=sample_activity_log["window_title"],
            domain=sample_activity_log["domain"],
            category=sample_activity_log["category"],
            duration_seconds=sample_activity_log["duration_seconds"],
        )

        # Export
        payload = storage.export_pending_logs()
        assert payload is not None
        assert isinstance(payload, str)
        assert len(payload) > 0

        storage.close()
