"""Phase 4 Step B, G1 plan checks (Phase4_registration.md section 7). Read-only on every input; writes one log.

  python Book1A/Phase4/stepB/g1_plans_check.py <log path>

1. Plans rebuilt from the Step B R1 run's own map packets (frozen plan_hand_check.build_day) equal the Step A files
   (plans_phase4), text and sidecar.
2. Step B map packets vs Step A packets: JSON equal without built_local (build_plans_phase.packet_body).
3. Every R4 ledger / candidate row's plan_sha256 equals plan_hashes_phase4.md.
Exit 1 on any difference. Written in Step A (Nov 9, 2026), the Phase 3 check with the phase changed and no C2 set.
"""
import csv
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # code/
sys.path.insert(0, str(ROOT))
os.environ.setdefault("BOOK1_ROOT", r"K:\Book1A_inputs")
from book1a import sessions as S                                        # noqa: E402
from book1a.build_plans_phase import packet_body                        # noqa: E402
from book1a.book1_import import jeron_engine                            # noqa: E402,F401
from book1a.hand_checks import plan_hand_check as PHC                   # noqa: E402

P4 = ROOT / "book1a" / "Phase4"
RUN = P4 / "runs" / "phase4"
out, bad = [], False


def hashes(md: Path) -> dict:
    h = {}
    for line in md.read_text(encoding="utf-8").splitlines():
        if re.match(r"\| 20\d\d-", line):
            c = [x.strip() for x in line.strip("|").split("|")]
            h[c[0]] = c
    return h


gex, cal = PHC.load_inputs(Path(os.environ["BOOK1_ROOT"]))
days = [d.isoformat() for d in S.phase_sessions("phase4")]
diff_b = []
for ds in days:
    t0, s0, _ = PHC.build_day(RUN, ds, gex, cal)
    if t0 != (P4 / "plans_phase4" / f"PreopenPlan_{ds}_book1a.txt").read_text(encoding="utf-8") or \
       json.dumps(s0, indent=1, default=str) != (P4 / "plans_phase4" / f"PreopenPlan_{ds}_book1a.json").read_text(encoding="utf-8"):
        diff_b.append(ds)
out.append(f"plans rebuilt from the Step B R1 run's map packets: {2 * len(days)} files, different: {diff_b}")
bad |= bool(diff_b)

pk_diff = []
for ds in days:
    a = sorted((P4 / "runs" / "maps_phase4" / "map").glob(f"PreopenPacket_*{ds}.json"))
    b = sorted((RUN / "map").glob(f"PreopenPacket_*{ds}.json"))
    if len(a) != 1 or len(b) != 1 or packet_body(a[0]) != packet_body(b[0]):
        pk_diff.append(ds)
out.append(f"Step B packets vs Step A packets (body without built_local): {len(days)}, different: {pk_diff}")
bad |= bool(pk_diff)

sha_col = {k: v[1] for k, v in hashes(P4 / "plan_hashes_phase4.md").items()}
if len(sha_col) != len(days):
    out.append(f"plan_hashes_phase4.md rows {len(sha_col)} != {len(days)}"); bad = True
for f in ("R4_M0_ledger.csv", "R4_candidates.csv"):
    rows = list(csv.DictReader(open(P4 / "runs" / "phase4_r4" / f, newline="", encoding="utf-8")))
    has = bool(rows) and "plan_sha256" in rows[0]
    dcol = "date" if rows and "date" in rows[0] else "session"
    mism = [r.get(dcol) for r in rows if r.get("plan_sha256") != sha_col.get(r.get(dcol))]
    out.append(f"R4 {f}: rows {len(rows)}, plan_sha256 column present {has}, mismatches {len(mism)}")
    bad |= bool(mism) or (bool(rows) and not has)
out.append("G1 plans: " + ("FAIL" if bad else "OK"))
text = "\n".join(out) + "\n"
Path(sys.argv[1]).write_text(text, encoding="utf-8")
print(text)
sys.exit(1 if bad else 0)
