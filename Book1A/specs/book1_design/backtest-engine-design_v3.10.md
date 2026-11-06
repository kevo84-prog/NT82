<!-- exported 2026-11-01T20:17Z from Google Doc 1G9Sr-S5oWo-4oUsL4G7sBpKLa0FYMPUE, modifiedTime 2026-10-26T11:18:35.580Z -->
# Jeron backtest engine: design v3.10 (Oct 25, 2026)

Replaces design v3.9 (Oct 25), v3.8 (Oct 25), v3.7 (Oct 25), v3.6 (Oct 25), v3.5 (Oct 24), v3.4 (Oct 24), v3.3 (Oct 24), v3.2 (Oct 24), v3.1 (Oct 23), v3 (Oct 23) and v2 (Oct 13).

**What changed in v3.10** (Kyron, Oct 25, after the Phase 2 exit first look):
- **Fill model v3.5 frozen for Phase 3** (informed by Phase 2, frozen before Phase 3). Full text: `docs\fill-model-v3.5-proposal.md`; summary under "Fill model" below. Phase 3 uses it for A0 and every arm, and A0 is rerun under it for the pairing. Phases 0-2 results stay on v3.4. Three additions to v3.4:
  - A stop change submitted at a bar close goes active 250 ms later; the previous stop works until then.
  - **Crossed stop change, PRIMARY: reject and keep, with live-equivalent timing.** At the decision (the bar close) the strategy checks the current quote: if the new stop is already crossed (long bid <= new stop; short ask >= new stop), it does not submit, and the old stop stays. A submitted change that is crossed on arrival (250 ms later) is rejected, and the old stop stays. The old stop works throughout; a later condition may still move it. Chosen because it was named primary before the v2 results and is how a correctly built trailing stop behaves live, not because it scored better on Phase 2.
  - **REPORT-ONLY: market exit** on a change crossed on arrival (matches today's S1.4 handling of a rejected protective order: `IgnoreAllErrors` plus PROTECT_FLAT). Always reported beside the primary; it cannot be promoted or replace the primary after Phase 3 results are seen.
  - A working stop that price jumps through fills at the first traded price at or beyond it, plus slippage.
  - Code: `fills.simulate(gap_fill=True)` and `daily_loop` config `"fill_model": "v3.5"` for A0; `exit_replay` with `gap_fill=True, stop_delay_ms=250, crossed="live"` for stop-moving models. Both give the same A0 on Phase 2 (105 of 105 trade-cases).
- **Live condition:** if a stop-moving exit model passes Phase 3, the live strategy must check the bid / ask before each stop move and not submit a crossed move, and a rejected stop CHANGE must keep the old stop. Only a rejected protective ORDER flattens (today's PROTECT_FLAT). Built and tested on Sim before any live use. S1.4 today never moves a stop after entry.
- **Promotion meaning** (added to the promotion rule): passing Phase 3 shows improvement over A0 under the registered tests. It does not show profitability or authorize live trading. Combinations go through the final-combination replay, and live use needs the Phase 4 holdout.
- **Exit replay engine built (step 9):** `jeron_engine\exit_replay.py`. Gate passed: M0 under v3.4 reproduces A0's 35 Phase 2 trades exactly at 1, 2 and 4 ticks (105 of 105).
- **Phase 2 exit first look** (Phase 2 first look, not promotion evidence; tags `phase2-exit-first-look`, `-v2`):
  - A0 under v3.5: -6.55 R.
  - M2E (v3.5 as frozen, live-equivalent timing; exit first look v3): -1.97 R, +0.218 R per session. Of 49 stop moves triggered, 26 were not submitted (crossed at the decision), 2 were rejected on arrival, 21 applied. (v2, arrival check only: -2.45 R, +0.195 R per session.)
  - M2E report-only line (same decision check, market exit on arrival = today's PROTECT_FLAT): -3.46 R, +0.147 R per session; cost of keeping today's rejected-change handling: +1.49 R (superseded v2 figure, market exit on every crossed change: -4.34 R). Under v3.4, M2E showed +1.39 R, mostly from filling stops the market had already passed.
  - M2: -8.20 R (gap-aware); the runner reached TP2 once.
  - M1 fires on 10 trades (-7.71 R gap-aware), not 4.
- **Bug fixed:** `change_list_checks.py` added 1 tick to each trade's risk (A0 -6.44 R vs the report card's -6.50 R). Logged in `backtest\bug_log.md`.

**What changed in v3.9** (Kyron, Oct 25, late):
- **Phase 1 passed.** The 3 hand-check days were checked against Databento's exchange-built NQ 1-minute bars (`chart_check.py`): 115 of 115 levels, entries, 15-bar outcomes and fills agree. RESPONSE entries sit at the confirmation bar's close, as the CONFIRM rows say.
- **Phase 2 baseline run** (Nov 5 – Dec 4, 2025, 21 sessions, no rule changes; see the Phase 2 folder).
  - A0: 15 APPROVED days, 35 trades, 9 wins, −6.5 R (base fills), max drawdown 12.3 R.
  - 30 of the 35 trades are 08:30–09:30.
  - Half-day check (gate 4) passed.
  - Chart check: 762 of 763 agree.
- **Rules-only plan bug fixed in Phase 2** (implementation vs the frozen definition, not a rule change). Check A now fails only on a data gap in the last 24 h, as the prompt says; the first version failed on any gap still listed in the packet. The Nov 28, 2025 CME outage (Nov 27 20:44 – Nov 28 07:30 CT) had made Dec 1–4 LOG_ONLY. Phase 1 plans are unchanged by the fix.
- **New reports:**
  - `phase_report.py`: A0 report card, by-blocking-rule, half-day check.
  - `chart_check.py`
  - `gex_overlap.py`: GEX levels vs plan zones, logged only.
- **GEX vs zones** (31 sessions): 57% of replica GEX levels within 1 ADR sit inside or within 10 points of a plan zone, against 38% by chance. HVL is closest (median 3.5 points). Whether that overlap adds anything is a candidate pre-registered arm for the Phase 3 change list. Jeron's July 31, 2026 recap ("Gamma Levels Explained") puts end-of-day gamma levels second in his order of operations and grades a zone A+ when they stack on it.

**What changed in v3.8** (Kyron, Oct 25, night):
- **Phase 0 closed.** Kyron's decisions:
  - Settlement keeps the exchange (CME) clock. Parity allows settlement-derived levels within 4 ticks of NT.
  - Fill model entry latency: 250 ms base case, 1,000 ms reported as the stress case.
  - The v3.4 defaults are confirmed (promotion rule, holdout rule, 1-tick-through targets).
  - The gate 2 pass rule is accepted.
- **Phase 1 run** (Oct 22 – Nov 4, 2025; see the Phase 1 folder). The daily loop is `jeron_engine.daily_loop`: map at 08:10 (MAP0) → rules-only plan → S1.4 (A0) → v3.4 fill model with stress cases → day sheets, row-type list, C1/C2 audits.
- **Rules-only plan: two bugs fixed in Phase 1** (allowed: Phase 1 is debug days).
  - Check C counts only TARGET zones as "the nearest target".
  - Invalidation uses only the decision zones on each side of price.
  - The "crossed both ways in the last day" test uses the packet's 1-hour bars of the last 24 h.
- **Harness inputs for the full defaults.**
  - The map gets 100 days of NQ 1-minute bars for the HTF composite.
  - It gets a Volumetric BidAsk series built from the MBO aggressor flag (delta profile).
  - It gets ES 1-minute bars. The strategy gets ES 1-minute bars too: its ES gate is now fed, and is log-only.
  - With NT's own Oct 8 ES, gate 1 is unchanged: 18 / 7-8-3 / +1063.
- **Lookback days** (map history before the first MBO file) come from the Databento trades schema. It has no book, so bid/ask there are set from the aggressor flag.

**What changed in v3.7** (Kyron, Oct 25, evening):
- **Gate 2 passed** (proposed rule, see Phase 0). The same S1.4 code was run on a Databento MBO tape and on NT's own run of Sep 28. 551 of NT's 558 candidates matched. Their status agrees on 550, and the delta is identical on 530 (median difference 0). Sep 28 had no plan, so the Qualified lists are empty on both sides.
- **Gate 3 run.** Map v2.3 was run on Databento NQ ticks plus NinjaTrader's own ES trades (from JeronTapeExporter). It matches NT's packets exactly on Sep 28, 29 and 30 and Oct 1, ES block included. On Oct 2 the ES block is identical and one level differs: PD settlement is 3 ticks off (NQ feed timing at the close), which moves one zone edge. **ES bar rule:** NinjaTrader closes an ES 1-minute bar only when the next ES trade arrives. The map harness models this with each bar's `release_local`.
- **Gate 3 code parity proven (Oct 25):** with NinjaTrader's own NQ and ES trades (JeronTapeExporter, Sep 23 – Oct 2) the map reproduces all 5 NT packets exactly. The Oct 2 settlement difference is the data alone. NT's and Databento's clocks agree within milliseconds during the afternoon, but in the 15:00 burst NT stamps trades 0.5–2 s late. On Oct 1 its 30-second settlement window held 7,074 contracts vs 7,558 on the exchange clock.
- **Known data difference: NT's timestamps around the 15:00 close.** They run behind CME's by about 0.1 s on Sep 28 and possibly more on Oct 1. This shifts trades between the 15:00 and 15:01 bars and moves the map's settlement (VWAP of the 30 s before 15:00). It comes from the data feed, not the code. Kyron decides whether settlement-derived levels get a tolerance (proposed: 4 ticks).
- **Gate 5 run (Oct 25)** on an NT S1.4 Playback run of Oct 8 (15 trades). **Exits pass:** all 15 are within 1 tick and have the same exit type. NT Sim fills stops at the stop price, so the model's 1-tick stop slippage is 1 tick conservative. Targets match exactly. **Entries do not pass at 250 ms:** only 5 of 15 are within 1 tick, with a maximum of 14 ticks. NT Playback filled market entries about 1 s after the bar closed, stamped on the next whole second. At 1,000 ms the model matches 12 of 15 (max 3 ticks). The differences go both ways: day total NT +549, model +557. Open decision: entry latency base case. Live DEMO Sim fills settle it.
- **Databento → harness tape** (`mbo_tape.py`): one row per CME trade record with the pre-event best bid/ask and the aggressor flag.
- **Map driver** (`JeronHarness --map`). The map's 1-tick series and 1-minute chart bars run in NT's order. ES 1-minute bars are fed in time order, with the tick series first when timestamps are equal.

**What changed in v3.6** (Kyron, Oct 25):
- **The engine runs the real C#, not a Python port.** Kyron chose this on Oct 25. JeronOrderFlowStrategy S1.4, JeronFlowShared and JeronPreopenMap v2.3 are compiled as they are in NinjaTrader, against NinjaTrader stand-ins (`jeron_harness`, Mono / .NET). Python does the rest: data, plans, arms, fills and reports. The only changes to the NT files are removing the NinjaScript generated-code block and adding the `JeronContextBias` enum (it lives in the tracker file). This removes porting error as a cause of any difference from NinjaTrader.
- **Parity gate 1 passed (Oct 25).** The tape was NT's own Oct 7–8 tick export (`OCT8_Tick Data.zip`, Preopen Exchange folder) with plan 2026-10-08-v1, plus `review=APPROVED` and `end=1`, which S1.4 requires. Result: 18 Qualified signals, 7 / 8 / 3, +1063. Every signal matches NT on time, side, entry, stop, target and 15-bar result. The result is the same with the S1.4 flags on and with the S1.4 default grades. To the session end it is 8 / 10, +1025. See `Phase 0 - Parity/phase0_gate1_oct8_tracker_parity.csv`.
- **Bar rule found by the gate:** NinjaTrader puts a tick stamped exactly hh:mm:00.000 in the **next** 1-minute bar. Putting it in the closing bar moved two closes by a tick.
- JeronTapeExporter is no longer needed for gate 1. It is still useful for exact event order and ES ticks.

**What changed in v3.5** (Kyron, Oct 24):
- **Roll dates follow NinjaTrader, not the CME calendar.** NinjaTrader's own database on Kyron's PC rolls NQ on **Dec 15, 2025** (Dec 25 → Mar 26) and **Mar 16, 2026** (Mar 26 → Jun 26); also Sep 15, 2025, Jun 12, 2026 and Sep 14, 2026. v3.4's Dec 11 / Mar 12 are withdrawn. See Contract and roll.
- **Roll-day data replaced.** Databento's continuous symbol switched two trading days after NinjaTrader each time (Dec 17, Mar 18, Sep 16), so those days were bought again for the contract NinjaTrader was on (see Data).
- **Data status updated:** GEX options data, roll-day files and the L2 feature files are on disk; Databento's degraded days are listed.
- **NinjaTrader settings confirmed (Oct 24):** global merge policy **Merge non back adjusted**, so history across a roll is **not** back-adjusted (see Contract and roll). **Commission baseline $2.87 per contract per side** (NinjaTrader Free pricing), i.e. $5.74 per round turn = 1.148 NQ ticks.
- **Parity gate 6 passed (Oct 24):** `data_integrity.py` checked all 161 weekday MBO files (Block 1, roll files, Sep 2026). See "Data integrity result". **Half days:** the cash session ends at 12:00 CT and CME futures trade until 12:15 CT (confirmed by the timestamps and the calendar file). The map's `HalfDayDates` stay 2025-11-28@12:00 and 2025-12-24@12:00, because the map works on the cash session.
- **Economic calendar spot-checked and copied (Oct 24):** jobs, CPI and PPI dates match the BLS shutdown-revised schedule and the BLS Mar/Apr 2026 calendars; FOMC dates match the Fed calendar. Roll rows moved to NinjaTrader's dates (Dec 15, Mar 16). File: `K:\Databento_BackTesting\econ_calendar_2025-10_2026-04.csv`.
- **Replica GEX computed for all 124 Block 1 sessions (Oct 24):** `gex_block1.py` → `gex_levels_block1.csv`. See GEX.

**What changed in v3.4** (from the external review of v3.3; the numbers are proposed defaults Kyron can change before Phase 1):
- **Fill model:** buys fill at the ask and sells at the bid, 250 ms after the bar closes; targets fill only when price trades 1 tick through; stop slippage is stress-tested at 1, 2 and 4 ticks. Fixed before Phase 1.
- **Labels:** a trade flattened at 14:55 is now TIME_EXIT with its real net R. A same-tick tie between stop and target counts as a stop. UNKNOWN is only for missing data.
- **Each arm replays the day:** candidate selection, confirmation, position state and daily limits are rerun per arm from the full candidate pool, shadows included. Exit models do the same before promotion.
- **Promotion rule in numbers:** paired net R per session vs A0, session-bootstrap 90% lower bound above 0, max drawdown no worse than 1.25× A0's, at least 20 trades that differ from A0. Otherwise "insufficient evidence" and A0 stays.
- ~~**Contract and roll:** front month by the CME roll date (Dec 11, 2025 and Mar 12, 2026)~~ Superseded in v3.5 by NinjaTrader's roll dates. History across a roll is back-adjusted to match NinjaTrader's merge setting, confirmed in Phase 0.
- **Final combination replayed** in Phase 3 before it is frozen.
- **XGBoost is exploratory only.** It plays no part in any Phase 4 decision.
- **Partials:** M2 and M3 also run with 2 contracts (1 off at TP1, 1 runner), the version that can actually be traded.
- **Phase wording:** Phases 2–3 are development and selection; Phase 4 is the only independent test. Phase 5 has a strict failure rule, Sep–Oct 2026 is a consistency check only, and the untouched part of Block 2 is Apr 22 – Aug 31, 2026.
- **Data checks:** Phase 0 checks timestamps, instrument IDs, gaps and decode errors, not just file counts. The economic calendar is now in the Drive folder (`econ_calendar_2025-10_2026-04.csv`). It lists MLK Day and Presidents' Day as no cash session, so Block 1 has 124 sessions (Phase 3 = 41, Phase 4 = 52).
- Wording fixes: features are known at or before **entry** time (A4 enters at the follow-through bar); the "close to break-even" line on weak delta is withdrawn until the payoff data exists.

**What changed in v3.3:**
- **Phase plan replaces the 20 / 65 / 37 split.** Block 1 runs in growing phases, each on days the earlier phases never saw: Phase 0 parity (2 known days), Phase 1 shakedown (2 weeks), Phase 2 first baseline (1 month), Phase 3 test changes (2 months), Phase 4 holdout (2½ months, run once), Phase 5 extra checks (Sep 2026, then Block 2). Each phase has a start condition, a run list, deliverables and a pass test. See the Phase plan section.
- The old split left Feb 25–27, 2026 in no part; the phase plan covers every Block 1 session.
- The holdout grows from about 37 to 53 sessions.
- **Data on disk checked (Oct 24):** the Block 1 MBO files are complete (157 daily files, no weekday missing). Holiday and half-day dates were read from the file sizes.

**What changed in v3.2:**
- **Scope rule:** every item in the three source files (strategy S1.4, map v2.3, prompt v1.5) is in the backtest. Each one is either replayed as a trading rule, reproduced as a logged column or row, decided in the plan step, or listed as excluded with the reason. The full list is in Appendices A–C.
- **Ports the new builds:**
  - Strategy S1.4: grades A+,B+,B by default, plus four logging-only flags (passive trap, relative delta, reversal after a stop-out, fight).
  - Map v2.3: half days, 3-month HTF composite from 1-minute bars, PD2 + PD + ON balance merge, time per visit, double distribution, PD2/PD3 highs and lows, settlement-family option.
- **Gate experiment:**
  - Thresholds are settled: A1 = 75 delta, A2 = 5%.
  - **B1 is withdrawn.** In the code the trapped-side gate only applies to RESPONSE candidates, so waiving it for continuations (INITIATION) changes nothing.
  - Secondary arms **A4–A8** are pre-registered: context-scaled proof, passive trap, EMA/CVD alignment, fight veto, relative delta.
- **Exit models M0–M3**, simulated on the same entries: Jeron's partials, break-even and trailing stop, plus exit on the second opposing effort zone.
- **New reports:** reversal after a stop-out, grade C, map variants.
- **Rules-only plan:** the algorithm is now written out, so it is frozen before the Phase 2 baseline.

## What is tested (the NinjaTrader C# itself, run in the harness; v3.6)

| Piece | Source file | Notes |
|---|---|---|
| Strategy | JeronOrderFlowStrategy.cs **S1.4** | Contains tracker v2.11 unchanged. Adds the trading layer and the S1.4 research flags. |
| Pre-open map | JeronPreopenMap.cs **v2.3** | As-of 08:10 CT (now also the file default). |
| Large-trade engine | JeronFlowShared.cs | Aggressor side, Consistent Bid/Ask clusters, time clusters, tiers, session clock. |
| Plan rules | jeron-preopen-review-prompt-v1.5.md | Questions, zone picking, zone review (checks A–F). GEX steps are replaced by the replica (below). |

Settings are the strategy defaults:

| Setting | Default |
|---|---|
| Max trades per day | 3 (also reported at 2) |
| Max daily loss | 400 ticks |
| Max consecutive losses | 2 (halt) |
| Last entry | 14:30 CT |
| Flatten | 14:55 CT |
| **Grades allowed** | **A+, B+, B** (S1.4). A "with C" run is reported as a sensitivity check, G-ALL. |
| Max entry slippage | 12 ticks |
| ES gate | log-only |
| L2 alignment | off |
| Exit on first exit warning | off (tested as exit model M1a) |
| S1.4 research flags | on (logging only) |

## Data (Kyron's PC, `K:\Databento_BackTesting`)

| What | Used for |
|---|---|
| NQ MBO (L3) | Every trade with the exchange aggressor flag, and the quote at each trade. Replaces NT's tick series and the Volumetric footprint. |
| NQ trades, lookback period | The map's history: weekly, prior-week, composite, ADR. **1-minute bars are built from these trades for the HTF composite** (map v2.3, 100 calendar days back). |
| ES 1-minute bars | The map's ES cross-check and the strategy's ES gate. |
| NQ options definition + statistics, NQ.FUT statistics | Replica GEX levels. |
| L2 features rebuilt from L3 (`l2_features.py`, `l2_features\mbo\`) | L2 columns, research only. Not used in any arm. See l2-features-from-l3.md. |
| Economic calendar file (`econ_calendar_2025-10_2026-04.csv`) | Check F of the zone review (`no_trade`, FOMC, earnings, roll days). |
| CME holiday and half-day list | Map `HolidayDates` / `HalfDayDates` for each date in the range. |

**On disk (checked Oct 24, 2026, `K:\Databento_BackTesting\raw\block1`):**

| Data | Range | Files | Notes |
|---|---|---|---|
| NQ MBO | Oct 21, 2025 – Apr 21, 2026 (UTC days) | 157 (44 GB) | No weekday missing. Oct 21 holds the first session's overnight. Continuous NQ.v.0: on the roll days below, use the roll files instead. |
| NQ trades (lookback) | Jul 20 – Oct 20, 2025 | 83 | History before the first session. Sep 15–16, 2025: use the roll file. |
| NQ, ES, ZN, CL 1-minute and daily bars; NQ and ES futures definitions and statistics | Jul 20, 2025 – Apr 21, 2026 | 239–240 each | About 64 trading days of history before Oct 22, enough for the 60-day HTF composite. |
| **Roll-day replacements (v3.5)** | see Contract and roll | `nq_roll_*`, `roll_*` | NQH6 MBO Dec 14–16, 2025; NQM6 MBO Mar 15–17, 2026; NQZ6 MBO Sep 13–15, 2026; NQZ5 trades Sep 14–16, 2025; NQ and ES 1-minute bars for the same windows (UTC days, incl. the Sunday open). |
| NQ options (NQ, QN1–QN4, QNE) definitions and statistics | Oct 20, 2025 – Apr 21, 2026 | 154–161 each | Complete. |
| Weekly options Q1A–Q5D | Oct 20, 2025 – Apr 21, 2026 | 41–157 each | Gaps are normal for weeklies. Q5B ends Jan 30 and Q5D ends Feb 27, 2026: check the replica does not need them later. QN5 has no listings. |
| NQ MBO, owned earlier | Sep 1 – Oct 4, 2026 | 29 | Phase 5 extra check (23 sessions). Sep 14–15: roll files. |
| L2 features (1 row per second, 08:00–15:15 CT) | every MBO weekday above | 153 + roll days | Rebuilt Oct 24 with full prices; roll days from the roll files. |
| Economic calendar | Oct 23, 2025 – Apr 21, 2026 | 1 | In the Back TEST Chat_Claude Drive folder (added Oct 24). Copy to `K:\Databento_BackTesting`. Contents are spot-checked against the official sources it cites before Phase 1. |
| Not on disk | Block 2 (Apr 22, 2026 to now, about 129 sessions) | — | Bought before Phase 5, with the Jun 12, 2026 roll fix. |

**Small MBO files (holidays and short sessions):** Dec 25 and Jan 1 (2 MB, closed); Apr 3, Good Friday (23 MB); Nov 27, Thanksgiving (38 MB); Nov 28 and Dec 24 (64–72 MB, half days); Feb 16, Presidents' Day (83 MB) and Jan 19, MLK Day (113 MB). The calendar file lists Jan 19 and Feb 16 as holidays with no cash session (CME equity futures halt at 12:00 CT). File sizes are only a screen: Phase 0 confirms each of these days from the timestamps in the files.

**Databento "degraded" days (v3.5):** trading dates **Nov 28, 2025, Mar 16, 2026 and Apr 10, 2026** (also the weekend dates Jan 31, Mar 15 and Mar 21). The integrity check found no gap in any of them (Mar 16 and Apr 10: longest pause in book updates 1 s, in trades 5–7 s), so they are **used**, and flagged `data_quality_flag=DATABENTO_DEGRADED` in every report.

### Data integrity result (parity gate 6, Oct 24 2026)

`data_integrity.py` → `K:\Databento_BackTesting\data_integrity_2025-10-21_2026-10-02.csv` (one row per file; `used_by_backtest` marks the file each date uses).
- **161 weekday MBO files, 0 decode errors.** 155 dates; on every date the file the backtest uses holds **only the contract NinjaTrader was on** (roll days from the roll files).
- **Block 1 (Oct 22, 2025 – Apr 21, 2026): 130 weekday dates = 122 normal + 2 half days (124 sessions) + 3 holiday halts + 3 closed.**
  - Normal days: longest pause in book updates 2 s, in trades 9 s, during 08:30–15:00 CT; lowest volume 193,624 (Dec 26).
  - Half days: cash session to **12:00 CT**, futures trading to 12:15 CT: Nov 28, 2025 and Dec 24, 2025.
  - Holiday halts, trading stops at **12:00 CT**, no cash session: Nov 27, 2025 (Thanksgiving), Jan 19, 2026 (MLK Day), Feb 16, 2026 (Presidents' Day). Also Sep 7, 2026 (Labor Day).
  - Closed: Dec 25, 2025, Jan 1, 2026, Apr 3, 2026 (Good Friday).
- These session types come from the timestamps, so they replace the file-size screen below.

## GEX: replica only (unchanged from v3.1; computed Oct 24, v3.5)

- **Computed for all 124 Block 1 sessions:** `K:\Databento_BackTesting\gex_levels_block1.csv`, by `gex_block1.py` (the tested `mq_levels.compute_levels` and `gex_calc.cme_day`, unchanged; only the file reading is new). 124 / 124 OK; 68 positive-gamma and 56 negative-gamma sessions.
- **Front contract** = highest CME cleared volume among figures **published before 11 PM ET on D** (each contract's latest non-zero figure). CME publishes D's own volume the next morning, after the 08:10 pre-open, so using it would be look-ahead. The GEX front therefore switches on Dec 17, 2025 and Mar 18, 2026.
- **Chart-contract columns (`*_nt`):** on Dec 15–16, 2025 and Mar 16–17, 2026 NinjaTrader is already on the new contract, so every level is also given shifted by the settlement spread on D (+256.0, +249.5, +211.5, +215.5 points). The engine uses the `_nt` columns for confluence with the chart.
- **0DTE levels** are blank on Dec 17–18, 2025 and Mar 18–19, 2026: right after the switch, the options expiring the next session are on the old contract.
- Levels from `mq_levels.compute_levels()` (method in gex-menthorq-replication.md); day D uses report date D-1.
- The code writes `gex_model=MQ_REPLICA`, `gex_source=EOD_PRIOR`, `gex_regime`, `mq_call_resistance`, `mq_put_support`, `mq_hvl` and the 0DTE levels into both plans after the plan step, so Claude never sees them.
- Logged only. GEX never moves a zone, changes a side rule or changes the review decision.

## Daily loop (every backtest date)

| Step | What | Output |
|---|---|---|
| 1 | Load the day's MBO trades and quotes, plus history from the cache | Parquet per day |
| 2 | Map v2.3 at 08:10 CT, from earlier data only. Map variants for the comparison run on the rules-only plan only (see Map variants). | `PreopenPacket_<day>.json` |
| 3 | Replica GEX from report date D-1 | `GexLevels_<day>.json` |
| 4 | Two plans: **rules-only** (code, algorithm below) and **blinded Claude** (dates hidden, prices shifted, no web) | `PreopenPlan_<day>_{rules,claude}.txt` |
| 5 | Add the GEX lines to both plans | Same files |
| 6 | Run the strategy (tracker v2.11 rules + S1.4 flags + trading layer) bar by bar, with fills on ticks | Trade ledger + JOFS-style log (every row type) |
| 7 | **Candidate outcomes:** every candidate, whatever its status, gets a tick-based outcome from its own entry, stop and target. The pool is kept **before** the one-per-bar ranking, shadows included. | `Candidates_<day>.parquet` |
| 8 | Gate-experiment arms A0–A8: each arm reruns candidate selection, confirmation, position state and daily limits on the full pool | `Arms_<day>.parquet` |
| 9 | Exit models M0–M3: first on the entries of A0 and of each arm (diagnosis), then as a full replay for any model put forward for promotion | `Exits_<day>.parquet` |
| 10 | Report | See Reports |

## Plan step in the backtest

- **No macro note** exists for past days, by design.
  - The plan writes `macro=not verified (backtest)`.
  - Check F uses the economic calendar file instead.
  - The rule "macro note missing and context None → LOG_ONLY" becomes "calendar missing and context None → LOG_ONLY".
- **Validation:** plans are schema-checked. On failure, retry; then fall back to the rules-only plan.
- **Shifting:** the Claude plan is un-shifted before the strategy runs.
- **Timing:** both plans are treated as written by 08:20 CT. PLAN_LOADED_LATE, PLAN_WAITING and replacement plans (`-v2`) are live-only and not simulated.

### Rules-only plan (frozen definition, v3.2)

Every threshold here is ours. It is written down now and not changed after any phase's results are read.

1. **Context**, from the packet:
   - **Bullish:** `value_migration` PD_vs_PD2 is HIGHER or HIGHER_NO_OVERLAP, and price is ABOVE_VALUE or INSIDE_VALUE of PD, and `h1_trend` ≠ DOWN.
   - **Bearish:** the mirror of Bullish.
   - **Balanced:** otherwise, if `balance_composite.overlapping` = true.
   - **None:** everything else.
2. **Decision zones:** the packet's DECISION zones, at most 2 per side of price, the nearest within 1 × `ranges.adr_full`. Neighbours that touch are merged. Zones wider than 60 points are cut back to the levels nearest the middle.
3. **Side rules:**
   - With-context side = ANY; counter-context side = INITIATION; Balanced or None = ANY on both sides.
   - A zone with 4+ tests whose `lower_highs_into_zone` / `higher_lows_into_zone` is true, or whose `shrinking_time` is true: the side that would respond off it gets NONE, and the side breaking through it gets INITIATION.
   - A zone crossed both ways in the last day: NONE on both sides.
4. **Targets:** every non-decision zone of the packet becomes a TARGET, with at least one on each side. If a side has none, use the nearest `structure.daily` high or low.
5. **Balance:** `balance=` and `balance_poc=` from `balance_composite` when it is overlapping; otherwise no balance line. **Lava** = the middle third of the balance, only if it stays 15+ points clear of every decision zone.
6. **Invalidation:** 2 ticks beyond the outermost decision zone on each side; the new context is Balanced.
7. **ES gates:** the ES PD cash high (longs above) and the ES PD cash low (shorts below), from the packet. Logged only.
8. **Zone review:** checks A–F exactly as the prompt (Appendix C), with the calendar file standing in for the macro note.

## Fill model (on real ticks, v3.4)

Fixed before Phase 1, because the shakedown is where it is tested.

- **Entry:** market order sent when the signal bar closes, filled after a **250 ms** delay.
  - Buys fill at the best **ask** and sells at the best **bid** from the MBO book at that moment. This is also how the NinjaTrader simulator fills market orders.
  - Initiations use the trigger bar; responses use the confirmation bar; A4 counter-context entries use the follow-through bar.
  - PRICE_PAST_STOP, PRICE_PAST_TARGET and ENTRY_SLIPPAGE (12 ticks) are checked against that fill price.
  - Latency sensitivity: 0 ms and 1,000 ms are also reported.
- **Target (limit order):** fills only when price trades **1 tick through** the target. A touch alone is not a fill.
- **Stop (stop-market):** fills at the stop price plus slippage. Base case 1 tick; stress tests at **2 and 4 ticks** are reported for every arm and exit model.
- **Costs:** commission **$2.87 per contract per side** (baseline, NinjaTrader Free pricing; $5.74 round turn = 1.148 NQ ticks at $5 per tick) is included in every net R. A 2-contract exit model pays it on both contracts.
- **Same-tick tie:** if the stop and the target are both reached at the same MBO timestamp, it counts as a **stop**. This is conservative and matches the tracker's "same bar = stop".
- **Other rules:** one position at a time; flatten at 14:55 CT; the session-close exit after 15:00 CT.
- **Two results per trade:** the strategy fill result, and the tracker OUTCOME row (bar-based, entry at the bar close), kept so the two can be compared, as live.

### Fill model v3.5 (Phase 3 onward; informed by Phase 2, frozen before Phase 3; v3.10)

Everything above still applies, plus (full text `docs\fill-model-v3.5-proposal.md`):
- **Stop-change delay:** a moved stop goes active **250 ms** after the bar close that triggers it. The previous stop works until then.
- **Crossed stop change (primary: reject and keep):** at the bar close the strategy checks the quote and does **not submit** a change that is already crossed (long bid <= new stop; short ask >= new stop); a submitted change that is crossed on arrival 250 ms later is **rejected**. Either way the old stop stays and works throughout. The **market exit** on a change crossed on arrival is reported beside it, report-only.
- **Gap fill:** a working stop (fixed or moved) fills at the **first traded price at or beyond the stop**, plus slippage. When that trade is at the stop, this equals v3.4.
- A0 is rerun under v3.5 so every Phase 3 pairing uses one fill model.

### Contract and roll (v3.5)

- **Traded contract:** the contract NinjaTrader is on, switching on **NinjaTrader's rollover dates** (read from its database on Kyron's PC, Oct 24 2026):

| NinjaTrader rolls to | On | Databento NQ.v.0 switched | Days replaced from roll files |
|---|---|---|---|
| NQ Dec 25 (NQZ5) | Sep 15, 2025 | Sep 17, 2025 | Sep 15–16, 2025 (lookback trades and bars) |
| NQ Mar 26 (NQH6) | **Dec 15, 2025** | Dec 17, 2025 | Dec 15–16, 2025 |
| NQ Jun 26 (NQM6) | **Mar 16, 2026** | Mar 18, 2026 | Mar 16–17, 2026 |
| NQ Sep 26 (NQU6) | Jun 12, 2026 | not checked yet | Block 2: buy before Phase 5 |
| NQ Dec 26 (NQZ6) | Sep 14, 2026 | Sep 16, 2026 | Sep 14–15, 2026 |

- Every row carries `contract`. The engine uses the explicit contract for each date, never the continuous symbol: on the days in the last column it reads the `nq_roll_*` / `roll_*` files.
- Roll-week volume is split between the two contracts, so the new contract's first days are lighter than normal (e.g. Mar 16 about 200k, Mar 17 about 255k RTH contracts vs about 400k).
- **History across a roll: not back-adjusted, as NinjaTrader.** Kyron's global merge policy (Tools → Options → Market data) is **Merge non back adjusted**, and the NQ instrument uses the global setting. So, as on her chart, the map's prior-day, weekly, composite and ADR history before the roll date comes from the old contract's own prices, joined to the new contract's prices from the roll date on, with no shift. After a roll the older levels therefore sit about 200–260 points off the new contract's price (the spread on Dec 15, 2025 and Mar 16, 2026). This is reproduced exactly for parity; packets on the first days after a roll get `notes: ROLL_UNADJUSTED_HISTORY`, and those days are already LOG_ONLY on the roll date itself.
- **Roll days** (Dec 15, 2025 and Mar 16, 2026 in Block 1) are LOG_ONLY (check F), as in the prompt.

## Parity gates (before any multi-month number counts)

1. **Oct 8 tracker parity. PASSED Oct 25 (v3.6).** Feed NT's Oct 8 ticks (tick export or JeronTapeExporter tape) into the harness.
   - With grades A+,B+,B,C and the S1.4 flags off, it must reproduce the NT log: 18 signals, 7/8/3, +1063.
   - S1.4 adds no gate, so turning the flags on must leave that result unchanged.
2. **Databento vs NT data (Sep 28). PASSED Oct 25 (v3.7), proposed rule.** The candidate list must match the NT run closely. Compare delta and delta % per candidate, and now also `trapped_passive`, `delta_pct_vs_session` and `fight_flag`. A systematic difference is a bug to fix before the baseline, not a threshold to tune.
3. **Map parity. PASSED Oct 25 (v3.7) on NinjaTrader's own NQ + ES trades (all 5 packets identical). On Databento NQ, Oct 2 PD settlement is 3 ticks off: NT's trade times lag CME's by 0.5–2 s in the 15:00 settlement burst.** Packets for 2–3 recent days must match NT's own map v2.3 packets: levels within a tick, the same zones, and the same `balance_composite`, `double_distribution` and `zones[].tests`.
   - The HTF composite from Databento 1-minute bars must match the NT `MINUTE_APPROX` levels within one HVN row (5 points).
4. **Half-day check. PASSED Oct 25 (v3.9); the Nov 28 CME outage gap is logged as a real gap.** For Nov 28 2025 (half day) and Dec 1 2025 (the Monday after), the map must keep PD, the weekly profile and the prior-week profile, with no data gap logged after the early close.
5. **Fill parity (v3.4). Run Oct 25 on NT Playback: exits pass (15/15 within 1 tick); entries fail at 250 ms because Playback fills about 1 s after the bar (12/15 within 1 tick at 1,000 ms).** On Oct 8, the bid/ask fill model must match NinjaTrader Sim fills of the same trades within 1 tick.
6. **Data integrity (v3.4).** For every Block 1 MBO file, roll files included: instrument IDs (which contracts are present), first and last timestamps, gaps over 60 seconds inside the 08:30–15:00 CT session, and decode errors. File counts and sizes alone don't prove completeness. Also decides the degraded days.

## Phase plan (Block 1: Oct 22, 2025 – Apr 21, 2026, 124 sessions incl. half days)

Each phase runs on new days. **Phases 2 and 3 are development and selection:** Phase 3 picks the winners, so its numbers are selection results, not proof. **Phase 4 is the only independent test** of the frozen strategy. Earlier days can be rerun with a change for reference, but they never decide it. Session counts exclude Thanksgiving, Christmas, New Year's Day, MLK Day, Presidents' Day and Good Friday (no cash session per the calendar file; confirmed from the MBO timestamps in Phase 0), and include the two half days.

| Phase | Days | Sessions | Purpose | Pass test to move on |
|---|---|---|---|---|
| **0. Parity** (closed Oct 25) | Oct 8 and Sep 28, 2026 (owned), plus 2–3 recent map days | 2 + map days | The engine (NT C# in the harness) reproduces NinjaTrader before any Block 1 run | Parity gates 1–3, 5 and 6 pass (gate 5: exits; entry latency decided) |
| **1. Shakedown (2 weeks)** (passed Oct 25) | Oct 22 – Nov 4, 2025 | 10 | Mechanics only: packets, plans, every log row, fills | No unexplained rows; bugs fixed; profit/loss ignored |
| **2. First baseline (1 month)** (A0 run Oct 25) | Nov 5 – Dec 4, 2025 | 21 | What passes, what fails and why | Written change list, declared before Phase 3 |
| **3. Test changes (2 months)** | Dec 5, 2025 – Feb 4, 2026 | 41 | Gate arms, exit models and map variants on fresh days | Changes that pass the promotion rule, replayed together, are frozen |
| **4. Holdout (2½ months)** | Feb 5 – Apr 21, 2026 | 52 | The frozen strategy, run once | Passes the holdout rule; this is the result to trust |
| **5. Extra checks** | Apr 22 – Aug 31, 2026 (Block 2, untouched); Sep 1 – Oct 2, 2026 (consistency only) | about 91 + 23 | Newer market conditions | Passes the same rule as the holdout; no explaining away |

### Phase 0. Parity

- **Starts when:** the harness runs strategy S1.4 and map v2.3 (strategy done Oct 25; map driver next).
- **Runs:** parity gates 1–3 (Oct 8 tape, Sep 28 Databento vs NT, map packets), gate 5 (fill parity) and gate 6 (data integrity of every Block 1 file). Confirms from the timestamps that Jan 19 and Feb 16, 2026 had no cash session. Confirms NinjaTrader's contract merge setting.
- **Delivers:** a parity report (signal counts, outcomes, per-candidate delta differences, packet level differences, fill differences) and a data-integrity table per file.
- **Pass:** gates 1–3, 5 and 6 pass. A systematic difference is fixed in code, never absorbed by changing a threshold.

### Phase 1. Shakedown (Oct 22 – Nov 4, 2025, 10 sessions)

- **Starts when:** Phase 0 passes, the v3.4 fill model and labels are coded, and the economic calendar is spot-checked.
- **Runs:** the full daily loop (both plans, the strategy, candidate outcomes), A0 only. Gate audits C1 (location) and C2 (reward:risk). Half-day check (parity gate 4) is moved to Phase 2, because Nov 28 falls there.
- **Delivers:** for each day, the packet, both plans, the JOFS-style log and a one-page day sheet (zones, candidates, trades). A bug list with fixes.
- **Pass:** every row type appears and makes sense against the chart for at least 3 hand-checked days; no crash, no missing day; C1 and C2 find no unexplained errors. **Profit/loss is not looked at.**
- **If it fails:** fix and rerun Phase 1. Its days stay debug days and never count.

### Phase 2. First baseline (Nov 5 – Dec 4, 2025, 21 sessions)

- **Starts when:** Phase 1 passes. The code is tagged; no rule changes during the phase. The promotion rule (below) is frozen before Phase 2 starts, so it cannot be fitted to what Phase 2 shows.
- **Runs:** A0 with both plans; every candidate gets its outcome; the by-blocking-rule report; the S1.4 flag reports (passive trap, relative delta, fight, reversal after a stop-out, grade C); exit models M0–M3 as a first look; map variants MAP0–MAP3 on the rules-only plan; half-day check on Nov 28 and Dec 1.
- **Delivers:**
  - A0 report card: trades, win rate, net R, drawdown, by grade, family, zone kind, time of day, plan source.
  - What-fails-and-why review: every losing trade and every blocked winner, by hand, with the reason.
  - **The Phase 3 change list,** written and dated before Phase 3 starts: which pre-registered arms (A1–A8) and exit models go forward, plus any new arm, each with its exact rule.
- **Pass:** the change list is written and frozen. Expect about 20–40 trades and several hundred candidates: enough to see why gates block, not enough to prove profit. No promotion decision is made in Phase 2.

### Phase 3. Test changes (Dec 5, 2025 – Feb 4, 2026, 41 sessions)

- **Starts when:** the Phase 2 change list is frozen.
- **Runs:** A0 and every listed arm, primary arms A1–A3 first, then A4–A8; exit models (full replay for any put forward); map variants. Factorial combinations only if declared in the change list.
- **Delivers:** each arm and exit model paired against A0, with session-bootstrap confidence intervals; for each one, a verdict of **promote**, **reject** or **insufficient evidence**.
- **Final combination:** the exact frozen configuration (A0 plus every promoted change, with its exit model and map variant) is declared in writing and **replayed as one strategy** over Phase 3 before it is frozen. Changes that each help alone can hurt together. If the combination fails the promotion rule against A0, the change with the weakest single result is dropped and the combination is replayed again.
- **The frozen strategy** is written down with its code tag.
- **If nothing passes:** A0 goes to the holdout unchanged.

### Promotion rule (frozen before Phase 2)

A change is promoted only if all four hold on the Phase 3 sessions:
1. **Primary metric:** net R per session, paired against A0 on the same sessions (base-case fills, 1-tick stop slippage).
2. **Evidence:** the lower bound of the 90% session-bootstrap confidence interval of the paired difference is above 0.
3. **Drawdown:** max drawdown in R is no worse than 1.25 × A0's.
4. **Sample:** at least 20 trades differ from A0's (admitted, removed or exited differently).

It must also stay at or above A0 under the 2-tick stop-slippage stress. If rule 4 fails, or the interval spans 0, the verdict is **insufficient evidence**, A0 stays, and the change can be retested on Block 2. With 41 sessions, expect this verdict often; it is an honest result, not a failure of the method.

**What passing means (v3.10, clarification; the four tests are unchanged):** passing Phase 3 shows improvement over A0 under the registered tests. It does not show profitability or authorize live trading. Combinations go through the final-combination replay, and live use needs the Phase 4 holdout.

### Phase 4. Holdout (Feb 5 – Apr 21, 2026, 52 sessions)

- **Starts when:** the frozen strategy is tagged. Nobody looks at these days before the run.
- **Runs:** the frozen strategy once, both plans. XGBoost may be scored afterwards for research, but it plays no part in the decision.
- **Delivers:** the holdout report card, compared with Phase 3.
- **Pass (holdout rule):** net R per session above 0 with the 90% session-bootstrap lower bound above −0.1 R; max drawdown within 1.5 × the Phase 3 drawdown of the same configuration; no day breaks the daily loss limit. If it fails, it is not retuned on these days.

### Phase 5. Extra checks

- **Untouched data:** Block 2 from Apr 22 to Aug 31, 2026 (about 91 sessions). Sep 1 – Oct 2, 2026 overlaps the parity days, the live DEMO period and the period the strategy was built on, so it is a **consistency check only** and never decides anything.
- **If Phase 4 passed:** run the frozen strategy once on Apr 22 – Aug 31. **Pass:** the same holdout rule. A market explanation for a poor result can start new research, but it never turns a failure into a pass.
- **If Phase 4 failed and the strategy changes:** before anyone looks at Block 2, split it by date into a new development period (Apr 22 – Jun 30, about 48 sessions) and a new validation period (Jul 1 – Aug 31, about 43 sessions), and repeat the Phase 3 and Phase 4 rules on them.
- Only after a pass does any gate change go into the NinjaTrader strategy, and only after the examples are checked by hand on the chart.

## Rejected-candidate gate experiment (Phases 2–4)

Source: "Jeron Rejected-Candidate Controlled Test, protocol v1.0" (Oct 22, 2026). This is an observational study: no live or SIM gate changes until an arm passes.

**Why:** Oct 22 export, 279 rejected candidates, 263 with a definite outcome. Target-first share by rejection reason:

| Reason | Target-first |
|---|---|
| All rejected | 38% |
| WEAK_DELTA | 92/232 = 40% |
| WEAK_DELTA_PCT | 91/240 = 38% |
| NO_TRAPPED_SIDE | 38/112 = 34% |
| UNQUALIFIED_LOCATION | 21/80 = 26% |
| POOR_REWARD_RISK | 35/55 = 64% (near targets are hit often; that doesn't mean profit) |

- Weak delta blocks about 1.5 losers per winner. Whether that is good or bad depends on the size of the winners and losers, which the export doesn't show, so it can only be settled in net R over many sessions.
- The counts overlap and are not deduplicated; many candidates failed several gates.

### Primary arms (pre-registered Oct 22–23)

| Arm | Change at the original signal | Phase |
|---|---|---|
| A0 Control | All gates unchanged (S1.4 defaults) | Phase 3 |
| A1 Delta only | WEAK_DELTA threshold 150 → **75**. Only the event gate; the trapped-side detector keeps 150. Delta % and all other gates unchanged. | Phase 3 |
| A2 Delta % only | WEAK_DELTA_PCT threshold 10% → **5%**; raw delta and all other gates unchanged | Phase 3 |
| A3 Both delta | 75 and 5% | Phase 3 |
| ~~B1 Continuation trapped-side~~ | **Withdrawn (v3.2).** In S1.4 NO_TRAPPED_SIDE fires only for RESPONSE candidates, so waiving it for continuations (INITIATION) changes nothing. Replaced by A5. | — |
| C1 Location audit | No override; recompute location from the frozen pre-open map and list misclassified zones | Phase 1 |
| C2 RR audit | No override; recompute risk and reachable target as of entry and list calculation errors | Phase 1 |

The 0.75× level (112.5 delta and 7.5%) is a secondary arm, run only after the 0.5× results are read.

### Secondary arms (pre-registered Oct 24, read only after A1–A3)

| Arm | Change | Jeron source |
|---|---|---|
| **A4 Context-scaled proof** | **With-context responses** (not counter-context) pass on a trapped side (aggressive, or `trapped_passive` = Y) plus the existing confirmation bar, with no WEAK_DELTA or WEAK_DELTA_PCT check. **Counter-context candidates** (grade C) need all of the L3 proof listed under the table; then grade C is allowed. With-context initiations are unchanged from A0. | Part 4 ~10:28, ~10:38; Strategy-in-30 ~13:05; entry-rules L3 |
| **A5 Passive trap** | A0, plus `trapped_passive` = Y counts as the trapped side. Only candidates with `passive_would_rescue` = Y can change. | Part 3 ~35:22; Part 4 ~6:04; Trade Recap ~5:11 |
| **A6 EMA / CVD alignment** | A0, plus `ema21_aligned` = Y and `cvd_avg_aligned` = Y both required | Strategy-in-30 ~17:28; Trade Recap ~5:14 (T7) |
| **A7 Fight veto** | A0, minus candidates with `fight_flag` = Y | Part 3 ~10:52 (L4) |
| **A8 Relative delta** | WEAK_DELTA and WEAK_DELTA_PCT replaced by `delta_pct_vs_session` ≥ 1.0 (stronger than the session's average bar) | Part 3 ~24:04 |

The A4 proof for a counter-context candidate (L3) is all of the following:
- INITIATION family
- a large trade or Power Trade in the trade's direction (LARGE_BUY / LARGE_SELL)
- an imbalance in the trade's direction (BUY_IMB / SELL_IMB)
- a follow-through bar: the next bar closes beyond the zone in the trade's direction, with delta in that direction
- an acceptance close: the trigger and follow-through closes are both beyond the zone

Entry is then at the follow-through bar close, with the initiation stop.

**Settled points:**
1. **Thresholds:** "relaxed" = 0.5 × the default for that gate. S1.4 defaults copied from the code (Oct 24): `MinAbsDelta = 150`, `MinDeltaPct = 10`. They are not changed after Phase 2.
2. **Trade limit:** 3 per day, also reported at 2 per day.
3. **Data source:** footprint and delta from MBO trades with the exchange aggressor flag; every row carries `footprint_source=MBO_AGGRESSOR`. No L2 or L3 book column enters any arm.
4. **All candidates** get an outcome (step 7), linked by EventId and the original signal time. Confirmed-entry outcomes are kept separate from candidate outcomes.
5. **Families (settled Oct 24):**
   - INITIATION = the market comes from one side and closes through the level: the continuation family.
   - RESPONSE = the market is pushed back away from the side it came from: the reversal family.
   - No other continuation label exists in S1.4.
6. **Grades:** A0 uses the S1.4 grade filter (A+,B+,B). Every arm is also reported with C allowed (G-ALL), so the effect of the S1.4 change is visible on its own.

**Rules:**
- A candidate passes an arm only if every other original gate passes. A candidate that failed three gates is not rescued by removing one.
- Factorial combinations (e.g. A3 + A5) only after the single-gate results, and declared before they are run.
- **Deduplication:**
  - Candidates with the same direction, setup family and zone form one opportunity until 15 bars pass with no candidate, or price leaves the zone by 1 ATR and comes back. 15 bars is a placeholder; sensitivity is checked at 10 and 30.
  - Within an opportunity, take the earliest eligible candidate per arm.
  - One position at a time; the daily trade limit and the 2-loss halt apply.
- **Each arm is a full replay of the day (v3.4).** The one-candidate-per-bar ranking depends partly on status, so when an arm relaxes a gate a different candidate can win that bar. Each arm therefore reruns, from the full pool kept in step 7 (shadows included): the per-bar ranking, confirmation, position state, the daily trade limit and the 2-loss halt.
- **Labels (v3.4):**
  - TARGET_FIRST, STOP_FIRST (including same-tick ties).
  - TIME_EXIT: flattened at 14:55 CT or by the session-close exit, with its realized net R.
  - NOT_TRIGGERED.
  - UNKNOWN: missing or corrupt data only, and every one is listed in the report.
  - TIME_EXIT trades always count in net R.
- **Costs:** commission, spread and slippage, as in the fill model.
- **A missed winner counts** only if the arm qualifies it before the move and the original target was reachable after a realistic entry.

**Measures per arm, paired against A0 on the same opportunities:**
- net R expectancy, median R, win rate
- MFE/MAE in R, max drawdown
- opportunity coverage, rejected winners recovered, rejected losers admitted

Bootstrap confidence intervals by session. Split by NY open vs later, reversal vs continuation, long vs short, zone class and volatility regime, always with the denominators.

**Promotion:**
- An arm replaces A0 only if it passes the promotion rule (Phase plan) in Phase 3, survives the final-combination replay, and the frozen strategy then passes the Phase 4 holdout (run once).
- Oct 22 alone never selects a parameter.
- Examples are reviewed by hand on the chart before any NinjaTrader gate change.

## Exit models (entry rules M1–M4)

Jeron scales out, moves the stop to break-even and trails; the strategy holds one target.
- **Diagnosis:** every model first runs on the **same entries**, A0's and separately each arm's. This shows what the exit does to the same trades.
- **Full replay (v3.4):** a model put forward for promotion is then replayed as a whole strategy. A runner held longer blocks later trades under the one-position rule, so the trade list changes.
- Results are in R of the original risk.
- **Partials:** the half-unit version (half of one contract) is kept as **theoretical attribution only**. M2 and M3 are also run with **2 contracts** (1 off at TP1, 1 runner) with commission on both, and only that version can be promoted.

| Model | Rule | Jeron source |
|---|---|---|
| **M0** | The strategy as built: one stop, one target, flatten at 14:55 | — |
| **M1** | Exit at the close of the bar that completes the **second** consecutive opposing effort bar (the EXIT_WARN streak of 2), whatever the P/L | Part 3 ~41:27 |
| **M1a** | Exit at the first EXIT_WARN if the trade is not in profit (the S1.x setting 'Exit on first exit warning', off live) | Part 1 ~53:00; Part 2 25:00 |
| **M2** | See below | Part 2 22:00, 1:17, 1:29; Trade Recap ~5:22; 60k 44:01 |
| **M3** | Counter-context trades (grade C, or COUNTER_CONTEXT flag): see below. With-context trades use M2. | Strategy-in-30 ~22:45 |
| M4 (report only) | Reversal after a stop-out: see the report below | Part 3 ~31:08; Strategy-in-30 ~16:40 |

**M2:**
- Half off at the candidate's target (TP1).
- The stop moves to entry from the bar after TP1 fills.
- The runner targets the next qualified level beyond TP1 (TP2), else holds to the flatten.
- The runner's stop trails 2 ticks beyond the far edge of the newest intraday imbalance or Power zone created in the trade's direction after entry. It only moves in the trade's favour.

**M3:**
- The stop moves to entry once the trade is +0.5 R (from the next bar).
- Half off at 1 R or TP1, whichever comes first.
- The runner trails the previous completed 1-minute bar's low (longs) or high (shorts).

All trailing and break-even rules take effect from the bar after the condition; same-bar ambiguity follows the fill model. A model can move into the strategy only after it passes the promotion rule against M0 in Phase 3 (full replay, 2-contract version) and the frozen strategy holds in the Phase 4 holdout.

## Map variants (rules-only plan, Phases 2–3)

Each variant changes one map v2.3 setting from the default; everything else is A0. The Claude plan is run only on the default map, for cost.

| Variant | Setting |
|---|---|
| MAP0 | v2.3 defaults (settlement family SET, PD2/PD3 high-low on, HTF 60 days from 1-minute bars, min 40) |
| MAP1 | Settlement family = PD (PD POC + PD settlement alone stays a TARGET zone) |
| MAP2 | PD2/PD3 high-low off (the v2.2 level set) |
| MAP3 | HTF 20 days from tick days, min 10 (the v2.2 composite) |

Measured: zone count and width, check B/C/D failures, the APPROVED share, and A0 net R per variant.

## Reports

Each report is broken down by:
- grade (also G-ALL), setup family, zone kind, time of day and day type
- rules-only plan vs Claude plan
- GEX regime and replica confluence (logged only)
- retest v1 vs v2 vs immediate entry
- research rules (FAV01–RIZ01) and exit models (FAV03, CAR04, **M0–M3**)
- gate-experiment arm (A0–A8)
- map variant (MAP0–MAP3)

**By blocking rule:** for each rejection reason, winners blocked vs losers blocked, in count and net R, after deduplication, plus how many of those candidates failed only that gate.

**New reports in v3.2:**
- **Reversal after a stop-out:** REVERSAL_CANDIDATE rows with RetestModel=AFTER_STOP and their REVERSAL_OUTCOME, split by source (LIVE_STOP, OUTCOME_STOP), family and bars after the stop. Also shown: how many fell after the 2-loss halt, i.e. trades Jeron would have taken that the halt blocks.
- **Passive trap:** count of `passive_would_rescue` = Y by kind (HIGH_EFFORT_LOW_REWARD, NO_AGGRESSION, WICK_NO_FOLLOW), with their outcomes.
- **Relative delta:** outcomes by decile of `delta_pct_vs_session` and of `delta_rank_20`, for event-valid and rejected candidates.
- **Fight:** outcomes with and without `fight_flag`, by `fight_kind`.
- **Grade C:** the S1.4 change on its own. A0 with C vs without, in trades, net R and drawdown.

Each report also shows the count of qualified trades.

**XGBoost (exploratory only, v3.4):** the Phase 2–3 sample is too small to validate a model, so XGBoost plays no part in any promotion or holdout decision. Before it could ever be used, a separate protocol is written and frozen: labels, feature timing (known at entry), chronological walk-forward validation, overlap control between neighbouring candidates, the tuning process and the decision threshold.

## Schema

`Arms_<day>.parquet` (unchanged fields): session_date, contract, run_id, strategy_version, plan_hash, EventId, opportunity_id, signal_time_ct, entry_time_ct, setup_family, direction, zone_id, frozen_zone_valid, footprint_source, delta, delta_pct, imbalance_flag, trapped_side_flag, displacement, original_gate_bitmask, rejection_reasons, arm_id, remaining_gates_pass, original_entry/stop/target, counterfactual_entry/stop/target, estimated_cost_ticks, label_status, gross_R, net_R, MFE_R, MAE_R, latency_ms, overlap_group, data_quality_flag.

**Added in v3.2:** grade, counter_context, trapped_passive, trapped_passive_kind, passive_would_rescue, delta_pct_vs_session, delta_pct_session_avg, delta_rank_20, fight_flag, fight_kind, ema21_aligned, cvd_avg_aligned, after_stop_src, after_stop_bars, map_variant, plan_source (rules / claude).

**Added in v3.4:** label_status values TARGET_FIRST / STOP_FIRST / TIME_EXIT / NOT_TRIGGERED / UNKNOWN; exit_reason; fill_side (ASK / BID); fill_latency_ms; stop_slippage_ticks; replay_mode (DIAGNOSIS / FULL_REPLAY).

`Exits_<day>.parquet`: EventId, arm_id, exit_model, contracts (1 = half-unit attribution, 2 = executable), replay_mode, tp1_hit, tp1_time, be_time, runner_exit_time, runner_exit_reason, partial_R, runner_R, total_net_R, MFE_R, MAE_R.

Every feature is known at or before the **entry** time. For most candidates that is the signal bar; for A4 counter-context candidates the entry moves to the follow-through bar close, so the follow-through features are known when the trade is placed.

## Open items

- ~~Copy the delta thresholds~~ Done: 150 / 10 (A1 = 75, A2 = 5%).
- ~~How continuations are labelled~~ Done: INITIATION = continuation, RESPONSE = reversal; B1 withdrawn.
- ~~Confirm the GEX options data was downloaded for Block 1~~ Done (Oct 23–24): all roots except QN5 (no listings).
- ~~Roll dates~~ Done (v3.5): NinjaTrader's dates; roll-day files bought for Block 1 and Sep 2026. Block 2 needs the Jun 12, 2026 roll fix.
- ~~Economic calendar for Oct 2025 – Apr 2026~~ Done (Oct 24): copied to `K:\Databento_BackTesting`, spot-checked against BLS and the Fed, roll rows on NinjaTrader's dates.
- ~~Replica GEX for Block 1~~ Done (Oct 24): `gex_levels_block1.csv`, 124 sessions.
- ~~Holiday and half-day list for Block 1~~ Done (Oct 24, from the MBO timestamps): closed Dec 25, Jan 1, Apr 3; holiday halt at 12:00 CT, no cash session, Nov 27, Jan 19, Feb 16; half days Nov 28 and Dec 24 (cash to 12:00 CT, futures to 12:15 CT).
- ~~Data integrity table (parity gate 6)~~ Done (Oct 24): passed; degraded days used with a flag.
- ~~NinjaTrader's contract merge setting~~ Done (Oct 24): Merge non back adjusted.
- ~~Commission~~ Done (Oct 24): $2.87 per contract per side baseline.
- ~~Kyron to confirm the v3.4 defaults before Phase 1~~ Confirmed Oct 25 (Kyron: "go with your recommendations").
- ~~Weekly options Q5B / Q5D coverage~~ Not an issue: fifth-week roots only list in months with a fifth week; the replica ran on all 124 sessions with 439–2,800+ options each.
- Prompt v1.5's exact packet title search uses `NQ_DEC26`; the map writes `NQ_12_26`. Change it in the prompt and the 08:11 scheduled task (the fallback search finds the file today).
- ~~Kyron's PC folder connected~~ Done: `K:\Databento_BackTesting` is connected (Oct 24).
- Block 2 data bought before Phase 5. Only Apr 22 – Aug 31, 2026 is untouched; nobody looks at it before its run.

---

## Appendix A — Strategy S1.4: every item and how the backtest treats it

**T** = trading rule, replayed exactly. **L** = logged column or row, reproduced. **X** = excluded, reason given. All numbers are the S1.4 defaults (ours unless marked Jeron).

### A1. Evidence (built from MBO trades in the backtest)

| Item | Default | Use |
|---|---|---|
| Footprint: bid/ask at price per 1-minute bar | MBO aggressor flag (NT: Volumetric) | T |
| Diagonal imbalance / strong / low-liquidity ratio | 400% / 900% / 300% (Jeron), min cell 10, zero denominator counts | T |
| Stack → intraday zone; qualified stack | ≥ 2 rows; ≥ 3 or all strong | T |
| Large trades: Consistent Bid/Ask clusters + time clusters | 250 ms, 2 ticks | T |
| Power Trade tiers | NY 300/400/500, low-liquidity 150/200 (Jeron) | T |
| Large-trade evidence; Deep Trades | ≥ 60; 60 / 100 (Jeron) | T |
| High effort, low reward | \|delta\| ≥ 400 and body < 8 ticks | T |
| Tape speed; CVD lookback | 10 bars, ratio 1.2; 3 bars | T (flags, grade) |
| Session VWAP + sigma, developing POC, ATR 14, EMA 21, CVD average 21 | — | T / L |

### A2. Locations and state

| Item | Default | Use |
|---|---|---|
| Plan zones replace frozen zones; DECISION vs TARGET; T_ prefix = target only | on | T |
| Side rules long= / short= (ANY, RESPONSE, INITIATION, NONE); alt_ rules after invalidation | enforced | T |
| Lava band (MIDDLE_IS_LAVA) | on | T |
| Invalidation after 'Acceptance closes' beyond the level → new context | 3 closes | T |
| Intraday IMB and Power zones; expire at session start | max 40 | T |
| Touch tolerance, break distance, re-arm distance | 2, 2, 40 ticks | T |
| State machine WAITING → TESTED → INITIATION / RESPONSE → ACCEPTED / FAILED | — | T / L (STATE rows) |
| Frozen-zone fallback (no plan) | blank | X (every backtest day has a plan) |

### A3. Event gates (the candidate is Rejected if any fails)

| Gate | Default | Use |
|---|---|---|
| NO_FOOTPRINT_DATA | — | T |
| WEAK_DELTA | 150 | T (arms A1, A3, A4, A8) |
| WEAK_DELTA_PCT | 10% | T (arms A2, A3, A4, A8) |
| NO_IMBALANCE_OR_LARGE_TRADE | on | T |
| LOW_DISPLACEMENT | 8 ticks | T |
| NO_TRAPPED_SIDE (RESPONSE only): aggressive failed attempt, search back to the first touch (max 30 bars), trigger bar excluded | on | T (arms A4, A5) |

### A4. Entry gates (the candidate is EventOnly if any fails)

| Gate | Default | Use |
|---|---|---|
| OPPOSING_VWAP | off | T |
| AT_SESSION_POC | 8 ticks | T |
| COUNTER_CONTEXT reject | off (grade C instead) | T |
| UNQUALIFIED_LOCATION | on | T |
| OUTSIDE_NY_SESSION | on | T |
| TARGET_ONLY_ZONE, PLAN_SIDE_BLOCKED, PLAN_NEEDS_RESPONSE, PLAN_NEEDS_INITIATION | on | T |
| MIDDLE_IS_LAVA | on | T |
| ES gate | log-only (ES_GATE_FAIL_LOGGED) | L |
| NO_PLAN | on | T (only on days the plan step fails) |
| L2 alignment | off | X (L2 not used in arms) |
| INVALID_RISK, RISK_TOO_WIDE (off), POOR_REWARD_RISK | min 1.5 R | T |

### A5. Candidate handling

| Item | Default | Use |
|---|---|---|
| Statuses Rejected / EventOnly / AwaitConfirm / Pending / Qualified | — | T |
| Response confirmation bar: body, beyond the zone, delta in the trade's direction; then risk, R:R, lava and ES are rechecked | on | T |
| Late trigger | 3 bars | T |
| One candidate per bar and direction (rank: status, location, R:R, first) | on | T |
| Shadow candidates and their outcomes | on | L |
| Stop by family: response beyond the defended zone or the rejection swing; initiation beyond the trigger bar; buffer | 2 ticks | T |
| Target: qualified levels, VWAP, session high/low; nearest meeting min R:R | on | T |
| Counter-context: first target only | on | T |
| Grades: initiation through VWAP with imbalance or large trade and tape speed = A+; ran through an opposing imbalance with tape speed = B+; other initiations B; response = B+; counter-context = C | — | T |

### A6. Outcomes and research rows (logging only)

| Item | Default | Use |
|---|---|---|
| OUTCOME to the NY session end; 15-bar snapshot; same bar = stop | — | L (step 7 replaces it with ticks; both kept) |
| EXIT_WARN: first opposing aggression; streak of opposing effort | streak 2 | L (exit models M1, M1a) |
| Retest v1 paths | 15 bars, 2 and 8 ticks | L |
| Retest v2 (order-flow retest), REVERSAL_CANDIDATE after a failed retest | 30 bars, 1 ATR, 3 bars, opposing delta 100, 2 ticks | L |
| Research rules v1.1: FAV01, FAV02, CAR01, CAR03, RIZ01 rows; feature columns G1–G13 | defaults in group 5d | L |
| Exit models FAV03 (balance POC target), CAR04 (break-even at 1 R) | — | L |
| ES research columns (v2.11) | — | L |
| L2 snapshot columns | — | L (from `l2_features.py`, research only) |
| **S1.4 2a** trapped_passive, trapped_passive_kind, passive_would_rescue, flag TRAPPED_PASSIVE | max delta 5%, wick 50% | L (arms A4, A5) |
| **S1.4 2b** delta_pct_vs_session, delta_pct_session_avg, delta_rank_20 | 20 bars | L (arm A8) |
| **S1.4 2c** reversal after a stop-out (LIVE_STOP / OUTCOME_STOP), REVERSAL_CANDIDATE AFTER_STOP, flag AFTER_STOP_REVERSAL | 10 bars | L (report) |
| **S1.4 2d** fight_flag, fight_kind, flag FIGHT | 3 bars, doji ≤ 20% | L (arm A7) |

### A7. Trading layer

| Item | Default | Use |
|---|---|---|
| Orders only for Qualified, non-shadow candidates | — | T |
| Market entry on the next tick; stop and target by signal name; one position | qty 1 | T |
| review=APPROVED required | on | T |
| no_trade windows; max_trades (plan can only lower it) | — | T |
| Grades allowed | A+,B+,B | T (G-ALL sensitivity) |
| Entry hours: NY session, last entry 14:30; flatten 14:55; session-close exit | — | T |
| Max daily loss, consecutive-loss halt | 400 ticks, 2 | T |
| PRICE_PAST_STOP, PRICE_PAST_TARGET, ENTRY_SLIPPAGE | 12 ticks | T |
| Protective order rejected → flatten | — | X (no broker in the backtest) |
| Live-account guard, simulated-account prefixes | — | X (no account) |
| Manual approval file | off | X |
| Exit on first exit warning | off | T as M1a only |
| Fast load, warm-up days | 1 / 1 | X (the engine evaluates every date, with history from the cache) |
| Chart display: zones, labels, status panel, trade lines | — | X |
| L2 recording to hourly files | — | X |
| Plan file polling, PLAN_WAITING, PLAN_LOADED_LATE, PLAN_MISSING, replacement plans | — | X (plans are delivered on time) |

## Appendix B — Map v2.3: every item and how the backtest treats it

**T** = feeds the plan and therefore the zones (replayed exactly). **P** = packet field, reproduced for the plan step and the reports. **X** = excluded.

| Item | Default | Use |
|---|---|---|
| As-of 08:10 CT; built on the first trade at or after it, from earlier data only | — | T |
| Cash 08:30–15:00 CT, session start 17:00, settlement = VWAP of the 30 s before 15:00 | Jeron (cash hours) | T |
| **Half days**: early cash end and settlement; no gap logged for the early close | 2025-11-28@12:00, 2025-12-24@12:00 for Block 1 (cash end; futures trade to 12:15) | T |
| Holidays (prior sessions by calendar) | Block 1 list (open item) | T |
| Data-gap detection; partial profiles left out | 15 min; on | T |
| PD, PD2, PD3 volume VA/POC (70%) and TPO VA/POC | Jeron (70%) | T |
| PDH / PDL; **PD2H/PD2L, PD3H/PD3L** | on | T (MAP2 turns the PD2/PD3 ones off) |
| PD settlement, **family SET or PD** | SET | T (MAP1 = PD) |
| Overnight VA / TPO / high-low; session VWAP ± 1 σ | — | T (VWAP not in zones) |
| Developing week and prior week VA / TPO / high-low; weekly VWAP | — | T |
| Single prints (TPO_PD, TPO_ON, TPO_WK, TPO_PWK) | ≥ 2 rows of 5 points | T (zone tags) |
| Composite HVN / LVN | 5 days, 5-point rows, 70% / 30% | T (zone tags) |
| **HTF composite from 1-minute bars** (approximate volume at price) | 60 days, min 40 for zones, 100 days loaded | T (MAP3 = 20 tick days, min 10) |
| **Dated manual HTF levels**; staleness flag | none in the backtest | X (no TradingView history; the field stays empty, so no hindsight) |
| Zone clustering | merge 15, pad 5, max width 60 points; DECISION = 2+ families | T |
| Manual zones | none | X |
| Packet: data notes and gaps, settings, levels, areas, zones | — | P |
| Zones[].tests on 1-hour bars, incl. **hours_per_test, shrinking_time** | 10 days | P (prompt check D; rules-only plan step 3) |
| prior_sessions, value_migration, value_vs_price | overlap 50% | P |
| Overnight inventory (net long / short), distance from settlement, pullback depth | 70% / 30% | P |
| Location vs PD, ON, week, prior week, VWAP, weekly VWAP, settlement, PD range | — | P |
| Delta profile (PD cash, overnight) | 5-point rows | P (from MBO) |
| Structure: 20 daily rows, 1-hour bars, swings, h1 trend | swing strength 3 | P |
| ES cross-check (PD settle, cash high/low, approx VA, ON high/low, relative strength) | ES 1-minute | P |
| pd_on_composite **+ va_overlap_pct, overlapping** | — | P |
| **balance_composite** (PD2 + PD + ON members, overlap %, merged_three) | — | P (rules-only plan steps 1 and 5) |
| **double_distribution** | — | P |
| ranges (ADR, ON range in ADR, PD move in ADR) | 10 days | P |
| swing_profile (anchored VA, top delta rows) | 10 days | P |
| overnight_distribution (thin thirds) | 20% | P |
| **calendar** (half_day_today, pd_half_day, cash end, settlement family) | — | P (check F) |
| Files: Zones_, FrozenZones_, PreopenLevels_ CSV; atomic write | — | X (the engine writes only the packet) |
| Drawing and status panel | — | X |

## Appendix C — Prompt v1.5: every item and how the backtest treats it

**T** = replayed by the rules-only plan and given to the blinded Claude plan. **X** = excluded.

| Item | Use |
|---|---|
| Packet selection by exact date; `date` and `asof_ct` verified; never another date's file | T (the engine passes only that day's packet) |
| No-hindsight rule (information before 08:25 CT only) | T (blinded: dates hidden, prices shifted, no web) |
| Macro note (VIX, 10-year, oil, news, calendar) | X: no note for past days; check F uses the calendar file; `macro=not verified (backtest)` |
| Jeron's questions: HTF structure, value, overnight inventory, who has been rewarded, delta profile, ES cross-check, macro alignment | T (Claude plan); the rules-only plan uses the packet fields named in its algorithm |
| Zone picking: start from packet zones, 2–4 decision zones near price on both sides, merge neighbours, targets on both sides, side rules, alt rules, confidence | T |
| Balance and balance_poc; omit on a migrating day | T |
| Lava: middle of the balance, 15+ points clear of decision zones | T |
| Invalidation levels with the new context | T |
| ES gates (logged only), es_settle | T |
| "Do not move a zone because of a GEX level" | T (GEX lines are added after the plan) |
| GEX map: MenthorQ manual file, replica fallback, regime, sanity check, QQQ conversion | Replaced by the replica only (see GEX) |
| Review A. Data: date and as-of correct, no gaps in 24 h, PD / ON / weekly profiles present, ref price near the ON range, ES present | T |
| Review B. Zones: no overlaps, ≤ 60 points wide, a decision zone each side within 1 ADR, targets above and below, lava 15+ points clear | T |
| Review C. Risk fit: stop ≈ zone width + 2 ticks, ≥ 1.5 R to the nearest target, stop ≤ about a third of the daily loss limit | T |
| Review D. Test history: 4+ rejections with lower highs / higher lows → INITIATION; crossed both ways in the last day → NONE | T |
| Review E. Context fit: counter-context sides INITIATION or NONE; invalidation beyond the zones | T |
| Review F. Day suitability: tier-1 data windows (2 min before to 15 min after; 07:30 data → 08:30–08:40); FOMC 12:45–15:00; mega-cap earnings → max_trades=1; ON range > 1 ADR or gap > 0.5 ADR → max_trades=1; half day, holiday or roll day (NinjaTrader's roll dates, v3.5) → LOG_ONLY | T (calendar file) |
| Decision: APPROVED only if A passes and B–E are fixed; when unsure, LOG_ONLY | T |
| Plan format, `end=1`, `plan_id`, `asof=08:25`, optional lines | T (schema check) |
| Plan file naming and replacement (`_replaced_HHMM`), Drive upload, 08:20 deadline | X (files are written directly) |
| Scheduled tasks at 07:45 and 08:11; MenthorQ deadline 08:05; approval file | X (live operations) |
