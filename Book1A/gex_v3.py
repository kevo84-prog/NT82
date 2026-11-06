r"""Phase 1b GEX diagnostics that need per-strike gamma: V3 second flip, volatility control, pc_gamma_ratio, pin_zone.

  python -m book1a.gex_v3 --inputs K:\Book1A_inputs --sessions 2025-10-22 ... --out <folder>

Code used through K:\Book1A_inputs only (checker copies, Nov 6, 2026; never their main()):
  gex_calc.py   sha256 7c8107b0eca57990e2ae9f753d9de2cbcc6eb72c7a05ab2d9e49c14182a9232b  (cme_day, smile_iv, R)
  mq_levels.py  sha256 d94b18f25d49e12bb2b9f8d3c023a1837ca877442ace76cc30fbf59e35f566e4  (strike_gex, compute_levels)
Data: K:\Book1A_inputs\raw\block1\opt_<root>_definition|statistics (CME NQ options; roots NQ, Q1A-Q5D, QN1-QNE, the
gex_calc asset filter) and the frozen gex_levels_block1.csv (front contract, front settlement, nt_shift_pts).

Per session s with report date D (= gex_levels_block1.csv report_date):
  open interest  stat_type 9, the latest per option published (ts_recv) at or before D 23:00 ET, ts_ref >= D - 4 days
                 (gex_calc.cme_day, unchanged);
  settlements    stat_type 3 with ts_ref on D, latest revision received at or before D 23:00 ET (this loader cuts
                 the files at the same 23:00 ET cutoff, so nothing published later can enter);
  definitions    the definition files of D - 6 .. D (last record per symbol);
  chain          gex_calc.cme_day(D, s, defs, oi, st, fut) with fut = the frozen front settlement on D;
  check          mq_levels.compute_levels(chain, settle, front, s) must equal the frozen gex_levels_block1.csv row
                 (every level, net_gex, regime, options_used): proves this loader gives the frozen method's chain.
Outputs (all available at D 23:00 ET, before the 08:10 CT map of s):
  flip_v3        zero crossing of the cumulative net GEX per strike (front contract, all expiries, strikes sorted
                 ascending, cumulated from the lowest strike), linear between the two strikes around the sign change;
                 when it changes sign more than once, the crossing nearest the front settlement (ours).
  regime_agree   Y when the front settlement is on the same side of flip_v3 as of HVL (ours), else N.
  pc_gamma_ratio |sum of put GEX| / |sum of call GEX| over the same front chain (value only; no rule uses it).
  pin_strike     the 0DTE strike (front contract, options expiring on s, the frozen 0DTE set) with the largest
                 open interest, calls + puts; ties: the strike nearest the settlement (ours).
  atm_iv         IV at the forward (log-moneyness 0) from gex_calc.smile_iv of the front contract's nearest expiry
                 after s (the 0DTE expiry excluded; ours), with its expiry and days to expiry.
Chart contract: levels are shifted by nt_shift_pts (gex_levels_block1.csv), as the *_nt columns.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

VERSION = "gex-v3-v1.0"
CODE_SHA = {"gex_calc.py": "7c8107b0eca57990e2ae9f753d9de2cbcc6eb72c7a05ab2d9e49c14182a9232b",
            "mq_levels.py": "d94b18f25d49e12bb2b9f8d3c023a1837ca877442ace76cc30fbf59e35f566e4"}
ROOT_RE = re.compile(r"^opt_(nq|q[1-5][a-d]|qn[1-5e])_(definition|statistics)$")
REPRO = ["call_resistance", "put_support", "hvl", "call_resistance_0dte", "put_support_0dte", "hvl_0dte", "net_gex", "regime",
         "options_used"]


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def import_code(inputs: Path):
    for name, h in CODE_SHA.items():
        if sha(inputs / name) != h:
            raise RuntimeError(f"{name}: sha256 differs from the checker copy")
    if str(inputs) not in sys.path:
        sys.path.insert(0, str(inputs))
    import gex_calc as GC
    import mq_levels as MQ
    return GC, MQ


def day_files(raw: Path, kind: str, days) -> list:
    out = []
    for d in sorted(raw.iterdir()):
        m = ROOT_RE.match(d.name)
        if not m or m.group(2) != kind:
            continue
        for day in days:
            out += sorted(d.glob(f"*/glbx-mdp3-{day:%Y%m%d}.{kind}.dbn.zst"))
    return out


def read(files, kind):
    import databento as db
    parts = []
    for f in files:
        df = db.DBNStore.from_file(str(f)).to_df()
        if df.empty:
            continue
        if kind == "statistics":
            df = df[df.stat_type.isin([3, 9])]
            df = df.reset_index()[["ts_recv", "ts_ref", "price", "quantity", "stat_type", "symbol"]]
        else:
            df = df.reset_index()[["ts_recv", "raw_symbol", "instrument_class", "strike_price", "expiration", "underlying", "asset"]]
        parts.append(df)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def build_session(GC, MQ, raw: Path, row: dict):
    s = dt.date.fromisoformat(row["session"]); D = dt.date.fromisoformat(row["report_date"])
    cutoff = pd.Timestamp(dt.datetime.combine(D, dt.time(23, 0)), tz="America/New_York").tz_convert("UTC")
    dfiles = day_files(raw, "definition", [D - dt.timedelta(days=k) for k in range(6, -1, -1)])
    sfiles = day_files(raw, "statistics", [D - dt.timedelta(days=k) for k in range(5, -2, -1)])   # D-5 .. D+1 (UTC files)
    d = read(dfiles, "definition")
    d = d[d.asset.astype(str).str.match(r"^(NQ|Q[1-5][A-D]|QN[1-5E])$") & d.instrument_class.isin(["C", "P"])]
    d = d.sort_values("ts_recv").drop_duplicates("raw_symbol", keep="last")
    d = d.rename(columns={"raw_symbol": "symbol", "instrument_class": "cp", "strike_price": "strike"})
    d["exp"] = d.expiration.dt.tz_convert("America/New_York").dt.date
    d = d[["symbol", "cp", "strike", "exp", "underlying"]]
    st_all = read(sfiles, "statistics")
    st_all = st_all[st_all.ts_recv <= cutoff]                     # nothing published after D 23:00 ET
    oi = st_all[st_all.stat_type == 9][["ts_recv", "ts_ref", "quantity", "symbol"]].rename(columns={"quantity": "oi"})
    st = st_all[st_all.stat_type == 3][["ts_recv", "ts_ref", "price", "symbol"]].copy()
    st["date"] = st.ts_ref.dt.date
    st_used = st[st.date == D]
    st = st.sort_values("ts_recv").groupby(["date", "symbol"], as_index=False).price.last()
    front, settle = row["front"], float(row["settle"])
    fut = pd.DataFrame(dict(date=[D], symbol=[front], price=[settle]))
    chain = GC.cme_day(D, s, d, oi, st, fut)
    lv = MQ.compute_levels(chain, settle, front, s) if chain is not None else None
    meta = dict(session=row["session"], report_date=row["report_date"], cutoff_utc=cutoff.isoformat(),
                oi_max_ts_recv=str(oi.ts_recv.max()) if len(oi) else "", settle_max_ts_recv=str(st_used.ts_recv.max()) if len(st_used) else "",
                definition_files=[str(f) for f in dfiles], statistics_files=[str(f) for f in sfiles])
    return chain, lv, meta


def flip_cross(p: pd.Series, S: float):
    cs = p.cumsum()
    k, v = cs.index.to_numpy(float), cs.to_numpy(float)
    sg = np.sign(v)
    idx = np.where(sg[:-1] * sg[1:] < 0)[0]
    if len(idx) == 0:
        return np.nan, 0
    xs = [k[i] - v[i] * (k[i + 1] - k[i]) / (v[i + 1] - v[i]) for i in idx]
    return float(min(xs, key=lambda x: abs(x - S))), len(xs)


def derive(GC, MQ, chain, row, s: dt.date):
    front, S = row["front"], float(row["settle"])
    ch = chain[chain.underlying == front]
    p = MQ.strike_gex(ch, S)
    flip, n_cross = flip_cross(p, S)
    hvl = float(row["hvl"]) if row.get("hvl") else np.nan
    side = lambda x: "ABOVE" if S > x else ("BELOW" if S < x else "AT")
    agree = "Y" if np.isfinite(flip) and np.isfinite(hvl) and side(flip) == side(hvl) else ("N" if np.isfinite(flip) else "NOT_APPLICABLE")
    # put / call gamma ratio on the same chain
    c = ch[(ch.oi > 0) & np.isfinite(ch.iv) & (ch["T"] > 0)]
    g = MQ._gamma(S, c.strike.values, c["T"].values, c.iv.values) * c.oi.values * 20.0 * S * S * 0.01
    call, put = float(g[c.cp.values == "C"].sum()), float(g[c.cp.values == "P"].sum())
    ratio = abs(put) / abs(call) if call else np.nan
    # 0DTE pin strike (largest OI)
    z = ch[(ch.exp == s) & (ch.oi > 0)]
    if len(z):
        oi_k = z.groupby("strike").oi.sum()
        top = oi_k[oi_k == oi_k.max()]
        pin = float(min(top.index, key=lambda k: abs(k - S))); pin_oi = int(oi_k.max())
    else:
        pin, pin_oi = np.nan, 0
    # ATM IV: nearest expiry after s
    later = sorted(e for e in ch.exp.unique() if e > s)
    atm, e_used, dte = np.nan, "", ""
    for e in later:
        ge = ch[ch.exp == e].copy()
        T = float(ge["T"].iloc[0])
        iv = GC.smile_iv(pd.concat([ge, pd.DataFrame(dict(symbol=["ATM"], cp=["C"], strike=[S], exp=[e], price=[0.0], T=[T]))], ignore_index=True),
                         {e: S}, {e: T}, "price")
        if np.isfinite(iv[-1]):
            atm, e_used, dte = float(iv[-1]), e.isoformat(), (e - dt.date.fromisoformat(row["report_date"])).days
            break
    shift = float(row.get("nt_shift_pts") or 0)
    return dict(flip_v3=flip, flip_v3_nt=flip + shift if np.isfinite(flip) else np.nan, flip_v3_crossings=n_cross,
                hvl=hvl, hvl_nt=hvl + shift if np.isfinite(hvl) else np.nan, regime_agree=agree,
                flip_v3_minus_hvl_pts=flip - hvl if np.isfinite(flip) and np.isfinite(hvl) else np.nan,
                pc_gamma_ratio=ratio, pin_strike_0dte=pin, pin_strike_0dte_nt=pin + shift if np.isfinite(pin) else np.nan,
                pin_strike_oi=pin_oi, n_0dte_options=int(len(z)), atm_iv=atm, atm_iv_expiry=e_used, atm_iv_dte_from_report=dte,
                n_front_options=int(len(ch)))


def run(inputs: Path, sessions, out: Path):
    GC, MQ = import_code(inputs)
    out.mkdir(parents=True, exist_ok=True)
    raw = inputs / "raw" / "block1"
    rows = {r["session"]: r for r in csv.DictReader(open(inputs / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
    res, files = [], {}
    for s in sessions:
        row = rows[s]
        chain, lv, meta = build_session(GC, MQ, raw, row)
        rep = {}
        for k in REPRO:
            a, b = (lv or {}).get(k), row.get(k)
            if k in ("regime",):
                rep[k] = a == b
            elif k == "options_used":
                rep[k] = a is not None and str(int(a)) == str(b)
            else:
                rep[k] = a is not None and b not in (None, "") and abs(float(a) - float(b)) <= max(1e-6, 1e-9 * abs(float(b)))
        x = derive(GC, MQ, chain, row, dt.date.fromisoformat(s)) if chain is not None else {}
        res.append(dict(session=s, report_date=row["report_date"], available_at=f"{row['report_date']} 23:00 ET", front=row["front"],
                        settle=row["settle"], repro_all_match="Y" if all(rep.values()) else "N",
                        repro_mismatch=",".join(k for k, v in rep.items() if not v), oi_max_ts_recv=meta["oi_max_ts_recv"],
                        settle_max_ts_recv=meta["settle_max_ts_recv"], cutoff_utc=meta["cutoff_utc"], **x))
        for f in meta["definition_files"] + meta["statistics_files"]:
            files.setdefault(f, None)
    for f in files:
        files[f] = sha(Path(f))
    with open(out / "gex_v3_input_files.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["file", "sha256"]); w.writerows(sorted(files.items()))
    (out / "gex_v3_manifest.json").write_text(json.dumps(dict(version=VERSION, code_sha256=CODE_SHA, n_input_files=len(files)), indent=1))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True); ap.add_argument("--sessions", nargs="+", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = run(Path(a.inputs), a.sessions, Path(a.out))
    pd.DataFrame(res).to_csv(Path(a.out) / "gex_v3_sessions.csv", index=False)
    print(pd.DataFrame(res)[["session", "repro_all_match", "repro_mismatch", "oi_max_ts_recv", "settle_max_ts_recv"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
