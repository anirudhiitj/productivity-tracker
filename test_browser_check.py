"""Quick test of is_browser_process"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.window_parser import WindowTitleParser

test_names = [
    "chrome.exe",
    "msedge.exe",
    "msedgewebview2.exe",
    "firefox.exe",
    "Code.exe",
]

print("Testing is_browser_process:")
for name in test_names:
    result = WindowTitleParser.is_browser_process(name)
    print(f"  {name:25} -> {result}")
