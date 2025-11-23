# Production Scheduling & Shop Floor Management - Implementation Tasks

## Phase 1: Foundation (Week 1-2)

### Task 1.1: Database Models
**Acceptance Criteria**: AC1, AC2
**Properties**: P7
**Estimated Time**: 8 hours

- [ ] Create WorkCenter model with fields and relationships
- [ ] Create OperationRoute model
- [ ] Create RouteOperation model
- [ ] Create ManufacturingOrderOperation model
- [ ] Create WorkCenterSchedule model
- [ ] Add OperationStatusEnum
- [ ] Update ManufacturingOrder model with scheduling fields
- [ ] Create Alembic migrations for all new tables
- [ ] Add database indexes for performance

**Files to Create/Modify**:
- `backend/app/models/manufacturing.py` (update)
- `backend/alembic/versions/xxx_add_production_scheduling.py` (new)

### Task 1.2: Schemas
**Acceptance Criteria**: AC1, AC2
**Estimated Time**: 4 hours

- [ ] Create WorkCenterCreate, WorkCenterUpdate, WorkCenterResponse schemas
- [ ] Create OperationRouteCreate, OperationRouteUpdate, OperationRouteResponse schemas
- [ ] Create RouteOperationCreate, RouteOperationUpdate, RouteOperationResponse schemas
- [ ] Create ManufacturingOrderOperationCreate, ManufacturingOrderOperationUpdate, ManufacturingOrderOperationResponse schemas
- [ ] Create WorkCenterScheduleResponse schema
- [ ] Add nested schemas for relationships

**Files to Create/Modify**:
- `backend/app/schemas/manufacturing.py` (update)

### Task 1.3: Repository Interfaces
**Acceptance Criteria**: AC1, AC2
**Estimated Time**: 2 hours

- [ ] Define IWorkCenterRepository protocol
- [ ] Define IOperationRouteRepository protocol
- [ ] Define IRouteOperationRepository protocol
- [ ] Define IManufacturingOrderOperationRepository protocol
- [ ] Define IWorkCenterScheduleRepository protocol

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/domain/interfaces.py` (update)

### Task 1.4: Repository Implementations
**Acceptance Criteria**: AC1, AC2
**Estimated Time**: 6 hours

- [ ] Implement WorkCenterRepository with CRUD operations
- [ ] Implement OperationRouteRepository with CRUD operations
- [ ] Implement RouteOperationRepository with CRUD operations
- [ ] Implement ManufacturingOrderOperationRepository with CRUD operations
- [ ] Implement WorkCenterScheduleRepository with CRUD operations
- [ ] Add query methods for filtering and searching

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/infra/repositories/work_center_repository.py` (new)
- `backend/app/modules/manufacturing/infra/repositories/operation_route_repository.py` (new)
- `backend/app/modules/manufacturing/infra/repositories/mo_operation_repository.py` (new)
- `backend/app/modules/manufacturing/infra/repositories/__init__.py` (update)

### Task 1.5: Work Center Service
**Acceptance Criteria**: AC1
**Properties**: P7
**Estimated Time**: 4 hours

- [ ] Create WorkCenterService
- [ ] Implement create_work_center()
- [ ] Implement get_work_center()
- [ ] Implement list_work_centers()
- [ ] Implement update_work_center()
- [ ] Implement delete_work_center() (soft delete)
- [ ] Add validation for work center data

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/work_center_service.py` (new)
- `backend/app/modules/manufacturing/application/services/__init__.py` (update)

### Task 1.6: Operation Route Service
**Acceptance Criteria**: AC2
**Estimated Time**: 6 hours

- [ ] Create OperationRouteService
- [ ] Implement create_route()
- [ ] Implement add_operation_to_route()
- [ ] Implement update_route_operation()
- [ ] Implement delete_route_operation()
- [ ] Implement reorder_operations()
- [ ] Implement copy_route()
- [ ] Add validation for sequence integrity

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/operation_route_service.py` (new)
- `backend/app/modules/manufacturing/application/services/__init__.py` (update)

### Task 1.7: Work Center API Endpoints
**Acceptance Criteria**: AC1
**Estimated Time**: 4 hours

