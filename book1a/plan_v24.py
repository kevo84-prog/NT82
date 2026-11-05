"""Book 1A plan builder (map v2.4 outputs + Context + zone selection + zone review + ladder; checklist P0.7-P0.9).

Wraps the frozen Book 1 pieces: the v2.3 packet is read as written by JeronPreopenMap v2.3 (never changed), and
the plan text keeps the Book 1 key=value format that JeronOrderFlowStrategy S1.4 reads (zone=, context=, balance=,
invalidate_*, review=, end=1). Book 1A fields are extra keys S1.4 logs and ignores. No lava= line is written
(Book 1A removed the lava band). Check B (zone coverage) and check F (day suitability) are logged, never applied
(Phase 4 doc). The 1-ADR filter and the 60-point cut are logged as research (Phase 3 doc).

Every zone written carries available_at (= the as-of time) in the sidecar JSON.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Sequence
from zoneinfo import ZoneInfo

from book1a import families as F, map_v24 as M, plan_fields as PF, risk as R
from book1a.map_v24 import Bar, Zone

VERSION = "plan-v2.4-book1a-v1.4"   # v1.4: htf_acceptance (PO-9 at HTF VAH/VAL) + context precedence (Nov 5, 2026)
                                    # v1.1: DD_EDGE reads the v2.3 packet form (E21)
                                    # v1.2: weekly DD_EDGE (E23, ours: PD rule applied to weekly, book1a.weekly_dd)
                                    # v1.3: weekly DD UNAVAILABLE noted (E26); FLIP review flag (E25)
CT = ZoneInfo("America/Chicago")
TICK = 0.25
PAD = 5.0
KEEP_PER_SIDE = 2


def _r(x: float) -> float:
    return round(round(x / TICK) * TICK, 2)


def _lv(p: dict) -> Dict[str, float]:
    return {l["name"]: float(l["price"]) for l in p.get("levels", []) if l.get("price") is not None}


def _find(lv: Dict[str, float], *parts: str) -> Optional[float]:
    for k, v in lv.items():
        if all(s in k.upper() for s in parts):
            return v
    return None


def _ctx_label(c: str) -> str:
    return {"BULLISH": "Bullish", "BEARISH": "Bearish", "BALANCED": "Balanced"}.get(c, "None")


def acceptance_evidence(used: Sequence[Bar], st, as_of) -> dict:
    """Hand-check evidence for one PO-9 state (not written to the plan): the first 1-minute close beyond the edge in
    the current excursion, the minutes, close share and volume share since it, and the bars window."""
    out = dict(name=st.level_name, level=st.level, state=st.state, minutes=st.minutes_since_first_close,
               close_share=st.close_share, volume_share=st.volume_share, first_close_ct=None, first_close=None,
               excursion_starts_at_window_start=False, n_bars_since=None,
               window_from=used[0].close_ct.isoformat() if used else None, window_to=used[-1].close_ct.isoformat() if used else None,
               as_of=as_of.isoformat())
    if st.minutes_since_first_close is None:
        return out
    beyond = (lambda b: b.close < st.level) if st.level_name.endswith("VAL") else (lambda b: b.close > st.level)
    first = None
    for k in range(len(used) - 1, -1, -1):
        if beyond(used[k]):
            first = k
        else:
            break
    if first is not None:
        out.update(first_close_ct=used[first].close_ct.isoformat(), first_close=used[first].close,
                   excursion_starts_at_window_start=(first == 0), n_bars_since=len(used) - first)
    return out


def dd_inputs(ddp) -> Optional[tuple]:
    """(dist_a, separator, dist_b, profile) from the packet's double_distribution, or None.
    JeronPreopenMap v2.3 writes the PD cash profile's split as pd_double_distribution=true with lower_hvn=[lo,hi],
    upper_hvn=[lo,hi], separator_lo, separator_hi (E21: v1.0 looked only for dist_a / separator / dist_b, which
    the packet never writes, so DD_EDGE never formed). The generic dist_a / separator / dist_b form is still read."""
    if not isinstance(ddp, dict):
        return None
    if all(k in ddp for k in ("dist_a", "separator", "dist_b")) and isinstance(ddp["separator"], (list, tuple)):
        return tuple(ddp["dist_a"]), tuple(ddp["separator"]), tuple(ddp["dist_b"]), ddp.get("profile", "WK")
    if str(ddp.get("pd_double_distribution")).lower() == "true" and all(k in ddp for k in ("lower_hvn", "upper_hvn", "separator_lo", "separator_hi")):
        lo_d, up_d = ddp["lower_hvn"], ddp["upper_hvn"]
        return ((float(lo_d[0]), float(lo_d[1])), (float(ddp["separator_lo"]), float(ddp["separator_hi"])),
                (float(up_d[0]), float(up_d[1])), "PD")
    return None


def build(p: dict, bars: Sequence[Bar], profiles: Dict[str, dict], vwap_res: dict, gex_row: Optional[dict],
          calendar_rows: Sequence[dict], roll_dates: Sequence[str] = (), as_of: Optional[datetime] = None,
          weekly_dd: Optional[dict] = None, evidence: Optional[dict] = None):
    """Returns (plan_text, sidecar dict). profiles: {"WK"|"PD"|"ON": {"volume": {row: v}, "delta": {row: d}, "poc_row": r}}.
    weekly_dd: book1a.weekly_dd.weekly() result (E23); None = no weekly DD input (logged in the sidecar).
    evidence: optional dict filled with the input numbers behind the context fields (for the hand-check sheet only;
    never written to the plan text or the sidecar, so plan and sidecar hashes do not depend on it)."""
    d = date.fromisoformat(p["date"])
    as_of = as_of or datetime.combine(d, time(8, 10), tzinfo=CT)
    ref = float(p["ref_price"])
    adr = float((p.get("ranges") or {}).get("adr_full") or 0) or 400.0
    lv = _lv(p)
    notes: List[str] = []
    fails: List[str] = []
    research: Dict[str, object] = {}

    # ---- VWAP (PO-8) ----------------------------------------------------------------------------
    sv, wv = vwap_res.get("SESSION"), vwap_res.get("WEEKLY")
    vwap_levels = []
    for name, res in (("VWAP", sv), ("WKVWAP", wv)):
        if res is not None and res.vwap is not None:
            vwap_levels.append(F.Level.point(name, res.vwap, available_at=as_of.isoformat()))
            vwap_levels.append(F.Level.point(name + "_SD1_UP", res.upper, available_at=as_of.isoformat()))
            vwap_levels.append(F.Level.point(name + "_SD1_DN", res.lower, available_at=as_of.isoformat()))
    session_vwap = sv.vwap if sv is not None else None

    # ---- GEX levels (one family) ----------------------------------------------------------------
    gex_levels, gex_regime = [], "UNKNOWN"
    if gex_row and str(gex_row.get("ok")) == "True":
        gex_regime = "POS" if gex_row.get("regime") == "positive" else ("NEG" if gex_row.get("regime") == "negative" else "UNKNOWN")
        for k, name in (("call_resistance", "CR"), ("put_support", "PS"), ("hvl", "HVL"), ("call_resistance_0dte", "CR_0DTE"),
                        ("put_support_0dte", "PS_0DTE"), ("hvl_0dte", "HVL_0DTE")):
            v = gex_row.get(k + "_nt") or gex_row.get(k)
            if v not in (None, ""):
                gex_levels.append(F.Level.point(name, float(v), family="GEX", available_at=PF.gex_available_at(d).isoformat()
                                                if hasattr(PF, "gex_available_at") else None))
        for k in sorted(gex_row):
            if k.startswith("gamma") and gex_row[k] not in (None, ""):   # P1.1 gamma ranks, if present
                gex_levels.append(F.Level.point(k.upper(), float(gex_row[k]), family="GEX"))

    # ---- map v2.4 zones (PO-1, PO-6, PO-7, PO-11) -------------------------------------------------
    bands: List[Zone] = []
    for prof in ("WK", "PD", "ON"):
        pr = profiles.get(prof)
        if pr and pr.get("delta"):
            bands += M.delta_bands(pr["delta"], as_of, prof, price=ref)
    rej = M.rejection_zones(bars, d, as_of, adr)
    rej = M.merge_same_side(rej)
    rej = M.flips(bars, rej, as_of)
    if any(z.kind == "FLIP" for z in rej):     # E25 (Kyron, Nov 4): the first real FLIP gets a mandatory targeted review
        research["flip_review_required"] = [f"{z.lo}-{z.hi}" for z in rej if z.kind == "FLIP"]
        notes.append("E25: FLIP zone formed - mandatory targeted review (FLIP is covered by a synthetic test only)")
    stack_levels = {k: v for k, v in lv.items() if F.family_of(k) in ("AUCTION_VALUE", "VOLUME")}
    M.tag_zones(rej, session_vwap, bands, stack_levels)
    rej_sel = M.select_zones(rej, ref, adr, bars, as_of)
    research["rej_zones_before_selection"] = len(rej)
    areas: List[Zone] = []
    for prof in ("WK", "PD", "ON"):
        pr = profiles.get(prof)
        if pr and pr.get("volume") and pr.get("poc_row") is not None:
            areas.append(M.map4_area(pr["volume"], pr["poc_row"], as_of, f"{prof}POC_AREA"))
    dd = None
    ddi = dd_inputs(p.get("double_distribution"))
    if ddi is not None:
        dd = M.dd_edge_zone(ddi[0], ddi[1], ddi[2], ref, as_of, ddi[3])
    # E23 (Kyron, Nov 4; ours: PD rule applied to weekly): the same split on the developing weekly profile
    from book1a import weekly_dd as WD
    dd_wk = None
    wdi = WD.as_plan_inputs(weekly_dd) if weekly_dd else None
    if wdi is not None:
        dd_wk = M.dd_edge_zone(wdi[0], wdi[1], wdi[2], ref, as_of, "WK")
        if dd_wk is not None:
            dd_wk.extra["rule"] = WD.LABEL
    if weekly_dd and weekly_dd.get("status") == "UNAVAILABLE":
        notes.append(f"E26: weekly double distribution UNAVAILABLE ({weekly_dd.get('reason')})")
    dds = [z for z in (dd, dd_wk) if z is not None]      # PD first, then weekly (ladder RUNNER order)

    # ---- candidate decision zones: packet zones + REJ/FLIP + MAP4 areas + DD edges -------------------
    all_levels = [F.Level.point(k, v) for k, v in lv.items()] + vwap_levels + gex_levels + \
                 [F.Level(b.label, b.lo, b.hi, family="DELTA") for b in bands] + \
                 [F.Level(a.label, a.lo, a.hi, family="VOLUME") for a in areas]
    cands = []
    for z in p.get("zones", []):
        lo, hi = float(z["lo"]), float(z["hi"])
        own = []
        cands.append(dict(lo=lo, hi=hi, label=z["label"], kind="PACKET", own=own, src=z, tests=z.get("tests") or {}))
    for z in rej_sel:
        cands.append(dict(lo=z.lo, hi=z.hi, label=f"{z.kind}_{z.session}", kind=z.kind, own=["STRUCTURE"], src=None, tests={}, zone=z))
    for a in areas:
        cands.append(dict(lo=a.lo, hi=a.hi, label=a.label, kind="MAP4_AREA", own=["VOLUME"], src=None, tests={}, zone=a))
    for z in dds:   # both DD edges belong to STRUCTURE; a merged zone counts the family once (own is a set)
        cands.append(dict(lo=z.lo, hi=z.hi, label=z.label, kind="DD_EDGE", own=["STRUCTURE"], src=None, tests={}, zone=z))
    for c in cands:
        fr = F.count_families(c["lo"], c["hi"], all_levels, own_families=c["own"])
        c["fam"] = fr
        c["class"] = fr.zone_class
    # balanced days: the balance POC is a target only, never a decision zone
    bc = p.get("balance_composite") or {}
    bal_poc = bc.get("poc")
    for c in cands:
        if bc.get("overlapping") and bal_poc is not None and c["lo"] <= bal_poc <= c["hi"] and "POC" in c["label"].upper():
            if c["class"] == "DECISION":
                c["class"] = "TARGET"; notes.append(f"Z3: {c['label']} at the balance POC: TARGET only")
    dec = [c for c in cands if c["class"] == "DECISION"]
    dec.sort(key=lambda c: c["lo"])
    merged = []
    for c in dec:                       # touching neighbours merge
        if merged and c["lo"] <= merged[-1]["hi"]:
            m = merged[-1]
            m["hi"] = max(m["hi"], c["hi"]); m["label"] = (m["label"] + "_" + c["label"])[:60]
            m["fam"] = F.count_families(m["lo"], m["hi"], all_levels, own_families=sorted(set(m["own"] + c["own"])))
            m["own"] = sorted(set(m["own"] + c["own"])); m["tests"] = m["tests"] or c["tests"]
            m["kinds"] = m.get("kinds", [m["kind"]]) + [c["kind"]]
        else:
            c = dict(c); c["kinds"] = [c["kind"]]; merged.append(c)
    for c in merged:
        c["side"] = "ABOVE" if c["lo"] > ref else ("BELOW" if c["hi"] < ref else "AT")
        c["dist"] = 0.0 if c["side"] == "AT" else (c["lo"] - ref if c["side"] == "ABOVE" else ref - c["hi"])
    research["would_drop_1adr"] = [c["label"] for c in merged if c["dist"] > adr]
    research["would_cut_60pt"] = [c["label"] for c in merged if c["hi"] - c["lo"] > 60.0]
    above = sorted([c for c in merged if c["side"] == "ABOVE"], key=lambda c: c["dist"])[:KEEP_PER_SIDE]
    below = sorted([c for c in merged if c["side"] == "BELOW"], key=lambda c: c["dist"])[:KEEP_PER_SIDE]
    at = [c for c in merged if c["side"] == "AT"]
    chosen = sorted(above + below + at, key=lambda c: c["lo"])
    research["decision_zones_beyond_cap"] = [c["label"] for c in merged if c not in chosen]
    targets = [c for c in cands if c["class"] == "TARGET"] + [dict(lo=b.lo, hi=b.hi, label=b.label, kind="DELTA_BAND") for b in bands
                                                                 if b.extra.get("role") == "TARGET"]

    # ---- context (Phase 2) ------------------------------------------------------------------------
    htf_val, htf_vah, htf_poc = _find(lv, "HTF", "VAL"), _find(lv, "HTF", "VAH"), _find(lv, "HTF", "POC")
    wk_val, wk_vah = _find(lv, "WKVAL") or _find(lv, "WK", "VAL"), _find(lv, "WKVAH") or _find(lv, "WK", "VAH")
    used = [b for b in bars if b.close_ct <= as_of]
    lo_w = min((b.low for b in used), default=ref); hi_w = max((b.high for b in used), default=ref)
    wk_val_state = M.acceptance_state(used, "VAL", wk_val, wk_vah, ref, as_of, "WKVAL") if wk_val and wk_vah else None
    wk_vah_state = M.acceptance_state(used, "VAH", wk_vah, wk_val, ref, as_of, "WKVAH") if wk_val and wk_vah else None
    ci = PF.ContextInputs(price=ref, htf_val=htf_val if htf_val is not None else -1e9, htf_vah=htf_vah if htf_vah is not None else 1e9,
                          held_or_reclaimed_val=(htf_val is not None and ref >= htf_val and lo_w <= htf_val),
                          failed_or_lost_vah=(htf_vah is not None and ref <= htf_vah and hi_w >= htf_vah),
                          wk_val_state=wk_val_state.state if wk_val_state else "INSIDE",
                          wk_vah_state=wk_vah_state.state if wk_vah_state else "INSIDE",
                          balance_overlapping=bool(bc.get("overlapping")), balance_lo=bc.get("val"), balance_hi=bc.get("vah"), balance_poc=bal_poc)
    # Nov 5, 2026 (pre-freeze specification change, Kyron): PO-9 acceptance, unchanged, at the HTF composite VAH and
    # VAL, bars closed at or before 08:10 only. PF.HTF_ACCEPTANCE_LABEL. Context evidence only.
    htf_ok = htf_val is not None and htf_vah is not None
    htf_val_state = M.acceptance_state(used, "VAL", htf_val, htf_vah, ref, as_of, "HTFVAL") if htf_ok else None
    htf_vah_state = M.acceptance_state(used, "VAH", htf_vah, htf_val, ref, as_of, "HTFVAH") if htf_ok else None
    htf_acc = PF.htf_acceptance_from_states(htf_val_state.state if htf_val_state else None,
                                            htf_vah_state.state if htf_vah_state else None)
    ctx_base = PF.context_base(ci) if htf_ok else "NONE_NO_EVIDENCE"
    mctx = PF.apply_htf_acceptance(ctx_base, htf_acc)
    if htf_val is None or htf_vah is None:
        notes.append("context: HTF composite value missing from the packet levels -> NONE")
    # draw: next HTF level in the context direction
    draw_cands = []
    if mctx == "BULLISH":
        for name, px in (("HTFPOC", htf_poc), ("HTFVAH", htf_vah)):
            if px is not None and px > ref: draw_cands.append((px - ref, name, px - PAD, px + PAD))
        for a in areas:
            if a.lo > ref: draw_cands.append((a.lo - ref, a.label, a.lo, a.hi))
        for g in gex_levels:
            if g.lo > ref: draw_cands.append((g.lo - ref, g.name, g.lo - PAD, g.hi + PAD))
    elif mctx == "BEARISH":
        for name, px in (("HTFPOC", htf_poc), ("HTFVAL", htf_val)):
            if px is not None and px < ref: draw_cands.append((ref - px, name, px - PAD, px + PAD))
        for a in areas:
            if a.hi < ref: draw_cands.append((ref - a.hi, a.label, a.lo, a.hi))
        for g in gex_levels:
            if g.hi < ref: draw_cands.append((ref - g.hi, g.name, g.lo - PAD, g.hi + PAD))
    draw = None
    if draw_cands:
        _, nm, dlo, dhi = min(draw_cands)
        draw = PF.DrawState(_r(dlo), _r(dhi)); draw_name = nm
    inv = PF.invalidation(mctx, wk_val if wk_val is not None else -1e9, wk_vah if wk_vah is not None else 1e9,
                          htf_val if htf_val is not None else -1e9, htf_vah if htf_vah is not None else 1e9)
    ps = {s.get("slot"): s for s in p.get("prior_sessions", [])}
    pd1, pd2 = ps.get("PD") or {}, ps.get("PD2") or {}
    vf = "WITH_PRICE"
    if all(pd1.get(k) is not None and pd2.get(k) is not None for k in ("day_high", "day_low", "vah", "val", "poc")):
        vf = PF.value_follows(pd1["day_high"], pd2["day_high"], pd1["day_low"], pd2["day_low"], pd1["vah"], pd2["vah"],
                              pd1["val"], pd2["val"], pd1["poc"], pd2["poc"])
    on = p.get("overnight") or {}
    settle = _find(lv, "SETTLE") or pd1.get("settle")
    on_inv = PF.on_inventory(on.get("vwap") or on.get("poc") or ref, settle if settle is not None else ref, ref)
    h1 = (p.get("structure") or {})
    hst = PF.htf_structure(h1.get("swing_highs") or [], h1.get("swing_lows") or [])
    if evidence is not None:
        evidence.update(
            price=ref, htf_val=htf_val, htf_vah=htf_vah, htf_poc=htf_poc, bars_low=lo_w, bars_high=hi_w,
            bars_from=used[0].close_ct.isoformat() if used else None, bars_to=used[-1].close_ct.isoformat() if used else None,
            held_or_reclaimed_val=ci.held_or_reclaimed_val, failed_or_lost_vah=ci.failed_or_lost_vah,
            wk_val=wk_val, wk_vah=wk_vah, wk_val_state=ci.wk_val_state, wk_vah_state=ci.wk_vah_state,
            balance_composite=bc, market_context=mctx,
            draw_candidates=[dict(dist=_r(c[0]), name=c[1], lo=_r(c[2]), hi=_r(c[3])) for c in sorted(draw_cands)],
            draw_status=draw.status if draw else "NONE", pd=dict(pd1), pd2=dict(pd2), value_follows=vf,
            overnight=dict(on), settle=settle, on_inventory=on_inv,
            context_base=ctx_base, htf_acceptance=htf_acc,
            htf_accept=[acceptance_evidence(used, st, as_of) for st in (htf_val_state, htf_vah_state) if st is not None])

    # ---- sides, check C, ladder per decision zone --------------------------------------------------
    zone_rows = []
    for c in chosen:
        z_above = c["lo"] > ref
        t = c["tests"] or {}
        ntests = (t.get("from_below") or 0) + (t.get("from_above") or 0)
        is_val_edge = any(k.endswith("VAL") for k in c["fam"].levels) or "VAL" in c["label"].upper()
        is_vah_edge = any(k.endswith("VAH") for k in c["fam"].levels) or "VAH" in c["label"].upper()
        acc = None
        if is_val_edge and wk_val_state and wk_val is not None and c["lo"] - PAD <= wk_val <= c["hi"] + PAD: acc = wk_val_state.state
        if is_vah_edge and wk_vah_state and wk_vah is not None and c["lo"] - PAD <= wk_vah <= c["hi"] + PAD: acc = wk_vah_state.state
        edge_bands = [b.extra["sign"] for b in bands if b.hi >= c["lo"] and b.lo <= c["hi"]]
        ec = PF.edge_control(edge_bands) if edge_bands and (is_val_edge or is_vah_edge) else None
        kind = "FLIP" if "FLIP" in c.get("kinds", []) else ("REJ_HIGH" if "REJ_HIGH" in c.get("kinds", []) else
                ("REJ_LOW" if "REJ_LOW" in c.get("kinds", []) else ("DD_EDGE" if "DD_EDGE" in c.get("kinds", []) else "VALUE_EDGE")))
        zs = PF.ZoneForSides(c["label"], c["lo"], c["hi"], z_above, kind=kind, tests=ntests,
                             lower_highs_into_zone=bool(t.get("lower_highs_into_zone")), higher_lows_into_zone=bool(t.get("higher_lows_into_zone")),
                             accept_state=acc, edge_control=ec, dd_far_side_is_long=(z_above if kind == "DD_EDGE" else None),
                             value_follows=vf, is_highs_edge=any(k in ("PDH", "PD2H", "WKH") for k in c["fam"].levels),
                             is_lows_edge=any(k in ("PDL", "PD2L", "WKL") for k in c["fam"].levels), gex_regime=gex_regime)
        fields = PF.zone_fields(zs, mctx)
        # check C (Phase 4): zone stop = width + 2 ticks; R at TP1/TP2/RUN logged; side NONE only if 1 NQ cannot fit
        stop_ticks = int(round((c["hi"] - c["lo"]) / TICK)) + 2
        fits = R.size_for(stop_ticks, R.DEFAULT.per_trade_budget_cents) >= 1
        ladder = {}
        for side in ("long", "short"):
            if fields[side] == "NONE":
                continue
            if not fits:
                fields[side] = "NONE"; notes.append(f"C: {c['label']} {side} NONE: 1 NQ does not fit ${R.DEFAULT.per_trade_budget_cents/100:.0f} (stop {stop_ticks} ticks)")
                continue
            ladder[side] = _ladder(side, c, ref, rej_sel, lv, areas, bands, wk_val, wk_vah, pd1, draw, dds, stop_ticks)
        c.update(fields); c["ladder"] = ladder; c["stop_ticks"] = stop_ticks; c["accept_state"] = acc
        zone_rows.append(c)
    if any(zr["side"] == "ABOVE" for zr in zone_rows) and any(zr["side"] == "BELOW" for zr in zone_rows):
        research["check_b"] = "pass"
    else:
        research["check_b"] = "would fail: no decision zone on each side (logged only)"

    # ---- check A (data), check E, check F (logged) ---------------------------------------------------
    data = p.get("data") or {}
    asof_dt = datetime.combine(d, time(8, 10))
    recent = [g for g in data.get("gaps", []) if datetime.strptime(g["to"][:16], "%Y-%m-%d %H:%M") > asof_dt - timedelta(hours=24)]
    if recent: fails.append("A: data gap in the last 24 h")
    if not pd1.get("covered", True): fails.append("A: PD profile missing")
    if on.get("vah") is None: fails.append("A: overnight profile missing")
    if (p.get("weekly") or {}).get("vah") is None: fails.append("A: weekly profile missing")
    cal = p.get("calendar") or {}
    if cal.get("half_day_today"): fails.append("A: half day")
    if p["date"] in roll_dates: fails.append("A: roll day")
    f_log = []
    for row in calendar_rows:
        if row.get("date") != p["date"] or row.get("status") == "CANCELED": continue
        if row.get("category") in ("HOLIDAY", "CLOSED"): fails.append(f"A: {row['category'].lower()} ({row.get('event', '')})")
        if row.get("no_trade_ct"): f_log.append(f"no_trade={row['no_trade_ct']}")
        if (row.get("action") or "").startswith("max_trades="): f_log.append("max_trades=1")
    research["check_f_would_set"] = f_log
    # check E: sides agree with the context and the invalidation sits beyond the zone it protects
    e_ok = True
    if mctx == "BULLISH" and inv["invalidate_below"] is not None:
        e_ok = all(not (zr["side"] == "BELOW" and zr["long"] == "ANY" and zr["lo"] < inv["invalidate_below"] - 2 * TICK) for zr in zone_rows)
    review = "APPROVED" if not fails and e_ok else "LOG_ONLY"
    if not e_ok: notes.append("E: a with-context zone lies beyond the invalidation edge")

    # ---- write (Book 1 keys first, Book 1A keys after) ------------------------------------------------
    L = ["# JeronPreopenPlan v1.5 (Book 1A plan builder, map v2.4 outputs; book1a.plan_v24 " + VERSION + ")",
         f"plan_id={p['date']}-b1a", f"date={p['date']}", "asof=08:25", f"packet_asof={p.get('asof_ct', '')}",
         f"context={_ctx_label(mctx)}", f"context_note=Book 1A context rule; htf_val={htf_val} htf_vah={htf_vah} wk_val_state={ci.wk_val_state} wk_vah_state={ci.wk_vah_state}"]
    for zr in zone_rows:
        L.append(f"zone={zr['lo']:.2f}-{zr['hi']:.2f}|{zr['label'][:60]}|DECISION|long={zr['long']}|short={zr['short']}|alt_long=ANY|alt_short=ANY|confidence=med|note=book1a")
    for tz in sorted(targets, key=lambda x: x["lo"]):
        lab = tz["label"] if tz["label"].startswith("T_") else "T_" + tz["label"]
        L.append(f"zone={tz['lo']:.2f}-{tz['hi']:.2f}|{lab[:60]}|TARGET")
    bf = PF.balance_fields(ci)
    if bf["balance"]: L.append(f"balance={bf['balance']}"); L.append(f"balance_poc={bf['balance_poc']}")
    if mctx in ("BULLISH", "BEARISH"):
        if inv["invalidate_above"] is not None: L.append(f"invalidate_above={_r(inv['invalidate_above'] + 2 * TICK):.2f}|Balanced")
        if inv["invalidate_below"] is not None: L.append(f"invalidate_below={_r(inv['invalidate_below'] - 2 * TICK):.2f}|Balanced")
    L += ["macro=not verified (backtest)", "news=not used (backtest)",
          "# --- Book 1A fields (logged by S1.4, not read) ---",
          f"market_context={mctx}", f"draw_status={draw.status if draw else 'NONE'}",
          f"context_base={ctx_base}", f"htf_acceptance={htf_acc}", "# htf_acceptance: " + PF.HTF_ACCEPTANCE_LABEL]
    if htf_val_state: L.append(f"htfval_state={htf_val_state.tag()}")
    if htf_vah_state: L.append(f"htfvah_state={htf_vah_state.tag()}")
    if draw: L.append(f"draw={draw.draw_lo:.2f}-{draw.draw_hi:.2f}|{draw_name}")
    L += [f"value_follows={vf}", f"on_inventory={on_inv['on_inventory']}", f"on_vs_settle={on_inv['on_vs_settle']}",
          f"htf_structure={hst}", f"gex_regime={gex_regime}",
          f"vwap_0810={'' if session_vwap is None else f'{session_vwap:.2f}'}", f"wkvwap_0810={'' if wv is None or wv.vwap is None else f'{wv.vwap:.2f}'}",
          f"vwap_vs_price={'' if session_vwap is None else f'{ref - session_vwap:.2f}'}"]
    if wk_val_state: L.append(f"wkval_state={wk_val_state.tag()}")
    if wk_vah_state: L.append(f"wkvah_state={wk_vah_state.tag()}")
    for zr in zone_rows:
        L.append(f"zone_meta={zr['label'][:60]}|{zr['fam'].families_field()}|{zr['fam'].levels_field()}|first_touch=YES|tests={zr['tests'] and zr.get('tests')}"
                 f"|edge_control={zr.get('edge_control')}|accept={zr['accept_state']}|stop_ticks={zr['stop_ticks']}")
        if zr["side_conflict"]: L.append(zr["side_conflict"])
        for side, lad in zr["ladder"].items():
            L.append(f"ladder={zr['label'][:60]}|{side}|TP1={lad['TP1']}|TP2={lad['TP2']}|RUN={lad['RUN']}|R_TP1={lad['R_TP1']}|R_TP2={lad['R_TP2']}|R_RUN={lad['R_RUN']}")
    L.append(f"research_check_b={research['check_b']}")
    L.append("research_check_f=" + (";".join(f_log) or "none"))
    L.append("research_1adr_would_drop=" + (",".join(research["would_drop_1adr"]) or "none"))
    L.append("research_60pt_would_cut=" + (",".join(research["would_cut_60pt"]) or "none"))
    if gex_row and str(gex_row.get("ok")) == "True":
        L += ["gex_model=MQ_REPLICA", "gex_source=EOD_PRIOR"]
        for g in gex_levels: L.append(f"mq_{g.name.lower()}={g.lo:.2f}")
    L += ["# --- review ---", f"review={review}", "review_note=" + ("; ".join(fails + notes) if (fails or notes) else "all checks passed"), "end=1"]
    side = {"plan": L, "date": p["date"], "as_of": as_of.isoformat(), "market_context": mctx, "context_base": ctx_base,
            "htf_acceptance": htf_acc, "htf_acceptance_states": [st.__dict__ | {"available_at": st.available_at.isoformat()}
                                                                  for st in (htf_val_state, htf_vah_state) if st is not None],
            "review": review, "fails": fails, "notes": notes,
            "research": research, "zones": [dict(label=zr["label"], lo=zr["lo"], hi=zr["hi"], long=zr["long"], short=zr["short"],
                                                 families=zr["fam"].families, levels=zr["fam"].levels, ladder=zr["ladder"],
                                                 stop_ticks=zr["stop_ticks"], available_at=as_of.isoformat()) for zr in zone_rows],
            "targets": [dict(label=t["label"], lo=t["lo"], hi=t["hi"]) for t in targets],
            "rej_flip_zones": [z.as_row() for z in rej_sel], "map4_areas": [a.as_row() for a in areas],
            "delta_bands": [b.as_row() for b in bands], "dd_edge": dd.as_row() if dd else None,
            "dd_edge_wk": dd_wk.as_row() if dd_wk else None, "weekly_dd": weekly_dd,
            "vwap": {k: v.as_row() for k, v in vwap_res.items() if v is not None}}
    return "\n".join(L) + "\n", side


def _ladder(side, c, ref, rej, lv, areas, bands, wk_val, wk_vah, pd1, draw, dds, stop_ticks):
    """Phase 6 P1: TP1 nearest REJ/FLIP zone else nearest value edge / POC / HVN; TP2 nearest HVN area or delta band
    beyond TP1; RUNNER the opposite edge of the value area price is trading into (weekly, then PD), else the draw,
    or the far edge of a double distribution. R uses the zone stop (width + 2 ticks) from the zone's near edge."""
    up = side == "long"
    entry = c["hi"] if up else c["lo"]
    def beyond(x): return x > entry if up else x < entry
    def dist(x): return abs(x - entry)
    def fmt(lo, hi): return f"{lo:.2f}-{hi:.2f}"
    tp1 = min(((dist(z.lo if up else z.hi), (z.lo, z.hi)) for z in rej if beyond(z.lo if up else z.hi)), default=None)
    if tp1 is None:
        pts = [(dist(v), (v - PAD, v + PAD)) for k, v in lv.items() if F.family_of(k) in ("AUCTION_VALUE", "VOLUME") and beyond(v)]
        tp1 = min(pts, default=None)
    tp2 = None
    if tp1:
        edge1 = tp1[1][1] if up else tp1[1][0]
        cands = [(dist(a.lo if up else a.hi), (a.lo, a.hi)) for a in areas if (a.lo > edge1 if up else a.hi < edge1)]
        cands += [(dist(b.lo if up else b.hi), (b.lo, b.hi)) for b in bands if (b.lo > edge1 if up else b.hi < edge1)]
        tp2 = min(cands, default=None)
    run = None
    for va in ((wk_val, wk_vah), (pd1.get("val"), pd1.get("vah"))):
        if va[0] is None or va[1] is None: continue
        far = va[1] if up else va[0]
        if beyond(far): run = (far - PAD, far + PAD); break
    if run is None and draw is not None and beyond(draw.draw_lo if up else draw.draw_hi): run = (draw.draw_lo, draw.draw_hi)
    for dd in dds:          # PD double distribution first, then the weekly one (E23)
        if run is None and beyond(dd.extra["runner"]): run = (dd.extra["runner"] - PAD, dd.extra["runner"] + PAD)
    risk_pts = stop_ticks * TICK
    def rr(t):
        if t is None: return ""
        near = t[0] if up else t[1]
        return f"{abs(near - entry) / risk_pts:.2f}"
    return {"TP1": fmt(*tp1[1]) if tp1 else "", "TP2": fmt(*tp2[1]) if tp2 else "", "RUN": fmt(*run) if run else "",
            "R_TP1": rr(tp1[1] if tp1 else None), "R_TP2": rr(tp2[1] if tp2 else None), "R_RUN": rr(run)}
