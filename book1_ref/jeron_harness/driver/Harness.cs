// JeronHarness driver v0.1 (Oct 25 2026): runs the REAL JeronOrderFlowStrategy (S1.4) on a tick tape, the way
// NinjaTrader 8 runs it on a 1-minute chart with Tick Replay:
//   - every tick: managed orders working from earlier ticks are filled first, then OnMarketData(Last, with bid/ask)
//     while the bar the tick belongs to is not yet open (so BarIndexForTime returns CurrentBar+1 for a new bar),
//     then the bar advances (first tick of a bar) and OnBarUpdate runs (Calculate.OnEachTick).
//   - 1-minute bars stamped at their END time; a tick exactly on hh:mm:00.000 opens the bar ending hh:mm+1 (as NT does).
//   - session = CME US Index ETH (17:00-16:00 CT); exit on session close 30 s before 16:00.
// Tape formats:
//   NT export Last file:  yyyyMMdd HHmmss fffffff;price;bid;ask;volume   (UTC)
//   JeronTapeExporter:    csv / csv.gz with header (time_local,price,bid,ask,volume ...)  [local = Central]
// Usage: mono JeronHarness.exe <tape> <planFolder> <outFolder> [Prop=Value ...]
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Strategies;

namespace NinjaTrader.Harness
{
	public struct Tick { public DateTime T; public double P, Bid, Ask; public long V; public char Aggr; }

	public static class TapeReader
	{
		static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
		public static IEnumerable<Tick> Read(string path, TimeZoneInfo central)
		{
			Stream s = File.OpenRead(path);
			if (path.EndsWith(".gz", StringComparison.OrdinalIgnoreCase)) s = new GZipStream(s, CompressionMode.Decompress);
			using (var r = new StreamReader(s))
			{
				string line; int[] col = null; bool ntExport = false; bool first = true;
				while ((line = r.ReadLine()) != null)
				{
					if (line.Length == 0) continue;
					if (first)
					{
						first = false;
						if (line.Length > 16 && char.IsDigit(line[0]) && line[8] == ' ' && line.IndexOf(';') > 0) ntExport = true;
						else
						{
							var h = line.Split(',');
							col = new int[6];
							col[0] = Find(h, "time_local", "TimeLocal", "time", "Time", "ct");
							col[1] = Find(h, "price", "Price", "last", "Last");
							col[2] = Find(h, "bid", "Bid");
							col[3] = Find(h, "ask", "Ask");
							col[4] = Find(h, "volume", "Volume", "size", "Size");
							col[5] = Find(h, "aggressor", "side");
							continue;
						}
					}
					Tick t;
					if (ntExport)
					{
						var p = line.Split(';');
						var utc = DateTime.ParseExact(p[0].Substring(0, 15), "yyyyMMdd HHmmss", Inv).AddTicks(long.Parse(p[0].Substring(16, 7), Inv));
						t.T = TimeZoneInfo.ConvertTimeFromUtc(DateTime.SpecifyKind(utc, DateTimeKind.Utc), central);
						t.P = double.Parse(p[1], Inv);
						t.Bid = p[2].Length > 0 ? double.Parse(p[2], Inv) : 0;
						t.Ask = p[3].Length > 0 ? double.Parse(p[3], Inv) : 0;
						t.V = long.Parse(p[4], Inv);
						t.Aggr = 'U';
					}
					else
					{
						var p = line.Split(',');
						t.T = DateTime.Parse(p[col[0]], Inv);
						t.P = double.Parse(p[col[1]], Inv);
						t.Bid = col[2] >= 0 && p[col[2]].Length > 0 ? double.Parse(p[col[2]], Inv) : 0;
						t.Ask = col[3] >= 0 && p[col[3]].Length > 0 ? double.Parse(p[col[3]], Inv) : 0;
						t.V = long.Parse(p[col[4]], Inv);
						t.Aggr = col[5] >= 0 && p[col[5]].Length > 0 ? p[col[5]][0] : 'U';
					}
					t.T = DateTime.SpecifyKind(t.T, DateTimeKind.Unspecified);
					yield return t;
				}
			}
		}
		static int Find(string[] h, params string[] names)
		{
			for (int i = 0; i < h.Length; i++) foreach (var n in names) if (string.Equals(h[i].Trim(), n, StringComparison.OrdinalIgnoreCase)) return i;
			return -1;
		}
	}

