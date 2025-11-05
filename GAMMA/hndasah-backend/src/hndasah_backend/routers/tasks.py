"""
Tasks router for WhatsApp PM System v3.0 (Gamma)
Task management, scheduling, and CPM endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text, or_, and_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta

from ..database import get_db
from ..models.sqlalchemy.task import Task, TaskComment, TaskDependency, TaskTemplate
from ..models.sqlalchemy.project import Project
from ..models.sqlalchemy.user import User
from ..schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskSearchFilters,
    TaskStats, TaskBulkUpdate, TaskDependency as TaskDepSchema,
    CPMResult, GanttData, TaskSchedule, TaskComment as TaskCommentSchema,
    TaskCommentResponse, TaskTemplate as TaskTemplateSchema,
    ProjectBaseline, BaselineCreateRequest, TaskBaselineComparison,
    ReportGenerationResult, ReportRequest, EarnedValueMetrics, EVMAnalysis, EVMPrediction,
    ImportResult, ExportResult, ImportExportRequest, DependencyValidationResult, DependencyGraph,
    SchedulingConflict, ConflictResolutionResult
)
from ..utils.security import get_current_user
from ..services.ai_service import AIService
from ..services.notification_service import NotificationService
from ..services.task_service import TaskService
from ..services.scheduling_service import AdvancedSchedulingService
from ..services.earned_value_service import EarnedValueService
from ..services.baseline_service import BaselineService
from ..services.reporting_service import ReportingService
from ..services.import_export_service import ImportExportService
from ..services.dependency_validation_service import DependencyValidationService
from ..services.conflict_resolution_service import ConflictResolutionService
from ..services.deadline_notification_service import DeadlineNotificationService

router = APIRouter()
ai_service = AIService()
notification_service = NotificationService()
task_service = TaskService()


async def check_task_access(task_id: UUID, current_user: User, db: AsyncSession, require_owner: bool = False) -> bool:
    """Check if user has access to a task."""
    # Get task with project info
    query = select(Task).join(Project).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        return False

    # Check if user is project member
    member_query = select(Project.members).where(
        and_(
            Project.id == task.project_id,
            Project.members.any(User.id == current_user.id)
        )
    )
    member_result = await db.execute(member_query)
    is_member = member_result.scalar_one_or_none() is not None

    if not is_member:
        return False

    if require_owner:
        # Check if user is project owner/manager
        owner_query = select(Project.members).where(
            and_(
                Project.id == task.project_id,
                Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
            )
        )
        owner_result = await db.execute(owner_query)
        return owner_result.scalar_one_or_none() is not None

    return True


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    search: Optional[str] = None,
    parent_task_id: Optional[UUID] = None,
    is_critical_path: Optional[bool] = None
):
    """List tasks for a project with filtering and search."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if user is project member
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Build query
    query = select(Task).where(
        and_(
            Task.project_id == project_id,
            Task.deleted_at.is_(None)
        )
    )

    # Apply filters
    if status:
        query = query.where(Task.status == status)
    if assigned_to:
        query = query.where(Task.assigned_to == assigned_to)
    if parent_task_id:
        query = query.where(Task.parent_task_id == parent_task_id)
    if is_critical_path is not None:
        query = query.where(Task.is_critical_path == is_critical_path)

    # Apply search
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Task.name.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Apply pagination and ordering
    query = query.order_by(Task.level, Task.created_at).offset(skip).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task."""
    try:
        # Use TaskService for business logic
        task = await task_service.create_task(task_data, project_id, current_user.id, db)

        # Background tasks
        background_tasks.add_task(ai_service.analyze_new_task, task)
        background_tasks.add_task(notification_service.notify_task_created, task, current_user)

        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error creating task", error=str(e), project_id=str(project_id))
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed task information."""
    # Check access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    # Get task with related data
    query = select(Task).options(
        selectinload(Task.subtasks),
        selectinload(Task.assigned_user),
        selectinload(Task.comments),
        selectinload(Task.cost_items)
    ).where(Task.id == task_id)

    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task information."""
    # Check access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Get task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ['predecessor_tasks', 'successor_tasks'] and value is not None:
            # Handle dependency updates separately
            continue
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    # Handle dependency updates
    if 'predecessor_tasks' in update_data and update_data['predecessor_tasks'] is not None:
        # Remove existing dependencies
        await db.execute(
            delete(TaskDependency).where(TaskDependency.successor_id == task_id)
        )

        # Add new dependencies
        for pred_id in update_data['predecessor_tasks']:
            dependency = TaskDependency(
                predecessor_id=pred_id,
                successor_id=task_id,
                lag_days=task.lag_days
            )
            db.add(dependency)

    await db.commit()
    await db.refresh(task)

    # Background tasks
    background_tasks.add_task(ai_service.analyze_task_update, task)
    background_tasks.add_task(notification_service.notify_task_updated, task, current_user)

    return task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a task."""
    # Check access with owner permission
    if not await check_task_access(task_id, current_user, db, require_owner=True):
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    # Get task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if task has subtasks
    subtask_count = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.parent_task_id == task_id,
                Task.deleted_at.is_(None)
            )
        )
    )
    if subtask_count.scalar() > 0:
        raise HTTPException(status_code=400, detail="Cannot delete task with active subtasks. Delete subtasks first.")

    # Soft delete task (set deleted_at timestamp)
    task.deleted_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    await db.commit()

    # Background tasks
    background_tasks.add_task(notification_service.notify_task_deleted, task, current_user)

    return {"message": "Task deleted successfully (soft delete)"}


