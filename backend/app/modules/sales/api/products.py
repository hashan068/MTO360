"""
Product API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import ProductCreate, ProductUpdate, ProductResponse
from app.modules.sales.application.services.product_service import ProductService
from app.models.manufacturing import BillOfMaterial

router = APIRouter(prefix="/api/sales/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all products"""
    service = ProductService(db)
    products = await service.get_products(skip=skip, limit=limit)
    
    # Query BOMs for all products in one query to avoid lazy loading
    # Use getattr to safely access id attribute without triggering lazy loads
    product_ids = [getattr(p, 'id', None) for p in products if hasattr(p, 'id')]
    bom_map = {}
    if product_ids:
        # Query only specific columns to avoid relationship access
        result = await db.execute(
            select(BillOfMaterial.id, BillOfMaterial.product_id)
            .where(BillOfMaterial.product_id.in_(product_ids))
        )
        boms = result.all()  # Returns tuples instead of objects
        for bom_id, bom_product_id in boms:
            if bom_product_id not in bom_map:
                bom_map[bom_product_id] = bom_id
    
    # Convert to Pydantic models explicitly to avoid lazy loading during serialization
    # Access all attributes using getattr while still in async context and convert to plain Python types
    response_products = []
    for product in products:
        # Use getattr to safely access attributes without triggering lazy loading
        product_id = getattr(product, 'id', None)
        product_dict = {
            "id": int(product_id) if product_id is not None else 0,
            "name": str(getattr(product, 'name', '')),
            "model_number": str(getattr(product, 'model_number', '')),
            "description": str(getattr(product, 'description', '')),
            "price": getattr(product, 'price', Decimal('0')),
            "inverter_type": getattr(product, 'inverter_type', None),
            "power_rating": int(getattr(product, 'power_rating', 0)),
            "frequency": getattr(product, 'frequency', Decimal('0')),
            "efficiency": getattr(product, 'efficiency', Decimal('0')),
            "surge_power": int(getattr(product, 'surge_power', 0)),
            "warranty_years": int(getattr(product, 'warranty_years', 0)),
            "input_voltage": getattr(product, 'input_voltage', Decimal('0')),
            "output_voltage": getattr(product, 'output_voltage', Decimal('0')),
            "created_at": getattr(product, 'created_at', None),
            "updated_at": getattr(product, 'updated_at', None),
            "product_name": str(getattr(product, 'name', '')),
            "bom": bom_map.get(product_id) if product_id else None,
        }
        # Ensure Decimal types are correct
        for key in ['price', 'frequency', 'efficiency', 'input_voltage', 'output_voltage']:
            if not isinstance(product_dict[key], Decimal):
                product_dict[key] = Decimal(str(product_dict[key])) if product_dict[key] else Decimal('0')
        
        response_products.append(ProductResponse.model_validate(product_dict))
    
    return response_products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get product by ID"""
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Query BOM for this product to avoid lazy loading - query only specific columns
    bom_result = await db.execute(
        select(BillOfMaterial.id)
        .where(BillOfMaterial.product_id == product_id)
        .limit(1)
    )
    bom_row = bom_result.first()
    bom_id = bom_row[0] if bom_row else None
    
    # Convert to Pydantic model explicitly to avoid lazy loading during serialization
    # Access all attributes using getattr to avoid relationship access
    product_dict = {
        "id": int(getattr(product, 'id', 0)),
        "name": str(getattr(product, 'name', '')),
        "model_number": str(getattr(product, 'model_number', '')),
        "description": str(getattr(product, 'description', '')),
        "price": getattr(product, 'price', Decimal('0')),
        "inverter_type": getattr(product, 'inverter_type', None),
        "power_rating": int(getattr(product, 'power_rating', 0)),
        "frequency": getattr(product, 'frequency', Decimal('0')),
        "efficiency": getattr(product, 'efficiency', Decimal('0')),
        "surge_power": int(getattr(product, 'surge_power', 0)),
        "warranty_years": int(getattr(product, 'warranty_years', 0)),
        "input_voltage": getattr(product, 'input_voltage', Decimal('0')),
        "output_voltage": getattr(product, 'output_voltage', Decimal('0')),
        "created_at": getattr(product, 'created_at', None),
        "updated_at": getattr(product, 'updated_at', None),
        "product_name": str(getattr(product, 'name', '')),
        "bom": int(bom_id) if bom_id else None,
    }
    # Ensure Decimal types are correct
    for key in ['price', 'frequency', 'efficiency', 'input_voltage', 'output_voltage']:
        if not isinstance(product_dict[key], Decimal):
            product_dict[key] = Decimal(str(product_dict[key])) if product_dict[key] else Decimal('0')
    
    return ProductResponse.model_validate(product_dict)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new product"""
    service = ProductService(db)
    product = await service.create_product(**data.model_dump())
    
    # Convert to Pydantic model explicitly to avoid lazy loading during serialization
    # Access all attributes using getattr to avoid relationship access
    product_dict = {
        "id": int(getattr(product, 'id', 0)),
        "name": str(getattr(product, 'name', '')),
        "model_number": str(getattr(product, 'model_number', '')),
        "description": str(getattr(product, 'description', '')),
        "price": getattr(product, 'price', Decimal('0')),
        "inverter_type": getattr(product, 'inverter_type', None),
        "power_rating": int(getattr(product, 'power_rating', 0)),
        "frequency": getattr(product, 'frequency', Decimal('0')),
        "efficiency": getattr(product, 'efficiency', Decimal('0')),
        "surge_power": int(getattr(product, 'surge_power', 0)),
        "warranty_years": int(getattr(product, 'warranty_years', 0)),
        "input_voltage": getattr(product, 'input_voltage', Decimal('0')),
        "output_voltage": getattr(product, 'output_voltage', Decimal('0')),
        "created_at": getattr(product, 'created_at', None),
        "updated_at": getattr(product, 'updated_at', None),
        "product_name": str(getattr(product, 'name', '')),
        "bom": None,
    }
    # Ensure Decimal types are correct
    for key in ['price', 'frequency', 'efficiency', 'input_voltage', 'output_voltage']:
        if not isinstance(product_dict[key], Decimal):
            product_dict[key] = Decimal(str(product_dict[key])) if product_dict[key] else Decimal('0')
    
    return ProductResponse.model_validate(product_dict)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update product"""
    service = ProductService(db)
    product = await service.update_product(product_id, **data.model_dump(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Query BOM for this product to avoid lazy loading - query only specific columns
    bom_result = await db.execute(
        select(BillOfMaterial.id)
        .where(BillOfMaterial.product_id == product_id)
        .limit(1)
    )
    bom_row = bom_result.first()
    bom_id = bom_row[0] if bom_row else None
    
    # Convert to Pydantic model explicitly to avoid lazy loading during serialization
    # Access all attributes using getattr to avoid relationship access
    product_dict = {
        "id": int(getattr(product, 'id', 0)),
        "name": str(getattr(product, 'name', '')),
        "model_number": str(getattr(product, 'model_number', '')),
        "description": str(getattr(product, 'description', '')),
        "price": getattr(product, 'price', Decimal('0')),
        "inverter_type": getattr(product, 'inverter_type', None),
        "power_rating": int(getattr(product, 'power_rating', 0)),
        "frequency": getattr(product, 'frequency', Decimal('0')),
        "efficiency": getattr(product, 'efficiency', Decimal('0')),
        "surge_power": int(getattr(product, 'surge_power', 0)),
        "warranty_years": int(getattr(product, 'warranty_years', 0)),
        "input_voltage": getattr(product, 'input_voltage', Decimal('0')),
        "output_voltage": getattr(product, 'output_voltage', Decimal('0')),
        "created_at": getattr(product, 'created_at', None),
        "updated_at": getattr(product, 'updated_at', None),
        "product_name": str(getattr(product, 'name', '')),
        "bom": int(bom_id) if bom_id else None,
    }
    # Ensure Decimal types are correct
    for key in ['price', 'frequency', 'efficiency', 'input_voltage', 'output_voltage']:
        if not isinstance(product_dict[key], Decimal):
            product_dict[key] = Decimal(str(product_dict[key])) if product_dict[key] else Decimal('0')
    
    return ProductResponse.model_validate(product_dict)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete product"""
    service = ProductService(db)
    result = await service.delete_product(product_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

