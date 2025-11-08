"""
Product Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.models.sales import Product, InverterTypeEnum
from app.modules.sales.domain.interfaces import ProductRepository as ProductRepositoryProtocol


class ProductRepository:
    """Repository implementation for Product"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        result = await self.db.execute(
            select(Product)
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, model_number: str, description: str, price: float,
                     inverter_type: InverterTypeEnum, power_rating: int, frequency: float,
                     efficiency: float, surge_power: int, warranty_years: int,
                     input_voltage: float, output_voltage: float) -> Product:
        """Create a new product"""
        # Generate name and model number (business logic)
        name = f"{inverter_type.value} {power_rating}W {frequency}Hz"
        model_num = f"INV-{inverter_type.value[:3].upper()}-{power_rating}-{int(frequency)}"
        
        product = Product(
            name=name,
            model_number=model_num,
            description=description,
            price=Decimal(str(price)),
            inverter_type=inverter_type,
            power_rating=power_rating,
            frequency=Decimal(str(frequency)),
            efficiency=Decimal(str(efficiency)),
            surge_power=surge_power,
            warranty_years=warranty_years,
            input_voltage=Decimal(str(input_voltage)),
            output_voltage=Decimal(str(output_voltage)),
        )
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def update(self, product_id: int, **kwargs) -> Optional[Product]:
        """Update product"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        # Regenerate name and model number if relevant fields changed
        if any(key in kwargs for key in ['inverter_type', 'power_rating', 'frequency']):
            inverter_type = kwargs.get('inverter_type', product.inverter_type)
            power_rating = kwargs.get('power_rating', product.power_rating)
            frequency = kwargs.get('frequency', product.frequency)
            kwargs['name'] = f"{inverter_type.value} {power_rating}W {frequency}Hz"
            kwargs['model_number'] = f"INV-{inverter_type.value[:3].upper()}-{power_rating}-{int(frequency)}"
        
        for key, value in kwargs.items():
            if hasattr(product, key):
                if key in ('price', 'frequency', 'efficiency', 'input_voltage', 'output_voltage') and value is not None:
                    setattr(product, key, Decimal(str(value)))
                else:
                    setattr(product, key, value)
        
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Delete product"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        await self.db.delete(product)
        await self.db.flush()
        return True

