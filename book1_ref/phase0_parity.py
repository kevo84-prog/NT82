"""
phase0_parity.py  -  Jeron backtest, Phase 0 (design v3.4)
=================================================================================
Runs on Kyron's PC (the data is on K:). Nothing is uploaded.

    pip install databento pandas numpy
    python "G:\\My Drive\\NT DATA\\research logs\\Jeron\\Back TEST Chat_Claude\\backtest_scripts\\phase0_parity.py"

Options:
    --workers 4        decode MBO files in parallel (default 4)
    --max-days N       only check the first N Block 1 files (quick test run)
    --skip-integrity   skip gate 6 (the slow part); uses whatever is cached
    --only GATE        run one part: paths, integrity, calendar, roll, nt, data_parity, engine

What it checks (design v3.4, Phase 0):
    P   Paths: every data location below exists and has the expected file count.
    G6  Data integrity of every Block 1 MBO file: records, trades, contracts present,
        first/last timestamps, 08:30-15:00 CT gaps > 60 s on the front contract, decode errors.
        Results are cached per file, so a stopped run resumes where it left off.
    HOL Holidays / half days confirmed from the trade timestamps (MLK Day, Presidents' Day,
        Nov 28, Dec 24, ...) against the economic calendar files.
    ROLL Front contract per day by volume, the day it switches, and the back-adjust offset
        (price gap between the two contracts) on each roll.
    NT  NinjaTrader settings: contract merge policy (Config.xml). Commission is reported as
        "enter manually" if it cannot be found.
    G2  Databento vs NinjaTrader data (September 2026): 1-minute volume, buy/sell volume and
        delta from MBO (exchange aggressor) vs the NT Volumetric exports.
    G1/G3/G5  Need the Python port of strategy S1.4 and map v2.3 (package `jeron_engine`).
        The script checks that every input file for these gates exists. If `jeron_engine`
        can be imported it runs them; otherwise they are reported as NOT RUN (engine not built).

Output: K:\\Databento_BackTesting\\backtest\\phase0\\  (report + CSV tables)
        and a copy of the report in the Drive folder "Phase 0 - Parity" if it is reachable.
=================================================================================
"""

import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import sys
import traceback
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

# =================================================================================
# 1. LOCATIONS OF ALL TEST DATA  (checked on Kyron's PC, Oct 24 2026)
# =================================================================================
DATA_ROOT = Path(r"K:\Databento_BackTesting")
BLOCK1 = DATA_ROOT / "raw" / "block1"

