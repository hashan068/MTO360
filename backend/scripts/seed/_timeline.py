"""Time anchor + helpers for staggered seed data."""
from datetime import datetime, date, time, timedelta, timezone


TODAY: date = date(2026, 5, 15)
NOW: datetime = datetime.combine(TODAY, time(9, 0), tzinfo=timezone.utc)
HORIZON_PAST_DAYS = 90
HORIZON_FUTURE_DAYS = 30
WINDOW_START: date = TODAY - timedelta(days=HORIZON_PAST_DAYS)
WINDOW_END: date = TODAY + timedelta(days=HORIZON_FUTURE_DAYS)


def days_ago(n: int) -> datetime:
    return NOW - timedelta(days=n)


def days_ahead(n: int) -> datetime:
    return NOW + timedelta(days=n)


def date_ago(n: int) -> date:
    return TODAY - timedelta(days=n)


def date_ahead(n: int) -> date:
    return TODAY + timedelta(days=n)


def business_days(start: date, count: int) -> list[date]:
    """Return `count` consecutive business days starting at `start` (skipping Sat/Sun)."""
    out: list[date] = []
    cur = start
    while len(out) < count:
        if cur.weekday() < 5:
            out.append(cur)
        cur += timedelta(days=1)
    return out
