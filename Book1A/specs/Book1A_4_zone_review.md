<!-- exported 2026-11-01T20:32Z from Google Doc 1bfoKjYZrx6NsVCUxv82kObYBvNR4-prt3bebMCQiy1A, modifiedTime 2026-11-01T17:18:44.554Z -->
# **Book 1A – 4 Zone review (go / no-go)**

**Status:** draft v2, updated Oct 31, 2026\. Changes 1–6 from the review of Parts 1–6, the webinar, Strategy In 30 Minutes and the late-July recaps were approved by Kyron on Oct 31\. Nov 1, 2026: C3 (pre-trade dollar risk check and dollar daily limit) approved by Kyron. Applies to Book 1A only.  
**Phase order:** 1 AMT (the map) → 2 Context → 3 Zone selection and side rules → **4 Zone review (go / no-go)** → 5 Entry → 6 Targets and exit.

## **What Book 1 did**

Checks A–F from prompt v1.5 decided review=APPROVED or LOG\_ONLY, closed sides, and set max\_trades and no\_trade windows. A: data. B: a decision zone each side within 1 ADR, targets above and below. C: risk fit (stop ≈ zone width \+ 2 ticks, at least 1.5 R to the nearest target, stop no wider than about a third of the daily loss limit, else the side closed). D: test history. E: context fit. F: day suitability (data releases, FOMC, earnings, wide overnight range, half day, holiday, roll day). The strategy also had 3 trades a day and a 2-loss halt.

## **What Jeron does**

* **No pre-open check list.** His go / no-go is alignment: "if I don't have that \[structure, profiling, positioning, then order flow\], I don't want to take it" (Strategy In 30 Minutes, 00:28:47–00:29:06); "you're going to avoid the ones that don't have this alignment" (Gamma Levels Explained, 00:15:11–00:15:19); "I am not going to trade until this happens… wait for a level to get hit" (Webinar, 13:04). In Book 1A this is enforced by Phase 3 (2+ sources) and zone-only entries.  
* **Stop at the invalidation point, size to the stop.** "I put my stop where my trade is invalidated. So if I have to have a 50-point stop… I need to make sure that I'm sized lighter. I don't think having a static stop… makes sense" (Webinar, 2:08).  
* **Reward against the whole trade idea.** "That's a relatively wide stop. Well, if our final target is the value area high of the weekly profile, this is a 5:1" (Part 1, 01:10); TP1 about 2:1, TP2 about 3R, "2.5 3R trades are what I live for" (Part 1, 00:20). His stats average about 2R (Part 3, 00:01–00:02).  
* **Reward depends on the entry stop.** The same idea gives 2R or 4R depending on the entry and stop (Part 2, 01:28–01:29); a range-chart stop "gives you a higher risk-to-reward" (Part 2, 00:29–00:30, 00:52).  
* **Done after a strong win; no revenge trades in chop.** "I hit a 4R within 15 minutes and I'm done for the day" (Part 6, 00:05:27–00:05:30); "This is chop… We're not revenge trading. We just made a lot of money" (Part 1, 00:54–00:55); "one and done" (Gamma Levels Explained, 00:01:39, chat).

## **Book 1A rules**

### **Check A, data: kept (ours, needed)**

* Packet date and as-of time, no data gap in the last 24 hours, PD / ON / weekly profiles present. Half day, holiday and roll day → LOG\_ONLY (roll days carry unadjusted history). Needed for data quality.

### **Check B, zone coverage: research**

* "A decision zone on each side within 1 ADR, else LOG\_ONLY" made Nov 7, Nov 14 and Dec 4, 2025 LOG\_ONLY. Ours. The plan logs the check; it does not set LOG\_ONLY.

### **Check C, stop and size (changed)**

* **Rule:** the stop goes at the invalidation point of the trade idea, and size is set so every trade risks the same fixed amount. A side closes only if even 1 micro cannot fit that risk. Jeron: Webinar, 2:08.  
* **Removed:** "close the side if the stop is wider than about a third of the daily loss limit". Ours, and it contradicts Jeron, who sizes down instead.  
* **Needed:** the fixed risk per trade (ours). Theoretical R does not depend on size, but realized net R can (commissions, whole contracts, partial exits), so the replay reports both; sizing keeps a single loss at the same dollar amount ([Book 1 result redacted]).  
* Pre-trade risk check (C3; risk control, ours): before every order the engine computes estimated risk \= stop distance in ticks × tick value × contracts \+ commissions \+ a slippage allowance (NQ \$5.00 per tick per contract, MNQ \$0.50). The order is accepted only if estimated risk ≤ the smaller of the per-trade risk budget and the remaining daily budget. Remaining daily budget \= daily dollar loss limit − realized losses today − risk reserved by any open position. Size \= the largest contract count that passes; if even 1 MNQ fails, the trade is rejected and logged as RISK\_REJECT. The daily loss limit is in dollars, not ticks.  
* Planned vs actual: the check uses planned risk. A loss larger than planned because a stop slipped is reported separately as RISK\_BREACH\_FILL, never hidden.  
* Frozen Nov 1, 2026 (Book 1A replay plan, U3): simulated balance \$100,000; 1% \= \$1,000 per trade; daily loss limit \$2,000; NQ only, minimum 1 NQ, wider stops rejected; commission \$5.74 round trip per NQ. Confirmed: slippage allowance of 2 ticks per contract on the stop in the risk estimate only. NQ formula: estimated risk \= (stop ticks \+ 2\) × \$5 × N \+ \$5.74 × N; the chosen N is logged before each order.

