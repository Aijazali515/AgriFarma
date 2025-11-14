#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final verification of all implemented features."""

from agrifarma import create_app
from agrifarma.models.blog import BlogPost
from agrifarma.models.ecommerce import Product
import os

app = create_app("config.DevelopmentConfig")

print("\n" + "="*80)
print("FINAL VERIFICATION - All Implemented Changes")
print("="*80 + "\n")

results = []

# 1. Check Database
with app.app_context():
    blog_count = BlogPost.query.count()
    product_count = Product.query.count()
    
    results.append(("Database - Blog Posts", blog_count > 0, f"{blog_count} articles"))
    results.append(("Database - Products", product_count > 0, f"{product_count} products"))
    
    # Check images in database
    blogs_with_images = BlogPost.query.filter(BlogPost.media_files.isnot(None)).count()
    products_with_images = Product.query.filter(Product.images.isnot(None)).count()
    
    results.append(("Blog articles have images", blogs_with_images > 0, f"{blogs_with_images}/{blog_count}"))
    results.append(("Products have images", products_with_images > 0, f"{products_with_images}/{product_count}"))

# 2. Check Image Files
blog_dir = "agrifarma/static/uploads/blog"
product_dir = "agrifarma/static/uploads/products"

blog_imgs = len([f for f in os.listdir(blog_dir) if f.endswith('.jpg')]) if os.path.exists(blog_dir) else 0
product_imgs = len([f for f in os.listdir(product_dir) if f.endswith('.jpg')]) if os.path.exists(product_dir) else 0

results.append(("Blog image files on disk", blog_imgs >= 10, f"{blog_imgs} images"))
results.append(("Product image files on disk", product_imgs >= 10, f"{product_imgs} images"))

# 3. Check Routes
with app.test_client() as client:
    routes = [
        ('/shop', 'Shop Page'),
        ('/blog', 'Blog List'),
        ('/blog/post/1', 'Blog Detail'),
    ]
    
    for route, name in routes:
        response = client.get(route, follow_redirects=True)
        results.append((f"Route: {name}", response.status_code == 200, f"Status {response.status_code}"))

# 4. Check Profile Page Fix
profile_template = "agrifarma/templates/profile_view.html"
if os.path.exists(profile_template):
    with open(profile_template, 'r', encoding='utf-8') as f:
        content = f.read()
        has_fix = '#212529' in content and '#6c757d' in content
        results.append(("Profile text visibility fix", has_fix, "CSS colors updated"))

# 5. Check CSRF Fix
blog_detail_template = "agrifarma/templates/blog_detail.html"
if os.path.exists(blog_detail_template):
    with open(blog_detail_template, 'r', encoding='utf-8') as f:
        content = f.read()
        has_csrf = 'csrf_token' in content
        results.append(("Like button CSRF protection", has_csrf, "Token present"))

# Print Results
print("TEST RESULTS:")
print("-" * 80)
for test_name, passed, detail in results:
    status = "PASS" if passed else "FAIL"
    indicator = "+" if passed else "-"
    print(f"[{status}] {indicator} {test_name:40s} | {detail}")

# Summary
total = len(results)
passed = sum(1 for _, p, _ in results if p)
failed = total - passed

print("-" * 80)
print(f"\nSUMMARY: {passed}/{total} tests passed")
if failed == 0:
    print("SUCCESS: All changes implemented and verified!")
else:
    print(f"WARNING: {failed} test(s) failed - needs attention")
print("="*80 + "\n")
