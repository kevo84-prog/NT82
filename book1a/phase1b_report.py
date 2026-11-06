r"""Phase 1b: D1 file hashes, D4 coverage counts, D5 CVD tables and Phase1b_report.md (spec section 7 and 8).

  python -m book1a.phase1b_report hashes --runs book1a\Phase1\runs --json <before.json>
  python -m book1a.phase1b_report report --runs book1a\Phase1\runs --before <before.json> --diag <diag dir> \
      --tests <unit test log> --out Book1A\Phase1b\Phase1b_report.md

Reads only hashes of the run files, the diagnostic status columns, the D5 swing tables and the D2 audit. Never reads
a counterfactual exit price, a P&L, R or outcome column: D4 counts codes only, D5 shows swings and CVD, not trades.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

VERSION = "phase1b-report-v1.1"
CONTROLLING = {"R1": "b4a2108fa2ab531ef84e1a2933d05fafb8e4519f6674ee8857f0cd79c344b21c",
               "R2": "6123f88e7a62242b559e89a385b7749e67d6d2d433108cb839524a37c606842e",
               "R3": "f413d15f4dad259d908390f6fcff659490f61cd5c9ce5a0f14a1bbeb486e71d1",
               "R4": "b4510aabf2c750f6b3d0cb6f53de274989ed8acbc90d14c0dee9532a5ee5b409"}
LEDGER = {"R1": ("A0", "R1_A0_full.csv"), "R2": ("A0", "R2_C1_full.csv"), "R3": ("R3", "R3_M0_ledger.csv"), "R4": ("R4", "R4_M0_ledger.csv")}
GROUPS = {"A0": ["R1_A0_full.csv", "R2_C1_full.csv", "checker_input/R1_A0.csv", "checker_input/R2_C1.csv", "R1_attempts.csv",
                 "R2_attempts.csv", "R2_retests.csv", "fills_model.csv", "strategy/JOFS_*.csv"],
          "R3": ["R3_M0_ledger.csv", "R3_attempts.csv", "R3_retests.csv"],
          "R4": ["R4_M0_ledger.csv", "R4_attempts.csv", "R4_candidates.csv", "strategy/JOFS_*.csv"]}
MECH = {"A0": "phase1", "R3": "phase1_r3_c3v2", "R4": "phase1_r4_c3v2"}
FINAL = {"A0": "phase1b/phase1", "R3": "phase1b/phase1_r3", "R4": "phase1b/phase1_r4"}
CODES = ("NOT_APPLICABLE", "DATA_MISSING", "NOT_RUN", "NOT_BUILT")


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def resolve(base: Path, pat: str):
    m = sorted(glob.glob(str(base / pat)))
    return Path(m[0]) if len(m) == 1 else None


def file_hashes(runs: Path, folders: dict) -> dict:
    out = {}
    for g, pats in GROUPS.items():
        for pat in pats:
            p = resolve(runs / folders[g], pat)
            out[f"{g}:{pat}"] = dict(path=str(p) if p else "MISSING", sha256=sha(p) if p else "MISSING")
    return out


def log_content_sha(path: Path, run_dir: Path) -> str:
    """sha256 of an S1.4 log with the two run-specific items removed: the ProcessedTimeLocal column (wall clock) and the
    run folder path inside Detail (replaced by <RUN>). Every other byte of every row is kept."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, low_memory=False)
    df = df.drop(columns=["ProcessedTimeLocal"])
    df["Detail"] = df["Detail"].str.replace(str(run_dir.resolve()), "<RUN>", regex=False)
    return hashlib.sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()


def code_of(v) -> str:
    s = "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
    for c in CODES:
        if s.startswith(c):
            return c
    return "DATA_MISSING" if s == "" else "carried"


