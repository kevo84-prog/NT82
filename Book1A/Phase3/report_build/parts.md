@@SEC4
## 4. What fails and why (registration section 3), every trade

Stopped trades (exit_reason STOP_FIRST) are classed by the first rule that applies:
- **GAVE_BACK**: MFE >= 1.0 R before the stop.
- **STOP_THEN_TARGET**: the original target traded in the post-stop window, truncated or not.
- **NO_POST_STOP_FOLLOW_THROUGH**: the window is complete, the move is < 1.0 R, and the target did not trade.
- **UNCLASSIFIED**: anything else, including a truncated window without the target and a window with no trade.

Other trades are NOT_STOPPED. The 1.0 R cut-off is a prespecified descriptive threshold. Post-stop window: (stop fill,
stop fill + 30 min], cut at the session close. R = ticks / stop ticks at the fill. Descriptive only; replay
(in-sample).

The review run (`phase3_review`, at `17ac9cd`) checked its inputs:
- 153 review rows = the 153 ledger trades (R1 63, R2 28, R3 20, R4 42), each exactly once;
- the 62 input files' sha256 are equal before and after;
- the overlap check is empty for all four strategies;
- the cr_ps_width cut-offs use one value per session over all 41 sessions;
- the premarket plan fields come from the 41 hashed sidecars;
- the state at entry is NOT_RUN; BREAKOUT_SPEED raw values are listed per trade and not counted.

CVD_DIV: fidelity to Jeron's CVD unproven (1 of 4 video examples reproduced; CVD_video_check, Nov 6). AT_ENTRY,
PROVISIONAL and POST_ENTRY are kept separate; cvd17 = 17:00 CT reset, cvd0830 = 08:30 CT reset. L1_PLAN_SIDE exists
only for R4 trades from an intraday zone admitted by L1; 5 R4 trades have no row (NA). market_context /
draw_status are the premarket plan values, not the state at entry.

What the classes show (descriptive, no rule follows from it):
- R4, ALL: 26 of 42 trades stopped: GAVE_BACK 6, STOP_THEN_TARGET 6, NO_POST_STOP_FOLLOW_THROUGH 6, UNCLASSIFIED 8.
- R1, ALL: 45 of 63 stopped, most of them NO_POST_STOP_FOLLOW_THROUGH (16) or UNCLASSIFIED (16).
- R3, ALL: 14 of 20 stopped, half of them GAVE_BACK (7).
- Ideas that come from these counts belong in `Block2_candidates.md` only; Phase 3 changes nothing.

@@SEC5
## 5. Primary comparisons (registration section 5)

The Book 1 promotion rule, `jeron_engine.arms.promotion`, is called unchanged by `phase3_compare.py` (seed 20251205,
n 10,000). The rule has four checks:
- **bound**: the 5th percentile of the session-bootstrap paired difference is > 0;
- **drawdown**: arm max drawdown <= 1.25 x the comparator's;
- **sample**: >= 20 trades differ;
- **two_tick**: the slip2 paired mean is >= 0.

All four pass → "promote"; otherwise "insufficient evidence". Book 1's code also has "reject": when the sample check
passes and the interval does not contain 0. Here it is shown as the code returns it, as information only. Deciding
population: ALL, "in-sample, includes 3 exposed sessions (Part 3)". UNEXPOSED is the registered sensitivity.

Why each verdict, from the checks:
- **P1 R4 vs R1, insufficient evidence** (ALL and UNEXPOSED). The bound fails: the interval contains 0. Drawdown,
  sample (101 / 94 trades differ) and two-tick pass.
- **P2 R4 vs R3, insufficient evidence** (ALL and UNEXPOSED). On ALL the bound fails and the other three pass. On
  UNEXPOSED, bound, drawdown and two-tick fail; sample passes.
- **P3 R3 vs R2, insufficient evidence** (ALL and UNEXPOSED). Bound, sample (16 / 14 differ, < 20) and two-tick fail;
  drawdown passes. The whole interval is below 0, but with fewer than 20 differing trades Book 1's code returns
  "insufficient evidence", not "reject".
- Sensitivity: SAME_VERDICT for P1, P2 and P3. Net R alone never decides.

@@SEC6
## 6. Section 5 diagnostics in Phase 3 (registration section 4)

Statuses are as registered. The per-trade and per-candidate outputs are in `book1a/Phase3/runs/phase3_diag_17ac9cd/`
(commit `17ac9cd`; row counts below; sha256 in section 9). Counterfactual exits are stored per trade only and are not
aggregated by outcome here.

