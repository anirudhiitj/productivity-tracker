"""Simple API test to see Chrome tabs"""
import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/api/processes/main', timeout=60)
    data = response.json()
    
    processes = data.get('processes', [])
    print(f"\n✓ Total processes: {len(processes)}")
    
    # Filter Chrome tabs
    chrome_tabs = [p for p in processes if 'chrome.exe' == p.get('name', '').lower()]
    print(f"✓ Chrome tabs found: {len(chrome_tabs)}\n")
    
    print("Chrome Tabs:")
    for i, tab in enumerate(chrome_tabs, 1):
        domain = tab.get('domain') or 'N/A'
        title = tab.get('window_title') or 'N/A'
        category = tab.get('category') or 'N/A'
        mem = tab.get('memory_mb', 0)
        print(f"  {i:2}. {domain:20} | {category:15} | {mem:6.1f}MB | {title[:60]}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
