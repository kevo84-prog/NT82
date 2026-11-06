"""Phase 1b diagnostics (book1a/specs/Phase1b_diagnostics_spec.md, section 7 D3). Synthetic tapes only."""
import datetime as dt
import gzip
import tempfile
import unittest
from pathlib import Path

import numpy as np

from book1a import diag_phase1b as D
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import exit_replay as XR

DAY = dt.date(2025, 10, 22)


def write_tape(path, ticks):
    """ticks: (datetime, price, volume, aggressor); bid = price - 0.25, ask = price."""
    with gzip.open(path, "wt") as f:
        f.write("time_local,price,bid,ask,volume,aggressor\n")
        for t, p, v, s in sorted(ticks):
            f.write(f"{t.strftime('%Y-%m-%d %H:%M:%S.%f')}0,{p:.2f},{p - 0.25:.2f},{p:.2f},{v},{s}\n")


def path_price(k):
    pts = [(0, 100.0), (40, 120.0), (60, 100.0), (80, 118.0), (100, 95.0), (149, 110.0)]
    for (k0, p0), (k1, p1) in zip(pts, pts[1:]):
        if k0 <= k <= k1:
            return round((p0 + (p1 - p0) * (k - k0) / (k1 - k0)) * 4) / 4
    raise ValueError(k)


def bar_end(k):
    return dt.datetime.combine(DAY, dt.time(8, 1)) + dt.timedelta(minutes=k)


