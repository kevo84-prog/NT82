r"""Phase 3 Step A2 / A3: the plan hash tables (Book1A/Phase3/plan_hashes_phase3.md and plan_hashes_phase3_c2.md).

  python -m book1a.phase3_plan_hashes --set base --plans book1a\Phase3\plans_phase3 --maps book1a\Phase3\runs\maps_phase3 \
      --out book1a\Phase3\plan_hashes_phase3.md [--check]
  python -m book1a.phase3_plan_hashes --set c2 --plans book1a\Phase3\plans_phase3_c2 --maps book1a\Phase3\runs\maps_phase3 \
      --out book1a\Phase3\plan_hashes_phase3_c2.md [--check]

The Phase 2 table (book1a.phase2_plan_hashes, its rows logic and packet_body_sha reused) on the 41 Phase 3 sessions:
sha256 of every plan .txt and sidecar .json, plan id, builder, context, review, decision-zone count, and the map packet
body sha256 (JSON without built_local, sorted keys, compact). Plan content only; no ledger or outcome. --check compares
the files with an existing table and exits 1 on any difference (G1 in Step B). Same columns as Phase 2, so
phase2_review_apply reads the sidecar_sha256 column unchanged.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from book1a import plan_v24 as P, sessions as S
from book1a.phase2_plan_hashes import packet_body_sha, sha_b

VERSION = "phase3-plan-hashes-v1.0"
COLS = ["session", "plan_sha256", "sidecar_sha256", "builder", "plan_id", "market_context", "review", "decision_zones", "packet",
        "packet_body_sha256"]
TITLE = {"base": "Book 1A plans (R4 baseline)", "c2": "C2 plans (VWAP as a tag only; book1a.plan_c2)"}


def rows(plans: Path, maps: Path, phase: str = "phase3"):
    out = []
    for d in S.phase_sessions(phase):
        ds = d.isoformat()
        t, j = plans / f"PreopenPlan_{ds}_book1a.txt", plans / f"PreopenPlan_{ds}_book1a.json"
        text = t.read_text(encoding="utf-8")
        kv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in text.splitlines() if "=" in l and not l.startswith("#")}
        side = json.loads(j.read_text(encoding="utf-8"))
        pk = sorted((maps / "map").glob(f"PreopenPacket_*{ds}.json"))
        m = re.search(r"plan-v[\w.\-]+", text.splitlines()[0])
        out.append(dict(session=ds, plan_sha256=sha_b(t.read_bytes()), sidecar_sha256=sha_b(j.read_bytes()),
                        builder=m.group(0) if m else "?", plan_id=kv.get("plan_id", "?"), market_context=kv.get("market_context", "?"),
                        review=kv.get("review", "?"), decision_zones=len(side.get("zones", [])),
                        packet=pk[0].name if pk else "MISSING", packet_body_sha256=packet_body_sha(pk[0]) if pk else "MISSING"))
    return out


def table(R, which: str) -> str:
    L = [f"# Book 1A Phase 3 plan hashes: {TITLE[which]} ({VERSION}; Step A, Nov 8, 2026)", "",
         f"{len(R)} premarket plans built with no trading run (map v2.3 packets from the frozen Book 1 map step by "
         f"`book1a.build_plans_phase --phase phase3`, then the frozen plan code {P.VERSION}"
         + ("" if which == "base" else "; C2: the same build with the VWAP family not counted, `book1a.plan_c2`") +
         "). Committed before any Phase 3 run. G1 checks the R4 rows' plan_sha256 and a rebuild from the Step B run's own "
         "map packets against this table. packet_body_sha256 = sha256 of the packet JSON without built_local (sorted keys, "
         "compact).", "", "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    L += ["| " + " | ".join(str(r[c]) for c in COLS) + " |" for r in R]
    return "\n".join(L) + "\n"


def body(text: str) -> dict:
    return {l.split(" | ")[0].strip("| "): l for l in text.splitlines() if re.match(r"\| 20\d\d-", l)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=sorted(TITLE)); ap.add_argument("--plans", required=True)
    ap.add_argument("--maps", required=True); ap.add_argument("--out", required=True); ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    R = rows(Path(a.plans), Path(a.maps))
    text = table(R, a.set)
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
