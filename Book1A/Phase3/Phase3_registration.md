# Book 1A Phase 3 registration (test changes, replay, in-sample)

Written Nov 8, 2026 (Step A), before any Phase 3 trading run. Kyron authorized Phase 3 Step A on Nov 8, 2026, after
the Phase 2 review: G1-G5 met (G4 passed by the checker). Nothing in this file comes from a Phase 3 result; no Phase 3
trading run has been made. Phase 1 outcomes are not used for anything, and Phase 2 results changed no rule, threshold or
comparison (Phase2_registration.md section 5); ideas found after seeing Phase 2 results are in
`Book1A/Block2_candidates.md` (Block 2 development only). Step B starts only after Kyron tags the commit that adds this
file `book1a-phase3-frozen`. The 41 sessions, their close times, front contracts, exposure flags and input checks are in
`Book1A/Phase3/phase3_sessions.md`; the plan hashes in `Book1A/Phase3/plan_hashes_phase3.md` (R4 baseline) and
`Book1A/Phase3/plan_hashes_phase3_c2.md` (C2); the final change list is `Book1A/Phase3/Phase3_change_list.md`.

Controlling doc: replay plan, results-free copy of the Drive version of Nov 6, 2026, 21:15Z, supplied by the checker
(sha256 `ba4a7d5f2801a78f36c6069c082240b72d577166d3a0d0c8b341ec1e6034848f`; it replaced the Nov 1 copy, sha256
`b1c8dcc3df2f2fe97d1473753d16575861f7955174df2ac661b0a6db92ab44f8`), then edited Nov 8 for the section 8 Part 3 row and
its change-log row (results-free copy and repo copy, sha256 `7044bcc22cde41c48430d7a746f6628025d986e07ae8ab79092935fdd02db257`; the checker applies the same text to the
Drive doc). Open items: Drive doc unchanged since Nov 1 (modifiedTime 2026-11-01T17:18:48Z); item N7a added Nov 8 in the
results-free copy (sha256 `ad874b0fa89e01143a3243d0aeab34304b68f3c7e098f764e5f8e4c3ccb19356`).

## 1. Frozen configuration

