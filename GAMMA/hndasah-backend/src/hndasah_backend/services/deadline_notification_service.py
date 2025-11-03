"""
Deadline Notification Service for WhatsApp PM System v3.0 (Gamma)
Smart reminders and escalation workflows for task deadlines
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import structlog

from models.sqlalchemy.task import Task
from models.sqlalchemy.user import User
from schemas.task import DeadlineNotification, NotificationSchedule

logger = structlog.get_logger(__name__)


class DeadlineNotificationService:
    """Service for managing deadline notifications and reminders."""

    def __init__(self):
        pass

    async def schedule_deadline_notifications(
        self,
        task_id: UUID,
        db_session=None
    ) -> List[NotificationSchedule]:
        """
        Schedule deadline notifications for a task.

        Args:
            task_id: Task identifier

        Returns:
            List of scheduled notifications
        """
        try:
            # Get task with project and assignee info
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task or not task.planned_end_date:
                return []

            # Define notification triggers (days before deadline)
            triggers = [30, 14, 7, 3, 1, 0]  # Days before deadline

            scheduled_notifications = []

            for days_before in triggers:
                notification_date = task.planned_end_date - timedelta(days=days_before)

                # Only schedule future notifications
                if notification_date >= date.today():
                    notification = NotificationSchedule(
                        id=f"{task_id}_{days_before}",
                        task_id=str(task_id),
                        notification_type=f"deadline_reminder_{days_before}d",
                        scheduled_time=datetime.combine(notification_date, datetime.min.time()),
                        status="pending",
                        retry_count=0
                    )
                    scheduled_notifications.append(notification)

            # Store scheduled notifications (in real implementation, save to database)
            await self._store_scheduled_notifications(scheduled_notifications, db_session)

            return scheduled_notifications

        except Exception as e:
            logger.error("Failed to schedule deadline notifications", error=str(e), task_id=str(task_id))
            return []

    async def check_and_send_notifications(self, db_session=None) -> Dict[str, int]:
        """
        Check for due notifications and send them.

        Returns:
            Notification processing statistics
        """
        try:
            # Get pending notifications due now or earlier
            current_time = datetime.utcnow()
            due_notifications = await self._get_due_notifications(current_time, db_session)

            sent_count = 0
            failed_count = 0

            for notification in due_notifications:
                success = await self._send_notification(notification, db_session)
                if success:
                    sent_count += 1
                    notification.status = "sent"
                else:
                    failed_count += 1
                    notification.retry_count += 1

                    # Mark as failed after 3 retries
                    if notification.retry_count >= 3:
                        notification.status = "failed"

                # Update notification status
                await self._update_notification_status(notification, db_session)

            return {
                "processed": len(due_notifications),
                "sent": sent_count,
                "failed": failed_count,
                "pending_retries": sum(1 for n in due_notifications if n.retry_count > 0 and n.status != "failed")
            }

        except Exception as e:
            logger.error("Notification processing failed", error=str(e))
            return {"processed": 0, "sent": 0, "failed": 0, "pending_retries": 0}

    async def _send_notification(
        self,
        notification: NotificationSchedule,
        db_session=None
    ) -> bool:
        """
        Send a deadline notification.

        Args:
            notification: Notification to send

        Returns:
            Success status
        """
        try:
            # Get task and recipient information
            task = db_session.query(Task).filter(Task.id == notification.task_id).first()
            if not task:
                return False

            # Get task assignee
            recipient = None
            if task.assigned_to:
                recipient = db_session.query(User).filter(User.id == task.assigned_to).first()

            if not recipient:
                return False

            # Generate notification message
            message = self._generate_notification_message(notification, task)

            # Send notification (in real implementation, integrate with notification service)
            success = await self._deliver_notification(recipient, message, notification.notification_type)

            if success:
                logger.info("Deadline notification sent", task_id=notification.task_id, type=notification.notification_type)
            else:
                logger.warning("Deadline notification failed", task_id=notification.task_id, type=notification.notification_type)

            return success

        except Exception as e:
            logger.error("Notification delivery failed", error=str(e), notification_id=notification.id)
            return False

    def _generate_notification_message(
        self,
        notification: NotificationSchedule,
        task: Task
    ) -> str:
        """Generate notification message based on type."""
        days_remaining = (task.planned_end_date - date.today()).days if task.planned_end_date else 0

        if "30d" in notification.notification_type:
            return f"⏰ REMINDER: Task '{task.name}' is due in 30 days ({task.planned_end_date}). Please review progress and ensure completion on schedule."
        elif "14d" in notification.notification_type:
            return f"⏰ REMINDER: Task '{task.name}' is due in 2 weeks ({task.planned_end_date}). Check progress and address any blockers."
        elif "7d" in notification.notification_type:
            return f"🚨 URGENT: Task '{task.name}' is due in 1 week ({task.planned_end_date}). Ensure all work is on track."
        elif "3d" in notification.notification_type:
            return f"🚨 CRITICAL: Task '{task.name}' is due in 3 days ({task.planned_end_date}). Immediate action required!"
        elif "1d" in notification.notification_type:
            return f"🚨 FINAL WARNING: Task '{task.name}' is due TOMORROW ({task.planned_end_date}). Complete immediately!"
        elif "0d" in notification.notification_type:
            return f"🚨 OVERDUE: Task '{task.name}' was due TODAY ({task.planned_end_date}). Immediate completion required!"
        else:
            return f"⏰ Task '{task.name}' deadline reminder: {days_remaining} days remaining."

    async def _deliver_notification(
        self,
        recipient: User,
        message: str,
        notification_type: str
    ) -> bool:
        """
        Deliver notification to recipient.

        Args:
            recipient: Notification recipient
            message: Notification message
            notification_type: Type of notification

        Returns:
            Delivery success status
        """
        try:
            # In a real implementation, this would integrate with:
            # - Email service
            # - WhatsApp messaging
            # - Push notifications
            # - In-app notifications

            # For now, simulate delivery
            print(f"[NOTIFICATION] To: {recipient.email} | Type: {notification_type} | Message: {message}")

            # Simulate occasional failures for testing
            import random
            return random.random() > 0.1  # 90% success rate

        except Exception as e:
            logger.error("Notification delivery error", error=str(e), recipient=str(recipient.id))
            return False

    async def get_upcoming_deadlines(
        self,
        project_id: Optional[UUID] = None,
        days_ahead: int = 30,
        db_session=None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming task deadlines.

        Args:
            project_id: Optional project filter
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming deadlines
        """
        try:
            # Calculate date range
            start_date = date.today()
            end_date = start_date + timedelta(days=days_ahead)

            # Query tasks with upcoming deadlines
            query = db_session.query(Task).filter(
                Task.planned_end_date >= start_date,
                Task.planned_end_date <= end_date,
                Task.status != 'completed'
            )

            if project_id:
                query = query.filter(Task.project_id == project_id)

            tasks = query.order_by(Task.planned_end_date).all()

            deadlines = []
            for task in tasks:
                days_remaining = (task.planned_end_date - start_date).days

                deadline_info = {
                    "task_id": str(task.id),
                    "task_name": task.name,
                    "project_id": str(task.project_id),
                    "deadline_date": task.planned_end_date.isoformat(),
                    "days_remaining": days_remaining,
                    "assigned_to": str(task.assigned_to) if task.assigned_to else None,
                    "progress_percentage": task.progress_percentage,
                    "priority": self._calculate_deadline_priority(days_remaining, task.progress_percentage),
                    "status": task.status
                }
                deadlines.append(deadline_info)

            return deadlines

        except Exception as e:
            logger.error("Failed to get upcoming deadlines", error=str(e))
            return []

    def _calculate_deadline_priority(self, days_remaining: int, progress_percentage: int) -> str:
        """Calculate deadline priority based on time remaining and progress."""
        if days_remaining <= 1:
            return "critical"
        elif days_remaining <= 3:
            return "high"
        elif days_remaining <= 7:
            return "medium"
        elif progress_percentage < 50 and days_remaining <= 14:
            return "medium"
        else:
            return "low"

    async def setup_escalation_workflow(
        self,
        task_id: UUID,
        escalation_rules: Dict[str, Any],
        db_session=None
    ) -> List[NotificationSchedule]:
        """
        Setup escalation workflow for a task.

        Args:
            task_id: Task identifier
            escalation_rules: Escalation configuration

        Returns:
            Scheduled escalation notifications
        """
        try:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task or not task.planned_end_date:
                return []

            escalations = []

            # Default escalation rules if not provided
            if not escalation_rules:
                escalation_rules = {
                    "overdue_1_day": {"delay_days": 1, "recipients": ["manager", "assignee"]},
                    "overdue_3_days": {"delay_days": 3, "recipients": ["manager", "team_lead", "assignee"]},
                    "overdue_7_days": {"delay_days": 7, "recipients": ["manager", "team_lead", "project_owner"]}
                }

            for escalation_key, config in escalation_rules.items():
                delay_days = config.get("delay_days", 1)
                escalation_date = task.planned_end_date + timedelta(days=delay_days)

                if escalation_date >= date.today():
                    escalation = NotificationSchedule(
                        id=f"{task_id}_escalation_{escalation_key}",
                        task_id=str(task_id),
                        notification_type=f"escalation_{escalation_key}",
                        scheduled_time=datetime.combine(escalation_date, datetime.min.time()),
                        status="pending",
                        retry_count=0
                    )
                    escalations.append(escalation)

            # Store escalation schedule
            await self._store_scheduled_notifications(escalations, db_session)

            return escalations

        except Exception as e:
            logger.error("Failed to setup escalation workflow", error=str(e), task_id=str(task_id))
            return []

    async def get_notification_history(
        self,
        task_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        days_back: int = 30,
        db_session=None
    ) -> List[Dict[str, Any]]:
        """
        Get notification history.

        Args:
            task_id: Optional task filter
            project_id: Optional project filter
            days_back: Number of days to look back

        Returns:
            Notification history
        """
        try:
            # In a real implementation, this would query notification history
            # For now, return empty list as placeholder
            return []

        except Exception as e:
            logger.error("Failed to get notification history", error=str(e))
            return []

    async def cancel_notifications(
        self,
        task_id: UUID,
        notification_types: Optional[List[str]] = None,
        db_session=None
    ) -> int:
        """
        Cancel scheduled notifications for a task.

        Args:
            task_id: Task identifier
            notification_types: Optional filter by notification types

        Returns:
            Number of cancelled notifications
        """
        try:
            # In a real implementation, this would update notification status to cancelled
            # For now, return 0 as placeholder
            return 0

        except Exception as e:
            logger.error("Failed to cancel notifications", error=str(e), task_id=str(task_id))
            return 0

    async def reschedule_notifications(
        self,
        task_id: UUID,
        new_deadline: date,
        db_session=None
    ) -> List[NotificationSchedule]:
        """
        Reschedule notifications when task deadline changes.

        Args:
            task_id: Task identifier
            new_deadline: New deadline date

        Returns:
            Rescheduled notifications
        """
        try:
            # Cancel existing notifications
            await self.cancel_notifications(task_id, db_session=db_session)

            # Update task deadline (assuming it's already updated in the task)
            # Schedule new notifications
            new_notifications = await self.schedule_deadline_notifications(task_id, db_session)

            return new_notifications

        except Exception as e:
            logger.error("Failed to reschedule notifications", error=str(e), task_id=str(task_id))
            return []

    # Placeholder methods for database operations (would be implemented in real system)

    async def _store_scheduled_notifications(
        self,
        notifications: List[NotificationSchedule],
        db_session=None
    ):
        """Store scheduled notifications in database."""
        # In a real implementation, this would save to a notifications table
        pass

    async def _get_due_notifications(
        self,
        current_time: datetime,
        db_session=None
    ) -> List[NotificationSchedule]:
        """Get notifications that are due for sending."""
        # In a real implementation, this would query due notifications
        return []

    async def _update_notification_status(
        self,
        notification: NotificationSchedule,
        db_session=None
    ):
        """Update notification status in database."""
        # In a real implementation, this would update the notification record
        pass

    async def get_deadline_summary(
        self,
        project_id: Optional[UUID] = None,
        db_session=None
    ) -> Dict[str, Any]:
        """
        Get deadline summary for monitoring.

        Args:
            project_id: Optional project filter

        Returns:
            Deadline summary statistics
        """
        try:
            upcoming = await self.get_upcoming_deadlines(project_id, 30, db_session)

            summary = {
                "total_upcoming_deadlines": len(upcoming),
                "deadlines_by_priority": {
                    "critical": len([d for d in upcoming if d["priority"] == "critical"]),
                    "high": len([d for d in upcoming if d["priority"] == "high"]),
                    "medium": len([d for d in upcoming if d["priority"] == "medium"]),
                    "low": len([d for d in upcoming if d["priority"] == "low"])
                },
                "overdue_tasks": len([d for d in upcoming if d["days_remaining"] < 0]),
                "due_today": len([d for d in upcoming if d["days_remaining"] == 0]),
                "due_this_week": len([d for d in upcoming if 0 < d["days_remaining"] <= 7]),
                "upcoming_deadlines": upcoming[:10]  # Top 10 most urgent
            }

            return summary

        except Exception as e:
            logger.error("Failed to get deadline summary", error=str(e))
            return {
                "total_upcoming_deadlines": 0,
                "deadlines_by_priority": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "overdue_tasks": 0,
                "due_today": 0,
                "due_this_week": 0,
                "upcoming_deadlines": []
            }
