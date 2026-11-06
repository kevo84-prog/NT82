r"""
l2_features.py  -  L2-only order book features for XGBoost (version L2F 1.0, Oct 22 2026)

WHERE THE NUMBERS COME FROM
  mbo  Databento L3 (MBO) files. Individual orders are used ONLY to keep the price-level book up to date.
  nt   The tracker's live L2 recordings (L2Depth_*.csv) plus the JeronTapeExporter tape for trades.

THE WALL (why these features are safe for a NinjaTrader model)
  Every feature is computed from just two inputs:
    1. the price-level book at the end of each second: top 30 levels per side, price -> total size
       (NinjaTrader's live depth feed sends 30 levels per side, aggregated by price);
    2. the trades during that second: price, size, aggressor side.
  Order IDs, queue position and individual adds/cancels never reach the feature code.

ONE ROW PER SECOND, 08:00:00-15:14:59 CT. Columns:
  t_ct                 end of the second (Central time)
  bid, ask, bid_sz, ask_sz, spread_ticks      best prices and sizes
  bid5, ask5, imb5     total size in the 5 best levels; imb5 = bid5 / (bid5 + ask5)
                       (same definition as the tracker's L2BidSize / L2AskSize / L2Imbalance at 5 levels)
  bid10, ask10, imb10  same for 10 levels
  bid30, ask30         total visible depth (30 levels)
  buy_vol, sell_vol, unk_vol, prints   traded volume by aggressor side, number of trade prints
  bid_stack5, bid_pull5, ask_stack5, ask_pull5
                       size added / removed during the second within 5 levels of the best price (at the start
                       or end of the second), NET of traded volume: per price, (size now - size a second ago
                       + volume traded against it). Positive = stacked, negative = pulled.
  bid_refill, ask_refill   the stacked part at prices that were traded against (refilled after being hit)
  book_age_s           seconds since the book last changed (tracker L2AgeSec)

Usage (from K:\Databento_BackTesting, Command Prompt):
  python l2_features.py mbo                          every weekday MBO file under this folder without output yet
  python l2_features.py mbo --day 2026-09-15 --force one day, rebuilt even if the output exists
  python l2_features.py nt --day 2026-10-22 [--l2-dir DIR] [--tape-dir DIR]
  python l2_features.py compare --day 2026-10-15     MBO vs NT for one day (needs both outputs)
Output: K:\Databento_BackTesting\l2_features\mbo\l2_1s_YYYY-MM-DD.csv.gz (and ...\nt\...)
"""
import argparse
import calendar
import csv
import datetime as dt
import glob
import gzip
import heapq
import os
import re
import sys
import time
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

VERSION = "L2F 1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(HERE, "l2_features")
NT_DIR = r"K:\Documents\NinjaTrader 8"
NT_L2_DIRS = [os.path.join(NT_DIR, "JeronLogs", "L2_staging"),
              r"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs\L2"]
NT_TAPE_DIR = os.path.join(NT_DIR, "JeronLogs", "Tape")

CT = ZoneInfo("America/Chicago")
TICK = 0.25
LEVELS = 30            # NinjaTrader depth: 30 levels per side
NEAR = 4               # best price + 4 more ticks = 5 levels
WINDOW = (dt.time(8, 0), dt.time(15, 15))
F_LAST, F_SNAPSHOT = 128, 32

COLS = ["t_ct", "bid", "ask", "bid_sz", "ask_sz", "spread_ticks",
        "bid5", "ask5", "imb5", "bid10", "ask10", "imb10", "bid30", "ask30",
        "buy_vol", "sell_vol", "unk_vol", "prints",
        "bid_stack5", "bid_pull5", "ask_stack5", "ask_pull5", "bid_refill", "ask_refill", "book_age_s"]


# =====================================================================================
#  Feature code: sees ONLY book snapshots (tick -> size, top 30) and trades. Shared by both sources.
# =====================================================================================
def clock(day, t):
    """Central wall-clock time as an integer second count (naive, so no time zone maths per record)."""
    return calendar.timegm(dt.datetime.combine(day, t).timetuple())


