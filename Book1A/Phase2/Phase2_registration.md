# Book 1A Phase 2 registration (first baseline, replay, in-sample)

Written Nov 6, 2026 (Step A), before any Phase 2 trading run. Kyron authorized Phase 2 on Nov 6, 2026; Phase 1 is
accepted (tag `book1a-phase1-pass` = `604faa8`). Nothing in this file comes from a Phase 2 result, and Phase 1
outcomes are not used for anything. Step B starts only after Kyron tags the commit that adds this file
`book1a-phase2-frozen`. The 21 sessions, their close times, exposure flags and input checks are in
`Book1A/Phase2/phase2_sessions.md`; the plan hashes are in `Book1A/Phase2/plan_hashes_phase2.md`.

## 1. Frozen configuration

| item | frozen value |
|---|---|
| Code | the commit that adds this file, tagged `book1a-phase2-frozen` by Kyron (parent `604faa8` = `book1a-phase1-pass`). Step B runs from a clean checkout of that tag: before each run `git status` must be clean and `git rev-parse HEAD` must equal the tag's commit (both recorded in the report); every run manifest records the commit. |
| Sessions | Nov 5 - Dec 4, 2025, Book 1 calendar: 21 sessions (no cash session Nov 27; Nov 28 half day included). 8 EXPOSED (Nov 17-21, Nov 24-26; replay plan section 8), 13 UNEXPOSED. |
| Inputs | `BOOK1_ROOT = K:\Book1A_inputs` only; harness `K:\Book1A_inputs\jeron_harness\build\JeronHarness.exe`; front contract NQZ5 ("NQ DEC25", NinjaTrader roll Dec 15, 2025) on all 21 sessions. |
| Plans | the 21 Book 1A plans built in Step A (`plan-v2.4-book1a-v1.6`, map v2.3 packets, frozen plan code), sha256 in `plan_hashes_phase2.md`. R4 loads exactly these files. |
| R1 A0 | unchanged from Phase 1: Book 1 S1.4 defaults, map v2.3, rules-only plan, no veto, exit M0, qty 1. `python -m book1a.run_r1_r2 --phase phase2 --fill v3.5 --block1 K:\Book1A_inputs --out book1a\Phase2\runs\phase2` |
| R2 C1 | unchanged: A0 + veto FZ1 or L1 or T8, RH1 retest 15 bars / 2 ticks, M0, qty 1 (same run). |
| R3 C1 + risk | unchanged: R2 signals + C3 risk check **risk-c3-v2** (`Phase1/risk-c3-v2_registration.md`). `python -m book1a.run_r3 --block1 K:\Book1A_inputs --a0-run book1a\Phase2\runs\phase2 --out book1a\Phase2\runs\phase2_r3` |
| R4 Book 1A | unchanged: Book 1A plans + S1.4, veto L1 or T8 (FZ1 logged only), RH1, exit **M0 fixed (E1)**, risk-c3-v2. `python -m book1a.run_r4 --block1 K:\Book1A_inputs --a0-run book1a\Phase2\runs\phase2 --plans book1a\Phase2\plans_phase2 --phase phase2 --out book1a\Phase2\runs\phase2_r4 --candidate-days <all 21>` |
| Fill model | **v3.5 for all four**: market entry 250 ms after the bar close at the best ask (long) / bid (short); target fills 1 tick through; stop fills 1 tick beyond the first traded price at or beyond the stop; same-tick stop and target = stop. |
| Costs | round trip NQ $5.74, MNQ $1.88 (MNQ only in the MNQ feasibility diagnostic). |
| U3 (R3, R4) | simulated balance $100,000; $1,000 per trade (1%); $2,000 daily loss limit; NQ only, whole contracts, minimum 1 NQ, a trade whose 1 NQ estimate exceeds the budget is RISK_REJECT, never shrunk; 2-tick slippage allowance in the pre-trade estimate only; 3 trades per day and the 2-loss halt. |
| Risk implementation | risk-c3-v2 for R3 and R4 (decision quote: best ask long / best bid short at the decision time; quote guards NO_QUOTE and REF_AT_OR_PAST_STOP). Written on every R3 / R4 ledger row. |
| Bootstrap | session bootstrap, seed **20251205** (section 2). |
| Stress | `book1a/stress.py` (stress-v1.0) and `python -m book1a.run_stress ... --stress lat1000 / slip2 / slip4 --out book1a\Phase2\runs\phase2_stress_<setting>`: the same replays on the same strategy logs with entry at 1,000 ms, or stop slippage 2 / 4 ticks. `--stress base` reproduces the four Phase 1 controlling ledgers byte for byte (checked Nov 6, 2026). |
| Review fields | `book1a/phase2_review_fields.py` (phase2-review-fields-v1.1), `compute("phase2", ...)` only. |
| Diagnostics | `python -m book1a.diag_phase1b --runs book1a\Phase2\runs --folders phase2 phase2_r3 phase2_r4 --d5-days --plans book1a\Phase2\plans_phase2 --gex K:\Book1A_inputs\gex_levels_block1.csv --inputs K:\Book1A_inputs --out book1a\Phase2\runs\phase2_diag` (diag-phase1b-v1.2; the D5 CVD video check is Phase 1 only). |
| G4 draw | `book1a/g4_draw.py` (g4-draw-v1.0), run unchanged in Step B (section 6, G4). |
| Labels | every result is "replay (in-sample)". Never "validation". |

