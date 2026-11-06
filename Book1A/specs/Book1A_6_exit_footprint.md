<!-- exported 2026-11-01T21:18Z from Google Doc 10FjFGf59x6L5VKCpwenRTNX6Dy2YAov4OsCNVi_tIfw, modifiedTime 2026-11-01T19:28:54.565Z -->
# **Book 1A – 6 Targets and exit: E-Footprint\_Imbalances**

**Status:** draft v2, updated Oct 31, 2026\. Changes P1–P6 from the Phase 6 review (Book 1 exit models M0–M3 and M2E against Parts 1–6, the webinar and the late-July recaps) were approved by Kyron on Oct 31\. Nov 1, 2026: C5 (nested M-J steps; no runner only on Balanced days with positive gamma) approved by Kyron. This doc covers the E-Footprint\_Imbalances arm only; E-Deep Effort Range has its own Phase 6 doc in its folder (paused). Applies to Book 1A only.  
**Phase order:** 1 AMT (the map) → 2 Context → 3 Zone selection and side rules → 4 Zone review (go / no-go) → 5 Entry (E-Footprint\_Imbalances) → **6 Targets and exit (E-Footprint\_Imbalances)**.

## **What Book 1 did**

* **M0 (traded):** one stop beyond the zone, one target at the nearest qualified level (S1.4), flatten at 14:55 CT. Phase 2: −6.55 R.  
* **Exit models tested against M0 (all lost):** M2 partials −8.20 R; M1 −7.71 R; M1a −11.22 R; fixed break-even at \+0.5 R −8.04 R; M3 never traded. In Phase 3 the zone-trail exit M2E lost −0.268 R per session and failed the 2-tick check.  
* **Finding kept:** 16 of 26 losers were up 0.5 R or more before a full stop. This is why the exit question stays open, but the Book 1 fixes for it all lost.

## **Target ladder (P1)**

* **Written by the pre-open plan** for every decision zone and open side: TP1 \= the nearest rejection or flip zone (AMT PO-1), else the nearest value edge, POC or HVN; TP2 \= the nearest HVN area (AMT PO-6) or delta band (AMT PO-7) beyond TP1; RUNNER \= the opposite edge of the value area price is trading into (weekly first, then PD), else the context draw (Phase 2), or the far edge of a double distribution (AMT PO-11).  
* **Added level types (P1):** prior highs and lows, settlement on inventory days, and the calculated gamma levels (call resistance, put support, HVL, 0DTE levels) count as ladder levels. The Book 1 exclusion list is removed: no level type is barred from the ladder.  
* **Jeron for the added levels:** opposite gamma level as the target, short at call resistance to put support (Part 6, 00:04:38–00:04:46); trade to the next significant level, gamma 2 at prior highs (Part 5, 00:07:52–00:08:08; Part 6, 00:05:58–00:06:10); partials at put support, all out at yesterday's high (Trade Recap, 00:05:19–00:05:31); settlement as a level on inventory days (Part 3, \~00:06).  
* **Jeron for the ladder:** "This would be target one" (Part 1, 00:13:06); "that could be TP1. Where could TP2 be? … the area where we know there was a lot of selling activity… if we wanted to hold a runner… to the value area high" (Part 1, 00:17:35–00:17:58); "if our final target is the value area high of the weekly profile, this is a 5:1" (Part 1, 01:10:33); "target higher time frame levels" (Part 1, 01:30:25).  
* Written as ladder=\<zone label\>\|\<long or short\>\|TP1=\<lo\>-\<hi\>\|TP2=\<lo\>-\<hi\>\|RUN=\<lo\>-\<hi\>. The ladder also feeds the R log in Phase 4\. Gamma levels come from our own calculation (Databento, MenthorQ method), not from MenthorQ.

## **Exit model M-J (P2), tested against M0 in nested steps (C5)**

* **Scale out at TP1, TP2 and RUN.** Jeron sizes to scale out (Part 1, 00:17) and names all three steps (Part 1, 00:17:35–00:17:58). The split per step is ours (needed).  
* **Break-even after TP1.** Jeron: Part 1, 01:14–01:17.  
* **Trail after TP1:** the stop moves beyond each new same-side footprint zone that forms after TP1 (Part 1, 01:14–01:17). Not from entry.  
* **Balanced \+ positive gamma: no runner.** Only on days that are Balanced (Phase 2\) with positive gamma does the trade end at TP2; other positive-gamma days keep the runner (C5). "I'm not going to try to hold runners" inside a balanced range whose edges are gamma levels (Part 5, 00:13:45–00:14:03). Regime from the calculated gamma levels (Phase 2).  
* **Counter-context: first target only, quick break-even.** A trade against the context targets only VWAP, the POC or at most the value edge (Part 2, 01:24:17–01:26:00). Tracker v2.4 already enforces the target. With the context, hold the runner to the higher-time-frame draw (Part 2, 01:27:02–01:27:22). The quick break-even trigger is ours (needed).  
* **Book 1 warning:** M2 partials lost to M0 in Book 1 (−8.20 R vs −6.55 R). M-J differs (break-even and trail only after TP1, ladder targets, regime and context rules), but it has to beat M0 under the Book 1 promotion rule before it replaces it.  
* Nested steps (C5), order fixed in advance, each compared with the step before: M0 (single target, control) → M-J1 (ladder targets, single exit: the whole position exits at RUN, else TP2, else TP1; ours, frozen Nov 1, 2026\) → M-J2 (+ 1 NQ off at TP1 when 2 or more NQ are on, the rest to M-J1's target; stop unchanged after TP1; frozen Nov 1, 2026 from Jeron's two-mini example, Part 1, 00:17) → M-J3 (+ break-even and structural trail after TP1) → M-J4 (+ the Balanced-positive-gamma no-runner and counter-context first-target rules). The position split and target order are frozen before M-J2 runs. Moving to the next step is not automatic: the progression and comparison rules are written in the Book 1A replay plan, and the steps are diagnostics inside Book 1A, not separate strategies to promote. Break-even and trailing never move a stop to a less protective level. For the Block 1 replay (replay plan U4, U5, Nov 1, 2026): M-J1 and M-J2 are diagnostics only (same entry, initial stop, fills and commissions as M0; M-J2 not applicable to 1 NQ trades; reported by initial size 2, 3 and 4+ NQ); M-J3 and M-J4 are deferred until their settings are defined independently of results.

