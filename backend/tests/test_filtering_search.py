"""
Integration tests for filtering and search functionality (Task 13.6)
"""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient


class TestFilteringAndSearch:
    """Test filtering and search functionality (Task 13.6)"""
    
    @pytest.mark.asyncio
    async def test_rfq_status_filtering(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
    ):
        """Test status filtering on RFQ list page"""
        
        # Create RFQs with different statuses
        for status in ["draft", "sent"]:
            rfq_data = {
                "status": status,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "description": f"Test RFQ {status}",
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
        
        # Test filtering by status
        response = await client.get(
            "/api/sales/rfqs?status=draft",
            headers=auth_headers
        )
        assert response.status_code == 200
        rfqs = response.json()
        assert all(rfq["status"] == "draft" for rfq in rfqs)
    
    @pytest.mark.asyncio
    async def test_rfq_search_functionality(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
    ):
        """Test search functionality on RFQ list"""
        
        # Create RFQ with specific description
        rfq_data = {
            "status": "draft",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "description": "Unique Search Term XYZ123",
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
        
        # Test search
        response = await client.get(
            "/api/sales/rfqs?search=XYZ123",
            headers=auth_headers
        )
        assert response.status_code == 200
        rfqs = response.json()
        assert len(rfqs) >= 1
        assert any("XYZ123" in rfq.get("description", "") for rfq in rfqs)
    
    @pytest.mark.asyncio
    async def test_quotation_status_filtering(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Test status filtering on quotation list page"""
        
        # Create quotations with different statuses
        for status in ["quotation", "accepted"]:
            quotation_data = {
                "customer_id": test_customer.id,
                "date": date.today().isoformat(),
                "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
                "invoicing_and_shipping_address": "Test Address",
                "status": status,
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
        
        # Test filtering by status
        response = await client.get(
            "/api/sales/quotations?status=accepted",
            headers=auth_headers
        )
        assert response.status_code == 200
        quotations = response.json()
        assert all(q["status"] == "accepted" for q in quotations)
    
    @pytest.mark.asyncio
    async def test_sales_order_date_range_filtering(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Test date range filtering on sales orders"""
        
        # Create quotation and sales order
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
        
        # Test date range filtering
        start_date = (date.today() - timedelta(days=1)).isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        
        response = await client.get(
            f"/api/sales/orders?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) >= 1
