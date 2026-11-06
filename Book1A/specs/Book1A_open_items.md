<!-- exported 2026-11-01T21:18Z from Google Doc 1Fi8Bo0plsY_I7kn_-w9i9l6NVXtP-7t6jgR966nh-v0, modifiedTime 2026-11-01T17:18:48.045Z -->
# **Book 1A – Needed and open items**

**Status:** compiled Oct 31, 2026 from the nine Book 1A phase docs (1 AMT, 2 Context, 3 Zone selection, 4 Zone review, 5 Entry overview, 5 Entry E-Footprint\_Imbalances, 5 Entry E-Deep Effort Range, 6 Targets and exit for each arm). "Needed" \= Jeron gives the idea but no number, so our value is kept and frozen before any Book 1A result is read. "Open" \= a decision, a check or a build that must happen before pre-registration. Updated Nov 1, 2026: C1–C7 approved; new items N1–N8 below; "Book 1A – Replay plan (controlling research doc)" now governs how everything is tested.

## **1\. Open decisions (need Kyron)**

| \# | Item | Phase | Options | Jeron source |
| :---- | :---- | :---- | :---- | :---- |
| O1 | All-time-high to swing-low profile with business zones | 1 AMT | Decided Nov 1 (E6): (b) research only for the replay | Part 2, 00:36:43–00:39:00, 00:52:24 |
| O2 | Deep effort sizing variant: risk 20% of the day's profit | 4 Zone review | Add as a logged variant, or leave out | Part 2, 00:54 |
| O3 | Bring back the 1-ADR filter or the 60-point width cut | 3 Zone selection | Decide after the Phase 5 stop is set; both logged as research for now | No Jeron number |
| O4 | Deep effort findings D1–D9 (second trigger, day type, definition, 60 range, two stops, hold count, exit, deep trades tag, add-ons) | 5 Entry: E-Deep Effort Range | Apply once the indicator rebuild passes its check | Listed in the E-Deep Effort Range entry doc |

## **2\. Open checks and builds**

| \# | Item | Phase | What is needed |
| :---- | :---- | :---- | :---- |
| B1 | Nov 17–19, 2025 diagnostic | 1 AMT | Rerun map v2.4 and the rules-only plan and compare zones with Jeron's levels and screenshots. Pre-registration comes after it. |
| B2 | Map outputs for context | 2 Context | Confirm the map can write draw=, balance=, balance\_poc=, value\_vs\_price, edge\_control and htf\_structure before the open. |
| B3 | Map outputs for zones | 3 Zone selection | Confirm the map can write sources=, first\_touch and the calculated gamma levels on each zone. |
| B4 | Gamma ranks (gamma 1, gamma 2…) | 2, 3, 6 | Rank strikes by net GEX from the calculated data. Can be built now. |
| B5 | 1-day min / max and blind levels | 2, 3, 6 | No published method. Define a formula and check it against the MenthorQ month (quin.txt). |
| B6 | Historical 10-year yield and VIX at 08:25 CT | 2 Context | A source for the backtest days. Until then logged on live days only (ZN or VIX futures would only be a proxy). |
| B7 | Deep effort indicator rebuild | 5 and 6, E-Deep Effort Range | Rebuild from MBO using Jeron's screenshots, then check zones by eye. Both deep effort docs stay PAUSED until then. |
| B8 | AMT doc phase list | 1 AMT | Done Nov 1, 2026: phase list now points to the per-arm Phase 5 and Phase 6 docs. |
| B9 | Pre-registration | All | Now the Book 1A replay plan (created Nov 1). Remaining: freeze every unresolved setting listed there (U1–U10) and tag the code before the first run. |

Closed: the counter-context target (now in the E-Footprint\_Imbalances Phase 6 doc); B8 (Nov 1).

Added Nov 1, 2026 (from C1–C7):

N1. VWAP definition frozen in AMT PO-8 (overnight session VWAP at 08:10 CT, one family); confirm the roll-day restart in Phase 0 parity.

