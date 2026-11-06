r"""E24 check: a blank reward_risk appears only where S1.4 does not need one; no blank becomes zero; no entry skips the check.

  python -m book1a.hand_checks.e24_reward_risk_check <r4 run dir> <out md>

S1.4 (JeronOrderFlowStrategy.cs, CANDIDATE rows ~L2617-2654, CONFIRM rows ~L2848-2868) computes RewardRisk only when
the candidate has a target and a positive risk; then rr < MinRewardRisk (1.5) adds POOR_REWARD_RISK. With no target the
status is Pending (NO_TARGET_REFERENCE); with risk <= 0 INVALID_RISK. Only Qualified rows become order attempts
(jeron_engine.arm_replay.attempts). So a blank is allowed only on a row with no target or no positive risk, and it
must never be on a Qualified row or an attempt.

Checks, over every CANDIDATE / CONFIRM / SHADOW row of the strategy log of the run (all its days):
  1. every blank RewardRisk row has no target (TargetPrice blank) or INVALID_RISK;
  2. no blank RewardRisk row is Qualified;
  3. every row of R4_candidates.csv carries the log's RewardRisk text unchanged (a blank stays blank, never 0);
  4. every attempt in R4_attempts.csv comes from a Qualified row with a target and RewardRisk >= MinRewardRisk.
"""
from __future__ import annotations

import csv
import os
import sys
from collections import Counter
from pathlib import Path

MIN_RR = 1.5     # S1.4 MinRewardRisk default (strategy_args.json is checked below)


def main(argv):
    run, out_md = Path(argv[0]).resolve(), Path(argv[1])
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    os.environ.setdefault("BOOK1_ROOT", r"K:\Databento_BackTesting")
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR
    args = (run / "strategy_args.json").read_text()
    min_rr = MIN_RR
    if "MinRewardRisk=" in args:
        min_rr = float(args.split("MinRewardRisk=")[1].split('"')[0].split(",")[0])
    log = AR.Log(run)
    rows = [r for r in log.rows if r.get("RecordType") in ("CANDIDATE", "CONFIRM", "SHADOW")]
    blank = [r for r in rows if (r.get("RewardRisk") or "") == ""]
    f1 = [r for r in blank if (r.get("TargetPrice") or "") != "" and "INVALID_RISK" not in (r.get("Reasons") or "")]
    f2 = [r for r in blank if r.get("CandidateStatus") == "Qualified"]
    by_status = Counter((r["RecordType"], r.get("CandidateStatus", "")) for r in blank)
    # 3. candidate file vs log, by event id and record
    logmap = {}
    for r in log.rows:
        if r.get("RecordType") in ("CANDIDATE", "SHADOW"):
            logmap.setdefault(r["EventId"], r)
    cand = list(csv.DictReader(open(run / "R4_candidates.csv", newline="")))
    f3, zero_from_blank, cblank = [], 0, 0
    for c in cand:
        lr = logmap.get(c["event"])
        if lr is None:
            f3.append((c["event"], "not in log")); continue
        if c["reward_risk"] != (lr.get("RewardRisk") or ""):
            f3.append((c["event"], f"file {c['reward_risk']!r} log {lr.get('RewardRisk')!r}"))
        if c["reward_risk"] == "":
            cblank += 1
        if (lr.get("RewardRisk") or "") == "" and c["reward_risk"] not in ("",):
            zero_from_blank += 1
    # 4. attempts
    q = {}
    for r in log.rows:
        if r.get("CandidateStatus") == "Qualified" and r.get("RecordType") in ("CANDIDATE", "CONFIRM"):
            q.setdefault(r["EventId"], []).append(r)
    att = list(csv.DictReader(open(run / "R4_attempts.csv", newline="")))
    f4 = []
    for a in att:
        rs = q.get(a["event"], [])
        if not rs:
            f4.append((a["event"], "no Qualified row")); continue
        for r in rs:
            rr = r.get("RewardRisk") or ""
            if (r.get("TargetPrice") or "") == "" or rr == "" or float(rr) < min_rr:
                f4.append((a["event"], f"target={r.get('TargetPrice')!r} rr={rr!r}"))
    L = ["# E24 check: blank reward_risk (S1.4 RewardRisk)", "", f"Run: `{run.name}`; MinRewardRisk = {min_rr}.", "",
         "| # | check | rows checked | failures |", "|---|---|---|---|",
         f"| 1 | blank only where there is no target or no positive risk | {len(blank)} blank of {len(rows)} | {len(f1)} |",
         f"| 2 | no blank row is Qualified | {len(blank)} | {len(f2)} |",
         f"| 3 | R4_candidates.csv keeps the log text (blank stays blank, never 0) | {len(cand)} ({cblank} blank) | {len(f3)} (blank turned into a value: {zero_from_blank}) |",
         f"| 4 | every attempt is Qualified, has a target and RewardRisk >= {min_rr} | {len(att)} attempts | {len(f4)} |", "",
         "Blank rows by record and status: " + ", ".join(f"{k[0]}/{k[1] or '-'} {v}" for k, v in sorted(by_status.items())), ""]
    for name, f in (("1", f1), ("2", f2), ("3", f3), ("4", f4)):
        for x in f[:20]:
            L.append(f"- failure {name}: {x if isinstance(x, tuple) else (x.get('EventId'), x.get('CandidateStatus'), x.get('TargetPrice'))}")
    ok = not (f1 or f2 or f3 or f4)
    L.append(f"Result: {'PASS' if ok else 'FAIL'}")
    out_md.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[4:11]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
