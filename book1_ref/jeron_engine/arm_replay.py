"""Arm replay engine (design step 8; JE 0.5, Oct 26 2026).

Replays a day's trading decisions from the strategy's own log, with an arm's rule applied, so an arm is a full replay
of the day (selection, confirmation, position state, daily limits), not a filter on finished trades.

What it replays, exactly as JeronOrderFlowStrategy S1.4 does it (source lines in brackets):
  1. Per-bar selection [FlushBarCandidates 2747]: on each bar and direction the best candidate is kept and the others
     become SHADOW rows. An arm vetoes candidates BEFORE this step, so when it vetoes the logged winner, the next-best
     surviving shadow wins instead. Ranking [CompareCandidates 2734]: status rank (Qualified / AwaitConfirm / Pending 3,
     EventOnly 2, else 1), then location rank [2476] (frozen plan zone 4, power 3, qualified stack 2, minor stack 1),
     then reward:risk, then the earlier candidate.
  2. Queueing [2720, 2861]: a winning Qualified candidate is queued at its bar; a winning AwaitConfirm candidate is
     queued at its confirmation bar if the confirmation (CONFIRM / SHADOW_CONFIRM row) made it Qualified.
  3. TryEnter [4732] at the first tick after the queueing bar, with every block reason in the code's order:
     plan review, plan no-trade window, grade, entry hours, no target, max trades (min of 3 and the plan's max_trades),
     halt (2-loss streak / 400-tick daily loss, from realized ticks), already in a trade, price past stop / target and
     entry slippage at the decision tick (the first trade after the bar close).
  4. Exits come from the exit engine (exit_replay.run_model): M0 (A0's stop and target) or M2E, fill model v3.4 or
     v3.5. The position is busy until the exit; realized gross ticks update the day's loss streak and P/L.
Not replayed: changes to later candidate generation inside the strategy (a zone's retrigger state after its candidate
lost the bar). The candidate pool, shadows included, is A0's log.
Gate (check_a0): with no veto and M0 / v3.4, the replay must give A0's order attempts, block reasons and 35 trades
exactly, and the same fills as fills_model.csv.
"""
import collections, csv, datetime as dt
from pathlib import Path

import numpy as np

from . import fills, exit_replay as xr

ALLOWED_GRADES = {"A+", "B+", "B"}
NY_START, NY_END, LAST_ENTRY = 8 * 60 + 30, 15 * 60, 14 * 60 + 30
MAX_TRADES, MAX_LOSS_STREAK, MAX_DAILY_LOSS = 3, 2, 400
STATE_REASONS = {"MAX_TRADES_REACHED", "LOSS_STREAK_LIMIT", "DAILY_LOSS_LIMIT", "ALREADY_IN_TRADE"}
SLIPPAGE_TICKS = 12
TK = fills.TICK


def ts(s): return dt.datetime.fromisoformat(s[:23])


# ---------------------------------------------------------------- inputs
class Log:
    def __init__(self, run_dir):
        run = Path(run_dir)
        jofs = next((run / "strategy").glob("JOFS_*.csv"))
        self.rows = list(csv.DictReader(open(jofs, newline="", encoding="utf-8-sig")))
        for i, r in enumerate(self.rows): r["_i"] = i
        self.run = run
        self.qualified_stack = {r["LocationId"]: r["Detail"].startswith("QUALIFIED") for r in self.rows if r["RecordType"] == "IMBALANCE"}
        self.confirm = {}   # EventId -> CONFIRM / SHADOW_CONFIRM row
        for r in self.rows:
            if r["RecordType"] in ("CONFIRM", "SHADOW_CONFIRM"): self.confirm.setdefault(r["EventId"], r)
        self.attempts_logged = {r["EventId"]: r for r in self.rows if r["RecordType"] in ("ORDER", "ORDER_BLOCKED")}
        self.zones = collections.defaultdict(list)
        for r in self.rows:
            if r["RecordType"] == "ZONE_CREATED":
                t = ts(r["EvidenceTimeCT"])
                self.zones[t.date()].append((t, r["LocationType"], float(r["ZoneLo"]), float(r["ZoneHi"])))
        self.plans = {}
        for f in (run / "plans").glob("PreopenPlan_*.txt"):
            kv, nt = {}, []
            for line in open(f, encoding="utf-8"):
                line = line.strip()
                if line.startswith("no_trade="):
                    a, b = line[9:].split("-"); nt.append((hhmm(a), hhmm(b)))
                elif "=" in line and not line.startswith(("#", "zone=")):
                    k, v = line.split("=", 1); kv[k] = v
            kv["_no_trade"] = nt
            self.plans[kv.get("date")] = kv

    def groups(self):
        """Per-bar groups in log order: the logged winner (CANDIDATE) and its shadows."""
        shadows = collections.defaultdict(list)
        for r in self.rows:
            if r["RecordType"] == "SHADOW": shadows[r["ShadowOf"]].append(r)
        return [[r] + shadows.get(r["EventId"], []) for r in self.rows if r["RecordType"] == "CANDIDATE"]


