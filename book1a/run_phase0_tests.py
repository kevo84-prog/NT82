"""Run the Book 1A Phase 0 unit tests and write the log the checklist asks for.

  python -m book1a.run_phase0_tests [out_dir]

Writes <out_dir>/unit_tests_<date>.log (default Book1A/Phase0/unit_tests) with the module version
tags, the git commit and the verbose unittest output, and prints the summary line.
"""
from __future__ import annotations

import io
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

import book1a
from book1a import families, ledger, lookahead, manifest, map_v24, plan_fields, replay_diff, risk, vwap


def main(argv):
    out_dir = Path(argv[0]) if argv else Path("Book1A/Phase0/unit_tests")
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        commit = "n/a"
    buf = io.StringIO()
    suite = unittest.defaultTestLoader.discover("book1a/tests", top_level_dir=".")
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    stamp = datetime.now(timezone.utc)
    header = [
        f"Book 1A Phase 0 unit tests  {stamp.isoformat(timespec='seconds')}  commit {commit}  package {book1a.VERSION}",
        "module versions: " + ", ".join(f"{m.__name__.split('.')[-1]}={m.VERSION}" for m in
                                        (risk, vwap, families, lookahead, map_v24, plan_fields, ledger, manifest, replay_diff)),
        f"python {sys.version.split()[0]}",
        f"tests run {result.testsRun}, failures {len(result.failures)}, errors {len(result.errors)}, "
        f"result {'PASS' if result.wasSuccessful() else 'FAIL'}",
        "",
    ]
    path = out_dir / f"unit_tests_{stamp.strftime('%Y-%m-%d')}.log"
    path.write_text("\n".join(header) + buf.getvalue())
    print(header[3]); print(f"log: {path}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
