# Advanced Planning & Scheduling (APS) - Spec Summary

## Overview
Replace the current simple forward scheduling algorithm with advanced constraint-based optimization to maximize throughput, minimize tardiness, and balance work center utilization.

## Business Value
- Reduce lead times by 20-30%
- Improve on-time delivery by 25%
- Increase capacity utilization by 15%
- Reduce overtime by 20%

## Timeline: 10-12 weeks | Complexity: High

---

## Key Features

### 1. Constraint-Based Scheduling
**Handle multiple constraints simultaneously:**
- Finite capacity (work center hours)
- Setup times (changeover between products)
- Tool/fixture availability
- Operator skill matching
- Material availability
- Sequence dependencies
- Due date constraints
- Priority levels (rush orders)

**Models:**
```python
class SchedulingConstraint(Base):
    constraint_type: ConstraintTypeEnum  # capacity, setup, tool, skill, material
    entity_type: str  # work_center, operation, resource
    entity_id: int
    constraint_data: JSON  # Flexible constraint definition
    is_hard: bool  # Hard constraint (must satisfy) vs soft (prefer to satisfy)
    weight: int  # For soft constraints, optimization weight

class SetupTime(Base):
    work_center_id: int
    from_product_id: int
    to_product_id: int
    setup_minutes: int  # Time to changeover
    
class ToolRequirement(Base):
    route_operation_id: int
    tool_id: int
    quantity_required: int
    
class Tool(Base):
    tool_id: int
    name: str
    quantity_available: int
    work_center_id: Optional[int]  # If tool is specific to work center
    
class OperatorSkill(Base):
    operator_id: int
    work_center_id: int
    skill_level: SkillLevelEnum  # beginner, intermediate, expert
    efficiency_factor: Decimal  # 0.8 = 80% of standard time
```

### 2. Optimization Algorithms
**Multiple optimization objectives:**
- **Minimize Makespan**: Total time to complete all orders
- **Minimize Tardiness**: Sum of late days across orders
- **Maximize Throughput**: Number of orders completed
- **Balance Utilization**: Even load across work centers
- **Minimize Setup Time**: Reduce changeovers

**Algorithms:**
- **Genetic Algorithm** (GA): Population-based search
- **Constraint Programming** (CP): Google OR-Tools
- **Simulated Annealing**: Probabilistic optimization
- **Dispatching Rules**: Priority-based heuristics (EDD, SPT, CR)

**Models:**
```python
class SchedulingObjective(Base):
    objective_type: ObjectiveTypeEnum  # minimize_makespan, minimize_tardiness, etc.
    weight: Decimal  # For multi-objective optimization
    is_active: bool
    
class ScheduleScenario(Base):
    scenario_id: int
    name: str
    description: str
    created_at: datetime
    created_by_id: int
    objectives: JSON  # List of objectives with weights
    constraints: JSON  # List of constraints
    schedule_data: JSON  # Serialized schedule
    metrics: JSON  # Makespan, tardiness, utilization, etc.
    is_active: bool  # Currently active schedule
```

### 3. Scenario Planning
**"What-if" analysis:**
- Save multiple schedule scenarios
- Compare scenarios side-by-side
- Simulate adding new orders
- Simulate capacity changes
- Simulate equipment downtime
- Rollback to previous schedule
- Scenario metrics comparison

**Models:**
```python
class ScheduleComparison(Base):
    comparison_id: int
    scenario_ids: JSON  # List of scenario IDs to compare
    comparison_metrics: JSON  # Side-by-side metrics
    created_at: datetime
    created_by_id: int
```

### 4. Dynamic Rescheduling
**Handle disruptions in real-time:**
- Rush order insertion (high priority)
- Equipment breakdown handling
- Material shortage handling
- Operator absence
- Order cancellation
- Due date changes
- Auto-reschedule on disruption
- Minimize schedule disruption (stability)