| item | frozen value |
|---|---|
| Code | the commit that adds this file, tagged `book1a-phase3-frozen` by Kyron. Step B runs from a clean checkout of that tag: before each run `git status` must be clean and `git rev-parse HEAD` must equal the tag's commit (both recorded in the report); every run manifest records the commit. |
| Sessions | Dec 5, 2025 - Feb 4, 2026, Book 1 calendar: **41 sessions** (no cash session Dec 25, Jan 1, Jan 19; Dec 24 half day included, close 12:15 CT). **3 EXPOSED** (Jan 12, Jan 14, Jan 16, 2026: Part 3, replay plan section 8 as updated Nov 8, session level whatever the instrument), **38 UNEXPOSED**. Every other unresolved video has no confirmed date and stays excluded until confirmed; it flags no Phase 3 session. |
| Inputs | `BOOK1_ROOT = K:\Book1A_inputs` only; harness `K:\Book1A_inputs\jeron_harness\build\JeronHarness.exe`; tapes: the phase3 tape folder (`run_r1_r2.phase_tapes_dir`: Book 1's Phase 3 tapes, the Feb 4, 2026 tape cut at 17:00 CT). |
| Front contract | NinjaTrader roll Dec 15, 2025: **NQZ5** ("NQ DEC25") on Dec 5-12 (6 sessions), **NQH6** ("NQ MAR26") from Dec 15 (35 sessions); Dec 15 is a roll day (a session; plan check A LOG_ONLY as frozen). Each session's front is checked against the data-integrity table (`phase3_sessions.md`). The harness `--instrument` label is one per phase (NQ MAR26), a label only, as in Book 1. |
| Plans | the 41 Book 1A plans built in Step A (`plan-v2.4-book1a-v1.6`, map v2.3 packets, frozen plan code, `book1a.build_plans_phase --phase phase3`), sha256 in `plan_hashes_phase3.md`. R4 loads exactly these files. G1 compares the table by its git (LF) content, sha256 `60206aa54fb142cd281530151eac78f1f3c75f674ac844c737633f4674608f1e` (`git show <tag>:Book1A/Phase3/plan_hashes_phase3.md`). |
| C2 plans | the 41 C2 plans (`book1a.plan_c2`, c2-vwap-tag-only-v1.0; section 4), sha256 in `plan_hashes_phase3_c2.md`, git (LF) content sha256 `a7ece816e86101945a1b17e2f4b7bbbf9614615ccbcb659343c2777a08f86c13`. Used only by the C2 R4 replay. |
| R1 A0 | unchanged: Book 1 S1.4 defaults, map v2.3, rules-only plan, no veto, exit M0, qty 1. `python -m book1a.run_r1_r2 --phase phase3 --fill v3.5 --block1 K:\Book1A_inputs --out book1a\Phase3\runs\phase3` |
| R2 C1 | unchanged: A0 + veto FZ1 or L1 or T8, RH1 retest 15 bars / 2 ticks, M0, qty 1 (same run). |
| R3 C1 + risk | unchanged: R2 signals + C3 risk check **risk-c3-v2**. `python -m book1a.run_r3 --block1 K:\Book1A_inputs --a0-run book1a\Phase3\runs\phase3 --out book1a\Phase3\runs\phase3_r3` |
| R4 Book 1A | **final configuration, declared in writing (replay plan section 6): Book 1A plans + S1.4, veto L1 or T8 (FZ1 logged only), RH1, exit M0 fixed (E1), risk-c3-v2; replayed as one strategy.** `python -m book1a.run_r4 --block1 K:\Book1A_inputs --a0-run book1a\Phase3\runs\phase3 --plans book1a\Phase3\plans_phase3 --phase phase3 --out book1a\Phase3\runs\phase3_r4 --candidate-days <all 41>` |
| C2 R4 (diagnostic) | the same R4 command with `--plans book1a\Phase3\plans_phase3_c2 --out book1a\Phase3\runs\phase3_r4_c2`; Step B only; never promoted; no Phase 1 or Phase 2 rerun of C2. |
| Fill model | **v3.5 for all four**: market entry 250 ms after the bar close at the best ask (long) / bid (short); target fills 1 tick through; stop fills 1 tick beyond the first traded price at or beyond the stop; same-tick stop and target = stop. |
| Costs | round trip NQ $5.74, MNQ $1.88 (MNQ only in the MNQ feasibility diagnostic). |
| U3 (R3, R4) | simulated balance $100,000; $1,000 per trade (1%); $2,000 daily loss limit; NQ only, whole contracts, minimum 1 NQ; a trade whose 1 NQ estimate exceeds the budget is RISK_REJECT, never shrunk; 2-tick slippage allowance in the pre-trade estimate only; 3 trades per day and the 2-loss halt. |
| Risk implementation | risk-c3-v2 for R3 and R4 (decision quote: best ask long / best bid short at the decision time; guards NO_QUOTE and REF_AT_OR_PAST_STOP). Written on every R3 / R4 ledger row. |
| Bootstrap | session bootstrap, seed **20251205**, B = 10,000 (sections 2 and 5). |
| Stress | `python -m book1a.run_stress --block1 K:\Book1A_inputs --a0-run book1a\Phase3\runs\phase3 --r4-run book1a\Phase3\runs\phase3_r4 --plans book1a\Phase3\plans_phase3 --stress lat1000 / slip2 / slip4 --out book1a\Phase3\runs\phase3_stress_<setting>` (stress-v1.0, unchanged). slip2 is also the 2-tick check of section 5. |
| Review fields | `book1a/phase2_review_fields.py` (phase2-review-fields-v1.2), `compute("phase3", ...)`; the rules are v1.1's, generalized only by the phase argument. |
| Report code | `book1a/phase2_report.py` (**phase2-report-v1.1**), `run("phase3", ...)`: report card (section 2), classes and tag counts (section 3), the half-day exit fields, the overlap check. v1.1 = v1.0 generalized only by the phase argument (Phase 3 exposure set `EXPOSED_BY_PHASE["phase3"]`); tested (`tests/test_phase3_phase_arg.py`) with the Phase 2 tests unchanged and passing. |
| Section 3 application | `book1a/phase2_review_apply.py` (**phase2-review-apply-v1.2**), `--phase phase3 ... --plans book1a\Phase3\plans_phase3 --plan-hashes book1a\Phase3\plan_hashes_phase3.md --out book1a\Phase3\runs\phase3_review`: v1.1's rules (hard mapping errors, cr_ps_width session terciles, premarket plan fields) generalized only by the phase argument; outputs `phase3_review*`. |
| Diagnostics | `python -m book1a.diag_phase1b --runs book1a\Phase3\runs --folders phase3 phase3_r3 phase3_r4 --d5-days --plans book1a\Phase3\plans_phase3 --gex K:\Book1A_inputs\gex_levels_block1.csv --inputs K:\Book1A_inputs --out book1a\Phase3\runs\phase3_diag` (diag-phase1b-v1.2, unchanged). |
| G4 draw | `book1a/g4_draw.py` (g4-draw-v1.1) `--phase phase3`, run unchanged in Step B (section 6, G4). |
| Labels | every result is "replay (in-sample)". Never "validation". UNEXPOSED is less exposed to prior analysis, not a holdout. |

Data conditions registered before any result (inputs only, `phase3_sessions.md`): all 41 sessions have Databento condition "available", the raw MBO file, a tape ending within 60 s of the close, complete NQ / ES 1-minute RTH bars (390, or 225 on Dec 24), an ok GEX row, a map packet and a plan; every session's front contract (NQZ5 Dec 5-12, NQH6 from Dec 15) equals the data-integrity table's main and NinjaTrader contract. Map v2.3 writes the Nov 27 20:44 - Nov 28 07:30 CT CME outage gap into the packets of Dec 5-12 (their history window includes it) and, as frozen, leaves out the Dec 5 prior-week profile; not DATA_MISSING (a real market outage). Plans review=LOG_ONLY, as frozen: Dec 15 (check A roll day; check C 1 NQ does not fit), Dec 24 (check A half day; check C) and Jan 26 (Z3 balance POC; check E). The session check flags **Dec 17 and Dec 18, 2025** only because the GEX V3 reproduction compares the 0DTE levels and counts an empty frozen value against an empty reproduction as a mismatch (`gex_v3.py` repro check; documented, not changed). Input-file check (`Book1A/Phase3/zdte_check_dec16_18.txt`, script `zdte_check_dec16_18.py`, inputs only): the CME option files of Dec 16, 17 and 18 do contain the Dec 17 (root Q3C) and Dec 18 (root Q3D) daily expiries with definitions, open interest and settlements, but their underlying is **NQZ5**, while the frozen GEX row's front is **NQH6** from the Dec 17 row (front_by_volume_of Dec 16); the frozen method uses only options on its front contract (`mq_levels.compute_levels`: `chain.underlying == front`, 0DTE = expiring the next session). So the empty 0DTE fields of the Dec 17 and Dec 18 rows are a **true absence under the frozen method, not a data gap**: the 0DTE levels are not labelled DATA_MISSING, the rest of each GEX row stays as frozen, and both sessions keep every trading input. The GEX V3 diagnostic for these two sessions follows its frozen code (repro N, flagged as such). In `phase3_sessions.md` their status DATA_MISSING (cause "GEX V3 inputs do not reproduce the frozen row") is this V3 flag only: both sessions are run in R1-R4 and C2 R4 and counted in G2; only the V3 diagnostic marks them repro N. Also noted, inputs only: the frozen GEX front is NQZ5 on the Dec 15 and Dec 16 rows (volume of Dec 11 and Dec 12) while the NinjaTrader front is NQH6 from Dec 15; the frozen nt_shift_pts maps the levels to the chart contract, unchanged.

Known behaviour registered before any result (frozen Book 1 code, not changed): on the **Dec 24, 2025 half day** the
tape ends at the 12:15 CT close and the replay's 14:55 flatten is never reached that day. A position still open at
12:15 is closed by the replay's FLATTEN branch at the last quote before the close (bid long / ask short of the last
Dec 24 tick), with its exit time stamped at the next tick in the tape (the next session's open). It is reported as it
comes out, flagged `EXIT_AFTER_SESSION_CLOSE` (`phase2_report.exit_times`), and every review measure stops at 12:15
(section 3), exactly as registered for Nov 28 in Phase 2. Any change goes to a later change list only with Kyron's
approval.

## 2. Report card (R1-R4)

The Phase 2 definitions (Phase2_registration.md section 2) apply unchanged, with Phase 3's populations: **ALL** = the 41
sessions; **UNEXPOSED** (the not-excluded population) = the 38 sessions without Jan 12, Jan 14 and Jan 16, 2026. Reported
separately and **never pooled**; both "replay (in-sample)". Confidence intervals are descriptive uncertainty, not
evidence of an edge. In particular: trade R = ledger `realized_net_R` (theoretical R beside it); session net R = the sum
of the session's trade R, 0 for a session without trades; net R per session = the mean over the population's sessions
(denominator 41 or 38); entry session = the ledger `date`; session dollar P&L; the 90% session-bootstrap CI (B = 10,000,
`numpy.random.default_rng(20251205)` per strategy and population, index matrix `rng.integers(0, n, size=(10000, n))`,
5th and 95th percentiles, numpy linear); win rate, average win / loss R; max drawdown over trades in (session, entry
time) order from a peak of 0 (R; dollars for R3 / R4) and the SUPPLEMENTAL session-order drawdown; the overlap check;
exit-reason counts; RISK_REJECT by reason, execution breaches (count, largest amount), RISK_BREACH_FILL (count,
largest overrun); stress at 1,000 ms and 2 / 4 ticks (whole replay rerun), **shown separately from the baseline**; the
gamma regime split (V5 sessions in "all" only) and the time-of-day split (08:30-08:45, 08:45-10:00, 10:00-13:00, after
13:00 CT by entry fill time); the daily table.

**Reporting split registered now (A4; not a new comparison, existing fields only):** R4 results are also shown by
`mj_alignment` from `diag_exit_trades` (plan zone / PLAN_ALIGNED / EXPLORATORY_NOT_PLAN_ALIGNED / other; a missing value
= other), in both populations: trades, net R per session (denominator = the population's session count), win rate.
Descriptive only, never promoted.

**C2 R4 card (diagnostic, section 4):** the same report card for the C2 R4 ledger (`phase2_report.run("phase3",
{"R4": <C2 ledger>}, {"R4": <C2 attempts>}, ...)`), shown beside R4 and labelled "C2 diagnostic (VWAP as a tag only),
not promotable", with the number of plans, decision zones and trades that differ from R4.

## 3. What-fails-and-why review (R1-R4, every trade)

Exactly Phase2_registration.md section 3, unchanged, through `phase2_review_apply.py --phase phase3` (frozen functions:
`phase2_review_fields.compute("phase3", ...)`, `phase2_report.exit_times`, `check_no_overlap`, `populations`, `in_pop`,
`class_table`): the per-trade fields (MFE / MAE, post-stop window (stop fill, stop fill + 30 min] cut at the session
close, TRUNCATED, minutes from initiation, confirm-bar delta / delta % / range), the diagnostics tags (mj_alignment,
L1_PLAN_SIDE, the GEX tags, the CVD tags kept separate by AT_ENTRY / PROVISIONAL / POST_ENTRY, BREAKOUT_SPEED raw values),
market_context_premarket and draw_status_premarket from the entry-session plan sidecar (sha256 must equal
`plan_hashes_phase3.md`; labelled "premarket (plan), not the state at entry"; the state at entry NOT_RUN).
Classes, first rule that applies, the 1.0 R cut-off a prespecified descriptive threshold: a. GAVE_BACK (MFE >= 1.0 R
before the stop); b. STOP_THEN_TARGET (target traded in the post-stop window); c. NO_POST_STOP_FOLLOW_THROUGH (window
complete, move < 1.0 R, target not traded); d. UNCLASSIFIED (anything else); NOT_STOPPED otherwise. Counts per class per
strategy and tag counts per class; numeric GEX tags (cr_ps_width, pc_gamma_ratio) by tercile of **one value per session
over the 41 Phase 3 sessions** (1/3 and 2/3 numpy linear quantiles; V5 sessions out of the cut-offs and their trades NA;
one set used for both populations; never outcomes). CVD_DIV with the note "fidelity to Jeron's CVD unproven (1 of 4
video examples reproduced; CVD_video_check, Nov 6)". Input mapping checks are hard errors (every ledger trade exactly
once, stable keys, inputs read-only with sha256 before and after).

