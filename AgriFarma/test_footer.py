import requests
import sys

def test_footer_on_pages():
    """Test that footer appears on all major pages"""
    base_url = "http://localhost:5000"
    
    # Test pages
    pages = {
        "Home": "/",
        "Shop": "/shop",
        "Knowledge Base": "/blog",
        "Forum": "/forum",
        "Consultants": "/consultancy"
    }
    
    print("=" * 60)
    print("FOOTER IMPLEMENTATION TEST")
    print("=" * 60)
    
    session = requests.Session()
    
    for page_name, endpoint in pages.items():
        try:
            url = base_url + endpoint
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                html = response.text
                
                # Check for footer elements in HTML
                has_footer = 'class="af-footer"' in html
                has_brand = 'class="af-footer-brand"' in html
                has_social = 'class="af-social-link"' in html
                has_bottom = 'class="af-footer-bottom"' in html
                
                # Count sections
                section_count = html.count('class="af-footer-section"')
                social_count = html.count('class="af-social-link"')
                
                print(f"\n{page_name} ({endpoint}):")
                print(f"  Status: {response.status_code} ✓")
                print(f"  Footer Present: {'✓' if has_footer else '✗'}")
                print(f"  Brand Section: {'✓' if has_brand else '✗'}")
                print(f"  Footer Sections: {section_count}/4")
                print(f"  Social Links: {social_count}/4")
                print(f"  Bottom Bar: {'✓' if has_bottom else '✗'}")
                
                if has_footer and section_count >= 4 and social_count >= 4:
                    print(f"  Overall: ✓ PASS")
                else:
                    print(f"  Overall: ✗ FAIL - Missing elements")
            else:
                print(f"\n{page_name} ({endpoint}): {response.status_code} ✗ FAIL")
                
        except Exception as e:
            print(f"\n{page_name} ({endpoint}): ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_footer_on_pages()
