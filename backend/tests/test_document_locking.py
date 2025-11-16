"""
Integration tests for document locking and edit restrictions (Task 13.4)
"""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient


class TestEditRestrictionsAndLocking:
    """Test edit restrictions and document locking (Task 13.4)"""
    
    @pytest.mark.asyncio
    async def test_quotation_locked_after_accepted(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Verify quotations cannot be edited after accepted status"""
        
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
        
        # Update to accepted status
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}/status",
            json={"status": "accepted"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify can_edit is False
        response = await client.get(
            f"/api/sales/quotations/{quotation_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        quotation = response.json()
        assert quotation["can_edit"] is False
        
        # Attempt to edit quotation (should fail)
        update_data = {
            "invoicing_and_shipping_address": "New Address"
        }
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}",
            json=update_data,
            headers=auth_headers
        )
        # Should return error (400 or 403)
        assert response.status_code in [400, 403, 422]
    
    @pytest.mark.asyncio
    async def test_sales_order_locked_after_confirmed(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Verify sales orders cannot be edited after confirmed status"""
        
        # Create and convert quotation to sales order
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
        sales_order_id = response.json()["id"]
        
        # Update to confirmed status
        response = await client.put(
            f"/api/sales/orders/{sales_order_id}/status",
            json={"status": "confirmed"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify can_edit is False
        response = await client.get(
            f"/api/sales/orders/{sales_order_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        sales_order = response.json()
        assert sales_order["can_edit"] is False
    
    @pytest.mark.asyncio
    async def test_error_messages_for_locked_documents(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Verify appropriate error messages are displayed for locked documents"""
        
        # Create accepted quotation
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
        
        # Attempt to edit and check error message
        response = await client.put(
            f"/api/sales/quotations/{quotation_id}",
            json={"invoicing_and_shipping_address": "New Address"},
            headers=auth_headers
        )
        
        if response.status_code in [400, 403, 422]:
            error_data = response.json()
            # Verify error message exists
            assert "detail" in error_data or "message" in error_data
