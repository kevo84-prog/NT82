"""Block 1 session calendar (Book 1 design v3.5 / data integrity result; replay plan section 2).

Sessions follow the Book 1 calendar: weekdays, no cash session on Thanksgiving, Christmas, New Year's Day, MLK Day,
Presidents' Day and Good Friday; half days (Nov 28 and Dec 24, 2025) included. Roll days (NinjaTrader): Dec 15, 2025
and Mar 16, 2026 (LOG_ONLY under check A, still sessions).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import List

VERSION = "sessions-v1.0"

NO_CASH_SESSION = {date(2025, 11, 27), date(2025, 12, 25), date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3)}
HALF_DAYS = {date(2025, 11, 28), date(2025, 12, 24)}
ROLL_DATES = {date(2025, 12, 15), date(2026, 3, 16)}
HOLIDAY_HALTS = {date(2025, 11, 27), date(2026, 1, 19), date(2026, 2, 16)}          # trading to 12:00 CT, no cash session
CLOSED = {date(2025, 12, 25), date(2026, 1, 1), date(2026, 4, 3)}

PHASES = {
    "phase1": (date(2025, 10, 22), date(2025, 11, 4)),
    "phase2": (date(2025, 11, 5), date(2025, 12, 4)),
    "phase3": (date(2025, 12, 5), date(2026, 2, 4)),
    "phase4": (date(2026, 2, 5), date(2026, 4, 21)),
}
PARITY_DAYS = [date(2026, 9, 28), date(2026, 10, 8)]
REPLAY_DIFF_DAYS = [date(2025, 11, 5), date(2025, 12, 15)]        # P0.3: one normal day, one roll day
VWAP_HAND_CHECK_DAYS = [date(2025, 10, 22), date(2025, 11, 5), date(2025, 12, 15), date(2026, 3, 16)]
PHASE1_HAND_CHECK_DAYS = [date(2025, 10, 22), date(2025, 10, 28), date(2025, 11, 4)]   # P0.7 / P0.9 / P0.11: 3 Phase 1 days (ours)


def sessions(start: date, end: date) -> List[date]:
    out = []
    d = start
    while d <= end:
        if d.weekday() < 5 and d not in NO_CASH_SESSION:
            out.append(d)
        d += timedelta(days=1)
    return out


def phase_sessions(name: str) -> List[date]:
    return sessions(*PHASES[name])


def block1_sessions() -> List[date]:
    return sessions(PHASES["phase1"][0], PHASES["phase4"][1])


def harness_dates(ds) -> str:
    return ",".join(d.isoformat() for d in sorted(ds))
