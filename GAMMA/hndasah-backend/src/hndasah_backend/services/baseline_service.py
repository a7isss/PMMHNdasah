"""
Baseline Management Service for WhatsApp PM System v3.0 (Gamma)
Task and project baseline creation, comparison, and version management
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4
import structlog
from decimal import Decimal

from ..models.sqlalchemy.task import Task
from ..models.sqlalchemy.project import Project
from ..schemas.task import (
    TaskBaseline, TaskBaselineComparison, ProjectBaseline,
    BaselineCreateRequest
)

logger = structlog.get_logger(__name__)


class BaselineService:
    """Service for managing task and project baselines."""

    def __init__(self):
        pass

    async def create_project_baseline(
        self,
        project_id: UUID,
        baseline_request: BaselineCreateRequest,
        created_by: UUID,
        db_session=None
    ) -> ProjectBaseline:
        """
        Create a new baseline for a project.

        Args:
            project_id: Project identifier
            baseline_request: Baseline creation parameters
            created_by: User creating the baseline

        Returns:
            Complete project baseline
        """
        try:
            # Get all project tasks
            tasks_query = db_session.query(Task).filter(Task.project_id == project_id)
            if baseline_request.task_ids:
                tasks_query = tasks_query.filter(Task.id.in_(baseline_request.task_ids))

            tasks = tasks_query.all()

            if not tasks:
                raise ValueError("No tasks found for baseline creation")

            # Generate baseline version
            baseline_version = self._generate_baseline_version(project_id, db_session)

            # Create task baselines
            task_baselines = []
            total_budget = Decimal('0')
            max_end_date = None
            min_start_date = None

            for task in tasks:
                task_baseline = TaskBaseline(
                    task_id=task.id,
                    baseline_version=baseline_version,
                    name=task.name,
                    description=task.description,
                    planned_start_date=task.planned_start_date,
                    planned_end_date=task.planned_end_date,
                    planned_duration_days=task.planned_duration_days,
                    budgeted_cost=task.budgeted_cost,
                    estimated_hours=task.estimated_hours,
                    predecessor_tasks=task.predecessor_tasks or [],
                    successor_tasks=task.successor_tasks or [],
                    created_at=datetime.utcnow(),
                    created_by=created_by
                )
                task_baselines.append(task_baseline)

                # Calculate project totals
                total_budget += task.budgeted_cost

                if task.planned_start_date:
                    if min_start_date is None or task.planned_start_date < min_start_date:
                        min_start_date = task.planned_start_date

                if task.planned_end_date:
                    if max_end_date is None or task.planned_end_date > max_end_date:
                        max_end_date = task.planned_end_date

            # Calculate planned duration
            planned_duration_days = 0
            if min_start_date and max_end_date:
                planned_duration_days = (max_end_date - min_start_date).days

            # Create project baseline
            project_baseline = ProjectBaseline(
                project_id=project_id,
                baseline_version=baseline_version,
                name=baseline_request.name,
                description=baseline_request.description,
                task_baselines=task_baselines,
                total_budget=total_budget,
                planned_duration_days=planned_duration_days,
                created_at=datetime.utcnow(),
                created_by=created_by
            )

            # Store baseline in database (simplified - in real implementation,
            # this would use dedicated baseline tables)
            await self._store_project_baseline(project_baseline, db_session)

            logger.info("Project baseline created", project_id=str(project_id), version=baseline_version)
            return project_baseline

        except Exception as e:
            logger.error("Baseline creation failed", error=str(e), project_id=str(project_id))
            raise

    def _generate_baseline_version(self, project_id: UUID, db_session) -> str:
        """Generate a unique baseline version identifier."""
        # In a real implementation, this would query existing baselines
        # For now, use timestamp-based versioning
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"BL_{timestamp}"

    async def _store_project_baseline(self, baseline: ProjectBaseline, db_session):
        """Store project baseline in database."""
        # In a real implementation, this would insert into dedicated baseline tables
        # For now, we'll store as JSON in a project metadata field or separate table
        # This is a placeholder implementation
        pass

    async def get_project_baselines(
        self,
        project_id: UUID,
        db_session=None
    ) -> List[ProjectBaseline]:
        """
        Get all baselines for a project.

        Args:
            project_id: Project identifier

        Returns:
            List of project baselines
        """
        # In a real implementation, this would query baseline tables
        # For now, return empty list as placeholder
        return []

    async def compare_task_to_baseline(
        self,
        task_id: UUID,
        baseline_version: str,
        db_session=None
    ) -> TaskBaselineComparison:
        """
        Compare current task state to a baseline version.

        Args:
            task_id: Task identifier
            baseline_version: Baseline version to compare against

        Returns:
            Comparison results
        """
        try:
            # Get current task
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            # Get baseline (in real implementation, query baseline tables)
            baseline = await self._get_task_baseline(task_id, baseline_version, db_session)
            if not baseline:
                raise ValueError(f"Baseline {baseline_version} not found for task {task_id}")

            # Compare fields
            changes = {}
            severity_scores = []

            # Compare core fields
            fields_to_compare = [
                ('name', 'Task name'),
                ('description', 'Description'),
                ('planned_start_date', 'Planned start date'),
                ('planned_end_date', 'Planned end date'),
                ('planned_duration_days', 'Planned duration'),
                ('budgeted_cost', 'Budgeted cost'),
                ('estimated_hours', 'Estimated hours')
            ]

            for field_name, display_name in fields_to_compare:
                current_value = getattr(task, field_name)
                baseline_value = getattr(baseline, field_name)

                if current_value != baseline_value:
                    changes[field_name] = {
                        'field_name': display_name,
                        'old_value': baseline_value,
                        'new_value': current_value,
                        'change_type': self._determine_change_type(field_name, baseline_value, current_value)
                    }
                    severity_scores.append(self._calculate_change_severity(field_name, baseline_value, current_value))

            # Compare dependencies
            current_predecessors = set(task.predecessor_tasks or [])
            baseline_predecessors = set(baseline.predecessor_tasks or [])
            if current_predecessors != baseline_predecessors:
                changes['predecessor_tasks'] = {
                    'field_name': 'Predecessor tasks',
                    'old_value': list(baseline_predecessors),
                    'new_value': list(current_predecessors),
                    'change_type': 'dependency_change'
                }
                severity_scores.append(3)  # High severity for dependency changes

            # Determine overall severity
            if severity_scores:
                max_severity = max(severity_scores)
                if max_severity >= 4:
                    overall_severity = "critical"
                elif max_severity >= 3:
                    overall_severity = "high"
                elif max_severity >= 2:
                    overall_severity = "medium"
                else:
                    overall_severity = "low"
            else:
                overall_severity = "none"

            # Generate summary
            change_summary = self._generate_change_summary(changes, overall_severity)

            return TaskBaselineComparison(
                task_id=task_id,
                baseline_version=baseline_version,
                changes=changes,
                change_summary=change_summary,
                severity=overall_severity,
                compared_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error("Baseline comparison failed", error=str(e), task_id=str(task_id))
            raise

    async def _get_task_baseline(self, task_id: UUID, baseline_version: str, db_session) -> Optional[TaskBaseline]:
        """Get task baseline from database."""
        # In a real implementation, this would query baseline tables
        # For now, return None as placeholder
        return None

    def _determine_change_type(self, field_name: str, old_value, new_value) -> str:
        """Determine the type of change."""
        if field_name in ['planned_start_date', 'planned_end_date']:
            return 'schedule_change'
        elif field_name in ['budgeted_cost', 'estimated_hours']:
            return 'cost_change'
        elif field_name in ['name', 'description']:
            return 'content_change'
        elif field_name == 'planned_duration_days':
            return 'duration_change'
        else:
            return 'general_change'

    def _calculate_change_severity(self, field_name: str, old_value, new_value) -> int:
        """Calculate severity score for a change (1-5)."""
        if field_name in ['budgeted_cost', 'estimated_hours']:
            # Cost changes are high severity
            if old_value and new_value:
                percent_change = abs((new_value - old_value) / old_value * 100)
                if percent_change > 50:
                    return 5  # Critical
                elif percent_change > 25:
                    return 4  # High
                elif percent_change > 10:
                    return 3  # Medium
            return 3
        elif field_name in ['planned_start_date', 'planned_end_date', 'planned_duration_days']:
            # Schedule changes are high severity
            return 4
        elif field_name in ['name']:
            # Name changes are medium severity
            return 2
        else:
            # Other changes are low severity
            return 1

    def _generate_change_summary(self, changes: Dict[str, Any], severity: str) -> str:
        """Generate a human-readable summary of changes."""
        if not changes:
            return "No changes detected compared to baseline."

        change_count = len(changes)
        change_types = [change['change_type'] for change in changes.values()]

        summary_parts = []

        if 'schedule_change' in change_types:
            summary_parts.append("schedule changes")
        if 'cost_change' in change_types:
            summary_parts.append("cost/budget changes")
        if 'dependency_change' in change_types:
            summary_parts.append("dependency changes")
        if 'content_change' in change_types:
            summary_parts.append("content changes")

        change_description = ", ".join(summary_parts) if summary_parts else "various changes"

        severity_desc = {
            "critical": "critical",
            "high": "significant",
            "medium": "moderate",
            "low": "minor",
            "none": "no"
        }.get(severity, "unknown")

        return f"Detected {change_count} {severity_desc} changes including {change_description}."

    async def get_baseline_history(
        self,
        task_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        db_session=None
    ) -> List[Dict[str, Any]]:
        """
        Get baseline history for a task or project.

        Args:
            task_id: Specific task ID (optional)
            project_id: Project ID (optional)

        Returns:
            List of baseline history entries
        """
        # In a real implementation, this would query baseline history
        # For now, return empty list as placeholder
        return []

    async def restore_task_from_baseline(
        self,
        task_id: UUID,
        baseline_version: str,
        fields_to_restore: Optional[List[str]] = None,
        user_id: UUID = None,
        db_session=None
    ) -> Dict[str, Any]:
        """
        Restore task fields from a baseline version.

        Args:
            task_id: Task to restore
            baseline_version: Baseline version to restore from
            fields_to_restore: Specific fields to restore (all if None)
            user_id: User performing the restore

        Returns:
            Restore operation results
        """
        try:
            # Get current task
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            # Get baseline
            baseline = await self._get_task_baseline(task_id, baseline_version, db_session)
            if not baseline:
                raise ValueError(f"Baseline {baseline_version} not found for task {task_id}")

            # Determine fields to restore
            if not fields_to_restore:
                fields_to_restore = [
                    'name', 'description', 'planned_start_date', 'planned_end_date',
                    'planned_duration_days', 'budgeted_cost', 'estimated_hours',
                    'predecessor_tasks', 'successor_tasks'
                ]

            # Restore fields
            restored_fields = []
            for field_name in fields_to_restore:
                if hasattr(baseline, field_name):
                    old_value = getattr(task, field_name)
                    new_value = getattr(baseline, field_name)

                    if old_value != new_value:
                        setattr(task, field_name, new_value)
                        restored_fields.append({
                            'field': field_name,
                            'old_value': old_value,
                            'new_value': new_value
                        })

            # Update task
            task.updated_at = datetime.utcnow()
            db_session.commit()

            return {
                'task_id': str(task_id),
                'baseline_version': baseline_version,
                'restored_fields': restored_fields,
                'fields_restored_count': len(restored_fields),
                'restored_at': datetime.utcnow(),
                'restored_by': str(user_id) if user_id else None
            }

        except Exception as e:
            logger.error("Baseline restore failed", error=str(e), task_id=str(task_id))
            raise

    async def delete_baseline(
        self,
        project_id: UUID,
        baseline_version: str,
        user_id: UUID,
        db_session=None
    ) -> bool:
        """
        Delete a project baseline.

        Args:
            project_id: Project identifier
            baseline_version: Baseline version to delete
            user_id: User performing the deletion

        Returns:
            Success status
        """
        try:
            # In a real implementation, this would delete from baseline tables
            # For now, return True as placeholder
            logger.info("Baseline deleted", project_id=str(project_id), version=baseline_version)
            return True

        except Exception as e:
            logger.error("Baseline deletion failed", error=str(e), project_id=str(project_id))
            raise
