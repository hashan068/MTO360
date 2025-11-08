"""
Sales Domain Repository Interfaces

Protocol-based repository interfaces for sales domain entities.
"""
from typing import Protocol, Optional, List
from datetime import datetime, date

from app.models.sales import (
    Customer,
    Product,
    RFQ,
    RFQItem,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
)
from app.models.sales import (
    RFQStatusEnum,
    QuotationStatusEnum,
    SalesOrderStatusEnum,
    InverterTypeEnum,
)


class CustomerRepository(Protocol):
    """Repository interface for Customer"""
    
    async def get_by_id(self, customer_id: int) -> Optional[Customer]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]: ...
    
    async def create(self, *, name: str, email: str, phone: str, street_address: str,
                     city: str, is_active: bool = True, notes: Optional[str] = None) -> Customer: ...
    
    async def update(self, customer_id: int, **kwargs) -> Optional[Customer]: ...
    
    async def delete(self, customer_id: int) -> bool: ...


class ProductRepository(Protocol):
    """Repository interface for Product"""
    
    async def get_by_id(self, product_id: int) -> Optional[Product]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]: ...
    
    async def create(self, *, model_number: str, description: str, price: float,
                     inverter_type: InverterTypeEnum, power_rating: int, frequency: float,
                     efficiency: float, surge_power: int, warranty_years: int,
                     input_voltage: float, output_voltage: float) -> Product: ...
    
    async def update(self, product_id: int, **kwargs) -> Optional[Product]: ...
    
    async def delete(self, product_id: int) -> bool: ...


class RFQRepository(Protocol):
    """Repository interface for RFQ"""
    
    async def get_by_id(self, rfq_id: int) -> Optional[RFQ]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RFQ]: ...
    
    async def create(self, *, creator_id: int, status: RFQStatusEnum = RFQStatusEnum.DRAFT,
                     due_date: Optional[datetime] = None, description: Optional[str] = None) -> RFQ: ...
    
    async def update(self, rfq_id: int, **kwargs) -> Optional[RFQ]: ...
    
    async def delete(self, rfq_id: int) -> bool: ...


class RFQItemRepository(Protocol):
    """Repository interface for RFQItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[RFQItem]: ...
    
    async def get_by_rfq_id(self, rfq_id: int) -> List[RFQItem]: ...
    
    async def create(self, *, rfq_id: int, product_id: int, quantity: int, unit_price: float) -> RFQItem: ...
    
    async def delete(self, item_id: int) -> bool: ...


class QuotationRepository(Protocol):
    """Repository interface for Quotation"""
    
    async def get_by_id(self, quotation_id: int) -> Optional[Quotation]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Quotation]: ...
    
    async def create(self, *, customer_id: int, date: date, expiration_date: date,
                     invoicing_and_shipping_address: str, total_amount: float,
                     status: QuotationStatusEnum = QuotationStatusEnum.QUOTATION,
                     created_by_id: int) -> Quotation: ...
    
    async def update(self, quotation_id: int, **kwargs) -> Optional[Quotation]: ...
    
    async def delete(self, quotation_id: int) -> bool: ...


class QuotationItemRepository(Protocol):
    """Repository interface for QuotationItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[QuotationItem]: ...
    
    async def get_by_quotation_id(self, quotation_id: int) -> List[QuotationItem]: ...
    
    async def create(self, *, quotation_id: int, product_id: int, quantity: int, unit_price: float) -> QuotationItem: ...
    
    async def delete(self, item_id: int) -> bool: ...


class SalesOrderRepository(Protocol):
    """Repository interface for SalesOrder"""
    
    async def get_by_id(self, order_id: int) -> Optional[SalesOrder]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100, 
                     start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[SalesOrder]: ...
    
    async def create(self, *, customer_id: int, total_amount: float,
                     status: SalesOrderStatusEnum = SalesOrderStatusEnum.PENDING,
                     created_at: Optional[datetime] = None) -> SalesOrder: ...
    
    async def update(self, order_id: int, **kwargs) -> Optional[SalesOrder]: ...
    
    async def delete(self, order_id: int) -> bool: ...


class SalesOrderItemRepository(Protocol):
    """Repository interface for SalesOrderItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[SalesOrderItem]: ...
    
    async def get_by_order_id(self, order_id: int) -> List[SalesOrderItem]: ...
    
    async def create(self, *, order_id: int, product_id: int, quantity: int, price: float) -> SalesOrderItem: ...
    
    async def delete(self, item_id: int) -> bool: ...
