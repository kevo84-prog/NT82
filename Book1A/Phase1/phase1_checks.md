# Book 1A Phase 1: mechanics checks (phase1-checks-v1.0)

No P&L, R, win rate or dollar result is read or written here. Ledger columns read: date, entry_time, side, qty, entry_price, stop, target, exit_time, exit_price, exit_reason, risk_decision, trade_id, stop_ticks, planned_risk_usd, commission_usd, fill_model, stop_slippage_ticks, entry_latency_ms, risk_breach_fill.

## P1 sessions and row types

- A0 run sessions (daily_loop_config): 10 = 2025-10-22 .. 2025-11-04; equal to the Phase 1 list: True
- A0 (R1 / R2 / R3 signals): S1.4 log rows on 10 / 10 sessions; PLAN_LOADED on 10 / 10 (all)
  - row types present: 27; CANDIDATE 5732, CONFIG 1, CONFIRM 45, EVIDENCE 3455, EXIT_MODEL 423, EXIT_WARN 4074, FILL 14, HALT 2, IMBALANCE 1839, NOTE 12151, ORDER 7, ORDER_BLOCKED 95, OUTCOME 5732, PLAN 21, RESEARCH_NOENTRY 236, RESEARCH_OUTCOME 181, RESEARCH_SIGNAL 181, RETEST 1269, REVERSAL_CANDIDATE 198, REVERSAL_OUTCOME 198, SHADOW 3347, SHADOW_CONFIRM 20, SHADOW_OUTCOME 3347, STATE 20063, TRADE_CLOSED 7, ZONE_ACTIVE 172, ZONE_CREATED 1900
  - expected row types with 0 rows (row_types.csv): ['FLATTEN']
- R4 (Book 1A plans): S1.4 log rows on 10 / 10 sessions; PLAN_LOADED on 10 / 10 (all)
  - row types present: 27; CANDIDATE 5811, CONFIG 1, CONFIRM 57, EVIDENCE 3858, EXIT_MODEL 436, EXIT_WARN 4115, FILL 44, HALT 5, IMBALANCE 1839, NOTE 12702, ORDER 22, ORDER_BLOCKED 90, OUTCOME 5811, PLAN 20, RESEARCH_NOENTRY 248, RESEARCH_OUTCOME 208, RESEARCH_SIGNAL 208, RETEST 1308, REVERSAL_CANDIDATE 196, REVERSAL_OUTCOME 196, SHADOW 3659, SHADOW_CONFIRM 26, SHADOW_OUTCOME 3659, STATE 20603, TRADE_CLOSED 22, ZONE_ACTIVE 230, ZONE_CREATED 1900
- R1: ledger rows 7, on sessions ['2025-10-22', '2025-10-30', '2025-10-31', '2025-11-03']
- R2: ledger rows 2, on sessions ['2025-10-30', '2025-11-03']
- R3: ledger rows 1, on sessions ['2025-11-03']
- R4: ledger rows 8, on sessions ['2025-10-29', '2025-10-30', '2025-10-31', '2025-11-03', '2025-11-04']

## P3 tick test

- ledger prices checked: 72 (entry, stop, target, exit on every row); attempt prices: 166; off-tick: 0 
- plan files: `book1a/tests/test_plan_ticks.py` (run with the unit tests).

## P4 risk mechanics (R3, R4)

Formula: estimate = (stop ticks + 2) x $5 x N + $5.74 x N; N = largest whole number with estimate <= min($1,000, remaining daily budget); RISK_REJECT when 1 NQ does not fit.

- largest stop that fits $1,000 (recomputed): 1 NQ 196, 2 NQ 96, 3 NQ 63, 5 NQ 36, 10 NQ 16 ticks (spec: 196 / 96 / 63 / 36 / 16)

