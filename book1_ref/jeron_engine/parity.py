"""Phase 0 parity gates for the C# harness (JE 0.1, Oct 25 2026).

gate1(tape, log) -> (ok, details)
    Runs JeronHarness.exe (the real S1.4 strategy) on the Oct 8 tape with plan 2026-10-08-v1, grades A+,B+,B,C,
    S1.4 flags off, ES gate off (no ES ticks), and compares the Qualified signals' 15-bar outcomes (Outcome15 /
    PnL15Ticks) with the NinjaTrader reference: 18 signals, 7 / 8 / 3, +1063 (time-expired trades count 0).
    `log` = an NT tracker/strategy log with the same day, if available: then every signal is compared row by row.
    Without it the reference table below (from NT log JOFT_NQ_DEC26_20261012-164824, v2.4) is used.
"""
import csv, os, subprocess, glob, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = Path(os.environ.get("JERON_HARNESS_EXE", next((p for p in (HERE.parent / "jeron_harness" / "build" / "JeronHarness.exe",
                                                                    HERE.parent / "build" / "JeronHarness.exe") if p.exists()),
                                                          HERE.parent / "jeron_harness" / "build" / "JeronHarness.exe")))
GATE1_EXPECT = {"signals": 18, "wins": 7, "losses": 8, "other": 3, "net_ticks": 1063}
# NT reference, Oct 8 2026 (time CT, direction, 15-bar result in ticks; None = timed out at 15 bars)
GATE1_REF = [("08:41", "Short", -96), ("08:55", "Short", -165), ("09:00", "Short", -109), ("09:19", "Long", 230),
             ("09:34", "Short", 58), ("10:04", "Short", -80), ("10:26", "Short", -51), ("10:40", "Short", -49),
             ("10:50", "Short", -44), ("10:54", "Short", None), ("11:37", "Short", 136), ("11:43", "Short", 330),
             ("11:44", "Short", 148), ("11:49", "Short", 557), ("12:17", "Short", 314), ("12:47", "Short", None),
             ("12:49", "Short", -116), ("13:36", "Short", None)]
# defaults on Kyron's PC (used when phase0_parity.py finds no JeronTapeExporter tape / passes no plan)
PREOPEN = Path(r"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange")
DEFAULT_TAPE_ZIP = PREOPEN / "OCT8_Tick Data.zip"          # NT tick export, Oct 7 00:00 - Oct 8 24:00 CT
DEFAULT_PLAN_V1 = PREOPEN / "PreopenPlan_2026-10-08.txt"     # plan 2026-10-08-v1 (the NT reference run's plan)
PLAN_V1_EXTRA = "review=APPROVED\nend=1\n"   # v1 predates the end=1 / review= lines S1.4 requires; nothing else changed


def run_harness(tape, plan_file, out_dir, settings):
    out_dir = Path(out_dir); plan_dir = out_dir / "plan"
    if out_dir.exists(): shutil.rmtree(out_dir)
    plan_dir.mkdir(parents=True)
    text = Path(plan_file).read_text(encoding="utf-8-sig")
    if "\nend=" not in "\n" + text:
        text = text.rstrip("\n") + "\n" + PLAN_V1_EXTRA
    (plan_dir / Path(plan_file).name).write_text(text, encoding="utf-8")
    cmd = ([] if os.name == "nt" else ["mono"]) + [str(EXE), str(tape), str(plan_dir), str(out_dir)] + [f"{k}={v}" for k, v in settings.items()]
    env = dict(os.environ, TZ="America/Chicago")
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise RuntimeError(p.stdout[-2000:] + p.stderr[-2000:])
    return Path(glob.glob(str(out_dir / "JOFS_*.csv"))[0])


def qualified_outcomes(log_path, day):
    rows = list(csv.DictReader(open(log_path, newline="", encoding="utf-8-sig")))
    out = []
    for x in rows:
        if x.get("RecordType") == "OUTCOME" and x.get("CandidateStatus") == "Qualified":
            t = (x.get("SignalTimeCT") or x.get("EvidenceTimeCT") or "")
            if not t.startswith(day): continue
            o15, p15 = x.get("Outcome15") or x.get("OutcomeType"), x.get("PnL15Ticks") or x.get("PnLTicks")
            pnl = None if o15 == "TIME_EXPIRED" else round(float(p15))
            out.append((t[11:16], x["Direction"], pnl, x))
    return sorted(out, key=lambda r: r[0])


