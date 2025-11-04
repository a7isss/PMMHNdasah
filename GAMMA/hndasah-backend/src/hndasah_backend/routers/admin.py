"""
Admin router for SuperAdmin operations - WhatsApp PM System v3.0 (Gamma)
Comprehensive tenant and user management for SuperAdmins only
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
import structlog

from ..database import get_db
from ..models.user import UserResponse, UserUpdate, UserCreate, TenantCreate, TenantResponse
from ..schemas.user import User, Tenant
from ..routers.auth import get_current_super_admin_user

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/admin", tags=["admin"])


# ===== TENANT MANAGEMENT =====

@router.get("/tenants", response_model=List[dict])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    List all tenants with filtering and pagination (SuperAdmin only).

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **search**: Search term for tenant name or domain
    - **is_active**: Filter by active status
    """
    query = select(Tenant)

    # Apply filters
    if search:
        query = query.where(
            (Tenant.name.ilike(f"%{search}%")) |
            (Tenant.domain.ilike(f"%{search}%"))
        )

    if is_active is not None:
        query = query.where(Tenant.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    tenants = result.scalars().all()

    # Get user count for each tenant
    tenant_data = []
    for tenant in tenants:
        user_count = await db.execute(
            select(func.count(User.id)).where(User.tenant_id == str(tenant.id))
        )
        user_count = user_count.scalar()

        tenant_dict = {
            "id": tenant.id,
            "name": tenant.name,
            "domain": tenant.domain,
            "subscription_plan": tenant.subscription_plan,
            "is_active": tenant.is_active,
            "contact_email": tenant.contact_email,
            "contact_phone": tenant.contact_phone,
            "user_count": user_count,
            "created_at": tenant.created_at,
            "updated_at": tenant.updated_at
        }
        tenant_data.append(tenant_dict)

    return tenant_data


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Create a new tenant (SuperAdmin only).
    """
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
        created_by=str(current_user.id)
    )

    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    logger.info("Tenant created successfully", tenant_name=tenant_data.name, tenant_id=str(tenant.id))

    return TenantResponse.from_orm(tenant)


@router.get("/tenants/{tenant_id}")
async def get_tenant_details(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Get detailed information about a specific tenant (SuperAdmin only).
    """
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Get tenant statistics
    user_count = await db.execute(
        select(func.count(User.id)).where(User.tenant_id == str(tenant.id))
    )
    user_count = user_count.scalar()

    active_user_count = await db.execute(
        select(func.count(User.id)).where(
            User.tenant_id == str(tenant.id),
            User.is_active == True
        )
    )
    active_user_count = active_user_count.scalar()

    # Get project count (if projects table exists)
    try:
        from ..schemas.project import Project
        project_count = await db.execute(
            select(func.count(Project.id)).where(Project.tenant_id == str(tenant.id))
        )
        project_count = project_count.scalar()
    except ImportError:
        project_count = 0

    return {
        "id": tenant.id,
        "name": tenant.name,
        "domain": tenant.domain,
        "subscription_plan": tenant.subscription_plan,
        "is_active": tenant.is_active,
        "contact_email": tenant.contact_email,
        "contact_phone": tenant.contact_phone,
        "address": tenant.address,
        "settings": tenant.settings,
        "ai_config": tenant.ai_config,
        "statistics": {
            "total_users": user_count,
            "active_users": active_user_count,
            "total_projects": project_count
        },
        "created_at": tenant.created_at,
        "updated_at": tenant.updated_at
    }


@router.put("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    tenant_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Update tenant information (SuperAdmin only).
    """
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Validate domain uniqueness if being updated
    if "domain" in tenant_data and tenant_data["domain"] != tenant.domain:
        existing = await db.execute(
            select(Tenant).where(Tenant.domain == tenant_data["domain"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain already in use"
            )

    # Update tenant
    update_data = {k: v for k, v in tenant_data.items() if v is not None}
    await db.execute(
        update(Tenant)
        .where(Tenant.id == tenant_id)
        .values(**update_data)
    )
    await db.commit()

    # Refresh and return updated tenant
    await db.refresh(tenant)

    logger.info("Tenant updated", tenant_id=tenant_id, updated_by=current_user.email)

    return {"message": "Tenant updated successfully", "tenant": tenant}


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Delete a tenant and all associated data (SuperAdmin only).
    Use with extreme caution - this will delete all users and data for the tenant.
    """
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Check if tenant has users
    user_count = await db.execute(
        select(func.count(User.id)).where(User.tenant_id == str(tenant.id))
    )
    if user_count.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tenant with existing users. Deactivate instead."
        )

    # Delete tenant (cascade will handle related data)
    await db.execute(delete(Tenant).where(Tenant.id == tenant_id))
    await db.commit()

    logger.warning("Tenant deleted", tenant_id=tenant_id, deleted_by=current_user.email)

    return {"message": "Tenant deleted successfully"}


# ===== USER MANAGEMENT =====

@router.get("/users", response_model=List[dict])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    tenant_id: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    List all users across all tenants with filtering and pagination (SuperAdmin only).

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **search**: Search term for user name or email
    - **tenant_id**: Filter by specific tenant
    - **role**: Filter by user role
    - **is_active**: Filter by active status
    """
    query = select(User).join(Tenant)

    # Apply filters
    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%")) |
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%"))
        )

    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)

    if role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    users = result.scalars().all()

    # Format response with tenant information
    user_data = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "whatsapp_verified": user.whatsapp_verified,
            "last_login_at": user.last_login_at,
            "tenant": {
                "id": user.tenant.id,
                "name": user.tenant.name,
                "domain": user.tenant.domain
            },
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        user_data.append(user_dict)

    return user_data


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Get detailed information about a specific user (SuperAdmin only).
    """
    result = await db.execute(
        select(User).join(Tenant).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "job_title": user.job_title,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "permissions": user.permissions,
        "preferences": user.preferences,
        "whatsapp_number": user.whatsapp_number,
        "whatsapp_verified": user.whatsapp_verified,
        "ai_profile": user.ai_profile,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "last_login_at": user.last_login_at,
        "tenant": {
            "id": user.tenant.id,
            "name": user.tenant.name,
            "domain": user.tenant.domain,
            "subscription_plan": user.tenant.subscription_plan
        },
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.post("/users")
async def create_user(
    user_data: UserCreate,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Create a new user in a specific tenant (SuperAdmin only).
    """
    # Verify tenant exists
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    from ..utils.security import get_password_hash
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
        created_by=str(current_user.id)
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    logger.info("User created by SuperAdmin", email=user_data.email, tenant_id=tenant_id, created_by=current_user.email)

    return {
        "message": "User created successfully",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "role": db_user.role,
            "tenant_name": tenant.name
        }
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Update user information (SuperAdmin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prepare update data
    update_data = user_data.dict(exclude_unset=True)

    # Hash password if provided
    if 'password' in update_data:
        from ..utils.security import get_password_hash
        update_data['password_hash'] = get_password_hash(update_data.pop('password'))

    # Update user
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
    )
    await db.commit()

    # Refresh user data
    await db.refresh(user)

    logger.info("User updated by SuperAdmin", user_id=user_id, updated_by=current_user.email)

    return {"message": "User updated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Delete a user (SuperAdmin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deletion of self
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Delete user
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

    logger.warning("User deleted by SuperAdmin", user_id=user_id, deleted_by=current_user.email)

    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Deactivate a user account (SuperAdmin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deactivation of self
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Deactivate user
    from datetime import datetime
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False, deactivated_at=datetime.utcnow())
    )
    await db.commit()

    logger.info("User deactivated by SuperAdmin", user_id=user_id, deactivated_by=current_user.email)

    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Reactivate a user account (SuperAdmin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Activate user
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=True, deactivated_at=None)
    )
    await db.commit()

    logger.info("User activated by SuperAdmin", user_id=user_id, activated_by=current_user.email)

    return {"message": "User activated successfully"}


# ===== DASHBOARD STATISTICS =====

@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    """
    Get comprehensive statistics for SuperAdmin dashboard (SuperAdmin only).
    """
    # Tenant statistics
    total_tenants = await db.execute(select(func.count(Tenant.id)))
    total_tenants = total_tenants.scalar()

    active_tenants = await db.execute(
        select(func.count(Tenant.id)).where(Tenant.is_active == True)
    )
    active_tenants = active_tenants.scalar()

    # User statistics
    total_users = await db.execute(select(func.count(User.id)))
    total_users = total_users.scalar()

    active_users = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users.scalar()

    # Users by role
    role_stats = await db.execute(
        select(User.role, func.count(User.id))
        .group_by(User.role)
    )
    role_breakdown = {role: count for role, count in role_stats}

    # Recent activity (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    new_users_30d = await db.execute(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    new_users_30d = new_users_30d.scalar()

    new_tenants_30d = await db.execute(
        select(func.count(Tenant.id)).where(Tenant.created_at >= thirty_days_ago)
    )
    new_tenants_30d = new_tenants_30d.scalar()

    return {
        "tenants": {
            "total": total_tenants,
            "active": active_tenants,
            "inactive": total_tenants - active_tenants,
            "new_last_30_days": new_tenants_30d
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "new_last_30_days": new_users_30d
        },
        "roles": role_breakdown,
        "system_health": {
            "database_status": "healthy",  # Could be enhanced with actual checks
            "last_updated": datetime.utcnow()
        }
    }
