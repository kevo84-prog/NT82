"""gex_v3.level_match: the post-freeze both-absent fix (Phase 3 Step B, Nov 9, 2026). Synthetic values only."""
import math
import unittest

from book1a import gex_v3 as GV

NAN = float("nan")


class TestLevelMatch(unittest.TestCase):
    def test_both_absent_match(self):
        for a in (None, NAN):
            for b in ("", "   ", None):
                self.assertTrue(GV.level_match(a, b), (a, b))

    def test_one_absent_one_present_mismatch(self):
        self.assertFalse(GV.level_match(None, "25475.0"))
        self.assertFalse(GV.level_match(NAN, "25475.0"))
        self.assertFalse(GV.level_match(25475.0, ""))
        self.assertFalse(GV.level_match(25475.0, None))
        self.assertFalse(GV.level_match(math.inf, ""))

    def test_nan_text_cell_is_not_absent(self):
        self.assertFalse(GV.level_match(NAN, "nan"))
        self.assertFalse(GV.level_match(None, "nan"))

    def test_present_values(self):
        self.assertTrue(GV.level_match(26000.0, "26000.0"))
        self.assertTrue(GV.level_match(-229808265.63139772, "-229808265.6313977"))   # inside 1e-9 relative
        self.assertFalse(GV.level_match(26000.0, "26000.25"))
        b = 1000.0
        tol = max(1e-6, 1e-9 * b)
        self.assertTrue(GV.level_match(b + 0.9 * tol, "1000.0"))
        self.assertFalse(GV.level_match(b + 1.5 * tol, "1000.0"))
        big = 6.0e8
        self.assertTrue(GV.level_match(big + 0.5, str(big)))       # 1e-9 * 6e8 = 0.6
        self.assertFalse(GV.level_match(big + 0.7, str(big)))

    def test_other_text_still_raises(self):
        with self.assertRaises(ValueError):
            GV.level_match(26000.0, "abc")
        with self.assertRaises(ValueError):
            GV.level_match(26000.0, "NA")


if __name__ == "__main__":
    unittest.main()
