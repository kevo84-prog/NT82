# P0.7-P0.9 hand-check sheet: Oct 22, 29, 31 and Nov 18, 2025 (hand-check-sheet-v1.0)

Check each value against the source named on its row, not against the plan. Sources: **NT VP** = the NinjaTrader Volume Profile tool drawn over the stated window (CT); **GEX csv** = `gex_levels_block1.csv`, row session = the day, the named column; **sidecar** = the frozen plan sidecar `PreopenPlan_<day>_book1a.json`, the named key. Every value is frozen at 08:10 CT from data before 08:10 CT. No trades, outcomes or P&L.

## 2025-10-22 (Wed)

Plan plan-v2.4-book1a-v1.3; market_context BALANCED; review APPROVED; 3 decision zones.

### 08:10 values (source: sidecar)

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 25258.75 | the 08:10 bar close on the chart; sidecar has it in the zone sides | | |
| session vwap | 25267.38 | sidecar `vwap.SESSION.vwap` (window 2025-10-21T17:00 - 08:10) | | |
| session sd1_up | 25296.63 | sidecar `vwap.SESSION.sd1_up` (window 2025-10-21T17:00 - 08:10) | | |
| session sd1_dn | 25238.13 | sidecar `vwap.SESSION.sd1_dn` (window 2025-10-21T17:00 - 08:10) | | |
| weekly vwap | 25262.44 | sidecar `vwap.WEEKLY.vwap` (window 2025-10-19T17:00 - 08:10) | | |
| weekly sd1_up | 25337.16 | sidecar `vwap.WEEKLY.sd1_up` (window 2025-10-19T17:00 - 08:10) | | |
| weekly sd1_dn | 25187.72 | sidecar `vwap.WEEKLY.sd1_dn` (window 2025-10-19T17:00 - 08:10) | | |
| market_context | BALANCED | sidecar `plan` line `market_context=` | | |
| draw_status | NONE | sidecar `plan` line `draw_status=` | | |
| balance | 25256-25340.5 | sidecar `plan` line `balance=` | | |
| balance_poc | 25318 | sidecar `plan` line `balance_poc=` | | |
| value_follows | DIVERGENT_UP | sidecar `plan` line `value_follows=` | | |
| on_inventory | NET_SHORT | sidecar `plan` line `on_inventory=` | | |
| on_vs_settle | -36.0 | sidecar `plan` line `on_vs_settle=` | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | POS | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| weekly double distribution | AVAILABLE; split no | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |

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
| VWAP | VWAP / 08:10 | 25267.5 | 2.50 pts outside | sidecar `vwap.SESSION.vwap` (= 25267.38; window 2025-10-21T17:00 - 08:10) | | |
| VWAPL1 | VWAP / 08:10 | 25238.25 | inside | sidecar `vwap.SESSION.sd1_dn` (= 25238.13; window 2025-10-21T17:00 - 08:10) | | |
| WKVAL | AUCTION_VALUE / VP | 25244.25 | inside | NT VP, developing week Sun Oct 19 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_DN | VWAP / 08:10 | 25238.13 | inside | sidecar `vwap.SESSION.sd1_dn` (= 25238.13; window 2025-10-21T17:00 - 08:10) | | |
| WKVWAP | VWAP / 08:10 | 25262.44 | inside | sidecar `vwap.WEEKLY.vwap` (= 25262.44; window 2025-10-19T17:00 - 08:10) | | |
| HVL | GEX / GEX | 25230.0 | inside | GEX csv: row 2025-10-22, column `hvl_nt` (= 25230.0); CME report 2025-10-21 (D-1) | | |
| HVL_0DTE | GEX / GEX | 25260.0 | inside | GEX csv: row 2025-10-22, column `hvl_0dte_nt` (= 25260.0); CME report 2025-10-21 (D-1) | | |
| T_DELTA_SELL_WK | DELTA / VP | 25295.0 - 25315.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 19 17:00 - 08:10 CT), 5-pt rows 25295.0-25315.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 25270.0 - 25280.0 | overlaps | NT VP with delta, PD profile (Tue Oct 21 cash 08:30-15:00 CT), 5-pt rows 25270.0-25280.0: SELL delta, each row in the top 20% of abs delta | | |
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
| WKVWAP_SD1_UP | VWAP / 08:10 | 25337.16 | inside | sidecar `vwap.WEEKLY.sd1_up` (= 25337.16; window 2025-10-19T17:00 - 08:10) | | |
| T_DELTA_BUY_WK | DELTA / VP | 25315.0 - 25355.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 19 17:00 - 08:10 CT), 5-pt rows 25315.0-25355.0: BUY delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | VOLUME / VP | 25292.5 - 25332.5 | overlaps | NT VP, Tue Oct 21 cash 08:30-15:00 CT, 5-pt rows >= 70% of the peak row (25310.0) | | |

