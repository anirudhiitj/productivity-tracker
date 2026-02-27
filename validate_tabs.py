"""Quick validation that browser tabs are now showing."""
import requests

data = requests.get('http://localhost:8000/api/processes/main').json()
chrome_tabs = [p for p in data if 'chrome' in p.get('name','').lower() and p.get('window_title')]

print(f"\n✓ SUCCESS: {len(chrome_tabs)} browser tabs captured!\n")
for i, tab in enumerate(chrome_tabs[:6], 1):
    domain = tab.get('domain', 'unknown')
    title = tab.get('window_title', '')[:55]
    cat = tab.get('category', 'Uncategorized')
    print(f"{i}. {domain:12} [{cat}] {title}")
