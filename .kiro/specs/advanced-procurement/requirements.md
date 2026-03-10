# Advanced Procurement & Supplier Management - Requirements Specification

**Document Version:** 1.0  
**Date:** November 25, 2025  
**Status:** Draft for Review  
**Project:** MTO360 - Advanced Procurement Module

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Scope](#2-scope)
3. [System Overview](#3-system-overview)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Integration Requirements](#6-integration-requirements)
7. [Security & Compliance](#7-security--compliance)
8. [User Stories](#8-user-stories)
9. [Acceptance Criteria](#9-acceptance-criteria)

---

## 1. Introduction

### 1.1 Purpose
This document outlines the detailed requirements for the Advanced Procurement & Supplier Management system that will enhance the existing basic procurement capabilities of MTO360 with enterprise-grade features for supplier performance tracking, competitive bidding, contract management, inventory optimization, and comprehensive cost analysis.

### 1.2 Document Conventions
- **SHALL/MUST**: Mandatory requirement
- **SHOULD**: Recommended requirement
- **MAY**: Optional requirement
- **Priority Levels**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)

### 1.3 Intended Audience
- Product Management
- Development Team
- Quality Assurance
- Business Stakeholders
- System Administrators

### 1.4 Project Scope References
- Executive Summary: `.kiro/specs/EXECUTIVE_SUMMARY.md`
- Feature Roadmap: `.kiro/specs/FEATURE_ROADMAP.md`
- Current System: Backend models in `backend/app/models/inventory.py`

---

## 2. Scope

### 2.1 In Scope
The Advanced Procurement system SHALL include:

1. **Supplier Performance Management**
   - Performance tracking and rating
   - Supplier scorecards with weighted metrics
   - Preferred supplier lists by category
   - Historical performance analytics

2. **RFQ & Competitive Bidding**
   - Multi-supplier request for quotation (RFQ)
   - Quote collection and comparison
   - Automated supplier notifications
   - Award decision tracking

3. **Contract Management**
   - Supplier contract lifecycle management
   - Volume-based tiered pricing
   - Payment terms management
   - Contract renewal alerts
   - Blanket purchase orders (call-off orders)

4. **Inventory Optimization**
   - Reorder point (ROP) calculations
   - Safety stock management
   - Economic Order Quantity (EOQ)
   - ABC analysis for inventory classification
   - Demand forecasting
   - Automated purchase requisition generation

5. **Cost Analysis & Reporting**
   - Component price history tracking
   - Cost variance analysis
   - Supplier spend analysis
   - Budget vs actual tracking
   - Price trend alerts
   - Total Cost of Ownership (TCO) calculations

### 2.2 Out of Scope
The following are explicitly OUT of scope for this phase:

- Integration with external ERP systems (SAP, Oracle)
- EDI (Electronic Data Interchange) integration
- Advanced forecasting algorithms (machine learning-based)
- Multi-currency support (Phase 2)
- International trade compliance (customs, tariffs)
- Vendor portal for direct supplier access
- Automated invoice reconciliation
- Purchase card (P-card) integration

### 2.3 Future Considerations
Features planned for future releases:
- Advanced demand forecasting using machine learning
- Supplier risk assessment and mitigation
- Supplier collaboration portal
- Blockchain-based contract management
- Predictive analytics for procurement optimization

---

## 3. System Overview

### 3.1 Business Context
MTO360 is a Make-to-Order manufacturing execution system for electronics manufacturing. The Advanced Procurement module will:

- **Reduce procurement costs** by 10-15% through competitive bidding and supplier optimization
- **Reduce stockouts** by 50% through intelligent reordering
- **Improve supplier delivery performance** by 30% through performance tracking
- **Reduce excess inventory** by 20% through demand forecasting and EOQ

### 3.2 System Architecture Context
The procurement module integrates with existing MTO360 modules:

- **Inventory Module**: Extends current `Supplier`, `Component`, `PurchaseOrder`, `PurchaseRequisition` models
- **Manufacturing Module**: Provides material availability forecasting
- **Quality Module**: Integrates supplier quality ratings
- **Sales Module**: Links delivery promises to supplier lead times
- **Notifications Module**: Sends alerts for RFQs, contracts, low stock

### 3.3 User Roles & Permissions

| Role | Responsibilities | Access Level |
|------|-----------------|--------------|
| **Procurement Manager** | Full procurement operations, approve contracts, award RFQs | Full Access |
| **Buyer** | Create RFQs, manage POs, update inventory policies | Create/Edit |
| **Warehouse Manager** | View stock levels, set reorder points, receive materials | Limited Edit |
| **Finance Manager** | View cost analysis, budgets, approve large purchases | View + Approve |
| **Production Planner** | View material availability, suggest PRs | View Only |
| **Quality Manager** | Update supplier quality ratings | Quality Edit |

---

## 4. Functional Requirements

### 4.1 Supplier Performance Management

#### REQ-SPM-001: Performance Metrics Tracking [P0]
**Description:** System SHALL track and calculate supplier performance metrics on a monthly basis.

**Specific Requirements:**
- **REQ-SPM-001.1**: Track on-time delivery rate (% of POs delivered by promised date) [P0]
- **REQ-SPM-001.2**: Track quality rating from quality module (defect rate per supplier) [P0]
- **REQ-SPM-001.3**: Track price competitiveness vs market/other suppliers [P1]
- **REQ-SPM-001.4**: Track quote response time (hours to submit quote) [P1]
- **REQ-SPM-001.5**: Calculate average lead time in days [P0]
- **REQ-SPM-001.6**: Track total spend per supplier per period [P0]

**Acceptance Criteria:**
- Metrics automatically calculated at month-end
- Historical data retained for 24 months minimum
- Manual recalculation capability for corrections

#### REQ-SPM-002: Supplier Scorecard [P0]
**Description:** System SHALL provide a weighted overall supplier score.

**Specific Requirements:**
- **REQ-SPM-002.1**: Overall score = weighted average of:
  - On-time delivery (40%)
  - Quality rating (30%)
  - Price competitiveness (20%)
  - Responsiveness (10%)
- **REQ-SPM-002.2**: Score range 0-100
- **REQ-SPM-002.3**: Color-coded rating: Green (≥80), Yellow (60-79), Red (<60)
- **REQ-SPM-002.4**: Configurable weights by system administrator

**Acceptance Criteria:**
- Score updates within 24 hours of new performance data
- Weights sum to 100%
- Historical scores retained for trending

#### REQ-SPM-003: Preferred Supplier Lists [P1]
**Description:** System SHALL maintain preferred supplier lists by component category.

**Specific Requirements:**
- **REQ-SPM-003.1**: Auto-recommend suppliers with score ≥75 as "preferred"
- **REQ-SPM-003.2**: Manual override capability to add/remove preferred status
- **REQ-SPM-003.3**: Multi-supplier support per category (up to 5 preferred)
- **REQ-SPM-003.4**: Display preferred suppliers first in RFQ supplier selection

**Acceptance Criteria:**
- Preferred status visible in supplier lists
- Filtering capability by preferred status
- Audit trail for manual preference changes

#### REQ-SPM-004: Performance Analytics & Reporting [P1]
**Description:** System SHALL provide performance analytics dashboards.

**Specific Requirements:**
- **REQ-SPM-004.1**: Supplier rankings by category (top 10)
- **REQ-SPM-004.2**: Performance trend charts (6-month view)
- **REQ-SPM-004.3**: Comparative analysis between suppliers (side-by-side)
- **REQ-SPM-004.4**: Export reports to PDF and Excel
- **REQ-SPM-004.5**: Email scheduled reports (monthly) to procurement team

**Acceptance Criteria:**
- Dashboard loads within 3 seconds
- Charts interactive with drill-down capability
- Export includes all visible data

---

### 4.2 RFQ & Competitive Bidding

#### REQ-RFQ-001: RFQ Creation [P0]
**Description:** System SHALL allow users to create RFQs for components.

**Specific Requirements:**
- **REQ-RFQ-001.1**: Select single or multiple components
- **REQ-RFQ-001.2**: Specify quantity required
- **REQ-RFQ-001.3**: Set required delivery date
- **REQ-RFQ-001.4**: Add specification documents (PDF, images)
- **REQ-RFQ-001.5**: Set RFQ closing date/time
- **REQ-RFQ-001.6**: Add internal notes (not visible to suppliers)
- **REQ-RFQ-001.7**: Auto-generate unique RFQ number (format: RFQ-YYYY-NNNN)

**Acceptance Criteria:**
- RFQ saved as draft before sending
- Validation: quantity > 0, required date in future
- RFQ number unique and sequential

#### REQ-RFQ-002: Supplier Selection for RFQ [P0]
**Description:** System SHALL allow selection of suppliers to receive RFQ.

**Specific Requirements:**
- **REQ-RFQ-002.1**: Select from all active suppliers
- **REQ-RFQ-002.2**: Auto-suggest preferred suppliers for component category
- **REQ-RFQ-002.3**: Select minimum 2 suppliers, maximum 10 suppliers
- **REQ-RFQ-002.4**: Display supplier scorecard during selection
- **REQ-RFQ-002.5**: Filter suppliers by category, location, rating

**Acceptance Criteria:**
- Validation: at least 2 suppliers selected
- Preferred suppliers highlighted
- Inactive suppliers excluded

#### REQ-RFQ-003: RFQ Sending & Notification [P0]
**Description:** System SHALL send RFQs to selected suppliers and notify them.

**Specific Requirements:**
- **REQ-RFQ-003.1**: Email notification to supplier contacts
- **REQ-RFQ-003.2**: Email includes RFQ details, attachments, submission deadline
- **REQ-RFQ-003.3**: Track email sent status and timestamp
- **REQ-RFQ-003.4**: Status change: Draft → Sent
- **REQ-RFQ-003.5**: In-app notification for procurement team

**Acceptance Criteria:**
- Email delivery within 5 minutes
- Failed email alerts procurement team
- Email template professional and branded

#### REQ-RFQ-004: Quote Collection [P0]
**Description:** System SHALL collect supplier quotes for RFQs.

**Specific Requirements:**
- **REQ-RFQ-004.1**: Suppliers submit: unit price, lead time, MOQ, validity date
- **REQ-RFQ-004.2**: Suppliers can add notes/clarifications
- **REQ-RFQ-004.3**: Track quote submission timestamp
- **REQ-RFQ-004.4**: Allow quote revisions before RFQ closing
- **REQ-RFQ-004.5**: Auto-close RFQ at deadline (no more submissions)
- **REQ-RFQ-004.6**: Manual data entry for phone/fax quotes

**Acceptance Criteria:**
- Quote status: Pending → Submitted
- Notification to procurement on quote receipt
- Latest quote version used if multiple revisions

#### REQ-RFQ-005: Quote Comparison [P0]
**Description:** System SHALL provide comparison tools for quotes.

**Specific Requirements:**
- **REQ-RFQ-005.1**: Side-by-side comparison table with:
  - Supplier name and score
  - Unit price
  - Total price (unit price × quantity)
  - Lead time
  - Minimum order quantity
  - Quote validity
  - Delivery date (required date + lead time)
- **REQ-RFQ-005.2**: Highlight best price in green
- **REQ-RFQ-005.3**: Highlight best lead time in blue
- **REQ-RFQ-005.4**: Calculate total cost including estimated shipping
- **REQ-RFQ-005.5**: Sort by price, lead time, supplier score
- **REQ-RFQ-005.6**: Filter out quotes exceeding budget or timeline

**Acceptance Criteria:**
- Comparison updates real-time as quotes received
- Export comparison to Excel
- Visual indicators for best options

#### REQ-RFQ-006: RFQ Award [P0]
**Description:** System SHALL allow awarding RFQ to selected supplier.

**Specific Requirements:**
- **REQ-RFQ-006.1**: Select winning quote and provide award justification
- **REQ-RFQ-006.2**: Auto-generate Purchase Order from awarded RFQ
- **REQ-RFQ-006.3**: Notify winning supplier via email
- **REQ-RFQ-006.4**: Notify non-selected suppliers (optional)
- **REQ-RFQ-006.5**: Status change: Quotes Received → Awarded
- **REQ-RFQ-006.6**: Record award decision maker and timestamp

**Acceptance Criteria:**
- PO pre-filled with RFQ and quote data
- Award cannot be changed once PO approved
- Audit trail of award decision

#### REQ-RFQ-007: RFQ Lifecycle Management [P1]
**Description:** System SHALL manage complete RFQ lifecycle.

**Specific Requirements:**
- **REQ-RFQ-007.1**: RFQ status workflow: Draft → Sent → Quotes Received → Awarded/Cancelled
- **REQ-RFQ-007.2**: Cancel RFQ before or after sending (with reason)
- **REQ-RFQ-007.3**: Extend RFQ deadline (notify suppliers)
- **REQ-RFQ-007.4**: Clone RFQ for similar requirements
- **REQ-RFQ-007.5**: Archive completed RFQs after 90 days

**Acceptance Criteria:**
- Status transitions logged with user and timestamp
- Cancelled RFQs do not create POs
- Deadline extensions notify all suppliers

---

### 4.3 Contract Management

#### REQ-CON-001: Contract Creation [P0]
**Description:** System SHALL allow creation of supplier contracts.

**Specific Requirements:**
- **REQ-CON-001.1**: Auto-generate contract number (format: CONTRACT-YYYY-NNNN)
- **REQ-CON-001.2**: Link contract to supplier
- **REQ-CON-001.3**: Define start and end dates
- **REQ-CON-001.4**: Set payment terms (Net 30, Net 60, Net 90, Custom)
- **REQ-CON-001.5**: Upload contract document (PDF, max 10MB)
- **REQ-CON-001.6**: Add internal notes and approval workflow
- **REQ-CON-001.7**: Define auto-renewal terms (yes/no, notice period)

**Acceptance Criteria:**
- Contract number unique and sequential
- End date must be after start date
- Payment terms validated
- Contract document required for activation

#### REQ-CON-002: Volume-Based Pricing [P0]
**Description:** System SHALL support tiered volume discounts in contracts.

**Specific Requirements:**
- **REQ-CON-002.1**: Define pricing tiers: [min_quantity, max_quantity, discount_%]
- **REQ-CON-002.2**: Support up to 10 tiers per contract
- **REQ-CON-002.3**: Validate tier ranges do not overlap
- **REQ-CON-002.4**: Auto-apply discount in PO based on order quantity
- **REQ-CON-002.5**: Display applicable discount in PO preview

**Example Tiers:**
```json
[
  {"min_qty": 1, "max_qty": 99, "discount_pct": 0},
  {"min_qty": 100, "max_qty": 499, "discount_pct": 5},
  {"min_qty": 500, "max_qty": null, "discount_pct": 10}
]
```

**Acceptance Criteria:**
- Tier validation on save
- Discounts calculated correctly in PO
- Visual tier display in contract view

#### REQ-CON-003: Contract Pricing Management [P0]
**Description:** System SHALL manage component pricing within contracts.

**Specific Requirements:**
- **REQ-CON-003.1**: Add multiple components to contract
- **REQ-CON-003.2**: Set unit price per component
- **REQ-CON-003.3**: Set minimum order quantity per component
- **REQ-CON-003.4**: Set lead time in days per component
- **REQ-CON-003.5**: Mark components as active/inactive in contract
- **REQ-CON-003.6**: Price effective dates (override contract dates if needed)

**Acceptance Criteria:**
- Component pricing auto-populates in PO creation
- Price history maintained for auditing
- Inactive components excluded from PO selection

#### REQ-CON-004: Contract Status & Lifecycle [P0]
**Description:** System SHALL manage contract status throughout lifecycle.

**Specific Requirements:**
- **REQ-CON-004.1**: Status: Draft → Active → Expired/Cancelled
- **REQ-CON-004.2**: Auto-activate on start date
- **REQ-CON-004.3**: Auto-expire on end date
- **REQ-CON-004.4**: Manual cancellation with reason
- **REQ-CON-004.5**: Only active contracts used for PO pricing
- **REQ-CON-004.6**: Prevent editing of expired/cancelled contracts

**Acceptance Criteria:**
- Daily job checks for contract activations/expirations
- Status changes logged with timestamp
- PO creation blocks with expired contract

#### REQ-CON-005: Contract Renewal Alerts [P1]
**Description:** System SHALL alert users of expiring contracts.

**Specific Requirements:**
- **REQ-CON-005.1**: Alert procurement team 90, 60, 30 days before expiry
- **REQ-CON-005.2**: Email and in-app notifications
- **REQ-CON-005.3**: Dashboard widget showing contracts expiring within 60 days
- **REQ-CON-005.4**: Bulk renewal action for multiple contracts
- **REQ-CON-005.5**: Renewal creates new contract (clone with new dates)

**Acceptance Criteria:**
- Alerts sent at 9 AM system time
- Alert frequency configurable
- Suppression option for contracts already renewed

#### REQ-CON-006: Blanket Purchase Orders [P2]
**Description:** System SHALL support blanket POs (call-off orders).

**Specific Requirements:**
- **REQ-CON-006.1**: Create blanket PO with total quantity and value
- **REQ-CON-006.2**: Define release schedule (weekly, monthly, on-demand)
- **REQ-CON-006.3**: Track released quantity vs total
- **REQ-CON-006.4**: Generate release orders against blanket PO
- **REQ-CON-006.5**: Auto-close blanket PO when fully released or end date reached

**Acceptance Criteria:**
- Released quantity cannot exceed blanket total
- Release orders link to parent blanket PO
- Financial commitment tracked separately

---

### 4.4 Inventory Optimization

#### REQ-INV-001: Component Inventory Policies [P0]
**Description:** System SHALL maintain inventory policies per component.

**Specific Requirements:**
- **REQ-INV-001.1**: Store reorder point (ROP) per component
- **REQ-INV-001.2**: Store safety stock level
- **REQ-INV-001.3**: Store economic order quantity (EOQ)
- **REQ-INV-001.4**: Store ABC classification (A/B/C)
- **REQ-INV-001.5**: Store average monthly demand
- **REQ-INV-001.6**: Store lead time in days
- **REQ-INV-001.7**: Last policy update date and user

**Acceptance Criteria:**
- Policies editable by warehouse and procurement roles
- Policy changes audited
- Default values for new components

#### REQ-INV-002: Reorder Point Calculation [P0]
**Description:** System SHALL calculate optimal reorder points.

**Formula:**  
```
ROP = (Average Daily Demand × Lead Time) + Safety Stock
Safety Stock = Z-score × σ × √Lead Time
```

**Specific Requirements:**
- **REQ-INV-002.1**: Calculate average daily demand from last 90 days consumption
- **REQ-INV-002.2**: Use configurable service level (default 95% = Z-score 1.65)
- **REQ-INV-002.3**: Calculate demand standard deviation (σ)
- **REQ-INV-002.4**: Use supplier's average lead time
- **REQ-INV-002.5**: Manual override capability
- **REQ-INV-002.6**: Recalculate monthly or on-demand

**Acceptance Criteria:**
- ROP calculation accurate within ±5%
- Calculation factors in seasonality (future)
- Manual overrides logged

#### REQ-INV-003: Economic Order Quantity Calculation [P0]
**Description:** System SHALL calculate optimal order quantities.

**Formula:**  
```
EOQ = √[(2 × Annual Demand × Ordering Cost) / Holding Cost per Unit]
```

**Specific Requirements:**
- **REQ-INV-003.1**: Calculate annual demand from historical data
- **REQ-INV-003.2**: Use configurable ordering cost (default $50 per order)
- **REQ-INV-003.3**: Calculate holding cost as % of unit cost (default 25% annually)
- **REQ-INV-003.4**: Round EOQ to nearest practical quantity
- **REQ-INV-003.5**: Apply supplier MOQ constraint
- **REQ-INV-003.6**: Recalculate when cost or demand changes significantly

**Acceptance Criteria:**
- EOQ calculation matches manual calculations
- Respects supplier minimum order quantities
- Updates trigger notification to buyer

#### REQ-INV-004: ABC Analysis [P1]
**Description:** System SHALL classify inventory using ABC analysis.

**Criteria:**
- **Class A**: Top 20% of items by value (typically 70-80% of total value)
- **Class B**: Next 30% of items (typically 15-20% of total value)
- **Class C**: Remaining 50% of items (typically 5-10% of total value)

**Specific Requirements:**
- **REQ-INV-004.1**: Calculate annual value = annual usage × unit cost
- **REQ-INV-004.2**: Sort components by annual value (descending)
- **REQ-INV-004.3**: Auto-classify into A/B/C based on cumulative percentage
- **REQ-INV-004.4**: Allow manual override of classification
- **REQ-INV-004.5**: Run analysis monthly
- **REQ-INV-004.6**: Visual chart showing distribution

**Acceptance Criteria:**
- Classification aligns with Pareto principle (80/20 rule)
- Manual overrides respected
- Charts exportable

#### REQ-INV-005: Demand Forecasting [P1]
**Description:** System SHALL forecast component demand.

**Methods (Phase 1):**
1. **Simple Moving Average (SMA)**  
   `Forecast = (Month[t-1] + Month[t-2] + Month[t-3]) / 3`
   
2. **Weighted Moving Average (WMA)**  
   `Forecast = (3×Month[t-1] + 2×Month[t-2] + 1×Month[t-3]) / 6`

**Specific Requirements:**
- **REQ-INV-005.1**: Store monthly actual demand
- **REQ-INV-005.2**: Calculate 3-month forecast using SMA and WMA
- **REQ-INV-005.3**: Track forecast accuracy (MAPE - Mean Absolute Percentage Error)
- **REQ-INV-005.4**: Auto-select best method based on historical accuracy
- **REQ-INV-005.5**: Display forecast vs actual trend chart
- **REQ-INV-005.6**: Edit forecast manually if needed

**Acceptance Criteria:**
- Forecast generated monthly
- Accuracy metrics visible
- Forecast influences ROP calculations

#### REQ-INV-006: Automated Purchase Requisition Generation [P0]
**Description:** System SHALL auto-generate PRs for components below ROP.

**Specific Requirements:**
- **REQ-INV-006.1**: Daily job checks all component stock levels
- **REQ-INV-006.2**: If current stock < ROP, create PR
- **REQ-INV-006.3**: PR quantity = EOQ (or reorder_quantity if EOQ not set)
- **REQ-INV-006.4**: PR priority based on (ROP - current stock):
  - High: stock < 50% of ROP
  - Medium: stock 50-75% of ROP  
  - Low: stock 75-100% of ROP
- **REQ-INV-006.5**: Set expected delivery date = today + lead time
- **REQ-INV-006.6**: Prevent duplicate PRs (check for pending PRs for same component)
- **REQ-INV-006.7**: Notification to procurement team
- **REQ-INV-006.8**: Auto-PR can be disabled per component

**Acceptance Criteria:**
- Job runs daily at 8 AM
- No duplicate PRs created
- PRs created with status "Pending"
- Notification sent with component list

#### REQ-INV-007: Stock Level Dashboard [P1]
**Description:** System SHALL provide inventory optimization dashboard.

**Specific Requirements:**
- **REQ-INV-007.1**: List components below ROP (red alert)
- **REQ-INV-007.2**: List components near ROP (yellow warning, 90-100% of ROP)
- **REQ-INV-007.3**: ABC analysis chart
- **REQ-INV-007.4**: Stock value by category
- **REQ-INV-007.5**: Forecast vs actual demand charts
- **REQ-INV-007.6**: Excess stock report (stock > 6 months demand)
- **REQ-INV-007.7**: Slow-moving items (no usage in 90 days)

**Acceptance Criteria:**
- Dashboard loads within 3 seconds
- Real-time data (refreshes on page load)
- Drill-down to component details

---

### 4.5 Cost Analysis & Reporting

#### REQ-COST-001: Price History Tracking [P0]
**Description:** System SHALL maintain complete price history for all components.

**Specific Requirements:**
- **REQ-COST-001.1**: Record price change when:
  - New PO created
  - Contract pricing updated
  - Component cost manually edited
- **REQ-COST-001.2**: Store: component_id, supplier_id, price, effective_date, source
- **REQ-COST-001.3**: Retain price history indefinitely
- **REQ-COST-001.4**: Display price trend chart (last 12 months)
- **REQ-COST-001.5**: Calculate price change %
- **REQ-COST-001.6**: Alert on price increase > 10%

**Acceptance Criteria:**
- Price changes recorded automatically
- History queryable by component and supplier
- Alerts sent to procurement and finance

#### REQ-COST-002: Cost Variance Analysis [P0]
**Description:** System SHALL analyze actual costs vs standard/budgeted costs.

**Specific Requirements:**
- **REQ-COST-002.1**: Define standard cost per component (baseline)
- **REQ-COST-002.2**: Calculate variance = (actual cost - standard cost) / standard cost × 100
- **REQ-COST-002.3**: Categorize variance:
  - Favorable: actual < standard (green)
  - Unfavorable: actual > standard (red)
- **REQ-COST-002.4**: Report by component, category, supplier
- **REQ-COST-002.5**: MTD (Month-to-Date) and YTD (Year-to-Date) variance
- **REQ-COST-002.6**: Drill-down to PO level

**Acceptance Criteria:**
- Variance calculated at PO receipt
- Reports exportable to Excel
- Configurable variance thresholds for alerts

#### REQ-COST-003: Spend Analysis [P0]
**Description:** System SHALL provide comprehensive spend analysis.

**Specific Requirements:**
- **REQ-COST-003.1**: Total spend by:
  - Supplier
  - Category
  - Component
  - Time period (month, quarter, year)
- **REQ-COST-003.2**: Top 10 suppliers by spend
- **REQ-COST-003.3**: Top 10 components by spend
- **REQ-COST-003.4**: Spend concentration analysis (% of spend with top suppliers)
- **REQ-COST-003.5**: Visual charts: pie, bar, trend line
- **REQ-COST-003.6**: Comparison between periods (MoM, YoY)

**Acceptance Criteria:**
- Data based on PO receipts and invoices
- Filters by date range, supplier, category
- Export to PDF and Excel

#### REQ-COST-004: Budget Management [P1]
**Description:** System SHALL support procurement budget tracking.

**Specific Requirements:**
- **REQ-COST-004.1**: Define annual budget by:
  - Overall procurement
  - Category
  - Supplier (optional)
- **REQ-COST-004.2**: Track actual spend against budget
- **REQ-COST-004.3**: Calculate variance and % consumed
- **REQ-COST-004.4**: Alert when budget 80%, 90%, 100% consumed
- **REQ-COST-004.5**: Monthly budget consumption report
- **REQ-COST-004.6**: Budget vs actual forecast (remaining months)

**Acceptance Criteria:**
- Budget editable by finance and procurement manager
- Real-time budget consumption tracking
- Monthly reports emailed to stakeholders

#### REQ-COST-005: Total Cost of Ownership (TCO) [P2]
**Description:** System SHOULD calculate total cost of ownership for components.

**TCO Components:**
```
TCO = Purchase Price + Ordering Cost + Holding Cost + Quality Cost + Delivery Cost
```

**Specific Requirements:**
- **REQ-COST-005.1**: Purchase price: unit price × quantity
- **REQ-COST-005.2**: Ordering cost: average cost per PO
- **REQ-COST-005.3**: Holding cost: (average inventory value) × (holding cost %)
- **REQ-COST-005.4**: Quality cost: rework/scrap cost from quality module
- **REQ-COST-005.5**: Delivery cost: freight, customs, delays
- **REQ-COST-005.6**: Compare TCO between suppliers

**Acceptance Criteria:**
- TCO calculated quarterly
- Cost breakdown visible
- Supplier comparison report

#### REQ-COST-006: Price Trend Alerts [P1]
**Description:** System SHALL alert on significant price trends.

**Specific Requirements:**
- **REQ-COST-006.1**: Alert on price increase > 10% from previous PO
- **REQ-COST-006.2**: Alert on price increase > 5% from contract price
- **REQ-COST-006.3**: Weekly market trend report (if external data available)
- **REQ-COST-006.4**: Alert on extended lead time (> 20% increase)
- **REQ-COST-006.5**: Configurable alert thresholds

**Acceptance Criteria:**
- Alerts sent to procurement and finance
- Include component, supplier, old/new price
- Option to approve or reject PO with price increase

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

#### REQ-PERF-001: Response Time [P0]
- Dashboard pages SHALL load within 3 seconds (90th percentile)
- API endpoints SHALL respond within 500ms for read operations
- API endpoints SHALL respond within 2 seconds for write operations
- Report generation SHALL complete within 10 seconds for standard reports
- Complex analytics (ABC analysis, forecasting) SHALL complete within 30 seconds

#### REQ-PERF-002: Scalability [P0]
- System SHALL support 10,000+ components
- System SHALL support 500+ suppliers
- System SHALL support 1,000+ concurrent RFQs
- System SHALL handle 100 concurrent users
- System SHALL process 10,000+ POs per year

#### REQ-PERF-003: Database Performance [P0]
- Database queries SHALL use proper indexing
- Critical tables SHALL have indexes on foreign keys and filter columns
- Aggregate queries SHALL use materialized views where appropriate
- Historical data archival after 3 years (soft delete)

### 5.2 Reliability & Availability

#### REQ-REL-001: Availability [P0]
- System uptime SHALL be 99.5% during business hours (6 AM - 8 PM)
- Planned maintenance SHALL occur outside business hours
- Automated database backups daily at 2 AM
- Disaster recovery plan with 24-hour recovery time objective (RTO)

#### REQ-REL-002: Data Integrity [P0]
- All database transactions SHALL be ACID-compliant
- Critical operations (RFQ award, PO approval) SHALL use database transactions
- Data validation at API layer before persistence
- Referential integrity enforced via foreign key constraints
- No orphaned records (cascade deletes where appropriate)

#### REQ-REL-003: Error Handling [P0]
- User-friendly error messages for all failures
- Detailed logging for debugging (Winston or equivalent)
- Automatic retry for transient failures (3 attempts)
- Email alerts for critical errors to system admin

### 5.3 Usability Requirements

#### REQ-USE-001: User Interface [P0]
- Consistent UI/UX with existing MTO360 design system
- Ant Design components for React frontend
- Responsive design (desktop 1920×1080, tablet 1024×768)
- Mobile-friendly views for dashboards (view-only)
- Accessibility compliance (WCAG 2.1 Level AA)

#### REQ-USE-002: Navigation [P0]
- Maximum 3 clicks to reach any function
- Breadcrumb navigation on all pages
- Contextual help tooltips on complex fields
- Keyboard shortcuts for common actions (Ctrl+S save, Esc cancel)

#### REQ-USE-003: Data Entry [P0]
- Form validation with inline error messages
- Auto-save for long forms (drafts)
- Required fields clearly marked with asterisk
- Dropdown selections for controlled vocabularies
- Date pickers for date fields
- Numeric input validation (min, max, decimal places)

#### REQ-USE-004: Documentation [P1]
- User manual with screenshots
- Context-sensitive help (F1 key)
- Video tutorials for complex workflows (RFQ, contracts)
- FAQ section
- Release notes for updates

### 5.4 Compatibility Requirements

#### REQ-COMP-001: Browser Support [P0]
- Google Chrome (latest 2 versions)
- Microsoft Edge (latest 2 versions)
- Mozilla Firefox (latest 2 versions)
- Safari (latest version) - view-only

#### REQ-COMP-002: Backend Technology [P0]
- Python 3.11+
- FastAPI framework
- PostgreSQL 14+
- SQLAlchemy 2.0 ORM
- Alembic for migrations

#### REQ-COMP-003: Frontend Technology [P0]
- React 18+
- TypeScript
- Ant Design 5
- React Query for data fetching
- React Router for navigation

### 5.5 Maintainability Requirements

#### REQ-MAIN-001: Code Quality [P0]
- Backend code SHALL follow PEP 8 style guide
- Frontend code SHALL use ESLint and Prettier
- Minimum 70% unit test coverage
- Integration tests for critical workflows
- Code reviews required for all changes

#### REQ-MAIN-002: Documentation [P0]
- API documentation using OpenAPI/Swagger
- Database schema diagrams (ERD)
- Architecture diagrams (C4 model)
- Inline code comments for complex logic
- README files in each module directory

#### REQ-MAIN-003: Logging & Monitoring [P0]
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Sensitive data (passwords, PII) excluded from logs
- Log retention: 90 days
- Application performance monitoring (APM) integration ready

---

## 6. Integration Requirements

### 6.1 Internal Module Integration

#### REQ-INT-001: Inventory Module Integration [P0]
**Description:** Seamless integration with existing inventory module.

**Specific Requirements:**
- **REQ-INT-001.1**: Extend `Supplier` model with performance fields
- **REQ-INT-001.2**: Extend `Component` model with policy fields (ROP, safety stock, EOQ, ABC)
- **REQ-INT-001.3**: Use existing `PurchaseOrder` and `PurchaseRequisition` models
- **REQ-INT-001.4**: Trigger inventory policy recalculation on component usage
- **REQ-INT-001.5**: Update component cost from latest PO pricing

**Acceptance Criteria:**
- No breaking changes to existing inventory APIs
- Database migration scripts for schema extensions
- Backward compatibility maintained

#### REQ-INT-002: Quality Module Integration [P0]
**Description:** Integrate supplier quality ratings from quality module.

**Specific Requirements:**
- **REQ-INT-002.1**: Pull defect rate data from quality inspections
- **REQ-INT-002.2**: Calculate supplier quality score from NCRs (Non-Conformance Reports)
- **REQ-INT-002.3**: Link quality issues to specific suppliers and POs
- **REQ-INT-002.4**: Quality score updated in supplier performance monthly

**Acceptance Criteria:**
- Quality data accessible via quality module API
- Supplier scorecard includes quality metrics
- Traceability from defect to supplier

#### REQ-INT-003: Manufacturing Module Integration [P1]
**Description:** Provide material availability forecasting for production.

**Specific Requirements:**
- **REQ-INT-003.1**: API endpoint to check component availability for MO
- **REQ-INT-003.2**: Calculate material ready date based on:
  - Current stock
  - Pending POs (expected delivery dates)
  - Lead times
- **REQ-INT-003.3**: Flag components with insufficient availability
- **REQ-INT-003.4**: Suggest PR creation for shortage

**Acceptance Criteria:**
- Manufacturing scheduler can query availability
- Availability considers pending orders
- Suggestions actionable (create PR from UI)

#### REQ-INT-004: Sales Module Integration [P1]
**Description:** Link delivery promises to supplier lead times.

**Specific Requirements:**
- **REQ-INT-004.1**: Sales order creation checks material availability
- **REQ-INT-004.2**: Calculate earliest delivery date considering:
  - Current stock
  - Supplier lead times
  - Manufacturing lead time
- **REQ-INT-004.3**: Alert sales team if delivery date not achievable
- **REQ-INT-004.4**: Track on-time delivery by sales order

**Acceptance Criteria:**
- Sales order workflow integrates availability check
- Unrealistic delivery dates flagged
- Customer-facing delivery estimates accurate

#### REQ-INT-005: Notifications Module Integration [P0]
**Description:** Send notifications for procurement events.

**Notification Types:**
- RFQ sent to suppliers
- Quote received
- Contract expiring (90, 60, 30 days)
- Stock below ROP
- Auto-PR created
- Price increase alert
- Budget threshold reached

**Specific Requirements:**
- **REQ-INT-005.1**: Use existing notification service
- **REQ-INT-005.2**: Support email and in-app notifications
- **REQ-INT-005.3**: User preferences for notification types
- **REQ-INT-005.4**: Notification templates for each event type
- **REQ-INT-005.5**: Batch notifications (daily digest option)

**Acceptance Criteria:**
- Notifications sent within 5 minutes of event
- User can opt-in/opt-out per notification type
- Email templates professional and clear

### 6.2 External Integration Preparedness

#### REQ-INT-006: External API Readiness [P2]
**Description:** System SHOULD be ready for future external integrations.

**Specific Requirements:**
- RESTful API design with versioning (/api/v1/...)
- API authentication using JWT tokens
- Rate limiting (100 requests/minute per API key)
- API documentation (OpenAPI 3.0)
- Webhook support for event notifications

**Acceptance Criteria:**
- API endpoints documented
- External clients can authenticate
- Webhooks tested with sample client

---

## 7. Security & Compliance

### 7.1 Authentication & Authorization

#### REQ-SEC-001: Authentication [P0]
- Users SHALL authenticate using existing MTO360 auth system
- JWT tokens for API access
- Session timeout after 8 hours of inactivity
- Password policy: min 8 chars, 1 upper, 1 lower, 1 number, 1 special

#### REQ-SEC-002: Authorization [P0]
- Role-based access control (RBAC)
- Permissions enforced at API layer
- Sensitive actions require additional confirmation (delete, approve)
- Audit trail for all permission changes

### 7.2 Data Security

#### REQ-SEC-003: Data Protection [P0]
- Passwords hashed using bcrypt (cost factor 12)
- Sensitive data (PII, financial) encrypted at rest (AES-256)
- TLS 1.3 for data in transit (HTTPS)
- Database connections encrypted
- No sensitive data in logs or error messages

#### REQ-SEC-004: Input Validation [P0]
- All user inputs sanitized (prevent XSS, SQL injection)
- File uploads scanned for malware
- File type and size validation (max 10MB)
- Parameterized SQL queries (ORM protection)

### 7.3 Audit & Compliance

#### REQ-SEC-005: Audit Trail [P0]
**Description:** System SHALL maintain comprehensive audit logs.

**Logged Events:**
- User login/logout
- RFQ creation, send, award
- Contract creation, approval, cancellation
- PO creation, approval
- Price changes
- Permission changes
- Data exports

**Audit Log Fields:**
- Timestamp
- User ID and username
- Action type
- Entity type and ID
- Old value / New value (for updates)
- IP address
- User agent

**Acceptance Criteria:**
- Audit logs immutable (append-only)
- Retention: 7 years (compliance)
- Searchable and exportable

#### REQ-SEC-006: Data Privacy [P0]
- GDPR compliance for EU users (data portability, right to be forgotten)
- Supplier contact data minimal (only business info)
- Data retention policy (3 years active, 7 years archived)
- Personal data anonymization in reports

### 7.4 Business Continuity

#### REQ-SEC-007: Backup & Recovery [P0]
- Daily automated database backups (2 AM)
- Backups stored offsite (cloud storage)
- Weekly backup restoration tests
- Backup retention: 30 days
- Point-in-time recovery capability

#### REQ-SEC-008: Disaster Recovery [P1]
- Recovery Time Objective (RTO): 24 hours
- Recovery Point Objective (RPO): 24 hours
- Documented disaster recovery plan
- Annual DR drill

---

## 8. User Stories

### 8.1 Supplier Performance Management

**US-SPM-001: Track Supplier Performance**  
**As a** Procurement Manager  
**I want to** view supplier performance scorecards  
**So that** I can make informed decisions on supplier selection and identify underperformers

**Acceptance Criteria:**
- Scorecard displays on-time delivery, quality, price, responsiveness
- Overall score calculated with configurable weights
- Historical trend visible (6 months)
- Exportable to PDF

---

**US-SPM-002: Identify Preferred Suppliers**  
**As a** Buyer  
**I want to** see preferred suppliers for each category  
**So that** I can prioritize them for RFQs and POs

**Acceptance Criteria:**
- Preferred suppliers auto-suggested based on score ≥75
- Manual override capability
- Preferred badge visible in supplier lists

---

### 8.2 RFQ & Competitive Bidding

**US-RFQ-001: Create RFQ**  
**As a** Buyer  
**I want to** create an RFQ for multiple components  
**So that** I can get competitive quotes from suppliers

**Acceptance Criteria:**
- Select components, quantities, delivery dates
- Attach specifications
- Generate unique RFQ number
- Save as draft before sending

---

**US-RFQ-002: Compare Supplier Quotes**  
**As a** Procurement Manager  
**I want to** compare quotes side-by-side  
**So that** I can award the best value supplier

**Acceptance Criteria:**
- Table shows price, lead time, MOQ, supplier score
- Best price and lead time highlighted
- Sort by any column
- Export comparison to Excel

---

**US-RFQ-003: Award RFQ**  
**As a** Procurement Manager  
**I want to** award the RFQ to the selected supplier  
**So that** a PO is automatically created

**Acceptance Criteria:**
- Select winning quote
- Provide award justification
- Auto-generate PO with quote details
- Notify winning and non-winning suppliers

---

### 8.3 Contract Management

**US-CON-001: Create Supplier Contract**  
**As a** Procurement Manager  
**I want to** create a contract with volume discounts  
**So that** I can secure better pricing for bulk orders

**Acceptance Criteria:**
- Define contract dates, payment terms
- Set up tiered pricing (qty ranges and discounts)
- Upload contract PDF
- Generate unique contract number

---

**US-CON-002: Get Contract Expiry Alerts**  
**As a** Procurement Manager  
**I want to** receive alerts for expiring contracts  
**So that** I can renew them before they expire

**Acceptance Criteria:**
- Alerts at 90, 60, 30 days before expiry
- Email and in-app notifications
- Dashboard widget shows expiring contracts
- One-click renewal (clone with new dates)

---

### 8.4 Inventory Optimization

**US-INV-001: Set Reorder Points**  
**As a** Warehouse Manager  
**I want to** set reorder points for components  
**So that** I never run out of stock

**Acceptance Criteria:**
- Calculate ROP based on lead time and demand
- Set safety stock buffer
- System suggests optimal ROP
- Manual override capability

---

**US-INV-002: Auto-Generate Purchase Requisitions**  
**As a** Procurement Manager  
**I want to** automatically generate PRs when stock is low  
**So that** I don't have to manually monitor inventory

**Acceptance Criteria:**
- Daily job checks all components
- PRs created when stock < ROP
- PR quantity = EOQ
- Notification sent to procurement team

---

**US-INV-003: Forecast Demand**  
**As a** Inventory Planner  
**I want to** view demand forecasts for components  
**So that** I can plan procurement proactively

**Acceptance Criteria:**
- 3-month forecast using moving average
- Forecast vs actual chart
- Forecast accuracy (MAPE) displayed
- Manual forecast override

---

### 8.5 Cost Analysis

**US-COST-001: Track Price History**  
**As a** Procurement Manager  
**I want to** view price history for components  
**So that** I can identify price trends and negotiate better

**Acceptance Criteria:**
- Price trend chart (12 months)
- List of price changes with dates
- Calculate price change %
- Filter by supplier

---

**US-COST-002: Analyze Spend by Supplier**  
**As a** Finance Manager  
**I want to** view spend analysis by supplier  
**So that** I can identify top suppliers and optimize spend

**Acceptance Criteria:**
- Total spend per supplier (YTD, MTD)
- Top 10 suppliers chart
- Spend concentration (% with top 3 suppliers)
- Export to Excel

---

**US-COST-003: Monitor Budget Consumption**  
**As a** Finance Manager  
**I want to** track procurement budget vs actual  
**So that** I can prevent overspending

**Acceptance Criteria:**
- Set annual budget by category
- Real-time budget consumption %
- Alerts at 80%, 90%, 100% consumed
- Monthly budget report emailed

---

## 9. Acceptance Criteria

### 9.1 Feature Acceptance

Each feature SHALL be accepted only when:

1. **Functionality**
   - All P0 and P1 requirements implemented
   - All user stories satisfied
   - No critical or high-severity bugs

2. **Code Quality**
   - Unit test coverage ≥70%
   - Integration tests pass
   - Code review approved
   - No linting errors

3. **Performance**
   - Response time requirements met
   - Load testing passed (100 concurrent users)
   - Database queries optimized

4. **Documentation**
   - API documentation complete
   - User manual updated
   - Database migrations tested

5. **Security**
   - Security review passed
   - Penetration testing completed (if applicable)
   - OWASP Top 10 vulnerabilities addressed

### 9.2 Phase Acceptance

Each implementation phase SHALL be accepted when:

1. **Phase 1: Supplier Performance** (Weeks 1-2)
   - REQ-SPM-001 to REQ-SPM-004 implemented
   - US-SPM-001, US-SPM-002 satisfied
   - Performance dashboard functional
   - Data migration from existing supplier table

2. **Phase 2: RFQ & Bidding** (Weeks 3-4)
   - REQ-RFQ-001 to REQ-RFQ-007 implemented
   - US-RFQ-001, US-RFQ-002, US-RFQ-003 satisfied
   - Email notifications working
   - RFQ to PO conversion tested

3. **Phase 3: Contract Management** (Weeks 5-6)
   - REQ-CON-001 to REQ-CON-006 implemented
   - US-CON-001, US-CON-002 satisfied
   - Volume discount calculations correct
   - Contract renewal workflow tested

4. **Phase 4: Inventory Optimization** (Weeks 7-8)
   - REQ-INV-001 to REQ-INV-007 implemented
   - US-INV-001, US-INV-002, US-INV-003 satisfied
   - ROP, EOQ, ABC calculations verified
   - Auto-PR generation tested

5. **Phase 5: Cost Analysis** (Weeks 9-10)
   - REQ-COST-001 to REQ-COST-006 implemented
   - US-COST-001, US-COST-002, US-COST-003 satisfied
   - Reports accurate and exportable
   - Budget tracking functional

### 9.3 Project Acceptance

The entire Advanced Procurement project SHALL be accepted when:

1. **All Phases Complete**
   - All 5 phases accepted individually
   - End-to-end workflows tested (RFQ → PO → Receipt → Analysis)

2. **Integration Verified**
   - Inventory module integration tested
   - Quality module integration tested
   - Manufacturing material availability working
   - Notifications functioning

3. **User Acceptance Testing (UAT)**
   - UAT plan executed
   - All critical user scenarios passed
   - User training completed
   - User feedback incorporated

4. **Production Readiness**
   - Production deployment plan reviewed
   - Database migrations tested on production clone
   - Rollback plan documented
   - Monitoring and alerting configured

5. **Documentation Complete**
   - User manual finalized
   - Admin guide finalized
   - API documentation published
   - Training materials delivered

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **ABC Analysis** | Inventory categorization method (A=high value, B=medium, C=low) |
| **Blanket PO** | Long-term PO with multiple release orders |
| **EOQ** | Economic Order Quantity - optimal order size to minimize costs |
| **MAPE** | Mean Absolute Percentage Error - forecast accuracy metric |
| **MOQ** | Minimum Order Quantity - smallest order supplier will accept |
| **NCR** | Non-Conformance Report - quality issue documentation |
| **RFQ** | Request for Quotation - solicitation for supplier quotes |
| **ROP** | Reorder Point - stock level triggering replenishment |
| **TCO** | Total Cost of Ownership - all costs associated with purchasing |
| **YTD** | Year-to-Date - from January 1 to current date |
| **MTD** | Month-to-Date - from 1st of month to current date |

---

## Appendix B: Assumptions & Constraints

### Assumptions
1. Existing MTO360 modules (inventory, quality, manufacturing) are stable
2. Suppliers willing to participate in RFQ process
3. Historical data available for demand forecasting (at least 6 months)
4. Users have basic procurement knowledge
5. Email server configured for notifications

### Constraints
1. Budget: $18,750 for development (250 hours @ $75/hour)
2. Timeline: 10 weeks (including UAT)
3. Team: 2-3 developers
4. Technology stack: Python/FastAPI, React/TypeScript, PostgreSQL
5. Browser support: Chrome, Edge, Firefox only

---

## Appendix C: Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2025-11-25 | AI Assistant | Initial draft for review |

---

**Document Status:** DRAFT - Pending Stakeholder Review

**Next Steps:**
1. Review by Product Management
2. Review by Technical Lead
3. Review by Finance
4. Approval and sign-off
5. Create detailed design document
