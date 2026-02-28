"""
Test if we can access Chrome DevTools Protocol to get ALL tabs
"""
import json
import requests

def get_all_chrome_tabs():
    """Get all Chrome tabs using Chrome DevTools Protocol"""
    try:
        # Chrome DevTools runs on port 9222 by default (must be launched with --remote-debugging-port=9222)
        response = requests.get('http://localhost:9222/json', timeout=2)
        tabs = response.json()
        
        print(f"✓ Found {len(tabs)} Chrome tabs via DevTools Protocol:\n")
        for i, tab in enumerate(tabs, 1):
            title = tab.get('title', 'No title')
            url = tab.get('url', 'No URL')
            tab_type = tab.get('type', 'unknown')
            print(f"  {i}. [{tab_type}] {title}")
            print(f"     URL: {url}\n")
        return tabs
    except requests.exceptions.ConnectionError:
        print("✗ Chrome DevTools Protocol not available")
        print("\nTo enable, restart Chrome with:")
        print('  chrome.exe --remote-debugging-port=9222')
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n=== Checking Chrome DevTools Protocol ===\n")
    tabs = get_all_chrome_tabs()
    
    if tabs is None:
        print("\n" + "="*60)
        print("ALTERNATIVE: Window enumeration (what we currently use)")
        print("="*60)
        print("\nThis method only sees:")
        print("  - Active tab in each Chrome WINDOW")
        print("  - Not background tabs in the same window")
        print("\nTo see ALL tabs, Chrome needs DevTools Protocol enabled.")
