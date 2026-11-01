# Book 1A Phase 0: ambiguities, missing definitions and runner choices

Every item below is either (a) a question the docs leave open, logged with the choice the code makes
("runner default", changeable before the freeze), or (b) a value the docs mark as not set, which the
code writes as null. Nothing here was chosen from a result. Updated as the build proceeds.

## A. Blocking for P0.4 (needs Kyron)

| # | Item | Where | Runner default |
|---|---|---|---|
| A1 | Fill model for the R2 (C1) reproduction. The replay plan freezes fill model v3.4 for R1-R4 and says the Oct 28 "v3.5" was only a design version. But `FROZEN_STRATEGY.md` and `fill-model-v3.5-proposal.md` say C1's Phase 3 result and the Phase 4 holdout used **fill model v3.5** (gap fill: a stop that price jumps through fills at the first traded price at or beyond it). On A0's fixed stops v3.5 differs from v3.4 only on gap fills (4 of 35 Phase 2 trades per the proposal). "Reproduce R1 and R2 exactly as frozen under the original Book 1 assumptions" (E5, P0.4) therefore means v3.4 for A0 Phases 1-2 and v3.5 for A0 and C1 Phases 3-4; the standardized replay (section 4a) then uses v3.4 for all four. | Replay plan 4a, P0.4; FROZEN_STRATEGY.md | Produce the checker ledgers under the fill model each Book 1 result was published with (v3.4 Phases 1-2; v3.5 Phases 3-4, which equals v3.4 except on gap fills) and label the column `fill_model`. Standardized R1-R4 replay: v3.4. Kyron to confirm. |
| A2 | "Current Book 1 tag" to branch from. No git tag or repository history is reachable from this session: the NT82 GitHub repository was empty, and the Book 1 git repo (tags `phase3-fill-v3.5`, `phase3-combination` commit 54e25fc, `phase4-result`) lives on the PC. | Task brief | Branch `book1a-phase0` created in NT82 with a byte-exact `book1_ref/` snapshot of the Drive mirror (see `book1_ref/MANIFEST.md`); Kyron to confirm the mirror equals the frozen tag on the PC (sha256 list provided). |
| A3 | Block 1 raw data and the C# harness run only on the PC (`K:\Databento_BackTesting`, 44 GB MBO, Mono build). This session has no Remote Control folder attached, so every data-dependent pass test (P0.2 checksums, P0.3, P0.4, P0.6-P0.9 hand checks on real days, P0.11-P0.13 on real days) is built and unit-tested here but must be executed on the PC. | Environment | Scripts are written to run from `K:\Databento_BackTesting\Book1A\`; see the report for the exact commands. |

## B. Runner choices inside the frozen rules (logged; change before the freeze if Kyron disagrees)

