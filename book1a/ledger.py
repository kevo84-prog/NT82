"""Book 1A trade ledger, R reporting and the checker hand-off CSV (checklist P0.4, P0.12).

Per trade (replay plan 4a, R reporting):
  theoretical R   = price move / stop distance (sign by side), independent of size
  realized net R  = realized net dollars (fills incl. slippage, minus commission on every contract)
                    / (stop distance in ticks x $5 x N)   [Book 1 convention: the denominator is the
                    planned stop distance; commission $5.74 round trip = 1.148 NQ ticks per contract]
  contracts N recorded on every trade (R1/R2 keep their original sizing, qty 1).

Checker hand-off CSV (P0.4): date, entry time, side, qty, entry price, stop, target, exit time,
exit price, exit reason, risk decision. One file per strategy. The runner never compares them.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, asdict, field
from typing import Iterable, List, Optional

VERSION = "ledger-v1.1"
TICK = 0.25
TICK_VALUE = 5.0
COMMISSION_PER_SIDE = 2.87

CHECKER_COLUMNS = ["date", "entry_time", "side", "qty", "entry_price", "stop", "target",
                   "exit_time", "exit_price", "exit_reason", "risk_decision"]

LEDGER_COLUMNS = CHECKER_COLUMNS + ["strategy", "trade_id", "stop_ticks", "theoretical_R", "gross_usd",
                                    "commission_usd", "net_usd", "realized_net_R", "planned_risk_usd",
                                    "risk_breach_fill", "fill_model", "stop_slippage_ticks", "entry_latency_ms"]


def ticks(a: float, b: float) -> int:
    """|a - b| in whole ticks (prices are on the tick grid)."""
    return int(round(abs(a - b) / TICK))


@dataclass
class Trade:
    strategy: str
    trade_id: str
    date: str
    entry_time: str
    side: str                 # LONG | SHORT
    qty: int
    entry_price: float
    stop: float
    target: float
    exit_time: str
    exit_price: float
    exit_reason: str          # TARGET_FIRST | STOP_FIRST | TIME_EXIT | UNKNOWN
    risk_decision: str = "ACCEPT"      # ACCEPT | RISK_REJECT:<why> | N/A (R1/R2 original sizing)
    planned_risk_usd: Optional[float] = None
    fill_model: str = "v3.4"
    stop_slippage_ticks: int = 1
    entry_latency_ms: int = 250
    risk_breach_fill: bool = False     # realized loss overrun (never the Phase 4 gate)
    extra: dict = field(default_factory=dict)   # extra ledger columns (risk-c3-v2); written only when asked for

    # ---- derived ---------------------------------------------------------------------------
    @property
    def sign(self) -> int:
        return 1 if self.side.upper() == "LONG" else -1

    @property
    def stop_ticks(self) -> int:
        return ticks(self.entry_price, self.stop)

    @property
    def move_ticks(self) -> int:
        return int(round(self.sign * (self.exit_price - self.entry_price) / TICK))

    @property
    def theoretical_R(self) -> Optional[float]:
        if self.stop_ticks == 0:
            return None
        return self.move_ticks / self.stop_ticks

    @property
    def gross_usd(self) -> float:
        return self.move_ticks * TICK_VALUE * self.qty

    @property
    def commission_usd(self) -> float:
        return 2 * COMMISSION_PER_SIDE * self.qty

    @property
    def net_usd(self) -> float:
        return self.gross_usd - self.commission_usd

    @property
    def realized_net_R(self) -> Optional[float]:
        denom = self.stop_ticks * TICK_VALUE * self.qty
        if denom == 0:
            return None
        return self.net_usd / denom

    def as_ledger_row(self) -> dict:
        d = {k: getattr(self, k) for k in CHECKER_COLUMNS}
        d.update({"strategy": self.strategy, "trade_id": self.trade_id, "stop_ticks": self.stop_ticks,
                  "theoretical_R": None if self.theoretical_R is None else round(self.theoretical_R, 4),
                  "gross_usd": round(self.gross_usd, 2), "commission_usd": round(self.commission_usd, 2),
                  "net_usd": round(self.net_usd, 2),
                  "realized_net_R": None if self.realized_net_R is None else round(self.realized_net_R, 4),
                  "planned_risk_usd": self.planned_risk_usd, "risk_breach_fill": int(self.risk_breach_fill),
                  "fill_model": self.fill_model, "stop_slippage_ticks": self.stop_slippage_ticks,
                  "entry_latency_ms": self.entry_latency_ms})
        return d

    def as_checker_row(self) -> dict:
        return {k: getattr(self, k) for k in CHECKER_COLUMNS}


def write_csv(path: str, rows: Iterable[dict], columns: List[str]) -> int:
    n = 0
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r); n += 1
    return n


def write_checker_ledger(path: str, trades: Iterable[Trade]) -> int:
    """The P0.4 hand-off file: checker columns only, sorted by date and entry time."""
    rows = sorted((t.as_checker_row() for t in trades), key=lambda r: (r["date"], r["entry_time"]))
    return write_csv(path, rows, CHECKER_COLUMNS)


def write_ledger(path: str, trades: Iterable[Trade], extra_columns: List[str] = ()) -> int:
    """extra_columns empty = the original layout (byte for byte as ledger-v1.0)."""
    rows = sorted(({**t.as_ledger_row(), **t.extra} for t in trades), key=lambda r: (r["date"], r["entry_time"]))
    return write_csv(path, rows, LEDGER_COLUMNS + list(extra_columns))
