"""
Add lead_time_days field to components table
"""
import asyncio
from sqlalchemy import text
from app.config.database import engine


async def add_component_fields():
    """Add production-related fields to components table"""
    async with engine.begin() as conn:
        print("=" * 60)
        print("ADDING COMPONENT FIELDS")
        print("=" * 60)
        print()
        
        # Check if columns already exist
        result = await conn.execute(text("PRAGMA table_info(components)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"Existing columns: {columns}")
        
        alterations = []
        
        # Rename quantity to quantity_on_hand for clarity
        if 'quantity' in columns and 'quantity_on_hand' not in columns:
            # SQLite doesn't support RENAME COLUMN easily, so we'll add new column
            # and copy data later if needed
            print("  Note: 'quantity' exists, adding 'quantity_on_hand' as alias")
        
        if 'quantity_on_hand' not in columns:
            alterations.append("ALTER TABLE components ADD COLUMN quantity_on_hand INTEGER DEFAULT 0 NOT NULL")
        
        if 'reorder_point' not in columns:
            alterations.append("ALTER TABLE components ADD COLUMN reorder_point INTEGER DEFAULT 0 NOT NULL")
        
        if 'lead_time_days' not in columns:
            alterations.append("ALTER TABLE components ADD COLUMN lead_time_days INTEGER DEFAULT 7")
        
        if 'unit' not in columns:
            # Rename unit_of_measure to unit if it doesn't exist
            alterations.append("ALTER TABLE components ADD COLUMN unit VARCHAR(20) DEFAULT 'pcs' NOT NULL")
        
        if 'code' not in columns:
            alterations.append("ALTER TABLE components ADD COLUMN code VARCHAR(50)")
        
        if alterations:
            print(f"\nAdding {len(alterations)} new columns...")
            for sql in alterations:
                await conn.execute(text(sql))
                print(f"  ✓ {sql.split('ADD COLUMN')[1].split()[0]}")
            
            # Copy quantity to quantity_on_hand if needed
            if 'quantity' in columns:
                print("\n  Copying 'quantity' values to 'quantity_on_hand'...")
                await conn.execute(text("UPDATE components SET quantity_on_hand = quantity WHERE quantity_on_hand = 0"))
            
            # Copy unit_of_measure to unit if needed
            if 'unit_of_measure' in columns:
                print("  Copying 'unit_of_measure' values to 'unit'...")
                await conn.execute(text("UPDATE components SET unit = unit_of_measure WHERE unit = 'pcs'"))
            
            print("\n✅ Columns added successfully!")
        else:
            print("\n✓ All columns already exist")


if __name__ == "__main__":
    asyncio.run(add_component_fields())
