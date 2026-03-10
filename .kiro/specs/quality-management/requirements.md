# Quality Management System (QMS) - Requirements

## Overview

Implement a comprehensive Quality Management System to track inspections, defects, non-conformances, and corrective actions throughout the manufacturing process. Enable data-driven quality improvements and support ISO 9001 compliance.

## Business Goals

- Reduce defect rates by 30-50% within 6 months
- Reduce rework and scrap costs by 40%
- Improve First Pass Yield (FPY) to >95%
- Enable root cause analysis and continuous improvement
- Support ISO 9001 certification path
- Improve customer satisfaction by reducing quality complaints

## Target Users

- **Quality Inspectors**: Perform inspections and record results
- **Production Operators**: Report defects during production
- **Quality Engineers**: Analyze quality data and manage CAPAs
- **Quality Manager**: Monitor quality metrics and trends
- **Production Manager**: View quality impact on production
- **Management**: Quality dashboards and compliance reporting

## Acceptance Criteria

### AC1: Inspection Management
- System shall allow defining inspection points in operation routes
- Inspection types supported:
  - In-process inspection (during operations)
  - Final inspection (before delivery)
  - Receiving inspection (incoming materials)
  - First article inspection (FAI)
- Each inspection shall have:
  - Inspection checklist with criteria
  - Pass/fail thresholds
  - Required measurements/tests
  - Photo/document attachments
- Inspectors shall be able to:
  - View assigned inspections
  - Record inspection results (pass/fail/conditional)
  - Record measurements
  - Attach photos/documents
  - Add notes/comments
- System shall prevent operation completion if required inspection fails
- System shall track inspection completion rate

### AC2: Defect Tracking
- System shall allow recording defects at any stage:
  - During production operations
  - During inspections
  - At receiving (supplier defects)
  - Customer returns
- Each defect shall capture:
  - Defect type (material, workmanship, design, other)
  - Severity (critical, major, minor, cosmetic)
  - Location (operation, work center, component)
  - Description and root cause
  - Responsible party (operator, supplier, design)
  - Photos/evidence
  - Quantity affected
- System shall categorize defects by:
  - Product/BOM
  - Operation/work center
  - Operator
  - Defect type
  - Time period
- System shall link defects to:
  - Manufacturing orders
  - Operations
  - Operators
  - Suppliers (for material defects)
  - Components/materials

### AC3: Non-Conformance Management (NCR)
- System shall support NCR workflow:
  - Create NCR from defect or inspection failure
  - Assign NCR owner
  - Investigation and root cause analysis
  - Disposition decision (rework, scrap, use-as-is, return to supplier)
  - Approval workflow (multi-level if needed)
  - Close NCR with verification
- NCR shall track:
  - NCR number (auto-generated)
  - Status (open, investigating, pending approval, approved, closed)
  - Priority (urgent, high, normal, low)
  - Affected quantity
  - Cost impact (rework labor, scrap cost)
  - Containment actions
  - Root cause
  - Disposition
  - Approvers and approval dates
- System shall support quality holds:
  - Hold inventory (quarantine)
  - Hold manufacturing order
  - Hold sales order shipment
  - Release hold after approval
- System shall track NCR aging and overdue NCRs

### AC4: Rework & Scrap Management
- System shall track rework operations:
  - Create rework operation from NCR
  - Assign to work center/operator
  - Track rework time and cost
  - Verify rework completion (re-inspection)
- System shall track scrap:
  - Scrap quantity and reason
  - Scrap cost (material + labor)
  - Scrap by product/operation/operator
  - Scrap inventory transactions
- System shall calculate Cost of Quality (COQ):
  - Internal failure costs (rework, scrap)
  - External failure costs (returns, warranty)
  - Appraisal costs (inspection labor)
  - Prevention costs (quality planning)

### AC5: Corrective & Preventive Actions (CAPA)
- System shall support CAPA workflow:
  - Create CAPA from NCR or quality trend
  - Root cause analysis (5 Whys, Fishbone)
  - Corrective action plan
  - Preventive action plan
  - Assign action owners
  - Set due dates
  - Track action completion
  - Verify effectiveness
- CAPA shall track:
  - CAPA number
  - Status (open, in progress, verification, closed)
  - Priority
  - Root cause category
  - Actions (description, owner, due date, status)
  - Effectiveness verification
  - Recurrence prevention
- System shall link CAPAs to:
  - NCRs
  - Defects
  - Audit findings
  - Customer complaints

### AC6: Quality Metrics & Analytics
- System shall calculate and display:
  - **First Pass Yield (FPY)**: % of units passing first time
    - By product
    - By operation
    - By work center
    - By operator
    - Trend over time
  - **Defect Rate**: Defects per unit or per 1000 units
    - By defect type
    - By severity
    - By source (internal vs supplier)
  - **Inspection Pass Rate**: % of inspections passed
  - **Rework Rate**: % of units requiring rework
  - **Scrap Rate**: % of units scrapped
  - **Cost of Quality**: Total COQ and breakdown
  - **NCR Metrics**: Open NCRs, aging, closure time
  - **CAPA Metrics**: Open CAPAs, on-time completion rate
- System shall provide quality dashboards:
  - Real-time quality status
  - Quality trends (daily, weekly, monthly)
  - Pareto charts (top defect types)
  - Control charts (SPC - future)
  - Operator quality performance
  - Supplier quality performance

### AC7: Quality Alerts & Notifications
- System shall send alerts for:
  - Inspection failure
  - Critical defect detected
  - NCR created or assigned
  - NCR overdue
  - CAPA action due or overdue
  - Quality hold placed
  - Quality threshold exceeded (e.g., defect rate >5%)
  - Recurring defect pattern detected

