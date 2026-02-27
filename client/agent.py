"""
Main system monitoring agent that orchestrates all components.
Continuously polls the foreground window, categorizes activity, and stores encrypted logs.
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
from client.config import AppConfig
from client.process_tracker import ProcessTracker
from client.window_parser import WindowTitleParser
from client.category_engine import CategoryEngine
from client.network_mapper import NetworkMapper
from client.local_storage import EncryptedStorage
from client.data_aggregator import DataAggregator

# Configure logging
logging.basicConfig(
    level=getattr(logging, AppConfig.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(AppConfig.LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class ProductivityAgent:
    """Main productivity tracking agent."""

    def __init__(self):
        """Initialize the agent with all components."""
        logger.info("Initializing Productivity Agent...")

        self.process_tracker = ProcessTracker()
        self.storage = EncryptedStorage()
        self.aggregator = DataAggregator(
            window_minutes=AppConfig.AGGREGATION_WINDOW_MIN
        )
        self.network_mapper = NetworkMapper(cache_dns=True)

        self.is_running = False
        self.last_aggregation_time = datetime.now()
        self.last_sync_time = None

        logger.info("Productivity Agent initialized")

    def start(self) -> None:
        """Start the monitoring agent."""
        if self.is_running:
            logger.warning("Agent is already running")
            return

        logger.info("Starting Productivity Agent...")
        self.is_running = True

        # Start background threads
        aggregation_thread = threading.Thread(
            target=self._periodic_aggregation_loop, daemon=True
        )
        aggregation_thread.start()

        # Main polling loop
        try:
            self._polling_loop()
        except KeyboardInterrupt:
            logger.info("Agent interrupted by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Fatal error in agent: {e}", exc_info=True)
            self.shutdown()

    def _polling_loop(self) -> None:
        """
        Main polling loop that runs every POLLING_INTERVAL_MS.
        Captures foreground process and stores activity.
        """
        logger.info("Starting main polling loop...")
        previous_snapshot = None

        while self.is_running:
            try:
                # Poll current foreground process
                current_snapshot = self.process_tracker.poll_active_process()

                # Check for activity change
                has_changed, prev_activity, curr_activity = (
                    self.process_tracker.detect_activity_change(
                        previous_snapshot, current_snapshot
                    )
                )

                if has_changed and previous_snapshot:
                    # Log the previous activity
                    self._log_activity(previous_snapshot)

                # Update tracking
                self.process_tracker.update_activity(current_snapshot)
                previous_snapshot = current_snapshot

                # Sleep for polling interval
                time.sleep(AppConfig.POLLING_INTERVAL_MS / 1000.0)

            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
                time.sleep(1)  # Brief pause before retry

        # Log final activity on shutdown
        if previous_snapshot:
            self._log_activity(previous_snapshot)

    def _log_activity(self, snapshot: dict) -> None:
        """
        Log an activity snapshot to storage.

        Args:
            snapshot: Process snapshot from tracker
        """
        try:
            process_name = snapshot.get("process_name")
            window_title = snapshot.get("window_title")
            process_path = snapshot.get("process_path")

            if not process_name:
                return

            # Extract domain from window title if browser
            domain = None
            if WindowTitleParser.is_browser_process(process_name) and window_title:
                domain = WindowTitleParser.extract_domain_from_title(window_title)

            # Get domains from network connections if available
            if not domain and snapshot.get("pid"):
                domains = self.network_mapper.get_domains_for_process(snapshot["pid"])
                if domains:
                    domain = domains[0]  # Use first domain

            # Categorize activity
            category = CategoryEngine.categorize_activity(
                process_name=process_name,
                domain=domain,
                window_title=window_title,
            )

            # Calculate duration
            duration_ms = self.process_tracker.get_activity_duration()
            duration_seconds = int((duration_ms or 0) / 1000)

            if duration_seconds <= 0:
                return

            # Store in local database
            log_id = self.storage.insert_activity_log(
                timestamp=snapshot["timestamp"],
                process_name=process_name,
                window_title=window_title,
                domain=domain,
                category=category,
                duration_seconds=duration_seconds,
            )

            if log_id:
                logger.debug(
                    f"Activity logged: {process_name} ({category}) - "
                    f"{duration_seconds}s (domain: {domain})"
                )

        except Exception as e:
            logger.error(f"Error logging activity: {e}", exc_info=True)

    def _periodic_aggregation_loop(self) -> None:
        """
        Background thread that periodically aggregates and syncs logs.
        Runs every 5 minutes or when log threshold is reached.
        """
        logger.info("Starting aggregation loop...")

        while self.is_running:
            try:
                # Check if aggregation is needed
                time_since_last = datetime.now() - self.last_aggregation_time
                if (
                    time_since_last.total_seconds()
                    >= AppConfig.AGGREGATION_WINDOW_MIN * 60
                ):
                    self._perform_aggregation()
                    self.last_aggregation_time = datetime.now()

                    # Check if sync is needed
                    stats = self.storage.get_statistics()
                    if self.aggregator.should_upload(
                        pending_count=stats.get("pending_logs", 0),
                        last_upload_time=self.last_sync_time,
                    ):
                        self._prepare_sync_payload()

                # Sleep between checks
                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}", exc_info=True)
                time.sleep(60)

    def _perform_aggregation(self) -> None:
        """Aggregate pending logs into time windows."""
        try:
            pending_logs = self.storage.get_pending_logs(limit=500)

            if pending_logs:
                aggregated = self.aggregator.aggregate_logs_batch(pending_logs)
                logger.info(
                    f"Aggregated {len(pending_logs)} logs into "
                    f"{len(aggregated)} time windows"
                )

                # Log aggregation summary
                stats = self.storage.get_statistics()
                logger.info(f"Storage stats: {stats}")

        except Exception as e:
            logger.error(f"Error in aggregation: {e}", exc_info=True)

    def _prepare_sync_payload(self) -> None:
        """Prepare aggregated logs for upload (mock for now)."""
        try:
            pending_logs = self.storage.get_pending_logs(limit=100)

            if pending_logs:
                aggregated = self.aggregator.aggregate_logs_batch(pending_logs)
                payload = self.aggregator.prepare_upload_payload(aggregated)

                logger.info(
                    f"Sync payload prepared: {payload['log_count']} logs, "
                    f"{payload['summary']['total_seconds']}s total, "
                    f"score: {payload['summary'].get('weighted_score', 0):.2f}"
                )

                self.last_sync_time = datetime.now()
                logger.debug(f"Payload ready for upload: {payload}")

        except Exception as e:
            logger.error(f"Error preparing sync payload: {e}", exc_info=True)

    def get_status(self) -> dict:
        """
        Get current agent status.

        Returns:
            Status dictionary.
        """
        try:
            stats = self.storage.get_statistics()
            return {
                "running": self.is_running,
                "start_time": datetime.now().isoformat(),
                "storage_stats": stats,
                "dns_cache": self.network_mapper.get_dns_cache_stats(),
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {"running": self.is_running, "error": str(e)}

    def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        logger.info("Shutting down Productivity Agent...")
        self.is_running = False

        try:
            # Cleanup
            self.storage.cleanup_old_logs(days=AppConfig.RETENTION_DAYS)
            self.storage.close()
            self.network_mapper.clear_dns_cache()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)

        logger.info("Productivity Agent shutdown complete")


def main():
    """Entry point for the agent."""
    agent = ProductivityAgent()
    agent.start()


if __name__ == "__main__":
    main()
