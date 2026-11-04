r"""P0.7-P0.9 hand-check sheet for 4 days (Kyron, Nov 4, 2026): every value with the source to check it against.

  python -m book1a.hand_checks.hand_check_sheet --block1 K:\Databento_BackTesting --out <md> --day <date>=<run dir>|<plans dir> [...]

Kyron, Nov 4: Oct 22, 29, 31 and Nov 18 only. For each value the sheet names where to check it:
  - volume-profile values (POC / VAH / VAL, TPO values, highs / lows, HVN / POC areas, delta bands, the double
    distribution blocks): the NinjaTrader Volume Profile tool drawn over the stated window (CT; 5-point rows where the
    rule uses rows; TPO values with the profile in TPO / 30-minute mode);
  - GEX values: `gex_levels_block1.csv`, row session = the day, the named column (the plan reads the `_nt` column,
    which is the level shifted to the NinjaTrader contract, when it is filled);
  - 08:10 values (session and weekly VWAP and +/-1 sigma, the 08:10 price, context, draw, acceptance states, value
    follows, overnight inventory, weekly DD status): the frozen plan sidecar `PreopenPlan_<day>_book1a.json`, the
    named key.
No trades, outcomes or P&L. The hand and match columns are left empty.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

VERSION = "hand-check-sheet-v1.0"
GEX_COLS = {"CR": "call_resistance", "PS": "put_support", "HVL": "hvl", "CR_0DTE": "call_resistance_0dte",
            "PS_0DTE": "put_support_0dte", "HVL_0DTE": "hvl_0dte"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--day", action="append", required=True, help="<date>=<run dir>|<plans dir>")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from book1a import families as F, vwap as V
    from book1a.hand_checks.hand_check_pack import hm, level_source, prior_sessions
    gex = {r["session"]: r for r in csv.DictReader(open(Path(a.block1) / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    L = [f"# P0.7-P0.9 hand-check sheet: Oct 22, 29, 31 and Nov 18, 2025 ({VERSION})", "",
         "Check each value against the source named on its row, not against the plan. Sources: **NT VP** = the NinjaTrader "
         "Volume Profile tool drawn over the stated window (CT); **GEX csv** = `gex_levels_block1.csv`, row session = the day, "
         "the named column; **sidecar** = the frozen plan sidecar `PreopenPlan_<day>_book1a.json`, the named key. "
         "Every value is frozen at 08:10 CT from data before 08:10 CT. No trades, outcomes or P&L.", ""]
    for spec in a.day:
        ds, rest = spec.split("=", 1)
        run, plans = (Path(x) for x in rest.split("|"))
        d = date.fromisoformat(ds)
        pk = json.load(open(sorted((run / "map").glob(f"PreopenPacket_*{ds}.json"))[0]))
        side_file = plans / f"PreopenPlan_{ds}_book1a.json"
        sc = json.load(open(side_file))
        g = gex.get(ds) or {}
        lv = {l["name"]: float(l["price"]) for l in pk.get("levels", []) if l.get("price") is not None}
        bands = {b["label"]: b for b in sc.get("delta_bands", [])}
        areas = {x["label"]: x for x in sc.get("map4_areas", [])}
        vw = sc.get("vwap") or {}
        sname = side_file.name

        def src(name):
            n = name.upper()
            if n in GEX_COLS or n.startswith("GAMMA"):
                col = GEX_COLS.get(n, name.lower())
                used = col + "_nt" if g.get(col + "_nt") not in (None, "") else col
                return "GEX", f"GEX csv: row {ds}, column `{used}` (= {g.get(used)}); CME report {g.get('report_date')} (D-1)"
            for nm, k in (("WKVWAP", "WEEKLY"), ("VWAP", "SESSION")):
                if n.startswith(nm):
                    key = "vwap" if n == nm else ("sd1_up" if n.endswith("UP") or n.endswith("U1") else "sd1_dn")
                    return "08:10", f"sidecar `vwap.{k}.{key}` (= {round(vw.get(k, {}).get(key, float('nan')), 2)}; window {vw.get(k, {}).get('window_start_ct', '')[:16]} - 08:10)"
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
              "### 08:10 values (source: sidecar)", "", "| value | plan / sidecar value | check against | hand | match |", "|---|---|---|---|---|"]
        kv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in sc["plan"] if "=" in l and not l.startswith("#")}
        L.append(f"| price at 08:10 (packet ref_price) | {pk.get('ref_price')} | the 08:10 bar close on the chart; sidecar has it in the zone sides | | |")
        for k in ("SESSION", "WEEKLY"):
            v = vw.get(k) or {}
            for key in ("vwap", "sd1_up", "sd1_dn"):
                if key in v:
                    L.append(f"| {k.lower()} {key} | {v[key]:.2f} | sidecar `vwap.{k}.{key}` (window {v.get('window_start_ct', '')[:16]} - 08:10) | | |")
        for k in ("market_context", "draw_status", "draw", "balance", "balance_poc", "value_follows", "on_inventory", "on_vs_settle",
                  "htf_structure", "gex_regime", "wkval_state", "wkvah_state"):
            if k in kv:
                L.append(f"| {k} | {kv[k]} | sidecar `plan` line `{k}=` | | |")
        w = sc.get("weekly_dd") or {}
        L.append(f"| weekly double distribution | {w.get('status')}; split {'yes' if w.get('double_distribution') else 'no'} | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |")
        L += ["", "### GEX values (source: GEX csv)", "", "| level | value in plan | check against | hand | match |", "|---|---|---|---|---|"]
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
                    if px is None and kind == "08:10":
                        k = "WEEKLY" if name.upper().startswith("WKVWAP") else "SESSION"
                        key = "vwap" if name.upper() in ("VWAP", "WKVWAP") else ("sd1_up" if name.upper().endswith(("UP", "U1")) else "sd1_dn")
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
                             f"distribution (two HVN blocks >= 70% of the smoothed peak, separator {dd.get('separator_lo')} - {dd.get('separator_hi')}) | | |")
            for r in sc.get("rej_flip_zones", []):
                if f"{r['kind']}_{r['session']}" in z["label"] and r["lo"] <= z["hi"] and r["hi"] >= z["lo"]:
                    L.append(f"| {r['kind']}_{r['session']} | STRUCTURE / chart | {r['lo']} - {r['hi']} | overlaps | 1-minute chart: swing bar close "
                             f"{hm(datetime.fromisoformat(r['formed_ct']))}, swing {r.get('swing_price')}; available {hm(datetime.fromisoformat(r['confirmed_ct'])) if r.get('confirmed_ct') else ''} (pack section B) | | |")
            L.append("")
        if w.get("double_distribution"):
            L += [f"### Weekly double distribution (ours: PD rule applied to weekly)", "",
                  f"NT VP over the developing week {hm(V.week_start(d))} - 08:10 CT, 5-pt rows: lower HVN {w['lower_hvn'][0]} - {w['lower_hvn'][1]}; "
                  f"separator ({w['separator']}) {w['separator_lo']} - {w['separator_hi']}; upper HVN {w['upper_hvn'][0]} - {w['upper_hvn'][1]}. "
                  "Row by row values: hand-check pack section E2.", ""]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
