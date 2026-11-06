# Wide decision zones: eligibility report (wide-zone-report-v1.0)

Descriptive only (Kyron, Nov 4). Frozen rules kept: no 60-point cap, no stop change. No outcomes, no P&L, no alternate trades. Zone = a plan DECISION zone whose planned stop (width in ticks + 2) is above 196 ticks, so 1 NQ does not fit the $1,000 budget.

## Zone counts

- Days: 13. Decision zones: 47. Wide zones: 9.
- Wide zones with a side NONE only because of the risk check: 9.
- Wide zones with a pre-existing structural invalidation level inside: 8.
- Wide zones where 1 MNQ would fit: 9.

| # | day | zone | lo - hi | width pts | families | levels | planned stop ticks | 1 NQ risk | long | short | rejected only for risk | structural level inside (which; pts from long / short entry edge) | 1 MNQ fits (estimate) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2025-10-22 | D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA | 25198.25 - 25265.0 | 66.75 | 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP | 21: PDVAL, PDL, ONPOC, ONVAL, ONTPOC, ONTVAL, ONL, VWAP, VWAPL1, WKVAL, VWAP, VWAP_SD1_DN, WKVWAP, HVL, HVL_0DTE, T_DELTA_SELL_WK, T_DELTA_SELL_WK, T_DELTA_SELL_PD, T_DELTA_SELL_PD, T_DELTA_SELL_ON, ONPOC_AREA | 269 | $1,360.74 | NONE: risk only | NONE: risk only | Y | Y: PDL 25203.25 (61.75 / 5.00); ONL 25206.5 (58.50 / 8.25) | Y ($141.24) |
| 2 | 2025-10-29 | D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC | 26220.0 - 26277.5 | 57.50 | 5: AUCTION_VALUE, STRUCTURE, VOLUME, GEX, VWAP | 11: PDH, ONPOC, ONVAL, ONTPOC, ONTVAL, VWAP, VWAPU1, VWAP, VWAP_SD1_UP, HVL_0DTE, ONPOC_AREA | 232 | $1,175.74 | NONE: risk only | NONE: risk only | Y | Y: PDH 26231.5 (46.00 / 11.50) | Y ($122.74) |
| 3 | 2025-10-30 | D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ONPOC_AREA_D_PD2H_ON | 26185.0 - 26262.5 | 77.50 | 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP | 16: PDVAL, PDTPOC, PD2H, ONPOC, ONTPOC, ONTVAL, VWAP, VWAP, WKVWAP_SD1_UP, HVL_0DTE, T_DELTA_SELL_WK, T_DELTA_SELL_PD, T_DELTA_SELL_ON, WKPOC_AREA, PDPOC_AREA, ONPOC_AREA | 312 | $1,575.74 | NONE: risk only | NONE: risk only | Y | Y: PD2H 26231.5 (31.00 / 46.50); REJ_HIGH_PD swing 26228.0 (34.50 / 43.00) | Y ($162.74) |
| 4 | 2025-10-31 | D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ | 25995.0 - 26099.75 | 104.75 | 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP | 9: PDVAH, PDTPOC, PD2L, PD3L, WKVWAP, CR, T_DELTA_BUY_WK, T_DELTA_SELL_PD, PDPOC_AREA | 421 | $2,120.74 | NONE: risk only | NONE: risk only | Y | Y: PD2L 26049.25 (50.50 / 54.25); PD3L 26006.0 (93.75 / 11.00) | Y ($217.24) |
| 5 | 2025-10-31 | REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC | 26142.5 - 26236.5 | 94.00 | 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP | 19: PDH, PD3H, ONVAH, ONPOC, ONVAL, ONTVAH, ONTPOC, ONTVAL, VWAP, VWAPU1, VWAPL1, VWAP, VWAP_SD1_UP, VWAP_SD1_DN, WKVWAP_SD1_UP, CR_0DTE, T_DELTA_SELL_WK, T_DELTA_BUY_ON, ONPOC_AREA | 378 | $1,905.74 | NONE: risk only | NONE: risk only | Y | Y: PDH 26182.5 (54.00 / 40.00); PD3H 26231.5 (5.00 / 89.00); REJ_HIGH_PD swing 26182.5 (54.00 / 40.00) | Y ($195.74) |
| 6 | 2025-10-31 | WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK | 26252.5 - 26306.5 | 54.00 | 4: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME | 4: ONH, WKVAH, T_DELTA_BUY_WK, WKPOC_AREA | 218 | $1,105.74 | NONE: risk only | NONE: risk only | Y | Y: ONH 26274.0 (32.50 / 21.50); REJ_HIGH_WK swing 26306.5 (0.00 / 54.00) | Y ($115.74) |
| 7 | 2025-11-17 | PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL | 25130.0 - 25183.5 | 53.50 | 4: AUCTION_VALUE, DELTA, VOLUME, GEX | 7: PDPOC, PDTPOC, PWKVAL, HVL_0DTE, T_DELTA_SELL_PD, T_DELTA_BUY_PD, PDPOC_AREA | 216 | $1,095.74 | NONE: risk only | NONE: risk only | Y | N | Y ($114.74) |
| 8 | 2025-11-19 | D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PDPOC_AREA | 24687.5 - 24777.5 | 90.00 | 3: STRUCTURE, DELTA, VOLUME | 8: PDTPOC, PD2L, ONH, WKPOC, T_DELTA_BUY_WK, T_DELTA_BUY_PD, WKPOC_AREA, PDPOC_AREA | 362 | $1,825.74 | NONE: risk only | NONE: risk only | Y | Y: PD2L 24731.75 (45.75 / 44.25); ONH 24733.25 (44.25 / 45.75) | Y ($187.74) |
| 9 | 2025-11-19 | T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH | 24779.75 - 24837.0 | 57.25 | 6: AUCTION_VALUE, STRUCTURE, DELTA, VOLUME, GEX, VWAP | 8: PDVAH, PDH, HTFPOC, WKVWAP, HVL, T_DELTA_BUY_WK, T_DELTA_SELL_WK, PDPOC_AREA | 231 | $1,170.74 | NONE: risk only | NONE: risk only | Y | Y: PDH 24832.0 (5.00 / 52.25); REJ_HIGH_PD swing 24832.0 (5.00 / 52.25) | Y ($122.24) |

