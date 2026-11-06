// =====================================================================================
//  JeronOrderFlowStrategy.cs  —  Jeron Order Flow AUTO-TRADING strategy (S1.4, Oct 24 2026)
//
//  WHAT THIS IS
//  JeronOrderFlowEventTracker v2.11 converted to a NinjaTrader 8 Strategy (S1.0 was built on v2.7). Every research rule, gate, flag,
//  outcome, retest path (v1 and order-flow v2), shadow and reversal row is the tracker's own code, unchanged.
//  The only new behaviour is a trading layer on top:
//   - An order is sent ONLY for a candidate the tracker marks Qualified (never Shadow, EventOnly, Pending,
//     AwaitConfirm). Initiations: at the trigger bar close. Responses: at the confirmation bar close.
//   - Market entry on the first tick after that bar closes; stop and target are the candidate's own
//     (SetStopLoss / SetProfitTarget by signal name). One position at a time.
//   - Claude review gate: the day's PreopenPlan must carry review=APPROVED (plan prompt v1.5). Claude can only
//     RESTRICT trading from the plan (review=LOG_ONLY, max_trades=, no_trade= windows); size stays here.
//   - Optional human gate: Approve_<date>.txt with approve=1 in the plan folder.
//   - Risk: max trades per day, max daily loss (ticks), max consecutive losses, last entry time, flatten
//     time, entry slippage check, live account blocked unless 'Allow live account' is on.
//   - Every order decision is logged in the same CSV (ORDER, ORDER_BLOCKED, FILL, TRADE_CLOSED, HALT,
//     FLATTEN, PROTECTIVE_REJECTED) next to the research rows, so the live fills can be compared with
//     the tracker's OUTCOME rows for the same EventId.
//
//  Requires JeronFlowShared.cs AND JeronOrderFlowEventTracker.cs in the same NinjaTrader install (the
//  JeronContextBias enum lives in the tracker file). Log files are JOFS_<instrument>_<stamp>.csv.
//  Run on a 1-minute BidAsk Volumetric chart with Tick Replay on (or Playback) for full evidence.
//  Historical bars without Tick Replay evaluate one bar late and have no Power/Deep trade evidence.
//
//   - S1.1: ATM-style TP / ENTRY / STP horizontal lines and the entry price marker, copied from
//     HarrisJigsawEventChainAutoTraderResearchV2 (HJ 2.17 display, all four settings). Display only:
//     HJ's X-cancel boxes and drag-to-move are not copied.
//   - S1.1: GEX lines (mq_*, gex_*) in the plan are logged by the tracker code exactly as v2.11 does; they never
//     open, block or size a trade. ES gate is log-only by default (v2.11).
//   - Run the STRATEGY INSTEAD OF the tracker indicator on the chart (it contains the tracker), so L2 files
//     and logs are not written twice.
//
//   - S1.2 FAST LOAD (like the map's 'Build from date'): only the last 'Evaluate last N trading days' (default 1 =
//     today's trading date, from its 17:00 CT open) is evaluated: signals, outcomes, research rows, plan reading and
//     logging. One warm-up day before it is read bar by bar (no signals, no rows) so ATR, EMA, prior RTH high/low
//     and prior RTH POC are ready at the open. Volumetric chart: the warm-up reads the Volumetric bars and ticks start
//     with the evaluated day. Plain bar chart + Tick Replay: ticks start with the warm-up day. Older ticks are ignored. 'Evaluate from date' overrides it for Playback; set N = 0 for every loaded day (Strategy
//     Analyzer). Rules are unchanged: a day inside the window is evaluated exactly as before.
//
//   - S1.3 (Oct 23): accounts named DEMO... count as simulated ('Simulated account name prefixes', default
//     Sim,Playback,Backtest,DEMO). DEMO5903068 is a NinjaTrader Simulation-connection account (display name DEMO, like Sim101).
//     On Oct 23 both Qualified signals on it were blocked LIVE_ACCOUNT_BLOCKED; the name prefix makes sure it is never blocked.
//
//   - S1.4 (Oct 24) — from the strategy-vs-transcripts review. ONE trading change, four logging additions:
//     0. 'Grades allowed' default is now A+,B+,B (was A+,B+,B,C). A counter-context candidate is graded C, and with C
//        allowed it traded on the same proof as a with-context trade, the opposite of Jeron ("buyers would have to be
//        the ones to prove to me", Part 4 ~10:38; Strategy-in-30 ~13:05). C candidates are still logged, followed and
//        reported (GRADE_NOT_ALLOWED on the ORDER_BLOCKED row). Put C back in the list to get the S1.3 behaviour.
//     Everything below is LOGGING ONLY: no gate, status, stop or target changes. Group "5e. S1.4 research flags".
//     2a. Passive trapped side (Part 3 ~35:22: "absorption, exhaustion, a lot of aggression with no reward, a lack of
//        aggression"). On RESPONSE candidates: trapped_passive (Y/N), trapped_passive_kind (HIGH_EFFORT_LOW_REWARD,
//        NO_AGGRESSION, WICK_NO_FOLLOW), passive_would_rescue (Y when NO_TRAPPED_SIDE_BEFORE_TRIGGER was the only event
//        reason and the passive check passed). Flag TRAPPED_PASSIVE when it passed and the aggressive check did not.
//     2b. Relative delta (Part 3 ~24:04: a -25% bar had "more aggressive selling ... than any other point of the
//        session"). delta_pct_vs_session = signed bar delta % in the trade's direction / the mean |delta %| of the
//        earlier bars of the same session segment (Asia / London / NY) today; delta_pct_session_avg = that mean;
//        delta_rank_20 = share of the last N bars (incl. this one) whose signed delta % is <= this bar's (1.00 = strongest).
//     2c. Reversal after a stop-out (Part 3 ~31:08, Strategy-in-30 ~16:40). A stop event is a live stop-loss fill
//        (LIVE_STOP) or a Qualified candidate's tracker outcome STOP_FIRST / AMBIGUOUS_SAME_BAR (OUTCOME_STOP, so the
//        backtest sees it without orders). An opposite-direction event-valid candidate at an overlapping zone within
//        'Reversal after stop window' bars writes a REVERSAL_CANDIDATE row (RetestModel=AFTER_STOP) followed to its own
//        REVERSAL_OUTCOME; the candidate gets the flag AFTER_STOP_REVERSAL and after_stop_src / after_stop_bars.
//        The 2-loss halt is unchanged.
//     2d. Fight at the level (Part 3 ~10:52: "we have a doji ... there's a fight at this level"). fight_flag (Y/N) and
//        fight_kind: BOTH_SIDES_EFFORT (a buy-effort bar and a sell-effort bar touching the zone within the lookback) and/or
//        DOJI_TWO_SIDED (a doji at the zone with buy AND sell imbalances). Flag FIGHT.
//     Every number in 2a-2d is OUR research parameter, not Jeron's.
//
//  The tracker v2.11 header follows (research history and rules).
// =====================================================================================
// =====================================================================================
//  JeronOrderFlowEventTracker.cs  —  Indicator 2: Jeron Order Flow Event Tracker
//
//  Decides whether aggressive executions MATTER at the locations marked before the open.
//  Four inputs:
//   1. Location map      : frozen preopen zones (with as-of time), session VWAP, session
//                          high/low, and separately recorded developing intraday zones
//                          (stacked diagonal imbalances, Power Trade locations)
//   2. Footprint evidence: bid/ask at price, 400% / 900% diagonal imbalance, delta, delta %
//   3. Aggressive events : 60/100 Deep Trade proxies and session Power Trade tiers
//                          (shared engine, Method B Consistent Bid/Ask by default)
//   4. State + scenario  : WAITING -> TESTED -> INITIATION or RESPONSE -> ACCEPTED / FAILED
//
//  No-hindsight rules built in
//   - Every bar is evaluated once, when it has CLOSED (first tick of the next bar).
//     The evidence timestamp is the bar close; nothing is ever relabelled retroactively.
//   - A failure is a NEW record with its own later timestamp, never an edit of the
//     initiation record.
//   - Outcomes (target/stop/MFE/MAE) are written as separate OUTCOME rows when resolved.
//   - Frozen zones only evaluate bars that START at or after the zones' as-of time.
//   - Every candidate is logged, including the ones our filters reject, with reasons.
//
//  v2 (Oct 11 2026) — two-branch entry model from the Jeron transcripts (Parts 2, 3, 4, 6)
//   - Setup family on every candidate: RESPONSE (one side trapped, other side steps in)
//     or INITIATION (one side drives through the level and is rewarded).
//   - RESPONSE needs a logged trapped side (aggression without follow-through, then a
//     delta flip) and, by default, a CONFIRMATION bar after the trigger: Jeron does not
//     enter on the trapping Power Trade itself, he waits for the next bar's response.
//   - INITIATION flags: ran through an opposing imbalance zone, tape speed (bar volume vs
//     recent bars), CVD aligned. Initiation through VWAP grades A+; a response alone B+.
//   - Stop by family: response = beyond the defended zone; initiation = far side of the
//     initiation bar.
//   - EVENT validity is logged separately from ENTRY qualification, so a real order-flow
//     event is never lost just because the target or reward:risk filter failed.
//   - EXIT_WARN rows: first opposing aggression that moves price against the trade;
//     two opposing effort bars in a row.
//   - Optional rejection of entries at the developing session POC (the middle of balance).
//   - Optional manual context bias (Bullish / Bearish / Balanced) for counter-context flags.
//
//  v2.1 (Oct 11 2026) — from the Oct 8 context notes (Preexcution v3 sections B, E, G, H) and the
//  first JOFT log (Oct 4-5 portion):
//   - Qualified-location gate: entries only at frozen zones, Power Trade zones and imbalance
//     stacks that meet a quality bar. Minor stacks are still tracked and logged.
//   - Targets only from qualified locations, session VWAP and session high/low.
//   - RESPONSE stop beyond the failed attempt's extreme (the rejection swing), not just the zone.
//   - Developing intraday zones expire at each session start (not carried into the next day).
//   - Entries limited to the NY session by default; other sessions log events only.
//   - Logging limited to the frozen-zone date(s) so the CSV stays small enough to review.
//   - CONFIG row at start (Tick Replay, footprint source, key settings).
//
//  v2.2 (Oct 12 2026) — four fixes from the Oct 8 Playback log review (JOFT_NQ_DEC26_20261011-172106):
//   1. RESPONSE trapped-side search reaches back to the zone's first touch (capped), and a rejected
//      trigger can be re-evaluated on the next few bars that close beyond the zone (LATE_TRIGGER).
//      Oct 8: the 9:29 trap at UPPER was 4 bars before the 9:33 trigger; 9:33 was weak, 9:34 was not.
//   2. One candidate per bar and direction. Overlapping zones that break on the same bar no longer
//      write up to 15 CANDIDATE rows; the best one is kept and the others are listed in its Detail.
//   3. Target = nearest qualified level that meets Min reward:risk (skipped nearer levels are flagged),
//      instead of the nearest level even when it fails reward:risk (POOR_REWARD_RISK fired 304 times).
//   4. Power Trades also aggregated by time cluster (Method C) alongside Consistent Bid/Ask, so one
//      order filled across a flickering quote is not split into several sub-300 pieces (12:29:43:
//      ~500 lots in ~100 ms split by bid changes). Overlapping Power zones from both methods merge.
//
//  v2.3 (Oct 12 2026) — reads the daily pre-open plan (PreopenPlan_<date>.txt) written by Claude from the
//  JeronPreopenMap packet (Jeron's HTF structure, value, overnight inventory, scenario plan, ES cross-check;
//  VIX / 10-year / news are logged only):
//   - Plan zones replace the Frozen zones for that date. DECISION zones are entry locations; TARGET zones are
//     targets only (TARGET_ONLY_ZONE). Frozen-zone labels starting T_ (map v2.0) are also targets only.
//   - Per-zone side rules: long=/short= ANY | RESPONSE | INITIATION | NONE (PLAN_SIDE_BLOCKED,
//     PLAN_NEEDS_RESPONSE, PLAN_NEEDS_INITIATION). Off with 'Enforce plan rules' = flags only.
//     alt_long=/alt_short= replace them after the plan is invalidated (default ANY: the thesis failed, so both
//     sides are open again, still subject to every order-flow gate). confidence= is logged only.
//   - 'Middle is lava' bands: no entries inside (MIDDLE_IS_LAVA).
//   - Plan context replaces the manual Context bias from the plan's as-of time; invalidate_above/below switch it
//     after 'Acceptance closes' closes beyond the level (PLAN_CONTEXT_CHANGE row).
//   - ES gate: longs need the last closed ES 1-minute bar above es_long_above, shorts below es_short_below
//     (ES_GATE_FAIL). Adds an ES 1-minute series.
//   - A plan that appears after its as-of time (live) applies from the bar after it was found (PLAN row says late).
//   - PLAN rows in the log record the plan id, context, rules and every change.
//
//  v2.4 (Oct 12 2026) — counter-context trades take the FIRST qualified target. Jeron, Part 2 ~1:24:00-1:27:00:
//  "if I'm shorting against where I know the market wants to go ... my only target would have to be VWAP or at
//  most the value area low"; Strategy-in-30 ~22:01: against the auction, tighter targets. With 'Counter-context:
//  first target only' on, a long in Bearish context or a short in Bullish context does not search past nearer
//  levels for Min reward:risk; if the first level is too close, POOR_REWARD_RISK fires (flag COUNTER_FIRST_TARGET).
//
//  v2.5 (Oct 16 2026) — RESEARCH LOGGING ONLY. No entry rule changed: the same candidates qualify as in v2.4.
//   1. Outcome window runs to the NY session end (SESSION_END with P/L at the close) instead of expiring after
//      15 bars. The old 15-bar result is still logged per candidate (Outcome15, PnL15Ticks) for comparison.
//      Every OUTCOME row now has PnLTicks and ExitPrice (same-bar stop+target counts as the stop).
//   2. Retest research paths: for every event-valid candidate, a hypothetical retest entry is followed for each
//      fail tolerance (default 2 and 8 ticks). One RETEST row per signal and tolerance holds BOTH paths:
//      immediate (the tracker's entry) and retest (zone revisited within the window, then a bar closes back in
//      the trade's direction; stop beyond the retest extreme; same target). No-retest reasons are logged.
//   3. Shadow candidates: candidates that per-bar dedupe used to drop are written as SHADOW rows (with ShadowOf
//      = the kept candidate) and get SHADOW_OUTCOME rows. They never count, alert or confirm as entries.
//
//  v2.6 (Oct 17 2026) — ORDER-FLOW RETEST (retest v2), RESEARCH LOGGING ONLY; entries unchanged. From the doc
//  "Order Flow Retest Entries: Research" (ATAS, LuxAlgo, NexusFi, Fabio/AMT playbooks). Runs beside retest v1:
//   - Price must LEAVE first: travel >= 'Min travel (ATR)' beyond the zone and >= 'Min bars' after the entry bar.
//     Touches before that are the break still forming (TouchesBeforeDeparture), not a retest.
//   - FIRST retest only. Its confirmation is order flow, not just a close: the opposite side shows up and fails
//     (absorption or trapped aggression at the zone) AND a fresh same-direction imbalance or a delta flip, on a
//     bar that closes back outside the zone in the trade's direction. No confirmation = the path ends.
//   - Skipped when the zone sits in the middle third of the plan balance (plan line balance=lo-hi; MIDDLE_OF_BALANCE).
//   - A full-bodied close back through the far edge fails it and logs a REVERSAL_CANDIDATE (Jeron M4) whose own
//     outcome is followed (REVERSAL_OUTCOME). Every candidate is tagged BreakStrength STRONG / ORDINARY.
//
//  v2.7 (Oct 20 2026) — AUTOMATED MORNING (map 08:20 CT -> Claude plan ~08:21-08:24 -> tracker activates 08:25)
//   1. Complete-plan check: a plan counts only when it has an 'end=1' line (Claude writes it last). A plan file
//      that is missing it, half-synced by Google Drive, unreadable or for the wrong date is ignored and read again on
//      the next bar close. The tracker no longer gives up for the day on one bad read; it stops looking only at
//      the NY session end. Each distinct read problem is logged once (PLAN_WAITING row).
//   2. 'Entries need a plan' (default on): until a plan is ACTIVE, every candidate logs as EventOnly with the
//      reason NO_PLAN (events, outcomes and research rows are still written). At 'Plan deadline' (default 08:30 CT)
//      a PLAN_MISSING row is written once if no plan is active.
//   3. Default folders: plans  G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\Pre-open Plan
//                       logs   G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs
//
//  v2.8 (Oct 20 2026) — LEVEL 2 CAPTURE (same idea as JeronChatGPTResearchTracker)
//   1. Records every Level 2 (market depth) update for the chart instrument: one CSV per hour, written to a local
//      staging folder and moved, once complete, to the L2 log folder
//      (default G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs\L2). Google Drive then uploads each
//      finished file once instead of re-uploading a growing file all day.
//   2. Keeps a live order book (by position, as NinjaTrader sends it) and attaches an L2 snapshot to every CANDIDATE
//      row and to retest entries: top-N bid/ask size, book imbalance, best bid/ask, depth age, update count, and
//      whether the book leaned the trade's way (L2Aligned).
//   3. 'Require L2 alignment for entries' is OFF by default: L2 is recorded and flagged for research, not used to
//      block entries, until the data shows it adds something.
//   L2 only exists live or in Playback with recorded Level 2 data. On ordinary historical bars the columns say
//   HISTORICAL_NO_L2; nothing is reconstructed or guessed. NinjaTrader's depth feed is aggregated by price level
//   (MBP); there are no order ids.
//
//  v2.10 (Oct 21 2026) — COMPARATIVE ORDER-FLOW RESEARCH RULES v1.1, RESEARCH LOGGING ONLY. No entry rule changed:
//  the same candidates qualify, with the same stops and targets, as in v2.8. (Named v2.10 because prompt v1.4 reserves
//  "v2.9" for the MenthorQ GEX logging build.) Source: "Comparative Order Flow Research Rules v1.1" and
//  "Jeron Research Rules v1.1 - XGBoost Log Measurements v1.0". Every number below is OUR research parameter, never a
//  trader's; new columns use the snake_case names of the XGBoost spec so the export maps 1:1.
//   1. Feature columns on every CANDIDATE / SHADOW row (groups G1-G4, G10, G12, G13): minutes since the open, plan
//      context / review / GEX regime and distance to mq_hvl (logged only), zone kind, side rule, confidence, width,
//      position in the balance, lava, VWAP distance in ATR and sigma, ES gate, stack, CVD slope, 1-min 21 EMA and CVD
//      average alignment (T7), displacement and move into the zone in ATR, trapped side, delta against the close, risk,
//      trade index of the day, P/L so far, Rizzo main-level acceptance, and whether the broken edge sits in a session LVN.
//   2. EXIT_MODEL rows (FAV03, CAR04): every event-valid candidate is followed again with Fabio's single target at the
//      balance POC (plan balance_poc=, else the prior RTH POC) and with Carmine's break-even stop (moved to entry once the
//      trade is up Car04BreakEvenR x risk, effective from the next bar). RIZ03 = trade_index_of_day on the candidate row.
//   3. RESEARCH_SIGNAL / RESEARCH_OUTCOME / RESEARCH_NOENTRY rows for the new detectors, each followed to the NY session end:
//      FAV01 impulse-leg LVN pullback (shadow study: the LVN is made after the open), FAV02 failed breakout of the plan
//      balance (FIRST_MOVE entry on the reclaim close and PULLBACK entry at the reclaim leg's LVN, target the balance POC),
//      CAR01 LVN return after a plan-zone candidate leaves the zone (passive side must hold), CAR03 stop run beyond PD /
//      overnight / plan-zone edges and reclaim, RIZ01 acceptance at the main (highest-confidence) decision zone.
//      Each row carries linked_event_id / jeron_status_same_bar so the logs show which setups Jeron's gates took or missed.
//   4. Plan lines balance_poc=, mq_hvl=, gex_regime=, review=, no_trade= are now read (logged only; they change nothing).
//   BOF01 = the existing RETEST rows plus bof01_broken_level_type; CAR02 = the existing L2 columns (PROXY until depth is bought);
//   RIZ02 and XMK01 are built in the Python export from the packet / an ES run, not here.
//
//  v2.11 (Oct 21 2026) — ES GATE LOG-ONLY (option 1 from the Oct 21 log review). The ES gate is our filter, not one of
//  Jeron's rules (his ES cross-check is pre-open context), and on Oct 21 it blocked three winning longs (09:19 +478,
//  09:24 +200, 09:44 +230). With 'ES gate blocks entries' OFF (the new default) a failed gate no longer adds the reason
//  ES_GATE_FAIL; the candidate gets the flag ES_GATE_FAIL_LOGGED instead and is judged on every other gate. Turn the
//  setting ON to get the v2.10 behaviour back. The ES series, the plan's es_long_above / es_short_below and es_gate_ok
//  are unchanged. New research columns on CANDIDATE / SHADOW rows (logged only):
//   - es_close, es_bar_age_min: the ES close used and how many minutes it sits before the NQ bar's evidence time
//     (normal = 0 or 1). es_bar_stale = Y when it is negative (ES bar AHEAD of the NQ bar) or more than 2 minutes old,
//     which is what happened for about 12 minutes after each chart reload on Oct 21 (08:42-08:53, 10:29-10:40).
//   - es_dist_gate_pts: ES close minus the gate level in the trade's direction (positive = gate passed).
//   - es_dist_settle_pts: ES close minus the plan line es_settle= (optional; blank if the plan has no es_settle line),
//     signed in the trade's direction.
//   - es_gate_blocks: Y if the gate was enforcing entries when the row was written.
//
//  Requires: JeronFlowShared.cs in the same folder.
//  Footprint: 1-minute BidAsk Volumetric chart recommended (read directly). Otherwise
//  the tracker builds its own footprint from ticks, which needs Tick Replay for history.
// =====================================================================================
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.DrawingTools;
using NinjaTrader.NinjaScript.Indicators.JeronShared;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
	public class JeronOrderFlowStrategy : Strategy
	{
		// ------------------------------------------------------------------------------
		//  Internal types
		// ------------------------------------------------------------------------------
		private enum ZState { Waiting, Tested, Initiation, Response, Accepted, Failed }

		private class ImbStack
		{
			public int Dir;
			public double Lo, Hi;
			public int Count;
			public double MinRatio;
			public bool AllStrong;
			public bool AnyZeroDen;
			public string Detail = "";
		}

		private class BarEvidence
		{
			public int Idx;
			public DateTime TimeLocal, TimeCt, StartCt;
			public JeronSession Session;
			public double O, H, L, C;
			public long Vol, BuyVol, SellVol, Delta;
			public double DeltaPct;
			public int BuyImb, SellImb, StrongBuyImb, StrongSellImb, MaxBuyStack, MaxSellStack, ZeroDenCells;
			public List<ImbStack> Stacks = new List<ImbStack>();
			public long LargeBuy, LargeSell;
			public string LargeBuyId = "", LargeSellId = "";
			public bool HighEffortLowReward;
			public string Source = "NONE";
			public double Vwap;
			// v2
			public double Cvd;            // session cumulative delta after this bar
			public double SpeedRatio;     // bar volume / average of the previous SpeedLookbackBars bars
			public double SessionPoc;     // developing session POC up to and including this bar
			public double Atr;            // v2.6: ATR of the 1-minute bars up to and including this bar
			// v2.10
			public Dictionary<long, long> Prof = new Dictionary<long, long>();   // volume at price (tick key) for this bar
			public double Ema = double.NaN;      // EMA of the close (ResearchEmaPeriod)
			public double CvdAvg = double.NaN;   // EMA of session CVD (ResearchCvdAvgPeriod)
			public double VwapSigma = double.NaN;
		}

		private class TickFootprint
		{
			public Dictionary<long, long[]> Levels = new Dictionary<long, long[]>();   // [0]=bid (sell aggr) [1]=ask (buy aggr)
			public long BuyVol, SellVol;
		}

		private class LargeAgg
		{
			public long MaxBuy, MaxSell;
			public string BuyId = "", SellId = "";
		}

		private class FrozenDef
		{
			public bool HasDate;
			public DateTime Date;
			public double Lo, Hi;
			public string Label;
		}

		// v2.3: the pre-open plan written by Claude (PreopenPlan_<date>.txt)
		private class PlanZone
		{
			public double Lo, Hi;
			public string Label = "PLAN";
			public bool TargetOnly;
			public string LongRule = "ANY", ShortRule = "ANY";
			public string AltLongRule = "ANY", AltShortRule = "ANY";   // used after the plan is invalidated
			public string Confidence = "";
			public string Note = "";
		}

		private class PreopenPlan
		{
			public DateTime Date = DateTime.MinValue;
			public int AsOfMin = -1;
			public string Id = "", Path = "";
			public bool HasContext;
			public JeronContextBias Context = JeronContextBias.None;
			public List<PlanZone> Zones = new List<PlanZone>();
			public List<double[]> Lava = new List<double[]>();
			public double InvAbove = double.NaN, InvBelow = double.NaN;
			public JeronContextBias InvAboveContext = JeronContextBias.Balanced, InvBelowContext = JeronContextBias.Balanced;
			public double EsLongAbove = double.NaN, EsShortBelow = double.NaN;
			public double EsSettle = double.NaN;   // v2.11: es_settle= (logged only)
			public double BalanceLo = double.NaN, BalanceHi = double.NaN;   // v2.6: balance=lo-hi (middle third skips retest v2)
			// v2.10 (logged only; none of these change an entry)
			public double BalancePoc = double.NaN;   // balance_poc=  (FAV03 / FAV02 target)
			public double Hvl = double.NaN;          // mq_hvl=       (price_vs_gamma_flip_atr)
			public string GexRegime = "";            // gex_regime=
			public string Review = "";               // review=
			public List<int[]> NoTrade = new List<int[]>();   // no_trade=HH:mm-HH:mm (minutes CT)
			public List<string> Info = new List<string>();
			public List<string> Warnings = new List<string>();
			public int MaxTrades = -1;   // S1.1 max_trades= (review restriction; -1 = use the strategy setting)
		}

		private class TrackedZone
		{
			public string Id;
			public string LocType;          // FROZEN_PREOPEN, INTRADAY_IMB_BUY/SELL, INTRADAY_POWER_BUY/SELL
			public bool IsFrozen;
			public int OriginDir;           // intraday zones: +1 buy-origin, -1 sell-origin
			public bool IsPower;            // created from a Power Trade cluster
			public long PowerVolume;
			public double Lo, Hi;
			public DateTime ActivateCt = DateTime.MinValue;
			public string AsOfText = "";
			public int CreatedBar = -1;
			public int StartBar = -1, EndBar = -1;
			public bool Active = true;
			public ZState State = ZState.Waiting;
			public int Dir;
			public int Approach;
			public double StopAnchor;
			public int AcceptCount;
			public bool Stalled, Retesting;
			public string CandidateId = "";
			public bool CandidateRejected;
			public List<string> History = new List<string>();
			// v2.1
			public bool Qualified;          // frozen, Power Trade, or imbalance stack meeting the quality bar
			public int StackCount;
			public bool AllStrong;
			// v2.2
			public int TouchBar = -1;           // first bar of the current visit (Waiting/Failed -> Tested)
			public int TriggerBar = -1;         // bar of the original break (initiation or response)
			public bool CandidateEventInvalid;  // the current candidate failed the EVENT gates (can re-trigger)
			public int Retriggers;
			// v2.3
			public bool FromPlan;
			public bool TargetOnly;            // target reference only, never an entry location
			public string LongRule = "ANY";     // ANY / RESPONSE / INITIATION / NONE
			public string ShortRule = "ANY";
			public string AltLongRule = "ANY";  // after plan invalidation (thesis failed)
			public string AltShortRule = "ANY";
			// v2.10
			public string Confidence = "";      // plan confidence= (low / med / high)
			public bool IsMain;                 // RIZ01 main level: the highest-confidence decision zone(s) of the plan
			public int EntryCount;              // candidates that passed the gates at this zone today (G13)
			public int RizAbove, RizBelow;      // consecutive closes above / below (RIZ01)
			public int RizSide;                 // last accepted side: +1 above, -1 below, 0 none yet
			public int RizAccepts;
			public double RizAcceptMin = double.NaN;   // minutes after the RTH open of the first acceptance
		}

		private class Candidate
		{
			public string Id;
			public TrackedZone Zone;
			public int Dir;
			public string Kind;
			public string Status;
			public double Entry, Stop, Target;
			public string TargetRef = "";
			public int TriggerBar;
			public double MfeTicks, MaeTicks;
			public int BarsSeen;
			public bool Resolved;
			// v2
			public string Family = "";       // RESPONSE / INITIATION
			public string Grade = "";        // A+ / B+ / B / C
			public bool EventValid;          // order-flow event itself is valid (independent of target/RR)
			public bool AwaitConfirm;        // RESPONSE waiting for the next bar's confirmation
			public string Flags = "";
			public int OppStreak;            // consecutive opposing effort bars since entry
			public bool WarnFirst, WarnDouble;
			// v2.2
			public double RR = double.NaN;
			public int LocRank;              // 4 frozen, 3 power, 2 qualified stack, 1 minor stack
			public int Seq;
			public Dictionary<string, string> Row;   // CANDIDATE row held until the bar's candidates are deduplicated
			public List<string> AlsoAt = new List<string>();
			// v2.5 research logging
			public bool IsShadow;            // dropped by per-bar dedupe; logged and followed, never counted
			public string ShadowOf = "";
			public DateTime SignalCt;        // bar close of the original trigger (before any confirmation)
			public DateTime SessionEndCt = DateTime.MaxValue;
			public string Outcome = "";
			public double PnL = double.NaN, ExitPrice = double.NaN;
			public string Outcome15 = "";
			public double Pnl15 = double.NaN;
			public List<RetestPath> Retests;
			// v2.6
			public double AtrAtSignal = double.NaN;
			public int TrigStack;            // largest stack in the trade's direction on the trigger bar
			public string BreakStrength = "";
			// v2.10 exit models (FAV03 single POC target, CAR04 break-even), research only
			public bool CountsAsEntry;       // passed the gates when committed (trade_index_of_day)
			public bool AltInit, ExitRowWritten, Fav03Done, Car04Done;
			public double AltRisk = double.NaN;
			public double Fav03Target = double.NaN, Fav03Pnl = double.NaN;
			public string Fav03Ref = "", Fav03Outcome = "";
			public double Car04Stop = double.NaN, Car04Pnl = double.NaN;
			public bool Car04Armed;
			public int Car04ArmBar = -1;
			public string Car04Outcome = "";
		}

		// v2.10: one research setup from the Comparative Order Flow Research Rules v1.1 (FAV01, FAV02, CAR01, CAR03, RIZ01).
		// Followed bar by bar like a retest path; never an entry, never counted.
		private class RWatch
		{
			public string Id = "", Rule = "", Stage = "";
			public int Dir;
			public int StartBar;             // stepping starts on the bar after this one
			public int Phase;                // 0 leg building, 1 LVN known (waiting for the touch), 2 at the LVN, 3 entered, 4 done
			public int OriginBar = -1, ExtremeBar = -1;
			public double OriginPrice = double.NaN, Extreme = double.NaN;
			public double MinImpulse;        // price units the leg must travel before its LVN is read (0 = none)
			public double AtrAt = double.NaN;
			public double LvnLo = double.NaN, LvnHi = double.NaN, LvnRatio = double.NaN;
			public int Bars, LegBars = -1, BarsToTouch = -1, TouchBar = -1;
			public double TouchExtreme = double.NaN;
			public bool OppAggr, Aggr;
			public bool NeedAggr, NeedPassive;
			public bool FixedTarget;
			public double FixedTargetPrice = double.NaN;
			public string FixedTargetRef = "";
			public double Entry = double.NaN, Stop = double.NaN, Target = double.NaN;
			public string TargetRef = "";
			public int EntryBar = -1, BarsInTrade;
			public DateTime EntryCt = DateTime.MinValue;
			public double Mfe, Mae, Pnl = double.NaN;
			public string Outcome = "", Reason = "";
			public DateTime SessionEndCt = DateTime.MaxValue;
			public TrackedZone Zone;
			public string Linked = "", LinkedStatus = "";
			public bool AfterAsOf, OriginPremarked;
			public Dictionary<string, string> Extra = new Dictionary<string, string>();
		}

		// v2.10 CAR03: one stop-run watch per level and side
		private class FlushState
		{
			public bool Active;
			public int StartBar;
			public double Extreme;
			public long DeltaSum;
			public int Signals;
		}

		// v2.6: failed order-flow retest -> the other side (Jeron M4 stop-and-reverse), followed for research
		private class ReversalCand
		{
			public string Id;
			public string Model = "v2";      // S1.4: v2 = failed order-flow retest, AFTER_STOP = after a stop-out
			public Candidate Src;
			public int Dir;
			public int StartBar;
			public double Entry, Stop, Target;
			public string TargetRef = "";
			public double Mfe, Mae;
			public int Bars;
			public bool Resolved;
		}

		// v2.5: one hypothetical retest entry per fail tolerance, followed alongside the immediate entry
		private class RetestPath
		{
			public int FailTicks;
			public int Phase;                // 0 waiting for a retest, 1 retest in progress, 2 entered, 3 finished
			public int StartBar;             // the immediate entry bar; the retest window starts on the next bar
			public int Bars;                 // bars watched in the window
			public int TouchBar = -1;
			public int BarsToTouch = -1;
			public double Extreme = double.NaN;
			public double DepthTicks = double.NaN;   // how far into the zone the retest went (ticks past the near edge)
			public bool Trapped;             // a retest bar showed opposing delta and failed to close through the zone
			public bool Entered;
			public int EntryBar = -1;
			public double Entry = double.NaN, Stop = double.NaN;
			public string Reason = "";
			public string Outcome = "";
			public double PnL = double.NaN;
			public double Mfe, Mae;
			public int BarsInTrade;
			public bool Written;
			// v2.6 order-flow retest (model v2)
			public string Model = "v1";
			public L2Snap EntryL2;           // v2.8: book at the retest entry
			public bool Departed;
			public double MaxTravel;         // furthest move beyond the near edge in the trade's direction (price units)
			public double TravelAtr = double.NaN;   // travel before the retest, in ATR at the signal
			public int TouchesBeforeDeparture;
			public double OppDelta;          // opposing delta summed over the retest bars (contracts, positive)
			public bool SawOppDelta, Absorption, FreshImb, DeltaFlip;
			public int ReactionBars = -1;    // bars from the first retest touch to the close back outside
			public string InMiddle = "";     // Y / N / "" (no balance in the plan)
		}

		private static readonly string[] LogColumns = new string[]
		{
			"RecordType", "EventId", "Mode", "Instrument", "EvidenceTimeLocal", "EvidenceTimeCT", "ProcessedTimeLocal",
			"Session", "LocationId", "LocationType", "ZoneLo", "ZoneHi", "Price", "NearestBoundary", "Direction",
			"PrevState", "State", "CandidateStatus", "Reasons", "EntryRef", "StopAnchor", "TargetRef", "TargetPrice",
			"RewardRisk", "BarVolume", "BuyVol", "SellVol", "Delta", "DeltaPct", "BuyImb", "SellImb",
			"StrongBuyImb", "StrongSellImb", "MaxBuyStack", "MaxSellStack", "ZeroDenCells", "LargeBuy", "LargeSell",
			"LargeMethod", "Displacement", "VWAP", "FootprintSource", "OutcomeType", "MFETicks", "MAETicks",
			"BarsToResolve", "SetupFamily", "Grade", "EventValid", "EntryStatus", "Flags", "CVD", "SpeedRatio", "SessionPOC",
			"Detail",
			// v2.5 research columns (appended so existing readers keep working)
			"PnLTicks", "ExitPrice", "Outcome15", "PnL15Ticks", "ShadowOf", "SignalTimeCT",
			"ImmediateOutcome", "ImmediatePnLTicks", "ImmediateMFETicks", "ImmediateMAETicks",
			"RetestFailTicks", "RetestOccurred", "RetestBarsElapsed", "RetestDepthTicks", "RetestTrapped", "RetestConfirmed",
			"RetestReason", "RetestEntry", "RetestStop", "RetestOutcome", "RetestPnLTicks", "RetestMFETicks", "RetestMAETicks",
			// v2.6 order-flow retest columns
			"RetestModel", "BreakStrength", "AtrAtSignal", "TravelBeforeRetestATR", "TouchesBeforeDeparture", "RetestOppDelta",
			"RetestAbsorption", "RetestFreshImbalance", "RetestDeltaFlip", "RetestReactionBars", "InBalanceMiddle",
			// v2.8 Level 2 snapshot columns
			"L2Status", "L2BidSize", "L2AskSize", "L2Imbalance", "L2Aligned", "L2AgeSec", "L2Events", "L2BestBid", "L2BestAsk",
			// v2.10 research rules v1.1 (snake_case = XGBoost Log Measurements v1.0 names)
			"rule_id", "rule_stage", "rule_version", "research_reason", "linked_event_id", "jeron_status_same_bar",
			"level_created_after_asof", "origin_premarked", "plan_id",
			"min_since_rth_open", "day_of_week", "in_no_trade_window",
			"plan_context", "plan_review", "gamma_regime", "price_vs_gamma_flip_atr", "balance_defined",
			"zone_kind", "side_rule", "zone_confidence", "zone_width_pts", "counter_context", "pos_in_balance", "in_middle_third",
			"in_lava", "dist_vwap_atr", "vwap_sigma", "es_gate_ok",
			"imb_stack_count", "cvd_slope_5", "ema21_aligned", "cvd_avg_aligned", "displacement_atr", "trapped_before",
			"delta_against_close", "move_into_zone_atr", "risk_ticks",
			"trade_index_of_day", "trades_at_zone_so_far", "session_pnl_ticks_so_far",
			"riz01_is_main_level", "riz01_accept_side", "riz01_min_to_accept", "riz01_with_acceptance",
			"bof01_broken_level_type", "bof01_edge_lvn_ratio",
			"lvn_lo", "lvn_hi", "lvn_vol_ratio", "leg_origin_price", "leg_extreme_price", "leg_atr", "leg_bars",
			"bars_to_lvn_touch", "lvn_touch_depth_ticks", "lvn_opp_aggression", "lvn_aggression", "lvn_in_plan_zone",
			"fav02_excursion_ticks", "fav02_excursion_bars", "fav02_poc", "fav02_poc_ref",
			"car03_level_type", "car03_level", "car03_flush_ticks", "car03_flush_atr", "car03_flush_delta", "car03_reclaim_bars",
			"fav03_target", "fav03_ref", "fav03_outcome", "fav03_pnl_ticks", "car04_outcome", "car04_pnl_ticks", "car04_be_bar",
			// v2.11 ES gate research columns (logged only)
			"es_close", "es_bar_age_min", "es_bar_stale", "es_dist_gate_pts", "es_dist_settle_pts", "es_gate_blocks",
			// S1.4 research flags (logged only)
			"trapped_passive", "trapped_passive_kind", "passive_would_rescue",
			"delta_pct_vs_session", "delta_pct_session_avg", "delta_rank_20",
			"fight_flag", "fight_kind", "after_stop_src", "after_stop_bars"
		};
		private const string ResearchRulesVersion = "v1.1";

		// ------------------------------------------------------------------------------
		//  State
		// ------------------------------------------------------------------------------
		private JeronFlowEngine engine;
		private JeronSessionClock clock;
		private JeronCsvLogger logger;
		private string logError = "";
		private string instrumentName = "";
		private double tickSize = 0.25;
		private NinjaTrader.NinjaScript.BarsTypes.VolumetricBarsType volType;
		private bool useVolumetric;
		private bool timeBasedBars;
		private SessionIterator sessionIterator;
		private DateTime tradingDate = DateTime.MinValue;

		private readonly object zLock = new object();
		private readonly List<TrackedZone> zones = new List<TrackedZone>();
		private readonly List<FrozenDef> frozenDefs = new List<FrozenDef>();
		private readonly List<Candidate> candidates = new List<Candidate>();
		private readonly Dictionary<int, TickFootprint> footprints = new Dictionary<int, TickFootprint>();
		private readonly Dictionary<int, LargeAgg> largeByBar = new Dictionary<int, LargeAgg>();
		private readonly Dictionary<int, BarEvidence> evidence = new Dictionary<int, BarEvidence>();
		private readonly List<TrackedZone> pendingPowerZones = new List<TrackedZone>();
		private int asOfMinutes = -1;
		private int seq;
		private int intradaySeq;
		private double cumPv, cumVol, completedVwap;
		private double sessHigh = double.MinValue, sessLow = double.MaxValue;
		private int labelBar = -1, labelStack;
		private long countQualified, countRejected, countPending;
		private DateTime lastStatusDraw = DateTime.MinValue;
		// v2 state
		private double sessCvd;
		private readonly Dictionary<long, long> sessProfile = new Dictionary<long, long>();
		private readonly List<long> recentVols = new List<long>();
		private long countEvents, countAplus, countConfirmed, countWarn;
		// v2.2 state
		private readonly List<Candidate> barCands = new List<Candidate>();
		private long countDuplicates, countLateTriggers, countPowerMerges, countTargetSkips;
		private SimpleFont labelFont;
		// v2.3 plan + ES gate state
		private PreopenPlan plan;
		private bool planActive, planInvalidated, planGaveUp;
		private DateTime planActiveCt = DateTime.MinValue;
		private int invAboveCount, invBelowCount;
		private string planError = "";
		private JeronContextBias effectiveContext = JeronContextBias.None;
		private int esIdx = -1;
		private double esClose = double.NaN;
		private DateTime esCloseCt = DateTime.MinValue;
		private long countPlanBlocks;
		// v2.7 automated-morning state
		private string planErrorLogged = "";
		private bool planMissingLogged;
		private int planDeadlineMin = -1;
		private long countNoPlan;
		// v2.8 Level 2 state (OnMarketDepth runs on a data thread; everything below is guarded by l2Lock / l2FileLock)
		private class L2Level { public double Price; public long Volume; }
		private class L2Snap
		{
			public string Status = "";
			public long Bid, Ask, Events;
			public double Imb = double.NaN, AgeSec = double.NaN, BestBid = double.NaN, BestAsk = double.NaN;
			public string Aligned = "";
		}
		private readonly object l2Lock = new object();
		private readonly object l2FileLock = new object();
		private readonly List<L2Level> l2Bids = new List<L2Level>();
		private readonly List<L2Level> l2Asks = new List<L2Level>();
		private long l2Events, l2Recorded, l2Dropped;
		private DateTime l2LastCt = DateTime.MinValue;
		private StreamWriter l2Writer;
		private string l2FilePath = "", l2FileHour = "", l2Folder = "", l2Staging = "", l2Error = "", l2RunStamp = "";
		private const string DefaultL2Folder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs\L2";
		// v2.5 research state
		private List<int> retestFailTicks = new List<int>();
		private long countShadows, countRetestRows, countRetestEntered, countSessionEnd;
		private BarEvidence lastEv;
		// v2.6 state
		private double atrVal = double.NaN, atrPrevClose = double.NaN;
		private int atrCount;
		private readonly List<ReversalCand> reversals = new List<ReversalCand>();
		private long countRetestV2Entered, countReversals;
		// S1.0 auto-trading state
		private readonly List<Candidate> entryQueue = new List<Candidate>();
		private Candidate liveCand;
		private string liveSignal = "";
		private bool entryPending, flattenSent, approvalOk;
		private int tradesToday, lossStreak, lastEntryMin = -1, flattenMin = -1;
		private double dailyPnlTicks, totalPnlTicks;
		private string haltReason = "";
		private long countOrders, countOrderBlocks, countFills, countTradesClosed;
		// S1.2 fast load window
		private DateTime evalStartDate = DateTime.MinValue, warmStartDate = DateTime.MinValue;
		private DateTime evalStartLocal = DateTime.MinValue, warmStartLocal = DateTime.MinValue;   // ticks before these are ignored
		private long countWarmupBars, countSkippedBars;
		private int reversalSeq;
		// v2.10 research-rule state
		private readonly List<RWatch> watches = new List<RWatch>();
		private int watchSeq;
		private long countResearchSignals, countResearchNoEntry, countExitRows;
		private readonly Dictionary<string, long> researchByRule = new Dictionary<string, long>();
		private double cumP2v;                         // session sum of typical^2 x volume (VWAP sigma)
		private double emaVal = double.NaN, cvdAvgVal = double.NaN;
		private readonly Dictionary<long, long> rthProfile = new Dictionary<long, long>();
		private double rthHigh = double.MinValue, rthLow = double.MaxValue, onHigh = double.MinValue, onLow = double.MaxValue;
		private double pdRthHigh = double.NaN, pdRthLow = double.NaN, prevRthPoc = double.NaN;
		private int dayEntryCount;
		private double sessionPnlTicks;
		private int[] fav01LastExtremeBar = new int[] { -1, -1 };   // [0] short leg, [1] long leg
		private readonly bool[] excActive = new bool[2];             // FAV02 balance excursion: [0] below, [1] above
		private readonly double[] excExtreme = new double[2];
		private readonly int[] excStartBar = new int[2];
		private readonly int[] excExtremeBar = new int[2];
		private readonly int[] excCount = new int[2];
		private readonly Dictionary<string, FlushState> flushStates = new Dictionary<string, FlushState>();
		// S1.4 research-flag state (logging only)
		private class StopEvt
		{
			public string SrcId = "", Source = "";
			public int Dir, Bar;
			public double Lo, Hi;
			public bool Used;
		}
		private readonly List<StopEvt> stopEvts = new List<StopEvt>();
		private readonly double[] segAbsDpSum = new double[3];   // mean |delta %| per session segment today (index = SegIndex)
		private readonly int[] segDpBars = new int[3];
		private long countPassiveTraps, countPassiveRescues, countFights, countAfterStopRev;

		private SharpDX.Direct2D1.Brush dxFrozen, dxBuyZone, dxSellZone, dxPowerBuyZone, dxPowerSellZone, dxPowerBuyEdge, dxPowerSellEdge, dxUp, dxDown, dxNeutral, dxText;

		// ==============================================================================
		//  Lifecycle
		// ==============================================================================
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description = "Jeron order-flow strategy: the tracker v2.11 research rules plus auto entries on Qualified candidates, gated by the Claude-reviewed pre-open plan.";
				Name = "JeronOrderFlowStrategy";
				Calculate = Calculate.OnEachTick;
				IsOverlay = true;
				DisplayInDataBox = true;
				DrawOnPricePanel = true;
				ScaleJustification = ScaleJustification.Right;
				AddPlot(new Stroke(Brushes.Goldenrod, 2), PlotStyle.Line, "SessionVwap");

				// 1. Locations — normally empty: each trading date's zones come from its PreopenPlan_<date>.txt.
				// Fill only as a fallback (e.g. paste JeronPreopenMap's FrozenZones line for dates without a plan).
				FrozenZones = "";
				ZonesDate = "";
				ZonesAsOfCT = "08:25";

				// 2. Footprint
				FootprintSource = JeronFootprintSource.Auto;
				ImbalanceRatioPct = 400;
				StrongImbalanceRatioPct = 900;
				UseLowLiquidityRatio = true;
				LowLiquidityRatioPct = 300;
				MinCellVolume = 10;
				ZeroDenominatorCounts = true;
				MinStackForZone = 2;

				// 3. Aggressive executions
				AggressionMethod = JeronMethod.ConsistentBidAsk;
				DeepTradeBaseline = 60;
				DeepTradeStrict = 100;
				NyPowerTiers = "300,400,500";
				LowLiquidityPowerTiers = "150,200";
				LargeTradeEvidenceMin = 60;
				CreatePowerTradeZones = true;
				TimeClusterMaxGapMs = 250;
				TimeClusterPriceTolTicks = 2;

				// 4. State rules (OUR research parameters, not Jeron's)
				TouchToleranceTicks = 2;
				BreakTicks = 2;
				MinDisplacementTicks = 8;
				MinAbsDelta = 150;
				MinDeltaPct = 10;
				RequireImbalanceOrLargeTrade = true;
				AcceptBars = 3;
				ResponseLookbackBars = 3;
				RearmDistanceTicks = 40;
				StopAnchorMode = JeronStopAnchorMode.ZoneOppositeBoundary;
				StopBufferTicks = 2;
				MinRewardRisk = 1.5;
				MaxRiskTicks = 0;
				RequireVwapAlignment = false;
				EffortDeltaMin = 400;
				LowRewardTicks = 8;

				// 4b. Entry model v2 (Jeron transcripts Parts 2/3/4/6; numbers are OUR placeholders)
				UseSetupFamilies = true;
				RequireResponseConfirmation = true;
				RequireDeltaFlipForResponse = true;
				StopByFamily = true;
				SpeedLookbackBars = 10;
				MinSpeedRatio = 1.2;
				CvdLookbackBars = 3;
				FlagInitiationWithoutSpeed = true;
				RejectAtSessionPoc = true;
				PocBufferTicks = 8;
				ContextBias = JeronContextBias.None;
				RejectCounterContext = false;
				ExitWarnOppStreak = 2;

				// 4c. Location & session filters (v2.1)
				RequireQualifiedLocation = true;
				QualifiedStackMin = 3;
				StrongStackQualifies = true;
				TargetsQualifiedOnly = true;
				ResponseStopBeyondAttempt = true;
				CarryIntradayZones = false;
				NyOnlyEntries = true;
				TrackZoneDatesOnly = true;

				// 4d. v2.2 entry fixes (numbers are OUR placeholders)
				ResponseLookbackToFirstTouch = true;
				MaxResponseLookbackBars = 30;
				RetriggerBars = 3;
				DedupeCandidatesPerBar = true;
				TargetMinRRSearch = true;
				AddTimeClusterPowerTrades = true;

				// 5. Outcomes
				OutcomeBars = 15;
				// 5b. v2.5 research logging (logging only; entries unchanged)
				OutcomeToSessionEnd = true;
				LogRetestPaths = true;
				RetestWindowBars = 15;
				RetestFailTicksList = "2,8";
				LogShadowCandidates = true;
				// 5c. v2.6 order-flow retest (logging only; numbers are OUR placeholders)
				LogRetestV2 = true;
				RetestV2WindowBars = 30;
				RetestV2MinTravelAtr = 1.0;
				RetestV2MinBars = 3;
				RetestV2AtrPeriod = 14;
				RetestV2OppDeltaMin = 100;
				RetestV2FailTicks = 2;
				LogReversalCandidates = true;
				// 5d. v2.10 research rules v1.1 (logging only; every number is OUR placeholder, not a trader's)
				LogResearchRules = true;
				LogExitModels = true;
				Car04BreakEvenR = 1.0;
				LvnRowTicks = 4;
				LvnMaxRatio = 0.5;
				LvnEdgeExcludePct = 15;
				ResearchWindowBars = 30;
				ResearchFailTicks = 2;
				Fav01ImpulseAtr = 3.0;
				Fav01LookbackBars = 10;
				Fav02MaxPerSide = 3;
				Car01MinImpulseAtr = 1.0;
				Car03MinFlushTicks = 4;
				Car03MaxReclaimBars = 10;
				ResearchEmaPeriod = 21;
				ResearchCvdAvgPeriod = 21;
				MoveIntoZoneBars = 10;

				// 6. Sessions
				AsiaStartCT = "17:00";
				LondonStartCT = "01:00";
				NyStartCT = "08:30";
				NyEndCT = "15:00";

				// 7. Display
				ShowFrozenZones = true;
				ShowIntradayZones = true;
				ShowLabels = true;
				ShowIntradayLabels = false;
				ShowRejectedLabels = true;
				ShowVwap = true;
				ShowStatusPanel = true;
				MaxIntradayZones = 40;
				ZoneOpacity = 18;
				FrozenZoneBrush = Brushes.SteelBlue;
				BuyZoneBrush = Brushes.SeaGreen;
				SellZoneBrush = Brushes.IndianRed;
				PowerBuyZoneBrush = Brushes.DarkTurquoise;
				PowerSellZoneBrush = Brushes.DarkOrange;
				ShowPowerZoneTags = true;

				// 8. Logging
				ExportEventLog = true;
				LogFolder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs";   // v2.7

				// 1b. Pre-open plan (v2.3)
				UsePreopenPlan = true;
				PlanFolder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\Pre-open Plan";   // v2.7
				RequirePlanForEntries = true;   // v2.7
				PlanDeadlineCT = "08:30";       // v2.7

				// 9. Level 2 (v2.8)
				CaptureL2 = true;
				RecordAllL2Updates = true;
				L2Folder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs\L2";
				L2BookLevels = 5;
				L2MinUpdates = 20;
				L2MaxAgeSeconds = 5;
				L2ImbalanceThreshold = 0.60;
				RequireL2Alignment = false;
				PlanReplacesFrozenZones = true;
				EnforcePlanRules = true;
				RejectInLava = true;
				UseEsGate = true;
				EsGateBlocksEntries = false;   // v2.11: option 1, ES gate is log-only by default
				EsInstrument = "ES 12-26";
				TargetPrefixIsTargetOnly = true;
				CounterContextFirstTarget = true;

				// 9. Auto trading (S1.0)
				// 0. Fast load (S1.2)
				EvaluateLastDays = 1;
				WarmupDays = 1;
				EvaluateFromDate = "";

				AutoTradeEnabled = true;
				TradeQuantity = 1;
				TradeHistoricalBars = true;
				AllowLiveAccount = false;
				SimAccountPrefixes = "Sim,Playback,Backtest,DEMO";   // S1.3: DEMO5903068 = NinjaTrader Simulation account (display name DEMO)
				RequirePlanReview = true;
				RequireManualApproval = false;
				MaxTradesPerDay = 3;
				MaxDailyLossTicks = 400;
				MaxConsecutiveLosses = 2;
				LastEntryCT = "14:30";
				FlattenCT = "14:55";
				AllowedGrades = "A+,B+,B";   // S1.4: counter-context (C) logged, not traded
				// 5e. S1.4 research flags (logging only; numbers are OUR placeholders)
				LogS14Flags = true;
				PassiveMaxDeltaPct = 5;
				PassiveWickPct = 50;
				RelativeDeltaBars = 20;
				ReversalAfterStopBars = 10;
				FightLookbackBars = 3;
				DojiBodyPct = 20;
				MaxEntrySlippageTicks = 12;
				ExitOnFirstExitWarn = false;

				// 12. Trade lines (HJ 2.17 defaults)
				EnableTradeLines = true;
				EnableEntryPriceMarker = true;
				AtmPnlDisplay = JeronAtmPnlDisplayMode.Currency;
				AtmLabelOffsetPixels = 500;

				// NinjaTrader strategy settings
				EntriesPerDirection = 1;
				EntryHandling = EntryHandling.AllEntries;
				IsExitOnSessionCloseStrategy = true;
				ExitOnSessionCloseSeconds = 30;
				StartBehavior = StartBehavior.WaitUntilFlat;
				StopTargetHandling = StopTargetHandling.PerEntryExecution;
				RealtimeErrorHandling = RealtimeErrorHandling.IgnoreAllErrors;   // rejected stops are handled in OnOrderUpdate (flatten)
				Slippage = 1;
				BarsRequiredToTrade = 1;
				TraceOrders = false;
				IsInstantiatedOnEachOptimizationIteration = true;
			}
			else if (State == State.Configure)
			{
				if (UseEsGate && !string.IsNullOrWhiteSpace(EsInstrument))
				{
					AddDataSeries(EsInstrument.Trim(), BarsPeriodType.Minute, 1);
					esIdx = 1;
				}
			}
			else if (State == State.DataLoaded)
			{
				tickSize = Instrument != null ? Instrument.MasterInstrument.TickSize : 0.25;
				instrumentName = Instrument != null ? Instrument.FullName : "NA";
				labelFont = new SimpleFont("Arial", 10);

				clock = new JeronSessionClock();
				clock.AsiaStartMin = JeronSessionClock.ParseHhmm(AsiaStartCT, 17 * 60);
				clock.LondonStartMin = JeronSessionClock.ParseHhmm(LondonStartCT, 60);
				clock.NyStartMin = JeronSessionClock.ParseHhmm(NyStartCT, 8 * 60 + 30);
				clock.NyEndMin = JeronSessionClock.ParseHhmm(NyEndCT, 15 * 60);
				asOfMinutes = string.IsNullOrWhiteSpace(ZonesAsOfCT) ? -1 : JeronSessionClock.ParseHhmm(ZonesAsOfCT, -1);
				planDeadlineMin = string.IsNullOrWhiteSpace(PlanDeadlineCT) ? -1 : JeronSessionClock.ParseHhmm(PlanDeadlineCT, -1);   // v2.7
				lastEntryMin = string.IsNullOrWhiteSpace(LastEntryCT) ? -1 : JeronSessionClock.ParseHhmm(LastEntryCT, -1);   // S1.0
				flattenMin = string.IsNullOrWhiteSpace(FlattenCT) ? -1 : JeronSessionClock.ParseHhmm(FlattenCT, -1);
				ComputeEvalWindow();   // S1.2 fast load
				SetupL2Recorder();   // v2.8

				volType = Bars.BarsSeries.BarsType as NinjaTrader.NinjaScript.BarsTypes.VolumetricBarsType;
				useVolumetric = volType != null && FootprintSource != JeronFootprintSource.InternalTicks;

				BarsPeriodType baseType = BarsPeriod.BarsPeriodType == BarsPeriodType.Volumetric ? BarsPeriod.BaseBarsPeriodType : BarsPeriod.BarsPeriodType;
				timeBasedBars = baseType == BarsPeriodType.Minute || baseType == BarsPeriodType.Second || baseType == BarsPeriodType.Day;

				retestFailTicks = JeronFmt.ParseInts(RetestFailTicksList, new int[] { 2, 8 });

				engine = new JeronFlowEngine();
				engine.TickSize = tickSize;
				engine.Clock = clock;
				engine.IdPrefix = "JOFT-LT";
				engine.EnableBlock = AggressionMethod == JeronMethod.IndividualBlock;
				engine.EnableBidAsk = AggressionMethod == JeronMethod.ConsistentBidAsk;
				// v2.2: time clusters run alongside the chosen method so split fills still reach Power Trade size
				engine.EnableTimeCluster = AggressionMethod == JeronMethod.TimeCluster || AddTimeClusterPowerTrades;
				engine.TimeClusterMaxGapMs = TimeClusterMaxGapMs;
				engine.TimeClusterPriceTolTicks = TimeClusterPriceTolTicks;
				engine.DeepTiers = new List<long>();
				if (DeepTradeBaseline > 0) engine.DeepTiers.Add(DeepTradeBaseline);
				if (DeepTradeStrict > 0 && DeepTradeStrict != DeepTradeBaseline) engine.DeepTiers.Add(DeepTradeStrict);
				engine.DeepTiers.Sort();
				engine.NyPowerTiers = JeronFmt.ParseTiers(NyPowerTiers, new long[] { 300, 400, 500 });
				engine.LowLiqPowerTiers = JeronFmt.ParseTiers(LowLiquidityPowerTiers, new long[] { 150, 200 });
				engine.TierCrossed = OnEngineTierCrossed;
				engine.ClusterClosed = OnEngineClusterClosed;

				ParseFrozenZones();

				if (ExportEventLog)
				{
					string folder = string.IsNullOrWhiteSpace(LogFolder) ? DefaultLogFolder : LogFolder.Trim();   // v2.7: blank = the Drive logs folder
					string fileName = "JOFS_" + JeronFmt.SafeFileToken(instrumentName) + "_" + DateTime.Now.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture) + ".csv";
					logger = new JeronCsvLogger();
					if (!logger.Open(folder, fileName, LogColumns, out logError))
						logger = null;
					else
					{
						Dictionary<string, string> crow = NewRow("CONFIG");
						crow["ProcessedTimeLocal"] = JeronFmt.T(DateTime.Now);
						bool tr = Bars != null && Bars.IsTickReplay;
						crow["Detail"] = "version=S1.4(tracker 2.11) footprint=" + (useVolumetric ? "Volumetric" : "InternalTicks")
							+ " tickReplay=" + (tr ? "on" : "off")
							+ (tr ? "" : " WARNING: historical bars get NO large-trade/Power Trade evidence without Tick Replay (Playback real-time bars are fine)")
							+ " imb=" + JeronFmt.N(ImbalanceRatioPct, 0) + "/" + JeronFmt.N(StrongImbalanceRatioPct, 0) + "% lowLiq=" + (UseLowLiquidityRatio ? JeronFmt.N(LowLiquidityRatioPct, 0) + "%" : "off")
							+ " deep=" + JeronFmt.I(DeepTradeBaseline) + "/" + JeronFmt.I(DeepTradeStrict) + " nyPower=" + NyPowerTiers + " method=" + AggressionMethod.ToString()
							+ " zonesAsOf=" + ZonesAsOfCT + " frozenZones=" + JeronFmt.I(frozenDefs.Count)
							+ " context=" + ContextBias.ToString() + " families=" + (UseSetupFamilies ? "on" : "off")
							+ " qualifiedLoc=" + (RequireQualifiedLocation ? "on stack>=" + QualifiedStackMin.ToString(CultureInfo.InvariantCulture) : "off")
							+ " nyOnly=" + (NyOnlyEntries ? "on" : "off") + " zoneDatesOnly=" + (TrackZoneDatesOnly ? "on" : "off")
							+ " minRR=" + JeronFmt.N(MinRewardRisk, 2) + " maxRiskTicks=" + JeronFmt.I(MaxRiskTicks)
							+ " respLookback=" + (ResponseLookbackToFirstTouch ? "firstTouch<=" + MaxResponseLookbackBars.ToString(CultureInfo.InvariantCulture) : ResponseLookbackBars.ToString(CultureInfo.InvariantCulture))
							+ " retrigger=" + RetriggerBars.ToString(CultureInfo.InvariantCulture)
							+ " dedupe=" + (DedupeCandidatesPerBar ? "on" : "off") + " targetMinRR=" + (TargetMinRRSearch ? "on" : "off")
							+ " timeClusterPower=" + (AddTimeClusterPowerTrades ? "on gap=" + TimeClusterMaxGapMs.ToString(CultureInfo.InvariantCulture) + "ms tol=" + TimeClusterPriceTolTicks.ToString(CultureInfo.InvariantCulture) + "t" : "off");
						crow["Detail"] = crow["Detail"] + " plan=" + (UsePreopenPlan ? "on folder=" + PlanFolderPath() + " replaceFrozen=" + (PlanReplacesFrozenZones ? "on" : "off")
							+ " enforceRules=" + (EnforcePlanRules ? "on" : "off") + " lava=" + (RejectInLava ? "on" : "off") : "off")
							+ " esGate=" + (esIdx > 0 ? EsInstrument + (EsGateBlocksEntries ? " blocks" : " logOnly") : "off") + " targetPrefixT=" + (TargetPrefixIsTargetOnly ? "on" : "off")
							+ " counterFirstTarget=" + (CounterContextFirstTarget ? "on" : "off")
							+ " outcomeWindow=" + (OutcomeToSessionEnd ? "sessionEnd(+" + OutcomeBars.ToString(CultureInfo.InvariantCulture) + "-bar snapshot)" : OutcomeBars.ToString(CultureInfo.InvariantCulture) + "bars")
							+ " retestPaths=" + (LogRetestPaths ? "on window=" + RetestWindowBars.ToString(CultureInfo.InvariantCulture) + " failTicks=" + RetestFailTicksList : "off")
							+ " shadows=" + (LogShadowCandidates ? "on" : "off")
							+ " retestV2=" + (LogRetestV2 ? "on window=" + RetestV2WindowBars.ToString(CultureInfo.InvariantCulture) + " minTravelAtr=" + JeronFmt.N(RetestV2MinTravelAtr, 2)
								+ " minBars=" + RetestV2MinBars.ToString(CultureInfo.InvariantCulture) + " atr=" + RetestV2AtrPeriod.ToString(CultureInfo.InvariantCulture)
								+ " oppDeltaMin=" + RetestV2OppDeltaMin.ToString(CultureInfo.InvariantCulture) + " failTicks=" + RetestV2FailTicks.ToString(CultureInfo.InvariantCulture) : "off")
							+ " reversals=" + (LogReversalCandidates ? "on" : "off")
							+ " l2=" + (CaptureL2 ? "on record=" + (RecordAllL2Updates && l2Staging.Length > 0 ? "on folder=" + l2Folder : "off" + (l2Error.Length > 0 ? " (" + l2Error + ")" : ""))
								+ " levels=" + L2BookLevels.ToString(CultureInfo.InvariantCulture) + " imb=" + JeronFmt.N(L2ImbalanceThreshold, 2)
								+ " gate=" + (RequireL2Alignment ? "on" : "off") : "off")
							+ " planEndLine=required entriesNeedPlan=" + (UsePreopenPlan && RequirePlanForEntries ? "on deadline=" + PlanDeadlineCT : "off")
							+ " researchRules=" + (LogResearchRules ? ResearchRulesVersion + " lvnRow=" + LvnRowTicks.ToString(CultureInfo.InvariantCulture) + "t lvnMaxRatio=" + JeronFmt.N(LvnMaxRatio, 2)
								+ " edgeExclude=" + LvnEdgeExcludePct.ToString(CultureInfo.InvariantCulture) + "% window=" + ResearchWindowBars.ToString(CultureInfo.InvariantCulture)
								+ " fav01=" + JeronFmt.N(Fav01ImpulseAtr, 2) + "ATR/" + Fav01LookbackBars.ToString(CultureInfo.InvariantCulture) + "bars car01Impulse=" + JeronFmt.N(Car01MinImpulseAtr, 2)
								+ "ATR car03Flush=" + Car03MinFlushTicks.ToString(CultureInfo.InvariantCulture) + "t/" + Car03MaxReclaimBars.ToString(CultureInfo.InvariantCulture) + "bars" : "off")
							+ " exitModels=" + (LogExitModels ? "on car04BE=" + JeronFmt.N(Car04BreakEvenR, 2) + "R" : "off")
							+ " ema=" + ResearchEmaPeriod.ToString(CultureInfo.InvariantCulture) + " cvdAvg=" + ResearchCvdAvgPeriod.ToString(CultureInfo.InvariantCulture)
							+ " entries=v2.8" + (esIdx > 0 && !EsGateBlocksEntries ? "+ES_GATE_LOG_ONLY" : "_UNCHANGED")
							+ " s14Flags=" + (LogS14Flags ? "on passiveMaxDp=" + JeronFmt.N(PassiveMaxDeltaPct, 1) + " wick=" + JeronFmt.N(PassiveWickPct, 0) + "% rankBars=" + RelativeDeltaBars.ToString(CultureInfo.InvariantCulture)
								+ " revAfterStop=" + ReversalAfterStopBars.ToString(CultureInfo.InvariantCulture) + "bars fight=" + FightLookbackBars.ToString(CultureInfo.InvariantCulture) + "bars doji<=" + JeronFmt.N(DojiBodyPct, 0) + "%" : "off");
						crow["Detail"] = crow["Detail"] + AutoConfigText();   // S1.0
						logger.Write(crow);
					}
				}
			}
			else if (State == State.Realtime)
			{
				if (logger != null) logger.Flush();
			}
			else if (State == State.Terminated)
			{
				if (logger != null)
				{
					// v2.5: anything still open when the data stops (Playback stopped early) is closed as DATA_END
					if (lastEv != null) CloseOpenAtDataEnd(lastEv);
					StringBuilder rsb = new StringBuilder();   // v2.10
					foreach (KeyValuePair<string, long> kv in researchByRule) rsb.Append(" ").Append(kv.Key).Append("=").Append(JeronFmt.I(kv.Value));
					Dictionary<string, string> row = NewRow("NOTE");
					row["ProcessedTimeLocal"] = JeronFmt.T(DateTime.Now);
					row["Detail"] = "SUMMARY qualified=" + JeronFmt.I(countQualified) + " rejected=" + JeronFmt.I(countRejected) + " pending=" + JeronFmt.I(countPending)
						+ (engine != null ? " trades=" + JeronFmt.I(engine.TradeCount) + " noQuote=" + JeronFmt.I(engine.MissingQuoteCount) + " largeClusters=" + JeronFmt.I(engine.EventCounts[0] + engine.EventCounts[1] + engine.EventCounts[2]) : "")
						+ " validEvents=" + JeronFmt.I(countEvents) + " aPlus=" + JeronFmt.I(countAplus) + " confirmed=" + JeronFmt.I(countConfirmed) + " exitWarns=" + JeronFmt.I(countWarn)
						+ " duplicatesMerged=" + JeronFmt.I(countDuplicates) + " lateTriggers=" + JeronFmt.I(countLateTriggers)
						+ " powerZoneMerges=" + JeronFmt.I(countPowerMerges) + " targetsBeyondNearest=" + JeronFmt.I(countTargetSkips)
						+ " shadows=" + JeronFmt.I(countShadows) + " retestRows=" + JeronFmt.I(countRetestRows) + " retestEntries=" + JeronFmt.I(countRetestEntered)
						+ " sessionEndOutcomes=" + JeronFmt.I(countSessionEnd) + " noPlanBlocks=" + JeronFmt.I(countNoPlan)
						+ " l2Updates=" + JeronFmt.I(l2Events) + " l2Recorded=" + JeronFmt.I(l2Recorded) + (l2Dropped > 0 ? " l2Dropped=" + JeronFmt.I(l2Dropped) : "")
						+ " retestV2Entries=" + JeronFmt.I(countRetestV2Entered) + " reversalCandidates=" + JeronFmt.I(countReversals)
						+ " researchSignals=" + JeronFmt.I(countResearchSignals) + " researchNoEntry=" + JeronFmt.I(countResearchNoEntry)
						+ " exitModelRows=" + JeronFmt.I(countExitRows) + (rsb.Length > 0 ? " byRule:" + rsb.ToString() : "")
						+ " s14 passiveTraps=" + JeronFmt.I(countPassiveTraps) + " passiveRescues=" + JeronFmt.I(countPassiveRescues)
						+ " fights=" + JeronFmt.I(countFights) + " afterStopReversals=" + JeronFmt.I(countAfterStopRev)
						+ " footprint=" + (useVolumetric ? "Volumetric" : "InternalTicks") + " tickReplay=" + (Bars != null && Bars.IsTickReplay ? "on" : "off");
					row["Detail"] = row["Detail"] + AutoSummaryText();   // S1.0
					logger.Write(row);
					logger.Dispose();
					logger = null;
				}
				CloseL2File(true);   // v2.8: finish and move the last hourly L2 file
				DisposeDx();
			}
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> SessionVwap
		{
			get { return Values[0]; }
		}

		// ==============================================================================
		//  Tick data: internal footprint + aggressive-execution engine
		// ==============================================================================
		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (engine == null || BarsInProgress != 0) return;
			// S1.2 fast load: Volumetric chart = ticks start with the evaluated day (the warm-up reads the Volumetric bars);
			// plain bar chart = ticks start with the warm-up day, so the internal footprint gives the prior RTH POC
			DateTime tickStart = useVolumetric ? evalStartLocal : warmStartLocal;
			if (tickStart != DateTime.MinValue && e.Time < tickStart) return;
			if (e.MarketDataType == MarketDataType.Bid) { engine.OnQuote(true, e.Price, e.Time); return; }
			if (e.MarketDataType == MarketDataType.Ask) { engine.OnQuote(false, e.Price, e.Time); return; }
			if (e.MarketDataType != MarketDataType.Last) return;

			DateTime ct = JeronSessionClock.ToCentral(e.Time, NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);
			engine.OnTrade(e.Time, ct, e.Price, e.Volume, e.Bid, e.Ask, State == State.Historical);

			if (!useVolumetric)
			{
				JeronAggSide side = engine.LastTradeSide;
				if (side == JeronAggSide.Unknown) return;
				int idx = BarIndexForTime(e.Time);
				TickFootprint fp;
				if (!footprints.TryGetValue(idx, out fp)) { fp = new TickFootprint(); footprints[idx] = fp; }
				long key = (long)Math.Round(e.Price / tickSize);
				long[] cell;
				if (!fp.Levels.TryGetValue(key, out cell)) { cell = new long[2]; fp.Levels[key] = cell; }
				if (side == JeronAggSide.Buy) { cell[1] += e.Volume; fp.BuyVol += e.Volume; }
				else { cell[0] += e.Volume; fp.SellVol += e.Volume; }
			}
		}

		// ==============================================================================
		//  v2.8 Level 2: record every depth update, keep the book, snapshot it for candidates
		// ==============================================================================
		protected override void OnMarketDepth(MarketDepthEventArgs e)
		{
			if (!CaptureL2 || e == null) return;
			if (e.Instrument != null && Instrument != null && e.Instrument.FullName != Instrument.FullName) return;   // chart instrument only (not ES)
			DateTime ct = JeronSessionClock.ToCentral(e.Time, NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);

			if (RecordAllL2Updates) RecordL2(e, ct);

			lock (l2Lock)
			{
				if (e.IsReset) { l2Bids.Clear(); l2Asks.Clear(); }
				List<L2Level> side = e.MarketDataType == MarketDataType.Bid ? l2Bids : (e.MarketDataType == MarketDataType.Ask ? l2Asks : null);
				if (side == null) return;
				int pos = e.Position;
				if (pos < 0) return;
				if (e.Operation == Operation.Add)
				{
					if (pos <= side.Count) side.Insert(pos, new L2Level { Price = e.Price, Volume = e.Volume });
				}
				else if (e.Operation == Operation.Update)
				{
					if (pos < side.Count) { side[pos].Price = e.Price; side[pos].Volume = e.Volume; }
					else if (pos == side.Count) side.Add(new L2Level { Price = e.Price, Volume = e.Volume });
				}
				else if (e.Operation == Operation.Remove)
				{
					if (pos < side.Count) side.RemoveAt(pos);
				}
				l2Events++;
				l2LastCt = ct;
			}
		}

		private void SetupL2Recorder()
		{
			l2Folder = string.IsNullOrWhiteSpace(L2Folder) ? DefaultL2Folder : L2Folder.Trim();
			l2RunStamp = DateTime.Now.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
			l2Staging = "";
			l2Error = "";
			if (!CaptureL2 || !RecordAllL2Updates) return;
			try
			{
				Directory.CreateDirectory(l2Folder);
				string staging = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "JeronLogs", "L2_staging");
				Directory.CreateDirectory(staging);
				l2Staging = staging;
				// finish moving hourly files left behind by an earlier run (crash, power cut)
				foreach (string old in Directory.GetFiles(staging, "L2Depth_*.csv"))
					MoveL2FileLater(old);
			}
			catch (Exception ex)
			{
				l2Error = "L2 folder error: " + ex.Message;
				l2Staging = "";
				Print("JeronOrderFlowEventTracker: " + l2Error);
			}
		}

		// one CSV per hour of market time (CT); written locally, moved to the L2 folder when the hour is complete
		private void RecordL2(MarketDepthEventArgs e, DateTime ct)
		{
			lock (l2FileLock)
			{
				if (l2Staging.Length == 0) return;
				try
				{
					string hour = ct.ToString("yyyy-MM-dd_HH", CultureInfo.InvariantCulture);
					if (l2Writer == null || hour != l2FileHour)
					{
						CloseL2File(false);
						l2FileHour = hour;
						l2FilePath = Path.Combine(l2Staging, "L2Depth_" + JeronFmt.SafeFileToken(instrumentName) + "_" + hour + "00CT_run" + l2RunStamp + ".csv");
						bool isNew = !File.Exists(l2FilePath);
						l2Writer = new StreamWriter(new FileStream(l2FilePath, FileMode.Append, FileAccess.Write, FileShare.Read), new UTF8Encoding(false));
						if (isNew) l2Writer.WriteLine("ReceivedUtc,MarketTimeCT,Instrument,Side,Operation,Position,Price,Volume,Reset,Seq");
					}
					l2Recorded++;
					l2Writer.WriteLine(DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss.fff", CultureInfo.InvariantCulture) + ","
						+ ct.ToString("yyyy-MM-dd HH:mm:ss.fff", CultureInfo.InvariantCulture) + ","
						+ instrumentName + ","
						+ e.MarketDataType.ToString() + "," + e.Operation.ToString() + ","
						+ e.Position.ToString(CultureInfo.InvariantCulture) + ","
						+ e.Price.ToString("R", CultureInfo.InvariantCulture) + ","
						+ e.Volume.ToString(CultureInfo.InvariantCulture) + ","
						+ (e.IsReset ? "1" : "0") + ","
						+ l2Recorded.ToString(CultureInfo.InvariantCulture));
					if (l2Recorded % 500 == 0) l2Writer.Flush();
				}
				catch (Exception ex)
				{
					l2Dropped++;
					if (l2Error.Length == 0) { l2Error = "L2 write error: " + ex.Message; Print("JeronOrderFlowEventTracker: " + l2Error); }
					try { if (l2Writer != null) l2Writer.Dispose(); } catch { }
					l2Writer = null;
				}
			}
		}

		private void CloseL2File(bool final)
		{
			lock (l2FileLock)
			{
				if (l2Writer == null) return;
				try { l2Writer.Flush(); l2Writer.Dispose(); } catch { }
				l2Writer = null;
				if (l2FilePath.Length > 0) MoveL2FileLater(l2FilePath);
				l2FilePath = "";
				l2FileHour = "";
			}
		}

		// move off the data thread: G: is Google Drive, a copy there can take a moment
		private void MoveL2FileLater(string path)
		{
			string dest = Path.Combine(l2Folder, Path.GetFileName(path));
			System.Threading.Tasks.Task.Run(() =>
			{
				try
				{
					if (!File.Exists(path)) return;
					Directory.CreateDirectory(Path.GetDirectoryName(dest));
					if (File.Exists(dest)) dest = Path.Combine(Path.GetDirectoryName(dest), Path.GetFileNameWithoutExtension(dest) + "_" + DateTime.Now.ToString("HHmmss", CultureInfo.InvariantCulture) + ".csv");
					File.Move(path, dest);
				}
				catch (Exception) { /* left in L2_staging; moved on the next start */ }
			});
		}

		private L2Snap TakeL2Snap(int dir, DateTime decisionCt)
		{
			L2Snap s = new L2Snap();
			if (!CaptureL2) { s.Status = "OFF"; return s; }
			if (State == State.Historical) { s.Status = "HISTORICAL_NO_L2"; return s; }
			lock (l2Lock)
			{
				s.Events = l2Events;
				if (l2Events < L2MinUpdates || l2Bids.Count == 0 || l2Asks.Count == 0) { s.Status = "DEPTH_UNAVAILABLE_OR_WARMING"; return s; }
				s.AgeSec = (decisionCt - l2LastCt).TotalSeconds;   // negative = book updated after the bar end (processed on the next tick)
				int n = Math.Max(1, L2BookLevels);
				for (int i = 0; i < l2Bids.Count && i < n; i++) s.Bid += l2Bids[i].Volume;
				for (int i = 0; i < l2Asks.Count && i < n; i++) s.Ask += l2Asks[i].Volume;
				s.BestBid = l2Bids[0].Price;
				s.BestAsk = l2Asks[0].Price;
			}
			if (s.AgeSec > L2MaxAgeSeconds) { s.Status = "DEPTH_STALE"; return s; }
			long total = s.Bid + s.Ask;
			if (total <= 0) { s.Status = "EMPTY_BOOK"; return s; }
			s.Imb = (double)s.Bid / total;
			bool aligned = dir > 0 ? s.Imb >= L2ImbalanceThreshold : s.Imb <= 1.0 - L2ImbalanceThreshold;
			s.Aligned = aligned ? "Y" : "N";
			s.Status = "OK";
			return s;
		}

		private static void FillL2(Dictionary<string, string> row, L2Snap s)
		{
			if (row == null || s == null) return;
			row["L2Status"] = s.Status;
			row["L2BidSize"] = s.Status == "OK" || s.Status == "DEPTH_STALE" ? JeronFmt.I(s.Bid) : "";
			row["L2AskSize"] = s.Status == "OK" || s.Status == "DEPTH_STALE" ? JeronFmt.I(s.Ask) : "";
			row["L2Imbalance"] = double.IsNaN(s.Imb) ? "" : JeronFmt.N(s.Imb, 3);
			row["L2Aligned"] = s.Aligned;
			row["L2AgeSec"] = double.IsNaN(s.AgeSec) ? "" : JeronFmt.N(s.AgeSec, 1);
			row["L2Events"] = s.Status == "OFF" || s.Status == "HISTORICAL_NO_L2" ? "" : JeronFmt.I(s.Events);
			row["L2BestBid"] = double.IsNaN(s.BestBid) ? "" : JeronFmt.P(s.BestBid);
			row["L2BestAsk"] = double.IsNaN(s.BestAsk) ? "" : JeronFmt.P(s.BestAsk);
		}

		private int BarIndexForTime(DateTime t)
		{
			if (CurrentBar < 0) return 0;
			if (timeBasedBars && t > Time[0]) return CurrentBar + 1;   // tick belongs to a bar not yet opened
			return CurrentBar;
		}

		private void OnEngineTierCrossed(JeronCluster c, JeronTier tier, bool first)
		{
			int idx = BarIndexForTime(c.LastLocal);
			LargeAgg agg;
			if (!largeByBar.TryGetValue(idx, out agg)) { agg = new LargeAgg(); largeByBar[idx] = agg; }
			if (c.Side == JeronAggSide.Buy && c.Volume > agg.MaxBuy) { agg.MaxBuy = c.Volume; agg.BuyId = c.Id; }
			if (c.Side == JeronAggSide.Sell && c.Volume > agg.MaxSell) { agg.MaxSell = c.Volume; agg.SellId = c.Id; }
		}

		private void OnEngineClusterClosed(JeronCluster c)
		{
			if (!CreatePowerTradeZones) return;
			List<long> power = engine.PowerTiersFor(c.Session);
			if (power.Count == 0 || c.Volume < power[0]) return;
			int idx = BarIndexForTime(c.LastLocal);
			int dir = c.Side == JeronAggSide.Buy ? 1 : -1;

			// v2.2: the same order can close as a Bid/Ask cluster AND a time cluster. Merge into one zone.
			TrackedZone twin = FindPowerTwin(dir, c.MinPrice, c.MaxPrice, idx);
			if (twin != null)
			{
				lock (zLock)
				{
					if (c.Volume > twin.PowerVolume) twin.PowerVolume = c.Volume;
					if (c.MinPrice < twin.Lo) twin.Lo = c.MinPrice;
					if (c.MaxPrice > twin.Hi) twin.Hi = c.MaxPrice;
					twin.History.Add("merged " + c.Id + " (" + c.Method.ToString() + ") vol=" + JeronFmt.I(c.Volume));
				}
				countPowerMerges++;
				return;
			}

			TrackedZone z = new TrackedZone();
			intradaySeq++;
			z.Id = (dir > 0 ? "PWR_BUY_" : "PWR_SELL_") + intradaySeq.ToString("000", CultureInfo.InvariantCulture);
			z.LocType = dir > 0 ? "INTRADAY_POWER_BUY" : "INTRADAY_POWER_SELL";
			z.OriginDir = dir;
			z.IsPower = true;
			z.Qualified = true;
			z.PowerVolume = c.Volume;
			z.Lo = c.MinPrice;
			z.Hi = c.MaxPrice;
			z.CreatedBar = idx;
			z.StartBar = idx;
			z.History.Add("created from " + c.Id + " (" + c.Method.ToString() + ") vol=" + JeronFmt.I(c.Volume));
			pendingPowerZones.Add(z);
		}

		// Same side, overlapping price (within the time-cluster tolerance), created on this bar or the one before.
		private TrackedZone FindPowerTwin(int dir, double lo, double hi, int idx)
		{
			double tol = TimeClusterPriceTolTicks * tickSize + tickSize * 0.01;
			foreach (TrackedZone p in pendingPowerZones)
				if (p.OriginDir == dir && Math.Abs(p.CreatedBar - idx) <= 1 && lo <= p.Hi + tol && hi >= p.Lo - tol) return p;
			lock (zLock)
			{
				for (int i = zones.Count - 1; i >= 0; i--)
				{
					TrackedZone t = zones[i];
					if (!t.IsPower || !t.Active || t.OriginDir != dir) continue;
					if (Math.Abs(t.CreatedBar - idx) <= 1 && lo <= t.Hi + tol && hi >= t.Lo - tol) return t;
				}
			}
			return null;
		}

		// ==============================================================================
		//  Bar processing
		// ==============================================================================
		protected override void OnBarUpdate()
		{
			if (esIdx > 0 && BarsInProgress == esIdx)
			{
				// v2.3 ES gate: the last FULLY CLOSED ES 1-minute bar. The tracker runs OnEachTick, so [0] is still
				// forming in real time / Tick Replay; on the first tick of a new bar, [1] is the bar that just closed.
				// (Historical without Tick Replay this lags one bar: conservative, never ahead of time.)
				if (CurrentBars[esIdx] >= 1 && IsFirstTickOfBar)
				{
					esClose = Closes[esIdx][1];
					esCloseCt = JeronSessionClock.ToCentral(Times[esIdx][1], NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);
				}
				return;
			}
			if (BarsInProgress != 0) return;

			CheckFlatten();   // S1.0
			UpdateAtmLastPrice();   // S1.1 trade lines

			if (CurrentBar == 0)
			{
				StartSession();
				cumPv = Typical[0] * Volume[0];
				cumP2v = Typical[0] * Typical[0] * Volume[0];   // v2.10
				cumVol = Volume[0];
				if (ShowVwap && cumVol > 0) Values[0][0] = cumPv / cumVol;
				return;
			}

			if (IsFirstTickOfBar)
			{
				// complete the previous bar (belongs to the session it traded in)
				cumPv += Typical[1] * Volume[1];
				cumP2v += Typical[1] * Typical[1] * Volume[1];   // v2.10
				cumVol += Volume[1];
				if (cumVol > 0) completedVwap = cumPv / cumVol;

				int mode = SessionMode();   // S1.2 fast load: 2 = evaluate, 1 = warm-up, 0 = skip
				if (mode == 2)
				{
					EvaluateBar(CurrentBar - 1);
					ProcessEntryQueue();   // S1.0: orders for candidates that became Qualified on the bar that just closed
				}
				else if (mode == 1) WarmupBar(CurrentBar - 1);
				else countSkippedBars++;

				if (Bars.IsFirstBarOfSession)
				{
					StartSession();
					cumPv = 0;
					cumP2v = 0;
					cumVol = 0;
				}
				Cleanup(CurrentBar);
			}

			double partialVol = cumVol + Volume[0];
			if (ShowVwap && partialVol > 0) Values[0][0] = (cumPv + Typical[0] * Volume[0]) / partialVol;

			if (ShowStatusPanel)
			{
				bool draw = State == State.Historical ? CurrentBar >= Count - 2 : (DateTime.Now - lastStatusDraw).TotalSeconds >= 1;
				if (draw)
				{
					lastStatusDraw = DateTime.Now;
					Draw.TextFixed(this, "JOFT_status", BuildStatus(), TextPosition.BottomLeft, Brushes.Gainsboro,
						new SimpleFont("Consolas", 11), Brushes.Transparent, Brushes.Black, 60);
				}
			}
		}

		private void StartSession()
		{
			if (sessionIterator == null) sessionIterator = new SessionIterator(Bars);
			sessionIterator.GetNextSession(Time[0], true);
			tradingDate = sessionIterator.ActualTradingDayExchange.Date;
			sessHigh = double.MinValue;
			sessLow = double.MaxValue;
			sessCvd = 0;
			sessProfile.Clear();
			recentVols.Clear();
			ResetResearchSession();   // v2.10
			// S1.4: relative-delta baselines and stop events are per trading date
			for (int i = 0; i < 3; i++) { segAbsDpSum[i] = 0; segDpBars[i] = 0; }
			stopEvts.Clear();

			lock (zLock)
			{
				foreach (TrackedZone z in zones)
				{
					if (z.Active && (z.IsFrozen || !CarryIntradayZones))
					{
						z.Active = false;
						z.EndBar = Math.Max(z.StartBar, CurrentBar - 1);
						if (!z.IsFrozen) z.History.Add("expired at session start");
					}
				}
			}

			// v2.3: plan for this trading date (written by Claude from the pre-open packet)
			plan = null;
			planActive = false;
			planInvalidated = false;
			planGaveUp = false;
			planError = "";
			planErrorLogged = "";
			planMissingLogged = false;
			ResetDailyTrading();   // S1.0
			planActiveCt = DateTime.MinValue;
			invAboveCount = 0;
			invBelowCount = 0;
			effectiveContext = ContextBias;
			if (SessionMode() < 2) return;   // S1.2 fast load: no plan, frozen zones or rows before the evaluation window
			bool planNow = UsePreopenPlan && TryLoadPlan(tradingDate);
			bool skipFrozen = planNow && PlanReplacesFrozenZones && plan.Zones.Count > 0;

			// create today's frozen zones (they activate at the as-of time)
			Dictionary<string, int> labelCounts = new Dictionary<string, int>();
			string onlyDate = (ZonesDate ?? "").Trim();
			foreach (FrozenDef def in frozenDefs)
			{
				if (def.HasDate)
				{
					if (def.Date.Date != tradingDate) continue;
				}
				else if (onlyDate.Length > 0)
				{
					DateTime d;
					if (!DateTime.TryParseExact(onlyDate, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d) || d.Date != tradingDate) continue;
				}
				if (skipFrozen) continue;
				int n;
				labelCounts.TryGetValue(def.Label, out n);
				n++;
				labelCounts[def.Label] = n;

				TrackedZone z = new TrackedZone();
				z.Id = def.Label + "_" + n.ToString("00", CultureInfo.InvariantCulture);
				z.LocType = "FROZEN_PREOPEN";
				z.IsFrozen = true;
				z.Qualified = true;
				z.TargetOnly = TargetPrefixIsTargetOnly && def.Label.StartsWith("T_");
				z.Lo = def.Lo;
				z.Hi = def.Hi;
				z.ActivateCt = asOfMinutes >= 0 ? tradingDate.AddMinutes(asOfMinutes) : DateTime.MinValue;
				z.AsOfText = asOfMinutes >= 0 ? z.ActivateCt.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + " CT" : "session start";
				z.CreatedBar = CurrentBar;
				lock (zLock) zones.Add(z);
			}
			if (planNow) ApplyPlan(PlanActivateCt(), false);
		}

		private bool DayIsTracked()
		{
			if (plan != null && plan.Date == tradingDate) return true;   // v2.3
			if (!TrackZoneDatesOnly) return true;
			bool anyDate = false;
			foreach (FrozenDef def in frozenDefs)
			{
				if (!def.HasDate) continue;
				anyDate = true;
				if (def.Date.Date == tradingDate) return true;
			}
			string onlyDate = (ZonesDate ?? "").Trim();
			if (onlyDate.Length > 0)
			{
				DateTime d;
				if (DateTime.TryParseExact(onlyDate, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d))
				{
					anyDate = true;
					if (d.Date == tradingDate) return true;
				}
			}
			return !anyDate;   // no dated map at all -> track everything
		}

		// ==============================================================================
		//  v2.3 Pre-open plan
		// ==============================================================================
		// v2.7: used when the folder boxes are blank (e.g. an older chart or template saved them empty)
		private const string DefaultPlanFolder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\Pre-open Plan";
		private const string DefaultLogFolder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\logs";

		private string PlanFolderPath()
		{
			return string.IsNullOrWhiteSpace(PlanFolder) ? DefaultPlanFolder : PlanFolder.Trim();   // v2.7: blank = the Drive plan folder
		}

		private bool TryLoadPlan(DateTime td)
		{
			string dateText = td.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
			string folder = PlanFolderPath();
			string specific = Path.Combine(folder, "PreopenPlan_" + JeronFmt.SafeFileToken(instrumentName) + "_" + dateText + ".txt");
			string generic = Path.Combine(folder, "PreopenPlan_" + dateText + ".txt");
			string path = File.Exists(specific) ? specific : (File.Exists(generic) ? generic : "");
			if (path.Length == 0) return false;
			string error;
			PreopenPlan p = ParsePlanFile(path, out error);
			// v2.7: a bad read is not final (Drive may still be syncing, or Claude may write a corrected plan).
			// The file is read again on the next bar close; TryLoadPlanLate stops looking at the NY session end.
			if (p == null) { NotePlanProblem(path, error); return false; }
			if (p.Date != td) { NotePlanProblem(path, "plan date " + p.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + " does not match " + dateText); return false; }
			planError = "";
			plan = p;
			return true;
		}

		// v2.7: log each distinct plan-read problem once (the status panel always shows the latest one)
		private void NotePlanProblem(string path, string error)
		{
			planError = error;
			if (error == planErrorLogged) return;
			planErrorLogged = error;
			Dictionary<string, string> row = NewRow("PLAN");
			row["ProcessedTimeLocal"] = JeronFmt.T(DateTime.Now);
			if (lastEv != null) row["EvidenceTimeCT"] = JeronFmt.T(lastEv.TimeCt);
			row["Detail"] = "PLAN_WAITING file=" + path + " problem=" + error + "; will read again on the next bar close";
			Write(row);
		}

		private PreopenPlan ParsePlanFile(string path, out string error)
		{
			error = "";
			List<string> lines = new List<string>();
			try
			{
				// v2.7: share read/write/delete so the tracker never blocks Google Drive while it replaces the file
				using (FileStream fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
				using (StreamReader sr = new StreamReader(fs, Encoding.UTF8, true))
				{
					string ln;
					while ((ln = sr.ReadLine()) != null) lines.Add(ln);
				}
			}
			catch (Exception ex) { error = "read failed: " + ex.Message; return null; }
			PreopenPlan p = new PreopenPlan();
			p.Path = path;
			int lineNo = 0;
			bool hasEnd = false;
			foreach (string raw in lines)
			{
				lineNo++;
				string line = raw.Trim();
				if (line.Length == 0 || line.StartsWith("#")) continue;
				int eq = line.IndexOf('=');
				if (eq <= 0) { p.Warnings.Add("line " + lineNo.ToString(CultureInfo.InvariantCulture) + ": no '='"); continue; }
				string key = line.Substring(0, eq).Trim().ToLowerInvariant();
				string val = line.Substring(eq + 1).Trim();
				double lo, hi, num;
				if (key == "end")
				{
					// v2.7: Claude writes end=1 as the plan's last line; anything after it is ignored
					if (val == "1") { hasEnd = true; break; }
					p.Warnings.Add("bad end '" + val + "' (expected end=1)");
				}
				else if (key == "date")
				{
					DateTime d;
					if (DateTime.TryParseExact(val, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d)) p.Date = d.Date;
					else p.Warnings.Add("bad date '" + val + "'");
				}
				else if (key == "asof") p.AsOfMin = JeronSessionClock.ParseHhmm(val, -1);
				else if (key == "plan_id") p.Id = val;
				else if (key == "context")
				{
					JeronContextBias cb;
					if (Enum.TryParse(val, true, out cb)) { p.Context = cb; p.HasContext = true; }
					else p.Warnings.Add("bad context '" + val + "'");
				}
				else if (key == "zone")
				{
					string[] parts = val.Split('|');
					if (parts.Length < 1 || !ParseRange(parts[0], out lo, out hi)) { p.Warnings.Add("bad zone '" + val + "'"); continue; }
					PlanZone z = new PlanZone();
					z.Lo = lo;
					z.Hi = hi;
					if (parts.Length > 1 && parts[1].Trim().Length > 0) z.Label = JeronFmt.SafeFileToken(parts[1].Trim().ToUpperInvariant());
					if (parts.Length > 2) z.TargetOnly = parts[2].Trim().ToUpperInvariant() == "TARGET";
					for (int i = 3; i < parts.Length; i++)
					{
						string part = parts[i].Trim();
						int e2 = part.IndexOf('=');
						if (e2 <= 0) continue;
						string k2 = part.Substring(0, e2).Trim().ToLowerInvariant();
						string v2 = part.Substring(e2 + 1).Trim();
						if (k2 == "long") z.LongRule = NormRule(v2, p);
						else if (k2 == "short") z.ShortRule = NormRule(v2, p);
						else if (k2 == "note") z.Note = v2;
						else if (k2 == "alt_long") z.AltLongRule = NormRule(v2, p);
						else if (k2 == "alt_short") z.AltShortRule = NormRule(v2, p);
						else if (k2 == "confidence") z.Confidence = v2;
					}
					p.Zones.Add(z);
				}
				else if (key == "lava")
				{
					if (ParseRange(val, out lo, out hi)) p.Lava.Add(new double[] { lo, hi });
					else p.Warnings.Add("bad lava '" + val + "'");
				}
				else if (key == "invalidate_above" || key == "invalidate_below")
				{
					string[] parts = val.Split('|');
					JeronContextBias cb = JeronContextBias.Balanced;
					if (!ParseNum(parts[0], out num)) { p.Warnings.Add("bad " + key + " '" + val + "'"); continue; }
					if (parts.Length > 1 && !Enum.TryParse(parts[1].Trim(), true, out cb)) cb = JeronContextBias.Balanced;
					if (key == "invalidate_above") { p.InvAbove = num; p.InvAboveContext = cb; }
					else { p.InvBelow = num; p.InvBelowContext = cb; }
				}
				else if (key == "es_long_above") { if (ParseNum(val, out num)) p.EsLongAbove = num; }
				else if (key == "es_short_below") { if (ParseNum(val, out num)) p.EsShortBelow = num; }
				else if (key == "es_settle") { if (ParseNum(val, out num)) { p.EsSettle = num; p.Info.Add(key + "=" + val); } else p.Warnings.Add("bad es_settle '" + val + "'"); }   // v2.11, logged only
				else if (key == "balance")
				{
					if (ParseRange(val, out lo, out hi)) { p.BalanceLo = lo; p.BalanceHi = hi; }
					else p.Warnings.Add("bad balance '" + val + "'");
				}
				// v2.10: read for research columns only (logged; nothing here changes an entry)
				else if (key == "balance_poc" || key == "mq_hvl")
				{
					double v = double.NaN;
					if (ParseRange(val, out lo, out hi)) v = (lo + hi) / 2.0;   // a band: use its middle
					else if (ParseNum(val, out num)) v = num;
					if (double.IsNaN(v)) p.Warnings.Add("bad " + key + " '" + val + "'");
					else if (key == "balance_poc") p.BalancePoc = v;
					else p.Hvl = v;
					p.Info.Add(key + "=" + val);
				}
				else if (key == "gex_regime") { p.GexRegime = val.Trim().ToUpperInvariant(); p.Info.Add(key + "=" + val); }
				else if (key == "review") { p.Review = val.Trim().ToUpperInvariant(); p.Info.Add(key + "=" + val); }
				else if (key == "no_trade")
				{
					string[] t = val.Split('-');
					int a = t.Length == 2 ? JeronSessionClock.ParseHhmm(t[0], -1) : -1;
					int b = t.Length == 2 ? JeronSessionClock.ParseHhmm(t[1], -1) : -1;
					if (a >= 0 && b > a) p.NoTrade.Add(new int[] { a, b });
					else p.Warnings.Add("bad no_trade '" + val + "'");
					p.Info.Add(key + "=" + val);
				}
				else if (key == "max_trades")   // S1.1 (strategy only)
				{
					int mt;
					if (int.TryParse(val.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out mt) && mt >= 0) p.MaxTrades = mt;
					else p.Warnings.Add("bad max_trades '" + val + "'");
					p.Info.Add(key + "=" + val);
				}
				else p.Info.Add(key + "=" + val);   // macro, news, context_note, source, note ... logged only
			}
			if (!hasEnd) { error = "plan incomplete: no end=1 line yet (still being written or synced)"; return null; }   // v2.7
			if (p.Date == DateTime.MinValue) { error = "plan has no date= line"; return null; }
			return p;
		}

		private static string NormRule(string v, PreopenPlan p)
		{
			string r = v.Trim().ToUpperInvariant();
			if (r == "ANY" || r == "RESPONSE" || r == "INITIATION" || r == "NONE") return r;
			p.Warnings.Add("unknown rule '" + v + "' (using ANY)");
			return "ANY";
		}

		private static bool ParseNum(string s, out double v)
		{
			return double.TryParse((s ?? "").Replace(",", "").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out v);
		}

		private static bool ParseRange(string s, out double lo, out double hi)
		{
			lo = hi = double.NaN;
			string[] b = (s ?? "").Split('-');
			double a, c;
			if (b.Length != 2 || !ParseNum(b[0], out a) || !ParseNum(b[1], out c)) return false;
			lo = Math.Min(a, c);
			hi = Math.Max(a, c);
			return true;
		}

		private DateTime PlanActivateCt()
		{
			if (plan != null && plan.AsOfMin >= 0) return tradingDate.AddMinutes(plan.AsOfMin);
			if (asOfMinutes >= 0) return tradingDate.AddMinutes(asOfMinutes);
			return tradingDate.AddMinutes(clock.NyStartMin);
		}

		// Plan found after its as-of time (live): applies from the end of the bar on which it was found.
		private void TryLoadPlanLate(BarEvidence ev)
		{
			if (tradingDate == DateTime.MinValue) return;
			if (ev.TimeCt >= tradingDate.AddMinutes(clock.NyEndMin)) { planGaveUp = true; return; }
			if (!TryLoadPlan(tradingDate)) return;
			DateTime act = PlanActivateCt();
			bool late = ev.TimeCt > act;
			ApplyPlan(late ? ev.TimeCt : act, late);
		}

		private void ApplyPlan(DateTime activateCt, bool late)
		{
			planActiveCt = activateCt;
			string asOfText = activateCt.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + " CT (plan " + (plan.Id.Length > 0 ? plan.Id : "") + ")";
			if (PlanReplacesFrozenZones && plan.Zones.Count > 0)
			{
				lock (zLock)
				{
					foreach (TrackedZone z in zones)
					{
						if (!z.Active || !z.IsFrozen || z.FromPlan) continue;
						z.Active = false;
						z.EndBar = Math.Max(z.StartBar, CurrentBar - 1);
						z.History.Add("replaced by plan");
					}
				}
			}
			Dictionary<string, int> labelCounts = new Dictionary<string, int>();
			foreach (PlanZone pz in plan.Zones)
			{
				int n;
				labelCounts.TryGetValue(pz.Label, out n);
				n++;
				labelCounts[pz.Label] = n;
				TrackedZone z = new TrackedZone();
				z.Id = "P_" + pz.Label + "_" + n.ToString("00", CultureInfo.InvariantCulture);
				z.LocType = pz.TargetOnly ? "PLAN_TARGET" : "PLAN_DECISION";
				z.IsFrozen = true;
				z.FromPlan = true;
				z.Qualified = true;
				z.TargetOnly = pz.TargetOnly;
				z.LongRule = pz.LongRule;
				z.ShortRule = pz.ShortRule;
				z.AltLongRule = pz.AltLongRule;
				z.AltShortRule = pz.AltShortRule;
				z.Confidence = pz.Confidence;   // v2.10
				z.Lo = pz.Lo;
				z.Hi = pz.Hi;
				z.ActivateCt = activateCt;
				z.AsOfText = asOfText;
				z.CreatedBar = CurrentBar;
				z.History.Add("plan zone long=" + pz.LongRule + " short=" + pz.ShortRule + " if_invalid long=" + pz.AltLongRule + " short=" + pz.AltShortRule
					+ (pz.Confidence.Length > 0 ? " confidence=" + pz.Confidence : "") + (pz.Note.Length > 0 ? " note=" + pz.Note : ""));
				lock (zLock) zones.Add(z);
			}
			string mainText = MarkMainLevels();   // v2.10 RIZ01
			Dictionary<string, string> row = NewRow("PLAN");
			row["ProcessedTimeLocal"] = JeronFmt.T(DateTime.Now);
			row["plan_id"] = plan.Id;
			row["Detail"] = "PLAN_LOADED" + (late ? "_LATE" : "") + " id=" + plan.Id + " file=" + plan.Path + " applies_from=" + asOfText
				+ " context=" + (plan.HasContext ? plan.Context.ToString() : "unchanged") + " zones=" + plan.Zones.Count.ToString(CultureInfo.InvariantCulture)
				+ " lava=" + plan.Lava.Count.ToString(CultureInfo.InvariantCulture)
				+ " invAbove=" + JeronFmt.P(plan.InvAbove) + " invBelow=" + JeronFmt.P(plan.InvBelow)
				+ " esLongAbove=" + JeronFmt.P(plan.EsLongAbove) + " esShortBelow=" + JeronFmt.P(plan.EsShortBelow)
				+ (plan.Warnings.Count > 0 ? " WARNINGS: " + string.Join(" / ", plan.Warnings.ToArray()) : "")
				+ (plan.Info.Count > 0 ? " INFO: " + string.Join(" / ", plan.Info.ToArray()) : "")
				+ " RESEARCH(v2.10): main=" + (mainText.Length > 0 ? mainText : "none") + " balancePoc=" + JeronFmt.P(plan.BalancePoc) + " hvl=" + JeronFmt.P(plan.Hvl)
				+ " review=" + plan.Review + " gexRegime=" + plan.GexRegime + " noTradeWindows=" + plan.NoTrade.Count.ToString(CultureInfo.InvariantCulture);
			Write(row);
		}

		private void UpdatePlanState(BarEvidence ev)
		{
			if (plan == null) return;
			if (!planActive)
			{
				if (ev.StartCt < planActiveCt) return;
				planActive = true;
				if (plan.HasContext) effectiveContext = plan.Context;
				Dictionary<string, string> row = NewRow("PLAN");
				row["EvidenceTimeCT"] = JeronFmt.T(ev.TimeCt);
				row["Detail"] = "PLAN_ACTIVE context=" + effectiveContext.ToString();
				Write(row);
			}
			if (planInvalidated) return;
			if (!double.IsNaN(plan.InvAbove))
			{
				invAboveCount = ev.C > plan.InvAbove ? invAboveCount + 1 : 0;
				if (invAboveCount >= Math.Max(1, AcceptBars)) { InvalidatePlan(ev, "above " + JeronFmt.P(plan.InvAbove), plan.InvAboveContext); return; }
			}
			if (!double.IsNaN(plan.InvBelow))
			{
				invBelowCount = ev.C < plan.InvBelow ? invBelowCount + 1 : 0;
				if (invBelowCount >= Math.Max(1, AcceptBars)) InvalidatePlan(ev, "below " + JeronFmt.P(plan.InvBelow), plan.InvBelowContext);
			}
		}

		private void InvalidatePlan(BarEvidence ev, string why, JeronContextBias next)
		{
			planInvalidated = true;
			JeronContextBias old = effectiveContext;
			effectiveContext = next;
			Dictionary<string, string> row = NewRow("PLAN");
			row["EvidenceTimeCT"] = JeronFmt.T(ev.TimeCt);
			row["Price"] = JeronFmt.P(ev.C);
			row["Detail"] = "PLAN_CONTEXT_CHANGE " + old.ToString() + " -> " + next.ToString() + "; accepted " + why + " (" + AcceptBars.ToString(CultureInfo.InvariantCulture) + " closes)";
			Write(row);
		}

		// Lava band and ES gate; flags may be null (confirmation re-check).
		private void PlanEntryChecks(List<string> reasons, List<string> flags, int d, double entry)
		{
			if (plan == null || !planActive) return;
			int before = reasons.Count;
			if (RejectInLava)
			{
				foreach (double[] band in plan.Lava)
					if (entry >= band[0] && entry <= band[1]) { reasons.Add("MIDDLE_IS_LAVA"); break; }
			}
			if (esIdx > 0)
			{
				double lvl = d > 0 ? plan.EsLongAbove : plan.EsShortBelow;
				if (!double.IsNaN(lvl))
				{
					if (double.IsNaN(esClose)) { if (flags != null) flags.Add("ES_NO_DATA"); }
					else if (d > 0 ? esClose <= lvl : esClose >= lvl)
					{
						// v2.11: blocks only with 'ES gate blocks entries' ON; otherwise flagged and logged
						if (EsGateBlocksEntries) reasons.Add("ES_GATE_FAIL");
						else if (flags != null) flags.Add("ES_GATE_FAIL_LOGGED");
					}
					else if (flags != null) flags.Add("ES_GATE_OK");
					if (flags != null && !double.IsNaN(esClose)) flags.Add("ES_" + JeronFmt.P(esClose).Replace(".", "_") + "_AT_" + esCloseCt.ToString("HHmm", CultureInfo.InvariantCulture));
				}
			}
			if (reasons.Count > before) countPlanBlocks++;
		}

		private void Cleanup(int current)
		{
			List<int> stale = new List<int>();
			foreach (int k in evidence.Keys) if (k < current - 200) stale.Add(k);
			foreach (int k in stale) evidence.Remove(k);
			stale.Clear();
			foreach (int k in footprints.Keys) if (k < current - 5) stale.Add(k);
			foreach (int k in stale) footprints.Remove(k);
			stale.Clear();
			foreach (int k in largeByBar.Keys) if (k < current - 5) stale.Add(k);
			foreach (int k in stale) largeByBar.Remove(k);
			candidates.RemoveAll(delegate(Candidate c) { return c.Resolved && RetestsDone(c) && ExitModelsDone(c); });   // v2.5/v2.10: keep until every research row is logged
		}

		private void EvaluateBar(int idx)
		{
			int ba = CurrentBar - idx;
			BarEvidence ev = BuildEvidence(idx, ba);
			evidence[idx] = ev;
			lastEv = ev;

			// v2.3: a plan written after the session started (live) is picked up here
			if (UsePreopenPlan && plan == null && !planGaveUp) TryLoadPlanLate(ev);

			// v2.1: only track the date(s) that have a frozen map, so logs stay focused and small
			if (!DayIsTracked())
			{
				UpdateOutcomes(ev);
				UpdateRetests(ev);
				UpdateResearch(ev);   // v2.10
				if (ev.H > sessHigh) sessHigh = ev.H;
				if (ev.L < sessLow) sessLow = ev.L;
				UpdateSessionLevels(ev);
				AddDeltaBaseline(ev);   // S1.4
				return;
			}

			// v2.3: plan activation at its as-of time, context invalidation
			UpdatePlanState(ev);

			// v2.7: one PLAN_MISSING row at the deadline if the morning automation did not deliver an active plan
			if (UsePreopenPlan && !planActive && !planMissingLogged && planDeadlineMin >= 0 && tradingDate != DateTime.MinValue
				&& ev.TimeCt >= tradingDate.AddMinutes(planDeadlineMin) && ev.TimeCt < tradingDate.AddMinutes(clock.NyEndMin))
			{
				planMissingLogged = true;
				Dictionary<string, string> mrow = NewRow("PLAN");
				mrow["EvidenceTimeCT"] = JeronFmt.T(ev.TimeCt);
				mrow["ProcessedTimeLocal"] = JeronFmt.T(DateTime.Now);
				mrow["Detail"] = "PLAN_MISSING no active plan by " + PlanDeadlineCT + " CT in " + PlanFolderPath()
					+ (plan != null ? " (plan loaded, activates " + planActiveCt.ToString("HH:mm", CultureInfo.InvariantCulture) + " CT)" : "")
					+ (planError.Length > 0 ? " last problem: " + planError : "")
					+ (RequirePlanForEntries ? "; entries blocked (NO_PLAN) until a plan is active" : "; entries NOT blocked ('Entries need a plan' is off)");
				Write(mrow);
			}

			// 0. RESPONSE candidates waiting for the bar after the trigger (v2)
			CheckConfirmations(ev);

			// 1. outcomes of earlier candidates (strictly later bars only) + exit warnings
			UpdateOutcomes(ev);
			// 1b. v2.5 retest research paths and the matched RETEST rows
			UpdateRetests(ev);

			// 2. activate intraday Power Trade zones created during earlier bars
			for (int i = pendingPowerZones.Count - 1; i >= 0; i--)
			{
				TrackedZone pz = pendingPowerZones[i];
				if (pz.CreatedBar <= idx)
				{
					pendingPowerZones.RemoveAt(i);
					AddIntradayZone(pz, ev);
				}
			}

			// 3. state machine on every active zone created before this bar
			TrackedZone[] snapshot;
			lock (zLock) snapshot = zones.ToArray();
			BarEvidence prev;
			evidence.TryGetValue(idx - 1, out prev);
			bool touchedFrozen = false;
			foreach (TrackedZone z in snapshot)
			{
				if (!z.Active) continue;
				if (z.IsFrozen)
				{
					if (z.ActivateCt != DateTime.MinValue && ev.StartCt < z.ActivateCt) continue;
					if (z.StartBar < 0)
					{
						z.StartBar = idx;
						Dictionary<string, string> row = ZoneRow("ZONE_ACTIVE", z, ev);
						row["Detail"] = "frozen preopen zone active; as-of " + z.AsOfText;
						Write(row);
					}
					if (ev.H >= z.Lo - TouchToleranceTicks * tickSize && ev.L <= z.Hi + TouchToleranceTicks * tickSize) touchedFrozen = true;
				}
				else if (z.CreatedBar >= idx) continue;
				EvaluateZone(z, ev, prev, idx);
			}

			// 3b. v2.2: one CANDIDATE row per bar and direction
			FlushBarCandidates();

			// 3c. v2.10 research rules v1.1 (logging only): step open setups, then look for new ones on this closed bar.
			// After the candidates so a setup on this bar can name the Jeron candidate of the same bar and direction.
			UpdateResearch(ev);
			if (LogResearchRules) DetectResearchSetups(ev, prev);

			// 4. new developing zones from this bar's stacked imbalances (usable from the next bar)
			foreach (ImbStack s in ev.Stacks)
			{
				if (s.Count < MinStackForZone) continue;
				TrackedZone z = new TrackedZone();
				intradaySeq++;
				z.Id = (s.Dir > 0 ? "IMB_BUY_" : "IMB_SELL_") + intradaySeq.ToString("000", CultureInfo.InvariantCulture);
				z.LocType = s.Dir > 0 ? "INTRADAY_IMB_BUY" : "INTRADAY_IMB_SELL";
				z.OriginDir = s.Dir;
				z.Lo = s.Lo;
				z.Hi = s.Hi;
				z.StackCount = s.Count;
				z.AllStrong = s.AllStrong;
				z.Qualified = s.Count >= QualifiedStackMin || (StrongStackQualifies && s.AllStrong);
				z.CreatedBar = idx;
				z.StartBar = idx;
				z.History.Add("stack " + s.Count.ToString(CultureInfo.InvariantCulture) + (s.AllStrong ? " (all >= strong ratio)" : ""));
				AddIntradayZone(z, ev);
				Dictionary<string, string> irow = ZoneRow("IMBALANCE", z, ev);
				irow["Detail"] = (z.Qualified ? "QUALIFIED " : "minor ") + "stack=" + s.Count.ToString(CultureInfo.InvariantCulture) + " minRatio=" + JeronFmt.N(s.MinRatio, 2)
					+ " tier=" + (s.AllStrong ? JeronFmt.N(StrongImbalanceRatioPct, 0) + "%" : JeronFmt.N(ActiveRatioPct(ev.Session), 0) + "%")
					+ " zeroDen=" + (s.AnyZeroDen ? "yes" : "no") + " cells[price:num/den]=" + s.Detail;
				Write(irow);
			}

			// 5. evidence row for bars that matter
			if (touchedFrozen || ev.LargeBuy > 0 || ev.LargeSell > 0 || ev.HighEffortLowReward || ev.MaxBuyStack >= MinStackForZone || ev.MaxSellStack >= MinStackForZone)
			{
				Dictionary<string, string> erow = NewRow("EVIDENCE");
				FillEvidence(erow, ev);
				erow["Price"] = JeronFmt.P(ev.C);
				erow["Displacement"] = JeronFmt.P(ev.C - ev.O);
				erow["Detail"] = (ev.HighEffortLowReward ? "HIGH_EFFORT_LOW_REWARD " : "") + (touchedFrozen ? "touches frozen zone" : "");
				Write(erow);
			}

			// 6. session extremes for target references (updated AFTER this bar was evaluated)
			if (ev.H > sessHigh) sessHigh = ev.H;
			if (ev.L < sessLow) sessLow = ev.L;
			UpdateSessionLevels(ev);   // v2.10 RTH / overnight extremes (also after evaluation)
			AddDeltaBaseline(ev);      // S1.4: this bar joins the baseline AFTER its own candidates were scored
		}

		private void AddIntradayZone(TrackedZone z, BarEvidence ev)
		{
			lock (zLock)
			{
				zones.Add(z);
				int active = 0;
				foreach (TrackedZone t in zones) if (!t.IsFrozen && t.Active) active++;
				if (active > MaxIntradayZones)
				{
					foreach (TrackedZone t in zones)
					{
						if (!t.IsFrozen && t.Active)
						{
							t.Active = false;
							t.EndBar = ev.Idx;
							t.History.Add("dropped (max intraday zones)");
							break;
						}
					}
				}
			}
			Dictionary<string, string> row = ZoneRow("ZONE_CREATED", z, ev);
			row["Detail"] = z.History.Count > 0 ? z.History[0] : "";
			Write(row);
		}

		// ==============================================================================
		//  Footprint evidence
		// ==============================================================================
		private double ActiveRatioPct(JeronSession session)
		{
			if (UseLowLiquidityRatio && clock.IsLowLiquidity(session)) return LowLiquidityRatioPct;
			return ImbalanceRatioPct;
		}

		private BarEvidence BuildEvidence(int idx, int ba)
		{
			BarEvidence ev = new BarEvidence();
			ev.Idx = idx;
			ev.TimeLocal = Time[ba];
			ev.TimeCt = JeronSessionClock.ToCentral(ev.TimeLocal, NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);
			ev.StartCt = ba + 1 <= CurrentBar ? JeronSessionClock.ToCentral(Time[ba + 1], NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo) : ev.TimeCt;
			ev.Session = clock.Classify(ev.TimeCt.AddSeconds(-1));
			ev.O = Open[ba];
			ev.H = High[ba];
			ev.L = Low[ba];
			ev.C = Close[ba];
			ev.Vol = (long)Volume[ba];
			ev.Vwap = completedVwap;

			Func<double, long> askAt = null;
			Func<double, long> bidAt = null;
			if (useVolumetric)
			{
				var vd = volType.Volumes[idx];
				ev.BuyVol = vd.TotalBuyingVolume;
				ev.SellVol = vd.TotalSellingVolume;
				ev.Delta = vd.BarDelta;
				ev.Source = "Volumetric";
				askAt = delegate(double p) { return vd.GetAskVolumeForPrice(p); };
				bidAt = delegate(double p) { return vd.GetBidVolumeForPrice(p); };
			}
			else
			{
				TickFootprint fp;
				if (footprints.TryGetValue(idx, out fp))
				{
					Dictionary<long, long[]> levels = fp.Levels;
					ev.BuyVol = fp.BuyVol;
					ev.SellVol = fp.SellVol;
					ev.Delta = fp.BuyVol - fp.SellVol;
					ev.Source = "InternalTicks";
					askAt = delegate(double p) { return CellAt(levels, p, 1); };
					bidAt = delegate(double p) { return CellAt(levels, p, 0); };
				}
			}
			ev.DeltaPct = ev.Vol > 0 ? 100.0 * ev.Delta / ev.Vol : 0;

			if (ev.Source != "NONE")
			{
				double ratio = ActiveRatioPct(ev.Session) / 100.0;
				double strong = StrongImbalanceRatioPct / 100.0;
				int nLevels = (int)Math.Round((ev.H - ev.L) / tickSize);
				ImbStack curBuy = null, curSell = null;
				for (int i = 0; i <= nLevels; i++)
				{
					double p = Instrument.MasterInstrument.RoundToTickSize(ev.L + i * tickSize);
					long pk = (long)Math.Round(p / tickSize);
					long pv;
					sessProfile.TryGetValue(pk, out pv);
					long cellVol = askAt(p) + bidAt(p);
					sessProfile[pk] = pv + cellVol;
					// v2.10: this bar's own volume at price (LVN legs) and the RTH-only profile (prior RTH POC)
					if (cellVol > 0)
					{
						ev.Prof[pk] = cellVol;
						if (ev.Session == JeronSession.NewYork)
						{
							long rv;
							rthProfile.TryGetValue(pk, out rv);
							rthProfile[pk] = rv + cellVol;
						}
					}

					// buy imbalance at p: ask volume at p vs bid volume one tick below
					long askP = askAt(p);
					long bidBelow = bidAt(Instrument.MasterInstrument.RoundToTickSize(p - tickSize));
					double r; bool zero;
					if (IsImbalance(askP, bidBelow, ratio, out r, out zero))
					{
						ev.BuyImb++;
						if (!zero && r >= strong) ev.StrongBuyImb++;
						if (zero) ev.ZeroDenCells++;
						if (curBuy == null) { curBuy = new ImbStack(); curBuy.Dir = 1; curBuy.Lo = p; curBuy.MinRatio = double.PositiveInfinity; curBuy.AllStrong = true; }
						AppendCell(curBuy, p, askP, bidBelow, r, zero, strong);
					}
					else if (curBuy != null) { CloseStack(ev, curBuy); curBuy = null; }

					// sell imbalance at p: bid volume at p vs ask volume one tick above
					long bidP = bidAt(p);
					long askAbove = askAt(Instrument.MasterInstrument.RoundToTickSize(p + tickSize));
					if (IsImbalance(bidP, askAbove, ratio, out r, out zero))
					{
						ev.SellImb++;
						if (!zero && r >= strong) ev.StrongSellImb++;
						if (zero) ev.ZeroDenCells++;
						if (curSell == null) { curSell = new ImbStack(); curSell.Dir = -1; curSell.Lo = p; curSell.MinRatio = double.PositiveInfinity; curSell.AllStrong = true; }
						AppendCell(curSell, p, bidP, askAbove, r, zero, strong);
					}
					else if (curSell != null) { CloseStack(ev, curSell); curSell = null; }
				}
				if (curBuy != null) CloseStack(ev, curBuy);
				if (curSell != null) CloseStack(ev, curSell);
			}

			LargeAgg agg;
			if (largeByBar.TryGetValue(idx, out agg))
			{
				ev.LargeBuy = agg.MaxBuy;
				ev.LargeSell = agg.MaxSell;
				ev.LargeBuyId = agg.BuyId;
				ev.LargeSellId = agg.SellId;
			}

			ev.HighEffortLowReward = Math.Abs(ev.Delta) >= EffortDeltaMin && Math.Abs(ev.C - ev.O) < LowRewardTicks * tickSize;

			// v2: CVD, tape speed proxy (volume vs recent bars), developing session POC
			sessCvd += ev.Delta;
			ev.Cvd = sessCvd;
			if (recentVols.Count > 0)
			{
				double sum = 0;
				foreach (long v in recentVols) sum += v;
				double avg = sum / recentVols.Count;
				ev.SpeedRatio = avg > 0 ? ev.Vol / avg : double.NaN;
			}
			else ev.SpeedRatio = double.NaN;
			recentVols.Add(ev.Vol);
			while (recentVols.Count > Math.Max(1, SpeedLookbackBars)) recentVols.RemoveAt(0);
			long bestVol = -1;
			foreach (KeyValuePair<long, long> kv in sessProfile)
				if (kv.Value > bestVol) { bestVol = kv.Value; ev.SessionPoc = kv.Key * tickSize; }
			// v2.6 ATR (simple average until the period fills, then Wilder smoothing; continuous across sessions)
			double tr = ev.H - ev.L;
			if (!double.IsNaN(atrPrevClose)) tr = Math.Max(tr, Math.Max(Math.Abs(ev.H - atrPrevClose), Math.Abs(ev.L - atrPrevClose)));
			atrCount++;
			int ap = Math.Max(1, RetestV2AtrPeriod);
			if (double.IsNaN(atrVal)) atrVal = tr;
			else atrVal += (tr - atrVal) / Math.Min(atrCount, ap);
			atrPrevClose = ev.C;
			ev.Atr = atrVal;
			// v2.10: 1-minute EMA of the close (continuous) and EMA of session CVD (restarts with the session CVD)
			double ka = 2.0 / (Math.Max(1, ResearchEmaPeriod) + 1.0);
			emaVal = double.IsNaN(emaVal) ? ev.C : emaVal + ka * (ev.C - emaVal);
			ev.Ema = emaVal;
			double kc = 2.0 / (Math.Max(1, ResearchCvdAvgPeriod) + 1.0);
			cvdAvgVal = double.IsNaN(cvdAvgVal) ? ev.Cvd : cvdAvgVal + kc * (ev.Cvd - cvdAvgVal);
			ev.CvdAvg = cvdAvgVal;
			if (cumVol > 0)
			{
				double mean = cumPv / cumVol;
				ev.VwapSigma = Math.Sqrt(Math.Max(0, cumP2v / cumVol - mean * mean));
			}
			return ev;
		}

		private long CellAt(Dictionary<long, long[]> levels, double price, int side)
		{
			if (levels == null) return 0;
			long[] cell;
			return levels.TryGetValue((long)Math.Round(price / tickSize), out cell) ? cell[side] : 0;
		}

		private bool IsImbalance(long num, long den, double ratio, out double r, out bool zero)
		{
			zero = den == 0;
			r = zero ? double.PositiveInfinity : (double)num / den;
			if (num < MinCellVolume) return false;
			if (zero) return ZeroDenominatorCounts;
			return r >= ratio;
		}

		private void AppendCell(ImbStack s, double p, long num, long den, double r, bool zero, double strong)
		{
			s.Hi = p;
			s.Count++;
			if (r < s.MinRatio) s.MinRatio = r;
			if (zero || r < strong) s.AllStrong = false;
			if (zero) s.AnyZeroDen = true;
			if (s.Detail.Length > 0) s.Detail += " ";
			s.Detail += JeronFmt.P(p) + ":" + JeronFmt.I(num) + "/" + JeronFmt.I(den);
		}

		private void CloseStack(BarEvidence ev, ImbStack s)
		{
			ev.Stacks.Add(s);
			if (s.Dir > 0 && s.Count > ev.MaxBuyStack) ev.MaxBuyStack = s.Count;
			if (s.Dir < 0 && s.Count > ev.MaxSellStack) ev.MaxSellStack = s.Count;
		}

		// ==============================================================================
		//  State machine
		// ==============================================================================
		private void EvaluateZone(TrackedZone z, BarEvidence ev, BarEvidence prev, int idx)
		{
			double tol = TouchToleranceTicks * tickSize;
			double brk = BreakTicks * tickSize;
			bool touch = ev.H >= z.Lo - tol && ev.L <= z.Hi + tol;
			int closePos = ev.C > z.Hi + brk ? 1 : (ev.C < z.Lo - brk ? -1 : 0);

			switch (z.State)
			{
				case ZState.Waiting:
				case ZState.Failed:
					if (!touch) return;
					double prevClose = prev != null ? prev.C : ev.O;
					if (prevClose > z.Hi) z.Approach = 1;
					else if (prevClose < z.Lo) z.Approach = -1;
					else z.Approach = ev.O >= (z.Lo + z.Hi) / 2.0 ? 1 : -1;
					z.CandidateId = "";
					z.CandidateRejected = false;
					z.TouchBar = idx;
					z.TriggerBar = -1;
					z.CandidateEventInvalid = false;
					z.Retriggers = 0;
					Transition(z, ZState.Tested, ev, idx, 0, "touch; approach from " + (z.Approach > 0 ? "above" : "below"), "WATCH", false);
					if (closePos != 0) HandleBreak(z, ev, idx, closePos);
					return;

				case ZState.Tested:
					if (closePos != 0) HandleBreak(z, ev, idx, closePos);
					return;

				default:
					ManageActive(z, ev, idx);
					return;
			}
		}

		private void HandleBreak(TrackedZone z, BarEvidence ev, int idx, int d)
		{
			// Came from the opposite side and closed through = INITIATION.
			// Came from the same side and was pushed back away = RESPONSE.
			bool isInit = z.Approach != d;
			ZState next = isInit ? ZState.Initiation : ZState.Response;

			Candidate cand = BuildCandidate(z, ev, idx, d, isInit, false);
			z.Dir = d;
			z.AcceptCount = 1;
			z.Stalled = false;
			z.Retesting = false;
			z.StopAnchor = cand.Stop;
			z.CandidateId = cand.Id;
			z.CandidateRejected = cand.Status == "Rejected" || cand.Status == "EventOnly";
			z.TriggerBar = idx;
			z.Retriggers = 0;
			z.CandidateEventInvalid = !cand.EventValid;

			string label = (isInit ? (d > 0 ? "BUY INIT" : "SELL INIT") : "RESPONSE") + (cand.Grade.Length > 0 ? " " + cand.Grade : "");
			Transition(z, next, ev, idx, d, (isInit ? "initiation" : "response") + "; candidate " + cand.Id + " " + cand.Status, label, z.CandidateRejected);
		}

		private void ManageActive(TrackedZone z, BarEvidence ev, int idx)
		{
			int d = z.Dir;
			double tol = TouchToleranceTicks * tickSize;
			bool stopHit = d > 0 ? ev.C < z.StopAnchor : ev.C > z.StopAnchor;
			if (stopHit)
			{
				string reason = z.State == ZState.Accepted ? "FAILED_ACCEPTANCE" : (z.State == ZState.Initiation ? "FAILED_INITIATION" : "FAILED_RESPONSE");
				Transition(z, ZState.Failed, ev, idx, d, reason + "; close through stop anchor " + JeronFmt.P(z.StopAnchor), "FAILED", z.CandidateRejected);
				z.Dir = 0;
				z.AcceptCount = 0;
				return;
			}

			// v2.2 LATE_TRIGGER: the first close beyond the zone was too weak to be an event; a stronger bar
			// closing beyond it within the next RetriggerBars bars is evaluated as the trigger instead.
			if (RetriggerBars > 0 && z.CandidateEventInvalid && z.TriggerBar >= 0 && idx > z.TriggerBar
				&& (z.Qualified || !RequireQualifiedLocation)
				&& idx - z.TriggerBar <= RetriggerBars && z.Retriggers < RetriggerBars
				&& (z.State == ZState.Response || z.State == ZState.Initiation || z.State == ZState.Accepted))
			{
				double brk = BreakTicks * tickSize;
				bool closedBeyond = d > 0 ? ev.C > z.Hi + brk : ev.C < z.Lo - brk;
				if (closedBeyond)
				{
					z.Retriggers++;
					bool isInit = z.Approach != d;
					Candidate rc = BuildCandidate(z, ev, idx, d, isInit, true);
					z.CandidateId = rc.Id;
					z.CandidateRejected = rc.Status == "Rejected" || rc.Status == "EventOnly";
					z.CandidateEventInvalid = !rc.EventValid;
					if (rc.EventValid)
					{
						z.StopAnchor = rc.Stop;
						countLateTriggers++;
					}
					Note(z, ev, "LATE_TRIGGER " + (idx - z.TriggerBar).ToString(CultureInfo.InvariantCulture) + " bar(s) after the first break; candidate " + rc.Id + " " + rc.Status);
					if (rc.EventValid)
						DrawLabel(z, (isInit ? (d > 0 ? "BUY INIT" : "SELL INIT") : "RESPONSE") + " LATE" + (rc.Grade.Length > 0 ? " " + rc.Grade : ""), d, z.CandidateRejected, idx, ev);
				}
			}

			bool beyond = d > 0 ? ev.C > z.Hi : ev.C < z.Lo;
			if (z.State != ZState.Accepted)
			{
				if (beyond)
				{
					z.AcceptCount++;
					if (z.AcceptCount >= AcceptBars)
						Transition(z, ZState.Accepted, ev, idx, d, z.AcceptCount.ToString(CultureInfo.InvariantCulture) + " consecutive closes beyond boundary", "ACCEPTED", z.CandidateRejected);
				}
				else
				{
					z.AcceptCount = 0;
					if (!z.Stalled) { z.Stalled = true; Note(z, ev, "STALLED_BACK_IN_ZONE"); }
				}
				return;
			}

			// ACCEPTED: retests and re-arming
			bool touchZone = d > 0 ? ev.L <= z.Hi + tol : ev.H >= z.Lo - tol;
			if (touchZone && !z.Retesting) { z.Retesting = true; Note(z, ev, "RETEST"); }
			else if (z.Retesting && beyond && !touchZone) { z.Retesting = false; Note(z, ev, "RETEST_HELD"); }

			double dist = d > 0 ? ev.L - z.Hi : z.Lo - ev.H;
			if (dist >= RearmDistanceTicks * tickSize)
			{
				Note(z, ev, "RESOLVED_AWAY; zone re-armed from the " + (d > 0 ? "upper" : "lower") + " side");
				if (!z.IsFrozen && d == -z.OriginDir)
				{
					z.Active = false;
					z.EndBar = idx;
					Note(z, ev, "INTRADAY_ZONE_RUN_THROUGH; projection ended");
				}
				z.State = ZState.Waiting;
				z.Dir = 0;
				z.AcceptCount = 0;
				z.Retesting = false;
			}
		}

		private void Transition(TrackedZone z, ZState next, BarEvidence ev, int idx, int d, string reason, string label, bool rejected)
		{
			ZState prevState = z.State;
			z.State = next;
			z.History.Add(JeronFmt.Hms(ev.TimeCt) + " " + next.ToString());

			Dictionary<string, string> row = ZoneRow("STATE", z, ev);
			row["PrevState"] = prevState.ToString();
			row["State"] = next.ToString();
			row["Direction"] = JeronFmt.DirText(d);
			row["CandidateStatus"] = z.CandidateId.Length > 0 && next != ZState.Tested ? (rejected ? "Rejected" : "see candidate") : "";
			row["Detail"] = reason;
			FillEvidence(row, ev);
			Write(row);

			DrawLabel(z, label, d, rejected, idx, ev);
		}

		private void Note(TrackedZone z, BarEvidence ev, string text)
		{
			z.History.Add(JeronFmt.Hms(ev.TimeCt) + " " + text);
			Dictionary<string, string> row = ZoneRow("NOTE", z, ev);
			row["State"] = z.State.ToString();
			row["Direction"] = JeronFmt.DirText(z.Dir);
			row["Detail"] = text;
			Write(row);
		}

		// ==============================================================================
		//  Candidates
		// ==============================================================================
		private Candidate BuildCandidate(TrackedZone z, BarEvidence ev, int idx, int d, bool isInit, bool lateTrigger)
		{
			seq++;
			Candidate cand = new Candidate();
			cand.Seq = seq;
			cand.LocRank = z.IsFrozen ? 4 : (z.IsPower ? 3 : (z.Qualified ? 2 : 1));
			cand.Id = "JOFT-" + ev.TimeCt.ToString("yyyyMMdd", CultureInfo.InvariantCulture) + "-" + seq.ToString("00000", CultureInfo.InvariantCulture);
			cand.Zone = z;
			cand.Dir = d;
			cand.Kind = isInit ? "INITIATION" : "RESPONSE";
			cand.Family = cand.Kind;
			cand.TriggerBar = idx;
			cand.Entry = ev.C;   // evidence complete at bar close; a real fill would be at or after the next tick
			cand.SignalCt = ev.TimeCt;
			cand.SessionEndCt = SessionEndFor(ev.TimeCt);   // v2.5 outcome window end
			cand.AtrAtSignal = ev.Atr;                      // v2.6
			cand.TrigStack = d > 0 ? ev.MaxBuyStack : ev.MaxSellStack;

			// trapped side (RESPONSE): aggression without follow-through at the zone, before the trigger bar
			bool excludeTrigger = UseSetupFamilies && RequireDeltaFlipForResponse;
			double attemptExtreme = double.NaN;
			bool trapped = !isInit && HasFailedAttempt(z, idx, -d, excludeTrigger, out attemptExtreme);

			// ---- stop: where the trade idea is wrong (Part 2 ~12:46-14:47, Part 3 ~31:13; notes v3 section G) ----
			double buf = StopBufferTicks * tickSize;
			bool useBarExtreme = StopAnchorMode == JeronStopAnchorMode.TriggerBarExtreme;
			if (StopByFamily && UseSetupFamilies) useBarExtreme = isInit;   // response defends the zone; initiation bar fuels the move
			if (useBarExtreme)
				cand.Stop = d > 0 ? ev.L - buf : ev.H + buf;
			else
				cand.Stop = d > 0 ? z.Lo - buf : z.Hi + buf;
			bool stopAtSwing = false;
			if (!isInit && ResponseStopBeyondAttempt && trapped && !double.IsNaN(attemptExtreme))
			{
				// beyond the rejection swing of the failed attempt, if that is further than the zone edge
				double swingStop = d > 0 ? attemptExtreme - buf : attemptExtreme + buf;
				if (d * (cand.Stop - swingStop) > 0) { cand.Stop = swingStop; stopAtSwing = true; }
			}

			string targetRef, skipped;
			cand.Target = FindTarget(cand.Entry, d, z, cand.Stop, out targetRef, out skipped);
			cand.TargetRef = targetRef;

			// ---- EVENT gates: is this a real order-flow event at the level? ----
			List<string> eventReasons = new List<string>();
			if (ev.Source == "NONE") eventReasons.Add("NO_FOOTPRINT_DATA");
			if (d * ev.Delta < MinAbsDelta) eventReasons.Add("WEAK_DELTA");
			if (d * ev.DeltaPct < MinDeltaPct) eventReasons.Add("WEAK_DELTA_PCT");
			bool imbOk = d > 0 ? ev.BuyImb > 0 : ev.SellImb > 0;
			bool largeOk = d > 0 ? ev.LargeBuy >= LargeTradeEvidenceMin : ev.LargeSell >= LargeTradeEvidenceMin;
			if (RequireImbalanceOrLargeTrade && !imbOk && !largeOk) eventReasons.Add("NO_IMBALANCE_OR_LARGE_TRADE");
			double disp = d > 0 ? ev.C - z.Hi : z.Lo - ev.C;
			if (disp < MinDisplacementTicks * tickSize) eventReasons.Add("LOW_DISPLACEMENT");
			if (!isInit && !trapped)
				eventReasons.Add(excludeTrigger ? "NO_TRAPPED_SIDE_BEFORE_TRIGGER" : "NO_FAILED_ATTEMPT_EVIDENCE");

			// ---- flags (recorded, not rejections) ----
			List<string> flags = new List<string>();
			bool ranThrough = RanThroughOpposingImbalance(ev, idx, d);
			if (ranThrough) flags.Add("RAN_THROUGH_OPP_IMB");
			bool speedOk = !double.IsNaN(ev.SpeedRatio) && ev.SpeedRatio >= MinSpeedRatio;
			if (isInit) flags.Add(speedOk ? "TAPE_SPEED_OK" : "NO_TAPE_SPEED");
			BarEvidence back;
			if (evidence.TryGetValue(idx - Math.Max(1, CvdLookbackBars), out back))
				flags.Add(d * (ev.Cvd - back.Cvd) > 0 ? "CVD_ALIGNED" : "CVD_DIVERGENT");
			bool vwapInit = completedVwap > 0 && (d > 0 ? (ev.L <= completedVwap && ev.C > completedVwap) : (ev.H >= completedVwap && ev.C < completedVwap));
			if (vwapInit) flags.Add("THROUGH_VWAP");
			bool counter = (effectiveContext == JeronContextBias.Bullish && d < 0) || (effectiveContext == JeronContextBias.Bearish && d > 0);
			if (counter) flags.Add("COUNTER_CONTEXT");
			if (counter && CounterContextFirstTarget) flags.Add("COUNTER_FIRST_TARGET");   // v2.4
			if (effectiveContext == JeronContextBias.Balanced && isInit) flags.Add("BALANCE_INITIATION");
			if (ev.HighEffortLowReward) flags.Add("HIGH_EFFORT_LOW_REWARD");
			if (largeOk) flags.Add(d > 0 ? "LARGE_BUY" : "LARGE_SELL");
			flags.Add(z.IsFrozen ? "LOC_FROZEN" : (z.IsPower ? "LOC_POWER" : (z.Qualified ? "LOC_IMB_QUALIFIED" : "LOC_IMB_MINOR")));
			if (stopAtSwing) flags.Add("STOP_AT_REJECTION_SWING");
			if (imbOk) flags.Add(d > 0 ? "BUY_IMB" : "SELL_IMB");
			if (lateTrigger) flags.Add("LATE_TRIGGER");
			if (skipped.Length > 0) flags.Add("TARGET_BEYOND_NEAREST");

			// ---- S1.4 research flags (logging only: nothing below changes a reason, status, stop or target) ----
			string passiveKind = "", fightKind = "";
			bool passive = false, passiveRescue = false, fight = false;
			if (LogS14Flags)
			{
				if (!isInit)
				{
					passive = HasPassiveTrap(z, idx, -d, excludeTrigger, out passiveKind);
					if (passive && !trapped) flags.Add("TRAPPED_PASSIVE");
					passiveRescue = passive && !trapped && eventReasons.Count == 1
						&& (eventReasons[0] == "NO_TRAPPED_SIDE_BEFORE_TRIGGER" || eventReasons[0] == "NO_FAILED_ATTEMPT_EVIDENCE");
				}
				fight = HasFight(z, idx, out fightKind);
				if (fight) flags.Add("FIGHT");
			}

			// ---- grade (Part 3 ~30:15: response alone B+, initiation through VWAP A+) ----
			string grade;
			if (isInit)
			{
				if (vwapInit && (imbOk || largeOk) && (speedOk || !FlagInitiationWithoutSpeed)) grade = "A+";
				else if (ranThrough && (speedOk || !FlagInitiationWithoutSpeed)) grade = "B+";
				else grade = "B";
			}
			else grade = "B+";
			if (counter) grade = "C";
			cand.Grade = UseSetupFamilies ? grade : "";

			// ---- ENTRY gates: is it a tradeable entry at this price? ----
			List<string> entryReasons = new List<string>();
			if (completedVwap > 0 && ((d > 0 && ev.C < completedVwap) || (d < 0 && ev.C > completedVwap)))
			{
				if (RequireVwapAlignment) entryReasons.Add("OPPOSING_VWAP");
			}
			if (RejectAtSessionPoc && ev.SessionPoc > 0 && Math.Abs(cand.Entry - ev.SessionPoc) <= PocBufferTicks * tickSize)
				entryReasons.Add("AT_SESSION_POC");
			if (counter && RejectCounterContext) entryReasons.Add("COUNTER_CONTEXT");
			if (RequireQualifiedLocation && !z.Qualified) entryReasons.Add("UNQUALIFIED_LOCATION");
			if (NyOnlyEntries && ev.Session != JeronSession.NewYork) entryReasons.Add("OUTSIDE_NY_SESSION");
			// v2.3 plan gates
			if (z.TargetOnly) entryReasons.Add("TARGET_ONLY_ZONE");
			bool altRules = planInvalidated && z.FromPlan;
			string rule = d > 0 ? (altRules ? z.AltLongRule : z.LongRule) : (altRules ? z.AltShortRule : z.ShortRule);
			if (altRules) flags.Add("PLAN_ALT_RULES");
			string ruleReason = "";
			if (rule == "NONE") ruleReason = "PLAN_SIDE_BLOCKED";
			else if (rule == "RESPONSE" && isInit) ruleReason = "PLAN_NEEDS_RESPONSE";
			else if (rule == "INITIATION" && !isInit) ruleReason = "PLAN_NEEDS_INITIATION";
			if (ruleReason.Length > 0)
			{
				if (EnforcePlanRules) entryReasons.Add(ruleReason);
				else flags.Add(ruleReason);
			}
			if (z.FromPlan) flags.Add(z.TargetOnly ? "LOC_PLAN_TARGET" : "LOC_PLAN_DECISION");
			PlanEntryChecks(entryReasons, flags, d, cand.Entry);
			// v2.7: no active plan = no entries (still logged and followed as EventOnly)
			if (UsePreopenPlan && RequirePlanForEntries && !planActive) { entryReasons.Add("NO_PLAN"); countNoPlan++; }
			// v2.8: Level 2 snapshot (recorded and flagged; blocks entries only with 'Require L2 alignment for entries')
			L2Snap l2 = TakeL2Snap(d, ev.TimeCt);
			string l2Tag = l2.Status == "OK" ? (l2.Aligned == "Y" ? "L2_ALIGNED" : "L2_NOT_ALIGNED") : "L2_" + l2.Status;
			if (CaptureL2)
			{
				if (RequireL2Alignment && l2Tag != "L2_ALIGNED") entryReasons.Add(l2Tag);
				else flags.Add(l2Tag);
			}
			if (planActive) flags.Add("PLAN_" + JeronFmt.SafeFileToken(plan.Id.Length > 0 ? plan.Id : plan.Date.ToString("yyyyMMdd", CultureInfo.InvariantCulture)));
			double risk = d * (cand.Entry - cand.Stop);
			if (risk <= 0) entryReasons.Add("INVALID_RISK");
			if (MaxRiskTicks > 0 && risk > MaxRiskTicks * tickSize) entryReasons.Add("RISK_TOO_WIDE");
			double rr = double.NaN;
			bool noTarget = cand.Target <= 0;
			if (!noTarget && risk > 0)
			{
				rr = d * (cand.Target - cand.Entry) / risk;
				if (rr < MinRewardRisk) entryReasons.Add("POOR_REWARD_RISK");
			}

			cand.EventValid = eventReasons.Count == 0;
			cand.RR = rr;

			// status only; counters are applied when the candidate is committed (after per-bar dedupe)
			if (!cand.EventValid) cand.Status = "Rejected";
			else if (entryReasons.Count > 0) cand.Status = UseSetupFamilies ? "EventOnly" : "Rejected";
			else if (UseSetupFamilies && !isInit && RequireResponseConfirmation) { cand.Status = "AwaitConfirm"; cand.AwaitConfirm = true; }
			else if (noTarget) cand.Status = "Pending";
			else cand.Status = "Qualified";
			cand.Flags = string.Join("|", flags.ToArray());
			// v2.6: strong initiation (speed plus power / stacked imbalance / VWAP) vs an ordinary break
			cand.BreakStrength = isInit && speedOk && (largeOk || cand.TrigStack >= QualifiedStackMin || vwapInit) ? "STRONG" : "ORDINARY";

			List<string> all = new List<string>(eventReasons);
			all.AddRange(entryReasons);
			if (noTarget) all.Add("NO_TARGET_REFERENCE");

			Dictionary<string, string> row = ZoneRow("CANDIDATE", z, ev);
			row["EventId"] = cand.Id;
			row["Direction"] = JeronFmt.DirText(d);
			row["State"] = cand.Kind;
			row["CandidateStatus"] = cand.Status;
			row["Reasons"] = string.Join("|", all.ToArray());
			row["EntryRef"] = JeronFmt.P(cand.Entry);
			row["StopAnchor"] = JeronFmt.P(cand.Stop);
			row["TargetRef"] = cand.TargetRef;
			row["TargetPrice"] = noTarget ? "" : JeronFmt.P(cand.Target);
			row["RewardRisk"] = JeronFmt.N(rr, 2);
			row["Displacement"] = JeronFmt.P(disp);
			row["NearestBoundary"] = JeronFmt.P(d > 0 ? z.Hi : z.Lo);
			row["Detail"] = "approach=" + (z.Approach > 0 ? "above" : "below")
				+ "; stop=" + (stopAtSwing ? "beyond rejection swing" : (useBarExtreme ? "trigger bar extreme" : "beyond defended zone"))
				+ "; vwapSide=" + (completedVwap <= 0 ? "n/a" : (ev.C >= completedVwap ? "above" : "below"))
				+ "; largeIds=" + ev.LargeBuyId + "/" + ev.LargeSellId
				+ (cand.AwaitConfirm ? "; waiting for next bar response" : "")
				+ (lateTrigger ? "; late trigger " + (idx - z.TriggerBar).ToString(CultureInfo.InvariantCulture) + " bar(s) after the first break" : "")
				+ (skipped.Length > 0 ? "; nearer levels below min R:R skipped: " + skipped : "");
			FillCandidateCols(row, cand, ev);
			FillEvidence(row, ev);
			FillL2(row, l2);   // v2.8
			FillCandidateFeatures(row, cand, z, ev, idx, d, trapped, rule);   // v2.10 research features (logging only)
			if (LogS14Flags)   // S1.4 (logging only)
			{
				row["trapped_passive"] = isInit ? "" : YN(passive);
				row["trapped_passive_kind"] = passiveKind;
				row["passive_would_rescue"] = isInit ? "" : YN(passiveRescue);
				FillRelativeDelta(row, ev, idx, d);
				row["fight_flag"] = YN(fight);
				row["fight_kind"] = fightKind;
			}
			cand.Row = row;

			if (DedupeCandidatesPerBar) barCands.Add(cand);
			else CommitCandidate(cand);
			return cand;
		}

		// v2.2: counters, log row and outcome tracking for a candidate that survived per-bar dedupe
		private void CommitCandidate(Candidate cand)
		{
			if (cand.EventValid) countEvents++;
			if (cand.EventValid && cand.Grade == "A+" && UseSetupFamilies) countAplus++;
			if (cand.Status == "Rejected" || cand.Status == "EventOnly") countRejected++;
			else if (cand.Status == "AwaitConfirm" || cand.Status == "Pending") countPending++;
			else if (cand.Status == "Qualified") countQualified++;
			if (cand.Flags.Contains("TARGET_BEYOND_NEAREST")) countTargetSkips++;
			// v2.10 G13: count entries that passed the gates (the row was filled with the counts BEFORE this one)
			if (cand.Status == "Qualified" || cand.Status == "AwaitConfirm" || cand.Status == "Pending")
			{
				cand.CountsAsEntry = true;
				dayEntryCount++;
				cand.Zone.EntryCount++;
			}
			// v2.10 CAR01: an event at a plan decision zone starts an LVN-return watch on the leg away from the zone
			if (LogResearchRules && cand.EventValid && cand.Zone.FromPlan && !cand.Zone.TargetOnly) StartCar01(cand);
			// S1.4 counters and reversal-after-stop check (logging only; the candidate's status is unchanged)
			if (LogS14Flags && cand.Row != null)
			{
				string v;
				if (cand.Row.TryGetValue("trapped_passive", out v) && v == "Y") countPassiveTraps++;
				if (cand.Row.TryGetValue("passive_would_rescue", out v) && v == "Y") countPassiveRescues++;
				if (cand.Row.TryGetValue("fight_flag", out v) && v == "Y") countFights++;
				CheckReversalAfterStop(cand);
			}
			if (cand.Row != null)
			{
				if (cand.AlsoAt.Count > 0)
					cand.Row["Detail"] = cand.Row["Detail"] + "; same bar+direction also at: " + string.Join(", ", cand.AlsoAt.ToArray());
				cand.Row["SignalTimeCT"] = JeronFmt.T(cand.SignalCt);
				Write(cand.Row);
				cand.Row = null;
			}
			candidates.Add(cand);
			if (cand.Status == "Qualified" && !cand.IsShadow) entryQueue.Add(cand);   // S1.0
		}

		private static int StatusRank(string status)
		{
			// Qualified, AwaitConfirm and Pending all passed the event and entry gates, so they rank equally
			// and the location decides (a frozen-zone response waiting for its confirmation bar must not lose
			// to an intraday-stack initiation on the same bar).
			if (status == "Qualified" || status == "AwaitConfirm" || status == "Pending") return 3;
			if (status == "EventOnly") return 2;
			return 1;
		}

		// Higher is better: passed gates, then location quality, then reward:risk, then first created.
		private static int CompareCandidates(Candidate a, Candidate b)
		{
			int c = StatusRank(a.Status).CompareTo(StatusRank(b.Status));
			if (c != 0) return c;
			c = a.LocRank.CompareTo(b.LocRank);
			if (c != 0) return c;
			double ra = double.IsNaN(a.RR) ? double.MinValue : a.RR;
			double rb = double.IsNaN(b.RR) ? double.MinValue : b.RR;
			c = ra.CompareTo(rb);
			if (c != 0) return c;
			return b.Seq.CompareTo(a.Seq);
		}

		// One CANDIDATE row per bar and direction (overlapping zones breaking on one bar used to write many rows).
		private void FlushBarCandidates()
		{
			if (barCands.Count == 0) return;
			for (int dir = -1; dir <= 1; dir += 2)
			{
				Candidate best = null;
				foreach (Candidate c in barCands)
					if (c.Dir == dir && (best == null || CompareCandidates(c, best) > 0)) best = c;
				if (best == null) continue;
				foreach (Candidate c in barCands)
				{
					if (c.Dir != dir || c == best) continue;
					countDuplicates++;
					best.AlsoAt.Add(c.Zone.Id + "(" + c.Status + ")");
					if (c.Zone.CandidateId == c.Id)
					{
						c.Zone.CandidateId = best.Id;   // later rows for that zone point at the logged candidate
						c.Zone.CandidateRejected = true;
					}
				}
				CommitCandidate(best);
				// v2.5: the dropped candidates are still written and followed as SHADOW rows (never counted as entries)
				if (LogShadowCandidates)
				{
					foreach (Candidate c in barCands)
					{
						if (c.Dir != dir || c == best) continue;
						WriteShadow(c, best);
					}
				}
			}
			barCands.Clear();
		}

		private void WriteShadow(Candidate c, Candidate best)
		{
			c.IsShadow = true;
			c.ShadowOf = best.Id;
			countShadows++;
			if (c.Row != null)
			{
				c.Row["RecordType"] = "SHADOW";
				c.Row["ShadowOf"] = best.Id;
				c.Row["SignalTimeCT"] = JeronFmt.T(c.SignalCt);
				c.Row["Detail"] = c.Row["Detail"] + "; shadow of " + best.Id + " (dropped by per-bar dedupe; research only)";
				Write(c.Row);
				c.Row = null;
			}
			candidates.Add(c);
		}

		private void FillCandidateCols(Dictionary<string, string> row, Candidate c, BarEvidence ev)
		{
			row["SetupFamily"] = c.Family;
			row["Grade"] = c.Grade;
			row["EventValid"] = c.EventValid ? "Y" : "N";
			row["EntryStatus"] = c.Status;
			row["Flags"] = c.Flags;
			row["CVD"] = JeronFmt.N(ev.Cvd, 0);
			row["SpeedRatio"] = JeronFmt.N(ev.SpeedRatio, 2);
			row["SessionPOC"] = ev.SessionPoc > 0 ? JeronFmt.P(ev.SessionPoc) : "";
		}

		private bool RanThroughOpposingImbalance(BarEvidence ev, int idx, int d)
		{
			TrackedZone[] snapshot;
			lock (zLock) snapshot = zones.ToArray();
			foreach (TrackedZone oz in snapshot)
			{
				if (oz.IsFrozen || !oz.Active || oz.CreatedBar >= idx || oz.OriginDir != -d) continue;
				bool through = d > 0 ? (ev.L <= oz.Lo && ev.C > oz.Hi) : (ev.H >= oz.Hi && ev.C < oz.Lo);
				if (through) return true;
			}
			return false;
		}

		// RESPONSE confirmation: the bar AFTER the trigger must close in the response direction, stay beyond the
		// zone and keep delta on the response side (Part 3 ~29:14: "I'm not just buying immediately with this power trade").
		private void CheckConfirmations(BarEvidence ev)
		{
			foreach (Candidate c in candidates)
			{
				if (!c.AwaitConfirm || c.TriggerBar >= ev.Idx) continue;
				c.AwaitConfirm = false;
				int d = c.Dir;
				TrackedZone z = c.Zone;
				bool body = d * (ev.C - ev.O) > 0;
				bool beyond = d > 0 ? ev.C > z.Hi : ev.C < z.Lo;
				bool deltaOk = d * ev.Delta > 0;
				bool cnt = !c.IsShadow;   // v2.5: shadow confirmations are logged, never counted
				Dictionary<string, string> row = ZoneRow(cnt ? "CONFIRM" : "SHADOW_CONFIRM", z, ev);
				if (!cnt) row["ShadowOf"] = c.ShadowOf;
				row["EventId"] = c.Id;
				row["Direction"] = JeronFmt.DirText(d);
				row["State"] = c.Kind;
				if (cnt) countPending--;
				if (body && beyond && deltaOk)
				{
					c.Entry = ev.C;
					c.TriggerBar = ev.Idx;   // outcomes measured from the bar after the confirmation
					string targetRef, skipped;
					c.Target = FindTarget(c.Entry, d, z, c.Stop, out targetRef, out skipped);
					c.TargetRef = targetRef;
					if (skipped.Length > 0 && !c.Flags.Contains("TARGET_BEYOND_NEAREST")) { c.Flags += (c.Flags.Length > 0 ? "|" : "") + "TARGET_BEYOND_NEAREST"; if (cnt) countTargetSkips++; }
					double risk = d * (c.Entry - c.Stop);
					double rr = c.Target > 0 && risk > 0 ? d * (c.Target - c.Entry) / risk : double.NaN;
					List<string> reasons = new List<string>();
					if (risk <= 0) reasons.Add("INVALID_RISK");
					if (MaxRiskTicks > 0 && risk > MaxRiskTicks * tickSize) reasons.Add("RISK_TOO_WIDE");
					if (!double.IsNaN(rr) && rr < MinRewardRisk) reasons.Add("POOR_REWARD_RISK");
					PlanEntryChecks(reasons, null, d, c.Entry);   // v2.3: lava band and ES gate at the confirmation bar
					if (reasons.Count > 0) { c.Status = "EventOnly"; if (cnt) countRejected++; }
					else if (c.Target <= 0) { c.Status = "Pending"; if (cnt) countPending++; reasons.Add("NO_TARGET_REFERENCE"); }
					else { c.Status = "Qualified"; if (cnt) { countQualified++; entryQueue.Add(c); } }   // S1.0: confirmed response
					if (cnt) countConfirmed++;
					row["Reasons"] = string.Join("|", reasons.ToArray());
					row["EntryRef"] = JeronFmt.P(c.Entry);
					row["StopAnchor"] = JeronFmt.P(c.Stop);
					row["TargetRef"] = c.TargetRef;
					row["TargetPrice"] = c.Target > 0 ? JeronFmt.P(c.Target) : "";
					row["RewardRisk"] = JeronFmt.N(rr, 2);
					row["Detail"] = "RESPONSE_CONFIRMED; entry moved to confirmation close"
						+ (skipped.Length > 0 ? "; nearer levels below min R:R skipped: " + skipped : "");
				}
				else
				{
					c.Status = "EventOnly";
					if (cnt) countRejected++;
					row["Reasons"] = "RESPONSE_NOT_CONFIRMED" + (!body ? "|BODY_AGAINST" : "") + (!beyond ? "|BACK_IN_ZONE" : "") + (!deltaOk ? "|DELTA_AGAINST" : "");
					row["Detail"] = "response not confirmed on the next bar; outcome still tracked from the trigger";
				}
				row["CandidateStatus"] = c.Status;
				FillCandidateCols(row, c, ev);
				FillEvidence(row, ev);
				Write(row);
				if (z.CandidateId == c.Id) z.CandidateRejected = c.Status != "Qualified" && c.Status != "Pending";
			}
		}

		private bool HasFailedAttempt(TrackedZone z, int idx, int attemptDir, bool excludeTrigger, out double extreme)
		{
			extreme = double.NaN;
			bool found = false;
			double tol = TouchToleranceTicks * tickSize;
			int first = excludeTrigger ? idx - 1 : idx;
			// v2.2: search back to the first touch of this visit (capped), not only a fixed few bars
			int last = idx - ResponseLookbackBars;
			if (ResponseLookbackToFirstTouch && z.TouchBar >= 0 && z.TouchBar < last)
				last = Math.Max(z.TouchBar, idx - Math.Max(ResponseLookbackBars, MaxResponseLookbackBars));
			for (int k = first; k >= last; k--)
			{
				BarEvidence b;
				if (!evidence.TryGetValue(k, out b)) continue;
				bool touched = b.H >= z.Lo - tol && b.L <= z.Hi + tol;
				if (!touched) continue;
				bool aggression = attemptDir * b.Delta > 0
					&& ((attemptDir > 0 ? b.BuyImb > 0 : b.SellImb > 0)
						|| (attemptDir > 0 ? b.LargeBuy >= LargeTradeEvidenceMin : b.LargeSell >= LargeTradeEvidenceMin)
						|| attemptDir * b.Delta >= MinAbsDelta);
				bool failedToClear = attemptDir > 0 ? b.C <= z.Hi + BreakTicks * tickSize : b.C >= z.Lo - BreakTicks * tickSize;
				if (aggression && failedToClear)
				{
					found = true;
					double ex = attemptDir > 0 ? b.H : b.L;   // how far the trapped side got
					if (double.IsNaN(extreme) || attemptDir * (ex - extreme) > 0) extreme = ex;
				}
			}
			// include the trigger bar's own extreme (the swing that defines the rejection)
			BarEvidence tb;
			if (found && evidence.TryGetValue(idx, out tb))
			{
				double ex = attemptDir > 0 ? tb.H : tb.L;
				if (attemptDir * (ex - extreme) > 0) extreme = ex;
			}
			return found;
		}

		// ==============================================================================
		//  S1.4 research flags (logging only)
		// ==============================================================================
		// 2a. Passive trapped side (Part 3 ~35:22). Same bars as HasFailedAttempt (first touch of this visit, capped),
		// but the trapped side need not be aggressive: effort without reward, no aggression and a close against them,
		// or a wick into the zone with no imbalance or large trade from them. The bar must still fail to clear the zone.
		private bool HasPassiveTrap(TrackedZone z, int idx, int attemptDir, bool excludeTrigger, out string kind)
		{
			kind = "";
			List<string> kinds = new List<string>();
			double tol = TouchToleranceTicks * tickSize;
			int first = excludeTrigger ? idx - 1 : idx;
			int last = idx - ResponseLookbackBars;
			if (ResponseLookbackToFirstTouch && z.TouchBar >= 0 && z.TouchBar < last)
				last = Math.Max(z.TouchBar, idx - Math.Max(ResponseLookbackBars, MaxResponseLookbackBars));
			for (int k = first; k >= last; k--)
			{
				BarEvidence b;
				if (!evidence.TryGetValue(k, out b)) continue;
				bool touched = b.H >= z.Lo - tol && b.L <= z.Hi + tol;
				if (!touched) continue;
				bool failedToClear = attemptDir > 0 ? b.C <= z.Hi + BreakTicks * tickSize : b.C >= z.Lo - BreakTicks * tickSize;
				if (!failedToClear) continue;
				bool sideImb = attemptDir > 0 ? b.BuyImb > 0 : b.SellImb > 0;
				bool sideLarge = attemptDir > 0 ? b.LargeBuy >= LargeTradeEvidenceMin : b.LargeSell >= LargeTradeEvidenceMin;
				double range = b.H - b.L;
				if (b.HighEffortLowReward && !kinds.Contains("HIGH_EFFORT_LOW_REWARD")) kinds.Add("HIGH_EFFORT_LOW_REWARD");
				bool weak = attemptDir * b.DeltaPct < PassiveMaxDeltaPct;
				bool closedAgainst = attemptDir * (b.C - b.O) < 0;
				if (weak && closedAgainst && !sideImb && !sideLarge && !kinds.Contains("NO_AGGRESSION")) kinds.Add("NO_AGGRESSION");
				if (range > 0 && !sideImb && !sideLarge)
				{
					double wick = attemptDir > 0 ? b.H - Math.Max(b.O, b.C) : Math.Min(b.O, b.C) - b.L;
					if (100.0 * wick / range >= PassiveWickPct && !kinds.Contains("WICK_NO_FOLLOW")) kinds.Add("WICK_NO_FOLLOW");
				}
			}
			kind = string.Join("+", kinds.ToArray());
			return kinds.Count > 0;
		}

		// 2d. Fight at the level (Part 3 ~10:52): both sides put in effort at the zone, or a two-sided doji there.
		private bool HasFight(TrackedZone z, int idx, out string kind)
		{
			kind = "";
			double tol = TouchToleranceTicks * tickSize;
			bool buyEffort = false, sellEffort = false, doji = false;
			for (int k = idx; k > idx - Math.Max(1, FightLookbackBars); k--)
			{
				BarEvidence b;
				if (!evidence.TryGetValue(k, out b)) continue;
				if (!(b.H >= z.Lo - tol && b.L <= z.Hi + tol)) continue;
				if (b.Delta > 0 && (b.BuyImb > 0 || b.LargeBuy >= LargeTradeEvidenceMin)) buyEffort = true;
				if (b.Delta < 0 && (b.SellImb > 0 || b.LargeSell >= LargeTradeEvidenceMin)) sellEffort = true;
				double range = b.H - b.L;
				if (range > 0 && 100.0 * Math.Abs(b.C - b.O) / range <= DojiBodyPct && b.BuyImb > 0 && b.SellImb > 0) doji = true;
			}
			List<string> kinds = new List<string>();
			if (buyEffort && sellEffort) kinds.Add("BOTH_SIDES_EFFORT");
			if (doji) kinds.Add("DOJI_TWO_SIDED");
			kind = string.Join("+", kinds.ToArray());
			return kinds.Count > 0;
		}

		// 2b. Relative delta. Baseline = earlier bars of the same session segment today (Asia / London / NY).
		private static int SegIndex(JeronSession s)
		{
			if (s == JeronSession.NewYork) return 2;
			if (s == JeronSession.London) return 1;
			return 0;
		}

		private void AddDeltaBaseline(BarEvidence ev)
		{
			if (ev == null || ev.Source == "NONE" || ev.Vol <= 0) return;
			int s = SegIndex(ev.Session);
			segAbsDpSum[s] += Math.Abs(ev.DeltaPct);
			segDpBars[s]++;
		}

		private void FillRelativeDelta(Dictionary<string, string> row, BarEvidence ev, int idx, int d)
		{
			int s = SegIndex(ev.Session);
			double avg = segDpBars[s] > 0 ? segAbsDpSum[s] / segDpBars[s] : double.NaN;
			double cur = d * ev.DeltaPct;
			row["delta_pct_session_avg"] = JeronFmt.N(avg, 2);
			row["delta_pct_vs_session"] = !double.IsNaN(avg) && avg > 0 ? JeronFmt.N(cur / avg, 2) : "";
			int n = 0, le = 0;
			for (int k = idx; k > idx - Math.Max(2, RelativeDeltaBars); k--)
			{
				BarEvidence b;
				if (!evidence.TryGetValue(k, out b) || b.Source == "NONE") continue;
				n++;
				if (d * b.DeltaPct <= cur) le++;
			}
			row["delta_rank_20"] = n >= 2 ? JeronFmt.N((double)le / n, 2) : "";
		}

		// 2c. Reversal after a stop-out (Part 3 ~31:08). One stop event per stopped candidate; LIVE_STOP and OUTCOME_STOP
		// for the same candidate are merged.
		private void AddStopEvent(Candidate c, int bar, string source)
		{
			if (c == null || c.Zone == null || ReversalAfterStopBars <= 0) return;
			foreach (StopEvt e in stopEvts)
			{
				if (e.SrcId != c.Id) continue;
				if (!e.Source.Contains(source)) e.Source += "+" + source;
				return;
			}
			StopEvt n = new StopEvt();
			n.SrcId = c.Id;
			n.Source = source;
			n.Dir = c.Dir;
			n.Bar = bar;
			n.Lo = c.Zone.Lo;
			n.Hi = c.Zone.Hi;
			stopEvts.Add(n);
		}

		private void CheckReversalAfterStop(Candidate cand)
		{
			if (ReversalAfterStopBars <= 0 || cand.IsShadow || !cand.EventValid || stopEvts.Count == 0) return;
			double tol = TouchToleranceTicks * tickSize;
			int bar = cand.TriggerBar;
			foreach (StopEvt e in stopEvts)
			{
				if (e.Used || cand.Dir != -e.Dir || bar < e.Bar || bar - e.Bar > ReversalAfterStopBars) continue;   // same bar allowed: stop and reverse on the initiation candle
				if (cand.Zone.Hi < e.Lo - tol || cand.Zone.Lo > e.Hi + tol) continue;   // zones must overlap
				e.Used = true;
				countAfterStopRev++;
				int bars = bar - e.Bar;
				cand.Flags += (cand.Flags.Length > 0 ? "|" : "") + "AFTER_STOP_REVERSAL";
				if (cand.Row != null)
				{
					cand.Row["Flags"] = cand.Flags;
					cand.Row["after_stop_src"] = e.Source + ":" + e.SrcId;
					cand.Row["after_stop_bars"] = bars.ToString(CultureInfo.InvariantCulture);
				}
				if (!LogReversalCandidates) return;
				ReversalCand r = new ReversalCand();
				reversalSeq++;
				countReversals++;
				r.Id = cand.Id + "-RAS" + reversalSeq.ToString("000", CultureInfo.InvariantCulture);
				r.Model = "AFTER_STOP";
				r.Src = cand;
				r.Dir = cand.Dir;
				r.StartBar = bar;
				r.Entry = cand.Entry;
				r.Stop = cand.Stop;
				string tref = cand.TargetRef;
				if (cand.Target > 0) r.Target = cand.Target;
				else { string skipped; r.Target = FindTarget(r.Entry, r.Dir, cand.Zone, r.Stop, out tref, out skipped); }
				r.TargetRef = tref;
				reversals.Add(r);
				BarEvidence ev;
				if (!evidence.TryGetValue(bar, out ev)) ev = lastEv;
				Dictionary<string, string> row = ZoneRow("REVERSAL_CANDIDATE", cand.Zone, ev);
				row["EventId"] = r.Id;
				row["Direction"] = JeronFmt.DirText(r.Dir);
				row["State"] = "REVERSAL";
				row["CandidateStatus"] = cand.Status;
				row["EntryRef"] = JeronFmt.P(r.Entry);
				row["StopAnchor"] = JeronFmt.P(r.Stop);
				row["TargetRef"] = r.TargetRef;
				row["TargetPrice"] = r.Target > 0 ? JeronFmt.P(r.Target) : "";
				double risk = r.Dir * (r.Entry - r.Stop);
				row["RewardRisk"] = r.Target > 0 && risk > 0 ? JeronFmt.N(r.Dir * (r.Target - r.Entry) / risk, 2) : "";
				row["SignalTimeCT"] = JeronFmt.T(cand.SignalCt);
				row["RetestModel"] = r.Model;
				row["SetupFamily"] = cand.Family;
				row["Grade"] = cand.Grade;
				row["Flags"] = cand.Flags;
				row["after_stop_src"] = e.Source + ":" + e.SrcId;
				row["after_stop_bars"] = bars.ToString(CultureInfo.InvariantCulture);
				row["Detail"] = "opposite " + cand.Family + " " + bars.ToString(CultureInfo.InvariantCulture) + " bar(s) after the stop-out of " + e.SrcId
					+ " (" + e.Source + "); candidate " + cand.Id + " is " + cand.Status + "; research only, not an entry";
				FillEvidence(row, ev);
				Write(row);
				return;
			}
		}

		// v2.2: nearest mapped level that meets Min reward:risk. Nearer levels that fail it are skipped and
		// reported; if no level meets it, the nearest is returned so POOR_REWARD_RISK still fires.
		private double FindTarget(double entry, int d, TrackedZone exclude, double stop, out string refLabel, out string skipped)
		{
			refLabel = "";
			skipped = "";
			List<double> prices = new List<double>();
			List<string> labels = new List<string>();
			TrackedZone[] snapshot;
			lock (zLock) snapshot = zones.ToArray();
			foreach (TrackedZone z in snapshot)
			{
				if (z == exclude || !z.Active) continue;
				if (z.IsFrozen && z.StartBar < 0) continue;
				if (TargetsQualifiedOnly && !z.Qualified) continue;
				double edge = d > 0 ? z.Lo : z.Hi;
				if (d * (edge - entry) > tickSize) { prices.Add(edge); labels.Add(z.Id + (d > 0 ? ".lo" : ".hi")); }
			}
			if (completedVwap > 0)
			{
				double vw = Instrument.MasterInstrument.RoundToTickSize(completedVwap);
				if (d * (vw - entry) > tickSize) { prices.Add(vw); labels.Add("SESSION_VWAP"); }
			}
			double ext = d > 0 ? sessHigh : sessLow;
			if (ext > double.MinValue && ext < double.MaxValue && d * (ext - entry) > tickSize)
			{
				prices.Add(ext);
				labels.Add(d > 0 ? "SESSION_HIGH" : "SESSION_LOW");
			}
			if (prices.Count == 0) return 0;

			// order by distance from entry (nearest first)
			int[] order = new int[prices.Count];
			double[] dists = new double[prices.Count];
			for (int i = 0; i < order.Length; i++) { order[i] = i; dists[i] = d * (prices[i] - entry); }
			Array.Sort(dists, order);

			double risk = d * (entry - stop);
			int pick = order[0];
			bool counterSide = (effectiveContext == JeronContextBias.Bullish && d < 0) || (effectiveContext == JeronContextBias.Bearish && d > 0);
			if (TargetMinRRSearch && risk > 0 && !(CounterContextFirstTarget && counterSide))   // v2.4
			{
				int found = -1;
				List<string> passed = new List<string>();
				for (int k = 0; k < order.Length; k++)
				{
					int i = order[k];
					if (d * (prices[i] - entry) / risk >= MinRewardRisk) { found = i; break; }
					passed.Add(labels[i] + "@" + JeronFmt.P(prices[i]));
				}
				if (found >= 0)
				{
					pick = found;
					skipped = string.Join(" ", passed.ToArray());
				}
			}
			refLabel = labels[pick];
			return prices[pick];
		}

		private void UpdateOutcomes(BarEvidence ev)
		{
			foreach (Candidate c in candidates)
			{
				if (c.Resolved || c.AwaitConfirm || c.TriggerBar >= ev.Idx) continue;
				c.BarsSeen++;
				if (!c.IsShadow) CheckExitWarnings(c, ev);
				double fav = c.Dir > 0 ? ev.H - c.Entry : c.Entry - ev.L;
				double adv = c.Dir > 0 ? c.Entry - ev.L : ev.H - c.Entry;
				if (fav / tickSize > c.MfeTicks) c.MfeTicks = fav / tickSize;
				if (adv / tickSize > c.MaeTicks) c.MaeTicks = adv / tickSize;
				bool hitTarget = c.Target > 0 && (c.Dir > 0 ? ev.H >= c.Target : ev.L <= c.Target);
				bool hitStop = c.Dir > 0 ? ev.L <= c.Stop : ev.H >= c.Stop;
				string outcome = "";
				if (hitTarget && hitStop) outcome = "AMBIGUOUS_SAME_BAR";
				else if (hitStop) outcome = "STOP_FIRST";
				else if (hitTarget) outcome = "TARGET_FIRST";
				// v2.5: the 15-bar result is kept as a snapshot; the outcome itself runs to the NY session end
				if (c.Outcome15.Length == 0)
				{
					if (outcome.Length > 0) { c.Outcome15 = outcome; c.Pnl15 = PnLFor(c.Dir, c.Entry, c.Stop, c.Target, outcome, ev.C); }
					else if (c.BarsSeen >= OutcomeBars) { c.Outcome15 = "TIME_EXPIRED"; c.Pnl15 = c.Dir * (ev.C - c.Entry) / tickSize; }
				}
				if (outcome.Length == 0)
				{
					if (OutcomeToSessionEnd) { if (ev.TimeCt >= c.SessionEndCt) outcome = "SESSION_END"; }
					else if (c.BarsSeen >= OutcomeBars) outcome = "TIME_EXPIRED";
				}
				if (outcome.Length == 0) continue;
				ResolveCandidate(c, ev, outcome);
			}
			StepExitModels(ev);   // v2.10
		}

		// v2.5: P/L in ticks. A same-bar stop+target touch counts as the stop (the backtest fill model's rule).
		private double PnLFor(int d, double entry, double stop, double target, string outcome, double close)
		{
			if (outcome == "TARGET_FIRST") return d * (target - entry) / tickSize;
			if (outcome == "STOP_FIRST" || outcome == "AMBIGUOUS_SAME_BAR") return d * (stop - entry) / tickSize;
			return d * (close - entry) / tickSize;
		}

		private double ExitFor(string outcome, double stop, double target, double close)
		{
			if (outcome == "TARGET_FIRST") return target;
			if (outcome == "STOP_FIRST" || outcome == "AMBIGUOUS_SAME_BAR") return stop;
			return close;
		}

		private void ResolveCandidate(Candidate c, BarEvidence ev, string outcome)
		{
			c.Resolved = true;
			c.Outcome = outcome;
			c.PnL = PnLFor(c.Dir, c.Entry, c.Stop, c.Target, outcome, ev.C);
			c.ExitPrice = ExitFor(outcome, c.Stop, c.Target, ev.C);
			if (c.Outcome15.Length == 0) { c.Outcome15 = outcome; c.Pnl15 = c.PnL; }
			if (outcome == "SESSION_END") countSessionEnd++;
			if (!c.IsShadow && c.Status == "Qualified" && !double.IsNaN(c.PnL)) sessionPnlTicks += c.PnL;   // v2.10 G13
			// S1.4: a Qualified candidate stopped out by the tracker's own outcome is a stop event (backtest sees it without orders)
			if (LogS14Flags && !c.IsShadow && c.Status == "Qualified" && (outcome == "STOP_FIRST" || outcome == "AMBIGUOUS_SAME_BAR"))
				AddStopEvent(c, ev.Idx, "OUTCOME_STOP");
			Dictionary<string, string> row = ZoneRow(c.IsShadow ? "SHADOW_OUTCOME" : "OUTCOME", c.Zone, ev);
			row["EventId"] = c.Id;
			row["Direction"] = JeronFmt.DirText(c.Dir);
			row["State"] = c.Kind;
			row["CandidateStatus"] = c.Status;
			row["EntryRef"] = JeronFmt.P(c.Entry);
			row["StopAnchor"] = JeronFmt.P(c.Stop);
			row["TargetRef"] = c.TargetRef;
			row["TargetPrice"] = c.Target > 0 ? JeronFmt.P(c.Target) : "";
			row["OutcomeType"] = outcome;
			row["MFETicks"] = JeronFmt.N(c.MfeTicks, 1);
			row["MAETicks"] = JeronFmt.N(c.MaeTicks, 1);
			row["BarsToResolve"] = c.BarsSeen.ToString(CultureInfo.InvariantCulture);
			row["PnLTicks"] = JeronFmt.N(c.PnL, 2);
			row["ExitPrice"] = JeronFmt.P(c.ExitPrice);
			row["Outcome15"] = c.Outcome15;
			row["PnL15Ticks"] = JeronFmt.N(c.Pnl15, 2);
			row["ShadowOf"] = c.ShadowOf;
			row["SignalTimeCT"] = JeronFmt.T(c.SignalCt);
			row["Detail"] = "intrabar high/low touch; evaluated from the bar after the trigger"
				+ (outcome == "SESSION_END" ? "; still open at the NY session end, P/L at that close" : "")
				+ (outcome == "DATA_END" ? "; data stopped before the outcome, P/L at the last close" : "")
				+ (outcome == "AMBIGUOUS_SAME_BAR" ? "; stop and target in the same bar, P/L counted as the stop" : "")
				+ (c.WarnFirst || c.WarnDouble ? "; exit warning issued before resolution" : "");
			FillCandidateCols(row, c, ev);
			Write(row);
		}

		private DateTime SessionEndFor(DateTime ct)
		{
			return clock.TradingDate(ct).AddMinutes(clock.NyEndMin);
		}

		private bool RetestsDone(Candidate c)
		{
			if (c.Retests == null) return !(LogRetestPaths || LogRetestV2) || c.IsShadow || !c.EventValid;
			foreach (RetestPath p in c.Retests) if (!p.Written) return false;
			return true;
		}

		// ==============================================================================
		//  v2.5 Retest research paths (logging only; never changes an entry)
		//  Definition (written down so it can be tuned, not a Jeron number):
		//   - Window: the RetestWindowBars bars after the immediate entry bar.
		//   - Retest: a bar trades back to the zone's near edge (within Touch tolerance).
		//   - Confirm: a bar (the touch bar or later) closes back outside the near edge in the trade's direction
		//     with a body in that direction. Entry at that close; stop beyond the lowest low / highest high of the
		//     retest plus the stop buffer; target = the immediate entry's target.
		//   - Fail: a close beyond the zone's FAR edge by FailTicks (RETEST_FAILED).
		//   - No retest: RAN_TO_TARGET (target reached first), RAN_AWAY (no touch, but price went 1R+ in favour),
		//     NO_RETEST_WINDOW (no touch, no run), RETEST_NO_CONFIRM (touched, never closed back), SESSION_END.
		// ==============================================================================
		private void UpdateRetests(BarEvidence ev)
		{
			UpdateReversals(ev);   // v2.6
			if (!LogRetestPaths && !LogRetestV2) return;
			foreach (Candidate c in candidates)
			{
				if (c.IsShadow || !c.EventValid || c.AwaitConfirm) continue;
				if (c.Retests == null)
				{
					if (c.TriggerBar >= ev.Idx) continue;
					c.Retests = new List<RetestPath>();
					if (LogRetestPaths)
					{
						foreach (int ft in retestFailTicks)
						{
							RetestPath p = new RetestPath();
							p.FailTicks = ft;
							p.StartBar = c.TriggerBar;
							c.Retests.Add(p);
						}
					}
					if (LogRetestV2)
					{
						RetestPath v2 = new RetestPath();
						v2.Model = "v2";
						v2.FailTicks = RetestV2FailTicks;
						v2.StartBar = c.TriggerBar;
						v2.InMiddle = ZoneInBalanceMiddle(c.Zone);
						if (v2.InMiddle == "Y") { v2.Phase = 3; v2.Reason = "MIDDLE_OF_BALANCE"; }
						c.Retests.Add(v2);
					}
				}
				foreach (RetestPath p in c.Retests)
				{
					if (p.Phase < 3) StepRetest(c, p, ev);
					if (p.Phase == 3 && !p.Written && c.Resolved) WriteRetestRow(c, p, ev);
				}
			}
		}

		private void StepRetest(Candidate c, RetestPath p, BarEvidence ev)
		{
			int d = c.Dir;
			TrackedZone z = c.Zone;
			if (p.Phase == 2)
			{
				if (ev.Idx <= p.EntryBar) return;
				p.BarsInTrade++;
				double fav = d > 0 ? ev.H - p.Entry : p.Entry - ev.L;
				double adv = d > 0 ? p.Entry - ev.L : ev.H - p.Entry;
				if (fav / tickSize > p.Mfe) p.Mfe = fav / tickSize;
				if (adv / tickSize > p.Mae) p.Mae = adv / tickSize;
				bool hitTarget = c.Target > 0 && (d > 0 ? ev.H >= c.Target : ev.L <= c.Target);
				bool hitStop = d > 0 ? ev.L <= p.Stop : ev.H >= p.Stop;
				string outcome = "";
				if (hitTarget && hitStop) outcome = "AMBIGUOUS_SAME_BAR";
				else if (hitStop) outcome = "STOP_FIRST";
				else if (hitTarget) outcome = "TARGET_FIRST";
				else if (OutcomeToSessionEnd ? ev.TimeCt >= c.SessionEndCt : p.BarsInTrade >= OutcomeBars) outcome = OutcomeToSessionEnd ? "SESSION_END" : "TIME_EXPIRED";
				if (outcome.Length == 0) return;
				p.Outcome = outcome;
				p.PnL = PnLFor(d, p.Entry, p.Stop, c.Target, outcome, ev.C);
				p.Phase = 3;
				return;
			}
			if (p.Model == "v2") { StepRetestV2(c, p, ev); return; }   // v2.6 order-flow retest

			if (ev.Idx <= p.StartBar) return;
			p.Bars++;
			double tol = TouchToleranceTicks * tickSize;
			double near = d > 0 ? z.Hi : z.Lo;
			double far = d > 0 ? z.Lo : z.Hi;
			bool touch = d > 0 ? ev.L <= near + tol : ev.H >= near - tol;
			bool failed = d > 0 ? ev.C < far - p.FailTicks * tickSize : ev.C > far + p.FailTicks * tickSize;
			if (touch)
			{
				if (p.TouchBar < 0) { p.TouchBar = ev.Idx; p.BarsToTouch = p.Bars; p.Phase = 1; }
				double ex = d > 0 ? ev.L : ev.H;
				if (double.IsNaN(p.Extreme) || d * (p.Extreme - ex) > 0) p.Extreme = ex;
				p.DepthTicks = d * (near - p.Extreme) / tickSize;
				if (-d * ev.Delta > 0 && !failed) p.Trapped = true;
			}
			if (failed) { p.Phase = 3; p.Reason = "RETEST_FAILED"; return; }
			if (p.Phase == 1)
			{
				bool closedBack = d > 0 ? (ev.C > near && ev.C > ev.O) : (ev.C < near && ev.C < ev.O);
				if (closedBack)
				{
					p.Entry = ev.C;
					p.Stop = d > 0 ? p.Extreme - StopBufferTicks * tickSize : p.Extreme + StopBufferTicks * tickSize;
					p.EntryBar = ev.Idx;
					if (c.Target > 0 && d * (c.Target - p.Entry) <= 0) { p.Phase = 3; p.Reason = "NO_ROOM_TO_TARGET"; return; }
					p.Entered = true;
					p.Reason = "RETEST_ENTERED";
					p.Phase = 2;
					p.EntryL2 = TakeL2Snap(d, ev.TimeCt);   // v2.8
					countRetestEntered++;
					return;
				}
			}
			if (p.Phase == 0 && c.Target > 0 && (d > 0 ? ev.H >= c.Target : ev.L <= c.Target)) { p.Phase = 3; p.Reason = "RAN_TO_TARGET"; return; }
			if (ev.TimeCt >= c.SessionEndCt) { p.Reason = p.Phase == 1 ? "RETEST_NO_CONFIRM" : "SESSION_END_NO_RETEST"; p.Phase = 3; return; }
			if (p.Bars >= RetestWindowBars)
			{
				double risk = d * (c.Entry - c.Stop);
				bool ranAway = risk > 0 && c.MfeTicks * tickSize >= risk;
				p.Reason = p.Phase == 1 ? "RETEST_NO_CONFIRM" : (ranAway ? "RAN_AWAY" : "NO_RETEST_WINDOW");
				p.Phase = 3;
			}
		}

		// ==============================================================================
		//  v2.6 Order-flow retest (retest v2), logging only. Placeholder numbers, not Jeron's.
		//   Phase 0: waiting for the DEPARTURE (travel >= RetestV2MinTravelAtr x ATR beyond the near edge, and at
		//            least RetestV2MinBars bars after the entry bar), then for the FIRST return to the near edge.
		//   Phase 1: the retest. Each bar is read for order flow until a bar closes back outside the near edge in
		//            the trade's direction (body in that direction). Entry needs BOTH
		//              (a) opposite side shows up and fails: absorption (opposing aggression, bar still closes with
		//                  or flat to the trade) or trapped aggression (opposing aggression without a close through), and
		//              (b) a fresh same-direction imbalance or a delta flip back to the trade's side.
		//            Not confirmed on that close = FIRST_RETEST_NO_OF_CONFIRM (later returns are ignored).
		//   Fail: a full-bodied close beyond the far edge by RetestV2FailTicks -> RETEST_FAILED + REVERSAL_CANDIDATE.
		// ==============================================================================
		private string ZoneInBalanceMiddle(TrackedZone z)
		{
			if (plan == null || double.IsNaN(plan.BalanceLo) || double.IsNaN(plan.BalanceHi) || plan.BalanceHi <= plan.BalanceLo) return "";
			double third = (plan.BalanceHi - plan.BalanceLo) / 3.0;
			double mid = (z.Lo + z.Hi) / 2.0;
			return mid > plan.BalanceLo + third && mid < plan.BalanceHi - third ? "Y" : "N";
		}

		private void StepRetestV2(Candidate c, RetestPath p, BarEvidence ev)
		{
			if (ev.Idx <= p.StartBar) return;
			p.Bars++;
			int d = c.Dir;
			TrackedZone z = c.Zone;
			double tol = TouchToleranceTicks * tickSize;
			double near = d > 0 ? z.Hi : z.Lo;
			double far = d > 0 ? z.Lo : z.Hi;
			double atr = double.IsNaN(c.AtrAtSignal) || c.AtrAtSignal <= 0 ? ev.Atr : c.AtrAtSignal;
			bool touch = d > 0 ? ev.L <= near + tol : ev.H >= near - tol;
			bool fullBodyFail = (d > 0 ? ev.C < far - p.FailTicks * tickSize : ev.C > far + p.FailTicks * tickSize) && d * (ev.C - ev.O) < 0;
			bool targetHit = c.Target > 0 && (d > 0 ? ev.H >= c.Target : ev.L <= c.Target);
			bool sessionOver = ev.TimeCt >= c.SessionEndCt;
			bool windowOver = p.Bars >= RetestV2WindowBars;

			if (p.Phase == 0)
			{
				if (!p.Departed)
				{
					if (touch) p.TouchesBeforeDeparture++;
					double travel = d > 0 ? ev.H - near : near - ev.L;
					if (travel > p.MaxTravel) p.MaxTravel = travel;
					if (fullBodyFail) { p.Phase = 3; p.Reason = "FAILED_BEFORE_DEPARTURE"; LogReversal(c, ev, "failed break: full-bodied close through the far edge before price left"); return; }
					if (targetHit) { p.Phase = 3; p.Reason = "RAN_TO_TARGET"; return; }
					if (atr > 0 && p.MaxTravel >= RetestV2MinTravelAtr * atr && p.Bars >= RetestV2MinBars) { p.Departed = true; return; }   // touches count from the next bar
					if (sessionOver || windowOver) { p.Phase = 3; p.Reason = "NEVER_LEFT"; }
					return;
				}
				double tr2 = d > 0 ? ev.H - near : near - ev.L;
				if (tr2 > p.MaxTravel && !touch) p.MaxTravel = tr2;
				if (!touch)
				{
					if (targetHit) { p.Phase = 3; p.Reason = "RAN_TO_TARGET"; return; }
					if (sessionOver) { p.Phase = 3; p.Reason = "SESSION_END_NO_RETEST"; return; }
					if (windowOver) { p.Phase = 3; p.Reason = "NO_RETEST_AFTER_DEPARTURE"; }
					return;
				}
				p.Phase = 1;
				p.TouchBar = ev.Idx;
				p.BarsToTouch = p.Bars;
				p.TravelAtr = atr > 0 ? p.MaxTravel / atr : double.NaN;
			}

			// Phase 1: read the retest bar by bar
			double ex = d > 0 ? ev.L : ev.H;
			if (double.IsNaN(p.Extreme) || d * (p.Extreme - ex) > 0) p.Extreme = ex;
			p.DepthTicks = d * (near - p.Extreme) / tickSize;
			double opp = -d * ev.Delta;
			bool oppImb = d > 0 ? ev.SellImb > 0 : ev.BuyImb > 0;
			bool oppLarge = d > 0 ? ev.LargeSell >= LargeTradeEvidenceMin : ev.LargeBuy >= LargeTradeEvidenceMin;
			bool oppAggression = opp > 0 && (oppImb || oppLarge || opp >= RetestV2OppDeltaMin);
			bool closedThrough = d > 0 ? ev.C < far : ev.C > far;
			if (p.SawOppDelta && d * ev.Delta > 0) p.DeltaFlip = true;
			if (opp > 0) { p.SawOppDelta = true; p.OppDelta += opp; }
			if (oppAggression && !closedThrough)
			{
				p.Trapped = true;
				if (d * (ev.C - ev.O) >= 0 || ev.HighEffortLowReward) p.Absorption = true;   // effort against, no reward
			}
			if (d > 0 ? ev.BuyImb > 0 : ev.SellImb > 0) p.FreshImb = true;

			if (fullBodyFail) { p.Phase = 3; p.Reason = "RETEST_FAILED"; LogReversal(c, ev, "failed retest: full-bodied close through the far edge"); return; }
			bool closedBack = d > 0 ? (ev.C > near && ev.C > ev.O) : (ev.C < near && ev.C < ev.O);
			if (closedBack)
			{
				p.ReactionBars = ev.Idx - p.TouchBar + 1;
				bool confirmed = (p.Absorption || p.Trapped) && (p.FreshImb || p.DeltaFlip);
				if (!confirmed) { p.Phase = 3; p.Reason = "FIRST_RETEST_NO_OF_CONFIRM"; return; }
				p.Entry = ev.C;
				p.Stop = d > 0 ? p.Extreme - StopBufferTicks * tickSize : p.Extreme + StopBufferTicks * tickSize;
				p.EntryBar = ev.Idx;
				if (c.Target > 0 && d * (c.Target - p.Entry) <= 0) { p.Phase = 3; p.Reason = "NO_ROOM_TO_TARGET"; return; }
				p.Entered = true;
				p.Reason = "RETEST_ENTERED";
				p.Phase = 2;
				p.EntryL2 = TakeL2Snap(d, ev.TimeCt);   // v2.8
				countRetestV2Entered++;
				return;
			}
			if (sessionOver || windowOver) { p.Phase = 3; p.Reason = "RETEST_NO_CONFIRM"; }
		}

		// Jeron M4 (stop and reverse), logged for research: the other side from the failing close, stop beyond that bar.
		private void LogReversal(Candidate c, BarEvidence ev, string why)
		{
			if (!LogReversalCandidates) return;
			ReversalCand r = new ReversalCand();
			reversalSeq++;
			countReversals++;
			r.Id = c.Id + "-REV" + reversalSeq.ToString("000", CultureInfo.InvariantCulture);
			r.Src = c;
			r.Dir = -c.Dir;
			r.StartBar = ev.Idx;
			r.Entry = ev.C;
			r.Stop = r.Dir > 0 ? ev.L - StopBufferTicks * tickSize : ev.H + StopBufferTicks * tickSize;
			string tref, skipped;
			r.Target = FindTarget(r.Entry, r.Dir, c.Zone, r.Stop, out tref, out skipped);
			r.TargetRef = tref;
			reversals.Add(r);
			Dictionary<string, string> row = ZoneRow("REVERSAL_CANDIDATE", c.Zone, ev);
			row["EventId"] = r.Id;
			row["Direction"] = JeronFmt.DirText(r.Dir);
			row["State"] = "REVERSAL";
			row["EntryRef"] = JeronFmt.P(r.Entry);
			row["StopAnchor"] = JeronFmt.P(r.Stop);
			row["TargetRef"] = r.TargetRef;
			row["TargetPrice"] = r.Target > 0 ? JeronFmt.P(r.Target) : "";
			double risk = r.Dir * (r.Entry - r.Stop);
			row["RewardRisk"] = r.Target > 0 && risk > 0 ? JeronFmt.N(r.Dir * (r.Target - r.Entry) / risk, 2) : "";
			row["SignalTimeCT"] = JeronFmt.T(c.SignalCt);
			row["RetestModel"] = "v2";
			row["Detail"] = why + "; from " + c.Id + " (" + JeronFmt.DirText(c.Dir) + " " + c.Family + "); research only, not an entry";
			FillEvidence(row, ev);
			Write(row);
		}

		private void UpdateReversals(BarEvidence ev)
		{
			for (int i = reversals.Count - 1; i >= 0; i--)
			{
				ReversalCand r = reversals[i];
				if (r.Resolved) { reversals.RemoveAt(i); continue; }
				if (ev.Idx <= r.StartBar) continue;
				r.Bars++;
				int d = r.Dir;
				double fav = d > 0 ? ev.H - r.Entry : r.Entry - ev.L;
				double adv = d > 0 ? r.Entry - ev.L : ev.H - r.Entry;
				if (fav / tickSize > r.Mfe) r.Mfe = fav / tickSize;
				if (adv / tickSize > r.Mae) r.Mae = adv / tickSize;
				bool hitTarget = r.Target > 0 && (d > 0 ? ev.H >= r.Target : ev.L <= r.Target);
				bool hitStop = d > 0 ? ev.L <= r.Stop : ev.H >= r.Stop;
				string outcome = "";
				if (hitTarget && hitStop) outcome = "AMBIGUOUS_SAME_BAR";
				else if (hitStop) outcome = "STOP_FIRST";
				else if (hitTarget) outcome = "TARGET_FIRST";
				else if (ev.TimeCt >= r.Src.SessionEndCt) outcome = "SESSION_END";
				if (outcome.Length > 0) ResolveReversal(r, ev, outcome);
			}
		}

		private void ResolveReversal(ReversalCand r, BarEvidence ev, string outcome)
		{
			r.Resolved = true;
			Dictionary<string, string> row = ZoneRow("REVERSAL_OUTCOME", r.Src.Zone, ev);
			row["EventId"] = r.Id;
			row["Direction"] = JeronFmt.DirText(r.Dir);
			row["State"] = "REVERSAL";
			row["EntryRef"] = JeronFmt.P(r.Entry);
			row["StopAnchor"] = JeronFmt.P(r.Stop);
			row["TargetRef"] = r.TargetRef;
			row["TargetPrice"] = r.Target > 0 ? JeronFmt.P(r.Target) : "";
			row["OutcomeType"] = outcome;
			row["MFETicks"] = JeronFmt.N(r.Mfe, 1);
			row["MAETicks"] = JeronFmt.N(r.Mae, 1);
			row["BarsToResolve"] = r.Bars.ToString(CultureInfo.InvariantCulture);
			row["PnLTicks"] = JeronFmt.N(PnLFor(r.Dir, r.Entry, r.Stop, r.Target, outcome, ev.C), 2);
			row["ExitPrice"] = JeronFmt.P(ExitFor(outcome, r.Stop, r.Target, ev.C));
			row["SignalTimeCT"] = JeronFmt.T(r.Src.SignalCt);
			row["RetestModel"] = r.Model;
			row["Detail"] = "reversal candidate outcome (research only); same-bar stop+target counts as the stop";
			Write(row);
		}

		// One matched row per signal and fail tolerance: immediate path and retest path side by side.
		private void WriteRetestRow(Candidate c, RetestPath p, BarEvidence ev)
		{
			p.Written = true;
			countRetestRows++;
			Dictionary<string, string> row = ZoneRow("RETEST", c.Zone, ev);
			row["EventId"] = c.Id;
			row["Direction"] = JeronFmt.DirText(c.Dir);
			row["State"] = c.Kind;
			row["CandidateStatus"] = c.Status;
			row["EntryRef"] = JeronFmt.P(c.Entry);
			row["StopAnchor"] = JeronFmt.P(c.Stop);
			row["TargetRef"] = c.TargetRef;
			row["TargetPrice"] = c.Target > 0 ? JeronFmt.P(c.Target) : "";
			row["SetupFamily"] = c.Family;
			row["Grade"] = c.Grade;
			row["EventValid"] = c.EventValid ? "Y" : "N";
			row["EntryStatus"] = c.Status;
			row["Flags"] = c.Flags;
			row["SignalTimeCT"] = JeronFmt.T(c.SignalCt);
			row["ImmediateOutcome"] = c.Outcome;
			row["ImmediatePnLTicks"] = JeronFmt.N(c.PnL, 2);
			row["ImmediateMFETicks"] = JeronFmt.N(c.MfeTicks, 1);
			row["ImmediateMAETicks"] = JeronFmt.N(c.MaeTicks, 1);
			row["Outcome15"] = c.Outcome15;
			row["PnL15Ticks"] = JeronFmt.N(c.Pnl15, 2);
			row["RetestFailTicks"] = p.FailTicks.ToString(CultureInfo.InvariantCulture);
			row["RetestOccurred"] = p.TouchBar >= 0 ? "Y" : "N";
			row["RetestBarsElapsed"] = p.BarsToTouch >= 0 ? p.BarsToTouch.ToString(CultureInfo.InvariantCulture) : "";
			row["RetestDepthTicks"] = JeronFmt.N(p.DepthTicks, 1);
			row["RetestTrapped"] = p.TouchBar >= 0 ? (p.Trapped ? "Y" : "N") : "";
			row["RetestConfirmed"] = p.Entered ? "Y" : "N";
			row["RetestReason"] = p.Reason;
			row["RetestEntry"] = JeronFmt.P(p.Entry);
			if (p.EntryL2 != null) FillL2(row, p.EntryL2);   // v2.8: book at the retest entry
			row["RetestStop"] = JeronFmt.P(p.Stop);
			row["RetestOutcome"] = p.Outcome;
			row["RetestPnLTicks"] = JeronFmt.N(p.PnL, 2);
			row["RetestMFETicks"] = p.Entered ? JeronFmt.N(p.Mfe, 1) : "";
			row["RetestMAETicks"] = p.Entered ? JeronFmt.N(p.Mae, 1) : "";
			row["RetestModel"] = p.Model;
			row["BreakStrength"] = c.BreakStrength;
			row["AtrAtSignal"] = JeronFmt.N(c.AtrAtSignal, 2);
			if (p.Model == "v2")
			{
				row["TravelBeforeRetestATR"] = JeronFmt.N(p.TravelAtr, 2);
				row["TouchesBeforeDeparture"] = p.TouchesBeforeDeparture.ToString(CultureInfo.InvariantCulture);
				row["RetestOppDelta"] = p.TouchBar >= 0 ? JeronFmt.N(p.OppDelta, 0) : "";
				row["RetestAbsorption"] = p.TouchBar >= 0 ? (p.Absorption ? "Y" : "N") : "";
				row["RetestFreshImbalance"] = p.TouchBar >= 0 ? (p.FreshImb ? "Y" : "N") : "";
				row["RetestDeltaFlip"] = p.TouchBar >= 0 ? (p.DeltaFlip ? "Y" : "N") : "";
				row["RetestReactionBars"] = p.ReactionBars >= 0 ? p.ReactionBars.ToString(CultureInfo.InvariantCulture) : "";
				row["InBalanceMiddle"] = p.InMiddle;
				row["Detail"] = "matched research record, ORDER-FLOW retest (v2): departure >= " + JeronFmt.N(RetestV2MinTravelAtr, 2) + " ATR and "
					+ RetestV2MinBars.ToString(CultureInfo.InvariantCulture) + " bars, first retest only within " + RetestV2WindowBars.ToString(CultureInfo.InvariantCulture)
					+ " bars, needs (absorption or trapped) and (fresh imbalance or delta flip); fail = full-bodied close "
					+ p.FailTicks.ToString(CultureInfo.InvariantCulture) + " ticks beyond the far edge of " + c.Zone.Id;
			}
			else
				row["Detail"] = "matched research record: immediate vs retest entry for the same signal; window=" + RetestWindowBars.ToString(CultureInfo.InvariantCulture)
					+ " bars, fail = close " + p.FailTicks.ToString(CultureInfo.InvariantCulture) + " ticks beyond the far edge of " + c.Zone.Id;
			Write(row);
		}

		// Playback stopped before the session end: close what is still open so every signal has a row.
		private void CloseOpenAtDataEnd(BarEvidence ev)
		{
			foreach (Candidate c in candidates)
			{
				if (c.Resolved || c.AwaitConfirm) continue;
				ResolveCandidate(c, ev, "DATA_END");
			}
			foreach (ReversalCand r in reversals) if (!r.Resolved) ResolveReversal(r, ev, "DATA_END");
			// v2.10: research setups and exit models still open
			foreach (RWatch w in watches)
			{
				if (w.Phase == 3) ResolveWatch(w, ev, "DATA_END");
				else if (w.Phase < 3) EndWatch(w, ev, "DATA_END_NO_ENTRY");
			}
			watches.Clear();
			if (LogExitModels)
			{
				foreach (Candidate c in candidates)
				{
					if (!NeedsExitRow(c) || c.ExitRowWritten || !c.Resolved) continue;
					if (!c.AltInit) InitExitModels(c);
					if (!c.Fav03Done) { c.Fav03Outcome = "DATA_END"; c.Fav03Pnl = c.Dir * (ev.C - c.Entry) / tickSize; c.Fav03Done = true; }
					if (!c.Car04Done) { c.Car04Outcome = "DATA_END"; c.Car04Pnl = c.Dir * (ev.C - c.Entry) / tickSize; c.Car04Done = true; }
					WriteExitModelRow(c, ev);
				}
			}
			if (!LogRetestPaths && !LogRetestV2) return;
			foreach (Candidate c in candidates)
			{
				if (c.Retests == null || !c.Resolved) continue;
				foreach (RetestPath p in c.Retests)
				{
					if (p.Written) continue;
					if (p.Phase == 2) { p.Outcome = "DATA_END"; p.PnL = c.Dir * (ev.C - p.Entry) / tickSize; }
					else if (p.Phase < 2) p.Reason = p.Phase == 1 ? "RETEST_NO_CONFIRM" : "DATA_END_NO_RETEST";
					p.Phase = 3;
					WriteRetestRow(c, p, ev);
				}
			}
		}

		// Exit warnings (Part 2 ~25:08: first opposing aggression that actually moves price;
		// Part 3 ~41:27: two or more opposing effort zones in a row -> get out).
		private void CheckExitWarnings(Candidate c, BarEvidence ev)
		{
			int d = c.Dir;
			bool oppDelta = -d * ev.Delta > 0;
			bool oppImb = d > 0 ? ev.SellImb > 0 : ev.BuyImb > 0;
			bool oppLarge = d > 0 ? ev.LargeSell >= LargeTradeEvidenceMin : ev.LargeBuy >= LargeTradeEvidenceMin;
			bool oppStack = d > 0 ? ev.MaxSellStack >= MinStackForZone : ev.MaxBuyStack >= MinStackForZone;
			bool movedAgainst = d * (ev.C - ev.O) < 0;

			if (!c.WarnFirst && oppDelta && (oppImb || oppLarge) && movedAgainst)
			{
				c.WarnFirst = true;
				countWarn++;
				WriteExitWarn(c, ev, "FIRST_OPPOSING_AGGRESSION_REWARDED");
			}
			bool oppEffort = oppDelta && (oppStack || oppLarge);
			c.OppStreak = oppEffort ? c.OppStreak + 1 : 0;
			if (!c.WarnDouble && ExitWarnOppStreak > 0 && c.OppStreak >= ExitWarnOppStreak)
			{
				c.WarnDouble = true;
				countWarn++;
				WriteExitWarn(c, ev, "OPPOSING_EFFORT_STREAK_" + c.OppStreak.ToString(CultureInfo.InvariantCulture));
			}
		}

		private void WriteExitWarn(Candidate c, BarEvidence ev, string why)
		{
			MaybeExitOnWarn(c, ev, why);   // S1.0 (off by default)
			Dictionary<string, string> row = ZoneRow("EXIT_WARN", c.Zone, ev);
			row["EventId"] = c.Id;
			row["Direction"] = JeronFmt.DirText(c.Dir);
			row["State"] = c.Kind;
			row["CandidateStatus"] = c.Status;
			row["Reasons"] = why;
			row["EntryRef"] = JeronFmt.P(c.Entry);
			row["StopAnchor"] = JeronFmt.P(c.Stop);
			row["MFETicks"] = JeronFmt.N(c.MfeTicks, 1);
			row["MAETicks"] = JeronFmt.N(c.MaeTicks, 1);
			row["Detail"] = "open P/L ticks at close=" + JeronFmt.N(c.Dir * (ev.C - c.Entry) / tickSize, 1);
			FillCandidateCols(row, c, ev);
			FillEvidence(row, ev);
			Write(row);
		}

		// ==============================================================================
		//  v2.10 Comparative order-flow research rules v1.1 (logging only; never changes an entry)
		//  Rule ids follow "Comparative Order Flow Research Rules v1.1". All thresholds are OUR parameters (section 5d).
		// ==============================================================================
		private void ResetResearchSession()
		{
			// anything still open from the previous trading date is closed before the new session starts
			if (lastEv != null)
			{
				foreach (RWatch w in watches)
				{
					if (w.Phase == 3) ResolveWatch(w, lastEv, "SESSION_END");
					else if (w.Phase < 3) EndWatch(w, lastEv, "SESSION_END_NO_ENTRY");
				}
			}
			watches.Clear();
			// prior RTH levels (PD high/low for CAR03, prior RTH POC for FAV03 / FAV02 when the plan has no balance_poc)
			if (rthHigh > double.MinValue && rthLow < double.MaxValue) { pdRthHigh = rthHigh; pdRthLow = rthLow; }
			if (rthProfile.Count > 0)
			{
				long best = -1;
				foreach (KeyValuePair<long, long> kv in rthProfile)
					if (kv.Value > best) { best = kv.Value; prevRthPoc = kv.Key * tickSize; }
			}
			rthProfile.Clear();
			rthHigh = double.MinValue; rthLow = double.MaxValue;
			onHigh = double.MinValue; onLow = double.MaxValue;
			cvdAvgVal = double.NaN;
			dayEntryCount = 0;
			sessionPnlTicks = 0;
			fav01LastExtremeBar[0] = -1; fav01LastExtremeBar[1] = -1;
			for (int k = 0; k < 2; k++) { excActive[k] = false; excCount[k] = 0; excStartBar[k] = -1; excExtremeBar[k] = -1; excExtreme[k] = double.NaN; }
			flushStates.Clear();
		}

		// RTH (NY) and overnight (Asia + London) extremes, updated after each bar is evaluated
		private void UpdateSessionLevels(BarEvidence ev)
		{
			if (ev.Session == JeronSession.NewYork)
			{
				if (ev.H > rthHigh) rthHigh = ev.H;
				if (ev.L < rthLow) rthLow = ev.L;
			}
			else if (ev.Session == JeronSession.Asia || ev.Session == JeronSession.London)
			{
				if (ev.H > onHigh) onHigh = ev.H;
				if (ev.L < onLow) onLow = ev.L;
			}
		}

		private static int ConfRank(string conf)
		{
			string c = (conf ?? "").Trim().ToLowerInvariant();
			if (c == "high") return 3;
			if (c == "med" || c == "medium") return 2;
			if (c == "low") return 1;
			return 0;
		}

		// RIZ01: the plan's main level = its highest-confidence decision zone(s). No confidence anywhere = no main level.
		private string MarkMainLevels()
		{
			int best = 0;
			List<string> names = new List<string>();
			lock (zLock)
			{
				foreach (TrackedZone z in zones)
					if (z.Active && z.FromPlan && !z.TargetOnly && ConfRank(z.Confidence) > best) best = ConfRank(z.Confidence);
				if (best == 0) return "";
				foreach (TrackedZone z in zones)
				{
					if (!z.Active || !z.FromPlan || z.TargetOnly) continue;
					z.IsMain = ConfRank(z.Confidence) == best;
					if (z.IsMain) names.Add(z.Id);
				}
			}
			return string.Join(",", names.ToArray());
		}

		private double MinSinceOpen(DateTime ct)
		{
			if (tradingDate == DateTime.MinValue || clock == null) return double.NaN;
			return (ct - tradingDate.AddMinutes(clock.NyStartMin)).TotalMinutes;
		}

		private static string YN(bool b) { return b ? "Y" : "N"; }

		private static long FloorDiv(long a, long b)
		{
			return a >= 0 ? a / b : -((-a + b - 1) / b);
		}

		private static string ZoneKind(TrackedZone z)
		{
			if (z == null) return "";
			if (z.FromPlan) return z.TargetOnly ? "PLAN_TARGET" : "PLAN_DECISION";
			if (z.IsFrozen) return "FROZEN";
			if (z.IsPower) return "POWER";
			return z.Qualified ? "IMB_QUALIFIED" : "IMB_MINOR";
		}

		private bool InPlanZone(double price)
		{
			double tol = TouchToleranceTicks * tickSize;
			lock (zLock)
			{
				foreach (TrackedZone z in zones)
					if (z.Active && z.FromPlan && price >= z.Lo - tol && price <= z.Hi + tol) return true;
			}
			return false;
		}

		// G1 / G2 / G3 (location vs VWAP, balance, lava, ES) / bar-level G4. Every value is known at this bar's close.
		private void FillContextFeatures(Dictionary<string, string> row, BarEvidence ev, int d, double entry)
		{
			double atr = ev.Atr;
			row["rule_version"] = ResearchRulesVersion;
			row["plan_id"] = plan != null ? plan.Id : "";
			row["min_since_rth_open"] = JeronFmt.N(MinSinceOpen(ev.TimeCt), 0);
			row["day_of_week"] = tradingDate == DateTime.MinValue ? "" : tradingDate.DayOfWeek.ToString().Substring(0, 3).ToUpperInvariant();
			int m = ev.TimeCt.Hour * 60 + ev.TimeCt.Minute;
			if (plan != null)
			{
				bool inNoTrade = false;
				foreach (int[] w in plan.NoTrade) if (m >= w[0] && m < w[1]) { inNoTrade = true; break; }
				row["in_no_trade_window"] = YN(inNoTrade);
				row["plan_review"] = plan.Review;
				row["gamma_regime"] = plan.GexRegime;
				row["price_vs_gamma_flip_atr"] = !double.IsNaN(plan.Hvl) && atr > 0 ? JeronFmt.N((entry - plan.Hvl) / atr, 2) : "";
				bool hasBal = !double.IsNaN(plan.BalanceLo) && plan.BalanceHi > plan.BalanceLo;
				row["balance_defined"] = YN(hasBal);
				row["pos_in_balance"] = hasBal ? JeronFmt.N((entry - plan.BalanceLo) / (plan.BalanceHi - plan.BalanceLo), 3) : "";
				bool lava = false;
				foreach (double[] band in plan.Lava) if (entry >= band[0] && entry <= band[1]) { lava = true; break; }
				row["in_lava"] = YN(lava);
				double lvl = d > 0 ? plan.EsLongAbove : plan.EsShortBelow;
				row["es_gate_ok"] = esIdx > 0 && !double.IsNaN(lvl) && !double.IsNaN(esClose) ? YN(d > 0 ? esClose > lvl : esClose < lvl) : "";
				// v2.11 ES research columns (logged only)
				row["es_dist_gate_pts"] = esIdx > 0 && !double.IsNaN(lvl) && !double.IsNaN(esClose) ? JeronFmt.N(d * (esClose - lvl), 2) : "";
				row["es_dist_settle_pts"] = esIdx > 0 && !double.IsNaN(plan.EsSettle) && !double.IsNaN(esClose) ? JeronFmt.N(d * (esClose - plan.EsSettle), 2) : "";
				row["es_gate_blocks"] = esIdx > 0 && !double.IsNaN(lvl) ? YN(EsGateBlocksEntries) : "";
			}
			if (esIdx > 0 && !double.IsNaN(esClose) && esCloseCt != DateTime.MinValue)
			{
				double age = (ev.TimeCt - esCloseCt).TotalMinutes;
				row["es_close"] = JeronFmt.P(esClose);
				row["es_bar_age_min"] = JeronFmt.N(age, 0);
				row["es_bar_stale"] = YN(age < -0.01 || age > 2.01);
			}
			row["plan_context"] = effectiveContext.ToString();
			row["dist_vwap_atr"] = completedVwap > 0 && atr > 0 ? JeronFmt.N(d * (entry - completedVwap) / atr, 2) : "";
			row["vwap_sigma"] = completedVwap > 0 && ev.VwapSigma > 0 ? JeronFmt.N((entry - completedVwap) / ev.VwapSigma, 2) : "";
			row["ema21_aligned"] = double.IsNaN(ev.Ema) ? "" : YN(d * (ev.C - ev.Ema) > 0);
			row["cvd_avg_aligned"] = double.IsNaN(ev.CvdAvg) ? "" : YN(d * (ev.Cvd - ev.CvdAvg) > 0);
			BarEvidence back;
			row["cvd_slope_5"] = evidence.TryGetValue(ev.Idx - 5, out back) ? JeronFmt.N(d * (ev.Cvd - back.Cvd), 0) : "";
			row["displacement_atr"] = atr > 0 ? JeronFmt.N((ev.H - ev.L) / atr, 2) : "";
		}

		// G3 / G4 / G10 / G12 / G13 on CANDIDATE and SHADOW rows
		private void FillCandidateFeatures(Dictionary<string, string> row, Candidate c, TrackedZone z, BarEvidence ev, int idx, int d, bool trapped, string rule)
		{
			if (!LogResearchRules && !LogExitModels) return;
			FillContextFeatures(row, ev, d, c.Entry);
			double atr = ev.Atr;
			row["zone_kind"] = ZoneKind(z);
			row["side_rule"] = z.FromPlan ? rule : "";
			row["zone_confidence"] = ConfRank(z.Confidence) > 0 ? ConfRank(z.Confidence).ToString(CultureInfo.InvariantCulture) : "";
			row["zone_width_pts"] = JeronFmt.P(z.Hi - z.Lo);
			bool counter = (effectiveContext == JeronContextBias.Bullish && d < 0) || (effectiveContext == JeronContextBias.Bearish && d > 0);
			row["counter_context"] = YN(counter);
			row["in_middle_third"] = ZoneInBalanceMiddle(z);
			row["imb_stack_count"] = c.TrigStack.ToString(CultureInfo.InvariantCulture);
			row["trapped_before"] = c.Family == "RESPONSE" ? YN(trapped) : "";
			bool deltaAgainst = (ev.C != ev.O && ev.Delta != 0 && Math.Sign(ev.Delta) != Math.Sign(ev.C - ev.O)) || ev.HighEffortLowReward;
			row["delta_against_close"] = YN(deltaAgainst);
			row["risk_ticks"] = JeronFmt.N(d * (c.Entry - c.Stop) / tickSize, 1);
			// T11 extended move into the zone: furthest distance from the zone over the bars before the first touch
			int tb = z.TouchBar >= 0 ? z.TouchBar : idx;
			double far = double.NaN;
			for (int k = tb - Math.Max(1, MoveIntoZoneBars); k < tb; k++)
			{
				BarEvidence b;
				if (!evidence.TryGetValue(k, out b)) continue;
				double dist = z.Approach > 0 ? b.H - z.Hi : z.Lo - b.L;
				if (double.IsNaN(far) || dist > far) far = dist;
			}
			row["move_into_zone_atr"] = !double.IsNaN(far) && atr > 0 ? JeronFmt.N(Math.Max(0, far) / atr, 2) : "";
			// G13 (RIZ03): what this trade's number would be today, entries already at this zone, P/L so far
			row["trade_index_of_day"] = (dayEntryCount + 1).ToString(CultureInfo.InvariantCulture);
			row["trades_at_zone_so_far"] = z.EntryCount.ToString(CultureInfo.InvariantCulture);
			row["session_pnl_ticks_so_far"] = JeronFmt.N(sessionPnlTicks, 1);
			// G10 (RIZ01): the main level nearest the entry and what it has accepted so far
			TrackedZone main = null;
			double mainDist = double.MaxValue;
			lock (zLock)
			{
				foreach (TrackedZone mz in zones)
				{
					if (!mz.Active || !mz.IsMain) continue;
					double dd = Math.Abs(c.Entry - (mz.Lo + mz.Hi) / 2.0);
					if (dd < mainDist) { mainDist = dd; main = mz; }
				}
			}
			if (main != null)
			{
				row["riz01_is_main_level"] = YN(z.IsMain);
				row["riz01_accept_side"] = main.RizSide > 0 ? "ABOVE" : (main.RizSide < 0 ? "BELOW" : "NONE");
				row["riz01_min_to_accept"] = JeronFmt.N(main.RizAcceptMin, 0);
				row["riz01_with_acceptance"] = main.RizSide == 0 ? "" : YN(main.RizSide == d);
			}
			// G12 (BOF01): is the broken edge also a low-volume area of today's session profile?
			double edge = d > 0 ? z.Hi : z.Lo;
			double ratio = SessionLvnRatio(edge);
			bool isLvn = !double.IsNaN(ratio) && ratio <= LvnMaxRatio;
			bool premarked = z.FromPlan || z.IsFrozen;
			row["bof01_broken_level_type"] = premarked ? (isLvn ? "BOTH" : "PLAN_ZONE_EDGE") : (isLvn ? "LVN" : "INTRADAY_EDGE");
			row["bof01_edge_lvn_ratio"] = JeronFmt.N(ratio, 3);
		}

		// volume of the LvnRowTicks bucket holding 'price' / mean bucket volume over the session's traded range
		private double SessionLvnRatio(double price)
		{
			if (sessProfile.Count == 0) return double.NaN;
			long rt = Math.Max(1, LvnRowTicks);
			Dictionary<long, long> buckets = new Dictionary<long, long>();
			long minB = long.MaxValue, maxB = long.MinValue, total = 0;
			foreach (KeyValuePair<long, long> kv in sessProfile)
			{
				long b = FloorDiv(kv.Key, rt);
				long v;
				buckets.TryGetValue(b, out v);
				buckets[b] = v + kv.Value;
				total += kv.Value;
				if (b < minB) minB = b;
				if (b > maxB) maxB = b;
			}
			long n = maxB - minB + 1;
			if (n < 3 || total <= 0) return double.NaN;
			double mean = (double)total / n;
			long tb = FloorDiv((long)Math.Round(price / tickSize), rt);
			long tv;
			buckets.TryGetValue(tb, out tv);
			return tv / mean;
		}

		// LVN of a leg (bars fromBar..toBar): LvnRowTicks buckets between the leg's low and high, outer LvnEdgeExcludePct
		// skipped at each end; the qualifying bucket (volume <= LvnMaxRatio x mean) nearest the leg's extreme is the LVN.
		private bool FindLegLvn(int fromBar, int toBar, int d, out double lo, out double hi, out double ratio, out string why)
		{
			lo = hi = ratio = double.NaN;
			why = "";
			if (toBar < fromBar) { int t = fromBar; fromBar = toBar; toBar = t; }
			long rt = Math.Max(1, LvnRowTicks);
			Dictionary<long, long> buckets = new Dictionary<long, long>();
			long minB = long.MaxValue, maxB = long.MinValue, total = 0;
			for (int k = fromBar; k <= toBar; k++)
			{
				BarEvidence b;
				if (!evidence.TryGetValue(k, out b)) { why = "PROFILE_GAP"; return false; }
				foreach (KeyValuePair<long, long> kv in b.Prof)
				{
					long bk = FloorDiv(kv.Key, rt);
					long v;
					buckets.TryGetValue(bk, out v);
					buckets[bk] = v + kv.Value;
					total += kv.Value;
					if (bk < minB) minB = bk;
					if (bk > maxB) maxB = bk;
				}
			}
			if (total <= 0) { why = "NO_FOOTPRINT_PROFILE"; return false; }
			long n = maxB - minB + 1;
			long excl = Math.Max(1, (long)Math.Round(n * LvnEdgeExcludePct / 100.0));
			if (n < 5 || minB + excl > maxB - excl) { why = "LEG_TOO_SHORT"; return false; }
			double mean = (double)total / n;
			long pick = long.MinValue;
			double pickRatio = double.NaN, minRatio = double.MaxValue;
			long start = d > 0 ? maxB - excl : minB + excl;
			long stop = d > 0 ? minB + excl : maxB - excl;
			long step = d > 0 ? -1 : 1;
			for (long bk = start; d > 0 ? bk >= stop : bk <= stop; bk += step)
			{
				long v;
				buckets.TryGetValue(bk, out v);
				double r = v / mean;
				if (r < minRatio) minRatio = r;
				if (r <= LvnMaxRatio && pick == long.MinValue) { pick = bk; pickRatio = r; }
			}
			if (pick == long.MinValue)
			{
				ratio = minRatio < double.MaxValue ? minRatio : double.NaN;
				why = "NO_LVN_IN_LEG";
				return false;
			}
			lo = pick * rt * tickSize;
			hi = (pick * rt + rt - 1) * tickSize;
			ratio = pickRatio;
			return true;
		}

		// ---- FAV03 / CAR04 exit models on the same entries (EXIT_MODEL rows) ----
		private bool NeedsExitRow(Candidate c)
		{
			return LogExitModels && !c.IsShadow && c.EventValid;
		}

		private bool ExitModelsDone(Candidate c)
		{
			return !NeedsExitRow(c) || c.ExitRowWritten;
		}

		private void InitExitModels(Candidate c)
		{
			c.AltInit = true;
			int d = c.Dir;
			c.AltRisk = d * (c.Entry - c.Stop);
			c.Car04Stop = c.Stop;
			if (!(c.AltRisk > 0))
			{
				c.Fav03Outcome = "INVALID_RISK"; c.Car04Outcome = "INVALID_RISK";
				c.Fav03Done = true; c.Car04Done = true;
				return;
			}
			double poc = double.NaN;
			string pref = "";
			if (plan != null && planActive && !double.IsNaN(plan.BalancePoc)) { poc = plan.BalancePoc; pref = "BALANCE_POC"; }
			else if (!double.IsNaN(prevRthPoc)) { poc = prevRthPoc; pref = "PRIOR_RTH_POC"; }
			c.Fav03Target = poc;
			c.Fav03Ref = pref;
			if (double.IsNaN(poc)) { c.Fav03Outcome = "NO_POC"; c.Fav03Done = true; }
			else if (d * (poc - c.Entry) <= tickSize) { c.Fav03Outcome = "POC_BEHIND_ENTRY"; c.Fav03Done = true; }
		}

		private void StepExitModels(BarEvidence ev)
		{
			if (!LogExitModels) return;
			foreach (Candidate c in candidates)
			{
				if (!NeedsExitRow(c) || c.ExitRowWritten || c.AwaitConfirm || c.TriggerBar >= ev.Idx) continue;
				if (!c.AltInit) InitExitModels(c);
				int d = c.Dir;
				bool sessionOver = ev.TimeCt >= c.SessionEndCt;
				if (!c.Fav03Done)
				{
					bool hitT = d > 0 ? ev.H >= c.Fav03Target : ev.L <= c.Fav03Target;
					bool hitS = d > 0 ? ev.L <= c.Stop : ev.H >= c.Stop;
					string o = hitT && hitS ? "AMBIGUOUS_SAME_BAR" : (hitS ? "STOP_FIRST" : (hitT ? "TARGET_FIRST" : (sessionOver ? "SESSION_END" : "")));
					if (o.Length > 0)
					{
						c.Fav03Outcome = o;
						c.Fav03Pnl = PnLFor(d, c.Entry, c.Stop, c.Fav03Target, o, ev.C);
						c.Fav03Done = true;
					}
				}
				if (!c.Car04Done)
				{
					bool hitT = c.Target > 0 && (d > 0 ? ev.H >= c.Target : ev.L <= c.Target);
					bool hitS = d > 0 ? ev.L <= c.Car04Stop : ev.H >= c.Car04Stop;
					string o = hitT && hitS ? "AMBIGUOUS_SAME_BAR" : (hitS ? "STOP_FIRST" : (hitT ? "TARGET_FIRST" : (sessionOver ? "SESSION_END" : "")));
					if (o.Length > 0)
					{
						if (o == "STOP_FIRST" && c.Car04Armed) o = "BREAKEVEN";
						c.Car04Outcome = o;
						if (o == "TARGET_FIRST") c.Car04Pnl = d * (c.Target - c.Entry) / tickSize;
						else if (o == "SESSION_END") c.Car04Pnl = d * (ev.C - c.Entry) / tickSize;
						else c.Car04Pnl = d * (c.Car04Stop - c.Entry) / tickSize;   // stop, break-even or same-bar (counted as the stop)
						c.Car04Done = true;
					}
					else if (!c.Car04Armed)
					{
						// armed at this close; the break-even stop applies from the next bar (no intrabar ordering guessed)
						double fav = d > 0 ? ev.H - c.Entry : c.Entry - ev.L;
						if (fav >= Car04BreakEvenR * c.AltRisk) { c.Car04Armed = true; c.Car04Stop = c.Entry; c.Car04ArmBar = ev.Idx; }
					}
				}
				if (c.Fav03Done && c.Car04Done && c.Resolved) WriteExitModelRow(c, ev);
			}
		}

		private void WriteExitModelRow(Candidate c, BarEvidence ev)
		{
			c.ExitRowWritten = true;
			countExitRows++;
			Dictionary<string, string> row = ZoneRow("EXIT_MODEL", c.Zone, ev);
			row["EventId"] = c.Id;
			row["Direction"] = JeronFmt.DirText(c.Dir);
			row["State"] = c.Kind;
			row["CandidateStatus"] = c.Status;
			row["SetupFamily"] = c.Family;
			row["Grade"] = c.Grade;
			row["EventValid"] = c.EventValid ? "Y" : "N";
			row["EntryStatus"] = c.Status;
			row["EntryRef"] = JeronFmt.P(c.Entry);
			row["StopAnchor"] = JeronFmt.P(c.Stop);
			row["TargetRef"] = c.TargetRef;
			row["TargetPrice"] = c.Target > 0 ? JeronFmt.P(c.Target) : "";
			row["OutcomeType"] = c.Outcome;
			row["PnLTicks"] = JeronFmt.N(c.PnL, 2);
			row["SignalTimeCT"] = JeronFmt.T(c.SignalCt);
			row["rule_id"] = "FAV03|CAR04";
			row["rule_version"] = ResearchRulesVersion;
			row["plan_id"] = plan != null ? plan.Id : "";
			row["risk_ticks"] = JeronFmt.N(c.AltRisk / tickSize, 1);
			row["fav03_target"] = JeronFmt.P(c.Fav03Target);
			row["fav03_ref"] = c.Fav03Ref;
			row["fav03_outcome"] = c.Fav03Outcome;
			row["fav03_pnl_ticks"] = JeronFmt.N(c.Fav03Pnl, 2);
			row["car04_outcome"] = c.Car04Outcome;
			row["car04_pnl_ticks"] = JeronFmt.N(c.Car04Pnl, 2);
			row["car04_be_bar"] = c.Car04ArmBar >= 0 ? (c.Car04ArmBar - c.TriggerBar).ToString(CultureInfo.InvariantCulture) : "";
			row["Detail"] = "exit models on the same entry (research only): JERON = OutcomeType/PnLTicks; FAV03 = one target at "
				+ (c.Fav03Ref.Length > 0 ? c.Fav03Ref : "no POC") + "; CAR04 = Jeron target, stop to entry after +" + JeronFmt.N(Car04BreakEvenR, 2)
				+ "R (from the next bar); same-bar stop+target counts as the stop";
			Write(row);
		}

		// ---- research setups (FAV01, FAV02, CAR01, CAR03, RIZ01) ----
		private RWatch NewWatch(string rule, string stage, int dir, BarEvidence ev, TrackedZone z)
		{
			watchSeq++;
			RWatch w = new RWatch();
			w.Id = "RR-" + rule + "-" + ev.TimeCt.ToString("yyyyMMdd", CultureInfo.InvariantCulture) + "-" + watchSeq.ToString("0000", CultureInfo.InvariantCulture);
			w.Rule = rule;
			w.Stage = stage;
			w.Dir = dir;
			w.StartBar = ev.Idx;
			w.Zone = z;
			w.AtrAt = ev.Atr;
			w.SessionEndCt = SessionEndFor(ev.TimeCt);
			watches.Add(w);
			return w;
		}

		// CAR01: after an event at a plan decision zone, the leg away from the zone; its LVN is the re-entry level
		private void StartCar01(Candidate c)
		{
			BarEvidence ev = lastEv;
			if (ev == null) return;
			TrackedZone z = c.Zone;
			int d = c.Dir;
			foreach (RWatch o in watches)
				if (o.Rule == "CAR01" && o.Zone == z && o.Dir == d && o.Phase < 3) return;   // one open watch per zone and side
			RWatch w = NewWatch("CAR01", "LVN_RETURN", d, ev, z);
			w.Linked = c.Id;
			w.OriginBar = ev.Idx;
			w.OriginPrice = d > 0 ? z.Lo : z.Hi;   // a close back through the zone's far edge ends the idea
			w.Extreme = d > 0 ? ev.H : ev.L;
			w.ExtremeBar = ev.Idx;
			double atr = ev.Atr > 0 ? ev.Atr : 0;
			w.MinImpulse = (z.Hi - z.Lo) + Car01MinImpulseAtr * atr;   // must leave the zone by Car01MinImpulseAtr x ATR
			w.NeedPassive = true;   // Carmine: passive side holds the LVN (opposing aggression without a close through)
			w.AfterAsOf = true;     // the LVN forms after the open
			w.OriginPremarked = true;
		}

		private void DetectResearchSetups(BarEvidence ev, BarEvidence prev)
		{
			if (ev.Session != JeronSession.NewYork) return;   // research setups are read in the NY session only (as entries are)
			DetectFav01(ev);
			DetectCar03(ev, prev);
			if (plan != null && planActive)
			{
				DetectFav02(ev);
				DetectRiz01(ev);
			}
		}

		// FAV01 (Fabio trend model, shadow study): a leg of >= Fav01ImpulseAtr x ATR within Fav01LookbackBars bars,
		// making a new extreme on this bar. Its LVN is read when the leg pauses; entry on aggression at the LVN.
		private void DetectFav01(BarEvidence ev)
		{
			if (ev.Atr <= 0) return;
			int n = Math.Max(2, Fav01LookbackBars);
			for (int d = -1; d <= 1; d += 2)
			{
				int k = d > 0 ? 1 : 0;
				bool open = false;
				foreach (RWatch o in watches) if (o.Rule == "FAV01" && o.Dir == d && o.Phase < 3) { open = true; break; }
				if (open) continue;
				int oIdx = -1;
				double origin = double.NaN, ext = d > 0 ? ev.H : ev.L;
				bool newExtreme = true;
				for (int j = ev.Idx - n + 1; j < ev.Idx; j++)
				{
					BarEvidence b;
					if (!evidence.TryGetValue(j, out b)) continue;
					double o2 = d > 0 ? b.L : b.H;
					if (double.IsNaN(origin) || d * (origin - o2) > 0) { origin = o2; oIdx = j; }
					if (d * ((d > 0 ? b.H : b.L) - ext) > 0) newExtreme = false;
				}
				if (oIdx < 0 || !newExtreme || oIdx <= fav01LastExtremeBar[k]) continue;
				if (d * (ext - origin) < Fav01ImpulseAtr * ev.Atr) continue;
				RWatch w = NewWatch("FAV01", "IMPULSE_LVN", d, ev, null);
				w.OriginBar = oIdx;
				w.OriginPrice = origin;
				w.Extreme = ext;
				w.ExtremeBar = ev.Idx;
				w.NeedAggr = true;      // Fabio: no aggression, no trade
				w.AfterAsOf = true;     // level created after the plan's as-of time -> experiment D only
				w.OriginPremarked = false;
				fav01LastExtremeBar[k] = ev.Idx;
			}
		}

		// FAV02 (Fabio mean-reversion model): price leaves the plan balance and closes back inside.
		// FIRST_MOVE = entry on that close (what Fabio says not to take); PULLBACK = entry at the reclaim leg's LVN.
		private void DetectFav02(BarEvidence ev)
		{
			if (double.IsNaN(plan.BalanceLo) || plan.BalanceHi <= plan.BalanceLo) return;
			double brk = BreakTicks * tickSize;
			double buf = StopBufferTicks * tickSize;
			for (int s = -1; s <= 1; s += 2)
			{
				int k = s > 0 ? 1 : 0;
				double edge = s > 0 ? plan.BalanceHi : plan.BalanceLo;
				if (!excActive[k])
				{
					bool outside = s > 0 ? ev.H > edge + brk : ev.L < edge - brk;
					if (!outside) continue;
					excActive[k] = true;
					excStartBar[k] = ev.Idx;
					excExtreme[k] = s > 0 ? ev.H : ev.L;
					excExtremeBar[k] = ev.Idx;
				}
				else
				{
					double ex = s > 0 ? ev.H : ev.L;
					if (s * (ex - excExtreme[k]) > 0) { excExtreme[k] = ex; excExtremeBar[k] = ev.Idx; }
				}
				bool back = s > 0 ? ev.C < edge : ev.C > edge;
				if (!back) continue;
				excActive[k] = false;
				if (excCount[k] >= Math.Max(1, Fav02MaxPerSide)) continue;
				excCount[k]++;
				int d = -s;
				double poc = double.NaN;
				string pref = "";
				if (!double.IsNaN(plan.BalancePoc)) { poc = plan.BalancePoc; pref = "BALANCE_POC"; }
				else if (!double.IsNaN(prevRthPoc)) { poc = prevRthPoc; pref = "PRIOR_RTH_POC"; }
				string exTicks = JeronFmt.N(s * (excExtreme[k] - edge) / tickSize, 1);
				string exBars = (ev.Idx - excStartBar[k] + 1).ToString(CultureInfo.InvariantCulture);

				RWatch f = NewWatch("FAV02", "FIRST_MOVE", d, ev, null);
				f.FixedTarget = true; f.FixedTargetPrice = poc; f.FixedTargetRef = pref;
				f.OriginPremarked = true;
				f.Extra["fav02_excursion_ticks"] = exTicks; f.Extra["fav02_excursion_bars"] = exBars;
				f.Extra["fav02_poc"] = JeronFmt.P(poc); f.Extra["fav02_poc_ref"] = pref;
				EnterWatch(f, ev, ev.C, s > 0 ? excExtreme[k] + buf : excExtreme[k] - buf);

				RWatch p = NewWatch("FAV02", "PULLBACK", d, ev, null);
				p.OriginBar = excExtremeBar[k];
				p.OriginPrice = excExtreme[k];
				p.Extreme = d > 0 ? ev.H : ev.L;
				p.ExtremeBar = ev.Idx;
				p.NeedAggr = true;
				p.FixedTarget = true; p.FixedTargetPrice = poc; p.FixedTargetRef = pref;
				p.AfterAsOf = true;
				p.OriginPremarked = true;
				p.Extra["fav02_excursion_ticks"] = exTicks; p.Extra["fav02_excursion_bars"] = exBars;
				p.Extra["fav02_poc"] = JeronFmt.P(poc); p.Extra["fav02_poc_ref"] = pref;
			}
		}

		// CAR03 (Carmine stop run and reclaim): price came from the inside, ran >= Car03MinFlushTicks beyond a known level,
		// then a bar closed back across it with a body in the reclaim direction within Car03MaxReclaimBars bars.
		private void DetectCar03(BarEvidence ev, BarEvidence prev)
		{
			if (prev == null) return;
			List<object[]> levels = new List<object[]>();   // { key, type, price, side (+1 = long reclaim of a low), zone }
			if (!double.IsNaN(pdRthLow)) levels.Add(new object[] { "PD_LOW", "PD_LOW", pdRthLow, 1, null });
			if (!double.IsNaN(pdRthHigh)) levels.Add(new object[] { "PD_HIGH", "PD_HIGH", pdRthHigh, -1, null });
			if (onLow < double.MaxValue) levels.Add(new object[] { "ON_LOW", "ON_LOW", onLow, 1, null });
			if (onHigh > double.MinValue) levels.Add(new object[] { "ON_HIGH", "ON_HIGH", onHigh, -1, null });
			lock (zLock)
			{
				foreach (TrackedZone z in zones)
				{
					if (!z.Active || !z.FromPlan || z.TargetOnly || z.StartBar < 0) continue;
					levels.Add(new object[] { z.Id + ".lo", "PLAN_ZONE", z.Lo, 1, z });
					levels.Add(new object[] { z.Id + ".hi", "PLAN_ZONE", z.Hi, -1, z });
				}
			}
			double flush = Car03MinFlushTicks * tickSize;
			double buf = StopBufferTicks * tickSize;
			foreach (object[] lv in levels)
			{
				string key = (string)lv[0];
				string type = (string)lv[1];
				double L = (double)lv[2];
				int s = (int)lv[3];
				TrackedZone z = lv[4] as TrackedZone;
				FlushState st;
				if (!flushStates.TryGetValue(key, out st)) { st = new FlushState(); flushStates[key] = st; }
				if (!st.Active)
				{
					bool cameFrom = s > 0 ? prev.C > L : prev.C < L;
					bool poked = s > 0 ? ev.L <= L - flush : ev.H >= L + flush;
					if (!cameFrom || !poked) continue;
					st.Active = true;
					st.StartBar = ev.Idx;
					st.Extreme = s > 0 ? ev.L : ev.H;
					st.DeltaSum = 0;
				}
				else
				{
					double ex = s > 0 ? ev.L : ev.H;
					if (s * (st.Extreme - ex) > 0) st.Extreme = ex;
				}
				st.DeltaSum += ev.Delta;
				bool reclaim = s > 0 ? (ev.C > L && ev.C > ev.O) : (ev.C < L && ev.C < ev.O);
				if (reclaim)
				{
					st.Active = false;
					if (st.Signals >= 2) continue;
					st.Signals++;
					RWatch w = NewWatch("CAR03", "STOP_RUN_RECLAIM", s, ev, z);
					w.OriginPremarked = true;
					double fl = s * (L - st.Extreme);
					w.Extra["car03_level_type"] = type;
					w.Extra["car03_level"] = JeronFmt.P(L);
					w.Extra["car03_flush_ticks"] = JeronFmt.N(fl / tickSize, 1);
					w.Extra["car03_flush_atr"] = ev.Atr > 0 ? JeronFmt.N(fl / ev.Atr, 2) : "";
					w.Extra["car03_flush_delta"] = JeronFmt.I(st.DeltaSum);
					w.Extra["car03_reclaim_bars"] = (ev.Idx - st.StartBar + 1).ToString(CultureInfo.InvariantCulture);
					EnterWatch(w, ev, ev.C, s > 0 ? st.Extreme - buf : st.Extreme + buf);
				}
				else if (ev.Idx - st.StartBar + 1 >= Math.Max(1, Car03MaxReclaimBars)) st.Active = false;   // accepted beyond: no stop run
			}
		}

		// RIZ01 (Rizzo): 'Acceptance closes' closes beyond the main level -> entry with the accepting side, stop beyond the
		// zone's other edge, target = the next qualified level. At most two acceptances (one flip) per zone per day.
		private void DetectRiz01(BarEvidence ev)
		{
			int need = Math.Max(1, AcceptBars);
			double buf = StopBufferTicks * tickSize;
			TrackedZone[] snapshot;
			lock (zLock) snapshot = zones.ToArray();
			foreach (TrackedZone z in snapshot)
			{
				if (!z.Active || !z.IsMain || z.StartBar < 0) continue;
				z.RizAbove = ev.C > z.Hi ? z.RizAbove + 1 : 0;
				z.RizBelow = ev.C < z.Lo ? z.RizBelow + 1 : 0;
				int side = z.RizAbove == need ? 1 : (z.RizBelow == need ? -1 : 0);
				if (side == 0 || side == z.RizSide || z.RizAccepts >= 2) continue;
				z.RizSide = side;
				z.RizAccepts++;
				if (double.IsNaN(z.RizAcceptMin)) z.RizAcceptMin = MinSinceOpen(ev.TimeCt);
				RWatch w = NewWatch("RIZ01", side > 0 ? "ACCEPT_ABOVE" : "ACCEPT_BELOW", side, ev, z);
				w.OriginPremarked = true;
				w.Extra["riz01_is_main_level"] = "Y";
				w.Extra["riz01_accept_side"] = side > 0 ? "ABOVE" : "BELOW";
				w.Extra["riz01_min_to_accept"] = JeronFmt.N(MinSinceOpen(ev.TimeCt), 0);
				EnterWatch(w, ev, ev.C, side > 0 ? z.Lo - buf : z.Hi + buf);
			}
		}

		private void UpdateResearch(BarEvidence ev)
		{
			if (watches.Count == 0) return;
			foreach (RWatch w in watches.ToArray())
				if (w.Phase < 4) StepWatch(w, ev);
			watches.RemoveAll(delegate(RWatch w) { return w.Phase >= 4; });
		}

		private void StepWatch(RWatch w, BarEvidence ev)
		{
			int d = w.Dir;
			if (w.Phase == 3)
			{
				if (ev.Idx <= w.EntryBar) return;
				w.BarsInTrade++;
				double fav = d > 0 ? ev.H - w.Entry : w.Entry - ev.L;
				double adv = d > 0 ? w.Entry - ev.L : ev.H - w.Entry;
				if (fav / tickSize > w.Mfe) w.Mfe = fav / tickSize;
				if (adv / tickSize > w.Mae) w.Mae = adv / tickSize;
				bool hitT = w.Target > 0 && (d > 0 ? ev.H >= w.Target : ev.L <= w.Target);
				bool hitS = d > 0 ? ev.L <= w.Stop : ev.H >= w.Stop;
				string o = hitT && hitS ? "AMBIGUOUS_SAME_BAR" : (hitS ? "STOP_FIRST" : (hitT ? "TARGET_FIRST" : (ev.TimeCt >= w.SessionEndCt ? "SESSION_END" : "")));
				if (o.Length > 0) ResolveWatch(w, ev, o);
				return;
			}
			if (ev.Idx <= w.StartBar) return;
			w.Bars++;
			int window = Math.Max(1, ResearchWindowBars);
			bool sessionOver = ev.TimeCt >= w.SessionEndCt;
			// the leg's origin is where the idea is wrong
			if (!double.IsNaN(w.OriginPrice) && d * (ev.C - w.OriginPrice) < 0) { EndWatch(w, ev, "LEG_FAILED"); return; }

			if (w.Phase == 0 || w.Phase == 1)
			{
				double ext = d > 0 ? ev.H : ev.L;
				if (d * (ext - w.Extreme) > 0)
				{
					// the leg is still extending: its LVN is read again once it pauses
					w.Extreme = ext;
					w.ExtremeBar = ev.Idx;
					w.Phase = 0;
					w.LvnLo = double.NaN; w.LvnHi = double.NaN; w.LvnRatio = double.NaN;
					if (w.Rule == "FAV01") fav01LastExtremeBar[d > 0 ? 1 : 0] = ev.Idx;
					if (sessionOver) EndWatch(w, ev, "SESSION_END_NO_ENTRY");
					return;
				}
				if (w.Phase == 0)
				{
					if (w.MinImpulse > 0 && d * (w.Extreme - w.OriginPrice) < w.MinImpulse)
					{
						if (sessionOver) EndWatch(w, ev, "SESSION_END_NO_ENTRY");
						else if (w.Bars >= window) EndWatch(w, ev, "NEVER_LEFT");
						return;
					}
					double lo, hi, ratio;
					string why;
					if (!FindLegLvn(w.OriginBar, w.ExtremeBar, d, out lo, out hi, out ratio, out why))
					{
						w.LvnRatio = ratio;
						EndWatch(w, ev, why);
						return;
					}
					w.LvnLo = lo; w.LvnHi = hi; w.LvnRatio = ratio;
					w.LegBars = Math.Abs(w.ExtremeBar - w.OriginBar) + 1;
					w.Phase = 1;
					w.Bars = 0;   // the window counts from the bar the LVN became known
					return;       // touches count from the next bar
				}
				// phase 1: LVN known, waiting for price to come back to it
				bool touch = d > 0 ? ev.L <= w.LvnHi : ev.H >= w.LvnLo;
				if (!touch)
				{
					if (sessionOver) EndWatch(w, ev, "SESSION_END_NO_TOUCH");
					else if (w.Bars >= window) EndWatch(w, ev, "NO_LVN_TOUCH");
					return;
				}
				w.Phase = 2;
				w.TouchBar = ev.Idx;
				w.BarsToTouch = w.Bars;
			}

			// phase 2: at the LVN. Read each bar until one closes back beyond it in the trade's direction.
			double near = d > 0 ? w.LvnHi : w.LvnLo;
			double far = d > 0 ? w.LvnLo : w.LvnHi;
			double ex2 = d > 0 ? ev.L : ev.H;
			if (double.IsNaN(w.TouchExtreme) || d * (w.TouchExtreme - ex2) > 0) w.TouchExtreme = ex2;
			double opp = -d * ev.Delta;
			bool oppImb = d > 0 ? ev.SellImb > 0 : ev.BuyImb > 0;
			bool oppLarge = d > 0 ? ev.LargeSell >= LargeTradeEvidenceMin : ev.LargeBuy >= LargeTradeEvidenceMin;
			bool closedThrough = d > 0 ? ev.C < far : ev.C > far;
			if (opp > 0 && (oppImb || oppLarge || opp >= MinAbsDelta) && !closedThrough) w.OppAggr = true;   // passive side held
			bool aggr = d * ev.Delta > 0 && ((d > 0 ? ev.BuyImb > 0 : ev.SellImb > 0)
				|| (d > 0 ? ev.LargeBuy >= LargeTradeEvidenceMin : ev.LargeSell >= LargeTradeEvidenceMin) || d * ev.Delta >= MinAbsDelta);
			bool fail = (d > 0 ? ev.C < far - ResearchFailTicks * tickSize : ev.C > far + ResearchFailTicks * tickSize) && d * (ev.C - ev.O) < 0;
			if (fail) { EndWatch(w, ev, "LVN_FAILED"); return; }
			bool closedBack = d > 0 ? (ev.C > near && ev.C > ev.O) : (ev.C < near && ev.C < ev.O);
			if (closedBack)
			{
				w.Aggr = aggr;
				if (w.NeedPassive && !w.OppAggr) { EndWatch(w, ev, "NO_PASSIVE_HOLD"); return; }   // first reaction only
				if (w.NeedAggr && !aggr) { EndWatch(w, ev, "NO_AGGRESSION"); return; }
				double buf = StopBufferTicks * tickSize;
				double stop = d > 0 ? Math.Min(w.TouchExtreme, w.LvnLo) - buf : Math.Max(w.TouchExtreme, w.LvnHi) + buf;
				EnterWatch(w, ev, ev.C, stop);
				return;
			}
			if (sessionOver) EndWatch(w, ev, "SESSION_END_NO_ENTRY");
			else if (w.Bars - w.BarsToTouch >= window) EndWatch(w, ev, "NO_CONFIRM");
		}

		private void EnterWatch(RWatch w, BarEvidence ev, double entry, double stop)
		{
			int d = w.Dir;
			if (d * (entry - stop) <= 0) { EndWatch(w, ev, "INVALID_RISK"); return; }
			w.Entry = entry;
			w.Stop = stop;
			w.EntryBar = ev.Idx;
			w.EntryCt = ev.TimeCt;
			w.Phase = 3;
			string tref = "", skipped;
			if (w.FixedTarget && !double.IsNaN(w.FixedTargetPrice) && d * (w.FixedTargetPrice - entry) > tickSize)
			{
				w.Target = w.FixedTargetPrice;
				tref = w.FixedTargetRef;
			}
			else
			{
				w.Target = FindTarget(entry, d, w.Zone, stop, out tref, out skipped);
				if (w.FixedTarget) tref = (double.IsNaN(w.FixedTargetPrice) ? "NO_POC>" : "POC_BEHIND_ENTRY>") + tref;
			}
			w.TargetRef = tref;
			LinkSameBar(w, ev);
			countResearchSignals++;
			long cnt;
			researchByRule.TryGetValue(w.Rule, out cnt);
			researchByRule[w.Rule] = cnt + 1;
			Dictionary<string, string> row = WatchRow("RESEARCH_SIGNAL", w, ev);
			FillContextFeatures(row, ev, d, entry);
			FillEvidence(row, ev);
			double risk = d * (entry - stop);
			row["EntryRef"] = JeronFmt.P(entry);
			row["StopAnchor"] = JeronFmt.P(stop);
			row["TargetRef"] = w.TargetRef;
			row["TargetPrice"] = w.Target > 0 ? JeronFmt.P(w.Target) : "";
			row["RewardRisk"] = w.Target > 0 ? JeronFmt.N(d * (w.Target - entry) / risk, 2) : "";
			row["risk_ticks"] = JeronFmt.N(risk / tickSize, 1);
			FillL2(row, TakeL2Snap(d, ev.TimeCt));   // CAR02: the book at the research entry (PROXY until depth history exists)
			Write(row);
		}

		// the Jeron candidate (if any) on the same bar and direction: what Jeron's gates did with this moment
		private void LinkSameBar(RWatch w, BarEvidence ev)
		{
			string status = "NONE", id = "";
			foreach (Candidate c in candidates)
			{
				if (c.Dir != w.Dir || c.SignalCt != ev.TimeCt) continue;
				if (!c.IsShadow) { status = c.Status; id = c.Id; break; }
				if (id.Length == 0) { status = "SHADOW_" + c.Status; id = c.Id; }
			}
			w.LinkedStatus = status;
			if (w.Linked.Length == 0) w.Linked = id;
		}

		private void ResolveWatch(RWatch w, BarEvidence ev, string outcome)
		{
			w.Phase = 4;
			w.Outcome = outcome;
			w.Pnl = PnLFor(w.Dir, w.Entry, w.Stop, w.Target, outcome, ev.C);
			Dictionary<string, string> row = WatchRow("RESEARCH_OUTCOME", w, ev);
			row["EntryRef"] = JeronFmt.P(w.Entry);
			row["StopAnchor"] = JeronFmt.P(w.Stop);
			row["TargetRef"] = w.TargetRef;
			row["TargetPrice"] = w.Target > 0 ? JeronFmt.P(w.Target) : "";
			row["OutcomeType"] = outcome;
			row["MFETicks"] = JeronFmt.N(w.Mfe, 1);
			row["MAETicks"] = JeronFmt.N(w.Mae, 1);
			row["BarsToResolve"] = w.BarsInTrade.ToString(CultureInfo.InvariantCulture);
			row["PnLTicks"] = JeronFmt.N(w.Pnl, 2);
			row["ExitPrice"] = JeronFmt.P(ExitFor(outcome, w.Stop, w.Target, ev.C));
			row["risk_ticks"] = JeronFmt.N(w.Dir * (w.Entry - w.Stop) / tickSize, 1);
			Write(row);
		}

		private void EndWatch(RWatch w, BarEvidence ev, string reason)
		{
			w.Phase = 4;
			w.Reason = reason;
			countResearchNoEntry++;
			Dictionary<string, string> row = WatchRow("RESEARCH_NOENTRY", w, ev);
			Write(row);
		}

		private Dictionary<string, string> WatchRow(string type, RWatch w, BarEvidence ev)
		{
			Dictionary<string, string> row;
			if (w.Zone != null) row = ZoneRow(type, w.Zone, ev);
			else
			{
				row = NewRow(type);
				row["EvidenceTimeLocal"] = JeronFmt.T(ev.TimeLocal);
				row["EvidenceTimeCT"] = JeronFmt.T(ev.TimeCt);
				row["ProcessedTimeLocal"] = CurrentBar >= 0 ? JeronFmt.T(Time[0]) : "";
				row["Session"] = ev.Session.ToString();
				row["Price"] = JeronFmt.P(ev.C);
				row["VWAP"] = JeronFmt.P(ev.Vwap);
			}
			int d = w.Dir;
			row["EventId"] = w.Id;
			row["Direction"] = JeronFmt.DirText(d);
			row["State"] = w.Rule;
			row["SignalTimeCT"] = JeronFmt.T(w.EntryCt);
			row["rule_id"] = w.Rule;
			row["rule_stage"] = w.Stage;
			row["rule_version"] = ResearchRulesVersion;
			row["research_reason"] = w.Reason;
			row["linked_event_id"] = w.Linked;
			row["jeron_status_same_bar"] = w.LinkedStatus;
			row["level_created_after_asof"] = w.AfterAsOf ? "1" : "0";
			row["origin_premarked"] = YN(w.OriginPremarked);
			row["plan_id"] = plan != null ? plan.Id : "";
			row["zone_kind"] = ZoneKind(w.Zone);
			if (!double.IsNaN(w.OriginPrice))
			{
				row["leg_origin_price"] = JeronFmt.P(w.OriginPrice);
				row["leg_extreme_price"] = JeronFmt.P(w.Extreme);
				row["leg_atr"] = w.AtrAt > 0 ? JeronFmt.N(d * (w.Extreme - w.OriginPrice) / w.AtrAt, 2) : "";
				row["leg_bars"] = w.LegBars >= 0 ? w.LegBars.ToString(CultureInfo.InvariantCulture) : "";
				row["lvn_vol_ratio"] = JeronFmt.N(w.LvnRatio, 3);
			}
			if (!double.IsNaN(w.LvnLo))
			{
				row["lvn_lo"] = JeronFmt.P(w.LvnLo);
				row["lvn_hi"] = JeronFmt.P(w.LvnHi);
				row["lvn_in_plan_zone"] = YN(InPlanZone((w.LvnLo + w.LvnHi) / 2.0));
				row["bars_to_lvn_touch"] = w.BarsToTouch >= 0 ? w.BarsToTouch.ToString(CultureInfo.InvariantCulture) : "";
				if (w.TouchBar >= 0)
				{
					row["lvn_touch_depth_ticks"] = JeronFmt.N(d * ((d > 0 ? w.LvnHi : w.LvnLo) - w.TouchExtreme) / tickSize, 1);
					row["lvn_opp_aggression"] = YN(w.OppAggr);
					row["lvn_aggression"] = YN(w.Aggr);
				}
			}
			foreach (KeyValuePair<string, string> kv in w.Extra) row[kv.Key] = kv.Value;
			row["Detail"] = "research rule " + w.Rule + " " + w.Stage + " (" + ResearchRulesVersion + "); research only, not an entry"
				+ (w.AfterAsOf ? "; level made after the plan as-of (shadow study)" : "");
			return row;
		}


		// ==============================================================================
		//  S1.2 Fast load: evaluate only the recent trading day(s), warm up the day before, skip the rest
		// ==============================================================================
		private void ComputeEvalWindow()
		{
			evalStartDate = warmStartDate = evalStartLocal = warmStartLocal = DateTime.MinValue;
			DateTime from;
			string fd = (EvaluateFromDate ?? "").Trim();
			if (fd.Length > 0 && DateTime.TryParseExact(fd, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out from))
				evalStartDate = from.Date;
			else if (EvaluateLastDays > 0)
			{
				DateTime last = DateTime.Now;
				try { if (BarsArray[0] != null && BarsArray[0].Count > 0) last = BarsArray[0].GetTime(BarsArray[0].Count - 1); } catch { }
				DateTime td;
				try { td = new SessionIterator(BarsArray[0]).GetTradingDay(last).Date; }
				catch { td = JeronSessionClock.ToCentral(last, NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo).Date; }
				evalStartDate = PrevWeekdays(td, EvaluateLastDays - 1);
			}
			if (evalStartDate == DateTime.MinValue) return;   // every loaded day
			warmStartDate = PrevWeekdays(evalStartDate, Math.Max(0, WarmupDays));
			// a trading date's session opens at Asia start (17:00 CT) on the calendar day before
			evalStartLocal = CtToLocal(evalStartDate.AddDays(-1).AddMinutes(clock.AsiaStartMin));
			warmStartLocal = CtToLocal(warmStartDate.AddDays(-1).AddMinutes(clock.AsiaStartMin));
		}

		private static DateTime PrevWeekdays(DateTime d, int n)
		{
			while (n > 0)
			{
				d = d.AddDays(-1);
				if (d.DayOfWeek != DayOfWeek.Saturday && d.DayOfWeek != DayOfWeek.Sunday) n--;
			}
			return d;
		}

		private static DateTime CtToLocal(DateTime ct)
		{
			try
			{
				TimeZoneInfo central = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
				return TimeZoneInfo.ConvertTime(DateTime.SpecifyKind(ct, DateTimeKind.Unspecified), central, NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);
			}
			catch { return ct; }
		}

		// 2 = evaluate (unchanged tracker logic), 1 = warm-up (state only), 0 = skip
		private int SessionMode()
		{
			if (evalStartDate == DateTime.MinValue || tradingDate == DateTime.MinValue || tradingDate >= evalStartDate) return 2;
			if (tradingDate >= warmStartDate) return 1;
			return 0;
		}

		// warm-up: the same evidence build from the bar / Volumetric data (ATR, EMA, RTH profile for the prior RTH POC) and
		// session extremes as an evaluated bar, but no plan, zones, candidates, outcomes, research rows or log rows
		private void WarmupBar(int idx)
		{
			int ba = CurrentBar - idx;
			BarEvidence ev = BuildEvidence(idx, ba);
			evidence[idx] = ev;
			lastEv = ev;
			if (ev.H > sessHigh) sessHigh = ev.H;
			if (ev.L < sessLow) sessLow = ev.L;
			UpdateSessionLevels(ev);
			countWarmupBars++;
		}

		private string FastLoadText()
		{
			if (evalStartDate == DateTime.MinValue) return "every loaded day";
			return "from " + evalStartDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture)
				+ " (warm-up " + (warmStartDate < evalStartDate ? warmStartDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) : "none") + ")";
		}

		// ==============================================================================
		//  S1.0 Auto trading. Orders come ONLY from candidates the research code marked Qualified.
		//  Nothing here changes a candidate, a gate or an outcome row; it only decides whether to send the order.
		// ==============================================================================
		private void ResetDailyTrading()
		{
			tradesToday = 0;
			lossStreak = 0;
			dailyPnlTicks = 0;
			haltReason = "";
			flattenSent = false;
			approvalOk = false;
			entryQueue.Clear();
		}

		private void ProcessEntryQueue()
		{
			if (entryQueue.Count == 0) return;
			List<Candidate> queue = new List<Candidate>(entryQueue);
			entryQueue.Clear();
			foreach (Candidate c in queue) TryEnter(c);
		}

		private void TryEnter(Candidate c)
		{
			int d = c.Dir;
			double px = Close[0];   // first tick of the bar after the signal bar
			DateTime ct = lastEv != null ? lastEv.TimeCt : JeronSessionClock.ToCentral(Times[0][0], NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);
			int m = (int)ct.TimeOfDay.TotalMinutes;
			List<string> block = new List<string>();

			// who is allowed to trade today
			if (!AutoTradeEnabled) block.Add("AUTO_TRADE_OFF");
			if (State == State.Historical && !TradeHistoricalBars) block.Add("HISTORICAL_BAR");
			if (State == State.Realtime && !AllowLiveAccount && !IsSimAccount()) block.Add("LIVE_ACCOUNT_BLOCKED");
			if (plan == null || !planActive) block.Add("NO_ACTIVE_PLAN");
			else
			{
				if (RequirePlanReview && plan.Review != "APPROVED")
					block.Add(plan.Review.Length == 0 ? "PLAN_NOT_REVIEWED" : "PLAN_REVIEW_" + JeronFmt.SafeFileToken(plan.Review));
				foreach (int[] w in plan.NoTrade)
					if (m >= w[0] && m < w[1]) { block.Add("PLAN_NO_TRADE_WINDOW"); break; }
			}
			if (RequireManualApproval && !ManualApprovalOk()) block.Add("NO_MANUAL_APPROVAL");

			// what and when
			if (!GradeAllowed(c.Grade)) block.Add("GRADE_NOT_ALLOWED");
			if (m < clock.NyStartMin || m >= clock.NyEndMin || (lastEntryMin >= 0 && m >= lastEntryMin)) block.Add("OUTSIDE_ENTRY_HOURS");
			if (c.Target <= 0) block.Add("NO_TARGET");

			// daily risk
			int limit = MaxTradesPerDay > 0 ? MaxTradesPerDay : int.MaxValue;
			if (plan != null && plan.MaxTrades >= 0) limit = Math.Min(limit, plan.MaxTrades);
			if (tradesToday >= limit) block.Add("MAX_TRADES_REACHED");
			if (haltReason.Length > 0) block.Add(haltReason);
			if (Position.MarketPosition != MarketPosition.Flat || entryPending) block.Add("ALREADY_IN_TRADE");

			// price still makes sense at the decision tick
			double tk = tickSize;
			if (d > 0 ? px <= c.Stop + tk : px >= c.Stop - tk) block.Add("PRICE_PAST_STOP");
			if (c.Target > 0 && (d > 0 ? px >= c.Target - tk : px <= c.Target + tk)) block.Add("PRICE_PAST_TARGET");
			if (MaxEntrySlippageTicks > 0 && Math.Abs(px - c.Entry) > MaxEntrySlippageTicks * tk) block.Add("ENTRY_SLIPPAGE");

			double risk = d * (px - c.Stop);
			double rr = risk > 0 && c.Target > 0 ? d * (c.Target - px) / risk : double.NaN;
			string detail = "signal close=" + JeronFmt.P(c.Entry) + " decision tick=" + JeronFmt.P(px)
				+ " riskTicks=" + JeronFmt.N(risk / tk, 1) + " rrAtTick=" + JeronFmt.N(rr, 2)
				+ " tradesToday=" + tradesToday.ToString(CultureInfo.InvariantCulture) + "/" + (limit == int.MaxValue ? "none" : limit.ToString(CultureInfo.InvariantCulture))
				+ " dayPnLTicks=" + JeronFmt.N(dailyPnlTicks, 1) + " account=" + (Account != null ? Account.Name : "n/a")
				+ " review=" + (plan != null ? plan.Review : "");

			if (block.Count > 0)
			{
				countOrderBlocks++;
				WriteTradeRow("ORDER_BLOCKED", c, string.Join("|", block.ToArray()), detail, px);
				return;
			}

			string sig = (d > 0 ? "JL_" : "JS_") + c.Seq.ToString("00000", CultureInfo.InvariantCulture);
			SetStopLoss(sig, CalculationMode.Price, c.Stop, false);
			SetProfitTarget(sig, CalculationMode.Price, c.Target);
			if (d > 0) EnterLong(Math.Max(1, TradeQuantity), sig);
			else EnterShort(Math.Max(1, TradeQuantity), sig);
			liveCand = c;
			liveSignal = sig;
			entryPending = true;
			tradesToday++;
			countOrders++;
			WriteTradeRow("ORDER", c, "", "market " + (d > 0 ? "BUY" : "SELL") + " " + Math.Max(1, TradeQuantity).ToString(CultureInfo.InvariantCulture) + " signal=" + sig + "; " + detail, px);
		}

		private bool IsSimAccount()
		{
			if (Account == null) return true;
			try { if (Account.Provider == Provider.Simulator || Account.Provider == Provider.Playback) return true; } catch { }
			string n = Account.Name ?? "";
			foreach (string pre in (SimAccountPrefixes ?? "").Split(new char[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
				if (n.StartsWith(pre.Trim(), StringComparison.OrdinalIgnoreCase)) return true;
			return false;
		}

		private bool GradeAllowed(string grade)
		{
			if (string.IsNullOrWhiteSpace(AllowedGrades) || string.IsNullOrEmpty(grade)) return true;
			foreach (string g in AllowedGrades.Split(new char[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
				if (string.Equals(g.Trim(), grade, StringComparison.OrdinalIgnoreCase)) return true;
			return false;
		}

		// Approve_<date>.txt in the plan folder with a line approve=1 (Kyron's own go-ahead after reading Claude's review)
		private bool ManualApprovalOk()
		{
			if (approvalOk) return true;
			string path = Path.Combine(PlanFolderPath(), "Approve_" + tradingDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + ".txt");
			if (!File.Exists(path)) return false;
			try
			{
				using (FileStream fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
				using (StreamReader sr = new StreamReader(fs, Encoding.UTF8, true))
				{
					string ln;
					while ((ln = sr.ReadLine()) != null)
						if (ln.Replace(" ", "").Trim().ToLowerInvariant() == "approve=1") { approvalOk = true; break; }
				}
			}
			catch { return false; }
			return approvalOk;
		}

		private void CheckFlatten()
		{
			if (flattenMin < 0 || flattenSent || CurrentBar < 0 || Position.MarketPosition == MarketPosition.Flat) return;
			DateTime ct = JeronSessionClock.ToCentral(Times[0][0], NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo);
			int m = (int)ct.TimeOfDay.TotalMinutes;
			if (m < flattenMin || m >= clock.AsiaStartMin) return;
			flattenSent = true;
			if (Position.MarketPosition == MarketPosition.Long) ExitLong("FLATTEN", liveSignal);
			else ExitShort("FLATTEN", liveSignal);
			WriteTradeRow("FLATTEN", liveCand, "FLATTEN_TIME", "flatten at " + FlattenCT + " CT", Close[0]);
		}

		// Jeron M1 (research idea 2): exit at the first exit warning while the trade is not in profit. Off by default.
		private void MaybeExitOnWarn(Candidate c, BarEvidence ev, string why)
		{
			if (!ExitOnFirstExitWarn || c == null || c != liveCand || Position.MarketPosition == MarketPosition.Flat) return;
			double open = c.Dir * (ev.C - Position.AveragePrice) / tickSize;
			if (open > 0) return;
			if (c.Dir > 0) ExitLong("EXIT_WARN", liveSignal);
			else ExitShort("EXIT_WARN", liveSignal);
			WriteTradeRow("EXIT_SIGNAL", c, why, "exit on first warning; open ticks=" + JeronFmt.N(open, 1), ev.C);
		}

		protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity, int filled, double averageFillPrice,
			OrderState orderState, DateTime time, ErrorCode error, string comment)
		{
			if (order == null) return;
			TrackAtmOrder(order);   // S1.1 trade lines
			bool isEntry = liveSignal.Length > 0 && order.Name == liveSignal;
			if (isEntry && (orderState == OrderState.Rejected || orderState == OrderState.Cancelled) && filled == 0)
			{
				entryPending = false;
				if (tradesToday > 0) tradesToday--;
				WriteTradeRow("ORDER_" + orderState.ToString().ToUpperInvariant(), liveCand, error.ToString(), comment ?? "", averageFillPrice);
				liveCand = null;
				liveSignal = "";
				return;
			}
			// a rejected stop or target leaves the position unprotected: flatten at once
			if (orderState == OrderState.Rejected && (order.Name == "Stop loss" || order.Name == "Profit target") && Position.MarketPosition != MarketPosition.Flat)
			{
				if (Position.MarketPosition == MarketPosition.Long) ExitLong("PROTECT_FLAT", liveSignal);
				else ExitShort("PROTECT_FLAT", liveSignal);
				WriteTradeRow("PROTECTIVE_REJECTED", liveCand, error.ToString(), order.Name + " rejected (" + (comment ?? "") + "); position flattened", stopPrice);
			}
		}

		protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
		{
			if (execution == null || execution.Order == null) return;
			countFills++;
			if (execution.Order.Name == liveSignal)
			{
				entryPending = false;
				if (liveCand != null) DrawEntryPriceMarker(liveCand.Dir, Position.AveragePrice > 0 ? Position.AveragePrice : price, time, liveSignal);   // S1.1
			}
			WriteTradeRow("FILL", liveCand, execution.Order.Name, execution.Order.OrderAction.ToString() + " " + quantity.ToString(CultureInfo.InvariantCulture)
				+ " @ " + JeronFmt.P(price) + " order=" + execution.Order.Name + " time=" + JeronFmt.T(time), price);
		}

		protected override void OnPositionUpdate(Position position, double averagePrice, int quantity, MarketPosition marketPosition)
		{
			if (marketPosition != MarketPosition.Flat) return;
			ClearAtmOrders();   // S1.1
			double pnl = double.NaN;
			string exitName = "";
			if (SystemPerformance != null && SystemPerformance.AllTrades.Count > 0)
			{
				NinjaTrader.Cbi.Trade t = SystemPerformance.AllTrades[SystemPerformance.AllTrades.Count - 1];
				int dd = t.Entry.MarketPosition == MarketPosition.Long ? 1 : -1;
				pnl = dd * (t.Exit.Price - t.Entry.Price) / tickSize;
				try { exitName = t.Exit.Name ?? ""; } catch { exitName = ""; }
			}
			// S1.4: a live stop-loss fill is a stop event for the reversal-after-stop research rows
			if (LogS14Flags && liveCand != null && lastEv != null && exitName == "Stop loss")
				AddStopEvent(liveCand, lastEv.Idx, "LIVE_STOP");
			if (!double.IsNaN(pnl))
			{
				countTradesClosed++;
				dailyPnlTicks += pnl;
				totalPnlTicks += pnl;
				if (pnl < 0) lossStreak++;
				else if (pnl > 0) lossStreak = 0;
			}
			WriteTradeRow("TRADE_CLOSED", liveCand, "", "realized ticks/contract=" + JeronFmt.N(pnl, 1) + " day=" + JeronFmt.N(dailyPnlTicks, 1)
				+ " lossStreak=" + lossStreak.ToString(CultureInfo.InvariantCulture), averagePrice);
			liveCand = null;
			liveSignal = "";
			entryPending = false;
			if (haltReason.Length == 0)
			{
				if (MaxDailyLossTicks > 0 && dailyPnlTicks <= -MaxDailyLossTicks) haltReason = "DAILY_LOSS_LIMIT";
				else if (MaxConsecutiveLosses > 0 && lossStreak >= MaxConsecutiveLosses) haltReason = "LOSS_STREAK_LIMIT";
				if (haltReason.Length > 0) WriteTradeRow("HALT", null, haltReason, "no more entries today; research logging continues", averagePrice);
			}
		}

		private void WriteTradeRow(string type, Candidate c, string reasons, string detail, double price)
		{
			Dictionary<string, string> row = c != null && lastEv != null ? ZoneRow(type, c.Zone, lastEv) : NewRow(type);
			if (c != null)
			{
				row["EventId"] = c.Id;
				row["Direction"] = JeronFmt.DirText(c.Dir);
				row["State"] = c.Kind;
				row["CandidateStatus"] = c.Status;
				row["EntryRef"] = JeronFmt.P(c.Entry);
				row["StopAnchor"] = JeronFmt.P(c.Stop);
				row["TargetRef"] = c.TargetRef;
				row["TargetPrice"] = c.Target > 0 ? JeronFmt.P(c.Target) : "";
				row["SetupFamily"] = c.Family;
				row["Grade"] = c.Grade;
				row["Flags"] = c.Flags;
				row["SignalTimeCT"] = JeronFmt.T(c.SignalCt);
			}
			else if (lastEv != null) row["EvidenceTimeCT"] = JeronFmt.T(lastEv.TimeCt);
			row["ProcessedTimeLocal"] = JeronFmt.T(DateTime.Now);
			row["Price"] = JeronFmt.P(price);
			row["Reasons"] = reasons;
			row["Detail"] = detail;
			Write(row);
		}

		private string AutoConfigText()
		{
			return " | FASTLOAD evaluate=" + FastLoadText().Replace(" ", "_") + " | AUTO enabled=" + (AutoTradeEnabled ? "on" : "off") + " qty=" + TradeQuantity.ToString(CultureInfo.InvariantCulture)
				+ " historical=" + (TradeHistoricalBars ? "on" : "off") + " allowLive=" + (AllowLiveAccount ? "on" : "off") + " simPrefixes=" + SimAccountPrefixes + " accountSim=" + (IsSimAccount() ? "Y" : "N")
				+ " needReview=" + (RequirePlanReview ? "on" : "off") + " manualApproval=" + (RequireManualApproval ? "on" : "off")
				+ " maxTrades=" + MaxTradesPerDay.ToString(CultureInfo.InvariantCulture) + " maxLossTicks=" + MaxDailyLossTicks.ToString(CultureInfo.InvariantCulture)
				+ " maxLossStreak=" + MaxConsecutiveLosses.ToString(CultureInfo.InvariantCulture) + " lastEntry=" + LastEntryCT + " flatten=" + FlattenCT
				+ " grades=" + AllowedGrades + " maxSlipTicks=" + MaxEntrySlippageTicks.ToString(CultureInfo.InvariantCulture)
				+ " exitOnWarn=" + (ExitOnFirstExitWarn ? "on" : "off") + " account=" + (Account != null ? Account.Name : "n/a");
		}

		private string AutoSummaryText()
		{
			return " | FASTLOAD warmupBars=" + JeronFmt.I(countWarmupBars) + " skippedBars=" + JeronFmt.I(countSkippedBars) + " | AUTO orders=" + JeronFmt.I(countOrders) + " blocked=" + JeronFmt.I(countOrderBlocks) + " fills=" + JeronFmt.I(countFills)
				+ " closedTrades=" + JeronFmt.I(countTradesClosed) + " realizedTicks=" + JeronFmt.N(totalPnlTicks, 1);
		}

		private string AutoStatusText()
		{
			string pos = Position == null || Position.MarketPosition == MarketPosition.Flat ? "flat"
				: Position.MarketPosition.ToString() + " " + Position.Quantity.ToString(CultureInfo.InvariantCulture) + " @ " + JeronFmt.P(Position.AveragePrice);
			string review = plan == null ? "no plan" : (plan.Review.Length > 0 ? plan.Review : "NOT REVIEWED");
			return "Evaluating " + FastLoadText() + "\n" + "AUTO " + (AutoTradeEnabled ? "ON" : "OFF") + "  account " + (Account != null ? Account.Name : "n/a")
				+ (State == State.Realtime && !AllowLiveAccount && !IsSimAccount() ? " (LIVE BLOCKED)" : "")
				+ "  review " + review + (RequireManualApproval ? (approvalOk ? "  approved" : "  waiting Approve file") : "")
				+ "  trades " + tradesToday.ToString(CultureInfo.InvariantCulture) + "/" + MaxTradesPerDay.ToString(CultureInfo.InvariantCulture)
				+ "  day " + JeronFmt.N(dailyPnlTicks, 0) + "t  " + pos + (haltReason.Length > 0 ? "  HALT " + haltReason : "");
		}

		// ==============================================================================
		//  S1.1 ATM-STYLE TRADE LINES, copied from HarrisJigsawEventChainAutoTraderResearchV2 (HJ 2.17 display)
		//  TP   : green line, green "qty TP" tag
		//  ENTRY: tan line, [open PnL | qty] box (PnL marked at the current price: bid for longs, ask for shorts,
		//         else the last trade)
		//  STP  : red line, red "qty STP" tag
		//  Same colors, font (Segoe UI SemiBold 11), row height, tag shape, label offset and PnL modes as HJ.
		//  Display only. HJ's X-cancel boxes and TP/STP drag are NOT copied: this strategy's orders are changed
		//  only by its own rules, so nothing on the chart can move or cancel them.
		// ==============================================================================
		private readonly object atmLock = new object();
		private double atmLastPrice = double.NaN, atmBid = double.NaN, atmAsk = double.NaN;
		private double atmTpPrice = double.NaN, atmSlPrice = double.NaN;
		private int atmTpQty, atmSlQty;
		private Order atmTpOrder, atmSlOrder;

		private const float AtmRowHeight = 20f;
		private const float AtmTagTipWidth = 8f;

		// called on every tick of the primary series (NinjaScript thread); OnRender only reads the cached values
		private void UpdateAtmLastPrice()
		{
			try
			{
				if (CurrentBars[0] < 0) return;
				atmLastPrice = Closes[0][0];
				atmBid = GetCurrentBid(0);
				atmAsk = GetCurrentAsk(0);
			}
			catch { }
			if (ChartControl != null && EnableTradeLines && Position != null && Position.MarketPosition != MarketPosition.Flat) ForceRefresh();
		}

		// keeps the working stop / target price and quantity for the lines (called from OnOrderUpdate)
		private void TrackAtmOrder(Order order)
		{
			if (order == null) return;
			bool isTp = order.Name == "Profit target", isSl = order.Name == "Stop loss";
			if (!isTp && !isSl) return;
			OrderState s = order.OrderState;
			bool working = s == OrderState.Initialized || s == OrderState.Submitted || s == OrderState.Accepted || s == OrderState.TriggerPending
				|| s == OrderState.Working || s == OrderState.ChangePending || s == OrderState.ChangeSubmitted || s == OrderState.PartFilled;
			lock (atmLock)
			{
				if (isTp)
				{
					if (working) { atmTpOrder = order; atmTpPrice = order.LimitPrice; atmTpQty = Math.Max(0, order.Quantity - order.Filled); }
					else if (atmTpOrder == null || atmTpOrder == order) { atmTpOrder = null; atmTpQty = 0; }
				}
				else
				{
					if (working) { atmSlOrder = order; atmSlPrice = order.StopPrice; atmSlQty = Math.Max(0, order.Quantity - order.Filled); }
					else if (atmSlOrder == null || atmSlOrder == order) { atmSlOrder = null; atmSlQty = 0; }
				}
			}
		}

		private void ClearAtmOrders()
		{
			lock (atmLock) { atmTpOrder = atmSlOrder = null; atmTpQty = atmSlQty = 0; atmTpPrice = atmSlPrice = double.NaN; }
		}

		private void DrawEntryPriceMarker(int dir, double avgEntry, DateTime fillTime, string signal)
		{
			if (!EnableEntryPriceMarker || ChartControl == null || avgEntry <= 0) return;
			int barsAgo = 0;
			try
			{
				int absolute = BarsArray[0].GetBar(fillTime);
				if (absolute >= 0 && CurrentBars[0] >= absolute) barsAgo = Math.Max(0, CurrentBars[0] - absolute);
			}
			catch { barsAgo = 0; }
			string baseTag = "SC_ENTRY_" + signal;
			double tk = TickSize > 0 ? TickSize : 0.25;
			if (dir > 0) Draw.ArrowUp(this, baseTag + "_ARROW", false, barsAgo, avgEntry - 2 * tk, Brushes.LimeGreen);
			else Draw.ArrowDown(this, baseTag + "_ARROW", false, barsAgo, avgEntry + 2 * tk, Brushes.OrangeRed);
			// PRICE ONLY (as in HJ): no pattern label on the entry candle
			Draw.Text(this, baseTag + "_PRICE", avgEntry.ToString("0.00", CultureInfo.InvariantCulture), barsAgo, avgEntry, Brushes.White);
		}

		private double AtmUnrealizedPoints(bool isLong, double avgEntry)
		{
			if (avgEntry <= 0) return 0.0;
			double bid = atmBid, ask = atmAsk;
			double mark = isLong ? bid : ask;
			if (!(mark > 0) || (bid > 0 && ask > 0 && bid >= ask)) mark = atmLastPrice;
			if (!(mark > 0)) return 0.0;
			return isLong ? mark - avgEntry : avgEntry - mark;
		}

		private static string FormatAtmPnl(double pnl)
		{
			string sign = pnl > 0 ? "+" : (pnl < 0 ? "-" : "");
			return sign + "$" + Math.Abs(pnl).ToString("0.00", CultureInfo.InvariantCulture);
		}

		private string AtmPnlText(bool isLong, double avgEntry, int remaining, out double pnlSign)
		{
			double pts = AtmUnrealizedPoints(isLong, avgEntry);
			pnlSign = pts;
			double tick = TickSize > 0 ? TickSize : 0.25;
			switch (AtmPnlDisplay)
			{
				case JeronAtmPnlDisplayMode.Points:
					return pts.ToString("0.00", CultureInfo.InvariantCulture);
				case JeronAtmPnlDisplayMode.Ticks:
					return (pts / tick).ToString("+0;-0;0", CultureInfo.InvariantCulture) + " t";
				default:
					return FormatAtmPnl(pts * Instrument.MasterInstrument.PointValue * remaining);
			}
		}

		private void RenderAtmTradeLines(ChartControl chartControl, ChartScale chartScale)
		{
			if (!EnableTradeLines || RenderTarget == null || chartScale == null || ChartPanel == null || Position == null) return;
			MarketPosition mp = Position.MarketPosition;
			int remaining = Position.Quantity;
			double avgEntry = Position.AveragePrice;
			if (mp == MarketPosition.Flat || remaining <= 0 || avgEntry <= 0) return;
			bool isLong = mp == MarketPosition.Long;

			double tpPrice, slPrice;
			int tpQty, slQty;
			lock (atmLock) { tpPrice = atmTpPrice; slPrice = atmSlPrice; tpQty = atmTpQty; slQty = atmSlQty; }
			Candidate lc = liveCand;
			if (double.IsNaN(tpPrice) && lc != null && lc.Target > 0) tpPrice = lc.Target;   // before the target order is accepted
			if (double.IsNaN(slPrice) && lc != null) slPrice = lc.Stop;
			if (tpQty <= 0) tpQty = remaining;
			if (slQty <= 0) slQty = remaining;

			float left = ChartPanel.X, right = ChartPanel.X + ChartPanel.W;
			float top = ChartPanel.Y, bottom = ChartPanel.Y + ChartPanel.H;
			// tag tips and the entry box share one x position, like the native ATM layout
			float labelRight = Math.Max(left + 130f, right - AtmLabelOffsetPixels);

			SharpDX.Direct2D1.AntialiasMode oldAa = RenderTarget.AntialiasMode;
			List<IDisposable> res = new List<IDisposable>();
			try
			{
				SharpDX.DirectWrite.TextFormat fmt = new SharpDX.DirectWrite.TextFormat(NinjaTrader.Core.Globals.DirectWriteFactory, "Segoe UI",
					SharpDX.DirectWrite.FontWeight.SemiBold, SharpDX.DirectWrite.FontStyle.Normal, 11f);
				res.Add(fmt);
				Func<float, float, float, SharpDX.Direct2D1.SolidColorBrush> brush = (r, g, b) =>
				{
					SharpDX.Direct2D1.SolidColorBrush x = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(r, g, b, 1f));
					res.Add(x);
					return x;
				};
				SharpDX.Direct2D1.SolidColorBrush green = brush(0.20f, 0.80f, 0.20f);
				SharpDX.Direct2D1.SolidColorBrush red = brush(0.93f, 0.11f, 0.14f);
				SharpDX.Direct2D1.SolidColorBrush tan = brush(0.96f, 0.87f, 0.70f);
				SharpDX.Direct2D1.SolidColorBrush black = brush(0f, 0f, 0f);
				SharpDX.Direct2D1.SolidColorBrush white = brush(1f, 1f, 1f);
				SharpDX.Direct2D1.SolidColorBrush dark = brush(0.13f, 0.13f, 0.13f);
				SharpDX.Direct2D1.SolidColorBrush grey = brush(0.75f, 0.75f, 0.75f);

				// ENTRY: tan line, [PnL | qty] box
				float yEntry = AtmY(chartScale, avgEntry);
				if (AtmOnPanel(yEntry, top, bottom))
				{
					RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;
					RenderTarget.DrawLine(new SharpDX.Vector2(left, yEntry), new SharpDX.Vector2(right, yEntry), tan, 1f);
					RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.PerPrimitive;
					double pnlSign;
					string pnl = AtmPnlText(isLong, avgEntry, remaining, out pnlSign);
					string q = remaining.ToString(CultureInfo.InvariantCulture);
					float pnlW = Math.Max(56f, AtmTextWidth(pnl, fmt) + 14f);
					float qW = Math.Max(20f, AtmTextWidth(q, fmt) + 10f);
					float bt = yEntry - AtmRowHeight / 2f;
					SharpDX.RectangleF pnlRect = new SharpDX.RectangleF(labelRight, bt, pnlW, AtmRowHeight);
					SharpDX.RectangleF qRect = new SharpDX.RectangleF(labelRight + pnlW, bt, qW, AtmRowHeight);
					RenderTarget.FillRectangle(pnlRect, dark);
					RenderTarget.DrawRectangle(pnlRect, grey, 1f);
					RenderTarget.FillRectangle(qRect, isLong ? green : red);
					RenderTarget.DrawRectangle(qRect, grey, 1f);
					AtmDrawText(pnl, fmt, pnlRect, pnlSign > 0 ? green : (pnlSign < 0 ? red : white), true);
					AtmDrawText(q, fmt, qRect, isLong ? black : white, true);
				}

				// TP: green line, "qty TP" tag
				if (!double.IsNaN(tpPrice) && tpPrice > 0)
				{
					float y = AtmY(chartScale, tpPrice);
					if (AtmOnPanel(y, top, bottom))
					{
						RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;
						RenderTarget.DrawLine(new SharpDX.Vector2(left, y), new SharpDX.Vector2(right, y), green, 1f);
						RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.PerPrimitive;
						AtmDrawTag(labelRight, y, tpQty.ToString(CultureInfo.InvariantCulture) + " TP", fmt, green, black);
					}
				}

				// STP: red line, "qty STP" tag
				if (!double.IsNaN(slPrice) && slPrice > 0)
				{
					float y = AtmY(chartScale, slPrice);
					if (AtmOnPanel(y, top, bottom))
					{
						RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;
						RenderTarget.DrawLine(new SharpDX.Vector2(left, y), new SharpDX.Vector2(right, y), red, 1f);
						RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.PerPrimitive;
						AtmDrawTag(labelRight, y, slQty.ToString(CultureInfo.InvariantCulture) + " STP", fmt, red, white);
					}
				}
			}
			catch { }
			finally
			{
				for (int i = res.Count - 1; i >= 0; i--) { try { res[i].Dispose(); } catch { } }
				RenderTarget.AntialiasMode = oldAa;
			}
		}

		private float AtmY(ChartScale scale, double price)
		{
			return (float)scale.GetYByValue(price) + 0.5f;   // +0.5 keeps a 1 px line crisp on the pixel grid
		}

		private bool AtmOnPanel(float y, float top, float bottom)
		{
			return !float.IsNaN(y) && y >= top && y <= bottom;
		}

		private float AtmTextWidth(string s, SharpDX.DirectWrite.TextFormat f)
		{
			using (SharpDX.DirectWrite.TextLayout l = new SharpDX.DirectWrite.TextLayout(NinjaTrader.Core.Globals.DirectWriteFactory, s ?? "", f, 1000f, AtmRowHeight))
				return l.Metrics.Width;
		}

		private void AtmDrawText(string s, SharpDX.DirectWrite.TextFormat f, SharpDX.RectangleF r, SharpDX.Direct2D1.Brush b, bool center)
		{
			using (SharpDX.DirectWrite.TextLayout l = new SharpDX.DirectWrite.TextLayout(NinjaTrader.Core.Globals.DirectWriteFactory, s ?? "", f, 1000f, r.Height))
			{
				float w = l.Metrics.Width, h = l.Metrics.Height;
				float x = center ? r.Left + (r.Width - w) / 2f : r.Left + 6f;
				float y = r.Top + (r.Height - h) / 2f;
				RenderTarget.DrawTextLayout(new SharpDX.Vector2(x, y), l, b);
			}
		}

		// native-ATM style tag: rectangle body with an arrow tip pointing right, tip ending at rightTip
		private SharpDX.RectangleF AtmDrawTag(float rightTip, float cy, string text, SharpDX.DirectWrite.TextFormat f,
			SharpDX.Direct2D1.Brush fill, SharpDX.Direct2D1.Brush fg)
		{
			float h = AtmRowHeight;
			float w = Math.Max(40f, AtmTextWidth(text, f) + 14f);
			float left = rightTip - AtmTagTipWidth - w, top = cy - h / 2f, bottom = cy + h / 2f, bodyRight = left + w;
			using (SharpDX.Direct2D1.PathGeometry g = new SharpDX.Direct2D1.PathGeometry(NinjaTrader.Core.Globals.D2DFactory))
			{
				using (SharpDX.Direct2D1.GeometrySink sink = g.Open())
				{
					sink.BeginFigure(new SharpDX.Vector2(left, top), SharpDX.Direct2D1.FigureBegin.Filled);
					sink.AddLine(new SharpDX.Vector2(bodyRight, top));
					sink.AddLine(new SharpDX.Vector2(rightTip, cy));
					sink.AddLine(new SharpDX.Vector2(bodyRight, bottom));
					sink.AddLine(new SharpDX.Vector2(left, bottom));
					sink.EndFigure(SharpDX.Direct2D1.FigureEnd.Closed);
					sink.Close();
				}
				RenderTarget.FillGeometry(g, fill);
			}
			AtmDrawText(text, f, new SharpDX.RectangleF(left, top, w, h), fg, false);
			return new SharpDX.RectangleF(left, top, w + AtmTagTipWidth, h);
		}

		// ==============================================================================
		//  Logging helpers
		// ==============================================================================
		private Dictionary<string, string> NewRow(string recordType)
		{
			Dictionary<string, string> row = new Dictionary<string, string>();
			row["RecordType"] = recordType;
			row["Mode"] = State == State.Historical ? "HIST" : "RT";
			row["Instrument"] = instrumentName;
			row["FootprintSource"] = useVolumetric ? "Volumetric" : "InternalTicks";
			row["LargeMethod"] = AggressionMethod.ToString();
			return row;
		}

		private Dictionary<string, string> ZoneRow(string recordType, TrackedZone z, BarEvidence ev)
		{
			Dictionary<string, string> row = NewRow(recordType);
			row["EventId"] = z.CandidateId;
			row["EvidenceTimeLocal"] = JeronFmt.T(ev.TimeLocal);
			row["EvidenceTimeCT"] = JeronFmt.T(ev.TimeCt);
			row["ProcessedTimeLocal"] = CurrentBar >= 0 ? JeronFmt.T(Time[0]) : "";
			row["Session"] = ev.Session.ToString();
			row["LocationId"] = z.Id;
			row["LocationType"] = z.IsFrozen ? "FROZEN_PREOPEN (as-of " + z.AsOfText + ")" : "DEVELOPING_" + z.LocType;
			row["ZoneLo"] = JeronFmt.P(z.Lo);
			row["ZoneHi"] = JeronFmt.P(z.Hi);
			row["Price"] = JeronFmt.P(ev.C);
			row["NearestBoundary"] = JeronFmt.P(Math.Abs(ev.C - z.Hi) <= Math.Abs(ev.C - z.Lo) ? z.Hi : z.Lo);
			row["VWAP"] = JeronFmt.P(ev.Vwap);
			return row;
		}

		private void FillEvidence(Dictionary<string, string> row, BarEvidence ev)
		{
			if (!row.ContainsKey("EvidenceTimeLocal"))
			{
				row["EvidenceTimeLocal"] = JeronFmt.T(ev.TimeLocal);
				row["EvidenceTimeCT"] = JeronFmt.T(ev.TimeCt);
				row["Session"] = ev.Session.ToString();
				row["VWAP"] = JeronFmt.P(ev.Vwap);
			}
			row["BarVolume"] = JeronFmt.I(ev.Vol);
			row["BuyVol"] = JeronFmt.I(ev.BuyVol);
			row["SellVol"] = JeronFmt.I(ev.SellVol);
			row["Delta"] = JeronFmt.I(ev.Delta);
			row["DeltaPct"] = JeronFmt.N(ev.DeltaPct, 1);
			row["BuyImb"] = ev.BuyImb.ToString(CultureInfo.InvariantCulture);
			row["SellImb"] = ev.SellImb.ToString(CultureInfo.InvariantCulture);
			row["StrongBuyImb"] = ev.StrongBuyImb.ToString(CultureInfo.InvariantCulture);
			row["StrongSellImb"] = ev.StrongSellImb.ToString(CultureInfo.InvariantCulture);
			row["MaxBuyStack"] = ev.MaxBuyStack.ToString(CultureInfo.InvariantCulture);
			row["MaxSellStack"] = ev.MaxSellStack.ToString(CultureInfo.InvariantCulture);
			row["ZeroDenCells"] = ev.ZeroDenCells.ToString(CultureInfo.InvariantCulture);
			row["LargeBuy"] = JeronFmt.I(ev.LargeBuy);
			row["LargeSell"] = JeronFmt.I(ev.LargeSell);
			row["FootprintSource"] = ev.Source;
		}

		private void Write(Dictionary<string, string> row)
		{
			if (logger != null) logger.Write(row);
		}

		private void ParseFrozenZones()
		{
			frozenDefs.Clear();
			if (string.IsNullOrWhiteSpace(FrozenZones)) return;
			foreach (string raw in FrozenZones.Split(new char[] { ';', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries))
			{
				string entry = raw.Trim();
				if (entry.Length == 0) continue;
				FrozenDef def = new FrozenDef();
				int at = entry.IndexOf('@');
				if (at > 0)
				{
					DateTime d;
					if (DateTime.TryParseExact(entry.Substring(0, at).Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d))
					{
						def.HasDate = true;
						def.Date = d.Date;
					}
					entry = entry.Substring(at + 1).Trim();
				}
				string label = "ZONE";
				int colon = entry.IndexOf(':');
				if (colon > 0)
				{
					label = JeronFmt.SafeFileToken(entry.Substring(colon + 1).Trim().ToUpperInvariant());
					entry = entry.Substring(0, colon).Trim();
				}
				string[] bounds = entry.Split('-');
				double a, b;
				if (bounds.Length != 2
					|| !double.TryParse(bounds[0].Replace(",", "").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out a)
					|| !double.TryParse(bounds[1].Replace(",", "").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out b))
				{
					Print("JeronOrderFlowEventTracker: could not parse zone '" + raw + "'");
					continue;
				}
				def.Lo = Math.Min(a, b);
				def.Hi = Math.Max(a, b);
				def.Label = label;
				frozenDefs.Add(def);
			}
		}

		private string BuildStatus()
		{
			int frozenActive = 0, intradayActive = 0;
			lock (zLock)
			{
				foreach (TrackedZone z in zones)
				{
					if (!z.Active) continue;
					if (z.IsFrozen) { if (z.StartBar >= 0) frozenActive++; }
					else intradayActive++;
				}
			}
			StringBuilder sb = new StringBuilder();
			sb.Append("Jeron Order Flow Event Tracker  |  Footprint: ").Append(useVolumetric ? "Volumetric" : "Internal ticks");
			sb.Append("  |  Large trades: ").Append(AggressionMethod.ToString()).AppendLine();
			sb.Append("Zones  frozen active: ").Append(frozenActive.ToString(CultureInfo.InvariantCulture));
			sb.Append("  intraday active: ").Append(intradayActive.ToString(CultureInfo.InvariantCulture));
			sb.Append("  |  Candidates  Q: ").Append(JeronFmt.I(countQualified));
			sb.Append("  R: ").Append(JeronFmt.I(countRejected));
			sb.Append("  P: ").Append(JeronFmt.I(countPending)).AppendLine();
			if (engine != null)
			{
				sb.Append("Data: trades ").Append(JeronFmt.I(engine.TradeCount));
				sb.Append("  no-quote ").Append(JeronFmt.I(engine.MissingQuoteCount));
				sb.Append("  large clusters ").Append(JeronFmt.I(engine.EventCounts[0] + engine.EventCounts[1] + engine.EventCounts[2]));
				if (engine.TradeCount > 200 && engine.MissingQuoteCount * 2 > engine.TradeCount)
					sb.Append("  WARNING: most trades have no bid/ask - use Market Replay data");
				else if (engine.TradeCount == 0 && State == State.Realtime)
					sb.Append("  WARNING: no trade ticks received");
				sb.AppendLine();
			}
			if (UseSetupFamilies)
			{
				sb.Append("Valid events: ").Append(JeronFmt.I(countEvents)).Append("  A+: ").Append(JeronFmt.I(countAplus));
				sb.Append("  Responses confirmed: ").Append(JeronFmt.I(countConfirmed)).Append("  Exit warnings: ").Append(JeronFmt.I(countWarn));
				if (effectiveContext != JeronContextBias.None) sb.Append("  Context: ").Append(effectiveContext.ToString());
				sb.AppendLine();
				sb.Append("v2.2  late triggers: ").Append(JeronFmt.I(countLateTriggers));
				sb.Append("  duplicates merged: ").Append(JeronFmt.I(countDuplicates));
				sb.Append("  power zone merges: ").Append(JeronFmt.I(countPowerMerges));
				sb.Append("  targets beyond nearest: ").Append(JeronFmt.I(countTargetSkips)).AppendLine();
				sb.Append("v2.5 research  shadows: ").Append(JeronFmt.I(countShadows));
				sb.Append("  retest rows: ").Append(JeronFmt.I(countRetestRows));
				sb.Append("  retest entries: ").Append(JeronFmt.I(countRetestEntered));
				sb.Append("  open at session end: ").Append(JeronFmt.I(countSessionEnd)).AppendLine();
				sb.Append("v2.6 order-flow retest  entries: ").Append(JeronFmt.I(countRetestV2Entered));
				sb.Append("  reversal candidates: ").Append(JeronFmt.I(countReversals));
				if (plan != null) sb.Append("  balance: ").Append(double.IsNaN(plan.BalanceLo) ? "not in plan" : JeronFmt.P(plan.BalanceLo) + "-" + JeronFmt.P(plan.BalanceHi));
				sb.AppendLine();
				if (LogResearchRules || LogExitModels)
				{
					int open = 0;
					foreach (RWatch w in watches) if (w.Phase < 4) open++;
					sb.Append("v2.10 research rules ").Append(ResearchRulesVersion).Append("  signals: ").Append(JeronFmt.I(countResearchSignals));
					sb.Append("  no-entry: ").Append(JeronFmt.I(countResearchNoEntry)).Append("  open: ").Append(open.ToString(CultureInfo.InvariantCulture));
					sb.Append("  exit-model rows: ").Append(JeronFmt.I(countExitRows)).AppendLine();
				}
			}
			if (Bars != null && !Bars.IsTickReplay)
			{
				if (!useVolumetric) sb.AppendLine("WARNING: Tick Replay OFF and chart not Volumetric - no historical footprint evidence.");
				else sb.AppendLine("Note: Tick Replay OFF - historical large-trade (Power/Deep) evidence unavailable; imbalances OK.");
			}
			sb.AppendLine(AutoStatusText());   // S1.0
			if (UsePreopenPlan)
			{
				if (plan != null)
				{
					int pd = 0, pt = 0;
					foreach (PlanZone pz in plan.Zones) { if (pz.TargetOnly) pt++; else pd++; }
					sb.Append("Plan ").Append(plan.Id.Length > 0 ? plan.Id : plan.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))
						.Append(planActive ? " ACTIVE" : " waiting for " + planActiveCt.ToString("HH:mm", CultureInfo.InvariantCulture) + " CT")
						.Append("  context ").Append(effectiveContext.ToString()).Append(planInvalidated ? " (invalidated)" : "")
						.Append("  decision ").Append(pd.ToString(CultureInfo.InvariantCulture)).Append(" / target ").Append(pt.ToString(CultureInfo.InvariantCulture))
						.Append("  lava ").Append(plan.Lava.Count.ToString(CultureInfo.InvariantCulture))
						.Append("  ES ").Append(esIdx > 0 ? (double.IsNaN(esClose) ? "no data" : JeronFmt.P(esClose)) : "off")
						.Append("  plan blocks ").Append(JeronFmt.I(countPlanBlocks)).AppendLine();
				}
				else sb.Append("Plan: none for ").Append(tradingDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture)).Append(" in ").Append(PlanFolderPath())
					.Append(planGaveUp ? "  (stopped looking at session end)" : "  (checking every bar)")
					.Append(RequirePlanForEntries ? "  ENTRIES BLOCKED (NO_PLAN): " + JeronFmt.I(countNoPlan) : "")
					.AppendLine(planError.Length > 0 ? "  (" + planError + ")" : "");
			}
			if (frozenDefs.Count == 0 && plan == null) sb.AppendLine("No frozen zones entered (Locations > Frozen zones).");
			if (logger != null) sb.Append("Log: ").Append(logger.FilePath);
			else if (ExportEventLog) sb.Append("Log FAILED: ").Append(logError);
			return sb.ToString();
		}

		// ==============================================================================
		//  Drawing
		// ==============================================================================
		private void DrawLabel(TrackedZone z, string text, int d, bool rejected, int idx, BarEvidence ev)
		{
			if (!ShowLabels) return;
			if (!z.IsFrozen && !ShowIntradayLabels) return;
			if (rejected && !ShowRejectedLabels) return;
			int ba = CurrentBar - idx;
			if (ba < 0 || ba > CurrentBar) return;

			if (labelBar != idx) { labelBar = idx; labelStack = 0; }
			labelStack++;

			Brush brush = rejected ? Brushes.Gray : (text == "WATCH" ? Brushes.Gold : (text == "FAILED" ? Brushes.Orange : (d > 0 ? Brushes.LimeGreen : Brushes.Tomato)));
			bool above = d >= 0;
			double y = above ? ev.H : ev.L;
			int offset = (above ? 1 : -1) * (10 + 14 * (labelStack - 1));
			string shown = text + (z.IsFrozen ? " " + z.Id : "") + (rejected ? " (rej)" : "");
			Draw.Text(this, "JOFT_" + z.Id + "_" + idx.ToString(CultureInfo.InvariantCulture) + "_" + text.Replace(" ", ""), false, shown,
				ba, y, offset, brush, labelFont, TextAlignment.Center, Brushes.Transparent, Brushes.Transparent, 0);
		}

		public override void OnRenderTargetChanged()
		{
			DisposeDx();
			if (RenderTarget == null) return;
			try
			{
				float op = (float)(ZoneOpacity / 100.0);
				dxFrozen = FrozenZoneBrush.ToDxBrush(RenderTarget); dxFrozen.Opacity = op;
				dxBuyZone = BuyZoneBrush.ToDxBrush(RenderTarget); dxBuyZone.Opacity = op;
				dxSellZone = SellZoneBrush.ToDxBrush(RenderTarget); dxSellZone.Opacity = op;
				float pop = (float)Math.Min(1.0, op * 1.6);
				dxPowerBuyZone = PowerBuyZoneBrush.ToDxBrush(RenderTarget); dxPowerBuyZone.Opacity = pop;
				dxPowerSellZone = PowerSellZoneBrush.ToDxBrush(RenderTarget); dxPowerSellZone.Opacity = pop;
				dxPowerBuyEdge = PowerBuyZoneBrush.ToDxBrush(RenderTarget);
				dxPowerSellEdge = PowerSellZoneBrush.ToDxBrush(RenderTarget);
				dxUp = Brushes.LimeGreen.ToDxBrush(RenderTarget);
				dxDown = Brushes.Tomato.ToDxBrush(RenderTarget);
				dxNeutral = Brushes.SlateGray.ToDxBrush(RenderTarget);
				dxText = Brushes.Gainsboro.ToDxBrush(RenderTarget);
			}
			catch { DisposeDx(); }
		}

		private void DisposeDx()
		{
			if (dxFrozen != null) { dxFrozen.Dispose(); dxFrozen = null; }
			if (dxBuyZone != null) { dxBuyZone.Dispose(); dxBuyZone = null; }
			if (dxSellZone != null) { dxSellZone.Dispose(); dxSellZone = null; }
			if (dxPowerBuyZone != null) { dxPowerBuyZone.Dispose(); dxPowerBuyZone = null; }
			if (dxPowerSellZone != null) { dxPowerSellZone.Dispose(); dxPowerSellZone = null; }
			if (dxPowerBuyEdge != null) { dxPowerBuyEdge.Dispose(); dxPowerBuyEdge = null; }
			if (dxPowerSellEdge != null) { dxPowerSellEdge.Dispose(); dxPowerSellEdge = null; }
			if (dxUp != null) { dxUp.Dispose(); dxUp = null; }
			if (dxDown != null) { dxDown.Dispose(); dxDown = null; }
			if (dxNeutral != null) { dxNeutral.Dispose(); dxNeutral = null; }
			if (dxText != null) { dxText.Dispose(); dxText = null; }
		}

		protected override void OnRender(ChartControl chartControl, ChartScale chartScale)
		{
			base.OnRender(chartControl, chartScale);
			try { RenderTrackerZones(chartControl, chartScale); } catch { }   // tracker v2.11 zones, unchanged
			RenderAtmTradeLines(chartControl, chartScale);                // S1.1 HJ trade lines
		}

		private void RenderTrackerZones(ChartControl chartControl, ChartScale chartScale)
		{
			if (Bars == null || ChartBars == null || RenderTarget == null || dxFrozen == null) return;

			TrackedZone[] snapshot;
			lock (zLock) snapshot = zones.ToArray();
			if (snapshot.Length == 0) return;

			int fromIdx = ChartBars.FromIndex;
			int toIdx = ChartBars.ToIndex;
			// half the pixel spacing between two adjacent bars (avoids version-specific ChartControl properties)
			float halfBar = 4f;
			if (toIdx >= 1)
				halfBar = Math.Abs(chartControl.GetXByBarIndex(ChartBars, toIdx) - chartControl.GetXByBarIndex(ChartBars, toIdx - 1)) / 2f;
			float rightEdge = ChartPanel.X + ChartPanel.W;
			SharpDX.DirectWrite.TextFormat format = null;
			try
			{
				format = new SharpDX.DirectWrite.TextFormat(NinjaTrader.Core.Globals.DirectWriteFactory, "Arial", 10f);
				foreach (TrackedZone z in snapshot)
				{
					if (z.StartBar < 0) continue;
					if (z.IsFrozen ? !ShowFrozenZones : !ShowIntradayZones) continue;
					int endIdx = z.EndBar >= 0 ? z.EndBar : toIdx;
					if (endIdx < fromIdx || z.StartBar > toIdx) continue;

					float x1 = z.StartBar < fromIdx ? ChartPanel.X : chartControl.GetXByBarIndex(ChartBars, z.StartBar) - halfBar;
					float x2 = z.EndBar < 0 ? rightEdge : chartControl.GetXByBarIndex(ChartBars, Math.Min(z.EndBar, toIdx)) + halfBar;
					float yTop = chartScale.GetYByValue(z.Hi + tickSize / 2.0);
					float yBot = chartScale.GetYByValue(z.Lo - tickSize / 2.0);
					if (x2 <= x1) continue;
					SharpDX.RectangleF rect = new SharpDX.RectangleF(x1, yTop, x2 - x1, Math.Max(1f, yBot - yTop));

					SharpDX.Direct2D1.Brush fill;
					if (z.IsFrozen) fill = dxFrozen;
					else if (z.IsPower) fill = z.OriginDir > 0 ? dxPowerBuyZone : dxPowerSellZone;
					else fill = z.OriginDir > 0 ? dxBuyZone : dxSellZone;
					RenderTarget.FillRectangle(rect, fill);

					SharpDX.Direct2D1.Brush border = z.IsPower ? (z.OriginDir > 0 ? dxPowerBuyEdge : dxPowerSellEdge) : dxNeutral;
					if (z.State == ZState.Initiation || z.State == ZState.Response || z.State == ZState.Accepted)
						border = z.Dir > 0 ? dxUp : dxDown;
					RenderTarget.DrawRectangle(rect, border, z.IsFrozen || z.IsPower ? 1.5f : 1f);

					if (z.IsPower && ShowPowerZoneTags)
					{
						string tag = (z.OriginDir > 0 ? "PWR BUY " : "PWR SELL ") + JeronFmt.I(z.PowerVolume);
						using (SharpDX.DirectWrite.TextLayout layout = new SharpDX.DirectWrite.TextLayout(NinjaTrader.Core.Globals.DirectWriteFactory, tag, format, 200f, 20f))
						{
							float tx = Math.Max(x1, ChartPanel.X) + 4f;
							float ty = z.OriginDir > 0 ? yBot + 1f : yTop - layout.Metrics.Height - 1f;
							RenderTarget.DrawTextLayout(new SharpDX.Vector2(tx, ty), layout, z.OriginDir > 0 ? dxPowerBuyEdge : dxPowerSellEdge);
						}
					}

					if (z.IsFrozen)
					{
						string text = z.Id + "  [" + z.State.ToString().ToUpperInvariant() + (z.Dir != 0 ? (z.Dir > 0 ? " UP" : " DOWN") : "") + "]";
						using (SharpDX.DirectWrite.TextLayout layout = new SharpDX.DirectWrite.TextLayout(NinjaTrader.Core.Globals.DirectWriteFactory, text, format, 400f, 20f))
						{
							float tx = Math.Max(x1, ChartPanel.X) + 4f;
							RenderTarget.DrawTextLayout(new SharpDX.Vector2(tx, yTop + 1f), layout, dxText);
						}
					}
				}
			}
			catch { }
			finally
			{
				if (format != null) format.Dispose();
			}
		}

		// ==============================================================================
		//  Properties
		// ==============================================================================
		#region Properties
		// ---- 1. Locations ----
		[Display(Name = "Frozen zones", Description = "Format: [yyyy-MM-dd@]low-high:LABEL; ...  e.g. yyyy-MM-dd@low-high:LABEL. Fallback only; a PreopenPlan file for the date replaces these. Entries without a date use 'Zones date'.", Order = 1, GroupName = "1. Locations")]
		public string FrozenZones { get; set; }

		[Display(Name = "Zones date (yyyy-MM-dd, blank = every day)", Description = "Applies only to entries without their own date.", Order = 2, GroupName = "1. Locations")]
		public string ZonesDate { get; set; }

		[Display(Name = "Zones as-of time (CT, HH:mm)", Description = "When the levels were frozen. Bars starting before this time never test the zones. Blank = from session start.", Order = 3, GroupName = "1. Locations")]
		public string ZonesAsOfCT { get; set; }

		// ---- 1b. Pre-open plan (v2.3) ----
		[Display(Name = "Use pre-open plan file", Description = "Reads PreopenPlan_<date>.txt (written by Claude from the JeronPreopenMap packet) for each trading date.", Order = 1, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool UsePreopenPlan { get; set; }

		[Display(Name = "Plan folder (blank = Drive Preopen Exchange\\Pre-open Plan)", Description = "Point this at the Google Drive for desktop folder Claude writes plans to.", Order = 2, GroupName = "1b. Pre-open plan (v2.3)")]
		public string PlanFolder { get; set; }

		[Display(Name = "Plan zones replace Frozen zones", Order = 3, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool PlanReplacesFrozenZones { get; set; }

		[Display(Name = "Enforce plan side rules", Description = "Off = PLAN_* reasons are logged as flags only (for A/B comparison).", Order = 4, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool EnforcePlanRules { get; set; }

		[Display(Name = "No entries in 'middle is lava' bands", Order = 5, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool RejectInLava { get; set; }

		[Display(Name = "ES gate (adds ES 1-minute series)", Order = 6, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool UseEsGate { get; set; }

		[Display(Name = "ES gate blocks entries (v2.11)", Description = "OFF (default) = the ES gate is logged only: a failed gate adds the flag ES_GATE_FAIL_LOGGED and the es_* columns, not the reason ES_GATE_FAIL. ON = v2.10 behaviour (ES_GATE_FAIL blocks the entry).", Order = 12, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool EsGateBlocksEntries { get; set; }

		[Display(Name = "ES contract", Description = "Update at the roll, e.g. ES 03-27.", Order = 7, GroupName = "1b. Pre-open plan (v2.3)")]
		public string EsInstrument { get; set; }

		[Display(Name = "Frozen labels starting T_ are targets only", Description = "JeronPreopenMap v2.0 marks single-source zones T_.", Order = 8, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool TargetPrefixIsTargetOnly { get; set; }

		[Display(Name = "Counter-context: first target only (v2.4)", Description = "Jeron Part 2 ~1:24:00: against the context, target VWAP / POC / value edge, not the far side. No min-R:R search past nearer levels.", Order = 9, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool CounterContextFirstTarget { get; set; }

		[Display(Name = "Entries need a plan (v2.7)", Description = "Until a PreopenPlan for the date is ACTIVE, every candidate is EventOnly with reason NO_PLAN. Events, outcomes and research rows are still logged.", Order = 10, GroupName = "1b. Pre-open plan (v2.3)")]
		public bool RequirePlanForEntries { get; set; }

		[Display(Name = "Plan deadline (CT, HH:mm)", Description = "If no plan is active by this time, one PLAN_MISSING row is logged. Blank = no warning.", Order = 11, GroupName = "1b. Pre-open plan (v2.3)")]
		public string PlanDeadlineCT { get; set; }

		// ---- 9. Level 2 (v2.8) ----
		[Display(Name = "Capture Level 2 (market depth)", Description = "Keeps the order book and adds an L2 snapshot to every candidate and retest entry. Needs a Level 2 feed live, or Playback with recorded Level 2.", Order = 1, GroupName = "9. Level 2 (v2.8)")]
		public bool CaptureL2 { get; set; }

		[Display(Name = "Record every L2 update to CSV", Description = "One file per hour, written locally and moved to the L2 folder when complete.", Order = 2, GroupName = "9. Level 2 (v2.8)")]
		public bool RecordAllL2Updates { get; set; }

		[Display(Name = "L2 log folder (blank = Drive Preopen Exchange\\logs\\L2)", Order = 3, GroupName = "9. Level 2 (v2.8)")]
		public string L2Folder { get; set; }

		[Range(1, 20)]
		[Display(Name = "Book levels per side", Order = 4, GroupName = "9. Level 2 (v2.8)")]
		public int L2BookLevels { get; set; }

		[Range(1, 100000)]
		[Display(Name = "Minimum depth updates before a snapshot counts", Order = 5, GroupName = "9. Level 2 (v2.8)")]
		public int L2MinUpdates { get; set; }

		[Range(1, 600)]
		[Display(Name = "Max depth age (seconds)", Order = 6, GroupName = "9. Level 2 (v2.8)")]
		public int L2MaxAgeSeconds { get; set; }

		[Range(0.5, 0.99)]
		[Display(Name = "Book imbalance threshold (bid share for longs)", Description = "Research setting, not a Jeron rule. 0.60 = longs need 60%+ of top-N size on the bid; shorts 60%+ on the ask.", Order = 7, GroupName = "9. Level 2 (v2.8)")]
		public double L2ImbalanceThreshold { get; set; }

		[Display(Name = "Require L2 alignment for entries", Description = "Off = L2 is only recorded and flagged. On = candidates without an aligned, fresh book are EventOnly (L2_NOT_ALIGNED, L2_DEPTH_STALE, L2_HISTORICAL_NO_L2...).", Order = 8, GroupName = "9. Level 2 (v2.8)")]
		public bool RequireL2Alignment { get; set; }

		// ---- 2. Footprint ----
		[Display(Name = "Footprint source", Description = "Auto = read the Volumetric chart if present, else build from ticks (needs Tick Replay for history).", Order = 1, GroupName = "2. Footprint")]
		public JeronFootprintSource FootprintSource { get; set; }

		[Range(100, 10000)]
		[Display(Name = "Imbalance ratio (%)", Description = "Jeron NY setting: 400%.", Order = 2, GroupName = "2. Footprint")]
		public double ImbalanceRatioPct { get; set; }

		[Range(100, 10000)]
		[Display(Name = "Strong imbalance ratio (%)", Description = "Jeron NY strong tier: 900%.", Order = 3, GroupName = "2. Footprint")]
		public double StrongImbalanceRatioPct { get; set; }

		[Display(Name = "Use lower-liquidity ratio outside NY", Description = "Optional Jeron non-NY setting.", Order = 4, GroupName = "2. Footprint")]
		public bool UseLowLiquidityRatio { get; set; }

		[Range(100, 10000)]
		[Display(Name = "Lower-liquidity ratio (%)", Description = "Jeron: 300%.", Order = 5, GroupName = "2. Footprint")]
		public double LowLiquidityRatioPct { get; set; }

		[Range(0, int.MaxValue)]
		[Display(Name = "Minimum cell volume", Description = "RESEARCH PARAMETER (Jeron gives no number). Numerator cell must reach this.", Order = 6, GroupName = "2. Footprint")]
		public int MinCellVolume { get; set; }

		[Display(Name = "Zero denominator counts as imbalance", Description = "If on, a cell vs an empty diagonal counts (flagged ZERO_DEN, never counted as the strong tier).", Order = 7, GroupName = "2. Footprint")]
		public bool ZeroDenominatorCounts { get; set; }

		[Range(1, 50)]
		[Display(Name = "Min stack for intraday zone", Description = "RESEARCH PARAMETER (Jeron gives no number).", Order = 8, GroupName = "2. Footprint")]
		public int MinStackForZone { get; set; }

		// ---- 3. Aggressive executions ----
		[Display(Name = "Aggregation method", Description = "Consistent Bid/Ask is the primary comparison method.", Order = 1, GroupName = "3. Aggressive executions")]
		public JeronMethod AggressionMethod { get; set; }

		[Range(0, int.MaxValue)]
		[Display(Name = "Deep Trade baseline", Description = "Jeron: 60.", Order = 2, GroupName = "3. Aggressive executions")]
		public int DeepTradeBaseline { get; set; }

		[Range(0, int.MaxValue)]
		[Display(Name = "Deep Trade strict", Description = "Jeron: 100.", Order = 3, GroupName = "3. Aggressive executions")]
		public int DeepTradeStrict { get; set; }

		[Display(Name = "NY Power Trade tiers", Description = "Jeron: 300,400,500.", Order = 4, GroupName = "3. Aggressive executions")]
		public string NyPowerTiers { get; set; }

		[Display(Name = "Asia/London Power Trade tiers", Description = "Jeron: 150,200.", Order = 5, GroupName = "3. Aggressive executions")]
		public string LowLiquidityPowerTiers { get; set; }

		[Range(1, int.MaxValue)]
		[Display(Name = "Large trade counts as evidence at", Description = "Aggregated size that counts as initiation evidence (default = Deep Trade baseline).", Order = 6, GroupName = "3. Aggressive executions")]
		public int LargeTradeEvidenceMin { get; set; }

		[Display(Name = "Create Power Trade zones", Description = "Clusters at or above the session's lowest Power tier become developing intraday zones.", Order = 7, GroupName = "3. Aggressive executions")]
		public bool CreatePowerTradeZones { get; set; }

		[Range(1, 60000)]
		[Display(Name = "Time cluster max gap (ms)", Description = "Used if method = TimeCluster or 'Also aggregate Power Trades by time cluster' is on. Research parameter.", Order = 8, GroupName = "3. Aggressive executions")]
		public int TimeClusterMaxGapMs { get; set; }

		[Range(0, 100)]
		[Display(Name = "Time cluster price tolerance (ticks)", Description = "Used if method = TimeCluster or 'Also aggregate Power Trades by time cluster' is on. Research parameter.", Order = 9, GroupName = "3. Aggressive executions")]
		public int TimeClusterPriceTolTicks { get; set; }

		// ---- 4. State rules ----
		[Range(0, 1000)]
		[Display(Name = "Touch tolerance (ticks)", Order = 1, GroupName = "4. State rules (research, not Jeron)")]
		public int TouchToleranceTicks { get; set; }

		[Range(0, 1000)]
		[Display(Name = "Break beyond boundary (ticks)", Description = "Close must be this far beyond the boundary to count as a break.", Order = 2, GroupName = "4. State rules (research, not Jeron)")]
		public int BreakTicks { get; set; }

		[Range(0, 10000)]
		[Display(Name = "Min displacement (ticks)", Description = "Close distance beyond the boundary required for 'reward'.", Order = 3, GroupName = "4. State rules (research, not Jeron)")]
		public int MinDisplacementTicks { get; set; }

		[Range(0, int.MaxValue)]
		[Display(Name = "Min bar delta (contracts)", Order = 4, GroupName = "4. State rules (research, not Jeron)")]
		public int MinAbsDelta { get; set; }

		[Range(0, 100)]
		[Display(Name = "Min delta %", Order = 5, GroupName = "4. State rules (research, not Jeron)")]
		public double MinDeltaPct { get; set; }

		[Display(Name = "Require imbalance or large trade", Order = 6, GroupName = "4. State rules (research, not Jeron)")]
		public bool RequireImbalanceOrLargeTrade { get; set; }

		[Range(1, 1000)]
		[Display(Name = "Acceptance closes", Description = "Consecutive closes beyond the boundary for ACCEPTED.", Order = 7, GroupName = "4. State rules (research, not Jeron)")]
		public int AcceptBars { get; set; }

		[Range(0, 100)]
		[Display(Name = "Response lookback (bars)", Description = "Bars searched for the failed attempt that precedes a RESPONSE.", Order = 8, GroupName = "4. State rules (research, not Jeron)")]
		public int ResponseLookbackBars { get; set; }

		[Range(1, 100000)]
		[Display(Name = "Re-arm distance (ticks)", Description = "After acceptance, price this far away re-arms the zone (intraday zones run through end).", Order = 9, GroupName = "4. State rules (research, not Jeron)")]
		public int RearmDistanceTicks { get; set; }

		[Display(Name = "Stop anchor", Order = 10, GroupName = "4. State rules (research, not Jeron)")]
		public JeronStopAnchorMode StopAnchorMode { get; set; }

		[Range(0, 1000)]
		[Display(Name = "Stop buffer (ticks)", Order = 11, GroupName = "4. State rules (research, not Jeron)")]
		public int StopBufferTicks { get; set; }

		[Range(0, 100)]
		[Display(Name = "Min reward:risk", Order = 12, GroupName = "4. State rules (research, not Jeron)")]
		public double MinRewardRisk { get; set; }

		[Range(0, 100000)]
		[Display(Name = "Max risk (ticks, 0 = off)", Order = 13, GroupName = "4. State rules (research, not Jeron)")]
		public int MaxRiskTicks { get; set; }

		[Display(Name = "Require VWAP alignment", Order = 14, GroupName = "4. State rules (research, not Jeron)")]
		public bool RequireVwapAlignment { get; set; }

		[Range(0, int.MaxValue)]
		[Display(Name = "Effort flag: min |delta|", Description = "With body below the next setting, flags HIGH_EFFORT_LOW_REWARD.", Order = 15, GroupName = "4. State rules (research, not Jeron)")]
		public int EffortDeltaMin { get; set; }

		[Range(0, 10000)]
		[Display(Name = "Effort flag: max body (ticks)", Order = 16, GroupName = "4. State rules (research, not Jeron)")]
		public int LowRewardTicks { get; set; }

		// ---- 4b. Entry model v2 ----
		[Display(Name = "Use setup families (Response / Initiation)", Description = "Off = original single-path qualification.", Order = 1, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool UseSetupFamilies { get; set; }

		[Display(Name = "Response: wait for confirmation bar", Description = "Jeron does not enter on the trapping Power Trade; the next bar must show the other side responding. Entry moves to that bar's close.", Order = 2, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool RequireResponseConfirmation { get; set; }

		[Display(Name = "Response: trapped side before trigger (delta flip)", Description = "The failed attempt must be on a bar BEFORE the trigger bar.", Order = 3, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool RequireDeltaFlipForResponse { get; set; }

		[Display(Name = "Stop by setup family", Description = "Response = beyond the defended zone. Initiation = far side of the initiation bar. Overrides 'Stop anchor'.", Order = 4, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool StopByFamily { get; set; }

		[Range(1, 500)]
		[Display(Name = "Tape speed lookback (bars)", Description = "RESEARCH PARAMETER. Bar volume vs the average of these bars (speed-of-tape proxy).", Order = 5, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public int SpeedLookbackBars { get; set; }

		[Range(0, 100)]
		[Display(Name = "Min tape speed ratio", Description = "RESEARCH PARAMETER. Below this an initiation is flagged NO_TAPE_SPEED.", Order = 6, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public double MinSpeedRatio { get; set; }

		[Range(1, 100)]
		[Display(Name = "CVD lookback (bars)", Description = "CVD change over these bars must agree with direction for CVD_ALIGNED.", Order = 7, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public int CvdLookbackBars { get; set; }

		[Display(Name = "No tape speed caps initiation grade", Description = "Jeron: a breakout without speed is a reversal warning. Caps grade at B.", Order = 8, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool FlagInitiationWithoutSpeed { get; set; }

		[Display(Name = "Reject entries at session POC", Description = "Part 6: don't trade the middle / POC of a range.", Order = 9, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool RejectAtSessionPoc { get; set; }

		[Range(0, 1000)]
		[Display(Name = "POC buffer (ticks)", Order = 10, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public int PocBufferTicks { get; set; }

		[Display(Name = "Context bias (manual, from your preopen read)", Description = "None / Bullish / Bearish / Balanced. Counter-context candidates grade C.", Order = 11, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public JeronContextBias ContextBias { get; set; }

		[Display(Name = "Reject counter-context entries", Order = 12, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public bool RejectCounterContext { get; set; }

		[Range(0, 100)]
		[Display(Name = "Exit warning: opposing effort streak", Description = "Consecutive opposing effort bars that trigger EXIT_WARN (Jeron: 2+). 0 = off.", Order = 13, GroupName = "4b. Entry model v2 (Jeron two-branch)")]
		public int ExitWarnOppStreak { get; set; }

		// ---- 4c. Location & session filters (v2.1) ----
		[Display(Name = "Entries only at qualified locations", Description = "Frozen zones, Power Trade zones, or imbalance stacks meeting the quality bar. Others log as EventOnly (UNQUALIFIED_LOCATION).", Order = 1, GroupName = "4c. Location & session filters (v2.1)")]
		public bool RequireQualifiedLocation { get; set; }

		[Range(1, 50)]
		[Display(Name = "Qualified imbalance stack (min levels)", Description = "RESEARCH PARAMETER (not a Jeron number).", Order = 2, GroupName = "4c. Location & session filters (v2.1)")]
		public int QualifiedStackMin { get; set; }

		[Display(Name = "All-strong (900%) stack qualifies", Order = 3, GroupName = "4c. Location & session filters (v2.1)")]
		public bool StrongStackQualifies { get; set; }

		[Display(Name = "Targets from qualified locations only", Description = "Next frozen/Power/qualified zone, session VWAP or session high/low. Minor stacks are skipped.", Order = 4, GroupName = "4c. Location & session filters (v2.1)")]
		public bool TargetsQualifiedOnly { get; set; }

		[Display(Name = "Response stop beyond rejection swing", Description = "Stop beyond the extreme the trapped side reached, if further than the zone edge.", Order = 5, GroupName = "4c. Location & session filters (v2.1)")]
		public bool ResponseStopBeyondAttempt { get; set; }

		[Display(Name = "Carry intraday zones across sessions", Description = "Off = developing zones expire at each session start.", Order = 6, GroupName = "4c. Location & session filters (v2.1)")]
		public bool CarryIntradayZones { get; set; }

		[Display(Name = "Entries in NY session only", Description = "Asia/London events are still logged (EventOnly, OUTSIDE_NY_SESSION).", Order = 7, GroupName = "4c. Location & session filters (v2.1)")]
		public bool NyOnlyEntries { get; set; }

		[Display(Name = "Track frozen-zone dates only", Description = "Only evaluate and log the trading date(s) in Frozen zones / Zones date. Keeps logs small.", Order = 8, GroupName = "4c. Location & session filters (v2.1)")]
		public bool TrackZoneDatesOnly { get; set; }

		// ---- 4d. v2.2 entry fixes ----
		[Display(Name = "Response: trapped-side search back to first touch", Description = "Search for the failed attempt back to the bar that first touched the zone on this visit (capped below), not only 'Response lookback' bars. The trapped side can be several bars before the trigger.", Order = 1, GroupName = "4d. v2.2 entry fixes")]
		public bool ResponseLookbackToFirstTouch { get; set; }

		[Range(1, 150)]
		[Display(Name = "Max trapped-side lookback (bars)", Description = "RESEARCH PARAMETER. Cap on the first-touch search.", Order = 2, GroupName = "4d. v2.2 entry fixes")]
		public int MaxResponseLookbackBars { get; set; }

		[Range(0, 20)]
		[Display(Name = "Late trigger window (bars, 0 = off)", Description = "RESEARCH PARAMETER. If the first close beyond a zone fails the event gates, a later bar that also closes beyond it within this many bars is evaluated as the trigger (LATE_TRIGGER).", Order = 3, GroupName = "4d. v2.2 entry fixes")]
		public int RetriggerBars { get; set; }

		[Display(Name = "One candidate per bar and direction", Description = "Overlapping zones breaking on the same bar log one CANDIDATE row (best status, then frozen > Power > qualified stack, then R:R). The others are listed in its Detail.", Order = 4, GroupName = "4d. v2.2 entry fixes")]
		public bool DedupeCandidatesPerBar { get; set; }

		[Display(Name = "Target: nearest level meeting min R:R", Description = "Skip nearer levels that fail Min reward:risk and use the next mapped level that meets it (flag TARGET_BEYOND_NEAREST, skipped levels in Detail).", Order = 5, GroupName = "4d. v2.2 entry fixes")]
		public bool TargetMinRRSearch { get; set; }

		[Display(Name = "Also aggregate Power Trades by time cluster", Description = "Runs the time-cluster method (gap/tolerance in group 3) alongside the chosen method, so one order filled across a flickering quote is not split. Overlapping Power zones merge.", Order = 6, GroupName = "4d. v2.2 entry fixes")]
		public bool AddTimeClusterPowerTrades { get; set; }

		// ---- 5. Outcomes ----
		[Range(1, 10000)]
		[Display(Name = "Outcome window (bars)", Description = "With the session-end window on (5b), this is the snapshot length logged as Outcome15 / PnL15Ticks. With it off, outcomes expire after this many bars (v2.4).", Order = 1, GroupName = "5. Outcomes")]
		public int OutcomeBars { get; set; }

		// ---- 5b. v2.5 research logging (entries unchanged) ----
		[Display(Name = "Outcome window: to NY session end", Description = "On: outcomes run until target, stop or the NY session end (SESSION_END, P/L at that close). The 'Outcome window (bars)' result is still logged as Outcome15 / PnL15Ticks. Off: v2.4 behaviour (TIME_EXPIRED after that many bars).", Order = 1, GroupName = "5b. Research logging (v2.5)")]
		public bool OutcomeToSessionEnd { get; set; }

		[Display(Name = "Log retest paths", Description = "Follows a hypothetical retest entry for every event-valid candidate and writes one RETEST row per signal and fail tolerance, with the immediate entry's result alongside. Logging only.", Order = 2, GroupName = "5b. Research logging (v2.5)")]
		public bool LogRetestPaths { get; set; }

		[Range(1, 500)]
		[Display(Name = "Retest window (bars)", Description = "RESEARCH PARAMETER. Bars after the immediate entry in which the retest must happen.", Order = 3, GroupName = "5b. Research logging (v2.5)")]
		public int RetestWindowBars { get; set; }

		[Display(Name = "Retest fail tolerances (ticks)", Description = "RESEARCH PARAMETER. Comma list; one retest path per value. A close this many ticks beyond the zone's far edge fails the retest.", Order = 4, GroupName = "5b. Research logging (v2.5)")]
		public string RetestFailTicksList { get; set; }

		[Display(Name = "Log shadow candidates", Description = "Candidates dropped by 'One candidate per bar and direction' are written as SHADOW rows with outcomes (SHADOW_OUTCOME). Never counted as entries.", Order = 5, GroupName = "5b. Research logging (v2.5)")]
		public bool LogShadowCandidates { get; set; }

		// ---- 5c. v2.6 order-flow retest (research logging, entries unchanged) ----
		[Display(Name = "Log order-flow retest (v2)", Description = "Adds a RETEST row (RetestModel = v2) per event-valid signal: price must leave first, first retest only, entry needs the opposite side to fail AND a fresh imbalance or delta flip. Logging only.", Order = 1, GroupName = "5c. Order-flow retest (v2.6)")]
		public bool LogRetestV2 { get; set; }

		[Range(1, 500)]
		[Display(Name = "Retest v2 window (bars)", Description = "RESEARCH PARAMETER. Bars after the entry bar in which departure and the first retest must happen.", Order = 2, GroupName = "5c. Order-flow retest (v2.6)")]
		public int RetestV2WindowBars { get; set; }

		[Range(0, 20)]
		[Display(Name = "Min travel before a retest counts (ATR)", Description = "RESEARCH PARAMETER (Jeron R2: about one ATR). Distance beyond the near edge price must reach first.", Order = 3, GroupName = "5c. Order-flow retest (v2.6)")]
		public double RetestV2MinTravelAtr { get; set; }

		[Range(0, 100)]
		[Display(Name = "Min bars before a retest counts", Description = "RESEARCH PARAMETER. A return sooner than this is the break still forming.", Order = 4, GroupName = "5c. Order-flow retest (v2.6)")]
		public int RetestV2MinBars { get; set; }

		[Range(1, 200)]
		[Display(Name = "ATR period (1-minute bars)", Order = 5, GroupName = "5c. Order-flow retest (v2.6)")]
		public int RetestV2AtrPeriod { get; set; }

		[Range(0, int.MaxValue)]
		[Display(Name = "Opposing delta that counts as the other side showing up", Description = "RESEARCH PARAMETER. Or an opposing imbalance / large trade on the retest bar.", Order = 6, GroupName = "5c. Order-flow retest (v2.6)")]
		public int RetestV2OppDeltaMin { get; set; }

		[Range(0, 1000)]
		[Display(Name = "Retest v2 fail (ticks beyond far edge, full body)", Order = 7, GroupName = "5c. Order-flow retest (v2.6)")]
		public int RetestV2FailTicks { get; set; }

		[Display(Name = "Log reversal candidates on failed retests", Description = "Jeron M4: a failed retest logs the other side (REVERSAL_CANDIDATE) with its own outcome (REVERSAL_OUTCOME). Research only.", Order = 8, GroupName = "5c. Order-flow retest (v2.6)")]
		public bool LogReversalCandidates { get; set; }

		// ---- 5d. Research rules v1.1 (v2.10) ----
		[Display(Name = "Log research rules v1.1 (FAV01/FAV02/CAR01/CAR03/RIZ01)", Description = "RESEARCH ONLY. RESEARCH_SIGNAL / OUTCOME / NOENTRY rows and the feature columns. Never changes an entry.", Order = 1, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public bool LogResearchRules { get; set; }

		[Display(Name = "Log exit models (FAV03 POC target, CAR04 break-even)", Description = "One EXIT_MODEL row per event-valid candidate: the same entry with Fabio's single POC target and with Carmine's break-even stop.", Order = 2, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public bool LogExitModels { get; set; }

		[Range(0.1, 20)]
		[Display(Name = "CAR04 break-even after (R)", Description = "RESEARCH PARAMETER (Carmine gives no number). Stop moves to entry from the bar after the trade is up this many R.", Order = 3, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public double Car04BreakEvenR { get; set; }

		[Range(1, 100)]
		[Display(Name = "LVN row size (ticks)", Description = "RESEARCH PARAMETER. Volume-profile rows used to find a low-volume node (4 ticks = 1 NQ point).", Order = 4, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int LvnRowTicks { get; set; }

		[Range(0.01, 1)]
		[Display(Name = "LVN max volume ratio", Description = "RESEARCH PARAMETER. A row is an LVN when its volume is at most this share of the leg's mean row volume.", Order = 5, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public double LvnMaxRatio { get; set; }

		[Range(0, 45)]
		[Display(Name = "LVN edge rows skipped (%)", Description = "RESEARCH PARAMETER. Rows at each end of the leg that cannot be its LVN.", Order = 6, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int LvnEdgeExcludePct { get; set; }

		[Range(1, 1000)]
		[Display(Name = "Research window (bars)", Description = "RESEARCH PARAMETER. Bars to wait for the LVN touch, and for the reaction after it.", Order = 7, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int ResearchWindowBars { get; set; }

		[Range(0, 1000)]
		[Display(Name = "Research LVN fail (ticks beyond, full body)", Order = 8, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int ResearchFailTicks { get; set; }

		[Range(0.1, 50)]
		[Display(Name = "FAV01 impulse (ATR)", Description = "RESEARCH PARAMETER. Leg size that counts as Fabio's out-of-balance impulse.", Order = 9, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public double Fav01ImpulseAtr { get; set; }

		[Range(2, 500)]
		[Display(Name = "FAV01 impulse lookback (bars)", Order = 10, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int Fav01LookbackBars { get; set; }

		[Range(1, 20)]
		[Display(Name = "FAV02 failed breakouts per side per day", Order = 11, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int Fav02MaxPerSide { get; set; }

		[Range(0, 50)]
		[Display(Name = "CAR01 move away from the zone (ATR)", Description = "RESEARCH PARAMETER. How far price must leave the plan zone before the leg's LVN is read.", Order = 12, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public double Car01MinImpulseAtr { get; set; }

		[Range(1, 1000)]
		[Display(Name = "CAR03 minimum flush (ticks beyond the level)", Order = 13, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int Car03MinFlushTicks { get; set; }

		[Range(1, 500)]
		[Display(Name = "CAR03 reclaim within (bars)", Order = 14, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int Car03MaxReclaimBars { get; set; }

		[Range(1, 500)]
		[Display(Name = "EMA period (ema21_aligned)", Description = "Jeron TikTok (manifest only): 1-minute 21 EMA.", Order = 15, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int ResearchEmaPeriod { get; set; }

		[Range(1, 500)]
		[Display(Name = "CVD average period (cvd_avg_aligned)", Description = "RESEARCH PARAMETER. Jeron does not state the CVD average length.", Order = 16, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int ResearchCvdAvgPeriod { get; set; }

		[Range(1, 200)]
		[Display(Name = "Move into zone lookback (bars)", Description = "move_into_zone_atr: bars before the first touch.", Order = 17, GroupName = "5d. Research rules v1.1 (v2.10)")]
		public int MoveIntoZoneBars { get; set; }

		// ---- 5e. S1.4 research flags (logging only) ----
		[Display(Name = "Log S1.4 research flags", Description = "Passive trapped side, relative delta, reversal after a stop-out, fight at the level. Logging only: no gate, status, stop or target changes.", Order = 1, GroupName = "5e. S1.4 research flags (logging only)")]
		public bool LogS14Flags { get; set; }

		[Range(0, 100)]
		[Display(Name = "Passive trap: max delta % of the trapped side", Description = "RESEARCH PARAMETER. NO_AGGRESSION: the trapped side's signed delta % on the bar is below this.", Order = 2, GroupName = "5e. S1.4 research flags (logging only)")]
		public double PassiveMaxDeltaPct { get; set; }

		[Range(1, 100)]
		[Display(Name = "Passive trap: min wick (% of bar range)", Description = "RESEARCH PARAMETER. WICK_NO_FOLLOW: the wick into the zone is at least this share of the bar's range, with no imbalance or large trade from that side.", Order = 3, GroupName = "5e. S1.4 research flags (logging only)")]
		public double PassiveWickPct { get; set; }

		[Range(2, 200)]
		[Display(Name = "Relative delta: rank window (bars)", Description = "RESEARCH PARAMETER. delta_rank_20 uses this many bars including the trigger bar.", Order = 4, GroupName = "5e. S1.4 research flags (logging only)")]
		public int RelativeDeltaBars { get; set; }

		[Range(0, 500)]
		[Display(Name = "Reversal after stop window (bars, 0 = off)", Description = "RESEARCH PARAMETER. An opposite candidate at an overlapping zone within this many bars of a stop event is logged as REVERSAL_CANDIDATE (AFTER_STOP).", Order = 5, GroupName = "5e. S1.4 research flags (logging only)")]
		public int ReversalAfterStopBars { get; set; }

		[Range(1, 50)]
		[Display(Name = "Fight lookback (bars)", Description = "RESEARCH PARAMETER. Bars up to and including the trigger bar searched for both-sides effort or a two-sided doji at the zone.", Order = 6, GroupName = "5e. S1.4 research flags (logging only)")]
		public int FightLookbackBars { get; set; }

		[Range(1, 100)]
		[Display(Name = "Doji: max body (% of bar range)", Description = "RESEARCH PARAMETER.", Order = 7, GroupName = "5e. S1.4 research flags (logging only)")]
		public double DojiBodyPct { get; set; }

		// ---- 6. Sessions ----
		[Display(Name = "Asia start (CT)", Order = 1, GroupName = "6. Sessions (Central Time)")]
		public string AsiaStartCT { get; set; }

		[Display(Name = "London start (CT)", Order = 2, GroupName = "6. Sessions (Central Time)")]
		public string LondonStartCT { get; set; }

		[Display(Name = "New York start (CT)", Order = 3, GroupName = "6. Sessions (Central Time)")]
		public string NyStartCT { get; set; }

		[Display(Name = "New York end (CT)", Order = 4, GroupName = "6. Sessions (Central Time)")]
		public string NyEndCT { get; set; }

		// ---- 7. Display ----
		[Display(Name = "Show frozen zones", Order = 1, GroupName = "7. Display")]
		public bool ShowFrozenZones { get; set; }

		[Display(Name = "Show intraday zones", Order = 2, GroupName = "7. Display")]
		public bool ShowIntradayZones { get; set; }

		[Display(Name = "Show state labels", Order = 3, GroupName = "7. Display")]
		public bool ShowLabels { get; set; }

		[Display(Name = "Labels on intraday zones", Order = 4, GroupName = "7. Display")]
		public bool ShowIntradayLabels { get; set; }

		[Display(Name = "Show rejected candidates (gray)", Order = 5, GroupName = "7. Display")]
		public bool ShowRejectedLabels { get; set; }

		[Display(Name = "Show session VWAP", Order = 6, GroupName = "7. Display")]
		public bool ShowVwap { get; set; }

		[Display(Name = "Status panel", Order = 7, GroupName = "7. Display")]
		public bool ShowStatusPanel { get; set; }

		[Range(1, 1000)]
		[Display(Name = "Max active intraday zones", Order = 8, GroupName = "7. Display")]
		public int MaxIntradayZones { get; set; }

		[Range(1, 100)]
		[Display(Name = "Zone opacity (%)", Order = 9, GroupName = "7. Display")]
		public int ZoneOpacity { get; set; }

		[XmlIgnore]
		[Display(Name = "Frozen zone color", Order = 10, GroupName = "7. Display")]
		public Brush FrozenZoneBrush { get; set; }

		[Browsable(false)]
		public string FrozenZoneBrushSerializable
		{
			get { return Serialize.BrushToString(FrozenZoneBrush); }
			set { FrozenZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Imbalance buy zone color", Description = "Zones created from stacked buy imbalances.", Order = 11, GroupName = "7. Display")]
		public Brush BuyZoneBrush { get; set; }

		[Browsable(false)]
		public string BuyZoneBrushSerializable
		{
			get { return Serialize.BrushToString(BuyZoneBrush); }
			set { BuyZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Imbalance sell zone color", Description = "Zones created from stacked sell imbalances.", Order = 12, GroupName = "7. Display")]
		public Brush SellZoneBrush { get; set; }

		[Browsable(false)]
		public string SellZoneBrushSerializable
		{
			get { return Serialize.BrushToString(SellZoneBrush); }
			set { SellZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Power Trade buy zone color", Description = "Zones created from buy Power Trade clusters.", Order = 13, GroupName = "7. Display")]
		public Brush PowerBuyZoneBrush { get; set; }

		[Browsable(false)]
		public string PowerBuyZoneBrushSerializable
		{
			get { return Serialize.BrushToString(PowerBuyZoneBrush); }
			set { PowerBuyZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Power Trade sell zone color", Description = "Zones created from sell Power Trade clusters.", Order = 14, GroupName = "7. Display")]
		public Brush PowerSellZoneBrush { get; set; }

		[Browsable(false)]
		public string PowerSellZoneBrushSerializable
		{
			get { return Serialize.BrushToString(PowerSellZoneBrush); }
			set { PowerSellZoneBrush = Serialize.StringToBrush(value); }
		}

		[Display(Name = "Power zone tags (PWR BUY/SELL + size)", Order = 15, GroupName = "7. Display")]
		public bool ShowPowerZoneTags { get; set; }

		// ---- 8. Logging ----
		[Display(Name = "Export event log (CSV)", Order = 1, GroupName = "8. Logging")]
		public bool ExportEventLog { get; set; }

		[Display(Name = "Log folder (blank = Drive Preopen Exchange\\logs)", Order = 2, GroupName = "8. Logging")]
		public string LogFolder { get; set; }


		// ---- 0. Fast load (S1.2) ----
		[Range(0, 1000)]
		[Display(Name = "Evaluate last N trading days (0 = all loaded)", Description = "1 = only today's trading date (from its 17:00 CT open). Older bars load but are not evaluated or logged, so the strategy starts fast. Use 0 in Strategy Analyzer.", Order = 1, GroupName = "0. Fast load (S1.2)")]
		public int EvaluateLastDays { get; set; }

		[Range(0, 10)]
		[Display(Name = "Warm-up days before that", Description = "Read bar by bar for ATR, EMA, prior RTH high/low and prior RTH POC. No ticks, no signals, no log rows. Load at least this many days + 1.", Order = 2, GroupName = "0. Fast load (S1.2)")]
		public int WarmupDays { get; set; }

		[Display(Name = "Evaluate from date (yyyy-MM-dd, blank = use N days)", Description = "For Playback or a backtest: evaluate from this trading date on. Overrides N days.", Order = 3, GroupName = "0. Fast load (S1.2)")]
		public string EvaluateFromDate { get; set; }

		// ---- 11. Auto trading (S1.1) ----
		[Display(Name = "Auto trading on", Description = "Off = the strategy only logs (same rows as the tracker) and never sends orders.", Order = 1, GroupName = "11. Auto trading (S1.1)")]
		public bool AutoTradeEnabled { get; set; }

		[Range(1, 100)]
		[Display(Name = "Contracts per trade", Order = 2, GroupName = "11. Auto trading (S1.1)")]
		public int TradeQuantity { get; set; }

		[Display(Name = "Trade historical bars", Description = "On for Playback and Strategy Analyzer. Live start uses Wait until flat.", Order = 3, GroupName = "11. Auto trading (S1.1)")]
		public bool TradeHistoricalBars { get; set; }

		[Display(Name = "Allow live (non-Sim) account", Description = "Off = orders are blocked on any account that is not Sim/Playback (ORDER_BLOCKED LIVE_ACCOUNT_BLOCKED).", Order = 4, GroupName = "11. Auto trading (S1.1)")]
		public bool AllowLiveAccount { get; set; }

		[Display(Name = "Simulated account name prefixes", Description = "Accounts whose name starts with one of these (comma list) count as simulated, besides NinjaTrader's own Sim/Playback accounts. Default includes DEMO (DEMO5903068 is a Simulation-connection account, like Sim101). Never add a funded account here.", Order = 4, GroupName = "11. Auto trading (S1.1)")]
		public string SimAccountPrefixes { get; set; }

		[Display(Name = "Require Claude review (review=APPROVED)", Description = "The day's PreopenPlan must contain review=APPROVED. Missing or LOG_ONLY = research logging only.", Order = 5, GroupName = "11. Auto trading (S1.1)")]
		public bool RequirePlanReview { get; set; }

		[Display(Name = "Require my approval file", Description = "Approve_<yyyy-MM-dd>.txt with the line approve=1 in the plan folder.", Order = 6, GroupName = "11. Auto trading (S1.1)")]
		public bool RequireManualApproval { get; set; }

		[Range(0, 100)]
		[Display(Name = "Max trades per day (0 = no limit)", Description = "The plan's max_trades= can lower this, never raise it.", Order = 7, GroupName = "11. Auto trading (S1.1)")]
		public int MaxTradesPerDay { get; set; }

		[Range(0, 100000)]
		[Display(Name = "Max daily loss (ticks per contract, 0 = off)", Order = 8, GroupName = "11. Auto trading (S1.1)")]
		public int MaxDailyLossTicks { get; set; }

		[Range(0, 100)]
		[Display(Name = "Max consecutive losses (0 = off)", Order = 9, GroupName = "11. Auto trading (S1.1)")]
		public int MaxConsecutiveLosses { get; set; }

		[Display(Name = "Last entry (CT, HH:mm)", Order = 10, GroupName = "11. Auto trading (S1.1)")]
		public string LastEntryCT { get; set; }

		[Display(Name = "Flatten (CT, HH:mm)", Order = 11, GroupName = "11. Auto trading (S1.1)")]
		public string FlattenCT { get; set; }

		[Display(Name = "Grades allowed", Description = "Comma list of A+, B+, B, C. S1.4 default A+,B+,B: counter-context candidates (C) are logged and followed but not traded. Add C for the S1.3 behaviour.", Order = 12, GroupName = "11. Auto trading (S1.1)")]
		public string AllowedGrades { get; set; }

		[Range(0, 1000)]
		[Display(Name = "Max entry slippage (ticks, 0 = off)", Description = "Skip if the decision tick is this far from the signal close.", Order = 13, GroupName = "11. Auto trading (S1.1)")]
		public int MaxEntrySlippageTicks { get; set; }

		[Display(Name = "Exit on first exit warning if not in profit", Description = "Jeron M1 research idea. Off by default.", Order = 14, GroupName = "11. Auto trading (S1.1)")]
		public bool ExitOnFirstExitWarn { get; set; }

		// ---- 12. Trade lines (copied from HarrisJigsaw HJ 2.17 "5. Display") ----
		[Display(Name = "Enable TP Entry SL Lines", Order = 1, GroupName = "12. Trade lines (HJ display)")]
		public bool EnableTradeLines { get; set; }

		[Display(Name = "Enable Entry Price Marker", Description = "Draws price only on entry candle; no Pattern text label.", Order = 2, GroupName = "12. Trade lines (HJ display)")]
		public bool EnableEntryPriceMarker { get; set; }

		[Display(Name = "ATM PnL Display", Description = "What the entry box shows: Currency (open PnL in $ for the remaining contracts), Points (like the native ATM), or Ticks.", Order = 3, GroupName = "12. Trade lines (HJ display)")]
		public JeronAtmPnlDisplayMode AtmPnlDisplay { get; set; }

		[Range(130, 3000)]
		[Display(Name = "ATM Label Offset Pixels", Description = "Distance from the right edge of the price panel to the TP/STP tags and the entry box.", Order = 4, GroupName = "12. Trade lines (HJ display)")]
		public int AtmLabelOffsetPixels { get; set; }
		#endregion
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	// S1.1: ATM PnL box modes (same values as HJ's AtmPnlDisplayMode; renamed so both strategies can be installed)
	public enum JeronAtmPnlDisplayMode { Currency, Points, Ticks }
}
