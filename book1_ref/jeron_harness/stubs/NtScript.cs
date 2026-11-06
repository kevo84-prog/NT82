// NinjaScript base classes for the harness: series, bars context, events, managed orders, drawing no-ops.
using System;
using System.Collections.Generic;
using System.Globalization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;

namespace NinjaTrader.NinjaScript
{
	public enum State { SetDefaults, Configure, Active, DataLoaded, Historical, Transition, Realtime, Terminated, Finalized }
	public enum Calculate { OnBarClose, OnEachTick, OnPriceChange }
	public enum MaximumBarsLookBack { TwoHundredFiftySix, Infinite }
	public enum ScaleJustification { Left, Right, Overlay }
	public enum PlotStyle { Line, Bar, Block, Cross, Dot, Hash, HLine, PriceBox, Square, TriangleDown, TriangleLeft, TriangleRight, TriangleUp }
	public enum EntryHandling { AllEntries, UniqueEntries }
	public enum StartBehavior { AdoptAccountPosition, ImmediatelySubmit, ImmediatelySubmitSynchronizeAccount, WaitUntilFlat, WaitUntilFlatSynchronizeAccount }
	public enum StopTargetHandling { ByStrategyPosition, PerEntryExecution }
	public enum RealtimeErrorHandling { IgnoreAllErrors, StopCancelClose, StopCancelCloseIgnoreRejects }
	public enum CalculationMode { Currency, Percent, Pips, Price, Ticks }
	public enum OrderFillResolution { Standard, High }
	public enum LogLevel { Alert, Error, Information, Warning }
	public enum PrintTo { OutputTab1, OutputTab2 }
	public enum BarsRequiredToPlot { }

	public interface ISeries<T>
	{
		T this[int barsAgo] { get; }
		int Count { get; }
		T GetValueAt(int barIndex);
		bool IsValidDataPoint(int barsAgo);
		bool IsValidDataPointAt(int barIndex);
	}

	/// <summary>Value per bar of one bar series; [0] = the bar being processed.</summary>
	public class Series<T> : ISeries<T>
	{
		internal readonly List<T> Values = new List<T>();
		internal readonly List<bool> Set = new List<bool>();
		readonly NinjaScriptBase owner;
		readonly int barsIndex;
		public Series(NinjaScriptBase owner) : this(owner, MaximumBarsLookBack.TwoHundredFiftySix) { }
		public Series(NinjaScriptBase owner, MaximumBarsLookBack lookBack) { this.owner = owner; barsIndex = owner != null ? owner.BarsInProgress : 0; if (owner != null) owner.RegisterSeries(this, barsIndex); }
		internal void Grow(int count) { while (Values.Count < count) { Values.Add(default(T)); Set.Add(false); } }
		int Cur { get { return owner.CurrentBars[barsIndex]; } }
		public T this[int barsAgo]
		{
			get { int i = Cur - barsAgo; Grow(i + 1); return i >= 0 ? Values[i] : default(T); }
			set { int i = Cur - barsAgo; if (i < 0) return; Grow(i + 1); Values[i] = value; Set[i] = true; }
		}
		public int Count { get { return owner.BarsArray[barsIndex].Count; } }
		public T GetValueAt(int barIndex) { Grow(barIndex + 1); return Values[barIndex]; }
		public bool IsValidDataPoint(int barsAgo) { int i = Cur - barsAgo; return i >= 0 && i < Set.Count && Set[i]; }
		public bool IsValidDataPointAt(int barIndex) { return barIndex >= 0 && barIndex < Set.Count && Set[barIndex]; }
		public void Reset() { int i = Cur; if (i >= 0 && i < Set.Count) { Set[i] = false; Values[i] = default(T); } }
		public void Reset(int barsAgo) { int i = Cur - barsAgo; if (i >= 0 && i < Set.Count) { Set[i] = false; Values[i] = default(T); } }
	}

