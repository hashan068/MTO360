import asyncio
import os
from httpx import AsyncClient, ASGITransport
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.middleware.auth import get_current_user_id
import uuid
from fastapi.exceptions import ResponseValidationError

# Configure test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Mock authentication
async def mock_get_current_user_id():
    return 1

app.dependency_overrides[get_current_user_id] = mock_get_current_user_id

async def test_work_center_crud():
    print("  Testing Work Center CRUD...")
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Work Center
        print("    Creating Work Center...")
        random_suffix = str(uuid.uuid4())[:8]
        wc_code = f"TEST-WC-{random_suffix}"
        try:
            response = await ac.post("/work-centers/", json={
                "name": f"Test Assembly Station {random_suffix}",
                "code": wc_code,
                "capacity_hours_per_day": 8.0,
                "is_active": True,
                "description": "Test Description"
            })
        except Exception as e:
            with open("exception_debug.txt", "w") as f:
                f.write(f"EXCEPTION TYPE: {type(e)}\n")
                f.write(f"EXCEPTION MODULE: {type(e).__module__}\n")
                f.write(f"EXCEPTION NAME: {type(e).__name__}\n")
                try:
                    import json
                    if hasattr(e, "errors"):
                        f.write(f"ERRORS: {json.dumps(e.errors(), default=str)}\n")
                except:
                    f.write("COULD NOT PRINT ERRORS\n")
            raise e
        if response.status_code != 201:
            print(f"    FAILED: {response.text}")
            return False
        
        data = response.json()
        if data["name"] != f"Test Assembly Station {random_suffix}": return False
        if data["code"] != wc_code: return False
        wc_id = data["id"]
        print("    Created Work Center ID:", wc_id)

        # 2. Get Work Center
        print("    Getting Work Center...")
        response = await ac.get(f"/work-centers/{wc_id}")
        if response.status_code != 200: return False
        if response.json()["id"] != wc_id: return False

        # 3. Update Work Center
        print("    Updating Work Center...")
        response = await ac.patch(f"/work-centers/{wc_id}", json={
            "name": "Updated Station"
        })
        if response.status_code != 200: return False
        if response.json()["name"] != "Updated Station": return False

        # 4. List Work Centers
        print("    Listing Work Centers...")
        response = await ac.get("/work-centers/")
        if response.status_code != 200: return False
        if len(response.json()) < 1: return False
        
        print("  ✅ Work Center CRUD Passed")
        return wc_id

async def test_operation_route_crud(wc_id):
    print("  Testing Operation Route CRUD...")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Operation Route
        print("    Creating Operation Route...")
        response = await ac.post("/operation-routes/", json={
            "name": "Test Route",
            "is_active": True,
            "route_operations": [
                {
                    "sequence": 1,
                    "name": "Op 1",
                    "work_center_id": wc_id,
                    "standard_time_minutes": 60,
                    "setup_time_minutes": 10
                }
            ]
        })
        if response.status_code != 201:
            print(f"    FAILED: {response.text}")
            return False
            
        data = response.json()
        if data["name"] != "Test Route": return False
        if len(data["route_operations"]) != 1: return False
        route_id = data["id"]
        print("    Created Route ID:", route_id)

        # 2. Get Route
        print("    Getting Route...")
        response = await ac.get(f"/operation-routes/{route_id}")
        if response.status_code != 200: return False
        if response.json()["id"] != route_id: return False

        # 3. Add Operation
        print("    Adding Operation to Route...")
        response = await ac.post(f"/operation-routes/{route_id}/operations", json={
            "sequence": 2,
            "name": "Op 2",
            "work_center_id": wc_id,
            "standard_time_minutes": 30
        })
        if response.status_code != 201: return False
        
        # Verify added operation
        response = await ac.get(f"/operation-routes/{route_id}")
        if len(response.json()["route_operations"]) != 2: return False
        
        print("  ✅ Operation Route CRUD Passed")
        return True

async def main():
    print("Starting API Verification...")
    wc_id = await test_work_center_crud()
    if wc_id:
        await test_operation_route_crud(wc_id)
    else:
        print("Skipping Route tests due to Work Center failure")

if __name__ == "__main__":
    asyncio.run(main())
