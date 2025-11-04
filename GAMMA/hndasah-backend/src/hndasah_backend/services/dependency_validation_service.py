"""
Dependency Validation Service for WhatsApp PM System v3.0 (Gamma)
Automated validation of task dependencies and circular reference detection
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID
import structlog
from collections import defaultdict, deque

from models.sqlalchemy.task import Task, TaskDependency
from schemas.task import DependencyValidationResult, DependencyGraph

logger = structlog.get_logger(__name__)


class DependencyValidationService:
    """Service for validating task dependencies and detecting issues."""

    def __init__(self):
        pass

    async def validate_project_dependencies(
        self,
        project_id: UUID,
        db_session=None
    ) -> DependencyValidationResult:
        """
        Validate all dependencies in a project.

        Args:
            project_id: Project identifier

        Returns:
            Validation results
        """
        try:
            # Get all tasks and dependencies for the project
            tasks_query = db_session.query(Task).filter(Task.project_id == project_id)
            tasks = tasks_query.all()

            dependencies_query = db_session.query(TaskDependency).filter(
                TaskDependency.predecessor.has(project_id=project_id) |
                TaskDependency.successor.has(project_id=project_id)
            )
            dependencies = dependencies_query.all()

            # Build dependency graph
            graph = self._build_dependency_graph(tasks, dependencies)

            # Validate dependencies
            is_valid = True
            errors = []
            warnings = []
            circular_references = []
            orphaned_tasks = []
            invalid_dependencies = []

            # Check for circular references
            cycles = self._detect_cycles(graph)
            if cycles:
                is_valid = False
                circular_references = cycles
                for cycle in cycles:
                    errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

            # Check for orphaned dependencies
            task_ids = {str(task.id) for task in tasks}
            for dep in dependencies:
                pred_id = str(dep.predecessor_id)
                succ_id = str(dep.successor_id)

                if pred_id not in task_ids:
                    invalid_dependencies.append({
                        "dependency_id": str(dep.id),
                        "predecessor_id": pred_id,
                        "successor_id": succ_id,
                        "issue": "predecessor_task_not_found"
                    })
                    errors.append(f"Dependency references non-existent predecessor task: {pred_id}")
                    is_valid = False

                if succ_id not in task_ids:
                    invalid_dependencies.append({
                        "dependency_id": str(dep.id),
                        "predecessor_id": pred_id,
                        "successor_id": succ_id,
                        "issue": "successor_task_not_found"
                    })
                    errors.append(f"Dependency references non-existent successor task: {succ_id}")
                    is_valid = False

            # Check for self-dependencies
            for dep in dependencies:
                if dep.predecessor_id == dep.successor_id:
                    invalid_dependencies.append({
                        "dependency_id": str(dep.id),
                        "predecessor_id": str(dep.predecessor_id),
                        "successor_id": str(dep.successor_id),
                        "issue": "self_dependency"
                    })
                    errors.append(f"Task cannot depend on itself: {dep.predecessor_id}")
                    is_valid = False

            # Check for duplicate dependencies
            dep_pairs = {}
            for dep in dependencies:
                pair = (str(dep.predecessor_id), str(dep.successor_id))
                if pair in dep_pairs:
                    warnings.append(f"Duplicate dependency found: {dep.predecessor_id} -> {dep.successor_id}")
                else:
                    dep_pairs[pair] = dep

            # Check for logical issues
            logical_issues = self._check_logical_issues(tasks, dependencies)
            warnings.extend(logical_issues)

            return DependencyValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                circular_references=circular_references,
                orphaned_tasks=orphaned_tasks,
                invalid_dependencies=invalid_dependencies
            )

        except Exception as e:
            logger.error("Dependency validation failed", error=str(e), project_id=str(project_id))
            return DependencyValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                circular_references=[],
                orphaned_tasks=[],
                invalid_dependencies=[]
            )

    async def validate_task_dependencies(
        self,
        task_id: UUID,
        db_session=None
    ) -> DependencyValidationResult:
        """
        Validate dependencies for a specific task.

        Args:
            task_id: Task identifier

        Returns:
            Validation results for the task
        """
        try:
            # Get task and its dependencies
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return DependencyValidationResult(
                    is_valid=False,
                    errors=["Task not found"],
                    warnings=[],
                    circular_references=[],
                    orphaned_tasks=[str(task_id)],
                    invalid_dependencies=[]
                )

            # Get dependencies where this task is involved
            dependencies = db_session.query(TaskDependency).filter(
                (TaskDependency.predecessor_id == task_id) |
                (TaskDependency.successor_id == task_id)
            ).all()

            # Build mini graph for this task
            graph = self._build_single_task_graph(task, dependencies)

            # Check for cycles involving this task
            cycles = self._detect_cycles_in_task_graph(graph, str(task_id))

            errors = []
            warnings = []
            is_valid = True

            if cycles:
                is_valid = False
                errors.append(f"Task is part of circular dependency: {' -> '.join(cycles[0])}")

            # Validate dependency dates
            date_issues = self._validate_dependency_dates(task, dependencies)
            if date_issues:
                warnings.extend(date_issues)

            return DependencyValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                circular_references=cycles,
                orphaned_tasks=[],
                invalid_dependencies=[]
            )

        except Exception as e:
            logger.error("Task dependency validation failed", error=str(e), task_id=str(task_id))
            return DependencyValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                circular_references=[],
                orphaned_tasks=[],
                invalid_dependencies=[]
            )

    def _build_dependency_graph(
        self,
        tasks: List[Task],
        dependencies: List[TaskDependency]
    ) -> DependencyGraph:
        """Build dependency graph from tasks and dependencies."""
        nodes = [str(task.id) for task in tasks]
        edges = []

        # Create adjacency list
        adj_list = defaultdict(list)

        for dep in dependencies:
            pred_id = str(dep.predecessor_id)
            succ_id = str(dep.successor_id)
            edges.append((pred_id, succ_id))
            adj_list[pred_id].append(succ_id)

        # Find cycles
        cycles = self._detect_cycles_from_adj_list(adj_list)

        # Find longest path (critical path approximation)
        longest_path = self._find_longest_path(adj_list, nodes)

        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            cycles=cycles,
            longest_path=longest_path
        )

    def _build_single_task_graph(self, task: Task, dependencies: List[TaskDependency]) -> Dict[str, Any]:
        """Build dependency graph for a single task."""
        adj_list = defaultdict(list)

        for dep in dependencies:
            pred_id = str(dep.predecessor_id)
            succ_id = str(dep.successor_id)
            adj_list[pred_id].append(succ_id)

        return {
            'nodes': [str(task.id)],
            'adj_list': adj_list
        }

    def _detect_cycles(self, graph: DependencyGraph) -> List[List[str]]:
        """Detect cycles in dependency graph."""
        return self._detect_cycles_from_adj_list(
            defaultdict(list, {node: [] for node in graph.nodes})
        )

    def _detect_cycles_from_adj_list(self, adj_list: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in adj_list:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _detect_cycles_in_task_graph(self, graph: Dict[str, Any], task_id: str) -> List[List[str]]:
        """Detect cycles involving a specific task."""
        # Simplified cycle detection for single task
        cycles = []

        # Check if task has any predecessors that eventually lead back to itself
        visited = set()

        def check_path(current: str, target: str, path: List[str]):
            if current in path:
                return True  # Cycle detected
            if current == target and len(path) > 0:
                cycles.append(path + [current])
                return True

            path.append(current)
            for pred in graph['adj_list'].get(current, []):
                if pred not in visited:
                    visited.add(pred)
                    if check_path(pred, target, path):
                        return True

            path.pop()
            return False

        # Check predecessors
        for pred in graph['adj_list'].get(task_id, []):
            if check_path(pred, task_id, []):
                break

        return cycles

    def _find_longest_path(self, adj_list: Dict[str, List[str]], nodes: List[str]) -> List[str]:
        """Find the longest path in the dependency graph (approximates critical path)."""
        # Simplified longest path calculation
        # In a real implementation, this would use topological sort and DP

        def calculate_path_length(node: str, memo: Dict[str, int]) -> int:
            if node in memo:
                return memo[node]

            if not adj_list[node]:
                return 1

            max_length = 1
            for successor in adj_list[node]:
                length = calculate_path_length(successor, memo) + 1
                max_length = max(max_length, length)

            memo[node] = max_length
            return max_length

        # Calculate longest path from each node
        memo = {}
        max_length = 0
        start_node = None

        for node in nodes:
            length = calculate_path_length(node, memo)
            if length > max_length:
                max_length = length
                start_node = node

        # Reconstruct path (simplified)
        if start_node:
            path = [start_node]
            current = start_node
            while adj_list[current]:
                next_node = max(adj_list[current], key=lambda x: calculate_path_length(x, memo))
                path.append(next_node)
                current = next_node
            return path

        return []

    def _check_logical_issues(self, tasks: List[Task], dependencies: List[TaskDependency]) -> List[str]:
        """Check for logical issues in dependencies."""
        warnings = []

        # Check for tasks with too many dependencies
        task_dep_count = defaultdict(int)
        for dep in dependencies:
            task_dep_count[str(dep.successor_id)] += 1

        for task_id, count in task_dep_count.items():
            if count > 10:
                task = next((t for t in tasks if str(t.id) == task_id), None)
                if task:
                    warnings.append(f"Task '{task.name}' has {count} predecessors - consider simplifying")

        # Check for date inconsistencies
        for dep in dependencies:
            pred_task = next((t for t in tasks if t.id == dep.predecessor_id), None)
            succ_task = next((t for t in tasks if t.id == dep.successor_id), None)

            if pred_task and succ_task:
                if (pred_task.planned_end_date and succ_task.planned_start_date and
                    pred_task.planned_end_date > succ_task.planned_start_date):
                    warnings.append(
                        f"Date inconsistency: '{pred_task.name}' ends after '{succ_task.name}' starts"
                    )

        return warnings

    def _validate_dependency_dates(self, task: Task, dependencies: List[TaskDependency]) -> List[str]:
        """Validate dependency dates for a task."""
        warnings = []

        for dep in dependencies:
            if dep.successor_id == task.id:
                # This task depends on predecessor
                pred_task = dep.predecessor
                if (pred_task.planned_end_date and task.planned_start_date and
                    pred_task.planned_end_date > task.planned_start_date):
                    warnings.append(
                        f"Dependency date issue: predecessor '{pred_task.name}' ends after this task starts"
                    )

        return warnings

    async def suggest_dependency_fixes(
        self,
        validation_result: DependencyValidationResult,
        db_session=None
    ) -> List[Dict[str, Any]]:
        """
        Suggest fixes for dependency validation issues.

        Args:
            validation_result: Results from dependency validation
            db_session: Database session

        Returns:
            List of suggested fixes
        """
        suggestions = []

        # Suggest fixes for circular references
        for cycle in validation_result.circular_references:
            suggestions.append({
                "issue_type": "circular_reference",
                "description": f"Break circular dependency: {' -> '.join(cycle)}",
                "suggested_action": "Remove one dependency in the cycle",
                "affected_tasks": cycle
            })

        # Suggest fixes for invalid dependencies
        for invalid_dep in validation_result.invalid_dependencies:
            if invalid_dep["issue"] == "predecessor_task_not_found":
                suggestions.append({
                    "issue_type": "missing_predecessor",
                    "description": f"Predecessor task {invalid_dep['predecessor_id']} not found",
                    "suggested_action": "Remove dependency or create missing task",
                    "affected_tasks": [invalid_dep['successor_id']]
                })
            elif invalid_dep["issue"] == "successor_task_not_found":
                suggestions.append({
                    "issue_type": "missing_successor",
                    "description": f"Successor task {invalid_dep['successor_id']} not found",
                    "suggested_action": "Remove dependency or create missing task",
                    "affected_tasks": [invalid_dep['predecessor_id']]
                })
            elif invalid_dep["issue"] == "self_dependency":
                suggestions.append({
                    "issue_type": "self_dependency",
                    "description": f"Task cannot depend on itself",
                    "suggested_action": "Remove self-dependency",
                    "affected_tasks": [invalid_dep['predecessor_id']]
                })

        return suggestions