PATHS = {
    # --- Block 1 (Oct 21, 2025 - Apr 21, 2026), Databento GLBX.MDP3 ---------------------
    "nq_mbo_block1":     BLOCK1 / "nq_mbo_20251021_20260421" / "GLBX-20261022-JHKARNQBGK",  # 157 daily .mbo.dbn.zst
    "nq_trades_lookback": BLOCK1 / "nq_trades_lookback" / "GLBX-20261022-7NX4S37BYT",       # Jul 20 - Oct 20, 2025
    "nq_ohlcv_1m":       BLOCK1 / "nq_ohlcv_1m" / "GLBX-20261022-H5DJNDVYNM",
    "nq_ohlcv_1d":       BLOCK1 / "nq_ohlcv_1d" / "GLBX-20261022-CLBXTRXNFA",
    "nq_fut_definition": BLOCK1 / "nq_fut_definition" / "GLBX-20261022-NW9534RLT5",
    "nq_fut_statistics": BLOCK1 / "nq_fut_statistics" / "GLBX-20261022-VFXEB76TGV",
    "es_ohlcv_1m":       BLOCK1 / "es_ohlcv_1m" / "GLBX-20261022-VDXRDCH7KU",
    "es_ohlcv_1d":       BLOCK1 / "es_ohlcv_1d" / "GLBX-20261022-WPJWNKGGKM",
    "es_fut_definition": BLOCK1 / "es_fut_definition" / "GLBX-20261022-Q4S5LDXQVH",
    "es_fut_statistics": BLOCK1 / "es_fut_statistics" / "GLBX-20261022-VPNMW88TCM",
    "cl_ohlcv_1m":       BLOCK1 / "cl_ohlcv_1m" / "GLBX-20261022-SD98KBVXF6",
    "cl_ohlcv_1d":       BLOCK1 / "cl_ohlcv_1d" / "GLBX-20261022-TKRDH7SFYU",
    "zn_ohlcv_1m":       BLOCK1 / "zn_ohlcv_1m",                                            # job folder found by glob
    "zn_ohlcv_1d":       BLOCK1 / "zn_ohlcv_1d",
    "opt_nq_definition": BLOCK1 / "opt_nq_definition" / "GLBX-20261022-68DRMUL3YR",
    "opt_nq_statistics": BLOCK1 / "opt_nq_statistics" / "GLBX-20261022-KMFXGFAVN6",
    # weekly / serial option folders: BLOCK1 / "opt_q1a_definition" ... "opt_qne_statistics" (found by glob)
    # roll-day MBO for the contract NT was on (nq_roll_NQH6_mbo_*, nq_roll_NQM6_mbo_*): found by glob in run_roll()
    "roll_NQZ5_trades":  BLOCK1 / "nq_roll_NQZ5_trades_20250914_20250916",
    "roll_NQZ5_1m":      BLOCK1 / "roll_NQZ5_ohlcv_1m_20250914_20250916",
    "roll_ESZ5_1m":      BLOCK1 / "roll_ESZ5_ohlcv_1m_20250914_20250916",
    # --- Owned MBO, Sep-Oct 2026 (parity days and the Phase 5 consistency check) ----------
    "nq_mbo_sep2026":    DATA_ROOT / "NQ_MBO_2026-09" / "GLBX-20260928-6GPK57A3YJ",         # Sep 1 - Sep 27, 2026
    "nq_mbo_oct2026":    DATA_ROOT / "NQ_MBO_2026-10" / "GLBX-20261005-KWSCSS7Q6S",         # Sep 28 - Oct 4, 2026
    # --- NinjaTrader exports on K: ---------------------------------------------------------
    "nt_volumetric":     DATA_ROOT / "VolumetricExports",                                   # NQ DEC26 Volumetric bars (Jun-Sep 2026)
    # --- Calendars ---------------------------------------------------------------------------
    "econ_cal_macro":    DATA_ROOT / "macro" / "econ_calendar_block1.csv",
    "econ_cal_drive":    Path(r"G:\My Drive\NT DATA\research logs\Jeron\Back TEST Chat_Claude\econ_calendar_2025-10_2026-04.csv"),
    "econ_cal_sep2026":  DATA_ROOT / "logs" / "econ_calendar.csv",
    # --- GEX replica ----------------------------------------------------------------------------
    "mq_levels_py":      DATA_ROOT / "mq_levels.py",
    "gex_results":       DATA_ROOT / "gex_results" / "final",
    # --- Live NinjaTrader output on Google Drive (logs, plans, map packets) -----------------
    "nt_logs":           Path(r"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs"),
    "nt_plans":          Path(r"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\Pre-open Plan"),
    "nt_map_packets":    Path(r"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\zones"),
    # --- NinjaTrader install -----------------------------------------------------------------
    "nt_root":           Path(r"K:\Documents\NinjaTrader 8"),
    "nt_strategy_cs":    Path(r"K:\Documents\NinjaTrader 8\bin\Custom\Strategies\JeronOrderFlowStrategy.cs"),
    "nt_map_cs":         Path(r"K:\Documents\NinjaTrader 8\bin\Custom\Indicators\JeronPreopenMap.cs"),
}

# Where the Oct 8 tape (JeronTapeExporter: Tape_<instrument>_2026-10-08.csv.gz) may be. First match wins.
TAPE_SEARCH = [PATHS["nt_logs"], PATHS["nt_root"], DATA_ROOT, Path(r"G:\My Drive\NT DATA")]

OUT = DATA_ROOT / "backtest" / "phase0"
DRIVE_PHASE0 = Path(r"G:\My Drive\NT DATA\research logs\Jeron\Back TEST Chat_Claude\Phase 0 - Parity")

# =================================================================================
# 2. FIXED FACTS FROM THE DESIGN (v3.4)
# =================================================================================
CT = ZoneInfo("America/Chicago")
TICK = 0.25
RTH_START, RTH_END = dt.time(8, 30), dt.time(15, 0)
GAP_SECONDS = 60                       # gate 6: a gap over 60 s inside 08:30-15:00 CT is flagged
EXPECTED_MBO_FILES = 157
EXPECTED_CLOSED = {"2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03"}  # no cash session
EXPECTED_HALF = {"2025-11-28": dt.time(12, 0), "2025-12-24": dt.time(12, 0)}                         # cash ends 12:00 CT
# Roll dates = NinjaTrader's own rollover dates (from its database, Oct 24 2026), not the CME
# 8-days-before-expiry rule, so the engine trades the same contract NT did (parity first).
CME_ROLLS = {"2025-12-15": ("NQZ5", "NQH6"), "2026-03-16": ("NQH6", "NQM6")}
# Databento-flagged degraded trading dates: reported in G6, kept out of training.
DEGRADED = {"2025-11-28", "2026-03-16", "2026-04-10"}
CHUNK = 2_000_000

# Gate 1 reference (NT log, Oct 8 2026, grades A+,B+,B,C, S1.4 flags off)
GATE1_EXPECT = {"signals": 18, "wins": 7, "losses": 8, "other": 3, "net_ticks": 1063}

# =================================================================================
lines = []
def out(s=""):
    print(s, flush=True)
    lines.append(str(s))

def hdr(s):
    out(""); out("=" * 90); out(s); out("=" * 90)

verdicts = {}   # gate -> (status, note)

def verdict(gate, status, note=""):
    verdicts[gate] = (status, note)
    out(f"  >> {gate}: {status}  {note}")

