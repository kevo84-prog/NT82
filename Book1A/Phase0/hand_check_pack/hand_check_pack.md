# P0.7-P0.9 hand-check pack (hand-check-pack-v1.2)

Every value below is frozen at 08:10 CT and comes from data before 08:10 CT. Times are CT, 1-minute bars stamped by their close (NinjaTrader bar time). Prices are NQ front month as on the chart. No trades, outcomes or P&L. Fill the hand column from the chart, not from the plan.

| day | plan | decision zones | REJ zones before selection | REJ in plan | FLIP | wide stop (> 196 ticks) | DD_EDGE (PD; weekly) |
|---|---|---|---|---|---|---|---|
| 2025-10-22 | plan-v2.4-book1a-v1.3 | 3 | 0 (0 after merge) | 0 | 0 | D_PDL_ONL_WKTVAL_ONVAL_ONTVA 269 | PD no; WK no |
| 2025-10-23 | plan-v2.4-book1a-v1.3 | 4 | 1 (1 after merge) | 1 | 0 | none | PD no; WK no |
| 2025-10-24 | plan-v2.4-book1a-v1.3 | 2 | 1 (1 after merge) | 0 | 0 | none | PD no; WK no |
| 2025-10-27 | plan-v2.4-book1a-v1.3 | 3 | 0 (0 after merge) | 0 | 0 | none | PD no; WK 25720.0-25734.75 |
| 2025-10-28 | plan-v2.4-book1a-v1.3 | 2 | 0 (0 after merge) | 0 | 0 | none | PD no; WK no |
| 2025-10-29 | plan-v2.4-book1a-v1.3 | 4 | 0 (0 after merge) | 0 | 0 | D_ONTVAL_PDH_ONVAL_ONPOC_ONP 232 | PD 26039.75-26079.75; WK 25925.0-25934.75 |
| 2025-10-30 | plan-v2.4-book1a-v1.3 | 4 | 5 (4 after merge) | 3 | 0 | D_ONTVAL_ONPOC_PDTVAL_PDVAL_ 312 | PD no; WK no |
| 2025-10-31 | plan-v2.4-book1a-v1.3 | 5 | 9 (7 after merge) | 4 | 0 | D_WKTVAL_PD3L_PD3VAL_PD3TVAL 421; REJ_HIGH_PD_D_PD3VAH_ONTVAL_ 378; WKPOC_AREA_D_WKVAH_ONH_PD2PO 218 | PD no; WK no |
| 2025-11-03 | plan-v2.4-book1a-v1.3 | 4 | 1 (1 after merge) | 1 | 0 | none | PD 26005.0-26014.75; WK no |
| 2025-11-04 | plan-v2.4-book1a-v1.3 | 2 | 2 (2 after merge) | 0 | 0 | none | PD no; WK no |
| 2025-11-17 | plan-v2.4-book1a-v1.3 | 4 | 0 (0 after merge) | 0 | 0 | PDPOC_AREA_D_PDPOC_PDTPOC_PW 216 | PD no; WK no |
| 2025-11-18 | plan-v2.4-book1a-v1.3 | 5 | 2 (2 after merge) | 2 | 0 | none | PD 24865.0-24874.75; WK 24970.0-24989.75 |
| 2025-11-19 | plan-v2.4-book1a-v1.3 | 5 | 4 (4 after merge) | 3 | 0 | D_PDTPOC_WKTPOC_WKPOC_AREA_D 362; T_PDTVAH_PDVAH_REJ_HIGH_PD_D 231 | PD no; WK no |

## A. Decision zones (P0.7, P0.8)

Rebuild each zone from its levels: every level must be inside the zone, or a GEX level within 10 points of an edge (C2). Families count once each; DECISION needs 2+.

**2025-10-22 D_PDVAH_ONH_WKVAH_PDH_PD2VAH_PD2H_P2**: 25325.5 - 25364.75 (39.25 pts), families 5: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, VWAP; long=INITIATION short=ANY; stop 159 ticks; frozen 2025-10-22T08:10:00-05:00

| level | price / rows | inside zone or distance | where it comes from (find on chart) | hand | match |
|---|---|---|---|---|---|
| PDVAH | 25326.0 | inside | Tue Oct 21 cash 08:30-15:00 CT, volume profile | | |
| PDH | 25348.5 | inside | Tue Oct 21 cash 08:30-15:00 CT, high | | |
| PD2H | 25354.5 | inside | Mon Oct 20 cash 08:30-15:00 CT, high | | |
| ONH | 25338.25 | inside | overnight Tue Oct 21 17:00 - 08:10 CT, high | | |
| WKVAH | 25340.5 | inside | developing week Sun Oct 19 17:00 - 08:10 CT, volume profile | | |
| WKVWAP_SD1_UP | 25337.16 | inside | weekly VWAP from Sun Oct 19 17:00, value at the 08:10 bar close | | |
| T_DELTA_BUY_WK | 25315.0 - 25355.0 (delta sum 5568) | band | WK profile, 5-pt rows 25315.0-25355.0: BUY delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | 25292.5 - 25332.5 (peak row 25310.0, vol 20438) | area | PD volume profile, 5-pt rows >= 70% of the peak row | | |

**2025-10-29 PDPOC_AREA_DD_EDGE_PD_D_PDPOC_WKPOC_PDTPOC**: 26035.0 - 26079.75 (44.75 pts), families 3: STRUCTURE, DELTA, VOLUME; long=ANY short=INITIATION; stop 181 ticks; frozen 2025-10-29T08:10:00-05:00

| level | price / rows | inside zone or distance | where it comes from (find on chart) | hand | match |
|---|---|---|---|---|---|
| DD_EDGE_PD (STRUCTURE) | 26039.75 - 26079.75 | overlaps | PD double distribution, see section E | | |
| PDPOC | 26045.0 | inside | Tue Oct 28 cash 08:30-15:00 CT, volume profile | | |
| PDTPOC | 26052.5 | inside | Tue Oct 28 cash 08:30-15:00 CT, TPO profile | | |
| WKPOC | 26045.0 | inside | developing week Sun Oct 26 17:00 - 08:10 CT, volume profile | | |
| T_DELTA_BUY_WK | 26045.0 - 26055.0 (delta sum 1373) | band | WK profile, 5-pt rows 26045.0-26055.0: BUY delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | 26030.0 - 26040.0 (delta sum -1423) | band | PD profile, 5-pt rows 26030.0-26040.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_PD | 26080.0 - 26095.0 (delta sum 1385) | band | PD profile, 5-pt rows 26080.0-26095.0: BUY delta, each row in the top 20% of abs delta | | |
| PDPOC_AREA | 26035.0 - 26055.0 (peak row 26035.0, vol 17374) | area | PD volume profile, 5-pt rows >= 70% of the peak row | | |

