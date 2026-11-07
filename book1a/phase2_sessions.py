r"""Phase 2 Step A1 (Nov 6, 2026): the 21 sessions, their close times and exposure flags, and an input check.

  python -m book1a.phase2_sessions --block1 K:\Book1A_inputs --maps book1a\Phase2\runs\maps_phase2 \
      --plans book1a\Phase2\plans_phase2 --gex-v3 book1a\Phase2\runs\gex_v3_stepA --out book1a\Phase2\phase2_sessions

Reads inputs only (no ledger, no strategy log, no fill): the Book 1 calendar (book1a.sessions and the econ calendar),
the raw MBO file list, the data-integrity table of the read-only Book 1 reference copy
(code\book1_ref\backtest\phase0_parity\phase0_data_integrity_2025-10-21_2026-10-02.csv: contracts, session type,
Databento condition), each day's tape (first / last trade, largest gap, trades after the close), the 1-minute bars the
map-only build made, gex_levels_block1.csv and the V3 reproduction, and each map packet and Book 1A plan.
A session with any missing input is DATA_MISSING with its cause; no session is dropped.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import sys
from pathlib import Path

from book1a import sessions as S

VERSION = "phase2-sessions-v1.0"
EXPOSED = {dt.date(2025, 11, d) for d in (17, 18, 19, 20, 21, 24, 25, 26)}     # replay plan section 8 (Parts 1 and 2)
EXPOSURE_SOURCE = {**{dt.date(2025, 11, d): "Part 1 (week of Nov 17-21)" for d in (17, 18, 19, 20, 21)},
                   **{dt.date(2025, 11, d): "Part 2 (week of Nov 24-26)" for d in (24, 25, 26)}}
ROLL_FRONT = [(dt.date(2025, 9, 15), "NQZ5", "NQ DEC25"), (dt.date(2025, 12, 15), "NQH6", "NQ MAR26")]   # NinjaTrader roll dates
DI_CSV = Path(__file__).resolve().parents[1] / "book1_ref" / "backtest" / "phase0_parity" / "phase0_data_integrity_2025-10-21_2026-10-02.csv"


def front(d: dt.date):
    f = None
    for start, sym, label in ROLL_FRONT:
        if d >= start:
            f = (sym, label)
    return f


def tape_stats(path: Path, d: dt.date, close: dt.datetime) -> dict:
    """First / last trade, trade count, largest gap 08:30-close and 17:00 (prior day)-08:30, trades after the close."""
    first = last = None; n = 0; after = 0
    rth0 = dt.datetime.combine(d, dt.time(8, 30)); gap_rth = gap_on = 0.0; prev = None
    with gzip.open(path, "rt") as fh:
        for line in fh:
            t = dt.datetime.fromisoformat(line[:26].rstrip(","))
            n += 1
            first = first or t; last = t
            if t > close:
                after += 1
            if prev is not None:
                g = (t - prev).total_seconds()
                if rth0 <= prev and t <= close:
                    gap_rth = max(gap_rth, g)
                elif t <= rth0:
                    gap_on = max(gap_on, g)
            prev = t
    return dict(tape_first=first.isoformat(sep=" ", timespec="seconds"), tape_last=last.isoformat(sep=" ", timespec="seconds"),
                tape_trades=n, tape_max_gap_rth_s=round(gap_rth, 1), tape_max_gap_overnight_s=round(gap_on, 1), tape_trades_after_close=after)


def bar_counts(path: Path, sessions, closes) -> dict:
    """1-minute bars ending in (08:30, close] per session (time column = bar time as the harness file writes it)."""
    out = {d: 0 for d in sessions}
    with open(path) as fh:
        next(fh)
        for line in fh:
            t = dt.datetime.fromisoformat(line[:19])
            d = t.date()
            if d in out and dt.datetime.combine(d, dt.time(8, 30)) < t <= closes[d]:
                out[d] += 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--maps", required=True); ap.add_argument("--plans", required=True)
    ap.add_argument("--gex-v3", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    block1, maps, plans, gv3, out = (Path(x) for x in (a.block1, a.maps, a.plans, a.gex_v3, a.out))
    sess = S.phase_sessions("phase2")
    if len(sess) != 21:
        raise SystemExit(f"expected 21 Phase 2 sessions, got {len(sess)}")
    closes = {d: S.session_close(d) for d in sess}
    cal = list(csv.DictReader(open(block1 / "econ_calendar_2025-10_2026-04.csv", newline="", encoding="utf-8-sig")))
    di = {r["date"]: r for r in csv.DictReader(open(DI_CSV, newline="", encoding="utf-8-sig"))}
    gex = {r["session"]: r for r in csv.DictReader(open(block1 / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    v3 = {r["session"]: r for r in csv.DictReader(open(gv3 / "gex_v3_sessions.csv", newline="", encoding="utf-8"))}
    mbo = {p.name[10:18]: p for p in (block1 / "raw" / "block1" / "nq_mbo_20251021_20260421").glob("*/glbx-mdp3-*.mbo.dbn.zst")}
    nqb = bar_counts(maps / "nq_1m.csv", sess, closes); esb = bar_counts(maps / "es_1m.csv", sess, closes)
    pman = json.loads((plans / "plan_build_manifest.json").read_text())
    prow = {r["session"]: r for r in pman["rows"]}
    rows = []
    for d in sess:
        ds, ymd = d.isoformat(), d.strftime("%Y%m%d")
        r = dict(session=ds, weekday=d.strftime("%a"), session_type="HALF_DAY" if d in S.HALF_DAYS else "FULL",
                 close_ct=closes[d].strftime("%H:%M"), cash_end_ct="12:00" if d in S.HALF_DAYS else "15:00",
                 exposure="EXPOSED" if d in EXPOSED else "UNEXPOSED", exposure_source=EXPOSURE_SOURCE.get(d, ""),
                 calendar_events="; ".join(f"{c['event']} ({c['action']}{' ' + c['no_trade_ct'] if c['no_trade_ct'] else ''})"
                                           for c in cal if c["date"] == ds and c["status"] != "CANCELED"))
        gaps = []
        f = mbo.get(ymd)
        r["mbo_file"] = f.name if f else ""
        r["mbo_mb"] = round(f.stat().st_size / 1e6, 1) if f else ""
        if not f:
            gaps.append("raw MBO file missing")
        x = di.get(ds, {})
        r.update(di_condition=x.get("databento_condition", ""), di_session=x.get("session", ""), di_contract=x.get("main_contract", ""),
                 di_nt_contract=x.get("nt_contract", ""), di_rth_last_trade=x.get("rth_last_trade_ct", ""))
        sym, label = front(d)
        r.update(front_by_roll=sym, instrument_label=label, roll_day="Y" if d in S.ROLL_DATES else "N")
        if not x:
            gaps.append("no data-integrity row")
        elif x.get("main_contract") != sym or x.get("nt_contract") != sym or x.get("contract_ok") != "True":
            gaps.append(f"contract {x.get('main_contract')} / NT {x.get('nt_contract')} is not the front {sym}")
        tp = block1 / "tapes" / f"tape_{ymd}.csv.gz"
        if tp.exists():
            r.update(tape_stats(tp, d, closes[d]))
            if dt.datetime.fromisoformat(r["tape_last"]) < closes[d] - dt.timedelta(seconds=60):   # the 60 s gap rule (design gate 6)
                gaps.append(f"tape ends {r['tape_last']}, more than 60 s before the close")
        else:
            gaps.append("tape missing")
        need = (closes[d] - dt.datetime.combine(d, dt.time(8, 30))).seconds // 60
        r.update(nq_rth_bars=nqb[d], es_rth_bars=esb[d], rth_bars_expected=need)
        if nqb[d] != need: gaps.append(f"NQ 1-minute bars {nqb[d]} of {need}")
        if esb[d] != need: gaps.append(f"ES 1-minute bars {esb[d]} of {need}")
        g = gex.get(ds)
        r.update(gex_row="Y" if g else "N", gex_ok=(g or {}).get("ok", ""), gex_regime=(g or {}).get("regime", ""),
                 gex_report_date=(g or {}).get("report_date", ""), gex_v3_repro=v3.get(ds, {}).get("repro_all_match", ""))
        if not g or g.get("ok") != "True": gaps.append("GEX levels row missing or not ok")
        if v3.get(ds, {}).get("repro_all_match") != "Y": gaps.append("GEX V3 inputs do not reproduce the frozen row")
        p = prow.get(ds)
        pk = maps / "map" / p["packet"] if p else None
        if not p or not pk.exists() or not (plans / f"PreopenPlan_{ds}_book1a.txt").exists():
            gaps.append("map packet or plan missing")
        else:
            pkt = json.loads(pk.read_text(encoding="utf-8"))
            r.update(packet_gaps="; ".join(str(x) for x in pkt.get("data", {}).get("gaps", [])) or "none",
                     packet_notes="; ".join(str(x) for x in pkt.get("data", {}).get("notes", [])) or "none",
                     plan_review=p["review"], market_context=p["market_context"], decision_zones=p["decision_zones"])
        r["status"] = "DATA_MISSING" if gaps else "OK"
        r["cause"] = "; ".join(gaps)
        rows.append(r)
    out.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(out / "phase2_sessions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    n_exp = sum(r["exposure"] == "EXPOSED" for r in rows)
    L = [f"# Book 1A Phase 2 sessions and inputs ({VERSION}, Step A1, Nov 6, 2026)", "",
         "Inputs only: no ledger, strategy log or fill was read. Book 1 calendar (`book1a/sessions.py`, "
         "`econ_calendar_2025-10_2026-04.csv`); exposure from replay plan section 8; contracts and session type from the "
         "data-integrity table of the read-only Book 1 reference copy; tape, bar, GEX and plan checks from the files "
         "themselves. A session with a missing input would be DATA_MISSING with its cause; none is dropped.", "",
         f"Sessions: {len(rows)}; EXPOSED {n_exp}; UNEXPOSED {len(rows) - n_exp}; DATA_MISSING "
         f"{sum(r['status'] == 'DATA_MISSING' for r in rows)}.", "",
         "| session | day | type | close CT | exposure | front (NT roll) | MBO file MB | Databento condition | tape last trade | "
         "max gap RTH s | max gap overnight s | NQ / ES RTH bars | GEX regime | GEX V3 repro | plan review | status | cause |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['session']} | {r['weekday']} | {r['session_type']} | {r['close_ct']} | {r['exposure']} | {r['front_by_roll']} | "
                 f"{r['mbo_mb']} | {r['di_condition']} | {r.get('tape_last', '')} | {r.get('tape_max_gap_rth_s', '')} | "
                 f"{r.get('tape_max_gap_overnight_s', '')} | {r['nq_rth_bars']} / {r['es_rth_bars']} of {r['rth_bars_expected']} | "
                 f"{r['gex_regime']} | {r['gex_v3_repro']} | {r.get('plan_review', '')} | {r['status']} | {r['cause'] or '-'} |")
    L += ["", "Calendar events on the sessions (logged; the plan applies its own rules):", ""]
    L += [f"- {r['session']}: {r['calendar_events']}" for r in rows if r["calendar_events"]]
    L += ["", "Map packet data notes (gaps / notes written by map v2.3):", ""]
    L += [f"- {r['session']}: gaps {r.get('packet_gaps', '')}; notes {r.get('packet_notes', '')}" for r in rows]
    (out / "phase2_sessions.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for r in rows:
        print(r["session"], r["close_ct"], r["exposure"], r["status"], r["cause"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
