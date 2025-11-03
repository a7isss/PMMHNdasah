#!/usr/bin/env python3
"""
Simple test script to check if the app can import correctly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from hndasah_backend.config import settings
    print("✅ Config import successful")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DATABASE_URL: {settings.DATABASE_URL[:50]}...")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from hndasah_backend.main import app
    print("✅ Main app import successful")
except Exception as e:
    print(f"❌ Main app import failed: {e}")
    import traceback
    traceback.print_exc()
