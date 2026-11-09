r"""Phase 4 Step A1 (Nov 9, 2026): the 52 sessions, their close times, front contract, exposure flags and an input check.

  python -m book1a.phase4_sessions --block1 K:\Book1A_inputs --maps book1a\Phase4\runs\maps_phase4 \
      --plans book1a\Phase4\plans_phase4 --gex-v3 book1a\Phase4\runs\gex_v3_stepA --out book1a\Phase4

The Phase 3 check (book1a.phase3_sessions, phase3-sessions-v1.0) on the Phase 4 sessions, the Phase 2 functions reused
unchanged (tape_stats, bar_counts, the data-integrity table). Reads inputs only (no ledger, strategy log or fill).
Differences from Phase 3, all inputs only:
  - front contract: the NinjaTrader roll Mar 16, 2026 (NQH6 -> NQM6), from sessions.ROLL_DATES and
    run_r1_r2.CONTRACT_LABELS; Feb 5 - Mar 13 NQH6 ("NQ MAR26"), Mar 16 - Apr 21 NQM6 ("NQ JUN26");
  - the data-integrity table has two rows on the roll days (the main NQH6 file and the roll NQM6 file); the row the
    Book 1 backtest used (used_by_backtest True) is the session's row, and its file is the session's MBO file;
  - tape price basis (runner decision, Step A): the first RTH tape trade must be within 50 points of the open of the
    NQ 1-minute bar ending 08:31 CT (the bars are the NinjaTrader contract's, roll-fixed); the NQH6 / NQM6 spread is
    about 200 points, so a tape on the wrong contract fails;
  - GEX price basis: nt_contract must be the front by roll, and nt_shift_pts must be 0 exactly when the GEX front equals
    nt_contract (as in Phase 3, Dec 15-16);
  - exposure: replay plan section 8. No confirmed video date falls in Feb 5 - Apr 21, 2026. Part 5 ("About Apr 2, 2026,
    approximate, not confirmed as a trading date") and Part 6 ("About Apr 9, 2026", same) are unresolved; the plan treats
    unresolved dates "as excluded until checked". Runner decision (most conservative, before any run): every session of
    the trading week of each approximate date is EXPOSED (Mar 30 - Apr 2 and Apr 6 - Apr 10, 2026; Apr 3 is Good
    Friday). Videos with no date at all (Parts 4, Strategy In 30 Minutes, webinar, 60k Profit) flag no session.
A session with any missing input is DATA_MISSING with its cause; no session is dropped. Databento "degraded" is logged as
a data condition (the Book 1 backtest used those files), not DATA_MISSING.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import sys
from pathlib import Path

from book1a import phase2_sessions as P2, sessions as S

VERSION = "phase4-sessions-v1.0"
PHASE = "phase4"
N_EXPECTED = 52
ROLL_FRONT = [(dt.date(2025, 12, 15), "NQH6", "NQ MAR26"), (dt.date(2026, 3, 16), "NQM6", "NQ JUN26")]   # NinjaTrader roll
BASIS_MAX_PTS = 50.0
_P5 = "Part 5, 45 Days Using This (about Apr 2, 2026; unresolved, treated as excluded; week of the approximate date)"
_P6 = "Part 6, Order Flow and GEX Levels (about Apr 9, 2026; unresolved, treated as excluded; week of the approximate date)"
EXPOSURE_SOURCE = {**{dt.date(2026, 3, d): _P5 for d in (30, 31)}, **{dt.date(2026, 4, d): _P5 for d in (1, 2)},
                   **{dt.date(2026, 4, d): _P6 for d in (6, 7, 8, 9, 10)}}
EXPOSED = set(EXPOSURE_SOURCE)


def front(d: dt.date):
    f = None
    for start, sym, label in ROLL_FRONT:
        if d >= start:
            f = (sym, label)
    return f


def di_rows(path=P2.DI_CSV) -> dict:
    """date -> the data-integrity row the Book 1 backtest used (one per date; a hard error otherwise)."""
    out = {}
    for r in csv.DictReader(open(path, newline="", encoding="utf-8-sig")):
        if r.get("used_by_backtest") != "True":
            continue
        if r["date"] in out:
            raise SystemExit(f"two used_by_backtest rows on {r['date']}")
        out[r["date"]] = r
    return out


def first_rth_trade(tp: Path, d: dt.date):
    t0 = f"{d.isoformat()} 08:30"
    with gzip.open(tp, "rt") as fh:
        for line in fh:
            if line[:16] >= t0:
                return float(line.split(",")[1])
    return None


def bar_open(path: Path, end: dt.datetime):
    key = end.strftime("%Y-%m-%d %H:%M:%S")
    with open(path) as fh:
        cols = next(fh).strip().split(",")
        io = [c.lower() for c in cols].index("open")
        for line in fh:
            if line[:19] == key:
                return float(line.split(",")[io])
    return None


def row_for(d, closes, cal, di, gex, v3, nqb, esb, prow, maps, plans, block1):
    ds, ymd = d.isoformat(), d.strftime("%Y%m%d")
    r = dict(session=ds, weekday=d.strftime("%a"), session_type="HALF_DAY" if d in S.HALF_DAYS else "FULL",
             close_ct=closes[d].strftime("%H:%M"), cash_end_ct="12:00" if d in S.HALF_DAYS else "15:00",
             exposure="EXPOSED" if d in EXPOSED else "UNEXPOSED", exposure_source=EXPOSURE_SOURCE.get(d, ""),
             calendar_events="; ".join(f"{c['event']} ({c['action']}{' ' + c['no_trade_ct'] if c['no_trade_ct'] else ''})"
                                       for c in cal if c["date"] == ds and c["status"] != "CANCELED"))
    gaps = []
    x = di.get(ds, {})
    f = Path(block1) / x["file"] if x.get("file") else None
    r["mbo_file"] = x.get("file", "")
    r["mbo_mb"] = round(f.stat().st_size / 1e6, 1) if f and f.exists() else ""
    if not f or not f.exists():
        gaps.append("raw MBO file missing")
    r.update(di_condition=x.get("databento_condition", ""), di_session=x.get("session", ""), di_contract=x.get("main_contract", ""),
             di_nt_contract=x.get("nt_contract", ""), di_rth_last_trade=x.get("rth_last_trade_ct", ""),
             di_gaps_trades_over_60s=x.get("gaps_trades_over_60s", ""))
    sym, label = front(d)
    r.update(front_by_roll=sym, instrument_label=label, roll_day="Y" if d in S.ROLL_DATES else "N")
    if not x:
        gaps.append("no data-integrity row")
    elif x.get("main_contract") != sym or x.get("nt_contract") != sym or x.get("contract_ok") != "True":
        gaps.append(f"contract {x.get('main_contract')} / NT {x.get('nt_contract')} is not the front {sym}")
    tp = Path(block1) / "tapes" / f"tape_{ymd}.csv.gz"
    r["tape_file"] = str(tp)
    if tp.exists():
        r.update(P2.tape_stats(tp, d, closes[d]))
        if dt.datetime.fromisoformat(r["tape_last"]) < closes[d] - dt.timedelta(seconds=60):
            gaps.append(f"tape ends {r['tape_last']}, more than 60 s before the close")
        p_tape, p_bar = first_rth_trade(tp, d), bar_open(Path(maps) / "nq_1m.csv", dt.datetime.combine(d, dt.time(8, 31)))
        r.update(tape_first_rth_price=p_tape, bar_0831_open=p_bar,
                 tape_minus_bar_pts=round(p_tape - p_bar, 2) if p_tape is not None and p_bar is not None else "")
        if p_tape is None or p_bar is None or abs(p_tape - p_bar) > BASIS_MAX_PTS:
            gaps.append(f"tape price basis: first RTH trade {p_tape} vs bar open {p_bar}")
    else:
        gaps.append("tape missing")
    need = (closes[d] - dt.datetime.combine(d, dt.time(8, 30))).seconds // 60
    r.update(nq_rth_bars=nqb[d], es_rth_bars=esb[d], rth_bars_expected=need)
    if nqb[d] != need: gaps.append(f"NQ 1-minute bars {nqb[d]} of {need}")
    if esb[d] != need: gaps.append(f"ES 1-minute bars {esb[d]} of {need}")
    g = gex.get(ds)
    r.update(gex_row="Y" if g else "N", gex_ok=(g or {}).get("ok", ""), gex_regime=(g or {}).get("regime", ""),
             gex_report_date=(g or {}).get("report_date", ""), gex_front=(g or {}).get("front", ""),
             gex_nt_contract=(g or {}).get("nt_contract", ""), gex_nt_shift_pts=(g or {}).get("nt_shift_pts", ""),
             gex_v3_repro=v3.get(ds, {}).get("repro_all_match", ""))
    if not g or g.get("ok") != "True":
        gaps.append("GEX levels row missing or not ok")
    else:
        if g.get("nt_contract") != sym:
            gaps.append(f"GEX nt_contract {g.get('nt_contract')} is not the front {sym}")
        shifted = float(g.get("nt_shift_pts") or 0) != 0.0
        if shifted != (g.get("front") != g.get("nt_contract")):
            gaps.append(f"GEX nt_shift_pts {g.get('nt_shift_pts')} does not match front {g.get('front')} vs NT {g.get('nt_contract')}")
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
    r["status"] = "DATA_MISSING" if gaps else "OK"
    r["cause"] = "; ".join(gaps)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--maps", required=True); ap.add_argument("--plans", required=True)
    ap.add_argument("--gex-v3", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    block1, maps, plans, gv3, out = (Path(x) for x in (a.block1, a.maps, a.plans, a.gex_v3, a.out))
    sess = S.phase_sessions(PHASE)
    if len(sess) != N_EXPECTED:
        raise SystemExit(f"expected {N_EXPECTED} Phase 4 sessions, got {len(sess)}")
    if not EXPOSED <= set(sess):
        raise SystemExit("an exposed date is not a Phase 4 session")
    closes = {d: S.session_close(d) for d in sess}
    cal = list(csv.DictReader(open(block1 / "econ_calendar_2025-10_2026-04.csv", newline="", encoding="utf-8-sig")))
    di = di_rows()
    gex = {r["session"]: r for r in csv.DictReader(open(block1 / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    v3 = {r["session"]: r for r in csv.DictReader(open(gv3 / "gex_v3_sessions.csv", newline="", encoding="utf-8"))}
    nqb = P2.bar_counts(maps / "nq_1m.csv", sess, closes); esb = P2.bar_counts(maps / "es_1m.csv", sess, closes)
    pman = json.loads((plans / "plan_build_manifest.json").read_text())
    prow = {r["session"]: r for r in pman["rows"]}
    rows = [row_for(d, closes, cal, di, gex, v3, nqb, esb, prow, maps, plans, block1) for d in sess]
    out.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(out / "phase4_sessions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    n_exp = sum(r["exposure"] == "EXPOSED" for r in rows)
    L = [f"# Book 1A Phase 4 sessions and inputs ({VERSION}, Step A1, Nov 9, 2026)", "",
         "Inputs only: no ledger, strategy log or fill was read. Book 1 calendar (`book1a/sessions.py`, "
         "`econ_calendar_2025-10_2026-04.csv`; no cash session Feb 16 Presidents' Day and Apr 3 Good Friday); close "
         "`sessions.session_close` (15:00 CT, no half day in Phase 4); front contract from the NinjaTrader roll (Mar 16, "
         "2026: NQH6 -> NQM6), checked against the data-integrity table row the Book 1 backtest used; tape price basis "
         f"(first RTH trade within {BASIS_MAX_PTS:g} points of the 08:31 NQ bar open); GEX price basis (nt_contract = the "
         "front by roll; nt_shift_pts nonzero exactly when the GEX front differs from it); exposure from replay plan "
         "section 8 (no confirmed date in Phase 4; Parts 5 and 6 unresolved, their approximate weeks EXPOSED, runner "
         "decision). A session with a missing input would be DATA_MISSING with its cause; none is dropped.", "",
         f"Sessions: {len(rows)}; EXPOSED {n_exp}; UNEXPOSED {len(rows) - n_exp}; DATA_MISSING "
         f"{sum(r['status'] == 'DATA_MISSING' for r in rows)}.", "",
         "| session | day | close CT | exposure | front (NT roll) | roll day | packet instrument | MBO file MB | "
         "Databento condition | tape last trade | max gap RTH s | tape - bar pts | NQ / ES RTH bars | GEX front / NT / shift | "
         "GEX regime | GEX V3 repro | plan review | status | cause |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['session']} | {r['weekday']} | {r['close_ct']} | {r['exposure']} | {r['front_by_roll']} | "
                 f"{r['roll_day']} | {r.get('packet_instrument', '')} | {r['mbo_mb']} | {r['di_condition']} | {r.get('tape_last', '')} | "
                 f"{r.get('tape_max_gap_rth_s', '')} | {r.get('tape_minus_bar_pts', '')} | "
                 f"{r['nq_rth_bars']} / {r['es_rth_bars']} of {r['rth_bars_expected']} | "
                 f"{r['gex_front']} / {r['gex_nt_contract']} / {r['gex_nt_shift_pts']} | {r['gex_regime']} | {r['gex_v3_repro']} | "
                 f"{r.get('plan_review', '')} | {r['status']} | {r['cause'] or '-'} |")
    L += ["", "Exposed sessions (replay plan section 8, unresolved dates treated as excluded):", ""]
    L += [f"- {r['session']}: {r['exposure_source']}" for r in rows if r["exposure"] == "EXPOSED"]
    L += ["", "Databento condition other than available (logged; files used by the Book 1 backtest):", ""]
    L += [f"- {r['session']}: {r['di_condition']} ({r['mbo_file']})" for r in rows if r["di_condition"] != "available"]
    L += ["", "Calendar events on the sessions (logged; the plan applies its own rules):", ""]
    L += [f"- {r['session']}: {r['calendar_events']}" for r in rows if r["calendar_events"]]
    L += ["", "Map packet data notes (gaps / notes written by map v2.3):", ""]
    L += [f"- {r['session']}: gaps {r.get('packet_gaps', '')}; notes {r.get('packet_notes', '')}" for r in rows]
    (out / "phase4_sessions.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for r in rows:
        print(r["session"], r["close_ct"], r["front_by_roll"], r["exposure"], r["di_condition"], r["status"], r["cause"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
