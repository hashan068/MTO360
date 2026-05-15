"""
Procurement module database models
"""
from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    Numeric,
    Boolean,
    DateTime,
    Date,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import enum

from app.models.base import Base, TimestampMixin


# ============================================================================
# Enumerations
# ============================================================================

class ProcurementRFQStatusEnum(str, enum.Enum):
    """Procurement RFQ status workflow (component sourcing — distinct from sales RFQStatusEnum)"""
    DRAFT = "draft"
    SENT = "sent"
    QUOTES_RECEIVED = "quotes_received"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class SupplierQuoteStatusEnum(str, enum.Enum):
    """Supplier quote status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ContractStatusEnum(str, enum.Enum):
    """Contract status"""
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ABCClassificationEnum(str, enum.Enum):
    """ABC inventory classification"""
    A = "A"  # High value (top 20% by value, ~70-80% of total value)
    B = "B"  # Medium value (next 30%, ~15-20% of total value)
    C = "C"  # Low value (remaining 50%, ~5-10% of total value)


class ForecastMethodEnum(str, enum.Enum):
    """Forecasting method"""
    SIMPLE_MOVING_AVERAGE = "simple_moving_average"
    WEIGHTED_MOVING_AVERAGE = "weighted_moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MANUAL = "manual"


class PriceChangeSourceEnum(str, enum.Enum):
    """Source of price change"""
    PURCHASE_ORDER = "purchase_order"
    CONTRACT_UPDATE = "contract_update"
    MANUAL_EDIT = "manual_edit"
    QUOTE = "quote"


# ============================================================================
# Phase 1: Supplier Performance Management
# ============================================================================

class SupplierPerformance(Base, TimestampMixin):
    """Supplier performance tracking (monthly snapshots)"""
    __tablename__ = "supplier_performance"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("suppliers.id", ondelete="CASCADE"), 
        nullable=False
    )
    period: Mapped[date] = mapped_column(Date, nullable=False)  # First day of month
    
    # Performance Metrics
    on_time_delivery_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False,
        default=Decimal("0.00")
    )  # 0-100%
    quality_rating: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False,
        default=Decimal("100.00")
    )  # 0-100%
    average_lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price_competitiveness_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False,
        default=Decimal("100.00")
    )  # 0-100%
    total_spend: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), 
        nullable=False, 
        default=Decimal("0.00")
    )
    
    # Overall Score (weighted average)
    overall_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False,
        default=Decimal("0.00")
    )  # 0-100
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="performance_records")
    
    def __repr__(self):
        return f"<SupplierPerformance(supplier_id={self.supplier_id}, period={self.period}, score={self.overall_score})>"


# ============================================================================
# Phase 2: RFQ & Competitive Bidding
# ============================================================================

class ProcurementRFQ(Base, TimestampMixin):
    """Request for Quotation"""
    __tablename__ = "procurement_rfqs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # RFQ-2025-0001
    
    # RFQ Details
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    required_by_date: Mapped[date] = mapped_column(Date, nullable=False)
    closing_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Status
    status: Mapped[ProcurementRFQStatusEnum] = mapped_column(
        SQLEnum(ProcurementRFQStatusEnum, name="procurement_rfq_status_enum"),
        default=ProcurementRFQStatusEnum.DRAFT,
        nullable=False
    )
    
    # Additional Info
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Technical specs
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Not sent to suppliers
    
    # Tracking
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    awarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component")
    quotes: Mapped[list["SupplierQuote"]] = relationship(
        "SupplierQuote", 
        back_populates="rfq", 
        cascade="all, delete-orphan"
    )
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ProcurementRFQ(rfq_number={self.rfq_number}, status={self.status.value})>"


class SupplierQuote(Base, TimestampMixin):
    """Supplier quote for an RFQ"""
    __tablename__ = "supplier_quotes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("procurement_rfqs.id", ondelete="CASCADE"), 
        nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Quote Details
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    minimum_order_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quote_valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[SupplierQuoteStatusEnum] = mapped_column(
        SQLEnum(SupplierQuoteStatusEnum, name="supplier_quote_status_enum"),
        default=SupplierQuoteStatusEnum.PENDING,
        nullable=False
    )
    is_awarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Tracking
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    awarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    award_justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    rfq: Mapped["ProcurementRFQ"] = relationship("ProcurementRFQ", back_populates="quotes")
    supplier: Mapped["Supplier"] = relationship("Supplier")
    
    def __repr__(self):
        return f"<SupplierQuote(rfq_id={self.rfq_id}, supplier_id={self.supplier_id}, price={self.unit_price})>"


# ============================================================================
# Phase 3: Contract Management
# ============================================================================

class SupplierContract(Base, TimestampMixin):
    """Supplier contract"""
    __tablename__ = "supplier_contracts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # CONTRACT-2025-0001
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Contract Terms
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(50), nullable=False)  # Net 30, Net 60, etc.
    
    # Volume Discounts (JSON array of tiers)
    # Example: [{"min_qty": 100, "max_qty": 499, "discount_pct": 5}, {...}]
    volume_discounts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[ContractStatusEnum] = mapped_column(
        SQLEnum(ContractStatusEnum), 
        default=ContractStatusEnum.DRAFT, 
        nullable=False
    )
    
    # File Upload
    contract_file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Auto-Renewal
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    renewal_notice_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    
    # Tracking
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="contracts")
    pricing: Mapped[list["ContractPricing"]] = relationship(
        "ContractPricing", 
        back_populates="contract", 
        cascade="all, delete-orphan"
    )
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<SupplierContract(contract_number={self.contract_number}, supplier_id={self.supplier_id}, status={self.status.value})>"


class ContractPricing(Base, TimestampMixin):
    """Component pricing in a contract"""
    __tablename__ = "contract_pricing"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("supplier_contracts.id", ondelete="CASCADE"), 
        nullable=False
    )
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"), nullable=False)
    
    # Pricing
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    minimum_order_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Effective Dates (optional override)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    contract: Mapped["SupplierContract"] = relationship("SupplierContract", back_populates="pricing")
    component: Mapped["Component"] = relationship("Component")
    
    def __repr__(self):
        return f"<ContractPricing(contract_id={self.contract_id}, component_id={self.component_id}, price={self.unit_price})>"


# ============================================================================
# Phase 4: Inventory Optimization
# ============================================================================

class ComponentInventoryPolicy(Base, TimestampMixin):
    """Inventory policy for a component"""
    __tablename__ = "component_inventory_policies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("components.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    
    # Calculated Policies
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    economic_order_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # ABC Analysis
    abc_classification: Mapped[ABCClassificationEnum] = mapped_column(
        SQLEnum(ABCClassificationEnum), 
        default=ABCClassificationEnum.C, 
        nullable=False
    )
    
    # Inputs for Calculations
    average_monthly_demand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ordering_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        nullable=False, 
        default=Decimal("50.00")
    )  # Cost per order ($)
    holding_cost_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        default=Decimal("25.00")
    )  # % of unit cost per year
    
    # Auto-PR
    auto_pr_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Tracking
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component", back_populates="inventory_policy")
    updater: Mapped[Optional["User"]] = relationship("User")
    
    def __repr__(self):
        return f"<ComponentInventoryPolicy(component_id={self.component_id}, ROP={self.reorder_point}, EOQ={self.economic_order_quantity})>"


class DemandForecast(Base, TimestampMixin):
    """Demand forecast for a component"""
    __tablename__ = "demand_forecasts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("components.id", ondelete="CASCADE"), 
        nullable=False
    )
    forecast_month: Mapped[date] = mapped_column(Date, nullable=False)  # First day of month
    
    # Forecast
    forecasted_demand: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_demand: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Populated after month ends
    
    # Method
    forecast_method: Mapped[ForecastMethodEnum] = mapped_column(
        SQLEnum(ForecastMethodEnum), 
        nullable=False
    )
    
    # Accuracy (calculated after actual demand known)
    forecast_accuracy_mape: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), 
        nullable=True
    )  # Mean Absolute Percentage Error
    
    # Relationships
    component: Mapped["Component"] = relationship("Component")
    
    def __repr__(self):
        return f"<DemandForecast(component_id={self.component_id}, month={self.forecast_month}, forecast={self.forecasted_demand})>"


# ============================================================================
# Phase 5: Cost Analysis & Reporting
# ============================================================================

class ComponentPriceHistory(Base):
    """Price history for components (append-only)"""
    __tablename__ = "component_price_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("components.id", ondelete="CASCADE"), 
        nullable=False
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("suppliers.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Price
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Source
    price_change_source: Mapped[PriceChangeSourceEnum] = mapped_column(
        SQLEnum(PriceChangeSourceEnum), 
        nullable=False
    )
    purchase_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("purchase_orders.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Tracking
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    component: Mapped["Component"] = relationship("Component")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder")
    recorder: Mapped[Optional["User"]] = relationship("User")
    
    def __repr__(self):
        return f"<ComponentPriceHistory(component_id={self.component_id}, price={self.unit_price}, date={self.effective_date})>"


class ProcurementBudget(Base, TimestampMixin):
    """Procurement budget by fiscal year and category"""
    __tablename__ = "procurement_budgets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)  # 2025, 2026, etc.
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("categories.id", ondelete="CASCADE"), 
        nullable=True
    )  # Null = overall budget
    
    # Budget
    budgeted_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    actual_spend: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), 
        nullable=False, 
        default=Decimal("0.00")
    )
    variance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), 
        nullable=False, 
        default=Decimal("0.00")
    )  # budgeted - actual
    variance_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        default=Decimal("0.00")
    )  # (variance / budgeted) * 100
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category")
    
    def __repr__(self):
        return f"<ProcurementBudget(year={self.fiscal_year}, category_id={self.category_id}, budget={self.budgeted_amount})>"
