# Book 1A Phase 1: R3 / R4 rerun with risk-c3-v2, mechanical P4 and P5 (phase1-checks-c3v2-v1.0)

No P&L, R, win rate or outcome is read or written here. Ledger columns read: date, entry_time, side, qty, entry_price, stop, target, exit_time, exit_price, exit_reason, risk_decision, trade_id, stop_ticks, planned_risk_usd, commission_usd, fill_model, stop_slippage_ticks, entry_latency_ms, risk_breach_fill, risk_impl_version, risk_decision_time, risk_ref_source, risk_entry_ref, signal_entry_ref, risk_budget_usd, entry_risk_ticks_at_fill, entry_risk_at_fill_usd, execution_variance_ticks, exec_risk_breach.

## Ledgers and versions

| strategy | ledger | rows | sha256 | risk_impl_version (rows) | manifest |
|---|---|---|---|---|---|
| R3 | `K:\Book1A_runner\code\book1a\Phase1\runs\phase1_r3_c3v2\R3_M0_ledger.csv` | 1 | `f413d15f4dad259d908390f6fcff659490f61cd5c9ce5a0f14a1bbeb486e71d1` | {'risk-c3-v2': 1} | version=run-r3-v1.1, commit=343fcf9402be5e107f3a98f17f31e907d40a4f87, risk_impl_version=risk-c3-v2, replay_risk_version=replay-risk-v1.1, ledger_version=ledger-v1.1, fill_model=v3.5; manifest sha256 = file |
| R4 | `K:\Book1A_runner\code\book1a\Phase1\runs\phase1_r4_c3v2\R4_M0_ledger.csv` | 8 | `b4510aabf2c750f6b3d0cb6f53de274989ed8acbc90d14c0dee9532a5ee5b409` | {'risk-c3-v2': 8} | version=run-r4-v1.1, commit=343fcf9402be5e107f3a98f17f31e907d40a4f87, risk_impl_version=risk-c3-v2, replay_risk_version=replay-risk-v1.1, ledger_version=ledger-v1.1, fill_model=v3.5; manifest sha256 = file |

## P4 risk mechanics with risk-c3-v2

Reference = best ask (long) / best bid (short) from the tape quote at the decision time (last trade at or before the bar close). Estimate = (stop ticks + 2) x $5 x N + $5.74 x N; N = the largest whole number with estimate <= min($1,000, remaining daily budget logged at the decision). Entry risk at fill = (|fill - stop| / 0.25 + 2) x $5 x N + $5.74 x N; breach = entry risk at fill > that cap. All in integer cents.

### Pre-trade decisions (every ACCEPT / RISK_REJECT row)

| strategy | event | decision time | side | ref logged / tape | stop ticks | decision | N logged / recomputed | estimate logged / recomputed | cap | impl | check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3 | JOFT-20251030-05780 | 2025-10-30 09:05:00 | SHORT | 26099.00 / 26099.00 | 336 | RISK_REJECT:PER_TRADE_BUDGET | 0 / 0 | 1695.74 / 1695.74 | 1000.00 | risk-c3-v2 | MATCH |
| R3 | JOFT-20251103-07485 | 2025-11-03 09:16:00 | SHORT | 26108.50 / 26108.50 | 191 | ACCEPT | 1 / 1 | 970.74 / 970.74 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251029-05249 | 2025-10-29 14:19:00 | LONG | 26190.00 / 26190.00 | 150 | ACCEPT | 1 / 1 | 765.74 / 765.74 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251030-05838 | 2025-10-30 09:05:00 | SHORT | 26099.00 / 26099.00 | 336 | RISK_REJECT:PER_TRADE_BUDGET | 0 / 0 | 1695.74 / 1695.74 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251030-05930 | 2025-10-30 09:56:00 | SHORT | 25994.75 / 25994.75 | 73 | ACCEPT | 2 / 2 | 761.48 / 761.48 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251030-06183 | 2025-10-30 12:32:00 | SHORT | 26037.50 / 26037.50 | 209 | RISK_REJECT:PER_TRADE_BUDGET | 0 / 0 | 1060.74 / 1060.74 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251031-06724 | 2025-10-31 08:52:00 | LONG | 26110.75 / 26110.75 | 40 | ACCEPT | 4 / 4 | 862.96 / 862.96 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251031-06763 | 2025-10-31 09:13:00 | LONG | 26099.75 / 26099.75 | 55 | ACCEPT | 3 / 3 | 872.22 / 872.22 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251103-07534 | 2025-11-03 08:55:00 | SHORT | 26136.75 / 26136.75 | 82 | ACCEPT | 2 / 2 | 851.48 / 851.48 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251103-07680 | 2025-11-03 10:01:00 | SHORT | 26074.75 / 26074.75 | 151 | ACCEPT | 1 / 1 | 770.74 / 770.74 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251103-07811 | 2025-11-03 11:20:00 | LONG | 26127.75 / 26127.75 | 38 | ACCEPT | 4 / 4 | 822.96 / 822.96 | 1000.00 | risk-c3-v2 | MATCH |
| R4 | JOFT-20251104-08968 | 2025-11-04 09:30:00 | SHORT | 25864.00 / 25864.00 | 121 | ACCEPT | 1 / 1 | 620.74 / 620.74 | 1000.00 | risk-c3-v2 | MATCH |

