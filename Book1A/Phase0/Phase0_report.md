# Book 1A – Phase 0 report (DRAFT, in progress)

Runner: Claude Code cloud session, Nov 1, 2026. Branch `book1a-phase0` in `kevo84-prog/NT82`.
Package tag `book1a-phase0-v0.1` (per-module tags below). Controlling doc: "Book 1A – Replay plan"; task
list: "Book 1A – Phase 0 build checklist". No P&L was opened; see `P0.1_blind_run_setup.md` for the one
blinding exposure (the C1 definition file also held a Phase 3 result table).

## 0. Where this run stands (read first)

The engine this session can reach is incomplete in one decisive way: the Block 1 MBO data (44 GB), the
roll files and the Mono-compiled C# harness exist only on the PC (`K:\Databento_BackTesting`), and no
Remote Control folder was connected to this session. The `NT82` GitHub repository was empty. The full
Book 1 code, harness, NT source and static inputs were found on Drive and copied byte-exact into
`book1_ref/`. Consequence:

- Every Book 1A module the checklist needs was **built and unit-tested here** against the exact numbers in
  the checklist (93 + 13 tests, all passing; logs in `unit_tests/`).
- Every pass test that needs real sessions (P0.2 checksums, P0.3 two-session replay, P0.4 R1/R2 ledgers,
  P0.6-P0.9 hand checks on real days, P0.11-P0.13 on Phase 1 days) is **scripted but not executed**. Each one
  is marked `BUILT / NOT RUN` with the exact command to run on the PC.
- The freeze tag `book1a-phase0-freeze` is therefore **not applied**: the checklist says it is set only when
  every P0 item passes.

## 1. One line per checklist item

| # | Item | Status | Version tag | Date | Note |
|---|---|---|---|---|---|
| P0.1 | Blind run setup | PASS (with one logged exposure) | book1a-phase0-v0.1 | Nov 1 | `P0.1_blind_run_setup.md`: layout, allowed/forbidden files, access events. |
| P0.2 | Data unchanged since Book 1 | BUILT / NOT RUN | manifest-v1.0 | Nov 1 | `python -m book1a.manifest build K:\Databento_BackTesting\raw Book1A\Phase0\manifest_block1.csv` then `compare` against the gate 6 table `data_integrity_2025-10-21_2026-10-02.csv`. |
| P0.3 | Deterministic replay | BUILT / NOT RUN | replay-diff-v1.0 | Nov 1 | `book1a/run_r1_r2.py --sessions 2025-11-05 2025-12-15 --out runA` twice, then `python -m book1a.replay_diff runA runB Book1A\Phase0\replay_diff\diff.md --ignore run_id`. |
| P0.4 | R1 / R2 reproduction (E5) | BUILT / NOT RUN; ledgers not yet produced | ledger-v1.0 | Nov 1 | See section 3 and ambiguity A1 (fill model v3.4 vs v3.5 for C1). |
| P0.5 | Execution model v3.4 | PASS (unit tests on Book 1's unchanged `fills.py`) | fills.py (Book 1, unchanged) + test-fills-v34 | Nov 1 | 13 long/short cases; log `unit_tests/`. |
| P0.6 | 08:10 VWAP | PASS (synthetic hand calc) / real-day table NOT RUN | vwap-v1.0 | Nov 1 | `python -m book1a.hand_checks.vwap_hand_check K:\Databento_BackTesting\raw Book1A\Phase0\hand_checks` (Oct 22, Nov 5, Dec 15, Mar 16). |
| P0.7 | Map v2.4 Book 1A outputs | BUILT, 23 synthetic tests PASS / 3-day hand check NOT RUN | map-v2.4-book1a-v1.0 | Nov 1 | PO-1, PO-6, PO-7, PO-9, PO-11, PO-13 implemented; harness adapter pending. |
| P0.8 | Source families | PASS (hand-built list) | families-v1.0 | Nov 1 | Six families, GEX within 10 points, each counts once, DECISION = 2+. |
| P0.9 | Context and side fields | PASS (unit) / 3-day sample plans NOT RUN | plan-fields-v1.0 | Nov 1 | Most restrictive side wins; side_conflict logged; first_touch. |
| P0.10 | Risk check and sizing | PASS | risk-v1.0 | Nov 1 | All checklist numbers exact (196/96/63/36/16; 947.22 / 1,262.96). |
| P0.11 | R4 entries | PENDING (candidate log builder in progress) | - | - | Needs the JOFS candidate rows of a Phase 1 run. |
| P0.12 | M0 exits and R reporting | PASS (unit) / ledger sample NOT RUN | ledger-v1.0 | Nov 1 | Theoretical R and realized net R per trade, N recorded. |
| P0.13 | Timestamp and lookahead audit | PASS (unit) / real-day audit NOT RUN | lookahead-v1.0 | Nov 1 | Registry + strict before-decision assertion; standard available_at rules for swings, VWAP, GEX, map, L2. |
| P0.14 | Freeze | NOT DONE | - | - | Tag only when every P0 item passes on the PC. |
| P1.1 | Gamma ranks | PENDING | - | - | Needs the D-1 option files (PC). |
| P1.2 | Calculated GEX levels and available_at | PENDING | - | - | `gex_levels_block1.csv` columns to be checked; available_at = D-1 23:00 ET. |
| P2.x | Diagnostics | NOT STARTED | - | - | Do not delay P0. |

(to be completed)
