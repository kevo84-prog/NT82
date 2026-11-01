# Book 1A – Phase 0 report

Runner: Claude Code cloud session (kevo84-prog/NT82), Nov 1, 2026. Branch `book1a-phase0` (also mirrored on the
session branch `ccr-634ccaf9-wh1psf`). Package tag `book1a-phase0-v0.1`; per-module tags in the table below.
Controlling doc: "Book 1A – Replay plan"; task list: "Book 1A – Phase 0 build checklist" (text copies in
`Book1A/specs/`). No P&L was opened. One blinding exposure is logged in section 5.

## 0. Read first: what passed here and what still has to run on the PC

The decisive constraint: the Block 1 MBO data (157 daily files, 44 GB), the roll files, the 1-minute bar files and
the Mono-compiled C# harness exist only on the PC (`K:\Databento_BackTesting`). No Remote Control folder was
connected to this session, the NT82 repository was empty, and Drive holds no Block 1 raw data (confirmed by search).
The full Book 1 engine, harness, NinjaTrader source, phase run scripts, the gate 6 data-integrity table and the
static inputs were found on Drive and copied byte-exact into `book1_ref/` (41 files, sha256 in `book1_ref/MANIFEST.md`).

So Phase 0 is in two states:

- **Built and passing here:** every Book 1A module the checklist names, with unit tests against the exact numbers
  in the checklist and on Book 1's own unchanged fill code (123 tests, 0 failures; log in `unit_tests/`); P1.2 passes
  on the real `gex_levels_block1.csv`.
- **Built, scripted, not executed:** every pass test that needs real sessions (P0.2 checksums, P0.3 two-session
  replay, P0.4 R1/R2 ledgers, P0.6-P0.9 hand checks on real days, P0.11-P0.13 on Phase 1 days). Each is marked
  `BUILT / NOT RUN`; `RUNBOOK_PC.md` gives the command for each.

The freeze tag `book1a-phase0-freeze` is **not applied**: the checklist sets it only when every P0 item passes, and
the real-day tests have not run. Nothing in Book 1 was edited, moved or overwritten.

## 1. One line per checklist item

