<!-- exported 2026-11-01T21:18Z from Google Doc 1qM9wZmipORAqati71DmK3Lzqe_y4Y_bU, modifiedTime 2026-10-26T11:18:34.624Z -->
# Fill model v3.5 (frozen for Phase 3)

**Informed by Phase 2, frozen before Phase 3.** Frozen by Kyron on Oct 25, 2026 (design v3.10, "What changed in v3.10"); tag `phase3-fill-v3.5`. Phase 3 uses it for A0 and every arm, and A0 is rerun under it for the pairing. Phases 0-2 results stay on v3.4. Drafted the same day from the Phase 2 exit first look (`backtest\phase2\exit_first_look\` v1, v2 and v3). Final cleanup the same day: rule 2 now uses live-equivalent timing (a decision check and an arrival check). (Fill model v3.5 is not design v3.5.)

## Why
v3.4 was written for A0, whose stop and target never move. Exit models that move the stop (M2E, M2, M3) hit two cases v3.4 does not cover:
1. **A stop moved to a level the market has already passed.** In Phase 2, 28 of the 49 stop moves M2E triggered were already crossed: 26 at the bar close and 2 more by the time a change sent then would arrive. Some were 50-160 ticks through. v3.4 still filled them at the new stop price, a price the market had left. With rules 1-3 below, M2E falls from +1.39 R to -1.97 R on the same 35 trades.
2. **Price jumping through a working stop.** v3.4 fills at stop -/+ slip even when the first trade at or beyond the stop is worse. On A0's fixed stops this changed 4 of 35 trades, by -0.05 R in total.

## Rules (additions to v3.4; everything else unchanged)
1. **Stop-change delay.** A stop change submitted at a bar close goes active **250 ms after that bar close** (the same latency as the entry). The previous stop keeps working until then, and can fill in that window.
2. **Crossed stop change (7a), PRIMARY policy: reject and keep** (decided by Kyron). Live-equivalent timing:
   - **Decision (at the bar close):** the strategy checks the current quote. If the new stop is already crossed (long: bid <= new stop; short: ask >= new stop), it **does not submit** the change. The old stop stays.
   - **Arrival (250 ms later):** a submitted change goes active. If it is crossed on arrival (same test, at that moment), it is **rejected and the old stop stays**.
   - The old stop works throughout. A later condition (for example a newer zone) may still move the stop.
   - **Why this policy:** it was named the primary policy before the v2 results, and it is how a correctly built trailing stop behaves live. It was **not** chosen because it scored better on Phase 2.
   - **REPORT-ONLY: market exit.** Same decision check as the primary (crossed at the bar close = not submitted). A submitted change crossed on arrival **exits at market** (bid for a long, ask for a short) at that moment. This matches today's S1.4 handling of a rejected protective order (see below). It is always reported beside the primary in Phase 3. It **cannot be promoted**, and it cannot replace the primary after Phase 3 results are seen.
3. **Gap through a working stop (7b).** A working stop, fixed or moved, fills at the **first traded price at or beyond the stop**, -/+ the stop slippage (base 1 tick; stress 2 and 4). When that trade prints exactly at the stop, this is the same as v3.4.
4. **Unchanged:** entry 250 ms after the signal bar close at the bid / ask; targets fill 1 tick through; same-timestamp tie = stop; flatten 14:55 CT; commission $2.87 per contract per side.

## Effect on Phase 2 (35 A0 entries; Phase 2 first look, not promotion evidence)
A0 rerun under v3.5 on Phase 2 (the reference for the Phase 3 pairing setup): -6.55 / -6.79 / -7.28 R at 1 / 2 / 4 ticks of stop slippage. Rule 3 changes 4 trades; rules 1-2 never apply to A0 (its stop never moves). The fills code (`fills.simulate(gap_fill=True)`, `daily_loop` with `fill_model: "v3.5"`) and the exit engine give the same A0 trade by trade (105 of 105). Source: `backtest\phase2\exit_first_look\v3\`.

| | v3.4 | v3.5 |
|---|---|---|
| A0 (M0) | -6.50 R | -6.55 R (rule 3 on 4 trades) |
| M2E | +1.39 R | -1.97 R (rules 1-3) |
| M2E vs M0, per session | +0.375 R | +0.218 R |
| M2E report-only market exit (same decision check; market exit on arrival) | | -3.46 R (+0.147 R per session). Superseded v2 figure (market exit on every crossed change): -4.34 R |

## What the live strategy does today (JeronOrderFlowStrategy S1.4; code not changed)
- It **never moves a stop after entry**. `SetStopLoss` is called once, before the entry (line 4788). Break-even and trailing exist only as logged exit models. So there is no price check before a stop change, because no change is ever made.
- `RealtimeErrorHandling = IgnoreAllErrors` (line 965). In `OnOrderUpdate` (lines 4877-4882), a rejected "Stop loss" or "Profit target" while in a position **flattens at market** ("PROTECT_FLAT") and logs PROTECTIVE_REJECTED.
- **Live condition (Kyron):** if M2E (or any stop-moving exit model) passes Phase 3, the live strategy must:
  - check the bid / ask before each stop move and not submit a crossed move;
  - treat a **rejected stop CHANGE** as "keep the old stop". Only a rejected protective **ORDER** (no working stop at all) flattens, as today's PROTECT_FLAT does.
  It is built and tested on the Sim account before any live use. No code change now.
  - Cost of not changing the rejected-change handling on Phase 2: +1.49 R (M2E primary -1.97 R minus report-only -3.46 R).

## Phase 3 use
- A0 and every arm run under v3.5 (`daily_loop` config `"fill_model": "v3.5"`; the exit engine with `gap_fill=True, stop_delay_ms=250, crossed="live"`). A0 is rerun under v3.5 for the pairing, so both sides use the same fill model.
- The stress cases are unchanged: stop slippage 2 and 4 ticks, entry latency 1,000 ms.
- Every stop-moving model reports the primary (reject and keep) and the report-only market-exit line side by side, with the number of moves not submitted at the decision and rejected on arrival.

