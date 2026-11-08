r"""Phase 3 Step A1 (Nov 8, 2026): the 41 sessions, their close times, front contract, exposure flags and an input check.

  python -m book1a.phase3_sessions --block1 K:\Book1A_inputs --maps book1a\Phase3\runs\maps_phase3 \
      --plans book1a\Phase3\plans_phase3 --c2-plans book1a\Phase3\plans_phase3_c2 --gex-v3 book1a\Phase3\runs\gex_v3_stepA \
      --out book1a\Phase3

The Phase 2 check (book1a.phase2_sessions, phase2-sessions-v1.0) on the Phase 3 sessions, its functions reused
unchanged (front, tape_stats, bar_counts, the data-integrity table). Reads inputs only (no ledger, strategy log or
fill). Exposure: replay plan section 8 as updated Nov 8, 2026 (Part 3: Jan 12, Jan 14, Jan 16, 2026, session level
whatever the instrument); the other unresolved videos have no confirmed dates and stay EXCLUDED until confirmed, which
flags no Phase 3 session. A session with any missing input is DATA_MISSING with its cause; no session is dropped.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

from book1a import phase2_sessions as P2, sessions as S

VERSION = "phase3-sessions-v1.0"
PHASE = "phase3"
N_EXPECTED = 41
EXPOSURE_SOURCE = {
    dt.date(2026, 1, 12): "Part 3, How I Frame Every Trade (gold example)",
    dt.date(2026, 1, 14): "Part 3, How I Frame Every Trade (gold example)",
    dt.date(2026, 1, 16): "Part 3, How I Frame Every Trade (NQ example, NQH6; transcript-derived date, pending tape confirmation)",
}
EXPOSED = set(EXPOSURE_SOURCE)


def row_for(d, closes, cal, di, gex, v3, mbo, nqb, esb, prow, maps, plans, c2_plans, block1):
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
    sym, label = P2.front(d)
    r.update(front_by_roll=sym, instrument_label=label, roll_day="Y" if d in S.ROLL_DATES else "N")
    if not x:
        gaps.append("no data-integrity row")
    elif x.get("main_contract") != sym or x.get("nt_contract") != sym or x.get("contract_ok") != "True":
        gaps.append(f"contract {x.get('main_contract')} / NT {x.get('nt_contract')} is not the front {sym}")
    tp = Path(maps) / "tapes_phase3" / f"tape_{ymd}.csv.gz"         # run_r1_r2.phase_tapes_dir (Feb 4 cut tape)
    if not (Path(maps) / "tapes_phase3").exists():
        tp = Path(block1) / "tapes" / f"tape_{ymd}.csv.gz"
    r["tape_file"] = str(tp)
    if tp.exists():
        r.update(P2.tape_stats(tp, d, closes[d]))
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
    pk = Path(maps) / "map" / p["packet"] if p else None
    if not p or not pk.exists() or not (Path(plans) / f"PreopenPlan_{ds}_book1a.txt").exists():
        gaps.append("map packet or plan missing")
    else:
        pkt = json.loads(pk.read_text(encoding="utf-8"))
        r.update(packet_gaps="; ".join(str(x) for x in pkt.get("data", {}).get("gaps", [])) or "none",
                 packet_notes="; ".join(str(x) for x in pkt.get("data", {}).get("notes", [])) or "none",
                 packet_instrument=pk.name[len("PreopenPacket_"):-len(f"_{ds}.json")],
                 plan_review=p["review"], market_context=p["market_context"], decision_zones=p["decision_zones"])
    if c2_plans is not None:
        ok = (Path(c2_plans) / f"PreopenPlan_{ds}_book1a.txt").exists() and (Path(c2_plans) / f"PreopenPlan_{ds}_book1a.json").exists()
        r["c2_plan"] = "Y" if ok else "N"
        if not ok: gaps.append("C2 plan missing")
    r["status"] = "DATA_MISSING" if gaps else "OK"
    r["cause"] = "; ".join(gaps)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--maps", required=True); ap.add_argument("--plans", required=True)
    ap.add_argument("--c2-plans", default=None); ap.add_argument("--gex-v3", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    block1, maps, plans, gv3, out = (Path(x) for x in (a.block1, a.maps, a.plans, a.gex_v3, a.out))
    sess = S.phase_sessions(PHASE)
    if len(sess) != N_EXPECTED:
        raise SystemExit(f"expected {N_EXPECTED} Phase 3 sessions, got {len(sess)}")
    if not EXPOSED <= set(sess):
        raise SystemExit("an exposed date is not a Phase 3 session")
    closes = {d: S.session_close(d) for d in sess}
    cal = list(csv.DictReader(open(block1 / "econ_calendar_2025-10_2026-04.csv", newline="", encoding="utf-8-sig")))
    di = {r["date"]: r for r in csv.DictReader(open(P2.DI_CSV, newline="", encoding="utf-8-sig"))}
    gex = {r["session"]: r for r in csv.DictReader(open(block1 / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    v3 = {r["session"]: r for r in csv.DictReader(open(gv3 / "gex_v3_sessions.csv", newline="", encoding="utf-8"))}
    mbo = {p.name[10:18]: p for p in (block1 / "raw" / "block1" / "nq_mbo_20251021_20260421").glob("*/glbx-mdp3-*.mbo.dbn.zst")}
    nqb = P2.bar_counts(maps / "nq_1m.csv", sess, closes); esb = P2.bar_counts(maps / "es_1m.csv", sess, closes)
    pman = json.loads((plans / "plan_build_manifest.json").read_text())
    prow = {r["session"]: r for r in pman["rows"]}
    rows = [row_for(d, closes, cal, di, gex, v3, mbo, nqb, esb, prow, maps, plans, a.c2_plans, block1) for d in sess]
    out.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(out / "phase3_sessions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    n_exp = sum(r["exposure"] == "EXPOSED" for r in rows)
    L = [f"# Book 1A Phase 3 sessions and inputs ({VERSION}, Step A1, Nov 8, 2026)", "",
         "Inputs only: no ledger, strategy log or fill was read. Book 1 calendar (`book1a/sessions.py`, "
         "`econ_calendar_2025-10_2026-04.csv`); close time `sessions.session_close` (15:00 CT full day, 12:15 CT half "
         "day); front contract from the NinjaTrader roll (Dec 15, 2025: NQZ5 -> NQH6) and checked against the "
         "data-integrity table of the read-only Book 1 reference copy; exposure from replay plan section 8 (updated Nov 8, "
         "2026: Part 3 = Jan 12, Jan 14, Jan 16, 2026, session level whatever the instrument; every other unresolved "
         "video has no confirmed date and stays EXCLUDED until confirmed, so it flags no session here); tape (the phase3 "
         "tape folder the map build used, Feb 4 cut at 17:00 CT), bar, GEX, GEX V3 and plan checks from the files "
         "themselves. A session with a missing input would be DATA_MISSING with its cause; none is dropped.", "",
         f"Sessions: {len(rows)}; EXPOSED {n_exp}; UNEXPOSED {len(rows) - n_exp}; DATA_MISSING "
         f"{sum(r['status'] == 'DATA_MISSING' for r in rows)}.", "",
         "| session | day | type | close CT | exposure | front (NT roll) | roll day | packet instrument | MBO file MB | "
         "Databento condition | tape last trade | max gap RTH s | max gap overnight s | NQ / ES RTH bars | GEX regime | "
         "GEX V3 repro | plan review | C2 plan | status | cause |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['session']} | {r['weekday']} | {r['session_type']} | {r['close_ct']} | {r['exposure']} | {r['front_by_roll']} | "
                 f"{r['roll_day']} | {r.get('packet_instrument', '')} | {r['mbo_mb']} | {r['di_condition']} | {r.get('tape_last', '')} | "
                 f"{r.get('tape_max_gap_rth_s', '')} | {r.get('tape_max_gap_overnight_s', '')} | "
                 f"{r['nq_rth_bars']} / {r['es_rth_bars']} of {r['rth_bars_expected']} | {r['gex_regime']} | {r['gex_v3_repro']} | "
                 f"{r.get('plan_review', '')} | {r.get('c2_plan', '')} | {r['status']} | {r['cause'] or '-'} |")
    L += ["", "Exposed sessions (replay plan section 8):", ""]
    L += [f"- {r['session']}: {r['exposure_source']}" for r in rows if r["exposure"] == "EXPOSED"]
    L += ["", "Calendar events on the sessions (logged; the plan applies its own rules):", ""]
    L += [f"- {r['session']}: {r['calendar_events']}" for r in rows if r["calendar_events"]]
    L += ["", "Map packet data notes (gaps / notes written by map v2.3):", ""]
    L += [f"- {r['session']}: gaps {r.get('packet_gaps', '')}; notes {r.get('packet_notes', '')}" for r in rows]
    (out / "phase3_sessions.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for r in rows:
        print(r["session"], r["close_ct"], r["front_by_roll"], r["exposure"], r["status"], r["cause"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