| # | Item | Status | Version tag | Date | Note |
|---|---|---|---|---|---|
| P0.1 | Blind run setup | PASS (one exposure logged) | book1a-phase0-v0.1 | Nov 1 | `P0.1_blind_run_setup.md`: layout, allowed / forbidden files, access events. Book 1 reference copy made by a separate download agent under a written blinding rule (no result folders opened). |
| P0.2 | Data unchanged since Book 1 | BUILT / NOT RUN | manifest-v1.0 | Nov 1 | Gate 6 table obtained (`book1_ref/backtest/phase0_parity/phase0_data_integrity_2025-10-21_2026-10-02.csv`: 161 files, 155 used, 0 decode errors, roll days from the roll files). It has sizes to 0.1 MB, no checksums: the PC run compares names and sizes and writes our sha256 list as the Book 1A reference. Static inputs (`gex_levels_block1.csv`, econ calendar, roll estimate) are in `book1_ref/data/` with sha256. |
| P0.3 | Deterministic replay | BUILT / NOT RUN | replay-diff-v1.0 | Nov 1 | `run_r1_r2.py --sessions 2025-11-05 2025-12-15` twice, then `replay_diff` (row-for-row, bit-identical floats); the only ignored columns are run_id / generated timestamps. |
| P0.4 | R1 / R2 reproduction (E5) | BUILT / NOT RUN; ledgers not yet produced | run-r1-r2-v1.0, ledger-v1.0 | Nov 1 | Section 3. The C1 replay call equals Book 1's `final_combination.py` / `run_holdout.py` (FZ1 ∪ L1 ∪ T8 veto, RH1 15 bars / 2 ticks, M0). Ambiguity A1 (fill model) needs Kyron's confirmation before the run. |
| P0.5 | Execution model v3.4 | PASS | fills.py (Book 1, unchanged, sha256 1b93cbde…) + test-fills-v34 | Nov 1 | 13 long / short cases on Book 1's `fills.simulate`: entry 250 ms at ask / bid, 1,000 ms stress, target 1 tick through (touch = no fill), stop 1 tick adverse (2 and 4 stress), same-timestamp tie = stop, 14:55 CT flatten at bid / ask, commission $2.87 per side in net R, v3.5 gap fill differs only on gaps. |
| P0.6 | 08:10 VWAP | PASS on synthetic hand calc / real-day table NOT RUN | vwap-v1.0 | Nov 1 | 9 tests (windows, Sunday 17:00 CT, DST change Nov 2, strict 08:10:00 cut, roll-day restart, order independence). PC: `hand_checks/vwap_hand_check.py` on Oct 22, Nov 5, Dec 15 and Mar 16, independent pandas calculation beside the module. |
| P0.7 | Map v2.4 Book 1A outputs | BUILT, 23 synthetic tests PASS / 3-day hand check NOT RUN | map-v2.4-book1a-v1.0, bars-v1.0, plan-v2.4-book1a-v1.0 | Nov 1 | PO-1 (15-bar swings, arrival delta 150 / IMB / LARGE, 0.25 ADR in 10 bars, 10-40 pt bands, 5-pt merge, 3-close flip, tags, 2-per-side selection), PO-6 (70% areas, 40-pt cap), PO-7 (top-20% delta bands), PO-9 (60 min / 80% / 20%, FAILED_RECLAIM), PO-11 (DD_EDGE), PO-13 (08:10 vs 08:29). Every zone carries available_at = 08:10 CT. PC: `hand_checks/plan_hand_check.py` writes the per-day tables with an empty "hand" column. |
| P0.8 | Source families (C1, C2) | PASS (hand-built list) | families-v1.0 | Nov 1 | Six families, each counts once; GEX counts inside or within 10 points (5 / 20 / 35 configurable); VWAP within 5; DECISION needs 2+. Jeron's Nov 18 zone example reproduces families=5. |
| P0.9 | Context and side fields | PASS (unit) / 3-day sample plans NOT RUN | plan-fields-v1.0 | Nov 1 | market_context and draw_status separate (C6), draw=, balance=, balance_poc=, value_follows, on_inventory (far / thin null), edge_control, htf_structure, gex_regime, first_touch, side_conflict; most restrictive side wins (NONE > INITIATION > RESPONSE > ANY). Plan builder writes an S1.4-readable plan (Book 1 keys unchanged, no lava line, check B / F logged only). |
| P0.10 | Risk check and sizing (C3, U3) | PASS | risk-v1.0 | Nov 1 | 15 tests, exact cents: 196 / 96 / 63 / 36 / 16 ticks; $947.22 accepted at 3 NQ, $1,262.96 rejected at 4; remaining daily budget; RISK_REJECT; RISK_BREACH_FILL; 3-trade cap and 2-loss halt and the dollar limit, whichever first. |
| P0.11 | R4 entries | BUILT / NOT RUN on real days | candidate-log-v1.0 | Nov 1 | For every CANDIDATE / SHADOW row: S1.4 gate results, RH1 state (frozen v2.5 path), T8 and L1 (Book 1 `arms.py` unchanged), FZ1 logged never applied, C3 risk decision, single-print gate note (U2), every Phase 5 tag present ("null" when not measurable). Synthetic log test passes. |
| P0.12 | M0 exits and R reporting | PASS (unit) / ledger sample NOT RUN | ledger-v1.0, replay-risk-v1.0 | Nov 1 | Theoretical R and realized net R per trade, N recorded, checker CSV format; R3 / R4 replay wrapper around Book 1's replay blocks with sizing and the dollar daily limit (2 tests). |
| P0.13 | Timestamp and lookahead audit | PASS (unit) / real-day audit NOT RUN | lookahead-v1.0, audit-run-v1.0 | Nov 1 | Registry + strict before-decision assertion (equality = violation); rules for swings (+15 bars), VWAP and map (08:10 CT), GEX (D-1 23:00 ET), L2 (completed second). PC: `audit_run.py` over the ledger and plan sidecars. |
| P0.14 | Freeze | NOT DONE | - | - | Tag only when every P0 row passes on the PC. |
| P1.1 | Gamma ranks (U6) | PARTLY BUILT | gamma-ranks-v1.0 | Nov 1 | Ranking by size of net GEX built and hand-tested. The per-strike net GEX needs `mq_levels.py` / `gex_calc.py`, which are on the PC only (not on Drive). Path if not built before the replay: ranks left out of the GEX family (U6). |
| P1.2 | Calculated GEX levels and available_at | PASS (real table) | gex-check-v1.0 | Nov 1 | `P1.2_gex_levels.md`: 124 / 124 sessions ok, 68 positive, 56 negative, 0DTE blanks only on Dec 17-18 and Mar 18-19 (expected after the roll), available_at = D-1 23:00 ET before every 08:10 CT map. |
| P2.1-P2.9 | Diagnostics | NOT STARTED (by design) | - | - | `P1_P2_status.md` lists each with its replay path. |

