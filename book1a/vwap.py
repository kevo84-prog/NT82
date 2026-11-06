"""Book 1A 08:10 CT VWAP (AMT PO-8, replay plan C2 / U1; checklist P0.6).

Definition (frozen for the replay):
  VWAP = sum(price x volume) / sum(volume) over every trade of the front NQ contract in the
  Databento MBO data (trade messages, both aggressor sides; same front contract and roll
  rule as the map).
  Session VWAP resets at 17:00 CT each trading day (the Globex open), so at 08:10 CT it is
  the overnight session VWAP. Weekly VWAP resets at the Sunday 17:00 CT open.
  Bands: +/-1 volume-weighted standard deviation around each VWAP.
  Only trades before 08:10:00 CT are used (strictly before; a trade stamped exactly
  08:10:00.000 is excluded, matching NinjaTrader's bar rule that a tick at hh:mm:00.000
  belongs to the next bar).
  The 16:00-17:00 CT halt adds no trades.
  Roll day (U1, "ours"): both VWAPs restart on the new front contract at its first session.
  Implemented as: the trade input is the new contract's tape only, and the weekly window
  start is max(Sunday 17:00 CT, contract_first_session_start) when the latter is given.
  The 08:30 RTH VWAP is diagnostic only and never changes the 08:10 map.

Every output carries available_at = 08:10:00 CT on the session date (the map as-of time).
Timestamps are UTC nanoseconds (Databento ts_event) or tz-aware datetimes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable, Optional, Sequence
from zoneinfo import ZoneInfo

import numpy as np

VERSION = "vwap-v1.0"
CT = ZoneInfo("America/Chicago")
AS_OF = time(8, 10, 0)
GLOBEX_OPEN = time(17, 0, 0)
NS = 1_000_000_000


def ct(d: date, t: time) -> datetime:
    return datetime.combine(d, t, tzinfo=CT)


def to_ns(dt: datetime) -> int:
    """tz-aware datetime -> UTC epoch nanoseconds (integer, exact to the microsecond)."""
    if dt.tzinfo is None:
        raise ValueError("naive datetime")
    return int(dt.timestamp()) * NS + dt.microsecond * 1000


def session_start(session_date: date) -> datetime:
    """17:00 CT on the previous calendar day (Sunday 17:00 CT for a Monday session)."""
    return ct(session_date - timedelta(days=1), GLOBEX_OPEN)


def week_start(session_date: date) -> datetime:
    """The Sunday 17:00 CT open at or before this session's start."""
    s = session_start(session_date)
    # weekday(): Monday=0 ... Sunday=6
    back = (s.weekday() - 6) % 7
    return ct(s.date() - timedelta(days=back), GLOBEX_OPEN)


def as_of(session_date: date) -> datetime:
    return ct(session_date, AS_OF)


@dataclass(frozen=True)
class VwapResult:
    session_date: date
    scope: str                 # SESSION | WEEKLY
    window_start_ct: datetime
    window_end_ct: datetime    # exclusive (08:10:00 CT)
    n_trades: int
    volume: int
    vwap: Optional[float]
    sd: Optional[float]
    available_at_ct: datetime

    @property
    def upper(self) -> Optional[float]:
        return None if self.vwap is None else self.vwap + self.sd

    @property
    def lower(self) -> Optional[float]:
        return None if self.vwap is None else self.vwap - self.sd

    def as_row(self) -> dict:
        return {
            "session_date": self.session_date.isoformat(),
            "scope": self.scope,
            "window_start_ct": self.window_start_ct.isoformat(),
            "window_end_ct": self.window_end_ct.isoformat(),
            "n_trades": self.n_trades,
            "volume": self.volume,
            "vwap": None if self.vwap is None else round(self.vwap, 6),
            "sd": None if self.sd is None else round(self.sd, 6),
            "sd1_up": None if self.vwap is None else round(self.upper, 6),
            "sd1_dn": None if self.vwap is None else round(self.lower, 6),
            "available_at_ct": self.available_at_ct.isoformat(),
        }


def _vwap_sd(prices: np.ndarray, sizes: np.ndarray):
    vol = int(sizes.sum())
    if vol <= 0:
        return None, None, vol
    p = prices.astype(np.float64)
    v = sizes.astype(np.float64)
    pv = math.fsum(p * v)
    vwap = pv / vol
    var = math.fsum(v * (p - vwap) ** 2) / vol
    return vwap, math.sqrt(max(var, 0.0)), vol


def compute_window(ts_ns: np.ndarray, price: np.ndarray, size: np.ndarray,
                   start: datetime, end: datetime, session_date: date, scope: str) -> VwapResult:
    """VWAP and +/-1 sigma over trades with start <= ts < end (end exclusive)."""
    ts_ns = np.asarray(ts_ns, dtype=np.int64)
    lo, hi = to_ns(start), to_ns(end)
    m = (ts_ns >= lo) & (ts_ns < hi)
    vwap, sd, vol = _vwap_sd(np.asarray(price)[m], np.asarray(size)[m])
    return VwapResult(session_date, scope, start, end, int(m.sum()), vol, vwap, sd, as_of(session_date))


def vwap_0810(ts_ns: Sequence[int], price: Sequence[float], size: Sequence[int], session_date: date,
              contract_first_session_start: Optional[datetime] = None) -> dict:
    """Session (overnight) and weekly VWAP with +/-1 sigma as of 08:10:00 CT.

    ts_ns/price/size: the front contract's trade messages (any order; filtered by time).
    contract_first_session_start: on a roll day, the 17:00 CT open of the new contract's first
    session as front (U1 restart). Both windows start no earlier than it.
    """
    end = as_of(session_date)
    s_start = session_start(session_date)
    w_start = week_start(session_date)
    if contract_first_session_start is not None:
        s_start = max(s_start, contract_first_session_start)
        w_start = max(w_start, contract_first_session_start)
    ts = np.asarray(ts_ns, dtype=np.int64)
    pr = np.asarray(price, dtype=np.float64)
    sz = np.asarray(size, dtype=np.int64)
    return {
        "SESSION": compute_window(ts, pr, sz, s_start, end, session_date, "SESSION"),
        "WEEKLY": compute_window(ts, pr, sz, w_start, end, session_date, "WEEKLY"),
    }


def tag_zone(zone_lo: float, zone_hi: float, level: Optional[float], tolerance_pts: float = 5.0) -> bool:
    """AMT PO-8: a zone gets the tag if the level is inside it or within 5 points (ours)."""
    if level is None:
        return False
    return (zone_lo - tolerance_pts) <= level <= (zone_hi + tolerance_pts)
