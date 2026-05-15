"""Top-level seed orchestrator — runs modules in topological order under one session."""
import time

from scripts.seed._session import AsyncSessionLocal
from scripts.seed import auth, catalog, manufacturing, notifications, procurement, quality, sales


async def run() -> int:
    print("[seed] starting MTO360 stress-profile seed")
    started = time.perf_counter()
    refs: dict = {}
    async with AsyncSessionLocal() as session:
        try:
            refs.update(await auth.seed(session, refs))
            refs.update(await catalog.seed(session, refs))
            refs.update(await sales.seed(session, refs))
            refs.update(await manufacturing.seed(session, refs))
            refs.update(await procurement.seed(session, refs))
            refs.update(await quality.seed(session, refs))
            refs.update(await notifications.seed(session, refs))
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    print(f"[seed] done in {time.perf_counter() - started:.1f}s")
    return 0
