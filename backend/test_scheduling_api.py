"""
API Verification Script for Phase 2: Scheduling Logic

This script tests the scheduling endpoints to verify they work correctly.
Run after starting the backend server.
"""
import httpx
import asyncio
from datetime import datetime, timedelta, date
import uuid


# Base URL
BASE_URL = "http://localhost:8000/api/manufacturing"


# Mock authentication by overriding the dependency
def mock_get_current_user_id():
    return 1


async def test_scheduling_endpoints():
    """Test scheduling API endpoints"""
    
    print("\n" + "="*60)
    print("PHASE 2: SCHEDULING LOGIC - API VERIFICATION")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Query Capacity
        print("TEST 1: Query Work Center Capacity")
        print("-" * 60)
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=7)
            
            response = await client.get(
                f"{BASE_URL}/schedule/capacity",
                params={
                    "work_center_id": 1,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                capacity_data = response.json()
                print(f"✓ Retrieved capacity for {len(capacity_data)} days")
                if capacity_data:
                    first_day = capacity_data[0]
                    print(f"  Example: {first_day['date']}")
                    print(f"    Capacity: {first_day['capacity_minutes']} min")
                    print(f"    Scheduled: {first_day['scheduled_minutes']} min")
                    print(f"    Available: {first_day['available_minutes']} min")
                    print(f"    Utilization: {first_day['utilization_pct']}%")
            else:
                print(f"✗ Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {e}")
        
        print()
        
        # Test 2: Check for Conflicts
        print("TEST 2: Detect Scheduling Conflicts")
        print("-" * 60)
        try:
            start_time = datetime.now() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            response = await client.get(
                f"{BASE_URL}/schedule/conflicts",
                params={
                    "work_center_id": 1,
                    "start_datetime": start_time.isoformat(),
                    "end_datetime": end_time.isoformat()
                }
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                conflicts = response.json()
                print(f"✓ Found {len(conflicts)} conflicting operations")
                if conflicts:
                    for conflict in conflicts[:3]:  # Show first 3
                        print(f"  - Op {conflict['operation_id']}: {conflict['operation_name']}")
                        print(f"    {conflict['scheduled_start']} to {conflict['scheduled_end']}")
            else:
                print(f"✗ Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception: {e}")
        
        print()
        
        # Test 3: Generate Operations (would need actual MO)
        print("TEST 3: Generate Operations for MO")
        print("-" * 60)
        print("⚠ Skipping - requires existing MO with route")
        print("  Example usage:")
        print("  POST /api/manufacturing/schedule/generate-operations/1")
        
        print()
        
        # Test 4: Auto-Schedule (would need actual MO with operations)
        print("TEST 4: Auto-Schedule MO")
        print("-" * 60)
        print("⚠ Skipping - requires existing MO with operations")
        print("  Example usage:")
        print("  POST /api/manufacturing/schedule/auto-schedule")
        print("  Body: { \"mo_id\": 1 }")
        
        print()
        
        # Test 5: Reschedule Operation (would need actual operation)
        print("TEST 5: Reschedule Operation")
        print("-" * 60)
        print("⚠ Skipping - requires existing scheduled operation")
        print("  Example usage:")
        print("  POST /api/manufacturing/schedule/reschedule")
        print("  Body: { \"operation_id\": 1, \"new_start_datetime\": \"2025-01-15T10:00:00\" }")
        
        print()
    
    print("="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    print("\nNOTE: Full testing requires:")
    print("  1. Work centers created in database")
    print("  2. Products with operation routes defined")
    print("  3. Manufacturing orders created")
    print("\nRun manual tests via Postman or curl for complete coverage.")


async def test_end_to_end_workflow():
    """
    End-to-end test workflow (conceptual - requires actual data)
    
    1. Create work centers
    2. Create product with BOM
    3. Create operation route for product
    4. Create manufacturing order
    5. Generate operations from route
    6. Auto-schedule the MO
    7. Query capacity to verify scheduling
    8. Reschedule an operation
    9. Verify no conflicts
    """
    print("\n" + "="*60)
    print("END-TO-END WORKFLOW (Conceptual)")
    print("="*60 + "\n")
    
    print("Step 1: Create Work Centers")
    print("  POST /api/manufacturing/work-centers")
    print("  - Assembly Station (8 hrs/day capacity)")
    print("  - Testing Bay (8 hrs/day capacity)")
    print()
    
    print("Step 2: Create Product and BOM")
    print("  POST /api/inventory/products")
    print("  POST /api/manufacturing/bom")
    print()
    
    print("Step 3: Create Operation Route")
    print("  POST /api/manufacturing/operation-routes")
    print("  Operations:")
    print("    1. PCB Assembly (45 min)")
    print("    2. Testing (30 min)")
    print()
    
    print("Step 4: Create Manufacturing Order")
    print("  POST /api/manufacturing/manufacturing-orders")
    print("  - Quantity: 5")
    print()
    
    print("Step 5: Generate Operations")
    print("  POST /api/manufacturing/schedule/generate-operations/{mo_id}")
    print("  → Creates 2 operations in PENDING status")
    print()
    
    print("Step 6: Auto-Schedule")
    print("  POST /api/manufacturing/schedule/auto-schedule")
    print("  → Finds available slots")
    print("  → Schedules operations sequentially")
    print("  → Updates MO with schedule")
    print()
    
    print("Step 7: Verify Capacity")
    print("  GET /api/manufacturing/schedule/capacity")
    print("  → Shows utilization increased")
    print()
    
    print("Step 8: Reschedule (if needed)")
    print("  POST /api/manufacturing/schedule/reschedule")
    print("  → Moves operation to new time")
    print("  → Updates capacity tracking")
    print()
    
    print("="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)


if __name__ == "__main__":
    print("\nPhase 2: Scheduling Logic - API Verification")
    print("=" * 60)
    print("\nRunning basic API tests...")
    
    try:
        asyncio.run(test_scheduling_endpoints())
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        print("\nMake sure the backend server is running:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
    
    print("\n" + "="*60)
    print("\nShowing end-to-end workflow...")
    asyncio.run(test_end_to_end_workflow())
