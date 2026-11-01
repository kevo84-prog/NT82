"""Exit replay engine: exit models M0 / M1 / M2 / M2E on fixed entries, on the tick tape (design step 9; JE 0.4, Oct 25 2026).

Same v3.4 fill model as fills.py (entry 250 ms after the signal bar close at the bid/ask; target limit fills 1 tick
through; stop-market fills stop -/+ slip ticks; same-timestamp tie = stop; flatten 14:55 CT at the bid/ask), extended to:
  - several legs (contracts), each with its own target or none (runner);
  - stop changes that take effect from the bar AFTER the condition (1-minute bars stamped at their end: a tick at
    exactly hh:mm:00.000 belongs to the bar ending then; a change made at bar end T applies to ticks after T);
  - stops that only move in the trade's favour;
  - a market exit at a given time, filled at the bid (long) / ask (short) known LATENCY_MS after the bar close.
M0 with one leg is the fill model itself; its gate is reproducing fills_model.csv trade by trade.

Models (design v3.9 "Exit models"; M2E = phase2_change_list_DRAFT.md arm 1):
  M0  one contract, A0's stop and target.
  M1  M0, plus exit at the close of the bar that completes the 2nd consecutive opposing effort bar
      (EXIT_WARN row with Reasons=OPPOSING_EFFORT_STREAK_2 for this trade), whatever the P/L.
  M2  two contracts; one off at TP1 (A0's target); stop to entry from the bar after TP1 fills; the runner targets TP2
      (next level beyond TP1 in the strategy's own target list, see target_levels) or holds to the flatten; the
      runner's stop trails 2 ticks beyond the far edge of the newest same-side intraday IMB / POWER zone created after
      entry, only in the trade's favour, from the bar after TP1 (and after the zone's bar).
  M2E one contract; from entry on, the stop trails 2 ticks beyond the far edge of each new same-side intraday IMB /
      POWER zone created after the fill and lying entirely beyond the fill (long ZoneLo > fill, short ZoneHi < fill).
R = net ticks / (contracts x planned risk ticks), planned risk = |entry fill - stop anchor| / tick (phase_report's
convention); commission COMM_TICKS per contract.
"""
import datetime as dt
import numpy as np

from .fills import TICK, LATENCY_MS, FLATTEN

COMM_TICKS = 2 * 2.87 / 5.0   # $5.74 per contract round turn = 1.148 NQ ticks
TRAIL_TICKS = 2


def bar_end(t):
    """End of the 1-minute bar that contains time t (bars are stamped at their end)."""
    t = t.astype(dt.datetime) if isinstance(t, np.datetime64) else t
    base = t.replace(second=0, microsecond=0)
    return base if t == base else base + dt.timedelta(minutes=1)