	public static class Program
	{
		static DateTime BarEnd(DateTime t)
		{
			// NinjaTrader puts a tick stamped exactly hh:mm:00.000 into the NEXT bar (checked on Oct 8: 09:34 and 11:44 closes)
			return new DateTime(t.Year, t.Month, t.Day, t.Hour, t.Minute, 0).AddMinutes(1);
		}

		static void SetProp(object o, string name, string val)
		{
			PropertyInfo p = o.GetType().GetProperty(name, BindingFlags.Public | BindingFlags.Instance);
			if (p == null) throw new ArgumentException("no property " + name);
			object v;
			Type ty = p.PropertyType;
			if (ty == typeof(string)) v = val;
			else if (ty.IsEnum) v = Enum.Parse(ty, val, true);
			else if (ty == typeof(bool)) v = bool.Parse(val);
			else v = Convert.ChangeType(val, ty, CultureInfo.InvariantCulture);
			p.SetValue(o, v, null);
		}

		static DateTime optFrom = DateTime.MinValue, optTo = DateTime.MaxValue;
		static string optInstrument = "NQ DEC26";
		static string optEsBars = null;
		static string optHtfBars = null;   // map: chart-instrument 1-minute bars csv for the HTF composite (same columns)   // map: ES 1-minute bars csv (time_end_local,open,high,low,close,volume[,release_local])

		/// <summary>Options before the positional arguments: --map, --from=yyyy-MM-dd HH:mm, --to=..., --instrument=NAME (local = Central).</summary>
		static List<string> ParseOptions(string[] args, out bool map)
		{
			map = false;
			var rest = new List<string>();
			foreach (var a in args)
			{
				if (a == "--map") map = true;
				else if (a.StartsWith("--from=")) optFrom = DateTime.Parse(a.Substring(7), CultureInfo.InvariantCulture);
				else if (a.StartsWith("--to=")) optTo = DateTime.Parse(a.Substring(5), CultureInfo.InvariantCulture);
				else if (a.StartsWith("--instrument=")) optInstrument = a.Substring(13);
				else if (a.StartsWith("--es=")) optEsBars = a.Substring(5);
				else if (a.StartsWith("--htf=")) optHtfBars = a.Substring(6);
				else rest.Add(a);
			}
			return rest;
		}

		static IEnumerable<Tick> Ticks(string tape)
		{
			foreach (var t in TapeReader.Read(tape, NinjaTrader.Core.Globals.Central))
			{
				if (t.T < optFrom) continue;
				if (t.T >= optTo) yield break;
				yield return t;
			}
		}

