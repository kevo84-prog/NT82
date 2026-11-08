"""phase3_compare on synthetic trades only (no Phase 1-3 ledger is read). Book 1's arms.promotion is called unchanged."""
import copy
import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from book1a import phase2_report as RP, phase3_compare as PC, sessions as S
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import arms

SESS = [d.isoformat() for d in S.phase_sessions("phase3")]
EXPOSED = sorted(d.isoformat() for d in RP.EXPOSED_BY_PHASE["phase3"])
UNEXP = [d for d in SESS if d not in EXPOSED]


def tr(date, st="10:00:00", R=1.0, entry=100.0, exit=101.0, exit_time=None):
    return dict(date=date, signal_time=st, entry=entry, exit=exit, exit_time=exit_time or f"{date} 11:00:00.000", R=R)


def one(trades_arm, trades_comp, arm2=None, comp2=None, sessions=SESS, exposed=EXPOSED):
    t = {"R4": trades_arm, "R1": trades_comp}
    t2 = {"R4": trades_arm if arm2 is None else arm2, "R1": trades_comp if comp2 is None else comp2}
    return PC.compare(t, t2, sessions, exposed, comparisons=(("P1", "R4", "R1"),))["P1"]


class TestRuleThroughWrapper(unittest.TestCase):
    def test_sessions_and_labels(self):
        self.assertEqual((len(SESS), len(UNEXP)), (41, 38))
        r = one([tr(SESS[0])], [])
        self.assertEqual(r["ALL"]["sessions"], 41); self.assertEqual(r["UNEXPOSED"]["sessions"], 38)
        self.assertEqual(r["label_ALL"], "in-sample, includes 3 exposed sessions (Part 3)")
        self.assertEqual(r["deciding_population"], "ALL")
        self.assertIn("not independent, not out-of-sample", r["label_UNEXPOSED"])

    def test_no_trade_sessions_count_as_zero(self):
        r = one([tr(SESS[0], R=4.1)], [])
        self.assertAlmostEqual(r["ALL"]["mean_diff_per_session"], 4.1 / 41)
        r0 = one([], [])
        self.assertEqual(r0["ALL"]["mean_diff_per_session"], 0.0)
        self.assertEqual(r0["ALL"]["verdict"], "insufficient evidence")

    def test_ties_identical_strategies(self):
        ts = [tr(d, R=(1.0 if i % 2 else -1.0)) for i, d in enumerate(SESS)]
        r = one(ts, copy.deepcopy(ts))
        self.assertEqual(r["ALL"]["differing"]["total"], 0)
        self.assertEqual((r["ALL"]["ci90_low"], r["ALL"]["ci90_high"]), (0.0, 0.0))
        self.assertEqual(r["ALL"]["verdict"], "insufficient evidence")

    def test_positive_delta_promotes(self):
        r = one([tr(d) for d in SESS], [])
        self.assertEqual(r["ALL"]["ci90_low"], 1.0)
        self.assertEqual(r["ALL"]["verdict"], "promote"); self.assertEqual(r["sensitivity"], PC.SAME)

    def test_negative_delta_upper_bound_le_0_rejects(self):
        r = one([], [tr(d) for d in SESS])
        self.assertLessEqual(r["ALL"]["ci90_high"], 0.0)
        self.assertTrue(r["ALL"]["checks"]["sample"])
        self.assertEqual(r["ALL"]["verdict"], "reject")

    def test_19_vs_20_differing(self):
        r19 = one([tr(d) for d in SESS[:19]], [])
        r20 = one([tr(d) for d in SESS[:20]], [])
        self.assertEqual(r19["ALL"]["differing"]["total"], 19); self.assertFalse(r19["ALL"]["checks"]["sample"])
        self.assertGreater(r19["ALL"]["ci90_low"], 0.0)
        self.assertEqual(r19["ALL"]["verdict"], "insufficient evidence")   # lower bound > 0 but < 20 trades
        self.assertEqual(r20["ALL"]["differing"]["total"], 20); self.assertTrue(r20["ALL"]["checks"]["sample"])
        self.assertEqual(r20["ALL"]["verdict"], "promote")

    def test_lower_bound_exactly_zero(self):
        # 20 differing trades netting 0 per session on 10 sessions, one +1 session: P(resample misses it) ~ 0.36 > 5 %
        arm = [tr(d, "10:00:00", 1.0) for d in SESS[:10]] + [tr(d, "10:30:00", -1.0) for d in SESS[:10]] + [tr(SESS[10])]
        r = one(arm, [])
        self.assertEqual(r["ALL"]["ci90_low"], 0.0); self.assertGreater(r["ALL"]["ci90_high"], 0.0)
        self.assertFalse(r["ALL"]["checks"]["bound"])
        self.assertEqual(r["ALL"]["verdict"], "insufficient evidence")

    def test_drawdown_exactly_1_25x(self):
        base = [tr(d) for d in SESS]                                      # 41 differing (admitted), x > 0
        comp = [tr(SESS[0], "09:00:00", -4.0, entry=1.0)]                  # comparator DD 4
        ok = base + [tr(SESS[0], "09:00:00", -5.0, entry=2.0)]             # arm DD 5 = 1.25 x 4
        bad = base + [tr(SESS[0], "09:00:00", -5.25, entry=2.0)]           # arm DD 5.25
        r_ok, r_bad = one(ok, comp), one(bad, comp)
        self.assertEqual((r_ok["ALL"]["max_dd_arm"], r_ok["ALL"]["max_dd_a0"]), (5.0, 4.0))
        self.assertTrue(r_ok["ALL"]["checks"]["drawdown"]); self.assertFalse(r_bad["ALL"]["checks"]["drawdown"])

    def test_comparator_drawdown_zero(self):
        comp = [tr(SESS[0], "09:00:00", 0.5, entry=1.0)]
        r0 = one([tr(d) for d in SESS], comp)
        r1 = one([tr(d) for d in SESS] + [tr(SESS[1], "09:00:00", -0.5)], comp)
        self.assertEqual(r0["ALL"]["max_dd_a0"], 0.0)
        self.assertTrue(r0["ALL"]["checks"]["drawdown"]); self.assertFalse(r1["ALL"]["checks"]["drawdown"])

    def test_lower_bound_positive_with_drawdown_failure_rejects(self):
        arm = [tr(d) for d in SESS] + [tr(SESS[0], "09:00:00", -0.5)]
        r = one(arm, [])
        self.assertGreater(r["ALL"]["ci90_low"], 0.0); self.assertFalse(r["ALL"]["checks"]["drawdown"])
        self.assertEqual(r["ALL"]["verdict"], "reject")

    def test_slip2_failure(self):
        arm = [tr(d) for d in SESS]
        r = one(arm, [], arm2=[], comp2=[tr(d, R=0.5) for d in SESS])
        self.assertLess(r["ALL"]["mean_diff_per_session_2tick"], 0)
        self.assertFalse(r["ALL"]["checks"]["two_tick"]); self.assertEqual(r["ALL"]["verdict"], "reject")

    def test_duplicate_key_raises(self):
        with self.assertRaises(PC.CompareInputError):
            one([tr(SESS[0]), tr(SESS[0], entry=99.0)], [])
        with self.assertRaises(PC.CompareInputError):
            one([], [tr(SESS[3]), tr(SESS[3])])

    def test_trade_outside_sessions_raises(self):
        with self.assertRaises(PC.CompareInputError):
            one([tr("2025-12-25")], [])
        with self.assertRaises(PC.CompareInputError):
            one([], [], arm2=[tr("2026-02-05")])

    def test_seed_reproduction(self):
        rng = np.random.default_rng(7)
        arm = [tr(d, R=float(rng.normal(0.2, 1))) for d in SESS]
        a, b = one(arm, []), one(copy.deepcopy(arm), [])
        self.assertEqual(a, b)
        x = np.array([t["R"] for t in arm])
        g = np.random.default_rng(20251205)
        lo, hi = np.percentile(x[g.integers(0, 41, size=(10_000, 41))].mean(axis=1), [5, 95])
        self.assertEqual((a["ALL"]["ci90_low"], a["ALL"]["ci90_high"]), (float(lo), float(hi)))

    def test_session_order_passed_unchanged(self):
        seen = []

        def spy(arm, a0, sessions, arm_2t=None, a0_2t=None):
            seen.append(list(sessions)); return arms.promotion(arm, a0, sessions, arm_2t=arm_2t, a0_2t=a0_2t)
        t = {"R4": [tr(SESS[5])], "R1": []}
        PC.compare(t, t, SESS, EXPOSED, promotion=spy, comparisons=(("P1", "R4", "R1"),))
        self.assertEqual(seen, [SESS, UNEXP])

    def test_unexposed_population_drops_exposed_trades(self):
        arm = [tr(d) for d in EXPOSED]
        r = one(arm, [])
        self.assertEqual(r["ALL"]["differing"]["total"], 3); self.assertEqual(r["UNEXPOSED"]["differing"]["total"], 0)
        self.assertEqual(r["UNEXPOSED"]["mean_diff_per_session"], 0.0)

    def test_sensitivity_label(self):
        arm =[tr(d) for d in UNEXP[:19]] + [tr(d) for d in EXPOSED]               # ALL 22, UNEXPOSED 19
        r = one(arm, [])
        self.assertEqual((r["ALL"]["verdict"], r["UNEXPOSED"]["verdict"]), ("promote", "insufficient evidence"))
        self.assertEqual(r["sensitivity"], "SENSITIVE_TO_EXPOSED_SESSIONS")

    def test_returns_exactly_arms_promotion(self):
        rng = np.random.default_rng(11)
        arm = [tr(d, f"1{i % 5}:00:00", float(rng.normal(0.1, 1))) for i, d in enumerate(SESS)]
        comp = [tr(d, "10:00:00", float(rng.normal(0, 1))) for d in SESS[::2]]
        arm2 = [dict(t, R=t["R"] - 0.1) for t in arm]; comp2 = [dict(t, R=t["R"] - 0.1) for t in comp]
        t, t2 = {"R4": arm, "R1": comp}, {"R4": arm2, "R1": comp2}
        res = PC.compare(t, t2, SESS, EXPOSED, comparisons=(("P1", "R4", "R1"),))["P1"]
        direct = arms.promotion({"trades": arm}, {"trades": comp}, SESS, arm_2t={"trades": arm2}, a0_2t={"trades": comp2})
        self.assertEqual(res["ALL"], direct)
        keep = set(UNEXP); f = lambda ts: [x for x in ts if x["date"] in keep]  # noqa: E731
        direct_u = arms.promotion({"trades": f(arm)}, {"trades": f(comp)}, UNEXP, arm_2t={"trades": f(arm2)},
                                  a0_2t={"trades": f(comp2)})
        self.assertEqual(res["UNEXPOSED"], direct_u)
        self.assertIs(PC.promotion_fn(), arms.promotion)


