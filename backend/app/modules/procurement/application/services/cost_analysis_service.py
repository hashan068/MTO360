"""
Cost Analysis Service - Price history, spend analysis, budget tracking
"""
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, extract

from app.models.procurement import (
    ComponentPriceHistory, ProcurementBudget,
    PriceChangeSourceEnum
)
from app.models.inventory import PurchaseOrder, Component, Category, Supplier


class CostAnalysisService:
    """Service for cost analysis and reporting"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_price_change(
        self,
        component_id: int,
        unit_price: Decimal,
        effective_date: date,
        price_change_source: PriceChangeSourceEnum,
        supplier_id: Optional[int] = None,
        purchase_order_id: Optional[int] = None,
        recorded_by: Optional[int] = None
    ) -> ComponentPriceHistory:
        """Record a price change for a component"""
        price_history = ComponentPriceHistory(
            component_id=component_id,
            supplier_id=supplier_id,
            unit_price=unit_price,
            effective_date=effective_date,
            price_change_source=price_change_source,
            purchase_order_id=purchase_order_id,
            recorded_by=recorded_by
        )
        
        self.db.add(price_history)
        await self.db.commit()
        await self.db.refresh(price_history)
        
        return price_history
    
    async def get_price_history(
        self,
        component_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        supplier_id: Optional[int] = None
    ) -> Dict:
        """
        Get price history for a component with trend analysis
        
        Args:
            component_id: Component ID
            start_date: Start date (default: 1 year ago)
            end_date: End date (default: today)
            supplier_id: Optional supplier filter
        
        Returns:
            Dict with history, trend, statistics
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        # Build query
        query = select(ComponentPriceHistory).where(
            and_(
                ComponentPriceHistory.component_id == component_id,
                ComponentPriceHistory.effective_date >= start_date,
                ComponentPriceHistory.effective_date <= end_date
            )
        )
        
        if supplier_id:
            query = query.where(ComponentPriceHistory.supplier_id == supplier_id)
        
        query = query.order_by(ComponentPriceHistory.effective_date)
        
        result = await self.db.execute(query)
        history = list(result.scalars().all())
        
        if not history:
            return {
                'component_id': component_id,
                'component_name': None,
                'history': [],
                'trend': 'no_data',
                'avg_price': Decimal("0"),
                'min_price': Decimal("0"),
                'max_price': Decimal("0"),
                'price_volatility': Decimal("0")
            }
        
        # Get component name
        component_result = await self.db.execute(
            select(Component.name).where(Component.id == component_id)
        )
        component_name = component_result.scalar_one_or_none()
        
        # Calculate statistics
        prices = [h.unit_price for h in history]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Calculate volatility (coefficient of variation)
        if avg_price > 0:
            std_dev = Decimal(str((sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5))
            price_volatility = (std_dev / avg_price) * 100
        else:
            price_volatility = Decimal("0")
        
        # Determine trend
        if len(history) >= 2:
            first_price = history[0].unit_price
            last_price = history[-1].unit_price
            price_change_pct = ((last_price - first_price) / first_price * 100) if first_price > 0 else Decimal("0")
            
            if price_change_pct > 5:
                trend = "increasing"
            elif price_change_pct < -5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Calculate price changes
        history_with_changes = []
        for i, record in enumerate(history):
            if i > 0:
                prev_price = history[i-1].unit_price
                change_pct = ((record.unit_price - prev_price) / prev_price * 100) if prev_price > 0 else Decimal("0")
            else:
                change_pct = Decimal("0")
            
            history_with_changes.append({
                'id': record.id,
                'effective_date': record.effective_date,
                'unit_price': record.unit_price,
                'supplier_id': record.supplier_id,
                'price_change_source': record.price_change_source,
                'price_change_pct': change_pct
            })
        
        return {
            'component_id': component_id,
            'component_name': component_name,
            'history': history_with_changes,
            'trend': trend,
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'price_volatility': price_volatility
        }
    
    async def analyze_spend(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "supplier"  # supplier, category, month
    ) -> Dict:
        """
        Analyze procurement spend
        
        Args:
            start_date: Analysis start date
            end_date: Analysis end date
            group_by: Grouping criteria (supplier, category, month)
        
        Returns:
            Spend analysis with breakdowns
        """
        # Get total spend
        total_result = await self.db.execute(
            select(func.coalesce(func.sum(PurchaseOrder.total_price), 0)).where(
                and_(
                    PurchaseOrder.created_at >= start_date,
                    PurchaseOrder.created_at <= end_date
                )
            )
        )
        total_spend = total_result.scalar()
        
        # Group by specified criteria
        breakdown = []
        
        if group_by == "supplier":
            # Spend by supplier
            query = (
                select(
                    Supplier.id,
                    Supplier.name,
                    func.sum(PurchaseOrder.total_price).label('spend'),
                    func.count(PurchaseOrder.id).label('order_count')
                )
                .join(Supplier, PurchaseOrder.supplier_id == Supplier.id)
                .where(
                    and_(
                        PurchaseOrder.created_at >= start_date,
                        PurchaseOrder.created_at <= end_date
                    )
                )
                .group_by(Supplier.id, Supplier.name)
                .order_by(desc('spend'))
            )
            
            result = await self.db.execute(query)
            rows = result.all()
            
            for row in rows:
                percentage = (Decimal(str(row.spend)) / Decimal(str(total_spend)) * 100) if total_spend > 0 else Decimal("0")
                avg_order = Decimal(str(row.spend)) / row.order_count if row.order_count > 0 else Decimal("0")
                
                breakdown.append({
                    'name': row.name,
                    'spend': Decimal(str(row.spend)),
                    'percentage': percentage,
                    'order_count': row.order_count,
                    'avg_order_value': avg_order
                })
        
        elif group_by == "category":
            # Spend by category (via components)
            query = (
                select(
                    Category.id,
                    Category.name,
                    func.sum(PurchaseOrder.total_price).label('spend'),
                    func.count(PurchaseOrder.id).label('order_count')
                )
                .join(Component, PurchaseOrder.purchase_requisition.has(component_id=Component.id))
                .join(Category, Component.category_id == Category.id)
                .where(
                    and_(
                        PurchaseOrder.created_at >= start_date,
                        PurchaseOrder.created_at <= end_date
                    )
                )
                .group_by(Category.id, Category.name)
                .order_by(desc('spend'))
            )
            
            # Note: This query is simplified and may need adjustment based on actual schema
            # For now, using a simpler approach
            breakdown = []  # Placeholder
        
        elif group_by == "month":
            # Spend by month
            query = (
                select(
                    func.date_trunc('month', PurchaseOrder.created_at).label('month'),
                    func.sum(PurchaseOrder.total_price).label('spend'),
                    func.count(PurchaseOrder.id).label('order_count')
                )
                .where(
                    and_(
                        PurchaseOrder.created_at >= start_date,
                        PurchaseOrder.created_at <= end_date
                    )
                )
                .group_by('month')
                .order_by('month')
            )
            
            result = await self.db.execute(query)
            rows = result.all()
            
            for row in rows:
                percentage = (Decimal(str(row.spend)) / Decimal(str(total_spend)) * 100) if total_spend > 0 else Decimal("0")
                avg_order = Decimal(str(row.spend)) / row.order_count if row.order_count > 0 else Decimal("0")
                
                breakdown.append({
                    'name': row.month.strftime('%Y-%m'),
                    'spend': Decimal(str(row.spend)),
                    'percentage': percentage,
                    'order_count': row.order_count,
                    'avg_order_value': avg_order
                })
        
        # Get top 10 suppliers for concentration analysis
        top_10_query = (
            select(
                Supplier.name,
                func.sum(PurchaseOrder.total_price).label('spend')
            )
            .join(Supplier, PurchaseOrder.supplier_id == Supplier.id)
            .where(
                and_(
                    PurchaseOrder.created_at >= start_date,
                    PurchaseOrder.created_at <= end_date
                )
            )
            .group_by(Supplier.name)
            .order_by(desc('spend'))
            .limit(10)
        )
        
        top_10_result = await self.db.execute(top_10_query)
        top_10_rows = top_10_result.all()
        
        top_10_suppliers = []
        top_3_spend = Decimal("0")
        top_10_spend = Decimal("0")
        
        for idx, row in enumerate(top_10_rows):
            spend = Decimal(str(row.spend))
            percentage = (spend / Decimal(str(total_spend)) * 100) if total_spend > 0 else Decimal("0")
            
            top_10_suppliers.append({
                'name': row.name,
                'spend': spend,
                'percentage': percentage,
                'order_count': 0,  # Would need separate query
                'avg_order_value': Decimal("0")
            })
            
            if idx < 3:
                top_3_spend += spend
            top_10_spend += spend
        
        # Calculate concentration
        top_3_pct = (top_3_spend / Decimal(str(total_spend)) * 100) if total_spend > 0 else Decimal("0")
        top_10_pct = (top_10_spend / Decimal(str(total_spend)) * 100) if total_spend > 0 else Decimal("0")
        
        return {
            'total_spend': Decimal(str(total_spend)),
            'period_start': start_date,
            'period_end': end_date,
            'breakdown': breakdown,
            'top_10_suppliers': top_10_suppliers,
            'concentration': {
                'top_3_pct': top_3_pct,
                'top_10_pct': top_10_pct
            }
        }
    
    async def get_or_create_budget(
        self,
        fiscal_year: int,
        category_id: Optional[int],
        budgeted_amount: Decimal
    ) -> ProcurementBudget:
        """Create or update procurement budget"""
        # Check if exists
        query = select(ProcurementBudget).where(
            and_(
                ProcurementBudget.fiscal_year == fiscal_year,
                ProcurementBudget.category_id == category_id
            )
        )
        
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.budgeted_amount = budgeted_amount
            existing.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            budget = ProcurementBudget(
                fiscal_year=fiscal_year,
                category_id=category_id,
                budgeted_amount=budgeted_amount,
                actual_spend=Decimal("0"),
                variance=budgeted_amount,
                variance_pct=Decimal("0")
            )
            self.db.add(budget)
            await self.db.commit()
            await self.db.refresh(budget)
            return budget
    
    async def update_budget_actuals(self, fiscal_year: int) -> List[ProcurementBudget]:
        """Update actual spend and variance for budgets"""
        # Get all budgets for fiscal year
        budgets_result = await self.db.execute(
            select(ProcurementBudget).where(
                ProcurementBudget.fiscal_year == fiscal_year
            )
        )
        budgets = list(budgets_result.scalars().all())
        
        # Calculate actuals for each budget
        for budget in budgets:
            # Get actual spend for the year
            query = select(func.coalesce(func.sum(PurchaseOrder.total_price), 0))
            query = query.where(
                extract('year', PurchaseOrder.created_at) == fiscal_year
            )
            
            # Filter by category if specified
            if budget.category_id:
                # Would need to join through components - simplified for now
                pass
            
            result = await self.db.execute(query)
            actual_spend = Decimal(str(result.scalar()))
            
            # Update budget
            budget.actual_spend = actual_spend
            budget.variance = budget.budgeted_amount - actual_spend
            budget.variance_pct = (budget.variance / budget.budgeted_amount * 100) if budget.budgeted_amount > 0 else Decimal("0")
            budget.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return budgets
    
    async def get_budget_tracking(self, fiscal_year: int) -> Dict:
        """Get budget tracking summary"""
        budgets = await self.update_budget_actuals(fiscal_year)
        
        overall_budget = sum(b.budgeted_amount for b in budgets)
        overall_actual = sum(b.actual_spend for b in budgets)
        overall_consumed_pct = (overall_actual / overall_budget * 100) if overall_budget > 0 else Decimal("0")
        
        # Add status to each budget
        budget_list = []
        for budget in budgets:
            consumed_pct = (budget.actual_spend / budget.budgeted_amount * 100) if budget.budgeted_amount > 0 else Decimal("0")
            
            if consumed_pct >= 100:
                status = "over_budget"
            elif consumed_pct >= 90:
                status = "at_risk"
            else:
                status = "on_track"
            
            budget_list.append({
                **budget.__dict__,
                'consumed_pct': consumed_pct,
                'status': status
            })
        
        return {
            'fiscal_year': fiscal_year,
            'budgets': budget_list,
            'overall_total_budget': overall_budget,
            'overall_total_actual': overall_actual,
            'overall_consumed_pct': overall_consumed_pct
        }
