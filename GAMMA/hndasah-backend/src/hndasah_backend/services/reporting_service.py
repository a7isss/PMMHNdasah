"""
Reporting Service for WhatsApp PM System v3.0 (Gamma)
PDF report generation using ReportLab for tasks, projects, and EVM analytics
"""

import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import structlog
from decimal import Decimal
from pathlib import Path

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, Flowable
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from ..models.sqlalchemy.task import Task
from ..models.sqlalchemy.project import Project
from ..schemas.task import (
    EarnedValueMetrics, EVMAnalysis, ReportRequest,
    ReportGenerationResult, ReportTemplate
)

logger = structlog.get_logger(__name__)


class ReportingService:
    """Service for generating PDF reports using ReportLab."""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.styles = self._setup_styles()

    def _setup_styles(self) -> Dict[str, Any]:
        """Setup ReportLab styles for consistent formatting."""
        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue,
            borderColor=colors.darkblue,
            borderWidth=1,
            borderPadding=5
        ))

        styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkgreen
        ))

        styles.add(ParagraphStyle(
            name='MetricValue',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.darkred
        ))

        styles.add(ParagraphStyle(
            name='TableCaption',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.grey
        ))

        return styles

    async def generate_task_report(
        self,
        tasks: List[Task],
        project: Project,
        report_request: ReportRequest,
        db_session=None
    ) -> ReportGenerationResult:
        """
        Generate a comprehensive task report PDF.

        Args:
            tasks: List of tasks to include
            project: Project information
            report_request: Report generation parameters

        Returns:
            Report generation result
        """
        try:
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"task_report_{project.id}_{timestamp}.pdf"
            filepath = self.reports_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build report content
            story = []

            # Title page
            story.extend(self._build_title_page(project, "Task Report", report_request))

            # Executive summary
            story.extend(self._build_task_executive_summary(tasks, project))

            # Task details table
            story.extend(self._build_task_details_table(tasks))

            # Task status breakdown
            story.extend(self._build_task_status_charts(tasks))

            # Critical path analysis
            story.extend(self._build_critical_path_section(tasks))

            # Build PDF
            doc.build(story)

            return ReportGenerationResult(
                report_id=f"task_{project.id}_{timestamp}",
                filename=filename,
                file_path=str(filepath),
                report_type="task_report",
                generated_at=datetime.utcnow(),
                file_size_bytes=filepath.stat().st_size
            )

        except Exception as e:
            logger.error("Task report generation failed", error=str(e), project_id=str(project.id))
            raise

    async def generate_evm_report(
        self,
        evm_metrics: EarnedValueMetrics,
        evm_analysis: EVMAnalysis,
        project: Project,
        tasks: List[Task],
        report_request: ReportRequest,
        db_session=None
    ) -> ReportGenerationResult:
        """
        Generate an Earned Value Management report PDF.

        Args:
            evm_metrics: EVM metrics data
            evm_analysis: EVM analysis results
            project: Project information
            tasks: Project tasks
            report_request: Report generation parameters

        Returns:
            Report generation result
        """
        try:
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"evm_report_{project.id}_{timestamp}.pdf"
            filepath = self.reports_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build report content
            story = []

            # Title page
            story.extend(self._build_title_page(project, "Earned Value Management Report", report_request))

            # EVM Executive Summary
            story.extend(self._build_evm_executive_summary(evm_metrics, evm_analysis))

            # EVM Metrics Dashboard
            story.extend(self._build_evm_metrics_dashboard(evm_metrics))

            # Performance Analysis
            story.extend(self._build_evm_performance_analysis(evm_analysis))

            # Recommendations
            story.extend(self._build_evm_recommendations(evm_analysis))

            # Detailed Task EVM
            story.extend(self._build_task_evm_details(tasks))

            # Build PDF
            doc.build(story)

            return ReportGenerationResult(
                report_id=f"evm_{project.id}_{timestamp}",
                filename=filename,
                file_path=str(filepath),
                report_type="evm_report",
                generated_at=datetime.utcnow(),
                file_size_bytes=filepath.stat().st_size
            )

        except Exception as e:
            logger.error("EVM report generation failed", error=str(e), project_id=str(project.id))
            raise

    async def generate_project_report(
        self,
        project: Project,
        tasks: List[Task],
        evm_metrics: Optional[EarnedValueMetrics] = None,
        report_request: ReportRequest = None,
        db_session=None
    ) -> ReportGenerationResult:
        """
        Generate a comprehensive project report PDF.

        Args:
            project: Project information
            tasks: Project tasks
            evm_metrics: Optional EVM metrics
            report_request: Report generation parameters

        Returns:
            Report generation result
        """
        try:
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"project_report_{project.id}_{timestamp}.pdf"
            filepath = self.reports_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build report content
            story = []

            # Title page
            story.extend(self._build_title_page(project, "Project Status Report", report_request))

            # Project Overview
            story.extend(self._build_project_overview(project, tasks))

            # Task Summary
            story.extend(self._build_task_summary_section(tasks))

            # Progress Analysis
            story.extend(self._build_progress_analysis(tasks))

            # EVM Section (if available)
            if evm_metrics:
                story.extend(self._build_project_evm_section(evm_metrics))

            # Risks and Issues
            story.extend(self._build_risks_issues_section(tasks))

            # Build PDF
            doc.build(story)

            return ReportGenerationResult(
                report_id=f"project_{project.id}_{timestamp}",
                filename=filename,
                file_path=str(filepath),
                report_type="project_report",
                generated_at=datetime.utcnow(),
                file_size_bytes=filepath.stat().st_size
            )

        except Exception as e:
            logger.error("Project report generation failed", error=str(e), project_id=str(project.id))
            raise

    def _build_title_page(self, project: Project, report_title: str, report_request: Optional[ReportRequest]) -> List[Flowable]:
        """Build the report title page."""
        story = []

        # Report title
        story.append(Paragraph(report_title, self.styles['ReportTitle']))
        story.append(Spacer(1, 30))

        # Project information
        story.append(Paragraph(f"Project: {project.name}", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))

        if project.description:
            story.append(Paragraph(f"Description: {project.description}", self.styles['Normal']))
            story.append(Spacer(1, 10))

        # Report metadata
        metadata = [
            f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Project ID: {project.id}",
        ]

        if report_request and report_request.date_range:
            start_date = report_request.date_range.get('start')
            end_date = report_request.date_range.get('end')
            if start_date and end_date:
                metadata.append(f"Date Range: {start_date} to {end_date}")

        for meta in metadata:
            story.append(Paragraph(meta, self.styles['Normal']))
            story.append(Spacer(1, 5))

        story.append(PageBreak())
        return story

    def _build_task_executive_summary(self, tasks: List[Task], project: Project) -> List[Flowable]:
        """Build task report executive summary."""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        # Calculate summary statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        in_progress_tasks = sum(1 for t in tasks if t.status == 'in_progress')
        overdue_tasks = sum(1 for t in tasks if t.planned_end_date and t.planned_end_date < date.today() and t.status != 'completed')

        total_budget = sum((t.budgeted_cost or Decimal('0')) for t in tasks)
        total_actual_cost = sum((t.actual_cost or Decimal('0')) for t in tasks)

        # Summary paragraphs
        summary_text = f"""
        This report provides a comprehensive overview of all tasks in project "{project.name}".
        The project currently has {total_tasks} tasks, with {completed_tasks} completed,
        {in_progress_tasks} in progress, and {overdue_tasks} overdue tasks.
        """

        story.append(Paragraph(summary_text.strip(), self.styles['Normal']))
        story.append(Spacer(1, 15))

        # Key metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Tasks', str(total_tasks)],
            ['Completed Tasks', str(completed_tasks)],
            ['In Progress Tasks', str(in_progress_tasks)],
            ['Overdue Tasks', str(overdue_tasks)],
            ['Total Budget', f"${total_budget:,.2f}"],
            ['Total Actual Cost', f"${total_actual_cost:,.2f}"],
            ['Budget Variance', f"${total_budget - total_actual_cost:,.2f}"]
        ]

        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]))

        story.append(metrics_table)
        story.append(Spacer(1, 20))

        return story

    def _build_task_details_table(self, tasks: List[Task]) -> List[Flowable]:
        """Build detailed task information table."""
        story = []

        story.append(Paragraph("Task Details", self.styles['SectionHeader']))

        # Table headers
        headers = ['Task Name', 'Status', 'Progress', 'Start Date', 'End Date', 'Budget', 'Actual Cost']

        # Table data
        table_data = [headers]

        for task in tasks:
            row = [
                task.name[:30] + '...' if len(task.name) > 30 else task.name,
                task.status.replace('_', ' ').title(),
                f"{task.progress_percentage}%",
                task.planned_start_date.strftime('%Y-%m-%d') if task.planned_start_date else 'N/A',
                task.planned_end_date.strftime('%Y-%m-%d') if task.planned_end_date else 'N/A',
                f"${task.budgeted_cost:,.2f}" if task.budgeted_cost else '$0.00',
                f"${task.actual_cost:,.2f}" if task.actual_cost else '$0.00'
            ]
            table_data.append(row)

        # Create table
        col_widths = [1.5*inch, 1*inch, 0.8*inch, 1*inch, 1*inch, 1*inch, 1*inch]
        task_table = Table(table_data, colWidths=col_widths)

        # Style the table
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(task_table)
        story.append(Spacer(1, 20))

        return story

    def _build_task_status_charts(self, tasks: List[Task]) -> List[Flowable]:
        """Build task status distribution charts/tables."""
        story = []

        story.append(Paragraph("Task Status Distribution", self.styles['SubSectionHeader']))

        # Calculate status counts
        status_counts = {}
        for task in tasks:
            status = task.status.replace('_', ' ').title()
            status_counts[status] = status_counts.get(status, 0) + 1

        # Create status table
        status_data = [['Status', 'Count', 'Percentage']]
        total_tasks = len(tasks)

        for status, count in status_counts.items():
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            status_data.append([status, str(count), f"{percentage:.1f}%"])

        status_table = Table(status_data, colWidths=[2*inch, 1*inch, 1*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(status_table)
        story.append(Spacer(1, 20))

        return story

    def _build_critical_path_section(self, tasks: List[Task]) -> List[Flowable]:
        """Build critical path analysis section."""
        story = []

        story.append(Paragraph("Critical Path Analysis", self.styles['SubSectionHeader']))

        # Find critical path tasks (simplified - tasks with no slack)
        critical_tasks = [t for t in tasks if t.is_critical_path]

        if critical_tasks:
            story.append(Paragraph(f"Found {len(critical_tasks)} tasks on the critical path:", self.styles['Normal']))
            story.append(Spacer(1, 10))

            for task in critical_tasks:
                task_info = f"• {task.name} (Duration: {task.planned_duration_days or 0} days)"
                story.append(Paragraph(task_info, self.styles['Normal']))
        else:
            story.append(Paragraph("No critical path tasks identified.", self.styles['Normal']))

        story.append(Spacer(1, 20))
        return story

    def _build_evm_executive_summary(self, evm_metrics: EarnedValueMetrics, evm_analysis: EVMAnalysis) -> List[Flowable]:
        """Build EVM report executive summary."""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        # Key EVM metrics
        summary_text = f"""
        This Earned Value Management (EVM) report provides a comprehensive analysis of project performance.
        The project shows a Schedule Performance Index (SPI) of {evm_metrics.schedule_performance_index:.3f}
        and Cost Performance Index (CPI) of {evm_metrics.cost_performance_index:.3f}.
        """

        story.append(Paragraph(summary_text.strip(), self.styles['Normal']))
        story.append(Spacer(1, 15))

        # Status indicators
        status_indicators = [
            ['Performance Indicator', 'Value', 'Status'],
            ['Schedule Performance', f"{evm_metrics.schedule_performance_index:.3f}", evm_analysis.schedule_status.replace('_', ' ').title()],
            ['Cost Performance', f"{evm_metrics.cost_performance_index:.3f}", evm_analysis.cost_status.replace('_', ' ').title()],
            ['Budget Variance', f"${evm_metrics.schedule_variance:,.2f}", 'Positive' if evm_metrics.schedule_variance >= 0 else 'Negative'],
            ['Cost Variance', f"${evm_metrics.cost_variance:,.2f}", 'Under Budget' if evm_metrics.cost_variance >= 0 else 'Over Budget'],
            ['Estimate at Completion', f"${evm_metrics.estimate_at_completion:,.2f}", 'Within Budget' if evm_metrics.variance_at_completion >= 0 else 'Over Budget']
        ]

        status_table = Table(status_indicators, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]))

        story.append(status_table)
        story.append(Spacer(1, 20))

        return story

    def _build_evm_metrics_dashboard(self, evm_metrics: EarnedValueMetrics) -> List[Flowable]:
        """Build EVM metrics dashboard."""
        story = []

        story.append(Paragraph("EVM Metrics Dashboard", self.styles['SectionHeader']))

        # Core metrics
        metrics_data = [
            ['Metric', 'Value', 'Description'],
            ['Planned Value (PV)', f"${evm_metrics.planned_value:,.2f}", 'Budgeted cost of work scheduled'],
            ['Earned Value (EV)', f"${evm_metrics.earned_value:,.2f}", 'Budgeted cost of work performed'],
            ['Actual Cost (AC)', f"${evm_metrics.actual_cost:,.2f}", 'Actual cost incurred'],
            ['Budget at Completion (BAC)', f"${evm_metrics.budget_at_completion:,.2f}", 'Total project budget'],
            ['Schedule Variance (SV)', f"${evm_metrics.schedule_variance:,.2f}", 'EV - PV'],
            ['Cost Variance (CV)', f"${evm_metrics.cost_variance:,.2f}", 'EV - AC'],
            ['Schedule Performance Index (SPI)', f"{evm_metrics.schedule_performance_index:.3f}", 'EV/PV'],
            ['Cost Performance Index (CPI)', f"{evm_metrics.cost_performance_index:.3f}", 'EV/AC'],
            ['Estimate at Completion (EAC)', f"${evm_metrics.estimate_at_completion:,.2f}", 'Projected total cost'],
            ['Variance at Completion (VAC)', f"${evm_metrics.variance_at_completion:,.2f}", 'BAC - EAC']
        ]

        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(metrics_table)
        story.append(Spacer(1, 20))

        return story

    def _build_evm_performance_analysis(self, evm_analysis: EVMAnalysis) -> List[Flowable]:
        """Build EVM performance analysis section."""
        story = []

        story.append(Paragraph("Performance Analysis", self.styles['SubSectionHeader']))

        # Schedule status
        schedule_status = f"Schedule Status: {evm_analysis.schedule_status.replace('_', ' ').title()}"
        story.append(Paragraph(schedule_status, self.styles['Normal']))

        # Cost status
        cost_status = f"Cost Status: {evm_analysis.cost_status.replace('_', ' ').title()}"
        story.append(Paragraph(cost_status, self.styles['Normal']))

        if evm_analysis.forecast_completion_date:
            forecast = f"Forecast Completion Date: {evm_analysis.forecast_completion_date.strftime('%Y-%m-%d')}"
            story.append(Paragraph(forecast, self.styles['Normal']))

        story.append(Spacer(1, 15))

        return story

    def _build_evm_recommendations(self, evm_analysis: EVMAnalysis) -> List[Flowable]:
        """Build EVM recommendations section."""
        story = []

        story.append(Paragraph("Recommendations", self.styles['SubSectionHeader']))

        if evm_analysis.recommendations:
            for i, recommendation in enumerate(evm_analysis.recommendations, 1):
                story.append(Paragraph(f"{i}. {recommendation}", self.styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No specific recommendations at this time.", self.styles['Normal']))

        story.append(Spacer(1, 20))

        return story

    def _build_task_evm_details(self, tasks: List[Task]) -> List[Flowable]:
        """Build detailed task EVM information."""
        story = []

        story.append(Paragraph("Task-Level EVM Details", self.styles['SubSectionHeader']))

        # Simplified task EVM table
        task_data = [['Task Name', 'Progress %', 'Budget', 'Actual Cost', 'Variance']]

        for task in tasks:
            variance = (task.budgeted_cost or Decimal('0')) - (task.actual_cost or Decimal('0'))
            row = [
                task.name[:25] + '...' if len(task.name) > 25 else task.name,
                f"{task.progress_percentage}%",
                f"${task.budgeted_cost or 0:,.2f}",
                f"${task.actual_cost or 0:,.2f}",
                f"${variance:,.2f}"
            ]
            task_data.append(row)

        task_table = Table(task_data, colWidths=[2*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(task_table)
        story.append(Spacer(1, 20))

        return story

    def _build_project_overview(self, project: Project, tasks: List[Task]) -> List[Flowable]:
        """Build project overview section."""
        story = []

        story.append(Paragraph("Project Overview", self.styles['SectionHeader']))

        # Project details
        details = [
            f"Project Name: {project.name}",
            f"Description: {project.description or 'N/A'}",
            f"Start Date: {project.start_date.strftime('%Y-%m-%d') if project.start_date else 'Not set'}",
            f"End Date: {project.end_date.strftime('%Y-%m-%d') if project.end_date else 'Not set'}",
            f"Budget: ${project.budget or 0:,.2f}",
            f"Total Tasks: {len(tasks)}",
            f"Status: {project.status.replace('_', ' ').title() if project.status else 'Unknown'}"
        ]

        for detail in details:
            story.append(Paragraph(detail, self.styles['Normal']))
            story.append(Spacer(1, 3))

        story.append(Spacer(1, 15))

        return story

    def _build_task_summary_section(self, tasks: List[Task]) -> List[Flowable]:
        """Build task summary section."""
        story = []

        story.append(Paragraph("Task Summary", self.styles['SubSectionHeader']))

        # Calculate summary stats
        completed = sum(1 for t in tasks if t.status == 'completed')
        in_progress = sum(1 for t in tasks if t.status == 'in_progress')
        not_started = sum(1 for t in tasks if t.status == 'not_started')

        summary_data = [
            ['Status', 'Count', 'Percentage'],
            ['Completed', str(completed), f"{(completed/len(tasks)*100):.1f}%" if tasks else "0%"],
            ['In Progress', str(in_progress), f"{(in_progress/len(tasks)*100):.1f}%" if tasks else "0%"],
            ['Not Started', str(not_started), f"{(not_started/len(tasks)*100):.1f}%" if tasks else "0%"]
        ]

        summary_table = Table(summary_data, colWidths=[1.5*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 20))

        return story

    def _build_progress_analysis(self, tasks: List[Task]) -> List[Flowable]:
        """Build progress analysis section."""
        story = []

        story.append(Paragraph("Progress Analysis", self.styles['SubSectionHeader']))

        if tasks:
            avg_progress = sum(t.progress_percentage for t in tasks) / len(tasks)
            story.append(Paragraph(f"Average Task Progress: {avg_progress:.1f}%", self.styles['MetricValue']))

            # Progress distribution
            progress_ranges = {
                '0-25%': sum(1 for t in tasks if t.progress_percentage <= 25),
                '26-50%': sum(1 for t in tasks if 26 <= t.progress_percentage <= 50),
                '51-75%': sum(1 for t in tasks if 51 <= t.progress_percentage <= 75),
                '76-100%': sum(1 for t in tasks if t.progress_percentage >= 76)
            }

            for range_name, count in progress_ranges.items():
                story.append(Paragraph(f"Tasks {range_name}: {count}", self.styles['Normal']))

        story.append(Spacer(1, 20))

        return story

    def _build_project_evm_section(self, evm_metrics: EarnedValueMetrics) -> List[Flowable]:
        """Build project EVM section."""
        story = []

        story.append(Paragraph("Earned Value Analysis", self.styles['SubSectionHeader']))

        evm_data = [
            ['Metric', 'Value'],
            ['SPI (Schedule Performance)', f"{evm_metrics.schedule_performance_index:.3f}"],
            ['CPI (Cost Performance)', f"{evm_metrics.cost_performance_index:.3f}"],
            ['CV (Cost Variance)', f"${evm_metrics.cost_variance:,.2f}"],
            ['SV (Schedule Variance)', f"${evm_metrics.schedule_variance:,.2f}"],
            ['EAC (Estimate at Completion)', f"${evm_metrics.estimate_at_completion:,.2f}"]
        ]

        evm_table = Table(evm_data, colWidths=[2.5*inch, 1.5*inch])
        evm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(evm_table)
        story.append(Spacer(1, 20))

        return story

    def _build_risks_issues_section(self, tasks: List[Task]) -> List[Flowable]:
        """Build risks and issues section."""
        story = []

        story.append(Paragraph("Risks and Issues", self.styles['SubSectionHeader']))

        # Identify potential risks
        overdue_tasks = [t for t in tasks if t.planned_end_date and t.planned_end_date < date.today() and t.status != 'completed']
        high_budget_tasks = [t for t in tasks if t.budgeted_cost and t.budgeted_cost > 5000]  # Example threshold

        if overdue_tasks:
            story.append(Paragraph(f"⚠️  {len(overdue_tasks)} overdue tasks identified", self.styles['Normal']))

        if high_budget_tasks:
            story.append(Paragraph(f"💰 {len(high_budget_tasks)} high-budget tasks require monitoring", self.styles['Normal']))

        if not overdue_tasks and not high_budget_tasks:
            story.append(Paragraph("✅ No significant risks identified", self.styles['Normal']))

        story.append(Spacer(1, 20))

        return story