- [ ] POST /api/manufacturing/work-centers
- [ ] GET /api/manufacturing/work-centers
- [ ] GET /api/manufacturing/work-centers/{id}
- [ ] PUT /api/manufacturing/work-centers/{id}
- [ ] DELETE /api/manufacturing/work-centers/{id}
- [ ] Add request validation
- [ ] Add error handling
- [ ] Add API documentation

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/work_centers.py` (new)
- `backend/app/modules/manufacturing/api/router.py` (update)

### Task 1.8: Operation Route API Endpoints
**Acceptance Criteria**: AC2
**Estimated Time**: 4 hours

- [ ] POST /api/manufacturing/operation-routes
- [ ] GET /api/manufacturing/operation-routes
- [ ] GET /api/manufacturing/operation-routes/{id}
- [ ] PUT /api/manufacturing/operation-routes/{id}
- [ ] DELETE /api/manufacturing/operation-routes/{id}
- [ ] POST /api/manufacturing/operation-routes/{id}/copy
- [ ] POST /api/manufacturing/operation-routes/{route_id}/operations
- [ ] PUT /api/manufacturing/operation-routes/{route_id}/operations/{id}
- [ ] DELETE /api/manufacturing/operation-routes/{route_id}/operations/{id}
- [ ] PUT /api/manufacturing/operation-routes/{route_id}/operations/reorder

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/operation_routes.py` (new)
- `backend/app/modules/manufacturing/api/router.py` (update)

### Task 1.9: Frontend - Work Center Management
**Acceptance Criteria**: AC1
**Estimated Time**: 8 hours

- [ ] Create WorkCenterList component
- [ ] Create WorkCenterForm component (create/edit)
- [ ] Create WorkCenterDetail component
- [ ] Add work center API client functions
- [ ] Add work center state management (Zustand)
- [ ] Add routing for work center pages
- [ ] Add form validation
- [ ] Add loading and error states

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/WorkCenterList.tsx` (new)
- `client/src/features/manufacturing/components/WorkCenterForm.tsx` (new)
- `client/src/features/manufacturing/components/WorkCenterDetail.tsx` (new)
- `client/src/features/manufacturing/api/workCenters.ts` (new)
- `client/src/features/manufacturing/state/workCenterStore.ts` (new)

### Task 1.10: Frontend - Operation Route Builder
**Acceptance Criteria**: AC2
**Estimated Time**: 10 hours

- [ ] Create OperationRouteList component
- [ ] Create OperationRouteForm component
- [ ] Create RouteOperationList component with drag-to-reorder
- [ ] Create RouteOperationForm component
- [ ] Add operation route API client functions
- [ ] Add operation route state management
- [ ] Implement copy route functionality
- [ ] Add routing for operation route pages

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/OperationRouteList.tsx` (new)
- `client/src/features/manufacturing/components/OperationRouteForm.tsx` (new)
- `client/src/features/manufacturing/components/RouteOperationList.tsx` (new)
- `client/src/features/manufacturing/components/RouteOperationForm.tsx` (new)
- `client/src/features/manufacturing/api/operationRoutes.ts` (new)
- `client/src/features/manufacturing/state/operationRouteStore.ts` (new)

## Phase 2: Scheduling (Week 3-4)

### Task 2.1: Operation Generation Service
**Acceptance Criteria**: AC3
**Properties**: P1, P6
**Estimated Time**: 6 hours

- [ ] Create SchedulingService
- [ ] Implement generate_operations_for_mo()
- [ ] Auto-generate operations when MO is created
- [ ] Copy standard times from route operations
- [ ] Set initial status to pending
- [ ] Validate route exists for product
- [ ] Handle MOs without routes (manual operation entry)

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/scheduling_service.py` (new)
- `backend/app/modules/manufacturing/application/services/manufacturing_order_service.py` (update)

### Task 2.2: Basic Scheduling Algorithm
**Acceptance Criteria**: AC4, AC5
**Properties**: P2, P5
**Estimated Time**: 10 hours

- [ ] Implement calculate_work_center_capacity()
- [ ] Implement find_available_slot()
- [ ] Implement schedule_operation()
- [ ] Implement auto_schedule_mo() (forward scheduling)
- [ ] Consider operation sequence constraints
- [ ] Consider work center capacity
- [ ] Update WorkCenterSchedule records
- [ ] Calculate and store MO scheduled start/end times

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/scheduling_service.py` (update)

