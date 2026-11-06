r"""Book 1A Phase 1 shakedown checks (mechanics only; no P&L is read or written).

  python -m book1a.phase1_checks --runs book1a\Phase1\runs --plans Book1A\Phase0\plans_phase1 --out book1a\Phase1

Reads ONLY these ledger columns (never gross / net / R / P&L columns):
  date, entry_time, side, qty, entry_price, stop, target, exit_time, exit_price, exit_reason, risk_decision, trade_id,
  stop_ticks, planned_risk_usd, commission_usd, fill_model, stop_slippage_ticks, entry_latency_ms
and from the S1.4 log only RecordType, EvidenceTimeCT, Detail, plan_context (PLAN rows) and row-type counts.
The risk-event json is not read (it carries realized dollar losses); RISK_BREACH_FILL is taken from the ledger flag.

Writes <out>/phase1_checks.md (P1, P3, P4, P5, P6 evidence) and <out>/day_sheets/day_sheet_<day>.md (P7).
P2 (lookahead) is book1a.audit_run, run separately.

P5 is an independent recompute from the tape (pandas + numpy here, not jeron_engine.exit_replay):
  entry = best ask (long) / bid (short) of the last tape row at or before bar close + 250 ms;
  then, walking tape rows after the entry time grouped by identical timestamp:
  stop  = first row at or beyond the stop (long: price <= stop); fill = min(stop, that price) - 1 tick (long),
          max(stop, that price) + 1 tick (short) (v3.5 gap-through);
  target = first row 1 tick through (long: price >= target + 1 tick); fill = target;
  a timestamp group holding both = stop; commission = $2.87 x qty per side.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

VERSION = "phase1-checks-v1.0"
TICK = 0.25
SAFE = ["date", "entry_time", "side", "qty", "entry_price", "stop", "target", "exit_time", "exit_price", "exit_reason",
        "risk_decision", "trade_id", "stop_ticks", "planned_risk_usd", "commission_usd", "fill_model",
        "stop_slippage_ticks", "entry_latency_ms", "risk_breach_fill"]
CAND_SAFE = ["event", "date", "signal_time_ct", "direction", "setup_family", "status", "is_shadow", "grade",
             "location_type", "location_id", "zone_lo", "zone_hi", "entry_ref", "stop", "target", "gate_reasons",
             "gates_pass", "rh1_state", "t8_veto", "l1_veto", "fz1_would_veto_applied", "single_print_gate",
             "risk_decision", "risk_contracts", "plan_zone_class", "plan_zone_long", "plan_zone_short"]
BUDGET, DAILY, SLIP_ALLOW, TICK_USD, COMM_RT = 1000.0, 2000.0, 2, 5.0, 5.74
SESSIONS = ["2025-10-22", "2025-10-23", "2025-10-24", "2025-10-27", "2025-10-28", "2025-10-29", "2025-10-30",
            "2025-10-31", "2025-11-03", "2025-11-04"]
FLATTEN_CT = dt.time(15, 0)   # replaced below by the engine constant when importable


def est(stop_ticks, n):
    return round((stop_ticks + SLIP_ALLOW) * TICK_USD * n + COMM_RT * n, 2)


def max_n(stop_ticks, cap):
    n = 0
    while est(stop_ticks, n + 1) <= cap + 1e-9:
        n += 1
    return n


def on_tick(x) -> bool:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return True
    return abs(round(float(x) / TICK) * TICK - float(x)) < 1e-9


def ledgers(runs: Path) -> dict:
    files = {"R1": runs / "phase1" / "R1_A0_full.csv", "R2": runs / "phase1" / "R2_C1_full.csv",
             "R3": runs / "phase1_r3" / "R3_M0_ledger.csv", "R4": runs / "phase1_r4" / "R4_M0_ledger.csv"}
    return {k: pd.read_csv(f, usecols=lambda c: c in SAFE, dtype={"entry_time": str, "exit_time": str}) for k, f in files.items()}


def ts(day, hms) -> np.datetime64:
    return np.datetime64(pd.Timestamp(f"{day} {hms}"), "us")


class TapeArr:
    def __init__(self, path: Path):
        df = pd.read_csv(path, usecols=[0, 1, 2, 3], header=0, names=["t", "p", "b", "a"], dtype={"t": str})
        self.t = pd.to_datetime(df["t"].str.slice(0, 26), format="%Y-%m-%d %H:%M:%S.%f").to_numpy().astype("datetime64[us]")
        self.p, self.b, self.a = df["p"].to_numpy(float), df["b"].fillna(0).to_numpy(float), df["a"].fillna(0).to_numpy(float)

    def quote(self, t):
        i = np.searchsorted(self.t, t, side="right") - 1
        return self.b[i], self.a[i], self.t[i]


def recompute(tape: TapeArr, r, flatten: dt.time) -> dict:
    side = 1 if str(r.side).upper().startswith("L") else -1
    t0 = ts(r.date, r.entry_time)
    bar_close = t0 - np.timedelta64(250, "ms")
    on_minute = pd.Timestamp(bar_close).second == 0 and pd.Timestamp(bar_close).microsecond == 0
    b, a, qt = tape.quote(t0)
    entry = a if side > 0 else b
    stop, tgt = float(r.stop), float(r.target) if not pd.isna(r.target) else None
    i = np.searchsorted(tape.t, t0, side="right")
    flat = ts(r.date, flatten.strftime("%H:%M:%S"))
    n = len(tape.t)
    out = dict(kind="DATA_END", exit_t=None, exit_px=np.nan, both=False, gap=False)
    while i < n:
        t = tape.t[i]
        if t >= flat:
            out.update(kind="FLATTEN", exit_t=t, exit_px=tape.b[i - 1] if side > 0 else tape.a[i - 1]); break
        j = np.searchsorted(tape.t, t, side="right")
        pr = tape.p[i:j]
        hs = (pr <= stop) if side > 0 else (pr >= stop)
        ht = np.zeros(len(pr), bool) if tgt is None else ((pr >= tgt + TICK) if side > 0 else (pr <= tgt - TICK))
        if hs.any():
            trig = pr[np.argmax(hs)]
            base = min(stop, trig) if side > 0 else max(stop, trig)
            out.update(kind="STOP", exit_t=t, exit_px=base - side * TICK, both=bool(ht.any()), gap=bool(trig != stop))
            break
        if ht.any():
            out.update(kind="TARGET", exit_t=t, exit_px=tgt); break
        i = j
    return dict(side=side, on_minute=on_minute, entry=entry, quote_t=qt, **out)


def reason_kind(reason: str) -> str:
    s = str(reason).upper()
    for k in ("STOP", "TARGET", "FLATTEN"):
        if k in s:
            return k
    return s


def fmt_t(t):
    return "-" if t is None else pd.Timestamp(t).strftime("%H:%M:%S.%f")[:-3]


def plan_zones(plans: Path, day: str) -> list:
    rows = []
    for line in (plans / f"PreopenPlan_{day}_book1a.txt").read_text().splitlines():
        if line.startswith("zone="):
            p = line[5:].split("|")
            lo, hi = p[0].split("-")
            kv = dict(x.split("=", 1) for x in p[3:] if "=" in x)
            rows.append(dict(lo=float(lo), hi=float(hi), label=p[1], cls=p[2], long=kv.get("long", ""), short=kv.get("short", "")))
    return rows


def plan_kv(plans: Path, day: str) -> dict:
    kv = {}
    for line in (plans / f"PreopenPlan_{day}_book1a.txt").read_text().splitlines():
        if "=" in line and not line.startswith(("#", "zone=", "zone_meta=", "ladder=")):
            k, v = line.split("=", 1)
            kv.setdefault(k, v)
    return kv


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True); ap.add_argument("--plans", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    runs, plans, out = Path(a.runs), Path(a.plans), Path(a.out)
    (out / "day_sheets").mkdir(parents=True, exist_ok=True)
    flatten = FLATTEN_CT
    try:
        from book1a.book1_import import jeron_engine  # noqa: F401
        from jeron_engine import exit_replay as XR
        flatten = XR.FLATTEN
    except Exception:
        pass
    L = ledgers(runs)
    md = [f"# Book 1A Phase 1: mechanics checks ({VERSION})", "",
          "No P&L, R, win rate or dollar result is read or written here. Ledger columns read: " + ", ".join(SAFE) + ".", ""]

    # ---------- P1 ----------
    md += ["## P1 sessions and row types", ""]
    a0_cfg = json.loads((runs / "phase1" / "daily_loop_config.json").read_text())
    md.append(f"- A0 run sessions (daily_loop_config): {len(a0_cfg['sessions'])} = {a0_cfg['sessions'][0]} .. {a0_cfg['sessions'][-1]}; "
              f"equal to the Phase 1 list: {a0_cfg['sessions'] == SESSIONS}")
    for name, sub in (("A0 (R1 / R2 / R3 signals)", "phase1"), ("R4 (Book 1A plans)", "phase1_r4")):
        f = glob.glob(str(runs / sub / "strategy" / "JOFS_*.csv"))[0]
        d = pd.read_csv(f, usecols=["RecordType", "EvidenceTimeCT", "Detail", "plan_context"], dtype=str, low_memory=False)
        days = sorted(set(d.EvidenceTimeCT.dropna().str[:10]) & set(SESSIONS))
        plan = d[d.RecordType == "PLAN"]
        loaded = sorted(set(re.findall(r"PLAN_LOADED id=(\d{4}-\d\d-\d\d)", " ".join(plan.Detail.dropna()))))
        md.append(f"- {name}: S1.4 log rows on {len(days)} / 10 sessions; PLAN_LOADED on {len(loaded)} / 10 "
                  f"({'all' if loaded == SESSIONS else 'MISSING ' + str(sorted(set(SESSIONS) - set(loaded)))})")
        rt = d.RecordType.value_counts()
        md.append(f"  - row types present: {len(rt)}; " + ", ".join(f"{k} {v}" for k, v in sorted(rt.items())))
        if sub == "phase1":
            exp = pd.read_csv(runs / "phase1" / "row_types.csv")
            zero = exp[exp.rows == 0].RecordType.tolist()
            md.append(f"  - expected row types with 0 rows (row_types.csv): {zero or 'none'}")
    for k, df in L.items():
        md.append(f"- {k}: ledger rows {len(df)}, on sessions {sorted(df.date.unique().tolist())}")
    md.append("")

    # ---------- P3 ----------
    md += ["## P3 tick test", ""]
    bad = []
    for k, df in L.items():
        for c in ("entry_price", "stop", "target", "exit_price"):
            for v in df[c]:
                if not on_tick(v):
                    bad.append((k, c, v))
    att = {"R3": pd.read_csv(runs / "phase1_r3" / "R3_attempts.csv"), "R4": pd.read_csv(runs / "phase1_r4" / "R4_attempts.csv"),
           "R1": pd.read_csv(runs / "phase1" / "R1_attempts.csv"), "R2": pd.read_csv(runs / "phase1" / "R2_attempts.csv")}
    n_att = 0
    for k, df in att.items():
        if "px" in df:
            for v in df.px:
                n_att += 1
                if not on_tick(v):
                    bad.append((k, "attempt px", v))
    n_led = sum(len(df) * 4 for df in L.values())
    md.append(f"- ledger prices checked: {n_led} (entry, stop, target, exit on every row); attempt prices: {n_att}; "
              f"off-tick: {len(bad)} {bad if bad else ''}")
    md.append("- plan files: `book1a/tests/test_plan_ticks.py` (run with the unit tests).")
    md.append("")

    # ---------- P4 ----------
    md += ["## P4 risk mechanics (R3, R4)", "",
           "Formula: estimate = (stop ticks + 2) x $5 x N + $5.74 x N; N = largest whole number with estimate <= "
           "min($1,000, remaining daily budget); RISK_REJECT when 1 NQ does not fit.", ""]
    tab = []
    for n in (1, 2, 3, 5, 10):
        m = max(s for s in range(0, 1000) if est(s, n) <= BUDGET)
        tab.append(f"{n} NQ {m}")
    md.append("- largest stop that fits $1,000 (recomputed): " + ", ".join(tab) + " ticks (spec: 196 / 96 / 63 / 36 / 16)")
    md.append("")
    md.append("| strategy | event | time | decision | stop ticks | N logged | N recomputed | estimate logged | estimate recomputed | cap (min budget, remaining) | check |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    p4_fail = 0
    for k in ("R3", "R4"):
        df = att[k]
        df = df[df.risk_decision.notna() & df.risk_decision.str.match(r"ACCEPT|RISK_REJECT")]
        for r in df.itertuples():
            cap = min(BUDGET, float(r.risk_remaining_daily_usd)) if not pd.isna(r.risk_remaining_daily_usd) else BUDGET
            n = max_n(int(r.risk_stop_ticks), cap)
            exp_dec = "ACCEPT" if n >= 1 else "RISK_REJECT"
            exp_est = est(int(r.risk_stop_ticks), max(n, 1))
            ok = r.risk_decision.startswith(exp_dec) and (int(r.risk_contracts) if not pd.isna(r.risk_contracts) else 0) in (n, 0 if n == 0 else n) \
                and abs(float(r.risk_estimate_usd) - exp_est) < 0.011
            if r.risk_decision.startswith("RISK_REJECT"):
                ok = ok and n == 0
            p4_fail += 0 if ok else 1
            md.append(f"| {k} | {r.event} | {r.time} | {r.risk_decision} | {int(r.risk_stop_ticks)} | "
                      f"{'' if pd.isna(r.risk_contracts) else int(r.risk_contracts)} | {n} | {float(r.risk_estimate_usd):.2f} | {exp_est:.2f} | {cap:.2f} | {'MATCH' if ok else 'MISMATCH'} |")
    md.append("")
    viol = []
    for k in ("R3", "R4"):
        df, at = L[k], att[k]
        for r in df.itertuples():
            row = at[at.event == r.trade_id]
            cap = BUDGET
            if len(row) and not pd.isna(row.iloc[0].risk_remaining_daily_usd):
                cap = min(BUDGET, float(row.iloc[0].risk_remaining_daily_usd))
            if float(r.planned_risk_usd) > cap + 1e-9:
                viol.append((k, r.trade_id, r.planned_risk_usd, cap))
            if len(row) and int(row.iloc[0].risk_contracts) != int(r.qty):
                viol.append((k, r.trade_id, "qty != risk_contracts"))
    md.append(f"- planned-risk violations (planned risk above min($1,000, remaining daily) at entry, or size != the logged N): "
              f"**{len(viol)}** {viol if viol else ''}")
    md.append(f"- RISK_REJECT / ACCEPT rows recomputed: mismatches **{p4_fail}**")
    for k in ("R3", "R4"):
        df = L[k]
        br = df[df.risk_breach_fill.astype(str).str.upper().isin(["TRUE", "1", "YES"])] if "risk_breach_fill" in df else df.iloc[0:0]
        md.append(f"- {k} RISK_BREACH_FILL (execution breaches, listed and counted, not judged): {len(br)}"
                  + ("".join(f"; {r.date} {r.trade_id} exit {r.exit_reason} {fmt_t(ts(r.date, r.exit_time))}" for r in br.itertuples()) if len(br) else ""))
    md.append("")

    # ---------- P5 ----------
    md += ["## P5 fill mechanics (independent tape recompute, every trade of R1-R4)", "",
           "| strategy | trade | side | qty | bar close + 250 ms | entry ledger / recomputed | quote row time | stop / target | exit reason ledger / recomputed | exit time ledger / recomputed | exit price ledger / recomputed | gap-through | same-tick stop+target | commission per side | result |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    tapes = {"A0": TapeArr(runs / "phase1" / "tape_strategy.csv.gz")}
    tapes["R4"] = tapes["A0"] if (runs / "phase1_r4" / "tape_strategy.csv.gz").stat().st_size == (runs / "phase1" / "tape_strategy.csv.gz").stat().st_size \
        else TapeArr(runs / "phase1_r4" / "tape_strategy.csv.gz")
    n_match = n_mis = n_stop = n_tgt = n_gap = 0
    for k, df in L.items():
        tp = tapes["R4" if k == "R4" else "A0"]
        for r in df.itertuples():
            c = recompute(tp, r, flatten)
            lk = reason_kind(r.exit_reason)
            ex_t = ts(r.date, r.exit_time) if isinstance(r.exit_time, str) else None
            ok_entry = c["on_minute"] and abs(c["entry"] - float(r.entry_price)) < 1e-9 and int(r.entry_latency_ms) == 250
            ok_exit = lk == c["kind"] and abs(c["exit_px"] - float(r.exit_price)) < 1e-9 and \
                (ex_t is not None and c["exit_t"] is not None and abs((pd.Timestamp(ex_t) - pd.Timestamp(c["exit_t"])).total_seconds()) < 0.001)
            ok_comm = abs(float(r.commission_usd) - COMM_RT * int(r.qty)) < 0.005
            ok = ok_entry and ok_exit and ok_comm and r.fill_model == "v3.5" and int(r.stop_slippage_ticks) == 1
            n_match += ok; n_mis += not ok
            n_stop += c["kind"] == "STOP"; n_tgt += c["kind"] == "TARGET"; n_gap += c["gap"]
            md.append(f"| {k} | {r.trade_id} | {r.side} | {r.qty} | {r.date} {r.entry_time} | {float(r.entry_price):.2f} / {c['entry']:.2f} | "
                      f"{fmt_t(c['quote_t'])} | {float(r.stop):.2f} / {'' if pd.isna(r.target) else f'{float(r.target):.2f}'} | "
                      f"{r.exit_reason} / {c['kind']} | {fmt_t(ex_t)} / {fmt_t(c['exit_t'])} | {float(r.exit_price):.2f} / {c['exit_px']:.2f} | "
                      f"{'YES' if c['gap'] else 'no'} | {'YES' if c['both'] else 'no'} | {float(r.commission_usd) / 2 / int(r.qty):.3f} | {'MATCH' if ok else 'MISMATCH'} |")
    md.append("")
    md.append(f"- trades checked {n_match + n_mis}: MATCH {n_match}, MISMATCH {n_mis}; stops {n_stop}, targets {n_tgt}, gap-through {n_gap}")
    md.append("")

    # ---------- P6 ----------
    md += ["## P6 context mechanics (R4)", "",
           "| day | plan market_context | plan context= (S1.4) | PLAN_ACTIVE context | context_source | draw_status | invalidate_below / above | PLAN_CONTEXT_CHANGE rows | longest run of 1-minute closes beyond the line after 08:25 CT | check |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    f = glob.glob(str(runs / "phase1_r4" / "strategy" / "JOFS_*.csv"))[0]
    d = pd.read_csv(f, usecols=["RecordType", "EvidenceTimeCT", "Detail", "Price"], dtype=str, low_memory=False)
    pr = d[d.RecordType == "PLAN"]
    bars = pd.read_csv(runs / "phase1" / "nq_1m.csv", parse_dates=["time_end_local"])
    p6_fail = 0
    for day in SESSIONS:
        kv = plan_kv(plans, day)
        act = pr[pr.EvidenceTimeCT.fillna("").str.startswith(day) & pr.Detail.str.startswith("PLAN_ACTIVE")].Detail.tolist()
        chg = pr[pr.EvidenceTimeCT.fillna("").str.startswith(day) & pr.Detail.str.startswith("PLAN_CONTEXT_CHANGE")]
        inv_b, inv_a = kv.get("invalidate_below", "-"), kv.get("invalidate_above", "-")
        run_txt = "-"
        longest = 0
        day_bars = bars[(bars.time_end_local > pd.Timestamp(f"{day} 08:25")) & (bars.time_end_local <= pd.Timestamp(f"{day} 15:00"))]
        for lab, line in (("below", inv_b), ("above", inv_a)):
            if line == "-":
                continue
            lv = float(line.split("|")[0])
            beyond = (day_bars.close < lv) if lab == "below" else (day_bars.close > lv)
            cur = 0
            for x in beyond:
                cur = cur + 1 if x else 0
                longest = max(longest, cur)
            run_txt = f"{lab} {lv:.2f}: {longest}"
        act_ctx = act[0].split("=", 1)[1] if act else "MISSING"
        ok = act_ctx == kv.get("context") and ((longest >= 3) == (len(chg) > 0))
        p6_fail += not ok
        chg_txt = "; ".join(f"{r.EvidenceTimeCT} {r.Detail}" for r in chg.itertuples()) or "0"
        md.append(f"| {day} | {kv.get('market_context')} | {kv.get('context')} | {act_ctx} | {kv.get('context_source')} | "
                  f"{kv.get('draw_status')} | {inv_b} / {inv_a} | {chg_txt} | {run_txt} | {'MATCH' if ok else 'MISMATCH'} |")
    md.append("")
    md.append(f"- days checked 10, mismatches **{p6_fail}**. A switch needs 3 consecutive 1-minute closes strictly beyond the line "
              "(S1.4 `UpdatePlanState`, AcceptBars = 3); bars used: the run's nq_1m.csv, bars closing after 08:25 CT up to 15:00 CT.")
    (out / "phase1_checks.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---------- P7 day sheets ----------
    cand = pd.read_csv(runs / "phase1_r4" / "R4_candidates.csv", usecols=lambda c: c in CAND_SAFE, dtype=str, low_memory=False)
    for day in SESSIONS:
        kv = plan_kv(plans, day)
        s = [f"# Day sheet {day} (Book 1A Phase 1, {VERSION})", "",
             "Mechanics only. No P&L column. Times CT. Plan = the frozen `plans_phase1` file (sha256 checked before the run).", "",
             f"Plan: market_context={kv.get('market_context')}, context={kv.get('context')}, context_source={kv.get('context_source')}, "
             f"draw_status={kv.get('draw_status')}, draw={kv.get('draw', '-')}, invalidate_below={kv.get('invalidate_below', '-')}, "
             f"invalidate_above={kv.get('invalidate_above', '-')}, balance={kv.get('balance', '-')}, review={kv.get('review')}", "",
             "## Zones (08:10 CT)", "", "| lo | hi | label | class | long | short |", "|---|---|---|---|---|---|"]
        for z in plan_zones(plans, day):
            s.append(f"| {z['lo']:.2f} | {z['hi']:.2f} | {z['label']} | {z['cls']} | {z['long']} | {z['short']} |")
        c = cand[(cand.date == day) & (cand.is_shadow.isin(["0", "False", "false"]))]
        s += ["", "## R4 candidates", "",
              f"Non-shadow candidates: {len(c)}; passed the S1.4 gates: {int((c.gates_pass == '1').sum())}.", "",
              "### Candidates that passed the S1.4 gates (veto, retest and risk outcome)", "",
              "'risk check' and 'N' are the candidate log's own check of each candidate on its own (from the entry "
              "reference, before the day's trades, halts or the one-position rule). Whether R4 sent an order is in the "
              "Trades table below.", "",
              "| time | dir | setup | location | zone | entry ref | stop | target | status | T8 veto | L1 veto | FZ1 (logged) | RH1 | risk check | N |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in c[c.gates_pass == "1"].itertuples():
            s.append(f"| {r.signal_time_ct} | {r.direction} | {r.setup_family} | {r.location_id} | {r.zone_lo}-{r.zone_hi} | {r.entry_ref} | "
                     f"{r.stop} | {r.target} | {r.status} | {r.t8_veto} | {r.l1_veto} | {r.fz1_would_veto_applied} | {r.rh1_state} | "
                     f"{r.risk_decision} | {r.risk_contracts} |")
        fz = c[c.location_type.fillna("").str.startswith("FROZEN_PREOPEN") & (c.gates_pass != "1")]
        s += ["", "### Plan-zone candidates that failed a gate (count by zone, direction and first gate reason)", "",
              "| zone | dir | first gate reason | count | first time | last time |", "|---|---|---|---|---|---|"]
        if len(fz):
            fz = fz.assign(first=fz.gate_reasons.fillna("").str.split(r"[;|]").str[0].str.strip())
            for (loc, dr, fr), g in fz.groupby(["location_id", "direction", "first"]):
                s.append(f"| {loc} | {dr} | {fr} | {len(g)} | {g.signal_time_ct.min()} | {g.signal_time_ct.max()} |")
        s += ["", "## Trades (entry / stop / target / exit; no P&L)", "",
              "| strategy | trade | side | N | entry time | entry | stop | target | exit time | exit | exit reason | risk |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for k, df in L.items():
            for r in df[df.date == day].itertuples():
                s.append(f"| {k} | {r.trade_id} | {r.side} | {r.qty} | {r.entry_time} | {float(r.entry_price):.2f} | {float(r.stop):.2f} | "
                         f"{'' if pd.isna(r.target) else f'{float(r.target):.2f}'} | {r.exit_time} | {float(r.exit_price):.2f} | {r.exit_reason} | {r.risk_decision} |")
        (out / "day_sheets" / f"day_sheet_{day}.md").write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"phase1 checks written -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