| strategy | event | time | decision | stop ticks | N logged | N recomputed | estimate logged | estimate recomputed | cap (min budget, remaining) | check |
|---|---|---|---|---|---|---|---|---|---|---|
| R3 | JOFT-20251030-05780 | 2025-10-30 09:05:00 | RISK_REJECT:PER_TRADE_BUDGET | 333 | 0 | 0 | 1680.74 | 1680.74 | 1000.00 | MATCH |
| R3 | JOFT-20251103-07485 | 2025-11-03 09:16:00 | ACCEPT | 191 | 1 | 1 | 970.74 | 970.74 | 1000.00 | MATCH |
| R4 | JOFT-20251029-05249 | 2025-10-29 14:19:00 | ACCEPT | 145 | 1 | 1 | 740.74 | 740.74 | 1000.00 | MATCH |
| R4 | JOFT-20251030-05838 | 2025-10-30 09:05:00 | RISK_REJECT:PER_TRADE_BUDGET | 333 | 0 | 0 | 1680.74 | 1680.74 | 1000.00 | MATCH |
| R4 | JOFT-20251030-05930 | 2025-10-30 09:56:00 | ACCEPT | 73 | 2 | 2 | 761.48 | 761.48 | 1000.00 | MATCH |
| R4 | JOFT-20251030-06183 | 2025-10-30 12:32:00 | RISK_REJECT:PER_TRADE_BUDGET | 209 | 0 | 0 | 1060.74 | 1060.74 | 1000.00 | MATCH |
| R4 | JOFT-20251031-06724 | 2025-10-31 08:52:00 | ACCEPT | 40 | 4 | 4 | 862.96 | 862.96 | 1000.00 | MATCH |
| R4 | JOFT-20251031-06763 | 2025-10-31 09:13:00 | ACCEPT | 55 | 3 | 3 | 872.22 | 872.22 | 1000.00 | MATCH |
| R4 | JOFT-20251103-07534 | 2025-11-03 08:55:00 | ACCEPT | 82 | 2 | 2 | 851.48 | 851.48 | 1000.00 | MATCH |
| R4 | JOFT-20251103-07680 | 2025-11-03 10:01:00 | ACCEPT | 151 | 1 | 1 | 770.74 | 770.74 | 1000.00 | MATCH |
| R4 | JOFT-20251103-07811 | 2025-11-03 11:20:00 | ACCEPT | 36 | 5 | 5 | 978.70 | 978.70 | 1000.00 | MATCH |
| R4 | JOFT-20251104-08968 | 2025-11-04 09:30:00 | ACCEPT | 121 | 1 | 1 | 620.74 | 620.74 | 1000.00 | MATCH |

- planned-risk violations (planned risk above min($1,000, remaining daily) at entry, or size != the logged N): **0** 
- RISK_REJECT / ACCEPT rows recomputed: mismatches **0**
- R3 RISK_BREACH_FILL (execution breaches, listed and counted, not judged): 0
- R4 RISK_BREACH_FILL (execution breaches, listed and counted, not judged): 3; 2025-10-29 JOFT-20251029-05249 exit STOP_FIRST 14:36:20.990; 2025-10-31 JOFT-20251031-06763 exit STOP_FIRST 09:14:43.129; 2025-11-03 JOFT-20251103-07811 exit STOP_FIRST 11:25:17.994

## P5 fill mechanics (independent tape recompute, every trade of R1-R4)

