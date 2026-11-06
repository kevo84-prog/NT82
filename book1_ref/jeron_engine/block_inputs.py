"""Block inputs for the daily loop (JE 0.3, Oct 25 2026).

bars_csv(...)       Databento ohlcv-1m (continuous NQ.v.0 / ES.v.0) -> 1-minute bars csv for the harness
                    (time_end_local = bar start + 1 minute, Central). UTC days that have a roll-fix file
                    (roll_<SYM>_ohlcv_1m_*) are taken from it, so every bar is on NinjaTrader's contract.
trades_day_tape()   Databento trades schema (lookback, no book) -> header-less day tape. The quote is not in the
                    trades schema, so bid/ask are set from the CME aggressor flag (buy: ask = price, bid = price -
                    1 tick; sell: the mirror). Only used for map history and the warm-up evening (flagged).
"""
import gzip, re, os
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

CT = ZoneInfo("America/Chicago")
TICK = 0.25


def _utc_day(path):
    return re.search(r"(\d{8})", Path(path).name).group(1)


def bars_csv(out_csv, cont_glob, roll_glob=None, first=None, last=None):
    import databento as db
    files = {}
    for f in sorted(Path("/").glob(cont_glob.lstrip("/"))) if cont_glob.startswith("/") else sorted(Path(".").glob(cont_glob)):
        files[_utc_day(f)] = f
    if roll_glob:
        for f in (sorted(Path("/").glob(roll_glob.lstrip("/"))) if roll_glob.startswith("/") else sorted(Path(".").glob(roll_glob))):
            files[_utc_day(f)] = f      # roll fix wins
    frames = []
    for d in sorted(files):
        if (first and d < first) or (last and d > last): continue
        df = db.DBNStore.from_file(str(files[d])).to_df(price_type="float", pretty_ts=True, map_symbols=False)
        if len(df): frames.append(df)
    df = pd.concat(frames).sort_index()
    end = (df.index + pd.Timedelta(minutes=1)).tz_convert(CT).tz_localize(None)
    with open(out_csv, "w", newline="") as o:
        o.write("time_end_local,open,high,low,close,volume\n")
        for t, r in zip(end, df.itertuples()):
            o.write(f"{t:%Y-%m-%d %H:%M:%S},{r.open},{r.high},{r.low},{r.close},{r.volume}\n")
    return out_csv, len(df)


def trades_day_tape(trades_path, out_dir):
    import databento as db
    d = _utc_day(trades_path)
    out = Path(out_dir) / f"tape_{d}.csv.gz"
    df = db.DBNStore.from_file(str(trades_path)).to_df(price_type="float", pretty_ts=True, map_symbols=False)
    if len(df):
        front = df["instrument_id"].mode().iloc[0]
        df = df[df["instrument_id"] == front]
    with gzip.open(str(out) + ".tmp", "wt") as o:
        for t, r in zip(df["ts_event"].dt.tz_convert(CT), df.itertuples()):
            p = r.price
            if r.side == "B": b, a, ag = p - TICK, p, "B"
            elif r.side == "A": b, a, ag = p, p + TICK, "S"
            else: b, a, ag = p - TICK, p + TICK, "U"
            ns = t.nanosecond
            o.write(f"{t:%Y-%m-%d %H:%M:%S}.{t.microsecond:06d}{ns // 100:01d},{p:.2f},{b:.2f},{a:.2f},{r.size},{ag}\n")
    os.replace(str(out) + ".tmp", out)
    return out, len(df)
