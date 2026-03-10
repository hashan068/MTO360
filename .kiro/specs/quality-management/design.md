# Quality Management System (QMS) - Design

## Architecture Overview

This feature extends the Manufacturing module with quality management capabilities, adding new entities and services for inspections, defects, non-conformances, and corrective actions.

## Data Model

### New Entities

#### InspectionPoint
```python
class InspectionPoint(Base, TimestampMixin):
    id: int
    route_operation_id: Optional[int]  # FK to RouteOperation (template)
    inspection_type: InspectionTypeEnum  # in_process, final, receiving, first_article
    name: str  # e.g., "PCB Visual Inspection"
    description: Optional[str]
    is_required: bool  # Blocks operation if failed
    checklist_items: JSON  # List of inspection criteria
    
    # Relationships
    route_operation: RouteOperation
    inspection_results: List[InspectionResult]
```

#### InspectionResult
```python
class InspectionResult(Base, TimestampMixin):
    id: int
    inspection_point_id: int  # FK to InspectionPoint
    mo_operation_id: Optional[int]  # FK to ManufacturingOrderOperation
    manufacturing_order_id: Optional[int]  # FK to ManufacturingOrder (for final inspection)
    component_id: Optional[int]  # FK to Component (for receiving inspection)
    
    # Inspector
    inspector_id: int  # FK to User
    inspection_date: datetime
    
    # Result
    result: InspectionResultEnum  # pass, fail, conditional
    checklist_results: JSON  # Results for each checklist item
    measurements: JSON  # Actual measurements
    notes: Optional[str]
    
    # Attachments
    photo_urls: JSON  # List of photo URLs
    document_urls: JSON  # List of document URLs
    
    # Relationships
    inspection_point: InspectionPoint
    mo_operation: Optional[ManufacturingOrderOperation]
    manufacturing_order: Optional[ManufacturingOrder]
    component: Optional[Component]
    inspector: User
    defects: List[Defect]  # Defects found during inspection
```

#### Defect
```python
class Defect(Base, TimestampMixin):
    id: int
    defect_number: str  # Auto-generated: DEF-YYYYMMDD-XXXX
    
    # Context
    manufacturing_order_id: Optional[int]  # FK to ManufacturingOrder
    mo_operation_id: Optional[int]  # FK to ManufacturingOrderOperation
    inspection_result_id: Optional[int]  # FK to InspectionResult
    component_id: Optional[int]  # FK to Component (material defect)
    sales_order_id: Optional[int]  # FK to SalesOrder (customer return)
    
    # Classification
    defect_type: DefectTypeEnum  # material, workmanship, design, other
    defect_category: str  # Specific category (e.g., "Solder Joint", "Scratch")
    severity: SeverityEnum  # critical, major, minor, cosmetic
    
    # Details
    description: str
    location: str  # Where on the product
    quantity_affected: int
    root_cause: Optional[str]
    
    # Responsibility
    reported_by_id: int  # FK to User
    responsible_party: ResponsiblePartyEnum  # internal, supplier, design, customer
    operator_id: Optional[int]  # FK to User (if operator error)
    supplier_id: Optional[int]  # FK to Supplier (if supplier defect)
    
    # Status
    status: DefectStatusEnum  # open, investigating, resolved, closed
    
    # Attachments
    photo_urls: JSON
    
    # Relationships
    manufacturing_order: Optional[ManufacturingOrder]
    mo_operation: Optional[ManufacturingOrderOperation]
    inspection_result: Optional[InspectionResult]
    component: Optional[Component]
    sales_order: Optional[SalesOrder]
    reported_by: User
    operator: Optional[User]
    supplier: Optional[Supplier]
    ncr: Optional[NonConformanceReport]
```

