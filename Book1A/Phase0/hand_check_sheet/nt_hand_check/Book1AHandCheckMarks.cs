// Book1AHandCheckMarks.cs  (Book 1A Phase 0 hand check, Nov 5, 2026; v1.1 adds exact volume profiles from NT 1-tick data)
// Marks the four hand-check days on a 1-minute NQ chart and auto-checks the highs, lows and 08:10 close
// against the chart's own bars. Values come from hand_check_sheet v1.3 and the independent recompute
// (hand_check_sheet_independent_recompute.md). Read-only: no orders, no strategy logic, no P&L.
//
// Chart: NQ 12-25, 1 Minute, trading hours CME US Index Futures ETH. Any display time zone works:
// every window below is in Central time and converted to the chart's time zone.
// NT stamps a 1-minute bar at its END time, so a window "08:30-15:00 CT" = bars stamped 08:31 ... 15:00,
// the overnight 17:00-08:10 = bars stamped 17:01 ... 08:10, and the 08:10 bar holds the 08:09 trades.
//
// What it draws per day:
//   - shaded windows: prior-day cash (08:30-15:00 CT) and overnight (17:00 - 08:10 CT)
//   - PD cash high / low and ON high / low lines, labelled expected vs chart (OK or DIFF)
//   - a diamond at the 08:10 close, labelled expected vs chart
//   - each decision zone as a rectangle from 08:10 to 15:00 CT, label = zone, range, families
//   - each zone's point levels as short lines (08:10-10:10) coloured by family, and its bands / areas
//     (delta bands, POC areas, DD edge, REJ zones) as dashed outlines (10:10-12:10).
//     Delta bands are the bands that COUNT for the zone (label-collision fix from the recompute).
// NinjaScript Output window: a full report (day, check, expected, chart, result) plus every zone level.

