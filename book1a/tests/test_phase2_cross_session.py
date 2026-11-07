"""Nov 28 early-close exit and the Dec 1 daily state (Phase 2 Step A follow-up, item 5); synthetic log and tape only.

Three Nov 28 trades (a win, a stop loss, then a long still open at the 12:15 half-day close, closed at a loss by the
frozen FLATTEN branch and stamped at the Nov 30 17:00 tick), then a Dec 1 candidate. Run through the frozen replays
(Book 1 arm_replay.replay for R1 / R2, replay_risk.replay for R3 / R4), unchanged. Nov 28 here has an APPROVED
synthetic plan so the replay can trade it (the real Book 1A Nov 28 plan is LOG_ONLY).
"""
import csv
import datetime as dt
import gzip
import tempfile
import unittest
from pathlib import Path

import numpy as np

from book1a import ledger as L, phase2_report as RP, phase2_review_fields as F, replay_risk as RR, risk as RK
from book1a import run_r1_r2 as R12
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import arm_replay as AR, fills

COLS = ["RecordType", "EventId", "EvidenceTimeCT", "Direction", "SetupFamily", "CandidateStatus", "ShadowOf", "Grade",
        "LocationType", "LocationId", "ZoneLo", "ZoneHi", "EntryRef", "StopAnchor", "TargetPrice", "RewardRisk", "Reasons", "Detail", "State"]
N28, N30, D01 = "2025-11-28", "2025-11-30", "2025-12-01"
CANDS = [("E-1", N28, "09:03"), ("E-2", N28, "10:03"), ("E-3", N28, "11:03"), ("E-4", D01, "09:03")]
# stop 23951 = 196 ticks below 24000 -> 1 NQ (est $995.74); target 24100 (fills on a trade at 24100.25 or above)
TICKS = [(N28, "09:02:59.000", 24000.0), (N28, "09:03:00.100", 24000.0), (N28, "09:20:00.000", 24101.0),   # A: target
         (N28, "10:02:59.000", 24000.0), (N28, "10:03:00.100", 24000.0), (N28, "10:20:00.000", 23951.0),   # B: stop
         (N28, "11:02:59.000", 24000.0), (N28, "11:03:00.100", 24000.0),
         (N28, "12:14:59.500", 23962.5),                                     # C: last Nov 28 tick (bid 23962.25)
         (N30, "17:00:00.000", 23970.0),                                     # next session open: the FLATTEN stamp
         (D01, "08:59:00.000", 24000.0), (D01, "09:03:00.100", 24000.0), (D01, "09:20:00.000", 24101.0),   # D: target
         (D01, "14:55:00.000", 24000.0)]


def row(**kw):
    r = {c: "" for c in COLS}; r.update(kw); return r


