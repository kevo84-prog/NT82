"""Context invalidation operator (Kyron, Nov 5, 2026): an acceptance-based context invalidates on 3 consecutive 1-minute
closes STRICTLY beyond the buffered line the plan writes (Bullish: close < invalidate_below; Bearish: close >
invalidate_above). The counter is S1.4's UpdatePlanState (book1_ref/jeron_harness/nt_source/JeronOrderFlowStrategy.cs,
lines 1874-1883; AcceptBars = 3 at line 791), run once per closed bar of the strategy's primary 1-minute series.

The C# cannot run inside this suite, so (1) the exact source lines are pinned here (the R4 harness exe is built from a
byte-identical copy of this file), and (2) `s14_counter` transcribes those two lines one for one and is tested on the
cases Kyron named."""
import hashlib
import os
import unittest
from pathlib import Path

from book1a import plan_fields as PF
from book1a import plan_v24 as P

CODE = Path(__file__).resolve().parents[2]
SRC = CODE / "book1_ref" / "jeron_harness" / "nt_source" / "JeronOrderFlowStrategy.cs"
LINES = {   # line number -> exact text (stripped)
    791: "AcceptBars = 3;",
    1876: "invAboveCount = ev.C > plan.InvAbove ? invAboveCount + 1 : 0;",
    1877: 'if (invAboveCount >= Math.Max(1, AcceptBars)) { InvalidatePlan(ev, "above " + JeronFmt.P(plan.InvAbove), plan.InvAboveContext); return; }',
    1881: "invBelowCount = ev.C < plan.InvBelow ? invBelowCount + 1 : 0;",
    1882: 'if (invBelowCount >= Math.Max(1, AcceptBars)) InvalidatePlan(ev, "below " + JeronFmt.P(plan.InvBelow), plan.InvBelowContext);',
}
ACCEPT_BARS = 3


def s14_counter(closes, line, side):
    """Lines 1876-1877 / 1881-1882 transcribed: returns the index of the close that invalidates, or None."""
    n = 0
    for i, c in enumerate(closes):
        if side == "below":
            n = n + 1 if c < line else 0
        else:
            n = n + 1 if c > line else 0
        if n >= max(1, ACCEPT_BARS):
            return i
    return None


def plan_line(edge, side):
    """The buffered line plan_v24 writes for an edge (edge - 2 ticks below, edge + 2 ticks above)."""
    return P._r(edge - 2 * P.TICK) if side == "below" else P._r(edge + 2 * P.TICK)


class TestS14Source(unittest.TestCase):
    def test_operator_lines_pinned(self):
        src = SRC.read_text(encoding="utf-8").splitlines()
        for no, text in LINES.items():
            self.assertEqual(src[no - 1].strip(), text, f"line {no}")

    def test_harness_source_identical(self):
        root = Path(os.environ.get("BOOK1_ROOT", r"K:\Databento_BackTesting"))
        built = root / "jeron_harness" / "nt_source" / "JeronOrderFlowStrategy.cs"
        if not built.exists():
            self.skipTest("Book 1 harness source not on this machine")
        h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h(SRC), h(built))


class TestInvalidationCounter(unittest.TestCase):
    VAH, VAL = 25394.75, 23640.0

    def test_plan_lines(self):
        inv = PF.invalidation("BULLISH", 25705.0, 26000.0, self.VAL, self.VAH, source="HTF_ACCEPTANCE")
        self.assertEqual(plan_line(inv["invalidate_below"], "below"), 25394.25)
        inv = PF.invalidation("BEARISH", 25705.0, 26000.0, self.VAL, self.VAH, source="HTF_ACCEPTANCE")
        self.assertEqual(plan_line(inv["invalidate_above"], "above"), 23640.5)

    def test_bullish_three_closes_strictly_below(self):
        line = 25394.25
        self.assertEqual(s14_counter([25400, 25394.0, 25393.0, 25390.0], line, "below"), 3)

    def test_close_on_the_line_does_not_count(self):
        line = 25394.25
        self.assertIsNone(s14_counter([25394.25] * 10, line, "below"))
        self.assertIsNone(s14_counter([25394.0, 25394.0, 25394.25, 25394.0, 25394.0], line, "below"))
        self.assertIsNone(s14_counter([23640.5] * 10, 23640.5, "above"))

    def test_two_beyond_then_one_inside_resets(self):
        line = 25394.25
        closes = [25394.0, 25393.0, 25395.0, 25394.0, 25393.0]          # 2 below, 1 back above, 2 below
        self.assertIsNone(s14_counter(closes, line, "below"))
        self.assertEqual(s14_counter(closes + [25392.0], line, "below"), 5)
        up = [23641.0, 23642.0, 23640.0, 23641.0, 23641.5]
        self.assertIsNone(s14_counter(up, 23640.5, "above"))
        self.assertEqual(s14_counter(up + [23645.0], 23640.5, "above"), 5)

    def test_bearish_three_closes_strictly_above(self):
        self.assertEqual(s14_counter([23630.0, 23641.0, 23640.75, 23650.0], 23640.5, "above"), 3)


if __name__ == "__main__":
    unittest.main()
