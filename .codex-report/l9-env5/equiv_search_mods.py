"""Search for inputs distinguishing L9-ENV-4 mutants M01 (shifted start), M02 (shifted end),
M03 (<=) from the clamp's midpoint rule.  Usage: equiv_search.py ROOT TRIALS SEED"""
import json, random, sys, types
from pathlib import Path
ROOT = Path("/home/user/JouleWise"); sys.path.insert(0, str(ROOT))
from joulewise.bundle_read import TracePoint, Window
import joulewise.whole_window as W
SRC = (ROOT / "joulewise/whole_window.py").read_text()
MID = ("                    Window(\n                        start_s=(window.start_s + window.end_s) / 2.0,\n"
       "                        end_s=(window.start_s + window.end_s) / 2.0,\n                    )")
MUT = {
 "M01_start": [(MID, "                    Window(\n                        start_s=window.start_s,\n                        end_s=window.start_s,\n                    )")],
 "M02_end": [(MID, "                    Window(\n                        start_s=window.end_s,\n                        end_s=window.end_s,\n                    )")],
 "M03_le": [("                    if window.end_s < window.start_s\n                    else window",
             "                    if window.end_s <= window.start_s\n                    else window")],
}
mods = {}
for name, pairs in MUT.items():
    src = SRC
    for o, n in pairs:
        assert src.count(o) == 1, name
        src = src.replace(o, n)
    m = types.ModuleType(name); m.__file__ = str(ROOT / "joulewise/whole_window.py")
    sys.modules[name] = m; exec(compile(src, name, "exec"), m.__dict__); mods[name] = m
