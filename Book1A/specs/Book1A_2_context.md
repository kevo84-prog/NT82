<!-- exported 2026-11-01T20:17Z from Google Doc 1FhnNBFcc58teeZ76Sbi7kjz0b2OhX0Nd1Rmyh-AepfY, modifiedTime 2026-11-01T17:59:42.973Z -->
# **Book 1A – 2 Context (bullish or bearish)**

**Status:** draft v2, updated Oct 31, 2026\. The context line and invalidation were approved by Kyron on Oct 31\. Changes 1–7 from the context review of Parts 1–6 and the other Jeron videos were approved the same day. Nov 1, 2026: C6 (market\_context and draw\_status written as separate fields) and C5 (no runner only on Balanced days with positive gamma) approved by Kyron. Applies to Book 1A only.  
**Phase order:** 1 AMT (the map) → **2 Context** → 3 Zone selection and side rules → 4 Zone review (go / no-go) → 5 Entry → 6 Targets and exit.

## **What Book 1 did**

* **Rules-only formula.** Bullish: value migrated higher vs the day before (PD vs PD2), price above or inside prior-day value, and the 1-hour trend not down. Bearish: the mirror. Balanced: the PD2 \+ PD \+ ON balance composite overlapping. None: anything else.  
* **Claude plan questions (prompt v1.5).** Weekly and 1-hour trend, value migration, location vs PD / ON / weekly value, overnight inventory, who has been rewarded, delta profile, ES vs settlement, a macro note (VIX, 10-year, oil, news) and "the 10-year can override in the afternoon".  
* **Invalidation.** 2 ticks beyond the outermost decision zone; the new context is Balanced.

## **Removed from Book 1A (not kept as research)**

* **The Book 1 context formula.** Our own algorithm, not Jeron's. Phase 2 (Nov 5 – Dec 4, 2025): days it labelled Bullish, Bearish or Balanced lost −7.6 R on 19 trades; days it left as None made \+1.1 R on 16 trades. Small sample, no sign it helps.  
* **The 1-hour "trend not down" filter.** Jeron reads hourly structure (input 7 below) but never uses a trend filter.  
* **The Book 1 invalidation** (2 ticks beyond the outermost zone → Balanced). It depends on the removed formula.  
* **"Macro note (or calendar) missing and context None → LOG\_ONLY".** Ours; no evidence it helps.

## **Moved to research (logged only)**

* **ES compared with settlement.** Ours. Jeron uses an ES level that must hold, not settlement (input 8).  
* **Event no-trade windows and earnings limits.** Fabio (MenthorQ host), not Jeron. Already research under Phase 4 check F.

## **Context rule (draft)**

**Jeron:** he sets context before the open from where price sits against higher-time-frame value and where the market is drawn to, then lets the open confirm it.

* Part 2: "higher time frame bounce… pushed back up into the value area" (00:04:00–00:05:04); "So context, I'm bullish. Clearly higher time frame" (00:06:45); "the overall higher time frame context is bullish. We bounced off… the higher time frame value area low" (00:10:08); "the draw and the auction is clearly bullish" (00:36:35).  
* Part 3: two-month composite and weekly profile, "which side do we see rewarded" (\~00:09–00:10); "That's the two scenarios" (\~00:10–00:11).  
* Part 4: "Our context is sellers are in control, and then the location is we're at the weekly and session value area high" (00:04:13–00:04:19).  
* Part 1: acceptance at the weekly value edge (00:34:58–00:35:10), and no fixed bias: the open decides (00:12:22–00:13:20, 00:36:23–00:36:38, 01:07:01–01:07:26).

**Rule:**

* **Bullish:** price is inside or above the higher-time-frame composite value after holding or reclaiming its VAL, and is not ACCEPTED\_BELOW the weekly VAL (acceptance state from AMT PO-9).  
* **Bearish:** the mirror (inside or below composite value after failing at or losing its VAH, and not ACCEPTED\_ABOVE the weekly VAH).  
* **Balanced (changed):** the PD2, PD and ON value areas, or the days of the current week, overlap and are merged into one range, written as balance= and balance\_poc=. Trade its extremes, not the POC. This replaces our earlier "inside composite and weekly value with no recent edge test". Jeron: Part 4, 00:01:51–00:02:23; Part 6, 00:01:40–00:02:50; Part 5, 00:05:11.  
* **None:** the higher-time-frame read and the weekly acceptance disagree (for example composite bullish but ACCEPTED\_BELOW the weekly VAL). Our mapping (needed).  
* **draw=\<lo\>-\<hi\>:** the next higher-time-frame level in the context direction: composite POC, HVN, the far value edge, or a gamma magnet (input 6). It is the runner target in Phase 6\. The plan writes market\_context=BULLISH \| BEARISH \| BALANCED \| NONE and, separately, draw\_status=ACTIVE \| REACHED \| INVALIDATED (C6). Reaching the draw changes draw\_status, not market\_context.  
* Context only sets sides and targets. The strategy still needs order-flow proof at the open.

