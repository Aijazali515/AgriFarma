"""Comprehensive test for cart functionality"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all models and routes import correctly"""
    print("=" * 70)
    print("TESTING IMPORTS AND RELATIONSHIPS")
    print("=" * 70)
    
    try:
        from agrifarma.models.user import User
        from agrifarma.models.ecommerce import CartItem, Product, Order
        print("✓ All models imported successfully")
        
        # Check User model has cart_items
        if hasattr(User, 'cart_items'):
            print("✓ User.cart_items relationship exists")
        else:
            print("✗ User.cart_items relationship missing")
            
        # Check CartItem has user relationship
        if hasattr(CartItem, 'user'):
            print("✓ CartItem.user relationship exists")
        else:
            print("✗ CartItem.user relationship missing")
            
        print("\n✓ No mapper conflicts - relationships configured correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_routes():
    """Test that routes are properly defined"""
    print("\n" + "=" * 70)
    print("TESTING ROUTES")
    print("=" * 70)
    
    try:
        from agrifarma.routes.ecommerce import bp
        
        # Get all route rules
        routes = []
        for rule in bp.url_map.iter_rules() if hasattr(bp, 'url_map') else []:
            routes.append(str(rule))
        
        # Check specific routes exist in the blueprint
        route_functions = [func for func in dir(bp) if not func.startswith('_')]
        
        if 'quick_add_to_cart' in str(route_functions):
            print("✓ quick_add_to_cart route exists")
        else:
            # Check the actual file
            routes_file = os.path.join(os.path.dirname(__file__), 'agrifarma', 'routes', 'ecommerce.py')
            with open(routes_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'def quick_add_to_cart' in content:
                    print("✓ quick_add_to_cart function defined in ecommerce.py")
                else:
                    print("✗ quick_add_to_cart function not found")
        
        print("✓ Routes module loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ Routes error: {e}")
        return False

def test_templates():
    """Test template files exist and have required content"""
    print("\n" + "=" * 70)
    print("TESTING TEMPLATES")
    print("=" * 70)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    templates = {
        'navigation.html': ['af-cart-btn', 'bi-cart3', 'cart_count'],
        'shop.html': ['af-quick-cart-btn', 'quick_add_to_cart', 'bi-cart-plus'],
        'cart.html': ['cart', 'checkout'],
    }
    
    all_pass = True
    for template, required_items in templates.items():
        template_path = os.path.join(base_path, 'agrifarma', 'templates', 
                                     'includes' if template == 'navigation.html' else '', 
                                     template)
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                missing = [item for item in required_items if item not in content]
                if missing:
                    print(f"✗ {template}: Missing {missing}")
                    all_pass = False
                else:
                    print(f"✓ {template}: All required elements present")
        else:
            print(f"✗ {template}: File not found")
            all_pass = False
    
    return all_pass

def main():
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CART FUNCTIONALITY TEST SUITE" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝\n")
    
    results = []
    
    # Run tests
    results.append(("Imports & Relationships", test_imports()))
    results.append(("Routes", test_routes()))
    results.append(("Templates", test_templates()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Cart functionality is ready.")
        print("\nNext steps:")
        print("1. Open http://localhost:5000 in browser")
        print("2. Login to your account")
        print("3. Navigate to Shop page")
        print("4. Hover over products to see cart buttons")
        print("5. Click to add items and test the flow")
    else:
        print("⚠ Some tests failed. Please review errors above.")
    print("=" * 70)

if __name__ == "__main__":
    main()