def lrow(tid, date, entry_time, R="1.5", theo="9.9", **kw):
    r = dict(trade_id=tid, date=date, entry_time=entry_time, entry_price="100.0", exit_price="101.0",
             exit_time="11:00:00.000", realized_net_R=R, theoretical_R=theo, net_usd="999", entry_latency_ms="250")
    r.update(kw); return r


class TestMapping(unittest.TestCase):
    D = SESS[0]

    def test_immediate_signal_time_from_attempt(self):
        led = [lrow("E1", self.D, "09:31:00.250")]
        att = [dict(event="E1", time=f"{self.D} 09:31:00", reasons=""), dict(event="E2", time=f"{self.D} 09:40:00", reasons="GRADE_NOT_ALLOWED")]
        t = PC.map_trades(led, att, [], "R1")[0]
        self.assertEqual(t["signal_time"], "09:31:00"); self.assertEqual(t["exit_time"], f"{self.D} 11:00:00.000")
        self.assertEqual((t["entry"], t["exit"]), (100.0, 101.0))

    def test_retest_signal_time_is_queueing_bar(self):
        led = [lrow("E1", self.D, "09:45:00.250")]
        att = [dict(event="E1", time=f"{self.D} 09:45:00", reasons="")]           # replay_risk stamps te
        ret = [dict(event="E1", time=f"{self.D} 09:31:00", outcome="RETEST_ENTERED", at=f"{self.D} 09:45:00")]
        self.assertEqual(PC.map_trades(led, att, ret, "R4")[0]["signal_time"], "09:31:00")

    def test_R_is_realized_net_R(self):
        t = PC.map_trades([lrow("E1", self.D, "09:31:00.250", R="-0.8732")],
                          [dict(event="E1", time=f"{self.D} 09:31:00", reasons="")], [], "R3")[0]
        self.assertEqual(t["R"], -0.8732)
        self.assertEqual(PC.map_stress([lrow("E1", self.D, "x", R="0.25")], "R3")[0]["R"], 0.25)
        with self.assertRaises(PC.CompareInputError):
            PC.map_stress([lrow("E1", self.D, "x", R="")], "R3")

    def test_mapping_errors(self):
        att = [dict(event="E1", time=f"{self.D} 09:31:00", reasons="")]
        with self.assertRaises(PC.CompareInputError):      # entry_time not the attempt bar + latency
            PC.map_trades([lrow("E1", self.D, "09:32:00.250")], att, [], "R1")
        with self.assertRaises(PC.CompareInputError):      # no attempts row
            PC.map_trades([lrow("E9", self.D, "09:31:00.250")], att, [], "R1")
        with self.assertRaises(PC.CompareInputError):      # duplicate trade_id
            PC.map_trades([lrow("E1", self.D, "09:31:00.250")] * 2, att, [], "R1")
        with self.assertRaisesRegex(PC.CompareInputError, "duplicate \\(date, signal_time\\)"):
            PC.map_trades([lrow("E1", self.D, "09:31:00.250"), lrow("E2", self.D, "09:31:00.650")],
                          att + [dict(event="E2", time=f"{self.D} 09:31:00.400", reasons="")], [], "R1")


