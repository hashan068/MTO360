"""
Contract Management API endpoints
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.procurement import (
    SupplierContractCreate,
    SupplierContractResponse,
    SupplierContractUpdate,
)
from app.models.procurement import ContractStatusEnum
from app.modules.procurement.application.services.contract_service import ContractService


router = APIRouter(prefix="/api/v1/procurement/contracts", tags=["Contract Management"])


@router.post("", response_model=SupplierContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    data: SupplierContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Create a new supplier contract with pricing"""
    service = ContractService(db)
    
    try:
        contract = await service.create_contract(
            supplier_id=data.supplier_id,
            start_date=data.start_date,
            end_date=data.end_date,
            payment_terms=data.payment_terms,
            pricing_items=[p.dict() for p in data.pricing],
            volume_discounts=[v.dict() for v in data.volume_discounts] if data.volume_discounts else None,
            auto_renew=data.auto_renew,
            renewal_notice_days=data.renewal_notice_days,
            contract_file_url=data.contract_file_url,
            created_by=current_user_id
        )
        return contract
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating contract: {str(e)}"
        )


@router.get("", response_model=List[SupplierContractResponse])
async def list_contracts(
    supplier_id: Optional[int] = None,
    status_filter: Optional[ContractStatusEnum] = Query(None, alias="status"),
    active_only: bool = False,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List contracts with filters"""
    service = ContractService(db)
    contracts = await service.list_contracts(supplier_id, status_filter, active_only, limit, offset)
    return contracts


@router.get("/expiring", response_model=List[SupplierContractResponse])
async def get_expiring_contracts(
    days: int = Query(90, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get contracts expiring within specified days"""
    service = ContractService(db)
    contracts = await service.get_expiring_contracts(days)
    return contracts


@router.post("/{contract_id}/activate", response_model=SupplierContractResponse)
async def activate_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Activate a contract (requires approval)"""
    service = ContractService(db)
    
    try:
        contract = await service.activate_contract(contract_id, current_user_id)
        return contract
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{contract_id}/price", response_model=dict)
async def get_contract_price(
    contract_id: int,
    component_id: int,
    quantity: int = Query(..., gt=0),
    reference_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get contract price for a component with volume discount
    
    Returns pricing details including discounts
    """
    service = ContractService(db)
    
    # Get contract to find supplier_id
    contract = await service.contract_repo.get_by_id(contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    price_info = await service.get_contract_price(
        contract.supplier_id,
        component_id,
        quantity,
        reference_date
    )
    
    if not price_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pricing found for this component in the contract"
        )
    
    return price_info


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_contract(
    contract_id: int,
    reason: str = Query(..., min_length=10),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Cancel a contract"""
    service = ContractService(db)
    
    try:
        await service.cancel_contract(contract_id, reason, current_user_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
