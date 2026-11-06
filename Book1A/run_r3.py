r"""R3 = C1 + risk on a finished A0 run (Book 1A Phase 1 and later).

  python -m book1a.run_r3 --block1 K:\Book1A_inputs --a0-run book1a\Phase1\runs\phase1 --out book1a\Phase1\runs\phase1_r3

The same call Phase 0 made inline for P0.12 (RUNBOOK_PC.md, P0.12 line), now as a script:
R2's signals unchanged (veto = FZ1 or L1 or T8, RH1 retest 15 bars / 2 ticks, M0) through replay_risk.replay with
the C3 pre-trade dollar risk check, U3 sizing, the dollar daily limit, fill model v3.5.
Reads the A0 run read-only; writes R3_M0_ledger.csv, R3_attempts.csv, R3_retests.csv, R3_risk_events.json and
run_manifest.json into --out. Never summarizes a result.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

from book1a import ledger as L

VERSION = "run-r3-v1.0"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--a0-run", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--fill", choices=["v3.4", "v3.5"], default="v3.5")
    a = ap.parse_args(argv)
    a0, out = Path(a.a0_run).resolve(), Path(a.out).resolve()
    os.environ["BOOK1_ROOT"] = str(Path(a.block1).resolve())
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, fills
    from book1a import replay_risk as RR
    out.mkdir(parents=True, exist_ok=True)
    log = AR.Log(a0)
    tape = fills.Tape(a0 / "tape_strategy.csv.gz")
    bars = A.MinuteBars(a0 / "tape_strategy.csv.gz")
    v_fz1, v_l1, v_t8 = A.fz1(log), A.l1(log), A.t8(log, bars)
    rep = RR.replay(log, tape, "R3", veto=lambda r: v_fz1(r) or v_l1(r) or v_t8(r),
                    retest=dict(bars=bars, fail_ticks=2), fill=a.fill)
    n_tr = L.write_ledger(str(out / "R3_M0_ledger.csv"), rep["trades"])
    for name in ("attempts", "retests"):
        rows = rep[name]
        with open(out / f"R3_{name}.csv", "w", newline="") as f:
            cols = list(dict.fromkeys(k for r in rows for k in r)) or ["event"]
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    (out / "R3_risk_events.json").write_text(json.dumps(rep["risk_events"], indent=1, default=str))
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=Path(__file__).resolve().parents[1]).strip()
    except Exception:
        commit = "n/a"
    sessions = json.loads((a0 / "daily_loop_config.json").read_text())["sessions"]
    (out / "run_manifest.json").write_text(json.dumps(dict(
        version=VERSION, commit=commit, a0_run=str(a0), sessions=sessions, fill_model=a.fill, veto="FZ1|L1|T8",
        retest="RH1 15 bars / 2 ticks", exit_model="M0", risk="C3 / U3", trades=n_tr,
        generated=dt.datetime.now().isoformat()), indent=1))
    print(f"R3 on {a0.name}: {len(sessions)} sessions, ledger rows written -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
