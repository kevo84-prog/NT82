"""Phase 4 holdout inputs (Feb 5 - Apr 21, 2026, 52 sessions). Run only after FROZEN_STRATEGY.md's Phase 4 decision
rule is committed (tag phase4-holdout).

1. Tapes, UTC days Feb 4 - Apr 21, 2026, from raw\\block1\\nq_mbo_20251021_20260421; UTC Mar 15-17 from
   raw\\block1\\nq_roll_NQM6_mbo_20260315_20260317 (NinjaTrader is on NQ Jun 26 from the Mar 16 session, which opens
   Sunday Mar 15 17:00 CT). Feb 4 is rebuilt in full (the Phase 3 tape was cut at 17:00 CT; that cut file is kept in
   tapes\\phase3_cut\\). Block 2 guard: Apr 21 is cut at 17:00 CT, so nothing of the Apr 22 session is used; no file
   dated Apr 22, 2026 or later is opened.
2. 1-minute bars (NQ HTF composite, ES) from Jul 20, 2025 to Apr 21, 2026 17:00 CT, with the 2025 and 2026 roll files;
   identical to the Phase 3 files on their overlap (checked).
3. Config: Phase 3's with the 52 sessions, warm-up = the Feb 4 session, fill model v3.5.
Run from the project folder:  python backtest\\phase4\\build_inputs.py [workers]
"""
import datetime as dt, glob, json, os, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
P3, P4 = ROOT / "backtest" / "phase3", ROOT / "backtest" / "phase4"
FIRST, LAST = dt.date(2026, 2, 4), dt.date(2026, 4, 21)
BLOCK2_FIRST = dt.date(2026, 4, 22)
ROLL_DAYS = {dt.date(2026, 3, 15), dt.date(2026, 3, 16), dt.date(2026, 3, 17)}
CUTOFF = {dt.date(2026, 4, 21): "2026-04-21 17:00"}
BAR_CUT = "2026-04-21 17:00:00"
HOLIDAYS = {"2026-02-16", "2026-04-03"}
CONT = glob.glob(str(ROOT / "raw" / "block1" / "nq_mbo_20251021_20260421" / "*" / "glbx-mdp3-*.mbo.dbn.zst"))
ROLL = glob.glob(str(ROOT / "raw" / "block1" / "nq_roll_NQM6_mbo_20260315_20260317" / "*" / "glbx-mdp3-*.mbo.dbn.zst"))
TAPES = ROOT / "tapes"


def sessions():
    d, out = dt.date(2026, 2, 5), []
    while d <= LAST:
        if d.weekday() < 5 and d.isoformat() not in HOLIDAYS: out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def file_for(d):
    tag = d.strftime("%Y%m%d")
    hits = [f for f in (ROLL if d in ROLL_DAYS else CONT) if f"glbx-mdp3-{tag}." in os.path.basename(f)]
    return hits[0] if hits else None


def one(d):
    from jeron_engine import mbo_tape
    assert d < BLOCK2_FIRST
    return d, mbo_tape.day_tape(file_for(d), str(TAPES), CUTOFF.get(d))


def tapes(workers):
    feb4 = TAPES / "tape_20260204.csv.gz"
    keep = TAPES / "phase3_cut" / "tape_20260204.csv.gz"
    if feb4.exists() and not keep.exists():
        keep.parent.mkdir(exist_ok=True); shutil.move(str(feb4), str(keep))
    days, d = [], FIRST
    while d <= LAST:
        if file_for(d) and not (TAPES / f"tape_{d:%Y%m%d}.csv.gz").exists(): days.append(d)
        elif not file_for(d) and d.weekday() != 5: print(f"no MBO file for {d}", flush=True)
        d += dt.timedelta(days=1)
    print(f"building {len(days)} tapes", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for fu in as_completed([ex.submit(one, x) for x in days]): print("done", fu.result()[0], flush=True)


def bars(sym):
    from jeron_engine import block_inputs
    out = P4 / f"{sym}_1m.csv"
    block_inputs.bars_csv(out, f"raw/block1/{sym}_ohlcv_1m/*/*.ohlcv-1m.dbn.zst",
                          f"raw/block1/roll_{sym.upper()}*_ohlcv_1m_202*/*/*.ohlcv-1m.dbn.zst", "20250720", "20260421")
    lines = open(out).read().splitlines()
    kept = [lines[0]] + [l for l in lines[1:] if l[:19] <= BAR_CUT]
    open(out, "w", newline="").write("\n".join(kept) + "\n")
    old = open(P3 / f"{sym}_1m.csv").read().splitlines()
    old = old[:1] + [l for l in old[1:] if l[:19] <= "2026-02-04 16:00:00"]
    same = kept[:len(old)] == old
    print(f"{sym}_1m.csv: {len(kept) - 1} bars to {kept[-1][:19]}; identical to Phase 3 on the overlap: {same}", flush=True)
    if not same or kept[-1][:19] > BAR_CUT: raise SystemExit("bar check failed")


def main():
    P4.mkdir(exist_ok=True)
    s = sessions(); assert len(s) == 52, len(s)
    tapes(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
    for sym in ("nq", "es"): bars(sym)
    cfg = json.load(open(P3 / "phase3_config.json"))
    cfg.update(sessions=s, nq_1m=str(P4 / "nq_1m.csv"), es_1m=str(P4 / "es_1m.csv"), out_dir=str(P4 / "run"),
               strategy_first_utc="20260203", strategy_from="2026-02-03 17:00", last_utc="20260421",
               to="2026-04-21 16:15", instrument="NQ JUN26", fill_model="v3.5",
               map_settings=["EsInstrument=ES JUN26"], strategy_settings=["EsInstrument=ES JUN26"])
    json.dump(cfg, open(P4 / "phase4_config.json", "w"), indent=1)
    print(f"config: {len(s)} sessions {s[0]} .. {s[-1]}", flush=True)


if __name__ == "__main__":
    main()