**2025-10-31 REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC**: 26142.5 - 26236.5 (94.00 pts), families 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 378 ticks; frozen 2025-10-31T08:10:00-05:00

| level | price / rows | inside zone or distance | where it comes from (find on chart) | hand | match |
|---|---|---|---|---|---|
| REJ_HIGH_PD (STRUCTURE) | 26142.5 - 26182.5 | overlaps | swing bar close Thu Oct 30 09:01, see section B | | |
| PDH | 26182.5 | inside | Thu Oct 30 cash 08:30-15:00 CT, high | | |
| PD3H | 26231.5 | inside | Tue Oct 28 cash 08:30-15:00 CT, high | | |
| ONVAH | 26217.25 | inside | overnight Thu Oct 30 17:00 - 08:10 CT, volume profile | | |
| ONPOC | 26190.0 | inside | overnight Thu Oct 30 17:00 - 08:10 CT, volume profile | | |
| ONVAL | 26158.5 | inside | overnight Thu Oct 30 17:00 - 08:10 CT, volume profile | | |
| ONTVAH | 26209.75 | inside | overnight Thu Oct 30 17:00 - 08:10 CT, TPO profile | | |
| ONTPOC | 26192.5 | inside | overnight Thu Oct 30 17:00 - 08:10 CT, TPO profile | | |
| ONTVAL | 26155.0 | inside | overnight Thu Oct 30 17:00 - 08:10 CT, TPO profile | | |
| VWAP | 26192.27 | inside | session VWAP from Thu Oct 30 17:00, value at the 08:10 bar close | | |
| VWAPU1 | 26222.25 | inside | session VWAP from Thu Oct 30 17:00, value at the 08:10 bar close | | |
| VWAPL1 | 26162.5 | inside | session VWAP from Thu Oct 30 17:00, value at the 08:10 bar close | | |
| VWAP_SD1_UP | 26222.15 | inside | session VWAP from Thu Oct 30 17:00, value at the 08:10 bar close | | |
| VWAP_SD1_DN | 26162.38 | inside | session VWAP from Thu Oct 30 17:00, value at the 08:10 bar close | | |
| WKVWAP_SD1_UP | 26230.44 | inside | weekly VWAP from Sun Oct 26 17:00, value at the 08:10 bar close | | |
| CR_0DTE | 26150.0 | inside | GEX, not on the chart: gex_levels_block1.csv row 2025-10-31, CME report 2025-10-30 (D-1) | | |
| T_DELTA_SELL_WK | 26230.0 - 26240.0 (delta sum -2185) | band | WK profile, 5-pt rows 26230.0-26240.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_BUY_ON | 26200.0 - 26215.0 (delta sum 922) | band | ON profile, 5-pt rows 26200.0-26215.0: BUY delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | 26175.0 - 26200.0 (peak row 26190.0, vol 7006) | area | ON volume profile, 5-pt rows >= 70% of the peak row | | |

**2025-10-22 D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA**: 25198.25 - 25265.0 (66.75 pts), families 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP; long=NONE short=NONE; stop 269 ticks; frozen 2025-10-22T08:10:00-05:00

| level | price / rows | inside zone or distance | where it comes from (find on chart) | hand | match |
|---|---|---|---|---|---|
| PDVAL | 25254.0 | inside | Tue Oct 21 cash 08:30-15:00 CT, volume profile | | |
| PDL | 25203.25 | inside | Tue Oct 21 cash 08:30-15:00 CT, low | | |
| ONPOC | 25250.0 | inside | overnight Tue Oct 21 17:00 - 08:10 CT, volume profile | | |
| ONVAL | 25222.75 | inside | overnight Tue Oct 21 17:00 - 08:10 CT, volume profile | | |
| ONTPOC | 25267.5 | 2.50 pts outside | overnight Tue Oct 21 17:00 - 08:10 CT, TPO profile | | |
| ONTVAL | 25235.0 | inside | overnight Tue Oct 21 17:00 - 08:10 CT, TPO profile | | |
| ONL | 25206.5 | inside | overnight Tue Oct 21 17:00 - 08:10 CT, low | | |
| VWAP | 25267.38 | 2.38 pts outside | session VWAP from Tue Oct 21 17:00, value at the 08:10 bar close | | |
| VWAPL1 | 25238.25 | inside | session VWAP from Tue Oct 21 17:00, value at the 08:10 bar close | | |
| WKVAL | 25244.25 | inside | developing week Sun Oct 19 17:00 - 08:10 CT, volume profile | | |
| VWAP_SD1_DN | 25238.13 | inside | session VWAP from Tue Oct 21 17:00, value at the 08:10 bar close | | |
| WKVWAP | 25262.44 | inside | weekly VWAP from Sun Oct 19 17:00, value at the 08:10 bar close | | |
| HVL | 25230.0 | inside | GEX, not on the chart: gex_levels_block1.csv row 2025-10-22, CME report 2025-10-21 (D-1) | | |
| HVL_0DTE | 25260.0 | inside | GEX, not on the chart: gex_levels_block1.csv row 2025-10-22, CME report 2025-10-21 (D-1) | | |
| T_DELTA_SELL_WK | 25295.0 - 25315.0 (delta sum -3619) | band | WK profile, 5-pt rows 25295.0-25315.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_PD | 25270.0 - 25280.0 (delta sum -1100) | band | PD profile, 5-pt rows 25270.0-25280.0: SELL delta, each row in the top 20% of abs delta | | |
| T_DELTA_SELL_ON | 25225.0 - 25240.0 (delta sum -666) | band | ON profile, 5-pt rows 25225.0-25240.0: SELL delta, each row in the top 20% of abs delta | | |
| ONPOC_AREA | 25245.0 - 25265.0 (peak row 25250.0, vol 6847) | area | ON volume profile, 5-pt rows >= 70% of the peak row | | |

## B. Rejection zones (P0.7, PO-1)

