"""
Permission checker middleware and dependencies
"""
from typing import List, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from functools import wraps

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.user import User
from app.models.permissions import Permission, Role


async def get_user_permissions(user_id: int, db: AsyncSession) -> Set[str]:
    """
    Get all permission codes for a user (from all their roles).
    
    Args:
        user_id: ID of the user
        db: Database session
        
    Returns:
        Set of permission codes (e.g., {"production.schedule.create", "production.schedule.view"})
    """
    # Query user with roles and permissions
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        return set()
    
    # If superuser, grant all permissions
    if user.is_superuser:
        all_permissions_query = select(Permission.code)
        all_permissions_result = await db.execute(all_permissions_query)
        return set(all_permissions_result.scalars().all())
    
    # Collect permissions from all roles
    permissions: Set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    
    return permissions


async def check_user_permission(user_id: int, permission_code: str, db: AsyncSession) -> bool:
    """
    Check if a user has a specific permission.
    
    Args:
        user_id: ID of the user
        permission_code: Permission code to check
        db: Database session
        
    Returns:
        True if user has the permission, False otherwise
    """
    user_permissions = await get_user_permissions(user_id, db)
    return permission_code in user_permissions


def require_permission(permission_code: str):
    """
    Dependency factory to require a specific permission for an endpoint.
    
    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            db: AsyncSession = Depends(get_db),
            user_id: int = Depends(get_current_user_id),
            _: None = Depends(require_permission("production.schedule.create"))
        ):
            # Endpoint logic here
    
    Args:
        permission_code: The required permission code
        
    Returns:
        Dependency function
    """
    async def permission_dependency(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
    ) -> None:
        has_permission = await check_user_permission(user_id, permission_code, db)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {permission_code}"
            )
    
    return permission_dependency


def require_any_permission(permission_codes: List[str]):
    """
    Dependency factory to require ANY of the specified permissions for an endpoint.
    
    Args:
        permission_codes: List of permission codes (user needs at least one)
        
    Returns:
        Dependency function
    """
    async def permission_dependency(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
    ) -> None:
        user_permissions = await get_user_permissions(user_id, db)
        
        has_any = any(perm in user_permissions for perm in permission_codes)
        
        if not has_any:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required one of: {', '.join(permission_codes)}"
            )
    
    return permission_dependency


def require_all_permissions(permission_codes: List[str]):
    """
    Dependency factory to require ALL of the specified permissions for an endpoint.
    
    Args:
        permission_codes: List of permission codes (user needs all of them)
        
    Returns:
        Dependency function
    """
    async def permission_dependency(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
    ) -> None:
        user_permissions = await get_user_permissions(user_id, db)
        
        has_all = all(perm in user_permissions for perm in permission_codes)
        
        if not has_all:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required all of: {', '.join(permission_codes)}"
            )
    
    return permission_dependency