	/// <summary>Read-only price series over one Bars object (Open/High/Low/Close/Volume/Typical/Time).</summary>
	public class PriceSeries<T> : ISeries<T>
	{
		readonly NinjaScriptBase owner; readonly int fixedIdx; readonly Func<Bars, int, T> get;
		public PriceSeries(NinjaScriptBase owner, int fixedIdx, Func<Bars, int, T> get) { this.owner = owner; this.fixedIdx = fixedIdx; this.get = get; }
		int Idx { get { return fixedIdx >= 0 ? fixedIdx : owner.BarsInProgress; } }
		public T this[int barsAgo]
		{
			get
			{
				Bars b = owner.BarsArray[Idx];
				int i = owner.CurrentBars[Idx] - barsAgo;
				if (i < 0 || i >= b.Count) throw new ArgumentOutOfRangeException("barsAgo", "barsAgo " + barsAgo + " at bar " + owner.CurrentBars[Idx]);
				return get(b, i);
			}
		}
		public int Count { get { return owner.BarsArray[Idx].Count; } }
		public T GetValueAt(int barIndex) { return get(owner.BarsArray[Idx], barIndex); }
		public bool IsValidDataPoint(int barsAgo) { int i = owner.CurrentBars[Idx] - barsAgo; return i >= 0 && i < owner.BarsArray[Idx].Count; }
		public bool IsValidDataPointAt(int barIndex) { return barIndex >= 0 && barIndex < owner.BarsArray[Idx].Count; }
	}

	public class SeriesArray<T>
	{
		readonly Func<int, T> f; public SeriesArray(Func<int, T> f) { this.f = f; }
		public T this[int i] { get { return f(i); } }
	}

	public class Plot { public string Name; public object Brush; public float Width = 1; public PlotStyle PlotStyle; public NinjaTrader.Gui.DashStyleHelper DashStyleHelper; public Plot() { } }

	public abstract class NinjaScriptBase
	{
		// ---- lifecycle -------------------------------------------------------------------------
		public State State { get; internal set; }
		public string Name { get; set; }
		public string Description { get; set; }
		public Calculate Calculate { get; set; }
		public bool IsOverlay { get; set; }
		public bool DisplayInDataBox { get; set; }
		public bool DrawOnPricePanel { get; set; }
		public bool DrawHorizontalGridLines { get; set; }
		public bool DrawVerticalGridLines { get; set; }
		public bool PaintPriceMarkers { get; set; }
		public bool IsSuspendedWhileInactive { get; set; }
		public bool IsAutoScale { get; set; }
		public bool ShowTransparentPlotsInDataBox { get; set; }
		public bool BarsRequiredToPlotSet { get; set; }
		public int BarsRequiredToPlot { get; set; }
		public ScaleJustification ScaleJustification { get; set; }
		public MaximumBarsLookBack MaximumBarsLookBack { get; set; }
		public bool IsVisible { get; set; }
		public dynamic ChartControl { get; set; }
		public dynamic ChartPanel { get; set; }
		public dynamic ChartBars { get; set; }
		public dynamic RenderTarget { get; set; }

		protected virtual void OnStateChange() { }
		protected virtual void OnBarUpdate() { }
		protected virtual void OnMarketData(MarketDataEventArgs e) { }
		protected virtual void OnMarketDepth(MarketDepthEventArgs e) { }
		public virtual void OnRenderTargetChanged() { }
		protected virtual void OnRender(NinjaTrader.Gui.Chart.ChartControl chartControl, NinjaTrader.Gui.Chart.ChartScale chartScale) { }
		public virtual string DisplayName { get { return Name; } }

