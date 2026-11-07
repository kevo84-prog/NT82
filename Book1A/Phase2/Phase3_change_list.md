# Book 1A – Phase 3 change list (DRAFT, not frozen)

Drafted Nov 7, 2026 (Phase 2 Step B) by the runner. **Draft only:** no Phase 2 review has been done, the list is not
frozen, and Phase 3 does not start until G4 and Kyron's review are done and Kyron freezes this list (tag
`book1a-phase3-frozen`).

Rule (Phase2_registration.md section 5): this list may contain only (i) items already in replay plan section 5,
(ii) documented calculation or timing fixes, each with its reason, (iii) values the plan says are frozen from Phase 2
(L2 terciles, E4 N). No item is added, and none is dropped, because of a Phase 2 outcome; an item may be dropped only
because it cannot run (data or build missing). No threshold or rule changes from Phase 2 results.

How this draft was made: every line below comes from replay plan section 5 and the Phase 2 status already registered
in Phase2_registration.md section 4 (written before any Phase 2 run). No Phase 2 result (P&L, R, win rate, class or tag
count) was used to add, drop, order or word any item.

## (i) Items from replay plan section 5

Primary comparisons (Phase 3 replay; Book 1 promotion rule, replay plan section 9):

| # | comparison | Phase 3 |
|---|---|---|
| P1 | R4 Book 1A vs R1 A0 | run |
| P2 | R4 Book 1A vs R3 C1 + risk | run |
| P3 | R3 C1 + risk vs R2 C1 (effect of risk control alone) | run |

R4's final configuration (always M0, E1) is declared in writing and replayed as one strategy before it is frozen
(replay plan section 6).

Diagnostics inside Book 1A (reported, never promoted on their own):

| diagnostic | Phase 2 status (registered) | Phase 3 entry |
|---|---|---|
| C2 location arm, VWAP as a family vs VWAP as a tag only | NOT_RUN (not built) | keep; runs only if the second plan set (VWAP as a tag) and its R4 rerun are built before the freeze, else drop: cannot run (build missing) |
| MAP4 high-volume areas vs MAP0 zones (AMT PO-6) | LOGGED_ONLY | keep; the comparison runs only if built before the freeze, else stays logged only |
| Exit steps M0 -> M-J1 -> M-J2 (R4 fixed at M0, E1) | RUN | keep, unchanged |
| Exit steps M-J3, M-J4 | NOT_RUN (U5) | keep listed; cannot run until objective triggers are specified (U5); drop for Phase 3 if still unspecified at the freeze |
| Quantower-style power trade vs S1.4 single print (C4) | LOGGED_ONLY (U2) | keep; logged only until its settings come from documentation or reference examples |
| 10 NQ feasibility (hypothetical) | RUN | keep, unchanged |
| MNQ feasibility (diagnostic only) | RUN | keep, unchanged |
| L2 diagnostics (L2F 1.0) | NOT_RUN (U11: L2F audit, fixed-price build, coverage list not done) | keep listed; cannot run until the L2F audit and build are done; see (iii) |
| E1 refill defense | NOT_RUN (U11) | as L2 |
| E2 defense pulled before the touch | NOT_RUN (U11) | as L2 |
| E4 book flip on the retest | NOT_RUN (U11; N not registered) | as L2, and needs N (iii) |
| Exit cue (a), absorption against the trade | RUN | keep, unchanged |
| GEX V2 random-level twin | RUN | keep, unchanged |
| GEX V3 second flip estimate | RUN | keep, unchanged |
| GEX V5 days without valid levels | RUN | keep, unchanged |
| Volatility control (ATM IV terciles) | RUN | keep, unchanged |
| Gamma regime and time-of-day splits; context GEX tags | RUN | keep, unchanged |
| CVD diagnostics: CVD_DIV by case and WITH / AGAINST (AT_ENTRY / PROVISIONAL / POST_ENTRY separate), T8 and passive-trap overlap, cvd_slope_5 by tercile, BREAKOUT_SPEED raw values, 08:30 vs 17:00 reset, 60-minute exclusions | RUN | keep, unchanged, with the fidelity note |
| Grade without CVD (counterfactual on R4) | NOT_RUN (needs a harness change) | keep listed; cannot run without a harness change, which is not allowed; drop for Phase 3 for that reason unless Kyron decides otherwise |
| Every logged tag | RUN | keep, unchanged |

## (ii) Documented calculation or timing fixes

None found in Phase 2. G1 was clean (plans byte-identical on rebuild, look-ahead and D2 audits 0 violations, unit
tests pass); no bug was logged and no execution code was changed after the freeze.

Noted, not proposed:
- Nov 28 early-close exit (registration section 1, known behaviour): any change goes here only with Kyron's approval.
  No strategy traded on Nov 28 in Phase 2; no change is proposed.
- The post-freeze reporting implementation amendment (`phase2_review_apply.py`, Nov 7) is reporting code, not a
  calculation or timing fix; it stays available for Phase 3 reporting as is.

## (iii) Values frozen from Phase 2

| value | source the plan names | Phase 2 | Phase 3 entry |
|---|---|---|---|
| L2 tercile cut-offs | Phase 2 replay candidates' L2 feature values, never outcomes | not available: L2 not run (U11) | cannot be frozen from Phase 2; L2 / E1 / E2 / E4 cannot run in Phase 3 unless Kyron registers another source before the freeze |
| E4 hold time N | frozen before the run (U11) | not registered | open for Kyron; without it E4 cannot run |
