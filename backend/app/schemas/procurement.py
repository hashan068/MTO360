"""
Pydantic schemas for Procurement module
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Import enums from models
from app.models.procurement import (
    RFQStatusEnum,
    QuoteStatusEnum,
    ContractStatusEnum,
    ABCClassificationEnum,
    ForecastMethodEnum,
    PriceChangeSourceEnum,
)


# ============================================================================
# Phase 1: Supplier Performance Schemas
# ============================================================================

class SupplierPerformanceBase(BaseModel):
    """Base supplier performance schema"""
    supplier_id: int
    period: date
    on_time_delivery_rate: Decimal = Field(ge=0, le=100)
    quality_rating: Decimal = Field(ge=0, le=100)
    average_lead_time_days: int = Field(ge=0)
    price_competitiveness_score: Decimal = Field(ge=0, le=100)
    total_spend: Decimal = Field(ge=0)
    overall_score: Decimal = Field(ge=0, le=100)


class SupplierPerformanceCreate(BaseModel):
    """Create supplier performance record"""
    supplier_id: int
    period: date


class SupplierPerformanceResponse(SupplierPerformanceBase):
    """Response schema for supplier performance"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplierRankingResponse(BaseModel):
    """Supplier ranking response"""
    supplier_id: int
    supplier_name: str
    overall_score: Decimal
    rank: int
    on_time_delivery_rate: Decimal
    quality_rating: Decimal
    total_spend: Decimal
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Phase 2: RFQ & Quote Schemas
# ============================================================================

class ProcurementRFQBase(BaseModel):
    """Base RFQ schema"""
    component_id: int
    quantity: int = Field(gt=0)
    required_by_date: date
    closing_datetime: datetime
    specifications: Optional[str] = None
    internal_notes: Optional[str] = None


class ProcurementRFQCreate(ProcurementRFQBase):
    """Create RFQ schema"""
    supplier_ids: List[int] = Field(min_length=2, max_length=10)


class ProcurementRFQUpdate(BaseModel):
    """Update RFQ schema"""
    quantity: Optional[int] = Field(None, gt=0)
    required_by_date: Optional[date] = None
    closing_datetime: Optional[datetime] = None
    specifications: Optional[str] = None
    internal_notes: Optional[str] = None


class ProcurementRFQResponse(ProcurementRFQBase):
    """RFQ response"""
    id: int
    rfq_number: str
    status: RFQStatusEnum
    created_by: Optional[int] = None
    sent_at: Optional[datetime] = None
    awarded_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    component_name: Optional[str] = None
    quotes_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class SupplierQuoteBase(BaseModel):
    """Base quote schema"""
    rfq_id: int
    supplier_id: int
    unit_price: Decimal = Field(gt=0)
    lead_time_days: int = Field(gt=0)
    minimum_order_quantity: int = Field(ge=1)
    quote_valid_until: date
    notes: Optional[str] = None


class SupplierQuoteCreate(BaseModel):
    """Create quote schema"""
    supplier_id: int
    unit_price: Decimal = Field(gt=0)
    lead_time_days: int = Field(gt=0)
    minimum_order_quantity: int = Field(ge=1)
    quote_valid_until: date
    notes: Optional[str] = None


class SupplierQuoteUpdate(BaseModel):
    """Update quote schema"""
    unit_price: Optional[Decimal] = Field(None, gt=0)
    lead_time_days: Optional[int] = Field(None, gt=0)
    minimum_order_quantity: Optional[int] = Field(None, ge=1)
    quote_valid_until: Optional[date] = None
    notes: Optional[str] = None


class SupplierQuoteResponse(SupplierQuoteBase):
    """Quote response"""
    id: int
    status: QuoteStatusEnum
    is_awarded: bool
    submitted_at: Optional[datetime] = None
    awarded_at: Optional[datetime] = None
    award_justification: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    supplier_name: Optional[str] = None
    total_price: Optional[Decimal] = None
    delivery_date: Optional[date] = None
    
    class Config:
        from_attributes = True


class QuoteComparisonItem(BaseModel):
    """Quote comparison item for side-by-side view"""
    quote_id: int
    supplier_id: int
    supplier_name: str
    supplier_score: Optional[Decimal] = None
    unit_price: Decimal
    total_price: Decimal
    lead_time_days: int
    minimum_order_quantity: int
    delivery_date: date
    quote_valid_until: date
    is_best_price: bool = False
    is_best_lead_time: bool = False


