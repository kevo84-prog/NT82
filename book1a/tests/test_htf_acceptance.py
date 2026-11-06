"""Nov 5, 2026 pre-freeze specification change (Kyron, Context doc "Acceptance outside composite value" and
"Precedence"): htf_acceptance = PO-9 acceptance, unchanged, at the HTF composite VAH / VAL, data before 08:10 CT only;
None split into NONE_NO_EVIDENCE / NONE_CONFLICT; deterministic precedence. Every precedence row and the 08:10 cutoff.
Nov 5 clarification: the weekly guard on every Bullish / Bearish (both conflict cases), and the acceptance-based
invalidation at the composite edge (Bullish below the composite VAH, Bearish above the composite VAL)."""
import itertools
import unittest
from datetime import datetime, time, timedelta

from book1a import map_v24 as M, plan_fields as PF
from book1a import plan_v24 as P
from book1a.bars import CT
from book1a.tests.test_plan_v24 import TestPlanBuilder

# (context_base, htf_acceptance) -> market_context, exactly as the Context doc writes it
PRECEDENCE = {
    ("BULLISH", "ABOVE"): "BULLISH", ("BULLISH", "BELOW"): "NONE", ("BULLISH", "NONE"): "BULLISH",
    ("BEARISH", "BELOW"): "BEARISH", ("BEARISH", "ABOVE"): "NONE", ("BEARISH", "NONE"): "BEARISH",
    ("BALANCED", "ABOVE"): "BALANCED", ("BALANCED", "BELOW"): "BALANCED", ("BALANCED", "NONE"): "BALANCED",
    ("NONE_NO_EVIDENCE", "ABOVE"): "BULLISH", ("NONE_NO_EVIDENCE", "BELOW"): "BEARISH", ("NONE_NO_EVIDENCE", "NONE"): "NONE",
    ("NONE_CONFLICT", "ABOVE"): "NONE", ("NONE_CONFLICT", "BELOW"): "NONE", ("NONE_CONFLICT", "NONE"): "NONE",
}


class TestPrecedence(unittest.TestCase):
    def test_table_covers_every_pair(self):
        self.assertEqual(set(PRECEDENCE), set(itertools.product(PF.CONTEXT_BASE_VALUES, PF.HTF_ACCEPTANCE_VALUES)))

    def _row(self, base, acc):
        self.assertEqual(PF.apply_htf_acceptance(base, acc), PRECEDENCE[(base, acc)], (base, acc))

    def test_bullish_above_is_bullish(self): self._row("BULLISH", "ABOVE")
    def test_bearish_below_is_bearish(self): self._row("BEARISH", "BELOW")
    def test_bullish_below_is_none_conflict(self): self._row("BULLISH", "BELOW")
    def test_bearish_above_is_none_conflict(self): self._row("BEARISH", "ABOVE")

    def test_balanced_stays_balanced(self):
        for acc in PF.HTF_ACCEPTANCE_VALUES: self._row("BALANCED", acc)

    def test_no_evidence_above_is_bullish(self): self._row("NONE_NO_EVIDENCE", "ABOVE")
    def test_no_evidence_below_is_bearish(self): self._row("NONE_NO_EVIDENCE", "BELOW")

    def test_conflict_stays_none(self):
        for acc in PF.HTF_ACCEPTANCE_VALUES: self._row("NONE_CONFLICT", acc)

    def test_no_acceptance_keeps_label(self):
        for base in PF.CONTEXT_BASE_VALUES: self._row(base, "NONE")

    def test_output_is_one_of_four_s14_values(self):
        for (b, a) in PRECEDENCE:
            self.assertIn(PF.apply_htf_acceptance(b, a), ("BULLISH", "BEARISH", "BALANCED", "NONE"))

    def test_unknown_values_raise(self):
        with self.assertRaises(ValueError): PF.apply_htf_acceptance("NONE", "ABOVE")
        with self.assertRaises(ValueError): PF.apply_htf_acceptance("BULLISH", "ACCEPTED_ABOVE")

    def test_states_to_acceptance(self):
        self.assertEqual(PF.htf_acceptance_from_states("ACCEPTED_BELOW", "INSIDE"), "BELOW")
        self.assertEqual(PF.htf_acceptance_from_states("INSIDE", "ACCEPTED_ABOVE"), "ABOVE")
        for s in ("INSIDE", "TESTING", None):
            self.assertEqual(PF.htf_acceptance_from_states(s, s), "NONE")


