"""Seed minimal sample data for AgriFarma: one user, one admin, one thread, blog post, consultant, product.
Run with: python seed_data.py
"""
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash

from agrifarma import create_app
from run import DefaultConfig
from agrifarma.extensions import db

from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from agrifarma.models.forum import Category, Thread, Post
from agrifarma.models.blog import BlogPost
from agrifarma.models.consultancy import Consultant
from agrifarma.models.ecommerce import Product

app = create_app(DefaultConfig)

ADMIN_EMAIL = 'admin@gmail.com'
USER_EMAIL = 'user@example.com'
DEFAULT_PASSWORD = 'Pass1234!'

with app.app_context():
    # Users
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()
    if not admin:
        admin = User(email=ADMIN_EMAIL, password_hash=generate_password_hash(DEFAULT_PASSWORD), role='Admin', is_active=True)
        db.session.add(admin)
        db.session.flush()
        db.session.add(Profile(user_id=admin.id, name='Site Admin'))
    user = User.query.filter_by(email=USER_EMAIL).first()
    if not user:
        user = User(email=USER_EMAIL, password_hash=generate_password_hash(DEFAULT_PASSWORD), role='User', is_active=True)
        db.session.add(user)
        db.session.flush()
        db.session.add(Profile(user_id=user.id, name='Regular User'))

    # Forum category/thread/post
    general = Category.query.filter_by(name='General').first()
    if not general:
        general = Category(name='General')
        db.session.add(general)
        db.session.flush()
    thread = Thread.query.filter_by(title='Welcome to AgriFarma').first()
    if not thread:
        thread = Thread(title='Welcome to AgriFarma', category_id=general.id, author_id=user.id)
        db.session.add(thread)
        db.session.flush()
        db.session.add(Post(thread_id=thread.id, author_id=user.id, content='First post introducing the platform.'))

    # Blog post
    post = BlogPost.query.filter_by(title='Soil Health Basics').first()
    if not post:
        post = BlogPost(title='Soil Health Basics', content='A short article on improving soil.', category='Agronomy', author_id=admin.id, tags='soil,health', approved=True)
        db.session.add(post)

    # Consultant (approved)
    consultant = Consultant.query.filter_by(user_id=admin.id).first()
    if not consultant:
        consultant = Consultant(user_id=admin.id, category='Crop Science', expertise_level='Expert', contact_email='admin@example.com', approval_status='Approved')
        db.session.add(consultant)

    # Product
    product = Product.query.filter_by(name='Organic Fertilizer').first()
    if not product:
        product = Product(name='Organic Fertilizer', description='High quality organic fertilizer.', price=19.99, category='Soil Care', images='', seller_id=admin.id, status='Active', featured=True, inventory=25)
        db.session.add(product)

    db.session.commit()
    print('Seed data applied.')
    print(f'Admin login: {ADMIN_EMAIL} / {DEFAULT_PASSWORD}')
    print(f'User  login: {USER_EMAIL} / {DEFAULT_PASSWORD}')
    print(f'Thread ID: {thread.id}, Blog Post ID: {post.id}, Consultant ID: {consultant.id}, Product ID: {product.id}')
