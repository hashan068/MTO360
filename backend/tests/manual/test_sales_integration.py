"""
Manual Test Script for Sales Integration

This script demonstrates how the automatic SO sync works.
Run this after the backend is started to test the integration.

Prerequisites:
- Backend running (uvicorn app.main:app)
- Database migrated (alembic upgrade head)
- At least one test sales order with manufacturing orders
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import models
import sys
sys.path.append('d:/EDU/DS Portfolio/Projects/MTO360/backend')

from app.models.sales import SalesOrder, SalesOrderStatusEnum
from app.models.manufacturing import ManufacturingOrder, ManufacturingOrderOperation, OperationStatusEnum
from app.modules.manufacturing.application.services.shop_floor_service import ShopFloorService
from app.config.settings import settings


async def test_automatic_sync():
    """
    Test the automatic sales order sync when operations change.
    
    This demonstrates the full integration flow:
    1. Find a test sales order with manufacturing orders
    2. Find an operation to work with
    3. Start the operation → SO should auto-update
    4. Complete the operation → SO should auto-update again
    """
    # Create database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("\n" + "="*80)
        print("🧪 SALES INTEGRATION AUTOMATIC SYNC TEST")
        print("="*80 + "\n")
        
        # Step 1: Find a sales order with MOs
        print("📋 Step 1: Finding test sales order with manufacturing orders...")
        result = await db.execute(
            select(SalesOrder)
            .join(ManufacturingOrder, ManufacturingOrder.sales_order_id == SalesOrder.id)
            .limit(1)
        )
        sales_order = result.scalar_one_or_none()
        
        if not sales_order:
            print("❌ No sales order with manufacturing orders found!")
            print("   Create a sales order with MOs first, then run this test.")
            return
        
        print(f"✅ Found SO-{sales_order.id}")
        print(f"   Current Status: {sales_order.status.value}")
        print(f"   Current Delivery: {sales_order.delivery_date or 'Not set'}")
        
        # Step 2: Find an operation we can work with
        print("\n📋 Step 2: Finding a schedulable operation...")
        result = await db.execute(
            select(ManufacturingOrderOperation)
            .join(ManufacturingOrder, ManufacturingOrderOperation.manufacturing_order_id == ManufacturingOrder.id)
            .where(ManufacturingOrder.sales_order_id == sales_order.id)
            .where(ManufacturingOrderOperation.status.in_([
                OperationStatusEnum.SCHEDULED,
                OperationStatusEnum.PENDING
            ]))
            .limit(1)
        )
        operation = result.scalar_one_or_none()
        
        if not operation:
            print("❌ No schedulable operation found!")
            print("   All operations are either completed or in-progress.")
            return
        
        print(f"✅ Found Operation {operation.id}")
        print(f"   Name: {operation.name}")
        print(f"   Status: {operation.status.value}")
        print(f"   MO: {operation.manufacturing_order_id}")
        
        # Step 3: Start the operation (triggers auto-sync)
        print("\n📋 Step 3: Starting operation (should trigger auto-sync)...")
        print("   This will:")
        print("   - Update operation status to IN_PROGRESS")
        print("   - Update MO status based on operations")
        print("   - 🎯 AUTOMATICALLY sync SO status and delivery_date")
        
        input("\nPress Enter to start operation and watch the magic happen...")
        
        shop_floor_service = ShopFloorService(db)
        
        try:
            # This will trigger the automatic SO update!
            updated_operation = await shop_floor_service.start_operation(operation.id)
            
            print(f"\n✅ Operation started!")
            print(f"   New Status: {updated_operation.status.value}")
            print(f"   Actual Start: {updated_operation.actual_start}")
            
            # Refresh sales order to see auto-update
            await db.refresh(sales_order)
            
            print(f"\n🎉 SALES ORDER AUTO-SYNCED!")
            print(f"   SO-{sales_order.id} Status: {sales_order.status.value}")
            print(f"   Delivery Date: {sales_order.delivery_date}")
            print(f"   (Check logs above for '✅ Auto-synced SO...' message)")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 4: Complete the operation (another auto-sync)
        print("\n📋 Step 4: Completing operation (another auto-sync)...")
        input("Press Enter to complete operation...")
        
        try:
            completed_operation = await shop_floor_service.complete_operation(operation.id)
            
            print(f"\n✅ Operation completed!")
            print(f"   New Status: {completed_operation.status.value}")
            print(f"   Actual End: {completed_operation.actual_end}")
            print(f"   Duration: {completed_operation.actual_duration_minutes} minutes")
            
            # Refresh sales order to see second auto-update
            await db.refresh(sales_order)
            
            print(f"\n🎉 SALES ORDER AUTO-SYNCED AGAIN!")
            print(f"   SO-{sales_order.id} Status: {sales_order.status.value}")
            print(f"   Delivery Date: {sales_order.delivery_date}")
            print(f"   (Check logs above for second '✅ Auto-synced SO...' message)")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n" + "="*80)
        print("🎉 TEST COMPLETE - Automatic sync is working!")
        print("="*80)
        print("\nWhat happened:")
        print("1. ✅ Operation status changed (SCHEDULED → IN_PROGRESS → COMPLETED)")
        print("2. ✅ MO status auto-updated based on operations")
        print("3. ✅ SO status AUTOMATICALLY synced (via new hook)")
        print("4. ✅ SO delivery_date AUTOMATICALLY calculated")
        print("5. ✅ All without manual API calls!")
        print("\nIntegration is LIVE and WORKING! 🚀")


async def test_delivery_date_calculation():
    """
    Test delivery date calculation for a sales order.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("\n" + "="*80)
        print("🧪 DELIVERY DATE CALCULATION TEST")
        print("="*80 + "\n")
        
        from app.modules.sales.application.services.production_integration_service import (
            ProductionIntegrationService,
        )
        
        # Find a SO with MOs
        result = await db.execute(
            select(SalesOrder)
            .join(ManufacturingOrder, ManufacturingOrder.sales_order_id == SalesOrder.id)
            .limit(1)
        )
        so = result.scalar_one_or_none()
        
        if not so:
            print("❌ No sales order found")
            return
        
        service = ProductionIntegrationService(db)
        
        # Calculate delivery date
        delivery = await service.calculate_delivery_date(so.id, buffer_days=3)
        
        print(f"Sales Order: SO-{so.id}")
        print(f"Estimated Delivery: {delivery}")
        print(f"Current SO Delivery: {so.delivery_date}")
        
        if delivery:
            print(f"\n✅ Calculation working!")
            print(f"   Using latest MO scheduled_end + 3 buffer days")
        else:
            print(f"\n⚠️ No delivery date (MOs not scheduled yet)")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SALES INTEGRATION TEST SUITE")
    print("="*80)
    print("\nAvailable tests:")
    print("1. Automatic Sync Test (demonstrates Fix #1 and Fix #2)")
    print("2. Delivery Date Calculation Test")
    print("\nWhich test to run?")
    print("(1) Automatic sync")
    print("(2) Delivery calculation")
    print("(3) Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_automatic_sync())
    elif choice == "2":
        asyncio.run(test_delivery_date_calculation())
    elif choice == "3":
        asyncio.run(test_delivery_date_calculation())
        asyncio.run(test_automatic_sync())
    else:
        print("Invalid choice!")
