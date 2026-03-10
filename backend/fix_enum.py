import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.config.database import engine

async def fix_enum():
    async with engine.begin() as conn:
        # Check if 'scheduled' exists
        result = await conn.execute(text("SELECT 1 FROM pg_enum WHERE enumlabel = 'scheduled' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'operationstatusenum')"))
        exists = result.scalar()
        
        if not exists:
            print("Adding 'scheduled' to operationstatusenum...")
            # PostgreSQL cannot run ALTER TYPE inside a transaction block usually, but with asyncpg/sqlalchemy begin() it might be tricky.
            # However, ALTER TYPE ADD VALUE cannot run inside a transaction block.
            # We need to use isolation_level="AUTOCOMMIT" or execute outside transaction.
            pass
        else:
            print("'scheduled' already exists in operationstatusenum.")

    # To run ALTER TYPE, we need a separate connection with autocommit
    if not exists:
        # Create a raw asyncpg connection or use engine with isolation level
        # Use engine.execution_options to set isolation level before connecting
        async with engine.execution_options(isolation_level="AUTOCOMMIT").connect() as conn:
             await conn.execute(text("ALTER TYPE operationstatusenum ADD VALUE 'scheduled'"))
             print("Added 'scheduled' successfully.")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(fix_enum())
    except Exception as e:
        print(f"Error: {e}")
