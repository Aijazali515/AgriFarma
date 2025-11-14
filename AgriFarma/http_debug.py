"""Make HTTP request with full debug output to see what's happening."""
import http.client
import sys

conn = http.client.HTTPConnection('127.0.0.1', 5000)
conn.set_debuglevel(1)

print("=" * 70)
print("Making GET request to http://127.0.0.1:5000/")
print("=" * 70)

try:
    conn.request("GET", "/")
    response = conn.getresponse()
    
    print(f"\n{'=' * 70}")
    print(f"Response Status: {response.status} {response.reason}")
    print(f"{'=' * 70}")
    print("\nResponse Headers:")
    for header, value in response.getheaders():
        print(f"  {header}: {value}")
    
    body = response.read()
    print(f"\nResponse Body Length: {len(body)} bytes")
    print(f"\nFirst 1000 characters of body:")
    print(body[:1000].decode('utf-8', errors='replace'))
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