#### NonConformanceReport (NCR)
```python
class NonConformanceReport(Base, TimestampMixin):
    id: int
    ncr_number: str  # Auto-generated: NCR-YYYYMMDD-XXXX
    
    # Context
    defect_id: Optional[int]  # FK to Defect (can be created from defect)
    manufacturing_order_id: Optional[int]  # FK to ManufacturingOrder
    
    # Status
    status: NCRStatusEnum  # open, investigating, pending_approval, approved, closed
    priority: PriorityEnum  # urgent, high, normal, low
    
    # Investigation
    description: str
    root_cause: Optional[str]
    root_cause_category: Optional[str]  # 5M: Man, Machine, Material, Method, Measurement
    containment_actions: Optional[str]
    
    # Disposition
    disposition: DispositionEnum  # rework, scrap, use_as_is, return_to_supplier
    disposition_justification: Optional[str]
    quantity_affected: int
    
    # Cost Impact
    rework_cost: Optional[Decimal]
    scrap_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    
    # Ownership
    owner_id: int  # FK to User (Quality Engineer)
    created_by_id: int  # FK to User
    
    # Approval
    approver_id: Optional[int]  # FK to User
    approval_date: Optional[datetime]
    approval_notes: Optional[str]
    
    # Closure
    closed_by_id: Optional[int]  # FK to User
    closed_date: Optional[datetime]
    verification_notes: Optional[str]
    
    # Relationships
    defect: Optional[Defect]
    manufacturing_order: Optional[ManufacturingOrder]
    owner: User
    created_by: User
    approver: Optional[User]
    closed_by: Optional[User]
    capa: Optional[CorrectiveAction]
    rework_operations: List[ReworkOperation]
```

#### ReworkOperation
```python
class ReworkOperation(Base, TimestampMixin):
    id: int
    ncr_id: int  # FK to NonConformanceReport
    manufacturing_order_id: int  # FK to ManufacturingOrder
    work_center_id: int  # FK to WorkCenter
    
    # Scheduling
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    scheduled_duration_minutes: int
    
    # Execution
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    actual_duration_minutes: Optional[int]
    
    # Status
    status: OperationStatusEnum  # Reuse from ManufacturingOrderOperation
    
    # Assignment
    assigned_operator_id: Optional[int]  # FK to User
    
    # Details
    rework_description: str
    notes: Optional[str]
    
    # Cost
    labor_cost: Optional[Decimal]
    material_cost: Optional[Decimal]
    
    # Verification
    re_inspection_result_id: Optional[int]  # FK to InspectionResult
    
    # Relationships
    ncr: NonConformanceReport
    manufacturing_order: ManufacturingOrder
    work_center: WorkCenter
    assigned_operator: Optional[User]
    re_inspection_result: Optional[InspectionResult]
```

#### CorrectiveAction (CAPA)
```python
class CorrectiveAction(Base, TimestampMixin):
    id: int
    capa_number: str  # Auto-generated: CAPA-YYYYMMDD-XXXX
    
    # Context
    ncr_id: Optional[int]  # FK to NonConformanceReport
    defect_id: Optional[int]  # FK to Defect
    
    # Type
    action_type: ActionTypeEnum  # corrective, preventive
    
    # Status
    status: CAPAStatusEnum  # open, in_progress, verification, closed
    priority: PriorityEnum
    
    # Root Cause Analysis
    problem_statement: str
    root_cause: str
    root_cause_method: Optional[str]  # 5_whys, fishbone, other
    root_cause_analysis: Optional[JSON]  # Structured data for analysis
    
    # Actions
    corrective_actions: JSON  # List of actions with owner, due date, status
    preventive_actions: JSON  # List of actions
    
    # Ownership
    owner_id: int  # FK to User
    created_by_id: int  # FK to User
    
    # Verification
    effectiveness_verification: Optional[str]
    verification_date: Optional[datetime]
    verified_by_id: Optional[int]  # FK to User
    
    # Closure
    closed_date: Optional[datetime]
    closed_by_id: Optional[int]  # FK to User
    
    # Relationships
    ncr: Optional[NonConformanceReport]
    defect: Optional[Defect]
    owner: User
    created_by: User
    verified_by: Optional[User]
    closed_by: Optional[User]
```