## 4. Section 5 diagnostics in Phase 3

Statuses as frozen in `Phase3_change_list.md`.

| replay plan section 5 diagnostic | Phase 3 status | cause / note |
|---|---|---|
| C2 location arm, VWAP as a family vs VWAP as a tag only | RUN (Step B) | C2 plan set built and hashed in Step A (definition below); C2 R4 replay in Step B; reported beside R4, never promoted |
| MAP4 high-volume areas vs MAP0 zones (AMT PO-6) | LOGGED_ONLY | MAP4 areas in every plan sidecar; the comparison is not built |
| Exit steps M0 -> M-J1 -> M-J2 (R4 fixed at M0, E1) | RUN | M-J1 / M-J2 per trade (diag_exit_trades), v1.1 ladder source, mj_alignment |
| Exit steps M-J3, M-J4 | DROPPED | U5: no objective triggers specified |
| Quantower-style power trade vs S1.4 single print (C4) | LOGGED_ONLY | `power_trade_qt` per candidate (U2) |
| 10 NQ feasibility (hypothetical) | RUN | diag_sizing_trades, labelled hypothetical |
| MNQ feasibility (diagnostic only) | RUN | R3 / R4 RISK_REJECT attempts (diag_mnq_rejects) |
| L2 diagnostics and L2 terciles | NOT_RUN | L2F audit, fixed-price build and coverage list not done (U11); no Phase 2 source for the terciles |
| E1 refill defense | NOT_RUN | as L2 |
| E2 defense pulled before the touch | NOT_RUN | as L2 |
| E4 book flip on the retest | NOT_RUN | as L2; E4's hold time N not registered |
| Exit cue (a), absorption against the trade | RUN | per trade, beside M0 |
| GEX V2 random-level twin | RUN | diag_gex_zones |
| GEX V3 second flip estimate | RUN | gex_v3 (reproduces the frozen levels row before use; Step A check in phase3_sessions.md) |
| GEX V5 days without valid levels | RUN | counted; such days stay in the baseline and leave the GEX groups |
| Volatility control (ATM IV terciles) | RUN | over the 41 sessions' atm_iv |
| Gamma regime and time-of-day splits; context GEX tags | RUN | sections 2 and 3 |
| CVD_DIV by case and WITH / AGAINST, AT_ENTRY / PROVISIONAL / POST_ENTRY separate | RUN | with the fidelity note |
| CVD_DIV overlap with T8 and the passive trap tag | RUN | t8_overlap, trapped_passive per candidate |
| cvd_slope_5 by tercile | RUN | cut-offs from the Phase 3 S1.4 candidate rows' own values, never outcomes |
| Grade without CVD (counterfactual on R4) | NOT_RUN: not needed | the S1.4 grade has no CVD input (harness `JeronOrderFlowStrategy.cs` lines 2566-2576; CVD only sets the logged CVD_ALIGNED / CVD_DIVERGENT flag, lines 2534-2535), so the counterfactual equals the current grade |
| BREAKOUT_SPEED raw values | RUN | per candidate and trade |
| 08:30 vs 17:00 CT CVD reset | RUN | both series per swing |
| Swing pairs excluded by the 60-minute window | RUN | counted |
| Every logged tag | RUN | descriptive |

