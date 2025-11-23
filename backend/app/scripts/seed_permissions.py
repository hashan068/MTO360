"""
Seed script to populate permissions and roles
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import AsyncSessionLocal
from app.models.permissions import Permission, Role
from app.seeds.permission_seeds import PRODUCTION_PERMISSIONS, DEFAULT_ROLES


async def seed_permissions_and_roles():
    """Seed permissions and roles into the database"""
    async with AsyncSessionLocal() as db:
        try:
            # Seed permissions
            print("Seeding permissions...")
            permission_map = {}  # Map permission code to Permission object
            
            for perm_data in PRODUCTION_PERMISSIONS:
                # Check if permission already exists
                query = select(Permission).where(Permission.code == perm_data["code"])
                result = await db.execute(query)
                existing_perm = result.scalar_one_or_none()
                
                if existing_perm:
                    print(f"  ✓ Permission '{perm_data['code']}' already exists")
                    permission_map[perm_data["code"]] = existing_perm
                else:
                    new_perm = Permission(**perm_data)
                    db.add(new_perm)
                    await db.flush()  # Flush to get the ID
                    permission_map[perm_data["code"]] = new_perm
                    print(f"  + Created permission '{perm_data['code']}'")
            
            await db.commit()
            print(f"✓ Seeded {len(PRODUCTION_PERMISSIONS)} permissions\n")
            
            # Seed roles
            print("Seeding roles...")
            for role_data in DEFAULT_ROLES:
                # Check if role already exists
                query = select(Role).where(Role.name == role_data["name"])
                result = await db.execute(query)
                existing_role = result.scalar_one_or_none()
                
                if existing_role:
                    print(f"  ✓ Role '{role_data['name']}' already exists")
                    # Update permissions if needed
                    existing_perms = {p.code for p in existing_role.permissions}
                    desired_perms = set(role_data["permissions"])
                    
                    if existing_perms != desired_perms:
                        # Update the role's permissions
                        existing_role.permissions = [
                            permission_map[code] for code in role_data["permissions"]
                        ]
                        print(f"    → Updated permissions for '{role_data['name']}'")
                else:
                    # Create new role
                    new_role = Role(
                        name=role_data["name"],
                        description=role_data["description"]
                    )
                    # Assign permissions
                    new_role.permissions = [
                        permission_map[code] for code in role_data["permissions"]
                    ]
                    db.add(new_role)
                    print(f"  + Created role '{role_data['name']}' with {len(role_data['permissions'])} permissions")
            
            await db.commit()
            print(f"✓ Seeded {len(DEFAULT_ROLES)} roles\n")
            
            print("✅ Permission and role seeding completed successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding permissions and roles: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("PERMISSION & ROLE SEEDING SCRIPT")
    print("=" * 60)
    print()
    
    asyncio.run(seed_permissions_and_roles())
