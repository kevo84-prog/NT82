r"""Book 1A Phase 2 report card and what-fails-and-why classification (Phase2_registration.md sections 2 and 3).

Written Nov 7, 2026 (Step A follow-up), before any Phase 2 trading run, on synthetic ledgers only
(book1a/tests/test_phase2_report.py). It reads ledgers only when Step B calls it; `run()` refuses every phase but
"phase2".

Definitions (registration section 2, implemented exactly):
  trade R            ledger realized_net_R (theoretical R: ledger theoretical_R); trade USD: ledger net_usd
  entry_session      the ledger `date` column = the trading session of the entry decision (both replays write
                     t.strftime("%Y-%m-%d") of the decision time). It controls attribution: the daily table, the
                     populations, the regime groups, the drawdown order and the review windows.
  session net R      sum of the session's trade R; a session with no trade counts with 0 (also net USD, theoretical R)
  net R per session  mean of session net R over the population's sessions (21 or 13, zero-trade sessions included)
  90% CI             B = 10,000 resamples of the population's sessions with replacement; statistic = mean session net
                     R; a new numpy default_rng(20251205) per strategy and population, index matrix
                     rng.integers(0, n, size=(10000, n)); 5th / 95th numpy percentile (linear)
  win rate           trades with R > 0 / trades (R == 0 is neither win nor loss); average win / loss R
  max drawdown       largest fall of cumulative R (USD for R3 / R4) from its running peak, the peak starting at 0, over
                     trades ordered by (entry_session, entry_time). Supplemental (never instead): the same over the
                     session net R series in session order.
  time of day        entry_time buckets 08:30-08:45, 08:45-10:00, 10:00-13:00, 13:00+ (start in, end out)
  gamma regime       gex_levels_block1.csv `regime` where ok == True; other sessions (V5) only in "all"

Overlap (code reading, frozen replays): a strategy never holds two positions. Book 1 arm_replay.replay (R1 / R2) blocks
an attempt with ALREADY_IN_TRADE while busy_until (the open trade's exit time, or the RH1 retest time) >= now;
replay_risk.replay (R3 / R4) does the same and DayRiskState.pre_trade_check adds RISK_REJECT:IN_POSITION. So entry
order equals realization order inside a strategy; the report never reorders trades. `check_no_overlap` asserts it.

Nov 28 early-close exit (registration section 1): the frozen FLATTEN branch closes a position still open at the
12:15 CT half-day close at the last Nov 28 quote and stamps the exit with the next tape tick (Nov 30 17:00 CT). The
ledger keeps only HH:MM:SS. `exit_times` rebuilds exit_time_raw (the engine stamp, with its date) and exit_time_model
(the last Nov 28 tick whose quote was used: a simulated fill reference under the frozen fill model, not a market
execution) from the tape, and flags EXIT_AFTER_SESSION_CLOSE. Price, USD and R stay as the engine produced them.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence

import numpy as np

from book1a import sessions as S

VERSION = "phase2-report-v1.0"
SEED = 20251205
B = 10_000
STRATEGIES = ("R1", "R2", "R3", "R4")
USD_DRAWDOWN = ("R3", "R4")                       # registered: max drawdown in dollars for R3 / R4
EXPOSED = {dt.date(2025, 11, d) for d in (17, 18, 19, 20, 21, 24, 25, 26)}
FLATTEN = dt.time(14, 55)                         # frozen Book 1 fills.FLATTEN
TOD_BUCKETS = (("08:30-08:45", dt.time(8, 30), dt.time(8, 45)), ("08:45-10:00", dt.time(8, 45), dt.time(10, 0)),
               ("10:00-13:00", dt.time(10, 0), dt.time(13, 0)), ("13:00+", dt.time(13, 0), None))
CLASSES = ("GAVE_BACK", "STOP_THEN_TARGET", "NO_POST_STOP_FOLLOW_THROUGH", "UNCLASSIFIED", "NOT_STOPPED")
CUTOFF_R = 1.0                                    # prespecified descriptive threshold (registration section 3)
NUMERIC_TAGS = ("cr_ps_width", "pc_gamma_ratio")
CVD_NOTE = "fidelity to Jeron's CVD unproven (1 of 4 video examples reproduced; CVD_video_check, Nov 6)"


# ------------------------------------------------------------------ parsing
def fnum(x) -> Optional[float]:
    if x is None or x == "" or (isinstance(x, float) and np.isnan(x)):
        return None
    return float(x)


def parse_time(s: str) -> dt.time:
    return dt.time.fromisoformat(s if len(s) > 8 else s + ".000")


def entry_session(row: dict) -> dt.date:
    return dt.date.fromisoformat(row["date"])


def trade_r(row: dict) -> float:
    r = fnum(row["realized_net_R"])
    if r is None:
        raise ValueError(f"trade {row.get('trade_id')}: realized_net_R missing (stop_ticks 0?)")
    return r


def order_key(row: dict):
    return (entry_session(row), parse_time(row["entry_time"]))


def read_csv(path) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ populations and sessions
def populations(sessions: Sequence[dt.date]) -> Dict[str, List[dt.date]]:
    s = sorted(sessions)
    return {"ALL": s, "UNEXPOSED": [d for d in s if d not in EXPOSED]}


def daily_table(trades: Iterable[dict], sessions: Sequence[dt.date]) -> List[dict]:
    """Every session of the population, zero-trade sessions included; trades attributed by entry_session."""
    by = {d: dict(session=d.isoformat(), trades=0, net_R=0.0, theoretical_R=0.0, net_usd=0.0) for d in sessions}
    for t in trades:
        d = entry_session(t)
        if d not in by:
            continue
        x = by[d]
        x["trades"] += 1
        x["net_R"] += trade_r(t)
        x["theoretical_R"] += fnum(t.get("theoretical_R")) or 0.0
        x["net_usd"] += fnum(t["net_usd"])
    out = [by[d] for d in sorted(by)]
    for x in out:
        x["net_R"], x["theoretical_R"], x["net_usd"] = round(x["net_R"], 6), round(x["theoretical_R"], 6), round(x["net_usd"], 2)
    return out


def in_pop(trades: Iterable[dict], sessions: Sequence[dt.date]) -> List[dict]:
    ss = set(sessions)
    return sorted((t for t in trades if entry_session(t) in ss), key=order_key)


# ------------------------------------------------------------------ statistics
def bootstrap_ci(session_values: Sequence[float], b: int = B, seed: int = SEED):
    """90% session bootstrap of the mean session net R. A new default_rng(seed) per call (= per strategy and population)."""
    v = np.asarray(session_values, dtype=float)
    n = len(v)
    if n == 0:
        return None, None
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(b, n))
    means = v[idx].mean(axis=1)
    lo, hi = np.percentile(means, [5, 95])
    return float(lo), float(hi)


def max_drawdown(values: Sequence[float]) -> float:
    """Largest fall of the running sum from its running peak; the peak starts at 0 (so a first loss is a drawdown)."""
    cum = peak = dd = 0.0
    for x in values:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    return round(dd, 6)


def win_stats(rs: Sequence[float]) -> dict:
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r < 0]
    return dict(win_rate=round(len(wins) / len(rs), 6) if rs else None, wins=len(wins), losses=len(losses),
                zero=sum(1 for r in rs if r == 0),
                avg_win_R=round(float(np.mean(wins)), 6) if wins else None,
                avg_loss_R=round(float(np.mean(losses)), 6) if losses else None)


def tod_bucket(entry_time: str) -> str:
    t = parse_time(entry_time)
    for name, a, b in TOD_BUCKETS:
        if t >= a and (b is None or t < b):
            return name
    return "before 08:30"


# ------------------------------------------------------------------ overlap
def check_no_overlap(trades: Iterable[dict], exit_dt: Callable[[dict], dt.datetime]) -> List[str]:
    """Trades in entry order; returns the ids of trades entered before the previous trade's exit (expected: none)."""
    bad, prev = [], None
    for t in sorted(trades, key=order_key):
        ent = dt.datetime.combine(entry_session(t), parse_time(t["entry_time"]))
        if prev is not None and ent < prev:
            bad.append(t["trade_id"])
        prev = exit_dt(t)
    return bad


