"""Split one synthetic 59-pulse v3 detection into fit time and projection (cell) time.

Diagnostic-only process: wraps pf._accepted_region_projection with a timer in
this process to separate counted cells from the uncounted coordinate-descent
fit. Synthetic bytes only.
"""
import json, sys, time
sys.path.insert(0, '.codex-report/l9-2')
from joulewise import powermetrics_fiducial as pf
import projection_bench as b

evidence, raw, events = b.build()
spent = []
original = pf._accepted_region_projection
def timed(**kw):
    budget = kw['work_budget']; before = budget.evaluated_cell_count; t = time.perf_counter()
    try: return original(**kw)
    finally: spent.append((time.perf_counter() - t, budget.evaluated_cell_count - before))
pf._accepted_region_projection = timed
t = time.perf_counter()
d = pf.rederive_detection_from_artifacts(raw, events, evidence['clock_anchor'], protocol_id=pf.PROTOCOL_ID)
total = time.perf_counter() - t
proj = sum(s for s, _ in spent); cells = sum(c for _, c in spent)
print(json.dumps(dict(total_s=round(total, 3), pulses=len(spent), projection_s=round(proj, 3),
    fit_and_other_s=round(total - proj, 3), cells=cells, projection_ms_per_cell=round(1000 * proj / cells, 4),
    fit_s_per_pulse=round((total - proj) / len(spent), 4),
    extrapolated_real_corpus_s={str(n): round(total - proj + n * proj / cells, 1) for n in (112205, 122044, 137189)})))
