"""Databento MBO -> JeronHarness tape (JE 0.2, Oct 25 2026).

One row per Databento trade record (action T = the aggressing order, one per price level it trades at),
the same unit as a NinjaTrader Last tick. bid/ask = the best bid/ask of the order book rebuilt from the MBO
records, as it stood just BEFORE the event that contains the trade (NT sends its Last tick with the quote it
had then). The exchange aggressor flag is kept in a column (B / S / U) for the design's MBO_AGGRESSOR footprint.

Time = ts_event (CME match time) converted to US Central, 7 decimals, as NinjaTrader shows exchange time.
Usage: python -m jeron_engine.mbo_tape <out.csv.gz> <mbo file> [<mbo file> ...]   (files in time order)
"""
import gzip, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

CT = ZoneInfo("America/Chicago")
TICK = 0.25
F_LAST, F_SNAPSHOT = 128, 32
HEADER = "time_local,price,bid,ask,volume,aggressor\n"


def ct_text(ns):
    t = dt.datetime.fromtimestamp(ns // 1_000_000_000, tz=dt.timezone.utc).astimezone(CT)
    return t.strftime("%Y-%m-%d %H:%M:%S") + "." + f"{(ns % 1_000_000_000) // 100:07d}"


class Book:
    """Price-level book with cached best bid / ask (ticks)."""
    def __init__(self):
        self.orders = {}
        self.lvl = {"B": {}, "A": {}}
        self.best = {"B": None, "A": None}

    def clear(self):
        self.orders.clear(); self.lvl["B"].clear(); self.lvl["A"].clear(); self.best = {"B": None, "A": None}

    def _add(self, side, tk, sz):
        d = self.lvl[side]; d[tk] = d.get(tk, 0) + sz
        b = self.best[side]
        if b is None or (tk > b if side == "B" else tk < b): self.best[side] = tk

    def _sub(self, side, tk, sz):
        d = self.lvl[side]; v = d.get(tk, 0) - sz
        if v > 0: d[tk] = v
        else:
            d.pop(tk, None)
            if self.best[side] == tk:
                self.best[side] = (max(d) if side == "B" else min(d)) if d else None

    def add(self, oid, side, tk, sz):
        if side not in ("B", "A"): return
        self.orders[oid] = [side, tk, sz]; self._add(side, tk, sz)

    def cancel(self, oid, sz):
        o = self.orders.get(oid)
        if o is None: return
        cut = min(sz, o[2]); self._sub(o[0], o[1], cut); o[2] -= cut
        if o[2] <= 0: del self.orders[oid]

    def modify(self, oid, side, tk, sz):
        o = self.orders.get(oid)
        if o is None: self.add(oid, side, tk, sz); return
        self._sub(o[0], o[1], o[2]); o[1], o[2] = tk, sz; self._add(o[0], tk, sz)


def build(out_path, files, front_only=True, header=True, time_field="ts_event", end_ns=None):
    """end_ns: stop at this exchange time (ns since epoch, exclusive); used to keep holdout data out of a tape."""
    import databento as db
    book = Book()
    n = 0
    in_event = False
    ev_bid = ev_ask = None
    with gzip.open(out_path, "wt", newline="") as out:
        if header: out.write(HEADER)
        for path in files:
            store = db.DBNStore.from_file(path)
            front = None
            for ch in store.to_df(price_type="float", pretty_ts=False, map_symbols=False, count=2_000_000):
                if front is None:   # one contract per file (NQ.v.0 or a roll file); keep the most traded id
                    ids = ch.loc[ch["action"] == "T", "instrument_id"]
                    front = int(ids.mode().iloc[0]) if len(ids) else int(ch["instrument_id"].iloc[0])
                acts = ch["action"].values; sides = ch["side"].values
                ticks = np.rint(ch["price"].fillna(0).values / TICK).astype(np.int64)
                sizes = ch["size"].values.astype(np.int64); oids = ch["order_id"].values
                flags = ch["flags"].values.astype(np.int64); tev = (ch.index.values if time_field == "ts_recv" and "ts_recv" not in ch.columns else ch[time_field].values).astype(np.int64)
                iids = ch["instrument_id"].values
                rows = []
                stop = False
                for act, side, tk, sz, oid, fl, te, iid in zip(acts, sides, ticks, sizes, oids, flags, tev, iids):
                    if end_ns is not None and te >= end_ns: stop = True; break
                    if front_only and iid != front: continue
                    if not in_event:                      # first record of an event: freeze the quote before it
                        ev_bid, ev_ask = book.best["B"], book.best["A"]
                        in_event = True
                    if act == "R": book.clear()
                    elif act == "A": book.add(oid, side, tk, sz)
                    elif act == "C": book.cancel(oid, sz)
                    elif act == "M": book.modify(oid, side, tk, sz)
                    elif act == "T" and not fl & F_SNAPSHOT and sz > 0:
                        aggr = "B" if side == "B" else ("S" if side == "A" else "U")
                        rows.append(f"{ct_text(te)},{tk * TICK:.2f},{'' if ev_bid is None else f'{ev_bid * TICK:.2f}'},"
                                    f"{'' if ev_ask is None else f'{ev_ask * TICK:.2f}'},{sz},{aggr}\n")
                    if fl & F_LAST: in_event = False
                out.writelines(rows); n += len(rows)
                if stop: break
            print(f"{path}: front id {front}, trades so far {n:,}", flush=True)
    return n


def day_tape(mbo_path, out_dir, end_ct=None):
    """Header-less tape for one daily MBO file; days are joined with join_tapes().
    end_ct: optional 'YYYY-MM-DD HH:MM' Central cutoff (exclusive), e.g. to stop before a holdout session opens."""
    import os, re
    d = re.search(r"(\d{8})", os.path.basename(mbo_path)).group(1)
    out = os.path.join(out_dir, f"tape_{d}.csv.gz")
    tmp = out + ".tmp"
    end_ns = None
    if end_ct:
        end_ns = int(dt.datetime.strptime(end_ct, "%Y-%m-%d %H:%M").replace(tzinfo=CT).timestamp()) * 1_000_000_000
    build(tmp, [mbo_path], header=False, end_ns=end_ns)
    os.replace(tmp, out)
    return out


def join_tapes(out_path, day_files):
    """One single-member gzip (header + the day tapes in order): .NET's GZipStream reads only the first member."""
    import shutil
    with gzip.open(out_path, "wb", compresslevel=3) as o:
        o.write(HEADER.encode())
        for f in day_files:
            with gzip.open(f, "rb") as i: shutil.copyfileobj(i, o, 1 << 20)
    return out_path


if __name__ == "__main__":
    if sys.argv[1] == "--day":
        print(day_tape(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
    else:
        build(sys.argv[1], sys.argv[2:])
