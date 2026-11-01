"""Book 1A map v2.4 outputs (AMT doc PO-1, PO-3, PO-6, PO-7, PO-9, PO-11, PO-13; checklist P0.7).

This module ADDS Book 1A outputs next to the frozen map v2.3 packet; it does not change any
v2.3 level or zone. Every zone is frozen at the as-of time (08:10 CT) and carries available_at.
Every number marked (ours) is our own setting from the AMT doc, frozen before any result is read.

Inputs are plain Python records so the module can be fed from the Book 1 harness (1-minute bars
with bid/ask volume from the MBO aggressor flag, the v2.3 packet's profiles, ADR and
double_distribution) or from synthetic data in the unit tests.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

VERSION = "map-v2.4-book1a-v1.0"
CT = ZoneInfo("America/Chicago")
TICK = 0.25

# ---- (ours) settings, AMT doc ---------------------------------------------------------------
SWING_BARS = 15                 # PO-1 step 1
ARRIVAL_BARS_BEFORE = 2         # PO-1 step 2: swing bar or the 2 bars before it
ARRIVAL_MIN_DELTA = 150         # S1.4 MinAbsDelta
DEPARTURE_BARS = 10             # PO-1 step 2
DEPARTURE_ADR = 0.25            # PO-1 step 2
ZONE_MIN_PTS = 10.0             # PO-1 step 3
ZONE_MAX_PTS = 40.0             # PO-1 step 3
MERGE_WITHIN_PTS = 5.0          # PO-1 step 3
FLIP_ACCEPT_CLOSES = 3          # PO-1 step 4 (strategy acceptance closes)
FLIP_ACCEPT_TICKS = 2           # PO-1 step 4 (break distance)
FLIP_OVERLAP = 0.50             # PO-1 step 4
VWAP_TAG_PTS = 5.0              # PO-1 step 5 / PO-8
STACK_PTS = 5.0                 # PO-1 step 5
DELTA_TOP_SHARE = 0.20          # PO-1 step 5 / PO-7
KEEP_PER_SIDE = 2               # PO-1 step 6
KEEP_WITHIN_ADR = 1.0           # PO-1 step 6
MAP4_PEAK_SHARE = 0.70          # PO-6
MAP4_MAX_PTS = 40.0             # PO-6
MAP4_PAD_PTS = 5.0              # PO-6 (narrower than 10: keep the +/-5 pad)
BAND_MIN_PTS = 10.0             # PO-7
BAND_MAX_PTS = 40.0             # PO-7
ACCEPT_MINUTES = 60             # PO-9
ACCEPT_CLOSE_SHARE = 0.80       # PO-9
ACCEPT_VOLUME_SHARE = 0.20      # PO-9
DD_EDGE_MAX_PTS = 40.0          # PO-11
ROW_PTS = 5.0                   # 5-point profile rows (map v2.3)


@dataclass(frozen=True)
class Bar:
    """One 1-minute bar; close_ct is the bar's close time (the bar is usable once close_ct <= as_of)."""
    close_ct: datetime
    open: float
    high: float
    low: float
    close: float
    buy_vol: int = 0
    sell_vol: int = 0
    imb_buy: bool = False      # stacked buy imbalance (400%, Jeron) inside the bar
    imb_sell: bool = False
    large_buy: bool = False    # large buy trade (Deep Trades 60, Jeron)
    large_sell: bool = False

    @property
    def delta(self) -> int:
        return self.buy_vol - self.sell_vol

    @property
    def volume(self) -> int:
        return self.buy_vol + self.sell_vol

    @property
    def body_lo(self) -> float:
        return min(self.open, self.close)

    @property
    def body_hi(self) -> float:
        return max(self.open, self.close)


@dataclass
class Zone:
    lo: float
    hi: float
    kind: str                       # REJ_HIGH | REJ_LOW | FLIP | MAP4_AREA | DELTA_BAND | DD_EDGE
    formed_ct: Optional[datetime]
    available_at: datetime
    session: str = ""               # ON | PD | WK (PO-1 step 5)
    arrival_evidence: str = ""      # DELTA:<v> | IMB | LARGE
    departure_pts: float = 0.0
    tags: List[str] = field(default_factory=list)
    stack: List[str] = field(default_factory=list)
    zone_class: str = "TARGET"      # DECISION | TARGET (PO-3, set by families)
    label: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def width(self) -> float:
        return self.hi - self.lo

    def as_row(self) -> dict:
        return {"lo": self.lo, "hi": self.hi, "kind": self.kind, "session": self.session,
                "formed_ct": None if self.formed_ct is None else self.formed_ct.isoformat(),
                "available_at": self.available_at.isoformat(), "arrival_evidence": self.arrival_evidence,
                "departure_pts": round(self.departure_pts, 2), "tags": "|".join(self.tags),
                "stack": "|".join(self.stack), "class": self.zone_class, "label": self.label, **self.extra}