class TestRunFiles(unittest.TestCase):
    def test_run_on_synthetic_folders(self):
        cols = ["trade_id", "date", "entry_time", "entry_price", "exit_price", "exit_time", "realized_net_R", "entry_latency_ms"]

        def write(p, rows, fields):
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); runs = {k: td / k for k in ("a0", "r3", "r4")}
            for k, (rk, led, att, _ret) in PC.FILES.items():
                n = {"R1": 3, "R2": 5, "R3": 8, "R4": 21}[k]
                rows = [lrow(f"{k}_{i}", SESS[i], "10:00:00.250", R=str(0.5 if k == "R4" else 0.1)) for i in range(n)]
                write(runs[rk] / led, rows, cols); write(td / "slip2" / led, rows, cols)
                write(runs[rk] / att, [dict(event=r["trade_id"], time=f"{r['date']} 10:00:00", reasons="") for r in rows],
                      ["event", "time", "reasons"])
            doc = PC.run(runs, td / "slip2", td / "out")
            self.assertTrue((td / "out" / "phase3_compare.json").exists())
            self.assertEqual(set(doc["comparisons"]), {"P1", "P2", "P3"})
            self.assertEqual((doc["sessions_ALL"], doc["sessions_UNEXPOSED"]), (41, 38))
            self.assertEqual(doc["comparisons"]["P3"]["arm"], "R3"); self.assertEqual(doc["comparisons"]["P3"]["comparator"], "R2")
            with self.assertRaises(FileExistsError):
                PC.run(runs, td / "slip2", td / "out")


if __name__ == "__main__":
    unittest.main()
