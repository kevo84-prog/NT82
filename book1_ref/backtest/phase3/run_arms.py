"""Phase 3: A0 and the 8 approved arms (phase3_change_list_APPROVED.md, approved Oct 26, 2026, Amendment 1 Oct 26, 2026).

Needs the two strategy runs first: backtest\\phase3\\run (A0, phase3_config.json) and backtest\\phase3\\run_RT0
(phase3_config_RT0.json, RetriggerBars=0). Everything is fill model v3.5, 1 tick of stop slippage; the 2-tick check
pairs each arm at 2 ticks with A0 at 2 ticks.

Gates (stop on failure): for each strategy run, the replay with no veto (M0, v3.4) reproduces the logged order
attempts, block reasons, decision ticks, trades and fills (fill ledger rerun under v3.4); the per-bar ranking picks
the logged winner in every group. Then A0 = replay(no veto, M0, v3.5); its trades are compared with fills_model.csv
(v3.5 ledger) and every difference is listed.
Arms: M2E (exit model, crossed = reject and keep), A7, L1 (10 pts), RT0 (RetriggerBars=0 strategy run, replayed with
no veto), FZ1 ((a) No, (b) Yes), T8, G1, RH1 (2-tick fail). Report-only lines (never promoted): M2E market exit on a
change crossed on arrival, L1 at 5 and 20 pts, RH1 with an 8-tick fail, RH1 split by gamma regime.
Promotion: arms.promotion (seed 20251205, 10,000 resamples, 5th percentile > 0, DD <= 1.25 x A0, >= 20 differing,
2-tick >= 0). Win rate is reported, never used.
Run from the project folder:  python backtest\\phase3\\run_arms.py
"""
import collections, csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from jeron_engine import arm_replay as ar, arms, daily_loop, fills  # noqa: E402

P3 = ROOT / "backtest" / "phase3"
RUN, RUN_RT0 = P3 / "run", P3 / "run_RT0"
OUT = P3 / "arm_results"
PRIMARY = ["M2E", "A7", "L1", "RT0", "FZ1", "T8", "G1", "RH1"]


def gate(name, run):
    log = ar.Log(run)
    tape = fills.Tape(run / "tape_strategy.csv.gz")
    jofs = next((run / "strategy").glob("JOFS_*.csv"))
    v34 = run / "fills_model_v34.csv"
    if not v34.exists(): daily_loop.fill_ledger(jofs, run / "tape_strategy.csv.gz", v34, "v3.4")
    rep, problems = ar.check_a0(log, tape, v34)
    groups = log.groups()
    bad = sum(1 for g in groups if max(g, key=lambda r: ar.rank_key(log, r)) is not g[0])
    print(f"Gate {name}: {len(rep['attempts'])} attempts, {len(rep['trades'])} trades (v3.4), problems {len(problems)}; "
          f"ranking {len(groups)} groups, {bad} different winners")
    for p in problems[:20]: print("   ", p)
    for p in rep.get("halt_label_diffs", []): print("    halt name only (same block):", p)
    if problems or bad: raise SystemExit(f"gate failed on {name}: stop here")
    return log, tape


def write_csv(path, rows, header=None):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        if header: fh.write(f"# {header}\n")
        if not rows: return
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if isinstance(rows[0], dict) else None); w.writeheader(); w.writerows(rows)


def key(t): return (t["date"], t["signal_time"])


