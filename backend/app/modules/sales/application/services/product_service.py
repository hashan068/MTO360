"""
Product Service

Business logic for product management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import Product, InverterTypeEnum
from app.modules.sales.domain.interfaces import ProductRepository
from app.modules.sales.infra.repositories.product_repo import ProductRepository as ProductRepositoryImpl


class ProductService:
    """Service for product operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        product_repo: Optional[ProductRepository] = None,
    ):
        self.db = db
        self.product_repo = product_repo or ProductRepositoryImpl(db)
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return await self.product_repo.get_by_id(product_id)
    
    async def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products"""
        return await self.product_repo.get_all(skip=skip, limit=limit)
    
    async def create_product(
        self,
        description: str,
        price: float,
        inverter_type: InverterTypeEnum,
        power_rating: int,
        frequency: float,
        efficiency: float,
        surge_power: int,
        warranty_years: int,
        input_voltage: float,
        output_voltage: float,
    ) -> Product:
        """Create a new product"""
        # Generate model number
        model_number = f"INV-{inverter_type.value[:3].upper()}-{power_rating}-{int(frequency)}"
        
        product = await self.product_repo.create(
            model_number=model_number,
            description=description,
            price=price,
            inverter_type=inverter_type,
            power_rating=power_rating,
            frequency=frequency,
            efficiency=efficiency,
            surge_power=surge_power,
            warranty_years=warranty_years,
            input_voltage=input_voltage,
            output_voltage=output_voltage,
        )
        await self.db.commit()
        return product
    
    async def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """Update product"""
        product = await self.product_repo.update(product_id, **kwargs)
        if product:
            await self.db.commit()
        return product
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        result = await self.product_repo.delete(product_id)
        if result:
            await self.db.commit()
        return result

