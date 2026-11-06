// =====================================================================================
//  JeronFlowShared.cs  —  shared engine for the Jeron NinjaTrader 8 indicators
//  Used by: JeronAdaptiveTradeDetector (Indicator 1) and JeronOrderFlowEventTracker (Indicator 2)
//
//  Place in: Documents\NinjaTrader 8\bin\Custom\Indicators\
//
//  What lives here
//   - JeronSessionClock   : deterministic Central Time session classification (DST-aware)
//   - JeronFlowEngine     : aggressor classification + three separately identified
//                           aggregation methods (A Individual Block, B Consistent Bid/Ask,
//                           C Short-Duration Aggressor Cluster), tier crossings, and the
//                           optional relative-activity (adaptive) regime layer
//   - JeronCsvLogger      : append-only CSV event log
//
//  Provenance of numbers
//   - 60 / 100 Deep Trade tiers, 300/400/500 NY and 150/200 Asia/London Power Trade tiers
//     are Jeron's documented settings (transcripts, Part 1).
//   - Everything else (time-cluster gap, price tolerance, adaptive percentile and cutoffs,
//     session boundaries other than the 8:30 CT NY open) is OUR research parameter,
//     not a Jeron rule. Defaults are placeholders to be calibrated from the logs.
//
//  Coding rules followed for NT8: C# 5 syntax only (no ?. , no $"", no expression-bodied
//  members), no C# contextual keywords used as identifiers.
// =====================================================================================
#region Using declarations
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
#endregion

namespace NinjaTrader.NinjaScript.Indicators.JeronShared
{
	public enum JeronAggSide { Unknown = 0, Buy = 1, Sell = -1 }

	public enum JeronMethod { IndividualBlock = 0, ConsistentBidAsk = 1, TimeCluster = 2 }

	public enum JeronSession { Asia, London, NewYork, PostNY }

	public enum JeronRegime { Research, Warmup, Quiet, Normal, Active }

	public enum JeronFootprintSource { Auto, Volumetric, InternalTicks }

	public enum JeronStopAnchorMode { ZoneOppositeBoundary, TriggerBarExtreme }

	// ---------------------------------------------------------------------------------
	//  Formatting helpers (invariant culture so CSVs are identical on every PC)
	// ---------------------------------------------------------------------------------
	public static class JeronFmt
	{
		public static string P(double price)
		{
			if (double.IsNaN(price) || double.IsInfinity(price)) return "";
			return price.ToString("0.00", CultureInfo.InvariantCulture);
		}

		public static string N(double num, int decimals)
		{
			if (double.IsNaN(num)) return "";
			if (double.IsPositiveInfinity(num)) return "INF";
			if (double.IsNegativeInfinity(num)) return "-INF";
			return Math.Round(num, decimals).ToString(CultureInfo.InvariantCulture);
		}

		public static string I(long num)
		{
			return num.ToString(CultureInfo.InvariantCulture);
		}

		public static string T(DateTime t)
		{
			if (t == DateTime.MinValue) return "";
			return t.ToString("yyyy-MM-dd HH:mm:ss.fff", CultureInfo.InvariantCulture);
		}

		public static string Hms(DateTime t)
		{
			return t.ToString("HH:mm:ss.fff", CultureInfo.InvariantCulture);
		}

		public static string SideText(JeronAggSide side)
		{
			if (side == JeronAggSide.Buy) return "Buy";
			if (side == JeronAggSide.Sell) return "Sell";
			return "Unknown";
		}

		public static string DirText(int dir)
		{
			if (dir > 0) return "Long";
			if (dir < 0) return "Short";
			return "Undetermined";
		}

		/// <summary>Parses "300,400,500" into a sorted list of positive sizes.</summary>
		public static List<long> ParseTiers(string text, long[] fallback)
		{
			List<long> result = new List<long>();
			if (!string.IsNullOrWhiteSpace(text))
			{
				string[] parts = text.Split(new char[] { ',', ';', '/', ' ' }, StringSplitOptions.RemoveEmptyEntries);
				foreach (string part in parts)
				{
					long parsed;
					if (long.TryParse(part.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out parsed) && parsed > 0 && !result.Contains(parsed))
						result.Add(parsed);
				}
			}
			if (result.Count == 0 && fallback != null)
				result.AddRange(fallback);
			result.Sort();
			return result;
		}

