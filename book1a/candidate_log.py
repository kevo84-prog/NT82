"""Book 1A R4 candidate log (checklist P0.11).

For every CANDIDATE and SHADOW row of an A0 strategy run (the S1.4 log, unchanged) it writes one row with:
  the S1.4 gate results (Reasons, status, grade), the RH1 state (frozen v2.5 retest path, 15 bars / 2 ticks),
  the T8 and L1 checks (Book 1 arms.t8 / arms.l1, unchanged), FZ1 logged but never applied, the Book 1A
  pre-trade risk decision (C3 / U3, per-trade budget; the day budget is applied in the replay), the single-print
  gate note (U2: S1.4's large print stays the gate; the Quantower-style rebuild is logged only), and every Phase 5
  tag. A tag that cannot be measured from the log is written as the string "null", never left missing; the column
  tag_status lists which tags were measurable for the row.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from book1a import risk as R
from book1a.book1_import import jeron_engine  # noqa: F401  (adds book1_ref to sys.path)
from jeron_engine import arm_replay as AR, arms as A

VERSION = "candidate-log-v1.1"   # v1.1: optional extra columns per row (R4 plan identity)
TICK = 0.25
NY_START = 8 * 60 + 30

# Phase 5 tags (E-Footprint_Imbalances doc + shared rules). S1.4 columns are copied when present.
S14_TAGS = ["fight_flag", "fight_kind", "trapped_passive", "trapped_passive_kind", "passive_would_rescue",
            "delta_pct_vs_session", "delta_pct_session_avg", "delta_rank_20", "ema21_aligned", "cvd_avg_aligned",
            "delta", "delta_pct", "imbalance_flag", "trapped_side_flag", "displacement"]
BOOK1A_TAGS = ["vwap_grade", "reentry_blocked", "stop_and_reverse", "fight", "wait_for_response", "r_tp1", "r_tp2", "r_run",
               "light_proof", "light_proof_first_touch_3src", "delta_vs_session_jeron", "delta_vs_session_ratio",
               "passive_trap", "ema_cvd_aligned", "counter_context_proof", "cvd_div", "cvd_div_timing", "breakout_speed",
               "retest_at_new_imb", "exhaustion", "tf_aligned", "stacked_imbalances", "wick_stop_R", "power_trade_qt",
               "fz1_would_veto", "first_touch", "test_number", "gex_regime", "add_opportunity"]
COLUMNS = ["event", "date", "signal_time_ct", "direction", "setup_family", "status", "is_shadow", "shadow_of", "grade",
           "location_type", "location_id", "zone_lo", "zone_hi", "entry_ref", "stop", "target", "reward_risk",
           "gate_reasons", "gates_pass", "rh1_state", "rh1_at", "rh1_entry", "rh1_stop", "t8_veto", "l1_dist_pts", "l1_veto",
           "fz1_would_veto_applied", "single_print_gate", "risk_decision", "risk_contracts", "risk_estimate_usd", "stop_ticks"] \
          + S14_TAGS + BOOK1A_TAGS + ["tag_status"]


def _null(v) -> str:
    return "null" if v in (None, "") else str(v)


def build(run_dir, tape_path, out_csv, sessions: Optional[List[str]] = None, ny_only: bool = True,
          row_extra: Optional[Callable[[dict], dict]] = None, extra_columns: Sequence[str] = ()) -> int:
    """row_extra(S1.4 row) -> extra columns for that row (R4: the Book 1A plan version, sha256 and zone fields);
    it may raise to stop the build."""
    log = AR.Log(run_dir)
    bars = A.MinuteBars(tape_path)
    t8 = A.t8(log, bars)
    l1 = A.l1(log)
    fz1 = A.fz1(log)
    plans = log.plans
    rows_out = []
    for r in log.rows:
        if r["RecordType"] not in ("CANDIDATE", "SHADOW"):
            continue
        d = r["EvidenceTimeCT"][:10]
        if sessions and d not in sessions:
            continue
        t = AR.ts(r["EvidenceTimeCT"])
        if ny_only and (t.hour * 60 + t.minute) < NY_START:
            continue
        reasons = r.get("Reasons", "")
        try:
            e, s = float(r["EntryRef"]), float(r["StopAnchor"])
            stop_ticks = int(round(abs(e - s) / TICK))
        except (ValueError, KeyError):
            stop_ticks = None
        if stop_ticks is not None:
            n = R.size_for(stop_ticks, R.DEFAULT.per_trade_budget_cents)
            dec = "ACCEPT" if n >= 1 else "RISK_REJECT:PER_TRADE_BUDGET"
            est = R.estimate_risk(stop_ticks, max(n, 1))
        else:
            n, dec, est = None, "null", None
        rh = {"outcome": "null", "at": None, "entry": None, "stop": None}
        if r.get("SetupFamily") == "INITIATION" and r.get("ZoneLo") and r.get("ZoneHi"):
            try:
                rh = AR.retest_path(bars, r, t, 2)
            except (ValueError, KeyError):
                pass
        l1d = l1.dist(r) if A.intraday(r) else None
        plan = plans.get(d) or {}
        tags: Dict[str, str] = {k: _null(r.get(k)) for k in S14_TAGS}
        for k in BOOK1A_TAGS:
            tags[k] = "null"
        tags["fz1_would_veto"] = "Y" if fz1(r) else "N"
        tags["gex_regime"] = _null(plan.get("gex_regime"))
        tags["fight"] = _null(r.get("fight_flag"))
        tags["passive_trap"] = _null(r.get("trapped_passive"))
        if r.get("ema21_aligned") and r.get("cvd_avg_aligned"):
            tags["ema_cvd_aligned"] = "Y" if (r["ema21_aligned"] == "Y" and r["cvd_avg_aligned"] == "Y") else "N"
        if r.get("delta_pct_vs_session"):
            tags["delta_vs_session_ratio"] = r["delta_pct_vs_session"]
        measurable = [k for k, v in tags.items() if v != "null"]
        rows_out.append({
            "event": r["EventId"], "date": d, "signal_time_ct": r["EvidenceTimeCT"][11:23], "direction": r["Direction"],
            "setup_family": r.get("SetupFamily", ""), "status": r.get("CandidateStatus", ""), "is_shadow": int(r["RecordType"] == "SHADOW"),
            "shadow_of": r.get("ShadowOf", ""), "grade": r.get("Grade", ""), "location_type": r.get("LocationType", ""),
            "location_id": r.get("LocationId", ""), "zone_lo": r.get("ZoneLo", ""), "zone_hi": r.get("ZoneHi", ""),
            "entry_ref": r.get("EntryRef", ""), "stop": r.get("StopAnchor", ""), "target": r.get("TargetPrice", ""),
            "reward_risk": r.get("RewardRisk", ""), "gate_reasons": reasons, "gates_pass": int(reasons in ("", "OK")),
            "rh1_state": rh.get("outcome", "null") if r.get("SetupFamily") == "INITIATION" else "N/A_RESPONSE",
            "rh1_at": _null(rh.get("at")), "rh1_entry": _null(rh.get("entry")), "rh1_stop": _null(rh.get("stop")),
            "t8_veto": "Y" if t8(r) else "N", "l1_dist_pts": _null(l1d), "l1_veto": "Y" if l1(r) else "N",
            "fz1_would_veto_applied": "LOGGED_ONLY", "single_print_gate": "S1.4_LARGE_PRINT (U2: Quantower rebuild logged only)",
            "risk_decision": dec, "risk_contracts": _null(n), "risk_estimate_usd": _null(None if est is None else round(est, 2)),
            "stop_ticks": _null(stop_ticks), **tags, "tag_status": "measurable=" + ",".join(measurable),
            **(row_extra(r) if row_extra else {}),
        })
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS + list(extra_columns), extrasaction="ignore")
        w.writeheader(); w.writerows(rows_out)
    return len(rows_out)
