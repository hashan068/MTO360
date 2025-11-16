"""
Integration tests for Enterprise MTO Sales Flow
Tests complete workflows from RFQ through Quotation to Sales Order
"""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient


class TestRFQToSalesOrderWorkflow:
    """Test complete RFQ to Sales Order workflow (Task 13.1)"""
    
    @pytest.mark.asyncio
    async def test_complete_rfq_to_sales_order_flow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """
        Test the complete workflow:
        1. Create RFQ with line items
        2. Convert RFQ to Quotation
        3. Verify quotation pre-population and RFQ link
        4. Update quotation status to accepted
        5. Convert quotation to Sales Order
        6. Verify sales order creation and document links
        """
        
        # Step 1: Create RFQ with line items
        rfq_data = {
            "status": "draft",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "description": "Test RFQ for integration test",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 10,
                    "unit_price": 100.00
                },
                {
                    "product_id": test_products[1].id,
                    "quantity": 5,
                    "unit_price": 200.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/rfqs",
            json=rfq_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        rfq = response.json()
        assert rfq["status"] == "draft"
        assert len(rfq["items"]) == 2
        rfq_id = rfq["id"]
        
        # Update RFQ status to sent
        response = await client.put(
            f"/api/sales/rfqs/{rfq_id}",
            json={"status": "sent"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 2: Convert RFQ to Quotation
        conversion_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "123 Test St, Test City"
        }
        
        response = await client.post(
            f"/api/sales/rfqs/{rfq_id}/convert",
            json=conversion_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        quotation = response.json()
        quotation_id = quotation["id"]
        
        # Step 3: Verify quotation pre-population and RFQ link
        assert quotation["rfq_id"] == rfq_id
        assert len(quotation["quotation_items"]) == 2
        assert quotation["quotation_items"][0]["quantity"] == 10
        assert quotation["quotation_items"][1]["quantity"] == 5
        assert quotation["status"] == "quotation"
        
        # Verify RFQ status updated to completed
        response = await client.get(
            f"/api/sales/rfqs/{rfq_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_rfq = response.json()
        assert updated_rfq["status"] == "completed"
        
        # Step 4: Update quotation status to accepted
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "accepted"},
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_quotation = response.json()
        assert updated_quotation["status"] == "accepted"
        
        # Step 5: Convert quotation to Sales Order
        response = await client.post(
            f"/api/sales/quotations/{quotation_id}/convert",
            headers=auth_headers
        )
        assert response.status_code == 201
        sales_order = response.json()
        sales_order_id = sales_order["id"]
        
        # Step 6: Verify sales order creation and document links
        assert sales_order["quotation_id"] == quotation_id
        assert sales_order["status"] == "pending"
        assert len(sales_order["order_items"]) == 2
        
        # Verify sales order has reference to quotation and RFQ
        response = await client.get(
            f"/api/sales/orders/{sales_order_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        full_sales_order = response.json()
        assert full_sales_order["quotation_id"] == quotation_id
        
        # Verify RFQ shows linked quotations
        response = await client.get(
            f"/api/sales/rfqs/{rfq_id}/quotations",
            headers=auth_headers
        )
        assert response.status_code == 200
        linked_quotations = response.json()
        assert len(linked_quotations) == 1
        assert linked_quotations[0]["id"] == quotation_id


class TestDirectQuotationWorkflow:
    """Test direct quotation to sales order workflow (Task 13.2)"""
    
    @pytest.mark.asyncio
    async def test_direct_quotation_to_sales_order(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """
        Test direct quotation workflow:
        1. Create quotation directly without RFQ
        2. Add line items and set customer information
        3. Update quotation status to accepted
        4. Convert quotation to Sales Order
        5. Verify sales order creation without RFQ reference
        """
        
        # Step 1-2: Create quotation directly with line items
        quotation_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "456 Direct St, Test City",
            "status": "quotation",
            "quotation_items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 15,
                    "unit_price": 100.00
                },
                {
                    "product_id": test_products[1].id,
                    "quantity": 8,
                    "unit_price": 200.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/quotations",
            json=quotation_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        quotation = response.json()
        quotation_id = quotation["id"]
        
        # Verify no RFQ link
        assert quotation.get("rfq_id") is None
        assert len(quotation["quotation_items"]) == 2
        
        # Step 3: Update quotation status to accepted
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "accepted"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 4: Convert quotation to Sales Order
        response = await client.post(
            f"/api/sales/quotations/{quotation_id}/convert",
            headers=auth_headers
        )
        assert response.status_code == 201
        sales_order = response.json()
        
        # Step 5: Verify sales order creation without RFQ reference
        assert sales_order["quotation_id"] == quotation_id
        assert sales_order["status"] == "pending"
        assert len(sales_order["order_items"]) == 2
        
        # Verify no RFQ reference in sales order
        response = await client.get(
            f"/api/sales/orders/{sales_order['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        full_sales_order = response.json()
        assert full_sales_order.get("rfq_reference") is None


class TestStatusTransitions:
    """Test status transition workflows (Task 13.3)"""
    
    @pytest.mark.asyncio
    async def test_rfq_status_transitions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
    ):
        """Test RFQ status transitions: draft → sent → completed"""
        
        # Create RFQ in draft status
        rfq_data = {
            "status": "draft",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "description": "Test RFQ",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 10,
                    "unit_price": 100.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/rfqs",
            json=rfq_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        rfq_id = response.json()["id"]
        
        # Transition: draft → sent
        response = await client.put(
            f"/api/sales/rfqs/{rfq_id}",
            json={"status": "sent"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "sent"
        
        # Note: completed status is set automatically when converting to quotation
        # Test invalid transition: sent → draft (should fail if implemented)
    
    @pytest.mark.asyncio
    async def test_quotation_status_transitions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Test Quotation status transitions"""
        
        # Create quotation
        quotation_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "Test Address",
            "status": "quotation",
            "quotation_items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 10,
                    "unit_price": 100.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/quotations",
            json=quotation_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        quotation_id = response.json()["id"]
        
        # Transition: quotation → quotation_sent
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "quotation_sent"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "quotation_sent"
        
        # Transition: quotation_sent → accepted
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "accepted"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        
        # Test invalid transition: accepted → rejected (should fail)
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "rejected"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]  # Should fail
    
    @pytest.mark.asyncio
    async def test_sales_order_status_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Test Sales Order status workflow"""
        
        # Create quotation and convert to sales order
        quotation_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "Test Address",
            "status": "accepted",
            "quotation_items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 10,
                    "unit_price": 100.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/quotations",
            json=quotation_data,
            headers=auth_headers
        )
        quotation_id = response.json()["id"]
        
        response = await client.post(
            f"/api/sales/quotations/{quotation_id}/convert",
            headers=auth_headers
        )
        assert response.status_code == 201
        sales_order_id = response.json()["id"]
        
        # Test status transitions
        statuses = ["confirmed", "processing", "in_production", "ready_for_delivery", "delivered"]
        
        for status in statuses:
            response = await client.put(
                f"/api/sales/orders/{sales_order_id}/status",
                json={"status": status},
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.json()["status"] == status
        
        # Verify delivered status prevents further changes
        response = await client.put(
            f"/api/sales/orders/{sales_order_id}/status",
            json={"status": "pending"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]  # Should fail
