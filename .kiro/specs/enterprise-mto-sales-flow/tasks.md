# Implementation Plan

- [x] 1. Database schema enhancements and migrations





  - Add foreign key columns for document linking (rfq_id in quotations, quotation_id in sales_orders)
  - Add delivery_date column to sales_orders table
  - Create database indexes for performance optimization
  - Write Alembic migration scripts with upgrade and downgrade functions
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 2. Backend: Enhance data models and schemas





  - [x] 2.1 Update SQLAlchemy models with new relationships


    - Add rfq_id foreign key and relationship to Quotation model
    - Add quotation_id foreign key and relationship to SalesOrder model
    - Add delivery_date field to SalesOrder model
    - Add bidirectional relationships (RFQ.quotations, Quotation.sales_orders)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 2.2 Create new Pydantic schemas for conversions and status updates


    - Create ConvertRFQToQuotationRequest schema
    - Create QuotationStatusUpdate schema
    - Create SalesOrderStatusUpdate schema
    - Add summary schemas (RFQSummary, QuotationSummary, SalesOrderSummary) for nested references
    - _Requirements: 3.1, 3.2, 6.1, 9.1_

  - [x] 2.3 Enhance existing response schemas with computed fields


    - Add is_expired computed field to QuotationResponse
    - Add can_edit computed field to QuotationResponse and SalesOrderResponse
    - Add rfq_reference, quotation_reference fields to response schemas
    - Add creator_name to RFQResponse
    - _Requirements: 5.4, 8.4, 12.1, 12.2, 12.3_

- [x] 3. Backend: Implement service layer business logic





  - [x] 3.1 Enhance RFQService with conversion and query methods


    - Implement convert_to_quotation() method to create quotation from RFQ
    - Implement get_rfq_quotations() method to retrieve linked quotations
    - Add status validation in update_rfq() method
    - Update get_rfqs() to support status filtering and search
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 1.2, 1.3_


  - [x] 3.2 Enhance QuotationService with conversion and status management

    - Implement convert_to_sales_order() method to create sales order from quotation
    - Implement update_quotation_status() method with validation
    - Implement check_expiration() method for expiration logic
    - Implement can_edit() method to check edit permissions based on status
    - Add duplicate conversion prevention logic
    - Update get_quotations() to support status filtering and search
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 6.1, 6.2, 6.3, 6.4, 6.5, 5.2_

  - [x] 3.3 Enhance SalesOrderService with status workflow management


    - Implement update_sales_order_status() method with workflow validation
    - Implement validate_status_transition() method for status rules
    - Implement cancel_sales_order() method with manufacturing order checks
    - Implement can_edit() method to check edit permissions based on status
    - Update get_sales_orders() to support status and date range filtering
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 8.2, 8.3_
-

- [x] 4. Backend: Create new API endpoints




  - [x] 4.1 Add RFQ conversion and query endpoints


    - Create POST /api/sales/rfqs/{id}/convert endpoint for RFQ to Quotation conversion
    - Create GET /api/sales/rfqs/{id}/quotations endpoint to list linked quotations
    - Update GET /api/sales/rfqs endpoint to support filtering and search query parameters
    - _Requirements: 3.1, 3.2, 11.5, 1.2, 1.3_

  - [x] 4.2 Add Quotation conversion and status endpoints


    - Create POST /api/sales/quotations/{id}/convert endpoint for Quotation to Sales Order conversion
    - Create PUT /api/sales/quotations/{id}/status endpoint for status updates
    - Update GET /api/sales/quotations endpoint to support filtering and search query parameters
    - _Requirements: 7.1, 7.2, 6.1, 5.2_

  - [x] 4.3 Add Sales Order status management endpoints


    - Create PUT /api/sales/orders/{id}/status endpoint for status updates
    - Update GET /api/sales/orders endpoint to support status, date range, and search filtering
    - _Requirements: 9.1, 9.2, 8.2, 8.3_
-

- [x] 5. Backend: Implement error handling and validation




  - [x] 5.1 Create custom exception classes

    - Create InvalidStatusTransitionError exception
    - Create DocumentLockedException exception
    - Create DuplicateConversionError exception
    - Create ValidationError exception
    - _Requirements: 12.4, 7.5, 6.3_

  - [x] 5.2 Add validation logic in service methods


    - Validate status transitions in update methods
    - Validate edit permissions before updates
    - Validate business rules (positive prices, quantities, date ranges)
    - Validate customer active status before document creation
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 12.1, 12.2, 12.3_

  - [x] 5.3 Add error handling in API endpoints


    - Map service exceptions to HTTP status codes
    - Return user-friendly error messages
    - Log errors with context for debugging
    - _Requirements: 12.4_

