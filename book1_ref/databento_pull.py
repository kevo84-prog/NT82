r"""
Databento pull for the Jeron XGBoost backtest.

Block 1 sessions: 2025-10-22 .. 2026-04-21 (trading dates; each starts 17:00 CT the evening before).
GEX inputs match gex-menthorq-replication.md.

Two depth options:
  default  L2 = MBP-10, NQ only, 08:00-15:15 CT, one request per weekday.
  l3       L3 = MBO, NQ only, full UTC days (same format as NQ_MBO_2026-09). Each daily file starts
           with a full book snapshot, so L2 can be rebuilt from any day on its own. MBO also holds
           every NQ trade with its CME aggressor side, so NQ trades are only bought for the lookback.
Days you already own as MBO (any glbx-mdp3-YYYYMMDD.mbo.dbn.zst under OWNED_MBO_ROOT) are skipped
in both options: no L2 and no L3 is bought for them.

Usage (Windows command prompt, from K:\Databento_BackTesting):
    set DATABENTO_API_KEY=db-xxxxxxxx
    python databento_pull.py estimate        # prices the L2 version, no charge -> estimate_block1.csv
    python databento_pull.py estimate l3     # prices the L3 version, no charge -> estimate_block1_l3.csv
    python databento_pull.py submit [l3]     # submits batch jobs (this is where you pay) -> jobs_block1.json
    python databento_pull.py download        # downloads finished jobs into OUT_DIR\<request name>\
    python databento_pull.py estimate roll   # roll-day fixes (contract NinjaTrader was on), no charge
    python databento_pull.py submit roll     # buys them; files land in OUT_DIR\nq_roll_* and roll_*
    python databento_pull.py estimate parity # ES Dec 26 1-minute bars for the parity days (Sep 20 - Oct 9, 2026), no charge
    python databento_pull.py submit parity   # buys them (a few cents); files land in OUT_DIR\parity_ESZ6_ohlcv_1m_*
    python databento_pull.py cot             # free CFTC COT (Traders in Financial Futures) for NQ -> cot_nq.csv

Pick ONE version per block for submit. Requests both versions share (bars, statistics, options, ES)
have the same names, so they are never bought twice.

Block 2: change BLOCK, FIRST_SESSION, LAST_SESSION and set WARMUP_START = FIRST_SESSION
(block 1 already holds the lookback). Re-running submit skips requests already submitted.
"""
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

try:
    import databento as db
except ImportError:
    db = None

# ---------------------------------------------------------------- settings
BLOCK = "block1"
ROOT = r"K:\Databento_BackTesting"
OUT_DIR = os.path.join(ROOT, "raw", BLOCK)
OWNED_MBO_ROOT = ROOT          # searched (with subfolders) for MBO files you already own
DATASET = "GLBX.MDP3"
CT = ZoneInfo("America/Chicago")

FIRST_SESSION = dt.date(2025, 10, 22)
LAST_SESSION = dt.date(2026, 4, 21)
# Lookback for the pre-open map: 2-3 month HTF composite, weekly / prior-week profiles, ADR.
WARMUP_START = dt.date(2025, 7, 21)

# MBP-10 (L2) only around the NY session, to keep cost and disk down.
MBP_WINDOW_CT = (dt.time(8, 0), dt.time(15, 15))

# Option roots for the GEX method (front NQ futures options: quarterly + weeklies + EOM).
# Same list as gex_weeklies_download.py (weeks 1-5; fifth-week roots only exist in some months).
WEEKLY_ROOTS = [f"Q{w}{d}" for d in "ABCD" for w in range(1, 6)] + [f"QN{w}" for w in range(1, 6)] + ["QNE"]
OPT_ROOTS = ["NQ"] + WEEKLY_ROOTS


# ---------------------------------------------------------------- helpers
def iso(d):
    return d.isoformat()


def owned_mbo_days():
    """UTC dates of NQ MBO day files already on disk."""
    days = set()
    pat = re.compile(r"glbx-mdp3-(\d{8})\.mbo\.dbn\.zst$")
    if not os.path.isdir(OWNED_MBO_ROOT):
        return days
    for folder, _, files in os.walk(OWNED_MBO_ROOT):
        for f in files:
            m = pat.match(f)
            if m:
                days.add(dt.datetime.strptime(m.group(1), "%Y%m%d").date())
    return days


def ranges(days):
    """Sorted dates -> list of (first, last) runs of consecutive days."""
    out = []
    for d in sorted(days):
        if out and d == out[-1][1] + dt.timedelta(days=1):
            out[-1][1] = d
        else:
            out.append([d, d])
    return out


