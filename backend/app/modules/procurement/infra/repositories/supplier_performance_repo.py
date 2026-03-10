"""
Supplier Performance Repository
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.procurement import SupplierPerformance
from app.models.inventory import Supplier


class SupplierPerformanceRepository:
    """Repository for supplier performance data access"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, performance_data: dict) -> SupplierPerformance:
        """Create a new supplier performance record"""
        performance = SupplierPerformance(**performance_data)
        self.db.add(performance)
        await self.db.commit()
        await self.db.refresh(performance)
        return performance
    
    async def get_by_id(self, performance_id: int) -> Optional[SupplierPerformance]:
        """Get performance record by ID"""
        result = await self.db.execute(
            select(SupplierPerformance).where(SupplierPerformance.id == performance_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_supplier_and_period(
        self, 
        supplier_id: int, 
        period: date
    ) -> Optional[SupplierPerformance]:
        """Get performance record for a specific supplier and period"""
        result = await self.db.execute(
            select(SupplierPerformance).where(
                and_(
                    SupplierPerformance.supplier_id == supplier_id,
                    SupplierPerformance.period == period
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_supplier_performance_history(
        self,
        supplier_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 12
    ) -> List[SupplierPerformance]:
        """
        Get performance history for a supplier
        
        Args:
            supplier_id: Supplier ID
            start_date: Start date filter (default: 6 months ago)
            end_date: End date filter (default: today)
            limit: Maximum records to return (default: 12 months)
        """
        if not start_date:
            start_date = date.today().replace(day=1) - timedelta(days=180)
        if not end_date:
            end_date = date.today()
        
        result = await self.db.execute(
            select(SupplierPerformance)
            .where(
                and_(
                    SupplierPerformance.supplier_id == supplier_id,
                    SupplierPerformance.period >= start_date,
                    SupplierPerformance.period <= end_date
                )
            )
            .order_by(desc(SupplierPerformance.period))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_latest_by_supplier(self, supplier_id: int) -> Optional[SupplierPerformance]:
        """Get the most recent performance record for a supplier"""
        result = await self.db.execute(
            select(SupplierPerformance)
            .where(SupplierPerformance.supplier_id == supplier_id)
            .order_by(desc(SupplierPerformance.period))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_supplier_rankings(
        self,
        category_id: Optional[int] = None,
        limit: int = 10
    ) -> List[dict]:
        """
        Get supplier rankings by overall score
        
        Returns list of dicts with supplier info and latest performance
        """
        # Build query to get latest performance for each supplier
        subquery = (
            select(
                SupplierPerformance.supplier_id,
                func.max(SupplierPerformance.period).label('latest_period')
            )
            .group_by(SupplierPerformance.supplier_id)
            .subquery()
        )
        
        query = (
            select(
                Supplier.id.label('supplier_id'),
                Supplier.name.label('supplier_name'),
                SupplierPerformance.overall_score,
                SupplierPerformance.on_time_delivery_rate,
                SupplierPerformance.quality_rating,
                SupplierPerformance.price_competitiveness_score,
                SupplierPerformance.total_spend,
                SupplierPerformance.period
            )
            .join(
                subquery,
                and_(
                    Supplier.id == subquery.c.supplier_id
                )
            )
            .join(
                SupplierPerformance,
                and_(
                    SupplierPerformance.supplier_id == subquery.c.supplier_id,
                    SupplierPerformance.period == subquery.c.latest_period
                )
            )
            .where(Supplier.is_active == True)
            .order_by(desc(SupplierPerformance.overall_score))
            .limit(limit)
        )
        
        # TODO: Add category filter if category_id provided
        # This would require joining through components
        
        result = await self.db.execute(query)
        rows = result.all()
        
        rankings = []
        for idx, row in enumerate(rows, start=1):
            rankings.append({
                'rank': idx,
                'supplier_id': row.supplier_id,
                'supplier_name': row.supplier_name,
                'overall_score': row.overall_score,
                'on_time_delivery_rate': row.on_time_delivery_rate,
                'quality_rating': row.quality_rating,
                'price_competitiveness_score': row.price_competitiveness_score,
                'total_spend': row.total_spend,
                'period': row.period
            })
        
        return rankings
    
    async def get_preferred_suppliers(
        self,
        category_id: Optional[int] = None,
        min_score: Decimal = Decimal("75.00")
    ) -> List[dict]:
        """
        Get preferred suppliers (score >= min_score)
        
        Args:
            category_id: Filter by component category
            min_score: Minimum overall score to be considered preferred (default: 75)
        """
        # Get latest performance for each supplier with score >= min_score
        subquery = (
            select(
                SupplierPerformance.supplier_id,
                func.max(SupplierPerformance.period).label('latest_period')
            )
            .group_by(SupplierPerformance.supplier_id)
            .subquery()
        )
        
        query = (
            select(
                Supplier.id.label('supplier_id'),
                Supplier.name.label('supplier_name'),
                SupplierPerformance.overall_score
            )
            .join(
                subquery,
                Supplier.id == subquery.c.supplier_id
            )
            .join(
                SupplierPerformance,
                and_(
                    SupplierPerformance.supplier_id == subquery.c.supplier_id,
                    SupplierPerformance.period == subquery.c.latest_period
                )
            )
            .where(
                and_(
                    Supplier.is_active == True,
                    SupplierPerformance.overall_score >= min_score
                )
            )
            .order_by(desc(SupplierPerformance.overall_score))
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                'supplier_id': row.supplier_id,
                'supplier_name': row.supplier_name,
                'overall_score': row.overall_score,
                'is_preferred': True
            }
            for row in rows
        ]
    
    async def update(
        self, 
        performance_id: int, 
        update_data: dict
    ) -> Optional[SupplierPerformance]:
        """Update an existing performance record"""
        performance = await self.get_by_id(performance_id)
        if not performance:
            return None
        
        for key, value in update_data.items():
            if hasattr(performance, key):
                setattr(performance, key, value)
        
        performance.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(performance)
        return performance
    
    async def delete(self, performance_id: int) -> bool:
        """Delete a performance record"""
        performance = await self.get_by_id(performance_id)
        if not performance:
            return False
        
        await self.db.delete(performance)
        await self.db.commit()
        return True
    
    async def get_all_active_suppliers(self) -> List[Supplier]:
        """Get all active suppliers for batch performance calculation"""
        result = await self.db.execute(
            select(Supplier).where(Supplier.is_active == True)
        )
        return list(result.scalars().all())
