"""
Supplier Quote Repository
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.procurement import SupplierQuote, SupplierQuoteStatusEnum


class SupplierQuoteRepository:
    """Repository for supplier quote data access"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, quote_data: dict) -> SupplierQuote:
        """Create a new quote"""
        quote = SupplierQuote(**quote_data)
        self.db.add(quote)
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def get_by_id(self, quote_id: int) -> Optional[SupplierQuote]:
        """Get quote by ID"""
        result = await self.db.execute(
            select(SupplierQuote)
            .options(joinedload(SupplierQuote.supplier))
            .where(SupplierQuote.id == quote_id)
        )
        return result.scalar_one_or_none()
    
    async def get_quotes_for_rfq(self, rfq_id: int, status: Optional[SupplierQuoteStatusEnum] = None) -> List[SupplierQuote]:
        """Get all quotes for an RFQ"""
        query = select(SupplierQuote).options(joinedload(SupplierQuote.supplier)).where(
            SupplierQuote.rfq_id == rfq_id
        )
        
        if status:
            query = query.where(SupplierQuote.status == status)
        
        query = query.order_by(SupplierQuote.unit_price)  # Sort by price (lowest first)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_quote_by_rfq_and_supplier(
        self, 
        rfq_id: int, 
        supplier_id: int
    ) -> Optional[SupplierQuote]:
        """Get a specific supplier's quote for an RFQ"""
        result = await self.db.execute(
            select(SupplierQuote).where(
                and_(
                    SupplierQuote.rfq_id == rfq_id,
                    SupplierQuote.supplier_id == supplier_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, quote_id: int, update_data: dict) -> Optional[SupplierQuote]:
        """Update a quote"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return None
        
        for key, value in update_data.items():
            if hasattr(quote, key):
                setattr(quote, key, value)
        
        quote.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def delete(self, quote_id: int) -> bool:
        """Delete a quote"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return False
        
        await self.db.delete(quote)
        await self.db.commit()
        return True
    
    async def get_best_quote_for_rfq(self, rfq_id: int) -> Optional[SupplierQuote]:
        """Get the best (lowest price) submitted quote for an RFQ"""
        result = await self.db.execute(
            select(SupplierQuote)
            .where(
                and_(
                    SupplierQuote.rfq_id == rfq_id,
                    SupplierQuote.status == SupplierQuoteStatusEnum.SUBMITTED
                )
            )
            .order_by(SupplierQuote.unit_price)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def count_quotes_for_rfq(self, rfq_id: int, status: Optional[SupplierQuoteStatusEnum] = None) -> int:
        """Count quotes for an RFQ"""
        query = select(func.count(SupplierQuote.id)).where(SupplierQuote.rfq_id == rfq_id)
        
        if status:
            query = query.where(SupplierQuote.status == status)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def award_quote(self, quote_id: int, justification: str) -> Optional[SupplierQuote]:
        """Mark a quote as awarded"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return None
        
        quote.status = SupplierQuoteStatusEnum.ACCEPTED
        quote.is_awarded = True
        quote.awarded_at = datetime.utcnow()
        quote.award_justification = justification
        quote.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def reject_quote(self, quote_id: int) -> Optional[SupplierQuote]:
        """Mark a quote as rejected"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return None
        
        quote.status = SupplierQuoteStatusEnum.REJECTED
        quote.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
