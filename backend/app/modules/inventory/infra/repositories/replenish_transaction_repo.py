"""
Replenish Transaction Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.inventory import ReplenishTransaction
from app.modules.inventory.domain.interfaces import ReplenishTransactionRepository as ReplenishTransactionRepositoryProtocol


class ReplenishTransactionRepository:
    """Repository implementation for ReplenishTransaction"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, transaction_id: int) -> Optional[ReplenishTransaction]:
        """Get replenish transaction by ID"""
        result = await self.db.execute(
            select(ReplenishTransaction)
            .options(
                selectinload(ReplenishTransaction.component),
                selectinload(ReplenishTransaction.purchase_requisition)
            )
            .where(ReplenishTransaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ReplenishTransaction]:
        """Get all replenish transactions with pagination"""
        result = await self.db.execute(
            select(ReplenishTransaction)
            .options(
                selectinload(ReplenishTransaction.component),
                selectinload(ReplenishTransaction.purchase_requisition)
            )
            .offset(skip)
            .limit(limit)
            .order_by(ReplenishTransaction.timestamp.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, purchase_requisition_id: int, component_id: int,
                     quantity: int, user_id: Optional[int] = None) -> ReplenishTransaction:
        """Create a new replenish transaction"""
        transaction = ReplenishTransaction(
            purchase_requisition_id=purchase_requisition_id,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
        )
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        return transaction

