"""
Task-related Pydantic models for WhatsApp PM System v3.0 (Gamma)
Task management, scheduling, and CPM models
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class TaskBase(BaseModel):
    """Base task model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    task_code: Optional[str] = Field(None, max_length=50, description="Unique task code")
    planned_start_date: Optional[date] = Field(None, description="Planned start date")
    planned_end_date: Optional[date] = Field(None, description="Planned end date")
    planned_duration_days: Optional[int] = Field(None, gt=0, description="Planned duration in days")
    progress_percentage: int = Field(0, ge=0, le=100, description="Task progress percentage")
    assigned_to: Optional[UUID] = Field(None, description="Assigned user ID")
    estimated_hours: Optional[Decimal] = Field(None, ge=0, description="Estimated hours")
    budgeted_cost: Decimal = Field(0, ge=0, description="Budgeted cost")

    @validator('planned_end_date')
    def validate_planned_dates(cls, v, values):
        """Validate that planned end date is after planned start date."""
        if v and 'planned_start_date' in values and values['planned_start_date'] and v <= values['planned_start_date']:
            raise ValueError("Planned end date must be after planned start date")
        return v


class TaskCreate(TaskBase):
    """Model for creating new tasks."""
    project_id: UUID = Field(..., description="Project ID")
    parent_task_id: Optional[UUID] = Field(None, description="Parent task ID for hierarchy")
    predecessor_tasks: Optional[List[UUID]] = Field(default_factory=list, description="Predecessor task IDs")
    successor_tasks: Optional[List[UUID]] = Field(default_factory=list, description="Successor task IDs")
    lag_days: int = Field(0, description="Lag days after predecessor tasks")
    tags: Optional[List[str]] = Field(default_factory=list, description="Task tags")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom task fields")


class TaskUpdate(BaseModel):
    """Model for updating existing tasks."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    task_code: Optional[str] = Field(None, max_length=50)
    planned_start_date: Optional[date] = Field(None)
    planned_end_date: Optional[date] = Field(None)
    actual_start_date: Optional[date] = Field(None)
    actual_end_date: Optional[date] = Field(None)
    planned_duration_days: Optional[int] = Field(None, gt=0)
    actual_duration_days: Optional[int] = Field(None, ge=0)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None)
    assigned_to: Optional[UUID] = Field(None)
    estimated_hours: Optional[Decimal] = Field(None, ge=0)
    actual_hours: Optional[Decimal] = Field(None, ge=0)
    budgeted_cost: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    predecessor_tasks: Optional[List[UUID]] = Field(None)
    successor_tasks: Optional[List[UUID]] = Field(None)
    lag_days: Optional[int] = Field(None)
    tags: Optional[List[str]] = Field(None)
    custom_fields: Optional[Dict[str, Any]] = Field(None)

    @validator('planned_end_date')
    def validate_planned_dates(cls, v, values):
        """Validate that planned end date is after planned start date if both are provided."""
        if v and 'planned_start_date' in values and values['planned_start_date'] and v <= values['planned_start_date']:
            raise ValueError("Planned end date must be after planned start date")
        return v

    @validator('actual_end_date')
    def validate_actual_dates(cls, v, values):
        """Validate that actual end date is after actual start date if both are provided."""
        if v and 'actual_start_date' in values and values['actual_start_date'] and v <= values['actual_start_date']:
            raise ValueError("Actual end date must be after actual start date")
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate task status."""
        if v is not None:
            valid_statuses = ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class TaskResponse(TaskBase):
    """Response model for task data."""
    id: UUID
    project_id: UUID
    parent_task_id: Optional[UUID]
    level: int
    wbs_code: Optional[str]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    actual_duration_days: Optional[int]
    status: str
    actual_hours: Optional[Decimal]
    actual_cost: Decimal
    is_critical_path: bool
    slack_days: int
    ai_priority_score: Optional[Decimal]
    ai_risk_score: Optional[Decimal]
    ai_insights: Dict[str, Any]
    predecessor_tasks: List[UUID]
    successor_tasks: List[UUID]
    lag_days: int
    tags: List[str]
    custom_fields: Dict[str, Any]
    ai_metadata: Dict[str, Any]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDependency(BaseModel):
    """Model for task dependencies."""
    predecessor_id: UUID = Field(..., description="Predecessor task ID")
    successor_id: UUID = Field(..., description="Successor task ID")
    lag_days: int = Field(0, description="Lag days between tasks")
    dependency_type: str = Field("finish_to_start", description="Type of dependency")

    @validator('dependency_type')
    def validate_dependency_type(cls, v):
        """Validate dependency type."""
        valid_types = ['finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish']
        if v not in valid_types:
            raise ValueError(f"Dependency type must be one of: {', '.join(valid_types)}")
        return v