		public static List<int> ParseInts(string text, int[] fallback)
		{
			List<int> result = new List<int>();
			if (!string.IsNullOrWhiteSpace(text))
			{
				foreach (string part in text.Split(new char[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries))
				{
					int parsed;
					if (int.TryParse(part.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out parsed) && parsed > 0 && !result.Contains(parsed))
						result.Add(parsed);
				}
			}
			if (result.Count == 0 && fallback != null)
				result.AddRange(fallback);
			result.Sort();
			return result;
		}

		public static string SafeFileToken(string text)
		{
			if (string.IsNullOrEmpty(text)) return "NA";
			StringBuilder sb = new StringBuilder();
			foreach (char ch in text)
				sb.Append(char.IsLetterOrDigit(ch) ? ch : '_');
			return sb.ToString();
		}
	}

	// ---------------------------------------------------------------------------------
	//  Session clock — everything classified in Central Time, DST handled by Windows TZ
	// ---------------------------------------------------------------------------------
	public class JeronSessionClock
	{
		private static TimeZoneInfo centralZone;

		public int AsiaStartMin   = 17 * 60;       // 17:00 CT (Globex reopen)  — research boundary
		public int LondonStartMin = 1 * 60;        // 01:00 CT                  — research boundary
		public int NyStartMin     = 8 * 60 + 30;   // 08:30 CT (cash open)      — from the plan
		public int NyEndMin       = 15 * 60;       // 15:00 CT                  — research boundary

