"""Rules-only plan (design v3.2, frozen algorithm) from a JeronPreopenMap v2.3 packet (JE 0.3, Oct 25 2026).

Steps (design "Rules-only plan"): 1 context, 2 decision zones, 3 side rules (+ test history), 4 targets,
5 balance and lava, 6 invalidation, 7 ES gates, 8 zone review A-F (econ calendar file instead of the macro note),
then GEX lines from the replica (logged only, added after the plan). Every threshold is OURS and frozen.

Approximations, written down so they are not changed after results are read:
- "lower highs / higher lows into the zone": higher_lows_into_zone (price pressing up into a zone above) weakens
  the short response there; lower_highs_into_zone (pressing down into a zone below) weakens the long response.
  The responding side becomes NONE and the breaking side INITIATION, when the zone has 4+ tests.
  shrinking_time does the same for the side that would respond off the zone (by where the zone sits vs price).
- "crossed both ways in the last day": from the packet's 1-hour bars (structure.h1) of the 24 hours before the
  as-of: hourly closes moved from below the zone to above it at least once AND from above to below at least once
  -> NONE on both sides.
- Check C (risk fit) per allowed side: entry at the zone edge facing the trade, stop at the far edge + 2 ticks,
  target = the nearest TARGET zone's near edge beyond the entry in the trade's direction (prompt: "the nearest
  target"); R < 1.5 or risk > 100 points -> NONE. (Phase 1 fix, Oct 25: the first version also counted other
  decision zones as targets, which made almost every side NONE.)
"""
import csv, datetime as dt, json
from pathlib import Path

TICK = 0.25
MAX_W = 60.0          # points
PAD = 5.0             # map pad (points)
LAVA_CLEAR = 15.0
MIN_R = 1.5
MAX_RISK_PTS = 100.0  # about a third of the 400-tick daily loss limit... (400 ticks = 100 points)
TIER1 = ("DATA_TIER1",)


def _r(x):  # round to tick
    return round(round(x / TICK) * TICK, 2)


def context_of(p):
    vm = next((v["label"] for v in p.get("value_migration", []) if v["pair"] == "PD_vs_PD2"), "")
    loc = (p.get("location") or {}).get("vs_pd_value", "")
    h1 = (p.get("structure") or {}).get("h1_trend", "")
    bc = p.get("balance_composite") or {}
    if vm in ("HIGHER", "HIGHER_NO_OVERLAP") and loc in ("ABOVE_VALUE", "INSIDE_VALUE") and h1 != "DOWN":
        return "Bullish", f"PD value {vm} vs PD2, price {loc} of PD value, 1h {h1}"
    if vm in ("LOWER", "LOWER_NO_OVERLAP") and loc in ("BELOW_VALUE", "INSIDE_VALUE") and h1 != "UP":
        return "Bearish", f"PD value {vm} vs PD2, price {loc} of PD value, 1h {h1}"
    if bc.get("overlapping"):
        return "Balanced", f"balance composite {'+'.join(bc.get('members', []))} overlapping; PD value {vm}, price {loc}, 1h {h1}"
    return "None", f"no rule matched: PD value {vm}, price {loc}, 1h {h1}"


def level_prices(p):
    return {l["name"]: float(l["price"]) for l in p.get("levels", []) if l.get("price") is not None}


def cut_zone(z, lv):
    """Zones wider than 60 points are cut back to the levels nearest the middle."""
    lo, hi = float(z["lo"]), float(z["hi"])
    if hi - lo <= MAX_W: return lo, hi, False
    mid = (lo + hi) / 2
    prices = sorted((lv[n] for n in z.get("levels", []) if n in lv), key=lambda x: abs(x - mid))
    keep = []
    for x in prices:
        span = (max(keep + [x]) - min(keep + [x])) + 2 * PAD
        if span <= MAX_W: keep.append(x)
    if not keep: keep = [mid]
    return _r(min(keep) - PAD), _r(max(keep) + PAD), True


