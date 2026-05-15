"""Smart DB bootstrap for container startup.

Behavior:
- Fresh database (no alembic_version table): create schema from SQLAlchemy
  models via Base.metadata.create_all, then `alembic stamp head` so future
  startups follow the migration path.
- Existing database: `alembic upgrade head` to apply incremental migrations.

This reconciles the codebase's hybrid schema strategy (models as source of
truth + incremental Alembic deltas) so that container startup is deterministic
regardless of volume state.
"""
import asyncio
import subprocess
import sys

from sqlalchemy import text

from app.config.database import engine, init_db


async def _has_alembic_version() -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT to_regclass('public.alembic_version')"))
        return result.scalar() is not None


async def _run() -> int:
    if await _has_alembic_version():
        print("[bootstrap] alembic_version found — running 'alembic upgrade head'", flush=True)
        await engine.dispose()
        return subprocess.call(["alembic", "upgrade", "head"])

    print("[bootstrap] empty database — create_all + 'alembic stamp head'", flush=True)
    await init_db()
    await engine.dispose()
    return subprocess.call(["alembic", "stamp", "head"])


if __name__ == "__main__":
    sys.exit(asyncio.run(_run()))
