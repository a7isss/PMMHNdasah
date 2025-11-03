"""
Authentication service for WhatsApp PM System v3.0 (Gamma)
JWT token management and user authentication logic
"""

from datetime import datetime, timedelta
from typing import Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from schemas.user import User
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    create_password_reset_token,
    decode_password_reset_token,
    verify_password
)

logger = structlog.get_logger(__name__)


class AuthService:
    """Authentication service for user management and token operations."""

    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    async def authenticate_user(self, email: str, password: str, db: AsyncSession) -> Optional[User]:
        """Authenticate a user with email and password."""
        try:
            # Find user by email
            result = await db.execute(
                select(User).where(User.email == email, User.is_active == True)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning("User not found", email=email)
                return None

            # Verify password
            if not verify_password(password, user.password_hash):
                logger.warning("Invalid password", email=email, user_id=str(user.id))
                return None

            logger.info("User authenticated successfully", email=email, user_id=str(user.id))
            return user

        except Exception as e:
            logger.error("Authentication error", email=email, error=str(e))
            return None

    def create_access_token(self, data: dict) -> str:
        """Create a JWT access token."""
        return create_access_token(data)

    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token."""
        return create_refresh_token(data)

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token."""
        return decode_token(token)

    def create_password_reset_token(self, email: str) -> str:
        """Create a password reset token."""
        return create_password_reset_token(email)

    def decode_password_reset_token(self, token: str) -> dict:
        """Decode and validate a password reset token."""
        return decode_password_reset_token(token)

    async def get_user_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email address."""
        result = await db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str, db: AsyncSession) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email_and_tenant(self, email: str, tenant_id: str, db: AsyncSession) -> Optional[User]:
        """Get user by email and tenant ID."""
        result = await db.execute(
            select(User).where(
                User.email == email,
                User.tenant_id == tenant_id,
                User.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def update_user_last_login(self, user_id: str, db: AsyncSession) -> None:
        """Update user's last login timestamp."""
        from sqlalchemy import update
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.utcnow())
        )
        await db.commit()

    async def validate_token_and_get_user(self, token: str, db: AsyncSession) -> Optional[User]:
        """Validate JWT token and return user if valid."""
        try:
            # Decode token
            payload = self.decode_token(token)

            # Extract user info
            email = payload.get("sub")
            tenant_id = payload.get("tenant_id")

            if not email or not tenant_id:
                return None

            # Get user
            user = await self.get_user_by_email_and_tenant(email, tenant_id, db)

            if not user:
                return None

            # Check if user is still active
            if not user.is_active:
                return None

            return user

        except Exception as e:
            logger.warning("Token validation failed", error=str(e))
            return None

    async def refresh_access_token(self, refresh_token: str, db: AsyncSession) -> Optional[str]:
        """Create new access token from valid refresh token."""
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)

            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                return None

            # Get user
            email = payload.get("sub")
            tenant_id = payload.get("tenant_id")

            user = await self.get_user_by_email_and_tenant(email, tenant_id, db)
            if not user or not user.is_active:
                return None

            # Create new access token
            access_token_data = {
                "sub": user.email,
                "tenant_id": str(user.tenant_id),
                "user_id": str(user.id),
                "role": user.role
            }

            return self.create_access_token(access_token_data)

        except Exception as e:
            logger.warning("Refresh token validation failed", error=str(e))
            return None

    async def invalidate_user_sessions(self, user_id: str, db: AsyncSession) -> None:
        """Invalidate all sessions for a user (for security)."""
        # In a real implementation, you might store session tokens in Redis
        # and invalidate them here. For now, just log the action.
        logger.info("Invalidating user sessions", user_id=user_id)

        # Update user's last login to force re-authentication
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(updated_at=datetime.utcnow())
        )
        await db.commit()

    async def check_user_permissions(self, user: User, required_permissions: list[str]) -> bool:
        """Check if user has required permissions."""
        if not user.permissions:
            return False

        user_permissions = set(user.permissions)
        required_permissions_set = set(required_permissions)

        return required_permissions_set.issubset(user_permissions)

    async def get_user_permissions(self, user: User) -> list[str]:
        """Get all permissions for a user."""
        base_permissions = []

        # Role-based permissions
        if user.role == 'super_admin':
            base_permissions.extend([
                'users:create', 'users:read', 'users:update', 'users:delete',
                'tenants:create', 'tenants:read', 'tenants:update', 'tenants:delete',
                'projects:create', 'projects:read', 'projects:update', 'projects:delete',
                'whatsapp:send', 'whatsapp:configure', 'ai:configure'
            ])
        elif user.role == 'admin':
            base_permissions.extend([
                'users:create', 'users:read', 'users:update',
                'projects:create', 'projects:read', 'projects:update', 'projects:delete',
                'whatsapp:send', 'whatsapp:configure'
            ])
        elif user.role == 'manager':
            base_permissions.extend([
                'projects:create', 'projects:read', 'projects:update',
                'tasks:create', 'tasks:read', 'tasks:update', 'tasks:delete',
                'costs:create', 'costs:read', 'costs:update', 'costs:approve',
                'whatsapp:send'
            ])
        elif user.role == 'member':
            base_permissions.extend([
                'projects:read',
                'tasks:create', 'tasks:read', 'tasks:update',
                'costs:create', 'costs:read', 'costs:update',
                'whatsapp:send'
            ])
        else:  # viewer
            base_permissions.extend([
                'projects:read',
                'tasks:read',
                'costs:read'
            ])

        # Add custom permissions from user record
        if user.permissions:
            base_permissions.extend(user.permissions)

        return list(set(base_permissions))  # Remove duplicates

    async def log_auth_event(self, event_type: str, user_id: Optional[str] = None,
                           email: Optional[str] = None, details: Optional[dict] = None):
        """Log authentication-related events."""
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if user_id:
            log_data["user_id"] = user_id
        if email:
            log_data["email"] = email
        if details:
            log_data["details"] = details

        logger.info("Auth event", **log_data)

    async def initialize(self):
        """Initialize the auth service."""
        logger.info("Auth service initialized")

    async def cleanup(self):
        """Cleanup auth service resources."""
        logger.info("Auth service cleaned up")
