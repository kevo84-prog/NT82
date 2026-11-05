"""Plan builder test on a synthetic packet + bars + profiles (the real 3-day sample plans run on the PC)."""
import unittest
from datetime import date, datetime, time, timedelta

from book1a import plan_v24 as P, vwap as V
from book1a.bars import CT, bars_from_rows, profiles_from_rows


def tick_rows():
    """A synthetic overnight: flat trading near 24000 with a rejection high at 24060 around 20:20 CT, then lower."""
    d = date(2025, 10, 21)
    t0 = datetime.combine(d, time(17, 0), tzinfo=CT)
    rows = []
    def add(minute, px, vol, ag, sec=30):
        rows.append((t0 + timedelta(minutes=minute, seconds=sec), px, vol, ag))
    for k in range(0, 200):
        add(k, 24000.0 + (k % 3) * 0.25, 10, "B" if k % 2 else "S")
    # arrival buying then rejection
    add(200, 24028.0, 400, "B", 10); add(200, 24030.0, 5, "S", 20)
    add(201, 24040.0, 350, "B", 10); add(201, 24045.0, 20, "S", 20)
    add(202, 24060.0, 200, "B", 10); add(202, 24032.0, 260, "S", 40)
    add(203, 24012.0, 300, "S", 10); add(204, 23995.0, 300, "S", 10)
    for k in range(205, 700):
        add(k, 23990.0 + (k % 3) * 0.25, 10, "B" if k % 2 else "S")
    return rows


