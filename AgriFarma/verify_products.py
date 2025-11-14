#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify product images in database."""

from agrifarma import create_app
from agrifarma.models.ecommerce import Product

app = create_app("config.DevelopmentConfig")

with app.app_context():
    products = Product.query.limit(10).all()
    print(f"\n📦 Sample Products with Images:\n")
    print("-" * 80)
    for p in products:
        print(f"ID: {p.id:3d} | {p.name:35s} | Image: {p.images}")
    print("-" * 80)
    print(f"\n✅ Total products in database: {Product.query.count()}")
