"""Design v3.4 fill model on real ticks, and parity gate 5 (JE 0.2, Oct 25 2026).

Fill model (frozen before Phase 1):
  entry   market order sent when the signal bar closes, filled LATENCY_MS (250) later at the best ask (buy) /
          best bid (sell) known at that moment (the quote that came with the last trade at or before it)
  target  limit: fills only when a trade prints 1 tick THROUGH the target; fill price = target
  stop    stop-market: triggers when a trade prints at or through the stop; fill = stop -/+ STOP_SLIP ticks
          (base 1; stress 2 and 4)
  tie     stop and target reached in the same timestamp = stop
  flatten 14:55 CT at the bid (long) / ask (short); the session-close exit after 15:00 (not reached on Oct 8)

gate5(nt_log, tape): for every trade NinjaTrader Sim filled (ORDER + FILL rows of a JOFS log), the model's
entry and exit prices must be within 1 tick of NinjaTrader's.
"""
import csv, datetime as dt, gzip
from pathlib import Path
import numpy as np

TICK = 0.25
LATENCY_MS = 250
STOP_SLIP = 1
FLATTEN = dt.time(14, 55)


class Tape:
    """Trades with the quote that came with each (NT Last export .txt, or a harness tape .csv/.csv.gz)."""
    def __init__(self, path, start=None, end=None):
        from zoneinfo import ZoneInfo
        ct = ZoneInfo("America/Chicago")
        path = str(path)
        op = gzip.open if path.endswith(".gz") else open
        with op(path, "rt") as f:
            first = f.readline()
        if not (first[:8].isdigit() and first[8] == " " and ";" in first):
            self._load_csv(path, start, end)       # harness tape: chunked loader, same values, far less memory
            return
        T, P, B, A = [], [], [], []
        with op(path, "rt") as f:
            first = f.readline()
            nt = first[:8].isdigit() and first[8] == " " and ";" in first
            lines = [first] if nt else []
            def rows():
                yield from lines
                yield from f
            for line in rows():
                if nt:
                    p = line.rstrip().split(";")
                    utc = dt.datetime.strptime(p[0][:15], "%Y%m%d %H%M%S").replace(tzinfo=dt.timezone.utc) + dt.timedelta(microseconds=int(p[0][16:23]) // 10)
                    t = utc.astimezone(ct).replace(tzinfo=None)
                    pr, bi, ak = float(p[1]), float(p[2] or 0), float(p[3] or 0)
                else:
                    p = line.rstrip().split(",")
                    t = dt.datetime.fromisoformat(p[0][:26])
                    pr, bi, ak = float(p[1]), float(p[2] or 0), float(p[3] or 0)
                if start and t < start: continue
                if end and t >= end: break
                T.append(t); P.append(pr); B.append(bi); A.append(ak)
        self.t = np.array(T, dtype="datetime64[us]"); self.p = np.array(P); self.b = np.array(B); self.a = np.array(A)

    def _load_csv(self, path, start, end, chunk=4_000_000):
        """Harness tape (.csv / .csv.gz with header): the same arrays as the line loop (time cut to microseconds,
        empty bid / ask = 0, rows before start skipped, stop at the first row at or after end), read in chunks so a
        long phase fits in memory (bug log, Oct 26, 2026)."""
        import pandas as pd
        ts, ps, bs, as_ = [], [], [], []
        for df in pd.read_csv(path, usecols=[0, 1, 2, 3], header=0, names=["t", "p", "b", "a"], dtype={"t": str},
                              chunksize=chunk):
            t = pd.to_datetime(df["t"].str.slice(0, 26), format="%Y-%m-%d %H:%M:%S.%f").to_numpy().astype("datetime64[us]")
            p, b, a = df["p"].to_numpy(float), df["b"].fillna(0).to_numpy(float), df["a"].fillna(0).to_numpy(float)
            m = np.ones(len(t), bool)
            if start: m &= t >= np.datetime64(start, "us")
            stop = False
            if end:
                hit = np.nonzero(t >= np.datetime64(end, "us"))[0]
                if len(hit): m[hit[0]:] = False; stop = True
            ts.append(t[m]); ps.append(p[m]); bs.append(b[m]); as_.append(a[m])
            if stop: break
        self.t = np.concatenate(ts) if ts else np.array([], dtype="datetime64[us]")
        self.p, self.b, self.a = (np.concatenate(x) if x else np.array([]) for x in (ps, bs, as_))

    def quote_at(self, t):
        i = np.searchsorted(self.t, np.datetime64(t, "us"), side="right") - 1
        return (self.b[i], self.a[i]) if i >= 0 else (np.nan, np.nan)


def simulate(tape, side, signal_bar_end, stop, target, latency_ms=LATENCY_MS, stop_slip=STOP_SLIP, flatten=FLATTEN,
             gap_fill=False):
    """side = +1 long / -1 short. Returns dict(entry_time, entry, exit_time, exit, reason, ticks).
    gap_fill=False: v3.4 (stop fills at stop -/+ slip). gap_fill=True: fill model v3.5 rule 7b (frozen for Phase 3):
    the stop fills at the first traded price at or beyond it, -/+ slip. (v3.5's stop-change rules do not apply here:
    this stop never moves.)"""
    t0 = signal_bar_end + dt.timedelta(milliseconds=latency_ms)
    bid, ask = tape.quote_at(t0)
    entry = ask if side > 0 else bid
    i = np.searchsorted(tape.t, np.datetime64(t0, "us"), side="right")
    flat_at = np.datetime64(dt.datetime.combine(signal_bar_end.date(), flatten), "us")
    n = len(tape.t)
    while i < n:
        ts = tape.t[i]
        if ts >= flat_at:
            b, a = tape.b[i - 1], tape.a[i - 1]
            ex = b if side > 0 else a
            return dict(entry_time=t0, entry=entry, exit_time=ts.astype(dt.datetime), exit=ex, reason="FLATTEN",
                        ticks=round((ex - entry) * side / TICK, 2))
        j = i
        hit_stop = hit_tgt = False
        trig = None
        while j < n and tape.t[j] == ts:          # one timestamp at a time (same-timestamp tie = stop)
            pr = tape.p[j]
            if side > 0:
                if pr <= stop and not hit_stop: hit_stop, trig = True, pr
                hit_tgt |= pr >= target + TICK
            else:
                if pr >= stop and not hit_stop: hit_stop, trig = True, pr
                hit_tgt |= pr <= target - TICK
            j += 1
        if hit_stop:
            base = (min(stop, trig) if side > 0 else max(stop, trig)) if gap_fill else stop
            ex = base - side * stop_slip * TICK
            return dict(entry_time=t0, entry=entry, exit_time=ts.astype(dt.datetime), exit=ex, reason="STOP",
                        ticks=round((ex - entry) * side / TICK, 2))
        if hit_tgt:
            return dict(entry_time=t0, entry=entry, exit_time=ts.astype(dt.datetime), exit=target, reason="TARGET",
                        ticks=round((target - entry) * side / TICK, 2))
        i = j
    return dict(entry_time=t0, entry=entry, exit_time=None, exit=np.nan, reason="DATA_END", ticks=np.nan)


def nt_trades(log_path, day=None):
    """Trades NinjaTrader filled, from a JOFS log: ORDER row (signal, stop, target) + its FILL rows."""
    # NT writes the entry FILL row before its ORDER row and without an EventId (Reasons = the signal name),
    # so entries are linked by signal name and exits (Stop loss / Profit target / flatten) by EventId.
    rows = list(csv.DictReader(open(log_path, newline="", encoding="utf-8-sig")))
    out, by_signal, pending_entry = {}, {}, {}
    for x in rows:
        if day and not x.get("EvidenceTimeCT", "").startswith(day): continue
        eid = x.get("EventId", "")
        if x["RecordType"] == "ORDER":
            sig = x["Detail"].split("signal=")[1].split(";")[0].strip() if "signal=" in x["Detail"] else ""
            out[eid] = dict(event=eid, signal=sig, side=1 if x["Direction"] == "Long" else -1,
                            signal_end=dt.datetime.fromisoformat(x["EvidenceTimeCT"][:23]),
                            stop=float(x["StopAnchor"]), target=float(x["TargetPrice"]), fills=[])
            by_signal[sig] = eid
            if sig in pending_entry: out[eid]["fills"].append(pending_entry.pop(sig))
        elif x["RecordType"] == "FILL":
            d = x["Detail"]   # "SellShort 1 @ 31210.00 order=JS_01284 time=2026-10-08 08:41:00.020"
            px = float(d.split("@")[1].split()[0]); tm = d.split("time=")[1].strip()
            name = d.split("order=")[1].split(" time=")[0].strip()
            f = dict(price=px, time=tm, name=name)
            if eid in out: out[eid]["fills"].append(f)
            elif name in by_signal: out[by_signal[name]]["fills"].insert(0, f)
            else: pending_entry[name] = f
    return [v for v in out.values() if len(v["fills"]) >= 2]


def gate5(nt_log, tape_path=None, day="2026-10-08", tol_ticks=1.0, out_csv=None):
    if not nt_log:
        return False, "no NinjaTrader Sim fills for Oct 8 (needs a JOFS log from an S1.4 Playback run on Sim101)"
    trades = nt_trades(nt_log, day)
    if not trades:
        return False, f"no filled trades on {day} in {nt_log}"
    tape = Tape(tape_path)
    res, worst = [], 0.0
    for tr in trades:
        m = simulate(tape, tr["side"], tr["signal_end"], tr["stop"], tr["target"])
        ent, ex = tr["fills"][0], tr["fills"][-1]
        de = abs(m["entry"] - ent["price"]) / TICK
        dx = abs(m["exit"] - ex["price"]) / TICK if m["exit"] == m["exit"] else float("inf")
        worst = max(worst, de, dx)
        res.append(dict(event=tr["event"], side="Long" if tr["side"] > 0 else "Short", signal_end=tr["signal_end"],
                        nt_entry=ent["price"], nt_entry_time=ent["time"], model_entry=m["entry"], entry_diff_ticks=de,
                        nt_exit=ex["price"], nt_exit_reason=ex["name"], nt_exit_time=ex["time"],
                        model_exit=m["exit"], model_exit_reason=m["reason"], model_exit_time=m["exit_time"], exit_diff_ticks=dx))
    if out_csv:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
    ok = worst <= tol_ticks
    return ok, f"{len(res)} trades, worst entry/exit difference {worst:.2f} ticks (limit {tol_ticks})"