def features(sec, prev, cur, trades, prints, age, have_trades):
    """prev, cur: (bids, asks), each a list of (tick, size) best first. trades: {(aggr, tick): volume}."""
    b, a = cur
    r = {"t_ct": sec}
    r["bid"] = b[0][0] * TICK if b else np.nan
    r["ask"] = a[0][0] * TICK if a else np.nan
    r["bid_sz"] = b[0][1] if b else 0
    r["ask_sz"] = a[0][1] if a else 0
    r["spread_ticks"] = a[0][0] - b[0][0] if (a and b) else np.nan
    for n in (5, 10):
        bn = sum(s for _, s in b[:n]); an = sum(s for _, s in a[:n])
        r[f"bid{n}"], r[f"ask{n}"] = bn, an
        r[f"imb{n}"] = bn / (bn + an) if bn + an > 0 else np.nan
    r["bid30"] = sum(s for _, s in b); r["ask30"] = sum(s for _, s in a)

    if have_trades:
        buy = sell = unk = 0
        for (side, _), v in trades.items():
            if side == "B": buy += v
            elif side == "S": sell += v
            else: unk += v
        r["buy_vol"], r["sell_vol"], r["unk_vol"], r["prints"] = buy, sell, unk, prints
    else:
        r["buy_vol"] = r["sell_vol"] = r["unk_vol"] = r["prints"] = np.nan

    # stacking / pulling within 5 levels of the touch, net of traded volume
    for name, pside, cside, hit, sign in (("bid", prev[0], b, "S", -1), ("ask", prev[1], a, "B", 1)):
        pd_, cd = dict(pside), dict(cside)
        prices = set()
        for side_list in (pside, cside):
            if side_list:
                best = side_list[0][0]
                prices.update(best + sign * k for k in range(NEAR + 1))
        stack = pull = refill = 0
        for p in prices:
            traded = trades.get((hit, p), 0) if have_trades else 0
            net = cd.get(p, 0) - pd_.get(p, 0) + traded
            if net > 0:
                stack += net
                if traded: refill += net
            else:
                pull -= net
        r[f"{name}_stack5"], r[f"{name}_pull5"] = stack, pull
        r[f"{name}_refill"] = refill if have_trades else np.nan
    r["book_age_s"] = age
    return r


class Sampler:
    """Turns a stream of book changes and trades into one feature row per second inside the window."""

    def __init__(self, lo, hi, get_book, have_trades=True):
        self.lo, self.hi, self.get_book, self.have_trades = lo, hi, get_book, have_trades
        self.cur = None
        self.prev = None
        self.trades = defaultdict(int)
        self.prints = 0
        self.last_change = None
        self.rows = []

    def changed(self):
        self.last_change = self.cur

    def trade(self, aggr, tick, size):
        if self.cur is not None and self.lo <= self.cur < self.hi:
            self.trades[(aggr, tick)] += size
            self.prints += 1

    def advance(self, sec):
        """Close every second from self.cur up to sec - 1, using the book as it stands now."""
        if self.cur is None:
            self.cur = sec
            return
        if sec <= self.cur:
            return
        last = sec - 1
        if last >= self.lo - 1 and self.cur < self.hi:
            book = self.get_book()
            for s in range(max(self.cur, self.lo - 1), min(last, self.hi - 1) + 1):
                if s >= self.lo:
                    tr = self.trades if s == self.cur else {}
                    pr = self.prints if s == self.cur else 0
                    age = s - self.last_change if self.last_change is not None else np.nan
                    self.rows.append(features(s, self.prev or book, book, tr, pr, age, self.have_trades))
                self.prev = book
        self.trades = defaultdict(int)
        self.prints = 0
        self.cur = sec

    def finish(self):
        self.advance(self.hi)
        df = pd.DataFrame(self.rows, columns=COLS)
        if not df.empty:
            df["t_ct"] = pd.to_datetime(df["t_ct"], unit="s")
        return df


