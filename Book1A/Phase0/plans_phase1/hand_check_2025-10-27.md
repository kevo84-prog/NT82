# Hand check 2025-10-27 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 25830.0 | 25840.0 | | | peak row 25830.0 | | | | 2025-10-27T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 25530.0 | 25555.0 | | | peak row 25535.0 | | | | 2025-10-27T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 25830.0 | 25840.0 | | | peak row 25830.0 | | | | 2025-10-27T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25730.0 | 25745.0 | | | BUY WK | | role=TARGET | | 2025-10-27T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25795.0 | 25805.0 | | | BUY WK | | role=TARGET | | 2025-10-27T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 25550.0 | 25560.0 | | | BUY PD | | role=TARGET | | 2025-10-27T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 25730.0 | 25745.0 | | | BUY ON | | role=TARGET | | 2025-10-27T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 25795.0 | 25805.0 | | | BUY ON | | role=TARGET | | 2025-10-27T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| D_ONL_ONVAL_WKVAL_ONTVAL_WKTVAL_ONPOC_P3_DD_EDGE_WK | 25695.0 | 25734.75 | 5\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,VWAP | 12\|ONPOC,ONVAL,ONTPOC,ONTVAL,ONL,VWAPL1,WKPOC,WKVAL,VWAP_SD1_DN,WKVWAP_SD1_DN,T_DELTA_BUY_WK,T_DELTA_BUY_ON | DECISION | | |
| D_ONTVAH_WKTVAH_ONVAH_WKVAH | 25799.75 | 25822.25 | 3\|AUCTION_VALUE,DELTA,VWAP | 8\|ONVAH,ONTVAH,VWAPU1,WKVAH,VWAP_SD1_UP,WKVWAP_SD1_UP,T_DELTA_BUY_WK,T_DELTA_BUY_ON | DECISION | | |
| WKPOC_AREA_ONPOC_AREA | 25830.0 | 25840.0 | 2\|VOLUME,VWAP | 5\|VWAPU1,VWAP_SD1_UP,WKVWAP_SD1_UP,WKPOC_AREA,ONPOC_AREA | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | NONE | | |
| draw |  | | |
| draw_status | NONE | | |
| balance |  | | |
| balance_poc |  | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_LONG | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 25781.15 | | |
| wkvwap_0810 | 25781.15 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=ABOVE|failed_reclaim=1 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| D_ONL_ONVAL_WKVAL_ONTVAL_WKTVAL_ONPOC_P3_DD_EDGE_WK | ANY | INITIATION | YES | side_conflict=D_ONL_ONVAL_WKVAL_ONTVAL_WKTVAL_ONPOC_P3_DD_EDGE_WK|short|context=ANY,dd_edge=INITIATION,edge_control=INITIATION | {"long": {"TP1": "25799.75-25809.75", "TP2": "25830.00-25840.00", "RUN": "25812.25-25822.25", "R_TP1": "1.61", "R_TP2": "2.37", "R_RUN": "1.93"}, "short": {"TP1": "25552.50-25562.50", "TP2": "", "RUN": "25498.25-25508.25", "R_TP1": "3.29", "R_TP2": "", "R_RUN": "4.64"}} |
| D_ONTVAH_WKTVAH_ONVAH_WKVAH | ANY | INITIATION | YES | side_conflict=D_ONTVAH_WKTVAH_ONVAH_WKVAH|short|context=ANY,accepted_edge=INITIATION,edge_control=INITIATION | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25722.50-25732.50", "TP2": "25550.00-25560.00", "RUN": "25700.00-25710.00", "R_TP1": "2.92", "R_TP2": "10.42", "R_RUN": "3.90"}} |
| WKPOC_AREA_ONPOC_AREA | ANY | ANY | YES |  | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25812.25-25822.25", "TP2": "25795.00-25805.00", "RUN": "25700.00-25710.00", "R_TP1": "0.74", "R_TP2": "2.38", "R_RUN": "11.43"}} |

review=APPROVED; fails=[]; notes=[]
