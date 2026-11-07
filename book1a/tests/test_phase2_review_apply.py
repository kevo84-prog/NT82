"""phase2_review_apply (post-freeze reporting implementation amendment, Nov 7, 2026): synthetic ledgers, logs, attempt
files, diagnostics files and tapes only; no Phase 1 or Phase 2 file. Expected values are hand-computed in the comments.

Trades (long, fill 24000, stop 23990 = 40 ticks = 1 R, target 24020, stop fill 23989.75, unless noted):
  E-1 R1 Nov 6 09:00  GAVE_BACK: MFE 24011 = 44 ticks = 1.1 R; then the target trades in the post-stop window
  E-3 R2 Nov 6 10:00  NO_POST_STOP_FOLLOW_THROUGH: RH1 retest entry (candidate 09:50); window complete, move 21 ticks
  E-5 R3 Nov 6 11:00  UNCLASSIFIED: no trade in the post-stop window (DATA_MISSING)
  E-6 R1 Nov 6 12:00  NOT_STOPPED (target); a SHADOW candidate row; no diag_gex_trades row (tags NA)
  E-4 R3 Nov 6 14:30  UNCLASSIFIED: window cut at 15:00 (TRUNCATED, 20 min), move 13 ticks, no target
  E-2 R4 Nov 7 14:30  STOP_THEN_TARGET in a TRUNCATED window (target trades at 14:50)
  E-7 R4 Nov 28 11:03 EXIT_AFTER_SESSION_CLOSE: stop 23951, target 24100, flattened, stamped Nov 30 17:00
Each decision bar: 30 B at 24000 (decision - 30 s) and 10 S at 23999 (at the decision): delta 20, vol 40, 50 %, 4 ticks.
"""
import csv
import datetime as dt
import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from book1a import ledger as L, phase2_review_apply as A

D1, D2, N28, N30 = "2025-11-06", "2025-11-07", "2025-11-28", "2025-11-30"
COLS = ["RecordType", "EventId", "EvidenceTimeCT", "Direction", "SetupFamily", "CandidateStatus", "ShadowOf", "Grade",
        "LocationType", "LocationId", "ZoneLo", "ZoneHi", "EntryRef", "StopAnchor", "TargetPrice", "RewardRisk", "Reasons", "Detail", "State"]
SESS = ["2025-11-05", "2025-11-06", "2025-11-07", "2025-11-10", "2025-11-11", "2025-11-12", "2025-11-13", "2025-11-14",
        "2025-11-17", "2025-11-18", "2025-11-19", "2025-11-20", "2025-11-21", "2025-11-24", "2025-11-25", "2025-11-26",
        "2025-11-28", "2025-12-01", "2025-12-02", "2025-12-03", "2025-12-04"]
PC = {d: float(i + 1) for i, d in enumerate(SESS)}
PC["2025-11-07"], PC["2025-11-18"] = 10.0, 3.0            # values still 1..21: cut-offs 7.6667 / 14.3333

# (label, event, day, decision hh:mm:ss, stop, target, exit hh:mm:ss.fff, exit price, reason)
TRADES = [("R1", "E-1", D1, "09:00:00", 23990.0, 24020.0, "09:10:00.000", 23989.75, "STOP_FIRST"),
          ("R2", "E-3", D1, "10:00:00", 23990.0, 24020.0, "10:05:00.000", 23989.75, "STOP_FIRST"),
          ("R3", "E-5", D1, "11:00:00", 23990.0, 24020.0, "11:05:00.000", 23989.75, "STOP_FIRST"),
          ("R1", "E-6", D1, "12:00:00", 23990.0, 24020.0, "12:10:00.000", 24020.0, "TARGET_FIRST"),
          ("R3", "E-4", D1, "14:30:00", 23990.0, 24020.0, "14:40:00.000", 23989.75, "STOP_FIRST"),
          ("R4", "E-2", D2, "14:30:00", 23990.0, 24020.0, "14:40:00.000", 23989.75, "STOP_FIRST"),
          ("R4", "E-7", N28, "11:03:00", 23951.0, 24100.0, "17:00:00.000", 23962.25, "TIME_EXIT")]
CAND = {"E-1": (D1, "09:00:00"), "E-3": (D1, "09:50:00"), "E-5": (D1, "11:00:00"), "E-6": (D1, "12:00:00"),
        "E-4": (D1, "14:30:00"), "E-2": (D2, "14:30:00"), "E-7": (N28, "11:03:00")}
