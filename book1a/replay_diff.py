"""Book 1A deterministic replay diff (checklist P0.3).

Usage:
  python -m book1a.replay_diff <run_a_dir> <run_b_dir> <report.md> [--ignore COL ...]

Compares every CSV / JSON / Parquet file present in both run folders, row for row and value for
value (float values must be bit-identical, not just close). Columns given with --ignore (for example
run_id, wall-clock timestamps) are dropped before the comparison. The report lists every differing
file with the first differing rows; it must be empty for P0.3 to pass.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

VERSION = "replay-diff-v1.0"


def _rows(path: Path, ignore: List[str]) -> Tuple[List[str], List[list]]:
    if path.suffix.lower() == ".csv":
        with open(path, newline="") as f:
            r = csv.reader(f)
            header = next(r, [])
            keep = [i for i, h in enumerate(header) if h not in ignore]
            return [header[i] for i in keep], [[row[i] if i < len(row) else "" for i in keep] for row in r]
    if path.suffix.lower() == ".json":
        txt = json.load(open(path))
        for k in ignore:
            if isinstance(txt, dict):
                txt.pop(k, None)
        return ["json"], [[json.dumps(txt, sort_keys=True)]]
    if path.suffix.lower() == ".parquet":
        import pandas as pd
        df = pd.read_parquet(path).drop(columns=[c for c in ignore if c in pd.read_parquet(path).columns])
        return list(df.columns), [[repr(v) for v in row] for row in df.itertuples(index=False, name=None)]
    return ["bytes"], [[open(path, "rb").read().hex()]]


def diff_runs(a: Path, b: Path, ignore: Optional[List[str]] = None) -> Dict[str, dict]:
    ignore = ignore or []
    fa = {p.relative_to(a).as_posix(): p for p in a.rglob("*") if p.is_file()}
    fb = {p.relative_to(b).as_posix(): p for p in b.rglob("*") if p.is_file()}
    out: Dict[str, dict] = {}
    for name in sorted(set(fa) | set(fb)):
        if name not in fa or name not in fb:
            out[name] = {"status": "ONLY_IN_" + ("B" if name not in fa else "A")}
            continue
        ha, ra = _rows(fa[name], ignore)
        hb, rb = _rows(fb[name], ignore)
        if ha != hb:
            out[name] = {"status": "HEADER_DIFF", "a": ha, "b": hb}
            continue
        if len(ra) != len(rb):
            out[name] = {"status": "ROW_COUNT_DIFF", "a": len(ra), "b": len(rb)}
            continue
        first = []
        for i, (x, y) in enumerate(zip(ra, rb)):
            if x != y:
                cols = [ha[j] for j in range(len(x)) if x[j] != y[j]]
                first.append({"row": i, "columns": cols, "a": [x[j] for j in range(len(x)) if x[j] != y[j]],
                              "b": [y[j] for j in range(len(y)) if x[j] != y[j]]})
                if len(first) >= 5:
                    break
        if first:
            out[name] = {"status": "VALUE_DIFF", "first": first}
    return out


def write_report(result: Dict[str, dict], path: Path, a: Path, b: Path, n_files: int) -> None:
    with open(path, "w") as f:
        f.write(f"# P0.3 deterministic replay diff\n\nrun A: {a}\nrun B: {b}\nfiles compared: {n_files}\n\n")
        if not result:
            f.write("**DIFF EMPTY: PASS** (every file identical row for row)\n")
            return
        f.write(f"**{len(result)} differing file(s): FAIL**\n\n")
        for name, d in result.items():
            f.write(f"## {name}\n{json.dumps(d, indent=1)}\n\n")


def main(argv: List[str]) -> int:
    if len(argv) < 3:
        print(__doc__); return 2
    a, b, rep = Path(argv[0]), Path(argv[1]), Path(argv[2])
    ignore = [x for x in argv[4:]] if len(argv) > 3 and argv[3] == "--ignore" else []
    res = diff_runs(a, b, ignore)
    n = len({p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()})
    write_report(res, rep, a, b, n)
    print("PASS (empty diff)" if not res else f"FAIL: {len(res)} differing files")
    return 0 if not res else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
