<!-- exported 2026-11-01T20:32Z from Google Doc 107qT_z6IGbG3zooWUck9Z5LBF-_TKjGuEfFtV44MwM8, modifiedTime 2026-11-01T18:14:16.960Z -->
# **Book 1A – 5 Entry: E-Footprint\_Imbalances**

**Status:** draft v2, updated Oct 31, 2026\. Changes F1–F6 from the Phase 5 review (S1.4 gates and the Book 1 Phase 3 arms against Parts 1–6, the webinar, Strategy In 30 Minutes and the late-July recaps) were approved by Kyron on Oct 31\. Nov 1, 2026: C4 (power-trade definition) approved by Kyron. This is the only entry arm tested in Phase 5 for now: E-Deep Effort Range is paused until the indicator rebuild is checked. Shared rules are in "Book 1A – 5 Entry (overview and shared rules)".

## **What Book 1 did**

* **S1.4 gates at a zone:** raw delta 150 and delta 10% (WEAK\_DELTA, WEAK\_DELTA\_PCT), an imbalance or large trade, a displacement close, a trapped side for RESPONSE, a confirmation bar, a retrigger window of 3 bars. Grades A+, B+ and B traded; grade C (counter-context) never traded.  
* **Phase 3 (41 sessions), promoted into the frozen C1:** RH1 retest-and-hold (+0.888 R per session vs A0), FZ1 fresh zone must have held (+0.796, NOT JERON), L1 intraday zones near the plan (+0.360, barely), T8 prior absorption (+0.147, thin). C1 then failed the Phase 4 holdout on the daily-loss test.  
* **Dropped before Phase 3:** A1–A3 relaxed delta (the weak-delta blocked set lost −31 R), A4 context-scaled proof (counter-context never fired), A5 passive trap (tiny), A6 21 EMA \+ CVD average (−1.2 R), A8 relative delta (never built). A7 fight veto, RT0 no retrigger and G1 GEX gate ended "insufficient evidence".

## **Jeron's footprint entry**

