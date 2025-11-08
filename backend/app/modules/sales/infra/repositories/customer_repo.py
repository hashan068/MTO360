"""
Customer Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sales import Customer
from app.modules.sales.domain.interfaces import CustomerRepository as CustomerRepositoryProtocol


class CustomerRepository:
    """Repository implementation for Customer"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers with pagination"""
        result = await self.db.execute(
            select(Customer)
            .offset(skip)
            .limit(limit)
            .order_by(Customer.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, name: str, email: str, phone: str, street_address: str,
                     city: str, is_active: bool = True, notes: Optional[str] = None) -> Customer:
        """Create a new customer"""
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            street_address=street_address,
            city=city,
            is_active=is_active,
            notes=notes,
        )
        self.db.add(customer)
        await self.db.flush()
        await self.db.refresh(customer)
        return customer
    
    async def update(self, customer_id: int, **kwargs) -> Optional[Customer]:
        """Update customer"""
        customer = await self.get_by_id(customer_id)
        if not customer:
            return None
        
        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        
        await self.db.flush()
        await self.db.refresh(customer)
        return customer
    
    async def delete(self, customer_id: int) -> bool:
        """Delete customer"""
        customer = await self.get_by_id(customer_id)
        if not customer:
            return False
        
        await self.db.delete(customer)
        await self.db.flush()
        return True