N2. Power-trade rebuild (C4): Jeron's time interval, trade-size and delta filters are unknown; freeze a value before the replay or keep it logged only.

N3. Dollar risk values (C3): commission frozen (NQ \$5.74, MNQ \$1.88 round trip, routing to confirm). Frozen Nov 1: \$100,000 simulated balance, 1% \= \$1,000 per trade, \$2,000 daily limit, NQ only (minimum 1 NQ). Slippage allowance of 2 ticks per contract in the risk estimate confirmed. N3 closed.

N4. Exit steps (C5): M-J2 position split and target order, and the step progression rule.

N5. Map fields: families=, levels= (C1), market\_context= and draw\_status= (C6), added to checks B2 and B3.

N6 (not needed before Phase 0; due before final validation). Exposure register: confirm the trading dates of Parts 3–6, the webinar, Strategy In 30 Minutes, 60k Profit, the Trade Recap (likely Jul 30, 2026\) and whether Jul 29–30 or Nov 20–21 are analyzed. Unconfirmed dates stay unresolved and are treated as excluded.

N7 (not needed before Phase 0; due before Block 2 validation, only after a "go"). Jul–Aug check: confirm Jul 1 – Aug 31, 2026 has not shaped any Book 1A choice beyond the excluded video sessions. If it has, it becomes exploratory and final confirmation moves to later unseen data.

N8. Block 2 go / no-go: rule written in the replay plan section 9, applied after the Phase 4 replay.

## **3\. Needed: our values (Jeron gives the idea, no number)**

### **1 AMT (the map)**

| Item | Our value | Jeron idea |
| :---- | :---- | :---- |
| Swing high / low | 15 bars each side | Rejection areas, Part 1, 00:38:58 |
| Arrival aggression window | Swing bar \+ 2 bars; delta 150 | Part 1, 00:39:35–00:40:30 |
| Fast departure | 0.25 ADR within 10 bars | Part 1, 00:38:58 |
| Zone width; merge | 10–40 pts; merge within 5 pts | Jeron's zones about 25–40 pts |
| Flip | 3 closes, 2 ticks beyond; 50% overlap | Part 1, 00:12:08–00:12:16 |
| VWAP tag distance | 5 pts | Part 1, 00:37:23–00:37:30 |
| Delta band | Top 20% of absolute delta | Part 1, 00:11:18–00:12:00 |
| Rejection zones kept | 2 per side within 1 ADR | None |
| MAP4 high-volume area | 70% of peak, 40-pt cap | Part 1, 00:08:10–00:08:35 |
| Acceptance state | 60 min, 80% of closes, 20% of volume | Part 1, 00:34:58–00:35:10 |
| Double distribution edge | 40 pts | Part 1, 01:21:35–01:22:02 |
| Map build rules | Merge 15 pts, pad ±5 pts, 60-pt cap, DECISION \= 2+ families | "Full alignment", Part 1, 00:37:00 |

### **2 Context**

