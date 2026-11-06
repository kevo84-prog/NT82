"""Phase 3 arms as written in backtest\\phase3\\phase3_change_list_APPROVED.md (approved Oct 26, 2026; JE 0.5).

Entry arms are vetoes on a candidate row (CANDIDATE or SHADOW) for arm_replay.replay(veto=...): True = the arm blocks
this candidate, so it cannot win its bar and cannot be traded. Inputs are known at or before the signal bar.
  A7   fight veto: fight_flag = Y (the strategy's own flag, logged at candidate time).
  L1   intraday IMB / POWER zone more than 10.0 points (gap between nearest edges; 0 if they overlap) from every
       DECISION zone of that day's rules-only plan. Report-only lines at 5 and 20 points.
  FZ1  INITIATION at an intraday zone that has not held: held = a STATE row "Response" at that zone, before the signal
       bar, with no "Failed" state at that zone after it and before the signal bar (Kyron's choice (a) No); overnight
       Responses count (choice (b) Yes).
  G1   on days whose plan gex_regime is POS (replica GEX), an INITIATION candidate at an intraday zone (Amendment 1).
  T8   any of the 3 completed 1-minute bars before the signal bar has bar delta in the trade's direction and closes
       against it (close < open for a long, close > open for a short); delta from the tape's aggressor flag.
  M2E  exit model (arm_replay.replay(exit_model="M2E")); RH1 = arm_replay.replay(retest=...) (Amendment 1); RT0 is the harness setting RetriggerBars=0 (a strategy run).
Promotion test (frozen): promotion() pairs an arm with A0 per session.
"""
import collections, datetime as dt, gzip

import numpy as np

from .arm_replay import ts

INTRADAY = ("DEVELOPING_INTRADAY_IMB", "DEVELOPING_INTRADAY_POWER")


def intraday(r): return r["LocationType"].startswith(INTRADAY)


def a7(log):
    return lambda r: r.get("fight_flag", "") == "Y"


def l1(log, cut=10.0):
    zones = collections.defaultdict(list)
    for f in (log.run / "plans").glob("PreopenPlan_*.txt"):
        d = f.stem.split("_")[1]
        for line in open(f, encoding="utf-8"):
            if line.startswith("zone=") and "|DECISION|" in line:
                lo, hi = line[5:].split("|")[0].split("-"); zones[d].append((float(lo), float(hi)))

    def dist(r):
        lo, hi = float(r["ZoneLo"]), float(r["ZoneHi"])
        best = None
        for a, b in zones.get(r["EvidenceTimeCT"][:10], []):
            x = 0.0 if (lo <= b and hi >= a) else (a - hi if hi < a else lo - b)
            best = x if best is None else min(best, x)
        return best

    def veto(r):
        if not intraday(r): return False
        x = dist(r)
        return x is None or x > cut + 1e-9
    veto.dist = dist
    return veto


def fz1(log):
    states = collections.defaultdict(list)
    for r in log.rows:
        if r["RecordType"] == "STATE": states[r["LocationId"]].append((r["EvidenceTimeCT"][:23], r["State"]))
    for v in states.values(): v.sort()

    def held(loc, t):
        prior = [(x, s) for x, s in states.get(loc, []) if x < t]
        for i, (x, s) in enumerate(prior):
            if s == "Response" and not any(s2 == "Failed" for _, s2 in prior[i + 1:]): return True
        return False

    def veto(r):
        return r["SetupFamily"] == "INITIATION" and intraday(r) and not held(r["LocationId"], r["EvidenceTimeCT"][:23])
    return veto


class MinuteBars:
    """1-minute bars from a tape (bar stamped at its end, ticks in (T-1min, T]): open, high, low, close, aggressor delta."""
    def __init__(self, tape_path, hours=(7, 15)):
        b = {}
        op = gzip.open if str(tape_path).endswith(".gz") else open
        with op(tape_path, "rt") as f:
            next(f)
            for line in f:
                p = line.split(",")
                tt = p[0]
                h = int(tt[11:13])
                if h < hours[0] or h > hours[1]: continue
                t = dt.datetime.fromisoformat(tt[:26])
                end = t.replace(second=0, microsecond=0)
                if t != end: end += dt.timedelta(minutes=1)
                px, vol, ag = float(p[1]), int(p[4]), p[5].strip()
                x = b.get(end)
                if x is None: x = b[end] = [px, px, px, px, 0]          # open, high, low, close, delta
                else: x[1] = max(x[1], px); x[2] = min(x[2], px); x[3] = px
                x[4] += vol if ag == "B" else (-vol if ag in ("S", "A") else 0)
        self.bars = b
        self.ends = sorted(b)

    def after(self, t, n):
        """The first n bars ending after t, as (end, open, high, low, close)."""
        import bisect
        i = bisect.bisect_right(self.ends, t)
        return [(e,) + tuple(self.bars[e][:4]) for e in self.ends[i:i + n]]