**T_HTFVAH**: 25389.75 - 25399.75 (10.00 pts); families 2: AUCTION_VALUE, GEX; long=ANY short=ANY; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| HTFVAH | AUCTION_VALUE / VP | 25394.75 | inside | NT VP over the packet's window (HTF composite (packet htf_composite window)) | | |
| CR | GEX / GEX | 25400.0 | 0.25 pts outside | GEX csv: row 2025-10-22, column `call_resistance_nt` (= 25400.0); CME report 2025-10-21 (D-1) | | |
| CR_0DTE | GEX / GEX | 25400.0 | 0.25 pts outside | GEX csv: row 2025-10-22, column `call_resistance_0dte_nt` (= 25400.0); CME report 2025-10-21 (D-1) | | |

## 2025-10-29 (Wed)

Plan plan-v2.4-book1a-v1.3; market_context NONE; review APPROVED; 4 decision zones.

### 08:10 values (source: sidecar)

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 26271 | the 08:10 bar close on the chart; sidecar has it in the zone sides | | |
| session vwap | 26247.05 | sidecar `vwap.SESSION.vwap` (window 2025-10-28T17:00 - 08:10) | | |
| session sd1_up | 26281.76 | sidecar `vwap.SESSION.sd1_up` (window 2025-10-28T17:00 - 08:10) | | |
| session sd1_dn | 26212.34 | sidecar `vwap.SESSION.sd1_dn` (window 2025-10-28T17:00 - 08:10) | | |
| weekly vwap | 26007.58 | sidecar `vwap.WEEKLY.vwap` (window 2025-10-26T17:00 - 08:10) | | |
| weekly sd1_up | 26151.07 | sidecar `vwap.WEEKLY.sd1_up` (window 2025-10-26T17:00 - 08:10) | | |
| weekly sd1_dn | 25864.08 | sidecar `vwap.WEEKLY.sd1_dn` (window 2025-10-26T17:00 - 08:10) | | |
| market_context | NONE | sidecar `plan` line `market_context=` | | |
| draw_status | NONE | sidecar `plan` line `draw_status=` | | |
| value_follows | WITH_PRICE | sidecar `plan` line `value_follows=` | | |
| on_inventory | NET_LONG | sidecar `plan` line `on_inventory=` | | |
| on_vs_settle | 107.5 | sidecar `plan` line `on_vs_settle=` | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | POS | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| weekly double distribution | AVAILABLE; split yes | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |

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
| T_DELTA_BUY_WK | DELTA / VP | 26045.0 - 26055.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26045.0-26055.0: BUY delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 26030.0 - 26040.0 | overlaps | NT VP with delta, PD profile (Tue Oct 28 cash 08:30-15:00 CT), 5-pt rows 26030.0-26040.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_PD | DELTA / VP | 26080.0 - 26095.0 | overlaps | NT VP with delta, PD profile (Tue Oct 28 cash 08:30-15:00 CT), 5-pt rows 26080.0-26095.0: BUY delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | VOLUME / VP | 26035.0 - 26055.0 | overlaps | NT VP, Tue Oct 28 cash 08:30-15:00 CT, 5-pt rows >= 70% of the peak row (26035.0) | | |
| DD_EDGE_PD | STRUCTURE / VP | 26039.75 - 26079.75 | overlaps | NT VP over Tue Oct 28 cash 08:30-15:00 CT, 5-pt rows: the PD double distribution (two HVN blocks >= 70% of the smoothed peak, separator 26090.0 - 26109.75) | | |