| # | Item | Doc | Runner default (in code) |
|---|---|---|---|
| B1 | VWAP: a trade stamped exactly 08:10:00.000 CT | PO-8 "trades before 08:10:00 only" | Excluded (strict `<`), consistent with NinjaTrader's bar rule (a tick at hh:mm:00.000 belongs to the next bar). |
| B2 | PO-1 look-back window start | "from the start of the prior-day cash session (08:30 CT) through the developing week (from Sunday 17:00 CT)" | min(prior-day 08:30 CT, Sunday 17:00 CT): Monday starts Friday 08:30. |
| B3 | Swing high/low ties | PO-1 step 1 "the highest of the 15 bars before and after" | Strictly higher than every neighbour; an equal high is not a swing. |
| B4 | Arrival evidence precedence | PO-1 step 2 | Delta first (largest), then IMB, then LARGE; the value written is the first that qualifies. |
| B5 | FLIP overlap denominator | PO-1 step 4 "overlapping the first zone by at least 50%" | overlap length / first zone's width. |
| B6 | FLIP zone cap side | PO-1 step 4 "union ... capped at 40 points" | The 40 points nearest the newer (opposite) rejection's extreme. |
| B7 | Merge cap side | PO-1 step 3 | The 40 points nearest the more extreme swing of the merged pair (the union's extreme). |
| B8 | Delta band "top 20% of absolute delta" | PO-7 | The ceil(20%) highest-ranked rows by absolute delta among non-zero rows of that profile. |
| B9 | Delta band longer than 40 points | PO-7 "10-40 points wide" | Keep the 40-point window (8 rows) with the largest absolute delta sum. |
| B10 | PO-9 "20% of the volume since then below it" | PO-9 | Share of bar volume whose bar closed beyond the edge, over all bars since the first close beyond it. |
| B11 | PO-9 first close "since then" | PO-9 | The current unbroken run of closes beyond the edge, scanned back from 08:10. |
| B12 | DD_EDGE when price is inside the separator | PO-11 | No zone (both distributions are "far"); logged. |
| B13 | Daily budget: do gains restore it? | U3 "daily loss limit minus realized losses today" | No (literal reading); config flag `gains_restore_daily_budget=False`. |
| B14 | Does a RISK_REJECT count toward the 3-trade cap? | U3 | No: it is not a trade. Rejections are logged with their reason. |
| B15 | Which halt comes first | U3 | Checked in this order at every candidate: existing halt, 3-trade cap, 2-loss halt, dollar limit; the first to trigger is recorded; a RISK_REJECT on the daily budget is distinct from DAILY_LIMIT. |
| B16 | Realized net R denominator | Replay plan 4a | Book 1 convention: stop distance in ticks x $5 x N (planned stop, no slippage allowance); numerator = realized net dollars after commission on every contract. Theoretical R = move ticks / stop ticks. |
| B17 | Family of a level with no family in the docs (settlement, TPO value areas, single prints) | AMT "moved to research: tags only" | Settlement: no family. TPO/single-print areas: VOLUME family per the Phase 3 list ("low-time and single-print areas"). |
| B18 | Context "inside or above composite value after holding or reclaiming its VAL" | Context rule | Two inputs: price >= composite VAL and a boolean `held_or_reclaimed_val` from the PO-9 state/history; NONE when both Bullish and Bearish fire or neither does and the balance is not overlapping. |
| B19 | Invalidation edge for a Bullish context | Context trigger 1 "below the weekly or composite VAL it depends on" | The higher of the two VALs (the one nearest price, which price would lose first). |
| B20 | 1-hour swing definition for htf_structure | Context input 7 (needed) | Map `h1_swings` as built (swing strength 3), last two highs and lows. |

## C. Values the docs mark as not set (written as null; never invented)

| # | Field | Doc |
|---|---|---|
| C1 | `on_profile` THIN/NORMAL ("thin" overnight) and "far" from settlement | Context input 2, U8 |
| C2 | `es_long_above` / `es_short_below` level choice | Context input 8, U8 |
| C3 | `tnx=`, `vix=`, `tnx_override=` thresholds and historical source | Context input 8, U8 |
| C4 | Gamma ranks, 1-day min/max, blind levels | U6, U7 (P1.1 builds ranks if the D-1 option files are on the PC) |
| C5 | Power-trade time interval, size inside 300-500, trade-size and delta filters | U2 (logged only; S1.4 single print stays the gate) |
| C6 | R minimums at entry (TP1 1.5 R / runner 3 R are examples) | Phase 5 shared rules (logged, not applied) |
| C7 | M-J3 / M-J4 triggers (quick break-even, new-zone definition) | U5 (deferred) |
| C8 | E4 hold time N | U11 (registered before the E4 diagnostic, not needed for Phase 0) |

## D. Blinding exposures (full disclosure)

See `P0.1_blind_run_setup.md`, section "Access events": `FROZEN_STRATEGY.md` (Phase 3 result table
seen while reading the C1 definition), plus result numbers quoted inside the Book 1A docs and the
design v3.10 change log.
