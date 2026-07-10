# P2-040 Reducer/Gate Correctness Batch

Queue authority: `TASK_QUEUE.md` row P2-040. Review authority:
`docs/reviews/2026-07-09-c027-whole-project-review.md` §3 B7(a) and §7
rows STA-5..STA-8, STA-11, ARC-3, ARC-5, ARC-6 (local half), and ARC-8.
Underlying evidence: `docs/reviews/c027/lens-stats.md` findings 5..8 and
`docs/reviews/c027/lens-arch.md` findings 3, 5, 6, and 8.

This specification is implementation-grade for P2-040 only. It does not
implement the P2-037 contrast/claim engine, P2-038 production uncertainty
capture, P2-039 floor artifacts, P2-041 campaign claim-readiness, or
NV-GATE-2 remote cleanup work.

Line references are against repository head `0a5c5e6` on 2026-07-09.

## Design Tradeoffs And Rulings

### Correctness versus read-only compatibility

The batch changes reducer semantics after real and fixture bundles already
exist. Rewriting raw evidence is forbidden by D-002, while blindly tolerating
old stored values would violate D-030.

Ruling:

1. `CONFIG_SCHEMA_VERSION` and `SUMMARY_SCHEMA_VERSION` remain `"0.1"`.
2. `SUMMARY_REDUCER_VERSION` becomes `"0.3.0"` because FIX-1, FIX-3, and
   FIX-4 change derivation semantics.
3. Strict validation gains a reducer-version compatibility projection. A
   stored `0.2.0` summary is compared with the exact `0.2.0` projection of
   raw evidence for fields whose semantics changed, not with wildcard
   tolerance. A tampered old field must still fail.
4. New additive fields may be absent from pre-0.3.0 summaries through
   explicit path/suffix tolerances. Stored values, if present, remain exact.
5. The six frozen pre-D-033 corpus bundles remain read-only inputs. They are
   not rewritten or added to another allowlist.
6. There is no exemption for a succeeded zero/nonpositive measured window.

For a stored `summary_provenance.reducer_version == "0.2.0"`, compatibility
projection:

- projects the fresh reducer version back to `0.2.0`;
- recomputes the legacy total-token denominator as configured prompt tokens
  plus runtime output events when available, otherwise the runtime-observed
  total;
- projects `energy_token_j` and
  `measurement_quality.token_count_source` accordingly; and
- leaves every other stored field under exact comparison.

After an explicit `joulewise reduce`, the canonical summary becomes 0.3.0
and strict validation uses current semantics. This is validation
compatibility, not automatic migration.

### Stable reason vocabulary

D-057 freezes `claim_eligibility.reasons`. Existing codes retain their exact
spelling and meaning. P2-040 proposes two additive codes, which must be
appended to D-057 before implementation lands:

| Code | Exact meaning |
|---|---|
| `nonpositive_window_duration` | The evaluated window has `duration_s <= 0` and cannot be claim-bearing. |
| `idle_baseline_unrecorded` | An idle-subtracted metric was requested but no valid idle baseline exists. |

Do not repurpose `insufficient_in_window_samples` for zero duration or
`drift_term_unknown` for a missing idle baseline.

The current `claim_eligibility` object remains a window-evidence precheck.
P2-037 owns its rename to `window_evidence_precheck` and the full
floor/effect/contrast evaluator.

### Metric-specific gates without a v0.1 break

The premise “gross request wrongly requires drift” is imprecise in the
current code: no explicit gross-request gate exists. The sole
`claim_eligibility.request` gate is ambiguous and always requires drift
(`joulewise/reduce.py:424-433`), while `energy_request_j` is the
idle-subtracted value (`joulewise/reduce.py:767-779`).

New summaries therefore add `gross_request` and
`idle_subtracted_request`. The old `request` key remains a deprecated alias
of the idle-subtracted precheck through schema v0.1.

### Joint-edge bound

The old one-edge sensitivity is useful diagnostic evidence but is not a
simultaneous endpoint bound. Replacing it in place would also make old
summaries drift.

Retain `E_interpolation_edge_bound_j` with its current meaning and add
`E_interpolation_joint_edge_bound_j` as the governed bound. Evaluate all
four Cartesian combinations of independently shifting the start and end by
plus or minus half their local gaps. P2-037 and floor tooling consume only
the joint field.

### Token fallback

D-058 is binding: runtime-observed denominators win. When no
runtime-observed total exists, constructing a configured-prompt-plus-output
denominator would require a separate L0-only metric and claim ceiling.

P2-040 instead fails closed: `energy_token_j` is null without a positive
runtime-observed total. Configured counts remain workload intent.

### Zero-MAD handling

MAD zero does not justify an invented modified z-score, but it must not hide
off-median points. Flag each off-median value for review with
`modified_z=null`; keep every point in the headline aggregate.