### AC8: Integration with Existing Modules
- **Manufacturing Orders**:
  - Link inspections to operations
  - Block MO completion if inspection fails
  - Track quality status per MO
- **Shop Floor**:
  - Operators record defects during operations
  - Quality holds block operation start
  - Rework operations in shop floor queue
- **Inventory**:
  - Receiving inspection for incoming materials
  - Quarantine stock (quality hold)
  - Scrap transactions
  - Supplier quality data
- **Sales**:
  - Final inspection before delivery
  - Customer return/complaint tracking
  - Link quality data to customer
- **Notifications**:
  - Quality alerts to relevant users

### AC9: Reporting & Compliance
- System shall generate reports:
  - Quality summary report (daily, weekly, monthly)
  - Defect analysis report
  - NCR report
  - CAPA report
  - Cost of Quality report
  - Operator quality report
  - Supplier quality report
  - Audit trail report
- Reports shall be exportable (PDF, Excel)
- System shall maintain audit trail:
  - All quality records timestamped
  - User who created/modified records
  - Status change history
  - Approval history

### AC10: Mobile Support
- Quality inspectors shall be able to use mobile devices:
  - View inspection checklists
  - Record inspection results
  - Take photos
  - Record defects
  - Access from shop floor (tablet/phone)

## User Stories

### US1: As a Quality Inspector
I want to view my assigned inspections for the day so that I can plan my work and ensure all inspections are completed on time.

### US2: As a Quality Inspector
I want to record inspection results with photos and measurements so that I have evidence of quality checks.

### US3: As a Production Operator
I want to report defects I find during production so that quality issues are documented and addressed.

### US4: As a Quality Engineer
I want to create an NCR when a defect is found so that we can investigate and determine the proper disposition.

### US5: As a Quality Engineer
I want to analyze defect trends by type and location so that I can identify root causes and implement corrective actions.

### US6: As a Quality Manager
I want to see First Pass Yield trends by product so that I can measure quality improvement over time.

### US7: As a Quality Manager
I want to track Cost of Quality so that I can quantify the financial impact of quality issues and justify quality investments.

### US8: As a Production Manager
I want to see which operators have the highest defect rates so that I can provide targeted training.

### US9: As a Purchasing Manager
I want to see supplier quality ratings so that I can make informed decisions about supplier selection.

### US10: As Management
I want a quality dashboard showing key metrics so that I can monitor quality performance at a glance.

## Non-Functional Requirements

### NFR1: Performance
- Inspection recording shall complete within 2 seconds
- Quality dashboard shall load within 3 seconds
- Defect search shall return results within 1 second
- Support 1000+ inspections per day

### NFR2: Usability
- Mobile-friendly inspection interface
- Barcode/QR code scanning for MO/component identification
- Photo capture from mobile camera
- Offline mode for inspections (sync when online)
- Intuitive defect categorization

### NFR3: Data Integrity
- All quality records immutable (no deletion, only status changes)
- Complete audit trail
- Approval workflows with electronic signatures
- Data validation (required fields, valid ranges)

### NFR4: Compliance
- Support ISO 9001 requirements
- Audit trail for all quality records
- Document control (inspection procedures, work instructions)
- Traceability (lot/serial number tracking)

### NFR5: Scalability
- Support 10,000+ inspections per month
- Support 5,000+ defects per month
- Historical data retention (5+ years)
- Efficient queries for large datasets

## Out of Scope (Future Enhancements)

- Statistical Process Control (SPC) charts
- Advanced root cause analysis tools (Fishbone, FMEA)
- Supplier portal for quality collaboration
- Customer portal for quality data sharing
- Integration with measurement equipment (CMM, calipers)
- Automated defect detection (AI/ML)
- Gage R&R studies
- Calibration management
- Document management system (DMS)

## Dependencies

- Existing Manufacturing module (MOs, Operations)
- Existing Shop Floor module (Operation execution)
- Existing Inventory module (Components, Suppliers)
- Existing Sales module (Sales Orders, Customers)
- User authentication and authorization

## Assumptions

- Inspectors have mobile devices (tablets or phones)
- Quality criteria are defined per product/operation
- Operators are trained to identify and report defects
- Management supports quality culture
- Quality data is reviewed regularly

## Success Metrics

- 90% of inspections completed on time
- Defect rate reduced by 30% within 6 months
- First Pass Yield improved to >95%
- Rework costs reduced by 40%
- NCR closure time <7 days average
- CAPA on-time completion rate >90%
- Customer quality complaints reduced by 50%
- Cost of Quality tracked and trending down

## Risks & Mitigation

### Risk 1: User Adoption
**Risk**: Operators and inspectors may resist additional data entry  
**Mitigation**: 
- Simple, mobile-friendly interface
- Minimize required fields
- Show value (quality trends, recognition)
- Training and change management

### Risk 2: Data Quality
**Risk**: Incomplete or inaccurate quality data  
**Mitigation**:
- Required fields and validation
- Dropdown lists for consistency
- Photo evidence required for critical defects
- Regular data audits

### Risk 3: Integration Complexity
**Risk**: Complex integration with existing modules  
**Mitigation**:
- Phased rollout (start with inspections)
- Clear integration points defined
- Thorough testing

### Risk 4: Performance
**Risk**: Large volume of quality data may slow system  
**Mitigation**:
- Database indexing
- Pagination and filtering
- Archival of old data
- Performance testing