### Task 2.3: Scheduling API Endpoints
**Acceptance Criteria**: AC3, AC4, AC5
**Estimated Time**: 4 hours

- [ ] GET /api/manufacturing/manufacturing-orders/{mo_id}/operations
- [ ] POST /api/manufacturing/manufacturing-orders/{mo_id}/operations/generate
- [ ] POST /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/reschedule
- [ ] GET /api/manufacturing/schedule
- [ ] POST /api/manufacturing/schedule/auto-schedule
- [ ] GET /api/manufacturing/schedule/capacity

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/manufacturing_orders.py` (update)
- `backend/app/modules/manufacturing/api/scheduling.py` (new)
- `backend/app/modules/manufacturing/api/router.py` (update)

### Task 2.4: Frontend - Scheduler Data Layer
**Acceptance Criteria**: AC4
**Estimated Time**: 4 hours

- [ ] Create scheduling API client functions
- [ ] Create scheduler state management
- [ ] Implement data fetching for schedule view
- [ ] Implement data transformation for Gantt display
- [ ] Add real-time updates (polling or WebSocket)

**Files to Create/Modify**:
- `client/src/features/manufacturing/api/scheduling.ts` (new)
- `client/src/features/manufacturing/state/schedulerStore.ts` (new)

### Task 2.5: Frontend - Scheduler UI (Read-Only)
**Acceptance Criteria**: AC4
**Estimated Time**: 12 hours

- [ ] Create SchedulerView component
- [ ] Create GanttChart component
- [ ] Create TimelineHeader component (day/week view)
- [ ] Create WorkCenterRow component
- [ ] Create OperationBlock component
- [ ] Implement color coding by status
- [ ] Add tooltips showing operation details
- [ ] Add date range selector
- [ ] Add work center filter
- [ ] Implement horizontal scrolling for timeline
- [ ] Add zoom controls (day/week view)

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/SchedulerView.tsx` (new)
- `client/src/features/manufacturing/components/GanttChart.tsx` (new)
- `client/src/features/manufacturing/components/TimelineHeader.tsx` (new)
- `client/src/features/manufacturing/components/WorkCenterRow.tsx` (new)
- `client/src/features/manufacturing/components/OperationBlock.tsx` (new)

### Task 2.6: Frontend - Capacity View
**Acceptance Criteria**: AC5
**Estimated Time**: 6 hours

- [ ] Create CapacityView component
- [ ] Display available vs scheduled capacity per work center
- [ ] Show utilization percentage
- [ ] Highlight overallocated periods (>100%)
- [ ] Add capacity chart (bar chart)
- [ ] Add date range selector

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/CapacityView.tsx` (new)
- `client/src/features/manufacturing/components/CapacityChart.tsx` (new)

## Phase 3: Shop Floor Execution (Week 5-6)

### Task 3.1: Shop Floor Service
**Acceptance Criteria**: AC6
**Properties**: P3, P4, P8
**Estimated Time**: 8 hours

- [ ] Create ShopFloorService
- [ ] Implement start_operation()
- [ ] Implement complete_operation()
- [ ] Implement pause_operation()
- [ ] Implement block_operation()
- [ ] Implement update_mo_status_from_operations()
- [ ] Add validation for status transitions
- [ ] Calculate actual duration on completion
- [ ] Create audit log entries for status changes

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/shop_floor_service.py` (new)
- `backend/app/modules/manufacturing/application/services/__init__.py` (update)

### Task 3.2: Shop Floor API Endpoints
**Acceptance Criteria**: AC6
**Estimated Time**: 4 hours

- [ ] POST /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/start
- [ ] POST /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/complete
- [ ] POST /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/pause
- [ ] POST /api/manufacturing/manufacturing-orders/{mo_id}/operations/{id}/block
- [ ] GET /api/manufacturing/shop-floor/work-centers/{id}/queue
- [ ] GET /api/manufacturing/shop-floor/operations/my-assignments

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/shop_floor.py` (new)
- `backend/app/modules/manufacturing/api/router.py` (update)

### Task 3.3: Dashboard Data Service
**Acceptance Criteria**: AC7
**Estimated Time**: 4 hours

- [ ] Implement get_dashboard_data()
- [ ] Get operations in progress by work center
- [ ] Get pending operations queue
- [ ] Get completed operations today
- [ ] Get work center status (idle/busy/blocked)
- [ ] Calculate real-time WIP count
- [ ] Optimize queries for performance

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/shop_floor_service.py` (update)

