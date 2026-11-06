// Chart, drawing, WPF and SharpDX no-ops. The harness has no chart: every draw call returns an inert object.
using System;
using System.Collections.Generic;

namespace System.Windows.Media
{
	public class Color { public byte A, R, G, B; public static Color FromArgb(byte a, byte r, byte g, byte b) { return new Color { A = a, R = r, G = g, B = b }; } public static Color FromRgb(byte r, byte g, byte b) { return FromArgb(255, r, g, b); } }
	public class Brush { public double Opacity = 1; public SharpDX.Direct2D1.Brush ToDxBrush(object rt) { return new SharpDX.Direct2D1.Brush(); } public Brush Clone() { return new Brush(); } public void Freeze() { } public bool IsFrozen { get { return true; } } public Brush CloneCurrentValue() { return this; } }
	public class SolidColorBrush : Brush { public Color Color; public SolidColorBrush() { } public SolidColorBrush(Color c) { Color = c; } }
	public static class Brushes
	{
		static readonly Brush b = new SolidColorBrush();
		public static Brush Transparent { get { return b; } }
		public static Brush Black { get { return b; } } public static Brush White { get { return b; } } public static Brush Gray { get { return b; } }
		public static Brush DimGray { get { return b; } } public static Brush DarkGray { get { return b; } } public static Brush LightGray { get { return b; } } public static Brush Silver { get { return b; } }
		public static Brush Gainsboro { get { return b; } } public static Brush WhiteSmoke { get { return b; } } public static Brush SlateGray { get { return b; } }
		public static Brush Red { get { return b; } } public static Brush DarkRed { get { return b; } } public static Brush IndianRed { get { return b; } } public static Brush Crimson { get { return b; } } public static Brush Firebrick { get { return b; } } public static Brush Tomato { get { return b; } } public static Brush Salmon { get { return b; } } public static Brush LightCoral { get { return b; } } public static Brush OrangeRed { get { return b; } } public static Brush Maroon { get { return b; } }
		public static Brush Green { get { return b; } } public static Brush DarkGreen { get { return b; } } public static Brush LimeGreen { get { return b; } } public static Brush Lime { get { return b; } } public static Brush SeaGreen { get { return b; } } public static Brush MediumSeaGreen { get { return b; } } public static Brush ForestGreen { get { return b; } } public static Brush LightGreen { get { return b; } } public static Brush PaleGreen { get { return b; } } public static Brush SpringGreen { get { return b; } } public static Brush MediumSpringGreen { get { return b; } } public static Brush Teal { get { return b; } } public static Brush DarkSeaGreen { get { return b; } } public static Brush Chartreuse { get { return b; } } public static Brush LawnGreen { get { return b; } } public static Brush YellowGreen { get { return b; } }
		public static Brush Blue { get { return b; } } public static Brush DodgerBlue { get { return b; } } public static Brush RoyalBlue { get { return b; } } public static Brush SteelBlue { get { return b; } } public static Brush DeepSkyBlue { get { return b; } } public static Brush CornflowerBlue { get { return b; } } public static Brush LightBlue { get { return b; } } public static Brush SkyBlue { get { return b; } } public static Brush LightSkyBlue { get { return b; } } public static Brush Navy { get { return b; } } public static Brush MidnightBlue { get { return b; } } public static Brush DarkBlue { get { return b; } } public static Brush CadetBlue { get { return b; } } public static Brush SlateBlue { get { return b; } } public static Brush MediumBlue { get { return b; } } public static Brush LightSteelBlue { get { return b; } } public static Brush PowderBlue { get { return b; } }
		public static Brush Cyan { get { return b; } } public static Brush Aqua { get { return b; } } public static Brush Turquoise { get { return b; } } public static Brush DarkCyan { get { return b; } } public static Brush DarkTurquoise { get { return b; } } public static Brush MediumTurquoise { get { return b; } } public static Brush Aquamarine { get { return b; } }
		public static Brush Yellow { get { return b; } } public static Brush Gold { get { return b; } } public static Brush Goldenrod { get { return b; } } public static Brush DarkGoldenrod { get { return b; } } public static Brush Khaki { get { return b; } } public static Brush DarkKhaki { get { return b; } } public static Brush LightYellow { get { return b; } } public static Brush Moccasin { get { return b; } } public static Brush Wheat { get { return b; } } public static Brush Beige { get { return b; } } public static Brush Ivory { get { return b; } }
		public static Brush Orange { get { return b; } } public static Brush DarkOrange { get { return b; } } public static Brush Coral { get { return b; } } public static Brush Peru { get { return b; } } public static Brush Chocolate { get { return b; } } public static Brush SandyBrown { get { return b; } } public static Brush Tan { get { return b; } } public static Brush BurlyWood { get { return b; } } public static Brush Sienna { get { return b; } } public static Brush SaddleBrown { get { return b; } } public static Brush Brown { get { return b; } }
		public static Brush Magenta { get { return b; } } public static Brush Fuchsia { get { return b; } } public static Brush Purple { get { return b; } } public static Brush Violet { get { return b; } } public static Brush Orchid { get { return b; } } public static Brush MediumOrchid { get { return b; } } public static Brush MediumPurple { get { return b; } } public static Brush DarkViolet { get { return b; } } public static Brush DarkOrchid { get { return b; } } public static Brush DarkMagenta { get { return b; } } public static Brush Plum { get { return b; } } public static Brush Thistle { get { return b; } } public static Brush Lavender { get { return b; } } public static Brush HotPink { get { return b; } } public static Brush DeepPink { get { return b; } } public static Brush Pink { get { return b; } } public static Brush LightPink { get { return b; } } public static Brush MediumVioletRed { get { return b; } } public static Brush PaleVioletRed { get { return b; } } public static Brush Indigo { get { return b; } } public static Brush BlueViolet { get { return b; } } public static Brush MediumSlateBlue { get { return b; } } public static Brush DarkSlateBlue { get { return b; } } public static Brush DarkSlateGray { get { return b; } } public static Brush DarkOliveGreen { get { return b; } } public static Brush Olive { get { return b; } } public static Brush OliveDrab { get { return b; } } public static Brush RosyBrown { get { return b; } } public static Brush MistyRose { get { return b; } } public static Brush AntiqueWhite { get { return b; } } public static Brush Linen { get { return b; } } public static Brush Snow { get { return b; } } public static Brush GhostWhite { get { return b; } } public static Brush FloralWhite { get { return b; } } public static Brush LightSlateGray { get { return b; } } public static Brush LightCyan { get { return b; } } public static Brush LemonChiffon { get { return b; } } public static Brush PeachPuff { get { return b; } } public static Brush NavajoWhite { get { return b; } } public static Brush PapayaWhip { get { return b; } } public static Brush BlanchedAlmond { get { return b; } } public static Brush Bisque { get { return b; } } public static Brush LightSalmon { get { return b; } } public static Brush DarkSalmon { get { return b; } } public static Brush LightSeaGreen { get { return b; } } public static Brush MediumAquamarine { get { return b; } }
	}
	public enum DashStyles { }
}
namespace System.Windows
{
	public enum TextAlignment { Left, Right, Center, Justify }
	public enum HorizontalAlignment { Left, Center, Right, Stretch }
	public enum VerticalAlignment { Top, Center, Bottom, Stretch }
	public struct Point { public double X, Y; public Point(double x, double y) { X = x; Y = y; } }
	public struct Thickness { public double Left, Top, Right, Bottom; public Thickness(double u) { Left = Top = Right = Bottom = u; } }
	public enum Visibility { Visible, Hidden, Collapsed }
}

