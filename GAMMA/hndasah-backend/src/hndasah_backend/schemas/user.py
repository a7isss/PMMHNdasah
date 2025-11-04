"""
User and Tenant database schemas for WhatsApp PM System v3.0 (Gamma)
SQLAlchemy models for authentication and multi-tenancy
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, JSON, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, TimestampMixin


class Tenant(BaseModel):
    """Tenant model for multi-tenancy support."""

    __tablename__ = "tenants"

    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)

    # Subscription
    subscription_plan: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="starter",
        index=True
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Contact information
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[dict]] = mapped_column(JSON)

    # Settings and configuration
    settings: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "timezone": "UTC",
            "currency": "USD",
            "language": "en",
            "features": {
                "whatsapp": True,
                "ai_insights": True,
                "advanced_reporting": False
            }
        }
    )

    # AI configuration
    ai_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "openai_api_key": None,
            "model_preferences": {
                "intent_classification": "gpt-4-turbo",
                "response_generation": "gpt-4-turbo",
                "forecasting": "gpt-4-turbo"
            },
            "confidence_thresholds": {
                "intent": 0.8,
                "sentiment": 0.7,
                "urgency": 0.75
            }
        }
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('domain', name='uq_tenants_domain'),
    )

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name}, domain={self.domain})>"


class User(BaseModel):
    """User model for authentication and profiles."""

    __tablename__ = "users"

    # Foreign keys
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True
    )

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))

    # Email verification
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    # Profile information
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Role and permissions
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
        index=True
    )
    permissions: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Preferences
    preferences: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "theme": "light",
            "notifications": {
                "email": True,
                "whatsapp": True,
                "push": True
            },
            "language": "en",
            "timezone": "UTC"
        }
    )

    # WhatsApp integration
    whatsapp_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        index=True
    )
    whatsapp_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    # AI personalization
    ai_profile: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "communication_style": "professional",
            "response_preferences": {
                "detail_level": "balanced",
                "urgency_sensitivity": "medium"
            },
            "learning_data": []
        }
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")

    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_users_tenant_email'),
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role in ['admin', 'super_admin']

    @property
    def is_super_admin(self) -> bool:
        """Check if user is a super admin."""
        return self.role == 'super_admin'

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        if not self.permissions:
            return False
        return permission in self.permissions

    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        if not self.permissions:
            return False
        return any(perm in self.permissions for perm in permissions)

    def can_access_tenant(self, tenant_id: str) -> bool:
        """Check if user can access a specific tenant."""
        return self.tenant_id == tenant_id or self.is_super_admin

    def get_role_permissions(self) -> List[str]:
        """Get permissions based on user role."""
        base_permissions = []

        # Role-based permissions
        if self.role == 'super_admin':
            base_permissions.extend([
                'users:create', 'users:read', 'users:update', 'users:delete',
                'tenants:create', 'tenants:read', 'tenants:update', 'tenants:delete',
                'projects:create', 'projects:read', 'projects:update', 'projects:delete',
                'whatsapp:send', 'whatsapp:configure', 'ai:configure'
            ])
        elif self.role == 'admin':
            base_permissions.extend([
                'users:create', 'users:read', 'users:update',
                'projects:create', 'projects:read', 'projects:update', 'projects:delete',
                'whatsapp:send', 'whatsapp:configure'
            ])
        elif self.role == 'manager':
            base_permissions.extend([
                'projects:create', 'projects:read', 'projects:update',
                'tasks:create', 'tasks:read', 'tasks:update', 'tasks:delete',
                'costs:create', 'costs:read', 'costs:update', 'costs:approve',
                'whatsapp:send'
            ])
        elif self.role == 'member':
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

        return base_permissions

    def get_all_permissions(self) -> List[str]:
        """Get all permissions (role-based + custom)."""
        permissions = self.get_role_permissions()

        # Add custom permissions
        if self.permissions:
            permissions.extend(self.permissions)

        return list(set(permissions))  # Remove duplicates

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role}, tenant={self.tenant_id})>"

