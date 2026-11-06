# P0.6 hand check: 08:10 CT VWAP

generated 2026-11-01T22:13:37-06:00

| day | scope | window start CT | files | front id | trades hand | trades module | vwap hand | vwap module | sd hand | sd module | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-22 | SESSION | 2025-10-21T17:00:00-05:00 | glbx-mdp3-20251021.mbo.dbn.zst, glbx-mdp3-20251022.mbo.dbn.zst | 158704 | 56808 | 56808 | 25267.379648 | 25267.379648 | 29.249935 | 29.249935 | PASS |
| 2025-10-22 | WEEKLY | 2025-10-19T17:00:00-05:00 | glbx-mdp3-20251021.mbo.dbn.zst, glbx-mdp3-20251022.mbo.dbn.zst | 158704 | 341243 | 341243 | 25280.433866 | 25280.433866 | 31.868837 | 31.868837 | PASS |
| 2025-11-05 | SESSION | 2025-11-04T17:00:00-06:00 | glbx-mdp3-20251104.mbo.dbn.zst, glbx-mdp3-20251105.mbo.dbn.zst | 158704 | 126139 | 126139 | 25464.252037 | 25464.252037 | 78.513881 | 78.513881 | PASS |
| 2025-11-05 | WEEKLY | 2025-11-02T17:00:00-06:00 | glbx-mdp3-20251104.mbo.dbn.zst, glbx-mdp3-20251105.mbo.dbn.zst | 158704 | 568439 | 568439 | 25674.355143 | 25674.355143 | 146.652217 | 146.652217 | PASS |
| 2025-12-15 | SESSION | 2025-12-14T17:00:00-06:00 | glbx-mdp3-20251214.mbo.dbn.zst, glbx-mdp3-20251214.mbo.dbn.zst, glbx-mdp3-20251215.mbo.dbn.zst, glbx-mdp3-20251215.mbo.dbn.zst | 42002475 | 32709 | 32709 | 25544.449065 | 25544.449065 | 64.274627 | 64.274627 | PASS |
| 2025-12-15 | WEEKLY | 2025-12-14T17:00:00-06:00 | glbx-mdp3-20251214.mbo.dbn.zst, glbx-mdp3-20251214.mbo.dbn.zst, glbx-mdp3-20251215.mbo.dbn.zst, glbx-mdp3-20251215.mbo.dbn.zst | 42002475 | 32709 | 32709 | 25544.449065 | 25544.449065 | 64.274627 | 64.274627 | PASS |
| 2026-03-16 | SESSION | 2026-03-15T17:00:00-05:00 | glbx-mdp3-20260315.mbo.dbn.zst, glbx-mdp3-20260315.mbo.dbn.zst, glbx-mdp3-20260316.mbo.dbn.zst, glbx-mdp3-20260316.mbo.dbn.zst | 42004058 | 55890 | 55890 | 24756.317678 | 24756.317678 | 84.639794 | 84.639794 | PASS |
| 2026-03-16 | WEEKLY | 2026-03-15T17:00:00-05:00 | glbx-mdp3-20260315.mbo.dbn.zst, glbx-mdp3-20260315.mbo.dbn.zst, glbx-mdp3-20260316.mbo.dbn.zst, glbx-mdp3-20260316.mbo.dbn.zst | 42004058 | 55890 | 55890 | 24756.317678 | 24756.317678 | 84.639794 | 84.639794 | PASS |

**Overall: PASS**

Hand calculation: pandas sum(price x size) / sum(size) and sqrt(sum(size x (price - vwap)^2) / sum(size)) over trade
messages (action T, size > 0, not snapshot) of the front contract, ts_event in [window start, 08:10:00 CT).
