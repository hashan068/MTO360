import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.config.database import engine

async def check_tables():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print("Tables in PostgreSQL:", tables)
        
        check_list = ['inspection_points']
        for t in check_list:
            print(f"Table '{t}' exists: {t in tables}")
            
        # Check enum values
        result = await conn.execute(text("SELECT e.enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = 'operationstatusenum'"))
        enums = [row[0] for row in result]
        print("Enum 'operationstatusenum' values:", enums)

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_tables())
