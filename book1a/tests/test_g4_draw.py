"""G4 draw script (book1a.g4_draw) on synthetic ledgers only."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from book1a import g4_draw as G
from book1a import sessions as S

DAYS = [d.isoformat() for d in S.phase_sessions("phase2")]


def fake(strategy, per_day, days=DAYS, price=100.0):
    rows = []
    for d in days:
        for i in range(per_day):
            rows.append(dict(strategy=strategy, trade_id=f"{strategy}-{d}-{i}", date=d, entry_time=f"09:{10 + i:02d}:00.250",
                             entry_price=price + i, exit_price=price - i, net_R=1.0 - i))
    return rows


def write(path, rows):
    cols = list(rows[0]) if rows else list(G.KEYS)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)


def keys(rows):
    return [{k: r[k] for k in G.KEYS} for r in rows]


class TestDraw(unittest.TestCase):
    def test_counts_and_fixed_days(self):
        r4 = keys(fake("R4_BOOK1A", 2))
        out = G.draw(keys(fake("R1_A0", 1)), keys(fake("R2_C1", 1)), keys(fake("R3_C1_RISK", 1)), r4)
        fixed = [r for r in out if r["draw"] == "FIXED_DAY"]
        self.assertEqual(len(fixed), 8)                                   # 4 fixed days x 2
        self.assertEqual({r["date"] for r in fixed}, set(G.FIXED_DAYS))
        a = [r for r in out if r["draw"] == "DRAW_R4"]; b = [r for r in out if r["draw"] == "DRAW_R1R3"]
        self.assertEqual((len(a), len(b), a[0]["pool_size"], b[0]["pool_size"]), (10, 10, 34, 63))
        self.assertFalse({r["date"] for r in a} & set(G.FIXED_DAYS))
        self.assertEqual(len({(r["strategy"], r["trade_id"]) for r in a + b}), 20)
        self.assertTrue({r["strategy"] for r in b} <= {"R1_A0", "R2_C1", "R3_C1_RISK"})

    def test_deterministic_and_pinned(self):
        args = (keys(fake("R1_A0", 1)), keys(fake("R2_C1", 1)), keys(fake("R3_C1_RISK", 1)), keys(fake("R4_BOOK1A", 2)))
        x, y = G.draw(*args), G.draw(*args)
        self.assertEqual(x, y)
        a = [r["trade_id"] for r in x if r["draw"] == "DRAW_R4"]
        self.assertEqual(a, PINNED_R4)                                    # seed 20251205; guards a change of method or numpy
        self.assertNotEqual(a, [r["trade_id"] for r in G.draw(*args, seed=1) if r["draw"] == "DRAW_R4"])

    def test_input_order_does_not_matter(self):
        r4 = keys(fake("R4_BOOK1A", 2))
        a = G.draw([], [], keys(fake("R3_C1_RISK", 1)), r4)
        b = G.draw([], [], list(reversed(keys(fake("R3_C1_RISK", 1)))), list(reversed(r4)))
        self.assertEqual(a, b)

    def test_short_pools_and_no_fixed_trades(self):
        other = [d for d in DAYS if d not in G.FIXED_DAYS][:3]
        out = G.draw(keys(fake("R1_A0", 1, other)), [], [], keys(fake("R4_BOOK1A", 1, other)))
        self.assertEqual([r for r in out if r["draw"] == "FIXED_DAY"], [])
        a = [r for r in out if r["draw"] == "DRAW_R4"]; b = [r for r in out if r["draw"] == "DRAW_R1R3"]
        self.assertEqual((len(a), len(b), a[0]["note"], b[0]["note"]), (3, 3, "SHORT_POOL", "SHORT_POOL"))
        empty = G.draw([], [], [], [])
        self.assertEqual(empty, [])


class TestMain(unittest.TestCase):
    def run_main(self, d, price=100.0):
        p = {s: Path(d) / f"{s}.csv" for s in ("R1", "R2", "R3", "R4")}
        write(p["R1"], fake("R1_A0", 1, price=price)); write(p["R2"], fake("R2_C1", 1, price=price))
        write(p["R3"], fake("R3_C1_RISK", 1, price=price)); write(p["R4"], fake("R4_BOOK1A", 2, price=price))
        out = Path(d) / "sample" / "g4_sample.csv"
        G.main(["--r1", str(p["R1"]), "--r2", str(p["R2"]), "--r3", str(p["R3"]), "--r4", str(p["R4"]), "--out", str(out)])
        return out.read_text(encoding="utf-8"), json.loads(Path(str(out) + ".manifest.json").read_text(encoding="utf-8"))

    def test_outputs_and_outcome_blind(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            s1, m1 = self.run_main(d1); s2, _ = self.run_main(d2, price=5000.0)    # prices / R differ, keys equal
            self.assertEqual(s1, s2)
            self.assertEqual(s1.splitlines()[0], ",".join(G.COLUMNS))
            self.assertEqual(m1["counts"], {"FIXED_DAY": 8, "DRAW_R4": 10, "DRAW_R1R3": 10})
            self.assertEqual((m1["seed"], m1["version"]), (20251205, G.VERSION))
            self.assertEqual(len(m1["inputs"]), 4)

    def test_bad_inputs_stop(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            dup = fake("R4_BOOK1A", 1)[:2]; dup[1]["trade_id"] = dup[0]["trade_id"]
            write(p / "dup.csv", dup)
            with self.assertRaises(SystemExit):
                G.read_keys(p / "dup.csv", "R4")
            write(p / "out.csv", fake("R4_BOOK1A", 1, ["2025-12-05"]))
            with self.assertRaises(SystemExit):
                G.read_keys(p / "out.csv", "R4")
            write(p / "wrong.csv", fake("R2_C1", 1))
            with self.assertRaises(SystemExit):
                G.read_keys(p / "wrong.csv", "R4")


PINNED_R4 = ['R4_BOOK1A-2025-11-24-1', 'R4_BOOK1A-2025-11-26-0', 'R4_BOOK1A-2025-11-10-1', 'R4_BOOK1A-2025-11-11-1',
             'R4_BOOK1A-2025-11-07-1', 'R4_BOOK1A-2025-12-02-1', 'R4_BOOK1A-2025-11-14-0', 'R4_BOOK1A-2025-11-26-1',
             'R4_BOOK1A-2025-12-04-0', 'R4_BOOK1A-2025-11-17-1']   # synthetic pool of 34; numpy 2.x default_rng(20251205)


if __name__ == "__main__":
    unittest.main()
