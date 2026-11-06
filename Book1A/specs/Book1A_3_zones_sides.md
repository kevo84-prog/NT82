<!-- exported 2026-11-01T20:32Z from Google Doc 1v85SXOa5VMMwn1wIfXsqkMZExPOQQwY9WRwzpN44CcY, modifiedTime 2026-11-01T17:59:37.793Z -->
# **Book 1A – 3 Zone selection and side rules**

**Status:** draft v2, updated Oct 31, 2026\. Changes 1–7 from the review of Parts 1–6 and the other Jeron videos were approved by Kyron on Oct 31\. Gamma levels are your calculated GEX levels (Databento data, MenthorQ method); MenthorQ itself is not used in Book 1A. Follow-up changes approved the same day: the 1-ADR filter and the 60-point cut move to research, and the most restrictive rule wins when rules disagree. Nov 1, 2026: C1 (count sources by family, six families) and C2 (VWAP is one family) approved by Kyron. Applies to Book 1A only.  
**Phase order:** 1 AMT (the map) → 2 Context → **3 Zone selection and side rules** → 4 Zone review (go / no-go) → 5 Entry → 6 Targets and exit.

## **What Book 1 did**

* **Zone selection.** A decision zone was a level found in 2+ independent periods; at most 2 per side of price within 1 ADR; touching neighbours merged; zones wider than 60 points cut back to the levels nearest the middle; single-source levels became targets. The Claude plan also weighed TPO, single-print, LVN and HVN tags.  
* **Gamma levels.** "Do not move, add or drop a zone because of a MenthorQ level" (prompt v1.5); GEX lines were logged only. The backtest replaced MenthorQ with the calculated GEX levels.  
* **Side rules.** With-context side ANY; counter-context side INITIATION. A zone tested 4+ times with lower highs or higher lows: INITIATION through it, NONE off it. A zone crossed both ways in the last day: NONE. The middle third of the balance was lava (no trades).

## **Removed (not kept as research)**

* **"Crossed both ways in the last day → NONE."** It switched off Jeron's Tuesday short zone (24,846–24,865) and all five Wednesday zones on Nov 18–19, 2025, and helped make Nov 12 and Nov 19 LOG\_ONLY. Part 1 says the opposite: a level that flipped matters more (00:12:08).  
* **Lava band** (middle third of the balance, 15 points clear). Phase 2: 60 candidates blocked, winner ticks \+2,785 vs loser ticks −2,516: no measurable value. Jeron's own idea (skip the middle) is kept in a narrower form: zone rule 3\.  
* **"NONE off a zone tested 4+ times."** Ours, and it contradicts Jeron: he takes the response off a zone the testing side keeps failing at (Part 2, 00:42–00:43, "It's safe to take a short here"; Part 3, \~00:04 and \~00:14–00:16, two months of shorts at the same supply). The INITIATION-through part stays (side rule 2).  
* **"Do not move, add or drop a zone because of a MenthorQ level."** Ours, and it contradicts Jeron, who counts gamma levels toward a zone's importance. Replaced by zone rule 2\.  
* **"2+ independent periods."** Replaced by 2+ independent sources (zone rule 1).

## **Zone selection (Book 1A)**

### **1\. Decision zones by confluence**

