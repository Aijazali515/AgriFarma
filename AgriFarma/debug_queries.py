#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug the homepage error by testing the route logic."""

from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.blog import BlogPost
from agrifarma.models.consultancy import Consultant
from agrifarma.models.ecommerce import Product, Order
from agrifarma.models.forum import Thread
from sqlalchemy import func

app = create_app()

with app.app_context():
    try:
        print("Testing database queries...")
        print("="*60)
        
        # Test queries from main.py
        users_count = db.session.query(func.count(User.id)).scalar() or 0
        print(f"✓ Users count: {users_count}")
        
        products_count = db.session.query(func.count(Product.id)).scalar() or 0
        print(f"✓ Products count: {products_count}")
        
        orders_count = db.session.query(func.count(Order.id)).scalar() or 0
        print(f"✓ Orders count: {orders_count}")
        
        pending_posts = BlogPost.query.filter_by(approved=False).count()
        print(f"✓ Pending posts: {pending_posts}")
        
        # Recent users
        recent_users = User.query.order_by(User.join_date.desc()).limit(10).all()
        print(f"✓ Recent users: {len(recent_users)}")
        
        # Check if users have profiles
        for user in recent_users[:3]:  # Check first 3
            has_profile = user.profile is not None
            print(f"  - User {user.email}: profile={has_profile}")
            if has_profile:
                print(f"    Full name: {user.profile.full_name}")
        
        # Pending blog posts
        pending_blog_posts = BlogPost.query.filter_by(approved=False).order_by(BlogPost.created_at.desc()).limit(5).all()
        print(f"✓ Pending blog posts: {len(pending_blog_posts)}")
        
        # Forum threads
        forum_threads = db.session.query(func.count(Thread.id)).scalar() or 0
        print(f"✓ Forum threads: {forum_threads}")
        
        # Consultants
        consultants_count = Consultant.query.filter_by(approval_status='Approved').count()
        print(f"✓ Consultants: {consultants_count}")
        
        print("\n" + "="*60)
        print("ALL QUERIES SUCCESSFUL ✓")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
