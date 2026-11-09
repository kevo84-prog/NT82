"""Phase 4 Step A (Nov 9, 2026): mj_steps on synthetic rows only."""
import unittest

from book1a import mj_steps as M, sessions as S
from book1a.ledger import Trade


def led(tid, d, side, qty, entry, stop, exit_):
    t = Trade("R4_M0", "E", d, "09:00:00.000", side, qty, entry, stop, float("nan"), "09:30:00.000", exit_, "STOP_FIRST",
              "ACCEPT", None, "v3.5", 1, 250)
    return dict(trade_id=tid, date=d, entry_time="09:00:00.000", side=side, qty=str(qty), entry_price=str(entry), stop=str(stop),
                exit_price=str(exit_), realized_net_R=str(round(t.realized_net_R, 4)), net_usd=str(t.net_usd))


def diag(tid, mj1="OK", mj1x="", mj2="OK", l1=("", ""), l2=("", ""), bucket="2", strategy="R4", cue="N", cuex=""):
    return dict(strategy=strategy, trade_id=tid, mj1_status=mj1, mj1_exit_price=str(mj1x), mj2_status=mj2,
                cue_fired=cue, cue_exit_price=str(cuex),
                mj2_leg1_qty=str(l1[0]), mj2_leg1_exit_price=str(l1[1]), mj2_leg2_qty=str(l2[0]), mj2_leg2_exit_price=str(l2[1]),
                mj2_size_bucket=bucket)


class TestNetR(unittest.TestCase):
    def test_matches_ledger_formula(self):
        t = Trade("R4_M0", "E", "2026-02-05", "09:00:00.000", "LONG", 3, 100.0, 90.0, float("nan"), "", 115.0, "TARGET_FIRST",
                  "ACCEPT", None, "v3.5", 1, 250)
        self.assertAlmostEqual(M.net_r("LONG", 100.0, 90.0, [(3, 115.0)], 3), t.realized_net_R)

    def test_two_legs(self):
        # short 2 NQ, entry 100, stop 110 (40 ticks): leg1 1 @ 95 (+20 ticks), leg2 1 @ 90 (+40 ticks)
        r = M.net_r("SHORT", 100.0, 110.0, [(1, 95.0), (1, 90.0)], 2)
        self.assertAlmostEqual(r, ((20 + 40) * 5.0 - 2 * 2.87 * 2) / (40 * 5.0 * 2))

    def test_leg_qty_must_add_up(self):
        with self.assertRaises(ValueError):
            M.net_r("LONG", 100.0, 90.0, [(1, 101.0)], 2)


class TestPerTrade(unittest.TestCase):
    D = S.phase_sessions("phase4")[0].isoformat()

    def test_fallbacks(self):
        L = [led("a", self.D, "LONG", 2, 100.0, 90.0, 90.0 - 0.25), led("b", self.D, "LONG", 1, 100.0, 90.0, 105.0),
             led("c", self.D, "LONG", 2, 100.0, 90.0, 104.0)]
        Dg = [diag("a", mj1x=120.0, l1=(1, 110.0), l2=(1, 120.0)),
              diag("b", mj1x=118.0, mj2="NOT_APPLICABLE (1 NQ)", bucket="NOT_APPLICABLE"),
              diag("c", mj1="NOT_APPLICABLE (no ladder)", mj2="NOT_APPLICABLE (no ladder)")]
        pt = {p["trade_id"]: p["R"] for p in M.per_trade(L, Dg, "R4")}
        self.assertAlmostEqual(pt["a"]["M-J1"], M.net_r("LONG", 100.0, 90.0, [(2, 120.0)], 2))
        self.assertAlmostEqual(pt["a"]["M-J2"], M.net_r("LONG", 100.0, 90.0, [(1, 110.0), (1, 120.0)], 2))
        self.assertAlmostEqual(pt["b"]["M-J2"], pt["b"]["M-J1"])           # 1 NQ: M-J2 keeps M-J1
        self.assertEqual(pt["c"]["M0"], pt["c"]["M-J1"]); self.assertEqual(pt["c"]["M-J1"], pt["c"]["M-J2"])

    def test_cue_a(self):
        L = [led("a", self.D, "SHORT", 2, 100.0, 110.0, 110.25), led("b", self.D, "SHORT", 2, 100.0, 110.0, 95.0)]
        Dg = [diag("a", mj1="NOT_APPLICABLE (no ladder)", mj2="x", cue="Y", cuex=102.0),
              diag("b", mj1="NOT_APPLICABLE (no ladder)", mj2="x", cue="NOT_APPLICABLE")]
        pt = {p["trade_id"]: p["R"] for p in M.per_trade(L, Dg, "R4")}
        self.assertAlmostEqual(pt["a"]["CUE_A"], M.net_r("SHORT", 100.0, 110.0, [(2, 102.0)], 2))
        self.assertEqual(pt["b"]["CUE_A"], pt["b"]["M0"])
        s = M.summary(L, M.per_trade(L, Dg, "R4"), S.phase_sessions("phase4"))
        self.assertEqual(s["CUE_A"]["trades_changed_vs_M0"], 1)
        self.assertEqual(s["status_counts"]["CUE_A"], {"Y": 1, "NOT_APPLICABLE": 1})

    def test_missing_diag_row_and_ledger_mismatch(self):
        L = [led("a", self.D, "LONG", 1, 100.0, 90.0, 105.0)]
        with self.assertRaises(ValueError):
            M.per_trade(L, [diag("a", strategy="R3")], "R4")
        bad = dict(L[0], realized_net_R="0.1234")
        with self.assertRaises(ValueError):
            M.per_trade([bad], [diag("a", mj1="NOT_APPLICABLE (no ladder)", mj2="x")], "R4")

    def test_summary_counts_changes(self):
        sess = S.phase_sessions("phase4")
        L = [led("a", self.D, "LONG", 2, 100.0, 90.0, 90.0), led("b", self.D, "LONG", 2, 100.0, 90.0, 104.0)]
        Dg = [diag("a", mj1x=120.0, l1=(1, 110.0), l2=(1, 120.0)), diag("b", mj1="NOT_APPLICABLE (no ladder)", mj2="NOT_APPLICABLE (no ladder)")]
        s = M.summary(L, M.per_trade(L, Dg, "R4"), sess)
        self.assertEqual(s["M-J1"]["trades_changed_vs_M0"], 1); self.assertEqual(s["M-J2"]["trades_changed_vs_M-J1"], 1)
        self.assertEqual(s["M0"]["sessions"], 52)
        self.assertEqual(s["mj2_by_size_bucket"]["2"]["trades"], 1)
        self.assertGreater(s["M-J1"]["net_R_per_session"], s["M0"]["net_R_per_session"])


if __name__ == "__main__":
    unittest.main()
