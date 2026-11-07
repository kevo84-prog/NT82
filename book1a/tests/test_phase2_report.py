"""book1a.phase2_report: report card and stopped-trade classes on synthetic ledgers only (hand-computed values)."""
import datetime as dt
import unittest

import numpy as np

from book1a import phase2_report as RP
from book1a import phase2_review_fields as F
from book1a import sessions as S

D1, D2, D3 = dt.date(2025, 11, 5), dt.date(2025, 11, 6), dt.date(2025, 11, 7)


def tr(tid, d, r, usd=None, entry="09:30:00.250", exit_reason="STOP_FIRST", theo=None, **kw):
    x = dict(strategy="R4", trade_id=tid, date=d.isoformat(), entry_time=entry, exit_time="10:00:00.000",
             exit_reason=exit_reason, realized_net_R=str(r), theoretical_R=str(r if theo is None else theo),
             net_usd=str(r * 100 if usd is None else usd), risk_breach_fill="0", exec_risk_breach="0")
    x.update(kw)
    return x


class TestSessions(unittest.TestCase):
    def test_zero_trade_sessions_in_denominator(self):
        t = [tr("a", D1, 2.0, 200.0), tr("b", D1, -0.5, -50.0)]
        day = RP.daily_table(t, [D1, D2, D3])
        self.assertEqual([(x["session"], x["trades"], x["net_R"], x["net_usd"]) for x in day],
                         [("2025-11-05", 2, 1.5, 150.0), ("2025-11-06", 0, 0.0, 0.0), ("2025-11-07", 0, 0.0, 0.0)])
        c = RP.report_card("R4", t, [D1, D2, D3])
        self.assertEqual((c["sessions"], c["trades"], c["net_R_per_session"], c["trades_per_session"]), (3, 2, 0.5, round(2 / 3, 6)))
        self.assertEqual((c["net_usd"], c["net_usd_per_session"]), (150.0, 50.0))

    def test_unexposed_population(self):
        pops = RP.populations(S.phase_sessions("phase2"))
        self.assertEqual((len(pops["ALL"]), len(pops["UNEXPOSED"])), (21, 13))
        self.assertTrue(RP.EXPOSED.isdisjoint(pops["UNEXPOSED"]))
        ex, un = dt.date(2025, 11, 17), dt.date(2025, 11, 28)
        t = [tr("e", ex, 3.0), tr("u", un, -1.3)]
        c = RP.report_card("R4", t, pops["UNEXPOSED"])
        self.assertEqual((c["sessions"], c["trades"], c["net_R_per_session"], c["max_drawdown_R"]), (13, 1, -0.1, 1.3))
        self.assertEqual(len(c["daily_table"]), 13)
        # the CI resamples only the 13 sessions
        sv = [x["net_R"] for x in c["daily_table"]]
        rng = np.random.default_rng(20251205)
        m = np.asarray(sv)[rng.integers(0, 13, size=(10000, 13))].mean(axis=1)
        self.assertEqual(c["net_R_per_session_ci90"], [round(float(np.percentile(m, 5)), 6), round(float(np.percentile(m, 95)), 6)])


class TestBootstrap(unittest.TestCase):
    def test_reproduces_with_seed(self):
        v = [1.07, -0.53, 0.0, 2.31, -1.0, 0.19, -0.77]
        self.assertEqual(RP.bootstrap_ci(v), RP.bootstrap_ci(v))
        rng = np.random.default_rng(20251205)
        m = np.asarray(v)[rng.integers(0, 7, size=(10000, 7))].mean(axis=1)
        self.assertEqual(RP.bootstrap_ci(v), (float(np.percentile(m, 5)), float(np.percentile(m, 95))))
        self.assertNotEqual(RP.bootstrap_ci(v), RP.bootstrap_ci(v, seed=1))

    def test_hand_values(self):
        lo, hi = RP.bootstrap_ci([0.7, 0.7, 0.7])                               # constant: every resample mean 0.7
        self.assertAlmostEqual(lo, 0.7, places=12); self.assertAlmostEqual(hi, 0.7, places=12)
        # n = 2, values 0 and 1: resample means 0 (p 1/4), 0.5 (1/2), 1 (1/4): 5th pct = 0, 95th = 1
        self.assertEqual(RP.bootstrap_ci([0.0, 1.0]), (0.0, 1.0))