* **Rule:** a decision zone is a price area where sources from 2+ of six families line up (C1). Families: (1) auction value: weekly, PD, ON, composite or merged-balance value edges; (2) rejection and structure: rejection or flip zones (AMT PO-1), double distribution edges and structural extremes; (3) delta control: delta profile bands (AMT PO-7); (4) volume distribution: POCs, HVN areas (AMT PO-6), LVN, low-time and single-print areas; (5) calculated GEX: call resistance, put support, HVL, 0DTE levels and gamma ranks (zone rule 2); (6) VWAP: overnight session VWAP, weekly VWAP and the ±1σ bands (AMT PO-8, C2). Each family counts at most once, however many of its levels overlap. The families are a practical guard against double counting, not proof of statistical independence. The plan writes families=\<n\>\|\<list\> and levels=\<n\>\|\<list\> on each zone (every individual level is kept, so the number of levels per family can be studied later); the family count is logged as the confluence grade.  
* **Jeron:** Part 6, 00:03:29–00:03:44 ("Value area highs, I have call resistance, I have strong selling pressure… and then another area that the market is not spending a lot of time in"); Part 4, 00:04:58–00:05:27 ("now we have full alignment"); Gamma Levels Explained, 00:03:31–00:04:15 (last week's VAL, single print, strong delta sellers, support-to-resistance pivot, gamma levels: "everything's aligned"); Strategy In 30 Minutes, 00:05:55–00:06:09.  
* **Needed:** the minimum of 2 families is ours. Jeron's examples have 3 to 5\.

### **2\. Calculated gamma levels count as a source**

* **Rule:** call resistance, put support, the high volatility level, the 0DTE levels and gamma ranks from the calculated GEX levels together form one family (calculated GEX) toward zone rule 1 (C1); the number of gamma levels in the zone is logged. A gamma level counts if it is inside the zone or within 10 points of its edge (ours, Nov 1, 2026: Jeron gives no tolerance, and his one example has seller pressure about 10 points above call resistance, Part 6, 00:02:01–00:02:23). Sensitivity: 5, 20 and 35 points (replay plan section 12). They are also draw candidates (Context, input 6).  
* **Jeron:** Part 4, 00:04:58–00:05:13 (value area high \+ delta profile \+ "call resistance and a gamma wall"); Part 6, 00:04:19–00:04:40; Gamma Levels Explained, 00:04:37–00:05:07.  
* **Needed:** gamma ranks (gamma 1, gamma 2…: rank strikes by the size of net GEX; can be built now); 1-day min / max and blind levels (MenthorQ's own levels, no published method; a formula would need to be defined and checked against the MenthorQ month).

### **3\. Balanced days: trade the edges, not the middle**

* **Rule:** on a Balanced day (Context), decision zones sit at the edges of the merged balance. The balance POC is a TARGET only, never a decision zone.  
* **Jeron:** Part 6, 00:02:23–00:02:52 ("I don't want to trade at the POC… wait to trade the extremes of the range"); Strategy In 30 Minutes, 00:10:16 ("Trade the edges, skip the middle") and 00:11:41 ("The middle is still lava", from his game plan); Part 1, 01:03 (at the POC at the open: "I'm not going to guess").

### **Kept from Book 1 (ours, needed)**

* Up to 2 decision zones per side. Needed: the plan must cap the list, and Jeron trades a few key levels ("the only significant level that I'm seeing so far", Gamma Levels Explained, 00:03:31; Part 5, 00:14:07) but gives no count, so 2 is ours.  
* Touching neighbours are merged. Needed: the plan format rejects overlapping zones. Single-source levels become targets (reviewed in Phase 6).  
* Moved to research (logged only): the 1-ADR distance filter and the 60-point width cut. The plan logs which zones each would have dropped or cut. Zone rule 1 (2+ sources) already filters weak far-away levels, and Phase 4 check C (stop cap) and the Phase 5 stop handle the risk of a wide zone. Jeron's zones can be wider (650–750, Gamma Levels Explained, 00:03:38–00:03:44; the A+ fade at 675–757, 00:06:12), and his stop was about 20 points (Part 6, 00:05:19), not the zone width.

## **Side rules (Book 1A)**

Every side rule answers Jeron's question "who has to prove what, where" (Gamma Levels Explained, 00:09:03–00:09:22).

### **Kept**

* **1\. Context sides.** With-context side ANY; counter-context side INITIATION. Jeron: Part 4, 00:10:28–00:10:52 ("if the framework is already telling me shorts, I don't need much confirmation… Buyers would have to be the ones to prove"); Part 5, 00:15:26–00:15:41.  
* **2\. Zone tested 4+ times (changed).** Lower highs or higher lows into a zone tested 4+ times: favour INITIATION through it. The response side stays open; order flow decides. Jeron: Part 2, 00:05–00:06 (rejected five times, "it would be much more advantageous for me to see buyers reclaim this level"); Strategy In 30 Minutes, 00:10:05 and 00:11:06 ("The fourth test is now the lean"); response kept open: Part 2, 00:42–00:43. The count of 4 is ours (needed).  
* **Rejection and flip zones** (AMT PO-1): the 4+ tests rule does not apply; a flip is the reason the zone exists (Part 1, 00:12:08). The context side rule applies; on a Balanced or None day both sides are ANY ("we don't have biases", Part 1, 00:36:00–00:36:20).  
* **Accepted value edge** (AMT PO-9): at a weekly or PD VAL that price has ACCEPTED\_BELOW, short side ANY and long side INITIATION (buyers must reclaim, as on Monday Nov 17). ACCEPTED\_ABOVE at a VAH is the mirror. Jeron: Part 1, 00:34:58–00:35:10, 00:15:29, 00:19:08.  
* **Double distribution edge** (AMT PO-11): the side moving into the far distribution is INITIATION only; the side responding off it is ANY. Jeron: Part 1, 01:22:02, 01:24:45–01:24:51, 01:24:59, 01:25:30.

### **New, from Jeron**

* **4\. Gamma regime (calculated).** POS: responses at the edges are favoured; an INITIATION side needs acceptance plus a retest. NEG: INITIATION sides open; do not fade a breakout. Logged first; part of the separate gamma regime test. Jeron: Part 6, 00:06:09–00:06:49 ("until there is acceptance… I am looking to play the range… once you get this acceptance, retest, buying out of it, cool"); Part 5, 00:13:25–00:14:03; Strategy In 30 Minutes, 00:10:19–00:10:24 ("don't you dare fade the breakout", from his game plan).  
* **5\. First touch.** first\_touch=YES on each decision zone's first test in regular trading hours; the test number is logged on every candidate. Jeron favours the first-touch fade and expects a break by the 4th test. Logged only. Jeron: Gamma Levels Explained, 00:07:53–00:07:59 ("first touch there is fade favored"); Strategy In 30 Minutes, 00:10:05–00:10:22; Part 6, 00:03:44–00:03:54.  
* **6\. Context side effects (from Phase 2).** edge\_control=SELLERS at an edge: the long side through it is INITIATION, the short side off it stays open; BUYERS is the mirror. value\_follows=DIVERGENT\_UP: the long side through the highs is INITIATION; DIVERGENT\_DOWN is the mirror. Jeron: Part 4, 00:00:57–00:01:31, 00:03:05–00:04:19.

### **When rules disagree on one side (ours, needed)**

* The most restrictive rule wins: NONE, then INITIATION, then RESPONSE, then ANY. Every conflict is logged as side\_conflict=\<zone\>\|\<side\>\|\<each rule and its answer\>, so the log shows whether a ranking is ever worth adding. Needed: the strategy needs one answer per side, and Jeron ranks no rules; this matches his "who has to prove what, where" (the side that has not proven itself must prove it). Gamma regime (rule 4\) and first touch (rule 5\) are logged tags until their tests are run.

### **Unchanged**

* alt\_long / alt\_short after invalidation stay ANY (Book 1 default). No entry change: the strategy still waits for order-flow proof at the zone (Part 1, 00:01, 00:40:50–00:47:00).

## **Jeron check**

| Item | Source | Verdict |
| :---- | :---- | :---- |
| Decision zone \= 2+ source families | Part 6, 00:03:29–00:03:44; Part 4, 00:04:58–00:05:27; Gamma Levels Explained, 00:03:31–00:04:15 | Jeron (minimum of 2 ours) |
| Calculated gamma levels count as a source | Part 4, 00:04:58–00:05:13; Part 6, 00:04:19–00:04:40 | Jeron (gamma ranks, 1-day min / max, blind levels needed) |
| Balanced: edges only, POC as target | Part 6, 00:02:23–00:02:52; Strategy In 30, 00:10:16, 00:11:41 | Jeron |
| 2 zones per side; merge touching zones (1-ADR filter and 60-point cut now research) | No Jeron number | Ours (needed) |
| Counter-context \= INITIATION | Part 4, 00:10:28–00:10:52; Part 5, 00:15:26–00:15:41 | Jeron |
| 4+ tests → favour INITIATION through | Part 2, 00:05–00:06; Strategy In 30, 00:11:06 | Jeron (count ours) |
| Response stays open at a 4+ tested zone | Part 2, 00:42–00:43; Part 3, \~00:04, \~00:14–00:16 | Jeron |
| Rejection / flip zones open | Part 1, 00:12:08 | Jeron |
| Accepted edge sides | Part 1, 00:34:58–00:35:10, 00:15:29 | Jeron |
| Double distribution edge needs initiation | Part 1, 01:22:02–01:25:30 | Jeron |
| Gamma regime side rule | Part 6, 00:06:09–00:06:49; Part 5, 00:13:25–00:14:03 | Jeron (own test) |
| First touch | Gamma Levels Explained, 00:07:53–00:07:59; Strategy In 30, 00:10:05–00:10:22 | Jeron (logged) |
| Edge control / value follows price sides | Part 4, 00:00:57–00:01:31, 00:03:05–00:04:19 | Jeron (side mapping ours) |
| Most restrictive rule wins; conflicts logged | Jeron gives no order | Ours (needed) |
| Crossed both ways → NONE; lava band; NONE off 4+ tests; MenthorQ no-move rule | Contradict Jeron or no value in Book 1 | Removed |

## **Needed (Jeron gives the idea, no specifics)**

* Minimum number of source families for a decision zone (zone rule 1; ours is 2).  
* Gamma ranks from the calculated GEX levels (can be built now); 1-day min / max and blind levels (formula to define and check against the MenthorQ month).  
* Test count for "favour initiation" (side rule 2; ours is 4).  
* Whether the 1-ADR filter or the 60-point width cut is worth bringing back (both logged as research), once the Phase 5 stop is set.

## **Still to review in this phase**

* Done: the counter-context target (VWAP, POC or value edge only) is in "Book 1A – 6 Targets and exit: E-Footprint\_Imbalances".  
* Confirm the map can write families=, levels=, first\_touch and the calculated gamma levels on each zone before the open.

## **Test**

* Part of the Book 1A location arm (see AMT, How it is tested). Logged on its own: the sides and days that change because of each removal and each new rule, candidate outcomes by source count, at accepted edges, double distribution edges and the balance POC, and first touch vs later tests.  
* The gamma regime side rule (rule 4\) is pre-registered with the Context gamma regime test before it changes any side.