# ---- helpers ----------------------------------------------------------------------------------
def _r(x: float) -> float:
    """Round to a tick, half away from zero."""
    return math.floor(x / TICK + 0.5) * TICK if x >= 0 else -math.floor(-x / TICK + 0.5) * TICK


def _cap_to_extreme(lo: float, hi: float, extreme: str) -> Tuple[float, float]:
    """Keep at most ZONE_MAX_PTS nearest the swing extreme ('hi' for a REJ_HIGH, 'lo' for a REJ_LOW)."""
    if hi - lo > ZONE_MAX_PTS:
        return (hi - ZONE_MAX_PTS, hi) if extreme == "hi" else (lo, lo + ZONE_MAX_PTS)
    return lo, hi


def _pad_min(lo: float, hi: float) -> Tuple[float, float]:
    if hi - lo < ZONE_MIN_PTS:
        pad = (ZONE_MIN_PTS - (hi - lo)) / 2.0
        return _r(lo - pad), _r(hi + pad)
    return lo, hi


def session_of(ts: datetime, session_date: date) -> str:
    """REJ_ON (overnight of this session), REJ_PD (prior-day cash 08:30-15:00), REJ_WK (earlier)."""
    on_start = datetime.combine(session_date - timedelta(days=1), time(17, 0), tzinfo=CT)
    if ts > on_start:
        return "ON"
    pd_date = prior_trading_day(session_date)
    pd_open = datetime.combine(pd_date, time(8, 30), tzinfo=CT)
    pd_close = datetime.combine(pd_date, time(15, 0), tzinfo=CT)
    if pd_open < ts <= pd_close:
        return "PD"
    return "WK"


def prior_trading_day(d: date) -> date:
    """Previous weekday (holiday handling comes from the packet's prior_sessions in the harness)."""
    p = d - timedelta(days=1)
    while p.weekday() >= 5:
        p -= timedelta(days=1)
    return p


def window_start(session_date: date) -> datetime:
    """PO-1: from the prior-day cash open (08:30 CT) through the developing week (Sunday 17:00 CT)."""
    pd_open = datetime.combine(prior_trading_day(session_date), time(8, 30), tzinfo=CT)
    s = datetime.combine(session_date - timedelta(days=1), time(17, 0), tzinfo=CT)
    back = (s.weekday() - 6) % 7
    wk = datetime.combine(s.date() - timedelta(days=back), time(17, 0), tzinfo=CT)
    return min(pd_open, wk)


# ---- PO-1: rejection and flip zones ----------------------------------------------------------
def find_swings(bars: Sequence[Bar], as_of: datetime, n: int = SWING_BARS) -> List[Tuple[int, str]]:
    """(index, 'HIGH'|'LOW') for bars whose high (low) is strictly the highest (lowest) of the n bars
    before and n after, where all n bars after closed at or before as_of. Ties are not swings (ours)."""
    out = []
    usable = [i for i, b in enumerate(bars) if b.close_ct <= as_of]
    last = usable[-1] if usable else -1
    for i in range(n, last - n + 1):
        b = bars[i]
        before = bars[i - n:i]
        after = bars[i + 1:i + 1 + n]
        if all(b.high > x.high for x in before) and all(b.high > x.high for x in after):
            out.append((i, "HIGH"))
        if all(b.low < x.low for x in before) and all(b.low < x.low for x in after):
            out.append((i, "LOW"))
    return out


def arrival_evidence(bars: Sequence[Bar], i: int, side: str) -> Optional[str]:
    """PO-1 step 2a: in the swing bar or the 2 bars before, delta >= 150 in the arrival direction,
    a stacked imbalance that way, or a large trade that way."""
    best = None
    for b in bars[max(0, i - ARRIVAL_BARS_BEFORE):i + 1]:
        if side == "HIGH":
            if b.delta >= ARRIVAL_MIN_DELTA:
                best = f"DELTA:{b.delta}" if best is None or best.startswith("DELTA") and b.delta > int(best[6:]) else best
            if b.imb_buy and best is None:
                best = "IMB"
            if b.large_buy and best is None:
                best = "LARGE"
        else:
            if -b.delta >= ARRIVAL_MIN_DELTA:
                best = f"DELTA:{b.delta}" if best is None or best.startswith("DELTA") and -b.delta > -int(best[6:]) else best
            if b.imb_sell and best is None:
                best = "IMB"
            if b.large_sell and best is None:
                best = "LARGE"
    return best


