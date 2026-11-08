r"""C2 plan set: the location arm with VWAP as a tag only (replay plan section 5, C2; Phase 3 Step A3, Nov 8, 2026).

  python -m book1a.plan_c2 --block1 K:\Book1A_inputs --phase phase3 --maps book1a\Phase3\runs\maps_phase3 \
      --base-plans book1a\Phase3\plans_phase3 --plans book1a\Phase3\plans_phase3_c2

Definition (frozen documents, quoted in Book1A/Phase3/Phase3_registration.md):
  AMT PO-8 "Source family (C2): session VWAP, weekly VWAP and the bands together are one family (VWAP) toward the
  2-family minimum in Phase 3 and PO-3 ... VWAP never creates a zone on its own and never changes a side." and
  "Diagnostic split (not promotable): the location arm with VWAP counted vs the same arm with VWAP as a tag only".
  PO-8 tag rule: "every zone gets VWAP if the session VWAP is inside it or within 5 points ..., and WKVWAP for the
  weekly VWAP. The +/-1 sigma bands are tagged the same way".

Implementation: the same frozen code (map packets of the baseline build, book1a.hand_checks.plan_hand_check.build_day
-> plan_v24.build, families-v1.0, every threshold unchanged). The only difference: inside vwap_tag_only(),
families.count_families drops the VWAP family from the family list (so from the 2-family DECISION count and the
families= field). The VWAP levels stay in levels= (the PO-8 tags: same names, same 5-point rule) and the PO-1 VWAP tag
on rejection zones is untouched. A zone that falls below 2 families becomes TARGET through the frozen code path.
The baseline plans are rebuilt in the same process outside the patch and must equal the --base-plans files byte for
byte (hard error otherwise), so the two sets differ only by the VWAP family.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

from book1a import families as F, sessions as S

VERSION = "c2-vwap-tag-only-v1.0"
DROPPED_FAMILY = "VWAP"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@contextlib.contextmanager
def vwap_tag_only():
    """families.count_families without the VWAP family; levels (the tags) unchanged. Restored on exit."""
    orig = F.count_families

    def count_families(zone_lo, zone_hi, levels, own_families=(), gex_tolerance=F.GEX_TOLERANCE_PTS):
        if DROPPED_FAMILY in own_families:
            raise ValueError("VWAP never creates a zone on its own (PO-8): no zone may carry VWAP as its own family")
        r = orig(zone_lo, zone_hi, levels, own_families=own_families, gex_tolerance=gex_tolerance)
        fams = [f for f in r.families if f != DROPPED_FAMILY]
        return F.FamilyResult(r.zone_lo, r.zone_hi, fams, list(r.levels), {f: r.per_family[f] for f in fams})

    F.count_families = count_families
    try:
        yield
    finally:
        F.count_families = orig


def zone_key(z: dict) -> str:
    return f"{z['lo']}-{z['hi']}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--block1", required=True); ap.add_argument("--phase", required=True, choices=list(S.PHASES))
    ap.add_argument("--maps", required=True); ap.add_argument("--base-plans", required=True); ap.add_argument("--plans", required=True)
    a = ap.parse_args(argv)
    block1, maps, base, plans = (Path(x).resolve() for x in (a.block1, a.maps, a.base_plans, a.plans))
    os.environ["BOOK1_ROOT"] = str(block1)
    from book1a.book1_import import jeron_engine  # noqa: F401
    from book1a.hand_checks import plan_hand_check as PHC
    gex, cal = PHC.load_inputs(block1)
    plans.mkdir(parents=True, exist_ok=False)
    rows = []
    for d in S.phase_sessions(a.phase):
        ds = d.isoformat()
        t0, s0, _ = PHC.build_day(maps, ds, gex, cal)
        j0 = json.dumps(s0, indent=1, default=str)
        bt, bj = base / f"PreopenPlan_{ds}_book1a.txt", base / f"PreopenPlan_{ds}_book1a.json"
        if t0 != bt.read_text(encoding="utf-8") or j0 != bj.read_text(encoding="utf-8"):   # text compare (files written by write_text)
            raise SystemExit(f"{ds}: the baseline rebuild differs from {bt.parent}; C2 not built")
        with vwap_tag_only():
            t1, s1, _ = PHC.build_day(maps, ds, gex, cal)
        if F.count_families.__module__ != F.__name__:
            raise SystemExit("count_families was not restored")
        j1 = json.dumps(s1, indent=1, default=str)
        ct, cj = plans / f"PreopenPlan_{ds}_book1a.txt", plans / f"PreopenPlan_{ds}_book1a.json"
        ct.write_text(t1, encoding="utf-8"); cj.write_text(j1, encoding="utf-8")       # written as build_plans_phase writes them
        k0 = {zone_key(z): z for z in s0["zones"]}; k1 = {zone_key(z): z for z in s1["zones"]}
        rows.append(dict(session=ds, base_plan_sha256=sha(bt.read_bytes()), plan_sha256=sha(ct.read_bytes()),
                         sidecar_sha256=sha(cj.read_bytes()), identical_to_base=t1 == t0 and j1 == j0,
                         base_decision_zones=len(s0["zones"]), decision_zones=len(s1["zones"]),
                         base_zones_with_vwap=sum(DROPPED_FAMILY in z["families"] for z in s0["zones"]),
                         zones_only_in_base=sorted(set(k0) - set(k1)), zones_only_in_c2=sorted(set(k1) - set(k0)),
                         market_context=s1["market_context"], review=s1["review"]))
        print(ds, "identical" if rows[-1]["identical_to_base"] else "differs", len(s0["zones"]), "->", len(s1["zones"]), "decision zones")
    (plans / "plan_build_manifest.json").write_text(json.dumps(dict(
        version=VERSION, phase=a.phase, variant="C2: VWAP as a tag only (VWAP family not counted)", maps=str(maps),
        base_plans=str(base), built_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), rows=rows), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
