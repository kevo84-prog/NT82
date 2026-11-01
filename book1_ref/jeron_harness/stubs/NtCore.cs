// NinjaTrader 8 stand-ins for the Jeron backtest harness (JeronHarness v0.1, Oct 24 2026).
// Only what the Jeron scripts use. Behaviour follows NinjaTrader 8 (Tick Replay, Calculate.OnEachTick / OnBarClose,
// time-based bars stamped at their END time, BarsAgo indexing, managed orders).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace NinjaTrader.Core
{
	public class GeneralOptionsClass { public TimeZoneInfo TimeZoneInfo = Globals.Central; }
	public static class Globals
	{
		public static TimeZoneInfo Central = FindCentral();
		static TimeZoneInfo FindCentral()
		{
			foreach (var id in new[] { "Central Standard Time", "America/Chicago" })
				try { return TimeZoneInfo.FindSystemTimeZoneById(id); } catch { }
			return TimeZoneInfo.Local;
		}
		public static GeneralOptionsClass GeneralOptions = new GeneralOptionsClass();
		public static string UserDataDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "nt_harness_userdata");
		public static object DirectWriteFactory = null;
		public static object D2DFactory = null;
		public static DateTime Now { get { return Harness.HarnessClock.Now; } }
	}
}

namespace NinjaTrader.Harness
{
	public static class HarnessClock { public static DateTime Now = DateTime.Now; }
}

namespace NinjaTrader.Cbi
{
	public enum MarketPosition { Flat, Long, Short }
	public enum OrderAction { Buy, BuyToCover, Sell, SellShort }
	public enum OrderType { Limit, Market, MIT, StopLimit, StopMarket }
	public enum OrderState { Accepted, Cancelled, ChangePending, ChangeSubmitted, CancelPending, CancelSubmitted, Filled, Initialized, PartFilled, Rejected, Submitted, TriggerPending, Unknown, Working }
	public enum ErrorCode { NoError, OrderRejected, UnableToCancelOrder, UnableToChangeOrder, UnableToSubmitOrder, UserAbort, LoginFailed, ServerConnectionIsBroken }
	public enum Currency { UsDollar }
	public enum InstrumentType { Future, Stock, Index, Forex, Option, Cfd, CryptoCurrency, Unknown }

	public class MasterInstrument
	{
		public string Name = "NQ";
		public double TickSize = 0.25;
		public double PointValue = 20.0;
		public InstrumentType InstrumentType = InstrumentType.Future;
		public double RoundToTickSize(double p) { return Math.Round(p / TickSize) * TickSize; }
		public string FormatPrice(double p) { return p.ToString("0.00", CultureInfo.InvariantCulture); }
		public override string ToString() { return Name; }
	}
	public class Instrument
	{
		public string FullName = "NQ 12-26";
		public MasterInstrument MasterInstrument = new MasterInstrument();
		public DateTime Expiry = DateTime.MinValue;
		public override string ToString() { return FullName; }
	}
	public class Account
	{
		public string Name = "Sim101";
		public Provider Provider = Provider.Simulator;
		public string DisplayName { get { return Name; } }
		public override string ToString() { return Name; }
	}
	public class Order
	{
		public string Name = "";
		public string FromEntrySignal = "";
		public OrderAction OrderAction;
		public OrderType OrderType;
		public OrderState OrderState = OrderState.Initialized;
		public int Quantity = 1;
		public int Filled;
		public double LimitPrice, StopPrice, AverageFillPrice;
		public DateTime Time;
		public string OrderId = Guid.NewGuid().ToString("N").Substring(0, 12);
		public bool IsLong { get { return OrderAction == OrderAction.Buy || OrderAction == OrderAction.BuyToCover; } }
		public bool IsShort { get { return !IsLong; } }
		public override string ToString() { return Name + " " + OrderAction + " " + OrderType + " " + OrderState; }
	}
	public class Execution
	{
		public Order Order;
		public double Price;
		public int Quantity;
		public DateTime Time;
		public MarketPosition MarketPosition;
		public string Name { get { return Order != null ? Order.Name : ""; } }
		public string ExecutionId = Guid.NewGuid().ToString("N").Substring(0, 12);
	}
	public class Position
	{
		public MarketPosition MarketPosition = MarketPosition.Flat;
		public int Quantity;
		public double AveragePrice;
		public Instrument Instrument;
		public double GetUnrealizedProfitLoss(NinjaTrader.Cbi.PerformanceUnit unit, double price)
		{
			if (MarketPosition == MarketPosition.Flat) return 0;
			double pts = (price - AveragePrice) * (MarketPosition == MarketPosition.Long ? 1 : -1) * Quantity;
			if (unit == PerformanceUnit.Ticks) return pts / (Instrument != null ? Instrument.MasterInstrument.TickSize : 0.25);
			if (unit == PerformanceUnit.Points) return pts;
			return pts * (Instrument != null ? Instrument.MasterInstrument.PointValue : 20.0);
		}
	}
	public enum PerformanceUnit { Currency, Percent, Pips, Points, Ticks }
}