### Task 3.4: Dashboard API Endpoint
**Acceptance Criteria**: AC7
**Estimated Time**: 2 hours

- [ ] GET /api/manufacturing/shop-floor/dashboard
- [ ] Add caching (30 second TTL)
- [ ] Add real-time update support

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/shop_floor.py` (update)

### Task 3.5: Frontend - Shop Floor Dashboard
**Acceptance Criteria**: AC7
**Estimated Time**: 10 hours

- [ ] Create ShopFloorDashboard component
- [ ] Create WorkCenterStatusCard component
- [ ] Create OperationQueueList component
- [ ] Create ActiveOperationsList component
- [ ] Create CompletedOperationsToday component
- [ ] Add auto-refresh (every 30 seconds)
- [ ] Add real-time status indicators
- [ ] Add work center filter
- [ ] Make mobile-responsive

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/ShopFloorDashboard.tsx` (new)
- `client/src/features/manufacturing/components/WorkCenterStatusCard.tsx` (new)
- `client/src/features/manufacturing/components/OperationQueueList.tsx` (new)
- `client/src/features/manufacturing/components/ActiveOperationsList.tsx` (new)
- `client/src/features/manufacturing/api/shopFloor.ts` (new)

### Task 3.6: Frontend - Operation Execution Interface
**Acceptance Criteria**: AC6
**Estimated Time**: 8 hours

- [ ] Create OperationExecutionView component
- [ ] Create OperationCard component with start/complete buttons
- [ ] Add timer showing elapsed time
- [ ] Add notes/comments field
- [ ] Add block/pause functionality with reason
- [ ] Show operation details (MO, product, work center)
- [ ] Add confirmation dialogs
- [ ] Make mobile-friendly for shop floor tablets

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/OperationExecutionView.tsx` (new)
- `client/src/features/manufacturing/components/OperationCard.tsx` (new)
- `client/src/features/manufacturing/components/OperationTimer.tsx` (new)

## Phase 4: Advanced Scheduling (Week 7-8)

### Task 4.1: Drag-and-Drop Rescheduling Backend
**Acceptance Criteria**: AC4
**Properties**: P2, P5
**Estimated Time**: 6 hours

- [ ] Implement reschedule_operation()
- [ ] Validate new time slot availability
- [ ] Check capacity constraints
- [ ] Update dependent operations (if sequence affected)
- [ ] Update WorkCenterSchedule records
- [ ] Return conflicts if any

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/scheduling_service.py` (update)

### Task 4.2: Conflict Detection
**Acceptance Criteria**: AC4, AC5
**Properties**: P5
**Estimated Time**: 4 hours

- [ ] Implement detect_scheduling_conflicts()
- [ ] Check for overlapping operations at same work center
- [ ] Check for capacity overallocation
- [ ] Check for sequence violations
- [ ] Return detailed conflict information

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/scheduling_service.py` (update)

### Task 4.3: Rescheduling API Endpoints
**Acceptance Criteria**: AC4
**Estimated Time**: 2 hours

- [ ] POST /api/manufacturing/schedule/reschedule
- [ ] GET /api/manufacturing/schedule/conflicts
- [ ] Add validation and error handling

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/scheduling.py` (update)

### Task 4.4: Frontend - Drag-and-Drop Scheduler
**Acceptance Criteria**: AC4
**Estimated Time**: 12 hours

- [ ] Add drag-and-drop to OperationBlock component
- [ ] Implement drop zones on timeline
- [ ] Show visual feedback during drag
- [ ] Validate drop location (capacity, conflicts)
- [ ] Show conflict warnings
- [ ] Update schedule on successful drop
- [ ] Add undo functionality
- [ ] Optimize for performance (virtual scrolling if needed)

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/GanttChart.tsx` (update)
- `client/src/features/manufacturing/components/OperationBlock.tsx` (update)
- `client/src/features/manufacturing/hooks/useDragAndDrop.ts` (new)

### Task 4.5: Frontend - Capacity Warnings
**Acceptance Criteria**: AC5
**Estimated Time**: 4 hours

- [ ] Show capacity utilization bars on scheduler
- [ ] Highlight overallocated time periods
- [ ] Show warning modal when scheduling exceeds capacity
- [ ] Add capacity legend/indicator

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/CapacityIndicator.tsx` (new)
- `client/src/features/manufacturing/components/SchedulerView.tsx` (update)

