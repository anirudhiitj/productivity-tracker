"""Check ALL windows to see what Chrome tabs exist"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.window_parser import WindowTitleParser

print("\n=== ALL BROWSER WINDOWS ===\n")
windows = WindowTitleParser.get_all_browser_windows()
print(f"Total windows found: {len(windows)}\n")

# Group by PID
from collections import defaultdict
by_pid = defaultdict(list)
for pid, title in windows:
    by_pid[pid].append(title)

print("Windows grouped by PID:\n")
for pid, titles in sorted(by_pid.items()):
    print(f"PID {pid}: {len(titles)} windows")
    for title in titles:
        is_junk = WindowTitleParser.is_junk_window(title)
        junk_marker = " [JUNK]" if is_junk else ""
        print(f"  - {title[:100]}{junk_marker}")
    print()