This is forensic flagging, not D-053 leave-one-out analysis.

### Atomic manifests are not resume

Atomic replacement prevents torn JSON. It does not implement experiment
resume: a rerun still starts at repetition one and collides with immutable
bundle directories.

### Unknown keys and `warmup_seconds`

Schema 0.1 uses deterministic warn-and-ignore for unknown keys. Hard
rejection would invalidate old configurations and make forward-compatible
readers brittle.

Deleting `sampling.warmup_seconds` would change normalized config bytes and
D-001/D-022 hashes pinned by D-029. It also appears as 5.0 in active Mac and
campaign configurations and in three immutable corpus configs. Implement it
as a post-warmup, pre-sampling settling delay instead.

### Cleanup failure

Runtime cleanup occurs after the measured window. Its failure can contaminate
the next repetition but does not retroactively erase the current
measurement.

Keep the current run status and energy result, add
`measurement_quality.runtime_cleanup_ok`, and leave campaign-level handling
to P2-041. Do not add a window-local D-057 reason.

## Shared Versioning And Compatibility Requirements

The implementation must:

- Set `SUMMARY_REDUCER_VERSION = "0.3.0"`.
- Keep config and summary schema versions at 0.1.
- Select strict compatibility only from the stored reducer version, never a
  caller flag.
- Add strict additive-absence compatibility for:
  - `claim_eligibility.gross_request`;
  - `claim_eligibility.idle_subtracted_request`;
  - nested `interpolation_joint_edge_bound_j` fields;
  - `energy_bound_terms_j.E_interpolation_joint_edge_bound_j`; and
  - `measurement_quality.runtime_cleanup_ok`.
- Add `runtime_cleanup_ok` as a nullable boolean to `MeasurementQuality` and
  the output JSON Schema.
- Update `docs/contracts/run_bundle_layout.md` for the metric-specific request
  entries, deprecated alias, interpolation fields, cleanup field, and new
  reason codes.
- Amend D-057 with the two additive reason codes.
- Amend D-030 to document reducer-version projection and explicit rejection
  of succeeded nonpositive windows.
- Never mutate raw corpus files.

A regression test must enumerate all six frozen corpus identities and call
`validate_bundle(path, strict=True)` without invoking `reduce` or writing any
file. Acceptance is six empty problem lists.

## FIX-1 — Nonpositive Measured Windows Fail Closed (ARC-3)

### Current behavior

- The reducer contract says a zero window integrates to zero and is not an
  error (`joulewise/reduce.py:22-35`).
- `_reduce` special-cases `duration_s == 0.0` and returns
  `_zero_window_summary` (`joulewise/reduce.py:742-756`).
- `_zero_window_summary` emits `status=succeeded`, zero energy, derived token
  ratios, phase/suite metrics, and `claim_eligibility`
  (`joulewise/reduce.py:832-884`).
- Strict validation applies the two-sample floor only when duration is
  positive (`joulewise/cli.py:272-304`).
- `_window_claim_eligibility` has no duration reason and skips sample-count
  enforcement for zero duration (`joulewise/reduce.py:523-582`).
- Wrong behavior is locked by `tests/test_reduce.py:406-433` and
  `tests/test_reduce.py:757-780`.

### Target behavior

1. `_reduce` must reject any measured window with `duration_s <= 0.0` before
   token, phase, suite, uncertainty, or energy derivation.
2. Raise `_ReduceError` with exact prefix:
   `measured_run window duration must be > 0 s; got `.
3. `reduce_bundle` returns a schema-valid
   `SummaryMetrics(status=failed, failure_reason=unknown_error)` through the
   existing structured reducer-failure path.
4. Delete `_zero_window_summary` and correct the reducer module contract.
5. `_window_claim_eligibility` appends
   `nonpositive_window_duration` for every nonpositive subwindow and never
   marks it eligible.
6. Strict validation of a stored succeeded bundle appends:
   `strict: succeeded bundle measured window duration must be > 0 s; got <x>`.
   This check must be independent of fresh-summary comparison.
7. Per D-030, a correctly stored failed bundle may remain valid as a failure
   record. The closed gate is admission as a strict-valid succeeded
   measurement.

### API/schema delta

- New D-057 reason: `nonpositive_window_duration`.
- No new `FailureReason`.
- Delete `_zero_window_summary`.
- No new summary field.

### Backward compatibility

- No succeeded nonpositive window is grandfathered.
- The six legacy bundles are not exempt; they pass naturally because their
  measured windows are positive.
- Historical failed bundles remain governed by D-030.

### Test obligation

Existing tests:

- Change `DegenerateTests.test_zero_length_window_is_zero_energy_not_failure`
  (`tests/test_reduce.py:406`) to require `failed/unknown_error`, null energy
  fields, and the exact failure-message prefix.
