"""
Productivity Tracker Client Package

OS-level process and network monitoring with encrypted local storage
and activity categorization for gamified productivity tracking.
"""

__version__ = "0.1.0"
__author__ = "Productivity Tracker Team"

from client.agent import ProductivityAgent
from client.process_tracker import ProcessTracker
from client.category_engine import CategoryEngine
from client.window_parser import WindowTitleParser
from client.local_storage import EncryptedStorage
from client.data_aggregator import DataAggregator
from client.network_mapper import NetworkMapper

__all__ = [
    "ProductivityAgent",
    "ProcessTracker",
    "CategoryEngine",
    "WindowTitleParser",
    "EncryptedStorage",
    "DataAggregator",
    "NetworkMapper",
]