Swing = the bar's high (low) is strictly above (below) the 15 bars before and the 15 after; arrival evidence = delta >= 150 that way (or a stacked imbalance / large trade) in the swing bar or the 2 before; departure = the largest move away within 10 bars, at least 0.25 x ADR; far edge = the body extreme of the swing bar +/- 2 bars, capped at 40 points, at least 10 points wide.

**2025-10-23** (ADR 523.95; plan keeps: REJ_LOW PD 24867.0-24907.0; decision zones built on a REJ: REJ_LOW_PD_T_PDVAL)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_LOW | PD | Wed Oct 22 11:34 | 24867.0 | 24878.25 (11:33) | 24941.25 (11:35) | 11:33 (delta -289) | 11:42, 25021.5, 154.50 (need >= 130.99 = 0.25 ADR) | 25002.5 at 11:36 (bars 11:32-11:36) | 24867.0 - 24907.0 | | |

**2025-10-24** (ADR 536.52; plan keeps: none; decision zones built on a REJ: none)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_LOW | WK | Wed Oct 22 11:34 | 24867.0 | 24878.25 (11:33) | 24941.25 (11:35) | 11:33 (delta -289) | 11:42, 25021.5, 154.50 (need >= 134.13 = 0.25 ADR) | 25002.5 at 11:36 (bars 11:32-11:36) | 24867.0 - 24907.0 | | |