# =====================================================================================
#  Source 1: Databento MBO (L3) -> price-level book
# =====================================================================================
def mbo_files():
    out = {}
    pat = re.compile(r"glbx-mdp3-(\d{8})\.mbo\.dbn\.zst$")
    for folder, _, files in os.walk(HERE, followlinks=True):
        for f in files:
            m = pat.match(f)
            if m:
                d = dt.datetime.strptime(m.group(1), "%Y%m%d").date()
                path = os.path.join(folder, f)
                # roll-day replacements (the new front contract, bought separately) win over NQ.v.0 files
                if d not in out or ("nq_roll_" in path.lower() and "nq_roll_" not in out[d].lower()):
                    out[d] = path
    return out


def run_mbo(path, day):
    import databento as db
    noon = dt.datetime.combine(day, dt.time(12), CT)
    off = int(noon.utcoffset().total_seconds())         # UTC -> Central offset for this date
    lo, hi = clock(day, WINDOW[0]), clock(day, WINDOW[1])

    orders = {}                                          # order_id -> [side, tick, size]  (book upkeep only)
    lvl = {"B": defaultdict(int), "A": defaultdict(int)}

    def get_book():
        return (heapq.nlargest(LEVELS, lvl["B"].items()), heapq.nsmallest(LEVELS, lvl["A"].items()))

    sm = Sampler(lo, hi, get_book)
    chk_ok = chk_n = 0
    instruments = Counter()
    t_last = 0
    prev_last = True
    store = db.DBNStore.from_file(path)
    for ch in store.to_df(price_type="float", pretty_ts=False, map_symbols=False, count=2_000_000):
        acts = ch["action"].values; sides = ch["side"].values
        ticks = np.rint(ch["price"].fillna(0).values / TICK).astype(np.int64)
        sizes = ch["size"].values.astype(np.int64); oids = ch["order_id"].values
        flags = ch["flags"].values.astype(np.int64); tev = ch["ts_event"].values.astype(np.int64)
        instruments.update(ch["instrument_id"].values)
        for act, side, tk, sz, oid, fl, te in zip(acts, sides, ticks, sizes, oids, flags, tev):
            if not fl & F_SNAPSHOT:
                if te > t_last: t_last = te
                sec = t_last // 1_000_000_000 + off
                if prev_last and (sm.cur is None or sec > sm.cur):
                    sm.advance(sec)
            prev_last = bool(fl & F_LAST)

            if act == "R":
                orders.clear(); lvl["B"].clear(); lvl["A"].clear(); sm.changed(); continue
            if act == "A":
                if side not in ("B", "A"): continue
                orders[oid] = [side, tk, sz]; lvl[side][tk] += sz; sm.changed()
            elif act == "C":
                o = orders.get(oid)
                if o is None: continue
                s0, p0, z0 = o; cut = min(sz, z0)
                lvl[s0][p0] -= cut
                if lvl[s0][p0] <= 0: del lvl[s0][p0]
                o[2] -= cut
                if o[2] <= 0: del orders[oid]
                sm.changed()
            elif act == "M":
                o = orders.get(oid)
                if o is None:
                    if side in ("B", "A"):
                        orders[oid] = [side, tk, sz]; lvl[side][tk] += sz; sm.changed()
                    continue
                s0, p0, z0 = o
                lvl[s0][p0] -= z0
                if lvl[s0][p0] <= 0: del lvl[s0][p0]
                o[1], o[2] = tk, sz; lvl[s0][tk] += sz; sm.changed()
            elif act == "T":                             # trades: the resting side is updated by C/M records
                aggr = "B" if side == "B" else ("S" if side == "A" else "U")
                sm.trade(aggr, tk, sz)
                if aggr != "U" and sm.lo <= (sm.cur or 0) < sm.hi and sm.prints % 20 == 1:
                    book = lvl["A"] if aggr == "B" else lvl["B"]
                    if book:
                        best = min(book) if aggr == "B" else max(book)
                        chk_n += 1; chk_ok += (best == tk)
    df = sm.finish()
    return df, (chk_ok / chk_n if chk_n else float("nan")), instruments