def make(d):
    run = Path(d) / "run"; (run / "strategy").mkdir(parents=True); (run / "plans").mkdir()
    with open(run / "strategy" / "JOFS_t.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for e, day, hh in CANDS:
            w.writerow(row(RecordType="CANDIDATE", EventId=e, EvidenceTimeCT=f"{day} {hh}:00.000", Direction="Long",
                           SetupFamily="RESPONSE", CandidateStatus="Qualified", Grade="B+", LocationType="FROZEN_PREOPEN",
                           LocationId="Z", ZoneLo="23985", ZoneHi="23995", EntryRef="24000.00", StopAnchor="23951.00",
                           TargetPrice="24100.00", RewardRisk="2"))
    for day in (N28, D01):
        (run / "plans" / f"PreopenPlan_{day}.txt").write_text(f"date={day}\ncontext=Bullish\nreview=APPROVED\nend=1\n")
    tape = Path(d) / "tape.csv.gz"
    with gzip.open(tape, "wt") as f:
        f.write("time_local,price,bid,ask,volume,aggressor\n")
        for day, t, p in TICKS:
            f.write(f"{day} {t}0000,{p:.2f},{p - 0.25:.2f},{p:.2f},5,B\n")
    return AR.Log(run), fills.Tape(tape)


def as_csv_rows(d, trades, name):
    p = Path(d) / name
    L.write_ledger(str(p), trades)
    return RP.read_csv(p)


class TestCrossSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        cls.log, cls.tape = make(cls.dir.name)
        cls.r3 = RR.replay(cls.log, cls.tape, "R3")                                        # risk-c3-v2, v3.5
        cls.r1 = AR.replay(cls.log, cls.tape, veto=None, exit_model="M0", fill="v3.5")
        cls.r3_rows = as_csv_rows(cls.dir.name, cls.r3["trades"], "r3.csv")
        cls.r1_rows = as_csv_rows(cls.dir.name, R12.to_trades("R1", cls.r1, "v3.5", "N/A"), "r1.csv")

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def by(self, rows):
        return {r["trade_id"]: r for r in rows}

    # ---- the Nov 28 trade as the frozen engine writes it
    def test_engine_output(self):
        for rows in (self.r3_rows, self.r1_rows):
            c = self.by(rows)["E-3"]
            self.assertEqual([r["trade_id"] for r in rows], ["E-1", "E-2", "E-3", "E-4"])
            self.assertEqual((c["date"], c["exit_reason"], c["exit_time"], float(c["exit_price"])),
                             (N28, "TIME_EXIT", "17:00:00.000", 23962.25))          # ledger session field = entry session
            self.assertEqual(float(c["net_usd"]), -151 * 5 - 5.74)                    # as produced, not corrected
            self.assertAlmostEqual(float(c["realized_net_R"]), round((-151 * 5 - 5.74) / (196 * 5), 4))

    def test_exit_time_fields(self):
        x = RP.exit_times(self.by(self.r3_rows)["E-3"], self.tape.t)
        self.assertEqual((x["entry_session"], x["exit_time_raw"], x["exit_time_model"], x["exit_flag"]),
                         (N28, f"{N30} 17:00:00", f"{N28} 12:14:59.500000", "EXIT_AFTER_SESSION_CLOSE"))
        self.assertEqual(x["holding_min_model"], round((dt.datetime(2025, 11, 28, 12, 14, 59, 500000)
                                                        - dt.datetime(2025, 11, 28, 11, 3, 0, 250000)).total_seconds() / 60, 4))
        a = RP.exit_times(self.by(self.r3_rows)["E-1"], self.tape.t)
        self.assertEqual((a["exit_flag"], a["exit_time_raw"]), ("N", f"{N28} 09:20:00"))
        bad = dict(self.by(self.r3_rows)["E-3"], exit_time="17:00:01.000")
        with self.assertRaises(ValueError):
            RP.exit_times(bad, self.tape.t)

    # ---- Dec 1 starts fresh
    def test_r3_r4_dec1_state_fresh(self):
        d = [a for a in self.r3["attempts"] if a["event"] == "E-4"][0]
        self.assertEqual((d["reasons"], d["risk_decision"], d["risk_contracts"]), ("", "ACCEPT", 1))
        self.assertEqual((d["risk_remaining_daily_usd"], d["risk_budget_usd"]), (2000.0, 1000.0))
        self.assertIn("E-4", self.by(self.r3_rows))
        # sensitivity: had the Nov 28 state carried into Dec 1, D would be refused (trade cap, then 2-loss halt / budget)
        st = RK.DayRiskState()
        for e, pnl in (("E-1", 400 * 5 * 100 - 574), ("E-2", -(197 * 5 * 100 + 574)), ("E-3", -(151 * 5 * 100 + 574))):
            st.on_entry(st.pre_trade_check(196)); st.on_exit(pnl, e)
        self.assertEqual(st.pre_trade_check(196).reason, "HALT:TRADE_CAP")
        self.assertEqual((st.consecutive_losses, st.remaining_daily_cents()), (2, 200_000 - 99_074 - 76_074))

    def test_r1_r2_dec1_state_fresh(self):
        d = [a for a in self.r1["attempts"] if a["event"] == "E-4"][0]
        self.assertEqual(d["reasons"], "")                         # no MAX_TRADES_REACHED / LOSS_STREAK_LIMIT
        self.assertIn("E-4", self.by(self.r1_rows))

    # ---- attribution
    def test_daily_table_and_drawdown_order(self):
        s = [dt.date(2025, 11, 28), dt.date(2025, 12, 1)]
        for strat, rows in (("R3", self.r3_rows), ("R1", self.r1_rows)):
            day = RP.daily_table(rows, s)
            self.assertEqual([(x["session"], x["trades"]) for x in day], [(N28, 3), (D01, 1)])
            self.assertAlmostEqual(day[0]["net_usd"], (400 * 5 - 5.74) + (-197 * 5 - 5.74) + (-151 * 5 - 5.74), places=2)
            self.assertEqual([t["trade_id"] for t in RP.in_pop(rows, s)], ["E-1", "E-2", "E-3", "E-4"])
            c = RP.report_card(strat, rows, s)
            rs = [float(r["realized_net_R"]) for r in rows]
            self.assertEqual(c["max_drawdown_R"], RP.max_drawdown(rs))
            self.assertEqual(RP.check_no_overlap(rows, lambda t: dt.datetime.fromisoformat(RP.exit_times(t, self.tape.t)["exit_time_raw"])), [])

    def test_review_window_uses_entry_session(self):
        c = self.by(self.r3_rows)["E-3"]
        x = RP.exit_times(c, self.tape.t)
        close = F.S.session_close(dt.date.fromisoformat(x["entry_session"]))
        self.assertEqual(close, dt.datetime(2025, 11, 28, 12, 15))
        m = F.mfe_mae(self.tape.t, self.tape.p, 1, dt.datetime(2025, 11, 28, 11, 3, 0, 250000), 24000.0,
                      dt.datetime.fromisoformat(x["exit_time_raw"]), 23951.0, close)
        self.assertEqual((m["mfe_mae_exit_flag"], m["mfe_mae_window_end"], m["mfe_mae_trades"]),
                         ("EXIT_AFTER_SESSION_CLOSE", close, 1))             # the 12:14:59.5 tick only; nothing after 12:15


if __name__ == "__main__":
    unittest.main()