| replay plan section 5 diagnostic | Phase 3 status | output (rows) | note |
|---|---|---|---|
| C2 location arm, VWAP as a family vs VWAP as a tag only | RUN | phase3_r4_c2 (43 trades); section 2.4 | not promotable; 5 trades differ from R4 on ALL |
| MAP4 high-volume areas vs MAP0 zones (AMT PO-6) | LOGGED_ONLY | plan sidecars `map4_areas` (41 plans) | the comparison is not built |
| Exit steps M0 -> M-J1 -> M-J2 (R4 fixed at M0, E1) | RUN | diag_exit_trades.csv (153) | M-J1 / M-J2 per trade, v1.1 ladder source, mj_alignment (section 2.3) |
| Exit steps M-J3, M-J4 | DROPPED | - | U5: no objective triggers specified |
| Quantower-style power trade vs S1.4 single print (C4) | LOGGED_ONLY | `power_trade_qt` in the candidate logs | U2 |
| 10 NQ feasibility (hypothetical) | RUN | diag_sizing_trades.csv (153) | labelled hypothetical |
| MNQ feasibility (diagnostic only) | RUN | diag_mnq_rejects.csv (27) | the R3 / R4 RISK_REJECT attempts (14 + 13) |
| L2 diagnostics and L2 terciles | NOT_RUN | - | L2F audit, fixed-price build and coverage list not done (U11) |
| E1 refill defense | NOT_RUN | - | as L2 |
| E2 defense pulled before the touch | NOT_RUN | - | as L2 |
| E4 book flip on the retest | NOT_RUN | - | as L2; E4's hold time N not registered |
| Exit cue (a), absorption against the trade | RUN | diag_exit_trades.csv (153) | per trade, beside M0 |
| GEX V2 random-level twin | RUN | diag_gex_zones.csv (756) | |
| GEX V3 second flip estimate | RUN | diag_gex_v3_sessions.csv (41), gex_v3_input_files.csv (2522) | 41 / 41 repro_all_match Y at `17ac9cd`; Dec 17-18 0DTE levels "absent, matching" (section 1.1) |
| GEX V5 days without valid levels | RUN | diag_gex_sessions.csv (41) | 0 V5 sessions |
| Volatility control (ATM IV terciles) | RUN | diag_gex_sessions.csv (41) | over the 41 sessions' atm_iv |
| Gamma regime and time-of-day splits; context GEX tags | RUN | section 2; section 4; diag_gex_trades.csv (153) | |
| CVD_DIV by case and WITH / AGAINST, AT_ENTRY / PROVISIONAL / POST_ENTRY separate | RUN | diag_cvd_trades.csv (153), diag_cvd_candidates.csv (41958); section 4 | with the fidelity note |
| CVD_DIV overlap with T8 and the passive trap tag | RUN | diag_cvd_candidates.csv (t8_overlap, trapped_passive) | |
| cvd_slope_5 by tercile | RUN | diag_cvd_candidates.csv (log_cvd_slope_5) | cut-offs from the Phase 3 S1.4 candidate rows' own values, never outcomes |
| Grade without CVD (counterfactual on R4) | NOT_RUN: not needed | - | the S1.4 grade has no CVD input, so the counterfactual equals the current grade |
| BREAKOUT_SPEED raw values | RUN | diag_cvd_candidates.csv, diag_cvd_trades.csv; phase3_review.csv | |
| 08:30 vs 17:00 CT CVD reset | RUN | cvd17 / cvd0830 columns per swing | |
| Swing pairs excluded by the 60-minute window | RUN | EXCLUDED_60MIN in the case columns | the D5 files (d5_cvd_*) are Phase 1 only and empty here (0 rows) |
| L1_PLAN_SIDE (R4 intraday zones admitted by L1) | RUN | diag_l1_plan_side.csv (8217) | 5 R4 trades without a row (NA) |
| Every logged tag | RUN | candidate logs; section 4 | descriptive |
| D2 point-in-time audit of every AT_ENTRY field | RUN | diag_timing.csv (188141), d2_lookahead_audit.json | 188141 groups (AT_ENTRY 103407, PROVISIONAL 84222, POST_ENTRY 512), 0 violations |

@@SEC7
## 7. Phase 3 gate (registration section 7; pass = all of G1-G5; performance is not a gate)

**G1 Integrity: met.**
- **Commits.** Run at the frozen commit: R1-R4, C2 R4 and the stress runs at `8107c0f`, tree clean; every manifest
  says `8107c0f`. The diagnostics, review, report cards, comparisons and G4 draw ran at `17ac9cd` (the approved
  amendment, section 1.1): the exact HEAD check, tree clean. The execution code is unchanged between the two commits;
  the diff touches only gex_v3's level check, its tests, the check files and the logs.
- **Plan hashes.** `git show <commit>:Book1A/Phase3/plan_hashes_phase3.md` sha256
  `60206aa54fb142cd281530151eac78f1f3c75f674ac844c737633f4674608f1e` at both `8107c0f` and `17ac9cd` (= registered);
  C2 table `a7ece816e86101945a1b17e2f4b7bbbf9614615ccbcb659343c2777a08f86c13` at both (= registered).
- **Plan rebuild.** Plans rebuilt from the Step B R1 run's own map packets: base 82 files, 0 different; C2 82 files,
  0 different. Step B packets vs Step A packets (body without built_local): 41, 0 different.
