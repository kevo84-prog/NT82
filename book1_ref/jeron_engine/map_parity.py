"""Parity gate 3: map packets built by the harness (JeronPreopenMap v2.3 C#, Databento ticks) vs NinjaTrader's
own packets for the same dates (JE 0.2, Oct 25 2026).

Compared per date:
  levels       every named level: present in both, price within TOL ticks
  zones        same count, and each NT zone matched to a harness zone with lo/hi within TOL ticks, same tier and label
  tests        zones[].tests counts (from/rejected/through below and above, lower highs / higher lows, shrinking time)
  composites   balance_composite (members, overlapping, vah/poc/val), double_distribution, htf_composite vah/poc/val
  areas        single prints / HVN / LVN areas
Skipped: es (no ES data in the harness run), data/built fields, ref_price (first tick after as-of; compared, reported only).
"""
import json, csv
from pathlib import Path

TICK = 0.25
TOL = 1   # ticks


def _near(a, b, tol=TOL):
    try: return abs(float(a) - float(b)) <= tol * TICK + 1e-9
    except (TypeError, ValueError): return a == b


def compare_packets(nt, hx, compare_es=False):
    rows = []
    def add(section, key, ntv, hxv, ok): rows.append(dict(section=section, item=key, nt=ntv, harness=hxv, ok=ok))
    add("ref", "ref_price", nt.get("ref_price"), hx.get("ref_price"), _near(nt.get("ref_price"), hx.get("ref_price"), 4))
    nl = {l["name"]: l for l in nt.get("levels", [])}; hl = {l["name"]: l for l in hx.get("levels", [])}
    for k in sorted(set(nl) | set(hl)):
        a, b = nl.get(k), hl.get(k)
        add("levels", k, a and a["price"], b and b["price"], bool(a and b and _near(a["price"], b["price"])))
    nz, hz = nt.get("zones", []), hx.get("zones", [])
    add("zones", "count", len(nz), len(hz), len(nz) == len(hz))
    used = set()
    for z in nz:
        best = None
        for i, w in enumerate(hz):
            if i in used: continue
            if _near(z["lo"], w["lo"]) and _near(z["hi"], w["hi"]): best = i; break
        if best is None:
            add("zones", f'{z["label"]} {z["lo"]}-{z["hi"]}', z["tier"], "missing", False); continue
        used.add(best); w = hz[best]
        add("zones", f'{z["label"]} {z["lo"]}-{z["hi"]}', f'{z["tier"]} {z["label"]}', f'{w["tier"]} {w["label"]} {w["lo"]}-{w["hi"]}',
            z["tier"] == w["tier"] and z["label"] == w["label"])
        ta, tb = z.get("tests", {}), w.get("tests", {})
        for k in ("from_below", "rejected_from_below", "through_from_below", "from_above", "rejected_from_above",
                  "through_from_above", "lower_highs_into_zone", "higher_lows_into_zone", "shrinking_time"):
            if k in ta or k in tb:
                add("tests", f'{z["label"]}.{k}', ta.get(k), tb.get(k), ta.get(k) == tb.get(k))
    for i, w in enumerate(hz):
        if i not in used: add("zones", f'{w["label"]} {w["lo"]}-{w["hi"]}', "missing", w["tier"], False)
    for sec, keys in (("balance_composite", ("available", "members", "overlapping", "merged_three", "vah", "poc", "val")),
                      ("double_distribution", ("available", "pd_double_distribution", "hvn_blocks")),
                      ("htf_composite", ("days_used", "vah", "poc", "val"))):
        a, b = nt.get(sec, {}) or {}, hx.get(sec, {}) or {}
        for k in keys:
            if k in a or k in b:
                add(sec, k, a.get(k), b.get(k), _near(a.get(k), b.get(k)) if isinstance(a.get(k), (int, float)) and not isinstance(a.get(k), bool) else a.get(k) == b.get(k))
    if compare_es:
        a, b = nt.get("es", {}) or {}, hx.get("es", {}) or {}
        for k in sorted(set(a) | set(b)):
            if isinstance(a.get(k), (int, float)) and not isinstance(a.get(k), bool):
                add("es", k, a.get(k), b.get(k), _near(a.get(k), b.get(k)))
    na = sorted((x["type"], x.get("source"), x["lo"], x["hi"]) for x in nt.get("areas", []))
    ha = sorted((x["type"], x.get("source"), x["lo"], x["hi"]) for x in hx.get("areas", []))
    for x in na:
        m = any(y[0] == x[0] and y[1] == x[1] and _near(y[2], x[2]) and _near(y[3], x[3]) for y in ha)
        add("areas", f"{x[0]} {x[1]} {x[2]}-{x[3]}", "present", "present" if m else "missing", m)
    for y in ha:
        if not any(y[0] == x[0] and y[1] == x[1] and _near(y[2], x[2]) and _near(y[3], x[3]) for x in na):
            add("areas", f"{y[0]} {y[1]} {y[2]}-{y[3]}", "missing", "present", False)
    return rows


def gate3_compare(nt_dir, hx_dir, dates, out_csv=None, compare_es=False):
    allrows, summary = [], []
    for d in dates:
        ntp = next(Path(nt_dir).glob(f"PreopenPacket_*_{d}.json"), None)
        hxp = next(Path(hx_dir).glob(f"PreopenPacket_*_{d}.json"), None)
        if not ntp or not hxp:
            summary.append(f"{d}: missing {'NT' if not ntp else 'harness'} packet"); continue
        rows = compare_packets(json.load(open(ntp)), json.load(open(hxp)), compare_es)
        for r in rows: r["date"] = d
        allrows += rows
        by = {}
        for r in rows:
            s = by.setdefault(r["section"], [0, 0]); s[0] += r["ok"]; s[1] += 1
        summary.append(f"{d}: " + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in by.items()))
    if out_csv and allrows:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["date", "section", "item", "nt", "harness", "ok"]); w.writeheader(); w.writerows(allrows)
    ok = bool(allrows) and all(r["ok"] for r in allrows if r["section"] != "ref")
    return ok, summary, allrows
