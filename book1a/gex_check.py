"""P1.2: confirm the calculated GEX levels per session and their available_at.

  python -m book1a.gex_check <gex_levels_block1.csv> <out.md> [--sessions-expected 124]

Reads the Book 1 replica table as rules_plan.load_gex does (one row per session; ok, regime, call_resistance,
put_support, hvl, the 0DTE levels and the *_nt chart-contract columns). For every Block 1 session it reports:
present / ok, regime (POS / NEG), the levels used by the plan (the _nt column when present, else the base
column), which are blank (0DTE levels right after a roll are expected blank: Dec 17-18, 2025 and Mar 18-19, 2026),
and available_at = D-1 23:00 ET (the D-1 end-of-day report, published before 11 PM ET; design v3.5 GEX section),
which is before the 08:10 CT map for every session. Values are copied, never recomputed here; the recomputation
(gex_block1.py on the D-1 option files) runs on the PC and must give the same numbers.
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

from book1a import sessions as S
from book1a.lookahead import gex_available_at, map_available_at

VERSION = "gex-check-v1.0"
LEVELS = ["call_resistance", "put_support", "hvl", "call_resistance_0dte", "put_support_0dte", "hvl_0dte"]
EXPECTED_BLANK_0DTE = {date(2025, 12, 17), date(2025, 12, 18), date(2026, 3, 18), date(2026, 3, 19)}


def check(csv_path: Path, out_md: Path, sessions=None) -> dict:
    rows = {r["session"]: r for r in csv.DictReader(open(csv_path, newline="", encoding="utf-8-sig"))}
    sessions = sessions or S.block1_sessions()
    lines = ["# P1.2 calculated GEX levels: coverage and available_at", "", f"source: {csv_path}", "",
             "| session | ok | regime | CR | PS | HVL | CR 0DTE | PS 0DTE | HVL 0DTE | available_at (ET) | before 08:10 CT | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    n_ok = n_missing = n_regime_pos = n_regime_neg = 0
    problems = []
    for d in sessions:
        r = rows.get(d.isoformat())
        avail = gex_available_at(d)
        before = avail < map_available_at(d)
        if r is None:
            n_missing += 1; problems.append(f"{d}: no row")
            lines.append(f"| {d} | MISSING | | | | | | | | {avail.isoformat()} | {before} | no row |"); continue
        ok = str(r.get("ok")) == "True"
        n_ok += ok
        regime = r.get("regime", "")
        n_regime_pos += regime == "positive"; n_regime_neg += regime == "negative"
        vals = []
        note = []
        for k in LEVELS:
            v = r.get(k + "_nt") or r.get(k) or ""
            vals.append(v)
            if not v and ok:
                if k.endswith("_0dte") and d in EXPECTED_BLANK_0DTE:
                    note.append(f"{k} blank (expected after the roll)")
                else:
                    note.append(f"{k} blank"); problems.append(f"{d}: {k} blank")
        if not ok:
            problems.append(f"{d}: ok={r.get('ok')}")
        if not before:
            problems.append(f"{d}: available_at not before the map")
        lines.append(f"| {d} | {ok} | {regime} | " + " | ".join(vals) + f" | {avail.isoformat()} | {before} | {'; '.join(note)} |")
    summary = dict(sessions=len(sessions), rows_ok=n_ok, missing=n_missing, positive=n_regime_pos, negative=n_regime_neg, problems=len(problems))
    lines += ["", f"sessions {summary['sessions']}, ok {n_ok}, missing {n_missing}, positive {n_regime_pos}, negative {n_regime_neg}, problems {len(problems)}",
              "", f"**Verdict: {'PASS' if not problems else 'FAIL'}** (Book 1 reported 124 / 124 OK, 68 positive and 56 negative)", ""]
    if problems:
        lines += ["## Problems"] + [f"- {p}" for p in problems]
    out_md.write_text("\n".join(lines) + "\n")
    return summary


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    print(check(Path(argv[0]), Path(argv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