Data condition registered before any result (inputs only, `phase2_sessions.md`): Databento marks Nov 28, 2025
"degraded". The CME outage left no data from Nov 27 20:44 CT to Nov 28 07:30 CT. Map v2.3 writes that gap into the
packets and, as frozen, leaves out the Nov 28 overnight / VWAP window and the weekly profile, and the prior-week
profile on Dec 1-4. The Nov 28 plan is review=LOG_ONLY (half day, check A, frozen rule). Nov 28 stays in both
populations (it is UNEXPOSED). It is not DATA_MISSING: every input file exists, and the gap is a real market outage.

Known behaviour registered before any result (frozen Book 1 code, not changed for Phase 2): on the Nov 28 half day
the tape ends at the 12:15 CT close and the replay's 14:55 flatten is never reached on that day. A position still open
at 12:15 is closed by the replay's FLATTEN branch at the last quote before the close (bid long / ask short of the last
Nov 28 tick), with its exit time stamped at the next tick in the tape (the Nov 30 17:00 CT session open). It is
reported as it comes out, flagged `EXIT_AFTER_SESSION_CLOSE` in the review fields, and every review measure stops at
12:15 (section 3). A change, if any, goes to the Phase 3 change list under (ii) only with Kyron's approval.

## 2. Report card (R1-R4)

Two populations, reported separately and **never pooled**: **ALL** = the 21 sessions; **UNEXPOSED** = the 13
UNEXPOSED sessions. Both are labelled "replay (in-sample)". UNEXPOSED means less exposed to prior analysis, not a
holdout, and is never called validation. Confidence intervals are descriptive uncertainty, not evidence of an edge.

Definitions (fixed now):

- **Trade R.** Realized net R = ledger `realized_net_R` = net USD / (stop_ticks x $5 x qty), net USD after the round
  trip commission ($5.74 x qty), the fill model and whole-contract size (R1 / R2 qty 1; R3 / R4 the risk-c3-v2 N).
  Theoretical R = ledger `theoretical_R` (price move / stop distance, before costs).
- **Session net R** = the sum of the session's trade realized net R; a session with no trade counts with 0. **Net R
  per session** = the mean over the population's sessions (denominator 21 or 13, zero-trade sessions included). The
  same for theoretical R. **Trades per session** = trades / 21 or 13.
- **90% session-bootstrap CI** of net R per session: B = 10,000 resamples of the population's sessions with
  replacement (n = 21 or 13, zero-trade sessions included), statistic = mean session net R; interval = the 5th and
  95th percentiles (numpy `percentile`, linear). A new `numpy.random.default_rng(20251205)` per strategy and
  population; the resample index matrix is drawn as `rng.integers(0, n, size=(10000, n))`.