**D_PDVAH_PDSET_ONL_PDTVAH**: 26149.5 - 26179.75 (30.25 pts); families 4: AUCTION_VALUE, STRUCTURE, GEX, VWAP; long=ANY short=ANY; stop 123 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDVAH | AUCTION_VALUE / VP | 26154.5 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, volume profile | | |
| ONL | STRUCTURE / VP | 26164.5 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, low | | |
| WKVWAP_SD1_UP | VWAP / 08:10 | 26151.07 | inside | sidecar `vwap.WEEKLY.sd1_up` (= 26151.07; window 2025-10-26T17:00 - 08:10) | | |
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
| VWAP | VWAP / 08:10 | 26247.0 | inside | sidecar `vwap.SESSION.vwap` (= 26247.05; window 2025-10-28T17:00 - 08:10) | | |
| VWAPU1 | VWAP / 08:10 | 26281.75 | 4.25 pts outside | sidecar `vwap.SESSION.sd1_up` (= 26281.76; window 2025-10-28T17:00 - 08:10) | | |
| VWAP_SD1_UP | VWAP / 08:10 | 26281.76 | 4.26 pts outside | sidecar `vwap.SESSION.sd1_up` (= 26281.76; window 2025-10-28T17:00 - 08:10) | | |
| HVL_0DTE | GEX / GEX | 26210.0 | 10.00 pts outside | GEX csv: row 2025-10-29, column `hvl_0dte_nt` (= 26210.0); CME report 2025-10-28 (D-1) | | |
| ONPOC_AREA | VOLUME / VP | 26227.5 - 26267.5 | overlaps | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26245.0) | | |

**D_ONVAH_WKTVAH_ONTVAH_WKVAH_ONH**: 26286.75 - 26314.75 (28.00 pts); families 5: AUCTION_VALUE, STRUCTURE, DELTA, GEX, VWAP; long=ANY short=ANY; stop 114 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONVAH | AUCTION_VALUE / VP | 26291.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, volume profile | | |
| ONTVAH | AUCTION_VALUE / VP | 26299.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, TPO profile | | |
| ONH | STRUCTURE / VP | 26309.75 | inside | NT VP, overnight Tue Oct 28 17:00 - 08:10 CT, high | | |
| VWAPU1 | VWAP / 08:10 | 26281.75 | 5.00 pts outside | sidecar `vwap.SESSION.sd1_up` (= 26281.76; window 2025-10-28T17:00 - 08:10) | | |
| WKVAH | AUCTION_VALUE / VP | 26303.25 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_UP | VWAP / 08:10 | 26281.76 | 4.99 pts outside | sidecar `vwap.SESSION.sd1_up` (= 26281.76; window 2025-10-28T17:00 - 08:10) | | |
| CR | GEX / GEX | 26300.0 | inside | GEX csv: row 2025-10-29, column `call_resistance_nt` (= 26300.0); CME report 2025-10-28 (D-1) | | |
| CR_0DTE | GEX / GEX | 26300.0 | inside | GEX csv: row 2025-10-29, column `call_resistance_0dte_nt` (= 26300.0); CME report 2025-10-28 (D-1) | | |
| T_DELTA_BUY_ON | DELTA / VP | 26285.0 - 26295.0 | overlaps | NT VP with delta, ON profile (overnight Tue Oct 28 17:00 - 08:10 CT), 5-pt rows 26285.0-26295.0: BUY delta, each row in the top 20% of abs delta | | |

### Weekly double distribution (ours: PD rule applied to weekly)

NT VP over the developing week Sun Oct 26 17:00 - 08:10 CT, 5-pt rows: lower HVN 25925.0 - 25934.75; separator (LVN) 25950.0 - 25954.75; upper HVN 25965.0 - 25974.75. Row by row values: hand-check pack section E2.

## 2025-10-31 (Fri)

Plan plan-v2.4-book1a-v1.3; market_context NONE; review APPROVED; 5 decision zones.