namespace NinjaTrader.Data
{
	public enum MarketDataType { Ask, Bid, DailyHigh, DailyLow, DailyVolume, Last, LastClose, Opening, OpenInterest, Settlement, Unknown }
	public enum Operation { Add, Update, Remove }
	public enum BarsPeriodType { Tick = 0, Volume = 1, Second = 2, Minute = 4, Day = 5, Week = 6, Month = 7, Year = 8, Range = 3, Volumetric = 9 }
	public enum MergePolicy { DoNotMerge, MergeBackAdjusted, MergeNonBackAdjusted, UseGlobalSettings }

	public class BarsPeriod
	{
		public BarsPeriodType BarsPeriodType = BarsPeriodType.Minute;
		public BarsPeriodType BaseBarsPeriodType = BarsPeriodType.Minute;
		public int Value = 1;
		public int BaseBarsPeriodValue = 1;
		public override string ToString() { return Value + " " + BarsPeriodType; }
	}

	public class MarketDataEventArgs : EventArgs
	{
		public MarketDataType MarketDataType;
		public double Price;
		public long Volume;
		public DateTime Time;
		public double Bid, Ask;
		public NinjaTrader.Cbi.Instrument Instrument;
		public override string ToString() { return MarketDataType + " " + Price + " " + Volume + " " + Time.ToString("HH:mm:ss.fff"); }
	}
	public class MarketDepthEventArgs : EventArgs
	{
		public MarketDataType MarketDataType;
		public Operation Operation;
		public int Position;
		public double Price;
		public long Volume;
		public DateTime Time;
		public bool IsReset;
		public string MarketMaker = "";
		public NinjaTrader.Cbi.Instrument Instrument;
	}

	/// <summary>One time-based bar series. Bars are stamped at their END time, as NinjaTrader does.</summary>
	public class Bars
	{
		public readonly List<DateTime> T = new List<DateTime>();
		public readonly List<double> O = new List<double>(), H = new List<double>(), L = new List<double>(), C = new List<double>();
		public readonly List<long> V = new List<long>();
		public readonly List<bool> FirstOfSession = new List<bool>();
		public NinjaTrader.Cbi.Instrument Instrument = new NinjaTrader.Cbi.Instrument();
		public BarsPeriod BarsPeriod = new BarsPeriod();
		public bool IsTickReplay = true;
		public BarsSeries BarsSeries = new BarsSeries();
		public TradingHours TradingHours = TradingHours.CmeUsIndexEth;
		public int Count { get { return T.Count; } }
		public int CurrentIndex = -1;     // bar being processed (== CurrentBar for this series)
		public bool IsFirstBarOfSession { get { return CurrentIndex >= 0 && CurrentIndex < FirstOfSession.Count && FirstOfSession[CurrentIndex]; } }
		public bool IsFirstBarOfSessionByIndex(int i) { return i >= 0 && i < FirstOfSession.Count && FirstOfSession[i]; }
		public DateTime GetTime(int i) { return T[i]; }
		public double GetOpen(int i) { return O[i]; }
		public double GetHigh(int i) { return H[i]; }
		public double GetLow(int i) { return L[i]; }
		public double GetClose(int i) { return C[i]; }
		public long GetVolume(int i) { return V[i]; }
		public DateTime GetSessionEndTime(int i) { return TradingHours.SessionEnd(T[i]); }
		/// <summary>NinjaTrader semantics: index of the first bar whose time stamp is at or after t (clamped).</summary>
		public int GetBar(DateTime t)
		{
			if (T.Count == 0) return -1;
			int lo = 0, hi = T.Count - 1;
			if (t >= T[hi]) return hi;
			while (lo < hi) { int mid = (lo + hi) / 2; if (T[mid] < t) lo = mid + 1; else hi = mid; }
			return lo;
		}
		public object BarsType { get { return BarsSeries.BarsType; } }
		public override string ToString() { return Instrument.FullName + " " + BarsPeriod; }
	}
	public class BarsSeries { public object BarsType = null; }

