# A1: the exact difference between fill model v3.4 and v3.5 in Book 1's code

Written Nov 1, 2026 by the runner. **This is a report, not a choice.** For the P0.4 ledgers the runner keeps Book 1's
published per-phase setting: **v3.4 for Phases 1-2, v3.5 for Phases 3-4** (`run_r1_r2.py --fill book1`, the default;
`fill_model` is written on every ledger row and in `run_manifest.json`).

Source: `book1_ref/jeron_engine/fills.py` (sha256 1b93cbde…), `exit_replay.py` (857aa35c…), `daily_loop.py`
(c8bff8c3…), `arm_replay.py` (7d7ee554…), all byte-exact copies of the Drive mirror (`book1_ref/MANIFEST.md`).
No result file was opened. Result numbers that the design notes attach to the change are **not** repeated here.

## 1. There is one function, not two files

`fills.py` holds one simulator, `simulate(...)`. v3.4 and v3.5 are the two values of its `gap_fill` keyword
(default `False` = v3.4). Every other line of the function is shared. The whole v3.4 / v3.5 difference inside
`fills.py` is:

```python
# fills.py line 86-87: the switch
def simulate(tape, side, signal_bar_end, stop, target, latency_ms=LATENCY_MS, stop_slip=STOP_SLIP, flatten=FLATTEN,
             gap_fill=False):

# fills.py line 89-91: the docstring that names the two models
    gap_fill=False: v3.4 (stop fills at stop -/+ slip). gap_fill=True: fill model v3.5 rule 7b (frozen for Phase 3):
    the stop fills at the first traded price at or beyond it, -/+ slip. (v3.5's stop-change rules do not apply here:
    this stop never moves.)

# fills.py line 117-119: the only behavioural difference
        if hit_stop:
            base = (min(stop, trig) if side > 0 else max(stop, trig)) if gap_fill else stop
            ex = base - side * stop_slip * TICK
```

Written as a diff of the stop-fill rule alone:

```diff
  if hit_stop:
-     base = stop                                                    # v3.4
+     base = min(stop, trig) if side > 0 else max(stop, trig)        # v3.5 (gap_fill=True)
      ex = base - side * stop_slip * TICK
```

where `trig` is the price of the **first trade at or through the stop** in the triggering timestamp (line 111 / 114:
`if pr <= stop and not hit_stop: hit_stop, trig = True, pr` for a long; `pr >= stop` for a short).

So, for a **long**: v3.4 exit = `stop - slip`; v3.5 exit = `min(stop, first trade at or below the stop) - slip`.
For a **short**: v3.4 exit = `stop + slip`; v3.5 exit = `max(stop, first trade at or above the stop) + slip`.
When the triggering trade prints exactly at the stop the two are identical. They differ only when price jumps through
the stop without printing at it (a gap), and then v3.5 is worse for the trade by the size of the jump.

Unchanged between the two (lines 92-104, 108-116, 122-126): entry 250 ms after the signal bar close at the best
ask / bid, target fills only 1 tick through at the target price, same-timestamp tie = stop, flatten 14:55 CT at the
bid / ask, `DATA_END` when the tape runs out, `ticks` rounded to 2 decimals. Stop slippage (1 tick base; 2 and 4
stress) and entry latency (250 ms base; 1,000 ms stress) are parameters of both.

## 2. The same switch in the exit engine, plus two rules that cannot fire for M0

The C1 and A0 replays (`arm_replay.replay`) do **not** call `fills.simulate`; they call
`exit_replay.run_model(...)` → `exit_replay.replay(...)`, which carries the same stop-fill line and two further v3.5
rules for **moving** stops:

```python
# exit_replay.py line 41-42: the switches
def replay(tape, side, signal_end, stop, legs, stop_events=(), market_exit_at=None, on_leg_fill=None,
           stop_slip=1, latency_ms=LATENCY_MS, flatten=FLATTEN, gap_fill=False, stop_delay_ms=0, crossed=None):

# exit_replay.py line 126-128: identical stop-fill difference to fills.py
        if hit_stop:
            base = (min(stop, trig) if side > 0 else max(stop, trig)) if gap_fill else stop
            px = base - side * stop_slip * TICK
```

- **Rule 1, stop-change delay** (`stop_delay_ms`; line 69: `events = sorted(((t + delay, p, t) ...`): a stop change
  decided at a bar close goes active `stop_delay_ms` later (v3.5: 250; v3.4: 0). The old stop works until then.
- **Rule 2, crossed stop change** (`crossed`; lines 96-109): `None` = v3.4, the stop moves regardless. `"live"` =
  v3.5 as frozen: at the decision (the bar close) the quote is checked and a change already crossed (long bid <= new
  stop; short ask >= new stop) is not submitted; a submitted change crossed on arrival 250 ms later is rejected; the
  old stop stays. (`"live_market"`, `"reject"`, `"market"` are report-only variants.)
