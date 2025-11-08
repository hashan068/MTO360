"""
FastAPI dependencies
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    Alias for get_db for convenience
    """
    async for session in get_db():
        yield session

