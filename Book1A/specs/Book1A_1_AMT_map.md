<!-- exported 2026-11-01T20:17Z from Google Doc 1KuiJY7HUi9JH25XncXaGxvUGVA01oTWdn27_JIskDLQ, modifiedTime 2026-11-01T16:49:40.203Z -->
# **Book 1A – 1 AMT (the map)**

**Status:** Phase 1 approved by Kyron, Oct 31, 2026\. This doc replaces the former "preopen" doc (same file). Items from it that belong to later phases were moved to their own docs (links below) and are drafts there, to be reviewed in order. Not yet pre-registered: that happens after the Nov 17–19 diagnostic and before any Book 1A result is read. Book 1 (design v3.9, Phase 3 change list of Oct 26\) is unchanged. Nov 1, 2026: C2 (VWAP is one source family, VWAP definition in PO-8) and the source-family rule (Phase 3, C1) approved by Kyron; see the change log in the Book 1A replay plan.  
**Source:** Jeron, "part 1 Past 90 Days Using This Strategy.txt" (week of Nov 17–21, 2025), the Part 1 screenshots in Extract\_screenshots/Part 1, and "Part 2 Stop taking bad entries.txt" (week of Nov 24–26, 2025\) for the Jeron check. Every number marked *(ours)* is our own setting, not Jeron's, and is frozen before any Book 1A result is read.

## **Phase order**

