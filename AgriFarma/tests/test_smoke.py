"""High-level smoke tests for critical flows.

Covers:
 - Password reset token lifecycle
 - Forum post like toggle
 - Blog post like toggle
 - Messaging send & read flag
 - Date-filtered order history (user side)
 - Sales report filter (admin side)

Relies on in-memory SQLite and existing blueprints/routes.
"""
from datetime import datetime, UTC, timedelta
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.password_reset import PasswordResetToken
from agrifarma.models.forum import Thread, Post, Category
from agrifarma.models.likes import PostLike, BlogLike
from agrifarma.models.blog import BlogPost
from agrifarma.models.message import Message
from agrifarma.models.ecommerce import Product, Order, OrderItem
from werkzeug.security import generate_password_hash


def create_user(email: str, role: str = "User") -> User:
    u = User(email=email, password_hash=generate_password_hash("pass"), role=role)
    db.session.add(u)
    db.session.commit()
    return u


def auth_login(client, email: str, password: str = "pass"):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)


def test_password_reset_token_validity(app):
    with app.app_context():
        user = create_user('reset@example.com')
        token = PasswordResetToken.create_token(user.id, validity_hours=1)
        assert token.is_valid() is True
        # Force expiry (use utcnow for naive datetime)
        token.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.session.commit()
        assert token.is_valid() is False
        # New token then mark used
        token2 = PasswordResetToken.create_token(user.id, validity_hours=1)
        assert token2.is_valid() is True
        token2.mark_used()
        assert token2.is_valid() is False


def test_forum_post_like_toggle(app, client):
    with app.app_context():
        user = create_user('forum@example.com')
        auth_login(client, 'forum@example.com')
        cat = Category(name='General')
        db.session.add(cat); db.session.commit()
        thread = Thread(title='Hello', category_id=cat.id, author_id=user.id)
        db.session.add(thread); db.session.commit()
        post = Post(thread_id=thread.id, author_id=user.id, content='First post')
        db.session.add(post); db.session.commit()
        # Toggle like
        r1 = client.post(f'/forum/post/{post.id}/like', follow_redirects=True)
        assert r1.status_code in (200, 302)
        assert PostLike.query.filter_by(post_id=post.id, user_id=user.id).count() == 1
        # Toggle again (should remove)
        r2 = client.post(f'/forum/post/{post.id}/like', follow_redirects=True)
        assert r2.status_code in (200, 302)
        assert PostLike.query.filter_by(post_id=post.id, user_id=user.id).count() == 0


def test_blog_post_like_toggle(app, client):
    with app.app_context():
        author = create_user('author@example.com')
        auth_login(client, 'author@example.com')
        post = BlogPost(title='Knowledge', content='Content', category='Techniques', author_id=author.id, approved=True)
        db.session.add(post); db.session.commit()
        r1 = client.post(f'/blog/post/{post.id}/like', follow_redirects=True)
        assert r1.status_code in (200, 302)
        assert BlogLike.query.filter_by(blog_id=post.id, user_id=author.id).count() == 1
        r2 = client.post(f'/blog/post/{post.id}/like', follow_redirects=True)
        assert r2.status_code in (200, 302)
        assert BlogLike.query.filter_by(blog_id=post.id, user_id=author.id).count() == 0


def test_messaging_send_and_read(app, client):
    with app.app_context():
        from agrifarma.models.consultancy import Consultant
        sender = create_user('sender@example.com')
        receiver = create_user('receiver@example.com', role='Consultant')
        # Create consultant record
        consultant = Consultant(
            user_id=receiver.id,
            category='Crop Management',
            expertise_level='Expert',
            contact_email='receiver@example.com',
            approval_status='Approved'
        )
        db.session.add(consultant)
        db.session.commit()
        auth_login(client, 'sender@example.com')
        # Messaging route expects consultant id
        resp = client.post(
            f'/consultancy/message/{consultant.id}',
            data={'subject': 'Hello there', 'content': 'This is a proper message for the consultant.'},
            follow_redirects=True
        )
        assert resp.status_code in (200, 302)
        msg = Message.query.filter_by(sender_id=sender.id, receiver_id=receiver.id).first()
        assert msg is not None
        assert msg.read is False
        # Simulate receiver viewing message (login as receiver)
        client.get('/logout')
        auth_login(client, 'receiver@example.com')
        view = client.get(f'/consultancy/message/{msg.id}', follow_redirects=True)
        assert view.status_code == 200
        db.session.refresh(msg)
        assert msg.read is True


def test_order_history_date_filter(app, client):
    with app.app_context():
        user = create_user('buyer@example.com')
        auth_login(client, 'buyer@example.com')
        product = Product(name='Seeds', description='Pack', price=10.0, category='Agri', images='', inventory=100, seller_id=user.id, status='Active')
        db.session.add(product); db.session.commit()
        # Create two orders different dates
        o1 = Order(user_id=user.id, status='Completed', shipping_address='123 St', payment_method='COD')
        db.session.add(o1); db.session.commit()
        oi1 = OrderItem(order_id=o1.id, product_id=product.id, quantity=2, unit_price=10.0)
        db.session.add(oi1); db.session.commit()
        o2 = Order(user_id=user.id, status='Completed', shipping_address='123 St', payment_method='COD')
        db.session.add(o2); db.session.commit()
        oi2 = OrderItem(order_id=o2.id, product_id=product.id, quantity=1, unit_price=10.0)
        db.session.add(oi2); db.session.commit()
        # Manually adjust created_at to simulate different days
        o1.created_at = datetime.utcnow() - timedelta(days=5)
        o2.created_at = datetime.utcnow() - timedelta(days=1)
        db.session.commit()
        start = (datetime.utcnow() - timedelta(days=2)).date().isoformat()
        resp = client.get(f'/orders?date_from={start}')
        assert resp.status_code == 200
        # Should include only the recent order (o2): ensure o2 present and o1 absent by checking order IDs in template
        html = resp.get_data(as_text=True)
        # Look for unique identifier "Order #2" vs "Order #1"
        assert f'Order #{o2.id}' in html
        assert f'Order #{o1.id}' not in html


def test_sales_report_date_filter(app, client):
    with app.app_context():
        admin = create_user('admin@example.com', role='Admin')
        auth_login(client, 'admin@example.com')
        product = Product(name='Fertilizer', description='Bag', price=25.0, category='Agri', images='', inventory=50, seller_id=admin.id, status='Active')
        db.session.add(product); db.session.commit()
        order = Order(user_id=admin.id, status='Completed', shipping_address='123 St', payment_method='COD')
        db.session.add(order); db.session.commit()
        oi = OrderItem(order_id=order.id, product_id=product.id, quantity=3, unit_price=25.0)
        db.session.add(oi); db.session.commit()
        order.created_at = datetime.utcnow() - timedelta(days=3)
        db.session.commit()
        start = (datetime.utcnow() - timedelta(days=4)).date().isoformat()
        end = (datetime.utcnow() - timedelta(days=2)).date().isoformat()
        resp = client.get(f'/admin/reports?start={start}&end={end}')
        assert resp.status_code == 200
        # Product name should appear in report
        assert 'Fertilizer' in resp.get_data(as_text=True)