- **Win rate** = trades with realized net R > 0 / trades (a trade at exactly 0 is neither win nor loss).
  **Average win R** = mean realized net R of trades > 0; **average loss R** = mean of trades < 0 (a negative number).
- **Max drawdown** = the largest fall of cumulative realized net R from its running peak, over trades ordered by
  (session, entry time), the peak starting at 0. In R for all four; also in dollars (cumulative net USD) for R3 / R4.
  UNEXPOSED: over the trades of those 13 sessions only, in the same order.
- **Exit-reason counts**: ledger `exit_reason` (TARGET_FIRST, STOP_FIRST, TIME_EXIT, other).
- **Risk counts (R3 / R4)**: RISK_REJECT count by reason (attempt rows with a RISK_REJECT reason); **execution
  breaches** (risk-c3-v2 EXEC_RISK_BREACH: entry risk at fill > min($1,000, remaining daily budget at the decision)),
  count and largest amount over the budget; **RISK_BREACH_FILL** = the realized loss overrun (ledger
  `risk_breach_fill`: realized net loss larger than the pre-trade estimate), count and largest dollar overrun. In the
  code RISK_BREACH_FILL and the realized overrun are the same event; it is reported once under both names.
- **Stress**: the report card's trades, net R per session, its 90% CI and max drawdown again from the stress ledgers:
  entry at 1,000 ms; stop slippage 2 ticks; stop slippage 4 ticks. The whole replay is rerun under each setting
  (risk and daily state included), so a stressed exit can change later decisions that day.
- **Gamma regime split**: the session's `regime` in `gex_levels_block1.csv` (positive / negative), plus "all". A
  session without valid GEX levels (V5) stays in "all" and is in neither regime group (counted). Per-session values
  in a regime group use that group's session count as denominator (zero-trade sessions included).
- **Time-of-day split**: by the trade's entry fill time (ledger `entry_time`, CT): 08:30-08:45, 08:45-10:00,
  10:00-13:00, after 13:00 (each bucket includes its start, excludes its end). Per bucket: trades, net R sum, net R per
  trade, win rate; net R per session = bucket net R / the population's session count.
- **Daily table**: every session of the population (session, trades, session net R), zero-trade sessions included.

Contents per strategy and population: trades; trades per session; net R per session (realized) and theoretical R per
session; the 90% session-bootstrap CI of net R per session; win rate; average win R and average loss R; max
drawdown (R; dollars for R3 / R4); exit-reason counts; RISK_REJECT count, execution breach count, RISK_BREACH_FILL
(realized overrun) count and the largest dollar overrun; stress at 1,000 ms and 2 / 4 ticks; the gamma regime and
time-of-day splits; the daily table.

## 3. What-fails-and-why review (R1-R4, every trade)

Fields per trade, from `phase2_review_fields.compute("phase2", ...)`: MFE / MAE (ticks and R, from the entry fill to
the exit fill); the post-stop window (largest move in the trade's direction from the stop fill, ticks and R; whether
the original target traded; TRUNCATED and minutes available); minutes from initiation (signal-bar close) to entry;
confirm-bar delta, delta % and range. Plus, from the diagnostics: mj_alignment, L1_PLAN_SIDE, market_context,
draw_status, the GEX tags (gamma_regime, hvl_side, cr_ps_width, pin_zone, pc_gamma_ratio) and the CVD tags (CVD_DIV
case and WITH / AGAINST at AT_ENTRY, PROVISIONAL and POST_ENTRY, kept separate; BREAKOUT_SPEED).

**Change registered before any Phase 2 result:** the post-stop window is (stop fill, stop fill + 30 min] cut at that
session's close from the Book 1 calendar (`sessions.session_close`: 15:00 CT on a full day; 12:15 CT on the Nov 28
half day, when CME equity futures close, per the calendar note "Cash ends 12:00 CT; CME equity futures close 12:15
CT"), not a fixed 15:00. TRUNCATED records the minutes available. Every POST_ENTRY / POST_EXIT measure uses only
prices inside the session: MFE / MAE stop at the earlier of the exit fill and the session close (a ledger exit after
the close is flagged `EXIT_AFTER_SESSION_CLOSE`). Unit tests: `tests/test_phase2_review_fields.py`
(TestSessionClose, TestHalfDayCut).

