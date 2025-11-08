"""
Purchase Service

Business logic for purchase requisitions and orders.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.inventory import (
    PurchaseRequisition,
    PurchaseOrder,
    ReplenishTransaction,
    ConsumptionTransaction,
    StatusEnum,
    PriorityEnum,
    PurchaseOrderStatusEnum,
)
from app.modules.inventory.domain.interfaces import (
    PurchaseRequisitionRepository,
    PurchaseOrderRepository,
    ReplenishTransactionRepository,
    ConsumptionTransactionRepository,
    ComponentRepository,
)
from app.modules.inventory.infra.repositories.purchase_requisition_repo import (
    PurchaseRequisitionRepository as PurchaseRequisitionRepositoryImpl,
)
from app.modules.inventory.infra.repositories.purchase_order_repo import (
    PurchaseOrderRepository as PurchaseOrderRepositoryImpl,
)
from app.modules.inventory.infra.repositories.replenish_transaction_repo import (
    ReplenishTransactionRepository as ReplenishTransactionRepositoryImpl,
)
from app.modules.inventory.infra.repositories.consumption_transaction_repo import (
    ConsumptionTransactionRepository as ConsumptionTransactionRepositoryImpl,
)
from app.modules.inventory.infra.repositories.component_repo import (
    ComponentRepository as ComponentRepositoryImpl,
)


class PurchaseService:
    """Service for purchase operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        purchase_requisition_repo: Optional[PurchaseRequisitionRepository] = None,
        purchase_order_repo: Optional[PurchaseOrderRepository] = None,
        replenish_transaction_repo: Optional[ReplenishTransactionRepository] = None,
        consumption_transaction_repo: Optional[ConsumptionTransactionRepository] = None,
        component_repo: Optional[ComponentRepository] = None,
    ):
        self.db = db
        self.purchase_requisition_repo = purchase_requisition_repo or PurchaseRequisitionRepositoryImpl(db)
        self.purchase_order_repo = purchase_order_repo or PurchaseOrderRepositoryImpl(db)
        self.replenish_transaction_repo = replenish_transaction_repo or ReplenishTransactionRepositoryImpl(db)
        self.consumption_transaction_repo = consumption_transaction_repo or ConsumptionTransactionRepositoryImpl(db)
        self.component_repo = component_repo or ComponentRepositoryImpl(db)
    
    async def get_purchase_requisition(self, requisition_id: int) -> Optional[PurchaseRequisition]:
        """Get purchase requisition by ID"""
        return await self.purchase_requisition_repo.get_by_id(requisition_id)
    
    async def get_purchase_requisitions(self, skip: int = 0, limit: int = 100) -> List[PurchaseRequisition]:
        """Get all purchase requisitions"""
        return await self.purchase_requisition_repo.get_all(skip=skip, limit=limit)
    
    async def create_purchase_requisition(
        self,
        user_id: Optional[int],
        component_id: int,
        quantity: int,
        status: StatusEnum = StatusEnum.PENDING,
        notes: Optional[str] = None,
        expected_delivery_date: Optional[datetime] = None,
        priority: PriorityEnum = PriorityEnum.HIGH,
    ) -> PurchaseRequisition:
        """Create a new purchase requisition"""
        requisition = await self.purchase_requisition_repo.create(
            user_id=user_id,
            component_id=component_id,
            quantity=quantity,
            status=status,
            notes=notes,
            expected_delivery_date=expected_delivery_date,
            priority=priority,
        )
        await self.db.commit()
        return requisition
    
    async def get_purchase_order(self, order_id: int) -> Optional[PurchaseOrder]:
        """Get purchase order by ID"""
        return await self.purchase_order_repo.get_by_id(order_id)
    
    async def get_purchase_orders(self, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Get all purchase orders"""
        return await self.purchase_order_repo.get_all(skip=skip, limit=limit)
    
    async def create_purchase_order(
        self,
        creator_id: Optional[int],
        purchase_requisition_id: int,
        supplier_id: Optional[int] = None,
        status: PurchaseOrderStatusEnum = PurchaseOrderStatusEnum.DRAFT,
        notes: Optional[str] = None,
        price_per_unit: Optional[float] = None,
    ) -> PurchaseOrder:
        """Create a new purchase order"""
        # Calculate total price if price_per_unit is provided
        total_price = None
        if price_per_unit:
            requisition = await self.purchase_requisition_repo.get_by_id(purchase_requisition_id)
            if requisition:
                total_price = float(price_per_unit) * requisition.quantity
        
        order = await self.purchase_order_repo.create(
            creator_id=creator_id,
            purchase_requisition_id=purchase_requisition_id,
            supplier_id=supplier_id,
            status=status,
            notes=notes,
            price_per_unit=price_per_unit,
            total_price=total_price,
        )
        await self.db.commit()
        return order
    
    async def create_replenish_transaction(
        self,
        purchase_requisition_id: int,
        component_id: int,
        quantity: int,
        user_id: Optional[int] = None,
    ) -> ReplenishTransaction:
        """Create a replenish transaction and update component quantity"""
        # Create transaction
        transaction = await self.replenish_transaction_repo.create(
            purchase_requisition_id=purchase_requisition_id,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
        )
        
        # Update component quantity
        await self.component_repo.update_quantity(component_id, quantity)
        
        await self.db.commit()
        return transaction
    
    async def create_consumption_transaction(
        self,
        material_requisition_item_id: int,
        component_id: int,
        quantity: int,
        user_id: Optional[int] = None,
    ) -> ConsumptionTransaction:
        """Create a consumption transaction and update component quantity"""
        # Check if component has sufficient quantity
        component = await self.component_repo.get_by_id(component_id)
        if not component:
            raise ValueError(f"Component {component_id} not found")
        
        if component.quantity < quantity:
            raise ValueError(
                f"Insufficient quantity for component {component.name}. "
                f"Available: {component.quantity}, Required: {quantity}"
            )
        
        # Create transaction
        transaction = await self.consumption_transaction_repo.create(
            material_requisition_item_id=material_requisition_item_id,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
        )
        
        # Update component quantity (subtract)
        await self.component_repo.update_quantity(component_id, -quantity)
        
        await self.db.commit()
        return transaction

