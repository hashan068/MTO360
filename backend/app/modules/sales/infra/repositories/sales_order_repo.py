"""
Sales Order Repository Implementation
"""
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.sales import SalesOrder, SalesOrderStatusEnum
from app.modules.sales.domain.interfaces import SalesOrderRepository as SalesOrderRepositoryProtocol


class SalesOrderRepository:
    """Repository implementation for SalesOrder"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, order_id: int) -> Optional[SalesOrder]:
        """Get sales order by ID"""
        from app.models.sales import SalesOrderItem
        
        result = await self.db.execute(
            select(SalesOrder)
            .options(
                selectinload(SalesOrder.customer),
                selectinload(SalesOrder.order_items).selectinload(SalesOrderItem.product),
                selectinload(SalesOrder.quotation)
            )
            .where(SalesOrder.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[SalesOrderStatusEnum] = None,
        search: Optional[str] = None,
    ) -> List[SalesOrder]:
        """Get all sales orders with pagination, date filtering, status filter, and search"""
        from app.models.sales import SalesOrderItem, Product, Customer
        
        query = select(SalesOrder).options(
            selectinload(SalesOrder.customer),
            selectinload(SalesOrder.order_items).selectinload(SalesOrderItem.product)
        )
        
        # Apply date range filter
        if start_date and end_date:
            query = query.where(
                SalesOrder.created_at >= datetime.combine(start_date, datetime.min.time()),
                SalesOrder.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        elif start_date:
            query = query.where(SalesOrder.created_at >= datetime.combine(start_date, datetime.min.time()))
        elif end_date:
            query = query.where(SalesOrder.created_at <= datetime.combine(end_date, datetime.max.time()))
        
        # Apply status filter
        if status_filter:
            query = query.where(SalesOrder.status == status_filter)
        
        # Apply search filter (search by customer name)
        if search:
            search_pattern = f"%{search}%"
            query = query.join(Customer).where(
                Customer.name.ilike(search_pattern)
            )
        
        result = await self.db.execute(
            query
            .offset(skip)
            .limit(limit)
            .order_by(SalesOrder.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, customer_id: int, total_amount: float,
                     status: SalesOrderStatusEnum = SalesOrderStatusEnum.PENDING,
                     created_at: Optional[datetime] = None) -> SalesOrder:
        """Create a new sales order"""
        order = SalesOrder(
            customer_id=customer_id,
            total_amount=Decimal(str(total_amount)),
            status=status,
        )
        if created_at:
            order.created_at = created_at
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def update(self, order_id: int, **kwargs) -> Optional[SalesOrder]:
        """Update sales order"""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        for key, value in kwargs.items():
            if hasattr(order, key):
                if key == 'total_amount' and value is not None:
                    setattr(order, key, Decimal(str(value)))
                else:
                    setattr(order, key, value)
        
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def delete(self, order_id: int) -> bool:
        """Delete sales order"""
        order = await self.get_by_id(order_id)
        if not order:
            return False
        
        await self.db.delete(order)
        await self.db.flush()
        return True

