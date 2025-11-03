"""
Project-related Pydantic models for WhatsApp PM System v3.0 (Gamma)
Project management and team models
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from decimal import Decimal


class ProjectBase(BaseModel):
    """Base project model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    project_number: Optional[str] = Field(None, max_length=50, description="Unique project number")
    contract_type: str = Field("lump_sum", description="Type of contract")
    start_date: date = Field(..., description="Project start date")
    end_date: date = Field(..., description="Project end date")
    budget_total: Decimal = Field(..., ge=0, description="Total project budget")
    currency: str = Field("USD", max_length=3, description="Project currency")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v

    @validator('contract_type')
    def validate_contract_type(cls, v):
        """Validate contract type."""
        valid_types = ['lump_sum', 'cost_plus', 'time_materials', 'unit_price']
        if v not in valid_types:
            raise ValueError(f"Contract type must be one of: {', '.join(valid_types)}")
        return v


class ProjectCreate(ProjectBase):
    """Model for creating new projects."""
    location: Optional[Dict[str, Any]] = Field(None, description="Project location coordinates")
    address: Optional[Dict[str, Any]] = Field(None, description="Project address details")
    project_manager_id: Optional[UUID] = Field(None, description="Project manager user ID")
    client_contact: Optional[Dict[str, Any]] = Field(None, description="Client contact information")
    tags: Optional[List[str]] = Field(default_factory=list, description="Project tags")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom project fields")


class ProjectUpdate(BaseModel):
    """Model for updating existing projects."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    project_number: Optional[str] = Field(None, max_length=50)
    contract_type: Optional[str] = Field(None)
    start_date: Optional[date] = Field(None)
    end_date: Optional[date] = Field(None)
    actual_start_date: Optional[date] = Field(None)
    actual_end_date: Optional[date] = Field(None)
    budget_total: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = Field(None)
    location: Optional[Dict[str, Any]] = Field(None)
    address: Optional[Dict[str, Any]] = Field(None)
    project_manager_id: Optional[UUID] = Field(None)
    client_contact: Optional[Dict[str, Any]] = Field(None)
    tags: Optional[List[str]] = Field(None)
    custom_fields: Optional[Dict[str, Any]] = Field(None)

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date if both are provided."""
        if v and 'start_date' in values and values['start_date'] and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v

    @validator('actual_end_date')
    def validate_actual_end_date(cls, v, values):
        """Validate that actual end date is after actual start date if both are provided."""
        if v and 'actual_start_date' in values and values['actual_start_date'] and v <= values['actual_start_date']:
            raise ValueError("Actual end date must be after actual start date")
        return v

    @validator('contract_type')
    def validate_contract_type(cls, v):
        """Validate contract type."""
        if v is not None:
            valid_types = ['lump_sum', 'cost_plus', 'time_materials', 'unit_price']
            if v not in valid_types:
                raise ValueError(f"Contract type must be one of: {', '.join(valid_types)}")
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        """Validate risk level."""
        if v is not None:
            valid_levels = ['low', 'medium', 'high', 'critical']
            if v not in valid_levels:
                raise ValueError(f"Risk level must be one of: {', '.join(valid_levels)}")
        return v


class ProjectResponse(ProjectBase):
    """Response model for project data."""
    id: UUID
    tenant_id: UUID
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    progress_percentage: int
    actual_cost: Decimal
    risk_level: str
    health_score: Optional[Decimal]
    location: Optional[Dict[str, Any]]
    address: Optional[Dict[str, Any]]
    project_manager_id: Optional[UUID]
    client_contact: Optional[Dict[str, Any]]
    tags: List[str]
    custom_fields: Dict[str, Any]
    ai_insights: Dict[str, Any]
    risk_predictions: List[Dict[str, Any]]
    whatsapp_settings: Dict[str, Any]
    status: str
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberBase(BaseModel):
    """Base project member model."""
    user_id: UUID = Field(..., description="User ID")
    role: str = Field("member", description="Role in project")
    capacity_percentage: int = Field(100, ge=0, le=100, description="Work capacity percentage")
    permissions: Optional[List[str]] = Field(default_factory=lambda: ["read"], description="Member permissions")

    @validator('role')
    def validate_role(cls, v):
        """Validate project role."""
        valid_roles = ['owner', 'manager', 'lead', 'member', 'viewer']
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class ProjectMemberCreate(ProjectMemberBase):
    """Model for adding project members."""
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification preferences")


class ProjectMemberUpdate(BaseModel):
    """Model for updating project members."""
    role: Optional[str] = Field(None)
    capacity_percentage: Optional[int] = Field(None, ge=0, le=100)
    permissions: Optional[List[str]] = Field(None)
    is_active: Optional[bool] = Field(None, description="Whether member is active")
    notification_settings: Optional[Dict[str, Any]] = Field(None)

    @validator('role')
    def validate_role(cls, v):
        """Validate project role."""
        if v is not None:
            valid_roles = ['owner', 'manager', 'lead', 'member', 'viewer']
            if v not in valid_roles:
                raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class ProjectMemberResponse(BaseModel):
    """Response model for project member data."""
    id: UUID
    project_id: UUID
    user_id: UUID
    role: str
    permissions: List[str]
    capacity_percentage: int
    workload_hours: Decimal
    notification_settings: Dict[str, Any]
    assigned_at: datetime
    assigned_by: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDashboard(BaseModel):
    """Project dashboard summary."""
    project: ProjectResponse
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_cost: Decimal
    budget_utilization: Decimal
    team_members: int
    recent_activity: List[Dict[str, Any]]
    health_metrics: Dict[str, Any]


class ProjectStats(BaseModel):
    """Project statistics for reporting."""
    total_projects: int
    active_projects: int
    completed_projects: int
    total_budget: Decimal
    total_actual_cost: Decimal
    average_health_score: Optional[Decimal]
    projects_by_status: Dict[str, int]
    projects_by_risk: Dict[str, int]


class ProjectSearchFilters(BaseModel):
    """Filters for project search and listing."""
    status: Optional[str] = Field(None)
    risk_level: Optional[str] = Field(None)
    project_manager_id: Optional[UUID] = Field(None)
    start_date_from: Optional[date] = Field(None)
    start_date_to: Optional[date] = Field(None)
    end_date_from: Optional[date] = Field(None)
    end_date_to: Optional[date] = Field(None)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    tags: Optional[List[str]] = Field(None)
    search_query: Optional[str] = Field(None, description="Full-text search query")