# =====================================================================================
#  Source 2: NinjaTrader L2 recordings (position-based, exactly as NinjaTrader keeps its book)
#    nt   tracker recordings  L2Depth_<inst>_<date>_<HH>CT_run<stamp>.csv  + JeronTapeExporter tape
#    hlr  HLR20 recorder      NQ_L2Depth_<date>_PartNNN.csv + NQ_Trades_<date>_PartNNN.csv
#  A position-based book must be replayed from the start of the NinjaTrader run, so every file of the
#  run (including the evening before) has to be present.
# =====================================================================================
def nt_l2_files(day, dirs):
    files = []
    for d in dirs:
        for dd in (day - dt.timedelta(days=1), day):
            files += glob.glob(os.path.join(d, f"L2Depth_*_{dd.isoformat()}_*CT_run*.csv"))
    def key(f):
        m = re.search(r"_(\d{4}-\d{2}-\d{2})_(\d{4})CT_run(\d{8}-\d{6})", f)
        return (m.group(3), m.group(1), m.group(2)) if m else ("", "", f)      # run, then date, then hour
    return sorted(set(files), key=key)


def nt_tape(day, tape_dir):
    hits = glob.glob(os.path.join(tape_dir, f"Tape_NQ*_{day.isoformat()}.csv*"))
    hits = [h for h in hits if not h.endswith(".partial")]
    if not hits:
        return None
    t = pd.read_csv(hits[0])
    t["sec"] = pd.to_datetime(t["ct"]).values.astype("datetime64[s]").astype(np.int64)
    t["tick"] = np.rint(t["price"] / TICK).astype(np.int64)
    return t[["sec", "tick", "size", "side"]].to_numpy()


def nt_chunks(files):
    last_run = None
    for f in files:
        m = re.search(r"run(\d{8}-\d{6})", f)
        run = m.group(1) if m else None
        df = pd.read_csv(f, dtype={"Side": str, "Operation": str})
        df = df[df["Side"].isin(["Bid", "Ask"])].dropna(subset=["MarketTimeCT", "Position", "Price", "Volume"])
        yield (run != last_run), df["MarketTimeCT"], df["Side"].str[0].values, df["Operation"].str.upper().values, \
            df["Position"], df["Price"], df["Volume"], df["Reset"]
        last_run = run


def hlr_files(day, root, kind):
    files = []
    for dd in (day - dt.timedelta(days=1), day):
        files += glob.glob(os.path.join(root, "**", f"NQ_{kind}_{dd.isoformat()}_Part*.csv"), recursive=True)
    def key(f):
        m = re.search(r"_(\d{4}-\d{2}-\d{2})_Part(\d+)", f)
        return (m.group(1), int(m.group(2)))
    out, seen = [], set()
    for f in sorted(files, key=key):                       # the same part may exist in two folders
        if key(f) not in seen:
            seen.add(key(f)); out.append(f)
    return out


def hlr_chunks(files):
    last_seq = None
    first = True
    for f in files:
        for df in pd.read_csv(f, dtype={"Side": str, "Operation": str}, chunksize=3_000_000):
            df = df.dropna(subset=["EventTime", "Position", "Price", "Volume"])
            seq = df["Sequence"].values
            new_run = first or (last_seq is not None and len(seq) and seq[0] < last_seq)
            if last_seq is not None and len(seq) and seq[0] > last_seq + 1000:
                print(f"  note: {seq[0] - last_seq:,} sequence numbers skipped before {os.path.basename(f)} "
                      f"(other record types share the counter; large gaps can mean lost depth updates)")
            if len(seq): last_seq = seq[-1]
            first = False
            yield new_run, df["EventTime"], df["Side"].str[0].values, df["Operation"].str.upper().values, \
                df["Position"], df["Price"], df["Volume"], df["IsReset"]


def hlr_tape(day, root):
    files = hlr_files(day, root, "Trades")
    if not files:
        return None
    t = pd.concat(pd.read_csv(f) for f in files)
    t["sec"] = pd.to_datetime(t["EventTime"]).values.astype("datetime64[s]").astype(np.int64)
    t["tick"] = np.rint(t["Price"] / TICK).astype(np.int64)
    t["side"] = t["QuoteBasedAggressor"].map({"BUY": "B", "SELL": "S"}).fillna("U")
    t = t.sort_values("sec", kind="stable")
    return t[["sec", "tick", "Volume", "side"]].to_numpy()