- Replace `test_zero_length_window_keeps_real_phase_energy`
  (`tests/test_reduce.py:418`) with the assertion that invalid measured
  windows emit no derived phase/suite metrics.
- Change
  `SuiteReduceTests.test_zero_window_suite_bundle_retains_degenerate_suite_metrics`
  (`tests/test_reduce.py:757`) to require structured failure.
- Correct the obsolete reducer-success comment at
  `tests/test_mock_adapters.py:691-697`.

New mutation-style tests:

- `StrictValidateTests.test_succeeded_zero_window_is_rejected_even_when_fresh_summary_comparison_is_stubbed_equal`:
  create a succeeded zero-window bundle, stub fresh re-reduction to equal the
  stored summary, and require the explicit strict duration problem.
- `ClaimGateTests.test_zero_duration_phase_has_nonpositive_window_reason`:
  place a zero phase inside a valid positive measured window and require the
  new reason and `eligible=false`.

### No-scope-creep fences

- Do not reject zero-duration cooldown or unrelated operational notes.
- Do not add a D-012 reason.
- Do not make correctly stored failed bundles default-validation failures.
- Do not preserve derived phase/suite metrics in the failed summary.

## FIX-2 — Metric-Specific Gross And Idle-Subtracted Gates (STA-5)

### Current behavior

- `_claim_eligibility` emits only `request` and passes
  `require_drift=True` (`joulewise/reduce.py:417-434`).
- `_window_claim_eligibility` therefore emits `drift_term_unknown` and
  `cooldown_cap_hit` for that generic request
  (`joulewise/reduce.py:563-569`).
- Gross and idle-subtracted metrics are separate, while `energy_request_j`
  aliases idle-subtracted energy (`joulewise/reduce.py:765-779`).
- Gross request has no idle-subtraction terms under
  `docs/phase_2/detection_floor.md:288-300`.
- Tests at `tests/test_uncertainty_p2029.py:221-243` and
  `tests/test_uncertainty_p2029.py:379-390` lock the generic drift-dependent
  behavior.

### Target behavior

`claim_eligibility` must contain:

- `gross_request`: for `gross_energy_j`; requires cadence, clock,
  nonpositive-window, joint interpolation, and request-level cooldown
  evidence, but not idle baseline or drift bound.
- `idle_subtracted_request`: for `idle_subtracted_energy_j` and
  `energy_request_j`; requires common evidence plus idle baseline and
  `E_drift_bound_j`.
- `request`: deprecated schema-0.1 alias retaining the old
  idle-subtracted meaning.

Each new entry carries:

- `metric_name`: `gross_energy_j` or `idle_subtracted_energy_j`;
- `window_class`: `gross_request` or `idle_subtracted_request`.

Missing idle baseline adds `idle_baseline_unrecorded` only to the
idle-subtracted entry. Missing drift adds `drift_term_unknown` only there.

`cooldown_cap_hit` remains a request-level quality exclusion for both request
metrics; it must be decoupled from the idle-drift switch.

Phase/item/block/level entries retain their gross-only rules.

### API/schema delta

- New keys `gross_request` and `idle_subtracted_request`.
- New entry fields `metric_name` and `window_class`.
- New D-057 reason `idle_baseline_unrecorded`.
- `request` is deprecated but retained.

### Backward compatibility

- Old summaries containing only `request` remain strict-valid through explicit
  additive absence tolerance for the two new keys.
- The stored old `request` value remains exact.
- The six corpus summaries predate `claim_eligibility`; existing root
  tolerance applies.
- New reductions always emit both specific entries, even when idle-subtracted
  energy is unavailable.

### Test obligation

Existing tests:

- Update
  `ClaimGateTests.test_request_window_at_cadence_and_clock_boundaries_is_eligible`
  (`tests/test_uncertainty_p2029.py:247`) for both specific entries and the
  alias.
- Update `test_request_without_drift_evidence_is_ineligible`
  (`tests/test_uncertainty_p2029.py:379`): gross passes; idle-subtracted and
  `request` contain `drift_term_unknown`.
- Update `test_drift_bound_rejects_alias_only_key_paths`
  (`tests/test_uncertainty_p2029.py:221`): unsupported drift aliases do not
  affect gross and fail idle-subtracted.
- Convert other direct `["request"]` accesses to the intended metric-specific
  key, retaining one explicit alias assertion.

New mutation-style test:

- `ClaimGateTests.test_gross_request_without_idle_model_passes_while_idle_subtracted_fails`:
  valid cadence/clock, no idle baseline, but a recorded drift bound. Require
  `gross_request.eligible=true` and
  `idle_subtracted_request.reasons == ["idle_baseline_unrecorded"]`.

### No-scope-creep fences

- Do not compare bounds to floors/effects.
- Do not rename the top-level `claim_eligibility`.
- Do not remove `request` before schema v0.2.
- Do not create idle-subtracted phase/item/block/level metrics.

