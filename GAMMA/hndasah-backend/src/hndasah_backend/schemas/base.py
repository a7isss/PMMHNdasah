"""
Base database schema for WhatsApp PM System v3.0 (Gamma)
Common base classes and utilities for all models
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
import structlog
from sqlalchemy import Column, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ..database import Base

logger = structlog.get_logger(__name__)


class BaseModel(Base):
    """Enhanced base model with common functionality."""

    __abstract__ = True

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Created by user (for audit trail)
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True
    )

    # Version for optimistic locking
    version: Mapped[int] = mapped_column(
        server_default=text("1"),
        nullable=False
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs) -> None:
        """Update model attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Update version for optimistic locking
        if hasattr(self, 'version'):
            self.version += 1

    async def save(self, db: AsyncSession) -> None:
        """Save the model to database."""
        try:
            db.add(self)
            await db.commit()
            await db.refresh(self)
            logger.info(
                "Model saved",
                model=self.__class__.__name__,
                id=self.id
            )
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to save model",
                model=self.__class__.__name__,
                error=str(e)
            )
            raise

    async def update_db(self, db: AsyncSession, **kwargs) -> None:
        """Update model in database."""
        try:
            self.update(**kwargs)
            self.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(self)
            logger.info(
                "Model updated",
                model=self.__class__.__name__,
                id=self.id
            )
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to update model",
                model=self.__class__.__name__,
                id=self.id,
                error=str(e)
            )
            raise

    async def delete_soft(self, db: AsyncSession) -> None:
        """Soft delete the model."""
        try:
            self.deleted_at = datetime.utcnow()
            await db.commit()
            logger.info(
                "Model soft deleted",
                model=self.__class__.__name__,
                id=self.id
            )
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to soft delete model",
                model=self.__class__.__name__,
                id=self.id,
                error=str(e)
            )
            raise

    def is_deleted(self) -> bool:
        """Check if model is soft deleted."""
        return self.deleted_at is not None

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this model."""
        return cls.__tablename__

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: str) -> Optional['BaseModel']:
        """Get model instance by ID."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.id == id, cls.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession, skip: int = 0, limit: int = 100) -> list['BaseModel']:
        """Get all model instances with pagination."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls)
            .where(cls.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @classmethod
    async def count(cls, db: AsyncSession) -> int:
        """Count total model instances."""
        from sqlalchemy import select, func
        result = await db.execute(
            select(func.count(cls.id)).where(cls.deleted_at.is_(None))
        )
        return result.scalar_one()


class TimestampMixin:
    """Mixin for timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    def soft_delete(self) -> None:
        """Mark as soft deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore from soft delete."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if soft deleted."""
        return self.deleted_at is not None


class AuditMixin:
    """Mixin for audit trail."""

    created_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True
    )


def generate_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.utcnow()

