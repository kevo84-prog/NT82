r"""draw_status NONE report (Kyron, Nov 4, 2026): every Book 1A plan day with draw_status, and why NONE.

  python -m book1a.hand_checks.draw_none_report --block1 K:\Databento_BackTesting --out <md> --day <date>=<run dir>|<plans dir> [...]

Context spec: draw_status = ACTIVE | REACHED | INVALIDATED | NONE; NONE = no draw candidate exists (never ACTIVE).
Each plan is rebuilt with the frozen code and must equal the frozen plan file byte for byte. No outcomes, no P&L.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

VERSION = "draw-none-report-v1.0"


def why_context(ev) -> str:
    p, val, vah = ev["price"], ev["htf_val"], ev["htf_vah"]
    parts = []
    loc = "above HTF value" if p > vah else ("below HTF value" if p < val else "inside HTF value")
    parts.append(f"price {p} {loc} ({val} - {vah})")
    if not ev["held_or_reclaimed_val"]:
        parts.append(f"HTF VAL not held / reclaimed (bars low {ev['bars_low']} {'>' if ev['bars_low'] > val else '<='} {val}"
                     f"{'' if p >= val else ', price below it'})")
    if not ev["failed_or_lost_vah"]:
        parts.append(f"HTF VAH not failed / lost (bars high {ev['bars_high']} {'<' if ev['bars_high'] < vah else '>='} {vah}"
                     f"{'' if p <= vah else ', price above it'})")
    if ev["wk_val_state"] == "ACCEPTED_BELOW":
        parts.append("weekly VAL ACCEPTED_BELOW blocks BULLISH")
    if ev["wk_vah_state"] == "ACCEPTED_ABOVE":
        parts.append("weekly VAH ACCEPTED_ABOVE blocks BEARISH")
    bc = ev["balance_composite"] or {}
    parts.append("balance composite overlaps" if bc.get("overlapping") else
                 f"no balance (PD-ON overlap {bc.get('overlap_pct_pd_on')}%)")
    return "; ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--day", action="append", required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from book1a.hand_checks.plan_hand_check import build_day, load_inputs
    gex, cal = load_inputs(Path(a.block1))
    rows = []
    for spec in a.day:
        ds, rest = spec.split("=", 1)
        run, plans = (Path(x) for x in rest.split("|"))
        ev = {}
        text, side, _ = build_day(run, ds, gex, cal, evidence=ev)
        if text != (plans / f"PreopenPlan_{ds}_book1a.txt").read_text(encoding="utf-8"):
            raise SystemExit(f"{ds}: rebuilt plan differs from the frozen plan in {plans}")
        kv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in text.splitlines() if "=" in l and not l.startswith("#")}
        assert kv["draw_status"] == ev["draw_status"]
        assert (kv["draw_status"] == "NONE") == (ev["draw_candidates"] == []), ds
        assert (kv["draw_status"] == "NONE") == ("draw" not in kv), ds
        if ev["draw_candidates"]:
            c = ev["draw_candidates"][0]
            why = f"{len(ev['draw_candidates'])} candidate(s); nearest {c['name']} {c['lo']} - {c['hi']} ({c['dist']} pts)"
        else:
            why = (f"no candidate: context {ev['market_context']} has no direction" if ev["market_context"] not in ("BULLISH", "BEARISH")
                   else "no candidate level in the context direction")
        rows.append((ds, date.fromisoformat(ds).strftime("%a"), ev["market_context"], kv["draw_status"], kv.get("draw", ""), why, why_context(ev)))
    n_none = sum(1 for r in rows if r[3] == "NONE")
    L = [f"# draw_status by day: NONE days and why ({VERSION})", "",
         "Context spec (Kyron, Nov 4, 2026): draw_status = ACTIVE | REACHED | INVALIDATED | NONE. NONE = no draw candidate "
         "exists; it is never treated as ACTIVE. Checked here on every day: the plan writes NONE exactly when the rule found no "
         "candidate, and then writes no `draw=` line. Downstream: S1.4 does not parse `draw` or `draw_status` (logged-only "
         "Book 1A fields); the plan's own ladder uses the draw only when one exists (unit tests TestDrawStatusNone).", "",
         f"Each plan was rebuilt with the frozen code and equals the frozen plan file byte for byte. {len(rows)} days; "
         f"{n_none} NONE, {len(rows) - n_none} not NONE. No outcomes, no P&L.", "",
         "The draw rule looks for a level only in a BULLISH (above price) or BEARISH (below price) context, so every BALANCED "
         "or NONE context day has draw_status NONE.", "",
         "| day | | market_context | draw_status | draw | why | context inputs |", "|---|---|---|---|---|---|---|"]
    L += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |" for r in rows]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(rows)} days, {n_none} NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
