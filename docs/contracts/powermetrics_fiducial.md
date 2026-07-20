# Powermetrics Pulse-Fiducial Instrument Calibration (D-078)

Contract for `runs/instrument_validation/<validation_id>/` artifacts and the
`B_fiducial` bound consumed by reducer 0.5.1/0.6.1 as
`B_effective = max(B_bundle, B_fiducial)`.

The ONE home for the estimator and protocol constants is
`joulewise/powermetrics_fiducial.py` plus the frozen protocol file
`configs/calibration/powermetrics_fiducial/protocol_v1.json`; this contract
fixes the artifact layout, binding rules, and fail-closed semantics.

## Protocol (`powermetrics_pulse_fiducial_v1`)

- Workload: preallocated 4096x4096 FP16 MLX matmuls; buffers allocated
  outside every pulse window; `mx.eval` fences each matmul so pulse edges are
  honest. MLX dispatch/fence latency stays IN the bound and is never
  subtracted.
- Shape: 3 warmup pulses, then k = 40 pulses of 1.0 s each; gap after pulse
  j is `1.5 + vanDerCorput_2(j)` s (deterministic low-discrepancy spacing;
  avoids 10 Hz phase lock); >= 5 s baseline before and after the train.
- Events: `pulse_command_on` / `pulse_command_off` with full paired
  `ClockStamps`; their half-widths widen every residual interval.
- Rails: `gpu_power` is the primary rail; CPU+GPU combined is corroboration
  only.
- Gates (all fail closed): plateau >= 10 W over baseline, robust
  SNR >= 10 (1.4826 * MAD), ALL 40 pulses detected, no spurious plateau
  outside the commanded windows, edge coverage across the full fit range.

## Estimator

Fit the interval-average model
`y_i = b + A * |I_i INTERSECT [t_on + d_on, t_off + d_off]| / |I_i|`
with a robust constrained loss (Huber; amplitude pinned to the plateau
median; coordinate descent over the two edge shifts). NEVER timestamp the
first above-threshold interval endpoint - that bakes in up to one cadence of
bias. Per-pulse onset/offset residual intervals are the contiguous
loss-tolerance regions around the fitted shifts, widened by the event-stamp
uncertainty.

`B_fiducial = max over all onset/offset residual intervals of
max(|r_lower|, |r_upper|)`. Median/p95 are recorded as diagnostics only and
never license anything.

## Window license

`T_min = max(4 * B_effective, existing cadence/sample-count requirement)` -
at ~115 ms cadence, request metrics need >= ~460 ms regardless of anchor
quality (`window_license_min_duration_s`).

## Artifact layout

```
runs/instrument_validation/<validation_id>/
  manifest.json              # schema joulewise.instrument_validation_manifest.v1 + sha256s
  events.jsonl               # pulse_command_on/off with full ClockStamps
  raw/powermetrics.plist     # NUL-framed native capture
  power_trace.csv            # anchor-corrected interval-support trace
  instrument_evidence.json   # schema joulewise.instrument_evidence.v1
```

## Binding (hash-referenced)

`instrument_evidence.json` binds: `hardware_model`, `os_build`,
`powermetrics_sha256`, `sampling_interval_ms`, `anchor_method_version`
(`powermetrics_native_second_censored_intersection_v1`), `mlx_version`,
`pulse_protocol_id`, `power_policy`. A missing/empty binding field makes the
artifact `invalid` (fail closed). Production bundles reference the artifact
via
`metadata.instrument_calibration = {artifact_path, artifact_sha256, b_fiducial_s}`;
any bound-field change invalidates the calibration and a new run is
required. `artifact_path` is the bundle-relative location of the copied
`instrument_evidence.json` (absolute paths and parent traversal are
rejected). At reduce time the reducer loads that file, verifies its sha256
equals `artifact_sha256`, and fails closed (`clock_anchor_unresolved`) unless
ALL of: `schema_version` is `joulewise.instrument_evidence.v1`; `protocol_id`
is `powermetrics_pulse_fiducial_v1`; `status` is `valid`;
`anchor_method_version` equals the reducer's own
`powermetrics_native_second_censored_intersection_v1`; the artifact's
`b_fiducial_s` matches the metadata scalar; every binding field is present
and non-empty; and the bundle-supplied environment fields (`hardware_model`
from `device.hw_model`, `os_build` from `device.kern_osversion`) match the
artifact bindings. `B_fiducial` is NEVER trusted from the self-asserted
metadata scalar alone. An invalid or malformed reference is
`clock_anchor_unresolved` at reduce time - never a silent fallback to
`B_bundle` alone.

The v1 protocol's `status = valid` predicate additionally requires ALL
`protocol_pulse_count` pulses detected (default 40): a run with a fitted
bound but fewer than the protocol count, or any undetected pulse, is
`invalid`. A capture whose own clock anchor is unresolved is forced `invalid`
(the harness exits nonzero) - detection may still run against the native
1 s-quantized stamps for diagnostics, but never licenses a bound.

## Execution discipline

Live captures are lead-owned `[QUIET-MAC]` operations
(`scripts/validate_powermetrics_fiducial.py --allow-live --power-policy ...`);
never run while any agent session is active. CI exercises only the pure
estimator via synthetic traces (`tests/test_powermetrics_fiducial.py`).
