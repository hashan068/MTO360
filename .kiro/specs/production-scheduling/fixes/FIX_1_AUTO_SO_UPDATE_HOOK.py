"""
IMPLEMENTATION FIX #1: Automatic Sales Order Update Hook
File to modify: backend/app/modules/manufacturing/application/services/shop_floor_service.py
Location: After line 361 in update_mo_status_from_operations() method
Priority: HIGH
Estimated Time: 30 minutes
"""

# ADD THIS CODE after line 361 (after "return mo")
# Replace the current "return mo" with this enhanced version:

CODE_TO_INSERT = """
        # Notify sales module of status change if MO has a sales order
        if mo.sales_order_id:
            try:
                from app.modules.sales.application.services.production_integration_service import (
                    ProductionIntegrationService,
                )
                
                # Update sales order delivery date and status
                sales_integration = ProductionIntegrationService(self.db)
                await sales_integration.update_so_status_from_production(mo.sales_order_id)
                
                # Optional: Log successful sync
                print(f"✅ Synced SO {mo.sales_order_id} from MO {mo_id} status change")
                
            except Exception as e:
                # Log error but don't fail MO status update
                # This is a best-effort sync - MO operations are critical path
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Failed to update sales order {mo.sales_order_id} "
                    f"from MO {mo_id} status change: {e}",
                    exc_info=True
                )

        return mo
"""


"""
WHAT THIS DOES:
1. After updating MO status, checks if the MO is linked to a sales order
2. If linked, calls the ProductionIntegrationService to update:
   - Sales order delivery_date (based on latest production schedule)
   - Sales order status (based on production progress) - when Fix #2 is implemented
3. Catches exceptions to prevent MO updates from failing
4. Logs success/failure for debugging

TESTING:
1. Create a SO with MOs
2. Schedule operations for the MOs
3. Start an operation → Should see "Synced SO X..." in logs
4. Complete operation → SO delivery_date should update
5. Block operation → SO status should update (after Fix #2)

ROLLBACK:
If issues occur, simply remove this code block and return to "return mo"
"""
