"""
Manufacturing Module Router

Aggregates all manufacturing-related routers into a single module router.
"""
from fastapi import APIRouter

# Import module subrouters
from app.modules.manufacturing.api.bom import router as bom_router
from app.modules.manufacturing.api.manufacturing_orders import router as manufacturing_orders_router
from app.modules.manufacturing.api.material_requisitions import router as material_requisitions_router
from app.modules.manufacturing.api.work_centers import router as work_centers_router
from app.modules.manufacturing.api.operation_routes import router as operation_routes_router
from app.modules.manufacturing.api.scheduling import router as scheduling_router
from app.modules.manufacturing.api.shop_floor import router as shop_floor_router
from app.modules.manufacturing.api.analytics import router as analytics_router

# Create module router without prefix - preserves all existing paths
router = APIRouter()

# Include all subrouters
router.include_router(bom_router)
router.include_router(manufacturing_orders_router)
router.include_router(material_requisitions_router)
router.include_router(work_centers_router)
router.include_router(operation_routes_router)
router.include_router(scheduling_router)
router.include_router(shop_floor_router)
router.include_router(analytics_router)

