"""
Supplier Performance Service
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from app.models.procurement import SupplierPerformance
from app.models.inventory import PurchaseOrder, PurchaseOrderStatusEnum
from app.modules.procurement.infra.repositories.supplier_performance_repo import SupplierPerformanceRepository


class SupplierPerformanceService:
    """Service for supplier performance management"""
    
    # Default weights for overall score calculation
    DEFAULT_WEIGHTS = {
        'on_time_delivery': Decimal("0.40"),  # 40%
        'quality': Decimal("0.30"),            # 30%
        'price_competitiveness': Decimal("0.20"),  # 20%
        'responsiveness': Decimal("0.10")      # 10%
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SupplierPerformanceRepository(db)
    
    async def calculate_supplier_performance(
        self,
        supplier_id: int,
        period: date,
        weights: Optional[dict] = None
    ) -> SupplierPerformance:
        """
        Calculate and save supplier performance for a given period
        
        Args:
            supplier_id: Supplier ID
            period: Period to calculate (should be first day of month)
            weights: Custom weights for score calculation (optional)
        
        Returns:
            SupplierPerformance record
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS
        
        # Ensure period is first day of month
        period = period.replace(day=1)
        
        # Define period range (full month)
        period_start = period
        if period.month == 12:
            period_end = period.replace(year=period.year + 1, month=1)
        else:
            period_end = period.replace(month=period.month + 1)
        
        # Calculate metrics
        on_time_delivery_rate = await self._calculate_on_time_delivery(
            supplier_id, period_start, period_end
        )
        quality_rating = await self._calculate_quality_rating(
            supplier_id, period_start, period_end
        )
        avg_lead_time = await self._calculate_average_lead_time(
            supplier_id, period_start, period_end
        )
        price_competitiveness = await self._calculate_price_competitiveness(
            supplier_id, period_start, period_end
        )
        total_spend = await self._calculate_total_spend(
            supplier_id, period_start, period_end
        )
        
        # Calculate overall weighted score
        overall_score = (
            (on_time_delivery_rate * weights['on_time_delivery']) +
            (quality_rating * weights['quality']) +
            (price_competitiveness * weights['price_competitiveness']) +
            (Decimal("100") * weights['responsiveness'])  # TODO: Calculate actual responsiveness
        )
        
        # Check if record exists for this supplier/period
        existing = await self.repo.get_by_supplier_and_period(supplier_id, period)
        
        performance_data = {
            'supplier_id': supplier_id,
            'period': period,
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating': quality_rating,
            'average_lead_time_days': avg_lead_time,
            'price_competitiveness_score': price_competitiveness,
            'total_spend': total_spend,
            'overall_score': overall_score
        }
        
        if existing:
            # Update existing record
            performance = await self.repo.update(existing.id, performance_data)
        else:
            # Create new record
            performance = await self.repo.create(performance_data)
        
        return performance
    
    async def _calculate_on_time_delivery(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """
        Calculate on-time delivery rate
        
        Returns percentage (0-100) of POs delivered on or before expected date
        """
        # Query POs for this supplier in the period that have been received
        result = await self.db.execute(
            select(
                func.count(PurchaseOrder.id).label('total_orders'),
                func.sum(
                    case(
                        (
                            and_(
                                PurchaseOrder.actual_delivery_date != None,
                                PurchaseOrder.expected_delivery_date >= PurchaseOrder.actual_delivery_date
                            ),
                            1
                        ),
                        else_=0
                    )
                ).label('on_time_orders')
            )
            .where(
                and_(
                    PurchaseOrder.supplier_id == supplier_id,
                    PurchaseOrder.created_at >= start_date,
                    PurchaseOrder.created_at < end_date,
                    PurchaseOrder.status == PurchaseOrderStatusEnum.RECEIVED
                )
            )
        )
        
        row = result.one()
        total = row.total_orders or 0
        on_time = row.on_time_orders or 0
        
        if total == 0:
            return Decimal("100.00")  # No orders = perfect score (neutral)
        
        return Decimal(str((on_time / total) * 100)).quantize(Decimal("0.01"))
    
    async def _calculate_quality_rating(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """
        Calculate quality rating from quality module
        
        TODO: Integrate with quality module to get actual defect rates
        For now, return default score
        """
        # This should query the quality module for:
        # - Inspection results
        # - Defect rates
        # - Non-conformance reports
        # And calculate a score based on defects per unit received
        
        # Placeholder: Return 100 (perfect quality)
        return Decimal("100.00")
    
    async def _calculate_average_lead_time(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date
    ) -> int:
        """
        Calculate average lead time in days
        
        Lead time = actual_delivery_date - PO creation date
        """
        result = await self.db.execute(
            select(
                func.avg(
                    func.extract('epoch', PurchaseOrder.actual_delivery_date - PurchaseOrder.created_at) / 86400
                ).label('avg_lead_time_days')
            )
            .where(
                and_(
                    PurchaseOrder.supplier_id == supplier_id,
                    PurchaseOrder.created_at >= start_date,
                    PurchaseOrder.created_at < end_date,
                    PurchaseOrder.status == PurchaseOrderStatusEnum.RECEIVED,
                    PurchaseOrder.actual_delivery_date != None
                )
            )
        )
        
        avg_days = result.scalar()
        return int(avg_days) if avg_days else 0
    
    async def _calculate_price_competitiveness(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """
        Calculate price competitiveness score
        
        TODO: Compare this supplier's prices against:
        - Market prices (if available)
        - Other suppliers for same components
        - Historical prices
        
        For now, return neutral score
        """
        # This should:
        # 1. Get components purchased from this supplier
        # 2. Compare prices with other suppliers for same components
        # 3. Calculate score: 100 = best price, lower = more expensive
        
        # Placeholder: Return 100 (competitive pricing)
        return Decimal("100.00")
    
    async def _calculate_total_spend(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """Calculate total spend with supplier in period"""
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(PurchaseOrder.total_price), 0).label('total_spend')
            )
            .where(
                and_(
                    PurchaseOrder.supplier_id == supplier_id,
                    PurchaseOrder.created_at >= start_date,
                    PurchaseOrder.created_at < end_date,
                    PurchaseOrder.status.in_([
                        PurchaseOrderStatusEnum.APPROVED,
                        PurchaseOrderStatusEnum.RECEIVED,
                        PurchaseOrderStatusEnum.INVOICED
                    ])
                )
            )
        )
        
        total = result.scalar()
        return Decimal(str(total or 0)).quantize(Decimal("0.01"))
    
    async def get_supplier_performance(
        self,
        supplier_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[SupplierPerformance]:
        """Get performance history for a supplier"""
        return await self.repo.get_supplier_performance_history(
            supplier_id,
            start_date,
            end_date
        )
    
    async def get_supplier_rankings(
        self,
        category_id: Optional[int] = None,
        limit: int = 10
    ) -> List[dict]:
        """Get supplier rankings by overall score"""
        return await self.repo.get_supplier_rankings(category_id, limit)
    
    async def get_preferred_suppliers(
        self,
        category_id: Optional[int] = None,
        min_score: Decimal = Decimal("75.00")
    ) -> List[dict]:
        """Get list of preferred suppliers (high performers)"""
        return await self.repo.get_preferred_suppliers(category_id, min_score)
    
    async def calculate_all_suppliers_performance(
        self,
        period: date,
        weights: Optional[dict] = None
    ) -> List[SupplierPerformance]:
        """
        Calculate performance for all active suppliers
        Used by monthly batch job
        """
        suppliers = await self.repo.get_all_active_suppliers()
        results = []
        
        for supplier in suppliers:
            try:
                performance = await self.calculate_supplier_performance(
                    supplier.id,
                    period,
                    weights
                )
                results.append(performance)
            except Exception as e:
                # Log error but continue with other suppliers
                print(f"Error calculating performance for supplier {supplier.id}: {e}")
                continue
        
        return results
