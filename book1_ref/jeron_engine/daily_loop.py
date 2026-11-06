"""Daily loop for a block of sessions (JE 0.3, Oct 25 2026): map -> rules-only plan -> S1.4 strategy -> fill model
-> day sheets and checks. Used for Phase 1 (shakedown) and later phases.

run(cfg) where cfg holds: sessions (list of yyyy-mm-dd), tapes_dir, nq_1m, es_1m, calendar, gex, out_dir,
map_from / strategy_from (Central, 'yyyy-mm-dd HH:MM'), to, holidays, half_days, roll_dates, instrument.

Strategy settings = S1.4 defaults (arm A0) except what the harness cannot do (L2 capture, display) and the
evaluation window (EvaluateFromDate = first session, WarmupDays = 1).
"""
import csv, glob, json, os, subprocess, collections, datetime as dt
from pathlib import Path
from . import rules_plan, fills
from .mbo_tape import join_tapes

HERE = Path(__file__).resolve().parent
EXE = next((p for p in (HERE.parent / "jeron_harness" / "build" / "JeronHarness.exe", HERE.parent / "build" / "JeronHarness.exe") if p.exists()),
           HERE.parent / "build" / "JeronHarness.exe")
ROW_TYPES = ["CONFIG", "PLAN", "STATE", "NOTE", "ZONE_CREATED", "ZONE_ACTIVE", "IMBALANCE", "EVIDENCE", "CANDIDATE", "CONFIRM",
             "OUTCOME", "EXIT_WARN", "SHADOW", "SHADOW_OUTCOME", "RETEST", "REVERSAL_CANDIDATE", "REVERSAL_OUTCOME",
             "RESEARCH_SIGNAL", "RESEARCH_OUTCOME", "RESEARCH_NOENTRY", "EXIT_MODEL", "ORDER", "ORDER_BLOCKED", "FILL",
             "TRADE_CLOSED", "HALT", "FLATTEN"]


def _mono():
    return [] if os.name == "nt" else ["mono"]


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, TZ="America/Chicago"))
    if p.returncode != 0: raise RuntimeError(" ".join(cmd)[:300] + "\n" + p.stdout[-3000:] + p.stderr[-3000:])
    return p.stdout


def day_tapes(tapes_dir, first_utc, last_utc):
    return sorted(f for f in Path(tapes_dir).glob("tape_*.csv.gz") if first_utc <= f.name[5:13] <= last_utc)


def run(cfg):
    out = Path(cfg["out_dir"]); out.mkdir(parents=True, exist_ok=True)
    s0, s1 = cfg["sessions"][0], cfg["sessions"][-1]
    log = []
    # 1. tapes
    map_tape = out / "tape_map.csv.gz"; strat_tape = out / "tape_strategy.csv.gz"
    if not map_tape.exists(): join_tapes(map_tape, day_tapes(cfg["tapes_dir"], cfg["map_first_utc"], cfg["last_utc"]))
    if not strat_tape.exists(): join_tapes(strat_tape, day_tapes(cfg["tapes_dir"], cfg["strategy_first_utc"], cfg["last_utc"]))
    # 2. map (MAP0 = v2.3 defaults; as-of 08:10)
    mdir = out / "map"; mdir.mkdir(exist_ok=True)
    margs = _mono() + [str(EXE), "--map", f"--from={cfg['map_from']}", f"--to={s1} 09:00", f"--es={cfg['es_1m']}", f"--htf={cfg['nq_1m']}",
                       f"--instrument={cfg['instrument']}", str(map_tape), str(mdir),
                       f"HolidayDates={cfg['holidays']}", f"HalfDayDates={cfg['half_days']}"] + cfg.get("map_settings", [])
    log.append(_run(margs)[-1500:])
    # 3. plans
    pdir = out / "plans"
    plans = rules_plan.write_plans(mdir, pdir, cfg["calendar"], cfg["gex"], set(cfg["sessions"]), set(cfg.get("roll_dates", [])))
    # 4. strategy (A0 = S1.4 defaults)
    sdir = out / "strategy"
    if sdir.exists():
        for f in sdir.glob("JOFS_*.csv"): f.unlink()
    sdir.mkdir(exist_ok=True)
    sargs = _mono() + [str(EXE), f"--from={cfg['strategy_from']}", f"--to={cfg['to']}", f"--es={cfg['es_1m']}", f"--instrument={cfg['instrument']}",
                       str(strat_tape), str(pdir), str(sdir), f"EvaluateFromDate={s0}", "WarmupDays=1"] + cfg.get("strategy_settings", [])
    log.append(_run(sargs)[-1500:])
    jofs = next(sdir.glob("JOFS_*.csv"))
    # 5. fill model on the strategy's orders (base 250 ms / 1 tick stop slip; stress 1,000 ms and 2 / 4 ticks)
    ledger = fill_ledger(jofs, strat_tape, out / "fills_model.csv", cfg.get("fill_model", "v3.4"))
    # 6. sheets and checks
    summary = day_sheets(jofs, pdir, mdir, ledger, cfg["sessions"], out)
    (out / "run_log.txt").write_text("\n\n".join(log), encoding="utf-8")
    return summary


