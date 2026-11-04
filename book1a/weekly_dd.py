"""Weekly double distribution (E23; ours: PD rule applied to weekly). Frozen Nov 4, 2026 before any real day was run.

Kyron, Nov 4 (frozen research-design decision, not a bug fix): apply the existing PD double-distribution algorithm
and thresholds of JeronPreopenMap v2.3 (DoubleDistJson), unchanged, to the developing weekly profile. The weekly
profile resets at the Sunday 17:00 CT open and uses only trades before the 08:10 CT as-of. Nothing is tuned.

The map's rule, ported line for line (JeronPreopenMap.cs DoubleDistJson, HvnLvnAreas, AddRuns, AddSinglePrints):
  - volume per tick -> rows of HvnTicksPerRow = 20 ticks (5 points), row = floor(tick / 20);
  - fewer than 5 rows with volume -> no areas;
  - 3-row smoothing s[i] = (raw[i-1] + raw[i] + raw[i+1]) / 3 over the dense row range (missing rows = 0);
  - HVN = runs of rows with s >= 70% of the peak (HvnPct); LVN = runs with s <= 30% of the peak (LvnPct) between
    the first and the last HVN row;
  - single prints = runs of at least MinSinglePrintRows = 2 TPO rows (TpoTicksPerRow = 20 ticks) touched by exactly
    one 30-minute period (period = floor(minutes since 2000-01-01 00:00 CT / 30));
  - separators = the LVNs (in order) then the single prints (in order); HVN blocks sorted by lo; the first pair of
    neighbouring HVN blocks with a separator touching the gap between them (not sp.hi < gap_lo and not
    sp.lo > gap_hi) is the double distribution;
  - area lo = first row * 5 points, area hi = (last row + 1) * 5 points - 1 tick.
The PD version reads the PD cash profile and the PD TPO single prints; this one reads the developing week.

E26 (Kyron, Nov 4): when the map leaves the developing weekly profile out (its packet note "DATA: weekly profile left
out: <reason>", e.g. a data gap; the map's Covered() check with SkipPartialProfiles on), the weekly rule is skipped and
the feature is marked status=UNAVAILABLE with the map's reason. UNAVAILABLE is never a valid profile with no edge: it
carries no double_distribution key and gives no plan inputs. Every other result has status=AVAILABLE.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

VERSION = "weekly-dd-v1.1"   # v1.1: UNAVAILABLE when the map leaves the weekly profile out (E26, Kyron Nov 4)
LABEL = "ours: PD rule applied to weekly"
TICK = 0.25
HVN_TICKS_PER_ROW = 20      # JeronPreopenMap HvnTicksPerRow
TPO_TICKS_PER_ROW = 20      # JeronPreopenMap TpoTicksPerRow
HVN_PCT = 70                # JeronPreopenMap HvnPct
LVN_PCT = 30                # JeronPreopenMap LvnPct
MIN_SINGLE_PRINT_ROWS = 2   # JeronPreopenMap MinSinglePrintRows
TPO_MINUTES = 30
EPOCH = datetime(2000, 1, 1)


def _floordiv(a: int, b: int) -> int:
    return a // b       # Python // floors, like the map's FloorDiv


class Profile:
    """Volume per tick and TPO counts per TPO row, built the way the map's PriceProfile.AddTick builds them."""

    def __init__(self):
        self.vol: Dict[int, int] = defaultdict(int)
        self.tpo: Dict[int, int] = defaultdict(int)
        self._last_period: Dict[int, int] = {}
        self.total = 0
        self.high = -math.inf
        self.low = math.inf
        self.pv = 0.0
        self.first_ct: Optional[datetime] = None
        self.last_ct: Optional[datetime] = None

    def add(self, ct: datetime, price: float, size: int) -> None:
        if size <= 0:
            return
        key = int(round(price / TICK))
        self.vol[key] += size
        self.total += size
        self.pv += price * size
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        if self.first_ct is None:
            self.first_ct = ct
        self.last_ct = ct
        naive = ct.replace(tzinfo=None)
        period = math.floor((naive - EPOCH).total_seconds() / 60.0 / TPO_MINUTES)
        row = _floordiv(key, TPO_TICKS_PER_ROW)
        if self._last_period.get(row) != period:
            self._last_period[row] = period
            self.tpo[row] += 1

    @property
    def vwap(self) -> Optional[float]:
        return self.pv / self.total if self.total else None


def build_profile(rows: Iterable[tuple], start: datetime, end: datetime) -> Profile:
    """rows: (time_ct, price, size, ...) in time order; keeps start <= t < end."""
    p = Profile()
    for r in rows:
        t = r[0]
        if t < start:
            continue
        if t >= end:
            break
        p.add(t, float(r[1]), int(r[2]))
    return p


def _area(kind: str, source: str, row_lo: int, row_end: int, rt: int) -> dict:
    return {"type": kind, "source": source, "lo": round(row_lo * rt * TICK, 2), "hi": round(row_end * rt * TICK - TICK, 2)}


def _runs(s: List[float], min_row: int, rt: int, a: int, b: int, test, kind: str, source: str, out: List[dict]) -> None:
    start = -1
    for i in range(a, b + 2):
        inrun = i <= b and test(s[i])
        if inrun and start < 0:
            start = i
        if not inrun and start >= 0:
            out.append(_area(kind, source, min_row + start, min_row + i, rt))
            start = -1


