# Powermetrics Pulse-Fiducial Instrument Calibration (D-078)

Contract for `runs/instrument_validation/<validation_id>/` artifacts and the
`B_fiducial` bound consumed by reducer 0.5.1/0.6.1 under their frozen replay
rule `B_effective = max(B_bundle, B_fiducial)`. Reducer 0.5.2/0.6.2 replaces
that under-composed mint rule with
`B_effective = B_bundle + B_fiducial + wall_minus_monotonic_span`: the
bundle-local censored anchor interval, calibrated instrument emission lag,
and wall/monotonic clock-span discrepancy constrain distinct causal links, so
none is proven to contain another. The full composed bound drives both the
continuous anchor-shift scan and every timing license.

The ONE home for the estimator and protocol constants is
`joulewise/powermetrics_fiducial.py` plus the executable protocol file
`configs/calibration/powermetrics_fiducial/protocol_v3.json`. Protocol v3 is
required for every future claim-bearing calibration collection. The v1 and
v2 protocol files are byte-frozen historical identities; authenticated v2
artifacts remain verifiable as the current D-078 arc's validation evidence,
but v2 must not mint a new claim-bearing calibration capture.

## Required protocol (`powermetrics_pulse_fiducial_v3`)

- Workload: preallocated 4096x4096 FP16 MLX matmuls; buffers allocated
  outside every pulse window; `mx.eval` fences each matmul so pulse edges are
  honest. MLX dispatch/fence latency stays IN the bound and is never
  subtracted.
- Shape: 3 warmup pulses, then k = 59 pulses of 1.0 s each; gap after pulse
  j is `1.5 + vanDerCorput_2(j)` s (deterministic low-discrepancy spacing;
  avoids 10 Hz phase lock); >= 5 s baseline before and after the train.
- Events: `pulse_command_on` / `pulse_command_off` with full paired
  `ClockStamps`; their half-widths widen every residual interval.
- Rails: `gpu_power` is the primary rail; CPU+GPU combined is corroboration
  only.
- Gates (all fail closed): plateau >= 10 W over baseline, robust
  SNR >= 10 (1.4826 * MAD), ALL 59 pulses detected, no spurious plateau
  outside the commanded windows, edge coverage across the full fit range.

## Estimator

The current v2 estimator fits the interval-average model
`y_i = b + A * |I_i INTERSECT [t_on + d_on, t_off + d_off]| / |I_i|`
with a robust constrained loss (Huber; amplitude pinned to the plateau
median). Estimator revision `joint_loss_sublevel_interval_branch_v2` uses
analytic interval branch-and-bound over the full accepted two-dimensional
loss region: overlap monotonicity supplies a rigorous loss lower bound for
each rectangle; a rectangle is discarded only when that lower bound exceeds
the acceptance threshold; retained rectangles are bisected to at most
0.1 ms on both axes and their full extents are included. This dominates all
points between resolution cells and therefore proves deterministic coverage
of the complete accepted region. The older v1 estimator scanned the two
coordinate slices plus common- and opposite-shift diagonals; that scan
geometry describes historical v1 artifacts only and is not a coverage claim
for the current estimator. NEVER timestamp the first above-threshold interval
endpoint - that bakes in up to one cadence of bias. Per-pulse onset/offset
residual intervals are the contiguous loss-tolerance regions around the
fitted shifts, widened by the event-stamp uncertainty.

`B_fiducial = max over all onset/offset residual intervals of
max(|r_lower|, |r_upper|)`. This finite-sample maximum is a
nonparametric 95/95 calibration bound on the calibration distribution: with n = 59,
`1 - 0.95^59 >= 0.95`. It is not an unconditional deterministic bound for an
unseen operating distribution. Median/p95 are diagnostics only and never
license anything.

The calibration capture's own freshly derived
`effective_clock_anchor_bound_s` is added to that residual maximum. This is
the conservative causal composition (not the anchor half-width alone), so the
new physical bound is monotone and cannot be smaller than the former
event-stamp/fit-only bound.

## Registered transfer assumptions (T1-T3)

The 95/95 bound is deterministic for a claim only conditional on all three
registered transfer assumptions. A report must retain these as limitations;
none may be restated as an empirically proved universal instrument property.