def find_dir(p):
    """Return p, or the single job folder inside p (GLBX-...) if p is the dataset folder."""
    if p.is_dir():
        subs = [d for d in p.iterdir() if d.is_dir() and d.name.startswith("GLBX-")]
        if subs and not any(p.glob("*.dbn.zst")):
            return sorted(subs)[-1]
    return p

def dbn_files(p):
    return sorted(find_dir(p).glob("*.dbn.zst"))

def file_date(f):
    m = re.search(r"(\d{8})", f.name)
    return dt.datetime.strptime(m.group(1), "%Y%m%d").date() if m else None

# =================================================================================
# P. PATHS
# =================================================================================
def check_paths():
    hdr("P  Paths (every data location used by the backtest)")
    ok = True
    for k, p in PATHS.items():
        q = find_dir(p)
        if not q.exists():
            out(f"  MISSING  {k:<20} {p}")
            if k not in ("econ_cal_drive", "zn_ohlcv_1m", "zn_ohlcv_1d"):
                ok = False
            continue
        if q.is_dir():
            n = len(list(q.glob("*.dbn.zst"))) or len(list(q.iterdir()))
            out(f"  ok       {k:<20} {q}  ({n} files)")
        else:
            out(f"  ok       {k:<20} {q}  ({q.stat().st_size:,} bytes)")
    opt = sorted(d.name for d in BLOCK1.glob("opt_q*_*"))
    out(f"  option folders found: {len(opt)}  ({', '.join(opt[:4])} ... {', '.join(opt[-2:])})")
    n = len(dbn_files(PATHS["nq_mbo_block1"]))
    out(f"  Block 1 MBO files: {n} (expected {EXPECTED_MBO_FILES})")
    if n != EXPECTED_MBO_FILES:
        ok = False
    verdict("P paths", "PASS" if ok else "FAIL", "" if ok else "fix the missing paths above (edit PATHS at the top)")

# =================================================================================
# G6. DATA INTEGRITY (one worker per file, cached)
# =================================================================================
def _iter_chunks(store):
    try:
        for a in store.to_ndarray(count=CHUNK):
            yield a
    except TypeError:
        a = store.to_ndarray()
        for i in range(0, len(a), CHUNK):
            yield a[i:i + CHUNK]

def integrity_one(path_str, cache_dir_str):
    import databento as db
    path = Path(path_str)
    cache = Path(cache_dir_str) / (path.name + ".json")
    if cache.exists():
        return json.loads(cache.read_text())
    day = file_date(path)
    res = {"file": path.name, "date": str(day), "records": 0, "trades": 0, "error": "",
           "first_utc": None, "last_utc": None, "by_id": {}}
    rth_lo = dt.datetime.combine(day, RTH_START, CT).timestamp() * 1e9
    rth_hi = dt.datetime.combine(day, RTH_END, CT).timestamp() * 1e9
    rth_ts = defaultdict(list)            # instrument_id -> RTH trade timestamps (ns)
    last_px = {}
    try:
        store = db.DBNStore.from_file(path)
        for a in _iter_chunks(store):
            if len(a) == 0:
                continue
            res["records"] += int(len(a))
            ts = a["ts_event"].astype("int64")
            res["first_utc"] = int(ts[0]) if res["first_utc"] is None else min(res["first_utc"], int(ts[0]))
            res["last_utc"] = int(ts[-1]) if res["last_utc"] is None else max(res["last_utc"], int(ts[-1]))
            act = a["action"]
            act = act if act.dtype.kind in "US" else act.astype("S1")
            mask = (act == b"T") | (act == "T")
            if not mask.any():
                continue
            t = a[mask]
            res["trades"] += int(len(t))
            tts = t["ts_event"].astype("int64")
            ids = t["instrument_id"].astype("int64")
            sz = t["size"].astype("int64")
            px = t["price"].astype("int64") / 1e9
            side = t["side"]
            side = side if side.dtype.kind in "US" else side.astype("S1")
            for iid in np.unique(ids):
                m = ids == iid
                d = res["by_id"].setdefault(str(int(iid)), {"trades": 0, "volume": 0, "buy": 0, "sell": 0,
                                                             "rth_volume": 0, "rth_first_ct": None, "rth_last_ct": None})
                d["trades"] += int(m.sum()); d["volume"] += int(sz[m].sum())
                s = side[m]
                d["buy"] += int(sz[m][(s == b"B") | (s == "B")].sum())      # Databento: side B = buy aggressor
                d["sell"] += int(sz[m][(s == b"A") | (s == "A")].sum())     #            side A = sell aggressor
                r = m & (tts >= rth_lo) & (tts < rth_hi)
                if r.any():
                    d["rth_volume"] += int(sz[r].sum())
                    rth_ts[str(int(iid))].append(tts[r])
                    last_px[str(int(iid))] = float(px[r][-1])
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
    for iid, chunks in rth_ts.items():
        t = np.sort(np.concatenate(chunks))
        d = res["by_id"][iid]
        d["rth_first_ct"] = dt.datetime.fromtimestamp(t[0] / 1e9, CT).strftime("%H:%M:%S")
        d["rth_last_ct"] = dt.datetime.fromtimestamp(t[-1] / 1e9, CT).strftime("%H:%M:%S")
        d["rth_last_price"] = last_px.get(iid)
        gaps = np.diff(t) / 1e9
        big = np.where(gaps > GAP_SECONDS)[0]
        d["rth_gaps_over_60s"] = int(len(big))
        d["rth_max_gap_s"] = float(gaps.max()) if len(gaps) else 0.0
        d["rth_gap_list"] = [dt.datetime.fromtimestamp(t[i] / 1e9, CT).strftime("%H:%M:%S") + f" ({gaps[i]:.0f}s)"
                             for i in big[:10]]
    cache.write_text(json.dumps(res))
    return res

