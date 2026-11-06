# P0.7-P0.9 hand-check sheet: Oct 22, 29, 31 and Nov 18, 2025 (hand-check-sheet-v1.4)

Check each value against the source named on its row, not against the plan. Sources: **NT VP** = the NinjaTrader Volume Profile tool drawn over the stated window (CT); **NT VWAP** = the NinjaTrader VWAP setting stated on the row; **GEX csv** = `gex_levels_block1.csv`, row session = the day, the named column; **sidecar** = the frozen plan sidecar `PreopenPlan_<day>_book1a.json`, the named key. Every value is frozen at 08:10 CT from data before 08:10 CT. No trades, outcomes or P&L.

**Tolerance (Kyron, Nov 4).** Highs and lows must match exactly. A profile value (POC, VAH, VAL, an HVN / LVN block edge, a separator edge, a delta band edge) may differ from the chart by at most one 5-point row, and only if that difference does not change whether a zone forms, merges or becomes a decision zone. Any other difference is material: write it in the match column as MATERIAL.

**VWAP.** The VWAP formula (volume-weighted price of all trades from the reset to 08:09:59.999 CT, and the volume-weighted standard deviation for the +/-1 sigma bands) was already verified against raw Databento trades in P0.6 (Oct 22, Nov 5 and both roll days). Here only check that the NinjaTrader VWAP with the stated setting shows the same numbers at the bar stamped 08:10.

Each day's plan was rebuilt with the frozen code for this sheet; the rebuilt plan text equals the frozen plan file byte for byte, so the evidence tables are the inputs of the frozen plan.

## 2025-10-22 (Wed)

Plan plan-v2.4-book1a-v1.6; market_context BALANCED; review APPROVED; 3 decision zones.

### 08:10 values

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 25258.75 | close of the bar stamped 08:10 on a 1-minute chart | | |
| session vwap | 25267.38 | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_up | 25296.63 | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_dn | 25238.13 | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly vwap | 25262.44 | the VWAP line: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 19 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_up | 25337.16 | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 19 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_dn | 25187.72 | the -1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 19 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| market_context | BALANCED | the inputs in the context evidence below (sidecar `plan` line `market_context=`) | | |
| context_base | BALANCED | the inputs in the context evidence below (sidecar `plan` line `context_base=`) | | |
| htf_acceptance | NONE | the inputs in the context evidence below (sidecar `plan` line `htf_acceptance=`) | | |
| draw_status | NONE | the inputs in the context evidence below (sidecar `plan` line `draw_status=`) | | |
| balance | 25256.00-25340.50 | the inputs in the context evidence below (sidecar `plan` line `balance=`) | | |
| balance_poc | 25318.00 | the inputs in the context evidence below (sidecar `plan` line `balance_poc=`) | | |
| value_follows | DIVERGENT_UP | the inputs in the context evidence below (sidecar `plan` line `value_follows=`) | | |
| on_inventory | NET_SHORT | the inputs in the context evidence below (sidecar `plan` line `on_inventory=`) | | |
| on_vs_settle | -36.0 | the inputs in the context evidence below (sidecar `plan` line `on_vs_settle=`) | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | POS | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| htfval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `htfval_state=` | | |
| htfvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `htfvah_state=` | | |
| weekly double distribution | AVAILABLE; split no | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |

### Context evidence: the inputs behind each label (check the inputs on the chart, not the label)

**market_context = BALANCED** (context_base = BALANCED, htf_acceptance = NONE). Step 1, context_base (plan_fields.context_base): BULLISH = price >= HTF VAL, the low of the bars window <= HTF VAL (held or reclaimed it) and the weekly VAL state is not ACCEPTED_BELOW; BEARISH = the mirror at HTF VAH (state not ACCEPTED_ABOVE); exactly one of them = that label; else BALANCED if the balance composite overlaps; else NONE_CONFLICT if a directional read passed but the weekly acceptance blocked it (or both reads passed), else NONE_NO_EVIDENCE. Step 2, the Nov 5 precedence with htf_acceptance (below).

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| price at 08:10 | 25258.75 | close of the bar stamped 08:10 (1-minute chart) | | |
| HTF VAL | 23590.0 | NT VP over the HTF composite: 60 days from 2025-07-29 through 2025-10-22 08:10 CT (map source MINUTE_APPROX) | | |
| HTF VAH | 25394.75 | same HTF composite profile | | |
| HTF POC | 24827.5 | same HTF composite profile | | |
| low of the bars window | 24410.0 | 1-minute bars 2025-10-12 17:00 - 2025-10-22 08:10 CT: lowest low | | |
| high of the bars window | 25368.0 | 1-minute bars 2025-10-12 17:00 - 2025-10-22 08:10 CT: highest high | | |
| held or reclaimed HTF VAL (price >= 23590.0 and low <= 23590.0) | N | from the rows above | | |
| failed or lost HTF VAH (price <= 25394.75 and high >= 25394.75) | N | from the rows above | | |
| weekly VAL / VAH | 25244.25 / 25340.5 | NT VP over the developing week Sun Oct 19 17:00 - 10-22 08:10 CT | | |
| weekly VAL state / VAH state | INSIDE / INSIDE | PO-9 acceptance on 1-minute closes vs the weekly VAL / VAH: INSIDE = price at 08:10 inside the weekly value (or on the inside of that edge); TESTING = price beyond the edge, not yet accepted; ACCEPTED_* = the minutes since the first close beyond it, the share of closes beyond and the share of volume beyond meet the frozen PO-9 thresholds (>= 60 minutes, >= 80% of closes, >= 20% of volume) (details in the plan lines `wkval_state=` / `wkvah_state=`) | | |
| balance composite overlaps | Y | see balance below | | |
| context_base | BALANCED | from the rows above | | |

**htf_acceptance = NONE.** Rule (Context doc, Nov 5, 2026; ours: acceptance outside composite value as context evidence, informed by Jeron Part 1, 00:34:58): the PO-9 acceptance definition, unchanged, at the HTF composite VAH and VAL: price at 08:10 beyond the edge, >= 60 minutes since the first 1-minute close beyond it (the first close of the current run of closes beyond, scanning back from 08:10), >= 80% of the closes since then beyond it, >= 20% of the volume since that close beyond it; bars closed at or before 08:10 CT only (the bar stamped 08:10 = trades 08:09:00-08:09:59.999 is the last one). ACCEPTED_ABOVE at the VAH = ABOVE, ACCEPTED_BELOW at the VAL = BELOW, else NONE. Context evidence only, never an entry signal. Precedence: BULLISH + ABOVE = BULLISH; BEARISH + BELOW = BEARISH; BULLISH + BELOW or BEARISH + ABOVE = NONE (conflict); BALANCED stays BALANCED whatever the acceptance; NONE_NO_EVIDENCE + ABOVE = BULLISH, + BELOW = BEARISH; NONE_CONFLICT stays NONE; no acceptance (NONE) = the existing label kept; then the weekly guard on every BULLISH (not ACCEPTED_BELOW the weekly VAL) and every BEARISH (not ACCEPTED_ABOVE the weekly VAH): failure = NONE_CONFLICT -> NONE (clarified Nov 5, 2026).

| edge | level | state | first 1-minute close beyond (CT, close) | minutes since | closes beyond | volume beyond | window (CT) | hand | match |
|---|---|---|---|---|---|---|---|---|---|
| HTFVAL (below) | 23590.0 | INSIDE | none (price at 08:10 not below the edge) |  |  |  | 1-minute bars 2025-10-12 17:00 - 2025-10-22 08:10 CT; level from the HTF composite: 60 days from 2025-07-29 through 2025-10-22 08:10 CT (map source MINUTE_APPROX) | | |
| HTFVAH (above) | 25394.75 | INSIDE | none (price at 08:10 not above the edge) |  |  |  | 1-minute bars 2025-10-12 17:00 - 2025-10-22 08:10 CT; level from the HTF composite: 60 days from 2025-07-29 through 2025-10-22 08:10 CT (map source MINUTE_APPROX) | | |

**Precedence result:** context_base BALANCED + htf_acceptance NONE -> BALANCED; weekly guard N/A (weekly VAL INSIDE, weekly VAH INSIDE) = market_context **BALANCED** (context_source NONE).

