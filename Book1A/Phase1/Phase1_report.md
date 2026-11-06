# Book 1A – Phase 1 report (shakedown, mechanics only)

Runner: Claude Code desktop session, `K:\Book1A_runner\code`, branch `book1a-phase1`, Nov 5, 2026 (Kyron's Phase 1 go
of Nov 5). Controlling doc: Book 1A replay plan, sections 2, 3, 6, 7, 10 (local export `Book1A/specs/Book1A_replay_plan.md`).
**No P&L, net R, win rate, dollar result or pass / fail of a result is in this report.** P1-P8 below are mechanics rules
written before the run. Phase 1 days are debug days and never count.

**Update (Nov 5, after Kyron's review):** ledger paths added (section 1); P6 closest-approach table added; specs now
come only from `K:\Book1A_runner\specs_no_results\` (checker-redacted), copied into `Book1A/specs/` in commit be85d5f
(access log event 10). The rules and thresholds used in this run are unchanged by the redaction (only Book 1 result
lines were replaced). Phase 1b not started.

## 0. Read first

| Item | Status |
|---|---|
| Phase 1 mechanics run, R1-R4, 10 sessions Oct 22 - Nov 4, 2025 | done |
| P1-P8 | **all PASS** (P7: sheets ready; Kyron's 3-day chart check pending) |
| Bugs found (calculation or timing) | **0**; no rerun needed |
| Diagnostics (M-J1, M-J2, exit cue (a), CVD_DIV, BREAKOUT_SPEED, GEX V2 / V3 / V5, volatility control, context GEX tags, 10 NQ / MNQ, wide-zone report) | **NOT BUILT**: moved to Phase 1b (Kyron, Nov 5) |
| L2 E1 / E2 / E4 | **NOT RUN (U11)**: L2F audit and fixed-price build not done; E4 hold time N not registered |
| Section 3, Nov 17-19 location diagnostic | done; 5 misses reported as findings, nothing changed |
| Section 4, CVD definition check | **moved to Phase 1b** (needs CVD_DIV; Kyron, Nov 5) |
| Step 0, Drive copies | already in Drive (see section 9) |

**Phase 1b (Kyron, Nov 5), before Phase 2:** build the diagnostics from the results-free spec Kyron will place in
`K:\Book1A_runner\specs_no_results\` (no Book 1B / 1C / 1D or footprint doc on Drive is opened); logged only, none may
change an R1-R4 entry, exit or size; rerun Phase 1 with them on and show the R1-R4 ledgers are byte-identical to this
run (sha256 in section 8); then section 4.

## 1. Run

| | |
|---|---|
| Code | R1 / R2 / R4 on `5ba0172`; R3 and the checks on `ffa85a2`. `git diff 5ba0172 ffa85a2` touches only `.gitignore`, the access log and two new files (`book1a/run_r3.py`, `book1a/phase1_checks.py`), so R1 / R2 / R4 ran the same code. R3 was first run on the uncommitted script and rerun on `ffa85a2`: all four R3 output files byte-identical. |
| Inputs | `BOOK1_ROOT = K:\Book1A_inputs` only; harness exe `K:\Book1A_inputs\jeron_harness\build\JeronHarness.exe` |
| Sessions | 2025-10-22, 23, 24, 27, 28, 29, 30, 31, Nov 3, 4 (10) |
| R1 A0 | `python -m book1a.run_r1_r2 --phase phase1 --fill v3.5 --block1 K:\Book1A_inputs --out book1a\Phase1\runs\phase1` (no veto, M0) |
| R2 C1 | same run: veto FZ1 or L1 or T8, RH1 15 bars / 2 ticks, M0 |
| R3 C1 + C3 risk | `python -m book1a.run_r3 --block1 K:\Book1A_inputs --a0-run book1a\Phase1\runs\phase1 --out book1a\Phase1\runs\phase1_r3` |
| R4 Book 1A at M0 | `python -m book1a.run_r4 --block1 K:\Book1A_inputs --a0-run book1a\Phase1\runs\phase1 --plans Book1A\Phase0\plans_phase1 --phase phase1 --out book1a\Phase1\runs\phase1_r4 --candidate-days <all 10>` (veto L1 or T8, RH1, FZ1 logged only) |
| Fill model | **v3.5 for all four** (`--fill v3.5` for R1 / R2; the run_r1_r2 default "book1" would have used v3.4 on Phase 1 days) |
| Risk (R3, R4) | U3: $100,000, 1% = $1,000 per trade, $2,000 daily, NQ only, whole contracts, RISK_REJECT never shrinks; 3 trades and the 2-loss halt |
| Bootstrap seed | 20251205 (no interval is computed in Phase 1) |
| Ledgers | `book1a\Phase1\runs\` only (git-ignored), not committed, not aggregated, not sent to the checker; full paths below |

**Ledger paths** (paths only; the checker compares R3 and R4 with the Phase 0 references, the runner does not):

| strategy | ledger |
|---|---|
| R1 A0 | `K:\Book1A_runner\code\book1a\Phase1\runs\phase1\R1_A0_full.csv` (checker columns: `K:\Book1A_runner\code\book1a\Phase1\runs\phase1\checker_input\R1_A0.csv`) |
| R2 C1 | `K:\Book1A_runner\code\book1a\Phase1\runs\phase1\R2_C1_full.csv` (checker columns: `K:\Book1A_runner\code\book1a\Phase1\runs\phase1\checker_input\R2_C1.csv`) |
| R3 C1 + risk | `K:\Book1A_runner\code\book1a\Phase1\runs\phase1_r3\R3_M0_ledger.csv` |
| R4 Book 1A | `K:\Book1A_runner\code\book1a\Phase1\runs\phase1_r4\R4_M0_ledger.csv` |

(`K:\Book1A_runner\code\book1a\Phase1\runs\phase1_r3_precommit\` holds the first R3 run, on the uncommitted script;
its files are byte-identical to `phase1_r3\`.)

**Plan hashes, checked before the run:** all 20 files in `Book1A/Phase0/plans_phase1/` (10 `.txt` + 10 `.json`) equal
`plan_hashes_2026-11-05b.md` (plan .txt and sidecar .json columns): 0 differ. R4's own check: every PLAN_LOADED is
`<day>-b1a` from the staged copies, and every ledger row carries the plan id and sha256.

| day | plan .txt sha256 | sidecar .json sha256 |
|---|---|---|
| 2025-10-22 | 52baa4b7cdbbb36d60eee974995da58e6786be8835855f0f9bcb557cad19dcea | 6ceb2819e23488cd31833e9084782cc37554bfc423ccde61487c677099637b0a |
| 2025-10-23 | 194379a9299d5fd0d750b2d8c3ce3401f12d4d5e0243c9735aaf2b5710d2dd62 | aa0aac6e483a3f263ac4672afd98a0a2a355c470813dc1d236efbfe2005b3ba6 |
| 2025-10-24 | 0ff1657f32071ff262bb1906a6bfb87e0a02b0b16abb633cb4255839853be00b | 8e9abb915b7ff4db72c6fcb965c9c44155f69b5aa866a50bab4a26aac9c80ca6 |
| 2025-10-27 | 0f9da98ea99d7ea50f0d8c94dffc0a8c7b86b319079f78d2e7f7263a6a12e5d1 | 8aadd358b60883beda9c01659cf0c02da25cb2f93edc1c9214e08c84655e23fb |
| 2025-10-28 | dc79331fa0b6714acbfb85918c3f01299774144221499cc446b22d0934733294 | 54f6ead6acf5b666e065a7120d46fc4fd23f8903a285a3b4804c97e0144fd786 |
| 2025-10-29 | d40be1bb3c03e78b62db5693b2ad3ffd7166249dfc82d2141ff91d07f7ef132c | 20436ef6060cf16fd520c559cb80540177879e8d18873730bf6b3abb94cf03bc |
| 2025-10-30 | b2880f72d96094d1c93caafd8317c8b8506c766226b4a86efb5a37a02a25523e | b12c6273d6572524035002cba652acb4bcc90c0f093041571cac4fbb4fa76743 |
| 2025-10-31 | 311f506218872d62fa036df54424b5d65ad82869a24b87c4529f4ac5019fa980 | e47bce880f601813a4f01744c3887564735b84ced15b8476095084854d08d8cd |
| 2025-11-03 | d50ac6bf8c33805fee547b783bc56da7ca7750c129c00192c0df3aef6e69d890 | 51592dd68ad300f35cc676acb136ef5590fa671763cee2ab28f0e0e2bc8094a7 |
| 2025-11-04 | 62c073fe4aa639f58b6f143a9296901de29c0d39594ea65f220772705933a40d | 53048e64b9348fa7dfabbac0353791091beb4bd8ca011d7d3cd8bf96d3e49ffd |

Unit tests on `ffa85a2`: **236 run, 0 failures, 0 errors** (`unit_tests/unit_tests_2026-11-06.log`, UTC date).

## 2. Pass rules P1-P8

Full evidence: `phase1_checks.md` (phase1-checks-v1.0). The check script reads only times, prices, sizes, reasons, risk
decisions and the risk / fill settings; it never reads a gross, net, R or P&L column.

### P1 No crash, no missing session, row types: **PASS**
- All four strategies ran to the end (exit 0). The A0 run and the R4 run each have S1.4 log rows and a PLAN_LOADED on
  10 / 10 sessions. Trades by strategy: R1 7, R2 2, R3 1, R4 8 (counts only).
- 27 S1.4 row types appear in both runs. The only expected type with 0 rows is **FLATTEN**: no position was open at the
  flatten time (all 18 trades left on a stop or a target, P5). HALT rows appear (A0 2, R4 5).
- **Diagnostic rows absent, explained:** M-J1, M-J2, exit cue (a), CVD_DIV, BREAKOUT_SPEED, GEX V2 / V3 / V5, volatility
  control, context GEX tags, 10 NQ and MNQ feasibility, wide-zone eligibility report: **NOT BUILT** (Phase 0 P2.1-P2.6
  "Not started"; moved to Phase 1b). The candidate log keeps their columns as `null`. L2 E1 / E2 / E4 with NOT_VISIBLE /
  DATA_MISSING: **NOT RUN (U11)**.

### P2 Lookahead audit: **PASS**
`book1a.audit_run` on each strategy (`lookahead/R1..R4/`):

| strategy | decisions | inputs | violations | missing | plan build checks |
|---|---|---|---|---|---|
| R1 | 7 | 156 | 0 | 0 | 63 / 63 |
| R2 | 2 | 50 | 0 | 0 | 63 / 63 |
| R3 | 1 | 21 | 0 | 0 | 63 / 63 |
| R4 | 8 | 192 | 0 | 0 | 63 / 63 |

Every plan, zone, level, VWAP and GEX value used has available_at <= its use time (plan and zones 08:10 CT, GEX D-1
23:00 ET, REJ / FLIP swings + 15 bars). No diagnostic input exists yet (not built).

### P3 Tick test: **PASS**
72 ledger prices (entry, stop, target, exit on all 18 rows) and 166 attempt prices: 0 off the 0.25 tick. Plan files:
`test_plan_ticks` passes in the 236-test run.

### P4 Risk mechanics: **PASS**
- Largest stop that fits $1,000, recomputed: 1 NQ 196, 2 NQ 96, 3 NQ 63, 5 NQ 36, 10 NQ 16 ticks = the U3 table.
- **Planned-risk violations: 0.** Every R3 / R4 entry has planned risk <= min($1,000, remaining daily budget), and its
  size equals the logged N.
- Every ACCEPT and RISK_REJECT (R3 2 rows, R4 10 rows) recomputed with (stop ticks + 2) x $5 x N + $5.74 x N:
  decision, N and estimate all MATCH. RISK_REJECT: R3 1 (Oct 30 09:05, 333 ticks); R4 2 (Oct 30 09:05, 333 ticks; Oct 30
  12:32, 209 ticks). None was shrunk.
- **RISK_BREACH_FILL (listed, counted, not judged): R3 0, R4 3**: Oct 29 JOFT-20251029-05249 (stop 14:36:20.990);
  Oct 31 JOFT-20251031-06763 (stop 09:14:43.129); Nov 3 JOFT-20251103-07811 (stop 11:25:17.994). See finding F1.

### P5 Fill mechanics: **PASS** (18 of 18 MATCH)
Every trade of R1-R4 was recomputed from the tape by code written for this check (not the engine's exit code): entry =
best ask (long) / bid (short) at the bar close + 250 ms; target = first trade 1 tick through, filled at the target; stop =
first trade at or beyond the stop, filled 1 tick beyond that trade (v3.5 gap-through); same timestamp = stop;
commission $2.87 per side. Sample: 18 trades, both sides, 13 stops, 5 targets, 2 gap-throughs. A same-tick stop + target
did not occur in these days; the rule is covered by `test_same_timestamp_stop_and_target_is_stop` (passes).

| strat | trade | side | N | entry (bar close + 250 ms) | entry px | stop | target | exit | exit time | exit px | gap | result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | JOFT-20251022-00153 | S | 1 | 10-22 08:34:00.250 | 25196.00 | 25225.50 | 25119.75 | STOP | 08:39:51.640 | 25225.75 | no | MATCH |
| R1 | JOFT-20251022-00202 | S | 1 | 10-22 09:14:00.250 | 25224.00 | 25242.25 | 25184.50 | STOP | 09:19:14.802 | 25242.50 | no | MATCH |
| R1 | JOFT-20251030-05681 | S | 1 | 10-30 08:33:00.250 | 26068.00 | 26095.75 | 25990.00 | TARGET | 08:36:46.644 | 25990.00 | no | MATCH |
| R1 | JOFT-20251031-06633 | S | 1 | 10-31 08:46:00.250 | 26094.50 | 26134.00 | 25575.75 | STOP | 09:36:18.546 | 26134.25 | no | MATCH |
| R1 | JOFT-20251103-07390 | S | 1 | 11-03 08:38:00.250 | 26189.50 | 26211.75 | 26150.00 | TARGET | 08:50:00.137 | 26150.00 | no | MATCH |
| R1 | JOFT-20251103-07429 | S | 1 | 11-03 08:51:00.250 | 26132.25 | 26159.00 | 26012.75 | STOP | 11:57:23.847 | 26159.25 | no | MATCH |
| R1 | JOFT-20251103-07751 | S | 1 | 11-03 12:22:00.250 | 26143.50 | 26152.75 | 26129.75 | STOP | 12:25:12.410 | 26153.00 | no | MATCH |
| R2 | JOFT-20251030-05780 | S | 1 | 10-30 09:05:00.250 | 26100.00 | 26183.00 | 25963.75 | TARGET | 14:05:18.715 | 25963.75 | no | MATCH |
| R2 | JOFT-20251103-07485 | S | 1 | 11-03 09:16:00.250 | 26109.00 | 26156.25 | 26012.75 | STOP | 11:51:10.868 | 26156.50 | no | MATCH |
| R3 | JOFT-20251103-07485 | S | 1 | 11-03 09:16:00.250 | 26109.00 | 26156.25 | 26012.75 | STOP | 11:51:10.868 | 26156.50 | no | MATCH |
| R4 | JOFT-20251029-05249 | L | 1 | 10-29 14:19:00.250 | 26189.50 | 26152.50 | 26261.50 | STOP | 14:36:20.990 | 26152.00 | YES | MATCH |
| R4 | JOFT-20251030-05930 | S | 2 | 10-30 09:56:00.250 | 25995.25 | 26013.00 | 25954.75 | STOP | 09:58:10.258 | 26013.25 | no | MATCH |
| R4 | JOFT-20251031-06724 | L | 4 | 10-31 08:52:00.250 | 26110.25 | 26100.75 | 26176.50 | STOP | 08:54:18.068 | 26100.25 | YES | MATCH |
| R4 | JOFT-20251031-06763 | L | 3 | 10-31 09:13:00.250 | 26101.75 | 26086.00 | 26142.50 | STOP | 09:14:43.129 | 26085.75 | no | MATCH |
| R4 | JOFT-20251103-07534 | S | 2 | 11-03 08:55:00.250 | 26135.75 | 26157.25 | 26095.00 | TARGET | 09:05:55.045 | 26095.00 | no | MATCH |
| R4 | JOFT-20251103-07680 | S | 1 | 11-03 10:01:00.250 | 26074.75 | 26112.50 | 26012.75 | STOP | 10:56:59.487 | 26112.75 | no | MATCH |
| R4 | JOFT-20251103-07811 | L | 5 | 11-03 11:20:00.250 | 26128.25 | 26118.25 | 26151.00 | STOP | 11:25:17.994 | 26118.00 | no | MATCH |
| R4 | JOFT-20251104-08968 | S | 1 | 11-04 09:30:00.250 | 25862.75 | 25894.25 | 25798.50 | TARGET | 09:55:37.564 | 25798.50 | no | MATCH |

Ledger and recompute agree on every entry price, exit reason, exit time (to the ms) and exit price. The quote row used for
each entry is in `phase1_checks.md`.

### P6 Context mechanics: **PASS**
On all 10 days the S1.4 `PLAN_ACTIVE context=` equals the frozen plan (`context=`, `market_context`), and context_source,
draw_status and invalidate_below / above are those of the frozen plan (they are read from it unchanged). **Context
switches: 0.** No `PLAN_CONTEXT_CHANGE` row on any day. Independent check on the 1-minute closes after 08:25 CT on the
three days with a line (Oct 27, 29, 31, BULLISH, invalidate_below 25394.25): longest run of closes below the line = 0
(3 are needed), so no switch was due.

| day | market_context | PLAN_ACTIVE | context_source | draw_status | invalidate_below | switches |
|---|---|---|---|---|---|---|
| Oct 22 | BALANCED | Balanced | NONE | NONE | - | 0 |
| Oct 23 | BALANCED | Balanced | NONE | NONE | - | 0 |
| Oct 24 | NONE | None | NONE | NONE | - | 0 |
| Oct 27 | BULLISH | Bullish | HTF_ACCEPTANCE | ACTIVE | 25394.25 | 0 |
| Oct 28 | BALANCED | Balanced | NONE | NONE | - | 0 |
| Oct 29 | BULLISH | Bullish | HTF_ACCEPTANCE | ACTIVE | 25394.25 | 0 |
| Oct 30 | BALANCED | Balanced | NONE | NONE | - | 0 |
| Oct 31 | BULLISH | Bullish | HTF_ACCEPTANCE | ACTIVE | 25394.25 | 0 |
| Nov 3 | BALANCED | Balanced | NONE | NONE | - | 0 |
| Nov 4 | NONE | None | NONE | NONE | - | 0 |

**Closest approach to the line (Kyron's check, Nov 5).** A context can switch only on a day whose plan has an
`invalidate_below=` or `invalidate_above=` line. Of the 10 plans, only Oct 27, 29 and 31 have one; the other 7 have
neither, so S1.4 has no counter to run (`UpdatePlanState` skips a NaN line). On the 3 days, the buffered line is
`invalidate_below=25394.25` (composite VAH 25394.75 minus 2 ticks); a switch needs 3 consecutive 1-minute closes
**strictly below** 25394.25 (a close on the line resets the count). Bars: the run's `nq_1m.csv` (CT, bar end time), from
the first bar after PLAN_ACTIVE (08:26 CT) through 16:00 CT (455 bars a day; the 08:26-15:00 window gives the same values).

| day | context | buffered line | lowest 1-minute close | at (CT) | distance above the line | closes strictly below | longest run below | qualifying 3-close sequence |
|---|---|---|---|---|---|---|---|---|
| Oct 27 | Bullish | below 25394.25 | 25808.50 | 08:36 | 414.25 pts | 0 | 0 | none |
| Oct 29 | Bullish | below 25394.25 | 26068.00 | 13:43 | 673.75 pts | 0 | 0 | none |
| Oct 31 | Bullish | below 25394.25 | 25892.50 | 12:37 | 498.25 pts | 0 | 0 | none |
| Oct 22, 23, 28, 30, Nov 3 (Balanced); Oct 24, Nov 4 (None) | - | no line | - | - | - | - | - | cannot switch |

**Confirmed: no qualifying 3-close sequence strictly beyond the buffered line occurred on any day where a context could
switch**, which agrees with 0 `PLAN_CONTEXT_CHANGE` rows.

### P7 Day sheets: **PASS (produced); Kyron's chart check pending**
`day_sheets/day_sheet_<day>.md` for all 10 sessions: plan context line; every zone (lo, hi, label, class, long, short);
R4 candidates that passed the S1.4 gates with T8 / L1 / FZ1 (logged) / RH1 / risk-check outcome; plan-zone candidates that
failed a gate, counted by zone, direction and first gate reason; every R1-R4 trade with entry / stop / target / exit
times and prices. No P&L column. **For the chart check: Oct 22, Oct 29, Oct 31.**

### P8 Bug list: **PASS: 0 calculation or timing errors found**
No fix was made to any calculation, so no Phase 1 rerun is needed. Changes in this phase (none changes a rule, a
threshold or a trade):

| # | Change | Type | Commit |
|---|---|---|---|
| 1 | `book1a/run_r3.py`: R3 as a script (the Phase 0 inline P0.12 call, same calls) | tooling | bb97bb4 |
| 2 | `book1a/phase1_checks.py`: P1, P3-P7 checks and day sheets | tooling | bb97bb4 |
| 3 | `.gitignore`: `book1a/Phase1/runs/` (ledgers never committed) | housekeeping | bb97bb4 |
| 4 | The two new scripts moved to the `book1a/` package path in git (Windows case folding had filed them under `Book1A/`) | packaging | ffa85a2 |

## 3. Findings (reported; nothing changed)

- **F1, planned vs filled stop distance.** The C3 check measures stop ticks from S1.4's entry reference (the signal bar),
  as frozen ("planned stop from the entry reference"); the order fills 250 ms later at the bid / ask. On the 3
  RISK_BREACH_FILL trades the fill was further from the stop than the reference: 05249 145 ticks planned, 148 from the
  fill, plus a gap-through stop; 06763 55 / 63; 07811 36 / 40. That is what RISK_BREACH_FILL is there to record. Using the
  fill would be a rule change, so it is not made. Kyron to note for the Phase 4 execution-breach gate.
- **F2, R1 on v3.5 has no harness cross-check.** `check_a0` (the Book 1 fills_model gate) runs only under v3.4 (E14), so on
  v3.5 the "check_a0 problems 0" line is not a check. P5's independent recompute covers R1 instead.
- **F3, the candidate log's risk columns are per candidate.** `R4_candidates.csv` risk_decision / risk_contracts check each
  candidate on its own (before the day's trades, halts and the one-position rule); the orders R4 actually sent are in
  `R4_attempts.csv`. The day sheets say so.
- **F4.** The R4 risk-event file (`R4_risk_events.json`) carries realized dollar amounts beside each RISK_BREACH_FILL. The
  runner opened it once while listing the run outputs; the amounts are not used or repeated anywhere (access log event 9).
  The check script does not read it.

## 4. Location diagnostic, Nov 17-19, 2025 (diagnostic only; never counts, never tunes the map)

Plans: the frozen hand-check-pack plans (`Book1A/Phase0/hand_check_pack/plans/`, plan-v2.4-book1a-v1.6, sha256 in
`plan_hashes_2026-11-05b.md`). Jeron's locations as Kyron gave them (Part 1 transcript, video times); the transcript
segments were read to confirm what each location is (no prices are added from it). **Every input was available before
08:10 CT on all three days:** the latest available_at / formed / confirmed time in each sidecar is 08:10:00 CT (Nov 17:
25 time stamps; Nov 18: 37; Nov 19: 39), the REJ swings formed on Nov 17-18, and the lookahead audits pass.

| # | Day | Jeron's location | Purpose / side | Our nearest object (class, sides) | Overlap | Same purpose | Side allowed | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | Mon Nov 17 | long on the reclaim into weekly value at the VAL, entry about 25,085 (00:17:32) | decision, long | `D_ONTVAL_WKTVAL` 25105.00-25115.00 (DECISION, long ANY); the WKVAL level itself is in `T_D_PD2TPOC_ONVAL_WKVAL` 25072.50-25082.75 (TARGET) | 0 pts: decision zone 20.00 pts above; WKVAL target zone 2.25 pts below | no (his entry level is a TARGET zone for us) | n/a | **MISS M1** |
| 2 | Nov 17 | TP1 the nearest rejection, about 25,175 | target | `PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL` 25130.00-25183.50 (DECISION, long / short NONE by C3, 216-tick stop); the `D_ONTVAL_WKTVAL` long ladder TP2 = 25175.00-25185.00 | inside both | yes via the ladder TP2; the zone itself is a decision zone | n/a | match |
| 3 | Nov 17 | TP2 the high-volume heavy-selling area 25,222-25,247 | target | `T_DELTA_SELL_WK` / `T_DELTA_SELL_ON` 25215.00-25225.00 (TARGET); MAP4 `WKPOC_AREA` 25220-25255 (map area) | 3.00 pts (25222-25225); MAP4 area 25.00 pts | yes | n/a | match (thin) |
| 4 | Nov 17 | runner to the weekly VAH (00:17:32-00:20:30) | target | no current-week VAH object: Monday's developing week is the overnight only (wkvah_state INSIDE); prior week `T_PWKVAH` 25759.00-25769.00; ladder RUN 25288.25-25298.25 | not measurable (no price given) | - | n/a | **MISS M2** |
| 5 | Tue Nov 18 | short area 24,823-24,863: weekly VAL accepted below + daily VAH + VWAP + overnight rejection (00:34:58-00:42:23; 1D_01) | decision, short | `D_ONVAH_WKVAL_ONTVAH` 24846.25-24864.75 (DECISION, short ANY, long INITIATION); `T_HTFPOC` 24822.50-24832.50 (DECISION, both ANY) | 16.75 pts (24846.25-24863.00) and 9.50 pts (24823.00-24832.50) | yes | yes (short ANY; wkval_state BELOW = his "accepted below") | match; parts: see M3 |
| 6 | Wed Nov 19 | open on POC + high-volume node + VWAP, long (01:03:00) | decision, long | `D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA` 24687.50-24777.50 (DECISION, long / short NONE by C3, 362-tick stop); session VWAP at 08:10 = 24611.63, inside `ONPOC_AREA_D_PDSET_ONPOC` 24590.00-24615.00 (DECISION, long ANY) | price not given; POC zone and VWAP are 76 pts apart | yes (decision) | **no** on the POC zone (risk); yes on the VWAP zone | **MISS M4** |
| 7 | Nov 19 | long through the daily VAH toward the weekly VAH (01:03:00-01:10:33) | target | daily VAH in `T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH` 24779.75-24837.00 (DECISION, both NONE by C3); weekly VAH in `T_D_WKVAH_PD3VAL` 24972.25-24983.50 (TARGET) | weekly VAH target present | yes (weekly VAH is a target) | n/a | match |
| 8 | Nov 19 | later short at the weekly VAH + double distribution (01:21:35-01:25:10) | decision, short | weekly VAH only as `T_D_WKVAH_PD3VAL` (TARGET); no weekly double distribution on Nov 19 (weekly_dd: 3 HVN blocks, no split; E27) | target zone present, no decision zone | **no** | **no** short decision | **MISS M5** |

**Misses (findings; the map is not changed for them):**
- **M1 (Nov 17 entry).** His decision level (weekly VAL) is a TARGET zone for us; our decision zone is 20 points higher.
  On a Monday our developing weekly profile holds only the overnight (Sunday 17:00 to 08:10 CT), so WKVAL equals ONVAL;
  his weekly profile on Monday is likely a longer window. Which weekly window is meant is not settled in the AMT doc.
- **M2 (Nov 17 runner).** No current-week VAH on the Monday plan (same cause as M1); his price is not given.
- **M3 (Nov 18 parts).** The zone overlaps and carries the weekly VAL (accepted below) and VWAP +1 sigma (24856.07).
  Session VWAP itself was 24774.35 at 08:10, about 49 points below the area; his VWAP remark comes after the open. His
  "daily profile" is a multi-day profile; our zone has the ON VAH, not a PD VAH. The overnight selling shows as the
  `T_DELTA_SELL_WK` / `_ON` bands 24820.00-24845.00 (TARGET); there is no REJ zone there.
- **M4 (Nov 19 open).** Our POC / HVN decision zone is 90 points wide (stop 362 ticks), so C3 sets both sides to NONE.
  The VWAP zone is a different, narrower decision zone 76 points lower. Without his price we cannot say which he meant.
- **M5 (Nov 19 short).** Weekly VAH is a target only, and the weekly double distribution does not form on Nov 19 (E27,
  accepted), so no short decision zone exists there.

## 5. CVD definition check (Book 1D P4): moved to Phase 1b
Not run: CVD_DIV is not built. Kyron (Nov 5): build it from the results-free spec in `K:\Book1A_runner\specs_no_results\`
in Phase 1b, then list every CVD_DIV event on Oct 24, 27, 28, 29, 2025 (time, price, swing pair, case, AT_ENTRY /
PROVISIONAL / POST_ENTRY) for Kyron's comparison with Jeron's video.

## 6. Diagnostics status

| Diagnostic | Status |
|---|---|
| M-J1, M-J2 (U4) | NOT BUILT (Phase 1b) |
| Exit cue (a) | NOT BUILT (Phase 1b) |
| L2 E1 / E2 / E4, NOT_VISIBLE / DATA_MISSING | NOT RUN (U11) |
| CVD_DIV, BREAKOUT_SPEED | NOT BUILT (Phase 1b); columns `null` in the candidate log |
| GEX V2 / V3 / V5, volatility control, context GEX tags | NOT BUILT (Phase 1b) |
| 10 NQ and MNQ feasibility | NOT BUILT (Phase 1b); formula ready in `risk.py` |
| Wide-zone eligibility report | NOT BUILT for this run (Phase 1b; the Phase 0 report is `Phase0/wide_zones/`) |

## 7. Blinding
- Session start showed only the runner's CLAUDE.md and its own commit. No Book 1 file outside `K:\Book1A_inputs` was
  opened; no git ran in the Book 1 repository; nothing in `K:\Book1A_checker\` was read, linked or written.
- Access log event 9 (`Book1A/Phase0/P0.1_blind_run_setup.md`): a code search printed Book 1's Phase 0 NT parity reference
  lines from `book1_ref` (Gate 1 counts); the replay plan's two in-sample C1 R totals were seen again (already event 5).
  Neither was used. Searches now exclude `book1_ref/`. F4 above (own run's dollar amounts in the risk-event file).
- Commit subjects carry no results.

## 8. Ledger sha256 (for the Phase 1b byte-identical test)

| file (under `book1a\Phase1\runs\`) | sha256 |
|---|---|
| `phase1/R1_A0_full.csv` | b4a2108fa2ab531ef84e1a2933d05fafb8e4519f6674ee8857f0cd79c344b21c |
| `phase1/R2_C1_full.csv` | 6123f88e7a62242b559e89a385b7749e67d6d2d433108cb839524a37c606842e |
| `phase1/checker_input/R1_A0.csv` | 4a7c1fe8224cd2e7ea828fa0476a3917fad9ee71a6538a3d1717529e91df97ab |
| `phase1/checker_input/R2_C1.csv` | 69b3f158d9037196d240e571227431760597829158750d81bcfc1239886a6cdc |
| `phase1/R1_attempts.csv` | 3106db5339fdbf73a2e5be09d8366024134f3192d594c598b86cc89b088f43b5 |
| `phase1/R2_attempts.csv` | 8230d1f8caba57d85a26bfee47e0dc592b9c94143e1f90d40d1f228280ad1f20 |
| `phase1/fills_model.csv` | 971420ae5d37fa9225de7a55d7b4ebfd5133a91c9da925b1eb0233cdbf203993 |
| `phase1_r3/R3_M0_ledger.csv` | b8ca24053d62c9b53846e585270c13225e12eb217266d7b9a2bd96af9ee4958f |
| `phase1_r3/R3_attempts.csv` | b6a16a525c91fe34b9f5576542687723ff1b3bb74acbca732387b8ea913d20d2 |
| `phase1_r4/R4_M0_ledger.csv` | 6daed6d5252d03eb77ea0612da58a2c2ab130c86394fc29ecb6639f464ea495d |
| `phase1_r4/R4_attempts.csv` | ea7aea61743a6a12c7902adac235adb1a6df38691f23d58240f1cbea60566bdb |
| `phase1_r4/R4_candidates.csv` | 6242af04048d46c301d8c224b3d711bbe6582dc6c78b7c2312b984cbcb34e61d |

(`phase1/checker_input/` here is the run folder's own sub-folder, written by run_r1_r2; nothing went to
`K:\Book1A_checker\`.)

## 9. Step 0, Drive copies
Already in Drive before this session (uploaded Nov 6 02:02 UTC), checked by listing each folder by its ID:
- Book 1A Phase 0 - Parity (`1YJ9ULz3bnqUZU3qYiWbq4HO6bsVWhtJC`): `hand_check_sheet_independent_recompute.md`
  100,764 bytes = local.
- Book 1A Scripts (`1B1Gu_6dbBfoodhylA-irvE3sK3RZW5kY`): `Book1AHandCheckMarks.cs` 29,779 = local (v1.1);
  `Book1A_VP_check.pine` 12,182 = local; folder `independent_recompute`. Listing that sub-folder was blocked by the
  session's permission check, so `rc.py` (9,806), `day.py` (3,066) and `compare.py` (19,933 bytes local) are **not
  confirmed** by the runner. Kyron to check.

## 10. Next
1. **Kyron: chart check of 3 days**, Oct 22, Oct 29 and Oct 31 (the Phase 0 hand-check days), with
   `day_sheets/day_sheet_2025-10-22.md`, `-10-29.md`, `-10-31.md`: zones, gate / veto reasons and the trades' entry /
   stop / target / exit times and prices.
2. Kyron: place the results-free diagnostics spec in `K:\Book1A_runner\specs_no_results\`.
3. **Phase 1b:** build the diagnostics (logged only), rerun Phase 1 with them on, show the R1-R4 ledgers byte-identical
   to section 8, then the CVD definition check (section 5) for Kyron's comparison with Jeron's CVD video.
4. Kyron tags after the hand check. Phase 2 only after Phase 1b and Kyron's go.
