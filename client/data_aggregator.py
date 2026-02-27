"""
Data aggregator that batches activity logs into 5-minute windows.
Reduces log volume by combining identical activities and preparing for upload.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from client.config import AppConfig

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates activity logs into time-windowed batches."""

    def __init__(self, window_minutes: int = 5):
        """
        Initialize data aggregator.

        Args:
            window_minutes: Aggregation window size in minutes
        """
        self.window_minutes = window_minutes

    def aggregate_logs_batch(self, logs: List[Dict]) -> List[Dict]:
        """
        Aggregate logs into time windows with combined durations.

        Args:
            logs: List of activity log dictionaries

        Returns:
            Aggregated list of logs grouped by time window.
        """
        if not logs:
            return []

        aggregated = {}

        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log["timestamp"])
                # Round to window boundary
                window_start = self._get_window_start(timestamp)
                window_key = (
                    window_start.isoformat(),
                    log.get("process_name"),
                    log.get("domain"),
                    log.get("category"),
                )

                if window_key not in aggregated:
                    aggregated[window_key] = {
                        "timestamp": window_start.isoformat(),
                        "process_name": log.get("process_name"),
                        "window_title": log.get("window_title"),
                        "domain": log.get("domain"),
                        "category": log.get("category"),
                        "total_duration_seconds": 0,
                        "log_count": 0,
                    }

                aggregated[window_key]["total_duration_seconds"] += log.get(
                    "duration_seconds", 0
                )
                aggregated[window_key]["log_count"] += 1

            except Exception as e:
                logger.error(f"Error aggregating log: {e}")
                continue

        return list(aggregated.values())

    def _get_window_start(self, timestamp: datetime) -> datetime:
        """
        Get the start of the time window for a given timestamp.

        Args:
            timestamp: Timestamp to find window for

        Returns:
            Start of the containing window.
        """
        minutes_elapsed = timestamp.minute + (timestamp.hour * 60)
        window_minutes = (minutes_elapsed // self.window_minutes) * self.window_minutes
        hours = window_minutes // 60
        minutes = window_minutes % 60

        window_start = timestamp.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        return window_start

    def compress_batch(self, logs: List[Dict]) -> List[Dict]:
        """
        Compress batch by removing duplicate/similar entries.

        Combines logs from same process in same time window.

        Args:
            logs: List of activity logs

        Returns:
            Compressed log list.
        """
        if not logs:
            return []

        # Group by (timestamp, process_name, category)
        compressed = {}

        for log in logs:
            key = (
                log.get("timestamp"),
                log.get("process_name"),
                log.get("category"),
            )

            if key not in compressed:
                compressed[key] = log.copy()
            else:
                # Accumulate duration
                compressed[key]["total_duration_seconds"] = compressed[key].get(
                    "total_duration_seconds", 0
                ) + log.get("duration_seconds", 0)

        return list(compressed.values())

    def should_upload(
        self,
        pending_count: int,
        last_upload_time: Optional[datetime] = None,
        threshold_logs: int = None,
        threshold_minutes: int = None,
    ) -> bool:
        """
        Determine if pending logs should be uploaded.

        Args:
            pending_count: Number of pending logs
            last_upload_time: Last upload timestamp
            threshold_logs: Upload if pending count exceeds this
            threshold_minutes: Upload if this many minutes since last upload

        Returns:
            True if upload should occur, False otherwise.
        """
        if threshold_logs is None:
            threshold_logs = AppConfig.SYNC_THRESHOLD_LOGS
        if threshold_minutes is None:
            threshold_minutes = AppConfig.SYNC_THRESHOLD_MINUTES

        # Check log count threshold
        if pending_count >= threshold_logs:
            logger.debug(
                f"Upload triggered: {pending_count} >= {threshold_logs} logs"
            )
            return True

        # Check time threshold
        if last_upload_time:
            time_since_upload = datetime.now() - last_upload_time
            if time_since_upload >= timedelta(minutes=threshold_minutes):
                logger.debug(
                    f"Upload triggered: {time_since_upload} >= {threshold_minutes} minutes"
                )
                return True

        return False

    def prepare_upload_payload(self, logs: List[Dict]) -> Dict:
        """
        Prepare aggregated logs for server transmission.

        Args:
            logs: Aggregated log list

        Returns:
            Upload payload dictionary.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "log_count": len(logs),
            "logs": logs,
            "summary": self._generate_summary(logs),
        }

    def _generate_summary(self, logs: List[Dict]) -> Dict:
        """
        Generate summary statistics for log batch.

        Args:
            logs: Log list

        Returns:
            Summary dictionary.
        """
        summary = {
            "total_logs": len(logs),
            "total_seconds": 0,
            "categories": {},
            "top_applications": {},
        }

        category_weights = {}

        for log in logs:
            duration = log.get("total_duration_seconds", log.get("duration_seconds", 0))
            summary["total_seconds"] += duration

            category = log.get("category", "Neutral")
            summary["categories"][category] = summary["categories"].get(category, 0) + 1

            # Track weighted score
            weight = AppConfig.get_category_weight(category)
            category_weights[category] = (
                category_weights.get(category, 0) + duration * weight
            )

            # Track top applications
            app = log.get("process_name", "Unknown")
            summary["top_applications"][app] = (
                summary["top_applications"].get(app, 0) + duration
            )

        # Sort top applications
        summary["top_applications"] = dict(
            sorted(
                summary["top_applications"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
        )

        # Calculate weighted productivity score
        if summary["total_seconds"] > 0:
            total_weight = sum(category_weights.values())
            summary["weighted_score"] = (
                total_weight / summary["total_seconds"]
                if summary["total_seconds"] > 0
                else 0
            )
        else:
            summary["weighted_score"] = 0

        return summary
