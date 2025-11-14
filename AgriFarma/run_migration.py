#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple script to run database migrations
"""
from agrifarma import create_app
from flask_migrate import upgrade

# Create Flask app and push app context
app = create_app()
with app.app_context():
    # Run migration
    print("Running database migration...")
    upgrade()
    print("Migration completed successfully!")