		// ---- bars context ----------------------------------------------------------------------
		public List<Bars> BarsList = new List<Bars>();
		public Bars[] BarsArray { get { return BarsList.ToArray(); } }
		public Bars Bars { get { return BarsList.Count > BarsInProgress ? BarsList[BarsInProgress] : null; } }
		public int BarsInProgress { get; internal set; }
		public int[] CurrentBars = new int[] { -1 };
		public int CurrentBar { get { return CurrentBars[BarsInProgress]; } }
		public bool IsFirstTickOfBar { get; internal set; }
		public BarsPeriod BarsPeriod { get { return Bars != null ? Bars.BarsPeriod : new BarsPeriod(); } }
		public BarsPeriod[] BarsPeriods { get { var a = new BarsPeriod[BarsList.Count]; for (int i = 0; i < a.Length; i++) a[i] = BarsList[i].BarsPeriod; return a; } }
		public Instrument Instrument { get { return BarsList.Count > 0 ? BarsList[0].Instrument : null; } }
		public Instrument[] Instruments { get { var a = new Instrument[BarsList.Count]; for (int i = 0; i < a.Length; i++) a[i] = BarsList[i].Instrument; return a; } }
		public double TickSize { get { return Instrument != null ? Instrument.MasterInstrument.TickSize : 0.25; } }
		public TradingHours TradingHours { get { return Bars != null ? Bars.TradingHours : TradingHours.CmeUsIndexEth; } }

		public PriceSeries<double> Open, High, Low, Close, Typical, Median, Weighted, Input;
		public PriceSeries<double> Volume;
		public PriceSeries<DateTime> Time;
		public SeriesArray<PriceSeries<double>> Opens, Highs, Lows, Closes, Volumes;
		public SeriesArray<PriceSeries<DateTime>> Times;
		public List<Series<double>> ValuesList = new List<Series<double>>();
		public Series<double>[] Values { get { return ValuesList.ToArray(); } }
		public List<Plot> PlotsList = new List<Plot>();
		public Plot[] Plots { get { return PlotsList.ToArray(); } }

		internal readonly List<KeyValuePair<object, int>> AllSeries = new List<KeyValuePair<object, int>>();
		internal void RegisterSeries(object s, int idx) { AllSeries.Add(new KeyValuePair<object, int>(s, idx)); }

		// data series requested in State.Configure; the harness resolves them
		public readonly List<Tuple<string, BarsPeriodType, int>> RequestedSeries = new List<Tuple<string, BarsPeriodType, int>>();

		protected NinjaScriptBase()
		{
			Calculate = Calculate.OnBarClose;
			Func<Bars, int, double> o = (b, i) => b.O[i], h = (b, i) => b.H[i], l = (b, i) => b.L[i], c = (b, i) => b.C[i];
			Open = new PriceSeries<double>(this, -1, o); High = new PriceSeries<double>(this, -1, h);
			Low = new PriceSeries<double>(this, -1, l); Close = new PriceSeries<double>(this, -1, c);
			Input = Close;
			Typical = new PriceSeries<double>(this, -1, (b, i) => (b.H[i] + b.L[i] + b.C[i]) / 3.0);
			Median = new PriceSeries<double>(this, -1, (b, i) => (b.H[i] + b.L[i]) / 2.0);
			Weighted = new PriceSeries<double>(this, -1, (b, i) => (b.H[i] + b.L[i] + 2 * b.C[i]) / 4.0);
			Volume = new PriceSeries<double>(this, -1, (b, i) => (double)b.V[i]);
			Time = new PriceSeries<DateTime>(this, -1, (b, i) => b.T[i]);
			Opens = new SeriesArray<PriceSeries<double>>(k => new PriceSeries<double>(this, k, o));
			Highs = new SeriesArray<PriceSeries<double>>(k => new PriceSeries<double>(this, k, h));
			Lows = new SeriesArray<PriceSeries<double>>(k => new PriceSeries<double>(this, k, l));
			Closes = new SeriesArray<PriceSeries<double>>(k => new PriceSeries<double>(this, k, c));
			Volumes = new SeriesArray<PriceSeries<double>>(k => new PriceSeries<double>(this, k, (b, i) => (double)b.V[i]));
			Times = new SeriesArray<PriceSeries<DateTime>>(k => new PriceSeries<DateTime>(this, k, (b, i) => b.T[i]));
		}