namespace SharpDX
{
	public struct Vector2 { public float X, Y; public Vector2(float x, float y) { X = x; Y = y; } }
	public struct RectangleF { public float X, Y, Width, Height; public RectangleF(float x, float y, float w, float h) { X = x; Y = y; Width = w; Height = h; }
		public float Left { get { return X; } } public float Top { get { return Y; } } public float Right { get { return X + Width; } } public float Bottom { get { return Y + Height; } } }
	public struct Color4 { public Color4(float r, float g, float b, float a) { } }
	public struct Color { }
	namespace Direct2D1
	{
		public class DxObj : IDisposable { public DxObj(params object[] a) { } public void Dispose() { } public bool IsDisposed { get { return false; } } }
		public class Brush : DxObj { public float Opacity; public Brush(params object[] a) { } }
		public class SolidColorBrush : Brush { public SolidColorBrush(params object[] a) { } }
		public class RenderTarget { }
		public enum AntialiasMode { Aliased, PerPrimitive }
		public enum FigureBegin { Filled, Hollow }
		public enum FigureEnd { Open, Closed }
		public class StrokeStyle : DxObj { public StrokeStyle(params object[] a) { } }
		public class GeometrySink : DxObj { public void BeginFigure(Vector2 p, FigureBegin b) { } public void AddLine(Vector2 p) { } public void AddLines(Vector2[] p) { } public void EndFigure(FigureEnd e) { } public void Close() { } }
		public class PathGeometry : DxObj { public PathGeometry(params object[] a) { } public GeometrySink Open() { return new GeometrySink(); } }
	}
	namespace DirectWrite
	{
		public enum FontWeight { Normal, Bold, SemiBold, Light }
		public enum FontStyle { Normal, Italic, Oblique }
		public enum TextAlignment { Leading, Trailing, Center, Justified }
		public enum ParagraphAlignment { Near, Far, Center }
		public enum WordWrapping { Wrap, NoWrap }
		public class TextFormat : IDisposable { public TextFormat(params object[] a) { } public void Dispose() { } public TextAlignment TextAlignment; public ParagraphAlignment ParagraphAlignment; public WordWrapping WordWrapping; }
		public struct TextMetrics { public float Width, Height; }
		public class TextLayout : IDisposable { public TextLayout(params object[] a) { } public void Dispose() { } public float MaxWidth; public float MaxHeight; public TextMetrics Metrics; }
		public class Factory { }
	}
}

