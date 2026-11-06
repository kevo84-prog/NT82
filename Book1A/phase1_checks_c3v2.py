r"""Mechanical P4 and P5 for the Phase 1 R3 / R4 reruns with risk-c3-v2 (Phase1/risk-c3-v2_registration.md).

  python -m book1a.phase1_checks_c3v2 --runs book1a\Phase1\runs --out Book1A\Phase1\c3v2

Independent of replay_risk: the decision-time quote, stop ticks, N, the estimate, entry risk at fill, the execution
breach and the execution variance are recomputed here from the tape and the logged ledger / attempt columns; the fills
(P5) are recomputed with phase1_checks.recompute. Reads only phase1_checks.SAFE plus the risk-c3-v2 columns from the
ledgers; never net_usd, gross_usd, R columns or the risk-events json. No P&L, R or outcome is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from book1a import phase1_checks as P

VERSION = "phase1-checks-c3v2-v1.0"
V2 = ["risk_impl_version", "risk_decision_time", "risk_ref_source", "risk_entry_ref", "signal_entry_ref", "risk_budget_usd",
      "entry_risk_ticks_at_fill", "entry_risk_at_fill_usd", "execution_variance_ticks", "exec_risk_breach"]
IMPL = "risk-c3-v2"
RUNS = {"R3": ("phase1_r3_c3v2", "R3_M0_ledger.csv", "R3_attempts.csv"),
        "R4": ("phase1_r4_c3v2", "R4_M0_ledger.csv", "R4_attempts.csv")}


def cents_est(stop_ticks: int, n: int) -> int:
    return (stop_ticks + 2) * 500 * n + 574 * n


def max_n_cents(stop_ticks: int, cap_cents: int) -> int:
    n = 0
    while n < 50 and cents_est(stop_ticks, n + 1) <= cap_cents:
        n += 1
    return n


def c(x) -> int:
    return int(round(float(x) * 100))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    runs, out = Path(a.runs), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from jeron_engine import exit_replay as XR
    tape = P.TapeArr(runs / "phase1" / "tape_strategy.csv.gz")
    md = [f"# Book 1A Phase 1: R3 / R4 rerun with {IMPL}, mechanical P4 and P5 ({VERSION})", "",
          "No P&L, R, win rate or outcome is read or written here. Ledger columns read: " + ", ".join(P.SAFE + V2) + ".", ""]
    summary = {}

    md += ["## Ledgers and versions", "", "| strategy | ledger | rows | sha256 | risk_impl_version (rows) | manifest |", "|---|---|---|---|---|---|"]
    led, att, man = {}, {}, {}
    for k, (sub, lf, af) in RUNS.items():
        p = (runs / sub / lf).resolve()
        led[k] = pd.read_csv(p, usecols=lambda col: col in P.SAFE + V2, dtype={"entry_time": str, "exit_time": str, "risk_decision_time": str})
        att[k] = pd.read_csv(runs / sub / af, dtype={"time": str})
        man[k] = json.loads((runs / sub / "run_manifest.json").read_text())
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        summary[k] = dict(ledger=str(p), sha256=sha, rows=len(led[k]))
        impl = led[k]["risk_impl_version"].value_counts().to_dict() if len(led[k]) else {}
        mtxt = ", ".join(f"{x}={man[k].get(x)}" for x in ("version", "commit", "risk_impl_version", "replay_risk_version",
                                                           "ledger_version", "fill_model"))
        md.append(f"| {k} | `{p}` | {len(led[k])} | `{sha}` | {impl} | {mtxt}; manifest sha256 {'= file' if man[k].get('ledger_sha256') == sha else 'DIFFERS'} |")
    md.append("")

    # ---------- P4 ----------
    md += ["## P4 risk mechanics with risk-c3-v2", "",
           "Reference = best ask (long) / best bid (short) from the tape quote at the decision time (last trade at or before "
           "the bar close). Estimate = (stop ticks + 2) x $5 x N + $5.74 x N; N = the largest whole number with estimate <= "
           "min($1,000, remaining daily budget logged at the decision). Entry risk at fill = (|fill - stop| / 0.25 + 2) x $5 x N "
           "+ $5.74 x N; breach = entry risk at fill > that cap. All in integer cents.", "",
           "### Pre-trade decisions (every ACCEPT / RISK_REJECT row)", "",
           "| strategy | event | decision time | side | ref logged / tape | stop ticks | decision | N logged / recomputed | estimate logged / recomputed | cap | impl | check |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    p4_dec_fail = n_dec = 0
    for k in RUNS:
        df = att[k]
        bad_impl = int((df["risk_impl_version"].fillna("") != IMPL).sum()) if "risk_impl_version" in df else len(df)
        summary[k]["attempt_rows"] = len(df); summary[k]["attempt_rows_without_impl"] = bad_impl
        d = df[df.risk_decision.notna() & df.risk_decision.astype(str).str.match(r"ACCEPT|RISK_REJECT")]
        for r in d.itertuples():
            n_dec += 1
            side = 1 if r.risk_ref_source == "BEST_ASK" else -1
            b, a_, _ = tape.quote(np.datetime64(pd.Timestamp(r.time), "us"))
            ref_tape = a_ if side > 0 else b
            st = int(r.risk_stop_ticks)
            cap = min(100_000, c(r.risk_remaining_daily_usd))
            n = max_n_cents(st, cap)
            exp_dec = "ACCEPT" if n >= 1 else "RISK_REJECT"
            exp_est = cents_est(st, max(n, 1))
            nl = 0 if pd.isna(r.risk_contracts) else int(r.risk_contracts)
            ok = (abs(float(r.risk_entry_ref) - ref_tape) < 1e-9 and str(r.risk_decision).startswith(exp_dec) and nl == n
                  and c(r.risk_estimate_usd) == exp_est and c(r.risk_budget_usd) == cap and r.risk_impl_version == IMPL)
            p4_dec_fail += not ok
            md.append(f"| {k} | {r.event} | {r.time} | {'LONG' if side > 0 else 'SHORT'} | {float(r.risk_entry_ref):.2f} / {ref_tape:.2f} | {st} | "
                      f"{r.risk_decision} | {nl} / {n} | {float(r.risk_estimate_usd):.2f} / {exp_est / 100:.2f} | {cap / 100:.2f} | {r.risk_impl_version} | "
                      f"{'MATCH' if ok else 'MISMATCH'} |")
    md.append("")
    md += ["### Trades (every ledger row)", "",
           "| strategy | trade | side | qty | ref | stop | stop ticks from ref (recomputed) | planned estimate | fill | variance ticks logged / recomputed | entry risk at fill logged / recomputed | cap logged / attempt | breach logged / recomputed | check |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    p4_tr_fail = n_breach = 0
    breaches = []
    for k in RUNS:
        df, at = led[k], att[k]
        for r in df.itertuples():
            side = 1 if str(r.side).upper().startswith("L") else -1
            row = at[at.event == r.trade_id].iloc[0]
            st = int(round(abs(float(r.risk_entry_ref) - float(r.stop)) / 0.25))
            cap_att = min(100_000, c(row.risk_remaining_daily_usd))
            fill_t = int(round(abs(float(r.entry_price) - float(r.stop)) / 0.25))
            fill_c = cents_est(fill_t, int(r.qty))
            var = int(round((float(r.entry_price) - float(r.risk_entry_ref)) * side / 0.25))
            br = fill_c > cap_att
            ok = (st == int(row.risk_stop_ticks) and int(r.qty) == int(row.risk_contracts) == max_n_cents(st, cap_att)
                  and c(r.planned_risk_usd) == cents_est(st, int(r.qty)) and c(r.risk_budget_usd) == cap_att
                  and int(r.entry_risk_ticks_at_fill) == fill_t and c(r.entry_risk_at_fill_usd) == fill_c
                  and int(r.execution_variance_ticks) == var and int(r.exec_risk_breach) == int(br)
                  and r.risk_impl_version == IMPL and r.risk_decision == "ACCEPT")
            p4_tr_fail += not ok
            n_breach += br
            if br:
                breaches.append(f"{k} {r.trade_id} ({r.date})")
            md.append(f"| {k} | {r.trade_id} | {r.side} | {r.qty} | {float(r.risk_entry_ref):.2f} | {float(r.stop):.2f} | {st} | {float(r.planned_risk_usd):.2f} | "
                      f"{float(r.entry_price):.2f} | {int(r.execution_variance_ticks)} / {var} | {float(r.entry_risk_at_fill_usd):.2f} / {fill_c / 100:.2f} | "
                      f"{float(r.risk_budget_usd):.2f} / {cap_att / 100:.2f} | {int(r.exec_risk_breach)} / {int(br)} | {'MATCH' if ok else 'MISMATCH'} |")
    md.append("")
    md.append(f"- pre-trade decisions recomputed: {n_dec}, mismatches **{p4_dec_fail}**")
    md.append(f"- trades recomputed: {sum(len(x) for x in led.values())}, mismatches **{p4_tr_fail}** "
              "(planned risk <= cap and qty = N are part of each row's check)")
    md.append(f"- attempt rows without `{IMPL}`: R3 {summary['R3']['attempt_rows_without_impl']} / {summary['R3']['attempt_rows']}, "
              f"R4 {summary['R4']['attempt_rows_without_impl']} / {summary['R4']['attempt_rows']}")
    md.append(f"- qualifying entry risk-budget breaches (registered definition, logged only, listed not judged): {n_breach}"
              + (f": {', '.join(breaches)}" if breaches else ""))
    md.append("")

    # ---------- P5 ----------
    md += ["## P5 fill mechanics (independent tape recompute, every R3 / R4 trade)", "",
           "| strategy | trade | side | qty | bar close + 250 ms | entry ledger / recomputed | exit reason ledger / recomputed | exit time ledger / recomputed | exit price ledger / recomputed | gap-through | result |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    n_ok = n_bad = 0
    for k in RUNS:
        for r in led[k].itertuples():
            x = P.recompute(tape, r, XR.FLATTEN)
            ex_t = P.ts(r.date, r.exit_time) if isinstance(r.exit_time, str) else None
            ok = (x["on_minute"] and abs(x["entry"] - float(r.entry_price)) < 1e-9 and int(r.entry_latency_ms) == 250
                  and P.reason_kind(r.exit_reason) == x["kind"] and abs(x["exit_px"] - float(r.exit_price)) < 1e-9
                  and ex_t is not None and x["exit_t"] is not None and abs((pd.Timestamp(ex_t) - pd.Timestamp(x["exit_t"])).total_seconds()) < 0.001
                  and abs(float(r.commission_usd) - P.COMM_RT * int(r.qty)) < 0.005 and r.fill_model == "v3.5" and int(r.stop_slippage_ticks) == 1)
            n_ok += ok; n_bad += not ok
            md.append(f"| {k} | {r.trade_id} | {r.side} | {r.qty} | {r.date} {r.entry_time} | {float(r.entry_price):.2f} / {x['entry']:.2f} | "
                      f"{r.exit_reason} / {x['kind']} | {P.fmt_t(ex_t)} / {P.fmt_t(x['exit_t'])} | {float(r.exit_price):.2f} / {x['exit_px']:.2f} | "
                      f"{'YES' if x['gap'] else 'no'} | {'MATCH' if ok else 'MISMATCH'} |")
    md.append("")
    md.append(f"- trades checked {n_ok + n_bad}: MATCH {n_ok}, MISMATCH {n_bad}")
    md.append("")
    summary.update(p4_decision_mismatches=p4_dec_fail, p4_trade_mismatches=p4_tr_fail, p5_match=n_ok, p5_mismatch=n_bad,
                   exec_breaches=n_breach)
    (out / "phase1_checks_c3v2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / "phase1_checks_c3v2.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
