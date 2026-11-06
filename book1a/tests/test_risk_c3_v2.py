"""risk-c3-v2 (Phase1/risk-c3-v2_registration.md): reference = best ask / bid at the decision; entry risk at fill;
execution breach logged only. Synthetic logs and tapes only."""
import csv
import gzip
import tempfile
import unittest
from pathlib import Path

from book1a import ledger as L, replay_risk as RR, risk as RK
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import arm_replay as AR, fills

COLS = ["RecordType", "EventId", "EvidenceTimeCT", "Direction", "SetupFamily", "CandidateStatus", "ShadowOf", "Grade",
        "LocationType", "LocationId", "ZoneLo", "ZoneHi", "EntryRef", "StopAnchor", "TargetPrice", "RewardRisk", "Reasons", "Detail", "State"]
DAY = "2025-10-22"


def cand(eid, hhmm, direction, entry_ref, stop, target):
    r = {c: "" for c in COLS}
    lo, hi = sorted((stop, entry_ref))
    r.update(RecordType="CANDIDATE", EventId=eid, EvidenceTimeCT=f"{DAY} {hhmm}:00.000", Direction=direction,
             SetupFamily="RESPONSE", CandidateStatus="Qualified", Grade="B+", LocationType="FROZEN_PREOPEN", LocationId="Z",
             ZoneLo=f"{lo:.2f}", ZoneHi=f"{hi:.2f}", EntryRef=f"{entry_ref:.2f}", StopAnchor=f"{stop:.2f}",
             TargetPrice=f"{target:.2f}", RewardRisk="2")
    return r


