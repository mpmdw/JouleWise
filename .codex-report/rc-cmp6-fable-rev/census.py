"""RC-CMP-4's real-shape step-11 leaf paths (324, from its report) against the COVERAGE rules at HEAD.
A numeric-class leaf (RC-CMP-4 listed these as uncovered_numeric, i.e. numbers) must match a rule that admits numbers."""
import importlib.util, re, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("cmpx", sys.argv[1]); cmp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cmp)
paths = [l.strip() for l in Path(sys.argv[2]).read_text().splitlines() if l.strip()]
unmapped, by_rule = [], {}
for path in paths:
    hit = None
    for rule in cmp.COVERAGE:
        m = re.fullmatch(rule[0], path)
        if m and cmp.admits(rule, 1.0, True, False, False):
            hit = rule; break
    if hit is None:
        unmapped.append(path)
    else:
        by_rule.setdefault(hit[1] if len(hit) == 2 else "BOUND:" + hit[1], []).append(path)
print("paths", len(paths), "unmapped_numeric", len(unmapped))
for p in unmapped: print("  UNMAPPED", p)
for k, v in sorted(by_rule.items()): print(len(v), k[:90])
