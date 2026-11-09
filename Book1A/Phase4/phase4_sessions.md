# Book 1A Phase 4 sessions and inputs (phase4-sessions-v1.0, Step A1, Nov 9, 2026)

Inputs only: no ledger, strategy log or fill was read. Book 1 calendar (`book1a/sessions.py`, `econ_calendar_2025-10_2026-04.csv`; no cash session Feb 16 Presidents' Day and Apr 3 Good Friday); close `sessions.session_close` (15:00 CT, no half day in Phase 4); front contract from the NinjaTrader roll (Mar 16, 2026: NQH6 -> NQM6), checked against the data-integrity table row the Book 1 backtest used; tape price basis (first RTH trade within 50 points of the 08:31 NQ bar open); GEX price basis (nt_contract = the front by roll; nt_shift_pts nonzero exactly when the GEX front differs from it); exposure from replay plan section 8 (no confirmed date in Phase 4; Parts 5 and 6 unresolved, their approximate weeks EXPOSED, runner decision). A session with a missing input would be DATA_MISSING with its cause; none is dropped.

Sessions: 52; EXPOSED 9; UNEXPOSED 43; DATA_MISSING 0.

| session | day | close CT | exposure | front (NT roll) | roll day | packet instrument | MBO file MB | Databento condition | tape last trade | max gap RTH s | tape - bar pts | NQ / ES RTH bars | GEX front / NT / shift | GEX regime | GEX V3 repro | plan review | status | cause |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-02-05 | Thu | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 694.2 | available | 2026-02-05 17:59:59 | 4.3 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-06 | Fri | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 459.7 | available | 2026-02-06 15:59:59 | 5.8 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-09 | Mon | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 337.0 | available | 2026-02-09 17:59:59 | 6.2 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-10 | Tue | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 317.2 | available | 2026-02-10 17:59:59 | 5.3 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-02-11 | Wed | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 377.2 | available | 2026-02-11 17:59:59 | 4.7 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-12 | Thu | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 497.0 | available | 2026-02-12 17:59:56 | 3.4 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-13 | Fri | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 551.4 | available | 2026-02-13 15:59:57 | 3.8 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-17 | Tue | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 519.3 | available | 2026-02-17 17:59:55 | 4.4 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-18 | Wed | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 355.1 | available | 2026-02-18 17:59:57 | 8.2 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-19 | Thu | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 380.0 | available | 2026-02-19 17:59:58 | 4.9 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-20 | Fri | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 433.9 | available | 2026-02-20 15:59:59 | 4.4 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-23 | Mon | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 425.2 | available | 2026-02-23 17:59:59 | 4.7 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-24 | Tue | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 363.3 | available | 2026-02-24 17:59:49 | 5.1 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-02-25 | Wed | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 237.6 | available | 2026-02-25 17:59:54 | 6.6 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | LOG_ONLY | OK | - |
| 2026-02-26 | Thu | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 379.1 | available | 2026-02-26 17:59:56 | 4.0 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | positive | Y | LOG_ONLY | OK | - |
| 2026-02-27 | Fri | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 387.3 | available | 2026-02-27 15:59:59 | 4.5 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-02 | Mon | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 413.4 | available | 2026-03-02 17:59:58 | 4.9 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-03 | Tue | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 550.1 | available | 2026-03-03 17:59:59 | 3.2 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-03-04 | Wed | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 440.2 | available | 2026-03-04 17:59:59 | 5.0 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-05 | Thu | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 521.8 | available | 2026-03-05 17:59:58 | 2.9 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-06 | Fri | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 510.4 | available | 2026-03-06 15:59:58 | 3.6 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-03-09 | Mon | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 515.7 | available | 2026-03-09 18:59:56 | 3.8 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-10 | Tue | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 468.5 | available | 2026-03-10 18:59:59 | 3.3 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | LOG_ONLY | OK | - |
| 2026-03-11 | Wed | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 404.2 | available | 2026-03-11 18:59:59 | 5.5 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | LOG_ONLY | OK | - |
| 2026-03-12 | Thu | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 396.7 | available | 2026-03-12 18:59:59 | 4.0 | 0.0 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-13 | Fri | 15:00 | UNEXPOSED | NQH6 | N | NQ_JUN26 | 390.0 | available | 2026-03-13 15:59:59 | 3.7 | -0.5 | 390 / 390 of 390 | NQH6 / NQH6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-16 | Mon | 15:00 | UNEXPOSED | NQM6 | Y | NQ_JUN26 | 331.2 | degraded | 2026-03-16 18:59:59 | 7.7 | 0.0 | 390 / 390 of 390 | NQH6 / NQM6 / 211.5 | negative | Y | LOG_ONLY | OK | - |
| 2026-03-17 | Tue | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 306.9 | available | 2026-03-17 18:59:58 | 5.8 | 0.0 | 390 / 390 of 390 | NQH6 / NQM6 / 215.5 | negative | Y | LOG_ONLY | OK | - |
| 2026-03-18 | Wed | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 330.0 | available | 2026-03-18 18:59:59 | 5.5 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-03-19 | Thu | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 489.4 | available | 2026-03-19 18:59:59 | 4.0 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-20 | Fri | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 398.2 | available | 2026-03-20 15:59:59 | 3.7 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-23 | Mon | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 539.8 | available | 2026-03-23 18:59:58 | 3.8 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-24 | Tue | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 444.9 | available | 2026-03-24 18:59:58 | 5.6 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-25 | Wed | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 342.7 | available | 2026-03-25 18:59:57 | 7.1 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-26 | Thu | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 366.9 | available | 2026-03-26 18:59:59 | 3.9 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-27 | Fri | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 360.8 | available | 2026-03-27 15:59:59 | 5.5 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-30 | Mon | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 405.9 | available | 2026-03-30 18:59:59 | 4.5 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-03-31 | Tue | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 535.9 | available | 2026-03-31 18:59:59 | 3.0 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | negative | Y | APPROVED | OK | - |
| 2026-04-01 | Wed | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 356.2 | available | 2026-04-01 18:59:58 | 4.7 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-02 | Thu | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 420.0 | available | 2026-04-02 18:59:59 | 4.2 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-06 | Mon | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 267.8 | available | 2026-04-06 18:59:59 | 7.3 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-07 | Tue | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 419.9 | available | 2026-04-07 18:59:59 | 4.0 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | LOG_ONLY | OK | - |
| 2026-04-08 | Wed | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 373.5 | available | 2026-04-08 18:59:59 | 5.0 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-09 | Thu | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 321.3 | available | 2026-04-09 18:59:58 | 4.5 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-10 | Fri | 15:00 | EXPOSED | NQM6 | N | NQ_JUN26 | 266.3 | degraded | 2026-04-10 15:59:59 | 5.7 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-13 | Mon | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 285.1 | available | 2026-04-13 18:59:59 | 5.4 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-14 | Tue | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 242.1 | available | 2026-04-14 18:59:58 | 4.8 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-15 | Wed | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 274.2 | available | 2026-04-15 18:59:59 | 4.0 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-16 | Thu | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 314.0 | available | 2026-04-16 18:59:55 | 4.0 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-17 | Fri | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 342.1 | available | 2026-04-17 15:59:58 | 3.6 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-20 | Mon | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 326.7 | available | 2026-04-20 18:59:59 | 5.5 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |
| 2026-04-21 | Tue | 15:00 | UNEXPOSED | NQM6 | N | NQ_JUN26 | 382.3 | available | 2026-04-21 15:59:59 | 5.2 | 0.0 | 390 / 390 of 390 | NQM6 / NQM6 / 0.0 | positive | Y | APPROVED | OK | - |

Exposed sessions (replay plan section 8, unresolved dates treated as excluded):

- 2026-03-30: Part 5, 45 Days Using This (about Apr 2, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-03-31: Part 5, 45 Days Using This (about Apr 2, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-01: Part 5, 45 Days Using This (about Apr 2, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-02: Part 5, 45 Days Using This (about Apr 2, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-06: Part 6, Order Flow and GEX Levels (about Apr 9, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-07: Part 6, Order Flow and GEX Levels (about Apr 9, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-08: Part 6, Order Flow and GEX Levels (about Apr 9, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-09: Part 6, Order Flow and GEX Levels (about Apr 9, 2026; unresolved, treated as excluded; week of the approximate date)
- 2026-04-10: Part 6, Order Flow and GEX Levels (about Apr 9, 2026; unresolved, treated as excluded; week of the approximate date)

Databento condition other than available (logged; files used by the Book 1 backtest):

- 2026-03-16: degraded (raw/block1/nq_roll_NQM6_mbo_20260315_20260317/GLBX-20261024-PDX3BWCNDV/glbx-mdp3-20260316.mbo.dbn.zst)
- 2026-04-10: degraded (raw/block1/nq_mbo_20251021_20260421/GLBX-20261022-JHKARNQBGK/glbx-mdp3-20260410.mbo.dbn.zst)

Calendar events on the sessions (logged; the plan applies its own rules):

- 2026-02-05: GOOGL earnings (Feb 4 after close) (max_trades=1)
- 2026-02-06: AMZN earnings (Feb 5 after close) (max_trades=1)
- 2026-02-10: Retail sales (advance) (no_trade 08:30-08:40)
- 2026-02-11: Employment Situation (NFP) (no_trade 08:30-08:40)
- 2026-02-13: CPI (no_trade 08:30-08:40)
- 2026-02-20: GDP Q4 advance + PCE (no_trade 08:30-08:40); Monthly options expiration (none)
- 2026-02-26: NVDA earnings (Feb 25 after close) (max_trades=1)
- 2026-02-27: PPI (no_trade 08:30-08:40)
- 2026-03-02: ISM Manufacturing PMI (no_trade 08:58-09:15)
- 2026-03-04: ISM Services PMI (no_trade 08:58-09:15)
- 2026-03-06: Employment Situation (NFP) (no_trade 08:30-08:40); Retail sales (advance) (no_trade 08:30-08:40)
- 2026-03-11: CPI (no_trade 08:30-08:40)
- 2026-03-13: GDP Q4 second estimate + PCE (no_trade 08:30-08:40)
- 2026-03-16: NQ roll day (Mar 26 to Jun 26) (LOG_ONLY)
- 2026-03-18: PPI (no_trade 08:30-08:40); FOMC decision + SEP + press conference (no_trade 12:45-15:00)
- 2026-03-20: Quarterly expiration (quad witching) (none)
- 2026-04-01: ISM Manufacturing PMI (no_trade 08:58-09:15); Retail sales (advance) (no_trade 08:30-08:40)
- 2026-04-06: ISM Services PMI (no_trade 08:58-09:15)
- 2026-04-09: GDP Q4 third estimate + PCE (no_trade 08:30-08:40)
- 2026-04-10: CPI (no_trade 08:30-08:40)
- 2026-04-14: PPI (no_trade 08:30-08:40)
- 2026-04-17: Monthly options expiration (none)
- 2026-04-21: Retail sales (advance) (no_trade 08:30-08:40)

Map packet data notes (gaps / notes written by map v2.3):

- 2026-02-05: gaps none; notes none
- 2026-02-06: gaps none; notes none
- 2026-02-09: gaps none; notes none
- 2026-02-10: gaps none; notes none
- 2026-02-11: gaps none; notes none
- 2026-02-12: gaps none; notes none
- 2026-02-13: gaps none; notes none
- 2026-02-17: gaps none; notes none
- 2026-02-18: gaps none; notes none
- 2026-02-19: gaps none; notes none
- 2026-02-20: gaps none; notes none
- 2026-02-23: gaps none; notes none
- 2026-02-24: gaps none; notes none
- 2026-02-25: gaps none; notes none
- 2026-02-26: gaps none; notes none
- 2026-02-27: gaps none; notes none
- 2026-03-02: gaps none; notes none
- 2026-03-03: gaps none; notes none
- 2026-03-04: gaps none; notes none
- 2026-03-05: gaps none; notes none
- 2026-03-06: gaps none; notes none
- 2026-03-09: gaps none; notes none
- 2026-03-10: gaps none; notes none
- 2026-03-11: gaps none; notes none
- 2026-03-12: gaps none; notes none
- 2026-03-13: gaps none; notes none
- 2026-03-16: gaps none; notes none
- 2026-03-17: gaps none; notes none
- 2026-03-18: gaps none; notes none
- 2026-03-19: gaps none; notes none
- 2026-03-20: gaps none; notes none
- 2026-03-23: gaps none; notes none
- 2026-03-24: gaps none; notes none
- 2026-03-25: gaps none; notes none
- 2026-03-26: gaps none; notes none
- 2026-03-27: gaps none; notes none
- 2026-03-30: gaps none; notes none
- 2026-03-31: gaps none; notes none
- 2026-04-01: gaps none; notes none
- 2026-04-02: gaps none; notes none
- 2026-04-06: gaps none; notes none
- 2026-04-07: gaps none; notes none
- 2026-04-08: gaps none; notes none
- 2026-04-09: gaps none; notes none
- 2026-04-10: gaps none; notes none
- 2026-04-13: gaps none; notes none
- 2026-04-14: gaps none; notes none
- 2026-04-15: gaps none; notes none
- 2026-04-16: gaps none; notes none
- 2026-04-17: gaps none; notes none
- 2026-04-20: gaps none; notes none
- 2026-04-21: gaps none; notes none