def load_symbols():
    """instrument_id -> raw_symbol from the NQ futures definition files (+ the MBO metadata)."""
    sym = {}
    try:
        import databento as db
        files = dbn_files(PATHS["nq_fut_definition"])
        for f in files[::10] + files[-1:]:
            df = db.DBNStore.from_file(f).to_df(map_symbols=False)
            if len(df) and "raw_symbol" in df:
                for iid, rs in zip(df["instrument_id"], df["raw_symbol"]):
                    sym[int(iid)] = str(rs)
    except Exception as e:
        out(f"  (could not read definitions: {e})")
    return sym

def run_integrity(args):
    hdr("G6  Data integrity of every Block 1 MBO file")
    cache_dir = OUT / "integrity_cache"; cache_dir.mkdir(parents=True, exist_ok=True)
    files = dbn_files(PATHS["nq_mbo_block1"])
    if args.max_days:
        files = files[:args.max_days]
    results = []
    if args.skip_integrity:
        for f in files:
            c = cache_dir / (f.name + ".json")
            if c.exists():
                results.append(json.loads(c.read_text()))
        out(f"  using cache only: {len(results)} of {len(files)} files")
    else:
        out(f"  decoding {len(files)} files with {args.workers} workers (cached, resumable) ...")
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(integrity_one, str(f), str(cache_dir)): f for f in files}
            for i, fu in enumerate(as_completed(futs), 1):
                f = futs[fu]
                try:
                    r = fu.result()
                except Exception as e:
                    r = {"file": f.name, "date": str(file_date(f)), "error": repr(e), "by_id": {}, "records": 0, "trades": 0}
                results.append(r)
                if i % 10 == 0 or i == len(files):
                    out(f"    {i}/{len(files)} done")
    results.sort(key=lambda r: r["date"])
    sym = load_symbols()
    rows = []
    for r in results:
        ids = r.get("by_id", {})
        front = max(ids, key=lambda k: ids[k].get("rth_volume", 0) or ids[k]["volume"]) if ids else None
        d = ids.get(front, {})
        rows.append({
            "date": r["date"], "file": r["file"], "error": r.get("error", ""),
            "records": r.get("records", 0), "trades": r.get("trades", 0),
            "contracts": ";".join(f"{sym.get(int(k), k)}:{v['volume']}" for k, v in sorted(ids.items(), key=lambda x: -x[1]["volume"])),
            "front_id": front, "front_symbol": sym.get(int(front), "") if front else "",
            "front_rth_volume": d.get("rth_volume", 0), "front_buy": d.get("buy", 0), "front_sell": d.get("sell", 0),
            "rth_first_ct": d.get("rth_first_ct"), "rth_last_ct": d.get("rth_last_ct"),
            "rth_last_price": d.get("rth_last_price"),
            "rth_gaps_over_60s": d.get("rth_gaps_over_60s", 0), "rth_max_gap_s": round(d.get("rth_max_gap_s", 0), 1),
            "rth_gap_list": " | ".join(d.get("rth_gap_list", [])),
            "first_utc": pd.to_datetime(r["first_utc"], utc=True) if r.get("first_utc") else None,
            "last_utc": pd.to_datetime(r["last_utc"], utc=True) if r.get("last_utc") else None,
            "_by_id": ids,
        })
    df = pd.DataFrame(rows)
    df.drop(columns=["_by_id"]).to_csv(OUT / "G6_data_integrity.csv", index=False)
    errs = df[df["error"].astype(str).str.len() > 0]
    weekdays = df[pd.to_datetime(df["date"]).dt.weekday < 5]
    sessions = weekdays[~weekdays["date"].isin(EXPECTED_CLOSED)]
    gappy = sessions[(sessions["rth_gaps_over_60s"] > 0) & ~sessions["date"].isin(DEGRADED)]
    for d in sorted(DEGRADED):
        r = df[df["date"] == d]
        if len(r):
            r = r.iloc[0]
            out(f"    DEGRADED (Databento) {d}: {r['rth_gaps_over_60s']} gaps, max {r['rth_max_gap_s']}s  -> logged, excluded from training")
    out(f"  files checked: {len(df)}   decode errors: {len(errs)}   sessions with RTH gaps > {GAP_SECONDS}s: {len(gappy)}")
    for _, r in errs.iterrows():
        out(f"    ERROR {r['date']}: {r['error']}")
    for _, r in gappy.head(25).iterrows():
        out(f"    GAP   {r['date']} {r['front_symbol']}: {r['rth_gaps_over_60s']} gaps, max {r['rth_max_gap_s']}s  {r['rth_gap_list']}")
    out(f"  table: {OUT / 'G6_data_integrity.csv'}")
    status = "PASS" if len(errs) == 0 and len(gappy) == 0 else ("CHECK" if len(errs) == 0 else "FAIL")
    verdict("G6 data integrity", status,
            "" if status == "PASS" else "review the gap/error list; a real outage day is logged, not fixed")
    return df

