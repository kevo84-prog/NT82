# Hand check 2025-10-22 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 25300.0 | 25320.0 | | | peak row 25315.0 | | | | 2025-10-22T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 25292.5 | 25332.5 | | | peak row 25310.0 | | | | 2025-10-22T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 25245.0 | 25265.0 | | | peak row 25250.0 | | | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25215.0 | 25225.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25270.0 | 25280.0 | | | SELL WK | | role=TARGET | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25295.0 | 25315.0 | | | SELL WK | | role=TARGET | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25315.0 | 25355.0 | | | BUY WK | | role=TAG_ONLY | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25215.0 | 25225.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25270.0 | 25280.0 | | | SELL PD | | role=TARGET | | 2025-10-22T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_ON | 25225.0 | 25240.0 | | | SELL ON | | role=TAG_ONLY | | 2025-10-22T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA | 25198.25 | 25265.0 | 6\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,GEX,VWAP | 21\|PDVAL,PDL,ONPOC,ONVAL,ONTPOC,ONTVAL,ONL,VWAP,VWAPL1,WKVAL,VWAP,VWAP_SD1_DN,WKVWAP,HVL,HVL_0DTE,T_DELTA_SELL_WK,T_DELTA_SELL_WK,T_DELTA_SELL_PD,T_DELTA_SELL_PD,T_DELTA_SELL_ON,ONPOC_AREA | DECISION | | |
| D_PDVAH_ONH_WKVAH_PDH_PD2VAH_PD2H_P2 | 25325.5 | 25364.75 | 5\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,VWAP | 8\|PDVAH,PDH,PD2H,ONH,WKVAH,WKVWAP_SD1_UP,T_DELTA_BUY_WK,PDPOC_AREA | DECISION | | |
| T_HTFVAH | 25389.75 | 25399.75 | 2\|AUCTION_VALUE,GEX | 3\|HTFVAH,CR,CR_0DTE | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BALANCED | | |
| draw |  | | |
| draw_status | NONE | | |
| balance | 25256-25340.5 | | |
| balance_poc | 25318 | | |
| value_follows | DIVERGENT_UP | | |
| on_inventory | NET_SHORT | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 25267.38 | | |
| wkvwap_0810 | 25262.44 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA | NONE | NONE | YES |  | {} |
| D_PDVAH_ONH_WKVAH_PDH_PD2VAH_PD2H_P2 | INITIATION | ANY | YES | side_conflict=D_PDVAH_ONH_WKVAH_PDH_PD2VAH_PD2H_P2|long|context=ANY,edge_control=ANY,value_follows=INITIATION | {"long": {"TP1": "25389.75-25399.75", "TP2": "", "RUN": "", "R_TP1": "0.63", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25299.75-25309.75", "TP2": "25270.00-25280.00", "RUN": "25239.25-25249.25", "R_TP1": "0.40", "R_TP2": "1.14", "R_RUN": "1.92"}} |
| T_HTFVAH | ANY | ANY | YES |  | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25335.50-25345.50", "TP2": "25292.50-25332.50", "RUN": "25239.25-25249.25", "R_TP1": "4.21", "R_TP2": "5.45", "R_RUN": "13.38"}} |

review=APPROVED; fails=[]; notes=['Z3: D_PD2TVAL_ONTPOC_PD2VAL_ONVAH_PDSET_WKTPOC_P7 at the balance POC: TARGET only', 'Z3: WKPOC_AREA at the balance POC: TARGET only', 'Z3: PDPOC_AREA at the balance POC: TARGET only', 'C: D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA long NONE: 1 NQ does not fit $1000 (stop 269 ticks)', 'C: D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA short NONE: 1 NQ does not fit $1000 (stop 269 ticks)']