### 08:10 values (source: sidecar)

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 26198.75 | the 08:10 bar close on the chart; sidecar has it in the zone sides | | |
| session vwap | 26192.27 | sidecar `vwap.SESSION.vwap` (window 2025-10-30T17:00 - 08:10) | | |
| session sd1_up | 26222.15 | sidecar `vwap.SESSION.sd1_up` (window 2025-10-30T17:00 - 08:10) | | |
| session sd1_dn | 26162.38 | sidecar `vwap.SESSION.sd1_dn` (window 2025-10-30T17:00 - 08:10) | | |
| weekly vwap | 26084.24 | sidecar `vwap.WEEKLY.vwap` (window 2025-10-26T17:00 - 08:10) | | |
| weekly sd1_up | 26230.44 | sidecar `vwap.WEEKLY.sd1_up` (window 2025-10-26T17:00 - 08:10) | | |
| weekly sd1_dn | 25938.04 | sidecar `vwap.WEEKLY.sd1_dn` (window 2025-10-26T17:00 - 08:10) | | |
| market_context | NONE | sidecar `plan` line `market_context=` | | |
| draw_status | NONE | sidecar `plan` line `draw_status=` | | |
| value_follows | DIVERGENT_UP | sidecar `plan` line `value_follows=` | | |
| on_inventory | NET_LONG | sidecar `plan` line `on_inventory=` | | |
| on_vs_settle | 316.0 | sidecar `plan` line `on_vs_settle=` | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | POS | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| weekly double distribution | AVAILABLE; split no | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |

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

**D_WKVAL_PDVAL_PDPOC_WKPOC_PDTVAL**: 25952.25 - 25980.0 (27.75 pts); families 3: AUCTION_VALUE, DELTA, VOLUME; long=ANY short=ANY; stop 113 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDPOC | VOLUME / VP | 25970.75 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, volume profile | | |
| PDVAL | AUCTION_VALUE / VP | 25967.5 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, volume profile | | |
| WKPOC | VOLUME / VP | 25970.75 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| WKVAL | AUCTION_VALUE / VP | 25957.25 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| T_DELTA_SELL_PD | DELTA / VP | 26040.0 - 26050.0 | overlaps | NT VP with delta, PD profile (Thu Oct 30 cash 08:30-15:00 CT), 5-pt rows 26040.0-26050.0: SELL delta, each row in the top 20% of abs delta | | |

**D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ**: 25995.0 - 26099.75 (104.75 pts); families 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 421 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDVAH | AUCTION_VALUE / VP | 26090.0 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, volume profile | | |
| PDTPOC | VOLUME / VP | 26037.5 | inside | NT VP, Thu Oct 30 cash 08:30-15:00 CT, TPO profile | | |
| PD2L | STRUCTURE / VP | 26049.25 | inside | NT VP, Wed Oct 29 cash 08:30-15:00 CT, low | | |
| PD3L | STRUCTURE / VP | 26006.0 | inside | NT VP, Tue Oct 28 cash 08:30-15:00 CT, low | | |
| WKVWAP | VWAP / 08:10 | 26084.24 | inside | sidecar `vwap.WEEKLY.vwap` (= 26084.24; window 2025-10-26T17:00 - 08:10) | | |
| CR | GEX / GEX | 26000.0 | inside | GEX csv: row 2025-10-31, column `call_resistance_nt` (= 26000.0); CME report 2025-10-30 (D-1) | | |
| T_DELTA_BUY_WK | DELTA / VP | 26275.0 - 26290.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26275.0-26290.0: BUY delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | DELTA / VP | 26040.0 - 26050.0 | overlaps | NT VP with delta, PD profile (Thu Oct 30 cash 08:30-15:00 CT), 5-pt rows 26040.0-26050.0: SELL delta, each row in the top 20% of abs delta | | |
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
| VWAP | VWAP / 08:10 | 26192.25 | inside | sidecar `vwap.SESSION.vwap` (= 26192.27; window 2025-10-30T17:00 - 08:10) | | |
| VWAPU1 | VWAP / 08:10 | 26222.25 | inside | sidecar `vwap.SESSION.sd1_up` (= 26222.15; window 2025-10-30T17:00 - 08:10) | | |
| VWAPL1 | VWAP / 08:10 | 26162.5 | inside | sidecar `vwap.SESSION.sd1_dn` (= 26162.38; window 2025-10-30T17:00 - 08:10) | | |
| VWAP_SD1_UP | VWAP / 08:10 | 26222.15 | inside | sidecar `vwap.SESSION.sd1_up` (= 26222.15; window 2025-10-30T17:00 - 08:10) | | |
| VWAP_SD1_DN | VWAP / 08:10 | 26162.38 | inside | sidecar `vwap.SESSION.sd1_dn` (= 26162.38; window 2025-10-30T17:00 - 08:10) | | |
| WKVWAP_SD1_UP | VWAP / 08:10 | 26230.44 | inside | sidecar `vwap.WEEKLY.sd1_up` (= 26230.44; window 2025-10-26T17:00 - 08:10) | | |
| CR_0DTE | GEX / GEX | 26150.0 | inside | GEX csv: row 2025-10-31, column `call_resistance_0dte_nt` (= 26150.0); CME report 2025-10-30 (D-1) | | |
| T_DELTA_SELL_WK | DELTA / VP | 26230.0 - 26240.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26230.0-26240.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_ON | DELTA / VP | 26200.0 - 26215.0 | overlaps | NT VP with delta, ON profile (overnight Thu Oct 30 17:00 - 08:10 CT), 5-pt rows 26200.0-26215.0: BUY delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | VOLUME / VP | 26175.0 - 26200.0 | overlaps | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26190.0) | | |
| REJ_HIGH_PD | STRUCTURE / chart | 26142.5 - 26182.5 | overlaps | 1-minute chart: swing bar close Thu Oct 30 09:01, swing 26182.5; available Thu Oct 30 09:16 (pack section B) | | |

