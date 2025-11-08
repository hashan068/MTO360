"""
Notifications Module Router

Aggregates all notifications-related routers into a single module router.
"""
from fastapi import APIRouter

# Import module subrouters
from app.modules.notifications.api.notifications import router as notifications_router

# Create module router without prefix - preserves all existing paths
router = APIRouter()

# Include all subrouters
router.include_router(notifications_router)

