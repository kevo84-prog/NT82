"""P0.9 unit tests: context and side fields, most restrictive side rule wins, conflicts logged."""
import unittest

from book1a import plan_fields as pf
from book1a.plan_fields import ContextInputs, DrawState, FirstTouchTracker, ZoneForSides, resolve_side, zone_fields


def ci(**kw):
    base = dict(price=24000.0, htf_val=23900.0, htf_vah=24100.0, held_or_reclaimed_val=True, failed_or_lost_vah=False,
                wk_val_state="INSIDE", wk_vah_state="INSIDE", balance_overlapping=False)
    base.update(kw)
    return ContextInputs(**base)


class TestContext(unittest.TestCase):
    def test_bullish(self):
        self.assertEqual(pf.market_context(ci()), "BULLISH")

    def test_bullish_blocked_by_accepted_below_is_none(self):
        self.assertEqual(pf.market_context(ci(wk_val_state="ACCEPTED_BELOW")), "NONE")

    def test_bearish(self):
        self.assertEqual(pf.market_context(ci(held_or_reclaimed_val=False, failed_or_lost_vah=True)), "BEARISH")

    def test_balanced(self):
        self.assertEqual(pf.market_context(ci(held_or_reclaimed_val=False, balance_overlapping=True,
                                              balance_lo=23950.0, balance_hi=24050.0, balance_poc=24000.0)), "BALANCED")
        f = pf.balance_fields(ci(balance_overlapping=True, balance_lo=23950.0, balance_hi=24050.0, balance_poc=24000.0))
        self.assertEqual(f, {"balance": "23950-24050", "balance_poc": "24000"})

    def test_value_follows(self):
        self.assertEqual(pf.value_follows(24200, 24100, 23900, 23800, 24050, 24080, 23950, 23900, 24000, 24040), "DIVERGENT_UP")
        self.assertEqual(pf.value_follows(24100, 24200, 23700, 23800, 24050, 24000, 23950, 23900, 24000, 23950), "DIVERGENT_DOWN")
        self.assertEqual(pf.value_follows(24200, 24100, 23900, 23800, 24150, 24080, 24000, 23900, 24100, 24040), "WITH_PRICE")

    def test_edge_control_and_structure(self):
        self.assertEqual(pf.edge_control(["SELL", "SELL"]), "SELLERS")
        self.assertEqual(pf.edge_control(["BUY"]), "BUYERS")
        self.assertEqual(pf.edge_control(["BUY", "SELL"]), "MIXED")
        self.assertEqual(pf.edge_control([]), "MIXED")
        self.assertEqual(pf.htf_structure([100, 110, 120], [90, 95, 105]), "RAISING_DEMAND")
        self.assertEqual(pf.htf_structure([120, 110, 100], [105, 95, 90]), "LOWERING_SUPPLY")
        self.assertEqual(pf.htf_structure([120, 110], [90, 95]), "BALANCE")

    def test_on_inventory_needed_values_are_none(self):
        r = pf.on_inventory(24000.0, 23980.0, 24050.0)
        self.assertEqual(r["on_inventory"], "NET_LONG")
        self.assertEqual(r["on_vs_settle"], 70.0)
        self.assertIsNone(r["on_far"]); self.assertIsNone(r["on_thin"])

    def test_draw_status_separate_from_context(self):
        d = DrawState(24100.0, 24120.0)
        self.assertEqual(d.as_fields(), {"draw": "24100-24120", "draw_status": "ACTIVE", "NEW_TARGET_NEEDED": "0"})
        d.on_price(24090.0, 24080.0)
        self.assertEqual(d.status, "ACTIVE")
        d.on_price(24105.0, 24095.0)
        self.assertEqual(d.status, "REACHED")
        self.assertEqual(d.as_fields()["NEW_TARGET_NEEDED"], "1")
        d.on_invalidation()
        self.assertEqual(d.status, "INVALIDATED")

    def test_invalidation_edges(self):
        self.assertEqual(pf.invalidation("BULLISH", 23950.0, 24150.0, 23900.0, 24200.0),
                         {"invalidate_below": 23950.0, "invalidate_above": None})
        self.assertEqual(pf.invalidation("BEARISH", 23950.0, 24150.0, 23900.0, 24200.0),
                         {"invalidate_below": None, "invalidate_above": 24150.0})
        self.assertEqual(pf.invalidation("BALANCED", 1, 2, 3, 4), {"invalidate_below": None, "invalidate_above": None})

    def test_gex_regime(self):
        self.assertEqual(pf.gex_regime(1.0), "POS"); self.assertEqual(pf.gex_regime(-2.0), "NEG"); self.assertIsNone(pf.gex_regime(None))


