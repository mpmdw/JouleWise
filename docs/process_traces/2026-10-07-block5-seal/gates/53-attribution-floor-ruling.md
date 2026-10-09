# Orchestrator's ruling on registration section 14 Q5, the attribution floor (2026-10-07 22:05 PDT)

Inputs: `REPORT.md` (investigator, Opus 5.5) and `REFUTATION.json` (refuter, Fable 5.1: HOLDS WITH CORRECTIONS; every
number in the report reproduced from raw bytes by scripts under `refuter/`).

**Ruling: register the formula and bind no number.** The attribution floor of a reported cell is the largest, over
the cell's kept members, of the per-member bound the frozen reducer already computes: the largest change in the
phase's assigned energy when each phase edge is displaced by the edge bound (fiducial bound plus the member's
wall-minus-monotonic span) at its four corners and the whole trace is shifted within the member clock bound (the
stored `max_abs_delta_j` of method `common_trace_shift_plus_independent_edge_corners_v3`), each member's bound taken
from its summary re-derived under the window's operative fiducial bound. It is computed at the analysis from the
window's own members and bracket. D-078's "about 1 J" is recorded as the lineage of the quantity: it was one
member's value on window a10 (macOS 25F84, fiducial bound 24.879 ms, Qwen2.5-1.5B), 0.031073829 s x 32.697 W.

Why: the number is not a constant of the instrument; every input changed for block 5 (on released 25G83 data the same
bound is 1.38 to 2.86 J per member); nothing in block 5 is decided by the number (it is printed beside four cells);
and binding a stale value would print a floor the instrument does not have.

Corrections the final registration pass must carry (from the refuter):
1. The registered quantity is the exact maximum over the four edge corners and the common shift. The first-order
   form g x (P_on + P_off) + m x |P_off - P_on| may appear only as an approximation, with its condition (the
   displaced edges stay inside the two records straddling the recorded edges); on recomputed rows it was off by
   -63% to +20%.
2. Do not write that the record at a decode start "holds mostly idle power" (measured 9 to 24 W).
3. The analysis plan's sentence that a reported cell's interval "does not include" this bound is false as written:
   the average of the same per-member bound is already inside the cell's bound B. Correct it.
4. If an upper limit of the operative fiducial bound is stated, give it as 67.47 ms under the rules as written, and
   say that 50.99 or 51.97 ms would apply only if a capture outside the observed range is refused, which is
   unverified.
5. For lane L9 (not for the seal): `_project_cell` requires exactly 50 rows and the fixed df-9 quantile, so the
   kept-units arithmetic of plan section 4 needs the kept-units kernel; the issuer prints the floor as the computed
   maximum and refuses a binding that differs from it.

The facts for the text are F1 to F17 of `REPORT.md` with these corrections. No artifact, no number and no code that
runs during collection is needed. The marker `FILL[ATTRIBUTION-FLOOR-BINDING]` is filled by this formula.
