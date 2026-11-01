// Managed-order Strategy stand-in. Orders are simulated on the tick stream the harness feeds:
//   market entry/exit: fills on the NEXT trade tick at the ask (buy) / bid (sell)
//   stop loss (stop market): triggers when a trade prints at or through the stop; fills at the worse of stop and that trade, plus Slippage ticks
//   profit target (limit): fills when a trade prints 1 tick through the target (a touch is not a fill), at the target
// This ledger is the strategy's own view; the Python fill model (design v3.4) re-simulates fills independently.
using System;
using System.Collections.Generic;
using NinjaTrader.Cbi;
using NinjaTrader.Data;

namespace NinjaTrader.Cbi
{
	public enum Provider { Simulator, Playback, Rithmic, Tradovate, Cqg, Unknown }
	public class Trade { public Execution Entry; public Execution Exit; public int Quantity; }
	public class TradeCollection : List<Trade> { public int TradesCount { get { return Count; } } }
	public class SystemPerformanceInfo { public TradeCollection AllTrades = new TradeCollection(); }
}
namespace NinjaTrader.Cbi
{
	public partial class AccountEx { }
}

namespace NinjaTrader.NinjaScript
{
	public enum TimeInForce { Day, Gtc }

	public abstract class StrategyBase : NinjaScriptBase
	{
		public EntryHandling EntryHandling { get; set; }
		public int EntriesPerDirection { get; set; }
		public bool IsExitOnSessionCloseStrategy { get; set; }
		public int ExitOnSessionCloseSeconds { get; set; }
		public StartBehavior StartBehavior { get; set; }
		public StopTargetHandling StopTargetHandling { get; set; }
		public RealtimeErrorHandling RealtimeErrorHandling { get; set; }
		public int Slippage { get; set; }
		public int BarsRequiredToTrade { get; set; }
		public bool TraceOrders { get; set; }
		public bool IsInstantiatedOnEachOptimizationIteration { get; set; }
		public bool IsFillLimitOnTouch { get; set; }
		public OrderFillResolution OrderFillResolution { get; set; }
		public TimeInForce TimeInForce { get; set; }
		public int DefaultQuantity { get; set; }
		public bool IsUnmanaged { get; set; }
		public Account Account = new Account();
		public Position Position = new Position();
		public SystemPerformanceInfo SystemPerformance = new SystemPerformanceInfo();