## **Context inputs added (approved Oct 31\)**

Each input is written as a plan key. The strategy logs keys it does not use, so S1.4 runs unchanged until a rule is tested.

### **1\. Value follows price**

* **Rule:** compare the prior day with the day before. A new high with a lower VAH and POC \= value\_follows=DIVERGENT\_UP ("buyers are not accepting up at this price"); a new low with a higher VAL and POC \= DIVERGENT\_DOWN; otherwise WITH\_PRICE.  
* **Use:** DIVERGENT\_UP counts as failed acceptance at the highs. The plan cannot call the day Bullish from location alone, and the long side through that edge is INITIATION. DIVERGENT\_DOWN is the mirror. The mapping to sides is ours.  
* **Jeron:** Part 4, 00:00:57–00:01:31. Map input: value\_vs\_price.

### **2\. Overnight inventory**

* **Rule:** on\_inventory=NET\_LONG \| NET\_SHORT \| NEUTRAL, on\_vs\_settle=\<points\>, on\_profile=THIN \| NORMAL.  
* **Use:** a net-long overnight far above settlement on a thin profile is expected to rebalance fast toward settlement, unless buyers accept above it; if they accept, upside targets open. Written as the two scenarios for the open. Net short is the mirror.  
* **Jeron:** Part 3, \~00:01–00:07 ("The overnight inventory is net long… the rebalancing is going to happen fast. That gives us an advantage on shorts. It also gives us an advantage on longs…").  
* **Needed:** how far from settlement counts as "far", and what counts as a "thin" profile. Jeron gives no numbers.

### **3\. Balanced \= Jeron's merged range**

* See the Balanced line above. The balance= and balance\_poc= lines come from the map's PD2 \+ PD \+ ON composite (the Book 1 composite matched Jeron).

### **4\. Who controls the edge (delta profile)**

* **Rule:** for each value edge, edge\_control=SELLERS \| BUYERS \| MIXED from the delta profile bands (AMT PO-7, same dominance threshold).  
* **Use:** an edge controlled by sellers needs buyers to prove it: the long side through it is INITIATION; the short side off it stays open after failed buying (Phase 3). Mirror for buyers.  
* **Jeron:** Part 4, 00:03:05–00:04:19 ("the context of this area is sellers are in control"); Part 3, \~00:08 (sellers on the lower end of the weekly delta profile).

### **5\. Gamma regime**

* **Rule:** gex\_regime=POS \| NEG from the calculated GEX levels (sign of total net GEX; Databento data, MenthorQ method). MenthorQ itself is not used in Book 1A.  
* **Use:** POS \= range day: favour responses at the balance extremes, do not expect breakouts, no runners on Balanced days (Phase 6, C5). NEG \= momentum: initiation and runners allowed. Logged first; it gets its own pre-registered test because it changes side rules and exits.  
* **Jeron:** Part 5, 00:01:25–00:01:40, 00:13:14–00:14:03 ("I'm not going to try to hold runners"); Part 6, 00:00:19–00:01:20, 00:05:05–00:05:13 ("In a mean reverting environment, in a balanced condition, trade value areas and align it with gamma levels").

### **6\. Gamma magnets as draw candidates**

