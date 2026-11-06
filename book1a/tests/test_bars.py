import unittest
from datetime import datetime, time, date

from book1a import bars as B
from book1a.bars import CT, bars_from_rows


def t(h, m, s=0, us=0):
    return datetime.combine(date(2025, 10, 22), time(h, m, s, us), tzinfo=CT)


class TestBars(unittest.TestCase):
    def test_bar_end_rule_and_volumes(self):
        rows = [(t(9, 2, 30), 100.0, 5, "B"), (t(9, 2, 59, 999_000), 100.25, 7, "S"), (t(9, 3, 0, 0), 100.5, 3, "B"),
                (t(9, 3, 0, 1), 100.0, 2, "U")]
        out = bars_from_rows(rows)
        self.assertEqual([b.close_ct for b in out], [t(9, 3), t(9, 4)])
        b = out[0]
        self.assertEqual((b.open, b.high, b.low, b.close), (100.0, 100.5, 100.0, 100.5))
        self.assertEqual((b.buy_vol, b.sell_vol, b.delta), (8, 7, 1))      # the 09:03:00.000 tick is in this bar
        self.assertEqual(out[1].volume, 0)                                  # U aggressor counts to neither side

    def test_stacked_buy_imbalance(self):
        rows = [(t(9, 0, 10), 100.00, 5, "S"), (t(9, 0, 11), 100.25, 40, "B"), (t(9, 0, 12), 100.25, 5, "S"),
                (t(9, 0, 13), 100.50, 40, "B")]
        b = bars_from_rows(rows)[0]
        self.assertTrue(b.imb_buy)          # 40 vs 5 at 100.25 and 40 vs 5 at 100.50: two adjacent rows >= 400%
        self.assertFalse(b.imb_sell)
        rows = [(t(9, 0, 10), 100.00, 5, "S"), (t(9, 0, 11), 100.25, 40, "B")]
        self.assertFalse(bars_from_rows(rows)[0].imb_buy)   # one row only: not stacked

    def test_large_trade(self):
        self.assertTrue(bars_from_rows([(t(9, 0, 10), 100.0, 60, "S")])[0].large_sell)
        self.assertFalse(bars_from_rows([(t(9, 0, 10), 100.0, 59, "S")])[0].large_sell)

    def test_string_times_and_bounds(self):
        rows = [("2025-10-22 09:00:30.1234567", 100.0, 1, "B"), ("2025-10-22 09:01:30.0000000", 101.0, 1, "B")]
        out = bars_from_rows(rows, end=t(9, 1))
        self.assertEqual(len(out), 1)


if __name__ == "__main__":
    unittest.main()