class TestPlanBuilder(unittest.TestCase):
    def setUp(self):
        d = date(2025, 10, 22)
        self.as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        rows = tick_rows()
        self.bars = bars_from_rows(rows, end=self.as_of)
        wk_start = V.week_start(d); s_start = V.session_start(d)
        self.profiles = profiles_from_rows(rows, {"WK": (wk_start, self.as_of), "ON": (s_start, self.as_of),
                                                  "PD": (datetime.combine(d - timedelta(days=1), time(8, 30), tzinfo=CT),
                                                         datetime.combine(d - timedelta(days=1), time(15, 0), tzinfo=CT))})
        import numpy as np
        ts = np.array([int(r[0].timestamp()) * 10**9 for r in rows]); px = np.array([r[1] for r in rows]); sz = np.array([r[2] for r in rows])
        self.vwap = V.vwap_0810(ts, px, sz, d)
        self.packet = {
            "date": "2025-10-22", "ref_price": 23990.0, "asof_ct": "08:10", "ranges": {"adr_full": 200.0},
            "levels": [{"name": "WKVAL", "price": 23985.0}, {"name": "WKVAH", "price": 24150.0}, {"name": "WKPOC", "price": 24050.0},
                       {"name": "HTFVAL", "price": 23900.0}, {"name": "HTFVAH", "price": 24300.0}, {"name": "HTFPOC", "price": 24120.0},
                       {"name": "PDVAH", "price": 24055.0}, {"name": "PDVAL", "price": 23950.0}, {"name": "PDPOC", "price": 24000.0},
                       {"name": "PDH", "price": 24080.0}, {"name": "PDL", "price": 23930.0}, {"name": "SETTLE", "price": 24010.0}],
            "zones": [{"lo": 23945.0, "hi": 23955.0, "label": "D_PDVAL_WKVAL", "tier": "DECISION", "levels": ["PDVAL"],
                       "tests": {"from_below": 1, "from_above": 1}},
                      {"lo": 23925.0, "hi": 23935.0, "label": "T_PDL", "tier": "TARGET", "levels": ["PDL"]}],
            "balance_composite": {"overlapping": False},
            "prior_sessions": [{"slot": "PD", "covered": True, "day_high": 24080.0, "day_low": 23930.0, "vah": 24055.0, "val": 23950.0, "poc": 24000.0, "settle": 24010.0},
                               {"slot": "PD2", "covered": True, "day_high": 24060.0, "day_low": 23900.0, "vah": 24040.0, "val": 23940.0, "poc": 23990.0}],
            "overnight": {"vah": 24040.0, "val": 23985.0, "poc": 24000.0, "high": 24060.0, "low": 23985.0, "vwap": 24001.0},
            "weekly": {"vah": 24150.0, "val": 23985.0, "poc": 24050.0}, "structure": {"swing_highs": [24000, 24060], "swing_lows": [23950, 23985]},
            "data": {"gaps": []}, "calendar": {"half_day_today": False},
        }
        self.gex = {"ok": "True", "regime": "positive", "call_resistance_nt": "24150.00", "put_support_nt": "23850.00", "hvl_nt": "24000.00"}

    def test_plan_text_and_sidecar(self):
        text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertIn("end=1", text)
        self.assertIn("context=", text)
        self.assertNotIn("lava=", text)
        self.assertIn("market_context=", text)
        self.assertIn("draw_status=", text)
        self.assertIn("review=APPROVED", text)
        self.assertTrue(any(l.startswith("zone=") and "|DECISION|" in l for l in text.splitlines()))
        metas = [l for l in text.splitlines() if l.startswith("zone_meta=")]
        self.assertTrue(metas)
        self.assertTrue(all("families=" in m and "levels=" in m for m in metas))
        self.assertTrue(any(l.startswith("ladder=") for l in text.splitlines()))
        self.assertTrue(all(z["available_at"] == self.as_of.isoformat() for z in side["zones"]))
        self.assertTrue(all(len(z["families"]) >= 2 for z in side["zones"]))
        self.assertIn("vwap_0810=", text)
        self.assertIn("gex_regime=POS", text)
        for z in side["zones"]:
            self.assertIn(z["long"], ("ANY", "RESPONSE", "INITIATION", "NONE"))
            self.assertIn(z["short"], ("ANY", "RESPONSE", "INITIATION", "NONE"))

    def test_rejection_zone_appears_with_structure_family(self):
        text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [])
        rf = side["rej_flip_zones"]
        self.assertTrue(rf, "expected a REJ_HIGH zone from the synthetic overnight")
        self.assertEqual(rf[0]["kind"], "REJ_HIGH")
        self.assertEqual(rf[0]["hi"], 24060.0)

    def test_roll_day_and_half_day_log_only(self):
        pk = dict(self.packet); pk["date"] = "2025-12-15"
        text, side = P.build(pk, [], {}, {"SESSION": None, "WEEKLY": None}, None, [], roll_dates=("2025-12-15",),
                             as_of=datetime(2025, 12, 15, 8, 10, tzinfo=CT))
        self.assertIn("review=LOG_ONLY", text)
        pk = dict(self.packet); pk["calendar"] = {"half_day_today": True}
        text, _ = P.build(pk, self.bars, self.profiles, self.vwap, self.gex, [])
        self.assertIn("review=LOG_ONLY", text); self.assertIn("A: half day", text)

    def test_check_f_logged_not_applied(self):
        cal = [{"date": "2025-10-22", "category": "DATA", "event": "CPI", "no_trade_ct": "07:25-08:35", "status": ""}]
        text, _ = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, cal)
        self.assertNotIn("\nno_trade=", text)
        self.assertIn("research_check_f=no_trade=07:25-08:35", text)
        self.assertIn("review=APPROVED", text)

    def test_s14_reads_only_book1_keys(self):
        # every Book 1 key keeps its exact spelling; Book 1A keys come after the marker
        text, _ = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [])
        lines = text.splitlines()
        marker = lines.index("# --- Book 1A fields (logged by S1.4, not read) ---")
        before = [l.split("=")[0] for l in lines[:marker] if "=" in l and not l.startswith("#")]
        for k in before:
            self.assertIn(k, ("plan_id", "date", "asof", "packet_asof", "context", "context_note", "zone", "balance", "balance_poc",
                              "invalidate_above", "invalidate_below", "macro", "news"))


if __name__ == "__main__":
    unittest.main()