def fill_ledger(jofs, tape_path, out_csv, fill_model="v3.4"):
    """fill_model "v3.4" (Phases 0-2) or "v3.5" (frozen for Phase 3: stop gap fill, rule 7b)."""
    if fill_model not in ("v3.4", "v3.5"): raise ValueError(fill_model)
    rows = list(csv.DictReader(open(jofs, newline="", encoding="utf-8-sig")))
    orders = [x for x in rows if x["RecordType"] == "ORDER"]
    if not orders:
        Path(out_csv).write_text("no orders\n", encoding="utf-8"); return []
    tape = fills.Tape(tape_path)
    res = []
    for o in orders:
        side = 1 if o["Direction"] == "Long" else -1
        t = dt.datetime.fromisoformat(o["EvidenceTimeCT"][:23])
        r = dict(date=o["EvidenceTimeCT"][:10], signal_time=o["EvidenceTimeCT"][11:19], event=o["EventId"], side=o["Direction"], grade=o["Grade"],
                 entry_ref=o["EntryRef"], stop=o["StopAnchor"], target=o["TargetPrice"])
        for lat, slip, k in ((250, 1, "base"), (1000, 1, "lat1000"), (250, 2, "slip2"), (250, 4, "slip4")):
            m = fills.simulate(tape, side, t, float(o["StopAnchor"]), float(o["TargetPrice"]), latency_ms=lat, stop_slip=slip,
                               gap_fill=fill_model == "v3.5")
            r[f"{k}_entry"] = m["entry"]; r[f"{k}_exit"] = m["exit"]; r[f"{k}_reason"] = m["reason"]; r[f"{k}_ticks"] = m["ticks"]
        res.append(r)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
    return res


def audits(rows):
    """C2 (reward:risk) recomputed from each candidate's own entry, stop and target; C1 (location) = the candidate's
    zone must be a plan zone (FROZEN_PREOPEN) or an intraday zone created that day."""
    c2 = []; c1 = []
    for x in rows:
        if x["RecordType"] != "CANDIDATE" or not x["EntryRef"] or not x["StopAnchor"] or not x["TargetPrice"]: continue
        e, s, t = float(x["EntryRef"]), float(x["StopAnchor"]), float(x["TargetPrice"])
        if e == s: continue
        rr = abs(t - e) / abs(e - s)
        try: logged = float(x["RewardRisk"])
        except ValueError: continue
        if abs(rr - logged) > 0.011: c2.append((x["EventId"], round(rr, 2), logged))
        lt = x.get("LocationType", "")
        if not (lt.startswith("FROZEN_PREOPEN") or lt.startswith("DEVELOPING_INTRADAY") or lt.startswith("POWER") or lt.startswith("INTRADAY")):
            c1.append((x["EventId"], lt))
    return c1, c2


