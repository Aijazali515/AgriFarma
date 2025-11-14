#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Complete testing of all pages and recent changes."""

from agrifarma import create_app
from agrifarma.models.blog import BlogPost
from agrifarma.models.ecommerce import Product

app = create_app("config.DevelopmentConfig")

print("\n" + "="*80)
print("COMPLETE TESTING - All Pages & Recent Changes")
print("="*80 + "\n")

# Test all major routes
print("1. TESTING ALL ROUTES:")
print("-" * 80)

with app.test_client() as client:
    routes = [
        ('/', 'Home/Dashboard'),
        ('/shop', 'Shop Page'),
        ('/blog', 'Knowledge Base'),
        ('/blog/post/1', 'Article Detail'),
        ('/forum', 'Forum'),
        ('/consultants', 'Consultants'),
    ]
    
    all_passed = True
    for route, name in routes:
        try:
            response = client.get(route, follow_redirects=True)
            status = "PASS" if response.status_code == 200 else "FAIL"
            print(f"[{status}] {name:25s} - Status: {response.status_code}")
            
            if response.status_code != 200:
                all_passed = False
        except Exception as e:
            print(f"[FAIL] {name:25s} - Error: {str(e)[:50]}")
            all_passed = False

# Test Shop Page Specifically
print("\n2. SHOP PAGE DETAILED TEST:")
print("-" * 80)

with app.test_client() as client:
    response = client.get('/shop')
    if response.status_code == 200:
        content = response.data.decode('utf-8')
        
        checks = [
            ('Agri Marketplace title', 'Agri Marketplace' in content),
            ('Product images reference', 'uploads/products/' in content),
            ('Shop hero section', 'af-shop-hero' in content),
        ]
        
        for check_name, passed in checks:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {check_name}")
    else:
        print(f"[FAIL] Could not load shop page - Status: {response.status_code}")

# Test Knowledge Base
print("\n3. KNOWLEDGE BASE DETAILED TEST:")
print("-" * 80)

with app.test_client() as client:
    response = client.get('/blog')
    if response.status_code == 200:
        content = response.data.decode('utf-8')
        
        checks = [
            ('KB title present', 'Knowledge Base' in content),
            ('Article images reference', 'uploads/blog/' in content),
            ('KB hero section', 'af-kb-hero' in content),
            ('HD background image', 'kb_hero_bg.jpg' in content),
        ]
        
        for check_name, passed in checks:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {check_name}")
    else:
        print(f"[FAIL] Could not load KB page - Status: {response.status_code}")

# Test Database
print("\n4. DATABASE CONTENT:")
print("-" * 80)

with app.app_context():
    blog_count = BlogPost.query.count()
    product_count = Product.query.count()
    
    blogs_with_images = BlogPost.query.filter(BlogPost.media_files.isnot(None)).count()
    products_with_images = Product.query.filter(Product.images.isnot(None)).count()
    
    print(f"[INFO] Total blog articles: {blog_count}")
    print(f"[INFO] Articles with images: {blogs_with_images}/{blog_count}")
    print(f"[INFO] Total products: {product_count}")
    print(f"[INFO] Products with images: {products_with_images}/{product_count}")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80 + "\n")