**T_PD2TPOC**: 26237.5 - 26247.5 (10.00 pts); families 2: DELTA, VOLUME; long=ANY short=ANY; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| T_DELTA_SELL_WK | DELTA / VP | 26230.0 - 26240.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26230.0-26240.0: SELL delta, each row in the top 20% of abs delta | | |
| WKPOC_AREA | VOLUME / VP | 26252.5 - 26292.5 | overlaps | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26270.0) | | |

**WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK**: 26252.5 - 26306.5 (54.00 pts); families 4: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME; long=NONE short=NONE; stop 218 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONH | STRUCTURE / VP | 26274.0 | inside | NT VP, overnight Thu Oct 30 17:00 - 08:10 CT, high | | |
| WKVAH | AUCTION_VALUE / VP | 26270.5 | inside | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| T_DELTA_BUY_WK | DELTA / VP | 26275.0 - 26290.0 | overlaps | NT VP with delta, WK profile (developing week Sun Oct 26 17:00 - 08:10 CT), 5-pt rows 26275.0-26290.0: BUY delta, each row in the top 20% of abs delta | | |
| WKPOC_AREA | VOLUME / VP | 26252.5 - 26292.5 | overlaps | NT VP, developing week Sun Oct 26 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (26270.0) | | |
| REJ_HIGH_WK | STRUCTURE / chart | 26266.5 - 26306.5 | overlaps | 1-minute chart: swing bar close Wed Oct 29 23:38, swing 26306.5; available Wed Oct 29 23:53 (pack section B) | | |

## 2025-11-18 (Tue)

Plan plan-v2.4-book1a-v1.3; market_context NONE; review APPROVED; 5 decision zones.

### 08:10 values (source: sidecar)

| value | plan / sidecar value | check against | hand | match |
|---|---|---|---|---|
| price at 08:10 (packet ref_price) | 24746.5 | the 08:10 bar close on the chart; sidecar has it in the zone sides | | |
| session vwap | 24774.35 | sidecar `vwap.SESSION.vwap` (window 2025-11-17T17:00 - 08:10) | | |
| session sd1_up | 24856.07 | sidecar `vwap.SESSION.sd1_up` (window 2025-11-17T17:00 - 08:10) | | |
| session sd1_dn | 24692.64 | sidecar `vwap.SESSION.sd1_dn` (window 2025-11-17T17:00 - 08:10) | | |
| weekly vwap | 24989.77 | sidecar `vwap.WEEKLY.vwap` (window 2025-11-16T17:00 - 08:10) | | |
| weekly sd1_up | 25163.00 | sidecar `vwap.WEEKLY.sd1_up` (window 2025-11-16T17:00 - 08:10) | | |
| weekly sd1_dn | 24816.55 | sidecar `vwap.WEEKLY.sd1_dn` (window 2025-11-16T17:00 - 08:10) | | |
| market_context | NONE | sidecar `plan` line `market_context=` | | |
| draw_status | NONE | sidecar `plan` line `draw_status=` | | |
| value_follows | WITH_PRICE | sidecar `plan` line `value_follows=` | | |
| on_inventory | NET_SHORT | sidecar `plan` line `on_inventory=` | | |
| on_vs_settle | -132.5 | sidecar `plan` line `on_vs_settle=` | | |
| htf_structure | BALANCE | sidecar `plan` line `htf_structure=` | | |
| gex_regime | NEG | sidecar `plan` line `gex_regime=` | | |
| wkval_state | accept=BELOW|failed_reclaim=0 | sidecar `plan` line `wkval_state=` | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | sidecar `plan` line `wkvah_state=` | | |
| weekly double distribution | AVAILABLE; split yes | sidecar `weekly_dd` (ours: PD rule applied to weekly) | | |

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
| T_DELTA_BUY_ON | DELTA / VP | 24650.0 - 24660.0 | overlaps | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24650.0-24660.0: BUY delta, each row in the top 20% of abs delta | | |

