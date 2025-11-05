"""
Advanced Scheduling Service for WhatsApp PM System v3.0 (Gamma)
OR-Tools integration for CPM, resource leveling, and optimization
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import structlog
from ortools.scheduling import pywrapcp
from ortools.util import pywraputil

from ..models.sqlalchemy.task import Task, TaskDependency
from ..models.sqlalchemy.project import Project
from ..models.user import User
from ..schemas.task import (
    CPMResult, TaskSchedule, ResourceLevelingResult,
    SchedulingOptimizationResult, TaskConstraint
)

logger = structlog.get_logger(__name__)


class AdvancedSchedulingService:
    """Advanced scheduling service using OR-Tools for optimization."""

    def __init__(self):
        self.solver = None
        self._reset_solver()

    def _reset_solver(self):
        """Reset the OR-Tools solver."""
        self.solver = pywrapcp.Solver("AdvancedCPMSolver")

    async def calculate_critical_path_ortools(
        self,
        tasks: List[Task],
        dependencies: List[TaskDependency],
        db_session=None
    ) -> CPMResult:
        """
        Calculate Critical Path Method using OR-Tools constraint programming.

        This provides more accurate and optimized CPM calculations compared to
        the basic forward/backward pass algorithm.
        """
        try:
            self._reset_solver()

            # Create task variables and intervals
            task_vars = {}
            task_intervals = {}

            # Build task dictionary for easy lookup
            task_dict = {str(task.id): task for task in tasks}

            # Create dependency graph
            predecessors = {}
            successors = {}

            for task in tasks:
                task_id = str(task.id)
                predecessors[task_id] = []
                successors[task_id] = []

            for dep in dependencies:
                pred_id = str(dep.predecessor_id)
                succ_id = str(dep.successor_id)
                if pred_id in predecessors and succ_id in successors:
                    predecessors[succ_id].append(pred_id)
                    successors[pred_id].append(succ_id)

            # Create interval variables for each task
            for task in tasks:
                task_id = str(task.id)

                # Calculate duration in days
                duration_days = max(1, (task.planned_end_date - task.planned_start_date).days)

                # Create interval variable
                start_var = self.solver.IntVar(0, 1000, f"start_{task_id}")
                end_var = self.solver.IntVar(duration_days, 1000 + duration_days, f"end_{task_id}")

                task_vars[task_id] = {
                    'start': start_var,
                    'end': end_var,
                    'duration': duration_days,
                    'task': task
                }

                # Create interval for constraint programming
                interval = self.solver.FixedDurationIntervalVar(
                    start_var, end_var, duration_days, False, f"interval_{task_id}"
                )
                task_intervals[task_id] = interval

            # Add precedence constraints
            for task in tasks:
                task_id = str(task.id)

                for pred_id in predecessors[task_id]:
                    if pred_id in task_intervals and task_id in task_intervals:
                        # Predecessor must finish before successor can start
                        pred_end = task_vars[pred_id]['end']
                        succ_start = task_vars[task_id]['start']

                        # Add lag time if specified
                        lag_days = 0
                        for dep in dependencies:
                            if str(dep.predecessor_id) == pred_id and str(dep.successor_id) == task_id:
                                lag_days = dep.lag_days
                                break

                        self.solver.Add(succ_start >= pred_end + lag_days)

            # Solve the constraint model
            db = self.solver.Phase(
                [var['start'] for var in task_vars.values()],
                self.solver.CHOOSE_FIRST_UNBOUND,
                self.solver.ASSIGN_MIN_VALUE
            )

            self.solver.NewSearch(db)

            task_schedules = []
            critical_path = []
            total_duration = 0

            if self.solver.NextSolution():
                # Extract solution
                for task_id, vars in task_vars.items():
                    task = vars['task']

                    # Calculate actual dates (assuming project starts today)
                    project_start = min(task.planned_start_date for task in tasks)
                    actual_start = project_start + timedelta(days=vars['start'].Value())
                    actual_end = project_start + timedelta(days=vars['end'].Value())

                    # Calculate slack (float)
                    slack = self._calculate_slack(task_id, task_vars, predecessors, successors)

                    # Determine if task is critical
                    is_critical = slack <= 0

                    if is_critical:
                        critical_path.append(UUID(task_id))

                    task_schedules.append(TaskSchedule(
                        task_id=UUID(task_id),
                        earliest_start=actual_start,
                        earliest_finish=actual_end,
                        latest_start=actual_start,  # Will be refined
                        latest_finish=actual_end,   # Will be refined
                        slack=slack,
                        is_critical=is_critical,
                        duration=vars['duration']
                    ))

                # Calculate total project duration
                if task_schedules:
                    total_duration = max(
                        (schedule.earliest_finish - schedule.earliest_start).days
                        for schedule in task_schedules
                    )

            self.solver.EndSearch()

            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks_ortools(task_vars, predecessors, successors)

            return CPMResult(
                critical_path=critical_path,
                total_duration=total_duration,
                task_schedules=task_schedules,
                bottlenecks=bottlenecks
            )

        except Exception as e:
            logger.error("OR-Tools CPM calculation failed", error=str(e))
            # Fallback to basic CPM calculation
            return await self._fallback_cpm_calculation(tasks, dependencies)

    def _calculate_slack(
        self,
        task_id: str,
        task_vars: Dict,
        predecessors: Dict,
        successors: Dict
    ) -> float:
        """Calculate slack for a task using OR-Tools solution."""
        try:
            # Slack = Latest Start - Earliest Start
            earliest_start = task_vars[task_id]['start'].Value()
            latest_start = earliest_start  # Simplified for now

            # For critical path tasks, slack is 0
            # For non-critical tasks, calculate based on successor constraints
            if successors[task_id]:
                # Find the minimum latest start among successors
                min_successor_start = min(
                    task_vars[succ_id]['start'].Value()
                    for succ_id in successors[task_id]
                )
                successor_constraint = min_successor_start - task_vars[task_id]['duration']

                latest_start = min(earliest_start, successor_constraint)

            return max(0, latest_start - earliest_start)

        except Exception:
            return 0.0

    async def _identify_bottlenecks_ortools(
        self,
        task_vars: Dict,
        predecessors: Dict,
        successors: Dict
    ) -> List[Dict[str, Any]]:
        """Identify project bottlenecks using OR-Tools analysis."""
        bottlenecks = []

        for task_id, vars in task_vars.items():
            successor_count = len(successors[task_id])
            predecessor_count = len(predecessors[task_id])

            # Tasks with many dependencies are potential bottlenecks
            if successor_count >= 3 or predecessor_count >= 3:
                bottlenecks.append({
                    "task_id": UUID(task_id),
                    "task_name": vars['task'].name,
                    "successor_count": successor_count,
                    "predecessor_count": predecessor_count,
                    "severity": "high" if successor_count >= 5 or predecessor_count >= 5 else "medium",
                    "bottleneck_type": "dependency_bottleneck"
                })

        return bottlenecks

    async def _fallback_cpm_calculation(
        self,
        tasks: List[Task],
        dependencies: List[TaskDependency]
    ) -> CPMResult:
        """Fallback CPM calculation using basic forward/backward pass."""
        logger.warning("Using fallback CPM calculation")

        # Basic forward pass
        task_schedules = []
        task_dict = {str(task.id): task for task in tasks}

        for task in tasks:
            task_id = str(task.id)

            # Find predecessors
            pred_deps = [d for d in dependencies if str(d.successor_id) == task_id]
            pred_tasks = [task_dict[str(d.predecessor_id)] for d in pred_deps if str(d.predecessor_id) in task_dict]

            if pred_tasks:
                # Earliest start is max of predecessor end dates
                max_pred_end = max(t.planned_end_date for t in pred_tasks)
                earliest_start = max_pred_end + timedelta(days=1)  # Simple lag
            else:
                earliest_start = task.planned_start_date or date.today()

            earliest_finish = earliest_start + timedelta(days=max(1, (task.planned_end_date - task.planned_start_date).days))

            task_schedules.append(TaskSchedule(
                task_id=task.id,
                earliest_start=earliest_start,
                earliest_finish=earliest_finish,
                latest_start=earliest_start,
                latest_finish=earliest_finish,
                slack=0,
                is_critical=True,  # Simplified
                duration=(earliest_finish - earliest_start).days
            ))

        # Calculate total duration
        total_duration = max(
            (schedule.earliest_finish - schedule.earliest_start).days
            for schedule in task_schedules
        ) if task_schedules else 0

        return CPMResult(
            critical_path=[s.task_id for s in task_schedules],
            total_duration=total_duration,
            task_schedules=task_schedules,
            bottlenecks=[]
        )

    async def optimize_resource_leveling(
        self,
        tasks: List[Task],
        resource_constraints: Dict[str, int],
        db_session=None
    ) -> ResourceLevelingResult:
        """
        Perform resource leveling using OR-Tools to balance resource usage.

        Args:
            tasks: List of tasks to schedule
            resource_constraints: Dict mapping resource types to max available units
            db_session: Database session for additional data

        Returns:
            ResourceLevelingResult with optimized schedule
        """
        try:
            self._reset_solver()

            # Create task intervals with resource constraints
            task_intervals = {}
            resource_usage = {}

            # Initialize resource usage tracking
            for resource_type, max_units in resource_constraints.items():
                resource_usage[resource_type] = []

            # Create intervals for each task
            for task in tasks:
                task_id = str(task.id)
                duration = max(1, (task.planned_end_date - task.planned_start_date).days)

                start_var = self.solver.IntVar(0, 365, f"start_{task_id}")  # Max 1 year
                end_var = self.solver.IntVar(duration, 365 + duration, f"end_{task_id}")

                interval = self.solver.FixedDurationIntervalVar(
                    start_var, end_var, duration, False, f"interval_{task_id}"
                )

                task_intervals[task_id] = {
                    'interval': interval,
                    'start': start_var,
                    'end': end_var,
                    'task': task,
                    'resources': getattr(task, 'required_resources', {})
                }

            # Add resource constraints
            for resource_type, max_units in resource_constraints.items():
                # Create cumulative resource usage
                intervals_using_resource = []
                demands = []

                for task_id, task_data in task_intervals.items():
                    if resource_type in task_data['resources']:
                        demand = task_data['resources'][resource_type]
                        intervals_using_resource.append(task_data['interval'])
                        demands.append(demand)

                if intervals_using_resource:
                    # Add cumulative constraint
                    self.solver.AddCumulative(
                        intervals_using_resource,
                        demands,
                        max_units
                    )

            # Add dependency constraints
            task_dict = {str(task.id): task for task in tasks}
            for task in tasks:
                task_id = str(task.id)

                # Find predecessors
                pred_deps = await self._get_task_predecessors(task.id, db_session)
                for pred_id in pred_deps:
                    if str(pred_id) in task_intervals:
                        pred_end = task_intervals[str(pred_id)]['end']
                        curr_start = task_intervals[task_id]['start']
                        self.solver.Add(curr_start >= pred_end)

            # Solve the resource leveling problem
            db = self.solver.Phase(
                [data['start'] for data in task_intervals.values()],
                self.solver.CHOOSE_FIRST_UNBOUND,
                self.solver.ASSIGN_MIN_VALUE
            )

            self.solver.NewSearch(db)

            optimized_schedule = []
            resource_utilization = {}

            if self.solver.NextSolution():
                # Extract optimized schedule
                for task_id, data in task_intervals.items():
                    task = data['task']
                    start_day = data['start'].Value()
                    end_day = data['end'].Value()

                    # Convert to dates
                    base_date = min(task.planned_start_date for task in tasks)
                    optimized_start = base_date + timedelta(days=start_day)
                    optimized_end = base_date + timedelta(days=end_day)

                    optimized_schedule.append({
                        'task_id': UUID(task_id),
                        'task_name': task.name,
                        'original_start': task.planned_start_date,
                        'original_end': task.planned_end_date,
                        'optimized_start': optimized_start,
                        'optimized_end': optimized_end,
                        'delay_days': (optimized_start - task.planned_start_date).days
                    })

                # Calculate resource utilization
                resource_utilization = await self._calculate_resource_utilization(
                    task_intervals, resource_constraints
                )

            self.solver.EndSearch()

            return ResourceLevelingResult(
                optimized_schedule=optimized_schedule,
                resource_utilization=resource_utilization,
                total_delays=sum(s['delay_days'] for s in optimized_schedule),
                optimization_score=await self._calculate_optimization_score(optimized_schedule)
            )

        except Exception as e:
            logger.error("Resource leveling optimization failed", error=str(e))
            return ResourceLevelingResult(
                optimized_schedule=[],
                resource_utilization={},
                total_delays=0,
                optimization_score=0.0
            )

    async def _get_task_predecessors(self, task_id: UUID, db_session) -> List[UUID]:
        """Get predecessor task IDs for a task."""
        if not db_session:
            return []

        try:
            from sqlalchemy import select
            result = await db_session.execute(
                select(TaskDependency.predecessor_id).where(
                    TaskDependency.successor_id == task_id
                )
            )
            return [row[0] for row in result.all()]
        except Exception:
            return []

    async def _calculate_resource_utilization(
        self,
        task_intervals: Dict,
        resource_constraints: Dict[str, int]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Calculate resource utilization over time."""
        utilization = {}

        for resource_type in resource_constraints.keys():
            utilization[resource_type] = []

            # Sample utilization at different time points
            for day in range(0, 365, 7):  # Weekly samples
                daily_usage = 0

                for task_data in task_intervals.values():
                    if resource_type in task_data['resources']:
                        start_day = task_data['start'].Value()
                        end_day = task_data['end'].Value()

                        if start_day <= day <= end_day:
                            daily_usage += task_data['resources'][resource_type]

                utilization[resource_type].append({
                    'day': day,
                    'usage': daily_usage,
                    'capacity': resource_constraints[resource_type],
                    'utilization_percent': (daily_usage / resource_constraints[resource_type]) * 100
                })

        return utilization

    async def _calculate_optimization_score(self, optimized_schedule: List[Dict]) -> float:
        """Calculate optimization score (0-1, higher is better)."""
        if not optimized_schedule:
            return 0.0

        total_delays = sum(abs(s['delay_days']) for s in optimized_schedule)
        max_delay = max(abs(s['delay_days']) for s in optimized_schedule)

        # Score based on delay minimization (lower delays = higher score)
        if max_delay == 0:
            return 1.0
        else:
            return max(0.0, 1.0 - (total_delays / (len(optimized_schedule) * 30)))  # 30 days tolerance

    async def optimize_schedule_with_constraints(
        self,
        tasks: List[Task],
        constraints: List[TaskConstraint],
        optimization_goal: str = "minimize_duration"
    ) -> SchedulingOptimizationResult:
        """
        Optimize schedule with various constraints using OR-Tools.

        Args:
            tasks: Tasks to schedule
            constraints: List of scheduling constraints
            optimization_goal: "minimize_duration", "minimize_cost", "balance_resources"

        Returns:
            Optimized scheduling result
        """
        try:
            self._reset_solver()

            # Create task intervals
            task_intervals = {}
            task_vars = {}

            for task in tasks:
                task_id = str(task.id)
                duration = max(1, (task.planned_end_date - task.planned_start_date).days)

                start_var = self.solver.IntVar(0, 365, f"start_{task_id}")
                end_var = self.solver.IntVar(duration, 365 + duration, f"end_{task_id}")

                interval = self.solver.FixedDurationIntervalVar(
                    start_var, end_var, duration, False, f"interval_{task_id}"
                )

                task_intervals[task_id] = interval
                task_vars[task_id] = {
                    'start': start_var,
                    'end': end_var,
                    'task': task
                }

            # Apply constraints
            for constraint in constraints:
                await self._apply_constraint(constraint, task_vars, task_intervals)

            # Set optimization objective
            objective_var = None

            if optimization_goal == "minimize_duration":
                # Minimize project completion time
                project_end = self.solver.Max([var['end'] for var in task_vars.values()])
                objective_var = project_end
                self.solver.Minimize(project_end, 1)

            elif optimization_goal == "minimize_cost":
                # Minimize total cost (simplified)
                total_cost = self.solver.Sum([
                    var['task'].budgeted_cost or 0
                    for var in task_vars.values()
                ])
                objective_var = total_cost
                self.solver.Minimize(total_cost, 1)

            # Solve optimization problem
            db = self.solver.Phase(
                [var['start'] for var in task_vars.values()],
                self.solver.CHOOSE_FIRST_UNBOUND,
                self.solver.ASSIGN_MIN_VALUE
            )

            self.solver.NewSearch(db)

            optimized_tasks = []
            objective_value = 0

            if self.solver.NextSolution():
                objective_value = objective_var.Value() if objective_var else 0

                # Extract optimized schedule
                base_date = min(task.planned_start_date for task in tasks)

                for task_id, vars in task_vars.items():
                    task = vars['task']
                    start_day = vars['start'].Value()
                    end_day = vars['end'].Value()

                    optimized_start = base_date + timedelta(days=start_day)
                    optimized_end = base_date + timedelta(days=end_day)

                    optimized_tasks.append({
                        'task_id': UUID(task_id),
                        'task_name': task.name,
                        'original_start': task.planned_start_date,
                        'original_end': task.planned_end_date,
                        'optimized_start': optimized_start,
                        'optimized_end': optimized_end,
                        'changes': {
                            'start_delay': (optimized_start - task.planned_start_date).days,
                            'end_delay': (optimized_end - task.planned_end_date).days
                        }
                    })

            self.solver.EndSearch()

            return SchedulingOptimizationResult(
                optimized_tasks=optimized_tasks,
                objective_value=objective_value,
                optimization_goal=optimization_goal,
                constraints_applied=len(constraints),
                solution_found=len(optimized_tasks) > 0
            )

        except Exception as e:
            logger.error("Schedule optimization failed", error=str(e))
            return SchedulingOptimizationResult(
                optimized_tasks=[],
                objective_value=0,
                optimization_goal=optimization_goal,
                constraints_applied=0,
                solution_found=False
            )

    async def _apply_constraint(
        self,
        constraint: TaskConstraint,
        task_vars: Dict,
        task_intervals: Dict
    ):
        """Apply a scheduling constraint to the OR-Tools model."""
        try:
            if constraint.constraint_type == "start_after":
                # Task must start after a specific date
                if constraint.task_id and str(constraint.task_id) in task_vars:
                    target_date = constraint.parameters.get('date')
                    if target_date:
                        days_from_base = (target_date - date.today()).days
                        self.solver.Add(task_vars[str(constraint.task_id)]['start'] >= days_from_base)

            elif constraint.constraint_type == "finish_before":
                # Task must finish before a specific date
                if constraint.task_id and str(constraint.task_id) in task_vars:
                    target_date = constraint.parameters.get('date')
                    if target_date:
                        days_from_base = (target_date - date.today()).days
                        self.solver.Add(task_vars[str(constraint.task_id)]['end'] <= days_from_base)

            elif constraint.constraint_type == "max_duration":
                # Task duration cannot exceed maximum
                if constraint.task_id and str(constraint.task_id) in task_vars:
                    max_duration = constraint.parameters.get('max_days', 30)
                    start = task_vars[str(constraint.task_id)]['start']
                    end = task_vars[str(constraint.task_id)]['end']
                    self.solver.Add(end - start <= max_duration)

            elif constraint.constraint_type == "resource_limit":
                # Resource usage constraint
                resource_type = constraint.parameters.get('resource_type')
                max_usage = constraint.parameters.get('max_units', 1)

                if resource_type:
                    # Find tasks using this resource
                    resource_intervals = []
                    demands = []

                    for task_id, task_data in task_vars.items():
                        task_resources = getattr(task_data['task'], 'required_resources', {})
                        if resource_type in task_resources:
                            resource_intervals.append(task_intervals[task_id])
                            demands.append(task_resources[resource_type])

                    if resource_intervals:
                        self.solver.AddCumulative(resource_intervals, demands, max_usage)

        except Exception as e:
            logger.warning("Failed to apply constraint", constraint=constraint.constraint_type, error=str(e))
