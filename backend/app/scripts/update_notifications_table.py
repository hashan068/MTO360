"""
Script to add new columns to notifications table
"""
import asyncio
from sqlalchemy import text
from app.config.database import engine


async def add_notification_columns():
    """Add production-specific columns to notifications table"""
    async with engine.begin() as conn:
        print("=" * 60)
        print("ADDING NOTIFICATION COLUMNS")
        print("=" * 60)
        print()
        
        # Check if columns already exist
        result = await conn.execute(text("PRAGMA table_info(notifications)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"Existing columns: {columns}")
        
        alterations = []
        
        if 'notification_type' not in columns:
            alterations.append("ALTER TABLE notifications ADD COLUMN notification_type VARCHAR(50) DEFAULT 'general' NOT NULL")
        
        if 'related_entity_type' not in columns:
            alterations.append("ALTER TABLE notifications ADD COLUMN related_entity_type VARCHAR(100)")
        
        if 'related_entity_id' not in columns:
            alterations.append("ALTER TABLE notifications ADD COLUMN related_entity_id INTEGER")
        
        if 'severity' not in columns:
            alterations.append("ALTER TABLE notifications ADD COLUMN severity VARCHAR(20) DEFAULT 'info' NOT NULL")
        
        if 'action_url' not in columns:
            alterations.append("ALTER TABLE notifications ADD COLUMN action_url VARCHAR(500)")
        
        if alterations:
            print(f"\nAdding {len(alterations)} new columns...")
            for sql in alterations:
                await conn.execute(text(sql))
                print(f"  ✓ {sql.split('ADD COLUMN')[1].split()[0]}")
            print("\n✅ Columns added successfully!")
        else:
            print("\n✓ All columns already exist")


if __name__ == "__main__":
    asyncio.run(add_notification_columns())
