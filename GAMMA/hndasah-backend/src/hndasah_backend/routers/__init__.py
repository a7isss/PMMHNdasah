"""
API routers for WhatsApp PM System v3.0 (Gamma)
FastAPI route handlers for all endpoints
"""

# Import only enabled routers for main.py
from . import auth, admin, debug

__all__ = ["auth", "admin", "debug"]