class TestDrawdown(unittest.TestCase):
    def test_from_zero_peak(self):
        self.assertEqual(RP.max_drawdown([-2.0]), 2.0)                     # first trade a loss: peak 0
        self.assertEqual(RP.max_drawdown([-1.0, 2.0, -3.0, 1.0]), 3.0)     # cum -1, 1, -2, -1: peak 1 -> -2
        self.assertEqual(RP.max_drawdown([1.0, 1.0]), 0.0)

    def test_order_and_supplemental(self):
        # entry order (session, entry time) whatever the input order; session order supplemental beside it
        t = [tr("b", D1, -2.0, entry="11:00:00.250"), tr("a", D1, 1.0, entry="09:00:00.250"), tr("c", D2, 1.5)]
        c = RP.report_card("R3", t, [D1, D2])
        self.assertEqual(c["max_drawdown_R"], 2.0)                          # 1, -1, 0.5: peak 1 -> -1
        self.assertEqual(c["max_drawdown_R_session_order_SUPPLEMENTAL"], 1.0)   # sessions -1, 1.5: peak 0 -> -1
        self.assertEqual(c["max_drawdown_usd"], 200.0)
        self.assertNotIn("max_drawdown_usd", RP.report_card("R1", t, [D1, D2]))


class TestWinRate(unittest.TestCase):
    def test_zero_R_trade(self):
        w = RP.win_stats([1.0, 0.0, -0.5, 2.0])
        self.assertEqual((w["win_rate"], w["wins"], w["losses"], w["zero"]), (0.5, 2, 1, 1))
        self.assertEqual((w["avg_win_R"], w["avg_loss_R"]), (1.5, -0.5))
        self.assertEqual(RP.win_stats([0.0])["win_rate"], 0.0)


class TestSplits(unittest.TestCase):
    def test_tod_edges(self):
        cases = {"08:29:59.999": "before 08:30", "08:30:00.250": "08:30-08:45", "08:44:59.999": "08:30-08:45",
                 "08:45:00.000": "08:45-10:00", "09:59:59.999": "08:45-10:00", "10:00:00.000": "10:00-13:00",
                 "12:59:59.999": "10:00-13:00", "13:00:00.000": "13:00+", "14:30:00.250": "13:00+"}
        for t, b in cases.items():
            self.assertEqual(RP.tod_bucket(t), b, t)

    def test_tod_card(self):
        t = [tr("a", D1, 1.0, entry="08:44:59.999"), tr("b", D2, -1.0, entry="08:45:00.000")]
        tod = RP.report_card("R1", t, [D1, D2, D3])["time_of_day"]
        self.assertEqual((tod["08:30-08:45"]["trades"], tod["08:30-08:45"]["net_R_per_session"]), (1, round(1 / 3, 6)))
        self.assertEqual(tod["08:45-10:00"]["net_R"], -1.0)
        self.assertNotIn("before 08:30", tod)

    def test_regime_without_valid_gex(self):
        reg = {D1: "positive", D2: "negative", D3: None}                   # D3: V5, no valid levels
        t = [tr("a", D1, 1.0), tr("b", D3, -2.0)]
        g = RP.report_card("R4", t, [D1, D2, D3], regime_of=reg)["gamma_regime"]
        self.assertEqual((g["all"]["sessions"], g["all"]["trades"], g["all"]["net_R_per_session"]), (3, 2, round(-1 / 3, 6)))
        self.assertEqual((g["positive"]["sessions"], g["positive"]["net_R_per_session"]), (1, 1.0))
        self.assertEqual((g["negative"]["sessions"], g["negative"]["trades"], g["negative"]["net_R_per_session"]), (1, 0, 0.0))
        self.assertEqual(g["no_valid_gex_V5"]["list"], ["2025-11-07"])