# =================================================================================
# HOL. HOLIDAYS / HALF DAYS FROM THE TIMESTAMPS + CALENDAR FILES
# =================================================================================
def run_calendar(df):
    hdr("HOL  Holidays and half days (from trade timestamps) vs the calendar files")
    cals = {}
    for k in ("econ_cal_drive", "econ_cal_macro", "econ_cal_sep2026"):
        p = PATHS[k]
        if p.exists():
            try:
                cals[k] = pd.read_csv(p)
                out(f"  {k}: {len(cals[k])} rows, {cals[k]['date'].min()} .. {cals[k]['date'].max()}")
            except Exception as e:
                out(f"  {k}: could not read ({e})")
        else:
            out(f"  {k}: not found at {p}")
    ok = True
    if df is not None and len(df):
        for day in sorted(EXPECTED_CLOSED | set(EXPECTED_HALF)):
            r = df[df["date"] == day]
            if r.empty:
                out(f"  {day}: no MBO file (expected for a full closure)"); continue
            r = r.iloc[0]
            last = r["rth_last_ct"]; vol = r["front_rth_volume"]
            if day in EXPECTED_CLOSED:
                # a holiday has no cash session; CME equity futures may still trade until 12:00 CT
                cash = last is not None and last > "12:15:00"
                out(f"  {day} expected NO cash session: RTH volume {vol:,}, last RTH trade {last}  -> {'CHECK (traded after 12:15)' if cash else 'confirmed'}")
                ok &= not cash
            else:
                good = last is not None and "11:55:00" <= last <= "12:16:00"
                out(f"  {day} expected HALF DAY (cash ends 12:00 CT): last RTH trade {last}  -> {'confirmed' if good else 'CHECK'}")
                ok &= good
        # any other weekday with a short or empty cash session?
        for _, r in df.iterrows():
            d = r["date"]
            if pd.Timestamp(d).weekday() >= 5 or d in EXPECTED_CLOSED or d in EXPECTED_HALF:
                continue
            if r["rth_last_ct"] is None or r["rth_last_ct"] < "14:55:00" or (r["rth_first_ct"] or "99") > "08:31:00":
                out(f"  UNEXPECTED short session {d}: first {r['rth_first_ct']} last {r['rth_last_ct']}")
                ok = False
    cal = cals.get("econ_cal_drive")
    if cal is not None:
        cat = cal.get("category", pd.Series(dtype=str)).astype(str)
        st = cal.get("status", pd.Series(dtype=str)).astype(str)
        out("  calendar file (Drive) market-calendar rows:")
        for _, r in cal[cat == "MARKET_CALENDAR"].iterrows():
            out(f"    {r['date']}  {r['event']}  {r.get('status', '')}  {r.get('action', '')}")
        out(f"  tier-1 releases: {(cat == 'DATA_TIER1').sum()}  (cancelled: {((cat == 'DATA_TIER1') & (st == 'CANCELED')).sum()}),"
            f" FOMC: {(cat == 'FOMC').sum()}, earnings: {(cat == 'EARNINGS').sum()}")
        out("  SPOT-CHECK BY HAND before Phase 1 (5 rows against the source link in the file):")
        sample = cal[cat.isin(["DATA_TIER1", "FOMC"])].sample(n=min(5, (cat.isin(["DATA_TIER1", "FOMC"])).sum()), random_state=1)
        for _, r in sample.iterrows():
            out(f"    {r['date']} {r.get('time_ct', '')} {r['event']}  -> {r.get('source', '')}")
    verdict("HOL holidays/half days", "PASS" if ok else "CHECK")

