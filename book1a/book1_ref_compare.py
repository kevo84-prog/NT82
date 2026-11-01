r"""A2: compare book1_ref/MANIFEST.md (sha256 of the Drive mirror) with the frozen Book 1 tag on the PC.

  python -m book1a.book1_ref_compare book1_ref\MANIFEST.md K:\Databento_BackTesting ..\Phase0\A2_book1_tag_compare.md
      [--tag phase4-result] [--raw K:\Databento_BackTesting\raw]

Reads only code, config and static-input files named in the manifest (never a result folder). For every manifest
row it looks for the file under the Book 1 root, hashes it, and reports MATCH / DIFFERS / MISSING. With --tag it
also records `git -C <root> rev-parse <tag>` and whether HEAD is at that tag (the checkout is not changed).
Exit code 0 = every file matches, 1 otherwise.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from book1a.manifest import sha256_of

VERSION = "book1-ref-compare-v1.0"

ROW = re.compile(r"^\|\s*(?P<path>[^|]+?)\s*\|\s*(?P<id>[^|]*?)\s*\|\s*(?P<mtime>[^|]*?)\s*\|\s*(?P<bytes>\d+)\s*\|\s*(?P<sha>[0-9a-f]{64})\s*\|")

# book1_ref keeps a few files under data/ and backtest/; on the PC they live where the Book 1 scripts expect them
# (phase0_parity.py PATHS, build_inputs.py). First hit wins; a bare file name is then searched under --raw.
PC_CANDIDATES = {
    "data/gex_levels_block1.csv": ["gex_levels_block1.csv", "gex_results/final/gex_levels_block1.csv"],
    "data/estimate_block1.csv": ["estimate_block1.csv", "raw/block1/estimate_block1.csv"],
    "data/estimate_block1_l3.csv": ["estimate_block1_l3.csv", "raw/block1/estimate_block1_l3.csv"],
    "data/estimate_block1_roll.csv": ["estimate_block1_roll.csv", "raw/block1/estimate_block1_roll.csv"],
    "data/econ_calendar_2025-10_2026-04.csv": ["econ_calendar_2025-10_2026-04.csv", "macro/econ_calendar_2025-10_2026-04.csv"],
    "data/condition_NQ_MBO_2026-09.json": ["NQ_MBO_2026-09/GLBX-20260928-6GPK57A3YJ/condition.json"],
}


def parse_manifest(path: Path) -> List[Dict[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        p = m.group("path").strip("`").split(" (")[0].strip()
        rows.append(dict(path=p, bytes=m.group("bytes"), sha256=m.group("sha")))
    return rows


def locate(rel: str, root: Path, raw: Optional[Path]) -> Optional[Path]:
    cands = [rel] + PC_CANDIDATES.get(rel, [])
    for c in cands:
        p = root / c
        if p.is_file():
            return p
    name = Path(rel).name
    if raw and raw.is_dir():
        hits = sorted(raw.rglob(name))
        if len(hits) == 1:
            return hits[0]
    return None


def git_info(root: Path, tag: Optional[str]) -> Dict[str, str]:
    def run(*args):
        try:
            return subprocess.check_output(["git", "-C", str(root)] + list(args), text=True, stderr=subprocess.STDOUT).strip()
        except Exception as e:  # not a git repo, git missing, unknown tag
            return f"n/a ({type(e).__name__})"
    info = dict(head=run("rev-parse", "HEAD"), describe=run("describe", "--tags", "--always"),
                status=run("status", "--porcelain", "--untracked-files=no"))
    if tag:
        info["tag"] = tag
        info["tag_commit"] = run("rev-parse", f"{tag}^{{commit}}")
        info["head_is_tag"] = str(info["tag_commit"] == info["head"])
    return info


def compare(manifest: Path, root: Path, report: Path, tag: Optional[str] = None, raw: Optional[Path] = None) -> Dict[str, int]:
    rows = parse_manifest(manifest)
    out, n_match = [], 0
    for r in rows:
        p = locate(r["path"], root, raw)
        if p is None:
            out.append((r["path"], "MISSING", "", r["sha256"], ""))
            continue
        h = sha256_of(p)
        size = p.stat().st_size
        if h == r["sha256"]:
            n_match += 1
            out.append((r["path"], "MATCH", str(p), h, str(size)))
        else:
            out.append((r["path"], "DIFFERS", str(p), f"{r['sha256'][:12]}… vs {h[:12]}…", f"{r['bytes']} vs {size}"))
    git = git_info(root, tag)
    n_diff = sum(1 for o in out if o[1] == "DIFFERS"); n_miss = sum(1 for o in out if o[1] == "MISSING")
    verdict = "PASS" if n_diff == 0 and n_miss == 0 else "FAIL"
    L = [f"# A2: book1_ref manifest vs the Book 1 checkout at `{root}`", "",
         f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by {VERSION}. Manifest `{manifest}` ({len(rows)} files).", "",
         "| git | |", "|---|---|"] + [f"| {k} | `{v}` |" for k, v in git.items()] + ["",
         f"**{verdict}**: {n_match} match, {n_diff} differ, {n_miss} missing.", "",
         "| manifest path | result | PC path | sha256 (manifest vs PC) | bytes (manifest vs PC) |", "|---|---|---|---|---|"]
    for path, res, pc, sha, size in out:
        if res == "MATCH":
            L.append(f"| {path} | MATCH | `{pc}` | {sha[:12]}… | {size} |")
        else:
            L.append(f"| {path} | **{res}** | `{pc}` | {sha} | {size} |")
    if verdict == "FAIL":
        L += ["", "Every DIFFERS / MISSING row above is a file whose Drive mirror is not the frozen tag's version. "
                  "Report them to Kyron before P0.4; do not edit either side."]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(L) + "\n", encoding="utf-8")
    return dict(files=len(rows), match=n_match, differing=n_diff, missing=n_miss)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest"); ap.add_argument("book1_root"); ap.add_argument("report")
    ap.add_argument("--tag", default=None); ap.add_argument("--raw", default=None)
    a = ap.parse_args(argv)
    r = compare(Path(a.manifest), Path(a.book1_root), Path(a.report), a.tag, Path(a.raw) if a.raw else None)
    print(r, "->", a.report)
    return 0 if r["differing"] == 0 and r["missing"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