namespace NinjaTrader.Gui
{
	public class Stroke { public object Brush; public float Width; public Stroke() { } public Stroke(object brush, float width) { Brush = brush; Width = width; } public Stroke(object brush, NinjaTrader.Gui.DashStyleHelper d, float width) { Brush = brush; Width = width; } }
	public enum DashStyleHelper { Dash, DashDot, DashDotDot, Dot, Solid }
	public class NinjaScriptPropertyAttribute : Attribute { }
	public class PropertyEditorAttribute : Attribute { public PropertyEditorAttribute(string s) { } public PropertyEditorAttribute(string s, string t) { } }
	public static class Serialize
	{
		public static string BrushToString(System.Windows.Media.Brush b) { return "#FF000000"; }
		public static System.Windows.Media.Brush StringToBrush(string s) { return new System.Windows.Media.SolidColorBrush(); }
	}
}
namespace NinjaTrader.Gui.Tools
{
	public class SimpleFont
	{
		public string Family; public double Size; public bool Bold;
		public SimpleFont() { } public SimpleFont(string family, double size) { Family = family; Size = size; }
		public SharpDX.DirectWrite.TextFormat ToDirectWriteTextFormat() { return new SharpDX.DirectWrite.TextFormat(); }
	}
}
namespace NinjaTrader.Gui.Chart
{
	public class ChartControl { public object Properties; public int GetXByBarIndex(object cb, int i) { return 0; } public int GetSlotIndexByTime(DateTime t) { return 0; } }
	public class ChartScale { public int GetYByValue(double v) { return 0; } public double MaxValue, MinValue; }
	public class ChartPanel { public int X, Y, W, H; }
	public class ChartBars { public int FromIndex, ToIndex; }
}

namespace NinjaTrader.NinjaScript.DrawingTools
{
	public class DrawingTool { public bool IsLocked; public string Tag; public object Brush; }
	public class Text : DrawingTool { public string DisplayText; }
	public class TextFixed : DrawingTool { public string DisplayText; }
	public class Line : DrawingTool { }
	public class HorizontalLine : DrawingTool { }
	public class Rectangle : DrawingTool { }
	public class ArrowUp : DrawingTool { }
	public class ArrowDown : DrawingTool { }
	public class Dot : DrawingTool { }
	public class Diamond : DrawingTool { }
	public class Square : DrawingTool { }
	public class TriangleUp : DrawingTool { }
	public class TriangleDown : DrawingTool { }
	public class Ray : DrawingTool { }
	public enum TextPosition { BottomLeft, BottomRight, Center, TopLeft, TopRight }

