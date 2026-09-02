# 70h — Ruling: clause 4's divergence gate fired; the finalized arm records `floor_stack_identity`

Date: 2026-09-01. Sol xhigh stage-1 session (scratchpad `92-sol-closeout-s1b`)
stopped at the pre-registered gate in the S1 brief ("if the two builders
disagree, STOP and return NEEDS_RULING with both values") — the correct
behaviour, and the gate did what it was installed to do.

## The fact (verified by the seat on the synthetic finalizer fixture)

- `arms[].realized_stack_identity` is the SEVEN-field scientific identity
  (`joulewise/analysis_engine/inputs.py:2528`; keys `device_boundary, model,
  model_artifact, quantization, runtime, telemetry, tokenizer`), recorded at
  `joulewise/analysis_manifest_v3.py:3104`.
- `expected_stack_sha` is computed from the ELEVEN-field governed identity
  (`joulewise/identity_pins.py:250 build_stack_identity`; keys
  `batching_concurrency_policy, hardware_unit, kernel_library,
  measurement_boundary_label, model_artifact_sha256, os_version, quantization,
  runtime_version, sampler_output_policy, telemetry_backend,
  tokenizer_identity`) at `analysis_manifest_v3.py:3219`, hashed by
  `stack_identity_sha256`.
- The seven-field value cannot be hashed by `stack_identity_sha256`
  (`ValueError: stack identity must contain exactly the governed eleven
  fields`). 70c clause 4's "sha256 of the arm's `realized_stack_identity`
  computed the way the finalizer computes `expected_stack_sha`" was therefore
  unbuildable as written; the two objects were never the same identity.

## Ruling (clause 4, amended — supersedes the 70c/70g wording for this point)

**Option 1 adopted.** The finalizer records, on every dominance-enabled
finalized arm (same presence condition as `floor_cell_id`: every prospective
contrast's `floor_estimator_registration` carries the key
`dominance_criterion`, presence-only, outcome-blind), a new arm field
`floor_stack_identity` = the eleven-field identity returned by
`build_stack_identity(raw_config, metadata)` for the arm's members. The
finalizer already requires every member of an arm to agree on
`(telemetry_backend, stack_identity_sha256(stack))` (`:3225` `observed`
set) — record the single agreed identity; if the set has more than one
element the existing refusal fires first, so no new refusal is needed for
disagreement. Add `floor_stack_identity` to `ARM_KEYS` beside
`floor_cell_id`; both present or both absent.

The close-out recomputes `stack_identity_sha256(arms[].floor_stack_identity)`
and requires equality with the sealed floor cell's
`source_regime.stack_identity_sha256`, AND with the finalizer's own
`expected_stack_sha` for that arm (pre-registered acceptance test from the
S1 brief, now expressed over `floor_stack_identity` instead of
`realized_stack_identity`). `realized_stack_identity` is untouched.

**Why not the alternatives.** Option 2 (record only the sha) forfeits
independent recomputation — the close-out would compare a hash the finalizer
minted against a hash the floor minted with no bytes of its own to check,
which is the exact failure shape D-165 close-out exists to refuse. Option 3
(widen the seven-field identity) touches the forbidden
`analysis_engine/inputs.py`, changes legacy finalized bytes, and conflates two
identities that are different on purpose (scientific vs. runtime-governed).

**Legacy invariance (unchanged).** Prospective manifests without
`dominance_criterion` finalize byte-identical; the S1 brief's byte-unchanged
test now asserts the absence of BOTH `floor_cell_id` and
`floor_stack_identity` and an unchanged `manifest_id`.

**Mutation rows added to the S1 table:** (m7) finalizer records the
seven-field identity under `floor_stack_identity` → the recomputation test
fails with the eleven-field ValueError or a sha mismatch; (m8) close-out
skips the `expected_stack_sha` equality → the pre-registered acceptance test
fails.

This is a first ruling on a newly-fired gate, not a second fix round on the
same defect: no cold gate is triggered. The delta re-audit seat (different
model) is explicitly licensed to dispute option 1.
