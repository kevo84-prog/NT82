# Book 1A – Phase 0 report

Runner: Claude Code desktop session on Kyron's PC (`K:\Databento_BackTesting`), Nov 1-2, 2026, branch `book1a-phase0`
(worktree `K:\Databento_BackTesting\Book1A\code`), blind runner for the real-data part. Earlier cloud sessions 1-2
(build and unit tests) are in the git history of this file (commit 31979f1).
Controlling doc: "Book 1A – Replay plan", re-exported Nov 2 (Drive edit Nov 1 22:23Z: fill model v3.5 for R1-R4).
Checklist: "Book 1A – Phase 0 build checklist", re-exported the same way. No P&L was opened, summarized or looked at.
Book 1 was not edited, moved or overwritten (it was read in place; Book 1 caches were read through hard links).

## 0. Nov 4 update (read this first)

Session 3 on the PC, Nov 4, 2026, branch `book1a-phase0-pc` (local commits, not pushed). Blind runner. Book 1 not
edited. No P&L opened or summarized. The checker's result file was copied, not opened. **Not frozen.**

**What was done**
1. **C1 Phase 2 recheck (v3.5).** `R2_C1_phase2_v35.csv` written by `book1a.recheck_c1_v35` (the R2 call of
   `run_r1_r2`, fill model v3.5, on the finished Phase 2 A0 run; the run folder and the v3.4 ledger untouched).
   Copied to `K:\Book1A_checker\checker_input\` and to `checker_input/`; sha256 f41050f0...d5989 added to
   `checker_input_sha256.txt`. All 9 files there match their listed sha256. The v3.4 file `R2_C1_phase2.csv` is
   unchanged (sha256 26bc3804...e9819, as before). Not compared to anything by the runner.
2. **Checker result.** `K:\Book1A_checker\checker_output\P0.4_result.md` copied to `checker_output/P0.4_result.md`
   (same sha256 4a1aef8a...82201), not opened. Recorded as Kyron gave it (section 7).
3. **E17 closed: R4 reads the Book 1A plans.** New `book1a.run_r4` (run-r4-v1.0). For every session it requires
   `PreopenPlan_<day>_book1a.txt` + `.json` with plan_id `<day>-b1a` and the plan builder version, or it stops
   (`R4PlanError`, no fallback to an A0 plan). It copies the plans byte for byte to the names S1.4 reads, runs S1.4
   with the A0 run's own arguments (only the plan folder differs), then checks the strategy log: one `PLAN_LOADED
   id=<day>-b1a` per day from that folder, no plan problem row, every plan-zone candidate tagged with the Book 1A
   plan. R4 = L1 | T8 veto, RH1, M0, v3.5, C3 risk and sizing; FZ1 logged only. Every ledger and candidate row
   carries `plan_version`, `plan_id`, `plan_sha256`, `plan_sidecar_sha256`; candidate rows on a plan zone also carry
   the zone's Book 1A class, families, long / short sides and the day's market_context. Test `test_run_r4` (8 tests):
   a missing plan or sidecar stops the run before the harness, also when an A0 plan for that day is present; an A0
   plan under the Book 1A name stops it; S1.4 loading an A0 plan stops it.
   - P0.11 rerun for R4 on Oct 22, 28, Nov 4: `P0.11_candidates_phase1.csv`, 2,058 rows, every row on the Book 1A
     plan of its day (hash checked), FZ1 `LOGGED_ONLY`, all tags present.
   - P0.12 rerun for R4 on all 10 Phase 1 days: `P0.12/R4_M0_phase1_ledger.csv` (+ plan manifest, run manifest,
     strategy arguments, console log): theoretical R, realized net R, N, planned risk, risk decision, fill v3.5 and
     the plan identity on every row (hash checked). Written, not summarized.
   - P0.13 rerun for R4: 0 violations, 0 missing (12 decisions, 194 inputs). The audit reads the same sidecars R4
     used (sha256 equal). R1 and R3 audits rerun on the rebuilt sidecars: 0 / 0.
   - The Nov 2 R4 samples (built on A0 plans) are replaced; they stay in git at d135225.
4. **Two map / plan bugs found and fixed while building the pack** (no threshold touched; `ambiguities.md` F):
   E21 DD_EDGE never formed (the packet's keys were not read); E22 merged REJ zones lost their swing time, so the
   FLIP check looked for acceptance before the zone existed. Plans rebuilt (plan-v2.4-book1a-v1.1,
   map-v2.4-book1a-v1.1); R4 and all P0.13 audits rerun on them. Phase 1 plan text changed only on Oct 29 (DD_EDGE
   merged into the PDPOC decision zone; short side INITIATION only, as PO-11 says).
5. **P0.7-P0.9 hand-check pack:** `hand_check_pack/hand_check_pack.md` (13 days: the 10 Phase 1 days and Nov 17-19;
   Nov 17-19 plans in `hand_check_pack/plans/`; command in `hand_check_pack/command.txt`). Sections: A decision
   zones (Oct 22 normal, Oct 29 with DD_EDGE, Oct 31 built on a REJ, Oct 22 wide), B every REJ zone (swing bar time
   and price, the 15-bar check, arrival-evidence bar, departure bar, body bars), C FLIP check for every REJ zone
   (none forms), D every wide-stop zone (9) with the C3 numbers, E DD_EDGE (Oct 29, Nov 3, Nov 18) with the PD
   profile rows. Each row names the chart time and price, or the profile / delta row, to check. No trades or P&L.
6. Unit tests: 143 run, 0 failures, 0 errors on commit e137fa5 (`unit_tests/unit_tests_2026-11-04.log`).

### Parity levels

| Area | Passed for the available fields | Pending | Not verifiable from Book 1 files | R4 integration |
|---|---|---|---|---|
| Raw data (P0.2) | 161 / 161 gate 6 files, same path and size | - | sha256 (gate 6 lists sizes only; our list is the new reference) | same data |
| Book 1 code used (A2) | 39 / 39 manifest files equal the frozen tag | - | `phase0_parity.py` (not in git; E19) | R4 uses the same engine, harness and S1.4 |
| R1 A0 reproduction (P0.4) | Phases 1-4 PASS (checker) | - | - | n/a |
| R2 C1 reproduction (P0.4) | Phases 3-4 PASS (checker) | Phase 2: FAIL on the v3.4 ledger, pending the v3.5 recheck (file handed over) | Phase 1: no Book 1 reference | n/a |
| Determinism (P0.3) | 146 files identical over two runs | - | - | R4 not yet run twice |
| Fill model (P0.5) | v3.4 and v3.5 rules, gap-through long and short | - | - | R4 runs v3.5 |
| VWAP (P0.6), GEX (P1.1, P1.2) | hand VWAP equal on 4 days; GEX levels 22 / 22 on 2 days; ranks 124 / 124 | - | - | in the Book 1A plan families |
| Book 1A map / plan (P0.7-P0.9) | machine checks (families unique, DECISION 2+, GEX within 10 pts); unit tests | Kyron's chart check (pack); E23 weekly double distribution | all of it (Book 1A only, no Book 1 counterpart) | R4 reads plan v1.1 on 10 / 10 Phase 1 days |
| R4 entries, exits, risk (P0.10-P0.12) | fields present on every row; 0 missing tags; plan identity on every row | - | all of it (Book 1A only) | wired (E17 closed); Phase 1 only |
| Lookahead (P0.13) | R1 7 / R3 1 / R4 12 decisions: 0 violations, 0 missing | - | - | R4 audit on the Book 1A plans |

### Open items

| # | Item | Status | Blocks the freeze? |
|---|---|---|---|
| 1 | R2 C1 Phase 2 v3.5 recheck | `R2_C1_phase2_v35.csv` with the checker | Yes |
| 2 | P0.7-P0.9 chart check | pack ready for Kyron | Yes |
| 3 | E23 weekly double distribution (PO-11) | not built; Kyron: PD only, or give a weekly rule | Yes |
| 4 | E21 / E22 bug fixes (DD_EDGE, merged REJ) | done; Kyron to look at the Oct 29 plan change | Yes, until Kyron accepts |
| 5 | E25 no real FLIP on the 13 days | rule unit-tested only | Kyron decides (runner: not blocking) |
| 6 | R2 Phase 1 has no Book 1 reference | cannot be checked | Kyron decides (runner: not blocking) |
| 7 | E5 reuse of Book 1's tapes | Kyron decides | Yes, until decided |
| 8 | E6 / E20 `Book1A/` vs `book1a/` folder names | works on the PC | No |
| 9 | E19 stale `backtest_scripts\phase0_parity.py` | not used by Book 1A | No |
| 10 | E24 `reward_risk` blank on 23 S1.4 rows | copied S1.4 field | No |
| 11 | R4 determinism (two runs) and R4 on Phases 2-4 | not run (Phase 1 and later work) | No |
| 12 | Push of the Nov 4 commits to `book1a-phase0-pc` | local only | No (Kyron's call) |
| 13 | P0.14 freeze tag | not applied (instruction) | - |

## 0b. Read first (Nov 2)

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
| P0.4 | R1 / R2 reproduction (E5) | **R1 Phases 1-4 PASS; R2 Phases 3-4 PASS; R2 Phase 1 no reference; R2 Phase 2 FAIL pending the v3.5 recheck** (checker, Nov 3; recheck ledger handed over Nov 4) | run-r1-r2-v1.0, ledger-v1.0; code 54ec485 (Phases 1-2) / cbb5fdb (Phases 3-4); recheck-c1-v35-v1.0 | Nov 2 / Nov 4 | `checker_input/R1_A0_phase1..4.csv`, `R2_C1_phase1..4.csv` (checker columns; target now filled). Fill model as published: v3.4 Phases 1-2, v3.5 Phases 3-4. `check_a0` 0 problems on Phases 1-2 (on v3.5 phases the gate is not run, E14). Not compared to anything by the runner. |
| P0.5 | Execution model v3.5 | **PASS** | test-fills-v34 + TestV35GapThrough (b206e45) | Nov 2 | Gap-through stop, long (stop 23990, first trade 23985.00 → 23984.75 / .50 / 23984.00 at 1 / 2 / 4 ticks) and short (stop 24010, first trade 24015.00 → 24015.25 / .50 / 24016.00), on both Book 1 fill paths (`fills.simulate`, `exit_replay.replay` with the v3.5 settings); no gap = v3.4. 16 fill tests, all v3.4 rules too. R3 / R4 default v3.5 (test pins it). |
| P0.6 | 08:10 VWAP | **PASS** | vwap-v1.0, vwap-hand-check (9943922) | Nov 2 | Oct 22, Nov 5 (normal), Dec 15, 2025 and Mar 16, 2026 (roll days): session and weekly VWAP and 1σ equal the pandas hand calculation, equal trade counts. Roll days use the new contract (NQH6 id 42002475, NQM6 id 42004058, from the roll files' symbol maps): both VWAPs restart (U1). Table in section 4. |
| P0.7 | Map v2.4 Book 1A outputs | PACK READY for Kyron (Nov 4, `hand_check_pack/`); E21, E22 fixed; E23 open | map-v2.4-book1a-v1.1, plan-v2.4-book1a-v1.1 | Nov 4 | `hand_checks/hand_check_2025-10-22/-28/-11-04.md` + Oct 31 (added: the three checklist days have no REJ / FLIP zone; Oct 31 has 4). No DD_EDGE on any Phase 1 day. Every zone carries available_at 08:10 CT. |
| P0.8 | Source families (C1, C2) | TABLES READY; machine check PASS | families-v1.0 | Nov 2 | On the 3 days: families unique on every zone, DECISION has 2+, the GEX family is present exactly when a gamma level is inside or within 10 points (e.g. Oct 28 CR 26000 is 24.75 pts from WKVAH: no GEX family). Hand families for Kyron. |
| P0.9 | Context and side fields | TABLES READY, hand column for Kyron | plan-fields-v1.0 | Nov 2 | All fields written for every zone before the open (market_context, draw_status, draw, balance, balance_poc, value_follows, edge / side, htf_structure, first_touch, side_conflict, ladder). |
| P0.10 | Risk check and sizing | PASS (unit) | risk-v1.0 | Nov 2 | 131-test run (0 failures) includes the 15 risk tests (log `unit_tests/unit_tests_2026-11-02.log`). |
| P0.11 | R4 entries | **PASS, rerun on the Book 1A plans** (Nov 4, section 0) | candidate-log-v1.1, run-r4-v1.0 | Nov 4 | `P0.11_candidates_phase1.csv`: 1,992 CANDIDATE / SHADOW rows on Oct 22, 28, Nov 4; every Phase 5 tag column filled ("null" when not measurable); FZ1 `LOGGED_ONLY` on every row; T8, L1, RH1 state, C3 decision, U2 note present. Blank cells only in copied S1.4 fields (gate_reasons on passing rows, target on rejected rows, shadow_of on non-shadows). |
| P0.12 | M0 exits and R reporting | **PASS (fields); R4 rerun on the Book 1A plans** (Nov 4) | ledger-v1.0, replay-risk-v1.0, run-r4-v1.0 | Nov 4 | `P0.12/R3_M0_phase1_ledger.csv`, `R4_M0_phase1_ledger.csv`: theoretical R, realized net R, N, planned risk, risk decision on every row, fill model v3.5. Written, not summarized. R4 sample uses the R4 entry gates on A0's plans (E17). |
| P0.13 | Timestamp and lookahead audit | **PASS** (Nov 4 rerun: R1 7 / R3 1 / R4 12 decisions, 0 violations, 0 missing) | lookahead-v1.0, audit-run-v1.0 | Nov 4 | Phase 1, every R1 entry: 7 decisions, 117 inputs, 0 violations, 0 missing (Book 1A plans built for all 10 Phase 1 days in `plans_phase1/`). R3: 1 / 16 / 0 / 0; R4: 3 / 52 / 0 / 0. |
| P0.14 | Freeze | NOT DONE (by instruction) | - | - | Open items 1-4 and 7 (section 0) block it. |
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

Original result (checker, Nov 3), recorded as Kyron gave it; the file `checker_output/P0.4_result.md` was copied
unopened: **R1 Phases 1-4 PASS. R2 Phases 3-4 PASS. R2 Phase 1: no reference. R2 Phase 2: FAIL, pending the v3.5
recheck.** This original result stays as it is. The recheck (`checker_input/R2_C1_phase2_v35.csv`: C1, Phase 2,
fill model v3.5) went to the checker on Nov 4; its result will be added here separately.

## 8. Next (Nov 2; superseded by section 0, open items)

1. Separate checker session: compare `checker_input/` with the Book 1 trade lists; return pass / fail and mismatches.
2. Kyron: fill the hand columns (P0.7-P0.9), answer section 6. The checker reads the ledgers from GitHub branch
   `book1a-phase0-pc`.
3. Fix any systematic mismatch in code, rerun the affected items, then P0.14 freeze. Only then Phase 1.