| strategy | trade | side | qty | bar close + 250 ms | entry ledger / recomputed | quote row time | stop / target | exit reason ledger / recomputed | exit time ledger / recomputed | exit price ledger / recomputed | gap-through | same-tick stop+target | commission per side | result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | JOFT-20251022-00153 | SHORT | 1 | 2025-10-22 08:34:00.250 | 25196.00 / 25196.00 | 08:34:00.232 | 25225.50 / 25119.75 | STOP_FIRST / STOP | 08:39:51.640 / 08:39:51.640 | 25225.75 / 25225.75 | no | no | 2.870 | MATCH |
| R1 | JOFT-20251022-00202 | SHORT | 1 | 2025-10-22 09:14:00.250 | 25224.00 / 25224.00 | 09:14:00.223 | 25242.25 / 25184.50 | STOP_FIRST / STOP | 09:19:14.802 / 09:19:14.802 | 25242.50 / 25242.50 | no | no | 2.870 | MATCH |
| R1 | JOFT-20251030-05681 | SHORT | 1 | 2025-10-30 08:33:00.250 | 26068.00 / 26068.00 | 08:33:00.202 | 26095.75 / 25990.00 | TARGET_FIRST / TARGET | 08:36:46.644 / 08:36:46.644 | 25990.00 / 25990.00 | no | no | 2.870 | MATCH |
| R1 | JOFT-20251031-06633 | SHORT | 1 | 2025-10-31 08:46:00.250 | 26094.50 / 26094.50 | 08:46:00.224 | 26134.00 / 25575.75 | STOP_FIRST / STOP | 09:36:18.546 / 09:36:18.546 | 26134.25 / 26134.25 | no | no | 2.870 | MATCH |
| R1 | JOFT-20251103-07390 | SHORT | 1 | 2025-11-03 08:38:00.250 | 26189.50 / 26189.50 | 08:38:00.023 | 26211.75 / 26150.00 | TARGET_FIRST / TARGET | 08:50:00.137 / 08:50:00.137 | 26150.00 / 26150.00 | no | no | 2.870 | MATCH |
| R1 | JOFT-20251103-07429 | SHORT | 1 | 2025-11-03 08:51:00.250 | 26132.25 / 26132.25 | 08:51:00.218 | 26159.00 / 26012.75 | STOP_FIRST / STOP | 11:57:23.847 / 11:57:23.847 | 26159.25 / 26159.25 | no | no | 2.870 | MATCH |
| R1 | JOFT-20251103-07751 | SHORT | 1 | 2025-11-03 12:22:00.250 | 26143.50 / 26143.50 | 12:22:00.236 | 26152.75 / 26129.75 | STOP_FIRST / STOP | 12:25:12.410 / 12:25:12.410 | 26153.00 / 26153.00 | no | no | 2.870 | MATCH |
| R2 | JOFT-20251030-05780 | SHORT | 1 | 2025-10-30 09:05:00.250 | 26100.00 / 26100.00 | 09:05:00.247 | 26183.00 / 25963.75 | TARGET_FIRST / TARGET | 14:05:18.715 / 14:05:18.715 | 25963.75 / 25963.75 | no | no | 2.870 | MATCH |
| R2 | JOFT-20251103-07485 | SHORT | 1 | 2025-11-03 09:16:00.250 | 26109.00 / 26109.00 | 09:16:00.182 | 26156.25 / 26012.75 | STOP_FIRST / STOP | 11:51:10.868 / 11:51:10.868 | 26156.50 / 26156.50 | no | no | 2.870 | MATCH |
| R3 | JOFT-20251103-07485 | SHORT | 1 | 2025-11-03 09:16:00.250 | 26109.00 / 26109.00 | 09:16:00.182 | 26156.25 / 26012.75 | STOP_FIRST / STOP | 11:51:10.868 / 11:51:10.868 | 26156.50 / 26156.50 | no | no | 2.870 | MATCH |
| R4 | JOFT-20251029-05249 | LONG | 1 | 2025-10-29 14:19:00.250 | 26189.50 / 26189.50 | 14:19:00.205 | 26152.50 / 26261.50 | STOP_FIRST / STOP | 14:36:20.990 / 14:36:20.990 | 26152.00 / 26152.00 | YES | no | 2.870 | MATCH |
| R4 | JOFT-20251030-05930 | SHORT | 2 | 2025-10-30 09:56:00.250 | 25995.25 / 25995.25 | 09:56:00.225 | 26013.00 / 25954.75 | STOP_FIRST / STOP | 09:58:10.258 / 09:58:10.258 | 26013.25 / 26013.25 | no | no | 2.870 | MATCH |
| R4 | JOFT-20251031-06724 | LONG | 4 | 2025-10-31 08:52:00.250 | 26110.25 / 26110.25 | 08:52:00.158 | 26100.75 / 26176.50 | STOP_FIRST / STOP | 08:54:18.068 / 08:54:18.068 | 26100.25 / 26100.25 | YES | no | 2.870 | MATCH |
| R4 | JOFT-20251031-06763 | LONG | 3 | 2025-10-31 09:13:00.250 | 26101.75 / 26101.75 | 09:13:00.205 | 26086.00 / 26142.50 | STOP_FIRST / STOP | 09:14:43.129 / 09:14:43.129 | 26085.75 / 26085.75 | no | no | 2.870 | MATCH |
| R4 | JOFT-20251103-07534 | SHORT | 2 | 2025-11-03 08:55:00.250 | 26135.75 / 26135.75 | 08:55:00.175 | 26157.25 / 26095.00 | TARGET_FIRST / TARGET | 09:05:55.045 / 09:05:55.045 | 26095.00 / 26095.00 | no | no | 2.870 | MATCH |
| R4 | JOFT-20251103-07680 | SHORT | 1 | 2025-11-03 10:01:00.250 | 26074.75 / 26074.75 | 10:01:00.189 | 26112.50 / 26012.75 | STOP_FIRST / STOP | 10:56:59.487 / 10:56:59.487 | 26112.75 / 26112.75 | no | no | 2.870 | MATCH |
| R4 | JOFT-20251103-07811 | LONG | 5 | 2025-11-03 11:20:00.250 | 26128.25 / 26128.25 | 11:20:00.088 | 26118.25 / 26151.00 | STOP_FIRST / STOP | 11:25:17.994 / 11:25:17.994 | 26118.00 / 26118.00 | no | no | 2.870 | MATCH |
| R4 | JOFT-20251104-08968 | SHORT | 1 | 2025-11-04 09:30:00.250 | 25862.75 / 25862.75 | 09:30:00.247 | 25894.25 / 25798.50 | TARGET_FIRST / TARGET | 09:55:37.564 / 09:55:37.564 | 25798.50 / 25798.50 | no | no | 2.870 | MATCH |