# ------------------------------------------------------------------ Nov 28 early-close exit
def exit_times(row: dict, tape_t: np.ndarray) -> dict:
    """entry_session, exit_time_raw, exit_time_model and the flag for one ledger trade.

    tape_t: the replay tape's trade times (np.datetime64[us], ascending), as fills.Tape.t. A ledger exit time that,
    on the entry session's date, falls after the session close can only come from the FLATTEN branch reaching the
    first tick at or after 14:55 of that date (the next session's open on a half day): exit_time_raw = that tick
    (it must carry the ledger's HH:MM:SS), exit_time_model = the tick before it, whose quote the branch used."""
    d = entry_session(row)
    close = S.session_close(d)
    entry = dt.datetime.combine(d, parse_time(row["entry_time"]))
    out = dict(entry_session=d.isoformat(), session_close=close.isoformat(sep=" "))
    if not row.get("exit_time"):
        return dict(out, exit_time_raw=None, exit_time_model=None, exit_flag="NO_EXIT_TIME", holding_min_model=None)
    naive = dt.datetime.combine(d, parse_time(row["exit_time"]))
    if naive <= close:
        return dict(out, exit_time_raw=naive.isoformat(sep=" "), exit_time_model=naive.isoformat(sep=" "), exit_flag="N",
                    holding_min_model=round((naive - entry).total_seconds() / 60.0, 4))
    i = int(np.searchsorted(tape_t, np.datetime64(dt.datetime.combine(d, FLATTEN), "us"), side="left"))
    if i <= 0 or i >= len(tape_t):
        raise ValueError(f"trade {row.get('trade_id')}: exit after the close but no tape tick at or after {d} 14:55")
    raw = tape_t[i].astype(dt.datetime)
    model = tape_t[i - 1].astype(dt.datetime)
    if raw.strftime("%H:%M:%S.%f")[:12] != row["exit_time"][:12] or row.get("exit_reason") != "TIME_EXIT" or model > close:
        raise ValueError(f"trade {row.get('trade_id')}: exit {row['exit_time']} after the close is not the FLATTEN stamp {raw}")
    return dict(out, exit_time_raw=raw.isoformat(sep=" "), exit_time_model=model.isoformat(sep=" "),
                exit_flag="EXIT_AFTER_SESSION_CLOSE", holding_min_model=round((model - entry).total_seconds() / 60.0, 4))