def make_run(d, cands, ticks):
    """ticks: (hh:mm:ss[.f], price, bid, ask)."""
    run = Path(d) / "run"; (run / "strategy").mkdir(parents=True); (run / "plans").mkdir()
    with open(run / "strategy" / "JOFS_t.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(cands)
    (run / "plans" / f"PreopenPlan_{DAY}.txt").write_text(f"date={DAY}\ncontext=Bullish\nreview=APPROVED\nend=1\n")
    tape = Path(d) / "tape.csv.gz"
    with gzip.open(tape, "wt") as f:
        f.write("time_local,price,bid,ask,volume,aggressor\n")
        for t, p, b, a in sorted(ticks):
            base, _, frac = t.partition(".")
            f.write(f"{DAY} {base}.{frac.ljust(7, '0')},{p:.2f},{b:.2f},{a:.2f},5,B\n")
    return AR.Log(run), fills.Tape(tape)


def run(cands, ticks, impl=RK.C3_V2, fill="v3.5"):
    with tempfile.TemporaryDirectory() as d:
        log, tape = make_run(d, cands, ticks)
        return RR.replay(log, tape, "R4", fill=fill, risk_impl=impl)


def att(rep, eid):
    return [a for a in rep["attempts"] if a["event"] == eid][0]


class TestPureFunctions(unittest.TestCase):
    def test_entry_risk_at_fill_integer_ticks_and_cents(self):
        self.assertEqual(RK.entry_risk_at_fill_cents(24000.75, 23951.50, 1), (197, 199 * 500 + 574))
        self.assertEqual(RK.entry_risk_at_fill_cents(23999.50, 24024.00, 2), (98, 100 * 500 * 2 + 574 * 2))
        with self.assertRaises(ValueError):
            RK.entry_risk_at_fill_cents(24000.10, 23951.50, 1)          # off the tick grid

    def test_exact_budget_boundary(self):
        self.assertFalse(RK.is_execution_breach(100_000, 100_000))       # $1,000.00 fits
        self.assertTrue(RK.is_execution_breach(100_001, 100_000))        # $1,000.01 does not
        self.assertFalse(RK.is_execution_breach(31_574, 31_574))         # remaining daily budget, exact
        self.assertTrue(RK.is_execution_breach(31_575, 31_574))

    def test_n_1_2_3_5_10_and_adverse_fills(self):
        for n, s in ((1, 196), (2, 96), (3, 63), (5, 36), (10, 16)):
            dec = RK.DayRiskState().pre_trade_check(s)
            self.assertEqual((dec.reason, dec.contracts), ("ACCEPT", n), (n, s))
            self.assertEqual(dec.budget_cents, 100_000)
            self.assertLessEqual(dec.estimated_risk_cents, 100_000)
            if n < 10:
                self.assertEqual(RK.DayRiskState().pre_trade_check(s + 1).contracts, n - 1 if n == 1 else
                                 RK.size_for(s + 1, 100_000))
            # 0-tick variance fits; 1 and 2 ticks adverse at the largest stop that fits breach the $1,000 budget
            for adverse, breach in ((0, False), (1, True), (2, True)):
                _, cents = RK.entry_risk_at_fill_cents(24000.0 + adverse * 0.25, 24000.0 - s * 0.25, n)
                self.assertEqual(RK.is_execution_breach(cents, dec.budget_cents), breach, (n, s, adverse))

    def test_daily_budget_below_1000_exact(self):
        st = RK.DayRiskState(); st.realized_losses_cents = 200_000 - 31_574; st.consecutive_losses = 1
        dec = st.pre_trade_check(60)                                     # 1 NQ, 60 ticks = $315.74
        self.assertEqual((dec.reason, dec.contracts, dec.budget_cents, dec.estimated_risk_cents), ("ACCEPT", 1, 31_574, 31_574))
        st.realized_losses_cents += 1
        self.assertEqual(st.pre_trade_check(60).reason, "RISK_REJECT:DAILY_BUDGET")

    def test_one_position_reserve_not_double_counted(self):
        st = RK.DayRiskState()
        dec = st.pre_trade_check(60)
        self.assertEqual(dec.budget_cents, 100_000)                      # read before the trade's own reserve
        st.on_entry(dec)
        self.assertEqual(st.remaining_daily_cents(), 200_000 - dec.estimated_risk_cents)
        self.assertEqual(st.pre_trade_check(10).reason, "RISK_REJECT:IN_POSITION")
        st.on_exit(-50_000, "E")
        self.assertEqual(st.remaining_daily_cents(), 150_000)            # reserve released, loss counted once


class TestReplayV2(unittest.TestCase):
    def long_case(self):
        # EntryRef 24000.00; best ask at the 09:03:00 decision 24000.50; stop 196 ticks below the ask; fill 250 ms
        # later at 24000.75 (1 tick adverse); later the stop trades.
        c = [cand("E-1", "09:03", "Long", 24000.00, 23951.50, 24100.00)]
        t = [("09:00:00", 24000.0, 23999.75, 24000.0), ("09:02:59.9", 24000.25, 24000.25, 24000.50),
             ("09:03:00.1", 24000.50, 24000.50, 24000.75), ("09:30:00", 23951.50, 23951.25, 23951.50),
             ("14:55:00", 24000.0, 23999.75, 24000.0)]
        return c, t

    def test_long_1_tick_adverse_breach_logged_no_exit_no_resize(self):
        c, t = self.long_case()
        rep = run(c, t)
        a = att(rep, "E-1")
        self.assertEqual((a["risk_impl_version"], a["risk_ref_source"], a["risk_entry_ref"], a["signal_entry_ref"]),
                         ("risk-c3-v2", "BEST_ASK", 24000.50, 24000.00))
        self.assertEqual((a["risk_stop_ticks"], a["risk_contracts"], a["risk_estimate_usd"]), (196, 1, 995.74))
        self.assertEqual(len(rep["trades"]), 1)
        tr = rep["trades"][0]
        self.assertEqual((tr.qty, tr.entry_price, tr.exit_reason, tr.exit_price), (1, 24000.75, "STOP_FIRST", 23951.25))
        x = tr.extra
        self.assertEqual((x["entry_risk_ticks_at_fill"], x["entry_risk_at_fill_usd"], x["risk_budget_usd"],
                          x["execution_variance_ticks"], x["exec_risk_breach"]), (197, 1000.74, 1000.0, 1, 1))
        ev = [e for e in rep["risk_events"] if e["event"] == "EXEC_RISK_BREACH"]
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["entry_risk_at_fill_cents"], ev[0]["budget_cents"], ev[0]["overrun_cents"]), (100_074, 100_000, 74))
        # no exit and no resize: the same trade as v1 (v1 sizes from EntryRef, 194 ticks -> also 1 NQ)
        v1 = run(c, t, impl=RK.C3_V1)
        self.assertEqual(att(v1, "E-1")["risk_stop_ticks"], 194)
        t1 = v1["trades"][0]
        self.assertEqual((t1.qty, t1.entry_price, t1.exit_time, t1.exit_price, t1.exit_reason),
                         (tr.qty, tr.entry_price, tr.exit_time, tr.exit_price, tr.exit_reason))

    def test_short_2_tick_adverse_breach(self):
        # best bid at the decision 24000.00; stop 96 ticks above -> 2 NQ; fill at 23999.50 (2 ticks adverse)
        c = [cand("S-1", "10:03", "Short", 24000.25, 24024.00, 23900.00)]
        t = [("10:02:59.9", 24000.00, 24000.00, 24000.25), ("10:03:00.1", 23999.75, 23999.50, 23999.75),
             ("10:40:00", 23899.75, 23899.75, 23900.00), ("14:55:00", 23950.0, 23949.75, 23950.0)]
        rep = run(c, t)
        a = att(rep, "S-1")
        self.assertEqual((a["risk_ref_source"], a["risk_entry_ref"], a["risk_stop_ticks"], a["risk_contracts"]), ("BEST_BID", 24000.0, 96, 2))
        tr = rep["trades"][0]
        self.assertEqual((tr.side, tr.qty, tr.entry_price, tr.exit_reason), ("SHORT", 2, 23999.50, "TARGET_FIRST"))
        x = tr.extra
        self.assertEqual((x["entry_risk_ticks_at_fill"], x["entry_risk_at_fill_usd"], x["execution_variance_ticks"], x["exec_risk_breach"]),
                         (98, 1011.48, 2, 1))

    def test_1_tick_adverse_with_room_is_not_a_breach(self):
        c = [cand("E-3", "09:03", "Long", 24000.00, 23985.00, 24040.00)]      # 60 ticks -> 3 NQ, $947.22
        t = [("09:02:59.9", 24000.0, 23999.75, 24000.0), ("09:03:00.1", 24000.25, 24000.0, 24000.25),
             ("09:20:00", 24041.0, 24040.75, 24041.0), ("14:55:00", 24000.0, 23999.75, 24000.0)]
        tr = run(c, t)["trades"][0]
        self.assertEqual((tr.qty, tr.planned_risk_usd), (3, 947.22))
        self.assertEqual((tr.extra["entry_risk_at_fill_usd"], tr.extra["exec_risk_breach"], tr.extra["execution_variance_ticks"]),
                         (962.22, 0, 1))

    def test_remaining_daily_below_1000_and_one_position(self):
        # E-1: 1 NQ, 196 ticks, fill = ask (0 variance), stop gaps 40 ticks -> realized loss $1,190.74 (gap fill
        # 23940.75). E-7 arrives while E-1 is open -> ALREADY_IN_TRADE, nothing reserved. E-2: budget
        # min($1,000, $2,000 - $1,190.74) = $809.26, read once (no reserve of its own subtracted); 77 ticks -> 2 NQ
        # ($801.48); fill 1 tick adverse -> $811.48 > $809.26 -> breach (below $1,000).
        c = [cand("E-1", "09:03", "Long", 24000.00, 23951.00, 24100.00),
             cand("E-7", "09:10", "Long", 24000.00, 23990.00, 24100.00),
             cand("E-2", "11:03", "Long", 24000.00, 23980.75, 24100.00)]
        t = [("09:02:59.9", 24000.0, 23999.75, 24000.0), ("09:03:00.1", 24000.0, 23999.75, 24000.0),
             ("09:10:00.1", 24000.0, 23999.75, 24000.0), ("09:30:00", 23941.0, 23940.75, 23941.0),
             ("11:02:59.9", 24000.0, 23999.75, 24000.0), ("11:03:00.1", 24000.0, 24000.0, 24000.25),
             ("11:30:00", 24101.0, 24100.75, 24101.0), ("14:55:00", 24000.0, 23999.75, 24000.0)]
        rep = run(c, t)
        self.assertEqual(att(rep, "E-7")["reasons"], "ALREADY_IN_TRADE")
        self.assertNotIn("risk_contracts", att(rep, "E-7"))
        self.assertEqual(len(rep["trades"]), 2)
        t1, t2 = rep["trades"]
        self.assertEqual((t1.exit_price, t1.extra["exec_risk_breach"]), (23940.75, 0))
        a2 = att(rep, "E-2")
        self.assertEqual((a2["risk_remaining_daily_usd"], a2["risk_budget_usd"], a2["risk_stop_ticks"], a2["risk_contracts"]),
                         (809.26, 809.26, 77, 2))
        self.assertEqual((t2.qty, t2.extra["risk_budget_usd"], t2.extra["entry_risk_at_fill_usd"], t2.extra["exec_risk_breach"]),
                         (2, 809.26, 811.48, 1))

    def test_no_quote_and_ref_past_stop_guards(self):
        c = [cand("E-5", "09:03", "Long", 24000.00, 23990.00, 24100.00)]
        t = [("09:02:59.9", 24000.0, 0.0, 0.0), ("09:03:00.1", 24000.0, 23999.75, 24000.0), ("14:55:00", 24000.0, 23999.75, 24000.0)]
        self.assertEqual(att(run(c, t), "E-5")["reasons"], "RISK_REJECT:NO_QUOTE")
        t = [("09:02:59.9", 23990.0, 23989.75, 23990.0), ("09:03:00.1", 24000.0, 23999.75, 24000.0), ("14:55:00", 24000.0, 23999.75, 24000.0)]
        self.assertEqual(att(run(c, t), "E-5")["reasons"], "RISK_REJECT:REF_AT_OR_PAST_STOP")

    def test_v1_ledger_layout_unchanged_and_v2_columns(self):
        c, t = self.long_case()
        with tempfile.TemporaryDirectory() as d:
            for impl, cols in ((RK.C3_V1, []), (RK.C3_V2, RR.V2_LEDGER_COLUMNS)):
                rep = run(c, t, impl=impl)
                p = Path(d) / f"{impl}.csv"
                L.write_ledger(str(p), rep["trades"], extra_columns=cols)
                with open(p, newline="") as f:
                    rows = list(csv.DictReader(f))
                self.assertEqual(list(rows[0].keys()), L.LEDGER_COLUMNS + cols)
                if impl == RK.C3_V1:
                    self.assertEqual(rep["trades"][0].extra, {})
                else:
                    self.assertEqual(rows[0]["risk_impl_version"], "risk-c3-v2")

    def test_unknown_impl_rejected(self):
        with self.assertRaises(ValueError):
            run(*self.long_case(), impl="risk-c3-v9")