def ci(price=100.0, held=False, failed=False, wk_val="INSIDE", wk_vah="INSIDE", bal=False):
    return PF.ContextInputs(price=price, htf_val=90.0, htf_vah=110.0, held_or_reclaimed_val=held, failed_or_lost_vah=failed,
                            wk_val_state=wk_val, wk_vah_state=wk_vah, balance_overlapping=bal)


def old_rule(c):
    """The Oct 31 rule as committed before Nov 5 (frozen copy for the regression check)."""
    bull = c.price >= c.htf_val and c.held_or_reclaimed_val and c.wk_val_state != "ACCEPTED_BELOW"
    bear = c.price <= c.htf_vah and c.failed_or_lost_vah and c.wk_vah_state != "ACCEPTED_ABOVE"
    if bull and not bear: return "BULLISH"
    if bear and not bull: return "BEARISH"
    if c.balance_overlapping: return "BALANCED"
    return "NONE"


class TestContextBase(unittest.TestCase):
    def test_no_directional_test_passed(self):
        self.assertEqual(PF.context_base(ci(price=120.0)), "NONE_NO_EVIDENCE")

    def test_bullish_read_but_weekly_accepted_below_is_conflict(self):
        self.assertEqual(PF.context_base(ci(held=True, wk_val="ACCEPTED_BELOW")), "NONE_CONFLICT")

    def test_bearish_read_but_weekly_accepted_above_is_conflict(self):
        self.assertEqual(PF.context_base(ci(failed=True, wk_vah="ACCEPTED_ABOVE")), "NONE_CONFLICT")

    def test_conflict_with_balance_is_balanced(self):
        self.assertEqual(PF.context_base(ci(held=True, wk_val="ACCEPTED_BELOW", bal=True)), "BALANCED")

    def test_both_reads_pass_is_conflict(self):
        self.assertEqual(PF.context_base(ci(held=True, failed=True)), "NONE_CONFLICT")

    def test_same_as_oct31_rule_when_no_acceptance(self):
        states = ("INSIDE", "TESTING", "ACCEPTED_BELOW", "ACCEPTED_ABOVE")
        for price, held, failed, wv, wh, bal in itertools.product((80.0, 100.0, 120.0), (False, True), (False, True),
                                                                  states, states, (False, True)):
            c = ci(price, held, failed, wv, wh, bal)
            self.assertEqual(PF.market_context(c), old_rule(c))
            base = PF.context_base(c)
            self.assertEqual(old_rule(c), "NONE" if base.startswith("NONE_") else base)

    def test_balanced_only_when_overlap_passes(self):
        """BALANCED is set only when the PD2 / PD / ON overlap test passed (never a fallback), and balance= is written
        only then."""
        states = ("INSIDE", "TESTING", "ACCEPTED_BELOW", "ACCEPTED_ABOVE")
        for price, held, failed, wv, wh in itertools.product((80.0, 100.0, 120.0), (False, True), (False, True), states, states):
            c = ci(price, held, failed, wv, wh, bal=False)
            self.assertNotEqual(PF.context_base(c), "BALANCED")
            for acc in PF.HTF_ACCEPTANCE_VALUES:
                self.assertNotEqual(PF.market_context(c, acc), "BALANCED")
            self.assertEqual(PF.balance_fields(c), {"balance": None, "balance_poc": None})

WK_STATES = ("INSIDE", "TESTING", "ACCEPTED_BELOW", "ACCEPTED_ABOVE")


