<!-- exported 2026-11-02 from Google Doc 1lrNk_8e5tRrbxh4ML5ah1URNIncdoLCghQ26zhId4K4, modifiedTime 2026-11-01T22:23:48.631Z -->
# **Book 1A – Phase 0 build checklist**

**Status:** v1, created Nov 1, 2026\. For whoever builds and runs the engine on Kyron's PC (K:\\Databento\_BackTesting, jeron\_harness / jeron\_engine). It lists what must be built and checked before the Book 1A replay starts. The rules themselves are in the Book 1A phase docs and "Book 1A – Replay plan"; if this checklist and the replay plan disagree, the replay plan wins.  
**Three priority groups.** P0 blocks the replay: nothing runs until every P0 item passes. P1 is needed only before the rule that uses it runs. P2 is diagnostic research and never holds up the primary replay (R1–R4 with M0).

## **General rules for every item**

> * Each item delivers: the code or config change, its version tag, the pass test result, and a short note in the Phase 0 report.  
> * A systematic difference is fixed in code, never absorbed by changing a threshold.  
> * No P\&L is looked at in Phase 0\. Parity days (Sep 28 and Oct 8, 2026\) and Phase 1 days (Oct 22 – Nov 4, 2025\) are mechanical checks only.  
> * Freeze before the first replay run: every rule and setting in the replay plan, dated, with one code tag.

## **P0: required before the replay (must pass)**

