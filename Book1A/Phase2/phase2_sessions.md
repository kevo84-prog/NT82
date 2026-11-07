# Book 1A Phase 2 sessions and inputs (phase2-sessions-v1.0, Step A1, Nov 6, 2026)

Inputs only: no ledger, strategy log or fill was read. Book 1 calendar (`book1a/sessions.py`, `econ_calendar_2025-10_2026-04.csv`); exposure from replay plan section 8; contracts and session type from the data-integrity table of the read-only Book 1 reference copy; tape, bar, GEX and plan checks from the files themselves. A session with a missing input would be DATA_MISSING with its cause; none is dropped.

Sessions: 21; EXPOSED 8; UNEXPOSED 13; DATA_MISSING 0.

| session | day | type | close CT | exposure | front (NT roll) | MBO file MB | Databento condition | tape last trade | max gap RTH s | max gap overnight s | NQ / ES RTH bars | GEX regime | GEX V3 repro | plan review | status | cause |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-11-05 | Wed | FULL | 15:00 | UNEXPOSED | NQZ5 | 351.6 | available | 2025-11-05 17:59:58 | 5.1 | 26.8 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-06 | Thu | FULL | 15:00 | UNEXPOSED | NQZ5 | 459.8 | available | 2025-11-06 17:59:59 | 3.8 | 37.3 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-07 | Fri | FULL | 15:00 | UNEXPOSED | NQZ5 | 460.8 | available | 2025-11-07 15:59:59 | 2.8 | 29.9 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-10 | Mon | FULL | 15:00 | UNEXPOSED | NQZ5 | 331.6 | available | 2025-11-10 17:59:56 | 4.7 | 30.1 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-11 | Tue | FULL | 15:00 | UNEXPOSED | NQZ5 | 325.8 | available | 2025-11-11 17:59:59 | 5.1 | 27.5 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-12 | Wed | FULL | 15:00 | UNEXPOSED | NQZ5 | 400.6 | available | 2025-11-12 17:59:59 | 4.9 | 34.8 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-13 | Thu | FULL | 15:00 | UNEXPOSED | NQZ5 | 534.9 | available | 2025-11-13 17:59:59 | 2.2 | 39.7 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-14 | Fri | FULL | 15:00 | UNEXPOSED | NQZ5 | 576.6 | available | 2025-11-14 15:59:59 | 4.2 | 24.2 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-17 | Mon | FULL | 15:00 | EXPOSED | NQZ5 | 520.3 | available | 2025-11-17 17:59:59 | 3.0 | 28.7 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-18 | Tue | FULL | 15:00 | EXPOSED | NQZ5 | 612.5 | available | 2025-11-18 17:59:57 | 3.2 | 35.3 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-19 | Wed | FULL | 15:00 | EXPOSED | NQZ5 | 538.9 | available | 2025-11-19 17:59:59 | 3.8 | 35.3 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-20 | Thu | FULL | 15:00 | EXPOSED | NQZ5 | 672.6 | available | 2025-11-20 17:59:59 | 2.3 | 28.9 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-21 | Fri | FULL | 15:00 | EXPOSED | NQZ5 | 699.6 | available | 2025-11-21 15:59:59 | 4.2 | 21.9 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-24 | Mon | FULL | 15:00 | EXPOSED | NQZ5 | 403.1 | available | 2025-11-24 17:59:59 | 3.7 | 34.0 | 390 / 390 of 390 | negative | Y | APPROVED | OK | - |
| 2025-11-25 | Tue | FULL | 15:00 | EXPOSED | NQZ5 | 443.0 | available | 2025-11-25 17:59:58 | 4.0 | 39.8 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-26 | Wed | FULL | 15:00 | EXPOSED | NQZ5 | 321.3 | available | 2025-11-26 17:59:57 | 4.6 | 32.6 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-11-28 | Fri | HALF_DAY | 12:15 | UNEXPOSED | NQZ5 | 64.3 | degraded | 2025-11-28 12:14:59 | 5.2 | 38745.2 | 225 / 225 of 225 | positive | Y | LOG_ONLY | OK | - |
| 2025-12-01 | Mon | FULL | 15:00 | UNEXPOSED | NQZ5 | 387.6 | available | 2025-12-01 17:59:57 | 5.4 | 35.8 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-12-02 | Tue | FULL | 15:00 | UNEXPOSED | NQZ5 | 400.3 | available | 2025-12-02 17:59:56 | 4.8 | 48.0 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-12-03 | Wed | FULL | 15:00 | UNEXPOSED | NQZ5 | 309.7 | available | 2025-12-03 17:59:54 | 7.3 | 52.6 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |
| 2025-12-04 | Thu | FULL | 15:00 | UNEXPOSED | NQZ5 | 338.7 | available | 2025-12-04 17:59:59 | 4.5 | 49.1 | 390 / 390 of 390 | positive | Y | APPROVED | OK | - |

Calendar events on the sessions (logged; the plan applies its own rules):

- 2025-11-05: ISM Services PMI (no_trade 08:58-09:15)
- 2025-11-20: Employment Situation (NFP) (no_trade 08:30-08:40); NVDA earnings (Nov 19 after close) (max_trades=1)
- 2025-11-21: Monthly options expiration (none)
- 2025-11-25: PPI (no_trade 08:30-08:40); Retail sales (advance) (no_trade 08:30-08:40)
- 2025-11-28: Day after Thanksgiving (half day) (LOG_ONLY)
- 2025-12-01: ISM Manufacturing PMI (no_trade 08:58-09:15)
- 2025-12-03: ISM Services PMI (no_trade 08:58-09:15)

Map packet data notes (gaps / notes written by map v2.3):

- 2025-11-05: gaps none; notes none
- 2025-11-06: gaps none; notes none
- 2025-11-07: gaps none; notes none
- 2025-11-10: gaps none; notes none
- 2025-11-11: gaps none; notes none
- 2025-11-12: gaps none; notes none
- 2025-11-13: gaps none; notes none
- 2025-11-14: gaps none; notes none
- 2025-11-17: gaps none; notes none
- 2025-11-18: gaps none; notes none
- 2025-11-19: gaps none; notes none
- 2025-11-20: gaps none; notes none
- 2025-11-21: gaps none; notes none
- 2025-11-24: gaps none; notes none
- 2025-11-25: gaps none; notes none
- 2025-11-26: gaps none; notes none
- 2025-11-28: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes CALENDAR: half day today, cash session ends 12:00 CT (prompt check F: LOG_ONLY); DATA: overnight/VWAP window left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT; DATA: weekly profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT
- 2025-12-01: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes DATA: prior-week profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT
- 2025-12-02: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes DATA: prior-week profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT
- 2025-12-03: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes DATA: prior-week profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT
- 2025-12-04: gaps {'from': '2025-11-27 20:44 CT', 'to': '2025-11-28 07:30 CT'}; notes DATA: prior-week profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT
