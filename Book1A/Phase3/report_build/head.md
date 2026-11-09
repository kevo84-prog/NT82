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

