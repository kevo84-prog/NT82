r"""Book 1A Phase 1b diagnostics (book1a/specs/Phase1b_diagnostics_spec.md). Logged only.

  python -m book1a.diag_phase1b --runs book1a\Phase1\runs\phase1b --plans Book1A\Phase0\plans_phase1 \
      --gex K:\Book1A_inputs\gex_levels_block1.csv --out book1a\Phase1\runs\phase1b\diagnostics

Reads a finished Phase 1 run (A0 run folder `phase1`, R3 folder `phase1_r3`, R4 folder `phase1_r4`) read-only and
writes every diagnostic to its own files in --out. It never writes into a run folder, never edits or re-orders a
ledger, candidate log or attempt file, and nothing it computes is fed back into R1-R4 (spec section 0, rule 1-2).
Ledger columns read: phase1_checks.SAFE plus the risk-c3-v2 reference columns; never net_usd, gross_usd, R columns or
a risk-events json. Counterfactual exits are stored per trade only; nothing is aggregated by outcome (rule 4).

Every output file starts with a `#` line naming the R3 / R4 risk implementation and the sha256 of every ledger used.
Every timed field group is registered in diag_timing.csv (decision time, available_at, latest data timestamp, timing
label) for the D2 point-in-time audit (audit()).

Definitions that the spec leaves open are fixed here as "ours" and listed in OURS (reported in Phase1b_report.md).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")

VERSION = "diag-phase1b-v1.1"
TICK = 0.25
SWING_N = 15                     # AMT PO-1: strictly highest / lowest of the 15 bars before and the 15 after
PAIR_MAX_MIN = 60                # CVD_DIV pair window (spec, research assumption)
LOC_PTS = 10.0                   # "at the entry zone": inside or within 10 points (spec, ours frozen there)
SPEED_S = 60                     # BREAKOUT_SPEED window (spec)
CUE_BARS = 3
SEED = 20251205
SIX = (("call_resistance", "CR"), ("put_support", "PS"), ("hvl", "HVL"), ("call_resistance_0dte", "CR_0DTE"),
       ("put_support_0dte", "PS_0DTE"), ("hvl_0dte", "HVL_0DTE"))
CODES = ("NOT_BUILT", "NOT_RUN", "DATA_MISSING", "NOT_APPLICABLE")
OURS = [
    "CVD at a swing = the CVD at the swing bar's close (the 1-minute bar is the swing's own timestamp).",
    "Session for the primary CVD, swings and the session extreme = from 17:00 CT the previous calendar day; the second "
    "series is reset at 08:30 CT (ticks after 08:30:00) and is NOT_APPLICABLE for a swing bar closing before 08:30.",
    "Bars: 1-minute, stamped at their end, ticks in (T - 1 min, T] (jeron_engine.arms.MinuteBars convention); "
    "aggressor B = +volume, S / A = -volume (the same convention).",
    "AT_ENTRY uses swings whose confirmation bar closed at or before the decision bar close (the signal bar's own "
    "information set; the order goes 250 ms later).",
    "CVD_DIV pair = the two most recent confirmed swings of the type; the location rule is tested on the second swing; "
    "a pair more than 60 minutes apart is EXCLUDED_60MIN (counted, case still logged as raw fields).",
    "POST_ENTRY CVD_DIV (trades only): the first same-type pair whose second swing is confirmed after the decision and "
    "at or before the M0 exit.",
    "PROVISIONAL (accepted by Kyron, Nov 6): the most recent swing confirmed by the decision vs the highest high (lowest low) "
    "of the bars after that swing's confirmation bar. Window: from the bar after the confirmation bar through the signal "
    "bar. Cutoff: bar end <= the decision time (the signal bar closes at the decision; no tick after it is used). The pair "
    "window (60 minutes) and the location rule as for AT_ENTRY.",
    "BREAKOUT_SPEED: volume per second over [t - 60 s, t); percentile = share of the earlier session bar closes (from "
    "17:00 CT) whose own 60 s value is <= the decision's, x 100; 3-bar CVD change = CVD(t) - CVD(t - 3 min), ticks "
    "strictly before each time.",
    "Exit cue (a): the first 3 bars ending after the entry fill; the first qualifying bar triggers; NOT_APPLICABLE when "
    "the M0 exit time is at or before the trigger bar's close.",
    "M-J1 / M-J2 target price = the near edge of the ladder target zone (long: its low; short: its high). Ladders exist "
    "only in Book 1A plans, so all R1-R3 trades (A0 plans) are NOT_APPLICABLE (no ladder). R4 trades from a plan zone use "
    "that zone's ladder; R4 trades from an intraday zone admitted by L1 use the admitting plan DECISION zone's ladder in "
    "the trade's direction (amendment Nov 6, 2026, Kyron), with mj_alignment PLAN_ALIGNED / EXPLORATORY_NOT_PLAN_ALIGNED; "
    "no ladder in that direction = NOT_APPLICABLE. A ladder target not beyond the fill is NOT_APPLICABLE (target behind entry).",
    "Sizing stop ticks = the risk-c3-v2 reference (best ask long / best bid short at the decision) to the stop.",
    "MNQ diagnostic covers R3 / R4 attempts rejected with RISK_REJECT:PER_TRADE_BUDGET or RISK_REJECT:DAILY_BUDGET.",
    "V2 random twin: rng = numpy default_rng(20251205 + yyyymmdd as an integer); one side draw (0 = below, 1 = above "
    "ref) per level in the order CR, PS, HVL, CR_0DTE, PS_0DTE, HVL_0DTE. ref_price = the last trade at or before "
    "08:10:00 CT. The P1.1 gamma-rank levels (GAMMA*) are not among the six and stay as they are in every twin set.",
    "hvl_side price = the last trade at or before the decision; AT = within 1 tick.",
    "L1_PLAN_SIDE: the admitting plan zone = the DECISION zone of the R4 run's staged plan with the smallest distance by the "
    "arms.l1 rule (first in file order on a tie); candidates before the plan as-of (08:25 CT) are NOT_APPLICABLE; a plan "
    "side other than ANY / RESPONSE / INITIATION / NONE is DATA_MISSING.",
    "pin_zone price = the last trade at or before the decision (the same as hvl_side); pin strike in the chart contract "
    "(+ nt_shift_pts).",
    "Volatility terciles: rank of atm_iv among the phase's sessions, tercile = ceil(3 x rank / n); a post-phase reporting "
    "grouping only (POST_PHASE_GROUPING), never an AT_ENTRY field.",
]


# ------------------------------------------------------------------ data
class TapeFull:
    def __init__(self, path: Path):
        df = pd.read_csv(path, usecols=[0, 1, 2, 3, 4, 5], header=0, names=["t", "p", "b", "a", "v", "s"], dtype={"t": str, "s": str})
        self.t = pd.to_datetime(df["t"].str.slice(0, 26), format="%Y-%m-%d %H:%M:%S.%f").to_numpy().astype("datetime64[us]")
        self.p = df["p"].to_numpy(float); self.b = df["b"].fillna(0).to_numpy(float); self.a = df["a"].fillna(0).to_numpy(float)
        self.v = df["v"].fillna(0).to_numpy(np.int64)
        s = df["s"].fillna("").str.strip()
        self.sg = np.where(s == "B", 1, np.where(s.isin(["S", "A"]), -1, 0)).astype(np.int64)

    def i_right(self, t) -> int:
        return int(np.searchsorted(self.t, np.datetime64(t, "us"), side="right"))

    def i_left(self, t) -> int:
        return int(np.searchsorted(self.t, np.datetime64(t, "us"), side="left"))

    def quote_at(self, t):
        i = self.i_right(t) - 1
        return (self.b[i], self.a[i], self.t[i].astype(dt.datetime)) if i >= 0 else (np.nan, np.nan, None)

    def last_trade(self, t):
        i = self.i_right(t) - 1
        return (float(self.p[i]), self.t[i].astype(dt.datetime)) if i >= 0 else (np.nan, None)


def ts64(x) -> np.datetime64:
    return np.datetime64(pd.Timestamp(x), "us")


class Day:
    """One session: ticks from 17:00 CT the previous day to 15:00 CT; 1-minute bars; CVD (two resets); swings."""

    def __init__(self, tape: TapeFull, d: dt.date, end_time=dt.time(15, 0)):
        self.d = d
        self.start = dt.datetime.combine(d - dt.timedelta(days=1), dt.time(17, 0))
        self.rth = dt.datetime.combine(d, dt.time(8, 30))
        self.end = dt.datetime.combine(d, end_time)
        i0, i1 = tape.i_right(self.start), tape.i_right(self.end)
        self.i0 = i0
        t, p, v, sg = tape.t[i0:i1], tape.p[i0:i1], tape.v[i0:i1], tape.sg[i0:i1]
        self.tt = t
        self.cum_p = np.cumsum(v * sg)                                   # CVD, primary reset 17:00 CT
        rth_mask = t > np.datetime64(self.rth, "us")
        self.cum_r = np.cumsum(np.where(rth_mask, v * sg, 0))            # CVD, second series reset 08:30 CT
        self.cum_v = np.cumsum(v)
        self.has_rth = rth_mask
        # bars stamped at their end: ticks in (T - 1 min, T]
        ends = t.astype("datetime64[m]")
        ends = np.where(t > ends.astype("datetime64[us]"), ends + np.timedelta64(1, "m"), ends).astype("datetime64[m]")
        df = pd.DataFrame(dict(end=ends, p=p, v=v, d=v * sg, k=np.arange(len(t))))
        g = df.groupby("end", sort=True)
        bars = pd.DataFrame(dict(o=g.p.first(), h=g.p.max(), l=g.p.min(), c=g.p.last(), vol=g.v.sum(), delta=g.d.sum(), last=g.k.last()))
        bars.index = bars.index.astype("datetime64[us]")
        self.bars = bars
        self.end_t = bars.index.to_numpy()
        last = bars["last"].to_numpy()
        self.b_cvd_p = self.cum_p[last].astype(float)
        self.b_cvd_r = np.where(self.end_t >= np.datetime64(self.rth, "us"), self.cum_r[last], np.nan).astype(float)
        self.b_cvd_r[self.end_t == np.datetime64(self.rth, "us")] = 0.0
        self.h, self.l = bars.h.to_numpy(), bars.l.to_numpy()
        self.o, self.c, self.delta = bars.o.to_numpy(), bars.c.to_numpy(), bars.delta.to_numpy()
        self.hi_sofar, self.lo_sofar = np.maximum.accumulate(self.h), np.minimum.accumulate(self.l)
        self.swings = find_swings(self.h, self.l, self.end_t)
        # volume per second over [e - 60 s, e) at every bar end (BREAKOUT_SPEED reference set)
        self.vps_end = np.array([self.vol_between(pd.Timestamp(e).to_pydatetime() - dt.timedelta(seconds=SPEED_S),
                                                  pd.Timestamp(e).to_pydatetime()) / SPEED_S for e in self.end_t])

    def cvd_before(self, t, reset="P") -> float:
        """CVD from ticks strictly before t."""
        k = int(np.searchsorted(self.tt, np.datetime64(t, "us"), side="left")) - 1
        if k < 0:
            return 0.0
        if reset == "R":
            return float(self.cum_r[k]) if t > self.rth else np.nan
        return float(self.cum_p[k])

    def vol_between(self, t0, t1) -> int:
        """Executed volume in [t0, t1)."""
        a = int(np.searchsorted(self.tt, np.datetime64(t0, "us"), side="left"))
        b = int(np.searchsorted(self.tt, np.datetime64(t1, "us"), side="left"))
        if b <= a:
            return 0
        return int(self.cum_v[b - 1] - (self.cum_v[a - 1] if a > 0 else 0))

    def swing_dict(self, i, kind) -> dict:
        return dict(kind=kind, i=i, t=pd.Timestamp(self.end_t[i]).to_pydatetime(),
                    confirm_t=pd.Timestamp(self.end_t[i + SWING_N]).to_pydatetime(),
                    price=float(self.h[i] if kind == "HIGH" else self.l[i]),
                    cvd_p=float(self.b_cvd_p[i]), cvd_r=float(self.b_cvd_r[i]))


def find_swings(h, l, ends) -> List[tuple]:
    """(bar index, 'HIGH'|'LOW'): strictly the highest (lowest) of the 15 bars before and the 15 after."""
    out = []
    n = len(h)
    for i in range(SWING_N, n - SWING_N):
        if h[i] > h[i - SWING_N:i].max() and h[i] > h[i + 1:i + 1 + SWING_N].max():
            out.append((i, "HIGH"))
        if l[i] < l[i - SWING_N:i].min() and l[i] < l[i + 1:i + 1 + SWING_N].min():
            out.append((i, "LOW"))
    return out


# ------------------------------------------------------------------ CVD_DIV (pure)
def classify(kind: str, p1: float, p2: float, c1: float, c2: float) -> str:
    if any(x is None or (isinstance(x, float) and np.isnan(x)) for x in (p1, p2, c1, c2)):
        return "NOT_APPLICABLE"
    if kind == "HIGH":
        if p2 < p1 and c2 > c1: return "HIGH_ABSORPTION"
        if p2 > p1 and c2 < c1: return "HIGH_EXHAUSTION"
    else:
        if p2 < p1 and c2 > c1: return "LOW_EXHAUSTION"
        if p2 > p1 and c2 < c1: return "LOW_ABSORPTION"
    return "NONE"


def with_against(case: str, side: int) -> str:
    if not case.startswith(("HIGH_", "LOW_")):
        return ""
    favours = -1 if case.startswith("HIGH_") else 1
    return "WITH" if favours == side else "AGAINST"


def location(day: Day, s2: dict, zone_lo: Optional[float], zone_hi: Optional[float]) -> str:
    if zone_lo is not None and zone_lo - LOC_PTS <= s2["price"] <= zone_hi + LOC_PTS:
        return "ZONE"
    i = s2["i"]
    if s2["kind"] == "HIGH" and s2["price"] >= day.hi_sofar[i]: return "SESSION_EXTREME"
    if s2["kind"] == "LOW" and s2["price"] <= day.lo_sofar[i]: return "SESSION_EXTREME"
    return "NOT_AT_LOCATION"


def pair_fields(day: Day, s1: dict, s2: dict, side: int, zone_lo, zone_hi, prefix: str) -> dict:
    gap = (s2["t"] - s1["t"]).total_seconds() / 60.0
    loc = location(day, s2, zone_lo, zone_hi)
    out = {f"{prefix}_s1_time": s1["t"], f"{prefix}_s1_confirm": s1["confirm_t"], f"{prefix}_s1_price": s1["price"],
           f"{prefix}_s2_time": s2["t"], f"{prefix}_s2_confirm": s2.get("confirm_t"), f"{prefix}_s2_price": s2["price"],
           f"{prefix}_s1_cvd17": s1["cvd_p"], f"{prefix}_s2_cvd17": s2["cvd_p"], f"{prefix}_s1_cvd0830": s1["cvd_r"],
           f"{prefix}_s2_cvd0830": s2["cvd_r"], f"{prefix}_gap_min": round(gap, 2), f"{prefix}_location": loc}
    for tag, k in (("cvd17", "cvd_p"), ("cvd0830", "cvd_r")):
        raw = classify(s1["kind"], s1["price"], s2["price"], s1[k], s2[k])
        if gap > PAIR_MAX_MIN:
            st = "EXCLUDED_60MIN"
        elif loc == "NOT_AT_LOCATION":
            st = "NOT_AT_LOCATION"
        else:
            st = raw
        out[f"{prefix}_raw_case_{tag}"] = raw
        out[f"{prefix}_case_{tag}"] = st
        out[f"{prefix}_with_{tag}"] = with_against(st, side)
    return out


def at_entry(day: Day, kind: str, t: dt.datetime, side: int, zone_lo, zone_hi) -> dict:
    pre = f"atentry_{kind.lower()}"
    conf = [day.swing_dict(i, k) for i, k in day.swings if k == kind and i + SWING_N < len(day.end_t)]
    conf = [s for s in conf if s["confirm_t"] <= t]
    if len(conf) < 2:
        return {f"{pre}_case_cvd17": "NOT_APPLICABLE", f"{pre}_case_cvd0830": "NOT_APPLICABLE", f"{pre}_note": f"{len(conf)} confirmed swings",
                "_data_max": max([s["confirm_t"] for s in conf], default=None)}
    out = pair_fields(day, conf[-2], conf[-1], side, zone_lo, zone_hi, pre)
    out["_data_max"] = conf[-1]["confirm_t"]
    return out


def provisional(day: Day, kind: str, t: dt.datetime, side: int, zone_lo, zone_hi) -> dict:
    pre = f"prov_{kind.lower()}"
    conf = [day.swing_dict(i, k) for i, k in day.swings if k == kind and i + SWING_N < len(day.end_t)]
    conf = [s for s in conf if s["confirm_t"] <= t]
    j = int(np.searchsorted(day.end_t, np.datetime64(t, "us"), side="right")) - 1     # entry bar (ends <= t)
    if not conf or j < 0 or j <= conf[-1]["i"] + SWING_N:
        return {f"{pre}_case_cvd17": "NOT_APPLICABLE", f"{pre}_case_cvd0830": "NOT_APPLICABLE", "_data_max": None}
    s1 = conf[-1]
    seg = range(s1["i"] + SWING_N + 1, j + 1)          # bars after the first swing's confirmation bar
    k = max(seg, key=lambda x: day.h[x]) if kind == "HIGH" else min(seg, key=lambda x: day.l[x])
    s2 = dict(kind=kind, i=k, t=pd.Timestamp(day.end_t[k]).to_pydatetime(), confirm_t=None,
              price=float(day.h[k] if kind == "HIGH" else day.l[k]), cvd_p=float(day.b_cvd_p[k]), cvd_r=float(day.b_cvd_r[k]))
    out = pair_fields(day, s1, s2, side, zone_lo, zone_hi, pre)
    out["_data_max"] = pd.Timestamp(day.end_t[j]).to_pydatetime()
    return out


def post_entry(day: Day, kind: str, t: dt.datetime, t_exit: Optional[dt.datetime], side: int, zone_lo, zone_hi) -> dict:
    pre = f"post_{kind.lower()}"
    sw = [day.swing_dict(i, k) for i, k in day.swings if k == kind and i + SWING_N < len(day.end_t)]
    for a, b in zip(sw, sw[1:]):
        if b["confirm_t"] > t and (t_exit is None or b["confirm_t"] <= t_exit):
            out = pair_fields(day, a, b, side, zone_lo, zone_hi, pre)
            out["_avail"] = b["confirm_t"]
            return out
    return {f"{pre}_case_cvd17": "NOT_APPLICABLE", f"{pre}_case_cvd0830": "NOT_APPLICABLE", "_avail": None}


def breakout_speed(day: Day, t: dt.datetime) -> dict:
    vps = day.vol_between(t - dt.timedelta(seconds=SPEED_S), t) / SPEED_S
    ref = day.vps_end[day.end_t < np.datetime64(t, "us")]
    pct = round(100.0 * float((ref <= vps).sum()) / len(ref), 2) if len(ref) else np.nan
    return dict(bs_vol_per_sec_60s=round(vps, 4), bs_percentile_session=pct, bs_n_earlier_bars=len(ref),
                bs_cvd_change_3bar=day.cvd_before(t) - day.cvd_before(t - dt.timedelta(minutes=3)))


# ------------------------------------------------------------------ exits
def cue_a(day: Day, tape: TapeFull, side: int, t_fill: dt.datetime, m0_exit: Optional[dt.datetime]) -> dict:
    after = [k for k in range(len(day.end_t)) if pd.Timestamp(day.end_t[k]).to_pydatetime() > t_fill][:CUE_BARS]
    trig = None
    for k in after:
        d_ok = day.delta[k] > 0 if side > 0 else day.delta[k] < 0
        c_against = day.c[k] < day.o[k] if side > 0 else day.c[k] > day.o[k]
        if d_ok and c_against:
            trig = k; break
    out = dict(cue_timing="POST_ENTRY", cue_bars_checked=len(after))
    if trig is None:
        out.update(cue_fired="N", cue_status="OK" if len(after) == CUE_BARS else "DATA_MISSING")
        out["_avail"] = pd.Timestamp(day.end_t[after[-1]]).to_pydatetime() if after else None
        return out
    te = pd.Timestamp(day.end_t[trig]).to_pydatetime()
    out.update(cue_trigger_bar=te, _avail=te)
    if m0_exit is not None and m0_exit <= te:
        out.update(cue_fired="NOT_APPLICABLE", cue_status="NOT_APPLICABLE")
        return out
    for ms, tag in ((250, ""), (1000, "_1000ms")):
        b, a, _ = tape.quote_at(te + dt.timedelta(milliseconds=ms))
        out[f"cue_exit_time{tag}"] = te + dt.timedelta(milliseconds=ms)
        out[f"cue_exit_price{tag}"] = float(b if side > 0 else a)
    out.update(cue_fired="Y", cue_status="OK")
    return out


def ladder_for(plans: Path, day: str, label: str, side: str) -> Optional[dict]:
    f = plans / f"PreopenPlan_{day}_book1a.txt"
    if not f.exists():
        return None
    for line in f.read_text().splitlines():
        if line.startswith("ladder="):
            p = line[7:].split("|")
            if p[0] == label and p[1] == side:
                kv = dict(x.split("=", 1) for x in p[2:] if "=" in x)
                return {k: kv.get(k, "") for k in ("TP1", "TP2", "RUN")}
    return None


def mj_alignment(l1_side: str) -> str:
    """Amendment Nov 6, 2026: PLAN_ALIGNED when l1_side_inherited = ALLOWED; EXPLORATORY_NOT_PLAN_ALIGNED for NONE or MISMATCH."""
    if l1_side == "ALLOWED":
        return "PLAN_ALIGNED"
    if l1_side in ("NONE", "MISMATCH"):
        return "EXPLORATORY_NOT_PLAN_ALIGNED"
    return f"DATA_MISSING (l1_side_inherited {l1_side})"


def mj_ladder_source(strategy: str, cand: dict, l1_row: Optional[dict], plans: Path, day: str, side: int):
    """Which ladder M-J1 / M-J2 use (amendment Nov 6, 2026). Returns (ladder or None, fields).
    R4 trade from a plan zone: that zone's ladder (unchanged). R4 trade from an intraday zone admitted by L1: the admitting
    plan DECISION zone's ladder in the trade's direction, with mj_alignment and that zone's long= / short=. Else no ladder."""
    sd = "long" if side > 0 else "short"
    if strategy != "R4":
        return None, dict(mj_zone_source="NOT_APPLICABLE (A0 plans carry no ladder)", mj_alignment="NOT_APPLICABLE (A0 plans carry no ladder)")
    lt, lid = cand.get("LocationType", ""), cand.get("LocationId", "")
    if lt.startswith("FROZEN_PREOPEN") and lid.startswith("P_"):
        lab = re.sub(r"_\d+$", "", lid[2:])
        return ladder_for(plans, day, lab, sd), dict(mj_zone_source="PLAN_ZONE", mj_zone_label=lab,
                                                     mj_alignment="NOT_APPLICABLE (plan-zone trade)")
    if l1_row is not None:
        lab, inh = l1_row["plan_zone_label"], l1_row["l1_side_inherited"]
        return ladder_for(plans, day, lab, sd), dict(mj_zone_source="L1_ADMITTING_PLAN_ZONE", mj_zone_label=lab,
                                                     mj_alignment=mj_alignment(inh), mj_l1_side_inherited=inh,
                                                     mj_plan_long=l1_row["plan_long"], mj_plan_short=l1_row["plan_short"])
    return None, dict(mj_zone_source="NOT_APPLICABLE (not a plan zone and not admitted by L1)",
                      mj_alignment="NOT_APPLICABLE (not a plan zone and not admitted by L1)")


