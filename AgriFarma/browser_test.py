"""Test actual browser request to capture real-time error.
Run with: python browser_test.py
"""
import requests

try:
    response = requests.get('http://127.0.0.1:5000/', timeout=5)
    print(f'Status Code: {response.status_code}')
    print(f'Content Length: {len(response.content)}')
    if response.status_code >= 400:
        print('\n=== RESPONSE CONTENT ===')
        print(response.text[:2000])
except requests.exceptions.ConnectionError:
    print('ERROR: Cannot connect to http://127.0.0.1:5000/')
    print('Is the Flask server running?')
except Exception as e:
    print(f'ERROR: {e}')
