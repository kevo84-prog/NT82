"""Tick regression (Kyron, Nov 5, 2026): every price the plan writes that orders, zones, stops, targets, the draw or the
invalidation use must be a multiple of 0.25 (NQ tick). Runs over every frozen plan in plans_phase1, the 4-day hand-check
plans and the hand-check pack plans.

Checked (plan text, the file S1.4 reads): zone= lo / hi (the entry is the zone edge), zone_meta stop_ticks (whole ticks, so
the stop = edge +- stop_ticks x 0.25 is on a tick), ladder TP1 / TP2 / RUN ranges, draw=, invalidate_below=,
invalidate_above=, balance=, balance_poc=, every mq_ GEX line. Also the sidecar zones / targets lo / hi.

Excluded as raw indicator readouts (logged only; no order, zone, stop or target is placed at them):
  vwap_0810, wkvwap_0810 (VWAP values to the cent), vwap_vs_price, on_vs_settle (point differences), ladder R_TP1 /
  R_TP2 / R_RUN (reward / risk ratios), the htf_val / htf_vah numbers inside context_note= (a free-text note; the same
  levels are tested where they become prices: invalidate_*, draw=)."""
import json
import re
import unittest
from pathlib import Path

PHASE0 = Path(__file__).resolve().parents[2] / "Book1A" / "Phase0"
FOLDERS = ("plans_phase1", "hand_checks", "hand_check_pack/plans")
TICK = 0.25
RANGE = re.compile(r"^(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)$")


def on_tick(x: float) -> bool:
    return abs(x / TICK - round(x / TICK)) < 1e-9


def _range(v: str):
    m = RANGE.match(v.strip())
    if not m:
        raise ValueError(f"not a lo-hi range: {v!r}")
    return float(m.group(1)), float(m.group(2))


def plan_prices(text: str):
    """(key, value) for every order / zone / stop / target / draw / invalidation price in a plan text."""
    out = []
    for line in text.splitlines():
        if line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        if key == "zone":
            lo, hi = _range(val.split("|")[0]); out += [("zone lo", lo), ("zone hi", hi)]
        elif key == "zone_meta":
            st = [p for p in val.split("|") if p.startswith("stop_ticks=")]
            if st:
                out.append(("stop_ticks (whole ticks)", float(st[0].split("=", 1)[1]) * TICK))
        elif key == "ladder":
            for part in val.split("|")[2:]:
                k, v = part.split("=", 1)
                if k in ("TP1", "TP2", "RUN") and v:
                    lo, hi = _range(v); out += [(f"ladder {k} lo", lo), (f"ladder {k} hi", hi)]
        elif key in ("draw", "balance"):
            lo, hi = _range(val.split("|")[0]); out += [(f"{key} lo", lo), (f"{key} hi", hi)]
        elif key in ("invalidate_below", "invalidate_above", "balance_poc") or key.startswith("mq_"):
            out.append((key, float(val.split("|")[0])))
    return out


def plan_files():
    return [f for folder in FOLDERS for f in sorted((PHASE0 / folder).glob("PreopenPlan_*_book1a.txt"))]


class TestPlanTicks(unittest.TestCase):
    def test_parser_flags_off_tick_values(self):
        bad = "zone=25874.2-26033.8|X|DECISION\nbalance=25874.20-26033.75\nmq_cr=26000.10\ninvalidate_below=25394.30|Balanced\n"
        self.assertEqual(sum(1 for _, v in plan_prices(bad) if not on_tick(v)), 5)
        good = "zone=25874.25-26033.75|X|DECISION\nbalance=25874.25-26033.75\nbalance_poc=25925.00\nmq_cr=26000.00\n"
        self.assertTrue(all(on_tick(v) for _, v in plan_prices(good)))

    def test_every_frozen_plan_price_on_tick(self):
        files = plan_files()
        self.assertEqual(len(files), 17, [f.name for f in files])      # 10 + 4 + 3 plan files
        bad, n, keys = [], 0, set()
        for f in files:
            for k, v in plan_prices(f.read_text(encoding="utf-8")):
                n += 1; keys.add(k.split(" ")[0])
                if not on_tick(v):
                    bad.append(f"{f.parent.name}/{f.name}: {k}={v}")
            sc = json.loads(f.with_suffix(".json").read_text(encoding="utf-8"))
            for grp in ("zones", "targets"):
                for z in sc.get(grp) or []:
                    for e in ("lo", "hi"):
                        n += 1
                        if not on_tick(float(z[e])):
                            bad.append(f"{f.name} sidecar {grp} {z['label']} {e}={z[e]}")
        self.assertEqual(bad, [])
        self.assertGreater(n, 1000)
        for k in ("zone", "ladder", "draw", "balance", "invalidate_below", "balance_poc", "mq_cr"):
            self.assertIn(k, keys)


if __name__ == "__main__":
    unittest.main()
