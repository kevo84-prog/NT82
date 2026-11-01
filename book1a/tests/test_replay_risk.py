"""R3/R4 replay wrapper on a synthetic A0 log and tape: sizing, RISK_REJECT, daily limit, ledger fields."""
import csv
import gzip
import tempfile
import unittest
from pathlib import Path

from book1a import replay_risk as RR
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import arm_replay as AR, fills

COLS = ["RecordType", "EventId", "EvidenceTimeCT", "Direction", "SetupFamily", "CandidateStatus", "ShadowOf", "Grade",
        "LocationType", "LocationId", "ZoneLo", "ZoneHi", "EntryRef", "StopAnchor", "TargetPrice", "RewardRisk", "Reasons", "Detail", "State"]


def row(**kw):
    r = {c: "" for c in COLS}; r.update(kw); return r


def make_run(d, cands, ticks):
    run = Path(d) / "run"; (run / "strategy").mkdir(parents=True); (run / "plans").mkdir()
    with open(run / "strategy" / "JOFS_t.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(cands)
    (run / "plans" / "PreopenPlan_2025-10-22.txt").write_text("date=2025-10-22\ncontext=Bullish\nreview=APPROVED\nend=1\n")
    tape = Path(d) / "tape.csv.gz"
    with gzip.open(tape, "wt") as f:
        f.write("time_local,price,bid,ask,volume,aggressor\n")
        for t, p in ticks:
            base, _, frac = t.partition(".")
            f.write(f"2025-10-22 {base}.{frac.ljust(7, '0')},{p:.2f},{p - 0.25:.2f},{p:.2f},5,B\n")
    return run, tape


class TestReplayRisk(unittest.TestCase):
    def test_sizing_reject_and_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            cands = [
                row(RecordType="CANDIDATE", EventId="E-1", EvidenceTimeCT="2025-10-22 09:03:00.000", Direction="Long", SetupFamily="RESPONSE",
                    CandidateStatus="Qualified", Grade="B+", LocationType="FROZEN_PREOPEN", LocationId="Z1", ZoneLo="23985", ZoneHi="23995",
                    EntryRef="24000.00", StopAnchor="23985.00", TargetPrice="24040.00", RewardRisk="2.67"),       # 60-tick stop -> 3 NQ
                row(RecordType="CANDIDATE", EventId="E-2", EvidenceTimeCT="2025-10-22 10:03:00.000", Direction="Long", SetupFamily="RESPONSE",
                    CandidateStatus="Qualified", Grade="B+", LocationType="FROZEN_PREOPEN", LocationId="Z2", ZoneLo="23900", ZoneHi="23950",
                    EntryRef="24000.00", StopAnchor="23950.00", TargetPrice="24300.00", RewardRisk="6.0"),        # 200-tick stop -> RISK_REJECT
            ]
            ticks = [("09:00:00", 24000.0), ("09:03:00.100", 24000.0), ("09:20:00", 23985.0),       # E-1 stopped: 1 tick adverse
                     ("10:03:00.100", 24000.0), ("10:30:00", 24000.0), ("14:55:00", 24000.0)]
            run, tape = make_run(d, cands, ticks)
            log = AR.Log(run); tp = fills.Tape(tape)
            rep = RR.replay(log, tp, "R4", fill="v3.4")
            self.assertEqual(len(rep["trades"]), 1)
            tr = rep["trades"][0]
            self.assertEqual(tr.qty, 3)
            self.assertEqual(tr.risk_decision, "ACCEPT")
            self.assertAlmostEqual(tr.planned_risk_usd, 947.22)
            self.assertEqual(tr.exit_reason, "STOP_FIRST")
            self.assertEqual(tr.exit_price, 23984.75)
            self.assertAlmostEqual(tr.theoretical_R, -61 / 60)
            self.assertAlmostEqual(tr.realized_net_R, (-61 * 5 * 3 - 17.22) / (60 * 5 * 3))
            self.assertFalse(tr.risk_breach_fill)                     # $932.22 loss within the $947.22 plan
            a2 = [a for a in rep["attempts"] if a["event"] == "E-2"][0]
            self.assertEqual(a2["reasons"], "RISK_REJECT:PER_TRADE_BUDGET")
            self.assertEqual(a2["risk_contracts"], 0)

    def test_two_loss_halt_and_daily_budget(self):
        with tempfile.TemporaryDirectory() as d:
            cands = []
            ticks = []
            for k, hh in enumerate(("09:03", "10:03", "11:03")):
                cands.append(row(RecordType="CANDIDATE", EventId=f"E-{k}", EvidenceTimeCT=f"2025-10-22 {hh}:00.000", Direction="Long",
                                 SetupFamily="RESPONSE", CandidateStatus="Qualified", Grade="B+", LocationType="FROZEN_PREOPEN", LocationId="Z",
                                 ZoneLo="23985", ZoneHi="23995", EntryRef="24000.00", StopAnchor="23951.00", TargetPrice="24100.00", RewardRisk="2"))  # 196 ticks -> 1 NQ
                ticks += [(f"{hh}:00.100", 24000.0), (f"{hh[:2]}:20:00", 23951.0)]
            ticks.append(("14:55:00", 24000.0))
            run, tape = make_run(d, cands, ticks)
            rep = RR.replay(AR.Log(run), fills.Tape(tape), "R3", fill="v3.4")
            self.assertEqual(len(rep["trades"]), 2)                    # third blocked by the 2-loss halt
            a3 = [a for a in rep["attempts"] if a["event"] == "E-2"][0]
            self.assertEqual(a3["reasons"], "HALT:LOSS_HALT")
            self.assertAlmostEqual(a3["risk_remaining_daily_usd"], 2000 - 2 * (197 * 5 + 5.74), places=2)


if __name__ == "__main__":
    unittest.main()
