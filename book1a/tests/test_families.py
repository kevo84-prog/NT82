"""P0.8 unit tests: families= / levels= against a hand-built zone list."""
import unittest

from book1a.families import Level, count_families, family_of, level_counts


class TestFamilyMapping(unittest.TestCase):
    def test_prefixes(self):
        self.assertEqual(family_of("WKVAL"), "AUCTION_VALUE")
        self.assertEqual(family_of("PDVAH"), "AUCTION_VALUE")
        self.assertEqual(family_of("HTFPOC"), "VOLUME")
        self.assertEqual(family_of("HVN_WK"), "VOLUME")
        self.assertEqual(family_of("DELTA_SELL_WK"), "DELTA")
        self.assertEqual(family_of("REJ_HIGH"), "STRUCTURE")
        self.assertEqual(family_of("FLIP"), "STRUCTURE")
        self.assertEqual(family_of("DD_EDGE"), "STRUCTURE")
        self.assertEqual(family_of("CR"), "GEX")
        self.assertEqual(family_of("PS_0DTE"), "GEX")
        self.assertEqual(family_of("HVL"), "GEX")
        self.assertEqual(family_of("GAMMA1"), "GEX")
        self.assertEqual(family_of("VWAP"), "VWAP")
        self.assertEqual(family_of("WKVWAP"), "VWAP")
        self.assertEqual(family_of("VWAP_SD1_UP"), "VWAP")
        self.assertIsNone(family_of("SETTLE"))      # settlement: tag only, no family (AMT, moved to research)


class TestTolerances(unittest.TestCase):
    def test_gex_counts_inside_or_within_10_points(self):
        z = (24823.0, 24863.0)
        self.assertTrue(level_counts(*z, Level.point("CR", 24850.0)))        # inside
        self.assertTrue(level_counts(*z, Level.point("CR", 24873.0)))        # 10.0 above the edge: counts
        self.assertTrue(level_counts(*z, Level.point("PS", 24813.0)))        # 10.0 below: counts
        self.assertFalse(level_counts(*z, Level.point("CR", 24873.25)))      # 10.25 above: does not
        self.assertFalse(level_counts(*z, Level.point("PS", 24812.75)))

    def test_other_families_5_points(self):
        z = (24823.0, 24863.0)
        self.assertTrue(level_counts(*z, Level.point("WKVAL", 24868.0)))
        self.assertFalse(level_counts(*z, Level.point("WKVAL", 24868.25)))
        self.assertTrue(level_counts(*z, Level.point("VWAP", 24818.0)))
        self.assertFalse(level_counts(*z, Level.point("VWAP", 24817.75)))

    def test_band_level_any_overlap(self):
        z = (100.0, 110.0)
        self.assertTrue(level_counts(*z, Level("DELTA_SELL_WK", 112.0, 130.0)))   # within 5 of the edge
        self.assertFalse(level_counts(*z, Level("DELTA_SELL_WK", 116.0, 130.0)))


class TestCountFamilies(unittest.TestCase):
    def test_hand_built_jeron_nov18_zone(self):
        # AMT expected effect, Tue Nov 18, 2025: one zone near 24,823-24,863 with REJ + WKVAL + VWAP tags
        z = (24823.0, 24863.0)
        levels = [Level.point("WKVAL", 24840.0), Level.point("PDVAH", 24846.0),
                  Level.point("VWAP", 24855.0), Level.point("VWAP_SD1_UP", 24990.0),
                  Level.point("HTFPOC", 24827.0), Level.point("CR", 24870.0), Level.point("HVL", 24700.0)]
        r = count_families(*z, levels, own_families=("STRUCTURE",))
        self.assertEqual(r.families, ["AUCTION_VALUE", "STRUCTURE", "VOLUME", "GEX", "VWAP"])
        self.assertEqual(r.levels, ["WKVAL", "PDVAH", "VWAP", "HTFPOC", "CR"])
        self.assertEqual(r.zone_class, "DECISION")
        self.assertEqual(r.families_field(), "families=5|AUCTION_VALUE,STRUCTURE,VOLUME,GEX,VWAP")
        self.assertEqual(r.levels_field(), "levels=5|WKVAL,PDVAH,VWAP,HTFPOC,CR")
        # each family counts once however many levels: two auction-value levels, one family
        self.assertEqual(r.per_family["AUCTION_VALUE"], ["WKVAL", "PDVAH"])

    def test_single_family_is_target(self):
        r = count_families(100.0, 110.0, [Level.point("PDVAH", 105.0), Level.point("WKVAL", 108.0)])
        self.assertEqual(r.n_families, 1)
        self.assertEqual(r.zone_class, "TARGET")

    def test_vwap_family_counts_once(self):
        r = count_families(100.0, 110.0, [Level.point("VWAP", 105.0), Level.point("WKVWAP", 107.0),
                                           Level.point("VWAP_SD1_DN", 104.0)])
        self.assertEqual(r.families, ["VWAP"])
        self.assertEqual(len(r.levels), 3)
        self.assertEqual(r.zone_class, "TARGET")

    def test_vwap_plus_gex_is_decision(self):
        r = count_families(100.0, 110.0, [Level.point("VWAP", 105.0), Level.point("PS", 118.0)])
        self.assertEqual(r.zone_class, "DECISION")
        r = count_families(100.0, 110.0, [Level.point("VWAP", 105.0), Level.point("PS", 121.0)])
        self.assertEqual(r.zone_class, "TARGET")

    def test_gex_tolerance_sensitivity(self):
        lv = [Level.point("WKVAL", 105.0), Level.point("CR", 125.0)]
        self.assertEqual(count_families(100.0, 110.0, lv, gex_tolerance=10.0).n_families, 1)
        self.assertEqual(count_families(100.0, 110.0, lv, gex_tolerance=20.0).n_families, 2)

    def test_unknown_level_ignored(self):
        r = count_families(100.0, 110.0, [Level.point("SETTLE", 105.0)])
        self.assertEqual(r.n_families, 0)


if __name__ == "__main__":
    unittest.main()
