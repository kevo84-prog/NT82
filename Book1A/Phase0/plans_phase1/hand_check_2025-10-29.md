# Hand check 2025-10-29 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 25922.5 | 25932.5 | | | peak row 25925.0 | | | | 2025-10-29T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 26035.0 | 26055.0 | | | peak row 26035.0 | | | | 2025-10-29T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 26227.5 | 26267.5 | | | peak row 26245.0 | | | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25885.0 | 25895.0 | | | BUY WK | | role=TARGET | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25895.0 | 25905.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25930.0 | 25940.0 | | | BUY WK | | role=TARGET | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25965.0 | 25975.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25975.0 | 25985.0 | | | BUY WK | | role=TARGET | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 26045.0 | 26055.0 | | | BUY WK | | role=TARGET | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 26030.0 | 26040.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 26045.0 | 26055.0 | | | BUY PD | | role=TARGET | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 26080.0 | 26095.0 | | | BUY PD | | role=TARGET | | 2025-10-29T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 26285.0 | 26295.0 | | | BUY ON | | role=TAG_ONLY | | 2025-10-29T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| PDPOC_AREA_D_PDPOC_WKPOC_PDTPOC | 26035.0 | 26057.5 | 2\|DELTA,VOLUME | 7\|PDPOC,PDTPOC,WKPOC,T_DELTA_BUY_WK,T_DELTA_SELL_PD,T_DELTA_BUY_PD,PDPOC_AREA | DECISION | | |
| D_PDVAH_PDSET_ONL_PDTVAH | 26149.5 | 26179.75 | 4\|AUCTION_VALUE,STRUCTURE,GEX,VWAP | 5\|PDVAH,ONL,WKVWAP_SD1_UP,PS,PS_0DTE | DECISION | | |
| D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC | 26220.0 | 26277.5 | 5\|AUCTION_VALUE,STRUCTURE,VOLUME,GEX,VWAP | 11\|PDH,ONPOC,ONVAL,ONTPOC,ONTVAL,VWAP,VWAPU1,VWAP,VWAP_SD1_UP,HVL_0DTE,ONPOC_AREA | DECISION | | |
| D_ONVAH_WKTVAH_ONTVAH_WKVAH_ONH | 26286.75 | 26314.75 | 5\|AUCTION_VALUE,STRUCTURE,DELTA,GEX,VWAP | 9\|ONVAH,ONTVAH,ONH,VWAPU1,WKVAH,VWAP_SD1_UP,CR,CR_0DTE,T_DELTA_BUY_ON | DECISION | | |

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
| vwap_0810 | 26247.05 | | |
| wkvwap_0810 | 26007.58 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| PDPOC_AREA_D_PDPOC_WKPOC_PDTPOC | ANY | ANY | YES |  | {"long": {"TP1": "26149.50-26159.50", "TP2": "26227.50-26267.50", "RUN": "26298.25-26308.25", "R_TP1": "4.00", "R_TP2": "7.39", "R_RUN": "10.47"}, "short": {"TP1": "26010.00-26020.00", "TP2": "25975.00-25985.00", "RUN": "25902.50-25912.50", "R_TP1": "0.65", "R_TP2": "2.17", "R_RUN": "5.33"}} |
| D_PDVAH_PDSET_ONL_PDTVAH | ANY | ANY | YES |  | {"long": {"TP1": "26220.00-26230.00", "TP2": "26285.00-26295.00", "RUN": "26298.25-26308.25", "R_TP1": "1.31", "R_TP2": "3.42", "R_RUN": "3.85"}, "short": {"TP1": "26047.50-26057.50", "TP2": "26030.00-26040.00", "RUN": "25902.50-25912.50", "R_TP1": "2.99", "R_TP2": "3.56", "R_RUN": "7.71"}} |
| D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC | NONE | NONE | YES |  | {} |
| D_ONVAH_WKTVAH_ONTVAH_WKVAH_ONH | ANY | ANY | YES |  | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "26267.50-26277.50", "TP2": "26080.00-26095.00", "RUN": "25902.50-25912.50", "R_TP1": "0.32", "R_TP2": "6.73", "R_RUN": "13.13"}} |

review=APPROVED; fails=[]; notes=['C: D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC long NONE: 1 NQ does not fit $1000 (stop 232 ticks)', 'C: D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC short NONE: 1 NQ does not fit $1000 (stop 232 ticks)']
