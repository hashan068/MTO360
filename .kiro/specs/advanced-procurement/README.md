# Advanced Procurement & Supplier Management - Spec Summary

## Overview
Enhance the existing basic procurement system with supplier performance tracking, RFQ/bidding, contract management, inventory optimization, and cost analysis.

## Business Value
- Reduce procurement costs by 10-15%
- Reduce stockouts by 50%
- Improve supplier on-time delivery by 30%
- Reduce excess inventory by 20%

## Timeline: 8-10 weeks | Complexity: Medium-High

---

## Key Features

### 1. Supplier Performance Management
**Track and rate suppliers based on:**
- On-time delivery rate (% of POs delivered on time)
- Quality rating (defect rate from quality module)
- Price competitiveness (vs market/other suppliers)
- Responsiveness (quote turnaround time)
- Overall supplier scorecard (weighted score)
- Preferred supplier lists by component category

**Models:**
```python
class SupplierPerformance(Base):
    supplier_id: int
    period: date  # Monthly snapshot
    on_time_delivery_rate: Decimal
    quality_rating: Decimal  # From quality module
    average_lead_time_days: int
    price_competitiveness_score: Decimal
    total_spend: Decimal
    overall_score: Decimal  # Weighted average
```

### 2. RFQ & Competitive Bidding
**Enable multi-supplier quoting:**
- Create RFQ for components
- Send to multiple suppliers
- Collect and compare quotes
- Award PO to best supplier
- Track quote response time
- Price negotiation history

**Models:**
```python
class ProcurementRFQ(Base):
    rfq_number: str
    component_id: int
    quantity: int
    required_by_date: date
    status: RFQStatusEnum  # draft, sent, quotes_received, awarded, cancelled
    
class SupplierQuote(Base):
    rfq_id: int
    supplier_id: int
    unit_price: Decimal
    lead_time_days: int
    minimum_order_quantity: int
    quote_valid_until: date
    notes: str
    status: QuoteStatusEnum  # pending, submitted, accepted, rejected
```

### 3. Contract Management
**Manage supplier agreements:**
- Supplier contracts with terms
- Volume discounts (tiered pricing)
- Payment terms (Net 30, Net 60, etc.)
- Contract start/end dates
- Contract renewal alerts
- Blanket POs (call-off orders)

**Models:**
```python
class SupplierContract(Base):
    contract_number: str
    supplier_id: int
    start_date: date
    end_date: date
    payment_terms: str
    volume_discounts: JSON  # [{min_qty: 100, discount_pct: 5}, ...]
    status: ContractStatusEnum  # active, expired, cancelled
    
class ContractPricing(Base):
    contract_id: int
    component_id: int
    unit_price: Decimal
    minimum_order_quantity: int
    lead_time_days: int
```

### 4. Inventory Optimization
**Intelligent reordering:**
- Reorder points (ROP) per component
- Safety stock calculations
- Economic Order Quantity (EOQ)
- ABC analysis (classify by value/usage)
- Lead time tracking
- Demand forecasting (simple moving average)
- Auto-generate PRs when stock below ROP

**Models:**
```python
class ComponentInventoryPolicy(Base):
    component_id: int
    reorder_point: int  # When to reorder
    safety_stock: int  # Buffer stock
    economic_order_quantity: int  # Optimal order size
    abc_classification: ABCEnum  # A (high value), B (medium), C (low)
    average_monthly_demand: int
    lead_time_days: int
    
class DemandForecast(Base):
    component_id: int
    forecast_date: date
    forecasted_demand: int
    actual_demand: Optional[int]
    forecast_method: str  # moving_average, exponential_smoothing
```

### 5. Cost Analysis & Reporting
**Track and analyze costs:**
- Price history per component/supplier
- Cost variance analysis (actual vs standard)
- Spend analysis by supplier/category
- Budget vs actual tracking
- Price trend alerts (significant increases)
- Total Cost of Ownership (TCO)

**Models:**
```python
class ComponentPriceHistory(Base):
    component_id: int
    supplier_id: int
    effective_date: date
    unit_price: Decimal
    purchase_order_id: Optional[int]
    
class ProcurementBudget(Base):
    fiscal_year: int
    category_id: Optional[int]
    budgeted_amount: Decimal
    actual_spend: Decimal
    variance: Decimal
```

