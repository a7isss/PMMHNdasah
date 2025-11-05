"""
Security utilities for WhatsApp PM System v3.0 (Gamma)
Password hashing, JWT tokens, and cryptographic functions
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from ..config import settings
from ..database import get_db
from ..models.sqlalchemy.user import User
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("Failed to decode JWT token", error=str(e))
        raise


def create_password_reset_token(email: str) -> str:
    """Create a password reset token."""
    expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset"
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_password_reset_token(token: str) -> dict:
    """Decode and validate a password reset token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != "password_reset":
            raise JWTError("Invalid token type")

        return payload
    except JWTError as e:
        logger.warning("Failed to decode password reset token", error=str(e))
        raise


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """Hash sensitive data using bcrypt (not for passwords)."""
    if salt:
        # Use salt for deterministic hashing
        salted_data = f"{data}{salt}"
        return pwd_context.hash(salted_data, scheme="bcrypt")
    else:
        # Use random salt for one-way hashing
        return pwd_context.hash(data, scheme="bcrypt")


def verify_sensitive_data(data: str, hashed_data: str, salt: Optional[str] = None) -> bool:
    """Verify sensitive data against its hash."""
    if salt:
        salted_data = f"{data}{salt}"
        return pwd_context.verify(salted_data, hashed_data)
    else:
        return pwd_context.verify(data, hashed_data)


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"gamma_{secrets.token_urlsafe(32)}"


def validate_api_key(api_key: str) -> bool:
    """Validate an API key format."""
    return api_key.startswith("gamma_") and len(api_key) == 40  # "gamma_" + 32 chars


def create_tenant_secret() -> str:
    """Create a tenant-specific secret for encryption."""
    return secrets.token_hex(32)


def encrypt_tenant_data(data: str, tenant_secret: str) -> str:
    """Encrypt tenant-specific data."""
    # Simple XOR encryption with tenant secret (for demonstration)
    # In production, use proper encryption like Fernet
    key = tenant_secret[:len(data)] if len(tenant_secret) >= len(data) else tenant_secret * (len(data) // len(tenant_secret) + 1)
    key = key[:len(data)]

    encrypted = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, key))
    return encrypted


def decrypt_tenant_data(encrypted_data: str, tenant_secret: str) -> str:
    """Decrypt tenant-specific data."""
    # Same XOR decryption
    return encrypt_tenant_data(encrypted_data, tenant_secret)  # XOR is symmetric


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return text

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
    sanitized = text

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized.strip()


def validate_email_domain(email: str, allowed_domains: Optional[list] = None) -> bool:
    """Validate email domain against allowed list."""
    if not allowed_domains:
        return True

    try:
        domain = email.split('@')[1].lower()
        return domain in [d.lower() for d in allowed_domains]
    except IndexError:
        return False


def check_password_strength(password: str) -> dict:
    """Check password strength and return requirements."""
    requirements = {
        "length": len(password) >= 8,
        "uppercase": any(char.isupper() for char in password),
        "lowercase": any(char.islower() for char in password),
        "digit": any(char.isdigit() for char in password),
        "special": any(not char.isalnum() for char in password)
    }

    requirements["overall"] = all(requirements.values())
    return requirements


def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes for 2FA."""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def validate_backup_code(code: str, stored_codes: list[str]) -> tuple[bool, list[str]]:
    """Validate a backup code and return updated list."""
    if code.upper() in stored_codes:
        # Remove used code
        updated_codes = [c for c in stored_codes if c != code.upper()]
        return True, updated_codes

    return False, stored_codes


def create_session_fingerprint(request) -> str:
    """Create a session fingerprint for security."""
    fingerprint_data = [
        request.client.host,
        request.headers.get("user-agent", ""),
        request.headers.get("accept-language", ""),
    ]

    fingerprint_string = "|".join(fingerprint_data)
    return hash_sensitive_data(fingerprint_string)


# FastAPI Security Scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Extract token
        token = credentials.credentials

        # Decode token
        payload = decode_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        from uuid import UUID
        user = await db.get(User, UUID(user_id))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