# ---------------------------------------------------------------- request list
def build_requests(l3):
    fut_start = WARMUP_START - dt.timedelta(days=1)          # covers the 17:00 CT evening session
    opt_start = iso(FIRST_SESSION - dt.timedelta(days=2))    # report date D-1 for the first session
    end = iso(LAST_SESSION + dt.timedelta(days=1))           # Databento end is exclusive
    owned = owned_mbo_days()

    reqs = []

    def add(name, symbols, stype_in, schema, start, end_=end):
        reqs.append(dict(name=name, symbols=symbols, stype_in=stype_in,
                         schema=schema, start=start, end=end_))

    # Tick by tick (aggressor side from CME) -> tape, footprint, delta, power/deep trades
    if l3:
        # MBO covers NQ trades from the UTC day before the first session; buy trades for the lookback only.
        mbo_first = FIRST_SESSION - dt.timedelta(days=1)
        if fut_start < mbo_first:
            add("nq_trades_lookback", ["NQ.v.0"], "continuous", "trades", iso(fut_start), iso(mbo_first))
    else:
        add("nq_trades", ["NQ.v.0"], "continuous", "trades", iso(fut_start))
    # ES: price only (1-minute and daily bars below); ES trades dropped Oct 22 2026 (no rule uses ES order flow).
    # To buy ES trades later for specific dates, add a request here with those dates.

    # Price and volume bars (cheap; also used for 10y and oil direction)
    for root in ("NQ", "ES", "ZN", "CL"):
        add(f"{root.lower()}_ohlcv_1m", [f"{root}.v.0"], "continuous", "ohlcv-1m", iso(fut_start))
        add(f"{root.lower()}_ohlcv_1d", [f"{root}.v.0"], "continuous", "ohlcv-1d", iso(fut_start))

    # Futures settlement, volume, open interest + contract definitions (roll dates, tick size)
    for root in ("NQ", "ES"):
        add(f"{root.lower()}_fut_statistics", [f"{root}.FUT"], "parent", "statistics", iso(fut_start))
        add(f"{root.lower()}_fut_definition", [f"{root}.FUT"], "parent", "definition", iso(fut_start))

    # GEX inputs: every front NQ option (definitions + settlement + OI)
    # One request per root, so a root Databento doesn't list only fails its own line.
    for root in OPT_ROOTS:
        add(f"opt_{root.lower()}_definition", [f"{root}.OPT"], "parent", "definition", opt_start)
        add(f"opt_{root.lower()}_statistics", [f"{root}.OPT"], "parent", "statistics", opt_start)

    skipped = 0
    if l3:
        # L3: full UTC days from the day before the first session (evening open) to the last session.
        want = set()
        d = FIRST_SESSION - dt.timedelta(days=1)
        while d <= LAST_SESSION:
            if d.weekday() != 5:          # Saturday files are empty
                if d in owned:
                    skipped += 1
                else:
                    want.add(d)
            d += dt.timedelta(days=1)
        # One job per run of days (Saturdays fill the gaps so a month stays one job)
        filled = set(want)
        for d in list(want):
            sat = d + dt.timedelta(days=1)
            if sat.weekday() == 5 and sat + dt.timedelta(days=1) in want:
                filled.add(sat)
        for a, b in ranges(filled):
            add(f"nq_mbo_{a:%Y%m%d}_{b:%Y%m%d}", ["NQ.v.0"], "continuous", "mbo",
                iso(a), iso(b + dt.timedelta(days=1)))
    else:
        # L2: MBP-10 for NQ, one request per weekday, NY window only (holidays come back empty)
        d = FIRST_SESSION
        while d <= LAST_SESSION:
            if d.weekday() < 5:
                if d in owned:
                    skipped += 1
                else:
                    s = dt.datetime.combine(d, MBP_WINDOW_CT[0], CT).astimezone(dt.timezone.utc)
                    e = dt.datetime.combine(d, MBP_WINDOW_CT[1], CT).astimezone(dt.timezone.utc)
                    add(f"nq_mbp10_{d:%Y%m%d}", ["NQ.v.0"], "continuous", "mbp-10",
                        s.strftime("%Y-%m-%dT%H:%M"), e.strftime("%Y-%m-%dT%H:%M"))
            d += dt.timedelta(days=1)

    if skipped:
        print(f"Skipping {skipped} days you already own as MBO (under {OWNED_MBO_ROOT}).")
    return reqs


