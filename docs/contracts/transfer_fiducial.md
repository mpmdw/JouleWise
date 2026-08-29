# TRANSFER-FIDUCIAL-01 inserted-gap diagnostic contract

Status: implemented but parked behind `V4-TRANSACTION-01`. Live execution is
`[QUIET-MAC]`, lead/Ed-owned, and must not occur while an agent session is
active. This protocol is diagnostic and non-claim-bearing. It mints no floor,
licenses no claim, and changes no `_v4` artifact.

## Purpose and fixed v1 regime

The arm tests whether the existing powermetrics pulse timing bound transfers
to the prefill/decode load regime. V1 is one separately verdictable stratum:

- Qwen2.5-1.5B-Instruct-4bit, revision
  `8b403126fc14f14cfc99bb4cfa72ecbc129ea677`;
- M3 Max, MLX runtime, powermetrics telemetry, int4;
- 4,096 prompt tokens, 512 output tokens, one repetition;
- one 0.5 second inserted gap and ten planned runs;
- at least 0.8 seconds in each active window and 6.0 seconds of post-window
  sampling dwell (the fit requires at least 4.5 seconds after margins).

No 7B arm exists in v1 because no evidenced prompt sizing point establishes
its 0.8-second prefill minimum. The plan schema is stratum-shaped so a future
ruled arm can receive its own ten-run verdict; observations across strata are
never pooled.

## Runtime boundary and zero-delta rule

`WorkloadProfile.transfer_fiducial_gap_s` is an additive, omission-serialized
optional in config schema `0.1`. Absence preserves normalized config bytes and
the legacy MLX event/call path. V1 accepts only finite value `0.5`, a
single-prompt workload, `repetitions == 1`, `output_tokens >= 1`, MLX runtime,
and powermetrics telemetry. Other runtimes refuse as `unsupported_workload`;
they never ignore the flag.

The measured boundary is
`boundary_semantics = first_yield_one_step_queued`. At the first `mlx_lm`
stream yield, one decode step is already queued. The flagged order is:

1. take `gap_start_stamp`;
2. emit `phase_end/prefill` and `fiducial_gap_start` at exactly that epoch;
3. call `mlx.core.synchronize()`;
4. call the injected clock's `sleep(0.5)` exactly once;
5. take `gap_end_stamp`;
6. emit `fiducial_gap_end` and `phase_start/decode` at exactly that epoch;
7. continue the unchanged generation loop.

The flagged outer `phase_start/prefill` and `phase_end/decode` events also
carry complete `clock_stamp` metadata. The gap lies in neither phase span.
Queued-work drain, sleep scheduling, and redispatch latency remain inside the
observed residual and are never subtracted. This is an inserted first-yield
transport fiducial, not a computation-exact natural phase boundary.

## Structural classification and claim lock

A bundle is transfer-diagnostic when either its config has a non-null
`transfer_fiducial_gap_s` or its events contain a `fiducial_gap_start` or
`fiducial_gap_end`. Config/event disagreement remains diagnostic and adds
`transfer_fiducial_class_inconsistent`. Every classified bundle receives the
LOCK reason `transfer_fiducial_claim_ineligible`; the inconsistency reason is
CONTRACT. A claim fence (a guard that prevents diagnostic evidence from
minting or supporting a claim) is active at each of the four consumers that
can mint or claim:

- `joulewise/analysis_engine/inputs.py:_read_bundle` labels classified input
  with the canonical refusal reason;
- `joulewise/floor_extraction.py:_evaluate_member` refuses a classified floor
  member;
- `scripts/mint_floor_artifact.py:_strict_bundle` refuses a classified bundle
  before minting; and
- `joulewise/whole_window.py:AuthenticatedConsumptionSession._prepare`
  refuses a whole-window set containing any classified bundle.

The reducer-layer defense-in-depth fence is deferred because the issued D079
calibration acceptance byte-hash-pins `joulewise/reduce.py`. Adding that fence
requires the governed post-V4 re-freeze of the D079 pin; issued pins must not
be hand-edited. Reduction therefore remains available so the diagnostic fit
can consume phase spans. The reducer's own outputs for a diagnostic bundle
are labelled non-claim-bearing by every downstream consumer listed above.
The diagnostic report keeps the bundle visible under the banner “DIAGNOSTIC
— non-claim-bearing (transfer fiducial).”

## Fit and statistic

The fitter re-anchors `raw/powermetrics.plist` from the bundle's stored clock
anchor and creates exactly two positive `CommandedPulse` values:

