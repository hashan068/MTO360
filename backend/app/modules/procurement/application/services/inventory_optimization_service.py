"""
Inventory Optimization Service - ROP, EOQ, ABC Analysis
"""
from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.procurement import (
    ComponentInventoryPolicy, DemandForecast, 
    ABCClassificationEnum, ForecastMethodEnum
)
from app.models.inventory import Component, PurchaseRequisition, StatusEnum


class InventoryOptimizationService:
    """Service for inventory optimization calculations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_reorder_point(
        self,
        component_id: int,
        average_daily_demand: int,
        lead_time_days: int,
        service_level_z: Decimal = Decimal("1.65")  # 95% service level
    ) -> Dict:
        """
        Calculate Reorder Point (ROP)
        
        Formula: ROP = (Average Daily Demand × Lead Time) + Safety Stock
        Safety Stock = Z-score × σ × √(Lead Time)
        
        Args:
            component_id: Component ID
            average_daily_demand: Average daily demand
            lead_time_days: Lead time in days
            service_level_z: Z-score for desired service level (1.65 = 95%)
        
        Returns:
            Dict with ROP, safety_stock, and calculation details
        """
        # Calculate demand during lead time
        demand_during_lead_time = average_daily_demand * lead_time_days
        
        # Calculate standard deviation (simplified: 20% of average demand)
        std_deviation = Decimal(str(average_daily_demand * 0.2))
        
        # Calculate safety stock
        safety_stock = int(service_level_z * std_deviation * Decimal(str(math.sqrt(lead_time_days))))
        
        # Calculate ROP
        reorder_point = demand_during_lead_time + safety_stock
        
        return {
            'reorder_point': reorder_point,
            'safety_stock': safety_stock,
            'demand_during_lead_time': demand_during_lead_time,
            'service_level': '95%',
            'z_score': service_level_z
        }
    
    async def calculate_economic_order_quantity(
        self,
        annual_demand: int,
        ordering_cost: Decimal,
        unit_cost: Decimal,
        holding_cost_pct: Decimal = Decimal("25.00")
    ) -> Dict:
        """
        Calculate Economic Order Quantity (EOQ)
        
        Formula: EOQ = √((2 × D × S) / H)
        Where:
        - D = Annual demand
        - S = Ordering cost per order
        - H = Holding cost per unit per year
        
        Args:
            annual_demand: Annual demand in units
            ordering_cost: Cost to place one order
            unit_cost: Cost per unit
            holding_cost_pct: Holding cost as percentage of unit cost
        
        Returns:
            Dict with EOQ and cost analysis
        """
        # Calculate holding cost per unit per year
        holding_cost = unit_cost * (holding_cost_pct / 100)
        
        # Calculate EOQ
        if holding_cost == 0 or annual_demand == 0:
            eoq = 1
        else:
            eoq_calc = (2 * annual_demand * ordering_cost) / holding_cost
            eoq = int(math.sqrt(float(eoq_calc)))
        
        # Calculate total cost at EOQ
        number_of_orders = annual_demand / eoq if eoq > 0 else 0
        total_ordering_cost = number_of_orders * ordering_cost
        average_inventory = eoq / 2
        total_holding_cost = average_inventory * holding_cost
        total_cost = total_ordering_cost + total_holding_cost
        
        return {
            'economic_order_quantity': eoq,
            'number_of_orders_per_year': round(number_of_orders, 2),
            'total_ordering_cost': float(total_ordering_cost),
            'total_holding_cost': float(total_holding_cost),
            'total_annual_cost': float(total_cost),
            'average_inventory_level': int(average_inventory)
        }
    
    async def perform_abc_analysis(
        self,
        category_id: Optional[int] = None
    ) -> Dict:
        """
        Perform ABC Analysis on components
        
        Classifies components based on annual value:
        - A items: Top 80% of value (typically 20% of items)
        - B items: Next 15% of value (typically 30% of items)
        - C items: Remaining 5% of value (typically 50% of items)
        
        Args:
            category_id: Optional category filter
        
        Returns:
            Dict with classification results
        """
        # Get components with usage data
        query = select(Component)
        
        if category_id:
            query = query.where(Component.category_id == category_id)
        
        result = await self.db.execute(query)
        components = list(result.scalars().all())
        
        # Calculate annual value for each component
        component_values = []
        total_value = Decimal("0.00")
        
        for component in components:
            # Estimate annual usage (simplified: current quantity * 12)
            annual_usage = component.quantity * 12 if component.quantity > 0 else 0
            annual_value = Decimal(str(annual_usage)) * component.cost
            
            component_values.append({
                'component_id': component.id,
                'component_name': component.name,
                'annual_usage': annual_usage,
                'unit_cost': component.cost,
                'annual_value': annual_value
            })
            
            total_value += annual_value
        
        # Sort by annual value (descending)
        component_values.sort(key=lambda x: x['annual_value'], reverse=True)
        
        # Calculate cumulative values and classify
        cumulative_value = Decimal("0.00")
        classified_components = []
        
        for item in component_values:
            cumulative_value += item['annual_value']
            cumulative_pct = (cumulative_value / total_value * 100) if total_value > 0 else Decimal("0")
            
            # Classify based on cumulative percentage
            if cumulative_pct <= 80:
                classification = ABCClassificationEnum.A
            elif cumulative_pct <= 95:
                classification = ABCClassificationEnum.B
            else:
                classification = ABCClassificationEnum.C
            
            classified_components.append({
                **item,
                'cumulative_value': cumulative_value,
                'cumulative_percentage': cumulative_pct,
                'classification': classification
            })
        
        # Calculate summary by classification
        summary = {
            'A': {'count': 0, 'value': Decimal("0"), 'percentage': Decimal("0")},
            'B': {'count': 0, 'value': Decimal("0"), 'percentage': Decimal("0")},
            'C': {'count': 0, 'value': Decimal("0"), 'percentage': Decimal("0")}
        }
        
        for item in classified_components:
            cls = item['classification'].value
            summary[cls]['count'] += 1
            summary[cls]['value'] += item['annual_value']
        
        for cls in summary:
            if total_value > 0:
                summary[cls]['percentage'] = (summary[cls]['value'] / total_value * 100)
        
        return {
            'total_components': len(components),
            'total_value': total_value,
            'classifications': summary,
            'components': classified_components
        }
    
    async def create_or_update_inventory_policy(
        self,
        component_id: int,
        average_monthly_demand: int,
        lead_time_days: int,
        ordering_cost: Decimal = Decimal("50.00"),
        holding_cost_pct: Decimal = Decimal("25.00"),
        auto_pr_enabled: bool = True,
        updated_by: Optional[int] = None
    ) -> ComponentInventoryPolicy:
        """
        Create or update inventory policy with calculated values
        
        Calculates ROP, Safety Stock, EOQ, and ABC classification
        """
        # Get component
        result = await self.db.execute(
            select(Component).where(Component.id == component_id)
        )
        component = result.scalar_one_or_none()
        
        if not component:
            raise ValueError(f"Component {component_id} not found")
        
        # Calculate metrics
        average_daily_demand = int(average_monthly_demand / 30)
        annual_demand = average_monthly_demand * 12
        
        # ROP calculation
        rop_result = await self.calculate_reorder_point(
            component_id,
            average_daily_demand,
            lead_time_days
        )
        
        # EOQ calculation
        eoq_result = await self.calculate_economic_order_quantity(
            annual_demand,
            ordering_cost,
            component.cost,
            holding_cost_pct
        )
        
        # ABC classification (simplified: based on annual value)
        annual_value = component.cost * Decimal(str(annual_demand))
        
        if annual_value > 100000:
            abc_classification = ABCClassificationEnum.A
        elif annual_value > 10000:
            abc_classification = ABCClassificationEnum.B
        else:
            abc_classification = ABCClassificationEnum.C
        
        # Check if policy exists
        result = await self.db.execute(
            select(ComponentInventoryPolicy).where(
                ComponentInventoryPolicy.component_id == component_id
            )
        )
        existing_policy = result.scalar_one_or_none()
        
        if existing_policy:
            # Update existing
            existing_policy.reorder_point = rop_result['reorder_point']
            existing_policy.safety_stock = rop_result['safety_stock']
            existing_policy.economic_order_quantity = eoq_result['economic_order_quantity']
            existing_policy.abc_classification = abc_classification
            existing_policy.average_monthly_demand = average_monthly_demand
            existing_policy.lead_time_days = lead_time_days
            existing_policy.ordering_cost = ordering_cost
            existing_policy.holding_cost_pct = holding_cost_pct
            existing_policy.auto_pr_enabled = auto_pr_enabled
            existing_policy.updated_by = updated_by
            existing_policy.last_calculated_at = datetime.utcnow()
            existing_policy.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(existing_policy)
            return existing_policy
        else:
            # Create new
            policy = ComponentInventoryPolicy(
                component_id=component_id,
                reorder_point=rop_result['reorder_point'],
                safety_stock=rop_result['safety_stock'],
                economic_order_quantity=eoq_result['economic_order_quantity'],
                abc_classification=abc_classification,
                average_monthly_demand=average_monthly_demand,
                lead_time_days=lead_time_days,
                ordering_cost=ordering_cost,
                holding_cost_pct=holding_cost_pct,
                auto_pr_enabled=auto_pr_enabled,
                updated_by=updated_by,
                last_calculated_at=datetime.utcnow()
            )
            
            self.db.add(policy)
            await self.db.commit()
            await self.db.refresh(policy)
            return policy
    
    async def get_components_below_rop(self) -> List[Dict]:
        """
        Get components that are below reorder point
        
        Returns components that need replenishment
        """
        # Query components with inventory policies
        query = (
            select(Component, ComponentInventoryPolicy)
            .join(ComponentInventoryPolicy, Component.id == ComponentInventoryPolicy.component_id)
            .where(
                and_(
                    Component.quantity < ComponentInventoryPolicy.reorder_point,
                    ComponentInventoryPolicy.auto_pr_enabled == True
                )
            )
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        below_rop_items = []
        
        for component, policy in rows:
            stock_deficit = policy.reorder_point - component.quantity
            
            # Check if there's a pending PR
            pr_result = await self.db.execute(
                select(PurchaseRequisition).where(
                    and_(
                        PurchaseRequisition.component_id == component.id,
                        PurchaseRequisition.status.in_([StatusEnum.PENDING, StatusEnum.APPROVED])
                    )
                )
            )
            has_pending_pr = pr_result.scalar_one_or_none() is not None
            
            # Calculate priority
            if component.quantity <= policy.safety_stock:
                priority = "high"
            elif component.quantity <= (policy.reorder_point * 0.8):
                priority = "medium"
            else:
                priority = "low"
            
            below_rop_items.append({
                'component_id': component.id,
                'component_name': component.name,
                'current_stock': component.quantity,
                'reorder_point': policy.reorder_point,
                'safety_stock': policy.safety_stock,
                'recommended_order_qty': policy.economic_order_quantity,
                'priority': priority,
                'has_pending_pr': has_pending_pr,
                'stock_deficit': stock_deficit
            })
        
        return below_rop_items