def hvn_lvn_areas(rows: Dict[int, int], source: str) -> List[dict]:
    """JeronPreopenMap.HvnLvnAreas on rows (row index -> volume)."""
    res: List[dict] = []
    if len(rows) < 5:
        return res
    mn, mx = min(rows), max(rows)
    n = mx - mn + 1
    raw = [0.0] * n
    for k, v in rows.items():
        raw[k - mn] = float(v)
    s = [0.0] * n
    peak = 0.0
    for i in range(n):
        a = raw[i - 1] if i > 0 else 0.0
        c = raw[i + 1] if i < n - 1 else 0.0
        s[i] = (a + raw[i] + c) / 3.0
        peak = max(peak, s[i])
    if peak <= 0:
        return res
    h_t, l_t = peak * HVN_PCT / 100.0, peak * LVN_PCT / 100.0
    hi_idx = [i for i in range(n) if s[i] >= h_t]
    first_h, last_h = (hi_idx[0], hi_idx[-1]) if hi_idx else (-1, -1)
    _runs(s, mn, HVN_TICKS_PER_ROW, 0, n - 1, lambda x: x >= h_t, "HVN", source, res)
    if first_h >= 0 and last_h > first_h:
        _runs(s, mn, HVN_TICKS_PER_ROW, first_h, last_h, lambda x: x <= l_t, "LVN", source, res)
    return res


def single_prints(tpo: Dict[int, int], source: str) -> List[dict]:
    """JeronPreopenMap.AddSinglePrints on TPO rows (row index -> number of 30-minute periods)."""
    out: List[dict] = []
    if not tpo:
        return out
    mn, mx = min(tpo), max(tpo)
    start = None
    for r in range(mn, mx + 2):
        single = r <= mx and tpo.get(r, 0) == 1
        if single and start is None:
            start = r
        if not single and start is not None:
            if r - start >= max(1, MIN_SINGLE_PRINT_ROWS):
                out.append(_area("SP", source, start, r, TPO_TICKS_PER_ROW))
            start = None
    return out


def double_distribution(vol_by_tick: Dict[int, int], sp_areas: List[dict], source: str) -> dict:
    """JeronPreopenMap.DoubleDistJson on any profile. Returns the packet form; profile names the source."""
    if not vol_by_tick or sum(vol_by_tick.values()) <= 0:
        return {"available": False}
    rows: Dict[int, int] = defaultdict(int)
    for k, v in vol_by_tick.items():
        rows[_floordiv(k, HVN_TICKS_PER_ROW)] += v
    areas = hvn_lvn_areas(dict(rows), source)
    hvn = [a for a in areas if a["type"] == "HVN"]
    sep = [a for a in areas if a["type"] == "LVN"] + list(sp_areas)
    hvn.sort(key=lambda a: a["lo"])     # List.Sort is not stable, but HVN runs never share a lo
    for i in range(1, len(hvn)):
        g_lo, g_hi = hvn[i - 1]["hi"], hvn[i]["lo"]
        for sp in sep:
            if sp["hi"] < g_lo or sp["lo"] > g_hi:
                continue
            return {"available": True, "double_distribution": True, "lower_hvn": [hvn[i - 1]["lo"], hvn[i - 1]["hi"]],
                    "upper_hvn": [hvn[i]["lo"], hvn[i]["hi"]], "separator": "SINGLE_PRINTS" if sp["type"] == "SP" else "LVN",
                    "separator_lo": sp["lo"], "separator_hi": sp["hi"], "hvn_blocks": len(hvn), "profile": source}
    return {"available": True, "double_distribution": False, "hvn_blocks": len(hvn), "profile": source}


def map_weekly_exclusion(packet: Optional[dict]) -> Optional[str]:
    """The map's reason for leaving the developing weekly profile out, or None when it built it (E26)."""
    if not packet:
        return None
    notes = ((packet.get("data") or {}).get("notes") or []) + (packet.get("notes") or [])
    for n in notes:
        if isinstance(n, str) and n.startswith("DATA: weekly profile left out"):
            return n.split(":", 2)[-1].strip() if n.count(":") >= 2 else n
    return None


def unavailable(reason: str, week_start: datetime, as_of: datetime) -> dict:
    return {"available": False, "status": "UNAVAILABLE", "reason": "map left the weekly profile out: " + reason, "profile": "WK",
            "rule": LABEL, "version": VERSION, "window_start": week_start.isoformat(), "window_end": as_of.isoformat(),
            "last_trade_ct": None, "available_at": as_of.isoformat()}


def weekly(rows: Iterable[tuple], week_start: datetime, as_of: datetime, packet: Optional[dict] = None) -> Tuple[dict, Optional[Profile], List[dict]]:
    """The weekly double distribution at the as-of: (result in packet form + rule label, profile, weekly single prints).
    packet: the day's map packet; when the map left the weekly profile out, the result is UNAVAILABLE (E26)."""
    why = map_weekly_exclusion(packet)
    if why is not None:
        return unavailable(why, week_start, as_of), None, []
    p = build_profile(rows, week_start, as_of)
    sps = single_prints(dict(p.tpo), "TPO_WK")
    res = double_distribution(dict(p.vol), sps, "WK")
    res.update({"status": "AVAILABLE" if res.get("available") else "UNAVAILABLE", "rule": LABEL, "version": VERSION, "window_start": week_start.isoformat(), "window_end": as_of.isoformat(),
                "last_trade_ct": p.last_ct.isoformat() if p.last_ct else None, "available_at": as_of.isoformat()})
    return res, p, sps


def as_plan_inputs(res: dict) -> Optional[tuple]:
    """(dist_a, separator, dist_b, profile) for map_v24.dd_edge_zone, or None when there is no weekly split."""
    if not res or res.get("status") != "AVAILABLE" or not res.get("double_distribution"):
        return None
    return ((res["lower_hvn"][0], res["lower_hvn"][1]), (res["separator_lo"], res["separator_hi"]),
            (res["upper_hvn"][0], res["upper_hvn"][1]), "WK")