# =================================================================================
# ROLL. FRONT CONTRACT PER DAY AND BACK-ADJUST OFFSETS
# =================================================================================
def run_roll(df):
    hdr("ROLL  Contract per day vs the CME roll rule, and roll offsets")
    out("  Note: the Block 1 MBO was pulled as NQ.v.0 (Databento continuous, rolls by volume two days late),")
    out("  so each daily file holds ONE contract. The nq_roll_* folders hold the NT contract on those days.")
    if df is None or not len(df):
        verdict("ROLL", "NOT RUN", "needs the G6 table"); return
    sym = load_symbols()
    sess = df[df["front_rth_volume"] > 0].copy()
    sess["prev"] = sess["front_symbol"].shift()
    for _, r in sess[(sess["front_symbol"] != sess["prev"]) & sess["prev"].notna()].iterrows():
        out(f"  Databento switch on {r['date']}: {r['prev']} -> {r['front_symbol']}")
    # second-contract prices from the roll folders (same worker, cached)
    extra = {}
    cache_dir = OUT / "integrity_cache"; cache_dir.mkdir(parents=True, exist_ok=True)
    roll_dirs = sorted(d for d in BLOCK1.glob("nq_roll_*_mbo_*") if d.is_dir())
    out(f"  roll-day MBO folders: {', '.join(d.name for d in roll_dirs) or 'NONE (run databento_pull.py submit roll / download)'}")
    for rd in roll_dirs:
        for f in dbn_files(rd):
            r = integrity_one(str(f), str(cache_dir))
            for iid, v in r["by_id"].items():
                extra.setdefault(r["date"], {})[sym.get(int(iid), iid)] = v.get("rth_last_price")
    rows = []
    for day, (old, new) in CME_ROLLS.items():
        after = sess[sess["date"] >= day]
        db_switch = after[after["front_symbol"] == new]["date"].min() if len(after) else None
        mism = after[(after["front_symbol"] == old)]["date"].tolist()
        out(f"  CME roll {day} ({old} -> {new}): Databento switches on {db_switch}; "
            f"days where the file still holds {old}: {', '.join(mism) or 'none'}")
        offs = []
        for d in sorted(set(mism + ([db_switch] if db_switch else []))):
            px = {}
            r = df[df["date"] == d]
            if len(r):
                for iid, v in r.iloc[0]["_by_id"].items():
                    px[sym.get(int(iid), iid)] = v.get("rth_last_price")
            px.update(extra.get(d, {}))
            if px.get(old) and px.get(new):
                offs.append((d, px[new] - px[old]))
                out(f"    {d}: {old} {px[old]}  {new} {px[new]}  offset {px[new] - px[old]:+.2f} points")
        rows.append({"cme_roll": day, "old": old, "new": new, "databento_switch": db_switch,
                     "days_on_old_contract": ";".join(mism), "offset_points": offs[-1][1] if offs else None,
                     "offset_day": offs[-1][0] if offs else None})
        if mism and not offs:
            out(f"    NO {new} data on disk for {', '.join(mism)}: either buy {new} MBO for those days, or keep "
                f"Databento's volume roll for them (decision for Kyron; record it in the design).")
    pd.DataFrame(rows).to_csv(OUT / "ROLL_contracts.csv", index=False)
    gaps = [r for r in rows if r["days_on_old_contract"] and r["offset_points"] is None]
    verdict("ROLL", "PASS" if not gaps else "DECISION",
            "" if not gaps else "missing second-contract data around: " + ", ".join(r["cme_roll"] for r in gaps))

# =================================================================================
# NT. NINJATRADER SETTINGS
# =================================================================================
def run_nt():
    hdr("NT  NinjaTrader settings (merge policy, commission)")
    cfg = PATHS["nt_root"] / "Config.xml"
    merge = None
    if cfg.exists():
        txt = cfg.read_text(errors="ignore")
        m = re.search(r"<MergePolicy>([^<]+)</MergePolicy>", txt) or re.search(r"MergePolicy[^>]*>([^<]+)<", txt)
        merge = m.group(1) if m else None
    out(f"  Config.xml: {cfg} ({'found' if cfg.exists() else 'NOT FOUND'})")
    out(f"  contract merge policy: {merge or 'not found in Config.xml -> check Tools > Options > Market data > Merge policy'}")
    comm = None
    for p in [PATHS["nt_root"] / "templates" / "Commission", PATHS["nt_root"] / "templates"]:
        if p.exists():
            for f in p.rglob("*.xml"):
                t = f.read_text(errors="ignore")
                m = re.search(r"<PerUnit>([\d.]+)</PerUnit>", t)
                if m and ("NQ" in t or "Nasdaq" in t or "Default" in f.name):
                    comm = f"{m.group(1)} per unit ({f.name})"; break
    out(f"  commission: {comm or 'not found -> enter it by hand in the cost model (per contract per side)'}")
    for k in ("nt_strategy_cs", "nt_map_cs"):
        p = PATHS[k]
        if p.exists():
            t = p.read_text(errors="ignore")
            v = re.search(r"S1\.\d+|v2\.\d+", t)
            out(f"  {p.name}: found ({v.group(0) if v else 'version?'})")
        else:
            out(f"  {p.name}: NOT FOUND at {p}")
    verdict("NT settings", "PASS" if merge else "MANUAL", "" if merge else "read the merge policy off the NT Options window")

