# Book 1A – Phase 0 report

Runner: Claude Code desktop session on Kyron's PC (`K:\Databento_BackTesting`), Nov 1-2, 2026, branch `book1a-phase0`
(worktree `K:\Databento_BackTesting\Book1A\code`), blind runner for the real-data part. Earlier cloud sessions 1-2
(build and unit tests) are in the git history of this file (commit 31979f1).
Controlling doc: "Book 1A – Replay plan", re-exported Nov 2 (Drive edit Nov 1 22:23Z: fill model v3.5 for R1-R4).
Checklist: "Book 1A – Phase 0 build checklist", re-exported the same way. No P&L was opened, summarized or looked at.
Book 1 was not edited, moved or overwritten (it was read in place; Book 1 caches were read through hard links).

## 0. Read first

- **Passed on real data:** P0.2 checksums, P0.3 deterministic replay (incl. the Dec 15, 2025 roll day), P0.5 v3.5
  gap-through tests (long and short), P0.6 VWAP (both roll days), P0.10, P0.11 candidate log, P0.12 ledger fields,
  P0.13 lookahead audit (0 violations, 0 missing), P1.1 gamma ranks (124 / 124 sessions; Nov 2, Book 1A venv), P1.2.
- **Waiting for others:** **P0.4: waiting for checker** (8 ledgers in `checker_input/`, not compared to anything by
  the runner). P0.7-P0.9: tables produced on 4 Phase 1 days; the "hand" column must be filled by Kyron from the
  chart (the runner machine-checked only what the tables state themselves).
- **Kyron's Nov 2 decisions, done:** (1) branch pushed to GitHub as a new branch `book1a-phase0-pc` (no force,
  `book1a-phase0` untouched); (2) P1.1 run in a separate Book 1A Python venv (system / Book 1 Python unchanged);
  (3) Book 1 result text moved out of the root CLAUDE.md into `BOOK1_RESULTS_PRIVATE.md`, and a rules-only
  `Book1A\CLAUDE.md` created (section 5).
- **Not run:** P2 (only after every P0 item passes). **Freeze tag not applied.**
- **Code fixed on the PC (systematic differences, no threshold touched):** R3 / R4 now default to fill model v3.5;
  the R1 / R2 daily-loop config now equals Book 1's phase configs key for key (it started the map one day late) and
  builds the bar files from raw; the checker ledgers now carry the target (it was `nan`); the P0.2 compare no longer
  pairs two different files that share a name. Full list: `ambiguities.md` section E (E1-E20).

## 1. One line per checklist item

