r"""Book 1A premarket plans for a phase with no trading run (Phase 2 Step A2, Nov 6, 2026).

  python -m book1a.build_plans_phase --block1 K:\Book1A_inputs --phase phase2 --out book1a\Phase2\runs\maps_phase2 \
      --plans book1a\Phase2\plans_phase2

Steps 1 and 2 of the frozen Book 1 daily loop only (jeron_engine.daily_loop.run, unchanged): the map tape, then the
JeronHarness map (v2.3 defaults, as-of 08:10), with the same config run_r1_r2.book1_cfg builds for a trading run
(map history from UTC Sep 21, 2025, holidays, half days, roll dates, instrument label, EsInstrument). Steps 3-6 (the
rules-only plan, the S1.4 strategy, the fill model, day sheets) are NOT run: no strategy log, no order, no fill.
Then the frozen Book 1A plan code (book1a.hand_checks.plan_hand_check.build_day -> plan_v24.build, the same call that
built plans_phase1) writes PreopenPlan_<day>_book1a.txt / .json for every session.
The map arguments are the daily loop's own (margs, copied line for line); --check-run compares the packets with a
trading run's map folder (JSON equal after removing built_local, the build wall clock).
Equivalence (Nov 6, 2026, on Phase 1): the 10 rebuilt plans and sidecars are byte-identical to plans_phase1, and all
32 map packets equal book1a\Phase1\runs\phase1\map except built_local.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import datetime as dt
from pathlib import Path

from book1a import sessions as S
from book1a.run_r1_r2 import book1_cfg, build_bars, phase_tapes_dir

VERSION = "build-plans-phase-v1.0"


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def packet_body(p: Path) -> dict:
    """A map packet without built_local (the wall-clock time the harness wrote it)."""
    x = json.loads(Path(p).read_text(encoding="utf-8"))
    x.pop("built_local", None)
    return x


def map_only(cfg: dict) -> str:
    """daily_loop.run steps 1 (map tape only) and 2 (map), unchanged."""
    from jeron_engine import daily_loop as DL
    from jeron_engine.mbo_tape import join_tapes
    out = Path(cfg["out_dir"]); out.mkdir(parents=True, exist_ok=True)
    s1 = cfg["sessions"][-1]
    map_tape = out / "tape_map.csv.gz"
    if not map_tape.exists(): join_tapes(map_tape, DL.day_tapes(cfg["tapes_dir"], cfg["map_first_utc"], cfg["last_utc"]))
    mdir = out / "map"; mdir.mkdir(exist_ok=True)
    margs = DL._mono() + [str(DL.EXE), "--map", f"--from={cfg['map_from']}", f"--to={s1} 09:00", f"--es={cfg['es_1m']}", f"--htf={cfg['nq_1m']}",
                          f"--instrument={cfg['instrument']}", str(map_tape), str(mdir),
                          f"HolidayDates={cfg['holidays']}", f"HalfDayDates={cfg['half_days']}"] + cfg.get("map_settings", [])
    log = DL._run(margs)[-1500:]
    (out / "map_log.txt").write_text(log, encoding="utf-8")
    return log


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True); ap.add_argument("--plans", required=True)
    ap.add_argument("--phase", choices=list(S.PHASES)); ap.add_argument("--sessions", nargs="*")
    ap.add_argument("--check-run", default=None, help="a trading run folder whose map/ packets must equal these byte for byte")
    a = ap.parse_args(argv)
    block1, out, plans = Path(a.block1).resolve(), Path(a.out).resolve(), Path(a.plans).resolve()
    os.environ["BOOK1_ROOT"] = str(block1)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from book1a.hand_checks import plan_hand_check as PHC
    sess = S.phase_sessions(a.phase) if a.phase else [dt.date.fromisoformat(s) for s in a.sessions]
    out.mkdir(parents=True, exist_ok=True); plans.mkdir(parents=True, exist_ok=True)
    cfg = book1_cfg(block1, sess, out, "n/a (no fills)")
    cfg["tapes_dir"] = str(phase_tapes_dir(block1, out, a.phase, cfg["map_first_utc"], cfg["last_utc"]))
    cfg["bars"] = build_bars(block1, out, sess[-1])
    (out / "map_only_config.json").write_text(json.dumps(cfg, indent=1))
    map_only(cfg)
    gex, cal = PHC.load_inputs(block1)
    rows = []
    for d in sess:
        ds = d.isoformat()
        text, side, _ = PHC.build_day(out, ds, gex, cal)
        (plans / f"PreopenPlan_{ds}_book1a.txt").write_text(text, encoding="utf-8")
        (plans / f"PreopenPlan_{ds}_book1a.json").write_text(json.dumps(side, indent=1, default=str), encoding="utf-8")
        pk = sorted((out / "map").glob(f"PreopenPacket_*{ds}.json"))[0]
        rows.append(dict(session=ds, packet=pk.name, packet_sha256=sha(pk), plan_sha256=sha(plans / f"PreopenPlan_{ds}_book1a.txt"),
                         sidecar_sha256=sha(plans / f"PreopenPlan_{ds}_book1a.json"), market_context=side["market_context"],
                         decision_zones=len(side["zones"]), review=side["review"]))
        print(ds, side["market_context"], len(side["zones"]), "decision zones", side["review"])
    check = None
    if a.check_run:
        other = Path(a.check_run) / "map"
        diff = [r["packet"] for r in rows if not (other / r["packet"]).exists()
                or packet_body(other / r["packet"]) != packet_body(out / "map" / r["packet"])]
        check = dict(check_run=str(Path(a.check_run).resolve()), packets_compared=len(rows), packets_different=diff,
                     rule="JSON equal after removing built_local (the map's wall-clock build time)")
        print("packets compared", len(rows), "different", diff)
    (plans / "plan_build_manifest.json").write_text(json.dumps(dict(version=VERSION, sessions=[d.isoformat() for d in sess], rows=rows,
                                                                     map_check=check, map_only_out=str(out)), indent=1))
    return 0 if not (check and check["packets_different"]) else 1


if __name__ == "__main__":
    sys.exit(main())
