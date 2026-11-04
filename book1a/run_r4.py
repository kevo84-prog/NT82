r"""R4 (Book 1A) run path: S1.4 reads the Book 1A v2.4 pre-open plans, never an A0 plan (ambiguity E17, Nov 4, 2026).

  python -m book1a.run_r4 --block1 K:\Databento_BackTesting --a0-run Book1A\Phase0\runs\phase1 \
      --plans Book1A\Phase0\plans_phase1 --phase phase1 --out Book1A\Phase0\runs\phase1_r4

Steps
  1. load_book1a_plans: for every session, PreopenPlan_<day>_book1a.txt and its sidecar .json must exist in --plans,
     carry plan_id=<day>-b1a, date=<day>, the plan builder version (plan_v24.VERSION) in the header, and a sidecar for
     the same day. Anything missing or different -> R4PlanError and the run stops. There is no fallback: an A0 plan
     (PreopenPlan_<day>.txt, plan_id <day>-v1) next to it is never read.
  2. The plan texts are copied byte for byte into <out>/plans/PreopenPlan_<day>.txt (the name S1.4 looks for);
     plan_manifest.json records version, plan_id and sha256 of the text and of the sidecar per day.
  3. S1.4 in the harness, with exactly the A0 run's strategy arguments (daily_loop step 4: same tape, warm-up, ES bars,
     instrument, settings, EvaluateFromDate, WarmupDays=1), only the plan folder differs. The A0 run is read only.
  4. verify_plans_loaded: the strategy log must show one PLAN_LOADED per session with id <day>-b1a and the file from
     <out>/plans, and no plan problem row; every candidate on a plan zone must name the Book 1A plan. Else R4PlanError.
  5. R4 = replay_risk.replay(veto = L1 or T8, RH1 retest 15 bars / 2 ticks, M0, v3.5, C3 risk check and sizing);
     FZ1 is logged only. Ledger rows and candidate rows carry plan_version, plan_id, plan_sha256 and
     plan_sidecar_sha256; candidate rows on a plan zone also carry the zone's Book 1A families, sides and the day's
     market_context from the sidecar.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from book1a import ledger as L, sessions as S

VERSION = "run-r4-v1.0"
PLAN_COLUMNS = ["plan_version", "plan_id", "plan_sha256", "plan_sidecar_sha256"]
ZONE_COLUMNS = ["plan_zone_label", "plan_zone_class", "plan_zone_families", "plan_zone_long", "plan_zone_short", "plan_market_context"]


class R4PlanError(RuntimeError):
    """A Book 1A plan is missing or is not the Book 1A plan; R4 never falls back to an A0 plan."""


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _plan_version() -> str:
    from book1a import plan_v24
    return plan_v24.VERSION


def load_book1a_plans(plans_dir, sessions: Iterable[str], version: Optional[str] = None) -> Dict[str, dict]:
    plans_dir = Path(plans_dir)
    version = version or _plan_version()
    out, problems = {}, []
    for d in sessions:
        txt, side = plans_dir / f"PreopenPlan_{d}_book1a.txt", plans_dir / f"PreopenPlan_{d}_book1a.json"
        if not txt.exists() or not side.exists():
            problems.append(f"{d}: Book 1A plan missing ({'text' if not txt.exists() else ''}{' ' if not txt.exists() and not side.exists() else ''}{'sidecar' if not side.exists() else ''})")
            continue
        text = txt.read_text(encoding="utf-8")
        kv = dict(l.split("=", 1) for l in text.splitlines() if "=" in l and not l.startswith("#"))
        head = text.splitlines()[0] if text else ""
        sc = json.loads(side.read_text(encoding="utf-8"))
        if kv.get("date") != d: problems.append(f"{d}: plan date {kv.get('date')}")
        if kv.get("plan_id") != f"{d}-b1a": problems.append(f"{d}: plan_id {kv.get('plan_id')} is not the Book 1A plan")
        if version not in head: problems.append(f"{d}: plan header has no {version}")
        if sc.get("date") != d: problems.append(f"{d}: sidecar date {sc.get('date')}")
        if kv.get("end") != "1": problems.append(f"{d}: plan has no end=1")
        out[d] = dict(date=d, plan_version=version, plan_id=kv.get("plan_id"), plan_sha256=_sha(txt),
                      plan_sidecar_sha256=_sha(side), text_path=str(txt), sidecar_path=str(side), sidecar=sc)
    if problems:
        raise R4PlanError("R4 stopped, no fallback to A0 plans: " + "; ".join(problems))
    return out


def stage_plans(plans: Dict[str, dict], out: Path) -> Path:
    pdir = out / "plans"
    if pdir.exists():
        shutil.rmtree(pdir)          # only ever holds copies this module wrote
    pdir.mkdir(parents=True)
    for d, p in plans.items():
        shutil.copyfile(p["text_path"], pdir / f"PreopenPlan_{d}.txt")
        if _sha(pdir / f"PreopenPlan_{d}.txt") != p["plan_sha256"]:
            raise R4PlanError(f"{d}: staged plan differs from the Book 1A plan")
    (pdir / "plan_manifest.json").write_text(json.dumps({d: {k: v for k, v in p.items() if k != "sidecar"} for d, p in plans.items()}, indent=1))
    return pdir


PLAN_LOADED = re.compile(r"PLAN_LOADED id=(\S+) file=(.+?) applies_from=")


def verify_plans_loaded(rows: List[dict], plans: Dict[str, dict], pdir: Path) -> None:
    problems, seen = [], {}
    for r in rows:
        if r["RecordType"] != "PLAN":
            continue
        det = r.get("Detail", "")
        if "PLAN_WAITING" in det or "problem=" in det:
            problems.append(f"plan problem row: {det[:160]}")
        m = PLAN_LOADED.search(det)
        if m:
            pid, f = m.group(1), Path(m.group(2))
            d = pid[:10]
            seen.setdefault(d, []).append(pid)
            if d in plans and (pid != plans[d]["plan_id"] or f.resolve() != (pdir / f"PreopenPlan_{d}.txt").resolve()):
                problems.append(f"{d}: S1.4 loaded {pid} from {f}, not the Book 1A plan")
    for d in plans:
        if seen.get(d) != [plans[d]["plan_id"]]:
            problems.append(f"{d}: PLAN_LOADED {seen.get(d)} (expected one {plans[d]['plan_id']})")
    for r in rows:
        if r["RecordType"] in ("CANDIDATE", "SHADOW") and r.get("LocationType", "").startswith("FROZEN_PREOPEN"):
            d = r["EvidenceTimeCT"][:10]
            if d in plans and f"(plan {plans[d]['plan_id']})" not in r["LocationType"]:
                problems.append(f"{r['EventId']}: plan zone from {r['LocationType']}")
    if problems:
        raise R4PlanError("R4 stopped: " + "; ".join(problems[:20]))


def zone_fields(row: dict, plan: dict) -> dict:
    """Book 1A zone fields for a candidate on a plan zone (LocationId P_<label>_NN); null for intraday zones."""
    sc = plan["sidecar"]
    out = {k: "null" for k in ZONE_COLUMNS}
    out["plan_market_context"] = sc.get("market_context") or "null"
    lid = row.get("LocationId", "")
    if not row.get("LocationType", "").startswith("FROZEN_PREOPEN") or not lid.startswith("P_"):
        return out
    label = re.sub(r"_\d+$", "", lid[2:])
    for cls, key in (("DECISION", "zones"), ("TARGET", "targets")):
        for z in sc.get(key) or []:
            zl = z.get("label", "")
            if zl == label or (cls == "TARGET" and "T_" + zl == label) or (cls == "TARGET" and zl == "T_" + label):
                out.update(plan_zone_label=zl, plan_zone_class=cls, plan_zone_families=",".join(z.get("families") or []) or "null",
                           plan_zone_long=z.get("long", "null"), plan_zone_short=z.get("short", "null"))
                return out
    out.update(plan_zone_label=label, plan_zone_class="NOT_IN_SIDECAR")
    return out


def plan_cols(plan: dict) -> dict:
    return {k: plan[k] for k in PLAN_COLUMNS}


def write_ledger(path: Path, trades, plans: Dict[str, dict]) -> int:
    rows = []
    for t in sorted(trades, key=lambda t: (t.date, t.entry_time)):
        if t.date not in plans:
            raise R4PlanError(f"trade {t.trade_id} on {t.date}: no Book 1A plan")
        rows.append({**t.as_ledger_row(), **plan_cols(plans[t.date])})
    return L.write_csv(str(path), rows, L.LEDGER_COLUMNS + PLAN_COLUMNS)


def run_strategy(a0_run: Path, out: Path, pdir: Path) -> Path:
    """daily_loop step 4 with the A0 run's own arguments; only the plan folder is the Book 1A one."""
    from jeron_engine import daily_loop as DL
    cfg = json.loads((a0_run / "daily_loop_config.json").read_text())
    tape = out / "tape_strategy.csv.gz"
    if not tape.exists():
        os.link(a0_run / "tape_strategy.csv.gz", tape)       # hard link, read only
    sdir = out / "strategy"
    if sdir.exists():
        for f in sdir.glob("JOFS_*.csv"): f.unlink()
    sdir.mkdir(exist_ok=True)
    sargs = DL._mono() + [str(DL.EXE), f"--from={cfg['strategy_from']}", f"--to={cfg['to']}", f"--es={cfg['es_1m']}", f"--instrument={cfg['instrument']}",
                          str(tape), str(pdir), str(sdir), f"EvaluateFromDate={cfg['sessions'][0]}", "WarmupDays=1"] + cfg.get("strategy_settings", [])
    (out / "run_log.txt").write_text(DL._run(sargs)[-3000:], encoding="utf-8")
    (out / "strategy_args.json").write_text(json.dumps(sargs, indent=1))
    return next(sdir.glob("JOFS_*.csv"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--a0-run", required=True); ap.add_argument("--plans", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--phase", choices=list(S.PHASES)); ap.add_argument("--sessions", nargs="*")
    ap.add_argument("--candidate-days", nargs="*", default=["2025-10-22", "2025-10-28", "2025-11-04"])
    ap.add_argument("--fill", choices=["v3.4", "v3.5"], default="v3.5")
    a = ap.parse_args(argv)
    block1, a0, out = Path(a.block1).resolve(), Path(a.a0_run).resolve(), Path(a.out).resolve()
    sess = [d.isoformat() for d in S.phase_sessions(a.phase)] if a.phase else list(a.sessions)
    plans = load_book1a_plans(a.plans, sess)                  # stops here if any Book 1A plan is missing
    a0_sessions = json.loads((a0 / "daily_loop_config.json").read_text())["sessions"]
    if a0_sessions != sess:
        raise SystemExit(f"--a0-run sessions {a0_sessions[0]}..{a0_sessions[-1]} differ from {sess[0]}..{sess[-1]}")
    os.environ["BOOK1_ROOT"] = str(block1)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import arm_replay as AR, arms as A, fills
    from book1a import candidate_log as CL, replay_risk as RR
    out.mkdir(parents=True, exist_ok=True)
    pdir = stage_plans(plans, out)
    run_strategy(a0, out, pdir)
    log = AR.Log(out)
    verify_plans_loaded(log.rows, plans, pdir)
    tape = fills.Tape(out / "tape_strategy.csv.gz")
    bars = A.MinuteBars(out / "tape_strategy.csv.gz")
    v_l1, v_t8 = A.l1(log), A.t8(log, bars)
    rep = RR.replay(log, tape, "R4", veto=lambda r: v_l1(r) or v_t8(r), retest=dict(bars=bars, fail_ticks=2), fill=a.fill)
    n_tr = write_ledger(out / "R4_M0_ledger.csv", rep["trades"], plans)
    with open(out / "R4_attempts.csv", "w", newline="") as f:
        cols = list(dict.fromkeys(k for r in rep["attempts"] for k in r)) or ["event"]
        w = csv.DictWriter(f, fieldnames=cols + ["plan_id", "plan_sha256"]); w.writeheader()
        for r in rep["attempts"]:
            w.writerow({**r, **{k: plans[r["time"].date().isoformat()][k] for k in ("plan_id", "plan_sha256")}})
    (out / "R4_risk_events.json").write_text(json.dumps(rep["risk_events"], indent=1, default=str))

    def extra(r):
        d = r["EvidenceTimeCT"][:10]
        if d not in plans:
            raise R4PlanError(f"candidate {r['EventId']} on {d}: no Book 1A plan")
        return {**plan_cols(plans[d]), **zone_fields(r, plans[d])}
    days = [d for d in a.candidate_days if d in plans]
    n_c = CL.build(out, out / "tape_strategy.csv.gz", out / "R4_candidates.csv", sessions=days, row_extra=extra,
                   extra_columns=PLAN_COLUMNS + ZONE_COLUMNS)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=Path(__file__).resolve().parents[1]).strip()
    except Exception:
        commit = "n/a"
    (out / "run_manifest.json").write_text(json.dumps(dict(
        version=VERSION, commit=commit, phase=a.phase, sessions=sess, a0_run=str(a0), plans_dir=str(Path(a.plans).resolve()),
        plan_version=_plan_version(), fill_model=a.fill, veto="L1|T8 (FZ1 logged only)", retest="RH1 15 bars / 2 ticks", exit_model="M0",
        trades=n_tr, candidate_rows=n_c, candidate_days=days, generated=dt.datetime.now().isoformat()), indent=1))
    print(f"R4 on Book 1A plans: {len(sess)} sessions, {n_c} candidate rows, ledger rows written -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
