"""
Tenant middleware for WhatsApp PM System v3.0 (Gamma)
Multi-tenant request isolation and context management
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from typing import Optional

from ..utils.security import decode_token

logger = structlog.get_logger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware for multi-tenant request processing.

    Extracts tenant information from:
    1. JWT token payload
    2. Subdomain (fallback)
    3. Custom header (for API clients)

    Sets request.state.tenant_id for use throughout the request lifecycle.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and extract tenant information."""

        tenant_id = None

        try:
            # Method 1: Extract from JWT token
            tenant_id = await self._extract_tenant_from_token(request)

            # Method 2: Extract from subdomain (fallback)
            if not tenant_id:
                tenant_id = self._extract_tenant_from_subdomain(request)

            # Method 3: Extract from custom header (for API clients)
            if not tenant_id:
                tenant_id = self._extract_tenant_from_header(request)

            # Validate tenant exists and is active
            if tenant_id:
                if not await self._validate_tenant(tenant_id):
                    logger.warning("Invalid or inactive tenant", tenant_id=tenant_id)
                    tenant_id = None

            # Set tenant context
            request.state.tenant_id = tenant_id

            # Add tenant to response headers for debugging
            response = await call_next(request)
            if tenant_id:
                response.headers["X-Tenant-ID"] = tenant_id

            return response

        except Exception as e:
            logger.error("Tenant middleware error", error=str(e), path=request.url.path)
            # Continue with request but without tenant context
            request.state.tenant_id = None
            return await call_next(request)

    async def _extract_tenant_from_token(self, request: Request) -> Optional[str]:
        """Extract tenant ID from JWT token."""
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)
            tenant_id = payload.get("tenant_id")

            if tenant_id:
                logger.debug("Tenant extracted from token", tenant_id=tenant_id)
                return tenant_id

        except Exception as e:
            logger.warning("Failed to decode token for tenant extraction", error=str(e))

        return None

    def _extract_tenant_from_subdomain(self, request: Request) -> Optional[str]:
        """Extract tenant ID from subdomain."""
        host = request.headers.get("host", "").lower()

        # Remove port if present
        if ":" in host:
            host = host.split(":")[0]

        # Check if it's a subdomain pattern
        if host.endswith((".whatsapppm.com", ".localhost")):
            subdomain = host.split(".")[0]

            # Skip 'www', 'app', 'api' subdomains
            if subdomain not in ['www', 'app', 'api', 'localhost']:
                logger.debug("Tenant extracted from subdomain", subdomain=subdomain)
                return subdomain

        return None

    def _extract_tenant_from_header(self, request: Request) -> Optional[str]:
        """Extract tenant ID from custom header (for API clients)."""
        tenant_header = request.headers.get("X-Tenant-ID")

        if tenant_header:
            logger.debug("Tenant extracted from header", tenant_id=tenant_header)
            return tenant_header

        return None

    async def _validate_tenant(self, tenant_id: str) -> bool:
        """Validate that tenant exists and is active."""
        try:
            # Import here to avoid circular imports
            from ..database import get_db
            from ..schemas.user import Tenant
            from sqlalchemy import select

            async with get_db() as db:
                result = await db.execute(
                    select(Tenant).where(
                        Tenant.id == tenant_id,
                        Tenant.is_active == True
                    )
                )
                tenant = result.scalar_one_or_none()

                return tenant is not None

        except Exception as e:
            logger.error("Tenant validation error", tenant_id=tenant_id, error=str(e))
            return False


class TenantContext:
    """Context manager for tenant-scoped operations."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.previous_tenant = None

    async def __aenter__(self):
        """Set tenant context."""
        # This would be used for background tasks or service methods
        # that need to operate within a specific tenant context
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up tenant context."""
        pass


def get_current_tenant_id(request: Request) -> Optional[str]:
    """Get current tenant ID from request state."""
    return getattr(request.state, 'tenant_id', None)


def require_tenant(func):
    """Decorator to require tenant context for a function."""
    async def wrapper(*args, **kwargs):
        # Extract tenant_id from kwargs or request
        tenant_id = kwargs.get('tenant_id')
        if not tenant_id:
            request = kwargs.get('request')
            if request:
                tenant_id = get_current_tenant_id(request)

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant context required"
            )

        return await func(*args, **kwargs)

    return wrapper