#### QualityHold
```python
class QualityHold(Base, TimestampMixin):
    id: int
    hold_number: str  # Auto-generated: QH-YYYYMMDD-XXXX
    
    # Context
    ncr_id: int  # FK to NonConformanceReport
    hold_type: HoldTypeEnum  # inventory, manufacturing_order, sales_order
    
    # Target
    component_id: Optional[int]  # FK to Component (inventory hold)
    manufacturing_order_id: Optional[int]  # FK to ManufacturingOrder
    sales_order_id: Optional[int]  # FK to SalesOrder
    
    # Status
    status: HoldStatusEnum  # active, released, cancelled
    
    # Details
    reason: str
    quantity_held: int
    
    # Ownership
    placed_by_id: int  # FK to User
    placed_date: datetime
    
    # Release
    released_by_id: Optional[int]  # FK to User
    released_date: Optional[datetime]
    release_reason: Optional[str]
    
    # Relationships
    ncr: NonConformanceReport
    component: Optional[Component]
    manufacturing_order: Optional[ManufacturingOrder]
    sales_order: Optional[SalesOrder]
    placed_by: User
    released_by: Optional[User]
```

### Enums

```python
class InspectionTypeEnum(str, enum.Enum):
    IN_PROCESS = "in_process"
    FINAL = "final"
    RECEIVING = "receiving"
    FIRST_ARTICLE = "first_article"

class InspectionResultEnum(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"  # Pass with notes

class DefectTypeEnum(str, enum.Enum):
    MATERIAL = "material"
    WORKMANSHIP = "workmanship"
    DESIGN = "design"
    OTHER = "other"

class SeverityEnum(str, enum.Enum):
    CRITICAL = "critical"  # Safety/function impact
    MAJOR = "major"  # Significant impact
    MINOR = "minor"  # Minor impact
    COSMETIC = "cosmetic"  # Appearance only

class ResponsiblePartyEnum(str, enum.Enum):
    INTERNAL = "internal"
    SUPPLIER = "supplier"
    DESIGN = "design"
    CUSTOMER = "customer"

class DefectStatusEnum(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class NCRStatusEnum(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    CLOSED = "closed"

class DispositionEnum(str, enum.Enum):
    REWORK = "rework"
    SCRAP = "scrap"
    USE_AS_IS = "use_as_is"
    RETURN_TO_SUPPLIER = "return_to_supplier"

class ActionTypeEnum(str, enum.Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"

class CAPAStatusEnum(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    VERIFICATION = "verification"
    CLOSED = "closed"

class HoldTypeEnum(str, enum.Enum):
    INVENTORY = "inventory"
    MANUFACTURING_ORDER = "manufacturing_order"
    SALES_ORDER = "sales_order"

class HoldStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    RELEASED = "released"
    CANCELLED = "cancelled"
```

### Updated Entities

#### ManufacturingOrderOperation (additions)
```python
# Add fields
inspection_status: Optional[InspectionResultEnum]  # Latest inspection result
quality_hold: bool  # True if operation has quality hold

# Add relationship
inspection_results: List[InspectionResult]
defects: List[Defect]
```

#### ManufacturingOrder (additions)
```python
# Add fields
quality_status: Optional[str]  # pass, fail, pending_inspection
final_inspection_result_id: Optional[int]  # FK to InspectionResult

# Add relationships
inspection_results: List[InspectionResult]
defects: List[Defect]
ncrs: List[NonConformanceReport]
quality_holds: List[QualityHold]
```

## API Endpoints

### Inspection Management

```
POST   /api/quality/inspection-points
GET    /api/quality/inspection-points
GET    /api/quality/inspection-points/{id}
PUT    /api/quality/inspection-points/{id}
DELETE /api/quality/inspection-points/{id}

POST   /api/quality/inspections
GET    /api/quality/inspections
GET    /api/quality/inspections/{id}
PUT    /api/quality/inspections/{id}
GET    /api/quality/inspections/my-assignments
POST   /api/quality/inspections/{id}/upload-photo
```

### Defect Management

```
POST   /api/quality/defects
GET    /api/quality/defects
GET    /api/quality/defects/{id}
PUT    /api/quality/defects/{id}
GET    /api/quality/defects/search?type=&severity=&date_from=&date_to=
POST   /api/quality/defects/{id}/upload-photo
```

### NCR Management

```
POST   /api/quality/ncrs
GET    /api/quality/ncrs
GET    /api/quality/ncrs/{id}
PUT    /api/quality/ncrs/{id}
POST   /api/quality/ncrs/{id}/approve
POST   /api/quality/ncrs/{id}/close
GET    /api/quality/ncrs/overdue
```

