"""
Notification Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notifications import Notification
from app.modules.notifications.domain.interfaces import NotificationRepository as NotificationRepositoryProtocol


class NotificationRepository:
    """Repository implementation for Notification"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Get all notifications with optional user filter"""
        query = select(Notification)
        if user_id:
            query = query.where(Notification.user_id == user_id)
        
        result = await self.db.execute(
            query
            .offset(skip)
            .limit(limit)
            .order_by(Notification.timestamp.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, user_id: int, message: str, read: bool = False) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            message=message,
            read=read,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification
    
    async def update(self, notification_id: int, **kwargs) -> Optional[Notification]:
        """Update notification"""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None
        
        for key, value in kwargs.items():
            if hasattr(notification, key):
                setattr(notification, key, value)
        
        await self.db.flush()
        await self.db.refresh(notification)
        return notification
    
    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """Mark notification as read"""
        return await self.update(notification_id, read=True)
    
    async def delete(self, notification_id: int) -> bool:
        """Delete notification"""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return False
        
        await self.db.delete(notification)
        await self.db.flush()
        return True

