# Book 1A – Phase 3 change list (final, Step A; frozen with the tag `book1a-phase3-frozen` by Kyron)

Written Nov 8, 2026 (Phase 3 Step A4) from the Phase 2 draft (`Book1A/Phase2/Phase3_change_list.md`, sha256
`9c21147d3115cad84b43b2f7fc9bbbfea97b9168a6dc5567190683c873c6d07a`, unchanged) with Kyron's decisions of Nov 8, 2026.
Phase 2 passed G1-G5 (G4 by the checker, Nov 7-8). Kyron freezes this list with the registration (tag
`book1a-phase3-frozen`) before any Phase 3 run.

Rule (Phase2_registration.md section 5): only (i) items already in replay plan section 5, (ii) documented calculation
or timing fixes, each with its reason, (iii) values the plan says are frozen from Phase 2 (L2 terciles, E4 N). No item
is added, and none is dropped, because of a Phase 2 outcome; an item may be dropped only because it cannot run (data or
build missing). No threshold or rule changes from Phase 2 results. Ideas found after seeing Phase 2 results go to
`Book1A/Block2_candidates.md` (Block 2 development only, never Phases 3-4).

## (i) Items from replay plan section 5

Primary comparisons (Phase 3 replay; promotion rule of replay plan section 9, quoted in Phase3_registration.md):

| # | comparison | Phase 3 |
|---|---|---|
| P1 | R4 Book 1A vs R1 A0 | run |
| P2 | R4 Book 1A vs R3 C1 + risk | run |
| P3 | R3 C1 + risk vs R2 C1 (effect of risk control alone) | run |

R4 stays **M0, E1, risk-c3-v2**, unchanged. R4's final configuration (always M0, E1) is declared in writing in
Phase3_registration.md section 1 and replayed as one strategy before it is frozen (replay plan section 6).

Diagnostics inside Book 1A (reported, never promoted on their own):

| diagnostic | Phase 2 status | Phase 3 decision | reason |
|---|---|---|---|
| C2 location arm, VWAP as a family vs VWAP as a tag only | NOT_RUN (not built) | **RUN (built in Step A3)** | the second plan set (`plans_phase3_c2`, `book1a.plan_c2`, VWAP family not counted, every other rule and threshold unchanged) is built and hashed in Step A; the C2 R4 replay runs only in Step B. No Phase 1 or Phase 2 rerun of C2 |
| MAP4 high-volume areas vs MAP0 zones (AMT PO-6) | LOGGED_ONLY | **LOGGED_ONLY** | the comparison itself is not built; MAP4 areas stay in every plan sidecar |
| Exit steps M0 -> M-J1 -> M-J2 (R4 fixed at M0, E1) | RUN | **RUN**, unchanged | |
| Exit steps M-J3, M-J4 | NOT_RUN (U5) | **DROPPED** for Phase 3 | cannot run: no objective triggers specified (U5) |
| Quantower-style power trade vs S1.4 single print (C4) | LOGGED_ONLY (U2) | LOGGED_ONLY, unchanged | settings not established from documentation or reference examples (U2) |
| 10 NQ feasibility (hypothetical) | RUN | RUN, unchanged | |
| MNQ feasibility (diagnostic only) | RUN | RUN, unchanged | |
| L2 diagnostics and L2 terciles (L2F 1.0) | NOT_RUN (U11) | **NOT_RUN** | the L2F audit, the fixed-price build and the coverage list are not done; no Phase 2 source for the terciles (iii) |
| E1 refill defense | NOT_RUN (U11) | **NOT_RUN** | as L2 |
| E2 defense pulled before the touch | NOT_RUN (U11) | **NOT_RUN** | as L2 |
| E4 book flip on the retest | NOT_RUN (U11) | **NOT_RUN** | as L2, and E4's hold time N is not registered (iii) |
| Exit cue (a), absorption against the trade | RUN | RUN, unchanged | |
| GEX V2 random-level twin | RUN | RUN, unchanged | |
| GEX V3 second flip estimate | RUN | RUN, unchanged | |
| GEX V5 days without valid levels | RUN | RUN, unchanged | |
| Volatility control (ATM IV terciles) | RUN | RUN, unchanged | |
| Gamma regime and time-of-day splits; context GEX tags | RUN | RUN, unchanged | |
| CVD diagnostics: CVD_DIV by case and WITH / AGAINST (AT_ENTRY / PROVISIONAL / POST_ENTRY separate), T8 and passive-trap overlap, cvd_slope_5 by tercile, BREAKOUT_SPEED raw values, 08:30 vs 17:00 reset, 60-minute exclusions | RUN | RUN, unchanged, with the fidelity note | "fidelity to Jeron's CVD unproven (1 of 4 video examples reproduced; CVD_video_check, Nov 6)" |
| Grade without CVD (counterfactual on R4) | NOT_RUN (needs a harness change) | **NOT_RUN: not needed** | the S1.4 grade has no CVD input (harness `JeronOrderFlowStrategy.cs` grade code, lines 2566-2576: the grade uses initiation / response, THROUGH_VWAP, imbalance or large trade, tape speed, ran-through and counter-context only; CVD only sets the logged CVD_ALIGNED / CVD_DIVERGENT flag, lines 2534-2535), so the counterfactual equals the current grade |
| Every logged tag | RUN | RUN, unchanged | |

**Reporting split registered now** (not a new comparison; existing fields only): R4 results are also shown by
`mj_alignment` (plan zone / PLAN_ALIGNED / EXPLORATORY_NOT_PLAN_ALIGNED / other), descriptive only, never promoted, in
both populations.

## (ii) Documented calculation or timing fixes

**None.** Phase 2 G1 was clean (plans byte-identical on rebuild, look-ahead and D2 audits 0 violations, unit tests pass);
no bug was logged and no execution code was changed after the freeze.

Noted findings, no change:
- Execution breaches (Phase 2: R4 5 / 19, R3 1 / 8) are reported as registered (risk-c3-v2) and judged by the Phase 4
  rule as frozen (replay plan section 9: fail on more than one execution breach, or any single overrun above 25% of the
  daily limit). An entry-side allowance is a Block 2 candidate only (Block2_candidates.md, item 1).
- Half-day early-close exit (Phase 2 registration section 1, known behaviour of the frozen FLATTEN branch): applies to
  the Dec 24, 2025 half day in Phase 3 in the same way; reported as it comes out, flagged `EXIT_AFTER_SESSION_CLOSE`; no
  change.
- The reporting scripts (`phase2_report.py` v1.1, `phase2_review_fields.py` v1.2, `phase2_review_apply.py` v1.2,
  `g4_draw.py` v1.1) are generalized only by a phase argument (phase2 behaviour unchanged, tested); reporting code, not
  a calculation or timing fix.

## (iii) Values frozen from Phase 2

| value | source the plan names | Phase 2 | Phase 3 |
|---|---|---|---|
| L2 tercile cut-offs | Phase 2 replay candidates' L2 feature values, never outcomes | not available: L2 not run (U11) | not frozen; L2 / E1 / E2 / E4 NOT_RUN |
| E4 hold time N | frozen before the run (U11) | not registered | not registered; E4 NOT_RUN |
