"""
Notifications module database models
"""
from sqlalchemy import Integer, Text, ForeignKey, Boolean, DateTime, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import enum

from app.models.base import Base


class NotificationTypeEnum(str, enum.Enum):
    """Notification type"""
    OPERATION_ASSIGNMENT = "operation_assignment"
    BLOCKING_ALERT = "blocking_alert"
    OVERALLOCATION_WARNING = "overallocation_warning"
    SCHEDULE_CHANGE = "schedule_change"
    GENERAL = "general"


class NotificationSeverityEnum(str, enum.Enum):
    """Notification severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Production-specific fields
    notification_type: Mapped[NotificationTypeEnum] = mapped_column(
        SQLEnum(NotificationTypeEnum), 
        default=NotificationTypeEnum.GENERAL, 
        nullable=False
    )
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "manufacturing_order_operation"
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    severity: Mapped[NotificationSeverityEnum] = mapped_column(
        SQLEnum(NotificationSeverityEnum), 
        default=NotificationSeverityEnum.INFO, 
        nullable=False
    )
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Deep link to relevant page
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.notification_type.value}, read={self.read})>"

