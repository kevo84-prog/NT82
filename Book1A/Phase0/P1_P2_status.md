# P1 and P2 items: readiness and the replay path each takes (replay plan sections 5, 7, 10)

| # | Item | Ready? | Replay path if not ready (from the replay plan / checklist) |
|---|---|---|---|
| P1.1 | Gamma ranks (U6) | Ranking function built and hand-tested (`book1a/gamma_ranks.py`); the per-strike net GEX hook to `gex_block1.py` / `mq_levels` runs on the PC (D-1 option files). Not yet run. | U6: if not built before the replay, ranks are left out of the GEX family (call resistance, put support, HVL, 0DTE levels still count). |
| P1.2 | Calculated GEX levels and available_at | Check script built (`book1a/gex_check.py`); runs on `gex_levels_block1.csv` on the PC. available_at = D-1 23:00 ET (before 08:10 CT). | Checklist: if the levels cannot be confirmed the replay cannot use the GEX family: stop and fix. |
| P2.1 | L2 diagnostics E1, E2, E4 (Book 1B) | Not started. Needs the L2F audit, the fixed-price build and the coverage list. | U11: if those are not done, E1, E2 and E4 are not run; nothing else changes. |
| P2.2 | CVD_DIV and BREAKOUT_SPEED (Book 1D) | Not started (tag columns are present as null in the candidate log). | Logged only; Phase 1 definition check on Oct 24, 27, 28, 29, 2025 documented, never tuned. |
| P2.3 | Exit diagnostics M-J1, M-J2, exit cue (a) | Not started. The exit engine (`exit_replay.replay` with several legs) supports them. | Diagnostics beside M0; R4 stays M0 (E1). M-J3 / M-J4 deferred (U4, U5). |
| P2.4 | GEX diagnostics V2, V3, V5, volatility control, context GEX tags | Not started. V2 needs a fixed seed; the volatility control needs ATM IV terciles from the option files. | Reported only; never promoted. |
| P2.5 | Quantower-style power-trade rebuild (U2) | Not started. | Logged only; S1.4's single print stays the gate for R4. |
| P2.6 | 10 NQ and MNQ feasibility | Formula ready (`risk.estimate_risk_cents` with N = 10; MNQ = $0.50 per tick, $1.88 round trip via a `RiskConfig(tick_value_cents=50, commission_rt_cents=188)`). Not run. | Hypothetical / diagnostic only. |
| P2.7 | Parameter sensitivity (section 12) | Not started; every baseline value is a named constant in the modules (map_v24, families, plan_fields, risk). | Diagnostic only; one parameter at a time after P0 passes. |
| P2.8 | All-time-high profile (O1) | Not started. | E6: research only; logged with overlap. |
| P2.9 | Every other logged tag | Columns present and null when not measurable (`candidate_log.py`); measurement code for the Book 1A-only tags (VWAP grade, re-entry, stacked imbalances, exhaustion, TF alignment, wick stop, retest at new imbalance, light proof, counter-context proof) not yet written. | Present as null; measured in Phase 1 shakedown work, never used as gates. |