def replay_depth(day, chunks, tape):
    lo, hi = clock(day, WINDOW[0]), clock(day, WINDOW[1])
    bids, asks = [], []                                   # [tick, size], position 0 = best

    def get_book():
        return ([(p, v) for p, v in bids[:LEVELS]], [(p, v) for p, v in asks[:LEVELS]])

    sm = Sampler(lo, hi, get_book, have_trades=tape is not None)
    ti = 0

    def feed_trades(until):
        nonlocal ti
        while ti < len(tape) and tape[ti][0] < until:
            tsec, ttk, tsz, tside = tape[ti]
            if sm.cur is not None and tsec > sm.cur:
                sm.advance(int(tsec))
            sm.trade(tside if tside in ("B", "S") else "U", int(ttk), int(tsz))
            ti += 1

    for new_run, times, sides, ops, pos, price, vol, reset in chunks:
        if new_run:
            bids.clear(); asks.clear()
        secs = pd.to_datetime(times).values.astype("datetime64[s]").astype(np.int64)
        ticks = np.rint(price.values / TICK).astype(np.int64)
        for sec, sd, op, ps, tk, vl, rst in zip(secs, sides, ops, pos.values.astype(int), ticks,
                                                vol.values.astype(np.int64), reset.values):
            if sec >= hi + 60 and sm.cur is not None and sm.cur >= hi:
                break
            if sm.cur is None or sec > sm.cur:
                if tape is not None:
                    feed_trades(sec)
                sm.advance(int(sec))
            if rst in (1, "1", True, "True"):
                bids.clear(); asks.clear()
            lst = bids if sd == "B" else asks
            if ps < 0: continue
            if op == "ADD":
                if ps <= len(lst): lst.insert(ps, [tk, vl])
            elif op == "UPDATE":
                if ps < len(lst): lst[ps] = [tk, vl]
                elif ps == len(lst): lst.append([tk, vl])
            elif op == "REMOVE":
                if ps < len(lst): del lst[ps]
            sm.changed()
    if tape is not None:
        feed_trades(hi)
    return sm.finish()


def run_nt(day, l2_dirs, tape_dir):
    files = nt_l2_files(day, l2_dirs)
    if not files:
        sys.exit(f"No L2Depth files for {day} in: " + "; ".join(l2_dirs))
    tape = nt_tape(day, tape_dir)
    return replay_depth(day, nt_chunks(files), tape), tape is not None, files


def run_hlr(day, root):
    files = hlr_files(day, root, "L2Depth")
    if not files:
        sys.exit(f"No NQ_L2Depth files for {day} (or the day before) under {root}")
    tape = hlr_tape(day, root)
    return replay_depth(day, hlr_chunks(files), tape), tape is not None, files


# =====================================================================================
#  Compare MBO vs NT for one day
# =====================================================================================
def compare(day, other="nt"):
    a = pd.read_csv(os.path.join(OUT_ROOT, "mbo", f"l2_1s_{day}.csv.gz"), parse_dates=["t_ct"])
    b = pd.read_csv(os.path.join(OUT_ROOT, other, f"l2_1s_{day}.csv.gz"), parse_dates=["t_ct"])
    m = a.merge(b, on="t_ct", suffixes=("_mbo", "_nt"))
    m = m[(m["book_age_s_nt"] <= 5) & m["bid_nt"].notna()]       # seconds where NT's book was live
    print(f"{day}: {len(m):,} seconds with a live NT book")
    out = []
    for c in ["bid", "ask"]:
        out.append((c, f"{(m[c + '_mbo'] == m[c + '_nt']).mean():.1%} identical", ""))
    for c in ["bid_sz", "ask_sz", "bid5", "ask5", "bid10", "ask10", "imb5", "imb10",
              "buy_vol", "sell_vol", "bid_stack5", "bid_pull5", "ask_stack5", "ask_pull5", "bid_refill", "ask_refill"]:
        x, y = m[c + "_mbo"], m[c + "_nt"]
        ok = x.notna() & y.notna()
        if ok.sum() < 100:
            out.append((c, "not enough data", "")); continue
        corr = np.corrcoef(x[ok], y[ok])[0, 1]
        mad = (x[ok] - y[ok]).abs().median()
        out.append((c, f"corr {corr:.3f}", f"median abs diff {mad:.3g}"))
    for side, thr in (("long", 0.60), ("short", 0.40)):
        f = (lambda s: s >= thr) if side == "long" else (lambda s: s <= thr)
        ok = m["imb5_mbo"].notna() & m["imb5_nt"].notna()
        out.append((f"L2Aligned {side}", f"{(f(m.loc[ok, 'imb5_mbo']) == f(m.loc[ok, 'imb5_nt'])).mean():.1%} agree", ""))
    for row in out:
        print(f"  {row[0]:<16} {row[1]:<22} {row[2]}")
    path = os.path.join(OUT_ROOT, f"compare_{day}_mbo_vs_{other}.csv")
    pd.DataFrame(out, columns=["feature", "match", "detail"]).to_csv(path, index=False)
    print("Saved", path)


