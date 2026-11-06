"""How often the replica GEX levels sit on the plan's zones (research only, JE 0.3, Oct 25 2026).

For each session: each GEX level (call resistance, put support, HVL and the 0DTE three) from the plan's mq_ lines
is classed INSIDE a plan zone, NEAR (within 10 points of a zone edge) or AWAY, with the distance to the nearest
zone. Chance baseline: the share of the price band ref +/- 1 ADR that the zones (+10 pt margin) cover, i.e. how
often a random level in that band would land on or near a zone.
"""
import json, glob, csv
from pathlib import Path

NEAR = 10.0
NAMES = ["mq_call_resistance", "mq_put_support", "mq_hvl", "mq_call_resistance_0dte", "mq_put_support_0dte", "mq_hvl_0dte"]


def plan_zones(text):
    zs = []
    for l in text.splitlines():
        if l.startswith("zone="):
            p = l[5:].split("|"); lo, hi = map(float, p[0].split("-")); zs.append((lo, hi, p[1], p[2]))
    return zs


def run(plan_dir, packet_dir, out_csv):
    rows, cover = [], []
    for f in sorted(Path(plan_dir).glob("PreopenPlan_*.txt")):
        t = f.read_text(); kv = dict(l.split("=", 1) for l in t.splitlines() if "=" in l and not l.startswith(("#", "zone=")))
        d = kv["date"]; zs = plan_zones(t)
        pk = next(Path(packet_dir).glob(f"PreopenPacket_*_{d}.json"), None)
        if not pk: continue
        P = json.load(open(pk)); ref = float(P["ref_price"]); adr = float(P["ranges"]["adr_full"])
        lo, hi = ref - adr, ref + adr
        # chance: fraction of [lo, hi] within NEAR of any zone
        iv = sorted((max(lo, a - NEAR), min(hi, b + NEAR)) for a, b, _, _ in zs if b + NEAR > lo and a - NEAR < hi)
        tot, cur = 0.0, None
        for a, b in iv:
            if cur is None or a > cur[1]:
                if cur: tot += cur[1] - cur[0]
                cur = [a, b]
            else: cur[1] = max(cur[1], b)
        if cur: tot += cur[1] - cur[0]
        cover.append(tot / (hi - lo))
        for n in NAMES:
            if n not in kv: continue
            x = float(kv[n])
            best = min(zs, key=lambda z: 0 if z[0] <= x <= z[1] else min(abs(x - z[0]), abs(x - z[1])))
            dist = 0 if best[0] <= x <= best[1] else min(abs(x - best[0]), abs(x - best[1]))
            cls = "INSIDE" if dist == 0 else ("NEAR" if dist <= NEAR else "AWAY")
            rows.append(dict(date=d, level=n.replace("mq_", ""), price=x, dist_to_ref=round(x - ref, 2), in_1adr=abs(x - ref) <= adr,
                             nearest_zone=best[2], zone_tier=best[3], zone=f"{best[0]}-{best[1]}", distance=round(dist, 2), cls=cls,
                             regime=kv.get("gex_regime", ""), review=kv.get("review", "")))
    if rows:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows, cover