**C2 definition (A3).** The frozen documents that define "VWAP as a tag only", quoted:

- Replay plan section 5: "Location arm with VWAP counted as a family vs VWAP as a tag only (C2)."
- AMT PO-8 (Book1A_1_AMT_map.md): "At 08:10 CT every zone gets VWAP if the session VWAP is inside it or within 5 points
  *(ours: 5 points)*, and WKVWAP for the weekly VWAP. The ±1σ bands are tagged the same way (VWAP\_SD1\_UP /
  VWAP\_SD1\_DN)."
- AMT PO-8: "Source family (C2): session VWAP, weekly VWAP and the bands together are one family (VWAP) toward the
  2-family minimum in Phase 3 and PO-3; several VWAP tags on one zone still count once. VWAP never creates a zone on its
  own and never changes a side."
- AMT PO-8: "Diagnostic split (not promotable): the location arm with VWAP counted vs the same arm with VWAP as a tag
  only, reported in the replay."
- Phase 3 zones doc (Book1A_3_zones_sides.md, zone rule 1, C1): "a decision zone is a price area where sources from 2+
  of six families line up (C1). Families: ... (6) VWAP: overnight session VWAP, weekly VWAP and the ±1σ bands (AMT
  PO-8, C2). Each family counts at most once ..."