### Trades (every ledger row)

| strategy | trade | side | qty | ref | stop | stop ticks from ref (recomputed) | planned estimate | fill | variance ticks logged / recomputed | entry risk at fill logged / recomputed | cap logged / attempt | breach logged / recomputed | check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R3 | JOFT-20251103-07485 | SHORT | 1 | 26108.50 | 26156.25 | 191 | 970.74 | 26109.00 | -2 / -2 | 960.74 / 960.74 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251029-05249 | LONG | 1 | 26190.00 | 26152.50 | 150 | 765.74 | 26189.50 | -2 / -2 | 755.74 / 755.74 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251030-05930 | SHORT | 2 | 25994.75 | 26013.00 | 73 | 761.48 | 25995.25 | -2 / -2 | 741.48 / 741.48 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251031-06724 | LONG | 4 | 26110.75 | 26100.75 | 40 | 862.96 | 26110.25 | -2 / -2 | 822.96 / 822.96 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251031-06763 | LONG | 3 | 26099.75 | 26086.00 | 55 | 872.22 | 26101.75 | 8 / 8 | 992.22 / 992.22 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251103-07534 | SHORT | 2 | 26136.75 | 26157.25 | 82 | 851.48 | 26135.75 | 4 / 4 | 891.48 / 891.48 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251103-07680 | SHORT | 1 | 26074.75 | 26112.50 | 151 | 770.74 | 26074.75 | 0 / 0 | 770.74 / 770.74 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251103-07811 | LONG | 4 | 26127.75 | 26118.25 | 38 | 822.96 | 26128.25 | 2 / 2 | 862.96 / 862.96 | 1000.00 / 1000.00 | 0 / 0 | MATCH |
| R4 | JOFT-20251104-08968 | SHORT | 1 | 25864.00 | 25894.25 | 121 | 620.74 | 25862.75 | 5 / 5 | 645.74 / 645.74 | 1000.00 / 1000.00 | 0 / 0 | MATCH |

- pre-trade decisions recomputed: 12, mismatches **0**
- trades recomputed: 9, mismatches **0** (planned risk <= cap and qty = N are part of each row's check)
- attempt rows without `risk-c3-v2`: R3 0 / 11, R4 0 / 42
- qualifying entry risk-budget breaches (registered definition, logged only, listed not judged): 0

## P5 fill mechanics (independent tape recompute, every R3 / R4 trade)

| strategy | trade | side | qty | bar close + 250 ms | entry ledger / recomputed | exit reason ledger / recomputed | exit time ledger / recomputed | exit price ledger / recomputed | gap-through | result |
|---|---|---|---|---|---|---|---|---|---|---|
| R3 | JOFT-20251103-07485 | SHORT | 1 | 2025-11-03 09:16:00.250 | 26109.00 / 26109.00 | STOP_FIRST / STOP | 11:51:10.868 / 11:51:10.868 | 26156.50 / 26156.50 | no | MATCH |
| R4 | JOFT-20251029-05249 | LONG | 1 | 2025-10-29 14:19:00.250 | 26189.50 / 26189.50 | STOP_FIRST / STOP | 14:36:20.990 / 14:36:20.990 | 26152.00 / 26152.00 | YES | MATCH |
| R4 | JOFT-20251030-05930 | SHORT | 2 | 2025-10-30 09:56:00.250 | 25995.25 / 25995.25 | STOP_FIRST / STOP | 09:58:10.258 / 09:58:10.258 | 26013.25 / 26013.25 | no | MATCH |
| R4 | JOFT-20251031-06724 | LONG | 4 | 2025-10-31 08:52:00.250 | 26110.25 / 26110.25 | STOP_FIRST / STOP | 08:54:18.068 / 08:54:18.068 | 26100.25 / 26100.25 | YES | MATCH |
| R4 | JOFT-20251031-06763 | LONG | 3 | 2025-10-31 09:13:00.250 | 26101.75 / 26101.75 | STOP_FIRST / STOP | 09:14:43.129 / 09:14:43.129 | 26085.75 / 26085.75 | no | MATCH |
| R4 | JOFT-20251103-07534 | SHORT | 2 | 2025-11-03 08:55:00.250 | 26135.75 / 26135.75 | TARGET_FIRST / TARGET | 09:05:55.045 / 09:05:55.045 | 26095.00 / 26095.00 | no | MATCH |
| R4 | JOFT-20251103-07680 | SHORT | 1 | 2025-11-03 10:01:00.250 | 26074.75 / 26074.75 | STOP_FIRST / STOP | 10:56:59.487 / 10:56:59.487 | 26112.75 / 26112.75 | no | MATCH |
| R4 | JOFT-20251103-07811 | LONG | 4 | 2025-11-03 11:20:00.250 | 26128.25 / 26128.25 | STOP_FIRST / STOP | 11:25:17.994 / 11:25:17.994 | 26118.00 / 26118.00 | no | MATCH |
| R4 | JOFT-20251104-08968 | SHORT | 1 | 2025-11-04 09:30:00.250 | 25862.75 / 25862.75 | TARGET_FIRST / TARGET | 09:55:37.564 / 09:55:37.564 | 25798.50 / 25798.50 | no | MATCH |

- trades checked 9: MATCH 9, MISMATCH 0