## **Logged variants (P3, P6)**

* **Exit when the other side is rewarded (P3):** exit the whole position on the first bar where the trapped side is put underwater and the other side is rewarded. Logged as "what if", not traded. Jeron: "This is the first time sellers were put underwater and buyers were rewarded. We want to get out cuz that's the first time that this market could reverse on us" (Part 1, 00:53:26–00:53:44).  
* **Add-ons (P6):** adding on pullbacks into new same-side zones while a trade is open (Part 2, \~00:51–00:53). Logged as ADD\_OPPORTUNITY only, never traded.

## **Removed (P4)**

* **Fixed break-even at \+0.5 R.** Ours. Lost in Book 1 (−8.04 R vs M0 −6.55 R). Jeron moves to break-even after TP1, not at a fixed R.  
* **Trail from entry (M1 / M1a, M2E).** Ours for this arm. Lost in Book 1 (M1 −7.71 R, M1a −11.22 R; M2E −0.268 R per session, failed the 2-tick check). Jeron trails from entry only on deep effort trades (see the E-Deep Effort Range Phase 6 doc).

## **Kept (P5, ours, needed)**

* **M0 stays the baseline:** one target, stop beyond the zone. Every exit change is measured against it.  
* **Flatten at 14:55 CT.** Ours; no Jeron rule. Needed so no position is held into the close.

## **Jeron check**

| Item | Source | Verdict |
| :---- | :---- | :---- |
| TP1 / TP2 / runner ladder | Part 1, 00:13:06, 00:17:35–00:17:58, 01:10:33 | Jeron |
| Runner to the higher-time-frame draw | Part 2, 01:27:02–01:27:22; Part 1, 01:30:25 | Jeron |
| Gamma levels as targets (opposite level, next level) | Part 6, 00:04:38–00:04:46, 00:05:58–00:06:10; Part 5, 00:07:52–00:08:08 | Jeron (calculated levels) |
| Prior highs / lows as targets | Trade Recap, 00:05:19–00:05:31; Part 6, 00:05:58 | Jeron |
| Settlement on inventory days | Part 3, \~00:06 | Jeron |
| Exclusion list | Contradicts the rows above | Removed |
| Scale out at TP1 / TP2 / RUN | Part 1, 00:17, 00:17:35–00:17:58 | Jeron (split ours) |
| Break-even and trail after TP1 | Part 1, 01:14–01:17 | Jeron |
| Balanced \+ positive gamma: no runner | Part 5, 00:13:45–00:14:03 | Jeron |
| Counter-context: first target only | Part 2, 01:24:17–01:26:00 | Jeron (quick break-even ours) |
| Exit when the other side is rewarded | Part 1, 00:53:26–00:53:44 | Jeron (logged variant) |
| Add-ons into new zones | Part 2, \~00:51–00:53 | Jeron (logged only) |
| Fixed break-even at \+0.5 R | Book 1: −8.04 R | Ours, failed: removed |
| Trail from entry (M1, M1a, M2E) | Book 1: all lost | Ours, failed: removed |
| M0 baseline, 14:55 CT flatten | Engine rules | Ours (needed) |

## **Needed (Jeron gives the idea, no specifics)**

* The size split across TP1, TP2 and RUN (ours to pick and pre-register).  
* The quick break-even trigger on counter-context trades.  
* What counts as a new same-side zone for the trail after TP1 (uses the Phase 5 footprint zone rules).  
* Gamma rank levels (gamma 1, gamma 2\) can be built from our data now; one-day min / max and blind levels are still missing.

## **Test**

* Every Book 1A run logs, for each trade, which ladder step price reached first (TP1, TP2, RUN or stop), and the R at each step.  
* M-J is pre-registered and run against M0 on the same trades from E-Footprint\_Imbalances, with the Book 1 promotion rule (paired net R, bootstrap 90% lower bound \> 0, drawdown ≤ 1.25× M0, ≥ 20 differing trades). The positive-gamma and counter-context parts are reported on their own as well (step M-J4).  
* The logged variants (exit when the other side is rewarded, add-ons) are reported as "what if" next to M0 and M-J.


