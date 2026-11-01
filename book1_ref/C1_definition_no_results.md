# C1: the frozen Book 1 strategy, rules only (no tables, no results)

Written Nov 1, 2026 by the Book 1A runner for the blind run. This file is the **only** C1 source the runner uses
from now on. It was assembled from the Book 1 code in this reference copy, which is the executable definition of
C1, and contains **no** result, trade count, R figure, drawdown figure or verdict. Where a Book 1 file mixes a rule
with a result (`FROZEN_STRATEGY.md`, docstrings in the phase scripts), only the rule is repeated here.

Source files (sha256 in `MANIFEST.md`):

| rule | file | lines |
|---|---|---|
| combination, order of application, fill model, stop slippage | `backtest/phase3/final_combination.py` | 3-9, 25, 70-77 |
| the same call on the holdout | `backtest/phase4/run_holdout.py` | 53-56 |
| vetoes FZ1, L1, T8; 1-minute bars | `jeron_engine/arms.py` | 1-16, 33-123 |
| A0 replay (selection, queueing, blocks, halts), RH1 retest path | `jeron_engine/arm_replay.py` | 1-30, 158-280 |
| exit M0 and fill model | `jeron_engine/exit_replay.py`, `jeron_engine/fills.py` | whole files |

## 1. What C1 is

**C1 = A0 + FZ1 + L1 + T8 + RH1**, replayed as one strategy with exit model **M0**, A0's plans (**MAP0**, the
rules-only plan from map v2.3 at 08:10 CT), **fill model v3.5**, **1 tick** of stop slippage (a 2-tick stop-slippage
line is run beside it as the stress check), **one contract** per trade.

It is a full replay of each day from A0's own strategy log (S1.4 in the harness): the candidate pool, shadows
included, is A0's log; candidate generation does not depend on position, trades, halts or the 3-trade limit.

Order of application inside the replay (`final_combination.py` 3-9; `arm_replay.replay`):

1. **Vetoes first.** A candidate (CANDIDATE or SHADOW row) that FZ1, L1 or T8 vetoes is removed from the pool
   **before** the per-bar selection, so a surviving shadow can win that bar. The veto is the union: any one of the
   three blocks the candidate.
2. **Per-bar selection and queueing as S1.4 does it** (`arm_replay.py` 7-13): on each bar and direction the best
   surviving candidate is kept; ranking = status rank (Qualified / AwaitConfirm / Pending 3, EventOnly 2, else 1), then
   location rank (frozen plan zone 4, power 3, qualified stack 2, minor stack 1), then reward:risk, then the earlier
   candidate. A winning Qualified candidate is queued at its bar; a winning AwaitConfirm candidate at its
   confirmation bar if the confirmation made it Qualified.
3. **Order attempt** at the first tick after the queueing bar, with every A0 block reason in the code's order: plan
   review, plan no-trade window, grade (allowed A+, B+, B), entry hours (08:30-15:00 CT, last entry before 14:30 CT),
   no target, max trades (the smaller of 3 and the plan's max_trades), halt (2-loss streak or 400-tick daily loss,
   from realized gross ticks), already in a trade, price past stop / target, and entry slippage at the decision tick
   (more than 12 ticks from the entry reference). A blocked attempt is logged and not traded.
4. **Entry path.** A surviving **RESPONSE** candidate with no block enters as in A0 (immediately: market order 250 ms
   after the signal bar close). A surviving **INITIATION** candidate with no block does **not** enter immediately: it
   goes through the **RH1 retest** (section 3); the trade slot is held while the retest is armed.
5. **Exit M0**, then the day's state (trades today, loss streak, daily P/L, halt) updates from the realized gross
   ticks when the exit time passes.

## 2. The three vetoes (`arms.py`)

Inputs are known at or before the signal bar. "Intraday zone" = LocationType starting with
`DEVELOPING_INTRADAY_IMB` or `DEVELOPING_INTRADAY_POWER`.

- **FZ1 (fresh zone must have held).** Vetoes an **INITIATION** candidate at an **intraday** zone that has not held.
  Held = a STATE row "Response" at that zone (LocationId) before the signal bar, with no "Failed" state at that zone
  after it and before the signal bar. Overnight Responses count. (Kyron's choices: (a) No, (b) Yes, as written in the
  arms.py docstring.)
- **L1 (intraday zones near the plan, 10 points).** Vetoes an **intraday** IMB / POWER candidate whose zone is more
  than **10.0 points** from every **DECISION** zone of that day's rules-only plan (`PreopenPlan_<date>.txt`, lines
  `zone=lo-hi|DECISION|...`). Distance = gap between nearest edges, 0 if they overlap; a day with no DECISION zone
  vetoes every intraday candidate. (5- and 20-point lines were report-only in Book 1; C1 uses 10.)
- **T8 (prior absorption).** Vetoes a candidate when any of the **3 completed 1-minute bars** before the signal bar
  has bar delta **in the trade's direction** and **closes against it** (close < open for a long, close > open for a
  short). Delta = aggressor-flagged volume from the strategy tape (B = +volume, S or A = -volume). Bars are built from
  the tape, stamped at their end, ticks in (T-1 min, T], 07:00-15:59 CT.

