# Book 1A – Phase 3 report (test changes, replay, in-sample)

Runner: Claude Code desktop session, `K:\Book1A_runner\code`, branch `book1a-phase1`, Nov 8-9, 2026 (Step B, Kyron's
go of Nov 8 and the diagnostics-rerun approval of Nov 9). Controlling docs: `Book1A/Phase3/Phase3_registration.md`
(frozen, tag `book1a-phase3-frozen` = `8107c0f`, with the Nov 9 amendment) and the Book 1A replay plan
(`Book1A/specs/`), sections 5, 6, 8 and 9.

**Label: every number here is "replay (in-sample)".** Never validation. The comparisons are decided on **ALL 41
sessions, "in-sample, includes 3 exposed sessions (Part 3)"**. The 38 UNEXPOSED sessions are a registered
sensitivity: less exposed to prior analysis, not independent, not out-of-sample. ALL and UNEXPOSED are reported
separately and never pooled. Confidence intervals are descriptive uncertainty, not evidence of an edge. Performance
is not a Phase 3 gate. Phase 1 outcomes were not used; no Book 1 result was opened.

## 0. Status

- **Code.** R1-R4, C2 R4 and the three stress settings ran once each, at the frozen commit `8107c0f`, tree clean. The
  diagnostics ran at `17ac9cd`, as did the review, both report cards, the comparisons and the G4 draw.
  `17ac9cd` = `8107c0f` + the approved post-freeze calculation fix to a diagnostic consistency check (section 1.1).
  Nothing in R1-R4, C2 R4 or the stress runs was rerun.
- **Gates (section 7).** **G1, G2, G3 met.** **G4 open**: it is the checker's reproduction; the sample and the pack
  are delivered. **G5 met** with this commit.
- **Primary comparisons (section 5), decided on ALL:** P1 R4 vs R1 **insufficient evidence**; P2 R4 vs R3
  **insufficient evidence**; P3 R3 vs R2 **insufficient evidence**. The UNEXPOSED sensitivity gives the same verdict
  for all three (SAME_VERDICT).
- **Not run, as registered (section 6 table):** L2 and E1 / E2 / E4; M-J3 / M-J4 dropped; grade without CVD not
  needed. MAP4 and the power trade are logged only.
- Stopped and reported before this report: the first diagnostics run stopped on Dec 17-18 (section 1.1). No other
  stop.

## 1. Runs: code, status, inputs

Every run's HEAD and `git status` were recorded just before it ran (`book1a/Phase3/runs/stepB_head_*.txt`). Every
run manifest records its commit. Times UTC (CT = UTC - 6).

| run | output folder (book1a/Phase3/runs/) | HEAD | git status | started (UTC) |
|---|---|---|---|---|
| R1 / R2 (`run_r1_r2 --phase phase3 --fill v3.5`) | phase3 | 8107c0f | clean (0 lines) | 2026-11-09 00:05:46 |
| R3 (`run_r3`) | phase3_r3 | 8107c0f | clean | 00:13:45 |
| R4 (`run_r4 --phase phase3 --candidate-days <41>`) | phase3_r4 | 8107c0f | clean | 00:14:52 |
| C2 R4 (`run_r4 --plans plans_phase3_c2`) | phase3_r4_c2 | 8107c0f | clean | 00:18:55 |
| stress lat1000 / slip2 / slip4 (`run_stress`) | phase3_stress_<setting> | 8107c0f | clean | 00:22:58 / 00:25:33 / 00:28:07 |
| diagnostics, first run (stopped, exit 1) | phase3_diag_partial_stopped_20261109 (archived, renamed) | 8107c0f | clean | 00:30:41 |
| **diagnostics** (`diag_phase1b`, diag-phase1b-v1.2, registered command, new output folder) | phase3_diag_17ac9cd | **17ac9cd** | clean | 03:26:02 |
| unit tests, look-ahead audits (R1-R4, C2 R4), G1-G3 checks | g1 | 17ac9cd | clean | 03:47:42 |
| G4 draw (`g4_draw --phase phase3`, g4-draw-v1.1, unchanged) | ../checker_input | 17ac9cd | clean | 05:22:28 |
| report cards (`phase2_report --phase phase3`, phase2-report-v1.1): R1-R4 with stress; C2 R4 | phase3_report_card.json, phase3_report_card_c2.json | 17ac9cd | clean | 05:22:29 / 05:22:30 |
| section 3 review (`phase2_review_apply --phase phase3`, phase2-review-apply-v1.2) | phase3_review | 17ac9cd | clean | 05:22:31 |
| comparisons (`phase3_compare`, phase3-compare-v1.0) | phase3_compare | 17ac9cd | clean | 05:25:32 |

