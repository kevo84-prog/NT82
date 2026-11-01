r"""
data_integrity.py  -  parity gate 6: checks every NQ MBO (L3) file before the backtest uses it  (v1.0, Oct 24 2026)

For every glbx-mdp3-YYYYMMDD.mbo.dbn.zst under K:\Databento_BackTesting (weekdays only):
  - decodes the whole file (decode errors are reported, never skipped silently)
  - contracts present (instrument IDs -> NQ contract names from the futures definition files)
  - which contract NinjaTrader was on that date (its roll dates) and whether the file the backtest uses matches
  - first and last event time, the book snapshot at the start of the file
  - cash session 08:30-15:00 CT: trades, volume, first/last trade, gaps over 60 s in book updates and in trades
  - session type from the timestamps: NORMAL, HALF_DAY (trading stops before 12:15 CT), NO_CASH (almost no trades)
  - Databento's own condition for the date (available / degraded) from condition.json
Writes data_integrity_<from>_<to>.csv and prints every file that needs a look.

Usage (Command Prompt, from K:\Databento_BackTesting):
  python data_integrity.py                       every MBO file, skipping files already in data_integrity_cache.csv
  python data_integrity.py --from 2025-10-21 --to 2026-04-21
  python data_integrity.py --force               recheck everything
Takes roughly 30-60 seconds per file.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import time
from collections import Counter
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

VERSION = "DI 1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data_integrity_cache.csv")
CT = ZoneInfo("America/Chicago")
F_SNAPSHOT = 32
GAP_S = 60

# NinjaTrader rollover dates (from its database on Kyron's PC, Oct 24 2026): the contract it is on from that date
NT_ROLLS = [
    (dt.date(2025, 6, 16), "NQU5"),
    (dt.date(2025, 9, 15), "NQZ5"),
    (dt.date(2025, 12, 15), "NQH6"),
    (dt.date(2026, 3, 16), "NQM6"),
    (dt.date(2026, 6, 12), "NQU6"),
    (dt.date(2026, 9, 14), "NQZ6"),
    (dt.date(2026, 12, 14), "NQH7"),
]


def nt_contract(d):
    cur = None
    for start, sym in NT_ROLLS:
        if d >= start:
            cur = sym
    return cur


def find_mbo():
    pat = re.compile(r"glbx-mdp3-(\d{8})\.mbo\.dbn\.zst$")
    out = []
    for folder, _, files in os.walk(HERE):
        for f in files:
            m = pat.match(f)
            if m:
                d = dt.datetime.strptime(m.group(1), "%Y%m%d").date()
                if d.weekday() < 5:
                    out.append((d, os.path.join(folder, f)))
    return sorted(out)


def used_file(files):
    """Same rule as l2_features.py: a roll replacement (path contains nq_roll_) wins for its date."""
    used = {}
    for d, p in files:
        if d not in used or ("nq_roll_" in p.lower() and "nq_roll_" not in used[d].lower()):
            used[d] = p
    return used


def condition_for(path, d):
    c = os.path.join(os.path.dirname(path), "condition.json")
    try:
        for row in json.load(open(c)):
            if row.get("date") == d.isoformat():
                return row.get("condition", "")
    except Exception:
        pass
    return "unknown"


def id_to_symbol():
    """instrument_id -> raw symbol, from every futures definition file and from MBO files bought by raw symbol."""
    import databento as db
    ids = {}
    for f in glob.glob(os.path.join(HERE, "**", "*.definition.dbn.zst"), recursive=True):
        if "fut_definition" not in f:
            continue
        try:
            df = db.DBNStore.from_file(f).to_df(map_symbols=False)
            for i, s in zip(df["instrument_id"].values, df["raw_symbol"].values):
                if isinstance(s, str) and s.startswith(("NQ", "ES")) and len(s) <= 5:
                    ids[int(i)] = s
        except Exception:
            pass
    for f in glob.glob(os.path.join(HERE, "**", "nq_roll_*", "**", "*.mbo.dbn.zst"), recursive=True):
        try:
            for sym, maps in db.DBNStore.from_file(f).metadata.mappings.items():
                for mp in maps:
                    ids.setdefault(int(mp["symbol"]), sym)
        except Exception:
            pass
    return ids


def check_file(path, d, ids):
    import databento as db
    noon = dt.datetime.combine(d, dt.time(12), CT)
    off_ns = int(noon.utcoffset().total_seconds()) * 1_000_000_000
    day0 = np.datetime64(d.isoformat(), "ns").astype(np.int64)        # midnight of the date, CT wall clock
    rth_lo = day0 + (8 * 3600 + 30 * 60) * 1_000_000_000
    rth_hi = day0 + 15 * 3600 * 1_000_000_000

    r = dict(date=d.isoformat(), file=os.path.relpath(path, HERE), size_mb=round(os.path.getsize(path) / 1e6, 1),
             databento_condition=condition_for(path, d), decode="OK", records=0, snapshot_records=0)
    inst = Counter()
    ev_first = ev_last = None
    rth_events, rth_trades = [], []
    rth_vol = 0
    try:
        store = db.DBNStore.from_file(path)
        for ch in store.to_df(pretty_ts=False, map_symbols=False, count=3_000_000):
            fl = ch["flags"].values.astype(np.int64)
            snap = (fl & F_SNAPSHOT) != 0
            r["records"] += len(ch)
            r["snapshot_records"] += int(snap.sum())
            live = ~snap
            if not live.any():
                continue
            te = ch["ts_event"].values.astype(np.int64)[live] + off_ns          # CT wall clock, ns
            inst.update(ch["instrument_id"].values[live].tolist())
            ev_first = te.min() if ev_first is None else min(ev_first, te.min())
            ev_last = te.max() if ev_last is None else max(ev_last, te.max())
            m = (te >= rth_lo) & (te < rth_hi)
            if m.any():
                rth_events.append(np.unique(te[m] // 1_000_000_000))
                acts = ch["action"].values[live][m]
                tr = acts == "T"
                if tr.any():
                    rth_trades.append(np.unique(te[m][tr] // 1_000_000_000))
                    rth_vol += int(ch["size"].values[live][m][tr].astype(np.int64).sum())
    except Exception as ex:
        r["decode"] = "ERROR: " + str(ex)[:150]

    def gaps(secs_list):
        if not secs_list:
            return np.inf, 1
        s = np.unique(np.concatenate(secs_list))
        edges = np.concatenate([[rth_lo // 1_000_000_000], s, [rth_hi // 1_000_000_000]])
        g = np.diff(edges)
        return float(g.max()), int((g > GAP_S).sum())

    to_ct = lambda ns: "" if ns is None else str(pd.Timestamp(int(ns)))
    total = sum(inst.values())
    main_id, main_n = (inst.most_common(1)[0] if inst else (None, 0))
    r["contracts"] = "; ".join(f"{ids.get(int(i), 'id:' + str(i))} {n / total:.1%}" for i, n in inst.most_common(4)) if total else ""
    r["main_contract"] = ids.get(int(main_id), f"id:{main_id}") if main_id is not None else ""
    r["first_event_ct"], r["last_event_ct"] = to_ct(ev_first), to_ct(ev_last)
    r["rth_trades_seconds"] = int(sum(len(x) for x in rth_trades))
    r["rth_volume"] = rth_vol
    if rth_trades:
        allt = np.unique(np.concatenate(rth_trades))
        r["rth_first_trade_ct"] = str(pd.Timestamp(int(allt[0]), unit="s").time())
        r["rth_last_trade_ct"] = str(pd.Timestamp(int(allt[-1]), unit="s").time())
    else:
        r["rth_first_trade_ct"] = r["rth_last_trade_ct"] = ""
    r["max_gap_book_s"], r["gaps_book_over_60s"] = gaps(rth_events)
    r["max_gap_trades_s"], r["gaps_trades_over_60s"] = gaps(rth_trades)
    last_t = r["rth_last_trade_ct"]
    if rth_vol < 5000:
        r["session"] = "NO_CASH"
    elif last_t and last_t < "12:15:00":
        r["session"] = "HALF_DAY"
    else:
        r["session"] = "NORMAL"
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="d0")
    ap.add_argument("--to", dest="d1")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--budget", type=float, default=0, help="stop starting new files after this many seconds (0 = no limit)")
    ap.add_argument("--shard", default="", help="i/n: check only every n-th file starting at i (for parallel runs)")
    a = ap.parse_args()
    t_start = time.time()
    d0 = dt.date.fromisoformat(a.d0) if a.d0 else dt.date.min
    d1 = dt.date.fromisoformat(a.d1) if a.d1 else dt.date.max

    files = [(d, p) for d, p in find_mbo() if d0 <= d <= d1]
    if not files:
        sys.exit("No MBO files found in that range.")
    used = used_file(files)
    ids_path = os.path.join(HERE, "data_integrity_ids.json")
    if os.path.exists(ids_path) and not a.force:
        ids = {int(k): v for k, v in json.load(open(ids_path)).items()}
    else:
        ids = id_to_symbol()
        json.dump({str(k): v for k, v in ids.items()}, open(ids_path, "w"))
    cache_files = glob.glob(CACHE.replace(".csv", "*.csv"))
    if a.force and not a.shard:
        for f in cache_files:
            os.remove(f)
        cache_files = []
    cache = pd.concat([pd.read_csv(f) for f in cache_files], ignore_index=True) if cache_files else pd.DataFrame()
    my_cache = CACHE.replace(".csv", f"_{a.shard.split('/')[0]}.csv") if a.shard else CACHE
    done = set(cache["file"]) if len(cache) else set()
    print(f"{VERSION}: {len(files)} weekday MBO files, {len(ids)} contract IDs known")

    rows = []
    todo = [(d, p) for d, p in files if os.path.relpath(p, HERE) not in done]
    if a.shard:
        i, n = (int(x) for x in a.shard.split("/"))
        todo = todo[i::n]
    longest = 0
    stopped = False
    for d, p in todo:
        if a.budget and time.time() - t_start + max(longest, 30) > a.budget:
            stopped = True
            break
        t0 = time.time()
        r = check_file(p, d, ids)
        r["seconds"] = round(time.time() - t0)
        longest = max(longest, time.time() - t0)
        rows.append(r)
        pd.DataFrame([r]).to_csv(my_cache, mode="a", header=not os.path.exists(my_cache),
                                 index=False)
        print(f"  {d} {r['main_contract']:<8} {r['session']:<8} vol {r['rth_volume']:>8,} | "
              f"max gap book {r['max_gap_book_s']:>6.0f}s trades {r['max_gap_trades_s']:>6.0f}s | "
              f"{r['databento_condition']} | {r['decode'][:20]} | {r['seconds']}s")

    if stopped or a.shard:
        left = len(todo) - len(rows)
        print(f"PAUSED: {len(rows)} checked this run, {left} still to do in this run's list. Run again to continue.")
        return
    allr = pd.concat([cache, pd.DataFrame(rows)], ignore_index=True) if len(cache) else pd.DataFrame(rows)
    allr = allr.drop_duplicates("file", keep="last")
    allr["date_d"] = pd.to_datetime(allr["date"]).dt.date
    allr = allr[(allr["date_d"] >= d0) & (allr["date_d"] <= d1)]
    allr["used_by_backtest"] = [used.get(dd) is not None and os.path.relpath(used[dd], HERE) == f
                                for dd, f in zip(allr["date_d"], allr["file"])]
    allr["nt_contract"] = [nt_contract(dd) for dd in allr["date_d"]]
    # session type from the timestamps: CME halts equity futures at 12:00 CT on holidays (no cash session);
    # scheduled early closes (day after Thanksgiving, Christmas Eve) end at 12:15 CT
    def session_type(vol, last):
        last = "" if not isinstance(last, str) else last
        if vol < 5000 or not last:
            return "CLOSED"
        if last < "12:05:00":
            return "HOLIDAY_HALT_1200"
        if last < "12:30:00":
            return "HALF_DAY_1215"
        return "NORMAL"
    allr["session"] = [session_type(v, l) for v, l in zip(allr["rth_volume"], allr["rth_last_trade_ct"])]
    allr["contract_ok"] = [(not u) or (m == n) for u, m, n in zip(allr["used_by_backtest"], allr["main_contract"], allr["nt_contract"])]
    allr = allr.drop(columns="date_d").sort_values(["date", "used_by_backtest"])
    lo, hi = allr["date"].min(), allr["date"].max()
    out = os.path.join(HERE, f"data_integrity_{lo}_{hi}.csv")
    allr.to_csv(out, index=False)

    u = allr[allr["used_by_backtest"]]
    flag = u[(u["decode"] != "OK") | (~u["contract_ok"]) | (u["session"] != "NORMAL") |
             (u["databento_condition"] != "available") | (u["gaps_book_over_60s"] > 0) | (u["gaps_trades_over_60s"] > 0)]
    print(f"\n{len(u)} dates checked (file the backtest uses). Needs a look: {len(flag)}")
    if len(flag):
        cols = ["date", "main_contract", "nt_contract", "session", "rth_volume", "rth_last_trade_ct",
                "gaps_book_over_60s", "max_gap_book_s", "gaps_trades_over_60s", "max_gap_trades_s",
                "databento_condition", "decode"]
        print(flag[cols].to_string(index=False))
    print("Saved", out)


if __name__ == "__main__":
    main()
