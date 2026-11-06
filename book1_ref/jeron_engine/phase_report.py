"""Phase report card (design v3.8, Phase 2 deliverables) from a daily_loop run (JE 0.3, Oct 25 2026).

A0 report card: trades from the v3.4 fill model (base case: 250 ms entry at bid/ask, 1-tick stop slippage,
1-tick-through targets, commission $2.87/side = 1.148 ticks per round turn), net R = net ticks / planned risk ticks.
Breakdowns: grade, setup family, zone kind, time of day, plan review / context.
By blocking rule: every NY-session candidate with a definite tracker outcome (OUTCOME row, to the session end,
same bar = stop), per rejection reason: winners blocked vs losers blocked, and how many failed ONLY that gate.
Half-day check (parity gate 4): Nov 28 (half day) and Dec 1 packets keep PD, weekly and prior-week profiles,
and no data gap is logged after the early close.
"""
import csv, json, collections, statistics as st, glob
from pathlib import Path

TICK = 0.25
COMM_TICKS = 2 * 2.87 / 5.0   # $ per round turn / $5 per NQ tick


def _f(x):
    try: return float(x)
    except (TypeError, ValueError): return None


def zone_kind(loc_type, loc_id):
    if loc_type.startswith("FROZEN_PREOPEN"): return "PLAN_" + ("TARGET" if loc_id.startswith("P_T_") else "DECISION")
    if "IMB" in loc_type or loc_id.startswith("IMB_"): return "INTRADAY_IMB"
    if "POWER" in loc_type or loc_id.startswith("PWR_"): return "INTRADAY_POWER"
    return loc_type.split(" ")[0] or "OTHER"


def tod(t):
    h = int(t[11:13]); m = int(t[14:16]); x = h * 60 + m
    return "08:30-09:30" if x < 570 else "09:30-11:00" if x < 660 else "11:00-13:00" if x < 780 else "13:00-15:00"


def trades_table(run_dir):
    run = Path(run_dir)
    jofs = next((run / "strategy").glob("JOFS_*.csv"))
    rows = list(csv.DictReader(open(jofs, newline="", encoding="utf-8-sig")))
    orders = {x["EventId"]: x for x in rows if x["RecordType"] == "ORDER"}
    fm = list(csv.DictReader(open(run / "fills_model.csv"))) if (run / "fills_model.csv").read_text().strip() != "no orders" else []
    plans = {}
    for f in (run / "plans").glob("PreopenPlan_*.txt"):
        kv = dict(l.split("=", 1) for l in f.read_text().splitlines() if "=" in l and not l.startswith(("#", "zone=")))
        plans[kv.get("date")] = kv
    out = []
    for m in fm:
        o = orders[m["event"]]
        side = 1 if o["Direction"] == "Long" else -1
        e = _f(m["base_entry"]); s = _f(o["StopAnchor"])
        risk = abs(e - s) / TICK if e and s else None
        for k in ("base", "lat1000", "slip2", "slip4"):
            m[k + "_net_ticks"] = (_f(m[k + "_ticks"]) or 0) - COMM_TICKS
            m[k + "_net_R"] = m[k + "_net_ticks"] / risk if risk else None
        p = plans.get(m["date"], {})
        m.update(risk_ticks=risk, family=o["SetupFamily"], zone_kind=zone_kind(o["LocationType"], o["LocationId"]), tod=tod(o["EvidenceTimeCT"]),
                 context=p.get("context", ""), review=p.get("review", ""), grade=o["Grade"])
        out.append(m)
    return out, rows


def stats(tr, key="base"):
    if not tr: return dict(trades=0)
    r = [t[key + "_net_R"] for t in tr]; tk = [t[key + "_net_ticks"] for t in tr]
    eq, peak, dd = 0.0, 0.0, 0.0
    for x in r:
        eq += x; peak = max(peak, eq); dd = max(dd, peak - eq)
    wins = sum(1 for t in tr if t[key + "_reason"] == "TARGET")
    return dict(trades=len(tr), wins=wins, win_rate=round(wins / len(tr), 3), net_R=round(sum(r), 2), mean_R=round(st.mean(r), 3),
                median_R=round(st.median(r), 3), net_ticks=round(sum(tk), 1), max_dd_R=round(dd, 2))