		public static int Main(string[] argv)
		{
			bool map;
			var args = ParseOptions(argv, out map).ToArray();
			if (map) return RunMap(args);
			if (args.Length < 3) { Console.Error.WriteLine("usage: JeronHarness.exe [--from=..] [--to=..] <tape> <planFolder> <outFolder> [Prop=Value ...]\n       JeronHarness.exe --map [--from=..] [--to=..] <tape> <outFolder> [Prop=Value ...]"); return 2; }
			string tape = args[0], planDir = args[1], outDir = args[2];
			Directory.CreateDirectory(outDir);
			NinjaTrader.Core.Globals.UserDataDir = Path.Combine(outDir, "userdata");

			var s = new JeronOrderFlowStrategy();
			s.H_SetState(State.SetDefaults);
			// harness folders and the things that need NinjaTrader itself
			s.LogFolder = outDir;
			s.PlanFolder = planDir;
			s.L2Folder = Path.Combine(outDir, "L2");
			s.CaptureL2 = false;
			s.RecordAllL2Updates = false;
			s.ShowStatusPanel = false;
			for (int i = 3; i < args.Length; i++)
			{
				int eq = args[i].IndexOf('=');
				SetProp(s, args[i].Substring(0, eq), args[i].Substring(eq + 1));
				Console.WriteLine("set " + args[i]);
			}
			s.H_SetState(State.Configure);

			// bar series: [0] = chart instrument 1 minute; extra requested series get empty bars (no ES ticks)
			var bars = new List<Bars>();
			var main = new Bars();
			main.Instrument.FullName = optInstrument;
			bars.Add(main);
			foreach (var rq in s.RequestedSeries)
			{
				var b = new Bars(); b.Instrument.FullName = rq.Item1 ?? optInstrument;
				if (b.Instrument.FullName.StartsWith("ES")) { b.Instrument.MasterInstrument.Name = "ES"; b.Instrument.MasterInstrument.PointValue = 50; }
				bars.Add(b);
				Console.WriteLine("series " + bars.Count + ": " + b.Instrument.FullName + " (no data in this tape)");
			}
			s.H_AttachBars(bars);
			s.H_SetState(State.DataLoaded);
			s.H_SetState(State.Historical);

			var th = main.TradingHours;
			long n = 0; DateTime lastSessEnd = DateTime.MinValue; bool closedThisSession = false;
			double lastBid = 0, lastAsk = 0;
			int exitSecs = s.ExitOnSessionCloseSeconds;
			// ES 1-minute bars for the strategy's ES series (OnEachTick: on the first tick of a new ES bar the strategy
			// reads [1] = the bar that just closed). Each closed bar is followed by a provisional bar that becomes the
			// next real bar when it is released, so [1] is always the latest closed ES bar.
			int esS = -1;
			for (int k = 1; k < bars.Count; k++) if (bars[k].Instrument.FullName.StartsWith("ES")) esS = k;
			BarFeed esFeed = optEsBars != null && esS > 0 ? BarFeed.Load(optEsBars, esS) : null;
			if (esFeed != null) Console.WriteLine("ES bars for the strategy: " + esFeed.Q.Count);
			Action<DateTime> flushEs = upTo =>
			{
				while (esFeed != null && esFeed.Next < esFeed.Q.Count)
				{
					var q = esFeed.Q[esFeed.Next];
					DateTime te = DateTime.Parse(q[0], CultureInfo.InvariantCulture);
					DateTime rel = q.Length >= 7 && q[6].Length > 0 ? DateTime.Parse(q[6], CultureInfo.InvariantCulture) : te;
					if (rel >= upTo) break;
					var eb = bars[esS];
					double o = double.Parse(q[1], CultureInfo.InvariantCulture), h = double.Parse(q[2], CultureInfo.InvariantCulture),
						l = double.Parse(q[3], CultureInfo.InvariantCulture), c = double.Parse(q[4], CultureInfo.InvariantCulture);
					long v = (long)double.Parse(q[5], CultureInfo.InvariantCulture);
					if (eb.Count > 0) { int j = eb.Count - 1; eb.T[j] = te; eb.O[j] = o; eb.H[j] = h; eb.L[j] = l; eb.C[j] = c; eb.V[j] = v; }   // the provisional bar becomes this bar
					else { eb.T.Add(te); eb.O.Add(o); eb.H.Add(h); eb.L.Add(l); eb.C.Add(c); eb.V.Add(v); eb.FirstOfSession.Add(false); }
					eb.T.Add(te.AddMinutes(1)); eb.O.Add(c); eb.H.Add(c); eb.L.Add(c); eb.C.Add(c); eb.V.Add(0); eb.FirstOfSession.Add(false);
					eb.CurrentIndex = eb.Count - 1;
					int keepBip = 0;
					s.H_SetCursor(esS, eb.Count - 1, true);
					s.H_BarUpdate();
					s.H_SetCursor(keepBip, Math.Max(0, main.Count - 1), false);
					esFeed.Next++;
				}
			};
			foreach (var t in Ticks(tape))
			{
				HarnessClock.Now = t.T;
				if (t.Bid > 0) lastBid = t.Bid; if (t.Ask > 0) lastAsk = t.Ask;
				s.CurrentBidH = lastBid; s.CurrentAskH = lastAsk;
				if (esFeed != null) flushEs(t.T);

				DateTime sessEnd = th.SessionEnd(t.T);
				if (sessEnd != lastSessEnd) { lastSessEnd = sessEnd; closedThisSession = false; }
				if (s.IsExitOnSessionCloseStrategy && !closedThisSession && t.T >= sessEnd.AddSeconds(-exitSecs))
				{
					s.H_SessionClose(lastBid, lastAsk, t.T);
					closedThisSession = true;
				}

				// 1. orders working from earlier ticks
				s.H_ProcessOrders(t.P, lastBid, lastAsk, t.T);

				// 2. OnMarketData before the bar for this tick exists
				DateTime be = BarEnd(t.T);
				int cur = main.Count - 1;
				bool newBar = cur < 0 || be > main.T[cur];
				s.H_SetCursor(0, cur, false);
				var e = new MarketDataEventArgs { MarketDataType = MarketDataType.Last, Price = t.P, Volume = t.V, Time = t.T, Bid = lastBid, Ask = lastAsk, Instrument = main.Instrument };
				if (cur >= 0) s.H_MarketData(0, e);

				// 3. advance / update the bar, then OnBarUpdate
				if (newBar)
				{
					bool firstOfSession = cur < 0 || th.TradingDay(main.T[cur].AddSeconds(-1)) != th.TradingDay(be.AddSeconds(-1));
					main.T.Add(be); main.O.Add(t.P); main.H.Add(t.P); main.L.Add(t.P); main.C.Add(t.P); main.V.Add(t.V);
					main.FirstOfSession.Add(firstOfSession);
					cur++;
				}
				else
				{
					if (t.P > main.H[cur]) main.H[cur] = t.P;
					if (t.P < main.L[cur]) main.L[cur] = t.P;
					main.C[cur] = t.P; main.V[cur] += t.V;
				}
				main.CurrentIndex = cur;
				s.H_SetCursor(0, cur, newBar);
				if (cur == 0) s.H_MarketData(0, e);   // the very first tick: the bar exists only now
				s.H_BarUpdate();
				n++;
				if (n % 200000 == 0) Console.WriteLine(t.T.ToString("yyyy-MM-dd HH:mm:ss") + "  ticks " + n.ToString("N0") + "  bars " + main.Count);
			}
			s.H_SetState(State.Terminated);
			File.WriteAllLines(Path.Combine(outDir, "harness_orders.csv"), s.OrderLog);
			Console.WriteLine("done: ticks " + n.ToString("N0") + ", bars " + main.Count + ", strategy trades " + s.SystemPerformance.AllTrades.Count);
			return 0;
		}

