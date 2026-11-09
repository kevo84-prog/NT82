#!/usr/bin/env bash
# Phase 4 Step B stage 2 (Phase4_registration.md sections 2-7): G1 checks, G4 draw, report card, review, Phase 4 gate,
# exit steps. Each step after a HEAD / clean record (HEAD = the commit of tag book1a-phase4-frozen). Written in Step A.
set -u
cd /k/Book1A_runner/code
export BOOK1_ROOT='K:\Book1A_inputs' PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
P=../.venv/Scripts/python.exe
R=book1a/Phase4/runs
R3P=book1a/Phase3/runs
G=$R/g1
PL=book1a/Phase4/plans_phase4
GEX='K:\Book1A_inputs\gex_levels_block1.csv'
TAG=$(git rev-parse 'book1a-phase4-frozen^{commit}') || { echo "STOP: no tag book1a-phase4-frozen"; exit 3; }
mkdir -p $G/unit_tests

head_rec() {
  local h s n
  h=$(git rev-parse HEAD); s=$(git status --porcelain); n=$(printf "%s" "$s" | grep -c . || true)
  printf "%s\nstatus_lines=%s\n%s\n" "$h" "$n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$R/stepB_head_$1.txt"
  if [ "$h" != "$TAG" ] || [ "$n" != "0" ]; then echo "STOP: HEAD $h (tag $TAG) status_lines $n before $1"; exit 3; fi
}
step() {
  local name=$1 log=$2; shift 2
  head_rec "$name"
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  "$@" > "$log" 2>&1
  local rc=$?
  echo "=== $name exit $rc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  [ $rc -eq 0 ] || { echo "STOP: $name failed (see $log)"; exit $rc; }
}

step unit_tests $G/unit_tests/unit_tests_phase4.log $P -m unittest discover -s book1a/tests -t .
step audit_R1 $G/audit_R1.log $P -m book1a.audit_run $R/phase4 $PL $R/phase4/R1_A0_full.csv $G/audit_R1
step audit_R2 $G/audit_R2.log $P -m book1a.audit_run $R/phase4 $PL $R/phase4/R2_C1_full.csv $G/audit_R2
step audit_R3 $G/audit_R3.log $P -m book1a.audit_run $R/phase4_r3 $PL $R/phase4_r3/R3_M0_ledger.csv $G/audit_R3
step audit_R4 $G/audit_R4.log $P -m book1a.audit_run $R/phase4_r4 $PL $R/phase4_r4/R4_M0_ledger.csv $G/audit_R4
step plan_hashes $G/plan_hashes_check.log $P -m book1a.phase4_plan_hashes --plans $PL --maps $R/maps_phase4 --out book1a/Phase4/plan_hashes_phase4.md --check
step g1_plans $G/g1_plans_console.log $P Book1A/Phase4/stepB/g1_plans_check.py $G/g1_plans.log
step g2_g3 $G/g2_g3_console.log $P Book1A/Phase4/stepB/g2_g3_check.py $G/g2_g3.log
step g4 $R/g4_console.log $P -m book1a.g4_draw --phase phase4 --r1 $R/phase4/R1_A0_full.csv --r2 $R/phase4/R2_C1_full.csv \
     --r3 $R/phase4_r3/R3_M0_ledger.csv --r4 $R/phase4_r4/R4_M0_ledger.csv --out book1a/Phase4/checker_input/g4_sample.csv
ST=""
for k in lat1000 slip2 slip4; do
  ST="$ST $k:R1=$R/phase4_stress_$k/R1_A0_full.csv $k:R2=$R/phase4_stress_$k/R2_C1_full.csv $k:R3=$R/phase4_stress_$k/R3_M0_ledger.csv $k:R4=$R/phase4_stress_$k/R4_M0_ledger.csv"
done
step report $R/report_console.log $P -m book1a.phase2_report --phase phase4 \
     --ledger R1=$R/phase4/R1_A0_full.csv R2=$R/phase4/R2_C1_full.csv R3=$R/phase4_r3/R3_M0_ledger.csv R4=$R/phase4_r4/R4_M0_ledger.csv \
     --attempts R3=$R/phase4_r3/R3_attempts.csv R4=$R/phase4_r4/R4_attempts.csv --stress $ST --gex "$GEX" --out $R/phase4_report_card.json
step review $R/phase4_review_console.log $P -m book1a.phase2_review_apply --phase phase4 --a0-run $R/phase4 --r3-run $R/phase4_r3 \
     --r4-run $R/phase4_r4 --diag $R/phase4_diag --gex "$GEX" --plans $PL --plan-hashes book1a/Phase4/plan_hashes_phase4.md --out $R/phase4_review
step gate $R/phase4_gate_console.log $P -m book1a.phase4_gate --r1 $R/phase4/R1_A0_full.csv --r2 $R/phase4/R2_C1_full.csv \
     --r3 $R/phase4_r3/R3_M0_ledger.csv --r4 $R/phase4_r4/R4_M0_ledger.csv --phase3-card $R3P/phase3_report_card.json --out $R/phase4_gate/phase4_gate.json
step mj_phase4 $R/mj_phase4_console.log $P -m book1a.mj_steps --phase phase4 --ledger R4=$R/phase4_r4/R4_M0_ledger.csv \
     --ledger R1=$R/phase4/R1_A0_full.csv --diag $R/phase4_diag --out $R/mj_steps/mj_steps_phase4.json
step mj_phase3 $R/mj_phase3_console.log $P -m book1a.mj_steps --phase phase3 --ledger R4=$R3P/phase3_r4/R4_M0_ledger.csv \
     --ledger R1=$R3P/phase3/R1_A0_full.csv --diag $R3P/phase3_diag_17ac9cd --out $R/mj_steps/mj_steps_phase3.json
echo "STAGE 2 DONE"