def departure(bars: Sequence[Bar], i: int, side: str, adr: float, as_of: datetime) -> float:
    """PO-1 step 2b: the largest move away from the swing within DEPARTURE_BARS bars after it."""
    best = 0.0
    for b in bars[i + 1:i + 1 + DEPARTURE_BARS]:
        if b.close_ct > as_of:
            break
        best = max(best, bars[i].high - b.low if side == "HIGH" else b.high - bars[i].low)
    return best


def rejection_zones(bars: Sequence[Bar], session_date: date, as_of: datetime, adr: float) -> List[Zone]:
    """PO-1 steps 1-3 (no merging, no flips, no selection)."""
    start = window_start(session_date)
    idx = [k for k, b in enumerate(bars) if start < b.close_ct <= as_of]
    if not idx:
        return []
    sub = [bars[k] for k in idx]
    zones = []
    for i, side in find_swings(sub, as_of):
        ev = arrival_evidence(sub, i, side)
        if ev is None:
            continue
        dep = departure(sub, i, side, adr, as_of)
        if dep < DEPARTURE_ADR * adr:
            continue
        window = sub[max(0, i - 2):i + 3]
        if side == "HIGH":
            hi = sub[i].high
            lo = min(b.body_lo for b in window)
            lo, hi = _cap_to_extreme(lo, hi, "hi")
            lo, hi = _pad_min(lo, hi)
            kind = "REJ_HIGH"
        else:
            lo = sub[i].low
            hi = max(b.body_hi for b in window)
            lo, hi = _cap_to_extreme(lo, hi, "lo")
            lo, hi = _pad_min(lo, hi)
            kind = "REJ_LOW"
        formed = sub[i].close_ct
        z = Zone(lo, hi, kind, formed, as_of, session_of(formed, session_date), ev, dep)
        z.extra["swing_price"] = sub[i].high if side == "HIGH" else sub[i].low
        z.extra["swing_index"] = idx[i]
        zones.append(z)
    return zones


def merge_same_side(zones: List[Zone]) -> List[Zone]:
    """PO-1 step 3: two REJ zones on the same side that overlap or sit within 5 points merge into one,
    still capped at 40 points (kept nearest the more extreme swing)."""
    out: List[Zone] = []
    for kind in ("REJ_HIGH", "REJ_LOW"):
        same = sorted([z for z in zones if z.kind == kind], key=lambda z: z.lo)
        cur: Optional[Zone] = None
        for z in same:
            if cur is not None and z.lo <= cur.hi + MERGE_WITHIN_PTS:
                lo, hi = min(cur.lo, z.lo), max(cur.hi, z.hi)
                lo, hi = _cap_to_extreme(lo, hi, "hi" if kind == "REJ_HIGH" else "lo")
                newer = z if z.formed_ct > cur.formed_ct else cur
                cur = Zone(lo, hi, kind, newer.formed_ct, newer.available_at, newer.session,
                           newer.arrival_evidence, max(cur.departure_pts, z.departure_pts),
                           extra={"merged_from": cur.extra.get("merged_from", 1) + 1})
            else:
                if cur is not None:
                    out.append(cur)
                cur = z
        if cur is not None:
            out.append(cur)
    return out


def accepted_through(bars: Sequence[Bar], start_idx: int, zone: Zone, as_of: datetime) -> Optional[int]:
    """PO-1 step 4: index of the bar completing 3 consecutive closes >= 2 ticks beyond the far edge."""
    run = 0
    for k in range(start_idx + 1, len(bars)):
        b = bars[k]
        if b.close_ct > as_of:
            break
        if zone.kind == "REJ_LOW":
            beyond = b.close <= zone.lo - FLIP_ACCEPT_TICKS * TICK
        else:
            beyond = b.close >= zone.hi + FLIP_ACCEPT_TICKS * TICK
        run = run + 1 if beyond else 0
        if run >= FLIP_ACCEPT_CLOSES:
            return k
    return None


