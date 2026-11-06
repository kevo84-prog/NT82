"""P1.1: gamma ranks (U6). Rank strikes by the size of net GEX from the same D-1 option files the replica uses.

rank_strikes({strike: net_gex}) -> [(rank, strike, net_gex)] ordered by |net_gex| descending (gamma 1 = the
largest absolute net GEX; ties broken by the lower strike so the order is deterministic). Positive and negative
strikes rank together (the "size" of net GEX), as the Context doc's "rank strikes by the size of net GEX".
Signed ranks are also returned for the report (largest positive, largest negative).

available_at = D-1 23:00 ET, like every other calculated GEX level.
The per-strike net GEX comes from the Book 1 replica (gex_block1.py: mq_levels.compute_levels / gex_calc.cme_day)
on the PC; this module only ranks. compute_from_block1(...) is the hook for that, used by the PC script.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

VERSION = "gamma-ranks-v1.0"


def rank_strikes(net_gex: Dict[float, float], top: int = 5) -> List[Tuple[int, float, float]]:
    items = sorted(net_gex.items(), key=lambda kv: (-abs(kv[1]), kv[0]))
    return [(i + 1, float(k), float(v)) for i, (k, v) in enumerate(items[:top])]


def signed_ranks(net_gex: Dict[float, float], top: int = 3) -> Dict[str, List[Tuple[int, float, float]]]:
    pos = sorted(((k, v) for k, v in net_gex.items() if v > 0), key=lambda kv: (-kv[1], kv[0]))
    neg = sorted(((k, v) for k, v in net_gex.items() if v < 0), key=lambda kv: (kv[1], kv[0]))
    return {"positive": [(i + 1, float(k), float(v)) for i, (k, v) in enumerate(pos[:top])],
            "negative": [(i + 1, float(k), float(v)) for i, (k, v) in enumerate(neg[:top])]}


def as_levels(ranks: List[Tuple[int, float, float]], shift_pts: float = 0.0) -> Dict[str, float]:
    """gamma1.. levels for the plan (GEX family), shifted to the chart contract like the *_nt columns."""
    return {f"gamma{r}": s + shift_pts for r, s, _ in ranks}