		protected void AddDataSeries(string instrumentName, BarsPeriodType type, int value) { RequestedSeries.Add(Tuple.Create(instrumentName, type, value)); }
		protected void AddDataSeries(BarsPeriodType type, int value) { RequestedSeries.Add(Tuple.Create((string)null, type, value)); }
		protected void AddPlot(object brush, string name) { PlotsList.Add(new Plot { Name = name, Brush = brush }); ValuesList.Add(new Series<double>(this)); }
		protected void AddPlot(object stroke, PlotStyle style, string name) { PlotsList.Add(new Plot { Name = name, Brush = stroke, PlotStyle = style }); ValuesList.Add(new Series<double>(this)); }
		protected void AddDataSeries(string instrumentName, BarsPeriod period, int barsToLoad, string tradingHoursName, bool? isResetOnNewTradingDay) { RequestedSeries.Add(Tuple.Create(instrumentName, period.BarsPeriodType, period.Value)); }
		protected void AddVolumetric(string instrumentName, BarsPeriodType type, int value, NinjaTrader.NinjaScript.BarsTypes.VolumetricDeltaType dt, int ticksPerLevel) { RequestedSeries.Add(Tuple.Create(instrumentName, BarsPeriodType.Volumetric, value)); }
		public int Count { get { return Bars != null ? Bars.Count : 0; } }
		public double CurrentBidH = 0, CurrentAskH = 0;
		public double GetCurrentBid() { return CurrentBidH; }
		public double GetCurrentAsk() { return CurrentAskH; }
		public double GetCurrentBid(int idx) { return CurrentBidH; }
		public double GetCurrentAsk(int idx) { return CurrentAskH; }
		protected void ClearOutputWindow() { }
		public void Print(object o) { if (Harness.HarnessOut.PrintEnabled) Console.WriteLine("[" + Name + "] " + o); }
		public void Log(string msg, LogLevel level) { if (Harness.HarnessOut.PrintEnabled) Console.WriteLine("[LOG " + level + "] " + msg); }
		protected void ForceRefresh() { }
		protected void RemoveDrawObject(string tag) { }
		protected void RemoveDrawObjects() { }
		public object DrawObjects { get { return new List<object>(); } }
		protected double RoundToTickSize(double p) { return Instrument.MasterInstrument.RoundToTickSize(p); }

		// ---- harness entry points --------------------------------------------------------------
		public void H_SetState(State s) { State = s; OnStateChange(); }
		public void H_SetCursor(int barsIdx, int curBar, bool firstTick) { BarsInProgress = barsIdx; CurrentBars[barsIdx] = curBar; IsFirstTickOfBar = firstTick; }
		public void H_BarUpdate() { OnBarUpdate(); }
		public void H_MarketData(int barsIdx, MarketDataEventArgs e) { int keep = BarsInProgress; BarsInProgress = barsIdx; OnMarketData(e); BarsInProgress = keep; }
		public void H_MarketDepth(MarketDepthEventArgs e) { OnMarketDepth(e); }
		public void H_AttachBars(List<Bars> bars) { BarsList = bars; CurrentBars = new int[bars.Count]; for (int i = 0; i < CurrentBars.Length; i++) CurrentBars[i] = -1; }
	}

	public abstract class IndicatorBase : NinjaScriptBase { }
}

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase { }
}
namespace NinjaTrader.Gui.NinjaScript
{
	public abstract class IndicatorRenderBase : NinjaTrader.NinjaScript.IndicatorBase { }
	public abstract class StrategyRenderBase : NinjaTrader.NinjaScript.StrategyBase { }
}
namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : NinjaTrader.NinjaScript.NinjaScriptBase { }
}
