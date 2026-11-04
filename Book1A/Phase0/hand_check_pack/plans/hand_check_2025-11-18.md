# Hand check 2025-11-18 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REJ_LOW | 24955.0 | 24995.0 | PD | 2025-11-17T08:31:00-06:00 | DELTA:-199 | 229.5 |  | TARGET | 2025-11-18T08:10:00-06:00 | | |
| REJ_HIGH | 25010.75 | 25050.75 | PD | 2025-11-17T12:49:00-06:00 | DELTA:268 | 164.0 |  | TARGET | 2025-11-18T08:10:00-06:00 | | |
| MAP4 WKPOC_AREA | 25130.0 | 25155.0 | | | peak row 25145.0 | | | | 2025-11-18T08:10:00-06:00 | | |
| MAP4 PDPOC_AREA | 25130.0 | 25155.0 | | | peak row 25145.0 | | | | 2025-11-18T08:10:00-06:00 | | |
| MAP4 ONPOC_AREA | 24715.0 | 24755.0 | | | peak row 24740.0 | | | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 24775.0 | 24790.0 | | | SELL WK | | role=TARGET | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 24820.0 | 24845.0 | | | SELL WK | | role=TARGET | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 25245.0 | 25255.0 | | | BUY WK | | role=TAG_ONLY | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_PD | 24775.0 | 24790.0 | | | SELL PD | | role=TARGET | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 25150.0 | 25160.0 | | | BUY PD | | role=TAG_ONLY | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_ON | 24650.0 | 24660.0 | | | BUY ON | | role=TARGET | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 24700.0 | 24720.0 | | | SELL ON | | role=TAG_ONLY | | 2025-11-18T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 24820.0 | 24845.0 | | | SELL ON | | role=TARGET | | 2025-11-18T08:10:00-06:00 | | |
| DD_EDGE | 24865.0 | 24874.75 | | | runner 24874.75 | | | | 2025-11-18T08:10:00-06:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| T_ONL | 24598.75 | 24608.75 | 2\|STRUCTURE,GEX | 2\|ONL,PS_0DTE | DECISION | | |
| T_ONTVAL_ONVAL | 24665.0 | 24685.5 | 2\|AUCTION_VALUE,DELTA | 3\|ONVAL,ONTVAL,T_DELTA_BUY_ON | DECISION | | |
| ONPOC_AREA_D_PDL_ONTPOC_ONPOC | 24715.0 | 24755.0 | 3\|STRUCTURE,DELTA,VOLUME | 5\|PDL,ONPOC,ONTPOC,T_DELTA_SELL_ON,ONPOC_AREA | DECISION | | |
| T_HTFPOC | 24822.5 | 24832.5 | 2\|DELTA,VOLUME | 3\|HTFPOC,T_DELTA_SELL_WK,T_DELTA_SELL_ON | DECISION | | |
| D_ONVAH_WKVAL_ONTVAH | 24846.25 | 24864.75 | 3\|AUCTION_VALUE,DELTA,VWAP | 7\|ONVAH,ONTVAH,VWAPU1,WKVAL,VWAP_SD1_UP,T_DELTA_SELL_WK,T_DELTA_SELL_ON | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | NONE | | |
| draw |  | | |
| draw_status | NONE | | |
| balance |  | | |
| balance_poc |  | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_SHORT | | |
| htf_structure | BALANCE | | |
| gex_regime | NEG | | |
| vwap_0810 | 24774.35 | | |
| wkvwap_0810 | 24989.77 | | |
| wkval_state | accept=BELOW|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| T_ONL | ANY | ANY | YES |  | {"long": {"TP1": "24955.00-24995.00", "TP2": "25130.00-25155.00", "RUN": "25280.25-25290.25", "R_TP1": "32.98", "R_TP2": "49.64", "R_RUN": "63.95"}, "short": {"TP1": "24425.00-24435.00", "TP2": "", "RUN": "", "R_TP1": "15.60", "R_TP2": "", "R_RUN": ""}} |
| T_ONTVAL_ONVAL | ANY | ANY | YES |  | {"long": {"TP1": "24955.00-24995.00", "TP2": "25130.00-25155.00", "RUN": "25280.25-25290.25", "R_TP1": "12.83", "R_TP2": "21.17", "R_RUN": "28.32"}, "short": {"TP1": "24425.00-24435.00", "TP2": "", "RUN": "", "R_TP1": "10.95", "R_TP2": "", "R_RUN": ""}} |
| ONPOC_AREA_D_PDL_ONTPOC_ONPOC | ANY | ANY | YES |  | {"long": {"TP1": "24955.00-24995.00", "TP2": "25130.00-25155.00", "RUN": "25280.25-25290.25", "R_TP1": "4.94", "R_TP2": "9.26", "R_RUN": "12.97"}, "short": {"TP1": "24675.50-24685.50", "TP2": "24650.00-24660.00", "RUN": "", "R_TP1": "0.73", "R_TP2": "1.36", "R_RUN": ""}} |
| T_HTFPOC | ANY | ANY | YES |  | {"long": {"TP1": "24955.00-24995.00", "TP2": "25130.00-25155.00", "RUN": "25280.25-25290.25", "R_TP1": "11.67", "R_TP2": "28.33", "R_RUN": "42.64"}, "short": {"TP1": "24745.00-24755.00", "TP2": "24700.00-24720.00", "RUN": "", "R_TP1": "6.43", "R_TP2": "9.76", "R_RUN": ""}} |
| D_ONVAH_WKVAL_ONTVAH | INITIATION | ANY | YES | side_conflict=D_ONVAH_WKVAL_ONTVAH|long|context=ANY,accepted_edge=INITIATION | {"long": {"TP1": "24955.00-24995.00", "TP2": "25130.00-25155.00", "RUN": "25280.25-25290.25", "R_TP1": "4.75", "R_TP2": "13.96", "R_RUN": "21.87"}, "short": {"TP1": "24822.50-24832.50", "TP2": "24775.00-24790.00", "RUN": "", "R_TP1": "0.72", "R_TP2": "2.96", "R_RUN": ""}} |

review=APPROVED; fails=[]; notes=[]