| Item | Our value | Jeron idea |
| :---- | :---- | :---- |
| "Far" from settlement; "thin" overnight profile | Not set | Part 3, \~00:05–00:07 |
| 1-hour swing definition | Map h1\_swings | Part 3, \~00:03–00:05 |
| How the ES level is chosen | Not set | Trade Recap, 00:03:17, 00:04:24 |
| 10-year and VIX thresholds; afternoon override level | Not set (Jeron's change daily) | Trade Recap, 00:03:02; Gamma Levels Explained, 00:06:26, 00:11:41 |
| Mapping to Bullish / Bearish / Balanced / None | Draft rule in the Context doc | Jeron describes the read, not a formula |
| Acceptance | 3 closes | Strategy setting |
| Value follows price and edge control side mapping | Draft in Context and Phase 3 | Part 4, 00:00:57–00:01:31, 00:03:05–00:04:19 |

### **3 Zone selection and side rules**

| Item | Our value | Jeron idea |
| :---- | :---- | :---- |
| Minimum source families for a decision zone (six families, C1) | 2 | His examples have 3 to 5 (Part 6, 00:03:29) |
| Tests before favouring initiation | 4 | Part 2, 00:05–00:06; Strategy In 30, 00:11:06 |
| Decision zones per side; merge touching | 2; merge | Gamma Levels Explained, 00:03:31 |
| Rule order when side rules disagree | Most restrictive wins; conflicts logged | Jeron gives no order |

### **4 Zone review (go / no-go)**

| Item | Our value | Jeron idea |
| :---- | :---- | :---- |
| Fixed risk per trade; micro / mini sizes; dollar daily loss limit, commissions, slippage (C3, N3) | Not set | Webinar, 2:08 |
| R minimums at entry (used in Phase 5\) | Example TP1 1.5 R or runner 3 R | Part 1, 00:20, 01:10 |
| "Done after a strong win" threshold | 2 R | Part 6, 00:05:27–00:05:30 |
| Daily limits | 3 trades, 2-loss halt | Account risk |
| Check A data rules | Half day, holiday, roll day \= LOG\_ONLY | Data quality |

### **5 Entry: E-Footprint\_Imbalances**

| Item | Our value | Jeron idea |
| :---- | :---- | :---- |
| Power-trade size inside 300–500 (New York) and its time window (C4, N2) | Not picked | Part 1, 01:33 |
| RH1 window and fail tolerance | 15 bars, 2 ticks | Part 1, 01:30:18 |
| T8 look-back | 3 bars | Webinar, 24:29–29:50 |
| L1 distance to a plan zone | 10 pts | Webinar, 13:04 |
| Delta gates | 150 and 10% (test against delta vs the session) | Part 3, 00:24:00–00:24:26 |
| Displacement; grades B / C; retrigger | S1.4 values; 3 bars | Part 1, 01:24:51 |
| Engine rules | 15-bar dedup, one position, 12-tick slippage check, last entry 14:30 CT | None |
| Response stop | Zone width \+ 2 ticks | Stop at invalidation, Webinar, 2:08 |

### **5 Entry: E-Deep Effort Range (paused)**

| Item | Our value | Jeron idea |
| :---- | :---- | :---- |
| Deep effort zone definition (volume, delta, how long valid, "holds" in ticks) | D3 draft: one-sided volume at power-trade size | Webinar, 52:55; Part 2, 00:03 |
| Range size; ticks or points | 60 primary, 40 / 80 logged | Part 5, 00:08:12–00:08:16 |
| Exit count: first opposing zone or 2+ | D7 draft: tighten on first, exit on run-through or 2+ | Part 2, 00:25–00:28; Part 3, 00:41:20–00:41:45 |
| Stop buffer; entry on bar close | 2 ticks; close | None |

### **6 Targets and exit**

| Item | Arm | Our value | Jeron idea |
| :---- | :---- | :---- | :---- |
| Size split across TP1, TP2 and RUN | Footprint | Not set | Part 1, 00:17:35–00:17:58 |
| Quick break-even trigger on counter-context trades | Footprint | Not set | Part 2, 01:24:17–01:26:00 |
| What counts as a new same-side zone for the trail after TP1 | Footprint | Phase 5 footprint zone rules | Part 1, 01:14–01:17 |
| Flatten time | Both | 14:55 CT | None |
| "Run-through" in bars and ticks; CVD and tape check in numbers | Deep effort | Not set | Part 2, 00:28 |
| Break-even trigger: top of zone or about 50 pts | Deep effort | Not set | Part 2, 00:22 |

## **4\. Suggested order**

> 1. Decide O1 and O2.  
> 2. Build B4 (gamma ranks) and fix B8 (AMT phase list).  
> 3. Run B1 (Nov 17–19 diagnostic) and confirm B2 and B3 in the same rerun.  
> 4. Freeze every "needed" value above and N1–N4, then start the replay (B9).  
> 5. B5, B6 and B7 can run in parallel; their items stay logged only until done.
