"""Book 1A source families on each zone (Phase 3 zone rule 1, C1; AMT PO-3; checklist P0.8).

Six families (Phase 3 doc, C1, approved Nov 1, 2026):
  1 AUCTION_VALUE  weekly, PD, ON, composite or merged-balance value edges (VAH / VAL)
  2 STRUCTURE      rejection or flip zones (PO-1), double distribution edges, structural extremes
  3 DELTA          delta profile bands (PO-7)
  4 VOLUME         POCs, HVN areas (PO-6), LVN, low-time and single-print areas
  5 GEX            calculated GEX: call resistance, put support, HVL, 0DTE levels, gamma ranks
  6 VWAP           overnight session VWAP, weekly VWAP and the +/-1 sigma bands (PO-8, C2)

Rules:
  - a level counts if it is inside the zone or within the family's tolerance of the zone's edge:
    GEX 10 points (Phase 3 zone rule 2, ours, Nov 1; sensitivity 5 / 20 / 35), VWAP 5 points
    (PO-8), every other family 5 points (PO-1 step 5 "stack ... inside the zone or within 5 points").
  - each family counts at most once however many of its levels overlap;
  - every individual level is kept in levels= so levels per family can be studied later;
  - DECISION needs 2+ families (ours; Jeron's examples have 3 to 5), else TARGET.
The plan writes families=<n>|<list> and levels=<n>|<list> on each zone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence

VERSION = "families-v1.0"

FAMILIES = ("AUCTION_VALUE", "STRUCTURE", "DELTA", "VOLUME", "GEX", "VWAP")
GEX_TOLERANCE_PTS = 10.0
DEFAULT_TOLERANCE_PTS = 5.0
MIN_FAMILIES_FOR_DECISION = 2

# level-name prefix -> family (names as the Book 1 map / Book 1A plan write them)
_PREFIX_FAMILY = {
    # auction value
    "WKVAH": "AUCTION_VALUE", "WKVAL": "AUCTION_VALUE", "PDVAH": "AUCTION_VALUE", "PDVAL": "AUCTION_VALUE",
    "ONVAH": "AUCTION_VALUE", "ONVAL": "AUCTION_VALUE", "PWKVAH": "AUCTION_VALUE", "PWKVAL": "AUCTION_VALUE",
    "HTFVAH": "AUCTION_VALUE", "HTFVAL": "AUCTION_VALUE", "BALVAH": "AUCTION_VALUE", "BALVAL": "AUCTION_VALUE",
    "ONTVAH": "AUCTION_VALUE", "ONTVAL": "AUCTION_VALUE",
    # structure
    "REJ": "STRUCTURE", "FLIP": "STRUCTURE", "DD_EDGE": "STRUCTURE", "PDH": "STRUCTURE", "PDL": "STRUCTURE",
    "PD2H": "STRUCTURE", "PD2L": "STRUCTURE", "PD3H": "STRUCTURE", "PD3L": "STRUCTURE", "ONH": "STRUCTURE",
    "ONL": "STRUCTURE", "WKH": "STRUCTURE", "WKL": "STRUCTURE", "SWING": "STRUCTURE",
    # delta
    "DELTA": "DELTA",
    # volume
    "WKPOC": "VOLUME", "PDPOC": "VOLUME", "ONPOC": "VOLUME", "HTFPOC": "VOLUME", "PWKPOC": "VOLUME", "HVN": "VOLUME",
    "LVN": "VOLUME", "TPO": "VOLUME", "SP": "VOLUME", "BALPOC": "VOLUME", "ONTPOC": "VOLUME", "PDTPOC": "VOLUME",
    # gex
    "CR": "GEX", "PS": "GEX", "HVL": "GEX", "0DTE": "GEX", "GAMMA": "GEX", "MQ_": "GEX", "GEX": "GEX",
    # vwap
    "WKVWAP": "VWAP", "VWAP": "VWAP",
}


def family_of(level_name: str) -> Optional[str]:
    """Map a level name to its family by prefix (longest prefix wins). None when unknown."""
    name = level_name.upper()
    best = None
    for pfx, fam in _PREFIX_FAMILY.items():
        if name.startswith(pfx) and (best is None or len(pfx) > len(best[0])):
            best = (pfx, fam)
    return None if best is None else best[1]


@dataclass(frozen=True)
class Level:
    name: str
    lo: float
    hi: float
    family: Optional[str] = None       # explicit family wins over the name prefix
    available_at: Optional[str] = None  # ISO timestamp (lookahead audit, P0.13)

    @staticmethod
    def point(name: str, price: float, family: Optional[str] = None, available_at: Optional[str] = None) -> "Level":
        return Level(name, price, price, family, available_at)

    def resolved_family(self) -> Optional[str]:
        return self.family or family_of(self.name)


def tolerance_for(family: str) -> float:
    return GEX_TOLERANCE_PTS if family == "GEX" else DEFAULT_TOLERANCE_PTS


def level_counts(zone_lo: float, zone_hi: float, level: Level, tolerance: Optional[float] = None) -> bool:
    """Inside the zone, or within the tolerance of either edge (band levels: any overlap)."""
    fam = level.resolved_family()
    if fam is None:
        return False
    tol = tolerance_for(fam) if tolerance is None else tolerance
    return level.hi >= zone_lo - tol and level.lo <= zone_hi + tol


@dataclass
class FamilyResult:
    zone_lo: float
    zone_hi: float
    families: List[str]
    levels: List[str]
    per_family: dict = field(default_factory=dict)

    @property
    def n_families(self) -> int:
        return len(self.families)

    @property
    def zone_class(self) -> str:
        return "DECISION" if self.n_families >= MIN_FAMILIES_FOR_DECISION else "TARGET"

    def families_field(self) -> str:
        return f"families={self.n_families}|{','.join(self.families)}"

    def levels_field(self) -> str:
        return f"levels={len(self.levels)}|{','.join(self.levels)}"


def count_families(zone_lo: float, zone_hi: float, levels: Iterable[Level],
                   own_families: Sequence[str] = (), gex_tolerance: float = GEX_TOLERANCE_PTS) -> FamilyResult:
    """families= / levels= for one zone.

    own_families: families the zone carries by construction (a REJ/FLIP zone is STRUCTURE; a
    MAP4 HVN area is VOLUME; a delta band zone is DELTA) even if no separate level record exists.
    """
    seen = {f: [] for f in FAMILIES}
    for f in own_families:
        if f not in seen:
            raise ValueError(f"unknown family {f}")
        seen[f].append("(zone)")
    kept: List[str] = []
    for lv in levels:
        fam = lv.resolved_family()
        if fam is None:
            continue
        tol = gex_tolerance if fam == "GEX" else tolerance_for(fam)
        if level_counts(zone_lo, zone_hi, lv, tol):
            seen[fam].append(lv.name)
            kept.append(lv.name)
    fams = [f for f in FAMILIES if seen[f]]
    return FamilyResult(zone_lo, zone_hi, fams, kept, {f: seen[f] for f in fams})