class TestSides(unittest.TestCase):
    def test_context_sides(self):
        z = ZoneForSides("D_X", 24050.0, 24060.0, above_price=True)
        self.assertEqual(resolve_side(z, "long", "BULLISH"), ("ANY", None))
        self.assertEqual(resolve_side(z, "short", "BULLISH"), ("INITIATION", None))
        self.assertEqual(resolve_side(z, "short", "BALANCED"), ("ANY", None))

    def test_rejection_zone_both_any_on_balanced(self):
        z = ZoneForSides("D_FLIP", 24050.0, 24060.0, above_price=True, kind="FLIP", tests=6, lower_highs_into_zone=True)
        self.assertEqual(resolve_side(z, "long", "NONE"), ("ANY", None))
        self.assertEqual(resolve_side(z, "short", "NONE"), ("ANY", None))

    def test_four_tests_favour_initiation_response_open(self):
        z = ZoneForSides("D_PDVAH", 24050.0, 24060.0, above_price=True, kind="VALUE_EDGE", tests=4, lower_highs_into_zone=True)
        self.assertEqual(resolve_side(z, "long", "BALANCED"), ("INITIATION", "side_conflict=D_PDVAH|long|context=ANY,tests4=INITIATION"))
        self.assertEqual(resolve_side(z, "short", "BALANCED"), ("ANY", None))

    def test_accepted_edge(self):
        z = ZoneForSides("D_WKVAL", 25072.0, 25083.0, above_price=True, kind="VALUE_EDGE", accept_state="ACCEPTED_BELOW")
        self.assertEqual(resolve_side(z, "long", "BALANCED")[0], "INITIATION")
        self.assertEqual(resolve_side(z, "short", "BALANCED")[0], "ANY")

    def test_most_restrictive_wins_and_conflict_logged(self):
        # bearish context (long = INITIATION) at an accepted-below VAL (long = INITIATION, short = ANY);
        # add edge_control BUYERS on the short through side -> short INITIATION vs context ANY: INITIATION wins
        z = ZoneForSides("D_WKVAL", 24050.0, 24060.0, above_price=False, kind="VALUE_EDGE",
                         accept_state="ACCEPTED_BELOW", edge_control="BUYERS")
        side, conflict = resolve_side(z, "long", "BEARISH")
        self.assertEqual(side, "INITIATION")
        self.assertEqual(conflict, "side_conflict=D_WKVAL|long|context=INITIATION,accepted_edge=INITIATION,edge_control=ANY")
        side, conflict = resolve_side(z, "short", "BEARISH")
        self.assertEqual(side, "INITIATION")
        self.assertEqual(conflict, "side_conflict=D_WKVAL|short|context=ANY,accepted_edge=ANY,edge_control=INITIATION")

    def test_dd_edge(self):
        z = ZoneForSides("DD_EDGE_WK", 24090.0, 24130.0, above_price=True, kind="DD_EDGE", dd_far_side_is_long=True)
        self.assertEqual(resolve_side(z, "long", "BALANCED")[0], "INITIATION")
        self.assertEqual(resolve_side(z, "short", "BALANCED")[0], "ANY")

    def test_value_follows_divergent_up(self):
        z = ZoneForSides("D_PDH", 24200.0, 24210.0, above_price=True, kind="STRUCTURE", value_follows="DIVERGENT_UP", is_highs_edge=True)
        self.assertEqual(resolve_side(z, "long", "BULLISH"), ("INITIATION", "side_conflict=D_PDH|long|context=ANY,value_follows=INITIATION"))

    def test_zone_fields_complete(self):
        z = ZoneForSides("D_X", 1, 2, True)
        f = zone_fields(z, "BULLISH")
        for k in ("zone", "long", "short", "side_conflict", "first_touch", "tests", "gex_regime", "edge_control", "value_follows"):
            self.assertIn(k, f)
        self.assertEqual(f["first_touch"], "YES")

    def test_first_touch_tracker(self):
        t = FirstTouchTracker()
        self.assertEqual(t.touch("D_X"), {"first_touch": "YES", "test_number": 1})
        self.assertEqual(t.touch("D_X"), {"first_touch": "NO", "test_number": 2})
        self.assertEqual(t.touch("D_Y")["first_touch"], "YES")


if __name__ == "__main__":
    unittest.main()
