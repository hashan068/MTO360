"""
Consumption Transaction Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.inventory import ConsumptionTransaction
from app.modules.inventory.domain.interfaces import ConsumptionTransactionRepository as ConsumptionTransactionRepositoryProtocol


class ConsumptionTransactionRepository:
    """Repository implementation for ConsumptionTransaction"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, transaction_id: int) -> Optional[ConsumptionTransaction]:
        """Get consumption transaction by ID"""
        result = await self.db.execute(
            select(ConsumptionTransaction)
            .options(
                selectinload(ConsumptionTransaction.component),
                selectinload(ConsumptionTransaction.material_requisition_item)
            )
            .where(ConsumptionTransaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ConsumptionTransaction]:
        """Get all consumption transactions with pagination"""
        result = await self.db.execute(
            select(ConsumptionTransaction)
            .options(
                selectinload(ConsumptionTransaction.component),
                selectinload(ConsumptionTransaction.material_requisition_item)
            )
            .offset(skip)
            .limit(limit)
            .order_by(ConsumptionTransaction.timestamp.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, material_requisition_item_id: int, component_id: int,
                     quantity: int, user_id: Optional[int] = None) -> ConsumptionTransaction:
        """Create a new consumption transaction"""
        transaction = ConsumptionTransaction(
            material_requisition_item_id=material_requisition_item_id,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
        )
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        return transaction

