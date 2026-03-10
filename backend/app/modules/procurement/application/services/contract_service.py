"""
Contract Service - Contract lifecycle and pricing management
"""
from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.procurement import (
    SupplierContract, ContractPricing, ContractStatusEnum
)
from app.modules.procurement.infra.repositories.contract_repo import ContractRepository


class ContractService:
    """Service for contract management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contract_repo = ContractRepository(db)
    
    async def create_contract(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date,
        payment_terms: str,
        pricing_items: List[Dict],
        volume_discounts: Optional[List[Dict]] = None,
        auto_renew: bool = False,
        renewal_notice_days: int = 90,
        contract_file_url: Optional[str] = None,
        created_by: int = None
    ) -> SupplierContract:
        """
        Create a new supplier contract
        
        Args:
            supplier_id: Supplier ID
            start_date: Contract start date
            end_date: Contract end date
            payment_terms: Payment terms (e.g., "Net 30")
            pricing_items: List of pricing items for components
            volume_discounts: Optional volume discount tiers
            auto_renew: Auto-renew flag
            renewal_notice_days: Days before expiry to send renewal notice
            contract_file_url: URL to contract document
            created_by: User ID creating contract
        
        Returns:
            Created contract
        """
        # Generate contract number
        contract_number = await self.contract_repo.generate_contract_number()
        
        # Create contract
        contract_data = {
            'contract_number': contract_number,
            'supplier_id': supplier_id,
            'start_date': start_date,
            'end_date': end_date,
            'payment_terms': payment_terms,
            'volume_discounts': volume_discounts,
            'status': ContractStatusEnum.DRAFT,
            'auto_renew': auto_renew,
            'renewal_notice_days': renewal_notice_days,
            'contract_file_url': contract_file_url,
            'created_by': created_by
        }
        
        contract = await self.contract_repo.create(contract_data)
        
        # Create pricing items
        for item in pricing_items:
            pricing = ContractPricing(
                contract_id=contract.id,
                component_id=item['component_id'],
                unit_price=item['unit_price'],
                minimum_order_quantity=item.get('minimum_order_quantity', 1),
                lead_time_days=item['lead_time_days'],
                effective_from=item.get('effective_from'),
                effective_to=item.get('effective_to'),
                is_active=True
            )
            self.db.add(pricing)
        
        await self.db.commit()
        await self.db.refresh(contract)
        
        return contract
    
    async def activate_contract(self, contract_id: int, approved_by: int) -> SupplierContract:
        """Activate a contract"""
        contract = await self.contract_repo.get_by_id(contract_id)
        
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        if contract.status != ContractStatusEnum.DRAFT:
            raise ValueError(f"Can only activate contracts in DRAFT status. Current: {contract.status}")
        
        update_data = {
            'status': ContractStatusEnum.ACTIVE,
            'approved_by': approved_by,
            'approved_at': datetime.utcnow()
        }
        
        return await self.contract_repo.update(contract_id, update_data)
    
    async def get_contract_price(
        self,
        supplier_id: int,
        component_id: int,
        quantity: int,
        reference_date: Optional[date] = None
    ) -> Optional[Dict]:
        """
        Get contract price for a component, including volume discounts
        
        Args:
            supplier_id: Supplier ID
            component_id: Component ID
            quantity: Order quantity
            reference_date: Date to check contract validity (default: today)
        
        Returns:
            Dict with price, discount, final_price, lead_time
        """
        if not reference_date:
            reference_date = date.today()
        
        # Get active contract
        contract = await self.contract_repo.get_active_contract_for_supplier(supplier_id)
        
        if not contract:
            return None
        
        # Check if contract is valid for the reference date
        if not (contract.start_date <= reference_date <= contract.end_date):
            return None
        
        # Get pricing for component
        result = await self.db.execute(
            select(ContractPricing).where(
                and_(
                    ContractPricing.contract_id == contract.id,
                    ContractPricing.component_id == component_id,
                    ContractPricing.is_active == True,
                    or_(
                        ContractPricing.effective_from == None,
                        ContractPricing.effective_from <= reference_date
                    ),
                    or_(
                        ContractPricing.effective_to == None,
                        ContractPricing.effective_to >= reference_date
                    )
                )
            )
        )
        
        pricing = result.scalar_one_or_none()
        
        if not pricing:
            return None
        
        # Calculate volume discount
        discount_pct = self.calculate_volume_discount(contract.volume_discounts, quantity)
        
        # Calculate final price
        base_price = pricing.unit_price
        discount_amount = base_price * (discount_pct / 100)
        final_price = base_price - discount_amount
        
        return {
            'contract_id': contract.id,
            'contract_number': contract.contract_number,
            'base_unit_price': base_price,
            'discount_percentage': discount_pct,
            'discount_amount': discount_amount,
            'final_unit_price': final_price,
            'total_price': final_price * quantity,
            'lead_time_days': pricing.lead_time_days,
            'minimum_order_quantity': pricing.minimum_order_quantity,
            'payment_terms': contract.payment_terms
        }
    
    def calculate_volume_discount(
        self,
        volume_discounts: Optional[List[Dict]],
        quantity: int
    ) -> Decimal:
        """
        Calculate volume discount percentage for given quantity
        
        Args:
            volume_discounts: List of discount tiers
            quantity: Order quantity
        
        Returns:
            Discount percentage
        """
        if not volume_discounts:
            return Decimal("0.00")
        
        # Find applicable tier
        applicable_discount = Decimal("0.00")
        
        for tier in volume_discounts:
            min_qty = tier['min_qty']
            max_qty = tier.get('max_qty')
            
            if quantity >= min_qty:
                if max_qty is None or quantity <= max_qty:
                    applicable_discount = Decimal(str(tier['discount_pct']))
                    break
        
        return applicable_discount
    
    async def get_expiring_contracts(self, days: int = 90) -> List[SupplierContract]:
        """Get contracts expiring soon"""
        return await self.contract_repo.get_expiring_contracts(days)
    
    async def cancel_contract(
        self,
        contract_id: int,
        reason: str,
        cancelled_by: int
    ) -> SupplierContract:
        """Cancel a contract"""
        contract = await self.contract_repo.get_by_id(contract_id)
        
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        if contract.status == ContractStatusEnum.CANCELLED:
            raise ValueError("Contract is already cancelled")
        
        update_data = {
            'status': ContractStatusEnum.CANCELLED,
            'cancelled_at': datetime.utcnow(),
            'cancellation_reason': reason
        }
        
        return await self.contract_repo.update(contract_id, update_data)
    
    async def list_contracts(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[ContractStatusEnum] = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupplierContract]:
        """List contracts with filters"""
        return await self.contract_repo.list_contracts(supplier_id, status, active_only, limit, offset)