def tally(sig):
    pn = [p for _, _, p, *_ in sig]
    return {"signals": len(sig), "wins": sum(1 for p in pn if p is not None and p > 0),
            "losses": sum(1 for p in pn if p is not None and p < 0), "other": sum(1 for p in pn if p is None or p == 0),
            "net_ticks": sum(p for p in pn if p is not None)}


def resolve_tape(tape, work):
    """A JeronTapeExporter csv(.gz), an NT 'Last' export .txt, or the NT tick-export zip (Last.txt is extracted)."""
    tape = Path(tape) if tape else (DEFAULT_TAPE_ZIP if DEFAULT_TAPE_ZIP.exists() else None)
    if tape is None or not tape.exists():
        return None
    if tape.suffix.lower() == ".zip":
        import zipfile
        with zipfile.ZipFile(tape) as z:
            name = next(n for n in z.namelist() if n.endswith(".Last.txt"))
            dest = Path(work) / "tape"; dest.mkdir(parents=True, exist_ok=True)
            target = dest / Path(name).name
            if not target.exists():
                with z.open(name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        return target
    return tape


def gate1(tape, log=None, plan=None, out_dir=None, extra=None):
    plan = plan or os.environ.get("JERON_PLAN_OCT8") or (str(DEFAULT_PLAN_V1) if DEFAULT_PLAN_V1.exists() else None)
    work = Path(out_dir).parent if out_dir else HERE.parent / "runs"
    tape = resolve_tape(tape, work)
    if not tape or not plan:
        return False, "missing tape or plan 2026-10-08-v1"
    out_dir = out_dir or (work / "harness_gate1")
    settings = {"EvaluateLastDays": 0, "UseEsGate": "false", "AllowedGrades": "A+,B+,B,C", "LogS14Flags": "false"}
    settings.update(extra or {})
    got = qualified_outcomes(run_harness(tape, plan, out_dir, settings), "2026-10-08")
    ref = [(t, d, p) for t, d, p in GATE1_REF]
    if log:
        r = qualified_outcomes(log, "2026-10-08")
        if r: ref = [(t, d, p) for t, d, p, _ in r]
    g = {(t, d): p for t, d, p, _ in got}
    rf = {(t, d): p for t, d, p in ref}
    diffs = [f"{k[0]} {k[1]}: NT {rf.get(k, 'absent')} vs harness {g.get(k, 'absent')}"
             for k in sorted(set(g) | set(rf)) if g.get(k, "absent") != rf.get(k, "absent")]
    t = tally(got)
    ok = t == GATE1_EXPECT and not diffs
    return ok, f"harness {t} vs NT {GATE1_EXPECT}; per-signal differences: {diffs if diffs else 'none'}"


# ---- gate 2: candidates, Databento vs NinjaTrader (Sep 28) ------------------------------------------
GATE2_DAY = "2026-09-28"
GATE2_FROM = "2026-09-21 17:00"          # the NT run's first data (JOFT_NQ_DEC26_20261022-172541: tracker v2.11, InternalTicks)
GATE2_SETTINGS = {"EvaluateLastDays": 0, "UseEsGate": "false"}   # no ES data from Databento here; the ES gate is log-only


def gate2(tape, nt_log, out_dir=None):
    """tape = Databento MBO tape (mbo_tape.py) covering GATE2_FROM .. the day's close; nt_log = the NT log covering the day."""
    from . import candidate_parity
    tape = tape or day_tapes_joined("20260921", "20260929", "joined_gate2_20260921_20260929.csv.gz")
    if not tape or not nt_log:
        return False, "missing Databento tape or NinjaTrader log for Sep 28"
    out_dir = Path(out_dir or HERE.parent / "runs" / "gate2")
    if out_dir.exists(): shutil.rmtree(out_dir)
    (out_dir / "plan").mkdir(parents=True)               # no plan existed for Sep 28 (NT log: PLAN_MISSING)
    cmd = ([] if os.name == "nt" else ["mono"]) + [str(EXE), f"--from={GATE2_FROM}", "--to=2026-09-29 00:00",
           str(tape), str(out_dir / "plan"), str(out_dir)] + [f"{k}={v}" for k, v in GATE2_SETTINGS.items()]
    p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, TZ="America/Chicago"))
    if p.returncode != 0: raise RuntimeError(p.stdout[-2000:] + p.stderr[-2000:])
    hx_log = next(out_dir.glob("JOFS_*.csv"))
    ok, res = candidate_parity.gate2(nt_log, hx_log, GATE2_DAY, out_csv=out_dir / "gate2_candidates_sep28.csv")
    return ok, res