	/// <summary>Every Draw.* overload the scripts call returns an inert object.</summary>
	public static class Draw
	{
		public static Text Text(object o, string tag, string text, int barsAgo, double y) { return new Text { Tag = tag, DisplayText = text }; }
		public static Text Text(object o, string tag, string text, int barsAgo, double y, object brush) { return new Text { Tag = tag, DisplayText = text }; }
		public static Text Text(object o, string tag, bool isAutoScale, string text, int barsAgo, double y, int yPixelOffset, object textBrush, NinjaTrader.Gui.Tools.SimpleFont font, System.Windows.TextAlignment alignment, object outlineBrush, object areaBrush, int areaOpacity) { return new Text { Tag = tag, DisplayText = text }; }
		public static Text Text(object o, string tag, bool isAutoScale, string text, DateTime time, double y, int yPixelOffset, object textBrush, NinjaTrader.Gui.Tools.SimpleFont font, System.Windows.TextAlignment alignment, object outlineBrush, object areaBrush, int areaOpacity) { return new Text { Tag = tag, DisplayText = text }; }
		public static TextFixed TextFixed(object o, string tag, string text, TextPosition pos) { return new TextFixed { Tag = tag, DisplayText = text }; }
		public static TextFixed TextFixed(object o, string tag, string text, TextPosition pos, object textBrush, NinjaTrader.Gui.Tools.SimpleFont font, object outlineBrush, object areaBrush, int areaOpacity) { return new TextFixed { Tag = tag, DisplayText = text }; }
		public static Line Line(object o, string tag, bool isAutoScale, DateTime t1, double y1, DateTime t2, double y2, object brush, NinjaTrader.Gui.DashStyleHelper dash, int width) { return new Line { Tag = tag }; }
		public static Line Line(object o, string tag, bool isAutoScale, int ba1, double y1, int ba2, double y2, object brush, NinjaTrader.Gui.DashStyleHelper dash, int width) { return new Line { Tag = tag }; }
		public static Line Line(object o, string tag, int ba1, double y1, int ba2, double y2, object brush) { return new Line { Tag = tag }; }
		public static HorizontalLine HorizontalLine(object o, string tag, double y, object brush) { return new HorizontalLine { Tag = tag }; }
		public static Rectangle Rectangle(object o, string tag, bool isAutoScale, DateTime t1, double y1, DateTime t2, double y2, object brush, object areaBrush, int opacity) { return new Rectangle { Tag = tag }; }
		public static Rectangle Rectangle(object o, string tag, bool isAutoScale, int ba1, double y1, int ba2, double y2, object brush, object areaBrush, int opacity) { return new Rectangle { Tag = tag }; }
		public static ArrowUp ArrowUp(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new ArrowUp { Tag = tag }; }
		public static ArrowUp ArrowUp(object o, string tag, bool isAutoScale, DateTime t, double y, object brush) { return new ArrowUp { Tag = tag }; }
		public static ArrowDown ArrowDown(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new ArrowDown { Tag = tag }; }
		public static ArrowDown ArrowDown(object o, string tag, bool isAutoScale, DateTime t, double y, object brush) { return new ArrowDown { Tag = tag }; }
		public static Dot Dot(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new Dot { Tag = tag }; }
		public static Diamond Diamond(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new Diamond { Tag = tag }; }
		public static Square Square(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new Square { Tag = tag }; }
		public static TriangleUp TriangleUp(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new TriangleUp { Tag = tag }; }
		public static TriangleDown TriangleDown(object o, string tag, bool isAutoScale, int barsAgo, double y, object brush) { return new TriangleDown { Tag = tag }; }
	}
}

namespace NinjaTrader.NinjaScript.BarsTypes
{
	/// <summary>Volumetric (BidAsk) bar data: ask (buy aggressor) and bid (sell aggressor) volume per price for one bar.</summary>
	public class VolumetricData
	{
		public readonly System.Collections.Generic.Dictionary<long, long> Ask = new System.Collections.Generic.Dictionary<long, long>(), Bid = new System.Collections.Generic.Dictionary<long, long>();
		public double TickSize = 0.25;
		public long TotalBuyingVolume, TotalSellingVolume;
		public long BarDelta { get { return TotalBuyingVolume - TotalSellingVolume; } }
		long Key(double p) { return (long)System.Math.Round(p / TickSize); }
		public long GetAskVolumeForPrice(double p) { long v; return Ask.TryGetValue(Key(p), out v) ? v : 0; }
		public long GetBidVolumeForPrice(double p) { long v; return Bid.TryGetValue(Key(p), out v) ? v : 0; }
		public void Add(double p, long size, bool buy)
		{
			var d = buy ? Ask : Bid; long v; d.TryGetValue(Key(p), out v); d[Key(p)] = v + size;
			if (buy) TotalBuyingVolume += size; else TotalSellingVolume += size;
		}
	}
	public class VolumetricBarsType { public System.Collections.Generic.List<VolumetricData> Volumes = new System.Collections.Generic.List<VolumetricData>(); }
	public enum VolumetricDeltaType { BidAsk, UpDownTick }
}

namespace NinjaTrader.Harness
{
	public static class HarnessOut { public static bool PrintEnabled = false; }
}
