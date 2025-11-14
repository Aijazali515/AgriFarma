from werkzeug.security import generate_password_hash
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.ecommerce import Product, CartItem, Order, OrderItem, Review


def login_as_admin(client, app):
    with app.app_context():
        admin = User(email='admin@shop.com', password_hash=generate_password_hash('adminpass'), role='Admin')
        db.session.add(admin)
        db.session.commit()
    client.post('/login', data={'email': 'admin@shop.com', 'password': 'adminpass'}, follow_redirects=True)


def register_user(client, email='buyer@example.com'):
    data = {
        'name': 'Buyer',
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123',
        'profession': 'farmer',
        'expertise_level': 'beginner',
    }
    client.post('/register', data=data, follow_redirects=True)


def test_admin_product_crud_and_listing(client, app):
    login_as_admin(client, app)
    # create product (must include hidden fields for WTForms if any). ProductForm has CSRF disabled in tests due to WTF_CSRF_ENABLED False.
    res = client.post('/admin/shop', data={
        'name': 'Tractor', 'description': 'Heavy duty', 'price': '1200.00',
        'category': 'equipment', 'images': '', 'status': 'Active', 'featured': 'true'
    }, follow_redirects=True)
    assert b'Product created' in res.data, res.data[:400]

    # shop list shows product
    res2 = client.get('/shop?category=equipment')
    assert b'Tractor' in res2.data


def test_cart_and_checkout_flow(client, app):
    # seed admin and product
    login_as_admin(client, app)
    client.post('/admin/shop', data={
        'name': 'Seeder', 'description': 'Handy', 'price': '100.00',
        'category': 'equipment', 'images': '', 'status': 'Active', 'featured': 'false'
    }, follow_redirects=True)

    # buyer adds to cart
    register_user(client, email='buyer1@example.com')
    res = client.post('/product/1', data={'quantity': 2}, follow_redirects=True)
    assert b'Added to cart' in res.data

    # view cart and checkout
    res2 = client.get('/cart')
    assert b'Seeder' in res2.data
    res3 = client.post('/checkout', data={'shipping_address': '123 Farm Lane', 'payment_method': 'COD'}, follow_redirects=True)
    assert b'Order placed successfully' in res3.data
    # order history shows it
    res4 = client.get('/orders')
    assert b'Order #' in res4.data


def test_reviews_and_moderation(client, app):
    # seed admin and product
    login_as_admin(client, app)
    client.post('/admin/shop', data={
        'name': 'Composter', 'description': 'Organic waste', 'price': '50.00',
        'category': 'bio', 'images': '', 'status': 'Active', 'featured': 'false'
    }, follow_redirects=True)

    # buyer posts review
    register_user(client, email='buyer2@example.com')
    res = client.post('/product/1', data={'rating': 5, 'comment': 'Great!'}, follow_redirects=True)
    assert b'Review submitted' in res.data

    # admin approves
    login_as_admin(client, app)
    with app.app_context():
        rv = Review.query.first()
        rid = rv.id
    res2 = client.post(f'/admin/review/{rid}/approve', follow_redirects=True)
    assert b'Review updated' in res2.data


def test_shop_pagination_boundaries(client, app):
    # Seed many products directly
    from agrifarma.models.ecommerce import Product
    from datetime import datetime, UTC, timedelta
    with app.app_context():
        base_time = datetime.now(UTC) - timedelta(days=1)
        for i in range(1, 26):
            name = f"P{str(i).zfill(3)}"
            p = Product(name=name, description='x', price=1.0, category='testcat', images='', seller_id=None, status='Active')
            # ensure deterministic ordering by name in tests
            p.created_at = base_time
            base_time = base_time + timedelta(minutes=1)
            db.session.add(p)
        db.session.commit()

    # Page 1 should have first 12 by name (P001..P012) when sort=name
    res1 = client.get('/shop?category=testcat&sort=name&page=1')
    assert b'P001' in res1.data and b'P013' not in res1.data
    # Page 2 should have P013..P024
    res2 = client.get('/shop?category=testcat&sort=name&page=2')
    assert b'P013' in res2.data and b'P001' not in res2.data
    # Page 3 should have P025 only
    res3 = client.get('/shop?category=testcat&sort=name&page=3')
    assert b'P025' in res3.data and b'P001' not in res3.data and b'P013' not in res3.data
    # Out of range page should show no products message
    res4 = client.get('/shop?category=testcat&sort=name&page=99')
    assert b'No products found' in res4.data