## 2. Deliverables in this folder

| File | What |
|---|---|
| `Phase0_report.md` | this report (identical copy `Phase0_report_for_Drive.md` for upload) |
| `P0.1_blind_run_setup.md` | folder layout, access rules, access events |
| `ambiguities.md` | every ambiguity, runner default and not-set value (section 6 summarises) |
| `unit_tests/unit_tests_2026-11-01.log` | P0.5, P0.8, P0.10 and all other unit-test logs, verbose, with module tags and commit |
| `P1.2_gex_levels.md` | the P1.2 coverage table on the real GEX file |
| `P1_P2_status.md` | P1 / P2 readiness and replay paths |
| `RUNBOOK_PC.md` | the exact command for every NOT RUN item |
| `checker_input/` | empty until P0.4 runs on the PC (R1_A0_<phase>.csv, R2_C1_<phase>.csv) |
| `hand_checks/`, `lookahead/`, `replay_diff/` | empty until the PC runs |
| `../specs/` | text exports of the ten Book 1A docs and the two Book 1 design docs, dated |
| `../../book1a/` | the Book 1A package (modules, tests, hand-check and run scripts) |
| `../../book1_ref/` | byte-exact Book 1 reference copy with MANIFEST.md (Drive ids, modifiedTime, sha256) |

## 3. P0.4 hand-off to the checker (not yet produced)

What `run_r1_r2.py` does per phase, with Book 1 code unchanged: (1) `daily_loop.run` (map v2.3 at 08:10 → rules-only
plan → S1.4 in the harness → `fills_model.csv`), config in the Book 1 phase pattern (warm-up two UTC days before the
first session, 16:15 end, contract labels, ES settings; `map_first_utc` from `phase2_config.json` on the PC);
(2) R1 = `arm_replay.replay(no veto, M0)` plus the `check_a0` gate against `fills_model.csv`; (3) R2 = the same replay
with the FZ1 ∪ L1 ∪ T8 veto and the RH1 retest (15 bars, 2-tick touch and fail, stop at the retest extreme + 2 ticks),
exactly the call in Book 1's `final_combination.py` and `run_holdout.py`; (4) ledgers in the checker columns (date, entry
time, side, qty, entry price, stop, target, exit time, exit price, exit reason, risk decision = "N/A (Book 1 sizing,
qty 1)"), one per strategy per phase, written to `checker_input/`. The runner compares nothing. The checker returns
pass / fail and the mismatch list; that result goes into section 7 when Kyron gives it.

