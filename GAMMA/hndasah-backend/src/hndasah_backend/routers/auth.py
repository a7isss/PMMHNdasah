"""
Authentication router for WhatsApp PM System v3.0 (Gamma)
JWT-based authentication with multi-tenant support
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import structlog

from config import settings
from ..database import get_db
from ..models.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin,
    TokenResponse, PasswordResetRequest, PasswordResetConfirm,
    TenantCreate, TenantResponse
)
from ..schemas.user import User, Tenant
from ..services.auth_service import AuthService
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..utils.email import send_password_reset_email

logger = structlog.get_logger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Initialize auth service
auth_service = AuthService()

# Create router
router = APIRouter()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate token
        payload = auth_service.decode_token(token)
        email: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")

        if email is None or tenant_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Get user from database
    result = await db.execute(
        select(User).where(
            User.email == email,
            User.tenant_id == tenant_id,
            User.is_active == True
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they have admin privileges."""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_super_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they have super admin privileges."""
    if current_user.role != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.

    - **username**: User email address
    - **password**: User password
    """
    logger.info("Login attempt", email=form_data.username)

    # Authenticate user
    user = await auth_service.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        logger.warning("Failed login attempt", email=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        logger.warning("Login attempt for inactive user", email=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Update last login
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(last_login_at=datetime.utcnow())
    )
    await db.commit()

    # Create access token
    access_token = auth_service.create_access_token({
        "sub": user.email,
        "tenant_id": str(user.tenant_id),
        "user_id": str(user.id),
        "role": user.role
    })

    # Calculate token expiration
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    logger.info("Successful login", email=form_data.username, user_id=str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.from_orm(user)
    )


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    tenant_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Register a new user (admin only).

    - **user_data**: User creation data
    - **tenant_name**: Optional tenant name for new tenant creation
    """
    logger.info("User registration attempt", email=user_data.email, by_user=current_user.email)

    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Handle tenant creation if specified
    tenant_id = current_user.tenant_id
    if tenant_name and current_user.role == 'super_admin':
        # Create new tenant
        tenant = Tenant(
            name=tenant_name,
            created_by=current_user.id
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        tenant_id = tenant.id
        logger.info("Created new tenant", tenant_name=tenant_name, tenant_id=str(tenant.id))

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        tenant_id=tenant_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        job_title=user_data.job_title,
        role=user_data.role,
        whatsapp_number=user_data.whatsapp_number,
        created_by=current_user.id
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    logger.info("User registered successfully", email=user_data.email, user_id=str(db_user.id))

    return UserResponse.from_orm(db_user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's information."""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's information."""
    update_data = user_update.dict(exclude_unset=True)

    # Hash password if provided
    if 'password' in update_data:
        update_data['password_hash'] = get_password_hash(update_data.pop('password'))

    # Update user
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(**update_data, updated_at=datetime.utcnow())
    )
    await db.commit()

    # Refresh user data
    await db.refresh(current_user)

    logger.info("User updated profile", user_id=str(current_user.id))

    return UserResponse.from_orm(current_user)


@router.post("/password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset for a user."""
    # Find user by email
    result = await db.execute(
        select(User).where(
            User.email == reset_request.email,
            User.is_active == True
        )
    )
    user = result.scalar_one_or_none()

    if user:
        # Generate reset token
        reset_token = auth_service.create_password_reset_token(user.email)

        # Send reset email in background
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            reset_token
        )

        logger.info("Password reset requested", email=user.email)

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with token."""
    try:
        # Decode reset token
        payload = auth_service.decode_password_reset_token(reset_confirm.token)
        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        # Find user
        result = await db.execute(
            select(User).where(
                User.email == email,
                User.is_active == True
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        # Update password
        hashed_password = get_password_hash(reset_confirm.new_password)
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                password_hash=hashed_password,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()

        logger.info("Password reset successful", email=email)

        return {"message": "Password reset successful"}

    except Exception as e:
        logger.error("Password reset failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """Create a new tenant (super admin only)."""
    logger.info("Tenant creation attempt", name=tenant_data.name, by_user=current_user.email)

    # Check if domain is already taken
    if tenant_data.domain:
        existing_tenant = await db.execute(
            select(Tenant).where(Tenant.domain == tenant_data.domain)
        )
        if existing_tenant.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain already in use"
            )

    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        domain=tenant_data.domain,
        subscription_plan=tenant_data.subscription_plan,
        contact_email=tenant_data.contact_email,
        contact_phone=tenant_data.contact_phone,
        created_by=current_user.id
    )

    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    logger.info("Tenant created successfully", tenant_name=tenant_data.name, tenant_id=str(tenant.id))

    return TenantResponse.from_orm(tenant)


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """List all tenants (super admin only)."""
    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()

    return [TenantResponse.from_orm(tenant) for tenant in tenants]


@router.post("/superadmin/login", response_model=TokenResponse)
async def superadmin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Superadmin login using environment variables.

    This endpoint allows superadmin login using credentials stored in environment variables,
    bypassing normal user authentication for administrative access.
    """
    import os

    # Get superadmin credentials from environment variables
    superadmin_email = os.getenv("SUPERADMIN_EMAIL")
    superadmin_password = os.getenv("SUPERADMIN_PASSWORD")

    # Check if superadmin credentials are configured
    if not superadmin_email or not superadmin_password:
        logger.warning("Superadmin login attempted but credentials not configured")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access not configured"
        )

    # Validate credentials against environment variables
    if form_data.username != superadmin_email or form_data.password != superadmin_password:
        logger.warning("Superadmin login failed - invalid credentials", email=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superadmin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if superadmin user exists in database, create if not
    result = await db.execute(
        select(User).where(User.email == superadmin_email)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create superadmin user if it doesn't exist
        from ..utils.security import get_password_hash
        from datetime import datetime

        superadmin_user = User(
            email=superadmin_email,
            password_hash=get_password_hash(superadmin_password),
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_active=True,
            is_email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(superadmin_user)
        await db.commit()
        await db.refresh(superadmin_user)
        user = superadmin_user

        logger.info("Superadmin user created", email=superadmin_email)

    # Update last login
    from datetime import datetime
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(last_login_at=datetime.utcnow())
    )
    await db.commit()

    # Create access token
    access_token = auth_service.create_access_token({
        "sub": user.email,
        "user_id": str(user.id),
        "role": user.role,
        "superadmin": True  # Mark as superadmin token
    })

    # Calculate token expiration
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    logger.info("Superadmin login successful", email=user.email)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.from_orm(user)
    )


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """Get tenant details (super admin only)."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    return TenantResponse.from_orm(tenant)
