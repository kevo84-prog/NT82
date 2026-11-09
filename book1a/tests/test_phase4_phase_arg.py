"""Phase 4 Step A (Nov 9, 2026): phase2_report / phase2_review_fields / phase2_review_apply / g4_draw generalized only by
the phase argument (phase4), and the phase4_sessions exposure set. Synthetic inputs only; phase2 / phase3 behaviour is
covered unchanged by their own tests."""
import csv
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from book1a import g4_draw as G, phase2_report as RP, phase2_review_apply as A, phase2_review_fields as F, sessions as S
from book1a import phase4_sessions as P4

P4_EXPOSED = {dt.date(2026, 3, 30), dt.date(2026, 3, 31), dt.date(2026, 4, 1), dt.date(2026, 4, 2), dt.date(2026, 4, 6),
              dt.date(2026, 4, 7), dt.date(2026, 4, 8), dt.date(2026, 4, 9), dt.date(2026, 4, 10)}


class TestSessions(unittest.TestCase):
    def test_52_sessions(self):
        s = S.phase_sessions("phase4")
        self.assertEqual(len(s), 52)
        self.assertNotIn(dt.date(2026, 2, 16), s); self.assertNotIn(dt.date(2026, 4, 3), s)
        self.assertEqual((s[0], s[-1]), (dt.date(2026, 2, 5), dt.date(2026, 4, 21)))

    def test_front_by_roll(self):
        self.assertEqual(P4.front(dt.date(2026, 3, 13)), ("NQH6", "NQ MAR26"))
        self.assertEqual(P4.front(dt.date(2026, 3, 16)), ("NQM6", "NQ JUN26"))
        self.assertIn(dt.date(2026, 3, 16), S.ROLL_DATES)

    def test_exposure_sets_agree(self):
        self.assertEqual(P4.EXPOSED, P4_EXPOSED)
        self.assertEqual(RP.EXPOSED_BY_PHASE["phase4"], P4_EXPOSED)
        self.assertTrue(P4_EXPOSED <= set(S.phase_sessions("phase4")))


class TestPopulations(unittest.TestCase):
    def test_phase4_populations(self):
        pops = RP.populations(S.phase_sessions("phase4"), "phase4")
        self.assertEqual((len(pops["ALL"]), len(pops["UNEXPOSED"])), (52, 43))
        self.assertEqual(set(pops["ALL"]) - set(pops["UNEXPOSED"]), P4_EXPOSED)

    def test_phase2_phase3_unchanged(self):
        self.assertEqual(len(RP.populations(S.phase_sessions("phase2"))["UNEXPOSED"]), 13)
        self.assertEqual(len(RP.populations(S.phase_sessions("phase3"), "phase3")["UNEXPOSED"]), 38)

    def test_report_run_phase4_writes_card(self):
        with tempfile.TemporaryDirectory() as td:
            gex = Path(td) / "gex.csv"
            with open(gex, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["session", "ok", "regime"])
                for d in S.phase_sessions("phase4"):
                    w.writerow([d.isoformat(), "True", "negative"])
            res = RP.run("phase4", {}, {}, {}, str(gex), str(Path(td) / "card.json"))
        self.assertEqual(res["phase"], "phase4"); self.assertEqual(len(res["populations"]["UNEXPOSED"]), 43)

    def test_report_refuses_others(self):
        for ph in ("phase1", "phase5", "Phase4", ""):
            with self.assertRaises(RuntimeError):
                RP.run(ph, {}, {}, {}, "x", "y")


class TestReview(unittest.TestCase):
    def test_fields(self):
        self.assertEqual(F.compute("phase4", [], None, None), [])
        with self.assertRaises(RuntimeError):
            F.compute("phase5", [], None, None)

    def test_apply_paths_and_text(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for run in ("a0", "r4"):
                (root / run / "strategy").mkdir(parents=True)
                (root / run / "strategy" / "JOFS_x.csv").write_text("h\n")
            p = A.input_paths(root / "a0", root / "r3", root / "r4", root / "dg", root / "g.csv", root / "plans",
                              root / "h.md", "phase4")
        self.assertEqual(sorted(p["plan"]), [d.isoformat() for d in S.phase_sessions("phase4")])
        self.assertIn("Phase4_registration.md", A.AMENDMENT["phase4"])
        with self.assertRaises(RuntimeError):
            A.run("phase5", *(Path("x"),) * 8)


def keys(strategy, days, per_day=1):
    return [dict(strategy=strategy, trade_id=f"{strategy}-{d}-{i}", date=d, entry_time=f"09:{i:02d}:00.000")
            for d in days for i in range(per_day)]


class TestG4Phase4(unittest.TestCase):
    DAYS = [d.isoformat() for d in S.phase_sessions("phase4")]

    def test_fixed_days(self):
        fx = G.PHASES["phase4"]["fixed_days"]
        self.assertEqual(fx, ("2026-02-11", "2026-03-04", "2026-03-17", "2026-04-09"))
        self.assertTrue(set(fx) <= set(self.DAYS))
        self.assertEqual(G.PHASES["phase3"]["fixed_days"], ("2025-12-10", "2025-12-18", "2026-01-14", "2026-01-29"))
        self.assertEqual(G.PHASES["phase2"]["fixed_days"], G.FIXED_DAYS)

    def test_draw(self):
        r4, r1 = keys("R4_M0", self.DAYS), keys("R1_A0", self.DAYS, 2)
        fx = G.PHASES["phase4"]["fixed_days"]
        rows = G.draw(r1, [], [], r4, fixed_days=fx)
        d4 = [r for r in rows if r["draw"] == "DRAW_R4"]
        self.assertEqual(len([r for r in rows if r["draw"] == "FIXED_DAY"]), 4)
        self.assertEqual(len(d4), 10); self.assertEqual(d4[0]["pool_size"], 48)
        self.assertFalse({r["date"] for r in d4} & set(fx))

    def test_cli_and_range(self):
        with tempfile.TemporaryDirectory() as td:
            led = {}
            for s, name in (("r1", "R1_A0"), ("r2", "R2_C1"), ("r3", "R3_M0"), ("r4", "R4_M0")):
                p = Path(td) / f"{s}.csv"
                with open(p, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(G.KEYS)); w.writeheader(); w.writerows(keys(name, self.DAYS))
                led[s] = p
            out = Path(td) / "sample.csv"
            args = sum(([f"--{s}", str(p)] for s, p in led.items()), []) + ["--out", str(out), "--phase", "phase4"]
            self.assertEqual(G.main(args), 0)
            man = json.loads(Path(str(out) + ".manifest.json").read_text())
            with self.assertRaises(SystemExit):
                G.read_keys(led["r4"], "R4", "phase3")
        self.assertEqual(man["counts"], {"FIXED_DAY": 4, "DRAW_R4": 10, "DRAW_R1R3": 10})


if __name__ == "__main__":
    unittest.main()