class TaskSchedule(BaseModel):
    """Task schedule information for CPM calculations."""
    task_id: UUID
    earliest_start: date
    earliest_finish: date
    latest_start: date
    latest_finish: date
    slack: int
    is_critical: bool
    duration: int


class CPMResult(BaseModel):
    """Result of Critical Path Method calculation."""
    critical_path: List[UUID] = Field(..., description="IDs of tasks on critical path")
    total_duration: int = Field(..., description="Total project duration in days")
    task_schedules: List[TaskSchedule] = Field(..., description="Schedule for each task")
    bottlenecks: List[Dict[str, Any]] = Field(default_factory=list, description="Identified bottlenecks")


class GanttData(BaseModel):
    """Data structure for Gantt chart visualization."""
    tasks: List[TaskResponse] = Field(..., description="All tasks in project")
    dependencies: List[TaskDependency] = Field(..., description="Task dependencies")
    milestones: List[Dict[str, Any]] = Field(default_factory=list, description="Project milestones")
    critical_path: List[UUID] = Field(default_factory=list, description="Critical path task IDs")
    today_line: date = Field(default_factory=date.today, description="Current date line")


class TaskSearchFilters(BaseModel):
    """Filters for task search and listing."""
    project_id: Optional[UUID] = Field(None)
    status: Optional[str] = Field(None)
    assigned_to: Optional[UUID] = Field(None)
    parent_task_id: Optional[UUID] = Field(None)
    planned_start_from: Optional[date] = Field(None)
    planned_start_to: Optional[date] = Field(None)
    planned_end_from: Optional[date] = Field(None)
    planned_end_to: Optional[date] = Field(None)
    progress_min: Optional[int] = Field(None, ge=0, le=100)
    progress_max: Optional[int] = Field(None, ge=0, le=100)
    is_critical_path: Optional[bool] = Field(None)
    tags: Optional[List[str]] = Field(None)
    search_query: Optional[str] = Field(None, description="Full-text search query")


class TaskStats(BaseModel):
    """Task statistics for project dashboard."""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    critical_path_tasks: int
    average_progress: Decimal
    total_estimated_hours: Decimal
    total_actual_hours: Decimal
    tasks_by_status: Dict[str, int]
    tasks_by_assignee: Dict[str, int]


