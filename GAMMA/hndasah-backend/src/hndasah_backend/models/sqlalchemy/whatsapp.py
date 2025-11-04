"""
SQLAlchemy models for WhatsApp integration in WhatsApp PM System v3.0 (Gamma)
WhatsApp contacts, messages, and AI processing
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import uuid4
import structlog
from sqlalchemy import Column, String, DateTime, Date, Text, Integer, Boolean, DECIMAL, func, text, ForeignKey, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from ...database import Base
from ...schemas.base import BaseModel

logger = structlog.get_logger(__name__)


class WhatsAppContact(BaseModel):
    """WhatsApp contact model for managing business contacts."""

    __tablename__ = "whatsapp_contacts"

    # Basic Information
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    whatsapp_number: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    company: Mapped[Optional[str]] = mapped_column(String(255))
    contact_type: Mapped[str] = mapped_column(String(50), nullable=False, default="client")

    # Profile
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    # Relationship
    projects: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Communication Preferences
    notification_settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=lambda: {
        "updates": True,
        "alerts": True,
        "reports": False
    })

    # AI Integration
    ai_personality_profile: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    ai_communication_history: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSONB, nullable=True)  # Vector embeddings stored as JSONB for now

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    messages: Mapped[List["WhatsAppMessage"]] = relationship(
        "WhatsAppMessage",
        back_populates="contact",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        text("CHECK (contact_type IN ('client', 'contractor', 'supplier', 'team_member', 'other'))"),
        text("UNIQUE (tenant_id, whatsapp_number)"),
    )

    def get_message_count_by_type(self, message_type: str = None) -> int:
        """Get message count by type."""
        if not self.messages:
            return 0

        if message_type:
            return sum(1 for msg in self.messages if msg.message_type == message_type)
        return len(self.messages)

    def get_last_message_at(self) -> Optional[datetime]:
        """Get timestamp of last message."""
        if not self.messages:
            return None
        return max(msg.created_at for msg in self.messages)

    def get_response_time_avg(self) -> Optional[float]:
        """Calculate average response time in minutes."""
        inbound_messages = [msg for msg in self.messages if msg.direction == 'inbound']
        if not inbound_messages:
            return None

        response_times = []
        for inbound in inbound_messages:
            # Find next outbound message after this inbound
            outbound_after = [
                msg for msg in self.messages
                if msg.direction == 'outbound' and msg.created_at > inbound.created_at
            ]
            if outbound_after:
                next_outbound = min(outbound_after, key=lambda x: x.created_at)
                response_time = (next_outbound.created_at - inbound.created_at).total_seconds() / 60
                response_times.append(response_time)

        return sum(response_times) / len(response_times) if response_times else None

    def get_communication_patterns(self) -> Dict[str, Any]:
        """Analyze communication patterns."""
        if not self.messages:
            return {}

        total_messages = len(self.messages)
        inbound_count = sum(1 for msg in self.messages if msg.direction == 'inbound')
        outbound_count = total_messages - inbound_count

        # Message types breakdown
        type_breakdown = {}
        for msg in self.messages:
            msg_type = msg.message_type or 'text'
            type_breakdown[msg_type] = type_breakdown.get(msg_type, 0) + 1

        # Sentiment analysis (if available)
        sentiment_scores = [msg.sentiment_score for msg in self.messages if msg.sentiment_score is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else None

        return {
            "total_messages": total_messages,
            "inbound_messages": inbound_count,
            "outbound_messages": outbound_count,
            "message_types": type_breakdown,
            "average_sentiment": avg_sentiment,
            "response_time_avg": self.get_response_time_avg()
        }


class WhatsAppMessage(BaseModel):
    """WhatsApp message model with AI processing capabilities."""

    __tablename__ = "whatsapp_messages"

    # Message Content
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("whatsapp_contacts.id"), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    content: Mapped[Optional[str]] = mapped_column(Text)
    whatsapp_message_id: Mapped[Optional[str]] = mapped_column(String(255))

    # WhatsApp Specific
    media_urls: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    media_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    whatsapp_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # AI Analysis Results
    ai_processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    intent_classification: Mapped[Optional[str]] = mapped_column(String(100))
    sentiment_score: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(3, 2))
    urgency_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    extracted_entities: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    confidence_score: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(3, 2))

    # Context Linking
    related_task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id"))
    related_cost_item_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cost_items.id"))
    conversation_context: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Response
    auto_response_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    response_content: Mapped[Optional[str]] = mapped_column(Text)
    response_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Delivery & Status
    delivery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="sent")
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    embedding: Mapped[Optional[List[float]]] = mapped_column(JSONB, nullable=True)  # Vector embeddings stored as JSONB for now

    # Relationships
    contact: Mapped["WhatsAppContact"] = relationship("WhatsAppContact", back_populates="messages")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="whatsapp_messages")
    related_task: Mapped[Optional["Task"]] = relationship("Task")
    related_cost_item: Mapped[Optional["CostItem"]] = relationship("CostItem")

    # Constraints
    __table_args__ = (
        text("CHECK (direction IN ('inbound', 'outbound'))"),
        text("CHECK (message_type IN ('text', 'image', 'video', 'audio', 'document', 'location', 'contact'))"),
        text("CHECK (urgency_level IN ('low', 'medium', 'high', 'critical'))"),
        text("CHECK (delivery_status IN ('sent', 'delivered', 'read', 'failed'))"),
        CheckConstraint("sentiment_score >= -1 AND sentiment_score <= 1 OR sentiment_score IS NULL"),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1 OR confidence_score IS NULL"),
    )

    def get_message_length(self) -> int:
        """Get message content length."""
        return len(self.content or "")

    def is_media_message(self) -> bool:
        """Check if message contains media."""
        return self.message_type in ['image', 'video', 'audio', 'document']

    def get_processing_status(self) -> Dict[str, Any]:
        """Get AI processing status."""
        return {
            "processed": self.ai_processed,
            "intent": self.intent_classification,
            "sentiment": float(self.sentiment_score) if self.sentiment_score else None,
            "urgency": self.urgency_level,
            "confidence": float(self.confidence_score) if self.confidence_score else None,
            "entities_found": len(self.extracted_entities) if self.extracted_entities else 0
        }

    def requires_response(self) -> bool:
        """Check if message requires a response based on AI analysis."""
        if not self.ai_processed:
            return True  # Default to requiring response if not processed

        # High urgency messages always require response
        if self.urgency_level in ['high', 'critical']:
            return True

        # Questions or requests typically require response
        if self.intent_classification in ['question', 'request', 'complaint', 'inquiry']:
            return True

        # Negative sentiment might require response
        if self.sentiment_score and self.sentiment_score < -0.3:
            return True

        return False

    def get_conversation_thread(self, limit: int = 10) -> List["WhatsAppMessage"]:
        """Get conversation thread around this message."""
        # This would need to be implemented with a query
        # For now, return empty list
        return []


class WhatsAppAutoResponse(BaseModel):
    """WhatsApp auto-response rules model."""

    __tablename__ = "whatsapp_auto_responses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    response_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Constraints
    __table_args__ = (
        CheckConstraint("priority >= 1"),
        CheckConstraint("usage_count >= 0"),
    )

    def matches_message(self, message: WhatsAppMessage) -> bool:
        """Check if this rule matches a message."""
        # Simple condition matching - can be extended
        for key, value in self.conditions.items():
            if key == 'intent' and message.intent_classification != value:
                return False
            elif key == 'urgency' and message.urgency_level != value:
                return False
            elif key == 'sentiment_min' and (not message.sentiment_score or message.sentiment_score < value):
                return False
            elif key == 'sentiment_max' and (not message.sentiment_score or message.sentiment_score > value):
                return False
            elif key == 'keywords':
                content = (message.content or "").lower()
                if not any(keyword.lower() in content for keyword in value):
                    return False

        return True

    def generate_response(self, message: WhatsAppMessage) -> str:
        """Generate response using template."""
        # Simple template replacement - can be extended
        response = self.response_template

        # Replace placeholders
        if message.contact and message.contact.name:
            response = response.replace("{name}", message.contact.name)
        if message.contact and message.contact.company:
            response = response.replace("{company}", message.contact.company)

        return response


class WhatsAppIntegrationSettings(BaseModel):
    """WhatsApp integration settings model."""

    __tablename__ = "whatsapp_integration_settings"

    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False, unique=True)
    api_token: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number_id: Mapped[str] = mapped_column(String(50), nullable=False)
    business_account_id: Mapped[str] = mapped_column(String(50), nullable=False)
    webhook_verify_token: Mapped[str] = mapped_column(String(255), nullable=False)
    auto_responses_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ai_processing_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    working_hours: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    rate_limits: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    notification_settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_webhook_received: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    webhook_failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class WhatsAppMessageTemplate(BaseModel):
    """WhatsApp message template model."""

    __tablename__ = "whatsapp_message_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Constraints
    __table_args__ = (
        text("CHECK (approval_status IN ('draft', 'submitted', 'approved', 'rejected'))"),
        CheckConstraint("usage_count >= 0"),
    )

    def validate_variables(self, provided_vars: Dict[str, Any]) -> List[str]:
        """Validate that all required variables are provided."""
        missing_vars = []
        for var in self.variables:
            if var not in provided_vars:
                missing_vars.append(var)
        return missing_vars

    def render_template(self, variables: Dict[str, Any]) -> str:
        """Render template with provided variables."""
        content = self.content
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            content = content.replace(placeholder, str(var_value))
        return content


class WhatsAppConversation(BaseModel):
    """WhatsApp conversation thread model."""

    __tablename__ = "whatsapp_conversations"

    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("whatsapp_contacts.id"), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    assigned_to: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"))
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # AI Analysis
    sentiment_trend: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(3, 2))
    urgency_trend: Mapped[Optional[str]] = mapped_column(String(20))
    topic_clusters: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Constraints
    __table_args__ = (
        text("CHECK (status IN ('active', 'closed', 'archived'))"),
        text("CHECK (priority IN ('low', 'normal', 'high', 'urgent'))"),
        CheckConstraint("sentiment_trend >= -1 AND sentiment_trend <= 1 OR sentiment_trend IS NULL"),
    )

    def get_duration_hours(self) -> float:
        """Get conversation duration in hours."""
        # This would need to be calculated from first and last messages
        # For now, return a placeholder
        return 0.0

    def get_participants_count(self) -> int:
        """Get number of participants in conversation."""
        # For WhatsApp, this is typically 2 (contact + business)
        return 2

    def requires_attention(self) -> bool:
        """Check if conversation requires attention."""
        if self.status != 'active':
            return False

        # High priority always requires attention
        if self.priority in ['high', 'urgent']:
            return True

        # Recent messages without response
        if self.last_message_at:
            hours_since_last = (datetime.utcnow() - self.last_message_at).total_seconds() / 3600
            if hours_since_last > 24:  # No response for 24+ hours
                return True

        return False


class WhatsAppWebhookLog(BaseModel):
    """WhatsApp webhook processing log."""

    __tablename__ = "whatsapp_webhook_logs"

    webhook_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="received")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    messages_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Constraints
    __table_args__ = (
        text("CHECK (processing_status IN ('received', 'processing', 'completed', 'failed'))"),
        CheckConstraint("processing_time_ms >= 0 OR processing_time_ms IS NULL"),
        CheckConstraint("messages_processed >= 0"),
    )



