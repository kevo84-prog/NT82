"""P0.6 hand check on the PC: 08:10 CT VWAP on 2 normal days and both roll days.

  python -m book1a.hand_checks.vwap_hand_check <raw_block1_dir> <out_dir> [--days 2025-10-22 2025-11-05 2025-12-15 2026-03-16]

For every day it (1) decodes the MBO trade messages of the front contract with the databento package
(independently of Book 1's tape builder), (2) does a plain pandas "hand" calculation of
sum(p*v)/sum(v) and the volume-weighted sigma over the session window (17:00 CT previous day to
08:10:00 CT, strict) and the weekly window (Sunday 17:00 CT), and (3) runs book1a.vwap on the same
trades. It writes <out_dir>/vwap_hand_check.md with both numbers side by side and PASS when the
module matches the hand calculation to 1e-6 and the trade counts are equal.

Roll days (Dec 15, 2025 and Mar 16, 2026): the new contract's roll file (nq_roll_* for Dec 14-16 /
Mar 15-17) is the input, so both VWAPs restart on the new contract at its first session (U1).
File discovery: the day's MBO file is the one whose name contains the UTC date of the session and of
the previous day (the overnight starts 17:00 CT = 22:00/23:00 UTC the day before). Pass --files to
override: --files 2025-10-22=path1,path2 ...
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
DEFAULT_DAYS = ["2025-10-22", "2025-11-05", "2025-12-15", "2026-03-16"]


def find_files(raw: Path, d: date) -> list:
    """MBO files covering the overnight (previous UTC day) and the session day; roll files first."""
    tags = [(d - timedelta(days=1)).strftime("%Y%m%d"), d.strftime("%Y%m%d")]
    out = []
    for tag in tags:
        roll = sorted(raw.rglob(f"*roll*{tag}*.dbn*")) + sorted(raw.rglob(f"*{tag}*roll*.dbn*"))
        cont = [p for p in sorted(raw.rglob(f"*{tag}*.mbo.dbn*")) if "roll" not in p.name.lower()]
        out += roll or cont
    return out


def load_trades(files: list):
    import databento as db
    import pandas as pd
    frames = []
    for f in files:
        store = db.DBNStore.from_file(f)
        df = store.to_df(price_type="float", pretty_ts=False, map_symbols=False)
        df = df[(df["action"] == "T") & (df["size"] > 0) & ((df["flags"] & 32) == 0)]       # trades, not snapshots
        frames.append(df[["ts_event", "instrument_id", "price", "size"]])
    t = pd.concat(frames, ignore_index=True)
    front = int(t["instrument_id"].mode().iloc[0])
    t = t[t["instrument_id"] == front]
    return t.sort_values("ts_event", kind="stable").reset_index(drop=True), front


def hand(t, start: datetime, end: datetime):
    import pandas as pd
    lo = int(start.timestamp()) * 10**9
    hi = int(end.timestamp()) * 10**9
    w = t[(t["ts_event"].astype("int64") >= lo) & (t["ts_event"].astype("int64") < hi)]
    v = float(w["size"].sum())
    if v == 0:
        return None, None, 0, 0
    vwap = float((w["price"] * w["size"]).sum() / v)
    sd = math.sqrt(float((w["size"] * (w["price"] - vwap) ** 2).sum() / v))
    return vwap, sd, len(w), int(v)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("raw"); ap.add_argument("out")
    ap.add_argument("--days", nargs="*", default=DEFAULT_DAYS)
    ap.add_argument("--files", nargs="*", default=[])
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from book1a import vwap as V
    override = {k: v.split(",") for k, v in (x.split("=", 1) for x in a.files)}
    raw, out = Path(a.raw), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    lines = ["# P0.6 hand check: 08:10 CT VWAP", "", f"generated {datetime.now(CT).isoformat(timespec='seconds')}", "",
             "| day | scope | window start CT | files | front id | trades hand | trades module | vwap hand | vwap module | sd hand | sd module | result |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    all_ok = True
    for ds in a.days:
        d = date.fromisoformat(ds)
        files = [Path(p) for p in override.get(ds, [])] or find_files(raw, d)
        if not files:
            lines.append(f"| {ds} | - | - | NO FILES FOUND | | | | | | | | FAIL |"); all_ok = False; continue
        t, front = load_trades(files)
        ts = t["ts_event"].astype("int64").to_numpy()
        res = V.vwap_0810(ts, t["price"].to_numpy(), t["size"].to_numpy(), d)
        for scope, start in (("SESSION", V.session_start(d)), ("WEEKLY", V.week_start(d))):
            hv, hs, hn, hvol = hand(t, start, V.as_of(d))
            r = res[scope]
            ok = (hn == r.n_trades) and (hv is None and r.vwap is None or (hv is not None and r.vwap is not None
                  and abs(hv - r.vwap) < 1e-6 and abs(hs - r.sd) < 1e-6))
            all_ok &= ok
            lines.append(f"| {ds} | {scope} | {start.isoformat()} | {', '.join(f.name for f in files)} | {front} | {hn} | {r.n_trades} | "
                         f"{'' if hv is None else f'{hv:.6f}'} | {'' if r.vwap is None else f'{r.vwap:.6f}'} | "
                         f"{'' if hs is None else f'{hs:.6f}'} | {'' if r.sd is None else f'{r.sd:.6f}'} | {'PASS' if ok else 'FAIL'} |")
    lines += ["", f"**Overall: {'PASS' if all_ok else 'FAIL'}**", "",
              "Hand calculation: pandas sum(price x size) / sum(size) and sqrt(sum(size x (price - vwap)^2) / sum(size)) over trade",
              "messages (action T, size > 0, not snapshot) of the front contract, ts_event in [window start, 08:10:00 CT)."]
    (out / "vwap_hand_check.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-4:]))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