def day_sheets(jofs, pdir, mdir, ledger, sessions, out):
    rows = list(csv.DictReader(open(jofs, newline="", encoding="utf-8-sig")))
    by_day = collections.defaultdict(list)
    for x in rows:
        d = (x.get("EvidenceTimeCT") or "")[:10]
        by_day[d].append(x)
    seen_types = collections.Counter(x["RecordType"] for x in rows)
    sheets = out / "day_sheets"; sheets.mkdir(exist_ok=True)
    summary = []
    for d in sessions:
        R = by_day.get(d, [])
        plan_txt = (Path(pdir) / f"PreopenPlan_{d}.txt").read_text(encoding="utf-8") if (Path(pdir) / f"PreopenPlan_{d}.txt").exists() else ""
        pl = {k: v for k, v in (l.split("=", 1) for l in plan_txt.splitlines() if "=" in l and not l.startswith("#") and not l.startswith("zone="))}
        zones = [l[5:] for l in plan_txt.splitlines() if l.startswith("zone=")]
        cands = [x for x in R if x["RecordType"] == "CANDIDATE"]
        ny = [x for x in cands if "OUTSIDE_NY_SESSION" not in x["Reasons"]]
        st = collections.Counter(x["CandidateStatus"] for x in cands)
        q_out = [x for x in R if x["RecordType"] == "OUTCOME" and x["CandidateStatus"] == "Qualified"]
        trades = [x for x in R if x["RecordType"] == "TRADE_CLOSED"]
        led = [l for l in ledger if l["date"] == d]
        c1, c2 = audits(R)
        reasons = collections.Counter(r for x in ny for r in x["Reasons"].split("|") if r)
        L = [f"# Day sheet {d}", "",
             f"**Plan:** review={pl.get('review', 'n/a')}, context={pl.get('context', 'n/a')}; {len(zones)} zones; "
             f"balance={pl.get('balance', 'none')}; lava={pl.get('lava', 'none')}; max_trades={pl.get('max_trades', '-')}; no_trade={pl.get('no_trade', '-')}; gex_regime={pl.get('gex_regime', '-')}",
             f"**Review note:** {pl.get('review_note', '')}", "", "**Zones**", ""] + [f"- {z}" for z in zones] + ["",
             f"**Candidates:** {len(cands)} ({len(ny)} in NY) — " + ", ".join(f"{k} {v}" for k, v in st.most_common()),
             "**Why NY candidates were blocked (count):** " + ", ".join(f"{k} {v}" for k, v in reasons.most_common(10)), "",
             "**Qualified (tracker outcome, to session end / 15 bars)**", ""]
        for x in q_out:
            L.append(f"- {x.get('SignalTimeCT', '')[11:16] or x['EvidenceTimeCT'][11:16]} {x['Direction']} {x['Grade']} {x['LocationId']}: entry {x['EntryRef']} stop {x['StopAnchor']} target {x['TargetPrice']} → {x['OutcomeType']} {x['PnLTicks']} / 15-bar {x['Outcome15']} {x['PnL15Ticks']}")
        if not q_out: L.append("- none")
        L += ["", "**Strategy trades (harness Sim) and the v3.4 fill model**", ""]
        for x in R:
            if x["RecordType"] in ("ORDER", "ORDER_BLOCKED", "FILL", "TRADE_CLOSED", "HALT", "FLATTEN"):
                L.append(f"- {x['RecordType']} {x['EvidenceTimeCT'][11:19]} {x['Direction']} {x['Detail'][:160]}")
        for l in led:
            L.append(f"- model {l['signal_time']} {l['side']}: base {l['base_entry']}→{l['base_exit']} {l['base_reason']} {l['base_ticks']} t; 1,000 ms {l['lat1000_ticks']} t; stop slip 2/4: {l['slip2_ticks']}/{l['slip4_ticks']} t")
        L += ["", f"**Audits:** C1 location issues {len(c1)}; C2 reward:risk mismatches {len(c2)}" + (f" (first: {c2[:3]})" if c2 else ""),
              "**Row types this day:** " + ", ".join(f"{k} {v}" for k, v in collections.Counter(x['RecordType'] for x in R).most_common())]
        (sheets / f"day_{d}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        summary.append(dict(date=d, review=pl.get("review", ""), context=pl.get("context", ""), plan_zones=len(zones), candidates=len(cands), ny_candidates=len(ny),
                            qualified=st.get("Qualified", 0), event_only=st.get("EventOnly", 0), rejected=st.get("Rejected", 0),
                            orders=sum(1 for x in R if x["RecordType"] == "ORDER"), blocked=sum(1 for x in R if x["RecordType"] == "ORDER_BLOCKED"),
                            trades=len(trades), c1_issues=len(c1), c2_mismatches=len(c2), rows=len(R)))
    with open(out / "phase_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    with open(out / "row_types.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["RecordType", "rows", "expected_in_phase1"])
        for k in sorted(set(ROW_TYPES) | set(seen_types)): w.writerow([k, seen_types.get(k, 0), "yes" if k in ROW_TYPES else "extra"])
    return summary
