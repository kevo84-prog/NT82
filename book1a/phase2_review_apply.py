r"""Phase 2 section 3 application: the what-fails-and-why review on the Phase 2 ledgers (Phase2_registration.md s. 3).

Post-freeze reporting implementation amendment (Nov 7, 2026, Kyron's option 1): added after the book1a-phase2-frozen
tag (e1d37a1), before section 3 was computed. Not part of the frozen implementation. The frozen commit had the section 3
functions but nothing that applied them to the ledgers. This file only reads the Phase 2 run outputs, builds each
trade's inputs, and calls the frozen functions unchanged:
  phase2_review_fields.compute("phase2", ...)                                   fields a), b), c)
  phase2_report.exit_times                                                      entry_session, exit_time_raw / _model, flag
  phase2_report.check_no_overlap                                                one position at a time per strategy
  phase2_report.populations / in_pop / class_table (classify, terciles, tags)   classes and tag counts
  bars.bars_from_rows (Book 1A 1-minute bars), fills.Tape (Book 1 replay tape)  market data, unchanged
It adds no parameter, threshold, cut-off, filter or definition.

  python -m book1a.phase2_review_apply --phase phase2 --a0-run book1a/Phase2/runs/phase2 --r3-run book1a/Phase2/runs/phase2_r3 \
      --r4-run book1a/Phase2/runs/phase2_r4 --diag book1a/Phase2/runs/phase2_diag --out book1a/Phase2/runs/phase2_review

Inputs (opened read-only; sha256 of each recorded before and after the run, and they must be equal):
  ledgers    R1 <a0>/R1_A0_full.csv, R2 <a0>/R2_C1_full.csv, R3 <r3>/R3_M0_ledger.csv, R4 <r4>/R4_M0_ledger.csv
  attempts   <a0>/R1_attempts.csv, <a0>/R2_attempts.csv, <r3>/R3_attempts.csv, <r4>/R4_attempts.csv; retests
             <a0>/R1_retests.csv, <a0>/R2_retests.csv, <r3>/R3_retests.csv (each only if the run wrote it)
  logs       the strategy log the replay read: <a0>/strategy/JOFS_*.csv for R1-R3, <r4>/strategy/JOFS_*.csv for R4
  tapes      the replay tape: <a0>/tape_strategy.csv.gz for R1-R3, <r4>/tape_strategy.csv.gz for R4 (as run_r1_r2,
             run_r3, run_r4 and diag_phase1b use them)
  diag       diag_gex_trades, diag_exit_trades, diag_cvd_trades (per trade), diag_l1_plan_side (per R4 event),
             diag_gex_sessions (per session)

How each compute() input is taken (no new definition):
  trade_id, side, fill (entry_price), stop, target, exit_fill (exit_price), exit_reason   the ledger row
  session        ledger `date` (phase2_report.entry_session)
  fill_time      session + ledger entry_time (the engine stamp: decision bar end + entry_latency_ms)
  decision_time  fill_time - entry_latency_ms (audit_run.decision_ts: "the bar close ... before the fill"). Checked:
                 it must equal the time of this event's attempt row with no block reason, or the `at` of its
                 RETEST_ENTERED retest row; and the diagnostics' own decision_time for the trade
  signal_time    the EvidenceTimeCT of the event's candidate row in the strategy log (RecordType CANDIDATE or SHADOW:
                 arm_replay.attempts' `cand`, the "candidate's signal-bar close"); must be <= decision_time
  exit_time      phase2_report.exit_times(...)["exit_time_raw"] (None when the ledger has no exit time)
  ticks_for      the replay tape's trade times and prices (fills.Tape t, p)
  bars_for       1-minute bars from the same tape (bars.bars_from_rows: bar stamped at its end); vol = buy + sell
                 volume, delta = buy - sell. A trade with unknown-aggressor (U) volume in its confirm bar stops the
                 run (bar volume would then need a new definition).
Tags (section 3): categorical by value via class_table; joined on (strategy, trade_id) (R4 L1_PLAN_SIDE on the R4
event id = trade_id), never on row position. A missing diagnostics row or field is NA. pc_gamma_ratio by tercile of
the 21 sessions' own values (diag_gex_sessions). Not computed here, reported NOT_RUN until Kyron names a source:
market_context and draw_status (no diagnostics file holds them), the cr_ps_width tercile (no file holds the 21
sessions' values; the per-trade value is listed). BREAKOUT_SPEED raw values are listed per trade, not counted
(section 3 gives a count rule only for categorical tags and the numeric GEX tags).

Hard errors (stop and report, never a choice): a duplicate trade_id or diagnostics key; a diagnostics row whose
session, side, qty, decision_time or ledger_sha256 differs from the ledger; a diagnostics trade key not in the ledger;
a trade outside the 21 sessions; no candidate row, conflicting candidate times, or a decision time no attempt / retest
row shows; U volume in a confirm bar; a trade without an exit time (overlap check undefined); an input whose sha256
changed during the run; a review count that differs from the ledger count. Outputs go only to a new --out folder.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from book1a import bars as BARS, phase2_report as RP, phase2_review_fields as F, sessions as S
from book1a.book1_import import jeron_engine  # noqa: F401
from jeron_engine import fills

VERSION = "phase2-review-apply-v1.0"
LABEL = "replay (in-sample), descriptive only"
STRATEGIES = ("R1", "R2", "R3", "R4")
GEX_CAT = ("gamma_regime", "hvl_side", "pin_zone")
EXIT_CAT = ("mj_alignment",)
CVD_CAT = tuple(f"{p}_{k}_{f}_{r}" for p in ("atentry", "prov", "post") for k in ("high", "low")
                for f in ("case", "with") for r in ("cvd17", "cvd0830"))
L1_TAG = "L1_PLAN_SIDE"                                   # diag_l1_plan_side.l1_side_inherited
SESSION_NUMERIC = ("pc_gamma_ratio",)                     # from diag_gex_sessions (one value per session)
BS_FIELDS = ("bs_status", "bs_vol_per_sec_60s", "bs_percentile_session", "bs_n_earlier_bars", "bs_cvd_change_3bar")
NOT_RUN_SOURCE = "NOT_RUN (no diagnostics file holds it; source not registered, Kyron to decide)"
NOT_RUN_TAGS = {"market_context": NOT_RUN_SOURCE, "draw_status": NOT_RUN_SOURCE}
NOT_RUN_NUMERIC = {"cr_ps_width": "NOT_RUN (no file holds the 21 sessions' values; per-trade value listed; Kyron to decide)"}
# diag_phase1b writes decision_time = entry fill - 250 ms per trade and, in diag_l1_plan_side, the candidate's
# EvidenceTimeCT; both must equal this script's decision_time / signal_time, or the run stops.


class MappingError(RuntimeError):
    """An input that cannot be taken from the files without a new interpretation: stop and report."""


# ------------------------------------------------------------------ read-only inputs
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_rows(path: Path, encoding: str = "utf-8") -> List[dict]:
    with open(path, "r", newline="", encoding=encoding) as f:
        return list(csv.DictReader(f))


def read_diag(path: Path) -> List[dict]:
    """A diag_phase1b csv: one '#' header line, then the table."""
    with open(path, "r", newline="", encoding="utf-8") as f:
        first = f.readline()
        if not first.startswith("#"):
            raise MappingError(f"{path.name}: no '#' header line (not a diag_phase1b file)")
        return list(csv.DictReader(f))


def unique(rows: List[dict], key, what: str) -> Dict:
    out = {}
    for r in rows:
        k = key(r)
        if k in out:
            raise MappingError(f"{what}: duplicate key {k}")
        out[k] = r
    return out


def check_unchanged(before: Dict[str, str], after: Dict[str, str]) -> None:
    bad = sorted(k for k in before if after.get(k) != before[k]) + sorted(k for k in after if k not in before)
    if bad:
        raise MappingError(f"inputs changed during the run: {bad}")


def parse_dt(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(str(s).strip())


def fnum(x) -> Optional[float]:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if np.isfinite(v) else None


def input_paths(a0: Path, r3: Path, r4: Path, diag: Path) -> dict:
    def jofs(run: Path) -> Path:
        x = sorted((run / "strategy").glob("JOFS_*.csv"))
        if len(x) != 1:
            raise MappingError(f"{run}: expected one strategy/JOFS_*.csv, found {len(x)}")
        return x[0]
    opt = lambda p: p if p.exists() else None
    log_a0, log_r4 = jofs(a0), jofs(r4)
    return dict(
        ledger=dict(R1=a0 / "R1_A0_full.csv", R2=a0 / "R2_C1_full.csv", R3=r3 / "R3_M0_ledger.csv", R4=r4 / "R4_M0_ledger.csv"),
        attempts=dict(R1=a0 / "R1_attempts.csv", R2=a0 / "R2_attempts.csv", R3=r3 / "R3_attempts.csv", R4=r4 / "R4_attempts.csv"),
        retests=dict(R1=opt(a0 / "R1_retests.csv"), R2=opt(a0 / "R2_retests.csv"), R3=opt(r3 / "R3_retests.csv"), R4=None),
        log=dict(R1=log_a0, R2=log_a0, R3=log_a0, R4=log_r4),
        tape=dict(R1=a0 / "tape_strategy.csv.gz", R2=a0 / "tape_strategy.csv.gz", R3=a0 / "tape_strategy.csv.gz",
                  R4=r4 / "tape_strategy.csv.gz"),
        diag=dict(gex=diag / "diag_gex_trades.csv", exit=diag / "diag_exit_trades.csv", cvd=diag / "diag_cvd_trades.csv",
                  l1=diag / "diag_l1_plan_side.csv", gex_sessions=diag / "diag_gex_sessions.csv"))


def all_files(paths: dict) -> List[Path]:
    out = []
    for group in paths.values():
        for p in group.values():
            if p is not None and p not in out:
                out.append(p)
    return out


# ------------------------------------------------------------------ market data (replay tape)
class TapeData:
    """Trades (fills.Tape, unchanged) and 1-minute bars (bars.bars_from_rows, unchanged) of one replay tape."""

    def __init__(self, path: Path):
        self.tape = fills.Tape(path)
        u_vol: Dict[dt.datetime, int] = defaultdict(int)

        def rows():
            with gzip.open(path, "rt") if str(path).endswith(".gz") else open(path, "r") as f:
                for line in f:
                    if line.startswith("time_local"):
                        continue
                    t, px, vol, ag = BARS._row(line)
                    if ag not in ("B", "S", "A"):
                        u_vol[BARS._bar_end(BARS._parse_ct(t)).replace(tzinfo=None)] += vol
                    yield t, px, vol, ag
        by_day: Dict[dt.date, list] = defaultdict(list)
        for b in BARS.bars_from_rows(rows()):
            by_day[b.close_ct.date()].append(b)
        self.u_vol = dict(u_vol)
        self.bars = {}
        for d, bs in by_day.items():
            self.bars[d] = dict(end=np.array([b.close_ct.replace(tzinfo=None) for b in bs], dtype="datetime64[us]"),
                                o=np.array([b.open for b in bs]), h=np.array([b.high for b in bs]),
                                l=np.array([b.low for b in bs]), c=np.array([b.close for b in bs]),
                                vol=np.array([b.buy_vol + b.sell_vol for b in bs]),
                                delta=np.array([b.buy_vol - b.sell_vol for b in bs]))
        self._empty = dict(end=np.array([], dtype="datetime64[us]"), o=[], h=[], l=[], c=[], vol=[], delta=[])

    def ticks_for(self, d: dt.date):
        return self.tape.t, self.tape.p           # windows are bounded by the trade's own times and session close

    def bars_for(self, d: dt.date):
        return self.bars.get(d, self._empty)


# ------------------------------------------------------------------ per-trade inputs
def candidate_times(log_path: Path) -> Dict[str, dt.datetime]:
    seen: Dict[str, set] = defaultdict(set)
    for r in read_rows(log_path, "utf-8-sig"):
        if r["RecordType"] in ("CANDIDATE", "SHADOW"):
            seen[r["EventId"]].add(r["EvidenceTimeCT"][:23])
    out = {}
    for e, ts in seen.items():
        if len(ts) != 1:
            raise MappingError(f"{log_path.name}: event {e} has conflicting candidate times {sorted(ts)}")
        out[e] = dt.datetime.fromisoformat(next(iter(ts)))
    return out


def decision_records(attempts: List[dict], retests: List[dict]) -> Dict[str, List[tuple]]:
    """event -> [(time, source)] of the records that open a position: an attempt with no block reason, or the `at`
    of a RETEST_ENTERED retest."""
    out: Dict[str, List[tuple]] = defaultdict(list)
    for a in attempts:
        if str(a.get("reasons", "")) == "":
            out[a["event"]].append((parse_dt(a["time"]), "attempt"))
    for r in retests:
        if r.get("outcome") == "RETEST_ENTERED":
            out[r["event"]].append((parse_dt(r["at"]), "retest"))
    return out


def trade_inputs(strategy: str, row: dict, cand_t: Dict[str, dt.datetime], decs: Dict[str, List[tuple]],
                 tape_t: np.ndarray) -> tuple:
    tid = row["trade_id"]
    d = RP.entry_session(row)
    fill_time = dt.datetime.combine(d, RP.parse_time(row["entry_time"]))
    lat = row.get("entry_latency_ms")
    if lat in (None, ""):
        raise MappingError(f"{strategy} {tid}: entry_latency_ms missing")
    decision = fill_time - dt.timedelta(milliseconds=int(lat))
    recs = [x for x in decs.get(tid, []) if x[0] == decision]
    if not recs:
        raise MappingError(f"{strategy} {tid}: decision {decision} not shown by any attempt / retest row {decs.get(tid, [])}")
    if tid not in cand_t:
        raise MappingError(f"{strategy} {tid}: no candidate row in the strategy log")
    signal = cand_t[tid]
    if signal > decision:
        raise MappingError(f"{strategy} {tid}: signal {signal} after the decision {decision}")
    side = {"LONG": 1, "SHORT": -1}.get(str(row["side"]).upper())
    if side is None:
        raise MappingError(f"{strategy} {tid}: side {row['side']!r}")
    x = RP.exit_times(row, tape_t)
    raw = None if x["exit_time_raw"] is None else dt.datetime.fromisoformat(x["exit_time_raw"])
    inp = dict(strategy=strategy, trade_id=tid, session=d, side=side, signal_time=signal, decision_time=decision,
               fill_time=fill_time, fill=float(row["entry_price"]), stop=float(row["stop"]), target=fnum(row["target"]),
               exit_time=raw, exit_fill=fnum(row["exit_price"]), exit_reason=row["exit_reason"])
    return inp, x


def check_diag_row(what: str, dr: dict, led: dict, led_sha: str, decision: dt.datetime) -> None:
    tid = led["trade_id"]
    probs = []
    if dr.get("ledger_sha256") != led_sha:
        probs.append("ledger_sha256")
    if dr.get("session") != led["date"]:
        probs.append("session")
    if "side" in dr and str(dr["side"]).upper() != str(led["side"]).upper():
        probs.append("side")
    if "qty" in dr and str(dr["qty"]) != str(led["qty"]):
        probs.append("qty")
    if dr.get("decision_time") and parse_dt(dr["decision_time"]) != decision:
        probs.append("decision_time")
    if probs:
        raise MappingError(f"{what} {dr.get('strategy')} {tid}: conflicts with the ledger on {probs}")


# ------------------------------------------------------------------ run
def git_state(cwd: Path) -> dict:
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=cwd).strip()
        st = subprocess.check_output(["git", "status", "--porcelain"], text=True, cwd=cwd)
        return dict(commit=head, status_lines=len([x for x in st.splitlines() if x.strip()]))
    except Exception:
        return dict(commit="n/a", status_lines=None)


def run(phase: str, a0: Path, r3: Path, r4: Path, diag: Path, out: Path) -> dict:
    if phase != "phase2":
        raise RuntimeError(f"phase2_review_apply: Phase 2 only, not {phase!r}")
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise MappingError(f"{out} exists and is not empty: outputs go only to a new folder")
    paths = input_paths(Path(a0), Path(r3), Path(r4), Path(diag))
    files = all_files(paths)
    before = {str(p): sha256(p) for p in files}
    sess = S.phase_sessions("phase2")
    sess_set = set(sess)
    pops = RP.populations(sess)

    # ledgers
    ledgers, led_sha = {}, {}
    for s in STRATEGIES:
        rows = read_rows(paths["ledger"][s])
        unique(rows, lambda r: r["trade_id"], f"{s} ledger")
        for r in rows:
            if RP.entry_session(r) not in sess_set:
                raise MappingError(f"{s} {r['trade_id']}: session {r['date']} is not one of the 21 Phase 2 sessions")
        ledgers[s], led_sha[s] = rows, before[str(paths["ledger"][s])]

    # diagnostics, keyed on (strategy, trade_id)
    keys = {(s, r["trade_id"]) for s in STRATEGIES for r in ledgers[s]}
    diag_tr = {}
    for name in ("gex", "exit", "cvd"):
        idx = unique(read_diag(paths["diag"][name]), lambda r: (r["strategy"], r["trade_id"]), f"diag {name}")
        extra = sorted(k for k in idx if k not in keys)
        if extra:
            raise MappingError(f"diag {name}: trade keys not in the ledgers {extra}")
        diag_tr[name] = idx
    l1 = unique([r for r in read_diag(paths["diag"]["l1"]) if r["strategy"] == "R4"], lambda r: r["event"], "diag l1_plan_side")
    gs = unique(read_diag(paths["diag"]["gex_sessions"]), lambda r: r["session"], "diag gex_sessions")
    if sorted(gs) != [d.isoformat() for d in sess]:
        raise MappingError(f"diag gex_sessions: sessions {sorted(gs)} are not the 21 registered sessions")
    session_numeric = {k: {d: fnum(gs[d.isoformat()].get(k)) for d in sess} for k in SESSION_NUMERIC}

    tapes: Dict[Path, TapeData] = {}
    cands: Dict[Path, dict] = {}
    review_rows, classes, overlap, missing = [], {}, {}, {}
    for s in STRATEGIES:
        tp, lp = paths["tape"][s], paths["log"][s]
        if tp not in tapes:
            tapes[tp] = TapeData(tp)
        if lp not in cands:
            cands[lp] = candidate_times(lp)
        td, ct = tapes[tp], cands[lp]
        att = read_rows(paths["attempts"][s])
        ret = read_rows(paths["retests"][s]) if paths["retests"][s] is not None else []
        decs = decision_records(att, ret)
        inputs, xs = [], {}
        for r in ledgers[s]:
            inp, x = trade_inputs(s, r, ct, decs, td.tape.t)
            if td.u_vol.get(inp["decision_time"], 0):
                raise MappingError(f"{s} {r['trade_id']}: unknown-aggressor volume in the confirm bar {inp['decision_time']}")
            inputs.append(inp)
            xs[r["trade_id"]] = x
        if any(x["exit_time_raw"] is None for x in xs.values()):
            raise MappingError(f"{s}: a trade has no exit time; the overlap check is undefined")
        overlap[s] = RP.check_no_overlap(ledgers[s], lambda t: dt.datetime.fromisoformat(xs[t["trade_id"]]["exit_time_raw"]))
        rev = F.compute("phase2", inputs, td.ticks_for, td.bars_for)
        reviews = unique(rev, lambda r: r["trade_id"], f"{s} review")
        if sorted(reviews) != sorted(r["trade_id"] for r in ledgers[s]):
            raise MappingError(f"{s}: review trades differ from the ledger trades")

        # tags per trade (missing row or field -> NA, via class_table)
        tags, miss = {}, Counter()
        by_inp = {i["trade_id"]: i for i in inputs}
        for r in ledgers[s]:
            tid = r["trade_id"]
            dec, sig = by_inp[tid]["decision_time"], by_inp[tid]["signal_time"]
            tg = {}
            for name, cols in (("gex", GEX_CAT + ("cr_ps_width",)), ("exit", EXIT_CAT), ("cvd", CVD_CAT + BS_FIELDS)):
                dr = diag_tr[name].get((s, tid))
                if dr is None:
                    miss[name] += 1
                    continue
                check_diag_row(f"diag {name}", dr, r, led_sha[s], dec)
                for c in cols:
                    tg[c] = dr.get(c, "")
            lr = l1.get(tid) if s == "R4" else None
            if lr is not None:
                if lr.get("is_trade") != "Y" or lr.get("session") != r["date"] or parse_dt(lr["decision_time"]) != sig:
                    raise MappingError(f"diag l1_plan_side R4 {tid}: conflicts with the ledger trade")
                tg[L1_TAG] = lr.get("l1_side_inherited", "")
            elif s == "R4":
                miss["l1"] += 1
            tg.update(NOT_RUN_TAGS)
            tags[tid] = tg
        missing[s] = dict(miss)
        cats = list(GEX_CAT) + list(EXIT_CAT) + [L1_TAG] + list(CVD_CAT) + list(NOT_RUN_TAGS)
        classes[s] = {p: RP.class_table(s, RP.in_pop(ledgers[s], ds), reviews, tags, session_numeric, cats)
                      for p, ds in pops.items()}
        all_tab = classes[s]["ALL"]
        if sum(all_tab["counts"].values()) != len(ledgers[s]) or len(all_tab["trades"]) != len(ledgers[s]):
            raise MappingError(f"{s}: class counts differ from the ledger count")
        by_cls = {t["trade_id"]: t for t in all_tab["trades"]}
        for inp in inputs:
            tid = inp["trade_id"]
            row = dict(strategy=s, trade_id=tid, entry_session=xs[tid]["entry_session"], cls=by_cls[tid]["cls"],
                       signal_time=inp["signal_time"], decision_time=inp["decision_time"], fill_time=inp["fill_time"])
            row.update({k: v for k, v in xs[tid].items() if k != "entry_session"})
            row.update({k: v for k, v in reviews[tid].items() if k not in ("strategy", "trade_id", "session")})
            for k in cats:
                row[k] = by_cls[tid][k]
            for k in SESSION_NUMERIC:
                row[k + "_session_value"] = session_numeric[k].get(inp["session"])
                row[k + "_tercile"] = by_cls[tid][k + "_tercile"]
            row["cr_ps_width_trade_value"] = tags[tid].get("cr_ps_width", "") or "NA"
            row["cr_ps_width_tercile"] = NOT_RUN_NUMERIC["cr_ps_width"]
            for k in BS_FIELDS:
                row[k] = tags[tid].get(k, "") or "NA"
            row["label"] = LABEL
            review_rows.append(row)

    counts = Counter(r["strategy"] for r in review_rows)
    for s in STRATEGIES:
        if counts.get(s, 0) != len(ledgers[s]):
            raise MappingError(f"{s}: {counts.get(s, 0)} review rows for {len(ledgers[s])} ledger trades")
    after = {str(p): sha256(p) for p in files}
    check_unchanged(before, after)

    out.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in review_rows for k in r))
    with open(out / "phase2_review.csv", "x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in review_rows:
            w.writerow({k: ("NA" if r.get(k) is None else r.get(k)) for k in cols})
    res = dict(version=VERSION, label=LABEL, review_fields_version=F.VERSION, report_version=RP.VERSION,
               classes=classes, overlap=overlap, overlap_ok=all(not v for v in overlap.values()))
    with open(out / "phase2_review_classes.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(res, indent=1, default=str))
    man = dict(version=VERSION, amendment="post-freeze reporting implementation amendment (Nov 7, 2026); not part of the "
               "frozen implementation; tag book1a-phase2-frozen stays on e1d37a1",
               script_sha256=sha256(Path(__file__)), git=git_state(Path(__file__).resolve().parents[1]),
               generated=dt.datetime.now().isoformat(timespec="seconds"), sessions=[d.isoformat() for d in sess],
               trades_per_strategy={s: len(ledgers[s]) for s in STRATEGIES}, review_rows=len(review_rows),
               missing_diag_rows=missing, not_run=dict(**NOT_RUN_TAGS, **{k + "_tercile": v for k, v in NOT_RUN_NUMERIC.items()},
                                                       BREAKOUT_SPEED="raw values listed per trade; not counted"),
               inputs_sha256_before=before, inputs_sha256_after=after, inputs_unchanged=True,
               outputs=["phase2_review.csv", "phase2_review_classes.json", "phase2_review_manifest.json"])
    with open(out / "phase2_review_manifest.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(man, indent=1, default=str))
    return dict(rows=review_rows, classes=classes, overlap=overlap, manifest=man)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Phase 2 section 3 review on the Phase 2 ledgers (Phase 2 only)")
    ap.add_argument("--phase", required=True)
    ap.add_argument("--a0-run", required=True)
    ap.add_argument("--r3-run", required=True)
    ap.add_argument("--r4-run", required=True)
    ap.add_argument("--diag", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    r = run(a.phase, Path(a.a0_run), Path(a.r3_run), Path(a.r4_run), Path(a.diag), Path(a.out))
    print(f"review rows {len(r['rows'])} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
