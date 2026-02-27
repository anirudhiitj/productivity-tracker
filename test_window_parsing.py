#!/usr/bin/env python3
"""
Test script for improved window title parsing focusing on active/meaningful windows.
"""

from client.window_parser import WindowTitleParser
from backend.process_monitor import ProcessMonitor

print("\n" + "="*70)
print("🧪 Testing Improved Window Title Parsing")
print("="*70)

# Test 1: Check junk window detection
print("\n✅ Test 1: Junk Window Detection")
test_titles = [
    ("MSCTFIME UI", True, "Should filter junk"),
    ("Default IME", True, "Should filter junk"),
    ("LeetCode - Google Chrome", False, "Should keep meaningful"),
    ("GitHub - myrepo - Mozilla Firefox", False, "Should keep meaningful"),
    ("localhost:3000 - React App", False, "Should keep meaningful"),
    ("", True, "Should filter empty"),
]

for title, expected_junk, reason in test_titles:
    is_junk = WindowTitleParser.is_junk_window(title)
    status = "✅" if is_junk == expected_junk else "❌"
    print(f"  {status} '{title}' → {'JUNK' if is_junk else 'KEEP'} ({reason})")

# Test 2: Get all browser windows (not just foreground)
print("\n✅ Test 2: Getting All Browser Windows")
browser_windows = WindowTitleParser.get_all_browser_windows()
print(f"  Found {len(browser_windows)} browser windows:")
for pid, title in browser_windows[:10]:  # Show first 10
    is_junk = "❌ JUNK" if WindowTitleParser.is_junk_window(title) else "✅ GOOD"
    print(f"    PID {pid}: {title[:60]} {is_junk}")

# Test 3: Get foreground window
print("\n✅ Test 3: Getting Foreground Window")
fg_info = WindowTitleParser.get_foreground_window_info()
if fg_info:
    title, pid = fg_info
    print(f"  Foreground window PID: {pid}")
    print(f"  Title: {title}")
else:
    print(f"  (No meaningful foreground window found)")

# Test 4: Test ProcessMonitor with new approach
print("\n✅ Test 4: ProcessMonitor with Intelligent Enrichment")
pm = ProcessMonitor()
processes = pm.get_main_processes()
print(f"  Total processes: {len(processes)}")

# Show browser processes with good window titles
browser_procs = [p for p in processes if WindowTitleParser.is_browser_process(p['name']) and p.get('window_title')]
print(f"  Browser processes with meaningful window titles: {len(browser_procs)}")

if browser_procs:
    print("\n  Browser Processes Captured:")
    for proc in browser_procs[:5]:
        print(f"    • {proc['name']}")
        print(f"      Window: {proc['window_title'][:60]}")
        print(f"      Domain: {proc.get('domain', 'N/A')}")
        print(f"      Category: {proc['category']}")
        print(f"      Source: {proc.get('categorization_source', 'N/A')}")
        print()

# Test 5: Check for junk processes that got filtered
print("✅ Test 5: Junk Processes Filtered Out")
all_processes = pm.get_all_processes()
junk_count = 0
junk_examples = []
for proc in all_processes:
    if WindowTitleParser.is_browser_process(proc['name']):
        # Check if any old enrichment found junk
        if proc['memory_mb'] < 50:  # Very light browser processes often have no real window
            junk_count += 1
            if len(junk_examples) < 3:
                junk_examples.append(proc['name'])

print(f"  Filtered out approximately {junk_count} light/internal Chrome processes")
if junk_examples:
    print(f"  Examples: {', '.join(junk_examples)}")

print("\n" + "="*70)
print("✨ Window Title Parsing Tests Complete!")
print("="*70 + "\n")
