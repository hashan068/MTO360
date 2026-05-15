"""
RFQ Service - Complete RFQ lifecycle management
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.procurement import (
    ProcurementRFQ, SupplierQuote,
    ProcurementRFQStatusEnum, SupplierQuoteStatusEnum,
)
from app.models.inventory import PurchaseOrder, Supplier, Component, PurchaseOrderStatusEnum
from app.modules.procurement.infra.repositories.rfq_repo import RFQRepository
from app.modules.procurement.infra.repositories.supplier_quote_repo import SupplierQuoteRepository


class RFQService:
    """Service for RFQ and competitive bidding management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rfq_repo = RFQRepository(db)
        self.quote_repo = SupplierQuoteRepository(db)
    
    async def create_rfq(
        self,
        component_id: int,
        quantity: int,
        required_by_date: date,
        closing_datetime: datetime,
        specifications: Optional[str],
        internal_notes: Optional[str],
        created_by: int,
        supplier_ids: List[int]
    ) -> ProcurementRFQ:
        """
        Create a new RFQ
        
        Args:
            component_id: Component to procure
            quantity: Quantity needed
            required_by_date: Date when components are needed
            closing_datetime: When RFQ closes for quotes
            specifications: Technical specifications
            internal_notes: Notes not shared with suppliers
            created_by: User ID creating the RFQ
            supplier_ids: List of supplier IDs to send RFQ to
        
        Returns:
            Created RFQ
        """
        # Generate RFQ number
        rfq_number = await self.rfq_repo.generate_rfq_number()
        
        # Create RFQ
        rfq_data = {
            'rfq_number': rfq_number,
            'component_id': component_id,
            'quantity': quantity,
            'required_by_date': required_by_date,
            'closing_datetime': closing_datetime,
            'specifications': specifications,
            'internal_notes': internal_notes,
            'created_by': created_by,
            'status': ProcurementRFQStatusEnum.DRAFT
        }
        
        rfq = await self.rfq_repo.create(rfq_data)
        
        # Create pending quotes for each supplier
        for supplier_id in supplier_ids:
            quote_data = {
                'rfq_id': rfq.id,
                'supplier_id': supplier_id,
                'status': SupplierQuoteStatusEnum.PENDING,
                'unit_price': Decimal('0.00'),  # Will be updated when quote is submitted
                'lead_time_days': 0,
                'minimum_order_quantity': 1,
                'quote_valid_until': closing_datetime.date()
            }
            await self.quote_repo.create(quote_data)
        
        return rfq
    
    async def send_rfq(self, rfq_id: int) -> ProcurementRFQ:
        """
        Send RFQ to suppliers
        
        Changes status to SENT and sends email notifications to suppliers
        """
        rfq = await self.rfq_repo.get_by_id(rfq_id, include_quotes=True)
        
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")
        
        if rfq.status != ProcurementRFQStatusEnum.DRAFT:
            raise ValueError(f"Can only send RFQs in DRAFT status. Current status: {rfq.status}")
        
        # Update status
        update_data = {
            'status': ProcurementRFQStatusEnum.SENT,
            'sent_at': datetime.utcnow()
        }
        
        rfq = await self.rfq_repo.update(rfq_id, update_data)
        
        # TODO: Send email to suppliers
        # For now, this is a placeholder
        # await self.send_rfq_emails(rfq)
        
        return rfq
    
    async def submit_quote(
        self,
        rfq_id: int,
        supplier_id: int,
        unit_price: Decimal,
        lead_time_days: int,
        minimum_order_quantity: int,
        quote_valid_until: date,
        notes: Optional[str] = None
    ) -> SupplierQuote:
        """
        Supplier submits a quote for an RFQ
        
        Args:
            rfq_id: RFQ ID
            supplier_id: Supplier submitting quote
            unit_price: Price per unit
            lead_time_days: Lead time in days
            minimum_order_quantity: Minimum order quantity
            quote_valid_until: Quote validity date
            notes: Optional notes
        
        Returns:
            Submitted quote
        """
        # Verify RFQ exists and is open
        rfq = await self.rfq_repo.get_by_id(rfq_id)
        
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")
        
        if rfq.status not in [ProcurementRFQStatusEnum.SENT, ProcurementRFQStatusEnum.QUOTES_RECEIVED]:
            raise ValueError(f"RFQ is not open for quotes. Status: {rfq.status}")
        
        if rfq.closing_datetime < datetime.utcnow():
            raise ValueError("RFQ has closed")
        
        # Get or create quote
        quote = await self.quote_repo.get_quote_by_rfq_and_supplier(rfq_id, supplier_id)
        
        if not quote:
            raise ValueError(f"No quote record found for supplier {supplier_id} on RFQ {rfq_id}")
        
        # Update quote
        update_data = {
            'unit_price': unit_price,
            'lead_time_days': lead_time_days,
            'minimum_order_quantity': minimum_order_quantity,
            'quote_valid_until': quote_valid_until,
            'notes': notes,
            'status': SupplierQuoteStatusEnum.SUBMITTED,
            'submitted_at': datetime.utcnow()
        }
        
        quote = await self.quote_repo.update(quote.id, update_data)
        
        # Update RFQ status if this is the first quote
        if rfq.status == ProcurementRFQStatusEnum.SENT:
            await self.rfq_repo.update(rfq_id, {'status': ProcurementRFQStatusEnum.QUOTES_RECEIVED})
        
        return quote
    
    async def compare_quotes(self, rfq_id: int, sort_by: str = "price") -> dict:
        """
        Compare all quotes for an RFQ
        
        Args:
            rfq_id: RFQ ID
            sort_by: Sort criteria (price, lead_time, score)
        
        Returns:
            Comparison data with recommendations
        """
        rfq = await self.rfq_repo.get_by_id(rfq_id, include_quotes=True)
        
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")
        
        # Get all submitted quotes
        quotes = await self.quote_repo.get_quotes_for_rfq(rfq_id, SupplierQuoteStatusEnum.SUBMITTED)
        
        if not quotes:
            return {
                'rfq': rfq,
                'quotes': [],
                'recommendation': 'No quotes received yet'
            }
        
        # Calculate total price and delivery date for each quote
        comparison_items = []
        best_price = min(q.unit_price for q in quotes)
        best_lead_time = min(q.lead_time_days for q in quotes)
        
        for quote in quotes:
            total_price = quote.unit_price * rfq.quantity
            delivery_date = date.today() + timedelta(days=quote.lead_time_days)
            
            # TODO: Get supplier performance score from SupplierPerformanceService
            supplier_score = Decimal("85.00")  # Placeholder
            
            comparison_items.append({
                'quote_id': quote.id,
                'supplier_id': quote.supplier_id,
                'supplier_name': quote.supplier.name if quote.supplier else "Unknown",
                'supplier_score': supplier_score,
                'unit_price': quote.unit_price,
                'total_price': total_price,
                'lead_time_days': quote.lead_time_days,
                'minimum_order_quantity': quote.minimum_order_quantity,
                'delivery_date': delivery_date,
                'quote_valid_until': quote.quote_valid_until,
                'is_best_price': quote.unit_price == best_price,
                'is_best_lead_time': quote.lead_time_days == best_lead_time
            })
        
        # Sort based on criteria
        if sort_by == "price":
            comparison_items.sort(key=lambda x: x['total_price'])
        elif sort_by == "lead_time":
            comparison_items.sort(key=lambda x: x['lead_time_days'])
        elif sort_by == "score":
            comparison_items.sort(key=lambda x: x['supplier_score'], reverse=True)
        
        # Generate recommendation
        best_overall = comparison_items[0]
        recommendation = f"Recommended: {best_overall['supplier_name']} "
        
        if best_overall['is_best_price'] and best_overall['is_best_lead_time']:
            recommendation += "(Best price and lead time)"
        elif best_overall['is_best_price']:
            recommendation += "(Best price)"
        elif best_overall['is_best_lead_time']:
            recommendation += "(Best lead time)"
        else:
            recommendation += f"(High supplier score: {best_overall['supplier_score']}%)"
        
        return {
            'rfq': rfq,
            'quotes': comparison_items,
            'recommendation': recommendation
        }
    
    async def award_rfq(self, rfq_id: int, quote_id: int, justification: str) -> dict:
        """
        Award RFQ to winning supplier and create Purchase Order
        
        Args:
            rfq_id: RFQ ID
            quote_id: Winning quote ID
            justification: Reason for award
        
        Returns:
            dict with RFQ, awarded quote, and created PO
        """
        # Start transaction
        async with self.db.begin_nested():
            # Verify RFQ
            rfq = await self.rfq_repo.get_by_id(rfq_id)
            
            if not rfq:
                raise ValueError(f"RFQ {rfq_id} not found")
            
            if rfq.status not in [ProcurementRFQStatusEnum.SENT, ProcurementRFQStatusEnum.QUOTES_RECEIVED]:
                raise ValueError(f"Cannot award RFQ with status {rfq.status}")
            
            # Verify quote belongs to this RFQ
            quote = await self.quote_repo.get_by_id(quote_id)
            
            if not quote or quote.rfq_id != rfq_id:
                raise ValueError(f"Quote {quote_id} not found for RFQ {rfq_id}")
            
            if quote.status != SupplierQuoteStatusEnum.SUBMITTED:
                raise ValueError(f"Quote must be in SUBMITTED status. Current: {quote.status}")
            
            # Award the winning quote
            awarded_quote = await self.quote_repo.award_quote(quote_id, justification)
            
            # Reject other quotes
            other_quotes = await self.quote_repo.get_quotes_for_rfq(rfq_id, SupplierQuoteStatusEnum.SUBMITTED)
            for other_quote in other_quotes:
                if other_quote.id != quote_id:
                    await self.quote_repo.reject_quote(other_quote.id)
            
            # Create Purchase Order
            po_data = {
                'supplier_id': quote.supplier_id,
                'purchase_requisition_id': None,  # RFQ-based PO doesn't require PR
                'status': PurchaseOrderStatusEnum.DRAFT,
                'price_per_unit': quote.unit_price,
                'total_price': quote.unit_price * rfq.quantity,
                'notes': f"Created from RFQ {rfq.rfq_number}. {justification}",
                'created_by': rfq.created_by
            }
            
            po = PurchaseOrder(**po_data)
            self.db.add(po)
            
            # Update RFQ status
            await self.rfq_repo.update(rfq_id, {
                'status': ProcurementRFQStatusEnum.AWARDED,
                'awarded_at': datetime.utcnow()
            })
        
        # Commit transaction
        await self.db.commit()
        await self.db.refresh(po)
        
        # TODO: Send notifications to suppliers
        
        return {
            'rfq': rfq,
            'awarded_quote': awarded_quote,
            'purchase_order': po
        }
    
    async def cancel_rfq(
self, rfq_id: int, reason: str, cancelled_by: int
    ) -> ProcurementRFQ:
        """Cancel an RFQ"""
        rfq = await self.rfq_repo.get_by_id(rfq_id)
        
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")
        
        if rfq.status == ProcurementRFQStatusEnum.AWARDED:
            raise ValueError("Cannot cancel an awarded RFQ")
        
        update_data = {
            'status': ProcurementRFQStatusEnum.CANCELLED,
            'cancelled_at': datetime.utcnow(),
            'cancellation_reason': reason
        }
        
        return await self.rfq_repo.update(rfq_id, update_data)
    
    async def get_rfq(self, rfq_id: int) -> Optional[ProcurementRFQ]:
        """Get RFQ by ID"""
        return await self.rfq_repo.get_by_id(rfq_id, include_quotes=True)
    
    async def list_rfqs(
        self,
        status: Optional[ProcurementRFQStatusEnum] = None,
        component_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ProcurementRFQ]:
        """List RFQs with filters"""
        return await self.rfq_repo.list_rfqs(status, component_id, None, limit, offset)