class TaskBulkUpdate(BaseModel):
    """Model for bulk updating multiple tasks."""
    task_ids: List[UUID] = Field(..., description="IDs of tasks to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update on all tasks")

    @validator('updates')
    def validate_updates(cls, v):
        """Validate that only allowed fields can be bulk updated."""
        allowed_fields = {
            'status', 'assigned_to', 'progress_percentage', 'tags',
            'planned_start_date', 'planned_end_date', 'priority'
        }
        invalid_fields = set(v.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(f"Cannot bulk update fields: {', '.join(invalid_fields)}")
        return v


class TaskTemplate(BaseModel):
    """Template for creating standardized tasks."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Task category")
    estimated_duration_days: int = Field(..., gt=0, description="Estimated duration")
    estimated_hours: Decimal = Field(..., ge=0, description="Estimated hours")
    default_assignee_role: Optional[str] = Field(None, description="Default assignee role")
    subtasks: List[Dict[str, Any]] = Field(default_factory=list, description="Default subtasks")
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="Default dependencies")
    is_active: bool = Field(True, description="Whether template is active")


class TaskComment(BaseModel):
    """Model for task comments and notes."""
    task_id: UUID = Field(..., description="Task ID")
    content: str = Field(..., min_length=1, description="Comment content")
    comment_type: str = Field("comment", description="Type of comment")
    is_internal: bool = Field(False, description="Whether comment is internal only")
    mentioned_users: Optional[List[UUID]] = Field(None, description="Mentioned user IDs")

    @validator('comment_type')
    def validate_comment_type(cls, v):
        """Validate comment type."""
        valid_types = ['comment', 'status_change', 'assignment_change', 'progress_update', 'system']
        if v not in valid_types:
            raise ValueError(f"Comment type must be one of: {', '.join(valid_types)}")
        return v


class TaskCommentResponse(BaseModel):
    """Response model for task comments."""
    id: UUID
    task_id: UUID
    content: str
    comment_type: str
    is_internal: bool
    mentioned_users: List[UUID]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Advanced Scheduling Models (Week 4)

class ResourceLevelingResult(BaseModel):
    """Result of resource leveling optimization."""
    optimized_schedule: List[Dict[str, Any]] = Field(..., description="Optimized task schedules")
    resource_utilization: Dict[str, List[Dict[str, Any]]] = Field(..., description="Resource utilization over time")
    total_delays: int = Field(..., description="Total delay days introduced")
    optimization_score: float = Field(..., description="Optimization quality score (0-1)")


class SchedulingOptimizationResult(BaseModel):
    """Result of schedule optimization with constraints."""
    optimized_tasks: List[Dict[str, Any]] = Field(..., description="Optimized task schedules")
    objective_value: float = Field(..., description="Optimization objective value")
    optimization_goal: str = Field(..., description="Optimization goal used")
    constraints_applied: int = Field(..., description="Number of constraints applied")
    solution_found: bool = Field(..., description="Whether a valid solution was found")


class TaskConstraint(BaseModel):
    """Scheduling constraint for optimization."""
    constraint_type: str = Field(..., description="Type of constraint")
    task_id: Optional[UUID] = Field(None, description="Specific task ID (if applicable)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Constraint parameters")

    @validator('constraint_type')
    def validate_constraint_type(cls, v):
        """Validate constraint type."""
        valid_types = [
            'start_after', 'finish_before', 'max_duration',
            'resource_limit', 'dependency_chain', 'milestone_date'
        ]
        if v not in valid_types:
            raise ValueError(f"Constraint type must be one of: {', '.join(valid_types)}")
        return v


# Earned Value Management Models (Week 4)

class EarnedValueMetrics(BaseModel):
    """Complete Earned Value Management metrics for project performance."""
    project_id: UUID = Field(..., description="Project identifier")
    planned_value: Decimal = Field(..., description="Planned Value (PV) - budgeted cost of work scheduled")
    earned_value: Decimal = Field(..., description="Earned Value (EV) - budgeted cost of work performed")
    actual_cost: Decimal = Field(..., description="Actual Cost (AC) - actual cost incurred")
    budget_at_completion: Decimal = Field(..., description="Budget at Completion (BAC)")
    schedule_variance: Decimal = Field(..., description="Schedule Variance (SV) = EV - PV")
    cost_variance: Decimal = Field(..., description="Cost Variance (CV) = EV - AC")
    schedule_performance_index: Decimal = Field(..., description="Schedule Performance Index (SPI) = EV/PV")
    cost_performance_index: Decimal = Field(..., description="Cost Performance Index (CPI) = EV/AC")
    estimate_at_completion: Decimal = Field(..., description="Estimate at Completion (EAC)")
    estimate_to_complete: Decimal = Field(..., description="Estimate to Complete (ETC) = EAC - AC")
    variance_at_completion: Decimal = Field(..., description="Variance at Completion (VAC) = BAC - EAC")
    to_complete_performance_index: Decimal = Field(..., description="To Complete Performance Index (TCPI)")
    percent_complete: Decimal = Field(..., description="Percent Complete (PC) = EV/BAC * 100")
    calculated_at: datetime = Field(..., description="When metrics were calculated")


class EVMAnalysis(BaseModel):
    """Analysis and insights from EVM metrics."""
    schedule_status: str = Field(..., description="Schedule performance status")
    cost_status: str = Field(..., description="Cost performance status")
    forecast_completion_date: Optional[date] = Field(None, description="Forecasted completion date")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    risk_indicators: Dict[str, Any] = Field(default_factory=dict, description="Project risk indicators")
    analysis_date: datetime = Field(..., description="When analysis was performed")


class EVMPrediction(BaseModel):
    """Project outcome predictions based on EVM analysis."""
    predicted_final_cost: Decimal = Field(..., description="Predicted final project cost")
    predicted_completion_date: Optional[date] = Field(None, description="Predicted completion date")
    cost_confidence_interval: Dict[str, Decimal] = Field(..., description="Cost prediction confidence interval")
    schedule_confidence_interval: Dict[str, date] = Field(..., description="Schedule prediction confidence interval")
    success_probability: Decimal = Field(..., description="Probability of project success (0-100)")
    key_risks: List[str] = Field(default_factory=list, description="Key project risks identified")
    prediction_date: datetime = Field(..., description="When prediction was made")


# Baseline Management Models (Week 4)

class TaskBaseline(BaseModel):
    """Task baseline for tracking changes over time."""
    task_id: UUID = Field(..., description="Task ID")
    baseline_version: str = Field(..., description="Baseline version identifier")
    name: str = Field(..., description="Task name at baseline")
    description: Optional[str] = Field(None, description="Task description at baseline")
    planned_start_date: Optional[date] = Field(None, description="Planned start date at baseline")
    planned_end_date: Optional[date] = Field(None, description="Planned end date at baseline")
    planned_duration_days: Optional[int] = Field(None, description="Planned duration at baseline")
    budgeted_cost: Decimal = Field(..., description="Budgeted cost at baseline")
    estimated_hours: Optional[Decimal] = Field(None, description="Estimated hours at baseline")
    predecessor_tasks: List[UUID] = Field(default_factory=list, description="Predecessor tasks at baseline")
    successor_tasks: List[UUID] = Field(default_factory=list, description="Successor tasks at baseline")
    created_at: datetime = Field(..., description="When baseline was created")
    created_by: UUID = Field(..., description="User who created the baseline")


class TaskBaselineComparison(BaseModel):
    """Comparison between current task state and baseline."""
    task_id: UUID = Field(..., description="Task ID")
    baseline_version: str = Field(..., description="Baseline version compared")
    changes: Dict[str, Dict[str, Any]] = Field(..., description="Changes detected (field -> {old_value, new_value})")
    change_summary: str = Field(..., description="Summary of changes")
    severity: str = Field(..., description="Change severity (low, medium, high, critical)")
    compared_at: datetime = Field(..., description="When comparison was made")


class ProjectBaseline(BaseModel):
    """Project baseline containing all task baselines."""
    project_id: UUID = Field(..., description="Project ID")
    baseline_version: str = Field(..., description="Baseline version identifier")
    name: str = Field(..., description="Baseline name")
    description: Optional[str] = Field(None, description="Baseline description")
    task_baselines: List[TaskBaseline] = Field(..., description="All task baselines in this project baseline")
    total_budget: Decimal = Field(..., description="Total project budget at baseline")
    planned_duration_days: int = Field(..., description="Total planned project duration at baseline")
    created_at: datetime = Field(..., description="When baseline was created")
    created_by: UUID = Field(..., description="User who created the baseline")


class BaselineCreateRequest(BaseModel):
    """Request to create a new baseline."""
    name: str = Field(..., description="Baseline name")
    description: Optional[str] = Field(None, description="Baseline description")
    task_ids: Optional[List[UUID]] = Field(None, description="Specific task IDs to baseline (all if not specified)")


# Reporting Models (Week 4)

class ReportTemplate(BaseModel):
    """Report template configuration."""
    id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: str = Field(..., description="Type of report (task, project, evm, etc.)")
    sections: List[Dict[str, Any]] = Field(..., description="Report sections configuration")
    is_active: bool = Field(True, description="Whether template is active")


class ReportRequest(BaseModel):
    """Request to generate a report."""
    report_type: str = Field(..., description="Type of report to generate")
    template_id: Optional[str] = Field(None, description="Report template to use")
    project_id: Optional[UUID] = Field(None, description="Project ID for project-specific reports")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Report filters")
    date_range: Optional[Dict[str, date]] = Field(None, description="Date range for the report")
    include_charts: bool = Field(True, description="Whether to include charts in the report")
    format: str = Field("pdf", description="Report format (pdf, excel, etc.)")


class ReportGenerationResult(BaseModel):
    """Result of report generation."""
    report_id: str = Field(..., description="Unique report identifier")
    filename: str = Field(..., description="Generated report filename")
    file_path: str = Field(..., description="Path to generated report file")
    report_type: str = Field(..., description="Type of report generated")
    generated_at: datetime = Field(..., description="When report was generated")
    file_size_bytes: int = Field(..., description="Size of generated report file")


# JSON Task Structure & Import/Export Models (Week 4)

class JsonTaskStructure(BaseModel):
    """JSON structure for task data import/export and templates."""
    id: Optional[str] = Field(None, description="Task ID (optional for import)")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    task_code: Optional[str] = Field(None, description="Unique task code")
    status: str = Field("not_started", description="Task status")
    progress_percentage: int = Field(0, description="Progress percentage (0-100)")
    priority: Optional[str] = Field(None, description="Task priority")

    # Dates
    planned_start_date: Optional[str] = Field(None, description="Planned start date (YYYY-MM-DD)")
    planned_end_date: Optional[str] = Field(None, description="Planned end date (YYYY-MM-DD)")
    actual_start_date: Optional[str] = Field(None, description="Actual start date (YYYY-MM-DD)")
    actual_end_date: Optional[str] = Field(None, description="Actual end date (YYYY-MM-DD)")

    # Duration and effort
    planned_duration_days: Optional[int] = Field(None, description="Planned duration in days")
    actual_duration_days: Optional[int] = Field(None, description="Actual duration in days")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours")
    actual_hours: Optional[float] = Field(None, description="Actual hours")

    # Financial
    budgeted_cost: float = Field(0.0, description="Budgeted cost")
    actual_cost: float = Field(0.0, description="Actual cost")

    # Relationships
    parent_task_id: Optional[str] = Field(None, description="Parent task ID")
    predecessor_tasks: List[str] = Field(default_factory=list, description="Predecessor task IDs")
    successor_tasks: List[str] = Field(default_factory=list, description="Successor task IDs")
    lag_days: int = Field(0, description="Lag days after predecessor tasks")

    # Assignment
    assigned_to: Optional[str] = Field(None, description="Assigned user ID or email")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Task tags")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")

    # Hierarchy (for nested structures)
    subtasks: List['JsonTaskStructure'] = Field(default_factory=list, description="Child tasks")

    # Dependencies (alternative format)
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="Task dependencies")

    class Config:
        allow_population_by_field_name = True


class JsonProjectStructure(BaseModel):
    """JSON structure for complete project data import/export."""
    id: Optional[str] = Field(None, description="Project ID (optional for import)")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field("planning", description="Project status")

    # Dates
    start_date: Optional[str] = Field(None, description="Project start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Project end date (YYYY-MM-DD)")
    planned_start_date: Optional[str] = Field(None, description="Planned start date (YYYY-MM-DD)")
    planned_end_date: Optional[str] = Field(None, description="Planned end date (YYYY-MM-DD)")

    # Financial
    budget: Optional[float] = Field(None, description="Project budget")
    currency: str = Field("USD", description="Budget currency")

    # Tasks
    tasks: List[JsonTaskStructure] = Field(default_factory=list, description="Project tasks")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Project tags")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")

    # Team
    team_members: List[str] = Field(default_factory=list, description="Team member IDs or emails")

    class Config:
        allow_population_by_field_name = True


class ImportExportRequest(BaseModel):
    """Request for import/export operations."""
    format: str = Field(..., description="File format (json, csv, excel)")
    include_subtasks: bool = Field(True, description="Include subtasks in export")
    include_dependencies: bool = Field(True, description="Include dependencies in export")
    date_format: str = Field("YYYY-MM-DD", description="Date format for export")
    include_metadata: bool = Field(True, description="Include metadata fields")


class ImportResult(BaseModel):
    """Result of data import operation."""
    total_records: int = Field(..., description="Total records processed")
    successful_imports: int = Field(..., description="Successfully imported records")
    failed_imports: int = Field(..., description="Failed imports")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Import errors")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")
    created_ids: List[str] = Field(default_factory=list, description="IDs of created records")


class ExportResult(BaseModel):
    """Result of data export operation."""
    filename: str = Field(..., description="Generated file name")
    file_path: str = Field(..., description="File path")
    record_count: int = Field(..., description="Number of records exported")
    file_size_bytes: int = Field(..., description="File size in bytes")
    generated_at: datetime = Field(..., description="Export timestamp")
    format: str = Field(..., description="Export format")


# Dependency Validation Models (Week 4)

class DependencyValidationResult(BaseModel):
    """Result of dependency validation."""
    is_valid: bool = Field(..., description="Whether dependencies are valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    circular_references: List[List[str]] = Field(default_factory=list, description="Detected circular references")
    orphaned_tasks: List[str] = Field(default_factory=list, description="Tasks with broken dependencies")
    invalid_dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="Invalid dependency details")


class DependencyGraph(BaseModel):
    """Task dependency graph structure."""
    nodes: List[str] = Field(..., description="Task IDs")
    edges: List[Tuple[str, str]] = Field(..., description="Dependency edges (predecessor, successor)")
    cycles: List[List[str]] = Field(default_factory=list, description="Detected cycles")
    longest_path: List[str] = Field(default_factory=list, description="Longest dependency chain")


# Conflict Resolution Models (Week 4)

class SchedulingConflict(BaseModel):
    """Detected scheduling conflict."""
    conflict_type: str = Field(..., description="Type of conflict")
    task_ids: List[str] = Field(..., description="Tasks involved in conflict")
    description: str = Field(..., description="Conflict description")
    severity: str = Field(..., description="Conflict severity (low, medium, high, critical)")
    suggested_resolution: str = Field(..., description="Suggested resolution")


class ConflictResolutionResult(BaseModel):
    """Result of conflict resolution."""
    conflicts_detected: int = Field(..., description="Number of conflicts detected")
    conflicts_resolved: int = Field(..., description="Number of conflicts resolved")
    unresolved_conflicts: List[SchedulingConflict] = Field(default_factory=list, description="Unresolved conflicts")
    applied_resolutions: List[Dict[str, Any]] = Field(default_factory=list, description="Applied resolutions")
    resolution_summary: str = Field(..., description="Summary of resolution actions")


# Deadline Notification Models (Week 4)

class DeadlineNotification(BaseModel):
    """Deadline notification configuration."""
    task_id: str = Field(..., description="Task ID")
    notification_type: str = Field(..., description="Type of notification")
    trigger_days_before: int = Field(..., description="Days before deadline to trigger")
    recipients: List[str] = Field(..., description="Notification recipients")
    message_template: str = Field(..., description="Notification message template")
    is_active: bool = Field(True, description="Whether notification is active")


class NotificationSchedule(BaseModel):
    """Scheduled notification."""
    id: str = Field(..., description="Schedule ID")
    task_id: str = Field(..., description="Task ID")
    notification_type: str = Field(..., description="Notification type")
    scheduled_time: datetime = Field(..., description="When to send notification")
    status: str = Field("pending", description="Schedule status")
    retry_count: int = Field(0, description="Number of retry attempts")
