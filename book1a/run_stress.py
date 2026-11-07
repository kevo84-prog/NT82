r"""Stress ledgers for R1-R4 from existing base runs (Phase 2 report card; registered in Step A, Nov 6, 2026).

  python -m book1a.run_stress --block1 K:\Book1A_inputs --a0-run <R1/R2 run> --r4-run <R4 run> --plans <Book 1A plans> \
      --stress lat1000 --out <folder>

Re-runs only the replays, with the same calls and arguments as run_r1_r2 (R1 at --fill v3.5, R2), run_r3 and run_r4,
on the same strategy logs and tapes; the harness is not run again. --stress picks the entry latency and stop
slippage (book1a.stress.SETTINGS). The whole replay is rerun under the stress setting, risk state and the 3-trade /
2-loss / daily-limit state included, so a stressed exit can change later decisions that day (as it would live).
Writes <out>/R1_A0_full.csv, R2_C1_full.csv, R3_M0_ledger.csv, R4_M0_ledger.csv and stress_manifest.json.
"--stress base" must reproduce the base ledgers byte for byte (checked on Phase 1 in Step A).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from book1a import ledger as L, stress as ST

VERSION = "run-stress-v1.0"


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--a0-run", required=True); ap.add_argument("--r4-run", required=True)
    ap.add_argument("--plans", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--stress", choices=list(ST.SETTINGS), required=True)
    a = ap.parse_args(argv)
    a0, r4, out = Path(a.a0_run).resolve(), Path(a.r4_run).resolve(), Path(a.out).resolve()
    os.environ["BOOK1_ROOT"] = str(Path(a.block1).resolve())
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, fills
    from book1a import replay_risk as RR, risk as RK, run_r1_r2 as R12, run_r4 as R4
    lat, slip = ST.SETTINGS[a.stress]
    out.mkdir(parents=True, exist_ok=True)
    sessions = json.loads((a0 / "daily_loop_config.json").read_text())["sessions"]
    if json.loads((r4 / "run_manifest.json").read_text())["sessions"] != sessions:
        raise SystemExit("--a0-run and --r4-run cover different sessions")
    plans = R4.load_book1a_plans(a.plans, sessions)
    with ST.entry_latency(lat):
        # R1 / R2 (run_r1_r2.main with --fill v3.5)
        log = AR.Log(a0)
        tape = fills.Tape(a0 / "tape_strategy.csv.gz")
        r1 = AR.replay(log, tape, veto=None, exit_model="M0", fill="v3.5", stop_slip=slip)
        bars = A.MinuteBars(a0 / "tape_strategy.csv.gz")
        v_fz1, v_l1, v_t8 = A.fz1(log), A.l1(log), A.t8(log, bars)
        veto2 = lambda r: v_fz1(r) or v_l1(r) or v_t8(r)
        r2 = AR.replay(log, tape, veto=veto2, exit_model="M0", fill="v3.5", stop_slip=slip, retest=dict(bars=bars, fail_ticks=2))
        t1 = R12.to_trades("R1_A0", r1, "v3.5", "N/A (Book 1 sizing, qty 1)", R12.attempt_targets(AR, log))
        t2 = R12.to_trades("R2_C1", r2, "v3.5", "N/A (Book 1 sizing, qty 1)", R12.attempt_targets(AR, log, veto2))
        for t in t1 + t2:
            t.stop_slippage_ticks, t.entry_latency_ms = slip, lat
        L.write_ledger(out / "R1_A0_full.csv", t1); L.write_ledger(out / "R2_C1_full.csv", t2)
        # R3 (run_r3.main, risk-c3-v2)
        r3 = RR.replay(log, tape, "R3", veto=veto2, retest=dict(bars=bars, fail_ticks=2), fill="v3.5", stop_slip=slip, risk_impl=RK.C3_V2)
        L.write_ledger(str(out / "R3_M0_ledger.csv"), r3["trades"], extra_columns=RR.V2_LEDGER_COLUMNS)
        # R4 (run_r4.main on the R4 run's own strategy log, risk-c3-v2)
        log4 = AR.Log(r4)
        tape4 = fills.Tape(r4 / "tape_strategy.csv.gz")
        bars4 = A.MinuteBars(r4 / "tape_strategy.csv.gz")
        w_l1, w_t8 = A.l1(log4), A.t8(log4, bars4)
        rep4 = RR.replay(log4, tape4, "R4", veto=lambda r: w_l1(r) or w_t8(r), retest=dict(bars=bars4, fail_ticks=2), fill="v3.5",
                         stop_slip=slip, risk_impl=RK.C3_V2)
        R4.write_ledger(out / "R4_M0_ledger.csv", rep4["trades"], plans, extra_columns=RR.V2_LEDGER_COLUMNS)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=Path(__file__).resolve().parents[1]).strip()
    except Exception:
        commit = "n/a"
    files = ("R1_A0_full.csv", "R2_C1_full.csv", "R3_M0_ledger.csv", "R4_M0_ledger.csv")
    (out / "stress_manifest.json").write_text(json.dumps(dict(
        version=VERSION, stress_version=ST.VERSION, commit=commit, stress=a.stress, entry_latency_ms=lat, stop_slip_ticks=slip,
        a0_run=str(a0), r4_run=str(r4), plans=str(Path(a.plans).resolve()), sessions=sessions,
        ledgers={f: sha(out / f) for f in files}, generated=dt.datetime.now().isoformat(timespec="seconds")), indent=1))
    print(f"stress {a.stress}: ledgers written -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