class TestWeeklyDD(TestPlanBuilder):
    """E23: the weekly DD edge joins the plan; PD and weekly DD edges are both STRUCTURE and count once."""
    def test_pd_and_weekly_dd_edges_count_structure_once(self):
        pk = dict(self.packet)
        pk["double_distribution"] = {"available": True, "pd_double_distribution": True, "lower_hvn": [23900.0, 23940.0],
                                     "upper_hvn": [23965.0, 24100.0], "separator": "LVN", "separator_lo": 23945.0, "separator_hi": 23960.0}
        wk = {"available": True, "status": "AVAILABLE", "double_distribution": True, "lower_hvn": [23905.0, 23938.0], "upper_hvn": [23970.0, 24150.0],
              "separator": "LVN", "separator_lo": 23945.0, "separator_hi": 23965.0, "profile": "WK"}
        text, side = P.build(pk, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), weekly_dd=wk)
        self.assertEqual(side["dd_edge"]["label"], "DD_EDGE_PD")
        self.assertEqual(side["dd_edge_wk"]["label"], "DD_EDGE_WK")
        self.assertEqual(side["dd_edge_wk"]["rule"], "ours: PD rule applied to weekly")
        self.assertEqual((side["dd_edge_wk"]["lo"], side["dd_edge_wk"]["hi"]), (23905.0, 23938.0))
        z = [z for z in side["zones"] if "DD_EDGE_PD" in z["label"] and "DD_EDGE_WK" in z["label"]]
        self.assertEqual(len(z), 1, [x["label"] for x in side["zones"]])
        self.assertEqual(z[0]["families"].count("STRUCTURE"), 1)

    def test_real_flip_raises_the_mandatory_review_flag(self):
        """E25 (Kyron, Nov 4): the first real FLIP must be reviewed; the plan says so (no gating change)."""
        from unittest import mock
        from book1a import map_v24 as M
        flip = M.Zone(24040.0, 24060.0, "FLIP", self.as_of, self.as_of, "ON")
        with mock.patch.object(M, "flips", side_effect=lambda bars, zones, as_of: list(zones) + [flip]):
            text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertEqual(side["research"]["flip_review_required"], ["24040.0-24060.0"])
        self.assertIn("E25: FLIP zone formed - mandatory targeted review", text)
        text2, side2 = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertNotIn("flip_review_required", side2["research"])

    def test_unavailable_weekly_is_noted_and_gives_no_zone(self):
        wk = {"available": False, "status": "UNAVAILABLE", "reason": "map left the weekly profile out: data gap x", "profile": "WK"}
        text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), weekly_dd=wk)
        self.assertIsNone(side["dd_edge_wk"])
        self.assertEqual(side["weekly_dd"]["status"], "UNAVAILABLE")
        self.assertIn("E26: weekly double distribution UNAVAILABLE", text)

    def test_no_weekly_input_means_no_weekly_zone(self):
        text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=())
        self.assertIsNone(side["dd_edge_wk"]); self.assertIsNone(side["weekly_dd"])


class TestDDInputs(unittest.TestCase):
    """E21: the v2.3 packet writes pd_double_distribution / lower_hvn / upper_hvn / separator_lo / separator_hi."""
    def test_packet_form(self):
        from book1a import plan_v24 as P
        ddp = {"available": True, "pd_double_distribution": True, "lower_hvn": [26035, 26079.75], "upper_hvn": [26180, 26189.75],
               "separator": "LVN", "separator_lo": 26090, "separator_hi": 26109.75, "hvn_blocks": 2}
        self.assertEqual(P.dd_inputs(ddp), ((26035.0, 26079.75), (26090.0, 26109.75), (26180.0, 26189.75), "PD"))

    def test_no_split_or_flag_only(self):
        from book1a import plan_v24 as P
        self.assertIsNone(P.dd_inputs({"available": True, "pd_double_distribution": False, "hvn_blocks": 1}))
        self.assertIsNone(P.dd_inputs(None))

    def test_generic_form(self):
        from book1a import plan_v24 as P
        self.assertEqual(P.dd_inputs({"dist_a": [1, 2], "separator": [2, 3], "dist_b": [3, 4], "profile": "WK"})[3], "WK")


