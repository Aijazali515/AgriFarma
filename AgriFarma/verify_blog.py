#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify blog articles with images in database."""

from agrifarma import create_app
from agrifarma.models.blog import BlogPost

app = create_app("config.DevelopmentConfig")

with app.app_context():
    articles = BlogPost.query.limit(10).all()
    print(f"\n📚 Sample Blog Articles with Images:\n")
    print("-" * 80)
    for p in articles:
        print(f"ID: {p.id:3d} | {p.title[:40]:42s} | Image: {p.media_files}")
    print("-" * 80)
    print(f"\n✅ Total articles in database: {BlogPost.query.count()}")
