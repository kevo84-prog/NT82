"""P0.5 unit tests: execution model v3.4, run on Book 1's own fills.simulate (unchanged, book1_ref) on a
synthetic harness tape. Long and short cases for every rule in the checklist:
  market entry 250 ms after the bar close at the best bid (sell) / ask (buy);
  target fills only 1 tick through; stop fills 1 tick adverse (below a long's stop, above a short's),
  2 and 4 ticks in stress; same-tick stop and target = stop; commission $2.87 per side per NQ in net R;
  14:55 CT flatten.
"""
import datetime as dt
import gzip
import os
import tempfile
import unittest

from book1a.book1_import import fills
from book1a.ledger import Trade

D = dt.date(2025, 10, 22)
HEADER = "time_local,price,bid,ask,volume,aggressor\n"


def row(h, m, s, ms, price, bid, ask, vol=1, ag="B"):
    t = dt.datetime.combine(D, dt.time(h, m, s, ms * 1000))
    return f"{t.strftime('%Y-%m-%d %H:%M:%S')}.{ms * 10000:07d},{price:.2f},{bid:.2f},{ask:.2f},{vol},{ag}\n"


class TapeCase(unittest.TestCase):
    def tape(self, rows):
        self.tmp = tempfile.TemporaryDirectory()
        p = os.path.join(self.tmp.name, "tape.csv.gz")
        with gzip.open(p, "wt") as f:
            f.write(HEADER); f.writelines(rows)
        return fills.Tape(p)

    def tearDown(self):
        if hasattr(self, "tmp"):
            self.tmp.cleanup()


class TestEntry(TapeCase):
    def test_long_fills_at_ask_250ms_after_close(self):
        # bar closes 09:03:00; quotes move at 09:03:00.100 and 09:03:00.400
        tape = self.tape([row(9, 2, 59, 900, 24000.00, 23999.75, 24000.00),
                          row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25),     # last trade at or before +250 ms
                          row(9, 3, 0, 400, 24000.50, 24000.25, 24000.50),
                          row(9, 10, 0, 0, 24030.50, 24030.25, 24030.50)])
        m = fills.simulate(tape, +1, dt.datetime.combine(D, dt.time(9, 3)), stop=23990.0, target=24030.0)
        self.assertEqual(m["entry_time"], dt.datetime.combine(D, dt.time(9, 3, 0, 250000)))
        self.assertEqual(m["entry"], 24000.25)        # the ask at 09:03:00.250 (from the 09:03:00.100 trade)

    def test_short_fills_at_bid(self):
        tape = self.tape([row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25),
                          row(9, 10, 0, 0, 23969.50, 23969.25, 23969.50)])
        m = fills.simulate(tape, -1, dt.datetime.combine(D, dt.time(9, 3)), stop=24010.0, target=23970.0)
        self.assertEqual(m["entry"], 24000.00)

    def test_latency_1000ms_stress(self):
        tape = self.tape([row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25),
                          row(9, 3, 0, 900, 24002.00, 24001.75, 24002.00),
                          row(9, 10, 0, 0, 24031.50, 24031.25, 24031.50)])
        m = fills.simulate(tape, +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0, latency_ms=1000)
        self.assertEqual(m["entry"], 24002.00)


class TestTarget(TapeCase):
    def test_long_target_needs_1_tick_through(self):
        base = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25)]
        touch = base + [row(9, 5, 0, 0, 24030.00, 24029.75, 24030.00)]          # touches the target only
        m = fills.simulate(self.tape(touch), +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0)
        self.assertEqual(m["reason"], "DATA_END")                                # no fill
        through = touch + [row(9, 6, 0, 0, 24030.25, 24030.00, 24030.25)]        # 1 tick through
        m = fills.simulate(self.tape(through), +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0)
        self.assertEqual((m["reason"], m["exit"]), ("TARGET", 24030.0))          # fill price = the target
        self.assertEqual(m["exit_time"], dt.datetime.combine(D, dt.time(9, 6)))
        self.assertEqual(m["ticks"], 119.0)                                      # (24030 - 24000.25) / 0.25

    def test_short_target_needs_1_tick_through(self):
        base = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25), row(9, 5, 0, 0, 23970.00, 23969.75, 23970.00)]
        m = fills.simulate(self.tape(base), -1, dt.datetime.combine(D, dt.time(9, 3)), 24010.0, 23970.0)
        self.assertEqual(m["reason"], "DATA_END")
        m = fills.simulate(self.tape(base + [row(9, 6, 0, 0, 23969.75, 23969.50, 23969.75)]), -1,
                           dt.datetime.combine(D, dt.time(9, 3)), 24010.0, 23970.0)
        self.assertEqual((m["reason"], m["exit"], m["ticks"]), ("TARGET", 23970.0, 120.0))