- **plan_sha256 on the rows.** The column is present with 0 mismatches in the R4 ledger (42 rows), R4_candidates
  (28919), the C2 R4 ledger (43) and C2 R4_candidates (29061).
- **Unit tests** at `17ac9cd`: 428 run, OK (`runs/g1/unit_tests/unit_tests_2026-11-09.log`).
- **Look-ahead audit** (`book1a.audit_run`):

  | ledger | decisions | inputs | violations | missing |
  |---|---|---|---|---|
  | R1 | 63 | 1460 | 0 | 0 |
  | R2 | 28 | 651 | 0 | 0 |
  | R3 | 20 | 458 | 0 | 0 |
  | R4 | 42 | 1021 | 0 | 0 |
  | C2 R4 | 43 | 1065 | 0 | 0 |

  Plan build checks: 377 per run, 0 failed. D2 audit of every AT_ENTRY field: 188141 groups, 0 violations.
- **Earlier ledgers unchanged.** The four Phase 1 ledgers and the four Phase 2 ledgers all equal their registered
  sha256 (`runs/g1/g1_prior_ledgers.log`).

**G2 Coverage: met.** 41 / 41 sessions, each equal to the registered list, in: the R1 / R2 run, the R3 run, the R4 run,
the C2 R4 run, the daily-loop config and the three stress runs. No coverage exception. Dec 17 and Dec 18 were run and
counted in every strategy.

**G3 Risk: met.** risk-c3-v2 is on every R3, R4 and C2 R4 row, with 0 non-ACCEPT ledger rows and **0 planned-risk
violations** (R3 20 rows, R4 42, C2 R4 43). Execution breaches are reported (section 2): R3 1, R4 4, largest $52.22 over
the budget. RISK_BREACH_FILL: R3 6, R4 7, largest realized overrun $40.00 (logged only).

**G4 Checker reproduction: open (the checker's step).** The sample: `g4_draw.py` v1.1 run unchanged (script sha256
`3444ec3d276bbf89b26fd444979821a004ce31863eef070e2f81e3e9397d8403`, seed 20251205, numpy 2.5.3):
- FIXED_DAY 5: every R4 trade on Dec 10 (3), Dec 18 (2), Jan 14 (0) and Jan 29 (0);
- DRAW_R4 10 from the other 37 sessions; DRAW_R1R3 10;
- 25 rows; sample sha256 `ee0aa154ad87ae28a81b2cc2ac957930ad149837434f02efee0314a2db19ddfa`.

The pack is `Book1A/Phase3/checker_input/`: 44 files plus `pack_manifest.json`, zipped as
`Phase3_G4_checker_pack.zip`. It holds the sample, the full ledgers, the R1 / R2 checker ledgers, the C2 R4 ledger,
the attempts, retests and risk events, the 12 stress ledgers with their manifests, the run manifests, both report
cards, the comparison results and the review outputs. The runner does not compare anything with the checker.

**G5 Deliverables complete and hashed: met with this commit.** This report, the ledgers (R1-R4 and C2 R4), the review
file, the comparison results and the Phase 4 readiness note (section 8) are hashed in section 9. The report and the
pack are hashed in `Phase3_deliverables_sha256.md`. Ledgers stay out of git (`.gitignore`); they are in the run folders
and the checker pack.

@@SEC8
## 8. Phase 4 readiness note

- **Not started.** Phase 4 ("Phase 4 replay: R1–R4 once, frozen") needs, first, G4 passed by the checker, then Kyron's
  go.
- **Change list.** `Phase3_change_list.md` is final for Phase 3 and was not edited. No item is added or dropped
  because of a Phase 3 outcome (registration section 6).
- **Code Phase 4 would start from.** `17ac9cd` = the frozen `8107c0f` + the gex_v3 diagnostic-check fix. No other
  change is pending. The R1-R4 execution code and the thresholds have not changed since `8107c0f`.
- **Logged only, not fixed.** `diag_phase1b.py` line 906 gives a Python SyntaxWarning (a `\B` in a help string). It
  does not change any output.
- **Open items, unchanged.** N7 / N7a (the Block 2 go / no-go audit) and the Part 3 exposure (Jan 12, 14, 16, 2026)
  carry forward as registered.

@@SEC10
## 10. Access and blinding

- **Book 1 and the checker.** No file of Book 1 or `K:\Book1A_checker` was opened, and no git command ran in
  `K:\Databento_BackTesting`. Inputs came only through `K:\Book1A_inputs`.
- **Before the report.** The Step B gate checks and the fix work showed only mechanics: run metadata, HEAD records,
  ledger sha256, the gex_v3 level flags and GEX input values, row counts, audit counts, G3 counts, the D2 count and
  the G4 counts. Results were first read after stage 2 had finished, to write this report.
- **No changes after results.** No threshold, rule, plan or execution code was changed after any result, and Phase 1
  outcomes were not used. The only code change in Step B (`17ac9cd`) was made and approved before any result was
  opened.
