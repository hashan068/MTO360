"""
Script to create a test user in the database
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.config.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.middleware.auth import get_password_hash


async def create_user(username: str, password: str, email: str = None, is_superuser: bool = False):
    """Create a user in the database"""
    # Initialize database (create tables if they don't exist)
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User '{username}' already exists!")
            return existing_user
        
        # Create new user
        password_hash = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            is_active=True,
            is_superuser=is_superuser,
            is_staff=is_superuser,
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        print(f"✅ User '{username}' created successfully!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Is Superuser: {user.is_superuser}")
        return user


async def main():
    """Main function to create default test user"""
    # Create a default test user
    await create_user(
        username="admin",
        password="admin123",
        email="admin@mto360.com",
        is_superuser=True
    )


if __name__ == "__main__":
    asyncio.run(main())

