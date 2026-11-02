# Hand check 2025-10-30 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REJ_HIGH | 26188.0 | 26228.0 | PD | 2025-10-29T13:56:00-05:00 | DELTA:223 | 116.25 | DELTA_SELL | TARGET | 2025-10-30T08:10:00-05:00 | | |
| REJ_HIGH | 26266.5 | 26306.5 | ON | 2025-10-29T23:38:00-05:00 | DELTA:387 | 234.25 | DELTA_BUY | TARGET | 2025-10-30T08:10:00-05:00 | | |
| REJ_LOW | 26049.25 | 26089.25 | PD | 2025-10-29T13:42:00-05:00 | IMB | 145.75 | DELTA_SELL | TARGET | 2025-10-30T08:10:00-05:00 | | |
| MAP4 WKPOC_AREA | 26252.5 | 26292.5 | | | peak row 26270.0 | | | | 2025-10-30T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 26240.0 | 26280.0 | | | peak row 26270.0 | | | | 2025-10-30T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 26222.5 | 26262.5 | | | peak row 26240.0 | | | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25885.0 | 25895.0 | | | BUY WK | | role=TARGET | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25895.0 | 25905.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25930.0 | 25940.0 | | | BUY WK | | role=TARGET | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25965.0 | 25975.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25975.0 | 25985.0 | | | BUY WK | | role=TARGET | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 26230.0 | 26240.0 | | | SELL WK | | role=TARGET | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 26275.0 | 26300.0 | | | BUY WK | | role=TAG_ONLY | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 26220.0 | 26240.0 | | | SELL PD | | role=TARGET | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 26275.0 | 26290.0 | | | BUY PD | | role=TAG_ONLY | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_ON | 26085.0 | 26095.0 | | | SELL ON | | role=TAG_ONLY | | 2025-10-30T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_ON | 26175.0 | 26190.0 | | | SELL ON | | role=TARGET | | 2025-10-30T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| D_PD3VAH_PD3H_WKVAL_WKTVAL | 25975.5 | 25990.0 | 3\|AUCTION_VALUE,STRUCTURE,DELTA | 4\|PD3H,WKVAL,T_DELTA_SELL_WK,T_DELTA_BUY_WK | DECISION | | |
| REJ_LOW_PD_T_ONL | 26049.25 | 26089.25 | 2\|STRUCTURE,DELTA | 3\|PDL,ONL,T_DELTA_SELL_ON | DECISION | | |
| D_ONVAL_PD2TVAH | 26165.0 | 26179.75 | 4\|AUCTION_VALUE,DELTA,GEX,VWAP | 5\|ONVAL,VWAPL1,VWAP_SD1_DN,HVL_0DTE,T_DELTA_SELL_ON | DECISION | | |
| D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON | 26185.0 | 26262.5 | 6\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,GEX,VWAP | 16\|PDVAL,PDTPOC,PD2H,ONPOC,ONTPOC,ONTVAL,VWAP,VWAP,WKVWAP_SD1_UP,HVL_0DTE,T_DELTA_SELL_WK,T_DELTA_SELL_PD,T_DELTA_SELL_ON,WKPOC_AREA,PDPOC_AREA,ONPOC_AREA | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BALANCED | | |
| draw |  | | |
| draw_status | NONE | | |
| balance | 26195.5-26297.5 | | |
| balance_poc | 26275 | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_SHORT | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 26233.37 | | |
| wkvwap_0810 | 26097.38 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| D_PD3VAH_PD3H_WKVAL_WKTVAL | ANY | INITIATION | YES | side_conflict=D_PD3VAH_PD3H_WKVAL_WKTVAL|short|context=ANY,edge_control=INITIATION | {"long": {"TP1": "26049.25-26089.25", "TP2": "26175.00-26190.00", "RUN": "26320.00-26330.00", "R_TP1": "3.95", "R_TP2": "12.33", "R_RUN": "22.00"}, "short": {"TP1": "25389.75-25399.75", "TP2": "", "RUN": "", "R_TP1": "38.38", "R_TP2": "", "R_RUN": ""}} |
| REJ_LOW_PD_T_ONL | ANY | ANY | YES |  | {"long": {"TP1": "26188.00-26228.00", "TP2": "26230.00-26240.00", "RUN": "26320.00-26330.00", "R_TP1": "2.44", "R_TP2": "3.48", "R_RUN": "5.70"}, "short": {"TP1": "25977.50-25987.50", "TP2": "25965.00-25975.00", "RUN": "25977.50-25987.50", "R_TP1": "1.52", "R_TP2": "1.83", "R_RUN": "1.52"}} |
| D_ONVAL_PD2TVAH | INITIATION | ANY | YES | side_conflict=D_ONVAL_PD2TVAH|long|context=ANY,edge_control=INITIATION | {"long": {"TP1": "26188.00-26228.00", "TP2": "26230.00-26240.00", "RUN": "26320.00-26330.00", "R_TP1": "0.54", "R_TP2": "3.30", "R_RUN": "9.20"}, "short": {"TP1": "26049.25-26089.25", "TP2": "25975.00-25985.00", "RUN": "25977.50-25987.50", "R_TP1": "4.97", "R_TP2": "11.80", "R_RUN": "11.64"}} |
| D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON | NONE | NONE | YES | side_conflict=D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON|long|context=ANY,edge_control=INITIATION | {} |

review=APPROVED; fails=[]; notes=['Z3: D_PDSET_WKPOC_PDPOC at the balance POC: TARGET only', 'Z3: WKPOC_AREA at the balance POC: TARGET only', 'Z3: PDPOC_AREA at the balance POC: TARGET only', 'C: D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON long NONE: 1 NQ does not fit $1000 (stop 312 ticks)', 'C: D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON short NONE: 1 NQ does not fit $1000 (stop 312 ticks)']
