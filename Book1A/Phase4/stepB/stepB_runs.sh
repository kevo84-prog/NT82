#!/usr/bin/env bash
# Phase 4 Step B stage 1 (Phase4_registration.md section 1): the registered run commands, each after a HEAD / clean-status
# record. HEAD must equal the commit of tag book1a-phase4-frozen exactly; stops on the first failure. Written in Step A.
set -u
cd /k/Book1A_runner/code
export BOOK1_ROOT='K:\Book1A_inputs' PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
P=../.venv/Scripts/python.exe
R=book1a/Phase4/runs
PL=book1a/Phase4/plans_phase4
TAG=$(git rev-parse 'book1a-phase4-frozen^{commit}') || { echo "STOP: no tag book1a-phase4-frozen"; exit 3; }
DAYS=$($P -c "from book1a import sessions as S; print(' '.join(d.isoformat() for d in S.phase_sessions('phase4')))")

head_rec() {   # $1 = name
  local h s n
  h=$(git rev-parse HEAD); s=$(git status --porcelain); n=$(printf "%s" "$s" | grep -c . || true)
  printf "%s\nstatus_lines=%s\n%s\n" "$h" "$n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$R/stepB_head_$1.txt"
  if [ "$h" != "$TAG" ] || [ "$n" != "0" ]; then echo "STOP: HEAD $h (tag $TAG) status_lines $n before $1"; exit 3; fi
}
step() {       # $1 = name, rest = command
  local name=$1; shift
  head_rec "$name"
  echo "=== $name start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  "$@" > "$R/${name}_console.log" 2>&1
  local rc=$?
  echo "=== $name exit $rc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  [ $rc -eq 0 ] || { echo "STOP: $name failed"; exit $rc; }
}

step phase4 $P -m book1a.run_r1_r2 --phase phase4 --fill v3.5 --block1 'K:\Book1A_inputs' --out $R/phase4
step phase4_r3 $P -m book1a.run_r3 --block1 'K:\Book1A_inputs' --a0-run $R/phase4 --out $R/phase4_r3
step phase4_r4 $P -m book1a.run_r4 --block1 'K:\Book1A_inputs' --a0-run $R/phase4 --plans $PL --phase phase4 --out $R/phase4_r4 --candidate-days $DAYS
for s in lat1000 slip2 slip4; do
  step phase4_stress_$s $P -m book1a.run_stress --block1 'K:\Book1A_inputs' --a0-run $R/phase4 --r4-run $R/phase4_r4 --plans $PL --stress $s --out $R/phase4_stress_$s
done
step phase4_diag $P -m book1a.diag_phase1b --runs $R --folders phase4 phase4_r3 phase4_r4 --d5-days --plans $PL --gex 'K:\Book1A_inputs\gex_levels_block1.csv' --inputs 'K:\Book1A_inputs' --out $R/phase4_diag
echo "ALL RUNS DONE"