def build_plan(p, calendar_rows, gex_row=None, roll_dates=(), daily_loss_ticks=400):
    date = p["date"]; ref = float(p["ref_price"]); notes, fails = [], []
    adr = float((p.get("ranges") or {}).get("adr_full") or 0) or 400.0
    lv = level_prices(p)
    ctx, ctx_note = context_of(p)

    # ---- A. data -------------------------------------------------------------------------
    data = p.get("data") or {}
    ps = {s["slot"]: s for s in p.get("prior_sessions", [])}
    on = p.get("overnight") or {}
    wk = p.get("weekly") or {}
    a_fail = []
    # prompt check A: "data.gaps empty in the last 24 h" (Phase 2 fix, Oct 25: the first version failed on any gap the
    # packet still listed, so the Nov 28, 2025 CME outage made Dec 1-4 LOG_ONLY)
    asof_dt = dt.datetime.strptime(date + " " + str(p.get("asof_ct", "08:10")), "%Y-%m-%d %H:%M")
    recent = [g for g in data.get("gaps", []) if dt.datetime.strptime(g["to"][:16], "%Y-%m-%d %H:%M") > asof_dt - dt.timedelta(hours=24)]
    if recent: a_fail.append("A: data gap in the last 24 h " + json.dumps(recent)[:80])
    if not (ps.get("PD") or {}).get("covered"): a_fail.append("A: PD profile missing")
    if on.get("vah") is None: a_fail.append("A: overnight profile missing")
    if wk.get("vah") is None: a_fail.append("A: weekly profile missing")
    if on.get("high") is not None and not (on["low"] - 0.1 * adr <= ref <= on["high"] + 0.1 * adr):
        a_fail.append("A: ref price outside the overnight range")
    es = p.get("es") or {}
    fails += a_fail

    # ---- 2. decision zones ---------------------------------------------------------------
    dz = []
    for z in p.get("zones", []):
        if z.get("tier") != "DECISION": continue
        lo, hi, cut = cut_zone(z, lv)
        side = "ABOVE" if lo > ref else ("BELOW" if hi < ref else "AT")
        dist = 0.0 if side == "AT" else (lo - ref if side == "ABOVE" else ref - hi)
        if dist > adr: continue
        dz.append(dict(lo=lo, hi=hi, label=z["label"], src=z, side=side, dist=dist, cut=cut))
    above = sorted([z for z in dz if z["side"] == "ABOVE"], key=lambda z: z["dist"])[:2]
    below = sorted([z for z in dz if z["side"] == "BELOW"], key=lambda z: z["dist"])[:2]
    at = [z for z in dz if z["side"] == "AT"]
    chosen = sorted(above + below + at, key=lambda z: z["lo"])
    merged = []
    for z in chosen:   # neighbours that touch are merged
        if merged and z["lo"] <= merged[-1]["hi"]:
            m = merged[-1]; m["hi"] = max(m["hi"], z["hi"]); m["label"] = m["label"] + "_" + z["label"].replace("D_", "")
            m["src_list"].append(z["src"]); m["cut"] = m["cut"] or z["cut"]
        else:
            z = dict(z); z["src_list"] = [z["src"]]; merged.append(z)
    for z in merged:
        if z["hi"] - z["lo"] > MAX_W:   # a merge made it too wide: keep the part nearest price
            if z["lo"] > ref: z["hi"] = _r(z["lo"] + MAX_W)
            else: z["lo"] = _r(z["hi"] - MAX_W)
            notes.append(f"B: {z['label']} narrowed to 60 pts")
        if z["cut"]: notes.append(f"B: {z['label']} cut to the levels nearest its middle")
        z["label"] = z["label"][:60]
    dec = merged
    if not any(z["lo"] > ref or z["hi"] >= ref for z in dec if z["hi"] >= ref) or not any(z["hi"] < ref or z["lo"] <= ref for z in dec if z["lo"] <= ref):
        pass
    has_above = any(z["hi"] >= ref for z in dec)
    has_below = any(z["lo"] <= ref for z in dec)
    if not (has_above and has_below):
        fails.append("B: no decision zone within 1 ADR on " + ("both sides" if not has_above and not has_below else ("the upper side" if not has_above else "the lower side")))

    # ---- 3. side rules + D (test history) ------------------------------------------------
    for z in dec:
        if ctx == "Bullish": lng, sht = "ANY", "INITIATION"
        elif ctx == "Bearish": lng, sht = "INITIATION", "ANY"
        else: lng, sht = "ANY", "ANY"
        zone_above = z["lo"] > ref
        for src in z["src_list"]:
            t = src.get("tests") or {}
            n = (t.get("from_below") or 0) + (t.get("from_above") or 0)
            if n >= 4 and t.get("higher_lows_into_zone"):
                sht, lng = "NONE", ("INITIATION" if lng != "NONE" else lng); notes.append(f"D: {z['label']} higher lows into it ({n} tests): short NONE, long INITIATION")
            if n >= 4 and t.get("lower_highs_into_zone"):
                lng, sht = "NONE", ("INITIATION" if sht != "NONE" else sht); notes.append(f"D: {z['label']} lower highs into it ({n} tests): long NONE, short INITIATION")
            if t.get("shrinking_time"):
                if zone_above: sht = "NONE"; lng = "INITIATION" if lng != "NONE" else lng
                else: lng = "NONE"; sht = "INITIATION" if sht != "NONE" else sht
                notes.append(f"D: {z['label']} shrinking time per test")
        if crossed_both_ways(p, z["lo"], z["hi"]):
            lng = sht = "NONE"; notes.append(f"D: {z['label']} crossed both ways in the last day: NONE")
        z["long"], z["short"] = lng, sht

    # ---- 4. targets ----------------------------------------------------------------------
    tg = []
    for z in p.get("zones", []):
        if z.get("tier") == "DECISION": continue
        lo, hi = float(z["lo"]), float(z["hi"])
        if any(lo <= d["hi"] and hi >= d["lo"] for d in dec): continue      # overlaps a decision zone
        if any(lo <= t["hi"] and hi >= t["lo"] for t in tg): continue
        tg.append(dict(lo=lo, hi=hi, label=z["label"] if z["label"].startswith("T_") else "T_" + z["label"]))
    daily = (p.get("structure") or {}).get("daily", [])
    for side in ("above", "below"):
        ok = any((t["lo"] > ref) if side == "above" else (t["hi"] < ref) for t in tg)
        if ok: continue
        cands = sorted([d["high"] for d in daily if d.get("high") and d["high"] > ref]) if side == "above" else \
                sorted([d["low"] for d in daily if d.get("low") and d["low"] < ref], reverse=True)
        for c in cands:
            lo, hi = _r(c - 5), _r(c + 5)
            if not any(lo <= x["hi"] and hi >= x["lo"] for x in dec + tg):
                tg.append(dict(lo=lo, hi=hi, label="T_DAILY_" + ("HIGH" if side == "above" else "LOW"))); notes.append(f"B: target {side} from structure.daily"); break
        else:
            fails.append(f"B: no target {side} price")

    # ---- C. risk fit -----------------------------------------------------------------------
    edges = sorted([(x["lo"], x["hi"]) for x in tg])
    for z in dec:
        risk = (z["hi"] - z["lo"]) + 2 * TICK
        if z["long"] != "NONE":
            entry = z["hi"]; up = [lo for lo, hi in edges if lo > entry]
            r = (min(up) - entry) / risk if up else 0
            if r < MIN_R or risk > MAX_RISK_PTS:
                z["long"] = "NONE"; notes.append(f"C: {z['label']} long NONE (R {r:.2f}, risk {risk:.1f} pts)")
        if z["short"] != "NONE":
            entry = z["lo"]; dn = [hi for lo, hi in edges if hi < entry]
            r = (entry - max(dn)) / risk if dn else 0
            if r < MIN_R or risk > MAX_RISK_PTS:
                z["short"] = "NONE"; notes.append(f"C: {z['label']} short NONE (R {r:.2f}, risk {risk:.1f} pts)")
    if dec and all(z["long"] == "NONE" and z["short"] == "NONE" for z in dec):
        fails.append("C/D: every decision side is NONE")

    # ---- 5. balance and lava ---------------------------------------------------------------
    bc = p.get("balance_composite") or {}
    balance = lava = None
    if bc.get("overlapping") and bc.get("val") is not None and bc.get("vah") is not None:
        balance = (_r(bc["val"]), _r(bc["vah"]))
        third = (balance[1] - balance[0]) / 3
        lv_lo, lv_hi = _r(balance[0] + third), _r(balance[1] - third)
        if lv_hi > lv_lo and all(lv_hi <= d["lo"] - LAVA_CLEAR or lv_lo >= d["hi"] + LAVA_CLEAR for d in dec):
            lava = (lv_lo, lv_hi)
        else:
            notes.append("B: no lava (middle third not 15 pts clear of the decision zones)")
    else:
        notes.append("balance omitted: PD-ON value not overlapping (migrating)")

    # ---- 6. invalidation ------------------------------------------------------------------
    # each side uses only the decision zones on that side of price (Phase 1 fix, Oct 25: with no zone above price
    # the first version put invalidate_above below price, so the context flipped minutes after the open)
    up = [z for z in dec if z["hi"] > ref]; dn = [z for z in dec if z["lo"] < ref]
    inv_above = _r(max(z["hi"] for z in up) + 2 * TICK) if up else None
    inv_below = _r(min(z["lo"] for z in dn) - 2 * TICK) if dn else None

    # ---- F. day suitability (calendar file) --------------------------------------------------
    no_trade, max_trades, events = [], None, []
    for row in calendar_rows:
        if row["date"] != date or row.get("status") == "CANCELED": continue
        events.append(row.get("gex_event") or row["category"])
        if row.get("no_trade_ct"): no_trade.append(row["no_trade_ct"])
        if (row.get("action") or "").startswith("max_trades="): max_trades = 1
        if row["category"] in ("ROLL", "HOLIDAY", "HALF_DAY", "CLOSED"): fails.append(f"F: {row['category'].lower()} ({row['event']})")
    rg = p.get("ranges") or {}
    if (rg.get("on_range_vs_adr_full") or 0) > 1.0: max_trades = 1; notes.append("F: overnight range > 1 ADR: max_trades=1")
    pd = ps.get("PD") or {}
    if pd.get("day_high") and pd.get("day_low"):
        gap = max(ref - pd["day_high"], pd["day_low"] - ref, 0)
        if gap > 0.5 * adr: max_trades = 1; notes.append("F: gap beyond PD range > 0.5 ADR: max_trades=1")
    cal = p.get("calendar") or {}
    if cal.get("half_day_today"): fails.append("F: half day")
    if date in roll_dates: fails.append("F: roll day")
    if not calendar_rows and ctx == "None": fails.append("F: calendar missing and context None")

    review = "APPROVED" if not fails else "LOG_ONLY"

    # ---- write ---------------------------------------------------------------------------
    L = ["# JeronPreopenPlan v1.5 (rules-only, backtest; design v3.2 frozen algorithm, rules_plan.py JE 0.3.3)",
         f"plan_id={date}-v1", f"date={date}", "asof=08:25", f"packet_asof={p.get('asof_ct', '')}",
         f"context={ctx}", f"context_note={ctx_note}"]
    for z in dec:
        L.append(f"zone={z['lo']:.2f}-{z['hi']:.2f}|{z['label']}|DECISION|long={z['long']}|short={z['short']}|alt_long=ANY|alt_short=ANY|confidence=med|note=rules-only")
    for t in sorted(tg, key=lambda t: t["lo"]):
        L.append(f"zone={t['lo']:.2f}-{t['hi']:.2f}|{t['label'][:60]}|TARGET")
    if balance:
        L.append(f"balance={balance[0]:.2f}-{balance[1]:.2f}")
        if bc.get("poc") is not None: L.append(f"balance_poc={_r(bc['poc']):.2f}")
    if lava: L.append(f"lava={lava[0]:.2f}-{lava[1]:.2f}")
    if ctx in ("Bullish", "Bearish"):
        if inv_above is not None: L.append(f"invalidate_above={inv_above:.2f}|Balanced")
        if inv_below is not None: L.append(f"invalidate_below={inv_below:.2f}|Balanced")
    if es.get("available"):
        if es.get("pd_cash_high") is not None: L.append(f"es_long_above={es['pd_cash_high']}")
        if es.get("pd_cash_low") is not None: L.append(f"es_short_below={es['pd_cash_low']}")
        if es.get("pd_settle") is not None: L.append(f"es_settle={es['pd_settle']}")
    L += ["macro=not verified (backtest)", "news=not used (backtest)",
          "calendar=" + ("; ".join(f"{r['time_ct'] or 'n/a'} {r['event']}" for r in calendar_rows if r['date'] == date and r.get('status') != 'CANCELED') or "none in the calendar file")]
    if gex_row and gex_row.get("ok") == "True":
        L.append("# --- GEX map (replica), logged only ---")
        L += ["gex_model=MQ_REPLICA", "gex_source=EOD_PRIOR", "gex_calc=FULL",
              f"gex_regime={'POS' if gex_row['regime'] == 'positive' else ('NEG' if gex_row['regime'] == 'negative' else 'UNKNOWN')}"]
        for k, name in (("call_resistance", "mq_call_resistance"), ("put_support", "mq_put_support"), ("hvl", "mq_hvl"),
                        ("call_resistance_0dte", "mq_call_resistance_0dte"), ("put_support_0dte", "mq_put_support_0dte"), ("hvl_0dte", "mq_hvl_0dte")):
            v = gex_row.get(k + "_nt") or gex_row.get(k)
            if v: L.append(f"{name}={float(v):.2f}")
    else:
        L.append("gex_regime=UNKNOWN")
    if events: L.append("gex_events=" + ",".join(sorted(set(events))))
    L += ["# --- review ---", f"review={review}",
          "review_note=" + ("; ".join(fails + notes) if (fails or notes) else "all checks passed")]
    if max_trades: L.append(f"max_trades={max_trades}")
    for w in no_trade: L.append(f"no_trade={w}")
    L.append("end=1")
    return "\n".join(L) + "\n", dict(review=review, context=ctx, fails=fails, notes=notes, decision_zones=len(dec), targets=len(tg))