### Rework Management

```
POST   /api/quality/rework-operations
GET    /api/quality/rework-operations
GET    /api/quality/rework-operations/{id}
PUT    /api/quality/rework-operations/{id}
POST   /api/quality/rework-operations/{id}/start
POST   /api/quality/rework-operations/{id}/complete
```

### CAPA Management

```
POST   /api/quality/capas
GET    /api/quality/capas
GET    /api/quality/capas/{id}
PUT    /api/quality/capas/{id}
POST   /api/quality/capas/{id}/verify
POST   /api/quality/capas/{id}/close
GET    /api/quality/capas/overdue
```

### Quality Holds

```
POST   /api/quality/holds
GET    /api/quality/holds
GET    /api/quality/holds/{id}
POST   /api/quality/holds/{id}/release
GET    /api/quality/holds/active
```

### Quality Analytics

```
GET    /api/quality/analytics/first-pass-yield?product_id=&start_date=&end_date=
GET    /api/quality/analytics/defect-rate?group_by=type|severity|operation
GET    /api/quality/analytics/cost-of-quality?start_date=&end_date=
GET    /api/quality/analytics/pareto?metric=defects|cost&limit=10
GET    /api/quality/analytics/operator-performance
GET    /api/quality/analytics/supplier-quality
GET    /api/quality/analytics/dashboard
```

## Business Logic

### Service: InspectionService

**Responsibilities:**
- Manage inspection points and checklists
- Record inspection results
- Link inspections to operations/MOs
- Calculate inspection completion rate

**Key Methods:**
```python
create_inspection_point(data: InspectionPointCreate) -> InspectionPoint
record_inspection(data: InspectionResultCreate) -> InspectionResult
get_my_inspections(inspector_id: int) -> List[InspectionResult]
get_pending_inspections(work_center_id: Optional[int]) -> List[Dict]
calculate_pass_rate(filters: Dict) -> float
```

### Service: DefectService

**Responsibilities:**
- Record and track defects
- Categorize and analyze defects
- Link defects to context (MO, operation, supplier)
- Generate defect reports

**Key Methods:**
```python
create_defect(data: DefectCreate) -> Defect
update_defect(defect_id: int, data: DefectUpdate) -> Defect
search_defects(filters: DefectFilters) -> List[Defect]
get_defect_trends(group_by: str, filters: Dict) -> List[Dict]
get_pareto_analysis(metric: str, limit: int) -> List[Dict]
```

### Service: NCRService

**Responsibilities:**
- Manage NCR lifecycle
- Approval workflow
- Cost tracking
- NCR aging and overdue tracking

**Key Methods:**
```python
create_ncr(data: NCRCreate) -> NonConformanceReport
update_ncr(ncr_id: int, data: NCRUpdate) -> NonConformanceReport
approve_ncr(ncr_id: int, approver_id: int, notes: str) -> NonConformanceReport
close_ncr(ncr_id: int, user_id: int, verification: str) -> NonConformanceReport
get_overdue_ncrs() -> List[NonConformanceReport]
calculate_ncr_metrics() -> Dict
```

### Service: ReworkService

**Responsibilities:**
- Create rework operations from NCRs
- Schedule and track rework
- Calculate rework costs
- Verify rework completion

**Key Methods:**
```python
create_rework_operation(ncr_id: int, data: ReworkCreate) -> ReworkOperation
start_rework(rework_id: int, operator_id: int) -> ReworkOperation
complete_rework(rework_id: int) -> ReworkOperation
calculate_rework_cost(rework_id: int) -> Decimal
```

### Service: CAPAService

**Responsibilities:**
- Manage CAPA lifecycle
- Track action items
- Verify effectiveness
- CAPA metrics

**Key Methods:**
```python
create_capa(data: CAPACreate) -> CorrectiveAction
update_capa(capa_id: int, data: CAPAUpdate) -> CorrectiveAction
add_action(capa_id: int, action: Dict) -> CorrectiveAction
update_action_status(capa_id: int, action_id: str, status: str) -> CorrectiveAction
verify_effectiveness(capa_id: int, user_id: int, notes: str) -> CorrectiveAction
close_capa(capa_id: int, user_id: int) -> CorrectiveAction
get_overdue_actions() -> List[Dict]
```

