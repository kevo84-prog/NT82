# Book 1A – Phase 2 report (first baseline, replay, in-sample)

Runner: Claude Code desktop session, `K:\Book1A_runner\code`, branch `book1a-phase1`, Nov 7, 2026 (Step B, Kyron's go
of Nov 7). Controlling docs: `Book1A/Phase2/Phase2_registration.md` (frozen, tag `book1a-phase2-frozen` = `e1d37a1`)
and the Book 1A replay plan (`Book1A/specs/Book1A_replay_plan.md`), sections 2, 5, 6.

**Label: every number here is "replay (in-sample)".** UNEXPOSED is less exposed to prior analysis, not a holdout, and
is never validation. Confidence intervals are descriptive uncertainty, not evidence of an edge. Performance is not a
Phase 2 gate. ALL and UNEXPOSED are reported separately and never pooled. Phase 1 outcomes are not used; no Book 1
result was opened.

## 0. Status

- Runs: R1-R4, three stress settings and the diagnostics, all from `e1d37a1` with a clean tree; the section 3 review
  from `79ab4c0` (post-freeze reporting implementation amendment, below).
- Gates: **G1, G2, G3 met.** **G4 open** (the checker's reproduction; the sample and the pack are delivered).
  **G5 met** with this commit (report, ledgers, review file and change-list draft, all hashed; section 7 and
  `Phase2_deliverables_sha256.md`).
- Not done in Phase 2, as registered (section 5 table): C2 VWAP arm, M-J3 / M-J4, L2 and E1 / E2 / E4, grade without
  CVD. The MAP4 and power-trade comparisons are logged only.

## 1. Runs: code, status, inputs

Every run's HEAD and `git status` were recorded just before it ran (`book1a/Phase2/runs/stepB_head_*.txt`); every
run manifest records the commit.

| run | output folder (book1a/Phase2/runs/) | HEAD | git status | started (UTC) |
|---|---|---|---|---|
| R1 / R2 (`run_r1_r2 --phase phase2 --fill v3.5`) | phase2 | e1d37a1 | clean (porcelain output empty) | 2026-11-07 15:22:27 |
| R3 (`run_r3`) | phase2_r3 | e1d37a1 | clean (0 lines) | 15:27:37 |
| R4 (`run_r4 --phase phase2 --candidate-days <21>`) | phase2_r4 | e1d37a1 | clean | 15:28:19 |
| stress lat1000 / slip2 / slip4 (`run_stress`) | phase2_stress_<setting> | e1d37a1 | clean | 15:31:16 / 15:32:56 / 15:34:38 |
| diagnostics (`diag_phase1b`, diag-phase1b-v1.2) | phase2_diag | e1d37a1 | clean | 15:31:16 |
| G4 draw (`g4_draw`, g4-draw-v1.0, unchanged) | ../checker_input | e1d37a1 | clean | 15:46:21 |
| report card (`phase2_report`, phase2-report-v1.0) | phase2_report_card.json | e1d37a1 | clean | 15:46:37 |
| section 3 review (`phase2_review_apply`, phase2-review-apply-v1.1) | phase2_review | 79ab4c0 | clean | 18:58:55 |

Commands are the registered ones (registration section 1). All 21 registered sessions in every run. R1-R4 were run
once each and not rerun.

**Post-freeze reporting implementation amendment** (change log, Nov 7, 2026): the frozen commit had the section 3
functions but nothing that applied them to the ledgers. `phase2_review_apply.py` (v1.0 `c834fae`, v1.1 `79ab4c0`,
script sha256 LF `2dd021bfc19ef7e2e7792a772ab6057c64b37fc617792d3216206ad086303a37`) calls the frozen functions
unchanged and adds no rule; the checker verified both diffs against `e1d37a1` (only the script, its tests and the
change-log row). Kyron approved the v1.1 sources: the cr_ps_width tercile from one session value per session
(gex_levels_block1.csv through the frozen `diag_phase1b.gex_tags`) and `market_context_premarket` /
`draw_status_premarket` from the hashed Book 1A plan sidecars, labelled "premarket (plan), not the state at entry"
(the state at entry is NOT_RUN). Run once: 75 review rows = the 75 ledger trades, each once; the 42 input files'
sha256 equal before and after; overlap check empty for all four.

Execution code at `e1d37a1` is unchanged; nothing was fixed or rerun. The report tables were formatted from the
JSON / CSV outputs by `runs/report_build/build_phase2_report_md.py` (formatting only; sha256 in section 7).

Data condition and known behaviour (registered before any result, section 1): Nov 28 is "degraded" (CME outage) and
its plan is LOG_ONLY. No strategy traded on Nov 28, so no trade has `EXIT_AFTER_SESSION_CLOSE`. All 21 sessions have
valid GEX levels (no V5 session).

## 2. Report cards (R1-R4), registration section 2

R in realized net R (ledger `realized_net_R`); R1 / R2 qty 1, R3 / R4 risk-c3-v2 size; v3.5 fills; $5.74 round trip.
Max drawdown from a peak starting at 0 over trades in (session, entry time) order. Bootstrap: 10,000 session
resamples, seed 20251205, 5th / 95th percentile.


### 2.1 ALL (21 sessions), replay (in-sample)

|  | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| trades | 35 | 13 | 8 | 19 |
| trades per session | 1.667 | 0.619 | 0.381 | 0.905 |
| net R per session (realized) | -0.312 | 0.287 | 0.017 | 0.417 |
| 90% session-bootstrap CI | [-0.938, 0.361] | [-0.143, 0.790] | [-0.313, 0.484] | [-0.352, 1.273] |
| theoretical R per session | -0.294 | 0.294 | 0.023 | 0.432 |
| win rate | 0.257 | 0.538 | 0.375 | 0.421 |
| wins / losses / zero | 9 / 26 / 0 | 7 / 6 / 0 | 3 / 5 / 0 | 8 / 11 / 0 |
| average win R | 2.225 | 1.745 | 1.849 | 2.526 |
| average loss R | -1.022 | -1.033 | -1.038 | -1.042 |
| max drawdown R (trade order) | 12.263 | 3.111 | 4.152 | 6.222 |
| max drawdown USD (R3 / R4) | - | - | 3,813.14 | 5,492.58 |
| SUPPLEMENTAL: max drawdown R, session order | 11.191 | 2.093 | 4.152 | 6.222 |
| session dollar P&L, total (R1 / R2 at 1 NQ) | -4,160.90 | 7,410.38 | -839.06 | 6,714.48 |
| session dollar P&L per session | -198.14 | 352.88 | -39.96 | 319.74 |
| exit reasons | STOP_FIRST 26, TARGET_FIRST 9 | STOP_FIRST 6, TARGET_FIRST 6, TIME_EXIT 1 | STOP_FIRST 5, TARGET_FIRST 3 | STOP_FIRST 11, TARGET_FIRST 8 |
| RISK_REJECT count | - | - | 6 | 7 |
| execution breaches | - | - | 1 | 5 |
| largest execution breach over budget, USD | - | - | 222.96 | 222.96 |
| RISK_BREACH_FILL (realized overrun) count | - | - | 1 | 5 |
| largest realized overrun, USD | - | - | 300.00 | 300.00 |
| RISK_REJECT by reason | - | - | PER_TRADE_BUDGET 6 | PER_TRADE_BUDGET 7 |

Gamma regime split (ALL): trades / net R per session / net R per trade / win rate / net USD

| regime | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| all (21 sessions) | 35 / -0.312 / -0.187 / 0.257 / -4,160.90 | 13 / 0.287 / 0.463 / 0.538 / 7,410.38 | 8 / 0.017 / 0.045 / 0.375 / -839.06 | 19 / 0.417 / 0.461 / 0.421 / 6,714.48 |
| positive (14 sessions) | 27 / -0.396 / -0.205 / 0.259 / -3,199.98 | 12 / 0.301 / 0.351 / 0.500 / 5,221.12 | 8 / 0.026 / 0.045 / 0.375 / -839.06 | 13 / 0.265 / 0.286 / 0.308 / 2,896.88 |
| negative (7 sessions) | 8 / -0.144 / -0.126 / 0.250 / -960.92 | 1 / 0.257 / 1.802 / 1.000 / 2,189.26 | 0 / 0.000 / - / - / 0.00 | 6 / 0.719 / 0.839 / 0.667 / 3,817.60 |

Sessions without valid GEX levels (V5, in "all" only): 0 []

Time of day (ALL, entry fill time CT): trades / net R per session / net R per trade / win rate

| bucket | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 08:30-08:45 | 6 / -0.085 / -0.299 / 0.167 | 1 / -0.049 / -1.036 / 0.000 | 1 / -0.049 / -1.036 / 0.000 | 2 / 0.097 / 1.017 / 0.500 |
| 08:45-10:00 | 26 / -0.343 / -0.277 / 0.269 | 6 / 0.084 / 0.295 / 0.500 | 3 / -0.061 / -0.429 / 0.333 | 7 / -0.152 / -0.456 / 0.143 |
| 10:00-13:00 | 3 / 0.116 / 0.814 / 0.333 | 5 / 0.301 / 1.265 / 0.800 | 3 / 0.177 / 1.241 / 0.667 | 10 / 0.472 / 0.991 / 0.600 |
| 13:00+ | 0 / 0.000 / - / - | 1 / -0.049 / -1.039 / 0.000 | 1 / -0.049 / -1.039 / 0.000 | 0 / 0.000 / - / - |

Daily table (ALL): trades / session net R / session dollar P&L

| session | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 2025-11-05 | 2 / -2.072 / -626.48 | 1 / -1.041 / -270.74 | 1 / -1.041 / -812.22 | 2 / -2.078 / -1,714.44 |
| 2025-11-06 | 3 / -0.184 / 437.78 | 1 / 2.264 / 3,339.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-07 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-10 | 3 / 2.458 / 337.78 | 1 / -1.054 / -305.74 | 1 / -1.054 / -1,222.96 | 2 / -2.082 / -2,034.44 |
| 2025-11-11 | 2 / -2.062 / -776.48 | 1 / -1.039 / -285.74 | 1 / -1.039 / -857.22 | 2 / -2.062 / -1,743.70 |
| 2025-11-12 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / 3.046 / 2,528.52 |
| 2025-11-13 | 2 / -2.032 / -1,426.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-14 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.028 / -801.48 |
| 2025-11-17 | 2 / -2.038 / -1,436.48 | 2 / 0.780 / 1,083.52 | 1 / -1.017 / -920.74 | 2 / 2.316 / 2,561.30 |
| 2025-11-18 | 2 / -2.015 / -2,811.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 3 / 6.142 / 5,117.78 |
| 2025-11-19 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / -0.080 / -498.70 |
| 2025-11-20 | 1 / -1.009 / -1,175.74 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-21 | 2 / -2.035 / -2,131.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-24 | 3 / 4.054 / 5,157.78 | 1 / 1.802 / 2,189.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-25 | 3 / -0.652 / -397.22 | 2 / 4.777 / 1,658.52 | 2 / 4.777 / 3,317.04 | 0 / 0.000 / 0.00 |
| 2025-11-26 | 3 / 1.660 / 482.78 | 3 / -1.274 / -962.22 | 2 / -0.266 / -342.96 | 1 / -1.013 / -855.74 |
| 2025-11-28 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-01 | 2 / -2.040 / -1,321.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / 6.682 / 5,035.56 |
| 2025-12-02 | 2 / -2.030 / -1,766.48 | 1 / 0.803 / 964.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-03 | 3 / 3.451 / 3,292.78 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-04 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.093 / -880.18 |

### 2.2 UNEXPOSED (13 sessions), replay (in-sample)

|  | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| trades | 19 | 5 | 3 | 11 |
| trades per session | 1.462 | 0.385 | 0.231 | 0.846 |
| net R per session (realized) | -0.347 | -0.005 | -0.241 | 0.107 |
| 90% session-bootstrap CI | [-1.100, 0.452] | [-0.342, 0.392] | [-0.481, -0.080] | [-0.811, 1.251] |
| theoretical R per session | -0.328 | 0.000 | -0.236 | 0.124 |
| win rate | 0.211 | 0.400 | 0.000 | 0.273 |
| wins / losses / zero | 4 / 15 / 0 | 2 / 3 / 0 | 0 / 3 / 0 | 3 / 8 / 0 |
| average win R | 2.725 | 1.534 | - | 3.243 |
| average loss R | -1.027 | -1.045 | -1.045 | -1.043 |
| max drawdown R (trade order) | 9.236 | 2.093 | 3.135 | 6.222 |
| max drawdown USD (R3 / R4) | - | - | 2,892.40 | 5,492.58 |
| SUPPLEMENTAL: max drawdown R, session order | 8.164 | 2.093 | 3.135 | 6.222 |
| session dollar P&L, total (R1 / R2 at 1 NQ) | -1,849.06 | 3,441.30 | -2,892.40 | 389.84 |
| session dollar P&L per session | -142.24 | 264.72 | -222.49 | 29.99 |
| exit reasons | STOP_FIRST 15, TARGET_FIRST 4 | STOP_FIRST 3, TARGET_FIRST 1, TIME_EXIT 1 | STOP_FIRST 3 | STOP_FIRST 8, TARGET_FIRST 3 |
| RISK_REJECT count | - | - | 2 | 2 |
| execution breaches | - | - | 1 | 3 |
| largest execution breach over budget, USD | - | - | 222.96 | 222.96 |
| RISK_BREACH_FILL (realized overrun) count | - | - | 1 | 3 |
| largest realized overrun, USD | - | - | 300.00 | 300.00 |
| RISK_REJECT by reason | - | - | PER_TRADE_BUDGET 2 | PER_TRADE_BUDGET 2 |

Gamma regime split (UNEXPOSED): trades / net R per session / net R per trade / win rate / net USD

| regime | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| all (13 sessions) | 19 / -0.347 / -0.237 / 0.211 / -1,849.06 | 5 / -0.005 / -0.013 / 0.400 / 3,441.30 | 3 / -0.241 / -1.045 / 0.000 / -2,892.40 | 11 / 0.107 / 0.126 / 0.273 / 389.84 |
| positive (11 sessions) | 19 / -0.410 / -0.237 / 0.211 / -1,849.06 | 5 / -0.006 / -0.013 / 0.400 / 3,441.30 | 3 / -0.285 / -1.045 / 0.000 / -2,892.40 | 10 / 0.219 / 0.241 / 0.300 / 1,191.32 |
| negative (2 sessions) | 0 / 0.000 / - / - / 0.00 | 0 / 0.000 / - / - / 0.00 | 0 / 0.000 / - / - / 0.00 | 1 / -0.514 / -1.028 / 0.000 / -801.48 |

Sessions without valid GEX levels (V5, in "all" only): 0 []

Time of day (UNEXPOSED, entry fill time CT): trades / net R per session / net R per trade / win rate

| bucket | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 08:30-08:45 | 3 / -0.234 / -1.014 / 0.000 | 0 / 0.000 / - / - | 0 / 0.000 / - / - | 1 / 0.234 / 3.046 / 1.000 |
| 08:45-10:00 | 13 / -0.301 / -0.301 / 0.231 | 2 / 0.094 / 0.611 / 0.500 | 1 / -0.080 / -1.041 / 0.000 | 6 / -0.165 / -0.358 / 0.167 |
| 10:00-13:00 | 3 / 0.188 / 0.814 / 0.333 | 2 / -0.019 / -0.125 / 0.500 | 1 / -0.081 / -1.054 / 0.000 | 4 / 0.038 / 0.122 / 0.250 |
| 13:00+ | 0 / 0.000 / - / - | 1 / -0.080 / -1.039 / 0.000 | 1 / -0.080 / -1.039 / 0.000 | 0 / 0.000 / - / - |

Daily table (UNEXPOSED): trades / session net R / session dollar P&L

| session | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 2025-11-05 | 2 / -2.072 / -626.48 | 1 / -1.041 / -270.74 | 1 / -1.041 / -812.22 | 2 / -2.078 / -1,714.44 |
| 2025-11-06 | 3 / -0.184 / 437.78 | 1 / 2.264 / 3,339.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-07 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-10 | 3 / 2.458 / 337.78 | 1 / -1.054 / -305.74 | 1 / -1.054 / -1,222.96 | 2 / -2.082 / -2,034.44 |
| 2025-11-11 | 2 / -2.062 / -776.48 | 1 / -1.039 / -285.74 | 1 / -1.039 / -857.22 | 2 / -2.062 / -1,743.70 |
| 2025-11-12 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / 3.046 / 2,528.52 |
| 2025-11-13 | 2 / -2.032 / -1,426.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-11-14 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.028 / -801.48 |
| 2025-11-28 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-01 | 2 / -2.040 / -1,321.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / 6.682 / 5,035.56 |
| 2025-12-02 | 2 / -2.030 / -1,766.48 | 1 / 0.803 / 964.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-03 | 3 / 3.451 / 3,292.78 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-04 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.093 / -880.18 |

## 3. Stress (separate from the baseline)

The same report-card core from the stress ledgers: the whole replay rerun at entry 1,000 ms, or stop slippage 2 / 4 ticks (risk and daily state included). Baseline rows repeat section 2 for comparison.

ALL:

| strategy | setting | trades | net R per session | 90% CI | max DD R | max DD USD |
|---|---|---|---|---|---|---|
| R1 | baseline (v3.5) | 35 | -0.312 | [-0.938, 0.361] | 12.263 | - |
| R1 | lat1000 | 35 | -0.252 | [-0.928, 0.479] | 12.273 | - |
| R1 | slip2 | 35 | -0.323 | [-0.949, 0.349] | 12.378 | - |
| R1 | slip4 | 35 | -0.347 | [-0.975, 0.326] | 12.607 | - |
| R2 | baseline (v3.5) | 13 | 0.287 | [-0.143, 0.790] | 3.111 | - |
| R2 | lat1000 | 13 | 0.271 | [-0.165, 0.790] | 3.125 | - |
| R2 | slip2 | 13 | 0.283 | [-0.149, 0.788] | 3.152 | - |
| R2 | slip4 | 13 | 0.275 | [-0.161, 0.782] | 3.234 | - |
| R3 | baseline (v3.5) | 8 | 0.017 | [-0.313, 0.484] | 4.152 | 3,813.14 |
| R3 | lat1000 | 8 | 0.019 | [-0.324, 0.509] | 4.168 | 3,528.14 |
| R3 | slip2 | 8 | 0.013 | [-0.318, 0.481] | 4.212 | 3,868.14 |
| R3 | slip4 | 8 | 0.006 | [-0.330, 0.474] | 4.333 | 3,978.14 |
| R4 | baseline (v3.5) | 19 | 0.417 | [-0.352, 1.273] | 6.222 | 5,492.58 |
| R4 | lat1000 | 18 | 0.359 | [-0.439, 1.280] | 6.225 | 5,467.58 |
| R4 | slip2 | 19 | 0.408 | [-0.362, 1.267] | 6.317 | 5,166.84 |
| R4 | slip4 | 19 | 0.390 | [-0.384, 1.255] | 6.508 | 5,326.84 |

UNEXPOSED:

| strategy | setting | trades | net R per session | 90% CI | max DD R | max DD USD |
|---|---|---|---|---|---|---|
| R1 | baseline (v3.5) | 19 | -0.347 | [-1.100, 0.452] | 9.236 | - |
| R1 | lat1000 | 19 | -0.226 | [-1.043, 0.682] | 9.251 | - |
| R1 | slip2 | 19 | -0.361 | [-1.111, 0.435] | 9.342 | - |
| R1 | slip4 | 19 | -0.388 | [-1.139, 0.407] | 9.557 | - |
| R2 | baseline (v3.5) | 5 | -0.005 | [-0.342, 0.392] | 2.093 | - |
| R2 | lat1000 | 5 | 0.002 | [-0.344, 0.409] | 2.107 | - |
| R2 | slip2 | 5 | -0.009 | [-0.349, 0.391] | 2.129 | - |
| R2 | slip4 | 5 | -0.018 | [-0.362, 0.388] | 2.200 | - |
| R3 | baseline (v3.5) | 3 | -0.241 | [-0.481, -0.080] | 3.135 | 2,892.40 |
| R3 | lat1000 | 3 | -0.242 | [-0.483, -0.080] | 3.150 | 2,607.40 |
| R3 | slip2 | 3 | -0.245 | [-0.490, -0.081] | 3.189 | 2,942.40 |
| R3 | slip4 | 3 | -0.254 | [-0.507, -0.084] | 3.299 | 3,042.40 |
| R4 | baseline (v3.5) | 11 | 0.107 | [-0.811, 1.251] | 6.222 | 5,492.58 |
| R4 | lat1000 | 11 | 0.122 | [-0.865, 1.358] | 6.225 | 5,467.58 |
| R4 | slip2 | 11 | 0.095 | [-0.830, 1.240] | 6.317 | 5,166.84 |
| R4 | slip4 | 11 | 0.072 | [-0.871, 1.220] | 6.508 | 5,326.84 |


## 4. What fails and why (registration section 3), every trade

Stopped trades (exit_reason STOP_FIRST) are classed by the first rule that applies: GAVE_BACK (MFE >= 1.0 R before
the stop), STOP_THEN_TARGET (the original target traded in the post-stop window, truncated or not),
NO_POST_STOP_FOLLOW_THROUGH (window complete, move < 1.0 R, target not traded), UNCLASSIFIED (anything else,
including a truncated window without the target and a window with no trade). Other trades are NOT_STOPPED. The 1.0 R
cut-off is a prespecified descriptive threshold. Post-stop window: (stop fill, stop fill + 30 min], cut at the session
close. R = ticks / stop ticks at the fill. Descriptive only; replay (in-sample).

CVD_DIV: fidelity to Jeron's CVD unproven (1 of 4 video examples reproduced; CVD_video_check, Nov 6). AT_ENTRY,
PROVISIONAL and POST_ENTRY are kept separate; cvd17 = 17:00 CT reset, cvd0830 = 08:30 CT reset. Strict swing divergence
is not mixed with any broader exhaustion / absorption idea. BREAKOUT_SPEED raw values are listed per trade in
`phase2_review.csv` and not counted. L1_PLAN_SIDE exists only for R4 trades from an intraday zone admitted by L1
(10 R4 trades have no row: NA). market_context / draw_status are the premarket plan values, not the state at entry.


### 4.1 Class counts per strategy

ALL:

| class | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| GAVE_BACK | 5 | 2 | 2 | 6 |
| STOP_THEN_TARGET | 4 | 1 | 1 | 3 |
| NO_POST_STOP_FOLLOW_THROUGH | 9 | 0 | 0 | 0 |
| UNCLASSIFIED | 8 | 3 | 2 | 2 |
| NOT_STOPPED | 9 | 7 | 3 | 8 |

UNEXPOSED:

| class | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| GAVE_BACK | 4 | 0 | 0 | 3 |
| STOP_THEN_TARGET | 3 | 1 | 1 | 3 |
| NO_POST_STOP_FOLLOW_THROUGH | 5 | 0 | 0 | 0 |
| UNCLASSIFIED | 3 | 2 | 2 | 2 |
| NOT_STOPPED | 4 | 2 | 0 | 3 |

Tercile cut-offs (one set from the 21 sessions' own values, both populations): pc_gamma_ratio T1 <= 0.6660 < T2 <= 0.9958 < T3; cr_ps_width T1 <= 600.0000 < T2 <= 2,000.0000 < T3

### 4.2 Tag counts per class, ALL (value count; NA = no diagnostics row or field)

R1:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 1; positive 4 | negative 1; positive 3 | negative 2; positive 7 | negative 2; positive 6 | negative 2; positive 7 |
| hvl_side | ABOVE 2; BELOW 3 | ABOVE 2; BELOW 2 | ABOVE 2; BELOW 7 | ABOVE 6; BELOW 2 | ABOVE 5; BELOW 4 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 5 | NOT_APPLICABLE (before 13:00 CT) 4 | NOT_APPLICABLE (before 13:00 CT) 9 | NOT_APPLICABLE (before 13:00 CT) 8 | NOT_APPLICABLE (before 13:00 CT) 9 |
| pc_gamma_ratio_tercile | T1 1; T2 3; T3 1 | T1 2; T2 1; T3 1 | T1 2; T2 5; T3 2 | T1 1; T2 5; T3 2 | T1 4; T2 3; T3 2 |
| cr_ps_width_tercile | T1 2; T2 2; T3 1 | T2 3; T3 1 | T1 5; T2 3; T3 1 | T1 3; T2 4; T3 1 | T1 6; T2 2; T3 1 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 5 | NOT_APPLICABLE (A0 plans carry no ladder) 4 | NOT_APPLICABLE (A0 plans carry no ladder) 9 | NOT_APPLICABLE (A0 plans carry no ladder) 8 | NOT_APPLICABLE (A0 plans carry no ladder) 9 |
| L1_PLAN_SIDE | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |
| market_context_premarket | BALANCED 1; BEARISH 3; NONE 1 | BEARISH 3; NONE 1 | BALANCED 2; BEARISH 2; BULLISH 2; NONE 3 | BALANCED 2; BULLISH 5; NONE 1 | BALANCED 2; BEARISH 1; BULLISH 5; NONE 1 |
| draw_status_premarket | ACTIVE 3; NONE 2 | ACTIVE 3; NONE 1 | ACTIVE 4; NONE 5 | ACTIVE 5; NONE 3 | ACTIVE 6; NONE 3 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 2; NONE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 6 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 2; NONE 2; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 4; NOT_AT_LOCATION 3 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 6 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_APPLICABLE 4; NOT_AT_LOCATION 3 |
| atentry_high_with_cvd17 | NA 5 | NA 4 | NA 8; WITH 1 | AGAINST 1; NA 6; WITH 1 | NA 9 |
| atentry_high_with_cvd0830 | NA 5 | NA 4 | NA 8; WITH 1 | NA 7; WITH 1 | NA 9 |
| atentry_low_case_cvd17 | LOW_ABSORPTION 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 6 | EXCLUDED_60MIN 2; LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 3 | NONE 2; NOT_AT_LOCATION 7 |
| atentry_low_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 4 | NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 6 | EXCLUDED_60MIN 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 3 | NOT_APPLICABLE 2; NOT_AT_LOCATION 7 |
| atentry_low_with_cvd17 | NA 4; WITH 1 | NA 4 | NA 8; WITH 1 | NA 6; WITH 2 | NA 9 |
| atentry_low_with_cvd0830 | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |
| prov_high_case_cvd17 | NONE 2; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 8 | HIGH_EXHAUSTION 1; NONE 3; NOT_AT_LOCATION 4 | NONE 5; NOT_AT_LOCATION 4 |
| prov_high_case_cvd0830 | NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 8 | HIGH_EXHAUSTION 1; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 4 | NONE 4; NOT_APPLICABLE 1; NOT_AT_LOCATION 4 |
| prov_high_with_cvd17 | NA 5 | NA 4 | NA 9 | NA 7; WITH 1 | NA 9 |
| prov_high_with_cvd0830 | NA 5 | NA 4 | NA 9 | NA 7; WITH 1 | NA 9 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 2; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 3; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | NONE 1; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 7 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 3 | NOT_APPLICABLE 1; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 7 |
| prov_low_with_cvd17 | NA 4; WITH 1 | NA 4 | NA 9 | NA 8 | NA 9 |
| prov_low_with_cvd0830 | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 3 | NOT_APPLICABLE 4 | EXCLUDED_60MIN 1; NOT_APPLICABLE 6; NOT_AT_LOCATION 2 | NONE 1; NOT_APPLICABLE 5; NOT_AT_LOCATION 2 | NONE 2; NOT_APPLICABLE 6; NOT_AT_LOCATION 1 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 3 | NOT_APPLICABLE 4 | EXCLUDED_60MIN 1; NOT_APPLICABLE 6; NOT_AT_LOCATION 2 | NOT_APPLICABLE 6; NOT_AT_LOCATION 2 | NONE 1; NOT_APPLICABLE 7; NOT_AT_LOCATION 1 |
| post_high_with_cvd17 | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |
| post_high_with_cvd0830 | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 4 | NOT_APPLICABLE 9 | NOT_APPLICABLE 8 | EXCLUDED_60MIN 2; NOT_APPLICABLE 5; NOT_AT_LOCATION 2 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 4 | NOT_APPLICABLE 9 | NOT_APPLICABLE 8 | EXCLUDED_60MIN 2; NOT_APPLICABLE 5; NOT_AT_LOCATION 2 |
| post_low_with_cvd17 | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |
| post_low_with_cvd0830 | NA 5 | NA 4 | NA 9 | NA 8 | NA 9 |

R2:

| tag | GAVE_BACK | STOP_THEN_TARGET | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|
| gamma_regime | positive 2 | positive 1 | positive 3 | negative 1; positive 6 |
| hvl_side | ABOVE 2 | ABOVE 1 | ABOVE 2; BELOW 1 | ABOVE 5; BELOW 2 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 1 | N 1; NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 7 |
| pc_gamma_ratio_tercile | T1 1; T2 1 | T2 1 | T1 1; T2 2 | T1 1; T2 5; T3 1 |
| cr_ps_width_tercile | T1 1; T2 1 | T3 1 | T1 2; T3 1 | T1 5; T2 2 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 3 | NOT_APPLICABLE (A0 plans carry no ladder) 7 |
| L1_PLAN_SIDE | NA 2 | NA 1 | NA 3 | NA 7 |
| market_context_premarket | BALANCED 1; BULLISH 1 | NONE 1 | BALANCED 1; BULLISH 1; NONE 1 | BALANCED 1; BEARISH 1; BULLISH 5 |
| draw_status_premarket | ACTIVE 1; NONE 1 | NONE 1 | ACTIVE 1; NONE 2 | ACTIVE 6; NONE 1 |
| atentry_high_case_cvd17 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1 | NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 3; NOT_AT_LOCATION 2 |
| atentry_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1 | NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 |
| atentry_high_with_cvd17 | NA 1; WITH 1 | NA 1 | NA 3 | NA 7 |
| atentry_high_with_cvd0830 | NA 2 | NA 1 | NA 3 | NA 7 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 1; NONE 1 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 7 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 7 |
| atentry_low_with_cvd17 | NA 2 | NA 1 | NA 3 | NA 7 |
| atentry_low_with_cvd0830 | NA 2 | NA 1 | NA 3 | NA 7 |
| prov_high_case_cvd17 | NONE 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 6 |
| prov_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 6 |
| prov_high_with_cvd17 | NA 2 | NA 1 | NA 2; WITH 1 | NA 7 |
| prov_high_with_cvd0830 | NA 2 | NA 1 | NA 2; WITH 1 | NA 7 |
| prov_low_case_cvd17 | NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 5 |
| prov_low_case_cvd0830 | NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 5 |
| prov_low_with_cvd17 | NA 2 | NA 1 | NA 2; WITH 1 | NA 7 |
| prov_low_with_cvd0830 | NA 2 | NA 1 | NA 2; WITH 1 | NA 7 |
| post_high_case_cvd17 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NONE 1; NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 2 |
| post_high_case_cvd0830 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NONE 1; NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 2 |
| post_high_with_cvd17 | NA 2 | NA 1 | NA 3 | NA 7 |
| post_high_with_cvd0830 | NA 2 | NA 1 | NA 3 | NA 7 |
| post_low_case_cvd17 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 2 |
| post_low_case_cvd0830 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 2 |
| post_low_with_cvd17 | NA 2 | NA 1 | NA 3 | NA 7 |
| post_low_with_cvd0830 | NA 2 | NA 1 | NA 3 | NA 7 |

R3:

| tag | GAVE_BACK | STOP_THEN_TARGET | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|
| gamma_regime | positive 2 | positive 1 | positive 2 | positive 3 |
| hvl_side | ABOVE 2 | ABOVE 1 | ABOVE 1; BELOW 1 | ABOVE 3 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 1 | N 1; NOT_APPLICABLE (before 13:00 CT) 1 | NOT_APPLICABLE (before 13:00 CT) 3 |
| pc_gamma_ratio_tercile | T1 1; T2 1 | T2 1 | T2 2 | T1 1; T2 2 |
| cr_ps_width_tercile | T1 1; T2 1 | T3 1 | T1 1; T3 1 | T1 3 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 3 |
| L1_PLAN_SIDE | NA 2 | NA 1 | NA 2 | NA 3 |
| market_context_premarket | BALANCED 1; BULLISH 1 | NONE 1 | BALANCED 1; NONE 1 | BULLISH 3 |
| draw_status_premarket | ACTIVE 1; NONE 1 | NONE 1 | NONE 2 | ACTIVE 3 |
| atentry_high_case_cvd17 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | NONE 1; NOT_AT_LOCATION 2 |
| atentry_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | NOT_APPLICABLE 1; NOT_AT_LOCATION 2 |
| atentry_high_with_cvd17 | NA 1; WITH 1 | NA 1 | NA 2 | NA 3 |
| atentry_high_with_cvd0830 | NA 2 | NA 1 | NA 2 | NA 3 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 1; NONE 1 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| atentry_low_with_cvd17 | NA 2 | NA 1 | NA 2 | NA 3 |
| atentry_low_with_cvd0830 | NA 2 | NA 1 | NA 2 | NA 3 |
| prov_high_case_cvd17 | NONE 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 2 |
| prov_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 2 |
| prov_high_with_cvd17 | NA 2 | NA 1 | NA 1; WITH 1 | NA 3 |
| prov_high_with_cvd0830 | NA 2 | NA 1 | NA 1; WITH 1 | NA 3 |
| prov_low_case_cvd17 | NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| prov_low_case_cvd0830 | NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| prov_low_with_cvd17 | NA 2 | NA 1 | NA 1; WITH 1 | NA 3 |
| prov_low_with_cvd0830 | NA 2 | NA 1 | NA 1; WITH 1 | NA 3 |
| post_high_case_cvd17 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_high_case_cvd0830 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_high_with_cvd17 | NA 2 | NA 1 | NA 2 | NA 3 |
| post_high_with_cvd0830 | NA 2 | NA 1 | NA 2 | NA 3 |
| post_low_case_cvd17 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | NOT_APPLICABLE 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 2 | NA 1 | NA 2 | NA 3 |
| post_low_with_cvd0830 | NA 2 | NA 1 | NA 2 | NA 3 |

R4:

| tag | GAVE_BACK | STOP_THEN_TARGET | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|
| gamma_regime | negative 1; positive 5 | positive 3 | negative 1; positive 1 | negative 4; positive 4 |
| hvl_side | ABOVE 3; BELOW 3 | ABOVE 2; BELOW 1 | BELOW 2 | ABOVE 4; BELOW 4 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 6 | NOT_APPLICABLE (before 13:00 CT) 3 | NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 8 |
| pc_gamma_ratio_tercile | T1 2; T2 3; T3 1 | T2 3 | T2 1; T3 1 | T1 3; T2 1; T3 4 |
| cr_ps_width_tercile | T1 4; T2 2 | T3 3 | T2 1; T3 1 | T2 8 |
| mj_alignment | EXPLORATORY_NOT_PLAN_ALIGNED 4; NOT_APPLICABLE (plan-zone trade) 1; PLAN_ALIGNED 1 | NOT_APPLICABLE (plan-zone trade) 3 | NOT_APPLICABLE (not a plan zone and not admitted by L1) 1; PLAN_ALIGNED 1 | EXPLORATORY_NOT_PLAN_ALIGNED 2; NOT_APPLICABLE (plan-zone trade) 5; PLAN_ALIGNED 1 |
| L1_PLAN_SIDE | ALLOWED 1; NA 1; NONE 4 | NA 3 | ALLOWED 1; NA 1 | ALLOWED 1; NA 5; NONE 2 |
| market_context_premarket | BALANCED 3; BULLISH 3 | NONE 3 | BEARISH 1; NONE 1 | BALANCED 1; BEARISH 2; BULLISH 1; NONE 4 |
| draw_status_premarket | ACTIVE 2; NONE 4 | NONE 3 | ACTIVE 1; NONE 1 | ACTIVE 3; NONE 5 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | HIGH_ABSORPTION 1; NOT_AT_LOCATION 7 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | HIGH_ABSORPTION 1; NOT_AT_LOCATION 7 |
| atentry_high_with_cvd17 | AGAINST 2; NA 4 | NA 3 | NA 2 | AGAINST 1; NA 7 |
| atentry_high_with_cvd0830 | AGAINST 1; NA 5 | NA 3 | NA 2 | AGAINST 1; NA 7 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 2; LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 5 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 5 |
| atentry_low_with_cvd17 | AGAINST 2; NA 4 | NA 3 | AGAINST 1; NA 1 | AGAINST 1; NA 7 |
| atentry_low_with_cvd0830 | NA 6 | NA 3 | NA 2 | AGAINST 1; NA 7 |
| prov_high_case_cvd17 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 2; NOT_AT_LOCATION 2 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 2 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 7 |
| prov_high_case_cvd0830 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 2 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 7 |
| prov_high_with_cvd17 | AGAINST 1; NA 5 | NA 2; WITH 1 | AGAINST 1; NA 1 | NA 8 |
| prov_high_with_cvd0830 | AGAINST 1; NA 5 | NA 2; WITH 1 | AGAINST 1; NA 1 | NA 8 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 3 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; LOW_EXHAUSTION 1; NOT_AT_LOCATION 5 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 3 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; LOW_EXHAUSTION 1; NOT_AT_LOCATION 5 |
| prov_low_with_cvd17 | AGAINST 1; NA 5 | NA 3 | NA 2 | AGAINST 1; NA 7 |
| prov_low_with_cvd0830 | NA 6 | NA 3 | NA 2 | AGAINST 1; NA 7 |
| post_high_case_cvd17 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 3 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5; NOT_AT_LOCATION 2 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 4 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5; NOT_AT_LOCATION 2 |
| post_high_with_cvd17 | NA 6 | NA 3 | NA 2 | NA 8 |
| post_high_with_cvd0830 | NA 6 | NA 3 | NA 2 | NA 8 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 1 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 3 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 1 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 3 |
| post_low_with_cvd17 | NA 6 | NA 3 | NA 2 | NA 8 |
| post_low_with_cvd0830 | NA 6 | NA 3 | NA 2 | NA 8 |

### 4.3 Tag counts per class, UNEXPOSED (value count; NA = no diagnostics row or field)

R1:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | positive 4 | positive 3 | positive 5 | positive 3 | positive 4 |
| hvl_side | ABOVE 2; BELOW 2 | ABOVE 2; BELOW 1 | ABOVE 1; BELOW 4 | ABOVE 2; BELOW 1 | ABOVE 3; BELOW 1 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 4 | NOT_APPLICABLE (before 13:00 CT) 3 | NOT_APPLICABLE (before 13:00 CT) 5 | NOT_APPLICABLE (before 13:00 CT) 3 | NOT_APPLICABLE (before 13:00 CT) 4 |
| pc_gamma_ratio_tercile | T1 1; T2 3 | T1 2; T2 1 | T1 2; T2 3 | T2 3 | T1 2; T2 2 |
| cr_ps_width_tercile | T1 2; T2 1; T3 1 | T2 2; T3 1 | T1 3; T2 1; T3 1 | T1 2; T3 1 | T1 3; T3 1 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 4 | NOT_APPLICABLE (A0 plans carry no ladder) 3 | NOT_APPLICABLE (A0 plans carry no ladder) 5 | NOT_APPLICABLE (A0 plans carry no ladder) 3 | NOT_APPLICABLE (A0 plans carry no ladder) 4 |
| L1_PLAN_SIDE | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |
| market_context_premarket | BALANCED 1; BEARISH 2; NONE 1 | BEARISH 2; NONE 1 | BALANCED 2; BEARISH 2; NONE 1 | BULLISH 2; NONE 1 | BALANCED 2; BEARISH 1; NONE 1 |
| draw_status_premarket | ACTIVE 2; NONE 2 | ACTIVE 2; NONE 1 | ACTIVE 2; NONE 3 | ACTIVE 2; NONE 1 | ACTIVE 1; NONE 3 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 2; NONE 2 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 3 | HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 2 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 3 | HIGH_EXHAUSTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 2 |
| atentry_high_with_cvd17 | NA 4 | NA 3 | NA 4; WITH 1 | NA 2; WITH 1 | NA 4 |
| atentry_high_with_cvd0830 | NA 4 | NA 3 | NA 4; WITH 1 | NA 2; WITH 1 | NA 4 |
| atentry_low_case_cvd17 | LOW_ABSORPTION 1; NOT_AT_LOCATION 3 | NONE 1; NOT_AT_LOCATION 2 | LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | NONE 1; NOT_AT_LOCATION 3 |
| atentry_low_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1; NOT_AT_LOCATION 3 |
| atentry_low_with_cvd17 | NA 3; WITH 1 | NA 3 | NA 4; WITH 1 | NA 3 | NA 4 |
| atentry_low_with_cvd0830 | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |
| prov_high_case_cvd17 | NONE 1; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 4 | HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 3 |
| prov_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 4 | HIGH_EXHAUSTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 3 |
| prov_high_with_cvd17 | NA 4 | NA 3 | NA 5 | NA 2; WITH 1 | NA 4 |
| prov_high_with_cvd0830 | NA 4 | NA 3 | NA 5 | NA 2; WITH 1 | NA 4 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 3 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 3 |
| prov_low_with_cvd17 | NA 3; WITH 1 | NA 3 | NA 5 | NA 3 | NA 4 |
| prov_low_with_cvd0830 | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3 | NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3 | NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 |
| post_high_with_cvd17 | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |
| post_high_with_cvd0830 | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |
| post_low_case_cvd17 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 3 | NOT_APPLICABLE 5 | NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 3 | NOT_APPLICABLE 5 | NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |
| post_low_with_cvd0830 | NA 4 | NA 3 | NA 5 | NA 3 | NA 4 |

R2:

| tag | STOP_THEN_TARGET | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|
| gamma_regime | positive 1 | positive 2 | positive 2 |
| hvl_side | ABOVE 1 | ABOVE 1; BELOW 1 | ABOVE 1; BELOW 1 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 1 | N 1; NOT_APPLICABLE (before 13:00 CT) 1 | NOT_APPLICABLE (before 13:00 CT) 2 |
| pc_gamma_ratio_tercile | T2 1 | T2 2 | T2 2 |
| cr_ps_width_tercile | T3 1 | T1 1; T3 1 | T1 2 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 2 |
| L1_PLAN_SIDE | NA 1 | NA 2 | NA 2 |
| market_context_premarket | NONE 1 | BALANCED 1; NONE 1 | BEARISH 1; BULLISH 1 |
| draw_status_premarket | NONE 1 | NONE 2 | ACTIVE 2 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1 |
| atentry_high_with_cvd17 | NA 1 | NA 2 | NA 2 |
| atentry_high_with_cvd0830 | NA 1 | NA 2 | NA 2 |
| atentry_low_case_cvd17 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 |
| atentry_low_case_cvd0830 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 |
| atentry_low_with_cvd17 | NA 1 | NA 2 | NA 2 |
| atentry_low_with_cvd0830 | NA 1 | NA 2 | NA 2 |
| prov_high_case_cvd17 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 |
| prov_high_case_cvd0830 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 |
| prov_high_with_cvd17 | NA 1 | NA 1; WITH 1 | NA 2 |
| prov_high_with_cvd0830 | NA 1 | NA 1; WITH 1 | NA 2 |
| prov_low_case_cvd17 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 |
| prov_low_case_cvd0830 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 |
| prov_low_with_cvd17 | NA 1 | NA 1; WITH 1 | NA 2 |
| prov_low_with_cvd0830 | NA 1 | NA 1; WITH 1 | NA 2 |
| post_high_case_cvd17 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 |
| post_high_case_cvd0830 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 |
| post_high_with_cvd17 | NA 1 | NA 2 | NA 2 |
| post_high_with_cvd0830 | NA 1 | NA 2 | NA 2 |
| post_low_case_cvd17 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 |
| post_low_case_cvd0830 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 |
| post_low_with_cvd17 | NA 1 | NA 2 | NA 2 |
| post_low_with_cvd0830 | NA 1 | NA 2 | NA 2 |

R3:

| tag | STOP_THEN_TARGET | UNCLASSIFIED |
|---|---|---|
| gamma_regime | positive 1 | positive 2 |
| hvl_side | ABOVE 1 | ABOVE 1; BELOW 1 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 1 | N 1; NOT_APPLICABLE (before 13:00 CT) 1 |
| pc_gamma_ratio_tercile | T2 1 | T2 2 |
| cr_ps_width_tercile | T3 1 | T1 1; T3 1 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 2 |
| L1_PLAN_SIDE | NA 1 | NA 2 |
| market_context_premarket | NONE 1 | BALANCED 1; NONE 1 |
| draw_status_premarket | NONE 1 | NONE 2 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 |
| atentry_high_with_cvd17 | NA 1 | NA 2 |
| atentry_high_with_cvd0830 | NA 1 | NA 2 |
| atentry_low_case_cvd17 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 |
| atentry_low_case_cvd0830 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 |
| atentry_low_with_cvd17 | NA 1 | NA 2 |
| atentry_low_with_cvd0830 | NA 1 | NA 2 |
| prov_high_case_cvd17 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 |
| prov_high_case_cvd0830 | NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 |
| prov_high_with_cvd17 | NA 1 | NA 1; WITH 1 |
| prov_high_with_cvd0830 | NA 1 | NA 1; WITH 1 |
| prov_low_case_cvd17 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 1 |
| prov_low_case_cvd0830 | NOT_AT_LOCATION 1 | LOW_ABSORPTION 1; NOT_AT_LOCATION 1 |
| prov_low_with_cvd17 | NA 1 | NA 1; WITH 1 |
| prov_low_with_cvd0830 | NA 1 | NA 1; WITH 1 |
| post_high_case_cvd17 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 |
| post_high_case_cvd0830 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 |
| post_high_with_cvd17 | NA 1 | NA 2 |
| post_high_with_cvd0830 | NA 1 | NA 2 |
| post_low_case_cvd17 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 |
| post_low_case_cvd0830 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 |
| post_low_with_cvd17 | NA 1 | NA 2 |
| post_low_with_cvd0830 | NA 1 | NA 2 |

R4:

| tag | GAVE_BACK | STOP_THEN_TARGET | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|
| gamma_regime | positive 3 | positive 3 | negative 1; positive 1 | positive 3 |
| hvl_side | ABOVE 1; BELOW 2 | ABOVE 2; BELOW 1 | BELOW 2 | ABOVE 3 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 3 | NOT_APPLICABLE (before 13:00 CT) 3 | NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 3 |
| pc_gamma_ratio_tercile | T1 1; T2 2 | T2 3 | T2 1; T3 1 | T1 3 |
| cr_ps_width_tercile | T1 3 | T3 3 | T2 1; T3 1 | T2 3 |
| mj_alignment | EXPLORATORY_NOT_PLAN_ALIGNED 3 | NOT_APPLICABLE (plan-zone trade) 3 | NOT_APPLICABLE (not a plan zone and not admitted by L1) 1; PLAN_ALIGNED 1 | EXPLORATORY_NOT_PLAN_ALIGNED 2; NOT_APPLICABLE (plan-zone trade) 1 |
| L1_PLAN_SIDE | NONE 3 | NA 3 | ALLOWED 1; NA 1 | NA 1; NONE 2 |
| market_context_premarket | BALANCED 2; BULLISH 1 | NONE 3 | BEARISH 1; NONE 1 | BEARISH 2; NONE 1 |
| draw_status_premarket | NONE 3 | NONE 3 | ACTIVE 1; NONE 1 | ACTIVE 2; NONE 1 |
| atentry_high_case_cvd17 | HIGH_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| atentry_high_case_cvd0830 | HIGH_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| atentry_high_with_cvd17 | AGAINST 1; NA 2 | NA 3 | NA 2 | NA 3 |
| atentry_high_with_cvd0830 | AGAINST 1; NA 2 | NA 3 | NA 2 | NA 3 |
| atentry_low_case_cvd17 | LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 |
| atentry_low_case_cvd0830 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 2 |
| atentry_low_with_cvd17 | AGAINST 2; NA 1 | NA 3 | AGAINST 1; NA 1 | NA 3 |
| atentry_low_with_cvd0830 | NA 3 | NA 3 | NA 2 | NA 3 |
| prov_high_case_cvd17 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 2 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| prov_high_case_cvd0830 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 2 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 |
| prov_high_with_cvd17 | AGAINST 1; NA 2 | NA 2; WITH 1 | AGAINST 1; NA 1 | NA 3 |
| prov_high_with_cvd0830 | AGAINST 1; NA 2 | NA 2; WITH 1 | AGAINST 1; NA 1 | NA 3 |
| prov_low_case_cvd17 | LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 |
| prov_low_case_cvd0830 | NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 |
| prov_low_with_cvd17 | AGAINST 1; NA 2 | NA 3 | NA 2 | NA 3 |
| prov_low_with_cvd0830 | NA 3 | NA 3 | NA 2 | NA 3 |
| post_high_case_cvd17 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 1 |
| post_high_with_cvd17 | NA 3 | NA 3 | NA 2 | NA 3 |
| post_high_with_cvd0830 | NA 3 | NA 3 | NA 2 | NA 3 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2 | NOT_APPLICABLE 3 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 3 | NA 3 | NA 2 | NA 3 |
| post_low_with_cvd0830 | NA 3 | NA 3 | NA 2 | NA 3 |

### 4.4 Per trade (review fields; the full row set is phase2_review.csv)

| strategy | trade | entry session | entry | exit reason | class | net R | MFE R | MAE R | post-stop move R | target traded | truncated | exit flag | min init->entry | confirm delta % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | JOFT-20251105-00577 | 2025-11-05 | 09:15:00 | STOP_FIRST | UNCLASSIFIED | -1.0413 | 0.7308 | 0.9808 | 3.5 | N | N | N | 0.0042 | -13.387 |
| R1 | JOFT-20251105-00749 | 2025-11-05 | 11:09:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0311 | 0.6377 | 0.9855 | 0.7971 | N | N | N | 0.0042 | -17.179 |
| R1 | JOFT-20251106-01371 | 2025-11-06 | 08:49:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0561 | 0.0541 | 0.9865 | 0.1892 | N | N | N | 0.0042 | 13.0719 |
| R1 | JOFT-20251106-01373 | 2025-11-06 | 08:50:00 | TARGET_FIRST | NOT_STOPPED | 1.886 | 1.8631 | 0.5655 | NA | NA | NA | N | 0.0042 | -11.9909 |
| R1 | JOFT-20251106-01408 | 2025-11-06 | 09:06:00 | STOP_FIRST | GAVE_BACK | -1.0144 | 1.0738 | 0.9128 | 3.6107 | Y | N | N | 0.0042 | 12.7907 |
| R1 | JOFT-20251110-03580 | 2025-11-10 | 08:36:00 | STOP_FIRST | GAVE_BACK | -1.0165 | 1.9846 | 0.9846 | 0.0077 | N | N | N | 0.0042 | 20.132 |
| R1 | JOFT-20251110-03728 | 2025-11-10 | 10:14:00 | TARGET_FIRST | NOT_STOPPED | 4.5461 | 4.5294 | 0.8627 | NA | NA | NA | N | 0.0042 | -13.2965 |
| R1 | JOFT-20251110-03874 | 2025-11-10 | 11:49:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0716 | 0.1667 | 0.9667 | 6.4667 | Y | N | N | 0.0042 | 24.0296 |
| R1 | JOFT-20251111-04533 | 2025-11-11 | 08:57:00 | STOP_FIRST | GAVE_BACK | -1.0224 | 1.0833 | 0.9792 | 0.5938 | N | N | N | 0.0042 | 23.1246 |
| R1 | JOFT-20251111-04615 | 2025-11-11 | 09:26:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0391 | 0.0 | 0.9818 | 0.3091 | N | N | N | 0.0042 | 19.0994 |
| R1 | JOFT-20251113-06975 | 2025-11-13 | 08:44:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0127 | 0.6213 | 0.9941 | 0.5976 | N | N | N | 0.0042 | -15.5832 |
| R1 | JOFT-20251113-06987 | 2025-11-13 | 08:53:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0192 | 0.1339 | 0.9732 | 5.0357 | Y | N | N | 0.0042 | 14.2968 |
| R1 | JOFT-20251117-09108 | 2025-11-17 | 08:44:00 | STOP_FIRST | UNCLASSIFIED | -1.024 | 0.0076 | 0.9695 | 2.9084 | N | N | N | 0.0042 | 15.5666 |
| R1 | JOFT-20251117-09134 | 2025-11-17 | 09:09:00 | STOP_FIRST | UNCLASSIFIED | -1.0142 | 0.5099 | 0.9073 | 1.702 | N | N | N | 0.0042 | -13.782 |
| R1 | JOFT-20251118-10111 | 2025-11-18 | 08:46:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.007 | 0.1863 | 0.9248 | 0.5229 | N | N | N | 0.0042 | 11.1995 |
| R1 | JOFT-20251118-10201 | 2025-11-18 | 09:21:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0085 | 0.9524 | 0.9881 | 0.7937 | N | N | N | 0.0042 | 10.9611 |
| R1 | JOFT-20251120-12651 | 2025-11-20 | 08:48:00 | STOP_FIRST | UNCLASSIFIED | -1.0092 | 0.1116 | 0.9828 | 1.6609 | N | N | N | 0.0042 | 20.8077 |
| R1 | JOFT-20251121-14025 | 2025-11-21 | 08:51:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0281 | 0.1339 | 0.9732 | 4.0446 | Y | N | N | 0.0042 | 15.8416 |
| R1 | JOFT-20251121-14045 | 2025-11-21 | 08:57:00 | STOP_FIRST | GAVE_BACK | -1.007 | 3.3301 | 0.9612 | 0.6667 | N | N | N | 0.0042 | -10.2352 |
| R1 | JOFT-20251124-15004 | 2025-11-24 | 08:32:00 | TARGET_FIRST | NOT_STOPPED | 3.2864 | 3.2926 | 0.2394 | NA | NA | NA | N | 0.0042 | 12.126 |
| R1 | JOFT-20251124-15068 | 2025-11-24 | 09:12:00 | STOP_FIRST | UNCLASSIFIED | -1.0199 | 0.6389 | 0.9444 | 1.0093 | N | N | N | 0.0042 | -15.9032 |
| R1 | JOFT-20251124-15073 | 2025-11-24 | 09:16:00 | TARGET_FIRST | NOT_STOPPED | 1.7879 | 1.7918 | 0.7713 | NA | NA | NA | N | 1.0042 | 0.2478 |
| R1 | JOFT-20251125-15739 | 2025-11-25 | 08:50:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0139 | 0.6258 | 0.9935 | 0.2516 | N | N | N | 0.0042 | -14.2014 |
| R1 | JOFT-20251125-15852 | 2025-11-25 | 09:29:00 | TARGET_FIRST | NOT_STOPPED | 1.3764 | 1.3473 | -0.006 | NA | NA | NA | N | 0.0042 | 16.4425 |
| R1 | JOFT-20251125-15877 | 2025-11-25 | 09:45:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0143 | 0.7533 | 0.9667 | 0.8667 | N | N | N | 0.0042 | 14.6675 |
| R1 | JOFT-20251126-16499 | 2025-11-26 | 08:31:00 | STOP_FIRST | UNCLASSIFIED | -1.0152 | 0.7872 | 0.9716 | 2.0709 | N | N | N | 0.0042 | 13.4624 |
| R1 | JOFT-20251126-16613 | 2025-11-26 | 08:56:00 | TARGET_FIRST | NOT_STOPPED | 1.0993 | 1.087 | 0.4203 | NA | NA | NA | N | 0.0042 | -14.1531 |
| R1 | JOFT-20251126-16620 | 2025-11-26 | 08:57:00 | TARGET_FIRST | NOT_STOPPED | 1.5755 | 1.5673 | 0.9423 | NA | NA | NA | N | 0.0042 | -10.5718 |
| R1 | JOFT-20251201-17959 | 2025-12-01 | 08:40:00 | STOP_FIRST | GAVE_BACK | -1.0116 | 1.1081 | 0.9946 | 0.3946 | N | N | N | 0.0042 | -16.131 |
| R1 | JOFT-20251201-18026 | 2025-12-01 | 09:27:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0286 | 0.2933 | 0.88 | 5.1733 | Y | N | N | 0.0042 | 10.8784 |
| R1 | JOFT-20251202-18644 | 2025-12-02 | 08:55:00 | STOP_FIRST | UNCLASSIFIED | -1.0124 | 0.0636 | 0.9942 | 1.6358 | N | N | N | 1.0042 | -9.9187 |
| R1 | JOFT-20251202-18700 | 2025-12-02 | 09:29:00 | STOP_FIRST | UNCLASSIFIED | -1.018 | 0.9429 | 0.9943 | 1.0914 | N | N | N | 0.0042 | -19.5645 |
| R1 | JOFT-20251203-19491 | 2025-12-03 | 08:55:00 | TARGET_FIRST | NOT_STOPPED | 1.8734 | 1.88 | 0.3429 | NA | NA | NA | N | 0.0042 | 11.251 |
| R1 | JOFT-20251203-19564 | 2025-12-03 | 09:20:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0167 | 0.9457 | 0.9922 | 0.6357 | N | N | N | 0.0042 | -17.5642 |
| R1 | JOFT-20251203-19613 | 2025-12-03 | 09:34:00 | TARGET_FIRST | NOT_STOPPED | 2.5947 | 2.5618 | 0.9157 | NA | NA | NA | N | 0.0042 | 14.1857 |
| R2 | JOFT-20251105-00577 | 2025-11-05 | 09:17:00 | STOP_FIRST | UNCLASSIFIED | -1.0413 | -0.0192 | 0.9423 | 3.75 | N | N | N | 2.0042 | -2.061 |
| R2 | JOFT-20251106-01375 | 2025-11-06 | 08:51:00 | TARGET_FIRST | NOT_STOPPED | 2.2639 | 2.2576 | 0.0712 | NA | NA | NA | N | 1.0042 | -11.5172 |
| R2 | JOFT-20251110-03728 | 2025-11-10 | 10:15:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0543 | 0.0 | 0.9655 | 4.8276 | Y | N | N | 1.0042 | -6.2409 |
| R2 | JOFT-20251111-05109 | 2025-11-11 | 13:38:00 | STOP_FIRST | UNCLASSIFIED | -1.0391 | 0.0364 | 0.8727 | 1.9818 | N | N | N | 1.0042 | 35.3293 |
| R2 | JOFT-20251117-09183 | 2025-11-17 | 09:24:00 | STOP_FIRST | GAVE_BACK | -1.0174 | 1.0773 | 0.9945 | 1.9227 | N | N | N | 1.0042 | 7.723 |
| R2 | JOFT-20251117-09452 | 2025-11-17 | 11:46:00 | TARGET_FIRST | NOT_STOPPED | 1.7975 | 1.7892 | 0.5336 | NA | NA | NA | N | 1.0042 | -9.0548 |
| R2 | JOFT-20251124-15047 | 2025-11-24 | 08:53:00 | TARGET_FIRST | NOT_STOPPED | 1.8019 | 1.8066 | 0.1646 | NA | NA | NA | N | 1.0042 | 11.4296 |
| R2 | JOFT-20251125-15937 | 2025-11-25 | 10:27:00 | TARGET_FIRST | NOT_STOPPED | 1.8106 | 1.8125 | 0.4625 | NA | NA | NA | N | 4.0042 | -4.6238 |
| R2 | JOFT-20251125-16014 | 2025-11-25 | 11:10:00 | TARGET_FIRST | NOT_STOPPED | 2.9659 | 2.9841 | 0.5079 | NA | NA | NA | N | 4.0042 | 7.6923 |
| R2 | JOFT-20251126-16530 | 2025-11-26 | 08:41:00 | STOP_FIRST | GAVE_BACK | -1.0364 | 2.0508 | 0.8814 | 7.1356 | Y | N | N | 3.0042 | 0.4386 |
| R2 | JOFT-20251126-16620 | 2025-11-26 | 08:59:00 | TARGET_FIRST | NOT_STOPPED | 0.7708 | 0.7651 | 0.0134 | NA | NA | NA | N | 2.0042 | -21.1962 |
| R2 | JOFT-20251126-16630 | 2025-11-26 | 09:00:00 | STOP_FIRST | UNCLASSIFIED | -1.0088 | 0.4508 | 0.9959 | 1.3074 | N | N | N | 1.0042 | -1.9104 |
| R2 | JOFT-20251202-18922 | 2025-12-02 | 11:02:00 | TIME_EXIT | NOT_STOPPED | 0.8035 | 1.7042 | 0.8 | NA | NA | NA | N | 1.0042 | 14.6568 |
| R3 | JOFT-20251105-00577 | 2025-11-05 | 09:17:00 | STOP_FIRST | UNCLASSIFIED | -1.0413 | -0.0192 | 0.9423 | 3.75 | N | N | N | 2.0042 | -2.061 |
| R3 | JOFT-20251110-03728 | 2025-11-10 | 10:15:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0543 | 0.0 | 0.9655 | 4.8276 | Y | N | N | 1.0042 | -6.2409 |
| R3 | JOFT-20251111-05109 | 2025-11-11 | 13:38:00 | STOP_FIRST | UNCLASSIFIED | -1.0391 | 0.0364 | 0.8727 | 1.9818 | N | N | N | 1.0042 | 35.3293 |
| R3 | JOFT-20251117-09183 | 2025-11-17 | 09:24:00 | STOP_FIRST | GAVE_BACK | -1.0174 | 1.0773 | 0.9945 | 1.9227 | N | N | N | 1.0042 | 7.723 |
| R3 | JOFT-20251125-15937 | 2025-11-25 | 10:27:00 | TARGET_FIRST | NOT_STOPPED | 1.8106 | 1.8125 | 0.4625 | NA | NA | NA | N | 4.0042 | -4.6238 |
| R3 | JOFT-20251125-16014 | 2025-11-25 | 11:10:00 | TARGET_FIRST | NOT_STOPPED | 2.9659 | 2.9841 | 0.5079 | NA | NA | NA | N | 4.0042 | 7.6923 |
| R3 | JOFT-20251126-16530 | 2025-11-26 | 08:41:00 | STOP_FIRST | GAVE_BACK | -1.0364 | 2.0508 | 0.8814 | 7.1356 | Y | N | N | 3.0042 | 0.4386 |
| R3 | JOFT-20251126-16620 | 2025-11-26 | 08:59:00 | TARGET_FIRST | NOT_STOPPED | 0.7708 | 0.7651 | 0.0134 | NA | NA | NA | N | 2.0042 | -21.1962 |
| R4 | JOFT-20251105-00559 | 2025-11-05 | 09:10:00 | STOP_FIRST | UNCLASSIFIED | -1.037 | 0.1724 | 0.9828 | 3.7931 | N | N | N | 3.0042 | 1.9793 |
| R4 | JOFT-20251105-00590 | 2025-11-05 | 09:17:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0413 | -0.0192 | 0.9423 | 3.75 | Y | N | N | 2.0042 | -2.061 |
| R4 | JOFT-20251110-03787 | 2025-11-10 | 10:15:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0543 | 0.0 | 0.9655 | 4.8276 | Y | N | N | 1.0042 | -6.2409 |
| R4 | JOFT-20251110-03875 | 2025-11-10 | 11:06:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0272 | 0.519 | 0.9747 | 2.4177 | Y | N | N | 2.0042 | 0.3836 |
| R4 | JOFT-20251111-04572 | 2025-11-11 | 08:52:00 | STOP_FIRST | GAVE_BACK | -1.0488 | 1.3409 | 0.9773 | 5.0227 | N | N | N | 2.0042 | 2.587 |
| R4 | JOFT-20251111-04631 | 2025-11-11 | 09:16:00 | STOP_FIRST | GAVE_BACK | -1.0133 | 1.9506 | 0.9198 | 1.2222 | N | N | N | 1.0042 | -13.6399 |
| R4 | JOFT-20251112-05876 | 2025-11-12 | 08:34:00 | TARGET_FIRST | NOT_STOPPED | 3.0464 | 2.9036 | 0.5783 | NA | NA | NA | N | 2.0042 | -2.2805 |
| R4 | JOFT-20251114-08525 | 2025-11-14 | 09:09:00 | STOP_FIRST | UNCLASSIFIED | -1.0275 | 0.6154 | 0.9872 | 4.1282 | N | N | N | 1.0042 | 3.8176 |
| R4 | JOFT-20251117-09569 | 2025-11-17 | 09:47:00 | STOP_FIRST | GAVE_BACK | -1.0404 | 1.1667 | 0.9872 | 0.7179 | N | N | N | 2.0042 | 3.8554 |
| R4 | JOFT-20251117-09632 | 2025-11-17 | 10:08:00 | TARGET_FIRST | NOT_STOPPED | 3.356 | 3.2537 | 0.8209 | NA | NA | NA | N | 1.0042 | -0.7194 |
| R4 | JOFT-20251118-10781 | 2025-11-18 | 10:47:00 | TARGET_FIRST | NOT_STOPPED | 2.5177 | 2.5079 | 0.8995 | NA | NA | NA | N | 7.0042 | -2.6593 |
| R4 | JOFT-20251118-10874 | 2025-11-18 | 11:40:00 | TARGET_FIRST | NOT_STOPPED | 1.8694 | 1.8345 | -0.0072 | NA | NA | NA | N | 1.0042 | 18.0787 |
| R4 | JOFT-20251118-10891 | 2025-11-18 | 11:48:00 | TARGET_FIRST | NOT_STOPPED | 1.7552 | 1.7622 | 0.4878 | NA | NA | NA | N | 5.0042 | 7.2542 |
| R4 | JOFT-20251119-11984 | 2025-11-19 | 10:34:00 | STOP_FIRST | GAVE_BACK | -1.0617 | 1.1176 | 0.9804 | 2.8627 | N | N | N | 5.0042 | 0.8365 |
| R4 | JOFT-20251119-12403 | 2025-11-19 | 12:52:00 | TARGET_FIRST | NOT_STOPPED | 0.9819 | 0.9832 | 0.3613 | NA | NA | NA | N | 1.0042 | 8.0402 |
| R4 | JOFT-20251126-17305 | 2025-11-26 | 08:40:00 | STOP_FIRST | GAVE_BACK | -1.0127 | 1.1716 | 0.9408 | 0.8107 | N | N | N | 9.0042 | 3.2787 |
| R4 | JOFT-20251201-18890 | 2025-12-01 | 09:39:00 | TARGET_FIRST | NOT_STOPPED | 3.0191 | 3.0309 | 0.4227 | NA | NA | NA | N | 2.0042 | 4.2453 |
| R4 | JOFT-20251201-18936 | 2025-12-01 | 10:25:00 | TARGET_FIRST | NOT_STOPPED | 3.6629 | 3.6923 | 0.4359 | NA | NA | NA | N | 4.0042 | -4.1667 |
| R4 | JOFT-20251204-21797 | 2025-12-04 | 12:31:00 | STOP_FIRST | GAVE_BACK | -1.0934 | 1.5217 | 0.9565 | 0.6087 | N | N | N | 2.0042 | 0.9074 |

EXIT_AFTER_SESSION_CLOSE trades: none


## 5. Section 5 diagnostics in Phase 2 (registration section 4)

Statuses as registered. Per-trade and per-candidate outputs are in `book1a/Phase2/runs/phase2_diag/` (row counts
below; sha256 in section 7). Counterfactual exits are stored per trade only and are not aggregated by outcome here.

| replay plan section 5 diagnostic | Phase 2 status | output (rows) | note |
|---|---|---|---|
| C2 location arm, VWAP as a family vs VWAP as a tag only | NOT_RUN | - | not built: needs a second plan set with VWAP as a tag and an R4 rerun on it |
| MAP4 high-volume areas vs MAP0 zones (AMT PO-6) | LOGGED_ONLY | plan sidecars `map4_areas` (21 plans) | the comparison itself is not built |
| Exit steps M0 -> M-J1 -> M-J2 (R4 fixed at M0, E1) | RUN | diag_exit_trades.csv (75) | M-J1 / M-J2 per trade, v1.1 ladder source and mj_alignment; R1-R3 have no ladder (NOT_APPLICABLE) |
| Exit steps M-J3, M-J4 | NOT_RUN | - | U5: deferred until objective triggers are specified |
| Quantower-style power trade vs S1.4 single print (C4) | LOGGED_ONLY | `power_trade_qt` in the candidate logs | U2; not a gate, no comparison built |
| 10 NQ feasibility (hypothetical) | RUN | diag_sizing_trades.csv (75) | labelled hypothetical |
| MNQ feasibility (diagnostic only) | RUN | diag_mnq_rejects.csv (13) | the R3 / R4 RISK_REJECT attempts (6 + 7) |
| L2 diagnostics and L2 terciles | NOT_RUN | - | the L2F audit, the fixed-price build and the coverage list are not done (U11) |
| E1 refill defense | NOT_RUN | - | L2F audit not done (U11) |
| E2 defense pulled before the touch | NOT_RUN | - | L2F audit not done (U11) |
| E4 book flip on the retest | NOT_RUN | - | L2F audit not done (U11); E4's hold time N is not registered |
| Exit cue (a), absorption against the trade | RUN | diag_exit_trades.csv (75) | per trade, beside M0 |
| GEX V2 random-level twin | RUN | diag_gex_zones.csv (526) | |
| GEX V3 second flip estimate | RUN | diag_gex_v3_sessions.csv (21), gex_v3_input_files.csv (1345) | reproduces the frozen levels row before use |
| GEX V5 days without valid levels | RUN | diag_gex_sessions.csv (21) | 0 V5 sessions in Phase 2 |
| Volatility control (ATM IV terciles) | RUN | diag_gex_sessions.csv (21) | POST_PHASE_GROUPING over the 21 sessions' atm_iv |
| Gamma regime and time-of-day splits; context GEX tags | RUN | section 2; section 4; diag_gex_trades.csv (75) | |
| CVD_DIV by case and WITH / AGAINST, AT_ENTRY / PROVISIONAL / POST_ENTRY separate | RUN | diag_cvd_trades.csv (75), diag_cvd_candidates.csv (25048); section 4 | with the fidelity note |
| CVD_DIV overlap with T8 and the passive trap tag | RUN | diag_cvd_candidates.csv (t8_overlap, log_trapped_passive) | |
| cvd_slope_5 by tercile | RUN | diag_cvd_candidates.csv (log_cvd_slope_5) | cut-offs from the Phase 2 S1.4 candidate rows' own values, never outcomes |
| Grade without CVD (counterfactual on R4) | NOT_RUN | - | the S1.4 grade is computed in the harness C# code; recomputing it needs a harness change |
| BREAKOUT_SPEED raw values | RUN | diag_cvd_candidates.csv, diag_cvd_trades.csv; phase2_review.csv | |
| 08:30 vs 17:00 CT CVD reset | RUN | cvd17 / cvd0830 columns per swing | |
| Swing pairs excluded by the 60-minute window | RUN | EXCLUDED_60MIN in the case columns | the D5 files (d5_cvd_*) are Phase 1 only and empty here |
| L1_PLAN_SIDE (R4 intraday zones admitted by L1) | RUN | diag_l1_plan_side.csv (3824) | |
| Every logged tag | RUN | candidate logs; section 4 | descriptive |
| D2 point-in-time audit of every AT_ENTRY field | RUN | diag_timing.csv (111331), d2_lookahead_audit.json | 111331 groups, 0 violations |

## 6. Phase 2 gate (registration section 6)

**G1 Integrity: met.**
- Run at the frozen commit: every R1-R4, stress, diagnostics, G4 and report-card run at `e1d37a1`, tree clean
  (section 1); the review at `79ab4c0` (the approved amendment; execution code unchanged).
- Plan hashes: `phase2_plan_hashes --check` MATCH; `git show e1d37a1:Book1A/Phase2/plan_hashes_phase2.md` sha256
  `5c1a913edcb9a37a4942ef19201a06774d990777686c41981b4721bca8341e74` (the registered reference). Plans rebuilt from the
  Step B R1 run's own map packets: 42 files, 0 different from the A2 files; Step B packets vs Step A packets (body
  without built_local): 21, 0 different. R4 ledger (19 rows) and R4_candidates (17778 rows): `plan_sha256` present,
  0 mismatches.
- Unit tests at the tag: 331 run, 0 failures (`runs/g1/unit_tests/unit_tests_2026-11-07.log`). At `79ab4c0`: 370 run,
  0 failures (checker: 368 / 368 runnable).
- Look-ahead audit (`book1a.audit_run`, every ledger): R1 730 inputs, R2 274, R3 171, R4 408; 0 violations, 0 missing;
  plan_build_checks 139, 0 failed. D2 audit of every AT_ENTRY field: 111331 groups, 0 violations.
- Phase 1 ledgers unchanged: R1 `b4a2108f...`, R2 `6123f88e...`, R3 `f413d15f...`, R4 `b4510aab...` (all four equal to
  the registered sha256; `runs/g1/g1_phase1_ledgers.log`).

**G2 Coverage: met.** 21 / 21 sessions in the R1 / R2 run, the R3 run, the R4 run and the daily-loop config, each equal
to the registered list; the stress and diagnostics runs read the same runs. No coverage exception.

**G3 Risk: met.** risk-c3-v2 on every R3 / R4 row; 0 non-ACCEPT ledger rows; **0 planned-risk violations** (no
accepted trade with `planned_risk_usd` above min($1,000, remaining daily budget)). Execution breaches reported
(section 2): R3 1, R4 5, largest $222.96 over the budget; RISK_BREACH_FILL (realized overrun) R3 1, R4 5, largest
$300.00 (logged only; not a Phase 2 gate).

**G4 Checker reproduction: open (the checker's step).** The sample: `g4_draw.py` v1.0 run unchanged (script sha256
`5f401190e59a53eaf883aad53f4b9c5bb80687bbeb5a103d6718bd0f072bae9c`, seed 20251205, numpy 2.5.3): FIXED_DAY 3 (every R4
trade on Nov 6, Nov 12, Nov 19, Dec 3), DRAW_R4 10, DRAW_R1R3 10; sample sha256
`e910dfec57a9bd0fbfd4622dd7ee859e4fdd0dea51a2a2837a17ac592fb7415f`. The pack (`Book1A/Phase2/checker_input/`, 35 files
+ `pack_manifest.json`, zipped as `Phase2_G4_checker_pack.zip`) holds the sample, the four full ledgers, the R1 / R2
checker ledgers, attempts, retests, risk events, the 12 stress ledgers with their manifests, the report card json and
the review outputs. The runner does not compare anything with the checker.

**G5 Deliverables complete and hashed: met with this commit.** This report, the ledgers and the review file
(`phase2_review.csv`, with `phase2_review_classes.json` and its manifest) are hashed in section 7; the report and the
Phase 3 change-list draft are hashed in `Phase2_deliverables_sha256.md`. Ledgers stay out of git (`.gitignore`); they
are in the run folders and the checker pack.


## 7. File sha256

Paths under `book1a/Phase2/runs/` (the checker pack under `book1a/Phase2/checker_input/`).

| file (under book1a/Phase2/runs/) | bytes | sha256 |
|---|---|---|
| phase2/R1_A0_full.csv | 7228 | 7c0ea1ecdc566d927fdbb533b37aab36827ccf5d33a731e72e112eb3774d24f8 |
| phase2/R2_C1_full.csv | 2841 | a9f06934eae85ef199b26fc372b20d107e8d0f5d3bced85452ec4e07d6b3451d |
| phase2_r3/R3_M0_ledger.csv | 2477 | 6d938f834ac4b10beb72a29f3171f7243a0fe8e1da2ef52815b5b0e94d1ac921 |
| phase2_r4/R4_M0_ledger.csv | 8469 | 478dbb3374ef5ac5f684c397f4e350e350b2b7a9cf02a014e4582c5fd2299b83 |
| phase2/checker_input/R1_A0.csv | 4286 | 13c34a0413968429b582a71db0670880971753483911eb014cc014a7792172ff |
| phase2/checker_input/R2_C1.csv | 1656 | f41050f085738c3f5183ec13ba335d4ae70d73197ff18cb6ea2f89bf7b0d5989 |
| phase2/R1_attempts.csv | 20522 | 213e6ca67427d065e49f6ec5b41586396115df2a3b9c1315108463577d2cbcf6 |
| phase2/R2_attempts.csv | 1681 | 1c270ed428fe3506c93ce32edbfd26253c0e05c748a7ba0a8d9270c16c266ed9 |
| phase2/R2_retests.csv | 1333 | 94507bb43ac99f8900174f3ca68bb9b2a0e46aa6b555218276c0e641dd79fec5 |
| phase2_r3/R3_attempts.csv | 3745 | c3ab52a9b9753e2807b9bc991fe40a41af9eeca4f70f8cd519f183ce8452fd01 |
| phase2_r3/R3_retests.csv | 919 | 5236ee8615791e1541a1b6decf4840a9c46ac60cb8ac06abdaa04779eba773f2 |
| phase2_r3/R3_risk_events.json | 428 | 354af5fc7425cbb2f0c20d7c18913d2bad4318084d43895741c1c938be05be0f |
| phase2_r4/R4_attempts.csv | 17497 | be4ae9a6aabf6fdf5c569b006d7b0c0d4c73a8e7bb7b5fc0be06aa55a0351913 |
| phase2_r4/R4_candidates.csv | 17794336 | 97d2579f98ebc93ebdd4bbeb46e280e9ef1e9bd91bc18793f20cbd501135e885 |
| phase2_r4/R4_risk_events.json | 2118 | 6bf4de95ed0116de2ab65d0d0b26dc8a26bd43a836256f490404c642a0a15499 |
| phase2_stress_lat1000/R1_A0_full.csv | 7260 | d7868cbe42a38d48d44a2ea92abf5fafe3a614070ab65caa581c6cb17cce0c53 |
| phase2_stress_lat1000/R2_C1_full.csv | 2849 | 323da7b2590f338a4d5ed5af5f6ec62234b6c64cb27db1e52da7168cf804e829 |
| phase2_stress_lat1000/R3_M0_ledger.csv | 2484 | 92f89a3919bf446df77f63892b25f46771f17e7d1ca01455b31f8e067ef55110 |
| phase2_stress_lat1000/R4_M0_ledger.csv | 8075 | 48cb6f1d942e5fa780616b26779e6dbbb3083abcf5b33f1a4bbdb18aef8011cd |
| phase2_stress_lat1000/stress_manifest.json | 1204 | 8e6a73c1d4491257a9a657107d541d9f129c317df629b39d48552384cdf34750 |
| phase2_stress_slip2/R1_A0_full.csv | 7230 | 79d96385472cd41ad706bb6b542d7ec3a5637645c12ad7702a6d02c5c7c95267 |
| phase2_stress_slip2/R2_C1_full.csv | 2846 | 4305fd7df5a7ffd7751265ef400b697e332a99712140bcf086970937aab0f8c3 |
| phase2_stress_slip2/R3_M0_ledger.csv | 2481 | af5456dce2adfae4e1545950e84f303f8d8d5ba611aa378a9b1c1e6dd1a665ab |
| phase2_stress_slip2/R4_M0_ledger.csv | 8463 | e912e60824c8ff3397c0aecdb81156ae8107056178f6b83697d8715f9368378a |
| phase2_stress_slip2/stress_manifest.json | 1201 | 3234013d6b42e114f9ee5789f0054473a9a7d0a499a1ad16f6cb64f2cf7aa98a |
| phase2_stress_slip4/R1_A0_full.csv | 7230 | 156e46130c5554ce56181b202d2abcdd26a94c3b4480551cfb614dec6ad9d634 |
| phase2_stress_slip4/R2_C1_full.csv | 2843 | b4b5f5b3071820aab49acc18a601820b606316f520910a7a093cda3841d62e2a |
| phase2_stress_slip4/R3_M0_ledger.csv | 2478 | 88fbaa8103ce299ee501ef73d4b5f1587bbaa988c6a9611a0d1b2966c7ce479a |
| phase2_stress_slip4/R4_M0_ledger.csv | 8458 | aa98d8931a6703b2d3ab8dde3a93e9ed9374642a8ba2241b5c3edcc6034bed02 |
| phase2_stress_slip4/stress_manifest.json | 1201 | f059f55ba2066d9caebb1e2941967ef641683185efa051f3fe27f07d3775a8d5 |
| phase2/run_manifest.json | 651 | 1628c68f95981103ab3e2066c9a55b8baafc5c9c5bf6ea57bd7bb06b501d68c5 |
| phase2_r3/run_manifest.json | 955 | 3a5794ee7ed85fb7ab7bb8d900ffa482091c2b548cb0755a6819d78362ee5f2d |
| phase2_r4/run_manifest.json | 1464 | e615753acffae60688b8a8bcac687dc368f9c30cba06af84f67b833424f62ded |
| phase2_diag/diag_manifest.json | 4563 | 247c012dcedf9e2b7a5b04d4a15b83f68ab84a65fc1c96b433608c953dfd75b6 |
| phase2_diag/d2_lookahead_audit.json | 355 | daa198da73328bfbaf46f40f46af009fc6b9553788486cbc0c6b7fef0100c4b6 |
| phase2_report_card.json | 48791 | b39e4ac1c5da28dd3e9de8408fd405c22a03a055b21977b205953114d1637307 |
| phase2_review/phase2_review.csv | 73904 | cdb6ad959116465caec9d67a243f9c3692247e5b8e6d786f70515c5a3639eda5 |
| phase2_review/phase2_review_classes.json | 267772 | d1150886fc9e951d51d62d90e7c64b0aabe9df8e933f68bc939e51dc6c8fb2e1 |
| phase2_review/phase2_review_manifest.json | 14679 | 11dfa75384e42ee01dbbbb3610ad1cb71194730607893736725d43cf02e570f0 |
| phase2_diag/d5_cvd_pairs.csv | 471 | d5507fcf5d32169aa4710a8e67c77da855918a51d339d6746c0b05440ef88185 |
| phase2_diag/d5_cvd_pairs_excluded_60min.csv | 471 | d5507fcf5d32169aa4710a8e67c77da855918a51d339d6746c0b05440ef88185 |
| phase2_diag/d5_cvd_swings.csv | 471 | d5507fcf5d32169aa4710a8e67c77da855918a51d339d6746c0b05440ef88185 |
| phase2_diag/diag_cvd_candidates.csv | 26427077 | 6a71bf891954f73718b8760f866f4e4ad549bbb9225e3e93bc4b01675f420ec4 |
| phase2_diag/diag_cvd_trades.csv | 85401 | 59b17875aab81dca913f65ec57afc3a628afaf047c9ece1b8a0f3166b2a9f951 |
| phase2_diag/diag_exit_trades.csv | 29245 | 5fe079ef1ce56af92ac604b00984c401f2e307bb446fc7653d269a9e7f16ffec |
| phase2_diag/diag_gex_sessions.csv | 4640 | 08e23c54689e7fa8436dca7f54f52c6a31f304a0278fb40c53daea85e45e1c30 |
| phase2_diag/diag_gex_trades.csv | 25835 | 8ff1634d493091721b2e05dcc46905226e33d6a39be9cbc13408a82a3278e16d |
| phase2_diag/diag_gex_v3_sessions.csv | 7191 | 3634be76a6fb2335e98ba45fff02f1c260c9b181de72e684b2c15e53e3602c93 |
| phase2_diag/diag_gex_zones.csv | 165925 | 517478fa54c9adb63aa86435c1923ed9421eb3a536ce9b780dc05a7da68ae4ef |
| phase2_diag/diag_l1_plan_side.csv | 1101350 | b82489d7f69acce08504ffbebb2e2fd7e6d359c02ba0b39708146678740ce57c |
| phase2_diag/diag_mnq_rejects.csv | 4013 | 221c9008f3325af925b4669bbd54b3c20d11ea2909e31f9ad94bec487194f171 |
| phase2_diag/diag_sizing_trades.csv | 16226 | 736f633eefe6895e11cbf42f63f160273fd0f6098f0c74c8c596cbe2dc80a91c |
| phase2_diag/diag_timing.csv | 14470752 | a96714b45b8c1f274ee787bc74e701f58159c45be22b4b3a306b9b829739f9c9 |
| phase2_diag/gex_v3_input_files.csv | 236671 | ed5791a5b0696c753e3bc88c71c1d0477640a300f2c62124e114afebec59be93 |
| ../checker_input/g4_sample.csv | 1509 | e910dfec57a9bd0fbfd4622dd7ee859e4fdd0dea51a2a2837a17ac592fb7415f |
| ../checker_input/g4_sample.csv.manifest.json | 1188 | bdf827935e944a11b035ef4dd4a94d6513f3624416d1d0fc260e9f93eae03038 |
| ../checker_input/pack_manifest.json | 5843 | efbd39903d3d37a26112515706ebe3e653a2052b3dae0eafd5093cf30195691a |
| ../checker_input/Phase2_G4_checker_pack.zip | 72869 | 9a8ed2cd2515e39031aef2e65265dadfe6ac7f4bf6ca30320d175bf983b90846 |
| report_build/build_phase2_report_md.py | 10611 | c09025cbd69f331c1dd15d364845f1afe399563177bd51325cb8f08e69ec4888 |



## 8. Access and blinding

- No file of Book 1 or `K:\Book1A_checker` was opened; no git command ran in `K:\Databento_BackTesting`. Inputs only
  through `K:\Book1A_inputs`.
- Before the review script was written (Nov 7), the Step B gate checks showed only mechanics: run metadata, check_a0
  0, R4 ledger rows 19 and candidate rows 17778, the G4 counts, audit input counts, G3 counts, the D2 count, and
  diagnostics column names (change log, Nov 7). Results were first read after the review run, to write this report.
- No threshold, rule, plan or execution code was changed after any result. Phase 1 outcomes were not used.
