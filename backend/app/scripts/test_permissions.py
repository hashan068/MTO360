"""
Test script for permissions and roles system
"""
import asyncio
from sqlalchemy import select
from app.config.database import AsyncSessionLocal
from app.models import Permission, Role, User
from app.middleware.permission_checker import get_user_permissions, check_user_permission


async def test_permissions():
    """Test the permissions system"""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("PERMISSIONS SYSTEM TEST")
        print("=" * 60)
        print()
        
        # 1. List all permissions
        print("1. Listing all permissions:")
        print("-" * 60)
        query = select(Permission).order_by(Permission.module, Permission.code)
        result = await db.execute(query)
        permissions = result.scalars().all()
        
        for perm in permissions:
            print(f"  [{perm.module}] {perm.code}: {perm.name}")
        print(f"\n✓ Total permissions: {len(permissions)}\n")
        
        # 2. List all roles with their permissions
        print("2. Listing all roles:")
        print("-" * 60)
        query = select(Role)
        result = await db.execute(query)
        roles = result.scalars().all()
        
        for role in roles:
            print(f"\n  Role: {role.name}")
            print(f"  Description: {role.description}")
            print(f"  Permissions ({len(role.permissions)}):")
            for perm in role.permissions:
                print(f"    - {perm.code}")
        print(f"\n✓ Total roles: {len(roles)}\n")
        
        # 3. Test user permissions
        print("3. Testing user permissions:")
        print("-" * 60)
        query = select(User).limit(1)
        result = await db.execute(query)
        test_user = result.scalar_one_or_none()
        
        if test_user:
            print(f"  Testing with user: {test_user.username} (ID: {test_user.id})")
            
            # Get user's permissions
            user_perms = await get_user_permissions(test_user.id, db)
            print(f"  User permissions: {user_perms}")
            
            # Test specific permission
            has_schedule = await check_user_permission(
                test_user.id, "production.schedule.create", db
            )
            print(f"  Has 'production.schedule.create': {has_schedule}")
            
            # Assign a role to test user if they don't have any
            if not test_user.roles:
                print("\n  User has no roles. Assigning 'Production Planner' role...")
                query = select(Role).where(Role.name == "Production Planner")
                result = await db.execute(query)
                planner_role = result.scalar_one_or_none()
                
                if planner_role:
                    test_user.roles.append(planner_role)
                    await db.commit()
                    print(f"  ✓ Assigned 'Production Planner' role to {test_user.username}")
                    
                    # Re-check permissions
                    user_perms = await get_user_permissions(test_user.id, db)
                    print(f"  Updated permissions: {list(user_perms)}")
        else:
            print("  No users found in database")
        
        print("\n" + "=" * 60)
        print("✅ PERMISSIONS SYSTEM TEST COMPLETED")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_permissions())
