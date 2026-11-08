<!-- Drive Google Doc 1tjkYvdg2zr1OvOT0crP40ACCQEHDqNEgCLCNu314IiU, modifiedTime 2026-11-06T21:15Z; results-free copy updated by the checker Nov 8, 2026 (the Nov 4 and Nov 6 edits added to the Nov 1 redacted copy; no Book 1 result added) -->
# **Book 1A – Replay plan (controlling research doc)**

**Status:** draft v1, created Nov 1, 2026\. C1–C7 and the three safeguards approved by Kyron on Nov 1\. This is the controlling document for the Book 1A replay: if a phase doc and this plan disagree on how something is tested, this plan wins. Nothing here changes the frozen Book 1 strategy (A0, C1) or its published results.

## **1\. Purpose**

> * Rerun Book 1A on the Book 1 data we already own (Block 1, Oct 22, 2025 to Apr 21, 2026), with the same phase gates Book 1 used, to set a baseline before buying and using Block 2\.  
> * Compare four frozen strategies under the same execution assumptions (section 4).  
> * Decide go / no-go for Block 2 (section 9).

**Label rule:** every Block 1 result in this plan is a **replay (in-sample)**. Book 1A rules were partly shaped by Book 1 results (RH1, T8, L1 kept and the \+0.5 R break-even and the lava band removed after Book 1 results; T8 3 bars and L1 10 points chosen after Phase 2). No Block 1 result is ever called validation.

## **2\. Data and periods**

| Period | Dates | Sessions | Use in Book 1A |
| :---- | :---- | :---- | :---- |
| Phase 0 parity | Oct 8 and Sep 28, 2026 plus map days | 2 \+ | Engine parity for the new Book 1A features (VWAP, power-trade rebuild, families, dollar risk) |
| Phase 1 shakedown | Oct 22 – Nov 4, 2025 | 10 | Mechanics only, plus the Nov 17–19 location diagnostic (section 6). P\&L not looked at |
| Phase 2 first baseline | Nov 5 – Dec 4, 2025 | 21 | Replay: what passes and fails; Phase 3 change list frozen before Phase 3 |
| Phase 3 test changes | Dec 5, 2025 – Feb 4, 2026 | 41 | Replay: fixed comparisons (section 5\) |
| Phase 4 replay | Feb 5 – Apr 21, 2026 | 52 | Replay of the frozen Book 1A, run once. Not a holdout for Book 1A |
| Block 2 development | Apr 22 – Jun 30, 2026 | about 48 | Only after a "go" (section 9\) |
| Block 2 validation | Jul 1 – Aug 31, 2026 | about 43, minus excluded video sessions | Final confirmation, once, after the Jul–Aug check in the open items doc confirms it is untouched |
| Consistency check | Sep 1 – Oct 2, 2026 | about 23 | Consistency only (parity days, live DEMO): mechanical checks only, no P\&L inspected, no thresholds touched, never decides anything (E7) |

> * Sessions follow the Book 1 calendar (no cash session on Thanksgiving, Christmas, New Year's Day, MLK Day, Presidents' Day, Good Friday; half days included).  
> * Calibration exposure, not strategy exposure: real MenthorQ levels for Aug 21 – Oct 20, 2026 were used only to check our GEX calculation. Recorded in the register (section 8); it does not exclude those sessions as long as no strategy rule was chosen from their outcomes.  
> * If Jul – Aug 2026 turns out to have shaped any Book 1A choice beyond the excluded video sessions (Jul–Aug check, open items doc), it becomes exploratory and final confirmation moves to later unseen data. Sep – Oct 2026 data is not bought for this now.

## **3\. Blinding and freezing**

> * **Freeze before any run:** every rule and setting in sections 4, 7 and 10, the comparison list (section 5), the promotion and go / no-go rules (section 9), all dated and given a code tag.  
> * **Fresh run folder.** The engine and whoever runs it (person or agent) get only the Book 1A docs, this plan and the raw data. Book 1 result files, reports and trade lists are not available to the run.  
> * **Gates:** results are opened only at the end of each phase. Pass rules are written before the phase starts.  
> * **No tuning on results.** Between phases, only demonstrable calculation or timing errors may be fixed, each logged in the change log with its reason. A threshold is never changed because of a P\&L result.  
> * **Unresolved settings:** each one either gets a documented value chosen before any result ("ours, chosen before results"), or the feature stays logged only and the replay runs without it. Section 10 lists which path each takes.

