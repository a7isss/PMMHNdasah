"""
Cost-related Pydantic models for WhatsApp PM System v3.0 (Gamma)
Cost management, BoQ, and budget tracking models
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any, UUID
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class CostItemBase(BaseModel):
    """Base cost item model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Cost item name")
    description: Optional[str] = Field(None, description="Cost item description")
    category: str = Field(..., description="Cost category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Cost subcategory")
    budgeted_amount: Decimal = Field(..., ge=0, description="Budgeted amount")
    currency: str = Field("USD", max_length=3, description="Currency code")
    planned_date: Optional[date] = Field(None, description="Planned expenditure date")
    vendor_name: Optional[str] = Field(None, max_length=255, description="Vendor or supplier name")
    contract_reference: Optional[str] = Field(None, max_length=100, description="Contract reference number")

    @validator('category')
    def validate_category(cls, v):
        """Validate cost category."""
        valid_categories = [
            'labor', 'materials', 'equipment', 'subcontractors', 'permits',
            'insurance', 'utilities', 'transportation', 'accommodation',
            'tools', 'safety', 'quality_control', 'administration', 'other'
        ]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v


class CostItemCreate(CostItemBase):
    """Model for creating new cost items."""
    project_id: UUID = Field(..., description="Project ID")
    task_id: Optional[UUID] = Field(None, description="Associated task ID")
    tags: Optional[List[str]] = Field(default_factory=list, description="Cost item tags")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom cost fields")


class CostItemUpdate(BaseModel):
    """Model for updating existing cost items."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    subcategory: Optional[str] = Field(None, max_length=100)
    budgeted_amount: Optional[Decimal] = Field(None, ge=0)
    actual_amount: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    planned_date: Optional[date] = Field(None)
    actual_date: Optional[date] = Field(None)
    status: Optional[str] = Field(None)
    vendor_name: Optional[str] = Field(None, max_length=255)
    contract_reference: Optional[str] = Field(None, max_length=100)
    task_id: Optional[UUID] = Field(None)
    tags: Optional[List[str]] = Field(None)
    custom_fields: Optional[Dict[str, Any]] = Field(None)

    @validator('category')
    def validate_category(cls, v):
        """Validate cost category."""
        if v is not None:
            valid_categories = [
                'labor', 'materials', 'equipment', 'subcontractors', 'permits',
                'insurance', 'utilities', 'transportation', 'accommodation',
                'tools', 'safety', 'quality_control', 'administration', 'other'
            ]
            if v not in valid_categories:
                raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate cost status."""
        if v is not None:
            valid_statuses = ['planned', 'committed', 'approved', 'incurred', 'paid']
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class CostItemResponse(CostItemBase):
    """Response model for cost item data."""
    id: UUID
    project_id: UUID
    actual_amount: Decimal
    actual_date: Optional[date]
    status: str
    approval_required: bool
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    task_id: Optional[UUID]
    ai_category_prediction: Optional[str]
    ai_amount_forecast: Optional[Decimal]
    ai_risk_score: Optional[Decimal]
    ai_insights: Dict[str, Any]
    tags: List[str]
    custom_fields: Dict[str, Any]
    ai_metadata: Dict[str, Any]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillOfQuantitiesItem(BaseModel):
    """Model for Bill of Quantities (BoQ) items."""
    item_number: str = Field(..., description="BoQ item number")
    description: str = Field(..., description="Item description")
    unit: str = Field(..., description="Unit of measurement")
    quantity: Decimal = Field(..., gt=0, description="Required quantity")
    unit_rate: Decimal = Field(..., ge=0, description="Rate per unit")
    total_amount: Decimal = Field(..., ge=0, description="Total amount (calculated)")
    category: str = Field(..., description="BoQ category")
    specification: Optional[str] = Field(None, description="Technical specifications")
    drawings_reference: Optional[str] = Field(None, description="Drawing references")

    @validator('total_amount', always=True)
    def calculate_total(cls, v, values):
        """Calculate total amount from quantity and unit rate."""
        if 'quantity' in values and 'unit_rate' in values:
            return values['quantity'] * values['unit_rate']
        return v or Decimal('0')


class BillOfQuantities(BaseModel):
    """Complete Bill of Quantities for a project."""
    project_id: UUID = Field(..., description="Project ID")
    title: str = Field(..., description="BoQ title")
    version: str = Field("1.0", description="BoQ version")
    prepared_by: str = Field(..., description="Prepared by")
    prepared_date: date = Field(..., description="Preparation date")
    total_amount: Decimal = Field(..., ge=0, description="Total BoQ amount")
    currency: str = Field("USD", max_length=3, description="Currency")
    items: List[BillOfQuantitiesItem] = Field(..., description="BoQ items")
    notes: Optional[str] = Field(None, description="Additional notes")
    approval_status: str = Field("draft", description="Approval status")

    @validator('approval_status')
    def validate_approval_status(cls, v):
        """Validate approval status."""
        valid_statuses = ['draft', 'submitted', 'approved', 'rejected']
        if v not in valid_statuses:
            raise ValueError(f"Approval status must be one of: {', '.join(valid_statuses)}")
        return v


class BudgetVariance(BaseModel):
    """Budget variance analysis model."""
    cost_item_id: UUID
    budgeted_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    variance_percentage: Decimal
    variance_type: str  # 'favorable' or 'unfavorable'
    explanation: Optional[str]
    corrective_action: Optional[str]


class CostForecast(BaseModel):
    """Cost forecasting model."""
    project_id: UUID
    forecast_date: date
    forecasted_total_cost: Decimal
    confidence_level: Decimal  # 0-1
    forecast_method: str  # 'linear', 'exponential', 'ai_prediction'
    assumptions: List[str]
    risk_factors: List[str]


