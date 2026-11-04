"""R4 reads the Book 1A plan for every day and stops with an error when it is missing; never an A0 fallback (E17)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from book1a import run_r4 as R4

V = "plan-v2.4-book1a-v1.1"


def write_b1a(d: Path, day: str, plan_id=None, header=V, sidecar=True):
    (d / f"PreopenPlan_{day}_book1a.txt").write_text(
        f"# JeronPreopenPlan v1.5 (Book 1A plan builder; book1a.plan_v24 {header})\nplan_id={plan_id or day + '-b1a'}\ndate={day}\n"
        "context=Balanced\nzone=100.00-101.00|D_PDVAH|DECISION|long=ANY|short=NONE\nzone=90.00-91.00|T_PDL|TARGET\nend=1\n", encoding="utf-8")
    if sidecar:
        (d / f"PreopenPlan_{day}_book1a.json").write_text(json.dumps(dict(
            date=day, market_context="BALANCED", zones=[dict(label="D_PDVAH", long="ANY", short="NONE", families=["AUCTION_VALUE", "GEX"])],
            targets=[dict(label="T_PDL", lo=90.0, hi=91.0)])), encoding="utf-8")


def write_a0(d: Path, day: str):
    (d / f"PreopenPlan_{day}.txt").write_text(f"plan_id={day}-v1\ndate={day}\ncontext=Bullish\nend=1\n", encoding="utf-8")


class TestR4Plans(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_loads_book1a_plan_with_version_and_sha(self):
        write_b1a(self.d, "2025-10-22")
        p = R4.load_book1a_plans(self.d, ["2025-10-22"], version=V)["2025-10-22"]
        self.assertEqual(p["plan_id"], "2025-10-22-b1a"); self.assertEqual(p["plan_version"], V)
        self.assertEqual(len(p["plan_sha256"]), 64); self.assertEqual(len(p["plan_sidecar_sha256"]), 64)

    def test_missing_plan_stops_even_with_an_a0_plan_present(self):
        write_b1a(self.d, "2025-10-22"); write_a0(self.d, "2025-10-23")
        with self.assertRaises(R4.R4PlanError) as e:
            R4.load_book1a_plans(self.d, ["2025-10-22", "2025-10-23"], version=V)
        self.assertIn("2025-10-23: Book 1A plan missing", str(e.exception))
        self.assertIn("no fallback to A0", str(e.exception))

    def test_missing_sidecar_stops(self):
        write_b1a(self.d, "2025-10-22", sidecar=False)
        with self.assertRaises(R4.R4PlanError):
            R4.load_book1a_plans(self.d, ["2025-10-22"], version=V)

    def test_a0_plan_under_the_book1a_name_stops(self):
        write_b1a(self.d, "2025-10-22", plan_id="2025-10-22-v1", header="rules_plan")
        with self.assertRaises(R4.R4PlanError) as e:
            R4.load_book1a_plans(self.d, ["2025-10-22"], version=V)
        self.assertIn("not the Book 1A plan", str(e.exception))

    def test_main_stops_before_the_harness_when_a_plan_is_missing(self):
        write_b1a(self.d, "2025-10-22")
        with mock.patch.object(R4, "run_strategy", side_effect=AssertionError("harness must not run")), \
             mock.patch.object(R4, "_plan_version", return_value=V):
            with self.assertRaises(R4.R4PlanError):
                R4.main(["--block1", str(self.d), "--a0-run", str(self.d), "--plans", str(self.d), "--out", str(self.d / "out"),
                         "--sessions", "2025-10-22", "2025-10-23"])
        self.assertFalse((self.d / "out").exists())

    def test_stage_copies_byte_for_byte(self):
        write_b1a(self.d, "2025-10-22")
        plans = R4.load_book1a_plans(self.d, ["2025-10-22"], version=V)
        pdir = R4.stage_plans(plans, self.d / "out")
        self.assertEqual((pdir / "PreopenPlan_2025-10-22.txt").read_bytes(), (self.d / "PreopenPlan_2025-10-22_book1a.txt").read_bytes())

    def test_verify_rejects_a0_plan_loaded_by_s14(self):
        write_b1a(self.d, "2025-10-22")
        plans = R4.load_book1a_plans(self.d, ["2025-10-22"], version=V)
        pdir = R4.stage_plans(plans, self.d / "out")
        good = [dict(RecordType="PLAN", Detail=f"PLAN_LOADED id=2025-10-22-b1a file={pdir / 'PreopenPlan_2025-10-22.txt'} applies_from=x", EvidenceTimeCT="")]
        R4.verify_plans_loaded(good, plans, pdir)
        bad = [dict(RecordType="PLAN", Detail=f"PLAN_LOADED id=2025-10-22-v1 file={self.d / 'PreopenPlan_2025-10-22.txt'} applies_from=x", EvidenceTimeCT="")]
        with self.assertRaises(R4.R4PlanError):
            R4.verify_plans_loaded(bad, plans, pdir)
        with self.assertRaises(R4.R4PlanError):        # no plan loaded at all
            R4.verify_plans_loaded([], plans, pdir)
        cand = dict(RecordType="CANDIDATE", EventId="E1", EvidenceTimeCT="2025-10-22 09:00:00.000",
                    LocationType="FROZEN_PREOPEN (as-of 2025-10-22 08:25 CT (plan 2025-10-22-v1))", LocationId="P_D_PDVAH_01")
        with self.assertRaises(R4.R4PlanError):
            R4.verify_plans_loaded(good + [cand], plans, pdir)

    def test_zone_fields_from_the_sidecar(self):
        write_b1a(self.d, "2025-10-22")
        p = R4.load_book1a_plans(self.d, ["2025-10-22"], version=V)["2025-10-22"]
        z = R4.zone_fields(dict(LocationType="FROZEN_PREOPEN (plan 2025-10-22-b1a)", LocationId="P_D_PDVAH_01"), p)
        self.assertEqual((z["plan_zone_class"], z["plan_zone_families"], z["plan_zone_long"], z["plan_zone_short"], z["plan_market_context"]),
                         ("DECISION", "AUCTION_VALUE,GEX", "ANY", "NONE", "BALANCED"))
        t = R4.zone_fields(dict(LocationType="FROZEN_PREOPEN (plan 2025-10-22-b1a)", LocationId="P_T_PDL_01"), p)
        self.assertEqual(t["plan_zone_class"], "TARGET")
        i = R4.zone_fields(dict(LocationType="DEVELOPING_INTRADAY_IMB_BUY", LocationId="IMB_BUY_026"), p)
        self.assertEqual(i["plan_zone_class"], "null")


if __name__ == "__main__":
    unittest.main()