		protected virtual void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity, int filled, double averageFillPrice,
			OrderState orderState, DateTime time, ErrorCode error, string comment) { }
		protected virtual void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time) { }
		protected virtual void OnPositionUpdate(Position position, double averagePrice, int quantity, MarketPosition marketPosition) { }

		// ---- managed order state ----------------------------------------------------------------
		class Pending { public Order Order; public bool IsEntry; public int Dir; }
		readonly List<Pending> marketQueue = new List<Pending>();
		readonly Dictionary<string, double> stopBySignal = new Dictionary<string, double>(), targetBySignal = new Dictionary<string, double>();
		Order stopOrder, targetOrder;
		string openSignal = "";
		Execution openEntry;
		public readonly List<string> OrderLog = new List<string>();

		protected void SetStopLoss(string fromEntrySignal, CalculationMode mode, double value, bool isSimulatedStop) { stopBySignal[fromEntrySignal] = value; }
		protected void SetProfitTarget(string fromEntrySignal, CalculationMode mode, double value) { targetBySignal[fromEntrySignal] = value; }
		protected Order EnterLong(int qty, string signal) { return Submit(OrderAction.Buy, qty, signal, true, 1); }
		protected Order EnterShort(int qty, string signal) { return Submit(OrderAction.SellShort, qty, signal, true, -1); }
		protected Order EnterLong(string signal) { return EnterLong(1, signal); }
		protected Order EnterShort(string signal) { return EnterShort(1, signal); }
		protected Order ExitLong(string signal, string fromEntry) { return Position.MarketPosition == MarketPosition.Long ? Submit(OrderAction.Sell, Position.Quantity, signal, false, -1) : null; }
		protected Order ExitShort(string signal, string fromEntry) { return Position.MarketPosition == MarketPosition.Short ? Submit(OrderAction.BuyToCover, Position.Quantity, signal, false, 1) : null; }
		protected Order ExitLong() { return ExitLong("Sell", ""); }
		protected Order ExitShort() { return ExitShort("Buy to cover", ""); }

		Order Submit(OrderAction action, int qty, string name, bool isEntry, int dir)
		{
			if (isEntry && Position.MarketPosition != MarketPosition.Flat) return null;   // EntriesPerDirection 1 / one position
			var o = new Order { Name = name, OrderAction = action, OrderType = OrderType.Market, Quantity = qty, OrderState = OrderState.Working, Time = Harness.HarnessClock.Now };
			marketQueue.Add(new Pending { Order = o, IsEntry = isEntry, Dir = dir });
			OnOrderUpdate(o, 0, 0, qty, 0, 0, OrderState.Submitted, o.Time, ErrorCode.NoError, "");
			OnOrderUpdate(o, 0, 0, qty, 0, 0, OrderState.Working, o.Time, ErrorCode.NoError, "");
			return o;
		}

		/// <summary>Called by the harness for every trade tick BEFORE OnMarketData / OnBarUpdate of that tick.</summary>
		public void H_ProcessOrders(double last, double bid, double ask, DateTime time)
		{
			double tick = TickSize;
			// protective orders first (they were working before this tick)
			if (Position.MarketPosition != MarketPosition.Flat)
			{
				int d = Position.MarketPosition == MarketPosition.Long ? 1 : -1;
				bool stopHit = stopOrder != null && (d > 0 ? last <= stopOrder.StopPrice : last >= stopOrder.StopPrice);
				bool tgtHit = targetOrder != null && (d > 0 ? last >= targetOrder.LimitPrice + tick : last <= targetOrder.LimitPrice - tick);
				if (stopHit)
				{
					double px = d > 0 ? Math.Min(stopOrder.StopPrice, last) - Slippage * tick : Math.Max(stopOrder.StopPrice, last) + Slippage * tick;
					CloseOut(stopOrder, px, time, targetOrder);
				}
				else if (tgtHit) CloseOut(targetOrder, targetOrder.LimitPrice, time, stopOrder);
			}
			if (marketQueue.Count == 0) return;
			var q = new List<Pending>(marketQueue); marketQueue.Clear();
			foreach (var p in q)
			{
				double px = p.Dir > 0 ? (ask > 0 ? ask : last) : (bid > 0 ? bid : last);
				if (p.IsEntry)
				{
					if (Position.MarketPosition != MarketPosition.Flat) { Cancel(p.Order, time); continue; }
					Fill(p.Order, px, time);
					Position.MarketPosition = p.Dir > 0 ? MarketPosition.Long : MarketPosition.Short;
					Position.Quantity = p.Order.Quantity; Position.AveragePrice = px; Position.Instrument = Instrument;
					openSignal = p.Order.Name;
					openEntry = new Execution { Order = p.Order, Price = px, Quantity = p.Order.Quantity, Time = time, MarketPosition = Position.MarketPosition };
					OnExecutionUpdate(openEntry, openEntry.ExecutionId, px, p.Order.Quantity, Position.MarketPosition, p.Order.OrderId, time);
					OnPositionUpdate(Position, px, Position.Quantity, Position.MarketPosition);
					double sp, tp;
					if (stopBySignal.TryGetValue(openSignal, out sp))
						stopOrder = new Order { Name = "Stop loss", FromEntrySignal = openSignal, OrderType = OrderType.StopMarket, StopPrice = sp, Quantity = Position.Quantity,
							OrderAction = p.Dir > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderState = OrderState.Accepted, Time = time };
					if (targetBySignal.TryGetValue(openSignal, out tp))
						targetOrder = new Order { Name = "Profit target", FromEntrySignal = openSignal, OrderType = OrderType.Limit, LimitPrice = tp, Quantity = Position.Quantity,
							OrderAction = p.Dir > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderState = OrderState.Accepted, Time = time };
					if (stopOrder != null) OnOrderUpdate(stopOrder, 0, stopOrder.StopPrice, stopOrder.Quantity, 0, 0, OrderState.Accepted, time, ErrorCode.NoError, "");
					if (targetOrder != null) OnOrderUpdate(targetOrder, targetOrder.LimitPrice, 0, targetOrder.Quantity, 0, 0, OrderState.Accepted, time, ErrorCode.NoError, "");
				}
				else if (Position.MarketPosition != MarketPosition.Flat) CloseOut(p.Order, px, time, null, true);
				else Cancel(p.Order, time);
			}
		}

		void Fill(Order o, double px, DateTime t)
		{
			o.Filled = o.Quantity; o.AverageFillPrice = px; o.OrderState = OrderState.Filled; o.Time = t;
			OnOrderUpdate(o, o.LimitPrice, o.StopPrice, o.Quantity, o.Filled, px, OrderState.Filled, t, ErrorCode.NoError, "");
			OrderLog.Add(t.ToString("yyyy-MM-dd HH:mm:ss.fff") + "," + o.Name + "," + o.OrderAction + "," + o.Quantity + "," + px.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture));
		}
		void Cancel(Order o, DateTime t)
		{
			if (o == null) return;
			o.OrderState = OrderState.Cancelled;
			OnOrderUpdate(o, o.LimitPrice, o.StopPrice, o.Quantity, o.Filled, 0, OrderState.Cancelled, t, ErrorCode.NoError, "");
		}
		void CloseOut(Order exitOrder, double px, DateTime t, Order other, bool cancelBoth = false)
		{
			Fill(exitOrder, px, t);
			var ex = new Execution { Order = exitOrder, Price = px, Quantity = Position.Quantity, Time = t, MarketPosition = MarketPosition.Flat };
			OnExecutionUpdate(ex, ex.ExecutionId, px, Position.Quantity, MarketPosition.Flat, exitOrder.OrderId, t);
			SystemPerformance.AllTrades.Add(new Trade { Entry = openEntry, Exit = ex, Quantity = Position.Quantity });
			Order s = stopOrder, g = targetOrder; stopOrder = null; targetOrder = null;
			if (s != null && s != exitOrder) Cancel(s, t);
			if (g != null && g != exitOrder) Cancel(g, t);
			Position.MarketPosition = MarketPosition.Flat; Position.Quantity = 0;
			OnPositionUpdate(Position, px, 0, MarketPosition.Flat);
			Position.AveragePrice = 0;
			openSignal = ""; openEntry = null;
		}
		/// <summary>NT "exit on session close": flatten at the session end.</summary>
		public void H_SessionClose(double bid, double ask, DateTime t)
		{
			if (Position.MarketPosition == MarketPosition.Flat) return;
			var o = new Order { Name = "Exit on session close", OrderAction = Position.MarketPosition == MarketPosition.Long ? OrderAction.Sell : OrderAction.BuyToCover, Quantity = Position.Quantity, OrderType = OrderType.Market };
			CloseOut(o, Position.MarketPosition == MarketPosition.Long ? bid : ask, t, null);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase { }
}
