"""Book 1A pre-trade dollar risk check, sizing and daily limits (checklist P0.10; replay plan C3 / U3).

Frozen settings (replay plan U3, Nov 1, 2026):
  simulated balance $100,000; per-trade budget 1% = $1,000; daily loss limit $2,000;
  NQ only, whole contracts, minimum 1 NQ; commission $5.74 round trip per NQ
  ($2.87 per side); slippage allowance 2 ticks per contract on the stop, used in the
  estimate only (never added to fills); NQ tick value $5.00.

Pre-trade formula (replay plan U3):
  estimated_risk = (stop_ticks + 2) x $5 x N + $5.74 x N
  N = the largest whole number with estimated_risk <= $1,000 and <= the remaining daily budget.
  Remaining daily budget = $2,000 - realized losses today - risk reserved by any open position.
  If even 1 NQ does not fit -> RISK_REJECT (never shrunk, never MNQ in the replay).
  A realized loss larger than the planned estimate -> RISK_BREACH_FILL (reported, never hidden).
  3 trades a day and the 2-loss halt stop the day too; whichever comes first.

All money is handled in integer cents so the boundary cases in the checklist are exact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

VERSION = "risk-v1.1"
# C3 implementation identifiers (Phase1/risk-c3-v2_registration.md, Kyron Nov 5, 2026, Option B)
C3_V1 = "risk-c3-v1"      # stop ticks from the signal-bar reference (Phase 0 / Phase 1 references; kept unchanged)
C3_V2 = "risk-c3-v2"      # stop ticks from the best ask (long) / best bid (short) at the decision; execution breach
C3_IMPLS = (C3_V1, C3_V2)
TICK = 0.25


@dataclass(frozen=True)
class RiskConfig:
    per_trade_budget_cents: int = 100_000        # $1,000
    daily_loss_limit_cents: int = 200_000        # $2,000
    tick_value_cents: int = 500                  # NQ $5.00 per tick
    commission_rt_cents: int = 574               # NQ $5.74 round trip ($2.87 per side)
    slippage_allowance_ticks: int = 2            # estimate only (fill model stress case)
    min_contracts: int = 1                       # NQ only, minimum 1 NQ
    max_contracts: int = 50                      # search bound only; never reached under $1,000
    max_trades_per_day: int = 3
    max_consecutive_losses: int = 2
    # AMBIGUITY (logged in the Phase 0 report): the replay plan says "realized losses today".
    # Literal reading: only losses reduce the daily budget; gains do not add it back.
    gains_restore_daily_budget: bool = False


DEFAULT = RiskConfig()


def estimate_risk_cents(stop_ticks: int, n: int, cfg: RiskConfig = DEFAULT) -> int:
    """(stop_ticks + allowance) x tick value x N + commission x N, in cents (exact)."""
    if stop_ticks < 0 or n < 0:
        raise ValueError("stop_ticks and n must be non-negative")
    return (stop_ticks + cfg.slippage_allowance_ticks) * cfg.tick_value_cents * n + cfg.commission_rt_cents * n


def estimate_risk(stop_ticks: int, n: int, cfg: RiskConfig = DEFAULT) -> float:
    """Same as estimate_risk_cents, in dollars."""
    return estimate_risk_cents(stop_ticks, n, cfg) / 100.0


def price_ticks(a: float, b: float) -> int:
    """|a - b| in whole ticks; both prices must be on the 0.25 grid."""
    x = abs(a - b) / TICK
    k = int(round(x))
    if abs(x - k) > 1e-6:
        raise ValueError(f"price distance {a} - {b} is not a whole number of ticks")
    return k


def entry_risk_at_fill_cents(fill: float, stop: float, filled: int, cfg: RiskConfig = DEFAULT):
    """risk-c3-v2 section 1: (|fill - stop| / 0.25 + 2) x $5 x filled + $5.74 x filled. Returns (ticks, cents)."""
    t = price_ticks(fill, stop)
    return t, estimate_risk_cents(t, filled, cfg)


def is_execution_breach(entry_risk_cents: int, budget_cents: int) -> bool:
    """Qualifying entry risk-budget breach: entry risk at fill > min($1,000, remaining daily at the decision)."""
    return entry_risk_cents > budget_cents


def largest_stop_that_fits(n: int, budget_cents: Optional[int] = None, cfg: RiskConfig = DEFAULT) -> int:
    """Largest stop (ticks) for which N contracts fit the budget (default: the per-trade budget)."""
    if budget_cents is None:
        budget_cents = cfg.per_trade_budget_cents
    per_contract = budget_cents // n if n > 0 else 0
    # (s + a) * tv + c <= budget / n   ->   s <= (budget/n - c) / tv - a
    s = (per_contract - cfg.commission_rt_cents) // cfg.tick_value_cents - cfg.slippage_allowance_ticks
    return max(s, -1)


def size_for(stop_ticks: int, budget_cents: int, cfg: RiskConfig = DEFAULT) -> int:
    """Largest whole N with estimated risk <= budget; 0 when even min_contracts does not fit."""
    n = 0
    for k in range(cfg.min_contracts, cfg.max_contracts + 1):
        if estimate_risk_cents(stop_ticks, k, cfg) <= budget_cents:
            n = k
        else:
            break
    return n


@dataclass
class RiskDecision:
    accepted: bool
    contracts: int
    stop_ticks: int
    estimated_risk_cents: int
    budget_cents: int                 # min(per-trade, remaining daily) at decision time
    remaining_daily_cents: int
    reason: str                       # ACCEPT | RISK_REJECT:<why> | HALT:<why>

    @property
    def estimated_risk(self) -> float:
        return self.estimated_risk_cents / 100.0

    def as_row(self) -> dict:
        return {
            "risk_decision": self.reason,
            "risk_contracts": self.contracts,
            "risk_stop_ticks": self.stop_ticks,
            "risk_estimate_usd": round(self.estimated_risk, 2),
            "risk_budget_usd": round(self.budget_cents / 100.0, 2),
            "risk_remaining_daily_usd": round(self.remaining_daily_cents / 100.0, 2),
        }


@dataclass
class DayRiskState:
    """Per-session state for the dollar daily limit, the 3-trade cap and the 2-loss halt."""
    cfg: RiskConfig = DEFAULT
    trades_entered: int = 0
    consecutive_losses: int = 0
    realized_losses_cents: int = 0        # sum of |loss| of losing trades (net of commission)
    realized_gains_cents: int = 0
    open_risk_cents: int = 0              # planned risk reserved by the open position
    open_contracts: int = 0
    halt_reason: Optional[str] = None     # TRADE_CAP | LOSS_HALT | DAILY_LIMIT
    breaches: list = field(default_factory=list)   # RISK_BREACH_FILL events (dicts)

    # ---- budget -------------------------------------------------------------------------
    def remaining_daily_cents(self) -> int:
        used = self.realized_losses_cents
        if self.cfg.gains_restore_daily_budget:
            used -= self.realized_gains_cents
        return self.cfg.daily_loss_limit_cents - used - self.open_risk_cents

    # ---- pre-trade check ----------------------------------------------------------------
    def pre_trade_check(self, stop_ticks: int) -> RiskDecision:
        cfg = self.cfg
        remaining = self.remaining_daily_cents()
        budget = min(cfg.per_trade_budget_cents, remaining)
        halt = self._halt_reason()
        if halt is not None:
            return RiskDecision(False, 0, stop_ticks, 0, budget, remaining, f"HALT:{halt}")
        if self.open_contracts > 0:
            return RiskDecision(False, 0, stop_ticks, 0, budget, remaining, "RISK_REJECT:IN_POSITION")
        est1 = estimate_risk_cents(stop_ticks, cfg.min_contracts, cfg)
        n = size_for(stop_ticks, budget, cfg)
        if n < cfg.min_contracts:
            why = "PER_TRADE_BUDGET" if est1 > cfg.per_trade_budget_cents else "DAILY_BUDGET"
            return RiskDecision(False, 0, stop_ticks, est1, budget, remaining, f"RISK_REJECT:{why}")
        return RiskDecision(True, n, stop_ticks, estimate_risk_cents(stop_ticks, n, cfg), budget, remaining, "ACCEPT")

    def _halt_reason(self) -> Optional[str]:
        cfg = self.cfg
        if self.halt_reason:
            return self.halt_reason
        if self.trades_entered >= cfg.max_trades_per_day:
            return "TRADE_CAP"
        if self.consecutive_losses >= cfg.max_consecutive_losses:
            return "LOSS_HALT"
        if self.realized_losses_cents >= cfg.daily_loss_limit_cents:
            return "DAILY_LIMIT"
        return None

    # ---- position lifecycle -------------------------------------------------------------
    def on_entry(self, decision: RiskDecision) -> None:
        if not decision.accepted:
            raise ValueError("on_entry needs an accepted decision")
        self.trades_entered += 1
        self.open_contracts = decision.contracts
        self.open_risk_cents = decision.estimated_risk_cents

    def on_exit(self, realized_net_pnl_cents: int, trade_id: str = "") -> Optional[dict]:
        """Record the realized net result (after commissions, all contracts). Returns a
        RISK_BREACH_FILL event when a loss exceeds the planned estimate, else None."""
        planned = self.open_risk_cents
        self.open_risk_cents = 0
        self.open_contracts = 0
        breach = None
        if realized_net_pnl_cents < 0:
            loss = -realized_net_pnl_cents
            self.realized_losses_cents += loss
            self.consecutive_losses += 1
            if loss > planned:
                breach = {"event": "RISK_BREACH_FILL", "trade_id": trade_id,
                          "planned_cents": planned, "realized_loss_cents": loss,
                          "overrun_cents": loss - planned}
                self.breaches.append(breach)
        else:
            self.realized_gains_cents += realized_net_pnl_cents
            self.consecutive_losses = 0
        # whichever limit comes first ends the day
        self.halt_reason = self._halt_reason()
        return breach
