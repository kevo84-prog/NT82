// =====================================================================================
//  JeronPreopenMap.cs  —  Jeron Pre-open Location Map + Review Packet (v2.3, Oct 24 2026)
//
//  WHAT IT DOES
//  Builds the frozen pre-open map from NinjaTrader's own data at your as-of time and writes:
//   1. PreopenPacket_<instrument>_<date>.json  — everything Claude needs to answer Jeron's pre-open
//      questions (levels, zones with confluence tiers, TPO, single prints, HVN/LVN, settlement,
//      overnight inventory, value migration, location, delta profile, 1-hour structure, ES cross-check).
//      Claude reads it, adds VIX / 10-year / news, and writes PreopenPlan_<date>.txt for the tracker.
//   2. Zones_<instrument>_<date>.txt and FrozenZones_..._run<stamp>.txt — the tracker's Frozen zones
//      format (fallback when there is no plan). Target-only zones are labelled T_..., decision zones D_...
//   3. PreopenLevels_..._run<stamp>.csv — every level, for checking against TradingView.
//
//  DATA SERIES (added automatically)
//   - 1 tick of the chart instrument: volume profiles, TPO, settlement, VWAP, overnight stats, hourly bars.
//   - 1-minute BidAsk Volumetric of the chart instrument (optional): exact delta profile.
//   - 1 minute of the ES contract (optional): ES cross-check levels.
//   Days to load: 10+ (prior week profile, composite HVN/LVN and 1-hour structure need them).
//
//  NO-HINDSIGHT RULES
//   - The map for trading date D is built on the FIRST tick at or after D's as-of time from earlier data only.
//   - Volumetric and ES values are whatever had been processed before that tick; the packet records the
//     time each one reached (delta_through_ct, es.through_ct).
//   - A profile whose window is not fully covered by loaded data (late start or a tick gap) is left out or
//     flagged. Prior sessions are assigned by calendar; a missing day keeps its slot.
//
//  OUR RESEARCH PARAMETERS (not Jeron numbers): merge distance, padding, max zone width, decision tier (2+
//  independent periods), TPO/HVN row sizes, HVN/LVN thresholds, inventory and migration thresholds, swing
//  strength. Jeron's: 70% value area, cash 9:30-16:00 ET, overnight 18:00 ET to the pre-open, session VWAP
//  with bands, weekly and prior-week profiles and TPO for framing, single prints / low-time areas, delta
//  profile, stacking levels to find decision zones.
//
//  v2.3  (Oct 24 2026) From the map-vs-transcripts review (Oct 24). Every number below is OUR research parameter.
//        1. As-of default 08:10 CT (prompt v1.5 schedule: map 08:10, Claude plan run 08:11). Was 08:20.
//        2. Half-day dates ('Half-day dates', default 2026-11-27@12:00; 2026-12-24@12:00): cash session and settlement end
//           at the given time, and the quiet stretch from 15 minutes after it to the 17:00 CT open is a normal break, not a
//           data gap. Before v2.3 the next morning lost PD (check A -> LOG_ONLY) and the prior-week profile for a week.
//           Packet: calendar.half_day_today / calendar.pd_half_day.
//        3. HTF depth (A6, Part 2 ~4:02, Part 3 ~7:00: 2-3 month composite). The HTF composite can now come from an extra
//           1-minute series of the chart instrument loaded for 'HTF load days' (default 100 calendar days) independently of
//           the tick series, so the chart's own Days to load stays small. Each minute's volume is spread evenly over its
//           range (approximate, like the ES profile); htf_composite.source = MINUTE_APPROX | TICK. Default 60 trading days,
//           40 minimum for zones. Tick-built days are kept 'Keep tick days (calendar)' (default 45, unchanged).
//           Manual HTF levels can carry a date: 2026-10-20@VAH=31600;POC=31200 (used from that trading date on; the latest
//           date wins per name; older than 'Manual HTF max age' = flagged stale in the packet). Undated levels work as before.
//           The all-time-high profile still has to come from the manual levels (ATHPOC=...).
//        4. Balance merge (B7, Part 6 ~1:40, Part 5 ~5:11, webinar ~24:28): balance_composite = the overlapping members of
//           PD2, PD and ON merged into one profile, with overlap % per pair and an overlapping flag; pd_on_composite gains
//           va_overlap_pct and overlapping.
//        5. Weakening zone (A7, Part 3 ~6:01): zones[].tests gains hours_per_test (last 4) and shrinking_time.
//        6. Double distribution (D8, Part 1 ~1:21-1:25): double_distribution = PD cash profile with two HVN blocks
//           separated by an LVN or a PD single-print run.
//        7. PD2 / PD3 cash highs and lows as levels (PD2H, PD2L, PD3H, PD3L) in their own families ('PD2/PD3 high-low').
//        8. 'Settlement family' SET (default, unchanged) or PD: with PD the settlement no longer counts as a separate
//           independent period, so PD POC + PD settlement alone stays a TARGET zone. For the backtest comparison only.
//        Not changed here: the packet file name keeps NinjaTrader's contract token (PreopenPacket_NQ_12_26_<date>.json;
//        prompt v1.5's exact-title search for NQ_DEC26 misses and its fallback search finds it). ES contract: update at the roll.
//  v2.2  (Oct 20 2026) Automated morning: as-of default 08:20 CT (the 08:21 Claude run reads the packet and the
//        tracker activates the plan at 08:25); output folder default
//        G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\zones; the packet and Zones file are written to a
//        .tmp file first and then renamed, so Google Drive never uploads a half-written packet.
//  v2.1  From the full transcript review (Parts 1-6 + webinars): zone test history from 1-hour bars (how many
//        times each zone was tested / rejected / crossed, highs and lows into it); value-vs-price check (new
//        high with lower value = no acceptance, Part 4 ~0:57); PD cash + overnight combined profile (Part 5 ~5:11,
//        Part 6 ~1:40); ADR and range context (Part 1 ~1:24:03 extended moves); HTF composite VA/POC/HVN/LVN
//        from loaded days plus optional manual HTF levels from a 2-3 month TradingView composite (Part 2 ~4:02,
//        Part 3 ~7:00); swing-anchored profile and delta bands (Part 4 ~2:43); overnight volume distribution
//        (thin overnight profile, Part 3 ~5:00). Days to load: 15+ for the swing profile, 30+ for a 20-day HTF
//        composite (or paste the HTF levels).
//  v2.0  Prior-week profile; TPO (30-min periods) POC/VAH/VAL and single prints; composite HVN/LVN; CME-style
//        settlement (VWAP of the last 30 s before 15:00 CT) and 16:00 close; overnight inventory; value
//        migration; location at the as-of time; weekly VWAP; delta profile from Volumetric bars; 1-hour bars
//        and swings; ES cross-check; confluence tiers by independent periods; JSON review packet.
//  v1.1  Data-gap detection; PD/PD2/PD3 by calendar; Holiday dates.
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
using NinjaTrader.NinjaScript.BarsTypes;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class JeronPreopenMap : Indicator
	{
		// ------------------------------------------------------------------------------
		//  Internal types
		// ------------------------------------------------------------------------------
		private class PriceProfile
		{
			public Dictionary<long, long> Vol = new Dictionary<long, long>();      // key = price in ticks
			public Dictionary<long, long> Tpo = new Dictionary<long, long>();      // key = TPO row index
			private readonly Dictionary<long, long> lastPeriod = new Dictionary<long, long>();
			public long Total;
			public double High = double.MinValue, Low = double.MaxValue;
			public DateTime FirstCt = DateTime.MinValue, LastCt = DateTime.MinValue;
			public int TpoRowTicks = 20;

			public void AddTick(long key, double price, long size, DateTime ct, long periodId)
			{
				long cur;
				Vol.TryGetValue(key, out cur);
				Vol[key] = cur + size;
				Total += size;
				if (price > High) High = price;
				if (price < Low) Low = price;
				if (FirstCt == DateTime.MinValue) FirstCt = ct;
				LastCt = ct;
				long row = FloorDiv(key, TpoRowTicks);
				long lp;
				if (!lastPeriod.TryGetValue(row, out lp) || lp != periodId)
				{
					lastPeriod[row] = periodId;
					long n;
					Tpo.TryGetValue(row, out n);
					Tpo[row] = n + 1;
				}
			}

			public bool Empty { get { return Total <= 0; } }
		}

		private class DayStats
		{
			public DateTime Date;
			public PriceProfile Cash;
			public Dictionary<long, long> Rows = new Dictionary<long, long>();   // whole trading day, HVN row size
			public double Open = double.NaN, High = double.MinValue, Low = double.MaxValue, Last = double.NaN, CashOpen = double.NaN;
			public double SettlePv, SettleV, PreSettleLast = double.NaN;
		}

		private class DataGap
		{
			public DateTime Start, End;
		}

		private class Level
		{
			public string Name;
			public string Family;    // independent period: PD, PD2, PD3, ON, WK, PWK, SET, VWAP, WVWAP
			public string Kind;      // VP, TPO, HL, SET, VWAP
			public double Price;
			public bool InZones;
		}

		private class Area
		{
			public string Type;      // SP, LVN, HVN
			public string Source;    // TPO_PD, TPO_ON, TPO_WK, TPO_PWK, COMP
			public double Lo, Hi;
		}

		private class Zone
		{
			public double Lo, Hi;
			public double MinLevel, MaxLevel;
			public List<Level> Levels = new List<Level>();
			public List<string> Tags = new List<string>();
			public int Sources;
			public string Tier = "TARGET";
			public string Label = "";
			public bool Manual;
		}

		private class DayMap
		{
			public DateTime Date;
			public DateTime AsOfCt, CashEndCt;
			public double RefPrice;
			public List<Level> Levels = new List<Level>();
			public List<Area> Areas = new List<Area>();
			public List<Zone> Zones = new List<Zone>();
			public List<string> Notes = new List<string>();
			public string PacketJson = "";
			public bool Drawn;
		}

		private class ManualDef
		{
			public bool HasDate;
			public DateTime Date;
			public double Lo, Hi;
			public string Label;
		}

		private class HourBar
		{
			public DateTime HourCt;
			public double O, H, L, C;
			public long V;
			public Dictionary<long, long> Rows;   // v2.1: volume by HVN row (chart instrument only; null for ES)
		}

		private class EsDay
		{
			public DateTime Date;
			public double CashHigh = double.MinValue, CashLow = double.MaxValue, Settle = double.NaN, Last = double.NaN;
			public Dictionary<long, double> Rows = new Dictionary<long, double>();   // approx cash profile
			public double RowTotal;
		}

		// ------------------------------------------------------------------------------
		//  State
		// ------------------------------------------------------------------------------
		private const string Version = "2.3";
		private static readonly DateTime Epoch = new DateTime(2000, 1, 1);
		private double tickSize = 0.25;
		private string instrumentToken = "NA";
		private TimeZoneInfo centralTz, localTz;
		private int asOfMin, cashStartMin, cashEndMin, sessionStartMin, settleMin;
		private int tickIdx = 1, esIdx = -1, volIdx = -1;
		private DateTime firstTickCt = DateTime.MinValue, lastTickCt = DateTime.MinValue;
		private DateTime curTradingDate = DateTime.MinValue, curWeekMonday = DateTime.MinValue, buildFromDate = DateTime.MinValue;
		private bool builtToday;
		private double lastPrice = double.NaN;

		private DayStats today;
		private readonly Dictionary<DateTime, DayStats> days = new Dictionary<DateTime, DayStats>();
		private readonly List<DataGap> gaps = new List<DataGap>();
		private readonly HashSet<DateTime> holidays = new HashSet<DateTime>();
		private readonly Dictionary<DateTime, int> halfDays = new Dictionary<DateTime, int>();   // v2.3: trading date -> early cash end (min CT)
		// v2.3 HTF composite from a 1-minute series (approximate: volume spread over each minute's range)
		private int htfIdx = -1;
		private readonly Dictionary<DateTime, Dictionary<long, double>> htfMinDays = new Dictionary<DateTime, Dictionary<long, double>>();
		private readonly Dictionary<DateTime, int> htfMinCount = new Dictionary<DateTime, int>();
		private DateTime htfThroughCt = DateTime.MinValue;
		private class HtfManual { public DateTime From = DateTime.MinValue; public string Name = ""; public double Price; }
		private readonly List<HtfManual> htfManual = new List<HtfManual>();

		private PriceProfile overnight, weekly, priorWeek;
		private DateTime priorWeekMonday = DateTime.MinValue;
		private double vwSumPv, vwSumP2v, vwSumV, wkPv, wkV;
		// overnight inventory
		private double onOpen = double.NaN, onRunHigh = double.MinValue, onRunLow = double.MaxValue, onMaxDrawFromHigh, onMaxRallyFromLow;
		private double onVolAboveSettle, onVolTotal, onSettleRef = double.NaN;

		private readonly List<HourBar> hours = new List<HourBar>();

		// delta profile (Volumetric)
		private NinjaTrader.NinjaScript.BarsTypes.VolumetricBarsType volType;
		private readonly Dictionary<DateTime, Dictionary<long, long[]>> cashDelta = new Dictionary<DateTime, Dictionary<long, long[]>>();
		private readonly Dictionary<DateTime, Dictionary<long, long[]>> onDelta = new Dictionary<DateTime, Dictionary<long, long[]>>();
		private DateTime deltaThroughCt = DateTime.MinValue;

		// ES
		private readonly Dictionary<DateTime, EsDay> esDays = new Dictionary<DateTime, EsDay>();
		private EsDay esToday;
		private DateTime esCurTd = DateTime.MinValue, esThroughCt = DateTime.MinValue;
		private double esLast = double.NaN, esOnHigh = double.MinValue, esOnLow = double.MaxValue, esPv, esV;
		private readonly List<HourBar> esHours = new List<HourBar>();
		private double esTickSize = 0.25;

		private readonly List<DayMap> maps = new List<DayMap>();
		private readonly List<ManualDef> manualDefs = new List<ManualDef>();
		private string outFolder = "", runStamp = "", pastePath = "", levelsPath = "", lastError = "";
		private DateTime lastStatusDraw = DateTime.MinValue;
		private SimpleFont labelFont;

		// ==============================================================================
		//  Lifecycle
		// ==============================================================================
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description = "Builds the frozen pre-open map and a JSON review packet (profiles, TPO, HVN/LVN, settlement, inventory, migration, delta profile, structure, ES) for the Jeron pre-open review.";
				Name = "JeronPreopenMap";
				Calculate = Calculate.OnBarClose;
				IsOverlay = true;
				DisplayInDataBox = false;
				DrawOnPricePanel = true;
				PaintPriceMarkers = false;
				IsSuspendedWhileInactive = false;

				// 1. Timing
				AsOfCT = "08:10";   // v2.3: prompt v1.5 schedule (map 08:10, Claude plan run 08:11)
				CashStartCT = "08:30";
				CashEndCT = "15:00";
				SessionStartCT = "17:00";
				SettlementCT = "15:00";
				BuildFromDate = "";

				// 2. Profiles
				PriorCashSessions = 3;
				ValueAreaPct = 70;
				TicksPerRow = 1;
				IncludePriorDayHighLow = true;
				IncludeSettlement = true;
				IncludeOvernight = true;
				IncludeOvernightHighLow = true;
				IncludeVwap = true;
				IncludeVwapBand1 = true;
				IncludeVwapBand2 = false;
				IncludeWeekly = true;
				IncludePriorWeek = true;
				IncludeTpo = true;
				TpoTicksPerRow = 20;
				MinSinglePrintRows = 2;
				SkipPartialProfiles = true;
				MaxTickGapMinutes = 15;
				HolidayDates = "2026-11-26; 2026-12-25; 2027-01-01";   // v2.3: full closures in the next few weeks (check the CME calendar)
				HalfDayDates = "2026-11-27@12:00; 2026-12-24@12:00";   // v2.3: check the CME holiday calendar each year
				KeepTickDays = 45;

				// 3. Zones
				MergeDistancePoints = 15;
				ZonePadPoints = 5;
				MaxZoneWidthPoints = 60;
				MaxDistancePoints = 0;
				MinSourcesForDecision = 2;
				IncludeVwapInZones = false;
				IncludeWeeklyVwapInZones = false;
				IncludePriorHighLowAll = true;   // v2.3
				SettlementFamily = "SET";        // v2.3: SET (unchanged) or PD
				ManualZones = "";

				// 4. Review packet
				WritePacket = true;
				StructureDays = 10;
				SwingStrength = 3;
				CompositeDays = 5;
				HvnTicksPerRow = 20;
				HvnPct = 70;
				LvnPct = 30;
				InventoryLongPct = 70;
				InventoryShortPct = 30;
				MigrationOverlapPct = 50;
				IncludeDeltaProfile = true;
				DeltaRowTicks = 20;
				IncludeEs = true;
				EsInstrument = "ES 12-26";
				EsTicksPerRow = 4;
				HtfCompositeDays = 60;   // v2.3: about 3 months (was 20)
				HtfMinDays = 40;         // v2.3: about 2 months (was 10)
				HtfFromMinuteBars = true;
				HtfLoadDays = 100;
				HtfTradingHours = "CME US Index Futures ETH";
				HtfMinMinutesPerDay = 900;
				HtfManualMaxAgeDays = 14;
				IncludeHtfInZones = true;
				HtfLevels = "";
				SwingAnchorDays = 10;

				// 5. Output
				WriteFiles = true;
				OutputFolder = @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\zones";   // v2.2
				PrintPasteLine = true;

				// 6. Display
				ShowZones = true;
				ShowTargetZones = true;
				ShowLevelLines = true;
				ShowStatusPanel = true;
				MaxDaysDrawn = 5;
				ZoneOpacity = 15;
				ZoneBrush = Brushes.SteelBlue;
				TargetZoneBrush = Brushes.SlateGray;
				ManualZoneBrush = Brushes.MediumPurple;
				LevelBrush = Brushes.LightSteelBlue;
			}
			else if (State == State.Configure)
			{
				AddDataSeries(BarsPeriodType.Tick, 1);
				tickIdx = 1;
				int next = 2;
				if (IncludeDeltaProfile)
				{
					AddVolumetric(Instrument != null ? Instrument.FullName : null, BarsPeriodType.Minute, 1, VolumetricDeltaType.BidAsk, 1);
					volIdx = next++;
				}
				if (IncludeEs && !string.IsNullOrWhiteSpace(EsInstrument))
				{
					AddDataSeries(EsInstrument.Trim(), BarsPeriodType.Minute, 1);
					esIdx = next++;
				}
				// v2.3: 1-minute bars of the chart instrument for the 2-3 month HTF composite, loaded independently of the
				// chart's Days to load (barsToLoad overload). Approximate volume at price.
				if (HtfFromMinuteBars && Instrument != null)
				{
					AddDataSeries(Instrument.FullName, new BarsPeriod { BarsPeriodType = BarsPeriodType.Minute, Value = 1 },
						Math.Max(1, HtfLoadDays) * 1000, string.IsNullOrWhiteSpace(HtfTradingHours) ? null : HtfTradingHours.Trim(), false);
					htfIdx = next++;
				}
			}
			else if (State == State.DataLoaded)
			{
				tickSize = Instrument != null ? Instrument.MasterInstrument.TickSize : 0.25;
				instrumentToken = SafeToken(Instrument != null ? Instrument.FullName : "NA");
				labelFont = new SimpleFont("Arial", 10);
				localTz = NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo;
				try { centralTz = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time"); }
				catch { centralTz = localTz; lastError = "Central time zone not found; using the chart time zone."; }

				asOfMin = ParseHhmm(AsOfCT, 8 * 60 + 20);
				cashStartMin = ParseHhmm(CashStartCT, 8 * 60 + 30);
				cashEndMin = ParseHhmm(CashEndCT, 15 * 60);
				sessionStartMin = ParseHhmm(SessionStartCT, 17 * 60);
				settleMin = ParseHhmm(SettlementCT, 15 * 60);
				DateTime bf;
				if (!string.IsNullOrWhiteSpace(BuildFromDate)
					&& DateTime.TryParseExact(BuildFromDate.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out bf))
					buildFromDate = bf.Date;
				ParseManualZones();
				ParseHolidays();
				ParseHalfDays();      // v2.3
				ParseHtfManual();     // v2.3

				overnight = NewProfile();
				weekly = NewProfile();

				if (volIdx > 0)
				{
					volType = BarsArray[volIdx].BarsType as NinjaTrader.NinjaScript.BarsTypes.VolumetricBarsType;
					if (volType == null) lastError = "Volumetric series unavailable (Order Flow+ needed); delta profile off.";
				}
				if (esIdx > 0 && BarsArray[esIdx].Instrument != null)
					esTickSize = BarsArray[esIdx].Instrument.MasterInstrument.TickSize;

				runStamp = DateTime.Now.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
				if (WriteFiles)
				{
					try
					{
						outFolder = string.IsNullOrWhiteSpace(OutputFolder)
							? @"G:\My Drive\NT DATA\research logs\Jeron\Preopen Exchange\zones"   // v2.2: blank = the Drive zones folder
							: OutputFolder.Trim();
						Directory.CreateDirectory(outFolder);
						pastePath = Path.Combine(outFolder, "FrozenZones_" + instrumentToken + "_run" + runStamp + ".txt");
						levelsPath = Path.Combine(outFolder, "PreopenLevels_" + instrumentToken + "_run" + runStamp + ".csv");
						File.WriteAllText(levelsPath, "Date,AsOfCT,Level,Family,Kind,Price,ZoneLo,ZoneHi,ZoneTier,ZoneLabel" + Environment.NewLine);
					}
					catch (Exception ex)
					{
						lastError = "Output folder error: " + ex.Message;
						outFolder = "";
					}
				}
			}
		}

		private PriceProfile NewProfile()
		{
			PriceProfile p = new PriceProfile();
			p.TpoRowTicks = Math.Max(1, TpoTicksPerRow);
			return p;
		}

		// ==============================================================================
		//  Bar processing
		// ==============================================================================
		protected override void OnBarUpdate()
		{
			if (BarsInProgress == tickIdx)
			{
				if (CurrentBars[tickIdx] < 0) return;
				ProcessTick(ToCentral(Times[tickIdx][0]), Closes[tickIdx][0], (long)Volumes[tickIdx][0]);
				return;
			}
			if (volIdx > 0 && BarsInProgress == volIdx)
			{
				if (CurrentBars[volIdx] >= 0 && volType != null) ProcessVolumetric();
				return;
			}
			if (esIdx > 0 && BarsInProgress == esIdx)
			{
				if (CurrentBars[esIdx] >= 0) ProcessEs();
				return;
			}
			if (htfIdx > 0 && BarsInProgress == htfIdx)
			{
				if (CurrentBars[htfIdx] >= 0) ProcessHtfMinute();   // v2.3
				return;
			}
			if (BarsInProgress != 0 || CurrentBars[0] < 1) return;
			DrawPending();

			if (ShowStatusPanel)
			{
				bool draw = State == State.Historical ? CurrentBars[0] >= BarsArray[0].Count - 2 : (DateTime.Now - lastStatusDraw).TotalSeconds >= 2;
				if (draw)
				{
					lastStatusDraw = DateTime.Now;
					Draw.TextFixed(this, "JPM_status", BuildStatus(), TextPosition.TopLeft, Brushes.Gainsboro,
						new SimpleFont("Consolas", 11), Brushes.Transparent, Brushes.Black, 60);
				}
			}
		}

		private void ProcessTick(DateTime ct, double price, long size)
		{
			if (size <= 0) return;
			if (firstTickCt == DateTime.MinValue) firstTickCt = ct;
			if (lastTickCt != DateTime.MinValue) CheckGap(lastTickCt, ct);
			lastTickCt = ct;

			DateTime td = TradingDateOf(ct);
			if (td != curTradingDate) StartTradingDate(td);

			// freeze: the first tick at or after the as-of time builds the map from earlier data only
			if (!builtToday && ct >= td.AddMinutes(asOfMin))
			{
				builtToday = true;
				if (buildFromDate == DateTime.MinValue || td >= buildFromDate) BuildMap(td);
			}

			long key = (long)Math.Round(price / tickSize);
			long period = (long)Math.Floor((ct - Epoch).TotalMinutes / 30.0);
			DateTime cashStart = td.AddMinutes(cashStartMin);
			DateTime cashEnd = td.AddMinutes(CashEndMinFor(td));    // v2.3 half days
			DateTime settleAt = td.AddMinutes(SettleMinFor(td));

			if (ct >= cashStart && ct < cashEnd)
			{
				today.Cash.AddTick(key, price, size, ct, period);
				if (double.IsNaN(today.CashOpen)) today.CashOpen = price;
			}
			if (ct < cashStart)
			{
				overnight.AddTick(key, price, size, ct, period);
				if (double.IsNaN(onOpen)) onOpen = price;
				if (price > onRunHigh) onRunHigh = price;
				if (price < onRunLow) onRunLow = price;
				if (onRunHigh - price > onMaxDrawFromHigh) onMaxDrawFromHigh = onRunHigh - price;
				if (price - onRunLow > onMaxRallyFromLow) onMaxRallyFromLow = price - onRunLow;
				onVolTotal += size;
				if (!double.IsNaN(onSettleRef) && price > onSettleRef) onVolAboveSettle += size;
			}
			weekly.AddTick(key, price, size, ct, period);

			// day stats (whole trading day)
			if (double.IsNaN(today.Open)) today.Open = price;
			if (price > today.High) today.High = price;
			if (price < today.Low) today.Low = price;
			today.Last = price;
			long hrow = FloorDiv(key, Math.Max(1, HvnTicksPerRow));
			long hv;
			today.Rows.TryGetValue(hrow, out hv);
			today.Rows[hrow] = hv + size;
			if (ct < settleAt)
			{
				today.PreSettleLast = price;
				if (ct >= settleAt.AddSeconds(-30)) { today.SettlePv += price * size; today.SettleV += size; }
			}

			// hourly bars (clock hours, CT)
			DateTime hk = new DateTime(ct.Year, ct.Month, ct.Day, ct.Hour, 0, 0);
			HourBar hb = hours.Count > 0 ? hours[hours.Count - 1] : null;
			if (hb == null || hb.HourCt != hk)
			{
				hb = new HourBar();
				hb.HourCt = hk;
				hb.O = price; hb.H = price; hb.L = price;
				hours.Add(hb);
				if (hours.Count > 24 * 40) hours.RemoveAt(0);
			}
			if (price > hb.H) hb.H = price;
			if (price < hb.L) hb.L = price;
			hb.C = price;
			hb.V += size;
			if (hb.Rows == null) hb.Rows = new Dictionary<long, long>();
			long hbv;
			hb.Rows.TryGetValue(hrow, out hbv);
			hb.Rows[hrow] = hbv + size;

			vwSumPv += price * size;
			vwSumP2v += price * price * size;
			vwSumV += size;
			wkPv += price * size;
			wkV += size;
			lastPrice = price;
		}

		private void StartTradingDate(DateTime td)
		{
			if (today != null && today.High > double.MinValue)
			{
				days[today.Date] = today;
				List<DateTime> old = new List<DateTime>();
				foreach (DateTime d in days.Keys) if (d < td.AddDays(-Math.Max(10, KeepTickDays))) old.Add(d);   // v2.3 setting (was 45)
				foreach (DateTime d in old) days.Remove(d);
			}
			gaps.RemoveAll(delegate(DataGap g) { return g.End < td.AddDays(-Math.Max(10, KeepTickDays)); });

			curTradingDate = td;
			builtToday = false;
			today = new DayStats();
			today.Date = td;
			today.Cash = NewProfile();

			overnight = NewProfile();
			vwSumPv = 0; vwSumP2v = 0; vwSumV = 0;
			onOpen = double.NaN; onRunHigh = double.MinValue; onRunLow = double.MaxValue;
			onMaxDrawFromHigh = 0; onMaxRallyFromLow = 0; onVolAboveSettle = 0; onVolTotal = 0;
			DayStats pd;
			onSettleRef = days.TryGetValue(PrevTradingDate(td), out pd) ? SettleOf(pd) : double.NaN;

			DateTime monday = td.AddDays(-(((int)td.DayOfWeek + 6) % 7));
			if (monday != curWeekMonday)
			{
				if (weekly != null && !weekly.Empty && curWeekMonday != DateTime.MinValue)
				{
					priorWeek = weekly;
					priorWeekMonday = curWeekMonday;
				}
				curWeekMonday = monday;
				weekly = NewProfile();
				wkPv = 0; wkV = 0;
			}
		}

		private double SettleOf(DayStats d)
		{
			if (d == null) return double.NaN;
			if (d.SettleV > 0) return RoundTick(d.SettlePv / d.SettleV);
			return d.PreSettleLast;
		}

		private void ProcessVolumetric()
		{
			DateTime ct = ToCentral(Times[volIdx][0]);
			DateTime barStart = ct.AddSeconds(-1);
			DateTime td = TradingDateOf(barStart);
			DateTime cashStart = td.AddMinutes(cashStartMin), cashEnd = td.AddMinutes(CashEndMinFor(td)), asOf = td.AddMinutes(asOfMin);
			Dictionary<DateTime, Dictionary<long, long[]>> target = null;
			if (barStart >= cashStart && barStart < cashEnd) target = cashDelta;
			else if (barStart < cashStart && ct <= asOf) target = onDelta;
			if (target == null) return;
			Dictionary<long, long[]> rows;
			if (!target.TryGetValue(td, out rows)) { rows = new Dictionary<long, long[]>(); target[td] = rows; }
			var vd = volType.Volumes[CurrentBars[volIdx]];
			double lo = Lows[volIdx][0], hi = Highs[volIdx][0];
			int n = (int)Math.Round((hi - lo) / tickSize);
			int rt = Math.Max(1, DeltaRowTicks);
			for (int i = 0; i <= n; i++)
			{
				double p = lo + i * tickSize;
				long ask = vd.GetAskVolumeForPrice(p), bid = vd.GetBidVolumeForPrice(p);
				if (ask == 0 && bid == 0) continue;
				long row = FloorDiv((long)Math.Round(p / tickSize), rt);
				long[] cell;
				if (!rows.TryGetValue(row, out cell)) { cell = new long[2]; rows[row] = cell; }
				cell[0] += ask - bid;
				cell[1] += ask + bid;
			}
			if (target == onDelta) deltaThroughCt = ct;
			PruneOld(cashDelta, td);
			PruneOld(onDelta, td);
		}

		private static void PruneOld(Dictionary<DateTime, Dictionary<long, long[]>> dict, DateTime td)
		{
			List<DateTime> old = new List<DateTime>();
			foreach (DateTime d in dict.Keys) if (d < td.AddDays(-10)) old.Add(d);
			foreach (DateTime d in old) dict.Remove(d);
		}

		private void ProcessEs()
		{
			DateTime ct = ToCentral(Times[esIdx][0]);
			DateTime barStart = ct.AddSeconds(-1);
			DateTime td = TradingDateOf(barStart);
			if (td != esCurTd)
			{
				if (esToday != null) esDays[esToday.Date] = esToday;
				esToday = new EsDay();
				esToday.Date = td;
				esCurTd = td;
				esOnHigh = double.MinValue; esOnLow = double.MaxValue; esPv = 0; esV = 0;
				List<DateTime> old = new List<DateTime>();
				foreach (DateTime d in esDays.Keys) if (d < td.AddDays(-20)) old.Add(d);
				foreach (DateTime d in old) esDays.Remove(d);
			}
			double o = Opens[esIdx][0], h = Highs[esIdx][0], l = Lows[esIdx][0], c = Closes[esIdx][0], v = Volumes[esIdx][0];
			DateTime cashStart = td.AddMinutes(cashStartMin), cashEnd = td.AddMinutes(CashEndMinFor(td)), settleAt = td.AddMinutes(SettleMinFor(td));
			if (barStart < cashStart)
			{
				if (h > esOnHigh) esOnHigh = h;
				if (l < esOnLow) esOnLow = l;
			}
			if (barStart >= cashStart && barStart < cashEnd)
			{
				if (h > esToday.CashHigh) esToday.CashHigh = h;
				if (l < esToday.CashLow) esToday.CashLow = l;
				// approximate profile: spread the minute's volume evenly over its range
				int rt = Math.Max(1, EsTicksPerRow);
				long r0 = FloorDiv((long)Math.Round(l / esTickSize), rt), r1 = FloorDiv((long)Math.Round(h / esTickSize), rt);
				double share = v / (double)(r1 - r0 + 1);
				for (long r = r0; r <= r1; r++)
				{
					double cur;
					esToday.Rows.TryGetValue(r, out cur);
					esToday.Rows[r] = cur + share;
				}
				esToday.RowTotal += v;
			}
			if (ct <= settleAt) esToday.Settle = c;   // close of the minute ending at the settlement time (approx)
			esToday.Last = c;
			esPv += (h + l + c) / 3.0 * v;
			esV += v;
			esLast = c;
			esThroughCt = ct;

			DateTime hk = new DateTime(barStart.Year, barStart.Month, barStart.Day, barStart.Hour, 0, 0);
			HourBar hb = esHours.Count > 0 ? esHours[esHours.Count - 1] : null;
			if (hb == null || hb.HourCt != hk)
			{
				hb = new HourBar();
				hb.HourCt = hk;
				hb.O = o; hb.H = h; hb.L = l;
				esHours.Add(hb);
				if (esHours.Count > 24 * 10) esHours.RemoveAt(0);
			}
			if (h > hb.H) hb.H = h;
			if (l < hb.L) hb.L = l;
			hb.C = c;
			hb.V += (long)v;
		}

		// v2.3: 1-minute bars for the HTF composite. Each minute's volume is spread evenly over its range at HVN rows.
		private void ProcessHtfMinute()
		{
			DateTime ct = ToCentral(Times[htfIdx][0]);
			DateTime barStart = ct.AddSeconds(-1);
			DateTime td = TradingDateOf(barStart);
			double h = Highs[htfIdx][0], l = Lows[htfIdx][0], v = Volumes[htfIdx][0];
			if (v <= 0 || h < l) return;
			Dictionary<long, double> rows;
			if (!htfMinDays.TryGetValue(td, out rows))
			{
				rows = new Dictionary<long, double>();
				htfMinDays[td] = rows;
				List<DateTime> old = new List<DateTime>();
				foreach (DateTime d in htfMinDays.Keys) if (d < td.AddDays(-(Math.Max(1, HtfLoadDays) + 40))) old.Add(d);
				foreach (DateTime d in old) { htfMinDays.Remove(d); htfMinCount.Remove(d); }
			}
			int rt = Math.Max(1, HvnTicksPerRow);
			long r0 = FloorDiv((long)Math.Round(l / tickSize), rt), r1 = FloorDiv((long)Math.Round(h / tickSize), rt);
			double share = v / (double)(r1 - r0 + 1);
			for (long r = r0; r <= r1; r++)
			{
				double cur;
				rows.TryGetValue(r, out cur);
				rows[r] = cur + share;
			}
			int n;
			htfMinCount.TryGetValue(td, out n);
			htfMinCount[td] = n + 1;
			htfThroughCt = ct;
		}

		private int CashEndMinFor(DateTime td)
		{
			int m;
			return halfDays.TryGetValue(td.Date, out m) ? m : cashEndMin;
		}

		private int SettleMinFor(DateTime td)
		{
			int m;
			return halfDays.TryGetValue(td.Date, out m) ? m : settleMin;
		}

		// When the daily maintenance break starts: 16:00 CT normally, 15 minutes after the early close on a half day.
		private DateTime BreakStartCt(DateTime td)
		{
			int m;
			return halfDays.TryGetValue(td.Date, out m) ? td.AddMinutes(m + 15) : td.AddMinutes(sessionStartMin - 60);
		}

		private void ParseHalfDays()
		{
			halfDays.Clear();
			if (string.IsNullOrWhiteSpace(HalfDayDates)) return;
			foreach (string raw in HalfDayDates.Split(new char[] { ';', ',', ' ', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries))
			{
				string e = raw.Trim();
				int at = e.IndexOf('@');
				string dText = at > 0 ? e.Substring(0, at) : e;
				int end = at > 0 ? ParseHhmm(e.Substring(at + 1), -1) : 12 * 60;
				DateTime d;
				if (end < 0 || !DateTime.TryParseExact(dText.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d))
				{
					lastError = "Could not parse half-day date '" + raw + "' (use yyyy-MM-dd@HH:mm)";
					continue;
				}
				halfDays[d.Date] = end;
			}
		}

		// Ticks from the session start (17:00 CT) onward belong to the next trading date.
		private DateTime TradingDateOf(DateTime ct)
		{
			DateTime d = ct.Date;
			if (ct.TimeOfDay.TotalMinutes >= sessionStartMin) d = d.AddDays(1);
			if (d.DayOfWeek == DayOfWeek.Saturday) d = d.AddDays(2);
			else if (d.DayOfWeek == DayOfWeek.Sunday) d = d.AddDays(1);
			return d;
		}

		private DateTime SessionStartCt(DateTime td)
		{
			return td.AddDays(-1).AddMinutes(sessionStartMin);   // Monday -> Sunday 17:00
		}

		private DateTime PrevTradingDate(DateTime td)
		{
			DateTime d = td.AddDays(-1);
			for (int guard = 0; guard < 14; guard++)
			{
				if (d.DayOfWeek != DayOfWeek.Saturday && d.DayOfWeek != DayOfWeek.Sunday && !holidays.Contains(d)) return d;
				d = d.AddDays(-1);
			}
			return d;
		}

		private void CheckGap(DateTime prev, DateTime cur)
		{
			double tol = Math.Max(1, MaxTickGapMinutes);
			if ((cur - prev).TotalMinutes <= tol) return;
			DateTime tdCur = TradingDateOf(cur);
			DateTime open = SessionStartCt(tdCur);
			DateTime breakStart = BreakStartCt(PrevTradingDate(tdCur));   // v2.3: 16:00 CT, or 15 min after a half day's early close
			bool normalBreak = prev >= breakStart.AddMinutes(-tol) && cur <= open.AddMinutes(tol);
			if (normalBreak) return;
			DataGap g = new DataGap();
			g.Start = prev;
			g.End = cur;
			gaps.Add(g);
		}

		private bool Covered(DateTime ws, DateTime we, out string reason)
		{
			reason = "";
			double tol = Math.Max(1, MaxTickGapMinutes);
			if (firstTickCt == DateTime.MinValue || firstTickCt > ws.AddMinutes(tol))
			{
				reason = "data starts " + JTime(firstTickCt);
				return false;
			}
			foreach (DataGap g in gaps)
			{
				DateTime a = g.Start > ws ? g.Start : ws;
				DateTime b = g.End < we ? g.End : we;
				if ((b - a).TotalMinutes > tol)
				{
					reason = "data gap " + JTime(g.Start) + " to " + JTime(g.End);
					return false;
				}
			}
			return true;
		}

		// ==============================================================================
		//  Map building
		// ==============================================================================
		private void BuildMap(DateTime td)
		{
			DayMap m = new DayMap();
			m.Date = td;
			m.AsOfCt = td.AddMinutes(asOfMin);
			m.CashEndCt = td.AddMinutes(CashEndMinFor(td));
			if (halfDays.ContainsKey(td)) m.Notes.Add("CALENDAR: half day today, cash session ends " + MinText(CashEndMinFor(td)) + " CT (prompt check F: LOG_ONLY)");
			m.RefPrice = lastPrice;
			string why;
			List<string> sessionJson = new List<string>();

			// 1. prior cash sessions by calendar (a missing day keeps its slot)
			DateTime pd = td;
			DayStats pdStats = null;
			List<double[]> vaByK = new List<double[]>();   // [poc, vah, val] for PD, PD2, PD3 (NaN when missing)
			List<double[]> hlByK = new List<double[]>();   // v2.1: [cash high, cash low] for the same slots
			DayStats pd2Stats = null;                        // v2.3 balance merge
			bool pd2Ok = false;
			for (int k = 1; k <= Math.Max(PriorCashSessions, 3); k++)
			{
				pd = PrevTradingDate(pd);
				string p = k == 1 ? "PD" : "PD" + k.ToString(CultureInfo.InvariantCulture);
				string dText = pd.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
				DayStats ds;
				double[] va = new double[] { double.NaN, double.NaN, double.NaN };
				if (!days.TryGetValue(pd, out ds) || ds.Cash == null || ds.Cash.Empty)
				{
					m.Notes.Add("DATA: " + p + " (" + dText + ") has no cash-session data; " + p + " levels left out. If the market was closed that day, add it to Holiday dates.");
					vaByK.Add(va);
					hlByK.Add(new double[] { double.NaN, double.NaN });
					continue;
				}
				if (k == 1) pdStats = ds;
				bool ok = Covered(pd.AddMinutes(cashStartMin), pd.AddMinutes(CashEndMinFor(pd)), out why);
				if (!ok && SkipPartialProfiles)
				{
					m.Notes.Add("DATA: " + p + " (" + dText + ") left out: " + why);
					vaByK.Add(va);
					hlByK.Add(new double[] { double.NaN, double.NaN });
					continue;
				}
				if (!ok) m.Notes.Add("DATA: " + p + " (" + dText + ") built from incomplete data: " + why);
				bool inZones = k <= PriorCashSessions;
				double poc, vah, val;
				if (VolumeVa(ds.Cash, out poc, out vah, out val))
				{
					va = new double[] { poc, vah, val };
					if (inZones) AddVa(m, p, p, "VP", poc, vah, val);
				}
				double tpoc = double.NaN, tvah = double.NaN, tval = double.NaN;
				if (IncludeTpo && TpoVa(ds.Cash, out tpoc, out tvah, out tval) && inZones)
					AddVa(m, p + "T", p, "TPO", tpoc, tvah, tval);
				if (IncludeTpo && k == 1) AddSinglePrints(m, ds.Cash, "TPO_PD");
				if (k == 1 && IncludePriorDayHighLow)
				{
					AddLevel(m, "PDH", "PD", "HL", ds.Cash.High, true);
					AddLevel(m, "PDL", "PD", "HL", ds.Cash.Low, true);
				}
				// v2.3: PD2 / PD3 cash high and low (the extremes of the merged balance Jeron trades)
				if (k >= 2 && inZones && IncludePriorHighLowAll)
				{
					AddLevel(m, p + "H", p, "HL", ds.Cash.High, true);
					AddLevel(m, p + "L", p, "HL", ds.Cash.Low, true);
				}
				if (k == 2) { pd2Stats = ds; pd2Ok = ok; }
				// v2.3: settlement family SET (own independent period, default) or PD (same period as the prior day)
				if (k == 1 && IncludeSettlement)
					AddLevel(m, "PDSET", (SettlementFamily ?? "SET").Trim().ToUpperInvariant() == "PD" ? "PD" : "SET", "SET", SettleOf(ds), true);
				vaByK.Add(va);
				hlByK.Add(new double[] { ds.Cash.High, ds.Cash.Low });
				sessionJson.Add(SessionJson(p, ds, va, tpoc, tvah, tval, ok));
			}

			// 2. overnight and session VWAP
			bool sessionCovered = Covered(SessionStartCt(td), m.AsOfCt, out why);
			if (!sessionCovered) m.Notes.Add("DATA: overnight/VWAP window " + (SkipPartialProfiles ? "left out: " : "incomplete: ") + why);
			bool useSession = sessionCovered || !SkipPartialProfiles;
			double onPoc = double.NaN, onVah = double.NaN, onVal = double.NaN;
			if (IncludeOvernight && useSession && !overnight.Empty)
			{
				if (VolumeVa(overnight, out onPoc, out onVah, out onVal)) AddVa(m, "ON", "ON", "VP", onPoc, onVah, onVal);
				double a, b, c;
				if (IncludeTpo && TpoVa(overnight, out a, out b, out c)) AddVa(m, "ONT", "ON", "TPO", a, b, c);
				if (IncludeTpo) AddSinglePrints(m, overnight, "TPO_ON");
				if (IncludeOvernightHighLow)
				{
					AddLevel(m, "ONH", "ON", "HL", overnight.High, true);
					AddLevel(m, "ONL", "ON", "HL", overnight.Low, true);
				}
			}
			double vw = double.NaN, sd = double.NaN;
			if (useSession && vwSumV > 0)
			{
				vw = vwSumPv / vwSumV;
				sd = Math.Sqrt(Math.Max(0, vwSumP2v / vwSumV - vw * vw));
				if (IncludeVwap)
				{
					AddLevel(m, "VWAP", "VWAP", "VWAP", vw, IncludeVwapInZones);
					if (IncludeVwapBand1) { AddLevel(m, "VWAPU1", "VWAP", "VWAP", vw + sd, IncludeVwapInZones); AddLevel(m, "VWAPL1", "VWAP", "VWAP", vw - sd, IncludeVwapInZones); }
					if (IncludeVwapBand2) { AddLevel(m, "VWAPU2", "VWAP", "VWAP", vw + 2 * sd, IncludeVwapInZones); AddLevel(m, "VWAPL2", "VWAP", "VWAP", vw - 2 * sd, IncludeVwapInZones); }
				}
			}

			// 3. developing week, prior week, weekly VWAP
			double wkPocV = double.NaN, wkVahV = double.NaN, wkValV = double.NaN;
			bool weekCovered = Covered(SessionStartCt(curWeekMonday), m.AsOfCt, out why);
			if (IncludeWeekly && !weekly.Empty)
			{
				if (weekCovered || !SkipPartialProfiles)
				{
					if (VolumeVa(weekly, out wkPocV, out wkVahV, out wkValV)) AddVa(m, "WK", "WK", "VP", wkPocV, wkVahV, wkValV);
					double a, b, c;
					if (IncludeTpo && TpoVa(weekly, out a, out b, out c)) AddVa(m, "WKT", "WK", "TPO", a, b, c);
					if (IncludeTpo) AddSinglePrints(m, weekly, "TPO_WK");
				}
				if (!weekCovered) m.Notes.Add("DATA: weekly profile " + (SkipPartialProfiles ? "left out: " : "incomplete: ") + why);
			}
			double wvwap = wkV > 0 && (weekCovered || !SkipPartialProfiles) ? wkPv / wkV : double.NaN;
			if (!double.IsNaN(wvwap)) AddLevel(m, "WVWAP", "WVWAP", "VWAP", wvwap, IncludeWeeklyVwapInZones);
			double pwPoc = double.NaN, pwVah = double.NaN, pwVal = double.NaN;
			if (IncludePriorWeek)
			{
				DateTime expectedMonday = curWeekMonday.AddDays(-7);
				if (priorWeek == null || priorWeek.Empty || priorWeekMonday != expectedMonday)
					m.Notes.Add("DATA: prior-week profile unavailable (load data from " + SessionStartCt(expectedMonday).ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + " CT)");
				else
				{
					bool pwOk = Covered(SessionStartCt(expectedMonday), priorWeek.LastCt, out why);
					if (!pwOk) m.Notes.Add("DATA: prior-week profile " + (SkipPartialProfiles ? "left out: " : "incomplete: ") + why);
					if (pwOk || !SkipPartialProfiles)
					{
						if (VolumeVa(priorWeek, out pwPoc, out pwVah, out pwVal)) AddVa(m, "PWK", "PWK", "VP", pwPoc, pwVah, pwVal);
						double a, b, c;
						if (IncludeTpo && TpoVa(priorWeek, out a, out b, out c)) AddVa(m, "PWKT", "PWK", "TPO", a, b, c);
						if (IncludeTpo) AddSinglePrints(m, priorWeek, "TPO_PWK");
						AddLevel(m, "PWKH", "PWK", "HL", priorWeek.High, true);
						AddLevel(m, "PWKL", "PWK", "HL", priorWeek.Low, true);
					}
				}
			}

			// 4. composite HVN / LVN
			List<string> compDates = new List<string>();
			Dictionary<long, long> comp = CompositeRows(td, compDates);
			AddHvnLvn(m, comp);

			// 4b. v2.1 higher-timeframe composite (Part 2 ~4:02 three-month composite, Part 3 ~7:00 two-month composite).
			// Built from the loaded days (max 44); levels join the zones only with HtfMinDays+ days. Manual HTF levels
			// (e.g. a 2-3 month TradingView composite) are added as family HTF as well.
			List<string> htfDates = new List<string>();
			string htfSource;
			Dictionary<long, long> htf = HtfRows(td, htfDates, out htfSource);
			double hPoc = double.NaN, hVah = double.NaN, hVal = double.NaN;
			bool htfOk = htfDates.Count >= Math.Max(1, HtfMinDays);
			List<Area> htfAreas = new List<Area>();
			if (htf.Count > 0 && VaFromRows(htf, Math.Max(1, HvnTicksPerRow), out hPoc, out hVah, out hVal))
			{
				htfAreas = HvnLvnAreas(htf, "HTF");
				if (htfOk)
				{
					AddLevel(m, "HTFVAH", "HTF", "VP", hVah, IncludeHtfInZones);
					AddLevel(m, "HTFPOC", "HTF", "VP", hPoc, IncludeHtfInZones);
					AddLevel(m, "HTFVAL", "HTF", "VP", hVal, IncludeHtfInZones);
					m.Areas.AddRange(htfAreas);
				}
			}
			if (!htfOk)
				m.Notes.Add("DATA: HTF composite has " + htfDates.Count.ToString(CultureInfo.InvariantCulture) + " day(s) (< " + HtfMinDays.ToString(CultureInfo.InvariantCulture)
					+ "); left out of the zones. Load more days or paste HTF levels.");
			string htfManualJson = ApplyHtfManual(m, td);   // v2.3 dated manual HTF levels

			// 5. distance filter
			if (MaxDistancePoints > 0 && !double.IsNaN(m.RefPrice))
			{
				int before = m.Levels.Count;
				m.Levels.RemoveAll(delegate(Level l) { return Math.Abs(l.Price - m.RefPrice) > MaxDistancePoints; });
				if (m.Levels.Count < before)
					m.Notes.Add((before - m.Levels.Count).ToString(CultureInfo.InvariantCulture) + " level(s) beyond " + JN(MaxDistancePoints, 0) + " pts from " + JN(m.RefPrice, 2) + " dropped");
			}

			// 6. zones, tiers, manual zones
			List<Level> zoneLevels = new List<Level>();
			foreach (Level l in m.Levels) if (l.InZones) zoneLevels.Add(l);
			m.Zones = Cluster(zoneLevels, m.Areas);
			foreach (ManualDef md in manualDefs)
			{
				if (md.HasDate && md.Date != td) continue;
				Zone z = new Zone();
				z.Lo = md.Lo; z.Hi = md.Hi; z.MinLevel = md.Lo; z.MaxLevel = md.Hi;
				z.Label = md.Label; z.Manual = true; z.Tier = "MANUAL"; z.Sources = 0;
				m.Zones.Add(z);
			}
			m.Zones.Sort(delegate(Zone a, Zone b) { return a.Lo.CompareTo(b.Lo); });

			// 7. review packet
			if (WritePacket)
			{
				// v2.1 extra packet sections
				List<string> extra = new List<string>();
				extra.Add(KV("value_vs_price", ValueVsPriceJson(vaByK, hlByK)));
				extra.Add(KV("pd_on_composite", PdOnJson(pdStats, useSession, m.RefPrice)));
				extra.Add(KV("ranges", RangesJson(td, pdStats, m.RefPrice)));
				extra.Add(KV("htf_composite", Obj(KV("days_used", htfDates.Count.ToString(CultureInfo.InvariantCulture)), KV("in_zones", htfOk && IncludeHtfInZones ? "true" : "false"),
					KV("vah", Num(hVah)), KV("poc", Num(hPoc)), KV("val", Num(hVal)), KV("location", Q(VaPos(m.RefPrice, new double[] { hPoc, hVah, hVal }))),
					KV("areas", AreasJson(htfAreas)), KV("manual_levels", Q(HtfLevels ?? "")),
					KV("source", Q(htfSource)), KV("first_day", Q(htfDates.Count > 0 ? htfDates[htfDates.Count - 1] : "")),
					KV("minute_through_ct", Q(JTime(htfThroughCt))), KV("manual", htfManualJson))));
				// v2.3
				extra.Add(KV("balance_composite", BalanceJson(pd2Stats, pd2Ok, pdStats, useSession, m.RefPrice)));
				extra.Add(KV("double_distribution", DoubleDistJson(pdStats, m)));
				extra.Add(KV("calendar", Obj(KV("half_day_today", halfDays.ContainsKey(td) ? "true" : "false"),
					KV("pd_half_day", pdStats != null && halfDays.ContainsKey(pdStats.Date) ? "true" : "false"),
					KV("cash_end_ct_today", Q(MinText(CashEndMinFor(td)))),
					KV("settlement_family", Q((SettlementFamily ?? "SET").Trim().ToUpperInvariant() == "PD" ? "PD" : "SET")))));
				extra.Add(KV("swing_profile", SwingProfileJson(td, m.AsOfCt, m.RefPrice)));
				extra.Add(KV("overnight_distribution", OnDistributionJson(useSession)));
				m.PacketJson = BuildPacket(m, sessionJson, vaByK, onPoc, onVah, onVal, vw, sd, wvwap, wkPocV, wkVahV, wkValV, pwPoc, pwVah, pwVal, pdStats, compDates, extra);
			}

			maps.Add(m);
			WriteOutputs(m);
		}

		private void AddLevel(DayMap m, string name, string family, string kind, double price, bool inZones)
		{
			if (double.IsNaN(price) || double.IsInfinity(price) || price <= 0 || price == double.MaxValue) return;
			Level l = new Level();
			l.Name = name; l.Family = family; l.Kind = kind; l.Price = RoundTick(price); l.InZones = inZones;
			m.Levels.Add(l);
		}

		private void AddVa(DayMap m, string prefix, string family, string kind, double poc, double vah, double val)
		{
			AddLevel(m, prefix + "VAH", family, kind, vah, true);
			AddLevel(m, prefix + "POC", family, kind, poc, true);
			AddLevel(m, prefix + "VAL", family, kind, val, true);
		}

		private bool VolumeVa(PriceProfile p, out double poc, out double vah, out double val)
		{
			Dictionary<long, long> rows = new Dictionary<long, long>();
			int tpr = Math.Max(1, TicksPerRow);
			foreach (KeyValuePair<long, long> kv in p.Vol)
			{
				long r = FloorDiv(kv.Key, tpr), cur;
				rows.TryGetValue(r, out cur);
				rows[r] = cur + kv.Value;
			}
			return VaFromRows(rows, tpr, out poc, out vah, out val);
		}

		private bool TpoVa(PriceProfile p, out double poc, out double vah, out double val)
		{
			return VaFromRows(p.Tpo, Math.Max(1, TpoTicksPerRow), out poc, out vah, out val);
		}

		// Standard value area on rows (key = row index, row = rowTicks ticks): start at the POC row and add the
		// larger neighbouring row (above wins ties) until ValueAreaPct is inside. POC ties: nearest the middle.
		private bool VaFromRows(Dictionary<long, long> src, int rowTicks, out double poc, out double vah, out double val)
		{
			poc = vah = val = double.NaN;
			if (src == null || src.Count == 0) return false;
			long minRow = long.MaxValue, maxRow = long.MinValue, total = 0;
			foreach (KeyValuePair<long, long> kv in src)
			{
				if (kv.Key < minRow) minRow = kv.Key;
				if (kv.Key > maxRow) maxRow = kv.Key;
				total += kv.Value;
			}
			if (total <= 0) return false;
			int n = (int)(maxRow - minRow + 1);
			long[] rows = new long[n];
			foreach (KeyValuePair<long, long> kv in src) rows[(int)(kv.Key - minRow)] += kv.Value;

			int pocIdx = 0;
			double mid = (n - 1) / 2.0;
			for (int i = 1; i < n; i++)
				if (rows[i] > rows[pocIdx] || (rows[i] == rows[pocIdx] && Math.Abs(i - mid) < Math.Abs(pocIdx - mid))) pocIdx = i;

			double target = total * Math.Max(1, Math.Min(100, ValueAreaPct)) / 100.0;
			int lo = pocIdx, hi = pocIdx;
			double acc = rows[pocIdx];
			while (acc < target && (lo > 0 || hi < n - 1))
			{
				long up = hi + 1 < n ? rows[hi + 1] : -1;
				long dn = lo - 1 >= 0 ? rows[lo - 1] : -1;
				if (up >= dn) { hi++; acc += up; }
				else { lo--; acc += dn; }
			}
			double span = (rowTicks - 1) * tickSize;
			val = (minRow + lo) * rowTicks * tickSize;
			vah = (minRow + hi) * rowTicks * tickSize + span;
			poc = RoundTick((minRow + pocIdx) * rowTicks * tickSize + span / 2.0);
			return true;
		}

		// Single prints: runs of TPO rows touched by exactly one 30-minute period (at least MinSinglePrintRows rows).
		private void AddSinglePrints(DayMap m, PriceProfile p, string source)
		{
			if (p == null || p.Tpo.Count == 0) return;
			long minRow = long.MaxValue, maxRow = long.MinValue;
			foreach (long r in p.Tpo.Keys) { if (r < minRow) minRow = r; if (r > maxRow) maxRow = r; }
			int rt = Math.Max(1, TpoTicksPerRow);
			long runStart = long.MinValue;
			for (long r = minRow; r <= maxRow + 1; r++)
			{
				long c;
				bool single = r <= maxRow && p.Tpo.TryGetValue(r, out c) && c == 1;
				if (single && runStart == long.MinValue) runStart = r;
				if (!single && runStart != long.MinValue)
				{
					long len = r - runStart;
					if (len >= Math.Max(1, MinSinglePrintRows))
					{
						Area a = new Area();
						a.Type = "SP"; a.Source = source;
						a.Lo = runStart * rt * tickSize;
						a.Hi = r * rt * tickSize - tickSize;
						m.Areas.Add(a);
					}
					runStart = long.MinValue;
				}
			}
		}

		// Composite of the last CompositeDays complete trading days plus today's session up to the as-of time.
		private Dictionary<long, long> CompositeRows(DateTime td, List<string> usedDates)
		{
			Dictionary<long, long> comp = new Dictionary<long, long>();
			DateTime d = td;
			string why;
			for (int k = 0; k < Math.Max(1, CompositeDays); k++)
			{
				d = PrevTradingDate(d);
				DayStats ds;
				if (!days.TryGetValue(d, out ds)) continue;
				if (!Covered(SessionStartCt(d), BreakStartCt(d), out why)) continue;
				foreach (KeyValuePair<long, long> kv in ds.Rows) { long c; comp.TryGetValue(kv.Key, out c); comp[kv.Key] = c + kv.Value; }
				usedDates.Add(d.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture));
			}
			if (today != null)
			{
				foreach (KeyValuePair<long, long> kv in today.Rows) { long c; comp.TryGetValue(kv.Key, out c); comp[kv.Key] = c + kv.Value; }
				usedDates.Add(td.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + " to as-of");
			}
			return comp;
		}

		// HVN: rows whose 3-row smoothed volume >= HvnPct of the peak. LVN: rows <= LvnPct of the peak lying
		// between the first and last HVN (the thin areas between volume concentrations).
		private void AddHvnLvn(DayMap m, Dictionary<long, long> comp)
		{
			m.Areas.AddRange(HvnLvnAreas(comp, "COMP"));
		}

		private List<Area> HvnLvnAreas(Dictionary<long, long> comp, string source)
		{
			List<Area> res = new List<Area>();
			if (comp.Count < 5) return res;
			long minRow = long.MaxValue, maxRow = long.MinValue;
			foreach (long r in comp.Keys) { if (r < minRow) minRow = r; if (r > maxRow) maxRow = r; }
			int n = (int)(maxRow - minRow + 1);
			double[] raw = new double[n], s = new double[n];
			foreach (KeyValuePair<long, long> kv in comp) raw[(int)(kv.Key - minRow)] = kv.Value;
			double peak = 0;
			for (int i = 0; i < n; i++)
			{
				double a = i > 0 ? raw[i - 1] : 0, c = i < n - 1 ? raw[i + 1] : 0;
				s[i] = (a + raw[i] + c) / 3.0;
				if (s[i] > peak) peak = s[i];
			}
			if (peak <= 0) return res;
			double hT = peak * HvnPct / 100.0, lT = peak * LvnPct / 100.0;
			int firstH = -1, lastH = -1;
			for (int i = 0; i < n; i++) if (s[i] >= hT) { if (firstH < 0) firstH = i; lastH = i; }
			int rt = Math.Max(1, HvnTicksPerRow);
			AddRuns(res, s, minRow, rt, 0, n - 1, delegate(double x) { return x >= hT; }, "HVN", source);
			if (firstH >= 0 && lastH > firstH)
				AddRuns(res, s, minRow, rt, firstH, lastH, delegate(double x) { return x <= lT; }, "LVN", source);
			return res;
		}

		private void AddRuns(List<Area> res, double[] s, long minRow, int rt, int startIdx, int endIdx, Predicate<double> test, string type, string source)
		{
			int start = -1;
			for (int i = startIdx; i <= endIdx + 1; i++)
			{
				bool inRun = i <= endIdx && test(s[i]);
				if (inRun && start < 0) start = i;
				if (!inRun && start >= 0)
				{
					Area a = new Area();
					a.Type = type; a.Source = source;
					a.Lo = (minRow + start) * rt * tickSize;
					a.Hi = (minRow + i) * rt * tickSize - tickSize;
					res.Add(a);
					start = -1;
				}
			}
		}

		// Levels sorted by price; a level joins the current zone if within MergeDistancePoints of the zone's highest
		// level and the zone stays within MaxZoneWidthPoints. Sources = distinct independent periods (families).
		private List<Zone> Cluster(List<Level> levels, List<Area> areas)
		{
			List<Level> sorted = new List<Level>(levels);
			sorted.Sort(delegate(Level a, Level b)
			{
				int c = a.Price.CompareTo(b.Price);
				return c != 0 ? c : string.CompareOrdinal(a.Name, b.Name);
			});
			List<Zone> zones = new List<Zone>();
			Zone cur = null;
			foreach (Level l in sorted)
			{
				bool joinZone = cur != null
					&& l.Price - cur.MaxLevel <= MergeDistancePoints + 1e-9
					&& (MaxZoneWidthPoints <= 0 || l.Price - cur.MinLevel <= MaxZoneWidthPoints + 1e-9);
				if (!joinZone)
				{
					cur = new Zone();
					cur.MinLevel = l.Price;
					zones.Add(cur);
				}
				cur.MaxLevel = l.Price;
				cur.Levels.Add(l);
			}
			foreach (Zone z in zones)
			{
				z.Lo = FloorTick(z.MinLevel - ZonePadPoints);
				z.Hi = CeilTick(z.MaxLevel + ZonePadPoints);
				List<string> names = new List<string>();
				List<string> fams = new List<string>();
				bool tpo = false;
				foreach (Level l in z.Levels)
				{
					if (!names.Contains(l.Name)) names.Add(l.Name);
					if (!fams.Contains(l.Family)) fams.Add(l.Family);
					if (l.Kind == "TPO") tpo = true;
				}
				z.Sources = fams.Count;
				if (tpo) z.Tags.Add("TPO");
				z.Tier = z.Sources >= Math.Max(1, MinSourcesForDecision) ? "DECISION" : "TARGET";
				string shortNames = names.Count <= 6 ? string.Join("_", names.ToArray()) : string.Join("_", names.GetRange(0, 6).ToArray()) + "_P" + (names.Count - 6).ToString(CultureInfo.InvariantCulture);
				z.Label = (z.Tier == "DECISION" ? "D_" : "T_") + shortNames;
			}
			for (int i = 1; i < zones.Count; i++)
			{
				Zone a = zones[i - 1], b = zones[i];
				if (b.Lo > a.Hi) continue;
				double cut = FloorTick((a.MaxLevel + b.MinLevel) / 2.0);
				a.Hi = Math.Max(a.MaxLevel, cut);
				b.Lo = Math.Min(b.MinLevel, a.Hi + tickSize);
			}
			foreach (Zone z in zones)
				foreach (Area ar in areas)
					if (ar.Lo <= z.Hi && ar.Hi >= z.Lo)
					{
						string tag = ar.Type == "SP" ? "SP_" + ar.Source.Replace("TPO_", "") : (ar.Source == "HTF" ? "HTF_" + ar.Type : ar.Type);
						if (!z.Tags.Contains(tag)) z.Tags.Add(tag);
					}
			return zones;
		}

		// ==============================================================================
		//  Review packet (JSON)
		// ==============================================================================
		private string SessionJson(string slot, DayStats ds, double[] va, double tpoc, double tvah, double tval, bool covered)
		{
			return Obj(KV("slot", Q(slot)), KV("date", Q(ds.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))), KV("covered", covered ? "true" : "false"),
				KV("cash_open", Num(ds.CashOpen)), KV("cash_high", Num(ds.Cash.High)), KV("cash_low", Num(ds.Cash.Low)),
				KV("settle", Num(SettleOf(ds))), KV("close_16", Num(ds.Last)), KV("day_high", Num(ds.High)), KV("day_low", Num(ds.Low)),
				KV("vah", Num(va[1])), KV("poc", Num(va[0])), KV("val", Num(va[2])),
				KV("tpo_vah", Num(tvah)), KV("tpo_poc", Num(tpoc)), KV("tpo_val", Num(tval)), KV("cash_volume", ds.Cash.Total.ToString(CultureInfo.InvariantCulture)));
		}

		private string BuildPacket(DayMap m, List<string> sessionJson, List<double[]> vaByK, double onPoc, double onVah, double onVal,
			double vw, double sd, double wvwap, double wkPoc, double wkVah, double wkVal, double pwPoc, double pwVah, double pwVal,
			DayStats pdStats, List<string> compDates, List<string> extra)
		{
			double rp = m.RefPrice;
			List<string> top = new List<string>();
			top.Add(KV("schema", Q("JeronPreopenPacket/1")));
			top.Add(KV("map_version", Q(Version)));
			top.Add(KV("instrument", Q(Instrument != null ? Instrument.FullName : "NA")));
			top.Add(KV("date", Q(m.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))));
			top.Add(KV("asof_ct", Q(AsOfCT)));
			top.Add(KV("built_local", Q(DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture))));
			top.Add(KV("ref_price", Num(rp)));
			top.Add(KV("tick_size", Num(tickSize)));

			// data quality
			List<string> gl = new List<string>();
			foreach (DataGap g in gaps) if (g.End > m.AsOfCt.AddDays(-15) && g.Start < m.AsOfCt) gl.Add(Obj(KV("from", Q(JTime(g.Start))), KV("to", Q(JTime(g.End)))));
			top.Add(KV("data", Obj(KV("first_tick_ct", Q(JTime(firstTickCt))), KV("gaps", Arr(gl)), KV("notes", Arr(QList(m.Notes))),
				KV("delta_through_ct", Q(JTime(deltaThroughCt))), KV("es_through_ct", Q(JTime(esThroughCt))))));

			top.Add(KV("settings", Obj(KV("value_area_pct", Num(ValueAreaPct)), KV("ticks_per_row", TicksPerRow.ToString(CultureInfo.InvariantCulture)),
				KV("tpo_row_points", Num(TpoTicksPerRow * tickSize)), KV("merge_points", Num(MergeDistancePoints)), KV("pad_points", Num(ZonePadPoints)),
				KV("decision_min_sources", MinSourcesForDecision.ToString(CultureInfo.InvariantCulture)), KV("hvn_row_points", Num(HvnTicksPerRow * tickSize)),
				KV("hvn_pct", Num(HvnPct)), KV("lvn_pct", Num(LvnPct)), KV("composite_days", Arr(QList(compDates))))));

			// levels, areas, zones
			List<string> lv = new List<string>();
			foreach (Level l in m.Levels)
				lv.Add(Obj(KV("name", Q(l.Name)), KV("family", Q(l.Family)), KV("kind", Q(l.Kind)), KV("price", Num(l.Price)), KV("in_zones", l.InZones ? "true" : "false"),
					KV("vs_price", Num(double.IsNaN(rp) ? double.NaN : l.Price - rp))));
			top.Add(KV("levels", Arr(lv)));
			List<string> ar = new List<string>();
			foreach (Area a in m.Areas) ar.Add(Obj(KV("type", Q(a.Type)), KV("source", Q(a.Source)), KV("lo", Num(a.Lo)), KV("hi", Num(a.Hi))));
			top.Add(KV("areas", Arr(ar)));
			List<string> zj = new List<string>();
			List<HourBar> testHrs = HoursBefore(hours, m.AsOfCt, StructureDays * 24);
			foreach (Zone z in m.Zones)
			{
				List<string> names = new List<string>();
				foreach (Level l in z.Levels) names.Add(l.Name);
				string zonePos = double.IsNaN(rp) ? "" : (rp > z.Hi ? "BELOW_PRICE" : (rp < z.Lo ? "ABOVE_PRICE" : "AT_PRICE"));
				zj.Add(Obj(KV("lo", Num(z.Lo)), KV("hi", Num(z.Hi)), KV("label", Q(z.Label)), KV("tier", Q(z.Tier)), KV("sources", z.Sources.ToString(CultureInfo.InvariantCulture)),
					KV("levels", Arr(QList(names))), KV("tags", Arr(QList(z.Tags))), KV("where", Q(zonePos)),
					KV("distance_points", Num(double.IsNaN(rp) ? double.NaN : (rp > z.Hi ? rp - z.Hi : (rp < z.Lo ? z.Lo - rp : 0)))),
					KV("tests", ZoneTestsJson(z.Lo, z.Hi, testHrs))));
			}
			top.Add(KV("zones", Arr(zj)));

			// sessions (PD, PD2, PD3) and value migration
			top.Add(KV("prior_sessions", Arr(sessionJson)));
			List<string> mig = new List<string>();
			string[] slots = new string[] { "PD", "PD2", "PD3" };
			for (int k = 0; k + 1 < vaByK.Count && k < 2; k++)
				mig.Add(MigrationJson(slots[k] + "_vs_" + slots[k + 1], vaByK[k], vaByK[k + 1]));
			if (vaByK.Count > 0) mig.Add(MigrationJson("ON_vs_PD", new double[] { onPoc, onVah, onVal }, vaByK[0]));
			top.Add(KV("value_migration", Arr(mig)));

			// overnight inventory
			double settle = pdStats != null ? SettleOf(pdStats) : double.NaN;
			double pctAbove = onVolTotal > 0 && !double.IsNaN(onSettleRef) ? 100.0 * onVolAboveSettle / onVolTotal : double.NaN;
			string inv = double.IsNaN(pctAbove) ? "UNKNOWN" : (pctAbove >= InventoryLongPct ? "NET_LONG" : (pctAbove <= InventoryShortPct ? "NET_SHORT" : "NEUTRAL"));
			double onHigh = overnight.Empty ? double.NaN : overnight.High, onLow = overnight.Empty ? double.NaN : overnight.Low;
			top.Add(KV("overnight", Obj(KV("open", Num(onOpen)), KV("high", Num(onHigh)), KV("low", Num(onLow)), KV("last", Num(rp)),
				KV("range", Num(onHigh - onLow)), KV("vah", Num(onVah)), KV("poc", Num(onPoc)), KV("val", Num(onVal)),
				KV("pd_settle", Num(settle)), KV("pd_close_16", Num(pdStats != null ? pdStats.Last : double.NaN)),
				KV("vs_settle", Num(rp - settle)), KV("pct_volume_above_settle", Num(pctAbove)), KV("inventory", Q(inv)),
				KV("max_pullback_from_high", Num(onMaxDrawFromHigh)), KV("max_rally_from_low", Num(onMaxRallyFromLow)),
				KV("position_in_range_pct", Num(onHigh > onLow ? 100.0 * (rp - onLow) / (onHigh - onLow) : double.NaN)),
				KV("vwap", Num(vw)), KV("vwap_sd", Num(sd)))));

			// location at the as-of time
			top.Add(KV("location", Obj(
				KV("vs_pd_value", Q(VaPos(rp, vaByK.Count > 0 ? vaByK[0] : null))),
				KV("vs_on_value", Q(VaPos(rp, new double[] { onPoc, onVah, onVal }))),
				KV("vs_week_value", Q(VaPos(rp, new double[] { wkPoc, wkVah, wkVal }))),
				KV("vs_prior_week_value", Q(VaPos(rp, new double[] { pwPoc, pwVah, pwVal }))),
				KV("vs_vwap", Q(Side(rp, vw))), KV("vwap_sigma", Num(sd > 0 ? (rp - vw) / sd : double.NaN)),
				KV("vs_weekly_vwap", Q(Side(rp, wvwap))), KV("vs_settle", Q(Side(rp, settle))),
				KV("vs_pd_range", Q(pdStats == null || pdStats.Cash == null ? "UNKNOWN" : (rp > pdStats.Cash.High ? "ABOVE_PDH" : (rp < pdStats.Cash.Low ? "BELOW_PDL" : "INSIDE")))))));

			// weekly
			top.Add(KV("weekly", Obj(KV("week_start", Q(curWeekMonday.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))),
				KV("week_high", Num(weekly.Empty ? double.NaN : weekly.High)), KV("week_low", Num(weekly.Empty ? double.NaN : weekly.Low)),
				KV("vah", Num(wkVah)), KV("poc", Num(wkPoc)), KV("val", Num(wkVal)), KV("weekly_vwap", Num(wvwap)),
				KV("prior_week_start", Q(priorWeekMonday == DateTime.MinValue ? "" : priorWeekMonday.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))),
				KV("prior_week_high", Num(priorWeek == null ? double.NaN : priorWeek.High)), KV("prior_week_low", Num(priorWeek == null ? double.NaN : priorWeek.Low)),
				KV("prior_week_vah", Num(pwVah)), KV("prior_week_poc", Num(pwPoc)), KV("prior_week_val", Num(pwVal)))));

			// delta profile (exact, from Volumetric)
			if (volType != null)
			{
				Dictionary<long, long[]> pdRows = null, onRows = null;
				if (pdStats != null) cashDelta.TryGetValue(pdStats.Date, out pdRows);
				onDelta.TryGetValue(m.Date, out onRows);
				top.Add(KV("delta_profile", Obj(KV("row_points", Num(DeltaRowTicks * tickSize)), KV("note", Q("rows: [row_low_price, delta, volume]; delta = ask - bid volume")),
					KV("pd_cash", DeltaRowsJson(pdRows)), KV("overnight", DeltaRowsJson(onRows)))));
			}

			// higher-timeframe structure: daily table, 1-hour bars and swings
			List<string> daily = new List<string>();
			List<DateTime> dk = new List<DateTime>(days.Keys);
			dk.Sort();
			int startIdx = Math.Max(0, dk.Count - 20);
			for (int i = startIdx; i < dk.Count; i++)
			{
				DayStats ds = days[dk[i]];
				if (ds.Date >= m.Date) continue;
				double a = double.NaN, b = double.NaN, c = double.NaN;
				if (ds.Cash == null || ds.Cash.Empty || !VolumeVa(ds.Cash, out a, out b, out c)) { a = b = c = double.NaN; }
				daily.Add(Obj(KV("date", Q(ds.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))), KV("open", Num(ds.Open)), KV("high", Num(ds.High)), KV("low", Num(ds.Low)),
					KV("close_16", Num(ds.Last)), KV("settle", Num(SettleOf(ds))), KV("cash_high", Num(ds.Cash != null && !ds.Cash.Empty ? ds.Cash.High : double.NaN)),
					KV("cash_low", Num(ds.Cash != null && !ds.Cash.Empty ? ds.Cash.Low : double.NaN)), KV("vah", Num(b)), KV("poc", Num(a)), KV("val", Num(c))));
			}
			List<HourBar> hrs = HoursBefore(hours, m.AsOfCt, StructureDays * 24);
			top.Add(KV("structure", Obj(KV("daily", Arr(daily)), KV("h1", HoursJson(hrs)), KV("h1_swings", SwingsJson(hrs)), KV("h1_trend", Q(TrendLabel(hrs))))));

			// ES cross-check
			if (esIdx > 0)
			{
				EsDay esPd = null;
				esDays.TryGetValue(PrevTradingDate(m.Date), out esPd);
				double ePoc = double.NaN, eVah = double.NaN, eVal = double.NaN;
				if (esPd != null) EsVa(esPd, out ePoc, out eVah, out eVal);
				double esSettle = esPd != null ? esPd.Settle : double.NaN;
				double nqPct = !double.IsNaN(settle) && settle > 0 ? 100.0 * (rp - settle) / settle : double.NaN;
				double esPct = !double.IsNaN(esSettle) && esSettle > 0 && !double.IsNaN(esLast) ? 100.0 * (esLast - esSettle) / esSettle : double.NaN;
				List<HourBar> eh = HoursBefore(esHours, m.AsOfCt, 3 * 24);
				top.Add(KV("es", Obj(KV("instrument", Q(EsInstrument)), KV("available", esPd != null && !double.IsNaN(esLast) ? "true" : "false"),
					KV("through_ct", Q(JTime(esThroughCt))), KV("last", Num(esLast)), KV("pd_settle", Num(esSettle)), KV("pd_close_16", Num(esPd != null ? esPd.Last : double.NaN)),
					KV("pd_cash_high", Num(esPd != null ? esPd.CashHigh : double.NaN)), KV("pd_cash_low", Num(esPd != null ? esPd.CashLow : double.NaN)),
					KV("pd_vah_approx", Num(eVah)), KV("pd_poc_approx", Num(ePoc)), KV("pd_val_approx", Num(eVal)),
					KV("on_high", Num(esOnHigh > double.MinValue ? esOnHigh : double.NaN)), KV("on_low", Num(esOnLow < double.MaxValue ? esOnLow : double.NaN)),
					KV("on_vwap_approx", Num(esV > 0 ? esPv / esV : double.NaN)),
					KV("es_pct_vs_settle", Num(esPct)), KV("nq_pct_vs_settle", Num(nqPct)),
					KV("relative", Q(double.IsNaN(esPct) || double.IsNaN(nqPct) ? "UNKNOWN" : (nqPct - esPct > 0.1 ? "NQ_STRONGER" : (esPct - nqPct > 0.1 ? "ES_STRONGER" : "IN_LINE")))),
					KV("h1", HoursJson(eh)))));
			}

			if (extra != null) top.AddRange(extra);
			return "{" + string.Join(",", top.ToArray()) + "}";
		}

		private string MigrationJson(string name, double[] a, double[] b)
		{
			// a = newer [poc, vah, val], b = older
			if (a == null || b == null || double.IsNaN(a[0]) || double.IsNaN(b[0]))
				return Obj(KV("pair", Q(name)), KV("label", Q("UNKNOWN")));
			double overlap = Math.Min(a[1], b[1]) - Math.Max(a[2], b[2]);
			double minWidth = Math.Max(tickSize, Math.Min(a[1] - a[2], b[1] - b[2]));
			double overlapPct = overlap <= 0 ? 0 : 100.0 * overlap / minWidth;
			double pocMove = a[0] - b[0];
			string label;
			if (a[2] > b[1]) label = "HIGHER_NO_OVERLAP";
			else if (a[1] < b[2]) label = "LOWER_NO_OVERLAP";
			else if (overlapPct < MigrationOverlapPct) label = pocMove > 0 ? "HIGHER" : "LOWER";
			else label = "OVERLAPPING";
			return Obj(KV("pair", Q(name)), KV("poc_change", Num(pocMove)), KV("vah_change", Num(a[1] - b[1])), KV("val_change", Num(a[2] - b[2])),
				KV("va_overlap_pct", Num(overlapPct)), KV("label", Q(label)));
		}

		// ------------------------------------------------------------------------------
		//  v2.1 packet helpers
		// ------------------------------------------------------------------------------

		// Tests of a zone on completed 1-hour bars. A test = consecutive hours whose range touches the zone. It came
		// from below/above (last hour fully outside before it) and ended rejected (left on the side it came from) or
		// through (left on the other side). Part 2 ~5:00 "rejected 1, 2, 3, 4, 5 times", Strategy-in-30 ~11:02
		// "fourth test of the floor", Part 3 ~6:01 "zone keeps getting smaller". Mechanical; for reference only.
		private string ZoneTestsJson(double lo, double hi, List<HourBar> hrs)
		{
			int lastOut = 0, entry = 0;
			bool inRun = false;
			double runH = 0, runL = 0;
			DateTime runStart = DateTime.MinValue;
			int fb = 0, rb = 0, tb = 0, fa = 0, ra = 0, ta = 0;
			List<double> highsIn = new List<double>(), lowsIn = new List<double>();
			List<double> runHours = new List<double>();   // v2.3: hours spent per test (Part 3 ~6:01 "spending even less time up here")
			int runLen = 0;
			string lastTest = "";
			foreach (HourBar h in hrs)
			{
				bool touch = h.H >= lo && h.L <= hi;
				if (touch)
				{
					if (!inRun) { inRun = true; entry = lastOut; runH = h.H; runL = h.L; runStart = h.HourCt; runLen = 0; }
					else { if (h.H > runH) runH = h.H; if (h.L < runL) runL = h.L; }
					runLen++;
					continue;
				}
				int side = h.L > hi ? 1 : -1;
				if (inRun)
				{
					lastTest = runStart.ToString("MM-dd HH", CultureInfo.InvariantCulture);
					if (entry < 0) { fb++; highsIn.Add(runH); if (side < 0) rb++; else tb++; }
					else if (entry > 0) { fa++; lowsIn.Add(runL); if (side > 0) ra++; else ta++; }
					if (entry != 0) runHours.Add(runLen);
					inRun = false;
				}
				lastOut = side;
			}
			if (inRun)
			{
				lastTest = runStart.ToString("MM-dd HH", CultureInfo.InvariantCulture);
				if (entry < 0) { fb++; highsIn.Add(runH); }
				else if (entry > 0) { fa++; lowsIn.Add(runL); }
				if (entry != 0) runHours.Add(runLen);
			}
			bool shrinking = runHours.Count >= 3 && runHours[runHours.Count - 1] < runHours[runHours.Count - 2] && runHours[runHours.Count - 2] < runHours[runHours.Count - 3];
			bool lowerHighs = highsIn.Count >= 3 && highsIn[highsIn.Count - 1] < highsIn[highsIn.Count - 2] && highsIn[highsIn.Count - 2] < highsIn[highsIn.Count - 3];
			bool higherLows = lowsIn.Count >= 3 && lowsIn[lowsIn.Count - 1] > lowsIn[lowsIn.Count - 2] && lowsIn[lowsIn.Count - 2] > lowsIn[lowsIn.Count - 3];
			return Obj(KV("window_hours", hrs.Count.ToString(CultureInfo.InvariantCulture)),
				KV("from_below", fb.ToString(CultureInfo.InvariantCulture)), KV("rejected_from_below", rb.ToString(CultureInfo.InvariantCulture)), KV("through_from_below", tb.ToString(CultureInfo.InvariantCulture)),
				KV("from_above", fa.ToString(CultureInfo.InvariantCulture)), KV("rejected_from_above", ra.ToString(CultureInfo.InvariantCulture)), KV("through_from_above", ta.ToString(CultureInfo.InvariantCulture)),
				KV("highs_into_zone", NumList(LastN(highsIn, 4))), KV("lows_into_zone", NumList(LastN(lowsIn, 4))),
				KV("lower_highs_into_zone", lowerHighs ? "true" : "false"), KV("higher_lows_into_zone", higherLows ? "true" : "false"),
				KV("last_test", Q(lastTest)), KV("in_zone_now", inRun ? "true" : "false"),
				KV("hours_per_test", NumList(LastN(runHours, 4))), KV("shrinking_time", shrinking ? "true" : "false"));
		}

		// Does value follow price? Part 4 ~0:57-1:24: "we made higher highs ... the value area high to the POC is
		// shifting lower ... buyers are not accepting up at this price." Newer cash session vs the one before.
		private string ValueVsPriceJson(List<double[]> vaByK, List<double[]> hlByK)
		{
			string[] slots = new string[] { "PD", "PD2", "PD3" };
			List<string> items = new List<string>();
			for (int k = 0; k + 1 < vaByK.Count && k + 1 < hlByK.Count && k < 2; k++)
			{
				double[] a = vaByK[k], b = vaByK[k + 1], ha = hlByK[k], hb = hlByK[k + 1];
				string pair = slots[k] + "_vs_" + slots[k + 1];
				if (double.IsNaN(a[0]) || double.IsNaN(b[0]) || double.IsNaN(ha[0]) || double.IsNaN(hb[0]))
				{
					items.Add(Obj(KV("pair", Q(pair)), KV("label", Q("UNKNOWN"))));
					continue;
				}
				double hiCh = ha[0] - hb[0], loCh = ha[1] - hb[1], pocCh = a[0] - b[0];
				string label;
				if (hiCh > 0 && pocCh < 0) label = "HIGHER_HIGH_LOWER_VALUE";
				else if (loCh < 0 && pocCh > 0) label = "LOWER_LOW_HIGHER_VALUE";
				else if (hiCh > 0 && pocCh > 0) label = "VALUE_FOLLOWS_UP";
				else if (loCh < 0 && pocCh < 0) label = "VALUE_FOLLOWS_DOWN";
				else label = "INSIDE_OR_MIXED";
				items.Add(Obj(KV("pair", Q(pair)), KV("high_change", Num(hiCh)), KV("low_change", Num(loCh)), KV("poc_change", Num(pocCh)),
					KV("vah_change", Num(a[1] - b[1])), KV("val_change", Num(a[2] - b[2])), KV("label", Q(label))));
			}
			return Arr(items);
		}

		// Prior cash session + overnight as one profile (Part 5 ~5:11 "combine yesterday's cash session with the
		// overnight"; Part 6 ~1:40 and webinar ~24:28 compress balanced profiles into one range).
		private string PdOnJson(DayStats pdStats, bool useSession, double rp)
		{
			if (pdStats == null || pdStats.Cash == null || pdStats.Cash.Empty || !useSession || overnight == null || overnight.Empty)
				return Obj(KV("available", "false"));
			PriceProfile p = NewProfile();
			foreach (KeyValuePair<long, long> kv in pdStats.Cash.Vol) { long c; p.Vol.TryGetValue(kv.Key, out c); p.Vol[kv.Key] = c + kv.Value; p.Total += kv.Value; }
			foreach (KeyValuePair<long, long> kv in overnight.Vol) { long c; p.Vol.TryGetValue(kv.Key, out c); p.Vol[kv.Key] = c + kv.Value; p.Total += kv.Value; }
			double a, b, c2;
			if (!VolumeVa(p, out a, out b, out c2)) return Obj(KV("available", "false"));
			double ov = double.NaN;   // v2.3: does PD value overlap ON value at all?
			double o1, o2, o3;
			if (VolumeVa(overnight, out o1, out o2, out o3)) ov = OverlapPct(VaOfCash(pdStats), new double[] { o1, o2, o3 });
			return Obj(KV("available", "true"), KV("vah", Num(b)), KV("poc", Num(a)), KV("val", Num(c2)),
				KV("high", Num(Math.Max(pdStats.Cash.High, overnight.High))), KV("low", Num(Math.Min(pdStats.Cash.Low, overnight.Low))),
				KV("location", Q(VaPos(rp, new double[] { a, b, c2 }))),
				KV("va_overlap_pct", Num(ov)), KV("overlapping", !double.IsNaN(ov) && ov > 0 ? "true" : "false"));
		}

		// Range context: average daily range of the last 10 loaded days, prior-day and overnight range in ADR
		// multiples (Part 1 ~1:24:03 "we just had a 300-400 point pump" -> continuation needs initiation).
		private string RangesJson(DateTime td, DayStats pdStats, double rp)
		{
			List<DateTime> dk = new List<DateTime>(days.Keys);
			dk.Sort();
			List<double> full = new List<double>(), cash = new List<double>();
			for (int i = dk.Count - 1; i >= 0 && full.Count < 10; i--)
			{
				if (dk[i] >= td) continue;
				DayStats ds = days[dk[i]];
				if (ds.High <= double.MinValue || ds.Low >= double.MaxValue) continue;
				full.Add(ds.High - ds.Low);
				if (ds.Cash != null && !ds.Cash.Empty) cash.Add(ds.Cash.High - ds.Cash.Low);
			}
			double adr = Avg(full), adrCash = Avg(cash);
			double pdCash = pdStats != null && pdStats.Cash != null && !pdStats.Cash.Empty ? pdStats.Cash.High - pdStats.Cash.Low : double.NaN;
			double pdFull = pdStats != null && pdStats.High > double.MinValue ? pdStats.High - pdStats.Low : double.NaN;
			double onRange = overnight != null && !overnight.Empty ? overnight.High - overnight.Low : double.NaN;
			double pdMove = double.NaN;
			DayStats pd2;
			if (pdStats != null && days.TryGetValue(PrevTradingDate(pdStats.Date), out pd2)) pdMove = pdStats.Last - pd2.Last;
			double vsSettle = pdStats != null ? rp - SettleOf(pdStats) : double.NaN;
			return Obj(KV("days_used", full.Count.ToString(CultureInfo.InvariantCulture)), KV("adr_full", Num(adr)), KV("adr_cash", Num(adrCash)),
				KV("pd_cash_range", Num(pdCash)), KV("pd_cash_range_vs_adr_cash", Num(adrCash > 0 ? pdCash / adrCash : double.NaN)),
				KV("pd_full_range", Num(pdFull)), KV("on_range", Num(onRange)), KV("on_range_vs_adr_full", Num(adr > 0 ? onRange / adr : double.NaN)),
				KV("pd_net_move_close16", Num(pdMove)), KV("pd_net_move_vs_adr_full", Num(adr > 0 ? pdMove / adr : double.NaN)),
				KV("last_vs_settle", Num(vsSettle)), KV("last_vs_settle_vs_adr_full", Num(adr > 0 ? vsSettle / adr : double.NaN)));
		}

		// Volume profile anchored at the start of the current leg: the later of the highest high / lowest low of
		// the last SwingAnchorDays of 1-hour bars (Part 4 ~2:43 "draw a volume profile from the swing point";
		// webinar: swing high to swing low profile). Delta bands are summed from whole sessions since the anchor
		// date (approximate; delta is kept for 10 days).
		private string SwingProfileJson(DateTime td, DateTime asOf, double rp)
		{
			List<HourBar> bars = new List<HourBar>();
			foreach (HourBar h in hours) if (h.HourCt < asOf && h.Rows != null) bars.Add(h);
			int max = Math.Max(1, SwingAnchorDays) * 24;
			if (bars.Count > max) bars.RemoveRange(0, bars.Count - max);
			if (bars.Count < 6) return Obj(KV("available", "false"));
			int maxIdx = 0, minIdx = 0;
			for (int i = 1; i < bars.Count; i++)
			{
				if (bars[i].H > bars[maxIdx].H) maxIdx = i;
				if (bars[i].L < bars[minIdx].L) minIdx = i;
			}
			bool fromHigh = maxIdx > minIdx || (maxIdx == minIdx && rp < (bars[maxIdx].H + bars[maxIdx].L) / 2.0);
			int anchorIdx = Math.Max(maxIdx, minIdx);
			double anchorPrice = fromHigh ? bars[maxIdx].H : bars[minIdx].L;
			Dictionary<long, long> rows = new Dictionary<long, long>();
			for (int i = anchorIdx; i < bars.Count; i++)
				foreach (KeyValuePair<long, long> kv in bars[i].Rows) { long c; rows.TryGetValue(kv.Key, out c); rows[kv.Key] = c + kv.Value; }
			double poc, vah, val;
			if (!VaFromRows(rows, Math.Max(1, HvnTicksPerRow), out poc, out vah, out val)) return Obj(KV("available", "false"));

			DateTime anchorTd = TradingDateOf(bars[anchorIdx].HourCt);
			Dictionary<long, long[]> drows = new Dictionary<long, long[]>();
			foreach (Dictionary<DateTime, Dictionary<long, long[]>> src in new Dictionary<DateTime, Dictionary<long, long[]>>[] { cashDelta, onDelta })
				foreach (KeyValuePair<DateTime, Dictionary<long, long[]>> dkv in src)
				{
					if (dkv.Key < anchorTd || dkv.Key > td) continue;
					foreach (KeyValuePair<long, long[]> r in dkv.Value)
					{
						long[] cell;
						if (!drows.TryGetValue(r.Key, out cell)) { cell = new long[2]; drows[r.Key] = cell; }
						cell[0] += r.Value[0];
						cell[1] += r.Value[1];
					}
				}
			List<long> keys = new List<long>(drows.Keys);
			keys.Sort(delegate(long x, long y) { return drows[y][0].CompareTo(drows[x][0]); });   // most positive first
			int rt = Math.Max(1, DeltaRowTicks);
			List<string> buys = new List<string>(), sells = new List<string>();
			long total = 0;
			foreach (long k in keys) total += drows[k][0];
			for (int i = 0; i < keys.Count && buys.Count < 3; i++)
				if (drows[keys[i]][0] > 0) buys.Add("[" + Num(keys[i] * rt * tickSize) + "," + drows[keys[i]][0].ToString(CultureInfo.InvariantCulture) + "," + drows[keys[i]][1].ToString(CultureInfo.InvariantCulture) + "]");
			for (int i = keys.Count - 1; i >= 0 && sells.Count < 3; i--)
				if (drows[keys[i]][0] < 0) sells.Add("[" + Num(keys[i] * rt * tickSize) + "," + drows[keys[i]][0].ToString(CultureInfo.InvariantCulture) + "," + drows[keys[i]][1].ToString(CultureInfo.InvariantCulture) + "]");
			return Obj(KV("available", "true"), KV("anchor", Q(fromHigh ? "FROM_SWING_HIGH" : "FROM_SWING_LOW")),
				KV("anchor_time", Q(bars[anchorIdx].HourCt.ToString("yyyy-MM-dd HH:00", CultureInfo.InvariantCulture))), KV("anchor_price", Num(anchorPrice)),
				KV("leg_points", Num(rp - anchorPrice)), KV("window_days", SwingAnchorDays.ToString(CultureInfo.InvariantCulture)),
				KV("vah", Num(vah)), KV("poc", Num(poc)), KV("val", Num(val)), KV("location", Q(VaPos(rp, new double[] { poc, vah, val }))),
				KV("delta_from_date", Q(anchorTd.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))), KV("delta_total", total.ToString(CultureInfo.InvariantCulture)),
				KV("top_buy_rows", "[" + string.Join(",", buys.ToArray()) + "]"), KV("top_sell_rows", "[" + string.Join(",", sells.ToArray()) + "]"),
				KV("note", Q("rows: [row_low_price, delta, volume]; delta summed from whole sessions since the anchor date (approximate)")));
		}

		// Where the overnight volume sits in its range (Part 3 ~5:00 "overnight profile is very thin ... not much
		// volume here"). Thin = under 20% of the volume in that third (our research threshold).
		private string OnDistributionJson(bool useSession)
		{
			if (!useSession || overnight == null || overnight.Empty || overnight.High <= overnight.Low) return Obj(KV("available", "false"));
			double third = (overnight.High - overnight.Low) / 3.0;
			double lo = 0, mid = 0, up = 0;
			foreach (KeyValuePair<long, long> kv in overnight.Vol)
			{
				double p = kv.Key * tickSize;
				if (p < overnight.Low + third) lo += kv.Value;
				else if (p < overnight.Low + 2 * third) mid += kv.Value;
				else up += kv.Value;
			}
			double t = lo + mid + up;
			if (t <= 0) return Obj(KV("available", "false"));
			double pl = 100.0 * lo / t, pm = 100.0 * mid / t, pu = 100.0 * up / t;
			string thin = pl < 20 && pu < 20 ? "BOTH_ENDS_THIN" : (pl < 20 ? "LOWER_THIN" : (pu < 20 ? "UPPER_THIN" : "NONE"));
			return Obj(KV("available", "true"), KV("lower_third_pct", Num(pl)), KV("middle_third_pct", Num(pm)), KV("upper_third_pct", Num(pu)), KV("thin", Q(thin)));
		}

		// Higher-timeframe composite: the last HtfCompositeDays complete trading days (whole day, HVN rows).
		// v2.3: from the 1-minute series when it is on (MINUTE_APPROX, up to 90 days), else from the tick days (TICK, max 44;
		// raise 'Keep tick days' to about 70 calendar days for 44 trading days).
		private Dictionary<long, long> HtfRows(DateTime td, List<string> usedDates, out string source)
		{
			Dictionary<long, long> comp = new Dictionary<long, long>();
			DateTime d = td;
			string why;
			bool useMin = htfIdx > 0 && htfMinDays.Count > 0;
			source = useMin ? "MINUTE_APPROX" : "TICK";
			int want = Math.Max(1, Math.Min(useMin ? 90 : 44, HtfCompositeDays));
			for (int k = 0; k < want + 40 && usedDates.Count < want; k++)
			{
				d = PrevTradingDate(d);
				if (useMin)
				{
					Dictionary<long, double> mr;
					int cnt;
					if (!htfMinDays.TryGetValue(d, out mr) || !htfMinCount.TryGetValue(d, out cnt)) continue;
					int need = halfDays.ContainsKey(d) ? Math.Max(1, HtfMinMinutesPerDay * 3 / 4) : Math.Max(1, HtfMinMinutesPerDay);
					if (cnt < need) continue;   // incomplete minute day
					foreach (KeyValuePair<long, double> kv in mr) { long c; comp.TryGetValue(kv.Key, out c); comp[kv.Key] = c + (long)Math.Round(kv.Value); }
				}
				else
				{
					DayStats ds;
					if (!days.TryGetValue(d, out ds)) continue;
					if (!Covered(SessionStartCt(d), BreakStartCt(d), out why)) continue;
					foreach (KeyValuePair<long, long> kv in ds.Rows) { long c; comp.TryGetValue(kv.Key, out c); comp[kv.Key] = c + kv.Value; }
				}
				usedDates.Add(d.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture));
			}
			return comp;
		}

		// v2.3 manual HTF levels: "[yyyy-MM-dd@]NAME=price; ..." e.g. "2026-10-20@VAH=31600; POC=31200; 2026-11-02@VAH=31750".
		// A date applies to the entries after it until the next date. A dated level is used from that trading date on; per
		// name the latest date at or before the trading date wins. Undated levels are used on every date (as before v2.3).
		private void ParseHtfManual()
		{
			htfManual.Clear();
			if (string.IsNullOrWhiteSpace(HtfLevels)) return;
			DateTime cur = DateTime.MinValue;
			foreach (string raw in HtfLevels.Split(new char[] { ';', ',' }, StringSplitOptions.RemoveEmptyEntries))
			{
				string part = raw.Trim();
				int at = part.IndexOf('@');
				if (at > 0)
				{
					DateTime d;
					if (DateTime.TryParseExact(part.Substring(0, at).Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d)) cur = d.Date;
					else lastError = "HTF level date not understood: '" + part + "'";
					part = part.Substring(at + 1).Trim();
				}
				string[] kv = part.Split('=');
				double price;
				if (kv.Length != 2 || !double.TryParse(kv[1].Replace(" ", "").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out price) || price <= 0)
				{
					lastError = "HTF level not understood: '" + raw.Trim() + "' (use [yyyy-MM-dd@]NAME=price)";
					continue;
				}
				HtfManual h = new HtfManual();
				h.From = cur;
				h.Name = SafeToken(kv[0].Trim().ToUpperInvariant());
				h.Price = price;
				htfManual.Add(h);
			}
		}

		private string ApplyHtfManual(DayMap m, DateTime td)
		{
			Dictionary<string, HtfManual> pick = new Dictionary<string, HtfManual>();
			foreach (HtfManual h in htfManual)
			{
				if (h.From != DateTime.MinValue && h.From > td) continue;   // not written yet on this trading date (no hindsight)
				HtfManual cur;
				if (!pick.TryGetValue(h.Name, out cur) || h.From >= cur.From) pick[h.Name] = h;
			}
			List<string> items = new List<string>();
			bool anyUndated = false, anyStale = false;
			foreach (HtfManual h in pick.Values)
			{
				AddLevel(m, "HTFM_" + h.Name, "HTF", "MAN", h.Price, IncludeHtfInZones);
				int age = h.From == DateTime.MinValue ? -1 : (int)(td - h.From).TotalDays;
				bool stale = age > Math.Max(1, HtfManualMaxAgeDays);
				if (h.From == DateTime.MinValue) anyUndated = true;
				if (stale) anyStale = true;
				items.Add(Obj(KV("name", Q(h.Name)), KV("price", Num(h.Price)), KV("from", Q(h.From == DateTime.MinValue ? "" : h.From.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))),
					KV("age_days", age < 0 ? "null" : age.ToString(CultureInfo.InvariantCulture)), KV("stale", stale ? "true" : "false")));
			}
			if (anyUndated) m.Notes.Add("HTF: undated manual HTF levels are used on every date; in a replay they may contain hindsight. Add a date: yyyy-MM-dd@NAME=price");
			if (anyStale) m.Notes.Add("HTF: manual HTF levels older than " + HtfManualMaxAgeDays.ToString(CultureInfo.InvariantCulture) + " days; refresh them");
			return Arr(items);
		}

		// v2.3 balance merge (Part 6 ~1:40, Part 5 ~5:11, webinar ~24:28): PD2, PD and ON value areas; consecutive members
		// whose value areas overlap are merged into one profile. Overlap % = overlap / the narrower value area (as in migration).
		private string BalanceJson(DayStats pd2, bool pd2Ok, DayStats pd, bool useSession, double rp)
		{
			double[] vPd2 = VaOfCash(pd2Ok || !SkipPartialProfiles ? pd2 : null);
			double[] vPd = VaOfCash(pd);
			double[] vOn = new double[] { double.NaN, double.NaN, double.NaN };
			if (useSession && overnight != null && !overnight.Empty)
			{
				double a, b, c;
				if (VolumeVa(overnight, out a, out b, out c)) vOn = new double[] { a, b, c };
			}
			double oPd2Pd = OverlapPct(vPd2, vPd), oPdOn = OverlapPct(vPd, vOn);
			bool pdOn = !double.IsNaN(oPdOn) && oPdOn > 0, pd2Pd = !double.IsNaN(oPd2Pd) && oPd2Pd > 0;
			List<string> members = new List<string>();
			PriceProfile p = NewProfile();
			double hi = double.MinValue, lo = double.MaxValue;
			if (pdOn)
			{
				members.Add("PD"); members.Add("ON");
				AddInto(p, pd.Cash); AddInto(p, overnight);
				hi = Math.Max(pd.Cash.High, overnight.High); lo = Math.Min(pd.Cash.Low, overnight.Low);
				if (pd2Pd) { members.Insert(0, "PD2"); AddInto(p, pd2.Cash); hi = Math.Max(hi, pd2.Cash.High); lo = Math.Min(lo, pd2.Cash.Low); }
			}
			double poc = double.NaN, vah = double.NaN, val = double.NaN;
			bool ok = members.Count >= 2 && VolumeVa(p, out poc, out vah, out val);
			return Obj(KV("available", ok ? "true" : "false"), KV("members", Arr(QList(members))),
				KV("overlapping", ok ? "true" : "false"), KV("merged_three", ok && members.Count == 3 ? "true" : "false"),
				KV("overlap_pct_pd2_pd", Num(oPd2Pd)), KV("overlap_pct_pd_on", Num(oPdOn)),
				KV("vah", Num(vah)), KV("poc", Num(poc)), KV("val", Num(val)),
				KV("high", Num(ok ? hi : double.NaN)), KV("low", Num(ok ? lo : double.NaN)),
				KV("location", Q(ok ? VaPos(rp, new double[] { poc, vah, val }) : "UNKNOWN")),
				KV("note", Q("members = consecutive profiles whose 70% value areas overlap (PD2-PD, PD-ON); no PD-ON overlap = no balance (migrating)")));
		}

		private double[] VaOfCash(DayStats ds)
		{
			double[] r = new double[] { double.NaN, double.NaN, double.NaN };
			if (ds == null || ds.Cash == null || ds.Cash.Empty) return r;
			double a, b, c;
			if (VolumeVa(ds.Cash, out a, out b, out c)) r = new double[] { a, b, c };
			return r;
		}

		private double OverlapPct(double[] a, double[] b)
		{
			if (a == null || b == null || double.IsNaN(a[1]) || double.IsNaN(b[1])) return double.NaN;
			double overlap = Math.Min(a[1], b[1]) - Math.Max(a[2], b[2]);
			double minWidth = Math.Max(tickSize, Math.Min(a[1] - a[2], b[1] - b[2]));
			return overlap <= 0 ? 0 : Math.Min(100.0, 100.0 * overlap / minWidth);
		}

		private static void AddInto(PriceProfile dst, PriceProfile src)
		{
			if (src == null) return;
			foreach (KeyValuePair<long, long> kv in src.Vol) { long c; dst.Vol.TryGetValue(kv.Key, out c); dst.Vol[kv.Key] = c + kv.Value; dst.Total += kv.Value; }
		}

		// v2.3 double distribution (Part 1 ~1:21-1:25): two HVN blocks in the PD cash profile separated by an LVN or by a
		// PD single-print run. Mechanical, for reference.
		private string DoubleDistJson(DayStats pd, DayMap m)
		{
			if (pd == null || pd.Cash == null || pd.Cash.Empty) return Obj(KV("available", "false"));
			Dictionary<long, long> rows = new Dictionary<long, long>();
			int rt = Math.Max(1, HvnTicksPerRow);
			foreach (KeyValuePair<long, long> kv in pd.Cash.Vol) { long r = FloorDiv(kv.Key, rt), c; rows.TryGetValue(r, out c); rows[r] = c + kv.Value; }
			List<Area> areas = HvnLvnAreas(rows, "PD");
			List<Area> hvn = new List<Area>(), sep = new List<Area>();
			foreach (Area a in areas) { if (a.Type == "HVN") hvn.Add(a); else if (a.Type == "LVN") sep.Add(a); }
			foreach (Area a in m.Areas) if (a.Type == "SP" && a.Source == "TPO_PD") sep.Add(a);
			hvn.Sort(delegate(Area x, Area y) { return x.Lo.CompareTo(y.Lo); });
			for (int i = 1; i < hvn.Count; i++)
			{
				double gLo = hvn[i - 1].Hi, gHi = hvn[i].Lo;
				foreach (Area sp in sep)
				{
					if (sp.Hi < gLo || sp.Lo > gHi) continue;
					return Obj(KV("available", "true"), KV("pd_double_distribution", "true"),
						KV("lower_hvn", "[" + Num(hvn[i - 1].Lo) + "," + Num(hvn[i - 1].Hi) + "]"), KV("upper_hvn", "[" + Num(hvn[i].Lo) + "," + Num(hvn[i].Hi) + "]"),
						KV("separator", Q(sp.Type == "SP" ? "SINGLE_PRINTS" : "LVN")), KV("separator_lo", Num(sp.Lo)), KV("separator_hi", Num(sp.Hi)),
						KV("hvn_blocks", hvn.Count.ToString(CultureInfo.InvariantCulture)));
				}
			}
			return Obj(KV("available", "true"), KV("pd_double_distribution", "false"), KV("hvn_blocks", hvn.Count.ToString(CultureInfo.InvariantCulture)));
		}

		private static string MinText(int m)
		{
			return (m / 60).ToString("00", CultureInfo.InvariantCulture) + ":" + (m % 60).ToString("00", CultureInfo.InvariantCulture);
		}

		private string AreasJson(List<Area> areas)
		{
			List<string> items = new List<string>();
			foreach (Area a in areas) items.Add(Obj(KV("type", Q(a.Type)), KV("lo", Num(a.Lo)), KV("hi", Num(a.Hi))));
			return Arr(items);
		}

		private static List<double> LastN(List<double> src, int n)
		{
			return src.Count <= n ? new List<double>(src) : src.GetRange(src.Count - n, n);
		}

		private string NumList(List<double> xs)
		{
			List<string> items = new List<string>();
			foreach (double x in xs) items.Add(Num(x));
			return "[" + string.Join(",", items.ToArray()) + "]";
		}

		private static double Avg(List<double> xs)
		{
			if (xs.Count == 0) return double.NaN;
			double s = 0;
			foreach (double x in xs) s += x;
			return s / xs.Count;
		}

		private string VaPos(double p, double[] va)
		{
			if (va == null || double.IsNaN(p) || double.IsNaN(va[1]) || double.IsNaN(va[2])) return "UNKNOWN";
			if (p > va[1]) return "ABOVE_VALUE";
			if (p < va[2]) return "BELOW_VALUE";
			return "INSIDE_VALUE";
		}

		private static string Side(double p, double r)
		{
			if (double.IsNaN(p) || double.IsNaN(r)) return "UNKNOWN";
			return p > r ? "ABOVE" : (p < r ? "BELOW" : "AT");
		}

		private string DeltaRowsJson(Dictionary<long, long[]> rows)
		{
			if (rows == null || rows.Count == 0) return "[]";
			List<long> keys = new List<long>(rows.Keys);
			keys.Sort();
			List<string> items = new List<string>();
			int rt = Math.Max(1, DeltaRowTicks);
			foreach (long k in keys)
				items.Add("[" + Num(k * rt * tickSize) + "," + rows[k][0].ToString(CultureInfo.InvariantCulture) + "," + rows[k][1].ToString(CultureInfo.InvariantCulture) + "]");
			return "[" + string.Join(",", items.ToArray()) + "]";
		}

		private static List<HourBar> HoursBefore(List<HourBar> src, DateTime asOf, int max)
		{
			List<HourBar> r = new List<HourBar>();
			foreach (HourBar h in src) if (h.HourCt.AddHours(1) <= asOf) r.Add(h);   // completed hours only
			if (r.Count > max) r.RemoveRange(0, r.Count - max);
			return r;
		}

		private string HoursJson(List<HourBar> hrs)
		{
			List<string> items = new List<string>();
			foreach (HourBar h in hrs)
				items.Add("[" + Q(h.HourCt.ToString("MM-dd HH", CultureInfo.InvariantCulture)) + "," + Num(h.O) + "," + Num(h.H) + "," + Num(h.L) + "," + Num(h.C) + "," + h.V.ToString(CultureInfo.InvariantCulture) + "]");
			return "[" + string.Join(",", items.ToArray()) + "]";
		}

		// Swing high: higher than SwingStrength hours on both sides (strict). Swing low mirrors it.
		private List<double[]> Swings(List<HourBar> hrs, out List<string> times)
		{
			times = new List<string>();
			List<double[]> sw = new List<double[]>();   // [type(+1 high/-1 low), price]
			int k = Math.Max(1, SwingStrength);
			for (int i = k; i < hrs.Count - k; i++)
			{
				bool hi = true, lo = true;
				for (int j = 1; j <= k; j++)
				{
					if (!(hrs[i].H > hrs[i - j].H && hrs[i].H > hrs[i + j].H)) hi = false;
					if (!(hrs[i].L < hrs[i - j].L && hrs[i].L < hrs[i + j].L)) lo = false;
				}
				if (hi) { sw.Add(new double[] { 1, hrs[i].H }); times.Add(hrs[i].HourCt.ToString("MM-dd HH", CultureInfo.InvariantCulture)); }
				if (lo) { sw.Add(new double[] { -1, hrs[i].L }); times.Add(hrs[i].HourCt.ToString("MM-dd HH", CultureInfo.InvariantCulture)); }
			}
			return sw;
		}

		private string SwingsJson(List<HourBar> hrs)
		{
			List<string> times;
			List<double[]> sw = Swings(hrs, out times);
			List<string> items = new List<string>();
			int start = Math.Max(0, sw.Count - 16);
			for (int i = start; i < sw.Count; i++)
				items.Add("[" + Q(times[i]) + "," + Q(sw[i][0] > 0 ? "H" : "L") + "," + Num(sw[i][1]) + "]");
			return "[" + string.Join(",", items.ToArray()) + "]";
		}

		// Last two swing highs and lows: HH+HL = UP, LH+LL = DOWN, otherwise MIXED. Mechanical, for reference only.
		private string TrendLabel(List<HourBar> hrs)
		{
			List<string> times;
			List<double[]> sw = Swings(hrs, out times);
			List<double> hs = new List<double>(), ls = new List<double>();
			foreach (double[] s in sw) { if (s[0] > 0) hs.Add(s[1]); else ls.Add(s[1]); }
			if (hs.Count < 2 || ls.Count < 2) return "INSUFFICIENT";
			bool hh = hs[hs.Count - 1] > hs[hs.Count - 2], hl = ls[ls.Count - 1] > ls[ls.Count - 2];
			if (hh && hl) return "UP";
			if (!hh && !hl) return "DOWN";
			return "MIXED";
		}

		private void EsVa(EsDay d, out double poc, out double vah, out double val)
		{
			poc = vah = val = double.NaN;
			if (d.Rows.Count == 0) return;
			Dictionary<long, long> rows = new Dictionary<long, long>();
			foreach (KeyValuePair<long, double> kv in d.Rows) rows[kv.Key] = (long)Math.Round(kv.Value);
			int rt = Math.Max(1, EsTicksPerRow);
			// VaFromRows works in this instrument's ticks; rescale the result for ES
			double ratio = esTickSize / tickSize;
			double a, b, c;
			if (!VaFromRows(rows, rt, out a, out b, out c)) return;
			poc = a * ratio; vah = b * ratio; val = c * ratio;
		}

		// ==============================================================================
		//  Output
		// ==============================================================================
		private string ZoneEntry(DayMap m, Zone z)
		{
			return m.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + "@" + JN(z.Lo, 2) + "-" + JN(z.Hi, 2) + ":" + z.Label;
		}

		private void WriteOutputs(DayMap m)
		{
			List<string> entries = new List<string>();
			foreach (Zone z in m.Zones) entries.Add(ZoneEntry(m, z));
			string dateText = m.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
			int dec = 0;
			foreach (Zone z in m.Zones) if (z.Tier == "DECISION") dec++;

			if (PrintPasteLine)
			{
				Print("JeronPreopenMap " + Version + " " + dateText + " as-of " + AsOfCT + " CT (ref " + JN(m.RefPrice, 2) + "): " + entries.Count.ToString(CultureInfo.InvariantCulture)
					+ " zones, " + dec.ToString(CultureInfo.InvariantCulture) + " decision");
				Print(string.Join(";", entries.ToArray()));
				foreach (string note in m.Notes) Print("  note: " + note);
			}

			if (!WriteFiles || outFolder.Length == 0) return;
			try
			{
				if (WritePacket && m.PacketJson.Length > 0)
					WriteAtomic(Path.Combine(outFolder, "PreopenPacket_" + instrumentToken + "_" + dateText + ".json"), m.PacketJson);   // v2.2

				StringBuilder sb = new StringBuilder();
				sb.AppendLine("# JeronPreopenMap v" + Version + "  date=" + dateText + "  asof=" + AsOfCT + " CT  instrument=" + (Instrument != null ? Instrument.FullName : "NA")
					+ "  built=" + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture));
				sb.AppendLine("# settings: VA=" + JN(ValueAreaPct, 0) + "% merge=" + JN(MergeDistancePoints, 2) + "pt pad=" + JN(ZonePadPoints, 2) + "pt maxWidth=" + JN(MaxZoneWidthPoints, 2)
					+ "pt decision>=" + MinSourcesForDecision.ToString(CultureInfo.InvariantCulture) + " sources refPrice=" + JN(m.RefPrice, 2));
				foreach (string note in m.Notes) sb.AppendLine("# note: " + note);
				foreach (Zone z in m.Zones)
				{
					StringBuilder parts = new StringBuilder();
					foreach (Level l in z.Levels) parts.Append(" ").Append(l.Name).Append("=").Append(JN(l.Price, 2));
					sb.AppendLine("# " + (z.Manual ? "manual zone" : z.Tier + " sources=" + z.Sources.ToString(CultureInfo.InvariantCulture) + " tags=" + string.Join(",", z.Tags.ToArray()) + " levels:" + parts.ToString()));
					sb.AppendLine(ZoneEntry(m, z));
				}
				WriteAtomic(Path.Combine(outFolder, "Zones_" + instrumentToken + "_" + dateText + ".txt"), sb.ToString());   // v2.2

				List<string> all = new List<string>();
				foreach (DayMap dm in maps) foreach (Zone z in dm.Zones) all.Add(ZoneEntry(dm, z));
				string header = "# Paste the line below into JeronOrderFlowEventTracker > 1. Locations > Frozen zones (fallback when there is no PreopenPlan file)."
					+ Environment.NewLine + "# Set 'Zones as-of time (CT)' to " + AsOfCT + ". T_ zones are targets only in tracker v2.3+."
					+ Environment.NewLine;
				foreach (DayMap dm in maps)
					foreach (string note in dm.Notes)
						if (note.StartsWith("DATA"))
							header += "# " + dm.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + " " + note + Environment.NewLine;
				File.WriteAllText(pastePath, header + string.Join(";", all.ToArray()) + Environment.NewLine);

				StringBuilder csv = new StringBuilder();
				foreach (Zone z in m.Zones)
				{
					if (z.Manual)
					{
						csv.AppendLine(dateText + "," + AsOfCT + ",MANUAL,,,," + JN(z.Lo, 2) + "," + JN(z.Hi, 2) + ",MANUAL," + z.Label);
						continue;
					}
					foreach (Level l in z.Levels)
						csv.AppendLine(dateText + "," + AsOfCT + "," + l.Name + "," + l.Family + "," + l.Kind + "," + JN(l.Price, 2) + "," + JN(z.Lo, 2) + "," + JN(z.Hi, 2) + "," + z.Tier + "," + z.Label);
				}
				foreach (Level l in m.Levels)
					if (!l.InZones) csv.AppendLine(dateText + "," + AsOfCT + "," + l.Name + "," + l.Family + "," + l.Kind + "," + JN(l.Price, 2) + ",,,NOT_IN_ZONES,");
				File.AppendAllText(levelsPath, csv.ToString());
			}
			catch (Exception ex)
			{
				lastError = "Write failed: " + ex.Message;
			}
		}

		// ==============================================================================
		//  Drawing
		// ==============================================================================
		private void DrawPending()
		{
			if (maps.Count == 0) return;
			bool ready = State == State.Realtime || CurrentBars[0] >= BarsArray[0].Count - 2;
			if (!ready) return;
			int first = Math.Max(0, maps.Count - Math.Max(1, MaxDaysDrawn));
			for (int i = first; i < maps.Count; i++)
			{
				DayMap m = maps[i];
				if (m.Drawn) continue;
				m.Drawn = true;
				DateTime x1 = ToLocal(m.AsOfCt);
				DateTime x2 = ToLocal(m.CashEndCt);
				string d = m.Date.ToString("yyyyMMdd", CultureInfo.InvariantCulture);
				int zi = 0;
				foreach (Zone z in m.Zones)
				{
					zi++;
					if (z.Tier == "TARGET" && !ShowTargetZones) continue;
					Brush b = z.Manual ? ManualZoneBrush : (z.Tier == "DECISION" ? ZoneBrush : TargetZoneBrush);
					string tag = "JPM_" + d + "_Z" + zi.ToString(CultureInfo.InvariantCulture);
					if (ShowZones)
					{
						Draw.Rectangle(this, tag, false, x1, z.Lo, x2, z.Hi, b, b, z.Tier == "TARGET" ? Math.Max(1, ZoneOpacity / 2) : ZoneOpacity);
						Draw.Text(this, tag + "_T", false, z.Label + "  " + JN(z.Lo, 2) + "-" + JN(z.Hi, 2), x1, z.Hi, 8, Brushes.Gainsboro,
							labelFont, TextAlignment.Left, Brushes.Transparent, Brushes.Transparent, 0);
					}
					if (ShowLevelLines && !z.Manual)
					{
						int li = 0;
						foreach (Level l in z.Levels)
						{
							li++;
							Draw.Line(this, tag + "_L" + li.ToString(CultureInfo.InvariantCulture), false, x1, l.Price, x2, l.Price, LevelBrush, DashStyleHelper.Dot, 1);
						}
					}
				}
			}
		}

		private string BuildStatus()
		{
			StringBuilder sb = new StringBuilder();
			sb.Append("Jeron Pre-open Map v").Append(Version).Append("  |  as-of ").Append(AsOfCT).Append(" CT  |  tick data from ").Append(firstTickCt == DateTime.MinValue ? "none" : JTime(firstTickCt)).AppendLine();
			sb.Append("Delta profile: ").Append(volType != null ? "on (through " + JTime(deltaThroughCt) + ")" : "off").Append("  |  ES: ").Append(esIdx > 0 ? (double.IsNaN(esLast) ? "no data" : EsInstrument + " " + JN(esLast, 2)) : "off").AppendLine();
			sb.Append("HTF: ").Append(htfIdx > 0 ? "1-min " + htfMinDays.Count.ToString(CultureInfo.InvariantCulture) + " day(s) through " + JTime(htfThroughCt) : "tick days only")
				.Append("  |  half days: ").Append(halfDays.Count.ToString(CultureInfo.InvariantCulture)).AppendLine();
			if (maps.Count == 0)
			{
				sb.AppendLine(firstTickCt == DateTime.MinValue
					? "WARNING: no 1-tick data received. Load tick history (Days to load 10+) or connect Playback."
					: "No map built yet: waiting for the first tick at or after " + AsOfCT + " CT.");
			}
			else
			{
				DayMap m = maps[maps.Count - 1];
				int dec = 0;
				foreach (Zone z in m.Zones) if (z.Tier == "DECISION") dec++;
				sb.Append("Last map: ").Append(m.Date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture)).Append("  zones ").Append(m.Zones.Count.ToString(CultureInfo.InvariantCulture))
					.Append(" (").Append(dec.ToString(CultureInfo.InvariantCulture)).Append(" decision)  levels ").Append(m.Levels.Count.ToString(CultureInfo.InvariantCulture))
					.Append("  areas ").Append(m.Areas.Count.ToString(CultureInfo.InvariantCulture)).Append("  maps this run ").Append(maps.Count.ToString(CultureInfo.InvariantCulture)).AppendLine();
				foreach (string note in m.Notes) sb.Append("note: ").AppendLine(note);
			}
			if (outFolder.Length > 0) sb.Append("Output folder: ").AppendLine(outFolder);
			if (lastError.Length > 0) sb.Append("ERROR: ").AppendLine(lastError);
			return sb.ToString();
		}

		// ==============================================================================
		//  Helpers
		// ==============================================================================
		private static long FloorDiv(long a, int b)
		{
			long q = a / b;
			if ((a % b != 0) && ((a < 0) != (b < 0))) q--;
			return q;
		}

		private static string Q(string s)
		{
			if (s == null) return "null";
			StringBuilder sb = new StringBuilder("\"");
			foreach (char c in s)
			{
				if (c == '"') sb.Append("\\\"");
				else if (c == '\\') sb.Append("\\\\");
				else if (c == '\n') sb.Append("\\n");
				else if (c == '\r') sb.Append("\\r");
				else if (c == '\t') sb.Append("\\t");
				else if (c < ' ') sb.Append("\\u").Append(((int)c).ToString("x4"));
				else sb.Append(c);
			}
			return sb.Append("\"").ToString();
		}

		private static string Num(double x)
		{
			if (double.IsNaN(x) || double.IsInfinity(x) || x == double.MaxValue || x == double.MinValue) return "null";
			return Math.Round(x, 4).ToString("0.####", CultureInfo.InvariantCulture);
		}

		private static string KV(string k, string v) { return Q(k) + ":" + v; }
		private static string Obj(params string[] kv) { return "{" + string.Join(",", kv) + "}"; }
		private static string Arr(List<string> items) { return "[" + string.Join(",", items.ToArray()) + "]"; }

		private static List<string> QList(List<string> items)
		{
			List<string> r = new List<string>();
			foreach (string s in items) r.Add(Q(s));
			return r;
		}

		private void ParseHolidays()
		{
			holidays.Clear();
			if (string.IsNullOrWhiteSpace(HolidayDates)) return;
			foreach (string raw in HolidayDates.Split(new char[] { ';', ',', ' ', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries))
			{
				DateTime d;
				if (DateTime.TryParseExact(raw.Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d)) holidays.Add(d.Date);
				else lastError = "Could not parse holiday date '" + raw + "'";
			}
		}

		private void ParseManualZones()
		{
			manualDefs.Clear();
			if (string.IsNullOrWhiteSpace(ManualZones)) return;
			foreach (string raw in ManualZones.Split(new char[] { ';', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries))
			{
				string entry = raw.Trim();
				if (entry.Length == 0 || entry.StartsWith("#")) continue;
				ManualDef md = new ManualDef();
				int at = entry.IndexOf('@');
				if (at > 0)
				{
					DateTime d;
					if (DateTime.TryParseExact(entry.Substring(0, at).Trim(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out d)) { md.HasDate = true; md.Date = d.Date; }
					entry = entry.Substring(at + 1).Trim();
				}
				string label = "MANUAL";
				int colon = entry.IndexOf(':');
				if (colon > 0)
				{
					label = SafeToken(entry.Substring(colon + 1).Trim().ToUpperInvariant());
					entry = entry.Substring(0, colon).Trim();
				}
				string[] bounds = entry.Split('-');
				double a, b;
				if (bounds.Length != 2
					|| !double.TryParse(bounds[0].Replace(",", "").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out a)
					|| !double.TryParse(bounds[1].Replace(",", "").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out b))
				{
					lastError = "Could not parse manual zone '" + raw + "'";
					continue;
				}
				md.Lo = Math.Min(a, b);
				md.Hi = Math.Max(a, b);
				md.Label = label;
				manualDefs.Add(md);
			}
		}

		private DateTime ToCentral(DateTime local)
		{
			if (centralTz == null || localTz == null || centralTz.Id == localTz.Id) return local;
			try { return TimeZoneInfo.ConvertTime(DateTime.SpecifyKind(local, DateTimeKind.Unspecified), localTz, centralTz); }
			catch { return local; }
		}

		private DateTime ToLocal(DateTime ct)
		{
			if (centralTz == null || localTz == null || centralTz.Id == localTz.Id) return ct;
			try { return TimeZoneInfo.ConvertTime(DateTime.SpecifyKind(ct, DateTimeKind.Unspecified), centralTz, localTz); }
			catch { return ct; }
		}

		private static int ParseHhmm(string text, int fallback)
		{
			if (string.IsNullOrWhiteSpace(text)) return fallback;
			string[] p = text.Trim().Split(':');
			int h, mm;
			if (p.Length != 2 || !int.TryParse(p[0], out h) || !int.TryParse(p[1], out mm) || h < 0 || h > 23 || mm < 0 || mm > 59) return fallback;
			return h * 60 + mm;
		}

		private double RoundTick(double p) { return Math.Round(p / tickSize) * tickSize; }
		private double FloorTick(double p) { return Math.Floor(p / tickSize + 1e-9) * tickSize; }
		private double CeilTick(double p) { return Math.Ceiling(p / tickSize - 1e-9) * tickSize; }

		private static string JN(double x, int decimals)
		{
			if (double.IsNaN(x)) return "";
			return x.ToString("F" + decimals.ToString(CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
		}

		private static string JTime(DateTime t)
		{
			return t == DateTime.MinValue ? "n/a" : t.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + " CT";
		}

		private static string SafeToken(string s)
		{
			StringBuilder sb = new StringBuilder();
			foreach (char c in s ?? "") sb.Append(char.IsLetterOrDigit(c) ? c : '_');
			return sb.Length > 0 ? sb.ToString() : "NA";
		}

		// v2.2: write to <name>.tmp, then rename over the final name, so a reader (Google Drive sync, the 08:21
		// Claude run) only ever sees a complete file.
		private static void WriteAtomic(string path, string text)
		{
			string tmp = path + ".tmp";
			File.WriteAllText(tmp, text, new UTF8Encoding(false));
			if (File.Exists(path)) File.Replace(tmp, path, null);
			else File.Move(tmp, path);
		}

		// ==============================================================================
		//  Properties
		// ==============================================================================
		#region Properties
		// ---- 1. Timing ----
		[Display(Name = "As-of time (CT, HH:mm)", Description = "The map and packet are frozen on the first tick at or after this time, from earlier data only. Automated morning (prompt v1.5): 08:10 (Claude's plan run starts 08:11; the strategy activates the plan at 08:25).", Order = 1, GroupName = "1. Timing (Central Time)")]
		public string AsOfCT { get; set; }

		[Display(Name = "Cash session start (CT)", Order = 2, GroupName = "1. Timing (Central Time)")]
		public string CashStartCT { get; set; }

		[Display(Name = "Cash session end (CT)", Order = 3, GroupName = "1. Timing (Central Time)")]
		public string CashEndCT { get; set; }

		[Display(Name = "Futures session start (CT)", Order = 4, GroupName = "1. Timing (Central Time)")]
		public string SessionStartCT { get; set; }

		[Display(Name = "Settlement time (CT)", Description = "CME equity index settlement: VWAP of the 30 s before this time.", Order = 5, GroupName = "1. Timing (Central Time)")]
		public string SettlementCT { get; set; }

		[Display(Name = "Build from date (yyyy-MM-dd, blank = all loaded days)", Order = 6, GroupName = "1. Timing (Central Time)")]
		public string BuildFromDate { get; set; }

		// ---- 2. Profiles ----
		[Range(0, 10)]
		[Display(Name = "Prior cash sessions in zones", Order = 1, GroupName = "2. Profiles")]
		public int PriorCashSessions { get; set; }

		[Range(1, 100)]
		[Display(Name = "Value area (%)", Description = "Jeron: 70%.", Order = 2, GroupName = "2. Profiles")]
		public double ValueAreaPct { get; set; }

		[Range(1, 100)]
		[Display(Name = "Volume profile ticks per row", Description = "RESEARCH PARAMETER. 1 = exact.", Order = 3, GroupName = "2. Profiles")]
		public int TicksPerRow { get; set; }

		[Display(Name = "Prior day high/low", Order = 4, GroupName = "2. Profiles")]
		public bool IncludePriorDayHighLow { get; set; }

		[Display(Name = "Prior day settlement", Order = 5, GroupName = "2. Profiles")]
		public bool IncludeSettlement { get; set; }

		[Display(Name = "Overnight VAH/POC/VAL", Order = 6, GroupName = "2. Profiles")]
		public bool IncludeOvernight { get; set; }

		[Display(Name = "Overnight high/low", Order = 7, GroupName = "2. Profiles")]
		public bool IncludeOvernightHighLow { get; set; }

		[Display(Name = "Session VWAP (packet)", Order = 8, GroupName = "2. Profiles")]
		public bool IncludeVwap { get; set; }

		[Display(Name = "VWAP 1 SD bands", Order = 9, GroupName = "2. Profiles")]
		public bool IncludeVwapBand1 { get; set; }

		[Display(Name = "VWAP 2 SD bands", Order = 10, GroupName = "2. Profiles")]
		public bool IncludeVwapBand2 { get; set; }

		[Display(Name = "Developing weekly profile", Order = 11, GroupName = "2. Profiles")]
		public bool IncludeWeekly { get; set; }

		[Display(Name = "Prior-week profile", Description = "Jeron's key level on Jul 31: last week's value area low.", Order = 12, GroupName = "2. Profiles")]
		public bool IncludePriorWeek { get; set; }

		[Display(Name = "TPO profiles (30-min periods)", Order = 13, GroupName = "2. Profiles")]
		public bool IncludeTpo { get; set; }

		[Range(1, 400)]
		[Display(Name = "TPO row size (ticks)", Description = "RESEARCH PARAMETER. 20 ticks = 5 NQ points.", Order = 14, GroupName = "2. Profiles")]
		public int TpoTicksPerRow { get; set; }

		[Range(1, 50)]
		[Display(Name = "Single print: min rows", Description = "RESEARCH PARAMETER.", Order = 15, GroupName = "2. Profiles")]
		public int MinSinglePrintRows { get; set; }

		[Display(Name = "Skip profiles not fully covered by loaded data", Order = 16, GroupName = "2. Profiles")]
		public bool SkipPartialProfiles { get; set; }

		[Range(1, 600)]
		[Display(Name = "Data gap threshold (minutes)", Order = 17, GroupName = "2. Profiles")]
		public int MaxTickGapMinutes { get; set; }

		[Display(Name = "Holiday dates (yyyy-MM-dd, ; or ,)", Order = 18, GroupName = "2. Profiles")]
		public string HolidayDates { get; set; }

		[Display(Name = "Half-day dates (yyyy-MM-dd@HH:mm CT cash end)", Description = "v2.3. Early-close days: cash session and settlement end at the time given; the stop 15 minutes later until 17:00 CT is a normal break, not a data gap. Check the CME holiday calendar each year.", Order = 19, GroupName = "2. Profiles")]
		public string HalfDayDates { get; set; }

		[Range(10, 400)]
		[Display(Name = "Keep tick days (calendar)", Description = "v2.3. Days of tick-built statistics kept in memory (was fixed at 45).", Order = 20, GroupName = "2. Profiles")]
		public int KeepTickDays { get; set; }

		// ---- 3. Zones ----
		[Range(0, 1000)]
		[Display(Name = "Merge distance (points)", Description = "RESEARCH PARAMETER.", Order = 1, GroupName = "3. Zones (research parameters)")]
		public double MergeDistancePoints { get; set; }

		[Range(0, 1000)]
		[Display(Name = "Zone padding (points)", Description = "RESEARCH PARAMETER.", Order = 2, GroupName = "3. Zones (research parameters)")]
		public double ZonePadPoints { get; set; }

		[Range(0, 10000)]
		[Display(Name = "Max zone width before padding (points, 0 = no cap)", Order = 3, GroupName = "3. Zones (research parameters)")]
		public double MaxZoneWidthPoints { get; set; }

		[Range(0, 100000)]
		[Display(Name = "Max distance from price (points, 0 = keep all)", Order = 4, GroupName = "3. Zones (research parameters)")]
		public double MaxDistancePoints { get; set; }

		[Range(1, 10)]
		[Display(Name = "Decision zone: min independent periods", Description = "RESEARCH PARAMETER. Periods = PD, PD2, PD3, ON, WK, PWK, settlement. Fewer = target-only zone (T_).", Order = 5, GroupName = "3. Zones (research parameters)")]
		public int MinSourcesForDecision { get; set; }

		[Display(Name = "Session VWAP in zones", Description = "Off: the tracker computes VWAP live; a frozen VWAP goes stale.", Order = 6, GroupName = "3. Zones (research parameters)")]
		public bool IncludeVwapInZones { get; set; }

		[Display(Name = "Weekly VWAP in zones", Order = 7, GroupName = "3. Zones (research parameters)")]
		public bool IncludeWeeklyVwapInZones { get; set; }

		[Display(Name = "PD2/PD3 high-low (v2.3)", Description = "Cash highs and lows of PD2 and PD3 as levels (families PD2, PD3).", Order = 9, GroupName = "3. Zones (research parameters)")]
		public bool IncludePriorHighLowAll { get; set; }

		[Display(Name = "Settlement family (SET or PD)", Description = "v2.3 RESEARCH OPTION. SET = the PD settlement counts as its own independent period (unchanged). PD = same period as the prior day, so PD POC + settlement alone is a TARGET zone. For the backtest comparison.", Order = 10, GroupName = "3. Zones (research parameters)")]
		public string SettlementFamily { get; set; }

		[Display(Name = "Manual zones", Description = "[yyyy-MM-dd@]low-high:LABEL; ...  Supply/demand, single prints from TradingView, etc.", Order = 8, GroupName = "3. Zones (research parameters)")]
		public string ManualZones { get; set; }

		// ---- 4. Review packet ----
		[Display(Name = "Write review packet (JSON)", Order = 1, GroupName = "4. Review packet")]
		public bool WritePacket { get; set; }

		[Range(1, 30)]
		[Display(Name = "1-hour structure: days", Order = 2, GroupName = "4. Review packet")]
		public int StructureDays { get; set; }

		[Range(1, 10)]
		[Display(Name = "Swing strength (hours each side)", Description = "RESEARCH PARAMETER.", Order = 3, GroupName = "4. Review packet")]
		public int SwingStrength { get; set; }

		[Range(1, 60)]
		[Display(Name = "Composite days (HVN/LVN)", Description = "RESEARCH PARAMETER.", Order = 4, GroupName = "4. Review packet")]
		public int CompositeDays { get; set; }

		[Range(1, 400)]
		[Display(Name = "HVN/LVN row size (ticks)", Order = 5, GroupName = "4. Review packet")]
		public int HvnTicksPerRow { get; set; }

		[Range(1, 100)]
		[Display(Name = "HVN threshold (% of peak)", Description = "RESEARCH PARAMETER.", Order = 6, GroupName = "4. Review packet")]
		public double HvnPct { get; set; }

		[Range(1, 100)]
		[Display(Name = "LVN threshold (% of peak)", Description = "RESEARCH PARAMETER.", Order = 7, GroupName = "4. Review packet")]
		public double LvnPct { get; set; }

		[Range(1, 100)]
		[Display(Name = "Inventory net long at (% ON volume above settle)", Description = "RESEARCH PARAMETER.", Order = 8, GroupName = "4. Review packet")]
		public double InventoryLongPct { get; set; }

		[Range(0, 99)]
		[Display(Name = "Inventory net short at (% ON volume above settle)", Description = "RESEARCH PARAMETER.", Order = 9, GroupName = "4. Review packet")]
		public double InventoryShortPct { get; set; }

		[Range(0, 100)]
		[Display(Name = "Migration: overlap below this % = directional", Description = "RESEARCH PARAMETER.", Order = 10, GroupName = "4. Review packet")]
		public double MigrationOverlapPct { get; set; }

		[Display(Name = "Delta profile (adds 1-min Volumetric series)", Description = "Needs Order Flow+.", Order = 11, GroupName = "4. Review packet")]
		public bool IncludeDeltaProfile { get; set; }

		[Range(1, 400)]
		[Display(Name = "Delta profile row size (ticks)", Order = 12, GroupName = "4. Review packet")]
		public int DeltaRowTicks { get; set; }

		[Display(Name = "ES cross-check (adds ES 1-min series)", Order = 13, GroupName = "4. Review packet")]
		public bool IncludeEs { get; set; }

		[Display(Name = "ES contract", Description = "Update at the roll, e.g. ES 03-27.", Order = 14, GroupName = "4. Review packet")]
		public string EsInstrument { get; set; }

		[Range(1, 100)]
		[Display(Name = "ES approx profile row (ticks)", Order = 15, GroupName = "4. Review packet")]
		public int EsTicksPerRow { get; set; }

		[Range(1, 90)]
		[Display(Name = "HTF composite days (v2.1)", Description = "Complete trading days in the higher-timeframe composite. v2.3 default 60 (about 3 months; Jeron uses a 2-3 month composite). Max 90 from 1-minute bars, 44 from tick days.", Order = 16, GroupName = "4. Review packet")]
		public int HtfCompositeDays { get; set; }

		[Range(1, 90)]
		[Display(Name = "HTF composite: min days for zones", Description = "RESEARCH PARAMETER. Fewer days = packet only, not in the zones.", Order = 17, GroupName = "4. Review packet")]
		public int HtfMinDays { get; set; }

		[Display(Name = "HTF levels join the zones", Order = 18, GroupName = "4. Review packet")]
		public bool IncludeHtfInZones { get; set; }

		[Display(Name = "Manual HTF levels", Description = "From a 2-3 month TradingView composite or the all-time-high profile. v2.3: put the date you read them first, e.g. 2026-10-20@VAH=31600; POC=31200; ATHPOC=31800. Used from that trading date on. Family HTF.", Order = 19, GroupName = "4. Review packet")]
		public string HtfLevels { get; set; }

		[Range(1, 40)]
		[Display(Name = "Swing profile: look-back days", Description = "RESEARCH PARAMETER. The swing anchor is the later of the highest high / lowest low in this window.", Order = 20, GroupName = "4. Review packet")]
		public int SwingAnchorDays { get; set; }

		[Display(Name = "HTF from 1-minute bars (v2.3)", Description = "Adds a 1-minute series of the chart instrument loaded for 'HTF load days' (independent of the chart's Days to load). Volume at price is approximate (spread over each minute's range).", Order = 21, GroupName = "4. Review packet")]
		public bool HtfFromMinuteBars { get; set; }

		[Range(10, 400)]
		[Display(Name = "HTF load days (calendar)", Order = 22, GroupName = "4. Review packet")]
		public int HtfLoadDays { get; set; }

		[Display(Name = "HTF trading hours template", Description = "Trading hours of the 1-minute series. Blank = the instrument default.", Order = 23, GroupName = "4. Review packet")]
		public string HtfTradingHours { get; set; }

		[Range(1, 1440)]
		[Display(Name = "HTF: min 1-minute bars for a complete day", Description = "RESEARCH PARAMETER. Days with fewer bars are left out of the composite (3/4 of it on half days).", Order = 24, GroupName = "4. Review packet")]
		public int HtfMinMinutesPerDay { get; set; }

		[Range(1, 365)]
		[Display(Name = "Manual HTF max age (days)", Description = "Dated manual HTF levels older than this are flagged stale in the packet.", Order = 25, GroupName = "4. Review packet")]
		public int HtfManualMaxAgeDays { get; set; }

		// ---- 5. Output ----
		[Display(Name = "Write files", Order = 1, GroupName = "5. Output")]
		public bool WriteFiles { get; set; }

		[Display(Name = "Output folder (blank = Drive Preopen Exchange\\zones)", Description = "Default: G:\\My Drive\\NT DATA\\research logs\\Jeron\\Preopen Exchange\\zones (the Drive folder the 08:21 Claude run reads).", Order = 2, GroupName = "5. Output")]
		public string OutputFolder { get; set; }

		[Display(Name = "Print paste line to Output window", Order = 3, GroupName = "5. Output")]
		public bool PrintPasteLine { get; set; }

		// ---- 6. Display ----
		[Display(Name = "Show zones", Order = 1, GroupName = "6. Display")]
		public bool ShowZones { get; set; }

		[Display(Name = "Show target-only zones", Order = 2, GroupName = "6. Display")]
		public bool ShowTargetZones { get; set; }

		[Display(Name = "Show level lines inside zones", Order = 3, GroupName = "6. Display")]
		public bool ShowLevelLines { get; set; }

		[Display(Name = "Status panel", Order = 4, GroupName = "6. Display")]
		public bool ShowStatusPanel { get; set; }

		[Range(1, 100)]
		[Display(Name = "Days drawn", Order = 5, GroupName = "6. Display")]
		public int MaxDaysDrawn { get; set; }

		[Range(1, 100)]
		[Display(Name = "Zone opacity (%)", Order = 6, GroupName = "6. Display")]
		public int ZoneOpacity { get; set; }

		[XmlIgnore]
		[Display(Name = "Decision zone color", Order = 7, GroupName = "6. Display")]
		public Brush ZoneBrush { get; set; }

		[Browsable(false)]
		public string ZoneBrushSerializable
		{
			get { return Serialize.BrushToString(ZoneBrush); }
			set { ZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Target zone color", Order = 8, GroupName = "6. Display")]
		public Brush TargetZoneBrush { get; set; }

		[Browsable(false)]
		public string TargetZoneBrushSerializable
		{
			get { return Serialize.BrushToString(TargetZoneBrush); }
			set { TargetZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Manual zone color", Order = 9, GroupName = "6. Display")]
		public Brush ManualZoneBrush { get; set; }

		[Browsable(false)]
		public string ManualZoneBrushSerializable
		{
			get { return Serialize.BrushToString(ManualZoneBrush); }
			set { ManualZoneBrush = Serialize.StringToBrush(value); }
		}

		[XmlIgnore]
		[Display(Name = "Level line color", Order = 10, GroupName = "6. Display")]
		public Brush LevelBrush { get; set; }

		[Browsable(false)]
		public string LevelBrushSerializable
		{
			get { return Serialize.BrushToString(LevelBrush); }
			set { LevelBrush = Serialize.StringToBrush(value); }
		}
		#endregion
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private JeronPreopenMap[] cacheJeronPreopenMap;
		public JeronPreopenMap JeronPreopenMap()
		{
			return JeronPreopenMap(Input);
		}

		public JeronPreopenMap JeronPreopenMap(ISeries<double> input)
		{
			if (cacheJeronPreopenMap != null)
				for (int idx = 0; idx < cacheJeronPreopenMap.Length; idx++)
					if (cacheJeronPreopenMap[idx] != null &&  cacheJeronPreopenMap[idx].EqualsInput(input))
						return cacheJeronPreopenMap[idx];
			return CacheIndicator<JeronPreopenMap>(new JeronPreopenMap(), input, ref cacheJeronPreopenMap);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.JeronPreopenMap JeronPreopenMap()
		{
			return indicator.JeronPreopenMap(Input);
		}

		public Indicators.JeronPreopenMap JeronPreopenMap(ISeries<double> input )
		{
			return indicator.JeronPreopenMap(input);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.JeronPreopenMap JeronPreopenMap()
		{
			return indicator.JeronPreopenMap(Input);
		}

		public Indicators.JeronPreopenMap JeronPreopenMap(ISeries<double> input )
		{
			return indicator.JeronPreopenMap(input);
		}
	}
}

#endregion
