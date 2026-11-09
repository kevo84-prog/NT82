"""Phase 4 Step B: G2 coverage, G3 risk, and the G1 earlier-ledger sha256 check (Phase4_registration.md section 7).

  python Book1A/Phase4/stepB/g2_g3_check.py <log path>

Read-only. Exit 1 on any G2 / G3 / earlier-ledger failure. Written in Step A (Nov 9, 2026).
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from book1a import sessions as S   # noqa: E402

R = ROOT / "book1a" / "Phase4" / "runs"
REG = [d.isoformat() for d in S.phase_sessions("phase4")]
out, bad = [], False
for f in ("phase4", "phase4_r3", "phase4_r4"):
    m = json.loads((R / f / "run_manifest.json").read_text())
    ss = m.get("sessions")
    ok = ss == REG
    out.append(f"G2 {f}: sessions {len(ss) if ss else None}, equal to the 52 registered: {ok}, commit {m.get('commit')}")
    bad |= not ok
cfg = json.loads((R / "phase4" / "daily_loop_config.json").read_text())
ok = cfg["sessions"] == REG
out.append(f"G2 A0 daily_loop sessions: {len(cfg['sessions'])} {ok}"); bad |= not ok
r4m = json.loads((R / "phase4_r4" / "run_manifest.json").read_text())
ok = r4m.get("candidate_days") == REG
out.append(f"G2 R4 candidate_days: {len(r4m.get('candidate_days') or [])} {ok}"); bad |= not ok
for f in ("phase4_stress_lat1000", "phase4_stress_slip2", "phase4_stress_slip4"):
    m = json.loads((R / f / "stress_manifest.json").read_text())
    ok = m["sessions"] == REG
    out.append(f"G2 {f}: sessions {len(m['sessions'])} {ok}, commit {m.get('commit')}"); bad |= not ok

for lab, p in (("R3", R / "phase4_r3" / "R3_M0_ledger.csv"), ("R4", R / "phase4_r4" / "R4_M0_ledger.csv")):
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    non = [r["trade_id"] for r in rows if r["risk_decision"] != "ACCEPT"]
    viol = [r["trade_id"] for r in rows if float(r["planned_risk_usd"]) > float(r["risk_budget_usd"]) + 1e-9]
    out.append(f"G3 {lab}: rows {len(rows)}, non-ACCEPT ledger rows {len(non)}, planned-risk violations {len(viol)} {viol}, "
               f"risk_impl {sorted({r['risk_impl_version'] for r in rows})}")
    bad |= bool(viol) or bool(non) or {r["risk_impl_version"] for r in rows} - {"risk-c3-v2"} != set()

REGISTERED = {  # Phase 1 and Phase 2 (Phase 3 G1) and Phase 3 (Phase3_report.md section 9) ledgers
    "Book1A/Phase1/runs/phase1/R1_A0_full.csv": "b4a2108fa2ab531ef84e1a2933d05fafb8e4519f6674ee8857f0cd79c344b21c",
    "Book1A/Phase1/runs/phase1/R2_C1_full.csv": "6123f88e7a62242b559e89a385b7749e67d6d2d433108cb839524a37c606842e",
    "Book1A/Phase1/runs/phase1_r3_c3v2/R3_M0_ledger.csv": "f413d15f4dad259d908390f6fcff659490f61cd5c9ce5a0f14a1bbeb486e71d1",
    "Book1A/Phase1/runs/phase1_r4_c3v2/R4_M0_ledger.csv": "b4510aabf2c750f6b3d0cb6f53de274989ed8acbc90d14c0dee9532a5ee5b409",
    "Book1A/Phase2/runs/phase2/R1_A0_full.csv": "7c0ea1ecdc566d927fdbb533b37aab36827ccf5d33a731e72e112eb3774d24f8",
    "Book1A/Phase2/runs/phase2/R2_C1_full.csv": "a9f06934eae85ef199b26fc372b20d107e8d0f5d3bced85452ec4e07d6b3451d",
    "Book1A/Phase2/runs/phase2_r3/R3_M0_ledger.csv": "6d938f834ac4b10beb72a29f3171f7243a0fe8e1da2ef52815b5b0e94d1ac921",
    "Book1A/Phase2/runs/phase2_r4/R4_M0_ledger.csv": "478dbb3374ef5ac5f684c397f4e350e350b2b7a9cf02a014e4582c5fd2299b83",
    "book1a/Phase3/runs/phase3/R1_A0_full.csv": "3a6314dd39318cb26005aa4263e099afbe5d9d2e35aa57e525eb3ac1c49a2784",
    "book1a/Phase3/runs/phase3/R2_C1_full.csv": "e6c92b2274a969017dc6e89690f693d92a772ce43ee1b0d666ff7e7d397a0769",
    "book1a/Phase3/runs/phase3_r3/R3_M0_ledger.csv": "0b1ed31db1b4d8e72b69dc5b1c8f6943bbad839046a3346f04a7a7f7eafe1b38",
    "book1a/Phase3/runs/phase3_r4/R4_M0_ledger.csv": "0e053e6f88e8ac31bc7c49d5906bb6692b0b089dd6d47601284d19c447fdc7d2",
    "book1a/Phase3/runs/phase3_r4_c2/R4_M0_ledger.csv": "9fbdc4289a4a5fc4a1014cfa86441e74123df6dfe90dc315aee20eb806aa20a2",
}
for p, h in REGISTERED.items():
    got = hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
    out.append(f"{got} *{p} registered_equal={got == h}")
    bad |= got != h
out.append("G2 / G3 / earlier ledgers: " + ("FAIL" if bad else "OK"))
text = "\n".join(out) + "\n"
Path(sys.argv[1]).write_text(text, encoding="utf-8")
print(text)
sys.exit(1 if bad else 0)
