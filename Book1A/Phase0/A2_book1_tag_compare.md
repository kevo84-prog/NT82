# A2: book1_ref manifest vs the Book 1 checkout at `K:\Databento_BackTesting`

Generated 2026-11-02T03:53:23+00:00 by book1-ref-compare-v1.0. Manifest `book1_ref\MANIFEST.md` (41 files).

| git | |
|---|---|
| head | `4cc698df10804e8bc37f7c5712adeb6652db45a9` |
| describe | `phase4-result-1-g4cc698d` |
| status | `` |
| tag | `phase4-result` |
| tag_commit | `8d3a2913766591def815bce09df58c5ea0957369` |
| head_is_tag | `False` |

**FAIL**: 39 match, 0 differ, 2 missing.

| manifest path | result | PC path | sha256 (manifest vs PC) | bytes (manifest vs PC) |
|---|---|---|---|---|
| databento_pull.py | MATCH | `K:\Databento_BackTesting\databento_pull.py` | d0a776bc16e4… | 17057 |
| data_integrity.py | MATCH | `K:\Databento_BackTesting\data_integrity.py` | bcc4c3bcd0e7… | 12712 |
| gex_block1.py | MATCH | `K:\Databento_BackTesting\gex_block1.py` | 6365a25d3045… | 11059 |
| l2_features.py | MATCH | `K:\Databento_BackTesting\l2_features.py` | 8c701c02805e… | 23473 |
| phase0_parity.py | **MISSING** | `` | 9a48104a2f0f0b20491291d16a68e96e0f07989a8ce9c1147bea249ded6c0103 |  |
| jeron_engine/__init__.py | MATCH | `K:\Databento_BackTesting\jeron_engine\__init__.py` | 8d1b824113b9… | 214 |
| jeron_engine/arm_replay.py | MATCH | `K:\Databento_BackTesting\jeron_engine\arm_replay.py` | 7d7ee554afef… | 19115 |
| jeron_engine/arms.py | MATCH | `K:\Databento_BackTesting\jeron_engine\arms.py` | 92267c6b4b21… | 8059 |
| jeron_engine/block_inputs.py | MATCH | `K:\Databento_BackTesting\jeron_engine\block_inputs.py` | 81c2c9a745d5… | 2984 |
| jeron_engine/candidate_parity.py | MATCH | `K:\Databento_BackTesting\jeron_engine\candidate_parity.py` | dd9d10c4eb91… | 5902 |
| jeron_engine/chart_check.py | MATCH | `K:\Databento_BackTesting\jeron_engine\chart_check.py` | c2adcaeaa30e… | 5793 |
| jeron_engine/daily_loop.py | MATCH | `K:\Databento_BackTesting\jeron_engine\daily_loop.py` | c8bff8c32d37… | 10954 |
| jeron_engine/exit_replay.py | MATCH | `K:\Databento_BackTesting\jeron_engine\exit_replay.py` | 857aa35cd366… | 12619 |
| jeron_engine/fills.py | MATCH | `K:\Databento_BackTesting\jeron_engine\fills.py` | 1b93cbdebef4… | 10165 |
| jeron_engine/gex_overlap.py | MATCH | `K:\Databento_BackTesting\jeron_engine\gex_overlap.py` | c1def5ab4b2c… | 2830 |
| jeron_engine/map_parity.py | MATCH | `K:\Databento_BackTesting\jeron_engine\map_parity.py` | fbcd95072c2a… | 5419 |
| jeron_engine/mbo_tape.py | MATCH | `K:\Databento_BackTesting\jeron_engine\mbo_tape.py` | 30db566a8413… | 6515 |
| jeron_engine/parity.py | MATCH | `K:\Databento_BackTesting\jeron_engine\parity.py` | 61a4433d9980… | 15386 |
| jeron_engine/phase_report.py | MATCH | `K:\Databento_BackTesting\jeron_engine\phase_report.py` | 79f2488aa6f0… | 8233 |
| jeron_engine/rules_plan.py | MATCH | `K:\Databento_BackTesting\jeron_engine\rules_plan.py` | bcddd6ce4d59… | 18053 |
| jeron_harness/build.py | MATCH | `K:\Databento_BackTesting\jeron_harness\build.py` | e48520f9fdbf… | 2133 |
| jeron_harness/driver/Harness.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\driver\Harness.cs` | f5d359c5686a… | 20128 |
| jeron_harness/stubs/NtCore.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\stubs\NtCore.cs` | 7965e1377f70… | 10843 |
| jeron_harness/stubs/NtGui.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\stubs\NtGui.cs` | 3af069a63656… | 18303 |
| jeron_harness/stubs/NtScript.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\stubs\NtScript.cs` | 80ede62527ab… | 13386 |
| jeron_harness/stubs/NtStrategy.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\stubs\NtStrategy.cs` | 20dcda79309e… | 10424 |
| jeron_harness/nt_source/JeronFlowShared.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\nt_source\JeronFlowShared.cs` | 1a531729a44f… | 23566 |
| jeron_harness/nt_source/JeronOrderFlowStrategy.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\nt_source\JeronOrderFlowStrategy.cs` | d8d2d5c83ba9… | 309757 |
| jeron_harness/nt_source/JeronPreopenMap.cs | MATCH | `K:\Databento_BackTesting\jeron_harness\nt_source\JeronPreopenMap.cs` | dbb4783f5cb5… | 128846 |
| data/gex_levels_block1.csv | MATCH | `K:\Databento_BackTesting\gex_levels_block1.csv` | c6c9649ed4ed… | 24060 |
| data/estimate_block1.csv | MATCH | `K:\Databento_BackTesting\raw\block1\estimate_block1.csv` | 07a1c524cf69… | 13623 |
| data/estimate_block1_l3.csv | MATCH | `K:\Databento_BackTesting\raw\block1\estimate_block1_l3.csv` | 44625a8f99d8… | 4546 |
| data/estimate_block1_roll.csv | MATCH | `K:\Databento_BackTesting\raw\block1\estimate_block1_roll.csv` | aa34e3aaeb08… | 966 |
| data/econ_calendar_2025-10_2026-04.csv | MATCH | `K:\Databento_BackTesting\econ_calendar_2025-10_2026-04.csv` | dc17c9bd9ea3… | 14045 |
| data/condition_NQ_MBO_2026-09.json | MATCH | `K:\Databento_BackTesting\NQ_MBO_2026-09\GLBX-20260928-6GPK57A3YJ\condition.json` | f88413fb300f… | 3242 |
| backtest/phase3/run_arms.py | MATCH | `K:\Databento_BackTesting\backtest\phase3\run_arms.py` | 60b833866029… | 10875 |
| backtest/phase3/build_inputs.py | MATCH | `K:\Databento_BackTesting\backtest\phase3\build_inputs.py` | 7e9774e2a3c7… | 3121 |
| backtest/phase3/final_combination.py | MATCH | `K:\Databento_BackTesting\backtest\phase3\final_combination.py` | bfec45430284… | 5729 |
| backtest/phase4/run_holdout.py | MATCH | `K:\Databento_BackTesting\backtest\phase4\run_holdout.py` | 8ff940043afb… | 8063 |
| backtest/phase4/build_inputs.py | MATCH | `K:\Databento_BackTesting\backtest\phase4\build_inputs.py` | 5e4483af7363… | 4763 |
| backtest/phase0_parity/phase0_data_integrity_2025-10-21_2026-10-02.csv | **MISSING** | `` | a39d79792049b8bcbbe18942f4c6066efb02ab79224090ff99bb6132f1b9633e |  |

Every DIFFERS / MISSING row above is a file whose Drive mirror is not the frozen tag's version. Report them to Kyron before P0.4; do not edit either side.

## Runner follow-up on the two MISSING rows (PC run, Nov 2, 2026)

The tool was run on the Book 1 working tree `K:\Databento_BackTesting` (branch `main`, HEAD `4cc698d`), not on a
checkout of the tag, so the Book 1 folder was not touched. HEAD is one commit after `phase4-result`; that commit
(`git diff --name-only phase4-result HEAD`) changes only 4 files under `backtest/research/c1_losers/` (a research
folder, not opened), none of them in the manifest. No tracked file is modified in the working tree. So every MATCH
above is also a match against the tag `phase4-result`.

| Manifest file | Finding | Effect |
|---|---|---|
| `backtest/phase0_parity/phase0_data_integrity_2025-10-21_2026-10-02.csv` | Present on the PC as `K:\Databento_BackTesting\data_integrity_2025-10-21_2026-10-02.csv`, sha256 `a39d7979…633e` = manifest | MATCH at a different path (path difference only) |
| `phase0_parity.py` | Not tracked in git (absent from the tag and from HEAD). Drive copy `Back TEST Chat_Claude\backtest_scripts\phase0_parity.py` sha256 `9a48104a…0103` = manifest. The PC copy `K:\Databento_BackTesting\backtest_scripts\phase0_parity.py` (Oct 24, 14:51) is an older version, sha256 `e9d982bd…c037`: it uses the CME roll dates (Dec 11, Mar 12) instead of NinjaTrader's (Dec 15, Mar 16) and lacks the Databento-degraded-day list | DIFFERS on the PC only; the tag has no copy. Book 1A does not import it (roll dates come from `book1a/sessions.py`). Kyron to decide whether the old PC copy should be replaced by the Drive version (not done: Book 1 frozen) |

Result: 0 code or config differences between `book1_ref` and the frozen tag; 1 stale untracked script on the PC.
