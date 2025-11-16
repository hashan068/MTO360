# Integration Test Guide for Enterprise MTO Sales Flow

This document provides a comprehensive guide for manually testing the complete Enterprise MTO Sales Flow implementation.

## Prerequisites

1. Backend server running (`python -m uvicorn app.main:app --reload`)
2. Frontend development server running (`npm run dev`)
3. Database initialized with test data (customers, products)
4. Authenticated user session

## Test 13.1: Complete RFQ to Sales Order Workflow

### Objective
Test the complete workflow from RFQ creation through Quotation to Sales Order.

### Steps

1. **Create RFQ with line items**
   - Navigate to RFQs page
   - Click "Create RFQ" button
   - Fill in:
     - Due date: 7 days from now
     - Description: "Test RFQ for integration test"
     - Add 2 line items with different products
   - Save as "draft" status
   - **Verify**: RFQ is created with status "draft"

2. **Update RFQ status to sent**
   - Open the created RFQ
   - Change status to "sent"
   - **Verify**: Status updates successfully

3. **Convert RFQ to Quotation**
   - Click "Create Quotation" button on RFQ detail page
   - **Verify**: Quotation form is pre-populated with:
     - All line items from RFQ
     - Correct quantities and prices
   - Fill in customer information and dates
   - Save quotation
   - **Verify**: 
     - Quotation is created with rfq_id link
     - RFQ status changes to "completed"
     - RFQ shows link to created quotation

4. **Update quotation status to accepted**
   - Open the created quotation
   - Change status to "accepted"
   - **Verify**: Status updates successfully
   - **Verify**: "Create Sales Order" button appears

5. **Convert quotation to Sales Order**
   - Click "Create Sales Order" button
   - **Verify**: Sales order is created with:
     - All line items from quotation
     - Status "pending"
     - Link to source quotation
     - Indirect link to source RFQ

6. **Verify document links**
   - From Sales Order: Click quotation link → should navigate to quotation
   - From Quotation: Click RFQ link → should navigate to RFQ
   - From RFQ: View quotations list → should show created quotation

### Expected Results
✅ Complete workflow from RFQ → Quotation → Sales Order works seamlessly
✅ All document links are properly maintained
✅ Status transitions occur automatically where appropriate

---

## Test 13.2: Direct Quotation to Sales Order Workflow

### Objective
Test creating a quotation directly without an RFQ.

### Steps

1. **Create quotation directly**
   - Navigate to Quotations page
   - Click "Create Quotation" button
   - Fill in all required fields:
     - Customer selection
     - Quotation date and expiration date
     - Shipping address
     - Add 2 line items
   - Save quotation
   - **Verify**: Quotation is created without rfq_id

2. **Update quotation status to accepted**
   - Change status to "accepted"
   - **Verify**: Status updates successfully

3. **Convert to Sales Order**
   - Click "Create Sales Order" button
   - **Verify**: Sales order is created with:
     - All line items from quotation
     - Link to quotation
     - No RFQ reference

### Expected Results
✅ Direct quotation creation works without RFQ
✅ Sales order creation from direct quotation works
✅ No RFQ reference in sales order

---

## Test 13.3: Status Transition Workflows

### Objective
Test all status transitions for RFQs, Quotations, and Sales Orders.

### RFQ Status Transitions

1. Create RFQ in "draft" status
2. Update to "sent" → **Verify**: Success
3. Attempt to update back to "draft" → **Verify**: Should fail (if validation exists)
4. Convert to quotation → **Verify**: Status changes to "completed"

### Quotation Status Transitions

1. Create quotation in "quotation" status
2. Update to "quotation_sent" → **Verify**: Success
3. Update to "accepted" → **Verify**: Success
4. Attempt to update to "rejected" → **Verify**: Should fail (invalid transition from accepted)

### Sales Order Status Workflow

1. Create sales order (status "pending")
2. Update to "confirmed" → **Verify**: Success
3. Update to "processing" → **Verify**: Success
4. Update to "in_production" → **Verify**: Success
5. Update to "ready_for_delivery" → **Verify**: Success
6. Update to "delivered" → **Verify**: Success
7. Attempt to change status after "delivered" → **Verify**: Should fail

### Expected Results
✅ Valid status transitions work correctly
✅ Invalid transitions are prevented
✅ Status workflow is enforced

---

## Test 13.4: Edit Restrictions and Document Locking

### Objective
Test that documents cannot be edited after certain status transitions.

### Quotation Locking

1. Create quotation in "quotation" status
2. **Verify**: can_edit = true, edit button enabled
3. Update status to "accepted"
4. **Verify**: can_edit = false, edit button disabled
5. Attempt to edit quotation → **Verify**: Error message displayed