---

## API Endpoints

### Supplier Performance
```
GET    /api/procurement/suppliers/{id}/performance
GET    /api/procurement/suppliers/rankings?category_id=
POST   /api/procurement/suppliers/{id}/performance/calculate
GET    /api/procurement/suppliers/preferred?category_id=
```

### RFQ & Bidding
```
POST   /api/procurement/rfqs
GET    /api/procurement/rfqs
GET    /api/procurement/rfqs/{id}
POST   /api/procurement/rfqs/{id}/send
POST   /api/procurement/rfqs/{id}/quotes
GET    /api/procurement/rfqs/{id}/quotes/compare
POST   /api/procurement/rfqs/{id}/award
```

### Contracts
```
POST   /api/procurement/contracts
GET    /api/procurement/contracts
GET    /api/procurement/contracts/{id}
GET    /api/procurement/contracts/expiring?days=30
POST   /api/procurement/contracts/{id}/pricing
```

### Inventory Optimization
```
POST   /api/procurement/inventory-policies
GET    /api/procurement/inventory-policies
PUT    /api/procurement/inventory-policies/{component_id}
POST   /api/procurement/inventory-policies/calculate-rop
GET    /api/procurement/components/below-reorder-point
POST   /api/procurement/auto-generate-prs
GET    /api/procurement/abc-analysis
```

### Cost Analysis
```
GET    /api/procurement/price-history?component_id=&supplier_id=
GET    /api/procurement/spend-analysis?start_date=&end_date=&group_by=supplier|category
GET    /api/procurement/cost-variance
GET    /api/procurement/budget-tracking
```

---

## Key Services

### SupplierPerformanceService
- calculate_supplier_performance(supplier_id, period)
- get_supplier_rankings(category_id)
- update_preferred_suppliers()

### RFQService
- create_rfq(data)
- send_rfq_to_suppliers(rfq_id, supplier_ids)
- submit_quote(rfq_id, supplier_id, quote_data)
- compare_quotes(rfq_id)
- award_rfq(rfq_id, supplier_id)

### ContractService
- create_contract(data)
- get_expiring_contracts(days)
- get_contract_pricing(component_id, supplier_id)

### InventoryOptimizationService
- calculate_reorder_point(component_id)
- calculate_eoq(component_id)
- perform_abc_analysis()
- forecast_demand(component_id, periods)
- auto_generate_purchase_requisitions()

### CostAnalysisService
- get_price_history(component_id, supplier_id)
- analyze_spend(filters)
- calculate_cost_variance()
- track_budget_performance()

---

## UI Components

1. **Supplier Performance Dashboard**
   - Supplier scorecards
   - Performance metrics
   - Rankings by category

2. **RFQ Management**
   - Create RFQ form
   - RFQ list
   - Quote comparison table
   - Award decision

3. **Contract Management**
   - Contract list
   - Contract detail view
   - Expiring contracts alert
   - Pricing management

4. **Inventory Optimization Dashboard**
   - Components below ROP
   - ABC analysis chart
   - Demand forecast charts
   - Auto-PR generation

5. **Cost Analysis Dashboard**
   - Price trends
   - Spend analysis
   - Budget vs actual
   - Cost variance reports

---

## Integration Points

- **Inventory**: Auto-generate PRs based on ROP
- **Manufacturing**: Material availability forecasting
- **Scheduling**: Consider lead times in scheduling
- **Quality**: Supplier quality data in performance
- **Notifications**: RFQ alerts, contract expiration, low stock

---

## Success Metrics

- Procurement costs reduced by 10-15%
- Stockouts reduced by 50%
- Supplier on-time delivery improved by 30%
- Excess inventory reduced by 20%
- 80% of components have optimized inventory policies
- 90% of RFQs receive 3+ quotes

---

## Implementation Phases

**Phase 1 (Weeks 1-2)**: Supplier Performance
**Phase 2 (Weeks 3-4)**: RFQ & Bidding
**Phase 3 (Weeks 5-6)**: Contract Management
**Phase 4 (Weeks 7-8)**: Inventory Optimization
**Phase 5 (Weeks 9-10)**: Cost Analysis & Reporting

---

**Full detailed specs (requirements.md, design.md, tasks.md) to be created when this feature is prioritized.**