### Service: QualityHoldService

**Responsibilities:**
- Place and manage quality holds
- Block affected items
- Release holds after approval
- Track hold duration

**Key Methods:**
```python
place_hold(data: QualityHoldCreate) -> QualityHold
release_hold(hold_id: int, user_id: int, reason: str) -> QualityHold
get_active_holds(hold_type: Optional[HoldTypeEnum]) -> List[QualityHold]
check_hold_status(entity_type: str, entity_id: int) -> Optional[QualityHold]
```

### Service: QualityAnalyticsService

**Responsibilities:**
- Calculate quality metrics
- Generate quality reports
- Trend analysis
- Pareto analysis

**Key Methods:**
```python
calculate_first_pass_yield(filters: Dict) -> Dict
calculate_defect_rate(filters: Dict) -> Dict
calculate_cost_of_quality(start_date: date, end_date: date) -> Dict
get_pareto_analysis(metric: str, limit: int) -> List[Dict]
get_operator_quality_performance() -> List[Dict]
get_supplier_quality_performance() -> List[Dict]
get_quality_dashboard() -> Dict
```

## UI Components

### 1. Inspection Management Page
- List of inspection points
- Create/edit inspection point form
- Inspection checklist builder

### 2. Inspector Dashboard
- My assigned inspections
- Pending inspections
- Inspection history
- Quick inspection entry

### 3. Inspection Entry Form (Mobile-Optimized)
- Checklist with pass/fail/conditional
- Measurement entry
- Photo capture
- Notes
- Submit inspection

### 4. Defect Entry Form
- Defect type and severity
- Location and description
- Photo capture
- Link to MO/operation
- Responsible party

### 5. Defect List & Search
- Filter by type, severity, date, product
- Defect details view
- Create NCR from defect

### 6. NCR Management Page
- NCR list with status
- Create NCR form
- NCR detail view
- Approval workflow
- Disposition selection

### 7. Rework Queue
- List of rework operations
- Similar to shop floor queue
- Start/complete rework
- Re-inspection link

### 8. CAPA Management Page
- CAPA list
- Create CAPA form
- Root cause analysis tools
- Action item tracking
- Effectiveness verification

### 9. Quality Dashboard
- Key metrics cards (FPY, defect rate, NCRs, CAPAs)
- Quality trends charts
- Pareto chart (top defects)
- Alerts (overdue NCRs, CAPAs)

### 10. Quality Analytics Page
- First Pass Yield trends
- Defect analysis
- Cost of Quality
- Operator performance
- Supplier quality

### 11. Quality Holds Page
- Active holds list
- Hold details
- Release hold form

## Database Migrations

### Migration 1: Create inspection tables
### Migration 2: Create defect tables
### Migration 3: Create NCR and rework tables
### Migration 4: Create CAPA tables
### Migration 5: Create quality hold tables
### Migration 6: Add quality fields to existing tables
### Migration 7: Create indexes for performance

## Integration Points

### With Manufacturing Module
- Inspection points in operation routes
- Inspection results block operation completion
- Quality holds block MO progress
- Rework operations in shop floor queue

### With Shop Floor Module
- Operators record defects during operations
- Quality holds prevent operation start
- Rework operations tracked like regular operations

### With Inventory Module
- Receiving inspection for incoming materials
- Quarantine stock (quality hold)
- Scrap transactions
- Supplier quality data

### With Sales Module
- Final inspection before delivery
- Quality holds block shipment
- Customer return/complaint tracking

### With Notifications Module
- Inspection failure alerts
- NCR assignment notifications
- CAPA action due reminders
- Quality threshold alerts

## Security & Permissions

### Roles
- **Quality Inspector**: Perform inspections, record defects
- **Quality Engineer**: Manage NCRs, CAPAs, analyze data
- **Quality Manager**: Full access, approve NCRs, view all analytics
- **Production Operator**: Record defects, view inspection results
- **Production Manager**: View quality data, approve dispositions