# ------------------------------------------------------------------ report card
def risk_counts(trades: List[dict], attempts: Optional[List[dict]]) -> dict:
    rej = Counter()
    for a in attempts or []:
        for x in str(a.get("reasons", "")).split("|"):
            if x.startswith("RISK_REJECT"):
                rej[x] += 1
    ex = [t for t in trades if str(t.get("exec_risk_breach", "0")) == "1"]
    ex_over = [fnum(t["entry_risk_at_fill_usd"]) - fnum(t["risk_budget_usd"]) for t in ex]
    bf = [t for t in trades if str(t.get("risk_breach_fill", "0")) == "1"]
    bf_over = [-fnum(t["net_usd"]) - fnum(t["planned_risk_usd"]) for t in bf]
    return dict(risk_reject=sum(rej.values()), risk_reject_by_reason=dict(sorted(rej.items())),
                exec_breach=len(ex), exec_breach_largest_usd=round(max(ex_over), 2) if ex_over else None,
                risk_breach_fill=len(bf), risk_breach_fill_largest_overrun_usd=round(max(bf_over), 2) if bf_over else None,
                note="RISK_BREACH_FILL = the realized loss overrun (same event, reported once under both names)")


def core(strategy: str, trades: List[dict], sessions: Sequence[dt.date]) -> dict:
    """Trades, net R per session, its 90% CI and max drawdown (also used for the stress ledgers)."""
    tr = in_pop(trades, sessions)
    day = daily_table(tr, sessions)
    sv = [x["net_R"] for x in day]
    n = len(sessions)
    lo, hi = bootstrap_ci(sv)
    rs = [trade_r(t) for t in tr]
    out = dict(sessions=n, trades=len(tr), trades_per_session=round(len(tr) / n, 6) if n else None,
               net_R_per_session=round(float(np.mean(sv)), 6) if n else None,
               net_R_per_session_ci90=[None if lo is None else round(lo, 6), None if hi is None else round(hi, 6)],
               max_drawdown_R=max_drawdown(rs))
    if strategy in USD_DRAWDOWN:
        out["max_drawdown_usd"] = round(max_drawdown([fnum(t["net_usd"]) for t in tr]), 2)
    return out


