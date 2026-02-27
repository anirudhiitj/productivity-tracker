"""
Secure local storage using encrypted SQLite database.
Encryption key is stored in Windows Credential Manager.
"""

import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import win32cred
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import pywintypes

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages encryption keys in Windows Credential Manager."""

    @staticmethod
    def store_key(app_name: str, key: bytes) -> bool:
        """
        Store encryption key in Windows Credential Manager.

        Args:
            app_name: Application name for credential target
            key: Encryption key bytes

        Returns:
            True if successful, False otherwise.
        """
        try:
            target = f"{app_name}_encryption_key"
            win32cred.CredWrite(
                {
                    "TargetName": target,
                    "UserName": "local_service",
                    "CredentialBlob": key,
                    "CredentialBlobSize": len(key),
                    "Type": win32cred.CRED_TYPE_GENERIC,
                    "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
                },
                0
            )
            logger.info(f"Encryption key stored in Credential Manager: {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to store encryption key: {e}")
            return False

    @staticmethod
    def retrieve_key(app_name: str) -> Optional[bytes]:
        """
        Retrieve encryption key from Windows Credential Manager.

        Args:
            app_name: Application name for credential target

        Returns:
            Encryption key bytes if found, None otherwise.
        """
        try:
            target = f"{app_name}_encryption_key"
            cred = win32cred.CredRead(
                TargetName=target,
                Type=win32cred.CRED_TYPE_GENERIC,
                Flags=0
            )
            return cred["CredentialBlob"]
        except pywintypes.error as e:
            logger.debug(f"Encryption key not found in Credential Manager: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve encryption key: {e}")
            return None

    @staticmethod
    def delete_key(app_name: str) -> bool:
        """
        Delete encryption key from Windows Credential Manager.

        Args:
            app_name: Application name for credential target

        Returns:
            True if successful, False otherwise.
        """
        try:
            target = f"{app_name}_encryption_key"
            win32cred.CredDelete(
                TargetName=target,
                Type=win32cred.CRED_TYPE_GENERIC,
                Flags=0
            )
            logger.info(f"Encryption key deleted from Credential Manager: {target}")
            return True
        except Exception as e:
            logger.debug(f"Failed to delete encryption key: {e}")
            return False


class EncryptedStorage:
    """Manages encrypted SQLite database for activity logs."""

    def __init__(
        self,
        db_path: str = "./data/activity_logs.db",
        app_name: str = "productivity_tracker",
    ):
        """
        Initialize encrypted storage.

        Args:
            db_path: Path to SQLite database file
            app_name: Application name for credential manager
        """
        self.db_path = db_path
        self.app_name = app_name
        self.encryption_key: Optional[bytes] = None
        self.cipher_suite: Optional[Fernet] = None

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._initialize_encryption()
        self._initialize_database()

    def _initialize_encryption(self) -> None:
        self.encryption_key = CredentialManager.retrieve_key(self.app_name)

        if not self.encryption_key:
            logger.info("Generating new encryption key...")
            self.encryption_key = Fernet.generate_key()

            if not CredentialManager.store_key(self.app_name, self.encryption_key):
                logger.warning(
                    "Failed to store encryption key in Credential Manager; using in-memory key"
                )

        self.cipher_suite = Fernet(self.encryption_key)
        logger.info("Encryption initialized")

    def _initialize_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id TEXT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                process_name VARCHAR(255) NOT NULL,
                window_title VARCHAR(512),
                domain VARCHAR(255),
                category VARCHAR(50) NOT NULL,
                duration_seconds INTEGER NOT NULL,
                is_synced BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME,
                UNIQUE(timestamp, process_name)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY,
                last_sync_time DATETIME,
                last_sync_status VARCHAR(50),
                pending_count INTEGER DEFAULT 0
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON activity_logs(timestamp)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_is_synced
            ON activity_logs(is_synced)
        """
        )

        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")

    # Rest of your file unchanged

    def insert_activity_log(
        self,
        timestamp: str,
        process_name: str,
        window_title: Optional[str],
        domain: Optional[str],
        category: str,
        duration_seconds: int,
    ) -> Optional[str]:
        """
        Insert a new activity log entry.

        Args:
            timestamp: ISO format timestamp
            process_name: Name of the active process
            window_title: Window title (if available)
            domain: Extracted domain (if available)
            category: Activity category
            duration_seconds: Duration of activity in seconds

        Returns:
            Log ID if successful, None otherwise.
        """
        try:
            log_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO activity_logs
                (log_id, timestamp, process_name, window_title, domain, category, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (log_id, timestamp, process_name, window_title, domain, category, duration_seconds),
            )

            conn.commit()
            conn.close()
            logger.debug(f"Activity log inserted: {log_id}")
            return log_id
        except sqlite3.IntegrityError:
            logger.debug(
                f"Duplicate log ignored: {process_name} at {timestamp}"
            )
            return None
        except Exception as e:
            logger.error(f"Error inserting activity log: {e}")
            return None

    def get_pending_logs(self, limit: int = 100) -> List[Dict]:
        """
        Get unsynchronized activity logs.

        Args:
            limit: Maximum number of logs to retrieve

        Returns:
            List of activity log dictionaries.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM activity_logs
                WHERE is_synced = 0
                ORDER BY timestamp ASC
                LIMIT ?
            """,
                (limit,),
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving pending logs: {e}")
            return []

    def mark_synced(self, log_ids: List[str]) -> bool:
        """
        Mark logs as synchronized.

        Args:
            log_ids: List of log IDs to mark as synced

        Returns:
            True if successful, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            sync_time = datetime.now().isoformat()

            for log_id in log_ids:
                cursor.execute(
                    """
                    UPDATE activity_logs
                    SET is_synced = 1, synced_at = ?
                    WHERE log_id = ?
                """,
                    (sync_time, log_id),
                )

            conn.commit()
            conn.close()
            logger.info(f"Marked {len(log_ids)} logs as synced")
            return True
        except Exception as e:
            logger.error(f"Error marking logs as synced: {e}")
            return False

    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Delete activity logs older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of logs deleted.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute(
                """
                DELETE FROM activity_logs
                WHERE created_at < ? AND is_synced = 1
            """,
                (cutoff_date,),
            )

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old logs")

            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return 0

    def get_statistics(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with log counts and aggregation info.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get total logs
            cursor.execute("SELECT COUNT(*) as total FROM activity_logs")
            total = cursor.fetchone()[0]

            # Get synced logs
            cursor.execute("SELECT COUNT(*) as synced FROM activity_logs WHERE is_synced = 1")
            synced = cursor.fetchone()[0]

            # Get pending logs
            cursor.execute(
                "SELECT COUNT(*) as pending FROM activity_logs WHERE is_synced = 0"
            )
            pending = cursor.fetchone()[0]

            # Get unique processes
            cursor.execute("SELECT COUNT(DISTINCT process_name) as processes FROM activity_logs")
            unique_processes = cursor.fetchone()[0]

            conn.close()

            return {
                "total_logs": total,
                "synced_logs": synced,
                "pending_logs": pending,
                "unique_processes": unique_processes,
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def export_pending_logs(self) -> Optional[str]:
        """
        Export pending logs as encrypted JSON payload.

        Returns:
            Encrypted payload string if successful, None otherwise.
        """
        import json
        try:
            logs = self.get_pending_logs(limit=1000)
            if not logs:
                return None

            payload = json.dumps(logs)
            encrypted_payload = self.cipher_suite.encrypt(payload.encode())
            return encrypted_payload.decode()
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            return None

    def close(self) -> None:
        """Clean shutdown of storage."""
        logger.info("Storage closed")