- [x] 6. Frontend: Create TypeScript types and API client functions





  - [x] 6.1 Define TypeScript types for enhanced models


    - Create RFQ, RFQItem, RFQStatus types
    - Create Quotation, QuotationItem, QuotationStatus types with new fields
    - Create SalesOrder, SalesOrderItem, SalesOrderStatus types with new fields
    - Create summary types (RFQSummary, QuotationSummary, SalesOrderSummary)
    - _Requirements: 1.1, 5.1, 8.1_

  - [x] 6.2 Implement API client functions


    - Add convertRFQToQuotation() function
    - Add updateQuotationStatus() function
    - Add convertQuotationToSalesOrder() function
    - Add updateSalesOrderStatus() function
    - Add getRFQQuotations() function
    - Update list functions to support filtering parameters
    - _Requirements: 3.1, 6.1, 7.1, 9.1, 11.5, 1.2, 5.2, 8.2_

- [x] 7. Frontend: Create reusable components





  - [x] 7.1 Create StatusBadge component


    - Display status with appropriate color coding
    - Support all status types (RFQ, Quotation, Sales Order)
    - Show expired indicator for quotations
    - _Requirements: 1.1, 5.1, 5.4, 8.1_

  - [x] 7.2 Create DocumentLink component


    - Display clickable links to related documents
    - Show document type and ID
    - Navigate to detail page on click
    - _Requirements: 11.3, 11.4, 13.3_

  - [x] 7.3 Create LineItemsTable component


    - Display line items in a table format
    - Show product name, quantity, unit price, subtotal
    - Calculate and display total amount
    - Support read-only and editable modes
    - _Requirements: 1.4, 5.3, 8.5_

- [x] 8. Frontend: Implement RFQ pages and functionality




  - [x] 8.1 Enhance RfqsPage with list view features


    - Add status filter dropdown
    - Add search input for RFQ number, description
    - Display RFQ list with columns: ID, creator, status, due date, created date
    - Add "Create RFQ" button
    - Add row click navigation to detail page
    - _Requirements: 1.1, 1.2, 1.3, 15.1, 15.2_

  - [x] 8.2 Create RfqDetailPage for viewing and editing


    - Display RFQ header information (ID, creator, status, dates)
    - Display line items table with product details
    - Show "Create Quotation" button when status allows
    - Show list of linked quotations with navigation links
    - Implement RFQ editing with status-based restrictions
    - _Requirements: 1.4, 1.5, 3.1, 11.5, 13.1_

  - [x] 8.3 Create RfqForm component for creation and editing


    - Add form fields: due date, description
    - Add dynamic line items section with add/remove functionality
    - Validate at least one line item exists
    - Validate quantities and prices are positive
    - Handle form submission and error display
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 14.1, 14.2_
-

- [x] 9. Frontend: Enhance Quotation pages and functionality



  - [x] 9.1 Enhance QuotationsPage with improved list view


    - Add status filter dropdown
    - Add search input for quotation number, customer name
    - Display quotation list with columns: ID, customer, date, expiration, total, status
    - Show expired indicator for past expiration dates
    - Add "Create Quotation" button for direct creation
    - Add row click navigation to detail page
    - _Requirements: 5.1, 5.2, 4.1, 15.1, 15.2_

  - [x] 9.2 Create QuotationDetailPage for viewing and managing


    - Display quotation header with customer info, dates, status
    - Display line items table with pricing
    - Show source RFQ link if created from RFQ
    - Show linked sales orders if any exist
    - Add status update dropdown with validation
    - Add "Create Sales Order" button when status is accepted
    - Implement edit restrictions based on status
    - _Requirements: 5.3, 5.5, 11.3, 11.4, 6.1, 6.2, 7.1, 12.1, 13.2_

  - [x] 9.3 Enhance QuotationForm component for creation workflows


    - Support both direct creation and RFQ conversion modes
    - Pre-populate form when converting from RFQ
    - Add customer selection, dates, address fields
    - Add dynamic line items section
    - Validate expiration date is after quotation date
    - Calculate and display total amount
    - Handle form submission for both creation modes
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 3.2, 3.3, 14.3, 14.5_
-