def near_edge(rng: str, side: int) -> Optional[float]:
    if not rng:
        return None
    lo, hi = (float(x) for x in rng.split("-"))
    return lo if side > 0 else hi


def mj1_choice(lad: dict) -> Optional[tuple]:
    for k in ("RUN", "TP2", "TP1"):
        if lad.get(k):
            return k, lad[k]
    return None


def size_bucket(n: int) -> str:
    return "NOT_APPLICABLE" if n < 2 else ("2" if n == 2 else "3" if n == 3 else "4+")


# ------------------------------------------------------------------ sizing (pure)
def nq_risk_cents(stop_ticks: int, n: int) -> int:
    return (stop_ticks + 2) * 500 * n + 574 * n


def mnq_risk_cents(stop_ticks: int, m: int) -> int:
    return (stop_ticks + 2) * 50 * m + 188 * m


def max_mnq(stop_ticks: int, cap_cents: int = 100_000) -> int:
    m = 0
    while mnq_risk_cents(stop_ticks, m + 1) <= cap_cents:
        m += 1
    return m


# ------------------------------------------------------------------ GEX (pure)
def twins(levels: Dict[str, float], ref: float, session: str) -> Dict[str, Dict[str, float]]:
    rng = np.random.default_rng(SEED + int(session.replace("-", "")))
    rnd, rnd_side, rnd100 = {}, {}, {}
    for _, name in SIX:
        draw = int(rng.integers(0, 2))                     # drawn for every level, in order, even if the level is blank
        v = levels.get(name)
        if v is None:
            continue
        dist = abs(v - ref)
        rnd[name] = ref + dist if draw == 1 else ref - dist
        rnd_side[name] = "ABOVE" if draw == 1 else "BELOW"
        rnd100[name] = round(v / 100.0) * 100.0
    return dict(random=rnd, random_side=rnd_side, round=rnd100)


