# Book 1A – Block 2 candidates (ideas for Block 2 development only)

Written Nov 8, 2026 (Phase 3 Step A5, Kyron's list). **Never used in Phases 3-4.** Nothing here changes R1-R4, the
Phase 3 change list, any threshold, any rule or any Phase 3 / Phase 4 report. Replay plan section 5: "No comparison is
added after results are seen. A new idea goes to Block 2 development, not into this replay." Each item says where it
came from and whether it was found after seeing Phase 2 results. A Block 2 candidate is tested only in Block 2
development (Apr 22 - Jun 30, 2026, after a "go"), registered before its own run.

| # | candidate | origin | found after seeing Phase 2 results |
|---|---|---|---|
| 1 | **Entry-side risk allowance.** The pre-trade risk estimate (U3, risk-c3-v2) covers stop slippage (2 ticks) but not the 250 ms entry delay. Candidate: add an entry-side allowance; candidate value 2 ticks, reusing U3's allowance. | Phase 2 G3: execution breaches R4 5 / 19, R3 1 / 8 (Phase2_report.md section 6) | yes |
| 2 | **GEX call-resistance / put-support width tercile as a session filter.** | Phase 2 what-fails-and-why, cr_ps_width terciles (phase2_review, v1.1): 8 / 11 wins in T2 vs 0 / 8 in T1 + T3, from 5 winning sessions | yes |
| 3 | **Profit protection after >= 1 R in profit.** | Phase 2 stopped-trade classes: 6 / 11 R4 stops were GAVE_BACK (MFE >= 1 R before the stop) | yes |
| 4 | **Entry timing and stop placement.** | Phase 2 stopped-trade classes: 3 / 11 R4 stops were STOP_THEN_TARGET (target traded within 30 min of the stop) | yes |
| 5 | **L1 next to a plan zone whose sides are NONE.** | Phase 2 L1_PLAN_SIDE: 6 / 19 R4 trades | yes |
| 6 | **Monday weekly window.** | Phase 1 location diagnostic M1 / M2 (Phase 1b) | no (Phase 1 diagnostic; Phase 1 outcomes are not used for anything in Book 1A) |
| 7 | **Candle-direction CVD (CVD-CANDLE)** as a possible match to Jeron's displayed CVD. | Nov 8, 2026; exploratory, handled in the separate Part 3 CVD study (`K:\CVD_Part3_Research`), not Book 1A | no (CVD fidelity question, CVD_video_check Nov 6; not from a Phase 2 outcome) |

Already registered for Block 2 development in the replay plan (section 5, Nov 4, 2026), listed here for completeness
and unchanged: the stop-model comparison (full-zone stop, structural-invalidation stop, component-level stop).

## Open item for the Block 2 go / no-go review

Added beside N7 in the open items (`Book1A_open_items.md`, item **N7a**, Nov 8, 2026), not replacing it:

> Audit whether the StrongCandidate export, the Strategy21F depth logs and the detector research covering May 29 –
> Aug 31, 2026 influenced any Book 1A design decision. Jul 1 – Aug 31, 2026 stays reserved for Book 1A Block 2
> validation, subject to that audit. If the audit establishes that those sessions shaped Book 1A rules, the affected
> sessions become exploratory and final confirmation moves to later untouched data.

The audit is not part of Phase 3 Step A (its registered instructions do not require it there).
