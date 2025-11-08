"""
Inventory Module

Handles inventory management including components, suppliers,
purchase requisitions, and purchase orders.
"""
from .api.router import router

__all__ = ["router"]

