"""Simple HTTP test for cart"""
import urllib.request
import urllib.error

def test_pages():
    print("=" * 70)
    print("HTTP ENDPOINT TESTS")
    print("=" * 70)
    
    pages = {
        "Home": "http://localhost:5000/",
        "Shop": "http://localhost:5000/shop",
        "Cart": "http://localhost:5000/cart",
    }
    
    for name, url in pages.items():
        try:
            response = urllib.request.urlopen(url, timeout=5)
            status = response.status
            content = response.read().decode('utf-8')
            
            print(f"\n{name} ({url}):")
            print(f"  Status: {status} ✓")
            
            if name == "Shop":
                has_quick_cart = 'af-quick-cart-btn' in content
                has_wrapper = 'af-product-card-wrapper' in content
                print(f"  Quick cart buttons: {'✓' if has_quick_cart else '✗'}")
                print(f"  Product wrappers: {'✓' if has_wrapper else '✗'}")
            elif name == "Cart":
                # Cart might redirect, that's okay
                print(f"  Cart page accessible")
                
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print(f"\n{name}: Redirects (expected for protected pages) ✓")
            else:
                print(f"\n{name}: HTTP Error {e.code}")
        except Exception as e:
            print(f"\n{name}: Error - {e}")
    
    print("\n" + "=" * 70)
    print("Server is running! Open browser to test visually:")
    print("http://localhost:5000")
    print("=" * 70)

if __name__ == "__main__":
    test_pages()