def g1(log):
    """Amendment 1: POS-regime days block intraday-zone initiations. Regime = the day's plan gex_regime (08:10 as-of);
    missing / UNKNOWN / NEG = no change."""
    def veto(r):
        plan = log.plans.get(r["EvidenceTimeCT"][:10]) or {}
        return plan.get("gex_regime", "").upper() == "POS" and r["SetupFamily"] == "INITIATION" and intraday(r)
    return veto


def t8(log, bars):
    def veto(r):
        side = 1 if r["Direction"] == "Long" else -1
        sig = ts(r["EvidenceTimeCT"])
        for k in (1, 2, 3):
            x = bars.bars.get(sig - dt.timedelta(minutes=k))
            if x is None: continue
            o, c, delta = x[0], x[3], x[4]
            if delta * side > 0 and (c - o) * side < 0: return True
        return False
    return veto


# ---------------------------------------------------------------- comparison with A0 (frozen promotion rule)
def differing_trades(arm_trades, a0_trades):
    """Counted once per trade: removed, admitted, or entered / exited differently; matched by date and signal time."""
    a = {(t["date"], t["signal_time"]): t for t in arm_trades}
    b = {(t["date"], t["signal_time"]): t for t in a0_trades}
    removed = len(set(b) - set(a)); admitted = len(set(a) - set(b))
    exited = sum(1 for k in set(a) & set(b) if a[k]["exit_time"] != b[k]["exit_time"] or abs(a[k]["exit"] - b[k]["exit"]) > 1e-9
                 or abs(a[k]["entry"] - b[k]["entry"]) > 1e-9)
    return dict(removed=removed, admitted=admitted, exited_differently=exited, total=removed + admitted + exited)


def per_session(trades, sessions):
    s = {d: 0.0 for d in sessions}
    for t in trades: s[t["date"]] = s.get(t["date"], 0.0) + t["R"]
    return [s[d] for d in sessions]


def max_dd(trades):
    eq = pk = dd = 0.0
    for t in sorted(trades, key=lambda t: (t["date"], t["signal_time"])):
        eq += t["R"]; pk = max(pk, eq); dd = max(dd, pk - eq)
    return dd


def promotion(arm, a0, sessions, arm_2t=None, a0_2t=None, seed=20251205, n=10_000):
    """Frozen rule: paired net R per session vs A0; session bootstrap (n resamples, seed) 90% interval = 5th-95th
    percentile, lower bound = 5th percentile > 0; max DD <= 1.25 x A0's; >= 20 differing trades; arm at 2-tick stop
    slippage paired against A0 at 2 ticks >= 0. arm / a0 are replay() results."""
    x = np.array(per_session(arm["trades"], sessions)) - np.array(per_session(a0["trades"], sessions))
    rng = np.random.default_rng(seed)
    boots = x[rng.integers(0, len(x), size=(n, len(x)))].mean(axis=1)
    lo, hi = np.percentile(boots, [5, 95])
    diff = differing_trades(arm["trades"], a0["trades"])
    dd_arm, dd_a0 = max_dd(arm["trades"]), max_dd(a0["trades"])
    out = dict(sessions=len(sessions), mean_diff_per_session=float(x.mean()), ci90_low=float(lo), ci90_high=float(hi),
               max_dd_arm=dd_arm, max_dd_a0=dd_a0, differing=diff)
    checks = dict(bound=lo > 0, drawdown=dd_arm <= 1.25 * dd_a0 + 1e-12, sample=diff["total"] >= 20)
    if arm_2t is not None and a0_2t is not None:
        x2 = np.array(per_session(arm_2t["trades"], sessions)) - np.array(per_session(a0_2t["trades"], sessions))
        out["mean_diff_per_session_2tick"] = float(x2.mean())
        checks["two_tick"] = x2.mean() >= 0
    out["checks"] = checks
    out["verdict"] = "promote" if all(checks.values()) else ("insufficient evidence" if not checks["sample"] or lo <= 0 < hi else "reject")
    return out
