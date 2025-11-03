"""
Conflict Resolution Service for WhatsApp PM System v3.0 (Gamma)
Automated detection and resolution of scheduling conflicts
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import structlog

from models.sqlalchemy.task import Task
from schemas.task import SchedulingConflict, ConflictResolutionResult

logger = structlog.get_logger(__name__)


class ConflictResolutionService:
    """Service for detecting and resolving scheduling conflicts."""

    def __init__(self):
        pass

    async def detect_project_conflicts(
        self,
        project_id: UUID,
        db_session=None
    ) -> List[SchedulingConflict]:
        """
        Detect all scheduling conflicts in a project.

        Args:
            project_id: Project identifier

        Returns:
            List of detected conflicts
        """
        try:
            # Get all project tasks
            tasks_query = db_session.query(Task).filter(Task.project_id == project_id)
            tasks = tasks_query.all()

            if not tasks:
                return []

            conflicts = []

            # Check for various types of conflicts
            conflicts.extend(self._detect_date_conflicts(tasks))
            conflicts.extend(self._detect_resource_conflicts(tasks))
            conflicts.extend(self._detect_dependency_conflicts(tasks))
            conflicts.extend(self._detect_capacity_conflicts(tasks))

            return conflicts

        except Exception as e:
            logger.error("Conflict detection failed", error=str(e), project_id=str(project_id))
            return []

    async def resolve_conflicts(
        self,
        conflicts: List[SchedulingConflict],
        resolution_strategy: str = "auto",
        db_session=None
    ) -> ConflictResolutionResult:
        """
        Resolve detected scheduling conflicts.

        Args:
            conflicts: List of conflicts to resolve
            resolution_strategy: Strategy for resolution ("auto", "manual", "conservative")
            db_session: Database session

        Returns:
            Resolution results
        """
        try:
            resolved_count = 0
            unresolved_conflicts = []
            applied_resolutions = []

            for conflict in conflicts:
                resolution = await self._resolve_single_conflict(conflict, resolution_strategy, db_session)
                if resolution:
                    resolved_count += 1
                    applied_resolutions.append(resolution)
                else:
                    unresolved_conflicts.append(conflict)

            summary = self._generate_resolution_summary(applied_resolutions, unresolved_conflicts)

            return ConflictResolutionResult(
                conflicts_detected=len(conflicts),
                conflicts_resolved=resolved_count,
                unresolved_conflicts=unresolved_conflicts,
                applied_resolutions=applied_resolutions,
                resolution_summary=summary
            )

        except Exception as e:
            logger.error("Conflict resolution failed", error=str(e))
            return ConflictResolutionResult(
                conflicts_detected=len(conflicts),
                conflicts_resolved=0,
                unresolved_conflicts=conflicts,
                applied_resolutions=[],
                resolution_summary=f"Resolution failed: {str(e)}"
            )

    def _detect_date_conflicts(self, tasks: List[Task]) -> List[SchedulingConflict]:
        """Detect date-related conflicts."""
        conflicts = []

        # Check for overlapping tasks assigned to same resource
        resource_tasks = {}
        for task in tasks:
            if task.assigned_to and task.planned_start_date and task.planned_end_date:
                resource_id = str(task.assigned_to)
                if resource_id not in resource_tasks:
                    resource_tasks[resource_id] = []
                resource_tasks[resource_id].append(task)

        # Check for overlaps within each resource
        for resource_id, task_list in resource_tasks.items():
            task_list.sort(key=lambda t: t.planned_start_date)

            for i in range(len(task_list) - 1):
                current = task_list[i]
                next_task = task_list[i + 1]

                if (current.planned_end_date and next_task.planned_start_date and
                    current.planned_end_date > next_task.planned_start_date):

                    overlap_days = (current.planned_end_date - next_task.planned_start_date).days

                    conflicts.append(SchedulingConflict(
                        conflict_type="resource_overlap",
                        task_ids=[str(current.id), str(next_task.id)],
                        description=f"Resource {resource_id} is double-booked: '{current.name}' overlaps with '{next_task.name}' by {overlap_days} days",
                        severity="medium" if overlap_days <= 3 else "high",
                        suggested_resolution=f"Delay '{next_task.name}' by {overlap_days} days or reassign resource"
                    ))

        # Check for tasks ending after project deadline
        for task in tasks:
            if task.planned_end_date and task.project.end_date and task.planned_end_date > task.project.end_date:
                overdue_days = (task.planned_end_date - task.project.end_date).days

                conflicts.append(SchedulingConflict(
                    conflict_type="project_deadline_violation",
                    task_ids=[str(task.id)],
                    description=f"Task '{task.name}' ends {overdue_days} days after project deadline",
                    severity="high",
                    suggested_resolution=f"Accelerate task completion or extend project deadline"
                ))

        return conflicts

    def _detect_resource_conflicts(self, tasks: List[Task]) -> List[SchedulingConflict]:
        """Detect resource-related conflicts."""
        conflicts = []

        # Check for overallocated resources (simplified - assumes 8 hour workdays)
        resource_workload = {}
        for task in tasks:
            if task.assigned_to and task.estimated_hours:
                resource_id = str(task.assigned_to)
                if resource_id not in resource_workload:
                    resource_workload[resource_id] = 0
                resource_workload[resource_id] += float(task.estimated_hours)

        # Assume 160 hours per month (40 hours/week * 4 weeks) as capacity
        monthly_capacity = 160

        for resource_id, hours in resource_workload.items():
            if hours > monthly_capacity:
                overload_percentage = ((hours - monthly_capacity) / monthly_capacity) * 100

                conflicts.append(SchedulingConflict(
                    conflict_type="resource_overallocation",
                    task_ids=[],  # All tasks assigned to this resource
                    description=f"Resource {resource_id} is overloaded by {overload_percentage:.1f}% ({hours:.1f} hours vs {monthly_capacity} capacity)",
                    severity="high" if overload_percentage > 50 else "medium",
                    suggested_resolution="Reassign tasks or extend resource capacity"
                ))

        return conflicts

    def _detect_dependency_conflicts(self, tasks: List[Task]) -> List[SchedulingConflict]:
        """Detect dependency-related conflicts."""
        conflicts = []

        # Check for dependency date violations
        task_dict = {task.id: task for task in tasks}

        for task in tasks:
            if task.predecessor_tasks:
                for pred_id in task.predecessor_tasks:
                    if pred_id in task_dict:
                        predecessor = task_dict[pred_id]

                        # Check if predecessor ends after successor starts
                        if (predecessor.planned_end_date and task.planned_start_date and
                            predecessor.planned_end_date > task.planned_start_date):

                            violation_days = (predecessor.planned_end_date - task.planned_start_date).days

                            conflicts.append(SchedulingConflict(
                                conflict_type="dependency_violation",
                                task_ids=[str(predecessor.id), str(task.id)],
                                description=f"Dependency violation: '{predecessor.name}' must complete before '{task.name}' starts (violated by {violation_days} days)",
                                severity="high",
                                suggested_resolution=f"Delay '{task.name}' by {violation_days} days or accelerate '{predecessor.name}'"
                            ))

        return conflicts

    def _detect_capacity_conflicts(self, tasks: List[Task]) -> List[SchedulingConflict]:
        """Detect capacity-related conflicts."""
        conflicts = []

        # Check for tasks with unrealistic duration vs effort
        for task in tasks:
            if task.planned_duration_days and task.estimated_hours:
                # Assume 8 hours per day capacity
                max_possible_hours = task.planned_duration_days * 8

                if float(task.estimated_hours) > max_possible_hours:
                    required_hours_per_day = float(task.estimated_hours) / task.planned_duration_days

                    conflicts.append(SchedulingConflict(
                        conflict_type="capacity_violation",
                        task_ids=[str(task.id)],
                        description=f"Task '{task.name}' requires {required_hours_per_day:.1f} hours/day but only 8 hours available",
                        severity="medium",
                        suggested_resolution=f"Extend duration to {int(float(task.estimated_hours) / 8) + 1} days or reduce scope"
                    ))

        return conflicts

    async def _resolve_single_conflict(
        self,
        conflict: SchedulingConflict,
        strategy: str,
        db_session=None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve a single conflict.

        Args:
            conflict: Conflict to resolve
            strategy: Resolution strategy
            db_session: Database session

        Returns:
            Resolution details or None if unresolved
        """
        try:
            if conflict.conflict_type == "resource_overlap" and strategy == "auto":
                return await self._resolve_resource_overlap(conflict, db_session)
            elif conflict.conflict_type == "dependency_violation" and strategy == "auto":
                return await self._resolve_dependency_violation(conflict, db_session)
            elif conflict.conflict_type == "capacity_violation" and strategy == "auto":
                return await self._resolve_capacity_violation(conflict, db_session)

            # For other conflict types or manual strategy, return None (unresolved)
            return None

        except Exception as e:
            logger.error("Single conflict resolution failed", error=str(e), conflict_type=conflict.conflict_type)
            return None

    async def _resolve_resource_overlap(
        self,
        conflict: SchedulingConflict,
        db_session=None
    ) -> Optional[Dict[str, Any]]:
        """Resolve resource overlap by delaying the second task."""
        if len(conflict.task_ids) != 2:
            return None

        # Get the two tasks
        task1 = db_session.query(Task).filter(Task.id == conflict.task_ids[0]).first()
        task2 = db_session.query(Task).filter(Task.id == conflict.task_ids[1]).first()

        if not task1 or not task2:
            return None

        # Assume task1 is the earlier one, delay task2
        if task1.planned_end_date and task2.planned_start_date:
            delay_days = (task1.planned_end_date - task2.planned_start_date).days + 1

            if delay_days > 0:
                # Delay task2
                task2.planned_start_date = task2.planned_start_date + timedelta(days=delay_days)
                if task2.planned_end_date:
                    task2.planned_end_date = task2.planned_end_date + timedelta(days=delay_days)

                task2.updated_at = datetime.utcnow()
                db_session.commit()

                return {
                    "conflict_type": "resource_overlap",
                    "resolution_type": "delay_task",
                    "affected_tasks": [str(task2.id)],
                    "changes": {
                        "planned_start_date": task2.planned_start_date.isoformat(),
                        "planned_end_date": task2.planned_end_date.isoformat() if task2.planned_end_date else None,
                        "delay_days": delay_days
                    },
                    "description": f"Delayed '{task2.name}' by {delay_days} days to resolve resource overlap"
                }

        return None

    async def _resolve_dependency_violation(
        self,
        conflict: SchedulingConflict,
        db_session=None
    ) -> Optional[Dict[str, Any]]:
        """Resolve dependency violation by delaying the successor task."""
        if len(conflict.task_ids) != 2:
            return None

        # Get the predecessor and successor tasks
        pred_task = db_session.query(Task).filter(Task.id == conflict.task_ids[0]).first()
        succ_task = db_session.query(Task).filter(Task.id == conflict.task_ids[1]).first()

        if not pred_task or not succ_task:
            return None

        # Calculate required delay
        if pred_task.planned_end_date and succ_task.planned_start_date:
            required_delay = (pred_task.planned_end_date - succ_task.planned_start_date).days + 1

            if required_delay > 0:
                # Delay successor
                succ_task.planned_start_date = succ_task.planned_start_date + timedelta(days=required_delay)
                if succ_task.planned_end_date:
                    succ_task.planned_end_date = succ_task.planned_end_date + timedelta(days=required_delay)

                succ_task.updated_at = datetime.utcnow()
                db_session.commit()

                return {
                    "conflict_type": "dependency_violation",
                    "resolution_type": "delay_successor",
                    "affected_tasks": [str(succ_task.id)],
                    "changes": {
                        "planned_start_date": succ_task.planned_start_date.isoformat(),
                        "planned_end_date": succ_task.planned_end_date.isoformat() if succ_task.planned_end_date else None,
                        "delay_days": required_delay
                    },
                    "description": f"Delayed '{succ_task.name}' by {required_delay} days to satisfy dependency"
                }

        return None

    async def _resolve_capacity_violation(
        self,
        conflict: SchedulingConflict,
        db_session=None
    ) -> Optional[Dict[str, Any]]:
        """Resolve capacity violation by extending duration."""
        if len(conflict.task_ids) != 1:
            return None

        task = db_session.query(Task).filter(Task.id == conflict.task_ids[0]).first()
        if not task or not task.estimated_hours or not task.planned_duration_days:
            return None

        # Calculate required duration for 8 hours/day
        required_duration = int(float(task.estimated_hours) / 8) + 1

        if required_duration > task.planned_duration_days:
            old_duration = task.planned_duration_days
            task.planned_duration_days = required_duration

            # Adjust end date if start date exists
            if task.planned_start_date:
                task.planned_end_date = task.planned_start_date + timedelta(days=required_duration)

            task.updated_at = datetime.utcnow()
            db_session.commit()

            return {
                "conflict_type": "capacity_violation",
                "resolution_type": "extend_duration",
                "affected_tasks": [str(task.id)],
                "changes": {
                    "planned_duration_days": required_duration,
                    "planned_end_date": task.planned_end_date.isoformat() if task.planned_end_date else None,
                    "old_duration": old_duration
                },
                "description": f"Extended '{task.name}' duration from {old_duration} to {required_duration} days"
            }

        return None

    def _generate_resolution_summary(
        self,
        applied_resolutions: List[Dict[str, Any]],
        unresolved_conflicts: List[SchedulingConflict]
    ) -> str:
        """Generate a summary of conflict resolution actions."""
        summary_parts = []

        if applied_resolutions:
            summary_parts.append(f"Successfully resolved {len(applied_resolutions)} conflicts:")

            resolution_types = {}
            for resolution in applied_resolutions:
                res_type = resolution.get("resolution_type", "unknown")
                resolution_types[res_type] = resolution_types.get(res_type, 0) + 1

            for res_type, count in resolution_types.items():
                summary_parts.append(f"  - {res_type.replace('_', ' ').title()}: {count}")

        if unresolved_conflicts:
            summary_parts.append(f"Unable to resolve {len(unresolved_conflicts)} conflicts automatically.")
            severity_counts = {}
            for conflict in unresolved_conflicts:
                severity_counts[conflict.severity] = severity_counts.get(conflict.severity, 0) + 1

            for severity, count in severity_counts.items():
                summary_parts.append(f"  - {severity.title()} severity: {count}")

        return "\n".join(summary_parts) if summary_parts else "No conflicts to resolve."

    async def get_conflict_statistics(
        self,
        project_id: UUID,
        db_session=None
    ) -> Dict[str, Any]:
        """
        Get conflict statistics for a project.

        Args:
            project_id: Project identifier

        Returns:
            Conflict statistics
        """
        conflicts = await self.detect_project_conflicts(project_id, db_session)

        stats = {
            "total_conflicts": len(conflicts),
            "conflicts_by_type": {},
            "conflicts_by_severity": {},
            "most_affected_tasks": []
        }

        # Count by type and severity
        for conflict in conflicts:
            stats["conflicts_by_type"][conflict.conflict_type] = stats["conflicts_by_type"].get(conflict.conflict_type, 0) + 1
            stats["conflicts_by_severity"][conflict.severity] = stats["conflicts_by_severity"].get(conflict.severity, 0) + 1

        # Find most affected tasks
        task_conflict_count = {}
        for conflict in conflicts:
            for task_id in conflict.task_ids:
                task_conflict_count[task_id] = task_conflict_count.get(task_id, 0) + 1

        most_affected = sorted(task_conflict_count.items(), key=lambda x: x[1], reverse=True)[:5]
        stats["most_affected_tasks"] = [{"task_id": tid, "conflict_count": count} for tid, count in most_affected]

        return stats
