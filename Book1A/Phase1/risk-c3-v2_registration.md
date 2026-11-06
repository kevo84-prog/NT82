# C3 risk check, implementation risk-c3-v2 (registration)

Decision: Kyron, Nov 5, 2026, Option B, versioned. Registered and committed before Phase 2 and before any existing
trade is evaluated against it. Written Nov 6, 2026.

## 1. Execution-breach definition (Phase 4 gate unchanged: fail on more than 1 qualifying breach)

- Entry risk at fill = (|filled entry - stop| / 0.25 + 2) x $5 x filled contracts + $5.74 x filled contracts.
  Computed in integer ticks and integer cents.
- Qualifying entry risk-budget breach: entry risk at fill > min($1,000, remaining daily budget at that decision).
  - The remaining daily budget comes from the sizing engine's own accounting (`risk.DayRiskState`), as it stood at
    the pre-trade check.
  - The current trade is not subtracted twice: its own reserve is not yet booked when the budget is read.
  - Exactly at the budget fits ($1,000.00 fits; $1,000.01 is a breach).
- Execution variance is logged on every trade: filled entry minus the pre-trade reference, in ticks, signed so that
  positive = adverse (long: fill above the ask at decision; short: fill below the bid at decision).
- Realized loss overrun (realized net loss larger than the planned estimate) is reported separately, in the existing
  `risk_breach_fill` column and the RISK_BREACH_FILL risk event. It never counts toward the gate.
- A breach is logged only. No automatic exit and no resize. A live response needs its own tested rule later.

## 2. Timing correction (C3)

- The pre-trade risk check and N use the best ask (long) / best bid (short) at the decision time as the entry
  reference, instead of the signal-bar reference (`EntryRef`, or the RH1 confirm close on the retest path).
- Decision time = the signal-bar close (the RH1 confirm-bar close on the retest path). The quote is the one that came
  with the last trade at or before that time (`fills.Tape.quote_at`): no look-ahead. The fill stays at the quote
  250 ms later (fill model v3.5, unchanged).
- Stop ticks = |reference - stop| / 0.25. The 2-tick allowance and every other U3 rule are unchanged ($1,000 per
  trade, $2,000 daily, NQ only, whole contracts, minimum 1 NQ, RISK_REJECT never shrunk, 3 trades, 2-loss halt).
- Guards (mechanical, no threshold):
  - no usable quote at the decision (bid / ask 0 or missing) -> RISK_REJECT:NO_QUOTE;
  - the reference at or beyond the stop -> RISK_REJECT:REF_AT_OR_PAST_STOP.
- Known limitation: partial fills are not modelled. Fill model v3.5 fills the whole order at one price, so
  "filled contracts" = N.

## 3. Version

- Implementation identifier: `risk-c3-v2` (`risk.C3_V2`). It is written into every R3 / R4 ledger row
  (`risk_impl_version`) and every R3 / R4 attempt row, and into each run manifest.
- The original implementation is `risk-c3-v1` (`risk.C3_V1`). It stays in the code, unchanged, so the Phase 0 and
  Phase 1 R3 / R4 ledgers can be reproduced byte for byte. A v1 run writes the original ledger layout (no new
  columns).
- The Phase 0 and Phase 1 R3 / R4 ledgers, hashes and parity reports are preserved unchanged. risk-c3-v2 runs go to
  new folders.
- Change-log entry: `book1a/Phase1/change_log.md` (material timing and sizing implementation correction).

## 4. New R3 / R4 ledger columns (risk-c3-v2 only)

| column | meaning |
|---|---|
| risk_impl_version | `risk-c3-v2` |
| risk_decision_time | decision time (bar close), CT |
| risk_ref_source | BEST_ASK (long) / BEST_BID (short) |
| risk_entry_ref | the reference price used for stop ticks and N |
| signal_entry_ref | the signal-bar reference v1 would have used (logged for comparison of mechanics only) |
| risk_budget_usd | min($1,000, remaining daily budget) at the decision |
| entry_risk_ticks_at_fill | abs(filled entry - stop) / 0.25 |
| entry_risk_at_fill_usd | entry risk at fill (section 1) |
| execution_variance_ticks | filled entry - reference, ticks, positive = adverse |
| exec_risk_breach | 1 = qualifying entry risk-budget breach (section 1), else 0 |

`planned_risk_usd` stays the pre-trade estimate. `risk_breach_fill` stays the realized loss overrun (not the gate).

## 5. Tests (before any historical run)

`book1a/tests/test_risk_c3_v2.py`: long and short; 1- and 2-tick adverse fills; exact budget boundary ($1,000.00
fits, $1,000.01 does not); N = 1, 2, 3, 5, 10; remaining daily budget below $1,000; one-position rule (no double
counting); breach logged with no exit or resize; v1 path unchanged.