- **T1 — binding-vector stationarity.** Calibration and measured collection
  use the same hardware, OS build, powermetrics binary, MLX version, sampling
  policy, anchor method, pulse protocol, and power policy. Exact hashes and
  field comparisons enforce the recorded vector; they do not prove stability
  of unobserved factors.
- **T2 — authenticated 24-hour transfer horizon.** The calibration capture
  time is authenticated from hash-verified event bytes and every licensed
  endpoint lies inside the governed 24-hour horizon. Host-time integrity and
  artifact custody remain operator assumptions.
- **T3 — load-regime transfer.** Calibration pulses are GPU matmuls under a
  CPU-light load. Transfer to sustained mixed CPU+GPU+ANE load is an
  assumption, not evidence produced by this protocol. The registered roadmap
  mitigation is a loaded-calibration protocol variant that exercises the
  sustained mixed-load regime; until that variant is validated, T3 remains an
  explicit limitation.

## V2/v3 capture-time freshness and authentication

Every v2/v3 `instrument_evidence.json` records
`capture_wall_time_s` and `max_age_s = 86400`. `capture_wall_time_s` must agree
within +/-1 s with the minimum timestamp re-derived from the complete,
hash-verified calibration `events.jsonl`; changing the declaration and
rehashing the summary artifact cannot move the authenticated event time.

Freshness binds both endpoints of a measured collection, never just a single
start marker. For a pre-calibration artifact, the unique `run_started` event
must be at or after the authenticated capture and the measured-window end
must be at or before `capture_wall_time_s + 86400`. Claim-bearing
whole-window collections additionally require a post-calibration artifact at
or after the measured-window end and no more than 86400 s from the collection
start. Horizon-shaped failures use `instrument_calibration_stale`.

## Claim-bearing calibration bracket

A claim-bearing collection requires two independently authenticated,
T1-matching artifacts: pre at-or-before the collection-window start and post
at-or-after its end. Both must satisfy their endpoint horizons above. The
claim consumes `B_fiducial = max(B_pre, B_post)`. It refuses
`instrument_calibration_bracket_missing` when either causal endpoint is
absent, reuses `instrument_calibration_stale` for a horizon failure, and
refuses as `instrument_calibration_mismatch` when
`abs(B_pre - B_post)` exceeds the registered
`calibration_bracket_max_drift_s` (production: 0.010 s). A single valid
calibration remains usable only for explicitly non-claim-bearing probe or
exploratory reduction.

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
`metadata.instrument_calibration = {artifact_path, artifact_sha256,
validation_manifest_path, validation_manifest_sha256, b_fiducial_s,
bindings, binding_observations}`. `bindings` repeats the complete eight-field
artifact vector (`hardware_model`, `os_build`, `powermetrics_sha256`,
`sampling_interval_ms`, `anchor_method_version`, `mlx_version`,
`pulse_protocol_id`, `power_policy`); `binding_observations` records the
runtime-observed powermetrics executable digest and the canonical power-policy
classification derived from the live campaign environment snapshot. A CLI or
config power-policy label is not an observation: the currently supported
`ac_high_power` classification requires observed AC power, an external power
connection, and low-power mode off; missing or contradictory live fields make
the binding unverifiable and refuse attachment. The referenced validation directory's `events.jsonl` and
`raw/powermetrics.plist` bytes are copied with the evidence artifact and their
hashes are reverified during reduction;
any bound-field change invalidates the calibration and a new run is
required. `artifact_path` is the bundle-relative location of the copied
`instrument_evidence.json` (absolute paths and parent traversal are
rejected). At reduce time the reducer loads that file, verifies its sha256
equals `artifact_sha256`, and fails closed (`clock_anchor_unresolved`) unless
ALL of: `schema_version` is `joulewise.instrument_evidence.v1`; under the
frozen historical replay arms only, `protocol_id` is
`powermetrics_pulse_fiducial_v1` or `powermetrics_pulse_fiducial_v2` (v2 is
pinned to the frozen replay sha; the current strict path accepts authenticated
v2 validation evidence from this arc and requires v3 for future claim-bearing
calibration collections, as specified below); `status` is `valid`;
`anchor_method_version` is a registered stored anchor method and equals the
measuring bundle's recorded anchor method; the artifact's
`b_fiducial_s` matches the metadata scalar; every binding field is present
and non-empty; and the bundle-supplied environment fields (`hardware_model`
from `device.hw_model`, `os_build` from `device.kern_osversion`) match the
artifact bindings. `B_fiducial` is NEVER trusted from the self-asserted
metadata scalar alone. An invalid or malformed reference is
`clock_anchor_unresolved` at reduce time - never a silent fallback to
`B_bundle` alone.

