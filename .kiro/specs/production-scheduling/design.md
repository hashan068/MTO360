# Production Scheduling & Shop Floor Management - Design

## Architecture Overview

This feature extends the existing Manufacturing module with new entities and services for production scheduling and shop floor execution.

## Data Model

### New Entities

#### WorkCenter
```python
class WorkCenter(Base, TimestampMixin):
    id: int
    name: str  # e.g., "Assembly Station 1"
    code: str  # unique identifier, e.g., "ASM-01"
    description: Optional[str]
    capacity_hours_per_day: Decimal  # e.g., 8.0, 16.0 for two shifts
    is_active: bool
    location: Optional[str]
    notes: Optional[str]
    
    # Relationships
    operations: List[Operation]
    work_center_schedules: List[WorkCenterSchedule]
```

#### OperationRoute
```python
class OperationRoute(Base, TimestampMixin):
    id: int
    name: str  # e.g., "Standard Inverter Assembly"
    product_id: Optional[int]  # FK to Product
    bom_id: Optional[int]  # FK to BillOfMaterial
    is_active: bool
    
    # Relationships
    product: Product
    bom: BillOfMaterial
    route_operations: List[RouteOperation]
```

#### RouteOperation
```python
class RouteOperation(Base):
    id: int
    route_id: int  # FK to OperationRoute
    sequence: int  # 1, 2, 3...
    name: str  # e.g., "PCB Assembly"
    description: Optional[str]
    work_center_id: int  # FK to WorkCenter
    standard_time_minutes: int  # estimated duration
    setup_time_minutes: int  # optional setup time
    
    # Relationships
    route: OperationRoute
    work_center: WorkCenter
```

#### ManufacturingOrderOperation
```python
class ManufacturingOrderOperation(Base, TimestampMixin):
    id: int
    manufacturing_order_id: int  # FK to ManufacturingOrder
    route_operation_id: Optional[int]  # FK to RouteOperation (template)
    sequence: int
    name: str
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
    status: OperationStatusEnum  # pending, scheduled, in_progress, completed, blocked, cancelled
    
    # Assignment
    assigned_operator_id: Optional[int]  # FK to User
    
    # Notes
    notes: Optional[str]
    blocking_reason: Optional[str]  # if status is blocked
    
    # Relationships
    manufacturing_order: ManufacturingOrder
    work_center: WorkCenter
    assigned_operator: Optional[User]
    route_operation: Optional[RouteOperation]
```

#### WorkCenterSchedule
```python
class WorkCenterSchedule(Base):
    """Track capacity allocation per work center per day"""
    id: int
    work_center_id: int
    date: date
    available_capacity_minutes: int  # e.g., 480 for 8 hours
    scheduled_capacity_minutes: int  # sum of scheduled operations
    utilization_percentage: Decimal  # calculated field
    
    # Relationships
    work_center: WorkCenter
```

### Enums

```python
class OperationStatusEnum(str, enum.Enum):
    PENDING = "pending"  # not yet scheduled
    SCHEDULED = "scheduled"  # scheduled but not started
    IN_PROGRESS = "in_progress"  # currently being worked on
    COMPLETED = "completed"  # finished
    BLOCKED = "blocked"  # cannot proceed due to issue
    CANCELLED = "cancelled"  # cancelled
```

### Updated Entities

#### ManufacturingOrder (additions)
```python
# Add new fields
scheduled_start: Optional[datetime]  # earliest operation start
scheduled_end: Optional[datetime]  # latest operation end
total_scheduled_duration_minutes: Optional[int]

# Add relationship
operations: List[ManufacturingOrderOperation]
```

#### Product (additions)
```python
# Add relationship
operation_routes: List[OperationRoute]
```

## API Endpoints

### Work Centers

```
POST   /api/manufacturing/work-centers
GET    /api/manufacturing/work-centers
GET    /api/manufacturing/work-centers/{id}
PUT    /api/manufacturing/work-centers/{id}
DELETE /api/manufacturing/work-centers/{id}
GET    /api/manufacturing/work-centers/{id}/utilization?start_date=&end_date=
GET    /api/manufacturing/work-centers/{id}/operations?status=
```

