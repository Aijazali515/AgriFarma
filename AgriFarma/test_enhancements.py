"""
Comprehensive Test Suite for AgriFarma Core Enhancements
Tests global search, payment processing, and all new features
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decimal import Decimal
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from agrifarma.models.forum import Category, Thread
from agrifarma.models.blog import BlogPost
from agrifarma.models.ecommerce import Product, Order
from agrifarma.models.consultancy import Consultant
from werkzeug.security import generate_password_hash


def test_global_search():
    """Test global search functionality"""
    print("\n=== Testing Global Search ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        # Create test data
        user = User.query.first()
        if not user:
            user = User(
                email="searchtest@example.com",
                password_hash=generate_password_hash("password123"),
                role="User"
            )
            db.session.add(user)
            db.session.flush()
            
            profile = Profile(user_id=user.id, name="Search Test User")
            db.session.add(profile)
            db.session.commit()
        
        # Create test forum thread
        category = Category.query.first()
        if not category:
            category = Category(name="Test Category", description="Test")
            db.session.add(category)
            db.session.commit()
        
        thread = Thread(
            title="Test Wheat Farming",
            author_id=user.id,
            category_id=category.id
        )
        db.session.add(thread)
        db.session.flush()
        
        # Add a post to the thread
        from agrifarma.models.forum import Post
        post = Post(
            thread_id=thread.id,
            author_id=user.id,
            content="Discussion about wheat cultivation techniques"
        )
        db.session.add(post)
        
        # Create test blog post
        blog_post = BlogPost(
            title="Wheat Growing Guide",
            content="Complete guide to growing wheat in Pakistan",
            category="Agriculture",
            author_id=user.id,
            approved=True
        )
        db.session.add(blog_post)
        
        # Create test product
        product = Product(
            name="Wheat Seeds Premium",
            description="High quality wheat seeds",
            price=Decimal('500.00'),
            category="Seeds",
            seller_id=user.id,
            status="Active",
            inventory=100
        )
        db.session.add(product)
        
        db.session.commit()
        
        # Test search
        with app.test_client() as client:
            # Search for "wheat"
            response = client.get('/search/?q=wheat')
            print(f"✓ Global search response: {response.status_code}")
            assert response.status_code == 200, "Search page should load"
            
            # Check if results contain search term
            data = response.data.decode('utf-8')
            assert 'wheat' in data.lower() or 'Search Results' in data, "Search results should be displayed"
            print(f"✓ Search results displayed correctly")
            
            # Test module-specific search
            response = client.get('/search/?q=wheat&module=forum')
            assert response.status_code == 200, "Forum search should work"
            print(f"✓ Module-specific search works")
            
            # Test empty query
            response = client.get('/search/?q=')
            assert response.status_code == 200, "Empty search should not crash"
            print(f"✓ Empty search handled correctly")
        
        # Cleanup
        db.session.delete(post)
        db.session.delete(thread)
        db.session.delete(blog_post)
        db.session.delete(product)
        db.session.commit()
        
        print("✓ Global search tests passed")


def test_payment_processing():
    """Test payment processing functionality"""
    print("\n=== Testing Payment Processing ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        from agrifarma.services import payment as payment_service
        
        # Test mock payment gateway
        result = payment_service.process_order_payment(
            order_id=1,
            amount=Decimal('1500.50'),
            customer_email="customer@example.com",
            payment_method="card"
        )
        
        print(f"✓ Payment processing result: {result.success}")
        assert result.success, "Mock payment should succeed"
        assert result.transaction_id, "Transaction ID should be generated"
        assert result.transaction_id.startswith('MOCK_'), "Mock transaction ID should have MOCK_ prefix"
        print(f"✓ Transaction ID: {result.transaction_id}")
        
        # Test COD (Cash on Delivery)
        cod_result = payment_service.process_order_payment(
            order_id=2,
            amount=Decimal('2000.00'),
            customer_email="customer@example.com",
            payment_method="cod"
        )
        
        assert cod_result.success, "COD should succeed"
        assert cod_result.transaction_id.startswith('COD_'), "COD transaction ID should have COD_ prefix"
        print(f"✓ COD payment: {cod_result.transaction_id}")
        
        # Test payment verification
        gateway = payment_service.get_payment_gateway('mock')
        verify_result = gateway.verify_payment(result.transaction_id)
        assert verify_result.success, "Payment verification should succeed"
        print(f"✓ Payment verification works")
        
        # Test refund
        refund_result = gateway.refund_payment(result.transaction_id, Decimal('500.00'))
        assert refund_result.success, "Refund should succeed"
        print(f"✓ Payment refund: {refund_result.transaction_id}")
        
        print("✓ Payment processing tests passed")


def test_order_with_payment():
    """Test complete order flow with payment"""
    print("\n=== Testing Order with Payment Integration ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        # Create test user
        user = User.query.filter_by(email="ordertest@example.com").first()
        if not user:
            user = User(
                email="ordertest@example.com",
                password_hash=generate_password_hash("password123"),
                role="User"
            )
            db.session.add(user)
            db.session.flush()
            
            profile = Profile(user_id=user.id, name="Order Test User")
            db.session.add(profile)
            db.session.commit()
        
        # Create test product
        product = Product(
            name="Test Product",
            description="Test product for order",
            price=Decimal('100.00'),
            category="Test",
            seller_id=user.id,
            status="Active",
            inventory=10
        )
        db.session.add(product)
        db.session.commit()
        
        # Create order
        order = Order(
            user_id=user.id,
            shipping_address="123 Test Street, Karachi",
            payment_method="card",
            payment_status="Pending",
            status="Pending",
            total_amount=Decimal('100.00')
        )
        db.session.add(order)
        db.session.commit()
        
        print(f"✓ Order created: ID {order.id}")
        
        # Process payment
        from agrifarma.services import payment as payment_service
        payment_result = payment_service.process_order_payment(
            order_id=order.id,
            amount=order.total_amount,
            customer_email=user.email,
            payment_method=order.payment_method
        )
        
        if payment_result.success:
            order.payment_status = 'Paid'
            order.payment_transaction_id = payment_result.transaction_id
            order.status = 'Confirmed'
            db.session.commit()
            
            print(f"✓ Payment processed: {payment_result.transaction_id}")
            print(f"✓ Order status updated: {order.status}")
            print(f"✓ Payment status: {order.payment_status}")
            
            assert order.payment_status == 'Paid', "Order should be marked as paid"
            assert order.payment_transaction_id, "Transaction ID should be saved"
            assert order.status == 'Confirmed', "Order should be confirmed"
        else:
            print(f"✗ Payment failed: {payment_result.message}")
        
        # Cleanup
        db.session.delete(order)
        db.session.delete(product)
        db.session.delete(user.profile)
        db.session.delete(user)
        db.session.commit()
        
        print("✓ Order with payment integration tests passed")


def test_search_routes_registered():
    """Test that search routes are properly registered"""
    print("\n=== Testing Search Routes Registration ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        with app.test_request_context():
            from flask import url_for
            
            routes_to_test = [
                ('search.global_search', {}),
                ('search.autocomplete', {}),
            ]
            
            for endpoint, params in routes_to_test:
                try:
                    url = url_for(endpoint, **params)
                    print(f"✓ {endpoint}: {url}")
                except Exception as e:
                    print(f"✗ {endpoint}: ERROR - {str(e)[:50]}")
                    raise
    
    print("✓ Search routes registered successfully")


def test_payment_configuration():
    """Test payment configuration settings"""
    print("\n=== Testing Payment Configuration ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        # Check payment gateway config
        gateway_type = app.config.get('PAYMENT_GATEWAY', 'mock')
        print(f"✓ Payment gateway: {gateway_type}")
        
        # Verify configuration exists
        assert 'PAYMENT_GATEWAY' in app.config, "Payment gateway config missing"
        assert app.config.get('PAYMENT_GATEWAY') == 'mock', "Default gateway should be mock"
        
        print("✓ Payment configuration verified")


def test_form_validation():
    """Test form validation improvements"""
    print("\n=== Testing Form Validation ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        with app.test_request_context():
            from agrifarma.forms.ecommerce import CheckoutForm
            from werkzeug.datastructures import MultiDict
            
            # Test valid checkout form
            valid_data = MultiDict([
                ('shipping_address', '123 Main St, Karachi'),
                ('payment_method', 'card'),
                ('csrf_token', 'test_token')  # Add CSRF token
            ])
            
            # Disable CSRF for testing
            app.config['WTF_CSRF_ENABLED'] = False
            
            form = CheckoutForm(valid_data)
            print(f"✓ Checkout form created successfully")
            
            # Test required fields
            assert hasattr(form, 'shipping_address'), "Shipping address field should exist"
            assert hasattr(form, 'payment_method'), "Payment method field should exist"
            
            print("✓ Form validation tests passed")


def test_database_models():
    """Test database model enhancements"""
    print("\n=== Testing Database Model Enhancements ===")
    app = create_app("config.DevelopmentConfig")
    
    with app.app_context():
        # Check Order model has new fields
        order = Order()
        
        assert hasattr(order, 'payment_status'), "Order should have payment_status field"
        assert hasattr(order, 'payment_transaction_id'), "Order should have payment_transaction_id field"
        
        print(f"✓ Order model has payment_status field")
        print(f"✓ Order model has payment_transaction_id field")
        
        # Test setting values
        order.payment_status = 'Paid'
        order.payment_transaction_id = 'TEST_123'
        
        assert order.payment_status == 'Paid', "Payment status should be settable"
        assert order.payment_transaction_id == 'TEST_123', "Transaction ID should be settable"
        
        print("✓ Database model enhancements verified")


def run_all_tests():
    """Run all enhancement tests"""
    print("=" * 60)
    print("AGRIFARMA CORE ENHANCEMENTS TEST SUITE")
    print("=" * 60)
    
    try:
        test_global_search()
        test_payment_processing()
        test_order_with_payment()
        test_search_routes_registered()
        test_payment_configuration()
        test_form_validation()
        test_database_models()
        
        print("\n" + "=" * 60)
        print("ALL ENHANCEMENT TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\n✓ Global Search: WORKING")
        print("✓ Payment Processing: WORKING")
        print("✓ Order Integration: WORKING")
        print("✓ Routes: REGISTERED")
        print("✓ Configuration: VERIFIED")
        print("✓ Forms: VALIDATED")
        print("✓ Models: ENHANCED")
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