- Replay plan change log, Nov 1, 2026: "C2: VWAP is one source family; VWAP definition frozen at 08:10 CT; on/off
  diagnostic".

C2 plan set built only from these: the same code (the Step A map packets, `plan_hand_check.build_day` ->
`plan_v24.build`, families-v1.0), the same thresholds (5 points VWAP / other families, 10 points GEX, 2-family
minimum, 2 zones per side), the only difference being that VWAP is not counted as a source family: inside
`plan_c2.vwap_tag_only()` `families.count_families` drops the VWAP family from the family list, so a zone whose second
family was VWAP falls below 2 families and becomes TARGET through the frozen code path. The VWAP levels stay on the
zone in `levels=` (the PO-8 tags: same names, same 5-point rule) and the PO-1 VWAP tag on rejection zones is untouched.
The baseline plans are rebuilt in the same process outside the patch and must equal `plans_phase3` byte for byte (hard
error otherwise). Unit tests on synthetic zones (`tests/test_plan_c2.py`): a VWAP-only second family loses decision
status; a zone with 2 other families is unchanged; tags preserved; thresholds unchanged; the patch is restored. No part
needed a definition the documents do not give.

C2 build (Nov 8, 2026; `plans_phase3_c2/plan_build_manifest.json`; plan structure only, no outcome): 41 / 41 days built,
every baseline rebuild equal to `plans_phase3`; every C2 plan differs from its base (the `families=` field drops VWAP on
the 97 base decision zones that counted it; `levels=` unchanged). Decision zones 158 (base) -> 156 (C2). On 15 days
the decision-zone set changes: on Dec 31 and Jan 28 one zone falls to TARGET with no replacement; on the other 13 days
a zone is replaced by another zone through the frozen ranking and 2-zones-per-side rule (on Dec 19 and Feb 2 the
replacement is a near-identical zone with an edge 0.25-1.25 points different).