### Permissions
```
inspection.create
inspection.read
inspection.update
inspection.perform

defect.create
defect.read
defect.update

ncr.create
ncr.read
ncr.update
ncr.approve
ncr.close

capa.create
capa.read
capa.update
capa.verify
capa.close

quality_hold.create
quality_hold.read
quality_hold.release

quality_analytics.read
```

## Performance Considerations

### Indexing
```sql
CREATE INDEX idx_inspection_results_mo_operation ON inspection_results(mo_operation_id);
CREATE INDEX idx_inspection_results_inspector ON inspection_results(inspector_id);
CREATE INDEX idx_inspection_results_date ON inspection_results(inspection_date);
CREATE INDEX idx_defects_mo ON defects(manufacturing_order_id);
CREATE INDEX idx_defects_type_severity ON defects(defect_type, severity);
CREATE INDEX idx_defects_date ON defects(created_at);
CREATE INDEX idx_ncrs_status ON non_conformance_reports(status);
CREATE INDEX idx_ncrs_priority ON non_conformance_reports(priority);
CREATE INDEX idx_capas_status ON corrective_actions(status);
```

### Caching
- Cache quality dashboard data (5-minute TTL)
- Cache quality metrics (15-minute TTL)
- Cache inspection checklists

### Optimization
- Paginate defect and NCR lists
- Lazy load photos (thumbnails first)
- Aggregate queries for analytics
- Database views for complex metrics

## Testing Strategy

### Unit Tests
- InspectionService: test inspection recording
- DefectService: test defect categorization
- NCRService: test approval workflow
- QualityAnalyticsService: test FPY calculation

### Integration Tests
- End-to-end: Inspection → Defect → NCR → Rework → Close
- Test quality holds blocking operations
- Test cost of quality calculations

### Performance Tests
- Load with 10,000 inspections
- Defect search performance
- Analytics query performance

## Rollout Plan

### Phase 1: Inspection Management (Weeks 1-2)
- Create inspection point models
- Inspection recording
- Basic inspection dashboard

### Phase 2: Defect Tracking (Weeks 3-4)
- Defect recording
- Defect categorization
- Defect analytics (Pareto)

### Phase 3: NCR & Rework (Weeks 5-6)
- NCR workflow
- Quality holds
- Rework operations
- Cost tracking

### Phase 4: CAPA (Week 7)
- CAPA workflow
- Action tracking
- Effectiveness verification

### Phase 5: Analytics & Reporting (Week 8)
- First Pass Yield
- Cost of Quality
- Quality dashboard
- Reports

## Correctness Properties

### P1: Inspection Integrity
**Property**: Required inspections must pass before operation completion
**Verification**: Operation cannot complete if required inspection failed
**Test**: Attempt to complete operation with failed inspection → should block

### P2: Quality Hold Enforcement
**Property**: Quality holds must prevent affected items from progressing
**Verification**: Held MO/inventory cannot be used/shipped
**Test**: Place hold on MO → attempt to start next operation → should block

### P3: NCR Approval Workflow
**Property**: NCR disposition requires approval before execution
**Verification**: Rework/scrap cannot proceed without approved NCR
**Test**: Create NCR → attempt rework without approval → should block

### P4: Cost Accuracy
**Property**: Cost of Quality must accurately sum all quality costs
**Verification**: COQ = rework costs + scrap costs + inspection labor
**Test**: Calculate COQ → verify against individual cost records

### P5: CAPA Traceability
**Property**: CAPAs must be linked to root causes (NCRs/defects)
**Verification**: Every CAPA has source NCR or defect
**Test**: Create CAPA → verify link exists

### P6: Defect Categorization Consistency
**Property**: Defects must have valid type, severity, and responsible party
**Verification**: Required fields enforced, valid enum values
**Test**: Create defect with invalid data → should fail validation

### P7: Audit Trail Completeness
**Property**: All quality records must have complete audit trail
**Verification**: Created by, created at, updated by, updated at tracked
**Test**: Create/update quality record → verify audit fields populated

### P8: First Pass Yield Accuracy
**Property**: FPY = (units passing first time) / (total units) * 100
**Verification**: FPY calculation matches manual calculation
**Test**: Create test data → calculate FPY → verify accuracy
