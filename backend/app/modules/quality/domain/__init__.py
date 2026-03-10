"""
Quality Management Domain Layer
"""
from app.modules.quality.domain.interfaces import (
    InspectionPointRepositoryProtocol,
    InspectionResultRepositoryProtocol,
    DefectRepositoryProtocol,
    NCRRepositoryProtocol,
    ReworkOperationRepositoryProtocol,
    CAPARepositoryProtocol,
    QualityHoldRepositoryProtocol,
)

__all__ = [
    "InspectionPointRepositoryProtocol",
    "InspectionResultRepositoryProtocol",
    "DefectRepositoryProtocol",
    "NCRRepositoryProtocol",
    "ReworkOperationRepositoryProtocol",
    "CAPARepositoryProtocol",
    "QualityHoldRepositoryProtocol",
]