# trade ticks after each fill (day, time, price, aggressor)
PATH = {"E-1": [("09:05:00.000", 24011.0), ("09:10:00.000", 23990.0), ("09:20:00.000", 24021.0)],
        "E-3": [("10:02:00.000", 24002.0), ("10:05:00.000", 23990.0), ("10:10:00.000", 23995.0), ("10:30:00.000", 23992.0)],
        "E-5": [("11:05:00.000", 23990.0)],
        "E-6": [("12:10:00.000", 24020.25)],
        "E-4": [("14:35:00.000", 24001.0), ("14:40:00.000", 23990.0), ("14:50:00.000", 23993.0)],
        "E-2": [("14:35:00.000", 24004.0), ("14:40:00.000", 23990.0), ("14:50:00.000", 24020.25)],
        "E-7": [("12:14:59.500", 23962.5)]}


def hms(s):
    return dt.time.fromisoformat(s)


def ticks_for_trade(ev, day, dec):
    d = dt.datetime.combine(dt.date.fromisoformat(day), hms(dec))
    out = [(d - dt.timedelta(seconds=30), 24000.0, 30, "B"), (d, 23999.0, 10, "S"),
           (d + dt.timedelta(milliseconds=250), 24000.0, 5, "B")]
    out += [(dt.datetime.combine(d.date(), hms(t)), p, 5, "B") for t, p in PATH.get(ev, [])]
    return out


def base_data():
    ticks = []
    for lab, ev, day, dec, *_ in TRADES:
        ticks += ticks_for_trade(ev, day, dec)
    ticks.append((dt.datetime(2025, 11, 30, 17, 0), 23970.0, 5, "B"))         # next session open: the FLATTEN stamp
    ledgers = {s: [] for s in A.STRATEGIES}
    for lab, ev, day, dec, stop, tgt, ex, exp, why in TRADES:
        fill_t = (dt.datetime.combine(dt.date.fromisoformat(day), hms(dec)) + dt.timedelta(milliseconds=250)).strftime("%H:%M:%S.%f")[:12]
        ledgers[lab].append(L.Trade(lab, ev, day, fill_t, "LONG", 1, 24000.0, stop, tgt, ex, exp, why,
                                    "ACCEPT" if lab in ("R3", "R4") else "N/A", None, "v3.5", 1, 250))
    att = {"R1": [], "R2": [], "R3": [], "R4": []}
    for lab, ev, day, dec, *_ in TRADES:
        cd, ct = CAND[ev]
        att[lab].append(dict(event=ev, time=f"{cd} {ct}", reasons="", px="24000.0"))
    att["R1"].append(dict(event="E-9", time=f"{D1} 09:02:00", reasons="ALREADY_IN_TRADE", px="24000.0"))
    retests = {"R2": [dict(event="E-3", time=f"{D1} 09:50:00", outcome="RETEST_ENTERED", at=f"{D1} 10:00:00")], "R3": []}
    logs = {"a0": [], "r4": []}
    for lab, ev, *_ in TRADES:
        cd, ct = CAND[ev]
        rt, sh = ("SHADOW", "E-1") if ev == "E-6" else ("CANDIDATE", "")
        logs["r4" if lab == "R4" else "a0"].append(dict(RecordType=rt, EventId=ev, ShadowOf=sh, EvidenceTimeCT=f"{cd} {ct}.000",
                                                         Direction="Long", SetupFamily="RESPONSE", CandidateStatus="Qualified"))
    return dict(ticks=ticks, ledgers=ledgers, att=att, retests=retests, logs=logs)


