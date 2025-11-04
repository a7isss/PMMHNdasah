"""
User-related Pydantic models for WhatsApp PM System v3.0 (Gamma)
Authentication and user management models
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")
    phone: Optional[str] = Field(None, max_length=50, description="User phone number")
    job_title: Optional[str] = Field(None, max_length=100, description="User job title")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        """Validate name fields."""
        if v and len(v.strip()) == 0:
            raise ValueError("Name cannot be empty string")
        return v.strip() if v else v


class UserCreate(UserBase):
    """Model for creating new users."""
    password: str = Field(..., min_length=8, description="User password")
    role: str = Field("member", description="User role in the system")
    whatsapp_number: Optional[str] = Field(None, description="WhatsApp number for integration")

    @validator('role')
    def validate_role(cls, v):
        """Validate user role."""
        valid_roles = ['super_admin', 'admin', 'manager', 'member', 'viewer']
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v

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


class UserUpdate(BaseModel):
    """Model for updating existing users."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None)
    role: Optional[str] = Field(None)
    whatsapp_number: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None, description="Whether user is active")

    @validator('role')
    def validate_role(cls, v):
        """Validate user role."""
        if v is not None:
            valid_roles = ['super_admin', 'admin', 'manager', 'member', 'viewer']
            if v not in valid_roles:
                raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v

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


class UserResponse(UserBase):
    """Response model for user data."""
    id: UUID
    tenant_id: UUID
    role: str
    whatsapp_number: Optional[str]
    whatsapp_verified: bool
    is_active: bool
    is_email_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Model for user login requests."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class PasswordResetRequest(BaseModel):
    """Model for password reset requests."""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Model for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserPreferences(BaseModel):
    """Model for user preferences."""
    theme: str = Field("light", description="UI theme preference")
    notifications: dict = Field({
        "email": True,
        "whatsapp": True,
        "push": True
    }, description="Notification preferences")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Preferred timezone")


class AIProfile(BaseModel):
    """Model for user's AI personalization profile."""
    communication_style: str = Field("professional", description="Preferred communication style")
    response_preferences: dict = Field({
        "detail_level": "balanced",
        "urgency_sensitivity": "medium"
    }, description="AI response preferences")
    learning_data: List[dict] = Field(default_factory=list, description="User interaction learning data")


class TenantCreate(BaseModel):
    """Model for creating new tenants."""
    name: str = Field(..., min_length=2, max_length=255, description="Tenant name")
    domain: Optional[str] = Field(None, description="Custom domain for tenant")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    subscription_plan: str = Field("starter", description="Subscription plan")

    @validator('subscription_plan')
    def validate_subscription_plan(cls, v):
        """Validate subscription plan."""
        valid_plans = ['free', 'starter', 'professional', 'enterprise']
        if v not in valid_plans:
            raise ValueError(f"Subscription plan must be one of: {', '.join(valid_plans)}")
        return v


class TenantResponse(BaseModel):
    """Response model for tenant data."""
    id: UUID
    name: str
    domain: Optional[str]
    subscription_plan: str
    is_active: bool
    contact_email: Optional[str]
    contact_phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserTenantInfo(BaseModel):
    """Model containing user and tenant information."""
    user: UserResponse
    tenant: TenantResponse
    permissions: List[str] = Field(..., description="User permissions")
    features: List[str] = Field(..., description="Enabled features for tenant")

