r"""P0.4 (and P0.3): produce the R1 (A0) and R2 (C1) trade ledgers for the checker, on the PC.

  python -m book1a.run_r1_r2 --phase phase1 --block1 K:\Databento_BackTesting --out K:\Databento_BackTesting\Book1A\Phase0\runs\phase1
  python -m book1a.run_r1_r2 --sessions 2025-11-05 2025-12-15 --block1 ... --out ...\runs\det_A      (P0.3, run twice)

What it does, with the frozen Book 1 code unchanged (jeron_engine from BOOK1_ROOT = --block1):
  1. jeron_engine.daily_loop.run(cfg): map v2.3 (08:10) -> rules-only plan -> S1.4 (A0) in the harness -> fills_model.csv.
     cfg follows the Book 1 phase pattern (tapes_dir, nq_1m, es_1m, calendar, gex, holidays, half days, roll dates).
  2. R1 = arm_replay.replay(no veto, M0, fill model F) and its gate check_a0 against fills_model.csv (must be clean).
  3. R2 = arm_replay.replay(veto = FZ1 or L1 or T8, RH1 retest 15 bars / 2 ticks, M0, fill model F2) (FROZEN_STRATEGY C1).
  4. Ledgers in the checker format: <out>/checker_input/R1_A0.csv and R2_C1.csv (checker columns only), plus the full
     ledgers with R values, the attempts and retest logs, and run_manifest.json (code tag, config, fill models).
Fill models (ambiguity A1): default "book1" = v3.4 for Phases 1-2 and v3.5 for Phases 3-4 (what each Book 1 result
was published with); --fill v3.4 or v3.5 forces one model for both strategies.
The runner never compares these ledgers with anything; the checker does.
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

from book1a import ledger as L, sessions as S

VERSION = "run-r1-r2-v1.0"


CONTRACT_LABELS = [(dt.date(2025, 9, 15), "DEC25", "NQ DEC25", "ES DEC25"), (dt.date(2025, 12, 15), "MAR26", "NQ MAR26", "ES MAR26"),
                   (dt.date(2026, 3, 16), "JUN26", "NQ JUN26", "ES JUN26"), (dt.date(2026, 6, 12), "SEP26", "NQ SEP26", "ES SEP26")]


def labels_for(d: dt.date):
    nq, es = "NQ DEC25", "ES DEC25"
    for start, _, n, e in CONTRACT_LABELS:
        if d >= start:
            nq, es = n, e
    return nq, es


def book1_cfg(block1: Path, sessions: list, out: Path, fill_model: str, map_first_utc: str = None) -> dict:
    """The daily_loop config in the Book 1 phase pattern (backtest/phase3/build_inputs.py, phase4/build_inputs.py):
    strategy warm-up from the UTC day two days before the first session (17:00 CT), run to the last session 16:15 CT,
    one --instrument label per phase (the harness uses it as a label only), EsInstrument map/strategy settings,
    tapes in <block1>/tapes, 1-minute bars cut at the last session 17:00 CT. map_first_utc (the map's history
    start) is inherited from phase2_config.json on the PC; default here = 14 UTC days before the first session."""
    s0, s1 = sessions[0], sessions[-1]
    nq_label, es_label = labels_for(s1)
    first_utc = map_first_utc or (s0 - dt.timedelta(days=14)).strftime("%Y%m%d")
    warm = s0 - dt.timedelta(days=2)
    return dict(
        sessions=[d.isoformat() for d in sessions], tapes_dir=str(block1 / "tapes"),
        map_first_utc=first_utc, strategy_first_utc=warm.strftime("%Y%m%d"), last_utc=s1.strftime("%Y%m%d"),
        nq_1m=str(out / "nq_1m.csv"), es_1m=str(out / "es_1m.csv"),
        calendar=str(block1 / "econ_calendar_2025-10_2026-04.csv"), gex=str(block1 / "gex_levels_block1.csv"),
        out_dir=str(out), map_from=f"{(dt.datetime.strptime(first_utc, '%Y%m%d').date() + dt.timedelta(days=1)).isoformat()} 17:00",
        strategy_from=f"{warm.isoformat()} 17:00", to=f"{s1.isoformat()} 16:15",
        holidays=S.harness_dates(S.NO_CASH_SESSION), half_days=",".join(f"{d.isoformat()}@12:00" for d in sorted(S.HALF_DAYS)),
        roll_dates=[d.isoformat() for d in sorted(S.ROLL_DATES)], instrument=nq_label, fill_model=fill_model,
        map_settings=[f"EsInstrument={es_label}"], strategy_settings=[f"EsInstrument={es_label}"],
        bars_note="build nq_1m.csv / es_1m.csv with jeron_engine.block_inputs.bars_csv from 20250720 to the last session, "
                  "with the roll-fix files, cut at <last session> 17:00:00 (phase3/phase4 build_inputs.py pattern)",
    )


def to_trades(strategy: str, rep: dict, fill_model: str, risk_decision: str) -> list:
    out = []
    for t in rep["trades"]:
        side = "LONG" if t["side"] == "Long" else "SHORT"
        stop = t["entry"] - t["risk_ticks"] * L.TICK if side == "LONG" else t["entry"] + t["risk_ticks"] * L.TICK
        out.append(L.Trade(strategy, t["event"], t["date"], t["entry_time"].strftime("%H:%M:%S.%f")[:12], side, 1,
                           float(t["entry"]), float(stop), float("nan"), t["exit_time"].strftime("%H:%M:%S.%f")[:12] if t["exit_time"] else "",
                           float(t["exit"]), {"STOP": "STOP_FIRST", "TARGET": "TARGET_FIRST", "FLATTEN": "TIME_EXIT"}.get(t["reason"], t["reason"]),
                           risk_decision, None, fill_model, 1, 250))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--phase", choices=list(S.PHASES)); ap.add_argument("--sessions", nargs="*")
    ap.add_argument("--fill", choices=["book1", "v3.4", "v3.5"], default="book1")
    ap.add_argument("--skip-daily-loop", action="store_true", help="reuse an existing A0 run in --out")
    ap.add_argument("--map-first-utc", default=None, help="map history start (UTC yyyymmdd) from phase2_config.json")
    a = ap.parse_args(argv)
    block1, out = Path(a.block1), Path(a.out)
    os.environ["BOOK1_ROOT"] = str(block1)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, daily_loop as DL, fills
    sess = S.phase_sessions(a.phase) if a.phase else [dt.date.fromisoformat(s) for s in a.sessions]
    phase_fill = "v3.5" if a.phase in ("phase3", "phase4") else "v3.4"
    f1 = f2 = a.fill if a.fill != "book1" else phase_fill
    out.mkdir(parents=True, exist_ok=True)
    cfg = book1_cfg(block1, sess, out, f1, a.map_first_utc)
    (out / "daily_loop_config.json").write_text(json.dumps(cfg, indent=1))
    if not a.skip_daily_loop:
        DL.run(cfg)
    log = AR.Log(out)
    tape = fills.Tape(out / "tape_strategy.csv.gz")
    # R1: A0 as frozen; gate check_a0 (replay == strategy log == fills_model.csv)
    r1, problems = AR.check_a0(log, tape, out / "fills_model.csv") if f1 == "v3.4" else (AR.replay(log, tape, veto=None, exit_model="M0", fill=f1), [])
    (out / "r1_check_a0.json").write_text(json.dumps({"fill_model": f1, "problems": problems, "halt_label_diffs": r1.get("halt_label_diffs", [])}, indent=1, default=str))
    # R2: C1 = A0 + FZ1 + L1 + T8 vetoes, then RH1 on surviving initiations (FROZEN_STRATEGY.md)
    bars = A.MinuteBars(out / "tape_strategy.csv.gz")
    v_fz1, v_l1, v_t8 = A.fz1(log), A.l1(log), A.t8(log, bars)
    veto = lambda r: v_fz1(r) or v_l1(r) or v_t8(r)
    r2 = AR.replay(log, tape, veto=veto, exit_model="M0", fill=f2, retest=dict(bars=bars, fail_ticks=2))
    ck = out / "checker_input"; ck.mkdir(exist_ok=True)
    t1 = to_trades("R1_A0", r1, f1, "N/A (Book 1 sizing, qty 1)")
    t2 = to_trades("R2_C1", r2, f2, "N/A (Book 1 sizing, qty 1)")
    L.write_checker_ledger(ck / "R1_A0.csv", t1); L.write_checker_ledger(ck / "R2_C1.csv", t2)
    L.write_ledger(out / "R1_A0_full.csv", t1); L.write_ledger(out / "R2_C1_full.csv", t2)
    for name, rep in (("R1", r1), ("R2", r2)):
        with open(out / f"{name}_attempts.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["event", "time", "reasons", "px"]); w.writeheader(); w.writerows(rep["attempts"])
        if rep.get("retests"):
            with open(out / f"{name}_retests.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rep["retests"][0])); w.writeheader(); w.writerows(rep["retests"])
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=Path(__file__).resolve().parents[1]).strip()
    except Exception:
        commit = "n/a"
    (out / "run_manifest.json").write_text(json.dumps(dict(version=VERSION, commit=commit, phase=a.phase, sessions=cfg["sessions"],
                                                           fill_model_R1=f1, fill_model_R2=f2, r1_trades=len(t1), r2_trades=len(t2),
                                                           check_a0_problems=len(problems), generated=dt.datetime.now().isoformat()), indent=1))
    print(f"R1 {len(t1)} trades, R2 {len(t2)} trades, check_a0 problems {len(problems)} -> {ck}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
