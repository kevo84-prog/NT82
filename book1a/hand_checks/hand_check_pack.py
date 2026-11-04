r"""P0.7-P0.9 hand-check pack: one table per zone type with the evidence to find on the chart (Kyron, Nov 4, 2026).

  python -m book1a.hand_checks.hand_check_pack --block1 K:\Databento_BackTesting --out Book1A\Phase0\hand_check_pack\hand_check_pack.md \
      --day 2025-10-22=Book1A\Phase0\runs\phase1:Book1A\Phase0\plans_phase1 ... (one --day per day: run folder : plans folder)

For every day it reads the map packet, the Book 1A plan sidecar (plan-v2.4-book1a) and the 1-minute bars / 5-point
profiles rebuilt from the map tape up to 08:10 CT (the same inputs plan_v24.build used). It writes, per zone type:
  - DECISION zones: each level behind the zone with its price, family and where it comes from (profile window,
    session, VWAP window, GEX report), so the zone can be rebuilt from the chart;
  - REJ zones (PO-1): the swing bar (close time, price), the 15-bar check before / after, the arrival-evidence bar
    (time, delta), the departure bar (time, price, points), and the body bars that set the far edge;
  - FLIP zones: every REJ zone before selection, whether it was accepted through (3 closes 2 ticks beyond) and by
    which opposite REJ; a FLIP row when one forms;
  - wide-stop zones: width, stop ticks (width + 2) and the C3 risk estimate for 1 NQ against the $1,000 budget;
  - DD_EDGE (PO-11): the packet's PD double distribution (both HVN blocks, the separator), price at 08:10, and the
    PD profile rows (5-point, volume) across the split.
No trade, candidate outcome or P&L is read or written. The "hand" column is left empty for Kyron.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from book1a import bars as B, map_v24 as M, risk as RK, sessions as S, vwap as V
from book1a.hand_checks.plan_hand_check import _rows

CT = ZoneInfo("America/Chicago")
VERSION = "hand-check-pack-v1.0"


def hm(t) -> str:
    return t.astimezone(CT).strftime("%a %b %d %H:%M") if t else ""


def prior_sessions(d: date, n: int = 3):
    return S.sessions(d - timedelta(days=14), d - timedelta(days=1))[-n:][::-1]


def level_source(name: str, d: date) -> str:
    """Where a packet level comes from (map v2.3 names), for finding it on the chart."""
    pd = prior_sessions(d)
    tpo = "TPO" if ("TVA" in name or "TPOC" in name) else "volume"
    n = name.upper()
    def cash(k):
        return f"{pd[k].strftime('%a %b %d')} cash 08:30-15:00 CT"
    for pre, k in (("PD3", 2), ("PD2", 1)):
        if n in (pre + "H", pre + "L"): return f"{cash(k)}, {'high' if n.endswith('H') else 'low'}"
        if n.startswith(pre): return f"{cash(k)}, {tpo} profile"
    if n in ("PDH", "PDL"): return f"{cash(0)}, {'high' if n == 'PDH' else 'low'}"
    if n == "PDSET": return f"{pd[0].strftime('%a %b %d')} settlement (15:00 CT)"
    if n.startswith("PD"): return f"{cash(0)}, {tpo} profile"
    on = f"overnight {hm(V.session_start(d))} - 08:10 CT"
    if n in ("ONH", "ONL"): return f"{on}, {'high' if n == 'ONH' else 'low'}"
    if n.startswith("ON"): return f"{on}, {tpo} profile"
    if n.startswith("PWK"): return f"prior week {hm(V.week_start(d) - timedelta(days=7))} - {hm(V.week_start(d) - timedelta(hours=1))}, {tpo} profile"
    if n.startswith("WKVWAP"): return f"weekly VWAP from {hm(V.week_start(d))}, value at the 08:10 bar close"
    if n.startswith("VWAP"): return f"session VWAP from {hm(V.session_start(d))}, value at the 08:10 bar close"
    if n.startswith("WK"): return f"developing week {hm(V.week_start(d))} - 08:10 CT, {tpo} profile"
    if n.startswith("HTF"): return "HTF composite (packet htf_composite window)"
    if n in ("CR", "PS", "HVL", "CR_0DTE", "PS_0DTE", "HVL_0DTE") or n.startswith("GAMMA"):
        return f"GEX, not on the chart: gex_levels_block1.csv row {d}, CME report {pd[0]} (D-1)"
    if n.startswith("T_DELTA_"): return "delta band (see the delta rows table)"
    if n.endswith("POC_AREA"): return "MAP4 POC area (see the area table)"
    return "packet level (name not mapped; check the packet)"


def load_day(block1: Path, run: Path, plans: Path, ds: str, gex: dict):
    d = date.fromisoformat(ds)
    as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
    hits = sorted((run / "map").glob(f"PreopenPacket_*{ds}.json"))
    if len(hits) != 1:
        raise SystemExit(f"{ds}: expected one map packet, found {len(hits)}")
    packet = json.load(open(hits[0]))
    side = json.load(open(plans / f"PreopenPlan_{ds}_book1a.json"))
    start = V.week_start(d) - timedelta(days=7)
    rows = list(_rows(run / "tape_map.csv.gz", start, as_of))
    bars = B.bars_from_rows(rows, start, as_of)
    pd = prior_sessions(d)[0]
    prof = B.profiles_from_rows(rows, {"PD": (datetime.combine(pd, time(8, 30), tzinfo=CT), datetime.combine(pd, time(15, 0), tzinfo=CT))})
    return dict(d=d, ds=ds, as_of=as_of, packet=packet, side=side, bars=bars, prof=prof, gex=gex.get(ds) or {},
                adr=float((packet.get("ranges") or {}).get("adr_full") or 0) or 400.0, plans=plans)


def level_prices(day) -> dict:
    lv = {l["name"]: float(l["price"]) for l in day["packet"].get("levels", []) if l.get("price") is not None}
    vw = day["side"].get("vwap") or {}
    for nm, k in (("VWAP", "SESSION"), ("WKVWAP", "WEEKLY")):
        if vw.get(k):
            lv[nm] = round(vw[k]["vwap"], 2); lv[nm + "_SD1_UP"] = round(vw[k]["sd1_up"], 2); lv[nm + "_SD1_DN"] = round(vw[k]["sd1_dn"], 2)
    g = day["gex"]
    for k, nm in (("call_resistance", "CR"), ("put_support", "PS"), ("hvl", "HVL"), ("call_resistance_0dte", "CR_0DTE"),
                  ("put_support_0dte", "PS_0DTE"), ("hvl_0dte", "HVL_0DTE")):
        v = g.get(k + "_nt") or g.get(k)
        if v not in (None, ""): lv[nm] = float(v)
    return lv


def decision_table(day, zone) -> list:
    lv = level_prices(day)
    bands = {b["label"]: b for b in day["side"].get("delta_bands", [])}
    areas = {a["label"]: a for a in day["side"].get("map4_areas", [])}
    out = [f"**{day['ds']} {zone['label']}**: {zone['lo']} - {zone['hi']} ({zone['hi'] - zone['lo']:.2f} pts), "
           f"families {len(zone['families'])}: {', '.join(zone['families'])}; long={zone['long']} short={zone['short']}; "
           f"stop {zone['stop_ticks']} ticks; frozen {zone['available_at']}", "",
           "| level | price / rows | inside zone or distance | where it comes from (find on chart) | hand | match |", "|---|---|---|---|---|---|"]
    lab = zone["label"]
    for r in day["side"].get("rej_flip_zones", []):
        if f"{r['kind']}_{r['session']}" in lab and r["lo"] <= zone["hi"] and r["hi"] >= zone["lo"]:
            out.append(f"| {r['kind']}_{r['session']} (STRUCTURE) | {r['lo']} - {r['hi']} | overlaps | swing bar close {hm(datetime.fromisoformat(r['formed_ct']))}, see section B | | |")
    dd = day["side"].get("dd_edge")
    if dd and "DD_EDGE" in lab:
        out.append(f"| {dd['label']} (STRUCTURE) | {dd['lo']} - {dd['hi']} | overlaps | PD double distribution, see section E | | |")
    for name in dict.fromkeys(zone["levels"]):
        if name in bands:
            b = bands[name]
            out.append(f"| {name} | {b['lo']} - {b['hi']} (delta sum {b.get('delta_sum')}) | band | {b.get('profile')} profile, 5-pt rows {b['lo']}-{b['hi']}: {b.get('sign')} delta, each row in the top 20% of abs delta | | |")
            continue
        if name in areas:
            a = areas[name]
            out.append(f"| {name} | {a['lo']} - {a['hi']} (peak row {a.get('peak_row_lo')}, vol {a.get('peak_volume')}) | area | {name[:2]} volume profile, 5-pt rows >= 70% of the peak row | | |")
            continue
        px = lv.get(name)
        if px is None:
            out.append(f"| {name} | not in packet levels | | {level_source(name, day['d'])} | | |"); continue
        where = "inside" if zone["lo"] <= px <= zone["hi"] else f"{min(abs(px - zone['lo']), abs(px - zone['hi'])):.2f} pts outside"
        out.append(f"| {name} | {px} | {where} | {level_source(name, day['d'])} | | |")
    return out


def extents(day, zone) -> list:
    """(name, lo, hi) of every piece behind a zone: point levels, delta bands, MAP4 areas, REJ zones, DD_EDGE."""
    lv = level_prices(day)
    bands = {b["label"]: b for b in day["side"].get("delta_bands", [])}
    areas = {a["label"]: a for a in day["side"].get("map4_areas", [])}
    out = []
    for n in dict.fromkeys(zone["levels"]):
        src = bands.get(n) or areas.get(n)
        if src: out.append((n, src["lo"], src["hi"]))
        elif n in lv: out.append((n, lv[n], lv[n]))
    for r in day["side"].get("rej_flip_zones", []):
        if f"{r['kind']}_{r['session']}" in zone["label"] and r["lo"] <= zone["hi"] and r["hi"] >= zone["lo"]:
            out.append((f"{r['kind']}_{r['session']}", r["lo"], r["hi"]))
    dd = day["side"].get("dd_edge")
    if dd and "DD_EDGE" in zone["label"]: out.append((dd["label"], dd["lo"], dd["hi"]))
    return out


def rej_tables(day) -> tuple:
    """Pre-selection REJ zones with chart evidence, the merge, the flip check, and the selected zones."""
    bars, d, as_of = day["bars"], day["d"], day["as_of"]
    raw = M.rejection_zones(bars, d, as_of, day["adr"])
    rej_rows = ["| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, z in enumerate(raw, 1):
        i = z.extra["swing_index"]; b = bars[i]; hi = z.kind == "REJ_HIGH"
        bef, aft = bars[i - 15:i], bars[i + 1:i + 16]
        ext = (lambda xs: max(xs, key=lambda x: x.high)) if hi else (lambda xs: min(xs, key=lambda x: x.low))
        eb, ea = ext(bef), ext(aft)
        ev_bars = bars[max(0, i - 2):i + 1]
        if z.arrival_evidence.startswith("DELTA"):
            evb = max(ev_bars, key=lambda x: x.delta if hi else -x.delta); evtxt = f"delta {evb.delta}"
        elif z.arrival_evidence == "IMB":
            evb = next(x for x in ev_bars if (x.imb_buy if hi else x.imb_sell)); evtxt = f"stacked {'buy' if hi else 'sell'} imbalance, delta {evb.delta}"
        else:
            evb = next(x for x in ev_bars if (x.large_buy if hi else x.large_sell)); evtxt = f"large {'buy' if hi else 'sell'} trade, delta {evb.delta}"
        dep = bars[i + 1:i + 1 + M.DEPARTURE_BARS]
        dep = [x for x in dep if x.close_ct <= as_of]
        db = (min(dep, key=lambda x: x.low) if hi else max(dep, key=lambda x: x.high)) if dep else None
        win = bars[max(0, i - 2):i + 3]
        fb = min(win, key=lambda x: x.body_lo) if hi else max(win, key=lambda x: x.body_hi)
        rej_rows.append(
            f"| {k} | {z.kind} | {z.session} | {hm(b.close_ct)} | {b.high if hi else b.low} | "
            f"{(eb.high if hi else eb.low)} ({hm(eb.close_ct)[-5:]}) | {(ea.high if hi else ea.low)} ({hm(ea.close_ct)[-5:]}) | "
            f"{hm(evb.close_ct)[-5:]} ({evtxt}) | "
            f"{(hm(db.close_ct)[-5:] + ', ' + str(db.low if hi else db.high)) if db else ''}, {z.departure_pts:.2f} (need >= {M.DEPARTURE_ADR * day['adr']:.2f} = 0.25 ADR) | "
            f"{fb.body_lo if hi else fb.body_hi} at {hm(fb.close_ct)[-5:]} (bars {hm(win[0].close_ct)[-5:]}-{hm(win[-1].close_ct)[-5:]}) | {z.lo} - {z.hi} | | |")
    merged = M.merge_same_side(list(raw))
    flip_rows = ["| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |", "|---|---|---|---|---|"]
    for z in merged:
        acc = M.accepted_through(bars, z.extra.get("swing_index", 0), z, as_of)
        opp = "REJ_HIGH" if z.kind == "REJ_LOW" else "REJ_LOW"
        cands = [o for o in merged if o.kind == opp and acc is not None and o.extra.get("swing_index", 0) > acc]
        ov = [f"{o.kind} {o.lo}-{o.hi} formed {hm(o.formed_ct)}: " + (f"overlap {(min(z.hi, o.hi) - max(z.lo, o.lo)) / z.width:.0%}" if min(z.hi, o.hi) > max(z.lo, o.lo) else "no overlap") for o in cands]
        is_flip = any((min(z.hi, o.hi) - max(z.lo, o.lo)) / z.width >= M.FLIP_OVERLAP for o in cands)
        flip_rows.append(f"| {z.kind} {z.lo}-{z.hi} | {hm(z.formed_ct)} | {'yes, 3rd close ' + hm(bars[acc].close_ct) if acc is not None else 'no'} | {'; '.join(ov) or 'none'} | {'FLIP' if is_flip else 'no'} |")
    flipped = [z for z in M.flips(bars, merged, as_of) if z.kind == "FLIP"]
    return raw, merged, flipped, rej_rows, flip_rows


def dd_table(day) -> list:
    dd, pk = day["side"].get("dd_edge"), day["packet"].get("double_distribution") or {}
    ref = float(day["packet"]["ref_price"])
    out = [f"**{day['ds']}**: packet double_distribution = {json.dumps(pk)}; price at 08:10 (packet ref_price) {ref}", ""]
    if not dd:
        return out + ["No DD_EDGE zone (the packet shows no PD split, or price is inside the separator)."]
    pd = prior_sessions(day["d"])[0]
    out += [f"DD_EDGE_PD zone {dd['lo']} - {dd['hi']} ({dd['hi'] - dd['lo']:.2f} pts, cap 40); runner {dd['runner']}; "
            f"separator {dd['separator_lo']} - {dd['separator_hi']}; frozen {dd['available_at']}.",
            f"Rule: price {'above' if ref >= dd['separator_hi'] else 'below'} the separator, so the far distribution is the "
            f"{'lower' if ref >= dd['separator_hi'] else 'upper'} HVN; its near edge (up to 40 pts) is the zone, its far edge the runner.", "",
            f"PD = {pd.strftime('%a %b %d')} cash 08:30-15:00 CT volume profile, 5-point rows (ours; the map's HVN/LVN bounds come from its own rows):", "",
            "| row lo | volume | packet block | hand | match |", "|---|---|---|---|---|"]
    vol = day["prof"]["PD"]["volume"]
    lo_b, up_b = pk.get("lower_hvn", [0, 0]), pk.get("upper_hvn", [0, 0])
    for r in sorted(k for k in vol if min(lo_b[0], up_b[0]) - 10 <= k <= max(lo_b[1], up_b[1]) + 10):
        blk = "lower HVN" if lo_b[0] <= r <= lo_b[1] else ("upper HVN" if up_b[0] <= r <= up_b[1] else
              ("separator (LVN)" if float(pk.get("separator_lo", 0)) <= r <= float(pk.get("separator_hi", 0)) else ""))
        out.append(f"| {r} | {vol[r]} | {blk} | | |")
    used = [z["label"] for z in day["side"]["zones"] if "DD_EDGE" in z["label"]]
    out += ["", f"In the plan: {'decision zone ' + ', '.join(used) if used else 'not a decision zone (class ' + dd['class'] + '; see research decision_zones_beyond_cap)'}"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--day", action="append", required=True, help="yyyy-mm-dd=<run dir>:<plans dir>")
    ap.add_argument("--decision", nargs="*", default=[], help="day:label of decision zones to tabulate (default: first per day)")
    a = ap.parse_args(argv)
    block1 = Path(a.block1)
    gex = {r["session"]: r for r in csv.DictReader(open(block1 / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    days = []
    for spec in a.day:
        ds, rest = spec.split("=", 1)
        run, plans = rest.rsplit(":", 1) if rest.count(":") > 1 else rest.split(":", 1)
        days.append(load_day(block1, Path(run), Path(plans), ds, gex))
    L = [f"# P0.7-P0.9 hand-check pack ({VERSION})", "",
         "Every value below is frozen at 08:10 CT and comes from data before 08:10 CT. Times are CT, 1-minute bars stamped by "
         "their close (NinjaTrader bar time). Prices are NQ front month as on the chart. No trades, outcomes or P&L. "
         "Fill the hand column from the chart, not from the plan.", "",
         "| day | plan | decision zones | REJ zones before selection | REJ in plan | FLIP | wide stop (> 196 ticks) | DD_EDGE |", "|---|---|---|---|---|---|---|---|"]
    rej_cache = {}
    for dy in days:
        raw, merged, flipped, rr, fr = rej_tables(dy)
        rej_cache[dy["ds"]] = (raw, merged, flipped, rr, fr)
        s = dy["side"]
        wide = [f"{z['label'][:28]} {z['stop_ticks']}" for z in s["zones"] if z["stop_ticks"] > 196]
        L.append(f"| {dy['ds']} | {(dy['plans'] / ('PreopenPlan_' + dy['ds'] + '_book1a.txt')).read_text(encoding='utf-8').splitlines()[0].split()[-1].rstrip(')')} | {len(s['zones'])} | "
                 f"{len(raw)} ({len(merged)} after merge) | {len(s['rej_flip_zones'])} | {len(flipped)} | {'; '.join(wide) or 'none'} | "
                 f"{'yes ' + str(s['dd_edge']['lo']) + '-' + str(s['dd_edge']['hi']) if s.get('dd_edge') else 'no'} |")
    # A. decision zones
    L += ["", "## A. Decision zones (P0.7, P0.8)", "", "Rebuild each zone from its levels: every level must be inside the zone, or a GEX level within "
          "10 points of an edge (C2). Families count once each; DECISION needs 2+.", ""]
    picks = [x.split(":", 1) for x in a.decision] or [[dy["ds"], dy["side"]["zones"][0]["label"]] for dy in days if dy["side"]["zones"]][:1]
    for ds, label in picks:
        dy = next(x for x in days if x["ds"] == ds)
        z = next(z for z in dy["side"]["zones"] if z["label"] == label)
        L += decision_table(dy, z) + [""]
    # B. REJ zones
    L += ["## B. Rejection zones (P0.7, PO-1)", "", "Swing = the bar's high (low) is strictly above (below) the 15 bars before and the 15 after; "
          "arrival evidence = delta >= 150 that way (or a stacked imbalance / large trade) in the swing bar or the 2 before; "
          f"departure = the largest move away within {M.DEPARTURE_BARS} bars, at least 0.25 x ADR; far edge = the body extreme of the "
          "swing bar +/- 2 bars, capped at 40 points, at least 10 points wide.", ""]
    for dy in days:
        raw, merged, flipped, rr, fr = rej_cache[dy["ds"]]
        if raw:
            L += [f"**{dy['ds']}** (ADR {dy['adr']:.2f}; plan keeps: " +
                  ("; ".join(f"{z['kind']} {z['session']} {z['lo']}-{z['hi']}" for z in dy["side"]["rej_flip_zones"]) or "none") +
                  "; decision zones built on a REJ: " + (", ".join(z["label"] for z in dy["side"]["zones"] if "REJ" in z["label"]) or "none") + ")", ""] + rr + [""]
    # C. FLIP
    L += ["## C. Flip zones (P0.7, PO-1 step 4)", "", "A REJ zone accepted through (3 one-minute closes 2 ticks beyond it), then an opposite REJ "
          "after that overlapping it by >= 50%, becomes a FLIP.", ""]
    nflip = 0
    for dy in days:
        raw, merged, flipped, rr, fr = rej_cache[dy["ds"]]
        nflip += len(flipped)
        if merged:
            L += [f"**{dy['ds']}**", ""] + fr + [""]
    if nflip == 0:
        L += [f"No FLIP zone forms on any of these {len(days)} days. Check by hand that no row above should be a FLIP; the FLIP rule "
              "itself is unit-tested only (test_map_v24) until a real day has one.", ""]
    # D. wide stops
    L += ["## D. Wide-stop zones (C3 risk check, U3)", "", "stop ticks = zone width in ticks + 2; estimated risk for 1 NQ = (stop ticks + 2) x $5 + $5.74; "
          "above $1,000 the side is NONE (RISK_REJECT, never shrunk).", "",
          "| day | zone | lo | hi | width pts | stop ticks | 1 NQ estimate | sides | pieces at the low / high end (a band, area or REJ zone can reach past the zone edge) | hand | match |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for dy in days:
        lv = level_prices(dy)
        for z in dy["side"]["zones"]:
            if z["stop_ticks"] > 196:
                est = RK.estimate_risk(z["stop_ticks"], 1)
                ext = extents(dy, z)
                lo_n = min(ext, key=lambda e: e[1]) if ext else None; hi_n = max(ext, key=lambda e: e[2]) if ext else None
                L.append(f"| {dy['ds']} | {z['label']} | {z['lo']} | {z['hi']} | {z['hi'] - z['lo']:.2f} | {z['stop_ticks']} | ${est:,.2f} | "
                         f"long={z['long']} short={z['short']} | low end: {lo_n[0]} {lo_n[1]}; high end: {hi_n[0]} {hi_n[2]} (a single price gets the 5-pt pad) | | |")
    # E. DD_EDGE
    L += ["", "## E. DD_EDGE (P0.7, PO-11)", ""]
    for dy in days:
        if dy["side"].get("dd_edge") or (dy["packet"].get("double_distribution") or {}).get("pd_double_distribution"):
            L += dd_table(dy) + [""]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(days)} days, FLIP {nflip}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