def base_diag(shas):
    g, e, c = [], [], []
    for lab, ev, day, dec, *_ in TRADES:
        base = dict(strategy=lab, risk_impl_version="x", ledger_sha256=shas[lab], session=day, trade_id=ev, side="LONG", qty=1,
                    decision_time=f"{day} {dec}")
        if ev != "E-6":
            g.append(dict(base, gamma_regime="positive", hvl_side="ABOVE", cr_ps_width=400.0,
                          pin_zone="N" if dec >= "13:00" else "NOT_APPLICABLE (before 13:00 CT)", pc_gamma_ratio=PC[day]))
        e.append(dict(base, mj_alignment="PLAN_ALIGNED" if ev == "E-2" else "NOT_APPLICABLE (x)"))
        c.append(dict(base, atentry_high_case_cvd17="HIGH_EXHAUSTION" if ev == "E-1" else "NONE",
                      atentry_high_with_cvd17="AGAINST" if ev == "E-1" else "",
                      **({"bs_status": "OK", "bs_vol_per_sec_60s": 12.5} if ev == "E-1" else {"bs_status": "NOT_APPLICABLE"})))
    l1 = [dict(strategy="R4", session=D2, event="E-2", is_trade="Y", decision_time=f"{D2} 14:30:00", l1_side_inherited="ALLOWED"),
          dict(strategy="R4", session=D2, event="E-99", is_trade="N", decision_time=f"{D2} 10:00:00", l1_side_inherited="NONE")]
    gs = [dict(session=d, gex_valid="Y", pc_gamma_ratio=PC[d]) for d in SESS]
    return dict(gex=g, exit=e, cvd=c, l1=l1, gex_sessions=gs)


def write_csv(p, rows, header_line=None, cols=None):
    cols = cols or list(dict.fromkeys(k for r in rows for k in r)) or ["event"]
    with open(p, "w", newline="", encoding="utf-8") as f:
        if header_line:
            f.write(header_line + "\n")
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def make(root, mut=None, mut_diag=None):
    root = Path(root)
    data = base_data()
    if mut:
        mut(data)
    a0, r3, r4, dg = (root / x for x in ("phase2", "phase2_r3", "phase2_r4", "phase2_diag"))
    for d in (a0, r3, r4, dg):
        d.mkdir(parents=True)
    for d in (a0, r4):
        (d / "strategy").mkdir()
        with gzip.open(d / "tape_strategy.csv.gz", "wt") as f:
            f.write("time_local,price,bid,ask,volume,aggressor\n")
            for t, p, v, ag in sorted(data["ticks"], key=lambda x: x[0]):
                f.write(f"{t.strftime('%Y-%m-%d %H:%M:%S.%f')}0,{p:.2f},{p - 0.25:.2f},{p:.2f},{v},{ag}\n")
    write_csv(a0 / "strategy" / "JOFS_t.csv", data["logs"]["a0"], cols=COLS)
    write_csv(r4 / "strategy" / "JOFS_t.csv", data["logs"]["r4"], cols=COLS)
    lp = dict(R1=a0 / "R1_A0_full.csv", R2=a0 / "R2_C1_full.csv", R3=r3 / "R3_M0_ledger.csv", R4=r4 / "R4_M0_ledger.csv")
    for s, p in lp.items():
        L.write_ledger(str(p), data["ledgers"][s])
    write_csv(a0 / "R1_attempts.csv", data["att"]["R1"]); write_csv(a0 / "R2_attempts.csv", data["att"]["R2"])
    write_csv(r3 / "R3_attempts.csv", data["att"]["R3"]); write_csv(r4 / "R4_attempts.csv", data["att"]["R4"])
    write_csv(a0 / "R2_retests.csv", data["retests"]["R2"]); write_csv(r3 / "R3_retests.csv", data["retests"]["R3"])
    diag = base_diag({s: sha(p) for s, p in lp.items()})
    if mut_diag:
        mut_diag(diag)
    hdr = "# synthetic diag | logged only"
    for name, fn in (("gex", "diag_gex_trades.csv"), ("exit", "diag_exit_trades.csv"), ("cvd", "diag_cvd_trades.csv"),
                     ("l1", "diag_l1_plan_side.csv"), ("gex_sessions", "diag_gex_sessions.csv")):
        write_csv(dg / fn, diag[name], header_line=hdr)
    return dict(a0=a0, r3=r3, r4=r4, diag=dg, out=root / "review")


def run(p):
    return A.run("phase2", p["a0"], p["r3"], p["r4"], p["diag"], p["out"])