def gex_present(lo: float, hi: float, levels: Dict[str, float], keep_gamma: bool) -> bool:
    return keep_gamma or any(lo - 10.0 <= v <= hi + 10.0 for v in levels.values())


def hvl_side(price: float, hvl: Optional[float]) -> str:
    if hvl is None or np.isnan(price):
        return "DATA_MISSING"
    if abs(price - hvl) <= TICK + 1e-9:
        return "AT"
    return "ABOVE" if price > hvl else "BELOW"


PIN_NOT_RUN = ("NOT_RUN (inputs: no 0DTE open-interest strike in gex_levels_block1.csv; per-strike data not reachable "
               "through K:\\Book1A_inputs)")
PC_NOT_RUN = "NOT_RUN (inputs: put / call gamma of the replica calculation not reachable through K:\\Book1A_inputs)"


def gex_tags(g: Optional[dict], px: float, t: dt.datetime, v3: Optional[dict] = None) -> dict:
    """Context GEX tags (AT_ENTRY): hvl_side, cr_ps_width, pin_zone, pc_gamma_ratio (spec section 5).
    v3 = the session's gex_v3 row (pin_strike_0dte_nt, pc_gamma_ratio); None -> NOT_RUN (inputs)."""
    out = {}
    if g and g.get("ok") == "True":
        hv = g.get("hvl_nt") or g.get("hvl")
        out["hvl_side"] = hvl_side(px, float(hv) if hv else None)
        cr, ps = g.get("call_resistance_nt") or g.get("call_resistance"), g.get("put_support_nt") or g.get("put_support")
        out["cr_ps_width"] = float(cr) - float(ps) if cr and ps else "DATA_MISSING"
    else:
        out.update(hvl_side="NOT_APPLICABLE (gex_valid N)", cr_ps_width="NOT_APPLICABLE (gex_valid N)")
    if t.hour < 13:
        out["pin_zone"] = "NOT_APPLICABLE (before 13:00 CT)"
    elif v3 is None:
        out["pin_zone"] = PIN_NOT_RUN
    elif not np.isfinite(float(v3.get("pin_strike_0dte_nt", np.nan))):
        out["pin_zone"] = "DATA_MISSING (no 0DTE open interest)"
    else:
        k = float(v3["pin_strike_0dte_nt"])
        out.update(pin_strike_nt=k, pin_distance_pts=round(px - k, 2), pin_zone="Y" if abs(px - k) <= 10.0 + 1e-9 else "N")
    out["pc_gamma_ratio"] = PC_NOT_RUN if v3 is None else float(v3["pc_gamma_ratio"])
    return out