@router.post("/projects/{project_id}/tasks/bulk-update", response_model=Dict[str, Any])
async def bulk_update_tasks(
    project_id: UUID,
    bulk_update: TaskBulkUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update multiple tasks."""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized for bulk operations on this project")

    # Validate task IDs belong to project
    task_query = select(Task.id).where(
        and_(
            Task.id.in_(bulk_update.task_ids),
            Task.project_id == project_id
        )
    )
    task_result = await db.execute(task_query)
    valid_task_ids = {row[0] for row in task_result.all()}

    if len(valid_task_ids) != len(bulk_update.task_ids):
        invalid_ids = set(bulk_update.task_ids) - valid_task_ids
        raise HTTPException(status_code=400, detail=f"Invalid task IDs: {list(invalid_ids)}")

    # Apply bulk update
    update_stmt = (
        update(Task)
        .where(Task.id.in_(bulk_update.task_ids))
        .values(**bulk_update.updates, updated_at=datetime.utcnow())
    )

    await db.execute(update_stmt)
    await db.commit()

    # Background tasks
    background_tasks.add_task(notification_service.notify_bulk_task_update, bulk_update.task_ids, bulk_update.updates, current_user)

    return {
        "message": f"Successfully updated {len(bulk_update.task_ids)} tasks",
        "updated_count": len(bulk_update.task_ids)
    }


@router.get("/projects/{project_id}/tasks/stats", response_model=TaskStats)
async def get_task_stats(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task statistics for a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Calculate statistics
    stats_query = select(
        func.count(Task.id).label('total_tasks'),
        func.sum(Task.estimated_hours).label('total_estimated_hours'),
        func.sum(Task.actual_hours).label('total_actual_hours'),
        func.avg(Task.progress_percentage).label('avg_progress')
    ).where(Task.project_id == project_id)

    stats_result = await db.execute(stats_query)
    stats_row = stats_result.first()

    # Status breakdown
    status_query = select(
        Task.status,
        func.count(Task.id).label('count')
    ).where(Task.project_id == project_id).group_by(Task.status)

    status_result = await db.execute(status_query)
    tasks_by_status = {row[0]: row[1] for row in status_result.all()}

    # Assignee breakdown
    assignee_query = select(
        Task.assigned_to,
        func.count(Task.id).label('count')
    ).where(
        and_(
            Task.project_id == project_id,
            Task.assigned_to.isnot(None)
        )
    ).group_by(Task.assigned_to)

    assignee_result = await db.execute(assignee_query)
    tasks_by_assignee = {}
    for row in assignee_result.all():
        assignee_id = str(row[0])
        tasks_by_assignee[assignee_id] = row[1]

    return TaskStats(
        total_tasks=stats_row[0] or 0,
        completed_tasks=tasks_by_status.get('completed', 0),
        in_progress_tasks=tasks_by_status.get('in_progress', 0),
        overdue_tasks=await calculate_overdue_tasks(project_id, db),
        critical_path_tasks=await calculate_critical_path_tasks(project_id, db),
        average_progress=round(stats_row[3] or 0, 2),
        total_estimated_hours=stats_row[1] or 0,
        total_actual_hours=stats_row[2] or 0,
        tasks_by_status=tasks_by_status,
        tasks_by_assignee=tasks_by_assignee
    )


@router.post("/projects/{project_id}/tasks/cpm", response_model=CPMResult)
async def calculate_cpm(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate Critical Path Method for project tasks."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get all tasks for CPM calculation
    tasks_query = select(Task).where(Task.project_id == project_id).order_by(Task.created_at)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks found for CPM calculation")

    # Perform CPM calculation
    cpm_result = await perform_cpm_calculation(tasks, db)

    # Update tasks with CPM results
    for task_schedule in cpm_result.task_schedules:
        await db.execute(
            update(Task).where(Task.id == task_schedule.task_id).values(
                is_critical_path=task_schedule.is_critical,
                slack_days=task_schedule.slack,
                updated_at=datetime.utcnow()
            )
        )

    await db.commit()

    return cpm_result


@router.get("/projects/{project_id}/tasks/gantt", response_model=GanttData)
async def get_gantt_data(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Gantt chart data for project tasks."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get tasks with dependencies
    tasks_query = select(Task).where(Task.project_id == project_id).order_by(Task.level, Task.created_at)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    # Get dependencies
    dep_query = select(TaskDependency).where(
        or_(
            TaskDependency.predecessor.has(project_id=project_id),
            TaskDependency.successor.has(project_id=project_id)
        )
    )
    dep_result = await db.execute(dep_query)
    dependencies = dep_result.scalars().all()

    # Convert to response format
    task_responses = [TaskResponse.from_orm(task) for task in tasks]
    dep_schemas = [
        TaskDepSchema(
            predecessor_id=dep.predecessor_id,
            successor_id=dep.successor_id,
            lag_days=dep.lag_days,
            dependency_type=dep.dependency_type
        )
        for dep in dependencies
    ]

    # Get milestones (tasks with no successors or marked as milestones)
    milestones = await identify_milestones(tasks, db)

    return GanttData(
        tasks=task_responses,
        dependencies=dep_schemas,
        milestones=milestones,
        critical_path=await get_critical_path_task_ids(project_id, db),
        today_line=date.today()
    )


@router.post("/tasks/{task_id}/comments", response_model=TaskCommentResponse)
async def add_task_comment(
    task_id: UUID,
    comment_data: TaskCommentSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a task."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to comment on this task")

    # Create comment
    db_comment = TaskComment(
        task_id=task_id,
        content=comment_data.content,
        comment_type=comment_data.comment_type,
        is_internal=comment_data.is_internal,
        mentioned_users=comment_data.mentioned_users or [],
        created_by=current_user.id
    )

    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    # Background tasks
    background_tasks.add_task(notification_service.notify_task_comment, db_comment, current_user)

    return db_comment


@router.get("/tasks/{task_id}/comments", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get comments for a task."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to view comments for this task")

    # Get comments
    query = select(TaskComment).where(TaskComment.task_id == task_id).order_by(
        TaskComment.created_at.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    comments = result.scalars().all()

    return comments


# Helper functions

async def generate_wbs_code(project_id: UUID, parent_task_id: Optional[UUID], db: AsyncSession) -> str:
    """Generate WBS code for a task."""
    if parent_task_id:
        # Get parent task WBS code
        parent_query = select(Task.wbs_code).where(Task.id == parent_task_id)
        parent_result = await db.execute(parent_query)
        parent_wbs = parent_result.scalar_one_or_none()

        if parent_wbs:
            # Count siblings
            sibling_count_query = select(func.count(Task.id)).where(
                and_(
                    Task.parent_task_id == parent_task_id,
                    Task.project_id == project_id
                )
            )
            sibling_count = await db.execute(sibling_count_query)
            count = sibling_count.scalar() + 1
            return f"{parent_wbs}.{count}"

    # Root level task
    root_count_query = select(func.count(Task.id)).where(
        and_(
            Task.project_id == project_id,
            Task.parent_task_id.is_(None)
        )
    )
    root_count = await db.execute(root_count_query)
    count = root_count.scalar() + 1
    return str(count)


async def calculate_overdue_tasks(project_id: UUID, db: AsyncSession) -> int:
    """Calculate number of overdue tasks."""
    today = date.today()
    query = select(func.count(Task.id)).where(
        and_(
            Task.project_id == project_id,
            Task.status != 'completed',
            Task.planned_end_date < today
        )
    )
    result = await db.execute(query)
    return result.scalar()


async def calculate_critical_path_tasks(project_id: UUID, db: AsyncSession) -> int:
    """Count critical path tasks."""
    query = select(func.count(Task.id)).where(
        and_(
            Task.project_id == project_id,
            Task.is_critical_path == True
        )
    )
    result = await db.execute(query)
    return result.scalar()


async def perform_cpm_calculation(tasks: List[Task], db: AsyncSession) -> CPMResult:
    """Perform Critical Path Method calculation."""
    # This is a simplified CPM implementation
    # In a real implementation, this would be much more complex

    task_schedules = []
    critical_path = []
    total_duration = 0

    # Build dependency graph
    task_dict = {task.id: task for task in tasks}
    dependency_graph = {}

    for task in tasks:
        dependency_graph[task.id] = {
            'task': task,
            'predecessors': [],
            'successors': []
        }

    # Get dependencies from database
    dep_query = select(TaskDependency)
    dep_result = await db.execute(dep_query)
    dependencies = dep_result.scalars().all()

    for dep in dependencies:
        if dep.predecessor_id in dependency_graph and dep.successor_id in dependency_graph:
            dependency_graph[dep.successor_id]['predecessors'].append(dep.predecessor_id)
            dependency_graph[dep.predecessor_id]['successors'].append(dep.successor_id)

    # Forward pass - calculate earliest start/finish
    for task_id, node in dependency_graph.items():
        task = node['task']
        if not node['predecessors']:
            # No predecessors - can start at project start
            earliest_start = task.planned_start_date or date.today()
        else:
            # Earliest start is max of predecessor finish dates
            max_pred_finish = max(
                dependency_graph[pred_id]['task'].planned_end_date or date.today()
                for pred_id in node['predecessors']
            )
            earliest_start = max_pred_finish + timedelta(days=task.lag_days)

        earliest_finish = earliest_start + timedelta(days=task.planned_duration_days or 0)

        task_schedules.append(TaskSchedule(
            task_id=task_id,
            earliest_start=earliest_start,
            earliest_finish=earliest_finish,
            latest_start=earliest_start,  # Simplified
            latest_finish=earliest_finish,  # Simplified
            slack=0,  # Simplified
            is_critical=len(node['successors']) == 0 or task.planned_duration_days == 0,  # Simplified
            duration=task.planned_duration_days or 0
        ))

        if task_schedules[-1].is_critical:
            critical_path.append(task_id)

        total_duration = max(total_duration, (earliest_finish - (task.planned_start_date or date.today())).days)

    return CPMResult(
        critical_path=critical_path,
        total_duration=total_duration,
        task_schedules=task_schedules,
        bottlenecks=[]  # Simplified
    )


async def identify_milestones(tasks: List[Task], db: AsyncSession) -> List[Dict[str, Any]]:
    """Identify project milestones."""
    milestones = []

    for task in tasks:
        # Tasks with no successors or explicitly marked as milestones
        successor_count_query = select(func.count(TaskDependency.id)).where(
            TaskDependency.predecessor_id == task.id
        )
        successor_count = await db.execute(successor_count_query)

        if successor_count.scalar() == 0 or task.name.lower().find('milestone') >= 0:
            milestones.append({
                "id": str(task.id),
                "name": task.name,
                "date": task.planned_end_date,
                "type": "milestone" if task.name.lower().find('milestone') >= 0 else "endpoint"
            })

    return milestones


async def get_critical_path_task_ids(project_id: UUID, db: AsyncSession) -> List[UUID]:
    """Get IDs of tasks on the critical path."""
    query = select(Task.id).where(
        and_(
            Task.project_id == project_id,
            Task.is_critical_path == True
        )
    )
    result = await db.execute(query)
    return [row[0] for row in result.all()]


# Task Template Management

@router.get("/task-templates", response_model=List[TaskTemplateSchema])
async def list_task_templates(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List available task templates."""
    query = select(TaskTemplate).where(TaskTemplate.is_active == True)

    if category:
        query = query.where(TaskTemplate.category == category)

    result = await db.execute(query.order_by(TaskTemplate.category, TaskTemplate.name))
    templates = result.scalars().all()

    return templates


@router.post("/task-templates", response_model=TaskTemplateSchema)
async def create_task_template(
    template_data: TaskTemplateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task template (admin only)."""
    # Check if user is admin (simplified check)
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to create templates")

    # Create template
    db_template = TaskTemplate(**template_data.dict())
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)

    return db_template


@router.post("/projects/{project_id}/tasks/from-template", response_model=List[TaskResponse])
async def create_tasks_from_template(
    project_id: UUID,
    template_id: UUID,
    parent_task_id: Optional[UUID] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create tasks from a template."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to create tasks in this project")

    # Get template
    template_query = select(TaskTemplate).where(TaskTemplate.id == template_id)
    template_result = await db.execute(template_query)
    template = template_result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create tasks from template
    created_tasks = []
    task_mapping = {}  # Map template task IDs to actual task IDs

    # Create main task
    main_task_data = TaskCreate(
        project_id=project_id,
        name=template.name,
        description=template.description,
        planned_duration_days=template.estimated_duration_days,
        estimated_hours=template.estimated_hours,
        budgeted_cost=Decimal('0'),  # Templates don't have costs
        parent_task_id=parent_task_id,
        tags=["template-generated"]
    )

    main_task = await create_task(project_id, main_task_data, background_tasks, db, current_user)
    created_tasks.append(main_task)
    task_mapping["main"] = main_task.id

    # Create subtasks if any
    if template.subtasks:
        for subtask_data in template.subtasks:
            sub_task_data = TaskCreate(
                project_id=project_id,
                name=subtask_data.get("name", "Subtask"),
                description=subtask_data.get("description"),
                planned_duration_days=subtask_data.get("duration_days", 1),
                estimated_hours=subtask_data.get("estimated_hours"),
                budgeted_cost=Decimal('0'),
                parent_task_id=main_task.id,
                tags=["template-generated"]
            )

            subtask = await create_task(project_id, sub_task_data, background_tasks, db, current_user)
            created_tasks.append(subtask)

    # Create dependencies if any
    if template.dependencies:
        for dep_data in template.dependencies:
            pred_key = dep_data.get("predecessor")
            succ_key = dep_data.get("successor")

            if pred_key in task_mapping and succ_key in task_mapping:
                dependency = TaskDependency(
                    predecessor_id=task_mapping[pred_key],
                    successor_id=task_mapping[succ_key],
                    lag_days=dep_data.get("lag_days", 0),
                    dependency_type=dep_data.get("type", "finish_to_start")
                )
                db.add(dependency)

        await db.commit()

    return created_tasks


# Resource Allocation and Workload Management

@router.get("/projects/{project_id}/workload")
async def get_team_workload(
    project_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team workload analysis for a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Set date range
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=30)

    # Get tasks with assignments in date range
    tasks_query = select(Task).where(
        and_(
            Task.project_id == project_id,
            Task.assigned_to.isnot(None),
            Task.planned_start_date <= end_date,
            Task.planned_end_date >= start_date
        )
    ).options(selectinload(Task.assigned_user))

    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    # Calculate workload by user
    workload = {}
    for task in tasks:
        user_id = str(task.assigned_to)
        if user_id not in workload:
            workload[user_id] = {
                "user_id": user_id,
                "user_name": task.assigned_user.first_name + " " + task.assigned_user.last_name if task.assigned_user else "Unknown",
                "total_tasks": 0,
                "total_hours": 0,
                "tasks": []
            }

        workload[user_id]["total_tasks"] += 1
        workload[user_id]["total_hours"] += float(task.estimated_hours or 0)
        workload[user_id]["tasks"].append({
            "id": str(task.id),
            "name": task.name,
            "estimated_hours": float(task.estimated_hours or 0),
            "start_date": task.planned_start_date,
            "end_date": task.planned_end_date,
            "progress": task.progress_percentage
        })

    return {
        "project_id": str(project_id),
        "period": {"start": start_date, "end": end_date},
        "workload": list(workload.values())
    }


@router.post("/projects/{project_id}/tasks/auto-assign")
async def auto_assign_tasks(
    project_id: UUID,
    skill_requirements: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-assign tasks based on availability and skills."""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized for auto-assignment")

    # Get unassigned tasks
    unassigned_query = select(Task).where(
        and_(
            Task.project_id == project_id,
            Task.assigned_to.is_(None),
            Task.status == "not_started"
        )
    )
    unassigned_result = await db.execute(unassigned_query)
    unassigned_tasks = unassigned_result.scalars().all()

    # Get available team members
    members_query = select(Project.members).where(
        and_(
            Project.id == project_id,
            Project.members.is_active == True
        )
    ).options(selectinload(Project.members, User))

    members_result = await db.execute(members_query)
    members = members_result.scalars().all()

    # Simple auto-assignment logic (can be enhanced with AI)
    assignments = []
    for task in unassigned_tasks:
        # Find least loaded member
        best_member = None
        min_load = float('inf')

        for member in members:
            # Calculate current load (simplified)
            load_query = select(func.sum(Task.estimated_hours)).where(
                and_(
                    Task.assigned_to == member.user_id,
                    Task.status.in_(["not_started", "in_progress"])
                )
            )
            load_result = await db.execute(load_query)
            current_load = load_result.scalar() or 0

            if current_load < min_load:
                min_load = current_load
                best_member = member

        if best_member:
            # Assign task
            task.assigned_to = best_member.user_id
            task.updated_at = datetime.utcnow()
            assignments.append({
                "task_id": str(task.id),
                "task_name": task.name,
                "assigned_to": str(best_member.user_id),
                "assignee_name": f"{best_member.user.first_name} {best_member.user.last_name}"
            })

    await db.commit()

    return {
        "message": f"Auto-assigned {len(assignments)} tasks",
        "assignments": assignments
    }


# Progress Tracking and Updates

@router.put("/tasks/{task_id}/progress")
async def update_task_progress(
    task_id: UUID,
    progress_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task progress with automatic calculations."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    # Get task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update progress
    new_progress = progress_data.get("progress_percentage")
    actual_hours = progress_data.get("actual_hours")
    status = progress_data.get("status")

    if new_progress is not None:
        task.progress_percentage = new_progress

        # Auto-update status based on progress
        if new_progress == 100 and task.status != "completed":
            task.status = "completed"
            task.actual_end_date = date.today()
        elif new_progress > 0 and task.status == "not_started":
            task.status = "in_progress"
            if not task.actual_start_date:
                task.actual_start_date = date.today()

    if actual_hours is not None:
        task.actual_hours = actual_hours

    if status:
        task.status = status
        if status == "in_progress" and not task.actual_start_date:
            task.actual_start_date = date.today()
        elif status == "completed" and not task.actual_end_date:
            task.actual_end_date = date.today()

    task.updated_at = datetime.utcnow()

    # Update parent task progress if this is a subtask
    if task.parent_task_id:
        await update_parent_progress(task.parent_task_id, db)

    await db.commit()
    await db.refresh(task)

    # Background tasks
    background_tasks.add_task(ai_service.analyze_progress_update, task)
    background_tasks.add_task(notification_service.notify_progress_update, task, current_user)

    return task


async def update_parent_progress(parent_task_id: UUID, db: AsyncSession):
    """Update parent task progress based on subtasks."""
    # Get parent task
    parent_query = select(Task).where(Task.id == parent_task_id)
    parent_result = await db.execute(parent_query)
    parent_task = parent_result.scalar_one_or_none()

    if not parent_task:
        return

    # Get all subtasks
    subtasks_query = select(Task).where(Task.parent_task_id == parent_task_id)
    subtasks_result = await db.execute(subtasks_query)
    subtasks = subtasks_result.scalars().all()

    if not subtasks:
        return

    # Calculate average progress
    total_progress = sum(subtask.progress_percentage for subtask in subtasks)
    avg_progress = total_progress / len(subtasks)

    # Update parent progress
    parent_task.progress_percentage = int(avg_progress)

    # Update parent status
    completed_subtasks = sum(1 for s in subtasks if s.status == "completed")
    if completed_subtasks == len(subtasks):
        parent_task.status = "completed"
        parent_task.actual_end_date = date.today()
    elif any(s.status == "in_progress" for s in subtasks):
        parent_task.status = "in_progress"

    parent_task.updated_at = datetime.utcnow()
    await db.commit()

# Advanced Scheduling Endpoints (Week 4)

@router.post("/projects/{project_id}/tasks/resource-leveling")
async def optimize_resource_leveling(
    project_id: UUID,
    resource_constraints: Dict[str, int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimize resource leveling for project tasks using OR-Tools"""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized for resource optimization")

    # Get all project tasks
    tasks_query = select(Task).where(Task.project_id == project_id).order_by(Task.created_at)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks found for optimization")

    # Use advanced scheduling service
    scheduling_service = AdvancedSchedulingService()
    result = await scheduling_service.optimize_resource_leveling(tasks, resource_constraints, db)

    return result


# Baseline Management Endpoints (Week 4)

@router.post("/projects/{project_id}/baseline", response_model=ProjectBaseline)
async def create_project_baseline(
    project_id: UUID,
    baseline_request: BaselineCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new baseline for a project."""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized to create baselines")

    # Create baseline
    baseline_service = BaselineService()
    baseline = await baseline_service.create_project_baseline(
        project_id=project_id,
        baseline_request=baseline_request,
        created_by=current_user.id,
        db_session=db
    )

    return baseline


@router.get("/projects/{project_id}/baselines", response_model=List[ProjectBaseline])
async def get_project_baselines(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all baselines for a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get baselines
    baseline_service = BaselineService()
    baselines = await baseline_service.get_project_baselines(project_id, db)

    return baselines


@router.get("/tasks/{task_id}/baseline-comparison", response_model=TaskBaselineComparison)
async def compare_task_to_baseline(
    task_id: UUID,
    baseline_version: str = Query(..., description="Baseline version to compare against"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare current task state to a baseline version."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    # Compare to baseline
    baseline_service = BaselineService()
    comparison = await baseline_service.compare_task_to_baseline(
        task_id=task_id,
        baseline_version=baseline_version,
        db_session=db
    )

    return comparison


@router.post("/tasks/{task_id}/restore-baseline")
async def restore_task_from_baseline(
    task_id: UUID,
    baseline_version: str = Query(..., description="Baseline version to restore from"),
    fields_to_restore: Optional[List[str]] = Query(None, description="Specific fields to restore"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restore task fields from a baseline version."""
    # Check task access with manager permission
    if not await check_task_access(task_id, current_user, db, require_owner=True):
        raise HTTPException(status_code=403, detail="Not authorized to restore baselines")

    # Restore from baseline
    baseline_service = BaselineService()
    result = await baseline_service.restore_task_from_baseline(
        task_id=task_id,
        baseline_version=baseline_version,
        fields_to_restore=fields_to_restore,
        user_id=current_user.id,
        db_session=db
    )

    return result


# Reporting Endpoints (Week 4)

@router.post("/reports/generate", response_model=ReportGenerationResult)
async def generate_report(
    report_request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a PDF report."""
    try:
        reporting_service = ReportingService()

        if report_request.report_type == "task_report":
            # Get project and tasks
            project_query = select(Project).where(Project.id == report_request.project_id)
            project_result = await db.execute(project_query)
            project = project_result.scalar_one_or_none()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Check membership
            member_check = await db.execute(
                select(Project.members).where(
                    and_(
                        Project.id == report_request.project_id,
                        Project.members.any(User.id == current_user.id)
                    )
                )
            )
            if not member_check.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="Not authorized to access this project")

            # Get tasks
            tasks_query = select(Task).where(Task.project_id == report_request.project_id)
            tasks_result = await db.execute(tasks_query)
            tasks = tasks_result.scalars().all()

            # Generate task report
            result = await reporting_service.generate_task_report(tasks, project, report_request, db)

        elif report_request.report_type == "evm_report":
            # Get project
            project_query = select(Project).where(Project.id == report_request.project_id)
            project_result = await db.execute(project_query)
            project = project_result.scalar_one_or_none()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Check membership
            member_check = await db.execute(
                select(Project.members).where(
                    and_(
                        Project.id == report_request.project_id,
                        Project.members.any(User.id == current_user.id)
                    )
                )
            )
            if not member_check.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="Not authorized to access this project")

            # Get EVM data
            evm_service = EarnedValueService()
            evm_metrics = await evm_service.calculate_project_evm(
                project_id=report_request.project_id,
                tasks=[],  # Would need to get tasks
                project_budget=project.budget or Decimal('0'),
                project_start_date=project.start_date or date.today(),
                project_end_date=project.end_date or date.today(),
                db_session=db
            )

            evm_analysis = await evm_service.analyze_evm_performance(evm_metrics)

            # Get tasks for detailed EVM
            tasks_query = select(Task).where(Task.project_id == report_request.project_id)
            tasks_result = await db.execute(tasks_query)
            tasks = tasks_result.scalars().all()

            # Generate EVM report
            result = await reporting_service.generate_evm_report(
                evm_metrics, evm_analysis, project, tasks, report_request, db
            )

        elif report_request.report_type == "project_report":
            # Get project and tasks
            project_query = select(Project).where(Project.id == report_request.project_id)
            project_result = await db.execute(project_query)
            project = project_result.scalar_one_or_none()

            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Check membership
            member_check = await db.execute(
                select(Project.members).where(
                    and_(
                        Project.id == report_request.project_id,
                        Project.members.any(User.id == current_user.id)
                    )
                )
            )
            if not member_check.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="Not authorized to access this project")

            # Get tasks
            tasks_query = select(Task).where(Task.project_id == report_request.project_id)
            tasks_result = await db.execute(tasks_query)
            tasks = tasks_result.scalars().all()

            # Get EVM metrics if available
            evm_metrics = None
            try:
                evm_service = EarnedValueService()
                evm_metrics = await evm_service.calculate_project_evm(
                    project_id=report_request.project_id,
                    tasks=tasks,
                    project_budget=project.budget or Decimal('0'),
                    project_start_date=project.start_date or date.today(),
                    project_end_date=project.end_date or date.today(),
                    db_session=db
                )
            except Exception:
                # EVM calculation might fail, continue without it
                pass

            # Generate project report
            result = await reporting_service.generate_project_report(
                project, tasks, evm_metrics, report_request, db
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported report type: {report_request.report_type}")

        return result

    except Exception as e:
        logger.error("Report generation failed", error=str(e), report_type=report_request.report_type)
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/reports/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download a generated report file."""
    # In a real implementation, this would serve the PDF file
    # For now, return a placeholder response
    return {
        "message": f"Report {report_id} download not implemented yet",
        "report_id": report_id
    }


# Earned Value Management Endpoints (Week 4)

@router.get("/projects/{project_id}/evm/metrics", response_model=EarnedValueMetrics)
async def get_evm_metrics(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate and return Earned Value Management metrics for a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get project tasks
    tasks_query = select(Task).where(Task.project_id == project_id)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    # Calculate EVM metrics
    evm_service = EarnedValueService()
    evm_metrics = await evm_service.calculate_project_evm(
        project_id=project_id,
        tasks=tasks,
        project_budget=project.budget or Decimal('0'),
        project_start_date=project.start_date or date.today(),
        project_end_date=project.end_date or date.today(),
        db_session=db
    )

    return evm_metrics


@router.get("/projects/{project_id}/evm/analysis", response_model=EVMAnalysis)
async def get_evm_analysis(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Earned Value Management analysis and recommendations."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get EVM metrics first
    evm_metrics = await get_evm_metrics(project_id, db, current_user)

    # Analyze performance
    evm_service = EarnedValueService()
    analysis = await evm_service.analyze_evm_performance(evm_metrics)

    return analysis


@router.get("/projects/{project_id}/evm/prediction", response_model=EVMPrediction)
async def get_evm_prediction(
    project_id: UUID,
    historical_projects: Optional[List[str]] = Query(None, description="Historical project IDs for improved predictions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Earned Value Management predictions for project outcomes."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get EVM metrics first
    evm_metrics = await get_evm_metrics(project_id, db, current_user)

    # Prepare historical data if provided
    historical_data = None
    if historical_projects:
        # In a real implementation, this would fetch historical project data
        # For now, we'll use None and let the service handle defaults
        pass

    # Generate predictions
    evm_service = EarnedValueService()
    prediction = await evm_service.predict_project_outcomes(evm_metrics, historical_data)

    return prediction


@router.get("/projects/{project_id}/evm/dashboard")
async def get_evm_dashboard(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive EVM dashboard data for project monitoring."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get all EVM data
    evm_metrics = await get_evm_metrics(project_id, db, current_user)
    evm_analysis = await get_evm_analysis(project_id, db, current_user)
    evm_prediction = await get_evm_prediction(project_id, db, current_user)

    # Get project progress data
    tasks_query = select(Task).where(Task.project_id == project_id)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    # Calculate progress trends (simplified - would use historical data in real implementation)
    progress_trend = []
    for i in range(7):  # Last 7 days
        check_date = date.today() - timedelta(days=i)
        completed_tasks = sum(1 for task in tasks if task.actual_end_date and task.actual_end_date <= check_date)
        progress_trend.append({
            "date": check_date,
            "completed_tasks": completed_tasks,
            "total_tasks": len(tasks),
            "progress_percentage": (completed_tasks / len(tasks) * 100) if tasks else 0
        })

    return {
        "project_id": str(project_id),
        "project_name": project.name,
        "evm_metrics": evm_metrics,
        "evm_analysis": evm_analysis,
        "evm_prediction": evm_prediction,
        "progress_trend": progress_trend,
        "generated_at": datetime.utcnow()
    }


@router.post("/projects/{project_id}/tasks/schedule-optimization")
async def optimize_schedule(
    project_id: UUID,
    optimization_request: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimize project schedule with constraints using OR-Tools"""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized for schedule optimization")

    # Get all project tasks
    tasks_query = select(Task).where(Task.project_id == project_id).order_by(Task.created_at)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks found for optimization")

    # Extract optimization parameters
    constraints = optimization_request.get("constraints", [])
    optimization_goal = optimization_request.get("optimization_goal", "minimize_duration")

    # Use advanced scheduling service
    scheduling_service = AdvancedSchedulingService()
    result = await scheduling_service.optimize_schedule_with_constraints(
        tasks, constraints, optimization_goal
    )

    return result


# Import/Export Endpoints (Week 4)

@router.post("/projects/{project_id}/tasks/import", response_model=ImportResult)
async def import_tasks(
    project_id: UUID,
    import_request: ImportExportRequest,
    file_data: bytes = None,  # Would come from file upload in real implementation
    json_data: str = None,
    csv_data: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import tasks from various formats."""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized for import operations")

    import_service = ImportExportService()

    try:
        if import_request.format == "json" and json_data:
            result = await import_service.import_json_tasks(
                json_data=json_data,
                project_id=str(project_id),
                created_by=str(current_user.id),
                db_session=db
            )
        elif import_request.format == "csv" and csv_data:
            result = await import_service.import_csv_tasks(
                csv_content=csv_data,
                project_id=str(project_id),
                created_by=str(current_user.id),
                db_session=db
            )
        elif import_request.format == "excel" and file_data:
            result = await import_service.import_excel_tasks(
                excel_content=file_data,
                project_id=str(project_id),
                created_by=str(current_user.id),
                db_session=db
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid import format or missing data")

        return result

    except Exception as e:
        logger.error("Import failed", error=str(e), format=import_request.format)
        raise HTTPException(status_code=500, detail="Import failed")


@router.post("/projects/{project_id}/tasks/export", response_model=ExportResult)
async def export_tasks(
    project_id: UUID,
    export_request: ImportExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export tasks to various formats."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get tasks
    tasks_query = select(Task).where(Task.project_id == project_id)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    export_service = ImportExportService()

    try:
        if export_request.format == "json":
            result = await export_service.export_tasks_json(tasks, project, export_request, db)
        elif export_request.format == "csv":
            result = await export_service.export_tasks_csv(tasks, project, export_request, db)
        elif export_request.format == "excel":
            result = await export_service.export_tasks_excel(tasks, project, export_request, db)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

        return result

    except Exception as e:
        logger.error("Export failed", error=str(e), format=export_request.format)
        raise HTTPException(status_code=500, detail="Export failed")


# Dependency Validation Endpoints (Week 4)

@router.post("/projects/{project_id}/dependencies/validate", response_model=DependencyValidationResult)
async def validate_project_dependencies(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate all dependencies in a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    validation_service = DependencyValidationService()
    result = await validation_service.validate_project_dependencies(project_id, db)

    return result


@router.post("/tasks/{task_id}/dependencies/validate", response_model=DependencyValidationResult)
async def validate_task_dependencies(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate dependencies for a specific task."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    validation_service = DependencyValidationService()
    result = await validation_service.validate_task_dependencies(task_id, db)

    return result


@router.get("/projects/{project_id}/dependencies/graph", response_model=DependencyGraph)
async def get_dependency_graph(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dependency graph for a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Get tasks and dependencies
    tasks_query = select(Task).where(Task.project_id == project_id)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()

    dependencies_query = select(TaskDependency).where(
        or_(
            TaskDependency.predecessor.has(project_id=project_id),
            TaskDependency.successor.has(project_id=project_id)
        )
    )
    dependencies_result = await db.execute(dependencies_query)
    dependencies = dependencies_result.scalars().all()

    validation_service = DependencyValidationService()
    graph = validation_service._build_dependency_graph(tasks, dependencies)

    return graph


# Conflict Resolution Endpoints (Week 4)

@router.post("/projects/{project_id}/conflicts/detect", response_model=List[SchedulingConflict])
async def detect_project_conflicts(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect all scheduling conflicts in a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    conflict_service = ConflictResolutionService()
    conflicts = await conflict_service.detect_project_conflicts(project_id, db)

    return conflicts


@router.post("/projects/{project_id}/conflicts/resolve", response_model=ConflictResolutionResult)
async def resolve_project_conflicts(
    project_id: UUID,
    resolution_strategy: str = Query("auto", description="Resolution strategy"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve scheduling conflicts in a project."""
    # Check project access with manager permission
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(and_(User.id == current_user.id, Project.members.role.in_(["owner", "manager"])))
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=403, detail="Not authorized for conflict resolution")

    # First detect conflicts
    conflict_service = ConflictResolutionService()
    conflicts = await conflict_service.detect_project_conflicts(project_id, db)

    if not conflicts:
        return ConflictResolutionResult(
            conflicts_detected=0,
            conflicts_resolved=0,
            unresolved_conflicts=[],
            applied_resolutions=[],
            resolution_summary="No conflicts detected"
        )

    # Resolve conflicts
    result = await conflict_service.resolve_conflicts(conflicts, resolution_strategy, db)

    return result


@router.get("/projects/{project_id}/conflicts/statistics")
async def get_conflict_statistics(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conflict statistics for a project."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    conflict_service = ConflictResolutionService()
    stats = await conflict_service.get_conflict_statistics(project_id, db)

    return stats


# Deadline Notification Endpoints (Week 4)

@router.post("/tasks/{task_id}/notifications/setup")
async def setup_deadline_notifications(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Setup deadline notifications for a task."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    notification_service = DeadlineNotificationService()
    notifications = await notification_service.schedule_deadline_notifications(task_id, db)

    return {
        "message": f"Scheduled {len(notifications)} deadline notifications",
        "notifications": [n.dict() for n in notifications]
    }


@router.post("/tasks/{task_id}/notifications/escalation")
async def setup_escalation_workflow(
    task_id: UUID,
    escalation_rules: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Setup escalation workflow for a task."""
    # Check task access with manager permission
    if not await check_task_access(task_id, current_user, db, require_owner=True):
        raise HTTPException(status_code=403, detail="Not authorized to setup escalation workflows")

    notification_service = DeadlineNotificationService()
    escalations = await notification_service.setup_escalation_workflow(task_id, escalation_rules, db)

    return {
        "message": f"Setup {len(escalations)} escalation notifications",
        "escalations": [e.dict() for e in escalations]
    }


@router.get("/projects/{project_id}/deadlines")
async def get_upcoming_deadlines(
    project_id: UUID,
    days_ahead: int = Query(30, description="Days to look ahead"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming task deadlines."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    notification_service = DeadlineNotificationService()
    deadlines = await notification_service.get_upcoming_deadlines(project_id, days_ahead, db)

    return {"deadlines": deadlines}


@router.get("/projects/{project_id}/deadlines/summary")
async def get_deadline_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get deadline summary for monitoring."""
    # Check project access
    project_query = select(Project).where(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check membership
    member_check = await db.execute(
        select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.any(User.id == current_user.id)
            )
        )
    )
    if not member_check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    notification_service = DeadlineNotificationService()
    summary = await notification_service.get_deadline_summary(project_id, db)

    return summary


@router.post("/notifications/process")
async def process_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process pending notifications (admin/system function)."""
    # In a real implementation, this would be restricted to admin users
    # For now, allow any authenticated user

    notification_service = DeadlineNotificationService()
    stats = await notification_service.check_and_send_notifications(db)

    return {
        "message": "Notification processing completed",
        "statistics": stats
    }


@router.put("/tasks/{task_id}/notifications/reschedule")
async def reschedule_notifications(
    task_id: UUID,
    new_deadline: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reschedule notifications when task deadline changes."""
    # Check task access
    if not await check_task_access(task_id, current_user, db):
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    notification_service = DeadlineNotificationService()
    new_notifications = await notification_service.reschedule_notifications(task_id, new_deadline, db)

    return {
        "message": f"Rescheduled {len(new_notifications)} notifications",
        "notifications": [n.dict() for n in new_notifications]
    }