class TestRiskAndExits(unittest.TestCase):
    def test_counts(self):
        t = [tr("a", D1, -1.2, -1100.0, planned_risk_usd="1000.0", risk_breach_fill="1",
                exec_risk_breach="1", entry_risk_at_fill_usd="1030.5", risk_budget_usd="1000.0"),
             tr("b", D1, 2.0, exit_reason="TARGET_FIRST"), tr("c", D2, 0.1, exit_reason="TIME_EXIT")]
        att = [dict(time="2025-11-05 09:30:00", reasons="RISK_REJECT:PER_TRADE_BUDGET"),
               dict(time="2025-11-06 10:00:00", reasons="RISK_REJECT:NO_QUOTE"),
               dict(time="2025-11-06 11:00:00", reasons="HALT:LOSS_HALT"), dict(time="2025-11-06 12:00:00", reasons="")]
        c = RP.report_card("R3", t, [D1, D2], attempts=att)
        self.assertEqual(c["exit_reasons"], {"STOP_FIRST": 1, "TARGET_FIRST": 1, "TIME_EXIT": 1})
        r = c["risk"]
        self.assertEqual((r["risk_reject"], r["risk_reject_by_reason"]), (2, {"RISK_REJECT:NO_QUOTE": 1, "RISK_REJECT:PER_TRADE_BUDGET": 1}))
        self.assertEqual((r["exec_breach"], r["exec_breach_largest_usd"]), (1, 30.5))
        self.assertEqual((r["risk_breach_fill"], r["risk_breach_fill_largest_overrun_usd"]), (1, 100.0))
        u = RP.report_card("R3", t, [D2], attempts=att)["risk"]           # population filter on attempts
        self.assertEqual(u["risk_reject"], 1)

    def test_stress_core(self):
        st = {"lat1000": [tr("a", D1, -1.0), tr("b", D2, 0.5)]}
        s = RP.report_card("R4", [tr("a", D1, 1.0)], [D1, D2], stress=st)["stress"]["lat1000"]
        self.assertEqual((s["trades"], s["net_R_per_session"], s["max_drawdown_R"]), (2, -0.25, 1.0))
        self.assertIn("max_drawdown_usd", s)


