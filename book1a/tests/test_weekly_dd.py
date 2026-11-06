"""E23: the PD double-distribution rule of JeronPreopenMap v2.3 applied unchanged to the developing weekly profile."""
import unittest
from datetime import date, datetime, time, timedelta

from book1a import families as F, weekly_dd as W
from book1a.bars import CT


def k(px):
    return int(round(px / 0.25))


class TestRule(unittest.TestCase):
    def test_settings_are_the_map_settings(self):
        self.assertEqual((W.HVN_TICKS_PER_ROW, W.TPO_TICKS_PER_ROW, W.HVN_PCT, W.LVN_PCT, W.MIN_SINGLE_PRINT_ROWS, W.TPO_MINUTES),
                         (20, 20, 70, 30, 2, 30))
        self.assertEqual(W.LABEL, "ours: PD rule applied to weekly")

    def test_two_blocks_with_lvn(self):
        # rows (5 pt): 100..104 heavy, 105..108 thin, 109..113 heavy
        vol = {}
        for r in range(100, 105): vol[k(r * 5.0)] = 1000
        for r in range(105, 109): vol[k(r * 5.0)] = 10
        for r in range(109, 114): vol[k(r * 5.0)] = 1000
        res = W.double_distribution(vol, [], "WK")
        self.assertTrue(res["double_distribution"])
        self.assertEqual(res["separator"], "LVN")
        # smoothed (3 rows): edge rows 100, 104, 109, 113 fall to 667-670 < 700 of the peak, so the HVNs are 101-103 and
        # 110-112; rows 106-107 (s = 10) are the LVN (rows 105 and 108 are 340 > 300)
        self.assertEqual(res["lower_hvn"], [101 * 5.0, 104 * 5.0 - 0.25])
        self.assertEqual(res["upper_hvn"], [110 * 5.0, 113 * 5.0 - 0.25])
        self.assertEqual((res["separator_lo"], res["separator_hi"]), (106 * 5.0, 108 * 5.0 - 0.25))

    def test_one_block_is_not_a_split(self):
        vol = {k(r * 5.0): 1000 - abs(r - 105) * 100 for r in range(100, 111)}
        res = W.double_distribution(vol, [], "WK")
        self.assertFalse(res["double_distribution"])
        self.assertTrue(res["available"])

    def test_fewer_than_five_rows(self):
        self.assertEqual(W.hvn_lvn_areas({1: 5, 2: 5, 3: 5, 4: 5}, "WK"), [])

    def test_single_print_separator(self):
        tpo = {10: 3, 11: 1, 12: 1, 13: 1, 14: 2, 15: 1, 16: 3}
        sp = W.single_prints(tpo, "TPO_WK")
        self.assertEqual(sp, [{"type": "SP", "source": "TPO_WK", "lo": 11 * 5.0, "hi": 14 * 5.0 - 0.25}])   # row 15 alone is too short

    def test_weekly_window_and_tpo_periods(self):
        d = date(2025, 10, 22)
        ws = datetime.combine(d - timedelta(days=3), time(17, 0), tzinfo=CT)      # Sunday 17:00 CT
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        rows = [(ws - timedelta(minutes=1), 900.0, 50), (ws, 500.0, 5), (ws + timedelta(minutes=29), 505.0, 5),
                (ws + timedelta(minutes=30), 505.0, 5), (as_of - timedelta(seconds=1), 510.0, 7), (as_of, 999.0, 99)]
        res, p, sps = W.weekly(rows, ws, as_of)
        self.assertEqual(p.total, 22)                         # the 17:59 Friday trade and the 08:10:00 trade are out
        self.assertEqual((p.high, p.low), (510.0, 500.0))
        self.assertEqual(p.tpo[W._floordiv(k(505.0), 20)], 2)  # two 30-minute periods touched row 101
        self.assertEqual(p.tpo[W._floordiv(k(500.0), 20)], 1)
        self.assertEqual(res["window_end"], as_of.isoformat())
        self.assertLess(datetime.fromisoformat(res["last_trade_ct"]), as_of)

    def test_plan_inputs_and_family(self):
        res = {"status": "AVAILABLE", "double_distribution": True, "lower_hvn": [100.0, 120.0], "upper_hvn": [150.0, 170.0], "separator_lo": 125.0, "separator_hi": 140.0}
        self.assertEqual(W.as_plan_inputs(res), ((100.0, 120.0), (125.0, 140.0), (150.0, 170.0), "WK"))
        self.assertIsNone(W.as_plan_inputs({"double_distribution": False}))
        # both DD edges are STRUCTURE and count once in a merged zone
        self.assertEqual(F.family_of("DD_EDGE_WK"), "STRUCTURE")
        self.assertEqual(F.family_of("DD_EDGE_PD"), "STRUCTURE")
        fr = F.count_families(100.0, 120.0, [F.Level.point("DD_EDGE_PD", 105.0), F.Level.point("DD_EDGE_WK", 110.0)],
                              own_families=sorted(set(["STRUCTURE", "STRUCTURE"])))
        self.assertEqual(fr.families, ["STRUCTURE"])


class TestUnavailable(unittest.TestCase):
    """E26 (Kyron, Nov 4): the map left the weekly profile out -> UNAVAILABLE, never a valid profile with no edge."""
    PK = {"data": {"notes": ["CALENDAR: half day today", "DATA: weekly profile left out: data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT"]}}

    def test_map_exclusion_reason(self):
        self.assertEqual(W.map_weekly_exclusion(self.PK), "data gap 2025-11-27 20:44 CT to 2025-11-28 07:30 CT")
        self.assertIsNone(W.map_weekly_exclusion({"data": {"notes": ["DATA: overnight/VWAP window left out: data gap x"]}}))
        self.assertIsNone(W.map_weekly_exclusion(None))

    def test_unavailable_is_not_a_no_edge_profile(self):
        ws = datetime.combine(date(2025, 11, 23), time(17, 0), tzinfo=CT)
        as_of = datetime.combine(date(2025, 11, 28), time(8, 10), tzinfo=CT)
        vol_rows = [(ws + timedelta(minutes=m), 500.0 + (m % 40), 10) for m in range(0, 3000)]
        res, prof, sps = W.weekly(vol_rows, ws, as_of, packet=self.PK)
        self.assertEqual(res["status"], "UNAVAILABLE")
        self.assertNotIn("double_distribution", res)
        self.assertIn("data gap", res["reason"])
        self.assertIsNone(prof); self.assertEqual(sps, [])
        self.assertIsNone(W.as_plan_inputs(res))
        ok, _, _ = W.weekly(vol_rows, ws, as_of, packet={"data": {"notes": []}})
        self.assertEqual(ok["status"], "AVAILABLE")
        self.assertIn("double_distribution", ok)

    def test_plan_inputs_need_available(self):
        res = {"status": "UNAVAILABLE", "double_distribution": True, "lower_hvn": [1, 2], "upper_hvn": [5, 6], "separator_lo": 3, "separator_hi": 4}
        self.assertIsNone(W.as_plan_inputs(res))


if __name__ == "__main__":
    unittest.main()
