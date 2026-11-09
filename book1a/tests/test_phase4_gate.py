"""Phase 4 Step A (Nov 9, 2026): phase4_gate on synthetic ledgers only (no Phase 4 run exists)."""
import csv
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from book1a import phase2_report as RP, phase4_gate as G, sessions as S

SESS = S.phase_sessions("phase4")
COLS = ["date", "entry_time", "trade_id", "realized_net_R", "net_usd", "planned_risk_usd", "risk_budget_usd",
        "exec_risk_breach", "entry_risk_at_fill_usd", "risk_breach_fill"]


def trade(d, r, i=0, usd=None, planned=900.0, budget=1000.0, breach=0, at_fill=None, bf=0):
    return dict(date=d.isoformat(), entry_time=f"09:{i:02d}:00.000", trade_id=f"T-{d:%Y%m%d}-{i}", realized_net_R=str(r),
                net_usd=str(usd if usd is not None else 1000.0 * r), planned_risk_usd=str(planned), risk_budget_usd=str(budget),
                exec_risk_breach=str(breach), entry_risk_at_fill_usd=str(at_fill if at_fill is not None else planned),
                risk_breach_fill=str(bf))


def good():
    """+0.5 R on every session: passes every check."""
    return [trade(d, 0.5) for d in SESS]


class TestRule(unittest.TestCase):
    def ev(self, tr, s="R4"):
        return G.evaluate(s, tr, SESS, G.PHASE3_DD_R[s])

    def test_registered_constants(self):
        self.assertEqual(G.PHASE3_DD_R, {"R3": 4.5862, "R4": 5.3103})
        self.assertEqual((G.LB_MIN, G.DD_FACTOR, G.MAX_EXEC_BREACHES, G.MAX_OVERRUN_USD), (-0.1, 1.5, 1, 500.0))
        self.assertEqual(len(SESS), 52)

    def test_pass(self):
        e = self.ev(good())
        self.assertEqual(e["result"], "PASS"); self.assertTrue(all(e["checks"].values()))
        self.assertAlmostEqual(e["net_R_per_session"], 0.5); self.assertEqual(e["trades"], 52)

    def test_net_r_zero_fails(self):
        tr = [trade(d, 1.0 if i % 2 == 0 else -1.0) for i, d in enumerate(SESS)]   # mean exactly 0
        e = self.ev(tr)
        self.assertFalse(e["checks"]["net_R_per_session_above_0"]); self.assertEqual(e["result"], "FAIL")

    def test_zero_trade_sessions_count(self):
        tr = [trade(SESS[0], 5.2)]                     # one trade; the other 51 sessions are 0
        e = self.ev(tr)
        self.assertAlmostEqual(e["net_R_per_session"], 5.2 / 52)
        self.assertEqual(e["ci90"][0], RP.bootstrap_ci([5.2] + [0.0] * 51)[0])

    def test_lower_bound(self):
        # mean > 0 but very noisy: lower bound below -0.1
        tr = [trade(d, 6.0 if i % 2 == 0 else -5.8) for i, d in enumerate(SESS)]
        e = self.ev(tr)
        self.assertTrue(e["checks"]["net_R_per_session_above_0"])
        self.assertFalse(e["checks"]["ci90_lower_above_minus_0_1"]); self.assertEqual(e["result"], "FAIL")

    def test_drawdown_limit_per_strategy(self):
        # 8 losses of -1 R at the start (dd 8.0 > 7.96545 for R4; > 6.8793 for R3), then wins
        tr = [trade(d, -1.0) for d in SESS[:8]] + [trade(d, 1.0) for d in SESS[8:]]
        for s, lim in (("R4", 7.96545), ("R3", 6.8793)):
            e = self.ev(tr, s)
            self.assertAlmostEqual(e["max_drawdown_limit_R"], lim); self.assertEqual(e["max_drawdown_R"], 8.0)
            self.assertFalse(e["checks"]["max_drawdown_within_1_5x_phase3"])
        tr = [trade(d, -1.0) for d in SESS[:6]] + [trade(d, 1.0) for d in SESS[6:]]      # dd 6.0 <= both limits
        self.assertTrue(self.ev(tr, "R3")["checks"]["max_drawdown_within_1_5x_phase3"])

    def test_drawdown_at_limit_passes(self):
        tr = [trade(SESS[0], -7.96545)] + [trade(d, 1.0) for d in SESS[1:]]
        self.assertTrue(self.ev(tr)["checks"]["max_drawdown_within_1_5x_phase3"])

    def test_planned_risk_violation(self):
        tr = good(); tr[3] = trade(SESS[3], 0.5, planned=1000.01, budget=1000.0)
        e = self.ev(tr)
        self.assertEqual(e["planned_risk_violations"], 1); self.assertEqual(e["result"], "FAIL")
        tr[3] = trade(SESS[3], 0.5, planned=600.0, budget=550.0)      # remaining daily budget below $1,000
        self.assertEqual(self.ev(tr)["planned_risk_violations"], 1)
        tr[3] = trade(SESS[3], 0.5, planned=1000.0, budget=1000.0)    # equal is allowed
        self.assertEqual(self.ev(tr)["result"], "PASS")

    def test_exec_breaches(self):
        tr = good(); tr[1] = trade(SESS[1], 0.5, breach=1, at_fill=1200.0)
        e = self.ev(tr)
        self.assertEqual((e["exec_breaches"], e["exec_largest_overrun_usd"]), (1, 200.0)); self.assertEqual(e["result"], "PASS")
        tr[2] = trade(SESS[2], 0.5, breach=1, at_fill=1100.0)
        self.assertFalse(self.ev(tr)["checks"]["exec_breaches_within_gate"])          # two breaches
        tr = good(); tr[1] = trade(SESS[1], 0.5, breach=1, at_fill=1500.01)
        self.assertFalse(self.ev(tr)["checks"]["exec_breaches_within_gate"])          # one overrun above $500
        tr = good(); tr[1] = trade(SESS[1], 0.5, breach=1, at_fill=1500.0)
        self.assertTrue(self.ev(tr)["checks"]["exec_breaches_within_gate"])           # exactly $500

    def test_realized_overrun_not_gated(self):
        tr = good(); tr[1] = trade(SESS[1], -1.3, usd=-1300.0, bf=1)
        e = self.ev(tr)
        self.assertEqual(e["risk_breach_fill"], 1); self.assertEqual(e["risk_breach_fill_largest_overrun_usd"], 400.0)
        self.assertTrue(e["checks"]["exec_breaches_within_gate"])


