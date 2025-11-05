"""
Authentication middleware for WhatsApp PM System v3.0 (Gamma)
JWT token validation and user context management
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from typing import Optional, List

from ..utils.security import decode_token

logger = structlog.get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication and user context.

    Validates JWT tokens and sets user context for protected routes.
    Handles both required and optional authentication.
    """

    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/superadmin/login",
            "/api/v1/auth/password-reset",
            "/api/v1/auth/password-reset/confirm"
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication."""

        # Skip authentication for excluded paths
        if self._should_skip_auth(request):
            request.state.user = None
            request.state.is_authenticated = False
            return await call_next(request)

        try:
            # Extract and validate token
            user_context = await self._extract_user_context(request)

            # Set user context
            request.state.user = user_context.get('user') if user_context else None
            request.state.is_authenticated = user_context is not None
            request.state.user_id = user_context.get('user_id') if user_context else None
            request.state.tenant_id = user_context.get('tenant_id') if user_context else None

            # Add user context to response headers for debugging
            response = await call_next(request)
            if user_context:
                response.headers["X-User-ID"] = user_context.get('user_id', '')
                response.headers["X-User-Role"] = user_context.get('role', '')

            return response

        except HTTPException:
            # Re-raise HTTP exceptions (like 401)
            raise
        except Exception as e:
            logger.error("Auth middleware error", error=str(e), path=request.url.path)
            # Continue with request but without user context
            request.state.user = None
            request.state.is_authenticated = False
            return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """Check if authentication should be skipped for this path."""
        path = request.url.path

        # Check exact matches
        if path in self.exclude_paths:
            return True

        # Check prefix matches (for API versioning)
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True

        return False

    async def _extract_user_context(self, request: Request) -> Optional[dict]:
        """Extract user context from JWT token."""
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            # Decode token
            payload = decode_token(token)

            # Validate token structure
            user_id = payload.get("user_id") or payload.get("sub")
            tenant_id = payload.get("tenant_id")
            role = payload.get("role", "member")

            if not user_id or not tenant_id:
                logger.warning("Invalid token payload", payload_keys=list(payload.keys()))
                return None

            # Get user from database to ensure they still exist and are active
            user = await self._get_user_from_db(user_id, tenant_id)
            if not user:
                logger.warning("User not found or inactive", user_id=user_id, tenant_id=tenant_id)
                return None

            return {
                'user': user,
                'user_id': user_id,
                'tenant_id': tenant_id,
                'role': role,
                'email': user.email,
                'permissions': user.get_all_permissions()
            }

        except Exception as e:
            logger.warning("Token validation failed", error=str(e))
            return None

    async def _get_user_from_db(self, user_id: str, tenant_id: str):
        """Get user from database with validation."""
        try:
            # Import here to avoid circular imports
            from ..database import get_db
            from ..schemas.user import User
            from sqlalchemy import select

            async with get_db() as db:
                result = await db.execute(
                    select(User).where(
                        User.id == user_id,
                        User.tenant_id == tenant_id,
                        User.is_active == True
                    )
                )
                user = result.scalar_one_or_none()
                return user

        except Exception as e:
            logger.error("Database error in auth middleware", error=str(e))
            return None


def get_current_user_optional(request: Request):
    """Get current user if authenticated (optional)."""
    return getattr(request.state, 'user', None)


def get_current_user_required(request: Request):
    """Get current user (required - raises exception if not authenticated)."""
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user(request: Request):
    """Alias for get_current_user_required for backward compatibility."""
    return get_current_user_required(request)


def require_auth(func):
    """Decorator to require authentication for a function."""
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if request:
            get_current_user_required(request)
        return await func(*args, **kwargs)
    return wrapper


def require_role(required_role: str):
    """Decorator to require specific role."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if request:
                user = get_current_user_required(request)
                if user.role not in ['super_admin', required_role]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role '{required_role}' required"
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if request:
                user = get_current_user_required(request)
                if not user.has_permission(permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission '{permission}' required"
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class AuthContext:
    """Context manager for authentication-scoped operations."""

    def __init__(self, user_id: str, tenant_id: str):
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def __aenter__(self):
        """Set authentication context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up authentication context."""
        pass
