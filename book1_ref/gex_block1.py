r"""
gex_block1.py  -  replica GEX levels for every backtest session (v1.0, Oct 24 2026)

Same method as mq_daily.py / gex-menthorq-replication.md (mq_levels.compute_levels + gex_calc.cme_day, unchanged):
  report date D = the previous session, levels used for session D+1 (day D's levels are known that evening)
  options     every CME option on the front NQ contract (quarterly + weeklies Q1A-Q5D, QN1-QN4, QNE)
  OI          freshest CME open interest published before 11 PM ET on D
  IV          from each option's settlement on D;  S = the front future's settlement on D
Only change: reads the Block 1 download layout (raw\block1\opt_<root>_<schema>\...\one file per UTC day).
Front contract = highest CME cleared volume among values PUBLISHED before 11 PM ET on D (no look-ahead:
CME publishes D's own cleared volume the next morning, after the 08:10 CT pre-open).

Sessions come from data_integrity_*.csv (NORMAL and HALF_DAY_1215 days).
Output: gex_levels_block1.csv (one row per session). Resumable; --budget seconds stops cleanly.
  python gex_block1.py                 all sessions not done yet
  python gex_block1.py --budget 150    stop starting new sessions after 150 s
"""
import argparse
import datetime as dt
import glob
import os
import re
import sys
import time
from datetime import datetime, time as dtime
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
import databento as db                     # noqa: E402
import gex_calc as gc                      # noqa: E402
from mq_levels import compute_levels       # noqa: E402

RAW = BASE / "raw" / "block1"
CACHE = BASE / "gex_cache"
OUT = BASE / "gex_levels_block1.csv"
ROOTS = ["NQ"] + [f"Q{w}{d}" for d in "ABCD" for w in range(1, 6)] + [f"QN{w}" for w in range(1, 5)] + ["QNE"]
VERSION = "GEXB1 1.1"
# NinjaTrader rollover dates (same table as data_integrity.py): the contract the chart is on from that date
NT_ROLLS = [(dt.date(2025, 9, 15), "NQZ5"), (dt.date(2025, 12, 15), "NQH6"), (dt.date(2026, 3, 16), "NQM6"),
            (dt.date(2026, 6, 12), "NQU6"), (dt.date(2026, 9, 14), "NQZ6"), (dt.date(2026, 12, 14), "NQH7")]
LEVEL_COLS = ["call_resistance", "put_support", "hvl", "call_resistance_0dte", "put_support_0dte", "hvl_0dte"]


def nt_contract(d):
    cur = None
    for start, sym in NT_ROLLS:
        if d >= start:
            cur = sym
    return cur


def add_nt_columns(res):
    """Levels in the price of the contract NinjaTrader trades that session (shift by the settlement spread on D)."""
    out = []
    for _, r in res.iterrows():
        sess, D = dt.date.fromisoformat(r.session), dt.date.fromisoformat(r.report_date)
        nt = nt_contract(sess)
        shift = 0.0
        if isinstance(r.get("front"), str) and nt != r.front:
            fs = pd.concat([x for x in (extract("fut", "NQ", "statistics", y) for y in days(D, D + dt.timedelta(days=1))) if len(x)])
            fs = fs[(fs.stat_type == 3) & (fs.ts_ref.dt.date == D)]
            px = fs.sort_values("ts_recv").groupby("symbol").price.last()
            shift = float(px[nt] - px[r.front]) if nt in px and r.front in px else float("nan")
        row = r.to_dict()
        row["nt_contract"], row["nt_shift_pts"] = nt, shift
        for c in LEVEL_COLS:
            row[c + "_nt"] = r[c] + shift if pd.notna(r.get(c)) else float("nan")
        out.append(row)
    return pd.DataFrame(out)


def day_file(folder_glob, day):
    hits = glob.glob(str(RAW / folder_glob / "*" / f"glbx-mdp3-{day:%Y%m%d}.*.dbn.zst"))
    return hits[0] if hits else None


