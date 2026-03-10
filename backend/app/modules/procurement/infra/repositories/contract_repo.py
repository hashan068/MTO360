"""
Contract Repository
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.procurement import SupplierContract, ContractStatusEnum


class ContractRepository:
    """Repository for supplier contract data access"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, contract_data: dict) -> SupplierContract:
        """Create a new contract"""
        contract = SupplierContract(**contract_data)
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract
    
    async def get_by_id(self, contract_id: int, include_pricing: bool = False) -> Optional[SupplierContract]:
        """Get contract by ID"""
        query = select(SupplierContract).where(SupplierContract.id == contract_id)
        
        if include_pricing:
            query = query.options(joinedload(SupplierContract.pricing_items))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_contract_number(self, contract_number: str) -> Optional[SupplierContract]:
        """Get contract by contract number"""
        result = await self.db.execute(
            select(SupplierContract).where(SupplierContract.contract_number == contract_number)
        )
        return result.scalar_one_or_none()
    
    async def list_contracts(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[ContractStatusEnum] = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupplierContract]:
        """List contracts with filters"""
        query = select(SupplierContract)
        
        filters = []
        if supplier_id:
            filters.append(SupplierContract.supplier_id == supplier_id)
        if status:
            filters.append(SupplierContract.status == status)
        if active_only:
            filters.append(SupplierContract.status == ContractStatusEnum.ACTIVE)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(SupplierContract.start_date)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, contract_id: int, update_data: dict) -> Optional[SupplierContract]:
        """Update a contract"""
        contract = await self.get_by_id(contract_id)
        if not contract:
            return None
        
        for key, value in update_data.items():
            if hasattr(contract, key):
                setattr(contract, key, value)
        
        contract.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(contract)
        return contract
    
    async def delete(self, contract_id: int) -> bool:
        """Delete a contract"""
        contract = await self.get_by_id(contract_id)
        if not contract:
            return False
        
        await self.db.delete(contract)
        await self.db.commit()
        return True
    
    async def get_expiring_contracts(self, days: int = 90) -> List[SupplierContract]:
        """Get contracts expiring within specified days"""
        today = date.today()
        expiry_threshold = today + timedelta(days=days)
        
        result = await self.db.execute(
            select(SupplierContract).where(
                and_(
                    SupplierContract.status == ContractStatusEnum.ACTIVE,
                    SupplierContract.end_date >= today,
                    SupplierContract.end_date <= expiry_threshold
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_active_contract_for_supplier(self, supplier_id: int) -> Optional[SupplierContract]:
        """Get active contract for a supplier"""
        result = await self.db.execute(
            select(SupplierContract).where(
                and_(
                    SupplierContract.supplier_id == supplier_id,
                    SupplierContract.status == ContractStatusEnum.ACTIVE
                )
            ).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def generate_contract_number(self) -> str:
        """Generate next contract number"""
        # Get the latest contract number
        result = await self.db.execute(
            select(SupplierContract.contract_number)
            .where(SupplierContract.contract_number.like('CNT-%'))
            .order_by(desc(SupplierContract.contract_number))
            .limit(1)
        )
        
        latest = result.scalar_one_or_none()
        
        if not latest:
            return f"CNT-{datetime.now().year}-0001"
        
        try:
            parts = latest.split('-')
            year = parts[1]
            number = int(parts[2])
            
            current_year = str(datetime.now().year)
            if year != current_year:
                return f"CNT-{current_year}-0001"
            else:
                return f"CNT-{current_year}-{number + 1:04d}"
        except:
            return f"CNT-{datetime.now().year}-{datetime.now().timestamp():.0f}"
