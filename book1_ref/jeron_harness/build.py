"""Rebuild JeronHarness.exe from the NinjaTrader sources (JH 0.1, Oct 25 2026).
1. copies the three NT files from nt_source/ (or from --nt <NinjaTrader 8\\bin\\Custom>), strips the
   '#region NinjaScript generated code' block and adds the JeronContextBias enum (it lives in the tracker file);
2. compiles them with the NinjaTrader stand-ins in stubs/ and the driver.
Linux: mono-devel 'mcs'. Windows: csc.exe from .NET Framework 4.x (C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe)
or any mcs. The strategy and map code are NOT edited: the harness runs the same C# NinjaTrader compiles."""
import argparse, os, re, shutil, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument("--nt", default=""); ap.add_argument("--compiler", default="")
a = ap.parse_args()
srcs = {"JeronOrderFlowStrategy.cs": "Strategies", "JeronFlowShared.cs": "Indicators", "JeronPreopenMap.cs": "Indicators"}
pp = H / "pp"; pp.mkdir(exist_ok=True)
for f, sub in srcs.items():
    src = Path(a.nt) / sub / f if a.nt else H / "nt_source" / f
    if a.nt: shutil.copy2(src, H / "nt_source" / f)
    text = src.read_text(encoding="utf-8-sig")
    text = re.sub(r"#region NinjaScript generated code.*?#endregion", "", text, flags=re.S)
    (pp / f).write_text(text, encoding="utf-8")
(pp / "JeronContextBias.cs").write_text("namespace NinjaTrader.NinjaScript.Indicators.JeronShared\n{\n\tpublic enum JeronContextBias { None, Bullish, Bearish, Balanced }\n}\n")
comp = a.compiler or shutil.which("mcs") or r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
files = sorted(map(str, (H / "stubs").glob("*.cs"))) + sorted(map(str, pp.glob("*.cs"))) + [str(H / "driver" / "Harness.cs")]
refs = ["-r:System.ComponentModel.DataAnnotations.dll", "-r:Microsoft.CSharp.dll", "-r:System.IO.Compression.dll", "-r:System.Core.dll"]
cmd = [comp] + (["-langversion:7"] if "mcs" in comp else []) + ["-out:" + str(H / "build" / "JeronHarness.exe")] + refs + files
p = subprocess.run(cmd, capture_output=True, text=True); print(p.stdout[-4000:], p.stderr[-2000:]); sys.exit(p.returncode)
