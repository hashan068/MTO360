# Production Scheduling & Shop Floor Management - Requirements

## Overview

Add production scheduling and shop floor management capabilities to enable capacity planning, work center management, operation routing, and real-time production tracking for the MTO360 system.

## Business Goals

- Enable realistic delivery date commitments based on actual capacity
- Provide visibility into production bottlenecks and resource utilization
- Track work-in-progress (WIP) across all manufacturing orders
- Optimize production sequencing to maximize throughput
- Capture actual production times for continuous improvement

## Target Users

- **Production Planners**: Schedule and sequence manufacturing orders
- **Shop Floor Supervisors**: Track production progress and manage work centers
- **Production Operators**: Update job status and record completion
- **Management**: Monitor capacity utilization and production metrics

## Acceptance Criteria

### AC1: Work Center Management
- System shall allow creation and management of work centers (e.g., Assembly Station 1, Testing Bay, Soldering Station)
- Each work center shall have:
  - Name and description
  - Capacity (hours per day/shift)
  - Active/inactive status
  - Assigned operators (optional)
- System shall support multiple shifts per work center
- Users shall be able to view work center utilization (scheduled vs available capacity)

### AC2: Operation Routing
- System shall allow defining operation routes for products
- Each route shall consist of sequential operations
- Each operation shall specify:
  - Operation name/description
  - Work center where it's performed
  - Standard time (estimated duration)
  - Sequence order
- Routes shall be linked to products or BOMs
- System shall support copying routes from existing products

### AC3: Manufacturing Order Operations
- When a manufacturing order is created, system shall automatically generate operations based on the product's route
- Each MO operation shall track:
  - Assigned work center
  - Scheduled start/end times
  - Actual start/end times
  - Status (pending, in_progress, completed, blocked)
  - Assigned operator
  - Notes/comments
- Operations shall follow sequence constraints (operation 2 can't start until operation 1 is complete)

### AC4: Production Scheduling
- System shall provide a visual scheduler showing:
  - Work centers (rows)
  - Time periods (columns - day/week view)
  - Scheduled operations as blocks
- Scheduler shall display:
  - MO number and product
  - Operation name
  - Scheduled duration
  - Status color coding
- Users shall be able to drag-and-drop operations to reschedule
- System shall validate capacity constraints when scheduling
- System shall warn about overallocated work centers

### AC5: Capacity Planning
- System shall calculate available capacity per work center per time period
- System shall calculate scheduled/allocated capacity
- System shall display capacity utilization percentage
- System shall highlight overallocated periods (>100% capacity)
- System shall support "what-if" scenarios by tentatively scheduling orders

### AC6: Shop Floor Execution
- Operators shall be able to:
  - View assigned operations for their work center
  - Start an operation (records actual start time)
  - Complete an operation (records actual end time)
  - Pause/resume operations
  - Report issues or blockages
- System shall update MO status based on operation completion:
  - All operations pending → MO status: pending
  - Any operation in progress → MO status: in_production
  - All operations completed → MO status: completed

### AC7: Production Dashboard
- System shall provide a shop floor dashboard showing:
  - Current operations in progress by work center
  - Pending operations queue
  - Completed operations today
  - Work center status (idle, busy, blocked)
  - Real-time WIP count
- Dashboard shall auto-refresh or support real-time updates

### AC8: Production Metrics
- System shall track and display:
  - Actual vs estimated operation times
  - Work center utilization rates
  - Average cycle time per product
  - On-time completion rate
  - Operations completed per day/week
- Metrics shall be filterable by date range, work center, product

### AC9: Bottleneck Identification
- System shall identify bottlenecks by:
  - Highest utilization work centers
  - Work centers with longest queue
  - Operations with highest variance (actual vs estimated time)
- System shall provide alerts for critical bottlenecks

### AC10: Integration with Existing Modules
- Manufacturing orders shall automatically schedule operations when MR is approved
- Material requisition approval shall check if materials are available before scheduling
- Sales order delivery dates shall consider production schedule
- System shall update sales order status when production starts/completes

## User Stories

### US1: As a Production Planner
I want to define work centers with their capacities so that I can schedule work realistically based on available resources.

### US2: As a Production Engineer
I want to create operation routes for products so that the system knows the manufacturing steps and can schedule them automatically.

### US3: As a Production Planner
I want to see a visual schedule of all operations across work centers so that I can identify capacity issues and optimize sequencing.

### US4: As a Production Planner
I want to drag-and-drop operations to reschedule them so that I can quickly adjust the plan when priorities change.

### US5: As a Shop Floor Supervisor
I want to see which operations are assigned to each work center so that I can assign operators and manage the workload.

### US6: As a Production Operator
I want to start and complete operations from a simple interface so that the system tracks actual production progress.

### US7: As a Production Manager
I want to see capacity utilization across all work centers so that I can identify bottlenecks and make investment decisions.

### US8: As a Production Manager
I want to see actual vs estimated operation times so that I can improve our time estimates and identify training needs.

### US9: As a Sales Manager
I want the system to suggest realistic delivery dates based on production capacity so that I can set accurate customer expectations.

### US10: As a Shop Floor Supervisor
I want to see a real-time dashboard of production status so that I can quickly identify and resolve issues.

## Non-Functional Requirements

### NFR1: Performance
- Scheduler shall load and render within 2 seconds for up to 100 concurrent operations
- Dashboard shall refresh within 1 second
- Drag-and-drop rescheduling shall provide immediate visual feedback

### NFR2: Usability
- Scheduler shall be intuitive with minimal training required
- Color coding shall be consistent and accessible (colorblind-friendly)
- Mobile-responsive interface for shop floor operators

### NFR3: Data Integrity
- Operation status changes shall be atomic and logged
- Concurrent updates shall be handled with optimistic locking
- Audit trail for all schedule changes

### NFR4: Scalability
- System shall support at least 50 work centers
- System shall handle 500+ active manufacturing orders
- Scheduler shall support 6-month planning horizon

## Out of Scope (Future Enhancements)

- Advanced optimization algorithms (genetic algorithms, constraint programming)
- Integration with IoT sensors or machine monitoring
- Automated scheduling based on AI/ML
- Finite capacity scheduling with setup times
- Multi-level production planning (MPS/MRP II)
- Preventive maintenance scheduling
- Tool and fixture management

## Dependencies

- Existing Manufacturing module (Manufacturing Orders, BOMs)
- Existing Inventory module (Material Requisitions)
- Existing Sales module (Sales Orders, delivery dates)
- User authentication and authorization

## Assumptions

- Work centers operate on standard shifts (configurable hours per day)
- Operations are performed sequentially (no parallel operations initially)
- One operation per work center at a time (no multi-tasking)
- Material availability is checked before scheduling (via MR approval)
- Standard times are reasonably accurate (within 20% variance)

## Success Metrics

- 90% of manufacturing orders scheduled within 24 hours of MR approval
- Capacity utilization visible for all work centers
- 80% of operations completed within estimated time ±20%
- Delivery date accuracy improved by 30%
- Production bottlenecks identified and reported weekly
