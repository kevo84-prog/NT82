# Book 1A Phase 0: runbook for the PC (K:\Databento_BackTesting)

Everything below runs from a fresh folder on the PC with the branch `book1a-phase0` checked out and the Book 1
code reachable as `BOOK1_ROOT` (the frozen tag on the PC; `book1_ref/` is only the Drive mirror used here).
No Book 1 result folder is read by any step. Order = checklist order. Each step writes into `Book1A\Phase0\`.

```bat
cd K:\Databento_BackTesting\Book1A
git clone https://github.com/kevo84-prog/NT82 code && cd code && git checkout book1a-phase0
set BOOK1_ROOT=K:\Databento_BackTesting
python -m book1a.run_phase0_tests ..\Phase0\unit_tests
```

| Item | Command | Output |
|---|---|---|
| 0 (C1 source) | none: `book1_ref\C1_definition_no_results.md` is the only C1 source the runner reads (created Nov 1, session 2). Do not open `FROZEN_STRATEGY.md`. | - |
| A2 | `python -m book1a.book1_ref_compare book1_ref\MANIFEST.md K:\Databento_BackTesting ..\Phase0\A2_book1_tag_compare.md --tag <frozen tag, e.g. phase4-result> --raw K:\Databento_BackTesting\raw` (run with the frozen tag checked out; the tool changes nothing) | A2_book1_tag_compare.md: every manifest file MATCH / DIFFERS / MISSING against the tag, plus HEAD and the tag commit. Report every DIFFERS / MISSING row to Kyron before P0.4 |
| P0.2 | `python -m book1a.manifest build K:\Databento_BackTesting\raw ..\Phase0\manifest_block1.csv` then `python -m book1a.manifest compare ..\Phase0\manifest_block1.csv K:\Databento_BackTesting\data_integrity_2025-10-21_2026-10-02.csv ..\Phase0\P0.2_checksums.md` | checksum table + comparison (must be PASS; the gate 6 table has no sha256 column, so sizes and file names are compared and our sha256 list becomes the Book 1A reference) |
| P0.3 | `python -m book1a.run_r1_r2 --sessions 2025-11-05 2025-12-15 --block1 K:\Databento_BackTesting --out ..\Phase0\replay_diff\runA` ; same with `runB` ; `python -m book1a.replay_diff ..\Phase0\replay_diff\runA ..\Phase0\replay_diff\runB ..\Phase0\replay_diff\diff.md --ignore run_id generated` | diff.md (must say DIFF EMPTY) |
| P0.4 | `python -m book1a.run_r1_r2 --phase phase1 --block1 K:\Databento_BackTesting --out ..\Phase0\runs\phase1 --map-first-utc <map_first_utc from backtest\phase2\phase2_config.json>` ; repeat for phase2, phase3, phase4 ; then copy `runs\phase*\checker_input\R1_A0.csv` and `R2_C1.csv` into `..\Phase0\checker_input\` as `R1_A0_<phase>.csv` / `R2_C1_<phase>.csv` | the hand-off to the checker; `r1_check_a0.json` must list 0 problems on the v3.4 phases |
| P0.6 | `python -m book1a.hand_checks.vwap_hand_check K:\Databento_BackTesting\raw ..\Phase0\hand_checks` | vwap_hand_check.md (PASS) |
| P0.7-P0.9 | `python -m book1a.hand_checks.plan_hand_check ..\Phase0\runs\phase1 K:\Databento_BackTesting ..\Phase0\hand_checks` | hand_check_<day>.md x 3 with the empty "hand" column to fill from the chart; the Book 1A plans and sidecars |
| P0.11 | `python -m book1a.candidate_log ..\Phase0\runs\phase1 ..\Phase0\runs\phase1\tape_strategy.csv.gz ..\Phase0\P0.11_candidates_phase1.csv` (as a module: `book1a.candidate_log.build(run, tape, out, sessions=[...3 days...])`) | candidate log, every tag present |
| P0.12 | the full ledgers written by P0.4 (`R1_A0_full.csv`, `R2_C1_full.csv`) and, for the sized strategies, `book1a.replay_risk.replay(...)` on the same run (see `book1a/replay_risk.py`) | ledger sample with theoretical R, realized net R and N |
| P0.13 | `python -m book1a.audit_run ..\Phase0\runs\phase1 ..\Phase0\hand_checks ..\Phase0\runs\phase1\R1_A0_full.csv ..\Phase0\lookahead` | lookahead_audit.csv + summary (0 violations, 0 missing) |
| P1.1 | `python -c "from book1a import gamma_ranks"` hooked to `gex_block1.py` per-strike net GEX (see the report, P1.1) | gamma1..5 per session, available_at D-1 23:00 ET |
| P1.2 | `python -m book1a.gex_check K:\Databento_BackTesting\gex_levels_block1.csv ..\Phase0\P1.2_gex_levels.md` | coverage table (PASS expected: 124 / 124) |
| P0.14 | only after every row above passes: `git tag book1a-phase0-freeze && git push origin book1a-phase0-freeze` | the freeze |

Notes
- `run_r1_r2.py` builds the daily-loop config from the Book 1 layout (`tapes\`, `bars\nq_1m.csv`, `bars\es_1m.csv`,
  the calendar and GEX files). If the Book 1 phase folders used other paths or history windows, copy them from
  `backtest\phase3\build_inputs.py` into `book1_cfg()` before running; they are inputs, not results.
- Fill model for P0.4: default `book1` (v3.4 on Phases 1-2, v3.5 on Phases 3-4) = Book 1's published per-phase setting, kept
  on Kyron's instruction (Nov 1, session 2). The exact v3.4 / v3.5 code difference is reported in `A1_fill_model_v34_v35_diff.md`.
- Mono must be on PATH (the harness runs `mono JeronHarness.exe` outside Windows; on Windows the exe runs directly).
