"""
SQLAlchemy User and Tenant models for Project Management & Procurement System v3.0 (Gamma)
Database models for authentication and multi-tenancy
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from .base import Base


class Tenant(Base):
    """Multi-tenant organization model."""
    __tablename__ = "tenants"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = Column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = Column(String(255), unique=True, index=True)
    subscription_plan: Mapped[str] = Column(String(50), nullable=False, default="starter")
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)

    # Contact information
    contact_email: Mapped[Optional[str]] = Column(String(255))
    contact_phone: Mapped[Optional[str]] = Column(String(50))

    # Metadata
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name='{self.name}', domain='{self.domain}')>"


class User(Base):
    """User authentication and profile model."""
    __tablename__ = "users"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Authentication
    email: Mapped[str] = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = Column(String(255), nullable=False)
    role: Mapped[str] = Column(String(50), nullable=False, default="member")  # super_admin, admin, manager, member, viewer

    # Profile information
    first_name: Mapped[Optional[str]] = Column(String(100))
    last_name: Mapped[Optional[str]] = Column(String(100))
    phone: Mapped[Optional[str]] = Column(String(50))
    job_title: Mapped[Optional[str]] = Column(String(100))
    avatar_url: Mapped[Optional[str]] = Column(Text)

    # WhatsApp integration
    whatsapp_number: Mapped[Optional[str]] = Column(String(20), index=True)
    whatsapp_verified: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Status
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    is_email_verified: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Activity tracking
    last_login_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    login_count: Mapped[int] = Column(Integer, nullable=False, default=0)

    # Preferences (stored as JSON)
    preferences: Mapped[Optional[Text]] = Column(Text)  # JSON string

    # Metadata
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")

    # Task assignments
    assigned_tasks: Mapped[List["Task"]] = relationship("Task", back_populates="assigned_user", foreign_keys="Task.assigned_to")

    # Project memberships
    project_memberships: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="user")

    # WhatsApp messages
    whatsapp_messages: Mapped[List["WhatsAppMessage"]] = relationship("WhatsAppMessage", back_populates="user")

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

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', tenant_id={self.tenant_id})>"
