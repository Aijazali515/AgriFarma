import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:5001/', timeout=5) as r:
        print(f"✅ Port 5001: {r.status} - {len(r.read())} bytes")
except Exception as e:
    print(f"❌ Port 5001: {e}")

try:
    with urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5) as r:
        print(f"✅ Port 5000: {r.status} - {len(r.read())} bytes")
except Exception as e:
    print(f"❌ Port 5000: {e}")
