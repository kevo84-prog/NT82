import unittest
from datetime import date

from book1a import sessions as S


class TestSessions(unittest.TestCase):
    def test_phase_counts_match_book1(self):
        self.assertEqual(len(S.phase_sessions("phase1")), 10)
        self.assertEqual(len(S.phase_sessions("phase2")), 21)
        self.assertEqual(len(S.phase_sessions("phase3")), 41)
        self.assertEqual(len(S.phase_sessions("phase4")), 52)
        self.assertEqual(len(S.block1_sessions()), 124)

    def test_half_days_in_roll_days_in_holidays_out(self):
        s = set(S.block1_sessions())
        self.assertIn(date(2025, 11, 28), s); self.assertIn(date(2025, 12, 24), s)
        self.assertIn(date(2025, 12, 15), s); self.assertIn(date(2026, 3, 16), s)
        for d in S.NO_CASH_SESSION: self.assertNotIn(d, s)


if __name__ == "__main__":
    unittest.main()