## FIX-3 — Joint-Edge Interpolation Bound (STA-6)

### Current behavior

- `_interpolation_edge_bound_j` shifts only one edge at a time and takes the
  maximum change (`joulewise/reduce.py:393-414`).
- The result is stored as `E_interpolation_edge_bound_j`
  (`joulewise/reduce.py:348-362`) and exposed as
  `interpolation_edge_bound_j` (`joulewise/reduce.py:555-582`).
- Aggregation propagates the old field (`joulewise/aggregate.py:322-385`).
- `tests/test_uncertainty_p2029.py:363-377` locks 4 J for a case whose joint
  inward/outward shifts change energy by 8 J.

### Target behavior

For window `[s,e]`:

1. Let `ds = 0.5 * start_bracketing_gap` and
   `de = 0.5 * end_bracketing_gap`.
2. Compute base energy `E(s,e)`.
3. Evaluate `E(s + a*ds, e + b*de)` for every `a,b ∈ {-1,+1}`.
4. Set the joint bound to the maximum absolute change from base.
5. Return null if either gap is unavailable.
6. Return null if the maximally inward combination inverts the window:
   `s+ds > e-de`. Equality is allowed and yields a zero-duration candidate.
7. Keep the old single-edge sensitivity unchanged.
8. Evidence prechecks use the joint field for recorded/unrecorded status and
   expose both fields.
9. Aggregate propagation carries the maximum known joint bound using the
   existing all-members-known rule.

This is a deterministic bound over the declared four-point perturbation
recipe, not a probability model for timing error.

### API/schema delta

- Add `energy_bound_terms_j.E_interpolation_joint_edge_bound_j`.
- Add `interpolation_joint_edge_bound_j` to single-window prechecks.
- Retain the old one-edge fields unchanged.
- Missing joint evidence uses existing
  `interpolation_bound_unrecorded`.

### Backward compatibility

- Old stored one-edge values remain exact and are never reinterpreted.
- New joint keys are additive-absence-tolerated in pre-0.3.0 summaries,
  including dynamic phase/item/block/level entries.
- The six corpus summaries omit these blocks and remain valid.
- Explicit re-reduction adds the joint field and reducer version 0.3.0.

### Test obligation

Existing tests:

- Rename/update
  `ClaimGateTests.test_interpolation_edge_bound_uses_edge_perturbation_recipe`
  (`tests/test_uncertainty_p2029.py:363`) to assert old one-edge = 4 J,
  joint-edge = 8 J, and that the precheck uses 8 J.
- Extend
  `test_interpolation_edge_bound_is_recorded_for_phase_window`
  (`tests/test_uncertainty_p2029.py:343`) from old 13 J to also assert
  hand-computed joint 26 J.
- Extend aggregator propagation tests at
  `tests/test_uncertainty_p2029.py:434-567` for joint maximum and
  null-on-any-member-unknown behavior.

New mutation-style test:

- `ReducerPropagationTests.test_joint_edge_bound_moves_both_edges`:
  constant 8 W, one-second gaps, window `[2.5,6.5]`; require joint 8 J and
  legacy one-edge 4 J.

### No-scope-creep fences

- Do not remove or rename the old field in schema 0.1.
- Do not assign a distribution to endpoint error.
- Do not add floor/effect comparison.
- Do not change trapezoidal integration or clamping.

## FIX-4 — D-058 Runtime-Observed Total-Token Precedence (STA-7)

### Current behavior

- `_total_tokens` prefers configured prompt tokens plus runtime output events
  over `metadata.workload_observed.token_count`
  (`joulewise/reduce.py:262-297`).
- `token_count_source` records `"config"` for that path
  (`joulewise/schemas.py:556-562`).
- `tests/test_reduce.py:577-584` explicitly locks configured 32 + four events
  over runtime-observed total 999.
- D-058 and `docs/contracts/token_normalization.md:39-49` require
  runtime-observed denominators.

### Target behavior

1. `_total_tokens` first reads the positive runtime-observed total.
2. If present, return it with source `runtime_observed` regardless of
   configured counts or output events.
3. If absent, return `(None, None)`.
4. Do not construct a governed total from configured prompt count plus output
   events.
5. `energy_token_j` is null without a runtime-observed total.
6. Request energy and runtime-observed output-token metrics remain available.
7. In 0.3.0 summaries, `token_count_source` is
   `runtime_observed | null`.
8. Historical stored `"config"` values are accepted only through exact 0.2.0
   projection.
9. `token_counts_source` for output-only token evidence is unchanged.

### API/schema delta

- No new field.
- Narrow the 0.3.0 `token_count_source` domain.
- `energy_token_j` remains nullable.
- Bump the reducer version and add the version-aware strict projection.

### Backward compatibility

- Stored 0.2.0 summaries validate against the frozen legacy denominator
  derivation; arbitrary stored values are not tolerated.
