"""P0.13 unit tests: the audit flags any input not strictly available before the decision."""
import os
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from book1a.lookahead import (CT, LookaheadAudit, gex_available_at, l2_second_available_at, map_available_at,
                              swing_available_at)


def c(d, h, m, s=0):
    return datetime.combine(d, time(h, m, s), tzinfo=CT)


class TestRules(unittest.TestCase):
    def test_swing_known_15_bars_later(self):
        d = date(2025, 10, 22)
        self.assertEqual(swing_available_at(c(d, 7, 30)), c(d, 7, 45))

    def test_gex_d_minus_1_11pm_et(self):
        a = gex_available_at(date(2025, 10, 22))
        self.assertEqual(a, datetime(2025, 10, 21, 23, 0, tzinfo=ZoneInfo("America/New_York")))
        self.assertLess(a, map_available_at(date(2025, 10, 22)))

    def test_l2_second(self):
        d = date(2025, 10, 22)
        self.assertEqual(l2_second_available_at(c(d, 9, 0, 5)), c(d, 9, 0, 6))


class TestAudit(unittest.TestCase):
    def test_clean_entry_passes(self):
        d = date(2025, 10, 22)
        a = LookaheadAudit()
        dec = c(d, 9, 3)                                            # entry decision at the 09:03 bar close
        a.register("E1", dec, "D_WKVAL", "ZONE", map_available_at(d))
        a.register("E1", dec, "VWAP_0810", "INDICATOR", map_available_at(d))
        a.register("E1", dec, "mq_call_resistance", "GEX", gex_available_at(d))
        a.register("E1", dec, "swing_high_0745", "SWING", swing_available_at(c(d, 7, 45)))
        a.register("E1", dec, "l2_bid_refill", "L2", l2_second_available_at(c(d, 9, 2, 58)))
        self.assertTrue(a.passed())
        self.assertEqual(a.violations(), [])

    def test_equal_timestamp_is_violation(self):
        d = date(2025, 10, 22)
        a = LookaheadAudit()
        a.register("E1", c(d, 8, 10), "VWAP_0810", "INDICATOR", map_available_at(d))
        v = a.violations()
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].lead_seconds, 0.0)

    def test_future_swing_flagged(self):
        d = date(2025, 10, 22)
        a = LookaheadAudit()
        a.register("E1", c(d, 9, 3), "swing_high_0855", "SWING", swing_available_at(c(d, 8, 55)))  # known 09:10
        self.assertFalse(a.passed())
        self.assertEqual(a.violations()[0].input_name, "swing_high_0855")
        self.assertEqual(a.violations()[0].lead_seconds, 7 * 60)

    def test_missing_available_at_fails(self):
        a = LookaheadAudit()
        a.register("E1", c(date(2025, 10, 22), 9, 3), "untagged_level", "LEVEL", None)
        self.assertFalse(a.passed())
        self.assertEqual(a.missing, [("E1", "untagged_level")])

    def test_naive_timestamp_rejected(self):
        a = LookaheadAudit()
        with self.assertRaises(ValueError):
            a.register("E1", datetime(2025, 10, 22, 9, 3), "x", "LEVEL", "2025-10-22T08:10:00")

    def test_log_written(self):
        d = date(2025, 10, 22)
        a = LookaheadAudit()
        a.register("E1", c(d, 9, 3), "D_WKVAL", "ZONE", map_available_at(d))
        a.register("E2", c(d, 9, 3), "gex", "GEX", c(d, 9, 30))
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "audit.csv")
            s = a.write_log(p)
            self.assertEqual(s, {"decisions": 2, "inputs": 2, "violations": 1, "missing": 0})
            txt = open(p).read()
            self.assertIn("VIOLATION", txt)
            self.assertIn("OK", txt)


if __name__ == "__main__":
    unittest.main()
