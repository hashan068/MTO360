"""
RFQ Repository
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.procurement import ProcurementRFQ, ProcurementRFQStatusEnum


class RFQRepository:
    """Repository for RFQ data access"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, rfq_data: dict) -> ProcurementRFQ:
        """Create a new RFQ"""
        rfq = ProcurementRFQ(**rfq_data)
        self.db.add(rfq)
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def get_by_id(self, rfq_id: int, include_quotes: bool = False) -> Optional[ProcurementRFQ]:
        """Get RFQ by ID"""
        query = select(ProcurementRFQ).where(ProcurementRFQ.id == rfq_id)
        
        if include_quotes:
            query = query.options(joinedload(ProcurementRFQ.quotes))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_rfq_number(self, rfq_number: str) -> Optional[ProcurementRFQ]:
        """Get RFQ by RFQ number"""
        result = await self.db.execute(
            select(ProcurementRFQ).where(ProcurementRFQ.rfq_number == rfq_number)
        )
        return result.scalar_one_or_none()
    
    async def list_rfqs(
        self,
        status: Optional[ProcurementRFQStatusEnum] = None,
        component_id: Optional[int] = None,
        created_by: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ProcurementRFQ]:
        """List RFQs with filters"""
        query = select(ProcurementRFQ)
        
        filters = []
        if status:
            filters.append(ProcurementRFQ.status == status)
        if component_id:
            filters.append(ProcurementRFQ.component_id == component_id)
        if created_by:
            filters.append(ProcurementRFQ.created_by == created_by)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(ProcurementRFQ.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, rfq_id: int, update_data: dict) -> Optional[ProcurementRFQ]:
        """Update an RFQ"""
        rfq = await self.get_by_id(rfq_id)
        if not rfq:
            return None
        
        for key, value in update_data.items():
            if hasattr(rfq, key):
                setattr(rfq, key, value)
        
        rfq.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def delete(self, rfq_id: int) -> bool:
        """Delete an RFQ"""
        rfq = await self.get_by_id(rfq_id)
        if not rfq:
            return False
        
        await self.db.delete(rfq)
        await self.db.commit()
        return True
    
    async def get_open_rfqs(self) -> List[ProcurementRFQ]:
        """Get all open RFQs (SENT status, not yet closed)"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(ProcurementRFQ).where(
                and_(
                    ProcurementRFQ.status == ProcurementRFQStatusEnum.SENT,
                    ProcurementRFQ.closing_datetime > now
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_closing_soon_rfqs(self, hours: int = 24) -> List[ProcurementRFQ]:
        """Get RFQs closing within specified hours"""
        from datetime import timedelta
        now = datetime.utcnow()
        closing_threshold = now + timedelta(hours=hours)
        
        result = await self.db.execute(
            select(ProcurementRFQ).where(
                and_(
                    ProcurementRFQ.status == ProcurementRFQStatusEnum.SENT,
                    ProcurementRFQ.closing_datetime > now,
                    ProcurementRFQ.closing_datetime <= closing_threshold
                )
            )
        )
        return list(result.scalars().all())
    
    async def generate_rfq_number(self) -> str:
        """Generate next RFQ number"""
        # Get the latest RFQ number
        result = await self.db.execute(
            select(ProcurementRFQ.rfq_number)
            .where(ProcurementRFQ.rfq_number.like('RFQ-%'))
            .order_by(desc(ProcurementRFQ.rfq_number))
            .limit(1)
        )
        
        latest = result.scalar_one_or_none()
        
        if not latest:
            # First RFQ
            return f"RFQ-{datetime.now().year}-0001"
        
        # Extract number and increment
        try:
            parts = latest.split('-')
            year = parts[1]
            number = int(parts[2])
            
            # Check if year changed
            current_year = str(datetime.now().year)
            if year != current_year:
                return f"RFQ-{current_year}-0001"
            else:
                return f"RFQ-{current_year}-{number + 1:04d}"
        except:
            # Fallback
            return f"RFQ-{datetime.now().year}-{datetime.now().timestamp():.0f}"
