#!/usr/bin/env python3
"""
Productivity Tracker Agent - Main Entry Point
Start the OS-level productivity monitoring agent.
"""

import sys
import logging
from client.agent import ProductivityAgent


def main():
    """Entry point for the application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Productivity Tracker Agent Starting")
    logger.info("=" * 60)

    try:
        agent = ProductivityAgent()
        agent.start()
    except KeyboardInterrupt:
        print("\n\nAgent interrupted by user. Cleaning up...")
        logger.info("Agent interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
