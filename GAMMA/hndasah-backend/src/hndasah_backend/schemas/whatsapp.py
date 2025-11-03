"""
WhatsApp-related Pydantic models for WhatsApp PM System v3.0 (Gamma)
WhatsApp integration, messaging, and contact models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, UUID
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class WhatsAppContactBase(BaseModel):
    """Base WhatsApp contact model with common fields."""
    whatsapp_number: str = Field(..., description="WhatsApp phone number")
    name: Optional[str] = Field(None, max_length=255, description="Contact name")
    company: Optional[str] = Field(None, max_length=255, description="Company name")
    contact_type: str = Field("client", description="Type of contact")

    @validator('whatsapp_number')
    def validate_whatsapp_number(cls, v):
        """Validate WhatsApp number format."""
        if v:
            # Remove all non-digit characters
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError("WhatsApp number must be 10-15 digits")
            return digits_only
        return v

    @validator('contact_type')
    def validate_contact_type(cls, v):
        """Validate contact type."""
        valid_types = ['client', 'contractor', 'supplier', 'team_member', 'other']
        if v not in valid_types:
            raise ValueError(f"Contact type must be one of: {', '.join(valid_types)}")
        return v


class WhatsAppContactCreate(WhatsAppContactBase):
    """Model for creating new WhatsApp contacts."""
    tenant_id: UUID = Field(..., description="Tenant ID")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    location: Optional[str] = Field(None, max_length=255, description="Contact location")
    language: str = Field("en", max_length=10, description="Preferred language")
    projects: Optional[List[UUID]] = Field(default_factory=list, description="Associated project IDs")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification preferences")


class WhatsAppContactUpdate(BaseModel):
    """Model for updating existing WhatsApp contacts."""
    name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    contact_type: Optional[str] = Field(None)
    avatar_url: Optional[str] = Field(None)
    location: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field(None, max_length=10)
    projects: Optional[List[UUID]] = Field(None)
    notification_settings: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None, description="Whether contact is active")

    @validator('contact_type')
    def validate_contact_type(cls, v):
        """Validate contact type."""
        if v is not None:
            valid_types = ['client', 'contractor', 'supplier', 'team_member', 'other']
            if v not in valid_types:
                raise ValueError(f"Contact type must be one of: {', '.join(valid_types)}")
        return v


class WhatsAppContactResponse(WhatsAppContactBase):
    """Response model for WhatsApp contact data."""
    id: UUID
    tenant_id: UUID
    avatar_url: Optional[str]
    location: Optional[str]
    language: str
    projects: List[UUID]
    notification_settings: Dict[str, Any]
    ai_personality_profile: Dict[str, Any]
    ai_communication_history: List[Dict[str, Any]]
    is_active: bool
    last_contacted_at: Optional[datetime]
    message_count: int
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WhatsAppMessageBase(BaseModel):
    """Base WhatsApp message model with common fields."""
    direction: str = Field(..., description="Message direction")
    message_type: str = Field("text", description="Type of message")
    content: Optional[str] = Field(None, description="Message content")
    whatsapp_message_id: Optional[str] = Field(None, max_length=255, description="WhatsApp message ID")

    @validator('direction')
    def validate_direction(cls, v):
        """Validate message direction."""
        valid_directions = ['inbound', 'outbound']
        if v not in valid_directions:
            raise ValueError(f"Direction must be one of: {', '.join(valid_directions)}")
        return v

    @validator('message_type')
    def validate_message_type(cls, v):
        """Validate message type."""
        valid_types = ['text', 'image', 'video', 'audio', 'document', 'location', 'contact']
        if v not in valid_types:
            raise ValueError(f"Message type must be one of: {', '.join(valid_types)}")
        return v


class WhatsAppMessageCreate(WhatsAppMessageBase):
    """Model for creating new WhatsApp messages."""
    contact_id: UUID = Field(..., description="Contact ID")
    project_id: Optional[UUID] = Field(None, description="Associated project ID")
    media_urls: Optional[List[str]] = Field(default_factory=list, description="Media URLs")
    media_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Media metadata")


class WhatsAppMessageUpdate(BaseModel):
    """Model for updating existing WhatsApp messages."""
    intent_classification: Optional[str] = Field(None, max_length=100)
    sentiment_score: Optional[Decimal] = Field(None, ge=-1, le=1)
    urgency_level: Optional[str] = Field(None)
    extracted_entities: Optional[Dict[str, Any]] = Field(None)
    related_task_id: Optional[UUID] = Field(None)
    related_cost_item_id: Optional[UUID] = Field(None)
    conversation_context: Optional[Dict[str, Any]] = Field(None)
    delivery_status: Optional[str] = Field(None)

    @validator('urgency_level')
    def validate_urgency_level(cls, v):
        """Validate urgency level."""
        if v is not None:
            valid_levels = ['low', 'medium', 'high', 'critical']
            if v not in valid_levels:
                raise ValueError(f"Urgency level must be one of: {', '.join(valid_levels)}")
        return v

    @validator('delivery_status')
    def validate_delivery_status(cls, v):
        """Validate delivery status."""
        if v is not None:
            valid_statuses = ['sent', 'delivered', 'read', 'failed']
            if v not in valid_statuses:
                raise ValueError(f"Delivery status must be one of: {', '.join(valid_statuses)}")
        return v


class WhatsAppMessageResponse(WhatsAppMessageBase):
    """Response model for WhatsApp message data."""
    id: UUID
    contact_id: UUID
    project_id: Optional[UUID]
    media_urls: List[str]
    media_metadata: Dict[str, Any]
    whatsapp_timestamp: Optional[datetime]
    ai_processed: bool
    intent_classification: Optional[str]
    sentiment_score: Optional[Decimal]
    urgency_level: Optional[str]
    extracted_entities: Dict[str, Any]
    confidence_score: Optional[Decimal]
    related_task_id: Optional[UUID]
    related_cost_item_id: Optional[UUID]
    conversation_context: Dict[str, Any]
    auto_response_sent: bool
    response_content: Optional[str]
    response_timestamp: Optional[datetime]
    delivery_status: str
    read_at: Optional[datetime]
    error_message: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class WhatsAppWebhookPayload(BaseModel):
    """Model for incoming WhatsApp webhook payloads."""
    object: str = Field(..., description="Webhook object type")
    entry: List[Dict[str, Any]] = Field(..., description="Webhook entries")
    messaging_product: Optional[str] = Field(None, description="Messaging product")


class WhatsAppWebhookMessage(BaseModel):
    """Model for individual WhatsApp webhook messages."""
    id: str = Field(..., description="Message ID")
    from_: str = Field(..., alias="from", description="Sender phone number")
    timestamp: str = Field(..., description="Message timestamp")
    type: str = Field(..., description="Message type")
    text: Optional[Dict[str, Any]] = Field(None, description="Text message content")
    image: Optional[Dict[str, Any]] = Field(None, description="Image message content")
    document: Optional[Dict[str, Any]] = Field(None, description="Document message content")
    audio: Optional[Dict[str, Any]] = Field(None, description="Audio message content")
    video: Optional[Dict[str, Any]] = Field(None, description="Video message content")
    location: Optional[Dict[str, Any]] = Field(None, description="Location message content")
    contacts: Optional[List[Dict[str, Any]]] = Field(None, description="Contact message content")


class WhatsAppOutgoingMessage(BaseModel):
    """Model for sending WhatsApp messages."""
    to: str = Field(..., description="Recipient phone number")
    type: str = Field("text", description="Message type")
    text: Optional[Dict[str, str]] = Field(None, description="Text message content")
    image: Optional[Dict[str, Any]] = Field(None, description="Image message content")
    document: Optional[Dict[str, Any]] = Field(None, description="Document message content")
    audio: Optional[Dict[str, Any]] = Field(None, description="Audio message content")
    video: Optional[Dict[str, Any]] = Field(None, description="Video message content")
    location: Optional[Dict[str, Any]] = Field(None, description="Location message content")
    contacts: Optional[List[Dict[str, Any]]] = Field(None, description="Contact message content")

    @validator('to')
    def validate_recipient(cls, v):
        """Validate recipient phone number."""
        if v:
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError("Recipient number must be 10-15 digits")
            return digits_only
        return v

    @validator('type')
    def validate_message_type(cls, v):
        """Validate message type."""
        valid_types = ['text', 'image', 'video', 'audio', 'document', 'location', 'contact']
        if v not in valid_types:
            raise ValueError(f"Message type must be one of: {', '.join(valid_types)}")
        return v


class WhatsAppTemplateMessage(BaseModel):
    """Model for sending WhatsApp template messages."""
    to: str = Field(..., description="Recipient phone number")
    template: Dict[str, Any] = Field(..., description="Template configuration")
    language: Dict[str, str] = Field(..., description="Language configuration")


class WhatsAppContactSearchFilters(BaseModel):
    """Filters for WhatsApp contact search and listing."""
    tenant_id: Optional[UUID] = Field(None)
    contact_type: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    whatsapp_number: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    company: Optional[str] = Field(None)
    projects: Optional[List[UUID]] = Field(None)
    last_contacted_from: Optional[datetime] = Field(None)
    last_contacted_to: Optional[datetime] = Field(None)
    search_query: Optional[str] = Field(None, description="Full-text search query")


class WhatsAppMessageSearchFilters(BaseModel):
    """Filters for WhatsApp message search and listing."""
    contact_id: Optional[UUID] = Field(None)
    project_id: Optional[UUID] = Field(None)
    direction: Optional[str] = Field(None)
    message_type: Optional[str] = Field(None)
    intent_classification: Optional[str] = Field(None)
    urgency_level: Optional[str] = Field(None)
    sentiment_score_min: Optional[Decimal] = Field(None, ge=-1, le=1)
    sentiment_score_max: Optional[Decimal] = Field(None, ge=-1, le=1)
    ai_processed: Optional[bool] = Field(None)
    delivery_status: Optional[str] = Field(None)
    created_from: Optional[datetime] = Field(None)
    created_to: Optional[datetime] = Field(None)
    search_query: Optional[str] = Field(None, description="Full-text search query")


class WhatsAppStats(BaseModel):
    """WhatsApp integration statistics."""
    total_contacts: int
    active_contacts: int
    total_messages: int
    messages_today: int
    ai_processed_messages: int
    average_response_time: Optional[float]  # in minutes
    message_types_breakdown: Dict[str, int]
    intent_classification_breakdown: Dict[str, int]
    sentiment_distribution: Dict[str, int]
    top_contacted_projects: List[Dict[str, Any]]


class WhatsAppConversation(BaseModel):
    """Model representing a WhatsApp conversation thread."""
    contact_id: UUID
    project_id: Optional[UUID]
    last_message_at: datetime
    message_count: int
    ai_summary: Optional[str]
    status: str  # 'active', 'closed', 'archived'
    priority: str  # 'low', 'medium', 'high', 'urgent'
    assigned_to: Optional[UUID]
    tags: List[str]

    @validator('status')
    def validate_status(cls, v):
        """Validate conversation status."""
        valid_statuses = ['active', 'closed', 'archived']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @validator('priority')
    def validate_priority(cls, v):
        """Validate conversation priority."""
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v


class WhatsAppAutoResponse(BaseModel):
    """Model for WhatsApp auto-response rules."""
    name: str = Field(..., description="Rule name")
    tenant_id: UUID = Field(..., description="Tenant ID")
    conditions: Dict[str, Any] = Field(..., description="Trigger conditions")
    response_template: str = Field(..., description="Response template")
    is_active: bool = Field(True, description="Whether rule is active")
    priority: int = Field(1, description="Rule priority (higher = more important)")
    usage_count: int = Field(0, description="Times this rule has been triggered")


class WhatsAppIntegrationSettings(BaseModel):
    """Model for WhatsApp integration settings."""
    tenant_id: UUID
    api_token: str
    phone_number_id: str
    business_account_id: str
    webhook_verify_token: str
    auto_responses_enabled: bool = True
    ai_processing_enabled: bool = True
    working_hours: Dict[str, Any] = Field(default_factory=dict)
    rate_limits: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, Any] = Field(default_factory=dict)


class WhatsAppMessageTemplate(BaseModel):
    """Model for WhatsApp message templates."""
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category")
    language: str = Field("en", description="Template language")
    content: str = Field(..., description="Template content")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    approval_status: str = Field("draft", description="Template approval status")
    usage_count: int = Field(0, description="Times template has been used")

    @validator('approval_status')
    def validate_approval_status(cls, v):
        """Validate approval status."""
        valid_statuses = ['draft', 'submitted', 'approved', 'rejected']
        if v not in valid_statuses:
            raise ValueError(f"Approval status must be one of: {', '.join(valid_statuses)}")
        return v


class WhatsAppBulkMessage(BaseModel):
    """Model for sending bulk WhatsApp messages."""
    contact_ids: List[UUID] = Field(..., description="Recipient contact IDs")
    message_template: str = Field(..., description="Message template")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Template variables")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    priority: str = Field("normal", description="Message priority")

    @validator('priority')
    def validate_priority(cls, v):
        """Validate message priority."""
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v


class WhatsAppWebhookVerification(BaseModel):
    """Model for WhatsApp webhook verification."""
    mode: str = Field(..., description="Verification mode")
    challenge: str = Field(..., description="Verification challenge")
    verify_token: str = Field(..., description="Verify token")


class WhatsAppAPIError(BaseModel):
    """Model for WhatsApp API errors."""
    error: Dict[str, Any] = Field(..., description="Error details")
    message_id: Optional[str] = Field(None, description="Related message ID")
    contact_id: Optional[UUID] = Field(None, description="Related contact ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