### **Check C, reward before the open (changed)**

* **Rule:** the plan logs R at TP1, TP2 and the runner of the Phase 6 ladder, using the zone stop (zone width \+ 2 ticks). No side is closed on it.  
* **Removed:** "at least 1.5 R to TP1, or 2 R to TP2, else close the side". Ours: Jeron judges reward with the entry stop and counts the runner (Part 1, 01:10).  
* **Moved to Phase 5:** R is checked at entry with the actual entry stop (see Book 1A – 5 Entry, shared rules).

### **Check D, test history: moved to Phase 3**

* It sets sides, so it lives with the side rules.

### **Check E, context fit: kept (ours)**

* Side rules agree with the context (Phase 2\) and the invalidation sits beyond the zone it protects. It only checks the plan is consistent.

### **Check F, day suitability: research**

* no\_trade windows around data releases and FOMC, and max\_trades=1 after mega-cap earnings or a wide overnight range, came from Fabio (MenthorQ host) and from us, not Jeron. The plan logs what it would have set; the strategy does not apply it. Half day, holiday and roll day stay under check A.

### **Daily limits**

* **Kept (ours, needed):** 3 trades a day and the 2-loss halt, for account risk. The daily dollar loss limit (C3) applies on top of both.  
* **New, logged variant (Jeron):** stop for the day after the first winner of 2R or more. Logged as "what if", not traded, until tested. Jeron: Part 6, 00:05:27–00:05:30; Part 1, 00:54–00:55. The 2R threshold is ours (needed).

### **The go / no-go decision**

* review=APPROVED only if check A passes and check E is fixed in the plan; otherwise LOG\_ONLY. The LOG\_ONLY mechanism is ours. Check C no longer makes a day LOG\_ONLY; it only closes a side when 1 micro cannot fit the risk.  
* No extra day filter for alignment: Phase 3 (2+ sources) and zone-only entries already cover it.

## **Jeron check**

| Item | Source | Verdict |
| :---- | :---- | :---- |
| Check A: data, half day, holiday, roll day | Data quality | Ours (needed) |
| Check B: zone coverage | None | Research |
| Stop at invalidation; size to the stop | Webinar, 2:08 | Jeron |
| Fixed risk per trade; close only if 1 micro cannot fit | Jeron gives no amount | Ours (needed) |
| Stop cap closes the side | Contradicts Webinar, 2:08 | Removed |
| R logged at TP1, TP2 and runner before the open | Part 1, 00:20, 01:10 | Jeron |
| 1.5 R / 2 R minimum closes the side before the open | Jeron judges R at entry | Removed (R check moves to Phase 5\) |
| Check E: context fit | Consistency check | Ours |
| Check F: news, FOMC, earnings limits | Fabio / ours | Research |
| 3 trades a day; 2-loss halt | Account risk | Ours (needed) |
| Done after a strong win (2R+) | Part 6, 00:05:27; Part 1, 00:54–00:55 | Jeron (logged variant; threshold ours) |
| No alignment, no trade | Strategy In 30, 00:28:47; Gamma Levels Explained, 00:15:11 | Jeron (covered by Phase 3\) |
| APPROVED / LOG\_ONLY | Part 2, 01:09:44–01:10:07 (no trade when unclear) | Ours, close to Jeron |

## **Needed (Jeron gives the idea, no specifics)**

* The fixed risk per trade, and the micro / mini contract sizes it allows; the daily dollar loss limit, commission per contract and slippage allowance (C3).  
* The R minimums used at entry (Phase 5), for TP1, TP2 or the runner.  
* The winner size that ends the day in the "done after a strong win" variant (ours is 2R).

## **Test**

* Part of the Book 1A location arm (see AMT, How it is tested). Logged on its own: sides that check C used to close and now stay open, and their outcomes; R at TP1, TP2 and the runner from the zone stop vs the entry stop; the research checks (B, F) with what they would have done; the share of days APPROVED; and the "done after a strong win" variant vs the 3-trade limit.