def l1_side_inherited(plan_side: str, setup_family: str) -> str:
    """Spec 5b: ALLOWED (ANY, or the plan side names this setup family), NONE, MISMATCH (only the other family)."""
    v = (plan_side or "").strip().upper()
    if v == "ANY" or (v in ("RESPONSE", "INITIATION") and v == setup_family.upper()):
        return "ALLOWED"
    if v == "NONE":
        return "NONE"
    if v in ("RESPONSE", "INITIATION"):
        return "MISMATCH"
    return f"DATA_MISSING (plan side '{plan_side}')"


def plan_decision_zones(plan_txt: Path) -> list:
    """DECISION zones of a plan text in file order: (lo, hi, label, long, short) (arms.l1 reads the same lines)."""
    out = []
    for line in plan_txt.read_text(encoding="utf-8").splitlines():
        if line.startswith("zone=") and "|DECISION|" in line:
            p = line[5:].split("|")
            lo, hi = (float(x) for x in p[0].split("-"))
            kv = dict(x.split("=", 1) for x in p[3:] if "=" in x)
            out.append((lo, hi, p[1], kv.get("long", ""), kv.get("short", "")))
    return out


def l1_admitting_zone(zones: list, lo: float, hi: float):
    """The plan DECISION zone with the smallest distance (arms.l1.dist rule; first in file order on a tie)."""
    best = None
    for z in zones:
        a, b = z[0], z[1]
        x = 0.0 if (lo <= b and hi >= a) else (a - hi if hi < a else lo - b)
        if best is None or x < best[0]:
            best = (x, z)
    return best


def mj2_split(n: int) -> Optional[tuple]:
    """M-J2 legs (qty at TP1, qty to the M-J1 target); None for a 1 NQ trade (NOT_APPLICABLE)."""
    return None if n < 2 else (1, n - 1)


