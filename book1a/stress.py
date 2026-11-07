"""Fill-model stress settings for the report card (replay plan 4a; registered for Phase 2 in Step A, Nov 6, 2026).

  base     entry 250 ms after the bar close, stop slippage 1 tick (fill model v3.5 as frozen)
  lat1000  entry 1,000 ms after the bar close, stop slippage 1 tick
  slip2    entry 250 ms, stop slippage 2 ticks
  slip4    entry 250 ms, stop slippage 4 ticks

Stop slippage is the replay's own stop_slip argument. The frozen Book 1 replay has no entry-latency argument:
jeron_engine.exit_replay.run_model calls exit_replay.replay without latency_ms (default bound to 250 at import),
and arm_replay / replay_risk stamp entry_time with fills.LATENCY_MS. entry_latency(ms) sets those three in memory
for the duration of the block (exit_replay.replay wrapped with latency_ms=ms, exit_replay.LATENCY_MS and
fills.LATENCY_MS = ms) and restores them afterwards. No Book 1 file is changed. Decision-time inputs (the
risk-c3-v2 quote at the bar close, the signal, the veto, the RH1 retest bars) do not depend on the entry latency.
"""
from __future__ import annotations

from contextlib import contextmanager

VERSION = "stress-v1.0"
SETTINGS = {"base": (250, 1), "lat1000": (1000, 1), "slip2": (250, 2), "slip4": (250, 4)}


@contextmanager
def entry_latency(ms: int):
    from jeron_engine import exit_replay as XR, fills
    orig, f0, x0 = XR.replay, fills.LATENCY_MS, XR.LATENCY_MS
    if ms == f0 == x0:
        yield
        return

    def replay(*a, **k):
        k.setdefault("latency_ms", ms)
        return orig(*a, **k)
    XR.replay, fills.LATENCY_MS, XR.LATENCY_MS = replay, ms, ms
    try:
        yield
    finally:
        XR.replay, fills.LATENCY_MS, XR.LATENCY_MS = orig, f0, x0
