"""
Permission and Role Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., description="Human-readable permission name")
    code: str = Field(..., description="Unique permission code, e.g., 'production.schedule.create'")
    description: Optional[str] = Field(None, description="Description of what this permission allows")
    module: str = Field(..., description="Module this permission belongs to, e.g., 'production', 'sales'")


class PermissionCreate(PermissionBase):
    """Schema for creating a permission"""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Description of the role")


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    permission_ids: List[int] = Field(default_factory=list, description="List of permission IDs to assign to this role")


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# User Role Assignment Schemas
class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to a user"""
    user_id: int
    role_ids: List[int] = Field(..., description="List of role IDs to assign to the user")


class UserPermissionsResponse(BaseModel):
    """Schema for user permissions response"""
    user_id: int
    username: str
    roles: List[RoleResponse] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list, description="Flattened list of permission codes")
    
    class Config:
        from_attributes = True