## 5. Primary comparisons and their rule

Replay plan section 9, verbatim: "**Primary comparisons (Phase 3 replay):** the Book 1 promotion rule: paired net R per
session; 90% session-bootstrap lower bound of the paired difference above 0; max drawdown no worse than 1.25× the
comparator; at least 20 trades that differ; still at or above the comparator under 2-tick stop slippage. Otherwise
\"insufficient evidence\"."

One-sided or two-sided, as Book 1 defines it: **the lower bound of a two-sided 90% percentile interval (the 5th
percentile)**. Sources: Book 1 engine design v3.10, Phase 3: "the lower bound of the 90% session-bootstrap confidence
interval of the paired difference is above 0"; Book 1 code `jeron_engine/arms.py` `promotion()`: "session bootstrap (n
resamples, seed) 90% interval = 5th-95th percentile, lower bound = 5th percentile > 0" (`np.percentile(boots, [5, 95])`,
n = 10,000, seed 20251205).

Comparisons P1 R4 vs R1, P2 R4 vs R3, P3 R3 vs R2 (Phase3_change_list.md). For each, the Book 1 rule as implemented in
`arms.promotion`, with Book 1A's registered R:
- x = per-session (R_arm - R_comparator), session net R = the sum of the session's trade `realized_net_R` (replay plan
  section 4a: "Promotion uses realized net R"), every session of the population included (0 when no trade);
- bootstrap: `rng = np.random.default_rng(20251205)`, means of `x[rng.integers(0, n, size=(10000, n))]`, lower bound =
  5th percentile; check: lower bound > 0;
- max drawdown of the arm <= 1.25 x the comparator's (cumulative realized net R, the report card's trade order);
- trades that differ >= 20, counted as Book 1's `differing_trades`: matched by (date, signal time), signal time as Book
  1's replay defines it (`arm_replay.replay`: "the candidate's queueing bar", i.e. `arm_replay.attempts` t = the
  EvidenceTimeCT of the candidate row, or of its CONFIRM row for an AwaitConfirm entry, as HH:MM:SS), taken from each
  run's own attempts / retests files (source rule in `phase3_compare.py`; corrected Nov 8, 2026 before the freeze: the
  earlier text said "the candidate row" only, which differs from Book 1 for AwaitConfirm entries); removed + admitted +
  entered or exited differently (entry price, exit price or exit time); size is not part of the Book 1 match;
- 2-tick check: the mean per-session paired difference of the slip2 stress ledgers (arm and comparator both at 2 ticks)
  >= 0;
- pass ("promote") = all four checks; otherwise "insufficient evidence" (replay plan section 9). Book 1's code also
  separates "reject"; it is reported beside it as information only.
Also reported for every comparison (section 9): paired daily results, the interval, max drawdown, number of changed
trades, RISK_REJECT count and RISK_BREACH_FILL events. Net R alone never decides. Seed 20251205.

