# Hand check 2025-10-28 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MAP4 WKPOC_AREA | 25922.5 | 25932.5 | | | peak row 25925.0 | | | | 2025-10-28T08:10:00-05:00 | | |
| MAP4 PDPOC_AREA | 25922.5 | 25932.5 | | | peak row 25925.0 | | | | 2025-10-28T08:10:00-05:00 | | |
| MAP4 ONPOC_AREA | 25965.0 | 25980.0 | | | peak row 25970.0 | | | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25895.0 | 25905.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25930.0 | 25940.0 | | | BUY WK | | role=TARGET | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_WK | 25965.0 | 25975.0 | | | SELL WK | | role=TAG_ONLY | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_WK | 25975.0 | 25985.0 | | | BUY WK | | role=TARGET | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_SELL_PD | 25895.0 | 25905.0 | | | SELL PD | | role=TAG_ONLY | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_PD | 25930.0 | 25940.0 | | | BUY PD | | role=TARGET | | 2025-10-28T08:10:00-05:00 | | |
| DELTA T_DELTA_BUY_ON | 26010.0 | 26020.0 | | | BUY ON | | role=TARGET | | 2025-10-28T08:10:00-05:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| T_ONTVAH_ONVAH | 25994.75 | 26008.0 | 3\|AUCTION_VALUE,DELTA,GEX | 4\|ONVAH,ONTVAH,CR,T_DELTA_BUY_ON | DECISION | | |
| T_WKTVAH_WKVAH | 26024.75 | 26038.75 | 2\|AUCTION_VALUE,DELTA | 2\|WKVAH,T_DELTA_BUY_ON | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BALANCED | | |
| draw |  | | |
| draw_status | NONE | | |
| balance | 25874.25-26033.75 | | |
| balance_poc | 25925.00 | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_LONG | | |
| htf_structure | BALANCE | | |
| gex_regime | POS | | |
| vwap_0810 | 25989.24 | | |
| wkvwap_0810 | 25890.77 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=TESTING|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| T_ONTVAH_ONVAH | ANY | ANY | YES |  | {"long": {"TP1": "26028.75-26038.75", "TP2": "", "RUN": "26028.75-26038.75", "R_TP1": "1.51", "R_TP2": "", "R_RUN": "1.51"}, "short": {"TP1": "25975.50-25985.50", "TP2": "25965.00-25975.00", "RUN": "25839.75-25849.75", "R_TP1": "0.67", "R_TP2": "1.44", "R_RUN": "10.55"}} |
| T_WKTVAH_WKVAH | ANY | ANY | YES |  | {"long": {"TP1": "", "TP2": "", "RUN": "", "R_TP1": "", "R_TP2": "", "R_RUN": ""}, "short": {"TP1": "25998.00-26008.00", "TP2": "25975.00-25985.00", "RUN": "25839.75-25849.75", "R_TP1": "1.16", "R_TP2": "2.74", "R_RUN": "12.07"}} |

review=APPROVED; fails=[]; notes=['Z3: D_PDPOC_WKPOC at the balance POC: TARGET only', 'Z3: WKPOC_AREA at the balance POC: TARGET only', 'Z3: PDPOC_AREA at the balance POC: TARGET only']