def row(name, arm, arm2, a0, a02, sessions, role):
    pr = arms.promotion(arm, a0, sessions, arm2, a02)
    A = {key(t): t for t in a0["trades"]}; B = {key(t): t for t in arm["trades"]}
    removed = [A[k] for k in A if k not in B]; admitted = [B[k] for k in B if k not in A]
    tr = arm["trades"]
    return dict(arm=name, role=role, verdict=pr["verdict"] if role == "arm" else "report only",
                trades=len(tr), wins=sum(1 for t in tr if t["R"] > 0),
                win_rate=round(sum(1 for t in tr if t["R"] > 0) / len(tr), 3) if tr else 0.0,
                net_R=round(sum(t["R"] for t in tr), 2), net_R_2tick=round(sum(t["R"] for t in arm2["trades"]), 2),
                per_session_vs_A0=round(pr["mean_diff_per_session"], 3), ci90_low=round(pr["ci90_low"], 3),
                ci90_high=round(pr["ci90_high"], 3), max_dd=round(pr["max_dd_arm"], 2), max_dd_limit=round(1.25 * pr["max_dd_a0"], 2),
                per_session_vs_A0_2tick=round(pr["mean_diff_per_session_2tick"], 3),
                diff_removed=pr["differing"]["removed"], diff_admitted=pr["differing"]["admitted"],
                diff_exited_differently=pr["differing"]["exited_differently"], diff_total=pr["differing"]["total"],
                removed_L=sum(1 for t in removed if t["R"] <= 0), removed_W=sum(1 for t in removed if t["R"] > 0),
                removed_R=round(sum(t["R"] for t in removed), 2),
                admitted_L=sum(1 for t in admitted if t["R"] <= 0), admitted_W=sum(1 for t in admitted if t["R"] > 0),
                admitted_R=round(sum(t["R"] for t in admitted), 2),
                check_bound=pr["checks"]["bound"], check_drawdown=pr["checks"]["drawdown"],
                check_sample=pr["checks"]["sample"], check_two_tick=pr["checks"]["two_tick"])


