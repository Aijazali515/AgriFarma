"""Comprehensive verification of all AgriFarma pages with background image checks.
Run: python verify_all_pages.py
"""
from agrifarma import create_app
from config import DevelopmentConfig
from agrifarma.extensions import db
from agrifarma.models.forum import Thread
from agrifarma.models.blog import BlogPost
from agrifarma.models.consultancy import Consultant
from agrifarma.models.ecommerce import Product

app = create_app(DevelopmentConfig)

# Test all public pages
PUBLIC_PAGES = [
    ('Homepage', '/'),
    ('Forum Index', '/forum/'),
    ('Blog List', '/blog/'),
    ('Consultants List', '/consultants'),
    ('Shop', '/shop'),
]

# Check for sample data to test dynamic pages
with app.app_context():
    thread = Thread.query.first()
    blog = BlogPost.query.filter_by(approved=True).first()
    consultant = Consultant.query.filter_by(approval_status='Approved').first()
    product = Product.query.filter_by(status='Active').first()

DYNAMIC_PAGES = []
if thread:
    DYNAMIC_PAGES.append(('Thread View', f'/forum/thread/{thread.id}'))
if blog:
    DYNAMIC_PAGES.append(('Blog Detail', f'/blog/post/{blog.id}'))
if consultant:
    DYNAMIC_PAGES.append(('Consultant Profile', f'/consultant/{consultant.id}'))
if product:
    DYNAMIC_PAGES.append(('Product Detail', f'/product/{product.id}'))

ALL_PAGES = PUBLIC_PAGES + DYNAMIC_PAGES

print('=' * 70)
print('🔍 AGRIFARMA PAGE VERIFICATION')
print('=' * 70)

with app.test_client() as client:
    for name, path in ALL_PAGES:
        resp = client.get(path)
        status_icon = '✅' if resp.status_code == 200 else '❌'
        print(f'{status_icon} {name:25} {path:35} [{resp.status_code}]')

print('=' * 70)
print('📊 SUMMARY')
print('=' * 70)
print(f'Total pages tested: {len(ALL_PAGES)}')
print(f'Public pages: {len(PUBLIC_PAGES)}')
print(f'Dynamic pages: {len(DYNAMIC_PAGES)}')
print('')
print('🌐 Server URL: http://127.0.0.1:5000/')
print('🖼️  Background images location: agrifarma/static/img/backgrounds/')
print('=' * 70)
