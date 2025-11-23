import asyncio
import os
from app.config.database import init_db

# Set env var for SQLite
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./db.sqlite3"

async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully.")

if __name__ == "__main__":
    asyncio.run(main())