### Operation Routes

```
POST   /api/manufacturing/operation-routes
GET    /api/manufacturing/operation-routes
GET    /api/manufacturing/operation-routes/{id}
PUT    /api/manufacturing/operation-routes/{id}
DELETE /api/manufacturing/operation-routes/{id}
POST   /api/manufacturing/operation-routes/{id}/copy
```

### Route Operations

```
POST   /api/manufacturing/operation-routes/{route_id}/operations
PUT    /api/manufacturing/operation-routes/{route_id}/operations/{id}
DELETE /api/manufacturing/operation-routes/{route_id}/operations/{id}
PUT    /api/manufacturing/operation-routes/{route_id}/operations/reorder
```

### Manufacturing Order Operations

```
GET    /api/manufacturing/manufacturing-orders/{mo_id}/operations
POST   /api/manufacturing/manufacturing-orders/{mo_id}/operations/generate
PUT    /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}
POST   /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/start
POST   /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/complete
POST   /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/pause
POST   /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/block
POST   /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/reschedule
```

### Scheduling

```
GET    /api/manufacturing/schedule?start_date=&end_date=&work_center_id=
POST   /api/manufacturing/schedule/auto-schedule
POST   /api/manufacturing/schedule/reschedule
GET    /api/manufacturing/schedule/capacity?start_date=&end_date=
GET    /api/manufacturing/schedule/conflicts
```

### Shop Floor

```
GET    /api/manufacturing/shop-floor/dashboard
GET    /api/manufacturing/shop-floor/work-centers/{id}/queue
GET    /api/manufacturing/shop-floor/operations/active
GET    /api/manufacturing/shop-floor/operations/my-assignments
```

### Analytics

```
GET    /api/manufacturing/analytics/capacity-utilization
GET    /api/manufacturing/analytics/bottlenecks
GET    /api/manufacturing/analytics/operation-performance
GET    /api/manufacturing/analytics/cycle-times
```

## Business Logic

### Service: OperationRouteService

**Responsibilities:**
- Create and manage operation routes
- Copy routes from existing products
- Validate route operations (sequence, work centers)

**Key Methods:**
```python
create_route(data: OperationRouteCreate) -> OperationRoute
add_operation(route_id: int, data: RouteOperationCreate) -> RouteOperation
reorder_operations(route_id: int, sequence_map: dict) -> None
copy_route(source_route_id: int, target_product_id: int) -> OperationRoute
```

### Service: SchedulingService

**Responsibilities:**
- Generate operations from routes when MO is created
- Schedule operations based on capacity
- Reschedule operations
- Calculate capacity utilization
- Identify conflicts and bottlenecks

**Key Methods:**
```python
generate_operations_for_mo(mo_id: int) -> List[ManufacturingOrderOperation]
schedule_operation(operation_id: int, start_time: datetime) -> None
auto_schedule_mo(mo_id: int) -> None
calculate_capacity(work_center_id: int, date: date) -> WorkCenterSchedule
get_available_slot(work_center_id: int, duration_minutes: int, after: datetime) -> datetime
identify_bottlenecks(start_date: date, end_date: date) -> List[dict]
```

**Scheduling Algorithm (Simple Forward Scheduling):**
1. Get all operations for MO sorted by sequence
2. For each operation:
   - Find earliest available slot in assigned work center
   - Consider: previous operation completion, material availability, work center capacity
   - Schedule operation in that slot
   - Update work center capacity
3. Update MO scheduled start/end times

### Service: ShopFloorService

**Responsibilities:**
- Start/complete operations
- Track actual times
- Update MO status based on operations
- Manage operation queue per work center