def flips(bars: Sequence[Bar], zones: List[Zone], as_of: datetime) -> List[Zone]:
    """PO-1 step 4: a REJ zone, accepted through, then an opposite REJ overlapping it by >= 50%
    becomes one FLIP zone (union, capped at 40). Both parents are replaced."""
    used = set()
    out = []
    for a in sorted(zones, key=lambda z: z.formed_ct):
        if id(a) in used or a.kind not in ("REJ_LOW", "REJ_HIGH"):
            continue
        acc = accepted_through(bars, a.extra.get("swing_index", 0), a, as_of)
        if acc is None:
            continue
        opp = "REJ_HIGH" if a.kind == "REJ_LOW" else "REJ_LOW"
        for b in sorted(zones, key=lambda z: z.formed_ct):
            if id(b) in used or b.kind != opp or b.extra.get("swing_index", 0) <= acc:
                continue
            overlap = min(a.hi, b.hi) - max(a.lo, b.lo)
            if overlap / a.width >= FLIP_OVERLAP:
                lo, hi = min(a.lo, b.lo), max(a.hi, b.hi)
                lo, hi = _cap_to_extreme(lo, hi, "hi" if b.kind == "REJ_HIGH" else "lo")
                z = Zone(lo, hi, "FLIP", b.formed_ct, as_of, b.session, b.arrival_evidence, b.departure_pts,
                         extra={"flip_from": a.kind, "accepted_at_index": acc})
                out.append(z)
                used.add(id(a)); used.add(id(b))
                break
    return [z for z in zones if id(z) not in used] + out


def tag_zones(zones: List[Zone], session_vwap: Optional[float], delta_bands: List[Zone],
              stack_levels: Dict[str, float]) -> None:
    """PO-1 step 5: VWAP (within 5), DELTA_SELL / DELTA_BUY (overlaps a band), stack (levels within 5)."""
    for z in zones:
        if session_vwap is not None and z.lo - VWAP_TAG_PTS <= session_vwap <= z.hi + VWAP_TAG_PTS:
            z.tags.append("VWAP")
        for b in delta_bands:
            if b.hi >= z.lo and b.lo <= z.hi:
                t = "DELTA_SELL" if b.extra.get("sign") == "SELL" else "DELTA_BUY"
                if t not in z.tags:
                    z.tags.append(t)
        for name, px in stack_levels.items():
            if z.lo - STACK_PTS <= px <= z.hi + STACK_PTS:
                z.stack.append(name)


def select_zones(zones: List[Zone], price: float, adr: float, bars: Sequence[Bar], as_of: datetime) -> List[Zone]:
    """PO-1 step 6: at most 2 per side within 1 x ADR, nearest first; ties FLIP > REJ, ON > PD > WK;
    zones price has traded through by more than 1 x ADR since they formed are dropped."""
    def traded_through(z: Zone) -> bool:
        after = [b for b in bars if z.formed_ct is not None and z.formed_ct < b.close_ct <= as_of]
        if not after:
            return False
        up = max(b.high for b in after) > z.hi + adr      # through a resistance, far above it
        dn = min(b.low for b in after) < z.lo - adr       # through a support, far below it
        if z.kind == "REJ_HIGH":
            return up
        if z.kind == "REJ_LOW":
            return dn
        return up or dn                                    # FLIP: either way

    rank_kind = {"FLIP": 0, "REJ_HIGH": 1, "REJ_LOW": 1}
    rank_sess = {"ON": 0, "PD": 1, "WK": 2}
    above = [z for z in zones if z.lo >= price and z.lo - price <= KEEP_WITHIN_ADR * adr and not traded_through(z)]
    below = [z for z in zones if z.hi <= price and price - z.hi <= KEEP_WITHIN_ADR * adr and not traded_through(z)]
    above.sort(key=lambda z: (z.lo - price, rank_kind.get(z.kind, 9), rank_sess.get(z.session, 9)))
    below.sort(key=lambda z: (price - z.hi, rank_kind.get(z.kind, 9), rank_sess.get(z.session, 9)))
    return above[:KEEP_PER_SIDE] + below[:KEEP_PER_SIDE]


