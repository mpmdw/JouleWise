# P2 witness replay at e323f1aa5b9d1579f4a93b13b2665388cdeaa643

Source command: `docs/process_traces/2026-09-04-peer-audit/02-claim-spine.md:175-190`.
Re-executed from repository root on 2026-09-04 with exit status 0.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from joulewise.dominance_closeout import replay_common_mode_dominance
from joulewise.detection_floor import comparative_false_effect_floor
bracket={'status':'passed','endpoint_max_b_fiducial_s':0.04,'calibration_drift_allowance_s':0.01,'b_fiducial_s':0.05,'acceptance':{'allowance':{'rule':'max(observed_drift_s,bracket_screen_s)','value_s':'0.01','embedding_count':1,'embedded_in':'b_fiducial_s'}}}
deltas=[1.0]*10
signed_slopes=[0.5,-0.5]*5
blocks=[{'delta_j':d,'onset_sweep_j':[d-s,d,d+s],'offset_sweep_j':[d],'zero_point_contrast_j':d,'bundle_residual_half_widths_j':[0.0]*4,'member_window_bounds_s':[[1.0,2.0]]*4,'member_envelope_integral_sum_j':100.0} for d,s in zip(deltas,signed_slopes)]
r=replay_common_mode_dominance(blocks,calibration_bracket=bracket,shared_edge_bound_s=0.05)
physical=max(comparative_false_effect_floor([d+q*s for d,s in zip(deltas,signed_slopes)],admissible_half_widths_j=[0.0]*10).unguarded_floor_j for q in [-1.0,1.0])
print('synthetic_common_time_shift_ratio=%.6f passes=%s' % (physical,physical>=2))
print('issued_shared_energy_sign_ratio=%.6f passes=%s' % (r['ratio'],r['passes']))
print('same shared time shift; opposite block edge sensitivities; all scalar replay preconditions pass')
PY
```

Complete tail:

```text
synthetic_common_time_shift_ratio=2.250368 passes=True
issued_shared_energy_sign_ratio=1.500000 passes=False
same shared time shift; opposite block edge sensitivities; all scalar replay preconditions pass
```
