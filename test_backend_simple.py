import requests
import json

try:
    print("Connecting to http://127.0.0.1:8000/api/health")
    response = requests.get('http://127.0.0.1:8000/api/health', timeout=5)
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