# ---- gate 3: map packets, Databento vs NinjaTrader -------------------------------------------------
GATE3_DAYS = ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"]
GATE3_FROM = "2026-09-23 17:00"          # the NT map run's first tick (packets: data.first_tick_ct)
# the NT run's map settings, read from its packets (as-of 08:20, no Volumetric delta, HTF from tick days, HTF min 10 days)
GATE3_SETTINGS = {"AsOfCT": "08:20", "IncludeDeltaProfile": "false", "HtfFromMinuteBars": "false", "HtfMinDays": 10}


TAPES = HERE.parent / "tapes"   # Databento day tapes (mbo_tape.py): tape_YYYYMMDD.csv.gz (UTC file days)


def day_tapes_joined(first_utc_day, last_utc_day, out_name):
    """Join the day tapes in [first, last] (UTC file dates, YYYYMMDD) into one tape file; returns its path or None."""
    from .mbo_tape import join_tapes
    files = sorted(f for f in TAPES.glob("tape_*.csv.gz") if first_utc_day <= f.name[5:13] <= last_utc_day)
    if not files: return None
    out = TAPES / out_name
    if not out.exists(): join_tapes(out, files)
    return out


RAW = HERE.parent / "raw" / "block1"


NT_TAPE_DIR = Path(r"K:\Documents\NinjaTrader 8\JeronLogs\Tape")


def es_bars_from_exporter(out_csv, tape_dir=None, instrument_prefix="Tape_ES"):
    """ES 1-minute bars built from NinjaTrader's own ES trades (JeronTapeExporter day files
    Tape_ES*_<date>.csv.gz, columns seq,utc_ms,ct,price,size,bid,ask,side). NinjaTrader stamps a bar at its END
    and puts a trade at exactly hh:mm:00.000 in the next bar, so bar end = floor(minute) + 1 minute.
    release_local = the time of the first ES trade after the bar's end: NinjaTrader closes a bar (OnBarUpdate on the
    ES series) only when the next ES trade arrives (checked on Sep 28 - Oct 2: Oct 2's first ES trade after 08:20 came
    at 08:20:01.160, after the map built, so NT's ES block stops at 08:19)."""
    import gzip, datetime as dt
    tape_dir = tape_dir or NT_TAPE_DIR
    files = sorted(Path(tape_dir).glob(instrument_prefix + "*_20*.csv*")) if Path(tape_dir).exists() else []
    files = [f for f in files if not f.name.endswith(".partial")]
    if not files: return None
    bars = {}
    first_after = {}   # bar end -> first trade time at or after it
    for f in files:
        op = gzip.open if f.suffix == ".gz" else open
        with op(f, "rt") as fh:
            next(fh)
            for line in fh:
                p = line.rstrip().split(",")
                t = dt.datetime.strptime(p[2][:19], "%Y-%m-%d %H:%M:%S")
                tf = p[2][:23]
                end = t.replace(second=0) + dt.timedelta(minutes=1)
                start = end - dt.timedelta(minutes=1)
                if start not in first_after: first_after[start] = tf   # first trade of this bar = release of the bars ending at or before it
                px, sz = float(p[3]), int(p[4])
                b = bars.get(end)
                if b is None: bars[end] = [px, px, px, px, sz]
                else:
                    b[1] = max(b[1], px); b[2] = min(b[2], px); b[3] = px; b[4] += sz
    ends = sorted(bars); starts = sorted(first_after)
    import bisect
    with open(out_csv, "w", newline="") as o:
        o.write("time_end_local,open,high,low,close,volume,release_local\n")
        for end in ends:
            b = bars[end]
            i = bisect.bisect_left(starts, end)        # first later bar that has a trade
            rel = first_after[starts[i]] if i < len(starts) else ""
            o.write(f"{end:%Y-%m-%d %H:%M:%S},{b[0]},{b[1]},{b[2]},{b[3]},{b[4]},{rel}\n")
    return out_csv