class TestWeeklyGuard(unittest.TestCase):
    """Clarified Nov 5, 2026: every BULLISH needs price not ACCEPTED_BELOW the weekly VAL; every BEARISH needs not
    ACCEPTED_ABOVE the weekly VAH; failure = NONE_CONFLICT -> NONE."""
    def test_acceptance_bullish_but_weekly_val_accepted_below_is_conflict(self):
        r = PF.resolve_context("NONE_NO_EVIDENCE", "ABOVE", wk_val_state="ACCEPTED_BELOW", wk_vah_state="INSIDE")
        self.assertEqual(r, dict(market_context="NONE", context_source="NONE", resolved="NONE_CONFLICT", weekly_guard="FAIL"))

    def test_acceptance_bearish_but_weekly_vah_accepted_above_is_conflict(self):
        r = PF.resolve_context("NONE_NO_EVIDENCE", "BELOW", wk_val_state="INSIDE", wk_vah_state="ACCEPTED_ABOVE")
        self.assertEqual(r, dict(market_context="NONE", context_source="NONE", resolved="NONE_CONFLICT", weekly_guard="FAIL"))

    def test_acceptance_bullish_guard_passes(self):
        for wh in WK_STATES:            # the weekly VAH state never blocks a Bullish
            r = PF.resolve_context("NONE_NO_EVIDENCE", "ABOVE", "INSIDE", wh)
            self.assertEqual((r["market_context"], r["context_source"], r["weekly_guard"]), ("BULLISH", "HTF_ACCEPTANCE", "PASS"))

    def test_acceptance_bearish_guard_passes(self):
        for wv in WK_STATES:            # the weekly VAL state never blocks a Bearish
            r = PF.resolve_context("NONE_NO_EVIDENCE", "BELOW", wv, "INSIDE")
            self.assertEqual((r["market_context"], r["context_source"], r["weekly_guard"]), ("BEARISH", "HTF_ACCEPTANCE", "PASS"))

    def test_guard_on_every_bullish_and_bearish(self):
        for base, acc, wv, wh in itertools.product(PF.CONTEXT_BASE_VALUES, PF.HTF_ACCEPTANCE_VALUES, WK_STATES, WK_STATES):
            r = PF.resolve_context(base, acc, wv, wh)
            m = r["market_context"]
            self.assertIn(m, ("BULLISH", "BEARISH", "BALANCED", "NONE"))
            if m == "BULLISH": self.assertNotEqual(wv, "ACCEPTED_BELOW", (base, acc, wv, wh))
            if m == "BEARISH": self.assertNotEqual(wh, "ACCEPTED_ABOVE", (base, acc, wv, wh))
            if r["weekly_guard"] == "FAIL": self.assertEqual((m, r["resolved"]), ("NONE", "NONE_CONFLICT"))
            # with the guard passing, the precedence table is unchanged
            if r["weekly_guard"] != "FAIL": self.assertEqual(m, PRECEDENCE[(base, acc)], (base, acc, wv, wh))

    def test_balanced_untouched_by_the_guard(self):
        for acc, wv, wh in itertools.product(PF.HTF_ACCEPTANCE_VALUES, WK_STATES, WK_STATES):
            self.assertEqual(PF.apply_htf_acceptance("BALANCED", acc, wv, wh), "BALANCED")

    def test_market_context_through_context_inputs(self):
        c = ci(price=120.0, wk_val="ACCEPTED_BELOW")          # no read passed: NONE_NO_EVIDENCE
        self.assertEqual(PF.context_base(c), "NONE_NO_EVIDENCE")
        self.assertEqual(PF.market_context(c, "ABOVE"), "NONE")
        self.assertEqual(PF.market_context(ci(price=120.0), "ABOVE"), "BULLISH")
        c = ci(price=80.0, wk_vah="ACCEPTED_ABOVE")
        self.assertEqual(PF.market_context(c, "BELOW"), "NONE")
        self.assertEqual(PF.market_context(ci(price=80.0), "BELOW"), "BEARISH")


class TestAcceptanceInvalidation(unittest.TestCase):
    """Nov 5, 2026: an acceptance-based context invalidates at the composite edge it is accepted beyond."""
    WK_VAL, WK_VAH, HTF_VAL, HTF_VAH = 95.0, 105.0, 90.0, 110.0

    def inv(self, ctx, source):
        return PF.invalidation(ctx, self.WK_VAL, self.WK_VAH, self.HTF_VAL, self.HTF_VAH, source=source)

    def test_acceptance_bullish_below_composite_vah(self):
        self.assertEqual(self.inv("BULLISH", "HTF_ACCEPTANCE"), {"invalidate_below": 110.0, "invalidate_above": None})

    def test_acceptance_bearish_above_composite_val(self):
        self.assertEqual(self.inv("BEARISH", "HTF_ACCEPTANCE"), {"invalidate_below": None, "invalidate_above": 90.0})

    def test_base_context_unchanged(self):
        self.assertEqual(self.inv("BULLISH", "BASE"), {"invalidate_below": 95.0, "invalidate_above": None})
        self.assertEqual(self.inv("BEARISH", "BASE"), {"invalidate_below": None, "invalidate_above": 105.0})
        self.assertEqual(PF.invalidation("BULLISH", 95.0, 105.0, 90.0, 110.0), {"invalidate_below": 95.0, "invalidate_above": None})
        for ctx in ("BALANCED", "NONE"):
            for src in ("BASE", "HTF_ACCEPTANCE", "NONE"):
                self.assertEqual(self.inv(ctx, src), {"invalidate_below": None, "invalidate_above": None})


