# Book 1A Phase 3 sessions and inputs (phase3-sessions-v1.0, Step A1, Nov 8, 2026)

Inputs only: no ledger, strategy log or fill was read. Book 1 calendar (`book1a/sessions.py`, `econ_calendar_2025-10_2026-04.csv`); close time `sessions.session_close` (15:00 CT full day, 12:15 CT half day); front contract from the NinjaTrader roll (Dec 15, 2025: NQZ5 -> NQH6) and checked against the data-integrity table of the read-only Book 1 reference copy; exposure from replay plan section 8 (updated Nov 8, 2026: Part 3 = Jan 12, Jan 14, Jan 16, 2026, session level whatever the instrument; every other unresolved video has no confirmed date and stays EXCLUDED until confirmed, so it flags no session here); tape (the phase3 tape folder the map build used, Feb 4 cut at 17:00 CT), bar, GEX, GEX V3 and plan checks from the files themselves. A session with a missing input would be DATA_MISSING with its cause; none is dropped.

Sessions: 41; EXPOSED 3; UNEXPOSED 38; DATA_MISSING 2.

| session | day | type | close CT | exposure | front (NT roll) | roll day | packet instrument | MBO file MB | Databento condition | tape last trade | max gap RTH s | max gap overnight s | NQ / ES RTH bars | GEX regime | GEX V3 repro | plan review | C2 plan | status | cause |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-12-05 | Fri | FULL | 15:00 | UNEXPOSED | NQZ5 | N | NQ_MAR26 | 302.3 | available | 2025-12-05 15:59:59 | 7.0 | 55.3 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-08 | Mon | FULL | 15:00 | UNEXPOSED | NQZ5 | N | NQ_MAR26 | 285.4 | available | 2025-12-08 17:59:59 | 4.3 | 46.4 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-09 | Tue | FULL | 15:00 | UNEXPOSED | NQZ5 | N | NQ_MAR26 | 246.0 | available | 2025-12-09 17:59:56 | 8.0 | 61.0 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-10 | Wed | FULL | 15:00 | UNEXPOSED | NQZ5 | N | NQ_MAR26 | 322.5 | available | 2025-12-10 17:59:59 | 5.1 | 43.4 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-11 | Thu | FULL | 15:00 | UNEXPOSED | NQZ5 | N | NQ_MAR26 | 356.2 | available | 2025-12-11 17:59:59 | 4.9 | 30.0 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-12 | Fri | FULL | 15:00 | UNEXPOSED | NQZ5 | N | NQ_MAR26 | 428.6 | available | 2025-12-12 15:59:59 | 4.3 | 57.2 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-15 | Mon | FULL | 15:00 | UNEXPOSED | NQH6 | Y | NQ_MAR26 | 336.4 | available | 2025-12-15 17:59:59 | 8.5 | 63.3 | 390 / 390 of 390 | negative | Y | LOG_ONLY | Y | OK | - |
| 2025-12-16 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 436.0 | available | 2025-12-16 17:59:55 | 3.5 | 38.7 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2025-12-17 | Wed | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 450.6 | available | 2025-12-17 17:59:59 | 5.2 | 39.7 | 390 / 390 of 390 | negative | N | APPROVED | Y | DATA_MISSING | GEX V3 inputs do not reproduce the frozen row |
| 2025-12-18 | Thu | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 431.1 | available | 2025-12-18 17:59:59 | 3.5 | 52.7 | 390 / 390 of 390 | negative | N | APPROVED | Y | DATA_MISSING | GEX V3 inputs do not reproduce the frozen row |
| 2025-12-19 | Fri | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 291.3 | available | 2025-12-19 15:59:59 | 7.3 | 39.0 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2025-12-22 | Mon | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 202.4 | available | 2025-12-22 17:59:57 | 7.8 | 57.2 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-23 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 169.0 | available | 2025-12-23 17:59:55 | 8.5 | 58.1 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-24 | Wed | HALF_DAY | 12:15 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 72.5 | available | 2025-12-24 12:14:58 | 8.0 | 82.8 | 225 / 225 of 225 | positive | Y | LOG_ONLY | Y | OK | - |
| 2025-12-26 | Fri | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 119.5 | available | 2025-12-26 15:59:59 | 9.4 | 97.5 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-29 | Mon | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 203.6 | available | 2025-12-29 17:59:59 | 6.6 | 50.5 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-30 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 158.4 | available | 2025-12-30 17:59:52 | 8.3 | 67.1 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2025-12-31 | Wed | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 188.8 | available | 2025-12-31 15:59:59 | 8.5 | 82.4 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-02 | Fri | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 334.2 | available | 2026-01-02 15:59:59 | 6.4 | 60.4 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-05 | Mon | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 282.2 | available | 2026-01-05 17:59:58 | 6.4 | 45.3 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-06 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 232.5 | available | 2026-01-06 17:59:59 | 6.3 | 64.7 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-07 | Wed | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 250.5 | available | 2026-01-07 17:59:53 | 5.8 | 45.1 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-08 | Thu | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 302.0 | available | 2026-01-08 17:59:58 | 5.1 | 37.3 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-09 | Fri | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 289.4 | available | 2026-01-09 15:59:59 | 6.8 | 49.0 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-12 | Mon | FULL | 15:00 | EXPOSED | NQH6 | N | NQ_MAR26 | 246.1 | available | 2026-01-12 17:59:59 | 5.7 | 36.7 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-13 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 336.3 | available | 2026-01-13 17:59:59 | 5.4 | 39.5 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-14 | Wed | FULL | 15:00 | EXPOSED | NQH6 | N | NQ_MAR26 | 380.8 | available | 2026-01-14 17:59:59 | 4.0 | 55.8 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-15 | Thu | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 334.3 | available | 2026-01-15 17:59:59 | 4.3 | 31.1 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-16 | Fri | FULL | 15:00 | EXPOSED | NQH6 | N | NQ_MAR26 | 279.1 | available | 2026-01-16 15:59:58 | 6.9 | 53.2 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-20 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 442.7 | available | 2026-01-20 17:59:58 | 3.0 | 50.4 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-21 | Wed | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 486.6 | available | 2026-01-21 17:59:57 | 3.2 | 47.4 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-22 | Thu | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 335.9 | available | 2026-01-22 17:59:59 | 7.4 | 43.9 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-01-23 | Fri | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 326.0 | available | 2026-01-23 15:59:59 | 5.2 | 49.5 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-26 | Mon | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 287.3 | available | 2026-01-26 17:59:58 | 7.4 | 50.6 | 390 / 390 of 390 | positive | Y | LOG_ONLY | Y | OK | - |
| 2026-01-27 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 234.0 | available | 2026-01-27 17:59:53 | 5.0 | 46.5 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-28 | Wed | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 348.8 | available | 2026-01-28 17:59:59 | 5.6 | 33.1 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-29 | Thu | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 504.4 | available | 2026-01-29 17:59:59 | 4.2 | 36.7 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-01-30 | Fri | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 585.7 | available | 2026-01-30 15:59:59 | 2.7 | 29.0 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-02-02 | Mon | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 455.3 | available | 2026-02-02 17:59:58 | 6.1 | 20.6 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |
| 2026-02-03 | Tue | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 535.6 | available | 2026-02-03 17:59:59 | 2.3 | 42.4 | 390 / 390 of 390 | positive | Y | APPROVED | Y | OK | - |
| 2026-02-04 | Wed | FULL | 15:00 | UNEXPOSED | NQH6 | N | NQ_MAR26 | 607.0 | available | 2026-02-04 15:59:59 | 4.6 | 39.2 | 390 / 390 of 390 | negative | Y | APPROVED | Y | OK | - |