class TestGuards(unittest.TestCase):
    """RISK_REJECT:NO_QUOTE and RISK_REJECT:REF_AT_OR_PAST_STOP (approved with risk-c3-v2, Kyron Nov 6, 2026)."""

    def test_valid_quote_rule(self):
        self.assertTrue(RR.valid_quote(24000.0, 24000.25))
        for b, a in ((0.0, 24000.25), (24000.0, 0.0), (0.0, 0.0), (24000.25, 24000.0),      # zero, crossed
                     (24000.0, 24000.0), (float("nan"), float("nan")), (None, 24000.0), (-1.0, 24000.0)):   # locked, missing
            self.assertFalse(RR.valid_quote(b, a), (b, a))

    def test_ref_past_stop_direction_aware(self):
        self.assertTrue(RR.ref_at_or_past_stop(+1, 23990.00, 23990.00))       # long: ask = stop
        self.assertTrue(RR.ref_at_or_past_stop(+1, 23989.75, 23990.00))       # long: ask below stop
        self.assertFalse(RR.ref_at_or_past_stop(+1, 23990.25, 23990.00))
        self.assertTrue(RR.ref_at_or_past_stop(-1, 24010.00, 24010.00))       # short: bid = stop
        self.assertTrue(RR.ref_at_or_past_stop(-1, 24010.25, 24010.00))       # short: bid above stop
        self.assertFalse(RR.ref_at_or_past_stop(-1, 24009.75, 24010.00))

    def _one(self, direction, stop, quote, entry_ref=24000.00, target=None):
        target = target if target is not None else (24100.00 if direction == "Long" else 23900.00)
        c = [cand("G-1", "09:03", direction, entry_ref, stop, target)]
        t = ([("09:02:59.9",) + quote] if quote else []) + [("09:03:00.1", 24000.0, 23999.75, 24000.0), ("14:55:00", 24000.0, 23999.75, 24000.0)]
        return att(run(c, t), "G-1")

    def test_long_equality_at_stop_and_one_tick_inside(self):
        self.assertEqual(self._one("Long", 23990.00, (23990.0, 23989.75, 23990.00))["reasons"], "RISK_REJECT:REF_AT_OR_PAST_STOP")
        a = self._one("Long", 23990.00, (23990.25, 23990.00, 23990.25))
        self.assertEqual((a["reasons"], a["risk_stop_ticks"]), ("", 1))

    def test_short_equality_at_stop_and_one_tick_inside(self):
        self.assertEqual(self._one("Short", 24010.00, (24010.0, 24010.00, 24010.25))["reasons"], "RISK_REJECT:REF_AT_OR_PAST_STOP")
        a = self._one("Short", 24010.00, (24009.75, 24009.75, 24010.00))
        self.assertEqual((a["reasons"], a["risk_ref_source"], a["risk_stop_ticks"]), ("", "BEST_BID", 1))

    def test_missing_quote(self):
        for d, stop in (("Long", 23990.00), ("Short", 24010.00)):
            self.assertEqual(self._one(d, stop, None)["reasons"], "RISK_REJECT:NO_QUOTE")         # no trade before the decision

    def test_invalid_quote_crossed_locked_or_zero(self):
        for d, stop in (("Long", 23990.00), ("Short", 24010.00)):
            for q in ((24000.0, 24000.25, 24000.00), (24000.0, 24000.0, 24000.0), (24000.0, 0.0, 24000.25), (24000.0, 24000.0, 0.0)):
                self.assertEqual(self._one(d, stop, q)["reasons"], "RISK_REJECT:NO_QUOTE", (d, q))


if __name__ == "__main__":
    unittest.main()
