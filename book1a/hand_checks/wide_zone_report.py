r"""Wide decision zones: descriptive eligibility report (Kyron, Nov 4, 2026). No outcomes, no P&L, no alternate trades.

  python -m book1a.hand_checks.wide_zone_report --out <md> --day <date>=<run dir>|<plans dir>[|<R4 run dir>] [...]

Kyron, Nov 4: keep the frozen rules for wide decision zones (no 60-point cap, no stop change). This report only
describes the zones whose planned stop (width in ticks + 2) is above 196 ticks, i.e. 1 NQ does not fit the $1,000
per-trade budget (C3: estimated risk = (stop ticks + 2) x $5 + $5.74). Per zone:
  - merged width, levels and families, planned stop and 1 NQ estimated risk;
  - each side: open / NONE by a side rule / NONE only because of the risk check (the plan's "C: ... does not fit" note);
  - pre-existing structural invalidation levels: STRUCTURE-family levels (PDH / PDL / ONH / ONL / WKH / WKL / PD2-3 H-L,
    REJ swing prices, DD edges) inside the zone, all known before 08:10 CT; Y/N and which, with the distance in points
    from each side's entry edge (long enters at the zone's high edge, short at its low edge, as in the plan ladder);
  - whether 1 MNQ would fit: (stop ticks + 2) x $0.50 + commission <= $1,000. The MNQ commission is not in the frozen
    rules; the NQ round trip ($5.74) is used as an upper bound. Book 1A never trades MNQ (C3); this is descriptive.
Zone counts and trade counts are reported separately. Trade counts come from the R4 run's own strategy log and
attempts (counts only: candidates on the zone, order attempts, risk rejections, entries); nothing is re-simulated.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

VERSION = "wide-zone-report-v1.0"
WIDE_TICKS = 196
MNQ_TICK_USD = 0.50
COMM_UPPER_USD = 5.74
STRUCT_POINT = ("PDH", "PDL", "ONH", "ONL", "WKH", "WKL", "PD2H", "PD2L", "PD3H", "PD3L")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--day", action="append", required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from book1a import families as F, risk as RK
    zones_total, wide, trades = 0, [], []
    for spec in a.day:
        ds, rest = spec.split("=", 1)
        parts = rest.split("|")         # <run dir>|<plans dir>[|<R4 run dir>] ('|' because Windows paths hold ':')
        run, plans, r4 = (parts + [None, None])[:3]
        run, plans = Path(run), Path(plans)
        pk = json.load(open(sorted((run / "map").glob(f"PreopenPacket_*{ds}.json"))[0]))
        lv = {l["name"]: float(l["price"]) for l in pk.get("levels", []) if l.get("price") is not None}
        sc = json.load(open(plans / f"PreopenPlan_{ds}_book1a.json"))
        zones_total += len(sc["zones"])
        rej = sc.get("rej_flip_zones", [])
        for z in sc["zones"]:
            if z["stop_ticks"] <= WIDE_TICKS:
                continue
            est = RK.estimate_risk(z["stop_ticks"], 1)
            mnq = (z["stop_ticks"] + 2) * MNQ_TICK_USD + COMM_UPPER_USD
            sides = {}
            for side in ("long", "short"):
                risk_note = any(n.startswith(f"C: {z['label']} {side} NONE") for n in sc.get("notes", []))
                sides[side] = "NONE: risk only" if risk_note else ("NONE: side rule" if z[side] == "NONE" else z[side])
            struct = []
            for n in dict.fromkeys(z["levels"]):
                if n in STRUCT_POINT and n in lv and z["lo"] <= lv[n] <= z["hi"]:
                    struct.append((n, lv[n]))
            for r in rej:
                if f"{r['kind']}_{r['session']}" in z["label"] and r.get("swing_price") is not None and z["lo"] <= r["swing_price"] <= z["hi"]:
                    struct.append((f"{r['kind']}_{r['session']} swing", float(r["swing_price"])))
            for key in ("dd_edge", "dd_edge_wk"):
                dd = sc.get(key)
                if dd and dd["label"] in z["label"]:
                    for edge in (dd["lo"], dd["hi"]):
                        if z["lo"] <= edge <= z["hi"]:
                            struct.append((f"{dd['label']} edge", float(edge)))
            wide.append(dict(day=ds, z=z, est=est, mnq=mnq, sides=sides, struct=struct, r4=r4))
    # trade counts from the R4 runs (counts only)
    os.environ.setdefault("BOOK1_ROOT", r"K:\Databento_BackTesting")
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR
    logs = {}
    for w in wide:
        if not w["r4"]:
            w["counts"] = None; continue
        r4 = Path(w["r4"])
        if r4 not in logs:
            att = list(csv.DictReader(open(r4 / "R4_attempts.csv", newline="")))
            logs[r4] = (AR.Log(r4), att)
        log, att = logs[r4]
        lab60 = w["z"]["label"][:60]
        evs = set()
        n_c = 0
        for r in log.rows:
            if r.get("RecordType") != "CANDIDATE" or not r.get("EvidenceTimeCT", "").startswith(w["day"]):
                continue
            lid = r.get("LocationId", "")
            if r.get("LocationType", "").startswith("FROZEN_PREOPEN") and re.sub(r"_\d+$", "", lid[2:]) == lab60:
                n_c += 1; evs.add(r["EventId"])
        at = [x for x in att if x["event"] in evs]
        w["counts"] = dict(candidates=n_c, attempts=len(at), risk_reject=sum(1 for x in at if x["risk_decision"].startswith("RISK_REJECT")),
                           entered=sum(1 for x in at if x["reasons"] == "" and x["risk_decision"] == "ACCEPT"))
    L = [f"# Wide decision zones: eligibility report ({VERSION})", "",
         "Descriptive only (Kyron, Nov 4). Frozen rules kept: no 60-point cap, no stop change. No outcomes, no P&L, no "
         "alternate trades. Zone = a plan DECISION zone whose planned stop (width in ticks + 2) is above "
         f"{WIDE_TICKS} ticks, so 1 NQ does not fit the $1,000 budget.", "",
         "## Zone counts", "",
         f"- Days: {len(a.day)}. Decision zones: {zones_total}. Wide zones: {len(wide)}.",
         f"- Wide zones with a side NONE only because of the risk check: {sum(1 for w in wide if any(v == 'NONE: risk only' for v in w['sides'].values()))}.",
         f"- Wide zones with a pre-existing structural invalidation level inside: {sum(1 for w in wide if w['struct'])}.",
         f"- Wide zones where 1 MNQ would fit: {sum(1 for w in wide if w['mnq'] <= 1000)}.", "",
         "| # | day | zone | lo - hi | width pts | families | levels | planned stop ticks | 1 NQ risk | long | short | rejected only for risk | structural level inside (which; pts from long / short entry edge) | 1 MNQ fits (estimate) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, w in enumerate(wide, 1):
        z = w["z"]
        only_risk = "Y" if any(v == "NONE: risk only" for v in w["sides"].values()) else "N"
        st = "; ".join(f"{n} {p} ({z['hi'] - p:.2f} / {p - z['lo']:.2f})" for n, p in w["struct"])
        L.append(f"| {k} | {w['day']} | {z['label']} | {z['lo']} - {z['hi']} | {z['hi'] - z['lo']:.2f} | {len(z['families'])}: {', '.join(z['families'])} | "
                 f"{len(z['levels'])}: {', '.join(z['levels'])} | {z['stop_ticks']} | ${w['est']:,.2f} | {w['sides']['long']} | {w['sides']['short']} | {only_risk} | "
                 f"{('Y: ' + st) if st else 'N'} | {'Y' if w['mnq'] <= 1000 else 'N'} (${w['mnq']:,.2f}) |")
    L += ["", "## Trade counts (separate from zone counts)", "",
          "From the R4 Phase 1 run's strategy log and attempts (counts only). A candidate on a wide zone has S1.4's own stop, "
          "not the zone stop, so it can pass the risk check. Days without an R4 run (Phase 2 days) show 'not run'.", "",
          "| # | day | zone | candidates on the zone | order attempts | risk rejected | entered |", "|---|---|---|---|---|---|---|"]
    tot = dict(candidates=0, attempts=0, risk_reject=0, entered=0)
    for k, w in enumerate(wide, 1):
        c = w["counts"]
        if c is None:
            L.append(f"| {k} | {w['day']} | {w['z']['label'][:40]} | not run | | | |"); continue
        for kk in tot: tot[kk] += c[kk]
        L.append(f"| {k} | {w['day']} | {w['z']['label'][:40]} | {c['candidates']} | {c['attempts']} | {c['risk_reject']} | {c['entered']} |")
    L.append(f"| | | total (R4 days) | {tot['candidates']} | {tot['attempts']} | {tot['risk_reject']} | {tot['entered']} |")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(wide)} wide zones of {zones_total}; trade counts {tot}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