- **Rule 3, gap fill** (`gap_fill`): line 127 above, the same as `fills.py`.

**For M0 the stop never moves** (`run_model` passes no `stop_events` for M0, line 161), so rules 1 and 2 never
execute on A0 or C1; the only live difference for the P0.4 ledgers is rule 3, the gap fill.

## 3. How Book 1 selects the model (the "published setting" per phase)

| where | v3.4 | v3.5 |
|---|---|---|
| `daily_loop.fill_ledger(..., fill_model)` line 72-88 (`fills_model.csv`) | `fill_model="v3.4"` → `gap_fill=False` (default; "Phases 0-2") | `"v3.5"` → `gap_fill=True` ("frozen for Phase 3: stop gap fill, rule 7b") |
| `arm_replay.replay(..., fill=...)` line 196, 202 | `fill="v3.4"` → `kw = {}` (gap_fill False, delay 0, crossed None) | `fill="v3.5"` (the default) → `kw = dict(gap_fill=True, stop_delay_ms=250, crossed="live")` |
| `arm_replay.check_a0` line 293-295 (the A0 gate) | always `fill="v3.4"` | - |
| Phase 3 `build_inputs.py` line 54, Phase 4 `build_inputs.py` line 90 (daily-loop configs) | - | `fill_model="v3.5"` |
| Phase 3 `run_arms.gate` line 36 | reruns `fills_model_v34.csv` under v3.4 for the gate only | arm and A0 replays under v3.5 (line 9-10, 100-107) |
| `final_combination.py` line 71, 77; `run_holdout.py` line 55-56 (C1 and its paired A0) | - | `"v3.5"`, stop slip 1 (and 2 for the 2-tick line) |
| `phase_report.py` line 3, 110 (A0 report card) | "v3.4 fill model" | the Phase 4 card text is patched to say v3.5 (`run_holdout.py` line 113) |

Hence the published setting: **Phases 0-2 = v3.4** (daily-loop default, report card, A0 gate); **Phase 3 = v3.5**
(A0 rerun under v3.5 for the pairing, every arm, C1); **Phase 4 = v3.5** (A0 and C1). `run_r1_r2.py` reproduces
exactly this with `--fill book1`. For Phases 1-2 the R1 ledger also passes through `check_a0` (v3.4 gate against
`fills_model.csv`); for Phases 3-4 `check_a0` is not applicable (it is v3.4 by construction) and R1 is the plain
v3.5 replay, which is what Book 1 paired C1 against.

## 4. Why, as the code and design notes state it (no numbers repeated)

- `fills.py` docstring (line 89-90): the gap fill is "fill model v3.5 rule 7b (frozen for Phase 3)".
- `daily_loop.py` line 73: v3.4 is "Phases 0-2", v3.5 is "frozen for Phase 3: stop gap fill, rule 7b".
- `fill-model-v3.5-proposal.md` (design note, "Why", item 2): v3.4 "fills at stop -/+ slip even when the first trade
  at or beyond the stop is worse", i.e. v3.4 is optimistic on a jump through a working stop; rule 7b corrects that.
  Items 1 and the stop-change rules address exit models that move the stop (M2E, M2, M3), which Phase 2 showed hit
  cases v3.4 did not cover; they do not apply to A0 / C1 (M0).
- Design v3.10, "What changed" and "Fill model v3.5": v3.5 was "informed by Phase 2, frozen before Phase 3", frozen by
  Kyron on Oct 25, 2026 under tag `phase3-fill-v3.5`; "Phases 0-2 results stay on v3.4"; "A0 is rerun under v3.5 so
  every Phase 3 pairing uses one fill model". The policy choice for crossed changes is stated to have been named
  before results were seen.
- One stale comment to note: `exit_replay.py` line 48-49 still describes `gap_fill=True` as "sensitivity only, not
  the frozen model". That text predates the Oct 25 freeze; `fills.py`, `daily_loop.py`, `arm_replay.py` and the
  design doc all call v3.5 the frozen Phase 3 model. The code path is the same either way.

## 5. What this means for the Book 1A replay plan

The replay plan (section 4a) standardizes **v3.4** for the R1-R4 comparison. That is a separate run from the P0.4
reproduction and is unaffected by this report. P0.4 asks for A0 and C1 "exactly as frozen under the original Book 1
assumptions", which per section 3 is v3.4 / v3.4 / v3.5 / v3.5 by phase. `run_r1_r2.py --fill v3.4` produces the
standardized version when that run is called for.
