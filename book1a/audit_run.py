"""P0.13 on real days: register every input of every entry decision and assert available_at < decision time.

  python -m book1a.audit_run <run_dir> <book1a_plans_dir> <ledger_full.csv> <out_dir>

For each trade in the ledger (R1-R4 full ledger format) it registers, for the decision timestamp (the signal bar
close for immediate entries; the retest confirmation bar close for RH1 entries):
  - every zone of that day's Book 1A plan sidecar (available_at = the as-of 08:10 CT),
  - the 08:10 session and weekly VWAP (08:10 CT),
  - every GEX level in the plan (D-1 23:00 ET),
  - the swing(s) behind every REJ/FLIP zone (formed_ct + 15 bars),
  - every L2 one-second feature named in the sidecar (completed second), when present,
  - the map packet as-of (08:10 CT),
  - v1.1: every component swing (and the flip acceptance bar) behind every REJ / merged REJ / FLIP zone at its own
    confirmation time (the close of the 15th bar after the swing), the PD and weekly DD_EDGE zones, and the weekly
    double-distribution profile (its last trade).
v1.1 also runs plan-build checks once per day (independent of the trades), written to plan_build_checks.csv:
  - a merged or FLIP zone's confirmed_ct equals the LATEST of its components' confirmation times (Kyron, Nov 4);
  - every component confirmation is at or before the 08:10 as-of (a bar closing at 08:10:00 holds only earlier ticks);
  - the weekly profile window starts at the Sunday 17:00 CT open, ends at the as-of, and its last trade is before it.
Writes <out_dir>/lookahead_audit.csv (one row per input) and lookahead_summary.json; the summary must show
0 violations and 0 missing.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from book1a.lookahead import CT, LookaheadAudit, gex_available_at, l2_second_available_at, map_available_at, swing_available_at

VERSION = "audit-run-v1.1"


def decision_ts(row: dict) -> datetime:
    d = date.fromisoformat(row["date"])
    et = row["entry_time"]
    hh, mm, ss = int(et[0:2]), int(et[3:5]), float(et[6:])
    entry = datetime.combine(d, time(hh, mm), tzinfo=CT) + timedelta(seconds=ss)
    # the decision is the bar close 250 ms before the fill
    return entry - timedelta(milliseconds=int(row.get("entry_latency_ms") or 250))


def run(run_dir: Path, plans_dir: Path, ledger_csv: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    audit = LookaheadAudit()
    for row in csv.DictReader(open(ledger_csv, newline="")):
        d = date.fromisoformat(row["date"])
        dec = decision_ts(row)
        did = f"{row['strategy']}:{row['trade_id']}"
        audit.register(did, dec, "map_packet_0810", "PLAN", map_available_at(d))
        side = plans_dir / f"PreopenPlan_{d.isoformat()}_book1a.json"
        if not side.exists():
            audit.register(did, dec, f"plan_sidecar_{d}", "PLAN", None); continue
        sc = json.load(open(side))
        for z in sc.get("zones", []):
            audit.register(did, dec, f"zone:{z['label']}", "ZONE", z.get("available_at"))
        for z in sc.get("rej_flip_zones", []):
            audit.register(did, dec, f"rej:{z['kind']}:{z['lo']}-{z['hi']}", "ZONE", z.get("available_at"))
            if z.get("formed_ct"):
                audit.register(did, dec, f"swing:{z['kind']}:{z['formed_ct']}", "SWING", swing_available_at(datetime.fromisoformat(z["formed_ct"])))
            audit.register(did, dec, f"rej_confirmed:{z['kind']}:{z['lo']}-{z['hi']}", "ZONE", z.get("confirmed_ct"))
            for c in z.get("components", []):
                audit.register(did, dec, f"component:{c['kind']}:{c['formed_ct']}", "SWING", c.get("confirmed_ct"))
        for key in ("dd_edge", "dd_edge_wk"):
            if sc.get(key):
                audit.register(did, dec, f"{key}:{sc[key]['lo']}-{sc[key]['hi']}", "ZONE", sc[key].get("available_at"))
        wdd = sc.get("weekly_dd")
        if wdd is not None:
            audit.register(did, dec, "weekly_dd", "PROFILE", wdd.get("available_at"))
            if wdd.get("last_trade_ct"):
                audit.register(did, dec, "weekly_dd_last_trade", "PROFILE", wdd["last_trade_ct"])
        for k, v in (sc.get("vwap") or {}).items():
            audit.register(did, dec, f"vwap:{k}", "INDICATOR", v.get("available_at_ct"))
        for line in sc.get("plan", []):
            if line.startswith("mq_") or line.startswith("gex_regime="):
                audit.register(did, dec, line.split("=")[0], "GEX", gex_available_at(d))
        for sec in sc.get("l2_seconds", []):
            audit.register(did, dec, f"l2:{sec}", "L2", l2_second_available_at(datetime.fromisoformat(sec)))
    summary = audit.write_log(str(out_dir / "lookahead_audit.csv"))
    pb = plan_build_checks(plans_dir, out_dir / "plan_build_checks.csv")
    summary["plan_build_checks"] = pb
    summary["passed"] = audit.passed() and pb["failed"] == 0
    (out_dir / "lookahead_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


def plan_build_checks(plans_dir: Path, out_csv: Path) -> dict:
    """Per plan sidecar: merged / FLIP zone availability = latest component confirmation, all <= as-of; weekly window."""
    from book1a import vwap as V
    rows, failed = [], 0
    def chk(day, item, ok, detail):
        nonlocal failed
        failed += 0 if ok else 1
        rows.append([day, item, "OK" if ok else "FAIL", detail])
    for side in sorted(Path(plans_dir).glob("PreopenPlan_*_book1a.json")):
        sc = json.load(open(side))
        day = sc["date"]; as_of = datetime.fromisoformat(sc["as_of"])
        for z in sc.get("rej_flip_zones", []):
            name = f"{z['kind']}:{z['lo']}-{z['hi']}"
            comps = z.get("components") or []
            chk(day, name + " has components", bool(comps), f"{len(comps)} components")
            if not comps:
                continue
            latest = max((datetime.fromisoformat(c["confirmed_ct"]) for c in comps))
            conf = datetime.fromisoformat(z["confirmed_ct"]) if z.get("confirmed_ct") else None
            chk(day, name + " confirmed_ct = latest component", conf == latest,
                f"zone {z.get('confirmed_ct')} latest {latest.isoformat()} ({len(comps)} components, merged_from={z.get('merged_from', 1)})")
            for c in comps:
                t = datetime.fromisoformat(c["confirmed_ct"])
                chk(day, f"{name} component {c['kind']} {c['formed_ct']} confirmed <= as-of", t <= as_of, f"{c['confirmed_ct']} vs {sc['as_of']}")
        wdd = sc.get("weekly_dd")
        if wdd is not None and wdd.get("window_start"):
            ws = V.week_start(date.fromisoformat(day))
            chk(day, "weekly profile starts Sunday 17:00 CT", datetime.fromisoformat(wdd["window_start"]) == ws, f"{wdd['window_start']} vs {ws.isoformat()}")
            chk(day, "weekly profile ends at the as-of", datetime.fromisoformat(wdd["window_end"]) == as_of, wdd["window_end"])
            lt = wdd.get("last_trade_ct")
            chk(day, "weekly profile last trade before the as-of", lt is not None and datetime.fromisoformat(lt) < as_of, str(lt))
        for key in ("dd_edge", "dd_edge_wk"):
            if sc.get(key):
                chk(day, f"{key} available at the as-of", datetime.fromisoformat(sc[key]["available_at"]) == as_of, sc[key]["available_at"])
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["day", "check", "status", "detail"]); w.writerows(rows)
    return {"checks": len(rows), "failed": failed}


def main(argv):
    if len(argv) != 4:
        print(__doc__); return 2
    s = run(Path(argv[0]), Path(argv[1]), Path(argv[2]), Path(argv[3]))
    print(s)
    return 0 if s["passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
