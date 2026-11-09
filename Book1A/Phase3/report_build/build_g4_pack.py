"""Phase 3 G4 checker pack: byte copies of the Step B outputs into book1a/Phase3/checker_input/, a manifest, a zip.
Copies only; no number is computed. Run from code/ after g4_draw has written checker_input/g4_sample.csv."""
import datetime as dt
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

CODE = Path(__file__).resolve().parents[4]
R = CODE / "book1a" / "Phase3" / "runs"
CI = CODE / "book1a" / "Phase3" / "checker_input"
COPY = {
    "ledgers/R1_A0_full.csv": "phase3/R1_A0_full.csv", "ledgers/R2_C1_full.csv": "phase3/R2_C1_full.csv",
    "ledgers/R1_A0_checker.csv": "phase3/checker_input/R1_A0.csv", "ledgers/R2_C1_checker.csv": "phase3/checker_input/R2_C1.csv",
    "ledgers/R3_M0_ledger.csv": "phase3_r3/R3_M0_ledger.csv", "ledgers/R4_M0_ledger.csv": "phase3_r4/R4_M0_ledger.csv",
    "ledgers/C2_R4_M0_ledger.csv": "phase3_r4_c2/R4_M0_ledger.csv",
    "attempts/R1_attempts.csv": "phase3/R1_attempts.csv", "attempts/R2_attempts.csv": "phase3/R2_attempts.csv",
    "attempts/R2_retests.csv": "phase3/R2_retests.csv", "attempts/R3_attempts.csv": "phase3_r3/R3_attempts.csv",
    "attempts/R3_retests.csv": "phase3_r3/R3_retests.csv", "attempts/R3_risk_events.json": "phase3_r3/R3_risk_events.json",
    "attempts/R4_attempts.csv": "phase3_r4/R4_attempts.csv", "attempts/R4_risk_events.json": "phase3_r4/R4_risk_events.json",
    "attempts/C2_R4_attempts.csv": "phase3_r4_c2/R4_attempts.csv", "attempts/C2_R4_risk_events.json": "phase3_r4_c2/R4_risk_events.json",
    "report/phase3_report_card.json": "phase3_report_card.json", "report/phase3_report_card_c2.json": "phase3_report_card_c2.json",
    "report/phase3_compare.json": "phase3_compare/phase3_compare.json",
}
for k in ("lat1000", "slip2", "slip4"):
    for n in ("R1_A0_full.csv", "R2_C1_full.csv", "R3_M0_ledger.csv", "R4_M0_ledger.csv", "stress_manifest.json"):
        COPY[f"stress/{k}/{n}"] = f"phase3_stress_{k}/{n}"
for p in sorted((R / "phase3_review").glob("*")):
    if p.is_file():
        COPY[f"report/{p.name}"] = f"phase3_review/{p.name}"
for m in ("phase3/run_manifest.json", "phase3_r3/run_manifest.json", "phase3_r4/run_manifest.json", "phase3_r4_c2/run_manifest.json"):
    COPY[f"manifests/{m.replace('/', '__')}"] = m
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()   # noqa: E731
for dst, src in COPY.items():
    s, d = R / src, CI / dst
    if not s.exists():
        raise SystemExit(f"missing {s}")
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(s, d)
    if sha(s) != sha(d):
        raise SystemExit(f"copy differs {dst}")
files = sorted(p for p in CI.rglob("*") if p.is_file() and p.name not in ("pack_manifest.json", "Phase3_G4_checker_pack.zip"))
man = dict(pack="Book 1A Phase 3 G4 checker pack", created_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           execution_commit="8107c0f9f1980d209dffbf7ebe98a57a9dce2e45 (book1a-phase3-frozen): R1-R4, C2 R4, stress",
           diagnostics_and_reporting_commit="17ac9cd0b503f8bd6c88367fa0cab192a8f0e350 (gex_v3 both-absent fix): diagnostics, review, "
                                            "report cards, phase3_compare, G4 draw",
           label="replay (in-sample)",
           note="Copies of the Step B outputs (book1a/Phase3/runs/...), byte for byte. G4 sample drawn by g4_draw.py v1.1 unchanged.",
           files=[dict(path=str(p.relative_to(CI)).replace("\\", "/"), bytes=p.stat().st_size, sha256=sha(p)) for p in files])
(CI / "pack_manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
z = CI / "Phase3_G4_checker_pack.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in files + [CI / "pack_manifest.json"]:
        zf.write(p, str(p.relative_to(CI)).replace("\\", "/"))
print(f"files {len(files)} + pack_manifest.json; zip {z.stat().st_size} bytes sha256 {sha(z)}")
