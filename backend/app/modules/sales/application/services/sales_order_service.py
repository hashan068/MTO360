"""
Sales Order Service

Business logic for sales order management.
"""
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.sales import SalesOrder, SalesOrderItem, SalesOrderStatusEnum
from app.modules.sales.domain.interfaces import (
    SalesOrderRepository,
    SalesOrderItemRepository,
)
from app.modules.sales.infra.repositories.sales_order_repo import (
    SalesOrderRepository as SalesOrderRepositoryImpl,
)
from app.modules.sales.infra.repositories.sales_order_item_repo import (
    SalesOrderItemRepository as SalesOrderItemRepositoryImpl,
)


class SalesOrderService:
    """Service for sales order operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        sales_order_repo: Optional[SalesOrderRepository] = None,
        sales_order_item_repo: Optional[SalesOrderItemRepository] = None,
    ):
        self.db = db
        self.sales_order_repo = sales_order_repo or SalesOrderRepositoryImpl(db)
        self.sales_order_item_repo = sales_order_item_repo or SalesOrderItemRepositoryImpl(db)
    
    async def get_sales_order(self, order_id: int) -> Optional[SalesOrder]:
        """Get sales order by ID"""
        return await self.sales_order_repo.get_by_id(order_id)
    
    async def get_sales_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[SalesOrder]:
        """Get all sales orders with optional date filtering"""
        return await self.sales_order_repo.get_all(
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )
    
    async def create_sales_order(
        self,
        customer_id: int,
        order_items: List[dict],
        created_at: Optional[datetime] = None,
    ) -> SalesOrder:
        """Create a new sales order with items"""
        # Calculate total amount
        total_amount = sum(
            Decimal(str(item['price'])) * item['quantity']
            for item in order_items
        )
        
        # Create order
        order = await self.sales_order_repo.create(
            customer_id=customer_id,
            total_amount=float(total_amount),
            status=SalesOrderStatusEnum.PENDING,
            created_at=created_at,
        )
        
        # Create order items
        for item_data in order_items:
            await self.sales_order_item_repo.create(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price'],
            )
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def update_sales_order(self, order_id: int, **kwargs) -> Optional[SalesOrder]:
        """Update sales order"""
        order = await self.sales_order_repo.update(order_id, **kwargs)
        if order:
            await self.db.commit()
        return order
    
    async def delete_sales_order(self, order_id: int) -> bool:
        """Delete sales order"""
        result = await self.sales_order_repo.delete(order_id)
        if result:
            await self.db.commit()
        return result
    
    async def delete_sales_order_item(self, item_id: int) -> bool:
        """Delete sales order item"""
        result = await self.sales_order_item_repo.delete(item_id)
        if result:
            await self.db.commit()
        return result

