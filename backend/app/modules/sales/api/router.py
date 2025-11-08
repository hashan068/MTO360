"""
Sales Module Router

Aggregates all sales-related routers into a single module router.
"""
from fastapi import APIRouter

# Import module subrouters
from app.modules.sales.api.customers import router as customers_router
from app.modules.sales.api.products import router as products_router
from app.modules.sales.api.sales_orders import router as sales_orders_router
from app.modules.sales.api.quotations import router as quotations_router
from app.modules.sales.api.rfqs import router as rfqs_router

# Create module router without prefix - preserves all existing paths
router = APIRouter()

# Include all subrouters
router.include_router(customers_router)
router.include_router(products_router)
router.include_router(sales_orders_router)
router.include_router(quotations_router)
router.include_router(rfqs_router)

