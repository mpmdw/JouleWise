# P1 witness replay at e323f1aa5b9d1579f4a93b13b2665388cdeaa643

Source command: `docs/process_traces/2026-09-04-peer-audit/02-claim-spine.md:150-164`.
Re-executed from repository root on 2026-09-04 with exit status 0.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from joulewise.bundle_read import TracePoint, Window
from joulewise.reduce import _integrate, _interpolation_joint_edge_bound_j, _corner_composed_anchor_shift_envelope
from joulewise.analysis_engine.claims import evaluate_claim
curve = [TracePoint(t=i/10, power_w=10.0, support_start_s=(i-1)/10, support_end_s=i/10) for i in range(1, 21)]
w = Window(0.55, 1.45)
env = _corner_composed_anchor_shift_envelope([(curve, [w])], 0.0, 0.01)
print('interval_average_point_J=%.3f interpolation_bound_J=%.3f envelope_J=[%.3f, %.3f]' % (_integrate(curve,w.start_s,w.end_s), _interpolation_joint_edge_bound_j(curve,w),env['lower_j'],env['upper_j']))
print('same_record_totals_true_window_J=[8.000, 10.000]; 20 W/0 W boundary half-intervals suffice')
r = evaluate_claim(estimate=6.0,metrology_aware_ci95={'lower':5.9,'upper':6.1},decision_interval={'lower':1.9,'upper':10.1},floor_gate_j=5.0,adjusted_rejected=True,hypothesized_direction='positive')
print('two_gate_example outcome=%s claim_ready=%s estimate=6 floor=5 deterministic_bound=4 sum=9' % (r['outcome'],r['claim_ready_for_l2_l3']))
PY
```

Complete tail:

```text
interval_average_point_J=9.000 interpolation_bound_J=0.000 envelope_J=[8.800, 9.200]
same_record_totals_true_window_J=[8.000, 10.000]; 20 W/0 W boundary half-intervals suffice
two_gate_example outcome=direction_supported claim_ready=True estimate=6 floor=5 deterministic_bound=4 sum=9
```