**Context invalidation edge: none.** No directional context, so no invalidation line. The plan writes it 2 ticks beyond the edge (`invalidate_below=` / `invalidate_above=`); S1.4 switches the context to Balanced after 3 consecutive 1-minute closes beyond that line (AcceptBars = 3, the strategy's acceptance rule). Context invalidation only, never a trade stop.

**balance = 25256-25340.5, balance_poc = 25318.** Rule (map BalanceJson): PD and ON value areas must overlap; PD2 joins if PD2 and PD overlap; the members are merged into one volume profile and its 70% value area is the balance. Overlap % = overlap / the narrower value area.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD2 VAH / POC / VAL | 25353 / 25318.5 / 25276.75 | NT VP over Mon Oct 20 cash 08:30-15:00 CT | | |
| PD VAH / POC / VAL | 25326 / 25300 / 25254 | NT VP over Tue Oct 21 cash 08:30-15:00 CT | | |
| ON VAH / POC / VAL | 25286.5 / 25250 / 25222.75 | NT VP over the overnight Tue Oct 21 17:00 - 10-22 08:10 CT | | |
| overlap PD2-PD | 68.4% | from the PD2 and PD value areas | | |
| overlap PD-ON | 51.0% | from the PD and ON value areas | | |
| members | PD2, PD, ON | | | |
| merged VAH / POC / VAL | 25340.5 / 25318 / 25256 | NT VP over the members' windows together (PD2, PD, ON; PD and PD2 cash only, ON overnight Tue Oct 21 17:00 - 10-22 08:10 CT); not one continuous window, so check the member values above first | | |
| merged high / low | 25354.5 / 25114.75 | highs and lows of the members' windows | | |

**value_follows = DIVERGENT_UP.** Rule (plan_fields.value_follows): DIVERGENT_UP = PD high > PD2 high AND PD VAH < PD2 VAH AND PD POC < PD2 POC; DIVERGENT_DOWN = PD low < PD2 low AND PD VAL > PD2 VAL AND PD POC > PD2 POC; else WITH_PRICE. Highs and lows are the full trading day; value areas are the cash session.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD high / low | 25368 / 25203.25 | Tue Oct 21 full trading day (Mon Oct 20 17:00 - Tue Oct 21 16:00 CT): high / low | | |
| PD2 high / low | 25354.5 / 24955.75 | Mon Oct 20 full trading day (Sun Oct 19 17:00 - Mon Oct 20 16:00 CT): high / low | | |
| PD VAH / VAL / POC | 25326 / 25254 / 25300 | NT VP over Tue Oct 21 cash 08:30-15:00 CT | | |
| PD2 VAH / VAL / POC | 25353 / 25276.75 / 25318.5 | NT VP over Mon Oct 20 cash 08:30-15:00 CT | | |
| DIVERGENT_UP tests: higher high / lower VAH / lower POC | Y / Y / Y | from the rows above | | |
| DIVERGENT_DOWN tests: lower low / higher VAL / higher POC | N / N / N | from the rows above | | |

**on_inventory = NET_SHORT, on_vs_settle = -36.0.** Rule (plan_fields.on_inventory): NET_LONG if price at 08:10 > the ON VWAP, NET_SHORT if below; on_vs_settle = price - the PD settlement. The overnight high / low vs the settlement are shown for reference; the rule does not use them.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| ON VWAP | 25267.38 | session VWAP: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| price at 08:10 | 25258.75 | close of the bar stamped 08:10 | | |
| PD settlement | 25294.75 | Tue Oct 21: volume-weighted price of the trades in the 30 s before 15:00 CT (map SettleOf); CME's settlement can differ by a tick | | |
| on_vs_settle (price - settlement) | -36.0 | from the rows above | | |
| ON high / ON low | 25338.25 / 25206.5 | overnight Tue Oct 21 17:00 - 10-22 08:10 CT: high / low | | |
| ON high - settlement / ON low - settlement (reference) | 43.50 / -88.25 | from the rows above | | |

**draw_status = NONE.** Rule (plan_v24): the draw is the nearest candidate in the context direction: BULLISH = HTF POC / HTF VAH above price, MAP4 POC areas above price, GEX levels above price; BEARISH = the mirror below price. NONE = no draw candidate exists (Context spec, Kyron Nov 4); it is never treated as ACTIVE: no draw= line is written and the ladder gets no draw.

No candidate: market_context is BALANCED, so the rule has no direction to look in and no candidate exists. For reference, the HTF levels the rule would scan: HTF POC 24827.5 (below price), HTF VAH 25394.75, HTF VAL 23590.0 (price 25258.75). Check that the context inputs above give BALANCED; then NONE follows.

### GEX values (source: GEX csv)

| level | value in plan | check against | hand | match |
|---|---|---|---|---|
| CR | 25400.00 | GEX csv: row 2025-10-22, column `call_resistance_nt` (= 25400.0); CME report 2025-10-21 (D-1) | | |
| PS | 23750.00 | GEX csv: row 2025-10-22, column `put_support_nt` (= 23750.0); CME report 2025-10-21 (D-1) | | |
| HVL | 25230.00 | GEX csv: row 2025-10-22, column `hvl_nt` (= 25230.0); CME report 2025-10-21 (D-1) | | |
| CR_0DTE | 25400.00 | GEX csv: row 2025-10-22, column `call_resistance_0dte_nt` (= 25400.0); CME report 2025-10-21 (D-1) | | |
| PS_0DTE | 25130.00 | GEX csv: row 2025-10-22, column `put_support_0dte_nt` (= 25130.0); CME report 2025-10-21 (D-1) | | |
| HVL_0DTE | 25260.00 | GEX csv: row 2025-10-22, column `hvl_0dte_nt` (= 25260.0); CME report 2025-10-21 (D-1) | | |
| regime | positive | GEX csv: row 2025-10-22, column `regime` | | |

### Decision zones: every level behind each zone

**D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA**: 25198.25 - 25265.0 (66.75 pts); families 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 269 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDVAL | AUCTION_VALUE / VP | 25254.0 | inside | NT VP, Tue Oct 21 cash 08:30-15:00 CT, volume profile | | |
| PDL | STRUCTURE / VP | 25203.25 | inside | NT VP, Tue Oct 21 cash 08:30-15:00 CT, low | | |
| ONPOC | VOLUME / VP | 25250.0 | inside | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, volume profile | | |
| ONVAL | AUCTION_VALUE / VP | 25222.75 | inside | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, volume profile | | |
| ONTPOC | VOLUME / VP | 25267.5 | 2.50 pts outside | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, TPO profile | | |
| ONTVAL | AUCTION_VALUE / VP | 25235.0 | inside | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, TPO profile | | |
| ONL | STRUCTURE / VP | 25206.5 | inside | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, low | | |
| VWAP | VWAP / VWAP | 25267.5 | 2.50 pts outside | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAPL1 | VWAP / VWAP | 25238.25 | inside | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| WKVAL | AUCTION_VALUE / VP | 25244.25 | inside | NT VP, developing week Sun Oct 19 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_DN | VWAP / VWAP | 25238.13 | inside | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 21 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| WKVWAP | VWAP / VWAP | 25262.44 | inside | the VWAP line: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 19 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| HVL | GEX / GEX | 25230.0 | inside | GEX csv: row 2025-10-22, column `hvl_nt` (= 25230.0); CME report 2025-10-21 (D-1) | | |
| HVL_0DTE | GEX / GEX | 25260.0 | inside | GEX csv: row 2025-10-22, column `hvl_0dte_nt` (= 25260.0); CME report 2025-10-21 (D-1) | | |
| T_DELTA_SELL_WK | DELTA / VP | 25215.0 - 25225.0 | overlaps; 3 delta bands share this label | NT VP with delta, WK profile (developing week Sun Oct 19 17:00 - 08:10 CT), 5-pt rows 25215.0-25225.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_WK | DELTA / VP | 25270.0 - 25280.0 | within 5.00 pts (above the zone; counts by the 5-pt family tolerance); 3 delta bands share this label | NT VP with delta, WK profile (developing week Sun Oct 19 17:00 - 08:10 CT), 5-pt rows 25270.0-25280.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 25215.0 - 25225.0 | overlaps; 2 delta bands share this label | NT VP with delta, PD profile (Tue Oct 21 cash 08:30-15:00 CT), 5-pt rows 25215.0-25225.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 25270.0 - 25280.0 | within 5.00 pts (above the zone; counts by the 5-pt family tolerance); 2 delta bands share this label | NT VP with delta, PD profile (Tue Oct 21 cash 08:30-15:00 CT), 5-pt rows 25270.0-25280.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_ON | DELTA / VP | 25225.0 - 25240.0 | overlaps | NT VP with delta, ON profile (overnight Tue Oct 21 17:00 - 08:10 CT), 5-pt rows 25225.0-25240.0: SELL delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | VOLUME / VP | 25245.0 - 25265.0 | overlaps | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (25250.0) | | |

**D_PDVAH_ONH_WKVAH_PDH_PD2VAH_PD2H_P2**: 25325.5 - 25364.75 (39.25 pts); families 5: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, VWAP; long=INITIATION short=ANY; stop 159 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDVAH | AUCTION_VALUE / VP | 25326.0 | inside | NT VP, Tue Oct 21 cash 08:30-15:00 CT, volume profile | | |
| PDH | STRUCTURE / VP | 25348.5 | inside | NT VP, Tue Oct 21 cash 08:30-15:00 CT, high | | |
| PD2H | STRUCTURE / VP | 25354.5 | inside | NT VP, Mon Oct 20 cash 08:30-15:00 CT, high | | |
| ONH | STRUCTURE / VP | 25338.25 | inside | NT VP, overnight Tue Oct 21 17:00 - 08:10 CT, high | | |
| WKVAH | AUCTION_VALUE / VP | 25340.5 | inside | NT VP, developing week Sun Oct 19 17:00 - 08:10 CT, volume profile | | |
| WKVWAP_SD1_UP | VWAP / VWAP | 25337.16 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 19 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| T_DELTA_BUY_WK | DELTA / VP | 25315.0 - 25355.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 19 17:00 - 08:10 CT), 5-pt rows 25315.0-25355.0: BUY delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | VOLUME / VP | 25292.5 - 25332.5 | overlaps | NT VP, Tue Oct 21 cash 08:30-15:00 CT, 5-pt rows >= 70% of the peak row (25310.0) | | |

**T_HTFVAH**: 25389.75 - 25399.75 (10.00 pts); families 2: AUCTION_VALUE, GEX; long=ANY short=ANY; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| HTFVAH | AUCTION_VALUE / VP | 25394.75 | inside | NT VP over the packet's window (HTF composite (packet htf_composite window)) | | |
| CR | GEX / GEX | 25400.0 | 0.25 pts outside | GEX csv: row 2025-10-22, column `call_resistance_nt` (= 25400.0); CME report 2025-10-21 (D-1) | | |
| CR_0DTE | GEX / GEX | 25400.0 | 0.25 pts outside | GEX csv: row 2025-10-22, column `call_resistance_0dte_nt` (= 25400.0); CME report 2025-10-21 (D-1) | | |

## 2025-10-29 (Wed)

Plan plan-v2.4-book1a-v1.6; market_context BULLISH; review APPROVED; 4 decision zones.