- `[phase_start/prefill, fiducial_gap_start]`;
- `[fiducial_gap_end, phase_end/decode]`.

Every endpoint uncertainty is `clock_stamp_half_width_s(stamp)`. The trace is
cropped at the last interval whose start is at or before
`prefill_start - FIT_HALF_RANGE_S`, retaining all later intervals. The fitter
then calls the imported, frozen
`powermetrics_fiducial.detect_pulses(intervals, pulses,
trace_anchor_bound_s=run_bound)` without changed constants or copied logic.

The run is inconclusive unless both active durations are at least 0.8 seconds,
the post-margin outside baseline is at least 4.5 seconds, all pulse edges have
coverage, both pulses are detected, the spurious plateau count is zero, and
all residual intervals are finite. The target edges are pulse 0 offset
(falling gap edge) and pulse 1 onset (rising gap edge); all other fit fields are
retained as nuisance diagnostics.

For each target edge:

```text
radius = max(abs(residual_lower_s), abs(residual_upper_s))
         + effective_clock_anchor_bound_s for that run
```

`residual_transfer_s` is the maximum over all 20 radii. Median and
nearest-rank p95 are diagnostic only and cannot decide the verdict.

## Calibration binding and verdict

The only comparison bound is
`<pulse-calibration-dir>/instrument_evidence.json#/b_fiducial_s`. The capture
records and verifies the evidence SHA-256, pulse protocol ID, estimator
revision, power policy, hardware model, OS build, and each run's attached
calibration identity. It also records the exact calibration path, capture
time/validation ID, `b_pulse_s`, estimator source SHA-256, config hashes,
bundle IDs, source commit, complete gap/boundary events and ClockStamps,
commanded and observed gap durations, anchors, constructed pulses, every fit
field, target radii, and pipeline caveat.

The only verdicts are:

- `supported`: every gate passes and `residual_transfer_s <= b_pulse_s`;
- `exceeds_bound`: every gate passes and the residual is larger;
- `inconclusive`: any planned run, binding, anchor, fit, or completeness gate
  fails.

`excess_s` is `max(0, residual_transfer_s - b_pulse_s)`. Failed runs are never
dropped and the pulse bound is never widened after observing the arm.

The bracket-calibration variant is not built. V1 binds one pulse calibration
directory named to the fit script, as ruled.

## Post-campaign live procedure

These commands are parked until `V4-TRANSACTION-01` closes. Run them only from
a clean, lead-controlled, agent-free quiet-machine session after the standard
readiness/idle procedure, with approved power, working `sudo -n powermetrics`,
and network-time custody.

```sh
JW_REPO=/Users/edr/code/JouleWise
JW_PY=/Users/edr/code/JouleWise/.venv/bin/python
TF_ROOT=/Users/edr/JouleWise-transfer-fiducial-01
TF_CAL_ROOT="$TF_ROOT/instrument_validation"
TF_RUNS_ROOT="$TF_ROOT/runs"
POWER_POLICY=ac_high_power

cd "$JW_REPO"
bash scripts/quiet_mac_prep.sh

"$JW_PY" scripts/validate_powermetrics_fiducial.py \
  --allow-live \
  --arm-countdown-s 20 \
  --sleep-display-before-capture \
  --output-root "$TF_CAL_ROOT" \
  --power-policy "$POWER_POLICY"
```

After selecting the unique successful calibration directory as `TF_CAL_DIR`:

```sh
for TF_CONFIG in configs/diagnostics/transfer_fiducial_v1/tf-q15-p4096-o512-r{01,02,03,04,05,06,07,08,09,10}.json
do
  "$JW_PY" -m joulewise run "$TF_CONFIG" \
    --runs-dir "$TF_RUNS_ROOT" \
    --instrument-calibration-dir "$TF_CAL_DIR" \
    --instrument-power-policy "$POWER_POLICY" \
    --post-window-sampling-dwell-s 6.0 || exit 1
done

"$JW_PY" scripts/fit_transfer_fiducial.py \
  --plan configs/diagnostics/transfer_fiducial_v1/plan.json \
  --runs-root "$TF_RUNS_ROOT" \
  --pulse-calibration-dir "$TF_CAL_DIR" \
  --output "$TF_ROOT/transfer_fiducial_capture.json"
```

Restore network time only after verification and backup. Review the capture
without promoting its diagnostic verdict into any claim or floor artifact.
