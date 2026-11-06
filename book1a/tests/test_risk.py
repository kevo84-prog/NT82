"""P0.10 unit tests: exact numbers from the Book 1A Phase 0 checklist and replay plan U3."""
import unittest

from book1a import risk
from book1a.risk import DayRiskState, RiskConfig, estimate_risk, estimate_risk_cents, largest_stop_that_fits, size_for


class TestFormula(unittest.TestCase):
    def test_formula_example_60_ticks(self):
        # replay plan U3: a 60-tick stop at 3 NQ = $947.22 (fits); 4 NQ = $1,262.96 (does not)
        self.assertEqual(estimate_risk_cents(60, 3), 94_722)
        self.assertEqual(estimate_risk_cents(60, 4), 126_296)
        self.assertAlmostEqual(estimate_risk(60, 3), 947.22, places=2)
        self.assertAlmostEqual(estimate_risk(60, 4), 1262.96, places=2)

    def test_components(self):
        # (stop ticks + 2) x $5 x N + $5.74 x N
        self.assertEqual(estimate_risk_cents(0, 1), 2 * 500 + 574)
        self.assertEqual(estimate_risk_cents(10, 2), (12 * 500 + 574) * 2)

    def test_largest_stops_that_fit_1000(self):
        # checklist P0.10: 1 NQ 196, 2 NQ 96, 3 NQ 63, 5 NQ 36, 10 NQ 16 ticks
        expected = {1: 196, 2: 96, 3: 63, 5: 36, 10: 16}
        for n, s in expected.items():
            with self.subTest(n=n):
                self.assertEqual(largest_stop_that_fits(n), s)
                self.assertLessEqual(estimate_risk_cents(s, n), 100_000)
                self.assertGreater(estimate_risk_cents(s + 1, n), 100_000)


class TestSizing(unittest.TestCase):
    def test_60_tick_stop_sizes_to_3(self):
        self.assertEqual(size_for(60, 100_000), 3)

    def test_196_fits_197_rejects(self):
        self.assertEqual(size_for(196, 100_000), 1)
        self.assertEqual(size_for(197, 100_000), 0)

    def test_16_tick_stop_sizes_to_10(self):
        self.assertEqual(size_for(16, 100_000), 10)
        self.assertEqual(size_for(17, 100_000), 9)


class TestDayState(unittest.TestCase):
    def test_accept_and_reject_above_budget(self):
        day = DayRiskState()
        d = day.pre_trade_check(60)
        self.assertTrue(d.accepted)
        self.assertEqual(d.contracts, 3)
        self.assertEqual(d.estimated_risk_cents, 94_722)
        self.assertEqual(d.reason, "ACCEPT")
        r = day.pre_trade_check(197)       # 1 NQ = $1,000.74 > $1,000
        self.assertFalse(r.accepted)
        self.assertEqual(r.reason, "RISK_REJECT:PER_TRADE_BUDGET")
        self.assertEqual(r.contracts, 0)

    def test_remaining_daily_budget_applied(self):
        # $2,000 - realized losses - open risk
        day = DayRiskState()
        d1 = day.pre_trade_check(60); day.on_entry(d1)            # reserves $947.22
        self.assertEqual(day.remaining_daily_cents(), 200_000 - 94_722)
        day.on_exit(-90_000)                                       # loss $900 (within plan)
        self.assertEqual(day.remaining_daily_cents(), 200_000 - 90_000)
        d2 = day.pre_trade_check(60); day.on_entry(d2)            # 3 NQ still fits (947.22 <= 1,000 and <= 1,100)
        self.assertEqual(d2.contracts, 3)
        day.on_exit(-80_000)                                       # second loss -> 2-loss halt
        self.assertEqual(day.halt_reason, "LOSS_HALT")
        self.assertEqual(day.pre_trade_check(10).reason, "HALT:LOSS_HALT")

    def test_daily_budget_shrinks_size_then_rejects(self):
        cfg = RiskConfig(max_consecutive_losses=99, max_trades_per_day=99)
        day = DayRiskState(cfg)
        day.realized_losses_cents = 150_000                        # $1,500 lost: $500 remaining
        d = day.pre_trade_check(60)                                # 1 NQ = $315.74 fits, 2 NQ = $631.48 does not
        self.assertTrue(d.accepted); self.assertEqual(d.contracts, 1)
        self.assertEqual(d.budget_cents, 50_000)
        day.realized_losses_cents = 170_000                        # $300 remaining: 1 NQ at 60 ticks = $315.74 -> reject
        r = day.pre_trade_check(60)
        self.assertFalse(r.accepted); self.assertEqual(r.reason, "RISK_REJECT:DAILY_BUDGET")

    def test_risk_breach_fill(self):
        day = DayRiskState()
        d = day.pre_trade_check(20); day.on_entry(d)               # 1 NQ... actually 8 NQ: (22*5*8)+5.74*8 = 925.92
        self.assertEqual(d.contracts, 8)
        ev = day.on_exit(-100_000, trade_id="T1")                  # realized loss $1,000 > planned $925.92
        self.assertIsNotNone(ev)
        self.assertEqual(ev["event"], "RISK_BREACH_FILL")
        self.assertEqual(ev["overrun_cents"], 100_000 - 92_592)
        self.assertEqual(len(day.breaches), 1)
        # a loss within plan is not a breach
        d2 = day.pre_trade_check(20); day.on_entry(d2)
        self.assertIsNone(day.on_exit(-50_000, trade_id="T2"))

    def test_three_trade_cap(self):
        cfg = RiskConfig(max_consecutive_losses=99)
        day = DayRiskState(cfg)
        for _ in range(3):
            d = day.pre_trade_check(10); day.on_entry(d); day.on_exit(+10_000)
        self.assertEqual(day.halt_reason, "TRADE_CAP")
        self.assertEqual(day.pre_trade_check(10).reason, "HALT:TRADE_CAP")

    def test_two_loss_halt_before_cap(self):
        day = DayRiskState()
        for _ in range(2):
            d = day.pre_trade_check(10); day.on_entry(d); day.on_exit(-10_000)
        self.assertEqual(day.trades_entered, 2)
        self.assertEqual(day.halt_reason, "LOSS_HALT")

    def test_daily_dollar_limit_halts(self):
        cfg = RiskConfig(max_consecutive_losses=99, max_trades_per_day=99)
        day = DayRiskState(cfg)
        d = day.pre_trade_check(196); day.on_entry(d)              # 1 NQ, $995.74 planned
        day.on_exit(-99_574)
        d = day.pre_trade_check(196); day.on_entry(d)
        day.on_exit(-100_500)                                      # breach; total losses $2,000.74 >= $2,000
        self.assertEqual(day.halt_reason, "DAILY_LIMIT")
        self.assertEqual(day.pre_trade_check(10).reason, "HALT:DAILY_LIMIT")

    def test_rejected_candidate_does_not_count_as_trade(self):
        day = DayRiskState()
        day.pre_trade_check(500)
        self.assertEqual(day.trades_entered, 0)

    def test_gains_do_not_restore_budget_by_default(self):
        day = DayRiskState()
        d = day.pre_trade_check(10); day.on_entry(d); day.on_exit(-50_000)
        d = day.pre_trade_check(10); day.on_entry(d); day.on_exit(+80_000)
        self.assertEqual(day.remaining_daily_cents(), 200_000 - 50_000)


if __name__ == "__main__":
    unittest.main()