Hash verification is not by itself calibration verification. Reducer
consumption re-parses the hash-verified raw plist, re-derives its
stored-method trace
anchor from the recorded ClockStamps, reconstructs all warmup and protocol
pulses from the hash-verified event ledger, and re-runs the shared fiducial
detector. Pulse count, detected flags, spurious-plateau count, and containment
of each freshly fitted edge by its declared per-pulse residual enclosure must
agree structurally. A newly wider coverage revision does not invalidate an
older self-consistent enclosure merely because its width grows. The effective
consumed calibration bound is `max(B_declared, B_freshly_rederived)`; a
conservatively wider declaration remains valid, while a declaration can never
shrink physics re-derived from primary bytes. Unknown diagnostic spellings or
any non-empty reason list on `status = valid` are invalid evidence and reduce
only to `instrument_calibration_invalid`.

The live harness loads
`configs/calibration/powermetrics_fiducial/protocol_v3.json` before calibration
and field-compares the complete JSON object with the executable module pins
(`protocol_v1.json` and `protocol_v2.json` stay byte-frozen historical
identities and are not loaded for new live execution). A missing, incomplete,
or tampered protocol file
refuses the run before any live capture. The JSON's estimator revision records
the v2 coverage and trace-anchor-widening rules above.

Every protocol's `status = valid` predicate additionally requires ALL
protocol-specific pulses detected (40 for v1/v2, 59 for v3): a run with a fitted
bound but fewer than the protocol count, or any undetected pulse, is
`invalid`. A capture whose own clock anchor is unresolved is forced `invalid`
(the harness exits nonzero) - detection may still run against the native
1 s-quantized stamps for diagnostics, but never licenses a bound.

## Execution discipline

Live captures are lead-owned `[QUIET-MAC]` operations
(`scripts/validate_powermetrics_fiducial.py --allow-live --power-policy ...`);
never run while any agent session is active. CI exercises only the pure
estimator via synthetic traces (`tests/test_powermetrics_fiducial.py`).

## Protocol identities and historical validation backstops

`powermetrics_pulse_fiducial_v1` remains byte-frozen at
`configs/calibration/powermetrics_fiducial/protocol_v1.json`; its identity
continues to describe the original directional-region estimator and the
fit/event residual-only stored scalar. The historical re-derivation path uses
`powermetrics_pulse_fiducial_v2`, bound to byte-frozen
`configs/calibration/powermetrics_fiducial/protocol_v2.json`. V2 fixes the
estimator as `joint_loss_sublevel_interval_branch_v2`, adds the capture's own
effective trace-anchor bound to the residual maximum, and requires complete
deterministic branch-and-bound coverage of the accepted two-edge loss region.

V2 and v3 extend the binding vector with `estimator_revision` and
`protocol_sha256`; those fields are absent only from sealed v1. Current
strict-physics reduction accepts authenticated v2 validation artifacts from
this D-078 arc and v3 artifacts. New claim-bearing calibration capture
requires v3; v1 is usable only under frozen historical replay. A body
relabeled across protocol identities is invalid. Re-deriving eligible
40-pulse historical primary bytes may mint only v2 validation evidence; it
cannot manufacture the additional 19 observations required by v3.

The live harness loads protocol v3. Its `--rederive-from ... --output ...`
mode performs no live capture: it verifies the source manifest and primary
hashes, reruns the current estimator over the same bytes, and emits v2
validation evidence for a compatible 40-pulse source. It refuses any hash
mismatch and never promotes 40 observations to v3.

Before baseline, warmup, or protocol pulses, the live harness must observe an
advancing native plist timestamp. Failure to observe rollover within the
bounded gate terminates powermetrics and refuses with
`pulse_calibration_rollover_gate_timeout`; no calibration evidence artifact is
minted from that capture.