def bars_beyond(start, end, level, above=True, vol=10):
    """1-minute bars closing from start to end (inclusive), all closing beyond the level."""
    out, t = [], start
    px = level + 5.0 if above else level - 5.0
    while t <= end:
        out.append(M.Bar(close_ct=t, open=px, high=px + 1, low=px - 1, close=px, buy_vol=vol, sell_vol=vol))
        t += timedelta(minutes=1)
    return out


class TestCutoff0810(unittest.TestCase):
    """PO-9 at the HTF edge uses only bars closed at or before 08:10 CT (bar stamped 08:10 = trades 08:09:00-08:09:59.999)."""
    D = datetime(2025, 10, 22, tzinfo=CT).date()
    AS_OF = datetime.combine(D, time(8, 10), tzinfo=CT)
    VAH, VAL = 24000.0, 23800.0

    def inside(self, t):
        return M.Bar(close_ct=t, open=23900, high=23905, low=23895, close=23900, buy_vol=10, sell_vol=10)

    def state(self, bars):
        return M.acceptance_state(bars, "VAH", self.VAH, self.VAL, self.VAH + 5, self.AS_OF, "HTFVAH")

    def at(self, hh, mm):
        return datetime.combine(self.D, time(hh, mm), tzinfo=CT)

    def test_60_minutes_by_0810_accepts(self):
        bars = [self.inside(self.at(7, 9))] + bars_beyond(self.at(7, 10), self.at(8, 10), self.VAH)
        st = self.state(bars)
        self.assertEqual((st.state, st.minutes_since_first_close), ("ACCEPTED_ABOVE", 60))

    def test_59_minutes_by_0810_is_testing_even_with_later_bars(self):
        bars = [self.inside(self.at(7, 10))] + bars_beyond(self.at(7, 11), self.at(10, 0), self.VAH)
        st = self.state(bars)
        self.assertEqual((st.state, st.minutes_since_first_close), ("TESTING", 59))

    def test_bar_closing_after_0810_is_ignored(self):
        bars = bars_beyond(self.at(6, 0), self.at(8, 10), self.VAH) + [self.inside(self.at(8, 11))]
        self.assertEqual(self.state(bars).state, "ACCEPTED_ABOVE")

    def test_bar_stamped_0810_is_used(self):
        bars = bars_beyond(self.at(6, 0), self.at(8, 9), self.VAH) + [self.inside(self.at(8, 10))]
        self.assertNotEqual(self.state(bars).state, "ACCEPTED_ABOVE")   # the 08:10 bar closed back inside

    def test_thresholds_unchanged(self):
        self.assertEqual((M.ACCEPT_MINUTES, M.ACCEPT_CLOSE_SHARE, M.ACCEPT_VOLUME_SHARE), (60, 0.80, 0.20))


