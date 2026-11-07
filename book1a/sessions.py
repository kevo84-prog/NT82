"""Block 1 session calendar (Book 1 design v3.5 / data integrity result; replay plan section 2).

Sessions follow the Book 1 calendar: weekdays, no cash session on Thanksgiving, Christmas, New Year's Day, MLK Day,
Presidents' Day and Good Friday; half days (Nov 28 and Dec 24, 2025) included. Roll days (NinjaTrader): Dec 15, 2025
and Mar 16, 2026 (LOG_ONLY under check A, still sessions).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import List

VERSION = "sessions-v1.1"   # v1.1 (Nov 6, 2026): session_close() for the Phase 2 review fields

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


# Session close (Book 1 calendar, econ_calendar_2025-10_2026-04.csv and design v3.10 "Data integrity result"): a full
# day closes at 15:00 CT (cash close); a half day (Nov 28 and Dec 24, 2025) at 12:15 CT, when CME equity futures close
# (the calendar note: "Cash ends 12:00 CT; CME equity futures close 12:15 CT"; the MBO files end at 12:15:00 CT).
# The map keeps its own cash end (HalfDayDates ...@12:00); this value is used only by the Phase 2 review fields.
FULL_DAY_CLOSE = time(15, 0)
HALF_DAY_CLOSE = time(12, 15)


def session_close(d: date) -> datetime:
    """The session's close in CT (naive), from the Book 1 calendar."""
    if d.weekday() >= 5 or d in NO_CASH_SESSION:
        raise ValueError(f"{d} is not a Book 1 session")
    return datetime.combine(d, HALF_DAY_CLOSE if d in HALF_DAYS else FULL_DAY_CLOSE)


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
