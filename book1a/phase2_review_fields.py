"""Per-trade fields registered Nov 6, 2026 (Kyron, before Phase 2) for the Phase 2 what-fails-and-why review.

Logged only, every R1-R4 trade. Never an entry, exit, stop, target, size or rule input. Computed in Phase 2 only:
`compute()` refuses any phase other than "phase2", and nothing in the Phase 1 / 1b code calls it. Built and tested on
synthetic data only (book1a/tests/test_phase2_review_fields.py); wired for phase "phase2" in Step A (Nov 6, 2026).

a) MFE / MAE (POST_ENTRY). From the actual entry fill price, over the tape's trades from the entry fill time to the exit
   fill time, both included. Long: MFE = highest trade - fill, MAE = fill - lowest trade; short: the mirror. In ticks and
   in R = ticks / stop_ticks, stop_ticks = |fill - stop| / 0.25 (as the ledger's stop_ticks). Only trades inside the
   session count: the window ends at the earlier of the exit fill time and the session close (a ledger exit time after
   the close, e.g. a position still open at the 12:15 half-day close, is flagged EXIT_AFTER_SESSION_CLOSE).
b) After a stop exit (POST_EXIT). Window (stop fill time, stop fill time + 30 min] in clock time, cut at that session's
   close from the Book 1 calendar (sessions.session_close: 15:00 CT on a full day, 12:15 CT on the Nov 28 / Dec 24 half
   days; change registered in Phase2_registration.md section 3 before any Phase 2 result; v1.0 cut at a fixed 15:00).
   The largest move in the trade's direction from the stop fill price (long: highest trade - stop fill; short: stop
   fill - lowest trade; ticks and R; may be negative when every trade in the window is against the trade), and whether
   the original target traded in the window (long: a trade at or above the target; short: at or below). Cut at the
   close: TRUNCATED with the minutes available. No trade in the window: DATA_MISSING. Not a stop exit: NOT_APPLICABLE.
c) Entry context (AT_ENTRY). Minutes from initiation (the candidate's signal-bar close) to the entry fill; the confirm bar
   (the bar closing at the entry decision): delta (B volume - S / A volume), delta % (delta / bar volume x 100) and
   range (high - low) in ticks.
compute("phase2", trades, ticks_for, bars_for) runs a), b) and c) for every trade (Phase 2 only).
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import numpy as np

from book1a import sessions as S

VERSION = "phase2-review-fields-v1.3"   # v1.3 (Nov 9, 2026): phase4 allowed (Phase 4 Step A); phase2 / phase3 unchanged
                                        # v1.2 (Nov 8, 2026): phase argument, phase3 allowed (Phase 3 Step A6); phase2 unchanged
                                        # v1.1 (Nov 6, 2026): session-close cut (Book 1 calendar), compute() wired for phase2
PHASES = ("phase2", "phase3", "phase4")  # the phases whose registration uses these fields
TICK = 0.25
WINDOW_MIN = 30


def _ticks(x: float) -> float:
    return round(x / TICK, 2)


def stop_ticks(fill: float, stop: float) -> int:
    return int(round(abs(fill - stop) / TICK))


def mfe_mae(t: np.ndarray, p: np.ndarray, side: int, fill_time: dt.datetime, fill: float, exit_time: Optional[dt.datetime],
            stop: float, close: Optional[dt.datetime] = None) -> dict:
    close = close or S.session_close(fill_time.date())
    end = close if exit_time is None else min(exit_time, close)
    a = np.searchsorted(t, np.datetime64(fill_time, "us"), side="left")
    b = np.searchsorted(t, np.datetime64(end, "us"), side="right")
    st = stop_ticks(fill, stop)
    out = dict(mfe_mae_timing="POST_ENTRY", mfe_mae_trades=int(max(b - a, 0)), stop_ticks_fill=st, mfe_mae_window_end=end,
               mfe_mae_exit_flag="EXIT_AFTER_SESSION_CLOSE" if exit_time is None or exit_time > close else "N")
    if b <= a:
        out["mfe_mae_status"] = "DATA_MISSING (no trade between fill and exit)"
        return out
    hi, lo = float(p[a:b].max()), float(p[a:b].min())
    mfe = _ticks(hi - fill) if side > 0 else _ticks(fill - lo)
    mae = _ticks(fill - lo) if side > 0 else _ticks(hi - fill)
    out.update(mfe_mae_status="OK", mfe_ticks=mfe, mae_ticks=mae,
               mfe_R=round(mfe / st, 4) if st else None, mae_R=round(mae / st, 4) if st else None)
    return out


def after_stop(t: np.ndarray, p: np.ndarray, side: int, exit_reason: str, stop_time: dt.datetime, stop_fill: float,
               target: Optional[float], stop_ticks_fill: int, close: Optional[dt.datetime] = None) -> dict:
    out = dict(post_exit_timing="POST_EXIT")
    if "STOP" not in str(exit_reason).upper():
        out["post_exit_status"] = "NOT_APPLICABLE (not a stop exit)"
        return out
    end = stop_time + dt.timedelta(minutes=WINDOW_MIN)
    cut = close or S.session_close(stop_time.date())
    truncated = end > cut
    w_end = min(end, cut)
    a = np.searchsorted(t, np.datetime64(stop_time, "us"), side="right")      # (stop fill time, ...
    b = np.searchsorted(t, np.datetime64(w_end, "us"), side="right")          # ..., window end]
    out.update(post_exit_window_end=w_end, post_exit_truncated="TRUNCATED" if truncated else "N",
               post_exit_minutes_available=round(max((w_end - stop_time).total_seconds(), 0) / 60.0, 2))
    if b <= a:
        out["post_exit_status"] = "DATA_MISSING (no trade in the window)"
        return out
    w = p[a:b]
    move = _ticks(float(w.max()) - stop_fill) if side > 0 else _ticks(stop_fill - float(w.min()))
    hit = None if target is None else bool((w >= target).any() if side > 0 else (w <= target).any())
    out.update(post_exit_status="OK", post_exit_move_ticks=move,
               post_exit_move_R=round(move / stop_ticks_fill, 4) if stop_ticks_fill else None,
               post_exit_target_traded="DATA_MISSING (no target)" if hit is None else ("Y" if hit else "N"))
    return out


def entry_context(bar_end: np.ndarray, bar_o, bar_h, bar_l, bar_c, bar_vol, bar_delta, signal_time: dt.datetime,
                  decision_time: dt.datetime, fill_time: dt.datetime) -> dict:
    out = dict(entry_context_timing="AT_ENTRY",
               minutes_initiation_to_entry=round((fill_time - signal_time).total_seconds() / 60.0, 4))
    k = np.searchsorted(bar_end, np.datetime64(decision_time, "us"), side="left")
    if k >= len(bar_end) or bar_end[k] != np.datetime64(decision_time, "us"):
        out["confirm_bar_status"] = "DATA_MISSING (no bar closing at the decision)"
        return out
    vol = float(bar_vol[k])
    out.update(confirm_bar_status="OK", confirm_bar_end=decision_time, confirm_delta=float(bar_delta[k]),
               confirm_delta_pct=round(100.0 * float(bar_delta[k]) / vol, 4) if vol else None,
               confirm_range_ticks=_ticks(float(bar_h[k]) - float(bar_l[k])))
    return out


TRADE_KEYS = ("strategy", "trade_id", "session", "side", "signal_time", "decision_time", "fill_time", "fill", "stop", "target",
              "exit_time", "exit_fill", "exit_reason")


def compute(phase: str, trades, ticks_for, bars_for) -> list:
    """Review fields for every trade. Refuses every phase not in PHASES (phase2; phase3 from v1.2, Nov 8, 2026).

    trades     iterable of dicts with TRADE_KEYS: session (date), side (+1 / -1), the times as naive CT datetimes
               (exit_time None when the ledger has none), prices as floats (target None when the ledger has none);
    ticks_for  session -> (t, p): that session's trade times (np.datetime64[us], ascending) and prices;
    bars_for   session -> dict(end, o, h, l, c, vol, delta): that session's 1-minute bars (end = bar end time).
    Returns one dict per trade: strategy, trade_id, session, the session close used, then a), b) and c)."""
    if phase not in PHASES:
        raise RuntimeError(f"phase2_review_fields: computed in {PHASES} only, not in {phase!r}")
    out = []
    for x in trades:
        missing = [k for k in TRADE_KEYS if k not in x]
        if missing:
            raise KeyError(f"trade {x.get('trade_id')}: missing {missing}")
        d = x["session"]
        close = S.session_close(d)
        t, p = ticks_for(d)
        b = bars_for(d)
        row = dict(strategy=x["strategy"], trade_id=x["trade_id"], session=d.isoformat(), session_close=close, review_version=VERSION)
        row.update(mfe_mae(t, p, x["side"], x["fill_time"], x["fill"], x["exit_time"], x["stop"], close))
        if x["exit_time"] is None:
            row.update(post_exit_timing="POST_EXIT", post_exit_status="DATA_MISSING (no exit time in the ledger)")
        else:
            row.update(after_stop(t, p, x["side"], x["exit_reason"], x["exit_time"], x["exit_fill"], x["target"],
                                  row["stop_ticks_fill"], close))
        row.update(entry_context(b["end"], b["o"], b["h"], b["l"], b["c"], b["vol"], b["delta"], x["signal_time"],
                                 x["decision_time"], x["fill_time"]))
        out.append(row)
    return out
