"""Per-trade fields registered Nov 6, 2026 (Kyron, before Phase 2) for the Phase 2 what-fails-and-why review.

Logged only, every R1-R4 trade. Never an entry, exit, stop, target, size or rule input. Computed in Phase 2 only:
`compute()` refuses any phase other than "phase2", and nothing in the Phase 1 / 1b code calls it. Built and tested on
synthetic data only (book1a/tests/test_phase2_review_fields.py).

a) MFE / MAE (POST_ENTRY). From the actual entry fill price, over the tape's trades from the entry fill time to the exit
   fill time, both included. Long: MFE = highest trade - fill, MAE = fill - lowest trade; short: the mirror. In ticks and
   in R = ticks / stop_ticks, stop_ticks = |fill - stop| / 0.25 (as the ledger's stop_ticks).
b) After a stop exit (POST_EXIT). Window (stop fill time, stop fill time + 30 min] in clock time, cut at 15:00 CT.
   The largest move in the trade's direction from the stop fill price (long: highest trade - stop fill; short: stop
   fill - lowest trade; ticks and R; may be negative when every trade in the window is against the trade), and whether
   the original target traded in the window (long: a trade at or above the target; short: at or below). Cut at 15:00:
   TRUNCATED with the minutes available. No trade in the window: DATA_MISSING. Not a stop exit: NOT_APPLICABLE.
c) Entry context (AT_ENTRY). Minutes from initiation (the candidate's signal-bar close) to the entry fill; the confirm bar
   (the bar closing at the entry decision): delta (B volume - S / A volume), delta % (delta / bar volume x 100) and
   range (high - low) in ticks.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import numpy as np

VERSION = "phase2-review-fields-v1.0"
TICK = 0.25
WINDOW_MIN = 30
CUTOFF = dt.time(15, 0)


def _ticks(x: float) -> float:
    return round(x / TICK, 2)


def stop_ticks(fill: float, stop: float) -> int:
    return int(round(abs(fill - stop) / TICK))


def mfe_mae(t: np.ndarray, p: np.ndarray, side: int, fill_time: dt.datetime, fill: float, exit_time: dt.datetime,
            stop: float) -> dict:
    a = np.searchsorted(t, np.datetime64(fill_time, "us"), side="left")
    b = np.searchsorted(t, np.datetime64(exit_time, "us"), side="right")
    st = stop_ticks(fill, stop)
    out = dict(mfe_mae_timing="POST_ENTRY", mfe_mae_trades=int(b - a), stop_ticks_fill=st)
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
               target: Optional[float], stop_ticks_fill: int) -> dict:
    out = dict(post_exit_timing="POST_EXIT")
    if "STOP" not in str(exit_reason).upper():
        out["post_exit_status"] = "NOT_APPLICABLE (not a stop exit)"
        return out
    end = stop_time + dt.timedelta(minutes=WINDOW_MIN)
    cut = dt.datetime.combine(stop_time.date(), CUTOFF)
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


def compute(phase: str, *args, **kwargs):
    """Entry point for the Phase 2 run. Refuses every phase other than Phase 2 (registered: computed in Phase 2 only)."""
    if phase != "phase2":
        raise RuntimeError(f"phase2_review_fields: computed in Phase 2 only, not in {phase!r}")
    raise NotImplementedError("wired into the Phase 2 run only after Kyron authorizes Phase 2")
