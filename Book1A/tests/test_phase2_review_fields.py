"""Phase 2 review fields (registered Nov 6, 2026): synthetic ticks and bars only."""
import datetime as dt
import unittest

import numpy as np

from book1a import phase2_review_fields as F

D = dt.date(2025, 10, 22)


def T(h, m, s=0, us=0):
    return dt.datetime.combine(D, dt.time(h, m, s, us))


def arr(ticks):
    t = np.array([np.datetime64(x, "us") for x, _ in ticks]); p = np.array([float(y) for _, y in ticks])
    return t, p


class TestMfeMae(unittest.TestCase):
    TICKS = [(T(9, 0, 0, 100000), 99.0),            # before the fill: excluded
             (T(9, 0, 0, 250000), 100.0),           # at the fill time: included
             (T(9, 1), 102.0), (T(9, 2), 98.5),
             (T(9, 3), 101.0),                      # at the exit time: included
             (T(9, 4), 110.0)]                      # after the exit: excluded

    def test_long_entry_and_exit_included(self):
        t, p = arr(self.TICKS)
        x = F.mfe_mae(t, p, 1, T(9, 0, 0, 250000), 100.0, T(9, 3), 97.5)          # stop 10 ticks from the fill
        self.assertEqual((x["mfe_mae_trades"], x["mfe_ticks"], x["mae_ticks"], x["stop_ticks_fill"]), (4, 8.0, 6.0, 10))
        self.assertEqual((x["mfe_R"], x["mae_R"], x["mfe_mae_timing"]), (0.8, 0.6, "POST_ENTRY"))

    def test_short_mirror(self):
        t, p = arr(self.TICKS)
        x = F.mfe_mae(t, p, -1, T(9, 0, 0, 250000), 100.0, T(9, 3), 102.5)
        self.assertEqual((x["mfe_ticks"], x["mae_ticks"], x["mfe_R"], x["mae_R"]), (6.0, 8.0, 0.6, 0.8))

    def test_exit_tick_counts(self):
        t, p = arr([(T(9, 0, 0, 250000), 100.0), (T(9, 3), 104.0)])
        self.assertEqual(F.mfe_mae(t, p, 1, T(9, 0, 0, 250000), 100.0, T(9, 3), 97.5)["mfe_ticks"], 16.0)
        self.assertEqual(F.mfe_mae(t, p, 1, T(9, 0, 0, 250000), 100.0, T(9, 2, 59), 97.5)["mfe_ticks"], 0.0)


class TestAfterStop(unittest.TestCase):
    def test_long_window_and_target(self):
        t, p = arr([(T(10, 0), 95.0),                       # the stop fill tick itself: excluded (window is open on the left)
                    (T(10, 10), 99.0), (T(10, 30), 101.0),  # 10:30 included (window end)
                    (T(10, 30, 0, 1), 120.0)])              # after the window
        x = F.after_stop(t, p, 1, "STOP_FIRST", T(10, 0), 95.0, 101.0, 20)
        self.assertEqual((x["post_exit_status"], x["post_exit_move_ticks"], x["post_exit_move_R"], x["post_exit_target_traded"]),
                         ("OK", 24.0, 1.2, "Y"))
        self.assertEqual((x["post_exit_truncated"], x["post_exit_minutes_available"], x["post_exit_timing"]), ("N", 30.0, "POST_EXIT"))
        self.assertEqual(F.after_stop(t, p, 1, "STOP_FIRST", T(10, 0), 95.0, 101.25, 20)["post_exit_target_traded"], "N")

    def test_short_mirror(self):
        t, p = arr([(T(11, 5), 103.0), (T(11, 20), 98.0)])
        x = F.after_stop(t, p, -1, "STOP_FIRST", T(11, 0), 105.0, 98.0, 28)
        self.assertEqual((x["post_exit_move_ticks"], x["post_exit_move_R"], x["post_exit_target_traded"]), (28.0, 1.0, "Y"))

    def test_truncated_at_1500(self):
        t, p = arr([(T(14, 50), 100.0), (T(14, 59), 100.5), (T(15, 1), 130.0)])
        x = F.after_stop(t, p, 1, "STOP_FIRST", T(14, 45), 99.0, 110.0, 10)
        self.assertEqual((x["post_exit_truncated"], x["post_exit_minutes_available"], x["post_exit_window_end"]), ("TRUNCATED", 15.0, T(15, 0)))
        self.assertEqual((x["post_exit_move_ticks"], x["post_exit_target_traded"]), (6.0, "N"))     # 15:01 not used

    def test_not_a_stop_and_empty_window(self):
        t, p = arr([(T(10, 5), 100.0)])
        self.assertTrue(F.after_stop(t, p, 1, "TARGET_FIRST", T(10, 0), 99.0, 101.0, 10)["post_exit_status"].startswith("NOT_APPLICABLE"))
        self.assertTrue(F.after_stop(t, p, 1, "STOP_FIRST", T(11, 0), 99.0, 101.0, 10)["post_exit_status"].startswith("DATA_MISSING"))

    def test_negative_move_kept(self):
        t, p = arr([(T(10, 5), 98.0)])
        self.assertEqual(F.after_stop(t, p, 1, "STOP_FIRST", T(10, 0), 99.0, 101.0, 10)["post_exit_move_ticks"], -4.0)


class TestEntryContext(unittest.TestCase):
    def test_fields(self):
        ends = np.array([np.datetime64(T(9, m), "us") for m in (1, 2, 3)])
        x = F.entry_context(ends, [1, 1, 1], [10.0, 11.0, 12.0], [9.0, 10.0, 11.25], [1, 1, 1], [100, 200, 50], [20, -50, 5],
                            T(9, 1), T(9, 2), T(9, 2, 0, 250000))
        self.assertEqual((x["entry_context_timing"], x["minutes_initiation_to_entry"]), ("AT_ENTRY", 1.0042))
        self.assertEqual((x["confirm_delta"], x["confirm_delta_pct"], x["confirm_range_ticks"]), (-50.0, -25.0, 4.0))
        y = F.entry_context(ends, [1] * 3, [1] * 3, [1] * 3, [1] * 3, [1] * 3, [1] * 3, T(9, 1), T(9, 4), T(9, 4, 0, 250000))
        self.assertTrue(y["confirm_bar_status"].startswith("DATA_MISSING"))


class TestGuard(unittest.TestCase):
    def test_phase2_only(self):
        for ph in ("phase1", "phase1b", "phase3", ""):
            with self.assertRaises(RuntimeError):
                F.compute(ph)


if __name__ == "__main__":
    unittest.main()