## 3. RH1 retest-and-hold (`arm_replay.retest_path`, frozen v2.5 values)

Constants: **RETEST_BARS = 15**, **TOUCH_TICKS = 2**, **STOP_BUFFER_TICKS = 2**, **fail_ticks = 2**, session end
15:00 CT, tick 0.25.

For an INITIATION candidate whose signal bar ends at t, with zone [lo, hi], direction d, near edge = hi (long) / lo
(short), far edge = the other edge, entry reference and stop anchor from the candidate row:

Scan the first 15 one-minute bars ending after t, in order. For each bar (open, high, low, close):

1. **Touch:** long, low <= near + 2 ticks; short, high >= near - 2 ticks. A touch arms phase 1 and records the
   retest extreme (lowest low for a long, highest high for a short, over all touching bars).
2. **Failed:** long, close < far - 2 ticks; short, close > far + 2 ticks. Outcome RETEST_FAILED; no trade.
3. **Confirm (phase 1 only):** long, close > near and close > open; short, close < near and close < open.
   Entry = that bar's close; **stop = retest extreme -/+ 2 ticks** (long: extreme - 2 ticks; short: extreme + 2
   ticks). If the candidate's target is already at or past the close, outcome NO_ROOM_TO_TARGET; no trade.
   Otherwise RETEST_ENTERED.
4. **Ran to target (phase 0 only):** long, high >= target; short, low <= target. Outcome RAN_TO_TARGET; no trade.
5. **Session end:** a bar ending at or after 15:00 CT ends the path (RETEST_NO_CONFIRM if touched, else
   SESSION_END_NO_RETEST).

After 15 bars without a decision: RETEST_NO_CONFIRM if touched; otherwise RAN_AWAY (if the candidate's own risk was
positive and the favourable excursion reached it) or NO_RETEST_WINDOW. None of these trades.

At RETEST_ENTERED the entry is re-checked at the first tick after the confirming bar: OUTSIDE_ENTRY_HOURS (at or
after 14:30 CT), PRICE_PAST_STOP (decision tick within 1 tick of or beyond the retest stop), PRICE_PAST_TARGET
(within 1 tick of or beyond the target), ENTRY_SLIPPAGE (decision tick more than 12 ticks from the confirm close).
Any of these blocks the trade. Otherwise the trade is a market entry 250 ms after the confirming bar's close, with
the retest stop and the candidate's original target, exit M0. The slot stays busy until the retest path ends.

## 4. Exit M0 and the fill model (`exit_replay.py`, `fills.py`)

- **M0:** one contract, one stop, one target (A0's, or the RH1 stop and A0's target on the retest path), the stop
  never moves, flatten at **14:55 CT**.
- **Entry:** market order at the signal bar close, filled **250 ms** later at the best ask (long) / best bid (short)
  known at that moment (the quote that came with the last trade at or before it).
- **Target:** limit; fills only when a trade prints **1 tick through** the target; fill price = target.
- **Stop:** stop-market; triggers when a trade prints at or through the stop. Fill price under **v3.5**: the first
  traded price at or beyond the stop, -/+ **1 tick** of slippage (2 ticks in the stress line). When that trade prints
  exactly at the stop this equals v3.4 (stop -/+ slip). v3.5's stop-change rules (250 ms delay, crossed-change
  policy) exist in the exit engine but never fire for M0 because its stop never moves.
- **Tie:** stop and target reached in the same timestamp = stop.
- **Flatten:** 14:55 CT at the bid (long) / ask (short).
- **Commission:** $2.87 per contract per side ($5.74 round turn = 1.148 NQ ticks).
- **R** per trade = net ticks / (contracts x planned risk ticks), planned risk = |entry fill - stop| / tick.

## 5. Sessions and fill model per Book 1 phase (inputs, not results)

| Book 1 phase | sessions | fill model the published A0 / C1 result used |
|---|---|---|
| Phase 1 | Oct 22 - Nov 4, 2025 | v3.4 (A0 only) |
| Phase 2 | Nov 5 - Dec 4, 2025 | v3.4 (A0 only) |
| Phase 3 | Dec 5, 2025 - Feb 4, 2026 (41 sessions) | v3.5 (A0 rerun under v3.5 for the pairing; C1) |
| Phase 4 holdout | Feb 5 - Apr 21, 2026 (52 sessions) | v3.5 (A0 and C1) |

Session calendar: weekdays; no cash session on Thanksgiving, Christmas, New Year's Day, MLK Day, Presidents' Day,
Good Friday; half days Nov 28 and Dec 24, 2025 included; NinjaTrader roll days Dec 15, 2025 and Mar 16, 2026.

## 6. Deliberately left out of this file

- Every number from the Phase 3 combination table and the Phase 4 holdout (trade counts, net R, per-session R,
  confidence bounds, drawdowns, verdicts), including the drawdown constant used by the Phase 4 decision rule and the
  per-arm figures quoted in the `final_combination.py` docstring (line 11). The checker holds them.
- The promotion and holdout decision rules themselves (they compare results and are the checker's business).
- C2, C3, C4 (the fallback combinations): not part of the frozen strategy.
