# Book 1A Phase 4 registration (replay, in-sample, run once)

Written Nov 9, 2026 (Step A), before any Phase 4 trading run. Kyron's instruction of Nov 9, 2026: finish Book 1A
without step-by-step approvals, taking the replay plan's defaults and the runner's recommendations; the runner tags
`book1a-phase4-frozen` before any Phase 4 run. Phase 3 closed: G1-G5 met (G4 PASS by the checker, Nov 9, bridge
3899703e), tag `book1a-phase3-results` at be8efd2. Nothing in this file comes from a Phase 4 result; no Phase 4 trading
run has been made. Phase 1 outcomes are not used for anything; Phase 2 and Phase 3 results changed no rule, threshold or
comparison (Phase3_registration.md section 6). New ideas go to `Book1A/Block2_candidates.md` only.

Controlling doc: replay plan, results-free copy supplied by the checker (`Book1A/specs/Book1A_replay_plan.md`, sha256
`7044bcc22cde41c48430d7a746f6628025d986e07ae8ab79092935fdd02db257`, as used in Phase 3). Drive doc
1tjkYvdg2zr1OvOT0crP40ACCQEHDqNEgCLCNu314IiU: modifiedTime 2026-11-08T23:47:55Z (metadata read Nov 9, content not read:
the Drive original holds Book 1 results). That time fits the checker's Nov 8 section 8 update. **Runner decision 1:** use
the results-free copy as the controlling text (the Drive original cannot be read under the blinding rules); any later
Drive edit is the checker's to bring into the copy.

Files: sessions, contracts, exposure and input checks `Book1A/Phase4/phase4_sessions.md` / `.csv`; plans
`Book1A/Phase4/plans_phase4/`; plan hashes `Book1A/Phase4/plan_hashes_phase4.md`; Step B scripts
`Book1A/Phase4/stepB/`.

## 1. Frozen configuration

