"""Formats the Phase 3 outputs into the tables of Phase3_report.md. Formatting only, except where noted:
  - the A4 mj_alignment split for R4 (registration section 2: trades, net R per session over the population's sessions,
    win rate = R > 0 / trades, as phase2_report defines them) from phase3_review.csv's mj_alignment and the ledger
    realized_net_R; a missing value = other;
  - the C2 trades that differ from R4: Book 1's jeron_engine.arms.differing_trades (unchanged) on the trade dicts of
    book1a.phase3_compare.map_trades (unchanged);
  - row counts and file sha256.
Run from code/:  python book1a/Phase3/runs/report_build/build_phase3_report_md.py > book1a/Phase3/runs/report_build/tables.md"""
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(CODE))
os.environ.setdefault("BOOK1_ROOT", r"K:\Book1A_inputs")
from book1a import phase3_compare as PC, phase2_report as RP, sessions as SS   # noqa: E402

R = CODE / "book1a" / "Phase3" / "runs"
CI = CODE / "book1a" / "Phase3" / "checker_input"
DIAG = R / "phase3_diag_17ac9cd"
S = ("R1", "R2", "R3", "R4")
POPS = ("ALL", "UNEXPOSED")
card = json.loads((R / "phase3_report_card.json").read_text(encoding="utf-8"))
card_c2 = json.loads((R / "phase3_report_card_c2.json").read_text(encoding="utf-8"))
cls = json.loads((R / "phase3_review" / "phase3_review_classes.json").read_text(encoding="utf-8"))
cmp_ = json.loads((R / "phase3_compare" / "phase3_compare.json").read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()   # noqa: E731
SESS = [d.isoformat() for d in SS.phase_sessions("phase3")]
EXPOSED = {d.isoformat() for d in RP.EXPOSED_BY_PHASE["phase3"]}
POPSESS = {"ALL": SESS, "UNEXPOSED": [d for d in SESS if d not in EXPOSED]}


def f(x, d=3):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        return f"{x:,.{d}f}"
    return str(x)


def usd(x):
    return "-" if x is None else f"{x:,.2f}"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def card_rows(c, cols):
    rows = [
        ("trades", *[c[s]["trades"] for s in cols]),
        ("trades per session", *[f(c[s]["trades_per_session"]) for s in cols]),
        ("net R per session (realized)", *[f(c[s]["net_R_per_session"]) for s in cols]),
        ("90% session-bootstrap CI", *[f"[{f(c[s]['net_R_per_session_ci90'][0])}, {f(c[s]['net_R_per_session_ci90'][1])}]" for s in cols]),
        ("theoretical R per session", *[f(c[s]["theoretical_R_per_session"]) for s in cols]),
        ("win rate", *[f(c[s]["win_rate"]) for s in cols]),
        ("wins / losses / zero", *[f"{c[s]['wins']} / {c[s]['losses']} / {c[s]['zero']}" for s in cols]),
        ("average win R", *[f(c[s]["avg_win_R"]) for s in cols]),
        ("average loss R", *[f(c[s]["avg_loss_R"]) for s in cols]),
        ("max drawdown R (trade order)", *[f(c[s]["max_drawdown_R"]) for s in cols]),
        ("max drawdown USD (R3 / R4)", *[usd(c[s].get("max_drawdown_usd")) if "R3" in s or "R4" in s else "-" for s in cols]),
        ("SUPPLEMENTAL: max drawdown R, session order", *[f(c[s]["max_drawdown_R_session_order_SUPPLEMENTAL"]) for s in cols]),
        ("session dollar P&L, total (R1 / R2 at 1 NQ)", *[usd(c[s]["net_usd"]) for s in cols]),
        ("session dollar P&L per session", *[usd(c[s]["net_usd_per_session"]) for s in cols]),
        ("exit reasons", *[", ".join(f"{k} {v}" for k, v in c[s]["exit_reasons"].items()) or "-" for s in cols]),
    ]
    risky = lambda s: "R3" in s or "R4" in s   # noqa: E731
    for k, lab in (("risk_reject", "RISK_REJECT count"), ("exec_breach", "execution breaches"),
                   ("exec_breach_largest_usd", "largest execution breach over budget, USD"),
                   ("risk_breach_fill", "RISK_BREACH_FILL (realized overrun) count"),
                   ("risk_breach_fill_largest_overrun_usd", "largest realized overrun, USD")):
        rows.append((lab, *[(usd(c[s]["risk"][k]) if "usd" in k else c[s]["risk"][k]) if risky(s) else "-" for s in cols]))
    rows.append(("RISK_REJECT by reason", *[", ".join(f"{k.split(':')[1]} {v}" for k, v in c[s]["risk"]["risk_reject_by_reason"].items()) or "0"
                                           if risky(s) else "-" for s in cols]))
    return rows


def regime_tod_daily(c, cols, pop, sec):
    pr(f"Gamma regime split ({pop}): trades / net R per session / net R per trade / win rate / net USD\n")
    rows = []
    for g in ("all", "positive", "negative"):
        x = {s: c[s]["gamma_regime"][g] for s in cols}
        rows.append((f"{g} ({x[cols[0]]['sessions']} sessions)", *[f"{x[s]['trades']} / {f(x[s]['net_R_per_session'])} / {f(x[s]['net_R_per_trade'])} / "
                                                                   f"{f(x[s]['win_rate'])} / {usd(x[s]['net_usd'])}" for s in cols]))
    v5 = c[cols[0]]["gamma_regime"]["no_valid_gex_V5"]
    pr(table(["regime", *cols], rows))
    pr(f"\nSessions without valid GEX levels (V5, in \"all\" only): {v5['sessions']} {v5['list']}\n")
    pr(f"Time of day ({pop}, entry fill time CT): trades / net R per session / net R per trade / win rate\n")
    names = list(dict.fromkeys(k for s in cols for k in c[s]["time_of_day"]))
    rows = [(n, *[(lambda x: f"{x['trades']} / {f(x['net_R_per_session'])} / {f(x['net_R_per_trade'])} / {f(x['win_rate'])}")(c[s]["time_of_day"][n])
                 if n in c[s]["time_of_day"] else "-" for s in cols]) for n in names]
    pr(table(["bucket", *cols], rows) + "\n")
    pr(f"Daily table ({pop}): trades / session net R / session dollar P&L\n")
    days = [x["session"] for x in c[cols[0]]["daily_table"]]
    by = {s: {x["session"]: x for x in c[s]["daily_table"]} for s in cols}
    rows = [(d + (" (EXPOSED)" if d in EXPOSED else ""), *[f"{by[s][d]['trades']} / {f(by[s][d]['net_R'])} / {usd(by[s][d]['net_usd'])}" for s in cols])
            for d in days]
    pr(table(["session", *cols], rows) + "\n")


P = []
pr = P.append

# ---------------- report cards
for pop in POPS:
    c = {s: card["cards"][s][pop] for s in S}
    lab = "in-sample, includes 3 exposed sessions (Part 3)" if pop == "ALL" else "registered sensitivity, not independent, not out-of-sample"
    pr(f"### 2.{POPS.index(pop) + 1} {pop} ({c['R1']['sessions']} sessions), replay (in-sample); {lab}\n")
    pr(table(["", *S], card_rows(c, S)) + "\n")
    regime_tod_daily(c, S, pop, 2)

# ---------------- A4 mj_alignment split (R4)
rv = list(csv.DictReader(open(R / "phase3_review" / "phase3_review.csv", newline="", encoding="utf-8")))
LED = {"R1": R / "phase3/R1_A0_full.csv", "R2": R / "phase3/R2_C1_full.csv", "R3": R / "phase3_r3/R3_M0_ledger.csv",
       "R4": R / "phase3_r4/R4_M0_ledger.csv"}
led = {}
for s, p in LED.items():
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        led[(s, r["trade_id"])] = r
MJ = ("plan zone", "PLAN_ALIGNED", "EXPLORATORY_NOT_PLAN_ALIGNED", "other")
mjcol = next((k for k in (rv[0].keys() if rv else []) if k.lower() in ("mj_alignment", "tag_mj_alignment")), None)
pr("### 2.3 R4 by mj_alignment (A4 reporting split, descriptive only, never promoted)\n")
pr(f"Source: `phase3_review.csv` column `{mjcol}` (from diag_exit_trades) and the R4 ledger `realized_net_R`; a missing value = other. "
   "trades / net R per session (denominator = the population's session count) / win rate (R > 0 / trades).\n")
vals_seen = sorted({(r.get(mjcol) or "") for r in rv if r["strategy"] == "R4"}) if mjcol else []
pr(f"mj_alignment values present in the R4 rows: {vals_seen}\n")
rows = []
for pop in POPS:
    keep = set(POPSESS[pop])
    r4 = [r for r in rv if r["strategy"] == "R4" and r["entry_session"] in keep]

    def grp(v):
        if v in MJ[:3]:
            return v
        if v and (v.lower().startswith("plan zone") or "plan-zone trade" in v):   # diag_exit_trades: "NOT_APPLICABLE (plan-zone trade)"
            return "plan zone"
        return "other"
    for g in MJ:
        xs = [float(led[("R4", r["trade_id"])]["realized_net_R"]) for r in r4 if grp((r.get(mjcol) or "") if mjcol else "") == g]
        wr = f(sum(1 for x in xs if x > 0) / len(xs)) if xs else "-"
        rows.append((pop, g, len(xs), f(sum(xs) / len(keep)), wr))
pr(table(["population", "mj_alignment", "trades", "net R per session", "win rate"], rows) + "\n")

# ---------------- C2 card beside R4
pr("### 2.4 C2 R4 card: C2 diagnostic (VWAP as a tag only), not promotable, beside R4\n")
for pop in POPS:
    c = {"R4": card["cards"]["R4"][pop], "C2 R4": card_c2["cards"]["R4"][pop]}
    pr(f"{pop} ({c['R4']['sessions']} sessions):\n")
    pr(table(["", "R4", "C2 R4"], card_rows(c, ("R4", "C2 R4"))) + "\n")
    regime_tod_daily(c, ("R4", "C2 R4"), pop, 2)
from book1a.book1_import import jeron_engine  # noqa: E402,F401
from jeron_engine import arms                  # noqa: E402
rd = lambda p: PC.read_rows(p)                 # noqa: E731
r4m = PC.map_trades(rd(R / "phase3_r4/R4_M0_ledger.csv"), rd(R / "phase3_r4/R4_attempts.csv"), rd(R / "phase3_r4/R4_retests.csv"), "R4")
c2m = PC.map_trades(rd(R / "phase3_r4_c2/R4_M0_ledger.csv"), rd(R / "phase3_r4_c2/R4_attempts.csv"), rd(R / "phase3_r4_c2/R4_retests.csv"), "C2 R4")
for pop in POPS:
    keep = set(POPSESS[pop])
    d = arms.differing_trades([t for t in c2m if t["date"] in keep], [t for t in r4m if t["date"] in keep])
    pr(f"C2 R4 trades that differ from R4, {pop} (arms.differing_trades, matched by date and signal time): removed {d['removed']}, "
       f"admitted {d['admitted']}, entered / exited differently {d['exited_differently']}, total {d['total']}\n")
bm = json.loads((CODE / "Book1A/Phase3/plans_phase3_c2/plan_build_manifest.json").read_text(encoding="utf-8")) \
    if (CODE / "Book1A/Phase3/plans_phase3_c2/plan_build_manifest.json").exists() else None
pr("C2 plans that differ from base: 41 of 41 (`families=` field); decision zones 158 (base) -> 156 (C2); decision-zone set "
   "changes on 15 days (Step A, registration section 4; plan structure only).\n")

# ---------------- stress
pr("### 3. Stress (separate from the baseline)\n")
for pop in POPS:
    rows = []
    for s in S:
        b = card["cards"][s][pop]
        rows.append((s, "baseline (v3.5)", b["trades"], f(b["net_R_per_session"]), f"[{f(b['net_R_per_session_ci90'][0])}, {f(b['net_R_per_session_ci90'][1])}]",
                     f(b["max_drawdown_R"]), usd(b.get("max_drawdown_usd")) if s in ("R3", "R4") else "-"))
        for k in ("lat1000", "slip2", "slip4"):
            x = b["stress"][k]
            rows.append((s, k, x["trades"], f(x["net_R_per_session"]), f"[{f(x['net_R_per_session_ci90'][0])}, {f(x['net_R_per_session_ci90'][1])}]",
                         f(x["max_drawdown_R"]), usd(x.get("max_drawdown_usd")) if s in ("R3", "R4") else "-"))
    pr(f"{pop}:\n")
    pr(table(["strategy", "setting", "trades", "net R per session", "90% CI", "max DD R", "max DD USD"], rows) + "\n")

# ---------------- comparisons
pr("### 5. Primary comparisons (registration section 5; jeron_engine.arms.promotion unchanged)\n")
for cid in ("P1", "P2", "P3"):
    x = cmp_["comparisons"][cid]
    pr(f"**{cid} {x['arm']} vs {x['comparator']}** - deciding population ALL; sensitivity: **{x['sensitivity']}**\n")
    rows = []
    for pop in POPS:
        y = x[pop]
        d = y["differing"]
        ch = y["checks"]
        rows.append((pop + (f" ({x['label_ALL']})" if pop == "ALL" else f" ({x['label_UNEXPOSED']})"), y["sessions"], f(y["mean_diff_per_session"]),
                     f"[{f(y['ci90_low'])}, {f(y['ci90_high'])}]", f"{f(y['max_dd_arm'])} / {f(y['max_dd_a0'])}",
                     f"{d['total']} (removed {d['removed']}, admitted {d['admitted']}, different {d['exited_differently']})",
                     f(y.get("mean_diff_per_session_2tick")),
                     ", ".join(f"{k} {v}" for k, v in ch.items()), f"**{y['verdict']}**"))
    pr(table(["population", "sessions", "mean paired diff R / session", "90% CI (5th, 95th)", "max DD arm / comparator R",
              "trades that differ", "2-tick mean diff", "checks", "verdict"], rows) + "\n")

# paired daily results (from the report-card daily tables, the same session net R that arms.per_session sums)
pr("Paired daily results, ALL (session net R arm - comparator; from the report-card daily tables)\n")
by = {s: {x["session"]: x for x in card["cards"][s]["ALL"]["daily_table"]} for s in S}
rows = []
for d in SESS:
    rows.append((d + (" (EXPOSED)" if d in EXPOSED else ""), *[f(by[a][d]["net_R"] - by[b][d]["net_R"]) for _, a, b in PC.COMPARISONS]))
pr(table(["session", "P1 R4-R1", "P2 R4-R3", "P3 R3-R2"], rows) + "\n")
for cid, a, b in PC.COMPARISONS:
    pr(f"{cid} RISK_REJECT / RISK_BREACH_FILL (ALL): {a} {card['cards'][a]['ALL']['risk']['risk_reject'] if a in ('R3', 'R4') else '-'} / "
       f"{card['cards'][a]['ALL']['risk']['risk_breach_fill'] if a in ('R3', 'R4') else '-'}; {b} "
       f"{card['cards'][b]['ALL']['risk']['risk_reject'] if b in ('R3', 'R4') else '-'} / {card['cards'][b]['ALL']['risk']['risk_breach_fill'] if b in ('R3', 'R4') else '-'}\n")

# ---------------- section 3 classes and tags
pr("### 4.1 Class counts per strategy\n")
CL = ("GAVE_BACK", "STOP_THEN_TARGET", "NO_POST_STOP_FOLLOW_THROUGH", "UNCLASSIFIED", "NOT_STOPPED")
for pop in POPS:
    pr(f"{pop}:\n")
    pr(table(["class", *S], [(k, *[cls["classes"][s][pop]["counts"][k] for s in S]) for k in CL]) + "\n")
cut = cls["classes"]["R1"]["ALL"]["tercile_cutoffs"]
pr("Tercile cut-offs (one set from the 41 sessions' own values, both populations): " +
   "; ".join(f"{k} T1 <= {f(v[0], 4)} < T2 <= {f(v[1], 4)} < T3" for k, v in cut.items()) + "\n")
TAGS = ["gamma_regime", "hvl_side", "pin_zone", "pc_gamma_ratio_tercile", "cr_ps_width_tercile", "mj_alignment", "L1_PLAN_SIDE",
        "market_context_premarket", "draw_status_premarket"]
CVD = [f"{p}_{k}_{a}_{r}" for p in ("atentry", "prov", "post") for k in ("high", "low") for a in ("case", "with") for r in ("cvd17", "cvd0830")]
for pop in POPS:
    pr(f"### 4.{2 + POPS.index(pop)} Tag counts per class, {pop} (value count; NA = no diagnostics row or field)\n")
    for s in S:
        t = cls["classes"][s][pop]["tags"]
        used = [k for k in CL if cls["classes"][s][pop]["counts"][k]]
        if not used:
            pr(f"{s}: no trades\n"); continue
        rows = [(tg, *["; ".join(f"{v} {n}" for v, n in t[k].get(tg, {}).items()) or "-" for k in used]) for tg in TAGS + CVD]
        pr(f"{s}:\n")
        pr(table(["tag", *used], rows) + "\n")

pr("### 4.4 Per trade (review fields; the full row set is phase3_review.csv)\n")
rows = []
for r in rv:
    L = led[(r["strategy"], r["trade_id"])]
    rows.append((r["strategy"], r["trade_id"], r["entry_session"] + (" (EXPOSED)" if r["entry_session"] in EXPOSED else ""), L["entry_time"][:8],
                 L["exit_reason"], r["cls"], L["realized_net_R"], r.get("mfe_R", "NA"), r.get("mae_R", "NA"), r.get("post_exit_move_R", "NA"),
                 r.get("post_exit_target_traded", "NA"), r.get("post_exit_truncated", "NA"), r["exit_flag"],
                 r.get("minutes_initiation_to_entry", "NA"), r.get("confirm_delta_pct", "NA")))
pr(table(["strategy", "trade", "entry session", "entry", "exit reason", "class", "net R", "MFE R", "MAE R", "post-stop move R",
          "target traded", "truncated", "exit flag", "min init->entry", "confirm delta %"], rows) + "\n")
ea = [r for r in rv if r["exit_flag"] == "EXIT_AFTER_SESSION_CLOSE"]
pr("EXIT_AFTER_SESSION_CLOSE trades: " + ("; ".join(f"{r['strategy']} {r['trade_id']} entry_session {r['entry_session']}, exit_time_raw "
                                                     f"{r['exit_time_raw']}, exit_time_model {r['exit_time_model']}, holding_min_model "
                                                     f"{r['holding_min_model']}" for r in ea) or "none") + "\n")

# ---------------- diagnostics row counts
pr("### Diagnostics files (phase3_diag_17ac9cd): data rows (excluding the # header line and the column line)\n")
rows = []
for p in sorted(DIAG.glob("*")):
    if p.suffix == ".csv":
        with open(p, encoding="utf-8") as fh:
            n = sum(1 for line in fh if not line.startswith("#")) - 1
        rows.append((p.name, max(n, 0)))
    else:
        rows.append((p.name, "-"))
pr(table(["file", "rows"], rows) + "\n")

# ---------------- hashes
pr("### 7. File sha256\n")
files = ["phase3/R1_A0_full.csv", "phase3/R2_C1_full.csv", "phase3_r3/R3_M0_ledger.csv", "phase3_r4/R4_M0_ledger.csv", "phase3_r4_c2/R4_M0_ledger.csv",
         "phase3/R1_attempts.csv", "phase3/R2_attempts.csv", "phase3/R2_retests.csv", "phase3_r3/R3_attempts.csv", "phase3_r3/R3_retests.csv",
         "phase3_r3/R3_risk_events.json", "phase3_r4/R4_attempts.csv", "phase3_r4/R4_candidates.csv", "phase3_r4/R4_risk_events.json",
         "phase3_r4_c2/R4_attempts.csv", "phase3_r4_c2/R4_candidates.csv", "phase3_r4_c2/R4_risk_events.json"]
files += [f"phase3_stress_{k}/{n}" for k in ("lat1000", "slip2", "slip4") for n in ("R1_A0_full.csv", "R2_C1_full.csv", "R3_M0_ledger.csv",
                                                                                  "R4_M0_ledger.csv", "stress_manifest.json")]
files += ["phase3/run_manifest.json", "phase3_r3/run_manifest.json", "phase3_r4/run_manifest.json", "phase3_r4_c2/run_manifest.json",
          "phase3_report_card.json", "phase3_report_card_c2.json", "phase3_compare/phase3_compare.json"]
files += sorted(str(p.relative_to(R)).replace("\\", "/") for p in (R / "phase3_review").glob("*") if p.is_file())
files += sorted(str(p.relative_to(R)).replace("\\", "/") for p in DIAG.glob("*") if p.is_file())
files += ["report_build/build_phase3_report_md.py"]
files = [p for p in dict.fromkeys(files) if (R / p).exists()]
pr(table(["file (under book1a/Phase3/runs/)", "bytes", "sha256"], [(p, (R / p).stat().st_size, sha(R / p)) for p in files]) + "\n")
if CI.exists():
    cfiles = sorted(str(p.relative_to(CI)).replace("\\", "/") for p in CI.rglob("*") if p.is_file())
    pr(table(["file (under book1a/Phase3/checker_input/)", "bytes", "sha256"], [(p, (CI / p).stat().st_size, sha(CI / p)) for p in cfiles]) + "\n")
print("\n".join(P))
