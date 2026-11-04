r"""P0.4 recheck: R2 (C1) on Phase 2 with fill model v3.5 (Kyron, Nov 4, 2026).

  python -m book1a.recheck_c1_v35 --block1 K:\Databento_BackTesting --run Book1A\Phase0\runs\phase2 --out Book1A\Phase0\runs\phase2_c1_v35

Reads the finished Phase 2 A0 run (map, plans, S1.4 strategy log, strategy tape) read-only and repeats only the R2
call of run_r1_r2 (veto FZ1 or L1 or T8, RH1 retest 15 bars / 2 ticks, M0) with fill="v3.5" (the same v3.5 settings
run_r1_r2 uses on Phases 3-4). The daily loop is not rerun: the strategy log does not depend on the fill model.
The v3.4 ledger R2_C1_phase2.csv and the run folder are not touched. Writes <out>/checker_input/R2_C1_phase2_v35.csv
(checker columns), <out>/R2_C1_phase2_v35_full.csv, R2 attempts / retests and run_manifest.json.
The runner never compares this ledger with anything; the checker does.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from book1a import ledger as L
from book1a.run_r1_r2 import attempt_targets, to_trades

VERSION = "recheck-c1-v35-v1.0"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--run", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="R2_C1_phase2_v35")
    a = ap.parse_args(argv)
    block1, run, out = Path(a.block1).resolve(), Path(a.run).resolve(), Path(a.out).resolve()
    os.environ["BOOK1_ROOT"] = str(block1)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, fills
    inputs = {n: sha256(run / n) for n in ("tape_strategy.csv.gz", "daily_loop_config.json")}
    log = AR.Log(run)
    tape = fills.Tape(run / "tape_strategy.csv.gz")
    bars = A.MinuteBars(run / "tape_strategy.csv.gz")
    v_fz1, v_l1, v_t8 = A.fz1(log), A.l1(log), A.t8(log, bars)
    veto = lambda r: v_fz1(r) or v_l1(r) or v_t8(r)
    rep = AR.replay(log, tape, veto=veto, exit_model="M0", fill="v3.5", retest=dict(bars=bars, fail_ticks=2))
    trades = to_trades("R2_C1", rep, "v3.5", "N/A (Book 1 sizing, qty 1)", attempt_targets(AR, log, veto))
    missing = [t.trade_id for t in trades if t.target != t.target]
    if missing:
        raise SystemExit(f"no target found for {missing}")
    ck = out / "checker_input"; ck.mkdir(parents=True, exist_ok=True)
    L.write_checker_ledger(ck / f"{a.name}.csv", trades)
    L.write_ledger(out / f"{a.name}_full.csv", trades)
    with open(out / "R2_attempts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["event", "time", "reasons", "px"]); w.writeheader(); w.writerows(rep["attempts"])
    if rep.get("retests"):
        with open(out / "R2_retests.csv", "w", newline="") as f:
            cols = list(dict.fromkeys(k for r in rep["retests"] for k in r))
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rep["retests"])
    unchanged = {n: sha256(run / n) == h for n, h in inputs.items()}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=Path(__file__).resolve().parents[1]).strip()
    except Exception:
        commit = "n/a"
    (out / "run_manifest.json").write_text(json.dumps(dict(
        version=VERSION, commit=commit, source_run=str(run), source_inputs_sha256=inputs, source_unchanged=unchanged,
        strategy="R2_C1", phase="phase2", fill_model="v3.5", trades=len(trades),
        checker_file=f"{a.name}.csv", checker_sha256=sha256(ck / f"{a.name}.csv"),
        generated=dt.datetime.now().isoformat()), indent=1))
    print(f"R2 C1 Phase 2 v3.5: {len(trades)} trades -> {ck / (a.name + '.csv')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
