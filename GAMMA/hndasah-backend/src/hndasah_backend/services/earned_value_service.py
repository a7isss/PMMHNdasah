"""
Earned Value Management Service for WhatsApp PM System v3.0 (Gamma)
EVM calculations for project performance measurement and forecasting
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import structlog
from decimal import Decimal, ROUND_HALF_UP

from models.sqlalchemy.task import Task
from models.sqlalchemy.project import Project
from schemas.task import EarnedValueMetrics, EVMAnalysis, EVMPrediction

logger = structlog.get_logger(__name__)


class EarnedValueService:
    """Service for Earned Value Management calculations and analysis."""

    def __init__(self):
        pass

    async def calculate_project_evm(
        self,
        project_id: UUID,
        tasks: List[Task],
        project_budget: Decimal,
        project_start_date: date,
        project_end_date: date,
        db_session=None
    ) -> EarnedValueMetrics:
        """
        Calculate comprehensive Earned Value metrics for a project.

        Args:
            project_id: Project identifier
            tasks: List of project tasks
            project_budget: Total project budget
            project_start_date: Project planned start date
            project_end_date: Project planned end date

        Returns:
            Complete EVM metrics
        """
        try:
            # Calculate basic EVM components
            pv = self._calculate_planned_value(tasks, project_budget, project_start_date, project_end_date)
            ev = self._calculate_earned_value(tasks, project_budget)
            ac = self._calculate_actual_cost(tasks)

            # Calculate variances
            sv = ev - pv  # Schedule Variance
            cv = ev - ac  # Cost Variance

            # Calculate performance indices
            spi = ev / pv if pv > 0 else Decimal('0')  # Schedule Performance Index
            cpi = ev / ac if ac > 0 else Decimal('0')  # Cost Performance Index

            # Calculate estimates at completion
            eac = self._calculate_eac(ac, ev, project_budget, cpi)
            etc = eac - ac  # Estimate to Complete

            # Calculate variances at completion
            vac = project_budget - eac  # Variance at Completion

            # Calculate TCPI (To Complete Performance Index)
            remaining_budget = project_budget - ac
            tcpi = remaining_budget / (eac - ev) if (eac - ev) > 0 else Decimal('0')

            # Calculate project completion percentage
            bac = project_budget  # Budget at Completion
            pc = (ev / bac * 100) if bac > 0 else Decimal('0')  # Percent Complete

            return EarnedValueMetrics(
                project_id=project_id,
                planned_value=pv,
                earned_value=ev,
                actual_cost=ac,
                budget_at_completion=bac,
                schedule_variance=sv,
                cost_variance=cv,
                schedule_performance_index=spi,
                cost_performance_index=cpi,
                estimate_at_completion=eac,
                estimate_to_complete=etc,
                variance_at_completion=vac,
                to_complete_performance_index=tcpi,
                percent_complete=pc,
                calculated_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error("EVM calculation failed", error=str(e), project_id=str(project_id))
            # Return zero metrics on error
            return EarnedValueMetrics(
                project_id=project_id,
                planned_value=Decimal('0'),
                earned_value=Decimal('0'),
                actual_cost=Decimal('0'),
                budget_at_completion=project_budget,
                schedule_variance=Decimal('0'),
                cost_variance=Decimal('0'),
                schedule_performance_index=Decimal('0'),
                cost_performance_index=Decimal('0'),
                estimate_at_completion=Decimal('0'),
                estimate_to_complete=Decimal('0'),
                variance_at_completion=Decimal('0'),
                to_complete_performance_index=Decimal('0'),
                percent_complete=Decimal('0'),
                calculated_at=datetime.utcnow()
            )

    def _calculate_planned_value(
        self,
        tasks: List[Task],
        project_budget: Decimal,
        project_start_date: date,
        project_end_date: date
    ) -> Decimal:
        """Calculate Planned Value (PV) - budgeted cost of work scheduled."""
        total_days = (project_end_date - project_start_date).days
        if total_days <= 0:
            return Decimal('0')

        # Calculate days elapsed from project start
        days_elapsed = (date.today() - project_start_date).days
        if days_elapsed <= 0:
            return Decimal('0')

        # Simple linear distribution of budget over time
        # In a real implementation, this would consider task schedules
        progress_ratio = min(days_elapsed / total_days, 1.0)
        return (project_budget * Decimal(str(progress_ratio))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _calculate_earned_value(self, tasks: List[Task], project_budget: Decimal) -> Decimal:
        """Calculate Earned Value (EV) - budgeted cost of work performed."""
        total_budgeted_cost = sum((task.budgeted_cost or Decimal('0')) for task in tasks)
        if total_budgeted_cost <= 0:
            return Decimal('0')

        # Calculate weighted progress based on task completion
        total_earned = Decimal('0')
        for task in tasks:
            task_budget = task.budgeted_cost or Decimal('0')
            if task_budget > 0:
                # Weight by task budget and completion percentage
                task_earned = task_budget * (Decimal(str(task.progress_percentage)) / Decimal('100'))
                total_earned += task_earned

        return total_earned.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _calculate_actual_cost(self, tasks: List[Task]) -> Decimal:
        """Calculate Actual Cost (AC) - actual cost incurred."""
        total_actual_cost = sum((task.actual_cost or Decimal('0')) for task in tasks)
        return total_actual_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _calculate_eac(
        self,
        actual_cost: Decimal,
        earned_value: Decimal,
        budget_at_completion: Decimal,
        cpi: Decimal
    ) -> Decimal:
        """Calculate Estimate at Completion (EAC)."""
        if cpi <= 0:
            # If CPI is zero or negative, assume future performance at planned rate
            return budget_at_completion

        # EAC = AC + (BAC - EV) / CPI
        remaining_work = budget_at_completion - earned_value
        if remaining_work <= 0:
            return actual_cost  # Project complete

        future_cost = remaining_work / cpi
        eac = actual_cost + future_cost

        return eac.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    async def analyze_evm_performance(self, evm_metrics: EarnedValueMetrics) -> EVMAnalysis:
        """
        Analyze EVM metrics and provide performance insights.

        Args:
            evm_metrics: Calculated EVM metrics

        Returns:
            Detailed performance analysis
        """
        # Determine schedule status
        schedule_status = self._analyze_schedule_status(evm_metrics)

        # Determine cost status
        cost_status = self._analyze_cost_status(evm_metrics)

        # Calculate forecast completion date
        forecast_completion = self._calculate_forecast_completion(evm_metrics)

        # Generate recommendations
        recommendations = self._generate_evm_recommendations(evm_metrics, schedule_status, cost_status)

        # Calculate risk indicators
        risk_indicators = self._calculate_risk_indicators(evm_metrics)

        return EVMAnalysis(
            schedule_status=schedule_status,
            cost_status=cost_status,
            forecast_completion_date=forecast_completion,
            recommendations=recommendations,
            risk_indicators=risk_indicators,
            analysis_date=datetime.utcnow()
        )

    def _analyze_schedule_status(self, evm: EarnedValueMetrics) -> str:
        """Analyze project schedule performance."""
        if evm.schedule_variance > 0:
            return "ahead_of_schedule"
        elif evm.schedule_variance == 0:
            return "on_schedule"
        else:
            sv_percent = abs(evm.schedule_variance / evm.planned_value * 100) if evm.planned_value > 0 else 0
            if sv_percent > 20:
                return "significantly_behind_schedule"
            elif sv_percent > 10:
                return "moderately_behind_schedule"
            else:
                return "slightly_behind_schedule"

    def _analyze_cost_status(self, evm: EarnedValueMetrics) -> str:
        """Analyze project cost performance."""
        if evm.cost_variance > 0:
            return "under_budget"
        elif evm.cost_variance == 0:
            return "on_budget"
        else:
            cv_percent = abs(evm.cost_variance / evm.earned_value * 100) if evm.earned_value > 0 else 0
            if cv_percent > 20:
                return "significantly_over_budget"
            elif cv_percent > 10:
                return "moderately_over_budget"
            else:
                return "slightly_over_budget"

    def _calculate_forecast_completion(self, evm: EarnedValueMetrics) -> Optional[date]:
        """Calculate forecast project completion date."""
        if evm.schedule_performance_index <= 0:
            return None  # Cannot forecast

        # Simple forecasting based on SPI
        # In a real implementation, this would consider task schedules
        days_remaining = 30  # Placeholder - would calculate from actual task schedules
        adjusted_days = days_remaining / float(evm.schedule_performance_index)

        return date.today() + timedelta(days=int(adjusted_days))

    def _generate_evm_recommendations(
        self,
        evm: EarnedValueMetrics,
        schedule_status: str,
        cost_status: str
    ) -> List[str]:
        """Generate recommendations based on EVM analysis."""
        recommendations = []

        # Schedule recommendations
        if "behind_schedule" in schedule_status:
            if evm.schedule_performance_index < 0.8:
                recommendations.append("Critical: Schedule performance is poor. Consider crashing or fast-tracking critical path activities.")
            else:
                recommendations.append("Monitor schedule variance closely and implement schedule recovery actions.")

        # Cost recommendations
        if "over_budget" in cost_status:
            if evm.cost_performance_index < 0.8:
                recommendations.append("Critical: Cost performance is poor. Review budget allocations and implement cost control measures.")
            else:
                recommendations.append("Track cost variances and implement corrective actions to prevent further overruns.")

        # TCPI recommendations
        if evm.to_complete_performance_index > 1.2:
            recommendations.append("High TCPI indicates aggressive performance needed for remaining work. Consider scope reduction or additional resources.")

        # General recommendations
        if evm.percent_complete < 50 and (evm.schedule_performance_index < 0.9 or evm.cost_performance_index < 0.9):
            recommendations.append("Early warning: Project is trending poorly. Implement immediate corrective actions.")

        if not recommendations:
            recommendations.append("Project performance is within acceptable ranges. Continue monitoring.")

        return recommendations

    def _calculate_risk_indicators(self, evm: EarnedValueMetrics) -> Dict[str, Any]:
        """Calculate project risk indicators based on EVM metrics."""
        risk_score = 0
        risk_factors = []

        # Schedule risk
        if evm.schedule_performance_index < 0.9:
            risk_score += 2
            risk_factors.append("schedule_performance")
        elif evm.schedule_performance_index < 0.95:
            risk_score += 1
            risk_factors.append("schedule_trending")

        # Cost risk
        if evm.cost_performance_index < 0.9:
            risk_score += 2
            risk_factors.append("cost_performance")
        elif evm.cost_performance_index < 0.95:
            risk_score += 1
            risk_factors.append("cost_trending")

        # TCPI risk
        if evm.to_complete_performance_index > 1.1:
            risk_score += 1
            risk_factors.append("completion_performance")

        # Variance at completion risk
        if evm.variance_at_completion < 0:
            vac_percent = abs(evm.variance_at_completion / evm.budget_at_completion * 100)
            if vac_percent > 15:
                risk_score += 2
                risk_factors.append("budget_completion")
            elif vac_percent > 5:
                risk_score += 1
                risk_factors.append("budget_completion")

        # Determine overall risk level
        if risk_score >= 4:
            risk_level = "high"
        elif risk_score >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "overall_risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "mitigation_priority": "high" if risk_level == "high" else "medium" if risk_level == "medium" else "low"
        }

    async def predict_project_outcomes(
        self,
        evm_metrics: EarnedValueMetrics,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> EVMPrediction:
        """
        Predict project outcomes using EVM metrics and historical data.

        Args:
            evm_metrics: Current EVM metrics
            historical_data: Optional historical project data for improved predictions

        Returns:
            Project outcome predictions
        """
        # Predict final cost
        predicted_final_cost = evm_metrics.estimate_at_completion

        # Predict completion date
        predicted_completion_date = self._calculate_forecast_completion(evm_metrics)

        # Calculate confidence intervals
        cost_confidence_interval = self._calculate_cost_confidence_interval(evm_metrics, historical_data)
        schedule_confidence_interval = self._calculate_schedule_confidence_interval(evm_metrics, historical_data)

        # Predict success probability
        success_probability = self._calculate_success_probability(evm_metrics)

        # Identify key risks
        key_risks = self._identify_key_risks(evm_metrics)

        return EVMPrediction(
            predicted_final_cost=predicted_final_cost,
            predicted_completion_date=predicted_completion_date,
            cost_confidence_interval=cost_confidence_interval,
            schedule_confidence_interval=schedule_confidence_interval,
            success_probability=success_probability,
            key_risks=key_risks,
            prediction_date=datetime.utcnow()
        )

    def _calculate_cost_confidence_interval(
        self,
        evm: EarnedValueMetrics,
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Decimal]:
        """Calculate confidence interval for cost predictions."""
        # Simple confidence interval based on CPI variability
        # In a real implementation, this would use statistical analysis of historical data

        base_eac = evm.estimate_at_completion
        cpi_variability = Decimal('0.1')  # 10% variability assumption

        lower_bound = base_eac * (1 - cpi_variability)
        upper_bound = base_eac * (1 + cpi_variability)

        return {
            "lower_bound": lower_bound.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "upper_bound": upper_bound.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "confidence_level": Decimal('80')  # 80% confidence
        }

    def _calculate_schedule_confidence_interval(
        self,
        evm: EarnedValueMetrics,
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, date]:
        """Calculate confidence interval for schedule predictions."""
        # Simple schedule confidence interval
        base_date = self._calculate_forecast_completion(evm)
        if not base_date:
            return {"lower_bound": None, "upper_bound": None, "confidence_level": Decimal('0')}

        # Assume 15% variability in schedule predictions
        variability_days = 15  # days

        lower_bound = base_date - timedelta(days=variability_days)
        upper_bound = base_date + timedelta(days=variability_days)

        return {
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence_level": Decimal('75')  # 75% confidence
        }

    def _calculate_success_probability(self, evm: EarnedValueMetrics) -> Decimal:
        """Calculate probability of project success."""
        # Simple success probability calculation based on EVM metrics
        success_score = 0

        # Schedule performance (40% weight)
        if evm.schedule_performance_index >= 1.0:
            success_score += 40
        elif evm.schedule_performance_index >= 0.9:
            success_score += 30
        elif evm.schedule_performance_index >= 0.8:
            success_score += 20
        else:
            success_score += 10

        # Cost performance (40% weight)
        if evm.cost_performance_index >= 1.0:
            success_score += 40
        elif evm.cost_performance_index >= 0.9:
            success_score += 30
        elif evm.cost_performance_index >= 0.8:
            success_score += 20
        else:
            success_score += 10

        # Progress (20% weight)
        if evm.percent_complete >= 75:
            success_score += 20
        elif evm.percent_complete >= 50:
            success_score += 15
        elif evm.percent_complete >= 25:
            success_score += 10
        else:
            success_score += 5

        return Decimal(str(success_score))

    def _identify_key_risks(self, evm: EarnedValueMetrics) -> List[str]:
        """Identify key project risks based on EVM metrics."""
        risks = []

        if evm.schedule_performance_index < 0.85:
            risks.append("Schedule slippage risk - SPI indicates significant delays")

        if evm.cost_performance_index < 0.85:
            risks.append("Cost overrun risk - CPI indicates budget issues")

        if evm.to_complete_performance_index > 1.2:
            risks.append("Completion performance risk - TCPI indicates unrealistic future performance requirements")

        if evm.variance_at_completion < 0:
            vac_percent = abs(evm.variance_at_completion / evm.budget_at_completion * 100)
            if vac_percent > 20:
                risks.append(f"Budget completion risk - projected shortfall of {vac_percent:.1f}%")

        if evm.percent_complete < 30 and (date.today() - min(date.today(), date.today())):  # Would need actual project start date
            risks.append("Early stage performance risk - poor initial performance trends")

        return risks if risks else ["No significant risks identified based on current EVM metrics"]

