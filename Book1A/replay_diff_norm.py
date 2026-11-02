r"""P0.3 on the PC: normalised whole-folder comparison of two run folders, on top of replay_diff.

  python -m book1a.replay_diff_norm <run_a> <run_b> <report.md>

replay_diff compares parsed rows; on two real daily-loop runs it reports every file because of four things that are
not results: gzip header times, wall-clock stamps written by the map / strategy, the run folder's own path, and the
JOFS file name (it carries the wall clock). This tool removes exactly those and nothing else, then compares every
file in both folders byte for byte:
  - *.gz: the decompressed content;
  - text: the run folder path (and its name runA / runB) replaced by <RUN>; 'built=YYYY-MM-DD HH:MM:SS' stamps, the map packet's "built_local" and the map's _run<clock> file-name part;
    the 'generated' and 'commit' lines of run_manifest.json;
  - strategy/JOFS_*.csv: paired by prefix, column 7 ProcessedTimeLocal (wall clock) blanked; every other column of
    every row must be equal.
Any other difference is listed with the first differing line. Exit 0 = DIFF EMPTY.
"""
from __future__ import annotations

import csv
import gzip
import io
import re
import sys
from pathlib import Path

VERSION = "replay-diff-norm-v1.0"
STAMP = re.compile(r"built=\d{4}-\d\d-\d\d \d\d:\d\d:\d\d")
BUILT_LOCAL = re.compile(r'"built_local":"[^"]*"')
RUNCLOCK = re.compile(r"_run\d{8}-\d{6}")
JOFS = re.compile(r"^(JOFS_.*_)\d{8}-\d{6}(\.csv)$")


def key(rel: str) -> str:
    p = rel.replace("\\", "/").split("/")
    m = JOFS.match(p[-1])
    if m:
        p[-1] = m.group(1) + "<CLOCK>" + m.group(2)
    p[-1] = RUNCLOCK.sub("_run<CLOCK>", p[-1])
    return "/".join(p)


def norm(path: Path, run: Path) -> bytes:
    if path.suffix == ".gz":
        # tapes (several GB unpacked; no paths or clock stamps inside): streamed sha256 of the decompressed content
        import hashlib
        h = hashlib.sha256()
        with gzip.open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 22), b""):
                h.update(chunk)
        return b"sha256 of content " + h.hexdigest().encode()
    data = path.read_bytes()
    if JOFS.match(path.name):
        rows = list(csv.reader(io.StringIO(data.decode("utf-8", "replace"))))
        i = rows[0].index("ProcessedTimeLocal") if rows and "ProcessedTimeLocal" in rows[0] else 6
        for r in rows[1:]:
            if len(r) > i:
                r[i] = ""
        out = io.StringIO(); csv.writer(out, lineterminator="\n").writerows(rows)
        data = out.getvalue().encode()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    for form in {str(run), str(run).replace("\\", "\\\\"), run.as_posix()}:
        text = text.replace(form, "<RUN>")
    text = text.replace(run.name, "<RUN>")
    text = STAMP.sub("built=<CLOCK>", text)
    text = BUILT_LOCAL.sub('"built_local":"<CLOCK>"', text)
    text = RUNCLOCK.sub("_run<CLOCK>", text)
    if path.name == "run_manifest.json":
        text = "\n".join(l for l in text.splitlines() if '"generated"' not in l and '"commit"' not in l)
    return text.encode()


def main(argv):
    a, b, rep = Path(argv[0]).resolve(), Path(argv[1]).resolve(), Path(argv[2])
    fa = {key(str(p.relative_to(a))): p for p in a.rglob("*") if p.is_file()}
    fb = {key(str(p.relative_to(b))): p for p in b.rglob("*") if p.is_file()}
    only_a, only_b = sorted(set(fa) - set(fb)), sorted(set(fb) - set(fa))
    diffs = []
    for k in sorted(set(fa) & set(fb)):
        x, y = norm(fa[k], a), norm(fb[k], b)
        if x != y:
            lx, ly = x.split(b"\n"), y.split(b"\n")
            n = next((i for i, (p, q) in enumerate(zip(lx, ly)) if p != q), min(len(lx), len(ly)))
            diffs.append((k, n + 1, lx[n][:300] if n < len(lx) else b"<end>", ly[n][:300] if n < len(ly) else b"<end>"))
    empty = not (only_a or only_b or diffs)
    L = [f"# P0.3 deterministic replay: normalised whole-folder diff ({VERSION})", "",
         f"run A: `{a}`", f"run B: `{b}`", f"files compared: {len(set(fa) & set(fb))}", "",
         "Normalised (not results): gzip headers (content compared), run folder path / name, `built=` wall-clock stamps,"
         " run_manifest `generated` / `commit`, JOFS file-name clock and column ProcessedTimeLocal (wall clock).", "",
         f"**{'DIFF EMPTY' if empty else 'DIFF NOT EMPTY'}**", ""]
    if only_a or only_b:
        L += ["## Files in one run only"] + [f"- A only: {k}" for k in only_a] + [f"- B only: {k}" for k in only_b] + [""]
    for k, n, x, y in diffs:
        L += [f"## {k} (first difference at line {n})", "```", "A: " + x.decode("utf-8", "replace"), "B: " + y.decode("utf-8", "replace"), "```", ""]
    rep.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(("DIFF EMPTY" if empty else f"DIFF NOT EMPTY: {len(diffs)} files, {len(only_a)} / {len(only_b)} unpaired") + f" -> {rep}")
    return 0 if empty else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
