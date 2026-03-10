"""
Quality Management API Router Aggregation
"""
from fastapi import APIRouter

from app.modules.quality.api.inspections import router as inspections_router
from app.modules.quality.api.defects import router as defects_router
from app.modules.quality.api.ncrs import router as ncrs_router
from app.modules.quality.api.rework import router as rework_router
from app.modules.quality.api.capas import router as capas_router
from app.modules.quality.api.quality_holds import router as holds_router
from app.modules.quality.api.analytics import router as analytics_router

# Create main quality router that includes all sub-routers
quality_router = APIRouter()

# Include all quality management routers
quality_router.include_router(inspections_router)
quality_router.include_router(defects_router)
quality_router.include_router(ncrs_router)
quality_router.include_router(rework_router)
quality_router.include_router(capas_router)
quality_router.include_router(holds_router)
quality_router.include_router(analytics_router)

__all__ = ["quality_router"]
