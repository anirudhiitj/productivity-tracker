#!/usr/bin/env python3
"""Direct API test - check if real browser tabs are being returned."""

import requests
import json

print("\nTesting API directly for browser tabs...")
print("=" * 70)

try:
    response = requests.get("http://localhost:8000/api/processes/main", timeout=5)
    data = response.json()
    
    print(f"\nTotal processes returned: {data['stats']['total_processes']}")
    
    # Find Chrome processes
    chrome_procs = [p for p in data['processes'] if 'chrome' in p['name'].lower()]
    print(f"Chrome processes: {len(chrome_procs)}")
    
    # Show only those with window titles
    chrome_with_titles = [p for p in chrome_procs if p.get('window_title')]
    print(f"Chrome with window titles: {len(chrome_with_titles)}")
    
    if chrome_with_titles:
        print("\nCapt browser tabs (first 5):")
        print("-" * 70)
        for proc in chrome_with_titles[:5]:
            print(f"  Site: {proc['domain']}")
            print(f"  Title: {proc['window_title'][:60]}")
            print(f"  Category: {proc['category']}")
            print()
    else:
        print("\nNo Chrome processes with window titles found.")
        print("First 3 Chrome processes:")
        for proc in chrome_procs[:3]:
            print(f"  Name: {proc['name']}")
            print(f"  Title: {proc.get('window_title', 'None')}")
            print(f"  Domain: {proc.get('domain', 'None')}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
    print("Backend may not be running on http://localhost:8000")

print("=" * 70)