### 08:10 values

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 26271 | close of the bar stamped 08:10 on a 1-minute chart | | |
| session vwap | 26247.05 | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_up | 26281.76 | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_dn | 26212.34 | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly vwap | 26007.58 | the VWAP line: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_up | 26151.07 | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_dn | 25864.08 | the -1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| market_context | BULLISH | the inputs in the context evidence below (sidecar `plan` line `market_context=`) | | |
| context_base | NONE_NO_EVIDENCE | the inputs in the context evidence below (sidecar `plan` line `context_base=`) | | |
| htf_acceptance | ABOVE | the inputs in the context evidence below (sidecar `plan` line `htf_acceptance=`) | | |
| draw_status | ACTIVE | the inputs in the context evidence below (sidecar `plan` line `draw_status=`) | | |
| draw | 26295.00-26305.00|CR | the inputs in the context evidence below (sidecar `plan` line `draw=`) | | |
| value_follows | WITH_PRICE | the inputs in the context evidence below (sidecar `plan` line `value_follows=`) | | |
| on_inventory | NET_LONG | the inputs in the context evidence below (sidecar `plan` line `on_inventory=`) | | |
| on_vs_settle | 107.5 | the inputs in the context evidence below (sidecar `plan` line `on_vs_settle=`) | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | POS | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| htfval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `htfval_state=` | | |
| htfvah_state | accept=ABOVE|failed_reclaim=0 | sidecar `plan` line `htfvah_state=` | | |
| weekly double distribution | AVAILABLE; split yes | the criteria table below (ours: PD rule applied to weekly) | | |

### Context evidence: the inputs behind each label (check the inputs on the chart, not the label)

**market_context = BULLISH** (context_base = NONE_NO_EVIDENCE, htf_acceptance = ABOVE). Step 1, context_base (plan_fields.context_base): BULLISH = price >= HTF VAL, the low of the bars window <= HTF VAL (held or reclaimed it) and the weekly VAL state is not ACCEPTED_BELOW; BEARISH = the mirror at HTF VAH (state not ACCEPTED_ABOVE); exactly one of them = that label; else BALANCED if the balance composite overlaps; else NONE_CONFLICT if a directional read passed but the weekly acceptance blocked it (or both reads passed), else NONE_NO_EVIDENCE. Step 2, the Nov 5 precedence with htf_acceptance (below).

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| price at 08:10 | 26271.0 | close of the bar stamped 08:10 (1-minute chart) | | |
| HTF VAL | 23655.0 | NT VP over the HTF composite: 60 days from 2025-08-05 through 2025-10-29 08:10 CT (map source MINUTE_APPROX) | | |
| HTF VAH | 25394.75 | same HTF composite profile | | |
| HTF POC | 24827.5 | same HTF composite profile | | |
| low of the bars window | 24804.75 | 1-minute bars 2025-10-19 17:00 - 2025-10-29 08:10 CT: lowest low | | |
| high of the bars window | 26309.75 | 1-minute bars 2025-10-19 17:00 - 2025-10-29 08:10 CT: highest high | | |
| held or reclaimed HTF VAL (price >= 23655.0 and low <= 23655.0) | N | from the rows above | | |
| failed or lost HTF VAH (price <= 25394.75 and high >= 25394.75) | N | from the rows above | | |
| weekly VAL / VAH | 25907.5 / 26303.25 | NT VP over the developing week Sun Oct 26 17:00 - 10-29 08:10 CT | | |
| weekly VAL state / VAH state | INSIDE / INSIDE | PO-9 acceptance on 1-minute closes vs the weekly VAL / VAH: INSIDE = price at 08:10 inside the weekly value (or on the inside of that edge); TESTING = price beyond the edge, not yet accepted; ACCEPTED_* = the minutes since the first close beyond it, the share of closes beyond and the share of volume beyond meet the frozen PO-9 thresholds (>= 60 minutes, >= 80% of closes, >= 20% of volume) (details in the plan lines `wkval_state=` / `wkvah_state=`) | | |
| balance composite overlaps | N | see balance below | | |
| context_base | NONE_NO_EVIDENCE | from the rows above | | |

**htf_acceptance = ABOVE.** Rule (Context doc, Nov 5, 2026; ours: acceptance outside composite value as context evidence, informed by Jeron Part 1, 00:34:58): the PO-9 acceptance definition, unchanged, at the HTF composite VAH and VAL: price at 08:10 beyond the edge, >= 60 minutes since the first 1-minute close beyond it (the first close of the current run of closes beyond, scanning back from 08:10), >= 80% of the closes since then beyond it, >= 20% of the volume since that close beyond it; bars closed at or before 08:10 CT only (the bar stamped 08:10 = trades 08:09:00-08:09:59.999 is the last one). ACCEPTED_ABOVE at the VAH = ABOVE, ACCEPTED_BELOW at the VAL = BELOW, else NONE. Context evidence only, never an entry signal. Precedence: BULLISH + ABOVE = BULLISH; BEARISH + BELOW = BEARISH; BULLISH + BELOW or BEARISH + ABOVE = NONE (conflict); BALANCED stays BALANCED whatever the acceptance; NONE_NO_EVIDENCE + ABOVE = BULLISH, + BELOW = BEARISH; NONE_CONFLICT stays NONE; no acceptance (NONE) = the existing label kept; then the weekly guard on every BULLISH (not ACCEPTED_BELOW the weekly VAL) and every BEARISH (not ACCEPTED_ABOVE the weekly VAH): failure = NONE_CONFLICT -> NONE (clarified Nov 5, 2026).

| edge | level | state | first 1-minute close beyond (CT, close) | minutes since | closes beyond | volume beyond | window (CT) | hand | match |
|---|---|---|---|---|---|---|---|---|---|
| HTFVAL (below) | 23655.0 | INSIDE | none (price at 08:10 not below the edge) |  |  |  | 1-minute bars 2025-10-19 17:00 - 2025-10-29 08:10 CT; level from the HTF composite: 60 days from 2025-08-05 through 2025-10-29 08:10 CT (map source MINUTE_APPROX) | | |
| HTFVAH (above) | 25394.75 | ACCEPTED_ABOVE | 2025-10-24 07:31 (25505.5) | 7239 (need >= 60) | 100.0% (need >= 80%) | 100.0% (need >= 20%) | 1-minute bars 2025-10-19 17:00 - 2025-10-29 08:10 CT; level from the HTF composite: 60 days from 2025-08-05 through 2025-10-29 08:10 CT (map source MINUTE_APPROX) | | |

**Precedence result:** context_base NONE_NO_EVIDENCE + htf_acceptance ABOVE -> BULLISH; weekly guard PASS (weekly VAL INSIDE, weekly VAH INSIDE) = market_context **BULLISH** (context_source HTF_ACCEPTANCE).