def by_block(rows):
    """NY candidates (not OUTSIDE_NY_SESSION) with a definite tracker OUTCOME, per rejection reason."""
    cand = {x["EventId"]: x for x in rows if x["RecordType"] == "CANDIDATE" and "OUTSIDE_NY_SESSION" not in x["Reasons"]}
    res = collections.defaultdict(lambda: dict(n=0, win=0, loss=0, win_ticks=0.0, loss_ticks=0.0, only=0, only_win=0, only_loss=0))
    for x in rows:
        if x["RecordType"] != "OUTCOME" or x["EventId"] not in cand: continue
        c = cand[x["EventId"]]
        if c["CandidateStatus"] == "Qualified": continue
        ot = x.get("OutcomeType", ""); pt = _f(x.get("PnLTicks")) or 0.0
        if ot not in ("TARGET_FIRST", "STOP_FIRST"): continue
        reasons = [r for r in c["Reasons"].split("|") if r and r != "NO_PLAN"]
        for r in reasons:
            d = res[r]; d["n"] += 1
            if ot == "TARGET_FIRST": d["win"] += 1; d["win_ticks"] += pt
            else: d["loss"] += 1; d["loss_ticks"] += pt
            if len(reasons) == 1:
                d["only"] += 1; d["only_win"] += ot == "TARGET_FIRST"; d["only_loss"] += ot == "STOP_FIRST"
    return dict(sorted(res.items(), key=lambda kv: -kv[1]["n"]))


def half_day_check(map_dir, days=("2025-11-28", "2025-12-01")):
    out = {}
    for d in days:
        f = next(Path(map_dir).glob(f"PreopenPacket_*_{d}.json"), None)
        if not f: out[d] = "no packet"; continue
        p = json.load(open(f))
        ps = {s["slot"]: s for s in p.get("prior_sessions", [])}
        wk = p.get("weekly") or {}
        out[d] = dict(pd_covered=(ps.get("PD") or {}).get("covered"), pd_date=(ps.get("PD") or {}).get("date"),
                      weekly=wk.get("vah") is not None, prior_week=wk.get("prior_week_vah") is not None,
                      gaps=p["data"].get("gaps"), notes=p["data"].get("notes"), calendar=p.get("calendar"))
    return out


def report(run_dir, out_md, phase_name):
    tr, rows = trades_table(run_dir)
    lines = [f"# {phase_name}: A0 report card", ""]
    base = stats(tr)
    lines += ["## A0 (S1.4 defaults, rules-only plan, MAP0), v3.4 fill model", "",
              "| Case | Trades | Wins | Win rate | Net R | Mean R | Median R | Net ticks | Max DD (R) |", "|---|---|---|---|---|---|---|---|---|"]
    for k, lab in (("base", "Base (250 ms, stop +1 tick)"), ("lat1000", "Latency 1,000 ms"), ("slip2", "Stop slippage 2 ticks"), ("slip4", "Stop slippage 4 ticks")):
        s = stats(tr, k)
        lines.append(f"| {lab} | {s.get('trades', 0)} | {s.get('wins', '')} | {s.get('win_rate', '')} | {s.get('net_R', '')} | {s.get('mean_R', '')} | {s.get('median_R', '')} | {s.get('net_ticks', '')} | {s.get('max_dd_R', '')} |")
    for key, title in (("grade", "Grade"), ("family", "Setup family"), ("zone_kind", "Zone kind"), ("tod", "Time of day (CT)"), ("context", "Plan context")):
        g = collections.defaultdict(list)
        for t in tr: g[t[key]].append(t)
        lines += ["", f"### By {title.lower()}", "", "| " + title + " | Trades | Wins | Net R | Mean R |", "|---|---|---|---|---|"]
        for k2 in sorted(g):
            s = stats(g[k2]); lines.append(f"| {k2} | {s['trades']} | {s['wins']} | {s['net_R']} | {s['mean_R']} |")
    bb = by_block(rows)
    lines += ["", "## By blocking rule (NY candidates with a definite tracker outcome, to the session end; NO_PLAN left out)", "",
              "Counts overlap: a candidate that failed three gates is in three rows. \"Only this gate\" = it failed nothing else.", "",
              "| Reason | Candidates | Target first | Stop first | Target-first share | Winner ticks | Loser ticks | Only this gate (W / L) |", "|---|---|---|---|---|---|---|---|"]
    for r, d in bb.items():
        share = d["win"] / d["n"] if d["n"] else 0
        lines.append(f"| {r} | {d['n']} | {d['win']} | {d['loss']} | {share:.0%} | {d['win_ticks']:.0f} | {d['loss_ticks']:.0f} | {d['only']} ({d['only_win']} / {d['only_loss']}) |")
    days = sorted({t["date"] for t in tr})
    lines += ["", "## Trades", "", "| Date | Signal | Side | Grade | Family | Zone kind | Risk ticks | Entry | Exit | Result | Net ticks | Net R |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in tr:
        lines.append(f"| {t['date']} | {t['signal_time'][:5]} | {t['side']} | {t['grade']} | {t['family']} | {t['zone_kind']} | {t['risk_ticks']:.0f} | {t['base_entry']} | {t['base_exit']} | {t['base_reason']} | {t['base_net_ticks']:.1f} | {t['base_net_R']:.2f} |")
    Path(out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(Path(out_md).with_suffix(".trades.csv"), "w", newline="") as f:
        if tr:
            w = csv.DictWriter(f, fieldnames=list(tr[0])); w.writeheader(); w.writerows(tr)
    return base, bb
