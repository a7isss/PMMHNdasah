"""
Import/Export Service for WhatsApp PM System v3.0 (Gamma)
JSON, CSV, and Excel import/export functionality with validation
"""

import json
import csv
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import structlog
from decimal import Decimal

import pandas as pd
from ..models.sqlalchemy.task import Task
from ..models.sqlalchemy.project import Project
from ..models.sqlalchemy.user import User
from ..schemas.task import (
    JsonTaskStructure, JsonProjectStructure, ImportResult, ExportResult,
    ImportExportRequest
)

logger = structlog.get_logger(__name__)


class ImportExportService:
    """Service for importing and exporting task/project data."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    async def import_json_tasks(
        self,
        json_data: str,
        project_id: str,
        created_by: str,
        db_session=None
    ) -> ImportResult:
        """
        Import tasks from JSON structure.

        Args:
            json_data: JSON string containing task data
            project_id: Target project ID
            created_by: User performing the import

        Returns:
            Import operation results
        """
        try:
            # Parse JSON data
            data = json.loads(json_data)

            # Handle both single project structure and task array
            if isinstance(data, dict) and 'tasks' in data:
                # Project structure
                project_data = JsonProjectStructure(**data)
                tasks_data = project_data.tasks
            elif isinstance(data, list):
                # Task array
                tasks_data = [JsonTaskStructure(**task) for task in data]
            else:
                # Single task
                tasks_data = [JsonTaskStructure(**data)]

            # Validate and import tasks
            return await self._import_task_structures(tasks_data, project_id, created_by, db_session)

        except json.JSONDecodeError as e:
            return ImportResult(
                total_records=0,
                successful_imports=0,
                failed_imports=1,
                errors=[{"row": 0, "field": "json", "error": f"Invalid JSON format: {str(e)}"}]
            )
        except Exception as e:
            logger.error("JSON import failed", error=str(e))
            return ImportResult(
                total_records=0,
                successful_imports=0,
                failed_imports=1,
                errors=[{"row": 0, "field": "general", "error": f"Import failed: {str(e)}"}]
            )

    async def import_csv_tasks(
        self,
        csv_content: str,
        project_id: str,
        created_by: str,
        db_session=None
    ) -> ImportResult:
        """
        Import tasks from CSV content.

        Args:
            csv_content: CSV string content
            project_id: Target project ID
            created_by: User performing the import

        Returns:
            Import operation results
        """
        try:
            # Parse CSV
            csv_reader = csv.DictReader(csv_content.splitlines())
            tasks_data = []

            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header
                try:
                    # Convert CSV row to JsonTaskStructure
                    task_data = self._csv_row_to_task_structure(row, row_num)
                    tasks_data.append(task_data)
                except Exception as e:
                    return ImportResult(
                        total_records=len(list(csv_reader)) + 1,  # +1 for current row
                        successful_imports=0,
                        failed_imports=1,
                        errors=[{"row": row_num, "field": "parsing", "error": f"Failed to parse row: {str(e)}"}]
                    )

            # Import tasks
            return await self._import_task_structures(tasks_data, project_id, created_by, db_session)

        except Exception as e:
            logger.error("CSV import failed", error=str(e))
            return ImportResult(
                total_records=0,
                successful_imports=0,
                failed_imports=1,
                errors=[{"row": 0, "field": "general", "error": f"CSV import failed: {str(e)}"}]
            )

    async def import_excel_tasks(
        self,
        excel_content: bytes,
        project_id: str,
        created_by: str,
        sheet_name: str = "Tasks",
        db_session=None
    ) -> ImportResult:
        """
        Import tasks from Excel file content.

        Args:
            excel_content: Excel file bytes
            project_id: Target project ID
            created_by: User performing the import
            sheet_name: Excel sheet name to read from

        Returns:
            Import operation results
        """
        try:
            # Read Excel file
            df = pd.read_excel(excel_content, sheet_name=sheet_name)

            tasks_data = []
            for idx, row in df.iterrows():
                try:
                    # Convert DataFrame row to JsonTaskStructure
                    task_data = self._excel_row_to_task_structure(row, idx + 2)  # +2 for header and 0-indexing
                    tasks_data.append(task_data)
                except Exception as e:
                    return ImportResult(
                        total_records=len(df),
                        successful_imports=0,
                        failed_imports=1,
                        errors=[{"row": idx + 2, "field": "parsing", "error": f"Failed to parse row: {str(e)}"}]
                    )

            # Import tasks
            return await self._import_task_structures(tasks_data, project_id, created_by, db_session)

        except Exception as e:
            logger.error("Excel import failed", error=str(e))
            return ImportResult(
                total_records=0,
                successful_imports=0,
                failed_imports=1,
                errors=[{"row": 0, "field": "general", "error": f"Excel import failed: {str(e)}"}]
            )

    async def export_tasks_json(
        self,
        tasks: List[Task],
        project: Project,
        export_request: ImportExportRequest,
        db_session=None
    ) -> ExportResult:
        """
        Export tasks to JSON format.

        Args:
            tasks: Tasks to export
            project: Project information
            export_request: Export configuration

        Returns:
            Export operation results
        """
        try:
            # Convert tasks to JSON structure
            json_tasks = []
            for task in tasks:
                json_task = self._task_to_json_structure(task, export_request)
                json_tasks.append(json_task)

            # Create project structure if requested
            if export_request.include_subtasks:
                # Build hierarchy
                task_dict = {str(task.id): task for task in tasks}
                root_tasks = []

                for task in tasks:
                    if not task.parent_task_id or str(task.parent_task_id) not in task_dict:
                        root_tasks.append(task)

                # Recursively build task hierarchy
                json_tasks = []
                for root_task in root_tasks:
                    json_task = self._build_task_hierarchy(root_task, task_dict, export_request)
                    json_tasks.append(json_task)

            # Create export data
            if export_request.include_metadata:
                export_data = JsonProjectStructure(
                    id=str(project.id),
                    name=project.name,
                    description=project.description,
                    status=project.status or "active",
                    start_date=project.start_date.isoformat() if project.start_date else None,
                    end_date=project.end_date.isoformat() if project.end_date else None,
                    budget=float(project.budget) if project.budget else None,
                    tasks=json_tasks
                )
            else:
                export_data = json_tasks

            # Generate filename and save
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"tasks_export_{project.id}_{timestamp}.json"
            filepath = self.data_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data.dict() if hasattr(export_data, 'dict') else export_data,
                         f, indent=2, ensure_ascii=False)

            return ExportResult(
                filename=filename,
                file_path=str(filepath),
                record_count=len(json_tasks),
                file_size_bytes=filepath.stat().st_size,
                generated_at=datetime.utcnow(),
                format="json"
            )

        except Exception as e:
            logger.error("JSON export failed", error=str(e))
            raise

    async def export_tasks_csv(
        self,
        tasks: List[Task],
        project: Project,
        export_request: ImportExportRequest,
        db_session=None
    ) -> ExportResult:
        """
        Export tasks to CSV format.

        Args:
            tasks: Tasks to export
            project: Project information
            export_request: Export configuration

        Returns:
            Export operation results
        """
        try:
            # Prepare CSV data
            csv_data = []
            headers = [
                'id', 'name', 'description', 'status', 'progress_percentage',
                'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date',
                'planned_duration_days', 'actual_duration_days', 'estimated_hours', 'actual_hours',
                'budgeted_cost', 'actual_cost', 'assigned_to', 'parent_task_id',
                'predecessor_tasks', 'successor_tasks', 'lag_days', 'tags'
            ]

            for task in tasks:
                row = {
                    'id': str(task.id),
                    'name': task.name,
                    'description': task.description,
                    'status': task.status,
                    'progress_percentage': task.progress_percentage,
                    'planned_start_date': task.planned_start_date.isoformat() if task.planned_start_date else '',
                    'planned_end_date': task.planned_end_date.isoformat() if task.planned_end_date else '',
                    'actual_start_date': task.actual_start_date.isoformat() if task.actual_start_date else '',
                    'actual_end_date': task.actual_end_date.isoformat() if task.actual_end_date else '',
                    'planned_duration_days': task.planned_duration_days,
                    'actual_duration_days': task.actual_duration_days,
                    'estimated_hours': float(task.estimated_hours) if task.estimated_hours else '',
                    'actual_hours': float(task.actual_hours) if task.actual_hours else '',
                    'budgeted_cost': float(task.budgeted_cost),
                    'actual_cost': float(task.actual_cost),
                    'assigned_to': str(task.assigned_to) if task.assigned_to else '',
                    'parent_task_id': str(task.parent_task_id) if task.parent_task_id else '',
                    'predecessor_tasks': ','.join(str(pid) for pid in (task.predecessor_tasks or [])),
                    'successor_tasks': ','.join(str(sid) for sid in (task.successor_tasks or [])),
                    'lag_days': task.lag_days,
                    'tags': ','.join(task.tags or [])
                }
                csv_data.append(row)

            # Generate filename and save
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"tasks_export_{project.id}_{timestamp}.csv"
            filepath = self.data_dir / filename

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(csv_data)

            return ExportResult(
                filename=filename,
                file_path=str(filepath),
                record_count=len(csv_data),
                file_size_bytes=filepath.stat().st_size,
                generated_at=datetime.utcnow(),
                format="csv"
            )

        except Exception as e:
            logger.error("CSV export failed", error=str(e))
            raise

    async def export_tasks_excel(
        self,
        tasks: List[Task],
        project: Project,
        export_request: ImportExportRequest,
        db_session=None
    ) -> ExportResult:
        """
        Export tasks to Excel format.

        Args:
            tasks: Tasks to export
            project: Project information
            export_request: Export configuration

        Returns:
            Export operation results
        """
        try:
            # Prepare data for Excel
            excel_data = []
            for task in tasks:
                row = {
                    'ID': str(task.id),
                    'Name': task.name,
                    'Description': task.description,
                    'Status': task.status.replace('_', ' ').title(),
                    'Progress %': task.progress_percentage,
                    'Planned Start': task.planned_start_date,
                    'Planned End': task.planned_end_date,
                    'Actual Start': task.actual_start_date,
                    'Actual End': task.actual_end_date,
                    'Planned Duration (Days)': task.planned_duration_days,
                    'Actual Duration (Days)': task.actual_duration_days,
                    'Estimated Hours': float(task.estimated_hours) if task.estimated_hours else None,
                    'Actual Hours': float(task.actual_hours) if task.actual_hours else None,
                    'Budgeted Cost': float(task.budgeted_cost),
                    'Actual Cost': float(task.actual_cost),
                    'Assigned To': str(task.assigned_to) if task.assigned_to else None,
                    'Parent Task': str(task.parent_task_id) if task.parent_task_id else None,
                    'Predecessors': ', '.join(str(pid) for pid in (task.predecessor_tasks or [])),
                    'Successors': ', '.join(str(sid) for sid in (task.successor_tasks or [])),
                    'Lag Days': task.lag_days,
                    'Tags': ', '.join(task.tags or [])
                }
                excel_data.append(row)

            # Create DataFrame and save to Excel
            df = pd.DataFrame(excel_data)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"tasks_export_{project.id}_{timestamp}.xlsx"
            filepath = self.data_dir / filename

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Tasks', index=False)

                # Add project info sheet
                project_info = {
                    'Field': ['Project Name', 'Description', 'Status', 'Budget', 'Start Date', 'End Date', 'Total Tasks'],
                    'Value': [
                        project.name,
                        project.description or '',
                        (project.status or 'active').replace('_', ' ').title(),
                        float(project.budget) if project.budget else 0,
                        project.start_date.isoformat() if project.start_date else '',
                        project.end_date.isoformat() if project.end_date else '',
                        len(tasks)
                    ]
                }
                project_df = pd.DataFrame(project_info)
                project_df.to_excel(writer, sheet_name='Project Info', index=False)

            return ExportResult(
                filename=filename,
                file_path=str(filepath),
                record_count=len(excel_data),
                file_size_bytes=filepath.stat().st_size,
                generated_at=datetime.utcnow(),
                format="excel"
            )

        except Exception as e:
            logger.error("Excel export failed", error=str(e))
            raise

    async def _import_task_structures(
        self,
        tasks_data: List[JsonTaskStructure],
        project_id: str,
        created_by: str,
        db_session=None
    ) -> ImportResult:
        """Import task structures into the database."""
        total_records = len(tasks_data)
        successful_imports = 0
        failed_imports = 0
        errors = []
        warnings = []
        created_ids = []

        # Track task ID mappings for dependencies
        id_mapping = {}  # old_id -> new_id

        for idx, task_data in enumerate(tasks_data):
            try:
                # Convert JSON structure to TaskCreate
                task_create_data = self._json_task_to_task_create(task_data, project_id, created_by)

                # Handle ID mapping for dependencies
                if task_data.id:
                    id_mapping[task_data.id] = str(uuid.uuid4())  # Generate new ID
                    task_create_data.id = id_mapping[task_data.id]

                # Create task
                from ..services.task_service import TaskService
                task_service = TaskService()
                task = await task_service.create_task(task_create_data, project_id, created_by, db_session)

                created_ids.append(str(task.id))
                successful_imports += 1

                # Handle subtasks recursively
                if task_data.subtasks:
                    subtask_result = await self._import_task_structures(
                        task_data.subtasks, project_id, created_by, db_session
                    )
                    successful_imports += subtask_result.successful_imports
                    failed_imports += subtask_result.failed_imports
                    errors.extend(subtask_result.errors)
                    created_ids.extend(subtask_result.created_ids)

            except Exception as e:
                failed_imports += 1
                errors.append({
                    "row": idx + 1,
                    "field": "general",
                    "error": f"Failed to import task '{task_data.name}': {str(e)}"
                })

        return ImportResult(
            total_records=total_records,
            successful_imports=successful_imports,
            failed_imports=failed_imports,
            errors=errors,
            warnings=warnings,
            created_ids=created_ids
        )

    def _csv_row_to_task_structure(self, row: Dict[str, Any], row_num: int) -> JsonTaskStructure:
        """Convert CSV row to JsonTaskStructure."""
        # Map CSV columns to task structure
        return JsonTaskStructure(
            id=row.get('id'),
            name=row.get('name', f'Imported Task {row_num}'),
            description=row.get('description'),
            status=row.get('status', 'not_started'),
            progress_percentage=int(row.get('progress_percentage', 0)),
            planned_start_date=row.get('planned_start_date'),
            planned_end_date=row.get('planned_end_date'),
            planned_duration_days=int(row.get('planned_duration_days', 0)) if row.get('planned_duration_days') else None,
            budgeted_cost=float(row.get('budgeted_cost', 0)),
            assigned_to=row.get('assigned_to'),
            tags=row.get('tags', '').split(',') if row.get('tags') else []
        )

    def _excel_row_to_task_structure(self, row: pd.Series, row_num: int) -> JsonTaskStructure:
        """Convert Excel row to JsonTaskStructure."""
        return JsonTaskStructure(
            id=str(row.get('ID')) if pd.notna(row.get('ID')) else None,
            name=str(row.get('Name', f'Imported Task {row_num}')),
            description=str(row.get('Description')) if pd.notna(row.get('Description')) else None,
            status=str(row.get('Status', 'not_started')).lower().replace(' ', '_'),
            progress_percentage=int(row.get('Progress %', 0)),
            planned_start_date=str(row.get('Planned Start')) if pd.notna(row.get('Planned Start')) else None,
            planned_end_date=str(row.get('Planned End')) if pd.notna(row.get('Planned End')) else None,
            planned_duration_days=int(row.get('Planned Duration (Days)')) if pd.notna(row.get('Planned Duration (Days)')) else None,
            budgeted_cost=float(row.get('Budgeted Cost', 0)),
            assigned_to=str(row.get('Assigned To')) if pd.notna(row.get('Assigned To')) else None,
            tags=str(row.get('Tags', '')).split(', ') if pd.notna(row.get('Tags')) else []
        )

    def _json_task_to_task_create(self, json_task: JsonTaskStructure, project_id: str, created_by: str) -> Dict[str, Any]:
        """Convert JsonTaskStructure to TaskCreate data."""
        from ..schemas.task import TaskCreate

        # Parse dates
        planned_start = None
        planned_end = None
        actual_start = None
        actual_end = None

        if json_task.planned_start_date:
            try:
                planned_start = date.fromisoformat(json_task.planned_start_date)
            except:
                planned_start = None

        if json_task.planned_end_date:
            try:
                planned_end = date.fromisoformat(json_task.planned_end_date)
            except:
                planned_end = None

        if json_task.actual_start_date:
            try:
                actual_start = date.fromisoformat(json_task.actual_start_date)
            except:
                actual_start = None

        if json_task.actual_end_date:
            try:
                actual_end = date.fromisoformat(json_task.actual_end_date)
            except:
                actual_end = None

        return {
            "project_id": project_id,
            "name": json_task.name,
            "description": json_task.description,
            "task_code": json_task.task_code,
            "planned_start_date": planned_start,
            "planned_end_date": planned_end,
            "actual_start_date": actual_start,
            "actual_end_date": actual_end,
            "planned_duration_days": json_task.planned_duration_days,
            "actual_duration_days": json_task.actual_duration_days,
            "progress_percentage": json_task.progress_percentage,
            "status": json_task.status,
            "assigned_to": json_task.assigned_to,  # This might need user ID resolution
            "estimated_hours": Decimal(str(json_task.estimated_hours)) if json_task.estimated_hours else None,
            "actual_hours": Decimal(str(json_task.actual_hours)) if json_task.actual_hours else None,
            "budgeted_cost": Decimal(str(json_task.budgeted_cost)),
            "actual_cost": Decimal(str(json_task.actual_cost)),
            "parent_task_id": json_task.parent_task_id,
            "predecessor_tasks": json_task.predecessor_tasks,
            "successor_tasks": json_task.successor_tasks,
            "lag_days": json_task.lag_days,
            "tags": json_task.tags,
            "custom_fields": json_task.custom_fields
        }

    def _task_to_json_structure(self, task: Task, export_request: ImportExportRequest) -> Dict[str, Any]:
        """Convert Task to JSON structure for export."""
        return {
            "id": str(task.id),
            "name": task.name,
            "description": task.description,
            "task_code": task.task_code,
            "status": task.status,
            "progress_percentage": task.progress_percentage,
            "planned_start_date": task.planned_start_date.isoformat() if task.planned_start_date else None,
            "planned_end_date": task.planned_end_date.isoformat() if task.planned_end_date else None,
            "actual_start_date": task.actual_start_date.isoformat() if task.actual_start_date else None,
            "actual_end_date": task.actual_end_date.isoformat() if task.actual_end_date else None,
            "planned_duration_days": task.planned_duration_days,
            "actual_duration_days": task.actual_duration_days,
            "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
            "actual_hours": float(task.actual_hours) if task.actual_hours else None,
            "budgeted_cost": float(task.budgeted_cost),
            "actual_cost": float(task.actual_cost),
            "assigned_to": str(task.assigned_to) if task.assigned_to else None,
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
            "predecessor_tasks": [str(pid) for pid in (task.predecessor_tasks or [])],
            "successor_tasks": [str(sid) for sid in (task.successor_tasks or [])],
            "lag_days": task.lag_days,
            "tags": task.tags or [],
            "custom_fields": task.custom_fields or {}
        }

    def _build_task_hierarchy(self, task: Task, task_dict: Dict[str, Task], export_request: ImportExportRequest) -> Dict[str, Any]:
        """Build hierarchical task structure for export."""
        json_task = self._task_to_json_structure(task, export_request)

        # Add subtasks
        if export_request.include_subtasks:
            subtasks = []
            for task_id, t in task_dict.items():
                if t.parent_task_id == task.id:
                    subtasks.append(self._build_task_hierarchy(t, task_dict, export_request))
            json_task["subtasks"] = subtasks

        return json_task
