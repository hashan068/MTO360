# Advanced Procurement & Supplier Management - Data Models Specification

**Document Version:** 1.0  
**Date:** November 25, 2025  
**Status:** Draft for Review  
**Project:** MTO360 - Advanced Procurement Module

---

## Table of Contents

1. [Overview](#1-overview)
2. [Database Schema](#2-database-schema)
3. [Entity Relationship Diagram](#3-entity-relationship-diagram)
4. [Model Definitions](#4-model-definitions)
5. [Enumerations](#5-enumerations)
6. [Indexes & Constraints](#6-indexes--constraints)
7. [Migration Strategy](#7-migration-strategy)
8. [Data Integrity Rules](#8-data-integrity-rules)

---

## 1. Overview

### 1.1 Purpose
This document defines the complete data model for the Advanced Procurement & Supplier Management system, including new tables, modifications to existing tables, relationships, constraints, and migration strategy.

### 1.2 Design Principles
- **Extend, Don't Replace**: Extend existing MTO360 models rather than replacing them
- **Backward Compatibility**: No breaking changes to existing APIs
- **Data Integrity**: Enforce referential integrity via foreign keys
- **Audit Trail**: Track all changes with timestamps and user IDs
- **Performance**: Proper indexing for query optimization
- **Scalability**: Schema designed for 10,000+ components, 500+ suppliers

### 1.3 Naming Conventions
- **Tables**: Lowercase with underscores (e.g., `supplier_performance`)
- **Columns**: Lowercase with underscores (e.g., `on_time_delivery_rate`)
- **Foreign Keys**: `{referenced_table}_id` (e.g., `supplier_id`)
- **Indexes**: `idx_{table}_{column(s)}` (e.g., `idx_supplier_performance_period`)
- **Constraints**: `{table}_{column}_{type}` (e.g., `supplier_performance_score_check`)

---

## 2. Database Schema

### 2.1 Schema Organization

```
MTO360 Database
├── Existing Tables (Extended)
│   ├── suppliers (add fields)
│   ├── components (add fields)
│   ├── purchase_orders (add fields)
│   └── purchase_requisitions (unchanged)
│
└── New Tables
    ├── Supplier Performance Management
    │   └── supplier_performance
    │
    ├── RFQ & Bidding
    │   ├── procurement_rfqs
    │   └── supplier_quotes
    │
    ├── Contract Management
    │   ├── supplier_contracts
    │   └── contract_pricing
    │
    ├── Inventory Optimization
    │   ├── component_inventory_policies
    │   └── demand_forecasts
    │
    └── Cost Analysis
        ├── component_price_history
        └── procurement_budgets
```

---

## 3. Entity Relationship Diagram

```mermaid
erDiagram
    %% Existing Entities (Extended)
    SUPPLIER {
        int id PK
        string name
        string email
        text address
        string website
        boolean is_active
        text notes
        datetime date_added
        datetime created_at
        datetime updated_at
    }
    
    COMPONENT {
        int id PK
        string name
        text description
        int quantity
        int category_id FK
        int reorder_level
        int reorder_quantity
        int order_quantity
        string unit_of_measure
        int supplier_id FK
        decimal cost
        datetime created_at
        datetime updated_at
    }
    
    PURCHASE_ORDER {
        int id PK
        int creator_id FK
        int purchase_requisition_id FK
        int supplier_id FK
        enum status
        text notes
        decimal price_per_unit
        decimal total_price
        date expected_delivery_date
        date actual_delivery_date
        datetime created_at
        datetime updated_at
    }
    
    PURCHASE_REQUISITION {
        int id PK
        int user_id FK
        int component_id FK
        int quantity
        enum status
        text notes
        datetime expected_delivery_date
        enum priority
        datetime created_at
        datetime updated_at
    }
    
    %% New Entities - Supplier Performance
    SUPPLIER_PERFORMANCE {
        int id PK
        int supplier_id FK
        date period
        decimal on_time_delivery_rate
        decimal quality_rating
        int average_lead_time_days
        decimal price_competitiveness_score
        decimal total_spend
        decimal overall_score
        datetime created_at
        datetime updated_at
    }
    
    %% New Entities - RFQ & Bidding
    PROCUREMENT_RFQ {
        int id PK
        string rfq_number UK
        int component_id FK
        int quantity
        date required_by_date
        datetime closing_datetime
        enum status
        text specifications
        text internal_notes
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    SUPPLIER_QUOTE {
        int id PK
        int rfq_id FK
        int supplier_id FK
        decimal unit_price
        int lead_time_days
        int minimum_order_quantity
        date quote_valid_until
        text notes
        enum status
        boolean is_awarded
        datetime submitted_at
        datetime created_at
        datetime updated_at
    }
    
    %% New Entities - Contract Management
    SUPPLIER_CONTRACT {
        int id PK
        string contract_number UK
        int supplier_id FK
        date start_date
        date end_date
        string payment_terms
        json volume_discounts
        enum status
        text contract_file_url
        boolean auto_renew
        int renewal_notice_days
        int created_by FK
        datetime created_at
        datetime updated_at
    }
    
    CONTRACT_PRICING {
        int id PK
        int contract_id FK
        int component_id FK
        decimal unit_price
        int minimum_order_quantity
        int lead_time_days
        date effective_from
        date effective_to
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    %% New Entities - Inventory Optimization
    COMPONENT_INVENTORY_POLICY {
        int id PK
        int component_id FK UK
        int reorder_point
        int safety_stock
        int economic_order_quantity
        enum abc_classification
        int average_monthly_demand
        int lead_time_days
        decimal ordering_cost
        decimal holding_cost_pct
        boolean auto_pr_enabled
        int updated_by FK
        datetime last_calculated_at
        datetime created_at
        datetime updated_at
    }
    
    DEMAND_FORECAST {
        int id PK
        int component_id FK
        date forecast_month
        int forecasted_demand
        int actual_demand
        string forecast_method
        decimal forecast_accuracy_mape
        datetime created_at
        datetime updated_at
    }
    
    %% New Entities - Cost Analysis
    COMPONENT_PRICE_HISTORY {
        int id PK
        int component_id FK
        int supplier_id FK
        decimal unit_price
        date effective_date
        int purchase_order_id FK
        string price_change_source
        int recorded_by FK
        datetime created_at
    }
    
    PROCUREMENT_BUDGET {
        int id PK
        int fiscal_year
        int category_id FK
        decimal budgeted_amount
        decimal actual_spend
        decimal variance
        decimal variance_pct
        datetime created_at
        datetime updated_at
    }
    
    %% Relationships
    SUPPLIER ||--o{ SUPPLIER_PERFORMANCE : "has performance records"
    SUPPLIER ||--o{ SUPPLIER_CONTRACT : "has contracts"
    SUPPLIER ||--o{ SUPPLIER_QUOTE : "submits quotes"
    SUPPLIER ||--o{ COMPONENT : "supplies"
    SUPPLIER ||--o{ PURCHASE_ORDER : "receives orders"
    SUPPLIER ||--o{ COMPONENT_PRICE_HISTORY : "price history"
    
    COMPONENT ||--o{ PROCUREMENT_RFQ : "requested in RFQs"
    COMPONENT ||--|| COMPONENT_INVENTORY_POLICY : "has policy"
    COMPONENT ||--o{ DEMAND_FORECAST : "has forecasts"
    COMPONENT ||--o{ CONTRACT_PRICING : "priced in contracts"
    COMPONENT ||--o{ COMPONENT_PRICE_HISTORY : "price history"
    COMPONENT ||--o{ PURCHASE_REQUISITION : "requested in PRs"
    
    PROCUREMENT_RFQ ||--o{ SUPPLIER_QUOTE : "receives quotes"
    
    SUPPLIER_CONTRACT ||--o{ CONTRACT_PRICING : "defines pricing"
    
    PURCHASE_ORDER ||--o| COMPONENT_PRICE_HISTORY : "creates price record"
    PURCHASE_REQUISITION ||--o{ PURCHASE_ORDER : "fulfilled by"
```

---

## 4. Model Definitions

### 4.1 Supplier Performance Management

#### 4.1.1 SupplierPerformance

**Purpose:** Track monthly performance metrics for each supplier.

**Table:** `supplier_performance`

```python
from sqlalchemy import Integer, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from decimal import Decimal

class SupplierPerformance(Base, TimestampMixin):
    """Supplier performance tracking (monthly snapshots)"""
    __tablename__ = "supplier_performance"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    period: Mapped[date] = mapped_column(Date, nullable=False)  # First day of month
    
    # Performance Metrics
    on_time_delivery_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100%
    quality_rating: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100%
    average_lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price_competitiveness_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100%
    total_spend: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    
    # Overall Score (weighted average)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="performance_records")
    
    def __repr__(self):
        return f"<SupplierPerformance(supplier_id={self.supplier_id}, period={self.period}, score={self.overall_score})>"
```

**Constraints:**
- Unique constraint on `(supplier_id, period)` - one record per supplier per month
- Check constraint: `overall_score BETWEEN 0 AND 100`
- Check constraint: `on_time_delivery_rate BETWEEN 0 AND 100`
- Check constraint: `quality_rating BETWEEN 0 AND 100`
- Check constraint: `price_competitiveness_score BETWEEN 0 AND 100`

**Indexes:**
- Primary Key: `id`
- Unique: `idx_supplier_performance_unique` on `(supplier_id, period)`
- Index: `idx_supplier_performance_period` on `period` (for date range queries)
- Index: `idx_supplier_performance_overall_score` on `overall_score` (for rankings)

---

### 4.2 RFQ & Competitive Bidding

#### 4.2.1 ProcurementRFQ

**Purpose:** Request for quotation sent to multiple suppliers.

**Table:** `procurement_rfqs`

```python
import enum
from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey, Enum as SQLEnum

class RFQStatusEnum(str, enum.Enum):
    """RFQ status workflow"""
    DRAFT = "draft"
    SENT = "sent"
    QUOTES_RECEIVED = "quotes_received"
    AWARDED = "awarded"
    CANCELLED = "cancelled"

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
    status: Mapped[RFQStatusEnum] = mapped_column(SQLEnum(RFQStatusEnum), default=RFQStatusEnum.DRAFT, nullable=False)
    
    # Additional Info
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Technical specs
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Not sent to suppliers
    
    # Tracking
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    awarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component")
    quotes: Mapped[list["SupplierQuote"]] = relationship("SupplierQuote", back_populates="rfq", cascade="all, delete-orphan")
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ProcurementRFQ(rfq_number={self.rfq_number}, status={self.status.value})>"
```

**Constraints:**
- Unique constraint on `rfq_number`
- Check constraint: `quantity > 0`
- Check constraint: `required_by_date >= CURRENT_DATE` (on insert)
- Check constraint: `closing_datetime >= CURRENT_TIMESTAMP` (on insert)

**Indexes:**
- Primary Key: `id`
- Unique: `idx_rfq_number` on `rfq_number`
- Index: `idx_rfq_component` on `component_id`
- Index: `idx_rfq_status` on `status`
- Index: `idx_rfq_closing` on `closing_datetime`
- Index: `idx_rfq_created_by` on `created_by`

---

#### 4.2.2 SupplierQuote

**Purpose:** Supplier's quote in response to an RFQ.

**Table:** `supplier_quotes`

```python
class QuoteStatusEnum(str, enum.Enum):
    """Quote status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class SupplierQuote(Base, TimestampMixin):
    """Supplier quote for an RFQ"""
    __tablename__ = "supplier_quotes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(Integer, ForeignKey("procurement_rfqs.id", ondelete="CASCADE"), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Quote Details
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    minimum_order_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quote_valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[QuoteStatusEnum] = mapped_column(SQLEnum(QuoteStatusEnum), default=QuoteStatusEnum.PENDING, nullable=False)
    is_awarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Tracking
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    awarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    award_justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    rfq: Mapped["ProcurementRFQ"] = relationship("ProcurementRFQ", back_populates="quotes")
    supplier: Mapped["Supplier"] = relationship("Supplier")
    
    def __repr__(self):
        return f"<SupplierQuote(rfq_id={self.rfq_id}, supplier_id={self.supplier_id}, price={self.unit_price})>"
```

**Constraints:**
- Unique constraint on `(rfq_id, supplier_id)` - one quote per supplier per RFQ
- Check constraint: `unit_price > 0`
- Check constraint: `lead_time_days > 0`
- Check constraint: `minimum_order_quantity > 0`
- Check constraint: `quote_valid_until >= CURRENT_DATE`
- Check constraint: Only one quote per RFQ can have `is_awarded=true`

**Indexes:**
- Primary Key: `id`
- Unique: `idx_quote_unique` on `(rfq_id, supplier_id)`
- Index: `idx_quote_rfq` on `rfq_id`
- Index: `idx_quote_supplier` on `supplier_id`
- Index: `idx_quote_status` on `status`
- Index: `idx_quote_awarded` on `is_awarded`

---

### 4.3 Contract Management

#### 4.3.1 SupplierContract

**Purpose:** Supplier contract with terms and volume discounts.

**Table:** `supplier_contracts`

```python
from sqlalchemy.dialects.postgresql import JSON

class ContractStatusEnum(str, enum.Enum):
    """Contract status"""
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

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
    status: Mapped[ContractStatusEnum] = mapped_column(SQLEnum(ContractStatusEnum), default=ContractStatusEnum.DRAFT, nullable=False)
    
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
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="contracts")
    pricing: Mapped[list["ContractPricing"]] = relationship("ContractPricing", back_populates="contract", cascade="all, delete-orphan")
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<SupplierContract(contract_number={self.contract_number}, supplier_id={self.supplier_id}, status={self.status.value})>"
```

**Constraints:**
- Unique constraint on `contract_number`
- Check constraint: `end_date > start_date`
- Check constraint: `renewal_notice_days >= 0`

**Indexes:**
- Primary Key: `id`
- Unique: `idx_contract_number` on `contract_number`
- Index: `idx_contract_supplier` on `supplier_id`
- Index: `idx_contract_status` on `status`
- Index: `idx_contract_dates` on `(start_date, end_date)`
- Index: `idx_contract_end_date` on `end_date` (for expiration alerts)

---

#### 4.3.2 ContractPricing

**Purpose:** Component pricing within a contract.

**Table:** `contract_pricing`

```python
class ContractPricing(Base, TimestampMixin):
    """Component pricing in a contract"""
    __tablename__ = "contract_pricing"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplier_contracts.id", ondelete="CASCADE"), nullable=False)
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
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    contract: Mapped["SupplierContract"] = relationship("SupplierContract", back_populates="pricing")
    component: Mapped["Component"] = relationship("Component")
    
    def __repr__(self):
        return f"<ContractPricing(contract_id={self.contract_id}, component_id={self.component_id}, price={self.unit_price})>"
```

**Constraints:**
- Unique constraint on `(contract_id, component_id)` - one pricing per component per contract
- Check constraint: `unit_price > 0`
- Check constraint: `minimum_order_quantity > 0`
- Check constraint: `lead_time_days > 0`
- Check constraint: `effective_to >= effective_from` (if both set)

**Indexes:**
- Primary Key: `id`
- Unique: `idx_contract_pricing_unique` on `(contract_id, component_id)`
- Index: `idx_contract_pricing_contract` on `contract_id`
- Index: `idx_contract_pricing_component` on `component_id`
- Index: `idx_contract_pricing_active` on `is_active`

---

### 4.4 Inventory Optimization

#### 4.4.1 ComponentInventoryPolicy

**Purpose:** Inventory management policies per component.

**Table:** `component_inventory_policies`

```python
class ABCClassificationEnum(str, enum.Enum):
    """ABC inventory classification"""
    A = "A"  # High value (top 20% by value, ~70-80% of total value)
    B = "B"  # Medium value (next 30%, ~15-20% of total value)
    C = "C"  # Low value (remaining 50%, ~5-10% of total value)

class ComponentInventoryPolicy(Base, TimestampMixin):
    """Inventory policy for a component"""
    __tablename__ = "component_inventory_policies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Calculated Policies
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    economic_order_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # ABC Analysis
    abc_classification: Mapped[ABCClassificationEnum] = mapped_column(SQLEnum(ABCClassificationEnum), default=ABCClassificationEnum.C, nullable=False)
    
    # Inputs for Calculations
    average_monthly_demand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ordering_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("50.00"))  # Cost per order
    holding_cost_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("25.00"))  # % of unit cost per year
    
    # Auto-PR
    auto_pr_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Tracking
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component", back_populates="inventory_policy")
    updater: Mapped[Optional["User"]] = relationship("User")
    
    def __repr__(self):
        return f"<ComponentInventoryPolicy(component_id={self.component_id}, ROP={self.reorder_point}, EOQ={self.economic_order_quantity})>"
```

**Constraints:**
- Unique constraint on `component_id`
- Check constraint: `reorder_point >= 0`
- Check constraint: `safety_stock >= 0`
- Check constraint: `economic_order_quantity >= 0`
- Check constraint: `average_monthly_demand >= 0`
- Check constraint: `lead_time_days >= 0`
- Check constraint: `ordering_cost >= 0`
- Check constraint: `holding_cost_pct >= 0 AND holding_cost_pct <= 100`

**Indexes:**
- Primary Key: `id`
- Unique: `idx_inv_policy_component` on `component_id`
- Index: `idx_inv_policy_abc` on `abc_classification`
- Index: `idx_inv_policy_auto_pr` on `auto_pr_enabled`

---

#### 4.4.2 DemandForecast

**Purpose:** Monthly demand forecasts for components.

**Table:** `demand_forecasts`

```python
class ForecastMethodEnum(str, enum.Enum):
    """Forecasting method"""
    SIMPLE_MOVING_AVERAGE = "simple_moving_average"
    WEIGHTED_MOVING_AVERAGE = "weighted_moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MANUAL = "manual"

class DemandForecast(Base, TimestampMixin):
    """Demand forecast for a component"""
    __tablename__ = "demand_forecasts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id", ondelete="CASCADE"), nullable=False)
    forecast_month: Mapped[date] = mapped_column(Date, nullable=False)  # First day of month
    
    # Forecast
    forecasted_demand: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_demand: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Populated after month ends
    
    # Method
    forecast_method: Mapped[ForecastMethodEnum] = mapped_column(SQLEnum(ForecastMethodEnum), nullable=False)
    
    # Accuracy (calculated after actual demand known)
    forecast_accuracy_mape: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # Mean Absolute Percentage Error
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component")
    
    def __repr__(self):
        return f"<DemandForecast(component_id={self.component_id}, month={self.forecast_month}, forecast={self.forecasted_demand})>"
```

**Constraints:**
- Unique constraint on `(component_id, forecast_month)`
- Check constraint: `forecasted_demand >= 0`
- Check constraint: `actual_demand >= 0` (if not null)

**Indexes:**
- Primary Key: `id`
- Unique: `idx_forecast_unique` on `(component_id, forecast_month)`
- Index: `idx_forecast_component` on `component_id`
- Index: `idx_forecast_month` on `forecast_month`

---

### 4.5 Cost Analysis

#### 4.5.1 ComponentPriceHistory

**Purpose:** Complete price history for auditing and trend analysis.

**Table:** `component_price_history`

```python
class PriceChangeSourceEnum(str, enum.Enum):
    """Source of price change"""
    PURCHASE_ORDER = "purchase_order"
    CONTRACT_UPDATE = "contract_update"
    MANUAL_EDIT = "manual_edit"
    QUOTE = "quote"

class ComponentPriceHistory(Base):
    """Price history for components"""
    __tablename__ = "component_price_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id", ondelete="CASCADE"), nullable=False)
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    
    # Price
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Source
    price_change_source: Mapped[PriceChangeSourceEnum] = mapped_column(SQLEnum(PriceChangeSourceEnum), nullable=False)
    purchase_order_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True)
    
    # Tracking
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder")
    recorder: Mapped[Optional["User"]] = relationship("User")
    
    def __repr__(self):
        return f"<ComponentPriceHistory(component_id={self.component_id}, price={self.unit_price}, date={self.effective_date})>"
```

**Constraints:**
- Check constraint: `unit_price > 0`
- Immutable records (no updates, append-only)

**Indexes:**
- Primary Key: `id`
- Index: `idx_price_history_component` on `component_id`
- Index: `idx_price_history_supplier` on `supplier_id`
- Index: `idx_price_history_date` on `effective_date`
- Composite Index: `idx_price_history_comp_supp_date` on `(component_id, supplier_id, effective_date)`

---

#### 4.5.2 ProcurementBudget

**Purpose:** Budget tracking by fiscal year and category.

**Table:** `procurement_budgets`

```python
class ProcurementBudget(Base, TimestampMixin):
    """Procurement budget by fiscal year and category"""
    __tablename__ = "procurement_budgets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)  # 2025, 2026, etc.
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)  # Null = overall budget
    
    # Budget
    budgeted_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    actual_spend: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    variance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))  # budgeted - actual
    variance_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))  # (variance / budgeted) * 100
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category")
    
    def __repr__(self):
        return f"<ProcurementBudget(year={self.fiscal_year}, category_id={self.category_id}, budget={self.budgeted_amount})>"
```

**Constraints:**
- Unique constraint on `(fiscal_year, category_id)`
- Check constraint: `budgeted_amount >= 0`
- Check constraint: `actual_spend >= 0`
- Check constraint: `fiscal_year BETWEEN 2000 AND 2100`

**Indexes:**
- Primary Key: `id`
- Unique: `idx_budget_unique` on `(fiscal_year, category_id)`
- Index: `idx_budget_year` on `fiscal_year`
- Index: `idx_budget_category` on `category_id`

---

## 5. Enumerations

### 5.1 RFQ Status
```python
class RFQStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    QUOTES_RECEIVED = "quotes_received"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
```

### 5.2 Quote Status
```python
class QuoteStatusEnum(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
```

### 5.3 Contract Status
```python
class ContractStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
```

### 5.4 ABC Classification
```python
class ABCClassificationEnum(str, enum.Enum):
    A = "A"  # High value
    B = "B"  # Medium value
    C = "C"  # Low value
```

### 5.5 Forecast Method
```python
class ForecastMethodEnum(str, enum.Enum):
    SIMPLE_MOVING_AVERAGE = "simple_moving_average"
    WEIGHTED_MOVING_AVERAGE = "weighted_moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MANUAL = "manual"
```

### 5.6 Price Change Source
```python
class PriceChangeSourceEnum(str, enum.Enum):
    PURCHASE_ORDER = "purchase_order"
    CONTRACT_UPDATE = "contract_update"
    MANUAL_EDIT = "manual_edit"
    QUOTE = "quote"
```

---

## 6. Indexes & Constraints

### 6.1 Primary Indexes Summary

| Table | Indexed Columns | Purpose |
|-------|----------------|---------|
| `supplier_performance` | `supplier_id, period`, `overall_score` | Performance queries, rankings |
| `procurement_rfqs` | `rfq_number`, `component_id`, `status`, `closing_datetime` | RFQ lookups, filtering |
| `supplier_quotes` | `rfq_id, supplier_id`, `is_awarded` | Quote comparison, award tracking |
| `supplier_contracts` | `contract_number`, `supplier_id`, `status`, `end_date` | Contract lookups, expiration alerts |
| `contract_pricing` | `contract_id, component_id`, `component_id` | Pricing lookups |
| `component_inventory_policies` | `component_id`, `abc_classification` | Policy lookups, ABC filtering |
| `demand_forecasts` | `component_id, forecast_month` | Forecast queries |
| `component_price_history` | `component_id`, `supplier_id`, `effective_date` | Price trend analysis |
| `procurement_budgets` | `fiscal_year, category_id` | Budget tracking |

### 6.2 Foreign Key Constraints

All foreign keys SHALL use:
- `ON DELETE CASCADE` for dependent data (e.g., quotes when RFQ deleted)
- `ON DELETE SET NULL` for optional references (e.g., supplier in price history)
- `ON DELETE RESTRICT` for critical references (e.g., supplier with active contracts)

### 6.3 Check Constraints

- **Numeric Ranges**: Percentages (0-100), amounts (>= 0)
- **Date Logic**: end_date > start_date, future dates >= today
- **Business Rules**: quantity > 0, price > 0, scores 0-100

---

## 7. Migration Strategy

### 7.1 Phase 1: Supplier Performance (Week 1-2)

**Migration 001: Add supplier performance fields**
```sql
-- Extend suppliers table
ALTER TABLE suppliers ADD COLUMN preferred_status BOOLEAN DEFAULT FALSE;
ALTER TABLE suppliers ADD COLUMN last_performance_calc_date DATE;

-- Create supplier_performance table
CREATE TABLE supplier_performance (...);
CREATE INDEX idx_supplier_performance_unique ON supplier_performance (supplier_id, period);
```

**Data Migration:**
- No historical data migration (start fresh)
- Initial performance calculations for existing suppliers based on past 3 months POs

### 7.2 Phase 2: RFQ & Bidding (Week 3-4)

**Migration 002: Create RFQ tables**
```sql
CREATE TABLE procurement_rfqs (...);
CREATE TABLE supplier_quotes (...);
CREATE INDEX idx_rfq_number ON procurement_rfqs (rfq_number);
```

**Data Migration:**
- No historical data (new feature)

### 7.3 Phase 3: Contract Management (Week 5-6)

**Migration 003: Create contract tables**
```sql
CREATE TABLE supplier_contracts (...);
CREATE TABLE contract_pricing (...);
```

**Data Migration:**
- Import existing contracts from spreadsheets (if available)
- Manual entry for active contracts

### 7.4 Phase 4: Inventory Optimization (Week 7-8)

**Migration 004: Extend components and create inventory policies**
```sql
-- Extend components table (if fields don't exist)
ALTER TABLE components ADD COLUMN standard_cost NUMERIC(10,2);

CREATE TABLE component_inventory_policies (...);
CREATE TABLE demand_forecasts (...);
```

**Data Migration:**
- Create inventory policies for all existing components
- Calculate initial ROP/EOQ based on existing `reorder_level` and `reorder_quantity`
- Import historical consumption data for demand forecasting (past 6 months)

### 7.5 Phase 5: Cost Analysis (Week 9-10)

**Migration 005: Create cost tracking tables**
```sql
CREATE TABLE component_price_history (...);
CREATE TABLE procurement_budgets (...);
```

**Data Migration:**
- Import historical prices from existing POs (past 12 months)
- Set up budgets for current fiscal year

---

## 8. Data Integrity Rules

### 8.1 Referential Integrity

- **Cascading Deletes**: When parent deleted, children auto-deleted
  - RFQ → Quotes
  - Contract → Contract Pricing
  - Component → Inventory Policy, Forecasts, Price History

- **Set Null on Delete**: When reference deleted, FK set to null
  - Supplier deleted → Price history supplier_id = NULL
  - PO deleted → Price history purchase_order_id = NULL

- **Restrict Delete**: Prevent deletion if dependents exist
  - Supplier with active contracts cannot be deleted
  - Component with pending RFQs cannot be deleted

### 8.2 Data Validation

- **Application Layer**: Validate in API before database
  - Business rules (ROP calculation, budget limits)
  - Complex validations (tiered pricing overlaps)

- **Database Layer**: Enforce at schema level
  - NOT NULL constraints
  - CHECK constraints
  - UNIQUE constraints
  - Foreign Key constraints

### 8.3 Audit Logging

- **Automatic Timestamps**: All tables have `created_at`, `updated_at`
- **User Tracking**: Critical actions track `created_by`, `updated_by`
- **Immutable Records**: Price history, audit logs (append-only)
- **Soft Deletes**: Contracts, RFQs (add `deleted_at`, hide from queries)

---

## Appendix A: SQL Schema Export

**File:** `advanced_procurement_schema.sql`

This file will contain the complete DDL (Data Definition Language) statements for all tables, indexes, and constraints. It will be generated from the Alembic migration scripts and maintained in the repository.

---

## Appendix B: Sample Data

**File:** `advanced_procurement_seed_data.sql`

This file will contain sample data for testing and demonstration purposes, including:
- 10 suppliers with varied performance
- 50 components with inventory policies
- 5 sample RFQs with quotes
- 3 sample contracts with pricing
- Historical price data (12 months)

---

**Document Status:** DRAFT - Pending Technical Review

**Next Steps:**
1. Review by Database Administrator
2. Review by Backend Lead
3. Validation of migration strategy
4. Approval for implementation
