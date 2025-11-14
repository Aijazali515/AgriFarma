"""Probe all major AgriFarma routes and report status codes / errors.
Run: python route_probe.py
"""
from agrifarma import create_app
from agrifarma.routes.main import bp as main_bp  # noqa: F401 (ensure imported)

from run import DefaultConfig

app = create_app(DefaultConfig)

ROUTES = [
    ('HOME', '/'),
    ('FORUM_INDEX', '/forum/'),
    ('FORUM_NEW_THREAD', '/forum/new'),
    # thread view will be probed dynamically if any thread exists
    ('BLOG_LIST', '/blog/'),
    # blog detail dynamic later
    ('BLOG_NEW', '/blog/new'),
    ('CONSULTANTS_LIST', '/consultants'),
    ('CONSULTANT_REGISTER', '/consultant/register'),
    ('SHOP_LIST', '/shop'),
    ('CART_VIEW', '/cart'),
    ('ADMIN_DASHBOARD', '/admin/'),
]

from agrifarma.extensions import db
from agrifarma.models.forum import Thread
from agrifarma.models.blog import BlogPost

extra_dynamic = []
with app.app_context():
    first_thread = Thread.query.order_by(Thread.created_at.desc()).first()
    if first_thread:
        extra_dynamic.append(('FORUM_THREAD_VIEW', f'/forum/thread/{first_thread.id}'))
    first_post = BlogPost.query.filter_by(approved=True).order_by(BlogPost.created_at.desc()).first()
    if first_post:
        extra_dynamic.append(('BLOG_DETAIL', f'/blog/post/{first_post.id}'))

ALL = ROUTES + extra_dynamic

print('Probing routes...')

errors = []

with app.test_client() as client:
    for name, path in ALL:
        try:
            resp = client.get(path)
            print(f'{name:22} {path:30} -> {resp.status_code}')
            if resp.status_code >= 400:
                errors.append((name, path, resp.status_code, resp.data[:300]))
        except Exception as e:  # capture internal errors
            errors.append((name, path, 'EXCEPTION', str(e)))
            print(f'{name:22} {path:30} !! EXCEPTION {e}')

if errors:
    print('\nFailures/Exceptions:')
    for err in errors:
        print(err)
else:
    print('\nAll probed routes returned 2xx/3xx status codes.')