class TestPlanHTFAcceptance(TestPlanBuilder):
    """Through the plan builder: price 23990 above an HTF VAH of 23950 all night, bars low above the HTF VAL."""
    def _kv(self, text):
        return {l.split("=", 1)[0]: l.split("=", 1)[1] for l in text.splitlines() if "=" in l and not l.startswith("#")}

    def _packet(self):
        p = dict(self.packet)
        p["levels"] = [l for l in p["levels"] if not l["name"].startswith("HTF")] + [
            {"name": "HTFVAL", "price": 23700.0}, {"name": "HTFVAH", "price": 23950.0}, {"name": "HTFPOC", "price": 23800.0}]
        return p

    def test_no_evidence_plus_above_is_bullish(self):
        ev = {}
        text, side = P.build(self._packet(), self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
        kv = self._kv(text)
        self.assertEqual(kv["context_base"], "NONE_NO_EVIDENCE")
        self.assertEqual(kv["htf_acceptance"], "ABOVE")
        self.assertEqual(kv["market_context"], "BULLISH")
        self.assertEqual(kv["context"], "Bullish")
        self.assertIn("# htf_acceptance: " + PF.HTF_ACCEPTANCE_LABEL, text)
        self.assertTrue(kv["htfvah_state"].startswith("accept=ABOVE"))
        self.assertEqual(side["htf_acceptance"], "ABOVE")
        vah_ev = [e for e in ev["htf_accept"] if e["name"] == "HTFVAH"][0]
        self.assertIsNotNone(vah_ev["first_close_ct"])
        self.assertLessEqual(vah_ev["window_to"], self.as_of.isoformat())

    def test_bars_after_0810_do_not_change_the_plan(self):
        later = [M.Bar(close_ct=self.as_of + timedelta(minutes=k), open=23900, high=23905, low=23600, close=23650,
                       buy_vol=10, sell_vol=500) for k in range(1, 120)]
        a, _ = P.build(self._packet(), self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        b, _ = P.build(self._packet(), list(self.bars) + later, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertEqual(a, b)

    def test_htf_inside_gives_none_acceptance(self):
        text, _ = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertEqual(self._kv(text)["htf_acceptance"], "NONE")   # fixture price 23990 inside HTF 23900-24300


    def test_acceptance_bullish_invalidates_below_composite_vah(self):
        ev = {}
        text, side = P.build(self._packet(), self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
        kv = self._kv(text)
        self.assertEqual((kv["context_source"], kv["weekly_guard"]), ("HTF_ACCEPTANCE", "PASS"))
        self.assertEqual(kv["invalidate_below"], f"{23950.0 - 2 * P.TICK:.2f}|Balanced")   # existing writer: edge - 2 ticks
        self.assertNotIn("invalidate_above", kv)
        self.assertEqual(ev["invalidation"], {"invalidate_below": 23950.0, "invalidate_above": None})
        self.assertEqual(side["context_source"], "HTF_ACCEPTANCE")

    def test_weekly_val_accepted_below_blocks_acceptance_bullish(self):
        from unittest import mock
        real = M.acceptance_state

        def fake(bars, edge, level, other, price, as_of, name):
            st = real(bars, edge, level, other, price, as_of, name)
            if name == "WKVAL":
                return M.AcceptanceState(name, level, "ACCEPTED_BELOW", False, 90, 1.0, 1.0, as_of)
            return st
        ev = {}
        with mock.patch.object(M, "acceptance_state", side_effect=fake):
            text, _ = P.build(self._packet(), self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
        kv = self._kv(text)
        self.assertEqual((kv["context_base"], kv["htf_acceptance"]), ("NONE_NO_EVIDENCE", "ABOVE"))
        self.assertEqual((kv["market_context"], kv["context"], kv["weekly_guard"], kv["context_source"]),
                         ("NONE", "None", "FAIL", "NONE"))
        self.assertEqual(ev["context_resolved"], "NONE_CONFLICT")
        self.assertNotIn("invalidate_below", kv); self.assertNotIn("draw", kv)

    def test_balance_lines_equal_the_map_composite(self):
        """BALANCED from the map's overlap test; balance= / balance_poc= are the packet's merged VAL-VAH / POC exactly."""
        p = dict(self.packet)
        p["balance_composite"] = {"available": True, "overlapping": True, "members": ["PD", "ON"],
                                  "val": 23874.25, "vah": 24033.75, "poc": 23925.0}
        ev = {}
        text, _ = P.build(p, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
        kv = self._kv(text)
        self.assertEqual((kv["balance"], kv["balance_poc"]), ("23874.25-24033.75", "23925.00"))
        if kv["market_context"] == "BALANCED":
            self.assertEqual(ev["context_base"], "BALANCED")
        p["balance_composite"] = {"overlapping": False}
        text, _ = P.build(p, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        kv = self._kv(text)
        self.assertNotIn("balance", kv); self.assertNotEqual(kv["market_context"], "BALANCED")

if __name__ == "__main__":
    unittest.main()