**Context invalidation edge: below 25394.75.** Acceptance-based context: it invalidates at the composite edge it is accepted beyond (Bullish: 3 closes below the composite VAH; Bearish: 3 closes above the composite VAL). The plan writes it 2 ticks beyond the edge (`invalidate_below=` / `invalidate_above=`); S1.4 switches the context to Balanced after 3 consecutive 1-minute closes beyond that line (AcceptBars = 3, the strategy's acceptance rule). Context invalidation only, never a trade stop.

**balance = none.** Rule (map BalanceJson): PD and ON value areas must overlap; PD2 joins if PD2 and PD overlap; the members are merged into one volume profile and its 70% value area is the balance. Overlap % = overlap / the narrower value area.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD2 VAH / POC / VAL | 25980.5 / 25925 / 25866 | NT VP over Mon Oct 27 cash 08:30-15:00 CT | | |
| PD VAH / POC / VAL | 26154.5 / 26045 / 26015 | NT VP over Tue Oct 28 cash 08:30-15:00 CT | | |
| ON VAH / POC / VAL | 26291.75 / 26240 / 26231.75 | NT VP over the overnight Tue Oct 28 17:00 - 10-29 08:10 CT | | |
| overlap PD2-PD | 0% | from the PD2 and PD value areas | | |
| overlap PD-ON | 0% | from the PD and ON value areas | | |
| members | none | | | |

**value_follows = WITH_PRICE.** Rule (plan_fields.value_follows): DIVERGENT_UP = PD high > PD2 high AND PD VAH < PD2 VAH AND PD POC < PD2 POC; DIVERGENT_DOWN = PD low < PD2 low AND PD VAL > PD2 VAL AND PD POC > PD2 POC; else WITH_PRICE. Highs and lows are the full trading day; value areas are the cash session.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD high / low | 26231.5 / 25943 | Tue Oct 28 full trading day (Mon Oct 27 17:00 - Tue Oct 28 16:00 CT): high / low | | |
| PD2 high / low | 26013.5 / 25700 | Mon Oct 27 full trading day (Sun Oct 26 17:00 - Mon Oct 27 16:00 CT): high / low | | |
| PD VAH / VAL / POC | 26154.5 / 26015 / 26045 | NT VP over Tue Oct 28 cash 08:30-15:00 CT | | |
| PD2 VAH / VAL / POC | 25980.5 / 25866 / 25925 | NT VP over Mon Oct 27 cash 08:30-15:00 CT | | |
| DIVERGENT_UP tests: higher high / lower VAH / lower POC | Y / N / N | from the rows above | | |
| DIVERGENT_DOWN tests: lower low / higher VAL / higher POC | N / Y / Y | from the rows above | | |

**on_inventory = NET_LONG, on_vs_settle = 107.5.** Rule (plan_fields.on_inventory): NET_LONG if price at 08:10 > the ON VWAP, NET_SHORT if below; on_vs_settle = price - the PD settlement. The overnight high / low vs the settlement are shown for reference; the rule does not use them.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| ON VWAP | 26247.05 | session VWAP: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| price at 08:10 | 26271.0 | close of the bar stamped 08:10 | | |
| PD settlement | 26163.5 | Tue Oct 28: volume-weighted price of the trades in the 30 s before 15:00 CT (map SettleOf); CME's settlement can differ by a tick | | |
| on_vs_settle (price - settlement) | 107.5 | from the rows above | | |
| ON high / ON low | 26309.75 / 26164.5 | overnight Tue Oct 28 17:00 - 10-29 08:10 CT: high / low | | |
| ON high - settlement / ON low - settlement (reference) | 146.25 / 1.00 | from the rows above | | |

**draw_status = ACTIVE.** Rule (plan_v24): the draw is the nearest candidate in the context direction: BULLISH = HTF POC / HTF VAH above price, MAP4 POC areas above price, GEX levels above price; BEARISH = the mirror below price. NONE = no draw candidate exists (Context spec, Kyron Nov 4); it is never treated as ACTIVE: no draw= line is written and the ladder gets no draw.

| candidate | level (with pad) | distance pts | check in | hand | match |
|---|---|---|---|---|---|
| CR | 26295.0 - 26305.0 | 29.0 | see the level's source | | |
| CR_0DTE | 26295.0 - 26305.0 | 29.0 | see the level's source | | |
### GEX values (source: GEX csv)

| level | value in plan | check against | hand | match |
|---|---|---|---|---|
| CR | 26300.00 | GEX csv: row 2025-10-29, column `call_resistance_nt` (= 26300.0); CME report 2025-10-28 (D-1) | | |
| PS | 26180.00 | GEX csv: row 2025-10-29, column `put_support_nt` (= 26180.0); CME report 2025-10-28 (D-1) | | |
| HVL | 24990.00 | GEX csv: row 2025-10-29, column `hvl_nt` (= 24990.0); CME report 2025-10-28 (D-1) | | |
| CR_0DTE | 26300.00 | GEX csv: row 2025-10-29, column `call_resistance_0dte_nt` (= 26300.0); CME report 2025-10-28 (D-1) | | |
| PS_0DTE | 26180.00 | GEX csv: row 2025-10-29, column `put_support_0dte_nt` (= 26180.0); CME report 2025-10-28 (D-1) | | |
| HVL_0DTE | 26210.00 | GEX csv: row 2025-10-29, column `hvl_0dte_nt` (= 26210.0); CME report 2025-10-28 (D-1) | | |
| regime | positive | GEX csv: row 2025-10-29, column `regime` | | |

### Decision zones: every level behind each zone

**PDPOC_AREA_DD_EDGE_PD_D_PDPOC_WKPOC_PDTPOC**: 26035.0 - 26079.75 (44.75 pts); families 3: STRUCTURE, DELTA, VOLUME; long=ANY short=INITIATION; stop 181 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDPOC | VOLUME / VP | 26045.0 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, volume profile | | |
| PDTPOC | VOLUME / VP | 26052.5 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, TPO profile | | |
| WKPOC | VOLUME / VP | 26045.0 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| T_DELTA_BUY_WK | DELTA / VP | 26045.0 - 26055.0 | overlaps; 4 delta bands share this label | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26045.0-26055.0: BUY delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 26030.0 - 26040.0 | overlaps | NT VP with delta, PD profile (Tue Oct 28 cash 08:30-15:00 CT), 5-pt rows 26030.0-26040.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_PD | DELTA / VP | 26045.0 - 26055.0 | overlaps; 2 delta bands share this label | NT VP with delta, PD profile (Tue Oct 28 cash 08:30-15:00 CT), 5-pt rows 26045.0-26055.0: BUY delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_PD | DELTA / VP | 26080.0 - 26095.0 | within 0.25 pts (above the zone; counts by the 5-pt family tolerance); 2 delta bands share this label | NT VP with delta, PD profile (Tue Oct 28 cash 08:30-15:00 CT), 5-pt rows 26080.0-26095.0: BUY delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | VOLUME / VP | 26035.0 - 26055.0 | overlaps | NT VP, Tue Oct 28 cash 08:30-15:00 CT, 5-pt rows >= 70% of the peak row (26035.0) | | |
| DD_EDGE_PD | STRUCTURE / VP | 26039.75 - 26079.75 | overlaps | NT VP over Tue Oct 28 cash 08:30-15:00 CT, 5-pt rows: the PD double distribution (two HVN blocks >= 70% of the smoothed peak, separator 26090.0 - 26109.75) | | |

**D_PDVAH_PDSET_ONL_PDTVAH**: 26149.5 - 26179.75 (30.25 pts); families 4: AUCTION_VALUE, STRUCTURE, GEX, VWAP; long=ANY short=INITIATION; stop 123 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDVAH | AUCTION_VALUE / VP | 26154.5 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, volume profile | | |
| ONL | STRUCTURE / VP | 26164.5 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, low | | |
| WKVWAP_SD1_UP | VWAP / VWAP | 26151.07 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| PS | GEX / GEX | 26180.0 | 0.25 pts outside | GEX csv: row 2025-10-29, column `put_support_nt` (= 26180.0); CME report 2025-10-28 (D-1) | | |
| PS_0DTE | GEX / GEX | 26180.0 | 0.25 pts outside | GEX csv: row 2025-10-29, column `put_support_0dte_nt` (= 26180.0); CME report 2025-10-28 (D-1) | | |

**D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC**: 26220.0 - 26277.5 (57.50 pts); families 5: AUCTION_VALUE, STRUCTURE, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 232 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDH | STRUCTURE / VP | 26231.5 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, high | | |
| ONPOC | VOLUME / VP | 26240.0 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, volume profile | | |
| ONVAL | AUCTION_VALUE / VP | 26231.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, volume profile | | |
| ONTPOC | VOLUME / VP | 26272.5 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, TPO profile | | |
| ONTVAL | AUCTION_VALUE / VP | 26225.0 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, TPO profile | | |
| VWAP | VWAP / VWAP | 26247.0 | inside | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAPU1 | VWAP / VWAP | 26281.75 | 4.25 pts outside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAP_SD1_UP | VWAP / VWAP | 26281.76 | 4.26 pts outside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| HVL_0DTE | GEX / GEX | 26210.0 | 10.00 pts outside | GEX csv: row 2025-10-29, column `hvl_0dte_nt` (= 26210.0); CME report 2025-10-28 (D-1) | | |
| ONPOC_AREA | VOLUME / VP | 26227.5 - 26267.5 | overlaps | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26245.0) | | |

**D_ONVAH_WKTVAH_ONTVAH_WKVAH_ONH**: 26286.75 - 26314.75 (28.00 pts); families 5: AUCTION_VALUE, STRUCTURE, DELTA, GEX, VWAP; long=ANY short=INITIATION; stop 114 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONVAH | AUCTION_VALUE / VP | 26291.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, volume profile | | |
| ONTVAH | AUCTION_VALUE / VP | 26299.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, TPO profile | | |
| ONH | STRUCTURE / VP | 26309.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, high | | |
| VWAPU1 | VWAP / VWAP | 26281.75 | 5.00 pts outside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| WKVAH | AUCTION_VALUE / VP | 26303.25 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_UP | VWAP / VWAP | 26281.76 | 4.99 pts outside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Tue Oct 28 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| CR | GEX / GEX | 26300.0 | inside | GEX csv: row 2025-10-29, column `call_resistance_nt` (= 26300.0); CME report 2025-10-28 (D-1) | | |
| CR_0DTE | GEX / GEX | 26300.0 | inside | GEX csv: row 2025-10-29, column `call_resistance_0dte_nt` (= 26300.0); CME report 2025-10-28 (D-1) | | |
| T_DELTA_BUY_ON | DELTA / VP | 26285.0 - 26295.0 | overlaps | NT VP with delta, ON profile (overnight Tue Oct 28 17:00 - 08:10 CT), 5-pt rows 26285.0-26295.0: BUY delta, each row in the top 20% of abs delta | | |

### Weekly double distribution: frozen criteria values (ours: PD rule applied to weekly, weekly-dd-v1.1)

Profile: NT VP over the developing week Sun Oct 26 17:00 - 10-29 08:10 CT (last trade used 2025-10-29T08:09:58), volume, 5-point rows (NT VP set to 20 ticks per row; row lo = a multiple of 5.00; a row holds lo to lo + 4.75). TPO rows: the same 5-point rows, 30-minute periods (period = floor(minutes since 2000-01-01 CT / 30)).

| criterion (frozen) | value | hand | match |
|---|---|---|---|
| rows in the profile | 122 (25700.0 - 26305.0) | | |
| smoothing | smoothed row = (row below + row + row above) / 3 | | |
| peak smoothed row | 26040.0: 19,107 | | |
| HVN line: smoothed >= 70% of peak | 13,375 | | |
| LVN line: smoothed <= 30% of peak, only between the first and last HVN row | 5,732 | | |
| single prints: runs of >= 2 TPO rows touched by exactly 1 period | 0 run(s) | | |
| split = the first neighbouring HVN pair (low to high) whose gap a separator touches; LVNs before single prints | lower HVN 25925.0 - 25934.75; LVN 25950.0 - 25954.75; upper HVN 25965.0 - 25974.75 | | |

All HVN blocks (runs of rows at or above the HVN line):

| # | block | rows | highest smoothed (% of peak) | used in the split | hand | match |
|---|---|---|---|---|---|---|
| 1 | 25830.0 - 25844.75 | 3 | 17,154 (90%) |  | | |
| 2 | 25895.0 - 25909.75 | 3 | 16,935 (89%) |  | | |
| 3 | 25925.0 - 25934.75 | 2 | 15,695 (82%) | lower | | |
| 4 | 25965.0 - 25974.75 | 2 | 17,190 (90%) | upper | | |
| 5 | 26035.0 - 26059.75 | 5 | 19,107 (100%) |  | | |
| 6 | 26065.0 - 26074.75 | 2 | 14,270 (75%) |  | | |
| 7 | 26175.0 - 26189.75 | 3 | 16,447 (86%) |  | | |

Low-volume separators (LVN runs) and single-print runs:

| type | rows | lies in the gap of HVN pair | used | hand | match |
|---|---|---|---|---|---|
| LVN | 25950.0 - 25954.75 | 3 / 4 | Y | | |
| LVN | 25985.0 - 26009.75 | 4 / 5 |  | | |
| LVN | 26085.0 - 26114.75 | 6 / 7 |  | | |

Row table: the gap between the two split blocks (2 rows either side) and the outer edges of both blocks. HVN line 13,375, LVN line 5,732.

