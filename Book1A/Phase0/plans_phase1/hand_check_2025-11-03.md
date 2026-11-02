# Hand check 2025-11-03 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REJ_HIGH | 26118.0 | 26158.0 | PD | 2025-10-31T10:46:00-05:00 | DELTA:495 | 102.0 | VWAP|DELTA_BUY | TARGET | 2025-11-03T08:10:00-06:00 | | |
| MAP4 WKPOC_AREA | 26065.0 | 26095.0 | | | peak row 26070.0 | | | | 2025-11-03T08:10:00-06:00 | | |
| MAP4 PDPOC_AREA | 26085.0 | 26110.0 | | | peak row 26090.0 | | | | 2025-11-03T08:10:00-06:00 | | |
| MAP4 ONPOC_AREA | 26065.0 | 26095.0 | | | peak row 26070.0 | | | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 26110.0 | 26125.0 | | | BUY WK | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 26160.0 | 26170.0 | | | BUY WK | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 26180.0 | 26190.0 | | | BUY WK | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_PD | 26060.0 | 26070.0 | | | SELL PD | | role=TAG_ONLY | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_PD | 26085.0 | 26095.0 | | | SELL PD | | role=TAG_ONLY | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 26110.0 | 26120.0 | | | BUY PD | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_ON | 26110.0 | 26125.0 | | | BUY ON | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_ON | 26160.0 | 26170.0 | | | BUY ON | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_ON | 26180.0 | 26190.0 | | | BUY ON | | role=TARGET | | 2025-11-03T08:10:00-06:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| D_ONVAL_WKVAL | 26061.75 | 26071.75 | 4\|AUCTION_VALUE,DELTA,VOLUME,VWAP | 8\|ONVAL,VWAPL1,WKVAL,VWAP_SD1_DN,WKVWAP_SD1_DN,T_DELTA_SELL_PD,WKPOC_AREA,ONPOC_AREA | DECISION | | |
| REJ_HIGH_PD_T_PDTVAH_D_ONTVAH_WKTVAH_ONPOC_WKPOC | 26118.0 | 26160.0 | 5\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,VWAP | 11\|ONPOC,ONTVAH,VWAP,WKPOC,VWAP,WKVWAP,T_DELTA_BUY_WK,T_DELTA_BUY_WK,T_DELTA_BUY_PD,T_DELTA_BUY_ON,T_DELTA_BUY_ON | DECISION | | |
| D_PWKTPOC_PD2H_PDVAH_ONVAH_WKVAH_PDH_P2 | 26172.5 | 26215.0 | 4\|AUCTION_VALUE,STRUCTURE,DELTA,VWAP | 12\|PDVAH,PDH,PD2H,ONVAH,VWAPU1,WKVAH,VWAP_SD1_UP,WKVWAP_SD1_UP,T_DELTA_BUY_WK,T_DELTA_BUY_WK,T_DELTA_BUY_ON,T_DELTA_BUY_ON | DECISION | | |
| D_ONH_PWKVAH_PD3POC | 26254.75 | 26280.0 | 2\|AUCTION_VALUE,STRUCTURE | 2\|ONH,PWKVAH | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BALANCED | | |
| draw |  | | |
| draw_status | NONE | | |
| balance | 25964.5-26126.8 | | |
| balance_poc | 26090 | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_LONG | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 26122.22 | | |
| wkvwap_0810 | 26122.22 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=TESTING|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| D_ONVAL_WKVAL | ANY | ANY | YES |  | {"long": {"TP1": "26118.00-26158.00", "TP2": "26160.00-26170.00", "RUN": "26185.75-26195.75", "R_TP1": "4.40", "R_TP2": "8.40", "R_RUN": "10.86"}, "short": {"TP1": "26015.00-26025.00", "TP2": "", "RUN": "25995.75-26005.75", "R_TP1": "3.50", "R_TP2": "", "R_RUN": "5.33"}} |
| REJ_HIGH_PD_T_PDTVAH_D_ONTVAH_WKTVAH_ONPOC_WKPOC | ANY | INITIATION | YES | side_conflict=REJ_HIGH_PD_T_PDTVAH_D_ONTVAH_WKTVAH_ONPOC_WKPOC|short|context=ANY,edge_control=INITIATION | {"long": {"TP1": "26179.00-26189.00", "TP2": "", "RUN": "26185.75-26195.75", "R_TP1": "0.45", "R_TP2": "", "R_RUN": "0.61"}, "short": {"TP1": "26095.00-26105.00", "TP2": "26060.00-26070.00", "RUN": "26061.75-26071.75", "R_TP1": "0.31", "R_TP2": "1.13", "R_RUN": "1.09"}} |
| D_PWKTPOC_PD2H_PDVAH_ONVAH_WKVAH_PDH_P2 | ANY | INITIATION | YES | side_conflict=D_PWKTPOC_PD2H_PDVAH_ONVAH_WKVAH_PDH_P2|short|context=ANY,edge_control=INITIATION | {"long": {"TP1": "26255.00-26265.00", "TP2": "", "RUN": "", "R_TP1": "0.93", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "26118.00-26158.00", "TP2": "26085.00-26110.00", "RUN": "26061.75-26071.75", "R_TP1": "0.34", "R_TP2": "1.45", "R_RUN": "2.34"}} |
| D_ONH_PWKVAH_PD3POC | INITIATION | ANY | YES | side_conflict=D_ONH_PWKVAH_PD3POC|long|context=ANY,tests4=INITIATION | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "26118.00-26158.00", "TP2": "26085.00-26110.00", "RUN": "26061.75-26071.75", "R_TP1": "3.76", "R_TP2": "5.62", "R_RUN": "7.11"}} |

review=APPROVED; fails=[]; notes=['Z3: D_ONTPOC_WKTPOC_PD2VAH_PD2TVAH_PDPOC_PWKPOC at the balance POC: TARGET only', 'Z3: WKPOC_AREA at the balance POC: TARGET only', 'Z3: PDPOC_AREA at the balance POC: TARGET only', 'Z3: ONPOC_AREA at the balance POC: TARGET only']
