r"""Phase 2 Step A2: the plan hash table (Book1A/Phase2/plan_hashes_phase2.md).

  python -m book1a.phase2_plan_hashes --plans book1a\Phase2\plans_phase2 --maps book1a\Phase2\runs\maps_phase2 \
      --out book1a\Phase2\plan_hashes_phase2.md [--check]

sha256 of every plan .txt and sidecar .json, the plan id and builder version from the plan header, and the sha256 of
the map packet body (canonical JSON without built_local, the build wall clock, so a rebuild can be compared). Plan
content only (context, zones, review); no ledger or outcome. --check compares the files with an existing table and
exits 1 on any difference (G1 in Step B).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from book1a import plan_v24 as P, sessions as S

VERSION = "phase2-plan-hashes-v1.0"


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def packet_body_sha(p: Path) -> str:
    x = json.loads(p.read_text(encoding="utf-8"))
    x.pop("built_local", None)
    return sha_b(json.dumps(x, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def rows(plans: Path, maps: Path):
    out = []
    for d in S.phase_sessions("phase2"):
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plans", required=True); ap.add_argument("--maps", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    R = rows(Path(a.plans), Path(a.maps))
    cols = ["session", "plan_sha256", "sidecar_sha256", "builder", "plan_id", "market_context", "review", "decision_zones", "packet", "packet_body_sha256"]
    L = [f"# Book 1A Phase 2 plan hashes ({VERSION}; Step A2, Nov 6, 2026)", "",
         f"21 premarket plans built with no trading run by `book1a.build_plans_phase` (map v2.3 packets from the frozen "
         f"Book 1 map step, then the frozen plan code {P.VERSION}). Committed before any Step B run. G1 checks the R4 "
         "rows' plan_sha256 and a rebuild from the Step B run's own map packets against this table. packet_body_sha256 = "
         "sha256 of the packet JSON without built_local (sorted keys, compact).", "",
         "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    L += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in R]
    text = "\n".join(L) + "\n"
    out = Path(a.out)
    if a.check:
        old = {l.split(" | ")[0].strip("| "): l for l in out.read_text(encoding="utf-8").splitlines() if l.startswith("| 2025-")}
        new = {l.split(" | ")[0].strip("| "): l for l in text.splitlines() if l.startswith("| 2025-")}
        diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        print("plan hash check:", "MATCH" if not diff else f"DIFFERENT {diff}")
        return 1 if diff else 0
    out.write_text(text, encoding="utf-8")
    print(f"{len(R)} plans -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
