"""Make actual HTTP request to capture browser-like error.
Run: python capture_browser_error.py
"""
import urllib.request
import urllib.error

try:
    with urllib.request.urlopen('http://127.0.0.1:5000/', timeout=10) as response:
        status = response.status
        content = response.read()
        print(f'✅ Status: {status}')
        print(f'Content-Length: {len(content)}')
        print(f'Content-Type: {response.headers.get("Content-Type")}')
except urllib.error.HTTPError as e:
    print(f'❌ HTTP Error {e.code}')
    print('Response body:')
    print(e.read().decode('utf-8')[:2000])
except urllib.error.URLError as e:
    print(f'❌ URL Error: {e.reason}')
except Exception as e:
    print(f'❌ Exception: {e}')
