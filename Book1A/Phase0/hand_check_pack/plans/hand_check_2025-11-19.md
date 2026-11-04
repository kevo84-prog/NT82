# Hand check 2025-11-19 (map v2.4 Book 1A outputs, families, context and sides)

## P0.7 zones (every zone frozen at 08:10 CT)

| kind | lo | hi | session | formed_ct | evidence | departure pts | tags | class | available_at | hand (lo-hi, kind) | match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REJ_HIGH | 24792.0 | 24832.0 | PD | 2025-11-18T08:34:00-06:00 | DELTA:620 | 186.5 | DELTA_BUY|DELTA_SELL | TARGET | 2025-11-19T08:10:00-06:00 | | |
| REJ_HIGH | 25010.75 | 25050.75 | WK | 2025-11-17T12:49:00-06:00 | DELTA:268 | 164.0 |  | TARGET | 2025-11-19T08:10:00-06:00 | | |
| REJ_LOW | 24376.25 | 24416.25 | PD | 2025-11-18T10:04:00-06:00 | DELTA:-951 | 176.25 |  | TARGET | 2025-11-19T08:10:00-06:00 | | |
| MAP4 WKPOC_AREA | 24702.5 | 24742.5 | | | peak row 24720.0 | | | | 2025-11-19T08:10:00-06:00 | | |
| MAP4 PDPOC_AREA | 24737.5 | 24777.5 | | | peak row 24755.0 | | | | 2025-11-19T08:10:00-06:00 | | |
| MAP4 ONPOC_AREA | 24590.0 | 24615.0 | | | peak row 24600.0 | | | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 24530.0 | 24540.0 | | | SELL WK | | role=TAG_ONLY | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 24675.0 | 24685.0 | | | BUY WK | | role=TAG_ONLY | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_WK | 24795.0 | 24810.0 | | | BUY WK | | role=TAG_ONLY | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_WK | 24820.0 | 24845.0 | | | SELL WK | | role=TARGET | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_PD | 24675.0 | 24700.0 | | | BUY PD | | role=TAG_ONLY | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_SELL_ON | 24525.0 | 24540.0 | | | SELL ON | | role=TAG_ONLY | | 2025-11-19T08:10:00-06:00 | | |
| DELTA T_DELTA_BUY_ON | 24610.0 | 24620.0 | | | BUY ON | | role=TARGET | | 2025-11-19T08:10:00-06:00 | | |

## P0.8 families and levels on each decision zone

| zone | lo | hi | families= | levels= | class | hand families | match |
|---|---|---|---|---|---|---|---|
| D_PDTVAL_PDVAL_ONTPOC | 24545.0 | 24562.5 | 4\|AUCTION_VALUE,DELTA,VOLUME,VWAP | 6\|PDVAL,ONTPOC,VWAPL1,VWAP_SD1_DN,T_DELTA_SELL_WK,T_DELTA_SELL_ON | DECISION | | |
| ONPOC_AREA_D_PDSET_ONPOC | 24590.0 | 24615.0 | 3\|DELTA,VOLUME,VWAP | 6\|ONPOC,VWAP,VWAP,WKVWAP_SD1_DN,T_DELTA_BUY_ON,ONPOC_AREA | DECISION | | |
| D_PD3L_PWKL | 24621.0 | 24631.0 | 2\|STRUCTURE,DELTA | 2\|PD3L,T_DELTA_BUY_ON | DECISION | | |
| D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA | 24687.5 | 24777.5 | 3\|STRUCTURE,DELTA,VOLUME | 8\|PDTPOC,PD2L,ONH,WKPOC,T_DELTA_BUY_WK,T_DELTA_BUY_PD,WKPOC_AREA,PDPOC_AREA | DECISION | | |
| T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH | 24779.75 | 24837.0 | 6\|AUCTION_VALUE,STRUCTURE,DELTA,VOLUME,GEX,VWAP | 8\|PDVAH,PDH,HTFPOC,WKVWAP,HVL,T_DELTA_BUY_WK,T_DELTA_SELL_WK,PDPOC_AREA | DECISION | | |

## P0.9 context and side fields

| field | value | hand | match |
|---|---|---|---|
| market_context | BULLISH | | |
| draw | 24702.50-24742.50|WKPOC_AREA | | |
| draw_status | ACTIVE | | |
| balance | 24549.5-24778.5 | | |
| balance_poc | 24670 | | |
| value_follows | WITH_PRICE | | |
| on_inventory | NET_LONG | | |
| htf_structure | BALANCE | | |
| gex_regime | NEG | | |
| vwap_0810 | 24611.63 | | |
| wkvwap_0810 | 24817.37 | | |
| wkval_state | accept=INSIDE|failed_reclaim=0 | | |
| wkvah_state | accept=INSIDE|failed_reclaim=0 | | |

| zone | long | short | first_touch | side_conflict | ladder |
|---|---|---|---|---|---|
| D_PDTVAL_PDVAL_ONTPOC | ANY | INITIATION | YES |  | {"long": {"TP1": "24792.00-24832.00", "TP2": "", "RUN": "24972.25-24982.25", "R_TP1": "12.75", "R_TP2": "", "R_RUN": "22.76"}, "short": {"TP1": "24376.25-24416.25", "TP2": "", "RUN": "24431.50-24441.50", "R_TP1": "7.15", "R_TP2": "", "R_RUN": "5.75"}} |
| ONPOC_AREA_D_PDSET_ONPOC | ANY | INITIATION | YES |  | {"long": {"TP1": "24792.00-24832.00", "TP2": "", "RUN": "24972.25-24982.25", "R_TP1": "6.94", "R_TP2": "", "R_RUN": "14.01"}, "short": {"TP1": "24376.25-24416.25", "TP2": "", "RUN": "24431.50-24441.50", "R_TP1": "6.81", "R_TP2": "", "R_RUN": "5.82"}} |
| D_PD3L_PWKL | ANY | INITIATION | YES |  | {"long": {"TP1": "24792.00-24832.00", "TP2": "", "RUN": "24972.25-24982.25", "R_TP1": "15.33", "R_TP2": "", "R_RUN": "32.50"}, "short": {"TP1": "24376.25-24416.25", "TP2": "", "RUN": "24431.50-24441.50", "R_TP1": "19.50", "R_TP2": "", "R_RUN": "17.10"}} |
| D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA | NONE | NONE | YES |  | {} |
| T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH | NONE | NONE | YES |  | {} |

review=APPROVED; fails=[]; notes=['Z3: D_ONVAH_PDPOC at the balance POC: TARGET only', 'C: D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA long NONE: 1 NQ does not fit $1000 (stop 362 ticks)', 'C: D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA short NONE: 1 NQ does not fit $1000 (stop 362 ticks)', 'C: T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH long NONE: 1 NQ does not fit $1000 (stop 231 ticks)', 'C: T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH short NONE: 1 NQ does not fit $1000 (stop 231 ticks)']