| # | Item | Status | Version tag / commit | Date | Note |
|---|---|---|---|---|---|
| step 0 | C1 source | DONE | `book1_ref/C1_definition_no_results.md` | Nov 2 | The only C1 source read. `run_r1_r2.py` R2 call checked against it: FZ1 ∪ L1 ∪ T8 veto first, RH1 15 bars / 2-tick fail / stop at retest extreme ± 2 ticks, M0, v3.5 on Phases 3-4. `FROZEN_STRATEGY.md` not opened. |
| A2 | Book 1 reference vs frozen tag | DONE, 0 code differences | book1-ref-compare-v1.0, tag `phase4-result` (8d3a291) | Nov 2 | 41 manifest files: 39 MATCH, 0 DIFFERS, 2 MISSING at the manifest path, both explained (section 3). HEAD `4cc698d` = tag + 1 research commit touching only `backtest/research/c1_losers/`. |
| P0.1 | Blind run setup | PASS, exposures logged | `P0.1_blind_run_setup.md` | Nov 2 | Item 5 added for the PC run: CLAUDE.md and the commit subjects shown at session start carry Book 1 result numbers; the replay plan quotes two in-sample R totals. None used. |
| P0.2 | Data unchanged since Book 1 | **PASS** | manifest-v1.0 (+ path join, b206e45) | Nov 2 | 161 of 161 gate 6 rows present at the same relative path and size (0 missing, 0 differing); 10,162 files hashed (sha256) in `manifest_all.csv` = the Book 1A reference. `gex_levels_block1.csv` and the econ calendar match `book1_ref` by sha256 (A2). |
| P0.3 | Deterministic replay | **PASS: DIFF EMPTY** | run-r1-r2-v1.0, replay-diff-norm-v1.0 (bbab572) | Nov 2 | Nov 5 and Dec 15, 2025 (roll day) run twice from scratch (map, plans, harness, fills, R1, R2). 146 files identical after removing only wall-clock stamps and the run-folder path; ledgers, fills, attempts, retests and plans identical in `replay_diff` too. |
| P0.4 | R1 / R2 reproduction (E5) | **WAITING FOR CHECKER** | run-r1-r2-v1.0, ledger-v1.0; code 54ec485 (Phases 1-2) / cbb5fdb (Phases 3-4) | Nov 2 | `checker_input/R1_A0_phase1..4.csv`, `R2_C1_phase1..4.csv` (checker columns; target now filled). Fill model as published: v3.4 Phases 1-2, v3.5 Phases 3-4. `check_a0` 0 problems on Phases 1-2 (on v3.5 phases the gate is not run, E14). Not compared to anything by the runner. |
| P0.5 | Execution model v3.5 | **PASS** | test-fills-v34 + TestV35GapThrough (b206e45) | Nov 2 | Gap-through stop, long (stop 23990, first trade 23985.00 → 23984.75 / .50 / 23984.00 at 1 / 2 / 4 ticks) and short (stop 24010, first trade 24015.00 → 24015.25 / .50 / 24016.00), on both Book 1 fill paths (`fills.simulate`, `exit_replay.replay` with the v3.5 settings); no gap = v3.4. 16 fill tests, all v3.4 rules too. R3 / R4 default v3.5 (test pins it). |
| P0.6 | 08:10 VWAP | **PASS** | vwap-v1.0, vwap-hand-check (9943922) | Nov 2 | Oct 22, Nov 5 (normal), Dec 15, 2025 and Mar 16, 2026 (roll days): session and weekly VWAP and 1σ equal the pandas hand calculation, equal trade counts. Roll days use the new contract (NQH6 id 42002475, NQM6 id 42004058, from the roll files' symbol maps): both VWAPs restart (U1). Table in section 4. |
| P0.7 | Map v2.4 Book 1A outputs | TABLES READY, hand column for Kyron | map-v2.4-book1a-v1.0, plan-v2.4-book1a-v1.0 | Nov 2 | `hand_checks/hand_check_2025-10-22/-28/-11-04.md` + Oct 31 (added: the three checklist days have no REJ / FLIP zone; Oct 31 has 4). No DD_EDGE on any Phase 1 day. Every zone carries available_at 08:10 CT. |
| P0.8 | Source families (C1, C2) | TABLES READY; machine check PASS | families-v1.0 | Nov 2 | On the 3 days: families unique on every zone, DECISION has 2+, the GEX family is present exactly when a gamma level is inside or within 10 points (e.g. Oct 28 CR 26000 is 24.75 pts from WKVAH: no GEX family). Hand families for Kyron. |
| P0.9 | Context and side fields | TABLES READY, hand column for Kyron | plan-fields-v1.0 | Nov 2 | All fields written for every zone before the open (market_context, draw_status, draw, balance, balance_poc, value_follows, edge / side, htf_structure, first_touch, side_conflict, ladder). |
| P0.10 | Risk check and sizing | PASS (unit) | risk-v1.0 | Nov 2 | 131-test run (0 failures) includes the 15 risk tests (log `unit_tests/unit_tests_2026-11-02.log`). |
| P0.11 | R4 entries | **PASS** | candidate-log-v1.0 | Nov 2 | `P0.11_candidates_phase1.csv`: 1,992 CANDIDATE / SHADOW rows on Oct 22, 28, Nov 4; every Phase 5 tag column filled ("null" when not measurable); FZ1 `LOGGED_ONLY` on every row; T8, L1, RH1 state, C3 decision, U2 note present. Blank cells only in copied S1.4 fields (gate_reasons on passing rows, target on rejected rows, shadow_of on non-shadows). |
| P0.12 | M0 exits and R reporting | **PASS (fields)** | ledger-v1.0, replay-risk-v1.0 | Nov 2 | `P0.12/R3_M0_phase1_ledger.csv`, `R4_M0_phase1_ledger.csv`: theoretical R, realized net R, N, planned risk, risk decision on every row, fill model v3.5. Written, not summarized. R4 sample uses the R4 entry gates on A0's plans (E17). |
| P0.13 | Timestamp and lookahead audit | **PASS** | lookahead-v1.0, audit-run-v1.0 | Nov 2 | Phase 1, every R1 entry: 7 decisions, 117 inputs, 0 violations, 0 missing (Book 1A plans built for all 10 Phase 1 days in `plans_phase1/`). R3: 1 / 16 / 0 / 0; R4: 3 / 52 / 0 / 0. |
| P0.14 | Freeze | NOT DONE (by instruction) | - | - | P0.4 and P0.7-P0.9 still open. |
| P1.1 | Gamma ranks (U6) | **PASS** | gamma-ranks-v1.0, gamma-ranks-pc-v1.1 | Nov 2 | Run in `K:\Databento_BackTesting\Book1A\.venv` (Python 3.14.7, scipy 1.18.1, numpy 2.5.3, pandas 3.0.6, databento 0.87.0; full list `P1.1_venv_requirements.txt`). Book 1 pipeline (`gex_block1.build`, `gex_calc.cme_day`, `mq_levels.strike_gex`) unchanged. 124 / 124 sessions ranked; largest positive / most negative strike = call_resistance / put_support on 124 / 124. Hand Black-76 ranking (no mq_levels code) equals the module top 5 on Nov 5, 2025 and Jan 15, 2026. The venv reproduces gex_levels_block1.csv on those 2 days: 22 / 22 values equal (front, settle, CR, PS, HVL, the three 0DTE levels, regime, options_used; net_gex equal to 15 significant digits). Only option / futures input files read. |
| P1.2 | Calculated GEX levels | PASS (cloud session) | gex-check-v1.0 | Nov 1 | Unchanged; the file's sha256 matches (A2). |
| P2.1-P2.9 | Diagnostics | NOT RUN | - | - | Not every P0 item has passed. |

## 2. Deliverables in this folder

| File | What |
|---|---|
| `A2_book1_tag_compare.md` | A2 table and the runner's follow-up on the 2 MISSING rows |
| `manifest_all.csv`, `manifest_block1.csv`, `manifest_nq_mbo_2026-09/-10.csv`, `P0.2_checksums.md`, `P0.2_build.log` | P0.2 |
| `replay_diff/diff.md` (normalised, DIFF EMPTY), `replay_diff/diff_raw_replay_diff.md` (short stub in git: the raw file is 1.4 GB, over GitHub's 100 MB limit; full file with its sha256 on the PC at `K:\Databento_BackTesting\Book1A\replay_diff_full\`), `runA_console.log`, `runB_console.log` | P0.3 (run folders kept on the PC, not in git) |
| `checker_input/R1_A0_phase1..4.csv`, `R2_C1_phase1..4.csv` | P0.4 hand-off |
| `runs/phase1..4_console.log`, `runs/phase*_ledgers.log`, `runs/phase4_console_attempt1_memoryerror.log` | P0.4 run logs (run folders on the PC only) |
| `unit_tests/unit_tests_2026-11-02.log` | 131 tests, 0 failures (P0.5, P0.10 and all others) |
| `hand_checks/vwap_hand_check.md` | P0.6 |
| `P1.1_gamma_ranks.md`, `P1.1_gamma_ranks.csv`, `P1.1_venv_requirements.txt` | P1.1 (gamma1-5 per session, checks, venv package versions) |
| `hand_checks/hand_check_<day>.md`, `PreopenPlan_<day>_book1a.txt/.json` | P0.7-P0.9 (Oct 22, Oct 28, Oct 31, Nov 4, 2025) |
| `plans_phase1/` | Book 1A plans and sidecars, all 10 Phase 1 days (input to P0.13) |
| `P0.11_candidates_phase1.csv` | P0.11 |
| `P0.12/R3_M0_phase1_ledger.csv`, `R4_M0_phase1_ledger.csv` | P0.12 |
| `lookahead/`, `lookahead_R3/`, `lookahead_R4/` | P0.13 |
| `ambiguities.md` | every ambiguity; section E = this run |
| `P0.1_blind_run_setup.md` | layout, access rules, access events (item 5 = this run) |
| `RUNBOOK_PC.md` | commands as run |

## 3. A2: every differing file

| Manifest file | Result | Note |
|---|---|---|
| 39 files (jeron_engine, jeron_harness, nt_source, phase run scripts and configs, static inputs) | MATCH | same sha256 as `book1_ref` and as tag `phase4-result` (no tracked file modified; HEAD differs from the tag only under `backtest/research/c1_losers/`) |
| `backtest/phase0_parity/phase0_data_integrity_2025-10-21_2026-10-02.csv` | MISSING at that path; MATCH at `K:\Databento_BackTesting\data_integrity_2025-10-21_2026-10-02.csv` | path difference only |
| `phase0_parity.py` | not in git (neither tag nor HEAD); Drive copy = manifest; PC copy `backtest_scripts\phase0_parity.py` (Oct 24) is older: CME roll dates Dec 11 / Mar 12 instead of NinjaTrader's Dec 15 / Mar 16, no Databento-degraded-day list | not used by Book 1A; Kyron to decide whether the PC copy should be replaced (not done: Book 1 frozen) |

## 4. Logs and hand-check tables

### P0.3
`replay_diff/diff.md`: **DIFF EMPTY**, 146 files compared (map packets and zones for every map day Sep 22 - Dec 15, 2025,
plans, strategy log, harness orders, fills_model, day sheets, both ledgers, attempts, retests, bars, both tapes by
content hash). Normalised only: gzip headers, `built=` / `built_local` wall-clock stamps, `_run<clock>` in two map
file names, the run-folder path, run_manifest `generated` / `commit`, the strategy log's ProcessedTimeLocal column
and file-name clock. The code that the run imports was the same in both runs (`git diff b206e45 1ba7b04` touches
only the VWAP hand check, the P1.1 script and docs).

### P0.6 (`hand_checks/vwap_hand_check.md`)

| day | scope | trades hand = module | VWAP hand | VWAP module | 1σ hand = module | result |
|---|---|---|---|---|---|---|
| 2025-10-22 | session | 56,808 | 25267.379648 | 25267.379648 | 29.249935 | PASS |
| 2025-10-22 | weekly | 341,243 | 25280.433866 | 25280.433866 | 31.868837 | PASS |
| 2025-11-05 | session | 126,139 | 25464.252037 | 25464.252037 | 78.513881 | PASS |
| 2025-11-05 | weekly | 568,439 | 25674.355143 | 25674.355143 | 146.652217 | PASS |
| 2025-12-15 (roll, NQH6) | session = weekly (restart) | 32,709 | 25544.449065 | 25544.449065 | see file | PASS |
| 2026-03-16 (roll, NQM6) | session = weekly (restart) | 55,890 | 24756.317678 | 24756.317678 | see file | PASS |

### P0.7-P0.9
Four files `hand_checks/hand_check_<day>.md`, each with three tables (zones with available_at; families= and
levels= per decision zone; context and side fields with ladder) and an empty "hand" column. Machine check on
Oct 22, Oct 28, Nov 4 (section 1, P0.8). Observation: the Oct 22 decision zone `D_PDL_ONL_..._ONPOC_AREA` is 66.75
points wide (stop 269 ticks); within the rules (E16), a RISK_REJECT under C3.

### P0.13
`lookahead/lookahead_summary.json`: decisions 7, inputs 117, violations 0, missing 0, passed true (map packet 08:10,
every zone 08:10, session and weekly VWAP 08:10, every GEX level D-1 23:00 ET, swings formed + 15 bars for REJ / FLIP
zones). R3 and R4 audits likewise 0 / 0.

## 5. Blinding exposures

1-4: cloud sessions (see `P0.1_blind_run_setup.md`). 5 (this run): the PC's root `CLAUDE.md` and the git commit
subjects that Claude Code shows at session start carry Book 1 Phase 3 / Phase 4 result numbers; the re-exported replay
plan quotes two in-sample R totals; while checking the `target` column the runner saw the count of stop / target exits
in our own Phase 2 R1 reproduction. Nothing used. Recommendation: start the next blind session in
`K:\Databento_BackTesting\Book1A\` with its own CLAUDE.md, and keep result numbers out of the root CLAUDE.md.

**Fix done Nov 2 (Kyron's decision 3).** Moved word for word from the root `CLAUDE.md` phase table into
`K:\Databento_BackTesting\BOOK1_RESULTS_PRIVATE.md` (the runner wrote it and has not opened it since):
- Phase 1 status cell: the one-word outcome. Now: "run (result: `BOOK1_RESULTS_PRIVATE.md`)".
- Phase 3 status cell: which arms were promoted, the C1 composition line with its net R per session and lower bound,
  and the frozen-strategy file path. Now: "done Oct 26, 2026; final combination C1 frozen (code `phase3-combination`;
  results tag `phase3-results`). Results: `BOOK1_RESULTS_PRIVATE.md`".
- Phase 4 status cell: the holdout verdict, the failing test with its day and trade size, the C1 R total, R per
  session, lower bound, drawdown and the results file path. Now: "run once Oct 26, 2026 (code `phase4-holdout-fix2`).
  Result: `BOOK1_RESULTS_PRIVATE.md`".
Nothing else moved: the Phase 0 and 2 cells, the integrity rules, folder map and run instructions carry no result and
are unchanged (no rule text edited). The root CLAUDE.md edit is not committed in the Book 1 repository (Kyron's
call). New `K:\Databento_BackTesting\Book1A\CLAUDE.md`: rules only (layout, blinding, method), no results. Still
exposed: the old text in Book 1's git history and the commit subjects (not rewritten). Note: a session started in
`Book1A\` still loads the root CLAUDE.md as well; it is now result-free.

## 6. Ambiguities

All in `ambiguities.md` (A1-A3, B1-B20, C1-C8 from the cloud sessions; E1-E20 from this run). The ones Kyron must
decide:
- E5: Book 1's tapes are reused (derived from the raw MBO, not results). Rebuild for Book 1A?
- E6 / E20: the repository has `Book1A/` and `book1a/`, which collide on Windows. Rename one?
- E17: no runbook step yet feeds the Book 1A v2.4 plans to S1.4 for an R4 run.
- E19: replace the stale `backtest_scripts\phase0_parity.py` with the Drive version?
- P0.7 day choice: the three checklist days have no REJ / FLIP zone; Oct 31 was added.

## 7. Checker's P0.4 result

**P0.4: waiting for checker.** The 8 ledgers are in `checker_input/`. The runner has not compared them with anything.

## 8. Next

1. Separate checker session: compare `checker_input/` with the Book 1 trade lists; return pass / fail and mismatches.
2. Kyron: fill the hand columns (P0.7-P0.9), answer section 6. The checker reads the ledgers from GitHub branch
   `book1a-phase0-pc`.
3. Fix any systematic mismatch in code, rerun the affected items, then P0.14 freeze. Only then Phase 1.