## Phase 5: Analytics (Week 9-10)

### Task 5.1: Capacity Analytics Service
**Acceptance Criteria**: AC8, AC9
**Estimated Time**: 8 hours

- [ ] Create CapacityAnalyticsService
- [ ] Implement get_utilization_report()
- [ ] Implement get_bottleneck_analysis()
- [ ] Implement get_operation_performance()
- [ ] Implement get_cycle_time_analysis()
- [ ] Calculate actual vs estimated time variance
- [ ] Identify high-utilization work centers
- [ ] Identify operations with longest queues

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/capacity_analytics_service.py` (new)
- `backend/app/modules/manufacturing/application/services/__init__.py` (update)

### Task 5.2: Analytics API Endpoints
**Acceptance Criteria**: AC8, AC9
**Estimated Time**: 4 hours

- [ ] GET /api/manufacturing/analytics/capacity-utilization
- [ ] GET /api/manufacturing/analytics/bottlenecks
- [ ] GET /api/manufacturing/analytics/operation-performance
- [ ] GET /api/manufacturing/analytics/cycle-times
- [ ] Add date range and filter parameters

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/api/analytics.py` (new)
- `backend/app/modules/manufacturing/api/router.py` (update)

### Task 5.3: Frontend - Analytics Dashboard
**Acceptance Criteria**: AC8
**Estimated Time**: 10 hours

