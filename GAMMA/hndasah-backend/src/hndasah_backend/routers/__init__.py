"""
API routers for WhatsApp PM System v3.0 (Gamma)
FastAPI route handlers for all endpoints
"""

# Import all routers for main.py
from . import auth, projects, tasks, costs, whatsapp, ai, admin

__all__ = ["auth", "projects", "tasks", "costs", "whatsapp", "ai", "admin"]

