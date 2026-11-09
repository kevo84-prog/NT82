r"""Exit steps M0 -> M-J1 -> M-J2, and exit cue (a), as session net R beside M0 (replay plan section 5; C5, U4). Diagnostic.

Written Nov 9, 2026 (Phase 4 Step A), before any Phase 4 run; registered in Phase4_registration.md section 4; tested on
synthetic rows only (book1a/tests/test_mj_steps.py). R4 is fixed at M0 (E1); these numbers never change R4.

  python -m book1a.mj_steps --phase phase4 --ledger R4=<R4 ledger> --ledger R1=<R1 ledger> \
      --diag <diag folder with diag_exit_trades.csv> --out <json>

Per trade (join: diag_exit_trades.trade_id = ledger trade_id, same strategy; every ledger trade must have exactly one
diag row):
  M0     the ledger realized_net_R (checked: recomputed below from the ledger's entry, stop, exit and qty, it must equal
         the ledger value to 4 decimals, otherwise a hard error);
  M-J1   mj1_status OK: one leg, the whole qty exits at mj1_exit_price; otherwise (NOT_APPLICABLE: no ladder, ...) the M0
         exit is kept;
  M-J2   mj2_status OK: leg 1 (mj2_leg1_qty at mj2_leg1_exit_price) + leg 2 (mj2_leg2_qty at mj2_leg2_exit_price), the leg
         quantities must add up to the ledger qty; otherwise (1 NQ, no TP1 beyond entry, no ladder) the trade keeps its
         M-J1 exit (= M0 when M-J1 does not apply): M-J2 differs from M-J1 only where it applies.
  CUE_A  exit cue (a) (Kyron's addendum, Nov 9, 2026): cue_fired Y: the whole qty exits at cue_exit_price (the
         market exit 250 ms after the trigger bar's close, diag_phase1b); otherwise (N, NOT_APPLICABLE) the M0 exit is
         kept. Compared with M0 (it is not a step in the M-J chain).
  R      the ledger formula (book1a.ledger.Trade): per leg move ticks = round(sign x (exit - entry) / 0.25); gross = sum of
         move ticks x $5 x leg qty; commission 2 x $2.87 x qty (same commissions as M0, U4); net R = (gross - commission)
         / (stop ticks x $5 x qty), stop ticks = round(|entry - stop| / 0.25).
Session net R, net R per session, the 90% session bootstrap (seed 20251205, 10,000) and max drawdown: phase2_report.core
on the ledger rows with realized_net_R replaced (the report card's own code). Populations: ALL and UNEXPOSED of the phase.
Reported per step: trades, trades changed versus the step before, net R per session, CI, max drawdown; M-J2 also by size
bucket (2, 3, 4+ NQ). R1 (and R2 / R3) plans carry no ladder, so every M-J step equals M0 for them (counted, reported).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

from book1a import phase2_report as RP, sessions as S
from book1a.ledger import COMMISSION_PER_SIDE, TICK, TICK_VALUE

VERSION = "mj-steps-v1.0"
STEPS = ("M0", "M-J1", "M-J2")
SERIES = STEPS + ("CUE_A",)


def read_diag(path) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))


def net_r(side: str, entry: float, stop: float, legs, qty: int) -> float:
    sign = 1 if side.upper() == "LONG" else -1
    st = int(round(abs(entry - stop) / TICK))
    if st == 0 or qty <= 0:
        raise ValueError("stop ticks or qty is 0")
    if sum(q for q, _ in legs) != qty:
        raise ValueError(f"leg quantities {[q for q, _ in legs]} do not add up to qty {qty}")
    gross = sum(int(round(sign * (x - entry) / TICK)) * TICK_VALUE * q for q, x in legs)
    return (gross - 2 * COMMISSION_PER_SIDE * qty) / (st * TICK_VALUE * qty)


def per_trade(ledger: List[dict], diag: List[dict], strategy: str) -> List[dict]:
    d = {}
    for x in diag:
        if x["strategy"] != strategy:
            continue
        if x["trade_id"] in d:
            raise ValueError(f"{strategy}: two diag rows for {x['trade_id']}")
        d[x["trade_id"]] = x
    out = []
    for t in ledger:
        x = d.get(t["trade_id"])
        if x is None:
            raise ValueError(f"{strategy}: no diag_exit_trades row for {t['trade_id']}")
        side, qty = t["side"], int(float(t["qty"]))
        e, s = float(t["entry_price"]), float(t["stop"])
        m0 = net_r(side, e, s, [(qty, float(t["exit_price"]))], qty)
        if abs(round(m0, 4) - float(t["realized_net_R"])) > 1e-9:
            raise ValueError(f"{t['trade_id']}: recomputed M0 R {m0:.4f} != ledger {t['realized_net_R']}")
        mj1 = net_r(side, e, s, [(qty, float(x["mj1_exit_price"]))], qty) if x["mj1_status"] == "OK" else m0
        if x["mj2_status"] == "OK":
            mj2 = net_r(side, e, s, [(int(float(x["mj2_leg1_qty"])), float(x["mj2_leg1_exit_price"])),
                                     (int(float(x["mj2_leg2_qty"])), float(x["mj2_leg2_exit_price"]))], qty)
        else:
            mj2 = mj1
        cue = net_r(side, e, s, [(qty, float(x["cue_exit_price"]))], qty) if x.get("cue_fired") == "Y" else m0
        out.append(dict(trade_id=t["trade_id"], session=t["date"], qty=qty, mj1_status=x["mj1_status"], mj2_status=x["mj2_status"],
                        cue_fired=x.get("cue_fired", ""), mj2_size_bucket=x.get("mj2_size_bucket", ""),
                        R={"M0": m0, "M-J1": mj1, "M-J2": mj2, "CUE_A": cue}))
    return out


def summary(ledger: List[dict], pt: List[dict], sessions) -> dict:
    by_id = {p["trade_id"]: p for p in pt}
    res, prev = {}, None
    for step in SERIES:
        rows = [dict(t, realized_net_R=repr(by_id[t["trade_id"]]["R"][step])) for t in ledger]
        c = RP.core("R4", rows, sessions)
        c.pop("max_drawdown_usd", None)
        ids = {t["trade_id"] for t in RP.in_pop(ledger, sessions)}
        base = "M0" if step == "CUE_A" else prev
        if base:
            c["trades_changed_vs_" + base] = sum(1 for p in pt if p["trade_id"] in ids and abs(p["R"][step] - p["R"][base]) > 1e-12)
        res[step] = c
        prev = step
    ids = {t["trade_id"] for t in RP.in_pop(ledger, sessions)}
    res["status_counts"] = {"M-J1": dict(Counter(p["mj1_status"] for p in pt if p["trade_id"] in ids)),
                            "M-J2": dict(Counter(p["mj2_status"] for p in pt if p["trade_id"] in ids)),
                            "CUE_A": dict(Counter(p["cue_fired"] for p in pt if p["trade_id"] in ids))}
    res["mj2_by_size_bucket"] = {}
    for b in ("2", "3", "4+"):
        sel = [p for p in pt if p["trade_id"] in ids and p["mj2_status"] == "OK" and p["mj2_size_bucket"] == b]
        res["mj2_by_size_bucket"][b] = dict(trades=len(sel), sum_R_MJ1=round(sum(p["R"]["M-J1"] for p in sel), 6),
                                            sum_R_MJ2=round(sum(p["R"]["M-J2"] for p in sel), 6))
    return res


def run(phase: str, ledgers: Dict[str, str], diag: str, out: str) -> dict:
    sess = S.phase_sessions(phase)
    pops = RP.populations(sess, phase)
    dpath = Path(diag) / "diag_exit_trades.csv"
    drows = read_diag(dpath)
    res = dict(version=VERSION, phase=phase, label="replay (in-sample), diagnostic only; R4 stays at M0 (E1)",
               diag=dict(path=str(dpath), sha256=hashlib.sha256(dpath.read_bytes()).hexdigest()), strategies={})
    for s, p in ledgers.items():
        led = RP.read_csv(p)
        pt = per_trade(led, drows, s)
        res["strategies"][s] = dict(ledger=dict(path=str(p), sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest()),
                                    populations={k: summary(led, pt, v) for k, v in pops.items()})
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=list(RP.EXPOSED_BY_PHASE)); ap.add_argument("--diag", required=True)
    ap.add_argument("--ledger", action="append", required=True, help="STRATEGY=path, e.g. R4=...R4_M0_ledger.csv")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    led = dict(x.split("=", 1) for x in a.ledger)
    run(a.phase, led, a.diag, a.out)
    print("written", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