#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class Book1AHandCheckMarks : Indicator
	{
		// ---- expected values per day: day | prior trading day | 08:10 close | ON high | ON low | PD cash high | PD cash low
		private static readonly string[] DayRows = new string[]
		{
			"2025-10-22|2025-10-21|25258.75|25338.25|25206.5|25348.5|25203.25",
			"2025-10-29|2025-10-28|26271|26309.75|26164.5|26231.5|26006",
			"2025-10-31|2025-10-30|26198.75|26274|26127.25|26182.5|25869",
			"2025-11-18|2025-11-17|24746.5|24959.5|24603.75|25254|24731.75",
		};

		// ---- decision zones and the levels behind them (ZONE | day | idx | label | lo | hi | families,
		//      LVL | day | idx | name | family | price, BAND | day | idx | name | family | lo | hi)
		private static readonly string[] ZoneRows = new string[]
		{
			"ZONE|2025-10-22|0|D_PDL_ONL_WKTVAL_ONVAL_ONTVAL_WKVAL_P3_ONPOC_AREA|25198.25|25265.0|6",
			"LVL|2025-10-22|0|PDVAL|AUCTION_VALUE|25254.0",
			"LVL|2025-10-22|0|PDL|STRUCTURE|25203.25",
			"LVL|2025-10-22|0|ONPOC|VOLUME|25250.0",
			"LVL|2025-10-22|0|ONVAL|AUCTION_VALUE|25222.75",
			"LVL|2025-10-22|0|ONTPOC|VOLUME|25267.5",
			"LVL|2025-10-22|0|ONTVAL|AUCTION_VALUE|25235.0",
			"LVL|2025-10-22|0|ONL|STRUCTURE|25206.5",
			"LVL|2025-10-22|0|VWAP|VWAP|25267.5",
			"LVL|2025-10-22|0|VWAPL1|VWAP|25238.25",
			"LVL|2025-10-22|0|WKVAL|AUCTION_VALUE|25244.25",
			"LVL|2025-10-22|0|VWAP_SD1_DN|VWAP|25238.13",
			"LVL|2025-10-22|0|WKVWAP|VWAP|25262.44",
			"LVL|2025-10-22|0|HVL|GEX|25230.0",
			"LVL|2025-10-22|0|HVL_0DTE|GEX|25260.0",
			"BAND|2025-10-22|0|T_DELTA_SELL_WK|DELTA|25215|25225",
			"BAND|2025-10-22|0|T_DELTA_SELL_WK|DELTA|25270|25280",
			"BAND|2025-10-22|0|T_DELTA_SELL_PD|DELTA|25215|25225",
			"BAND|2025-10-22|0|T_DELTA_SELL_PD|DELTA|25270|25280",
			"BAND|2025-10-22|0|T_DELTA_SELL_ON|DELTA|25225|25240",
			"BAND|2025-10-22|0|ONPOC_AREA|VOLUME|25245.0|25265.0",
			"ZONE|2025-10-22|1|D_PDVAH_ONH_WKVAH_PDH_PD2VAH_PD2H_P2|25325.5|25364.75|5",
			"LVL|2025-10-22|1|PDVAH|AUCTION_VALUE|25326.0",
			"LVL|2025-10-22|1|PDH|STRUCTURE|25348.5",
			"LVL|2025-10-22|1|PD2H|STRUCTURE|25354.5",
			"LVL|2025-10-22|1|ONH|STRUCTURE|25338.25",
			"LVL|2025-10-22|1|WKVAH|AUCTION_VALUE|25340.5",
			"LVL|2025-10-22|1|WKVWAP_SD1_UP|VWAP|25337.16",
			"BAND|2025-10-22|1|T_DELTA_BUY_WK|DELTA|25315|25355",
			"BAND|2025-10-22|1|PDPOC_AREA|VOLUME|25292.5|25332.5",
			"ZONE|2025-10-22|2|T_HTFVAH|25389.75|25399.75|2",
			"LVL|2025-10-22|2|HTFVAH|AUCTION_VALUE|25394.75",
			"LVL|2025-10-22|2|CR|GEX|25400.0",
			"LVL|2025-10-22|2|CR_0DTE|GEX|25400.0",
			"ZONE|2025-10-29|0|PDPOC_AREA_DD_EDGE_PD_D_PDPOC_WKPOC_PDTPOC|26035.0|26079.75|3",
			"LVL|2025-10-29|0|PDPOC|VOLUME|26045.0",
			"LVL|2025-10-29|0|PDTPOC|VOLUME|26052.5",
			"LVL|2025-10-29|0|WKPOC|VOLUME|26045.0",
			"BAND|2025-10-29|0|T_DELTA_BUY_WK|DELTA|26045|26055",
			"BAND|2025-10-29|0|T_DELTA_SELL_PD|DELTA|26030|26040",
			"BAND|2025-10-29|0|T_DELTA_BUY_PD|DELTA|26045|26055",
			"BAND|2025-10-29|0|T_DELTA_BUY_PD|DELTA|26080|26095",
			"BAND|2025-10-29|0|PDPOC_AREA|VOLUME|26035.0|26055.0",
			"BAND|2025-10-29|0|DD_EDGE_PD|STRUCTURE|26039.75|26079.75",
			"ZONE|2025-10-29|1|D_PDVAH_PDSET_ONL_PDTVAH|26149.5|26179.75|4",
			"LVL|2025-10-29|1|PDVAH|AUCTION_VALUE|26154.5",
			"LVL|2025-10-29|1|ONL|STRUCTURE|26164.5",
			"LVL|2025-10-29|1|WKVWAP_SD1_UP|VWAP|26151.07",
			"LVL|2025-10-29|1|PS|GEX|26180.0",
			"LVL|2025-10-29|1|PS_0DTE|GEX|26180.0",
			"ZONE|2025-10-29|2|D_ONTVAL_PDH_ONVAL_ONPOC_ONPOC_AREA_T_ONTPOC|26220.0|26277.5|5",
			"LVL|2025-10-29|2|PDH|STRUCTURE|26231.5",
			"LVL|2025-10-29|2|ONPOC|VOLUME|26240.0",
			"LVL|2025-10-29|2|ONVAL|AUCTION_VALUE|26231.75",
			"LVL|2025-10-29|2|ONTPOC|VOLUME|26272.5",
			"LVL|2025-10-29|2|ONTVAL|AUCTION_VALUE|26225.0",
			"LVL|2025-10-29|2|VWAP|VWAP|26247.0",
			"LVL|2025-10-29|2|VWAPU1|VWAP|26281.75",
			"LVL|2025-10-29|2|VWAP_SD1_UP|VWAP|26281.76",
			"LVL|2025-10-29|2|HVL_0DTE|GEX|26210.0",
			"BAND|2025-10-29|2|ONPOC_AREA|VOLUME|26227.5|26267.5",
			"ZONE|2025-10-29|3|D_ONVAH_WKTVAH_ONTVAH_WKVAH_ONH|26286.75|26314.75|5",
			"LVL|2025-10-29|3|ONVAH|AUCTION_VALUE|26291.75",
			"LVL|2025-10-29|3|ONTVAH|AUCTION_VALUE|26299.75",
			"LVL|2025-10-29|3|ONH|STRUCTURE|26309.75",
			"LVL|2025-10-29|3|VWAPU1|VWAP|26281.75",
			"LVL|2025-10-29|3|WKVAH|AUCTION_VALUE|26303.25",
			"LVL|2025-10-29|3|VWAP_SD1_UP|VWAP|26281.76",
			"LVL|2025-10-29|3|CR|GEX|26300.0",
			"LVL|2025-10-29|3|CR_0DTE|GEX|26300.0",
			"BAND|2025-10-29|3|T_DELTA_BUY_ON|DELTA|26285|26295",
			"ZONE|2025-10-31|0|D_WKVAL_PDVAL_PDPOC_WKPOC_PDTVAL|25952.25|25980.0|3",
			"LVL|2025-10-31|0|PDPOC|VOLUME|25970.75",
			"LVL|2025-10-31|0|PDVAL|AUCTION_VALUE|25967.5",
			"LVL|2025-10-31|0|WKPOC|VOLUME|25970.75",
			"LVL|2025-10-31|0|WKVAL|AUCTION_VALUE|25957.25",
			"BAND|2025-10-31|0|T_DELTA_SELL_PD|DELTA|25945|25955",
			"BAND|2025-10-31|0|T_DELTA_SELL_PD|DELTA|25975|25985",
			"ZONE|2025-10-31|1|D_WKTVAL_PD3L_PD3VAL_PD3TVAL_PDTPOC_PD3POC_P2_PDPOC_AREA_REJ|25995.0|26099.75|6",
			"LVL|2025-10-31|1|PDVAH|AUCTION_VALUE|26090.0",
			"LVL|2025-10-31|1|PDTPOC|VOLUME|26037.5",
			"LVL|2025-10-31|1|PD2L|STRUCTURE|26049.25",
			"LVL|2025-10-31|1|PD3L|STRUCTURE|26006.0",
			"LVL|2025-10-31|1|WKVWAP|VWAP|26084.24",
			"LVL|2025-10-31|1|CR|GEX|26000.0",
			"BAND|2025-10-31|1|T_DELTA_BUY_WK|DELTA|26070|26080",
			"BAND|2025-10-31|1|T_DELTA_SELL_PD|DELTA|26040|26050",
			"BAND|2025-10-31|1|PDPOC_AREA|VOLUME|26040.0|26070.0",
			"ZONE|2025-10-31|2|REJ_HIGH_PD_D_PD3VAH_ONTVAL_ONVAL_D_PD3TVAH_PDH_WKTPOC_ONPOC|26142.5|26236.5|6",
			"LVL|2025-10-31|2|PDH|STRUCTURE|26182.5",
			"LVL|2025-10-31|2|PD3H|STRUCTURE|26231.5",
			"LVL|2025-10-31|2|ONVAH|AUCTION_VALUE|26217.25",
			"LVL|2025-10-31|2|ONPOC|VOLUME|26190.0",
			"LVL|2025-10-31|2|ONVAL|AUCTION_VALUE|26158.5",
			"LVL|2025-10-31|2|ONTVAH|AUCTION_VALUE|26209.75",
			"LVL|2025-10-31|2|ONTPOC|VOLUME|26192.5",
			"LVL|2025-10-31|2|ONTVAL|AUCTION_VALUE|26155.0",
			"LVL|2025-10-31|2|VWAP|VWAP|26192.25",
			"LVL|2025-10-31|2|VWAPU1|VWAP|26222.25",
			"LVL|2025-10-31|2|VWAPL1|VWAP|26162.5",
			"LVL|2025-10-31|2|VWAP_SD1_UP|VWAP|26222.15",
			"LVL|2025-10-31|2|VWAP_SD1_DN|VWAP|26162.38",
			"LVL|2025-10-31|2|WKVWAP_SD1_UP|VWAP|26230.44",
			"LVL|2025-10-31|2|CR_0DTE|GEX|26150.0",
			"BAND|2025-10-31|2|T_DELTA_SELL_WK|DELTA|26230|26240",
			"BAND|2025-10-31|2|T_DELTA_BUY_ON|DELTA|26200|26215",
			"BAND|2025-10-31|2|ONPOC_AREA|VOLUME|26175.0|26200.0",
			"BAND|2025-10-31|2|REJ_HIGH_PD|STRUCTURE|26142.5|26182.5",
			"ZONE|2025-10-31|3|T_PD2TPOC|26237.5|26247.5|2",
			"BAND|2025-10-31|3|T_DELTA_SELL_WK|DELTA|26230|26240",
			"BAND|2025-10-31|3|WKPOC_AREA|VOLUME|26252.5|26292.5",
			"ZONE|2025-10-31|4|WKPOC_AREA_D_WKVAH_ONH_PD2POC_REJ_HIGH_WK|26252.5|26306.5|4",
			"LVL|2025-10-31|4|ONH|STRUCTURE|26274.0",
			"LVL|2025-10-31|4|WKVAH|AUCTION_VALUE|26270.5",
			"BAND|2025-10-31|4|T_DELTA_BUY_WK|DELTA|26275|26290",
			"BAND|2025-10-31|4|WKPOC_AREA|VOLUME|26252.5|26292.5",
			"BAND|2025-10-31|4|REJ_HIGH_WK|STRUCTURE|26266.5|26306.5",
			"ZONE|2025-11-18|0|T_ONL|24598.75|24608.75|2",
			"LVL|2025-11-18|0|ONL|STRUCTURE|24603.75",
			"LVL|2025-11-18|0|PS_0DTE|GEX|24600.0",
			"ZONE|2025-11-18|1|T_ONTVAL_ONVAL|24665.0|24685.5|2",
			"LVL|2025-11-18|1|ONVAL|AUCTION_VALUE|24680.5",
			"LVL|2025-11-18|1|ONTVAL|AUCTION_VALUE|24670.0",
			"BAND|2025-11-18|1|T_DELTA_BUY_ON|DELTA|24650|24660",
			"ZONE|2025-11-18|2|ONPOC_AREA_D_PDL_ONTPOC_ONPOC|24715.0|24755.0|3",
			"LVL|2025-11-18|2|PDL|STRUCTURE|24731.75",
			"LVL|2025-11-18|2|ONPOC|VOLUME|24750.0",
			"LVL|2025-11-18|2|ONTPOC|VOLUME|24742.5",
			"BAND|2025-11-18|2|T_DELTA_SELL_ON|DELTA|24700|24720",
			"BAND|2025-11-18|2|ONPOC_AREA|VOLUME|24715.0|24755.0",
			"ZONE|2025-11-18|3|T_HTFPOC|24822.5|24832.5|2",
			"LVL|2025-11-18|3|HTFPOC|VOLUME|24827.5",
			"BAND|2025-11-18|3|T_DELTA_SELL_WK|DELTA|24820|24845",
			"BAND|2025-11-18|3|T_DELTA_SELL_ON|DELTA|24820|24845",
			"ZONE|2025-11-18|4|D_ONVAH_WKVAL_ONTVAH|24846.25|24864.75|3",
			"LVL|2025-11-18|4|ONVAH|AUCTION_VALUE|24851.25",
			"LVL|2025-11-18|4|ONTVAH|AUCTION_VALUE|24859.75",
			"LVL|2025-11-18|4|VWAPU1|VWAP|24856.0",
			"LVL|2025-11-18|4|WKVAL|AUCTION_VALUE|24856.0",
			"LVL|2025-11-18|4|VWAP_SD1_UP|VWAP|24856.07",
			"BAND|2025-11-18|4|T_DELTA_SELL_WK|DELTA|24820|24845",
			"BAND|2025-11-18|4|T_DELTA_SELL_ON|DELTA|24820|24845",
		};

		private class DayCheck
		{
			public DateTime Day, Pd;
			public double ExpPx, ExpOnH, ExpOnL, ExpPdH, ExpPdL;
			public double OnH = double.MinValue, OnL = double.MaxValue, PdH = double.MinValue, PdL = double.MaxValue, Px = double.NaN;
			public int OnBars, PdBars;
			public bool Done;
			public DateTime OnStart { get { return Pd.Date.AddHours(17); } }      // previous session open (Mon: Fri 17:00 is not used; none of the 4 days is a Monday)
			public DateTime AsOf { get { return Day.Date.AddHours(8).AddMinutes(10); } }
			public DateTime PdCashStart { get { return Pd.Date.AddHours(8).AddMinutes(30); } }
			public DateTime PdCashEnd { get { return Pd.Date.AddHours(15); } }
		}

		// ---- v1.1 volume profiles (exact, from NT 1-tick data): day | profile | window start CT | window end CT | POC | VAH | VAL (recompute)
		private static readonly string[] ProfRows = new string[]
		{
			"2025-10-22|PD2|2025-10-20 08:30|2025-10-20 15:00|25318.5|25353|25276.75",
			"2025-10-22|PD|2025-10-21 08:30|2025-10-21 15:00|25300|25326|25254",
			"2025-10-22|ON|2025-10-21 17:00|2025-10-22 08:10|25250|25286.5|25222.75",
			"2025-10-22|WK|2025-10-19 17:00|2025-10-22 08:10|25300|25340.5|25244.25",
			"2025-10-29|PD2|2025-10-27 08:30|2025-10-27 15:00|25925|25980.5|25866",
			"2025-10-29|PD|2025-10-28 08:30|2025-10-28 15:00|26045|26154.5|26015",
			"2025-10-29|ON|2025-10-28 17:00|2025-10-29 08:10|26240|26291.75|26231.75",
			"2025-10-29|WK|2025-10-26 17:00|2025-10-29 08:10|26045|26303.25|25907.5",
			"2025-10-31|PD2|2025-10-29 08:30|2025-10-29 15:00|26275|26303.75|26210",
			"2025-10-31|PD|2025-10-30 08:30|2025-10-30 15:00|25970.75|26090|25967.5",
			"2025-10-31|ON|2025-10-30 17:00|2025-10-31 08:10|26190|26217.25|26158.5",
			"2025-10-31|WK|2025-10-26 17:00|2025-10-31 08:10|25970.75|26270.5|25957.25",
			"2025-11-18|PD2|2025-11-14 08:30|2025-11-14 15:00|25150|25289|24978.5",
			"2025-11-18|PD|2025-11-17 08:30|2025-11-17 15:00|25150|25253.5|24932.25",
			"2025-11-18|ON|2025-11-17 17:00|2025-11-18 08:10|24750|24851.25|24680.5",
			"2025-11-18|WK|2025-11-16 17:00|2025-11-18 08:10|25150|25285.25|24856",
		};

		private class VProf
		{
			public string Day, Name; public DateTime T0, T1; public double EPoc, EVah, EVal;
			public Dictionary<long, long> Vol = new Dictionary<long, long>();
			public long Ticks; public DateTime FirstTick = DateTime.MaxValue;
		}
		private List<VProf> vprofs;
		private DateTime firstTickCt = DateTime.MaxValue;

		private class ZoneLevel { public string Name, Family; public double Lo, Hi; public bool IsBand; }
		private class Zone { public string Day, Label; public int Idx, Families; public double Lo, Hi; public List<ZoneLevel> Levels = new List<ZoneLevel>(); }

		private List<DayCheck> days;
		private List<Zone> zones;
		private TimeZoneInfo central;
		private StringBuilder summary;
		private int nOk, nDiff, nMissing;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description = "Book 1A Phase 0 hand check: marks the 4 check days (zones, levels, highs / lows, 08:10 close) and auto-checks highs / lows / 08:10 close against the chart bars.";
				Name = "Book1AHandCheckMarks";
				Calculate = Calculate.OnBarClose;
				IsOverlay = true;
				DisplayInDataBox = false;
				DrawOnPricePanel = true;
				PaintPriceMarkers = false;
				IsSuspendedWhileInactive = true;
				ShowWindows = true;
				ShowZones = true;
				ShowLevels = true;
				ShowLevelLabels = false;
				ZoneOpacity = 12;
				WindowOpacity = 6;
				UseTickProfiles = true;
			}
			else if (State == State.Configure)
			{
				if (UseTickProfiles) AddDataSeries(BarsPeriodType.Tick, 1);
			}
			else if (State == State.DataLoaded)
			{
				central = TimeZoneInfo.FindSystemTimeZoneById("Central Standard Time");
				days = new List<DayCheck>();
				foreach (string r in DayRows)
				{
					string[] p = r.Split('|');
					DayCheck d = new DayCheck();
					d.Day = DateTime.ParseExact(p[0], "yyyy-MM-dd", CultureInfo.InvariantCulture);
					d.Pd = DateTime.ParseExact(p[1], "yyyy-MM-dd", CultureInfo.InvariantCulture);
					d.ExpPx = D(p[2]); d.ExpOnH = D(p[3]); d.ExpOnL = D(p[4]); d.ExpPdH = D(p[5]); d.ExpPdL = D(p[6]);
					days.Add(d);
				}
				zones = new List<Zone>();
				foreach (string r in ZoneRows)
				{
					string[] p = r.Split('|');
					if (p[0] == "ZONE")
						zones.Add(new Zone { Day = p[1], Idx = int.Parse(p[2]), Label = p[3], Lo = D(p[4]), Hi = D(p[5]), Families = int.Parse(p[6]) });
					else
					{
						Zone z = zones.LastOrDefault(x => x.Day == p[1] && x.Idx == int.Parse(p[2]));
						if (z == null) continue;
						if (p[0] == "LVL") z.Levels.Add(new ZoneLevel { Name = p[3], Family = p[4], Lo = D(p[5]), Hi = D(p[5]), IsBand = false });
						else z.Levels.Add(new ZoneLevel { Name = p[3], Family = p[4], Lo = D(p[5]), Hi = D(p[6]), IsBand = true });
					}
				}
				vprofs = new List<VProf>();
				foreach (string r in ProfRows)
				{
					string[] p = r.Split('|');
					vprofs.Add(new VProf { Day = p[0], Name = p[1],
						T0 = DateTime.ParseExact(p[2], "yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture),
						T1 = DateTime.ParseExact(p[3], "yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture),
						EPoc = D(p[4]), EVah = D(p[5]), EVal = D(p[6]) });
				}
				summary = new StringBuilder();
				nOk = nDiff = nMissing = 0;
				ClearOutputWindow();
				Print("Book 1A hand check marks: chart time zone = " + Core.Globals.GeneralOptions.TimeZoneInfo.Id + "; all windows in Central time.");
			}
			else if (State == State.Realtime || State == State.Terminated)
			{
				if (days != null && State == State.Realtime)
					foreach (DayCheck d in days)
					{
						if (d.Done) continue;
						if (d.OnBars + d.PdBars > 0) Evaluate(d);
						else Print(d.Day.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + ": not on this chart (scroll / load more days back, 1 Minute, NQ 12-25)");
					}
			}
		}

		private static double D(string s) { return double.Parse(s, CultureInfo.InvariantCulture); }

		private DateTime ToCt(DateTime chartTime)
		{
			return TimeZoneInfo.ConvertTime(DateTime.SpecifyKind(chartTime, DateTimeKind.Unspecified), Core.Globals.GeneralOptions.TimeZoneInfo, central);
		}

		private DateTime FromCt(DateTime ct)
		{
			return TimeZoneInfo.ConvertTime(DateTime.SpecifyKind(ct, DateTimeKind.Unspecified), central, Core.Globals.GeneralOptions.TimeZoneInfo);
		}

		protected override void OnBarUpdate()
		{
			if (BarsInProgress == 1)
			{
				// one 1-tick bar = one trade: price = Closes[1][0], size = Volumes[1][0]; window [T0, T1) on trade time (CT)
				DateTime tc = ToCt(Times[1][0]);
				if (tc < firstTickCt) firstTickCt = tc;
				long key = (long)Math.Round(Closes[1][0] / 0.25);
				long sz = (long)Volumes[1][0];
				foreach (VProf vp in vprofs)
					if (tc >= vp.T0 && tc < vp.T1)
					{
						long cur; vp.Vol.TryGetValue(key, out cur); vp.Vol[key] = cur + sz;
						vp.Ticks++;
						if (tc < vp.FirstTick) vp.FirstTick = tc;
					}
				return;
			}
			if (BarsInProgress != 0) return;
			if (CurrentBar == 0 && (BarsPeriod.BarsPeriodType != BarsPeriodType.Minute || BarsPeriod.Value != 1))
				Draw.TextFixed(this, "b1a_warn", "Book1AHandCheckMarks: use a 1 Minute chart. The auto-check needs 1-minute bars.", TextPosition.Center);

			DateTime ct = ToCt(Time[0]);     // bar END time in Central
			foreach (DayCheck d in days)
			{
				if (d.Done) continue;
				if (ct > d.OnStart && ct <= d.AsOf)
				{
					d.OnBars++;
					if (High[0] > d.OnH) d.OnH = High[0];
					if (Low[0] < d.OnL) d.OnL = Low[0];
				}
				if (ct > d.PdCashStart && ct <= d.PdCashEnd)
				{
					d.PdBars++;
					if (High[0] > d.PdH) d.PdH = High[0];
					if (Low[0] < d.PdL) d.PdL = Low[0];
				}
				if (ct == d.AsOf) d.Px = Close[0];
				if (ct > d.AsOf) Evaluate(d);
			}
		}

		private string CheckValue(string day, string what, double exp, double got, int bars, bool loaded)
		{
			string res;
			if (!loaded || bars == 0 || double.IsNaN(got) || got == double.MinValue || got == double.MaxValue) { res = "NOT LOADED"; nMissing++; }
			else if (Math.Abs(exp - got) < 1e-9) { res = "OK"; nOk++; }
			else { res = "DIFF " + (got - exp).ToString("+0.00;-0.00", CultureInfo.InvariantCulture); nDiff++; }
			string shown = (bars == 0 || double.IsNaN(got) || got == double.MinValue || got == double.MaxValue) ? "-" : got.ToString("0.00", CultureInfo.InvariantCulture);
			Print(string.Format(CultureInfo.InvariantCulture, "{0} | {1,-22} | expected {2,9:0.00} | chart {3,9} | {4}", day, what, exp, shown, res));
			summary.AppendLine(string.Format(CultureInfo.InvariantCulture, "{0} {1}: {2}", day.Substring(5), what, res));
			return res;
		}

		private void Evaluate(DayCheck d)
		{
			d.Done = true;
			string day = d.Day.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
			bool loaded = ToCt(Time.GetValueAt(0)) <= d.PdCashStart;   // the chart must start before the prior-day cash open
			Print("---- " + day + " (prior trading day " + d.Pd.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + ")" + (loaded ? "" : "  * chart starts too late: load more days *"));
			string rPx = CheckValue(day, "08:10 close", d.ExpPx, d.Px, double.IsNaN(d.Px) ? 0 : 1, true);
			string rOnH = CheckValue(day, "ON high (17:00-08:10)", d.ExpOnH, d.OnH, d.OnBars, true);
			string rOnL = CheckValue(day, "ON low (17:00-08:10)", d.ExpOnL, d.OnL, d.OnBars, true);
			string rPdH = CheckValue(day, "PD cash high", d.ExpPdH, d.PdH, d.PdBars, loaded);
			string rPdL = CheckValue(day, "PD cash low", d.ExpPdL, d.PdL, d.PdBars, loaded);

			string t = "b1a_" + day + "_";
			DateTime onS = FromCt(d.OnStart), asOf = FromCt(d.AsOf), pdS = FromCt(d.PdCashStart), pdE = FromCt(d.PdCashEnd);
			DateTime zEnd = FromCt(d.Day.Date.AddHours(15));

			if (ShowWindows)
			{
				Draw.RegionHighlightX(this, t + "win_pd", pdS, pdE, Brushes.Transparent, Brushes.SteelBlue, WindowOpacity);
				Draw.RegionHighlightX(this, t + "win_on", onS, asOf, Brushes.Transparent, Brushes.MediumPurple, WindowOpacity);
			}
			HLine(t + "pdh", pdS, pdE, d.ExpPdH, Brushes.Orange, "PD cash H " + F(d.ExpPdH) + " exp / " + Got(d.PdH) + " chart: " + rPdH, 12);
			HLine(t + "pdl", pdS, pdE, d.ExpPdL, Brushes.Orange, "PD cash L " + F(d.ExpPdL) + " exp / " + Got(d.PdL) + " chart: " + rPdL, -12);
			HLine(t + "onh", onS, asOf, d.ExpOnH, Brushes.Violet, "ON H " + F(d.ExpOnH) + " exp / " + Got(d.OnH) + " chart: " + rOnH, 12);
			HLine(t + "onl", onS, asOf, d.ExpOnL, Brushes.Violet, "ON L " + F(d.ExpOnL) + " exp / " + Got(d.OnL) + " chart: " + rOnL, -12);
			Draw.Diamond(this, t + "px", false, asOf, d.ExpPx, Brushes.White);
			Draw.Text(this, t + "pxt", false, "08:10 close " + F(d.ExpPx) + " exp / " + (double.IsNaN(d.Px) ? "-" : F(d.Px)) + " chart: " + rPx,
				asOf, d.ExpPx, -18, Brushes.White, new SimpleFont("Arial", 10), TextAlignment.Center, Brushes.Transparent, Brushes.Black, 60);

			Print("  decision zones (levels: family, price or band; bands are the ones that count for the zone)");
			foreach (Zone z in zones.Where(x => x.Day == day))
			{
				string zt = t + "z" + z.Idx;
				string zl = "Z" + (z.Idx + 1) + " " + z.Label + "  " + F(z.Lo) + " - " + F(z.Hi) + " (" + (z.Hi - z.Lo).ToString("0.00", CultureInfo.InvariantCulture) + " pts, " + z.Families + " fam)";
				Print("  " + zl);
				foreach (ZoneLevel l in z.Levels)
					Print("      " + l.Name + " | " + l.Family + " | " + (l.IsBand ? F(l.Lo) + " - " + F(l.Hi) : F(l.Lo)));
				if (!ShowZones) continue;
				Draw.Rectangle(this, zt, false, asOf, z.Lo, zEnd, z.Hi, Brushes.Gold, Brushes.Gold, ZoneOpacity);
				Draw.Text(this, zt + "_t", false, zl, zEnd, z.Hi, 8, Brushes.Gold, new SimpleFont("Arial", 9), TextAlignment.Left, Brushes.Transparent, Brushes.Black, 50);
				if (!ShowLevels) continue;
				DateTime a = FromCt(d.AsOf), b = FromCt(d.Day.Date.AddHours(10).AddMinutes(10)), c = FromCt(d.Day.Date.AddHours(12).AddMinutes(10));
				int k = 0;
				foreach (ZoneLevel l in z.Levels)
				{
					Brush br = FamilyBrush(l.Family);
					string lt = zt + "_l" + (k++);
					if (!l.IsBand)
					{
						Draw.Line(this, lt, false, a, l.Lo, b, l.Lo, br, DashStyleHelper.Solid, 2);
						if (ShowLevelLabels)
							Draw.Text(this, lt + "_t", false, l.Name + " " + F(l.Lo), b, l.Lo, (k % 2 == 0 ? 6 : -6), br, new SimpleFont("Arial", 8), TextAlignment.Left, Brushes.Transparent, Brushes.Transparent, 0);
					}
					else
					{
						Rectangle rb = Draw.Rectangle(this, lt, false, b, l.Lo, c, l.Hi, br, Brushes.Transparent, 0);
						if (rb != null && rb.OutlineStroke != null) rb.OutlineStroke.DashStyleHelper = DashStyleHelper.Dash;
						if (ShowLevelLabels)
							Draw.Text(this, lt + "_t", false, l.Name + " " + F(l.Lo) + "-" + F(l.Hi), c, l.Hi, 6, br, new SimpleFont("Arial", 8), TextAlignment.Left, Brushes.Transparent, Brushes.Transparent, 0);
					}
				}
			}
			if (UseTickProfiles) EvaluateProfiles(d, day);
			Draw.TextFixed(this, "b1a_summary", "Book 1A hand check (auto part): OK " + nOk + ", DIFF " + nDiff + ", not loaded " + nMissing + "\n" + summary.ToString(),
				TextPosition.TopRight, Brushes.White, new SimpleFont("Consolas", 10), Brushes.Transparent, Brushes.Black, 70);
		}

		private void HLine(string tag, DateTime s, DateTime e, double y, Brush br, string label, int yOff)
		{
			Draw.Line(this, tag, false, s, y, e, y, br, DashStyleHelper.Solid, 2);
			Draw.Text(this, tag + "_t", false, label, e, y, yOff, br, new SimpleFont("Arial", 9), TextAlignment.Left, Brushes.Transparent, Brushes.Black, 60);
		}

		private static string F(double x) { return x.ToString("0.00", CultureInfo.InvariantCulture); }
		private static string Got(double x) { return (x == double.MinValue || x == double.MaxValue || double.IsNaN(x)) ? "-" : F(x); }

		private static Brush FamilyBrush(string fam)
		{
			switch (fam)
			{
				case "AUCTION_VALUE": return Brushes.DodgerBlue;
				case "STRUCTURE": return Brushes.Orange;
				case "DELTA": return Brushes.Magenta;
				case "VOLUME": return Brushes.Gold;
				case "GEX": return Brushes.LimeGreen;
				case "VWAP": return Brushes.Cyan;
				default: return Brushes.Gray;
			}
		}

		// Value area exactly as the map: 1-tick rows, POC = largest row (ties: nearest the middle of the range),
		// expand one row at a time to the larger neighbour (above wins ties) until 70% of the volume is inside.
		private bool ValueArea(Dictionary<long, long> vol, out double poc, out double vah, out double val)
		{
			poc = vah = val = double.NaN;
			if (vol.Count == 0) return false;
			long mn = vol.Keys.Min(), mx = vol.Keys.Max();
			int n = (int)(mx - mn + 1);
			long[] rows = new long[n]; long tot = 0;
			foreach (KeyValuePair<long, long> kv in vol) { rows[kv.Key - mn] += kv.Value; tot += kv.Value; }
			double mid = (n - 1) / 2.0; int pi = 0;
			for (int i = 1; i < n; i++)
				if (rows[i] > rows[pi] || (rows[i] == rows[pi] && Math.Abs(i - mid) < Math.Abs(pi - mid))) pi = i;
			double target = tot * 0.70; int lo = pi, hi = pi; double acc = rows[pi];
			while (acc < target && (lo > 0 || hi < n - 1))
			{
				long up = hi + 1 < n ? rows[hi + 1] : -1, dn = lo - 1 >= 0 ? rows[lo - 1] : -1;
				if (up >= dn) { hi++; acc += up; } else { lo--; acc += dn; }
			}
			poc = (mn + pi) * 0.25; vah = (mn + hi) * 0.25; val = (mn + lo) * 0.25;
			return true;
		}

		private string Res(double got, double exp)
		{
			double dd = Math.Abs(got - exp);
			if (dd < 1e-9) { nOk++; return "OK"; }
			if (dd <= 5.0) { nOk++; return "<=1 row (" + (got - exp).ToString("+0.00;-0.00", CultureInfo.InvariantCulture) + ")"; }
			nDiff++; return "DIFF " + (got - exp).ToString("+0.00;-0.00", CultureInfo.InvariantCulture);
		}

		private void EvaluateProfiles(DayCheck d, string day)
		{
			Print("  volume profiles from NT 1-tick data (1-tick rows, 70% value area)");
			foreach (VProf vp in vprofs.Where(x => x.Day == day))
			{
				bool partial = firstTickCt > vp.T0;
				double poc, vah, val;
				if (partial || !ValueArea(vp.Vol, out poc, out vah, out val))
				{
					nMissing++;
					string why = vp.Ticks == 0 ? "NO TICKS" : "PARTIAL (tick data starts " + firstTickCt.ToString("MM-dd HH:mm", CultureInfo.InvariantCulture) + ")";
					Print(string.Format("  {0} {1,-3} {2:MM-dd HH:mm} - {3:MM-dd HH:mm} CT: NOT LOADED, {4}", day, vp.Name, vp.T0, vp.T1, why));
					summary.AppendLine(day.Substring(5) + " " + vp.Name + " profile: NOT LOADED");
					continue;
				}
				string rv = Res(vah, vp.EVah), rp = Res(poc, vp.EPoc), rl = Res(val, vp.EVal);
				string line = string.Format(CultureInfo.InvariantCulture, "{0} VAH {1:0.00}/{2:0.00} {3} | POC {4:0.00}/{5:0.00} {6} | VAL {7:0.00}/{8:0.00} {9}",
					vp.Name, vah, vp.EVah, rv, poc, vp.EPoc, rp, val, vp.EVal, rl);
				Print(string.Format(CultureInfo.InvariantCulture, "  {0} {1:MM-dd HH:mm} - {2:MM-dd HH:mm} CT ({3:N0} trades) {4}", day, vp.T0, vp.T1, vp.Ticks, line));
				summary.AppendLine(day.Substring(5) + " " + line);
				if (vp.Name == "WK") continue;   // the week window overlaps the others: report only, no lines
				Brush br = vp.Name == "PD" ? Brushes.Orange : vp.Name == "PD2" ? Brushes.Yellow : Brushes.Violet;
				DateTime a = FromCt(vp.T0), b = FromCt(vp.T1);
				string tg = "b1a_" + day + "_vp_" + vp.Name;
				Draw.Line(this, tg + "_vah", false, a, vah, b, vah, br, DashStyleHelper.Dash, 1);
				Draw.Line(this, tg + "_poc", false, a, poc, b, poc, br, DashStyleHelper.Solid, 2);
				Draw.Line(this, tg + "_val", false, a, val, b, val, br, DashStyleHelper.Dash, 1);
				Draw.Text(this, tg + "_t", false, vp.Name + " POC " + F(poc) + " " + rp + " / VAH " + F(vah) + " " + rv + " / VAL " + F(val) + " " + rl,
					a, poc, 12, br, new SimpleFont("Arial", 9), TextAlignment.Left, Brushes.Transparent, Brushes.Black, 60);
			}
		}

		#region Properties
		[NinjaScriptProperty]
		[Display(Name = "Volume profiles from 1-tick data (exact)", Order = 0, GroupName = "Display")]
		public bool UseTickProfiles { get; set; }

		[NinjaScriptProperty]
		[Display(Name = "Shade windows (PD cash, overnight)", Order = 1, GroupName = "Display")]
		public bool ShowWindows { get; set; }

		[NinjaScriptProperty]
		[Display(Name = "Show decision zones", Order = 2, GroupName = "Display")]
		public bool ShowZones { get; set; }

		[NinjaScriptProperty]
		[Display(Name = "Show zone levels and bands", Order = 3, GroupName = "Display")]
		public bool ShowLevels { get; set; }

		[NinjaScriptProperty]
		[Display(Name = "Label every level (busy)", Order = 4, GroupName = "Display")]
		public bool ShowLevelLabels { get; set; }

		[NinjaScriptProperty]
		[Range(0, 100)]
		[Display(Name = "Zone fill opacity %", Order = 5, GroupName = "Display")]
		public int ZoneOpacity { get; set; }

		[NinjaScriptProperty]
		[Range(0, 100)]
		[Display(Name = "Window shade opacity %", Order = 6, GroupName = "Display")]
		public int WindowOpacity { get; set; }
		#endregion
	}
}
