"""
RFQ Repository Implementation
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.sales import RFQ, RFQStatusEnum
from app.modules.sales.domain.interfaces import RFQRepository as RFQRepositoryProtocol


class RFQRepository:
    """Repository implementation for RFQ"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, rfq_id: int) -> Optional[RFQ]:
        """Get RFQ by ID"""
        result = await self.db.execute(
            select(RFQ)
            .options(selectinload(RFQ.items))
            .where(RFQ.id == rfq_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RFQ]:
        """Get all RFQs with pagination"""
        result = await self.db.execute(
            select(RFQ)
            .options(selectinload(RFQ.items))
            .offset(skip)
            .limit(limit)
            .order_by(RFQ.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, creator_id: int, status: RFQStatusEnum = RFQStatusEnum.DRAFT,
                     due_date: Optional[datetime] = None, description: Optional[str] = None) -> RFQ:
        """Create a new RFQ"""
        rfq = RFQ(
            creator_id=creator_id,
            status=status,
            due_date=due_date,
            description=description,
        )
        self.db.add(rfq)
        await self.db.flush()
        await self.db.refresh(rfq)
        return rfq
    
    async def update(self, rfq_id: int, **kwargs) -> Optional[RFQ]:
        """Update RFQ"""
        rfq = await self.get_by_id(rfq_id)
        if not rfq:
            return None
        
        for key, value in kwargs.items():
            if hasattr(rfq, key):
                setattr(rfq, key, value)
        
        await self.db.flush()
        await self.db.refresh(rfq)
        return rfq
    
    async def delete(self, rfq_id: int) -> bool:
        """Delete RFQ"""
        rfq = await self.get_by_id(rfq_id)
        if not rfq:
            return False
        
        await self.db.delete(rfq)
        await self.db.flush()
        return True

