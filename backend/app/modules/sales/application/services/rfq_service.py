"""
RFQ Service

Business logic for RFQ management.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import RFQ, RFQItem, RFQStatusEnum
from app.modules.sales.domain.interfaces import (
    RFQRepository,
    RFQItemRepository,
)
from app.modules.sales.infra.repositories.rfq_repo import (
    RFQRepository as RFQRepositoryImpl,
)
from app.modules.sales.infra.repositories.rfq_item_repo import (
    RFQItemRepository as RFQItemRepositoryImpl,
)


class RFQService:
    """Service for RFQ operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        rfq_repo: Optional[RFQRepository] = None,
        rfq_item_repo: Optional[RFQItemRepository] = None,
    ):
        self.db = db
        self.rfq_repo = rfq_repo or RFQRepositoryImpl(db)
        self.rfq_item_repo = rfq_item_repo or RFQItemRepositoryImpl(db)
    
    async def get_rfq(self, rfq_id: int) -> Optional[RFQ]:
        """Get RFQ by ID"""
        return await self.rfq_repo.get_by_id(rfq_id)
    
    async def get_rfqs(self, skip: int = 0, limit: int = 100) -> List[RFQ]:
        """Get all RFQs"""
        return await self.rfq_repo.get_all(skip=skip, limit=limit)
    
    async def create_rfq(
        self,
        creator_id: int,
        status: RFQStatusEnum = RFQStatusEnum.DRAFT,
        due_date: Optional[datetime] = None,
        description: Optional[str] = None,
        items: Optional[List[dict]] = None,
    ) -> RFQ:
        """Create a new RFQ with optional items"""
        rfq = await self.rfq_repo.create(
            creator_id=creator_id,
            status=status,
            due_date=due_date,
            description=description,
        )
        
        # Create RFQ items if provided
        if items:
            for item_data in items:
                await self.rfq_item_repo.create(
                    rfq_id=rfq.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                )
        
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def update_rfq(self, rfq_id: int, **kwargs) -> Optional[RFQ]:
        """Update RFQ"""
        rfq = await self.rfq_repo.update(rfq_id, **kwargs)
        if rfq:
            await self.db.commit()
        return rfq
    
    async def delete_rfq(self, rfq_id: int) -> bool:
        """Delete RFQ"""
        result = await self.rfq_repo.delete(rfq_id)
        if result:
            await self.db.commit()
        return result

