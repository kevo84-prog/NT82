"""Phase 3 final-combination replay (design line 329), as declared in final_combination_DECLARATION.md.

Combination C1 = A0 + FZ1 + L1 + T8 + RH1, replayed as one strategy over the 41 Phase 3 sessions from A0's strategy log
(candidate generation does not depend on position, trades, halts or the 3-trade limit: declaration, step 2).
- The vetoes (FZ1, L1 10 pts, T8) apply first: a candidate any of them vetoes is removed from the pool before the
  per-bar selection (a surviving shadow can win the bar).
- Surviving INITIATION candidates that reach an order attempt with no block then go through the RH1 retest
  (2-tick fail; the slot is held while armed). RESPONSE candidates enter as in A0.
- Exit M0, MAP0 (A0's plans), fill model v3.5, 1 tick of stop slippage; 2-tick check vs A0 at 2 ticks.
Frozen promotion rule vs A0. If a combination fails, the arm with the weakest single per-session result is dropped
and the rest replayed: C2 = without T8 (+0.147), C3 = also without L1 (+0.360), C4 = also without FZ1 (+0.796), i.e.
RH1 alone. The first combination that passes is the frozen strategy. Every step is reported.
Run from the project folder:  python backtest\\phase3\\final_combination.py
"""
import collections, csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).resolve().parent))
from jeron_engine import arm_replay as ar, arms  # noqa: E402
import run_arms  # noqa: E402

P3 = ROOT / "backtest" / "phase3"
OUT = P3 / "combination"
STEPS = [("C1", ["FZ1", "L1", "T8"], True), ("C2", ["FZ1", "L1"], True), ("C3", ["FZ1"], True), ("C4", [], True)]


def union(vs):
    if not vs: return None
    return lambda r: any(v(r) for v in vs)


def key(t): return (t["date"], t["signal_time"])


def split(arm, a0, a0_block):
    A = {key(t): t for t in a0}; B = {key(t): t for t in arm}
    removed = [A[k] for k in A if k not in B]; admitted = [B[k] for k in B if k not in A]
    changed = [(A[k], B[k]) for k in A if k in B and abs(A[k]["R"] - B[k]["R"]) > 1e-9]
    why = collections.defaultdict(lambda: [0, 0.0])
    for t in admitted:
        rs = a0_block.get(t["event"])
        if rs is None: w = "not selected in A0 (another candidate won its bar)"
        else:
            s = set(rs.split("|")); parts = []
            if s & {"LOSS_STREAK_LIMIT", "DAILY_LOSS_LIMIT"}: parts.append("A0 halted")
            if "MAX_TRADES_REACHED" in s: parts.append("A0 at its trade limit")
            if "ALREADY_IN_TRADE" in s: parts.append("A0 already in a trade")
            w = " + ".join(parts) or "other A0 block: " + rs
        why[w][0] += 1; why[w][1] += t["R"]
    saved = -sum(t["R"] for t in removed if t["R"] <= 0); lost = sum(t["R"] for t in removed if t["R"] > 0)
    adm = sum(t["R"] for t in admitted); chg = sum(b["R"] - a["R"] for a, b in changed)
    total = sum(t["R"] for t in arm) - sum(t["R"] for t in a0)
    assert abs(saved - lost + adm + chg - total) < 1e-6
    return dict(gain_vs_A0=round(total, 2), blocked_losers=sum(1 for t in removed if t["R"] <= 0), R_saved=round(saved, 2),
                blocked_winners=sum(1 for t in removed if t["R"] > 0), R_lost=round(-lost, 2),
                admitted=len(admitted), admitted_W=sum(1 for t in admitted if t["R"] > 0), R_admitted=round(adm, 2),
                changed_same_signal=len(changed), R_changed=round(chg, 2),
                admitted_why={k: [v[0], round(v[1], 2)] for k, v in sorted(why.items())})


def main():
    OUT.mkdir(exist_ok=True)
    sessions = json.load(open(P3 / "phase3_config.json"))["sessions"]
    assert len(sessions) == 41 and sessions[-1] == "2026-02-04"
    tag = subprocess.run(["git", "describe", "--tags", "--exact-match"], capture_output=True, text=True, cwd=ROOT).stdout.strip() or "untagged"
    print(f"Final-combination replay, code tag {tag}")
    log, tape = run_arms.gate("A0", P3 / "run")
    bars = arms.MinuteBars(P3 / "run" / "tape_strategy.csv.gz")
    V = {"FZ1": arms.fz1(log), "L1": arms.l1(log, 10.0), "T8": arms.t8(log, bars)}
    a0, a02 = ar.replay(log, tape, None, "M0", "v3.5", 1), ar.replay(log, tape, None, "M0", "v3.5", 2)
    a0_block = {e: ("" if r["RecordType"] == "ORDER" else r["Reasons"]) for e, r in log.attempts_logged.items()}
    rows, final = [], None
    for name, vs, rh in STEPS:
        veto = union([V[v] for v in vs])
        rt = dict(bars=bars, fail_ticks=2) if rh else None
        c1, c2 = ar.replay(log, tape, veto, "M0", "v3.5", 1, retest=rt), ar.replay(log, tape, veto, "M0", "v3.5", 2, retest=rt)
        r = run_arms.row(name, c1, c2, a0, a02, sessions, "arm")
        r["arms"] = "+".join(["RH1"] + vs)
        r.update({f"split_{k}": (json.dumps(v) if isinstance(v, dict) else v) for k, v in split(c1["trades"], a0["trades"], a0_block).items()})
        rows.append(r)
        run_arms.write_csv(OUT / f"trades_{name}.csv", c1["trades"], f"Phase 3 final combination {name} ({r['arms']}), tag {tag}")
        print({k: r[k] for k in ("arm", "arms", "verdict", "trades", "net_R", "per_session_vs_A0", "ci90_low", "ci90_high", "max_dd",
                                 "max_dd_limit", "per_session_vs_A0_2tick", "diff_total")})
        if r["verdict"] == "promote": final = r; break
    run_arms.write_csv(OUT / "combination_results.csv", rows, f"Phase 3 final-combination replay, fill model v3.5, tag {tag}")
    json.dump(dict(tag=tag, final=final and final["arm"], final_arms=final and final["arms"],
                   steps=[{k: r[k] for k in ("arm", "arms", "verdict")} for r in rows]),
              open(OUT / "combination_summary.json", "w"), indent=1)
    print("FINAL:", final and final["arms"])


if __name__ == "__main__":
    main()
