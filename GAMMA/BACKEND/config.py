"""
Configuration settings for WhatsApp PM System v3.0 (Gamma)
Environment-based configuration with validation
"""

import os
import secrets
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "WhatsApp PM API - Gamma v3.0"
    VERSION: str = "3.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://app.whatsapppm.com",
        "https://*.whatsapppm.com"
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/whatsapp_pm"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Authentication
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # WhatsApp Integration
    WHATSAPP_API_VERSION: str = "v18.0"
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = secrets.token_urlsafe(16)
    WHATSAPP_WEBHOOK_URL: str = ""

    # AI Services
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    # AI Configuration
    AI_INTENT_CONFIDENCE_THRESHOLD: float = 0.8
    AI_SENTIMENT_CONFIDENCE_THRESHOLD: float = 0.7
    AI_URGENCY_CONFIDENCE_THRESHOLD: float = 0.75
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.1

    # Redis/Caching
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 300
    CACHE_MAX_MEMORY_MB: int = 100

    # Email
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@whatsapppm.com"

    # File Storage
    UPLOAD_MAX_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg"]

    # Monitoring
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True

    # Security
    BCRYPT_ROUNDS: int = 12
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    WEATHER_API_KEY: str = ""

    # Feature Flags
    ENABLE_AI_FEATURES: bool = True
    ENABLE_WHATSAPP_INTEGRATION: bool = True
    ENABLE_REAL_TIME_FEATURES: bool = True
    ENABLE_OFFLINE_MODE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from comma-separated string or list."""
        if isinstance(v, str):
            return [ftype.strip() for ftype in v.split(",")]
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")
        return v

    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        """Ensure JWT secret is sufficiently long."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    def get_database_config(self) -> dict:
        """Get database configuration for SQLAlchemy."""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DEBUG,
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20,
        }

    def get_redis_config(self) -> dict:
        """Get Redis configuration."""
        return {
            "url": self.REDIS_URL,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        }

    def get_ai_config(self) -> dict:
        """Get AI service configuration."""
        return {
            "openai_api_key": self.OPENAI_API_KEY,
            "openai_model": self.OPENAI_MODEL,
            "anthropic_api_key": self.ANTHROPIC_API_KEY,
            "anthropic_model": self.ANTHROPIC_MODEL,
            "intent_threshold": self.AI_INTENT_CONFIDENCE_THRESHOLD,
            "sentiment_threshold": self.AI_SENTIMENT_CONFIDENCE_THRESHOLD,
            "urgency_threshold": self.AI_URGENCY_CONFIDENCE_THRESHOLD,
            "max_tokens": self.AI_MAX_TOKENS,
            "temperature": self.AI_TEMPERATURE,
        }

    def get_whatsapp_config(self) -> dict:
        """Get WhatsApp integration configuration."""
        return {
            "api_version": self.WHATSAPP_API_VERSION,
            "access_token": self.WHATSAPP_ACCESS_TOKEN,
            "phone_number_id": self.WHATSAPP_PHONE_NUMBER_ID,
            "verify_token": self.WHATSAPP_VERIFY_TOKEN,
            "webhook_url": self.WHATSAPP_WEBHOOK_URL,
        }

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return not self.DEBUG and os.getenv("ENVIRONMENT") == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.DEBUG or os.getenv("ENVIRONMENT") in ("development", "dev", None)


# Global settings instance
settings = Settings()
