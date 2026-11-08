"""Phase 2 review fields (registered Nov 6, 2026): synthetic ticks and bars only."""
import datetime as dt
import unittest

import numpy as np

from book1a import phase2_review_fields as F
from book1a import sessions as S

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


H = dt.date(2025, 11, 28)          # half day (Book 1 calendar): close 12:15 CT


def TH(h, m, s=0, day=H):
    return dt.datetime.combine(day, dt.time(h, m, s))


class TestSessionClose(unittest.TestCase):
    def test_calendar(self):
        self.assertEqual(S.session_close(H), TH(12, 15))
        self.assertEqual(S.session_close(dt.date(2025, 11, 26)), dt.datetime(2025, 11, 26, 15, 0))
        self.assertEqual(S.session_close(dt.date(2025, 12, 24)), dt.datetime(2025, 12, 24, 12, 15))
        for d in (dt.date(2025, 11, 27), dt.date(2025, 11, 29)):
            with self.assertRaises(ValueError):
                S.session_close(d)


class TestHalfDayCut(unittest.TestCase):
    """Nov 28, 2025: the post-stop window and MFE / MAE stop at 12:15 CT; nothing after the close is used."""
    TICKS = [(TH(11, 50), 100.0), (TH(12, 5), 101.0), (TH(12, 15), 102.0),       # 12:15:00 is the close: included
             (TH(12, 15, 1), 130.0),                                              # after the close: excluded
             (dt.datetime(2025, 11, 30, 17, 0), 140.0)]                          # next session's first trade: excluded

    def test_post_stop_truncated_at_1215(self):
        t, p = arr(self.TICKS)
        x = F.after_stop(t, p, 1, "STOP_FIRST", TH(12, 0), 99.0, 110.0, 10)
        self.assertEqual((x["post_exit_window_end"], x["post_exit_truncated"], x["post_exit_minutes_available"]), (TH(12, 15), "TRUNCATED", 15.0))
        self.assertEqual((x["post_exit_move_ticks"], x["post_exit_target_traded"]), (12.0, "N"))
        y = F.after_stop(t, p, 1, "STOP_FIRST", TH(11, 30), 99.0, 110.0, 10)      # 11:30 + 30 min = 12:00 < 12:15: complete
        self.assertEqual((y["post_exit_truncated"], y["post_exit_minutes_available"], y["post_exit_move_ticks"]), ("N", 30.0, 4.0))

    def test_short_half_day(self):
        t, p = arr(self.TICKS)
        x = F.after_stop(t, p, -1, "STOP_FIRST", TH(12, 10), 103.0, 101.0, 8)      # only the 12:15:00 trade (102.0) is in the window
        self.assertEqual((x["post_exit_move_ticks"], x["post_exit_target_traded"], x["post_exit_minutes_available"]), (4.0, "N", 5.0))

    def test_full_day_unchanged(self):
        t, p = arr([(T(14, 50), 100.0), (T(15, 0), 101.0), (T(15, 0, 1), 130.0)])
        x = F.after_stop(t, p, 1, "STOP_FIRST", T(14, 45), 99.0, 110.0, 10)
        self.assertEqual((x["post_exit_window_end"], x["post_exit_minutes_available"], x["post_exit_move_ticks"]), (T(15, 0), 15.0, 8.0))

    def test_mfe_mae_cut_at_close(self):
        t, p = arr(self.TICKS)
        x = F.mfe_mae(t, p, 1, TH(11, 50), 100.0, dt.datetime(2025, 11, 30, 17, 0), 97.5)   # ledger exit after the close
        self.assertEqual((x["mfe_ticks"], x["mfe_mae_trades"], x["mfe_mae_window_end"], x["mfe_mae_exit_flag"]),
                         (8.0, 3, TH(12, 15), "EXIT_AFTER_SESSION_CLOSE"))
        y = F.mfe_mae(t, p, 1, TH(11, 50), 100.0, TH(12, 5), 97.5)
        self.assertEqual((y["mfe_ticks"], y["mfe_mae_exit_flag"]), (4.0, "N"))


def _bars(day, minutes):
    ends = np.array([np.datetime64(dt.datetime.combine(day, dt.time(h, m)), "us") for h, m in minutes])
    n = len(minutes)
    return dict(end=ends, o=[100.0] * n, h=[101.0] * n, l=[99.0] * n, c=[100.5] * n, vol=[200] * n, delta=[40] * n)


class TestComputeWiring(unittest.TestCase):
    def setUp(self):
        self.ticks = {D: arr([(T(9, 0, 0, 250000), 100.0), (T(9, 5), 103.0), (T(9, 10), 97.25), (T(9, 20), 101.0)]),
                      H: arr(TestHalfDayCut.TICKS)}
        self.bars = {D: _bars(D, [(9, 0), (9, 1)]), H: _bars(H, [(11, 49), (11, 50)])}
        self.trades = [
            dict(strategy="R4", trade_id="a", session=D, side=1, signal_time=T(8, 59), decision_time=T(9, 0), fill_time=T(9, 0, 0, 250000),
                 fill=100.0, stop=97.5, target=105.0, exit_time=T(9, 10), exit_fill=97.25, exit_reason="STOP_FIRST"),
            dict(strategy="R1", trade_id="b", session=H, side=1, signal_time=TH(11, 49), decision_time=TH(11, 50), fill_time=TH(11, 50),
                 fill=100.0, stop=97.5, target=None, exit_time=dt.datetime(2025, 11, 30, 17, 0), exit_fill=101.0, exit_reason="TIME_EXIT"),
            dict(strategy="R3", trade_id="c", session=H, side=-1, signal_time=TH(11, 49), decision_time=TH(11, 50), fill_time=TH(11, 50),
                 fill=100.0, stop=102.5, target=95.0, exit_time=None, exit_fill=None, exit_reason="DATA_END")]

    def run_(self):
        return F.compute("phase2", self.trades, self.ticks.__getitem__, self.bars.__getitem__)

    def test_rows(self):
        a, b, c = self.run_()
        self.assertEqual((a["strategy"], a["session"], a["session_close"], a["review_version"]), ("R4", "2025-10-22", T(15, 0), F.VERSION))
        self.assertEqual((a["mfe_ticks"], a["mae_ticks"], a["mfe_R"]), (12.0, 11.0, 1.2))     # 09:10 exit tick included, 09:20 not
        self.assertEqual((a["post_exit_status"], a["post_exit_move_ticks"], a["post_exit_truncated"]), ("OK", 15.0, "N"))
        self.assertEqual((a["confirm_bar_status"], a["confirm_delta_pct"], a["minutes_initiation_to_entry"]), ("OK", 20.0, 1.0042))
        self.assertEqual((b["session_close"], b["mfe_mae_exit_flag"], b["mfe_mae_window_end"]), (TH(12, 15), "EXIT_AFTER_SESSION_CLOSE", TH(12, 15)))
        self.assertTrue(b["post_exit_status"].startswith("NOT_APPLICABLE"))
        self.assertTrue(c["post_exit_status"].startswith("DATA_MISSING"))
        self.assertEqual(c["mfe_mae_exit_flag"], "EXIT_AFTER_SESSION_CLOSE")

    def test_missing_key(self):
        del self.trades[0]["decision_time"]
        with self.assertRaises(KeyError):
            self.run_()


class TestGuard(unittest.TestCase):
    def test_phase2_only(self):
        for ph in ("phase1", "phase1b", "phase4", "", "Phase2", "Phase3"):
            with self.assertRaises(RuntimeError):
                F.compute(ph, [], None, None)


if __name__ == "__main__":
    unittest.main()
