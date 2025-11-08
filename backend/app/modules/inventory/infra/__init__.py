"""
Inventory Infrastructure Layer

Contains repositories, adapters, and external integrations.
"""
from .repositories import (
    ComponentRepository,
    SupplierRepository,
    CategoryRepository,
    PurchaseRequisitionRepository,
    PurchaseOrderRepository,
    ReplenishTransactionRepository,
    ConsumptionTransactionRepository,
)

__all__ = [
    "ComponentRepository",
    "SupplierRepository",
    "CategoryRepository",
    "PurchaseRequisitionRepository",
    "PurchaseOrderRepository",
    "ReplenishTransactionRepository",
    "ConsumptionTransactionRepository",
]