* **Charts:** 5-minute footprint and Quantower 1-minute with power trades and imbalances (Part 3, 00:13:00–00:13:30, 00:29:55–00:30:05).  
* **Trapped side:** lots of selling (or buying) at the level, an imbalance or power trade, no continuation; the delta flips and the other side trades out of it (Part 3, 00:27:00–00:29:50). Passive absorption counts: aggressive selling but the candle closes green (Part 3, 00:24).  
* **Lack of interest:** at the highs, a buy imbalance with no deep trades and no buying effort, then sellers step in (Part 3, 00:11:30–00:12:10; Part 4, 00:06:01–00:06:35).  
* **Trigger:** the other side creates a new imbalance or power trade through the trapped side's imbalance: "created, retested, sell off" (Part 4, 00:09:08–00:09:18); "power trade with aggressive selling imbalance created and we're running through a buy imbalance" (Part 3, 00:17:00–00:17:20).  
* **Wait for the response:** not on the trapping bar itself (Part 3, 00:31:05).  
* **Proof scales with context:** with context, little is needed ("I don't need much confirmation", Part 4, 00:10:28; Part 5, 00:15:26–00:15:41; Gamma Levels Explained, 00:09:55–00:10:22). Against context: "power trades and deep effort and imbalances and continuation and effort being rewarded and follow through" (Part 4, 00:10:38–00:10:52).  
* **Settings (Jeron's):** imbalance 400%, 900% strong, 300% in thin sessions (Part 1, 01:32); power trades 300–500 in New York, 150–200 in Asia / London (Part 1, 01:33); deep trades filter 60, 100 when volatile (Part 1, 00:04).

## **Book 1A baseline (F1)**

* **E-Footprint\_Imbalances \= S1.4 gates \+ RH1 \+ T8 \+ L1.** These three promoted arms are Jeron's:  
* **RH1 retest and hold (initiations):** an INITIATION candidate arms a retest instead of entering; a bar touches the broken zone's near edge (within 2 ticks), then closes back outside it with a body in the trade's direction; enter on that close; stop at the retest extreme \+ 2 ticks; fail on a close 2 ticks beyond the far edge; no retest in 15 bars \= no trade (NO\_RETEST logged, missed runners counted). Jeron: Part 1, 01:30:18 ("once there is a winner, wait for a retrace"), 00:45:09; Part 4, 00:09:03; Part 5, 00:15:09. Against: Webinar, 24:29–29:50 (some initiation days do not retrace). The 15 bars, 2-tick touch and 2-tick fail are ours (needed).  
* **T8 prior absorption:** skip the candidate if any of the 3 completed bars before it had delta in the trade's direction but closed against it. Jeron: Webinar, 24:29–29:50 ("all these aggressive buyers are absorbed"); Part 2, 00:41:37–00:41:46. The 3 bars are ours, chosen after Phase 2 (needed).  
* **L1 intraday zones near the plan:** an intraday IMB or power zone may trade only if it is within 10 points of a plan DECISION zone. Jeron: Webinar, 13:04 ("I have to wait for a level to get hit"); he allows intraday levels (Webinar, 41:27–52:09). The 10 points are ours, chosen after Phase 2 (needed).  
* **Settings (F4):** imbalance 400% / 900% and power trades 300–500 for the New York session (Part 1, 01:32–01:33). The exact pick inside his power-trade range is ours (needed).  
* Power-trade definition (C4): a Quantower-style power trade, not a single print. Quantower describes power trades as "the execution of a large number of orders in a very short time": a zone is drawn when the total volume of qualifying trades inside a time interval (seconds) reaches Total Volume, with optional min / max trade size and delta filters (Quantower Help, Power Trades). Rebuilt from MBO trades as same-side aggressor volume summed over that interval; Jeron's 300–500 is that total volume. This approximates Quantower's event type, not Jeron's own settings: his time interval, trade-size and delta filters are unknown. For the Book 1A replay, S1.4's single large print stays the gate and the Quantower-style rebuild is logged only, until its settings are established from documentation or reference examples (replay plan U2, Nov 1, 2026).

## **Moved to research (logged only)**

* **FZ1 (fresh intraday zone must have held once before a break counts).** NOT JERON (outside research, evidence weak to mixed). It was strong in Book 1 Phase 3 (+0.796 R per session, 0.71 correlation with RH1), so the log records what each blocked trade would have done.

## **New logged tags (F2, F3)**

* **With-context light proof:** a with-context candidate that passes on a trapped side plus a confirmation bar, without the delta and imbalance gates. Logged twice: as is, and with the first-touch and 3+ source conditions (both ours, needed). Logged, not traded (Book 1 evidence against relaxing: weak-delta blocked set −31 R). Jeron: Part 4, 00:06:50–00:07:04, 00:10:28–00:10:52; Gamma Levels Explained, 00:09:55–00:10:22.  
* **Delta vs the session:** two measures, both logged on every candidate, then tested against the fixed 150 / 10%. (1) Jeron's: is this bar's delta the largest of the session so far, and how far does it stand out from the bars around it. (2) Ours: the ratio to the session's average bar. Jeron: Part 1, 00:55–00:56 ("the delta percentage… is a −23% while the rest of them are 7, 4, 0, 10… this is an obvious outlier"); Part 3, 00:24:00–00:24:26 ("a lot more aggressive selling at this level than there has been in any other point of the session").  
* **Passive trap:** passive absorption (aggressive volume one way, the bar closes the other way) counts as the trapped side. Logged. Jeron: Part 3, 00:24, 00:27–00:29.  
* **21 EMA and CVD average:** alignment on the 1-minute. Logged only, never a gate (Book 1 A6: −1.2 R; Jeron shorted against both in Gamma Levels Explained, 00:10:40). Jeron: Strategy In 30 Minutes, 00:17:28–00:18:00; Trade Recap, 00:05:14.  
* **Counter-context proof (F3):** a counter-context INITIATION side needs all of: a power trade in the trade's direction, an imbalance in the trade's direction, a follow-through bar closing beyond the zone with delta that way, and both closes beyond the zone (the two-close acceptance count is ours, needed). Logged first: counter-context never fired in Book 1\. Jeron: Part 4, 00:10:38–00:10:52.  
* Also logged on every candidate: the shared tags from the overview doc (VWAP grade, re-entry, fight, R at entry).  
* CVD\_DIV (Jeron swing-pair divergence; added Nov 1, 2026; logged only, never changes the grade, eligibility, stop, target or size): compare the two most recent confirmed swings (AMT PO-1 rule, 15 one-minute bars each side) at the entry zone or the session extreme, at most 60 minutes apart (our research assumption; pairs it excludes are counted). CVD \= running sum of signed executed trade volume from the MBO aggressor flag (trades only, no book changes), reset at 17:00 CT (08:30 CT reset reported as a diagnostic), sampled at each price swing's own timestamp. Four cases: high absorption (price lower high, CVD higher high); high exhaustion (price higher high, CVD lower high); low exhaustion (price lower low, CVD higher low); low absorption (price higher low, CVD lower low); each tagged WITH or AGAINST the trade. Fields: both swing times and confirmation times, price and CVD at both, case, direction, earliest knowable time, and AT\_ENTRY or POST\_ENTRY. A PROVISIONAL version compares the first confirmed swing with the extreme so far at the entry bar, which is knowable at entry. Overlap with T8, the passive trap tag and the delta gates is reported. Jeron: "I made \$50,000 this week, here's how" (Oct 29, 2025), 1:17, 2:08, 2:41, 3:11, 3:46, 4:18, 5:07, always at a session high, low or marked level.  
* BREAKOUT\_SPEED (logged only): on INITIATION entries, executed volume per second over the 60 s before the decision (trades before the decision timestamp only; 60 s ours), its percentile against the session so far, and the signed 3-bar CVD change. Raw values only, no warning label. Jeron: "a breakout without speed is a warning" (Part 2, \~00:09:00, \~00:26:00, \~00:45:01, via the Book 1 CVD review).  
* Retest at the new imbalance (RETEST\_AT\_NEW\_IMB): RH1 retests the broken zone's edge; this logs whether the retest also held at the newly created imbalance. Jeron: "it's created, retested, and we sell off" (Part 4, 00:09:08–00:09:18); "VWAP break, retest, imbalance holds, buy out of it" (Part 5, 00:15:07–00:15:11).  
* Exhaustion (EXHAUSTION): no effort at the retest of the extreme (low volume and delta) counts as a trapped side. Logged. Jeron: "Is there selling here? No… This is exhaustion. There's no more selling effort" (Part 3, 00:24:10–00:24:26); a volume tail, "last seller sells" (Part 3, 00:27:30–00:28:00).  
* 5-minute and 1-minute alignment (TF\_ALIGNED): a same-direction imbalance or power trade on the 5-minute bar at that time. Logged. Jeron: "multiple power trades on the one minute, imbalance on the one minute, power trade on the 5-minute… full alignment" (Part 3, 00:30:00–00:31:00).  
* Stacked imbalances: the count of stacked imbalances in the trade's direction. Logged. Jeron: "two stacked imbalances" (Part 3, 00:28); "multiple imbalances stacked through this candle" (Part 4, 00:08:01–00:08:05).  
* Wick stop (variant): for responses, the stop below the last trapped wick instead of beyond the zone; the R difference is logged. Jeron: two stops by trade idea (Part 2, 00:12:40–00:14:50); "this is my total invalidation point" (Part 3, 00:30:35–00:31:00).

## **Kept from S1.4 (ours, needed) (F6)**

* Raw delta 150 and delta 10% (WEAK\_DELTA / WEAK\_DELTA\_PCT): the baseline until delta vs the session is tested. Relaxing them lost in Book 1 (A1–A3). Needed: the code needs a cut-off for aggression. Jeron reads delta and delta % on every candle ("total volume, the delta of the candle and then the percentage", Part 1, 00:05) but judges it against the other candles, never a fixed number (Part 1, 00:55–00:56; Part 3, 00:24:00–00:24:26).  
* Displacement: the close beyond the zone is Jeron's ("buyers still were able to hold this level because we did not close below it", Part 1, 01:08; "when the market aggressively pushes through a high… You don't have to guess", Part 1, 00:42); the size threshold is ours (needed). Grades B and C: needed only because the S1.4 grade filter reads grades. Jeron grades A+ / B+ by VWAP (Part 3, 00:30:05–00:30:35) and calls off-context trades "a lower quality trade anyways" (Part 3, \~00:10); the B / C split could be dropped later, since the Phase 3 side rules handle counter-context.  
* Retrigger window of 3 bars. RT0 (no retrigger) was insufficient evidence. Jeron: "an initiation candle and a breakout with strength" (Part 1, 01:24:51), which leans to the breaking bar only (0); Book 1 RT0 (0 bars) was neutral (−0.041 R per session). Needed: the code must decide how long after the break a signal counts; trades from bars 1–3 are logged.  
* 15-bar dedup: one setup is counted once. Jeron re-enters by structure, not a count ("I don't want to be in shorts again till this is ran through", Part 3, 00:19:10–00:19:35; "if we dip down to 816 to 790 and hold again I can take another trade", Trade Recap, 00:07:19–00:07:27), which is a logged shared tag. One position at a time: keeps R, limits and fills checkable; it is not one contract. Jeron scales and adds ("two on", Part 1, 00:47; adds on pullbacks, Part 2, \~00:51–00:53), handled in Phase 6\. 12-tick entry slippage check: fill realism, no Jeron rule. Last entry 14:30 CT: the strategy must stop opening trades before the 14:55 flatten; Jeron gives no cut-off. He trades early ("I took this short basically right at market open", Part 4, 00:05:33–00:05:38), stops after a strong win (Part 6, 00:05:27–00:05:30), and later "we just chopped the rest of the day" (Part 2, 01:18); his game plan says "afternoon belongs to the expiry mechanics" (Gamma Levels Explained, 00:05:47–00:05:54).  
* Stop zone width \+ 2 ticks for responses; the RH1 retest stop for initiations. Size is set to the fixed risk per trade (Phase 4).

## **Moved to Phase 6 (F5)**

* Adding on pullbacks into new zones while a trade is open (Part 2, \~00:51–00:53), logged as ADD\_OPPORTUNITY.

## **Jeron check**

| Item | Source | Verdict |
| :---- | :---- | :---- |
| Trapped side, delta flip, new imbalance through the trapped one | Part 3, 00:17:00–00:17:20, 00:27:00–00:29:50; Part 4, 00:09:08 | Jeron |
| RH1 retest and hold | Part 1, 01:30:18, 00:45:09; Part 4, 00:09:03; Part 5, 00:15:09 | Jeron (15 bars, 2-tick fail ours) |
| T8 prior absorption | Webinar, 24:29–29:50; Part 2, 00:41:37 | Jeron (3 bars ours) |
| L1 intraday zones near the plan | Webinar, 13:04, 41:27–52:09 | Jeron (10 points ours) |
| Imbalance 400% / 900%; power trades 300–500 (New York) | Part 1, 01:32–01:33 | Jeron (exact pick and time window ours) |
| FZ1 fresh zone must have held | Outside research | Not Jeron: research |
| With-context light proof | Part 4, 00:10:28; Gamma Levels Explained, 00:09:55–00:10:22 | Jeron (logged) |
| Delta vs the session | Part 3, 00:24:00–00:24:26 | Jeron (logged, then tested) |
| Passive trap | Part 3, 00:24, 00:27–00:29 | Jeron (logged) |
| 21 EMA and CVD average | Strategy In 30, 00:17:28; Trade Recap, 00:05:14 | Jeron (logged only) |
| Counter-context proof list | Part 4, 00:10:38–00:10:52 | Jeron (logged first) |
| Retest held at the new imbalance | Part 4, 00:09:08–00:09:18; Part 5, 00:15:07–00:15:11 | Jeron (logged) |
| Exhaustion as a trapped side | Part 3, 00:24:10–00:24:26, 00:27:30–00:28:00 | Jeron (logged) |
| 5-minute and 1-minute alignment | Part 3, 00:30:00–00:31:00 | Jeron (logged) |
| Stacked imbalances | Part 3, 00:28; Part 4, 00:08:01–00:08:05 | Jeron (logged) |
| Wick stop for responses | Part 2, 00:12:40–00:14:50; Part 3, 00:30:35–00:31:00 | Jeron (logged variant) |
| Large trade \= Quantower power trade (burst) | Part 1, 01:33; Webinar, 52:55 | Check needed |
| Delta 150 / 10%, displacement, grades B / C, retrigger 3 bars | Jeron: delta vs other candles (Part 1, 00:55–00:56; Part 3, 00:24); strength on the breaking bar (Part 1, 01:24:51); close beyond (Part 1, 01:08); grades A+ / B+ only (Part 3, 00:30:05). No numbers | Ours (needed) |
| Dedup, one position, entry slippage, last entry 14:30 CT | Engine rules. Jeron re-enters by structure (Part 3, 00:19:10; Trade Recap, 00:07:19), adds to winners (Part 2, \~00:51), trades early (Part 4, 00:05:33); no cut-off | Ours (needed) |

## **Needed (Jeron gives the idea, no specifics)**

* The power-trade size inside 300–500 for NQ in New York, and the time interval, trade-size and delta filters of the Quantower-style rebuild (C4). Unresolved until frozen before the replay; never picked by backtest result. First check that S1.4's large-trade definition matches a Quantower power trade (a burst of trades in a short time, not a single print).  
* RH1 window and fail tolerance (ours: 15 bars, 2 ticks); T8 look-back (ours: 3 bars); L1 distance (ours: 10 points).  
* Whether delta vs the session replaces the fixed 150 / 10% (test).  
* The R minimums at entry and the fixed risk per trade (Phase 4).

## **Test**

* Phase 5 runs this arm alone for now. Reported against Book 1 A0 on the same sessions, with the Book 1 promotion rule (paired net R, bootstrap 90% lower bound \> 0, drawdown ≤ 1.25× A0, ≥ 20 differing trades).  
* Logged per trade and candidate: entry bar, stop, R at TP1 / TP2 / runner, RH1 outcome (entered, failed, no retest, runner missed), every new tag, and what FZ1 would have done.  
* Book 1 C1 failed the holdout on the daily-loss test, so the Phase 4 sizing and daily limits are part of this run.