### Sales Order Locking

1. Create sales order in "pending" status
2. **Verify**: can_edit = true
3. Update status to "confirmed"
4. **Verify**: can_edit = false
5. Attempt to edit sales order → **Verify**: Error message displayed

### Expected Results
✅ Documents are locked after appropriate status transitions
✅ UI reflects locked state (disabled buttons)
✅ API returns appropriate error messages

---

## Test 13.5: Document Traceability and Navigation

### Objective
Test that all document links work correctly and navigation is seamless.

### Steps

1. **Create complete document chain**
   - Create RFQ → Convert to Quotation → Convert to Sales Order

2. **Test RFQ navigation**
   - Open RFQ detail page
   - **Verify**: Shows list of linked quotations
   - Click quotation link → **Verify**: Navigates to quotation

3. **Test Quotation navigation**
   - Open quotation detail page
   - **Verify**: Shows link to source RFQ
   - Click RFQ link → **Verify**: Navigates to RFQ
   - **Verify**: Shows list of linked sales orders
   - Click sales order link → **Verify**: Navigates to sales order

4. **Test Sales Order navigation**
   - Open sales order detail page
   - **Verify**: Shows link to source quotation
   - Click quotation link → **Verify**: Navigates to quotation
   - **Verify**: Shows indirect link to RFQ (through quotation)

5. **Test breadcrumb navigation**
   - **Verify**: Breadcrumbs show document hierarchy
   - Click breadcrumb items → **Verify**: Navigation works

### Expected Results
✅ All document links are present and functional
✅ Navigation between documents is seamless
✅ Document hierarchy is clear

---

## Test 13.6: Filtering and Search Functionality

### Objective
Test filtering and search capabilities on all list pages.

### RFQ Filtering and Search

1. Create multiple RFQs with different statuses
2. Apply status filter → **Verify**: Only matching RFQs shown
3. Enter search term in description → **Verify**: Filtered results
4. Clear filters → **Verify**: All RFQs shown

### Quotation Filtering and Search

1. Create multiple quotations with different statuses
2. Apply status filter → **Verify**: Only matching quotations shown
3. Search by customer name → **Verify**: Filtered results
4. Test expired indicator → **Verify**: Shows for past expiration dates

### Sales Order Filtering

1. Create multiple sales orders
2. Apply status filter → **Verify**: Only matching orders shown
3. Apply date range filter → **Verify**: Only orders in range shown
4. Search by customer name → **Verify**: Filtered results

### Expected Results
✅ Status filtering works on all pages
✅ Search functionality works correctly
✅ Date range filtering works for sales orders
✅ Filters can be combined

---

## Test 13.7: Validation and Error Handling

### Objective
Test that all validation rules are enforced and error messages are user-friendly.

### Price and Quantity Validation

1. Attempt to create RFQ with negative price → **Verify**: Error message
2. Attempt to create RFQ with zero quantity → **Verify**: Error message
3. Attempt to create RFQ with negative quantity → **Verify**: Error message

### Date Validation

1. Attempt to create quotation with expiration before creation date → **Verify**: Error message
2. **Verify**: Error message is clear and user-friendly

### Customer Active Status

1. Create inactive customer
2. Attempt to create quotation with inactive customer → **Verify**: Error message

### Duplicate Conversion Prevention

1. Create quotation and convert to sales order
2. Attempt to convert same quotation again → **Verify**: Error message
3. **Verify**: Error message indicates duplicate conversion

### Error Message Quality

1. For each validation error:
   - **Verify**: Error message is displayed
   - **Verify**: Message is user-friendly (not technical)
   - **Verify**: Message indicates what needs to be fixed

### Expected Results
✅ All validation rules are enforced
✅ Error messages are clear and helpful
✅ Duplicate conversions are prevented
✅ Business rules are validated

---

## Summary Checklist

After completing all tests, verify:

- [ ] Complete RFQ to Sales Order workflow works end-to-end
- [ ] Direct quotation workflow works without RFQ
- [ ] All status transitions are properly validated
- [ ] Document locking prevents unauthorized edits
- [ ] Document traceability and navigation work correctly
- [ ] Filtering and search work on all list pages
- [ ] All validation rules are enforced
- [ ] Error messages are user-friendly
- [ ] No console errors during testing
- [ ] Performance is acceptable for all operations

## Notes

- These tests should be performed in a test environment, not production
- Document any bugs or issues found during testing
- Take screenshots of any unexpected behavior
- Test with different user roles if applicable
- Verify mobile responsiveness if required
