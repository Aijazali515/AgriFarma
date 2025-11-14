#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make a request to capture the full error traceback."""

import sys
import traceback
from agrifarma import create_app

app = create_app()

# Simulate a request
with app.test_client() as client:
    try:
        print("Making request to /...")
        response = client.get('/')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 500:
            print("\n" + "="*70)
            print("ERROR RESPONSE:")
            print("="*70)
            print(response.data.decode('utf-8'))
        else:
            print("\n✓ SUCCESS - Homepage loaded")
            print(f"Content length: {len(response.data)} bytes")
            
    except Exception as e:
        print(f"\n✗ EXCEPTION: {e}")
        print("\n" + "="*70)
        print("FULL TRACEBACK:")
        print("="*70)
        traceback.print_exc()
        sys.exit(1)
