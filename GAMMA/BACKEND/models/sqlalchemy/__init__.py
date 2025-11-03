"""
SQLAlchemy models for WhatsApp PM System v3.0 (Gamma)
Database models with relationships and business logic
"""

from .project import Project, ProjectMember
from .task import Task, TaskComment, TaskDependency, TaskTemplate
from .cost import CostItem, BillOfQuantities, CostComment, CostApprovalWorkflow, VendorContract, CostTemplate
from .whatsapp import (
    WhatsAppContact, WhatsAppMessage, WhatsAppAutoResponse,
    WhatsAppIntegrationSettings, WhatsAppMessageTemplate,
    WhatsAppConversation, WhatsAppWebhookLog
)

__all__ = [
    # Project models
    "Project",
    "ProjectMember",

    # Task models
    "Task",
    "TaskComment",
    "TaskDependency",
    "TaskTemplate",

    # Cost models
    "CostItem",
    "BillOfQuantities",
    "CostComment",
    "CostApprovalWorkflow",
    "VendorContract",
    "CostTemplate",

    # WhatsApp models
    "WhatsAppContact",
    "WhatsAppMessage",
    "WhatsAppAutoResponse",
    "WhatsAppIntegrationSettings",
    "WhatsAppMessageTemplate",
    "WhatsAppConversation",
    "WhatsAppWebhookLog",
]
