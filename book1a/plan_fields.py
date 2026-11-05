"""Book 1A context and side fields written on every zone before the open (checklist P0.9).

Phase 2 (Context, C6):
  market_context = BULLISH | BEARISH | BALANCED | NONE, and separately draw_status = ACTIVE | REACHED |
  INVALIDATED | NONE (NONE = no draw candidate exists; written by plan_v24 only then, with no draw= line, and never
  treated as ACTIVE; a DrawState is never NONE); draw=<lo>-<hi>; balance=<lo>-<hi>, balance_poc=; value_follows (value_vs_price);
  on_inventory; edge_control; gex_regime; htf_structure.
  Nov 5, 2026 (pre-freeze specification change, Kyron): htf_acceptance = ABOVE | BELOW | NONE (PO-9 at the HTF
  composite VAH / VAL, data before 08:10 CT), context_base = BULLISH | BEARISH | BALANCED | NONE_NO_EVIDENCE |
  NONE_CONFLICT, and the precedence in apply_htf_acceptance. Context evidence only.
Phase 3 (zone selection and side rules):
  sides long= / short= in {ANY, RESPONSE, INITIATION, NONE}; the most restrictive rule wins
  (NONE > INITIATION > RESPONSE > ANY); every conflict is logged as
  side_conflict=<zone>|<side>|<rule=answer,...>; first_touch=YES on the first RTH test.

Everything marked (ours) in the docs is implemented as written there, with no new numbers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

VERSION = "plan-fields-v1.1"   # v1.1: htf_acceptance precedence, None split (Nov 5, 2026)

RESTRICTIVENESS = {"NONE": 3, "INITIATION": 2, "RESPONSE": 1, "ANY": 0}


# ---- context (Phase 2) -----------------------------------------------------------------------
@dataclass
class ContextInputs:
    price: float
    htf_val: float                      # higher-time-frame composite value area low
    htf_vah: float
    held_or_reclaimed_val: bool         # price inside/above composite value after holding or reclaiming its VAL
    failed_or_lost_vah: bool            # mirror
    wk_val_state: str                   # PO-9 state at the weekly VAL: ACCEPTED_BELOW | TESTING | INSIDE | ...
    wk_vah_state: str                   # PO-9 state at the weekly VAH
    balance_overlapping: bool           # PD2 + PD + ON (or days of the week) value areas overlap
    balance_lo: Optional[float] = None
    balance_hi: Optional[float] = None
    balance_poc: Optional[float] = None


HTF_ACCEPTANCE_LABEL = ("ours: acceptance outside composite value as context evidence, informed by Jeron Part 1, "
                        "00:34:58")
HTF_ACCEPTANCE_VALUES = ("ABOVE", "BELOW", "NONE")
CONTEXT_BASE_VALUES = ("BULLISH", "BEARISH", "BALANCED", "NONE_NO_EVIDENCE", "NONE_CONFLICT")


def context_base(ci: ContextInputs) -> str:
    """Context rule before the HTF acceptance step (draft, approved Oct 31; our mapping marked 'needed').
    None is split (Kyron, Nov 5, 2026, pre-freeze specification change):
      NONE_CONFLICT    = a higher-time-frame directional read passed but the weekly PO-9 acceptance disagrees
                         (bullish read but ACCEPTED_BELOW the weekly VAL, or bearish read but ACCEPTED_ABOVE the
                         weekly VAH); also both directional reads passing at once (price inside HTF value with
                         both edges touched; the HTF acceptance is always NONE there, so the label is kept either way);
      NONE_NO_EVIDENCE = no directional test passed."""
    inside_or_above = ci.price >= ci.htf_val
    inside_or_below = ci.price <= ci.htf_vah
    read_bull = inside_or_above and ci.held_or_reclaimed_val
    read_bear = inside_or_below and ci.failed_or_lost_vah
    bullish = read_bull and ci.wk_val_state != "ACCEPTED_BELOW"
    bearish = read_bear and ci.wk_vah_state != "ACCEPTED_ABOVE"
    if bullish and not bearish:
        return "BULLISH"
    if bearish and not bullish:
        return "BEARISH"
    if ci.balance_overlapping:
        return "BALANCED"
    if read_bull or read_bear:
        return "NONE_CONFLICT"
    return "NONE_NO_EVIDENCE"


def apply_htf_acceptance(base: str, htf_acceptance: str) -> str:
    """Precedence (Context doc, Nov 5, 2026; deterministic). Returns the market_context written to S1.4:
    BULLISH | BEARISH | BALANCED | NONE.
      BULLISH + ABOVE = BULLISH;  BEARISH + BELOW = BEARISH;
      BULLISH + BELOW or BEARISH + ABOVE = NONE (conflict);
      BALANCED stays BALANCED whatever the acceptance (acceptance logged only);
      NONE_NO_EVIDENCE + ABOVE = BULLISH, + BELOW = BEARISH;  NONE_CONFLICT stays NONE;
      no acceptance (NONE) = the existing label kept."""
    if base not in CONTEXT_BASE_VALUES:
        raise ValueError(f"unknown context base {base!r}")
    if htf_acceptance not in HTF_ACCEPTANCE_VALUES:
        raise ValueError(f"unknown htf_acceptance {htf_acceptance!r}")
    if base == "BALANCED":
        return "BALANCED"
    if base == "NONE_CONFLICT":
        return "NONE"
    if htf_acceptance == "NONE":
        return "NONE" if base == "NONE_NO_EVIDENCE" else base
    if base == "NONE_NO_EVIDENCE":
        return "BULLISH" if htf_acceptance == "ABOVE" else "BEARISH"
    if base == "BULLISH":
        return "BULLISH" if htf_acceptance == "ABOVE" else "NONE"
    return "BEARISH" if htf_acceptance == "BELOW" else "NONE"     # BEARISH


def htf_acceptance_from_states(val_state: Optional[str], vah_state: Optional[str]) -> str:
    """PO-9 states at the HTF composite VAL / VAH -> htf_acceptance."""
    below = val_state == "ACCEPTED_BELOW"
    above = vah_state == "ACCEPTED_ABOVE"
    if below and not above:
        return "BELOW"
    if above and not below:
        return "ABOVE"
    return "NONE"


def market_context(ci: ContextInputs, htf_acceptance: str = "NONE") -> str:
    """market_context written to S1.4 (BULLISH | BEARISH | BALANCED | NONE): context_base, then the HTF
    acceptance precedence. With htf_acceptance=NONE this is the Oct 31 rule unchanged."""
    return apply_htf_acceptance(context_base(ci), htf_acceptance)


def balance_fields(ci: ContextInputs) -> Dict[str, Optional[str]]:
    if ci.balance_overlapping and ci.balance_lo is not None:
        return {"balance": f"{ci.balance_lo:g}-{ci.balance_hi:g}", "balance_poc": f"{ci.balance_poc:g}"}
    return {"balance": None, "balance_poc": None}


def value_follows(pd_high: float, pd2_high: float, pd_low: float, pd2_low: float,
                  pd_vah: float, pd2_vah: float, pd_val: float, pd2_val: float,
                  pd_poc: float, pd2_poc: float) -> str:
    """Context input 1: a new high with a lower VAH and POC = DIVERGENT_UP; a new low with a higher
    VAL and POC = DIVERGENT_DOWN; otherwise WITH_PRICE."""
    if pd_high > pd2_high and pd_vah < pd2_vah and pd_poc < pd2_poc:
        return "DIVERGENT_UP"
    if pd_low < pd2_low and pd_val > pd2_val and pd_poc > pd2_poc:
        return "DIVERGENT_DOWN"
    return "WITH_PRICE"


def on_inventory(on_vwap_or_poc: float, settlement: float, price: float) -> Dict[str, object]:
    """Context input 2 (fields only; 'far' and 'thin' are NOT SET in the docs: logged as None)."""
    inv = "NET_LONG" if price > on_vwap_or_poc else "NET_SHORT" if price < on_vwap_or_poc else "NEUTRAL"
    return {"on_inventory": inv, "on_vs_settle": round(price - settlement, 2), "on_profile": None,
            "on_far": None, "on_thin": None}


def edge_control(bands_at_edge: List[str]) -> str:
    """Context input 4: SELLERS | BUYERS | MIXED from the delta bands (PO-7) touching the edge."""
    s = {b for b in bands_at_edge}
    if s == {"SELL"}:
        return "SELLERS"
    if s == {"BUY"}:
        return "BUYERS"
    return "MIXED"


def htf_structure(h1_swing_highs: List[float], h1_swing_lows: List[float]) -> str:
    """Context input 7 from the 1-hour swings (map h1_swings, ours): demand zones stepping higher and
    supply run through = RAISING_DEMAND; supply stepping lower = LOWERING_SUPPLY; else BALANCE."""
    if len(h1_swing_highs) >= 2 and len(h1_swing_lows) >= 2:
        hh = h1_swing_highs[-1] > h1_swing_highs[-2]
        hl = h1_swing_lows[-1] > h1_swing_lows[-2]
        lh = h1_swing_highs[-1] < h1_swing_highs[-2]
        ll = h1_swing_lows[-1] < h1_swing_lows[-2]
        if hh and hl:
            return "RAISING_DEMAND"
        if lh and ll:
            return "LOWERING_SUPPLY"
    return "BALANCE"


def gex_regime(total_net_gex: Optional[float]) -> Optional[str]:
    if total_net_gex is None:
        return None
    return "POS" if total_net_gex >= 0 else "NEG"


@dataclass
class DrawState:
    draw_lo: float
    draw_hi: float
    status: str = "ACTIVE"             # ACTIVE | REACHED | INVALIDATED (NONE = no DrawState at all; see plan_v24)
    new_target_needed: bool = False     # logged only (Context, trigger 2)

    def on_price(self, bar_high: float, bar_low: float) -> None:
        if self.status == "ACTIVE" and bar_high >= self.draw_lo and bar_low <= self.draw_hi:
            self.status = "REACHED"
            self.new_target_needed = True

    def on_invalidation(self) -> None:
        self.status = "INVALIDATED"

    def as_fields(self) -> Dict[str, str]:
        return {"draw": f"{self.draw_lo:g}-{self.draw_hi:g}", "draw_status": self.status,
                "NEW_TARGET_NEEDED": "1" if self.new_target_needed else "0"}


def invalidation(context: str, wk_val: float, wk_vah: float, htf_val: float, htf_vah: float) -> Dict[str, Optional[float]]:
    """Trigger 1: a Bullish context invalidates below the weekly or composite VAL it depends on
    (the nearer edge below price is the one that protects it: we write the higher of the two);
    a Bearish one above the VAH. Acceptance = 3 closes (strategy rule)."""
    if context == "BULLISH":
        return {"invalidate_below": max(wk_val, htf_val), "invalidate_above": None}
    if context == "BEARISH":
        return {"invalidate_below": None, "invalidate_above": min(wk_vah, htf_vah)}
    return {"invalidate_below": None, "invalidate_above": None}


# ---- sides (Phase 3) --------------------------------------------------------------------------
@dataclass
class ZoneForSides:
    label: str
    lo: float
    hi: float
    above_price: bool
    kind: str = ""                      # REJ_HIGH | REJ_LOW | FLIP | VALUE_EDGE | DD_EDGE | MAP4_AREA | ...
    tests: int = 0                      # tests on 1-hour bars (packet zones[].tests)
    lower_highs_into_zone: bool = False
    higher_lows_into_zone: bool = False
    accept_state: Optional[str] = None  # PO-9 state for value edges
    edge_control: Optional[str] = None  # SELLERS | BUYERS | MIXED at value edges
    dd_far_side_is_long: Optional[bool] = None   # DD_EDGE: the side moving INTO the far distribution
    value_follows: str = "WITH_PRICE"
    is_highs_edge: bool = False         # the zone sits at the prior highs (value_follows DIVERGENT_UP applies)
    is_lows_edge: bool = False
    gex_regime: Optional[str] = None    # logged only (rule 4 is a tag until tested)


def _rules_for_side(z: ZoneForSides, side: str, context: str) -> List[Tuple[str, str]]:
    """(rule, answer) for one side of one zone. 'long' through a zone above price is INITIATION-type
    (break through); 'long' off a zone below price is the response side."""
    rules: List[Tuple[str, str]] = []
    breaking = (side == "long" and z.above_price) or (side == "short" and not z.above_price)
    # 1. context sides (counter-context = INITIATION, with-context = ANY; Balanced/None = ANY)
    if context in ("BULLISH", "BEARISH"):
        with_ctx = (context == "BULLISH") == (side == "long")
        rules.append(("context", "ANY" if with_ctx else "INITIATION"))
    else:
        rules.append(("context", "ANY"))
    is_rej = z.kind in ("REJ_HIGH", "REJ_LOW", "FLIP")
    # 2. zone tested 4+ times with lower highs / higher lows: favour INITIATION through it;
    #    the response side stays open (ANY). Does not apply to rejection / flip zones.
    if not is_rej and z.tests >= 4 and (z.lower_highs_into_zone or z.higher_lows_into_zone):
        rules.append(("tests4", "INITIATION" if breaking else "ANY"))
    # accepted value edge: ACCEPTED_BELOW at a VAL -> short ANY, long INITIATION; mirror at a VAH
    if z.accept_state == "ACCEPTED_BELOW":
        rules.append(("accepted_edge", "INITIATION" if side == "long" else "ANY"))
    elif z.accept_state == "ACCEPTED_ABOVE":
        rules.append(("accepted_edge", "INITIATION" if side == "short" else "ANY"))
    # double distribution edge: into the far distribution = INITIATION only; responding off it = ANY
    if z.kind == "DD_EDGE" and z.dd_far_side_is_long is not None:
        into = (side == "long") == z.dd_far_side_is_long
        rules.append(("dd_edge", "INITIATION" if into else "ANY"))
    # 6. context side effects: edge_control and value_follows
    if z.edge_control == "SELLERS":
        rules.append(("edge_control", "INITIATION" if side == "long" and breaking else "ANY"))
    elif z.edge_control == "BUYERS":
        rules.append(("edge_control", "INITIATION" if side == "short" and breaking else "ANY"))
    if z.value_follows == "DIVERGENT_UP" and z.is_highs_edge and side == "long" and breaking:
        rules.append(("value_follows", "INITIATION"))
    if z.value_follows == "DIVERGENT_DOWN" and z.is_lows_edge and side == "short" and breaking:
        rules.append(("value_follows", "INITIATION"))
    return rules


def resolve_side(z: ZoneForSides, side: str, context: str) -> Tuple[str, Optional[str]]:
    """Most restrictive rule wins; returns (answer, side_conflict string or None)."""
    rules = _rules_for_side(z, side, context)
    answers = {a for _, a in rules}
    best = max(rules, key=lambda ra: RESTRICTIVENESS[ra[1]])[1]
    conflict = None
    if len(answers) > 1:
        conflict = f"side_conflict={z.label}|{side}|" + ",".join(f"{r}={a}" for r, a in rules)
    return best, conflict


def zone_fields(z: ZoneForSides, context: str, first_touch_pending: bool = True) -> Dict[str, object]:
    long_side, c1 = resolve_side(z, "long", context)
    short_side, c2 = resolve_side(z, "short", context)
    return {"zone": z.label, "long": long_side, "short": short_side,
            "side_conflict": "; ".join(c for c in (c1, c2) if c) or None,
            "first_touch": "YES" if first_touch_pending else "NO", "tests": z.tests,
            "gex_regime": z.gex_regime, "edge_control": z.edge_control, "value_follows": z.value_follows}


class FirstTouchTracker:
    """first_touch=YES on each decision zone's first RTH test; the test number is logged per candidate."""
    def __init__(self):
        self.counts: Dict[str, int] = {}

    def touch(self, zone_label: str) -> Dict[str, object]:
        n = self.counts.get(zone_label, 0) + 1
        self.counts[zone_label] = n
        return {"first_touch": "YES" if n == 1 else "NO", "test_number": n}
