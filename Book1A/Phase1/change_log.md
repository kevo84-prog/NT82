# Book 1A runner change log

Changes to runner code that change what a strategy does. Bugs go to the bug log; this file holds registered
corrections. The same rows belong in the replay plan's section 11 on Drive (Kyron edits the Drive doc).

| Date | Change | Docs / code | Type |
|---|---|---|---|
| Nov 5, 2026 (decision), Nov 6, 2026 (code) | risk-c3-v2: the C3 pre-trade risk check and N use the best ask (long) / best bid (short) at the decision time instead of the signal-bar reference; execution-breach definition registered (entry risk at fill > min($1,000, remaining daily budget at the decision); logged only, no exit or resize); realized loss overrun reported separately and not counted toward the Phase 4 gate; implementation version written into every R3 / R4 ledger row; risk-c3-v1 kept unchanged for reproduction; Phase 0 and Phase 1 R3 / R4 ledgers, hashes and parity reports preserved | `Phase1/risk-c3-v2_registration.md`; `risk.py`, `replay_risk.py`, `run_r3.py`, `run_r4.py`, `ledger.py` | Material timing and sizing implementation correction (Kyron, Option B) |
