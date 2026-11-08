r"""Phase 3 primary comparisons: a thin wrapper around Book 1's frozen promotion rule (Phase3_registration.md section 5).

  python -m book1a.phase3_compare --block1 K:\Book1A_inputs --a0-run <R1/R2 run> --r3-run <R3 run> --r4-run <R4 run> \
      --slip2 <run_stress --stress slip2 folder> --out <new folder>

Imports and calls jeron_engine.arms.promotion UNCHANGED (seed 20251205, n 10,000). No formula is re-implemented here:
this module only maps Book 1A ledger rows to the dicts arms.promotion reads, checks them, and calls it.

  P1  R4 vs R1      P2  R4 vs R3      P3  R3 vs R2          (arm vs comparator; arms.promotion(arm, a0, ...))

Populations (registered Nov 8, 2026): ALL = the 41 Phase 3 sessions, "in-sample, includes 3 exposed sessions (Part 3)",
decides; UNEXPOSED = the 38 sessions without the exposed ones (phase2_report.EXPOSED_BY_PHASE["phase3"]), a registered
sensitivity, never independent or out-of-sample. Verdicts that differ -> SENSITIVE_TO_EXPOSED_SESSIONS (no selection).
A population's sessions = the registered list (zero-trade sessions included); its trades = the trades on those sessions.

Trade dict per ledger row (the fields arms.promotion, per_session, max_dd and differing_trades read):
  date         ledger `date` (YYYY-MM-DD; the sessions are given in the same form)
  signal_time  Book 1's replay definition (arm_replay.replay: "the candidate's queueing bar" = arm_replay.attempts t,
               the EvidenceTimeCT of the candidate row or of its CONFIRM row for an AwaitConfirm entry), HH:MM:SS as
               arm_replay writes it. Source, per run (its own files, never the strategy log re-read):
                 - the event has a retests row with outcome RETEST_ENTERED (RH1 path; R2, R3, R4): that row's `time`
                   (arm_replay / replay_risk write it with the queueing bar t); check: ledger entry_time = its `at`
                   + entry_latency_ms;
                 - otherwise (immediate path; R1 always): the event's single attempts row with no block reason
                   (arm_replay / replay_risk write it at t); check: ledger entry_time = its `time` + entry_latency_ms.
               event = ledger trade_id. No row, two rows, or a failed check -> error.
  entry, exit  ledger entry_price, exit_price
  exit_time    ledger date + " " + exit_time
  R            ledger realized_net_R (replay plan 4a: "Promotion uses realized net R"); missing -> error
2-tick inputs (arm_2t, a0_2t): the slip2 stress ledgers, same date / entry / exit / exit_time / R mapping. arms.promotion
reads only date and R from them (per_session); run_stress writes no attempts file, so their signal_time is None.
Errors before arms.promotion is called: duplicate (date, signal_time) key in a strategy, duplicate trade_id, missing
realized_net_R, a trade outside the 41 sessions.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

VERSION = "phase3-compare-v1.0"
PHASE = "phase3"
COMPARISONS = (("P1", "R4", "R1"), ("P2", "R4", "R3"), ("P3", "R3", "R2"))
LABEL_ALL = "in-sample, includes 3 exposed sessions (Part 3)"
LABEL_UNEXPOSED = "registered sensitivity on the 38 UNEXPOSED sessions; not independent, not out-of-sample"
SENSITIVE = "SENSITIVE_TO_EXPOSED_SESSIONS"
SAME = "SAME_VERDICT"
# run folder -> (ledger, attempts, retests) per strategy, as run_r1_r2 / run_r3 / run_r4 write them
FILES = {"R1": ("a0", "R1_A0_full.csv", "R1_attempts.csv", "R1_retests.csv"),
         "R2": ("a0", "R2_C1_full.csv", "R2_attempts.csv", "R2_retests.csv"),
         "R3": ("r3", "R3_M0_ledger.csv", "R3_attempts.csv", "R3_retests.csv"),
         "R4": ("r4", "R4_M0_ledger.csv", "R4_attempts.csv", "R4_retests.csv")}


class CompareInputError(RuntimeError):
    """An input that cannot be mapped without a new interpretation: stop before arms.promotion is called."""


def promotion_fn():
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arms
    return arms.promotion


# ------------------------------------------------------------------ mapping (no formula)
def _hms(s: str) -> str:
    return dt.datetime.fromisoformat(s).strftime("%H:%M:%S")


def _fill_stamp(s: str, latency_ms: int) -> str:
    return (dt.datetime.fromisoformat(s) + dt.timedelta(milliseconds=latency_ms)).strftime("%H:%M:%S.%f")[:12]


def _R(row: dict, strategy: str) -> float:
    v = row.get("realized_net_R")
    if v is None or str(v).strip() == "":
        raise CompareInputError(f"{strategy} trade {row.get('trade_id')}: realized_net_R missing")
    return float(v)


def _base(row: dict, strategy: str) -> dict:
    return dict(date=row["date"], entry=float(row["entry_price"]), exit=float(row["exit_price"]),
                exit_time=f"{row['date']} {row['exit_time']}", R=_R(row, strategy), trade_id=row["trade_id"])


def _unique_ids(rows: List[dict], strategy: str):
    seen = set()
    for r in rows:
        if r["trade_id"] in seen:
            raise CompareInputError(f"{strategy}: duplicate trade_id {r['trade_id']}")
        seen.add(r["trade_id"])


def signal_time(row: dict, attempts: List[dict], retests: List[dict], strategy: str) -> str:
    ev, lat = row["trade_id"], int(row.get("entry_latency_ms") or 250)
    entered = [r for r in retests if r["event"] == ev and r.get("outcome") == "RETEST_ENTERED"]
    if len(entered) > 1:
        raise CompareInputError(f"{strategy} trade {ev}: {len(entered)} RETEST_ENTERED rows")
    if entered:
        src, fill_at = entered[0]["time"], entered[0]["at"]
    else:
        order = [a for a in attempts if a["event"] == ev and (a.get("reasons") or "") == ""]
        if len(order) != 1:
            raise CompareInputError(f"{strategy} trade {ev}: {len(order)} attempts rows without a block reason")
        src = fill_at = order[0]["time"]
    if dt.datetime.fromisoformat(src).date().isoformat() != row["date"]:
        raise CompareInputError(f"{strategy} trade {ev}: signal bar {src} not on the ledger date {row['date']}")
    if _fill_stamp(fill_at, lat) != row["entry_time"]:
        raise CompareInputError(f"{strategy} trade {ev}: entry_time {row['entry_time']} != {fill_at} + {lat} ms")
    return _hms(src)


def map_trades(ledger: List[dict], attempts: List[dict], retests: List[dict], strategy: str) -> List[dict]:
    _unique_ids(ledger, strategy)
    out = [dict(_base(r, strategy), signal_time=signal_time(r, attempts, retests, strategy)) for r in ledger]
    check_keys(out, strategy)
    return out


def map_stress(ledger: List[dict], strategy: str) -> List[dict]:
    _unique_ids(ledger, strategy)
    return [dict(_base(r, strategy), signal_time=None) for r in ledger]


def check_keys(trades: List[dict], strategy: str):
    seen = set()
    for t in trades:
        k = (t["date"], t["signal_time"])
        if k in seen:
            raise CompareInputError(f"{strategy}: duplicate (date, signal_time) key {k}")
        seen.add(k)


def check_sessions(trades: Dict[str, List[dict]], sessions: List[str]):
    s = set(sessions)
    for name, ts in trades.items():
        bad = sorted({t["date"] for t in ts} - s)
        if bad:
            raise CompareInputError(f"{name}: trades outside the registered sessions: {bad}")


# ------------------------------------------------------------------ the comparison (arms.promotion unchanged)
def compare(trades: Dict[str, List[dict]], trades_2t: Dict[str, List[dict]], sessions: List[str], exposed,
            promotion=None, comparisons=COMPARISONS) -> dict:
    """trades / trades_2t: strategy -> mapped trade dicts. sessions: the registered ISO dates (all of them).
    Returns {comparison: {ALL: promotion dict, UNEXPOSED: promotion dict, labels, sensitivity}}."""
    promotion = promotion or promotion_fn()
    for name, ts in trades.items():
        check_keys(ts, name)
    check_sessions(trades, sessions)
    check_sessions({f"{k} slip2": v for k, v in trades_2t.items()}, sessions)
    exposed = {str(d) for d in exposed}
    pops = {"ALL": list(sessions), "UNEXPOSED": [d for d in sessions if d not in exposed]}
    out = {}
    for cid, arm, comp in comparisons:
        res = {}
        for pop, ss in pops.items():
            keep = set(ss)
            sel = lambda ts: [t for t in ts if t["date"] in keep]   # noqa: E731  the population's trades
            res[pop] = promotion({"trades": sel(trades[arm])}, {"trades": sel(trades[comp])}, ss,
                                 arm_2t={"trades": sel(trades_2t[arm])}, a0_2t={"trades": sel(trades_2t[comp])})
        out[cid] = dict(arm=arm, comparator=comp, ALL=res["ALL"], UNEXPOSED=res["UNEXPOSED"],
                        label_ALL=LABEL_ALL, label_UNEXPOSED=LABEL_UNEXPOSED, deciding_population="ALL",
                        sensitivity=SAME if res["ALL"]["verdict"] == res["UNEXPOSED"]["verdict"] else SENSITIVE)
    return out


# ------------------------------------------------------------------ files
def read_rows(p: Path) -> List[dict]:
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(runs: Dict[str, Path], slip2: Path, out: Path, promotion=None) -> dict:
    from book1a import phase2_report as RP, sessions as S
    sessions = [d.isoformat() for d in S.phase_sessions(PHASE)]
    exposed = sorted(d.isoformat() for d in RP.EXPOSED_BY_PHASE[PHASE])
    inputs, trades, trades_2t = {}, {}, {}
    for k, (run_key, led, att, ret) in FILES.items():
        base = runs[run_key]
        for p in (base / led, base / att):
            if not p.exists():
                raise CompareInputError(f"{p}: missing")
        trades[k] = map_trades(read_rows(base / led), read_rows(base / att), read_rows(base / ret), k)
        s2 = slip2 / led
        if not s2.exists():
            raise CompareInputError(f"{s2}: missing")
        trades_2t[k] = map_stress(read_rows(s2), k)
        for p in (base / led, base / att, base / ret, s2):
            if p.exists():
                inputs[str(p)] = sha256(p)
    res = compare(trades, trades_2t, sessions, exposed, promotion=promotion)
    for p, h in inputs.items():
        if sha256(Path(p)) != h:
            raise CompareInputError(f"{p}: changed during the run")
    out.mkdir(parents=True, exist_ok=False)
    doc = dict(version=VERSION, phase=PHASE, rule="jeron_engine.arms.promotion (Book 1, unchanged)", seed=20251205,
               sessions_ALL=len(sessions), sessions_UNEXPOSED=len(sessions) - len(exposed), exposed=exposed,
               inputs_sha256=inputs, comparisons=res,
               generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    (out / "phase3_compare.json").write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--a0-run", required=True)
    ap.add_argument("--r3-run", required=True); ap.add_argument("--r4-run", required=True)
    ap.add_argument("--slip2", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    os.environ["BOOK1_ROOT"] = str(Path(a.block1).resolve())
    runs = {"a0": Path(a.a0_run).resolve(), "r3": Path(a.r3_run).resolve(), "r4": Path(a.r4_run).resolve()}
    run(runs, Path(a.slip2).resolve(), Path(a.out).resolve())
    print(f"written: {Path(a.out).resolve() / 'phase3_compare.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