Open before the run: ambiguity A1. Book 1 published A0 Phases 1-2 under fill model v3.4 and A0 / C1 Phases 3-4 under
v3.5 (gap fill); the replay plan freezes v3.4 for the standardized R1-R4 comparison. The script's default reproduces
each result under the fill model it was published with and labels the column; `--fill v3.4` forces one model.

## 4. Deterministic replay diff (P0.3), unit-test logs (P0.5, P0.10), hand-check tables (P0.6-P0.9), samples (P0.11, P0.12), lookahead audit (P0.13)

- P0.3 diff: not run (needs the PC); the tool compares every CSV / JSON / Parquet row for row and must report an empty diff.
- Unit-test logs: `unit_tests/unit_tests_2026-11-01.log` (123 tests, PASS); P0.5 cases are in `test_fills_v34`, P0.10 in `test_risk`.
- Hand-check tables: synthetic ones are the tests (`test_vwap`, `test_map_v24`, `test_families`, `test_plan_fields`,
  `test_plan_v24`); real-day tables are produced by the two hand-check scripts on the PC.
- Candidate log and ledger samples: produced by the PC run (`P0.11_candidates_phase1.csv`, `R*_full.csv`); formats are
  fixed by `candidate_log.COLUMNS` and `ledger.LEDGER_COLUMNS` and tested.
- Lookahead audit: `audit_run.py` on the PC; the registry asserts strictly-before for every input.

## 5. Blinding exposures (full disclosure)

1. The runner read `FROZEN_STRATEGY.md` (Drive, Book 1 phase3 folder) for the exact C1 definition. That file also
   contains the Phase 3 final-combination result table (trade counts, net R, drawdown, verdict). The numbers were
   not used; the exposure is logged here and in `P0.1_blind_run_setup.md`. Recommendation: a results-free copy of the
   C1 definition for future runners.
2. The Book 1A phase docs and the design v3.10 change log quote Book 1 Phase 2 / 3 per-arm and A0 numbers; those are in
   the documents the runner was told to read.
3. The download agent listed (names only) the Phase 0 parity folder and the project folder; it opened no result file.

## 6. Ambiguities and missing definitions (full list in `ambiguities.md`)

Needs Kyron: A1 fill model for the C1 reproduction (v3.4 vs v3.5, above); A2 the "current Book 1 tag" is not reachable
(no git history on Drive or GitHub; the branch was created in NT82 with the sha256-listed reference copy, to be
confirmed against the PC's tagged checkout); A3 all real-data runs must happen on the PC.
Runner defaults inside the rules (changeable before the freeze): strict 08:10:00 cut; PO-1 window = min(prior-day
08:30, Sunday 17:00); strict swing ties; FLIP overlap over the first zone's width; 40-pt cap nearest the newer swing;
delta-band top 20% by rank and 40-pt window by largest |delta|; PO-9 volume share by bars closing beyond; gains do not
restore the daily budget; RISK_REJECT is not a trade; realized net R over the planned stop (Book 1 convention);
Bullish "held or reclaimed VAL" = window low touched the composite VAL and price is now above it; invalidation at the
nearer VAL / VAH. Written as null, never invented: far / thin overnight, ES level choice, 10-year / VIX thresholds and
sources, gamma ranks (until P1.1 runs), power-trade interval and size, R minimums at entry, M-J3 / M-J4 triggers, E4 hold N.

## 7. Checker's P0.4 result

Pending: the ledgers have not been produced yet (section 3). To be filled in when Kyron hands back the checker's
pass / fail and mismatch list.

## 8. What to do next (in order)

1. Kyron: confirm A1 (fill model per phase for the reproduction) and A2 (reference copy = frozen tag).
2. On the PC, follow `RUNBOOK_PC.md` top to bottom; hand `checker_input/` to the checker session.
3. Fill section 7; fix any systematic difference in code (never a threshold); rerun; then tag `book1a-phase0-freeze`.
4. Only then Phase 1.
