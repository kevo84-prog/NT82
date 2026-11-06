# Hand check 2025-11-17 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 25220.0 | 25255.0 | | | peak row 25240.0 | | | | 2025-11-17T08:10:00-06:00 | | |
| MAP4 PDPOC_AREA | 25130.0 | 25165.0 | | | peak row 25150.0 | | | | 2025-11-17T08:10:00-06:00 | | |
| MAP4 ONPOC_AREA | 25220.0 | 25255.0 | | | peak row 25240.0 | | | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 25215.0 | 25225.0 | | | SELL WK | | role=TARGET | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 25310.0 | 25320.0 | | | SELL WK | | role=TARGET | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 24875.0 | 24885.0 | | | BUY PD | | role=TARGET | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_PD | 25000.0 | 25010.0 | | | SELL PD | | role=TAG_ONLY | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_PD | 25120.0 | 25130.0 | | | SELL PD | | role=TARGET | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 25175.0 | 25185.0 | | | BUY PD | | role=TAG_ONLY | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 25240.0 | 25270.0 | | | BUY PD | | role=TAG_ONLY | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 25215.0 | 25225.0 | | | SELL ON | | role=TARGET | | 2025-11-17T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 25310.0 | 25320.0 | | | SELL ON | | role=TARGET | | 2025-11-17T08:10:00-06:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| T_PDVAL | 24973.5 | 24983.5 | 2\|AUCTION_VALUE,GEX | 2\|PDVAL,HVL | DECISION | | |
| D_PD2L_PD2VAL_ONL_PD2TVAL_PDTVAL | 24997.5 | 25020.0 | 2\|STRUCTURE,DELTA | 3\|PD2L,ONL,T_DELTA_SELL_PD | DECISION | | |
| D_ONTVAL_WKTVAL | 25105.0 | 25115.0 | 4\|AUCTION_VALUE,DELTA,GEX,VWAP | 6\|ONTVAL,VWAPL1,VWAP_SD1_DN,WKVWAP_SD1_DN,HVL_0DTE,T_DELTA_SELL_PD | DECISION | | |
| PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL | 25130.0 | 25183.5 | 4\|AUCTION_VALUE,DELTA,VOLUME,GEX | 7\|PDPOC,PDTPOC,PWKVAL,HVL_0DTE,T_DELTA_SELL_PD,T_DELTA_BUY_PD,PDPOC_AREA | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BALANCED | | |
| draw |  | | |
| draw_status | NONE | | |
| balance | 25012.75-25284.50 | | |
| balance_poc | 25200.00 | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_SHORT | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 25197.20 | | |
| wkvwap_0810 | 25197.20 | | |
| wkval_state | accept=TESTING|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| T_PDVAL | ANY | ANY | YES |  | {"long": {"TP1": "25072.75-25082.75", "TP2": "25120.00-25130.00", "RUN": "25288.25-25298.25", "R_TP1": "8.50", "R_TP2": "13.00", "R_RUN": "29.02"}, "short": {"TP1": "24822.50-24832.50", "TP2": "", "RUN": "", "R_TP1": "13.43", "R_TP2": "", "R_RUN": ""}} |
| D_PD2L_PD2VAL_ONL_PD2TVAL_PDTVAL | ANY | ANY | YES |  | {"long": {"TP1": "25072.75-25082.75", "TP2": "25120.00-25130.00", "RUN": "25288.25-25298.25", "R_TP1": "2.29", "R_TP2": "4.35", "R_RUN": "11.66"}, "short": {"TP1": "24973.50-24983.50", "TP2": "24875.00-24885.00", "RUN": "24973.50-24983.50", "R_TP1": "0.61", "R_TP2": "4.89", "R_RUN": "0.61"}} |
| D_ONTVAL_WKTVAL | ANY | ANY | YES |  | {"long": {"TP1": "25145.00-25155.00", "TP2": "25175.00-25185.00", "RUN": "25288.25-25298.25", "R_TP1": "2.86", "R_TP2": "5.71", "R_RUN": "16.50"}, "short": {"TP1": "25072.75-25082.75", "TP2": "25000.00-25010.00", "RUN": "25072.75-25082.75", "R_TP1": "2.12", "R_TP2": "9.05", "R_RUN": "2.12"}} |
| PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL | NONE | NONE | YES |  | {} |

review=APPROVED; fails=[]; notes=['C: PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL long NONE: 1 NQ does not fit $1000 (stop 216 ticks)', 'C: PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL short NONE: 1 NQ does not fit $1000 (stop 216 ticks)']