# =====================================================================================
def save(df, source, day, extra=""):
    folder = os.path.join(OUT_ROOT, source)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"l2_1s_{day}.csv.gz")
    df = df.copy()
    for c in ("imb5", "imb10"):
        df[c] = df[c].round(4)
    df.to_csv(path, index=False, compression="gzip", date_format="%Y-%m-%d %H:%M:%S")
    crossed = int((df["bid"] >= df["ask"]).sum())
    print(f"  {day} {source}: {len(df):,} seconds | crossed-book seconds {crossed} | "
          f"{os.path.getsize(path) / 1_048_576:.1f} MB {extra}")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", choices=["mbo", "nt", "hlr", "compare"])
    ap.add_argument("--hlr-dir", default=r"K:\HLR20 Research Recorder", help="HLR20 recorder folder (searched with subfolders)")
    ap.add_argument("--against", default="nt", choices=["nt", "hlr"], help="compare: which NinjaTrader source")
    ap.add_argument("--day", help="YYYY-MM-DD")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--l2-dir", action="append", help="folder with L2Depth_*.csv (repeatable)")
    ap.add_argument("--tape-dir", default=NT_TAPE_DIR)
    a = ap.parse_args()
    day = dt.date.fromisoformat(a.day) if a.day else None

    if a.source == "compare":
        if not day: sys.exit("--day is required")
        compare(day, a.against); return

    if a.source == "hlr":
        if not day: sys.exit("--day is required")
        t0 = time.time()
        df, have_tape, files = run_hlr(day, a.hlr_dir)
        save(df, "hlr", day, f"| {len(files)} L2 files | tape {'yes' if have_tape else 'NO (book-only)'} | "
                             f"{time.time() - t0:.0f}s")
        return

    if a.source == "nt":
        if not day: sys.exit("--day is required")
        t0 = time.time()
        df, have_tape, files = run_nt(day, a.l2_dir or NT_L2_DIRS, a.tape_dir)
        save(df, "nt", day, f"| {len(files)} L2 files | tape {'yes' if have_tape else 'NO (book-only)'} | "
                            f"{time.time() - t0:.0f}s")
        return

    files = mbo_files()
    days = [day] if day else sorted(d for d in files if d.weekday() < 5)
    if day and day not in files:
        sys.exit(f"No MBO file for {day} under {HERE}")
    print(f"{VERSION}: {len(days)} MBO day(s)")
    for d in days:
        out = os.path.join(OUT_ROOT, "mbo", f"l2_1s_{d}.csv.gz")
        if os.path.exists(out) and not a.force:
            continue
        t0 = time.time()
        df, chk, inst = run_mbo(files[d], d)
        if df.empty or df["bid"].isna().all():
            print(f"  {d}: no book in the window (holiday?), skipped"); continue
        note = f"| trades at the rebuilt touch {chk:.1%} | {time.time() - t0:.0f}s"
        if len(inst) > 1:
            note += f" | WARNING {len(inst)} instruments in file"
        save(df, "mbo", d, note)


if __name__ == "__main__":
    main()
