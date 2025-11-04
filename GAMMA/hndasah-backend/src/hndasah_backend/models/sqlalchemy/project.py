"""
SQLAlchemy models for project management in WhatsApp PM System v3.0 (Gamma)
Project, project members, and related entities
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import uuid4
import structlog
from sqlalchemy import Column, String, DateTime, Date, Text, Integer, Boolean, DECIMAL, func, text, ForeignKey, Table, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
try:
    from geoalchemy2 import Geography
    HAS_GEOALCHEMY2 = True
except ImportError:
    Geography = None
    HAS_GEOALCHEMY2 = False
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import Base
from ...schemas.base import BaseModel

logger = structlog.get_logger(__name__)


class Project(BaseModel):
    """Project model with AI integration and vector embeddings."""

    __tablename__ = "projects"

    # Basic Information
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False, default="lump_sum")

    # Location with PostGIS (optional - falls back to JSONB if geoalchemy2 not available)
    location: Mapped[Optional[Any]] = mapped_column(JSONB)
    address: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # Schedule
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Financial
    budget_total: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), nullable=False, default=0)
    actual_cost: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Progress & Risk
    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planning")

    # Team
    project_manager_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    client_contact: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # AI Integration
    ai_insights: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    risk_predictions: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSONB, nullable=True)  # Vector embeddings stored as JSONB for now

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    ai_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # WhatsApp Settings
    whatsapp_settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=lambda: {
        "auto_responses": True,
        "ai_processing": True,
        "notification_contacts": []
    })

    # Relationships
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    cost_items: Mapped[List["CostItem"]] = relationship(
        "CostItem",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    whatsapp_messages: Mapped[List["WhatsAppMessage"]] = relationship(
        "WhatsAppMessage",
        back_populates="project"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="check_end_date_after_start"),
        CheckConstraint("actual_end_date >= actual_start_date OR actual_end_date IS NULL", name="check_actual_dates"),
        CheckConstraint("status IN ('planning', 'active', 'on_hold', 'completed', 'cancelled')", name="check_status_valid"),
        CheckConstraint("contract_type IN ('lump_sum', 'cost_plus', 'time_materials', 'unit_price')", name="check_contract_type_valid"),
        CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name="check_risk_level_valid"),
        CheckConstraint("progress_percentage >= 0 AND progress_percentage <= 100", name="check_progress_percentage_range"),
    )

    @hybrid_property
    def health_score(self) -> Optional[float]:
        """Calculate project health score based on multiple factors."""
        # This would be implemented with a database function
        # For now, return a computed value
        return None

    def calculate_health_score(self) -> float:
        """Calculate health score based on progress, budget, schedule, and risk."""
        progress_weight = 0.3
        budget_weight = 0.25
        schedule_weight = 0.25
        risk_weight = 0.2

        # Progress Score (0-100)
        progress_score = self.progress_percentage

        # Budget Score (0-100): Lower variance = higher score
        if self.budget_total and self.budget_total > 0:
            budget_variance = ((self.actual_cost - self.budget_total) / self.budget_total) * 100
            budget_score = max(0, 100 - abs(budget_variance))
        else:
            budget_score = 100

        # Schedule Score (0-100): Based on planned vs actual dates
        if self.end_date and self.actual_end_date:
            planned_days = (self.end_date - self.start_date).days
            actual_days = (self.actual_end_date - self.start_date).days
            schedule_variance = (actual_days - planned_days) / planned_days * 100
            schedule_score = max(0, 100 - abs(schedule_variance))
        elif not self.actual_end_date:
            # Project still active, score based on progress vs time elapsed
            total_days = (self.end_date - self.start_date).days
            elapsed_days = (date.today() - self.start_date).days
            expected_progress = (elapsed_days / total_days) * 100 if total_days > 0 else 0
            schedule_score = max(0, 100 - abs(self.progress_percentage - expected_progress))
        else:
            schedule_score = 100  # Project completed on time

        # Risk Score (0-100): Based on risk level
        risk_scores = {'low': 90, 'medium': 70, 'high': 40, 'critical': 10}
        risk_score = risk_scores.get(self.risk_level, 50)

        # Calculate weighted health score
        health_score = (
            progress_score * progress_weight +
            budget_score * budget_weight +
            schedule_score * schedule_weight +
            risk_score * risk_weight
        )

        return round(health_score, 2)

    def get_completion_percentage(self) -> float:
        """Get project completion percentage based on tasks."""
        if not self.tasks:
            return 0.0

        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task.status == 'completed')

        if total_tasks == 0:
            return 0.0

        return round((completed_tasks / total_tasks) * 100, 2)

    def get_budget_variance(self) -> Dict[str, float]:
        """Calculate budget variance metrics."""
        if not self.budget_total or self.budget_total == 0:
            return {
                "variance_amount": 0,
                "variance_percentage": 0,
                "status": "no_budget"
            }

        variance_amount = float(self.actual_cost - self.budget_total)
        variance_percentage = (variance_amount / float(self.budget_total)) * 100

        if variance_amount > 0:
            status = "over_budget"
        elif variance_amount < 0:
            status = "under_budget"
        else:
            status = "on_budget"

        return {
            "variance_amount": round(variance_amount, 2),
            "variance_percentage": round(variance_percentage, 2),
            "status": status
        }

    def get_schedule_variance(self) -> Dict[str, Any]:
        """Calculate schedule variance metrics."""
        if not self.end_date:
            return {"variance_days": 0, "variance_percentage": 0, "status": "no_schedule"}

        if self.actual_end_date:
            # Project completed
            planned_days = (self.end_date - self.start_date).days
            actual_days = (self.actual_end_date - self.start_date).days
            variance_days = actual_days - planned_days
            variance_percentage = (variance_days / planned_days) * 100 if planned_days > 0 else 0

            if variance_days > 0:
                status = "delayed"
            elif variance_days < 0:
                status = "ahead"
            else:
                status = "on_schedule"
        else:
            # Project in progress
            total_days = (self.end_date - self.start_date).days
            elapsed_days = (date.today() - self.start_date).days
            expected_progress = (elapsed_days / total_days) * 100 if total_days > 0 else 0
            actual_progress = self.progress_percentage

            variance_percentage = actual_progress - expected_progress
            variance_days = int((variance_percentage / 100) * total_days) if total_days > 0 else 0

            if variance_percentage < 0:
                status = "behind_schedule"
            elif variance_percentage > 0:
                status = "ahead_schedule"
            else:
                status = "on_schedule"

        return {
            "variance_days": variance_days,
            "variance_percentage": round(variance_percentage, 2),
            "status": status
        }


class ProjectMember(BaseModel):
    """Project member model for team management."""

    __tablename__ = "project_members"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Role in Project
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    permissions: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Assignment Details
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    assigned_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Workload & Capacity
    capacity_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    workload_hours: Mapped[DECIMAL] = mapped_column(DECIMAL(5, 2), nullable=False, default=0)

    # Communication Preferences
    notification_settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=lambda: {
        "email": True,
        "whatsapp": True,
        "task_assignments": True,
        "project_updates": True,
        "deadline_reminders": True
    })

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    assigned_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_by])

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('owner', 'manager', 'lead', 'member', 'viewer')", name="check_role_valid"),
        CheckConstraint("capacity_percentage >= 0 AND capacity_percentage <= 100", name="check_capacity_percentage_range"),
        UniqueConstraint("project_id", "user_id", name="unique_project_user"),
    )

    def get_active_tasks_count(self) -> int:
        """Get count of active tasks assigned to this member."""
        if not self.user or not self.user.tasks:
            return 0

        return sum(1 for task in self.user.tasks
                  if task.project_id == self.project_id
                  and task.status in ['not_started', 'in_progress'])

    def get_workload_percentage(self) -> float:
        """Calculate current workload as percentage of capacity."""
        if self.capacity_percentage == 0:
            return 0.0

        # Assuming 40 hours per week as standard capacity
        standard_weekly_hours = 40
        capacity_hours = (self.capacity_percentage / 100) * standard_weekly_hours

        if capacity_hours == 0:
            return 0.0

        return min(100.0, (float(self.workload_hours) / capacity_hours) * 100)

    def can_access_resource(self, resource_type: str, action: str) -> bool:
        """Check if member has permission for specific action on resource type."""
        if self.role == 'owner':
            return True

        role_permissions = {
            'manager': ['read', 'write', 'delete', 'manage_members'],
            'lead': ['read', 'write', 'manage_tasks'],
            'member': ['read', 'write'],
            'viewer': ['read']
        }

        user_permissions = role_permissions.get(self.role, [])
        required_permission = f"{action}_{resource_type}"

        return required_permission in user_permissions or action in user_permissions

