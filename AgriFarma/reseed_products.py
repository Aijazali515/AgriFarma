#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reseed database with real product images."""

from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.seed_data import clear_all, seed_all

app = create_app("config.DevelopmentConfig")

with app.app_context():
    print("🧹 Clearing existing data...")
    clear_all()
    print("✅ Data cleared.")
    
    print("🌱 Seeding database with new data (using real product images)...")
    seed_all()
    print("✅ Database seeded successfully!")
    print("\n📦 Products now have real images from uploads/products/")