| row lo | volume | smoothed | % of peak | TPO periods | flags | hand | match |
|---|---|---|---|---|---|---|---|
| 25920.0 | 8,976 | 11,157 | 58% | 5 |  | | |
| 25925.0 | 21,750 | 14,883 | 78% | 5 | HVN | | |
| 25930.0 | 13,923 | 15,695 | 82% | 4 | HVN | | |
| 25935.0 | 11,412 | 11,045 | 58% | 4 |  | | |
| 25940.0 | 7,801 | 8,432 | 44% | 4 |  | | |
| 25945.0 | 6,083 | 6,441 | 34% | 6 |  | | |
| 25950.0 | 5,438 | 5,366 | 28% | 7 | LVN, separator | | |
| 25955.0 | 4,576 | 7,989 | 42% | 10 |  | | |
| 25960.0 | 13,952 | 11,804 | 62% | 15 |  | | |
| 25965.0 | 16,883 | 17,190 | 90% | 18 | HVN | | |
| 25970.0 | 20,734 | 16,392 | 86% | 20 | HVN | | |
| 25975.0 | 11,559 | 12,504 | 65% | 19 |  | | |
| 25980.0 | 5,219 | 7,212 | 38% | 16 |  | | |

## 2025-10-31 (Fri)

Plan plan-v2.4-book1a-v1.6; market_context BULLISH; review APPROVED; 5 decision zones.

### 08:10 values

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 26198.75 | close of the bar stamped 08:10 on a 1-minute chart | | |
| session vwap | 26192.27 | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_up | 26222.15 | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_dn | 26162.38 | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly vwap | 26084.24 | the VWAP line: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_up | 26230.44 | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_dn | 25938.04 | the -1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| market_context | BULLISH | the inputs in the context evidence below (sidecar `plan` line `market_context=`) | | |
| context_base | NONE_NO_EVIDENCE | the inputs in the context evidence below (sidecar `plan` line `context_base=`) | | |
| htf_acceptance | ABOVE | the inputs in the context evidence below (sidecar `plan` line `htf_acceptance=`) | | |
| draw_status | ACTIVE | the inputs in the context evidence below (sidecar `plan` line `draw_status=`) | | |
| draw | 26252.50-26292.50|WKPOC_AREA | the inputs in the context evidence below (sidecar `plan` line `draw=`) | | |
| value_follows | DIVERGENT_UP | the inputs in the context evidence below (sidecar `plan` line `value_follows=`) | | |
| on_inventory | NET_LONG | the inputs in the context evidence below (sidecar `plan` line `on_inventory=`) | | |
| on_vs_settle | 316.0 | the inputs in the context evidence below (sidecar `plan` line `on_vs_settle=`) | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | POS | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| htfval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `htfval_state=` | | |
| htfvah_state | accept=ABOVE|failed_reclaim=0 | sidecar `plan` line `htfvah_state=` | | |
| weekly double distribution | AVAILABLE; split no | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |

### Context evidence: the inputs behind each label (check the inputs on the chart, not the label)

**market_context = BULLISH** (context_base = NONE_NO_EVIDENCE, htf_acceptance = ABOVE). Step 1, context_base (plan_fields.context_base): BULLISH = price >= HTF VAL, the low of the bars window <= HTF VAL (held or reclaimed it) and the weekly VAL state is not ACCEPTED_BELOW; BEARISH = the mirror at HTF VAH (state not ACCEPTED_ABOVE); exactly one of them = that label; else BALANCED if the balance composite overlaps; else NONE_CONFLICT if a directional read passed but the weekly acceptance blocked it (or both reads passed), else NONE_NO_EVIDENCE. Step 2, the Nov 5 precedence with htf_acceptance (below).

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| price at 08:10 | 26198.75 | close of the bar stamped 08:10 (1-minute chart) | | |
| HTF VAL | 23645.0 | NT VP over the HTF composite: 60 days from 2025-08-07 through 2025-10-31 08:10 CT (map source MINUTE_APPROX) | | |
| HTF VAH | 25394.75 | same HTF composite profile | | |
| HTF POC | 24827.5 | same HTF composite profile | | |
| low of the bars window | 24804.75 | 1-minute bars 2025-10-19 17:00 - 2025-10-31 08:10 CT: lowest low | | |
| high of the bars window | 26399.0 | 1-minute bars 2025-10-19 17:00 - 2025-10-31 08:10 CT: highest high | | |
| held or reclaimed HTF VAL (price >= 23645.0 and low <= 23645.0) | N | from the rows above | | |
| failed or lost HTF VAH (price <= 25394.75 and high >= 25394.75) | N | from the rows above | | |
| weekly VAL / VAH | 25957.25 / 26270.5 | NT VP over the developing week Sun Oct 26 17:00 - 10-31 08:10 CT | | |
| weekly VAL state / VAH state | INSIDE / INSIDE | PO-9 acceptance on 1-minute closes vs the weekly VAL / VAH: INSIDE = price at 08:10 inside the weekly value (or on the inside of that edge); TESTING = price beyond the edge, not yet accepted; ACCEPTED_* = the minutes since the first close beyond it, the share of closes beyond and the share of volume beyond meet the frozen PO-9 thresholds (>= 60 minutes, >= 80% of closes, >= 20% of volume) (details in the plan lines `wkval_state=` / `wkvah_state=`) | | |
| balance composite overlaps | N | see balance below | | |
| context_base | NONE_NO_EVIDENCE | from the rows above | | |

**htf_acceptance = ABOVE.** Rule (Context doc, Nov 5, 2026; ours: acceptance outside composite value as context evidence, informed by Jeron Part 1, 00:34:58): the PO-9 acceptance definition, unchanged, at the HTF composite VAH and VAL: price at 08:10 beyond the edge, >= 60 minutes since the first 1-minute close beyond it (the first close of the current run of closes beyond, scanning back from 08:10), >= 80% of the closes since then beyond it, >= 20% of the volume since that close beyond it; bars closed at or before 08:10 CT only (the bar stamped 08:10 = trades 08:09:00-08:09:59.999 is the last one). ACCEPTED_ABOVE at the VAH = ABOVE, ACCEPTED_BELOW at the VAL = BELOW, else NONE. Context evidence only, never an entry signal. Precedence: BULLISH + ABOVE = BULLISH; BEARISH + BELOW = BEARISH; BULLISH + BELOW or BEARISH + ABOVE = NONE (conflict); BALANCED stays BALANCED whatever the acceptance; NONE_NO_EVIDENCE + ABOVE = BULLISH, + BELOW = BEARISH; NONE_CONFLICT stays NONE; no acceptance (NONE) = the existing label kept; then the weekly guard on every BULLISH (not ACCEPTED_BELOW the weekly VAL) and every BEARISH (not ACCEPTED_ABOVE the weekly VAH): failure = NONE_CONFLICT -> NONE (clarified Nov 5, 2026).

| edge | level | state | first 1-minute close beyond (CT, close) | minutes since | closes beyond | volume beyond | window (CT) | hand | match |
|---|---|---|---|---|---|---|---|---|---|
| HTFVAL (below) | 23645.0 | INSIDE | none (price at 08:10 not below the edge) |  |  |  | 1-minute bars 2025-10-19 17:00 - 2025-10-31 08:10 CT; level from the HTF composite: 60 days from 2025-08-07 through 2025-10-31 08:10 CT (map source MINUTE_APPROX) | | |
| HTFVAH (above) | 25394.75 | ACCEPTED_ABOVE | 2025-10-24 07:31 (25505.5) | 10119 (need >= 60) | 100.0% (need >= 80%) | 100.0% (need >= 20%) | 1-minute bars 2025-10-19 17:00 - 2025-10-31 08:10 CT; level from the HTF composite: 60 days from 2025-08-07 through 2025-10-31 08:10 CT (map source MINUTE_APPROX) | | |

**Precedence result:** context_base NONE_NO_EVIDENCE + htf_acceptance ABOVE -> BULLISH; weekly guard PASS (weekly VAL INSIDE, weekly VAH INSIDE) = market_context **BULLISH** (context_source HTF_ACCEPTANCE).

