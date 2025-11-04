"""
Task Service for WhatsApp PM System v3.0 (Gamma)
Business logic for task management, scheduling, and CPM calculations
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text, or_, and_

from models.sqlalchemy.task import Task, TaskComment, TaskDependency, TaskTemplate
from models.sqlalchemy.project import Project
from models.sqlalchemy.user import User
from schemas.task import TaskCreate, TaskUpdate, CPMResult, TaskSchedule
from services.ai_service import AIService
from services.notification_service import NotificationService
from services.scheduling_service import AdvancedSchedulingService

logger = structlog.get_logger(__name__)


class TaskService:
    """Service class for task management operations."""

    def __init__(self):
        self.ai_service = AIService()
        self.notification_service = NotificationService()
        self.scheduling_service = AdvancedSchedulingService()

    async def create_task(
        self,
        task_data: TaskCreate,
        project_id: UUID,
        created_by: UUID,
        db: AsyncSession
    ) -> Task:
        """Create a new task with validation and AI analysis."""
        # Validate project exists and user has access
        project = await self._validate_project_access(project_id, created_by, db)

        # Generate WBS code
        wbs_code = await self._generate_wbs_code(project_id, task_data.parent_task_id, db)

        # Calculate level
        level = await self._calculate_task_level(task_data.parent_task_id, db)

        # Create task
        db_task = Task(
            project_id=project_id,
            name=task_data.name,
            description=task_data.description,
            task_code=task_data.task_code,
            parent_task_id=task_data.parent_task_id,
            level=level,
            wbs_code=wbs_code,
            planned_start_date=task_data.planned_start_date,
            planned_end_date=task_data.planned_end_date,
            planned_duration_days=task_data.planned_duration_days,
            progress_percentage=task_data.progress_percentage,
            assigned_to=task_data.assigned_to,
            estimated_hours=task_data.estimated_hours,
            budgeted_cost=task_data.budgeted_cost,
            predecessor_tasks=task_data.predecessor_tasks or [],
            successor_tasks=task_data.successor_tasks or [],
            lag_days=task_data.lag_days,
            tags=task_data.tags or [],
            custom_fields=task_data.custom_fields or {},
            created_by=created_by
        )

        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

        # Create dependencies
        if task_data.predecessor_tasks:
            await self._create_task_dependencies(
                db_task.id, task_data.predecessor_tasks, task_data.lag_days, db
            )

        # AI analysis
        await self.ai_service.analyze_new_task(db_task)

        logger.info("Task created", task_id=str(db_task.id), project_id=str(project_id))
        return db_task

    async def update_task(
        self,
        task_id: UUID,
        task_update: TaskUpdate,
        updated_by: UUID,
        db: AsyncSession
    ) -> Task:
        """Update task with validation and AI analysis."""
        # Get and validate task
        task = await self._get_task_with_access_check(task_id, updated_by, db)

        # Apply updates
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field not in ['predecessor_tasks', 'successor_tasks']:
                setattr(task, field, value)

        task.updated_at = datetime.utcnow()

        # Handle dependency updates
        if 'predecessor_tasks' in update_data:
            await self._update_task_dependencies(
                task_id, update_data['predecessor_tasks'], task.lag_days, db
            )

        await db.commit()
        await db.refresh(task)

        # AI analysis
        await self.ai_service.analyze_task_update(task)

        logger.info("Task updated", task_id=str(task_id))
        return task

    async def calculate_critical_path(self, project_id: UUID, db: AsyncSession) -> CPMResult:
        """Calculate Critical Path Method for project tasks using OR-Tools."""
        # Get all project tasks
        tasks_query = select(Task).where(Task.project_id == project_id).order_by(Task.created_at)
        tasks_result = await db.execute(tasks_query)
        tasks = tasks_result.scalars().all()

        if not tasks:
            raise ValueError("No tasks found for CPM calculation")

        # Get dependencies
        dep_query = select(TaskDependency).where(
            or_(
                TaskDependency.predecessor.has(project_id=project_id),
                TaskDependency.successor.has(project_id=project_id)
            )
        )
        dep_result = await db.execute(dep_query)
        dependencies = dep_result.scalars().all()

        # Use OR-Tools for advanced CPM calculation
        cpm_result = await self.scheduling_service.calculate_critical_path_ortools(
            tasks, dependencies, db
        )

        # Update tasks with CPM results
        await self._update_tasks_with_cpm_results(cpm_result.task_schedules, db)

        logger.info("CPM calculation completed", project_id=str(project_id), critical_path_count=len(cpm_result.critical_path))
        return cpm_result

    async def get_gantt_data(self, project_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Generate Gantt chart data."""
        # Get tasks with hierarchy
        tasks_query = select(Task).where(Task.project_id == project_id).order_by(
            Task.level, Task.created_at
        )
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

        # Identify milestones
        milestones = await self._identify_milestones(tasks, db)

        return {
            "tasks": tasks,
            "dependencies": dependencies,
            "milestones": milestones,
            "critical_path": await self._get_critical_path_task_ids(project_id, db),
            "today_line": date.today()
        }

    async def auto_assign_tasks(self, project_id: UUID, user_id: UUID, db: AsyncSession) -> List[Dict[str, Any]]:
        """Auto-assign tasks based on workload balancing."""
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

        # Get team members
        members_query = select(Project.members).where(
            and_(
                Project.id == project_id,
                Project.members.is_active == True
            )
        ).options(selectinload(Project.members, User))
        members_result = await db.execute(members_query)
        members = members_result.scalars().all()

        # Calculate current workloads
        workloads = await self._calculate_team_workloads(project_id, members, db)

        # Assign tasks using workload balancing algorithm
        assignments = []
        for task in unassigned_tasks:
            best_member = await self._find_best_assignee(task, members, workloads, db)

            if best_member:
                task.assigned_to = best_member.user_id
                task.updated_at = datetime.utcnow()

                assignments.append({
                    "task_id": str(task.id),
                    "task_name": task.name,
                    "assigned_to": str(best_member.user_id),
                    "assignee_name": f"{best_member.user.first_name} {best_member.user.last_name}"
                })

                # Update workload
                workloads[str(best_member.user_id)] += float(task.estimated_hours or 0)

        await db.commit()

        logger.info("Auto-assigned tasks", count=len(assignments), project_id=str(project_id))
        return assignments

    async def update_task_progress(
        self,
        task_id: UUID,
        progress_data: Dict[str, Any],
        updated_by: UUID,
        db: AsyncSession
    ) -> Task:
        """Update task progress with automatic calculations."""
        task = await self._get_task_with_access_check(task_id, updated_by, db)

        # Update progress fields
        if "progress_percentage" in progress_data:
            task.progress_percentage = progress_data["progress_percentage"]

            # Auto-update status based on progress
            if task.progress_percentage == 100:
                task.status = "completed"
                task.actual_end_date = date.today()
            elif task.progress_percentage > 0 and task.status == "not_started":
                task.status = "in_progress"
                if not task.actual_start_date:
                    task.actual_start_date = date.today()

        if "actual_hours" in progress_data:
            task.actual_hours = progress_data["actual_hours"]

        if "status" in progress_data:
            task.status = progress_data["status"]
            if task.status == "in_progress" and not task.actual_start_date:
                task.actual_start_date = date.today()
            elif task.status == "completed" and not task.actual_end_date:
                task.actual_end_date = date.today()

        task.updated_at = datetime.utcnow()

        # Update parent progress if this is a subtask
        if task.parent_task_id:
            await self._update_parent_progress(task.parent_task_id, db)

        await db.commit()
        await db.refresh(task)

        # AI analysis
        await self.ai_service.analyze_progress_update(task)

        return task

    async def get_task_statistics(self, project_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Calculate comprehensive task statistics."""
        # Basic counts
        stats_query = select(
            func.count(Task.id).label('total_tasks'),
            func.sum(Task.estimated_hours).label('total_estimated'),
            func.sum(Task.actual_hours).label('total_actual'),
            func.avg(Task.progress_percentage).label('avg_progress')
        ).where(Task.project_id == project_id)

        stats_result = await db.execute(stats_query)
        stats = stats_result.first()

        # Status breakdown
        status_counts = await db.execute(
            select(Task.status, func.count(Task.id))
            .where(Task.project_id == project_id)
            .group_by(Task.status)
        )

        # Overdue tasks
        overdue_count = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.status != 'completed',
                    Task.planned_end_date < date.today()
                )
            )
        )

        # Critical path tasks
        critical_count = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.is_critical_path == True
                )
            )
        )

        return {
            "total_tasks": stats[0] or 0,
            "completed_tasks": dict(status_counts).get('completed', 0),
            "in_progress_tasks": dict(status_counts).get('in_progress', 0),
            "overdue_tasks": overdue_count.scalar(),
            "critical_path_tasks": critical_count.scalar(),
            "average_progress": round(stats[3] or 0, 2),
            "total_estimated_hours": stats[1] or 0,
            "total_actual_hours": stats[2] or 0,
            "tasks_by_status": dict(status_counts),
            "tasks_by_assignee": await self._get_assignee_breakdown(project_id, db)
        }

    # Private helper methods

    async def _validate_project_access(self, project_id: UUID, user_id: UUID, db: AsyncSession) -> Project:
        """Validate project access and return project."""
        project_query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.tenant_id == (await self._get_user_tenant(user_id, db))
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise ValueError("Project not found")

        # Check membership
        member_check = await db.execute(
            select(Project.members).where(
                and_(
                    Project.id == project_id,
                    Project.members.any(User.id == user_id)
                )
            )
        )
        if not member_check.scalar_one_or_none():
            raise ValueError("Not authorized to access this project")

        return project

    async def _get_task_with_access_check(self, task_id: UUID, user_id: UUID, db: AsyncSession) -> Task:
        """Get task with access validation."""
        task_query = select(Task).join(Project).where(Task.id == task_id)
        task_result = await db.execute(task_query)
        task = task_result.scalar_one_or_none()

        if not task:
            raise ValueError("Task not found")

        # Validate access
        await self._validate_project_access(task.project_id, user_id, db)

        return task

    async def _get_user_tenant(self, user_id: UUID, db: AsyncSession) -> UUID:
        """Get user's tenant ID."""
        user_query = select(User.tenant_id).where(User.id == user_id)
        user_result = await db.execute(user_query)
        return user_result.scalar_one()

    async def _generate_wbs_code(self, project_id: UUID, parent_task_id: Optional[UUID], db: AsyncSession) -> str:
        """Generate WBS code for task."""
        if parent_task_id:
            parent_query = select(Task.wbs_code).where(Task.id == parent_task_id)
            parent_result = await db.execute(parent_query)
            parent_wbs = parent_result.scalar_one_or_none()

            if parent_wbs:
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

    async def _calculate_task_level(self, parent_task_id: Optional[UUID], db: AsyncSession) -> int:
        """Calculate task level in hierarchy."""
        if not parent_task_id:
            return 1

        parent_query = select(Task.level).where(Task.id == parent_task_id)
        parent_result = await db.execute(parent_query)
        parent_level = parent_result.scalar_one_or_none()

        return (parent_level or 0) + 1

    async def _create_task_dependencies(
        self,
        successor_id: UUID,
        predecessor_ids: List[UUID],
        lag_days: int,
        db: AsyncSession
    ):
        """Create task dependencies."""
        for pred_id in predecessor_ids:
            dependency = TaskDependency(
                predecessor_id=pred_id,
                successor_id=successor_id,
                lag_days=lag_days
            )
            db.add(dependency)
        await db.commit()

    async def _update_task_dependencies(
        self,
        successor_id: UUID,
        predecessor_ids: List[UUID],
        lag_days: int,
        db: AsyncSession
    ):
        """Update task dependencies."""
        # Remove existing
        await db.execute(
            delete(TaskDependency).where(TaskDependency.successor_id == successor_id)
        )

        # Add new
        await self._create_task_dependencies(successor_id, predecessor_ids, lag_days, db)

    async def _build_dependency_graph(self, tasks: List[Task], db: AsyncSession) -> Dict[str, Dict]:
        """Build dependency graph for CPM calculation."""
        task_dict = {str(task.id): task for task in tasks}
        graph = {}

        for task in tasks:
            task_id = str(task.id)
            graph[task_id] = {
                'task': task,
                'predecessors': [],
                'successors': [],
                'earliest_start': None,
                'earliest_finish': None,
                'latest_start': None,
                'latest_finish': None,
                'slack': 0
            }

        # Get dependencies from database
        dep_query = select(TaskDependency)
        dep_result = await db.execute(dep_query)
        dependencies = dep_result.scalars().all()

        for dep in dependencies:
            pred_id = str(dep.predecessor_id)
            succ_id = str(dep.successor_id)

            if pred_id in graph and succ_id in graph:
                graph[succ_id]['predecessors'].append(pred_id)
                graph[pred_id]['successors'].append(succ_id)

        return graph

    async def _forward_pass(self, graph: Dict[str, Dict]) -> List[TaskSchedule]:
        """Perform forward pass of CPM calculation."""
        schedules = []

        for task_id, node in graph.items():
            task = node['task']

            if not node['predecessors']:
                # No predecessors
                earliest_start = task.planned_start_date or date.today()
            else:
                # Earliest start is max of predecessor finish dates
                max_pred_finish = max(
                    graph[pred_id]['earliest_finish'] or date.today()
                    for pred_id in node['predecessors']
                )
                earliest_start = max_pred_finish + timedelta(days=task.lag_days)

            earliest_finish = earliest_start + timedelta(days=task.planned_duration_days or 0)

            # Update node
            node['earliest_start'] = earliest_start
            node['earliest_finish'] = earliest_finish

            schedules.append(TaskSchedule(
                task_id=UUID(task_id),
                earliest_start=earliest_start,
                earliest_finish=earliest_finish,
                latest_start=earliest_start,  # Will be updated in backward pass
                latest_finish=earliest_finish,  # Will be updated in backward pass
                slack=0,  # Will be calculated
                is_critical=False,  # Will be determined
                duration=task.planned_duration_days or 0
            ))

        return schedules

    async def _backward_pass(self, graph: Dict[str, Dict], schedules: List[TaskSchedule]):
        """Perform backward pass of CPM calculation."""
        # Find project end date (latest task finish)
        project_end = max(schedule.earliest_finish for schedule in schedules)

        # Start backward pass from tasks with no successors
        for task_id, node in graph.items():
            if not node['successors']:
                # No successors - latest finish is project end
                node['latest_finish'] = project_end
                node['latest_start'] = project_end - timedelta(days=node['task'].planned_duration_days or 0)
            else:
                # Latest finish is min of successor start dates
                min_succ_start = min(
                    graph[succ_id]['latest_start'] or project_end
                    for succ_id in node['successors']
                )
                node['latest_finish'] = min_succ_start - timedelta(days=node['task'].lag_days)
                node['latest_start'] = node['latest_finish'] - timedelta(days=node['task'].planned_duration_days or 0)

            # Calculate slack
            node['slack'] = (node['latest_start'] - node['earliest_start']).days

    async def _identify_critical_path(self, graph: Dict[str, Dict], schedules: List[TaskSchedule]) -> List[UUID]:
        """Identify tasks on the critical path."""
        critical_path = []

        for schedule in schedules:
            task_id = str(schedule.task_id)
            node = graph[task_id]

            # Task is critical if slack is zero
            if node['slack'] <= 0:
                critical_path.append(schedule.task_id)

        return critical_path

    async def _calculate_project_duration(self, schedules: List[TaskSchedule]) -> int:
        """Calculate total project duration."""
        if not schedules:
            return 0

        project_end = max(schedule.earliest_finish for schedule in schedules)
        project_start = min(schedule.earliest_start for schedule in schedules)

        return (project_end - project_start).days

    async def _identify_bottlenecks(self, graph: Dict[str, Dict], schedules: List[TaskSchedule]) -> List[Dict[str, Any]]:
        """Identify project bottlenecks."""
        bottlenecks = []

        for schedule in schedules:
            task_id = str(schedule.task_id)
            node = graph[task_id]

            # Tasks with high successor count and low slack are bottlenecks
            successor_count = len(node['successors'])
            slack = node['slack']

            if successor_count > 2 and slack <= 1:
                bottlenecks.append({
                    "task_id": schedule.task_id,
                    "task_name": node['task'].name,
                    "successor_count": successor_count,
                    "slack_days": slack,
                    "severity": "high" if slack == 0 else "medium"
                })

        return bottlenecks

    async def _update_tasks_with_cpm_results(self, schedules: List[TaskSchedule], db: AsyncSession):
        """Update tasks with CPM calculation results."""
        for schedule in schedules:
            await db.execute(
                update(Task).where(Task.id == schedule.task_id).values(
                    is_critical_path=schedule.is_critical,
                    slack_days=schedule.slack,
                    updated_at=datetime.utcnow()
                )
            )
        await db.commit()

    async def _identify_milestones(self, tasks: List[Task], db: AsyncSession) -> List[Dict[str, Any]]:
        """Identify project milestones."""
        milestones = []

        for task in tasks:
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

    async def _get_critical_path_task_ids(self, project_id: UUID, db: AsyncSession) -> List[UUID]:
        """Get IDs of tasks on the critical path."""
        query = select(Task.id).where(
            and_(
                Task.project_id == project_id,
                Task.is_critical_path == True
            )
        )
        result = await db.execute(query)
        return [row[0] for row in result.all()]

    async def _calculate_team_workloads(self, project_id: UUID, members: List, db: AsyncSession) -> Dict[str, float]:
        """Calculate current team workloads."""
        workloads = {}

        for member in members:
            user_id = str(member.user_id)

            # Calculate current load
            load_query = select(func.sum(Task.estimated_hours)).where(
                and_(
                    Task.assigned_to == member.user_id,
                    Task.status.in_(["not_started", "in_progress"])
                )
            )
            load_result = await db.execute(load_query)
            current_load = load_result.scalar() or 0

            workloads[user_id] = float(current_load)

        return workloads

    async def _find_best_assignee(self, task: Task, members: List, workloads: Dict[str, float], db: AsyncSession):
        """Find best assignee for task using workload balancing."""
        best_member = None
        min_load = float('inf')

        for member in members:
            user_id = str(member.user_id)
            current_load = workloads.get(user_id, 0)

            # Skip if already overloaded (simple check)
            if current_load > 40:  # 40 hours/week threshold
                continue

            if current_load < min_load:
                min_load = current_load
                best_member = member

        return best_member

    async def _update_parent_progress(self, parent_task_id: UUID, db: AsyncSession):
        """Update parent task progress based on subtasks."""
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

        # Calculate weighted progress
        total_progress = sum(subtask.progress_percentage for subtask in subtasks)
        avg_progress = total_progress / len(subtasks)

        parent_task.progress_percentage = int(avg_progress)

        # Update status
        completed_count = sum(1 for s in subtasks if s.status == "completed")
        if completed_count == len(subtasks):
            parent_task.status = "completed"
            parent_task.actual_end_date = date.today()
        elif any(s.status == "in_progress" for s in subtasks):
            parent_task.status = "in_progress"

        parent_task.updated_at = datetime.utcnow()
        await db.commit()

    async def _get_assignee_breakdown(self, project_id: UUID, db: AsyncSession) -> Dict[str, int]:
        """Get task count breakdown by assignee."""
        query = select(
            Task.assigned_to,
            func.count(Task.id).label('count')
        ).where(
            and_(
                Task.project_id == project_id,
                Task.assigned_to.isnot(None)
            )
        ).group_by(Task.assigned_to)

        result = await db.execute(query)
        return {str(row[0]): row[1] for row in result.all()}