# ---- PO-6: MAP4 whole high-volume area -------------------------------------------------------
def map4_area(rows: Dict[float, int], peak_row_lo: float, as_of: datetime, name: str) -> Zone:
    """rows: {row_lo: volume} in 5-point rows. Area = run of rows either side of the peak with volume
    >= 70% of the peak row; stops at the first row below; capped at 40 points centred on the peak;
    narrower than 10 points -> keep the +/-5 pad."""
    peak = rows[peak_row_lo]
    thr = MAP4_PEAK_SHARE * peak
    lo = peak_row_lo
    while (lo - ROW_PTS) in rows and rows[lo - ROW_PTS] >= thr:
        lo -= ROW_PTS
    hi = peak_row_lo + ROW_PTS
    while hi in rows and rows[hi] >= thr:
        hi += ROW_PTS
    centre = peak_row_lo + ROW_PTS / 2
    if hi - lo > MAP4_MAX_PTS:
        lo, hi = centre - MAP4_MAX_PTS / 2, centre + MAP4_MAX_PTS / 2
    if hi - lo < ZONE_MIN_PTS:
        lo, hi = centre - MAP4_PAD_PTS, centre + MAP4_PAD_PTS
    z = Zone(lo, hi, "MAP4_AREA", None, as_of, label=name, extra={"peak_row_lo": peak_row_lo, "peak_volume": peak})
    return z


# ---- PO-7: delta bands --------------------------------------------------------------------------
def delta_bands(rows: Dict[float, int], as_of: datetime, profile: str, price: Optional[float] = None) -> List[Zone]:
    """rows: {row_lo: signed delta} (5-point rows). A band is 2+ adjacent rows with the same sign,
    each in the top 20% of absolute delta for that profile (ours), 10-40 points wide; same-sign bands
    that overlap or sit within 5 points merge. A run longer than 40 points keeps the 40-point window with
    the largest absolute delta sum (ours, not in the doc: logged as an ambiguity)."""
    keys = sorted(k for k, v in rows.items() if v != 0)
    if not keys:
        return []
    n_top = max(1, math.ceil(DELTA_TOP_SHARE * len(keys)))
    thr = sorted((abs(rows[k]) for k in keys), reverse=True)[n_top - 1]
    top = {k for k in keys if abs(rows[k]) >= thr}
    bands: List[Zone] = []
    run: List[float] = []

    def flush(run):
        if len(run) >= 2:
            lo, hi = run[0], run[-1] + ROW_PTS
            if hi - lo > BAND_MAX_PTS:
                w = int(BAND_MAX_PTS / ROW_PTS)
                best = max(range(len(run) - w + 1), key=lambda s: sum(abs(rows[r]) for r in run[s:s + w]))
                lo, hi = run[best], run[best + w - 1] + ROW_PTS
            sign = "SELL" if rows[run[0]] < 0 else "BUY"
            z = Zone(lo, hi, "DELTA_BAND", None, as_of, extra={"sign": sign, "profile": profile,
                                                               "delta_sum": sum(rows[r] for r in run)})
            bands.append(z)

    for k in keys:
        if k in top and run and k == run[-1] + ROW_PTS and (rows[k] > 0) == (rows[run[-1]] > 0):
            run.append(k)
        else:
            flush(run)
            run = [k] if k in top else []
    flush(run)
    # merge same-sign bands within 5 points
    merged: List[Zone] = []
    for z in sorted(bands, key=lambda z: z.lo):
        if merged and merged[-1].extra["sign"] == z.extra["sign"] and z.lo <= merged[-1].hi + MERGE_WITHIN_PTS:
            m = merged[-1]
            m.hi = max(m.hi, z.hi)
            m.extra["delta_sum"] += z.extra["delta_sum"]
        else:
            merged.append(z)
    for z in merged:
        sign = z.extra["sign"]
        z.label = f"T_DELTA_{sign}_{profile}"
        # a selling band above price is a TARGET for longs; a buying band below for shorts; else tag only
        if price is not None:
            z.extra["role"] = ("TARGET" if (sign == "SELL" and z.lo >= price) or (sign == "BUY" and z.hi <= price)
                               else "TAG_ONLY")
    return merged


# ---- PO-9: acceptance state at the value edges --------------------------------------------------
@dataclass
class AcceptanceState:
    level_name: str
    level: float
    state: str                  # ACCEPTED_BELOW | ACCEPTED_ABOVE | TESTING | INSIDE
    failed_reclaim: bool
    minutes_since_first_close: Optional[int]
    close_share: Optional[float]
    volume_share: Optional[float]
    available_at: datetime

    def tag(self) -> str:
        s = {"ACCEPTED_BELOW": "BELOW", "ACCEPTED_ABOVE": "ABOVE"}.get(self.state, self.state)
        return f"accept={s}|failed_reclaim={int(self.failed_reclaim)}"


