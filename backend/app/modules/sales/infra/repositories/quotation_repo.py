"""
Quotation Repository Implementation
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.sales import Quotation, QuotationStatusEnum
from app.modules.sales.domain.interfaces import QuotationRepository as QuotationRepositoryProtocol


class QuotationRepository:
    """Repository implementation for Quotation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """Get quotation by ID"""
        result = await self.db.execute(
            select(Quotation)
            .options(selectinload(Quotation.customer), selectinload(Quotation.quotation_items))
            .where(Quotation.id == quotation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Quotation]:
        """Get all quotations with pagination"""
        result = await self.db.execute(
            select(Quotation)
            .options(selectinload(Quotation.customer))
            .offset(skip)
            .limit(limit)
            .order_by(Quotation.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, customer_id: int, date: date, expiration_date: date,
                     invoicing_and_shipping_address: str, total_amount: float,
                     status: QuotationStatusEnum = QuotationStatusEnum.QUOTATION,
                     created_by_id: int) -> Quotation:
        """Create a new quotation"""
        quotation = Quotation(
            customer_id=customer_id,
            date=date,
            expiration_date=expiration_date,
            invoicing_and_shipping_address=invoicing_and_shipping_address,
            total_amount=Decimal(str(total_amount)),
            status=status,
            created_by_id=created_by_id,
        )
        self.db.add(quotation)
        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation
    
    async def update(self, quotation_id: int, **kwargs) -> Optional[Quotation]:
        """Update quotation"""
        quotation = await self.get_by_id(quotation_id)
        if not quotation:
            return None
        
        for key, value in kwargs.items():
            if hasattr(quotation, key):
                if key == 'total_amount' and value is not None:
                    setattr(quotation, key, Decimal(str(value)))
                else:
                    setattr(quotation, key, value)
        
        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation
    
    async def delete(self, quotation_id: int) -> bool:
        """Delete quotation"""
        quotation = await self.get_by_id(quotation_id)
        if not quotation:
            return False
        
        await self.db.delete(quotation)
        await self.db.flush()
        return True