The commands are the registered ones (registration section 1). There is one difference: the diagnostics output folder
is `phase3_diag_17ac9cd`, not `phase3_diag`, so the rerun cannot be mixed up with the stopped run (Kyron, Nov 9: "a
NEW output folder"). The review reads that folder. All 41 registered sessions are in every run. The stage 2 HEAD
check was exact: `17ac9cd0b503f8bd6c88367fa0cab192a8f0e350`.

### 1.1 Post-freeze calculation fix (commit 17ac9cd), and the diagnostics rerun

Post-freeze calculation fix to a diagnostic consistency check (gex_v3 treated two absent values as a mismatch). Found
in Step B before any result was opened. Tag book1a-phase3-frozen stays on 8107c0f; this commit is listed in the Phase 3
report.

- **What happened.** The first diagnostics run (`8107c0f`) stopped:
  `RuntimeError: gex_v3 does not reproduce gex_levels_block1.csv on ['2025-12-17', '2025-12-18']; stop`
  (`diag_phase1b.py` lines 603-606). On those two sessions the rebuilt 0DTE levels are NaN and the frozen cells are
  empty, because there are no options on the front contract that expire the next session (registration section 1,
  input-file check). The frozen per-level check counted "absent vs absent" as a mismatch. The Step A text had said
  only the V3 flag would mark them; that was wrong, and it is corrected in the registration. I stopped and reported;
  no result file was opened.
- **Fix (Kyron, Nov 9; scope: the missing-value branch only).** `gex_v3.level_match()`: rebuilt absent = None or a
  float NaN; frozen absent = None or empty after strip ('nan' text is not absent; other text still raises). Two absent
  values match; one absent and one present is a mismatch; the tolerance, regime and options_used branches and
  `mq_levels.py` are unchanged. Diff `8107c0f..17ac9cd`: 8 files, 979 insertions, 2 deletions (`gex_v3.py` +15 / -1;
  the new test file; the old-vs-new check script, CSV and text; a unit-test log; the change-log row; the registration
  amendment). The checker verified `17ac9cd` (bridge EXECUTION_RESULT 271483c1) before the rerun.
- **Old-vs-new check** (`Book1A/Phase3/gex_v3_fix_check.py`, `.csv`, `.txt`; GEX inputs only): 62 sessions (21
  Phase 2 + 41 Phase 3), 558 level flags, 6 changed. On the 60 other sessions every flag is identical. On Dec 17-18
  only call_resistance_0dte, put_support_0dte and hvl_0dte changed, N -> Y, each through the both-absent branch
  (rebuilt NaN, frozen ''). ACCEPTANCE: PASS.
- **Rerun.** The partial output folder was renamed `phase3_diag_partial_stopped_20261109` (nothing deleted), and
  `diag_phase1b` was rerun at `17ac9cd` into `phase3_diag_17ac9cd`: exit 0. Every one of the 41 sessions has
  repro_all_match Y. For **Dec 17 and Dec 18, 2025** the three 0DTE levels are **"absent, matching"** (absent in the
  frozen row and absent in the rebuild; not "reproduced"), with n_0dte_options 0 and pin_strike_0dte NaN.
- **Ledgers not touched.** Before the rerun I hashed all 17 ledgers (R1-R4, C2 R4, 12 stress;
  `runs/g1/ledger_sha256_pre_diag_rerun.txt`). Each equals its sha256 recorded at run time: R3, R4 and C2 R4 in their
  run manifests, the stress ledgers in their stress manifests, R1 / R2 in the header of the stopped diagnostics run.
  They were unchanged again after stage 2 (17 / 17 OK). Every diagnostics file header and `diag_manifest.json` name
  the same R1-R4 ledgers: R1 `3a6314dd…`, R2 `e6c92b22…`, R3 `0b1ed31d…`, R4 `0e053e6f…` (full values in section 9).
  The replay and stress manifests keep commit `8107c0f`.

Data conditions and known behaviour (registered before any result, section 1): Dec 15, Dec 24 and Jan 26 plans are
LOG_ONLY, as frozen. No trade has `EXIT_AFTER_SESSION_CLOSE`: no position was open at the Dec 24 12:15 close. All 41
sessions have valid GEX levels (no V5 session).

The report tables were formatted from the JSON / CSV outputs by `runs/report_build/build_phase3_report_md.py`
(formatting only, apart from the items in its docstring: the A4 mj_alignment split and the C2-vs-R4 differing trades
through Book 1's `arms.differing_trades`; sha256 in section 9). The G4 pack was copied by
`runs/report_build/build_g4_pack.py` (copies only).

## 2. Report cards (R1-R4), registration section 2

R is realized net R (ledger `realized_net_R`). R1 / R2 trade qty 1; R3 / R4 use risk-c3-v2 sizing. Fills are v3.5,
costs $5.74 round trip. Max drawdown is measured from a peak starting at 0, over trades in (session, entry time) order.
Bootstrap: 10,000 session resamples, seed 20251205, 5th / 95th percentile.

### 2.1 ALL (41 sessions), replay (in-sample); in-sample, includes 3 exposed sessions (Part 3)

|  | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| trades | 63 | 28 | 20 | 42 |
| trades per session | 1.537 | 0.683 | 0.488 | 1.024 |
| net R per session (realized) | -0.179 | 0.310 | 0.002 | 0.212 |
| 90% session-bootstrap CI | [-0.611, 0.282] | [-0.101, 0.748] | [-0.325, 0.365] | [-0.234, 0.701] |
| theoretical R per session | -0.154 | 0.318 | 0.010 | 0.232 |
| win rate | 0.286 | 0.393 | 0.250 | 0.381 |
| wins / losses / zero | 18 / 45 / 0 | 11 / 17 / 0 | 5 / 15 / 0 | 16 / 26 / 0 |
| average win R | 2.160 | 2.685 | 2.986 | 2.236 |
| average loss R | -1.027 | -0.990 | -0.991 | -1.041 |
| max drawdown R (trade order) | 15.516 | 4.583 | 4.586 | 5.310 |
| max drawdown USD (R3 / R4) | - | - | 3,228.70 | 3,982.58 |
| SUPPLEMENTAL: max drawdown R, session order | 15.516 | 4.583 | 4.586 | 4.495 |
| session dollar P&L, total (R1 / R2 at 1 NQ) | -936.62 | 8,324.28 | 93.92 | 7,114.52 |
| session dollar P&L per session | -22.84 | 203.03 | 2.29 | 173.52 |
| exit reasons | STOP_FIRST 45, TARGET_FIRST 17, TIME_EXIT 1 | STOP_FIRST 16, TARGET_FIRST 10, TIME_EXIT 2 | STOP_FIRST 14, TARGET_FIRST 5, TIME_EXIT 1 | STOP_FIRST 26, TARGET_FIRST 15, TIME_EXIT 1 |
| RISK_REJECT count | - | - | 14 | 13 |
| execution breaches | - | - | 1 | 4 |
| largest execution breach over budget, USD | - | - | 20.18 | 52.22 |
| RISK_BREACH_FILL (realized overrun) count | - | - | 6 | 7 |
| largest realized overrun, USD | - | - | 25.00 | 40.00 |
| RISK_REJECT by reason | - | - | PER_TRADE_BUDGET 14 | PER_TRADE_BUDGET 13 |

Gamma regime split (ALL): trades / net R per session / net R per trade / win rate / net USD

| regime | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| all (41 sessions) | 63 / -0.179 / -0.117 / 0.286 / -936.62 | 28 / 0.310 / 0.454 / 0.393 / 8,324.28 | 20 / 0.002 / 0.003 / 0.250 / 93.92 | 42 / 0.212 / 0.207 / 0.381 / 7,114.52 |
| positive (25 sessions) | 37 / -0.042 / -0.028 / 0.297 / 1,952.62 | 15 / 0.558 / 0.930 / 0.467 / 6,168.90 | 12 / 0.309 / 0.643 / 0.417 / 5,230.58 | 24 / -0.170 / -0.177 / 0.292 / -3,461.62 |
| negative (16 sessions) | 26 / -0.394 / -0.242 / 0.269 / -2,889.24 | 13 / -0.078 / -0.096 / 0.308 / 2,155.38 | 8 / -0.479 / -0.957 / 0.000 / -5,136.66 | 18 / 0.809 / 0.719 / 0.500 / 10,576.14 |

Sessions without valid GEX levels (V5, in "all" only): 0 []

Time of day (ALL, entry fill time CT): trades / net R per session / net R per trade / win rate

| bucket | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 08:30-08:45 | 13 / -0.010 / -0.031 / 0.308 | 4 / -0.017 / -0.173 / 0.250 | 2 / -0.050 / -1.024 / 0.000 | 2 / -0.050 / -1.024 / 0.000 |
| 08:45-10:00 | 35 / 0.014 / 0.016 / 0.314 | 11 / 0.003 / 0.011 / 0.273 | 8 / -0.127 / -0.649 / 0.125 | 25 / 0.179 / 0.293 / 0.360 |
| 10:00-13:00 | 13 / -0.132 / -0.417 / 0.231 | 11 / 0.211 / 0.787 / 0.545 | 8 / 0.066 / 0.336 / 0.375 | 13 / 0.075 / 0.236 / 0.462 |
| 13:00+ | 2 / -0.051 / -1.042 / 0.000 | 2 / 0.112 / 2.306 / 0.500 | 2 / 0.112 / 2.306 / 0.500 | 2 / 0.009 / 0.180 / 0.500 |

Daily table (ALL): trades / session net R / session dollar P&L

| session | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 2025-12-05 | 2 / -2.079 / -666.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-08 | 3 / 3.644 / 1,687.78 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.049 / -692.22 |
| 2025-12-09 | 2 / -2.039 / -1,326.48 | 2 / -2.036 / -1,236.48 | 2 / -2.036 / -1,236.48 | 2 / -2.093 / -1,478.70 |
| 2025-12-10 | 3 / 2.286 / 1,112.78 | 3 / -0.521 / -142.22 | 3 / -0.521 / -142.22 | 3 / -0.525 / -492.96 |
| 2025-12-11 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 3 / 0.390 / 7.78 |
| 2025-12-12 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.014 / -760.74 |
| 2025-12-15 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-16 | 3 / -0.403 / -142.22 | 1 / -1.019 / -565.74 | 1 / -1.019 / -565.74 | 2 / 1.554 / 888.52 |
| 2025-12-17 | 2 / -2.042 / -1,636.48 | 1 / -1.007 / -1,515.74 | 0 / 0.000 / 0.00 | 1 / -1.044 / -767.22 |
| 2025-12-18 | 3 / 2.622 / 2,422.78 | 1 / 1.689 / 2,179.26 | 0 / 0.000 / 0.00 | 2 / 0.360 / 580.56 |
| 2025-12-19 | 2 / -2.031 / -1,491.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-22 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.074 / -778.70 |
| 2025-12-23 | 2 / 3.798 / 2,983.52 | 1 / 2.102 / 2,364.26 | 0 / 0.000 / 0.00 | 3 / 3.645 / 2,586.12 |
| 2025-12-24 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-26 | 2 / -2.082 / -241.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-29 | 2 / -2.053 / -831.48 | 1 / 5.132 / 359.26 | 1 / 5.132 / 3,951.86 | 0 / 0.000 / 0.00 |
| 2025-12-30 | 3 / -0.760 / -652.22 | 2 / -2.096 / -966.48 | 2 / -2.096 / -1,810.92 | 2 / -2.140 / -1,687.40 |
| 2025-12-31 | 1 / 2.363 / 2,859.26 | 1 / 2.363 / 2,859.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-02 | 1 / -1.005 / -2,070.74 | 1 / -1.035 / -315.74 | 1 / -1.035 / -631.48 | 2 / 3.685 / 2,767.04 |
| 2026-01-05 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.058 / -782.96 |
| 2026-01-06 | 3 / -0.341 / 1,347.78 | 2 / 0.733 / 1,413.52 | 1 / -1.015 / -710.74 | 1 / -1.015 / -710.74 |
| 2026-01-07 | 3 / 0.026 / -1,072.22 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-08 | 2 / -2.033 / -2,211.48 | 1 / -1.006 / -1,795.74 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-09 | 2 / -2.044 / -2,041.48 | 1 / 2.475 / 1,324.26 | 1 / 2.475 / 1,324.26 | 2 / -2.144 / -1,451.66 |
| 2026-01-12 (EXPOSED) | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-13 | 3 / 2.107 / 827.78 | 3 / 5.503 / 592.78 | 3 / 4.767 / 3,144.08 | 3 / 2.357 / 1,124.82 |
| 2026-01-14 (EXPOSED) | 2 / -2.049 / -971.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-15 | 1 / -1.018 / -610.74 | 1 / -1.008 / -1,280.74 | 1 / -1.016 / -705.74 | 2 / -2.079 / -1,609.44 |
| 2026-01-16 (EXPOSED) | 2 / -2.052 / -886.48 | 2 / -2.031 / -1,626.48 | 2 / -2.037 / -1,191.48 | 3 / 6.379 / 4,621.30 |
| 2026-01-20 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / 5.363 / 5,306.30 |
| 2026-01-21 | 2 / -2.078 / -826.48 | 1 / 1.602 / 2,339.26 | 0 / 0.000 / 0.00 | 1 / 1.833 / 1,054.26 |
| 2026-01-22 | 3 / -0.458 / -637.22 | 2 / -1.533 / -1,331.48 | 2 / -1.533 / -1,331.48 | 1 / -1.029 / -771.48 |
| 2026-01-23 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / 1.443 / 1,428.52 |
| 2026-01-26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-27 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-28 | 2 / -2.039 / -1,136.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-29 | 1 / 3.224 / 2,434.26 | 1 / 4.395 / 5,669.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-30 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / -2.035 / -1,266.48 |
| 2026-02-02 | 1 / 2.161 / 1,199.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-03 | 3 / 1.050 / 4,057.78 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-04 | 2 / -2.019 / -2,416.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |

### 2.2 UNEXPOSED (38 sessions), replay (in-sample); registered sensitivity, not independent, not out-of-sample

|  | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| trades | 59 | 26 | 18 | 39 |
| trades per session | 1.553 | 0.684 | 0.474 | 1.026 |
| net R per session (realized) | -0.085 | 0.388 | 0.055 | 0.061 |
| 90% session-bootstrap CI | [-0.539, 0.384] | [-0.045, 0.857] | [-0.282, 0.442] | [-0.351, 0.508] |
| theoretical R per session | -0.060 | 0.396 | 0.064 | 0.081 |
| win rate | 0.305 | 0.423 | 0.278 | 0.333 |
| wins / losses / zero | 18 / 41 / 0 | 11 / 15 / 0 | 5 / 13 / 0 | 13 / 26 / 0 |
| average win R | 2.160 | 2.685 | 2.986 | 2.262 |
| average loss R | -1.027 | -0.987 | -0.987 | -1.041 |
| max drawdown R (trade order) | 11.415 | 4.583 | 4.146 | 5.310 |
| max drawdown USD (R3 / R4) | - | - | 3,153.14 | 3,982.58 |
| SUPPLEMENTAL: max drawdown R, session order | 11.415 | 4.583 | 4.146 | 4.495 |
| session dollar P&L, total (R1 / R2 at 1 NQ) | 921.34 | 9,950.76 | 1,285.40 | 2,493.22 |
| session dollar P&L per session | 24.25 | 261.86 | 33.83 | 65.61 |
| exit reasons | STOP_FIRST 41, TARGET_FIRST 17, TIME_EXIT 1 | STOP_FIRST 14, TARGET_FIRST 10, TIME_EXIT 2 | STOP_FIRST 12, TARGET_FIRST 5, TIME_EXIT 1 | STOP_FIRST 26, TARGET_FIRST 12, TIME_EXIT 1 |
| RISK_REJECT count | - | - | 13 | 12 |
| execution breaches | - | - | 1 | 3 |
| largest execution breach over budget, USD | - | - | 20.18 | 52.22 |
| RISK_BREACH_FILL (realized overrun) count | - | - | 5 | 7 |
| largest realized overrun, USD | - | - | 25.00 | 40.00 |
| RISK_REJECT by reason | - | - | PER_TRADE_BUDGET 13 | PER_TRADE_BUDGET 12 |

Gamma regime split (UNEXPOSED): trades / net R per session / net R per trade / win rate / net USD

| regime | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| all (38 sessions) | 59 / -0.085 / -0.055 / 0.305 / 921.34 | 26 / 0.388 / 0.567 / 0.423 / 9,950.76 | 18 / 0.055 / 0.117 / 0.278 / 1,285.40 | 39 / 0.061 / 0.060 / 0.333 / 2,493.22 |
| positive (23 sessions) | 35 / 0.044 / 0.029 / 0.314 / 2,924.10 | 15 / 0.606 / 0.930 / 0.467 / 6,168.90 | 12 / 0.336 / 0.643 / 0.417 / 5,230.58 | 24 / -0.184 / -0.177 / 0.292 / -3,461.62 |
| negative (15 sessions) | 24 / -0.283 / -0.177 / 0.292 / -2,002.76 | 11 / 0.052 / 0.071 / 0.364 / 3,781.86 | 6 / -0.375 / -0.936 / 0.000 / -3,945.18 | 15 / 0.438 / 0.438 / 0.400 / 5,954.84 |

Sessions without valid GEX levels (V5, in "all" only): 0 []

Time of day (UNEXPOSED, entry fill time CT): trades / net R per session / net R per trade / win rate

| bucket | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 08:30-08:45 | 13 / -0.011 / -0.031 / 0.308 | 4 / -0.018 / -0.173 / 0.250 | 2 / -0.054 / -1.024 / 0.000 | 2 / -0.054 / -1.024 / 0.000 |
| 08:45-10:00 | 31 / 0.123 / 0.150 / 0.355 | 10 / 0.030 / 0.114 / 0.300 | 7 / -0.110 / -0.595 / 0.143 | 23 / 0.059 / 0.098 / 0.304 |
| 10:00-13:00 | 13 / -0.143 / -0.417 / 0.231 | 10 / 0.254 / 0.967 / 0.600 | 7 / 0.098 / 0.530 / 0.429 | 12 / 0.046 / 0.147 / 0.417 |
| 13:00+ | 2 / -0.055 / -1.042 / 0.000 | 2 / 0.121 / 2.306 / 0.500 | 2 / 0.121 / 2.306 / 0.500 | 2 / 0.009 / 0.180 / 0.500 |

Daily table (UNEXPOSED): trades / session net R / session dollar P&L

| session | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 2025-12-05 | 2 / -2.079 / -666.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-08 | 3 / 3.644 / 1,687.78 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.049 / -692.22 |
| 2025-12-09 | 2 / -2.039 / -1,326.48 | 2 / -2.036 / -1,236.48 | 2 / -2.036 / -1,236.48 | 2 / -2.093 / -1,478.70 |
| 2025-12-10 | 3 / 2.286 / 1,112.78 | 3 / -0.521 / -142.22 | 3 / -0.521 / -142.22 | 3 / -0.525 / -492.96 |
| 2025-12-11 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 3 / 0.390 / 7.78 |
| 2025-12-12 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.014 / -760.74 |
| 2025-12-15 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-16 | 3 / -0.403 / -142.22 | 1 / -1.019 / -565.74 | 1 / -1.019 / -565.74 | 2 / 1.554 / 888.52 |
| 2025-12-17 | 2 / -2.042 / -1,636.48 | 1 / -1.007 / -1,515.74 | 0 / 0.000 / 0.00 | 1 / -1.044 / -767.22 |
| 2025-12-18 | 3 / 2.622 / 2,422.78 | 1 / 1.689 / 2,179.26 | 0 / 0.000 / 0.00 | 2 / 0.360 / 580.56 |
| 2025-12-19 | 2 / -2.031 / -1,491.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-22 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.074 / -778.70 |
| 2025-12-23 | 2 / 3.798 / 2,983.52 | 1 / 2.102 / 2,364.26 | 0 / 0.000 / 0.00 | 3 / 3.645 / 2,586.12 |
| 2025-12-24 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-26 | 2 / -2.082 / -241.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-29 | 2 / -2.053 / -831.48 | 1 / 5.132 / 359.26 | 1 / 5.132 / 3,951.86 | 0 / 0.000 / 0.00 |
| 2025-12-30 | 3 / -0.760 / -652.22 | 2 / -2.096 / -966.48 | 2 / -2.096 / -1,810.92 | 2 / -2.140 / -1,687.40 |
| 2025-12-31 | 1 / 2.363 / 2,859.26 | 1 / 2.363 / 2,859.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-02 | 1 / -1.005 / -2,070.74 | 1 / -1.035 / -315.74 | 1 / -1.035 / -631.48 | 2 / 3.685 / 2,767.04 |
| 2026-01-05 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / -1.058 / -782.96 |
| 2026-01-06 | 3 / -0.341 / 1,347.78 | 2 / 0.733 / 1,413.52 | 1 / -1.015 / -710.74 | 1 / -1.015 / -710.74 |
| 2026-01-07 | 3 / 0.026 / -1,072.22 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-08 | 2 / -2.033 / -2,211.48 | 1 / -1.006 / -1,795.74 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-09 | 2 / -2.044 / -2,041.48 | 1 / 2.475 / 1,324.26 | 1 / 2.475 / 1,324.26 | 2 / -2.144 / -1,451.66 |
| 2026-01-13 | 3 / 2.107 / 827.78 | 3 / 5.503 / 592.78 | 3 / 4.767 / 3,144.08 | 3 / 2.357 / 1,124.82 |
| 2026-01-15 | 1 / -1.018 / -610.74 | 1 / -1.008 / -1,280.74 | 1 / -1.016 / -705.74 | 2 / -2.079 / -1,609.44 |
| 2026-01-20 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / 5.363 / 5,306.30 |
| 2026-01-21 | 2 / -2.078 / -826.48 | 1 / 1.602 / 2,339.26 | 0 / 0.000 / 0.00 | 1 / 1.833 / 1,054.26 |
| 2026-01-22 | 3 / -0.458 / -637.22 | 2 / -1.533 / -1,331.48 | 2 / -1.533 / -1,331.48 | 1 / -1.029 / -771.48 |
| 2026-01-23 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 1 / 1.443 / 1,428.52 |
| 2026-01-26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-27 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-28 | 2 / -2.039 / -1,136.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-29 | 1 / 3.224 / 2,434.26 | 1 / 4.395 / 5,669.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-30 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 2 / -2.035 / -1,266.48 |
| 2026-02-02 | 1 / 2.161 / 1,199.26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-03 | 3 / 1.050 / 4,057.78 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-04 | 2 / -2.019 / -2,416.48 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |

### 2.3 R4 by mj_alignment (A4 reporting split, descriptive only, never promoted)

Source: `phase3_review.csv` column `mj_alignment` (from diag_exit_trades) and the R4 ledger `realized_net_R`; a missing value = other. trades / net R per session (denominator = the population's session count) / win rate (R > 0 / trades).

mj_alignment values present in the R4 rows: ['EXPLORATORY_NOT_PLAN_ALIGNED', 'NOT_APPLICABLE (plan-zone trade)', 'PLAN_ALIGNED']

| population | mj_alignment | trades | net R per session | win rate |
|---|---|---|---|---|
| ALL | plan zone | 5 | 0.064 | 0.400 |
| ALL | PLAN_ALIGNED | 11 | 0.068 | 0.364 |
| ALL | EXPLORATORY_NOT_PLAN_ALIGNED | 26 | 0.081 | 0.385 |
| ALL | other | 0 | 0.000 | - |
| UNEXPOSED | plan zone | 3 | -0.083 | 0.000 |
| UNEXPOSED | PLAN_ALIGNED | 11 | 0.074 | 0.364 |
| UNEXPOSED | EXPLORATORY_NOT_PLAN_ALIGNED | 25 | 0.071 | 0.360 |
| UNEXPOSED | other | 0 | 0.000 | - |

### 2.4 C2 R4 card: C2 diagnostic (VWAP as a tag only), not promotable, beside R4

ALL (41 sessions):

|  | R4 | C2 R4 |
|---|---|---|
| trades | 42 | 43 |
| trades per session | 1.024 | 1.049 |
| net R per session (realized) | 0.212 | 0.215 |
| 90% session-bootstrap CI | [-0.234, 0.701] | [-0.228, 0.706] |
| theoretical R per session | 0.232 | 0.235 |
| win rate | 0.381 | 0.395 |
| wins / losses / zero | 16 / 26 / 0 | 17 / 26 / 0 |
| average win R | 2.236 | 2.111 |
| average loss R | -1.041 | -1.042 |
| max drawdown R (trade order) | 5.310 | 6.184 |
| max drawdown USD (R3 / R4) | 3,982.58 | 4,897.02 |
| SUPPLEMENTAL: max drawdown R, session order | 4.495 | 5.160 |
| session dollar P&L, total (R1 / R2 at 1 NQ) | 7,114.52 | 6,790.82 |
| session dollar P&L per session | 173.52 | 165.63 |
| exit reasons | STOP_FIRST 26, TARGET_FIRST 15, TIME_EXIT 1 | STOP_FIRST 26, TARGET_FIRST 16, TIME_EXIT 1 |
| RISK_REJECT count | 13 | 13 |
| execution breaches | 4 | 5 |
| largest execution breach over budget, USD | 52.22 | 153.70 |
| RISK_BREACH_FILL (realized overrun) count | 7 | 8 |
| largest realized overrun, USD | 40.00 | 150.00 |
| RISK_REJECT by reason | PER_TRADE_BUDGET 13 | PER_TRADE_BUDGET 13 |

Gamma regime split (ALL): trades / net R per session / net R per trade / win rate / net USD

| regime | R4 | C2 R4 |
|---|---|---|
| all (41 sessions) | 42 / 0.212 / 0.207 / 0.381 / 7,114.52 | 43 / 0.215 / 0.205 / 0.395 / 6,790.82 |
| positive (25 sessions) | 24 / -0.170 / -0.177 / 0.292 / -3,461.62 | 25 / -0.166 / -0.166 / 0.320 / -3,785.32 |
| negative (16 sessions) | 18 / 0.809 / 0.719 / 0.500 / 10,576.14 | 18 / 0.809 / 0.719 / 0.500 / 10,576.14 |

Sessions without valid GEX levels (V5, in "all" only): 0 []

Time of day (ALL, entry fill time CT): trades / net R per session / net R per trade / win rate

| bucket | R4 | C2 R4 |
|---|---|---|
| 08:30-08:45 | 2 / -0.050 / -1.024 / 0.000 | 2 / -0.050 / -1.024 / 0.000 |
| 08:45-10:00 | 25 / 0.179 / 0.293 / 0.360 | 26 / 0.181 / 0.286 / 0.385 |
| 10:00-13:00 | 13 / 0.075 / 0.236 / 0.462 | 13 / 0.075 / 0.236 / 0.462 |
| 13:00+ | 2 / 0.009 / 0.180 / 0.500 | 2 / 0.009 / 0.180 / 0.500 |

Daily table (ALL): trades / session net R / session dollar P&L

| session | R4 | C2 R4 |
|---|---|---|
| 2025-12-05 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-08 | 1 / -1.049 / -692.22 | 1 / -1.049 / -692.22 |
| 2025-12-09 | 2 / -2.093 / -1,478.70 | 2 / -2.093 / -1,478.70 |
| 2025-12-10 | 3 / -0.525 / -492.96 | 3 / -0.525 / -492.96 |
| 2025-12-11 | 3 / 0.390 / 7.78 | 3 / 0.390 / 7.78 |
| 2025-12-12 | 1 / -1.014 / -760.74 | 1 / -1.014 / -760.74 |
| 2025-12-15 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-16 | 2 / 1.554 / 888.52 | 2 / 1.554 / 888.52 |
| 2025-12-17 | 1 / -1.044 / -767.22 | 1 / -1.044 / -767.22 |
| 2025-12-18 | 2 / 0.360 / 580.56 | 2 / 0.360 / 580.56 |
| 2025-12-19 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-22 | 1 / -1.074 / -778.70 | 0 / 0.000 / 0.00 |
| 2025-12-23 | 3 / 3.645 / 2,586.12 | 3 / 3.645 / 2,586.12 |
| 2025-12-24 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-29 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-30 | 2 / -2.140 / -1,687.40 | 2 / -2.140 / -1,687.40 |
| 2025-12-31 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-02 | 2 / 3.685 / 2,767.04 | 2 / 3.685 / 2,767.04 |
| 2026-01-05 | 1 / -1.058 / -782.96 | 1 / -1.058 / -782.96 |
| 2026-01-06 | 1 / -1.015 / -710.74 | 1 / -1.015 / -710.74 |
| 2026-01-07 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-08 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-09 | 2 / -2.144 / -1,451.66 | 2 / -2.144 / -1,451.66 |
| 2026-01-12 (EXPOSED) | 0 / 0.000 / 0.00 | 2 / -0.942 / -1,040.18 |
| 2026-01-13 | 3 / 2.357 / 1,124.82 | 3 / 2.316 / 1,062.60 |
| 2026-01-14 (EXPOSED) | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-15 | 2 / -2.079 / -1,609.44 | 2 / -2.079 / -1,609.44 |
| 2026-01-16 (EXPOSED) | 3 / 6.379 / 4,621.30 | 3 / 6.379 / 4,621.30 |
| 2026-01-20 | 2 / 5.363 / 5,306.30 | 2 / 5.363 / 5,306.30 |
| 2026-01-21 | 1 / 1.833 / 1,054.26 | 1 / 1.833 / 1,054.26 |
| 2026-01-22 | 1 / -1.029 / -771.48 | 1 / -1.029 / -771.48 |
| 2026-01-23 | 1 / 1.443 / 1,428.52 | 1 / 1.443 / 1,428.52 |
| 2026-01-26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-27 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-28 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-29 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-30 | 2 / -2.035 / -1,266.48 | 2 / -2.035 / -1,266.48 |
| 2026-02-02 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-03 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-04 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |

UNEXPOSED (38 sessions):

|  | R4 | C2 R4 |
|---|---|---|
| trades | 39 | 38 |
| trades per session | 1.026 | 1.000 |
| net R per session (realized) | 0.061 | 0.089 |
| 90% session-bootstrap CI | [-0.351, 0.508] | [-0.321, 0.531] |
| theoretical R per session | 0.081 | 0.108 |
| win rate | 0.333 | 0.342 |
| wins / losses / zero | 13 / 26 / 0 | 13 / 25 / 0 |
| average win R | 2.262 | 2.262 |
| average loss R | -1.041 | -1.041 |
| max drawdown R (trade order) | 5.310 | 5.310 |
| max drawdown USD (R3 / R4) | 3,982.58 | 3,982.58 |
| SUPPLEMENTAL: max drawdown R, session order | 4.495 | 4.291 |
| session dollar P&L, total (R1 / R2 at 1 NQ) | 2,493.22 | 3,209.70 |
| session dollar P&L per session | 65.61 | 84.47 |
| exit reasons | STOP_FIRST 26, TARGET_FIRST 12, TIME_EXIT 1 | STOP_FIRST 25, TARGET_FIRST 12, TIME_EXIT 1 |
| RISK_REJECT count | 12 | 12 |
| execution breaches | 3 | 3 |
| largest execution breach over budget, USD | 52.22 | 52.22 |
| RISK_BREACH_FILL (realized overrun) count | 7 | 7 |
| largest realized overrun, USD | 40.00 | 40.00 |
| RISK_REJECT by reason | PER_TRADE_BUDGET 12 | PER_TRADE_BUDGET 12 |

Gamma regime split (UNEXPOSED): trades / net R per session / net R per trade / win rate / net USD

| regime | R4 | C2 R4 |
|---|---|---|
| all (38 sessions) | 39 / 0.061 / 0.060 / 0.333 / 2,493.22 | 38 / 0.089 / 0.089 / 0.342 / 3,209.70 |
| positive (23 sessions) | 24 / -0.184 / -0.177 / 0.292 / -3,461.62 | 23 / -0.139 / -0.139 / 0.304 / -2,745.14 |
| negative (15 sessions) | 15 / 0.438 / 0.438 / 0.400 / 5,954.84 | 15 / 0.438 / 0.438 / 0.400 / 5,954.84 |

Sessions without valid GEX levels (V5, in "all" only): 0 []

Time of day (UNEXPOSED, entry fill time CT): trades / net R per session / net R per trade / win rate

| bucket | R4 | C2 R4 |
|---|---|---|
| 08:30-08:45 | 2 / -0.054 / -1.024 / 0.000 | 2 / -0.054 / -1.024 / 0.000 |
| 08:45-10:00 | 23 / 0.059 / 0.098 / 0.304 | 22 / 0.087 / 0.150 / 0.318 |
| 10:00-13:00 | 12 / 0.046 / 0.147 / 0.417 | 12 / 0.046 / 0.147 / 0.417 |
| 13:00+ | 2 / 0.009 / 0.180 / 0.500 | 2 / 0.009 / 0.180 / 0.500 |

Daily table (UNEXPOSED): trades / session net R / session dollar P&L

| session | R4 | C2 R4 |
|---|---|---|
| 2025-12-05 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-08 | 1 / -1.049 / -692.22 | 1 / -1.049 / -692.22 |
| 2025-12-09 | 2 / -2.093 / -1,478.70 | 2 / -2.093 / -1,478.70 |
| 2025-12-10 | 3 / -0.525 / -492.96 | 3 / -0.525 / -492.96 |
| 2025-12-11 | 3 / 0.390 / 7.78 | 3 / 0.390 / 7.78 |
| 2025-12-12 | 1 / -1.014 / -760.74 | 1 / -1.014 / -760.74 |
| 2025-12-15 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-16 | 2 / 1.554 / 888.52 | 2 / 1.554 / 888.52 |
| 2025-12-17 | 1 / -1.044 / -767.22 | 1 / -1.044 / -767.22 |
| 2025-12-18 | 2 / 0.360 / 580.56 | 2 / 0.360 / 580.56 |
| 2025-12-19 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-22 | 1 / -1.074 / -778.70 | 0 / 0.000 / 0.00 |
| 2025-12-23 | 3 / 3.645 / 2,586.12 | 3 / 3.645 / 2,586.12 |
| 2025-12-24 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-29 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2025-12-30 | 2 / -2.140 / -1,687.40 | 2 / -2.140 / -1,687.40 |
| 2025-12-31 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-02 | 2 / 3.685 / 2,767.04 | 2 / 3.685 / 2,767.04 |
| 2026-01-05 | 1 / -1.058 / -782.96 | 1 / -1.058 / -782.96 |
| 2026-01-06 | 1 / -1.015 / -710.74 | 1 / -1.015 / -710.74 |
| 2026-01-07 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-08 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-09 | 2 / -2.144 / -1,451.66 | 2 / -2.144 / -1,451.66 |
| 2026-01-13 | 3 / 2.357 / 1,124.82 | 3 / 2.316 / 1,062.60 |
| 2026-01-15 | 2 / -2.079 / -1,609.44 | 2 / -2.079 / -1,609.44 |
| 2026-01-20 | 2 / 5.363 / 5,306.30 | 2 / 5.363 / 5,306.30 |
| 2026-01-21 | 1 / 1.833 / 1,054.26 | 1 / 1.833 / 1,054.26 |
| 2026-01-22 | 1 / -1.029 / -771.48 | 1 / -1.029 / -771.48 |
| 2026-01-23 | 1 / 1.443 / 1,428.52 | 1 / 1.443 / 1,428.52 |
| 2026-01-26 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-27 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-28 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-29 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-01-30 | 2 / -2.035 / -1,266.48 | 2 / -2.035 / -1,266.48 |
| 2026-02-02 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-03 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |
| 2026-02-04 | 0 / 0.000 / 0.00 | 0 / 0.000 / 0.00 |

C2 R4 trades that differ from R4, ALL (arms.differing_trades, matched by date and signal time): removed 2, admitted 3, entered / exited differently 0, total 5

C2 R4 trades that differ from R4, UNEXPOSED (arms.differing_trades, matched by date and signal time): removed 2, admitted 1, entered / exited differently 0, total 3

C2 plans that differ from base: 41 of 41 (`families=` field); decision zones 158 (base) -> 156 (C2); decision-zone set changes on 15 days (Step A, registration section 4; plan structure only).

## 3. Stress (separate from the baseline)

The same report-card core from the stress ledgers: the whole replay rerun at entry 1,000 ms, or stop slippage 2 / 4 ticks (risk and daily state included). Baseline rows repeat section 2 for comparison.

ALL:

| strategy | setting | trades | net R per session | 90% CI | max DD R | max DD USD |
|---|---|---|---|---|---|---|
| R1 | baseline (v3.5) | 63 | -0.179 | [-0.611, 0.282] | 15.516 | - |
| R1 | lat1000 | 63 | -0.197 | [-0.618, 0.246] | 15.732 | - |
| R1 | slip2 | 63 | -0.197 | [-0.633, 0.265] | 16.062 | - |
| R1 | slip4 | 63 | -0.232 | [-0.676, 0.235] | 17.333 | - |
| R2 | baseline (v3.5) | 28 | 0.310 | [-0.101, 0.748] | 4.583 | - |
| R2 | lat1000 | 28 | 0.300 | [-0.102, 0.730] | 4.501 | - |
| R2 | slip2 | 28 | 0.306 | [-0.105, 0.745] | 4.631 | - |
| R2 | slip4 | 28 | 0.299 | [-0.114, 0.740] | 4.726 | - |
| R3 | baseline (v3.5) | 20 | 0.002 | [-0.325, 0.365] | 4.586 | 3,228.70 |
| R3 | lat1000 | 20 | -0.006 | [-0.323, 0.347] | 4.604 | 3,258.70 |
| R3 | slip2 | 20 | -0.002 | [-0.329, 0.363] | 4.616 | 3,248.70 |
| R3 | slip4 | 20 | -0.010 | [-0.339, 0.356] | 4.677 | 3,318.14 |
| R4 | baseline (v3.5) | 42 | 0.212 | [-0.234, 0.701] | 5.310 | 3,982.58 |
| R4 | lat1000 | 42 | 0.228 | [-0.232, 0.746] | 5.607 | 4,489.76 |
| R4 | slip2 | 42 | 0.201 | [-0.247, 0.690] | 5.408 | 4,052.58 |
| R4 | slip4 | 42 | 0.177 | [-0.275, 0.670] | 5.732 | 4,554.76 |

UNEXPOSED:

| strategy | setting | trades | net R per session | 90% CI | max DD R | max DD USD |
|---|---|---|---|---|---|---|
| R1 | baseline (v3.5) | 59 | -0.085 | [-0.539, 0.384] | 11.415 | - |
| R1 | lat1000 | 59 | -0.105 | [-0.545, 0.348] | 11.633 | - |
| R1 | slip2 | 59 | -0.103 | [-0.559, 0.369] | 11.915 | - |
| R1 | slip4 | 59 | -0.138 | [-0.601, 0.343] | 13.091 | - |
| R2 | baseline (v3.5) | 26 | 0.388 | [-0.045, 0.857] | 4.583 | - |
| R2 | lat1000 | 26 | 0.377 | [-0.045, 0.833] | 4.501 | - |
| R2 | slip2 | 26 | 0.384 | [-0.049, 0.854] | 4.631 | - |
| R2 | slip4 | 26 | 0.377 | [-0.058, 0.849] | 4.726 | - |
| R3 | baseline (v3.5) | 18 | 0.055 | [-0.282, 0.442] | 4.146 | 3,153.14 |
| R3 | lat1000 | 18 | 0.047 | [-0.281, 0.423] | 4.137 | 3,243.14 |
| R3 | slip2 | 18 | 0.052 | [-0.285, 0.439] | 4.215 | 3,208.14 |
| R3 | slip4 | 18 | 0.044 | [-0.293, 0.433] | 4.351 | 3,318.14 |
| R4 | baseline (v3.5) | 39 | 0.061 | [-0.351, 0.508] | 5.310 | 3,982.58 |
| R4 | lat1000 | 39 | 0.041 | [-0.359, 0.471] | 5.607 | 4,489.76 |
| R4 | slip2 | 39 | 0.049 | [-0.366, 0.497] | 5.408 | 4,052.58 |
| R4 | slip4 | 39 | 0.023 | [-0.395, 0.475] | 5.732 | 4,554.76 |

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

### 4.1 Class counts per strategy

ALL:

| class | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| GAVE_BACK | 9 | 6 | 7 | 6 |
| STOP_THEN_TARGET | 4 | 1 | 1 | 6 |
| NO_POST_STOP_FOLLOW_THROUGH | 16 | 4 | 2 | 6 |
| UNCLASSIFIED | 16 | 5 | 4 | 8 |
| NOT_STOPPED | 18 | 12 | 6 | 16 |

UNEXPOSED:

| class | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| GAVE_BACK | 7 | 5 | 5 | 6 |
| STOP_THEN_TARGET | 2 | 1 | 1 | 6 |
| NO_POST_STOP_FOLLOW_THROUGH | 16 | 3 | 2 | 6 |
| UNCLASSIFIED | 16 | 5 | 4 | 8 |
| NOT_STOPPED | 18 | 12 | 6 | 13 |

Tercile cut-offs (one set from the 41 sessions' own values, both populations): pc_gamma_ratio T1 <= 0.7395 < T2 <= 1.0666 < T3; cr_ps_width T1 <= 1,066.6667 < T2 <= 1,500.0000 < T3

### 4.2 Tag counts per class, ALL (value count; NA = no diagnostics row or field)

R1:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 5; positive 4 | negative 2; positive 2 | negative 6; positive 10 | negative 6; positive 10 | negative 7; positive 11 |
| hvl_side | ABOVE 5; BELOW 4 | ABOVE 2; BELOW 2 | ABOVE 10; BELOW 6 | ABOVE 9; BELOW 7 | ABOVE 9; BELOW 9 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 9 | NOT_APPLICABLE (before 13:00 CT) 4 | N 1; NOT_APPLICABLE (before 13:00 CT) 15 | N 1; NOT_APPLICABLE (before 13:00 CT) 15 | NOT_APPLICABLE (before 13:00 CT) 18 |
| pc_gamma_ratio_tercile | T1 2; T2 2; T3 5 | T1 1; T2 1; T3 2 | T1 5; T2 8; T3 3 | T1 6; T2 4; T3 6 | T1 6; T2 6; T3 6 |
| cr_ps_width_tercile | T1 1; T2 6; T3 2 | T1 1; T2 3 | T1 5; T2 7; T3 4 | T1 6; T2 10 | T1 7; T2 8; T3 3 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 9 | NOT_APPLICABLE (A0 plans carry no ladder) 4 | NOT_APPLICABLE (A0 plans carry no ladder) 16 | NOT_APPLICABLE (A0 plans carry no ladder) 16 | NOT_APPLICABLE (A0 plans carry no ladder) 18 |
| L1_PLAN_SIDE | NA 9 | NA 4 | NA 16 | NA 16 | NA 18 |
| market_context_premarket | BALANCED 3; BEARISH 6 | BALANCED 1; BEARISH 2; BULLISH 1 | BALANCED 5; BEARISH 7; BULLISH 4 | BALANCED 5; BEARISH 6; BULLISH 5 | BALANCED 8; BEARISH 6; BULLISH 4 |
| draw_status_premarket | ACTIVE 6; NONE 3 | ACTIVE 3; NONE 1 | ACTIVE 11; NONE 5 | ACTIVE 9; NONE 7 | ACTIVE 9; NONE 9 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 5; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 8; HIGH_EXHAUSTION 1; NONE 2; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 7; HIGH_EXHAUSTION 1; NONE 3; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 4; HIGH_EXHAUSTION 1; NONE 4; NOT_AT_LOCATION 9 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 5; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 8; NOT_APPLICABLE 3; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 7; NONE 2; NOT_APPLICABLE 2; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 9 |
| atentry_high_with_cvd17 | AGAINST 1; NA 8 | AGAINST 1; NA 3 | NA 15; WITH 1 | NA 15; WITH 1 | AGAINST 1; NA 17 |
| atentry_high_with_cvd0830 | NA 9 | NA 4 | NA 16 | NA 16 | NA 18 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 6 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 5; NOT_AT_LOCATION 9 | EXCLUDED_60MIN 3; NONE 6; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NOT_AT_LOCATION 15 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 6 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 9 | EXCLUDED_60MIN 3; NONE 1; NOT_APPLICABLE 5; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 15 |
| atentry_low_with_cvd17 | NA 9 | NA 4 | NA 16 | NA 16 | AGAINST 1; NA 16; WITH 1 |
| atentry_low_with_cvd0830 | NA 9 | NA 4 | NA 16 | NA 16 | NA 18 |
| prov_high_case_cvd17 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 6 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 3 | HIGH_EXHAUSTION 2; NONE 4; NOT_AT_LOCATION 10 | EXCLUDED_60MIN 3; NONE 2; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; HIGH_EXHAUSTION 1; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 9 |
| prov_high_case_cvd0830 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 6 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 3 | HIGH_EXHAUSTION 1; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 10 | EXCLUDED_60MIN 3; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 9 |
| prov_high_with_cvd17 | NA 9 | NA 3; WITH 1 | AGAINST 1; NA 14; WITH 1 | NA 16 | AGAINST 1; NA 17 |
| prov_high_with_cvd0830 | NA 9 | NA 3; WITH 1 | AGAINST 1; NA 15 | NA 16 | NA 18 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 3; NONE 2; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; LOW_EXHAUSTION 1; NONE 4; NOT_AT_LOCATION 9 | LOW_EXHAUSTION 1; NONE 4; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; LOW_ABSORPTION 2; NOT_AT_LOCATION 11 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 9 | NONE 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; LOW_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 11 |
| prov_low_with_cvd17 | NA 9 | NA 4 | AGAINST 1; NA 15 | NA 15; WITH 1 | AGAINST 1; NA 16; WITH 1 |
| prov_low_with_cvd0830 | NA 9 | NA 4 | NA 16 | NA 16 | AGAINST 1; NA 17 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 4 | NOT_APPLICABLE 4 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 13; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 8; NONE 1; NOT_APPLICABLE 7; NOT_AT_LOCATION 2 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 4 | NOT_APPLICABLE 4 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 8; NONE 1; NOT_APPLICABLE 7; NOT_AT_LOCATION 2 |
| post_high_with_cvd17 | NA 9 | NA 4 | NA 16 | NA 16 | NA 18 |
| post_high_with_cvd0830 | NA 9 | NA 4 | NA 16 | NA 16 | NA 18 |
| post_low_case_cvd17 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 4 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 13; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 4; LOW_ABSORPTION 2; NONE 1; NOT_APPLICABLE 9; NOT_AT_LOCATION 2 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 4 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 11; NOT_AT_LOCATION 2 |
| post_low_with_cvd17 | NA 9 | NA 4 | NA 16 | NA 16 | NA 16; WITH 2 |
| post_low_with_cvd0830 | NA 9 | NA 4 | NA 16 | NA 16 | NA 18 |

R2:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 2; positive 4 | negative 1 | negative 3; positive 1 | negative 2; positive 3 | negative 5; positive 7 |
| hvl_side | ABOVE 3; BELOW 3 | BELOW 1 | ABOVE 2; BELOW 2 | ABOVE 4; BELOW 1 | ABOVE 6; BELOW 6 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 6 | NOT_APPLICABLE (before 13:00 CT) 1 | NOT_APPLICABLE (before 13:00 CT) 4 | NOT_APPLICABLE (before 13:00 CT) 5 | N 2; NOT_APPLICABLE (before 13:00 CT) 10 |
| pc_gamma_ratio_tercile | T1 3; T2 2; T3 1 | T3 1 | T1 1; T3 3 | T1 1; T2 3; T3 1 | T1 5; T2 3; T3 4 |
| cr_ps_width_tercile | T1 2; T2 3; T3 1 | T1 1 | T1 1; T2 2; T3 1 | T1 2; T2 3 | T1 3; T2 6; T3 3 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 6 | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 4 | NOT_APPLICABLE (A0 plans carry no ladder) 5 | NOT_APPLICABLE (A0 plans carry no ladder) 12 |
| L1_PLAN_SIDE | NA 6 | NA 1 | NA 4 | NA 5 | NA 12 |
| market_context_premarket | BALANCED 4; BEARISH 2 | BEARISH 1 | BALANCED 1; BEARISH 3 | BALANCED 2; BEARISH 2; BULLISH 1 | BALANCED 5; BEARISH 5; BULLISH 2 |
| draw_status_premarket | ACTIVE 2; NONE 4 | ACTIVE 1 | ACTIVE 3; NONE 1 | ACTIVE 3; NONE 2 | ACTIVE 7; NONE 5 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 4; HIGH_EXHAUSTION 1; NONE 1 | NONE 1 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 3; HIGH_EXHAUSTION 2; NOT_AT_LOCATION 7 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 3; HIGH_EXHAUSTION 2; NOT_AT_LOCATION 7 |
| atentry_high_with_cvd17 | AGAINST 1; NA 5 | NA 1 | NA 3; WITH 1 | NA 5 | AGAINST 1; NA 10; WITH 1 |
| atentry_high_with_cvd0830 | NA 6 | NA 1 | NA 4 | NA 5 | AGAINST 1; NA 10; WITH 1 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 4 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; LOW_ABSORPTION 2; NOT_AT_LOCATION 8 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 4 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; LOW_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 8 |
| atentry_low_with_cvd17 | NA 6 | NA 1 | NA 4 | NA 5 | NA 10; WITH 2 |
| atentry_low_with_cvd0830 | NA 6 | NA 1 | NA 4 | NA 5 | NA 11; WITH 1 |
| prov_high_case_cvd17 | NONE 2; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 9 |
| prov_high_case_cvd0830 | NONE 2; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 4 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 9 |
| prov_high_with_cvd17 | NA 6 | NA 1 | NA 4 | NA 4; WITH 1 | AGAINST 1; NA 11 |
| prov_high_with_cvd0830 | NA 6 | NA 1 | NA 4 | NA 4; WITH 1 | NA 12 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 2; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 2 | LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 4; LOW_ABSORPTION 1; NONE 2; NOT_AT_LOCATION 5 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 2; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 4; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 5 |
| prov_low_with_cvd17 | NA 5; WITH 1 | NA 1 | NA 4 | NA 4; WITH 1 | NA 11; WITH 1 |
| prov_low_with_cvd0830 | NA 5; WITH 1 | NA 1 | NA 4 | NA 5 | NA 12 |
| post_high_case_cvd17 | NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 2; NOT_APPLICABLE 5; NOT_AT_LOCATION 3 |
| post_high_case_cvd0830 | NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 2; NOT_APPLICABLE 5; NOT_AT_LOCATION 3 |
| post_high_with_cvd17 | NA 6 | NA 1 | NA 4 | NA 4; WITH 1 | NA 12 |
| post_high_with_cvd0830 | NA 6 | NA 1 | NA 4 | NA 4; WITH 1 | NA 12 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 5; LOW_ABSORPTION 2; NOT_APPLICABLE 4; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 5; NOT_APPLICABLE 6; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 5; WITH 1 | NA 1 | NA 4 | NA 4; WITH 1 | NA 10; WITH 2 |
| post_low_with_cvd0830 | NA 5; WITH 1 | NA 1 | NA 4 | NA 5 | NA 12 |

R3:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 4; positive 3 | negative 1 | negative 1; positive 1 | negative 1; positive 3 | negative 1; positive 5 |
| hvl_side | ABOVE 3; BELOW 4 | BELOW 1 | ABOVE 2 | ABOVE 4 | ABOVE 5; BELOW 1 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 7 | NOT_APPLICABLE (before 13:00 CT) 1 | NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 4 | N 2; NOT_APPLICABLE (before 13:00 CT) 4 |
| pc_gamma_ratio_tercile | T1 2; T2 3; T3 2 | T3 1 | T1 1; T3 1 | T1 2; T2 1; T3 1 | T1 4; T2 1; T3 1 |
| cr_ps_width_tercile | T1 2; T2 4; T3 1 | T1 1 | T1 1; T2 1 | T1 2; T2 2 | T1 2; T2 4 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 7 | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 4 | NOT_APPLICABLE (A0 plans carry no ladder) 6 |
| L1_PLAN_SIDE | NA 7 | NA 1 | NA 2 | NA 4 | NA 6 |
| market_context_premarket | BALANCED 3; BEARISH 4 | BEARISH 1 | BALANCED 1; BEARISH 1 | BALANCED 3; BULLISH 1 | BALANCED 4; BEARISH 1; BULLISH 1 |
| draw_status_premarket | ACTIVE 4; NONE 3 | ACTIVE 1 | ACTIVE 1; NONE 1 | ACTIVE 1; NONE 3 | ACTIVE 2; NONE 4 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 3; HIGH_EXHAUSTION 2; NONE 2 | NONE 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 4 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 3; NONE 1; NOT_APPLICABLE 3 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 4 |
| atentry_high_with_cvd17 | AGAINST 2; NA 5 | NA 1 | NA 2 | NA 4 | AGAINST 1; NA 5 |
| atentry_high_with_cvd0830 | NA 7 | NA 1 | NA 2 | NA 4 | AGAINST 1; NA 5 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 4; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 3 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NOT_AT_LOCATION 3 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 4; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 2; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 |
| atentry_low_with_cvd17 | NA 7 | NA 1 | NA 2 | NA 4 | AGAINST 1; NA 4; WITH 1 |
| atentry_low_with_cvd0830 | NA 7 | NA 1 | NA 2 | NA 4 | NA 5; WITH 1 |
| prov_high_case_cvd17 | NONE 2; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 |
| prov_high_case_cvd0830 | NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 |
| prov_high_with_cvd17 | NA 7 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| prov_high_with_cvd0830 | NA 7 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 2; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 1 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 |
| prov_low_with_cvd17 | NA 6; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |
| prov_low_with_cvd0830 | NA 6; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NONE 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 2; NOT_APPLICABLE 4 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 2; NOT_APPLICABLE 4 |
| post_high_with_cvd17 | NA 7 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| post_high_with_cvd0830 | NA 7 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| post_low_case_cvd17 | EXCLUDED_60MIN 2; LOW_ABSORPTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | NONE 1; NOT_APPLICABLE 1 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 2; LOW_ABSORPTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 6; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |
| post_low_with_cvd0830 | NA 6; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |

R4:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 3; positive 3 | negative 3; positive 3 | negative 2; positive 4 | negative 1; positive 7 | negative 9; positive 7 |
| hvl_side | ABOVE 4; BELOW 2 | ABOVE 3; BELOW 3 | ABOVE 4; BELOW 2 | ABOVE 8 | ABOVE 5; BELOW 11 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 6 | NOT_APPLICABLE (before 13:00 CT) 6 | DATA_MISSING (no 0DTE open interest) 1; NOT_APPLICABLE (before 13:00 CT) 5 | NOT_APPLICABLE (before 13:00 CT) 8 | DATA_MISSING (no 0DTE open interest) 1; NOT_APPLICABLE (before 13:00 CT) 15 |
| pc_gamma_ratio_tercile | T1 2; T2 4 | T1 2; T2 1; T3 3 | T1 4; T3 2 | T1 3; T2 4; T3 1 | T1 4; T2 3; T3 9 |
| cr_ps_width_tercile | T1 2; T2 2; T3 2 | T1 2; T2 3; T3 1 | T1 2; T2 4 | T1 3; T2 3; T3 2 | T1 7; T2 8; T3 1 |
| mj_alignment | EXPLORATORY_NOT_PLAN_ALIGNED 4; NOT_APPLICABLE (plan-zone trade) 1; PLAN_ALIGNED 1 | EXPLORATORY_NOT_PLAN_ALIGNED 4; PLAN_ALIGNED 2 | EXPLORATORY_NOT_PLAN_ALIGNED 3; NOT_APPLICABLE (plan-zone trade) 2; PLAN_ALIGNED 1 | EXPLORATORY_NOT_PLAN_ALIGNED 5; PLAN_ALIGNED 3 | EXPLORATORY_NOT_PLAN_ALIGNED 10; NOT_APPLICABLE (plan-zone trade) 2; PLAN_ALIGNED 4 |
| L1_PLAN_SIDE | ALLOWED 1; NA 1; NONE 4 | ALLOWED 2; NONE 4 | ALLOWED 1; NA 2; NONE 3 | ALLOWED 3; NONE 5 | ALLOWED 4; NA 2; NONE 10 |
| market_context_premarket | BALANCED 2; BEARISH 3; BULLISH 1 | BALANCED 3; BEARISH 3 | BALANCED 3; BEARISH 2; BULLISH 1 | BALANCED 5; BEARISH 2; BULLISH 1 | BALANCED 6; BEARISH 9; BULLISH 1 |
| draw_status_premarket | ACTIVE 4; NONE 2 | ACTIVE 3; NONE 3 | ACTIVE 2; NONE 4 | ACTIVE 3; NONE 5 | ACTIVE 10; NONE 6 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 2; NONE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 3; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 2; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 6; HIGH_EXHAUSTION 3; NOT_AT_LOCATION 7 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 3; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 6; HIGH_EXHAUSTION 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 7 |
| atentry_high_with_cvd17 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 6; WITH 1 | NA 13; WITH 3 |
| atentry_high_with_cvd0830 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 7 | NA 15; WITH 1 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 3; LOW_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 4; NOT_AT_LOCATION 12 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 3; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 4; NOT_AT_LOCATION 12 |
| atentry_low_with_cvd17 | NA 5; WITH 1 | NA 6 | NA 6 | NA 8 | NA 16 |
| atentry_low_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |
| prov_high_case_cvd17 | NONE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 4; NOT_APPLICABLE 2; NOT_AT_LOCATION 9 |
| prov_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 4; NOT_APPLICABLE 2; NOT_AT_LOCATION 9 |
| prov_high_with_cvd17 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 7 | NA 16 |
| prov_high_with_cvd0830 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 7 | NA 16 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 14 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 14 |
| prov_low_with_cvd17 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |
| prov_low_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 6 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 7 | NONE 1; NOT_APPLICABLE 13; NOT_AT_LOCATION 2 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | NOT_APPLICABLE 6 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 7 | NONE 1; NOT_APPLICABLE 13; NOT_AT_LOCATION 2 |
| post_high_with_cvd17 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |
| post_high_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | NONE 1; NOT_APPLICABLE 5 | NOT_APPLICABLE 8 | EXCLUDED_60MIN 2; NOT_APPLICABLE 13; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | NOT_APPLICABLE 6 | NOT_APPLICABLE 8 | EXCLUDED_60MIN 2; NOT_APPLICABLE 13; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |
| post_low_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 16 |

### 4.3 Tag counts per class, UNEXPOSED (value count; NA = no diagnostics row or field)

R1:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 4; positive 3 | negative 1; positive 1 | negative 6; positive 10 | negative 6; positive 10 | negative 7; positive 11 |
| hvl_side | ABOVE 5; BELOW 2 | ABOVE 2 | ABOVE 10; BELOW 6 | ABOVE 9; BELOW 7 | ABOVE 9; BELOW 9 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 7 | NOT_APPLICABLE (before 13:00 CT) 2 | N 1; NOT_APPLICABLE (before 13:00 CT) 15 | N 1; NOT_APPLICABLE (before 13:00 CT) 15 | NOT_APPLICABLE (before 13:00 CT) 18 |
| pc_gamma_ratio_tercile | T1 2; T2 1; T3 4 | T1 1; T3 1 | T1 5; T2 8; T3 3 | T1 6; T2 4; T3 6 | T1 6; T2 6; T3 6 |
| cr_ps_width_tercile | T1 1; T2 4; T3 2 | T1 1; T2 1 | T1 5; T2 7; T3 4 | T1 6; T2 10 | T1 7; T2 8; T3 3 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 7 | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 16 | NOT_APPLICABLE (A0 plans carry no ladder) 16 | NOT_APPLICABLE (A0 plans carry no ladder) 18 |
| L1_PLAN_SIDE | NA 7 | NA 2 | NA 16 | NA 16 | NA 18 |
| market_context_premarket | BALANCED 3; BEARISH 4 | BALANCED 1; BULLISH 1 | BALANCED 5; BEARISH 7; BULLISH 4 | BALANCED 5; BEARISH 6; BULLISH 5 | BALANCED 8; BEARISH 6; BULLISH 4 |
| draw_status_premarket | ACTIVE 4; NONE 3 | ACTIVE 1; NONE 1 | ACTIVE 11; NONE 5 | ACTIVE 9; NONE 7 | ACTIVE 9; NONE 9 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 5; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1 | EXCLUDED_60MIN 8; HIGH_EXHAUSTION 1; NONE 2; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 7; HIGH_EXHAUSTION 1; NONE 3; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 4; HIGH_EXHAUSTION 1; NONE 4; NOT_AT_LOCATION 9 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 5; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 8; NOT_APPLICABLE 3; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 7; NONE 2; NOT_APPLICABLE 2; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 4; NOT_AT_LOCATION 9 |
| atentry_high_with_cvd17 | NA 7 | NA 2 | NA 15; WITH 1 | NA 15; WITH 1 | AGAINST 1; NA 17 |
| atentry_high_with_cvd0830 | NA 7 | NA 2 | NA 16 | NA 16 | NA 18 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 5; NOT_AT_LOCATION 9 | EXCLUDED_60MIN 3; NONE 6; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NOT_AT_LOCATION 15 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 9 | EXCLUDED_60MIN 3; NONE 1; NOT_APPLICABLE 5; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 15 |
| atentry_low_with_cvd17 | NA 7 | NA 2 | NA 16 | NA 16 | AGAINST 1; NA 16; WITH 1 |
| atentry_low_with_cvd0830 | NA 7 | NA 2 | NA 16 | NA 16 | NA 18 |
| prov_high_case_cvd17 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 4 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 2; NONE 4; NOT_AT_LOCATION 10 | EXCLUDED_60MIN 3; NONE 2; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; HIGH_EXHAUSTION 1; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 9 |
| prov_high_case_cvd0830 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 4 | HIGH_EXHAUSTION 1; NOT_AT_LOCATION 1 | HIGH_EXHAUSTION 1; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 10 | EXCLUDED_60MIN 3; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 9 |
| prov_high_with_cvd17 | NA 7 | NA 1; WITH 1 | AGAINST 1; NA 14; WITH 1 | NA 16 | AGAINST 1; NA 17 |
| prov_high_with_cvd0830 | NA 7 | NA 1; WITH 1 | AGAINST 1; NA 15 | NA 16 | NA 18 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 3; NOT_AT_LOCATION 4 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; LOW_EXHAUSTION 1; NONE 4; NOT_AT_LOCATION 9 | LOW_EXHAUSTION 1; NONE 4; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; LOW_ABSORPTION 2; NOT_AT_LOCATION 11 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 3; NOT_AT_LOCATION 4 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 9 | NONE 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 11 | EXCLUDED_60MIN 5; LOW_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 11 |
| prov_low_with_cvd17 | NA 7 | NA 2 | AGAINST 1; NA 15 | NA 15; WITH 1 | AGAINST 1; NA 16; WITH 1 |
| prov_low_with_cvd0830 | NA 7 | NA 2 | NA 16 | NA 16 | AGAINST 1; NA 17 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 4 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 13; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 8; NONE 1; NOT_APPLICABLE 7; NOT_AT_LOCATION 2 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 4 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 8; NONE 1; NOT_APPLICABLE 7; NOT_AT_LOCATION 2 |
| post_high_with_cvd17 | NA 7 | NA 2 | NA 16 | NA 16 | NA 18 |
| post_high_with_cvd0830 | NA 7 | NA 2 | NA 16 | NA 16 | NA 18 |
| post_low_case_cvd17 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 13; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 4; LOW_ABSORPTION 2; NONE 1; NOT_APPLICABLE 9; NOT_AT_LOCATION 2 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 14; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 4; NONE 1; NOT_APPLICABLE 11; NOT_AT_LOCATION 2 |
| post_low_with_cvd17 | NA 7 | NA 2 | NA 16 | NA 16 | NA 16; WITH 2 |
| post_low_with_cvd0830 | NA 7 | NA 2 | NA 16 | NA 16 | NA 18 |

R2:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 1; positive 4 | negative 1 | negative 2; positive 1 | negative 2; positive 3 | negative 5; positive 7 |
| hvl_side | ABOVE 3; BELOW 2 | BELOW 1 | ABOVE 2; BELOW 1 | ABOVE 4; BELOW 1 | ABOVE 6; BELOW 6 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 5 | NOT_APPLICABLE (before 13:00 CT) 1 | NOT_APPLICABLE (before 13:00 CT) 3 | NOT_APPLICABLE (before 13:00 CT) 5 | N 2; NOT_APPLICABLE (before 13:00 CT) 10 |
| pc_gamma_ratio_tercile | T1 3; T2 2 | T3 1 | T1 1; T3 2 | T1 1; T2 3; T3 1 | T1 5; T2 3; T3 4 |
| cr_ps_width_tercile | T1 2; T2 2; T3 1 | T1 1 | T1 1; T2 1; T3 1 | T1 2; T2 3 | T1 3; T2 6; T3 3 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 5 | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 3 | NOT_APPLICABLE (A0 plans carry no ladder) 5 | NOT_APPLICABLE (A0 plans carry no ladder) 12 |
| L1_PLAN_SIDE | NA 5 | NA 1 | NA 3 | NA 5 | NA 12 |
| market_context_premarket | BALANCED 4; BEARISH 1 | BEARISH 1 | BALANCED 1; BEARISH 2 | BALANCED 2; BEARISH 2; BULLISH 1 | BALANCED 5; BEARISH 5; BULLISH 2 |
| draw_status_premarket | ACTIVE 1; NONE 4 | ACTIVE 1 | ACTIVE 2; NONE 1 | ACTIVE 3; NONE 2 | ACTIVE 7; NONE 5 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 4; NONE 1 | NONE 1 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 2; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 3; HIGH_EXHAUSTION 2; NOT_AT_LOCATION 7 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 4; NONE 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 3; HIGH_EXHAUSTION 2; NOT_AT_LOCATION 7 |
| atentry_high_with_cvd17 | NA 5 | NA 1 | NA 3 | NA 5 | AGAINST 1; NA 10; WITH 1 |
| atentry_high_with_cvd0830 | NA 5 | NA 1 | NA 3 | NA 5 | AGAINST 1; NA 10; WITH 1 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; LOW_ABSORPTION 2; NOT_AT_LOCATION 8 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 2; NOT_AT_LOCATION 3 | NOT_AT_LOCATION 1 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; LOW_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 8 |
| atentry_low_with_cvd17 | NA 5 | NA 1 | NA 3 | NA 5 | NA 10; WITH 2 |
| atentry_low_with_cvd0830 | NA 5 | NA 1 | NA 3 | NA 5 | NA 11; WITH 1 |
| prov_high_case_cvd17 | NONE 2; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 9 |
| prov_high_case_cvd0830 | NONE 2; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 9 |
| prov_high_with_cvd17 | NA 5 | NA 1 | NA 3 | NA 4; WITH 1 | AGAINST 1; NA 11 |
| prov_high_with_cvd0830 | NA 5 | NA 1 | NA 3 | NA 4; WITH 1 | NA 12 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 1 | LOW_EXHAUSTION 1; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 4; LOW_ABSORPTION 1; NONE 2; NOT_AT_LOCATION 5 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NOT_APPLICABLE 2; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 4; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 5 |
| prov_low_with_cvd17 | NA 4; WITH 1 | NA 1 | NA 3 | NA 4; WITH 1 | NA 11; WITH 1 |
| prov_low_with_cvd0830 | NA 4; WITH 1 | NA 1 | NA 3 | NA 5 | NA 12 |
| post_high_case_cvd17 | NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 2; NOT_APPLICABLE 5; NOT_AT_LOCATION 3 |
| post_high_case_cvd0830 | NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 2; NOT_APPLICABLE 5; NOT_AT_LOCATION 3 |
| post_high_with_cvd17 | NA 5 | NA 1 | NA 3 | NA 4; WITH 1 | NA 12 |
| post_high_with_cvd0830 | NA 5 | NA 1 | NA 3 | NA 4; WITH 1 | NA 12 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 2; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; LOW_EXHAUSTION 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 5; LOW_ABSORPTION 2; NOT_APPLICABLE 4; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 2; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 2 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 5; NOT_APPLICABLE 6; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 4; WITH 1 | NA 1 | NA 3 | NA 4; WITH 1 | NA 10; WITH 2 |
| post_low_with_cvd0830 | NA 4; WITH 1 | NA 1 | NA 3 | NA 5 | NA 12 |

R3:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 2; positive 3 | negative 1 | negative 1; positive 1 | negative 1; positive 3 | negative 1; positive 5 |
| hvl_side | ABOVE 3; BELOW 2 | BELOW 1 | ABOVE 2 | ABOVE 4 | ABOVE 5; BELOW 1 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 5 | NOT_APPLICABLE (before 13:00 CT) 1 | NOT_APPLICABLE (before 13:00 CT) 2 | NOT_APPLICABLE (before 13:00 CT) 4 | N 2; NOT_APPLICABLE (before 13:00 CT) 4 |
| pc_gamma_ratio_tercile | T1 2; T2 3 | T3 1 | T1 1; T3 1 | T1 2; T2 1; T3 1 | T1 4; T2 1; T3 1 |
| cr_ps_width_tercile | T1 2; T2 2; T3 1 | T1 1 | T1 1; T2 1 | T1 2; T2 2 | T1 2; T2 4 |
| mj_alignment | NOT_APPLICABLE (A0 plans carry no ladder) 5 | NOT_APPLICABLE (A0 plans carry no ladder) 1 | NOT_APPLICABLE (A0 plans carry no ladder) 2 | NOT_APPLICABLE (A0 plans carry no ladder) 4 | NOT_APPLICABLE (A0 plans carry no ladder) 6 |
| L1_PLAN_SIDE | NA 5 | NA 1 | NA 2 | NA 4 | NA 6 |
| market_context_premarket | BALANCED 3; BEARISH 2 | BEARISH 1 | BALANCED 1; BEARISH 1 | BALANCED 3; BULLISH 1 | BALANCED 4; BEARISH 1; BULLISH 1 |
| draw_status_premarket | ACTIVE 2; NONE 3 | ACTIVE 1 | ACTIVE 1; NONE 1 | ACTIVE 1; NONE 3 | ACTIVE 2; NONE 4 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 3; NONE 2 | NONE 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 4 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 3; NONE 1; NOT_APPLICABLE 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 4 |
| atentry_high_with_cvd17 | NA 5 | NA 1 | NA 2 | NA 4 | AGAINST 1; NA 5 |
| atentry_high_with_cvd0830 | NA 5 | NA 1 | NA 2 | NA 4 | AGAINST 1; NA 5 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 3; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 3 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; LOW_EXHAUSTION 1; NOT_AT_LOCATION 3 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 3; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 2; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 |
| atentry_low_with_cvd17 | NA 5 | NA 1 | NA 2 | NA 4 | AGAINST 1; NA 4; WITH 1 |
| atentry_low_with_cvd0830 | NA 5 | NA 1 | NA 2 | NA 4 | NA 5; WITH 1 |
| prov_high_case_cvd17 | NONE 2; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 |
| prov_high_case_cvd0830 | NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1 | NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 |
| prov_high_with_cvd17 | NA 5 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| prov_high_with_cvd0830 | NA 5 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | NOT_AT_LOCATION 1 | NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 |
| prov_low_with_cvd17 | NA 4; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |
| prov_low_with_cvd0830 | NA 4; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |
| post_high_case_cvd17 | NONE 2; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 2; NOT_APPLICABLE 4 |
| post_high_case_cvd0830 | NONE 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1 | EXCLUDED_60MIN 1; HIGH_ABSORPTION 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 1 | NONE 2; NOT_APPLICABLE 4 |
| post_high_with_cvd17 | NA 5 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| post_high_with_cvd0830 | NA 5 | NA 1 | NA 2 | NA 3; WITH 1 | NA 6 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | NONE 1; NOT_APPLICABLE 1 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; LOW_ABSORPTION 1; NONE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 1 | NOT_APPLICABLE 2 | NOT_APPLICABLE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 2; NOT_APPLICABLE 3; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 4; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |
| post_low_with_cvd0830 | NA 4; WITH 1 | NA 1 | NA 2 | NA 4 | NA 6 |

R4:

| tag | GAVE_BACK | STOP_THEN_TARGET | NO_POST_STOP_FOLLOW_THROUGH | UNCLASSIFIED | NOT_STOPPED |
|---|---|---|---|---|---|
| gamma_regime | negative 3; positive 3 | negative 3; positive 3 | negative 2; positive 4 | negative 1; positive 7 | negative 6; positive 7 |
| hvl_side | ABOVE 4; BELOW 2 | ABOVE 3; BELOW 3 | ABOVE 4; BELOW 2 | ABOVE 8 | ABOVE 5; BELOW 8 |
| pin_zone | NOT_APPLICABLE (before 13:00 CT) 6 | NOT_APPLICABLE (before 13:00 CT) 6 | DATA_MISSING (no 0DTE open interest) 1; NOT_APPLICABLE (before 13:00 CT) 5 | NOT_APPLICABLE (before 13:00 CT) 8 | DATA_MISSING (no 0DTE open interest) 1; NOT_APPLICABLE (before 13:00 CT) 12 |
| pc_gamma_ratio_tercile | T1 2; T2 4 | T1 2; T2 1; T3 3 | T1 4; T3 2 | T1 3; T2 4; T3 1 | T1 4; T2 3; T3 6 |
| cr_ps_width_tercile | T1 2; T2 2; T3 2 | T1 2; T2 3; T3 1 | T1 2; T2 4 | T1 3; T2 3; T3 2 | T1 7; T2 5; T3 1 |
| mj_alignment | EXPLORATORY_NOT_PLAN_ALIGNED 4; NOT_APPLICABLE (plan-zone trade) 1; PLAN_ALIGNED 1 | EXPLORATORY_NOT_PLAN_ALIGNED 4; PLAN_ALIGNED 2 | EXPLORATORY_NOT_PLAN_ALIGNED 3; NOT_APPLICABLE (plan-zone trade) 2; PLAN_ALIGNED 1 | EXPLORATORY_NOT_PLAN_ALIGNED 5; PLAN_ALIGNED 3 | EXPLORATORY_NOT_PLAN_ALIGNED 9; PLAN_ALIGNED 4 |
| L1_PLAN_SIDE | ALLOWED 1; NA 1; NONE 4 | ALLOWED 2; NONE 4 | ALLOWED 1; NA 2; NONE 3 | ALLOWED 3; NONE 5 | ALLOWED 4; NONE 9 |
| market_context_premarket | BALANCED 2; BEARISH 3; BULLISH 1 | BALANCED 3; BEARISH 3 | BALANCED 3; BEARISH 2; BULLISH 1 | BALANCED 5; BEARISH 2; BULLISH 1 | BALANCED 6; BEARISH 6; BULLISH 1 |
| draw_status_premarket | ACTIVE 4; NONE 2 | ACTIVE 3; NONE 3 | ACTIVE 2; NONE 4 | ACTIVE 3; NONE 5 | ACTIVE 7; NONE 6 |
| atentry_high_case_cvd17 | EXCLUDED_60MIN 2; NONE 3; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 3; NONE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 2; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 5; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 7 |
| atentry_high_case_cvd0830 | EXCLUDED_60MIN 2; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 1 | EXCLUDED_60MIN 3; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 5; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 7 |
| atentry_high_with_cvd17 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 6; WITH 1 | NA 12; WITH 1 |
| atentry_high_with_cvd0830 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 7 | NA 12; WITH 1 |
| atentry_low_case_cvd17 | EXCLUDED_60MIN 3; LOW_ABSORPTION 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 2; NONE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 3; NOT_AT_LOCATION 10 |
| atentry_low_case_cvd0830 | EXCLUDED_60MIN 3; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 4 | EXCLUDED_60MIN 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 3; NOT_AT_LOCATION 10 |
| atentry_low_with_cvd17 | NA 5; WITH 1 | NA 6 | NA 6 | NA 8 | NA 13 |
| atentry_low_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |
| prov_high_case_cvd17 | NONE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 7 |
| prov_high_case_cvd0830 | NOT_APPLICABLE 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 3; NOT_AT_LOCATION 2 | EXCLUDED_60MIN 2; HIGH_EXHAUSTION 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 3; NOT_APPLICABLE 2; NOT_AT_LOCATION 7 |
| prov_high_with_cvd17 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 7 | NA 13 |
| prov_high_with_cvd0830 | NA 6 | NA 6 | NA 6 | AGAINST 1; NA 7 | NA 13 |
| prov_low_case_cvd17 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NONE 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 12 |
| prov_low_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 4 | NONE 1; NOT_AT_LOCATION 7 | EXCLUDED_60MIN 1; NOT_AT_LOCATION 12 |
| prov_low_with_cvd17 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |
| prov_low_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |
| post_high_case_cvd17 | EXCLUDED_60MIN 1; NONE 2; NOT_APPLICABLE 1; NOT_AT_LOCATION 2 | NOT_APPLICABLE 6 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 7 | NONE 1; NOT_APPLICABLE 10; NOT_AT_LOCATION 2 |
| post_high_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 2; NOT_AT_LOCATION 2 | NOT_APPLICABLE 6 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | EXCLUDED_60MIN 1; NOT_APPLICABLE 7 | NONE 1; NOT_APPLICABLE 10; NOT_AT_LOCATION 2 |
| post_high_with_cvd17 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |
| post_high_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |
| post_low_case_cvd17 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | NONE 1; NOT_APPLICABLE 5 | NOT_APPLICABLE 8 | EXCLUDED_60MIN 2; NOT_APPLICABLE 10; NOT_AT_LOCATION 1 |
| post_low_case_cvd0830 | EXCLUDED_60MIN 1; NONE 1; NOT_APPLICABLE 1; NOT_AT_LOCATION 3 | EXCLUDED_60MIN 1; NOT_APPLICABLE 5 | NOT_APPLICABLE 6 | NOT_APPLICABLE 8 | EXCLUDED_60MIN 2; NOT_APPLICABLE 10; NOT_AT_LOCATION 1 |
| post_low_with_cvd17 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |
| post_low_with_cvd0830 | NA 6 | NA 6 | NA 6 | NA 8 | NA 13 |

### 4.4 Per trade (review fields; the full row set is phase3_review.csv)

| strategy | trade | entry session | entry | exit reason | class | net R | MFE R | MAE R | post-stop move R | target traded | truncated | exit flag | min init->entry | confirm delta % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | JOFT-20251205-00384 | 2025-12-05 | 10:26:00 | STOP_FIRST | UNCLASSIFIED | -1.0239 | 0.2333 | 0.9778 | 1.6889 | N | N | N | 0.0042 | 22.1293 |
| R1 | JOFT-20251205-00514 | 2025-12-05 | 12:31:00 | STOP_FIRST | UNCLASSIFIED | -1.0551 | 0.2821 | 0.9487 | 1.6154 | N | N | N | 0.0042 | 18.2692 |
| R1 | JOFT-20251208-01164 | 2025-12-08 | 09:24:00 | TARGET_FIRST | NOT_STOPPED | 5.7091 | 5.7108 | 0.9639 | NA | NA | NA | N | 0.0042 | -16.5798 |
| R1 | JOFT-20251208-01405 | 2025-12-08 | 12:59:00 | STOP_FIRST | UNCLASSIFIED | -1.033 | 0.1231 | 0.9846 | 1.4615 | N | N | N | 0.0042 | -14.651 |
| R1 | JOFT-20251208-01407 | 2025-12-08 | 13:00:00 | STOP_FIRST | UNCLASSIFIED | -1.0321 | 0.4478 | 0.9701 | 2.2388 | N | N | N | 0.0042 | 21.8673 |
| R1 | JOFT-20251209-01809 | 2025-12-09 | 08:41:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0117 | 0.2678 | 0.9454 | 0.7869 | N | N | N | 0.0042 | -16.6847 |
| R1 | JOFT-20251209-01880 | 2025-12-09 | 09:04:00 | STOP_FIRST | GAVE_BACK | -1.0275 | 1.6795 | 0.9744 | 1.8077 | N | N | N | 0.0042 | -17.8487 |
| R1 | JOFT-20251210-02380 | 2025-12-10 | 08:36:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0134 | 0.3 | 0.9938 | 0.7937 | N | N | N | 0.0042 | -15.3483 |
| R1 | JOFT-20251210-02426 | 2025-12-10 | 08:50:00 | TARGET_FIRST | NOT_STOPPED | 1.7816 | 1.7925 | 0.8113 | NA | NA | NA | N | 0.0042 | -19.6629 |
| R1 | JOFT-20251210-02591 | 2025-12-10 | 10:13:00 | TARGET_FIRST | NOT_STOPPED | 1.5182 | 1.5271 | 0.0775 | NA | NA | NA | N | 1.0042 | 13.5308 |
| R1 | JOFT-20251216-05544 | 2025-12-16 | 08:51:00 | STOP_FIRST | UNCLASSIFIED | -1.0101 | 0.7512 | 0.9906 | 1.6667 | N | N | N | 0.0042 | 18.892 |
| R1 | JOFT-20251216-05596 | 2025-12-16 | 09:10:00 | TARGET_FIRST | NOT_STOPPED | 1.6218 | 1.6225 | 0.402 | NA | NA | NA | N | 0.0042 | -19.8376 |
| R1 | JOFT-20251216-05638 | 2025-12-16 | 09:26:00 | STOP_FIRST | UNCLASSIFIED | -1.0151 | 0.493 | 0.9789 | 1.0775 | N | N | N | 0.0042 | -10.481 |
| R1 | JOFT-20251217-06403 | 2025-12-17 | 08:50:00 | STOP_FIRST | GAVE_BACK | -1.0115 | 1.0108 | 0.9946 | 0.2151 | N | N | N | 0.0042 | 15.0611 |
| R1 | JOFT-20251217-06572 | 2025-12-17 | 10:13:00 | STOP_FIRST | GAVE_BACK | -1.0307 | 1.0593 | 0.9926 | 2.7926 | N | N | N | 0.0042 | -12.2373 |
| R1 | JOFT-20251218-07274 | 2025-12-18 | 08:49:00 | STOP_FIRST | UNCLASSIFIED | -1.0149 | 0.6528 | 0.9931 | 1.2847 | N | N | N | 0.0042 | -12.2543 |
| R1 | JOFT-20251218-07290 | 2025-12-18 | 08:54:00 | TARGET_FIRST | NOT_STOPPED | 1.7198 | 1.7235 | 0.8199 | NA | NA | NA | N | 1.0042 | 3.108 |
| R1 | JOFT-20251218-07492 | 2025-12-18 | 11:05:00 | TARGET_FIRST | NOT_STOPPED | 1.917 | 1.94 | 0.16 | NA | NA | NA | N | 0.0042 | -16.4444 |
| R1 | JOFT-20251219-08190 | 2025-12-19 | 08:44:00 | STOP_FIRST | GAVE_BACK | -1.0118 | 2.011 | 0.956 | 2.1429 | N | N | N | 0.0042 | 16.8626 |
| R1 | JOFT-20251219-08337 | 2025-12-19 | 10:07:00 | STOP_FIRST | GAVE_BACK | -1.0192 | 1.1429 | 0.9911 | 2.4107 | N | N | N | 0.0042 | 26.4803 |
| R1 | JOFT-20251223-09609 | 2025-12-23 | 08:51:00 | TARGET_FIRST | NOT_STOPPED | 1.6966 | 1.7123 | 0.8219 | NA | NA | NA | N | 0.0042 | -20.6674 |
| R1 | JOFT-20251223-09657 | 2025-12-23 | 09:17:00 | TARGET_FIRST | NOT_STOPPED | 2.1016 | 2.1022 | 0.2089 | NA | NA | NA | N | 1.0042 | 20.7154 |
| R1 | JOFT-20251226-10414 | 2025-12-26 | 09:32:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0296 | NA | NA | 19.8 | Y | N | N | 0.0042 | 14.1935 |
| R1 | JOFT-20251226-10556 | 2025-12-26 | 13:49:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0524 | 0.9512 | 0.9756 | 0.3902 | N | N | N | 0.0042 | 28.9649 |
| R1 | JOFT-20251229-10832 | 2025-12-29 | 08:54:00 | STOP_FIRST | UNCLASSIFIED | -1.025 | 0.907 | 0.9884 | 1.7326 | N | N | N | 0.0042 | 11.473 |
| R1 | JOFT-20251229-10872 | 2025-12-29 | 09:12:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0283 | 0.6053 | 0.9605 | 0.1316 | N | N | N | 0.0042 | -21.2032 |
| R1 | JOFT-20251230-11486 | 2025-12-30 | 08:37:00 | STOP_FIRST | UNCLASSIFIED | -1.0132 | 0.4417 | 0.9939 | 1.2209 | N | N | N | 1.0042 | -3.9872 |
| R1 | JOFT-20251230-11538 | 2025-12-30 | 09:12:00 | TARGET_FIRST | NOT_STOPPED | 1.318 | 1.1698 | 0.0377 | NA | NA | NA | N | 0.0042 | -17.3313 |
| R1 | JOFT-20251230-11688 | 2025-12-30 | 10:51:00 | STOP_FIRST | GAVE_BACK | -1.0651 | 3.4545 | 0.9091 | 3.5152 | N | N | N | 0.0042 | -19.5076 |
| R1 | JOFT-20251231-12190 | 2025-12-31 | 08:38:00 | TIME_EXIT | NOT_STOPPED | 2.363 | 2.5289 | 0.2479 | NA | NA | NA | N | 1.0042 | -9.1618 |
| R1 | JOFT-20260102-12827 | 2026-01-02 | 08:34:00 | STOP_FIRST | UNCLASSIFIED | -1.0052 | 0.1845 | 0.9976 | 1.9879 | N | N | N | 1.0042 | -5.292 |
| R1 | JOFT-20260106-14727 | 2026-01-06 | 08:41:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0178 | 0.5124 | 0.9339 | 0.0661 | N | N | N | 0.0042 | -12.3093 |
| R1 | JOFT-20260106-14745 | 2026-01-06 | 08:45:00 | TARGET_FIRST | NOT_STOPPED | 1.7484 | 1.7202 | 0.1029 | NA | NA | NA | N | 1.0042 | 32.1306 |
| R1 | JOFT-20260106-14864 | 2026-01-06 | 09:39:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0716 | 0.1667 | 0.9333 | 0.5667 | N | N | N | 0.0042 | 15.0123 |
| R1 | JOFT-20260107-15703 | 2026-01-07 | 09:28:00 | TARGET_FIRST | NOT_STOPPED | 2.1361 | 2.0233 | 0.0465 | NA | NA | NA | N | 0.0042 | 25.0774 |
| R1 | JOFT-20260107-15736 | 2026-01-07 | 09:39:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0076 | 0.2313 | 0.9929 | 0.0605 | N | N | N | 0.0042 | -30.5482 |
| R1 | JOFT-20260107-15834 | 2026-01-07 | 11:26:00 | STOP_FIRST | UNCLASSIFIED | -1.1023 | 0.9524 | 0.9524 | 5.2381 | N | N | N | 0.0042 | -26.9122 |
| R1 | JOFT-20260108-16321 | 2026-01-08 | 08:44:00 | STOP_FIRST | UNCLASSIFIED | -1.006 | 0.619 | 0.958 | 1.1513 | N | N | N | 1.0042 | -1.9555 |
| R1 | JOFT-20260108-16420 | 2026-01-08 | 09:29:00 | STOP_FIRST | UNCLASSIFIED | -1.0265 | 0.0 | 0.9877 | 1.0494 | N | N | N | 0.0042 | 19.4638 |
| R1 | JOFT-20260109-17367 | 2026-01-09 | 08:49:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0068 | 0.8836 | 0.9811 | 0.4182 | N | N | N | 0.0042 | -18.8221 |
| R1 | JOFT-20260109-17557 | 2026-01-09 | 09:32:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.037 | 0.5765 | 0.9882 | 0.5412 | N | N | N | 0.0042 | 14.2388 |
| R1 | JOFT-20260113-19538 | 2026-01-13 | 08:43:00 | TARGET_FIRST | NOT_STOPPED | 1.6347 | 1.1705 | 0.1477 | NA | NA | NA | N | 0.0042 | -10.3272 |
| R1 | JOFT-20260113-19541 | 2026-01-13 | 08:44:00 | TARGET_FIRST | NOT_STOPPED | 1.4807 | 1.3862 | 0.6508 | NA | NA | NA | N | 0.0042 | -17.7489 |
| R1 | JOFT-20260113-19619 | 2026-01-13 | 09:03:00 | STOP_FIRST | GAVE_BACK | -1.0084 | 1.5156 | 0.9688 | 0.0312 | N | N | N | 1.0042 | -15.1233 |
| R1 | JOFT-20260114-20423 | 2026-01-14 (EXPOSED) | 08:45:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0316 | 0.4412 | 0.9412 | 6.9559 | Y | N | N | 0.0042 | -10.1438 |
| R1 | JOFT-20260114-20479 | 2026-01-14 (EXPOSED) | 08:59:00 | STOP_FIRST | GAVE_BACK | -1.0176 | 2.1721 | 0.9836 | 1.7623 | N | N | N | 0.0042 | -16.3655 |
| R1 | JOFT-20260115-21326 | 2026-01-15 | 08:45:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0179 | 0.8333 | 0.9833 | 0.8833 | N | N | N | 0.0042 | 13.2025 |
| R1 | JOFT-20260116-22236 | 2026-01-16 (EXPOSED) | 09:22:00 | STOP_FIRST | GAVE_BACK | -1.0209 | 1.4272 | 0.9417 | 0.5631 | N | N | N | 1.0042 | 8.1672 |
| R1 | JOFT-20260116-22290 | 2026-01-16 (EXPOSED) | 09:45:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0307 | 0.1714 | 0.9429 | 5.7286 | Y | N | N | 0.0042 | 13.6 |
| R1 | JOFT-20260121-24899 | 2026-01-21 | 08:49:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0407 | 0.1078 | 0.9804 | 0.3333 | N | N | N | 0.0042 | -12.2647 |
| R1 | JOFT-20260121-24970 | 2026-01-21 | 10:12:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0377 | 0.9298 | 0.9825 | 0.807 | N | N | N | 0.0042 | 13.7931 |
| R1 | JOFT-20260122-25743 | 2026-01-22 | 08:57:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0082 | 0.6882 | 0.9962 | 0.6996 | N | N | N | 1.0042 | -3.3504 |
| R1 | JOFT-20260122-25839 | 2026-01-22 | 10:01:00 | TARGET_FIRST | NOT_STOPPED | 1.6375 | 1.6481 | 0.8981 | NA | NA | NA | N | 0.0042 | 15.5685 |
| R1 | JOFT-20260122-25900 | 2026-01-22 | 10:30:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0874 | 0.6667 | 0.9444 | 3.3056 | Y | N | N | 0.0042 | -17.5858 |
| R1 | JOFT-20260128-29086 | 2026-01-28 | 08:33:00 | STOP_FIRST | UNCLASSIFIED | -1.0192 | 0.2143 | 0.9643 | 1.6875 | N | N | N | 0.0042 | 11.3665 |
| R1 | JOFT-20260128-29290 | 2026-01-28 | 09:38:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0194 | 0.3874 | 0.964 | 0.3874 | N | N | N | 1.0042 | 10.3362 |
| R1 | JOFT-20260129-30173 | 2026-01-29 | 08:36:00 | TARGET_FIRST | NOT_STOPPED | 3.2242 | 3.2252 | 0.1325 | NA | NA | NA | N | 0.0042 | -12.9405 |
| R1 | JOFT-20260202-32222 | 2026-02-02 | 08:47:00 | TARGET_FIRST | NOT_STOPPED | 2.1608 | 2.1532 | 0.955 | NA | NA | NA | N | 0.0042 | 13.1138 |
| R1 | JOFT-20260203-32996 | 2026-02-03 | 08:48:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0188 | 0.4649 | 0.9649 | 0.3772 | N | N | N | 0.0042 | 12.1937 |
| R1 | JOFT-20260203-33007 | 2026-02-03 | 08:56:00 | TARGET_FIRST | NOT_STOPPED | 3.1027 | 3.1031 | 0.0156 | NA | NA | NA | N | 1.0042 | -11.1111 |
| R1 | JOFT-20260203-33232 | 2026-02-03 | 11:26:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0341 | 0.0159 | 0.9841 | 0.3651 | N | N | N | 0.0042 | 17.1247 |
| R1 | JOFT-20260204-33687 | 2026-02-04 | 08:32:00 | STOP_FIRST | UNCLASSIFIED | -1.0116 | 0.7297 | 0.9892 | 4.373 | N | N | N | 0.0042 | -16.0189 |
| R1 | JOFT-20260204-33781 | 2026-02-04 | 09:24:00 | STOP_FIRST | UNCLASSIFIED | -1.0073 | 0.5578 | 0.9966 | 1.0986 | N | N | N | 0.0042 | 11.4035 |
| R2 | JOFT-20251209-01813 | 2025-12-09 | 08:45:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0197 | 0.789 | 0.9908 | 0.9817 | N | N | N | 1.0042 | -8.0439 |
| R2 | JOFT-20251209-01882 | 2025-12-09 | 09:05:00 | STOP_FIRST | UNCLASSIFIED | -1.016 | 0.5597 | 0.9851 | 1.0522 | N | N | N | 1.0042 | -8.6347 |
| R2 | JOFT-20251210-02447 | 2025-12-10 | 09:04:00 | STOP_FIRST | GAVE_BACK | -1.0219 | 1.1735 | 0.9898 | 0.9796 | N | N | N | 4.0042 | 11.5456 |
| R2 | JOFT-20251210-02591 | 2025-12-10 | 10:13:00 | TARGET_FIRST | NOT_STOPPED | 1.5182 | 1.5271 | 0.0775 | NA | NA | NA | N | 1.0042 | 13.5308 |
| R2 | JOFT-20251210-02636 | 2025-12-10 | 10:50:00 | STOP_FIRST | GAVE_BACK | -1.0176 | 1.3852 | 0.9836 | 0.7541 | N | N | N | 1.0042 | 7.3406 |
| R2 | JOFT-20251216-05596 | 2025-12-16 | 09:11:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0194 | 0.2252 | 0.955 | 5.7838 | Y | N | N | 1.0042 | -8.0173 |
| R2 | JOFT-20251217-06418 | 2025-12-17 | 08:58:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0071 | 0.1628 | 0.9867 | 0.0897 | N | N | N | 1.0042 | 13.1711 |
| R2 | JOFT-20251218-07569 | 2025-12-18 | 11:35:00 | TARGET_FIRST | NOT_STOPPED | 1.6893 | 1.6899 | 0.2597 | NA | NA | NA | N | 1.0042 | 4.0435 |
| R2 | JOFT-20251223-09657 | 2025-12-23 | 09:17:00 | TARGET_FIRST | NOT_STOPPED | 2.1016 | 2.1022 | 0.2089 | NA | NA | NA | N | 1.0042 | 20.7154 |
| R2 | JOFT-20251229-11310 | 2025-12-29 | 13:26:00 | TARGET_FIRST | NOT_STOPPED | 5.1323 | 5.2143 | 0.0714 | NA | NA | NA | N | 3.0042 | -12.7517 |
| R2 | JOFT-20251230-11486 | 2025-12-30 | 08:37:00 | STOP_FIRST | UNCLASSIFIED | -1.0132 | 0.4417 | 0.9939 | 1.2209 | N | N | N | 1.0042 | -3.9872 |
| R2 | JOFT-20251230-11688 | 2025-12-30 | 10:53:00 | STOP_FIRST | GAVE_BACK | -1.0826 | 4.0769 | 0.9615 | 3.8846 | N | N | N | 2.0042 | -1.4493 |
| R2 | JOFT-20251231-12190 | 2025-12-31 | 08:38:00 | TIME_EXIT | NOT_STOPPED | 2.363 | 2.5289 | 0.2479 | NA | NA | NA | N | 1.0042 | -9.1618 |
| R2 | JOFT-20260102-12879 | 2026-01-02 | 08:41:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0352 | 0.5738 | 0.9508 | 0.7213 | N | N | N | 1.0042 | -11.7647 |
| R2 | JOFT-20260106-14745 | 2026-01-06 | 08:45:00 | TARGET_FIRST | NOT_STOPPED | 1.7484 | 1.7202 | 0.1029 | NA | NA | NA | N | 1.0042 | 32.1306 |
| R2 | JOFT-20260106-14933 | 2026-01-06 | 10:02:00 | STOP_FIRST | GAVE_BACK | -1.0153 | 1.0357 | 0.9929 | 0.2714 | N | N | N | 1.0042 | -11.6152 |
| R2 | JOFT-20260108-16321 | 2026-01-08 | 08:44:00 | STOP_FIRST | UNCLASSIFIED | -1.006 | 0.619 | 0.958 | 1.1513 | N | N | N | 1.0042 | -1.9555 |
| R2 | JOFT-20260109-17815 | 2026-01-09 | 12:30:00 | TARGET_FIRST | NOT_STOPPED | 2.4753 | 2.486 | 0.0561 | NA | NA | NA | N | 1.0042 | 25.1546 |
| R2 | JOFT-20260113-19619 | 2026-01-13 | 09:03:00 | STOP_FIRST | GAVE_BACK | -1.0084 | 1.5156 | 0.9688 | 0.0312 | N | N | N | 1.0042 | -15.1233 |
| R2 | JOFT-20260113-19842 | 2026-01-13 | 10:46:00 | TARGET_FIRST | NOT_STOPPED | 3.8424 | 3.8718 | 0.7436 | NA | NA | NA | N | 3.0042 | 1.5448 |
| R2 | JOFT-20260113-20019 | 2026-01-13 | 12:45:00 | TARGET_FIRST | NOT_STOPPED | 2.6688 | 2.5765 | 0.8941 | NA | NA | NA | N | 1.0042 | -11.6915 |
| R2 | JOFT-20260115-21362 | 2026-01-15 | 08:55:00 | STOP_FIRST | UNCLASSIFIED | -1.0085 | 0.189 | 0.9843 | 1.315 | N | N | N | 1.0042 | 10.371 |
| R2 | JOFT-20260116-22236 | 2026-01-16 (EXPOSED) | 09:22:00 | STOP_FIRST | GAVE_BACK | -1.0209 | 1.4272 | 0.9417 | 0.5631 | N | N | N | 1.0042 | 8.1672 |
| R2 | JOFT-20260116-22325 | 2026-01-16 (EXPOSED) | 10:04:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0099 | 0.1193 | 0.9954 | 0.656 | N | N | N | 1.0042 | -14.0952 |
| R2 | JOFT-20260121-24995 | 2026-01-21 | 10:38:00 | TARGET_FIRST | NOT_STOPPED | 1.6022 | 1.6062 | 0.0137 | NA | NA | NA | N | 1.0042 | -5.7513 |
| R2 | JOFT-20260122-26123 | 2026-01-22 | 12:59:00 | STOP_FIRST | UNCLASSIFIED | -1.0123 | 0.0057 | 0.9828 | 1.6724 | N | N | N | 1.0042 | -6.2958 |
| R2 | JOFT-20260122-26309 | 2026-01-22 | 14:27:00 | TIME_EXIT | NOT_STOPPED | -0.5211 | 0.9249 | 0.6647 | NA | NA | NA | N | 1.0042 | -1.1392 |
| R2 | JOFT-20260129-30211 | 2026-01-29 | 08:59:00 | TARGET_FIRST | NOT_STOPPED | 4.3948 | 4.3915 | 0.0853 | NA | NA | NA | N | 1.0042 | -9.3134 |
| R3 | JOFT-20251209-01813 | 2025-12-09 | 08:45:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0197 | 0.789 | 0.9908 | 0.9817 | N | N | N | 1.0042 | -8.0439 |
| R3 | JOFT-20251209-01882 | 2025-12-09 | 09:05:00 | STOP_FIRST | UNCLASSIFIED | -1.016 | 0.5597 | 0.9851 | 1.0522 | N | N | N | 1.0042 | -8.6347 |
| R3 | JOFT-20251210-02447 | 2025-12-10 | 09:04:00 | STOP_FIRST | GAVE_BACK | -1.0219 | 1.1735 | 0.9898 | 0.9796 | N | N | N | 4.0042 | 11.5456 |
| R3 | JOFT-20251210-02591 | 2025-12-10 | 10:13:00 | TARGET_FIRST | NOT_STOPPED | 1.5182 | 1.5271 | 0.0775 | NA | NA | NA | N | 1.0042 | 13.5308 |
| R3 | JOFT-20251210-02636 | 2025-12-10 | 10:50:00 | STOP_FIRST | GAVE_BACK | -1.0176 | 1.3852 | 0.9836 | 0.7541 | N | N | N | 1.0042 | 7.3406 |
| R3 | JOFT-20251216-05596 | 2025-12-16 | 09:11:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0194 | 0.2252 | 0.955 | 5.7838 | Y | N | N | 1.0042 | -8.0173 |
| R3 | JOFT-20251229-11310 | 2025-12-29 | 13:26:00 | TARGET_FIRST | NOT_STOPPED | 5.1323 | 5.2143 | 0.0714 | NA | NA | NA | N | 3.0042 | -12.7517 |
| R3 | JOFT-20251230-11486 | 2025-12-30 | 08:37:00 | STOP_FIRST | UNCLASSIFIED | -1.0132 | 0.4417 | 0.9939 | 1.2209 | N | N | N | 1.0042 | -3.9872 |
| R3 | JOFT-20251230-11688 | 2025-12-30 | 10:53:00 | STOP_FIRST | GAVE_BACK | -1.0826 | 4.0769 | 0.9615 | 3.8846 | N | N | N | 2.0042 | -1.4493 |
| R3 | JOFT-20260102-12879 | 2026-01-02 | 08:41:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0352 | 0.5738 | 0.9508 | 0.7213 | N | N | N | 1.0042 | -11.7647 |
| R3 | JOFT-20260106-14933 | 2026-01-06 | 10:02:00 | STOP_FIRST | GAVE_BACK | -1.0153 | 1.0357 | 0.9929 | 0.2714 | N | N | N | 1.0042 | -11.6152 |
| R3 | JOFT-20260109-17815 | 2026-01-09 | 12:30:00 | TARGET_FIRST | NOT_STOPPED | 2.4753 | 2.486 | 0.0561 | NA | NA | NA | N | 1.0042 | 25.1546 |
| R3 | JOFT-20260113-19650 | 2026-01-13 | 09:16:00 | TARGET_FIRST | NOT_STOPPED | 1.9612 | 1.8972 | 0.1776 | NA | NA | NA | N | 1.0042 | -9.4963 |
| R3 | JOFT-20260113-19721 | 2026-01-13 | 09:56:00 | STOP_FIRST | UNCLASSIFIED | -1.037 | 0.9655 | 0.9828 | 3.3448 | N | N | N | 1.0042 | 5.0868 |
| R3 | JOFT-20260113-19842 | 2026-01-13 | 10:46:00 | TARGET_FIRST | NOT_STOPPED | 3.8424 | 3.8718 | 0.7436 | NA | NA | NA | N | 3.0042 | 1.5448 |
| R3 | JOFT-20260115-21379 | 2026-01-15 | 08:59:00 | STOP_FIRST | GAVE_BACK | -1.0155 | 1.2158 | 0.9928 | 3.3237 | Y | N | N | 1.0042 | -0.7102 |
| R3 | JOFT-20260116-22236 | 2026-01-16 (EXPOSED) | 09:22:00 | STOP_FIRST | GAVE_BACK | -1.0209 | 1.4272 | 0.9417 | 0.5631 | N | N | N | 1.0042 | 8.1672 |
| R3 | JOFT-20260116-22376 | 2026-01-16 (EXPOSED) | 10:22:00 | STOP_FIRST | GAVE_BACK | -1.0164 | 1.0687 | 0.9924 | 0.8779 | N | N | N | 1.0042 | 11.2828 |
| R3 | JOFT-20260122-26123 | 2026-01-22 | 12:59:00 | STOP_FIRST | UNCLASSIFIED | -1.0123 | 0.0057 | 0.9828 | 1.6724 | N | N | N | 1.0042 | -6.2958 |
| R3 | JOFT-20260122-26309 | 2026-01-22 | 14:27:00 | TIME_EXIT | NOT_STOPPED | -0.5211 | 0.9249 | 0.6647 | NA | NA | NA | N | 1.0042 | -1.1392 |
| R4 | JOFT-20251208-01080 | 2025-12-08 | 08:47:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0488 | 0.4773 | 0.9545 | 0.5 | N | N | N | 3.0042 | -0.67 |
| R4 | JOFT-20251209-01920 | 2025-12-09 | 08:45:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0197 | 0.789 | 0.9908 | 0.9817 | N | N | N | 1.0042 | -8.0439 |
| R4 | JOFT-20251209-02008 | 2025-12-09 | 09:13:00 | STOP_FIRST | UNCLASSIFIED | -1.0732 | 0.9535 | 0.9767 | 5.0698 | N | N | N | 3.0042 | 7.9284 |
| R4 | JOFT-20251210-02624 | 2025-12-10 | 08:52:00 | STOP_FIRST | GAVE_BACK | -1.0259 | 2.2651 | 0.9759 | 4.3976 | Y | N | N | 2.0042 | -9.9567 |
| R4 | JOFT-20251210-02778 | 2025-12-10 | 10:13:00 | TARGET_FIRST | NOT_STOPPED | 1.5182 | 1.5271 | 0.0775 | NA | NA | NA | N | 1.0042 | 13.5308 |
| R4 | JOFT-20251210-02823 | 2025-12-10 | 10:50:00 | STOP_FIRST | GAVE_BACK | -1.0176 | 1.3852 | 0.9836 | 0.7541 | N | N | N | 1.0042 | 7.3406 |
| R4 | JOFT-20251211-03841 | 2025-12-11 | 09:35:00 | TARGET_FIRST | NOT_STOPPED | 0.9685 | 0.98 | 0.17 | NA | NA | NA | N | 3.0042 | 0.0672 |
| R4 | JOFT-20251211-03906 | 2025-12-11 | 10:01:00 | TARGET_FIRST | NOT_STOPPED | 0.4363 | 0.4453 | 0.3516 | NA | NA | NA | N | 2.0042 | -0.1735 |
| R4 | JOFT-20251211-04100 | 2025-12-11 | 11:58:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0144 | 0.1946 | 0.9799 | 0.396 | N | N | N | 1.0042 | -2.8065 |
| R4 | JOFT-20251212-04687 | 2025-12-12 | 08:48:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0143 | 0.76 | 0.9933 | 4.8133 | Y | N | N | 2.0042 | -12.0879 |
| R4 | JOFT-20251216-06007 | 2025-12-16 | 09:11:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0194 | 0.2252 | 0.955 | 5.7838 | Y | N | N | 1.0042 | -8.0173 |
| R4 | JOFT-20251216-06023 | 2025-12-16 | 09:18:00 | TARGET_FIRST | NOT_STOPPED | 2.5739 | 2.4956 | 0.2478 | NA | NA | NA | N | 2.0042 | 0.4854 |
| R4 | JOFT-20251217-07063 | 2025-12-17 | 09:27:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0438 | 0.551 | 0.9592 | 20.3673 | Y | N | N | 1.0042 | -6.0026 |
| R4 | JOFT-20251218-08325 | 2025-12-18 | 13:02:00 | TARGET_FIRST | NOT_STOPPED | 1.4074 | 1.4262 | 0.3443 | NA | NA | NA | N | 1.0042 | -4.3965 |
| R4 | JOFT-20251218-08424 | 2025-12-18 | 14:07:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0477 | 0.8889 | 0.9556 | 0.5556 | N | N | N | 15.0042 | 0.9412 |
| R4 | JOFT-20251222-09512 | 2025-12-22 | 08:54:00 | STOP_FIRST | GAVE_BACK | -1.0741 | 3.8276 | 0.8966 | 1.3103 | N | N | N | 2.0042 | 6.1463 |
| R4 | JOFT-20251223-10358 | 2025-12-23 | 08:53:00 | TARGET_FIRST | NOT_STOPPED | 2.8719 | 2.8958 | 0.1042 | NA | NA | NA | N | 2.0042 | 1.0446 |
| R4 | JOFT-20251223-10463 | 2025-12-23 | 09:38:00 | TARGET_FIRST | NOT_STOPPED | 1.8382 | 1.8684 | 0.3158 | NA | NA | NA | N | 1.0042 | 4.9231 |
| R4 | JOFT-20251223-10523 | 2025-12-23 | 10:11:00 | STOP_FIRST | UNCLASSIFIED | -1.0651 | 0.6667 | 0.9697 | 1.3636 | N | N | N | 2.0042 | -11.1111 |
| R4 | JOFT-20251230-12359 | 2025-12-30 | 08:37:00 | STOP_FIRST | UNCLASSIFIED | -1.0132 | 0.4417 | 0.9939 | 1.2209 | N | N | N | 1.0042 | -3.9872 |
| R4 | JOFT-20251230-12597 | 2025-12-30 | 10:52:00 | STOP_FIRST | STOP_THEN_TARGET | -1.1264 | -0.1176 | 0.8824 | 7.5882 | Y | N | N | 1.0042 | 0.0 |
| R4 | JOFT-20260102-13864 | 2026-01-02 | 08:41:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0352 | 0.5738 | 0.9508 | 0.7213 | N | N | N | 1.0042 | -11.7647 |
| R4 | JOFT-20260102-13913 | 2026-01-02 | 09:04:00 | TARGET_FIRST | NOT_STOPPED | 4.7202 | 4.7083 | -0.0556 | NA | NA | NA | N | 11.0042 | -10.2479 |
| R4 | JOFT-20260105-14951 | 2026-01-05 | 09:59:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0581 | 0.2703 | 0.9459 | 4.4865 | Y | N | N | 2.0042 | -1.2788 |
| R4 | JOFT-20260106-15973 | 2026-01-06 | 10:02:00 | STOP_FIRST | GAVE_BACK | -1.0153 | 1.0357 | 0.9929 | 0.2714 | N | N | N | 1.0042 | -11.6152 |
| R4 | JOFT-20260109-18456 | 2026-01-09 | 08:52:00 | STOP_FIRST | UNCLASSIFIED | -1.025 | 0.754 | 0.9841 | 3.9841 | N | N | N | 3.0042 | -4.0979 |
| R4 | JOFT-20260109-18749 | 2026-01-09 | 10:18:00 | STOP_FIRST | UNCLASSIFIED | -1.1193 | 0.8889 | 0.9444 | 4.2222 | N | N | N | 4.0042 | 3.0675 |
| R4 | JOFT-20260113-20732 | 2026-01-13 | 08:54:00 | STOP_FIRST | NO_POST_STOP_FOLLOW_THROUGH | -1.0241 | 0.1348 | 0.9775 | 0.6404 | N | N | N | 1.0042 | 11.7616 |
| R4 | JOFT-20260113-20743 | 2026-01-13 | 08:58:00 | TARGET_FIRST | NOT_STOPPED | 4.4262 | 4.4444 | 0.3016 | NA | NA | NA | N | 3.0042 | -5.4688 |
| R4 | JOFT-20260113-20789 | 2026-01-13 | 09:12:00 | STOP_FIRST | STOP_THEN_TARGET | -1.0448 | 0.375 | 0.9792 | 9.1667 | Y | N | N | 2.0042 | -16.9118 |
| R4 | JOFT-20260115-22611 | 2026-01-15 | 08:59:00 | STOP_FIRST | GAVE_BACK | -1.0155 | 1.2158 | 0.9928 | 3.3237 | Y | N | N | 1.0042 | -0.7102 |
| R4 | JOFT-20260115-22792 | 2026-01-15 | 09:46:00 | STOP_FIRST | GAVE_BACK | -1.0632 | 5.6176 | 0.2941 | 1.9412 | N | N | N | 1.0042 | 4.4309 |
| R4 | JOFT-20260116-23431 | 2026-01-16 (EXPOSED) | 09:15:00 | TARGET_FIRST | NOT_STOPPED | 0.5985 | 0.58 | 0.4 | NA | NA | NA | N | 2.0042 | -14.615 |
| R4 | JOFT-20260116-23451 | 2026-01-16 (EXPOSED) | 09:29:00 | TARGET_FIRST | NOT_STOPPED | 4.478 | 4.48 | 0.24 | NA | NA | NA | N | 3.0042 | -7.6383 |
| R4 | JOFT-20260116-23656 | 2026-01-16 (EXPOSED) | 11:46:00 | TARGET_FIRST | NOT_STOPPED | 1.3025 | 1.3137 | 0.451 | NA | NA | NA | N | 15.0042 | -22.8571 |
| R4 | JOFT-20260120-25081 | 2026-01-20 | 11:14:00 | TARGET_FIRST | NOT_STOPPED | 2.0276 | 2.0448 | 0.5672 | NA | NA | NA | N | 5.0042 | 2.7624 |
| R4 | JOFT-20260120-25210 | 2026-01-20 | 12:38:00 | TARGET_FIRST | NOT_STOPPED | 3.3352 | 3.3469 | 0.5102 | NA | NA | NA | N | 1.0042 | -0.7874 |
| R4 | JOFT-20260121-26289 | 2026-01-21 | 10:51:00 | TARGET_FIRST | NOT_STOPPED | 1.8335 | 1.8087 | 0.4348 | NA | NA | NA | N | 6.0042 | -6.2467 |
| R4 | JOFT-20260122-27363 | 2026-01-22 | 11:41:00 | STOP_FIRST | UNCLASSIFIED | -1.0286 | 0.84 | 0.9867 | 1.0667 | N | N | N | 8.0042 | 26.1719 |
| R4 | JOFT-20260123-28060 | 2026-01-23 | 09:18:00 | TIME_EXIT | NOT_STOPPED | 1.4429 | 5.9596 | 0.9899 | NA | NA | NA | N | 2.0042 | -13.0343 |
| R4 | JOFT-20260130-32421 | 2026-01-30 | 08:57:00 | STOP_FIRST | UNCLASSIFIED | -1.0158 | 0.1397 | 0.9559 | 2.0368 | N | N | N | 1.0042 | 5.135 |
| R4 | JOFT-20260130-32448 | 2026-01-30 | 09:05:00 | STOP_FIRST | UNCLASSIFIED | -1.019 | 0.1416 | 0.9823 | 2.6283 | N | N | N | 2.0042 | -4.2518 |

EXIT_AFTER_SESSION_CLOSE trades: none

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

### 5.1 Results (phase3_compare.json)

**P1 R4 vs R1** - deciding population ALL; sensitivity: **SAME_VERDICT**

| population | sessions | mean paired diff R / session | 90% CI (5th, 95th) | max DD arm / comparator R | trades that differ | 2-tick mean diff | checks | verdict |
|---|---|---|---|---|---|---|---|---|
| ALL (in-sample, includes 3 exposed sessions (Part 3)) | 41 | 0.392 | [-0.218, 1.022] | 5.310 / 15.516 | 101 (removed 61, admitted 40, different 0) | 0.397 | bound False, drawdown True, sample True, two_tick True | **insufficient evidence** |
| UNEXPOSED (registered sensitivity on the 38 UNEXPOSED sessions; not independent, not out-of-sample) | 38 | 0.147 | [-0.419, 0.699] | 5.310 / 11.415 | 94 (removed 57, admitted 37, different 0) | 0.152 | bound False, drawdown True, sample True, two_tick True | **insufficient evidence** |

**P2 R4 vs R3** - deciding population ALL; sensitivity: **SAME_VERDICT**

| population | sessions | mean paired diff R / session | 90% CI (5th, 95th) | max DD arm / comparator R | trades that differ | 2-tick mean diff | checks | verdict |
|---|---|---|---|---|---|---|---|---|
| ALL (in-sample, includes 3 exposed sessions (Part 3)) | 41 | 0.211 | [-0.345, 0.805] | 5.310 / 4.586 | 50 (removed 14, admitted 36, different 0) | 0.203 | bound False, drawdown True, sample True, two_tick True | **insufficient evidence** |
| UNEXPOSED (registered sensitivity on the 38 UNEXPOSED sessions; not independent, not out-of-sample) | 38 | 0.006 | [-0.496, 0.521] | 5.310 / 4.146 | 45 (removed 12, admitted 33, different 0) | -0.003 | bound False, drawdown False, sample True, two_tick False | **insufficient evidence** |

**P3 R3 vs R2** - deciding population ALL; sensitivity: **SAME_VERDICT**

| population | sessions | mean paired diff R / session | 90% CI (5th, 95th) | max DD arm / comparator R | trades that differ | 2-tick mean diff | checks | verdict |
|---|---|---|---|---|---|---|---|---|
| ALL (in-sample, includes 3 exposed sessions (Part 3)) | 41 | -0.308 | [-0.567, -0.087] | 4.586 / 4.584 | 16 (removed 12, admitted 4, different 0) | -0.309 | bound False, drawdown True, sample False, two_tick False | **insufficient evidence** |
| UNEXPOSED (registered sensitivity on the 38 UNEXPOSED sessions; not independent, not out-of-sample) | 38 | -0.332 | [-0.605, -0.089] | 4.146 / 4.584 | 14 (removed 11, admitted 3, different 0) | -0.333 | bound False, drawdown True, sample False, two_tick False | **insufficient evidence** |

Paired daily results, ALL (session net R arm - comparator; from the report-card daily tables)

| session | P1 R4-R1 | P2 R4-R3 | P3 R3-R2 |
|---|---|---|---|
| 2025-12-05 | 2.079 | 0.000 | 0.000 |
| 2025-12-08 | -4.693 | -1.049 | 0.000 |
| 2025-12-09 | -0.054 | -0.057 | 0.000 |
| 2025-12-10 | -2.812 | -0.004 | 0.000 |
| 2025-12-11 | 0.390 | 0.390 | 0.000 |
| 2025-12-12 | -1.014 | -1.014 | 0.000 |
| 2025-12-15 | 0.000 | 0.000 | 0.000 |
| 2025-12-16 | 1.958 | 2.574 | 0.000 |
| 2025-12-17 | 0.998 | -1.044 | 1.007 |
| 2025-12-18 | -2.262 | 0.360 | -1.689 |
| 2025-12-19 | 2.031 | 0.000 | 0.000 |
| 2025-12-22 | -1.074 | -1.074 | 0.000 |
| 2025-12-23 | -0.153 | 3.645 | -2.102 |
| 2025-12-24 | 0.000 | 0.000 | 0.000 |
| 2025-12-26 | 2.082 | 0.000 | 0.000 |
| 2025-12-29 | 2.053 | -5.132 | 0.000 |
| 2025-12-30 | -1.379 | -0.044 | 0.000 |
| 2025-12-31 | -2.363 | 0.000 | -2.363 |
| 2026-01-02 | 4.690 | 4.720 | 0.000 |
| 2026-01-05 | -1.058 | -1.058 | 0.000 |
| 2026-01-06 | -0.674 | 0.000 | -1.748 |
| 2026-01-07 | -0.026 | 0.000 | 0.000 |
| 2026-01-08 | 2.033 | 0.000 | 1.006 |
| 2026-01-09 | -0.100 | -4.620 | 0.000 |
| 2026-01-12 (EXPOSED) | 0.000 | 0.000 | 0.000 |
| 2026-01-13 | 0.250 | -2.409 | -0.736 |
| 2026-01-14 (EXPOSED) | 2.049 | 0.000 | 0.000 |
| 2026-01-15 | -1.061 | -1.063 | -0.007 |
| 2026-01-16 (EXPOSED) | 8.431 | 8.416 | -0.006 |
| 2026-01-20 | 5.363 | 5.363 | 0.000 |
| 2026-01-21 | 3.912 | 1.833 | -1.602 |
| 2026-01-22 | -0.571 | 0.505 | 0.000 |
| 2026-01-23 | 1.443 | 1.443 | 0.000 |
| 2026-01-26 | 0.000 | 0.000 | 0.000 |
| 2026-01-27 | 0.000 | 0.000 | 0.000 |
| 2026-01-28 | 2.039 | 0.000 | 0.000 |
| 2026-01-29 | -3.224 | 0.000 | -4.395 |
| 2026-01-30 | -2.035 | -2.035 | 0.000 |
| 2026-02-02 | -2.161 | 0.000 | 0.000 |
| 2026-02-03 | -1.050 | 0.000 | 0.000 |
| 2026-02-04 | 2.019 | 0.000 | 0.000 |

P1 RISK_REJECT / RISK_BREACH_FILL (ALL): R4 13 / 7; R1 - / -

P2 RISK_REJECT / RISK_BREACH_FILL (ALL): R4 13 / 7; R3 14 / 6

P3 RISK_REJECT / RISK_BREACH_FILL (ALL): R3 14 / 6; R2 - / -

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

### 6.1 Diagnostics files (phase3_diag_17ac9cd): data rows (excluding the # header line and the column line)

| file | rows |
|---|---|
| d2_lookahead_audit.json | - |
| d5_cvd_pairs.csv | 0 |
| d5_cvd_pairs_excluded_60min.csv | 0 |
| d5_cvd_swings.csv | 0 |
| diag_cvd_candidates.csv | 41958 |
| diag_cvd_trades.csv | 153 |
| diag_exit_trades.csv | 153 |
| diag_gex_sessions.csv | 41 |
| diag_gex_trades.csv | 153 |
| diag_gex_v3_sessions.csv | 41 |
| diag_gex_zones.csv | 756 |
| diag_l1_plan_side.csv | 8217 |
| diag_manifest.json | - |
| diag_mnq_rejects.csv | 27 |
| diag_sizing_trades.csv | 153 |
| diag_timing.csv | 188141 |
| gex_v3_input_files.csv | 2522 |
| gex_v3_manifest.json | - |

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

## 9. File sha256

Raw bytes as on disk (outputs are not in git). Runs under `book1a/Phase3/runs/`; the pack under `book1a/Phase3/checker_input/`.

| file (under book1a/Phase3/runs/) | bytes | sha256 |
|---|---|---|
| phase3/R1_A0_full.csv | 12781 | 3a6314dd39318cb26005aa4263e099afbe5d9d2e35aa57e525eb3ac1c49a2784 |
| phase3/R2_C1_full.csv | 5848 | e6c92b2274a969017dc6e89690f693d92a772ce43ee1b0d666ff7e7d397a0769 |
| phase3_r3/R3_M0_ledger.csv | 5514 | 0b1ed31db1b4d8e72b69dc5b1c8f6943bbad839046a3346f04a7a7f7eafe1b38 |
| phase3_r4/R4_M0_ledger.csv | 18103 | 0e053e6f88e8ac31bc7c49d5906bb6692b0b089dd6d47601284d19c447fdc7d2 |
| phase3_r4_c2/R4_M0_ledger.csv | 18513 | 9fbdc4289a4a5fc4a1014cfa86441e74123df6dfe90dc315aee20eb806aa20a2 |
| phase3/R1_attempts.csv | 33718 | 26e249ea5d8ca7662064f66a39af20965b9774aa42dd4633abaa146919adf8e9 |
| phase3/R2_attempts.csv | 4744 | ce867c88960d1a9f794d21f87a3682bd1f588933ff84ec26c815523cb7f42c12 |
| phase3/R2_retests.csv | 1852 | ace01ac6a2d61c8c9b19a708d5431c126764bfe5332c2ee49eca23ea3e1b82bd |
| phase3_r3/R3_attempts.csv | 9744 | 88fbb44e1bd3e09077c8e2b8a35dc2a5342e67d4a1f059c08fa12f1eb354d98c |
| phase3_r3/R3_retests.csv | 1905 | 236860e499a3633f6c21dee41e0f53dbc07c72235de606e9b736760c4368cf2f |
| phase3_r3/R3_risk_events.json | 1370 | 3e8b10f2306d97f314a5c4956bb118910ecd99425396dd08594a69263a366761 |
| phase3_r4/R4_attempts.csv | 35510 | c924f7c57edd3a0d2259144d7ef57fcf4fbbb46f62b5a7068af4090d6c3d80aa |
| phase3_r4/R4_candidates.csv | 29029151 | 6705aa2ebb025986a88c130c8122814834d9d15f4879440d5ad20a4f1a197265 |
| phase3_r4/R4_risk_events.json | 2258 | e5ecadecdbdc84c1a15ca60f3246de7ba7bc117557912546e81519c07e60cffe |
| phase3_r4_c2/R4_attempts.csv | 34251 | 03e9ab5b967aa3368a047cf80c80348adfe2d41da340280c0729e8d870aec7f0 |
| phase3_r4_c2/R4_candidates.csv | 29176006 | 32c3971a5ccd2c56fa47df70b52f2c5b1b4a1a722607856f9c59ea99df9b7fa0 |
| phase3_r4_c2/R4_risk_events.json | 2683 | b266842caea4cb6602ae2a3ed5fed77dc38a3310cb688a1f53ee43a631631051 |
| phase3_stress_lat1000/R1_A0_full.csv | 12847 | 1f366d3dc4f51799b4e7ed4c31eb3067b1149720c57fcae4d637e20eb8665d9f |
| phase3_stress_lat1000/R2_C1_full.csv | 5876 | 9726ffc9b16725061f47f1686c955759502b070d72f2092e5ffefe5f0273b35d |
| phase3_stress_lat1000/R3_M0_ledger.csv | 5544 | d4fbea6f28b81aea099ef91332597b0f051f8740c261dae8abb00e135a463ddb |
| phase3_stress_lat1000/R4_M0_ledger.csv | 18145 | 49f321477849af0fe403e2b340e86d25a0a14d49ef7ca6c61ac9fbbc30caf15a |
| phase3_stress_lat1000/stress_manifest.json | 1544 | 0eeebb4acaf77abf14752cf9dca090693cf2b9f351c4607675df2d4a96491143 |
| phase3_stress_slip2/R1_A0_full.csv | 12776 | 986bfbe053a29ee86ec63fe812e755ce584b50342059269d846498666de39a20 |
| phase3_stress_slip2/R2_C1_full.csv | 5846 | fe73e05fbdd8b03e2f341c32a10bfd15820da4aa87f8b6137959084304c59b39 |
| phase3_stress_slip2/R3_M0_ledger.csv | 5514 | cc5e9c27e4661338a70d4d010ac985f4777b38dd1119ac67db2871bcfc20c4ab |
| phase3_stress_slip2/R4_M0_ledger.csv | 18098 | 39221541b0f64a6aaba9966c3c1303ca48d2d53e3f1042b8faeafb6a17054047 |
| phase3_stress_slip2/stress_manifest.json | 1541 | dd982c66877f5767cf44bd6ee3069fee23ce94ff3006c4ae8c74fc1d7ec236a4 |
| phase3_stress_slip4/R1_A0_full.csv | 12776 | d6de8ae0037a5c0b637ecb88ae5b61200a154ff9dbd8710b28ca5485acc67fe6 |
| phase3_stress_slip4/R2_C1_full.csv | 5842 | 6aba6e6e84c01d8434b2c6257cccdda3059469861867e6b18b608a3004634e2d |
| phase3_stress_slip4/R3_M0_ledger.csv | 5510 | cf90d8a8d7d2da710046a1b152b2cbea99d6319316d8b0fce4edbe51db5b58e0 |
| phase3_stress_slip4/R4_M0_ledger.csv | 18097 | 1a1e10786a016359e94de315ff81573b4b13ea830c789c81569d8118317b5e01 |
| phase3_stress_slip4/stress_manifest.json | 1541 | 5929e528ca03328c11b1f65b1100ae83e9aa9576c0a850732911b78746a6ab11 |
| phase3/run_manifest.json | 991 | f9d4c001a46e01498180695c6374fd85a2466bc244da42ba0f0419e5a85c6762 |
| phase3_r3/run_manifest.json | 1296 | d78584acc87a45b95c4a864f35b62108f12b6889e910d4ef8029aa128250060e |
| phase3_r4/run_manifest.json | 2144 | 221c88c88613243ece357e36904e3012197ccd79e87a0bf5a027e5a96e2a601a |
| phase3_r4_c2/run_manifest.json | 2147 | e1469702aa28d9a0d34c8a449f758dd3fe96830e3ab2588b679c64f647374b00 |
| phase3_report_card.json | 76561 | bc8a02c40a3a813e4a6c105cfb49a3f9157dc1b235d07d470ea1d166a4311e99 |
| phase3_report_card_c2.json | 19039 | c36d706866e25d62b0a3dd7f2843f382e708bfdfba8140996a83308dd15aa42b |
| phase3_compare/phase3_compare.json | 6856 | f318bbaae048f3467ed90f4b34931b72a6c3a026f480fd5ac9bf00f1f43f3492 |
| phase3_review/phase3_review.csv | 148911 | 1820a32a6cc142a2dee4d28962bd900d6147356a857ff1d21df506aaf7dc94bd |
| phase3_review/phase3_review_classes.json | 593514 | 26ada59137f9c421b8160008ec3ae1a3084fb0b0f80f51a33c857a8560469084 |
| phase3_review/phase3_review_manifest.json | 22518 | a8bdc336eb6c4f86c053e1c6e77f83165a98b249924da34cbb6116e4468d73ce |
| phase3_diag_17ac9cd/d2_lookahead_audit.json | 356 | d6153cc8665a191342a5850508195b41bd49c8df8497ee75ff1935cd2bdd848d |
| phase3_diag_17ac9cd/d5_cvd_pairs.csv | 471 | 0a9d3180608a3eb51ad2c4eca473c307a0472bdd51acd41eeee7442363943533 |
| phase3_diag_17ac9cd/d5_cvd_pairs_excluded_60min.csv | 471 | 0a9d3180608a3eb51ad2c4eca473c307a0472bdd51acd41eeee7442363943533 |
| phase3_diag_17ac9cd/d5_cvd_swings.csv | 471 | 0a9d3180608a3eb51ad2c4eca473c307a0472bdd51acd41eeee7442363943533 |
| phase3_diag_17ac9cd/diag_cvd_candidates.csv | 44176665 | 019e100b52020e12d695c5f70b4f6cb8feaba4e887f18bd7ca88d7c434b1afdd |
| phase3_diag_17ac9cd/diag_cvd_trades.csv | 175461 | e202d95c464a40f8b8c4097f5fcf82fa61dd25ccd00dd64d20ed9f2fc24d1812 |
| phase3_diag_17ac9cd/diag_exit_trades.csv | 58657 | 5929c700e13b7d1503573b485c79a91f37abd36af602c34d79c8c09c0360c0fe |
| phase3_diag_17ac9cd/diag_gex_sessions.csv | 8380 | 234f9bc42e46f0a52b7e69e9f51b7ca348284cdcd4bc8b7c69368d7f6c4963fd |
| phase3_diag_17ac9cd/diag_gex_trades.csv | 51841 | 970e17008fd4a01c14e5f52ab38dadb6dd183f76bf9a7b1868b65308824062f0 |
| phase3_diag_17ac9cd/diag_gex_v3_sessions.csv | 13233 | 9c689ebb1ed4e30a45780e8f4e2860d8b3ba5299a2bb42377077ce8d16ee1830 |
| phase3_diag_17ac9cd/diag_gex_zones.csv | 237584 | a3f8461e987631dd11f1906b5eb63cf13ebe857d423e5bb424d4a27a65f9f876 |
| phase3_diag_17ac9cd/diag_l1_plan_side.csv | 2430230 | 4ce16c85d8a9691303b3ee38329dfa863cfaeb6b0000e56af43821dd9e0f994a |
| phase3_diag_17ac9cd/diag_manifest.json | 4563 | 48d010b6710bf52b08c90d62f02e181cbeb19949f8c2f9e5407bd4eecdc81024 |
| phase3_diag_17ac9cd/diag_mnq_rejects.csv | 7588 | e6fecfbe18378b9a270d63036b62c1f4bf468832eb7ad7c7c92029aeb0afee1c |
| phase3_diag_17ac9cd/diag_sizing_trades.csv | 32374 | d04e5af856bddde1829a4c194e2d2fee7363f8ebe18200cf5989090c5c509d37 |
| phase3_diag_17ac9cd/diag_timing.csv | 24440969 | be4a8c2801950c8d70292af47e05cc9b621976ee7b23e3ea0512150373c4e5c9 |
| phase3_diag_17ac9cd/gex_v3_input_files.csv | 443769 | dc9705512017bfc5b10f8426bf8e1606ff26d54d51fc0cbf8e638e6c311aaf93 |
| phase3_diag_17ac9cd/gex_v3_manifest.json | 252 | 54bb7d6e3259f61eedc7d80203d05e0154eb954f89302e9bfeabe3df9f2f5b34 |
| report_build/build_phase3_report_md.py | 18369 | 1d850120b5a8e71bf54e4992aab6a10bded5c150d2e19776d9b074e6a450e0a4 |

| file (under book1a/Phase3/checker_input/) | bytes | sha256 |
|---|---|---|
| Phase3_G4_checker_pack.zip | 144574 | d5235a1f55799448cc814d9f3c1392ddde5101c4b9cec7f6021bef63e4ead333 |
| attempts/C2_R4_attempts.csv | 34251 | 03e9ab5b967aa3368a047cf80c80348adfe2d41da340280c0729e8d870aec7f0 |
| attempts/C2_R4_risk_events.json | 2683 | b266842caea4cb6602ae2a3ed5fed77dc38a3310cb688a1f53ee43a631631051 |
| attempts/R1_attempts.csv | 33718 | 26e249ea5d8ca7662064f66a39af20965b9774aa42dd4633abaa146919adf8e9 |
| attempts/R2_attempts.csv | 4744 | ce867c88960d1a9f794d21f87a3682bd1f588933ff84ec26c815523cb7f42c12 |
| attempts/R2_retests.csv | 1852 | ace01ac6a2d61c8c9b19a708d5431c126764bfe5332c2ee49eca23ea3e1b82bd |
| attempts/R3_attempts.csv | 9744 | 88fbb44e1bd3e09077c8e2b8a35dc2a5342e67d4a1f059c08fa12f1eb354d98c |
| attempts/R3_retests.csv | 1905 | 236860e499a3633f6c21dee41e0f53dbc07c72235de606e9b736760c4368cf2f |
| attempts/R3_risk_events.json | 1370 | 3e8b10f2306d97f314a5c4956bb118910ecd99425396dd08594a69263a366761 |
| attempts/R4_attempts.csv | 35510 | c924f7c57edd3a0d2259144d7ef57fcf4fbbb46f62b5a7068af4090d6c3d80aa |
| attempts/R4_risk_events.json | 2258 | e5ecadecdbdc84c1a15ca60f3246de7ba7bc117557912546e81519c07e60cffe |
| g4_sample.csv | 1649 | ee0aa154ad87ae28a81b2cc2ac957930ad149837434f02efee0314a2db19ddfa |
| g4_sample.csv.manifest.json | 1209 | 3ea4f6e52d6e4e27c3f367440918671c48354ee0191e33111842b60e53013415 |
| ledgers/C2_R4_M0_ledger.csv | 18513 | 9fbdc4289a4a5fc4a1014cfa86441e74123df6dfe90dc315aee20eb806aa20a2 |
| ledgers/R1_A0_checker.csv | 7646 | 5fb911461c016f3e780225ad720b773211074be87c71971f52cd135859aca575 |
| ledgers/R1_A0_full.csv | 12781 | 3a6314dd39318cb26005aa4263e099afbe5d9d2e35aa57e525eb3ac1c49a2784 |
| ledgers/R2_C1_checker.csv | 3464 | 54b90ea495505ae006e139f1c5140289ea6af5b3053ed9ca12b612f6f4d29944 |
| ledgers/R2_C1_full.csv | 5848 | e6c92b2274a969017dc6e89690f693d92a772ce43ee1b0d666ff7e7d397a0769 |
| ledgers/R3_M0_ledger.csv | 5514 | 0b1ed31db1b4d8e72b69dc5b1c8f6943bbad839046a3346f04a7a7f7eafe1b38 |
| ledgers/R4_M0_ledger.csv | 18103 | 0e053e6f88e8ac31bc7c49d5906bb6692b0b089dd6d47601284d19c447fdc7d2 |
| manifests/phase3__run_manifest.json | 991 | f9d4c001a46e01498180695c6374fd85a2466bc244da42ba0f0419e5a85c6762 |
| manifests/phase3_r3__run_manifest.json | 1296 | d78584acc87a45b95c4a864f35b62108f12b6889e910d4ef8029aa128250060e |
| manifests/phase3_r4__run_manifest.json | 2144 | 221c88c88613243ece357e36904e3012197ccd79e87a0bf5a027e5a96e2a601a |
| manifests/phase3_r4_c2__run_manifest.json | 2147 | e1469702aa28d9a0d34c8a449f758dd3fe96830e3ab2588b679c64f647374b00 |
| pack_manifest.json | 7394 | b669d8d06318635f3d3dae45b05c35d7dcfded0155b9851a0dadbf8453e94bf8 |
| report/phase3_compare.json | 6856 | f318bbaae048f3467ed90f4b34931b72a6c3a026f480fd5ac9bf00f1f43f3492 |
| report/phase3_report_card.json | 76561 | bc8a02c40a3a813e4a6c105cfb49a3f9157dc1b235d07d470ea1d166a4311e99 |
| report/phase3_report_card_c2.json | 19039 | c36d706866e25d62b0a3dd7f2843f382e708bfdfba8140996a83308dd15aa42b |
| report/phase3_review.csv | 148911 | 1820a32a6cc142a2dee4d28962bd900d6147356a857ff1d21df506aaf7dc94bd |
| report/phase3_review_classes.json | 593514 | 26ada59137f9c421b8160008ec3ae1a3084fb0b0f80f51a33c857a8560469084 |
| report/phase3_review_manifest.json | 22518 | a8bdc336eb6c4f86c053e1c6e77f83165a98b249924da34cbb6116e4468d73ce |
| stress/lat1000/R1_A0_full.csv | 12847 | 1f366d3dc4f51799b4e7ed4c31eb3067b1149720c57fcae4d637e20eb8665d9f |
| stress/lat1000/R2_C1_full.csv | 5876 | 9726ffc9b16725061f47f1686c955759502b070d72f2092e5ffefe5f0273b35d |
| stress/lat1000/R3_M0_ledger.csv | 5544 | d4fbea6f28b81aea099ef91332597b0f051f8740c261dae8abb00e135a463ddb |
| stress/lat1000/R4_M0_ledger.csv | 18145 | 49f321477849af0fe403e2b340e86d25a0a14d49ef7ca6c61ac9fbbc30caf15a |
| stress/lat1000/stress_manifest.json | 1544 | 0eeebb4acaf77abf14752cf9dca090693cf2b9f351c4607675df2d4a96491143 |
| stress/slip2/R1_A0_full.csv | 12776 | 986bfbe053a29ee86ec63fe812e755ce584b50342059269d846498666de39a20 |
| stress/slip2/R2_C1_full.csv | 5846 | fe73e05fbdd8b03e2f341c32a10bfd15820da4aa87f8b6137959084304c59b39 |
| stress/slip2/R3_M0_ledger.csv | 5514 | cc5e9c27e4661338a70d4d010ac985f4777b38dd1119ac67db2871bcfc20c4ab |
| stress/slip2/R4_M0_ledger.csv | 18098 | 39221541b0f64a6aaba9966c3c1303ca48d2d53e3f1042b8faeafb6a17054047 |
| stress/slip2/stress_manifest.json | 1541 | dd982c66877f5767cf44bd6ee3069fee23ce94ff3006c4ae8c74fc1d7ec236a4 |
| stress/slip4/R1_A0_full.csv | 12776 | d6de8ae0037a5c0b637ecb88ae5b61200a154ff9dbd8710b28ca5485acc67fe6 |
| stress/slip4/R2_C1_full.csv | 5842 | 6aba6e6e84c01d8434b2c6257cccdda3059469861867e6b18b608a3004634e2d |
| stress/slip4/R3_M0_ledger.csv | 5510 | cf90d8a8d7d2da710046a1b152b2cbea99d6319316d8b0fce4edbe51db5b58e0 |
| stress/slip4/R4_M0_ledger.csv | 18097 | 1a1e10786a016359e94de315ff81573b4b13ea830c789c81569d8118317b5e01 |
| stress/slip4/stress_manifest.json | 1541 | 5929e528ca03328c11b1f65b1100ae83e9aa9576c0a850732911b78746a6ab11 |

## 10. Access and blinding

- **Book 1 and the checker.** No file of Book 1 or `K:\Book1A_checker` was opened, and no git command ran in
  `K:\Databento_BackTesting`. Inputs came only through `K:\Book1A_inputs`.
- **Before the report.** The Step B gate checks and the fix work showed only mechanics: run metadata, HEAD records,
  ledger sha256, the gex_v3 level flags and GEX input values, row counts, audit counts, G3 counts, the D2 count and
  the G4 counts. Results were first read after stage 2 had finished, to write this report.
- **No changes after results.** No threshold, rule, plan or execution code was changed after any result, and Phase 1
  outcomes were not used. The only code change in Step B (`17ac9cd`) was made and approved before any result was
  opened.
