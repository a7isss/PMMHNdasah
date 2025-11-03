"""
Pydantic models for WhatsApp PM System v3.0 (Gamma)
API request/response models with validation
"""

from .user import *
from .project import *
from .task import *
from .cost import *
from .whatsapp import *
from .ai import *

__all__ = [
    # User models
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",

    # Project models
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectDetailResponse",

    # Task models
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",

    # Cost models
    "CostItemCreate",
    "CostItemUpdate",
    "CostItemResponse",

    # WhatsApp models
    "WhatsAppMessageCreate",
    "WhatsAppMessageResponse",
    "SendMessageRequest",
    "WhatsAppContactResponse",

    # AI models
    "AIMessageAnalysisRequest",
    "AIAnalysisResponse",
    "AIResponseSuggestion",
    "AIInsightsResponse",
]
