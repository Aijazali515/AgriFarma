#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add display_picture column to profiles table directly using SQLite
"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'agrifarma.db')

print(f"Connecting to database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'display_picture' in columns:
        print("✓ Column 'display_picture' already exists in profiles table")
    else:
        # Add the column
        print("Adding 'display_picture' column to profiles table...")
        cursor.execute("ALTER TABLE profiles ADD COLUMN display_picture VARCHAR(256)")
        conn.commit()
        print("✓ Column 'display_picture' added successfully!")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(profiles)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nCurrent columns in profiles table: {', '.join(columns)}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("\nDatabase connection closed.")