Exposed sessions (replay plan section 8):

- 2026-01-12: Part 3, How I Frame Every Trade (gold example)
- 2026-01-14: Part 3, How I Frame Every Trade (gold example)
- 2026-01-16: Part 3, How I Frame Every Trade (NQ example, NQH6; transcript-derived date, pending tape confirmation)

Calendar events on the sessions (logged; the plan applies its own rules):

- 2025-12-05: Personal income and outlays (PCE) (no_trade 08:58-09:15)
- 2025-12-10: FOMC decision + SEP + press conference (no_trade 12:45-15:00)
- 2025-12-15: NQ roll day (Dec 25 to Mar 26) (LOG_ONLY)
- 2025-12-16: Employment Situation (NFP) (no_trade 08:30-08:40); Retail sales (advance) (no_trade 08:30-08:40)
- 2025-12-18: CPI (no_trade 08:30-08:40)
- 2025-12-19: Quarterly expiration (quad witching) (none)
- 2025-12-23: GDP Q3 initial + PCE Jul-Sep updates (no_trade 08:30-08:40)
- 2025-12-24: Christmas Eve (half day) (LOG_ONLY)
- 2026-01-05: ISM Manufacturing PMI (no_trade 08:58-09:15)
- 2026-01-07: ISM Services PMI (no_trade 08:58-09:15)
- 2026-01-09: Employment Situation (NFP) (no_trade 08:30-08:40)
- 2026-01-13: CPI (no_trade 08:30-08:40)
- 2026-01-14: PPI (no_trade 08:30-08:40); Retail sales (advance) (no_trade 08:30-08:40)
- 2026-01-16: Monthly options expiration (none)
- 2026-01-22: GDP Q3 updated estimate (no_trade 08:30-08:40); Personal income and outlays (PCE) (no_trade 08:58-09:15)
- 2026-01-28: FOMC decision + press conference (no_trade 12:45-15:00)
- 2026-01-29: MSFT / META / TSLA earnings (Jan 28 after close) (max_trades=1)
- 2026-01-30: PPI (no_trade 08:30-08:40); AAPL earnings (Jan 29 after close) (max_trades=1)
- 2026-02-02: ISM Manufacturing PMI (no_trade 08:58-09:15)
- 2026-02-04: ISM Services PMI (no_trade 08:58-09:15)

