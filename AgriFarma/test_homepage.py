#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the homepage to see the actual error."""

import requests

try:
    response = requests.get('http://127.0.0.1:5000/', timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("\n=== ERROR RESPONSE ===")
        print(response.text[:2000])  # First 2000 chars
    else:
        print("\n=== SUCCESS ===")
        print(f"Content length: {len(response.text)} bytes")
except Exception as e:
    print(f"Request failed: {e}")
