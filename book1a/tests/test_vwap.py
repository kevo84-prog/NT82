"""P0.6 unit tests: hand calculation of the 08:10 CT VWAP on synthetic trades.

The real-data pass test (2 normal days and the roll days Dec 15, 2025 and Mar 16, 2026 against a
hand calculation from the MBO files) runs with book1a/hand_checks/vwap_hand_check.py on the PC.
"""
import math
import unittest
from datetime import date, datetime, time, timedelta

from book1a import vwap
from book1a.vwap import CT, ct, session_start, to_ns, vwap_0810, week_start


def trade(d, t, price, size):
    return (to_ns(ct(d, t)), price, size)


class TestWindows(unittest.TestCase):
    def test_session_start_is_prev_day_1700(self):
        self.assertEqual(session_start(date(2025, 10, 22)), ct(date(2025, 10, 21), time(17, 0)))

    def test_monday_session_starts_sunday(self):
        self.assertEqual(session_start(date(2025, 12, 15)), ct(date(2025, 12, 14), time(17, 0)))
        self.assertEqual(session_start(date(2025, 12, 15)).weekday(), 6)

    def test_week_start_is_sunday_1700(self):
        self.assertEqual(week_start(date(2025, 10, 22)), ct(date(2025, 10, 19), time(17, 0)))   # Wed -> Sun
        self.assertEqual(week_start(date(2025, 12, 15)), ct(date(2025, 12, 14), time(17, 0)))   # Mon -> same Sun
        self.assertEqual(week_start(date(2026, 3, 20)), ct(date(2026, 3, 15), time(17, 0)))     # Fri -> Sun

    def test_dst_change_nov_2_2025(self):
        # Nov 2, 2025 01:00 CDT -> CST. The Monday Nov 3 session still opens 17:00 CT Sunday,
        # which is 23:00 UTC (CST), while the Friday Oct 31 open was 22:00 UTC (CDT).
        s = session_start(date(2025, 11, 3))
        self.assertEqual(s.utcoffset(), timedelta(hours=-6))
        self.assertEqual(to_ns(s) // 10**9 % 86400, 23 * 3600)
        f = session_start(date(2025, 10, 31))
        self.assertEqual(f.utcoffset(), timedelta(hours=-5))


class TestHandCalc(unittest.TestCase):
    def setUp(self):
        d = date(2025, 10, 22)          # Wednesday
        p = date(2025, 10, 21)          # Tuesday (overnight starts 17:00 CT)
        self.d = d
        self.trades = [
            trade(date(2025, 10, 20), time(3, 0), 24000.00, 7),   # Monday 03:00 CT: weekly only
            trade(p, time(10, 0), 24100.00, 5),                   # Tue RTH: weekly only
            trade(p, time(16, 59, 59), 24150.00, 9),              # before the 17:00 reset: weekly only
            trade(p, time(17, 0, 0), 24200.00, 2),                # exactly 17:00:00 -> session
            trade(p, time(20, 30), 24210.25, 3),
            trade(d, time(2, 15), 24190.50, 4),
            trade(d, time(8, 9, 59, 999_000), 24205.00, 1),       # last ms before 08:10
            trade(d, time(8, 10, 0), 24300.00, 100),              # exactly 08:10:00 -> excluded
            trade(d, time(9, 0), 24400.00, 50),                   # after -> excluded
        ]

    def hand(self, rows):
        vol = sum(s for _, _, s in rows)
        v = sum(p * s for _, p, s in rows) / vol
        sd = math.sqrt(sum(s * (p - v) ** 2 for _, p, s in rows) / vol)
        return v, sd, vol

    def test_session_and_weekly_match_hand_calc(self):
        ts, pr, sz = zip(*self.trades)
        r = vwap_0810(ts, pr, sz, self.d)
        sess_rows = self.trades[3:7]
        v, sd, vol = self.hand(sess_rows)
        self.assertEqual(r["SESSION"].n_trades, 4)
        self.assertEqual(r["SESSION"].volume, vol)
        self.assertAlmostEqual(r["SESSION"].vwap, v, places=9)
        self.assertAlmostEqual(r["SESSION"].sd, sd, places=9)
        wk_rows = self.trades[0:7]
        v, sd, vol = self.hand(wk_rows)
        self.assertEqual(r["WEEKLY"].n_trades, 7)
        self.assertAlmostEqual(r["WEEKLY"].vwap, v, places=9)
        self.assertAlmostEqual(r["WEEKLY"].sd, sd, places=9)
        # explicit hand numbers for the session window
        # (24200*2 + 24210.25*3 + 24190.5*4 + 24205*1) / 10 = 241997.75 / 10
        self.assertAlmostEqual(r["SESSION"].vwap, 24199.775, places=9)
        self.assertEqual(r["SESSION"].available_at_ct, ct(self.d, time(8, 10)))
        self.assertEqual(r["SESSION"].window_end_ct, ct(self.d, time(8, 10)))

    def test_order_independent(self):
        ts, pr, sz = zip(*reversed(self.trades))
        r1 = vwap_0810(ts, pr, sz, self.d)
        ts, pr, sz = zip(*self.trades)
        r2 = vwap_0810(ts, pr, sz, self.d)
        self.assertEqual(r1["SESSION"].vwap, r2["SESSION"].vwap)
        self.assertEqual(r1["WEEKLY"].sd, r2["WEEKLY"].sd)

    def test_empty_window(self):
        r = vwap_0810([], [], [], self.d)
        self.assertIsNone(r["SESSION"].vwap)
        self.assertEqual(r["SESSION"].n_trades, 0)

    def test_roll_day_restart(self):
        # Mon Dec 15, 2025 (NinjaTrader rolls to NQH6). Weekly = session on a Monday anyway;
        # with an explicit contract start later than Sunday 17:00, both windows start there.
        d = date(2025, 12, 15)
        rows = [trade(date(2025, 12, 14), time(17, 0), 25000.0, 1),
                trade(date(2025, 12, 14), time(19, 0), 25010.0, 1),
                trade(d, time(3, 0), 25020.0, 2)]
        ts, pr, sz = zip(*rows)
        r = vwap_0810(ts, pr, sz, d)
        self.assertEqual(r["SESSION"].window_start_ct, r["WEEKLY"].window_start_ct)
        self.assertEqual(r["SESSION"].vwap, r["WEEKLY"].vwap)
        r2 = vwap_0810(ts, pr, sz, d, contract_first_session_start=ct(date(2025, 12, 14), time(18, 0)))
        self.assertEqual(r2["SESSION"].n_trades, 2)
        self.assertAlmostEqual(r2["SESSION"].vwap, (25010.0 + 25020.0 * 2) / 3, places=9)


class TestTag(unittest.TestCase):
    def test_tag_within_5_points(self):
        self.assertTrue(vwap.tag_zone(100.0, 110.0, 105.0))
        self.assertTrue(vwap.tag_zone(100.0, 110.0, 114.99))
        self.assertTrue(vwap.tag_zone(100.0, 110.0, 95.0))
        self.assertFalse(vwap.tag_zone(100.0, 110.0, 115.25))
        self.assertFalse(vwap.tag_zone(100.0, 110.0, None))


if __name__ == "__main__":
    unittest.main()