def tod_bucket(t: dt.datetime) -> str:
    m = t.hour * 60 + t.minute
    return "08:30-08:45" if m < 8 * 60 + 45 else "08:45-10:00" if m < 600 else "10:00-13:00" if m < 780 else "after 13:00"


# ------------------------------------------------------------------ io
def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Out:
    def __init__(self, out: Path, header: str):
        self.out, self.header = out, header
        self.timing: List[dict] = []

    def csv(self, name: str, rows: List[dict]):
        cols = list(dict.fromkeys(k for r in rows for k in r if not k.startswith("_"))) or ["none"]
        with open(self.out / name, "w", newline="", encoding="utf-8") as f:
            f.write(self.header + "\n")
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
            for r in rows:
                w.writerow({k: ("" if v is None else v) for k, v in r.items() if not k.startswith("_")})

    def time(self, file, key, group, timing, decision_t, available_at, data_max):
        self.timing.append(dict(file=file, key=key, group=group, timing=timing, decision_t=decision_t,
                                available_at=available_at, data_max_t=data_max))


def ledger(p: Path) -> pd.DataFrame:
    from book1a import phase1_checks as P
    cols = P.SAFE + ["risk_impl_version", "risk_entry_ref", "risk_decision_time"]
    return pd.read_csv(p, usecols=lambda c: c in cols, dtype={"entry_time": str, "exit_time": str, "risk_decision_time": str})


def tm(day: str, hms) -> Optional[dt.datetime]:
    if not isinstance(hms, str) or not hms:
        return None
    return pd.Timestamp(f"{day} {hms}").to_pydatetime()


