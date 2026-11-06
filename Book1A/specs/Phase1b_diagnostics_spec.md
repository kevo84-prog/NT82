# Book 1A Phase 1b: diagnostics specification (results-free)

Written by the checker, Nov 5, 2026, from the frozen definitions in the Book 1A replay plan (sections 5, 7 and 10;
U4, U5, U11), the Book 1A entry footprint doc (CVD_DIV, BREAKOUT_SPEED) and the parked Book 1C / 1D screens.
It contains no Book 1 results. Values marked "(ours, frozen here)" had no number in the sources and are fixed
by this document, dated before any Phase 1b run and before any Phase 2 result. Approved for writing by Kyron,
Nov 5, 2026.

## 0. Rules for every diagnostic

1. **Logged only.** No diagnostic changes an R1-R4 candidate, gate, grade, entry, stop, target, exit, size,
   risk decision or plan. No diagnostic becomes an entry filter during the replay.
2. **Separate files.** Diagnostics are written to their own files, keyed by session, strategy and trade_id or
   candidate id. The R1-R4 ledgers and candidate logs are never edited or re-ordered.
3. **Point in time.** Every field records `available_at`. A field may only use data with a timestamp before its
   `available_at`. Fields that are knowable only after entry are labelled POST_ENTRY and never mixed with
   AT_ENTRY fields.
4. **No outcome review in Phase 1b.** Counterfactual fields (alternative exits, hypothetical sizes) are
   computed and stored per trade, but nothing is aggregated, summarised or reported by outcome in Phase 1b.
   Outcome analysis happens only at the end of Phase 2, as the replay plan says.
5. **Missing data.** A diagnostic that cannot be computed writes a code, never a guess: NOT_BUILT,
   NOT_RUN (reason), DATA_MISSING, NOT_APPLICABLE.

## 1. Not run in Phase 1b (and why)

| Item | Status | Reason |
|---|---|---|
| L2 E1, E2, E4 | NOT_RUN (U11) | U11: not run until the L2F audit and the fixed-price build are done; E4's hold time N is not registered |
| M-J3, M-J4 | NOT_RUN (U5) | U5: deferred until objective triggers are specified |
| GEX V3, volatility control | Build only if their inputs are reachable through `K:\Book1A_inputs` (per-strike gamma and option settlements). If not, write NOT_RUN (inputs) and stop to ask Kyron. Do not add inputs on your own. | Inputs |

## 2. Exit diagnostics (per trade, R4; also on R1-R3 trades)

**Exit cue (a), absorption against the trade.** In any of the first 3 completed one-minute bars after entry,
a bar whose delta is in the trade's direction (buy delta for a long, sell delta for a short) but closes
against the trade (close below its open for a long, above for a short) triggers a hypothetical exit at
market 250 ms after that bar's close, filled by the v3.5 rules (best bid for a long exit, best ask for a
short). If the M0 trade has already exited before the trigger, the cue is NOT_APPLICABLE. Fields: trigger bar
time, cue exit time and price, `cue_fired` (Y/N), POST_ENTRY. Stress: the same at 1,000 ms.

**M-J1 (single exit at the ladder).** Same entry, initial stop, fills and commissions as M0. The whole
position exits at the plan ladder's RUN target if the zone side has one, else TP2, else TP1 (U4). Stop never
moved. Fields: target used (RUN / TP2 / TP1), exit time, exit price, exit reason.

**M-J2 (one NQ off at TP1).** Only for trades with 2 or more NQ; 1 NQ trades are NOT_APPLICABLE. 1 NQ exits at
TP1; the rest goes to M-J1's target. The stop is unchanged after TP1 (break-even belongs to M-J3). Same entry,
initial stop, fills and commissions as M0. Fields: per-leg exit times, prices and reasons; contract count;
size bucket (2, 3, 4+ NQ).

## 3. Sizing diagnostics (per trade)

**10 NQ feasibility (hypothetical).** For every eligible trade: planned dollar risk at 10 NQ by the U3
formula ((stop ticks + 2) x $5 x 10 + $5.74 x 10), whether it fits the $1,000 per-trade budget (largest stop
that fits 10 NQ: 16 ticks), and the account equity needed at 1% risk. Per-trade fields only in Phase 1b.

**MNQ feasibility (diagnostic only, not promotable).** For every RISK_REJECT under NQ-only sizing: the largest
whole number of MNQ that fits $1,000 by the same formula with $0.50 per tick and $1.88 round trip
((stop ticks + 2) x $0.50 x M + $1.88 x M), whether at least 1 MNQ fits, and the trade's hypothetical entry,
stop, target and exit under the same fill rules. Per-trade fields only in Phase 1b.

