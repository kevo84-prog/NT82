"""P0.12 unit tests: theoretical R and realized net R both written per trade; contract count recorded."""
import csv
import os
import tempfile
import unittest

from book1a.ledger import CHECKER_COLUMNS, LEDGER_COLUMNS, Trade, write_checker_ledger, write_ledger


def t(side, qty, entry, stop, target, exit_px, reason):
    return Trade("R4", "T1", "2025-10-22", "09:03:00.250", side, qty, entry, stop, target, "09:20:00", exit_px, reason)


class TestR(unittest.TestCase):
    def test_long_target_one_contract(self):
        tr = t("LONG", 1, 24000.0, 23990.0, 24030.0, 24030.25, "TARGET_FIRST")   # stop 40 ticks, +121 ticks
        self.assertEqual(tr.stop_ticks, 40)
        self.assertEqual(tr.move_ticks, 121)
        self.assertAlmostEqual(tr.theoretical_R, 121 / 40)
        self.assertAlmostEqual(tr.gross_usd, 605.0)
        self.assertAlmostEqual(tr.commission_usd, 5.74)
        self.assertAlmostEqual(tr.net_usd, 599.26)
        self.assertAlmostEqual(tr.realized_net_R, 599.26 / 200.0)        # (121 - 1.148) / 40

    def test_long_stop_with_1_tick_slip(self):
        tr = t("LONG", 1, 24000.0, 23990.0, 24030.0, 23989.75, "STOP_FIRST")     # filled 1 tick below the stop
        self.assertEqual(tr.move_ticks, -41)
        self.assertAlmostEqual(tr.theoretical_R, -41 / 40)
        self.assertAlmostEqual(tr.realized_net_R, (-41 * 5 - 5.74) / 200.0)

    def test_short_mirror_and_size(self):
        tr = t("SHORT", 3, 24000.0, 24010.0, 23970.0, 23969.75, "TARGET_FIRST")
        self.assertEqual(tr.stop_ticks, 40)
        self.assertEqual(tr.move_ticks, 121)
        self.assertAlmostEqual(tr.gross_usd, 605.0 * 3)
        self.assertAlmostEqual(tr.commission_usd, 5.74 * 3)
        # realized net R is size-independent apart from commission (paid per contract): same as 1 NQ here
        self.assertAlmostEqual(tr.realized_net_R, (121 * 5 * 3 - 5.74 * 3) / (40 * 5 * 3))
        self.assertAlmostEqual(tr.realized_net_R, t("SHORT", 1, 24000.0, 24010.0, 23970.0, 23969.75, "TARGET_FIRST").realized_net_R)

    def test_time_exit_counts(self):
        tr = t("LONG", 2, 24000.0, 23980.0, 24100.0, 24005.0, "TIME_EXIT")
        self.assertEqual(tr.move_ticks, 20)
        self.assertAlmostEqual(tr.net_usd, 200.0 - 11.48)

    def test_zero_stop_is_none(self):
        tr = t("LONG", 1, 24000.0, 24000.0, 24030.0, 24010.0, "TARGET_FIRST")
        self.assertIsNone(tr.theoretical_R)
        self.assertIsNone(tr.realized_net_R)


class TestFiles(unittest.TestCase):
    def test_checker_and_full_ledger(self):
        trades = [t("LONG", 1, 24000.0, 23990.0, 24030.0, 24030.25, "TARGET_FIRST"),
                  Trade("R4", "T0", "2025-10-21", "10:00:00.250", "SHORT", 2, 24100.0, 24110.0, 24070.0,
                        "10:30:00", 24110.25, "STOP_FIRST", "ACCEPT", 947.22)]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "R4.csv")
            self.assertEqual(write_checker_ledger(p, trades), 2)
            rows = list(csv.DictReader(open(p)))
            self.assertEqual(list(rows[0].keys()), CHECKER_COLUMNS)
            self.assertEqual(rows[0]["date"], "2025-10-21")            # sorted by date
            self.assertEqual(rows[0]["qty"], "2")
            p2 = os.path.join(d, "R4_full.csv")
            write_ledger(p2, trades)
            rows = list(csv.DictReader(open(p2)))
            self.assertEqual(list(rows[0].keys()), LEDGER_COLUMNS)
            self.assertIn("theoretical_R", rows[0]); self.assertIn("realized_net_R", rows[0])
            self.assertEqual(rows[1]["qty"], "1")


if __name__ == "__main__":
    unittest.main()
