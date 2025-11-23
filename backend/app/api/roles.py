"""
Role and Permission Management API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.permission_checker import require_permission, get_user_permissions
from app.models.user import User
from app.models.permissions import Permission, Role
from app.schemas.permissions import (
    PermissionResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    UserRoleAssignment,
    UserPermissionsResponse,
)


router = APIRouter(prefix="/api/auth", tags=["Roles & Permissions"])


# Permission Endpoints
@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    module: str = Query(None, description="Filter by module"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get all available permissions (optionally filtered by module)"""
    query = select(Permission)
    if module:
        query = query.where(Permission.module == module)
    
    query = query.order_by(Permission.module, Permission.code)
    result = await db.execute(query)
    permissions = result.scalars().all()
    
    return permissions


# Role Endpoints
@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get all roles with their permissions"""
    query = select(Role).order_by(Role.name)
    result = await db.execute(query)
    roles = result.scalars().all()
    
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get a specific role by ID"""
    query = select(Role).where(Role.id == role_id)
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    return role


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("admin.roles.manage")),  # Only admins can create roles
):
    """Create a new role (admin only)"""
    # Check if role name already exists
    query = select(Role).where(Role.name == role_data.name)
    result = await db.execute(query)
    existing_role = result.scalar_one_or_none()
    
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_data.name}' already exists"
        )
    
    # Create new role
    new_role = Role(
        name=role_data.name,
        description=role_data.description
    )
    
    # Assign permissions
    if role_data.permission_ids:
        query = select(Permission).where(Permission.id.in_(role_data.permission_ids))
        result = await db.execute(query)
        permissions = result.scalars().all()
        new_role.permissions = list(permissions)
    
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    
    return new_role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("admin.roles.manage")),  # Only admins can update roles
):
    """Update an existing role (admin only)"""
    query = select(Role).where(Role.id == role_id)
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    # Update fields
    if role_data.name is not None:
        # Check if new name conflicts with existing role
        query = select(Role).where(Role.name == role_data.name, Role.id != role_id)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_data.name}' already exists"
            )
        role.name = role_data.name
    
    if role_data.description is not None:
        role.description = role_data.description
    
    # Update permissions
    if role_data.permission_ids is not None:
        query = select(Permission).where(Permission.id.in_(role_data.permission_ids))
        result = await db.execute(query)
        permissions = result.scalars().all()
        role.permissions = list(permissions)
    
    await db.commit()
    await db.refresh(role)
    
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("admin.roles.manage")),  # Only admins can delete roles
):
    """Delete a role (admin only)"""
    query = select(Role).where(Role.id == role_id)
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    await db.delete(role)
    await db.commit()


# User Role Assignment Endpoints
@router.post("/users/{user_id}/roles", response_model=UserPermissionsResponse)
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("admin.users.manage")),  # Only admins can assign roles
):
    """Assign roles to a user (admin only)"""
    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get roles
    query = select(Role).where(Role.id.in_(role_ids))
    result = await db.execute(query)
    roles = result.scalars().all()
    
    # Assign roles
    user.roles = list(roles)
    await db.commit()
    await db.refresh(user)
    
    # Get flattened permissions
    permissions_set = await get_user_permissions(user_id, db)
    
    return UserPermissionsResponse(
        user_id=user.id,
        username=user.username,
        roles=[RoleResponse.model_validate(r) for r in user.roles],
        permissions=list(permissions_set)
    )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get all permissions for a user (from their roles)"""
    # Users can view their own permissions, admins can view any user's permissions
    if user_id != current_user_id:
        # Check if current user is admin
        query = select(User).where(User.id == current_user_id)
        result = await db.execute(query)
        current_user = result.scalar_one_or_none()
        
        if not current_user or not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can view other users' permissions"
            )
    
    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get flattened permissions
    permissions_set = await get_user_permissions(user_id, db)
    
    return UserPermissionsResponse(
        user_id=user.id,
        username=user.username,
        roles=[RoleResponse.model_validate(r) for r in user.roles],
        permissions=list(permissions_set)
    )