# ------------------------------------------------------------------ main
def run(runs: Path, plans: Path, gex_csv: Path, out: Path, d5_days=("2025-10-24", "2025-10-27", "2025-10-28", "2025-10-29"),
        inputs: Optional[Path] = None):
    import os
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, exit_replay as XR
    from book1a import lookahead as LA
    out.mkdir(parents=True, exist_ok=True)
    a0, r3, r4 = runs / "phase1", runs / "phase1_r3", runs / "phase1_r4"
    files = {"R1": a0 / "R1_A0_full.csv", "R2": a0 / "R2_C1_full.csv", "R3": r3 / "R3_M0_ledger.csv", "R4": r4 / "R4_M0_ledger.csv"}
    hashes = {k: sha(v) for k, v in files.items()}
    impl = {k: json.loads((d / "run_manifest.json").read_text()).get("risk_impl_version") for k, d in (("R3", r3), ("R4", r4))}
    try:
        import subprocess
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=Path(__file__).resolve().parents[1]).strip()
    except Exception:
        commit = "n/a"
    header = (f"# Book 1A Phase 1b {VERSION} | code {commit} | R1 ledger sha256 {hashes['R1']} | R2 ledger sha256 {hashes['R2']} | "
              f"R3 {impl['R3']} ledger sha256 {hashes['R3']} | R4 {impl['R4']} ledger sha256 {hashes['R4']} | logged only, no P&L")
    O = Out(out, header)
    tape = TapeFull(a0 / "tape_strategy.csv.gz")
    sessions = json.loads((a0 / "daily_loop_config.json").read_text())["sessions"]
    days = {d: Day(tape, dt.date.fromisoformat(d)) for d in sorted(set(sessions) | set(d5_days))}
    logs = {"A0": AR.Log(a0), "R4": AR.Log(r4)}
    bars = {"A0": A.MinuteBars(a0 / "tape_strategy.csv.gz"), "R4": A.MinuteBars(r4 / "tape_strategy.csv.gz")}
    t8 = {k: A.t8(logs[k], bars[k]) for k in logs}
    led = {k: ledger(v) for k, v in files.items()}
    log_of = {"R1": "A0", "R2": "A0", "R3": "A0", "R4": "R4"}

    # ---------- per candidate (CVD_DIV, PROVISIONAL, BREAKOUT_SPEED, overlaps) ----------
    cand_rows = []
    keep = ["trapped_passive", "trapped_passive_kind", "delta_pct_vs_session", "delta_pct_session_avg", "delta_rank_20", "DeltaPct", "cvd_slope_5", "Grade"]
    for lk, log in logs.items():
        seen = set()
        for r in log.rows:
            if r["RecordType"] != "CANDIDATE" or r["EventId"] in seen:
                continue
            day_s = r["EvidenceTimeCT"][:10]
            if day_s not in sessions:
                continue
            seen.add(r["EventId"])
            t = pd.Timestamp(r["EvidenceTimeCT"]).to_pydatetime()
            side = 1 if r["Direction"] == "Long" else -1
            zl, zh = (float(r["ZoneLo"]), float(r["ZoneHi"])) if r["ZoneLo"] and r["ZoneHi"] else (None, None)
            dy = days[day_s]
            row = dict(log=lk, strategies="R1,R2,R3" if lk == "A0" else "R4", session=day_s, event=r["EventId"], decision_time=t,
                       direction=r["Direction"], setup_family=r["SetupFamily"], status=r["CandidateStatus"], zone_lo=zl, zone_hi=zh,
                       cvd_div_timing_atentry="AT_ENTRY", cvd_div_timing_prov="PROVISIONAL", available_at=t)
            for kind in ("HIGH", "LOW"):
                x = at_entry(dy, kind, t, side, zl, zh); dm = x.pop("_data_max"); row.update(x)
                O.time("diag_cvd_candidates.csv", f"{lk}:{r['EventId']}", f"atentry_{kind}", "AT_ENTRY", t, t, dm)
                x = provisional(dy, kind, t, side, zl, zh); dm = x.pop("_data_max"); row.update(x)
                O.time("diag_cvd_candidates.csv", f"{lk}:{r['EventId']}", f"prov_{kind}", "PROVISIONAL", t, t, dm)
            if r["SetupFamily"] == "INITIATION":
                row.update(breakout_speed(dy, t)); row["bs_status"] = "OK"
                O.time("diag_cvd_candidates.csv", f"{lk}:{r['EventId']}", "breakout_speed", "AT_ENTRY", t, t,
                       pd.Timestamp(tape.t[tape.i_left(t) - 1]).to_pydatetime())
            else:
                row["bs_status"] = "NOT_APPLICABLE"
            row["t8_overlap"] = "Y" if t8[lk](r) else "N"
            for k in keep:
                row[f"log_{k}"] = r.get(k, "")
            row["grade_without_cvd"] = "NOT_RUN (harness: the S1.4 grade is computed in the harness C# code; recomputing it needs a harness change, which is not allowed)"
            cand_rows.append(row)
    O.csv("diag_cvd_candidates.csv", cand_rows)

    # ---------- GEX inputs that need per-strike gamma (gex_v3; None -> NOT_RUN (inputs)) ----------
    v3 = None
    if inputs is not None:
        from book1a import gex_v3 as GV
        v3 = {r_["session"]: r_ for r_ in GV.run(Path(inputs), sessions, out)}
        O.csv("diag_gex_v3_sessions.csv", list(v3.values()))
        bad = [k_ for k_, r_ in v3.items() if r_["repro_all_match"] != "Y"]
        if bad:
            raise RuntimeError(f"gex_v3 does not reproduce gex_levels_block1.csv on {bad}; stop")

    def v3_avail_ct(d_):
        r_ = v3[d_]
        mx = max(pd.Timestamp(r_["oi_max_ts_recv"]), pd.Timestamp(r_["settle_max_ts_recv"]))
        return mx.tz_convert(CT).tz_localize(None).to_pydatetime(),             pd.Timestamp(r_["cutoff_utc"]).tz_convert(CT).tz_localize(None).to_pydatetime()

    # ---------- L1_PLAN_SIDE (spec 5b): R4 candidates / trades from an intraday zone admitted by L1 ----------
    l1rows = []
    r4_trades = set(led["R4"].trade_id)
    seen = set()
    for r in logs["R4"].rows:
        if r["RecordType"] != "CANDIDATE" or r["EventId"] in seen or r["EvidenceTimeCT"][:10] not in sessions:
            continue
        seen.add(r["EventId"])
        if not A.intraday(r) or not r["ZoneLo"] or not r["ZoneHi"]:
            continue
        d_ = r["EvidenceTimeCT"][:10]
        t = pd.Timestamp(r["EvidenceTimeCT"]).to_pydatetime()
        zs = plan_decision_zones(r4 / "plans" / f"PreopenPlan_{d_}.txt")
        best = l1_admitting_zone(zs, float(r["ZoneLo"]), float(r["ZoneHi"]))
        if best is None or best[0] > 10.0 + 1e-9:
            continue                                    # vetoed by L1: not admitted
        dist, z = best
        side = "long" if r["Direction"] == "Long" else "short"
        asof = dt.datetime.combine(t.date(), dt.time(8, 25))
        row = dict(strategy="R4", risk_impl_version=impl["R4"], ledger_sha256=hashes["R4"], session=d_, event=r["EventId"],
                   is_trade="Y" if r["EventId"] in r4_trades else "N", decision_time=t, direction=r["Direction"],
                   setup_family=r["SetupFamily"], status=r["CandidateStatus"], intraday_zone=r["LocationId"],
                   intraday_lo=float(r["ZoneLo"]), intraday_hi=float(r["ZoneHi"]), plan_zone_label=z[2], plan_zone_lo=z[0],
                   plan_zone_hi=z[1], distance_pts=round(dist, 2), plan_long=z[3], plan_short=z[4], timing="AT_ENTRY")
        if t < asof:
            row["l1_side_inherited"] = "NOT_APPLICABLE (before the plan as-of 08:25 CT)"
        else:
            row["l1_side_inherited"] = l1_side_inherited(z[3] if side == "long" else z[4], r["SetupFamily"])
            O.time("diag_l1_plan_side.csv", f"R4:{r['EventId']}", "l1_plan_side", "AT_ENTRY", t, t, asof)
        l1rows.append(row)
    O.csv("diag_l1_plan_side.csv", l1rows)
    l1map = {x["event"]: x for x in l1rows}

    # ---------- per trade: CVD (AT_ENTRY / PROVISIONAL / POST_ENTRY), exits, sizing, GEX tags ----------
    gex = {r["session"]: r for r in csv.DictReader(open(gex_csv, newline="", encoding="utf-8-sig"))}
    cvd_tr, exit_tr, size_tr, gex_tr = [], [], [], []
    for k, df in led.items():
        log = logs[log_of[k]]
        cmap = {}
        for r in log.rows:
            if r["RecordType"] == "CANDIDATE" and r["EventId"] not in cmap:
                cmap[r["EventId"]] = r
        for r in df.itertuples():
            day_s = r.date
            dy = days[day_s]
            side = 1 if str(r.side).upper().startswith("L") else -1
            t_fill = tm(day_s, r.entry_time)
            t = t_fill - dt.timedelta(milliseconds=250)
            t_exit = tm(day_s, r.exit_time)
            c = cmap.get(r.trade_id, {})
            zl, zh = (float(c["ZoneLo"]), float(c["ZoneHi"])) if c.get("ZoneLo") and c.get("ZoneHi") else (None, None)
            key = f"{k}:{r.trade_id}"
            base = dict(strategy=k, risk_impl_version=impl.get(k, "N/A (Book 1 sizing, qty 1)"), ledger_sha256=hashes[k],
                        session=day_s, trade_id=r.trade_id, side=r.side, qty=int(r.qty), decision_time=t)
            # CVD
            row = dict(base)
            for kind in ("HIGH", "LOW"):
                x = at_entry(dy, kind, t, side, zl, zh); dm = x.pop("_data_max"); row.update(x)
                O.time("diag_cvd_trades.csv", key, f"atentry_{kind}", "AT_ENTRY", t, t, dm)
                x = provisional(dy, kind, t, side, zl, zh); dm = x.pop("_data_max"); row.update(x)
                O.time("diag_cvd_trades.csv", key, f"prov_{kind}", "PROVISIONAL", t, t, dm)
                x = post_entry(dy, kind, t, t_exit, side, zl, zh); av = x.pop("_avail"); row.update(x)
                row[f"post_{kind.lower()}_timing"] = "POST_ENTRY"
                O.time("diag_cvd_trades.csv", key, f"post_{kind}", "POST_ENTRY", t, av, av)
            if c.get("SetupFamily") == "INITIATION":
                row.update(breakout_speed(dy, t)); row["bs_status"] = "OK"
                O.time("diag_cvd_trades.csv", key, "breakout_speed", "AT_ENTRY", t, t, pd.Timestamp(tape.t[tape.i_left(t) - 1]).to_pydatetime())
            else:
                row["bs_status"] = "NOT_APPLICABLE"
            cvd_tr.append(row)
            # exits (POST_ENTRY counterfactuals, per trade only)
            e = dict(base, timing="POST_ENTRY")
            x = cue_a(dy, tape, side, t_fill, t_exit); av = x.pop("_avail"); e.update(x)
            O.time("diag_exit_trades.csv", key, "cue_a", "POST_ENTRY", t, av, av)
            lad, src = mj_ladder_source(k, c, l1map.get(r.trade_id) if k == "R4" else None, plans, day_s, side)
            e.update(src)
            kw = dict(stop_slip=1, gap_fill=True, stop_delay_ms=250, crossed="live")
            ch = mj1_choice(lad) if lad else None
            if ch is None:
                e.update(mj1_status="NOT_APPLICABLE (no ladder)", mj2_status="NOT_APPLICABLE (no ladder)")
            else:
                tgt = near_edge(ch[1], side)
                if (tgt - float(r.entry_price)) * side <= 0:
                    e.update(mj1_target_used=ch[0], mj1_target=tgt, mj1_status="NOT_APPLICABLE (target behind entry)",
                             mj2_status="NOT_APPLICABLE (target behind entry)")
                else:
                    m = XR.replay(tape_xr(tape), side, t, float(r.stop), [tgt], **kw)
                    lg = m["legs"][0]
                    e.update(mj1_status="OK", mj1_target_used=ch[0], mj1_target=tgt, mj1_exit_time=lg["exit_time"], mj1_exit_price=lg["exit"],
                             mj1_exit_reason=lg["reason"], mj1_entry_check=float(m["entry"]))
                    O.time("diag_exit_trades.csv", key, "mj1", "POST_ENTRY", t, lg["exit_time"], lg["exit_time"])
                    n = int(r.qty)
                    tp1 = near_edge(lad.get("TP1", ""), side)
                    sp = mj2_split(n)
                    if sp is None:
                        e.update(mj2_status="NOT_APPLICABLE (1 NQ)", mj2_size_bucket="NOT_APPLICABLE")
                    elif tp1 is None or (tp1 - float(r.entry_price)) * side <= 0:
                        e.update(mj2_status="NOT_APPLICABLE (no TP1 beyond entry)", mj2_size_bucket=size_bucket(n))
                    else:
                        m2 = XR.replay(tape_xr(tape), side, t, float(r.stop), [tp1, tgt], **kw)
                        l1, l2 = m2["legs"]
                        e.update(mj2_status="OK", mj2_contracts=n, mj2_size_bucket=size_bucket(n), mj2_leg1_qty=sp[0], mj2_leg1_target=tp1,
                                 mj2_leg1_exit_time=l1["exit_time"], mj2_leg1_exit_price=l1["exit"], mj2_leg1_reason=l1["reason"],
                                 mj2_leg2_qty=sp[1], mj2_leg2_target=tgt, mj2_leg2_exit_time=l2["exit_time"], mj2_leg2_exit_price=l2["exit"],
                                 mj2_leg2_reason=l2["reason"])
                        last = max((x_ for x_ in (l1["exit_time"], l2["exit_time"]) if x_), default=None)
                        O.time("diag_exit_trades.csv", key, "mj2", "POST_ENTRY", t, last, last)
            exit_tr.append(e)
            # sizing (AT_ENTRY)
            qb, qa, qt = tape.quote_at(t)
            ref = float(r.risk_entry_ref) if k in ("R3", "R4") and not pd.isna(getattr(r, "risk_entry_ref", np.nan)) else float(qa if side > 0 else qb)
            st = int(round(abs(ref - float(r.stop)) / TICK))
            r10 = nq_risk_cents(st, 10)
            size_tr.append(dict(base, timing="AT_ENTRY", ref_source="BEST_ASK" if side > 0 else "BEST_BID", ref_price=ref, stop=float(r.stop),
                                stop_ticks_ref=st, nq10_risk_usd=r10 / 100, nq10_fits_1000="Y" if r10 <= 100_000 else "N",
                                nq10_equity_needed_usd=r10 / 100 / 0.01))
            O.time("diag_sizing_trades.csv", key, "nq10", "AT_ENTRY", t, t, qt)
            # GEX tags (AT_ENTRY)
            g = gex.get(day_s)
            ga = LA.gex_available_at(dt.date.fromisoformat(day_s)).astimezone(CT).replace(tzinfo=None)
            px, pxt = tape.last_trade(t)
            gt = dict(base, timing="AT_ENTRY", gex_report_date=g.get("report_date") if g else "", gex_available_at_ct=ga,
                      gex_valid="Y" if g and g.get("ok") == "True" else "N", gamma_regime=g.get("regime") if g else "DATA_MISSING",
                      time_of_day=tod_bucket(t), price_at_decision=px)
            gt.update(gex_tags(g, px, t, v3.get(day_s) if v3 else None))
            if v3:
                dm3, cut3 = v3_avail_ct(day_s)
                gt.update(gex_v3_data_max_ct=dm3, gex_v3_cutoff_ct=cut3)
                O.time("diag_gex_trades.csv", key, "gex_v3_tags", "AT_ENTRY", t, t, max(dm3, cut3))
            gex_tr.append(gt)
            O.time("diag_gex_trades.csv", key, "gex_tags", "AT_ENTRY", t, t, max(ga, pxt) if pxt else ga)
    O.csv("diag_cvd_trades.csv", cvd_tr); O.csv("diag_exit_trades.csv", exit_tr)
    O.csv("diag_sizing_trades.csv", size_tr); O.csv("diag_gex_trades.csv", gex_tr)

    # ---------- MNQ feasibility (R3 / R4 RISK_REJECT) ----------
    mnq, att_cache = [], {}
    for k, d_ in (("R3", r3), ("R4", r4)):
        at = pd.read_csv(d_ / f"{k}_attempts.csv", dtype={"time": str})
        log = logs[log_of[k]]
        lb = bars[log_of[k]]
        for r in at.itertuples():
            if not re.match(r"RISK_REJECT:(PER_TRADE_BUDGET|DAILY_BUDGET)", str(r.reasons)):
                continue
            t = pd.Timestamp(r.time).to_pydatetime()
            cand = att_cache.setdefault(k, {a["event"]: a for a in AR.attempts(log, None)}).get(r.event)
            st = int(r.risk_stop_ticks)
            m = max_mnq(st)
            row = dict(strategy=k, risk_impl_version=impl[k], ledger_sha256=hashes[k], session=t.date().isoformat(), event=r.event,
                       decision_time=t, nq_reject=r.reasons, stop_ticks_ref=st, mnq_max=m, mnq_fits_1="Y" if m >= 1 else "N",
                       mnq_risk_usd_at_max=mnq_risk_cents(st, m) / 100 if m else "", timing_hypothetical="POST_ENTRY")
            if cand is None:
                row["hyp_status"] = "DATA_MISSING (candidate not found)"
            else:
                c = cand["row"]; side = 1 if c["Direction"] == "Long" else -1
                stop, tgt = float(c["StopAnchor"]), float(c["TargetPrice"])
                if t != cand["t"]:                                  # RH1 retest path: the retest stop
                    p = AR.retest_path(lb, cand["cand"], cand["t"], 2); stop = p["stop"]
                mm = XR.run_model("M0", tape_xr(tape), dict(side=side, signal_end=t, stop=stop, target=tgt), log.zones[t.date()],
                                  stop_slip=1, gap_fill=True, stop_delay_ms=250, crossed="live")
                lg = mm["legs"][0]
                row.update(hyp_status="OK", hyp_entry=float(mm["entry"]), hyp_stop=stop, hyp_target=tgt, hyp_exit_time=lg["exit_time"],
                           hyp_exit_price=lg["exit"], hyp_exit_reason=lg["reason"])
                O.time("diag_mnq_rejects.csv", f"{k}:{r.event}", "mnq_hyp", "POST_ENTRY", t, lg["exit_time"], lg["exit_time"])
            O.time("diag_mnq_rejects.csv", f"{k}:{r.event}", "mnq_size", "AT_ENTRY", t, t, t)
            mnq.append(row)
    O.csv("diag_mnq_rejects.csv", mnq)

    # ---------- GEX: V2 twins per R4 zone, V5 per session, NOT_RUN items ----------
    zrows, srows = [], []
    for d in sessions:
        g = gex.get(d)
        valid = bool(g and g.get("ok") == "True")
        ref, reft = tape.last_trade(dt.datetime.combine(dt.date.fromisoformat(d), dt.time(8, 10)))
        srow = dict(session=d, gex_valid="Y" if valid else "N", report_date=g.get("report_date") if g else "",
                    regime=g.get("regime") if g else "", ref_price_0810=ref)
        if v3 and d in v3:
            x3 = v3[d]
            dm3, cut3 = v3_avail_ct(d)
            srow.update(available_at_ct=cut3, inputs_data_max_ct=dm3, flip_v3_nt=x3["flip_v3_nt"], hvl_nt=x3["hvl_nt"],
                        regime_agree=x3["regime_agree"], flip_v3_minus_hvl_pts=x3["flip_v3_minus_hvl_pts"],
                        flip_v3_crossings=x3["flip_v3_crossings"], pc_gamma_ratio=x3["pc_gamma_ratio"],
                        atm_iv=x3["atm_iv"], atm_iv_expiry=x3["atm_iv_expiry"], atm_iv_dte_from_report=x3["atm_iv_dte_from_report"])
            O.time("diag_gex_sessions.csv", d, "gex_v3", "AT_ENTRY", dt.datetime.combine(dt.date.fromisoformat(d), dt.time(8, 10)),
                   cut3, dm3)
        else:
            srow.update(v3_flip="NOT_RUN (inputs)", volatility_control="NOT_RUN (inputs)")
        srows.append(srow)
        sc = json.loads((plans / f"PreopenPlan_{d}_book1a.json").read_text(encoding="utf-8"))
        if not valid:
            for z in (sc.get("zones") or []) + (sc.get("targets") or []):
                zrows.append(dict(session=d, zone=z.get("label"), gex_valid="N", v2_status="NOT_APPLICABLE (gex_valid N)"))
            continue
        lv = {name: float(g.get(c + "_nt") or g.get(c)) for c, name in SIX if (g.get(c + "_nt") or g.get(c))}
        tw = twins(lv, ref, d)
        from book1a import families as F
        for src, zs in (("zones", sc.get("zones") or []), ("targets", sc.get("targets") or [])):
            for z in zs:
                fams = list(z.get("families") or [])
                lvs = list(z.get("levels") or [])
                gamma = any(n.startswith("GAMMA") for n in lvs)
                other = [f for f in fams if f != "GEX"]
                real_class = "DECISION" if len(fams) >= F.MIN_FAMILIES_FOR_DECISION else "TARGET"
                row = dict(session=d, zone=z.get("label"), sidecar_list=src, zone_lo=z.get("lo"), zone_hi=z.get("hi"), gex_valid="Y",
                           families_real=",".join(fams), gex_real="Y" if "GEX" in fams else "N", gamma_rank_level_in_zone="Y" if gamma else "N",
                           class_real=real_class, v2_status="OK")
                for nm in ("random", "round"):
                    pres = gex_present(float(z["lo"]), float(z["hi"]), tw[nm], gamma)
                    n_f = len(other) + (1 if pres else 0)
                    cl = "DECISION" if n_f >= F.MIN_FAMILIES_FOR_DECISION else "TARGET"
                    row.update({f"gex_{nm}": "Y" if pres else "N", f"class_{nm}": cl, f"status_differs_{nm}": "Y" if cl != real_class else "N"})
                row["twin_random_levels"] = ";".join(f"{k_}={v:.2f}({tw['random_side'][k_]})" for k_, v in tw["random"].items())
                row["twin_round_levels"] = ";".join(f"{k_}={v:.2f}" for k_, v in tw["round"].items())
                zrows.append(row)
    if v3:
        # volatility terciles: a post-phase reporting grouping (computed after the phase from this phase's sessions only)
        ivs = sorted((float(x["atm_iv"]), x["session"]) for x in srows if "atm_iv" in x and np.isfinite(float(x["atm_iv"])))
        n_ = len(ivs)
        rank = {s_: i + 1 for i, (_, s_) in enumerate(ivs)}
        for x in srows:
            x["vol_tercile_POST_PHASE_GROUPING"] = int(math.ceil(3 * rank[x["session"]] / n_)) if x["session"] in rank else "DATA_MISSING"
    O.csv("diag_gex_zones.csv", zrows); O.csv("diag_gex_sessions.csv", srows)

    # ---------- D5 CVD definition check days ----------
    ev, excl, swl = [], [], []
    for d in d5_days:
        dy = days[d]
        sw = [dy.swing_dict(i, k_) for i, k_ in dy.swings if i + SWING_N < len(dy.end_t)]
        for s in sw:
            swl.append(dict(session=d, kind=s["kind"], swing_bar=s["t"], confirm=s["confirm_t"], price=s["price"], cvd17=s["cvd_p"], cvd0830=s["cvd_r"]))
        for kind in ("HIGH", "LOW"):
            s_k = [s for s in sw if s["kind"] == kind]
            for a, b in zip(s_k, s_k[1:]):
                if b["t"] < dy.rth or b["t"] > dy.end:
                    continue
                x = pair_fields(dy, a, b, 0, None, None, "p")
                row = dict(session=d, kind=kind, s1_time=a["t"], s1_confirm=a["confirm_t"], s1_price=a["price"], s1_cvd17=a["cvd_p"],
                           s1_cvd0830=a["cvd_r"], s2_time=b["t"], s2_confirm=b["confirm_t"], s2_price=b["price"], s2_cvd17=b["cvd_p"],
                           s2_cvd0830=b["cvd_r"], gap_min=x["p_gap_min"], at_session_extreme="Y" if x["p_location"] == "SESSION_EXTREME" else "N",
                           case_cvd17=x["p_raw_case_cvd17"], case_cvd0830=x["p_raw_case_cvd0830"], earliest_knowable=b["confirm_t"])
                (excl if x["p_gap_min"] > PAIR_MAX_MIN else ev).append(row)
    O.csv("d5_cvd_swings.csv", swl); O.csv("d5_cvd_pairs.csv", ev); O.csv("d5_cvd_pairs_excluded_60min.csv", excl)

    # ---------- timing registry ----------
    O.csv("diag_timing.csv", O.timing)
    (out / "diag_manifest.json").write_text(json.dumps(dict(version=VERSION, commit=commit, ledgers={k: str(v) for k, v in files.items()},
                                                            ledger_sha256=hashes, risk_impl_version=impl, ours=OURS, seed=SEED), indent=1))
    return dict(hashes=hashes, impl=impl, header=header)


