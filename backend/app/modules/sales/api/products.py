"""
Product API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import ProductCreate, ProductUpdate, ProductResponse
from app.modules.sales.application.services.product_service import ProductService

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
    # Add product_name and bom fields for response
    for product in products:
        product.product_name = product.name
        # Get BOM if exists
        if product.bill_of_materials:
            product.bom = product.bill_of_materials[0].id if product.bill_of_materials else None
    return products


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
    product.product_name = product.name
    if product.bill_of_materials:
        product.bom = product.bill_of_materials[0].id if product.bill_of_materials else None
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new product"""
    service = ProductService(db)
    product = await service.create_product(**data.model_dump())
    product.product_name = product.name
    return product


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
    product.product_name = product.name
    return product


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

