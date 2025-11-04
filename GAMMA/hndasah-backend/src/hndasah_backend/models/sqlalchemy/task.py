"""
SQLAlchemy models for task management in WhatsApp PM System v3.0 (Gamma)
Tasks, scheduling, CPM calculations, and Gantt charts
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import uuid4
import structlog
from sqlalchemy import Column, String, DateTime, Date, Text, Integer, Boolean, DECIMAL, func, text, ForeignKey, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from ...database import Base
from ...schemas.base import BaseModel

logger = structlog.get_logger(__name__)


class Task(BaseModel):
    """Task model with AI integration and scheduling."""

    __tablename__ = "tasks"

    # Basic Information
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_code: Mapped[Optional[str]] = mapped_column(String(50))

    # Hierarchy
    parent_task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"))
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    wbs_code: Mapped[Optional[str]] = mapped_column(String(100))

    # Schedule
    planned_start_date: Mapped[Optional[date]] = mapped_column(Date)
    planned_end_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Duration & Progress
    planned_duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    actual_duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")

    # Resources
    assigned_to: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    estimated_hours: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(8, 2))
    actual_hours: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(8, 2))

    # Dependencies
    predecessor_tasks: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    successor_tasks: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    lag_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Cost
    budgeted_cost: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    actual_cost: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)

    # Critical Path
    is_critical_path: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    slack_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # AI Integration
    ai_priority_score: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(3, 2))
    ai_risk_score: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(3, 2))
    ai_insights: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSONB, nullable=True)  # Vector embeddings stored as JSONB for now

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    ai_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assigned_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])
    parent_task: Mapped[Optional["Task"]] = relationship("Task", remote_side="Task.id")
    subtasks: Mapped[List["Task"]] = relationship("Task", cascade="all, delete-orphan")
    cost_items: Mapped[List["CostItem"]] = relationship("CostItem", back_populates="task")
    comments: Mapped[List["TaskComment"]] = relationship(
        "TaskComment",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("planned_end_date >= planned_start_date OR planned_end_date IS NULL"),
        CheckConstraint("actual_end_date >= actual_start_date OR actual_end_date IS NULL"),
        text("CHECK (status IN ('not_started', 'in_progress', 'completed', 'on_hold', 'cancelled'))"),
        CheckConstraint("progress_percentage >= 0 AND progress_percentage <= 100"),
        CheckConstraint("level >= 1"),
        CheckConstraint("ai_priority_score >= 0 AND ai_priority_score <= 1 OR ai_priority_score IS NULL"),
        CheckConstraint("ai_risk_score >= 0 AND ai_risk_score <= 1 OR ai_risk_score IS NULL"),
    )

    def get_duration_days(self) -> int:
        """Get actual duration or calculate from dates."""
        if self.actual_duration_days:
            return self.actual_duration_days

        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days

        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days

        return self.planned_duration_days or 0

    def get_completion_percentage(self) -> float:
        """Calculate completion percentage based on subtasks if any."""
        if self.subtasks:
            total_subtasks = len(self.subtasks)
            if total_subtasks == 0:
                return self.progress_percentage

            completed_subtasks = sum(1 for subtask in self.subtasks if subtask.status == 'completed')
            return round((completed_subtasks / total_subtasks) * 100, 2)

        return self.progress_percentage

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.status == 'completed':
            return False

        check_date = self.planned_end_date
        if not check_date:
            return False

        return date.today() > check_date

    def get_slack_days(self) -> int:
        """Calculate slack (float) days for this task."""
        if not self.planned_end_date or not self.project:
            return 0

        # This would be calculated by CPM algorithm
        # For now, return a simple estimate
        if self.is_critical_path:
            return 0

        # Estimate slack based on project buffer
        project_duration = (self.project.end_date - self.project.start_date).days
        task_position = ((self.planned_end_date - self.project.start_date).days / project_duration) if project_duration > 0 else 0

        # Tasks later in project have less slack
        estimated_slack = int((1 - task_position) * 30)  # Up to 30 days buffer
        return max(0, estimated_slack)

    def get_predecessors(self) -> List["Task"]:
        """Get predecessor task objects."""
        if not self.predecessor_tasks:
            return []

        # This would need to be implemented with a query
        # For now, return empty list
        return []

    def get_successors(self) -> List["Task"]:
        """Get successor task objects."""
        if not self.successors:
            return []

        # This would need to be implemented with a query
        # For now, return empty list
        return []

    def can_start(self) -> bool:
        """Check if task can start based on predecessor completion."""
        if not self.predecessor_tasks:
            return True

        # Check if all predecessors are completed
        predecessors = self.get_predecessors()
        return all(pred.status == 'completed' for pred in predecessors)

    def update_progress_from_subtasks(self) -> None:
        """Update progress based on subtasks completion."""
        if not self.subtasks:
            return

        total_subtasks = len(self.subtasks)
        if total_subtasks == 0:
            return

        completed_subtasks = sum(1 for subtask in self.subtasks if subtask.status == 'completed')
        self.progress_percentage = int((completed_subtasks / total_subtasks) * 100)

    def calculate_earned_value(self) -> Dict[str, float]:
        """Calculate earned value metrics."""
        budgeted_cost = float(self.budgeted_cost)
        planned_value = budgeted_cost * (self.progress_percentage / 100)
        earned_value = planned_value  # Assuming progress = earned value
        actual_cost = float(self.actual_cost)

        cost_variance = earned_value - actual_cost
        schedule_variance = earned_value - planned_value

        return {
            "planned_value": round(planned_value, 2),
            "earned_value": round(earned_value, 2),
            "actual_cost": round(actual_cost, 2),
            "cost_variance": round(cost_variance, 2),
            "schedule_variance": round(schedule_variance, 2),
            "cost_performance_index": round(earned_value / actual_cost, 2) if actual_cost > 0 else 0,
            "schedule_performance_index": round(earned_value / planned_value, 2) if planned_value > 0 else 0
        }


class TaskComment(BaseModel):
    """Task comment model for notes and updates."""

    __tablename__ = "task_comments"

    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    comment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="comment")
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mentioned_users: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="comments")

    # Constraints
    __table_args__ = (
        text("CHECK (comment_type IN ('comment', 'status_change', 'assignment_change', 'progress_update', 'system'))"),
    )


class TaskDependency(BaseModel):
    """Task dependency model for CPM calculations."""

    __tablename__ = "task_dependencies"

    predecessor_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    successor_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    lag_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dependency_type: Mapped[str] = mapped_column(String(20), nullable=False, default="finish_to_start")

    # Relationships
    predecessor: Mapped["Task"] = relationship("Task", foreign_keys=[predecessor_id])
    successor: Mapped["Task"] = relationship("Task", foreign_keys=[successor_id])

    # Constraints
    __table_args__ = (
        text("CHECK (dependency_type IN ('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish'))"),
        CheckConstraint("predecessor_id != successor_id"),
    )


class TaskTemplate(BaseModel):
    """Task template model for standardized tasks."""

    __tablename__ = "task_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    estimated_duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_hours: Mapped[DECIMAL] = mapped_column(DECIMAL(8, 2), nullable=False)
    default_assignee_role: Mapped[Optional[str]] = mapped_column(String(50))
    subtasks: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    dependencies: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Constraints
    __table_args__ = (
        CheckConstraint("estimated_duration_days > 0"),
        CheckConstraint("estimated_hours >= 0"),
    )



