import csv
import gzip
import os
import tempfile
import unittest
from pathlib import Path

from book1a import candidate_log as CL

JOFS_COLS = ["RecordType", "EventId", "EvidenceTimeCT", "Direction", "SetupFamily", "CandidateStatus", "ShadowOf", "Grade",
             "LocationType", "LocationId", "ZoneLo", "ZoneHi", "EntryRef", "StopAnchor", "TargetPrice", "RewardRisk", "Reasons",
             "Detail", "State", "fight_flag", "trapped_passive", "delta_pct_vs_session", "ema21_aligned", "cvd_avg_aligned"]


def jofs_row(**kw):
    r = {c: "" for c in JOFS_COLS}; r.update(kw); return r


class TestCandidateLog(unittest.TestCase):
    def test_rows_and_tags_never_missing(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d) / "run"; (run / "strategy").mkdir(parents=True); (run / "plans").mkdir()
            rows = [
                jofs_row(RecordType="CANDIDATE", EventId="E-1", EvidenceTimeCT="2025-10-22 09:03:00.000", Direction="Long",
                         SetupFamily="RESPONSE", CandidateStatus="Qualified", Grade="B+", LocationType="FROZEN_PREOPEN",
                         LocationId="Z1", ZoneLo="23945.00", ZoneHi="23955.00", EntryRef="23960.00", StopAnchor="23944.50",
                         TargetPrice="24000.00", RewardRisk="2.58", Reasons="", fight_flag="N", trapped_passive="Y",
                         delta_pct_vs_session="1.4", ema21_aligned="Y", cvd_avg_aligned="N"),
                jofs_row(RecordType="SHADOW", EventId="E-2", EvidenceTimeCT="2025-10-22 09:03:00.000", Direction="Long",
                         SetupFamily="INITIATION", CandidateStatus="Rejected", ShadowOf="E-1", Grade="B",
                         LocationType="DEVELOPING_INTRADAY_IMB", LocationId="I7", ZoneLo="23930.00", ZoneHi="23940.00",
                         EntryRef="23941.00", StopAnchor="23928.00", TargetPrice="24000.00", RewardRisk="4.5",
                         Reasons="WEAK_DELTA|NO_IMBALANCE_OR_LARGE_TRADE"),
                jofs_row(RecordType="CANDIDATE", EventId="E-3", EvidenceTimeCT="2025-10-22 07:50:00.000", Direction="Short",
                         SetupFamily="RESPONSE", CandidateStatus="EventOnly", Reasons="OUTSIDE_NY_SESSION"),
            ]
            with open(run / "strategy" / "JOFS_test.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=JOFS_COLS); w.writeheader(); w.writerows(rows)
            (run / "plans" / "PreopenPlan_2025-10-22.txt").write_text(
                "date=2025-10-22\ncontext=Bullish\nzone=23945.00-23955.00|D_PDVAL|DECISION|long=ANY|short=INITIATION\n"
                "review=APPROVED\ngex_regime=POS\nend=1\n")
            tape = Path(d) / "tape.csv.gz"
            with gzip.open(tape, "wt") as f:
                f.write("time_local,price,bid,ask,volume,aggressor\n")
                for m in range(0, 30):
                    f.write(f"2025-10-22 09:{m:02d}:30.0000000,23960.00,23959.75,23960.00,5,B\n")
            out = Path(d) / "cands.csv"
            n = CL.build(run, tape, out)
            self.assertEqual(n, 2)                                  # the 07:50 candidate is outside NY
            got = list(csv.DictReader(open(out)))
            self.assertEqual(list(got[0].keys()), CL.COLUMNS)
            r1, r2 = got
            self.assertEqual(r1["gates_pass"], "1"); self.assertEqual(r2["gates_pass"], "0")
            self.assertEqual(r1["rh1_state"], "N/A_RESPONSE")
            self.assertNotEqual(r2["rh1_state"], "null")           # an INITIATION candidate gets a retest state
            self.assertEqual(r2["l1_dist_pts"], "5.0")               # 23940 to 23945
            self.assertEqual(r2["l1_veto"], "N")
            self.assertEqual(r1["fz1_would_veto_applied"], "LOGGED_ONLY")
            self.assertEqual(r1["risk_decision"], "ACCEPT")          # stop 62 ticks -> 3 NQ
            self.assertEqual(r1["risk_contracts"], "3")
            self.assertEqual(r1["risk_estimate_usd"], "977.22")
            self.assertEqual(r1["gex_regime"], "POS")
            self.assertEqual(r1["passive_trap"], "Y")
            for k in CL.BOOK1A_TAGS + CL.S14_TAGS:
                self.assertIn(k, r1); self.assertNotEqual(r1[k], "")   # present, "null" when not measurable
            self.assertEqual(r1["cvd_div"], "null")
            self.assertIn("measurable=", r1["tag_status"])


if __name__ == "__main__":
    unittest.main()
