#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test basic routes to verify they work."""

from agrifarma import create_app

app = create_app("config.DevelopmentConfig")

print("\n🔍 Testing Routes:\n")
print("-" * 80)

with app.test_client() as client:
    routes_to_test = [
        ('/', 'Home Page'),
        ('/shop', 'Shop Page'),
        ('/blog', 'Blog/Knowledge Base'),
        ('/blog/post/1', 'Blog Detail Page'),
        ('/forum', 'Forum Page'),
        ('/consultants', 'Consultants Page'),
    ]
    
    for route, name in routes_to_test:
        try:
            response = client.get(route, follow_redirects=True)
            status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{status} | {name:25s} | {route}")
        except Exception as e:
            print(f"❌ | {name:25s} | {route} | Error: {str(e)[:50]}")

print("-" * 80)
print("\n✅ Route testing complete!")
