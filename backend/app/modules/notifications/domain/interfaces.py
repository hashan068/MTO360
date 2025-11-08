"""
Notifications Domain Repository Interfaces

Protocol-based repository interfaces for notifications domain entities.
"""
from typing import Protocol, Optional, List

from app.models.notifications import Notification


class NotificationRepository(Protocol):
    """Repository interface for Notification"""
    
    async def get_by_id(self, notification_id: int) -> Optional[Notification]: ...
    
    async def get_all(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Notification]: ...
    
    async def create(self, *, user_id: int, message: str, read: bool = False) -> Notification: ...
    
    async def update(self, notification_id: int, **kwargs) -> Optional[Notification]: ...
    
    async def mark_as_read(self, notification_id: int) -> Optional[Notification]: ...
    
    async def delete(self, notification_id: int) -> bool: ...