**Context invalidation edge: below 25394.75.** Acceptance-based context: it invalidates at the composite edge it is accepted beyond (Bullish: 3 closes below the composite VAH; Bearish: 3 closes above the composite VAL). The plan writes it 2 ticks beyond the edge (`invalidate_below=` / `invalidate_above=`); S1.4 switches the context to Balanced after 3 consecutive 1-minute closes beyond that line (AcceptBars = 3, the strategy's acceptance rule). Context invalidation only, never a trade stop.

**balance = none.** Rule (map BalanceJson): PD and ON value areas must overlap; PD2 joins if PD2 and PD overlap; the members are merged into one volume profile and its 70% value area is the balance. Overlap % = overlap / the narrower value area.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD2 VAH / POC / VAL | 26303.75 / 26275 / 26210 | NT VP over Wed Oct 29 cash 08:30-15:00 CT | | |
| PD VAH / POC / VAL | 26090 / 25970.75 / 25967.5 | NT VP over Thu Oct 30 cash 08:30-15:00 CT | | |
| ON VAH / POC / VAL | 26217.25 / 26190 / 26158.5 | NT VP over the overnight Thu Oct 30 17:00 - 10-31 08:10 CT | | |
| overlap PD2-PD | 0% | from the PD2 and PD value areas | | |
| overlap PD-ON | 0% | from the PD and ON value areas | | |
| members | none | | | |

**value_follows = DIVERGENT_UP.** Rule (plan_fields.value_follows): DIVERGENT_UP = PD high > PD2 high AND PD VAH < PD2 VAH AND PD POC < PD2 POC; DIVERGENT_DOWN = PD low < PD2 low AND PD VAL > PD2 VAL AND PD POC > PD2 POC; else WITH_PRICE. Highs and lows are the full trading day; value areas are the cash session.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD high / low | 26399 / 25853 | Thu Oct 30 full trading day (Wed Oct 29 17:00 - Thu Oct 30 16:00 CT): high / low | | |
| PD2 high / low | 26379.75 / 26049.25 | Wed Oct 29 full trading day (Tue Oct 28 17:00 - Wed Oct 29 16:00 CT): high / low | | |
| PD VAH / VAL / POC | 26090 / 25967.5 / 25970.75 | NT VP over Thu Oct 30 cash 08:30-15:00 CT | | |
| PD2 VAH / VAL / POC | 26303.75 / 26210 / 26275 | NT VP over Wed Oct 29 cash 08:30-15:00 CT | | |
| DIVERGENT_UP tests: higher high / lower VAH / lower POC | Y / Y / Y | from the rows above | | |
| DIVERGENT_DOWN tests: lower low / higher VAL / higher POC | Y / N / N | from the rows above | | |

**on_inventory = NET_LONG, on_vs_settle = 316.0.** Rule (plan_fields.on_inventory): NET_LONG if price at 08:10 > the ON VWAP, NET_SHORT if below; on_vs_settle = price - the PD settlement. The overnight high / low vs the settlement are shown for reference; the rule does not use them.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| ON VWAP | 26192.27 | session VWAP: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| price at 08:10 | 26198.75 | close of the bar stamped 08:10 | | |
| PD settlement | 25882.75 | Thu Oct 30: volume-weighted price of the trades in the 30 s before 15:00 CT (map SettleOf); CME's settlement can differ by a tick | | |
| on_vs_settle (price - settlement) | 316.0 | from the rows above | | |
| ON high / ON low | 26274 / 26127.25 | overnight Thu Oct 30 17:00 - 10-31 08:10 CT: high / low | | |
| ON high - settlement / ON low - settlement (reference) | 391.25 / 244.50 | from the rows above | | |

**draw_status = ACTIVE.** Rule (plan_v24): the draw is the nearest candidate in the context direction: BULLISH = HTF POC / HTF VAH above price, MAP4 POC areas above price, GEX levels above price; BEARISH = the mirror below price. NONE = no draw candidate exists (Context spec, Kyron Nov 4); it is never treated as ACTIVE: no draw= line is written and the ladder gets no draw.

| candidate | level (with pad) | distance pts | check in | hand | match |
|---|---|---|---|---|---|
| WKPOC_AREA | 26252.5 - 26292.5 | 53.75 | see the level's source | | |
### GEX values (source: GEX csv)

| level | value in plan | check against | hand | match |
|---|---|---|---|---|
| CR | 26000.00 | GEX csv: row 2025-10-31, column `call_resistance_nt` (= 26000.0); CME report 2025-10-30 (D-1) | | |
| PS | 24800.00 | GEX csv: row 2025-10-31, column `put_support_nt` (= 24800.0); CME report 2025-10-30 (D-1) | | |
| HVL | 25275.00 | GEX csv: row 2025-10-31, column `hvl_nt` (= 25275.0); CME report 2025-10-30 (D-1) | | |
| CR_0DTE | 26150.00 | GEX csv: row 2025-10-31, column `call_resistance_0dte_nt` (= 26150.0); CME report 2025-10-30 (D-1) | | |
| PS_0DTE | 25775.00 | GEX csv: row 2025-10-31, column `put_support_0dte_nt` (= 25775.0); CME report 2025-10-30 (D-1) | | |
| HVL_0DTE | 25390.00 | GEX csv: row 2025-10-31, column `hvl_0dte_nt` (= 25390.0); CME report 2025-10-30 (D-1) | | |
| regime | positive | GEX csv: row 2025-10-31, column `regime` | | |

### Decision zones: every level behind each zone

**D_WKVAL_PDVAL_PDPOC_WKPOC_PDTVAL**: 25952.25 - 25980.0 (27.75 pts); families 3: AUCTION_VALUE, DELTA, VOLUME; long=ANY short=INITIATION; stop 113 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDPOC | VOLUME / VP | 25970.75 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, volume profile | | |
| PDVAL | AUCTION_VALUE / VP | 25967.5 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, volume profile | | |
| WKPOC | VOLUME / VP | 25970.75 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| WKVAL | AUCTION_VALUE / VP | 25957.25 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| T_DELTA_SELL_PD | DELTA / VP | 25945.0 - 25955.0 | overlaps; 3 delta bands share this label | NT VP with delta, PD profile (Thu Oct 30 cash 08:30-15:00 CT), 5-pt rows 25945.0-25955.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 25975.0 - 25985.0 | overlaps; 3 delta bands share this label | NT VP with delta, PD profile (Thu Oct 30 cash 08:30-15:00 CT), 5-pt rows 25975.0-25985.0: SELL delta, each row in the top 20% of abs delta | | |

**D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ**: 25995.0 - 26099.75 (104.75 pts); families 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 421 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDVAH | AUCTION_VALUE / VP | 26090.0 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, volume profile | | |
| PDTPOC | VOLUME / VP | 26037.5 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, TPO profile | | |
| PD2L | STRUCTURE / VP | 26049.25 | inside | NT VP, Wed Oct 29 cash 08:30-15:00 CT, low | | |
| PD3L | STRUCTURE / VP | 26006.0 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, low | | |
| WKVWAP | VWAP / VWAP | 26084.24 | inside | the VWAP line: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| CR | GEX / GEX | 26000.0 | inside | GEX csv: row 2025-10-31, column `call_resistance_nt` (= 26000.0); CME report 2025-10-30 (D-1) | | |
| T_DELTA_BUY_WK | DELTA / VP | 26070.0 - 26080.0 | overlaps; 3 delta bands share this label | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26070.0-26080.0: BUY delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 26040.0 - 26050.0 | overlaps; 3 delta bands share this label | NT VP with delta, PD profile (Thu Oct 30 cash 08:30-15:00 CT), 5-pt rows 26040.0-26050.0: SELL delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | VOLUME / VP | 26040.0 - 26070.0 | overlaps | NT VP, Thu Oct 30 cash 08:30-15:00 CT, 5-pt rows >= 70% of the peak row (26060.0) | | |

**REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC**: 26142.5 - 26236.5 (94.00 pts); families 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 378 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDH | STRUCTURE / VP | 26182.5 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, high | | |
| PD3H | STRUCTURE / VP | 26231.5 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, high | | |
| ONVAH | AUCTION_VALUE / VP | 26217.25 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, volume profile | | |
| ONPOC | VOLUME / VP | 26190.0 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, volume profile | | |
| ONVAL | AUCTION_VALUE / VP | 26158.5 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, volume profile | | |
| ONTVAH | AUCTION_VALUE / VP | 26209.75 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, TPO profile | | |
| ONTPOC | VOLUME / VP | 26192.5 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, TPO profile | | |
| ONTVAL | AUCTION_VALUE / VP | 26155.0 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, TPO profile | | |
| VWAP | VWAP / VWAP | 26192.25 | inside | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAPU1 | VWAP / VWAP | 26222.25 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAPL1 | VWAP / VWAP | 26162.5 | inside | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAP_SD1_UP | VWAP / VWAP | 26222.15 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| VWAP_SD1_DN | VWAP / VWAP | 26162.38 | inside | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Thu Oct 30 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| WKVWAP_SD1_UP | VWAP / VWAP | 26230.44 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Oct 26 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| CR_0DTE | GEX / GEX | 26150.0 | inside | GEX csv: row 2025-10-31, column `call_resistance_0dte_nt` (= 26150.0); CME report 2025-10-30 (D-1) | | |
| T_DELTA_SELL_WK | DELTA / VP | 26230.0 - 26240.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26230.0-26240.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_ON | DELTA / VP | 26200.0 - 26215.0 | overlaps | NT VP with delta, ON profile (overnight Thu Oct 30 17:00 - 08:10 CT), 5-pt rows 26200.0-26215.0: BUY delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | VOLUME / VP | 26175.0 - 26200.0 | overlaps | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26190.0) | | |
| REJ_HIGH_PD | STRUCTURE / chart | 26142.5 - 26182.5 | overlaps | 1-minute chart: swing bar close Thu Oct 30 09:01, swing 26182.5; available Thu Oct 30 09:16 (pack section B) | | |

**T_PD2TPOC**: 26237.5 - 26247.5 (10.00 pts); families 2: DELTA, VOLUME; long=ANY short=INITIATION; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| T_DELTA_SELL_WK | DELTA / VP | 26230.0 - 26240.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26230.0-26240.0: SELL delta, each row in the top 20% of abs delta | | |
| WKPOC_AREA | VOLUME / VP | 26252.5 - 26292.5 | within 5.00 pts (above the zone; counts by the 5-pt family tolerance) | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26270.0) | | |

**WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK**: 26252.5 - 26306.5 (54.00 pts); families 4: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME; long=NONE short=NONE; stop 218 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONH | STRUCTURE / VP | 26274.0 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, high | | |
| WKVAH | AUCTION_VALUE / VP | 26270.5 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| T_DELTA_BUY_WK | DELTA / VP | 26275.0 - 26290.0 | overlaps; 3 delta bands share this label | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26275.0-26290.0: BUY delta, each row in the top 20% of abs delta | | |
| WKPOC_AREA | VOLUME / VP | 26252.5 - 26292.5 | overlaps | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26270.0) | | |
| REJ_HIGH_WK | STRUCTURE / chart | 26266.5 - 26306.5 | overlaps | 1-minute chart: swing bar close Wed Oct 29 23:38, swing 26306.5; available Wed Oct 29 23:53 (pack section B) | | |

## 2025-11-18 (Tue)

Plan plan-v2.4-book1a-v1.6; market_context NONE; review APPROVED; 5 decision zones.