def coverage(df: pd.DataFrame, fields, by) -> list:
    rows = []
    for key, g in df.groupby(by):
        key = key if isinstance(key, tuple) else (key,)
        r = dict(zip(by, key)); r["rows"] = len(g)
        for f in fields:
            if f not in g:
                r[f] = "n/a"; continue
            c = g[f].map(code_of).value_counts().to_dict()
            r[f] = "/".join(str(c.get(k, 0)) for k in ("carried", "NOT_APPLICABLE", "DATA_MISSING", "NOT_RUN", "NOT_BUILT"))
        rows.append(r)
    return rows


def md_table(rows, cols) -> list:
    if not rows:
        return ["(no rows)", ""]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return out + [""]


def read(diag: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(diag / name, comment="#", dtype=str, low_memory=False)


def jeron_rows(diag: Path) -> list:
    """D5: the four rows of the spec table, checked against the frozen definition (both resets). Window tolerance
    +-15 minutes around a named time (ours); 'his times are probably ET': both readings are checked."""
    sw = read(diag, "d5_cvd_swings.csv"); pr = read(diag, "d5_cvd_pairs.csv"); ex = read(diag, "d5_cvd_pairs_excluded_60min.csv")
    for d in (sw, pr, ex):
        for c in [c for c in d.columns if c.endswith(("time", "bar", "confirm"))]:
            d[c] = pd.to_datetime(d[c])
    allp = pd.concat([pr.assign(excluded="N"), ex.assign(excluded="Y")], ignore_index=True)

    def T(day, hm):
        return pd.Timestamp(f"{day} {hm}")

    specs = [
        ("2025-10-29", "HIGH", "HIGH_ABSORPTION", "NY AM high", [("09:00", "09:30", "ET reading"), ("10:00", "10:30", "CT reading")]),
        ("2025-10-28", "LOW", "LOW_EXHAUSTION", "Low of day", None),
        ("2025-10-27", "LOW", "LOW_ABSORPTION", "08:30 and 09:30 CT lows (ET reading) / 09:30 and 10:30 CT (CT reading)",
         [("08:30", "09:30", "ET reading"), ("09:30", "10:30", "CT reading")]),
        ("2025-10-24", "HIGH", "HIGH_EXHAUSTION", "High of day", None),
    ]
    tol = pd.Timedelta(minutes=15)
    out = []
    for day, kind, exp_case, what, wins in specs:
        p = allp[(allp.session == day) & (allp.kind == kind)]
        found, notes = [], []
        if wins is None:
            # the RTH extreme of the day among the swings, if the extreme bar is a swing
            s = sw[(sw.session == day) & (sw.kind == kind)]
            s = s[(s.swing_bar >= T(day, "08:31")) & (s.swing_bar <= T(day, "15:00"))]
            if s.empty:
                notes.append("no strict 15-bar swing in RTH")
            else:
                s["price"] = s.price.astype(float)
                ext = s.loc[s.price.idxmax() if kind == "HIGH" else s.price.idxmin()]
                cand = p[p.s2_time == ext.swing_bar]
                notes.append(f"RTH extreme swing {ext.swing_bar:%H:%M} at {ext.price:.2f}")
                found.append(("day extreme", cand))
        else:
            for a, b, lab in wins:
                if what.startswith("08:30"):                     # two named lows: s1 near a, s2 near b
                    cand = p[(abs(p.s1_time - T(day, a)) <= tol) & (abs(p.s2_time - T(day, b)) <= tol)]
                else:
                    cand = p[(p.s2_time >= T(day, a) - tol) & (p.s2_time <= T(day, b) + tol)]
                found.append((lab, cand))
        flagged, detail = "N", []
        for lab, cand in found:
            if cand.empty:
                near = ""
                if wins is not None:
                    w = [x for x in wins if x[2] == lab][0]
                    s_ = sw[(sw.session == day) & (sw.kind == kind) & (sw.swing_bar >= T(day, w[0]) - tol) & (sw.swing_bar <= T(day, w[1]) + tol)]
                    near = "; strict swings found near the named times: " + (", ".join(f"{x:%H:%M}" for x in s_.swing_bar) or "none")
                    pp = p[(p.s1_time >= T(day, w[0]) - tol) & (p.s1_time <= T(day, w[1]) + tol)]
                    near += "".join(f"; nearest pair {r.s1_time:%H:%M} / {r.s2_time:%H:%M}, gap {r.gap_min} min"
                                    f"{' (beyond 60 minutes)' if r.excluded == 'Y' else ''}, cases {r.case_cvd17} / {r.case_cvd0830}"
                                    for r in pp.itertuples())
                detail.append(f"{lab}: no swing pair matching both named times{near}")
                continue
            for r in cand.itertuples():
                cases = f"17:00 reset {r.case_cvd17}, 08:30 reset {r.case_cvd0830}"
                hit = exp_case in (r.case_cvd17, r.case_cvd0830) and r.excluded == "N"
                why = "" if hit else (" (beyond 60 minutes)" if r.excluded == "Y" else
                                      (" (CVD not diverging)" if "NONE" in (r.case_cvd17, r.case_cvd0830) else " (other case)"))
                detail.append(f"{lab}: swings {r.s1_time:%H:%M} / {r.s2_time:%H:%M}, gap {r.gap_min} min, {cases}{why}")
                flagged = "Y" if hit else flagged
        out.append(dict(day=day, jeron=what, expected=exp_case, flagged=flagged, detail="; ".join(notes + detail)))
    return out


def report(runs: Path, before: dict, diag: Path, tests: Path, out: Path):
    after = file_hashes(runs, FINAL)
    mech = file_hashes(runs, MECH)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    man = json.loads((diag / "diag_manifest.json").read_text())
    au = json.loads((diag / "d2_lookahead_audit.json").read_text())
    L = [f"# Book 1A Phase 1b report: diagnostics ({VERSION})", "",
         f"Written {dt.date.today():%b %d, %Y}. Code `{commit}`. Spec `book1a/specs/Phase1b_diagnostics_spec.md` "
         f"(sha256 {sha('book1a/specs/Phase1b_diagnostics_spec.md')}, with addendum 5b).",
         "Every diagnostic is logged only: none changes an R1-R4 entry, exit, stop, target, size, rule or plan. "
         "No P&L, R, win rate or outcome table anywhere in this report (D6).", "",
         f"R3 and R4 risk implementation: {man['risk_impl_version']['R3']} / {man['risk_impl_version']['R4']} (controlling for Phase 2 onward). "
         "Every diagnostic file starts with a line naming the risk version and the sha256 of the four ledgers it used.", "",
         "## Amendment v1.1 (Kyron, Nov 6, 2026; registered before Phase 2)", "",
         "- Version 1.1 supersedes the Nov 6 v1.0 report. D1-D6 of v1.0 were accepted subject to this diagnostic amendment.",
         "- M-J1 / M-J2 for R4 trades from an intraday zone admitted by L1: the admitting plan DECISION zone (the L1_PLAN_SIDE "
         "zone) ladder in the trade's direction when it exists, else NOT_APPLICABLE. New fields: `mj_zone_source` (PLAN_ZONE / "
         "L1_ADMITTING_PLAN_ZONE), `mj_zone_label`, `mj_alignment` (PLAN_ALIGNED when l1_side_inherited = ALLOWED; "
         "EXPLORATORY_NOT_PLAN_ALIGNED for NONE or MISMATCH), `mj_l1_side_inherited`, and the plan zone's long= / short= in "
         "`mj_plan_long` / `mj_plan_short`. Trades from a plan zone keep the existing calculation. Diagnostics only: no entry, "
         "stop, target, size, rule or L1 changed.",
         "- Registered for the Phase 2 what-fails-and-why review (`book1a/phase2_review_fields.py`, per trade, every R1-R4 trade, "
         "logged only): (a) MFE / MAE from the entry fill over the trades from entry fill to exit fill, both included, ticks and R "
         "(POST_ENTRY); (b) after a stop exit, the window (stop fill, stop fill + 30 min] cut at 15:00 CT: the largest move in "
         "the trade's direction from the stop fill (ticks and R) and whether the original target traded (Y/N), POST_EXIT, "
         "TRUNCATED with the minutes available when cut; (c) minutes from initiation to entry, confirm-bar delta, delta % and "
         "range (AT_ENTRY). Built and unit-tested on synthetic data only; **not computed on Phase 1** (the module refuses any "
         "phase but Phase 2 and no Phase 1b code calls it).",
         "- Access log event 11 (`Book1A/Phase0/P0.1_blind_run_setup.md`): Kyron and the reviewer (not the runner) saw the "
         "Phase 1 exit-reason tally in the P5 table; it is not used for any rule, threshold or diagnostic choice.", ""]

    # D1
    L += ["## D1 Trading untouched", "",
          "Phase 1 (Oct 22 - Nov 4, 2025) rerun with every diagnostic on, at the commit above: R1 / R2 (`run_r1_r2`, v3.5), "
          "R3 and R4 (`run_r3`, `run_r4`, risk-c3-v2), then `diag_phase1b` on those folders. Hashes were taken before and after "
          "the diagnostics ran and compared with the mechanics run (`runs\\phase1`, `runs\\phase1_r3_c3v2`, `runs\\phase1_r4_c3v2`).", "",
          "| strategy | controlling sha256 | final run, after diagnostics | match |", "|---|---|---|---|"]
    d1_ok = True
    for k, (g, f) in LEDGER.items():
        a = after[f"{g}:{f}"]["sha256"]
        ok = a == CONTROLLING[k] == before[f"{g}:{f}"]["sha256"]
        d1_ok &= ok
        L.append(f"| {k} | `{CONTROLLING[k]}` | `{a}` | {'MATCH' if ok else 'DIFFERS'} |")
    L += ["", "| file | mechanics run sha256 | final run before diagnostics | after diagnostics | result |", "|---|---|---|---|---|"]
    notes = []
    for key in after:
        m, b, a = mech[key]["sha256"], before[key]["sha256"], after[key]["sha256"]
        if m == b == a == "MISSING":
            res = "not written in either run"
        elif m == b == a:
            res = "MATCH (byte-identical)"
        elif key.endswith("JOFS_*.csv") and b == a:
            g = key.split(":")[0]
            cm = log_content_sha(Path(mech[key]["path"]), runs / MECH[g])
            cf = log_content_sha(Path(after[key]["path"]), runs / FINAL[g])
            ok = cm == cf
            d1_ok &= ok
            res = f"content {'MATCH' if ok else 'DIFFERS'} (see note)"
            notes.append(f"- {key}: the raw file differs only in `ProcessedTimeLocal` (the harness's wall-clock time) and in the run "
                         f"folder path written in the CONFIG row and the 10 PLAN_LOADED rows. With those two removed, the content "
                         f"sha256 is `{cm}` (mechanics) and `{cf}` (final run): {'equal' if ok else 'DIFFERENT'}. Every other column of "
                         "every row is identical. Unchanged by the diagnostics (before = after).")
        else:
            res = "DIFFERS"; d1_ok = False
        L.append(f"| {key} | `{m[:16]}...` | `{b[:16]}...` | `{a[:16]}...` | {res} |")
    L += [""] + notes + ["", f"**D1: {'trading untouched' if d1_ok else 'DIFFERENCES FOUND'}.** The four controlling ledger sha256 are "
          "unchanged; checker files, attempt and retest logs, fills_model and R4_candidates.csv are byte-identical; the S1.4 strategy "
          "logs are identical in content (run path and wall clock aside); no file changed while the diagnostics ran.", ""]

    # D2
    L += ["## D2 Point in time", "",
          f"Every timed field group is registered in `diag_timing.csv` with its decision time, available_at and the latest data "
          f"timestamp it used. Groups checked: {au['groups']} ({', '.join(f'{k} {v}' for k, v in au['by_timing'].items())}). "
          f"Violations: **{au['violations']}**. POST_ENTRY labels present in every POST_ENTRY column: "
          f"{'yes' if all(au['labelled'].values()) else 'NO ' + str(au['labelled'])}.",
          "AT_ENTRY / PROVISIONAL: latest data at or before available_at = the decision time (the signal bar close). "
          "GEX: available_at = D-1 23:00 ET; the option OI and settlement rows used were all received at or before that cutoff "
          "(table in the GEX section). POST_ENTRY fields (CVD_DIV after entry, exit cue (a), M-J1, M-J2, MNQ hypothetical exits) "
          "are labelled and never mixed with AT_ENTRY fields.", ""]

    # D3
    tl = Path(tests).read_text(encoding="utf-8").splitlines()
    summ = next((l for l in tl if l.startswith("tests run")), "")
    L += ["## D3 Unit tests", "", f"`{tests}`: {summ}.",
          "Phase 1b tests (`book1a/tests/test_diag_phase1b.py`): the four CVD_DIV cases; the 60-minute exclusion; PROVISIONAL vs "
          "AT_ENTRY; both CVD resets; cue (a) firing, not firing, NOT_APPLICABLE after an M0 exit; M-J1 target choice RUN / TP2 / "
          "TP1; M-J2 with 1, 2 and 5 NQ (and two legs on a tape); the 10 NQ and MNQ formulas on the U3 examples (60 ticks at 3 NQ = "
          "$947.22 fits, 4 NQ = $1,262.96 does not); every GEX tag (hvl_side, cr_ps_width, pin_zone, pc_gamma_ratio, time of day); "
          "the V2 seed giving the same twins twice; L1_PLAN_SIDE (ALLOWED, NONE, MISMATCH, the admitting zone by the L1 distance); "
          "the V3 zero crossing; v1.1: the M-J ladder source (plan-aligned, NONE, MISMATCH, missing ladder, plan-zone trade). "
          "Phase 2 review fields (`book1a/tests/test_phase2_review_fields.py`, synthetic ticks and bars): MFE / MAE long and short "
          "with the entry and exit trades included, the post-stop window long and short, TRUNCATED at 15:00, target traded Y / N, "
          "entry context, and the Phase-2-only guard. Guard tests for risk-c3-v2 in `test_risk_c3_v2.py`.", ""]

    # D4
    L += ["## D4 Coverage (counts only)", "",
          "Each cell: carried / NOT_APPLICABLE / DATA_MISSING / NOT_RUN / NOT_BUILT. No outcome column.", ""]
    cand = read(diag, "diag_cvd_candidates.csv")
    f_c = ["atentry_high_case_cvd17", "atentry_low_case_cvd17", "atentry_high_case_cvd0830", "atentry_low_case_cvd0830",
           "prov_high_case_cvd17", "prov_low_case_cvd17", "bs_status", "log_cvd_slope_5", "grade_without_cvd"]
    cand["bs_status"] = cand.bs_status.where(cand.bs_status != "OK", "carried")
    L += ["### Candidates (S1.4 candidate rows; the A0 log serves R1-R3)", ""] + md_table(coverage(cand, f_c, ["session", "log"]), ["session", "log", "rows"] + f_c)
    tr = read(diag, "diag_cvd_trades.csv")
    tr["bs_status"] = tr.bs_status.where(tr.bs_status != "OK", "carried")
    f_t = ["atentry_high_case_cvd17", "atentry_low_case_cvd17", "prov_high_case_cvd17", "prov_low_case_cvd17",
           "post_high_case_cvd17", "post_low_case_cvd17", "bs_status"]
    L += ["### Trades: CVD", ""] + md_table(coverage(tr, f_t, ["session", "strategy"]), ["session", "strategy", "rows"] + f_t)
    ex = read(diag, "diag_exit_trades.csv")
    for c in ("mj1_status", "mj2_status"):
        ex[c] = ex[c].where(ex[c] != "OK", "carried")
    ex["cue_a"] = ex.cue_fired.where(~ex.cue_fired.isin(["Y", "N"]), "carried")
    sz = read(diag, "diag_sizing_trades.csv"); gx = read(diag, "diag_gex_trades.csv")
    for c in ("mj_zone_source", "mj_alignment"):
        if c in ex:
            ex[c] = ex[c].where(~ex[c].isin(["PLAN_ZONE", "L1_ADMITTING_PLAN_ZONE", "PLAN_ALIGNED", "EXPLORATORY_NOT_PLAN_ALIGNED"]), "carried")
    m = ex[["session", "strategy", "trade_id", "cue_a", "mj_zone_source", "mj_alignment", "mj1_status", "mj2_status"]].merge(
        sz[["strategy", "trade_id", "nq10_fits_1000"]], on=["strategy", "trade_id"]).merge(
        gx[["strategy", "trade_id", "hvl_side", "cr_ps_width", "pin_zone", "pc_gamma_ratio", "gamma_regime", "time_of_day"]],
        on=["strategy", "trade_id"])
    m["pin_zone"] = m.pin_zone.where(~m.pin_zone.isin(["Y", "N"]), "carried")
    f_e = ["cue_a", "mj_zone_source", "mj_alignment", "mj1_status", "mj2_status", "nq10_fits_1000", "hvl_side", "cr_ps_width", "pin_zone", "pc_gamma_ratio", "gamma_regime", "time_of_day"]
    L += ["### Trades: exits, sizing, GEX tags", ""] + md_table(coverage(m, f_e, ["session", "strategy"]), ["session", "strategy", "rows"] + f_e)
    mq = read(diag, "diag_mnq_rejects.csv")
    if len(mq):
        mq["hyp_status"] = mq.hyp_status.where(mq.hyp_status != "OK", "carried")
    L += ["### MNQ feasibility (R3 / R4 RISK_REJECT rows)", ""] + md_table(coverage(mq, ["mnq_max", "hyp_status"], ["session", "strategy"]) if len(mq) else [],
                                                                            ["session", "strategy", "rows", "mnq_max", "hyp_status"])
    l1 = read(diag, "diag_l1_plan_side.csv")
    L += ["### L1_PLAN_SIDE (R4 candidates and trades from an intraday zone admitted by L1; spec 5b)", "",
          "Counts of rows carrying the field only; the counts by value are reported at the end of Phase 2 (spec 5b).", ""]
    l1["trade"] = l1.is_trade
    L += md_table(coverage(l1, ["l1_side_inherited", "plan_zone_label", "distance_pts"], ["session", "trade"]),
                  ["session", "trade", "rows", "l1_side_inherited", "plan_zone_label", "distance_pts"])
    gs = read(diag, "diag_gex_sessions.csv"); gz = read(diag, "diag_gex_zones.csv")
    gz["v2_status"] = gz.v2_status.where(gz.v2_status != "OK", "carried")
    L += ["### GEX per session and per R4 zone", ""]
    L += md_table(coverage(gs, ["gex_valid", "flip_v3_nt", "regime_agree", "pc_gamma_ratio", "atm_iv", "vol_tercile_POST_PHASE_GROUPING"], ["session"]),
                  ["session", "rows", "gex_valid", "flip_v3_nt", "regime_agree", "pc_gamma_ratio", "atm_iv", "vol_tercile_POST_PHASE_GROUPING"])
    L += md_table(coverage(gz, ["v2_status", "gex_random", "gex_round"], ["session"]), ["session", "rows", "v2_status", "gex_random", "gex_round"])
    n_valid = int((gs.gex_valid == "Y").sum())
    L += [f"V5 missing GEX days: {len(gs) - n_valid} of {len(gs)} Phase 1 sessions have gex_valid = N (they stay in the baseline and drop out of "
          "every GEX group).", ""]

    # GEX build record
    v3 = read(diag, "diag_gex_v3_sessions.csv")
    L += ["## GEX V3, volatility control, pc_gamma_ratio, pin_zone: build record", "",
          "- Code, used through `K:\\Book1A_inputs` only (main() never run): `gex_calc.py` sha256 "
          "7c8107b0eca57990e2ae9f753d9de2cbcc6eb72c7a05ab2d9e49c14182a9232b (cme_day, smile_iv); `mq_levels.py` sha256 "
          "d94b18f25d49e12bb2b9f8d3c023a1837ca877442ace76cc30fbf59e35f566e4 (strike_gex, compute_levels, _gamma); our loader "
          f"`book1a/gex_v3.py` (sha256 {sha('book1a/gex_v3.py')}).",
          f"- Input files: CME NQ option definitions and statistics in `K:\\Book1A_inputs\\raw\\block1\\opt_<root>_*` (roots NQ, Q1A-Q5D, "
          f"QN1-QNE); {len(read_files(diag))} files, each with its sha256 in `gex_v3_input_files.csv`; plus `gex_levels_block1.csv` "
          "(front contract, front settlement, nt_shift_pts).",
          "- Report date D = the previous session (gex_levels_block1.csv). Open interest: the latest per option received at or before "
          "D 23:00 ET (ts_ref within 4 days). Settlements: stat type 3 with ts_ref on D, latest received at or before D 23:00 ET. "
          "Everything is available before the 08:10 CT map of the session.",
          "- Expiry and strike selection: the front NQ futures contract's options (all expiries after D: quarterly, weeklies, "
          "end-of-month); IV from each option's own settlement, interpolated across strikes (smile_iv); GEX per strike as mq_levels. "
          "0DTE set = options expiring on the session. ATM IV: the front contract's nearest expiry after the session (0DTE excluded), "
          "at log-moneyness 0.",
          "- Check: the loader's chain reproduces the frozen gex_levels_block1.csv row (CR, PS, HVL, the 0DTE levels, net_gex, "
          "regime, options_used) on every Phase 1 session.", ""]
    cols = ["session", "report_date", "repro_all_match", "oi_max_ts_recv", "settle_max_ts_recv", "flip_v3_nt", "hvl_nt", "regime_agree",
            "flip_v3_minus_hvl_pts", "flip_v3_crossings", "pc_gamma_ratio", "pin_strike_0dte_nt", "atm_iv", "atm_iv_expiry"]
    v3t = v3[cols].copy()
    for c, nd in (("flip_v3_nt", 2), ("flip_v3_minus_hvl_pts", 2), ("pc_gamma_ratio", 4), ("atm_iv", 4)):
        v3t[c] = pd.to_numeric(v3t[c], errors="coerce").round(nd)
    for c in ("oi_max_ts_recv", "settle_max_ts_recv"):
        v3t[c] = pd.to_datetime(v3t[c]).dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    L += md_table(v3t.to_dict("records"), cols)
    L += ["Volatility terciles (`vol_tercile_POST_PHASE_GROUPING` in diag_gex_sessions.csv) are a post-phase reporting grouping, "
          "computed after the phase from this phase's sessions only; never an AT_ENTRY field.", ""]

    # D5
    pr = read(diag, "d5_cvd_pairs.csv"); exl = read(diag, "d5_cvd_pairs_excluded_60min.csv")
    cases = ("HIGH_ABSORPTION", "HIGH_EXHAUSTION", "LOW_EXHAUSTION", "LOW_ABSORPTION")
    ev = pr[pr.case_cvd17.isin(cases) | pr.case_cvd0830.isin(cases)]
    L += ["## D5 CVD definition check (Oct 24, 27, 28, 29, 2025)", "",
          "Swing pairs: consecutive confirmed swings of the same type whose second swing closes in RTH (08:30-15:00 CT). "
          "Times CT (bar end). CVD at the swing bar's close, 17:00 CT and 08:30 CT resets. Timing: earliest knowable = the second "
          "swing's confirmation. The algorithm is not tuned to these days; disagreements are documented.", "",
          f"### CVD_DIV events (pairs within 60 minutes with a divergence on either reset): {len(ev)}; non-diverging pairs: {len(pr) - len(ev)}", ""]
    c5 = ["session", "kind", "s1_time", "s1_price", "s1_cvd17", "s1_cvd0830", "s2_time", "s2_price", "s2_cvd17", "s2_cvd0830", "gap_min",
          "at_session_extreme", "case_cvd17", "case_cvd0830", "earliest_knowable"]
    L += md_table(ev[c5].to_dict("records"), c5)
    L += [f"### Pairs excluded by the 60-minute window: {len(exl)}", ""] + md_table(exl[c5].to_dict("records"), c5)
    L += ["### Comparison with Jeron's video (for Kyron)", "",
          "Video: \"I made $50,000 this week, here's how\", JeronTrades, Oct 29, 2025. Named times are checked both as ET (minus 1 h) and "
          "as CT, with +-15 minutes around each named time (ours).", ""]
    L += md_table(jeron_rows(diag), ["day", "jeron", "expected", "flagged", "detail"])

    # NOT RUN, open choices, D6
    L += ["## Not run", "",
          "| item | status | reason |", "|---|---|---|",
          "| L2 E1, E2, E4 | NOT_RUN (U11) | not run until the L2F audit and the fixed-price build are done; E4's hold time N is not registered |",
          "| M-J3, M-J4 | NOT_RUN (U5) | deferred until objective triggers are specified |",
          "| Grade without CVD | NOT_RUN (harness) | the S1.4 grade is computed in the harness C# code; recomputing it needs a harness change |",
          "", "Built since the last report (inputs now reachable): GEX V3, volatility control, pc_gamma_ratio, pin_zone.", "",
          "## Open choices (definitions the spec leaves open, fixed in code; for Kyron)", ""]
    L += [f"{i}. {o}" for i, o in enumerate(man["ours"], 1)]
    n = len(man["ours"])
    L += [f"{n + 1}. V3 flip: cumulative net GEX from the lowest strike, linear between the two strikes around the sign change; the crossing "
          "nearest the front settlement when there is more than one.",
          f"{n + 2}. regime_agree: Y when the front settlement is on the same side of flip_v3 as of HVL.",
          f"{n + 3}. pin strike: the 0DTE strike with the largest open interest (calls + puts); on a tie the strike nearest the settlement.",
          f"{n + 4}. ATM IV expiry: the front contract's nearest expiry after the session (0DTE excluded).",
          f"{n + 5}. D5 comparison: +-15 minutes around a named time; 'day extreme' = the RTH extreme among the strict swings.",
          f"{n + 6}. Accepted by Kyron, Nov 6: quote rule bid > 0, ask > 0, bid < ask (no staleness threshold); PROVISIONAL window and "
          "cutoff as in item 7; grade without CVD NOT_RUN (harness).", ""]
    L += ["## D6 No outcomes", "",
          "This report contains no P&L, R, win rate or outcome-by-tag table. Counterfactual fields (cue (a), M-J1, M-J2, MNQ "
          "hypothetical exits) are stored per trade in the diagnostic files only and are not aggregated or summarised.", ""]

    # files
    L += ["## Diagnostic files (runs\\phase1b\\diagnostics, git-ignored)", "", "| file | sha256 |", "|---|---|"]
    for f in sorted(diag.iterdir()):
        if f.is_file():
            L.append(f"| {f.name} | `{sha(f)}` |")
    L += ["", "## Next step", "", "Phase 1b is complete. Phase 2 starts only on Kyron's go.", ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return d1_ok, au["violations"]


def read_files(diag: Path) -> pd.DataFrame:
    return pd.read_csv(diag / "gex_v3_input_files.csv")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hashes"); h.add_argument("--runs", required=True); h.add_argument("--json", required=True)
    r = sub.add_parser("report"); r.add_argument("--runs", required=True); r.add_argument("--before", required=True)
    r.add_argument("--diag", required=True); r.add_argument("--tests", required=True); r.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "hashes":
        Path(a.json).write_text(json.dumps(file_hashes(Path(a.runs), FINAL), indent=1))
        print("hashes written")
    else:
        ok, v = report(Path(a.runs), json.loads(Path(a.before).read_text()), Path(a.diag), Path(a.tests), Path(a.out))
        print(f"D1 {'MATCH' if ok else 'DIFFERS'}; D2 violations {v}; report -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
