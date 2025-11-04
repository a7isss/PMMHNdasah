#!/usr/bin/env python3
"""
Test script to verify health check endpoint functionality
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_health_check():
    """Test the health check functionality."""
    try:
        from hndasah_backend.database import health_check_database, health_check_redis
        from hndasah_backend.main import health_check
        from hndasah_backend.config import settings

        print("🔍 Testing health check functionality...")

        # Test database health check
        print("📊 Testing database health check...")
        db_health = await health_check_database()
        print(f"Database health: {db_health}")

        # Test Redis health check
        print("📊 Testing Redis health check...")
        redis_health = await health_check_redis()
        print(f"Redis health: {redis_health}")

        # Test full health check endpoint
        print("📊 Testing full health check endpoint...")
        health_response = await health_check()
        print(f"Full health check response: {health_response}")

        print("✅ All health checks completed successfully")

    except Exception as e:
        print(f"❌ Health check test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_health_check())