def hhmm(s):
    h, m = s.strip().split(":"); return int(h) * 60 + int(m)


def loc_rank(log, r):
    lt = r["LocationType"]
    if lt.startswith("FROZEN_PREOPEN"): return 4
    if "POWER" in lt: return 3
    return 2 if log.qualified_stack.get(r["LocationId"], False) else 1


def status_rank(s): return 3 if s in ("Qualified", "AwaitConfirm", "Pending") else (2 if s == "EventOnly" else 1)


def rank_key(log, r):
    # reward:risk at full precision (the logged RewardRisk is rounded to 2 decimals, which can hide the winner of a tie)
    try:
        d = 1 if r["Direction"] == "Long" else -1
        e, s, t = float(r["EntryRef"]), float(r["StopAnchor"]), float(r["TargetPrice"])
        risk = d * (e - s)
        rr = d * (t - e) / risk if t > 0 and risk > 0 else float("-inf")
    except ValueError:
        rr = float("-inf")
    return (status_rank(r["CandidateStatus"]), loc_rank(log, r), rr, -int(r["EventId"].rsplit("-", 1)[1]))


# ---------------------------------------------------------------- selection and queueing
def attempts(log, veto=None):
    """Order attempts in the arm's world: list of dict(event, t (queueing bar end), row (candidate or confirm row),
    cand (candidate row), order (log position))."""
    out = []
    for g in log.groups():
        alive = [r for r in g if not (veto and veto(r))]
        if not alive: continue
        best = max(alive, key=lambda r: rank_key(log, r))
        st = best["CandidateStatus"]
        if st == "Qualified":
            out.append(dict(event=best["EventId"], t=ts(best["EvidenceTimeCT"]), row=best, cand=best, order=best["_i"]))
        elif st == "AwaitConfirm":
            c = log.confirm.get(best["EventId"])
            if c is not None and c["CandidateStatus"] == "Qualified":
                out.append(dict(event=best["EventId"], t=ts(c["EvidenceTimeCT"]), row=c, cand=best, order=c["_i"]))
    out.sort(key=lambda a: (a["t"], a["order"]))
    return out


# ---------------------------------------------------------------- entry decision
def decision_tick(tape, t):
    i = np.searchsorted(tape.t, np.datetime64(t, "us"), side="right")
    return float(tape.p[i]) if i < len(tape.t) else None


def static_blocks(log, a, px):
    """TryEnter's block reasons that do not depend on the replay's own state, split into the parts before and after
    the state checks (to keep the code's order)."""
    r, t = a["row"], a["t"]
    m = t.hour * 60 + t.minute
    pre, post = [], []
    plan = log.plans.get(t.strftime("%Y-%m-%d"))
    if plan is None or t.time() < dt.time(8, 25): pre.append("NO_ACTIVE_PLAN")
    else:
        if plan.get("review") != "APPROVED": pre.append("PLAN_REVIEW_" + plan.get("review", ""))
        for w0, w1 in plan["_no_trade"]:
            if w0 <= m < w1: pre.append("PLAN_NO_TRADE_WINDOW"); break
    if r["Grade"] not in ALLOWED_GRADES and a["cand"]["Grade"] not in ALLOWED_GRADES: pre.append("GRADE_NOT_ALLOWED")
    if m < NY_START or m >= NY_END or m >= LAST_ENTRY: pre.append("OUTSIDE_ENTRY_HOURS")
    tgt = float(r["TargetPrice"] or 0)
    if tgt <= 0: pre.append("NO_TARGET")
    d = 1 if r["Direction"] == "Long" else -1
    stop, entry = float(r["StopAnchor"]), float(r["EntryRef"])
    if px is not None:
        if (px <= stop + TK) if d > 0 else (px >= stop - TK): post.append("PRICE_PAST_STOP")
        if tgt > 0 and ((px >= tgt - TK) if d > 0 else (px <= tgt + TK)): post.append("PRICE_PAST_TARGET")
        if SLIPPAGE_TICKS > 0 and abs(px - entry) > SLIPPAGE_TICKS * TK + 1e-9: post.append("ENTRY_SLIPPAGE")
    return pre, post, plan