class SwingDay(unittest.TestCase):
    """Bars 0..149 end at 08:01 + k; swing highs at 40 (120) and 80 (118), swing lows at 60 (100) and 100 (95);
    every tick is a 1-lot buy, so CVD rises every bar."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        p = Path(cls.tmp.name) / "tape.csv.gz"
        write_tape(p, [(bar_end(k) - dt.timedelta(seconds=30), path_price(k), 1, "B") for k in range(150)])
        cls.tape = D.TapeFull(p)
        cls.day = D.Day(cls.tape, DAY)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_swings_po1(self):
        sw = [(self.day.swing_dict(i, k)["t"], k) for i, k in self.day.swings]
        self.assertEqual(sw, [(bar_end(40), "HIGH"), (bar_end(60), "LOW"), (bar_end(80), "HIGH"), (bar_end(100), "LOW")])
        s = self.day.swing_dict(self.day.swings[0][0], "HIGH")
        self.assertEqual(s["confirm_t"], bar_end(55))                   # the 15th bar after closes

    def test_both_cvd_resets(self):
        s = self.day.swing_dict(self.day.swings[0][0], "HIGH")          # bar 40
        self.assertEqual(s["cvd_p"], 41.0)                               # 17:00 CT reset: 41 one-lot buys
        self.assertEqual(s["cvd_r"], 11.0)                               # 08:30 CT reset: ticks after 08:30:00 (bars 30..40)
        self.assertTrue(np.isnan(self.day.b_cvd_r[5]))                   # bar before 08:30: second series not applicable

    def test_provisional_vs_at_entry(self):
        t = bar_end(85)                                                 # swing 80 not yet confirmed (confirms at bar 95)
        a = D.at_entry(self.day, "HIGH", t, -1, 115.0, 119.0)
        self.assertEqual(a["atentry_high_case_cvd17"], "NOT_APPLICABLE")
        p = D.provisional(self.day, "HIGH", t, -1, 115.0, 119.0)
        self.assertEqual((p["prov_high_case_cvd17"], p["prov_high_s2_time"], p["prov_high_with_cvd17"]), ("HIGH_ABSORPTION", bar_end(80), "WITH"))
        self.assertLessEqual(p["_data_max"], t)
        t2 = bar_end(96)
        a2 = D.at_entry(self.day, "HIGH", t2, -1, 115.0, 119.0)
        self.assertEqual((a2["atentry_high_case_cvd17"], a2["atentry_high_location"]), ("HIGH_ABSORPTION", "ZONE"))
        self.assertEqual(a2["_data_max"], bar_end(95))

    def test_low_exhaustion_at_session_extreme(self):
        a = D.at_entry(self.day, "LOW", bar_end(120), 1, None, None)
        self.assertEqual((a["atentry_low_case_cvd17"], a["atentry_low_location"], a["atentry_low_with_cvd17"]),
                         ("LOW_EXHAUSTION", "SESSION_EXTREME", "WITH"))

    def test_60_minute_exclusion(self):
        s1 = dict(kind="HIGH", i=40, t=bar_end(40), confirm_t=bar_end(55), price=120.0, cvd_p=41.0, cvd_r=11.0)
        s2 = dict(kind="HIGH", i=80, t=bar_end(40) + dt.timedelta(minutes=61), confirm_t=None, price=118.0, cvd_p=81.0, cvd_r=51.0)
        x = D.pair_fields(self.day, s1, s2, -1, 115.0, 119.0, "p")
        self.assertEqual((x["p_case_cvd17"], x["p_raw_case_cvd17"], x["p_gap_min"]), ("EXCLUDED_60MIN", "HIGH_ABSORPTION", 61.0))
        s2["t"] = bar_end(40) + dt.timedelta(minutes=60)
        self.assertEqual(D.pair_fields(self.day, s1, s2, -1, 115.0, 119.0, "p")["p_case_cvd17"], "HIGH_ABSORPTION")

    def test_breakout_speed_strictly_before(self):
        x = D.breakout_speed(self.day, bar_end(50))
        self.assertEqual(x["bs_vol_per_sec_60s"], round(1 / 60, 4))       # one 1-lot tick in [t - 60 s, t)
        self.assertEqual(x["bs_cvd_change_3bar"], 3.0)


class TestCases(unittest.TestCase):
    def test_four_cases(self):
        self.assertEqual(D.classify("HIGH", 120, 118, 10, 20), "HIGH_ABSORPTION")    # lower high, higher CVD high
        self.assertEqual(D.classify("HIGH", 118, 125, 20, 10), "HIGH_EXHAUSTION")    # higher high, lower CVD high
        self.assertEqual(D.classify("LOW", 100, 95, 10, 20), "LOW_EXHAUSTION")       # lower low, higher CVD low
        self.assertEqual(D.classify("LOW", 95, 100, 20, 10), "LOW_ABSORPTION")       # higher low, lower CVD low
        self.assertEqual(D.classify("HIGH", 120, 118, 20, 10), "NONE")
        self.assertEqual(D.with_against("HIGH_EXHAUSTION", -1), "WITH")
        self.assertEqual(D.with_against("LOW_ABSORPTION", -1), "AGAINST")


class TestCue(unittest.TestCase):
    """Entry fill 09:00:00.250 (long). Bars ending 09:01, 09:02, 09:03, two ticks each (open, close)."""

    def make(self, bars):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "t.csv.gz"
        ticks = [(dt.datetime.combine(DAY, dt.time(8, 59, 50)), 100.0, 1, "B")]
        for k, (o, c, v, s) in enumerate(bars):
            e = dt.datetime.combine(DAY, dt.time(9, 1)) + dt.timedelta(minutes=k)
            ticks += [(e - dt.timedelta(seconds=50), o, v, s), (e - dt.timedelta(seconds=10), c, v, s)]
        write_tape(p, ticks)
        tape = D.TapeFull(p)
        return tape, D.Day(tape, DAY)

    def test_fires(self):
        tape, day = self.make([(100.0, 100.25, 1, "B"), (100.5, 100.0, 3, "B"), (100.0, 100.5, 1, "S")])
        x = D.cue_a(day, tape, 1, dt.datetime.combine(DAY, dt.time(9, 0, 0, 250000)), None)
        self.assertEqual((x["cue_fired"], x["cue_trigger_bar"]), ("Y", dt.datetime.combine(DAY, dt.time(9, 2))))
        self.assertEqual(x["cue_exit_time"], dt.datetime.combine(DAY, dt.time(9, 2, 0, 250000)))
        self.assertEqual(x["cue_exit_price"], 99.75)                       # best bid for a long exit
        self.assertEqual(x["cue_exit_time_1000ms"], dt.datetime.combine(DAY, dt.time(9, 2, 1)))

    def test_not_fired(self):
        tape, day = self.make([(100.0, 100.25, 1, "B"), (100.25, 100.5, 1, "B"), (100.5, 100.75, 1, "S")])
        self.assertEqual(D.cue_a(day, tape, 1, dt.datetime.combine(DAY, dt.time(9, 0, 0, 250000)), None)["cue_fired"], "N")

    def test_not_applicable_after_m0_exit(self):
        tape, day = self.make([(100.0, 100.25, 1, "B"), (100.5, 100.0, 3, "B"), (100.0, 100.5, 1, "S")])
        x = D.cue_a(day, tape, 1, dt.datetime.combine(DAY, dt.time(9, 0, 0, 250000)), dt.datetime.combine(DAY, dt.time(9, 1, 30)))
        self.assertEqual(x["cue_fired"], "NOT_APPLICABLE")


class TestMJ(unittest.TestCase):
    def test_mj1_target_choice(self):
        self.assertEqual(D.mj1_choice(dict(TP1="10-11", TP2="20-21", RUN="30-31")), ("RUN", "30-31"))
        self.assertEqual(D.mj1_choice(dict(TP1="10-11", TP2="20-21", RUN="")), ("TP2", "20-21"))
        self.assertEqual(D.mj1_choice(dict(TP1="10-11", TP2="", RUN="")), ("TP1", "10-11"))
        self.assertIsNone(D.mj1_choice(dict(TP1="", TP2="", RUN="")))
        self.assertEqual((D.near_edge("30-31", 1), D.near_edge("30-31", -1)), (30.0, 31.0))

    def test_mj2_sizes(self):
        self.assertEqual((D.mj2_split(1), D.size_bucket(1)), (None, "NOT_APPLICABLE"))
        self.assertEqual((D.mj2_split(2), D.size_bucket(2)), ((1, 1), "2"))
        self.assertEqual((D.mj2_split(5), D.size_bucket(5)), ((1, 4), "4+"))

    def test_mj2_two_legs_on_tape(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.csv.gz"
            t0 = dt.datetime.combine(DAY, dt.time(9, 0))
            write_tape(p, [(t0 + dt.timedelta(seconds=s), px, 1, "B") for s, px in
                           ((0.1, 100.0), (60, 105.25), (120, 110.25), (3600, 100.0))])
            tape = D.TapeFull(p)
            m = XR.replay(D.tape_xr(tape), 1, t0, 95.0, [105.0, 110.0], stop_slip=1, gap_fill=True, stop_delay_ms=250, crossed="live")
            self.assertEqual([(l["reason"], l["exit"]) for l in m["legs"]], [("TARGET", 105.0), ("TARGET2", 110.0)])


class TestSizing(unittest.TestCase):
    def test_u3_examples_and_10nq(self):
        self.assertEqual(D.nq_risk_cents(60, 3), 94_722)                   # $947.22 fits
        self.assertEqual(D.nq_risk_cents(60, 4), 126_296)                  # $1,262.96 does not
        self.assertLessEqual(D.nq_risk_cents(16, 10), 100_000)             # 10 NQ: largest stop that fits = 16 ticks
        self.assertGreater(D.nq_risk_cents(17, 10), 100_000)

    def test_mnq_formula(self):
        self.assertEqual(D.mnq_risk_cents(60, 1), 62 * 50 + 188)          # (60 + 2) x $0.50 + $1.88
        self.assertEqual(D.max_mnq(60), 100_000 // (62 * 50 + 188))
        self.assertEqual(D.max_mnq(336), 5)
        self.assertEqual(D.max_mnq(10_000), 0)


class TestGex(unittest.TestCase):
    LV = dict(CR=25400.0, PS=23750.0, HVL=25230.0, CR_0DTE=25400.0, PS_0DTE=25130.0, HVL_0DTE=25260.0)

    def test_v2_seed_same_twice(self):
        a = D.twins(self.LV, 25258.75, "2025-10-22"); b = D.twins(self.LV, 25258.75, "2025-10-22")
        self.assertEqual(a, b)
        for k, v in a["random"].items():
            self.assertAlmostEqual(abs(v - 25258.75), abs(self.LV[k] - 25258.75))
            self.assertEqual(v > 25258.75 or v == 25258.75, a["random_side"][k] == "ABOVE")
        self.assertEqual(a["round"], dict(CR=25400.0, PS=23800.0, HVL=25200.0, CR_0DTE=25400.0, PS_0DTE=25100.0, HVL_0DTE=25300.0))

    def test_gex_present_rule(self):
        self.assertTrue(D.gex_present(100.0, 110.0, {"X": 120.0}, False))      # within 10 points
        self.assertFalse(D.gex_present(100.0, 110.0, {"X": 120.25}, False))
        self.assertTrue(D.gex_present(100.0, 110.0, {}, True))                 # gamma-rank level kept

    def test_tags(self):
        g = dict(ok="True", hvl_nt="25230.0", call_resistance_nt="25400.0", put_support_nt="23750.0")
        am, pm = dt.datetime.combine(DAY, dt.time(9, 0)), dt.datetime.combine(DAY, dt.time(13, 5))
        self.assertEqual(D.gex_tags(g, 25230.25, am)["hvl_side"], "AT")
        self.assertEqual(D.gex_tags(g, 25230.50, am)["hvl_side"], "ABOVE")
        self.assertEqual(D.gex_tags(g, 25229.50, am)["hvl_side"], "BELOW")
        self.assertEqual(D.gex_tags(g, 25230.0, am)["cr_ps_width"], 1650.0)
        self.assertEqual(D.gex_tags(g, 25230.0, am)["pin_zone"], "NOT_APPLICABLE (before 13:00 CT)")
        self.assertTrue(D.gex_tags(g, 25230.0, pm)["pin_zone"].startswith("NOT_RUN (inputs"))
        self.assertTrue(D.gex_tags(g, 25230.0, am)["pc_gamma_ratio"].startswith("NOT_RUN (inputs"))
        self.assertEqual(D.gex_tags(dict(ok="False"), 25230.0, am)["hvl_side"], "NOT_APPLICABLE (gex_valid N)")
        self.assertEqual(D.tod_bucket(dt.datetime.combine(DAY, dt.time(8, 44))), "08:30-08:45")
        self.assertEqual(D.tod_bucket(dt.datetime.combine(DAY, dt.time(13, 0))), "after 13:00")


class TestL1PlanSide(unittest.TestCase):
    """Spec 5b: L1_PLAN_SIDE (logged only; arms.l1 unchanged)."""

    def test_inherited_values(self):
        self.assertEqual(D.l1_side_inherited("ANY", "RESPONSE"), "ALLOWED")
        self.assertEqual(D.l1_side_inherited("RESPONSE", "RESPONSE"), "ALLOWED")
        self.assertEqual(D.l1_side_inherited("INITIATION", "INITIATION"), "ALLOWED")
        self.assertEqual(D.l1_side_inherited("NONE", "RESPONSE"), "NONE")
        self.assertEqual(D.l1_side_inherited("INITIATION", "RESPONSE"), "MISMATCH")
        self.assertEqual(D.l1_side_inherited("RESPONSE", "INITIATION"), "MISMATCH")
        self.assertTrue(D.l1_side_inherited("", "RESPONSE").startswith("DATA_MISSING"))

    def test_admitting_zone_and_plan_sides(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "PreopenPlan_2025-10-22.txt"
            p.write_text("\n".join(["date=2025-10-22",
                                    "zone=100.00-110.00|D_A|DECISION|long=INITIATION|short=ANY|alt_long=ANY",
                                    "zone=130.00-140.00|D_B|DECISION|long=NONE|short=RESPONSE",
                                    "zone=115.00-116.00|T_C|TARGET|long=ANY|short=ANY", "end=1", ""]), encoding="utf-8")
            zs = D.plan_decision_zones(p)
            self.assertEqual([z[2:] for z in zs], [("D_A", "INITIATION", "ANY"), ("D_B", "NONE", "RESPONSE")])   # TARGET zones not used
            dist, z = D.l1_admitting_zone(zs, 112.0, 114.0)                   # 2 points above D_A
            self.assertEqual((dist, z[2]), (2.0, "D_A"))
            dist, z = D.l1_admitting_zone(zs, 125.0, 127.0)                   # 3 points below D_B, 15 above D_A
            self.assertEqual((dist, z[2]), (3.0, "D_B"))
            self.assertEqual(D.l1_admitting_zone(zs, 105.0, 106.0)[0], 0.0)   # overlap
            self.assertGreater(D.l1_admitting_zone(zs, 150.25, 151.0)[0], 10.0)   # vetoed by L1 (not admitted)
            self.assertEqual(D.l1_side_inherited(z[3], "RESPONSE"), "NONE")   # long into D_B


class TestGexV3(unittest.TestCase):
    def test_pin_zone_with_inputs(self):
        pm = dt.datetime.combine(DAY, dt.time(13, 5))
        g = dict(ok="True", hvl_nt="25230.0", call_resistance_nt="25400.0", put_support_nt="23750.0")
        x = D.gex_tags(g, 25305.0, pm, dict(pin_strike_0dte_nt=25300.0, pc_gamma_ratio=0.8))
        self.assertEqual((x["pin_zone"], x["pin_distance_pts"], x["pc_gamma_ratio"]), ("Y", 5.0, 0.8))
        self.assertEqual(D.gex_tags(g, 25310.25, pm, dict(pin_strike_0dte_nt=25300.0, pc_gamma_ratio=0.8))["pin_zone"], "N")
        self.assertEqual(D.gex_tags(g, 25310.0, pm, dict(pin_strike_0dte_nt=25300.0, pc_gamma_ratio=0.8))["pin_zone"], "Y")
        self.assertTrue(D.gex_tags(g, 25305.0, pm, dict(pin_strike_0dte_nt=float("nan"), pc_gamma_ratio=0.8))["pin_zone"].startswith("DATA_MISSING"))

    def test_flip_cross(self):
        import pandas as pd
        from book1a import gex_v3 as GV
        p = pd.Series([-5.0, -3.0, 2.0, 10.0], index=[100.0, 110.0, 120.0, 130.0])   # cumsum -5, -8, -6, 4
        x, n = GV.flip_cross(p, 125.0)
        self.assertEqual(n, 1)
        self.assertAlmostEqual(x, 120.0 + 6 * 10 / 10)                     # linear between 120 (-6) and 130 (+4)
        p2 = pd.Series([5.0, -10.0, 10.0], index=[100.0, 110.0, 120.0])    # cumsum 5, -5, 5: two crossings
        x2, n2 = GV.flip_cross(p2, 118.0)
        self.assertEqual((n2, x2), (2, 115.0))                             # nearest the settlement
        self.assertEqual(GV.flip_cross(pd.Series([1.0, 2.0], index=[1.0, 2.0]), 1.5)[1], 0)


if __name__ == "__main__":
    unittest.main()