**Key Methods:**
```python
start_operation(operation_id: int, operator_id: int) -> ManufacturingOrderOperation
complete_operation(operation_id: int) -> ManufacturingOrderOperation
pause_operation(operation_id: int, reason: str) -> ManufacturingOrderOperation
block_operation(operation_id: int, reason: str) -> ManufacturingOrderOperation
get_work_center_queue(work_center_id: int) -> List[ManufacturingOrderOperation]
get_dashboard_data() -> dict
```

**Status Update Logic:**
```python
def update_mo_status_from_operations(mo_id: int):
    operations = get_operations(mo_id)
    
    if all(op.status == "completed" for op in operations):
        mo.status = "completed"
    elif any(op.status == "in_progress" for op in operations):
        mo.status = "in_production"
    elif any(op.status == "blocked" for op in operations):
        mo.status = "blocked"  # new status
    elif all(op.status in ["pending", "scheduled"] for op in operations):
        mo.status = "pending"
```

### Service: CapacityAnalyticsService

**Responsibilities:**
- Calculate utilization metrics
- Generate capacity reports
- Identify bottlenecks
- Track performance metrics

**Key Methods:**
```python
get_utilization_report(start_date: date, end_date: date) -> dict
get_bottleneck_analysis() -> List[dict]
get_operation_performance(work_center_id: Optional[int]) -> dict
get_cycle_time_analysis(product_id: Optional[int]) -> dict
```

## UI Components

### 1. Work Center Management Page
- List of work centers with capacity and utilization
- Create/edit work center form
- View work center details and assigned operations

### 2. Operation Route Builder
- Product selector
- Operation list with drag-to-reorder
- Add/edit operation form with work center selector
- Copy route functionality

### 3. Production Scheduler (Gantt-style)
- Rows: Work centers
- Columns: Time periods (day/week view)
- Blocks: Operations (color-coded by status)
- Drag-and-drop to reschedule
- Capacity utilization bars
- Filters: date range, work center, MO status

### 4. Shop Floor Dashboard
- Current operations in progress (by work center)
- Pending operations queue
- Completed operations today
- Work center status indicators
- Real-time updates

### 5. Operation Execution Interface
- List of assigned operations
- Start/Complete buttons
- Timer showing elapsed time
- Notes/comments field
- Block/pause functionality

### 6. Capacity Analytics Dashboard
- Utilization charts (by work center, over time)
- Bottleneck identification
- Actual vs estimated time comparison
- Cycle time trends

## Database Migrations

### Migration 1: Create work_centers table
### Migration 2: Create operation_routes table
### Migration 3: Create route_operations table
### Migration 4: Create manufacturing_order_operations table
### Migration 5: Create work_center_schedules table
### Migration 6: Add scheduling fields to manufacturing_orders
### Migration 7: Add blocked status to ManufacturingOrderStatusEnum

## Integration Points

### With Manufacturing Module
- When MO is created and MR approved → generate operations
- When all operations completed → update MO status to completed
- MO delivery date calculation considers scheduled end time

### With Inventory Module
- Check material availability before scheduling
- Material requisition approval triggers auto-scheduling

### With Sales Module
- Sales order delivery date suggestions based on production schedule
- Update sales order status when production starts/completes

### With Notifications Module
- Notify when operation is assigned
- Alert when operation is blocked
- Notify supervisor when work center is overallocated

## Security & Permissions

### Roles
- **Production Planner**: Full access to scheduling, work centers, routes
- **Shop Floor Supervisor**: View schedule, manage operations, assign operators
- **Production Operator**: View assigned operations, start/complete operations
- **Production Manager**: View all, analytics access

### Permissions
```
work_center.create
work_center.read
work_center.update
work_center.delete

operation_route.create
operation_route.read
operation_route.update
operation_route.delete

schedule.read
schedule.update
schedule.auto_schedule

operation.start
operation.complete
operation.block
operation.assign

analytics.read
```

## Performance Considerations

### Indexing
```sql
CREATE INDEX idx_mo_operations_mo_id ON manufacturing_order_operations(manufacturing_order_id);
CREATE INDEX idx_mo_operations_work_center ON manufacturing_order_operations(work_center_id);
CREATE INDEX idx_mo_operations_status ON manufacturing_order_operations(status);
CREATE INDEX idx_mo_operations_scheduled_start ON manufacturing_order_operations(scheduled_start);
CREATE INDEX idx_work_center_schedule_date ON work_center_schedules(work_center_id, date);
```