class TestDrawStatusNone(TestPlanBuilder):
    """Context spec (Kyron, Nov 4): draw_status = ACTIVE | REACHED | INVALIDATED | NONE; NONE = no draw candidate exists,
    never treated as ACTIVE."""
    def _kv(self, text):
        return {l.split("=", 1)[0]: l.split("=", 1)[1] for l in text.splitlines() if "=" in l and not l.startswith("#")}

    def test_none_only_when_no_candidate(self):
        ev = {}
        text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
        kv = self._kv(text)
        self.assertEqual(kv["draw_status"] == "NONE", ev["draw_candidates"] == [])
        if kv["draw_status"] == "NONE":
            self.assertNotIn("draw", kv)            # no draw level is written, so nothing can read one as a target

    def test_bullish_with_a_candidate_is_active_not_none(self):
        from unittest import mock
        from book1a import plan_fields as PF
        ev = {}
        with mock.patch.object(PF, "resolve_context", return_value=dict(market_context="BULLISH", context_source="BASE",
                                                                        resolved="BULLISH", weekly_guard="PASS")):
            text, side = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
        kv = self._kv(text)
        self.assertTrue(ev["draw_candidates"])     # HTFPOC 24120 / HTFVAH 24300 sit above price 23990
        self.assertEqual(kv["draw_status"], "ACTIVE")
        self.assertIn("draw", kv)

    def test_balanced_or_none_context_has_no_candidate(self):
        from unittest import mock
        from book1a import plan_fields as PF
        for ctx in ("BALANCED", "NONE"):
            ev = {}
            with mock.patch.object(PF, "resolve_context", return_value=dict(market_context=ctx, context_source="NONE",
                                                                            resolved=ctx, weekly_guard="N/A")):
                text, _ = P.build(self.packet, self.bars, self.profiles, self.vwap, self.gex, [], roll_dates=(), evidence=ev)
            self.assertEqual(ev["draw_candidates"], [])
            self.assertEqual(self._kv(text)["draw_status"], "NONE")

    def test_draw_state_never_none(self):
        from book1a import plan_fields as PF
        d = PF.DrawState(100.0, 110.0)
        self.assertEqual(d.status, "ACTIVE")
        d.on_price(105.0, 99.0); self.assertEqual(d.status, "REACHED")
        d2 = PF.DrawState(100.0, 110.0); d2.on_invalidation(); self.assertEqual(d2.status, "INVALIDATED")

    def test_ladder_does_not_use_a_draw_when_none(self):
        """The ladder runner falls back to the draw only when a DrawState exists; NONE passes draw=None."""
        from book1a import plan_fields as PF
        c = {"lo": 100.0, "hi": 101.0}
        far = PF.DrawState(500.0, 510.0)
        with_none = P._ladder("long", c, 100.5, [], {}, [], [], None, None, {}, None, [], 6)
        with_draw = P._ladder("long", c, 100.5, [], {}, [], [], None, None, {}, far, [], 6)
        self.assertEqual(with_none["RUN"], "")
        self.assertEqual(with_draw["RUN"], "500.00-510.00")

    def test_s14_has_no_draw_key(self):
        """S1.4 (the frozen NT strategy) does not parse draw= or draw_status= (logged-only Book 1A fields)."""
        import os
        from pathlib import Path
        src = Path(os.environ.get("BOOK1_ROOT", r"K:\Databento_BackTesting")) / "jeron_harness" / "nt_source" / "JeronOrderFlowStrategy.cs"
        if not src.exists():
            self.skipTest("NT source not on this machine")
        s = src.read_text(encoding="utf-8", errors="replace")
        self.assertNotIn('key == "draw', s)
        self.assertNotIn('"draw_status"', s)
