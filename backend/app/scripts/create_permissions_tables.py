"""
Create permissions and roles tables directly
"""
import asyncio
from sqlalchemy import inspect
from app.config.database import AsyncSessionLocal, engine
from app.models import Permission, Role, User


async def create_permissions_tables():
    """Create permissions and roles tables if they don't exist"""
    from app.models.base import Base
    
    async with engine.begin() as conn:
        # Check if tables exist
        def check_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
        
        existing_tables = await conn.run_sync(check_tables)
        
        print(f"Existing tables: {existing_tables}")
        
        if 'permissions' not in existing_tables or 'roles' not in existing_tables:
            print("Creating permissions and roles tables...")
            # Create only the new tables
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            print("✓ Tables created successfully")
        else:
            print("✓ Permissions and roles tables already exist")


if __name__ == "__main__":
    print("=" * 60)
    print("CREATE PERMISSIONS TABLES")
    print("=" * 60)
    print()
    
    asyncio.run(create_permissions_tables())
