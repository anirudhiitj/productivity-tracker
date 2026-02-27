#!/usr/bin/env python3
"""Demonstration of actual browser tabs now being properly captured."""

import sys
from backend.process_monitor import ProcessMonitor
from client.window_parser import WindowTitleParser

print("\n" + "="*80)
print("REAL BROWSER TABS WITH IMPROVED PARSING")
print("="*80)

# Get all browser windows first
all_windows = WindowTitleParser.get_all_browser_windows()
print(f"\nAll visible browser tabs found: {len(all_windows)}")
print("-" * 80)

for pid, title in sorted(all_windows):
    extracted = WindowTitleParser.extract_domain_from_title(title)
    is_junk = WindowTitleParser.is_junk_window(title)
    
    status = "JUNK" if is_junk else f"OK: {extracted or 'generic'}"
    title_display = title[:70]
    print(f"  {status:<25} | {title_display}")

# Now show what ProcessMonitor enriches
print(f"\n" + "="*80)
print("PROCESS MONITOR - ENRICHED DATA")
print("="*80)

pm = ProcessMonitor()
processes = pm.get_main_processes()

# Filter to show only browser processes with meaningful titles
browser_with_titles = [p for p in processes 
                       if WindowTitleParser.is_browser_process(p['name']) 
                       and p.get('window_title')
                       and not WindowTitleParser.is_junk_window(p.get('window_title'))]

print(f"\nBrowser tabs with meaningful content: {len(browser_with_titles)}")
print("-" * 80)
print(f"{'Site':<15} {'Memory':<12} {'Category':<15} {'Tab Title'}") 
print("-" * 80)

for proc in sorted(browser_with_titles, key=lambda p: p.get('domain', ''))[:15]:
    site = proc.get('domain', 'unknown')[:14]
    memory = f"{proc['memory_mb']:.0f}MB"
    category = proc['category'][:14]
    title = proc['window_title'][:50]
    
    print(f"{site:<15} {memory:<12} {category:<15} {title}")

print("\n" + "="*80)
print("Success! Now showing actual website tabs, not internal processes!")
print("="*80 + "\n")
