"""
Database models
"""
from app.models.base import Base

# Import User model first
from app.models.user import User

# Import all models to ensure they are registered
from app.models.inventory import (
    Supplier,
    Category,
    Component,
    PurchaseRequisition,
    PurchaseOrder,
    ReplenishTransaction,
    ConsumptionTransaction,
)

from app.models.sales import (
    Customer,
    Product,
    RFQ,
    RFQItem,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
)

from app.models.manufacturing import (
    ManufacturingOrder,
    MaterialRequisition,
    MaterialRequisitionItem,
    BillOfMaterial,
    BOMItem,
    WorkCenter,
    OperationRoute,
    RouteOperation,
    ManufacturingOrderOperation,
    WorkCenterSchedule,
)

from app.models.notifications import (
    Notification,
)

from app.models.permissions import (
    Permission,
    Role,
)

__all__ = [
    "Base",
    "User",
    # Inventory
    "Supplier",
    "Category",
    "Component",
    "PurchaseRequisition",
    "PurchaseOrder",
    "ReplenishTransaction",
    "ConsumptionTransaction",
    # Sales
    "Customer",
    "Product",
    "RFQ",
    "RFQItem",
    "Quotation",
    "QuotationItem",
    "SalesOrder",
    "SalesOrderItem",
    # Manufacturing
    "ManufacturingOrder",
    "MaterialRequisition",
    "MaterialRequisitionItem",
    "BillOfMaterial",
    "BOMItem",
    "WorkCenter",
    "OperationRoute",
    "RouteOperation",
    "ManufacturingOrderOperation",
    "WorkCenterSchedule",
    # Notifications
    "Notification",
    # Permissions
    "Permission",
    "Role",
]