# ---------------------------------------------------------------- roll-day fixes
# Databento's NQ.v.0 / ES.v.0 switch contracts by the previous day's volume, two trading days AFTER
# NinjaTrader's roll (NT rollover dates from its database: Sep 15 2025, Dec 15 2025, Mar 16 2026,
# Jun 12 2026, Sep 14 2026). On those two days the continuous files hold the expiring contract.
# These requests buy the contract NinjaTrader was on. UTC days include the Sunday evening open.
# (new contract, first UTC day, last UTC day, what to buy)
ROLL_FIX = {
    "block1": [
        ("NQZ5", dt.date(2025, 9, 14), dt.date(2025, 9, 16), "trades"),     # lookback: Sep 15-16 2025
        ("NQH6", dt.date(2025, 12, 14), dt.date(2025, 12, 16), "mbo"),      # Dec 15-16 2025
        ("NQM6", dt.date(2026, 3, 15), dt.date(2026, 3, 17), "mbo"),        # Mar 16-17 2026
        ("NQZ6", dt.date(2026, 9, 13), dt.date(2026, 9, 15), "mbo"),        # Sep 14-15 2026 (owned Sep data)
    ],
    "block2": [],   # fill in at block 2: Jun 12 2026 roll (check Databento's switch date first)
}
ES_FOR = {"NQZ5": "ESZ5", "NQH6": "ESH6", "NQM6": "ESM6", "NQZ6": "ESZ6"}


def build_roll_requests():
    reqs = []
    for sym, a, b, schema in ROLL_FIX.get(BLOCK, []):
        start, end = iso(a), iso(b + dt.timedelta(days=1))
        reqs.append(dict(name=f"nq_roll_{sym}_{schema}_{a:%Y%m%d}_{b:%Y%m%d}", symbols=[sym],
                         stype_in="raw_symbol", schema=schema, start=start, end=end))
        for root_sym in (sym, ES_FOR[sym]):     # matching 1-minute bars for the pre-open map
            reqs.append(dict(name=f"roll_{root_sym}_ohlcv_1m_{a:%Y%m%d}_{b:%Y%m%d}", symbols=[root_sym],
                             stype_in="raw_symbol", schema="ohlcv-1m", start=start, end=end))
    return reqs


# Parity gates (Oct 25 2026): ES 1-minute bars for the map's ES block (gate 3) and the strategy's ES gate (gates 1-2).
PARITY_ES = [("ESZ6", dt.date(2026, 9, 20), dt.date(2026, 10, 9))]


def build_parity_requests():
    reqs = []
    for sym, a, b in PARITY_ES:
        reqs.append(dict(name=f"parity_{sym}_ohlcv_1m_{a:%Y%m%d}_{b:%Y%m%d}", symbols=[sym], stype_in="raw_symbol",
                         schema="ohlcv-1m", start=iso(a), end=iso(b + dt.timedelta(days=1))))
    return reqs


# ---------------------------------------------------------------- COT (not on Databento)
# CFTC Traders in Financial Futures, futures only. 209742 = NASDAQ-100 Consolidated (E-mini).
# Report is as of Tuesday, released Friday 3:30 PM ET: use it from the following Monday's session.
COT_URL = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv"
COT_CODE = "209742"


def cot():
    os.makedirs(OUT_DIR, exist_ok=True)
    q = {
        "$where": (f"cftc_contract_market_code='{COT_CODE}' AND "
                   f"report_date_as_yyyy_mm_dd >= '{iso(WARMUP_START - dt.timedelta(days=90))}' AND "
                   f"report_date_as_yyyy_mm_dd <= '{iso(LAST_SESSION)}'"),
        "$order": "report_date_as_yyyy_mm_dd",
        "$limit": "5000",
    }
    url = COT_URL + "?" + urllib.parse.urlencode(q)
    path = os.path.join(OUT_DIR, "cot_nq.csv")
    with urllib.request.urlopen(url, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())
    rows = sum(1 for _ in open(path)) - 1
    print(f"Saved {rows} weekly COT rows to {path}")


# ---------------------------------------------------------------- actions
def client():
    if db is None:
        sys.exit("pip install databento")
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        sys.exit("Set DATABENTO_API_KEY first.")
    return db.Historical(key)


