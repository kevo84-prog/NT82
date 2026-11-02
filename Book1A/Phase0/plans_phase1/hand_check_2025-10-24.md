# Hand check 2025-10-24 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 25300.0 | 25320.0 | | | peak row 25315.0 | | | | 2025-10-24T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 25260.0 | 25275.0 | | | peak row 25260.0 | | | | 2025-10-24T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 25365.0 | 25380.0 | | | peak row 25370.0 | | | | 2025-10-24T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25295.0 | 25315.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-24T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25315.0 | 25355.0 | | | BUY WK | | role=TARGET | | 2025-10-24T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25145.0 | 25155.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-24T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 25180.0 | 25195.0 | | | BUY PD | | role=TARGET | | 2025-10-24T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 25340.0 | 25350.0 | | | BUY ON | | role=TARGET | | 2025-10-24T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 25360.0 | 25370.0 | | | BUY ON | | role=TARGET | | 2025-10-24T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| T_ONPOC_ONTPOC_ONPOC_AREA_D_WKTVAH_ONTVAH_HTFVAH | 25360.0 | 25399.75 | 4\|AUCTION_VALUE,DELTA,VOLUME,VWAP | 9\|ONPOC,ONTVAH,ONTPOC,VWAP,HTFVAH,VWAP,T_DELTA_BUY_WK,T_DELTA_BUY_ON,ONPOC_AREA | DECISION | | |
| T_ONVAH | 25450.25 | 25460.25 | 2\|AUCTION_VALUE,VWAP | 3\|ONVAH,VWAPU1,VWAP_SD1_UP | DECISION | | |

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
| vwap_0810 | 25387.97 | | |
| wkvwap_0810 | 25182.64 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=ABOVE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| T_ONPOC_ONTPOC_ONPOC_AREA_D_WKTVAH_ONTVAH_HTFVAH | ANY | INITIATION | YES | side_conflict=T_ONPOC_ONTPOC_ONPOC_AREA_D_WKTVAH_ONTVAH_HTFVAH|short|context=ANY,edge_control=INITIATION | {"long": {"TP1": "25450.25-25460.25", "TP2": "", "RUN": "", "R_TP1": "1.25", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25340.50-25350.50", "TP2": "25300.00-25320.00", "RUN": "25088.50-25098.50", "R_TP1": "0.24", "R_TP2": "0.99", "R_RUN": "6.50"}} |
| T_ONVAH | ANY | ANY | YES |  | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25389.75-25399.75", "TP2": "25365.00-25380.00", "RUN": "25088.50-25098.50", "R_TP1": "4.81", "R_TP2": "6.69", "R_RUN": "33.50"}} |

review=APPROVED; fails=[]; notes=[]