- [x] 10. Frontend: Enhance Sales Order pages and functionality



  - [x] 10.1 Enhance SalesOrdersPage with filtering and search


    - Add status filter dropdown
    - Add date range picker for filtering by creation date
    - Add search input for order number, customer name
    - Display sales order list with columns: ID, customer, date, total, status
    - Add row click navigation to detail page
    - _Requirements: 8.1, 8.2, 8.3, 15.1, 15.2, 15.3_

  - [x] 10.2 Create SalesOrderDetailPage for viewing and status management


    - Display sales order header with customer info, dates, status
    - Display line items table with product details and pricing
    - Show source quotation link if created from quotation
    - Show source RFQ link if quotation was from RFQ
    - Add status update dropdown with workflow validation
    - Show delivery date when status is delivered
    - Display manufacturing order status for each line item
    - Implement edit restrictions based on status
    - _Requirements: 8.4, 8.5, 11.4, 9.1, 9.4, 9.5, 12.2, 12.3, 13.2_

  - [x] 10.3 Implement sales order creation from quotation


    - Create conversion flow triggered from QuotationDetailPage
    - Pre-populate sales order with quotation data
    - Set initial status to pending
    - Link to source quotation
    - Navigate to new sales order detail page after creation
    - _Requirements: 7.2, 7.3, 7.4, 13.4_

- [x] 11. Frontend: Implement navigation and workflow integration




  - [x] 11.1 Update routing configuration


    - Add route for /sales/rfqs/:id (RfqDetailPage)
    - Add route for /sales/quotations/:id (QuotationDetailPage)
    - Add route for /sales/orders/:id (SalesOrderDetailPage)
    - _Requirements: 13.3_

  - [x] 11.2 Implement breadcrumb navigation


    - Show document hierarchy (RFQ → Quotation → Sales Order)
    - Display breadcrumbs on detail pages
    - Make breadcrumb items clickable for navigation
    - _Requirements: 13.5_

  - [x] 11.3 Add action buttons with conditional visibility



    - Show "Create Quotation" on RFQ detail when status allows
    - Show "Create Sales Order" on Quotation detail when status is accepted
    - Show status update controls based on current status
    - Disable edit actions when document is locked
    - _Requirements: 13.1, 13.2, 1.5, 5.5_

- [x] 12. Frontend: Implement data fetching hooks





  - [x] 12.1 Create useRfqs hook


    - Fetch RFQ list with filtering and search
    - Fetch single RFQ with items and quotations
    - Handle loading and error states
    - Implement cache invalidation on mutations
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 12.2 Create useQuotations hook




    - Fetch quotation list with filtering and search
    - Fetch single quotation with items and references
    - Handle loading and error states
    - Implement optimistic updates for status changes
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 12.3 Create useSalesOrders hook


    - Fetch sales order list with filtering and search
    - Fetch single sales order with items and references
    - Handle loading and error states
    - Implement optimistic updates for status changes
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

-

- [x] 13. Integration and workflow testing






  - [x] 13.1 Test complete RFQ to Sales Order workflow


    - Create RFQ with line items
    - Convert RFQ to Quotation
    - Verify quotation pre-population and RFQ link
    - Update quotation status to accepted
    - Convert quotation to Sales Order
    - Verify sales order creation and document links
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 7.1, 7.2, 7.3, 7.4, 11.1, 11.2, 11.3, 11.4_

  - [x] 13.2 Test direct quotation to sales order workflow

    - Create quotation directly without RFQ
    - Add line items and set customer information
    - Update quotation status to accepted
    - Convert quotation to Sales Order
    - Verify sales order creation without RFQ reference
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2, 7.3_

  - [x] 13.3 Test status transition workflows

    - Test RFQ status transitions (draft → sent → completed)
    - Test Quotation status transitions (quotation → quotation_sent → accepted/rejected)
    - Test Sales Order status workflow (pending → confirmed → processing → in_production → ready_for_delivery → delivered)
    - Verify invalid transitions are prevented
    - _Requirements: 2.5, 6.1, 6.2, 6.3, 6.4, 6.5, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 13.4 Test edit restrictions and document locking

    - Verify quotations cannot be edited after accepted status
    - Verify sales orders cannot be edited after confirmed status
    - Verify appropriate error messages are displayed
    - Test administrator override capabilities
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [x] 13.5 Test document traceability and navigation

    - Verify RFQ shows list of created quotations
    - Verify Quotation shows link to source RFQ
    - Verify Sales Order shows links to quotation and RFQ
    - Test navigation between linked documents
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.3_

  - [x] 13.6 Test filtering and search functionality

    - Test status filtering on all list pages
    - Test search functionality across document numbers and customer names
    - Test date range filtering on sales orders
    - Test filter persistence within session
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 13.7 Test validation and error handling

    - Test price and quantity validation (positive values)
    - Test date validation (expiration after creation)
    - Test customer active status validation
    - Test duplicate conversion prevention
    - Verify user-friendly error messages are displayed
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 7.5_