## **4\. The four frozen strategies**

| \# | Strategy | Definition | Purpose |
| :---- | :---- | :---- | :---- |
| R1 | A0 | Book 1 baseline exactly as frozen (S1.4, map v2.3, M0) | Original baseline |
| R2 | C1 | A0 \+ FZ1 \+ L1 \+ T8 \+ RH1 exactly as frozen, M0 | Original frozen combination |
| R3 | C1 \+ risk | R2 signals unchanged, plus the C3 pre-trade dollar risk check, sizing and dollar daily limit | Separates the effect of risk control from strategy changes |
| R4 | Book 1A | Phases 1–6 docs as frozen: map, context, zones and sides, zone review with C3, E-Footprint\_Imbalances entry, exit M0, fixed (E1) | The revised framework |

> * R1 and R2 signals are never changed. E-Deep Effort Range is excluded (paused).

## **4a. Common execution assumptions (all four)**

> * Same Databento MBO data, same front contract and roll rule (NinjaTrader roll dates, back-adjusted per Phase 0).  
> * Book 1 fill model v3.5 for all four strategies (changed Nov 1, 2026, Kyron; Book 1 used it in Phases 3 and 4): market entries fill 250 ms after the bar close at the best bid / ask (1,000 ms reported as stress, set in v3.8); targets fill only 1 tick through; stops fill with 1 tick of adverse slippage beyond the stop price (below the stop for a long, above it for a short; 2 and 4 ticks reported as stress), measured from the first traded price at or beyond the stop when price jumps through it (the only difference from v3.4, which fills at the stop plus slippage; identical otherwise; see Book1A/Phase0/A1\_fill\_model\_v34\_v35\_diff.md); a same-tick stop and target counts as a stop. Correction: an earlier version of this plan said v3.4 was unchanged and that "v3.5" was only a design version; that was wrong. The P0.4 reproduction of R1 and R2 still uses each Book 1 phase's own model (v3.4 for Phases 1 and 2, v3.5 for Phases 3 and 4). Every confidence interval uses the session bootstrap with seed 20251205\.  
> * Common costs for R1–R4 (E2): round-trip commission NQ \$5.74 and MNQ \$1.88 (NinjaTrader Free pricing, \$2.87 per contract per side, confirmed by Kyron in design v3.5 and matching the Aug 14, 2026 schedule; routing fees to confirm), plus the fill model above.  
> * Risk controls (E2): the C3 dollar risk veto and sizing apply to R3 and R4 only. R1 and R2 keep their original sizing and entry eligibility. The U3 slippage allowance is used only in the pre-trade risk estimate, never added to fills, because the fill model already includes stop slippage.  
> * Sizing (R3, R4): the largest position that fits the risk budget, NQ only, whole contracts, minimum 1 NQ (U3). The contract count is recorded on every trade.  
> * R reporting: theoretical R (price move / stop distance) and realized net R (after commissions, whole-contract sizing, partial exits and fills) are both reported. Promotion uses realized net R.  
> * The original Book 1 results stay as published. The replay adds a second, standardized set (same costs for all four) next to them; neither overwrites the other.

## **5\. Fixed comparison list**

**Primary (decide promotion and go / no-go):**

> 1. R4 Book 1A vs R1 A0.  
> 2. R4 Book 1A vs R3 C1 \+ risk.  
> 3. R3 C1 \+ risk vs R2 C1 (effect of risk control alone).

**Diagnostics inside Book 1A (reported, never promoted on their own):**

