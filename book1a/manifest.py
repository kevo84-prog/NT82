"""Book 1A data manifest and checksum comparison (checklist P0.2).

Usage:
  python -m book1a.manifest build  <root> <out.csv> [--glob PATTERN ...]
  python -m book1a.manifest compare <ours.csv> <reference.csv> <report.md>

build: one row per file under <root>: relative path, bytes, mtime (UTC), sha256.
compare: joins on the file name (basename) and reports missing / extra / size or hash differences.
The reference is the Book 1 Phase 0 gate 6 table (data_integrity_*.csv: columns date, file, size_mb, ...; no
checksums, so sizes are compared to 0.1 MB and our sha256 list becomes the Book 1A reference) or any CSV with a
file-name column and, if present, 'bytes'/'size' and 'sha256'.
"""
from __future__ import annotations

import csv
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

VERSION = "manifest-v1.0"


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def build(root: Path, out_csv: Path, patterns: Optional[List[str]] = None) -> int:
    files: List[Path] = []
    if patterns:
        for p in patterns:
            files += sorted(root.rglob(p))
    else:
        files = sorted(p for p in root.rglob("*") if p.is_file())
    files = sorted(set(files))
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "name", "bytes", "mtime_utc", "sha256"])
        for p in files:
            st = p.stat()
            w.writerow([p.relative_to(root).as_posix(), p.name, st.st_size,
                        datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(), sha256_of(p)])
    return len(files)


def _load(path: Path) -> Dict[str, dict]:
    rows = list(csv.DictReader(open(path, newline="")))
    out = {}
    for r in rows:
        raw = r.get("name") or r.get("file") or r.get("filename") or r.get("path", "")
        name = raw.replace("\\", "/").split("/")[-1] if raw else ""
        if name:
            out[name] = r
    return out


def _num(r: dict, *keys):
    for k in keys:
        if k in r and r[k] not in ("", None):
            try:
                return int(float(r[k]))
            except ValueError:
                return None
    return None


def _hash(r: dict, *keys):
    for k in keys:
        if k in r and r[k]:
            return r[k].strip().lower()
    return None


def compare(ours_csv: Path, ref_csv: Path, report_md: Path) -> dict:
    ours, ref = _load(ours_csv), _load(ref_csv)
    missing = sorted(n for n in ref if n not in ours)
    extra = sorted(n for n in ours if n not in ref)
    diffs = []
    checked_hash = 0
    for n in sorted(set(ours) & set(ref)):
        a, b = ours[n], ref[n]
        sa, sb = _num(a, "bytes", "size", "size_bytes"), _num(b, "bytes", "size", "size_bytes", "file_size")
        size_diff = sa is not None and sb is not None and sa != sb
        if sb is None and "size_mb" in b and b["size_mb"] not in ("", None) and sa is not None:
            # Book 1 gate 6 table (data_integrity.py): size_mb = round(bytes / 1e6, 1)
            size_diff = round(sa / 1e6, 1) != round(float(b["size_mb"]), 1)
            sb = f"{float(b['size_mb']):.1f} MB"
        ha, hb = _hash(a, "sha256"), _hash(b, "sha256")
        if ha and hb:
            checked_hash += 1
        if size_diff or (ha and hb and ha != hb):
            diffs.append((n, sa, sb, ha, hb))
    with open(report_md, "w") as f:
        f.write(f"# P0.2 data manifest comparison\n\nours: {ours_csv}\nreference: {ref_csv}\n\n")
        f.write(f"- files in reference: {len(ref)}\n- files in ours: {len(ours)}\n- common: {len(set(ours) & set(ref))}\n")
        f.write(f"- hash-checked: {checked_hash}\n- missing from ours: {len(missing)}\n- extra in ours: {len(extra)}\n- differing: {len(diffs)}\n\n")
        verdict = "PASS" if not missing and not diffs else "FAIL"
        f.write(f"**Verdict: {verdict}** (extra files are listed, not failures, unless the backtest uses them)\n\n")
        if missing:
            f.write("## Missing\n" + "\n".join(f"- {m}" for m in missing) + "\n\n")
        if extra:
            f.write("## Extra\n" + "\n".join(f"- {m}" for m in extra) + "\n\n")
        if diffs:
            f.write("## Differing\n| file | bytes ours | bytes ref | sha256 ours | sha256 ref |\n|---|---|---|---|---|\n")
            for d in diffs:
                f.write(f"| {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} |\n")
    return {"reference": len(ref), "ours": len(ours), "missing": len(missing), "extra": len(extra),
            "differing": len(diffs), "hash_checked": checked_hash}


def main(argv: List[str]) -> int:
    if len(argv) >= 3 and argv[0] == "build":
        pats = [a for a in argv[3:] if not a.startswith("--")]
        n = build(Path(argv[1]), Path(argv[2]), pats or None)
        print(f"{n} files -> {argv[2]}")
        return 0
    if len(argv) == 4 and argv[0] == "compare":
        print(compare(Path(argv[1]), Path(argv[2]), Path(argv[3])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
