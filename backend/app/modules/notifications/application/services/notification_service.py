"""
Notification Service

Business logic for notification management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import Notification
from app.modules.notifications.domain.interfaces import NotificationRepository
from app.modules.notifications.infra.repositories.notification_repo import NotificationRepository as NotificationRepositoryImpl


class NotificationService:
    """Service for notification operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        notification_repo: Optional[NotificationRepository] = None,
    ):
        self.db = db
        self.notification_repo = notification_repo or NotificationRepositoryImpl(db)
    
    async def get_notification(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        return await self.notification_repo.get_by_id(notification_id)
    
    async def get_notifications(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Notification]:
        """Get all notifications with optional user filter"""
        return await self.notification_repo.get_all(user_id=user_id, skip=skip, limit=limit)
    
    async def create_notification(
        self,
        user_id: int,
        message: str,
        read: bool = False,
    ) -> Notification:
        """Create a new notification"""
        notification = await self.notification_repo.create(
            user_id=user_id,
            message=message,
            read=read,
        )
        await self.db.commit()
        return notification
    
    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """Mark notification as read"""
        notification = await self.notification_repo.mark_as_read(notification_id)
        if notification:
            await self.db.commit()
        return notification
    
    async def delete_notification(self, notification_id: int) -> bool:
        """Delete notification"""
        result = await self.notification_repo.delete(notification_id)
        if result:
            await self.db.commit()
        return result

