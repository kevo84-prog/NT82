"""book1a.stress: the 1,000 ms entry stress reaches the frozen replay's M0 entry; synthetic tape only."""
import gzip
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("BOOK1_ROOT", r"K:\Book1A_inputs")
from book1a.book1_import import jeron_engine  # noqa: E402,F401
from jeron_engine import exit_replay as XR, fills  # noqa: E402

from book1a import stress as ST  # noqa: E402
import datetime as dt  # noqa: E402

D = "2025-11-05"
# time, price, bid, ask, size, side: the ask moves from 100.25 to 101.00 between +250 ms and +1,000 ms
ROWS = [(f"{D} 09:00:00.1000000", 100.00, 100.00, 100.25), (f"{D} 09:00:00.5000000", 100.25, 100.00, 100.25),
        (f"{D} 09:00:00.9000000", 100.75, 100.75, 101.00), (f"{D} 09:00:05.0000000", 101.00, 100.75, 101.00),
        (f"{D} 09:10:00.0000000", 110.00, 109.75, 110.00)]


class TestEntryLatency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        p = Path(cls.dir.name) / "tape_x.csv.gz"
        with gzip.open(p, "wt") as f:
            f.write("time_local,price,bid,ask,size,side\n")             # the harness tape has a header row
            for t, pr, b, a in ROWS:
                f.write(f"{t},{pr:.2f},{b:.2f},{a:.2f},1,B\n")
        cls.tape = fills.Tape(p)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def m0(self):
        tr = dict(side=1, signal_end=dt.datetime(2025, 11, 5, 9, 0), stop=95.0, target=105.0)
        return XR.run_model("M0", self.tape, tr, [], stop_slip=1, gap_fill=True, stop_delay_ms=250, crossed="live")

    def test_settings(self):
        self.assertEqual(ST.SETTINGS, {"base": (250, 1), "lat1000": (1000, 1), "slip2": (250, 2), "slip4": (250, 4)})

    def test_m0_entry_moves_and_restores(self):
        self.assertEqual(self.m0()["entry"], 100.25)                  # quote at 09:00:00.250
        with ST.entry_latency(1000):
            self.assertEqual(self.m0()["entry"], 101.00)              # quote at 09:00:01.000
            self.assertEqual((fills.LATENCY_MS, XR.LATENCY_MS), (1000, 1000))
        self.assertEqual(self.m0()["entry"], 100.25)
        self.assertEqual((fills.LATENCY_MS, XR.LATENCY_MS), (250, 250))

    def test_base_is_a_no_op(self):
        orig = XR.replay
        with ST.entry_latency(250):
            self.assertIs(XR.replay, orig)

    def test_restored_after_error(self):
        orig = XR.replay
        with self.assertRaises(ZeroDivisionError):
            with ST.entry_latency(1000):
                1 / 0
        self.assertIs(XR.replay, orig)
        self.assertEqual(fills.LATENCY_MS, 250)


if __name__ == "__main__":
    unittest.main()
