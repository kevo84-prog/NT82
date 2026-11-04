"""P0.7 unit tests on hand-built synthetic bars (the real-data hand-check on 3 Phase 1 days runs on the PC)."""
import unittest
from datetime import date, datetime, time, timedelta

from book1a import map_v24 as m
from book1a.map_v24 import CT, Bar, Zone


def bar(d, h, mi, o, hi, lo, c, buy=100, sell=100, **kw):
    return Bar(datetime.combine(d, time(h, mi), tzinfo=CT), o, hi, lo, c, buy, sell, **kw)


def flat_bars(d, h0, m0, n, px, start_delta_min=0):
    """n flat bars from (h0, m0), 1 minute apart."""
    t0 = datetime.combine(d, time(h0, m0), tzinfo=CT)
    out = []
    for k in range(n):
        t = t0 + timedelta(minutes=k)
        out.append(Bar(t, px, px + 1, px - 1, px, 100, 100))
    return out


class TestSwingAndRejection(unittest.TestCase):
    def setUp(self):
        self.d = date(2025, 10, 22)   # Wednesday session; overnight from Tue 17:00 CT
        self.as_of = datetime.combine(self.d, time(8, 10), tzinfo=CT)
        self.adr = 200.0
        p = date(2025, 10, 21)
        bars = flat_bars(p, 20, 0, 20, 24000.0)              # 20:00-20:19 flat (before the swing)
        t = datetime.combine(p, time(20, 20), tzinfo=CT)
        # arrival: two bars of aggressive buying, then the swing bar; bodies 24020-24040
        bars.append(Bar(t, 24000.0, 24030.0, 23999.0, 24028.0, 400, 100))                 # delta +300
        bars.append(Bar(t + timedelta(minutes=1), 24028.0, 24045.0, 24026.0, 24040.0, 350, 150))  # +200
        bars.append(Bar(t + timedelta(minutes=2), 24040.0, 24060.0, 24030.0, 24032.0, 200, 260))  # swing high 24060
        bars.append(Bar(t + timedelta(minutes=3), 24032.0, 24034.0, 24010.0, 24012.0, 100, 300))
        bars.append(Bar(t + timedelta(minutes=4), 24012.0, 24013.0, 23990.0, 23995.0, 100, 300))  # departure 70 pts
        # 20 more flat bars well below (so the swing is confirmed and the 15 after have closed)
        bars += flat_bars(p, 20, 25, 20, 23990.0)
        self.bars = bars

    def test_swing_found_and_zone_drawn(self):
        zs = m.rejection_zones(self.bars, self.d, self.as_of, self.adr)
        self.assertEqual(len(zs), 1)
        z = zs[0]
        self.assertEqual(z.kind, "REJ_HIGH")
        self.assertEqual(z.hi, 24060.0)
        # bottom = lowest body among the swing bar +/-2: bodies 24000/24028, 24028/24040, 24040/24032,
        # 24032/24012, 24012/23995 -> 23995 ; width 65 > 40 -> keep the 40 nearest the extreme: 24020
        self.assertEqual(z.lo, 24020.0)
        self.assertEqual(z.session, "ON")
        self.assertTrue(z.arrival_evidence.startswith("DELTA:"))
        self.assertAlmostEqual(z.departure_pts, 71.0)   # 24060 - 23989 (lows of the flat bars)
        self.assertEqual(z.available_at, self.as_of)
        self.assertEqual(z.zone_class, "TARGET")        # class is set by the families step

    def test_no_zone_without_arrival_aggression(self):
        bars = [Bar(b.close_ct, b.open, b.high, b.low, b.close, 100, 100) for b in self.bars]
        self.assertEqual(m.rejection_zones(bars, self.d, self.as_of, self.adr), [])

    def test_no_zone_without_fast_departure(self):
        # ADR so large that 70 points is under 0.25 x ADR
        self.assertEqual(m.rejection_zones(self.bars, self.d, self.as_of, adr=400.0), [])

    def test_swing_not_known_before_15_bars_closed(self):
        early = datetime.combine(date(2025, 10, 21), time(20, 30), tzinfo=CT)   # 8 bars after the swing
        self.assertEqual(m.rejection_zones(self.bars, self.d, early, self.adr), [])
        late = datetime.combine(date(2025, 10, 21), time(20, 37), tzinfo=CT)    # 15th bar after closes 20:37
        self.assertEqual(len(m.rejection_zones(self.bars, self.d, late, self.adr)), 1)
        self.assertEqual(m.rejection_zones(self.bars, self.d, late - timedelta(minutes=1), self.adr), [])

    def test_min_width_padding(self):
        lo, hi = m._pad_min(100.0, 104.0)
        self.assertEqual((lo, hi), (97.0, 107.0))
        self.assertEqual(m._pad_min(100.0, 115.0), (100.0, 115.0))

    def test_merge_within_5_points(self):
        a = Zone(100.0, 120.0, "REJ_HIGH", datetime.combine(self.d, time(1, 0), tzinfo=CT), self.as_of, "ON")
        b = Zone(124.0, 140.0, "REJ_HIGH", datetime.combine(self.d, time(2, 0), tzinfo=CT), self.as_of, "ON")
        c = Zone(150.0, 160.0, "REJ_HIGH", datetime.combine(self.d, time(3, 0), tzinfo=CT), self.as_of, "ON")
        out = m.merge_same_side([a, b, c])
        self.assertEqual([(z.lo, z.hi) for z in out], [(100.0, 140.0), (150.0, 160.0)])
        # a 45-point union is capped at 40 nearest the high
        a2 = Zone(100.0, 125.0, "REJ_HIGH", a.formed_ct, self.as_of, "ON")
        b2 = Zone(126.0, 145.0, "REJ_HIGH", b.formed_ct, self.as_of, "ON")
        out = m.merge_same_side([a2, b2])
        self.assertEqual((out[0].lo, out[0].hi), (105.0, 145.0))

    def test_merge_keeps_newer_swing_index(self):
        """E22: the merged zone keeps the newer swing's index and the more extreme swing price."""
        a = Zone(100.0, 120.0, "REJ_HIGH", datetime.combine(self.d, time(1, 0), tzinfo=CT), self.as_of, "ON",
                 extra={"swing_index": 10, "swing_price": 120.0})
        b = Zone(110.0, 125.0, "REJ_HIGH", datetime.combine(self.d, time(2, 0), tzinfo=CT), self.as_of, "ON",
                 extra={"swing_index": 70, "swing_price": 125.0})
        out = m.merge_same_side([a, b])
        self.assertEqual((out[0].extra["swing_index"], out[0].extra["swing_price"], out[0].extra["merged_from"]), (70, 125.0, 2))
        lo1 = Zone(100.0, 110.0, "REJ_LOW", datetime.combine(self.d, time(3, 0), tzinfo=CT), self.as_of, "ON",
                   extra={"swing_index": 90, "swing_price": 100.0})
        lo2 = Zone(98.0, 108.0, "REJ_LOW", datetime.combine(self.d, time(1, 0), tzinfo=CT), self.as_of, "ON",
                   extra={"swing_index": 20, "swing_price": 98.0})
        out = m.merge_same_side([lo1, lo2])
        self.assertEqual((out[0].extra["swing_index"], out[0].extra["swing_price"]), (90, 98.0))

    def test_merged_zone_confirmed_at_its_last_component(self):
        """Kyron, Nov 4: a merged zone is available at the later of its components' confirmation times."""
        c1 = {"kind": "REJ_HIGH", "formed_ct": datetime.combine(self.d, time(1, 0), tzinfo=CT).isoformat(),
              "confirmed_ct": datetime.combine(self.d, time(1, 15), tzinfo=CT).isoformat()}
        c2 = {"kind": "REJ_HIGH", "formed_ct": datetime.combine(self.d, time(2, 0), tzinfo=CT).isoformat(),
              "confirmed_ct": datetime.combine(self.d, time(2, 15), tzinfo=CT).isoformat()}
        a = Zone(100.0, 120.0, "REJ_HIGH", datetime.combine(self.d, time(1, 0), tzinfo=CT), self.as_of, "ON",
                 extra={"swing_index": 10, "swing_price": 120.0, "confirmed_ct": c1["confirmed_ct"], "components": [c1]})
        b = Zone(110.0, 125.0, "REJ_HIGH", datetime.combine(self.d, time(2, 0), tzinfo=CT), self.as_of, "ON",
                 extra={"swing_index": 70, "swing_price": 125.0, "confirmed_ct": c2["confirmed_ct"], "components": [c2]})
        for order in ([a, b], [b, a]):
            out = m.merge_same_side(order)
            self.assertEqual(out[0].extra["confirmed_ct"], c2["confirmed_ct"])
            self.assertEqual(len(out[0].extra["components"]), 2)

    def test_merged_confirmation_compares_times_across_dst(self):
        """Oct 31 (-05:00) vs Nov 3 (-06:00): the later time wins, not the larger string."""
        early = {"confirmed_ct": "2025-11-02 00:30:00-05:00", "kind": "REJ_LOW", "formed_ct": "2025-11-02 00:15:00-05:00"}
        late = {"confirmed_ct": "2025-11-02 01:10:00-06:00", "kind": "REJ_LOW", "formed_ct": "2025-11-02 00:55:00-06:00"}
        z1 = Zone(100.0, 110.0, "REJ_LOW", datetime.fromisoformat(early["formed_ct"]), self.as_of, "ON", extra={"components": [late]})
        z2 = Zone(101.0, 111.0, "REJ_LOW", datetime.fromisoformat(late["formed_ct"]), self.as_of, "ON", extra={"components": [early]})
        out = m.merge_same_side([z1, z2])
        self.assertEqual(out[0].extra["confirmed_ct"], late["confirmed_ct"])

    def test_session_tags(self):
        self.assertEqual(m.session_of(datetime.combine(date(2025, 10, 21), time(20, 0), tzinfo=CT), self.d), "ON")
        self.assertEqual(m.session_of(datetime.combine(date(2025, 10, 21), time(10, 0), tzinfo=CT), self.d), "PD")
        self.assertEqual(m.session_of(datetime.combine(date(2025, 10, 20), time(10, 0), tzinfo=CT), self.d), "WK")
        # Monday: prior day is Friday, overnight starts Sunday 17:00
        mon = date(2025, 10, 27)
        self.assertEqual(m.session_of(datetime.combine(date(2025, 10, 26), time(18, 0), tzinfo=CT), mon), "ON")
        self.assertEqual(m.session_of(datetime.combine(date(2025, 10, 24), time(12, 0), tzinfo=CT), mon), "PD")

    def test_window_start(self):
        # Wed: min(Tue 08:30, Sun 17:00) = Sun 17:00 ; Mon: min(Fri 08:30, Sun 17:00) = Fri 08:30
        self.assertEqual(m.window_start(self.d), datetime.combine(date(2025, 10, 19), time(17, 0), tzinfo=CT))
        self.assertEqual(m.window_start(date(2025, 10, 27)), datetime.combine(date(2025, 10, 24), time(8, 30), tzinfo=CT))