**2025-10-30** (ADR 386.50; plan keeps: REJ_HIGH PD 26188.0-26228.0; REJ_HIGH ON 26266.5-26306.5; REJ_LOW PD 26049.25-26089.25; decision zones built on a REJ: REJ_LOW_PD_T_ONL, D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_HIGH | PD | Wed Oct 29 13:35 | 26283.5 | 26281.75 (13:34) | 26272.75 (13:36) | 13:34 (delta 292) | 13:42, 26049.25, 234.25 (need >= 96.62 = 0.25 ADR) | 26152.75 at 13:36 (bars 13:33-13:37) | 26243.5 - 26283.5 | | |
| 2 | REJ_LOW | PD | Wed Oct 29 13:42 | 26049.25 | 26060.0 (13:41) | 26052.0 (13:44) | 13:40 (stacked sell imbalance, delta -73) | 13:52, 26195.0, 145.75 (need >= 96.62 = 0.25 ADR) | 26143.0 at 13:40 (bars 13:40-13:44) | 26049.25 - 26089.25 | | |
| 3 | REJ_HIGH | PD | Wed Oct 29 13:56 | 26228.0 | 26213.0 (13:55) | 26220.0 (13:58) | 13:55 (delta 223) | 14:05, 26111.75, 116.25 (need >= 96.62 = 0.25 ADR) | 26174.25 at 13:57 (bars 13:54-13:58) | 26188.0 - 26228.0 | | |
| 4 | REJ_HIGH | WK | Wed Oct 29 15:03 | 26379.75 | 26355.0 (15:02) | 26361.0 (15:04) | 15:01 (delta 742) | 15:09, 26159.75, 220.00 (need >= 96.62 = 0.25 ADR) | 26275.0 at 15:05 (bars 15:01-15:05) | 26339.75 - 26379.75 | | |
| 5 | REJ_HIGH | ON | Wed Oct 29 23:38 | 26306.5 | 26299.75 (23:37) | 26303.5 (23:39) | 23:36 (delta 387) | 23:47, 26196.25, 110.25 (need >= 96.62 = 0.25 ADR) | 26184.0 at 23:36 (bars 23:36-23:40) | 26266.5 - 26306.5 | | |
| merged | REJ_HIGH | ON | REJ_HIGH swing Wed Oct 29 13:35 confirmed Wed Oct 29 13:50; REJ_HIGH swing Wed Oct 29 23:38 confirmed Wed Oct 29 23:53 | | | | | | | 26266.5 - 26306.5; available at the latest confirmation Wed Oct 29 23:53 | | |

**2025-10-31** (ADR 387.50; plan keeps: REJ_HIGH WK 26266.5-26306.5; REJ_HIGH WK 26339.75-26379.75; REJ_HIGH PD 26142.5-26182.5; REJ_LOW WK 26049.25-26089.25; decision zones built on a REJ: D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ, REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC, WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_HIGH | WK | Wed Oct 29 13:35 | 26283.5 | 26281.75 (13:34) | 26272.75 (13:36) | 13:34 (delta 292) | 13:42, 26049.25, 234.25 (need >= 96.88 = 0.25 ADR) | 26152.75 at 13:36 (bars 13:33-13:37) | 26243.5 - 26283.5 | | |
| 2 | REJ_LOW | WK | Wed Oct 29 13:42 | 26049.25 | 26060.0 (13:41) | 26052.0 (13:44) | 13:40 (stacked sell imbalance, delta -73) | 13:52, 26195.0, 145.75 (need >= 96.88 = 0.25 ADR) | 26143.0 at 13:40 (bars 13:40-13:44) | 26049.25 - 26089.25 | | |
| 3 | REJ_HIGH | WK | Wed Oct 29 13:56 | 26228.0 | 26213.0 (13:55) | 26220.0 (13:58) | 13:55 (delta 223) | 14:05, 26111.75, 116.25 (need >= 96.88 = 0.25 ADR) | 26174.25 at 13:57 (bars 13:54-13:58) | 26188.0 - 26228.0 | | |
| 4 | REJ_HIGH | WK | Wed Oct 29 15:03 | 26379.75 | 26355.0 (15:02) | 26361.0 (15:04) | 15:01 (delta 742) | 15:09, 26159.75, 220.00 (need >= 96.88 = 0.25 ADR) | 26275.0 at 15:05 (bars 15:01-15:05) | 26339.75 - 26379.75 | | |
| 5 | REJ_HIGH | WK | Wed Oct 29 23:38 | 26306.5 | 26299.75 (23:37) | 26303.5 (23:39) | 23:36 (delta 387) | 23:47, 26196.25, 110.25 (need >= 96.88 = 0.25 ADR) | 26184.0 at 23:36 (bars 23:36-23:40) | 26266.5 - 26306.5 | | |
| 6 | REJ_LOW | PD | Thu Oct 30 08:41 | 25942.25 | 25949.25 (08:40) | 25947.75 (08:43) | 08:39 (delta -152) | 08:51, 26103.75, 161.50 (need >= 96.88 = 0.25 ADR) | 25973.0 at 08:43 (bars 08:39-08:43) | 25942.25 - 25973.0 | | |
| 7 | REJ_HIGH | PD | Thu Oct 30 09:01 | 26182.5 | 26147.25 (08:55) | 26162.5 (09:02) | 08:59 (stacked buy imbalance, delta 75) | 09:11, 26068.5, 114.00 (need >= 96.88 = 0.25 ADR) | 26124.75 at 09:01 (bars 08:59-09:03) | 26142.5 - 26182.5 | | |
| 8 | REJ_LOW | WK | Thu Oct 30 15:01 | 25853.0 | 25869.0 (15:00) | 25902.25 (15:02) | 15:01 (delta -353) | 15:02, 26000.0, 147.00 (need >= 96.88 = 0.25 ADR) | 25983.5 at 15:03 (bars 14:59-15:03) | 25853.0 - 25893.0 | | |
| 9 | REJ_LOW | WK | Thu Oct 30 15:31 | 25920.0 | 25993.5 (15:16) | 25951.25 (15:32) | 15:31 (delta -570) | 15:41, 26098.5, 178.50 (need >= 96.88 = 0.25 ADR) | 26033.25 at 15:30 (bars 15:29-15:33) | 25920.0 - 25960.0 | | |
| merged | REJ_HIGH | WK | REJ_HIGH swing Wed Oct 29 13:35 confirmed Wed Oct 29 13:50; REJ_HIGH swing Wed Oct 29 23:38 confirmed Wed Oct 29 23:53 | | | | | | | 26266.5 - 26306.5; available at the latest confirmation Wed Oct 29 23:53 | | |
| merged | REJ_LOW | WK | REJ_LOW swing Thu Oct 30 15:31 confirmed Thu Oct 30 15:46; REJ_LOW swing Thu Oct 30 08:41 confirmed Thu Oct 30 08:56 | | | | | | | 25920.0 - 25960.0; available at the latest confirmation Thu Oct 30 15:46 | | |

**2025-11-03** (ADR 361.45; plan keeps: REJ_HIGH PD 26118.0-26158.0; decision zones built on a REJ: REJ_HIGH_PD_T_PDTVAH_D_ONTVAH_WKTVAH_ONPOC_WKPOC)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_HIGH | PD | Fri Oct 31 10:46 | 26158.0 | 26154.5 (10:33) | 26141.75 (10:47) | 10:45 (delta 495) | 10:51, 26056.0, 102.00 (need >= 90.36 = 0.25 ADR) | 26084.75 at 10:45 (bars 10:44-10:48) | 26118.0 - 26158.0 | | |

**2025-11-04** (ADR 346.90; plan keeps: none; decision zones built on a REJ: none)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_HIGH | PD | Mon Nov 03 08:34 | 26266.0 | 26262.75 (08:32) | 26255.25 (08:35) | 08:32 (large buy trade, delta 125) | 08:43, 26155.0, 111.00 (need >= 86.72 = 0.25 ADR) | 26209.25 at 08:36 (bars 08:32-08:36) | 26226.0 - 26266.0 | | |
| 2 | REJ_LOW | PD | Mon Nov 03 09:37 | 26015.5 | 26017.0 (09:33) | 26021.5 (09:38) | 09:36 (delta -172) | 09:45, 26103.0, 87.50 (need >= 86.72 = 0.25 ADR) | 26060.0 at 09:39 (bars 09:35-09:39) | 26015.5 - 26055.5 | | |

**2025-11-18** (ADR 558.85; plan keeps: REJ_LOW PD 24955.0-24995.0; REJ_HIGH PD 25010.75-25050.75; decision zones built on a REJ: none)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_LOW | PD | Mon Nov 17 08:31 | 24955.0 | 24988.75 (08:30) | 24962.5 (08:32) | 08:29 (delta -199) | 08:41, 25184.5, 229.50 (need >= 139.71 = 0.25 ADR) | 25068.5 at 08:33 (bars 08:29-08:33) | 24955.0 - 24995.0 | | |
| 2 | REJ_HIGH | PD | Mon Nov 17 12:49 | 25050.75 | 25045.75 (12:48) | 25042.0 (12:50) | 12:47 (delta 268) | 12:59, 24886.75, 164.00 (need >= 139.71 = 0.25 ADR) | 25009.75 at 12:47 (bars 12:47-12:51) | 25010.75 - 25050.75 | | |

**2025-11-19** (ADR 559.00; plan keeps: REJ_HIGH PD 24792.0-24832.0; REJ_HIGH WK 25010.75-25050.75; REJ_LOW PD 24376.25-24416.25; decision zones built on a REJ: T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH)

| # | kind | session | swing bar close (CT) | swing price | 15 bars before: extreme (bar) | 15 bars after: extreme (bar) | arrival evidence bar (delta) | departure: bar, price, pts | far edge from bodies (bars) | zone lo - hi | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | REJ_LOW | WK | Mon Nov 17 08:31 | 24955.0 | 24988.75 (08:30) | 24962.5 (08:32) | 08:29 (delta -199) | 08:41, 25184.5, 229.50 (need >= 139.75 = 0.25 ADR) | 25068.5 at 08:33 (bars 08:29-08:33) | 24955.0 - 24995.0 | | |
| 2 | REJ_HIGH | WK | Mon Nov 17 12:49 | 25050.75 | 25045.75 (12:48) | 25042.0 (12:50) | 12:47 (delta 268) | 12:59, 24886.75, 164.00 (need >= 139.75 = 0.25 ADR) | 25009.75 at 12:47 (bars 12:47-12:51) | 25010.75 - 25050.75 | | |
| 3 | REJ_HIGH | PD | Tue Nov 18 08:34 | 24832.0 | 24798.0 (08:33) | 24802.75 (08:35) | 08:33 (delta 620) | 08:44, 24645.5, 186.50 (need >= 139.75 = 0.25 ADR) | 24670.0 at 08:33 (bars 08:32-08:36) | 24792.0 - 24832.0 | | |
| 4 | REJ_LOW | PD | Tue Nov 18 10:04 | 24376.25 | 24383.25 (10:03) | 24395.5 (10:05) | 10:02 (delta -951) | 10:12, 24552.5, 176.25 (need >= 139.75 = 0.25 ADR) | 24471.0 at 10:02 (bars 10:02-10:06) | 24376.25 - 24416.25 | | |

## C. Flip zones (P0.7, PO-1 step 4)

A REJ zone accepted through (3 one-minute closes 2 ticks beyond it), then an opposite REJ after that overlapping it by >= 50%, becomes a FLIP.

**2025-10-23**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_LOW 24867.0-24907.0 | Wed Oct 22 11:34 | yes, 3rd close Wed Oct 22 12:42 | none | no |

**2025-10-24**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_LOW 24867.0-24907.0 | Wed Oct 22 11:34 | yes, 3rd close Wed Oct 22 12:42 | none | no |

**2025-10-30**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_HIGH 26188.0-26228.0 | Wed Oct 29 13:56 | yes, 3rd close Wed Oct 29 14:53 | none | no |
| REJ_HIGH 26266.5-26306.5 | Wed Oct 29 23:38 | yes, 3rd close Thu Oct 30 00:41 | none | no |
| REJ_HIGH 26339.75-26379.75 | Wed Oct 29 15:03 | yes, 3rd close Wed Oct 29 22:18 | none | no |
| REJ_LOW 26049.25-26089.25 | Wed Oct 29 13:42 | no | none | no |

**2025-10-31**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_HIGH 26142.5-26182.5 | Thu Oct 30 09:01 | yes, 3rd close Thu Oct 30 19:29 | none | no |
| REJ_HIGH 26188.0-26228.0 | Wed Oct 29 13:56 | yes, 3rd close Wed Oct 29 14:53 | REJ_LOW 25853.0-25893.0 formed Thu Oct 30 15:01: no overlap; REJ_LOW 25920.0-25960.0 formed Thu Oct 30 15:31: no overlap | no |
| REJ_HIGH 26266.5-26306.5 | Wed Oct 29 23:38 | yes, 3rd close Thu Oct 30 00:41 | REJ_LOW 25853.0-25893.0 formed Thu Oct 30 15:01: no overlap; REJ_LOW 25920.0-25960.0 formed Thu Oct 30 15:31: no overlap | no |
| REJ_HIGH 26339.75-26379.75 | Wed Oct 29 15:03 | yes, 3rd close Wed Oct 29 22:18 | REJ_LOW 25853.0-25893.0 formed Thu Oct 30 15:01: no overlap; REJ_LOW 25920.0-25960.0 formed Thu Oct 30 15:31: no overlap | no |
| REJ_LOW 25853.0-25893.0 | Thu Oct 30 15:01 | no | none | no |
| REJ_LOW 25920.0-25960.0 | Thu Oct 30 15:31 | no | none | no |
| REJ_LOW 26049.25-26089.25 | Wed Oct 29 13:42 | yes, 3rd close Thu Oct 30 08:37 | REJ_HIGH 26142.5-26182.5 formed Thu Oct 30 09:01: no overlap | no |

**2025-11-03**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_HIGH 26118.0-26158.0 | Fri Oct 31 10:46 | yes, 3rd close Mon Nov 03 05:12 | none | no |

**2025-11-04**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_HIGH 26226.0-26266.0 | Mon Nov 03 08:34 | no | none | no |
| REJ_LOW 26015.5-26055.5 | Mon Nov 03 09:37 | yes, 3rd close Mon Nov 03 18:21 | none | no |

**2025-11-18**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_HIGH 25010.75-25050.75 | Mon Nov 17 12:49 | no | none | no |
| REJ_LOW 24955.0-24995.0 | Mon Nov 17 08:31 | yes, 3rd close Mon Nov 17 12:58 | none | no |

**2025-11-19**

| REJ zone (after merge) | formed | accepted through (3 closes 2 ticks beyond) | opposite REJ after that, overlap >= 50% | FLIP? |
|---|---|---|---|---|
| REJ_HIGH 24792.0-24832.0 | Tue Nov 18 08:34 | no | none | no |
| REJ_HIGH 25010.75-25050.75 | Mon Nov 17 12:49 | no | none | no |
| REJ_LOW 24376.25-24416.25 | Tue Nov 18 10:04 | no | none | no |
| REJ_LOW 24955.0-24995.0 | Mon Nov 17 08:31 | yes, 3rd close Mon Nov 17 12:58 | REJ_HIGH 24792.0-24832.0 formed Tue Nov 18 08:34: no overlap | no |

No FLIP zone forms on any of these 13 days, so **no historical flip has been checked**. Check by hand that no row above should be a FLIP. The FLIP rule's evidence is mechanical only: a synthetic unit test (test_map_v24) shows the code joins an accepted-through REJ and a later opposite REJ; it is not evidence from a real chart.

## D. Wide-stop zones (C3 risk check, U3)

stop ticks = zone width in ticks + 2; estimated risk for 1 NQ = (stop ticks + 2) x $5 + $5.74; above $1,000 the side is NONE (RISK_REJECT, never shrunk).

| day | zone | lo | hi | width pts | stop ticks | 1 NQ estimate | sides | pieces at the low / high end (a band, area or REJ zone can reach past the zone edge) | hand | match |
|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA | 25198.25 | 25265.0 | 66.75 | 269 | $1,360.74 | long=NONE short=NONE | low end: PDL 25203.25; high end: T_DELTA_SELL_WK 25315.0 (a single price gets the 5-pt pad) | | |
| 2025-10-29 | D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC | 26220.0 | 26277.5 | 57.50 | 232 | $1,175.74 | long=NONE short=NONE | low end: HVL_0DTE 26210.0; high end: VWAP_SD1_UP 26281.76 (a single price gets the 5-pt pad) | | |
| 2025-10-30 | D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON | 26185.0 | 26262.5 | 77.50 | 312 | $1,575.74 | long=NONE short=NONE | low end: T_DELTA_SELL_ON 26175.0; high end: WKPOC_AREA 26292.5 (a single price gets the 5-pt pad) | | |
| 2025-10-31 | D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ | 25995.0 | 26099.75 | 104.75 | 421 | $2,120.74 | long=NONE short=NONE | low end: CR 26000.0; high end: T_DELTA_BUY_WK 26290.0 (a single price gets the 5-pt pad) | | |
| 2025-10-31 | REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC | 26142.5 | 26236.5 | 94.00 | 378 | $1,905.74 | long=NONE short=NONE | low end: REJ_HIGH_PD 26142.5; high end: T_DELTA_SELL_WK 26240.0 (a single price gets the 5-pt pad) | | |
| 2025-10-31 | WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK | 26252.5 | 26306.5 | 54.00 | 218 | $1,105.74 | long=NONE short=NONE | low end: WKPOC_AREA 26252.5; high end: REJ_HIGH_WK 26306.5 (a single price gets the 5-pt pad) | | |
| 2025-11-17 | PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL | 25130.0 | 25183.5 | 53.50 | 216 | $1,095.74 | long=NONE short=NONE | low end: T_DELTA_SELL_PD 25120.0; high end: T_DELTA_BUY_PD 25270.0 (a single price gets the 5-pt pad) | | |
| 2025-11-19 | D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA | 24687.5 | 24777.5 | 90.00 | 362 | $1,825.74 | long=NONE short=NONE | low end: T_DELTA_BUY_PD 24675.0; high end: T_DELTA_BUY_WK 24810.0 (a single price gets the 5-pt pad) | | |
| 2025-11-19 | T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH | 24779.75 | 24837.0 | 57.25 | 231 | $1,170.74 | long=NONE short=NONE | low end: PDPOC_AREA 24737.5; high end: T_DELTA_SELL_WK 24845.0 (a single price gets the 5-pt pad) | | |

## E. DD_EDGE (P0.7, PO-11)

### E1. PD double distribution (the map's rule)

**2025-10-29**: packet double_distribution = {"available": true, "pd_double_distribution": true, "lower_hvn": [26035, 26079.75], "upper_hvn": [26180, 26189.75], "separator": "LVN", "separator_lo": 26090, "separator_hi": 26109.75, "hvn_blocks": 2}; price at 08:10 (packet ref_price) 26271.0

DD_EDGE_PD zone 26039.75 - 26079.75 (40.00 pts, cap 40); runner 26035.0; separator 26090.0 - 26109.75; frozen 2025-10-29T08:10:00-05:00.
Rule: price above the separator, so the far distribution is the lower HVN; its near edge (up to 40 pts) is the zone, its far edge the runner.

PD = Tue Oct 28 cash 08:30-15:00 CT volume profile, 5-point rows (ours; the map's HVN/LVN bounds come from its own rows):

| row lo | volume | packet block | hand | match |
|---|---|---|---|---|
| 26025.0 | 5802 |  | | |
| 26030.0 | 10353 |  | | |
| 26035.0 | 17374 | lower HVN | | |
| 26040.0 | 17236 | lower HVN | | |
| 26045.0 | 15727 | lower HVN | | |
| 26050.0 | 12331 | lower HVN | | |
| 26055.0 | 10743 | lower HVN | | |
| 26060.0 | 13493 | lower HVN | | |
| 26065.0 | 13249 | lower HVN | | |
| 26070.0 | 15931 | lower HVN | | |
| 26075.0 | 12324 | lower HVN | | |
| 26080.0 | 8830 |  | | |
| 26085.0 | 3863 |  | | |
| 26090.0 | 4094 | separator (LVN) | | |
| 26095.0 | 2672 | separator (LVN) | | |
| 26100.0 | 3123 | separator (LVN) | | |
| 26105.0 | 5344 | separator (LVN) | | |
| 26110.0 | 5732 |  | | |
| 26115.0 | 5693 |  | | |
| 26120.0 | 8483 |  | | |
| 26125.0 | 7328 |  | | |
| 26130.0 | 8577 |  | | |
| 26135.0 | 5446 |  | | |
| 26140.0 | 4844 |  | | |
| 26145.0 | 7712 |  | | |
| 26150.0 | 6638 |  | | |
| 26155.0 | 5837 |  | | |
| 26160.0 | 4910 |  | | |
| 26165.0 | 5552 |  | | |
| 26170.0 | 6433 |  | | |
| 26175.0 | 12532 |  | | |
| 26180.0 | 16229 | upper HVN | | |
| 26185.0 | 12491 | upper HVN | | |
| 26190.0 | 7297 |  | | |
| 26195.0 | 4618 |  | | |

In the plan: decision zone PDPOC_AREA_DD_EDGE_PD_D_PDPOC_WKPOC_PDTPOC

**2025-11-03**: packet double_distribution = {"available": true, "pd_double_distribution": true, "lower_hvn": [26005, 26014.75], "upper_hvn": [26085, 26109.75], "separator": "LVN", "separator_lo": 26035, "separator_hi": 26059.75, "hvn_blocks": 3}; price at 08:10 (packet ref_price) 26213.0

DD_EDGE_PD zone 26005.0 - 26014.75 (9.75 pts, cap 40); runner 26005.0; separator 26035.0 - 26059.75; frozen 2025-11-03T08:10:00-06:00.
Rule: price above the separator, so the far distribution is the lower HVN; its near edge (up to 40 pts) is the zone, its far edge the runner.

PD = Fri Oct 31 cash 08:30-15:00 CT volume profile, 5-point rows (ours; the map's HVN/LVN bounds come from its own rows):

| row lo | volume | packet block | hand | match |
|---|---|---|---|---|
| 25995.0 | 10890 |  | | |
| 26000.0 | 11002 |  | | |
| 26005.0 | 13201 | lower HVN | | |
| 26010.0 | 14325 | lower HVN | | |
| 26015.0 | 11587 |  | | |
| 26020.0 | 8706 |  | | |
| 26025.0 | 7598 |  | | |
| 26030.0 | 7176 |  | | |
| 26035.0 | 4731 | separator (LVN) | | |
| 26040.0 | 2407 | separator (LVN) | | |
| 26045.0 | 2392 | separator (LVN) | | |
| 26050.0 | 3151 | separator (LVN) | | |
| 26055.0 | 5296 | separator (LVN) | | |
| 26060.0 | 6833 |  | | |
| 26065.0 | 7631 |  | | |
| 26070.0 | 9003 |  | | |
| 26075.0 | 7479 |  | | |
| 26080.0 | 9825 |  | | |
| 26085.0 | 15075 | upper HVN | | |
| 26090.0 | 17485 | upper HVN | | |
| 26095.0 | 17042 | upper HVN | | |
| 26100.0 | 17123 | upper HVN | | |
| 26105.0 | 14426 | upper HVN | | |
| 26110.0 | 12121 |  | | |
| 26115.0 | 9553 |  | | |

In the plan: not a decision zone (class TARGET; see research decision_zones_beyond_cap)

**2025-11-18**: packet double_distribution = {"available": true, "pd_double_distribution": true, "lower_hvn": [24780, 24794.75], "upper_hvn": [24865, 24874.75], "separator": "LVN", "separator_lo": 24810, "separator_hi": 24829.75, "hvn_blocks": 5}; price at 08:10 (packet ref_price) 24746.5

DD_EDGE_PD zone 24865.0 - 24874.75 (9.75 pts, cap 40); runner 24874.75; separator 24810.0 - 24829.75; frozen 2025-11-18T08:10:00-06:00.
Rule: price below the separator, so the far distribution is the upper HVN; its near edge (up to 40 pts) is the zone, its far edge the runner.

PD = Mon Nov 17 cash 08:30-15:00 CT volume profile, 5-point rows (ours; the map's HVN/LVN bounds come from its own rows):

| row lo | volume | packet block | hand | match |
|---|---|---|---|---|
| 24770.0 | 7547 |  | | |
| 24775.0 | 7582 |  | | |
| 24780.0 | 8556 | lower HVN | | |
| 24785.0 | 9523 | lower HVN | | |
| 24790.0 | 8018 | lower HVN | | |
| 24795.0 | 6646 |  | | |
| 24800.0 | 6771 |  | | |
| 24805.0 | 4221 |  | | |
| 24810.0 | 3069 | separator (LVN) | | |
| 24815.0 | 1885 | separator (LVN) | | |
| 24820.0 | 1886 | separator (LVN) | | |
| 24825.0 | 3693 | separator (LVN) | | |
| 24830.0 | 4206 |  | | |
| 24835.0 | 4886 |  | | |
| 24840.0 | 4254 |  | | |
| 24845.0 | 3213 |  | | |
| 24850.0 | 3012 |  | | |
| 24855.0 | 4986 |  | | |
| 24860.0 | 8345 |  | | |
| 24865.0 | 9759 | upper HVN | | |
| 24870.0 | 8518 | upper HVN | | |
| 24875.0 | 6477 |  | | |
| 24880.0 | 5822 |  | | |

In the plan: not a decision zone (class TARGET; see research decision_zones_beyond_cap)

### E2. Weekly double distribution (E23; ours: PD rule applied to weekly)

Kyron, Nov 4: the map's PD double-distribution rule and thresholds, unchanged, on the developing weekly profile (Sunday 17:00 CT reset, trades before 08:10 CT). Frozen in code (commit 31cebdb) before it was run on any day. PD and weekly DD edges are both STRUCTURE and count once in a zone. The weekly profile was rebuilt independently and matched the map's weekly high, low, VWAP, POC / VAH / VAL (volume and TPO) and weekly single prints on all these days (`weekly_dd/weekly_dd_check.md`).

**2025-10-22 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 19 17:00 to Wed Oct 22 08:10 CT (last trade used 2025-10-22T08:09:59.476763-05:00); split = no; HVN blocks 1; price at 08:10 25258.75


**2025-10-23 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 19 17:00 to Thu Oct 23 08:10 CT (last trade used 2025-10-23T08:09:59.897821-05:00); split = no; HVN blocks 1; price at 08:10 24954.0


**2025-10-24 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 19 17:00 to Fri Oct 24 08:10 CT (last trade used 2025-10-24T08:09:59.098544-05:00); split = no; HVN blocks 2; price at 08:10 25475.0


**2025-10-27 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 26 17:00 to Mon Oct 27 08:10 CT (last trade used 2025-10-27T08:09:50.922221-05:00); split = yes; HVN blocks 2; price at 08:10 25838.0

Lower HVN 25720.0 - 25734.75; separator (LVN) 25745.0 - 25754.75; upper HVN 25825.0 - 25844.75.
DD_EDGE_WK zone 25720.0 - 25734.75 (14.75 pts, cap 40); runner 25720.0; frozen 2025-10-27T08:10:00-05:00.

Weekly volume, 5-point rows; smoothed = (row below + row + row above) / 3; peak smoothed 5,463; HVN >= 70% = 3,824; LVN <= 30% = 1,639.

| row lo | volume | smoothed | % of peak | block | hand | match |
|---|---|---|---|---|---|---|
| 25710.0 | 1750 | 1,839 | 34% |  | | |
| 25715.0 | 3087 | 3,403 | 62% |  | | |
| 25720.0 | 5372 | 4,673 | 86% | lower HVN | | |
| 25725.0 | 5561 | 4,977 | 91% | lower HVN | | |
| 25730.0 | 3999 | 4,352 | 80% | lower HVN | | |
| 25735.0 | 3497 | 3,090 | 57% |  | | |
| 25740.0 | 1773 | 2,315 | 42% |  | | |
| 25745.0 | 1675 | 1,398 | 26% | separator | | |
| 25750.0 | 745 | 1,380 | 25% | separator | | |
| 25755.0 | 1720 | 1,749 | 32% |  | | |
| 25760.0 | 2782 | 2,150 | 39% |  | | |
| 25765.0 | 1949 | 2,200 | 40% |  | | |
| 25770.0 | 1869 | 2,033 | 37% |  | | |
| 25775.0 | 2281 | 2,136 | 39% |  | | |
| 25780.0 | 2258 | 2,533 | 46% |  | | |
| 25785.0 | 3060 | 3,228 | 59% |  | | |
| 25790.0 | 4366 | 3,574 | 65% |  | | |
| 25795.0 | 3297 | 3,571 | 65% |  | | |
| 25800.0 | 3051 | 2,701 | 49% |  | | |
| 25805.0 | 1755 | 2,200 | 40% |  | | |
| 25810.0 | 1793 | 1,737 | 32% |  | | |
| 25815.0 | 1664 | 1,873 | 34% |  | | |
| 25820.0 | 2162 | 2,397 | 44% |  | | |
| 25825.0 | 3366 | 4,009 | 73% | upper HVN | | |
| 25830.0 | 6499 | 5,381 | 98% | upper HVN | | |
| 25835.0 | 6277 | 5,463 | 100% | upper HVN | | |
| 25840.0 | 3613 | 3,913 | 72% | upper HVN | | |
| 25845.0 | 1850 | 1,922 | 35% |  | | |
| 25850.0 | 304 | 718 | 13% |  | | |

In the plan: decision zone D_ONL_ONVAL_WKVAL_ONTVAL_WKTVAL_ONPOC_P3_DD_EDGE_WK

**2025-10-28 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 26 17:00 to Tue Oct 28 08:10 CT (last trade used 2025-10-28T08:09:59.829965-05:00); split = no; HVN blocks 4; price at 08:10 26051.25


**2025-10-29 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 26 17:00 to Wed Oct 29 08:10 CT (last trade used 2025-10-29T08:09:58.269853-05:00); split = yes; HVN blocks 7; price at 08:10 26271.0

Lower HVN 25925.0 - 25934.75; separator (LVN) 25950.0 - 25954.75; upper HVN 25965.0 - 25974.75.
DD_EDGE_WK zone 25925.0 - 25934.75 (9.75 pts, cap 40); runner 25925.0; frozen 2025-10-29T08:10:00-05:00.

Weekly volume, 5-point rows; smoothed = (row below + row + row above) / 3; peak smoothed 19,107; HVN >= 70% = 13,375; LVN <= 30% = 5,732.

| row lo | volume | smoothed | % of peak | block | hand | match |
|---|---|---|---|---|---|---|
| 25915.0 | 2744 | 6,900 | 36% |  | | |
| 25920.0 | 8976 | 11,157 | 58% |  | | |
| 25925.0 | 21750 | 14,883 | 78% | lower HVN | | |
| 25930.0 | 13923 | 15,695 | 82% | lower HVN | | |
| 25935.0 | 11412 | 11,045 | 58% |  | | |
| 25940.0 | 7801 | 8,432 | 44% |  | | |
| 25945.0 | 6083 | 6,441 | 34% |  | | |
| 25950.0 | 5438 | 5,366 | 28% | separator | | |
| 25955.0 | 4576 | 7,989 | 42% |  | | |
| 25960.0 | 13952 | 11,804 | 62% |  | | |
| 25965.0 | 16883 | 17,190 | 90% | upper HVN | | |
| 25970.0 | 20734 | 16,392 | 86% | upper HVN | | |
| 25975.0 | 11559 | 12,504 | 65% |  | | |
| 25980.0 | 5219 | 7,212 | 38% |  | | |

In the plan: merged into T_PD2POC_WKPOC_AREA_DD_EDGE_WK, beyond the 2-per-side cap (not written)

**2025-10-30 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 26 17:00 to Thu Oct 30 08:10 CT (last trade used 2025-10-30T08:09:58.462857-05:00); split = no; HVN blocks 2; price at 08:10 26101.75


**2025-10-31 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Oct 26 17:00 to Fri Oct 31 08:10 CT (last trade used 2025-10-31T08:09:59.662455-05:00); split = no; HVN blocks 4; price at 08:10 26198.75


**2025-11-03 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Nov 02 17:00 to Mon Nov 03 08:10 CT (last trade used 2025-11-03T08:09:59.636488-06:00); split = no; HVN blocks 2; price at 08:10 26213.0


**2025-11-04 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Nov 02 17:00 to Tue Nov 04 08:10 CT (last trade used 2025-11-04T08:09:56.420580-06:00); split = no; HVN blocks 1; price at 08:10 25696.25


**2025-11-17 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Nov 16 17:00 to Mon Nov 17 08:10 CT (last trade used 2025-11-17T08:09:59.084675-06:00); split = no; HVN blocks 2; price at 08:10 25044.75


**2025-11-18 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Nov 16 17:00 to Tue Nov 18 08:10 CT (last trade used 2025-11-18T08:09:58.374681-06:00); split = yes; HVN blocks 5; price at 08:10 24746.5

Lower HVN 24865.0 - 24874.75; separator (LVN) 24925.0 - 24954.75; upper HVN 24970.0 - 24989.75.
DD_EDGE_WK zone 24970.0 - 24989.75 (19.75 pts, cap 40); runner 24989.75; frozen 2025-11-18T08:10:00-06:00.

Weekly volume, 5-point rows; smoothed = (row below + row + row above) / 3; peak smoothed 13,773; HVN >= 70% = 9,641; LVN <= 30% = 4,132.

| row lo | volume | smoothed | % of peak | block | hand | match |
|---|---|---|---|---|---|---|
| 24855.0 | 5844 | 6,344 | 46% |  | | |
| 24860.0 | 9177 | 8,708 | 63% |  | | |
| 24865.0 | 11103 | 10,108 | 73% | lower HVN | | |
| 24870.0 | 10044 | 9,836 | 71% | lower HVN | | |
| 24875.0 | 8362 | 8,761 | 64% |  | | |
| 24880.0 | 7877 | 7,641 | 55% |  | | |
| 24885.0 | 6684 | 7,206 | 52% |  | | |
| 24890.0 | 7057 | 7,394 | 54% |  | | |
| 24895.0 | 8442 | 7,565 | 55% |  | | |
| 24900.0 | 7197 | 7,261 | 53% |  | | |
| 24905.0 | 6145 | 5,958 | 43% |  | | |
| 24910.0 | 4531 | 5,127 | 37% |  | | |
| 24915.0 | 4704 | 4,323 | 31% |  | | |
| 24920.0 | 3733 | 4,215 | 31% |  | | |
| 24925.0 | 4207 | 3,927 | 29% | separator | | |
| 24930.0 | 3842 | 3,667 | 27% | separator | | |
| 24935.0 | 2952 | 2,895 | 21% | separator | | |
| 24940.0 | 1891 | 2,288 | 17% | separator | | |
| 24945.0 | 2022 | 2,430 | 18% | separator | | |
| 24950.0 | 3378 | 3,073 | 22% | separator | | |
| 24955.0 | 3818 | 4,313 | 31% |  | | |
| 24960.0 | 5744 | 6,406 | 47% |  | | |
| 24965.0 | 9655 | 8,874 | 64% |  | | |
| 24970.0 | 11224 | 10,385 | 75% | upper HVN | | |
| 24975.0 | 10275 | 10,920 | 79% | upper HVN | | |
| 24980.0 | 11261 | 10,974 | 80% | upper HVN | | |
| 24985.0 | 11386 | 9,979 | 72% | upper HVN | | |
| 24990.0 | 7290 | 9,048 | 66% |  | | |
| 24995.0 | 8467 | 7,277 | 53% |  | | |

In the plan: merged into D_PDVAL_PDTVAL_ONH_REJ_LOW_PD_DD_EDGE_WK, beyond the 2-per-side cap (not written)

**2025-11-19 weekly** (ours: PD rule applied to weekly, weekly-dd-v1.1): profile Sun Nov 16 17:00 to Wed Nov 19 08:10 CT (last trade used 2025-11-19T08:09:59.647644-06:00); split = no; HVN blocks 3; price at 08:10 24630.75


