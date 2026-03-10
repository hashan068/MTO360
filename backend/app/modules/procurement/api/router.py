"""
Main procurement API router
Registers all procurement sub-routers
"""
from fastapi import APIRouter

from app.modules.procurement.api import (
    supplier_performance, rfqs, contracts, 
    inventory_optimization, cost_analysis
)


# Create main procurement router
router = APIRouter()

# Include all sub-routers (5 phases complete!)
router.include_router(supplier_performance.router)
router.include_router(rfqs.router)
router.include_router(contracts.router)
router.include_router(inventory_optimization.router)
router.include_router(cost_analysis.router)