# ---------------------------------------------------------------- RH1 retest path (Amendment 1)
RETEST_BARS, TOUCH_TICKS, STOP_BUFFER_TICKS = 15, 2, 2      # frozen v2.5 values (StepRetest, lines 3319-3388)
SESSION_END = dt.time(15, 0)


def retest_path(bars, cand, t, fail_ticks=2):
    """The frozen v2.5 retest path for an initiation candidate whose signal bar ends at t. Returns dict(outcome, at
    (bar end where the path ended), entry (confirm close), stop)."""
    d = 1 if cand["Direction"] == "Long" else -1
    lo, hi = float(cand["ZoneLo"]), float(cand["ZoneHi"])
    near, far = (hi, lo) if d > 0 else (lo, hi)
    tol = TOUCH_TICKS * TK
    target = float(cand["TargetPrice"] or 0)
    entry0, stop0 = float(cand["EntryRef"]), float(cand["StopAnchor"])
    risk0 = d * (entry0 - stop0)
    phase, extreme, mfe, last = 0, None, 0.0, t
    for n, (end, o, h, l, c) in enumerate(bars.after(t, RETEST_BARS), start=1):
        last = end
        mfe = max(mfe, (h - entry0) if d > 0 else (entry0 - l))
        touch = (l <= near + tol) if d > 0 else (h >= near - tol)
        failed = (c < far - fail_ticks * TK) if d > 0 else (c > far + fail_ticks * TK)
        if touch:
            phase = max(phase, 1)
            ex = l if d > 0 else h
            if extreme is None or d * (extreme - ex) > 0: extreme = ex
        if failed: return dict(outcome="RETEST_FAILED", at=end)
        if phase == 1 and ((c > near and c > o) if d > 0 else (c < near and c < o)):
            stop = extreme - STOP_BUFFER_TICKS * TK if d > 0 else extreme + STOP_BUFFER_TICKS * TK
            if target > 0 and d * (target - c) <= 0: return dict(outcome="NO_ROOM_TO_TARGET", at=end)
            return dict(outcome="RETEST_ENTERED", at=end, entry=c, stop=stop)
        if phase == 0 and target > 0 and ((h >= target) if d > 0 else (l <= target)): return dict(outcome="RAN_TO_TARGET", at=end)
        if end.time() >= SESSION_END:
            return dict(outcome="RETEST_NO_CONFIRM" if phase == 1 else "SESSION_END_NO_RETEST", at=end)
    if phase == 1: return dict(outcome="RETEST_NO_CONFIRM", at=last)
    return dict(outcome="RAN_AWAY" if risk0 > 0 and mfe >= risk0 else "NO_RETEST_WINDOW", at=last)