### 08:10 values

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 24746.5 | close of the bar stamped 08:10 on a 1-minute chart | | |
| session vwap | 24774.35 | the VWAP line: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Mon Nov 17 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_up | 24856.07 | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Mon Nov 17 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| session sd1_dn | 24692.64 | the -1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Mon Nov 17 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly vwap | 24989.77 | the VWAP line: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Nov 16 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_up | 25163.00 | the +1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Nov 16 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| weekly sd1_dn | 24816.55 | the -1 sigma band: NT VWAP (Order Flow VWAP), weekly, anchored at Sunday 17:00 CT (Sun Nov 16 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| market_context | NONE | the inputs in the context evidence below (sidecar `plan` line `market_context=`) | | |
| context_base | NONE_NO_EVIDENCE | the inputs in the context evidence below (sidecar `plan` line `context_base=`) | | |
| htf_acceptance | NONE | the inputs in the context evidence below (sidecar `plan` line `htf_acceptance=`) | | |
| draw_status | NONE | the inputs in the context evidence below (sidecar `plan` line `draw_status=`) | | |
| value_follows | WITH_PRICE | the inputs in the context evidence below (sidecar `plan` line `value_follows=`) | | |
| on_inventory | NET_SHORT | the inputs in the context evidence below (sidecar `plan` line `on_inventory=`) | | |
| on_vs_settle | -132.5 | the inputs in the context evidence below (sidecar `plan` line `on_vs_settle=`) | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | NEG | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=BELOW|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| htfval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `htfval_state=` | | |
| htfvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `htfvah_state=` | | |
| weekly double distribution | AVAILABLE; split yes | the criteria table below (ours: PD rule applied to weekly) | | |

### Context evidence: the inputs behind each label (check the inputs on the chart, not the label)

**market_context = NONE** (context_base = NONE_NO_EVIDENCE, htf_acceptance = NONE). Step 1, context_base (plan_fields.context_base): BULLISH = price >= HTF VAL, the low of the bars window <= HTF VAL (held or reclaimed it) and the weekly VAL state is not ACCEPTED_BELOW; BEARISH = the mirror at HTF VAH (state not ACCEPTED_ABOVE); exactly one of them = that label; else BALANCED if the balance composite overlaps; else NONE_CONFLICT if a directional read passed but the weekly acceptance blocked it (or both reads passed), else NONE_NO_EVIDENCE. Step 2, the Nov 5 precedence with htf_acceptance (below).

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| price at 08:10 | 24746.5 | close of the bar stamped 08:10 (1-minute chart) | | |
| HTF VAL | 24430.0 | NT VP over the HTF composite: 60 days from 2025-08-25 through 2025-11-18 08:10 CT (map source MINUTE_APPROX) | | |
| HTF VAH | 25954.75 | same HTF composite profile | | |
| HTF POC | 24827.5 | same HTF composite profile | | |
| low of the bars window | 24603.75 | 1-minute bars 2025-11-09 17:00 - 2025-11-18 08:10 CT: lowest low | | |
| high of the bars window | 25830.0 | 1-minute bars 2025-11-09 17:00 - 2025-11-18 08:10 CT: highest high | | |
| held or reclaimed HTF VAL (price >= 24430.0 and low <= 24430.0) | N | from the rows above | | |
| failed or lost HTF VAH (price <= 25954.75 and high >= 25954.75) | N | from the rows above | | |
| weekly VAL / VAH | 24856.0 / 25285.25 | NT VP over the developing week Sun Nov 16 17:00 - 11-18 08:10 CT | | |
| weekly VAL state / VAH state | ACCEPTED_BELOW / INSIDE | PO-9 acceptance on 1-minute closes vs the weekly VAL / VAH: INSIDE = price at 08:10 inside the weekly value (or on the inside of that edge); TESTING = price beyond the edge, not yet accepted; ACCEPTED_* = the minutes since the first close beyond it, the share of closes beyond and the share of volume beyond meet the frozen PO-9 thresholds (>= 60 minutes, >= 80% of closes, >= 20% of volume) (details in the plan lines `wkval_state=` / `wkvah_state=`) | | |
| balance composite overlaps | N | see balance below | | |
| context_base | NONE_NO_EVIDENCE | from the rows above | | |

**htf_acceptance = NONE.** Rule (Context doc, Nov 5, 2026; ours: acceptance outside composite value as context evidence, informed by Jeron Part 1, 00:34:58): the PO-9 acceptance definition, unchanged, at the HTF composite VAH and VAL: price at 08:10 beyond the edge, >= 60 minutes since the first 1-minute close beyond it (the first close of the current run of closes beyond, scanning back from 08:10), >= 80% of the closes since then beyond it, >= 20% of the volume since that close beyond it; bars closed at or before 08:10 CT only (the bar stamped 08:10 = trades 08:09:00-08:09:59.999 is the last one). ACCEPTED_ABOVE at the VAH = ABOVE, ACCEPTED_BELOW at the VAL = BELOW, else NONE. Context evidence only, never an entry signal. Precedence: BULLISH + ABOVE = BULLISH; BEARISH + BELOW = BEARISH; BULLISH + BELOW or BEARISH + ABOVE = NONE (conflict); BALANCED stays BALANCED whatever the acceptance; NONE_NO_EVIDENCE + ABOVE = BULLISH, + BELOW = BEARISH; NONE_CONFLICT stays NONE; no acceptance (NONE) = the existing label kept; then the weekly guard on every BULLISH (not ACCEPTED_BELOW the weekly VAL) and every BEARISH (not ACCEPTED_ABOVE the weekly VAH): failure = NONE_CONFLICT -> NONE (clarified Nov 5, 2026).

| edge | level | state | first 1-minute close beyond (CT, close) | minutes since | closes beyond | volume beyond | window (CT) | hand | match |
|---|---|---|---|---|---|---|---|---|---|
| HTFVAL (below) | 24430.0 | INSIDE | none (price at 08:10 not below the edge) |  |  |  | 1-minute bars 2025-11-09 17:00 - 2025-11-18 08:10 CT; level from the HTF composite: 60 days from 2025-08-25 through 2025-11-18 08:10 CT (map source MINUTE_APPROX) | | |
| HTFVAH (above) | 25954.75 | INSIDE | none (price at 08:10 not above the edge) |  |  |  | 1-minute bars 2025-11-09 17:00 - 2025-11-18 08:10 CT; level from the HTF composite: 60 days from 2025-08-25 through 2025-11-18 08:10 CT (map source MINUTE_APPROX) | | |

**Precedence result:** context_base NONE_NO_EVIDENCE + htf_acceptance NONE -> NONE_NO_EVIDENCE; weekly guard N/A (weekly VAL ACCEPTED_BELOW, weekly VAH INSIDE) = market_context **NONE** (context_source NONE).

**Context invalidation edge: none.** No directional context, so no invalidation line. The plan writes it 2 ticks beyond the edge (`invalidate_below=` / `invalidate_above=`); S1.4 switches the context to Balanced after 3 consecutive 1-minute closes beyond that line (AcceptBars = 3, the strategy's acceptance rule). Context invalidation only, never a trade stop.

**balance = none.** Rule (map BalanceJson): PD and ON value areas must overlap; PD2 joins if PD2 and PD overlap; the members are merged into one volume profile and its 70% value area is the balance. Overlap % = overlap / the narrower value area.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD2 VAH / POC / VAL | 25289 / 25150 / 24978.5 | NT VP over Fri Nov 14 cash 08:30-15:00 CT | | |
| PD VAH / POC / VAL | 25253.5 / 25150 / 24932.25 | NT VP over Mon Nov 17 cash 08:30-15:00 CT | | |
| ON VAH / POC / VAL | 24851.25 / 24750 / 24680.5 | NT VP over the overnight Mon Nov 17 17:00 - 11-18 08:10 CT | | |
| overlap PD2-PD | 88.6% | from the PD2 and PD value areas | | |
| overlap PD-ON | 0% | from the PD and ON value areas | | |
| members | none | | | |

**value_follows = WITH_PRICE.** Rule (plan_fields.value_follows): DIVERGENT_UP = PD high > PD2 high AND PD VAH < PD2 VAH AND PD POC < PD2 POC; DIVERGENT_DOWN = PD low < PD2 low AND PD VAL > PD2 VAL AND PD POC > PD2 POC; else WITH_PRICE. Highs and lows are the full trading day; value areas are the cash session.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| PD high / low | 25361.25 / 24731.75 | Mon Nov 17 full trading day (Sun Nov 16 17:00 - Mon Nov 17 16:00 CT): high / low | | |
| PD2 high / low | 25293.25 / 24626 | Fri Nov 14 full trading day (Thu Nov 13 17:00 - Fri Nov 14 16:00 CT): high / low | | |
| PD VAH / VAL / POC | 25253.5 / 24932.25 / 25150 | NT VP over Mon Nov 17 cash 08:30-15:00 CT | | |
| PD2 VAH / VAL / POC | 25289 / 24978.5 / 25150 | NT VP over Fri Nov 14 cash 08:30-15:00 CT | | |
| DIVERGENT_UP tests: higher high / lower VAH / lower POC | Y / Y / N | from the rows above | | |
| DIVERGENT_DOWN tests: lower low / higher VAL / higher POC | N / N / N | from the rows above | | |

**on_inventory = NET_SHORT, on_vs_settle = -132.5.** Rule (plan_fields.on_inventory): NET_LONG if price at 08:10 > the ON VWAP, NET_SHORT if below; on_vs_settle = price - the PD settlement. The overnight high / low vs the settlement are shown for reference; the rule does not use them.

| input | value | check in (chart window) | hand | match |
|---|---|---|---|---|
| ON VWAP | 24774.35 | session VWAP: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Mon Nov 17 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| price at 08:10 | 24746.5 | close of the bar stamped 08:10 | | |
| PD settlement | 24879 | Mon Nov 17: volume-weighted price of the trades in the 30 s before 15:00 CT (map SettleOf); CME's settlement can differ by a tick | | |
| on_vs_settle (price - settlement) | -132.5 | from the rows above | | |
| ON high / ON low | 24959.5 / 24603.75 | overnight Mon Nov 17 17:00 - 11-18 08:10 CT: high / low | | |
| ON high - settlement / ON low - settlement (reference) | 80.50 / -275.25 | from the rows above | | |

**draw_status = NONE.** Rule (plan_v24): the draw is the nearest candidate in the context direction: BULLISH = HTF POC / HTF VAH above price, MAP4 POC areas above price, GEX levels above price; BEARISH = the mirror below price. NONE = no draw candidate exists (Context spec, Kyron Nov 4); it is never treated as ACTIVE: no draw= line is written and the ladder gets no draw.

No candidate: market_context is NONE, so the rule has no direction to look in and no candidate exists. For reference, the HTF levels the rule would scan: HTF POC 24827.5 (above price), HTF VAH 25954.75, HTF VAL 24430.0 (price 24746.5). Check that the context inputs above give NONE; then NONE follows.

### GEX values (source: GEX csv)

| level | value in plan | check against | hand | match |
|---|---|---|---|---|
| CR | 26000.00 | GEX csv: row 2025-11-18, column `call_resistance_nt` (= 26000.0); CME report 2025-11-17 (D-1) | | |
| PS | 24000.00 | GEX csv: row 2025-11-18, column `put_support_nt` (= 24000.0); CME report 2025-11-17 (D-1) | | |
| HVL | 24970.00 | GEX csv: row 2025-11-18, column `hvl_nt` (= 24970.0); CME report 2025-11-17 (D-1) | | |
| CR_0DTE | 25250.00 | GEX csv: row 2025-11-18, column `call_resistance_0dte_nt` (= 25250.0); CME report 2025-11-17 (D-1) | | |
| PS_0DTE | 24600.00 | GEX csv: row 2025-11-18, column `put_support_0dte_nt` (= 24600.0); CME report 2025-11-17 (D-1) | | |
| HVL_0DTE | 24875.00 | GEX csv: row 2025-11-18, column `hvl_0dte_nt` (= 24875.0); CME report 2025-11-17 (D-1) | | |
| regime | negative | GEX csv: row 2025-11-18, column `regime` | | |

### Decision zones: every level behind each zone

**T_ONL**: 24598.75 - 24608.75 (10.00 pts); families 2: STRUCTURE, GEX; long=ANY short=ANY; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONL | STRUCTURE / VP | 24603.75 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, low | | |
| PS_0DTE | GEX / GEX | 24600.0 | inside | GEX csv: row 2025-11-18, column `put_support_0dte_nt` (= 24600.0); CME report 2025-11-17 (D-1) | | |

**T_ONTVAL_ONVAL**: 24665.0 - 24685.5 (20.50 pts); families 2: AUCTION_VALUE, DELTA; long=ANY short=ANY; stop 84 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONVAL | AUCTION_VALUE / VP | 24680.5 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, volume profile | | |
| ONTVAL | AUCTION_VALUE / VP | 24670.0 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, TPO profile | | |
| T_DELTA_BUY_ON | DELTA / VP | 24650.0 - 24660.0 | within 5.00 pts (below the zone; counts by the 5-pt family tolerance) | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24650.0-24660.0: BUY delta, each row in the top 20% of abs delta | | |

**ONPOC_AREA_D_PDL_ONTPOC_ONPOC**: 24715.0 - 24755.0 (40.00 pts); families 3: STRUCTURE, DELTA, VOLUME; long=ANY short=ANY; stop 162 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDL | STRUCTURE / VP | 24731.75 | inside | NT VP, Mon Nov 17 cash 08:30-15:00 CT, low | | |
| ONPOC | VOLUME / VP | 24750.0 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, volume profile | | |
| ONTPOC | VOLUME / VP | 24742.5 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, TPO profile | | |
| T_DELTA_SELL_ON | DELTA / VP | 24700.0 - 24720.0 | overlaps; 2 delta bands share this label | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24700.0-24720.0: SELL delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | VOLUME / VP | 24715.0 - 24755.0 | overlaps | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (24740.0) | | |

**T_HTFPOC**: 24822.5 - 24832.5 (10.00 pts); families 2: DELTA, VOLUME; long=ANY short=ANY; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| HTFPOC | VOLUME / VP | 24827.5 | inside | NT VP over the packet's window (HTF composite (packet htf_composite window)) | | |
| T_DELTA_SELL_WK | DELTA / VP | 24820.0 - 24845.0 | overlaps; 2 delta bands share this label | NT VP with delta, WK profile (developing week Sun Nov 16 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_ON | DELTA / VP | 24820.0 - 24845.0 | overlaps; 2 delta bands share this label | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |

**D_ONVAH_WKVAL_ONTVAH**: 24846.25 - 24864.75 (18.50 pts); families 3: AUCTION_VALUE, DELTA, VWAP; long=INITIATION short=ANY; stop 76 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONVAH | AUCTION_VALUE / VP | 24851.25 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, volume profile | | |
| ONTVAH | AUCTION_VALUE / VP | 24859.75 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, TPO profile | | |
| VWAPU1 | VWAP / VWAP | 24856.0 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Mon Nov 17 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| WKVAL | AUCTION_VALUE / VP | 24856.0 | inside | NT VP, developing week Sun Nov 16 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_UP | VWAP / VWAP | 24856.07 | inside | the +1 sigma band: NT VWAP (Order Flow VWAP), session, reset at 17:00 CT (Mon Nov 17 17:00), ETH (all hours), 1 standard deviation band; read the bar stamped 08:10 on a 1-minute chart (= trades 08:09:00-08:09:59.999; the last bar included) | | |
| T_DELTA_SELL_WK | DELTA / VP | 24820.0 - 24845.0 | within 1.25 pts (below the zone; counts by the 5-pt family tolerance); 2 delta bands share this label | NT VP with delta, WK profile (developing week Sun Nov 16 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_ON | DELTA / VP | 24820.0 - 24845.0 | within 1.25 pts (below the zone; counts by the 5-pt family tolerance); 2 delta bands share this label | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |

### Weekly double distribution: frozen criteria values (ours: PD rule applied to weekly, weekly-dd-v1.1)

Profile: NT VP over the developing week Sun Nov 16 17:00 - 11-18 08:10 CT (last trade used 2025-11-18T08:09:58), volume, 5-point rows (NT VP set to 20 ticks per row; row lo = a multiple of 5.00; a row holds lo to lo + 4.75). TPO rows: the same 5-point rows, 30-minute periods (period = floor(minutes since 2000-01-01 CT / 30)).

| criterion (frozen) | value | hand | match |
|---|---|---|---|
| rows in the profile | 153 (24600.0 - 25360.0) | | |
| smoothing | smoothed row = (row below + row + row above) / 3 | | |
| peak smoothed row | 25140.0: 13,773 | | |
| HVN line: smoothed >= 70% of peak | 9,641 | | |
| LVN line: smoothed <= 30% of peak, only between the first and last HVN row | 4,132 | | |
| single prints: runs of >= 2 TPO rows touched by exactly 1 period | 0 run(s) | | |
| split = the first neighbouring HVN pair (low to high) whose gap a separator touches; LVNs before single prints | lower HVN 24865.0 - 24874.75; LVN 24925.0 - 24954.75; upper HVN 24970.0 - 24989.75 | | |

All HVN blocks (runs of rows at or above the HVN line):

| # | block | rows | highest smoothed (% of peak) | used in the split | hand | match |
|---|---|---|---|---|---|---|
| 1 | 24775.0 - 24804.75 | 6 | 11,801 (86%) |  | | |
| 2 | 24865.0 - 24874.75 | 2 | 10,108 (73%) | lower | | |
| 3 | 24970.0 - 24989.75 | 4 | 10,974 (80%) | upper | | |
| 4 | 25065.0 - 25104.75 | 8 | 11,898 (86%) |  | | |
| 5 | 25125.0 - 25159.75 | 7 | 13,773 (100%) |  | | |

Low-volume separators (LVN runs) and single-print runs:

| type | rows | lies in the gap of HVN pair | used | hand | match |
|---|---|---|---|---|---|
| LVN | 24925.0 - 24954.75 | 2 / 3 | Y | | |

Row table: the gap between the two split blocks (2 rows either side) and the outer edges of both blocks. HVN line 9,641, LVN line 4,132.

| row lo | volume | smoothed | % of peak | TPO periods | flags | hand | match |
|---|---|---|---|---|---|---|---|
| 24860.0 | 9,177 | 8,708 | 63% | 7 |  | | |
| 24865.0 | 11,103 | 10,108 | 73% | 7 | HVN | | |
| 24870.0 | 10,044 | 9,836 | 71% | 7 | HVN | | |
| 24875.0 | 8,362 | 8,761 | 64% | 8 |  | | |
| 24880.0 | 7,877 | 7,641 | 55% | 9 |  | | |
| 24885.0 | 6,684 | 7,206 | 52% | 11 |  | | |
| 24890.0 | 7,057 | 7,394 | 54% | 10 |  | | |
| 24895.0 | 8,442 | 7,565 | 55% | 8 |  | | |
| 24900.0 | 7,197 | 7,261 | 53% | 8 |  | | |
| 24905.0 | 6,145 | 5,958 | 43% | 11 |  | | |
| 24910.0 | 4,531 | 5,127 | 37% | 10 |  | | |
| 24915.0 | 4,704 | 4,323 | 31% | 9 |  | | |
| 24920.0 | 3,733 | 4,215 | 31% | 9 |  | | |
| 24925.0 | 4,207 | 3,927 | 29% | 9 | LVN, separator | | |
| 24930.0 | 3,842 | 3,667 | 27% | 8 | LVN, separator | | |
| 24935.0 | 2,952 | 2,895 | 21% | 7 | LVN, separator | | |
| 24940.0 | 1,891 | 2,288 | 17% | 6 | LVN, separator | | |
| 24945.0 | 2,022 | 2,430 | 18% | 6 | LVN, separator | | |
| 24950.0 | 3,378 | 3,073 | 22% | 7 | LVN, separator | | |
| 24955.0 | 3,818 | 4,313 | 31% | 6 |  | | |
| 24960.0 | 5,744 | 6,406 | 47% | 4 |  | | |
| 24965.0 | 9,655 | 8,874 | 64% | 4 |  | | |
| 24970.0 | 11,224 | 10,385 | 75% | 4 | HVN | | |
| 24975.0 | 10,275 | 10,920 | 79% | 4 | HVN | | |
| 24980.0 | 11,261 | 10,974 | 80% | 4 | HVN | | |
| ... | | | | | | | |
| 24990.0 | 7,290 | 9,048 | 66% | 5 |  | | |
| 24995.0 | 8,467 | 7,277 | 53% | 6 |  | | |

