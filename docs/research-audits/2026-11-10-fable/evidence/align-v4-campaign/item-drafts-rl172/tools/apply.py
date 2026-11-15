"""Apply exact, each-must-match-once replacements to a copy of an items-rl165 draft. Usage: apply.py SRC DST EDITS.py"""
import sys, runpy
src, dst, edits = sys.argv[1:4]
s = open(src).read()
E = runpy.run_path(edits)["EDITS"]
for i, (old, new) in enumerate(E):
    n = s.count(old)
    if n != 1:
        sys.exit(f"edit {i}: {n} matches for {old[:120]!r}")
    s = s.replace(old, new)
open(dst, "w").write(s)
print(f"{dst}: {len(E)} edits applied")