- trades checked 18: MATCH 18, MISMATCH 0; stops 13, targets 5, gap-through 2

## P6 context mechanics (R4)

| day | plan market_context | plan context= (S1.4) | PLAN_ACTIVE context | context_source | draw_status | invalidate_below / above | PLAN_CONTEXT_CHANGE rows | longest run of 1-minute closes beyond the line after 08:25 CT | check |
|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | BALANCED | Balanced | Balanced | NONE | NONE | - / - | 0 | - | MATCH |
| 2025-10-23 | BALANCED | Balanced | Balanced | NONE | NONE | - / - | 0 | - | MATCH |
| 2025-10-24 | NONE | None | None | NONE | NONE | - / - | 0 | - | MATCH |
| 2025-10-27 | BULLISH | Bullish | Bullish | HTF_ACCEPTANCE | ACTIVE | 25394.25|Balanced / - | 0 | below 25394.25: 0 | MATCH |
| 2025-10-28 | BALANCED | Balanced | Balanced | NONE | NONE | - / - | 0 | - | MATCH |
| 2025-10-29 | BULLISH | Bullish | Bullish | HTF_ACCEPTANCE | ACTIVE | 25394.25|Balanced / - | 0 | below 25394.25: 0 | MATCH |
| 2025-10-30 | BALANCED | Balanced | Balanced | NONE | NONE | - / - | 0 | - | MATCH |
| 2025-10-31 | BULLISH | Bullish | Bullish | HTF_ACCEPTANCE | ACTIVE | 25394.25|Balanced / - | 0 | below 25394.25: 0 | MATCH |
| 2025-11-03 | BALANCED | Balanced | Balanced | NONE | NONE | - / - | 0 | - | MATCH |
| 2025-11-04 | NONE | None | None | NONE | NONE | - / - | 0 | - | MATCH |

- days checked 10, mismatches **0**. A switch needs 3 consecutive 1-minute closes strictly beyond the line (S1.4 `UpdatePlanState`, AcceptBars = 3); bars used: the run's nq_1m.csv, bars closing after 08:25 CT up to 15:00 CT.
