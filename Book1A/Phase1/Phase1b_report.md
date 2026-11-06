# Book 1A Phase 1b report: diagnostics (phase1b-report-v1.0)

Written Nov 06, 2026. Code `142cbbe3ba030bacde983e292122269e571468ff`. Spec `book1a/specs/Phase1b_diagnostics_spec.md` (sha256 8ac07a864590d6a4f87e47dce802ecdf3ead521d3003f90e0a9fe335a06c393a, with addendum 5b).
Every diagnostic is logged only: none changes an R1-R4 entry, exit, stop, target, size, rule or plan. No P&L, R, win rate or outcome table anywhere in this report (D6).

R3 and R4 risk implementation: risk-c3-v2 / risk-c3-v2 (controlling for Phase 2 onward). Every diagnostic file starts with a line naming the risk version and the sha256 of the four ledgers it used.

## D1 Trading untouched

Phase 1 (Oct 22 - Nov 4, 2025) rerun with every diagnostic on, at the commit above: R1 / R2 (`run_r1_r2`, v3.5), R3 and R4 (`run_r3`, `run_r4`, risk-c3-v2), then `diag_phase1b` on those folders. Hashes were taken before and after the diagnostics ran and compared with the mechanics run (`runs\phase1`, `runs\phase1_r3_c3v2`, `runs\phase1_r4_c3v2`).

| strategy | controlling sha256 | final run, after diagnostics | match |
|---|---|---|---|
| R1 | `b4a2108fa2ab531ef84e1a2933d05fafb8e4519f6674ee8857f0cd79c344b21c` | `b4a2108fa2ab531ef84e1a2933d05fafb8e4519f6674ee8857f0cd79c344b21c` | MATCH |
| R2 | `6123f88e7a62242b559e89a385b7749e67d6d2d433108cb839524a37c606842e` | `6123f88e7a62242b559e89a385b7749e67d6d2d433108cb839524a37c606842e` | MATCH |
| R3 | `f413d15f4dad259d908390f6fcff659490f61cd5c9ce5a0f14a1bbeb486e71d1` | `f413d15f4dad259d908390f6fcff659490f61cd5c9ce5a0f14a1bbeb486e71d1` | MATCH |
| R4 | `b4510aabf2c750f6b3d0cb6f53de274989ed8acbc90d14c0dee9532a5ee5b409` | `b4510aabf2c750f6b3d0cb6f53de274989ed8acbc90d14c0dee9532a5ee5b409` | MATCH |

| file | mechanics run sha256 | final run before diagnostics | after diagnostics | result |
|---|---|---|---|---|
| A0:R1_A0_full.csv | `b4a2108fa2ab531e...` | `b4a2108fa2ab531e...` | `b4a2108fa2ab531e...` | MATCH (byte-identical) |
| A0:R2_C1_full.csv | `6123f88e7a62242b...` | `6123f88e7a62242b...` | `6123f88e7a62242b...` | MATCH (byte-identical) |
| A0:checker_input/R1_A0.csv | `4a7c1fe8224cd2e7...` | `4a7c1fe8224cd2e7...` | `4a7c1fe8224cd2e7...` | MATCH (byte-identical) |
| A0:checker_input/R2_C1.csv | `69b3f158d9037196...` | `69b3f158d9037196...` | `69b3f158d9037196...` | MATCH (byte-identical) |
| A0:R1_attempts.csv | `3106db5339fdbf73...` | `3106db5339fdbf73...` | `3106db5339fdbf73...` | MATCH (byte-identical) |
| A0:R2_attempts.csv | `8230d1f8caba57d8...` | `8230d1f8caba57d8...` | `8230d1f8caba57d8...` | MATCH (byte-identical) |
| A0:R2_retests.csv | `MISSING...` | `MISSING...` | `MISSING...` | not written in either run |
| A0:fills_model.csv | `971420ae5d37fa92...` | `971420ae5d37fa92...` | `971420ae5d37fa92...` | MATCH (byte-identical) |
| A0:strategy/JOFS_*.csv | `e9df8b9cc42164d7...` | `639a8a99cd91a0a5...` | `639a8a99cd91a0a5...` | content MATCH (see note) |
| R3:R3_M0_ledger.csv | `f413d15f4dad259d...` | `f413d15f4dad259d...` | `f413d15f4dad259d...` | MATCH (byte-identical) |
| R3:R3_attempts.csv | `79dd93ad699e8d67...` | `79dd93ad699e8d67...` | `79dd93ad699e8d67...` | MATCH (byte-identical) |
| R3:R3_retests.csv | `5abceb0348b3ffc3...` | `5abceb0348b3ffc3...` | `5abceb0348b3ffc3...` | MATCH (byte-identical) |
| R4:R4_M0_ledger.csv | `b4510aabf2c750f6...` | `b4510aabf2c750f6...` | `b4510aabf2c750f6...` | MATCH (byte-identical) |
| R4:R4_attempts.csv | `9d64d1e4d6ccb9d4...` | `9d64d1e4d6ccb9d4...` | `9d64d1e4d6ccb9d4...` | MATCH (byte-identical) |
| R4:R4_candidates.csv | `1d447234f207270f...` | `1d447234f207270f...` | `1d447234f207270f...` | MATCH (byte-identical) |
| R4:strategy/JOFS_*.csv | `2e98452bdd3e0de5...` | `6db023df0729c577...` | `6db023df0729c577...` | content MATCH (see note) |

- A0:strategy/JOFS_*.csv: the raw file differs only in `ProcessedTimeLocal` (the harness's wall-clock time) and in the run folder path written in the CONFIG row and the 10 PLAN_LOADED rows. With those two removed, the content sha256 is `5950617dbe5c2974c77d172d5ad931f3b7b8326bfa9c6a88cad6a7931f121c70` (mechanics) and `5950617dbe5c2974c77d172d5ad931f3b7b8326bfa9c6a88cad6a7931f121c70` (final run): equal. Every other column of every row is identical. Unchanged by the diagnostics (before = after).
- R4:strategy/JOFS_*.csv: the raw file differs only in `ProcessedTimeLocal` (the harness's wall-clock time) and in the run folder path written in the CONFIG row and the 10 PLAN_LOADED rows. With those two removed, the content sha256 is `5ced71f142a7cd1618748f1e15e84ed764f681b226b9ed5b0aa175c4a2e1dd98` (mechanics) and `5ced71f142a7cd1618748f1e15e84ed764f681b226b9ed5b0aa175c4a2e1dd98` (final run): equal. Every other column of every row is identical. Unchanged by the diagnostics (before = after).

**D1: trading untouched.** The four controlling ledger sha256 are unchanged; checker files, attempt and retest logs, fills_model and R4_candidates.csv are byte-identical; the S1.4 strategy logs are identical in content (run path and wall clock aside); no file changed while the diagnostics ran.

## D2 Point in time

Every timed field group is registered in `diag_timing.csv` with its decision time, available_at and the latest data timestamp it used. Groups checked: 49647 (AT_ENTRY 27250, PROVISIONAL 22338, POST_ENTRY 59). Violations: **0**. POST_ENTRY labels present in every POST_ENTRY column: yes.
AT_ENTRY / PROVISIONAL: latest data at or before available_at = the decision time (the signal bar close). GEX: available_at = D-1 23:00 ET; the option OI and settlement rows used were all received at or before that cutoff (table in the GEX section). POST_ENTRY fields (CVD_DIV after entry, exit cue (a), M-J1, M-J2, MNQ hypothetical exits) are labelled and never mixed with AT_ENTRY fields.

## D3 Unit tests

`Book1A\Phase1\Phase1b_unit_tests\unit_tests_2026-11-06.log`: tests run 276, failures 0, errors 0, result PASS.
Phase 1b tests (`book1a/tests/test_diag_phase1b.py`): the four CVD_DIV cases; the 60-minute exclusion; PROVISIONAL vs AT_ENTRY; both CVD resets; cue (a) firing, not firing, NOT_APPLICABLE after an M0 exit; M-J1 target choice RUN / TP2 / TP1; M-J2 with 1, 2 and 5 NQ (and two legs on a tape); the 10 NQ and MNQ formulas on the U3 examples (60 ticks at 3 NQ = $947.22 fits, 4 NQ = $1,262.96 does not); every GEX tag (hvl_side, cr_ps_width, pin_zone, pc_gamma_ratio, time of day); the V2 seed giving the same twins twice; L1_PLAN_SIDE (ALLOWED, NONE, MISMATCH, the admitting zone by the L1 distance); the V3 zero crossing. Guard tests for risk-c3-v2 in `test_risk_c3_v2.py`.

## D4 Coverage (counts only)

Each cell: carried / NOT_APPLICABLE / DATA_MISSING / NOT_RUN / NOT_BUILT. No outcome column.

### Candidates (S1.4 candidate rows; the A0 log serves R1-R3)

| session | log | rows | atentry_high_case_cvd17 | atentry_low_case_cvd17 | atentry_high_case_cvd0830 | atentry_low_case_cvd0830 | prov_high_case_cvd17 | prov_low_case_cvd17 | bs_status | log_cvd_slope_5 | grade_without_cvd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | A0 | 571 | 571/0/0/0/0 | 571/0/0/0/0 | 535/36/0/0/0 | 473/98/0/0/0 | 559/12/0/0/0 | 564/7/0/0/0 | 173/398/0/0/0 | 571/0/0/0/0 | 0/0/0/571/0 |
| 2025-10-22 | R4 | 583 | 583/0/0/0/0 | 583/0/0/0/0 | 542/41/0/0/0 | 481/102/0/0/0 | 571/12/0/0/0 | 576/7/0/0/0 | 169/414/0/0/0 | 583/0/0/0/0 | 0/0/0/583/0 |
| 2025-10-23 | A0 | 391 | 391/0/0/0/0 | 391/0/0/0/0 | 327/64/0/0/0 | 390/1/0/0/0 | 387/4/0/0/0 | 382/9/0/0/0 | 112/279/0/0/0 | 391/0/0/0/0 | 0/0/0/391/0 |
| 2025-10-23 | R4 | 411 | 411/0/0/0/0 | 411/0/0/0/0 | 345/66/0/0/0 | 410/1/0/0/0 | 407/4/0/0/0 | 402/9/0/0/0 | 117/294/0/0/0 | 411/0/0/0/0 | 0/0/0/411/0 |
| 2025-10-24 | A0 | 566 | 566/0/0/0/0 | 566/0/0/0/0 | 471/95/0/0/0 | 510/56/0/0/0 | 556/10/0/0/0 | 554/12/0/0/0 | 176/390/0/0/0 | 566/0/0/0/0 | 0/0/0/566/0 |
| 2025-10-24 | R4 | 566 | 566/0/0/0/0 | 566/0/0/0/0 | 471/95/0/0/0 | 510/56/0/0/0 | 556/10/0/0/0 | 554/12/0/0/0 | 174/392/0/0/0 | 566/0/0/0/0 | 0/0/0/566/0 |
| 2025-10-27 | A0 | 570 | 570/0/0/0/0 | 570/0/0/0/0 | 402/168/0/0/0 | 514/56/0/0/0 | 555/15/0/0/0 | 562/8/0/0/0 | 157/413/0/0/0 | 570/0/0/0/0 | 0/0/0/570/0 |
| 2025-10-27 | R4 | 572 | 572/0/0/0/0 | 572/0/0/0/0 | 400/172/0/0/0 | 513/59/0/0/0 | 557/15/0/0/0 | 564/8/0/0/0 | 153/419/0/0/0 | 572/0/0/0/0 | 0/0/0/572/0 |
| 2025-10-28 | A0 | 532 | 532/0/0/0/0 | 532/0/0/0/0 | 470/62/0/0/0 | 437/95/0/0/0 | 519/13/0/0/0 | 525/7/0/0/0 | 170/362/0/0/0 | 532/0/0/0/0 | 0/0/0/532/0 |
| 2025-10-28 | R4 | 533 | 533/0/0/0/0 | 533/0/0/0/0 | 471/62/0/0/0 | 435/98/0/0/0 | 520/13/0/0/0 | 526/7/0/0/0 | 170/363/0/0/0 | 533/0/0/0/0 | 0/0/0/533/0 |
| 2025-10-29 | A0 | 653 | 653/0/0/0/0 | 653/0/0/0/0 | 539/114/0/0/0 | 646/7/0/0/0 | 638/15/0/0/0 | 641/12/0/0/0 | 222/431/0/0/0 | 653/0/0/0/0 | 0/0/0/653/0 |
| 2025-10-29 | R4 | 642 | 642/0/0/0/0 | 642/0/0/0/0 | 533/109/0/0/0 | 630/12/0/0/0 | 627/15/0/0/0 | 632/10/0/0/0 | 229/413/0/0/0 | 642/0/0/0/0 | 0/0/0/642/0 |
| 2025-10-30 | A0 | 631 | 631/0/0/0/0 | 631/0/0/0/0 | 621/10/0/0/0 | 574/57/0/0/0 | 614/17/0/0/0 | 618/13/0/0/0 | 209/422/0/0/0 | 631/0/0/0/0 | 0/0/0/631/0 |
| 2025-10-30 | R4 | 637 | 637/0/0/0/0 | 637/0/0/0/0 | 627/10/0/0/0 | 584/53/0/0/0 | 620/17/0/0/0 | 626/11/0/0/0 | 193/444/0/0/0 | 637/0/0/0/0 | 0/0/0/637/0 |
| 2025-10-31 | A0 | 426 | 426/0/0/0/0 | 426/0/0/0/0 | 426/0/0/0/0 | 396/30/0/0/0 | 419/7/0/0/0 | 420/6/0/0/0 | 160/266/0/0/0 | 426/0/0/0/0 | 0/0/0/426/0 |
| 2025-10-31 | R4 | 418 | 418/0/0/0/0 | 418/0/0/0/0 | 418/0/0/0/0 | 390/28/0/0/0 | 412/6/0/0/0 | 412/6/0/0/0 | 157/261/0/0/0 | 418/0/0/0/0 | 0/0/0/418/0 |
| 2025-11-03 | A0 | 574 | 574/0/0/0/0 | 574/0/0/0/0 | 490/84/0/0/0 | 553/21/0/0/0 | 565/9/0/0/0 | 570/4/0/0/0 | 198/376/0/0/0 | 574/0/0/0/0 | 0/0/0/574/0 |
| 2025-11-03 | R4 | 621 | 621/0/0/0/0 | 621/0/0/0/0 | 536/85/0/0/0 | 600/21/0/0/0 | 612/9/0/0/0 | 615/6/0/0/0 | 205/416/0/0/0 | 621/0/0/0/0 | 0/0/0/621/0 |
| 2025-11-04 | A0 | 622 | 622/0/0/0/0 | 622/0/0/0/0 | 585/37/0/0/0 | 509/113/0/0/0 | 609/13/0/0/0 | 611/11/0/0/0 | 235/387/0/0/0 | 622/0/0/0/0 | 0/0/0/622/0 |
| 2025-11-04 | R4 | 632 | 632/0/0/0/0 | 632/0/0/0/0 | 588/44/0/0/0 | 519/113/0/0/0 | 619/13/0/0/0 | 620/12/0/0/0 | 232/400/0/0/0 | 632/0/0/0/0 | 0/0/0/632/0 |

### Trades: CVD

| session | strategy | rows | atentry_high_case_cvd17 | atentry_low_case_cvd17 | prov_high_case_cvd17 | prov_low_case_cvd17 | post_high_case_cvd17 | post_low_case_cvd17 | bs_status |
|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | R1 | 2 | 2/0/0/0/0 | 2/0/0/0/0 | 1/1/0/0/0 | 2/0/0/0/0 | 0/2/0/0/0 | 0/2/0/0/0 | 2/0/0/0/0 |
| 2025-10-29 | R4 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | R1 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | R2 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 |
| 2025-10-30 | R4 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 |
| 2025-10-31 | R1 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-31 | R4 | 2 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 0/2/0/0/0 | 0/2/0/0/0 | 2/0/0/0/0 |
| 2025-11-03 | R1 | 3 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 2/1/0/0/0 | 1/2/0/0/0 | 3/0/0/0/0 |
| 2025-11-03 | R2 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 |
| 2025-11-03 | R3 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 |
| 2025-11-03 | R4 | 3 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 1/2/0/0/0 | 1/2/0/0/0 | 2/1/0/0/0 |
| 2025-11-04 | R4 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 |

### Trades: exits, sizing, GEX tags

| session | strategy | rows | cue_a | mj1_status | mj2_status | nq10_fits_1000 | hvl_side | cr_ps_width | pin_zone | pc_gamma_ratio | gamma_regime | time_of_day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | R1 | 2 | 2/0/0/0/0 | 0/2/0/0/0 | 0/2/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 0/2/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 |
| 2025-10-29 | R4 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | R1 | 1 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | R2 | 1 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | R4 | 1 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-31 | R1 | 1 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-31 | R4 | 2 | 2/0/0/0/0 | 0/2/0/0/0 | 0/2/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 0/2/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 |
| 2025-11-03 | R1 | 3 | 3/0/0/0/0 | 0/3/0/0/0 | 0/3/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 0/3/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 |
| 2025-11-03 | R2 | 1 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-11-03 | R3 | 1 | 1/0/0/0/0 | 0/1/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-11-03 | R4 | 3 | 3/0/0/0/0 | 0/3/0/0/0 | 0/3/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 0/3/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 |
| 2025-11-04 | R4 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 0/1/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |

### MNQ feasibility (R3 / R4 RISK_REJECT rows)

| session | strategy | rows | mnq_max | hyp_status |
|---|---|---|---|---|
| 2025-10-30 | R3 | 1 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | R4 | 2 | 2/0/0/0/0 | 2/0/0/0/0 |

### L1_PLAN_SIDE (R4 candidates and trades from an intraday zone admitted by L1; spec 5b)

Counts of rows carrying the field only; the counts by value are reported at the end of Phase 2 (spec 5b).

| session | trade | rows | l1_side_inherited | plan_zone_label | distance_pts |
|---|---|---|---|---|---|
| 2025-10-22 | N | 102 | 37/65/0/0/0 | 102/0/0/0/0 | 102/0/0/0/0 |
| 2025-10-23 | N | 66 | 5/61/0/0/0 | 66/0/0/0/0 | 66/0/0/0/0 |
| 2025-10-24 | N | 104 | 10/94/0/0/0 | 104/0/0/0/0 | 104/0/0/0/0 |
| 2025-10-27 | N | 219 | 30/189/0/0/0 | 219/0/0/0/0 | 219/0/0/0/0 |
| 2025-10-28 | N | 127 | 66/61/0/0/0 | 127/0/0/0/0 | 127/0/0/0/0 |
| 2025-10-29 | N | 503 | 388/115/0/0/0 | 503/0/0/0/0 | 503/0/0/0/0 |
| 2025-10-30 | N | 295 | 212/83/0/0/0 | 295/0/0/0/0 | 295/0/0/0/0 |
| 2025-10-30 | Y | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-31 | N | 305 | 238/67/0/0/0 | 305/0/0/0/0 | 305/0/0/0/0 |
| 2025-10-31 | Y | 2 | 2/0/0/0/0 | 2/0/0/0/0 | 2/0/0/0/0 |
| 2025-11-03 | N | 292 | 191/101/0/0/0 | 292/0/0/0/0 | 292/0/0/0/0 |
| 2025-11-03 | Y | 3 | 3/0/0/0/0 | 3/0/0/0/0 | 3/0/0/0/0 |
| 2025-11-04 | N | 227 | 38/189/0/0/0 | 227/0/0/0/0 | 227/0/0/0/0 |

### GEX per session and per R4 zone

| session | rows | gex_valid | flip_v3_nt | regime_agree | pc_gamma_ratio | atm_iv | vol_tercile_POST_PHASE_GROUPING |
|---|---|---|---|---|---|---|---|
| 2025-10-22 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-23 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-24 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-27 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-28 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-29 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-30 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-10-31 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-11-03 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |
| 2025-11-04 | 1 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 | 1/0/0/0/0 |

| session | rows | v2_status | gex_random | gex_round |
|---|---|---|---|---|
| 2025-10-22 | 25 | 25/0/0/0/0 | 25/0/0/0/0 | 25/0/0/0/0 |
| 2025-10-23 | 17 | 17/0/0/0/0 | 17/0/0/0/0 | 17/0/0/0/0 |
| 2025-10-24 | 15 | 15/0/0/0/0 | 15/0/0/0/0 | 15/0/0/0/0 |
| 2025-10-27 | 23 | 23/0/0/0/0 | 23/0/0/0/0 | 23/0/0/0/0 |
| 2025-10-28 | 24 | 24/0/0/0/0 | 24/0/0/0/0 | 24/0/0/0/0 |
| 2025-10-29 | 26 | 26/0/0/0/0 | 26/0/0/0/0 | 26/0/0/0/0 |
| 2025-10-30 | 31 | 31/0/0/0/0 | 31/0/0/0/0 | 31/0/0/0/0 |
| 2025-10-31 | 21 | 21/0/0/0/0 | 21/0/0/0/0 | 21/0/0/0/0 |
| 2025-11-03 | 28 | 28/0/0/0/0 | 28/0/0/0/0 | 28/0/0/0/0 |
| 2025-11-04 | 20 | 20/0/0/0/0 | 20/0/0/0/0 | 20/0/0/0/0 |

V5 missing GEX days: 0 of 10 Phase 1 sessions have gex_valid = N (they stay in the baseline and drop out of every GEX group).

## GEX V3, volatility control, pc_gamma_ratio, pin_zone: build record

- Code, used through `K:\Book1A_inputs` only (main() never run): `gex_calc.py` sha256 7c8107b0eca57990e2ae9f753d9de2cbcc6eb72c7a05ab2d9e49c14182a9232b (cme_day, smile_iv); `mq_levels.py` sha256 d94b18f25d49e12bb2b9f8d3c023a1837ca877442ace76cc30fbf59e35f566e4 (strike_gex, compute_levels, _gamma); our loader `book1a/gex_v3.py` (sha256 086de0b6e52c5987d98fbf3de7627d1cafbd6cb34fa5d3e99083c1b856e0dcf4).
- Input files: CME NQ option definitions and statistics in `K:\Book1A_inputs\raw\block1\opt_<root>_*` (roots NQ, Q1A-Q5D, QN1-QNE); 520 files, each with its sha256 in `gex_v3_input_files.csv`; plus `gex_levels_block1.csv` (front contract, front settlement, nt_shift_pts).
- Report date D = the previous session (gex_levels_block1.csv). Open interest: the latest per option received at or before D 23:00 ET (ts_ref within 4 days). Settlements: stat type 3 with ts_ref on D, latest received at or before D 23:00 ET. Everything is available before the 08:10 CT map of the session.
- Expiry and strike selection: the front NQ futures contract's options (all expiries after D: quarterly, weeklies, end-of-month); IV from each option's own settlement, interpolated across strikes (smile_iv); GEX per strike as mq_levels. 0DTE set = options expiring on the session. ATM IV: the front contract's nearest expiry after the session (0DTE excluded), at log-moneyness 0.
- Check: the loader's chain reproduces the frozen gex_levels_block1.csv row (CR, PS, HVL, the 0DTE levels, net_gex, regime, options_used) on every Phase 1 session.

| session | report_date | repro_all_match | oi_max_ts_recv | settle_max_ts_recv | flip_v3_nt | hvl_nt | regime_agree | flip_v3_minus_hvl_pts | flip_v3_crossings | pc_gamma_ratio | pin_strike_0dte_nt | atm_iv | atm_iv_expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | 2025-10-21 | Y | 2025-10-22 01:55:37 UTC | 2025-10-21 23:01:17 UTC | 25532.84 | 25230.0 | N | 302.84 | 1 | 0.7086 | 25200.0 | 0.1543 | 2025-10-23 |
| 2025-10-23 | 2025-10-22 | Y | 2025-10-23 02:24:32 UTC | 2025-10-22 22:39:03 UTC | 25962.25 | 24990.0 | N | 972.25 | 1 | 0.8905 | 24900.0 | 0.2069 | 2025-10-24 |
| 2025-10-24 | 2025-10-23 | Y | 2025-10-24 02:45:53 UTC | 2025-10-23 22:44:38 UTC | 25448.87 | 24990.0 | N | 458.87 | 1 | 0.6564 | 24900.0 | 0.139 | 2025-10-27 |
| 2025-10-27 | 2025-10-24 | Y | 2025-10-24 14:44:48 UTC | 2025-10-24 21:40:05 UTC | 25495.12 | 24990.0 | Y | 505.12 | 1 | 0.5178 | 25325.0 | 0.1219 | 2025-10-28 |
| 2025-10-28 | 2025-10-27 | Y | 2025-10-27 13:44:36 UTC | 2025-10-28 01:47:15 UTC | 25594.12 | 24990.0 | Y | 604.12 | 1 | 0.3392 | 25400.0 | 0.1652 | 2025-10-29 |
| 2025-10-29 | 2025-10-28 | Y | 2025-10-29 02:10:12 UTC | 2025-10-28 22:50:07 UTC | 25939.15 | 24990.0 | Y | 949.15 | 1 | 0.4673 | 26300.0 | 0.2431 | 2025-10-30 |
| 2025-10-30 | 2025-10-29 | Y | 2025-10-30 02:40:30 UTC | 2025-10-29 22:47:37 UTC | 26090.6 | 25390.0 | Y | 700.6 | 3 | 0.4762 | 26000.0 | 0.2878 | 2025-10-31 |
| 2025-10-31 | 2025-10-30 | Y | 2025-10-30 14:37:10 UTC | 2025-10-30 22:58:14 UTC | 25898.51 | 25275.0 | N | 623.51 | 1 | 0.5625 | 23750.0 | 0.167 | 2025-11-03 |
| 2025-11-03 | 2025-10-31 | Y | 2025-10-31 15:06:27 UTC | 2025-10-31 21:40:09 UTC | 25999.53 | 25490.0 | Y | 509.53 | 1 | 0.5779 | 26000.0 | 0.1353 | 2025-11-04 |
| 2025-11-04 | 2025-11-03 | Y | 2025-11-03 16:12:27 UTC | 2025-11-04 01:02:27 UTC | 26097.1 | 24975.0 | Y | 1122.1 | 1 | 0.5601 | 25000.0 | 0.1676 | 2025-11-05 |

Volatility terciles (`vol_tercile_POST_PHASE_GROUPING` in diag_gex_sessions.csv) are a post-phase reporting grouping, computed after the phase from this phase's sessions only; never an AT_ENTRY field.

## D5 CVD definition check (Oct 24, 27, 28, 29, 2025)

Swing pairs: consecutive confirmed swings of the same type whose second swing closes in RTH (08:30-15:00 CT). Times CT (bar end). CVD at the swing bar's close, 17:00 CT and 08:30 CT resets. Timing: earliest knowable = the second swing's confirmation. The algorithm is not tuned to these days; disagreements are documented.

### CVD_DIV events (pairs within 60 minutes with a divergence on either reset): 16; non-diverging pairs: 51

| session | kind | s1_time | s1_price | s1_cvd17 | s1_cvd0830 | s2_time | s2_price | s2_cvd17 | s2_cvd0830 | gap_min | at_session_extreme | case_cvd17 | case_cvd0830 | earliest_knowable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-24 | HIGH | 2025-10-24 08:46:00 | 25535.0 | 3529.0 | 1987.0 | 2025-10-24 09:07:00 | 25548.75 | 3253.0 | 1711.0 | 21.0 | Y | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-24 09:22:00 |
| 2025-10-24 | HIGH | 2025-10-24 11:21:00 | 25563.0 | 4834.0 | 3292.0 | 2025-10-24 11:52:00 | 25561.75 | 5221.0 | 3679.0 | 31.0 | N | HIGH_ABSORPTION | HIGH_ABSORPTION | 2025-10-24 12:07:00 |
| 2025-10-24 | LOW | 2025-10-24 08:51:00 | 25464.0 | 2768.0 | 1226.0 | 2025-10-24 09:32:00 | 25469.0 | 1941.0 | 399.0 | 41.0 | N | LOW_ABSORPTION | LOW_ABSORPTION | 2025-10-24 09:47:00 |
| 2025-10-24 | LOW | 2025-10-24 12:16:00 | 25538.75 | 4940.0 | 3398.0 | 2025-10-24 13:04:00 | 25534.25 | 5474.0 | 3932.0 | 48.0 | N | LOW_EXHAUSTION | LOW_EXHAUSTION | 2025-10-24 13:19:00 |
| 2025-10-27 | HIGH | 2025-10-27 08:12:00 | 25842.5 | 4268.0 | nan | 2025-10-27 08:32:00 | 25859.5 | 4118.0 | 193.0 | 20.0 | Y | HIGH_EXHAUSTION | NOT_APPLICABLE | 2025-10-27 08:47:00 |
| 2025-10-27 | HIGH | 2025-10-27 09:05:00 | 25875.75 | 4900.0 | 975.0 | 2025-10-27 09:47:00 | 25892.0 | 4445.0 | 520.0 | 42.0 | Y | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-27 10:02:00 |
| 2025-10-27 | HIGH | 2025-10-27 10:42:00 | 25910.0 | 6246.0 | 2321.0 | 2025-10-27 11:08:00 | 25912.0 | 5957.0 | 2032.0 | 26.0 | Y | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-27 11:23:00 |
| 2025-10-27 | HIGH | 2025-10-27 11:56:00 | 25917.25 | 5826.0 | 1901.0 | 2025-10-27 12:49:00 | 25929.0 | 5643.0 | 1718.0 | 53.0 | Y | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-27 13:04:00 |
| 2025-10-28 | HIGH | 2025-10-28 08:13:00 | 26063.5 | 1872.0 | nan | 2025-10-28 08:34:00 | 26094.75 | 1350.0 | -276.0 | 21.0 | Y | HIGH_EXHAUSTION | NOT_APPLICABLE | 2025-10-28 08:49:00 |
| 2025-10-28 | HIGH | 2025-10-28 11:50:00 | 26133.0 | 2536.0 | 910.0 | 2025-10-28 12:19:00 | 26140.25 | 2297.0 | 671.0 | 29.0 | N | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-28 12:34:00 |
| 2025-10-28 | LOW | 2025-10-28 09:46:00 | 26008.75 | -812.0 | -2438.0 | 2025-10-28 10:36:00 | 26006.0 | -291.0 | -1917.0 | 50.0 | N | LOW_EXHAUSTION | LOW_EXHAUSTION | 2025-10-28 10:51:00 |
| 2025-10-29 | HIGH | 2025-10-29 10:54:00 | 26249.5 | 1543.0 | -1491.0 | 2025-10-29 11:46:00 | 26266.5 | 529.0 | -2505.0 | 52.0 | N | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-29 12:01:00 |
| 2025-10-29 | HIGH | 2025-10-29 11:46:00 | 26266.5 | 529.0 | -2505.0 | 2025-10-29 12:17:00 | 26268.25 | 398.0 | -2636.0 | 31.0 | N | HIGH_EXHAUSTION | HIGH_EXHAUSTION | 2025-10-29 12:32:00 |
| 2025-10-29 | HIGH | 2025-10-29 13:01:00 | 26290.0 | 613.0 | -2421.0 | 2025-10-29 13:35:00 | 26283.5 | 1307.0 | -1727.0 | 34.0 | N | HIGH_ABSORPTION | HIGH_ABSORPTION | 2025-10-29 13:50:00 |
| 2025-10-29 | HIGH | 2025-10-29 13:35:00 | 26283.5 | 1307.0 | -1727.0 | 2025-10-29 13:56:00 | 26228.0 | 1562.0 | -1472.0 | 21.0 | N | HIGH_ABSORPTION | HIGH_ABSORPTION | 2025-10-29 14:11:00 |
| 2025-10-29 | LOW | 2025-10-29 12:28:00 | 26219.0 | -184.0 | -3218.0 | 2025-10-29 13:06:00 | 26204.75 | 453.0 | -2581.0 | 38.0 | N | LOW_EXHAUSTION | LOW_EXHAUSTION | 2025-10-29 13:21:00 |

### Pairs excluded by the 60-minute window: 6

| session | kind | s1_time | s1_price | s1_cvd17 | s1_cvd0830 | s2_time | s2_price | s2_cvd17 | s2_cvd0830 | gap_min | at_session_extreme | case_cvd17 | case_cvd0830 | earliest_knowable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-24 | HIGH | 2025-10-24 07:32:00 | 25523.25 | 3022.0 | nan | 2025-10-24 08:46:00 | 25535.0 | 3529.0 | 1987.0 | 74.0 | Y | NONE | NOT_APPLICABLE | 2025-10-24 09:01:00 |
| 2025-10-27 | LOW | 2025-10-27 08:36:00 | 25796.5 | 3663.0 | -262.0 | 2025-10-27 10:00:00 | 25851.25 | 4538.0 | 613.0 | 84.0 | N | NONE | NONE | 2025-10-27 10:15:00 |
| 2025-10-28 | HIGH | 2025-10-28 08:57:00 | 26085.5 | 140.0 | -1486.0 | 2025-10-28 10:09:00 | 26056.75 | 620.0 | -1006.0 | 72.0 | N | HIGH_ABSORPTION | HIGH_ABSORPTION | 2025-10-28 10:24:00 |
| 2025-10-28 | HIGH | 2025-10-28 12:19:00 | 26140.25 | 2297.0 | 671.0 | 2025-10-28 13:33:00 | 26190.75 | 3642.0 | 2016.0 | 74.0 | Y | NONE | NONE | 2025-10-28 13:48:00 |
| 2025-10-28 | HIGH | 2025-10-28 13:33:00 | 26190.75 | 3642.0 | 2016.0 | 2025-10-28 14:35:00 | 26231.5 | 4389.0 | 2763.0 | 62.0 | Y | NONE | NONE | 2025-10-28 14:50:00 |
| 2025-10-29 | LOW | 2025-10-29 11:11:00 | 26203.25 | -488.0 | -3522.0 | 2025-10-29 12:28:00 | 26219.0 | -184.0 | -3218.0 | 77.0 | N | NONE | NONE | 2025-10-29 12:43:00 |

### Comparison with Jeron's video (for Kyron)

Video: "I made $50,000 this week, here's how", JeronTrades, Oct 29, 2025. Named times are checked both as ET (minus 1 h) and as CT, with +-15 minutes around each named time (ours).

| day | jeron | expected | flagged | detail |
|---|---|---|---|---|
| 2025-10-29 | NY AM high | HIGH_ABSORPTION | N | ET reading: swings 08:34 / 09:02, gap 28.0 min, 17:00 reset NONE, 08:30 reset NONE (CVD not diverging); ET reading: swings 09:02 / 09:36, gap 34.0 min, 17:00 reset NONE, 08:30 reset NONE (CVD not diverging); CT reading: swings 09:36 / 10:25, gap 49.0 min, 17:00 reset NONE, 08:30 reset NONE (CVD not diverging) |
| 2025-10-28 | Low of day | LOW_EXHAUSTION | Y | RTH extreme swing 10:36 at 26006.00; day extreme: swings 09:46 / 10:36, gap 50.0 min, 17:00 reset LOW_EXHAUSTION, 08:30 reset LOW_EXHAUSTION |
| 2025-10-27 | 08:30 and 09:30 CT lows (ET reading) / 09:30 and 10:30 CT (CT reading) | LOW_ABSORPTION | N | ET reading: no swing pair matching both named times; strict swings found near the named times: 08:36; nearest pair 08:36 / 10:00, gap 84.0 min (beyond 60 minutes), cases NONE / NONE; CT reading: no swing pair matching both named times; strict swings found near the named times: 10:00; nearest pair 10:00 / 10:56, gap 56.0 min, cases NONE / NONE |
| 2025-10-24 | High of day | HIGH_EXHAUSTION | N | RTH extreme swing 12:48 at 25570.75; day extreme: swings 12:11 / 12:48, gap 37.0 min, 17:00 reset NONE, 08:30 reset NONE (CVD not diverging) |

## Not run

| item | status | reason |
|---|---|---|
| L2 E1, E2, E4 | NOT_RUN (U11) | not run until the L2F audit and the fixed-price build are done; E4's hold time N is not registered |
| M-J3, M-J4 | NOT_RUN (U5) | deferred until objective triggers are specified |
| Grade without CVD | NOT_RUN (harness) | the S1.4 grade is computed in the harness C# code; recomputing it needs a harness change |

Built since the last report (inputs now reachable): GEX V3, volatility control, pc_gamma_ratio, pin_zone.

## Open choices (definitions the spec leaves open, fixed in code; for Kyron)

1. CVD at a swing = the CVD at the swing bar's close (the 1-minute bar is the swing's own timestamp).
2. Session for the primary CVD, swings and the session extreme = from 17:00 CT the previous calendar day; the second series is reset at 08:30 CT (ticks after 08:30:00) and is NOT_APPLICABLE for a swing bar closing before 08:30.
3. Bars: 1-minute, stamped at their end, ticks in (T - 1 min, T] (jeron_engine.arms.MinuteBars convention); aggressor B = +volume, S / A = -volume (the same convention).
4. AT_ENTRY uses swings whose confirmation bar closed at or before the decision bar close (the signal bar's own information set; the order goes 250 ms later).
5. CVD_DIV pair = the two most recent confirmed swings of the type; the location rule is tested on the second swing; a pair more than 60 minutes apart is EXCLUDED_60MIN (counted, case still logged as raw fields).
6. POST_ENTRY CVD_DIV (trades only): the first same-type pair whose second swing is confirmed after the decision and at or before the M0 exit.
7. PROVISIONAL (accepted by Kyron, Nov 6): the most recent swing confirmed by the decision vs the highest high (lowest low) of the bars after that swing's confirmation bar. Window: from the bar after the confirmation bar through the signal bar. Cutoff: bar end <= the decision time (the signal bar closes at the decision; no tick after it is used). The pair window (60 minutes) and the location rule as for AT_ENTRY.
8. BREAKOUT_SPEED: volume per second over [t - 60 s, t); percentile = share of the earlier session bar closes (from 17:00 CT) whose own 60 s value is <= the decision's, x 100; 3-bar CVD change = CVD(t) - CVD(t - 3 min), ticks strictly before each time.
9. Exit cue (a): the first 3 bars ending after the entry fill; the first qualifying bar triggers; NOT_APPLICABLE when the M0 exit time is at or before the trigger bar's close.
10. M-J1 / M-J2 target price = the near edge of the ladder target zone (long: its low; short: its high). Ladders exist only in Book 1A plans, so trades on intraday zones and all R1-R3 trades (A0 plans) are NOT_APPLICABLE (no ladder). A ladder target not beyond the fill is NOT_APPLICABLE (target behind entry).
11. Sizing stop ticks = the risk-c3-v2 reference (best ask long / best bid short at the decision) to the stop.
12. MNQ diagnostic covers R3 / R4 attempts rejected with RISK_REJECT:PER_TRADE_BUDGET or RISK_REJECT:DAILY_BUDGET.
13. V2 random twin: rng = numpy default_rng(20251205 + yyyymmdd as an integer); one side draw (0 = below, 1 = above ref) per level in the order CR, PS, HVL, CR_0DTE, PS_0DTE, HVL_0DTE. ref_price = the last trade at or before 08:10:00 CT. The P1.1 gamma-rank levels (GAMMA*) are not among the six and stay as they are in every twin set.
14. hvl_side price = the last trade at or before the decision; AT = within 1 tick.
15. L1_PLAN_SIDE: the admitting plan zone = the DECISION zone of the R4 run's staged plan with the smallest distance by the arms.l1 rule (first in file order on a tie); candidates before the plan as-of (08:25 CT) are NOT_APPLICABLE; a plan side other than ANY / RESPONSE / INITIATION / NONE is DATA_MISSING.
16. pin_zone price = the last trade at or before the decision (the same as hvl_side); pin strike in the chart contract (+ nt_shift_pts).
17. Volatility terciles: rank of atm_iv among the phase's sessions, tercile = ceil(3 x rank / n); a post-phase reporting grouping only (POST_PHASE_GROUPING), never an AT_ENTRY field.
18. V3 flip: cumulative net GEX from the lowest strike, linear between the two strikes around the sign change; the crossing nearest the front settlement when there is more than one.
19. regime_agree: Y when the front settlement is on the same side of flip_v3 as of HVL.
20. pin strike: the 0DTE strike with the largest open interest (calls + puts); on a tie the strike nearest the settlement.
21. ATM IV expiry: the front contract's nearest expiry after the session (0DTE excluded).
22. D5 comparison: +-15 minutes around a named time; 'day extreme' = the RTH extreme among the strict swings.
23. Accepted by Kyron, Nov 6: quote rule bid > 0, ask > 0, bid < ask (no staleness threshold); PROVISIONAL window and cutoff as in item 7; grade without CVD NOT_RUN (harness).

## D6 No outcomes

This report contains no P&L, R, win rate or outcome-by-tag table. Counterfactual fields (cue (a), M-J1, M-J2, MNQ hypothetical exits) are stored per trade in the diagnostic files only and are not aggregated or summarised.

## Diagnostic files (runs\phase1b\diagnostics, git-ignored)

| file | sha256 |
|---|---|
| d2_lookahead_audit.json | `91c0914b8359952f98873e4e3e7a102504c3fd4928663b8a43d25f9c0b30905c` |
| d5_cvd_pairs.csv | `4eb3cd29130f40efca222ce0b17c8a076cf7d9f5292c7e0f9247e28e6f1a03b9` |
| d5_cvd_pairs_excluded_60min.csv | `0845e5dd42f73eef498f5b5f192fae033b5e27f8616a5461459b591046fcc93c` |
| d5_cvd_swings.csv | `5c2529ae00f119accfcb42668ed601d23eb59ad5d04e9a629e1e91360607ffbd` |
| diag_cvd_candidates.csv | `6fbd9b8d73453dd1b90facadb9592c381ded101147ff4668655cca78b3377590` |
| diag_cvd_trades.csv | `cd3dd9bd34102ccbaa0fe05dc2d3ff04b5eb34d9d7524536ab96c0bcbbec25c2` |
| diag_exit_trades.csv | `a071debdd59e6934d640d967382a9c377cda37d9f09fd878b4e06c564c1f4bbd` |
| diag_gex_sessions.csv | `05c2b118c7778bc6d716ad356e8fbf7281ec1f2eef4f5e77fbab547e633fbc1b` |
| diag_gex_trades.csv | `98fc4a1f5fe0004d2f5a038731fbd739d11dd5c27b9cfe8fe9393850a6e9be29` |
| diag_gex_v3_sessions.csv | `33cbf85f9e86b947b93b2e871849c76417a9a1427ec1d421637bf81c32b236e9` |
| diag_gex_zones.csv | `8e807f57b77ec1fcbf8e0850c87ca671d74f6a4772fac3dfa0971d08a64d5736` |
| diag_l1_plan_side.csv | `d590f9413bf1bcb38e93b6babed448d49d754219d669c18705a8a03bbb2beebc` |
| diag_manifest.json | `58f04ce8bfda814a332d3b79bfca1d7c7e727fd30a99a8044b101e02fa269a5f` |
| diag_mnq_rejects.csv | `ec80d3b0b7ed333a7b88c45c8202c5d6fbbe0de43328c20ba4bbeae84b29a0af` |
| diag_sizing_trades.csv | `58158abd19ddc10605c1abb98c4d1eef478b6827012c84c4817c0ba6d4669829` |
| diag_timing.csv | `e00afde0093ba07be32b56f59fb31622d0eceb91d46cd883e5fbb7723c358fa7` |
| gex_v3_input_files.csv | `ad7c989604c1431b21108ec15ff0ecba75ddc59e4d3d913575559dbade5bee63` |
| gex_v3_manifest.json | `35631037b31d104f90734caf3112251c6df747241975e543151b2cbe2a29325b` |

## Next step

Phase 1b is complete. Phase 2 starts only on Kyron's go.

