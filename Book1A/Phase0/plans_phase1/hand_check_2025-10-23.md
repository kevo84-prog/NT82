# Hand check 2025-10-23 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REJ_LOW | 24867.0 | 24907.0 | PD | 2025-10-22T11:34:00-05:00 | DELTA:-289 | 154.5 | DELTA_SELL | TARGET | 2025-10-23T08:10:00-05:00 | | |
| MAP4 WKPOC_AREA | 25300.0 | 25320.0 | | | peak row 25315.0 | | | | 2025-10-23T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 25025.0 | 25040.0 | | | peak row 25030.0 | | | | 2025-10-23T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 25087.5 | 25097.5 | | | peak row 25090.0 | | | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25215.0 | 25225.0 | | | SELL WK | | role=TARGET | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25270.0 | 25280.0 | | | SELL WK | | role=TARGET | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25295.0 | 25315.0 | | | SELL WK | | role=TARGET | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25315.0 | 25335.0 | | | BUY WK | | role=TAG_ONLY | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25345.0 | 25355.0 | | | BUY WK | | role=TAG_ONLY | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 24870.0 | 24885.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 25045.0 | 25055.0 | | | BUY PD | | role=TAG_ONLY | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25170.0 | 25180.0 | | | SELL PD | | role=TARGET | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25210.0 | 25220.0 | | | SELL PD | | role=TARGET | | 2025-10-23T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_ON | 25015.0 | 25025.0 | | | SELL ON | | role=TARGET | | 2025-10-23T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| T_HTFPOC | 24822.5 | 24832.5 | 2\|VOLUME,GEX | 2\|HTFPOC,PS_0DTE | DECISION | | |
| REJ_LOW_PD_T_PDVAL | 24867.0 | 24907.0 | 4\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME | 3\|PDVAL,PWKPOC,T_DELTA_SELL_PD | DECISION | | |
| T_PWKVAH_PWKTVAH | 24974.5 | 24984.75 | 3\|AUCTION_VALUE,GEX,VWAP | 4\|VWAPL1,PWKVAH,VWAP_SD1_DN,HVL | DECISION | | |
| D_ONPOC_PDSET_PDTPOC_WKTVAL_PDPOC_AREA | 25025.0 | 25065.0 | 4\|DELTA,VOLUME,GEX,VWAP | 9\|PDTPOC,ONPOC,VWAP,VWAP,WKVWAP_SD1_DN,HVL_0DTE,T_DELTA_BUY_PD,T_DELTA_SELL_ON,PDPOC_AREA | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BALANCED | | |
| draw |  | | |
| draw_status | NONE | | |
| balance | 24896-25134 | | |
| balance_poc | 25000 | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_SHORT | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 25036.02 | | |
| wkvwap_0810 | 25171.50 | | |
| wkval_state | accept=BELOW|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| T_HTFPOC | ANY | ANY | YES |  | {"long": {"TP1": "24867.00-24907.00", "TP2": "25015.00-25025.00", "RUN": "25348.00-25358.00", "R_TP1": "3.29", "R_TP2": "17.38", "R_RUN": "49.10"}, "short": {"TP1": "24690.00-24700.00", "TP2": "", "RUN": "", "R_TP1": "11.67", "R_TP2": "", "R_RUN": ""}} |
| REJ_LOW_PD_T_PDVAL | ANY | ANY | YES |  | {"long": {"TP1": "24974.50-24984.50", "TP2": "25015.00-25025.00", "RUN": "25348.00-25358.00", "R_TP1": "1.67", "R_TP2": "2.67", "R_RUN": "10.89"}, "short": {"TP1": "24822.50-24832.50", "TP2": "", "RUN": "", "R_TP1": "0.85", "R_TP2": "", "R_RUN": ""}} |
| T_PWKVAH_PWKTVAH | ANY | ANY | YES |  | {"long": {"TP1": "24995.00-25005.00", "TP2": "25015.00-25025.00", "RUN": "25348.00-25358.00", "R_TP1": "0.95", "R_TP2": "2.81", "R_RUN": "33.79"}, "short": {"TP1": "24867.00-24907.00", "TP2": "", "RUN": "24872.50-24882.50", "R_TP1": "6.28", "R_TP2": "", "R_RUN": "8.56"}} |
| D_ONPOC_PDSET_PDTPOC_WKTVAL_PDPOC_AREA | ANY | ANY | YES |  | {"long": {"TP1": "25076.25-25086.25", "TP2": "25087.50-25097.50", "RUN": "25348.00-25358.00", "R_TP1": "0.28", "R_TP2": "0.56", "R_RUN": "6.99"}, "short": {"TP1": "24867.00-24907.00", "TP2": "", "RUN": "24872.50-24882.50", "R_TP1": "2.91", "R_TP2": "", "R_RUN": "3.52"}} |

review=APPROVED; fails=[]; notes=['Z3: D_PDPOC_ONVAL_ONTVAL at the balance POC: TARGET only']
