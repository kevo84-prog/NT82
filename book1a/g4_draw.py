r"""Phase 2 gate G4: the checker's reproduction sample (registered in Step A, Nov 6, 2026; run unchanged in Step B).

  python -m book1a.g4_draw --r1 <R1 ledger> --r2 <R2 ledger> --r3 <R3 ledger> --r4 <R4 ledger> --out <sample csv>

Inputs: the four Phase 2 full ledgers (book1a.ledger.LEDGER_COLUMNS; the draw reads only strategy, trade_id, date,
entry_time). It never reads a price, exit, P&L or R column, so no outcome can steer the sample.
Sample (Phase2_registration.md section 6, G4):
  FIXED_DAY  every R4 trade on Nov 6, Nov 12, Nov 19 and Dec 3, 2025 (however many there are, zero included);
  DRAW_R4    10 R4 trades from the other 17 sessions;
  DRAW_R1R3  10 trades from the R1, R2 and R3 ledgers pooled.
Both draws are always taken, whatever the trade counts on the fixed days.
v1.1 (Nov 8, 2026): --phase phase3 (default phase2, unchanged): fixed days Dec 10, Dec 18, 2025, Jan 14, Jan 29, 2026;
DRAW_R4 from the other 37 Phase 3 sessions; dates checked against Dec 5, 2025 - Feb 4, 2026. Same seed and method.
v1.2 (Nov 9, 2026): --phase phase4: fixed days Feb 11, Mar 4, Mar 17 and Apr 9, 2026 (registered in Phase4_registration.md
before any Phase 4 run); DRAW_R4 from the other 48 Phase 4 sessions; dates checked against Feb 5 - Apr 21, 2026.
Method: each pool is sorted by (strategy, date, entry_time, trade_id); one numpy Generator,
np.random.default_rng(20251205), draws DRAW_R4 first and DRAW_R1R3 second, each as the first k entries of
rng.permutation(len(pool)), k = min(10, len(pool)). A pool with fewer than 10 trades is taken whole and marked
SHORT_POOL. A duplicate (strategy, trade_id) in a ledger stops the draw.
Output: the sample csv (draw, order, strategy, trade_id, date, entry_time, pool_size, note) and <out>.manifest.json
(script sha256, input sha256, seed, numpy version, counts).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

VERSION = "g4-draw-v1.2"   # v1.2 (Nov 9, 2026): phase4 fixed days; phase2 / phase3 unchanged. v1.1 v1.1 (Nov 8, 2026): --phase (phase3 fixed days registered in Phase3_registration.md); phase2 unchanged
SEED = 20251205
K = 10
FIXED_DAYS = ("2025-11-06", "2025-11-12", "2025-11-19", "2025-12-03")
PHASE2_FIRST, PHASE2_LAST = "2025-11-05", "2025-12-04"
PHASES = {"phase2": dict(fixed_days=FIXED_DAYS, first=PHASE2_FIRST, last=PHASE2_LAST),
          "phase3": dict(fixed_days=("2025-12-10", "2025-12-18", "2026-01-14", "2026-01-29"), first="2025-12-05", last="2026-02-04"),
          "phase4": dict(fixed_days=("2026-02-11", "2026-03-04", "2026-03-17", "2026-04-09"), first="2026-02-05", last="2026-04-21")}
KEYS = ("strategy", "trade_id", "date", "entry_time")
COLUMNS = ["draw", "order", "strategy", "trade_id", "date", "entry_time", "pool_size", "note"]


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_keys(path: Path, strategy: str, phase: str = "phase2") -> list:
    """The key columns of one ledger. The strategy column must start with the expected name (R1 .. R4)."""
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        r = csv.DictReader(fh)
        miss = [k for k in KEYS if k not in (r.fieldnames or [])]
        if miss:
            raise SystemExit(f"{path}: missing columns {miss}")
        for x in r:
            k = {c: x[c] for c in KEYS}
            if not k["strategy"].startswith(strategy):
                raise SystemExit(f"{path}: strategy {k['strategy']!r} is not {strategy}")
            if not PHASES[phase]["first"] <= k["date"] <= PHASES[phase]["last"]:
                raise SystemExit(f"{path}: date {k['date']} outside {phase}")
            rows.append(k)
    seen = set()
    for k in rows:
        if (k["strategy"], k["trade_id"]) in seen:
            raise SystemExit(f"{path}: duplicate trade {k['strategy']} {k['trade_id']}")
        seen.add((k["strategy"], k["trade_id"]))
    return rows


def order(pool: list) -> list:
    return sorted(pool, key=lambda k: (k["strategy"], k["date"], k["entry_time"], k["trade_id"]))


def draw(r1: list, r2: list, r3: list, r4: list, seed: int = SEED, k: int = K, fixed_days=FIXED_DAYS) -> list:
    out = []
    fixed = order([x for x in r4 if x["date"] in fixed_days])
    for i, x in enumerate(fixed, 1):
        out.append(dict(draw="FIXED_DAY", order=i, **x, pool_size=len(fixed), note=""))
    rng = np.random.default_rng(seed)
    for name, pool in (("DRAW_R4", order([x for x in r4 if x["date"] not in fixed_days])), ("DRAW_R1R3", order(r1 + r2 + r3))):
        n = min(k, len(pool))
        idx = rng.permutation(len(pool))[:n] if len(pool) else []
        note = "SHORT_POOL" if len(pool) < k else ""
        for i, j in enumerate(idx, 1):
            out.append(dict(draw=name, order=i, **pool[int(j)], pool_size=len(pool), note=note))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    for s in ("r1", "r2", "r3", "r4"):
        ap.add_argument(f"--{s}", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--phase", default="phase2", choices=sorted(PHASES))
    a = ap.parse_args(argv)
    fixed_days = PHASES[a.phase]["fixed_days"]
    paths = {s: Path(getattr(a, s.lower())) for s in ("R1", "R2", "R3", "R4")}
    led = {s: read_keys(p, s, a.phase) for s, p in paths.items()}
    rows = draw(led["R1"], led["R2"], led["R3"], led["R4"], fixed_days=fixed_days)
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    counts = {d: sum(1 for r in rows if r["draw"] == d) for d in ("FIXED_DAY", "DRAW_R4", "DRAW_R1R3")}
    man = dict(version=VERSION, phase=a.phase, script_sha256=sha(Path(__file__)), seed=SEED, k=K, fixed_days=list(fixed_days),
               numpy_version=np.__version__, inputs={s: dict(path=str(p), sha256=sha(p)) for s, p in paths.items()},
               sample=str(out), sample_sha256=sha(out), counts=counts, generated=dt.datetime.now().isoformat(timespec="seconds"))
    Path(str(out) + ".manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"sample written: {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