	/// <summary>CME US Index Futures ETH: Sun-Fri 17:00 -> 16:00 CT, trading day = the date the session ends.</summary>
	public class TradingHours
	{
		public static readonly TradingHours CmeUsIndexEth = new TradingHours { Name = "CME US Index Futures ETH" };
		public string Name;
		public TimeSpan Begin = new TimeSpan(17, 0, 0), End = new TimeSpan(16, 0, 0);
		public TimeZoneInfo TimeZoneInfo = NinjaTrader.Core.Globals.Central;
		public DateTime TradingDay(DateTime t)
		{
			DateTime d = t.TimeOfDay >= Begin ? t.Date.AddDays(1) : t.Date;
			while (d.DayOfWeek == DayOfWeek.Saturday || d.DayOfWeek == DayOfWeek.Sunday) d = d.AddDays(1);
			return d;
		}
		public DateTime SessionBegin(DateTime t)
		{
			DateTime td = TradingDay(t);
			DateTime prev = td.AddDays(-1);
			while (prev.DayOfWeek == DayOfWeek.Saturday) prev = prev.AddDays(-1);
			if (td.DayOfWeek == DayOfWeek.Monday) prev = td.AddDays(-1);   // Sunday 17:00
			return prev.Date + Begin;
		}
		public DateTime SessionEnd(DateTime t) { return TradingDay(t).Date + End; }
		public override string ToString() { return Name; }
	}

	public class SessionIterator
	{
		readonly TradingHours th;
		public DateTime ActualSessionBegin, ActualSessionEnd, ActualTradingDayExchange, ActualTradingDayEndLocal;
		public SessionIterator(Bars bars) { th = bars != null ? bars.TradingHours : TradingHours.CmeUsIndexEth; }
		public SessionIterator(TradingHours hours) { th = hours ?? TradingHours.CmeUsIndexEth; }
		public DateTime GetTradingDay(DateTime t) { return th.TradingDay(t); }
		public bool GetNextSession(DateTime t, bool includesEndTimeStamp)
		{
			DateTime probe = t;
			if (includesEndTimeStamp && th.SessionEnd(t) == t) probe = t;   // a bar stamped exactly at the end belongs to that session
			ActualSessionBegin = th.SessionBegin(probe);
			ActualSessionEnd = th.SessionEnd(probe);
			if (!includesEndTimeStamp && t >= ActualSessionEnd) { ActualSessionBegin = th.SessionBegin(t.AddSeconds(1)); ActualSessionEnd = th.SessionEnd(t.AddSeconds(1)); }
			ActualTradingDayExchange = th.TradingDay(probe);
			ActualTradingDayEndLocal = ActualSessionEnd;
			return true;
		}
		public bool IsInSession(DateTime t, bool includesEndTimeStamp, bool isIntraday)
		{
			DateTime b = th.SessionBegin(t), e = th.SessionEnd(t);
			return t > b && (includesEndTimeStamp ? t <= e : t < e);
		}
		public DateTime GetTradingDayBeginLocal(DateTime td) { return th.SessionBegin(td.Date + new TimeSpan(12, 0, 0)); }
		public DateTime GetTradingDayEndLocal(DateTime td) { return td.Date + th.End; }
		public bool IsTradingDayDefined(DateTime d) { return d.DayOfWeek != DayOfWeek.Saturday && d.DayOfWeek != DayOfWeek.Sunday; }
	}
}
