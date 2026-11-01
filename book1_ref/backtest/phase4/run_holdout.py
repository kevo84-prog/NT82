"""Phase 4 holdout: C1 (frozen, FROZEN_STRATEGY.md) and A0, replayed ONCE from the Phase 4 A0 strategy log.

Needs backtest\\phase4\\run from daily_loop.run(phase4_config.json) (A0 through the real harness, fill model v3.5).
Decision rule: FROZEN_STRATEGY.md, "Phase 4 decision rule" (C1's own net R per session > 0; bootstrap 5th percentile
> -0.10 R, seed 20251205, 10,000 resamples; max DD <= 1.5 x 4.58 R; no session below -400 net ticks after commission).
Reported only: C1 vs A0 paired, the 2-tick check, net ticks, months, gain split, Feb 17, A0's daily-limit breaks.
Run once from the project folder:  python backtest\\phase4\\run_holdout.py
"""
import collections, csv, json, subprocess, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
P3, P4 = ROOT / "backtest" / "phase3", ROOT / "backtest" / "phase4"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(P3))
from jeron_engine import arm_replay as ar, arms, phase_report, chart_check  # noqa: E402
import run_arms, final_combination as fc  # noqa: E402

OUT = P4 / "holdout"
SEED, N = 20251205, 10_000
P3_DD_C1 = 4.58
DAILY_LIMIT = -400.0


def boot_low(x):
    rng = np.random.default_rng(SEED)
    b = x[rng.integers(0, len(x), size=(N, len(x)))].mean(axis=1)
    return float(np.percentile(b, 5)), float(np.percentile(b, 95))


def per_day_ticks(trades, sessions):
    s = {d: 0.0 for d in sessions}
    for t in trades: s[t["date"]] += t["net_ticks"]
    return s


