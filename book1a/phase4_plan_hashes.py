r"""Phase 4 Step A2: the plan hash table (Book1A/Phase4/plan_hashes_phase4.md).

  python -m book1a.phase4_plan_hashes --plans book1a\Phase4\plans_phase4 --maps book1a\Phase4\runs\maps_phase4 \
      --out book1a\Phase4\plan_hashes_phase4.md [--check]

The Phase 3 table (book1a.phase3_plan_hashes.rows, unchanged, with phase="phase4") on the 52 Phase 4 sessions: sha256 of
every plan .txt and sidecar .json, plan id, builder, context, review, decision-zone count, and the map packet body sha256.
Plan content only; no ledger or outcome. --check compares with an existing table and exits 1 on any difference (G1).
Same columns as Phase 2 / 3, so phase2_review_apply reads the sidecar_sha256 column unchanged. No C2 set in Phase 4.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from book1a import plan_v24 as P
from book1a.phase3_plan_hashes import COLS, body, rows

VERSION = "phase4-plan-hashes-v1.0"


def table(R) -> str:
    L = [f"# Book 1A Phase 4 plan hashes: Book 1A plans (R4) ({VERSION}; Step A, Nov 9, 2026)", "",
         f"{len(R)} premarket plans built with no trading run (map v2.3 packets from the frozen Book 1 map step by "
         f"`book1a.build_plans_phase --phase phase4`, then the frozen plan code {P.VERSION}). Committed before any Phase 4 "
         "run. G1 checks the R4 rows' plan_sha256 and a rebuild from the Step B run's own map packets against this table. "
         "packet_body_sha256 = sha256 of the packet JSON without built_local (sorted keys, compact).", "",
         "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    L += ["| " + " | ".join(str(r[c]) for c in COLS) + " |" for r in R]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plans", required=True); ap.add_argument("--maps", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    R = rows(Path(a.plans), Path(a.maps), "phase4")
    text = table(R)
    out = Path(a.out)
    if a.check:
        old, new = body(out.read_text(encoding="utf-8")), body(text)
        diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        print("plan hash check:", "MATCH" if not diff else f"DIFFERENT {diff}")
        return 1 if diff else 0
    out.write_text(text, encoding="utf-8")
    print(f"{len(R)} plans -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
