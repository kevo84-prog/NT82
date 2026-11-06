"""Day-sheet check against independent chart bars (JE 0.3, Oct 25 2026).

The harness builds its own 1-minute bars from the MBO trade tape. This check uses Databento's exchange-built
NQ 1-minute OHLCV bars (a separate product, the bars a chart draws) and confirms, for a day:
  levels    PDH / PDL / PD cash open (08:30-15:00 CT of the prior session), ONH / ONL (17:00 - as-of),
            PD settlement (VWAP of 14:59:30-15:00 is not in 1-min bars: checked against the 14:59 bar's range)
  signals   every Qualified candidate: entry = close of the 1-minute bar ending at the signal time;
            the tracker's 15-bar outcome (stop / target first) re-derived from the bars
  trades    every strategy fill: entry inside the range of the bar it filled in; the stop / target fill
            inside the bar range of its exit minute, and the stop / target reached there
"""
import csv, json, datetime as dt
from pathlib import Path

TICK = 0.25


def load_bars(path, first, last):
    bars = {}
    with open(path) as f:
        next(f)
        for line in f:
            t, o, h, l, c, v = line.rstrip().split(",")[:6]
            if t[:10] < first or t[:10] > last: continue
            bars[dt.datetime.fromisoformat(t)] = (float(o), float(h), float(l), float(c), float(v))
    return bars


def rng(bars, a, b):
    hs = [x[1] for t, x in bars.items() if a < t <= b]; ls = [x[2] for t, x in bars.items() if a < t <= b]
    return (max(hs), min(ls)) if hs else (None, None)


HOLIDAYS = {dt.date(2025, 11, 27), dt.date(2025, 12, 25), dt.date(2026, 1, 1), dt.date(2026, 1, 19), dt.date(2026, 2, 16), dt.date(2026, 4, 3)}
HALF_DAYS = {dt.date(2025, 11, 28): dt.time(12, 0), dt.date(2025, 12, 24): dt.time(12, 0)}


def prev_session(d):
    p = d - dt.timedelta(days=1)
    while p.weekday() >= 5 or p in HOLIDAYS: p -= dt.timedelta(days=1)
    return p


def check_day(day, packet_path, jofs_path, bars, tol=TICK):
    d = dt.date.fromisoformat(day); pd = prev_session(d)
    out = []
    def add(kind, item, ours, chart, ok, note=""): out.append(dict(date=day, kind=kind, item=item, ours=ours, chart=chart, ok=ok, note=note))
    P = json.load(open(packet_path))
    lv = {l["name"]: l["price"] for l in P["levels"]}
    c0 = dt.datetime.combine(pd, dt.time(8, 30)); c1 = dt.datetime.combine(pd, HALF_DAYS.get(pd, dt.time(15, 0)))
    h, l = rng(bars, c0, c1)
    for name, val in (("PDH", h), ("PDL", l)):
        if name in lv: add("level", name, lv[name], val, abs(lv[name] - val) <= tol)
    # overnight = Globex from 17:00 of the calendar day before the session (after a holiday with a short Globex
    # session, e.g. MLK / Presidents' Day, that session belongs to neither PD nor ON, as in the map); fixed Oct 26, 2026
    o0 = dt.datetime.combine(d - dt.timedelta(days=1), dt.time(17, 0)); asof = dt.datetime.combine(d, dt.time(*map(int, P["asof_ct"].split(":"))))
    h, l = rng(bars, o0, asof)
    for name, val in (("ONH", h), ("ONL", l)):
        if name in lv: add("level", name, lv[name], val, abs(lv[name] - val) <= tol)
    b = bars.get(c1)
    if "PDSET" in lv and b:
        add("level", "PDSET", lv["PDSET"], f"{b[2]}-{b[1]} (14:59 bar)", b[2] - tol <= lv["PDSET"] <= b[1] + tol)
    rows = list(csv.DictReader(open(jofs_path, newline="", encoding="utf-8-sig")))
    for x in rows:
        if x["RecordType"] == "OUTCOME" and x["CandidateStatus"] == "Qualified" and x["EvidenceTimeCT"].startswith(day):
            st = dt.datetime.fromisoformat((x.get("SignalTimeCT") or x["EvidenceTimeCT"])[:19])
            # RESPONSE entries move to the confirmation bar's close (the next bar, CONFIRM row); INITIATION = the signal bar
            eb = st + dt.timedelta(minutes=1) if x["SetupFamily"] == "RESPONSE" else st
            bb = bars.get(eb)
            e, s, t = float(x["EntryRef"]), float(x["StopAnchor"]), float(x["TargetPrice"])
            add("signal_entry", f"{st:%H:%M} {x['Direction']} {x['SetupFamily']} {x['LocationId']}", e, bb[3] if bb else None, bool(bb) and abs(bb[3] - e) <= tol)
            side = 1 if x["Direction"] == "Long" else -1
            res = "TIME_EXPIRED"
            for k in range(1, 16):   # 15 bars after the entry bar (the confirmation bar for RESPONSE)
                q = bars.get(eb + dt.timedelta(minutes=k))
                if not q: continue
                hit_s = q[2] <= s if side > 0 else q[1] >= s
                hit_t = q[1] >= t if side > 0 else q[2] <= t
                if hit_s: res = "STOP_FIRST"; break
                if hit_t: res = "TARGET_FIRST"; break
            ours = x["Outcome15"]
            same = res == ours or (ours == "AMBIGUOUS_SAME_BAR" and res == "STOP_FIRST") or (ours == "SESSION_END" and res in ("TIME_EXPIRED", "STOP_FIRST", "TARGET_FIRST") and st.time() >= dt.time(14, 45))
            add("signal_outcome15", f"{st:%H:%M} {x['Direction']}", ours, res, same,
                "window cut at the session end" if ours == "SESSION_END" else ("same-bar tie counts as stop" if ours == "AMBIGUOUS_SAME_BAR" else ""))
        if x["RecordType"] == "FILL" and x["EvidenceTimeCT"].startswith(day):
            det = x["Detail"]; px = float(det.split("@")[1].split()[0]); tm = dt.datetime.fromisoformat(det.split("time=")[1].strip()[:19])
            bar_end = tm.replace(second=0) + dt.timedelta(minutes=1)
            q = bars.get(bar_end)
            name = det.split("order=")[1].split(" time=")[0]
            add("fill", f"{tm:%H:%M:%S} {name}", px, f"{q[2]}-{q[1]}" if q else None, bool(q) and q[2] - tol <= px <= q[1] + tol)
    return out


def write(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
