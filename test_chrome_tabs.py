"""Test to see how many Chrome tabs the API is returning"""
import requests

try:
    resp = requests.get('http://localhost:8000/api/processes/main', timeout=10)
    data = resp.json()
    
    chrome = [p for p in data if 'chrome' in p.get('name','').lower() and p.get('window_title')]
    
    print(f'\nChrome processes with tabs: {len(chrome)}')
    print('=' * 80)
    
    for i, p in enumerate(chrome[:20], 1):
        domain = p.get('domain', 'N/A')
        title = p.get('window_title', '')[:70]
        category = p.get('category', 'N/A')
        print(f'{i:2}. {domain:12} | {category:15} | {title}')
    
    print('=' * 80)
    
except Exception as e:
    print(f'Error: {e}')
    print('\nMake sure backend is running: python -m uvicorn backend.main:app --port 8000')
