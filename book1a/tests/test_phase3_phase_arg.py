"""Phase 3 Step A6: phase2_report / phase2_review_fields / phase2_review_apply / g4_draw generalized only by a phase
argument (Nov 8, 2026). Synthetic inputs only; phase2 behaviour is covered unchanged by the Phase 2 tests."""
import csv
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from book1a import g4_draw as G, phase2_report as RP, phase2_review_apply as A, phase2_review_fields as F, sessions as S

P3_EXPOSED = {dt.date(2026, 1, 12), dt.date(2026, 1, 14), dt.date(2026, 1, 16)}


class TestPopulations(unittest.TestCase):
    def test_phase3_populations(self):
        sess = S.phase_sessions("phase3")
        self.assertEqual(len(sess), 41)
        pops = RP.populations(sess, "phase3")
        self.assertEqual(len(pops["ALL"]), 41)
        self.assertEqual(len(pops["UNEXPOSED"]), 38)
        self.assertEqual(set(pops["ALL"]) - set(pops["UNEXPOSED"]), P3_EXPOSED)

    def test_phase2_default_unchanged(self):
        sess = S.phase_sessions("phase2")
        self.assertEqual(RP.populations(sess), RP.populations(sess, "phase2"))
        self.assertEqual(len(RP.populations(sess)["UNEXPOSED"]), 13)
        self.assertIs(RP.EXPOSED_BY_PHASE["phase2"], RP.EXPOSED)

    def test_phase2_exposure_not_used_in_phase3(self):
        pops = RP.populations(S.phase_sessions("phase3"), "phase3")
        self.assertFalse(set(pops["ALL"]) & RP.EXPOSED)

    def test_report_run_refuses_other_phases(self):
        for ph in ("phase1", "phase5", "Phase3", ""):
            with self.assertRaises(RuntimeError):
                RP.run(ph, {}, {}, {}, "x", "y")

    def test_report_run_phase3_writes_card(self):
        with tempfile.TemporaryDirectory() as td:
            gex = Path(td) / "gex.csv"
            with open(gex, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["session", "ok", "regime"])
                for d in S.phase_sessions("phase3"):
                    w.writerow([d.isoformat(), "True", "positive"])
            res = RP.run("phase3", {}, {}, {}, str(gex), str(Path(td) / "card.json"))
        self.assertEqual(res["phase"], "phase3")
        self.assertEqual(len(res["populations"]["ALL"]), 41)
        self.assertEqual(len(res["populations"]["UNEXPOSED"]), 38)


class TestReviewFields(unittest.TestCase):
    def test_phase3_allowed(self):
        self.assertEqual(F.compute("phase3", [], None, None), [])
        self.assertEqual(F.compute("phase2", [], None, None), [])

    def test_others_refused(self):
        for ph in ("phase1", "phase5", "PHASE3"):
            with self.assertRaises(RuntimeError):
                F.compute(ph, [], None, None)


class TestReviewApply(unittest.TestCase):
    def test_refuses_phase5(self):
        with self.assertRaises(RuntimeError):
            A.run("phase5", *(Path("x"),) * 8)

    def test_phase3_plan_paths_are_the_41_sessions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for run in ("a0", "r4"):
                (root / run / "strategy").mkdir(parents=True)
                (root / run / "strategy" / "JOFS_x.csv").write_text("h\n")
            p = A.input_paths(root / "a0", root / "r3", root / "r4", root / "dg", root / "g.csv", root / "plans",
                              root / "h.md", "phase3")
            p2 = A.input_paths(root / "a0", root / "r3", root / "r4", root / "dg", root / "g.csv", root / "plans", root / "h.md")
        self.assertEqual(sorted(p["plan"]), [d.isoformat() for d in S.phase_sessions("phase3")])
        self.assertEqual(sorted(p2["plan"]), [d.isoformat() for d in S.phase_sessions("phase2")])

    def test_amendment_text_per_phase(self):
        self.assertIn("e1d37a1", A.AMENDMENT["phase2"])
        self.assertIn("Phase3_registration.md", A.AMENDMENT["phase3"])


def keys(strategy, days, per_day=1):
    return [dict(strategy=strategy, trade_id=f"{strategy}-{d}-{i}", date=d, entry_time=f"09:{i:02d}:00.000")
            for d in days for i in range(per_day)]


class TestG4Phase3(unittest.TestCase):
    DAYS = [d.isoformat() for d in S.phase_sessions("phase3")]

    def test_fixed_days_registered(self):
        fx = G.PHASES["phase3"]["fixed_days"]
        self.assertEqual(fx, ("2025-12-10", "2025-12-18", "2026-01-14", "2026-01-29"))
        self.assertTrue(set(fx) <= set(self.DAYS))
        self.assertEqual(G.PHASES["phase2"]["fixed_days"], G.FIXED_DAYS)

    def test_phase3_draw(self):
        r4 = keys("R4_M0", self.DAYS)
        r1 = keys("R1_A0", self.DAYS, 2)
        rows = G.draw(r1, [], [], r4, fixed_days=G.PHASES["phase3"]["fixed_days"])
        fixed = [r for r in rows if r["draw"] == "FIXED_DAY"]
        self.assertEqual(sorted(r["date"] for r in fixed), list(G.PHASES["phase3"]["fixed_days"]))
        d4 = [r for r in rows if r["draw"] == "DRAW_R4"]
        self.assertEqual(len(d4), 10); self.assertEqual(d4[0]["pool_size"], 37)
        self.assertFalse({r["date"] for r in d4} & set(G.PHASES["phase3"]["fixed_days"]))
        self.assertEqual(len([r for r in rows if r["draw"] == "DRAW_R1R3"]), 10)
        self.assertEqual(rows, G.draw(r1, [], [], r4, fixed_days=G.PHASES["phase3"]["fixed_days"]))   # same seed

    def test_phase2_draw_default_unchanged(self):
        d2 = [d.isoformat() for d in S.phase_sessions("phase2")]
        r4, r1 = keys("R4_M0", d2), keys("R1_A0", d2)
        self.assertEqual(G.draw(r1, [], [], r4), G.draw(r1, [], [], r4, fixed_days=G.FIXED_DAYS))

    def test_date_range_per_phase(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "l.csv"
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(G.KEYS)); w.writeheader()
                w.writerow(dict(strategy="R4_M0", trade_id="E-1", date="2025-11-12", entry_time="09:00:00.000"))
            self.assertEqual(len(G.read_keys(p, "R4")), 1)
            with self.assertRaises(SystemExit):
                G.read_keys(p, "R4", "phase3")

    def test_cli_phase3(self):
        with tempfile.TemporaryDirectory() as td:
            led = {}
            for s, name in (("r1", "R1_A0"), ("r2", "R2_C1"), ("r3", "R3_M0"), ("r4", "R4_M0")):
                p = Path(td) / f"{s}.csv"
                with open(p, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(G.KEYS)); w.writeheader(); w.writerows(keys(name, self.DAYS))
                led[s] = p
            out = Path(td) / "sample.csv"
            args = sum(([f"--{s}", str(p)] for s, p in led.items()), []) + ["--out", str(out), "--phase", "phase3"]
            self.assertEqual(G.main(args), 0)
            import json
            man = json.loads(Path(str(out) + ".manifest.json").read_text())
        self.assertEqual(man["phase"], "phase3"); self.assertEqual(man["counts"], {"FIXED_DAY": 4, "DRAW_R4": 10, "DRAW_R1R3": 10})


if __name__ == "__main__":
    unittest.main()
