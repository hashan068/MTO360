"""
Integration tests for validation and error handling (Task 13.7)
"""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient


class TestValidationAndErrorHandling:
    """Test validation and error handling (Task 13.7)"""
    
    @pytest.mark.asyncio
    async def test_price_validation_positive_values(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
    ):
        """Test price validation requires positive values"""
        
        # Attempt to create RFQ with negative price
        rfq_data = {
            "status": "draft",
            "description": "Test RFQ",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 10,
                    "unit_price": -100.00  # Invalid negative price
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/rfqs",
            json=rfq_data,
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_quantity_validation_positive_values(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
    ):
        """Test quantity validation requires positive values"""
        
        # Attempt to create RFQ with zero quantity
        rfq_data = {
            "status": "draft",
            "description": "Test RFQ",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 0,  # Invalid zero quantity
                    "unit_price": 100.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/rfqs",
            json=rfq_data,
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_date_validation_expiration_after_creation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Test date validation: expiration after creation"""
        
        # Attempt to create quotation with expiration before creation
        quotation_data = {
            "customer_id": test_customer.id,
            "date": date.today().isoformat(),
            "expiration_date": (date.today() - timedelta(days=1)).isoformat(),  # Invalid
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
        # Should fail validation
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_customer_active_status_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
        db_session,
    ):
        """Test customer active status validation"""
        from app.models.customer import Customer
        
        # Create inactive customer
        inactive_customer = Customer(
            name="Inactive Customer",
            email="inactive@test.com",
            phone="123-456-7890",
            address="Test Address",
            is_active=False,
        )
        db_session.add(inactive_customer)
        await db_session.commit()
        await db_session.refresh(inactive_customer)
        
        # Attempt to create quotation with inactive customer
        quotation_data = {
            "customer_id": inactive_customer.id,
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
        # Should fail validation
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_duplicate_conversion_prevention(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_customer,
        test_products,
    ):
        """Test duplicate conversion prevention"""
        
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
        
        # First conversion should succeed
        response = await client.post(
            f"/api/sales/quotations/{quotation_id}/convert",
            headers=auth_headers
        )
        assert response.status_code == 201
        
        # Second conversion should fail
        response = await client.post(
            f"/api/sales/quotations/{quotation_id}/convert",
            headers=auth_headers
        )
        assert response.status_code in [400, 409, 422]
    
    @pytest.mark.asyncio
    async def test_user_friendly_error_messages(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_products,
    ):
        """Verify user-friendly error messages are displayed"""
        
        # Create invalid RFQ
        rfq_data = {
            "status": "draft",
            "description": "Test RFQ",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": -5,  # Invalid
                    "unit_price": 100.00
                }
            ]
        }
        
        response = await client.post(
            "/api/sales/rfqs",
            json=rfq_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]
        error_data = response.json()
        
        # Verify error message structure
        assert "detail" in error_data or "message" in error_data
        
        # Error message should be informative
        error_text = str(error_data)
        assert len(error_text) > 0