**Models:**
```python
class ScheduleDisruption(Base):
    disruption_id: int
    disruption_type: DisruptionTypeEnum  # rush_order, breakdown, shortage, absence
    entity_type: str  # work_center, material, operator
    entity_id: int
    occurred_at: datetime
    resolved_at: Optional[datetime]
    impact_description: str
    rescheduling_triggered: bool
    
class ReschedulingEvent(Base):
    event_id: int
    disruption_id: Optional[int]
    trigger_type: TriggerTypeEnum  # manual, automatic, disruption
    old_scenario_id: int
    new_scenario_id: int
    operations_affected: int
    rescheduling_time_seconds: Decimal
    created_at: datetime
```

### 5. Advanced Visualizations
**Enhanced scheduling views:**
- **Load Chart**: Work center utilization over time
- **Critical Path**: Longest path through operations
- **Bottleneck Visualization**: Highlight constrained resources
- **Schedule Feasibility**: Color-coded by constraint violations
- **Gantt with Dependencies**: Show operation dependencies
- **Resource Allocation**: Tool/operator assignments
- **Setup Time Visualization**: Show changeover times

**UI Components:**
- Interactive Gantt with constraint indicators
- Load chart with capacity lines
- Critical path overlay
- Bottleneck heatmap
- Scenario comparison dashboard

---

## API Endpoints

### Optimization
```
POST   /api/scheduling/optimize
POST   /api/scheduling/optimize/genetic-algorithm
POST   /api/scheduling/optimize/constraint-programming
GET    /api/scheduling/optimization-status/{job_id}
```

### Scenarios
```
POST   /api/scheduling/scenarios
GET    /api/scheduling/scenarios
GET    /api/scheduling/scenarios/{id}
PUT    /api/scheduling/scenarios/{id}
DELETE /api/scheduling/scenarios/{id}
POST   /api/scheduling/scenarios/{id}/activate
POST   /api/scheduling/scenarios/compare
```

### Constraints
```
POST   /api/scheduling/constraints
GET    /api/scheduling/constraints
PUT    /api/scheduling/constraints/{id}
DELETE /api/scheduling/constraints/{id}
GET    /api/scheduling/constraints/violations
```

### Dynamic Rescheduling
```
POST   /api/scheduling/reschedule/rush-order
POST   /api/scheduling/reschedule/breakdown
POST   /api/scheduling/reschedule/auto
GET    /api/scheduling/disruptions
```

### Analytics
```
GET    /api/scheduling/analytics/critical-path
GET    /api/scheduling/analytics/bottlenecks
GET    /api/scheduling/analytics/load-chart
GET    /api/scheduling/analytics/schedule-metrics
```

---

## Key Services

### OptimizationService
- optimize_schedule(objectives, constraints, algorithm)
- genetic_algorithm_optimize(population_size, generations)
- constraint_programming_optimize(time_limit)
- calculate_schedule_metrics(scenario)

### ScenarioService
- create_scenario(name, objectives, constraints)
- save_scenario(scenario_data)
- compare_scenarios(scenario_ids)
- activate_scenario(scenario_id)
- rollback_to_scenario(scenario_id)

### ConstraintService
- add_constraint(constraint_data)
- validate_constraints(schedule)
- detect_violations(schedule)
- suggest_constraint_relaxation()

### DynamicReschedulingService
- handle_rush_order(order_id, priority)
- handle_breakdown(work_center_id, downtime_minutes)
- handle_material_shortage(component_id, shortage_quantity)
- auto_reschedule(disruption)
- minimize_schedule_disruption(old_schedule, new_schedule)

### CriticalPathService
- calculate_critical_path(scenario)
- identify_bottlenecks(scenario)
- calculate_slack_time(operation)

---

## Optimization Algorithms

### 1. Genetic Algorithm (GA)
**Best for**: Multi-objective optimization, large problem sizes

**Parameters:**
- Population size: 100-500
- Generations: 50-200
- Crossover rate: 0.7-0.9
- Mutation rate: 0.01-0.1

**Chromosome Encoding**: Operation sequence + work center assignment

**Fitness Function**: Weighted sum of objectives

### 2. Constraint Programming (CP)
**Best for**: Hard constraints, feasibility checking

**Tool**: Google OR-Tools CP-SAT Solver