class QuoteComparisonResponse(BaseModel):
    """Quote comparison response"""
    rfq: ProcurementRFQResponse
    quotes: List[QuoteComparisonItem]
    recommendation: Optional[str] = None


class RFQAwardRequest(BaseModel):
    """Award RFQ request"""
    quote_id: int
    justification: str = Field(min_length=10)


class RFQAwardResponse(BaseModel):
    """Award RFQ response"""
    rfq: ProcurementRFQResponse
    awarded_quote: SupplierQuoteResponse
    purchase_order_id: int


# ============================================================================
# Phase 3: Contract Schemas
# ============================================================================

class VolumeDiscountTier(BaseModel):
    """Volume discount tier"""
    min_qty: int = Field(ge=1)
    max_qty: Optional[int] = Field(None, ge=1)
    discount_pct: Decimal = Field(ge=0, le=100)
    
    @field_validator('max_qty')
    @classmethod
    def validate_max_qty(cls, v, info):
        if v is not None and 'min_qty' in info.data and v < info.data['min_qty']:
            raise ValueError('max_qty must be greater than min_qty')
        return v


class ContractPricingBase(BaseModel):
    """Base contract pricing schema"""
    component_id: int
    unit_price: Decimal = Field(gt=0)
    minimum_order_quantity: int = Field(ge=1)
    lead_time_days: int = Field(gt=0)
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: bool = True


class ContractPricingCreate(ContractPricingBase):
    """Create contract pricing"""
    pass


class ContractPricingResponse(ContractPricingBase):
    """Contract pricing response"""
    id: int
    contract_id: int
    component_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplierContractBase(BaseModel):
    """Base contract schema"""
    supplier_id: int
    start_date: date
    end_date: date
    payment_terms: str
    volume_discounts: Optional[List[VolumeDiscountTier]] = None
    auto_renew: bool = False
    renewal_notice_days: int = Field(ge=0, default=90)
    contract_file_url: Optional[str] = None


class SupplierContractCreate(SupplierContractBase):
    """Create contract schema"""
    pricing: List[ContractPricingCreate]
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class SupplierContractUpdate(BaseModel):
    """Update contract schema"""
    end_date: Optional[date] = None
    payment_terms: Optional[str] = None
    volume_discounts: Optional[List[VolumeDiscountTier]] = None
    auto_renew: Optional[bool] = None
    renewal_notice_days: Optional[int] = Field(None, ge=0)
    status: Optional[ContractStatusEnum] = None


class SupplierContractResponse(SupplierContractBase):
    """Contract response"""
    id: int
    contract_number: str
    status: ContractStatusEnum
    created_by: Optional[int] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    supplier_name: Optional[str] = None
    pricing_items_count: Optional[int] = None
    days_until_expiry: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Phase 4: Inventory Optimization Schemas
# ============================================================================

class ComponentInventoryPolicyBase(BaseModel):
    """Base inventory policy schema"""
    component_id: int
    reorder_point: int = Field(ge=0)
    safety_stock: int = Field(ge=0)
    economic_order_quantity: int = Field(ge=0)
    abc_classification: ABCClassificationEnum
    average_monthly_demand: int = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    ordering_cost: Decimal = Field(ge=0, default=Decimal("50.00"))
    holding_cost_pct: Decimal = Field(ge=0, le=100, default=Decimal("25.00"))
    auto_pr_enabled: bool = True


class ComponentInventoryPolicyCreate(BaseModel):
    """Create inventory policy"""
    component_id: int
    average_monthly_demand: int = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    ordering_cost: Decimal = Field(ge=0, default=Decimal("50.00"))
    holding_cost_pct: Decimal = Field(ge=0, le=100, default=Decimal("25.00"))
    auto_pr_enabled: bool = True


class ComponentInventoryPolicyUpdate(BaseModel):
    """Update inventory policy"""
    reorder_point: Optional[int] = Field(None, ge=0)
    safety_stock: Optional[int] = Field(None, ge=0)
    economic_order_quantity: Optional[int] = Field(None, ge=0)
    abc_classification: Optional[ABCClassificationEnum] = None
    average_monthly_demand: Optional[int] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    ordering_cost: Optional[Decimal] = Field(None, ge=0)
    holding_cost_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    auto_pr_enabled: Optional[bool] = None


