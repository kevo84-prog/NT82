"""Old vs new gex_v3 repro flags (Phase 3 Step B fix check, Nov 9, 2026). GEX inputs only; no trade outcome is read.

  python book1a/Phase3/gex_v3_fix_check.py      (from code/, BOOK1_ROOT=K:\\Book1A_inputs)

OLD = book1a/gex_v3.py at 8107c0f (git show, loaded as a separate module); NEW = the working-tree book1a/gex_v3.py.
Both run() on the 21 Phase 2 and the 41 Phase 3 sessions. Writes gex_v3_fix_check.csv (one row per session and level:
old flag, new flag, rebuilt value, frozen cell) and prints the acceptance result:
  - every session except Dec 17-18, 2025: every flag identical and repro_all_match = Y in both;
  - Dec 17-18: only call_resistance_0dte, put_support_0dte, hvl_0dte may change N -> Y, each with rebuilt value absent
    (None / NaN) and frozen cell absent (empty after strip).
"""
import csv
import importlib.util
import math
import os
import subprocess
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CODE))
from book1a import gex_v3 as NEW, sessions as S          # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "runs" / "gex_v3_fix_check"
OUT.mkdir(parents=True, exist_ok=True)
old_src = subprocess.check_output(["git", "show", "8107c0f:book1a/gex_v3.py"], cwd=CODE)
(OUT / "gex_v3_old_8107c0f.py").write_bytes(old_src)
spec = importlib.util.spec_from_file_location("gex_v3_old", OUT / "gex_v3_old_8107c0f.py")
OLD = importlib.util.module_from_spec(spec); spec.loader.exec_module(OLD)

inputs = Path(os.environ.get("BOOK1_ROOT", r"K:\Book1A_inputs"))
sessions = [d.isoformat() for ph in ("phase2", "phase3") for d in S.phase_sessions(ph)]
SPECIAL = {"2025-12-17", "2025-12-18"}
ALLOWED = {"call_resistance_0dte", "put_support_0dte", "hvl_0dte"}

old = {r["session"]: r for r in OLD.run(inputs, sessions, OUT / "old")}
new = {r["session"]: r for r in NEW.run(inputs, sessions, OUT / "new")}
rows_f = {r["session"]: r for r in csv.DictReader(open(inputs / "gex_levels_block1.csv", newline="", encoding="utf-8-sig"))}
GC, MQ = NEW.import_code(inputs)

out, problems, changed = [], [], []
for s in sessions:
    om = set(filter(None, old[s]["repro_mismatch"].split(",")))
    nm = set(filter(None, new[s]["repro_mismatch"].split(",")))
    lv = None
    if s in SPECIAL:
        _, lv, _ = NEW.build_session(GC, MQ, inputs / "raw" / "block1", rows_f[s])
    for k in NEW.REPRO:
        fo, fn = "N" if k in om else "Y", "N" if k in nm else "Y"
        a = (lv or {}).get(k) if lv is not None else ""
        out.append(dict(session=s, phase="phase2" if s < "2025-12-05" else "phase3", level=k, old_flag=fo, new_flag=fn,
                        changed="Y" if fo != fn else "N", rebuilt_value=repr(a) if lv is not None else "",
                        frozen_cell=repr(rows_f[s].get(k))))
        if s not in SPECIAL:
            if fo != fn or fn != "Y":
                problems.append(f"{s} {k}: old {fo} new {fn}")
        elif fo != fn:
            a_abs = a is None or (isinstance(a, float) and math.isnan(a))
            b = rows_f[s].get(k)
            b_abs = b is None or (isinstance(b, str) and b.strip() == "")
            ok = k in ALLOWED and fo == "N" and fn == "Y" and a_abs and b_abs
            changed.append(f"{s} {k}: {fo} -> {fn} (rebuilt {a!r}, frozen {b!r}, both-absent {a_abs and b_abs})")
            if not ok:
                problems.append(f"{s} {k}: change not allowed ({fo} -> {fn})")
    if s not in SPECIAL and (old[s]["repro_all_match"] != "Y" or new[s]["repro_all_match"] != "Y"):
        problems.append(f"{s}: repro_all_match old {old[s]['repro_all_match']} new {new[s]['repro_all_match']}")
    if s in SPECIAL and new[s]["repro_all_match"] != "Y":
        problems.append(f"{s}: new repro_all_match {new[s]['repro_all_match']} ({new[s]['repro_mismatch']})")

with open(HERE / "gex_v3_fix_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
other = [s for s in sessions if s not in SPECIAL]
print(f"sessions {len(sessions)} (other {len(other)}), level flags {len(out)}, changed {sum(r['changed'] == 'Y' for r in out)}")
print("changes:\n  " + "\n  ".join(changed))
print("ACCEPTANCE:", "PASS" if not problems else "FAIL")
for p in problems:
    print("  ", p)
sys.exit(1 if problems else 0)