def nt_tape_joined(out_path, prefix="Tape_NQ", first=None, last=None, tape_dir=None):
    """NinjaTrader's own trades (JeronTapeExporter day files) joined into one harness tape, in file order
    (each day file keeps NT's trade order via seq). first/last = trading dates yyyy-mm-dd (inclusive)."""
    import gzip
    tape_dir = Path(tape_dir or NT_TAPE_DIR)
    files = sorted(f for f in tape_dir.glob(prefix + "*_20*.csv.gz")
                   if (not first or f.name[-17:-7] >= first) and (not last or f.name[-17:-7] <= last))
    if not files: return None
    with gzip.open(out_path, "wt", compresslevel=3) as o:
        o.write("time_local,price,bid,ask,volume,aggressor\n")
        for f in files:
            with gzip.open(f, "rt") as fh:
                next(fh)
                for line in fh:
                    p = line.rstrip().split(",")   # seq,utc_ms,ct,price,size,bid,ask,side
                    o.write(f"{p[2]},{p[3]},{p[5]},{p[6]},{p[4]},{p[7]}\n")
    return out_path


def es_bars_csv(out_csv):
    """ES 1-minute bars for the map harness (bar END time in Central). First choice: NinjaTrader's own ES trades
    from JeronTapeExporter (what NT's map used); else Databento bars from `databento_pull.py submit parity`."""
    nt = es_bars_from_exporter(out_csv)
    if nt: return nt
    files = sorted(RAW.glob("parity_ESZ6_ohlcv_1m_*/*/*.ohlcv-1m.dbn.zst"))
    if not files: return None
    import databento as db
    from zoneinfo import ZoneInfo
    import pandas as pd
    rows = []
    for f in files:
        df = db.DBNStore.from_file(str(f)).to_df(price_type="float", pretty_ts=True, map_symbols=False)
        if len(df): rows.append(df)
    df = pd.concat(rows).sort_index()
    end = (df.index + pd.Timedelta(minutes=1)).tz_convert(ZoneInfo("America/Chicago")).tz_localize(None)
    with open(out_csv, "w", newline="") as o:
        o.write("time_end_local,open,high,low,close,volume\n")
        for t, r in zip(end, df.itertuples()):
            o.write(f"{t:%Y-%m-%d %H:%M:%S},{r.open},{r.high},{r.low},{r.close},{r.volume}\n")
    return out_csv


def gate3(map_packets, tape=None, out_dir=None, days=None, es_csv=None):
    from . import map_parity
    tape = tape or day_tapes_joined("20260923", "20261002", "joined_gate3_20260923_20261002.csv.gz")
    if not tape:
        return False, "missing Databento tape for the map days (" + GATE3_FROM + " onward)"
    out_dir = Path(out_dir or HERE.parent / "runs" / "gate3")
    if out_dir.exists(): shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    days = days or GATE3_DAYS
    es_csv = es_csv or es_bars_csv(out_dir / "es_1m.csv")
    cmd = ([] if os.name == "nt" else ["mono"]) + [str(EXE), "--map", f"--from={GATE3_FROM}", f"--to={days[-1]} 09:00"] \
        + ([f"--es={es_csv}"] if es_csv else []) + [str(tape), str(out_dir)] + [f"{k}={v}" for k, v in GATE3_SETTINGS.items()]
    p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, TZ="America/Chicago"))
    if p.returncode != 0: raise RuntimeError(p.stdout[-2000:] + p.stderr[-2000:])
    ok, summary, rows = map_parity.gate3_compare(map_packets, out_dir, days, out_csv=out_dir / "gate3_map_parity.csv",
                                                 compare_es=bool(es_csv))
    if not es_csv: summary.append("es block NOT compared: no ES 1-minute bars (JeronTapeExporter ES files or databento_pull.py submit parity)")
    return ok, summary


# ---- gate 5: fills -------------------------------------------------------------------------------------
def gate5(nt_log, tape=None, out_dir=None):
    from . import fills
    work = Path(out_dir or HERE.parent / "runs" / "gate5"); work.mkdir(parents=True, exist_ok=True)
    tape = resolve_tape(tape, work)
    return fills.gate5(nt_log, tape, out_csv=work / "gate5_fills_oct8.csv")


if __name__ == "__main__":
    import sys, json
    ok, d = gate1(sys.argv[1], None, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print("PASS" if ok else "FAIL", d)