class CostReport(BaseModel):
    """Comprehensive cost report."""
    project_id: UUID
    report_period: Dict[str, date]  # start_date, end_date
    total_budget: Decimal
    total_actual_cost: Decimal
    total_committed_cost: Decimal
    budget_utilization: Decimal
    cost_variance: Decimal
    cost_variance_percentage: Decimal
    category_breakdown: Dict[str, Dict[str, Decimal]]  # category -> {budgeted, actual, variance}
    monthly_spending: List[Dict[str, Any]]  # monthly cost data
    top_cost_items: List[Dict[str, Any]]  # highest cost items
    forecast_accuracy: Optional[Decimal]
    recommendations: List[str]


class CostSearchFilters(BaseModel):
    """Filters for cost item search and listing."""
    project_id: Optional[UUID] = Field(None)
    category: Optional[str] = Field(None)
    subcategory: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    vendor_name: Optional[str] = Field(None)
    planned_date_from: Optional[date] = Field(None)
    planned_date_to: Optional[date] = Field(None)
    actual_date_from: Optional[date] = Field(None)
    actual_date_to: Optional[date] = Field(None)
    budgeted_amount_min: Optional[Decimal] = Field(None, ge=0)
    budgeted_amount_max: Optional[Decimal] = Field(None, ge=0)
    actual_amount_min: Optional[Decimal] = Field(None, ge=0)
    actual_amount_max: Optional[Decimal] = Field(None, ge=0)
    tags: Optional[List[str]] = Field(None)
    search_query: Optional[str] = Field(None, description="Full-text search query")


class CostStats(BaseModel):
    """Cost statistics for project dashboard."""
    total_budgeted: Decimal
    total_actual: Decimal
    total_committed: Decimal
    budget_utilization: Decimal
    cost_variance: Decimal
    cost_variance_percentage: Decimal
    categories_count: int
    approved_items: int
    pending_approval: int
    overdue_payments: int
    costs_by_category: Dict[str, Decimal]
    monthly_spending_trend: List[Dict[str, Any]]


class CostApprovalWorkflow(BaseModel):
    """Cost approval workflow model."""
    cost_item_id: UUID
    approval_level: str  # 'manager', 'senior_manager', 'director', 'cfo'
    approver_id: UUID
    approval_limit: Decimal
    approval_status: str  # 'pending', 'approved', 'rejected'
    approval_date: Optional[datetime]
    comments: Optional[str]
    escalation_required: bool = False

    @validator('approval_level')
    def validate_approval_level(cls, v):
        """Validate approval level."""
        valid_levels = ['manager', 'senior_manager', 'director', 'cfo']
        if v not in valid_levels:
            raise ValueError(f"Approval level must be one of: {', '.join(valid_levels)}")
        return v

    @validator('approval_status')
    def validate_approval_status(cls, v):
        """Validate approval status."""
        valid_statuses = ['pending', 'approved', 'rejected']
        if v not in valid_statuses:
            raise ValueError(f"Approval status must be one of: {', '.join(valid_statuses)}")
        return v


class VendorContract(BaseModel):
    """Vendor contract information."""
    vendor_id: UUID
    contract_number: str
    contract_type: str  # 'supply', 'service', 'subcontract'
    start_date: date
    end_date: date
    total_value: Decimal
    currency: str
    payment_terms: str
    scope_of_work: str
    deliverables: List[str]
    penalties: Optional[str]
    contact_person: Dict[str, str]  # name, email, phone
    is_active: bool = True

    @validator('contract_type')
    def validate_contract_type(cls, v):
        """Validate contract type."""
        valid_types = ['supply', 'service', 'subcontract']
        if v not in valid_types:
            raise ValueError(f"Contract type must be one of: {', '.join(valid_types)}")
        return v


class CostBulkUpdate(BaseModel):
    """Model for bulk updating multiple cost items."""
    cost_item_ids: List[UUID] = Field(..., description="IDs of cost items to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update on all items")

    @validator('updates')
    def validate_updates(cls, v):
        """Validate that only allowed fields can be bulk updated."""
        allowed_fields = {
            'status', 'category', 'vendor_name', 'planned_date',
            'actual_date', 'tags', 'approval_required'
        }
        invalid_fields = set(v.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(f"Cannot bulk update fields: {', '.join(invalid_fields)}")
        return v


class CostTemplate(BaseModel):
    """Template for creating standardized cost items."""
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Cost category")
    subcategory: Optional[str] = Field(None, description="Cost subcategory")
    typical_amount: Decimal = Field(..., ge=0, description="Typical amount")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    description: str = Field(..., description="Template description")
    is_active: bool = Field(True, description="Whether template is active")


class CostComment(BaseModel):
    """Model for cost item comments and notes."""
    cost_item_id: UUID = Field(..., description="Cost item ID")
    content: str = Field(..., min_length=1, description="Comment content")
    comment_type: str = Field("comment", description="Type of comment")
    is_internal: bool = Field(False, description="Whether comment is internal only")
    mentioned_users: Optional[List[UUID]] = Field(None, description="Mentioned user IDs")

    @validator('comment_type')
    def validate_comment_type(cls, v):
        """Validate comment type."""
        valid_types = ['comment', 'approval_request', 'approval_granted', 'approval_rejected', 'payment_made', 'system']
        if v not in valid_types:
            raise ValueError(f"Comment type must be one of: {', '.join(valid_types)}")
        return v


class CostCommentResponse(BaseModel):
    """Response model for cost comments."""
    id: UUID
    cost_item_id: UUID
    content: str
    comment_type: str
    is_internal: bool
    mentioned_users: List[UUID]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True
