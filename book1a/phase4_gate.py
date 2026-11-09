r"""Book 1A Phase 4 replay rule (replay plan section 9) for R3 and R4, and the section 9 go / no-go mapping.

Written Nov 9, 2026 (Phase 4 Step A), before any Phase 4 run; tested on synthetic ledgers only
(book1a/tests/test_phase4_gate.py). Registered in Book1A/Phase4/Phase4_registration.md section 5.

  python -m book1a.phase4_gate --r1 <R1 ledger> --r2 <R2 ledger> --r3 <R3 ledger> --r4 <R4 ledger> \
      --phase3-card book1a\Phase3\runs\phase3_report_card.json --out book1a\Phase4\runs\phase4_gate\phase4_gate.json

Replay plan section 9, "Phase 4 replay rule", applied to R3 and R4 (R1 and R2 reported, not gated):
  1. net R per session > 0                   mean over the population's sessions of the session net R (sum of the
                                             session's trade realized_net_R, 0 when no trade) - phase2_report.daily_table;
  2. 90% bootstrap lower bound > -0.1 R      session bootstrap of that mean, numpy default_rng(20251205), B = 10,000,
                                             lower bound = 5th percentile (Book 1's convention, Phase3_registration.md
                                             section 5) - phase2_report.bootstrap_ci;
  3. max drawdown <= 1.5 x Phase 3           realized net R over trades in (session, entry time) order from a peak of 0
                                             (phase2_report.max_drawdown, the report card's max_drawdown_R), against
                                             1.5 x the Phase 3 ALL max_drawdown_R of the same strategy (R3 4.5862, R4
                                             5.3103, from book1a/Phase3/runs/phase3_report_card.json; the card is read
                                             and must equal these values);
  4. planned-risk violations = 0             (E3) an accepted trade whose planned_risk_usd is above risk_budget_usd
                                             (= min($1,000, remaining daily budget at the decision), risk-c3-v2);
  5. execution breaches (risk-c3-v2)         qualifying breach = ledger exec_risk_breach 1 (entry risk at fill above
                                             risk_budget_usd); overrun = entry_risk_at_fill_usd - risk_budget_usd; fail
                                             if more than 1 breach or any overrun above 25% of the $2,000 daily limit
                                             ($500). Realized loss overrun (RISK_BREACH_FILL) is reported, never gated.
  PASS = all five. Population: ALL sessions decide; UNEXPOSED (phase2_report.EXPOSED_BY_PHASE["phase4"]) is a
  sensitivity only (label SENSITIVE_TO_EXPOSED_SESSIONS when the two differ; the ALL result stays the decision).
Go / no-go (section 9, as written): R4 passes -> Book 1A goes to Block 2; only R3 passes -> C1 with risk controls goes
to Block 2, not Book 1A; both -> both, as separately frozen candidates; neither -> no Block 2 data is bought solely for
validation; record why, and research on Block 1 diagnostics first. A replay pass is a reason to test on Block 2, never
proof the strategy works.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

from book1a import phase2_report as RP, sessions as S

VERSION = "phase4-gate-v1.0"
PHASE = "phase4"
GATED = ("R3", "R4")
REPORTED = ("R1", "R2")
LB_MIN = -0.1
DD_FACTOR = 1.5
PHASE3_DD_R = {"R3": 4.5862, "R4": 5.3103}          # Phase 3 report card, ALL, max_drawdown_R (registered)
DAILY_LIMIT_USD = 2000.0
MAX_EXEC_BREACHES = 1
MAX_OVERRUN_USD = 0.25 * DAILY_LIMIT_USD             # $500
EPS = 1e-9
GO_NO_GO = {
    (True, True): "BOTH: R4 (Book 1A) and R3 (C1 + risk) go to Block 2, as separately frozen candidates",
    (False, True): "R4: Book 1A goes to Block 2 (E4)",
    (True, False): "R3 ONLY: C1 with risk controls goes to Block 2, not Book 1A (C1 includes FZ1, which is not Jeron)",
    (False, False): "NEITHER: no Block 2 data is bought solely for validation; record why, and research on Block 1 diagnostics first",
}
LABEL = "replay (in-sample); a replay pass is a reason to test on Block 2, never proof the strategy works"


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stats(trades: List[dict], sessions: Sequence[dt.date]) -> dict:
    tr = RP.in_pop(trades, sessions)
    sv = [x["net_R"] for x in RP.daily_table(tr, sessions)]
    lo, hi = RP.bootstrap_ci(sv)
    rs = [RP.trade_r(t) for t in tr]
    ws = RP.win_stats(rs)
    return dict(sessions=len(sessions), trades=len(tr), wins=ws["wins"], losses=ws["losses"], zero=ws["zero"],
                net_R_per_session=float(np.mean(sv)) if sv else None, ci90=[lo, hi], max_drawdown_R=RP.max_drawdown(rs),
                net_usd=round(sum(RP.fnum(t["net_usd"]) for t in tr), 2) if all(t.get("net_usd") not in (None, "") for t in tr) else None)


def risk_checks(trades: List[dict]) -> dict:
    viol = [t["trade_id"] for t in trades if RP.fnum(t["planned_risk_usd"]) > RP.fnum(t["risk_budget_usd"]) + EPS]
    ex = [t for t in trades if str(t.get("exec_risk_breach", "0")) == "1"]
    over = [RP.fnum(t["entry_risk_at_fill_usd"]) - RP.fnum(t["risk_budget_usd"]) for t in ex]
    bf = [t for t in trades if str(t.get("risk_breach_fill", "0")) == "1"]
    return dict(planned_risk_violations=len(viol), planned_risk_violation_ids=viol, exec_breaches=len(ex),
                exec_breach_ids=[t["trade_id"] for t in ex], exec_largest_overrun_usd=round(max(over), 2) if over else None,
                risk_breach_fill=len(bf),
                risk_breach_fill_largest_overrun_usd=round(max(-RP.fnum(t["net_usd"]) - RP.fnum(t["planned_risk_usd"]) for t in bf), 2) if bf else None)


def evaluate(strategy: str, trades: List[dict], sessions: Sequence[dt.date], phase3_dd: float) -> dict:
    s = stats(trades, sessions)
    rk = risk_checks(RP.in_pop(trades, sessions))
    lim = DD_FACTOR * phase3_dd
    checks = dict(
        net_R_per_session_above_0=s["net_R_per_session"] is not None and s["net_R_per_session"] > 0,
        ci90_lower_above_minus_0_1=s["ci90"][0] is not None and s["ci90"][0] > LB_MIN,
        max_drawdown_within_1_5x_phase3=s["max_drawdown_R"] <= lim + EPS,
        zero_planned_risk_violations=rk["planned_risk_violations"] == 0,
        exec_breaches_within_gate=rk["exec_breaches"] <= MAX_EXEC_BREACHES
        and (rk["exec_largest_overrun_usd"] is None or rk["exec_largest_overrun_usd"] <= MAX_OVERRUN_USD + EPS),
    )
    return dict(strategy=strategy, **s, **rk, phase3_max_drawdown_R=phase3_dd, max_drawdown_limit_R=round(lim, 6),
                checks=checks, result="PASS" if all(checks.values()) else "FAIL")


def go_no_go(r3_pass: bool, r4_pass: bool) -> str:
    return GO_NO_GO[(bool(r3_pass), bool(r4_pass))]


def check_phase3_card(path) -> dict:
    card = json.loads(Path(path).read_text(encoding="utf-8"))
    got = {s: card["cards"][s]["ALL"]["max_drawdown_R"] for s in GATED}
    if any(abs(got[s] - PHASE3_DD_R[s]) > EPS for s in GATED):
        raise RuntimeError(f"Phase 3 card drawdowns {got} differ from the registered {PHASE3_DD_R}")
    return dict(path=str(path), sha256=sha(path), max_drawdown_R_ALL=got)


def run(ledgers: Dict[str, str], phase3_card: str, out: str) -> dict:
    sess = S.phase_sessions(PHASE)
    pops = RP.populations(sess, PHASE)
    p3 = check_phase3_card(phase3_card)
    res = dict(version=VERSION, label=LABEL, phase=PHASE, phase3_card=p3,
               populations={k: dict(sessions=len(v), dates=[d.isoformat() for d in v]) for k, v in pops.items()},
               inputs={s: dict(path=str(p), sha256=sha(p)) for s, p in ledgers.items()}, gated={}, reported={})
    rows = {s: RP.read_csv(p) for s, p in ledgers.items()}
    for s, tr in rows.items():
        dates = {RP.entry_session(t) for t in tr}
        if not dates <= set(sess):
            raise RuntimeError(f"{s}: trades outside the Phase 4 sessions {sorted(dates - set(sess))}")
    for s in GATED:
        res["gated"][s] = {k: evaluate(s, rows[s], v, PHASE3_DD_R[s]) for k, v in pops.items()}
        a, u = res["gated"][s]["ALL"]["result"], res["gated"][s]["UNEXPOSED"]["result"]
        res["gated"][s]["decision"] = a
        res["gated"][s]["sensitivity"] = "SAME_RESULT" if a == u else "SENSITIVE_TO_EXPOSED_SESSIONS"
    for s in REPORTED:
        if s in rows:
            res["reported"][s] = {k: stats(rows[s], v) for k, v in pops.items()}
    res["go_no_go"] = go_no_go(res["gated"]["R3"]["decision"] == "PASS", res["gated"]["R4"]["decision"] == "PASS")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    for s in ("r1", "r2", "r3", "r4"):
        ap.add_argument(f"--{s}", required=s in ("r3", "r4"))
    ap.add_argument("--phase3-card", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    led = {s.upper(): getattr(a, s) for s in ("r1", "r2", "r3", "r4") if getattr(a, s)}
    res = run(led, a.phase3_card, a.out)
    for s in GATED:
        print(s, res["gated"][s]["decision"], res["gated"][s]["sensitivity"])
    print("go / no-go:", res["go_no_go"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