def main():
    global OUT, P4
    if "--dry-phase3" in sys.argv:
        # machinery check on Phase 3 data only (not a holdout result): Phase 3 run, sessions and bars
        P4, OUT = P3, Path(sys.argv[-1])
        sessions = json.load(open(P3 / "phase3_config.json"))["sessions"]
    else:
        sessions = json.load(open(P4 / "phase4_config.json"))["sessions"]
        assert len(sessions) == 52 and sessions[0] == "2026-02-05" and sessions[-1] == "2026-04-21"
        if (OUT / "holdout_decision.json").exists(): raise SystemExit("the holdout has already been run once: no rerun")
    OUT.mkdir(exist_ok=True)
    tag = subprocess.run(["git", "describe", "--tags", "--exact-match"], capture_output=True, text=True, cwd=ROOT).stdout.strip() or "untagged"
    print(f"Phase 4 holdout, code tag {tag}", flush=True)
    log, tape = run_arms.gate("A0", P4 / "run")
    bars = arms.MinuteBars(P4 / "run" / "tape_strategy.csv.gz")
    veto = fc.union([arms.fz1(log), arms.l1(log, 10.0), arms.t8(log, bars)])
    rt = dict(bars=bars, fail_ticks=2)
    a0, a02 = ar.replay(log, tape, None, "M0", "v3.5", 1), ar.replay(log, tape, None, "M0", "v3.5", 2)
    c1, c12 = ar.replay(log, tape, veto, "M0", "v3.5", 1, retest=rt), ar.replay(log, tape, veto, "M0", "v3.5", 2, retest=rt)

    # ---- the decision (FROZEN_STRATEGY.md)
    x = np.array(arms.per_session(c1["trades"], sessions))
    lo, hi = boot_low(x)
    dd = arms.max_dd(c1["trades"])
    ticks = per_day_ticks(c1["trades"], sessions)
    breaks = {d: round(v, 1) for d, v in ticks.items() if v < DAILY_LIMIT}
    tests = dict(mean_above_0=bool(x.mean() > 0), bound_above_minus_0_1=lo > -0.1, drawdown_within=bool(dd <= 1.5 * P3_DD_C1 + 1e-12),
                 no_daily_limit_break=not breaks)
    decision = dict(tag=tag, sessions=len(sessions), C1_trades=len(c1["trades"]), C1_net_R=round(float(x.sum()), 2),
                    C1_net_ticks=round(sum(t["net_ticks"] for t in c1["trades"]), 1),
                    C1_mean_R_per_session=round(float(x.mean()), 4), C1_ci90=[round(lo, 4), round(hi, 4)],
                    C1_max_dd_R=round(dd, 2), dd_limit_R=round(1.5 * P3_DD_C1, 2), C1_daily_limit_breaks=breaks,
                    C1_worst_day_net_ticks=round(min(ticks.values()), 1), tests=tests,
                    verdict="PASS" if all(tests.values()) else "FAIL")
    # ---- reported only
    pr = arms.promotion(c1, a0, sessions, c12, a02)
    a0t = per_day_ticks(a0["trades"], sessions)
    xa = np.array(arms.per_session(a0["trades"], sessions))
    a0_block = {e: ("" if r["RecordType"] == "ORDER" else r["Reasons"]) for e, r in log.attempts_logged.items()}
    months = []
    for m in sorted({d[:7] for d in sessions}):
        ss = [d for d in sessions if d[:7] == m]
        for name, res in (("C1", c1), ("A0", a0)):
            tr = [t for t in res["trades"] if t["date"][:7] == m]
            months.append(dict(month=m, variant=name, sessions=len(ss), trades=len(tr), wins=sum(1 for t in tr if t["R"] > 0),
                               net_R=round(sum(t["R"] for t in tr), 2), net_ticks=round(sum(t["net_ticks"] for t in tr), 1),
                               max_dd_R=round(arms.max_dd(tr), 2)))
    feb17 = {name: [dict(signal=t["signal_time"], side=t["side"], path=t["path"], reason=t["reason"], R=round(t["R"], 3),
                         net_ticks=round(t["net_ticks"], 1)) for t in res["trades"] if t["date"] == "2026-02-17"]
             for name, res in (("C1", c1), ("A0", a0))}
    plan17 = log.plans.get("2026-02-17", {})
    report = dict(
        C1_vs_A0_paired=dict(mean_per_session=round(pr["mean_diff_per_session"], 4), ci90=[round(pr["ci90_low"], 4), round(pr["ci90_high"], 4)],
                             differing=pr["differing"], two_tick_mean_per_session=round(pr["mean_diff_per_session_2tick"], 4),
                             C1_2tick_net_R=round(sum(t["R"] for t in c12["trades"]), 2), A0_2tick_net_R=round(sum(t["R"] for t in a02["trades"]), 2)),
        A0=dict(trades=len(a0["trades"]), net_R=round(float(xa.sum()), 2), net_ticks=round(sum(t["net_ticks"] for t in a0["trades"]), 1),
                mean_R_per_session=round(float(xa.mean()), 4), ci90=[round(v, 4) for v in boot_low(xa)], max_dd_R=round(arms.max_dd(a0["trades"]), 2),
                daily_limit_breaks={d: round(v, 1) for d, v in a0t.items() if v < DAILY_LIMIT}),
        gain_split=fc.split(c1["trades"], a0["trades"], a0_block),
        months=months,
        feb17=dict(plan_review=plan17.get("review"), plan_context=plan17.get("context"), gex_regime=plan17.get("gex_regime"),
                   no_trade=plan17.get("_no_trade"), trades=feb17),
        plan_status=dict(collections.Counter((log.plans.get(d) or {}).get("review", "missing") for d in sessions)),
        RH1_outcomes=dict(collections.Counter(r["outcome"] for r in c1["retests"])))
    json.dump(decision, open(OUT / "holdout_decision.json", "w"), indent=1, default=str)
    json.dump(report, open(OUT / "holdout_report.json", "w"), indent=1, default=str)
    for name, res in (("C1", c1), ("A0", a0), ("C1_2tick", c12), ("A0_2tick", a02)):
        run_arms.write_csv(OUT / f"trades_{name}.csv", res["trades"], f"Phase 4 holdout, {name}, tag {tag}")
    with open(OUT / "per_session.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["date", "C1_R", "A0_R", "C1_net_ticks", "A0_net_ticks"])
        for d, a, b in zip(sessions, x, xa): w.writerow([d, round(a, 4), round(b, 4), round(ticks[d], 1), round(a0t[d], 1)])
    run_arms.write_csv(OUT / "months.csv", months, f"Phase 4 holdout by month, tag {tag}")
    # A0 report card and chart check (the day after Presidents' Day included)
    card = OUT / "phase4_A0_report_card.md"
    phase_report.report(P4 / "run", card, "Phase 4 holdout (A0)")
    card.write_text(card.read_text(encoding="utf-8").replace("v3.4 fill model", "v3.5 fill model (Phase 4 config fill_model = v3.5)"), encoding="utf-8")
    cb = chart_check.load_bars(P4 / "nq_1m.csv", "2025-11-28", "2026-04-21")
    jofs = next((P4 / "run" / "strategy").glob("JOFS_*.csv")); rows = []
    for d in sessions: rows += chart_check.check_day(d, next((P4 / "run" / "map").glob(f"PreopenPacket_*_{d}.json")), jofs, cb)
    chart_check.write(rows, OUT / "phase4_chart_check.csv")
    print(json.dumps(decision, indent=1, default=str))
    print(json.dumps({k: v for k, v in report.items() if k != "months"}, indent=1, default=str))
    print("chart check not ok:", [(r["date"], r["kind"], r["item"], r["ours"], r["chart"]) for r in rows if not r["ok"]])


if __name__ == "__main__":
    main()
