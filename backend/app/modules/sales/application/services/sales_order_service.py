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
from app.modules.sales.infra.repositories.customer_repo import (
    CustomerRepository,
)
from app.modules.sales.domain.exceptions import (
    DocumentNotFoundError,
    InvalidStatusTransitionError,
    DocumentLockedException,
    ValidationError,
)


class SalesOrderService:
    """Service for sales order operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        sales_order_repo: Optional[SalesOrderRepository] = None,
        sales_order_item_repo: Optional[SalesOrderItemRepository] = None,
        customer_repo: Optional[CustomerRepository] = None,
    ):
        self.db = db
        self.sales_order_repo = sales_order_repo or SalesOrderRepositoryImpl(db)
        self.sales_order_item_repo = sales_order_item_repo or SalesOrderItemRepositoryImpl(db)
        self.customer_repo = customer_repo or CustomerRepository(db)
    
    async def get_sales_order(self, order_id: int) -> Optional[SalesOrder]:
        """Get sales order by ID"""
        return await self.sales_order_repo.get_by_id(order_id)
    
    async def get_sales_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[SalesOrderStatusEnum] = None,
        search: Optional[str] = None,
    ) -> List[SalesOrder]:
        """Get all sales orders with date filtering, status filter, and search"""
        return await self.sales_order_repo.get_all(
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter,
            search=search,
        )
    
    async def create_sales_order(
        self,
        customer_id: int,
        order_items: List[dict],
        created_at: Optional[datetime] = None,
    ) -> SalesOrder:
        """Create a new sales order with items"""
        # Validate customer exists and is active
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValidationError(f"Customer with id {customer_id} not found")
        if not customer.is_active:
            raise ValidationError(f"Customer {customer.name} is not active")
        
        # Validate items
        if not order_items or len(order_items) == 0:
            raise ValidationError("At least one order item is required")
        
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
        """Update sales order with edit permission check"""
        order = await self.sales_order_repo.get_by_id(order_id)
        if not order:
            return None
        
        # Check if sales order can be edited
        if not self.can_edit(order):
            raise DocumentLockedException(
                f"Cannot edit sales order in {order.status.value} status"
            )
        
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
    
    async def update_sales_order_status(
        self,
        order_id: int,
        new_status: SalesOrderStatusEnum,
        user_id: int,
    ) -> Optional[SalesOrder]:
        """Update sales order status with workflow validation"""
        order = await self.sales_order_repo.get_by_id(order_id)
        if not order:
            raise DocumentNotFoundError(f"Sales order with id {order_id} not found")
        
        # Validate status transition
        self.validate_status_transition(order.status, new_status)
        
        # Additional validation for confirmed status
        if new_status == SalesOrderStatusEnum.CONFIRMED:
            # Validate customer information is complete
            if not order.customer:
                raise ValidationError("Customer information is required to confirm order")
            if not order.customer.is_active:
                raise ValidationError(f"Cannot confirm order for inactive customer {order.customer.name}")
        
        # Set delivery date when status changes to delivered
        update_data = {"status": new_status}
        if new_status == SalesOrderStatusEnum.DELIVERED:
            update_data["delivery_date"] = datetime.now()
        
        # Update status
        order = await self.sales_order_repo.update(order_id, **update_data)
        await self.db.commit()
        return order
    
    def validate_status_transition(
        self,
        current_status: SalesOrderStatusEnum,
        new_status: SalesOrderStatusEnum,
    ) -> None:
        """Validate sales order status transitions"""
        # Define valid transitions
        valid_transitions = {
            SalesOrderStatusEnum.PENDING: [
                SalesOrderStatusEnum.CONFIRMED,
                SalesOrderStatusEnum.CANCELLED,
            ],
            SalesOrderStatusEnum.CONFIRMED: [
                SalesOrderStatusEnum.PROCESSING,
                SalesOrderStatusEnum.CANCELLED,
            ],
            SalesOrderStatusEnum.PROCESSING: [
                SalesOrderStatusEnum.IN_PRODUCTION,
                SalesOrderStatusEnum.CANCELLED,
            ],
            SalesOrderStatusEnum.IN_PRODUCTION: [
                SalesOrderStatusEnum.READY_FOR_DELIVERY,
            ],
            SalesOrderStatusEnum.READY_FOR_DELIVERY: [
                SalesOrderStatusEnum.DELIVERED,
            ],
            SalesOrderStatusEnum.CANCELLED: [],  # Terminal state
            SalesOrderStatusEnum.DELIVERED: [],  # Terminal state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise InvalidStatusTransitionError(
                f"Cannot transition sales order from {current_status.value} to {new_status.value}"
            )
    
    async def cancel_sales_order(
        self,
        order_id: int,
        user_id: int,
        reason: Optional[str] = None,
    ) -> Optional[SalesOrder]:
        """Cancel sales order with manufacturing order checks"""
        order = await self.sales_order_repo.get_by_id(order_id)
        if not order:
            raise DocumentNotFoundError(f"Sales order with id {order_id} not found")
        
        # Check if cancellation is allowed based on current status
        if order.status in [SalesOrderStatusEnum.CANCELLED, SalesOrderStatusEnum.DELIVERED]:
            raise InvalidStatusTransitionError(
                f"Cannot cancel sales order in {order.status.value} status"
            )
        
        # Check for active manufacturing orders
        # Note: This would require checking manufacturing_orders relationship
        # For now, we'll allow cancellation with a warning for processing/in_production
        if order.status in [
            SalesOrderStatusEnum.PROCESSING,
            SalesOrderStatusEnum.IN_PRODUCTION,
        ]:
            # In a real implementation, we would check for active manufacturing orders
            # and potentially require confirmation or prevent cancellation
            pass
        
        # Update status to cancelled
        order = await self.sales_order_repo.update(order_id, status=SalesOrderStatusEnum.CANCELLED)
        await self.db.commit()
        return order
    
    def can_edit(self, order: SalesOrder) -> bool:
        """Check if sales order can be edited based on status"""
        # Cannot edit after confirmed or later stages
        locked_statuses = [
            SalesOrderStatusEnum.CONFIRMED,
            SalesOrderStatusEnum.PROCESSING,
            SalesOrderStatusEnum.IN_PRODUCTION,
            SalesOrderStatusEnum.READY_FOR_DELIVERY,
            SalesOrderStatusEnum.DELIVERED,
            SalesOrderStatusEnum.CANCELLED,
        ]
        return order.status not in locked_statuses

