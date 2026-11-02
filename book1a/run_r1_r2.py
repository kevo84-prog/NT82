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


# Book 1 phase configs (phase1_config.json .. phase4_config.json, identical in these keys): map history from UTC
# Sep 21, 2025 with map_from on that same date at 17:00 CT; holidays incl. Labor Day 2025; "; " separators.
BOOK1_MAP_FIRST_UTC = "20250921"
BOOK1_EXTRA_HOLIDAYS = {dt.date(2025, 9, 1)}


def build_bars(block1: Path, out: Path, last_session: dt.date) -> dict:
    """nq_1m.csv / es_1m.csv in the Book 1 pattern (backtest/phase3/build_inputs.py, phase4/build_inputs.py): Book 1
    block_inputs.bars_csv from raw/block1/<sym>_ohlcv_1m with the roll-fix files roll_<SYM>*_ohlcv_1m_202*, UTC
    Jul 20, 2025 to the last session, then cut at the last session 17:00:00 CT. Built from raw, never copied from a
    Book 1 phase folder. Skipped when both files already exist in out."""
    from jeron_engine import block_inputs
    cut = f"{last_session.isoformat()} 17:00:00"
    info, cwd = {}, os.getcwd()
    os.chdir(block1)                    # bars_csv globs are relative to the Book 1 root, as in the phase scripts
    try:
        for sym in ("nq", "es"):
            f = out / f"{sym}_1m.csv"
            if not f.exists():
                block_inputs.bars_csv(f, f"raw/block1/{sym}_ohlcv_1m/*/*.ohlcv-1m.dbn.zst",
                                      f"raw/block1/roll_{sym.upper()}*_ohlcv_1m_202*/*/*.ohlcv-1m.dbn.zst", "20250720",
                                      last_session.strftime("%Y%m%d"))
                lines = open(f).read().splitlines()
                kept = [lines[0]] + [l for l in lines[1:] if l[:19] <= cut]
                open(f, "w", newline="").write("\n".join(kept) + "\n")
            lines = open(f).read().splitlines()
            info[sym] = dict(bars=len(lines) - 1, first=lines[1][:19], last=lines[-1][:19], cut=cut)
            if lines[-1][:19] > cut:
                raise SystemExit(f"{f}: bars after the cut {cut}")
    finally:
        os.chdir(cwd)
    return info


def phase_tapes_dir(block1: Path, out: Path, phase: str, first_utc: str, last_utc: str) -> Path:
    """The tape folder each Book 1 phase ran on. Phase 3 ran before the Phase 4 holdout rebuilt UTC Feb 4, 2026 in full;
    its Feb 4 tape was cut at 17:00 CT and is kept in tapes/phase3_cut/ (phase4/build_inputs.py). For phase3 a folder of
    hard links (read-only use) with that cut tape is made in out; every other run uses <block1>/tapes as is."""
    src = block1 / "tapes"
    cut = src / "phase3_cut" / "tape_20260204.csv.gz"
    if phase != "phase3" or not cut.exists():
        return src
    dst = out / "tapes_phase3"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("tape_*.csv.gz"):
        if first_utc <= f.name[5:13] <= last_utc and not (dst / f.name).exists():
            os.link(cut if f.name == cut.name else f, dst / f.name)
    return dst


def book1_cfg(block1: Path, sessions: list, out: Path, fill_model: str, map_first_utc: str = None) -> dict:
    """The daily_loop config in the Book 1 phase pattern (backtest/phase3/build_inputs.py, phase4/build_inputs.py):
    strategy warm-up from the UTC day two days before the first session (17:00 CT), run to the last session 16:15 CT,
    one --instrument label per phase (the harness uses it as a label only), EsInstrument map/strategy settings,
    tapes in <block1>/tapes, 1-minute bars cut at the last session 17:00 CT. map_first_utc (the map's history
    start) is Book 1's (phase2_config.json, kept by every phase): UTC Sep 21, 2025; map_from = that date 17:00 CT.
    holidays / half_days are written exactly as in the Book 1 configs ("; " separated, Labor Day 2025 included)."""
    s0, s1 = sessions[0], sessions[-1]
    nq_label, es_label = labels_for(s1)
    first_utc = map_first_utc or BOOK1_MAP_FIRST_UTC
    warm = s0 - dt.timedelta(days=2)
    return dict(
        sessions=[d.isoformat() for d in sessions], tapes_dir=str(block1 / "tapes"),
        map_first_utc=first_utc, strategy_first_utc=warm.strftime("%Y%m%d"), last_utc=s1.strftime("%Y%m%d"),
        nq_1m=str(out / "nq_1m.csv"), es_1m=str(out / "es_1m.csv"),
        calendar=str(block1 / "econ_calendar_2025-10_2026-04.csv"), gex=str(block1 / "gex_levels_block1.csv"),
        out_dir=str(out), map_from=f"{dt.datetime.strptime(first_utc, '%Y%m%d').date().isoformat()} 17:00",
        strategy_from=f"{warm.isoformat()} 17:00", to=f"{s1.isoformat()} 16:15",
        holidays="; ".join(d.isoformat() for d in sorted(set(S.NO_CASH_SESSION) | BOOK1_EXTRA_HOLIDAYS)),
        half_days="; ".join(f"{d.isoformat()}@12:00" for d in sorted(S.HALF_DAYS)),
        roll_dates=[d.isoformat() for d in sorted(S.ROLL_DATES)], instrument=nq_label, fill_model=fill_model,
        map_settings=[f"EsInstrument={es_label}"], strategy_settings=[f"EsInstrument={es_label}"],
    )