* **Rule:** the nearest calculated gamma levels in the context direction (call resistance, put support, high volatility level, 0DTE levels, gamma ranks) are added to the draw= candidates. They also count as a confluence source for decision zones (Phase 3, zone rule 2); the prompt v1.5 rule "do not move a zone because of a MenthorQ level" is dropped in Book 1A. Needed: gamma ranks (can be built now), 1-day min / max and blind levels (no calculation yet).  
* GEX tags added Nov 1, 2026 (logged only; Jeron items found through the Oct 29 GEX doc): hvl\_side \= ABOVE \| BELOW \| INSIDE the HVL band (dips are bought above put support and HVL, Gamma Levels Explained, 00:06:15–00:06:26); cr\_ps\_width \= points from put support to call resistance, a narrow range read as compressed (Part 6, 00:00:14–00:01:20; 80 points on Apr 9, 2026); pin\_zone \= YES when the HVL sits within 10 points of 0DTE put support (10 points ours), reported for the afternoon (Part 5, 00:10:07–00:11:14; Gamma Levels Explained, 00:05:42–00:05:52); pc\_gamma\_ratio \= the put/call gamma ratio, value only, no rule (Part 5, 00:01:48–00:03:03).  
* Blocked until gamma 1 (U6) and the one-day min (U7) exist: failure to accelerate and last level before air on negative-gamma days (Webinar, 24:29–29:50), and acceptance through VWAP at the one-day min (Part 5, 00:06:05–00:06:40).  
* **Jeron:** Part 5, 00:03:08–00:04:44 ("all the significant levels are above us… now I can see the magnets that price could be attracted to").

### **7\. Hourly structure read**

* **Rule:** htf\_structure=RAISING\_DEMAND \| LOWERING\_SUPPLY \| BALANCE from the 1-hour swings: demand zones stepping higher and supply run through, supply stepping lower, or consolidation-and-push inside a range. Used with the composite location; it is not a trend filter.  
* **Jeron:** Part 3, \~00:03–00:05 (hour time frame: "consolidation with a push up… This is a strong area of demand"); \~00:20–00:22 ("I'm going to look for longs on gold every time until I see sellers rewarded on the higher time frame").  
* **Needed:** the swing definition (map h1\_swings is ours).

### **8\. ES, 10-year, VIX and news (corrected Oct 31\)**

* **ES level:** es\_long\_above= / es\_short\_below=, the ES level that must hold for longs or break for shorts. Logged, then tested. Jeron: Trading NQ – Trade Recap, 00:03:17, 00:04:24 ("While ES holds 7397… Everything's aligned"); Strategy In 30 Minutes, 00:08:01, 00:08:48, 00:10:42–00:11:04 ("ES rejecting its gate first"). **Needed:** how the ES level is chosen.  
* **10-year and VIX alignment:** tnx= and vix= with a note on whether each supports the context. Logged. Jeron: Trade Recap, 00:01:27, 00:03:02 ("The 10-year can hold at or below 4.65 while the VIX stays sub 19"), 00:06:37; Gamma Levels Explained, 00:11:41–00:12:11, 00:13:20, 00:14:42. **Needed:** the thresholds. Jeron's change daily and come from his AI game plan.  
* **10-year afternoon override:** tnx\_override=\<level\>. Logged first. Jeron reads it from his Claude game plan and endorses it: "The 10-year through 4.7 still overrides everything in the afternoon" (Gamma Levels Explained, 00:06:26, 00:11:41). **Needed:** how the override level is set.  
* **News:** news= and a note on how the market reacted about 30 minutes before the open. Logged (judgment call). Jeron: Trade Recap, 00:01:22, 00:02:03.  
* **Data:** ES is in the Databento data. The 10-year yield and VIX at 08:25 CT for the Nov–Dec 2025 test days need a historical source; ZN or VIX futures would only be a proxy. Until then these are logged on live days and not backtested.  
* These items appear only in Jeron's late-July recaps, not in Parts 1–6, the webinar or 60k Profit.

## **Invalidation (draft, approved Oct 31\)**

**Jeron:** context holds "at least until it gets to this zone… until sellers show us they're in control" (Part 2, 01:00:59–01:01:18); it flips when a reclaim fails: "as long as we don't reclaim this level, sellers are in control" (00:46:57), "we are leaning bearish… we are bearish" (00:48:15); a reclaim back into value works the other way (Part 1, 00:15:29, 00:19:08); "look for longs… until I see sellers rewarded on the higher time frame" (Part 3, \~00:21–00:22). Stops sit at "the invalidation point of your trade idea" (Part 1, 00:20:13; Part 2, 01:27:35).