# =================================================================================
# G2. DATABENTO vs NINJATRADER DATA (September 2026)
# =================================================================================
def mbo_minute_bars(path, instrument=None):
    import databento as db
    store = db.DBNStore.from_file(path)
    frames = []
    for a in _iter_chunks(store):
        act = a["action"]; act = act if act.dtype.kind in "US" else act.astype("S1")
        t = a[(act == b"T") | (act == "T")]
        if len(t):
            frames.append(pd.DataFrame({
                "ts": t["ts_event"].astype("int64"), "id": t["instrument_id"].astype("int64"),
                "px": t["price"].astype("int64") / 1e9, "sz": t["size"].astype("int64"),
                "side": [s.decode() if isinstance(s, bytes) else s for s in t["side"]]}))
    if not frames:
        return pd.DataFrame()
    tr = pd.concat(frames)
    if instrument is None:
        instrument = tr.groupby("id")["sz"].sum().idxmax()
    tr = tr[tr["id"] == instrument]
    tr["minute"] = pd.to_datetime(tr["ts"], utc=True).dt.tz_convert(CT).dt.floor("min").dt.tz_localize(None)
    g = tr.groupby("minute")
    bars = pd.DataFrame({"close": g["px"].last(), "volume": g["sz"].sum(),
                         "buy": tr[tr["side"] == "B"].groupby("minute")["sz"].sum(),     # B = buy aggressor
                         "sell": tr[tr["side"] == "A"].groupby("minute")["sz"].sum()}).fillna(0)
    bars["delta"] = bars["buy"] - bars["sell"]
    return bars

def load_nt_bars():
    root = PATHS["nt_volumetric"]
    frames = []
    for f in root.glob("2026-09-*/*_Bars_*.csv"):
        try:
            x = pd.read_csv(f, usecols=["Time", "Close", "TotalVolume", "BuyingVolume", "SellingVolume", "BarDelta"])
            x["Time"] = pd.to_datetime(x["Time"]); x["run"] = f.name
            frames.append(x)
        except Exception:
            pass
    if not frames:
        return pd.DataFrame()
    nt = pd.concat(frames).sort_values(["Time", "run"]).drop_duplicates("Time", keep="last").set_index("Time")
    return nt

def run_data_parity(args):
    hdr("G2  Databento (MBO aggressor) vs NinjaTrader Volumetric, September 2026")
    nt = load_nt_bars()
    if nt.empty:
        verdict("G2 data parity", "NOT RUN", f"no NT Volumetric bars in {PATHS['nt_volumetric']}"); return
    files = dbn_files(PATHS["nq_mbo_sep2026"]) + dbn_files(PATHS["nq_mbo_oct2026"])
    rows = []
    for f in files:
        day = file_date(f)
        if day.weekday() >= 5 or day > dt.date(2026, 9, 30):
            continue
        lo = pd.Timestamp(dt.datetime.combine(day, RTH_START)); hi = pd.Timestamp(dt.datetime.combine(day, RTH_END))
        n = nt[(nt.index > lo) & (nt.index <= hi + pd.Timedelta(minutes=1))]
        if n.empty:
            continue
        try:
            b = mbo_minute_bars(f)
        except Exception as e:
            out(f"  {day}: decode error {e}"); continue
        b = b[(b.index >= lo) & (b.index < hi)]
        best = None
        for shift in (0, 1, -60, -59, 60, 61):          # NT stamps bars at the close; also allow a 1 h clock offset
            nn = n.copy(); nn.index = nn.index - pd.Timedelta(minutes=shift)
            j = b.join(nn, how="inner")
            if len(j) < 30:
                continue
            match = (abs(j["close"] - j["Close"]) < TICK / 2).mean()
            if best is None or match > best[0]:
                best = (match, shift, j)
        if best is None:
            out(f"  {day}: no overlapping minutes"); continue
        match, shift, j = best
        vol_ratio = j["TotalVolume"].sum() / max(j["volume"].sum(), 1)
        dcorr = j["delta"].corr(j["BarDelta"])
        dmae = (j["delta"] - j["BarDelta"]).abs().mean()
        rows.append({"date": day, "minutes": len(j), "nt_shift_min": shift, "close_match": round(match, 4),
                     "vol_NT_over_DB": round(vol_ratio, 4), "delta_corr": round(dcorr, 4), "delta_mean_abs_diff": round(dmae, 1),
                     "delta_sum_DB": int(j["delta"].sum()), "delta_sum_NT": int(j["BarDelta"].sum())})
        out(f"  {day}: {len(j)} min, close match {match:.1%}, vol NT/DB {vol_ratio:.3f}, delta corr {dcorr:.3f}, |dDelta| {dmae:.1f}")
        if args.max_days and len(rows) >= args.max_days:
            break
    r = pd.DataFrame(rows); r.to_csv(OUT / "G2_data_parity_sep2026.csv", index=False)
    if r.empty:
        verdict("G2 data parity", "NOT RUN", "no overlapping days"); return
    good = (r["close_match"].mean() > 0.98) and (r["vol_NT_over_DB"].between(0.97, 1.03).mean() > 0.9) and (r["delta_corr"].mean() > 0.9)
    out(f"  mean close match {r['close_match'].mean():.1%}, mean vol ratio {r['vol_NT_over_DB'].mean():.3f}, mean delta corr {r['delta_corr'].mean():.3f}")
    out("  A systematic delta difference is a bug to explain before the baseline, not a threshold to tune.")
    verdict("G2 data parity (bars)", "PASS" if good else "CHECK",
            "candidate-level part of gate 2 (Sep 28) runs with the engine")