**Classification of each stopped trade** (exit_reason STOP_FIRST), the first rule that applies. The 1.0 R cut-off is
a prespecified descriptive threshold, not a trading or optimized threshold:

- a. **GAVE_BACK**: MFE >= 1.0 R before the stop (takes priority even if the target trades afterwards).
- b. **STOP_THEN_TARGET**: the original target traded within the post-stop window (truncated or not).
- c. **NO_POST_STOP_FOLLOW_THROUGH**: the window is complete (not TRUNCATED), the move in the trade's direction from
  the stop fill is < 1.0 R, and the target did not trade.
- d. **UNCLASSIFIED**: anything else, including a TRUNCATED window where (b) did not happen (and a window with no
  trade, DATA_MISSING).

R = ticks / stop ticks at the fill (|entry fill - stop| / 0.25). Trades that are not stopped are listed with their
fields and class NOT_STOPPED. Counts per class per strategy, and the tags of each class as counts: categorical tags
by value; the numeric GEX values (cr_ps_width, pc_gamma_ratio) by tercile of the 21 sessions' own values (cut-offs
from those values only, never outcomes). Descriptive only.

CVD_DIV is reported with this note: "fidelity to Jeron's CVD unproven (1 of 4 video examples reproduced;
CVD_video_check, Nov 6)". Strict swing divergence (CVD_DIV) is never mixed with any broader exhaustion / absorption
idea.

## 4. Section 5 diagnostics in Phase 2

| replay plan section 5 diagnostic | Phase 2 status | cause / note |
|---|---|---|
| C2 location arm, VWAP as a family vs VWAP as a tag only | NOT_RUN | not built: needs a second plan set with VWAP as a tag and an R4 rerun on it; no code exists |
| MAP4 high-volume areas vs MAP0 zones (AMT PO-6) | LOGGED_ONLY | MAP4 areas are in every plan sidecar; the comparison itself is not built |
| Exit steps M0 -> M-J1 -> M-J2 (R4 fixed at M0, E1) | RUN | M-J1 and M-J2 counterfactuals per trade (diag_exit_trades), with the v1.1 ladder source and mj_alignment |
| Exit steps M-J3, M-J4 | NOT_RUN | U5: deferred until objective triggers are specified |
| Quantower-style power trade vs S1.4 single print (C4) | LOGGED_ONLY | `power_trade_qt` logged per candidate (U2); not a gate, no comparison built |
| 10 NQ feasibility (hypothetical) | RUN | per trade (diag_sizing_trades), labelled hypothetical |
| MNQ feasibility (diagnostic only) | RUN | R3 / R4 RISK_REJECT attempts (diag_mnq_rejects) |
| L2 diagnostics and L2 terciles | NOT_RUN | the L2F audit, the fixed-price build and the coverage list are not done (U11) |
| E1 refill defense | NOT_RUN | L2F audit not done (U11) |
| E2 defense pulled before the touch | NOT_RUN | L2F audit not done (U11) |
| E4 book flip on the retest | NOT_RUN | L2F audit not done (U11), and E4's hold time N is not registered |
| Exit cue (a), absorption against the trade | RUN | per trade (diag_exit_trades), beside M0 |
| GEX V2 random-level twin | RUN | diag_gex_zones |
| GEX V3 second flip estimate | RUN | gex_v3 (reproduces the frozen levels row before use) |
| GEX V5 days without valid levels | RUN | counted; such days stay in the baseline and leave the GEX groups |
| Volatility control (ATM IV terciles) | RUN | POST_PHASE_GROUPING over the 21 sessions' atm_iv |
| Gamma regime and time-of-day splits; context GEX tags (hvl_side, cr_ps_width, pin_zone, pc_gamma_ratio) | RUN | section 2 and section 3 |
| CVD_DIV by case and WITH / AGAINST, AT_ENTRY / PROVISIONAL / POST_ENTRY separate | RUN | with the fidelity note (section 3) |
| CVD_DIV overlap with T8 and the passive trap tag | RUN | t8_overlap and trapped_passive per candidate |
| cvd_slope_5 by tercile | RUN | tercile cut-offs from the Phase 2 S1.4 candidate rows' own `log_cvd_slope_5` values (1/3 and 2/3 quantiles, numpy linear), never outcomes |
| Grade without CVD (counterfactual on R4) | NOT_RUN | the S1.4 grade is computed in the harness C# code; recomputing it needs a harness change |
| BREAKOUT_SPEED raw values | RUN | per candidate and trade |
| 08:30 vs 17:00 CT CVD reset | RUN | both series per swing |
| Swing pairs excluded by the 60-minute window | RUN | counted |
| Every logged tag (light proof, delta vs session, passive trap, first touch, side_conflict, draw_status, NEW_TARGET_NEEDED, ...) | RUN | logged tags reported with the trades they mark; descriptive |