class TestFlip(unittest.TestCase):
    def test_support_accepted_through_then_resisted(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        p = date(2025, 10, 21)
        t0 = datetime.combine(p, time(19, 0), tzinfo=CT)
        bars = []
        k = 0
        def add(o, h, l, c, buy=100, sell=100):
            nonlocal k
            bars.append(Bar(t0 + timedelta(minutes=k), o, h, l, c, buy, sell)); k += 1
        for _ in range(16): add(24050, 24051, 24049, 24050)
        add(24050, 24051, 24030, 24032, 100, 400)       # aggressive selling into the low
        add(24032, 24033, 24020, 24022, 100, 300)       # swing low 24020 (REJ_LOW), delta -200
        add(24022, 24070, 24021, 24068, 300, 100)       # fast departure up 50
        for _ in range(16): add(24068, 24069, 24067, 24068)
        # acceptance below: 3 closes <= 24020 - 0.5
        for _ in range(3): add(24010, 24011, 24005, 24008)
        for _ in range(14): add(24008, 24009, 24007, 24008)
        # now a REJ_HIGH forms inside the old support band (24020-24032 padded...)
        add(24008, 24009, 24007, 24008, 300, 100)       # arrival buy delta +200
        add(24008, 24045, 24007, 24042, 350, 100)       # swing high 24045 inside the old support band
        add(24042, 24043, 24010, 24012, 100, 300)
        add(24012, 24013, 23980, 23982, 100, 300)       # departure 65 pts
        for _ in range(16): add(23982, 23983, 23981, 23982)
        zs = m.rejection_zones(bars, d, as_of, adr=100.0)
        kinds = sorted(z.kind for z in zs)
        self.assertEqual(kinds, ["REJ_HIGH", "REJ_LOW"])
        out = m.flips(bars, zs, as_of)
        self.assertEqual([z.kind for z in out], ["FLIP"])
        f = out[0]
        self.assertEqual(f.extra["flip_from"], "REJ_LOW")
        # REJ_LOW band (24020-24060 after the 40-pt cap) accepted through, then REJ_HIGH 24005-24045:
        # overlap 25 / 40 = 62.5% >= 50%; union 24005-24060 capped at 40 nearest the newer swing high
        self.assertEqual((f.lo, f.hi), (24020.0, 24060.0))

    def test_no_flip_without_acceptance(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        a = Zone(100.0, 110.0, "REJ_LOW", datetime.combine(d, time(1, 0), tzinfo=CT), as_of, "ON", extra={"swing_index": 0})
        b = Zone(102.0, 115.0, "REJ_HIGH", datetime.combine(d, time(3, 0), tzinfo=CT), as_of, "ON", extra={"swing_index": 5})
        bars = flat_bars(d, 0, 0, 10, 105.0)       # never closes 2 ticks below 100
        out = m.flips(bars, [a, b], as_of)
        self.assertEqual(sorted(z.kind for z in out), ["REJ_HIGH", "REJ_LOW"])


class TestSelection(unittest.TestCase):
    def test_two_per_side_nearest_first_and_traded_through_dropped(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        f = lambda h: datetime.combine(d, time(h, 0), tzinfo=CT)
        zs = [Zone(24100, 24120, "REJ_HIGH", f(1), as_of, "ON"), Zone(24150, 24170, "REJ_HIGH", f(2), as_of, "PD"),
              Zone(24200, 24220, "REJ_HIGH", f(3), as_of, "WK"), Zone(23900, 23920, "REJ_LOW", f(4), as_of, "ON"),
              Zone(23500, 23520, "REJ_LOW", f(5), as_of, "ON")]
        sel = m.select_zones(zs, price=24000.0, adr=250.0, bars=[], as_of=as_of)
        self.assertEqual([(z.lo, z.hi) for z in sel], [(24100, 24120), (24150, 24170), (23900, 23920)])
        # price traded 300 points above a zone after it formed (adr 250): dropped
        bars = [Bar(f(6), 24400.0, 24450.0, 24390.0, 24400.0)]
        sel = m.select_zones(zs, price=24000.0, adr=250.0, bars=bars, as_of=as_of)
        self.assertEqual([(z.lo, z.hi) for z in sel], [(24200, 24220), (23900, 23920)])


class TestMap4(unittest.TestCase):
    def test_area_70_percent_of_peak(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        rows = {24000.0: 50, 24005.0: 72, 24010.0: 100, 24015.0: 80, 24020.0: 69, 24025.0: 90}
        z = m.map4_area(rows, 24010.0, as_of, "D_PDPOC")
        self.assertEqual((z.lo, z.hi), (24005.0, 24020.0))      # 24020 row (69 < 70) stops the run
        self.assertEqual(z.kind, "MAP4_AREA")

    def test_area_capped_40_centred(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        rows = {24000.0 + 5 * k: 100 for k in range(20)}       # 100 points all at the peak level
        z = m.map4_area(rows, 24050.0, as_of, "D_WKPOC")
        self.assertEqual(z.width, 40.0)
        self.assertEqual((z.lo, z.hi), (24032.5, 24072.5))

    def test_narrow_area_keeps_pad(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        rows = {24000.0: 10, 24005.0: 100, 24010.0: 10}
        z = m.map4_area(rows, 24005.0, as_of, "D_ONPOC")
        self.assertEqual((z.lo, z.hi), (24002.5, 24012.5))


class TestDeltaBands(unittest.TestCase):
    def test_bands_top_20_percent_adjacent_same_sign(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        rows = {24000.0 + 5 * k: 10 for k in range(10)}     # 10 rows: top 20% = 2 rows
        rows[24030.0] = -900; rows[24035.0] = -800          # adjacent selling rows
        bands = m.delta_bands(rows, as_of, "WK", price=24000.0)
        self.assertEqual(len(bands), 1)
        b = bands[0]
        self.assertEqual((b.lo, b.hi), (24030.0, 24040.0))
        self.assertEqual(b.extra["sign"], "SELL")
        self.assertEqual(b.label, "T_DELTA_SELL_WK")
        self.assertEqual(b.extra["role"], "TARGET")         # selling band above price: target for longs

    def test_single_top_row_is_not_a_band(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        rows = {24000.0 + 5 * k: 10 for k in range(10)}
        rows[24030.0] = -900; rows[24040.0] = -800          # not adjacent
        self.assertEqual(m.delta_bands(rows, as_of, "PD"), [])

    def test_opposite_sign_breaks_band_and_buy_band_below_price(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        rows = {24000.0 + 5 * k: 10 for k in range(20)}     # top 20% = 4 rows
        rows[24010.0] = 900; rows[24015.0] = 850; rows[24020.0] = -870; rows[24025.0] = -860
        bands = m.delta_bands(rows, as_of, "ON", price=24050.0)
        self.assertEqual([(b.lo, b.hi, b.extra["sign"]) for b in bands],
                         [(24010.0, 24020.0, "BUY"), (24020.0, 24030.0, "SELL")])
        self.assertEqual(bands[0].extra["role"], "TARGET")
        self.assertEqual(bands[1].extra["role"], "TAG_ONLY")


class TestAcceptance(unittest.TestCase):
    def test_accepted_below_after_60_minutes(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        bars = flat_bars(d, 6, 0, 70, 23990.0)              # closes 06:00-07:09, all below VAL 24000
        bars += flat_bars(d, 7, 10, 60, 23995.0)            # 07:10-08:09
        st = m.acceptance_state(bars, "VAL", 24000.0, 24100.0, price=23995.0, as_of=as_of, name="WKVAL")
        self.assertEqual(st.state, "ACCEPTED_BELOW")
        self.assertFalse(st.failed_reclaim)
        self.assertEqual(st.tag(), "accept=BELOW|failed_reclaim=0")

    def test_testing_when_too_recent(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        bars = flat_bars(d, 7, 0, 30, 24050.0) + flat_bars(d, 7, 30, 40, 23990.0)   # first close below at 07:30
        st = m.acceptance_state(bars, "VAL", 24000.0, 24100.0, 23990.0, as_of, "WKVAL")
        self.assertEqual(st.state, "TESTING")
        self.assertEqual(st.minutes_since_first_close, 40)

    def test_inside_and_failed_reclaim(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        st = m.acceptance_state(flat_bars(d, 7, 0, 10, 24050.0), "VAL", 24000.0, 24100.0, 24050.0, as_of, "WKVAL")
        self.assertEqual(st.state, "INSIDE")
        bars = flat_bars(d, 6, 0, 100, 23990.0)
        # one bar trades back up into the VAL with buy aggression and closes below it again
        bars[50] = Bar(bars[50].close_ct, 23990.0, 24003.0, 23989.0, 23992.0, 400, 100)
        bars += flat_bars(d, 7, 40, 30, 23990.0)
        st = m.acceptance_state(bars, "VAL", 24000.0, 24100.0, 23990.0, as_of, "WKVAL")
        self.assertEqual(st.state, "ACCEPTED_BELOW")
        self.assertTrue(st.failed_reclaim)

    def test_accepted_above_mirror(self):
        d = date(2025, 10, 22)
        as_of = datetime.combine(d, time(8, 10), tzinfo=CT)
        bars = flat_bars(d, 6, 0, 130, 24120.0)
        st = m.acceptance_state(bars, "VAH", 24100.0, 24000.0, 24120.0, as_of, "WKVAH")
        self.assertEqual(st.state, "ACCEPTED_ABOVE")


class TestDDEdge(unittest.TestCase):
    def test_far_distribution_near_edge(self):
        as_of = datetime.combine(date(2025, 10, 22), time(8, 10), tzinfo=CT)
        z = m.dd_edge_zone((24000.0, 24060.0), (24060.0, 24090.0), (24090.0, 24180.0), price=24030.0, as_of=as_of, profile="WK")
        self.assertEqual((z.lo, z.hi), (24090.0, 24130.0))
        self.assertEqual(z.extra["runner"], 24180.0)
        self.assertIn("DD_EDGE", z.tags)
        z = m.dd_edge_zone((24000.0, 24060.0), (24060.0, 24090.0), (24090.0, 24180.0), price=24150.0, as_of=as_of, profile="WK")
        self.assertEqual((z.lo, z.hi), (24020.0, 24060.0))
        self.assertEqual(z.extra["runner"], 24000.0)
        self.assertIsNone(m.dd_edge_zone((24000.0, 24060.0), (24060.0, 24090.0), (24090.0, 24180.0), 24075.0, as_of, "WK"))


class TestCompare(unittest.TestCase):
    def test_added_dropped_moved(self):
        d = date(2025, 10, 22)
        a = datetime.combine(d, time(8, 10), tzinfo=CT); b = datetime.combine(d, time(8, 29), tzinfo=CT)
        z1 = [Zone(100, 110, "REJ_HIGH", a, a, "ON"), Zone(200, 210, "REJ_LOW", a, a, "PD")]
        z2 = [Zone(100, 110.25, "REJ_HIGH", b, b, "ON"), Zone(201, 212, "REJ_LOW", b, b, "PD"), Zone(300, 310, "FLIP", b, b, "ON")]
        self.assertEqual(m.compare_as_of(z1, z2), {"same": 1, "moved": 1, "dropped": 0, "added": 1})


if __name__ == "__main__":
    unittest.main()