class TestStop(TapeCase):
    def setUp(self):
        self.rows = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25), row(9, 5, 0, 0, 23990.00, 23989.75, 23990.00)]

    def test_long_stop_1_tick_below(self):
        m = fills.simulate(self.tape(self.rows), +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0)
        self.assertEqual((m["reason"], m["exit"]), ("STOP", 23989.75))
        self.assertEqual(m["ticks"], -42.0)

    def test_long_stop_stress_2_and_4(self):
        for slip, px in ((2, 23989.50), (4, 23989.00)):
            m = fills.simulate(self.tape(self.rows), +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0, stop_slip=slip)
            self.assertEqual(m["exit"], px)

    def test_short_stop_1_tick_above(self):
        rows = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25), row(9, 5, 0, 0, 24010.00, 24009.75, 24010.00)]
        m = fills.simulate(self.tape(rows), -1, dt.datetime.combine(D, dt.time(9, 3)), 24010.0, 23970.0)
        self.assertEqual((m["reason"], m["exit"]), ("STOP", 24010.25))
        m = fills.simulate(self.tape(rows), -1, dt.datetime.combine(D, dt.time(9, 3)), 24010.0, 23970.0, stop_slip=4)
        self.assertEqual(m["exit"], 24011.00)

    def test_stop_triggers_on_a_trade_through_not_a_touch_of_quote(self):
        rows = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25), row(9, 5, 0, 0, 23990.25, 23990.00, 23990.25)]
        m = fills.simulate(self.tape(rows), +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0)
        self.assertEqual(m["reason"], "DATA_END")

    def test_v35_gap_fill_differs_only_on_gaps(self):
        gap = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25), row(9, 5, 0, 0, 23985.00, 23984.75, 23985.00)]
        t = dt.datetime.combine(D, dt.time(9, 3))
        self.assertEqual(fills.simulate(self.tape(gap), +1, t, 23990.0, 24030.0)["exit"], 23989.75)                 # v3.4
        self.assertEqual(fills.simulate(self.tape(gap), +1, t, 23990.0, 24030.0, gap_fill=True)["exit"], 23984.75)  # v3.5
        self.assertEqual(fills.simulate(self.tape(self.rows), +1, t, 23990.0, 24030.0, gap_fill=True)["exit"], 23989.75)


class TestTie(TapeCase):
    def test_same_timestamp_stop_and_target_is_stop(self):
        rows = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25),
                row(9, 5, 0, 0, 24030.25, 24030.00, 24030.25),     # target 1 tick through ...
                row(9, 5, 0, 0, 23990.00, 23989.75, 23990.00)]     # ... and the stop, same timestamp
        m = fills.simulate(self.tape(rows), +1, dt.datetime.combine(D, dt.time(9, 3)), 23990.0, 24030.0)
        self.assertEqual((m["reason"], m["exit"]), ("STOP", 23989.75))
        rows = [row(9, 3, 0, 100, 24000.25, 24000.00, 24000.25),
                row(9, 5, 0, 0, 23969.75, 23969.50, 23969.75), row(9, 5, 0, 0, 24010.00, 24009.75, 24010.00)]
        m = fills.simulate(self.tape(rows), -1, dt.datetime.combine(D, dt.time(9, 3)), 24010.0, 23970.0)
        self.assertEqual((m["reason"], m["exit"]), ("STOP", 24010.25))


class TestFlatten(TapeCase):
    def test_1455_flatten_long_at_bid_short_at_ask(self):
        rows = [row(14, 30, 0, 100, 24000.25, 24000.00, 24000.25),
                row(14, 54, 59, 990, 24005.00, 24004.75, 24005.00),
                row(14, 55, 0, 0, 24005.25, 24005.00, 24005.25),
                row(14, 56, 0, 0, 24006.00, 24005.75, 24006.00)]
        t = dt.datetime.combine(D, dt.time(14, 30))
        m = fills.simulate(self.tape(rows), +1, t, 23990.0, 24030.0)
        self.assertEqual((m["reason"], m["exit"], m["exit_time"]), ("FLATTEN", 24004.75, dt.datetime.combine(D, dt.time(14, 55))))
        m = fills.simulate(self.tape(rows), -1, t, 24010.0, 23970.0)
        self.assertEqual((m["reason"], m["exit"]), ("FLATTEN", 24005.00))


class TestCommissionInNetR(unittest.TestCase):
    def test_commission_287_per_side_per_contract(self):
        tr = Trade("R1", "T", "2025-10-22", "09:03", "LONG", 1, 24000.25, 23990.0, 24030.0, "09:06", 24030.0, "TARGET_FIRST")
        self.assertAlmostEqual(tr.commission_usd, 5.74)
        self.assertAlmostEqual(tr.net_usd, 119 * 5 - 5.74)
        self.assertAlmostEqual(tr.realized_net_R, (119 - 1.148) / 41)       # stop 41 ticks from the fill
        tr3 = Trade("R4", "T", "2025-10-22", "09:03", "SHORT", 3, 24000.0, 24010.0, 23970.0, "09:06", 24010.25, "STOP_FIRST")
        self.assertAlmostEqual(tr3.commission_usd, 17.22)
        self.assertAlmostEqual(tr3.net_usd, -41 * 5 * 3 - 17.22)


if __name__ == "__main__":
    unittest.main()