class TestGoNoGo(unittest.TestCase):
    def test_mapping(self):
        self.assertTrue(G.go_no_go(False, True).startswith("R4: Book 1A goes to Block 2"))
        self.assertTrue(G.go_no_go(True, False).startswith("R3 ONLY: C1 with risk controls"))
        self.assertTrue(G.go_no_go(True, True).startswith("BOTH"))
        self.assertTrue(G.go_no_go(False, False).startswith("NEITHER: no Block 2 data is bought"))


def write(p, rows):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)


class TestRun(unittest.TestCase):
    def card(self, td, r3=4.5862, r4=5.3103):
        p = Path(td) / "card.json"
        p.write_text(json.dumps({"cards": {"R3": {"ALL": {"max_drawdown_R": r3}}, "R4": {"ALL": {"max_drawdown_R": r4}}}}))
        return p

    def test_run_and_sensitivity(self):
        with tempfile.TemporaryDirectory() as td:
            exposed = RP.EXPOSED_BY_PHASE["phase4"]
            r4 = [trade(d, 0.5) for d in SESS]
            # R3: the exposed sessions carry all the gains -> ALL passes, UNEXPOSED has net R 0 -> fails
            r3 = [trade(d, 3.0 if d in exposed else 0.0) for d in SESS]
            paths = {}
            for s, rows in (("R3", r3), ("R4", r4), ("R1", r4), ("R2", r4)):
                paths[s] = Path(td) / f"{s}.csv"; write(paths[s], rows)
            res = G.run({k: str(v) for k, v in paths.items()}, str(self.card(td)), str(Path(td) / "g" / "gate.json"))
            self.assertTrue((Path(td) / "g" / "gate.json").exists())
        self.assertEqual(res["populations"]["ALL"]["sessions"], 52); self.assertEqual(res["populations"]["UNEXPOSED"]["sessions"], 43)
        self.assertEqual(res["gated"]["R4"]["decision"], "PASS"); self.assertEqual(res["gated"]["R4"]["sensitivity"], "SAME_RESULT")
        self.assertEqual(res["gated"]["R3"]["decision"], "PASS")
        self.assertEqual(res["gated"]["R3"]["sensitivity"], "SENSITIVE_TO_EXPOSED_SESSIONS")
        self.assertTrue(res["go_no_go"].startswith("BOTH"))
        self.assertEqual(set(res["reported"]), {"R1", "R2"})

    def test_card_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(RuntimeError):
                G.check_phase3_card(self.card(td, r3=4.59))

    def test_trade_outside_phase_stops(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "R.csv"; write(p, [trade(dt.date(2026, 2, 4), 0.5)])
            with self.assertRaises(RuntimeError):
                G.run({"R3": str(p), "R4": str(p)}, str(self.card(td)), str(Path(td) / "o.json"))


if __name__ == "__main__":
    unittest.main()