## 4. CVD diagnostics (per candidate and per trade)

**CVD.** Running sum of signed executed trade volume from the MBO aggressor flag (buy aggressor +, sell
aggressor -; trades only, no book changes). Primary reset at 17:00 CT; a second series reset at 08:30 CT is
logged as a diagnostic. CVD is sampled at each price swing's own timestamp.

**Swings.** The AMT PO-1 rule: a one-minute bar whose high (low) is strictly the highest (lowest) of the 15
bars before and the 15 after. A swing is confirmed when the 15th bar after it closes; that close is its
earliest knowable time.

**CVD_DIV (swing-pair divergence).** Compare the two most recent confirmed swings of the same type (two highs
or two lows) at the entry zone or at the session extreme, at most 60 minutes apart (our research assumption;
pairs excluded by the 60-minute window are counted, not dropped silently). The four cases:

| Case | Price | CVD |
|---|---|---|
| HIGH_ABSORPTION | lower high | higher high |
| HIGH_EXHAUSTION | higher high | lower high |
| LOW_EXHAUSTION | lower low | higher low |
| LOW_ABSORPTION | higher low | lower low |

Each is tagged WITH or AGAINST the trade (a high case favours shorts, a low case favours longs). Fields: both
swing times and confirmation times, price and CVD at both swings (both resets), case, WITH / AGAINST, the
earliest knowable time, and timing: AT_ENTRY (both swings confirmed before the entry decision), POST_ENTRY
(confirmed after). **PROVISIONAL:** compares the first confirmed swing with the extreme so far at the entry
bar (knowable at entry); logged separately and never combined with AT_ENTRY or POST_ENTRY. Overlap fields: T8,
the passive trap tag, the delta gates.

**"At the entry zone or the session extreme" (ours, frozen here):** the second swing's price is inside the
trade's decision zone or within 10 points of it (the GEX / L1 distance used elsewhere in Book 1A), or the
second swing makes or equals the session high (low) so far.

**BREAKOUT_SPEED (INITIATION entries only).** Executed volume per second over the 60 s before the decision
timestamp (trades strictly before the decision only; 60 s ours), its percentile against the same measure at
every earlier one-minute bar close of the session so far, and the signed 3-bar CVD change. Raw values only,
no label.

**Other CVD fields already logged:** cvd_slope_5 (unchanged). "Grade without CVD" (the S1.4 grade recomputed
with the CVD and tape-speed inputs neutral) is a counterfactual field on R4 candidates, never a new grade.

## 5. GEX diagnostics (per zone, per trade, per session)

Source levels: `gex_levels_block1.csv` (`*_nt` columns), report date D-1, as frozen.

**V2 random-level twin (ours, frozen here: seed 20251205).** For each session, build two twin sets of the six
GEX levels:
- random twin: each level moved to the price at the same distance from the 08:10 ref_price, on a side drawn at
  random (seed 20251205 plus the session date as yyyymmdd);
- round-number twin: each level moved to the nearest multiple of 100 points.

Recount the GEX family on every R4 zone with each twin set (same 10-point rule). Fields: GEX family present
(real / random / round), and whether the zone's decision status would differ. Logged only; R4's zones are
never changed.

**V3 second flip estimate.** A simple zero crossing of cumulative net GEX across strikes (sorted by strike),
beside our HVL: `flip_v3`, `regime_agree` (Y/N), distance to HVL in points. Build only if per-strike net GEX is
reachable through the inputs folder (section 1).

**V5 missing GEX days.** Sessions without valid GEX levels stay in the baseline, carry `gex_valid = N`, and
drop out of every GEX group. Counts per phase.

**Volatility control.** NQ ATM implied volatility for each session from the same CME option settlements
(report date D-1), and its tercile within the phase (computed after the phase from that phase's sessions
only). Build only if the inputs are reachable (section 1).

**Context GEX tags (per trade, AT_ENTRY):**
- `hvl_side`: ABOVE / BELOW / AT (within 1 tick): price at entry vs HVL.
- `cr_ps_width`: call resistance minus put support, in points.
- `pin_zone`: after 13:00 CT, the largest 0DTE open-interest strike (the 0DTE level from the frozen GEX
  method) and the entry's distance to it in points; before 13:00 CT, NOT_APPLICABLE. "Pin zone" = within 10
  points (ours, frozen here, the GEX distance rule).
- `pc_gamma_ratio`: the put/call gamma ratio value only (absolute put gamma / absolute call gamma from the same
  replica calculation, ours, frozen here). Value only; no rule uses it.

