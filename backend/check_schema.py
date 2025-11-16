"""Quick script to check database schema"""
import asyncio
from sqlalchemy import text
from app.config.database import engine


async def check_columns():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sales_orders' ORDER BY ordinal_position")
        )
        columns = [row[0] for row in result]
        print("Columns in sales_orders table:")
        for col in columns:
            print(f"  - {col}")
        
        if 'quotation_id' in columns:
            print("\n✓ quotation_id column EXISTS")
        else:
            print("\n✗ quotation_id column MISSING")
        
        if 'delivery_date' in columns:
            print("✓ delivery_date column EXISTS")
        else:
            print("✗ delivery_date column MISSING")


if __name__ == "__main__":
    asyncio.run(check_columns())