* **Trigger 1:** acceptance across the key edge against the context, 3 closes beyond it (the strategy's acceptance rule). A Bullish context invalidates below the weekly or composite VAL it depends on, a Bearish one above the VAH. draw\_status becomes INVALIDATED and market\_context becomes Balanced (ours, needed); the plan writes invalidate\_below= / invalidate\_above= at that edge.  
* **Trigger 2:** the draw is reached. Once price trades into the draw= zone, draw\_status becomes REACHED and market\_context is unchanged (C6). Jeron says only "bullish at least until it gets to this zone", not what comes after. Logged only, not enforced: a new valid target is required before another entry in the same direction (tag NEW\_TARGET\_NEEDED).  
* The order-flow part ("sellers show us they're in control") is read during the session by the strategy, not by the pre-open plan.

## **Inputs this phase needs from Phase 1 (AMT)**

* Higher-time-frame composite value area and POC (map htf\_composite, 60 days ≈ Jeron's 2–3 month composite).  
* Developing weekly value area and the PO-9 acceptance state of each value edge.  
* PD2 \+ PD \+ ON balance composite (balance=, balance\_poc=) and value\_vs\_price.  
* Delta profile bands (PO-7), overnight profile and settlement, and 1-hour swings.  
* Calculated GEX levels (regime, call resistance, put support, high volatility level, 0DTE levels, gamma ranks), ES levels; 10-year and VIX for live days.  
* Draw candidates: composite POC, HVN areas (PO-6), the far value edge and gamma magnets.

## **Jeron check**

| Item | Source | Verdict |
| :---- | :---- | :---- |
| Context from higher-time-frame value and the draw | Part 2, 00:04:00–00:10:08, 00:36:35; Part 3, \~00:09–00:10 | Jeron |
| Weekly acceptance as part of context | Part 1, 00:34:58–00:35:10; Part 4, 00:04:13 | Jeron |
| No fixed bias; two scenarios; the open confirms | Part 1, 00:36:23–00:36:38; Part 3, \~00:10–00:11 | Jeron |
| Balanced \= merged overlapping value areas | Part 4, 00:01:51–00:02:23; Part 6, 00:01:40–00:02:50 | Jeron |
| Value follows price | Part 4, 00:00:57–00:01:31 | Jeron (side mapping ours) |
| Overnight inventory and rebalance speed | Part 3, \~00:05–00:07 | Jeron ("far", "thin" needed) |
| Delta control of the edge | Part 4, 00:03:05–00:04:19 | Jeron |
| Gamma regime | Part 5, 00:13:14–00:14:03; Part 6, 00:00:19–00:01:20 | Jeron (own test) |
| Gamma magnets as draw | Part 5, 00:03:08–00:04:44 | Jeron |
| Hourly structure read | Part 3, \~00:03–00:05, \~00:20–00:22 | Jeron (swing definition ours) |
| ES level must hold / break | Trade Recap, 00:03:17, 00:04:24; Strategy In 30, 00:10:42 | Jeron (level choice needed) |
| 10-year and VIX alignment; afternoon override | Trade Recap, 00:03:02; Gamma Levels Explained, 00:06:26, 00:11:41 | Jeron (thresholds needed) |
| Exact mapping to Bullish / Bearish / Balanced / None | Jeron describes the read, not a formula | Ours (needed: S1.4 reads context=) |
| Invalidation on failed or completed reclaim | Part 2, 00:46:57, 00:48:15; Part 1, 00:15:29 | Jeron |
| Draw reached: draw\_status=REACHED, context unchanged | Part 2, 01:00:59–01:01:18 | Jeron |
| 3 closes as "acceptance" | Strategy setting | Ours (needed) |
| ES vs settlement; event windows | Not Jeron (ours / Fabio) | Research |
| Book 1 formula, 1-hour trend filter, 2-tick invalidation, macro-missing LOG\_ONLY | Ours; no value in Book 1 | Removed |

## **Needed (Jeron gives the idea, no specifics)**

* "Far" from settlement and a "thin" overnight profile (input 2).  
* The 1-hour swing definition (input 7).  
* How the ES level is chosen (input 8).  
* 10-year and VIX thresholds and the afternoon override level (input 8).  
* A historical source for the 10-year yield and VIX on the backtest days (input 8). Gamma ranks, 1-day min / max and blind levels from the calculated GEX data (inputs 5 and 6; gamma ranks can be built now).

## **Still to review in this phase**

* Confirm the map can produce draw=, balance=, value\_vs\_price, edge\_control and htf\_structure before the open.

## **Test**

* Part of the Book 1A location arm (see AMT, How it is tested). Logged on its own: the context and draw each day, invalidation events, trades by with-context vs counter-context, and each new key (inputs 1–8) with the outcome of the trades it would have changed.  
* Gamma regime (input 5\) and ES / 10-year / VIX (input 8\) are pre-registered as separate tests before they change any side rule or exit.
