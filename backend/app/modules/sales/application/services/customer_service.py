"""
Customer Service

Business logic for customer management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import Customer
from app.modules.sales.domain.interfaces import CustomerRepository
from app.modules.sales.infra.repositories.customer_repo import CustomerRepository as CustomerRepositoryImpl


class CustomerService:
    """Service for customer operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        customer_repo: Optional[CustomerRepository] = None,
    ):
        self.db = db
        self.customer_repo = customer_repo or CustomerRepositoryImpl(db)
    
    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return await self.customer_repo.get_by_id(customer_id)
    
    async def get_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers"""
        return await self.customer_repo.get_all(skip=skip, limit=limit)
    
    async def create_customer(
        self,
        name: str,
        email: str,
        phone: str,
        street_address: str,
        city: str,
        is_active: bool = True,
        notes: Optional[str] = None,
    ) -> Customer:
        """Create a new customer"""
        customer = await self.customer_repo.create(
            name=name,
            email=email,
            phone=phone,
            street_address=street_address,
            city=city,
            is_active=is_active,
            notes=notes,
        )
        await self.db.commit()
        return customer
    
    async def update_customer(self, customer_id: int, **kwargs) -> Optional[Customer]:
        """Update customer"""
        customer = await self.customer_repo.update(customer_id, **kwargs)
        if customer:
            await self.db.commit()
        return customer
    
    async def delete_customer(self, customer_id: int) -> bool:
        """Delete customer"""
        result = await self.customer_repo.delete(customer_id)
        if result:
            await self.db.commit()
        return result