# ---------------------------------------------------------------- the replay
def replay(log, tape, veto=None, exit_model="M0", fill="v3.5", stop_slip=1, retest=None, crossed=None):
    """Returns dict(attempts=[...], trades=[...], retests=[...]). Each attempt: event, time, reasons ('' = ORDER).
    Each trade: event, date, signal_time (the candidate's queueing bar), entry_time, side, entry, exit, exit_time,
    reason, gross_ticks, net_ticks, risk_ticks, R, path ('immediate' or 'retest').
    retest = dict(bars=arms.MinuteBars, fail_ticks=2) switches on RH1 (Amendment 1); None = A0's immediate entries.
    crossed overrides v3.5's crossed-stop policy ("live_market" = M2E's report-only market-exit line)."""
    kw = dict(gap_fill=True, stop_delay_ms=250, crossed=crossed or "live") if fill == "v3.5" else {}
    if fill not in ("v3.4", "v3.5"): raise ValueError(fill)
    res_att, trades, retests = [], [], []
    day = None
    busy_until = None          # exit time of the open position
    pending_close = None       # (exit_time, gross ticks) applied when time passes it
    trades_today = loss_streak = 0
    pnl_today, halt = 0.0, ""

    def apply_close(now):
        nonlocal pending_close, loss_streak, pnl_today, halt
        if pending_close and pending_close[0] < now:
            g = pending_close[1]; pending_close = None
            pnl_today += g
            if g < 0: loss_streak += 1
            elif g > 0: loss_streak = 0
            if not halt:
                if pnl_today <= -MAX_DAILY_LOSS: halt = "DAILY_LOSS_LIMIT"
                elif loss_streak >= MAX_LOSS_STREAK: halt = "LOSS_STREAK_LIMIT"

    for a in attempts(log, veto):
        t = a["t"]
        if t.date() != day:
            if pending_close: apply_close(dt.datetime.max)
            day, busy_until, trades_today, loss_streak, pnl_today, halt = t.date(), None, 0, 0, 0.0, ""
        px = decision_tick(tape, t)
        i = np.searchsorted(tape.t, np.datetime64(t, "us"), side="right")
        now = tape.t[i].astype(dt.datetime) if i < len(tape.t) else t   # TryEnter runs on the first tick after the bar
        apply_close(now)
        pre, post, plan = static_blocks(log, a, px)
        limit = MAX_TRADES
        if plan is not None and plan.get("max_trades", "") not in ("", "-"):
            try: limit = min(limit, int(plan["max_trades"]))
            except ValueError: pass
        state = []
        if trades_today >= limit: state.append("MAX_TRADES_REACHED")
        if halt: state.append(halt)
        if busy_until is not None and busy_until >= now: state.append("ALREADY_IN_TRADE")
        reasons = pre + state + post
        res_att.append(dict(event=a["event"], time=t, reasons="|".join(reasons), px=px))
        if reasons: continue
        r = a["row"]
        side = 1 if r["Direction"] == "Long" else -1
        tr = dict(side=side, signal_end=t, stop=float(r["StopAnchor"]), target=float(r["TargetPrice"]))
        path = "immediate"
        if retest is not None and a["cand"]["SetupFamily"] == "INITIATION":
            # RH1: no immediate entry; the slot is held while the retest is armed
            p = retest_path(retest["bars"], a["cand"], t, retest.get("fail_ticks", 2))
            imm = xr.run_model("M0", tape, tr, log.zones[t.date()], stop_slip=stop_slip, **kw)
            rec = dict(event=a["event"], time=t, outcome=p["outcome"], at=p["at"], a0_immediate_R=imm["R"],
                       runner_missed=p["outcome"] not in ("RETEST_ENTERED", "RETEST_FAILED") and imm["R"] > 0,
                       regime=(plan or {}).get("gex_regime", ""))
            retests.append(rec)
            busy_until = p["at"]
            if p["outcome"] != "RETEST_ENTERED": continue
            te = p["at"]
            m_ = te.hour * 60 + te.minute
            px2 = decision_tick(tape, te)
            blk = []
            if m_ >= LAST_ENTRY or m_ >= NY_END: blk.append("OUTSIDE_ENTRY_HOURS")
            if px2 is not None:
                if (px2 <= p["stop"] + TK) if side > 0 else (px2 >= p["stop"] - TK): blk.append("PRICE_PAST_STOP")
                if (px2 >= tr["target"] - TK) if side > 0 else (px2 <= tr["target"] + TK): blk.append("PRICE_PAST_TARGET")
                if abs(px2 - p["entry"]) > SLIPPAGE_TICKS * TK + 1e-9: blk.append("ENTRY_SLIPPAGE")
            rec["entry_blocks"] = "|".join(blk)
            if blk: continue
            tr = dict(side=side, signal_end=te, stop=p["stop"], target=tr["target"])
            path = "retest"
        m = xr.run_model(exit_model, tape, tr, log.zones[t.date()], stop_slip=stop_slip, **kw)
        leg = m["legs"][0]
        trades_today += 1
        busy_until = leg["exit_time"]
        pending_close = (leg["exit_time"], leg["ticks"])
        trades.append(dict(event=a["event"], date=t.strftime("%Y-%m-%d"), signal_time=t.strftime("%H:%M:%S"),
                           entry_time=(tr["signal_end"] + dt.timedelta(milliseconds=fills.LATENCY_MS)),
                           side=r["Direction"], entry=m["entry"], exit=leg["exit"], exit_time=leg["exit_time"],
                           reason=leg["reason"], gross_ticks=leg["ticks"], net_ticks=m["net_ticks"],
                           risk_ticks=m["risk_ticks"], R=m["R"], path=path))
    return dict(attempts=res_att, trades=trades, retests=retests)


