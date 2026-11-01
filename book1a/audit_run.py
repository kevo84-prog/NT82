"""P0.13 on real days: register every input of every entry decision and assert available_at < decision time.

  python -m book1a.audit_run <run_dir> <book1a_plans_dir> <ledger_full.csv> <out_dir>

For each trade in the ledger (R1-R4 full ledger format) it registers, for the decision timestamp (the signal bar
close for immediate entries; the retest confirmation bar close for RH1 entries):
  - every zone of that day's Book 1A plan sidecar (available_at = the as-of 08:10 CT),
  - the 08:10 session and weekly VWAP (08:10 CT),
  - every GEX level in the plan (D-1 23:00 ET),
  - the swing(s) behind every REJ/FLIP zone (formed_ct + 15 bars),
  - every L2 one-second feature named in the sidecar (completed second), when present,
  - the map packet as-of (08:10 CT).
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

VERSION = "audit-run-v1.0"


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
        for k, v in (sc.get("vwap") or {}).items():
            audit.register(did, dec, f"vwap:{k}", "INDICATOR", v.get("available_at_ct"))
        for line in sc.get("plan", []):
            if line.startswith("mq_") or line.startswith("gex_regime="):
                audit.register(did, dec, line.split("=")[0], "GEX", gex_available_at(d))
        for sec in sc.get("l2_seconds", []):
            audit.register(did, dec, f"l2:{sec}", "L2", l2_second_available_at(datetime.fromisoformat(sec)))
    summary = audit.write_log(str(out_dir / "lookahead_audit.csv"))
    summary["passed"] = audit.passed()
    (out_dir / "lookahead_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


def main(argv):
    if len(argv) != 4:
        print(__doc__); return 2
    s = run(Path(argv[0]), Path(argv[1]), Path(argv[2]), Path(argv[3]))
    print(s)
    return 0 if s["passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
