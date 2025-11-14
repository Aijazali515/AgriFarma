import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:5002/', timeout=5) as r:
        status = r.status
        content = r.read()
        print(f"✅ SUCCESS!")
        print(f"Status: {status}")
        print(f"Content-Length: {len(content)}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}")
except Exception as e:
    print(f"❌ Error: {e}")