def estimate(c, reqs, l3, suffix=None):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"estimate_{BLOCK}{suffix if suffix else ('_l3' if l3 else '')}.csv")
    total_cost = total_gb = depth_cost = depth_gb = 0.0
    depth = "mbo" if l3 else "mbp-10"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "schema", "start", "end", "cost_usd", "size_gb"])
        for r in reqs:
            kw = dict(dataset=DATASET, symbols=r["symbols"], stype_in=r["stype_in"],
                      schema=r["schema"], start=r["start"], end=r["end"])
            try:
                cost = c.metadata.get_cost(**kw)
                gb = c.metadata.get_billable_size(**kw) / 1e9
            except Exception as ex:  # unresolved symbols, bad range, etc.
                print(f"{r['name']}: ERROR {ex}")
                w.writerow([r["name"], r["schema"], r["start"], r["end"], "ERROR", str(ex)[:200]])
                continue
            w.writerow([r["name"], r["schema"], r["start"], r["end"], f"{cost:.2f}", f"{gb:.2f}"])
            total_cost += cost
            total_gb += gb
            if r["schema"] == depth:
                depth_cost += cost
                depth_gb += gb
            else:
                print(f"{r['name']:<28} ${cost:>9.2f}  {gb:>8.2f} GB")
    label = "NQ L3 (mbo, all days)" if l3 else "NQ L2 (mbp-10, all days)"
    print(f"{label:<28} ${depth_cost:>9.2f}  {depth_gb:>8.2f} GB")
    print(f"{'TOTAL':<28} ${total_cost:>9.2f}  {total_gb:>8.2f} GB (uncompressed billable)")
    print(f"Saved {path}")


def jobs_path():
    return os.path.join(OUT_DIR, f"jobs_{BLOCK}.json")


def load_jobs():
    p = jobs_path()
    return json.load(open(p)) if os.path.exists(p) else {}


def save_jobs(jobs):
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(jobs, open(jobs_path(), "w"), indent=1)


def submit(c, reqs, l3):
    jobs = load_jobs()
    other = "mbp-10" if l3 else "mbo"
    if any(j.get("schema") == other for j in jobs.values()):
        sys.exit(f"This block already has {other} jobs submitted. Pick one depth version per block, "
                 f"or change BLOCK to submit the other one on purpose.")
    for r in reqs:
        if r["name"] in jobs:
            continue
        job = None
        for attempt in range(6):
            try:
                job = c.batch.submit_job(
                    dataset=DATASET, symbols=r["symbols"], stype_in=r["stype_in"], schema=r["schema"],
                    start=r["start"], end=r["end"], encoding="dbn", compression="zstd",
                    split_duration="day", delivery="download")
                break
            except Exception as ex:
                msg = str(ex)
                if "429" in msg:      # rate limit: wait as told, then try again
                    m = re.search(r"Retry in (\d+)", msg)
                    wait = int(m.group(1)) + 2 if m else 20
                    print(f"  rate limited on {r['name']}; waiting {wait}s")
                    time.sleep(wait)
                    continue
                print(f"skipped {r['name']}: {msg[:150]}")   # e.g. an option root with no listings
                break
        if job is None:
            continue
        time.sleep(1)                  # stay under Databento's submit rate limit
        jobs[r["name"]] = {"id": job["id"], "schema": r["schema"], "downloaded": False}
        save_jobs(jobs)  # save after each job so a crash never double-submits
        print(f"submitted {r['name']}: {job['id']}")
    print(f"{len(jobs)} jobs recorded in {jobs_path()}")


def download(c):
    jobs = load_jobs()
    state = {j["id"]: j["state"] for j in c.batch.list_jobs()}
    waiting = 0
    for name, j in jobs.items():
        if j["downloaded"]:
            continue
        if state.get(j["id"]) != "done":
            waiting += 1
            continue
        c.batch.download(job_id=j["id"], output_dir=os.path.join(OUT_DIR, name))
        j["downloaded"] = True
        save_jobs(jobs)
        print(f"downloaded {name}")
    print(f"{waiting} jobs still processing; run download again later.")


if __name__ == "__main__":
    args = [a.lower() for a in sys.argv[1:]]
    action = args[0] if args else "estimate"
    l3 = "l3" in args[1:]
    if action == "cot":
        cot()
        sys.exit()
    if action not in ("estimate", "submit", "download"):
        sys.exit("Use: estimate [l3|roll|parity] | submit [l3|roll|parity] | download | cot")
    roll = "roll" in args[1:]
    parity = "parity" in args[1:]
    c = client()
    if action == "download":
        download(c)
    elif parity:
        reqs = build_parity_requests()
        if action == "estimate":
            estimate(c, reqs, True, suffix="_parity")
        else:
            submit(c, reqs, True)
    elif roll:
        reqs = build_roll_requests()
        if action == "estimate":
            estimate(c, reqs, True, suffix="_roll")
        else:
            submit(c, reqs, True)
    else:
        reqs = build_requests(l3)
        if action == "estimate":
            estimate(c, reqs, l3)
        else:
            submit(c, reqs, l3)
