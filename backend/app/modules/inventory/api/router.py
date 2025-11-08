"""
Inventory Module Router

Aggregates all inventory-related routers into a single module router.
"""
from fastapi import APIRouter

# Import module subrouters
from app.modules.inventory.api.components import router as components_router
from app.modules.inventory.api.suppliers import router as suppliers_router
from app.modules.inventory.api.purchase_requisitions import router as purchase_requisitions_router
from app.modules.inventory.api.purchase_orders import router as purchase_orders_router

# Create module router without prefix - preserves all existing paths
router = APIRouter()

# Include all subrouters
router.include_router(components_router)
router.include_router(suppliers_router)
router.include_router(purchase_requisitions_router)
router.include_router(purchase_orders_router)

