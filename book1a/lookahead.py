"""Book 1A timestamp and lookahead audit (checklist P0.13).

Every level, zone, indicator and tag carries available_at. The audit asserts, for every entry,
that available_at < the decision timestamp of every input the decision used. It is a generic
registry so the same check covers swing confirmation (15 bars after the swing), the 08:10 VWAP
(available 08:10:00 CT), GEX inputs (D-1 report, published before 11 PM ET on D-1), map zones
(08:10 CT) and L2 seconds (only seconds completed before the decision).

Rule: available_at must be strictly before decision_ts. Equality is a violation (a value that
becomes known at the decision instant was not usable when the decision was made).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

VERSION = "lookahead-v1.0"
CT = ZoneInfo("America/Chicago")


def parse_ts(v) -> datetime:
    if isinstance(v, datetime):
        if v.tzinfo is None:
            raise ValueError(f"naive datetime: {v}")
        return v
    dt = datetime.fromisoformat(str(v))
    if dt.tzinfo is None:
        raise ValueError(f"naive timestamp string: {v}")
    return dt


@dataclass(frozen=True)
class Input:
    name: str
    kind: str                 # LEVEL | ZONE | INDICATOR | TAG | GEX | L2 | SWING | PLAN
    available_at: datetime
    source: str = ""


@dataclass
class Decision:
    decision_id: str
    decision_ts: datetime
    inputs: List[Input] = field(default_factory=list)


@dataclass(frozen=True)
class Violation:
    decision_id: str
    decision_ts: str
    input_name: str
    kind: str
    available_at: str
    lead_seconds: float       # available_at - decision_ts (>= 0 means lookahead)


class LookaheadAudit:
    def __init__(self):
        self.decisions: Dict[str, Decision] = {}
        self.missing: List[tuple] = []     # (decision_id, input_name) with no available_at

    def register(self, decision_id: str, decision_ts, name: str, kind: str, available_at, source: str = "") -> None:
        d = self.decisions.setdefault(decision_id, Decision(decision_id, parse_ts(decision_ts)))
        if available_at is None:
            self.missing.append((decision_id, name))
            return
        d.inputs.append(Input(name, kind, parse_ts(available_at), source))

    def violations(self) -> List[Violation]:
        out = []
        for d in self.decisions.values():
            for i in d.inputs:
                if not (i.available_at < d.decision_ts):
                    out.append(Violation(d.decision_id, d.decision_ts.isoformat(), i.name, i.kind,
                                         i.available_at.isoformat(), (i.available_at - d.decision_ts).total_seconds()))
        return out

    def passed(self) -> bool:
        return not self.violations() and not self.missing

    def write_log(self, path: str) -> dict:
        v = self.violations()
        n_inputs = sum(len(d.inputs) for d in self.decisions.values())
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["decision_id", "decision_ts", "input_name", "kind", "available_at", "lead_seconds", "status"])
            for d in self.decisions.values():
                for i in d.inputs:
                    ok = i.available_at < d.decision_ts
                    w.writerow([d.decision_id, d.decision_ts.isoformat(), i.name, i.kind, i.available_at.isoformat(),
                                (i.available_at - d.decision_ts).total_seconds(), "OK" if ok else "VIOLATION"])
            for did, name in self.missing:
                w.writerow([did, self.decisions[did].decision_ts.isoformat(), name, "", "", "", "MISSING_AVAILABLE_AT"])
        return {"decisions": len(self.decisions), "inputs": n_inputs, "violations": len(v), "missing": len(self.missing)}


# ---- standard available_at rules -------------------------------------------------------------
def swing_available_at(swing_bar_close: datetime, bars_after: int = 15) -> datetime:
    """A swing is known only when the 15th bar after it has closed (AMT PO-1 step 1)."""
    from datetime import timedelta
    return swing_bar_close + timedelta(minutes=bars_after)


def gex_available_at(session_date) -> datetime:
    """D-1 report, published before 11 PM ET on D-1 (design v3.5 GEX front rule): 23:00 ET on D-1."""
    from datetime import date, time, timedelta
    d1 = session_date - timedelta(days=1)
    return datetime.combine(d1, time(23, 0), tzinfo=ZoneInfo("America/New_York"))


def map_available_at(session_date) -> datetime:
    from datetime import time
    return datetime.combine(session_date, time(8, 10), tzinfo=CT)


def l2_second_available_at(second_start: datetime) -> datetime:
    """A one-second book state is usable once that second has completed."""
    from datetime import timedelta
    return second_start + timedelta(seconds=1)