def crossed_both_ways(p, lo, hi, hours=24):
    h1 = (p.get("structure") or {}).get("h1") or []
    closes = [b[4] for b in h1[-hours:]]
    pos = [(-1 if c < lo else (1 if c > hi else 0)) for c in closes]
    last, up, down = None, False, False
    for x in pos:
        if x == 0: continue
        if last is not None and x != last:
            up |= x > last; down |= x < last
        last = x
    return up and down


def _recent(last_test, date):
    """last_test 'MM-dd HH' within 24 h before the as-of (08:xx on `date`)."""
    if not last_test: return False
    try:
        d = dt.datetime.strptime(date[:4] + "-" + last_test, "%Y-%m-%d %H")
        asof = dt.datetime.strptime(date, "%Y-%m-%d").replace(hour=8, minute=20)
        if d > asof: d = d.replace(year=d.year - 1)
        return (asof - d).total_seconds() <= 24 * 3600
    except ValueError:
        return False


def load_calendar(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8-sig")))


def load_gex(path):
    return {r["session"]: r for r in csv.DictReader(open(path, newline="", encoding="utf-8-sig"))}


def write_plans(packet_dir, out_dir, calendar_csv, gex_csv, dates=None, roll_dates=()):
    cal = load_calendar(calendar_csv); gex = load_gex(gex_csv)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); res = {}
    for f in sorted(Path(packet_dir).glob("PreopenPacket_*.json")):
        p = json.load(open(f)); d = p["date"]
        if dates and d not in dates: continue
        text, info = build_plan(p, cal, gex.get(d), roll_dates)
        (out / f"PreopenPlan_{d}.txt").write_text(text, encoding="utf-8")
        res[d] = info
    return res