class ComponentInventoryPolicyResponse(ComponentInventoryPolicyBase):
    """Inventory policy response"""
    id: int
    updated_by: Optional[int] = None
    last_calculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    component_name: Optional[str] = None
    current_stock: Optional[int] = None
    
    class Config:
        from_attributes = True


class ComponentBelowROPResponse(BaseModel):
    """Component below reorder point"""
    component_id: int
    component_name: str
    current_stock: int
    reorder_point: int
    safety_stock: int
    recommended_order_qty: int
    priority: str  # high, medium, low
    has_pending_pr: bool
    stock_deficit: int
    days_until_stockout: Optional[int] = None


class DemandForecastBase(BaseModel):
    """Base demand forecast schema"""
    component_id: int
    forecast_month: date
    forecasted_demand: int = Field(ge=0)
    actual_demand: Optional[int] = Field(None, ge=0)
    forecast_method: ForecastMethodEnum


class DemandForecastCreate(BaseModel):
    """Create demand forecast"""
    component_id: int
    forecast_month: date
    forecasted_demand: int = Field(ge=0)
    forecast_method: ForecastMethodEnum


class DemandForecastResponse(DemandForecastBase):
    """Demand forecast response"""
    id: int
    forecast_accuracy_mape: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ABCAnalysisComponentItem(BaseModel):
    """ABC analysis component item"""
    component_id: int
    component_name: str
    annual_usage: int
    unit_cost: Decimal
    annual_value: Decimal
    cumulative_value: Decimal
    cumulative_percentage: Decimal
    classification: ABCClassificationEnum


class ABCAnalysisResponse(BaseModel):
    """ABC analysis response"""
    total_components: int
    total_value: Decimal
    classifications: dict  # {A: {count, value, percentage}, B: {...}, C: {...}}
    components: List[ABCAnalysisComponentItem]


# ============================================================================
# Phase 5: Cost Analysis Schemas
# ============================================================================

class ComponentPriceHistoryBase(BaseModel):
    """Base price history schema"""
    component_id: int
    supplier_id: Optional[int] = None
    unit_price: Decimal = Field(gt=0)
    effective_date: date
    price_change_source: PriceChangeSourceEnum
    purchase_order_id: Optional[int] = None



class ComponentPriceHistoryResponse(ComponentPriceHistoryBase):
    """Price history response"""
    id: int
    recorded_by: Optional[int] = None
    created_at: datetime
    
    # Related data
    component_name: Optional[str] = None
    supplier_name: Optional[str] = None
    price_change_pct: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    """Price history analysis response"""
    component_id: int
    component_name: str
    history: List[ComponentPriceHistoryResponse]
    trend: str  # increasing, decreasing, stable
    avg_price: Decimal
    min_price: Decimal
    max_price: Decimal
    price_volatility: Decimal


class SpendAnalysisItem(BaseModel):
    """Spend analysis item"""
    name: str  # supplier, category, or month
    spend: Decimal
    percentage: Decimal
    order_count: int
    avg_order_value: Decimal


class SpendAnalysisResponse(BaseModel):
    """Spend analysis response"""
    total_spend: Decimal
    period_start: date
    period_end: date
    breakdown: List[SpendAnalysisItem]
    top_10_suppliers: List[SpendAnalysisItem]
    concentration: dict  # {top_3_pct, top_10_pct}


class ProcurementBudgetBase(BaseModel):
    """Base budget schema"""
    fiscal_year: int = Field(ge=2000, le=2100)
    category_id: Optional[int] = None
    budgeted_amount: Decimal = Field(gt=0)


class ProcurementBudgetCreate(ProcurementBudgetBase):
    """Create budget"""
    pass


class ProcurementBudgetUpdate(BaseModel):
    """Update budget"""
    budgeted_amount: Optional[Decimal] = Field(None, gt=0)


class ProcurementBudgetResponse(ProcurementBudgetBase):
    """Budget response"""
    id: int
    actual_spend: Decimal
    variance: Decimal
    variance_pct: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    category_name: Optional[str] = None
    consumed_pct: Decimal
    status: str  # on_track, at_risk, over_budget
    projected_annual: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class BudgetTrackingResponse(BaseModel):
    """Budget tracking response"""
    fiscal_year: int
    budgets: List[ProcurementBudgetResponse]
    overall_total_budget: Decimal
    overall_total_actual: Decimal
    overall_consumed_pct: Decimal