def attempt_targets(AR, log, veto=None) -> dict:
    """(event, 'YYYY-MM-DD HH:MM:SS' of the queueing bar) -> TargetPrice of the row the replay used for that attempt.
    Book 1's arm_replay.replay takes the target from the attempt's row (the candidate, or its CONFIRM row for an
    AwaitConfirm entry; the RH1 retest path keeps it) but does not return it; AR.attempts is the same call."""
    out = {}
    for a in AR.attempts(log, veto):
        out[(a["event"], a["t"].strftime("%Y-%m-%d %H:%M:%S"))] = float(a["row"]["TargetPrice"])
    return out


def to_trades(strategy: str, rep: dict, fill_model: str, risk_decision: str, targets: dict = None) -> list:
    out = []
    for t in rep["trades"]:
        side = "LONG" if t["side"] == "Long" else "SHORT"
        stop = t["entry"] - t["risk_ticks"] * L.TICK if side == "LONG" else t["entry"] + t["risk_ticks"] * L.TICK
        target = (targets or {}).get((t["event"], f"{t['date']} {t['signal_time']}"), float("nan"))
        out.append(L.Trade(strategy, t["event"], t["date"], t["entry_time"].strftime("%H:%M:%S.%f")[:12], side, 1,
                           float(t["entry"]), float(stop), target, t["exit_time"].strftime("%H:%M:%S.%f")[:12] if t["exit_time"] else "",
                           float(t["exit"]), {"STOP": "STOP_FIRST", "TARGET": "TARGET_FIRST", "FLATTEN": "TIME_EXIT"}.get(t["reason"], t["reason"]),
                           risk_decision, None, fill_model, 1, 250))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--phase", choices=list(S.PHASES)); ap.add_argument("--sessions", nargs="*")
    ap.add_argument("--fill", choices=["book1", "v3.4", "v3.5"], default="book1")
    ap.add_argument("--skip-daily-loop", action="store_true", help="reuse an existing A0 run in --out")
    ap.add_argument("--map-first-utc", default=None, help="map history start (UTC yyyymmdd); default Book 1's 20250921")
    a = ap.parse_args(argv)
    block1, out = Path(a.block1).resolve(), Path(a.out).resolve()   # absolute: build_bars changes folder
    os.environ["BOOK1_ROOT"] = str(block1)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, daily_loop as DL, fills
    sess = S.phase_sessions(a.phase) if a.phase else [dt.date.fromisoformat(s) for s in a.sessions]
    phase_fill = "v3.5" if a.phase in ("phase3", "phase4") else "v3.4"
    f1 = f2 = a.fill if a.fill != "book1" else phase_fill
    out.mkdir(parents=True, exist_ok=True)
    cfg = book1_cfg(block1, sess, out, f1, a.map_first_utc)
    cfg["tapes_dir"] = str(phase_tapes_dir(block1, out, a.phase, cfg["map_first_utc"], cfg["last_utc"]))
    cfg["bars"] = build_bars(block1, out, sess[-1])
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
    t1 = to_trades("R1_A0", r1, f1, "N/A (Book 1 sizing, qty 1)", attempt_targets(AR, log))
    t2 = to_trades("R2_C1", r2, f2, "N/A (Book 1 sizing, qty 1)", attempt_targets(AR, log, veto))
    missing_target = [t.trade_id for t in t1 + t2 if t.target != t.target]
    if missing_target:
        raise SystemExit(f"no target found for {missing_target}")
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
