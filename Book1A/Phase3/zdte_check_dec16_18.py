import re, sys
from pathlib import Path
import pandas as pd, databento as db
raw = Path(r"K:\Book1A_inputs\raw\block1")
RX = re.compile(r"^opt_(nq|q[1-5][a-d]|qn[1-5e])_(definition|statistics)$")
days = ["20251216", "20251217", "20251218"]
defs, stats = [], []
for d in sorted(raw.iterdir()):
    m = RX.match(d.name)
    if not m: continue
    for day in days:
        for f in sorted(d.glob(f"*/glbx-mdp3-{day}.{m.group(2)}.dbn.zst")):
            df = db.DBNStore.from_file(str(f)).to_df()
            if df.empty: continue
            df = df.reset_index(); df["file_day"] = day; df["root_dir"] = d.name
            (defs if m.group(2) == "definition" else stats).append(df)
D = pd.concat(defs, ignore_index=True)
D = D[D.asset.astype(str).str.match(r"^(NQ|Q[1-5][A-D]|QN[1-5E])$") & D.instrument_class.isin(["C", "P"])].copy()
D["exp"] = D.expiration.dt.tz_convert("America/New_York").dt.date
print("DEFINITION rows (NQ option roots, C/P) by file day, expiry, underlying, asset:")
g = D.groupby(["file_day", "exp", "underlying", "asset"]).size().reset_index(name="rows")
print(g[g.exp <= pd.Timestamp("2025-12-22").date()].to_string(index=False))
last = D.sort_values("ts_recv").drop_duplicates("raw_symbol", keep="last")
S = pd.concat(stats, ignore_index=True)
S = S[S.stat_type.isin([3, 9])].merge(last[["raw_symbol", "exp", "underlying"]], left_on="symbol", right_on="raw_symbol")
print("\nSTATISTICS rows (stat 9 open interest, stat 3 settlement) by file day, expiry, underlying:")
h = S.groupby(["file_day", "exp", "underlying", "stat_type"]).size().reset_index(name="rows")
print(h[h.exp <= pd.Timestamp("2025-12-22").date()].to_string(index=False))
