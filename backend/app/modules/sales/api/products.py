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
    product_ids = [p.id for p in products]
    bom_map = {}
    if product_ids:
        result = await db.execute(
            select(BillOfMaterial.id, BillOfMaterial.product_id)
            .where(BillOfMaterial.product_id.in_(product_ids))
        )
        boms = result.all()
        for bom_id, bom_product_id in boms:
            if bom_product_id not in bom_map:
                bom_map[bom_product_id] = bom_id
    
    # Build response list
    response_products = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "model_number": product.model_number,
            "description": product.description,
            "price": product.price,
            "inverter_type": product.inverter_type,
            "power_rating": product.power_rating,
            "frequency": product.frequency,
            "efficiency": product.efficiency,
            "surge_power": product.surge_power,
            "warranty_years": product.warranty_years,
            "input_voltage": product.input_voltage,
            "output_voltage": product.output_voltage,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "product_name": product.name,
            "bom": bom_map.get(product.id),
        }
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
    
    # Query BOM for this product to avoid lazy loading
    bom_result = await db.execute(
        select(BillOfMaterial.id)
        .where(BillOfMaterial.product_id == product_id)
        .limit(1)
    )
    bom_row = bom_result.first()
    bom_id = bom_row[0] if bom_row else None
    
    product_dict = {
        "id": product.id,
        "name": product.name,
        "model_number": product.model_number,
        "description": product.description,
        "price": product.price,
        "inverter_type": product.inverter_type,
        "power_rating": product.power_rating,
        "frequency": product.frequency,
        "efficiency": product.efficiency,
        "surge_power": product.surge_power,
        "warranty_years": product.warranty_years,
        "input_voltage": product.input_voltage,
        "output_voltage": product.output_voltage,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "product_name": product.name,
        "bom": bom_id,
    }
    
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
    
    product_dict = {
        "id": product.id,
        "name": product.name,
        "model_number": product.model_number,
        "description": product.description,
        "price": product.price,
        "inverter_type": product.inverter_type,
        "power_rating": product.power_rating,
        "frequency": product.frequency,
        "efficiency": product.efficiency,
        "surge_power": product.surge_power,
        "warranty_years": product.warranty_years,
        "input_voltage": product.input_voltage,
        "output_voltage": product.output_voltage,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "product_name": product.name,
        "bom": None,
    }
    
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
    
    # Query BOM for this product to avoid lazy loading
    bom_result = await db.execute(
        select(BillOfMaterial.id)
        .where(BillOfMaterial.product_id == product_id)
        .limit(1)
    )
    bom_row = bom_result.first()
    bom_id = bom_row[0] if bom_row else None
    
    product_dict = {
        "id": product.id,
        "name": product.name,
        "model_number": product.model_number,
        "description": product.description,
        "price": product.price,
        "inverter_type": product.inverter_type,
        "power_rating": product.power_rating,
        "frequency": product.frequency,
        "efficiency": product.efficiency,
        "surge_power": product.surge_power,
        "warranty_years": product.warranty_years,
        "input_voltage": product.input_voltage,
        "output_voltage": product.output_voltage,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "product_name": product.name,
        "bom": bom_id,
    }
    
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