def acceptance_state(bars: Sequence[Bar], edge: str, level: float, other_level: float, price: float,
                     as_of: datetime, name: str) -> AcceptanceState:
    """edge: 'VAL' (ACCEPTED_BELOW) or 'VAH' (ACCEPTED_ABOVE). other_level: the opposite edge.
    Uses only bars closed at or before as_of."""
    used = [b for b in bars if b.close_ct <= as_of]
    lo_edge, hi_edge = (level, other_level) if edge == "VAL" else (other_level, level)
    if lo_edge <= price <= hi_edge:
        return AcceptanceState(name, level, "INSIDE", False, None, None, None, as_of)
    outside = (price < level) if edge == "VAL" else (price > level)
    if not outside:
        return AcceptanceState(name, level, "INSIDE", False, None, None, None, as_of)
    beyond = (lambda b: b.close < level) if edge == "VAL" else (lambda b: b.close > level)
    # first close beyond it in the current excursion: scan back to the last close not beyond
    first = None
    for k in range(len(used) - 1, -1, -1):
        if beyond(used[k]):
            first = k
        else:
            break
    if first is None:
        return AcceptanceState(name, level, "TESTING", False, None, None, None, as_of)
    since = used[first:]
    minutes = int((as_of - used[first].close_ct).total_seconds() // 60)
    closes = sum(1 for b in since if beyond(b)) / len(since)
    vol_total = sum(b.volume for b in since)
    vol_beyond = sum(b.volume for b in since if beyond(b)) / vol_total if vol_total else 0.0
    accepted = minutes >= ACCEPT_MINUTES and closes >= ACCEPT_CLOSE_SHARE and vol_beyond >= ACCEPT_VOLUME_SHARE
    state = ("ACCEPTED_BELOW" if edge == "VAL" else "ACCEPTED_ABOVE") if accepted else "TESTING"
    failed = False
    if accepted:
        for b in since:
            if edge == "VAL":
                back_in = b.high >= level and b.close < level
                aggression = b.delta >= ARRIVAL_MIN_DELTA or b.imb_buy or b.large_buy
            else:
                back_in = b.low <= level and b.close > level
                aggression = -b.delta >= ARRIVAL_MIN_DELTA or b.imb_sell or b.large_sell
            if back_in and aggression:
                failed = True
    return AcceptanceState(name, level, state, failed, minutes, round(closes, 4), round(vol_beyond, 4), as_of)


# ---- PO-11: double distribution edge zone --------------------------------------------------------
def dd_edge_zone(dist_a: Tuple[float, float], separator: Tuple[float, float], dist_b: Tuple[float, float],
                 price: float, as_of: datetime, profile: str) -> Optional[Zone]:
    """dist_a / dist_b: (lo, hi) of the two high-volume distributions; separator: the thin area.
    The near edge of the FAR distribution (as seen from price) becomes a zone, at most 40 points wide,
    tagged DD_EDGE; the far distribution's opposite edge is the RUNNER candidate."""
    lower, upper = (dist_a, dist_b) if dist_a[0] < dist_b[0] else (dist_b, dist_a)
    if price <= separator[0]:
        far = upper
        lo, hi = far[0], min(far[1], far[0] + DD_EDGE_MAX_PTS)
        runner = far[1]
    elif price >= separator[1]:
        far = lower
        lo, hi = max(far[0], far[1] - DD_EDGE_MAX_PTS), far[1]
        runner = far[0]
    else:
        return None     # price inside the separator: both distributions are "far"; logged, no zone (ours)
    z = Zone(lo, hi, "DD_EDGE", None, as_of, tags=["DD_EDGE"], label=f"DD_EDGE_{profile}",
             extra={"runner": runner, "separator_lo": separator[0], "separator_hi": separator[1]})
    return z


# ---- PO-13: 08:10 vs 08:29 comparison (research) --------------------------------------------------
def compare_as_of(z0810: List[Zone], z0829: List[Zone], tol_pts: float = 2 * TICK) -> dict:
    """Zones added, dropped or moved more than 2 ticks between the two as-of times."""
    def key(z):
        return (z.kind, z.session)
    moved, same = 0, 0
    used = set()
    for a in z0810:
        match = None
        for j, b in enumerate(z0829):
            if j in used or key(a) != key(b):
                continue
            if abs(a.lo - b.lo) <= tol_pts and abs(a.hi - b.hi) <= tol_pts:
                match = j; same += 1; break
            if min(a.hi, b.hi) > max(a.lo, b.lo):
                match = j; moved += 1; break
        if match is not None:
            used.add(match)
    dropped = len(z0810) - same - moved
    added = len(z0829) - len(used)
    return {"same": same, "moved": moved, "dropped": dropped, "added": added}
