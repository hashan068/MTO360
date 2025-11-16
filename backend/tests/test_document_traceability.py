"""
Integration tests for document traceability and navigation (Task 13.5)
"""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient


class TestDocumentTraceability:
    """Test document traceability and navigation (Task 13.5)"""
    
    @pytest.mark.asyncio
    async def test_rfq_shows_linked_quotations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Verify RFQ shows list of created quotations"""
        
        # Create RFQ
        rfq_data = {
            "status": "sent",
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
        rfq_id = response.json()["id"]
        
        # Convert to quotation
        conversion_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "Test Address"
        }
        
        response = await client.post(
            f"/api/sales/rfqs/{rfq_id}/convert",
            json=conversion_data,
            headers=auth_headers
        )
        quotation_id = response.json()["id"]
        
        # Verify RFQ shows linked quotations
        response = await client.get(
            f"/api/sales/rfqs/{rfq_id}/quotations",
            headers=auth_headers
        )
        assert response.status_code == 200
        quotations = response.json()
        assert len(quotations) >= 1
        assert any(q["id"] == quotation_id for q in quotations)
    
    @pytest.mark.asyncio
    async def test_quotation_shows_source_rfq_link(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Verify Quotation shows link to source RFQ"""
        
        # Create RFQ and convert to quotation
        rfq_data = {
            "status": "sent",
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
        rfq_id = response.json()["id"]
        
        conversion_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "Test Address"
        }
        
        response = await client.post(
            f"/api/sales/rfqs/{rfq_id}/convert",
            json=conversion_data,
            headers=auth_headers
        )
        quotation_id = response.json()["id"]
        
        # Verify quotation shows RFQ link
        response = await client.get(
            f"/api/sales/quotations/{quotation_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        quotation = response.json()
        assert quotation["rfq_id"] == rfq_id
    
    @pytest.mark.asyncio
    async def test_sales_order_shows_quotation_and_rfq_links(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Verify Sales Order shows links to quotation and RFQ"""
        
        # Create complete chain: RFQ → Quotation → Sales Order
        rfq_data = {
            "status": "sent",
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
        rfq_id = response.json()["id"]
        
        conversion_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
            "invoicing_and_shipping_address": "Test Address"
        }
        
        response = await client.post(
            f"/api/sales/rfqs/{rfq_id}/convert",
            json=conversion_data,
            headers=auth_headers
        )
        quotation_id = response.json()["id"]
        
        # Accept quotation
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "accepted"},
            headers=auth_headers
        )
        
        # Convert to sales order
        response = await client.post(
            f"/api/sales/quotations/{quotation_id}/convert",
            headers=auth_headers
        )
        sales_order_id = response.json()["id"]
        
        # Verify sales order shows both quotation and RFQ links
        response = await client.get(
            f"/api/sales/orders/{sales_order_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        sales_order = response.json()
        assert sales_order["quotation_id"] == quotation_id
        
        # Check if RFQ reference is available through quotation
        if "quotation_reference" in sales_order:
            assert sales_order["quotation_reference"]["rfq_id"] == rfq_id