**Splits (fields, used at Phase 2 end):** gamma regime (positive, negative), time of day of entry
(08:30-08:45, 08:45-10:00, 10:00-13:00, after 13:00 CT).

## 5b. Addendum, Nov 6, 2026 (registered before Phase 2; results-free)

**L1_PLAN_SIDE (per R4 candidate and trade from an intraday zone admitted by L1).** Finding from the Phase 1 P7 check:
L1 admits an intraday zone within 10 points of a plan DECISION zone but does not take that plan zone's side rule. Log,
for each such candidate and trade: the plan zone it was admitted by (label, lo, hi), the distance in points, the plan
zone's `long=` and `short=` values, and `l1_side_inherited` = ALLOWED (the plan side for the trade's direction is ANY,
RESPONSE or INITIATION and matches the setup), NONE (the plan side is NONE) or MISMATCH (the plan side allows only the
other setup family). Logged only; L1 is not changed. At the end of Phase 2 the count is reported, and the outcomes by
`l1_side_inherited` are part of the what-fails-and-why review. A rule that makes intraday zones inherit the plan side
would be a separately registered variant for Block 2, never applied to this replay.

## 6. Already built (Phase 0), carried forward unchanged

Wide-zone eligibility report; RISK_REJECT and RISK_BREACH_FILL logging; theoretical and realized net R fields.

## 7. Phase 1b acceptance criteria (all must hold)

- **D1 Trading untouched.** Rerun Phase 1 (Oct 22 - Nov 4, 2025) with every diagnostic on. The R1-R4 ledgers
  and candidate logs are byte-identical to the Phase 1 mechanics run (sha256 listed for each file).
- **D2 Point in time.** The lookahead audit, extended to every diagnostic field, shows 0 violations; every
  POST_ENTRY field is labelled.
- **D3 Unit tests.** Synthetic tests for: each of the four CVD_DIV cases; the 60-minute exclusion; PROVISIONAL
  vs AT_ENTRY; both CVD resets; cue (a) firing, not firing, and NOT_APPLICABLE after an M0 exit; M-J1 target
  choice (RUN, TP2, TP1); M-J2 with 1, 2 and 5 NQ; the 10 NQ and MNQ formulas on the U3 examples (60 ticks at
  3 NQ = $947.22 fits; 4 NQ = $1,262.96 does not); each GEX tag; the V2 seed giving the same twins twice.
- **D4 Coverage, counts only.** Per session and strategy: how many trades and candidates carry each diagnostic,
  and how many are NOT_APPLICABLE, DATA_MISSING or NOT_RUN. No outcome column in this table.
- **D5 CVD definition check (replay plan section 6; Book 1D P4).** For Oct 24, 27, 28 and 29, 2025: every
  CVD_DIV event (both resets), with swing times, prices, CVD values, case and timing, plus every swing pair
  excluded by the 60-minute window. Then the table below for Kyron to compare with Jeron's video. The
  algorithm is not required to find every divergence he points out; disagreements are documented, never tuned.

| Day | Jeron's swing (video; his times are probably ET) | Price | CVD | Expected case |
|---|---|---|---|---|
| Oct 29, 2025 (FOMC) | NY AM high, about 10:00-10:30 (09:00-09:30 CT if ET) | lower high | higher high | HIGH_ABSORPTION |
| Oct 28, 2025 | Low of day | lower low | higher low | LOW_EXHAUSTION |
| Oct 27, 2025 | 9:30 and 10:30 lows (08:30 and 09:30 CT if ET) | higher low | lower low | LOW_ABSORPTION |
| Oct 24, 2025 (CPI) | High | much higher high | lower high | HIGH_EXHAUSTION |

Video: "I made $50,000 this week, here's how", JeronTrades, Oct 29, 2025 (NQ examples at 1:17, 2:08, 2:41,
3:11, 3:46, 5:07; 4:18 is gold). For each row: did the frozen definition flag it (Y/N), with which swings, and
if not, why (swing not strict over 15 bars, beyond 60 minutes, CVD not diverging, other).

- **D6 No outcomes.** The Phase 1b report contains no P&L, R, win rate, or outcome-by-tag table.

## 8. Report

`Phase1b_report.md` with D1-D6, the NOT_RUN list, code SHA and file hashes. Upload only to
Book 1A Phase 1 - Shakedown (1-2B949RqsnfEN_ZP1Yqk4gtz5s7oJbxo). Commit subjects carry no results. Stop after
the report; Phase 2 needs Kyron's go.