def extract(kind, root, schema, day):
    """One UTC-day file -> small cached extract (or an empty frame if the root had no file that day)."""
    CACHE.mkdir(exist_ok=True)
    cp = CACHE / f"{kind}_{root}_{schema}_{day:%Y%m%d}.pkl"
    if cp.exists():
        return pd.read_pickle(cp)
    folder = f"opt_{root.lower()}_{schema}" if kind == "opt" else f"nq_fut_{schema}"
    f = day_file(folder, day)
    df = pd.DataFrame()
    if f:
        parts = []
        for ch in db.DBNStore.from_file(f).to_df(count=2_000_000):
            if schema == "definition":
                ch = ch[ch.instrument_class.isin(["C", "P"])] if kind == "opt" else ch
                ch = ch[["raw_symbol", "instrument_class", "strike_price", "expiration", "underlying", "asset"]]
            else:
                keep = [3, 9] if kind == "opt" else [3, 6]
                ch = ch[ch.stat_type.isin(keep)][["ts_ref", "price", "quantity", "stat_type", "symbol"]]
                ch = ch.reset_index()          # ts_recv becomes a column
            parts.append(ch)
        df = pd.concat(parts) if parts else pd.DataFrame()
    df.to_pickle(cp)
    return df


def days(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(days=1)


def build(D):
    """Assemble what gex_calc.load_cme returns, for report date D only."""
    defs = [extract("opt", r, "definition", x) for r in ROOTS for x in days(D - dt.timedelta(days=1), D)]
    d = pd.concat([x for x in defs if len(x)])
    nq_assets = d.asset.astype(str).str.match(r"^(NQ|Q[1-5][A-D]|QN[1-5E])$")
    d = d[nq_assets & d.instrument_class.isin(["C", "P"])].drop_duplicates("raw_symbol", keep="last")
    d = d.rename(columns={"raw_symbol": "symbol", "instrument_class": "cp", "strike_price": "strike"})
    d["exp"] = d.expiration.dt.tz_convert("America/New_York").dt.date
    d = d[["symbol", "cp", "strike", "exp", "underlying"]]

    stats = [extract("opt", r, "statistics", x) for r in ROOTS for x in days(D - dt.timedelta(days=5), D + dt.timedelta(days=1))]
    s = pd.concat([x for x in stats if len(x)])
    oi = s[s.stat_type == 9][["ts_recv", "ts_ref", "quantity", "symbol"]].rename(columns={"quantity": "oi"})
    st = s[s.stat_type == 3][["ts_recv", "ts_ref", "price", "symbol"]].copy()
    st["date"] = st.ts_ref.dt.date
    st = st.sort_values("ts_recv").groupby(["date", "symbol"], as_index=False).price.last()

    fs = pd.concat([x for x in (extract("fut", "NQ", "statistics", y) for y in days(D - dt.timedelta(days=4), D + dt.timedelta(days=1))) if len(x)])
    fs = fs[fs.symbol.str.match(r"^NQ[HMUZ]\d$", na=False)].copy()
    f3 = fs[fs.stat_type == 3].copy()
    f3["date"] = f3.ts_ref.dt.date
    fut = f3.sort_values("ts_recv").groupby(["date", "symbol"], as_index=False).price.last()

    cutoff = pd.Timestamp(datetime.combine(D, dtime(23, 0)), tz="America/New_York").tz_convert("UTC")
    v = fs[(fs.stat_type == 6) & (fs.ts_recv <= cutoff)]
    if v.empty:
        return None
    # each contract's most recent published cleared volume (a day's figures can arrive incomplete
    # before the cutoff, e.g. Nov 3 2025, so one contract's older full-day volume still counts)
    v = v[v.quantity > 0].sort_values(["ts_ref", "ts_recv"]).groupby("symbol").last()
    if v.empty:
        return None
    front = v.quantity.idxmax()
    return d, oi, st, fut, front, v.loc[front, "ts_ref"].date()


def sessions():
    hits = sorted(glob.glob(str(BASE / "data_integrity_20*.csv")))
    if not hits:
        sys.exit("Run data_integrity.py first (it decides which dates are sessions).")
    di = pd.read_csv(hits[-1])
    di = di[di.used_by_backtest & di.session.isin(["NORMAL", "HALF_DAY_1215"])]
    return sorted(dt.date.fromisoformat(x) for x in di.date.unique())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="d0", default="2025-10-22")
    ap.add_argument("--to", dest="d1", default="2026-04-21")
    ap.add_argument("--budget", type=float, default=0)
    ap.add_argument("--redo", default="", help="comma-separated sessions to recompute")
    ap.add_argument("--check-front", action="store_true", help="list sessions whose front contract changes, then stop")
    a = ap.parse_args()
    if a.redo and OUT.exists():
        res = pd.read_csv(OUT)
        res[~res.session.isin(a.redo.split(","))].to_csv(OUT, index=False)
    if a.check_front:
        res = pd.read_csv(OUT)
        changed = []
        for sess, D, old in zip(res.session, res.report_date, res.front):
            b = build(dt.date.fromisoformat(D))
            if b is not None and b[4] != old:
                changed.append(sess)
                print(f"  {sess}: {old} -> {b[4]}")
        print("CHANGED:" + ",".join(changed))
        return
    t0 = time.time()
    allsess = sessions()
    d0, d1 = dt.date.fromisoformat(a.d0), dt.date.fromisoformat(a.d1)
    done = set(pd.read_csv(OUT).session) if OUT.exists() else set()
    todo = [(allsess[i - 1], s) for i, s in enumerate(allsess) if i > 0 and d0 <= s <= d1 and s.isoformat() not in done]
    print(f"{VERSION}: {len(todo)} sessions to compute", flush=True)
    longest = 0
    for D, sess in todo:
        if a.budget and time.time() - t0 + max(longest, 20) > a.budget:
            print(f"PAUSED: {len(todo)} left before this run; run again to continue.")
            return
        t1 = time.time()
        row = {"session": sess.isoformat(), "report_date": D.isoformat()}
        try:
            b = build(D)
            if b is None:
                raise ValueError("no cleared volume published before the cutoff")
            d, oi, st, fut, front, vol_date = b
            fu = fut[(fut.date == D) & (fut.symbol == front)].price
            if fu.empty:
                raise ValueError(f"no {front} settlement on {D}")
            S = float(fu.iloc[0])
            chain = gc.cme_day(D, sess, d, oi, st, fut)
            if chain is None or chain.empty:
                raise ValueError("empty option chain")
            lv = compute_levels(chain, S, front, sess)
            row.update(front=front, front_by_volume_of=vol_date.isoformat(), settle=S, **lv,
                       ok=bool(lv["options_used"] >= 200 and np.isfinite(lv["hvl"])), error="")
        except Exception as ex:                       # noqa: BLE001
            row.update(ok=False, error=str(ex)[:200])
        row["seconds"] = round(time.time() - t1)
        longest = max(longest, time.time() - t1)
        pd.DataFrame([row]).to_csv(OUT, mode="a", header=not OUT.exists(), index=False)
        print(f"  {sess} (D={D}) {row.get('front', ''):<5} S={row.get('settle', '')}  CR={row.get('call_resistance', '')}  "
              f"PS={row.get('put_support', '')}  HVL={row.get('hvl', '')}  opts={row.get('options_used', '')}  "
              f"{'OK' if row['ok'] else 'CHECK ' + row['error']}  {row['seconds']}s", flush=True)
    res = pd.read_csv(OUT)
    res = res.drop(columns=[c for c in res.columns if c.endswith("_nt") or c in ("nt_contract", "nt_shift_pts")])
    res = add_nt_columns(res.sort_values("session"))
    res.to_csv(OUT, index=False)
    moved = res[res.nt_shift_pts != 0]
    for _, r in moved.iterrows():
        print(f"  {r.session}: GEX from {r.front}, chart on {r.nt_contract}: levels shifted {r.nt_shift_pts:+.2f} pts")
    print(f"DONE: {len(res)} sessions, {int(res.ok.sum())} OK. Saved {OUT}")


if __name__ == "__main__":
    main()
