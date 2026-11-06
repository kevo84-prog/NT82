"""Parity gate 2: the same strategy code on Databento data vs NinjaTrader's run on NinjaTrader data (JE 0.2, Oct 25 2026).

NT side: a NinjaTrader tracker v2.11 / strategy S1.4 log (JOFT/JOFS csv) that covers the day.
Harness side: JeronHarness on a Databento MBO tape over the same span of days.
Candidates are matched on (signal minute, direction, setup family, zone within 2 points). For matched pairs the
bar evidence is compared: bar volume, buy / sell volume, delta, delta %, status, grade, rejection reasons.

Proposed pass rule (ours, not a Jeron number; Kyron can change it): at least 90% of NT candidates matched,
status agrees on at least 90% of matched pairs, the Qualified lists agree, and no systematic delta bias
(median delta difference within 5% of the median |delta|).
"""
import csv, statistics as st
from collections import Counter

ZONE_TOL = 2.0   # points


def load(path, day, kinds=("CANDIDATE",)):
    out = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for x in csv.DictReader(f):
            if x["RecordType"] in kinds and x.get("EvidenceTimeCT", "").startswith(day):
                out.append(x)
    return out


def _f(x, k):
    try: return float(x.get(k) or "nan")
    except ValueError: return float("nan")


def match(nt, hx):
    by = {}
    for i, h in enumerate(hx):
        by.setdefault((h["EvidenceTimeCT"][:16], h["Direction"], h["SetupFamily"]), []).append(i)
    pairs, used = [], set()
    for n in nt:
        best, bd = None, None
        for i in by.get((n["EvidenceTimeCT"][:16], n["Direction"], n["SetupFamily"]), []):
            if i in used: continue
            d = abs(_f(n, "ZoneLo") - _f(hx[i], "ZoneLo")) + abs(_f(n, "ZoneHi") - _f(hx[i], "ZoneHi"))
            if d <= 2 * ZONE_TOL and (bd is None or d < bd): best, bd = i, d
        if best is not None: used.add(best); pairs.append((n, hx[best]))
    return pairs, [n for n in nt if not any(n is p[0] for p in pairs)], [h for i, h in enumerate(hx) if i not in used]


def gate2(nt_log, hx_log, day, out_csv=None):
    nt, hx = load(nt_log, day), load(hx_log, day)
    pairs, nt_only, hx_only = match(nt, hx)
    res = {"day": day, "nt_candidates": len(nt), "harness_candidates": len(hx), "matched": len(pairs),
           "nt_status": dict(Counter(x["CandidateStatus"] for x in nt)), "harness_status": dict(Counter(x["CandidateStatus"] for x in hx))}
    same_status = sum(a["CandidateStatus"] == b["CandidateStatus"] for a, b in pairs)
    same_grade = sum(a["Grade"] == b["Grade"] for a, b in pairs)
    same_reasons = sum(set(a["Reasons"].split("|")) == set(b["Reasons"].split("|")) for a, b in pairs)
    dd = [_f(b, "Delta") - _f(a, "Delta") for a, b in pairs if _f(a, "Delta") == _f(a, "Delta")]
    dv = [_f(b, "BarVolume") - _f(a, "BarVolume") for a, b in pairs]
    dp = [_f(b, "DeltaPct") - _f(a, "DeltaPct") for a, b in pairs]
    absd = [abs(_f(a, "Delta")) for a, b in pairs]
    res.update(status_agree=same_status, grade_agree=same_grade, reasons_agree=same_reasons,
               delta_diff_median=st.median(dd) if dd else None, delta_diff_mean=round(st.mean(dd), 1) if dd else None,
               delta_absdiff_median=st.median([abs(x) for x in dd]) if dd else None, nt_absdelta_median=st.median(absd) if absd else None,
               barvol_diff_median=st.median(dv) if dv else None, barvol_diff_mean=round(st.mean(dv), 1) if dv else None,
               deltapct_absdiff_median=round(st.median([abs(x) for x in dp]), 2) if dp else None)
    q = lambda xs: sorted((x["EvidenceTimeCT"][11:16], x["Direction"]) for x in xs if x["CandidateStatus"] == "Qualified")
    res["nt_qualified"], res["harness_qualified"] = q(nt), q(hx)
    reasons_nt = Counter(r for x in nt for r in x["Reasons"].split("|") if r)
    reasons_hx = Counter(r for x in hx for r in x["Reasons"].split("|") if r)
    res["reasons"] = {k: (reasons_nt.get(k, 0), reasons_hx.get(k, 0)) for k in sorted(set(reasons_nt) | set(reasons_hx))}
    if out_csv:
        with open(out_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["match", "SignalMinute", "Direction", "Family", "NT_Zone", "HX_Zone", "NT_Status", "HX_Status", "NT_Grade", "HX_Grade",
                        "NT_BarVolume", "HX_BarVolume", "NT_BuyVol", "HX_BuyVol", "NT_SellVol", "HX_SellVol", "NT_Delta", "HX_Delta",
                        "NT_DeltaPct", "HX_DeltaPct", "NT_Reasons", "HX_Reasons"])
            for a, b in pairs:
                w.writerow(["both", a["EvidenceTimeCT"][:16], a["Direction"], a["SetupFamily"], f'{a["ZoneLo"]}-{a["ZoneHi"]}', f'{b["ZoneLo"]}-{b["ZoneHi"]}',
                            a["CandidateStatus"], b["CandidateStatus"], a["Grade"], b["Grade"], a["BarVolume"], b["BarVolume"], a["BuyVol"], b["BuyVol"],
                            a["SellVol"], b["SellVol"], a["Delta"], b["Delta"], a["DeltaPct"], b["DeltaPct"], a["Reasons"], b["Reasons"]])
            for a in nt_only:
                w.writerow(["NT_only", a["EvidenceTimeCT"][:16], a["Direction"], a["SetupFamily"], f'{a["ZoneLo"]}-{a["ZoneHi"]}', "", a["CandidateStatus"], "",
                            a["Grade"], "", a["BarVolume"], "", a["BuyVol"], "", a["SellVol"], "", a["Delta"], "", a["DeltaPct"], "", a["Reasons"], ""])
            for b in hx_only:
                w.writerow(["harness_only", b["EvidenceTimeCT"][:16], b["Direction"], b["SetupFamily"], "", f'{b["ZoneLo"]}-{b["ZoneHi"]}', "", b["CandidateStatus"],
                            "", b["Grade"], "", b["BarVolume"], "", b["BuyVol"], "", b["SellVol"], "", b["Delta"], "", b["DeltaPct"], "", b["Reasons"]])
    m = len(pairs)
    ok = (len(nt) > 0 and m >= 0.9 * len(nt) and same_status >= 0.9 * max(1, m) and res["nt_qualified"] == res["harness_qualified"]
          and (res["delta_diff_median"] is None or abs(res["delta_diff_median"]) <= 0.05 * max(1.0, res["nt_absdelta_median"] or 1.0)))
    return ok, res