_XR_TAPE = {}


def tape_xr(tape: TapeFull):
    """exit_replay needs .t .p .b .a and quote_at -> (bid, ask); a thin view of the same arrays."""
    if id(tape) not in _XR_TAPE:
        class V:
            pass
        v = V(); v.t, v.p, v.b, v.a = tape.t, tape.p, tape.b, tape.a
        v.quote_at = lambda t, _t=tape: _t.quote_at(t)[:2]
        _XR_TAPE[id(tape)] = v
    return _XR_TAPE[id(tape)]


def audit(out: Path) -> dict:
    """D2: every registered field group; AT_ENTRY / PROVISIONAL: latest data <= available_at = decision time;
    POST_ENTRY: labelled, latest data <= available_at."""
    df = pd.read_csv(out / "diag_timing.csv", comment="#", dtype=str)
    bad = []
    for r in df.itertuples():
        dmax = pd.Timestamp(r.data_max_t) if isinstance(r.data_max_t, str) and r.data_max_t else None
        av = pd.Timestamp(r.available_at) if isinstance(r.available_at, str) and r.available_at else None
        dec = pd.Timestamp(r.decision_t)
        if r.timing in ("AT_ENTRY", "PROVISIONAL"):
            if av is None or av > dec or (dmax is not None and dmax > av):
                bad.append(r._asdict())
        elif r.timing == "POST_ENTRY":
            if dmax is not None and av is not None and dmax > av:
                bad.append(r._asdict())
        else:
            bad.append(r._asdict())
    # every POST_ENTRY column group is labelled in its file
    lab = {}
    for f, col in (("diag_cvd_trades.csv", "post_high_timing"), ("diag_cvd_trades.csv", "post_low_timing"),
                   ("diag_exit_trades.csv", "timing"), ("diag_mnq_rejects.csv", "timing_hypothetical")):
        x = pd.read_csv(out / f, comment="#", dtype=str)
        lab[f"{f}:{col}"] = bool(len(x) == 0 or (col in x and (x[col] == "POST_ENTRY").all()))
    return dict(groups=len(df), violations=len(bad), by_timing=df.timing.value_counts().to_dict(), labelled=lab, bad=bad[:20])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True); ap.add_argument("--plans", required=True); ap.add_argument("--gex", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--inputs", default=None, help="K:\Book1A_inputs: builds GEX V3, volatility control, pc_gamma_ratio, pin_zone")
    a = ap.parse_args(argv)
    res = run(Path(a.runs), Path(a.plans), Path(a.gex), Path(a.out), inputs=a.inputs)
    au = audit(Path(a.out))
    (Path(a.out) / "d2_lookahead_audit.json").write_text(json.dumps(au, indent=1, default=str))
    print(json.dumps(dict(hashes=res["hashes"], impl=res["impl"], audit={k: v for k, v in au.items() if k != "bad"}), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