		public static TimeZoneInfo CentralZone
		{
			get
			{
				if (centralZone == null)
				{
					try { centralZone = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time"); }
					catch { centralZone = TimeZoneInfo.Local; }
				}
				return centralZone;
			}
		}

		/// <summary>Converts a timestamp expressed in the NinjaTrader display time zone to Central Time.</summary>
		public static DateTime ToCentral(DateTime timeInSourceZone, TimeZoneInfo sourceZone)
		{
			try
			{
				if (sourceZone == null) return timeInSourceZone;
				if (sourceZone.Id == CentralZone.Id) return timeInSourceZone;
				return TimeZoneInfo.ConvertTime(DateTime.SpecifyKind(timeInSourceZone, DateTimeKind.Unspecified), sourceZone, CentralZone);
			}
			catch
			{
				return timeInSourceZone;
			}
		}

		public static int ParseHhmm(string text, int fallbackMinutes)
		{
			if (string.IsNullOrWhiteSpace(text)) return fallbackMinutes;
			string[] parts = text.Trim().Split(':');
			int hh, mm = 0;
			if (parts.Length >= 1 && int.TryParse(parts[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out hh))
			{
				if (parts.Length >= 2) int.TryParse(parts[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out mm);
				if (hh >= 0 && hh < 24 && mm >= 0 && mm < 60) return hh * 60 + mm;
			}
			return fallbackMinutes;
		}

		private static bool InWindow(int minute, int startMin, int endMin)
		{
			if (startMin == endMin) return false;
			if (startMin < endMin) return minute >= startMin && minute < endMin;
			return minute >= startMin || minute < endMin;   // wraps midnight
		}

		public JeronSession Classify(DateTime ct)
		{
			int m = ct.Hour * 60 + ct.Minute;
			if (InWindow(m, NyStartMin, NyEndMin))       return JeronSession.NewYork;
			if (InWindow(m, LondonStartMin, NyStartMin)) return JeronSession.London;
			if (InWindow(m, AsiaStartMin, LondonStartMin)) return JeronSession.Asia;
			return JeronSession.PostNY;
		}

		/// <summary>CME-style trading date: activity from the Asia start (17:00 CT) belongs to the next day.</summary>
		public DateTime TradingDate(DateTime ct)
		{
			int m = ct.Hour * 60 + ct.Minute;
			return m >= AsiaStartMin ? ct.Date.AddDays(1) : ct.Date;
		}

		/// <summary>Key that changes at every session boundary; used to reset clustering and baselines.</summary>
		public string SessionKey(DateTime ct)
		{
			return TradingDate(ct).ToString("yyyyMMdd", CultureInfo.InvariantCulture) + "_" + Classify(ct).ToString();
		}

		public bool IsLowLiquidity(JeronSession session)
		{
			return session != JeronSession.NewYork;
		}
	}

	// ---------------------------------------------------------------------------------
	//  Tiers and clusters
	// ---------------------------------------------------------------------------------
	public class JeronTier
	{
		public string Label;     // DT60, DT100, PT300 ...
		public long Size;
		public bool IsPower;
	}

	public class JeronCluster
	{
		public string Id = "";
		public JeronMethod Method;
		public JeronAggSide Side;
		public JeronSession Session;
		public bool IsHistorical;

		public DateTime StartLocal, StartCt, LastLocal, LastCt, DetectLocal, DetectCt;
		public double FirstPrice, LastPrice, MinPrice, MaxPrice, DetectPrice;
		public double PvSum;
		public long Volume;
		public int Prints;
		public int InferredPrints;
		public double Bid, Ask;                 // quote when the cluster started

		public List<JeronTier> Tiers;
		public int NextTierIdx;
		public bool Detected;
		public string HighestTierLabel = "";
		public long HighestTierSize;
		public bool ReachedPower;               // crossed at least the session's lowest Power Trade tier
		public DateTime PowerLocal, PowerCt;    // when it first became a Power Trade (real-time knowable)

		public JeronRegime Regime;
		public double RegimeStat;
		public long ActiveThreshold;            // power threshold in force for this cluster
		public bool ActiveQualified;            // cluster volume reached ActiveThreshold

		public bool Closed;
		public int BarIndex = -1;               // resolved by the host indicator
		public string ReactionSummary = "";     // filled ONLY after each reaction window has elapsed

		public double Vwap
		{
			get { return Volume > 0 ? PvSum / Volume : FirstPrice; }
		}
	}

	// ---------------------------------------------------------------------------------
	//  The engine
	// ---------------------------------------------------------------------------------
	public class JeronFlowEngine
	{
		// ---- configuration (set by the host before data flows) ----
		public double TickSize = 0.25;
		public JeronSessionClock Clock = new JeronSessionClock();
		public string IdPrefix = "JAT";

		public bool EnableBlock = true;
		public bool EnableBidAsk = true;
		public bool EnableTimeCluster = false;
		public bool IncludeInferredSide = false;     // trades between bid and ask (tick-rule side)
		public int TimeClusterMaxGapMs = 250;        // research parameter
		public int TimeClusterPriceTolTicks = 2;     // research parameter
		public double StaleQuoteSeconds = 5;         // real-time only

		public List<long> DeepTiers = new List<long>(new long[] { 60, 100 });
		public List<long> NyPowerTiers = new List<long>(new long[] { 300, 400, 500 });
		public List<long> LowLiqPowerTiers = new List<long>(new long[] { 150, 200 });

		public bool AutoAdapt = false;
		public int AdaptLookback = 200;
		public int AdaptMinSamples = 50;
		public double AdaptPercentile = 95;
		public double QuietCutoff = 40;
		public double ActiveCutoff = 90;
		public long AdaptFloor = 10;

		// ---- callbacks ----
		/// <summary>(cluster, tier crossed, isFirstCrossing). Fired the moment the tier becomes detectable.</summary>
		public Action<JeronCluster, JeronTier, bool> TierCrossed;
		/// <summary>Fired when a detected cluster ends (quote change, side change, gap, session boundary).</summary>
		public Action<JeronCluster> ClusterClosed;

		// ---- diagnostics ----
		public long TradeCount, MissingQuoteCount, StaleQuoteCount, InferredCount;
		public long[] EventCounts = new long[3];
		public JeronSession CurrentSession = JeronSession.PostNY;
		public JeronAggSide LastTradeSide = JeronAggSide.Unknown;
		public bool LastTradeInferred;
		public bool LastTradeQuoteOk;

		// ---- state ----
		private double quoteBid, quoteAsk;
		private DateTime quoteTime = DateTime.MinValue;
		private double prevTradePrice;
		private JeronAggSide prevTradeSide = JeronAggSide.Unknown;
		private string currentSessionKey = "";
		private JeronCluster bidAskCluster;
		private JeronCluster timeCluster;
		private int sequence;
		private readonly List<long> baseline = new List<long>();

		public void OnQuote(bool isBid, double price, DateTime timeLocal)
		{
			if (price <= 0) return;
			if (isBid) quoteBid = price; else quoteAsk = price;
			quoteTime = timeLocal;
		}

		public int BaselineCount
		{
			get { return baseline.Count; }
		}

		public double CurrentBaselineStat()
		{
			return Percentile(baseline, AdaptPercentile);
		}

		public List<long> PowerTiersFor(JeronSession session)
		{
			return session == JeronSession.NewYork ? NyPowerTiers : LowLiqPowerTiers;
		}

		public List<JeronTier> TiersFor(JeronSession session)
		{
			List<JeronTier> list = new List<JeronTier>();
			foreach (long size in DeepTiers)
				list.Add(new JeronTier { Label = "DT" + JeronFmt.I(size), Size = size, IsPower = false });
			foreach (long size in PowerTiersFor(session))
				list.Add(new JeronTier { Label = "PT" + JeronFmt.I(size), Size = size, IsPower = true });
			list.Sort(delegate(JeronTier a, JeronTier b)
			{
				int c = a.Size.CompareTo(b.Size);
				if (c != 0) return c;
				return a.IsPower.CompareTo(b.IsPower);
			});
			return list;
		}

		/// <summary>Call for every Last (trade) event, in arrival order.</summary>
		public void OnTrade(DateTime timeLocal, DateTime timeCt, double price, long volume, double eventBid, double eventAsk, bool isHistorical)
		{
			TradeCount++;

			// ---- session boundary: close open clusters, reset the adaptive baseline ----
			string key = Clock.SessionKey(timeCt);
			if (key != currentSessionKey)
			{
				CloseAll();
				currentSessionKey = key;
				CurrentSession = Clock.Classify(timeCt);
				baseline.Clear();
			}

			// ---- quote at the time of the trade ----
			bool quoteFromEvent = eventBid > 0 && eventAsk > 0 && eventAsk >= eventBid;
			double bid = quoteFromEvent ? eventBid : quoteBid;
			double ask = quoteFromEvent ? eventAsk : quoteAsk;
			bool quoteOk = bid > 0 && ask > 0 && ask >= bid;
			if (quoteOk && !quoteFromEvent && !isHistorical && quoteTime != DateTime.MinValue
				&& (timeLocal - quoteTime).TotalSeconds > StaleQuoteSeconds)
			{
				quoteOk = false;
				StaleQuoteCount++;
			}
			if (!quoteOk) MissingQuoteCount++;

			// ---- aggressor classification: at/above ask = buy, at/below bid = sell, else tick rule (flagged) ----
			JeronAggSide side;
			bool inferred = false;
			if (quoteOk && price >= ask - TickSize * 0.01) side = JeronAggSide.Buy;
			else if (quoteOk && price <= bid + TickSize * 0.01) side = JeronAggSide.Sell;
			else
			{
				inferred = true;
				if (prevTradePrice <= 0) side = JeronAggSide.Unknown;
				else if (price > prevTradePrice) side = JeronAggSide.Buy;
				else if (price < prevTradePrice) side = JeronAggSide.Sell;
				else side = prevTradeSide;
			}
			if (inferred) InferredCount++;
			prevTradePrice = price;
			if (side != JeronAggSide.Unknown) prevTradeSide = side;
			LastTradeSide = side;
			LastTradeInferred = inferred;
			LastTradeQuoteOk = quoteOk;

			bool eligible = side != JeronAggSide.Unknown && (!inferred || IncludeInferredSide);

			// ---- Method A: Individual Block ----
			if (EnableBlock && eligible)
			{
				List<JeronTier> tiers = TiersFor(CurrentSession);
				if (tiers.Count > 0 && volume >= tiers[0].Size)
				{
					JeronCluster block = NewCluster(JeronMethod.IndividualBlock, side, timeLocal, timeCt, price, bid, ask, isHistorical);
					AddPrint(block, timeLocal, timeCt, price, volume, inferred);
					CheckTiers(block, price);
					CloseCluster(ref block);
				}
			}

			// ---- Method B: Consistent Bid/Ask (requires a valid quote) ----
			if (EnableBidAsk)
			{
				if (!quoteOk)
				{
					CloseCluster(ref bidAskCluster);   // never build a cluster on a missing/stale quote
				}
				else
				{
					if (bidAskCluster != null && (!SamePrice(bidAskCluster.Bid, bid) || !SamePrice(bidAskCluster.Ask, ask)))
						CloseCluster(ref bidAskCluster);   // quote changed -> reset
					if (eligible)
					{
						if (bidAskCluster != null && bidAskCluster.Side != side)
							CloseCluster(ref bidAskCluster);   // side changed -> reset
						if (bidAskCluster == null)
							bidAskCluster = NewCluster(JeronMethod.ConsistentBidAsk, side, timeLocal, timeCt, price, bid, ask, isHistorical);
						AddPrint(bidAskCluster, timeLocal, timeCt, price, volume, inferred);
						CheckTiers(bidAskCluster, price);
					}
				}
			}

			// ---- Method C: Short-Duration Aggressor Cluster (experimental proxy) ----
			if (EnableTimeCluster && eligible)
			{
				if (timeCluster != null)
				{
					bool sideChanged = timeCluster.Side != side;
					bool gapExceeded = (timeLocal - timeCluster.LastLocal).TotalMilliseconds > TimeClusterMaxGapMs;
					bool outsideTol = Math.Abs(price - timeCluster.FirstPrice) > TimeClusterPriceTolTicks * TickSize + TickSize * 0.01;
					if (sideChanged || gapExceeded || outsideTol)
						CloseCluster(ref timeCluster);
				}
				if (timeCluster == null)
					timeCluster = NewCluster(JeronMethod.TimeCluster, side, timeLocal, timeCt, price, bid, ask, isHistorical);
				AddPrint(timeCluster, timeLocal, timeCt, price, volume, inferred);
				CheckTiers(timeCluster, price);
			}
		}

		public void CloseAll()
		{
			CloseCluster(ref bidAskCluster);
			CloseCluster(ref timeCluster);
		}

		// ------------------------------------------------------------------------------
		private bool SamePrice(double a, double b)
		{
			return Math.Abs(a - b) < TickSize * 0.5;
		}

		private JeronCluster NewCluster(JeronMethod method, JeronAggSide side, DateTime tLocal, DateTime tCt, double price, double bid, double ask, bool hist)
		{
			JeronCluster c = new JeronCluster();
			c.Method = method;
			c.Side = side;
			c.Session = CurrentSession;
			c.IsHistorical = hist;
			c.StartLocal = tLocal;
			c.StartCt = tCt;
			c.FirstPrice = price;
			c.MinPrice = price;
			c.MaxPrice = price;
			c.Bid = bid;
			c.Ask = ask;
			c.Tiers = TiersFor(CurrentSession);
			AssignRegime(c);   // uses ONLY clusters completed before this one started
			return c;
		}

		private void AddPrint(JeronCluster c, DateTime tLocal, DateTime tCt, double price, long volume, bool inferred)
		{
			c.LastLocal = tLocal;
			c.LastCt = tCt;
			c.LastPrice = price;
			if (price < c.MinPrice) c.MinPrice = price;
			if (price > c.MaxPrice) c.MaxPrice = price;
			c.PvSum += price * volume;
			c.Volume += volume;
			c.Prints++;
			if (inferred) c.InferredPrints++;
		}

		private void CheckTiers(JeronCluster c, double price)
		{
			while (c.Tiers != null && c.NextTierIdx < c.Tiers.Count && c.Volume >= c.Tiers[c.NextTierIdx].Size)
			{
				JeronTier tier = c.Tiers[c.NextTierIdx];
				bool first = !c.Detected;
				if (first)
				{
					c.Detected = true;
					sequence++;
					c.Id = IdPrefix + "-" + Clock.TradingDate(c.StartCt).ToString("yyyyMMdd", CultureInfo.InvariantCulture) + "-" + sequence.ToString("000000", CultureInfo.InvariantCulture);
					c.DetectLocal = c.LastLocal;
					c.DetectCt = c.LastCt;
					c.DetectPrice = price;
					EventCounts[(int)c.Method]++;
				}
				c.HighestTierLabel = tier.Label;
				c.HighestTierSize = tier.Size;
				if (tier.IsPower && !c.ReachedPower)
				{
					c.ReachedPower = true;
					c.PowerLocal = c.LastLocal;
					c.PowerCt = c.LastCt;
				}
				if (c.ActiveThreshold > 0 && c.Volume >= c.ActiveThreshold) c.ActiveQualified = true;
				c.NextTierIdx++;
				if (TierCrossed != null) TierCrossed(c, tier, first);
			}
		}

		private void CloseCluster(ref JeronCluster c)
		{
			if (c == null) return;
			if (c.Method == JeronMethod.ConsistentBidAsk && c.Volume >= AdaptFloor)
			{
				baseline.Add(c.Volume);
				while (baseline.Count > Math.Max(1, AdaptLookback)) baseline.RemoveAt(0);
			}
			if (c.Detected)
			{
				c.Closed = true;
				if (ClusterClosed != null) ClusterClosed(c);
			}
			c = null;
		}

		private void AssignRegime(JeronCluster c)
		{
			List<long> power = PowerTiersFor(c.Session);
			if (power.Count == 0) { c.Regime = JeronRegime.Research; c.ActiveThreshold = 0; return; }
			int mid = (power.Count - 1) / 2;
			if (!AutoAdapt)
			{
				c.Regime = JeronRegime.Research;      // all tiers logged in parallel; display uses lowest power tier
				c.ActiveThreshold = power[0];
				return;
			}
			if (baseline.Count < AdaptMinSamples)
			{
				c.Regime = JeronRegime.Warmup;
				c.RegimeStat = Percentile(baseline, AdaptPercentile);
				c.ActiveThreshold = power[mid];
				return;
			}
			double stat = Percentile(baseline, AdaptPercentile);
			c.RegimeStat = stat;
			if (stat < QuietCutoff) { c.Regime = JeronRegime.Quiet; c.ActiveThreshold = power[0]; }
			else if (stat >= ActiveCutoff) { c.Regime = JeronRegime.Active; c.ActiveThreshold = power[power.Count - 1]; }
			else { c.Regime = JeronRegime.Normal; c.ActiveThreshold = power[mid]; }
		}

		public static double Percentile(List<long> data, double pct)
		{
			if (data == null || data.Count == 0) return 0;
			long[] arr = data.ToArray();
			Array.Sort(arr);
			int k = (int)Math.Ceiling(pct / 100.0 * arr.Length) - 1;
			if (k < 0) k = 0;
			if (k >= arr.Length) k = arr.Length - 1;
			return arr[k];
		}
	}

	// ---------------------------------------------------------------------------------
	//  CSV logger
	// ---------------------------------------------------------------------------------
	public class JeronCsvLogger : IDisposable
	{
		private StreamWriter writer;
		private readonly object sync = new object();
		private string[] columns;
		private int pendingRows;
		public string FilePath = "";
		public long RowsWritten;

		public bool Open(string folder, string fileName, string[] cols, out string error)
		{
			error = "";
			try
			{
				Directory.CreateDirectory(folder);
				FilePath = Path.Combine(folder, fileName);
				columns = cols;
				writer = new StreamWriter(FilePath, false, new UTF8Encoding(false));
				writer.WriteLine(string.Join(",", cols));
				writer.Flush();
				return true;
			}
			catch (Exception ex)
			{
				error = ex.Message;
				writer = null;
				return false;
			}
		}

		public bool IsOpen
		{
			get { return writer != null; }
		}

		public void Write(Dictionary<string, string> row)
		{
			if (writer == null || row == null) return;
			lock (sync)
			{
				try
				{
					StringBuilder sb = new StringBuilder();
					for (int i = 0; i < columns.Length; i++)
					{
						if (i > 0) sb.Append(',');
						string cell;
						if (row.TryGetValue(columns[i], out cell)) sb.Append(Escape(cell));
					}
					writer.WriteLine(sb.ToString());
					RowsWritten++;
					pendingRows++;
					if (pendingRows >= 200) { writer.Flush(); pendingRows = 0; }
				}
				catch { }
			}
		}

		public void Flush()
		{
			if (writer == null) return;
			lock (sync)
			{
				try { writer.Flush(); pendingRows = 0; } catch { }
			}
		}

		public void Dispose()
		{
			lock (sync)
			{
				if (writer != null)
				{
					try { writer.Flush(); writer.Dispose(); } catch { }
					writer = null;
				}
			}
		}

		private static string Escape(string cell)
		{
			if (cell == null) return "";
			if (cell.IndexOfAny(new char[] { ',', '"', '\n', '\r' }) >= 0)
				return "\"" + cell.Replace("\"", "\"\"") + "\"";
			return cell;
		}
	}
}