def main():
    global RUN, RUN_RT0, OUT
    if "--dry-phase2" in sys.argv:
        # machinery check on Phase 2 (A0's run stands in for RT0's); output to the given folder, not a Phase 3 result
        RUN = RUN_RT0 = ROOT / "backtest" / "phase2" / "run"; OUT = Path(sys.argv[-1])
        sessions = json.load(open(ROOT / "backtest" / "phase2" / "phase2_config.json"))["sessions"]
    else:
        sessions = json.load(open(P3 / "phase3_config.json"))["sessions"]
        assert len(sessions) == 41 and sessions[0] == "2025-12-05" and sessions[-1] == "2026-02-04"
    OUT.mkdir(exist_ok=True)
    tag = subprocess.run(["git", "describe", "--tags", "--exact-match"], capture_output=True, text=True, cwd=ROOT).stdout.strip() or "untagged"
    print(f"Phase 3 arm run, code tag {tag}")
    log, tape = gate("A0", RUN)
    log_rt0, tape_rt0 = gate("RT0", RUN_RT0)
    bars = arms.MinuteBars(RUN / "tape_strategy.csv.gz")

    def both(lg=log, tp=tape, veto=None, **kw):
        return ar.replay(lg, tp, veto, stop_slip=1, **kw), ar.replay(lg, tp, veto, stop_slip=2, **kw)

    a0, a02 = both()
    # A0 replay vs the v3.5 fill ledger
    fm = {r["event"]: r for r in csv.DictReader(open(RUN / "fills_model.csv", encoding="utf-8"))}
    ev = {t["event"]: t for t in a0["trades"]}
    a0_vs_ledger = dict(replay_trades=len(ev), ledger_trades=len(fm), only_in_replay=sorted(set(ev) - set(fm)),
                        only_in_ledger=sorted(set(fm) - set(ev)),
                        fill_differs=sorted(e for e in set(ev) & set(fm) if abs(ev[e]["entry"] - float(fm[e]["base_entry"])) > 1e-9
                                            or abs(ev[e]["exit"] - float(fm[e]["base_exit"])) > 1e-9))
    print("A0 replay vs fills_model.csv (v3.5):", json.dumps(a0_vs_ledger))

    runs = {"A0": (a0, a02, "baseline")}
    runs["M2E"] = both(exit_model="M2E") + ("arm",)
    runs["M2E_market_exit"] = both(exit_model="M2E", crossed="live_market") + ("report only",)
    runs["A7"] = both(veto=arms.a7(log)) + ("arm",)
    runs["L1"] = both(veto=arms.l1(log, 10.0)) + ("arm",)
    runs["L1_5pt"] = both(veto=arms.l1(log, 5.0)) + ("report only",)
    runs["L1_20pt"] = both(veto=arms.l1(log, 20.0)) + ("report only",)
    runs["RT0"] = both(lg=log_rt0, tp=tape_rt0) + ("arm",)
    runs["FZ1"] = both(veto=arms.fz1(log)) + ("arm",)
    runs["T8"] = both(veto=arms.t8(log, bars)) + ("arm",)
    runs["G1"] = both(veto=arms.g1(log)) + ("arm",)
    runs["RH1"] = both(retest=dict(bars=bars, fail_ticks=2)) + ("arm",)
    runs["RH1_fail8"] = both(retest=dict(bars=bars, fail_ticks=8)) + ("report only",)

    rows = [row(k, v[0], v[1], a0, a02, sessions, v[2]) for k, v in runs.items()]
    write_csv(OUT / "phase3_arm_results.csv", rows, f"Phase 3 ({len(sessions)} sessions), fill model v3.5, code tag {tag}")
    for k, v in runs.items():
        write_csv(OUT / f"trades_{k}.csv", v[0]["trades"], f"Phase 3, {k}, 1-tick stop slippage, tag {tag}")
    for k in ("RH1", "RH1_fail8"):
        rt = runs[k][0]["retests"]
        flds = sorted({f for x in rt for f in x})
        write_csv(OUT / f"retests_{k}.csv", [{f: x.get(f, "") for f in flds} for x in rt], f"Phase 3, {k} retest outcomes, tag {tag}")

    # details: overlaps, RH1 outcomes and the gamma split (report only), regimes, per-session series
    cand = {r["EventId"]: r for r in log.rows if r["RecordType"] == "CANDIDATE"}
    traded = [cand[t["event"]] for t in a0["trades"]]
    vet = {"A7": arms.a7(log), "L1": arms.l1(log, 10.0), "FZ1": arms.fz1(log), "T8": arms.t8(log, bars), "G1": arms.g1(log)}
    hit = {k: {r["EventId"] for r in traded if v(r)} for k, v in vet.items()}
    rt0_keys = {key(t) for t in runs["RT0"][0]["trades"]}
    hit["RT0_absent"] = {t["event"] for t in a0["trades"] if key(t) not in rt0_keys}
    regimes = collections.Counter((log.plans.get(d) or {}).get("gex_regime", "missing") for d in sessions)
    split = {}
    for reg in ("NEG", "POS", "UNKNOWN"):
        days = {d for d in sessions if (log.plans.get(d) or {}).get("gex_regime") == reg}
        split[reg] = dict(sessions=len(days), RH1_net_R=round(sum(t["R"] for t in runs["RH1"][0]["trades"] if t["date"] in days), 2),
                          A0_net_R=round(sum(t["R"] for t in a0["trades"] if t["date"] in days), 2))
    status = collections.Counter()
    for d in sessions:
        p = log.plans.get(d) or {}
        status[p.get("review", "missing")] += 1
    details = dict(
        tag=tag, sessions=len(sessions), a0_vs_ledger=a0_vs_ledger, plan_status=dict(status), gex_regimes=dict(regimes),
        vetoes_on_a0_trades={k: len(v) for k, v in hit.items()},
        overlap_on_a0_trades={f"{a}&{b}": len(hit[a] & hit[b]) for i, a in enumerate(hit) for b in list(hit)[i + 1:]},
        G1_overlap=dict(g1=len(hit["G1"]), also_FZ1=len(hit["G1"] & hit["FZ1"]), also_L1=len(hit["G1"] & hit["L1"]),
                        all_three=len(hit["G1"] & hit["FZ1"] & hit["L1"]), only_G1=len(hit["G1"] - hit["FZ1"] - hit["L1"])),
        RH1_outcomes={k: dict(collections.Counter(x["outcome"] for x in runs[k][0]["retests"])) for k in ("RH1", "RH1_fail8")},
        RH1_runners_missed={k: sum(1 for x in runs[k][0]["retests"] if x["runner_missed"]) for k in ("RH1", "RH1_fail8")},
        RH1_entries_blocked={k: sum(1 for x in runs[k][0]["retests"] if x.get("entry_blocks")) for k in ("RH1", "RH1_fail8")},
        RH1_regime_split_report_only=split,
        per_session={k: arms.per_session(v[0]["trades"], sessions) for k, v in runs.items()})
    json.dump(details, open(OUT / "details.json", "w"), indent=1, default=str)
    for r in rows: print({k: r[k] for k in ("arm", "role", "verdict", "trades", "net_R", "per_session_vs_A0", "ci90_low", "ci90_high",
                                         "max_dd", "max_dd_limit", "per_session_vs_A0_2tick", "diff_total")})
    print(json.dumps({k: v for k, v in details.items() if k != "per_session"}, indent=1, default=str))


if __name__ == "__main__":
    main()
