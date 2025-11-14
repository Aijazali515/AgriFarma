#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix background image filenames to match template references."""

import os
from pathlib import Path

bg_dir = Path("agrifarma/static/img/backgrounds")

# Map of current files to expected names
renames = {
    "admin_bg.jpg.jpg": "admin_bg.jpg",
    "forum_bg.jpg.jpg": "forum_bg.jpg",
    "shop_bg.jpg.jpg": "shop_bg.jpg",
    "consultancy_bg.jpg.jpg": "consultant_bg.jpg",
    "home_bg.jpg.png": "home_bg.jpg",
}

print("Fixing background image filenames...")
print("=" * 60)

for old_name, new_name in renames.items():
    old_path = bg_dir / old_name
    new_path = bg_dir / new_name
    
    if old_path.exists():
        if new_path.exists():
            print(f"✓ {new_name} already exists, skipping {old_name}")
        else:
            old_path.rename(new_path)
            print(f"✓ Renamed {old_name} → {new_name}")
    else:
        print(f"- {old_name} not found (may already be renamed)")

print("=" * 60)
print("\nVerifying final filenames:")
expected_files = ["admin_bg.jpg", "forum_bg.jpg", "shop_bg.jpg", "consultant_bg.jpg", "home_bg.jpg", "blog_bg.jpg"]

for filename in sorted(bg_dir.iterdir()):
    status = "✓" if filename.name in expected_files else "?"
    print(f"{status} {filename.name}")

print("\nDone!")