- All six corpus summaries already record
  `token_count_source=runtime_observed` and reproduce their stored values.
- Explicit `joulewise reduce` migrates only the derived summary.

### Test obligation

Existing tests:

- Rename `TokenFallbackTests.test_config_supplied_counts_still_win`
  (`tests/test_reduce.py:577`) to
  `test_runtime_observed_total_wins_over_configured_counts`; assert `25/999`
  and source `runtime_observed`.
- Rename the “prompt text fallback” test language: runtime observation is
  authoritative, not a fallback.
- Keep output-token-only tests unchanged.
- Add strict compatibility coverage for an on-disk 0.2.0 summary whose
  legacy config-derived total differs from runtime observation. It passes
  read-only; a stored metric mutation fails.

New mutation-style test:

- `TokenFallbackTests.test_config_plus_output_events_does_not_fabricate_total_denominator`:
  configured prompt count and four output events, but no observed total.
  Require `energy_token_j is None`, `token_count_source is None`, and
  `energy_output_token_j` remains present.

### No-scope-creep fences

- Do not derive J/char, J/byte, or semantic denominators.
- Do not change output-event filtering or `token_counts_source`.
- Do not add an L0-only duplicate total-token metric.
- Mark TASK_QUEUE P2-016(i)'s total-token “config fallback” work superseded by
  D-058/P2-040. Its output-token `config_fallback` vocabulary remains valid.

## FIX-5 — Zero-MAD Off-Median Review Flags (STA-8)

### Current behavior

- `_outlier_entries` returns no entries and
  `mad_zero_not_computable` whenever MAD is zero
  (`joulewise/aggregate.py:423-454`).
- `_aggregate_metric` reports the empty result while retaining all points
  (`joulewise/aggregate.py:201-245`).
- `tests/test_aggregate.py:239-245` locks `[5,5,5,100] -> zero flags`.
- D-014 requires forensic flagging without silent deletion.

### Target behavior

When MAD > 0, retain the existing modified-z algorithm and strict
`abs(z) > 3.5` threshold.

When MAD == 0 and every value equals the median:

- emit no flags;
- set `outlier_method_status = "mad_zero_all_equal"`.

When MAD == 0 and values differ from the median:

- emit one `outliers[]` entry per off-median point;
- set `modified_z = null`;
- set `flag_basis = "mad_zero_off_median_review"`;
- set `review_only = true`;
- set `outlier_method_status = "mad_zero_fallback_applied"`.

`outlier_count` includes the review flags. `headline_includes_outliers`
remains true and every point remains in the headline interval.

### API/schema delta

- New statuses `mad_zero_all_equal` and
  `mad_zero_fallback_applied`.
- Fallback entries add `flag_basis`, `review_only`, and nullable
  `modified_z`.
- No run-bundle summary schema change.

### Backward compatibility

- Existing experiment manifests remain readable historical snapshots.
- Re-aggregation writes the new flags.
- The six run bundles are unaffected; strict bundle validation does not call
  the experiment aggregator.

### Test obligation

Existing tests:

- Update
  `OutlierTests.test_mad_zero_path_records_status_without_fake_z_scores`
  (`tests/test_aggregate.py:239`) to expect the review-only flag for 100.
- Update
  `ConfidenceIntervalTests.test_zero_variance_values_have_point_interval_and_mad_zero_status`
  (`tests/test_aggregate.py:108`) to expect `mad_zero_all_equal`.
- Keep ordinary positive/negative modified-z tests unchanged.

New mutation-style test:

- `OutlierTests.test_zero_mad_fallback_flags_off_median_point_but_keeps_it_in_headline`:
  aggregate `[5,5,5,5,100]`; require the r5 review flag, headline mean 24,
  and a keep-all interval.

### No-scope-creep fences

- Do not implement D-053 LOO contrasts.
- Do not emit a “without flagged point” interval without documented physical
  cause.
- Do not change the z threshold or scale.
- Do not automatically exclude fallback flags.

## FIX-6 — Atomic Experiment-Manifest Replacement (ARC-5)

### Current behavior

- `write_experiment_manifest` calls `Path.write_text` directly on the
  canonical path (`joulewise/bundle.py:92-106`).
- `run_experiment` rewrites after every member and cooldown note
  (`joulewise/controller.py:1162-1192`).
- Failure during overwrite can leave truncated JSON.
- Tests prove overwrite is allowed but not atomic
  (`tests/test_bundle.py:493-516`).
- The controller's “valid partial manifest” claim
  (`joulewise/controller.py:1123-1125`) is stronger than the writer
  guarantees. No resume mechanism exists.

### Target behavior

`write_experiment_manifest` must:

1. Serialize once using the existing sorted/indented/trailing-newline form.
2. Create a unique temporary file in the same `experiments/` directory.
3. Write all bytes, flush, and `os.fsync` the file.
4. Close it and call `os.replace(temp, destination)`.
5. Best-effort fsync the parent directory after replacement.
6. On failure before replacement, close/unlink the temp file best-effort,
   propagate the original error, and leave an existing destination
   byte-for-byte unchanged.
7. Leave no temp file after success.

The contract must say a killed experiment leaves either the previous complete
manifest or the new complete manifest. It must not promise resume.

### API/schema delta

- `write_experiment_manifest(runs_root, manifest) -> Path` is unchanged.
- Manifest bytes and schema are unchanged.
- Add a private same-directory atomic-write helper.

### Backward compatibility

- Existing readers and manifests require no changes.
- Validation never rewrites a manifest.
- The six corpus bundles/manifests are unaffected.

### Test obligation

Existing tests:

- Keep `ExperimentManifestTests.test_overwrite_is_allowed`
  (`tests/test_bundle.py:507`) and assert no temp files remain and canonical
  JSON formatting is unchanged.
- Keep sanitization and missing-id tests unchanged.

New mutation-style test:

- `ExperimentManifestTests.test_failed_atomic_replace_preserves_previous_manifest`:
  write an old manifest, patch `joulewise.bundle.os.replace` to raise while
  writing an extension, and require byte-identical old destination plus no
  temp files.

### No-scope-creep fences

- Do not implement experiment resume or repetition skipping.
- Do not change immutable bundle behavior.
- Do not add concurrent-writer locking.
- Do not convert raw bundle artifacts to atomic replacement in this batch.

## FIX-7 — Unknown-Key Warnings And `warmup_seconds` Semantics (ARC-8)

### Current behavior

- Every `from_mapping` extracts known keys and ignores all others;
  `BenchmarkConfig.from_mapping` has no unknown-key pass
  (`joulewise/schemas.py:118-378`).
- `tests/test_audit_schema_edges.py:53-62` explicitly requires silent ignore.
- `SamplingConfig` accepts and serializes `warmup_seconds`
  (`joulewise/schemas.py:292-318`), and the JSON Schema exposes it
  (`joulewise/schemas.py:494-500`).
- The lifecycle executes `warmup_runs` but never reads
  `config.sampling.warmup_seconds` (`joulewise/controller.py:425-434`).
- The field appears in every active example config and in campaign templates.

### Target behavior: unknown keys

1. Add `ConfigKeyWarning(UserWarning)` with:
   - `code = "unknown_config_key"`;
   - deterministic dotted `path`; and
   - message:
     `unknown config key '<path>' ignored by schema 0.1`.
2. Add central allowlists for the root and every typed nested object:
   `model`, `quantization`, `hardware_target`, `workload_profile`,
   `interconnect`, `sampling`, and `run_metadata`.
3. `BenchmarkConfig.from_mapping` emits one
   `warnings.warn(ConfigKeyWarning(...), stacklevel=2)` per unknown path in
   lexicographic path order, then continues parsing.
4. Non-object typed sections remain `SchemaError`; do not inspect child keys.
5. Unknown values remain ignored and never appear in `to_dict()`, normalized
   config, hashes, or metadata.
6. Add top-level JSON Schema extension:
   `"x-joulewise-unknown-key-policy": "warn-and-ignore"`.
7. Do not set `additionalProperties:false` in schema 0.1.

### Target behavior: `warmup_seconds`

1. Keep its field, validation, schema, and serialized bytes unchanged.
2. Define it as post-warmup settling time.
3. After all `warmup_runs` calls and alignment captures, but before
   `stage_completed(warmup)` and `sampling_started`, call the injected clock's
   `sleep(warmup_seconds)` when positive.
4. Warmup completion metadata contains both `warmup_runs` and
   `warmup_seconds`.
5. The runtime log records the settling duration.
6. Zero preserves current timing.
7. The delay applies to single-prompt and suite runs and remains outside the
   measured window.
8. Update `docs/phase_2/phase_2_plan.md` and measurement-methodology lifecycle
   prose.

### API/schema delta

- New warning category `ConfigKeyWarning`.
- New warning code `unknown_config_key`.
- Add the JSON Schema extension only; field schemas and versions remain
  unchanged.
- `sampling.warmup_seconds` becomes executable lifecycle behavior.

### Backward compatibility

- Unknown keys warn but do not invalidate configs or bundles.
- `warmup_seconds` remains known, so the six corpus bundles issue no warning
  and validate read-only.
- Validation/reduction never executes the delay.
- Re-executing a historical config with `warmup_seconds=5.0` now performs the
  five-second settle. Old evidence remains untouched.
- Config hash pins must not change.

### Test obligation

Existing tests:

- Rename/update
  `SchemaCoverageGapTests.test_unknown_workload_keys_are_ignored`
  (`tests/test_audit_schema_edges.py:53`) to assert exactly one typed warning,
  dotted path, and continued ignore behavior.
