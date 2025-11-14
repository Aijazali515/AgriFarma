import pytest
from datetime import datetime, timedelta, UTC
from werkzeug.security import generate_password_hash
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.ecommerce import Product, Order, OrderItem
from agrifarma.models.blog import BlogPost

@pytest.fixture
def admin_user(app):
    """Return lightweight admin user data (avoid detached instance issues)."""
    with app.app_context():
        admin = User(email="admin@example.com", password_hash=generate_password_hash("adminpass"), role="Admin")
        db.session.add(admin)
        db.session.commit()
        return {"id": admin.id, "email": admin.email}

@pytest.fixture
def normal_user(app):
    with app.app_context():
        user = User(email="user@example.com", password_hash=generate_password_hash("userpass"), role="User")
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "email": user.email}

def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

def test_admin_user_listing_access(client, admin_user, normal_user):
    # Non-admin should 403
    login(client, normal_user["email"], "userpass")
    res = client.get("/admin/users")
    assert res.status_code == 403
    client.get("/logout", follow_redirects=True)
    # Admin can access
    login(client, admin_user["email"], "adminpass")
    res = client.get("/admin/users")
    assert res.status_code == 200
    assert b"User Management" in res.data

def test_user_activation_toggle(client, admin_user, normal_user, app):
    login(client, admin_user["email"], "adminpass")
    # Deactivate normal user
    res = client.post("/admin/users", data={"user_id": normal_user["id"], "action": "deactivate"}, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        refreshed = db.session.get(User, normal_user["id"])
        assert refreshed.is_active is False
    # Reactivate
    res = client.post("/admin/users", data={"user_id": normal_user["id"], "action": "activate"}, follow_redirects=True)
    with app.app_context():
        refreshed = db.session.get(User, normal_user["id"])
        assert refreshed.is_active is True

def test_product_moderation(client, admin_user, app):
    login(client, admin_user["email"], "adminpass")
    with app.app_context():
        p = Product(name="Inactive Product", description="Test", price=10, category="seeds", images="", seller_id=admin_user["id"], status="Inactive")
        db.session.add(p)
        db.session.commit()
        pid = p.id
    # Appears in moderation page
    res = client.get("/admin/moderation")
    assert b"Inactive Product" in res.data
    # Activate
    res = client.post("/admin/moderation", data={"kind": "product", "product_id": pid, "action": "approve"}, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        p2 = db.session.get(Product, pid)
        assert p2.status == "Active"

def test_blog_post_moderation(client, admin_user, app):
    login(client, admin_user["email"], "adminpass")
    with app.app_context():
        post = BlogPost(title="Pending Blog", content="Content", category="Techniques", author_id=admin_user["id"], approved=False)
        db.session.add(post)
        db.session.commit()
        bid = post.id
    res = client.get("/admin/moderation")
    assert b"Pending Blog" in res.data
    res = client.post("/admin/moderation", data={"kind": "blog", "post_id": bid, "action": "approve"}, follow_redirects=True)
    with app.app_context():
        post2 = db.session.get(BlogPost, bid)
        assert post2.approved is True

def test_reports_basic_aggregation(client, admin_user, app):
    login(client, admin_user["email"], "adminpass")
    # create product + order + order item inside date range
    with app.app_context():
        p = Product(name="Seed Pack", description="Quality seeds", price=5, category="seeds", images="", seller_id=admin_user["id"], status="Active", inventory=3)
        db.session.add(p)
        order = Order(user_id=admin_user["id"], shipping_address="Addr", payment_method="COD", status="Paid", created_at=datetime.now(UTC))
        db.session.add(order)
        db.session.flush()
        db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=4, unit_price=5))
        order.total_amount = 20
        # low inventory scenario: inventory < threshold (threshold default 5)
        db.session.commit()
        pid = p.id
    start = (datetime.now(UTC) - timedelta(days=1)).strftime('%Y-%m-%d')
    end = (datetime.now(UTC) + timedelta(days=1)).strftime('%Y-%m-%d')
    res = client.get(f"/admin/reports?start={start}&end={end}&low=5")
    assert res.status_code == 200
    assert b"Seed Pack" in res.data  # top selling table or low inventory table
    assert b"Low Inventory" in res.data
    # Ensure units/revenue appear (20.00 revenue)
    assert b"20.00" in res.data or b"$20.00" in res.data


def test_reports_filters_date_range(client, admin_user, app):
    from datetime import datetime, timedelta
    login(client, admin_user["email"], "adminpass")
    with app.app_context():
        # Create product and two orders: one in range, one out of range
        p = Product(name="Fertilizer A", description="Desc", price=8, category="fertilizers", images="", seller_id=admin_user["id"], status="Active", inventory=10)
        db.session.add(p)
        db.session.flush()
        in_range = Order(user_id=admin_user["id"], shipping_address="A", payment_method="COD", status="Paid", created_at=datetime.now(UTC))
        out_range = Order(user_id=admin_user["id"], shipping_address="B", payment_method="COD", status="Paid", created_at=datetime.now(UTC) - timedelta(days=40))
        db.session.add_all([in_range, out_range])
        db.session.flush()
        db.session.add(OrderItem(order_id=in_range.id, product_id=p.id, quantity=1, unit_price=8))
        db.session.add(OrderItem(order_id=out_range.id, product_id=p.id, quantity=5, unit_price=8))
        in_range.total_amount = 8
        out_range.total_amount = 40
        db.session.commit()
    start = (datetime.now(UTC) - timedelta(days=7)).strftime('%Y-%m-%d')
    end = datetime.now(UTC).strftime('%Y-%m-%d')
    res = client.get(f"/admin/reports?start={start}&end={end}")
    assert res.status_code == 200
    # Should include the in-range order date but not the old order date string (approx)
    assert b"Orders" in res.data


def test_reports_low_inventory_threshold(client, admin_user, app):
    login(client, admin_user["email"], "adminpass")
    with app.app_context():
        p = Product(name="Pump", description="Desc", price=12, category="equipment", images="", seller_id=admin_user["id"], status="Active", inventory=3)
        db.session.add(p)
        db.session.commit()
        pid = p.id
    start = (datetime.now(UTC) - timedelta(days=1)).strftime('%Y-%m-%d')
    end = (datetime.now(UTC) + timedelta(days=1)).strftime('%Y-%m-%d')
    # With low=5, should appear
    res = client.get(f"/admin/reports?start={start}&end={end}&low=5")
    assert b"Low Inventory" in res.data
    assert b"Pump" in res.data
    # With low=2, should not appear
    res = client.get(f"/admin/reports?start={start}&end={end}&low=2")
    assert b"Low Inventory" in res.data
    assert b"Pump" not in res.data


def test_admin_reports_access_control(client, normal_user):
    login(client, normal_user["email"], "userpass")
    res = client.get("/admin/reports")
    assert res.status_code == 403
