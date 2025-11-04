"""
Projects router for WhatsApp PM System v3.0 (Gamma)
Project management endpoints with AI integration
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text, or_, and_
from sqlalchemy.orm import selectinload, joinedload

from ..database import get_db
from ..models.sqlalchemy import Project, ProjectMember, Task, CostItem, WhatsAppMessage, User
from schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberCreate,
    ProjectMemberUpdate, ProjectMemberResponse, ProjectDashboard,
    ProjectStats, ProjectSearchFilters
)
from middleware.auth_middleware import get_current_user
from middleware.tenant_middleware import get_current_tenant_id
from services.ai_service import AIService
from services.notification_service import NotificationService

# Initialize services
ai_service = AIService()
notification_service = NotificationService()

# Create router
router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)


async def check_project_access(
    project_id: UUID,
    current_user: User,
    db: AsyncSession,
    require_owner: bool = False
) -> bool:
    """Check if user has access to a project."""
    # Get project and check tenant
    project_query = select(Project).where(
        and_(Project.id == project_id, Project.tenant_id == current_user.tenant_id)
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        return False

    # If owner access required, check if user is owner or admin
    if require_owner:
        member_query = select(ProjectMember).where(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
                ProjectMember.role.in_(['owner', 'manager']),
                ProjectMember.is_active == True
            )
        )
        member_result = await db.execute(member_query)
        member = member_result.scalar_one_or_none()
        return member is not None

    # For read access, check if user is a member
    member_query = select(ProjectMember).where(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.is_active == True
        )
    )
    member_result = await db.execute(member_query)
    member = member_result.scalar_one_or_none()
    return member is not None


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    risk_level: Optional[str] = Query(None),
    project_manager_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("updated_at", enum=["created_at", "updated_at", "name", "health_score", "progress_percentage"]),
    sort_order: str = Query("desc", enum=["asc", "desc"])
):
    """List projects with filtering, search, and pagination."""

    # Base query with tenant isolation
    query = select(Project).where(Project.tenant_id == current_user.tenant_id)

    # Apply filters
    if status_filter:
        query = query.where(Project.status == status_filter)

    if risk_level:
        query = query.where(Project.risk_level == risk_level)

    if project_manager_id:
        query = query.where(Project.project_manager_id == project_manager_id)

    # Apply search
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.project_number.ilike(search_term)
            )
        )

    # Apply sorting
    sort_column = getattr(Project, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    projects = result.scalars().all()

    return projects


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project."""

    # Validate dates
    if project_data.end_date <= project_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )

    # Create project
    db_project = Project(
        **project_data.dict(),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        status="planning",
        progress_percentage=0,
        actual_cost=0
    )

    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    # Add creator as project owner
    project_member = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role="owner",
        assigned_by=current_user.id,
        capacity_percentage=100
    )

    db.add(project_member)
    await db.commit()

    # Generate AI insights for new project
    background_tasks.add_task(ai_service.analyze_new_project, db_project, db)

    # Send notification
    background_tasks.add_task(
        notification_service.notify_project_created,
        db_project,
        current_user,
        db
    )

    return db_project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed project information."""

    # Check access
    if not await check_project_access(project_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    # Get project with related data
    query = select(Project).options(
        selectinload(Project.members).selectinload(ProjectMember.user),
        selectinload(Project.tasks),
        selectinload(Project.cost_items),
        selectinload(Project.whatsapp_messages)
    ).where(Project.id == project_id)

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project information."""

    # Check access with owner requirement
    if not await check_project_access(project_id, current_user, db, require_owner=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project"
        )

    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(project)

    # Trigger AI analysis for project changes
    background_tasks.add_task(ai_service.analyze_project_update, project, db)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project."""

    # Check access with owner requirement
    if not await check_project_access(project_id, current_user, db, require_owner=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )

    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Soft delete by marking as cancelled (don't actually delete due to data integrity)
    project.status = "cancelled"
    project.updated_at = datetime.utcnow()

    await db.commit()

    # Notify team members
    background_tasks.add_task(
        notification_service.notify_project_deleted,
        project,
        current_user,
        db
    )

    return {"message": "Project deleted successfully"}


# Project Member Management Endpoints

@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List project members."""

    # Check access
    if not await check_project_access(project_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    # Get members with user details
    query = select(ProjectMember).options(
        selectinload(ProjectMember.user),
        selectinload(ProjectMember.assigned_by_user)
    ).where(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.is_active == True
        )
    )

    result = await db.execute(query)
    members = result.scalars().all()

    return members


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a member to the project."""

    # Check access with owner/manager requirement
    if not await check_project_access(project_id, current_user, db, require_owner=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage project members"
        )

    # Check if user is already a member
    existing_query = select(ProjectMember).where(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id
        )
    )
    existing_result = await db.execute(existing_query)
    existing_member = existing_result.scalar_one_or_none()

    if existing_member:
        if existing_member.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this project"
            )
        else:
            # Reactivate member
            existing_member.is_active = True
            existing_member.role = member_data.role
            existing_member.capacity_percentage = member_data.capacity_percentage or 100
            existing_member.permissions = member_data.permissions or ["read"]
            existing_member.notification_settings = member_data.notification_settings or {}
            existing_member.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(existing_member)
            return existing_member

    # Create new member
    db_member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role,
        capacity_percentage=member_data.capacity_percentage or 100,
        permissions=member_data.permissions or ["read"],
        notification_settings=member_data.notification_settings or {},
        assigned_by=current_user.id
    )

    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)

    # Send notification
    background_tasks.add_task(
        notification_service.notify_member_added,
        db_member,
        current_user,
        db
    )

    return db_member


@router.put("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_project_member(
    project_id: UUID,
    user_id: UUID,
    member_update: ProjectMemberUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project member information."""

    # Check access with owner/manager requirement
    if not await check_project_access(project_id, current_user, db, require_owner=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage project members"
        )

    # Get member
    query = select(ProjectMember).where(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
    )
    result = await db.execute(query)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )

    # Update fields
    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    member.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(member)

    return member


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from the project."""

    # Check access with owner/manager requirement
    if not await check_project_access(project_id, current_user, db, require_owner=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage project members"
        )

    # Cannot remove yourself if you're the only owner
    if user_id == current_user.id:
        owner_count_query = select(func.count()).select_from(ProjectMember).where(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.role == "owner",
                ProjectMember.is_active == True
            )
        )
        owner_count_result = await db.execute(owner_count_query)
        owner_count = owner_count_result.scalar()

        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last owner from the project"
            )

    # Soft delete member
    update_query = (
        update(ProjectMember)
        .where(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        )
        .values(
            is_active=False,
            deactivated_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )

    result = await db.execute(update_query)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )

    await db.commit()

    # Send notification
    background_tasks.add_task(
        notification_service.notify_member_removed,
        project_id,
        user_id,
        current_user,
        db
    )


# Project Dashboard and Analytics

@router.get("/{project_id}/dashboard", response_model=ProjectDashboard)
async def get_project_dashboard(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project dashboard with statistics and health metrics."""

    # Check access
    if not await check_project_access(project_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    # Get project with related data
    query = select(Project).options(
        selectinload(Project.members).selectinload(ProjectMember.user),
        selectinload(Project.tasks),
        selectinload(Project.cost_items),
        selectinload(Project.whatsapp_messages)
    ).where(Project.id == project_id)

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Calculate dashboard metrics
    total_tasks = len(project.tasks)
    completed_tasks = sum(1 for task in project.tasks if task.status == 'completed')
    overdue_tasks = sum(1 for task in project.tasks
                       if task.due_date and task.due_date < date.today() and task.status != 'completed')

    total_cost = sum(cost_item.actual_amount for cost_item in project.cost_items if cost_item.actual_amount)
    team_members = len([m for m in project.members if m.is_active])

    # Recent activity (simplified)
    recent_activity = []

    # Calculate health metrics
    health_metrics = {
        "schedule_health": project.get_schedule_variance(),
        "budget_health": project.get_budget_variance(),
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "team_utilization": sum(m.capacity_percentage for m in project.members if m.is_active) / team_members if team_members > 0 else 0
    }

    dashboard = ProjectDashboard(
        project=project,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        total_cost=total_cost,
        budget_utilization=(total_cost / project.budget_total * 100) if project.budget_total > 0 else 0,
        team_members=team_members,
        recent_activity=recent_activity,
        health_metrics=health_metrics
    )

    return dashboard


@router.get("/stats/overview", response_model=ProjectStats)
async def get_project_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project statistics overview."""

    # Get project counts by status
    status_query = select(
        Project.status,
        func.count(Project.id).label('count')
    ).where(Project.tenant_id == current_user.tenant_id).group_by(Project.status)

    status_result = await db.execute(status_query)
    status_counts = {row.status: row.count for row in status_result}

    # Get project counts by risk level
    risk_query = select(
        Project.risk_level,
        func.count(Project.id).label('count')
    ).where(Project.tenant_id == current_user.tenant_id).group_by(Project.risk_level)

    risk_result = await db.execute(risk_query)
    risk_counts = {row.risk_level: row.count for row in risk_result}

    # Get financial totals
    financial_query = select(
        func.sum(Project.budget_total).label('total_budget'),
        func.sum(Project.actual_cost).label('total_actual_cost'),
        func.avg(Project.health_score).label('avg_health_score')
    ).where(Project.tenant_id == current_user.tenant_id)

    financial_result = await db.execute(financial_query)
    financial_data = financial_result.first()

    stats = ProjectStats(
        total_projects=sum(status_counts.values()),
        active_projects=status_counts.get('active', 0),
        completed_projects=status_counts.get('completed', 0),
        total_budget=financial_data.total_budget or 0,
        total_actual_cost=financial_data.total_actual_cost or 0,
        average_health_score=financial_data.avg_health_score,
        projects_by_status=status_counts,
        projects_by_risk=risk_counts
    )

    return stats


@router.post("/{project_id}/ai-insights")
async def generate_project_insights(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger AI analysis for project insights."""

    # Check access
    if not await check_project_access(project_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Trigger AI analysis
    background_tasks.add_task(ai_service.generate_project_insights, project, db)

    return {"message": "AI analysis started", "project_id": project_id}

