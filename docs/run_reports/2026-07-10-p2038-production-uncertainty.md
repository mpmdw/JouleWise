# P2-038 Production Uncertainty Evidence — Software Side (2026-07-10)

Status: software implementation and tests complete on `impl/p2038`; no commit.
The adjudicated live closure remains OPEN until a clean lead-controlled
quiet-machine shakedown succeeds and the resulting bundle is backed up to the
P0-003-approved destination.

## Baseline

- Branch: `impl/p2038`, stacked on `origin/c027-int-p2040`.
- Initial worktree: clean.
- Initial canonical suite: `Ran 910 tests in 32.965s`, `OK (skipped=12)`.
- The retained `/Users/edr/code/JouleWise/runs` corpus is not mounted in this
  worktree. The six-bundle test emitted its required loud acceptance-gate skip.

## Per-unit status

1. **Clock anchor — COMPLETE (software).** `ClockStamp` brackets a direct
   `time.time()` read with controller-monotonic reads. The real powermetrics
   path records pre-spawn, first-parse, start-marker, stop-marker, and
   post-parse stamps; current-era trace record zero is the midpoint endpoint
   of the spawn/first-parse interval after applying the run offset envelope.
   Whole-second plist dates are consistency-only. The exact six legacy
   identities retain the original offset/cumulative algorithm.
2. **Idle drift — COMPLETE (interim software).** The adapter retains the
   untrimmed pre-idle summed powers, captures a short post-idle plist after
   `sampling_stopped` and before cleanup, applies both GPU contamination
   checks, and records the full observed envelope about the pre-idle mean.
   The separate `idle_drift_guard` handoff block is reserved without importing
   the absent P2-039 module.
3. **Marker/sample phase — COMPLETE (software).** First- and last-interval
   support bounds are derived per run from the raw elapsed intervals and
   paired controller marker stamps. The effective clock scalar is the maximum
   of anchor-only, first-edge, and last-edge bounds.
4. **Post-run sentinel — COMPLETE (software).** Requested duration is
   `max(3 * interval, min(5 s, pre_idle_duration))`; it is outside the measured
   window and while the runtime remains prepared/resident. Detection-floor
   economics now include +5 s/bundle (about +15 to +28.3 minutes over the
   180–340 bundle range).
5. **Shakedown assertion — COMPLETE (software), LIVE OPEN.** Campaign mode
   `--shakedown-gate production_uncertainty_v1` requires one single-repetition
   config plus backup, executes strict -> reduce -> strict -> evidence/request
   assertion -> backup, fails loudly with named codes, and records a JSONL gate
   row. The committed lead-only config uses MLX, real powermetrics, and the
   five-item frozen sentinel suite. CI uses `SystemClock`, a real child process,
   the real `PowermetricsTelemetryAdapter` and committed fixture plists, the
   controller, reducer, and strict validator; only the runtime is mock.

## Metadata contract and derivations

Additive top-level metadata:

- `clock_anchor_bound_s = max(anchor_only_bound_s,
  marker_to_first_sample_phase_bound_s,
  marker_to_last_sample_phase_bound_s)`; omitted when clock evidence is
  unknown.
- `marker_to_first_sample_phase_bound_s`: maximum absolute separation between
  the bounded first averaging support and the bounded `sampling_started`
  marker.
- `marker_to_last_sample_phase_bound_s`: analogous maximum for the last
  averaging support and `sampling_stopped`.
- `idle_drift_bound_w = max(max_i(abs(pre_i - pre_mean)),
  max_j(abs(post_j - pre_mean)))` for >=3 finite, uncontaminated samples in
  each window; omitted otherwise. A later matched guard composes by
  `max(run_bound_w, guard_w)`.
- `uncertainty_evidence.schema_version = "p2-038.1"` with separate
  `clock_anchor`, `sample_phase`, `idle_drift`, and `idle_drift_guard` blocks.

Clock provenance records all five paired stamps, wall/monotonic resolutions,
offset-envelope endpoints, first-endpoint lower/upper/midpoint,
anchor-only/effective bounds, and every raw plist consistency result. Idle
provenance records both artifact names, counts, pre mean, contamination flags,
run envelope, calibration status/components, and effective bound.

The separate interim guard block is:

```json
{
  "calibration_status": "pending_calibration",
  "method": "p2_015_prediction_guard_v1",
  "guard_w": null,
  "n_bundles": 0,
  "bundle_sha256": [],
  "cell_id": null,
  "artifact_sha256": null
}
```

`calibration_status=pending_calibration` and `n_bundles=0` mean not applied;
the idle derivation records
`calibration_status=interim_run_sentinels_only` and a null applied guard.
P2-039's adjudicated schema example now reserves the same separately named
block for populated calibration provenance.

## New named tests

- `ClockEvidenceTests.test_paired_stamp_envelope_and_midpoint_timestamp_arithmetic`
- `ClockEvidenceTests.test_wall_clock_step_enlarges_envelope`
- `ClockEvidenceTests.test_nonfinite_or_reversed_stamp_is_unknown`
- `ClockEvidenceTests.test_plist_date_is_consistency_only_and_cannot_tighten_anchor`
- `ClockEvidenceTests.test_effective_bound_is_maximum_of_anchor_and_both_phases`
- `IdleDriftEvidenceTests.test_full_pre_post_envelope_retains_large_sample`
- `IdleDriftEvidenceTests.test_contamination_or_too_few_samples_withholds_scalar`
- `IdleDriftEvidenceTests.test_calibration_combination_is_exact_max_and_guard_formula`
- `P2038ProductionPathTests.test_real_powermetrics_evidence_path_passes_p2029_p2040_gates`
- `P2038ProductionPathTests.test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits`
- `P2038ProductionPathTests.test_strict_rederivation_rejects_evidence_raw_and_marker_tampering`
- `RunCampaignTests.test_p2038_shakedown_requires_backup_and_exactly_one_config`
- `RunCampaignTests.test_p2038_shakedown_rejects_mock_backend_with_named_gate_row`

The real child-process negative paths naturally exercise
`clock_bound_unrecorded`, `clock_bound_exceeds_quarter_window`, and
`drift_term_unknown`; no reducer scalar is inserted or deleted to create those
outcomes.

## Verification

- Required focused set (256 tests): `OK`.
- Additional post-review focused set (110 tests): `OK`.
- Lead shakedown config: `valid config`, target `macbook_m3_max`, runtime
  `mlx`, telemetry `powermetrics`.
- `git diff --check`: clean.
- Final canonical suite: `Ran 923 tests in 56.507s`, `OK (skipped=12)`.
- Six retained corpus bundles: not available in this worktree; loud skip
  recorded. The regression remains read-only and exact-identity-dispatched.

## Deviations and contradictions

- No authority contradiction was found. The adjudication superseded the
  draft's unresolved questions exactly as the prompt stated.
- The queue acceptance premise of a global `claim_eligibility.eligible` does
  not match the implemented schema; the governing spec corrects it to
  `claim_eligibility.request.eligible`, which is what the assertion tests.
- The CI shakedown uses a mock runtime but no mock telemetry or synthesized
  uncertainty. `assert_production_uncertainty(..., allow_mock_runtime=True)` is
  test-only; campaign mode rejects a mock runtime. This does not replace the
  true `/usr/bin/powermetrics` + MLX live gate.
- P2-039 code is absent on this branch as expected. P2-038 defines/tests only
  the separate guard handoff and updates the adjudicated schema prose; it does
  not import or implement the floor calculator.

## Double-check list / exact next step

- [x] Current-era midpoint/bracket derivation; plist dates do not tighten it.
- [x] Exact legacy algorithm and allowlist dispatch retained.
- [x] Post sentinel is after stop, before cleanup, and outside measurement.
- [x] Both idle windows require >=3 finite uncontaminated summed samples.
- [x] Unknown evidence preserves successful L0/L1 while gates fail closed.
- [x] Strict mode re-derives trace, bounds, markers, and idle artifacts.
- [x] Positive production-shaped gate contains no caller uncertainty metadata.
- [x] Negative gate reasons arise from real evidence-path conditions.
- [x] Campaign backup failure is fatal under shakedown mode.
- [ ] Lead reviews this uncommitted diff by pathspec.
- [ ] In a clean `[QUIET-MAC]` session after P0-003 is approved, run the
  committed production-shakedown campaign, require strict before/after reduce,
  request eligibility with `reasons=[]`, and successful approved backup.
