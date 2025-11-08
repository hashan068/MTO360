"""
Purchase Order Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.inventory import PurchaseOrder, PurchaseOrderStatusEnum
from app.modules.inventory.domain.interfaces import PurchaseOrderRepository as PurchaseOrderRepositoryProtocol


class PurchaseOrderRepository:
    """Repository implementation for PurchaseOrder"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, order_id: int) -> Optional[PurchaseOrder]:
        """Get purchase order by ID"""
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.purchase_requisition),
                selectinload(PurchaseOrder.supplier)
            )
            .where(PurchaseOrder.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Get all purchase orders with pagination"""
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.purchase_requisition),
                selectinload(PurchaseOrder.supplier)
            )
            .offset(skip)
            .limit(limit)
            .order_by(PurchaseOrder.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, creator_id: Optional[int], purchase_requisition_id: int,
                     supplier_id: Optional[int] = None, status: PurchaseOrderStatusEnum = PurchaseOrderStatusEnum.DRAFT,
                     notes: Optional[str] = None, price_per_unit: Optional[float] = None,
                     total_price: Optional[float] = None) -> PurchaseOrder:
        """Create a new purchase order"""
        order = PurchaseOrder(
            creator_id=creator_id,
            purchase_requisition_id=purchase_requisition_id,
            supplier_id=supplier_id,
            status=status,
            notes=notes,
            price_per_unit=Decimal(str(price_per_unit)) if price_per_unit else None,
            total_price=Decimal(str(total_price)) if total_price else None,
        )
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def update(self, order_id: int, **kwargs) -> Optional[PurchaseOrder]:
        """Update purchase order"""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        for key, value in kwargs.items():
            if hasattr(order, key):
                if key in ('price_per_unit', 'total_price') and value is not None:
                    setattr(order, key, Decimal(str(value)))
                else:
                    setattr(order, key, value)
        
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def delete(self, order_id: int) -> bool:
        """Delete purchase order"""
        order = await self.get_by_id(order_id)
        if not order:
            return False
        
        await self.db.delete(order)
        await self.db.flush()
        return True

