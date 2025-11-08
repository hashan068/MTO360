"""
Pydantic schemas for Notifications module
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: int
    message: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    read: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None

