# Hand check 2025-11-04 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 26075.0 | 26115.0 | | | peak row 26090.0 | | | | 2025-11-04T08:10:00-06:00 | | |
| MAP4 PDPOC_AREA | 26085.0 | 26110.0 | | | peak row 26095.0 | | | | 2025-11-04T08:10:00-06:00 | | |
| MAP4 ONPOC_AREA | 25737.5 | 25777.5 | | | peak row 25755.0 | | | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 25755.0 | 25765.0 | | | SELL WK | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 26020.0 | 26030.0 | | | SELL WK | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 26080.0 | 26095.0 | | | SELL WK | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 26105.0 | 26115.0 | | | BUY WK | | role=TAG_ONLY | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 26135.0 | 26145.0 | | | SELL WK | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 26150.0 | 26160.0 | | | BUY WK | | role=TAG_ONLY | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_PD | 26080.0 | 26095.0 | | | SELL PD | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 26105.0 | 26115.0 | | | BUY PD | | role=TAG_ONLY | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 25755.0 | 25770.0 | | | SELL ON | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 25985.0 | 25995.0 | | | SELL ON | | role=TARGET | | 2025-11-04T08:10:00-06:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| ONPOC_AREA_T_ONPOC_ONTPOC | 25737.5 | 25777.5 | 2\|DELTA,VOLUME | 5\|ONPOC,ONTPOC,T_DELTA_SELL_WK,T_DELTA_SELL_ON,ONPOC_AREA | DECISION | | |
| T_PD2L | 25883.75 | 25893.75 | 2\|STRUCTURE,VWAP | 2\|PD2L,WKVWAP_SD1_DN | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BULLISH | | |
| draw | 25737.50-25777.50|ONPOC_AREA | | |
| draw_status | ACTIVE | | |
| balance |  | | |
| balance_poc |  | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_SHORT | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 25807.95 | | |
| wkvwap_0810 | 26042.55 | | |
| wkval_state | accept=BELOW|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| ONPOC_AREA_T_ONPOC_ONTPOC | ANY | INITIATION | YES |  | {"long": {"TP1": "25813.25-25823.25", "TP2": "25985.00-25995.00", "RUN": "26184.00-26194.00", "R_TP1": "0.88", "R_TP2": "5.12", "R_RUN": "10.04"}, "short": {"TP1": "25660.00-25670.00", "TP2": "", "RUN": "", "R_TP1": "1.67", "R_TP2": "", "R_RUN": ""}} |
| T_PD2L | ANY | INITIATION | YES |  | {"long": {"TP1": "25919.75-25929.75", "TP2": "25985.00-25995.00", "RUN": "26184.00-26194.00", "R_TP1": "2.48", "R_TP2": "8.69", "R_RUN": "27.64"}, "short": {"TP1": "25813.25-25823.25", "TP2": "25737.50-25777.50", "RUN": "25737.50-25777.50", "R_TP1": "5.76", "R_TP2": "10.12", "R_RUN": "10.12"}} |

review=APPROVED; fails=[]; notes=[]
