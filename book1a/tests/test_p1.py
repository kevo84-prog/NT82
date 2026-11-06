import tempfile
import unittest
from datetime import date
from pathlib import Path

from book1a import gamma_ranks as G, gex_check as X
from book1a import sessions as S


class TestGammaRanks(unittest.TestCase):
    def test_hand_ranking(self):
        net = {24000.0: 1.2e9, 24100.0: -3.5e9, 24200.0: 2.0e9, 23900.0: -0.5e9, 24300.0: 2.0e9}
        r = G.rank_strikes(net, top=3)
        self.assertEqual([(x[0], x[1]) for x in r], [(1, 24100.0), (2, 24200.0), (3, 24300.0)])   # tie 2.0e9: lower strike first
        s = G.signed_ranks(net, top=2)
        self.assertEqual([x[1] for x in s["positive"]], [24200.0, 24300.0])
        self.assertEqual([x[1] for x in s["negative"]], [24100.0, 23900.0])
        self.assertEqual(G.as_levels(r, shift_pts=256.0), {"gamma1": 24356.0, "gamma2": 24456.0, "gamma3": 24556.0})


class TestGexCheck(unittest.TestCase):
    def test_coverage_table(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "gex.csv"
            sess = S.phase_sessions("phase1")
            lines = ["session,ok,regime,call_resistance,put_support,hvl,call_resistance_0dte,put_support_0dte,hvl_0dte,call_resistance_nt"]
            for s in sess[:-1]:
                lines.append(f"{s},True,positive,25100,24800,24950,25050,24850,24940,")
            p.write_text("\n".join(lines) + "\n")
            out = Path(d) / "out.md"
            summary = X.check(p, out, sessions=sess)
            self.assertEqual(summary["sessions"], 10); self.assertEqual(summary["rows_ok"], 9); self.assertEqual(summary["missing"], 1)
            txt = out.read_text()
            self.assertIn("FAIL", txt); self.assertIn("no row", txt)
            self.assertIn("2025-10-21T23:00:00-04:00", txt)     # D-1 23:00 ET for Oct 22

    def test_expected_blank_0dte_after_roll(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "gex.csv"
            p.write_text("session,ok,regime,call_resistance,put_support,hvl,call_resistance_0dte,put_support_0dte,hvl_0dte\n"
                         "2025-12-17,True,negative,25100,24800,24950,,,\n")
            out = Path(d) / "out.md"
            summary = X.check(p, out, sessions=[date(2025, 12, 17)])
            self.assertEqual(summary["problems"], 0)
            self.assertIn("expected after the roll", out.read_text())


if __name__ == "__main__":
    unittest.main()
