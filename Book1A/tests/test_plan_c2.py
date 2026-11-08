"""C2 (VWAP as a tag only) on synthetic zones and the synthetic plan of test_plan_v24 (Phase 3 Step A3)."""
import unittest

from book1a import families as F, plan_c2 as C2, plan_v24 as P
from book1a.tests.test_plan_v24 import TestPlanBuilder


def L(name, px, fam=None):
    return F.Level.point(name, px, family=fam)


class TestVwapTagOnly(unittest.TestCase):
    def test_vwap_only_second_family_loses_decision(self):
        lv = [L("VWAP", 100.0), L("VWAP_SD1_UP", 103.0)]
        base = F.count_families(98.0, 102.0, lv, own_families=["STRUCTURE"])
        self.assertEqual(base.families, ["STRUCTURE", "VWAP"]); self.assertEqual(base.zone_class, "DECISION")
        with C2.vwap_tag_only():
            r = F.count_families(98.0, 102.0, lv, own_families=["STRUCTURE"])
        self.assertEqual(r.families, ["STRUCTURE"]); self.assertEqual(r.zone_class, "TARGET")
        self.assertEqual(r.levels, ["VWAP", "VWAP_SD1_UP"])             # tags preserved in levels=
        self.assertNotIn("VWAP", r.per_family)

    def test_two_other_families_unchanged(self):
        lv = [L("PDVAH", 100.0), L("VWAP", 101.0), L("WKVWAP", 99.0)]
        base = F.count_families(98.0, 102.0, lv, own_families=["STRUCTURE"])
        with C2.vwap_tag_only():
            r = F.count_families(98.0, 102.0, lv, own_families=["STRUCTURE"])
        self.assertEqual(base.zone_class, "DECISION"); self.assertEqual(r.zone_class, "DECISION")
        self.assertEqual(r.families, ["AUCTION_VALUE", "STRUCTURE"])
        self.assertEqual(r.levels, base.levels)                         # every level (tags) kept
        self.assertEqual(r.families_field(), "families=2|AUCTION_VALUE,STRUCTURE")
        self.assertEqual(r.levels_field(), base.levels_field())

    def test_zone_without_vwap_identical(self):
        lv = [L("PDVAH", 100.0), L("CR", 108.0, "GEX")]
        base = F.count_families(98.0, 102.0, lv)
        with C2.vwap_tag_only():
            r = F.count_families(98.0, 102.0, lv)
        self.assertEqual((r.families, r.levels, r.per_family), (base.families, base.levels, base.per_family))

    def test_same_thresholds(self):
        far = [L("PDVAH", 100.0), L("VWAP", 107.5)]                     # VWAP beyond 5 points: no tag either way
        with C2.vwap_tag_only():
            r = F.count_families(98.0, 102.0, far, own_families=["STRUCTURE"])
        self.assertEqual(r.levels, ["PDVAH"])
        self.assertEqual(F.GEX_TOLERANCE_PTS, 10.0); self.assertEqual(F.DEFAULT_TOLERANCE_PTS, 5.0)
        self.assertEqual(F.MIN_FAMILIES_FOR_DECISION, 2)

    def test_vwap_cannot_be_own_family(self):
        with C2.vwap_tag_only():
            with self.assertRaises(ValueError):
                F.count_families(98.0, 102.0, [], own_families=["VWAP"])

    def test_restored_after_exit_and_error(self):
        orig = F.count_families
        with C2.vwap_tag_only():
            self.assertIsNot(F.count_families, orig)
        self.assertIs(F.count_families, orig)
        with self.assertRaises(RuntimeError):
            with C2.vwap_tag_only():
                raise RuntimeError("x")
        self.assertIs(F.count_families, orig)


class TestC2Plan(TestPlanBuilder):
    """The synthetic plan of test_plan_v24 built twice by the frozen plan_v24.build."""

    def _both(self):
        t0, s0 = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        with C2.vwap_tag_only():
            t1, s1 = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        return t0, s0, t1, s1

    def test_plan_has_no_vwap_family_and_keeps_two_others(self):
        t0, s0, t1, s1 = self._both()
        for z in s1["zones"]:
            self.assertNotIn("VWAP", z["families"])
            self.assertGreaterEqual(len(z["families"]), 2)
        for m in [l for l in t1.splitlines() if l.startswith("zone_meta=")]:
            fams = m.split("|families=")[1].split("|")[1]
            self.assertNotIn("VWAP", fams.split(","))

    def test_zones_with_two_non_vwap_families_survive(self):
        t0, s0, t1, s1 = self._both()
        keys1 = {(z["lo"], z["hi"]) for z in s1["zones"]}
        for z in s0["zones"]:
            if len([f for f in z["families"] if f != "VWAP"]) >= 2:
                self.assertIn((z["lo"], z["hi"]), keys1)

    def test_vwap_levels_kept_as_tags(self):
        t0, s0, t1, s1 = self._both()
        lv0 = {(z["lo"], z["hi"]): z["levels"] for z in s0["zones"]}
        for z in s1["zones"]:
            if (z["lo"], z["hi"]) in lv0:
                self.assertEqual(z["levels"], lv0[(z["lo"], z["hi"])])
        self.assertIn("vwap_0810=", t1)

    def test_baseline_unchanged_after_c2(self):
        t0, s0, _, _ = self._both()
        t2, s2 = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertEqual(t0, t2); self.assertEqual(s0, s2)


del TestPlanBuilder   # its own tests run in test_plan_v24

if __name__ == "__main__":
    unittest.main()