# =================================================================================
# G1 / G3 / G5. NEED THE ENGINE PORT
# =================================================================================
def find_first(patterns):
    for root in TAPE_SEARCH:
        if not root.exists():
            continue
        for pat in patterns:
            hits = list(root.rglob(pat))
            if hits:
                return hits[0]
    return None

def run_engine_gates():
    hdr("G1 / G3 / G5  Engine parity (needs the Python port of S1.4 + map v2.3)")
    need = {
        "G1 Oct 8 tape (JeronTapeExporter)": find_first(["Tape_*2026-10-08*.csv*"]),
        "G1 Oct 8 NT strategy log":           find_first(["*2026-10-08*.csv"]) if PATHS["nt_logs"].exists() else None,
        "G3 NT map packets (recent days)":    next(iter(sorted(PATHS["nt_map_packets"].glob("PreopenPacket_*.json"), reverse=True)), None) if PATHS["nt_map_packets"].exists() else None,
        "G5 Oct 8 NT Sim fills (executions)": find_first(["*Executions*2026-10-08*", "*Fills*2026-10-08*", "*2026-10-08*Trades*.csv"]),
        "G2 Sep 28 NT strategy log":          find_first(["*2026-09-28*.csv"]) if PATHS["nt_logs"].exists() else None,
    }
    for k, v in need.items():
        out(f"  {'found  ' if v else 'MISSING'} {k}: {v or '-'}")
    try:
        import jeron_engine  # noqa: F401  (the port; not built yet as of Oct 24 2026)
        have = True
    except ImportError:
        have = False
    if not have:
        out("  jeron_engine not found: gates 1, 3 and 5 cannot run yet. Next step: port S1.4 + map v2.3 to Python.")
        out(f"  Gate 1 target when it runs: {GATE1_EXPECT}")
        for g in ("G1 tracker parity", "G3 map parity", "G5 fill parity"):
            verdict(g, "NOT RUN", "engine port not built")
        return
    from jeron_engine import parity  # expected API: parity.gate1(tape, log) etc. -> (ok, details)
    for g, fn, args in (("G1 tracker parity", parity.gate1, (need["G1 Oct 8 tape (JeronTapeExporter)"], need["G1 Oct 8 NT strategy log"])),
                        ("G3 map parity", parity.gate3, (PATHS["nt_map_packets"],)),
                        ("G5 fill parity", parity.gate5, (need["G5 Oct 8 NT Sim fills (executions)"],))):
        try:
            ok, details = fn(*args)
            out(f"  {g}: {details}")
            verdict(g, "PASS" if ok else "FAIL")
        except Exception as e:
            verdict(g, "ERROR", repr(e))

# =================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-days", type=int, default=0)
    ap.add_argument("--skip-integrity", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now()
    out(f"Jeron backtest - Phase 0 parity and data checks (design v3.4)   started {started:%Y-%m-%d %H:%M}")
    out(f"data root: {DATA_ROOT}   output: {OUT}")
    try:
        import databento  # noqa
    except ImportError:
        out("databento is not installed: run  pip install databento pandas numpy"); sys.exit(1)

    only = args.only.lower()
    df = None
    try:
        if not only or only == "paths":       check_paths()
        if not only or only == "integrity" or only in ("calendar", "roll"):
            df = run_integrity(args)
        if not only or only == "calendar":    run_calendar(df)
        if not only or only == "roll":        run_roll(df)
        if not only or only == "nt":          run_nt()
        if not only or only == "data_parity": run_data_parity(args)
        if not only or only == "engine":      run_engine_gates()
    except Exception:
        out(traceback.format_exc())

    hdr("SUMMARY")
    for g, (s, n) in verdicts.items():
        out(f"  {s:<8} {g}  {n}")
    blocking = [g for g, (s, _) in verdicts.items() if s in ("FAIL", "ERROR")]
    out("")
    out("Phase 0 passes when gates 1-3, 5 and 6 are PASS (design v3.4). "
        + ("Blocking: " + ", ".join(blocking) if blocking else "No blocking failures in the parts that ran."))
    out(f"finished {dt.datetime.now():%Y-%m-%d %H:%M}  ({(dt.datetime.now() - started).seconds // 60} min)")

    rep = OUT / f"phase0_report_{started:%Y%m%d_%H%M}.txt"
    rep.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nreport: {rep}")
    if DRIVE_PHASE0.exists():
        for f in [rep] + list(OUT.glob("*.csv")):
            shutil.copy2(f, DRIVE_PHASE0 / f.name)
        print(f"copied to {DRIVE_PHASE0}")

if __name__ == "__main__":
    main()