def replay(tape, side, signal_end, stop, legs, stop_events=(), market_exit_at=None, on_leg_fill=None,
           stop_slip=1, latency_ms=LATENCY_MS, flatten=FLATTEN, gap_fill=False, stop_delay_ms=0, crossed=None):
    """side +1/-1; legs = list of target prices (None = runner, no target).
    stop_events = iterable of (effective_after: datetime, stop_price): candidate stops, each applied to ticks after
      effective_after if it moves the stop in the trade's favour.
    market_exit_at = datetime of a bar close at which all open legs are exited at market (filled latency_ms later).
    on_leg_fill(leg_index, fill_time) -> list of new (effective_after, stop_price) events (used by M2 after TP1).
    gap_fill=False is the v3.4 fill model (stop fills at stop -/+ slip). gap_fill=True (sensitivity only, not the frozen
      model): when the triggering trade is already beyond the stop (a stop moved to a level the market has passed, or a
      jump), the fill is that trade's price -/+ slip.
    stop_delay_ms: a stop change goes active this long after its effective_after time (fill model v3.5 proposal: 250);
      the previous stop works until then. 0 = v3.4 (active from the first tick after the bar close).
    crossed: what happens to a change the market is already through (long: bid <= new stop; short: ask >= new stop).
      None = v3.4 (no check, the stop moves anyway).
      "live" = fill model v3.5 as frozen: at the decision (the bar close) the strategy checks the current quote and does
        not submit a crossed change; a submitted change arrives stop_delay_ms later and is rejected if crossed on
        arrival. Either way the existing stop stays and keeps working throughout.
      "reject" = exit first look v2: checked only on arrival, rejected if crossed, existing stop stays.
      "market" = v2 report-only line: checked on arrival only; a crossed change exits all legs at market (bid long / ask
        short).
      "live_market" = v3.5 report-only line (today's S1.4 handling, PROTECT_FLAT): the same decision check as "live"
        (crossed at the bar close = not submitted), but a change crossed on arrival exits at market at that moment.
    Returns dict(entry_time, entry, legs=[dict(exit_time, exit, reason, ticks)], moves, skipped, skipped_decision,
    rejected_arrival)."""
    t0 = signal_end + dt.timedelta(milliseconds=latency_ms)
    bid, ask = tape.quote_at(t0)
    entry = ask if side > 0 else bid
    delay = dt.timedelta(milliseconds=stop_delay_ms)
    events = sorted(((t + delay, p, t) for t, p in stop_events), key=lambda e: e[0])   # (active at, price, decided at)
    ev_i = 0
    moves = skip_dec = rej_arr = 0
    open_legs = {k: tg for k, tg in enumerate(legs)}
    out = [None] * len(legs)
    mx = None if market_exit_at is None else market_exit_at + dt.timedelta(milliseconds=latency_ms)
    i = np.searchsorted(tape.t, np.datetime64(t0, "us"), side="right")
    flat_at = np.datetime64(dt.datetime.combine(signal_end.date(), flatten), "us")
    n = len(tape.t)

    def close(k, ts, px, reason):
        out[k] = dict(exit_time=ts, exit=px, reason=reason, ticks=round((px - entry) * side / TICK, 2))
        open_legs.pop(k)

    while i < n and open_legs:
        ts = tape.t[i]
        tsd = ts.astype(dt.datetime)
        if ts >= flat_at:
            b, a = tape.b[i - 1], tape.a[i - 1]
            for k in list(open_legs): close(k, tsd, b if side > 0 else a, "FLATTEN")
            break
        if mx is not None and tsd > mx:
            b, a = tape.quote_at(mx)
            for k in list(open_legs): close(k, mx, b if side > 0 else a, "M1_EXIT")
            break
        mkt_exit = None
        while ev_i < len(events) and events[ev_i][0] < tsd:   # stop changes active for ticks after their activation time
            act, cand, dec = events[ev_i]
            ev_i += 1
            if side * (cand - stop) <= 0: continue            # only moves in the trade's favour
            if crossed in ("live", "live_market"):
                b, a = tape.quote_at(dec)                     # decision: quote at the bar close; crossed = not submitted
                if (b <= cand) if side > 0 else (a >= cand):
                    skip_dec += 1; continue
            if crossed:
                b, a = tape.quote_at(act)                     # arrival
                if (b <= cand) if side > 0 else (a >= cand):
                    if crossed in ("reject", "live"):
                        rej_arr += 1; continue
                    mkt_exit = (act, b if side > 0 else a); break
            stop = cand; moves += 1
        if mkt_exit:
            for k in list(open_legs): close(k, mkt_exit[0], mkt_exit[1], "CROSSED_MKT")
            break
        j = i
        hit_stop = False
        trig = None
        hit_tgt = set()
        while j < n and tape.t[j] == ts:
            pr = tape.p[j]
            if side > 0:
                if pr <= stop and not hit_stop: hit_stop, trig = True, pr
                hit_tgt |= {k for k, tg in open_legs.items() if tg is not None and pr >= tg + TICK}
            else:
                if pr >= stop and not hit_stop: hit_stop, trig = True, pr
                hit_tgt |= {k for k, tg in open_legs.items() if tg is not None and pr <= tg - TICK}
            j += 1
        if hit_stop:
            base = (min(stop, trig) if side > 0 else max(stop, trig)) if gap_fill else stop
            px = base - side * stop_slip * TICK
            for k in list(open_legs): close(k, tsd, px, "STOP")
            break
        for k in sorted(hit_tgt):
            close(k, tsd, legs[k], "TARGET" if k == 0 else "TARGET2")
            if on_leg_fill:
                new = on_leg_fill(k, tsd)
                if new:
                    events = events[:ev_i] + sorted(events[ev_i:] + [(t + delay, p, t) for t, p in new], key=lambda e: e[0])
        i = j
    for k in list(open_legs):
        out[k] = dict(exit_time=None, exit=np.nan, reason="DATA_END", ticks=np.nan)
    return dict(entry_time=t0, entry=entry, legs=out, moves=moves, skipped=skip_dec + rej_arr,
                skipped_decision=skip_dec, rejected_arrival=rej_arr)


