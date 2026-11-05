r"""P0.7-P0.9 hand-check sheet for 4 days (Kyron, Nov 4, 2026): every value with the source to check it against.

  python -m book1a.hand_checks.hand_check_sheet --block1 K:\Databento_BackTesting --out <md> --day <date>=<run dir>|<plans dir> [...]

Kyron, Nov 4: Oct 22, 29, 31 and Nov 18 only. For each value the sheet names where to check it:
  - volume-profile values (POC / VAH / VAL, TPO values, highs / lows, HVN / POC areas, delta bands, the double
    distribution blocks): the NinjaTrader Volume Profile tool drawn over the stated window (CT; 5-point rows where the
    rule uses rows; TPO values with the profile in TPO / 30-minute mode);
  - GEX values: `gex_levels_block1.csv`, row session = the day, the named column (the plan reads the `_nt` column,
    which is the level shifted to the NinjaTrader contract, when it is filled);
  - VWAP values: the NinjaTrader VWAP setting named in the sheet (v1.1, Kyron Nov 4: session reset 17:00 CT, weekly
    from Sunday 17:00 CT, the bar stamped 08:10 is the last bar included);
  - the other 08:10 values: the frozen plan sidecar `PreopenPlan_<day>_book1a.json`, the named key.
v1.1 (Kyron, Nov 4, second sheet request): the input numbers behind market_context, balance, value_follows,
on_inventory and draw_status with the chart window to check each in (Kyron checks the inputs, not the label); the
tolerance rule; the weekly double distribution criteria values (all HVN blocks, the low-volume and single-print
separator rows, the row table). The sheet rebuilds each day's plan with the frozen code and stops unless the rebuilt
plan text equals the frozen plan file byte for byte, so the evidence is the evidence of the frozen plan.
v1.2 (Kyron, Nov 5, 2026): htf_acceptance evidence (first close beyond the HTF edge, close share, volume share, window)
and the context_base -> market_context precedence.
No trades, outcomes or P&L. The hand and match columns are left empty.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path

VERSION = "hand-check-sheet-v1.2"
GEX_COLS = {"CR": "call_resistance", "PS": "put_support", "HVL": "hvl", "CR_0DTE": "call_resistance_0dte",
            "PS_0DTE": "put_support_0dte", "HVL_0DTE": "hvl_0dte"}

TOLERANCE = ("**Tolerance (Kyron, Nov 4).** Highs and lows must match exactly. A profile value (POC, VAH, VAL, an HVN / LVN "
             "block edge, a separator edge, a delta band edge) may differ from the chart by at most one 5-point row, and only "
             "if that difference does not change whether a zone forms, merges or becomes a decision zone. Any other "
             "difference is material: write it in the match column as MATERIAL.")


def vwap_setting(scope: str, d: date, V) -> str:
    """The NinjaTrader VWAP setting to check a VWAP value against (Kyron, Nov 4)."""
    start = V.week_start(d) if scope == "WEEKLY" else V.session_start(d)
    reset = (f"weekly, anchored at Sunday 17:00 CT ({start.strftime('%a %b %d %H:%M')})" if scope == "WEEKLY"
             else f"session, reset at 17:00 CT ({start.strftime('%a %b %d %H:%M')})")
    return (f"NT VWAP (Order Flow VWAP), {reset}, ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a "
            "1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included)")


def _f(x, nd=2):
    return "" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def _yn(b):
    return "Y" if b else "N"


PRECEDENCE_TEXT = ("BULLISH + ABOVE = BULLISH; BEARISH + BELOW = BEARISH; BULLISH + BELOW or BEARISH + ABOVE = NONE (conflict); "
                   "BALANCED stays BALANCED whatever the acceptance; NONE_NO_EVIDENCE + ABOVE = BULLISH, + BELOW = BEARISH; "
                   "NONE_CONFLICT stays NONE; no acceptance (NONE) = the existing label kept")


def htf_acceptance_evidence(ev, bars_win, htf_win):
    """Nov 5, 2026: PO-9 acceptance, unchanged, at the HTF composite VAL and VAH (bars closed by 08:10 CT only)."""
    from book1a import plan_fields as PF
    L = [f"**htf_acceptance = {ev['htf_acceptance']}.** Rule (Context doc, Nov 5, 2026; {PF.HTF_ACCEPTANCE_LABEL}): the PO-9 "
         "acceptance definition, unchanged, at the HTF composite VAH and VAL: price at 08:10 beyond the edge, >= 60 minutes since "
         "the first 1-minute close beyond it (the first close of the current run of closes beyond, scanning back from 08:10), "
         ">= 80% of the closes since then beyond it, >= 20% of the volume since that close beyond it; bars closed at or before "
         "08:10 CT only (the bar stamped 08:10 = trades 08:09:00-08:09:59.999 is the last one). ACCEPTED_ABOVE at the VAH = "
         "ABOVE, ACCEPTED_BELOW at the VAL = BELOW, else NONE. Context evidence only, never an entry signal. "
         f"Precedence: {PRECEDENCE_TEXT}.", "",
         "| edge | level | state | first 1-minute close beyond (CT, close) | minutes since | closes beyond | volume beyond | "
         "window (CT) | hand | match |", "|---|---|---|---|---|---|---|---|---|---|"]
    for a in ev.get("htf_accept") or []:
        side = "below" if a["name"].endswith("VAL") else "above"
        if a["first_close_ct"]:
            fc = f"{a['first_close_ct'][:16].replace('T', ' ')} ({a['first_close']})"
            if a["excursion_starts_at_window_start"]:
                fc += "; every bar in the window closed beyond it, so the run starts at or before the window start"
        else:
            fc = "none (price at 08:10 not " + side + " the edge)" if a["state"] == "INSIDE" else "none"
        mins = "" if a["minutes"] is None else f"{a['minutes']} (need >= 60)"
        cs = "" if a["close_share"] is None else f"{a['close_share'] * 100:.1f}% (need >= 80%)"
        vs = "" if a["volume_share"] is None else f"{a['volume_share'] * 100:.1f}% (need >= 20%)"
        L.append(f"| {a['name']} ({side}) | {a['level']} | {a['state']} | {fc} | {mins} | {cs} | {vs} | "
                 f"{bars_win}; level from the {htf_win} | | |")
    if not ev.get("htf_accept"):
        L.append("| HTF VAL / VAH | missing | not computed | | | | | | | |")
    L += ["", f"**Precedence result:** context_base {ev['context_base']} + htf_acceptance {ev['htf_acceptance']} = market_context "
          f"**{ev['market_context']}**.", ""]
    return L


def context_evidence(d, ds, ev, pk, hm, V, prior_sessions):
    """Tables of the input numbers behind market_context, balance, value_follows, on_inventory and draw_status."""
    pdd, pd2d = prior_sessions(d)[0], prior_sessions(d)[1]
    cash = lambda x: f"{x.strftime('%a %b %d')} cash 08:30-15:00 CT"
    fullday = lambda x: f"{x.strftime('%a %b %d')} full trading day ({(x - timedelta(days=1)).strftime('%a %b %d')} 17:00 - {x.strftime('%a %b %d')} 16:00 CT)"
    on_win = f"overnight {hm(V.session_start(d))} - {ds[5:]} 08:10 CT"
    wk_win = f"developing week {hm(V.week_start(d))} - {ds[5:]} 08:10 CT"
    htf = pk.get("htf_composite") or {}
    htf_win = (f"HTF composite: {htf.get('days_used')} days from {htf.get('first_day')} through {htf.get('minute_through_ct')} "
               f"(map source {htf.get('source')})")
    bars_win = f"1-minute bars {ev['bars_from'][:16].replace('T', ' ')} - {ev['bars_to'][:16].replace('T', ' ')} CT"
    price = ev["price"]
    T = lambda: ["| input | value | check in (chart window) | hand | match |", "|---|---|---|---|---|"]
    L = ["### Context evidence: the inputs behind each label (check the inputs on the chart, not the label)", ""]

    # market_context
    L += [f"**market_context = {ev['market_context']}** (context_base = {ev['context_base']}, htf_acceptance = "
          f"{ev['htf_acceptance']}). Step 1, context_base (plan_fields.context_base): BULLISH = price >= HTF VAL, the low "
          f"of the bars window <= HTF VAL (held or reclaimed it) and the weekly VAL state is not ACCEPTED_BELOW; BEARISH = the "
          f"mirror at HTF VAH (state not ACCEPTED_ABOVE); exactly one of them = that label; else BALANCED if the balance "
          f"composite overlaps; else NONE_CONFLICT if a directional read passed but the weekly acceptance blocked it (or both "
          f"reads passed), else NONE_NO_EVIDENCE. Step 2, the Nov 5 precedence with htf_acceptance (below).", ""] + T()
    L += [f"| price at 08:10 | {price} | close of the bar stamped 08:10 (1-minute chart) | | |",
          f"| HTF VAL | {ev['htf_val']} | NT VP over the {htf_win} | | |",
          f"| HTF VAH | {ev['htf_vah']} | same HTF composite profile | | |",
          f"| HTF POC | {ev['htf_poc']} | same HTF composite profile | | |",
          f"| low of the bars window | {ev['bars_low']} | {bars_win}: lowest low | | |",
          f"| high of the bars window | {ev['bars_high']} | {bars_win}: highest high | | |",
          f"| held or reclaimed HTF VAL (price >= {ev['htf_val']} and low <= {ev['htf_val']}) | {_yn(ev['held_or_reclaimed_val'])} | from the rows above | | |",
          f"| failed or lost HTF VAH (price <= {ev['htf_vah']} and high >= {ev['htf_vah']}) | {_yn(ev['failed_or_lost_vah'])} | from the rows above | | |",
          f"| weekly VAL / VAH | {ev['wk_val']} / {ev['wk_vah']} | NT VP over the {wk_win} | | |",
          f"| weekly VAL state / VAH state | {ev['wk_val_state']} / {ev['wk_vah_state']} | PO-9 acceptance on 1-minute closes vs the weekly VAL / VAH: INSIDE = price at 08:10 inside the weekly value (or on the inside of that edge); TESTING = price beyond the edge, not yet accepted; ACCEPTED_* = the minutes since the first close beyond it, the share of closes beyond and the share of volume beyond meet the frozen PO-9 thresholds (>= 60 minutes, >= 80% of closes, >= 20% of volume) (details in the plan lines `wkval_state=` / `wkvah_state=`) | | |",
          f"| balance composite overlaps | {_yn((ev['balance_composite'] or {}).get('overlapping'))} | see balance below | | |",
          f"| context_base | {ev['context_base']} | from the rows above | | |", ""]
    L += htf_acceptance_evidence(ev, bars_win, htf_win)

    # balance
    bc = ev["balance_composite"] or {}
    pd1, pd2, on = ev["pd"], ev["pd2"], ev["overnight"]
    L += [f"**balance = {(str(bc.get('val')) + '-' + str(bc.get('vah'))) if bc.get('overlapping') else 'none'}"
          f"{', balance_poc = ' + str(bc.get('poc')) if bc.get('overlapping') else ''}.** Rule (map BalanceJson): PD and ON "
          "value areas must overlap; PD2 joins if PD2 and PD overlap; the members are merged into one volume profile and its "
          "70% value area is the balance. Overlap % = overlap / the narrower value area.", ""] + T()
    L += [f"| PD2 VAH / POC / VAL | {pd2.get('vah')} / {pd2.get('poc')} / {pd2.get('val')} | NT VP over {cash(pd2d)} | | |",
          f"| PD VAH / POC / VAL | {pd1.get('vah')} / {pd1.get('poc')} / {pd1.get('val')} | NT VP over {cash(pdd)} | | |",
          f"| ON VAH / POC / VAL | {on.get('vah')} / {on.get('poc')} / {on.get('val')} | NT VP over the {on_win} | | |",
          f"| overlap PD2-PD | {_f(bc.get('overlap_pct_pd2_pd'), 1)}% | from the PD2 and PD value areas | | |",
          f"| overlap PD-ON | {_f(bc.get('overlap_pct_pd_on'), 1)}% | from the PD and ON value areas | | |",
          f"| members | {', '.join(bc.get('members') or []) or 'none'} | | | |"]
    if bc.get("overlapping"):
        L.append(f"| merged VAH / POC / VAL | {bc.get('vah')} / {bc.get('poc')} / {bc.get('val')} | NT VP over the members' windows together "
                 f"({', '.join(bc.get('members') or [])}; PD and PD2 cash only, ON {on_win}); not one continuous window, so check the member values above first | | |")
        L.append(f"| merged high / low | {bc.get('high')} / {bc.get('low')} | highs and lows of the members' windows | | |")
    L.append("")

    # value_follows
    up = (pd1.get("day_high", 0) > pd2.get("day_high", 0), pd1.get("vah", 0) < pd2.get("vah", 0), pd1.get("poc", 0) < pd2.get("poc", 0))
    dn = (pd1.get("day_low", 0) < pd2.get("day_low", 0), pd1.get("val", 0) > pd2.get("val", 0), pd1.get("poc", 0) > pd2.get("poc", 0))
    L += [f"**value_follows = {ev['value_follows']}.** Rule (plan_fields.value_follows): DIVERGENT_UP = PD high > PD2 high AND PD "
          "VAH < PD2 VAH AND PD POC < PD2 POC; DIVERGENT_DOWN = PD low < PD2 low AND PD VAL > PD2 VAL AND PD POC > PD2 POC; "
          "else WITH_PRICE. Highs and lows are the full trading day; value areas are the cash session.", ""] + T()
    L += [f"| PD high / low | {pd1.get('day_high')} / {pd1.get('day_low')} | {fullday(pdd)}: high / low | | |",
          f"| PD2 high / low | {pd2.get('day_high')} / {pd2.get('day_low')} | {fullday(pd2d)}: high / low | | |",
          f"| PD VAH / VAL / POC | {pd1.get('vah')} / {pd1.get('val')} / {pd1.get('poc')} | NT VP over {cash(pdd)} | | |",
          f"| PD2 VAH / VAL / POC | {pd2.get('vah')} / {pd2.get('val')} / {pd2.get('poc')} | NT VP over {cash(pd2d)} | | |",
          f"| DIVERGENT_UP tests: higher high / lower VAH / lower POC | {' / '.join(_yn(x) for x in up)} | from the rows above | | |",
          f"| DIVERGENT_DOWN tests: lower low / higher VAL / higher POC | {' / '.join(_yn(x) for x in dn)} | from the rows above | | |", ""]

    # on_inventory
    oi = ev["on_inventory"]
    ref_kind = "ON VWAP" if on.get("vwap") is not None else ("ON POC" if on.get("poc") is not None else "price (no ON data)")
    ref_val = on.get("vwap") if on.get("vwap") is not None else on.get("poc")
    settle = ev["settle"]
    L += [f"**on_inventory = {oi['on_inventory']}, on_vs_settle = {oi['on_vs_settle']}.** Rule (plan_fields.on_inventory): "
          f"NET_LONG if price at 08:10 > the {ref_kind}, NET_SHORT if below; on_vs_settle = price - the PD settlement. The "
          "overnight high / low vs the settlement are shown for reference; the rule does not use them.", ""] + T()
    L += [f"| {ref_kind} | {_f(ref_val)} | {('session VWAP: ' + vwap_setting('SESSION', d, V)) if ref_kind == 'ON VWAP' else 'NT VP over the ' + on_win} | | |",
          f"| price at 08:10 | {price} | close of the bar stamped 08:10 | | |",
          f"| PD settlement | {settle} | {pdd.strftime('%a %b %d')}: volume-weighted price of the trades in the 30 s before 15:00 CT (map SettleOf); CME's settlement can differ by a tick | | |",
          f"| on_vs_settle (price - settlement) | {oi['on_vs_settle']} | from the rows above | | |",
          f"| ON high / ON low | {on.get('high')} / {on.get('low')} | {on_win}: high / low | | |",
          f"| ON high - settlement / ON low - settlement (reference) | {_f(on.get('high') - settle if on.get('high') is not None and settle is not None else None)} / "
          f"{_f(on.get('low') - settle if on.get('low') is not None and settle is not None else None)} | from the rows above | | |", ""]

    # draw_status
    L += [f"**draw_status = {ev['draw_status']}.** Rule (plan_v24): the draw is the nearest candidate in the context direction: "
          "BULLISH = HTF POC / HTF VAH above price, MAP4 POC areas above price, GEX levels above price; BEARISH = the mirror "
          "below price. NONE = no draw candidate exists (Context spec, Kyron Nov 4); it is never treated as ACTIVE: no draw= "
          "line is written and the ladder gets no draw.", ""]
    if ev["draw_candidates"]:
        L += ["| candidate | level (with pad) | distance pts | check in | hand | match |", "|---|---|---|---|---|---|"]
        for c in ev["draw_candidates"]:
            L.append(f"| {c['name']} | {c['lo']} - {c['hi']} | {c['dist']} | see the level's source | | |")
    else:
        why = (f"market_context is {ev['market_context']}, so the rule has no direction to look in and no candidate exists"
               if ev["market_context"] not in ("BULLISH", "BEARISH") else "no candidate level lies in the context direction")
        L += [f"No candidate: {why}. For reference, the HTF levels the rule would scan: HTF POC {ev['htf_poc']} "
              f"({'above' if (ev['htf_poc'] or 0) > price else 'below'} price), HTF VAH {ev['htf_vah']}, HTF VAL {ev['htf_val']} "
              f"(price {price}). Check that the context inputs above give {ev['market_context']}; then NONE follows.", ""]
    return L


def weekly_dd_criteria(d, ds, rows, sc, hm, V, WD):
    """The frozen weekly double-distribution criteria values (E23) from the map tape, checked against the sidecar."""
    ws = V.week_start(d)
    as_of = datetime.combine(d, time(8, 10), tzinfo=ws.tzinfo)
    w = sc.get("weekly_dd") or {}
    if w.get("status") == "UNAVAILABLE":
        return ["### Weekly double distribution: UNAVAILABLE", "", f"{w.get('reason')}. The rule was not run (E26).", ""]
    prof = WD.build_profile(rows, ws, as_of)
    res = WD.double_distribution(dict(prof.vol), WD.single_prints(dict(prof.tpo), "TPO_WK"), "WK")
    for k in ("double_distribution", "lower_hvn", "upper_hvn", "separator", "separator_lo", "separator_hi"):
        if res.get(k) != w.get(k):
            raise SystemExit(f"{ds}: weekly DD recomputed {k}={res.get(k)} differs from the sidecar {w.get(k)}")
    r5 = defaultdict(int)
    for k, v in prof.vol.items():
        r5[k // WD.HVN_TICKS_PER_ROW] += v
    mn, mx = min(r5), max(r5)
    raw = [r5.get(r, 0) for r in range(mn, mx + 1)]
    n = len(raw)
    sm = [((raw[i - 1] if i else 0) + raw[i] + (raw[i + 1] if i < n - 1 else 0)) / 3.0 for i in range(n)]
    peak = max(sm); ipk = sm.index(peak)
    h_t, l_t = peak * WD.HVN_PCT / 100.0, peak * WD.LVN_PCT / 100.0
    areas = WD.hvn_lvn_areas(dict(r5), "WK")
    hvn = sorted([a for a in areas if a["type"] == "HVN"], key=lambda a: a["lo"])
    lvn = sorted([a for a in areas if a["type"] == "LVN"], key=lambda a: a["lo"])
    sps = WD.single_prints(dict(prof.tpo), "TPO_WK")
    px = lambda i: round((mn + i) * WD.HVN_TICKS_PER_ROW * WD.TICK, 2)
    L = [f"### Weekly double distribution: frozen criteria values (ours: PD rule applied to weekly, {w.get('version')})", "",
         f"Profile: NT VP over the developing week {hm(ws)} - {ds[5:]} 08:10 CT (last trade used {(w.get('last_trade_ct') or '')[:19]}), "
         f"volume, 5-point rows (NT VP set to 20 ticks per row; row lo = a multiple of 5.00; a row holds lo to lo + 4.75). TPO rows: the same 5-point rows, "
         "30-minute periods (period = floor(minutes since 2000-01-01 CT / 30)).", "",
         "| criterion (frozen) | value | hand | match |", "|---|---|---|---|",
         f"| rows in the profile | {n} ({px(0)} - {px(n - 1)}) | | |",
         f"| smoothing | smoothed row = (row below + row + row above) / 3 | | |",
         f"| peak smoothed row | {px(ipk)}: {peak:,.0f} | | |",
         f"| HVN line: smoothed >= {WD.HVN_PCT}% of peak | {h_t:,.0f} | | |",
         f"| LVN line: smoothed <= {WD.LVN_PCT}% of peak, only between the first and last HVN row | {l_t:,.0f} | | |",
         f"| single prints: runs of >= {WD.MIN_SINGLE_PRINT_ROWS} TPO rows touched by exactly 1 period | {len(sps)} run(s) | | |",
         f"| split = the first neighbouring HVN pair (low to high) whose gap a separator touches; LVNs before single prints | "
         f"lower HVN {w['lower_hvn'][0]} - {w['lower_hvn'][1]}; {w['separator']} {w['separator_lo']} - {w['separator_hi']}; "
         f"upper HVN {w['upper_hvn'][0]} - {w['upper_hvn'][1]} | | |", "",
         "All HVN blocks (runs of rows at or above the HVN line):", "",
         "| # | block | rows | highest smoothed (% of peak) | used in the split | hand | match |", "|---|---|---|---|---|---|---|"]
    for j, a in enumerate(hvn, 1):
        i0, i1 = int(round(a["lo"] / 5.0)) - mn, int(round((a["hi"] + WD.TICK) / 5.0)) - mn - 1
        top = max(sm[i0:i1 + 1])
        used = "lower" if [a["lo"], a["hi"]] == list(w["lower_hvn"]) else ("upper" if [a["lo"], a["hi"]] == list(w["upper_hvn"]) else "")
        L.append(f"| {j} | {a['lo']} - {a['hi']} | {i1 - i0 + 1} | {top:,.0f} ({top / peak:.0%}) | {used} | | |")
    L += ["", "Low-volume separators (LVN runs) and single-print runs:", "",
          "| type | rows | lies in the gap of HVN pair | used | hand | match |", "|---|---|---|---|---|---|"]
    for s in lvn + sps:
        pair = ""
        for j in range(1, len(hvn)):
            if not (s["hi"] < hvn[j - 1]["hi"] or s["lo"] > hvn[j]["lo"]):
                pair = f"{j} / {j + 1}"; break
        used = "Y" if (s["lo"], s["hi"]) == (w["separator_lo"], w["separator_hi"]) and ((s["type"] == "SP") == (w["separator"] == "SINGLE_PRINTS")) else ""
        L.append(f"| {'single prints' if s['type'] == 'SP' else 'LVN'} | {s['lo']} - {s['hi']} | {pair or 'none'} | {used} | | |")
    # the row table: 2 rows below the lower HVN's top edge through 2 rows above the upper HVN's bottom edge, plus each block's outer edges
    lo_b, up_b = w["lower_hvn"], w["upper_hvn"]
    gi0 = max(0, int(round(lo_b[1] / 5.0)) - mn - 2)
    gi1 = min(n - 1, int(round(up_b[0] / 5.0)) - mn + 2)
    edges = {max(0, int(round(lo_b[0] / 5.0)) - mn - 1), int(round(lo_b[0] / 5.0)) - mn,
             int(round(up_b[1] / 5.0)) - mn, min(n - 1, int(round(up_b[1] / 5.0)) - mn + 1)}
    idx = sorted(set(range(gi0, gi1 + 1)) | edges)
    tpo = dict(prof.tpo)
    L += ["", f"Row table: the gap between the two split blocks (2 rows either side) and the outer edges of both blocks. "
          f"HVN line {h_t:,.0f}, LVN line {l_t:,.0f}.", "",
          "| row lo | volume | smoothed | % of peak | TPO periods | flags | hand | match |", "|---|---|---|---|---|---|---|---|"]
    prev = None
    for i in idx:
        if prev is not None and i != prev + 1:
            L.append("| ... | | | | | | | |")
        prev = i
        p = px(i)
        fl = []
        if sm[i] >= h_t: fl.append("HVN")
        if sm[i] <= l_t and hvn and hvn[0]["lo"] <= p <= hvn[-1]["hi"]: fl.append("LVN")
        if any(s["lo"] <= p <= s["hi"] for s in sps): fl.append("SP")
        if w["separator_lo"] <= p <= w["separator_hi"]: fl.append("separator")
        L.append(f"| {p} | {raw[i]:,} | {sm[i]:,.0f} | {sm[i] / peak:.0%} | {tpo.get(mn + i, 0)} | {', '.join(fl)} | | |")
    L.append("")
    return L


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--day", action="append", required=True, help="<date>=<run dir>|<plans dir>")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from book1a import families as F, vwap as V, weekly_dd as WD
    from book1a.hand_checks.hand_check_pack import hm, level_source, prior_sessions
    from book1a.hand_checks.plan_hand_check import _rows, build_day, load_inputs
    gexd, cal = load_inputs(Path(a.block1))
    gex = {r["session"]: r for r in csv.DictReader(open(Path(a.block1) / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    L = [f"# P0.7-P0.9 hand-check sheet: Oct 22, 29, 31 and Nov 18, 2025 ({VERSION})", "",
         "Check each value against the source named on its row, not against the plan. Sources: **NT VP** = the NinjaTrader "
         "Volume Profile tool drawn over the stated window (CT); **NT VWAP** = the NinjaTrader VWAP setting stated on the row; "
         "**GEX csv** = `gex_levels_block1.csv`, row session = the day, the named column; **sidecar** = the frozen plan sidecar "
         "`PreopenPlan_<day>_book1a.json`, the named key. Every value is frozen at 08:10 CT from data before 08:10 CT. "
         "No trades, outcomes or P&L.", "",
         TOLERANCE, "",
         "**VWAP.** The VWAP formula (volume-weighted price of all trades from the reset to 08:09:59.999 CT, and the volume-"
         "weighted standard deviation for the +/-1 sigma bands) was already verified against raw Databento trades in P0.6 "
         "(Oct 22, Nov 5 and both roll days). Here only check that the NinjaTrader VWAP with the stated setting shows the same "
         "numbers at the bar stamped 08:10.", "",
         "Each day's plan was rebuilt with the frozen code for this sheet; the rebuilt plan text equals the frozen plan file "
         "byte for byte, so the evidence tables are the inputs of the frozen plan.", ""]
    for spec in a.day:
        ds, rest = spec.split("=", 1)
        run, plans = (Path(x) for x in rest.split("|"))
        d = date.fromisoformat(ds)
        ev = {}
        text, _side, pk = build_day(run, ds, gexd, cal, evidence=ev)
        frozen = (plans / f"PreopenPlan_{ds}_book1a.txt").read_text(encoding="utf-8")
        if text != frozen:
            raise SystemExit(f"{ds}: the rebuilt plan differs from the frozen plan {plans}; the evidence would not be the frozen plan's")
        side_file = plans / f"PreopenPlan_{ds}_book1a.json"
        sc = json.load(open(side_file))
        g = gex.get(ds) or {}
        lv = {l["name"]: float(l["price"]) for l in pk.get("levels", []) if l.get("price") is not None}
        bands = {b["label"]: b for b in sc.get("delta_bands", [])}
        areas = {x["label"]: x for x in sc.get("map4_areas", [])}
        vw = sc.get("vwap") or {}

        def vwap_key(n):
            k = "WEEKLY" if n.startswith(("WKVWAP", "WVWAP")) else "SESSION"
            key = "vwap" if n in ("VWAP", "WKVWAP", "WVWAP") else ("sd1_up" if n.endswith(("UP", "U1")) else "sd1_dn")
            return k, key

        def src(name):
            n = name.upper()
            if n in GEX_COLS or n.startswith("GAMMA"):
                col = GEX_COLS.get(n, name.lower())
                used = col + "_nt" if g.get(col + "_nt") not in (None, "") else col
                return "GEX", f"GEX csv: row {ds}, column `{used}` (= {g.get(used)}); CME report {g.get('report_date')} (D-1)"
            if n.startswith(("WKVWAP", "WVWAP", "VWAP")):
                k, key = vwap_key(n)
                band = {"vwap": "the VWAP line", "sd1_up": "the +1 sigma band", "sd1_dn": "the -1 sigma band"}[key]
                return "VWAP", f"{band}: {vwap_setting(k, d, V)}"
            if name in bands:
                b = bands[name]
                return "VP", f"NT VP with delta, {b.get('profile')} profile ({level_source(b.get('profile', '') + 'POC', d).split(',')[0]}), 5-pt rows {b['lo']}-{b['hi']}: {b.get('sign')} delta, each row in the top 20% of abs delta"
            if name in areas:
                x = areas[name]
                return "VP", f"NT VP, {level_source(name[:2] + 'POC', d).split(',')[0]}, 5-pt rows >= 70% of the peak row ({x.get('peak_row_lo')})"
            ls = level_source(name, d)
            if ls.startswith("packet level") or ls.startswith("HTF"):
                return "VP", "NT VP over the packet's window (" + ls + ")"
            return "VP", "NT VP, " + ls
        L += [f"## {ds} ({d.strftime('%a')})", "",
              f"Plan {sc['plan'][0].split()[-1].rstrip(')')}; market_context {sc['market_context']}; review {sc['review']}; "
              f"{len(sc['zones'])} decision zones.", "",
              "### 08:10 values", "", "| value | plan / sidecar value | check against | hand | match |", "|---|---|---|---|---|"]
        kv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in sc["plan"] if "=" in l and not l.startswith("#")}
        L.append(f"| price at 08:10 (packet ref_price) | {pk.get('ref_price')} | close of the bar stamped 08:10 on a 1-minute chart | | |")
        for k in ("SESSION", "WEEKLY"):
            v = vw.get(k) or {}
            for key, band in (("vwap", "the VWAP line"), ("sd1_up", "the +1 sigma band"), ("sd1_dn", "the -1 sigma band")):
                if key in v:
                    L.append(f"| {k.lower()} {key} | {v[key]:.2f} | {band}: {vwap_setting(k, d, V)} | | |")
        for k in ("market_context", "context_base", "htf_acceptance", "draw_status", "draw", "balance", "balance_poc", "value_follows", "on_inventory", "on_vs_settle"):
            if k in kv:
                L.append(f"| {k} | {kv[k]} | the inputs in the context evidence below (sidecar `plan` line `{k}=`) | | |")
        for k in ("htf_structure", "gex_regime", "wkval_state", "wkvah_state", "htfval_state", "htfvah_state"):
            if k in kv:
                L.append(f"| {k} | {kv[k]} | sidecar `plan` line `{k}=` | | |")
        w = sc.get("weekly_dd") or {}
        L.append(f"| weekly double distribution | {w.get('status')}; split {'yes' if w.get('double_distribution') else 'no'} | "
                 f"{'the criteria table below' if w.get('double_distribution') else 'sidecar `weekly_dd`'} (ours: PD rule applied to weekly) | | |")
        L += [""] + context_evidence(d, ds, ev, pk, hm, V, prior_sessions)
        L += ["### GEX values (source: GEX csv)", "", "| level | value in plan | check against | hand | match |", "|---|---|---|---|---|"]
        for line in sc["plan"]:
            if line.startswith("mq_"):
                nm = line.split("=")[0][3:].upper()
                L.append(f"| {nm} | {line.split('=')[1]} | {src(nm)[1]} | | |")
        L.append(f"| regime | {g.get('regime')} | GEX csv: row {ds}, column `regime` | | |")
        L += ["", "### Decision zones: every level behind each zone", ""]
        for z in sc["zones"]:
            L += [f"**{z['label']}**: {z['lo']} - {z['hi']} ({z['hi'] - z['lo']:.2f} pts); families {len(z['families'])}: "
                  f"{', '.join(z['families'])}; long={z['long']} short={z['short']}; stop {z['stop_ticks']} ticks", "",
                  "| level | type | value | inside zone / distance | check against | hand | match |", "|---|---|---|---|---|---|---|"]
            for name in dict.fromkeys(z["levels"]):
                kind, where = src(name)
                if name in bands or name in areas:
                    x = bands.get(name) or areas.get(name)
                    val, pos = f"{x['lo']} - {x['hi']}", "overlaps"
                else:
                    px = lv.get(name)
                    if px is None and kind == "VWAP":
                        k, key = vwap_key(name.upper())
                        px = round(vw.get(k, {}).get(key), 2) if vw.get(k, {}).get(key) is not None else None
                    if px is None and kind == "GEX":
                        col = GEX_COLS.get(name.upper())
                        px = g.get(col + "_nt") or g.get(col) if col else None
                        px = float(px) if px not in (None, "") else None
                    val = px
                    pos = "" if px is None else ("inside" if z["lo"] <= px <= z["hi"] else f"{min(abs(px - z['lo']), abs(px - z['hi'])):.2f} pts outside")
                fam = "DELTA" if name in bands else ("VOLUME" if name in areas else (F.family_of(name) or "unmapped"))
                L.append(f"| {name} | {fam} / {kind} | {val} | {pos} | {where} | | |")
            for key, what in (("dd_edge", "PD"), ("dd_edge_wk", "weekly")):
                dd = sc.get(key)
                if dd and dd["label"] in z["label"]:
                    win = (f"{prior_sessions(d)[0].strftime('%a %b %d')} cash 08:30-15:00 CT" if what == "PD"
                           else f"developing week {hm(V.week_start(d))} - 08:10 CT")
                    L.append(f"| {dd['label']} | STRUCTURE / VP | {dd['lo']} - {dd['hi']} | overlaps | NT VP over {win}, 5-pt rows: the {what} double "
                             f"distribution (two HVN blocks >= 70% of the smoothed peak, separator {dd.get('separator_lo')} - {dd.get('separator_hi')}"
                             f"{'; criteria table below' if what == 'weekly' else ''}) | | |")
            for r in sc.get("rej_flip_zones", []):
                if f"{r['kind']}_{r['session']}" in z["label"] and r["lo"] <= z["hi"] and r["hi"] >= z["lo"]:
                    L.append(f"| {r['kind']}_{r['session']} | STRUCTURE / chart | {r['lo']} - {r['hi']} | overlaps | 1-minute chart: swing bar close "
                             f"{hm(datetime.fromisoformat(r['formed_ct']))}, swing {r.get('swing_price')}; available {hm(datetime.fromisoformat(r['confirmed_ct'])) if r.get('confirmed_ct') else ''} (pack section B) | | |")
            L.append("")
        if w.get("double_distribution"):
            ws = V.week_start(d)
            rows = list(_rows(run / "tape_map.csv.gz", ws, datetime.combine(d, time(8, 10), tzinfo=ws.tzinfo)))
            L += weekly_dd_criteria(d, ds, rows, sc, hm, V, WD)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
