r"""P1.1 on the PC: gamma ranks (U6) for every Block 1 session from the same D-1 option files as the GEX levels.

  python -m book1a.gamma_ranks_pc K:\Databento_BackTesting Book1A\Phase0 [--hand 2025-11-05 2026-01-15] [--sessions ...]

Per session D+1 (report date D = the previous session, as gex_levels_block1.csv):
  1. Book 1's own pipeline, unchanged: gex_block1.build(D) -> gex_calc.cme_day -> mq_levels.strike_gex on the front
     contract's chain = net GEX per strike (the numbers mq_levels.compute_levels turns into CR / PS / HVL).
  2. book1a.gamma_ranks.rank_strikes: gamma1..5 by |net GEX|, shifted to the chart contract with nt_shift_pts.
  3. Consistency check against gex_levels_block1.csv: the largest positive strike = call_resistance and the most
     negative = put_support (same inputs, so they must agree on every ok session).
  4. Hand ranking on the --hand days: an independent numpy Black-76 gamma (no mq_levels code), summed per strike and
     sorted by hand; top 5 must equal step 2.
  5. Reproduction on the --hand days: mq_levels.compute_levels rerun in this Python (the Book 1A venv) must give the
     gex_levels_block1.csv values (front, settle, every level, net_gex, regime, options_used).
available_at = D-1 23:00 ET (the report date's 11 PM ET cutoff), before the 08:10 CT map of D+1.
Writes P1.1_gamma_ranks.csv and P1.1_gamma_ranks.md. Reads option / futures files only (no result file).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import os
import sys
from pathlib import Path

from book1a import gamma_ranks as G

VERSION = "gamma-ranks-pc-v1.1"
REPRO = ["front", "settle", "call_resistance", "put_support", "hvl", "call_resistance_0dte", "put_support_0dte",
         "hvl_0dte", "net_gex", "regime", "options_used"]


def hand_strike_gex(ch, S: float) -> dict:
    """Independent of mq_levels: Black-76 gamma = exp(-rT) n(d1) / (S iv sqrt T), d1 = (ln(S/K) + iv^2 T / 2) / (iv sqrt T),
    r = 4%; GEX = gamma * OI * 20 * S^2 * 1%, calls +, puts -; summed per strike."""
    out = {}
    for k, cp, T, iv, oi in zip(ch.strike, ch.cp, ch["T"], ch.iv, ch.oi):
        if not (oi > 0 and math.isfinite(iv) and math.isfinite(T) and T > 0):
            continue
        iv = max(iv, 1e-3)
        sq = iv * math.sqrt(T)
        d1 = (math.log(S / k) + 0.5 * iv * iv * T) / sq
        g = math.exp(-0.04 * T) * math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi) / (S * sq)
        out[float(k)] = out.get(float(k), 0.0) + g * oi * 20.0 * S * S * 0.01 * (1.0 if cp == "C" else -1.0)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("book1_root"); ap.add_argument("out_dir")
    ap.add_argument("--hand", nargs="*", default=["2025-11-05", "2026-01-15"])
    ap.add_argument("--sessions", nargs="*", default=None)
    a = ap.parse_args(argv)
    root, out = Path(a.book1_root).resolve(), Path(a.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root))
    import pandas as pd
    import gex_block1 as GB          # Book 1, unchanged
    import gex_calc as gc
    from mq_levels import strike_gex, compute_levels
    # Book 1's extract cache, read through hard links: an extract missing there is written to our folder only
    cache = out / "gex_cache_links"
    cache.mkdir(exist_ok=True)
    for f in (root / "gex_cache").glob("*.pkl"):
        if not (cache / f.name).exists():
            os.link(f, cache / f.name)
    GB.CACHE = cache

    lv = pd.read_csv(root / "gex_levels_block1.csv")
    if a.sessions:
        lv = lv[lv.session.isin(a.sessions)]
    rows, checks, hands, repro = [], [], [], []
    for r in lv.itertuples():
        sess, D = dt.date.fromisoformat(r.session), dt.date.fromisoformat(r.report_date)
        row = dict(session=r.session, report_date=r.report_date, available_at=f"{r.report_date} 23:00 ET", front=r.front,
                   nt_shift_pts=r.nt_shift_pts, ok=bool(r.ok))
        if not r.ok:
            rows.append(dict(row, error="GEX levels not ok for this session")); continue
        b = GB.build(D)
        d, oi, st, fut, front, _ = b
        S = float(fut[(fut.date == D) & (fut.symbol == front)].price.iloc[0])
        chain = gc.cme_day(D, sess, d, oi, st, fut)
        ch = chain[chain.underlying == front]
        p = strike_gex(ch, S)
        net = {float(k): float(v) for k, v in p.items()}
        ranks = G.rank_strikes(net, top=5)
        lev = G.as_levels(ranks, float(r.nt_shift_pts))
        sg = G.signed_ranks(net, top=1)
        pos_ok = bool(sg["positive"]) and sg["positive"][0][1] == float(r.call_resistance)
        neg_ok = bool(sg["negative"]) and sg["negative"][0][1] == float(r.put_support)
        checks.append((r.session, pos_ok, neg_ok))
        for rank, k, v in ranks:
            row[f"gamma{rank}_strike"] = k
            row[f"gamma{rank}_net_gex"] = round(v, 2)
            row[f"gamma{rank}_nt"] = lev[f"gamma{rank}"]
        row.update(front_used=front, settle=S, cr_matches=pos_ok, ps_matches=neg_ok, error="")
        rows.append(row)
        if r.session in a.hand:
            h = hand_strike_gex(ch, S)
            hand_top = sorted(h.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:5]
            same = [k for k, _ in hand_top] == [k for _, k, _ in ranks] and all(
                abs(hv - mv) <= 1e-6 * max(1.0, abs(mv)) for (_, hv), (_, _, mv) in zip(hand_top, ranks))
            hands.append((r.session, ranks, hand_top, same))
            lv2 = dict(compute_levels(chain, S, front, sess), front=front, settle=S)
            for c in REPRO:
                x, y = getattr(r, c), lv2[c]
                eq = (x == y) if isinstance(x, str) or isinstance(y, str) else (
                    float(x) == float(y) or abs(float(x) - float(y)) <= 1e-9 * max(1.0, abs(float(x))))
                repro.append((r.session, c, x, y, bool(eq)))
        print(f"{r.session} {front} gamma1-5 {[k for _, k, _ in ranks]} CR {pos_ok} PS {neg_ok}", flush=True)

    cols = list(dict.fromkeys(k for x in rows for k in x))
    with open(out / "P1.1_gamma_ranks.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    n_ok = len(checks)
    n_cons = sum(1 for _, p_, n_ in checks if p_ and n_)
    hand_pass = bool(hands) and all(h[3] for h in hands) and len(hands) >= 2
    repro_pass = bool(repro) and all(x[4] for x in repro)
    verdict = "PASS" if hand_pass and repro_pass and n_cons == n_ok else "FAIL"
    L = [f"# P1.1 gamma ranks (U6)", "", f"Version {VERSION} with {G.VERSION}; Book 1 pipeline gex_block1.build / gex_calc.cme_day /"
         " mq_levels.strike_gex unchanged. Run " + dt.datetime.now().strftime("%Y-%m-%d %H:%M") + ".", "",
         f"**Verdict: {verdict}**", "",
         f"- sessions in gex_levels_block1.csv: {len(lv)}; ranked: {n_ok}; not ok (no levels): {len(lv) - n_ok}",
         f"- consistency (largest positive strike = call_resistance and most negative = put_support): {n_cons} / {n_ok}",
         f"- hand ranking days: {', '.join(h[0] for h in hands)}: {'all equal' if hand_pass else 'MISMATCH'}",
         f"- reproduction of gex_levels_block1.csv in this Python ({sys.version.split()[0]}) on the hand days: "
         f"{sum(x[4] for x in repro)} / {len(repro)} values equal",
         "- available_at = report date D-1 23:00 ET for every session, before the 08:10 CT map of the session.",
         "- gamma1 = the strike with the largest |net GEX| (sign kept in the table); levels shifted to the chart contract with nt_shift_pts (the *_nt columns).",
         ""]
    bad = [c for c in checks if not (c[1] and c[2])]
    if bad:
        L += ["## Consistency misses", "| session | CR match | PS match |", "|---|---|---|"] + [f"| {s} | {p_} | {n_} |" for s, p_, n_ in bad] + [""]
    for s, ranks, hand_top, same in hands:
        L += [f"## Hand ranking {s}: {'EQUAL' if same else 'MISMATCH'}", "| rank | module strike | module net GEX | hand strike | hand net GEX |",
              "|---|---|---|---|---|"]
        for (rk, k, v), (hk, hv) in zip(ranks, hand_top):
            L.append(f"| {rk} | {k:g} | {v:,.0f} | {hk:g} | {hv:,.0f} |")
        L.append("")
    L += ["## Reproduction of gex_levels_block1.csv (hand days)", "| session | field | gex_levels_block1.csv | rerun | equal |",
          "|---|---|---|---|---|"] + [f"| {a_} | {c} | {x} | {y} | {'yes' if e else '**NO**'} |" for a_, c, x, y, e in repro] + [""]
    (out / "P1.1_gamma_ranks.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict}: {n_cons}/{n_ok} consistent, hand {hand_pass} -> {out / 'P1.1_gamma_ranks.md'}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
