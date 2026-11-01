"""Phase 3 inputs: 1-minute bars (NQ HTF composite, ES) and the A0 / RT0 configs.

Bars: block_inputs.bars_csv from raw\\block1\\nq_ohlcv_1m / es_ohlcv_1m with the 2025 roll-fix files (NQH6 / ESH6 on
UTC Dec 14-16), from Jul 20, 2025 (as Phase 2) to UTC Feb 4, 2026, then cut at Feb 4, 2026 17:00 CT, the same cut as
the Feb 4 tape: nothing of the Feb 5 session (Phase 4) is kept. Check: on the overlap with Phase 2's files (through
Dec 4, 2025 17:00 CT) every row must be identical.
Configs: Phase 2's config with Phase 3 sessions (41), dates, fill model v3.5, out dirs. One --instrument label is
used for the whole phase (the harness only uses the name as a label; the contract on each day comes from the tapes
and bar files). RT0 = A0 + RetriggerBars=0.
Run from the project folder:  python backtest\\phase3\\build_inputs.py
"""
import datetime as dt, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from jeron_engine import block_inputs  # noqa: E402

P2, P3 = ROOT / "backtest" / "phase2", ROOT / "backtest" / "phase3"
CUT = "2026-02-04 17:00:00"
HOLIDAYS = {"2025-12-25", "2026-01-01", "2026-01-19"}


def sessions():
    d, out = dt.date(2025, 12, 5), []
    while d <= dt.date(2026, 2, 4):
        if d.weekday() < 5 and d.isoformat() not in HOLIDAYS: out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def bars(sym):
    out = P3 / f"{sym}_1m.csv"
    block_inputs.bars_csv(out, f"raw/block1/{sym}_ohlcv_1m/*/*.ohlcv-1m.dbn.zst",
                          f"raw/block1/roll_{sym.upper()}*_ohlcv_1m_2025*/*/*.ohlcv-1m.dbn.zst", "20250720", "20260204")
    lines = open(out).read().splitlines()
    kept = [lines[0]] + [l for l in lines[1:] if l[:19] <= CUT]
    open(out, "w", newline="").write("\n".join(kept) + "\n")
    old = open(P2 / f"{sym}_1m.csv").read().splitlines()
    old = old[:1] + [l for l in old[1:] if l[:19] <= "2025-12-04 17:00:00"]
    same = kept[:len(old)] == old
    print(f"{sym}_1m.csv: {len(kept) - 1} bars, {kept[1][:19]} to {kept[-1][:19]}; "
          f"first {len(old) - 1} rows identical to Phase 2: {same}")
    if not same or kept[-1][:19] > CUT: raise SystemExit("bar check failed")


def main():
    s = sessions()
    assert len(s) == 41, len(s)
    for sym in ("nq", "es"): bars(sym)
    cfg = json.load(open(P2 / "phase2_config.json"))
    cfg.update(sessions=s, nq_1m=str(P3 / "nq_1m.csv"), es_1m=str(P3 / "es_1m.csv"), out_dir=str(P3 / "run"),
               strategy_first_utc="20251203", strategy_from="2025-12-03 17:00", last_utc="20260204",
               to="2026-02-04 16:15", instrument="NQ MAR26", fill_model="v3.5",
               map_settings=["EsInstrument=ES MAR26"], strategy_settings=["EsInstrument=ES MAR26"])
    json.dump(cfg, open(P3 / "phase3_config.json", "w"), indent=1)
    rt0 = dict(cfg, out_dir=str(P3 / "run_RT0"), strategy_settings=cfg["strategy_settings"] + ["RetriggerBars=0"])
    json.dump(rt0, open(P3 / "phase3_config_RT0.json", "w"), indent=1)
    print(f"configs written: {len(s)} sessions, {s[0]} to {s[-1]}")


if __name__ == "__main__":
    main()