def zone_stop(side, lo, hi):
    """2 ticks beyond the zone's far edge (long: below its low; short: above its high)."""
    return lo - TRAIL_TICKS * TICK if side > 0 else hi + TRAIL_TICKS * TICK


def run_model(model, tape, trade, zones, exit_warns=(), stop_slip=1, gap_fill=False, stop_delay_ms=0, crossed=None):
    """trade: dict(side, signal_end, stop, target, tp2). zones: list of (time, LocationType, lo, hi) of ZONE_CREATED rows
    that day. exit_warns: times of OPPOSING_EFFORT_STREAK_2 rows for this trade. Returns dict with R and per-leg exits."""
    side, se, stop0, tgt = trade["side"], trade["signal_end"], trade["stop"], trade["target"]
    t0 = se + dt.timedelta(milliseconds=LATENCY_MS)
    want = "BUY" if side > 0 else "SELL"
    later = [(t, lo, hi) for t, lt, lo, hi in zones if t > t0 and lt.endswith(want)]
    if model in ("M0", "M1"):
        mx = None
        if model == "M1":
            ws = sorted(w for w in exit_warns if w > t0)
            mx = ws[0] if ws else None
        r = replay(tape, side, se, stop0, [tgt], market_exit_at=mx, stop_slip=stop_slip, gap_fill=gap_fill, stop_delay_ms=stop_delay_ms, crossed=crossed)
    elif model == "M2E":
        bid, ask = tape.quote_at(t0)
        fill = ask if side > 0 else bid
        ev = [(t, zone_stop(side, lo, hi)) for t, lo, hi in later if (lo > fill if side > 0 else hi < fill)]
        r = replay(tape, side, se, stop0, [tgt], stop_events=ev, stop_slip=stop_slip, gap_fill=gap_fill, stop_delay_ms=stop_delay_ms, crossed=crossed)
    elif model == "M2":
        bid, ask = tape.quote_at(t0)
        fill = ask if side > 0 else bid

        def after_tp1(k, ts):
            if k != 0: return []
            be = bar_end(ts)
            return [(be, fill)] + [(max(t, be), zone_stop(side, lo, hi)) for t, lo, hi in later]
        r = replay(tape, side, se, stop0, [tgt, trade.get("tp2")], on_leg_fill=after_tp1, stop_slip=stop_slip, gap_fill=gap_fill, stop_delay_ms=stop_delay_ms, crossed=crossed)
    else:
        raise ValueError(model)
    risk = abs(r["entry"] - stop0) / TICK
    ticks = sum(l["ticks"] for l in r["legs"])
    nc = len(r["legs"])
    net = ticks - nc * COMM_TICKS
    return dict(model=model, entry=r["entry"], legs=r["legs"], contracts=nc, gross_ticks=ticks, net_ticks=net,
                risk_ticks=risk, R=net / (nc * risk) if risk else np.nan,
                exit_reason="+".join(l["reason"] for l in r["legs"]), moves=r["moves"], skipped=r["skipped"],
                skipped_decision=r["skipped_decision"], rejected_arrival=r["rejected_arrival"],
                exit_time=max((l["exit_time"] for l in r["legs"] if l["exit_time"] is not None), default=None))


def target_levels(side, entry, stop, exclude_id, plan_zones, intraday_zones, vwap, sess_ext, min_rr=1.5, counter_first=False):
    """The strategy's FindTarget level list (JeronOrderFlowStrategy.cs FindTarget): active qualified zones' near edges
    beyond entry (long: zone lows above entry + 1 tick), the session VWAP and the session high / low, nearest first.
    Returns (levels sorted nearest first as (price, label), tp1_index) with tp1 = nearest meeting min R:R."""
    lv = []
    for zid, lo, hi in list(plan_zones) + list(intraday_zones):
        if zid == exclude_id: continue
        edge = lo if side > 0 else hi
        if side * (edge - entry) > TICK + 1e-9: lv.append((edge, zid + (".lo" if side > 0 else ".hi")))
    if vwap and side * (vwap - entry) > TICK + 1e-9: lv.append((vwap, "SESSION_VWAP"))
    if sess_ext is not None and side * (sess_ext - entry) > TICK + 1e-9:
        lv.append((sess_ext, "SESSION_HIGH" if side > 0 else "SESSION_LOW"))
    lv.sort(key=lambda x: side * (x[0] - entry))
    if not lv: return [], None
    risk = side * (entry - stop)
    pick = 0
    if risk > 0 and not counter_first:
        for k, (p, _) in enumerate(lv):
            if side * (p - entry) / risk >= min_rr: pick = k; break
    return lv, pick