| \# | Item | Inputs | Pass test | Output | Depends on |
| :---- | :---- | :---- | :---- | :---- | :---- |
| P0.1 | Blind run setup | Fresh run folder; Book 1A docs, replay plan, raw data only | The runner cannot open Book 1 result files, reports or trade lists; a separate checker (person or agent) holds them | Folder layout and access note | none |
| P0.2 | Data unchanged since Book 1 | Block 1 MBO files, roll-day files, gex\_levels\_block1.csv, econ calendar | File list and checksums match the Book 1 Phase 0 gate 6 run; any change explained | Checksum table | P0.1 |
| P0.3 | Deterministic replay | Two sessions (one normal, one roll day: Dec 15, 2025\) | Same inputs run twice give identical trade ledgers and identical feature values, row for row | Diff report (must be empty) | P0.2 |
| P0.4 | R1 and R2 reproduction (E5) | A0 and C1 exactly as frozen; original Book 1 assumptions | The checker compares trade by trade, not totals: entry time, side, quantity, entry price, stop, target, exit time, exit price, exit reason and risk decision. All Book 1 A0 and C1 trades match; the runner sees only pass / fail and the mismatch list | Reconciliation table from the checker | P0.3 |
| P0.5 | Execution model v3.5 (Book 1A standard; P0.4 keeps each Book 1 phase's own model) | Fill model code | Unit tests: market entry 250 ms after bar close at best bid (sell) / ask (buy); target fills only 1 tick through; stop fills 1 tick adverse (below a long's stop, above a short's), 2 and 4 ticks in stress, measured from the first traded price at or beyond the stop when price jumps through it (v3.5); a gap-through test case for both sides; same-tick stop and target \= stop; commission \$2.87 per side per NQ in every net R; 14:55 CT flatten | Unit test log, long and short cases | P0.3 |
| P0.6 | 08:10 VWAP (AMT PO-8) | MBO trades, front contract | Matches a hand calculation at 08:10:00 CT on 2 normal days and both roll days (Dec 15, 2025; Mar 16, 2026): overnight session VWAP from 17:00 CT, weekly from Sunday 17:00 CT, ±1σ bands, trades before 08:10:00 only | Hand-check table | P0.3 |
| P0.7 | Map v2.4 Book 1A outputs | Map code (PO-1, PO-3, PO-6, PO-7, PO-9, PO-11, PO-13) | Rejection / flip zones, MAP4 areas, delta bands, acceptance states and DD\_EDGE match a hand-built list on 3 Phase 1 days; every zone frozen at 08:10 | Hand-check table, one per day | P0.6 |
| P0.8 | Source families (C1, C2) | Map zones, calculated GEX levels, VWAP | families= and levels= on each zone match a hand-built list; each family counts once; a gamma level counts inside the zone or within 10 points of its edge; DECISION needs 2+ families | Hand-check table | P0.7 |
| P0.9 | Context and side fields | Plan code (Phase 2, Phase 3\) | market\_context, draw\_status, draw=, balance=, balance\_poc=, value\_vs\_price, edge\_control, htf\_structure, first\_touch and side\_conflict are written for every zone before the open; most restrictive side rule wins | Sample plans for 3 days | P0.8 |
| P0.10 | Risk check and sizing (C3, U3) | Risk code | Unit tests: estimated risk \= (stop ticks \+ 2\) × \$5 × N \+ \$5.74 × N; largest stops that fit \$1,000: 1 NQ 196, 2 NQ 96, 3 NQ 63, 5 NQ 36, 10 NQ 16 ticks; 60-tick stop at 3 NQ \= $947.22accepted,4NQrejected;remainingdailybudget($2,000 minus realized losses minus open risk) applied; RISK\_REJECT when 1 NQ does not fit; RISK\_BREACH\_FILL when a realized loss exceeds plan; 3-trade cap and 2-loss halt stop the day, whichever comes first | Unit test log | P0.5 |
| P0.11 | R4 entries | S1.4 gates \+ RH1 \+ T8 \+ L1; single-print gate (U2) | On 3 Phase 1 days every R4 candidate shows the gate results, RH1 state, T8 and L1 checks; FZ1 is logged, never applied; all Phase 5 tags present (null when not measurable, never missing) | Candidate log sample | P0.9, P0.10 |
| P0.12 | M0 exits and R reporting | Exit code | M0 single target and zone stop; theoretical R and realized net R both written per trade; contract count recorded | Trade ledger sample | P0.11 |
| P0.13 | Timestamp and lookahead audit | Every level, zone, indicator and tag | Each value carries available\_at; an automated check asserts available\_at is before the decision timestamp for every entry. Covers swing confirmation (15 bars), the 08:10 VWAP, GEX inputs (D-1 report before 11 PM ET), map zones and L2 seconds | Audit log with zero violations | P0.11 |
| P0.14 | Freeze | All of the above | Replay plan settings dated, code tagged, Phase 0 report saved | Phase 0 report | P0.1 – P0.13 |

## **P1: needed before the rule that uses it**

| \# | Item | Pass test | If not ready |
| :---- | :---- | :---- | :---- |
| P1.1 | Gamma ranks (U6): rank strikes by net GEX from the same D-1 option files | Ranks match a hand ranking on 2 days; available before 08:10 | Ranks are left out of the GEX family (replay plan U6) |
| P1.2 | Calculated GEX levels per session (regime, call resistance, put support, HVL, 0DTE levels) | Already built for Book 1; confirm the same values and their available\_at | Replay cannot use the GEX family; stop and fix |

## **P2: diagnostics (after P0 passes; never block the primary replay)**

| \# | Item | Pass test before use |
| :---- | :---- | :---- |
| P2.1 | L2 diagnostics E1, E2, E4 (Book 1B) | L2F audit, fixed-price build and coverage list done; NOT\_VISIBLE vs DATA\_MISSING codes; only seconds completed before the decision used |
| P2.2 | CVD\_DIV and BREAKOUT\_SPEED (Book 1D) | CVD from signed executed trades, reset 17:00 CT (08:30 diagnostic), value at each price swing; AT\_ENTRY / PROVISIONAL / POST\_ENTRY timing; Phase 1 definition check on Oct 24, 27, 28, 29, 2025 documented, not tuned |
| P2.3 | Exit diagnostics: M-J1, M-J2, exit cue (a) | Same entry, stop, fills and commissions as M0; M-J2 only on 2+ NQ trades; stop never loosened |
| P2.4 | GEX diagnostics (Book 1C): V2 random-level twin, V3 second flip, V5 missing days, volatility control, Context GEX tags | Random levels generated with a fixed seed; ATM IV terciles from the same option files |
| P2.5 | Quantower-style power-trade rebuild (U2) | Logged only until its settings are set from documentation or reference examples |
| P2.6 | 10 NQ and MNQ feasibility | Uses the P0.10 formula with N \= 10 and with MNQ (\$0.50 per tick, \$1.88 round trip) |
| P2.7 | Parameter sensitivity runs (replay plan section 12\) | One parameter at a time; every other setting at baseline |
| P2.8 | All-time-high profile levels (O1, research) | Logged with their overlap with Book 1A zones |
| P2.9 | Every other logged tag in the phase docs | Present on every candidate; null when not measurable |

## **Phase 0 report (what to hand back)**

> * One line per item: pass / fail, version tag, date.  
> * The checker's R1 / R2 reconciliation table (P0.4) and the deterministic replay diff (P0.3).  
> * Hand-check tables (P0.6 – P0.9), unit test logs (P0.5, P0.10) and the lookahead audit (P0.13).  
> * A list of any P1 or P2 item not ready, and which replay path it takes.
