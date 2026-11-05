# E24 check: blank reward_risk (S1.4 RewardRisk)

Run: `phase1_r4`; MinRewardRisk = 1.5.

| # | check | rows checked | failures |
|---|---|---|---|
| 1 | blank only where there is no target or no positive risk | 143 blank of 9530 | 0 |
| 2 | no blank row is Qualified | 143 | 0 |
| 3 | R4_candidates.csv keeps the log text (blank stays blank, never 0) | 2058 (23 blank) | 0 (blank turned into a value: 0) |
| 4 | every attempt is Qualified, has a target and RewardRisk >= 1.5 | 43 attempts | 0 |

Blank rows by record and status: CANDIDATE/EventOnly 5, CANDIDATE/Pending 1, CANDIDATE/Rejected 76, CONFIRM/EventOnly 38, SHADOW/EventOnly 3, SHADOW/Pending 1, SHADOW/Rejected 19

Result: PASS