def group_stats(tr: List[dict], n_sessions: int) -> dict:
    rs = [trade_r(t) for t in tr]
    return dict(sessions=n_sessions, trades=len(tr), net_R=round(sum(rs), 6),
                net_R_per_trade=round(sum(rs) / len(rs), 6) if rs else None,
                net_R_per_session=round(sum(rs) / n_sessions, 6) if n_sessions else None,
                net_usd=round(sum(fnum(t["net_usd"]) for t in tr), 2), win_rate=win_stats(rs)["win_rate"])


def report_card(strategy: str, trades: List[dict], sessions: Sequence[dt.date], attempts: Optional[List[dict]] = None,
                regime_of: Optional[Dict[dt.date, Optional[str]]] = None, stress: Optional[Dict[str, List[dict]]] = None) -> dict:
    tr = in_pop(trades, sessions)
    day = daily_table(tr, sessions)
    n = len(sessions)
    rs = [trade_r(t) for t in tr]
    card = dict(strategy=strategy, label="replay (in-sample)", version=VERSION, **core(strategy, trades, sessions))
    card["theoretical_R_per_session"] = round(sum(x["theoretical_R"] for x in day) / n, 6) if n else None
    card["net_usd"] = round(sum(x["net_usd"] for x in day), 2)
    card["net_usd_per_session"] = round(card["net_usd"] / n, 2) if n else None
    card.update(win_stats(rs))
    card["max_drawdown_R_session_order_SUPPLEMENTAL"] = max_drawdown([x["net_R"] for x in day])
    card["exit_reasons"] = dict(sorted(Counter(t["exit_reason"] for t in tr).items()))
    if strategy in ("R3", "R4"):
        ss = set(sessions)
        att = None if attempts is None else [a for a in attempts if dt.date.fromisoformat(str(a["time"])[:10]) in ss]
        card["risk"] = risk_counts(tr, att)
    if stress:
        card["stress"] = {k: core(strategy, v, sessions) for k, v in stress.items()}
    if regime_of is not None:
        groups = {"all": list(sessions)}
        for g in ("positive", "negative"):
            groups[g] = [d for d in sessions if regime_of.get(d) == g]
        no_gex = [d for d in sessions if regime_of.get(d) not in ("positive", "negative")]
        card["gamma_regime"] = {g: group_stats(in_pop(tr, ds), len(ds)) for g, ds in groups.items()}
        card["gamma_regime"]["no_valid_gex_V5"] = dict(sessions=len(no_gex), in_groups="all only",
                                                      list=[d.isoformat() for d in no_gex])
    tod = {}
    for name, _, _ in TOD_BUCKETS + (("before 08:30", None, None),):
        b = [t for t in tr if tod_bucket(t["entry_time"]) == name]
        if b or name != "before 08:30":
            tod[name] = group_stats(b, n)
    card["time_of_day"] = tod
    card["daily_table"] = day
    return card


# ------------------------------------------------------------------ section 3 classification
def classify(trade: dict, review: dict) -> str:
    """The first rule that applies (registration section 3). review = phase2_review_fields.compute row."""
    if trade["exit_reason"] != "STOP_FIRST":
        return "NOT_STOPPED"
    mfe = fnum(review.get("mfe_R"))
    if mfe is not None and mfe >= CUTOFF_R:
        return "GAVE_BACK"
    ok = review.get("post_exit_status") == "OK"
    if ok and review.get("post_exit_target_traded") == "Y":
        return "STOP_THEN_TARGET"
    move = fnum(review.get("post_exit_move_R"))
    if ok and review.get("post_exit_truncated") == "N" and move is not None and move < CUTOFF_R \
            and review.get("post_exit_target_traded") == "N":
        return "NO_POST_STOP_FOLLOW_THROUGH"
    return "UNCLASSIFIED"


def terciles(values: Iterable[Optional[float]]):
    """Cut-offs (1/3, 2/3 numpy linear quantiles) from one value per session (the 21 sessions); never outcomes."""
    v = np.asarray([x for x in values if x is not None], dtype=float)
    if len(v) == 0:
        return None
    q1, q2 = np.quantile(v, [1 / 3, 2 / 3])
    return float(q1), float(q2)