# ---------------------------------------------------------------- the gate
def _halt_norm(reasons):
    return "|".join("HALT" if x in ("DAILY_LOSS_LIMIT", "LOSS_STREAK_LIMIT") else x for x in reasons.split("|"))


def _static_same(r1, r2):
    s1, s2 = set(r1.split("|")) - STATE_REASONS - {""}, set(r2.split("|")) - STATE_REASONS - {""}
    return bool(s1) and s1 == s2


def check_a0(log, tape, fills_model_csv):
    """No veto, M0, v3.4: attempts, reasons, trades and fills must equal A0's log and fills_model.csv."""
    rep = replay(log, tape, veto=None, exit_model="M0", fill="v3.4")
    problems = []
    got = {a["event"]: a for a in rep["attempts"]}
    if set(got) != set(log.attempts_logged):
        problems.append(f"attempt sets differ: {len(set(got) - set(log.attempts_logged))} extra, {len(set(log.attempts_logged) - set(got))} missing")
    for e, lr in log.attempts_logged.items():
        g = got.get(e)
        if g is None: continue
        want = "" if lr["RecordType"] == "ORDER" else lr["Reasons"]
        if g["reasons"] != want:
            # The halt is computed from the fill model's realized ticks, the strategy's from its own fills, so the two
            # halts can carry different names (e.g. Jan 9, 2026: strategy -399 ticks = 2-loss streak; v3.4 model -405
            # ticks = daily loss limit). Both stop entries for the rest of the day, so only the name differs: listed
            # in rep["halt_label_diffs"], not a problem.
            # Also name-only: both are blocked by the same state-independent reasons (entry hours, plan, grade, target,
            # price checks) and differ only in position-state reasons, e.g. Mar 17, 2026 14:55: the fill model flattens
            # at 14:55, the strategy at 14:54, so only the replay adds ALREADY_IN_TRADE to an attempt blocked anyway.
            if _halt_norm(g["reasons"]) == _halt_norm(want) or _static_same(g["reasons"], want):
                rep.setdefault("halt_label_diffs", []).append(f"{e} {lr['EvidenceTimeCT'][:16]}: '{g['reasons']}' vs logged '{want}'")
            else: problems.append(f"{e} {lr['EvidenceTimeCT'][:16]}: reasons '{g['reasons']}' vs logged '{want}'")
        if ts(lr["EvidenceTimeCT"]) != g["time"]: problems.append(f"{e}: time {g['time']} vs logged {lr['EvidenceTimeCT']}")
        dtick = lr["Detail"].split("decision tick=")[1].split()[0] if "decision tick=" in lr["Detail"] else None
        if dtick is not None and g["px"] is not None and abs(float(dtick) - g["px"]) > 1e-9:
            problems.append(f"{e}: decision tick {g['px']} vs logged {dtick}")
    fm = {r["event"]: r for r in csv.DictReader(open(fills_model_csv, encoding="utf-8"))}
    if {t["event"] for t in rep["trades"]} != set(fm): problems.append("trade set differs from fills_model.csv")
    for t in rep["trades"]:
        f = fm.get(t["event"])
        if f and (abs(t["entry"] - float(f["base_entry"])) > 1e-9 or abs(t["exit"] - float(f["base_exit"])) > 1e-9
                  or t["reason"] != f["base_reason"]):
            problems.append(f"{t['event']}: fill differs from fills_model.csv")
    return rep, problems
