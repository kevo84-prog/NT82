"""Plan hash table after the Nov 5 htf_acceptance change (plan-v2.4-book1a-v1.4).

  python book1a/hand_checks/plan_hashes_nov5.py . Book1A/Phase0/plan_hashes_2026-11-05.md Book1A/Phase0/plan_hashes_2026-11-05_before.txt

Run before the rebuilt plans are committed (it compares with the plan files at git HEAD). Reads only plan columns of R4 rows."""
import csv, hashlib, json, subprocess, sys
from pathlib import Path

root = Path(sys.argv[1]); out = Path(sys.argv[2])
before = {}
for line in Path(sys.argv[3]).read_text().splitlines():
    d, f, h = line.split(); before[(d, f)] = h
sha = lambda b: hashlib.sha256(b).hexdigest()
KEYS = ("context=", "market_context=", "context_base=", "htf_acceptance=", "draw_status=", "draw=", "review=",
        "invalidate_below=", "invalidate_above=")
rows = []
for folder in ("Book1A/Phase0/plans_phase1", "Book1A/Phase0/hand_checks", "Book1A/Phase0/hand_check_pack/plans"):
    for f in sorted((root / folder).glob("PreopenPlan_*_book1a.txt")):
        day = f.name.split("_")[1]
        t = f.read_bytes(); j = f.with_suffix(".json").read_bytes()
        old = subprocess.run(["git", "show", f"HEAD:{folder}/{f.name}"], cwd=root, capture_output=True).stdout.decode("utf-8")
        new = t.decode("utf-8")
        ol = [l for l in old.splitlines()[1:]]; nl = [l for l in new.splitlines()[1:]]
        added = [l for l in nl if l not in ol]; removed = [l for l in ol if l not in nl]
        new_keys_only = all(l.startswith(("context_base=", "htf_acceptance=", "# htf_acceptance:", "htfval_state=", "htfvah_state="))
                            for l in added) and not removed
        kv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in nl if "=" in l and not l.startswith("#")}
        okv = {l.split("=", 1)[0]: l.split("=", 1)[1] for l in ol if "=" in l and not l.startswith("#")}
        changed = [k.rstrip("=") for k in KEYS if kv.get(k.rstrip("=")) != okv.get(k.rstrip("="))
                   and k not in ("context_base=", "htf_acceptance=")]
        zone_side = sum(1 for a in added if a.startswith("zone="))
        ladder = sum(1 for a in added if a.startswith("ladder="))
        if new_keys_only:
            ch = "new keys only (context_base, htf_acceptance, htfval_state, htfvah_state, label comment)"
        else:
            ch = ("; ".join(f"{k} {okv.get(k, '-')} -> {kv.get(k, '-')}" for k in changed) or "-") + \
                 f"; zone lines changed {zone_side}; ladder lines changed {ladder}"
        rows.append((folder.replace("Book1A/Phase0/", ""), day, sha(t), sha(j), before.get((folder, f.name), "?"),
                     kv.get("context_base"), kv.get("htf_acceptance"), kv.get("market_context"), ch.replace("|", r"\|")))
# R4 rows vs the plan files
man = json.loads((root / "Book1A/Phase0/P0.12/R4_plan_manifest.json").read_text())
L = ["# Book 1A plan hashes after the htf_acceptance change (plan-v2.4-book1a-v1.4, plan-fields-v1.1; Nov 5, 2026)", "",
     "Code: the rule and tests at commit 0e0210d (committed before any real day was run). Every plan header names the "
     "builder version, so every plan's sha256 changed; every plan gains context_base=, htf_acceptance=, htfval_state=, "
     "htfvah_state= and the label comment line. The previous table (plan v1.3) is `plan_hashes_2026-11-04.md`.", "",
     "| folder | day | plan .txt sha256 | sidecar .json sha256 | plan .txt sha256 before (v1.3) | context_base | htf_acceptance | market_context | text change besides the header |",
     "|---|---|---|---|---|---|---|---|---|"]
L += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
bad = 0; n = 0
p1 = {r[1]: r for r in rows if r[0] == "plans_phase1"}
for fn in ("Book1A/Phase0/P0.12/R4_M0_phase1_ledger.csv", "Book1A/Phase0/P0.11_candidates_phase1.csv"):
    with open(root / fn, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            sess = (row.get("plan_id") or "")[:10]
            if not row.get("plan_sha256"):
                continue
            n += 1
            r = p1.get(sess)
            if r is None or row["plan_sha256"] != r[2] or row.get("plan_version") != "plan-v2.4-book1a-v1.4":
                bad += 1
L += ["", f"R4 rows checked against these files (P0.12 ledger + P0.11 candidates): {n} rows, {bad} with a wrong plan version or sha256."]
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(n, bad)