## Trade counts (separate from zone counts)

From the R4 Phase 1 run's strategy log and attempts (counts only). A candidate on a wide zone has S1.4's own stop, not the zone stop, so it can pass the risk check. Days without an R4 run (Phase 2 days) show 'not run'.

| # | day | zone | candidates on the zone | order attempts | risk rejected | entered |
|---|---|---|---|---|---|---|
| 1 | 2025-10-22 | D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_O | 9 | 0 | 0 | 0 |
| 2 | 2025-10-29 | D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ON | 36 | 0 | 0 | 0 |
| 3 | 2025-10-30 | D_ONTVAL_ONPOC_PDTVAL_PDVAL_REJ_HIGH_PD_ | 0 | 0 | 0 | 0 |
| 4 | 2025-10-31 | D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3P | 17 | 0 | 0 | 0 |
| 5 | 2025-10-31 | REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3T | 3 | 0 | 0 | 0 |
| 6 | 2025-10-31 | WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_W | 0 | 0 | 0 | 0 |
| 7 | 2025-11-17 | PDPOC_AREA_D_PDPOC_PDTPOC_PWKTVAL_PWKVAL | not run | | | |
| 8 | 2025-11-19 | D_PDTPOC_WKTPOC_WKPOC_AREA_D_PD2L_ONH_PD | not run | | | |
| 9 | 2025-11-19 | T_PDTVAH_PDVAH_REJ_HIGH_PD_D_HTFPOC_PDH | not run | | | |
| | | total (R4 days) | 65 | 0 | 0 | 0 |