* 1 AMT (the map): this doc. At 08:10 CT the map builds the auction picture from earlier data only.  
* [2 Context](https://docs.google.com/document/d/1FhnNBFcc58teeZ76Sbi7kjz0b2OhX0Nd1Rmyh-AepfY/edit)  
* [3 Zone selection and side rules](https://docs.google.com/document/d/1v85SXOa5VMMwn1wIfXsqkMZExPOQQwY9WRwzpN44CcY/edit)  
* [4 Zone review (go / no-go)](https://docs.google.com/document/d/1bfoKjYZrx6NsVCUxv82kObYBvNR4-prt3bebMCQiy1A/edit)  
* 5 Entry: "Book 1A – 5 Entry (overview and shared rules)", with one doc per arm in the E-Footprint\_Imbalances and E-Deep Effort Range folders (deep effort paused). Phase 6 is also one doc per arm: "Book 1A – 6 Targets and exit: E-Footprint\_Imbalances" (link below) and "Book 1A – 6 Targets and exit: E-Deep Effort Range" (paused).  
* [6 Targets and exit](https://docs.google.com/document/d/10FjFGf59x6L5VKCpwenRTNX6Dy2YAov4OsCNVi_tIfw/edit)

## **What changes in the map**

Moved out of this doc: PO-4 (side rules) → 3 Zone selection and side rules; PO-5 and the check C part of PO-10 (risk fit) → 4 Zone review; the ladder part of PO-10 → 6 Targets and exit; PO-12 → split by phase (context and invalidation → 2 Context; crossed-both-ways and lava → 3; checks A, B, C, F → 4; map items → below). The side-rule parts of PO-9 and PO-11 → 3; the context use of PO-9 → 2\.

| ID | Map change | Jeron source | Jeron check |
| :---- | :---- | :---- | :---- |
| PO-1 | Rejection and flip zones from the overnight, prior day and week, with VWAP and delta-band tags | Part 1: 00:12:08, 00:17:32, 00:38:58, 00:42:23. Part 2: business zone rejected five times (00:05:46); resistance became support (00:33:21) | Jeron. Numbers (15 bars, 10 bars, 0.25 ADR, 10–40 pts) ours |
| PO-2 | Packet field rejection\_zones\[\] | Carries PO-1 | Plumbing |
| PO-3 | Rejection/flip zone is DECISION when its sources span 2+ families (Phase 3, C1); else TARGET | "Full alignment" (Part 1, 00:37:00–00:37:30) | Jeron |
| PO-6 | MAP4: POC/HVN zones cover the whole high-volume area (70% of peak, 10–40 pts) | Part 1, 00:08:10–00:08:35 | Jeron. 70% and 40 pts ours |
| PO-7 | Weekly delta profile; delta bands become TARGET zones | Part 1, 00:11:18–00:12:00, 00:17:38, 01:02:37; Part 2, 00:06:58 | Jeron. 20% ours |
| PO-8 | VWAP, weekly VWAP and ±1σ bands: one source family (C2) | Part 1, 00:37:23–00:37:30, 01:03:00–01:05:11; Part 2, 00:28:52, 00:32:53, 01:19:18 | Jeron (one family in the location arm; on/off split reported). 5 pts ours |
| PO-9 | Acceptance state of weekly and PD value edges | Part 1, 00:34:58–00:35:10, 00:15:29, 00:19:08; Part 2, 00:38:09–00:39:00 | Jeron. 60 min / 80% / 20% ours |
| PO-11 | Double distribution edge zone (DD\_EDGE) | Part 1, 01:21:35–01:22:02; Part 2, 00:36:08 | Jeron. 40 pts ours |
| PO-13 | Map stays at 08:10; 08:29 comparison as research | Part 1, 00:03:28, 00:38:00–00:38:04 | Jeron re-checks, does not rebuild |
| Research | TPO value areas/POCs, settlement, single prints: tags only | No Jeron source found | Not Jeron |
| Open | All-time-high to swing-low profile with business zones | Part 2, 00:36:43–00:39:00, 00:52:24 | Jeron. Needs your decision |

## **PO-1. Rejection and flip areas**

### **Window (no hindsight)**

* Data: NQ 1-minute bars with bid/ask volume (MBO aggressor flag in the backtest, Volumetric in NinjaTrader).  
* Look back from the start of the prior-day cash session (08:30 CT) through the developing week (from Sunday 17:00 CT), up to the map's as-of time (08:10 CT). Only bars that closed before the as-of time are used. Jeron draws his profiles from Sunday 18:00 ET to 9:29 ET (00:03:28, 00:07:10).  
* Zones are frozen at the as-of time, like every other map zone.

### **Step 1\. Find the turn**

* A swing high is a 1-minute bar whose high is the highest of the 15 bars before and 15 bars after it *(ours: 15\)*. A swing low is the mirror.  
* The 15 bars after it must have closed before the as-of time, so a turn becomes known only 15 minutes after it happened.

### **Step 2\. Prove the rejection**

A swing high is a rejection (REJ\_HIGH) only if both hold. REJ\_LOW is the mirror.

* Failed aggression on arrival: in the swing bar or the 2 bars before it *(ours: 2\)*, at least one bar has buy delta of 150 or more *(ours: S1.4 MinAbsDelta)*, or a stacked buy imbalance (400%, Jeron), or a large buy trade (Deep Trades 60, Jeron). Jeron: "a lot of aggressive buying attempts… but at the very top there was a seller just waiting" (00:39:35–00:40:30).  
* Fast departure: within 10 bars after the swing *(ours: 10\)*, price trades at least 0.25 × ADR away from the swing high *(ours: 0.25; ADR \= packet ranges.adr\_full)*.

### **Step 3\. Draw the zone**

* REJ\_HIGH: top \= the swing high; bottom \= the lowest bar body (open or close) among the swing bar and the 2 bars on each side. This is the band "from aggressive selling to aggressive selling" (00:38:58).  
* Width: at least 10 points and at most 40 points *(ours)*. Under 10: pad both sides equally; over 40: keep the 40 points nearest the swing extreme. Jeron's zones in Part 1 are about 25–40 points (screenshots 1C\_03: 25,222–25,247; 1D\_01: 24,823–24,863).  
* Two REJ zones on the same side that overlap, or sit within 5 points *(ours)*, merge into one, still capped at 40 points.

### **Step 4\. Flip**

A zone becomes FLIP when all three happen in order inside the window:

* It formed as REJ\_LOW (support), or REJ\_HIGH (resistance).  
* Price then accepted through it: 3 consecutive 1-minute closes at least 2 ticks beyond the far edge *(ours: the strategy's acceptance closes and break distance)*.  
* Later, a REJ in the opposite direction forms with its band overlapping the first zone by at least 50% *(ours)*.

The FLIP zone is the union of the two bands, capped at 40 points. Jeron: "It was previous support. We broke through it. Now we're resisting it" (00:12:08–00:12:16).

### **Step 5\. Tags**

* Session: REJ\_ON (overnight), REJ\_PD (prior-day cash), REJ\_WK (earlier days of the week).  
* VWAP: the overnight session VWAP (definition in PO-8) at the as-of time is inside the zone or within 5 points *(ours)* (00:06:48, 00:37:23, 00:41:28, 01:05:11).  
* Delta band: the zone overlaps a delta-profile row in the top 20% of absolute delta for the weekly, PD or overnight profile *(ours: 20%)*; tag DELTA\_SELL or DELTA\_BUY (00:11:18–00:12:00).  
* Stack: every weekly, PD or ON value edge, POC or HVN inside the zone or within 5 points *(ours)*.

### **Step 6\. Selection**

* Keep at most 2 REJ/FLIP zones on each side of price within 1 × ADR *(ours)*, nearest first. Ties go to FLIP over REJ, then ON over PD over WK.  
* Zones price has traded through by more than 1 × ADR since they formed are dropped.

## **PO-2. Packet field**

rejection\_zones\[\], one entry per zone: lo, hi, kind (REJ\_HIGH / REJ\_LOW / FLIP), formed\_ct, session (ON / PD / WK), arrival\_evidence (DELTA / IMB / LARGE, with the value), departure\_pts, tags (VWAP, DELTA\_SELL, DELTA\_BUY), stack (list of level names), class (DECISION / TARGET).

## **PO-3. Zone class: DECISION or TARGET**

* DECISION if the zone's sources span 2 or more of the six source families in Phase 3 (C1, approved Nov 1, 2026). The rejection or flip is the structure family; a value edge, a delta band, an HVN / LVN / low-time area, a calculated gamma level or VWAP each adds its own family. TARGET otherwise. In practice a rejection zone with a weekly or PD value edge, POC / HVN or VWAP still qualifies, as before. Jeron: "full alignment" between levels (00:37:00–00:37:30).  
* A REJ/FLIP decision zone that overlaps an existing packet decision zone merges with it (union, capped at 60 points by the existing map rule) and keeps the REJ/FLIP tag. How the plan then reacts at it is Phase 3\.  
* Label example: D\_FLIP\_WKVAL\_PDVAH\_VWAP.

## **PO-6. Map variant MAP4: whole high-volume area**

**Why:** Jeron marks the whole high-volume area around the POC, not the single tick, "to give yourself more room" (00:08:10–00:08:35); his zones in Part 1 are about 25–40 points wide. Book 1 builds every zone around one price padded ±5 points; high-volume areas are only tags, and zone width was never tested (MAP0–MAP3 cover settlement, PD2/PD3 highs and lows and the HTF composite). Nov 18, 2025: Jeron's short area 24,823–24,863 was split by Book 1 into a decision zone (24,846–24,865) and a separate target (T\_HTFPOC, 24,822–24,832).

* Applies to the POC and HVN levels of the developing weekly, PD and ON volume profiles, using 5-point rows.  
* Area \= the run of 5-point rows on either side of the POC or HVN peak whose volume is at least 70% of the peak row *(ours: 70%)*. The run stops at the first row below 70%.  
* Width capped at 40 points *(ours)*, keeping the 40 points centred on the peak. Narrower than 10 points: keep the ±5-point pad.  
* The area replaces the ±5-point pad for POC and HVN levels only; value edges and highs/lows keep it.  
* A TARGET zone inside a DECISION zone's area merges into it and adds its label (for example D\_ONVAH\_WKVAL\_ONTVAH\_HTFPOC).  
* Test: its own pre-registered map variant, run alone and with the location arm. Also report average zone width, average stop in points, sides closed by check C and the share of days APPROVED.

## **PO-7. Delta bands**

**Why:** Jeron uses the delta profile to find where one side was heavy and targets that band: "a significant amount of selling volume here… that would be an area that I want to target" (00:11:18–00:12:00); TP2 is "this area where we know there was a lot of selling activity" (00:17:38); on Wednesday he reads it to see which side won (01:02:37). Book 1's map writes PD and ON delta profiles but nothing uses them, and there is no weekly one.

* Add a developing weekly delta profile (Sunday 17:00 CT to the as-of time), 5-point rows like the PD and ON ones.  
* A delta band is 2 or more adjacent rows with the same sign, each in the top 20% of absolute delta for that profile *(ours: 20%)*, 10–40 points wide *(ours)*. Same-sign bands that overlap or sit within 5 points *(ours)* merge.  
* A selling band above price becomes a TARGET zone for longs; a buying band below price a TARGET zone for shorts (label example T\_DELTA\_SELL\_WK). Opposite-side bands are tags only. A band is never a DECISION zone on its own.  
* Test: part of the location arm; logged: delta bands per day and whether price reached one before the stop. How bands are used as targets is Phase 4 / Phase 6\.

## **PO-8. VWAP and deviation-band tags (logged only)**

**Why:** before the open Jeron checks that VWAP lines up with his levels: "we have VWOP right here… deviation bands up here… alignment between our levels" (Part 1, 00:37:23–00:37:30); Wednesday's open sits on "the point of control, this high volume node and VWOP" (01:03:00–01:05:11). Part 2 also uses the deviation bands as confluence (00:28:52, 00:32:53, 01:19:18). Book 1 computes them but the plan never uses them.

* At 08:10 CT every zone gets VWAP if the session VWAP is inside it or within 5 points *(ours: 5 points)*, and WKVWAP for the weekly VWAP. The ±1σ bands are tagged the same way (VWAP\_SD1\_UP / VWAP\_SD1\_DN).  
* VWAP definition (C2, frozen for the replay): VWAP \= sum(price × volume) / sum(volume) over every trade of the front NQ contract in the Databento MBO data (trade messages, both aggressor sides; same front contract and roll rule as the map). Session VWAP resets at 17:00 CT each trading day (the Globex open), so at 08:10 CT it is the overnight session VWAP. Weekly VWAP resets at the Sunday 17:00 CT open. Bands: ±1 volume-weighted standard deviation around each VWAP. Only trades before 08:10:00 CT are used. The 16:00–17:00 CT halt adds no trades. On a roll day both VWAPs restart on the new front contract at its first session (ours, needed). The 08:30 RTH VWAP is diagnostic only (PO-13) and never changes the 08:10 map.  
* Source family (C2): session VWAP, weekly VWAP and the bands together are one family (VWAP) toward the 2-family minimum in Phase 3 and PO-3; several VWAP tags on one zone still count once. VWAP never creates a zone on its own and never changes a side. The plan logs the 08:10 VWAP and its distance to price.  
* Report: tagged vs untagged zones, how often price reached them in the first NY hour and how often a candidate formed there; drift between the 08:10 and 08:30 VWAP. Diagnostic split (not promotable): the location arm with VWAP counted vs the same arm with VWAP as a tag only, reported in the replay.

## **PO-9. Acceptance state at the value edges**

**Why:** Jeron reads before the open whether price has accepted outside the weekly value area: "value area low here that we've accepted below… building volume and sustaining below it. We also tried to come up pre-market… and we failed" (00:34:58–00:35:10; again 00:39:41, 00:54:46). Monday is the mirror: "a strong acceptance back into the value area" (00:15:29); "since we've traded back into it… not going to come back down" (00:19:08). This doc defines the state only. Its use for sides is Phase 3; its use for context is Phase 2\.

* Applies to the developing weekly VAH and VAL and the PD VAH and VAL at the as-of time.  
* ACCEPTED\_BELOW (VAL): price below the VAL; at least 60 minutes since the first 1-minute close below it *(ours: 60\)*; at least 80% of closes since then below it *(ours: 80%)*; at least 20% of the volume since then below it *(ours: 20%)*. ACCEPTED\_ABOVE (VAH) is the mirror.  
* FAILED\_RECLAIM: while ACCEPTED\_BELOW, a bar traded back into the VAL zone with buy aggression (buy delta 150+, a stacked buy imbalance or a large buy trade) and closed back below it. Mirror for VAH.  
* INSIDE: between VAL and VAH. TESTING: outside but not yet accepted. Each value-edge zone carries its state as a tag (for example D\_WKVAL…\|accept=BELOW\|failed\_reclaim=1).

## **PO-11. Double distribution edge zone**

**Why:** on Wednesday, after a 300–400 point rally into the weekly VAH, Jeron points to a double distribution: a high-volume area, a thin low-volume area, then a second high-volume area (01:21:35–01:21:53). "It will take the equal amount of buying to accept into this double distribution" (01:22:02). Part 2 also notes price consolidating at "this double distribution of this… composite" (00:36:08). The map writes double\_distribution, but Book 1's plan never uses it. This doc defines the zone; the initiation-only side rule is Phase 3\.

* Source: the packet's double\_distribution for the developing weekly and PD profiles. If the packet only flags it, map v2.4 also writes the bounds of both distributions and the low-volume separator.  
* The near edge of the far distribution (the first high-volume rows beyond the separator, as seen from price) becomes a zone, at most 40 points wide *(ours)*, tagged DD\_EDGE. The separator itself is not a zone.  
* The far distribution's opposite edge is a RUNNER candidate for the target ladder (Phase 6).

## **PO-13. Map timing: 08:10 vs Jeron's 08:29**

**Why:** Jeron draws his profiles up to 08:29 CT (00:03:28, 00:07:10) but at the open only checks they have not moved: "make sure the levels still all are the same. Yep, they are" (00:38:00–00:38:04; again 01:04:22). Live, the map runs at 08:10 CT because the plan needs time (Drive sync, a scheduled Claude task that starts a few minutes late, activation at 08:25).

* Live timing is unchanged: map 08:10, plan by 08:20, activation 08:25. Moving to Python would not make the calculation faster; the delay is the hand-offs.  
* Step 1 (Book 1A research, no trade changes): the backtest also builds the map and rules-only plan as of 08:29 CT and reports per day: zones added, dropped or moved more than 2 ticks; acceptance states, VWAP tags, REJ/FLIP zones, context or draw lines that changed; and whether the day traded differently.  
* Step 2, only if Step 1 shows the gap matters (the threshold is written down before Step 2 is built): a code-only refresh at about 08:28 CT, with no Claude step, that updates tags and states and writes the plan file. It never adds a zone the 08:10 plan did not allow, and needs its own parity check and test before live use.  
* Not in this doc: moving entries to Python or letting XGBoost choose entries. Entries stay in NinjaTrader until something passes its own holdout; XGBoost stays exploratory.

## **Inserted map items (from the former PO-12)**

* Moved to research (logged as tags only; no longer a DECISION family, a TARGET zone or a ladder step): TPO value areas and POCs, the settlement level, single prints. No Jeron source found in Part 1, Part 2 or the transcript findings.  
* Needed (Jeron gives the idea, not the number; kept and marked ours): merge 15 points, pad ±5 points (PO-6 changes this for POC/HVN), 60-point cap, DECISION \= 2 or more families. Jeron says "full alignment" (00:37:00) and marks areas, but gives no widths or counts.  
* Kept as is (Jeron): prior-day and overnight value areas and POCs, developing weekly and prior-week profiles, HVN/LVN composites, the 60-day composite (Jeron's "3-month composite", Part 2, 00:04:20), overnight inventory, and the balance composite (Jeron's balance merge, Parts 5–6).

## **Open item: all-time-high profile (needs your decision)**

Part 2: Jeron also draws "a volume profile from all-time highs down to this swing low" with "peak and valley" and its business zones (00:36:43–00:39:00), and price later found support at that profile's VAL and business zone (00:52:24). Book 1 has no such level (dated manual HTF levels are excluded in the backtest). Options: (a) add it to the map, computed from history between the all-time high and the latest swing low; or (b) log it as research only. Decided Nov 1, 2026 (E6): (b) research only for the Book 1A replay. The profile's levels and their overlap with Book 1A zones are logged; it gets its own registered test later.

## **Expected effect on the Nov 17–19, 2025 maps (to be checked by rerun)**

| Day | Jeron's level | Book 1 map / plan | Expected from the Book 1A map |
| :---- | :---- | :---- | :---- |
| Mon 11/17 | Long on the reclaim of weekly VAL (about 25,085); TP2 at 25,222–25,247 | Long zone 25,072–25,083 present; 25,222–25,247 missing | 25,222–25,247 appears as a REJ/FLIP zone with DELTA\_SELL (PO-1, PO-7); the weekly VAL zone carries its acceptance state (PO-9) |
| Tue 11/18 | Short at 24,823–24,863 (weekly VAL \+ daily VAH \+ VWAP \+ overnight rejection) | Split into 24,846–24,865 (decision) and 24,822–24,832 (target) | One zone near 24,823–24,863 with REJ \+ WKVAL \+ VWAP tags (PO-1, PO-6, PO-8); state ACCEPTED\_BELOW with FAILED\_RECLAIM (PO-9) |
| Wed 11/19 | Open at POC \+ HVN \+ VWAP; long toward weekly VAH; short at the double distribution | POC-area zones present; no double distribution zone | POC area as a high-volume zone with VWAP tag (PO-6, PO-8); DD\_EDGE zone at the weekly VAH (PO-11). Check the packet |

## **How it is tested**

* Diagnostic first (does not count): rerun map v2.4 and the rules-only plan on Nov 17–19, 2025 and compare the zones with Jeron's levels and screenshots.  
* Pre-register before any Book 1A result is read: the location arm (PO-1, PO-2, PO-3, PO-7, PO-9, PO-11 here, plus the Phase 2–4 drafts once reviewed) as one map/plan arm; PO-6 (MAP4) as its own map variant; and the combined run.  
* Judge each against A0 on the same sessions with the promotion rule from design v3.9 (paired net R per session, 90% bootstrap lower bound above 0, drawdown within 1.25 × A0, at least 20 trades that differ).  
* Logged in every run: PO-8 tags, PO-13 08:10-vs-08:29 comparison, the research items above, REJ/FLIP zones per day and how often price reached one in the first NY hour.

## **Not changing**

* Map as-of time stays 08:10 CT live. Entry rules, grades, gates and exits in strategy S1.4 are unchanged here. GEX stays logged only.
