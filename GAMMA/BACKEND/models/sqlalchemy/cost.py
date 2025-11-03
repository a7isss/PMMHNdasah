"""
SQLAlchemy models for cost management in WhatsApp PM System v3.0 (Gamma)
Cost items, BoQ, budget tracking, and financial management
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import uuid4
import structlog
from sqlalchemy import Column, String, DateTime, Date, Text, Integer, Boolean, DECIMAL, func, text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, VECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from database import Base
from schemas.base import BaseModel

logger = structlog.get_logger(__name__)


class CostItem(Base, BaseModel):
    """Cost item model with AI categorization and approval workflow."""

    __tablename__ = "cost_items"

    # Basic Information
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))

    # Financial
    budgeted_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    actual_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    committed_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Schedule
    planned_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_date: Mapped[Optional[date]] = mapped_column(Date)

    # Vendor/Supplier
    vendor_id: Mapped[Optional[str]] = mapped_column(String(36))
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    contract_reference: Mapped[Optional[str]] = mapped_column(String(100))

    # Approval Workflow
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Task Association
    task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"))

    # AI Integration
    ai_category_prediction: Mapped[Optional[str]] = mapped_column(String(100))
    ai_amount_forecast: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(12, 2))
    ai_risk_score: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(3, 2))
    ai_insights: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    embedding: Mapped[Optional[Any]] = mapped_column(VECTOR(1536))
    search_vector: Mapped[Any] = mapped_column(
        text,
        server_default=text("to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, ''))"),
        index=True
    )

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    ai_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="cost_items")
    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="cost_items")
    approved_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    comments: Mapped[List["CostComment"]] = relationship(
        "CostComment",
        back_populates="cost_item",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        text("CHECK (status IN ('planned', 'committed', 'approved', 'incurred', 'paid'))"),
        text("CHECK (actual_amount >= 0)"),
        text("CHECK (budgeted_amount >= 0)"),
        text("CHECK (ai_risk_score >= 0 AND ai_risk_score <= 1 OR ai_risk_score IS NULL)"),
    )

    def get_variance_amount(self) -> float:
        """Calculate cost variance amount."""
        return float(self.actual_amount - self.budgeted_amount)

    def get_variance_percentage(self) -> float:
        """Calculate cost variance percentage."""
        if self.budgeted_amount == 0:
            return 0.0
        return round((self.get_variance_amount() / float(self.budgeted_amount)) * 100, 2)

    def is_over_budget(self) -> bool:
        """Check if cost item is over budget."""
        return self.actual_amount > self.budgeted_amount

    def get_remaining_budget(self) -> float:
        """Calculate remaining budget."""
        return float(self.budgeted_amount - self.actual_amount)

    def can_approve(self, user: "User", project_member: "ProjectMember") -> bool:
        """Check if user can approve this cost item."""
        if not self.approval_required:
            return True

        # Project owner can approve anything
        if project_member.role == 'owner':
            return True

        # Manager can approve up to certain limits
        if project_member.role == 'manager':
            # Define approval limits by category
            limits = {
                'materials': 50000,
                'labor': 25000,
                'equipment': 100000,
                'subcontractors': 75000,
                'other': 10000
            }
            limit = limits.get(self.category, 10000)
            return float(self.budgeted_amount) <= limit

        # Lead can approve small amounts
        if project_member.role == 'lead':
            return float(self.budgeted_amount) <= 5000

        return False

    def get_approval_workflow_status(self) -> Dict[str, Any]:
        """Get approval workflow status."""
        if not self.approval_required:
            return {"status": "not_required", "approved": True}

        if self.status == 'approved':
            return {
                "status": "approved",
                "approved": True,
                "approved_by": self.approved_by,
                "approved_at": self.approved_at
            }

        if self.approved_by:
            return {
                "status": "pending_final_approval",
                "approved": False,
                "approved_by": self.approved_by
            }

        return {"status": "pending_approval", "approved": False}


class BillOfQuantities(Base, BaseModel):
    """Bill of Quantities model for project estimation."""

    __tablename__ = "bill_of_quantities"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    prepared_by: Mapped[str] = mapped_column(String(255), nullable=False)
    prepared_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")

    # Items stored as JSONB for flexibility
    items: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)

    # Relationships
    project: Mapped["Project"] = relationship("Project")

    # Constraints
    __table_args__ = (
        text("CHECK (approval_status IN ('draft', 'submitted', 'approved', 'rejected'))"),
        text("CHECK (total_amount >= 0)"),
    )

    def calculate_total_amount(self) -> float:
        """Recalculate total amount from items."""
        total = 0.0
        for item in self.items:
            quantity = float(item.get('quantity', 0))
            unit_rate = float(item.get('unit_rate', 0))
            total += quantity * unit_rate
        return round(total, 2)

    def validate_items(self) -> List[str]:
        """Validate BoQ items and return any errors."""
        errors = []
        for i, item in enumerate(self.items):
            if not item.get('item_number'):
                errors.append(f"Item {i+1}: Missing item number")
            if not item.get('description'):
                errors.append(f"Item {i+1}: Missing description")
            if item.get('quantity', 0) <= 0:
                errors.append(f"Item {i+1}: Invalid quantity")
            if item.get('unit_rate', 0) < 0:
                errors.append(f"Item {i+1}: Invalid unit rate")
        return errors

    def get_items_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by category."""
        categories = {}
        for item in self.items:
            category = item.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        return categories


class CostComment(Base, BaseModel):
    """Cost comment model for approval notes and updates."""

    __tablename__ = "cost_comments"

    cost_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("cost_items.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    comment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="comment")
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mentioned_users: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Relationships
    cost_item: Mapped["CostItem"] = relationship("CostItem", back_populates="comments")

    # Constraints
    __table_args__ = (
        text("CHECK (comment_type IN ('comment', 'approval_request', 'approval_granted', 'approval_rejected', 'payment_made', 'system'))"),
    )


class CostApprovalWorkflow(Base, BaseModel):
    """Cost approval workflow model."""

    __tablename__ = "cost_approval_workflows"

    cost_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("cost_items.id"), nullable=False, index=True)
    approval_level: Mapped[str] = mapped_column(String(20), nullable=False)
    approver_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    approval_limit: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    approval_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    comments: Mapped[Optional[str]] = mapped_column(Text)
    escalation_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    cost_item: Mapped["CostItem"] = relationship("CostItem")
    approver: Mapped["User"] = relationship("User")

    # Constraints
    __table_args__ = (
        text("CHECK (approval_level IN ('manager', 'senior_manager', 'director', 'cfo'))"),
        text("CHECK (approval_status IN ('pending', 'approved', 'rejected'))"),
        text("CHECK (approval_limit >= 0)"),
    )


class VendorContract(Base, BaseModel):
    """Vendor contract information model."""

    __tablename__ = "vendor_contracts"

    vendor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    contract_number: Mapped[str] = mapped_column(String(100), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    payment_terms: Mapped[str] = mapped_column(Text, nullable=False)
    scope_of_work: Mapped[str] = mapped_column(Text, nullable=False)
    deliverables: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
    penalties: Mapped[Optional[str]] = mapped_column(Text)
    contact_person: Mapped[Dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Constraints
    __table_args__ = (
        text("CHECK (contract_type IN ('supply', 'service', 'subcontract'))"),
        text("CHECK (end_date >= start_date)"),
        text("CHECK (total_value >= 0)"),
    )


class CostTemplate(Base, BaseModel):
    """Cost template model for standardized cost items."""

    __tablename__ = "cost_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    typical_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Constraints
    __table_args__ = (
        text("CHECK (typical_amount >= 0)"),
    )
