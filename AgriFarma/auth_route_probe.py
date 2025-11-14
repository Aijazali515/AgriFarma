"""Authenticate as user/admin and probe protected & dynamic routes for 200 status codes.
Run: python auth_route_probe.py
"""
from agrifarma import create_app
from test_config import TestConfig
from agrifarma.extensions import db
from agrifarma.models.forum import Thread
from agrifarma.models.blog import BlogPost
from agrifarma.models.consultancy import Consultant
from agrifarma.models.ecommerce import Product

app = create_app(TestConfig)

ADMIN_EMAIL = 'admin@example.com'
USER_EMAIL = 'user@example.com'
PASSWORD = 'Pass1234!'

PROTECTED_ROUTES = [
    ('FORUM_NEW_THREAD', '/forum/new'),
    ('BLOG_NEW', '/blog/new'),
    ('CONSULTANT_REGISTER', '/consultant/register'),
    ('CART_VIEW', '/cart'),
]
ADMIN_ROUTES = [
    ('ADMIN_DASHBOARD_SHOP', '/admin/shop'),
]

with app.app_context():
    thread = Thread.query.order_by(Thread.created_at.asc()).first()
    blog = BlogPost.query.order_by(BlogPost.created_at.asc()).first()
    consultant = Consultant.query.order_by(Consultant.created_at.asc()).first()
    product = Product.query.order_by(Product.created_at.asc()).first()

DYNAMIC = [
    ('THREAD_VIEW', f'/forum/thread/{thread.id}' if thread else None),
    ('BLOG_DETAIL', f'/blog/post/{blog.id}' if blog else None),
    ('CONSULTANT_PROFILE', f'/consultant/{consultant.id}' if consultant else None),
    ('PRODUCT_DETAIL', f'/product/{product.id}' if product else None),
]
DYNAMIC = [r for r in DYNAMIC if r[1]]


def login(client, email, password):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

print('=== USER SESSION TESTS ===')
with app.test_client() as client:
    rv = login(client, USER_EMAIL, PASSWORD)
    print('Login user status:', rv.status_code)
    for name, path in PROTECTED_ROUTES:
        resp = client.get(path)
        print(f'{name:20} {resp.status_code}')
    for name, path in DYNAMIC:
        resp = client.get(path)
        print(f'{name:20} {resp.status_code}')

print('\n=== ADMIN SESSION TESTS ===')
with app.test_client() as client:
    rv = login(client, ADMIN_EMAIL, PASSWORD)
    print('Login admin status:', rv.status_code)
    for name, path in PROTECTED_ROUTES + ADMIN_ROUTES:
        resp = client.get(path)
        print(f'{name:20} {resp.status_code}')
    for name, path in DYNAMIC:
        resp = client.get(path)
        print(f'{name:20} {resp.status_code}')

print('\nAuth route probe complete.')
