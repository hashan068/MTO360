"""
Notification Pydantic schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    user_id: int = Field(..., description="ID of the user to notify")
    message: str = Field(..., description="Notification message")
    notification_type: str = Field(default="general", description="Type of notification")
    related_entity_type: Optional[str] = Field(None, description="Type of related entity (e.g., 'manufacturing_order_operation')")
    related_entity_id: Optional[int] = Field(None, description="ID of related entity")
    severity: str = Field(default="info", description="Notification severity: info, warning, error")
    action_url: Optional[str] = Field(None, description="URL to navigate to when notification is clicked")


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    user_id: int
    message: str
    read: bool
    timestamp: datetime
    notification_type: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    severity: str
    action_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None
