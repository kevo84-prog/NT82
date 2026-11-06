r"""E23 check: the weekly profile and the ported double-distribution rule, verified against the map's own outputs.

  python -m book1a.hand_checks.weekly_dd_check --out <md> --day <date>=<book1a run dir> [...]

Independent of the plan builder. For each day it rebuilds from the run's map tape (tape_map.csv.gz, the ticks the map
read), with book1a.weekly_dd only:
  1. the developing weekly profile (Sunday 17:00 CT to 08:10 CT): high, low, VWAP, volume POC / VAH / VAL (the map's
     VaFromRows, 1 tick per row, 70%), TPO POC / VAH / VAL (20-tick rows) and the weekly single prints, and compares
     them with the packet's weekly block, WK* / WKT* levels and TPO_WK areas;
  2. the port of the rule: the same functions on the PD cash profile (08:30-15:00 CT; half days skipped) with our own
     PD single prints, compared with the packet's double_distribution and TPO_PD areas;
  3. the weekly double distribution itself (the E23 result), printed for the hand-check pack.
Nothing is tuned: a mismatch is reported, not fitted.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
VERSION = "weekly-dd-check-v1.1"   # v1.1: E26 UNAVAILABLE days shown, map comparison skipped


def va_from_rows(src, row_ticks, pct=70, tick=0.25):
    """JeronPreopenMap.VaFromRows."""
    if not src:
        return None
    mn, mx = min(src), max(src)
    total = sum(src.values())
    if total <= 0:
        return None
    n = mx - mn + 1
    rows = [0] * n
    for k, v in src.items():
        rows[k - mn] += v
    poc, mid = 0, (n - 1) / 2.0
    for i in range(1, n):
        if rows[i] > rows[poc] or (rows[i] == rows[poc] and abs(i - mid) < abs(poc - mid)):
            poc = i
    target = total * max(1, min(100, pct)) / 100.0
    lo = hi = poc
    acc = rows[poc]
    while acc < target and (lo > 0 or hi < n - 1):
        up = rows[hi + 1] if hi + 1 < n else -1
        dn = rows[lo - 1] if lo - 1 >= 0 else -1
        if up >= dn:
            hi += 1; acc += up
        else:
            lo -= 1; acc += dn
    span = (row_ticks - 1) * tick
    val = (mn + lo) * row_ticks * tick
    vah = (mn + hi) * row_ticks * tick + span
    pocp = round(round(((mn + poc) * row_ticks * tick + span / 2.0) / tick) * tick, 2)
    return pocp, round(vah, 2), round(val, 2)


def _rows(tape, start, end):
    import gzip
    with gzip.open(tape, "rt") as f:
        for line in f:
            if line.startswith("time_local"):
                continue
            p = line.rstrip("\n").split(",")
            t = datetime.fromisoformat(p[0][:26]).replace(tzinfo=CT)
            if t < start:
                continue
            if t >= end:
                break
            yield t, float(p[1]), int(p[4])


def check_day(ds: str, run: Path):
    from book1a import sessions as S, vwap as V, weekly_dd as W
    d = date.fromisoformat(ds)
    as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
    hits = sorted((run / "map").glob(f"PreopenPacket_*{ds}.json"))
    if len(hits) != 1:
        raise SystemExit(f"expected one packet for {ds}")
    pk = json.load(open(hits[0]))
    ws = V.week_start(d)
    pd_date = S.sessions(d - timedelta(days=7), d - timedelta(days=1))[-1]
    pd_s, pd_e = datetime.combine(pd_date, time(8, 30), tzinfo=CT), datetime.combine(pd_date, time(15, 0), tzinfo=CT)
    start = min(ws, pd_s)
    rows = list(_rows(run / "tape_map.csv.gz", start, as_of))
    wres, wp, wsp = W.weekly(rows, ws, as_of, packet=pk)
    out = {"day": ds, "weekly_dd": wres, "checks": []}
    if wres.get("status") == "UNAVAILABLE":       # E26: the map left the weekly profile out; nothing to compare
        out["checks"].append(("weekly profile", "UNAVAILABLE", wres["reason"], "SKIP"))
        return out

    def chk(name, ours, map_, tol=0.0):
        ok = (ours is None and map_ is None) or (ours is not None and map_ is not None and abs(float(ours) - float(map_)) <= tol)
        out["checks"].append((name, ours, map_, "OK" if ok else "DIFF"))

    wk = pk.get("weekly") or {}
    lv = {l["name"]: l["price"] for l in pk.get("levels", [])}
    chk("week high", wp.high, wk.get("week_high")); chk("week low", wp.low, wk.get("week_low"))
    chk("weekly VWAP", round(wp.vwap, 4), wk.get("weekly_vwap"), 0.0001)
    v = va_from_rows(dict(wp.vol), 1)
    chk("WKPOC", v[0], lv.get("WKPOC")); chk("WKVAH", v[1], lv.get("WKVAH")); chk("WKVAL", v[2], lv.get("WKVAL"))
    t = va_from_rows(dict(wp.tpo), 20)
    chk("WKTPOC", t[0], lv.get("WKTPOC")); chk("WKTVAH", t[1], lv.get("WKTVAH")); chk("WKTVAL", t[2], lv.get("WKTVAL"))
    map_wsp = [(a["lo"], a["hi"]) for a in pk.get("areas", []) if a.get("source") == "TPO_WK"]
    out["checks"].append(("weekly single prints", [(a["lo"], a["hi"]) for a in wsp], map_wsp,
                          "OK" if [(a["lo"], a["hi"]) for a in wsp] == map_wsp else "DIFF"))
    # port check on the PD cash profile
    if pd_date in S.HALF_DAYS:
        out["checks"].append(("PD double distribution (port check)", "skipped: PD is a half day", "", "SKIP"))
    else:
        pp = W.build_profile(rows, pd_s, pd_e)
        psp = W.single_prints(dict(pp.tpo), "TPO_PD")
        map_psp = [(a["lo"], a["hi"]) for a in pk.get("areas", []) if a.get("source") == "TPO_PD"]
        out["checks"].append(("PD single prints", [(a["lo"], a["hi"]) for a in psp], map_psp,
                              "OK" if [(a["lo"], a["hi"]) for a in psp] == map_psp else "DIFF"))
        pres = W.double_distribution(dict(pp.vol), psp, "PD")
        mdd = pk.get("double_distribution") or {}
        keys = ("lower_hvn", "upper_hvn", "separator", "separator_lo", "separator_hi", "hvn_blocks")
        ours = (bool(pres.get("double_distribution")),) + tuple(pres.get(k) for k in keys)
        theirs = (str(mdd.get("pd_double_distribution")).lower() == "true",) + tuple(mdd.get(k) for k in keys)
        if not ours[0]:
            ours = ours[:1] + (None,) * 5 + (pres.get("hvn_blocks"),)
        out["checks"].append(("PD double distribution (port check)", ours, theirs, "OK" if list(ours) == list(theirs) else "DIFF"))
    out["weekly_profile"] = {"window": [ws.isoformat(), as_of.isoformat()], "trades_volume": wp.total, "last_trade_ct": wres["last_trade_ct"],
                             "rows_5pt": {}}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--day", action="append", required=True, help="<date>=<run dir>")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    res = [check_day(x.split("=", 1)[0], Path(x.split("=", 1)[1])) for x in a.day]
    L = [f"# E23 weekly profile and double-distribution check ({VERSION})", "",
         "Rule: ours: PD rule applied to weekly (book1a.weekly_dd, frozen at commit 31cebdb before any real day was run).",
         "Rebuilt from each run's map tape, compared with the map packet. OK = equal (VWAP within 0.0001).", ""]
    n_ok = sum(1 for r in res for c in r["checks"] if c[3] == "OK")
    n_diff = sum(1 for r in res for c in r["checks"] if c[3] == "DIFF")
    n_skip = sum(1 for r in res for c in r["checks"] if c[3] == "SKIP")
    L += [f"Summary: {n_ok} OK, {n_diff} DIFF, {n_skip} skipped, over {len(res)} days.", "",
          "| day | check | ours | map | status |", "|---|---|---|---|---|"]
    for r in res:
        for c in r["checks"]:
            L.append(f"| {r['day']} | {c[0]} | {c[1]} | {c[2]} | {c[3]} |")
    L += ["", "## Weekly double distribution (E23 result)", "",
          "| day | split | lower HVN | separator | upper HVN | HVN blocks | last trade used |", "|---|---|---|---|---|---|---|"]
    for r in res:
        w = r["weekly_dd"]
        if w.get("status") == "UNAVAILABLE":
            L.append(f"| {r['day']} | UNAVAILABLE ({w['reason']}) | | | | | |")
        elif w.get("double_distribution"):
            L.append(f"| {r['day']} | yes | {w['lower_hvn'][0]} - {w['lower_hvn'][1]} | {w['separator']} {w['separator_lo']} - {w['separator_hi']} | "
                     f"{w['upper_hvn'][0]} - {w['upper_hvn'][1]} | {w['hvn_blocks']} | {w['last_trade_ct']} |")
        else:
            L.append(f"| {r['day']} | no | | | | {w.get('hvn_blocks')} | {w['last_trade_ct']} |")
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    Path(a.out).with_suffix(".json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"{n_ok} OK, {n_diff} DIFF, {n_skip} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
