r"""P0.7 / P0.8 / P0.9 on the PC: Book 1A plans for the 3 Phase 1 hand-check days, with the tables to check by hand.

  python -m book1a.hand_checks.plan_hand_check <book1_run_dir> <block1_root> <out_dir> [--days 2025-10-22 2025-10-28 2025-11-04]

<book1_run_dir> is a Book 1 daily-loop run folder for Phase 1 produced by run_r1_r2.py (map/PreopenPacket_*.json,
tape_map.csv.gz, tape_strategy.csv.gz). For each day it builds 1-minute bars and profiles from the map tape, the
08:10 VWAP, reads the GEX row and the econ calendar, runs book1a.plan_v24.build and writes:
  <out_dir>/PreopenPlan_<day>_book1a.txt     the S1.4-readable Book 1A plan
  <out_dir>/PreopenPlan_<day>_book1a.json    the sidecar (zones with families/levels/sides/ladder/available_at, REJ/FLIP
                                             zones, MAP4 areas, delta bands, DD_EDGE, VWAP, acceptance states)
  <out_dir>/hand_check_<day>.md              the P0.7 / P0.8 / P0.9 tables with an empty "hand" column to fill in
The hand-built list is made by a person from the chart; the script never fills that column.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
DEFAULT_DAYS = ["2025-10-22", "2025-10-28", "2025-11-04"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("block1"); ap.add_argument("out")
    ap.add_argument("--days", nargs="*", default=DEFAULT_DAYS)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from book1a import bars as B, plan_v24 as P, sessions as S, vwap as V
    run, block1, out = Path(a.run), Path(a.block1), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    gex = {r["session"]: r for r in csv.DictReader(open(block1 / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    cal = list(csv.DictReader(open(block1 / "econ_calendar_2025-10_2026-04.csv", newline="", encoding="utf-8-sig")))
    tape = run / "tape_map.csv.gz"
    for ds in a.days:
        d = date.fromisoformat(ds)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        # the map names packets PreopenPacket_<instrument>_<day>.json (e.g. PreopenPacket_NQ_DEC25_2025-10-22.json)
        hits = sorted((run / "map").glob(f"PreopenPacket_*{ds}.json"))
        if len(hits) != 1:
            raise SystemExit(f"expected one map packet for {ds}, found {[h.name for h in hits]}")
        packet = json.load(open(hits[0]))
        start = V.week_start(d) - timedelta(days=7)
        rows = list(_rows(tape, start, as_of))
        bars = B.bars_from_rows(rows, start, as_of)
        pd_date = S.sessions(d - timedelta(days=7), d - timedelta(days=1))[-1]
        prof = B.profiles_from_rows(rows, {"WK": (V.week_start(d), as_of), "ON": (V.session_start(d), as_of),
                                           "PD": (datetime.combine(pd_date, time(8, 30), tzinfo=CT), datetime.combine(pd_date, time(15, 0), tzinfo=CT))})
        ts, px, sz = B.trades_from_tape(tape, V.week_start(d), as_of)
        vres = V.vwap_0810(ts, px, sz, d)
        text, side = P.build(packet, bars, prof, vres, gex.get(ds), cal, roll_dates=[x.isoformat() for x in S.ROLL_DATES], as_of=as_of)
        (out / f"PreopenPlan_{ds}_book1a.txt").write_text(text, encoding="utf-8")
        (out / f"PreopenPlan_{ds}_book1a.json").write_text(json.dumps(side, indent=1, default=str), encoding="utf-8")
        L = [f"# Hand check {ds} (map v2.4 Book 1A outputs, families, context and sides)", "",
             "## P0.7 zones (every zone frozen at 08:10 CT)", "",
             "| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for z in side["rej_flip_zones"]:
            L.append(f"| {z['kind']} | {z['lo']} | {z['hi']} | {z['session']} | {z['formed_ct']} | {z['arrival_evidence']} | {z['departure_pts']} | {z['tags']} | {z['class']} | {z['available_at']} | | |")
        for z in side["map4_areas"]:
            L.append(f"| MAP4 {z['label']} | {z['lo']} | {z['hi']} | | | peak row {z.get('peak_row_lo')} | | | | {z['available_at']} | | |")
        for z in side["delta_bands"]:
            L.append(f"| DELTA {z['label']} | {z['lo']} | {z['hi']} | | | {z.get('sign')} {z.get('profile')} | | role={z.get('role')} | | {z['available_at']} | | |")
        if side.get("dd_edge"):
            z = side["dd_edge"]; L.append(f"| DD_EDGE | {z['lo']} | {z['hi']} | | | runner {z.get('runner')} | | | | {z['available_at']} | | |")
        L += ["", "## P0.8 families and levels on each decision zone", "", "| zone | lo | hi | families= | levels= | class | hand families | match |", "|---|---|---|---|---|---|---|---|"]
        for z in side["zones"]:
            L.append(f"| {z['label']} | {z['lo']} | {z['hi']} | {len(z['families'])}\\|{','.join(z['families'])} | {len(z['levels'])}\\|{','.join(z['levels'])} | DECISION | | |")
        L += ["", "## P0.9 context and side fields", ""]
        keys = ("market_context", "draw", "draw_status", "balance", "balance_poc", "value_follows", "on_inventory", "htf_structure", "gex_regime",
                "vwap_0810", "wkvwap_0810", "wkval_state", "wkvah_state")
        kv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in side["plan"] if "=" in l and not l.startswith("#")}
        L += ["| field | value | hand | match |", "|---|---|---|---|"] + [f"| {k} | {kv.get(k, '')} | | |" for k in keys]
        L += ["", "| zone | long | short | first_touch | side_conflict | ladder |", "|---|---|---|---|---|---|"]
        for z in side["zones"]:
            conf = [l for l in side["plan"] if l.startswith("side_conflict=" + z["label"])]
            L.append(f"| {z['label']} | {z['long']} | {z['short']} | YES | {'; '.join(conf)} | {json.dumps(z['ladder'])} |")
        L += ["", f"review={side['review']}; fails={side['fails']}; notes={side['notes']}"]
        (out / f"hand_check_{ds}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print(ds, side["market_context"], len(side["zones"]), "decision zones", side["review"])
    return 0


def _rows(tape, start, end):
    import gzip
    with gzip.open(tape, "rt") as f:
        for line in f:
            if line.startswith("time_local"):
                continue
            p = line.rstrip("\n").split(",")
            t = datetime.fromisoformat(p[0][:26]).replace(tzinfo=CT)
            if t < start:
                continue
            if t >= end:
                break
            yield t, float(p[1]), int(p[4]), p[5].strip()


if __name__ == "__main__":
    sys.exit(main())