Registered now: if L2 runs in a later phase, its tercile cut-offs come from Phase 2 candidates' feature values only,
never outcomes. E4's hold time N is not registered here, so **E4 is NOT_RUN** in Phase 2. L2 / E1 / E2 / E4 cannot run
in Phase 2 because the L2F audit is not done.

## 5. Phase 3 change list rule

The draft `Phase3_change_list.md` may contain only:

1. items already in replay plan section 5;
2. documented calculation or timing fixes, each with its reason;
3. values the plan says are frozen from Phase 2 (L2 terciles, E4 N).

No item is added, and none is dropped, because of a Phase 2 outcome. An item may be dropped only because it cannot
run (data or build missing). No threshold or rule changes from Phase 2 results. Kyron freezes the list (tag
`book1a-phase3-frozen`) before Phase 3.

## 6. Phase 2 gate (pass = all of G1-G5; performance is not a gate)

- **G1 Integrity**: run at the frozen commit; plan hashes unchanged from A2 (every R4 ledger and candidate row's
  `plan_sha256` equals `plan_hashes_phase2.md`, and the plans rebuilt from the Step B R1 run's own map packets are
  byte-identical to the A2 files); unit tests pass; look-ahead audit clean for R1-R4 (`book1a.audit_run` on each
  ledger) and for every AT_ENTRY field (the diagnostics' D2 timing audit); Phase 1 ledgers unchanged (the four
  controlling sha256: R1 `b4a2108fa2ab531ef84e1a2933d05fafb8e4519f6674ee8857f0cd79c344b21c`, R2
  `6123f88e7a62242b559e89a385b7749e67d6d2d433108cb839524a37c606842e`, R3
  `f413d15f4dad259d908390f6fcff659490f61cd5c9ce5a0f14a1bbeb486e71d1`, R4
  `b4510aabf2c750f6b3d0cb6f53de274989ed8acbc90d14c0dee9532a5ee5b409`).
- **G2 Coverage**: 21 / 21 sessions run for R1-R4. A missing session is either repaired and rerun, or accepted in
  writing by Kyron as a named coverage exception before the gate is decided. Documentation alone does not pass G2.
- **G3 Risk**: zero planned-risk violations for R3 / R4 (risk-c3-v2 definition: an accepted trade whose pre-trade
  estimate `planned_risk_usd` is above min($1,000, the remaining daily budget at the decision)); execution breaches
  reported.
- **G4 Checker reproduction**: the checker independently rebuilds, from the raw tape and the frozen specs with its
  own code (never the runner's implementation), every R4 trade on Nov 6, Nov 12, Nov 19 and Dec 3, 2025; plus 10 R4
  trades from the other 17 sessions and 10 trades from the R1-R3 ledgers, both drawn with seed 20251205 by
  `book1a/g4_draw.py` (committed in Step A, run unchanged in Step B; both draws always taken, whatever the trade
  counts on the fixed days); checking entry and exit time, price, reason, size and the risk-c3-v2 numbers, and
  recomputing the report card arithmetic from the ledgers. Pass = every field matches, or each mismatch is traced to
  a documented calculation error that is fixed, rerun and rechecked. Any unexplained mismatch fails G4.
- **G5 Deliverables complete and hashed**: report, ledgers, review file, Phase3_change_list draft.