> * Location arm with VWAP counted as a family vs VWAP as a tag only (C2).  
> * MAP4 high-volume areas vs MAP0 zones (AMT PO-6).  
> * Exit steps in fixed order: M0 → M-J1 → M-J2 → M-J3 → M-J4 (C5). Each step is compared with the one before. R4 is fixed at M0 throughout (E1); the steps are reported beside it. A promising M-J step becomes a new candidate for Block 2 development, never a change to R4.  
> * Quantower-style power trade vs S1.4 single print (C4).  
> * 10 NQ feasibility (hypothetical): for every eligible trade, planned dollar risk at 10 NQ, whether it fits the per-trade budget, the share of trades that fit, the account equity needed at the chosen risk %, and dollar P\&L and max drawdown at a fixed 10 NQ. Labelled hypothetical: a fixed 10 NQ can break the account's risk rules.  
> * MNQ feasibility (diagnostic only, not promotable): for every trade rejected as RISK\_REJECT under NQ-only sizing, whether it would fit with MNQ (\$0.50 per tick, \$1.88 round trip) and what it would have done. Shows whether NQ-only sizing is excluding otherwise valid trades.  
> * L2 diagnostics (logged only, never gates), from the Oct 28 L2 doc (now "Book 1B: L2 screen (parked)"), adjusted for this plan. Data: L2F 1.0 one-second features rebuilt from MBO (30 levels per side, live-visible only), run only after the L2F audit, the fixed-price build and the coverage list are done. Measured at the zone's near edge, at prices inside the visible 30 levels (7.5 points from the best price); two missing codes, never combined: NOT\_VISIBLE (the price is outside the 30-level book) and DATA\_MISSING (too few valid depth updates in the window). Only book states from seconds completed before the decision timestamp are used (the touch for E2, the retest confirmation for E4, the entry for E1). Coverage is reported by setup type, session time, zone distance, market context and outcome; the outcome split is diagnostic only and never used to set coverage rules, so a signal cannot look useful just because of which trades were measurable. Tercile cut-offs come from Phase 2 replay candidates' feature values only, never their outcomes, and are frozen before Phase 3\.  
> * E1 refill defense: on R4 RESPONSE candidates, defending-side refill at the zone edge over the 30 s before entry (bid\_refill for longs, ask\_refill for shorts), tagged by tercile. Overlap reported with the passive trap tag and with T8.  
> * E2 defense pulled before the touch: defending-side size at the zone edge falls during the 60 s before the touch with no trades against it (bottom tercile of stack minus pull). Tag only, not a veto.  
> * E4 book flip on the retest: on R4 RH1 retests, the broken side held resting size at the zone edge for at least N of the 60 s before the break, and on the retest that size is gone and the other side shows size through the confirmation bar. N frozen before the run (U11). Overlap reported with RETEST\_AT\_NEW\_IMB; closest fit to Jeron's "created, retested, sell off" (Part 4, 00:09:08).  
> * Exit cue (a), absorption against the trade: in any of the first 3 one-minute bars after entry, a bar whose delta is in the trade's direction but closes against it triggers an exit at market 250 ms after that bar's close. Reported beside M0 and the M-J steps; [Book 1 result redacted].  
> * GEX diagnostics (from the Oct 29 GEX doc, now "Book 1C: GEX screen (parked)"): V2 random-level twin, the same R4 zones with the gamma levels replaced by random and round-number levels at matched distances, to show whether the GEX family adds anything; V3 second flip estimate, a simple zero crossing of cumulative net GEX beside our HVL, logging regime agreement and distance; V5 days without valid GEX levels stay in the baseline and drop out of the GEX group, with counts reported; volatility control (Oct 29 \#57): regime results repeated within ATM implied-volatility terciles computed from the same CME option files, so a regime effect that is really volatility shows up.  
> * Every result is split by gamma regime (positive, negative, all) and by time of day (08:30–08:45, 08:45–10:00, 10:00–13:00, after 13:00 CT). Context GEX tags (hvl\_side, cr\_ps\_width, pin\_zone, pc\_gamma\_ratio) are reported with the outcome of the trades they mark.  
> * CVD diagnostics (from the parked "Book 1D: CVD screen"): CVD\_DIV outcomes by case and by WITH / AGAINST, with AT\_ENTRY, PROVISIONAL and POST\_ENTRY reported separately and never combined; overlap with T8 and the passive trap tag; cvd\_slope\_5 by tercile (already logged, never analysed); grade without CVD (CVD doc O11) as a counterfactual on R4, not a new grade; BREAKOUT\_SPEED raw values against outcome; the 08:30 vs 17:00 CT CVD reset; swing pairs excluded by the 60-minute window. Descriptive only: no CVD diagnostic changes R4's entries or exits.  
> * Every logged tag in the phase docs (light proof, delta vs session, passive trap, first touch, side\_conflict, draw\_status, NEW\_TARGET\_NEEDED, etc.), with the outcome of the trades it would have changed.

No comparison is added after results are seen. A new idea goes to Block 2 development, not into this replay. Wide-zone eligibility report (descriptive, added Nov 4, 2026): for every decision zone whose 1 NQ risk exceeds the budget (9 zones on the 13 Phase 0 days), its merged width, constituent levels and families, planned stop and 1 NQ risk, whether it was rejected only for risk, whether a pre-existing structural invalidation level was available, and whether MNQ would have fit; zone counts and trade counts reported separately. Registered for Block 2 development, not run in this replay: a stop-model comparison of the current full-zone stop, a structural-invalidation stop and a component-level stop, each identifiable before entry, measured on risk rejection, size, stop-out rate, net R, drawdown and eligibility. Parked side screens, not run in this replay: Book 1B (L2), Book 1C (GEX), Book 1D (CVD) and Book 1E (other traders' order-flow rules, not Jeron).

## **6\. Phase gates (same sequence as Book 1\)**

> * **Phase 0:** first reproduce R1 and R2 signals and fills under the original Book 1 assumptions (E5). A separate checker, not the runner, compares them with the Book 1 trade lists and returns only pass / fail and the mismatches, so the run stays blind to Book 1 results. Then parity gates for the new code (VWAP at 08:10 matches a hand calculation; power-trade rebuild matches Quantower on sample bars where available; family counts match a hand-built zone list; dollar risk check rejects a test trade above budget). A systematic difference is fixed in code, never absorbed by a threshold.  
> * **Phase 1:** shakedown (mechanics only) and the Nov 17–19, 2025 location diagnostic. For each day: overlap of our zones with Jeron's marked zones, same auction purpose, correct side, and whether every input existed before the open. Fix only calculation or timing errors. The map is never adjusted just to make it reproduce the three days: they are known examples, not evidence. CVD definition check (Book 1D P4): rebuild Oct 24, 27, 28 and 29, 2025 and compare CVD\_DIV with the swings in Jeron's CVD video. The calculation must follow the frozen definition and use only data available at the time; the algorithm is not required to find every divergence he points out, and any disagreement is documented, never tuned away.  
> * **Phase 2:** R1–R4 report cards; what-fails-and-why; Phase 3 change list (only items already in section 5\) frozen before Phase 3\.  
> * **Phase 3:** the fixed comparisons; R4's final configuration (always M0, E1) declared in writing and replayed as one strategy before it is frozen.  
> * **Phase 4 replay:** R1–R4 once, frozen.

## **7\. Specification frozen for the replay (from the phase docs)**

> * VWAP: AMT PO-8 definition (overnight session VWAP from 17:00 CT, weekly from Sunday 17:00 CT, ±1σ bands, trades before 08:10:00 CT only, one family).  
> * Zones: six source families, minimum 2 (Phase 3, C1); a gamma level counts inside the zone or within 10 points of its edge; families= and levels= written on each zone.  
> * Context: market\_context and draw\_status as separate fields (Phase 2, C6).  
> * Risk: pre-trade dollar check, dollar daily limit, RISK\_REJECT and RISK\_BREACH\_FILL logging (Phase 4, C3); 3 trades and the 2-loss halt.  
> * Power trade: R4 uses S1.4's single print; the Quantower-style rebuild (total volume in a time window) is logged only (Phase 5, C4; U2).  
> * Exits: M0 primary; M-J1 and M-J2 diagnostics; M-J3 and M-J4 deferred (U4, U5); no runner only on Balanced days with positive gamma; stops never loosened (Phase 6, C5).

## **8\. Exposure register (mandatory)**

Every session analyzed in a Jeron video is excluded from final validation metrics at the session level (the whole session, not only the trade shown). Exposed sessions can still be used for diagnostics. Dates not yet confirmed from the video itself stay **unresolved** and are treated as excluded until checked.

| Video | Confirmed trading dates | Excluded sessions | Status | Rules informed |
| :---- | :---- | :---- | :---- | :---- |
| Part 1, Past 90 Days Using This Strategy | Week of Nov 17–21, 2025 (Mon to Wed analyzed in detail) | Nov 17–21, 2025 | Confirmed week; which of Nov 20–21 are analyzed to check | AMT PO-1 to PO-13, ladder, retest (RH1), stop at invalidation, power-trade settings |
| Part 2, Stop Taking Bad Entries | Week of Nov 24–26, 2025 | Nov 24–26, 2025 | Confirmed week | Context, invalidation, counter-context targets, deep effort exits, all-time-high profile (O1) |
| Part 3, How I Frame Every Trade | Jan 12, 2026 (gold example, "This was the 12th"); Jan 14, 2026 (gold example, "I think it was the 14th"); Fri Jan 16, 2026 (NQ example, NQH6, "last week on Friday"; transcript-derived date, pending tape confirmation) | Jan 12, Jan 14 and Jan 16, 2026 (session level, whatever the instrument) | EXPOSED (Kyron, Nov 8, 2026); Jan 16 pending tape confirmation | Overnight inventory, trapped side, VWAP grade, re-entry, stop and reverse |
| Part 4, Here's Exactly How | Not confirmed | Unresolved | Unresolved | Value follows price, edge control, counter-context proof |
| Part 5, 45 Days Using This | About Apr 2, 2026 (approximate, not confirmed as a trading date) | Unresolved | Unresolved | Gamma regime, no runner, gamma magnets, next-level targets |
| Part 6, Order Flow and GEX Levels | About Apr 9, 2026 (approximate, not confirmed as a trading date) | Unresolved | Unresolved | Balance extremes, gamma as a source, opposite gamma target |
| Gamma Levels Explained (Jul 31 recap) | Fri Jul 31, 2026 (stated in the video) | Jul 31, 2026; Jul 29–30 also described as context (to check) | Jul 31 confirmed; Jul 29–30 unresolved | ES / 10-year / VIX, first-touch fade, who has to prove it, done after a win |
| Trading NQ – Trade Recap | Likely Thu Jul 30, 2026 (the Jul 31 video calls it "the same recap that I made on Thursday") | Jul 30, 2026 (treated as excluded) | Unresolved | ES level, 10-year and VIX alignment, partials at put support |
| Strategy In 30 Minutes | Not confirmed | Unresolved | Unresolved | Order of operations, edges not middle, fourth test, 21 EMA / CVD |
| Jerontrades webinar | Not confirmed | Unresolved | Unresolved | Stop and sizing, GEX regime, deep effort as last resort |
| 60k Profit | Not confirmed | Unresolved | Unresolved | To list |
| Jeron CVD video, "I made \$50,000 this week, here's how" | Oct 24 (CPI), 27, 28 and 29 (FOMC), 2025 (from the video summary) | Oct 24, 27, 28, 29, 2025 (all Phase 1 debug days, no validation impact) | Confirmed from the video summary; recheck against the video | CVD\_DIV swing-pair divergence, Phase 1 CVD definition check (Book 1D P4) |
| MenthorQ level check (calibration, not a video) | Aug 21 – Oct 20, 2026 | None (levels only) | Recorded | GEX calculation match only |

## **9\. Promotion and go / no-go rules**

> * **Primary comparisons (Phase 3 replay):** the Book 1 promotion rule: paired net R per session; 90% session-bootstrap lower bound of the paired difference above 0; max drawdown no worse than 1.25× the comparator; at least 20 trades that differ; still at or above the comparator under 2-tick stop slippage. Otherwise "insufficient evidence".  
> * **Phase 4 replay rule:** the Book 1 holdout rule: net R per session above 0 with the 90% bootstrap lower bound above −0.1 R; max drawdown within 1.5× the Phase 3 drawdown of the same configuration; any planned-risk violation (a trade entered with planned risk above the per-trade budget or the remaining daily budget) is an automatic fail (E3). Execution breaches (a realized loss above plan from a gap or a slipped stop) are reported as a count and the largest dollar overrun, against a provisional research gate frozen before the run: fail if more than one execution breach, or any single overrun above 25% of the daily limit. The live account's own limits replace this gate later.  
> * **Also reported for every comparison:** paired daily results, confidence intervals, max drawdown, number of changed trades, RISK\_REJECT count and RISK\_BREACH\_FILL events. Net R alone never decides.  
> * **Go / no-go for Block 2:**  
  * R4 passes: Book 1A goes to Block 2 (E4). Only R3 passes: C1 with risk controls goes to Block 2, not Book 1A (C1 includes FZ1, which is not Jeron). Both pass: both go, as separately frozen candidates.  
  * Neither passes: no Block 2 data is bought solely for validation. Record why, and research on Block 1 diagnostics first.  
  * A replay pass is a reason to test on Block 2, never proof the strategy works.

## **10\. Unresolved settings and how each is handled**

| \# | Setting | Phase | Path before the replay |
| :---- | :---- | :---- | :---- |
| U1 | VWAP roll-day restart | 1 AMT | Freeze as written in PO-8 (ours) |
| U2 | Power-trade time interval, size inside 300–500, trade-size and delta filters | 5 Entry | Decided Nov 1: R4 keeps S1.4's single-print gate. The Quantower-style rebuild is a logged diagnostic until its settings are established from documentation or reference examples, never from results |
| U3 | Per-trade risk budget, dollar daily loss limit, commission per contract, slippage allowance | 4 Zone review | Commission frozen: NQ \$5.74, MNQ \$1.88 round trip (routing to confirm). Frozen Nov 1, 2026 (Kyron): simulated research balance \$100,000; risk 1% \= \$1,000 per trade; daily loss limit \$2,000; NQ only, whole contracts, minimum 1 NQ. A trade whose planned risk for 1 NQ is above the budget (stop wider than about 196 ticks / 49 points) is rejected (RISK\_REJECT), never shrunk. Slippage allowance in the risk estimate: 2 ticks per contract on the stop (the fill model's stress case), confirmed Nov 1; never added again to actual fills. Pre-trade formula: estimated risk \= (stop ticks \+ 2\) × \$5 × N \+ \$5.74 × N, with N \= NQ contracts; N \= the largest whole number with estimated risk ≤ \$1,000 (and ≤ the remaining daily budget); N and the estimate are logged before each order. Largest stop that fits: 1 NQ 196 ticks, 2 NQ 96, 3 NQ 63, 5 NQ 36, 10 NQ 16\. Example: a 60-tick stop at 3 NQ \= \$947.22 (fits); 4 NQ \= \$1,262.96 (does not). The dollar daily limit and the 2-loss halt both apply and trading stops at whichever comes first; they are not equivalent. Purpose: decides which trades are taken, their size, when the day stops, and the dollar pass / fail rules |
| U4 | M-J2 position split and target order; M-J step progression rule | 6 Targets and exit | Decided Nov 1: R4 stays M0. M-J1 (diagnostic): the whole position exits at the ladder RUN target, else TP2, else TP1 (ours). M-J2 (diagnostic, frozen Nov 1 from Jeron's two-mini example, Part 1, 00:17): with 2+ NQ on, 1 NQ off at TP1 and the rest to M-J1's target; stop unchanged after TP1 (break-even belongs to M-J3); not applicable to 1 NQ trades; same entry, initial stop, fills and commissions as M0; reported separately for 2, 3 and 4+ NQ, since 1 NQ is 50% of a 2 NQ trade but 20% of a 5 NQ trade. M-J3 and M-J4 deferred |
| U5 | Counter-context quick break-even trigger; new-zone definition for the trail | 6 Targets and exit | Decided Nov 1: logged only until objective triggers are specified; M-J3 / M-J4 not run |
| U6 | Gamma ranks | 2, 3, 6 | Build and freeze before the replay; if not built, ranks are left out of the GEX family |
| U7 | 1-day min / max, blind levels | 2, 3, 6 | Logged only (no definition) |
| U8 | ES level choice, 10-year and VIX thresholds and override; "far" and "thin" overnight | 2 Context | Logged only (no historical 10-year / VIX source; no Jeron numbers) |
| U9 | All-time-high profile (O1) | 1 AMT | Decided (E6): research only for this replay. Profile levels and their overlap with Book 1A zones are logged; a separate registered test later |
| U10 | Every other "needed" value in the open items doc | All | Kept at our current value, frozen as is. U11 (added Nov 1): E1 window 30 s and E2 window 60 s frozen Nov 1 (from the Oct 28 L2 doc); E4 hold time N registered before the E4 diagnostic runs, not needed for Phase 0; if the L2F audit and fixed-price build are not done, E1, E2 and E4 are not run |

## **11\. Change log**

| Date | Change | Docs | Type |
| :---- | :---- | :---- | :---- |
| Oct 31, 2026 | Phase reviews 1–6 (AMT, Context 1–7, Phase 3 1–7, Phase 4 1–6, footprint F1–F6, Phase 6 P1–P6); deep effort paused | All phase docs | Jeron-supported rules, with ours marked "needed" |
| Nov 1, 2026 | C1: decision zones counted by six source families; levels per family logged | Phase 3, AMT PO-3 | Correction (double counting) |
| Nov 1, 2026 | C2: VWAP is one source family; VWAP definition frozen at 08:10 CT; on/off diagnostic | AMT PO-8, Phase 3 | Jeron-supported (Part 1, 00:37:23; Part 3, 00:12:00) and correction (PO-3 / PO-8 conflict) |
| Nov 1, 2026 | C3: pre-trade dollar risk check, dollar daily limit, planned vs actual risk reporting | Phase 4 | Risk-control requirement |
| Nov 1, 2026 | C4: power trade \= Quantower-style total volume in a time window; Jeron's settings unknown | Phase 5 footprint | Correction (definition), settings research |
| Nov 1, 2026 | C5: nested exit steps M-J1 to M-J4; no runner only on Balanced days with positive gamma | Phase 6 footprint, Context | Jeron-supported (Part 5, 00:13:45) and research design |
| Nov 1, 2026 | C6: market\_context and draw\_status separate; NEW\_TARGET\_NEEDED logged only | Context | Correction (our label); research hypothesis |
| Nov 1, 2026 | C7: this plan, risk-compliant control, exposure register, session-level video exclusion | This doc, open items | Research design |
| Nov 1, 2026 | AMT phase list updated to the per-arm Phase 5 and Phase 6 docs (B8). Later Nov 1: E1–E7 (R4 fixed at M0; cost vs risk-control split; planned vs execution breaches; separate go / no-go outcomes; Phase 0 reproduction by a separate checker; O1 research only; Sep–Oct mechanical only), risk-based sizing (NQ only after U3), theoretical and realized net R, 10 NQ and MNQ feasibility diagnostics; U3 frozen (\$100,000, 1%, \$2,000 daily, 2-tick allowance); section 12 parameter sensitivity protocol added; L2 diagnostics E1, E2, E4 and exit cue (a) added as diagnostics (from the parked Book 1B L2 screen); bootstrap seed 20251205 aligned; fill model changed to v3.5 for all four strategies after the A1 diff (v3.4 note corrected); sensitivity thresholds confirmed and the 20% / 25% rules made flags; NOT\_VISIBLE vs DATA\_MISSING and point-in-time L2; adverse stop wording; U2, U4, U5, U11 decided; GEX distance rule (10 points), GEX diagnostics (V2, V3, V5, volatility control), regime and time-of-day splits, and Context GEX tags added from the parked Book 1C GEX screen; CVD\_DIV (with AT\_ENTRY / PROVISIONAL / POST\_ENTRY) and BREAKOUT\_SPEED tags, CVD diagnostics, the Phase 1 CVD definition check and the CVD video in the exposure register, from the parked Book 1D CVD screen; M-J1 single exit (RUN, else TP2, else TP1) and M-J2 (1 NQ off at TP1, rest to the runner) frozen as diagnostics; Phase 0 build checklist created; Nov 4: E26 (skip weekly DD when the map excludes the weekly profile; feature marked unavailable), E27 and E25 accepted with disclosure (first real flip gets a targeted review), wide decision zones kept as frozen, wide-zone eligibility report added, Block 2 stop-model comparison registered | AMT | Housekeeping |
| Nov 6, 2026 | risk-c3-v2 (Kyron, Nov 5-6, after Phase 1 mechanics; registered before any Phase 2 result). (1) Pre-trade risk check and size N use the best ask (long) / best bid (short) at the decision time as the entry reference, instead of the signal-bar reference; the U3 formula, the 2-tick allowance and every other U3 rule unchanged; integer ticks and cents. (2) Execution-breach definition for the Phase 4 gate (threshold unchanged: fail on more than 1 qualifying breach): entry risk at fill \= (\|filled entry \- stop\| / 0.25 \+ 2\) x \$5 x filled contracts \+ \$5.74 x filled contracts; a qualifying breach is entry risk at fill above min(\$1,000, remaining daily budget from the sizing engine's own accounting). Execution variance is logged; realized loss overrun is reported separately and never counts toward the gate; a breach is logged only, no automatic exit or resize. (3) Safety guards: RISK\_REJECT:NO\_QUOTE (no valid executable quote at the decision, using the existing quote-validity rules, no new staleness threshold) and RISK\_REJECT:REF\_AT\_OR\_PAST\_STOP (long: ask at or below the stop; short: bid at or above the stop). (4) Partial fills are not modelled: v3.5 fills the whole order at one price (known limitation). (5) Version: risk-c3-v2 is the controlling R3 / R4 sizing implementation for Phase 2 onward; risk-c3-v1 and its Phase 0 and Phase 1 reference ledgers are preserved unchanged for reproduction. Checker verification Nov 6: v2 reference prices, sizes, entry risk at fill and breach flags recomputed from the raw tape on all Phase 1 R3 / R4 trades; v1 reruns byte-identical to the originals; versioned sha256 references kept by the checker. | 4 Zone review (C3, U3); Phase 1 risk-c3-v2\_registration.md | Timing and sizing correction (not a performance change) |
| Nov 8, 2026 | Exposure register (section 8), Part 3 row: "Unresolved" replaced by Jan 12, 2026 (gold example), Jan 14, 2026 (gold example) and Jan 16, 2026 (NQ example, NQH6; transcript-derived date, pending tape confirmation), all three EXPOSED at session level whatever the instrument (Kyron, Nov 8, 2026; evidence K:\CVD\_Part3\_Research\results\part3\_cvd\_reference.md). All three are Phase 3 sessions; recorded in Phase 3 Step A before any Phase 3 run. Every other unresolved video stays excluded until confirmed. No strategy definition, Phase 3 rule or outcome changed. | This doc (section 8); Phase 3 registration | Exposure register update |

## **12\. Parameter sensitivity protocol (diagnostic only)**

**Status:** added Nov 1, 2026, approved by Kyron. Diagnostic only: no Block 1 result ever changes a frozen value. A proposed change goes to Block 2 development (Apr 22 – Jun 30, 2026\) and is confirmed only on eligible, untouched validation sessions. Numeric thresholds confirmed by Kyron on Nov 1, 2026\. All labels and flags are diagnostic classifications, never automatic strategy failures.

### **Parameters and values (frozen before running)**

* **Group A, entry eligibility** (question: does the threshold change which trades qualify?): delta gates 100 / **150** / 200 (with 10% held); RH1 retest window 10 / **15** / 20 bars; L1 distance 5 / **10** / 15 pts; T8 look-back 2 / **3** / 5 bars; minimum source families **2** / 3\.  
* **Group B, market interpretation** (question: does the read of structure stay consistent?): tests before favouring initiation 3 / **4** / 5; swing definition 10 / **15** / 20 bars; fast departure 0.15 / **0.25** / 0.35 ADR; acceptance time 45 / **60** / 90 min; zone width cap 30 / 40 / 50 pts; GEX level distance to the zone 5 / 10 / 20 / 35 pts (baseline 10). Bold \= baseline.

### **Method**

* One parameter at a time; every other setting stays at its baseline. Run on R4 (Book 1A, M0) over the replay Phases 2–4 (114 sessions), with results also shown by phase as chronological subperiods.  
* Group B first: location fidelity, then trades and performance. Fidelity \= share of Jeron's marked zones (Nov 17–19 and Nov 24–26, 2025, plus the screenshots) overlapped by our decision zones, and the number of extra zones. About six known days, so this is a rough guide, not a fit.  
* Reported for each value: paired daily R vs baseline with a 90% session-bootstrap interval, trades added / removed / changed, trade overlap with baseline, max drawdown, RISK\_REJECT and risk-rule failures, and results under 1-tick and 2-tick stop slippage.  
* Interactions are documented, not gridded. Known ones: zone width changes stop distance, NQ size and RISK\_REJECT; swing and departure change which rejection zones exist; minimum families interacts with VWAP on / off.

### **Classification (confirmed Nov 1, 2026, before any run)**

* **Inconclusive:** fewer than 10 trades differ from baseline, or the paired interval is too wide to tell (spans both \+0.10 and −0.10 R per session).  
* **Stable:** both neighbouring values keep the baseline's sign of net R per session, and max drawdown no more than 25% worse (see flags below).  
* **Sloped:** results move in one direction as the value rises (net R per session changes monotonically across the three values) without a sign flip.  
* **Fragile:** a neighbouring value flips the sign of net R per session, or causes a risk-rule failure.  
* Flags, reported beside the label: MATERIAL\_ELIGIBILITY\_CHANGE when 20% or more of the frozen baseline's trades change (denominator \= the baseline's eligible trade count; additions and removals reported separately). MATERIAL\_DRAWDOWN when max drawdown is 25% or more worse, shown both as a percentage and in absolute R, because a percentage misleads when the baseline drawdown is near zero.  
* Actual numbers are always shown next to the label: a parameter can look stable only because it changes almost no trades.

### **Not used as a gate**

* PBO (probability of backtest overfitting) is optional research only, not pass / fail: the design selects no winner and 41 to 114 sessions are too few for reliable partitions.