**Variables**: Operation start times, work center assignments

**Constraints**: Capacity, precedence, resource availability

### 3. Dispatching Rules (Heuristics)
**Fast approximations:**
- **EDD** (Earliest Due Date): Minimize tardiness
- **SPT** (Shortest Processing Time): Minimize makespan
- **CR** (Critical Ratio): Balance urgency and slack
- **FIFO** (First In First Out): Simple queue

---

## UI Components

1. **Optimization Configuration**
   - Select objectives and weights
   - Configure constraints
   - Choose algorithm
   - Set parameters

2. **Scenario Manager**
   - Scenario list
   - Create/edit scenario
   - Scenario comparison table
   - Activate scenario

3. **Advanced Gantt Chart**
   - Critical path overlay
   - Constraint violation indicators
   - Setup time blocks
   - Resource assignments
   - Drag-and-drop with validation

4. **Load Chart**
   - Work center utilization over time
   - Capacity lines
   - Overload indicators
   - Bottleneck highlighting

5. **Critical Path View**
   - Network diagram
   - Critical operations highlighted
   - Slack time display

6. **Bottleneck Analysis**
   - Bottleneck work centers
   - Queue length
   - Utilization percentage
   - Recommendations

7. **Disruption Manager**
   - Active disruptions
   - Rescheduling triggers
   - Impact assessment
   - Reschedule button

---

## Integration Points

- **Production Scheduling**: Replace simple algorithm
- **Shop Floor**: Real-time schedule updates on disruptions
- **Sales**: Promise dates based on optimized schedule
- **Maintenance**: Consider PM schedules as constraints
- **Quality**: Rework operations in optimization

---

## Performance Considerations

### Optimization Performance
- **Small problems** (<50 operations): <5 seconds
- **Medium problems** (50-200 operations): <30 seconds
- **Large problems** (200-500 operations): <2 minutes
- **Very large problems** (>500 operations): Background job

### Strategies:
- Incremental optimization (only reschedule affected operations)
- Time-limited optimization (return best solution found)
- Parallel optimization (multiple algorithms simultaneously)
- Caching of constraint checks

---

## Success Metrics

- Lead times reduced by 20-30%
- On-time delivery improved by 25%
- Capacity utilization increased by 15%
- Overtime reduced by 20%
- Schedule optimization time <30 seconds for typical problems
- 90% of schedules feasible (no constraint violations)
- Rescheduling after disruption <1 minute

---

## Implementation Phases

**Phase 1 (Weeks 1-2)**: Constraint modeling & validation
**Phase 2 (Weeks 3-4)**: Genetic Algorithm implementation
**Phase 3 (Weeks 5-6)**: Constraint Programming integration (OR-Tools)
**Phase 4 (Weeks 7-8)**: Scenario management & comparison
**Phase 5 (Weeks 9-10)**: Dynamic rescheduling
**Phase 6 (Weeks 11-12)**: Advanced visualizations & optimization

---

## Technical Dependencies

### External Libraries
- **Google OR-Tools**: Constraint programming solver
- **DEAP** (Python): Genetic algorithm framework
- **NumPy/Pandas**: Data manipulation
- **Plotly/D3.js**: Advanced visualizations

### Infrastructure
- Background job queue (Celery/Redis) for long optimizations
- Caching layer (Redis) for constraint checks
- Database optimization for large datasets

---

## Risks & Mitigation

### Risk 1: Optimization Performance
**Risk**: Large problems may take too long  
**Mitigation**: Time-limited optimization, incremental rescheduling, background jobs

### Risk 2: Algorithm Complexity
**Risk**: Difficult to tune and maintain  
**Mitigation**: Start with simple heuristics, add advanced algorithms incrementally

### Risk 3: User Adoption
**Risk**: Users may not trust automated scheduling  
**Mitigation**: Scenario comparison, manual override, gradual rollout

### Risk 4: Integration Complexity
**Risk**: Complex integration with existing scheduling  
**Mitigation**: Parallel run (old + new), phased migration

---

**Full detailed specs (requirements.md, design.md, tasks.md) to be created when this feature is prioritized.**