### Caching
- Cache work center capacity calculations
- Cache dashboard data (refresh every 30 seconds)
- Cache utilization reports

### Optimization
- Batch operation generation for multiple MOs
- Lazy load operation details in scheduler
- Paginate operation lists
- Use database views for complex analytics queries

## Testing Strategy

### Unit Tests
- SchedulingService: test scheduling algorithms
- ShopFloorService: test status transitions
- CapacityAnalyticsService: test calculations

### Integration Tests
- End-to-end: Create MO → Generate operations → Schedule → Execute → Complete
- Test capacity constraint validation
- Test concurrent operation updates

### Performance Tests
- Load scheduler with 500 operations
- Test drag-and-drop responsiveness
- Test dashboard refresh with 50 active operations

## Rollout Plan

### Phase 1: Foundation (Week 1-2)
- Create data models and migrations
- Implement work center CRUD
- Implement operation route CRUD

### Phase 2: Scheduling (Week 3-4)
- Implement operation generation
- Implement basic scheduling service
- Build scheduler UI (read-only)

### Phase 3: Shop Floor (Week 5-6)
- Implement operation execution
- Build shop floor dashboard
- Build operation execution interface

### Phase 4: Advanced Scheduling (Week 7-8)
- Implement drag-and-drop rescheduling
- Implement auto-scheduling
- Add capacity validation

### Phase 5: Analytics (Week 9-10)
- Implement capacity analytics
- Build analytics dashboards
- Add bottleneck identification

### Phase 6: Polish & Integration (Week 11-12)
- Integration with sales module (delivery dates)
- Notifications
- Performance optimization
- User acceptance testing

## Open Questions

1. Should we support parallel operations (multiple operations at same sequence)?
2. How to handle work center downtime/maintenance?
3. Should operators clock in/out of work centers?
4. Do we need shift management (day/night shifts)?
5. Should we track scrap/rework at operation level?
6. How to handle rush orders (priority scheduling)?
7. Should we support operation splitting (partial completion)?

## Correctness Properties

### P1: Operation Sequence Integrity
**Property**: Operations must be executed in sequence order
**Verification**: Operation N cannot start until operation N-1 is completed
**Test**: Attempt to start operation 2 before operation 1 completes → should fail

### P2: Capacity Constraint
**Property**: Scheduled capacity cannot exceed available capacity
**Verification**: Sum of scheduled operation durations ≤ work center capacity for any day
**Test**: Schedule operations exceeding capacity → should warn or prevent

### P3: Operation Status Consistency
**Property**: MO status must reflect operation statuses
**Verification**: 
- All operations completed → MO completed
- Any operation in_progress → MO in_production
**Test**: Complete all operations → MO status should update to completed

### P4: Time Tracking Accuracy
**Property**: Actual duration = actual_end - actual_start
**Verification**: When operation completes, calculate and store actual duration
**Test**: Start operation at T1, complete at T2 → actual_duration = T2 - T1

### P5: Schedule Conflict Prevention
**Property**: A work center cannot have overlapping operations
**Verification**: No two operations scheduled at same work center with overlapping time ranges
**Test**: Schedule two operations at same work center, same time → should conflict

### P6: Material Availability Prerequisite
**Property**: Operations cannot be scheduled until materials are available
**Verification**: MO operations only generated after MR approved
**Test**: Try to schedule MO with pending MR → should block

### P7: Work Center Assignment Validity
**Property**: Operations must be assigned to active work centers
**Verification**: Cannot assign operation to inactive work center
**Test**: Assign operation to inactive work center → should fail

### P8: Audit Trail Completeness
**Property**: All operation status changes must be logged
**Verification**: Every status transition creates audit record with timestamp and user
**Test**: Change operation status → verify audit log entry exists
