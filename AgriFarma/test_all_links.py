import urllib.request
import urllib.error

def test_all_pages():
    """Test all major pages and footer links"""
    base_url = "http://localhost:5000"
    
    # Test pages
    pages = {
        "Home": "/",
        "Shop": "/shop",
        "Knowledge Base": "/blog",
        "Forum": "/forum",
        "Consultants": "/consultancy",
    }
    
    print("=" * 60)
    print("COMPLETE PAGE & FOOTER LINK TEST")
    print("=" * 60)
    
    all_passed = True
    
    for page_name, endpoint in pages.items():
        try:
            url = base_url + endpoint
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.status
                html = response.read().decode('utf-8')
                
                # Check for footer
                has_footer = 'class="af-footer"' in html
                has_sections = html.count('class="af-footer-section"')
                has_social = html.count('class="af-social-link"')
                
                print(f"\n{page_name} ({endpoint}):")
                print(f"  Status: {status} {'✓' if status == 200 else '✗'}")
                print(f"  Footer: {'✓' if has_footer else '✗'}")
                print(f"  Sections: {has_sections}/4 {'✓' if has_sections >= 4 else '✗'}")
                print(f"  Social: {has_social}/4 {'✓' if has_social >= 4 else '✗'}")
                
                if status == 200 and has_footer and has_sections >= 4:
                    print(f"  Result: ✓ PASS")
                else:
                    print(f"  Result: ✗ FAIL")
                    all_passed = False
                    
        except urllib.error.HTTPError as e:
            print(f"\n{page_name} ({endpoint}): HTTP {e.code} ✗ FAIL")
            all_passed = False
        except Exception as e:
            print(f"\n{page_name} ({endpoint}): ERROR - {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - Footer working on all pages!")
    else:
        print("✗ SOME TESTS FAILED - Check errors above")
    print("=" * 60)

if __name__ == "__main__":
    test_all_pages()
