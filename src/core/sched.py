"""KRX market schedule helpers (KST)."""

from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

# KRX 정규장 (단순 모델: 09:00~15:30, 평일)
OPEN = time(9, 0)
CLOSE = time(15, 30)


def _now(now: datetime | None = None) -> datetime:
    return (now or datetime.now(tz=KST)).astimezone(KST)


def is_weekday(now: datetime | None = None) -> bool:
    return _now(now).weekday() < 5


def is_market_open(now: datetime | None = None) -> bool:
    """True during KRX regular session on weekdays."""
    dt = _now(now)
    if not is_weekday(dt):
        return False
    t = dt.time()
    return OPEN <= t < CLOSE


def market_label(now: datetime | None = None) -> str:
    """Human-readable session label."""
    dt = _now(now)
    if not is_weekday(dt):
        return "weekend"
    t = dt.time()
    if t < OPEN:
        return "pre_market"
    if t >= CLOSE:
        return "after_market"
    return "open"