Map packet data notes (gaps / notes written by map v2.3):

- 2025-12-05: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes DATA: prior-week profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT
- 2025-12-08: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes none
- 2025-12-09: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes none
- 2025-12-10: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes none
- 2025-12-11: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes none
- 2025-12-12: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes none
- 2025-12-15: gaps none; notes none
- 2025-12-16: gaps none; notes none
- 2025-12-17: gaps none; notes none
- 2025-12-18: gaps none; notes none
- 2025-12-19: gaps none; notes none
- 2025-12-22: gaps none; notes none
- 2025-12-23: gaps none; notes none
- 2025-12-24: gaps none; notes CALENDAR: half day today, cash session ends 12:00 CT (prompt check F: LOG_ONLY)
- 2025-12-26: gaps none; notes none
- 2025-12-29: gaps none; notes none
- 2025-12-30: gaps none; notes none
- 2025-12-31: gaps none; notes none
- 2026-01-02: gaps none; notes none
- 2026-01-05: gaps none; notes none
- 2026-01-06: gaps none; notes none
- 2026-01-07: gaps none; notes none
- 2026-01-08: gaps none; notes none
- 2026-01-09: gaps none; notes none
- 2026-01-12: gaps none; notes none
- 2026-01-13: gaps none; notes none
- 2026-01-14: gaps none; notes none
- 2026-01-15: gaps none; notes none
- 2026-01-16: gaps none; notes none
- 2026-01-20: gaps none; notes none
- 2026-01-21: gaps none; notes none
- 2026-01-22: gaps none; notes none
- 2026-01-23: gaps none; notes none
- 2026-01-26: gaps none; notes none
- 2026-01-27: gaps none; notes none
- 2026-01-28: gaps none; notes none
- 2026-01-29: gaps none; notes none
- 2026-01-30: gaps none; notes none
- 2026-02-02: gaps none; notes none
- 2026-02-03: gaps none; notes none
- 2026-02-04: gaps none; notes none