- [ ] Create AnalyticsDashboard component
- [ ] Create UtilizationChart component (bar/line chart)
- [ ] Create PerformanceMetrics component
- [ ] Create CycleTimeChart component
- [ ] Add date range selector
- [ ] Add work center filter
- [ ] Add product filter
- [ ] Display key metrics (cards)

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/AnalyticsDashboard.tsx` (new)
- `client/src/features/manufacturing/components/UtilizationChart.tsx` (new)
- `client/src/features/manufacturing/components/PerformanceMetrics.tsx` (new)
- `client/src/features/manufacturing/components/CycleTimeChart.tsx` (new)
- `client/src/features/manufacturing/api/analytics.ts` (new)

### Task 5.4: Frontend - Bottleneck View
**Acceptance Criteria**: AC9
**Estimated Time**: 6 hours

- [ ] Create BottleneckView component
- [ ] Display bottleneck work centers with metrics
- [ ] Show queue length and wait times
- [ ] Show utilization percentage
- [ ] Highlight critical bottlenecks
- [ ] Add recommendations or alerts

**Files to Create/Modify**:
- `client/src/features/manufacturing/components/BottleneckView.tsx` (new)
- `client/src/features/manufacturing/components/BottleneckCard.tsx` (new)

## Phase 6: Integration & Polish (Week 11-12)

### Task 6.1: Sales Module Integration
**Acceptance Criteria**: AC10
**Estimated Time**: 6 hours

- [ ] Update sales order delivery date calculation to consider production schedule
- [ ] Add API endpoint to suggest delivery dates based on capacity
- [ ] Update sales order status when production starts
- [ ] Update sales order status when production completes
- [ ] Add production schedule link in sales order detail view

**Files to Create/Modify**:
- `backend/app/modules/sales/application/services/sales_order_service.py` (update)
- `backend/app/modules/manufacturing/api/scheduling.py` (update)
- `client/src/features/sales/components/SalesOrderDetail.tsx` (update)

### Task 6.2: Inventory Module Integration
**Acceptance Criteria**: AC10
**Properties**: P6
**Estimated Time**: 4 hours

- [ ] Trigger auto-scheduling when material requisition is approved
- [ ] Check material availability before scheduling
- [ ] Update MO status if materials become unavailable
- [ ] Add material availability indicator in scheduler

**Files to Create/Modify**:
- `backend/app/modules/inventory/application/services/material_requisition_service.py` (update)
- `backend/app/modules/manufacturing/application/services/scheduling_service.py` (update)

### Task 6.3: Notifications Integration
**Acceptance Criteria**: AC10
**Estimated Time**: 4 hours

- [ ] Send notification when operation is assigned to operator
- [ ] Send notification when operation is blocked
- [ ] Send notification when work center is overallocated
- [ ] Send notification when MO is scheduled
- [ ] Add notification preferences for production users

**Files to Create/Modify**:
- `backend/app/modules/manufacturing/application/services/shop_floor_service.py` (update)
- `backend/app/modules/manufacturing/application/services/scheduling_service.py` (update)
- `backend/app/modules/notifications/application/services/notification_service.py` (update)

### Task 6.4: Permissions & Security
**Estimated Time**: 4 hours

- [ ] Define production-related permissions
- [ ] Add role-based access control to endpoints
- [ ] Restrict operation execution to assigned operators
- [ ] Add audit logging for sensitive operations
- [ ] Test permission enforcement

**Files to Create/Modify**:
- `backend/app/middleware/auth.py` (update)
- `backend/app/modules/manufacturing/api/*.py` (update all)

### Task 6.5: Performance Optimization
**Estimated Time**: 6 hours

- [ ] Add database indexes
- [ ] Implement caching for dashboard data
- [ ] Optimize scheduler queries (N+1 prevention)
- [ ] Add pagination to operation lists
- [ ] Profile and optimize slow queries
- [ ] Add database query logging

**Files to Create/Modify**:
- `backend/alembic/versions/xxx_add_indexes.py` (new)
- Various service files (add caching)

### Task 6.6: Testing
**Estimated Time**: 12 hours

- [ ] Write unit tests for SchedulingService
- [ ] Write unit tests for ShopFloorService
- [ ] Write unit tests for CapacityAnalyticsService
- [ ] Write integration tests for operation generation
- [ ] Write integration tests for scheduling flow
- [ ] Write integration tests for shop floor execution
- [ ] Write E2E tests for scheduler UI
- [ ] Write E2E tests for shop floor dashboard
- [ ] Test concurrent operation updates
- [ ] Test capacity constraint validation

**Files to Create/Modify**:
- `backend/tests/modules/manufacturing/test_scheduling_service.py` (new)
- `backend/tests/modules/manufacturing/test_shop_floor_service.py` (new)
- `backend/tests/modules/manufacturing/test_capacity_analytics_service.py` (new)
- `backend/tests/modules/manufacturing/test_scheduling_integration.py` (new)

### Task 6.7: Documentation
**Estimated Time**: 4 hours

- [ ] Write user guide for production planners
- [ ] Write user guide for shop floor operators
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Create video tutorials for key workflows
- [ ] Document scheduling algorithm
- [ ] Add inline code documentation

**Files to Create/Modify**:
- `backend/docs/production-scheduling-guide.md` (new)
- `backend/docs/shop-floor-guide.md` (new)
- `backend/docs/api/manufacturing.md` (update)

### Task 6.8: User Acceptance Testing
**Estimated Time**: 8 hours

- [ ] Conduct UAT with production planners
- [ ] Conduct UAT with shop floor supervisors
- [ ] Conduct UAT with operators
- [ ] Gather feedback and create bug list
- [ ] Fix critical bugs
- [ ] Validate all acceptance criteria
- [ ] Get sign-off from stakeholders

### Task 6.9: Deployment Preparation
**Estimated Time**: 4 hours

- [ ] Create deployment checklist
- [ ] Prepare database migration scripts
- [ ] Create rollback plan
- [ ] Set up monitoring and alerts
- [ ] Prepare training materials
- [ ] Schedule deployment window
- [ ] Communicate to users

## Summary

**Total Estimated Time**: ~240 hours (12 weeks at 20 hours/week)

**Critical Path**:
1. Database models and migrations
2. Operation generation and scheduling
3. Shop floor execution
4. Scheduler UI
5. Integration with existing modules

**Dependencies**:
- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 2
- Phase 4 depends on Phase 3
- Phase 5 can be done in parallel with Phase 4
- Phase 6 depends on all previous phases

**Risk Areas**:
- Scheduler UI complexity (drag-and-drop with constraints)
- Performance with large datasets (500+ operations)
- Concurrent updates to operation status
- Integration with existing manufacturing order workflow