| item | frozen value |
|---|---|
| Code | the commit that adds this file, tagged `book1a-phase4-frozen` by the runner (Kyron's pre-authorization, Nov 9). Step B runs from a clean checkout of that commit: before each step `git status` must be clean and `git rev-parse HEAD` must equal the tag's commit exactly (`Book1A/Phase4/stepB/*.sh`, recorded in `runs/stepB_head_*.txt`); every run manifest records the commit. |
| Sessions | Feb 5 - Apr 21, 2026, Book 1 calendar: **52 sessions** (no cash session Feb 16 Presidents' Day and Apr 3 Good Friday; no half day). Exposure: section 1.1. |
| Inputs | `BOOK1_ROOT = K:\Book1A_inputs` only; harness `K:\Book1A_inputs\jeron_harness\build\JeronHarness.exe`; tapes `<BOOK1_ROOT>\tapes` as is (`run_r1_r2.phase_tapes_dir`: no cut tape outside Phase 3; the Feb 4, 2026 tape there is the full one). |
| Front contract | NinjaTrader roll **Mar 16, 2026**: **NQH6** ("NQ MAR26") Feb 5 - Mar 13 (26 sessions), **NQM6** ("NQ JUN26") from Mar 16 (26 sessions). Mar 16 is a roll day (a session; plan check A LOG_ONLY as frozen). The harness `--instrument` label is one per phase (`run_r1_r2.labels_for(last session)` = NQ JUN26), a label only, as in Book 1. Each session's front is checked against the data-integrity table row the Book 1 backtest used (section 1.2). |
| Plans | the 52 Book 1A plans built in Step A (`plan-v2.4-book1a-v1.6`, map v2.3 packets, frozen plan code, `book1a.build_plans_phase --phase phase4`, unchanged: its `--phase` option already accepted phase4), sha256 in `plan_hashes_phase4.md` (git LF content sha256 `b3b5c82279c6c22861cf702d79368e362b8a02ab75cc3b826fb5ecbc799b2f00`). R4 loads exactly these files. |
| R1 A0 | unchanged: Book 1 S1.4 defaults, map v2.3, rules-only plan, no veto, exit M0, qty 1. `python -m book1a.run_r1_r2 --phase phase4 --fill v3.5 --block1 K:\Book1A_inputs --out book1a\Phase4\runs\phase4` |
| R2 C1 | unchanged: A0 + veto FZ1 or L1 or T8, RH1 retest 15 bars / 2 ticks, M0, qty 1 (same run). |
| R3 C1 + risk | unchanged: R2 signals + C3 risk check **risk-c3-v2**. `python -m book1a.run_r3 --block1 K:\Book1A_inputs --a0-run book1a\Phase4\runs\phase4 --out book1a\Phase4\runs\phase4_r3` |
| R4 Book 1A | **the Phase 3 final configuration, unchanged (replay plan section 6: "Phase 4 replay: R1–R4 once, frozen"): Book 1A plans + S1.4, veto L1 or T8 (FZ1 logged only), RH1, exit M0 fixed (E1), risk-c3-v2.** `python -m book1a.run_r4 --block1 K:\Book1A_inputs --a0-run book1a\Phase4\runs\phase4 --plans book1a\Phase4\plans_phase4 --phase phase4 --out book1a\Phase4\runs\phase4_r4 --candidate-days <all 52>` |
| Not run | no C2 run, no MAP4 comparison, no comparison added; the Phase 3 primary comparisons (P1-P3) are not rerun (they are Phase 3's, replay plan section 9). |
| Fill model | **v3.5 for all four** (as Phase 3). |
| Costs | round trip NQ $5.74 (MNQ $1.88 only in the MNQ feasibility diagnostic). |
| U3 (R3, R4) | $100,000 simulated balance; $1,000 per trade; $2,000 daily loss limit; NQ only, whole contracts, minimum 1 NQ; RISK_REJECT never shrunk; 2-tick allowance in the pre-trade estimate only; 3 trades per day and the 2-loss halt. |
| Risk implementation | risk-c3-v2 for R3 and R4, written on every R3 / R4 ledger row. |
| Bootstrap | session bootstrap, seed **20251205**, B = 10,000; lower bound = 5th percentile (Book 1's convention, Phase3_registration.md section 5). |
| Stress | `python -m book1a.run_stress ... --a0-run book1a\Phase4\runs\phase4 --r4-run book1a\Phase4\runs\phase4_r4 --plans book1a\Phase4\plans_phase4 --stress lat1000 / slip2 / slip4 --out book1a\Phase4\runs\phase4_stress_<setting>` (stress-v1.0, unchanged). Shown separately from the baseline; not part of the gate. |
| Diagnostics | `python -m book1a.diag_phase1b --runs book1a\Phase4\runs --folders phase4 phase4_r3 phase4_r4 --d5-days --plans book1a\Phase4\plans_phase4 --gex K:\Book1A_inputs\gex_levels_block1.csv --inputs K:\Book1A_inputs --out book1a\Phase4\runs\phase4_diag` (diag-phase1b-v1.2, with the 17ac9cd gex_v3 fix). |
| Report code | `phase2_report.py` **phase2-report-v1.2** (`run("phase4", ...)`); `phase2_review_fields.py` v1.3; `phase2_review_apply.py` **v1.3** (`--phase phase4`); `g4_draw.py` **v1.2** (`--phase phase4`); new `phase4_gate.py` (phase4-gate-v1.0, section 5); new `mj_steps.py` (mj-steps-v1.0, section 4). The phase4 additions change no rule: each module is generalized only by the phase argument (phase2 / phase3 behaviour unchanged; their tests pass). Tests: `tests/test_phase4_phase_arg.py`, `tests/test_phase4_gate.py`, `tests/test_mj_steps.py`; four existing tests that used "phase4" as the example of a refused phase (three in `test_phase3_phase_arg.py`, one in `test_phase2_review_fields.py`) now use "phase5". |
| Labels | every result is "replay (in-sample)". Never "validation". Phase 4 is not a holdout for Book 1A (replay plan section 2). |

### 1.1 Exposure (replay plan section 8)

No confirmed video date falls in Feb 5 - Apr 21, 2026. Part 5 ("45 Days Using This") is listed "About Apr 2, 2026
(approximate, not confirmed as a trading date)", Part 6 ("Order Flow and GEX Levels") "About Apr 9, 2026", both with
excluded sessions "Unresolved"; the plan says unresolved dates are "treated as excluded until checked". **Runner
decision 2 (most conservative, before any run):** every session of the trading week of each approximate date is
**EXPOSED**: Mar 30, Mar 31, Apr 1, Apr 2 (Part 5; Apr 3 Good Friday) and Apr 6-10 (Part 6), **9 EXPOSED, 43
UNEXPOSED**. A week, not a single day, because the dates are approximate (as the Part 1 and Part 2 rows exclude weeks).
Videos with no date at all (Part 4, Strategy In 30 Minutes, the webinar, 60k Profit) cannot be placed and flag no
session. The exposure set is in `phase4_sessions.EXPOSED` and `phase2_report.EXPOSED_BY_PHASE["phase4"]` (tested equal).

### 1.2 Data conditions registered before any result (inputs only, `phase4_sessions.md`)

All **52 sessions OK**: Databento raw MBO file (the one the Book 1 backtest used), a tape ending after the 15:00 CT
close (largest RTH gap between trades 8.2 s), complete NQ / ES 1-minute RTH bars (390 / 390 every session), an ok GEX
row, GEX V3 reproduction Y on all 52 (`runs/gex_v3_stepA`), a map packet (no packet gaps or notes) and a plan. Every
session's front by roll equals the data-integrity table's main and NinjaTrader contract (NQH6 Feb 5 - Mar 13, NQM6 from
Mar 16; on Mar 16 and Mar 17 the row used is the NQM6 roll file `raw/block1/nq_roll_NQM6_mbo_20260315_20260317`). Tape
price basis: first RTH tape trade minus the 08:31 bar open between -0.50 and 0.00 points on every session (the tape and
the bars are the same contract). GEX price basis: the frozen GEX front is NQH6 on the Mar 16 and Mar 17 rows (volume of
Mar 12 and Mar 13) while the NinjaTrader front is NQM6; their nt_shift_pts (211.5 and 215.5) map the levels to the
chart contract, unchanged (as Dec 15-16 in Phase 3); every other row has front = nt_contract and shift 0. **Databento
condition "degraded" on Mar 16 (roll file) and Apr 10, 2026**: logged, not DATA_MISSING (decode OK, no gap over 60 s,
used by the Book 1 backtest; runner decision 6). Plans review=LOG_ONLY, as frozen: Feb 25, Feb 26 (Z3 balance POC),
Mar 10 (check C: 1 NQ does not fit), Mar 11 (Z3; check C), Mar 16 (check A roll day), Mar 17 (check C), Apr 7 (Z3;
check C). Calendar events are logged in `phase4_sessions.md` (the plan applies its own rules, e.g. the 08:30-08:40
no-trade windows, FOMC Mar 18 no-trade 12:45-15:00). No half day in Phase 4, so the Phase 3 EXIT_AFTER_SESSION_CLOSE
case does not arise.

## 2. Report card (R1-R4)

The Phase 2 / Phase 3 definitions apply unchanged (Phase3_registration.md section 2), with Phase 4's populations: **ALL**
= the 52 sessions; **UNEXPOSED** = the 43 sessions without the 9 of section 1.1. Reported separately, **never pooled**,
both "replay (in-sample)". Same report card (phase2_report.run("phase4", ...)): trades, net R per session, 90% CI, win
rate, average win / loss, max drawdown (trade order from a peak of 0; dollars for R3 / R4; the SUPPLEMENTAL session-order
drawdown), exit reasons, RISK_REJECT by reason, execution breaches, RISK_BREACH_FILL, stress at 1,000 ms and 2 / 4 ticks
(shown separately), gamma regime and time-of-day splits, the daily table; R4 by `mj_alignment` (A4 split, descriptive).

## 3. What-fails-and-why review (R1-R4, every trade)

Exactly Phase3_registration.md section 3, through `phase2_review_apply.py --phase phase4` (same frozen functions; plan
sidecar sha256 must equal `plan_hashes_phase4.md`; numeric GEX tags by tercile of one value per session over the 52 Phase
4 sessions; CVD_DIV with the fidelity note).

## 4. Section 5 diagnostics in Phase 4

Same statuses as Phase 3 (Phase3_registration.md section 4), except C2: **NOT_RUN in Phase 4** (C2 is a Phase 3 location
diagnostic; replay plan section 6, Phase 4 = R1-R4 once). Exit steps (C5): M-J1 and M-J2 per trade (diag_exit_trades)
**and, new as a report of existing outputs, as session net R beside M0** (`mj_steps.py`, mj-steps-v1.0, its docstring is
the definition): per trade the ledger's own R formula on the M-J exit legs (same entry, initial stop, fills, commissions,
U4); where a step does not apply (no ladder; M-J2 on 1 NQ or no TP1 beyond entry) the trade keeps the previous step's
exit; net R per session, CI and drawdown by the report card's `core`; ALL and UNEXPOSED; M-J2 also by size bucket (2, 3,
4+ NQ). R1 / R2 / R3 plans carry no ladder, so every step equals M0 for them (shown as such). Run for Phase 4 and, with
the same code, for Phase 3 (R4 and R1, Phase 3 diag `phase3_diag_17ac9cd`), so the two phases are reported side by side.
**Runner decision 3:** the "previous step's exit when the step does not apply" rule is the only definition that keeps
every session's trades in the series (the plan says "each step is compared with the one before"); chosen before any
Phase 4 result. Diagnostic only: R4 is fixed at M0 (E1); a promising step is a Block 2 candidate, never a change to R4.

**Exit cue (a) as session net R (Kyron's addendum, Nov 9):** the same file and code give a CUE_A series beside M0 (not a
step in the M-J chain): where `cue_fired` = Y the whole position exits at `cue_exit_price` (diag_phase1b: market exit
250 ms after the trigger bar's close), otherwise the M0 exit is kept; for R4 and R1, Phase 3 and Phase 4.

**Pause trigger (b) (Kyron, Nov 9, with the addendum):** the runner pauses and reports, changing nothing, if M-J1, M-J2
or CUE_A gives a higher net R per session than M0 for R4 or for R1 in **both** Phase 3 and Phase 4 (population ALL).
For R1 the M-J steps equal M0 by construction (no ladder), so only CUE_A can trigger for R1.

## 5. Phase 4 replay rule (gate for R3 and R4) and go / no-go

Replay plan section 9, verbatim: "**Phase 4 replay rule:** the Book 1 holdout rule: net R per session above 0 with the
90% bootstrap lower bound above −0.1 R; max drawdown within 1.5× the Phase 3 drawdown of the same configuration; any
planned-risk violation (a trade entered with planned risk above the per-trade budget or the remaining daily budget) is
an automatic fail (E3). Execution breaches (a realized loss above plan from a gap or a slipped stop) are reported as a
count and the largest dollar overrun, against a provisional research gate frozen before the run: fail if more than one
execution breach, or any single overrun above 25% of the daily limit. The live account's own limits replace this gate
later."

Implementation (`book1a/phase4_gate.py`, phase4-gate-v1.0, tested on synthetic ledgers only), for R3 and R4 each:

1. net R per session > 0 (session net R = sum of the session's trade `realized_net_R`, 0 for a session without trades;
   mean over the population's sessions);
2. 90% session-bootstrap lower bound > -0.1 R (seed 20251205, B = 10,000, 5th percentile);
3. max drawdown (`max_drawdown_R`, the report card's definition) <= 1.5 x the Phase 3 ALL `max_drawdown_R` of the same
   strategy, taken from `book1a/Phase3/runs/phase3_report_card.json` (sha256
   `bc8a02c40a3a813e4a6c105cfb49a3f9157dc1b235d07d470ea1d166a4311e99`): **R3 4.5862 R -> limit 6.8793 R; R4 5.3103 R -> limit 7.96545 R**. (Kyron's instruction
   quoted R3 as 4.5900 and said to take the exact values from the card; the card says 4.5862.) The gate reads the card
   and stops if it differs from these values;
4. zero planned-risk violations (risk-c3-v2: `planned_risk_usd` above `risk_budget_usd` = min($1,000, remaining daily
   budget at the decision));
5. execution breaches as risk-c3-v2 defines them (change log Nov 6, 2026): a qualifying breach = entry risk at fill above
   `risk_budget_usd` (ledger `exec_risk_breach` 1); fail if more than 1, or if any single overrun (entry risk at fill
   minus `risk_budget_usd`) is above $500 (25% of the $2,000 daily limit). The realized loss overrun (RISK_BREACH_FILL)
   is reported and never counts toward the gate (risk-c3-v2 (2)).

PASS = all five. **Deciding population: ALL 52 sessions.** The same rule on the 43 UNEXPOSED sessions is a sensitivity
only; if the two differ the result is labelled SENSITIVE_TO_EXPOSED_SESSIONS and the ALL result stays the decision.
R1 and R2 are reported (trades, wins, losses, net R per session, CI, drawdown, net $), not gated. Stress results do not
enter the gate.

**Go / no-go for Block 2 (section 9, as written),** recorded in `Book1A/GoNoGo_record.md` after the Phase 4 report:
R4 passes -> Book 1A goes to Block 2 (E4); only R3 passes -> C1 with risk controls goes to Block 2, not Book 1A (C1
includes FZ1, which is not Jeron); both pass -> both go, as separately frozen candidates; neither passes -> no Block 2
data is bought solely for validation; record why, and research on Block 1 diagnostics first. A replay pass is a reason to
test on Block 2, never proof the strategy works. The runner buys no data and starts no Block 2 work in any case.

## 6. Change rule

Phase 4 runs once. Between the freeze and the report only a demonstrable calculation error in diagnostic or report code
may be fixed (narrow fix, unit tests, an old-vs-new check showing nothing else changes, a change-log row and an amendment
here, a separate commit, listed in the report). Anything touching replay, execution, fill, risk or sizing code, a ledger,
a rule, a threshold, a registered comparison or a frozen file stops the phase.

## 7. Phase 4 gate (pass = all of G1-G5; the replay rule of section 5 is reported, not a G gate)

- **G1 Integrity**: every step at the frozen commit, clean tree; plan hashes unchanged from Step A (every R4 ledger and
  candidate row's `plan_sha256` equals `plan_hashes_phase4.md`; the plans rebuilt from the Step B R1 run's own map packets
  are byte-identical to the Step A files; the Step B packets equal the Step A packets without built_local); unit tests
  pass; look-ahead audit clean for R1-R4 (`book1a.audit_run`) and for every AT_ENTRY field (D2 in diag_phase1b); the
  Phase 1, Phase 2 and Phase 3 ledgers unchanged (registered sha256, `stepB/g2_g3_check.py`).
- **G2 Coverage**: 52 / 52 sessions in R1-R4 and every stress run. A missing session is repaired and rerun, or accepted in
  writing by Kyron as a named coverage exception before the gate is decided.
- **G3 Risk**: zero planned-risk violations for R3 / R4; every R3 / R4 ledger row ACCEPT and risk-c3-v2; execution
  breaches reported.
- **G4 Checker reproduction**: the checker independently rebuilds, from the raw tape and the frozen specs with its own
  code, every R4 trade on the fixed days **Feb 11, Mar 4, Mar 17 and Apr 9, 2026**; plus 10 R4 trades from the other 48
  sessions and 10 trades from the R1-R3 ledgers, drawn with seed 20251205 by `book1a/g4_draw.py --phase phase4`
  (g4-draw-v1.2, both draws always taken); checking entry and exit time, price, reason, size and the risk-c3-v2 numbers,
  and recomputing the report card and the Phase 4 gate arithmetic from the ledgers. Pass = every field matches, or each
  mismatch is traced to a documented calculation error that is fixed, rerun and rechecked. **Fixed days chosen by the
  Phase 3 method, before any run (runner decision 4):** spread over the phase, mid-week, one session with a special input
  condition and one EXPOSED session: Feb 11 (Wed, early, NQH6), Mar 4 (Wed, NQH6, before the roll), Mar 17 (Tue, the
  first full NQM6 session after the roll, GEX nt_shift_pts 215.5: the roll-basis case, as Dec 18 was the 0DTE case in
  Phase 3), Apr 9 (Thu, EXPOSED, Part 6's approximate date). Chosen from the calendar and the input table only.
- **G5 Deliverables complete and hashed**: report, ledgers (R1-R4), review file, gate file, exit-step file, G4 pack.

## 8. Section 12 parameter sensitivity protocol (Step 5, after the go / no-go record; Kyron's addendum, Nov 9)

Run exactly as frozen in replay plan section 12 (quoted there; nothing here adds a value or a threshold). Diagnostic only:
no result changes any frozen value; a promising value is a Block 2 candidate only. Reported in
`Book1A/Phase4/Sensitivity_report.md`. Method as implemented (registered now, before the Phase 4 freeze):

- **Strategy and sessions:** R4 (Book 1A, M0, risk-c3-v2, v3.5) over Phases 2-4, **114 sessions** (21 + 41 + 52), results
  also by phase. **Baseline** = the frozen R4 ledgers: Phase 2 (sha256 478dbb33…), Phase 3 (0e053e6f…), Phase 4 (Step B).
- **One parameter at a time**, every other setting at baseline; **Group B first** (location fidelity, then trades and
  performance), then Group A. Values exactly as section 12 (bold = baseline): A: delta gates 100 / **150** / 200 (10%
  held); RH1 retest window 10 / **15** / 20 bars; L1 distance 5 / **10** / 15 pts; T8 look-back 2 / **3** / 5 bars;
  minimum source families **2** / 3. B: tests before favouring initiation 3 / **4** / 5; swing definition 10 / **15** /
  20 bars; fast departure 0.15 / **0.25** / 0.35 ADR; acceptance time 45 / **60** / 90 min; zone width cap 30 / 40 / 50
  pts; GEX level distance 5 / **10** / 20 / 35 pts.
- **Where each parameter lives and how it is varied** (in memory for the run only, as `stress.py` and `plan_c2.py` do;
  no file of Book 1A or Book 1 is changed): delta gate = the harness S1.4 `MinAbsDelta` strategy setting (MinDeltaPct 10
  held) for a rerun of each phase's A0 strategy run, plus `map_v24.ARRIVAL_MIN_DELTA` (PO-1 arrival, "S1.4 MinAbsDelta")
  for the plans; RH1 = `jeron_engine.arm_replay.RETEST_BARS`; L1 = the `cut` of `jeron_engine.arms.l1`; T8 = the bars
  checked by `arms.t8` (1..k); minimum families = `families.MIN_FAMILIES_FOR_DECISION`; tests = the `tests >= 4` rule
  in `plan_fields`; swing = `map_v24.SWING_BARS`; departure = `map_v24.DEPARTURE_ADR`; acceptance =
  `map_v24.ACCEPT_MINUTES`; zone width cap = `map_v24.ZONE_MAX_PTS` (PO-1 rejection / flip zones, frozen 40); GEX
  distance = `families.GEX_TOLERANCE_PTS`. Plans are rebuilt from each phase's Step A map packets with the frozen plan
  code (as the C2 build); R4 is rerun with `run_r4`'s own replay on the frozen A0 run of the phase (or the delta rerun).
- **Acceptance of the tool (hard check per parameter):** run at the baseline value it must reproduce every phase's plans
  and frozen R4 ledger byte for byte, and a unit test must show the override reaches the code it names. If either fails
  for a parameter, that parameter is NOT_RUN with the cause (no workaround).
- **Reported for each value** (section 12 "Method"): paired daily R vs baseline (per session, 0 when no trade) with the
  90% session bootstrap of the mean paired difference (seed 20251205, 10,000, 5th / 95th percentile), over the 114
  sessions and by phase; trades added / removed / changed and the overlap with baseline (trades matched by (date, signal
  time) and compared as Book 1's `differing_trades`, as in Phase 3); max drawdown (R, trade order from 0); RISK_REJECT
  count and risk-rule failures (planned-risk violations and the section 9 execution-breach gate); results under 1-tick
  (baseline v3.5) and 2-tick stop slippage (the R4 replay rerun with stress-v1.0 slip2, variant and baseline).
  Group B also: location fidelity = the share of Jeron's marked locations **that have a price in
  `Book1A/Phase1/Phase1_report.md` section 4** (Nov 17: about 25,085, about 25,175, 25,222-25,247; Nov 18: 24,823-24,863)
  overlapped by a DECISION zone of the variant's plan that day, and the number of extra decision zones on Nov 17-19 (no
  marked-zone list with prices exists for Nov 24-26 or other screenshots: not measured, stated as such).
- **Classification (section 12, confirmed Nov 1, applied per parameter):** a value is Inconclusive when fewer than 10
  trades differ or its paired interval spans both +0.10 and -0.10 R per session. Parameter label, first that applies:
  **Inconclusive** (every neighbouring value Inconclusive); **Fragile** (a neighbouring value flips the sign of net R
  per session or causes a risk-rule failure); **Sloped** (net R per session changes monotonically across the values,
  no sign flip); **Stable** (both neighbouring values keep the baseline's sign and max drawdown no more than 25% worse);
  otherwise NOT_CLASSIFIED (numbers shown). Neighbours: the values next to the baseline (GEX distance: 5 and 20; 35
  reported; Sloped over all four). Minimum families has one neighbour (3): Sloped needs three values, so it can be only
  Inconclusive, Fragile, Stable or NOT_CLASSIFIED; zone width cap: neighbours 30 and 50 of the frozen 40. Flags beside
  the label: MATERIAL_ELIGIBILITY_CHANGE (20% or more of the baseline's trades change; additions and removals
  separately) and MATERIAL_DRAWDOWN (25% or more worse, % and absolute R). Numbers always shown next to the label. PBO
  not used.
- **Pause trigger (c) (Kyron, Nov 9):** a value of a parameter labelled Stable or Sloped whose paired 90% interval vs
  baseline is above 0 over the 114 sessions (5th percentile > 0) **and** whose mean paired difference is positive in each
  of Phases 2, 3 and 4 separately. Reported; nothing changed; a Block 2 candidate only.

## 9. Runner decisions (also in Book1A/Phase1/change_log.md)

1. Controlling text = the results-free copy of the replay plan (section 0).
2. Exposure: the weeks of the Part 5 and Part 6 approximate dates EXPOSED (section 1.1).
3. Exit steps as session net R: the previous step's exit where a step does not apply (section 4).
4. G4 fixed days Feb 11, Mar 4, Mar 17, Apr 9, 2026 (section 7).
5. Tape price basis check (inputs only, `phase4_sessions.py`): the first RTH tape trade within 50 points of the open of the
   NQ 1-minute bar ending 08:31 CT; the NQH6 / NQM6 spread is about 200 points, so a wrong-contract tape fails it.
6. Data-integrity rows: on Mar 16 and Mar 17 the table has two rows (main NQH6 file, roll NQM6 file); the row the Book 1
   backtest used (`used_by_backtest` True) is the session's row. Databento "degraded" days are a logged condition, not
   DATA_MISSING (decode OK, no gap over 60 s, used by Book 1).
7. Drawdown baselines from the Phase 3 card (R3 4.5862, not the 4.5900 quoted in the instruction).
8. The Step B check scripts are written and committed in Step A (`Book1A/Phase4/stepB/`), so the checks are frozen with
   the code; G3 also requires every R3 / R4 ledger row to be ACCEPT and risk-c3-v2 (a stricter check than Phase 3's).
9. Section 12: parameter label precedence Inconclusive > Fragile > Sloped > Stable > NOT_CLASSIFIED; a value is
   Inconclusive by section 12's own test; minimum families (one neighbour) cannot be Sloped (section 8).
10. Section 12 zone width cap = PO-1's `ZONE_MAX_PTS` only (the PO-1 "Width ... at most 40 points"); the other 40-point
    caps (MAP4, delta bands, DD_EDGE) stay at baseline.
11. Section 12 fidelity uses only the marked locations with a price (Phase 1 report section 4); Nov 24-26 not measured.
12. Section 12 risk-rule failure = a planned-risk violation or a failed section 9 execution-breach gate over the 114
    sessions.
