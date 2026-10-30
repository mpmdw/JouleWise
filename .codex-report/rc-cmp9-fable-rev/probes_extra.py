"""P1/P3/P4 on the unwidened window (each registered condition false on both sides), and the kept-n condition."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/home/user/JouleWise")
import probes as p  # noqa: E402  (runs the widened probes again on import; their output is above)

print("=" * 8, "EXTRA: the same registered-condition-false windows, unwidened")
c = p.case(False); p.l9_reported_refused(c); p.ours_reported_refused(c)
p.show("X1 unwidened: both sides refuse ALPHA's decode reported cell", c, 3)
c = p.case(False); p.l9_floor_refused(c); p.ours_floor_refused(c)
p.show("X3 unwidened: both sides refuse the decode absolute floor", c, 3)
c = p.case(False); p.l9_ratio_bare(c); p.ours_ratio_none(c)
p.show("X4 unwidened: both sides ratio not computable", c, 3)
print("=" * 8, "EXTRA: P1 with the recompute's reported cell carrying only a status word (no counts)")
c = p.case(); p.l9_reported_refused(c); p.ours_reported_refused(c)
c.ours["reported_cells"][p.FAMILY] = {"status": "below_minimum"}
p.show("X5 widened: recompute reported cell = {status: below_minimum}", c, 3)
