"""
Quality Management Module
Main exports for quality management system
"""
from app.modules.quality.api import quality_router
from app.modules.quality.application import (
    InspectionService,
    DefectService,
    NCRService,
    ReworkService,
    CAPAService,
    QualityHoldService,
    QualityAnalyticsService,
)
from app.modules.quality.domain import (
    InspectionPointRepositoryProtocol,
    InspectionResultRepositoryProtocol,
    DefectRepositoryProtocol,
    NCRRepositoryProtocol,
    ReworkOperationRepositoryProtocol,
    CAPARepositoryProtocol,
    QualityHoldRepositoryProtocol,
)
from app.modules.quality.infra import (
    InspectionPointRepository,
    InspectionResultRepository,
    DefectRepository,
    NCRRepository,
    ReworkOperationRepository,
    CAPARepository,
    QualityHoldRepository,
)

__all__ = [
    # API
    "quality_router",
    # Services
    "InspectionService",
    "DefectService",
    "NCRService",
    "ReworkService",
    "CAPAService",
    "QualityHoldService",
    "QualityAnalyticsService",
    # Domain protocols
    "InspectionPointRepositoryProtocol",
    "InspectionResultRepositoryProtocol",
    "DefectRepositoryProtocol",
    "NCRRepositoryProtocol",
    "ReworkOperationRepositoryProtocol",
    "CAPARepositoryProtocol",
    "QualityHoldRepositoryProtocol",
    # Repository implementations
    "InspectionPointRepository",
    "InspectionResultRepository",
    "DefectRepository",
    "NCRRepository",
    "ReworkOperationRepository",
    "CAPARepository",
    "QualityHoldRepository",
]
