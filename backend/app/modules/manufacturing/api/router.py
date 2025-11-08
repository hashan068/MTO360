"""
Manufacturing Module Router

Aggregates all manufacturing-related routers into a single module router.
"""
from fastapi import APIRouter

# Import module subrouters
from app.modules.manufacturing.api.bom import router as bom_router
from app.modules.manufacturing.api.manufacturing_orders import router as manufacturing_orders_router
from app.modules.manufacturing.api.material_requisitions import router as material_requisitions_router

# Create module router without prefix - preserves all existing paths
router = APIRouter()

# Include all subrouters
router.include_router(bom_router)
router.include_router(manufacturing_orders_router)
router.include_router(material_requisitions_router)