class TestReviewApply(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.p = make(cls.tmp.name)
        cls.before = sorted(str(x.relative_to(cls.tmp.name)) for x in Path(cls.tmp.name).rglob("*"))
        cls.res = run(cls.p)
        cls.by = {(r["strategy"], r["trade_id"]): r for r in cls.res["rows"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # ---- every ledger trade once, counts per strategy
    def test_each_trade_once(self):
        ids = [(r["strategy"], r["trade_id"]) for r in self.res["rows"]]
        self.assertEqual(sorted(ids), sorted((lab, ev) for lab, ev, *_ in TRADES))
        self.assertEqual(self.res["manifest"]["trades_per_strategy"], {"R1": 2, "R2": 1, "R3": 2, "R4": 2})
        with open(self.p["out"] / "phase2_review.csv", newline="", encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 7)

    # ---- one stopped trade per class, and NOT_STOPPED
    def test_classes(self):
        want = {"E-1": "GAVE_BACK", "E-3": "NO_POST_STOP_FOLLOW_THROUGH", "E-5": "UNCLASSIFIED", "E-6": "NOT_STOPPED",
                "E-4": "UNCLASSIFIED", "E-2": "STOP_THEN_TARGET", "E-7": "NOT_STOPPED"}
        self.assertEqual({r["trade_id"]: r["cls"] for r in self.res["rows"]}, want)
        c = self.res["classes"]
        self.assertEqual(c["R3"]["ALL"]["counts"], dict(GAVE_BACK=0, STOP_THEN_TARGET=0, NO_POST_STOP_FOLLOW_THROUGH=0,
                                                        UNCLASSIFIED=2, NOT_STOPPED=0))
        self.assertEqual(c["R4"]["ALL"]["counts"]["STOP_THEN_TARGET"], 1)
        self.assertEqual(c["R4"]["UNEXPOSED"]["counts"]["STOP_THEN_TARGET"], 1)       # Nov 7 is unexposed

    def test_gave_back_fields(self):
        r = self.by[("R1", "E-1")]
        self.assertEqual((r["mfe_mae_trades"], r["mfe_ticks"], r["mae_ticks"], r["stop_ticks_fill"], r["mfe_R"], r["mae_R"]),
                         (3, 44.0, 40.0, 40, 1.1, 1.0))
        self.assertEqual((r["post_exit_truncated"], r["post_exit_minutes_available"], r["post_exit_move_ticks"],
                          r["post_exit_move_R"], r["post_exit_target_traded"]), ("N", 30.0, 125.0, 3.125, "Y"))
        self.assertEqual((r["confirm_bar_status"], r["confirm_delta"], r["confirm_delta_pct"], r["confirm_range_ticks"]),
                         ("OK", 20.0, 50.0, 4.0))
        self.assertEqual(r["minutes_initiation_to_entry"], 0.0042)                   # 0.25 s
        self.assertEqual((r["exit_flag"], r["exit_time_raw"]), ("N", f"{D1} 09:10:00"))

    def test_retest_and_no_follow_through(self):
        r = self.by[("R2", "E-3")]
        self.assertEqual(r["signal_time"], dt.datetime(2025, 11, 6, 9, 50))
        self.assertEqual(r["decision_time"], dt.datetime(2025, 11, 6, 10, 0))
        self.assertEqual(r["minutes_initiation_to_entry"], 10.0042)                  # 10 min 0.25 s
        self.assertEqual((r["mfe_ticks"], r["mfe_R"], r["post_exit_move_ticks"], r["post_exit_move_R"],
                          r["post_exit_target_traded"], r["post_exit_truncated"]), (8.0, 0.2, 21.0, 0.525, "N", "N"))

    def test_unclassified_no_ticks_and_truncated(self):
        r = self.by[("R3", "E-5")]
        self.assertEqual(r["post_exit_status"], "DATA_MISSING (no trade in the window)")
        r = self.by[("R3", "E-4")]
        self.assertEqual((r["post_exit_truncated"], r["post_exit_minutes_available"], r["post_exit_move_ticks"],
                          r["post_exit_move_R"], r["post_exit_target_traded"]), ("TRUNCATED", 20.0, 13.0, 0.325, "N"))
        self.assertEqual(r["post_exit_window_end"], dt.datetime(2025, 11, 6, 15, 0))

    def test_stop_then_target_truncated(self):
        r = self.by[("R4", "E-2")]
        self.assertEqual((r["mfe_R"], r["post_exit_truncated"], r["post_exit_target_traded"], r["post_exit_move_ticks"]),
                         (0.4, "TRUNCATED", "Y", 122.0))

    def test_not_stopped(self):
        r = self.by[("R1", "E-6")]
        self.assertEqual((r["post_exit_status"], r["mfe_ticks"], r["mfe_R"]), ("NOT_APPLICABLE (not a stop exit)", 81.0, 2.025))

    def test_nov28_exit_after_close(self):
        r = self.by[("R4", "E-7")]
        self.assertEqual((r["entry_session"], r["exit_time_raw"], r["exit_time_model"], r["exit_flag"]),
                         (N28, f"{N30} 17:00:00", f"{N28} 12:14:59.500000", "EXIT_AFTER_SESSION_CLOSE"))
        self.assertEqual(r["holding_min_model"], 71.9875)                            # 11:03:00.25 -> 12:14:59.5
        self.assertEqual((r["mfe_mae_exit_flag"], r["mfe_mae_window_end"], r["mfe_mae_trades"], r["mfe_ticks"],
                          r["mae_ticks"], r["stop_ticks_fill"], r["mae_R"]),
                         ("EXIT_AFTER_SESSION_CLOSE", dt.datetime(2025, 11, 28, 12, 15), 2, 0.0, 150.0, 196, 0.7653))

    # ---- tags: stable keys, missing row or field -> NA
    def test_tags_and_na(self):
        r = self.by[("R1", "E-6")]                                     # no diag_gex_trades row
        self.assertEqual((r["gamma_regime"], r["hvl_side"], r["pin_zone"], r["cr_ps_width_trade_value"]), ("NA",) * 4)
        self.assertEqual(r["mj_alignment"], "NOT_APPLICABLE (x)")
        self.assertEqual((r["atentry_high_case_cvd17"], r["atentry_high_with_cvd17"], r["post_low_case_cvd0830"]),
                         ("NONE", "NA", "NA"))                         # empty field and missing column -> NA
        self.assertEqual(self.by[("R1", "E-1")]["atentry_high_with_cvd17"], "AGAINST")
        self.assertEqual((self.by[("R1", "E-1")]["bs_vol_per_sec_60s"], r["bs_vol_per_sec_60s"]), ("12.5", "NA"))
        self.assertEqual((self.by[("R4", "E-2")]["L1_PLAN_SIDE"], self.by[("R4", "E-7")]["L1_PLAN_SIDE"], r["L1_PLAN_SIDE"]),
                         ("ALLOWED", "NA", "NA"))
        self.assertTrue(r["market_context"].startswith("NOT_RUN") and r["draw_status"].startswith("NOT_RUN"))
        self.assertTrue(r["cr_ps_width_tercile"].startswith("NOT_RUN"))
        self.assertEqual(self.res["manifest"]["missing_diag_rows"], {"R1": {"gex": 1}, "R2": {}, "R3": {}, "R4": {"l1": 1}})
        t = self.res["classes"]["R1"]["ALL"]["tags"]
        self.assertEqual(t["NOT_STOPPED"]["gamma_regime"], {"NA": 1})
        self.assertEqual(t["GAVE_BACK"]["atentry_high_case_cvd17"], {"HIGH_EXHAUSTION": 1})

    def test_terciles(self):
        c = self.res["classes"]["R4"]
        q1, q2 = c["ALL"]["tercile_cutoffs"]["pc_gamma_ratio"]
        self.assertAlmostEqual(q1, 1 + 20 / 3); self.assertAlmostEqual(q2, 1 + 40 / 3)
        self.assertEqual(c["UNEXPOSED"]["tercile_cutoffs"], c["ALL"]["tercile_cutoffs"])          # one set, both populations
        self.assertEqual((self.by[("R1", "E-1")]["pc_gamma_ratio_tercile"], self.by[("R4", "E-2")]["pc_gamma_ratio_tercile"],
                          self.by[("R4", "E-7")]["pc_gamma_ratio_tercile"]), ("T1", "T2", "T3"))   # 2, 10, 17

    # ---- overlap, inputs untouched, outputs only in --out
    def test_overlap_none(self):
        self.assertEqual(self.res["overlap"], {"R1": [], "R2": [], "R3": [], "R4": []})

    def test_inputs_unchanged_outputs_new(self):
        m = self.res["manifest"]
        self.assertEqual(m["inputs_sha256_before"], m["inputs_sha256_after"])
        self.assertEqual(len(m["inputs_sha256_before"]), 19)   # 4 ledgers, 4 attempts, 2 retests, 2 logs, 2 tapes, 5 diag
        after = sorted(str(x.relative_to(self.tmp.name)) for x in Path(self.tmp.name).rglob("*"))
        self.assertEqual(sorted(set(after) - set(self.before)),
                         sorted(["review"] + [str(Path("review") / x) for x in m["outputs"]]))
        self.assertEqual(json.loads((self.p["out"] / "phase2_review_manifest.json").read_text())["version"], A.VERSION)


class TestOverlapFlagged(unittest.TestCase):
    def test_overlap_flagged(self):
        def mut(d):
            d["ledgers"]["R1"].append(L.Trade("R1", "E-8", D1, "09:05:00.250", "LONG", 1, 24011.0, 24000.0, 24030.0,
                                              "09:08:00.000", 23999.75, "STOP_FIRST", "N/A", None, "v3.5", 1, 250))
            d["att"]["R1"].append(dict(event="E-8", time=f"{D1} 09:05:00", reasons="", px="24011.0"))
            d["logs"]["a0"].append(dict(RecordType="CANDIDATE", EventId="E-8", EvidenceTimeCT=f"{D1} 09:05:00.000"))
        with tempfile.TemporaryDirectory() as t:
            res = run(make(t, mut))
            self.assertEqual(res["overlap"]["R1"], ["E-8"])           # entered 09:05 while E-1 was open until 09:10


class TestHardErrors(unittest.TestCase):
    def check(self, mut=None, mut_diag=None, exc=A.MappingError, prep=None):
        with tempfile.TemporaryDirectory() as t:
            p = make(t, mut, mut_diag)
            if prep:
                prep(p)
            with self.assertRaises(exc):
                run(p)
            if exc is A.MappingError and not prep:
                self.assertFalse(p["out"].exists())                    # nothing written

    def test_duplicate_trade_id(self):
        self.check(lambda d: d["ledgers"]["R1"].append(d["ledgers"]["R1"][0]))

    def test_duplicate_diag_key(self):
        self.check(mut_diag=lambda g: g["gex"].append(dict(g["gex"][0])))

    def test_conflicting_diag_record(self):
        self.check(mut_diag=lambda g: g["exit"][0].update(session=D2))

    def test_diag_decision_differs(self):
        self.check(mut_diag=lambda g: g["cvd"][0].update(decision_time=f"{D1} 09:01:00"))

    def test_diag_other_ledger(self):
        self.check(mut_diag=lambda g: g["gex"][0].update(ledger_sha256="0" * 64))

    def test_diag_key_not_in_ledger(self):
        self.check(mut_diag=lambda g: g["exit"].append(dict(g["exit"][0], trade_id="E-77")))

    def test_l1_conflict(self):
        self.check(mut_diag=lambda g: g["l1"][0].update(is_trade="N"))

    def test_decision_not_in_attempts(self):
        self.check(lambda d: d["att"]["R1"].pop(0))

    def test_retest_missing(self):
        self.check(lambda d: d["retests"]["R2"].clear())

    def test_missing_candidate(self):
        self.check(lambda d: d["logs"]["a0"].__setitem__(slice(None), [r for r in d["logs"]["a0"] if r["EventId"] != "E-5"]))

    def test_conflicting_candidate_times(self):
        self.check(lambda d: d["logs"]["a0"].append(dict(RecordType="CANDIDATE", EventId="E-5", EvidenceTimeCT=f"{D1} 10:59:00.000")))

    def test_unknown_aggressor_in_confirm_bar(self):
        self.check(lambda d: d["ticks"].append((dt.datetime(2025, 11, 6, 8, 59, 50), 24000.0, 5, "U")))

    def test_session_outside_phase2(self):
        def mut(d):
            d["ledgers"]["R1"][1].date = "2025-11-08"
        self.check(mut)

    def test_gex_sessions_incomplete(self):
        self.check(mut_diag=lambda g: g["gex_sessions"].pop())

    def test_out_not_empty(self):
        def prep(p):
            p["out"].mkdir(); (p["out"] / "x.txt").write_text("x")
        self.check(prep=prep)

    def test_phase_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = make(t)
            with self.assertRaises(RuntimeError):
                A.run("phase1", p["a0"], p["r3"], p["r4"], p["diag"], p["out"])

    def test_check_unchanged(self):
        A.check_unchanged({"a": "1"}, {"a": "1"})
        with self.assertRaises(A.MappingError):
            A.check_unchanged({"a": "1"}, {"a": "2"})
        with self.assertRaises(A.MappingError):
            A.check_unchanged({"a": "1"}, {"a": "1", "b": "3"})


if __name__ == "__main__":
    unittest.main()