- Keep negative `warmup_seconds` validation
  (`tests/test_audit_schema_edges.py:31-43`).
- Keep `tests/test_schemas.py:295-307` hash pins byte-identical.
- Extend controller happy-path stage assertions with `warmup_seconds`.

New mutation-style tests:

- `SchemaCoverageGapTests.test_sampling_typo_warns_before_defaulting`:
  supply `sampling.power_hzz=10` without `power_hz`; require the warning and
  default `power_hz == 1.0`.
- `HappyPathTests.test_warmup_seconds_advances_injected_clock_before_sampling`:
  use a distinctive settle value; assert exact event-time advancement,
  completion metadata, and measured-window start afterward.

### No-scope-creep fences

- Do not hard-reject unknown keys under schema 0.1.
- Do not preserve unknown values.
- Do not rename `warmup_seconds` or reinterpret it as repeated active
  workload.
- Do not implement suite-manifest `warmup_policy`.
- Do not change `warmup_runs` or move warmup inside sampling.

## FIX-8 — Local Runtime-Cleanup Failure In Measurement Quality (ARC-6)

### Current behavior

- `_stage_cleanup` records `cleanup_ok=false` in the cleanup completion event
  when cleanup raises or returns `ok=false`, while leaving status unchanged
  (`joulewise/controller.py:508-546`).
- Cleanup occurs before reduction, and `_stage_reduce` flushes events before
  calling the pure reducer (`joulewise/controller.py:548-561`).
- The reducer ignores cleanup events and `MeasurementQuality` has no cleanup
  field (`joulewise/schemas.py:540-576`).

### Target behavior

1. Add `BundleReader.runtime_cleanup_ok() -> bool | None`.
2. Inspect `stage_completed` events for phase `cleanup`:
   - return false if any well-formed matching event has
     `metadata.cleanup_ok == false`;
   - return true when matching events all record true;
   - return null when no boolean evidence exists or a matching completion has
     a non-boolean value.
3. `_reduce` copies the result to
   `measurement_quality.runtime_cleanup_ok`.
4. Cleanup failure does not change current status, failure reason, energy, or
   window reasons.
5. New successful controller bundles emit true or false, never null.
6. Legacy/post-hoc bundles without cleanup evidence may emit null.
7. P2-041 later consumes false as a suspect quality flag.

### API/schema delta

- Add nullable boolean `MeasurementQuality.runtime_cleanup_ok`.
- Add it to the output JSON Schema.
- Add `BundleReader.runtime_cleanup_ok()`.
- Add no `FailureReason` or D-057 reason.

### Backward compatibility

- Add the field to strict additive-absence tolerance for pre-0.3.0 summaries.
- If an old summary already contains a value, it remains exact.
- All six corpus event streams record `cleanup_ok=true`; their stored
  summaries omit the field and pass read-only through the additive tolerance.
- Failure-path summaries before normal cleanup retain null.

### Test obligation

Existing tests:

- Extend `HappyPathTests.test_summary_is_reduced_by_default_reducer`
  (`tests/test_controller.py:529-548`) to require true in memory and on disk.
- Extend strict additive-field tests at `tests/test_cli_run.py:416-430` and
  legacy honesty-field tests at `tests/test_cli_run.py:606-618`.

New mutation-style tests:

- `CleanupQualityTests.test_cleanup_adapter_failure_surfaces_without_retroactive_run_failure`:
  wrap the local mock runtime so cleanup returns `AdapterResult(ok=false)`.
  Require succeeded status, null failure reason, cleanup event false, and
  in-memory/stored `runtime_cleanup_ok=false`.
- A companion exception-path test should require the same false field when
  cleanup raises.

### No-scope-creep fences

- Do not demote the current run solely for post-window cleanup failure.
- Do not stop/resume experiment execution.
- Do not add remote cleanup reporting.
- Do not copy free-form cleanup messages into `MeasurementQuality`.

## Ordering And Dependencies

Land as one reviewable P2-040 PR in this order:

1. Shared reducer-version/strict-compatibility scaffolding and D-057
   vocabulary amendment.
2. FIX-1.
3. FIX-3, then FIX-2, so metric-specific gates consume the joint field.
4. FIX-4 with its 0.2.0 strict projection.
5. FIX-5 and FIX-6.
6. FIX-7 before final controller fixtures, because warmup changes event times.
7. FIX-8, followed by the six-corpus read-only regression and canonical suite.

Interactions:

- FIX-1 and FIX-3 both touch window handling; nonpositive measured windows
  exit before bound calculation.
- FIX-2 consumes FIX-3 and shares D-057 amendments with FIX-1.
- FIX-4 alone needs old-semantic value projection rather than only additive
  absence tolerance.
- FIX-7 and FIX-8 both affect controller tests but different lifecycle stages.
- FIX-6 changes manifest publication only.