def tercile_label(x: Optional[float], cuts) -> str:
    if x is None or cuts is None:
        return "NA"
    return "T1" if x <= cuts[0] else ("T2" if x <= cuts[1] else "T3")


def class_table(strategy: str, trades: List[dict], reviews: Dict[str, dict], tags: Dict[str, dict],
                session_numeric: Dict[str, Dict[dt.date, Optional[float]]], categorical: Sequence[str]) -> dict:
    """Class per trade, counts per class, and tag counts per class. session_numeric[tag][session] = the session's
    value; the tercile cut-offs come from all its sessions (the 21) and are used for both populations."""
    cuts = {k: terciles(v.values()) for k, v in session_numeric.items()}
    rows, counts, tagc = [], Counter(), {c: {} for c in CLASSES}
    for t in sorted(trades, key=order_key):
        c = classify(t, reviews.get(t["trade_id"], {}))
        counts[c] += 1
        tg = tags.get(t["trade_id"], {})
        row = dict(strategy=strategy, trade_id=t["trade_id"], entry_session=t["date"], cls=c)
        for k in categorical:
            row[k] = tg.get(k, "NA") or "NA"
            tagc[c].setdefault(k, Counter())[row[k]] += 1
        for k, by in session_numeric.items():
            row[k + "_tercile"] = tercile_label(by.get(entry_session(t)), cuts[k])
            tagc[c].setdefault(k + "_tercile", Counter())[row[k + "_tercile"]] += 1
        rows.append(row)
    return dict(strategy=strategy, counts={c: counts.get(c, 0) for c in CLASSES}, tercile_cutoffs=cuts,
                tags={c: {k: dict(sorted(v.items())) for k, v in d.items()} for c, d in tagc.items()},
                trades=rows, cvd_note=CVD_NOTE, label="replay (in-sample), descriptive only")


# ------------------------------------------------------------------ inputs
def gex_regimes(path, sessions: Sequence[dt.date]) -> Dict[dt.date, Optional[str]]:
    rows = {r["session"]: r for r in read_csv(path)}
    out = {}
    for d in sessions:
        r = rows.get(d.isoformat())
        out[d] = r["regime"] if r and r.get("ok") == "True" and r.get("regime") in ("positive", "negative") else None
    return out


def run(phase: str, ledgers: Dict[str, str], attempts: Dict[str, str], stress: Dict[str, Dict[str, str]], gex: str, out: str) -> dict:
    """Step B only. Refuses every phase but phase2."""
    if phase != "phase2":
        raise RuntimeError(f"phase2_report: Phase 2 only, not {phase!r}")
    sess = S.phase_sessions("phase2")
    pops = populations(sess)
    reg = gex_regimes(gex, sess)
    res = dict(version=VERSION, label="replay (in-sample)", populations={k: [d.isoformat() for d in v] for k, v in pops.items()}, cards={})
    for s in STRATEGIES:
        if s not in ledgers:
            continue
        tr = read_csv(ledgers[s])
        att = read_csv(attempts[s]) if s in attempts else None
        st = {k: read_csv(v[s]) for k, v in stress.items() if s in v}
        res["cards"][s] = {p: report_card(s, tr, ds, att, reg, st) for p, ds in pops.items()}
    Path(out).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    return res


def _kv(items: Sequence[str]) -> Dict[str, str]:
    return dict(x.split("=", 1) for x in items or [])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Phase 2 report card (Step B only)")
    ap.add_argument("--phase", required=True)
    ap.add_argument("--ledger", nargs="*", help="R1=path R2=path ...")
    ap.add_argument("--attempts", nargs="*", help="R3=path R4=path")
    ap.add_argument("--stress", nargs="*", help="lat1000:R1=path ...")
    ap.add_argument("--gex", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    st: Dict[str, Dict[str, str]] = {}
    for x in a.stress or []:
        k, rest = x.split(":", 1)
        s, p = rest.split("=", 1)
        st.setdefault(k, {})[s] = p
    run(a.phase, _kv(a.ledger), _kv(a.attempts), st, a.gex, a.out)
    print(f"report card -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