**ONPOC_AREA_D_PDL_ONTPOC_ONPOC**: 24715.0 - 24755.0 (40.00 pts); families 3: STRUCTURE, DELTA, VOLUME; long=ANY short=ANY; stop 162 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| PDL | STRUCTURE / VP | 24731.75 | inside | NT VP, Mon Nov 17 cash 08:30-15:00 CT, low | | |
| ONPOC | VOLUME / VP | 24750.0 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, volume profile | | |
| ONTPOC | VOLUME / VP | 24742.5 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, TPO profile | | |
| T_DELTA_SELL_ON | DELTA / VP | 24820.0 - 24845.0 | overlaps | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | VOLUME / VP | 24715.0 - 24755.0 | overlaps | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, 5-pt rows >= 70% of the peak row (24740.0) | | |

**T_HTFPOC**: 24822.5 - 24832.5 (10.00 pts); families 2: DELTA, VOLUME; long=ANY short=ANY; stop 42 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| HTFPOC | VOLUME / VP | 24827.5 | inside | NT VP over the packet's window (HTF composite (packet htf_composite window)) | | |
| T_DELTA_SELL_WK | DELTA / VP | 24820.0 - 24845.0 | overlaps | NT VP with delta, WK profile (developing week Sun Nov 16 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_ON | DELTA / VP | 24820.0 - 24845.0 | overlaps | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |

**D_ONVAH_WKVAL_ONTVAH**: 24846.25 - 24864.75 (18.50 pts); families 3: AUCTION_VALUE, DELTA, VWAP; long=INITIATION short=ANY; stop 76 ticks

| level | type | value | inside zone / distance | check against | hand | match |
|---|---|---|---|---|---|---|
| ONVAH | AUCTION_VALUE / VP | 24851.25 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, volume profile | | |
| ONTVAH | AUCTION_VALUE / VP | 24859.75 | inside | NT VP, overnight Mon Nov 17 17:00 - 08:10 CT, TPO profile | | |
| VWAPU1 | VWAP / 08:10 | 24856.0 | inside | sidecar `vwap.SESSION.sd1_up` (= 24856.07; window 2025-11-17T17:00 - 08:10) | | |
| WKVAL | AUCTION_VALUE / VP | 24856.0 | inside | NT VP, developing week Sun Nov 16 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_UP | VWAP / 08:10 | 24856.07 | inside | sidecar `vwap.SESSION.sd1_up` (= 24856.07; window 2025-11-17T17:00 - 08:10) | | |
| T_DELTA_SELL_WK | DELTA / VP | 24820.0 - 24845.0 | overlaps | NT VP with delta, WK profile (developing week Sun Nov 16 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_ON | DELTA / VP | 24820.0 - 24845.0 | overlaps | NT VP with delta, ON profile (overnight Mon Nov 17 17:00 - 08:10 CT), 5-pt rows 24820.0-24845.0: SELL delta, each row in the top 20% of abs delta | | |

### Weekly double distribution (ours: PD rule applied to weekly)

NT VP over the developing week Sun Nov 16 17:00 - 08:10 CT, 5-pt rows: lower HVN 24865.0 - 24874.75; separator (LVN) 24925.0 - 24954.75; upper HVN 24970.0 - 24989.75. Row by row values: hand-check pack section E2.

