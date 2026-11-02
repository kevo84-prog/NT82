# Hand check 2025-10-31 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REJ_HIGH | 26266.5 | 26306.5 | WK | 2025-10-29T23:38:00-05:00 | DELTA:387 | 234.25 | DELTA_BUY | TARGET | 2025-10-31T08:10:00-05:00 | | |
| REJ_HIGH | 26339.75 | 26379.75 | WK | 2025-10-29T15:03:00-05:00 | DELTA:742 | 220.0 |  | TARGET | 2025-10-31T08:10:00-05:00 | | |
| REJ_HIGH | 26142.5 | 26182.5 | PD | 2025-10-30T09:01:00-05:00 | IMB | 114.0 |  | TARGET | 2025-10-31T08:10:00-05:00 | | |
| REJ_LOW | 26049.25 | 26089.25 | WK | 2025-10-29T13:42:00-05:00 | IMB | 145.75 | DELTA_BUY|DELTA_SELL | TARGET | 2025-10-31T08:10:00-05:00 | | |
| MAP4 WKPOC_AREA | 26252.5 | 26292.5 | | | peak row 26270.0 | | | | 2025-10-31T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 26040.0 | 26070.0 | | | peak row 26060.0 | | | | 2025-10-31T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 26175.0 | 26200.0 | | | peak row 26190.0 | | | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25930.0 | 25940.0 | | | BUY WK | | role=TARGET | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 26070.0 | 26080.0 | | | BUY WK | | role=TARGET | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 26230.0 | 26240.0 | | | SELL WK | | role=TARGET | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 26275.0 | 26290.0 | | | BUY WK | | role=TAG_ONLY | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25945.0 | 25955.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25975.0 | 25985.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 26040.0 | 26050.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-31T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 26200.0 | 26215.0 | | | BUY ON | | role=TAG_ONLY | | 2025-10-31T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| D_WKVAL_PDVAL_PDPOC_WKPOC_PDTVAL | 25952.25 | 25980.0 | 3\|AUCTION_VALUE,DELTA,VOLUME | 6\|PDPOC,PDVAL,WKPOC,WKVAL,T_DELTA_SELL_PD,T_DELTA_SELL_PD | DECISION | | |
| D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ | 25995.0 | 26099.75 | 6\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,GEX,VWAP | 9\|PDVAH,PDTPOC,PD2L,PD3L,WKVWAP,CR,T_DELTA_BUY_WK,T_DELTA_SELL_PD,PDPOC_AREA | DECISION | | |
| REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC | 26142.5 | 26236.5 | 6\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,GEX,VWAP | 19\|PDH,PD3H,ONVAH,ONPOC,ONVAL,ONTVAH,ONTPOC,ONTVAL,VWAP,VWAPU1,VWAPL1,VWAP,VWAP_SD1_UP,VWAP_SD1_DN,WKVWAP_SD1_UP,CR_0DTE,T_DELTA_SELL_WK,T_DELTA_BUY_ON,ONPOC_AREA | DECISION | | |
| T_PD2TPOC | 26237.5 | 26247.5 | 2\|DELTA,VOLUME | 2\|T_DELTA_SELL_WK,WKPOC_AREA | DECISION | | |
| WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK | 26252.5 | 26306.5 | 4\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME | 4\|ONH,WKVAH,T_DELTA_BUY_WK,WKPOC_AREA | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | NONE | | |
| draw |  | | |
| draw_status | NONE | | |
| balance |  | | |
| balance_poc |  | | |
| value_follows | DIVERGENT_UP | | |
| on_inventory | NET_LONG | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 26192.27 | | |
| wkvwap_0810 | 26084.24 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| D_WKVAL_PDVAL_PDPOC_WKPOC_PDTVAL | ANY | ANY | YES |  | {"long": {"TP1": "26049.25-26089.25", "TP2": "26175.00-26200.00", "RUN": "26265.50-26275.50", "R_TP1": "2.45", "R_TP2": "6.90", "R_RUN": "10.11"}, "short": {"TP1": "25389.75-25399.75", "TP2": "", "RUN": "", "R_TP1": "19.56", "R_TP2": "", "R_RUN": ""}} |
| D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ | NONE | NONE | YES |  | {} |
| REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC | NONE | NONE | YES |  | {} |
| T_PD2TPOC | ANY | ANY | YES |  | {"long": {"TP1": "26266.50-26306.50", "TP2": "", "RUN": "26265.50-26275.50", "R_TP1": "1.81", "R_TP2": "", "R_RUN": "1.71"}, "short": {"TP1": "26142.50-26182.50", "TP2": "26070.00-26080.00", "RUN": "25952.25-25962.25", "R_TP1": "5.24", "R_TP2": "15.00", "R_RUN": "26.21"}} |
| WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK | NONE | NONE | YES |  | {} |

review=APPROVED; fails=[]; notes=['C: D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ long NONE: 1 NQ does not fit $1000 (stop 421 ticks)', 'C: D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ short NONE: 1 NQ does not fit $1000 (stop 421 ticks)', 'C: REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC long NONE: 1 NQ does not fit $1000 (stop 378 ticks)', 'C: REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC short NONE: 1 NQ does not fit $1000 (stop 378 ticks)', 'C: WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK long NONE: 1 NQ does not fit $1000 (stop 218 ticks)', 'C: WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK short NONE: 1 NQ does not fit $1000 (stop 218 ticks)']