class TestClasses(unittest.TestCase):
    STOP = dict(exit_reason="STOP_FIRST")

    def rv(self, **kw):
        x = dict(mfe_R=0.4, post_exit_status="OK", post_exit_truncated="N", post_exit_move_R=0.5, post_exit_target_traded="N")
        x.update(kw); return x

    def test_each_class(self):
        C = RP.classify
        self.assertEqual(C(dict(exit_reason="TARGET_FIRST"), self.rv(mfe_R=3.0)), "NOT_STOPPED")
        self.assertEqual(C(dict(exit_reason="TIME_EXIT"), {}), "NOT_STOPPED")
        self.assertEqual(C(self.STOP, self.rv(mfe_R=1.0)), "GAVE_BACK")                              # exactly 1.0 R
        self.assertEqual(C(self.STOP, self.rv(mfe_R=1.2, post_exit_target_traded="Y")), "GAVE_BACK")  # priority over b
        self.assertEqual(C(self.STOP, self.rv(post_exit_target_traded="Y")), "STOP_THEN_TARGET")
        self.assertEqual(C(self.STOP, self.rv(post_exit_target_traded="Y", post_exit_truncated="TRUNCATED")), "STOP_THEN_TARGET")
        self.assertEqual(C(self.STOP, self.rv(post_exit_move_R=0.9999)), "NO_POST_STOP_FOLLOW_THROUGH")
        self.assertEqual(C(self.STOP, self.rv(post_exit_move_R=-0.5)), "NO_POST_STOP_FOLLOW_THROUGH")
        self.assertEqual(C(self.STOP, self.rv(post_exit_move_R=1.0)), "UNCLASSIFIED")                 # move >= 1 R, no target
        self.assertEqual(C(self.STOP, self.rv(post_exit_truncated="TRUNCATED")), "UNCLASSIFIED")
        self.assertEqual(C(self.STOP, dict(mfe_R=0.2, post_exit_status="DATA_MISSING (no trade in the window)")), "UNCLASSIFIED")

    def test_truncated_window_from_review_fields(self):
        # stop at 14:50 on a full day: window cut at 15:00 (10 of 30 min), target not traded -> UNCLASSIFIED;
        # the same with the target trading at 14:58 -> STOP_THEN_TARGET
        T = lambda h, m: dt.datetime.combine(D1, dt.time(h, m))
        t = np.array([np.datetime64(T(14, 52), "us"), np.datetime64(T(14, 58), "us"), np.datetime64(T(15, 10), "us")])
        for prices, want in (([99.0, 99.5, 120.0], "UNCLASSIFIED"), ([99.0, 104.0, 99.0], "STOP_THEN_TARGET")):
            a = F.after_stop(t, np.array(prices), 1, "STOP_FIRST", T(14, 50), 98.0, 104.0, 8)
            self.assertEqual((a["post_exit_truncated"], a["post_exit_minutes_available"]), ("TRUNCATED", 10.0))
            self.assertEqual(RP.classify(self.STOP, dict(mfe_R=0.5, **a)), want)

    def test_class_table_and_terciles(self):
        sess = S.phase_sessions("phase2")
        width = {d: float(k) for k, d in enumerate(sess)}                  # 0..20: cut-offs 6.6667, 13.3333
        cuts = RP.terciles(width.values())
        self.assertAlmostEqual(cuts[0], 20 / 3); self.assertAlmostEqual(cuts[1], 40 / 3)
        self.assertEqual([RP.tercile_label(x, cuts) for x in (0.0, 6.0, 7.0, 13.0, 14.0, None)], ["T1", "T1", "T2", "T2", "T3", "NA"])
        t = [tr("a", sess[0], -1.0), tr("b", sess[20], 2.0, exit_reason="TARGET_FIRST")]
        rv = {"a": dict(mfe_R=1.5)}
        tags = {"a": dict(gamma_regime="positive"), "b": dict(gamma_regime="negative")}
        ct = RP.class_table("R4", t, rv, tags, {"cr_ps_width": width}, ["gamma_regime"])
        self.assertEqual(ct["counts"], dict(GAVE_BACK=1, STOP_THEN_TARGET=0, NO_POST_STOP_FOLLOW_THROUGH=0, UNCLASSIFIED=0, NOT_STOPPED=1))
        self.assertEqual(ct["tags"]["GAVE_BACK"], {"gamma_regime": {"positive": 1}, "cr_ps_width_tercile": {"T1": 1}})
        self.assertEqual(ct["tags"]["NOT_STOPPED"]["cr_ps_width_tercile"], {"T3": 1})
        # one set of cut-offs from the 21 sessions, used for the UNEXPOSED population too
        un = [x for x in t if dt.date.fromisoformat(x["date"]) not in RP.EXPOSED]
        self.assertEqual(RP.class_table("R4", un, rv, tags, {"cr_ps_width": width}, [])["tercile_cutoffs"], ct["tercile_cutoffs"])


class TestOverlapAndGuard(unittest.TestCase):
    def test_overlap(self):
        a, b = tr("a", D1, 1.0, entry="09:00:00.250"), tr("b", D1, 1.0, entry="09:30:00.250")
        ex = {"a": dt.datetime(2025, 11, 5, 9, 20), "b": dt.datetime(2025, 11, 5, 10)}
        self.assertEqual(RP.check_no_overlap([b, a], lambda t: ex[t["trade_id"]]), [])
        ex["a"] = dt.datetime(2025, 11, 5, 9, 45)
        self.assertEqual(RP.check_no_overlap([a, b], lambda t: ex[t["trade_id"]]), ["b"])

    def test_phase_guard(self):
        with self.assertRaises(RuntimeError):
            RP.run("phase1", {}, {}, {}, "x", "y")


if __name__ == "__main__":
    unittest.main()