Per STA-11, every named mutation test must be demonstrated red against the
pre-fix implementation or an equivalent reverted mutation and green after
the fix. Record red/green evidence by test name; a green full suite alone is
insufficient.

## Global No-Scope-Creep Fence

P2-040 must not:

- implement paired/block contrasts, multiplicity, LOO verdict tables,
  metrology-aware contrast intervals, or the full claim evaluator;
- fabricate production clock/drift evidence;
- implement or freeze floor artifacts;
- change campaign “publishable” semantics;
- implement experiment resume;
- mutate raw evidence or rewrite corpus summaries during validation;
- implement remote cleanup, NVIDIA lineage, or vLLM token semantics; or
- change schema version 0.1.

## Acceptance Checklist

- [ ] FIX-1 through FIX-8 are implemented exactly.
- [ ] `SUMMARY_REDUCER_VERSION == "0.3.0"`; config/summary schemas stay 0.1.
- [ ] D-057 adds exactly `nonpositive_window_duration` and
      `idle_baseline_unrecorded`.
- [ ] Existing reason spellings are unchanged.
- [ ] Old one-edge and new joint-edge fields are emitted; gates consume joint.
- [ ] Gross and idle-subtracted request prechecks are emitted; `request`
      remains deprecated.
- [ ] No total-token ratio is emitted without a runtime-observed total.
- [ ] Zero-MAD off-median values are review-flagged and kept in headline.
- [ ] Manifest replacement is same-directory atomic and does not claim resume.
- [ ] Unknown config keys warn with deterministic dotted paths.
- [ ] `warmup_seconds` executes outside the measured window without changing
      config hashes.
- [ ] Local cleanup status appears in measurement quality without changing
      current run status.
- [ ] Every mutation test is red-before/green-after.
- [ ] All six corpus bundles pass strict validation read-only with no bytes or
      mtimes changed.
- [ ] Focused tests and `python3 -m unittest discover -s tests` pass.
- [ ] No `[QUIET-MAC]` measurement or live hardware command is run.

## DEVIATIONS / OPEN QUESTIONS

1. **Generic request is not a gross gate.** The code exposes one ambiguous
   request gate rather than explicitly rejecting gross energy. The specified
   fix adds both metric-specific keys instead of silently changing the old key.
2. **D-057 amendment required.** Approve the two exact additive codes above.
3. **Deprecated `request` alias.** Recommendation: retain through v0.1 and
   remove only in v0.2.
4. **`warmup_seconds` disposition.** Recommendation: implement as
   post-warmup/pre-sampling settle. Deletion conflicts with D-029 hash
   stability and immutable corpus configs. If rejected, deletion requires a
   D-029 amendment and explicit hash migration.
5. **Reducer-version projection.** Recommendation: adopt the exact 0.2.0
   projection. Wildcard tolerance violates D-030; forced rewrites violate the
   requested read-only compatibility.
6. **Strict wording.** D-030 lets correctly stored failed bundles validate as
   failure records. This spec interprets “zero-window strict failure” as
   “cannot be a strict-valid succeeded measurement.” Making all zero-window
   failure records invalid would require a D-030 amendment.
7. **P2-016(i) conflict.** Its total-token `config fallback` naming request
   predates D-058. Mark that half superseded; output-token
   `token_counts_source=config_fallback` remains valid.
8. **D-053/D-054 scope.** LOO tables and executable floor comparisons remain
   P2-037/P2-039. FIX-5 provides only the P2-040 fallback flag assigned by
   C-027.

## CHECKS PERFORMED

- Read the P2-040 queue row, Do-Not-Do-Yet list, cleared stop card, current
  status/workspace/next-action sections, Mission M0, source-of-truth map, and
  relevant orchestration rules.
- Read C-027 review §3 and §7; lens-stats findings 5..8; lens-arch findings
  3, 5, 6, and 8.
- Read D-002, D-008, D-011, D-012, D-014, D-026..D-030, D-053, D-054, D-057,
  and D-058 plus the token-normalization, claims-ladder, detection-floor, and
  bundle contracts.
- Inspected the named reducer, aggregator, strict validator, manifest writer,
  schemas, controller cleanup/warmup, and behavior-locking tests.
- Confirmed all six `runs/*__r*` corpus bundles currently return an empty
  problem list from `validate_bundle(path, strict=True)` in a read-only pass.
- Confirmed all six cleanup streams record `cleanup_ok=true` and all six
  stored total-token sources are `runtime_observed`.
- Confirmed `sampling.warmup_seconds` occurs in active configs/templates but
  has no production reader.
- Confirmed the worktree is clean at `0a5c5e6`. Git emitted temporary-cache
  warnings because the sandbox cannot write `/tmp`; repository reads
  succeeded.
- No hardware, network, quiet-window measurement, code mutation, bundle
  rewrite, or full test suite was run during this design pass.
```