		/// <summary>JeronPreopenMap v2.3 as NinjaTrader runs it historically: [0] chart 1-minute bars (OnBarClose),
		/// [1] the 1-tick series it adds (every trade = one bar, OnBarUpdate per tick), further series it requests
		/// (Volumetric / ES / HTF minutes) are attached empty unless a bars file is given (not in this version).
		/// A 1-minute bar is closed (OnBarUpdate on [0]) before the first tick after its end time is processed.</summary>
		class BarFeed
		{
			public int Series; public List<string[]> Q = new List<string[]>(); public int Next;
			public static BarFeed Load(string path, int series)
			{
				var f = new BarFeed { Series = series };
				foreach (var line in File.ReadLines(path).Skip(1)) { var p = line.Split(','); if (p.Length >= 6) f.Q.Add(p); }
				return f;
			}
		}

		/// <summary>JeronPreopenMap v2.3 as NinjaTrader runs it historically:
		///  [0] chart 1-minute bars (OnBarClose) - closed before the first tick after their end time,
		///  the 1-tick series it adds (every trade = one bar),
		///  the 1-minute BidAsk Volumetric series (built here from the tape: ask volume = buy aggressor, bid = sell
		///      aggressor, U by the quote), closed together with [0],
		///  ES 1-minute bars (--es) and the chart instrument's HTF 1-minute bars (--htf), each fed when NT would close
		///      it: release_local (the series' next trade) when the file has it, else the bar's end time.</summary>
		static int RunMap(string[] args)
		{
			if (args.Length < 2) { Console.Error.WriteLine("usage: JeronHarness.exe --map [--from=..] [--to=..] [--es=bars.csv] [--htf=bars.csv] <tape> <outFolder> [Prop=Value ...]"); return 2; }
			string tape = args[0], outDir = args[1];
			Directory.CreateDirectory(outDir);
			NinjaTrader.Core.Globals.UserDataDir = Path.Combine(outDir, "userdata");
			var m = new NinjaTrader.NinjaScript.Indicators.JeronPreopenMap();
			m.H_SetState(State.SetDefaults);
			m.OutputFolder = outDir;
			m.ShowStatusPanel = false;
			for (int i = 2; i < args.Length; i++)
			{
				int eq = args[i].IndexOf('=');
				SetProp(m, args[i].Substring(0, eq), args[i].Substring(eq + 1));
				Console.WriteLine("set " + args[i]);
			}
			var bars = new List<Bars>();
			var main = new Bars(); main.Instrument.FullName = optInstrument; bars.Add(main);
			m.H_AttachBars(new List<Bars> { main });   // the instrument must be known in Configure
			m.H_SetState(State.Configure);
			int tickIdx = -1, volIdx = -1, esIdx = -1, htfIdx = -1;
			foreach (var rq in m.RequestedSeries)
			{
				var b = new Bars(); b.Instrument.FullName = rq.Item1 ?? optInstrument;
				b.BarsPeriod.BarsPeriodType = rq.Item2; b.BarsPeriod.Value = rq.Item3;
				bool es = b.Instrument.FullName.StartsWith("ES");
				if (es) { b.Instrument.MasterInstrument.Name = "ES"; b.Instrument.MasterInstrument.PointValue = 50; }
				bars.Add(b);
				int k = bars.Count - 1; string src = "empty";
				if (rq.Item2 == BarsPeriodType.Tick && tickIdx < 0) { tickIdx = k; src = "tape"; }
				else if (rq.Item2 == BarsPeriodType.Volumetric) { volIdx = k; b.BarsPeriod.BaseBarsPeriodType = BarsPeriodType.Minute; b.BarsSeries.BarsType = new NinjaTrader.NinjaScript.BarsTypes.VolumetricBarsType(); src = "tape (MBO aggressor)"; }
				else if (es && rq.Item2 == BarsPeriodType.Minute) { esIdx = k; src = optEsBars ?? "empty"; }
				else if (rq.Item2 == BarsPeriodType.Minute) { htfIdx = k; src = optHtfBars ?? "empty"; }
				Console.WriteLine("series " + k + ": " + b.Instrument.FullName + " " + rq.Item2 + " " + rq.Item3 + " <- " + src);
			}
			m.H_AttachBars(bars);
			m.H_SetState(State.DataLoaded);
			m.H_SetState(State.Historical);
			var th = main.TradingHours;
			var feeds = new List<BarFeed>();
			if (optHtfBars != null && htfIdx > 0) feeds.Add(BarFeed.Load(optHtfBars, htfIdx));
			if (optEsBars != null && esIdx > 0) feeds.Add(BarFeed.Load(optEsBars, esIdx));
			foreach (var f in feeds) Console.WriteLine("bars for series " + f.Series + ": " + f.Q.Count);
			Action<DateTime> flush = upTo =>
			{
				// all feeds in time order (ties: lower series index first)
				while (true)
				{
					BarFeed best = null; DateTime bestRel = DateTime.MaxValue, bestEnd = DateTime.MaxValue;
					foreach (var f in feeds)
					{
						if (f.Next >= f.Q.Count) continue;
						var p = f.Q[f.Next];
						DateTime te = DateTime.Parse(p[0], CultureInfo.InvariantCulture);
						DateTime rel = p.Length >= 7 && p[6].Length > 0 ? DateTime.Parse(p[6], CultureInfo.InvariantCulture) : te;
						if (rel < bestRel) { best = f; bestRel = rel; bestEnd = te; }
					}
					if (best == null || bestRel >= upTo) break;
					var q = best.Q[best.Next];
					var eb = bars[best.Series];
					eb.T.Add(bestEnd); eb.O.Add(double.Parse(q[1], CultureInfo.InvariantCulture)); eb.H.Add(double.Parse(q[2], CultureInfo.InvariantCulture));
					eb.L.Add(double.Parse(q[3], CultureInfo.InvariantCulture)); eb.C.Add(double.Parse(q[4], CultureInfo.InvariantCulture)); eb.V.Add((long)double.Parse(q[5], CultureInfo.InvariantCulture));
					eb.FirstOfSession.Add(false);
					eb.CurrentIndex = eb.Count - 1;
					m.H_SetCursor(best.Series, eb.Count - 1, true);
					m.H_BarUpdate();
					best.Next++;
				}
			};
			// tick series keeps only the current trade (the map reads [0] only)
			var tb = bars[tickIdx];
			tb.T.Add(DateTime.MinValue); tb.O.Add(0); tb.H.Add(0); tb.L.Add(0); tb.C.Add(0); tb.V.Add(0); tb.FirstOfSession.Add(false);
			var vb = volIdx > 0 ? bars[volIdx] : null;
			var vt = vb != null ? (NinjaTrader.NinjaScript.BarsTypes.VolumetricBarsType)vb.BarsSeries.BarsType : null;
			NinjaTrader.NinjaScript.BarsTypes.VolumetricData vcur = null;
			double lastBid = 0, lastAsk = 0;
			long n = 0;
			foreach (var t in Ticks(tape))
			{
				HarnessClock.Now = t.T;
				if (t.Bid > 0) lastBid = t.Bid; if (t.Ask > 0) lastAsk = t.Ask;
				if (feeds.Count > 0) flush(t.T);   // bars NT has closed before this tick (same time stamp: the tick series goes first)
				DateTime be = BarEnd(t.T);
				int cur = main.Count - 1;
				if (cur < 0 || be > main.T[cur])
				{
					// close the previous 1-minute bar (OnBarClose): primary first, then the Volumetric series
					if (cur >= 0)
					{
						main.CurrentIndex = cur; m.H_SetCursor(0, cur, false); m.H_BarUpdate();
						if (vb != null) { vb.CurrentIndex = vb.Count - 1; m.H_SetCursor(volIdx, vb.Count - 1, false); m.H_BarUpdate(); }
					}
					bool firstOfSession = cur < 0 || th.TradingDay(main.T[cur].AddSeconds(-1)) != th.TradingDay(be.AddSeconds(-1));
					main.T.Add(be); main.O.Add(t.P); main.H.Add(t.P); main.L.Add(t.P); main.C.Add(t.P); main.V.Add(t.V); main.FirstOfSession.Add(firstOfSession);
					if (vb != null)
					{
						vb.T.Add(be); vb.O.Add(t.P); vb.H.Add(t.P); vb.L.Add(t.P); vb.C.Add(t.P); vb.V.Add(0); vb.FirstOfSession.Add(firstOfSession);
						vcur = new NinjaTrader.NinjaScript.BarsTypes.VolumetricData(); vt.Volumes.Add(vcur);
					}
				}
				else
				{
					if (t.P > main.H[cur]) main.H[cur] = t.P;
					if (t.P < main.L[cur]) main.L[cur] = t.P;
					main.C[cur] = t.P; main.V[cur] += t.V;
					if (vb != null) { int vi = vb.Count - 1; if (t.P > vb.H[vi]) vb.H[vi] = t.P; if (t.P < vb.L[vi]) vb.L[vi] = t.P; vb.C[vi] = t.P; }
				}
				if (vb != null)
				{
					bool buy = t.Aggr == 'B' || (t.Aggr != 'S' && lastAsk > 0 && t.P >= lastAsk);
					bool sell = t.Aggr == 'S' || (t.Aggr != 'B' && lastBid > 0 && t.P <= lastBid);
					if (buy || sell) vcur.Add(t.P, t.V, buy);
					vb.V[vb.Count - 1] += t.V;
				}
				// the tick bar (only the current trade is kept)
				tb.T[0] = t.T; tb.O[0] = t.P; tb.H[0] = t.P; tb.L[0] = t.P; tb.C[0] = t.P; tb.V[0] = t.V;
				tb.CurrentIndex = 0;
				m.H_SetCursor(tickIdx, 0, true);
				m.H_BarUpdate();
				n++;
				if (n % 2000000 == 0) Console.WriteLine(t.T.ToString("yyyy-MM-dd HH:mm:ss") + "  ticks " + n.ToString("N0"));
			}
			m.H_SetState(State.Terminated);
			Console.WriteLine("done: ticks " + n.ToString("N0") + ", minute bars " + main.Count);
			return 0;
		}
	}
}
