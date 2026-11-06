"""1-minute bars with aggressor buy/sell volume and footprint flags from a harness tape (Book 1A input).

Tape rows (jeron_engine.mbo_tape): time_local (CT, 7 decimals), price, bid, ask, volume, aggressor (B/S/U).
Bars are stamped at their END; a tick at exactly hh:mm:00.000 belongs to the bar ending then (NinjaTrader rule,
the same convention as jeron_engine.arms.MinuteBars). close_ct is tz-aware (America/Chicago).

Flags (approximations of the S1.4 footprint evidence, used only by Book 1A map v2.4 arrival evidence and PO-9):
  imb_buy / imb_sell  a stacked diagonal imbalance: 2+ adjacent price rows where ask volume at p is >= 400% of the
                      bid volume at p - 1 tick (buy), min cell 10, zero denominator counts (S1.4 defaults, Jeron 400%)
  large_buy / large_sell  a single tape record of >= 60 contracts (Deep Trades 60, Jeron). S1.4 clusters records
                      within 250 ms / 2 ticks; this is the un-clustered approximation and is logged as such.
"""
from __future__ import annotations

import gzip
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from book1a.map_v24 import Bar

VERSION = "bars-v1.0"
CT = ZoneInfo("America/Chicago")
TICK = 0.25
IMB_RATIO = 4.0
IMB_MIN_CELL = 10
IMB_STACK = 2
LARGE_TRADE = 60


def _bar_end(t: datetime) -> datetime:
    base = t.replace(second=0, microsecond=0)
    return base if t == base else base + timedelta(minutes=1)


def _parse_ct(s: str) -> datetime:
    return datetime.fromisoformat(s[:26]).replace(tzinfo=CT)


def bars_from_rows(rows, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Bar]:
    """rows: iterable of (time_ct str or datetime, price, volume, aggressor). start/end: tz-aware CT bounds on tick time."""
    acc: Dict[datetime, dict] = {}
    for t, px, vol, ag in rows:
        if isinstance(t, str):
            t = _parse_ct(t)
        if start is not None and t < start:
            continue
        if end is not None and t >= end:
            break
        e = _bar_end(t)
        b = acc.get(e)
        if b is None:
            b = acc[e] = {"o": px, "h": px, "l": px, "c": px, "buy": 0, "sell": 0, "ask_at": defaultdict(int),
                          "bid_at": defaultdict(int), "large_buy": False, "large_sell": False}
        b["h"] = max(b["h"], px); b["l"] = min(b["l"], px); b["c"] = px
        if ag == "B":
            b["buy"] += vol; b["ask_at"][px] += vol
            if vol >= LARGE_TRADE: b["large_buy"] = True
        elif ag in ("S", "A"):
            b["sell"] += vol; b["bid_at"][px] += vol
            if vol >= LARGE_TRADE: b["large_sell"] = True
    out = []
    for e in sorted(acc):
        b = acc[e]
        imb_buy, imb_sell = _stacked(b["ask_at"], b["bid_at"])
        out.append(Bar(e, b["o"], b["h"], b["l"], b["c"], b["buy"], b["sell"], imb_buy, imb_sell, b["large_buy"], b["large_sell"]))
    return out


def _stacked(ask_at: Dict[float, int], bid_at: Dict[float, int]):
    """Diagonal imbalances: buy at price p vs sell at p - tick; sell at p vs buy at p + tick."""
    prices = sorted(set(ask_at) | set(bid_at))
    buy_rows, sell_rows = [], []
    for p in prices:
        a, b_below = ask_at.get(p, 0), bid_at.get(round(p - TICK, 2), 0)
        if a >= IMB_MIN_CELL and (b_below == 0 or a >= IMB_RATIO * b_below):
            buy_rows.append(p)
        s, a_above = bid_at.get(p, 0), ask_at.get(round(p + TICK, 2), 0)
        if s >= IMB_MIN_CELL and (a_above == 0 or s >= IMB_RATIO * a_above):
            sell_rows.append(p)
    return _has_stack(buy_rows), _has_stack(sell_rows)


def _has_stack(rows: List[float]) -> bool:
    run = 1
    for i in range(1, len(rows)):
        run = run + 1 if abs(rows[i] - rows[i - 1] - TICK) < 1e-9 else 1
        if run >= IMB_STACK:
            return True
    return len(rows) >= IMB_STACK and IMB_STACK <= 1


def bars_from_tape(path, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Bar]:
    op = gzip.open if str(path).endswith(".gz") else open

    def rows():
        with op(path, "rt") as f:
            first = f.readline()
            if not first.startswith("time_local"):
                yield _row(first)
            for line in f:
                yield _row(line)
    return bars_from_rows(rows(), start, end)


def _row(line: str):
    p = line.rstrip("\n").split(",")
    return p[0], float(p[1]), int(p[4]), p[5].strip()


def trades_from_tape(path, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """(ts_ns, price, size) arrays for book1a.vwap from a harness tape (trades of the front contract only)."""
    import numpy as np
    op = gzip.open if str(path).endswith(".gz") else open
    T, P, S = [], [], []
    with op(path, "rt") as f:
        for line in f:
            if line.startswith("time_local"):
                continue
            p = line.rstrip("\n").split(",")
            t = _parse_ct(p[0])
            if start is not None and t < start:
                continue
            if end is not None and t >= end:
                break
            T.append(int(t.timestamp()) * 1_000_000_000 + t.microsecond * 1000); P.append(float(p[1])); S.append(int(p[4]))
    return np.array(T, dtype=np.int64), np.array(P), np.array(S, dtype=np.int64)


# ---- profiles in 5-point rows (for MAP4 areas and delta bands) ------------------------------------
ROW_PTS = 5.0


def row_of(px: float) -> float:
    import math
    return math.floor(px / ROW_PTS) * ROW_PTS


def profiles_from_rows(rows, windows: Dict[str, tuple]) -> Dict[str, dict]:
    """rows: (time_ct, price, volume, aggressor). windows: name -> (start_ct, end_ct), end exclusive.
    Returns name -> {"volume": {row_lo: vol}, "delta": {row_lo: signed delta}, "poc_row": row_lo of max volume}."""
    out = {k: {"volume": defaultdict(int), "delta": defaultdict(int)} for k in windows}
    for t, px, vol, ag in rows:
        if isinstance(t, str):
            t = _parse_ct(t)
        r = row_of(px)
        for k, (s, e) in windows.items():
            if s <= t < e:
                out[k]["volume"][r] += vol
                out[k]["delta"][r] += vol if ag == "B" else (-vol if ag in ("S", "A") else 0)
    res = {}
    for k, v in out.items():
        vol = dict(v["volume"])
        res[k] = {"volume": vol, "delta": dict(v["delta"]), "poc_row": max(vol, key=vol.get) if vol else None}
    return res