**Deciding population (registered Nov 8, 2026, before any outcome; Kyron approved, checker and reviewer review of
Step A):** the primary comparisons P1 (R4 vs R1), P2 (R4 vs R3) and P3 (R3 vs R2) are decided on **ALL 41 sessions**,
labelled **"in-sample, includes 3 exposed sessions (Part 3)"**. The same rule on the **38 UNEXPOSED sessions** is a
registered **sensitivity**, never called independent or out-of-sample. If the two verdicts differ, the comparison is
reported **SENSITIVE_TO_EXPOSED_SESSIONS**; no selection either way (the ALL verdict stays the decision, the UNEXPOSED
verdict is shown beside it).

**Comparison code:** `book1a/phase3_compare.py` (phase3-compare-v1.0), a thin wrapper that imports and calls Book 1's
`jeron_engine.arms.promotion` **unchanged** (arm, comparator, sessions, arm_2t, a0_2t; seed 20251205, n 10,000). It only
maps Book 1A ledger rows to the dicts `arms.promotion` reads: `date` (ledger date), `signal_time` (source rule above),
`entry` / `exit` (ledger entry_price / exit_price), `exit_time` (ledger date + exit_time), `R` = ledger `realized_net_R`
(replay plan 4a). Sessions = the registered list of the population (zero-trade sessions included); a population's
trades are the trades on its sessions. 2-tick inputs = the slip2 stress ledgers (`book1a.run_stress --stress slip2`).
A duplicate (date, signal_time) key in any strategy, a duplicate trade_id, a missing realized_net_R, a trade outside
the 41 sessions or a signal time the run files do not give stops the run before `arms.promotion` is called. No formula
is re-implemented. Output: the `arms.promotion` dict per comparison and population, the population labels and the
sensitivity label. Tested on synthetic ledgers only (`tests/test_phase3_compare.py`).

## 6. Change list rule (Phase 4)

`Phase3_change_list.md` is final for Phase 3. For Phase 4, the replay plan rule applies: "Phase 4 replay: R1–R4 once,
frozen". Between phases only demonstrable calculation or timing errors may be fixed, each logged in the change log with
its reason; a threshold is never changed because of a result. No item is added, and none is dropped, because of a Phase
3 outcome. New ideas go to `Block2_candidates.md`.

## 7. Phase 3 gate (pass = all of G1-G5; performance is not a gate)

- **G1 Integrity**: run at the frozen commit; plan hashes unchanged from Step A (every R4 ledger and candidate row's
  `plan_sha256` equals `plan_hashes_phase3.md`, every C2 R4 row's equals `plan_hashes_phase3_c2.md`; the plans rebuilt
  from the Step B R1 run's own map packets are byte-identical to the Step A files, base and C2); unit tests pass;
  look-ahead audit clean for R1-R4 and C2 R4 (`book1a.audit_run` on each ledger) and for every AT_ENTRY field (D2);
  Phase 1 and Phase 2 ledgers unchanged (their registered sha256).
- **G2 Coverage**: 41 / 41 sessions run for R1-R4 and C2 R4. A missing session is either repaired and rerun, or
  accepted in writing by Kyron as a named coverage exception before the gate is decided. Documentation alone does not
  pass G2.
- **G3 Risk**: zero planned-risk violations for R3 / R4 / C2 R4 (risk-c3-v2: an accepted trade whose `planned_risk_usd`
  is above min($1,000, the remaining daily budget at the decision)); execution breaches reported.
- **G4 Checker reproduction**: the checker independently rebuilds, from the raw tape and the frozen specs with its own
  code (never the runner's implementation), every R4 trade on the fixed days **Dec 10, Dec 18, 2025, Jan 14 and Jan 29,
  2026**; plus 10 R4 trades from the other 37 sessions and 10 trades from the R1-R3 ledgers, both drawn with seed
  20251205 by `book1a/g4_draw.py --phase phase3` (g4-draw-v1.1, committed in Step A, run unchanged in Step B; both draws
  always taken, whatever the trade counts on the fixed days); checking entry and exit time, price, reason, size and the
  risk-c3-v2 numbers, and recomputing the report card arithmetic and the comparison arithmetic from the ledgers. Pass =
  every field matches, or each mismatch is traced to a documented calculation error that is fixed, rerun and rechecked.
  Any unexplained mismatch fails G4.
- **G5 Deliverables complete and hashed**: report, ledgers (R1-R4 and C2 R4), review file, comparison results, Phase 4
  readiness note.
