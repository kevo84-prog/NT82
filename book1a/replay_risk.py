"""Book 1A replay with the C3 dollar risk check, sizing and dollar daily limit (R3 = C1 + risk; R4 = Book 1A).

Uses the frozen Book 1 replay building blocks unchanged (jeron_engine.arm_replay: candidate selection, queueing,
TryEnter block order, the RH1 retest path, exit_replay.run_model M0 and the v3.4 / v3.5 fills). What changes for
R3 / R4 only (replay plan 4a, E2):
  - before every order: estimated risk = (stop ticks + 2) x $5 x N + $5.74 x N; N = the largest whole number
    fitting min($1,000, remaining daily budget); if 1 NQ does not fit the candidate is RISK_REJECT (never shrunk);
  - the dollar daily limit ($2,000), the 3-trade cap and the 2-loss halt all apply; the day stops at whichever
    comes first (the Book 1 400-tick halt is not used for R3 / R4);
  - RISK_BREACH_FILL when a realized loss exceeds the plan; every trade records N, planned risk, theoretical R and
    realized net R (commission on every contract).
R1 and R2 keep Book 1's own replay (qty 1, 400-tick halt): see run_r1_r2.py.
Fill model: v3.5 by default for R3 / R4 (replay plan 4a, changed Nov 1, 2026: v3.5 for all four strategies);
v3.4 only when asked for explicitly.
"""
from __future__ import annotations

import datetime as dt
from typing import Callable, List, Optional

import numpy as np

from book1a import ledger as L, risk as RK
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import arm_replay as AR, exit_replay as XR, fills

VERSION = "replay-risk-v1.0"
TK = fills.TICK


def replay(log, tape, strategy: str, veto: Optional[Callable] = None, retest: Optional[dict] = None, fill: str = "v3.5",
           stop_slip: int = 1, risk_cfg: RK.RiskConfig = RK.DEFAULT) -> dict:
    kw = dict(gap_fill=True, stop_delay_ms=250, crossed="live") if fill == "v3.5" else {}
    if fill not in ("v3.4", "v3.5"):
        raise ValueError(fill)
    attempts, trades, retests, risk_events = [], [], [], []
    day = None
    state: Optional[RK.DayRiskState] = None
    busy_until = None
    pending = None            # (exit_time, net_pnl_cents, trade_id)

    def settle(now):
        nonlocal pending
        if pending and pending[0] < now:
            ev = state.on_exit(pending[1], pending[2])
            if ev:
                risk_events.append(dict(date=day.isoformat(), **ev))
            pending = None

    for a in AR.attempts(log, veto):
        t = a["t"]
        if t.date() != day:
            if pending:
                settle(dt.datetime.max)
            day, busy_until, state = t.date(), None, RK.DayRiskState(risk_cfg)
        px = AR.decision_tick(tape, t)
        i = np.searchsorted(tape.t, np.datetime64(t, "us"), side="right")
        now = tape.t[i].astype(dt.datetime) if i < len(tape.t) else t
        settle(now)
        pre, post, plan = AR.static_blocks(log, a, px)
        reasons = list(pre)
        if busy_until is not None and busy_until >= now:
            reasons.append("ALREADY_IN_TRADE")
        reasons += post
        r = a["row"]
        side = 1 if r["Direction"] == "Long" else -1
        tr = dict(side=side, signal_end=t, stop=float(r["StopAnchor"]), target=float(r["TargetPrice"]))
        path = "immediate"
        decision = None
        if not reasons and retest is not None and a["cand"]["SetupFamily"] == "INITIATION":
            p = AR.retest_path(retest["bars"], a["cand"], t, retest.get("fail_ticks", 2))
            retests.append(dict(event=a["event"], time=t, outcome=p["outcome"], at=p["at"]))
            busy_until = p["at"]
            if p["outcome"] != "RETEST_ENTERED":
                attempts.append(dict(event=a["event"], time=t, reasons="RH1_" + p["outcome"], px=px)); continue
            te = p["at"]; px2 = AR.decision_tick(tape, te)
            m_ = te.hour * 60 + te.minute
            blk = []
            if m_ >= AR.LAST_ENTRY or m_ >= AR.NY_END: blk.append("OUTSIDE_ENTRY_HOURS")
            if px2 is not None:
                if (px2 <= p["stop"] + TK) if side > 0 else (px2 >= p["stop"] - TK): blk.append("PRICE_PAST_STOP")
                if (px2 >= tr["target"] - TK) if side > 0 else (px2 <= tr["target"] + TK): blk.append("PRICE_PAST_TARGET")
                if abs(px2 - p["entry"]) > AR.SLIPPAGE_TICKS * TK + 1e-9: blk.append("ENTRY_SLIPPAGE")
            if blk:
                attempts.append(dict(event=a["event"], time=te, reasons="|".join(blk), px=px2)); continue
            tr = dict(side=side, signal_end=te, stop=p["stop"], target=tr["target"]); path = "retest"
            t = te
        if not reasons:
            # Book 1A pre-trade dollar risk check at the decision (planned stop from the entry reference)
            entry_ref = float(a["row"]["EntryRef"]) if path == "immediate" else p["entry"]
            stop_ticks = int(round(abs(entry_ref - tr["stop"]) / TK))
            decision = state.pre_trade_check(stop_ticks)
            if not decision.accepted:
                reasons.append(decision.reason)
        attempts.append(dict(event=a["event"], time=t, reasons="|".join(reasons), px=px,
                             **(decision.as_row() if decision else {})))
        if reasons:
            continue
        m = XR.run_model("M0", tape, tr, log.zones[t.date()], stop_slip=stop_slip, **kw)
        leg = m["legs"][0]
        n = decision.contracts
        state.on_entry(decision)
        exit_reason = {"STOP": "STOP_FIRST", "TARGET": "TARGET_FIRST", "FLATTEN": "TIME_EXIT"}.get(leg["reason"], leg["reason"])
        trade = L.Trade(strategy, a["event"], t.strftime("%Y-%m-%d"), (tr["signal_end"] + dt.timedelta(milliseconds=fills.LATENCY_MS)).strftime("%H:%M:%S.%f")[:12],
                        "LONG" if side > 0 else "SHORT", n, float(m["entry"]), float(tr["stop"]), float(tr["target"]),
                        leg["exit_time"].strftime("%H:%M:%S.%f")[:12] if leg["exit_time"] else "", float(leg["exit"]), exit_reason,
                        decision.reason, decision.estimated_risk, fill, stop_slip, fills.LATENCY_MS)
        net_cents = int(round(trade.net_usd * 100))
        trade.risk_breach_fill = net_cents < 0 and -net_cents > decision.estimated_risk_cents
        trades.append(trade)
        busy_until = leg["exit_time"]
        pending = (leg["exit_time"], net_cents, a["event"])
    if pending:
        settle(dt.datetime.max)
    return dict(attempts=attempts, trades=trades, retests=retests, risk_events=risk_events)
