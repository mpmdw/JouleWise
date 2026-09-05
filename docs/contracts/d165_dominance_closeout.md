# D-165 dominance replay and close-out contract

Status: stage-1 contract, 2026-09-01; semantic relabel updated 2026-09-05
under the ratified D-165 addendum. The two JSON schemas are
`joulewise.d165_dominance_replay.v1` and
`joulewise.d165_dominance_closeout.v1`.

This document defines every field that stage 1 reads or writes. A **cell** is
one model and one phase, for example the small model's decode phase. Each cell
has an **absolute component**, which measures repeated-run scatter within one
condition, and a **comparative component**, which measures A/B/B/A blocks. An
**A/B/B/A block** is four measurements ordered A1, B1, B2, A2; that order lets
the comparative estimator cancel a slow linear drift.

A **replay sidecar** (shortened to **sidecar**) is the separate JSON file that
holds the physical A/B/B/A operands needed to replay the common-mode result.
The **mint** (in full, the **stage-2 mint**) is the program, owed by the second
delivery stage (`D165-SIDECAR-EMIT-01`), that writes the sidecar from the floor
extractor's own block inputs at the moment the common-mode result is computed;
it is the only producer of a sidecar, and stage 1 defines its interface below.
The **close-out builder** is the function that reads the exact bytes of the
finalized manifest, floor artifact, and sidecar and produces the one decision
record defined below. **Lineage** is the chain of custody between those physical
files: each link names an identity and digest so a later reader can prove which
bytes fed the next link. A **census** is an exact, positioned, count-checked
comparison of two lists. For example, floor members `[A1=a, B1=b, B2=c, A2=d]`
and sidecar members `[A1=b, B1=a, B2=c, A2=d]` fail the census: the A1/B1 swap
preserves the member set and count but not the positioned list. **Neither
branch** is the fail-closed state used when the evidence cannot truthfully select
A or B: `branch` and both `all_*_pass` fields are null, both prose licenses are
false, and `refusal_reason` names the broken link.

An **ordinary dominance ratio**, written R, divides the corner-widened
unguarded floor by the point unguarded floor. A **corner** selects an allowed
low or high endpoint for every uncertainty. “Unguarded” means the small-sample
safety multiplier has not been applied. The registered predicate is R >= 2.0;
exact equality passes.

The comparative ratio R_cm is a **shared-energy-sign/local-corner sensitivity
diagnostic**. It holds one additive energy sign across every comparative block
and enumerates every combination of independent local energy signs. This does
not establish conservatism for physical common-time motion; passing the gate
licenses no physical timing-robustness claim. Absolute R_cm is the text value
`not_applicable`, never a number. Its registered rationale is:

> a uniform additive energy offset cancels from absolute residuals; no absolute common-time replay is implemented; absolute R_cm is not_applicable because the registered replay is comparative-only, not because absolute timing uncertainty vanishes

A **manifest attachment** is an evidence record inside the finalized manifest
that names an external file and seals its exact bytes with SHA-256, a 256-bit
content digest. The attachment lets the finalized manifest authenticate the
replay sidecar without copying its measurement operands into the manifest.

## Forcing problems and worked examples

Each mechanism exists because a simpler construction can state a result that
the physical files do not support:

| Mechanism | Forcing problem | Worked example |
|---|---|---|
| Ordinary R | A widened floor alone does not say whether attribution uncertainty dominates repeatability. | A 2.0 J corner-widened floor divided by a 1.0 J point floor gives R = 2.0 and passes; 1.5 J / 1.0 J gives R = 1.5 and selects B when every record is complete. |
| Shared/local split and replay | The diagnostic restricts the additive energy sign shared across blocks while enumerating independent local corners; it does not prove physical timing coverage. | Measured block `b01` has `delta_j = 0.21462565134537215`, `shared_width_j = 0.2617693341828027`, and `local_width_j = 0.048579253149402035`. With the authenticated `shared_edge_bound_s = 0.03678263869781979`, the two-block replay gives point 2.430576610260499 J, corner 8.830437643102993 J, and R_cm = 3.6330628731577335. |
| Attachment lineage | A sidecar identity without its bytes lets a different file reuse the name. | The worked sidecar is produced by `replay_sidecar` in `tests/test_d165_dominance_closeout.py:200`; its bytes hash to `cff755ba28175cff51bc47298ee97c97011444c8a7f2dd08de89d3216fe38500`. Reproduce the pinned digest with `TMPDIR=<scratch> python3 -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_worked_sidecar_digest_matches_contract_literal`; changing one operand changes the digest and yields `replay_sidecar_digest_mismatch`. |
| Exact census | Twelve plausible records can still omit a physical cell and duplicate another. | Cells `cell-decode-a`, `cell-decode-b`, `cell-prefill_p<N>-a`, and `cell-prefill_p<N>-b` must yield exactly eight ordinary slots (4 × 2 components) and four R_cm slots (4 × 1 comparative component). |
| Byte-only source custody | A parsed object and an authenticated byte string supplied through two channels can describe different artifacts. | A close-out built from sidecar bytes X must validate against X. If block 0's energy operands are multiplied by 0.9 and its split/result are recomputed into bytes Y, validation still refuses because X's stored file digest does not equal Y's digest, even though Y is internally consistent. |
| Manifest-sealed floor | A close-out canonical digest can authenticate a newly rendered floor Y while the finalized manifest separately seals floor X; both digests can be individually valid but authenticate different artifacts. | The worked manifest seals floor X as `5be2fdc561e93b40810d6707f531e1d8668f2a675586a2d6ddbeccbc4dbe8a8c`. Changing one corner from 2.0 J to 2.1 J produces floor Y at `39221b0503af3479db2bad595c2e7201a522b0e5e1dc4b426562e7b538854099`; the builder records `floor_artifact_source_hash_mismatch` and selects neither branch. |
| Exclusive output creation | Overwriting an older close-out destroys the physical record needed to explain a published decision. | If `closeout.json` already contains 1,024 bytes, `--output closeout.json` writes zero bytes and returns `output_already_exists`; the original 1,024 bytes remain. |

In the prefill cell names, N is fixed by the G2-a
`joulewise.prefill_prompt_pin.v2` record (512 for `_v5`; 256 was the `_v3`
value).

## Shared arithmetic

`joulewise.dominance_closeout.dominance_ratio` is the only production
implementation of R >= 2.0. It accepts the numerator
`corner_widened_unguarded_floor_j` and denominator
`point_unguarded_floor_j`. Both are finite, nonnegative numbers in joules. A
zero denominator raises `dominance_ratio_zero_denominator`; infinity and
not-a-number values are never emitted.

`joulewise.dominance_closeout.split_common_mode_block_width` is the only
production implementation that separates one comparative block's uncertainty
into `shared_width_j` and `local_width_j`. The calculation is the arithmetic
formerly written inside
`joulewise.floor_extraction._common_mode_block_half_width`: the same
`math.fsum`, extrema padding, four-step outward rounding, and residual sum are
preserved. Governed extraction calls the shared split and then performs its
unchanged outward-rounded final sum. Thus existing aggregate floors keep the
same meaning and bits while the two terms become available to the sidecar.

`joulewise.dominance_closeout.replay_common_mode_dominance` authenticates the
shared-edge bound, validates every four-member window, calculates every split,
holds one shared additive energy sign across the blocks, enumerates every local-sign
combination, and calls the existing comparative false-effect floor. A
false-effect floor is the smallest energy difference the registered noise
calculation can distinguish from zero. The supplied shared-edge bound must
match the authenticated bound with zero relative tolerance and an absolute
tolerance of exactly `1e-12` seconds. The exact-corner cap is exactly 16 blocks:
the implementation reads `MAX_EXACT_ADMISSIBLE_CORNER_N`, whose registered
value is 16, and rejects 17 or more.

For an ordinary point floor, the close-out builder calls
`joulewise.detection_floor._point_floor_diagnostic` on the floor artifact's
unconditional parents. It does not copy that function's maximum calculation.
The absolute parent is `max_abs_residual_j`; the comparative parent is
`max_abs_delta_j`; both use `prediction_component_j` as the other input.

## Replay sidecar: `joulewise.d165_dominance_replay.v1`

New replay sidecars are JSON objects with exactly these top-level fields:

| Field | Type | Meaning and producer |
|---|---|---|
| `schema_version` | string | Exact value `joulewise.d165_dominance_replay.v1`; the stage-2 mint writes it. |
| `rule_id` | string | Producer-declared replay era. New output must carry `d165_shared_sign_local_corner_replay.v2`. Historical v1 may explicitly declare `d165_shared_sign_local_corner_replay.v1`. |
| `sidecar_id` | nonempty string | Mint-issued identity for this replay sidecar. |
| `cells` | nonempty array of cell objects | One record for each cell emitted by the mint. The standalone validator permits a one-cell diagnostic sidecar; the close-out requires exactly the four floor cells. |

The historical producer shape has exactly `schema_version`, `sidecar_id`, and
`cells`. That original three-field shape declares the v1 era and remains readable
without rewriting its bytes. Its missing `rule_id` never means v2 or an era
inferred from a result. A present `rule_id` must be one of the two registered
strings; null, unknown values, and extra fields are invalid. The schema version
continues to identify the structural family; the producer declaration binds the
replay meaning within it.

Every comparative replay result must carry the sidecar's declared rule id.
`validate_d165_replay_sidecar` refuses a mismatch with the named error
`d165_replay_rule_era_mismatch` at the offending result's `rule_id`, including
when every result has been relabelled to the other era. A v2 result in the
historical three-field shape is also refused. This check uses producer metadata,
not agreement among result labels. The current builder always emits the explicit
v2 declaration, including for sidecars containing only default-estimator cells.

Each cell object has exactly `cell_id` (nonempty string), `absolute` (object),
and `comparative` (object). `cell_id` comes from the matching
`joulewise.detection_floor_artifact.v2` cell and must be unique.

### Independent ratio record

Both `absolute.independent` and `comparative.independent` have exactly these
fields:

| Field | Type | Unit | Meaning and source |
|---|---|---:|---|
| `status` | `complete` or `refused` | none | The stage-2 record builder sets `complete` after `dominance_ratio`; a zero point floor sets `refused`. |
| `ratio_id` | string | none | Exact value `attribution_dominance_ratio.v1`. |
| `point_unguarded_floor_j` | finite number | J | Produced through `_point_floor_diagnostic` from `max_abs_residual_j` plus `prediction_component_j` for absolute, or `max_abs_delta_j` plus `prediction_component_j` for comparative. |
| `corner_widened_unguarded_floor_j` | finite number | J | Copied from the matching floor-artifact component. |
| `ratio` | finite number or null | dimensionless | `dominance_ratio` output when complete; null when refused. “Dimensionless” means the joules in numerator and denominator cancel. |
| `threshold` | number | dimensionless | Exact value `2.0`. |
| `comparison` | string | none | Exact value `greater_than_or_equal`. |
| `passes` | Boolean or null | none | `ratio >= 2.0` when complete; null when refused. |
| `refusal_reason` | string or null | none | Null when complete; `dominance_ratio_zero_denominator` for the registered zero-denominator refusal. |

`absolute.common_mode` has exactly `status` and `reason`. `status` is
`not_applicable`. New output uses the comparative-only rationale returned by
`ABSOLUTE_COMMON_MODE_REASON` (quoted above). Declared v1 sidecars instead require
the exact `LEGACY_ABSOLUTE_COMMON_MODE_REASON` to keep historical bytes readable;
that withdrawn rationale is not the active physical interpretation. No numeric
R_cm field is allowed.

### Comparative estimator and common-mode replay

Every `comparative` object has exactly one of two shapes. A default-estimator
cell has exactly `independent` and `estimator`, with `estimator` equal to
`default`. A common-mode cell has exactly `independent`, `estimator`, and
`common_mode_replay`, with `estimator` equal to `common_mode`. A default cell
must not carry `common_mode_replay`, and a common-mode cell must carry it. The
schema version remains `joulewise.d165_dominance_replay.v1` because no
production sidecar was emitted before this exact shape was fixed.

For a common-mode cell, `comparative.common_mode_replay` has exactly `inputs`
and `result`.
`inputs` has exactly:

| Field | Type | Unit | Meaning and evidence |
|---|---|---:|---|
| `calibration_bracket` | object | mixed, internally suffixed | The authenticated calibration-bracket object used by `registered_common_mode_operative_bound`; it comes from the cell's mint evidence. |
| `calibration_bracket_sha256` | 64-character lowercase hexadecimal string | none | SHA-256 of the bracket's canonical JSON. SHA-256 is a 256-bit content digest; canonical JSON means UTF-8 JSON with sorted object keys, no insignificant spaces, and no non-finite numbers. |
| `shared_edge_bound_s` | finite positive number | s | The once-widened operative shared timing-edge bound. `registered_common_mode_operative_bound(calibration_bracket)` must reproduce it within the registered absolute tolerance. |
| `blocks` | array, length 1 through `MAX_EXACT_ADMISSIBLE_CORNER_N` | none | Raw replay inputs reconstructed by extraction from the authenticated bundle evidence. |

Every block has exactly these fields:

| Field | Type | Unit | Producer and evidence |
|---|---|---:|---|
| `block_id` | nonempty string | none | The authenticated extraction specification's block identity, unique within the floor cell. |
| `members` | object with exactly `A1`, `B1`, `B2`, `A2` | none | Positioned A/B/B/A member map copied from the authenticated extraction specification; each value is a nonempty bundle id. Position is semantic, so swapping A1 and B1 is not equivalent membership. |
| `delta_j` | finite number | J | The zero-shift A/B/B/A contrast from the authenticated block evidence. |
| `onset_sweep_j` | nonempty array of finite numbers | J | Energy contrasts obtained by replaying the registered onset-shift grid. |
| `offset_sweep_j` | nonempty array of finite numbers | J | Energy contrasts obtained by replaying the registered offset-shift grid. |
| `zero_point_contrast_j` | finite number | J | The explicitly evaluated zero-shift contrast; it must belong to both sweep arrays and agree with `delta_j` inside the registered provenance tolerance. |
| `bundle_residual_half_widths_j` | array of exactly four finite nonnegative numbers | J | One local residual half-width for A1, B1, B2, and A2, reconstructed from their authenticated bundle evidence. |
| `member_window_bounds_s` | array of exactly four `[start_s, end_s]` pairs | s | The four member phase-window bounds reconstructed from events; every interval must remain strictly noncollapsed after applying the authenticated shared-edge bound. |
| `member_envelope_integral_sum_j` | finite nonnegative number | J | Sum of the four member envelope integrals reconstructed from their power traces and uncertainty evidence. |
| `derived_split` | object | none | Output of `split_common_mode_block_width`; it has exactly the two fields below. |

`derived_split.shared_width_j` and `derived_split.local_width_j` are finite
nonnegative numbers in joules. The first is the excursion envelope used with
one shared additive energy sign across all blocks; it is not a claim that one
physical timing displacement produces those signed excursions. The second is
half the sum of the four bundle-local residual widths and gets an independent
energy sign in each block.

`result` has exactly:

| Field | Type | Unit | Producer |
|---|---|---:|---|
| `rule_id` | string | none | Must match the sidecar's producer-declared era: active output is `d165_shared_sign_local_corner_replay.v2`; historical v1 sidecars require `d165_shared_sign_local_corner_replay.v1`. Arithmetic is unchanged. |
| `point_unguarded_floor_j` | finite nonnegative number | J | `replay_common_mode_dominance`, using the block deltas with zero added widths. |
| `common_mode_corner_widened_unguarded_floor_j` | finite nonnegative number | J | `replay_common_mode_dominance`, taking the maximum floor over the shared/local sign enumeration. |
| `ratio` | finite nonnegative number | dimensionless | `dominance_ratio` over the preceding two fields. |
| `threshold` | number | dimensionless | Exact value `2.0`. |
| `comparison` | string | none | Exact value `greater_than_or_equal`. |
| `passes` | Boolean | none | True exactly when `ratio >= 2.0`. |

`validate_d165_replay_sidecar` rejects missing or extra keys, duplicate cell
or block identities, non-finite numbers, a block count above the named cap,
incorrect derived splits, a bracket digest mismatch, an unauthenticated bound,
invalid member windows, or a stored result that differs from a fresh replay.

### Stage-2 mint interface

**STAGE-2 mint interface (clauses 8 and 9):** the generalized authenticated
mint now captures the complete comparative recomputation at both the gate and
the evidence-binding pass. `bind_v2_floor_artifact_evidence` returns its
legacy evidence mapping together with that pass's recomputation record. The
four records are keyed by authenticated `cell_id` and compared byte-for-byte
with the gate records before any output write. A mismatch refuses
`d165_replay_recomputation_divergence`; a common-mode cell without the replay
output flag refuses `d165_replay_output_required_for_common_mode` at its first
selection. The gate recomputation runs once per cell and the binding
recomputation runs once per cell; sidecar assembly is after the four-cell
binding pass, so it cannot duplicate emission from either estimator call.

`joulewise.dominance_closeout.d165_replay_blocks_from_mint_inputs` is the only
sanctioned constructor for sidecar block records. It accepts exactly the four
values the mint holds at the call to
`floor_extraction._common_mode_floor_from_block_inputs`: the extraction-spec
block identities, the block deltas in joules, the extraction-owned
`_CommonModeBlockInputs` records, and the positioned member maps from the
authenticated extraction specification's `cell.blocks[].members`:

```python
def d165_replay_blocks_from_mint_inputs(
    block_ids: Sequence[str],
    block_deltas_j: Sequence[float],
    block_inputs: Sequence[_CommonModeBlockInputs],
    block_members: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    ...
```

The adapter checks aligned lengths, unique nonempty block identities, the
16-block cap, finite deltas, and every member map's exact positioned key and
nonempty-bundle-id census. An unhashable block identity, for example
`block_ids=[[]]`, is caught at this entry boundary and becomes
`closeout_input_malformed: replay.block_ids`; Python's incidental `TypeError`
does not escape. The adapter copies all six numeric fields held by each
`_CommonModeBlockInputs` record together with the spec-supplied A/B/B/A member map, adds
`block_id` and `delta_j`, and computes `derived_split` through
`split_common_mode_block_width`. `_raw_replay_block` deliberately omits
`members`: membership is identity evidence, while the arithmetic replay
consumes only the extraction-owned numeric projection. Stage 2 may wrap those
records with the cell's independent records, authenticated bracket, bound,
result, `schema_version`, and `sidecar_id`; it may not hand-build or rewrite a
block record. Sidecar emission itself remains a separate mint stream and does
not change the floor-artifact schema.

The sidecar's block `inputs` are trusted from this sole producer and replayed;
the close-out does not re-derive them from bundle files. Under D-161's
operator-only adversary model, their physical correctness rests on the
stage-2 per-cell recomputation-divergence check and on byte identity between
the validated producer output and the manifest-sealed sidecar.

The v2 CLI accepts optional `--d165-replay-out`. It is optional to parse but
not optional for a mint whose first authenticated common-mode cell selects
the registered estimator. Supplying it to a v2 mint with no common-mode cell
refuses `d165_replay_output_unused_without_common_mode`. The floor, statement,
and sidecar destinations are all checked for collisions and pre-existing
files before the first exclusive write. They are then written as one
transactional sequence; a later write failure removes the floor and
statement already written by that sequence. The floor payload and statement
renderer remain the legacy outputs, and the sidecar is the only new file.

### Finalized-manifest attachment

`prospective_finalization_required_attachments` retains the four legacy rows
by default and accepts an explicit optional-role argument. The existing
required-role/schema constants are not widened. The single presence-only
predicate `_dominance_floor_identity_enabled` governs the optional role: a
prospective manifest with `dominance_criterion` in every contrast must declare
exactly five rows, including `dominance_replay_sidecar`; criterion-present
without that row refuses as
`analysis_prospective_dominance_replay_attachment_missing`. Legacy D-134-form
four-row packs (no `dominance_criterion`) still validate and finalize
byte-identically; pre-D-134 packs (`as_generated_pre_d134_freeze`) are outside
the promise and are retired by D-167.

Finalization requires the sidecar path under that same predicate and seals its
path, file hash, schema, and sidecar identity. Omitting it refuses as
`analysis_finalization_attachment_missing`; supplying it to a legacy
prospective refuses as `analysis_finalization_attachment_invalid`. An invalid
sidecar schema or identity uses that same invalid-attachment refusal. A
finalized manifest without the role is nevertheless fail-closed at its
consumer: the close-out refuses it as `manifest_lacks_replay_sidecar`. When
present, `dominance_replay_sidecar` has exactly these fields:

| Field | Type | Meaning |
|---|---|---|
| `path` | nonempty string | Manifest-relative path to the replay-sidecar file. |
| `sha256` | 64-character lowercase hexadecimal string | SHA-256 of the replay-sidecar file bytes, not its re-rendered JSON. |
| `schema_version` | string | Exact replay-sidecar schema version. |
| `sidecar_id` | nonempty string | Exact replay-sidecar identity. |

Producer→finalizer sidecar custody is unproven until
`D165-SIDECAR-EMIT-01` lands; the paper cannot cite a close-out before then.

When every prospective contrast's floor-estimator registration carries the
`dominance_criterion` key, each finalized `arms[]` record also carries the
presence-coupled pair `floor_cell_id` and `floor_stack_identity`.
`floor_stack_identity` is the eleven-field governed identity returned by
`build_stack_identity` for that arm's authenticated bundle members. For an
`exact_stack_only` arm whose finalizer selector resolves exactly one eligible
sealed floor cell, `floor_cell_id` is that cell's `cell_id`; otherwise
`floor_cell_id` is null. Legacy prospective manifests gain neither field and
finalize to the same bytes and `manifest_id` as before. The finalizer does not
read the `dominance_criterion` value.

In `joulewise.identity_pins.STACK_IDENTITY_FIELDS` order, the eleven
`floor_stack_identity` fields are `hardware_unit`, `os_version`,
`runtime_version`, `kernel_library`, `model_artifact_sha256`, `quantization`,
`tokenizer_identity`, `sampler_output_policy`, `batching_concurrency_policy`,
`measurement_boundary_label`, and `telemetry_backend`; they are the complete
runtime-governed identity required by `stack_identity_sha256`, so dropping any
one cannot stand in for this object.

The distinct seven-field `realized_stack_identity` contains `device_boundary`,
`model`, `model_artifact`, `quantization`, `runtime`, `telemetry`, and
`tokenizer`, as built by
`joulewise.analysis_engine.inputs.realized_scientific_identity`; it cannot
stand in because it is a scientific cross-block identity and is rejected by
the eleven-field `stack_identity_sha256` schema.

The close-out maps each contrast arm through `arms[].floor_cell_id`; null is
the named stop `floor_cell_unresolved`. It then rechecks that the named sealed
floor cell has the arm's `condition_family_id` and
`condition_family_sha256`, has `eligibility.claim_usable` exactly true, and
has `source_regime.stack_identity_sha256` equal to the SHA-256 derived from
the arm's `floor_stack_identity` by `stack_identity_sha256`. This recomputed
value is the finalizer's bundle-derived `expected_stack_sha`; it must equal the
sealed floor cell's value. The seven-field `realized_stack_identity` remains
unchanged and is not accepted in its place. A resolved sidecar cell whose
`comparative.estimator` is not `common_mode`, or which has no replay, stops
with `cell_not_common_mode`.

For every sidecar cell whose `comparative.estimator` is `common_mode`, the
close-out binds each sidecar block by `block_id` to the sealed floor cell's
`comparative.blocks[]`. `n_blocks` is the floor comparative record's integer
count of A/B/B/A blocks. Both sides must contain exactly `n_blocks` unique
block ids, with no absent, extra, or duplicated id. For each
matched block, the positioned `members` maps must agree exactly at A1, B1, B2,
and A2 after projecting each sealed floor member row to `position` →
`bundle_id`, and `delta_j` must agree under the registered
`joulewise.detection_floor._close` tolerance: for expected value `x`, absolute
error is at most `min(max(1e-12, 1e-12 * abs(x)), 1e-6)` joules.
Any mismatch stops with `floor_member_census_mismatch`. The manifest's
contrast block namespace is not used for this census.

## Byte-only builder, validator, and command line

The Python API has one source channel. It never accepts a decoded manifest,
floor, or sidecar object alongside separately authenticated bytes:

```python
build_d165_dominance_closeout(
    finalized_manifest_bytes: bytes,
    floor_artifact_bytes: bytes,
    replay_sidecar_bytes: bytes,
) -> dict[str, Any]

validate_d165_closeout(
    value: Mapping[str, Any],
    *,
    finalized_manifest_bytes: bytes,
    floor_artifact_bytes: bytes,
    replay_sidecar_bytes: bytes,
) -> list[str]
```

Both functions decode all three UTF-8 JSON objects internally. The forcing
problem is the split-channel pair in the worked table: authenticating bytes X
while calculating from object Y would let Y license A without ever appearing
in the authenticated file. With one channel, calculation and authentication
necessarily consume the same decoded bytes.

After decoding, both entry paths perform their census and block-membership
computations inside one `TypeError` boundary. A malformed source set records
`closeout_input_malformed: source.census_or_block_membership`; a malformed
close-out record census records
`closeout_input_malformed: closeout.independent_ratios`. For example,
`contrasts[0].block_ids=[[]]` cannot be hashed, so the builder emits the first
reason with neither branch selected instead of crashing. Likewise, replacing
one close-out `component` string with `[]` requires the second reason and the
same neither-branch fields.

The floor byte check is independent of the close-out's canonical JSON source
reference. The builder and validator hash `floor_artifact_bytes` exactly as
read and compare that value with
`finalized_manifest.evidence.aggregate_floor_artifact.sha256`. The two-digest
forcing problem is concrete: without this comparison, the manifest can
correctly authenticate floor X while `closeout.sources.floor_artifact`
correctly authenticates a different floor Y. A mismatch records
`floor_artifact_source_hash_mismatch` before an operand-alignment message, so
the refusal says the supplied floor is not the artifact the manifest sealed.

The runnable command is:

```text
python3 scripts/build_d165_dominance_closeout.py --finalized-manifest … --floor-artifact … --replay-sidecar … [--output …]
```

The command reads each named file once as bytes and passes only those three
byte strings to the builder. Without `--output`, it prints the close-out to
standard output. With `--output`, it creates the named file exclusively. If
that path already exists, it preserves the existing bytes, writes no close-out,
returns exit status 2, and prints the named refusal `output_already_exists`.

## Close-out: `joulewise.d165_dominance_closeout.v1`

The close-out is a JSON object with exactly these top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | Exact value `joulewise.d165_dominance_closeout.v1`. |
| `sources` | object | SHA-256 bindings for the finalized manifest, floor artifact, and replay sidecar. |
| `finalized_manifest_sha256` | 64-character lowercase hexadecimal string | SHA-256 of the exact finalized-manifest file bytes supplied to the builder. |
| `replay_sidecar_sha256` | 64-character lowercase hexadecimal string | SHA-256 of the exact replay-sidecar file bytes supplied to the builder. |
| `independent_ratios` | array of exactly eight records | Four cells times absolute and comparative components. |
| `comparative_common_mode_ratios` | array of exactly four records | One comparative R_cm slot for each cell; there are no absolute R_cm records. |
| `all_independent_pass` | Boolean or null | True only when all eight completed ordinary ratios pass; false when all complete and at least one fails; null on a stop. |
| `all_required_common_mode_pass` | Boolean or null | True only when all four completed comparative R_cm values pass; false when all complete and at least one fails; null on a stop. |
| `branch` | `A`, `B`, or null | Branch A, branch B, or neither branch after a stop. |
| `dominance_sentence_licensed` | Boolean | True only in branch A. “Licensed” means downstream prose is allowed to print the sentence. |
| `subtitle_licensed` | Boolean | True only in branch A. |
| `refusal_reason` | nonempty string or null | First deterministic stop reason, or null for branches A and B. |

`sources` has exactly `finalized_manifest`, `floor_artifact`, and
`replay_sidecar`. Each source reference has exactly:

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | The source's exact schema version. |
| `identity` | nonempty string | `manifest_id`, `artifact_id`, or `sidecar_id`, respectively. |
| `canonical_json_sha256` | 64-character lowercase hexadecimal string | SHA-256 of the complete source object's canonical JSON. `validate_d165_closeout` decodes the three required byte strings internally and recomputes every digest. |

The two top-level file-byte digests intentionally complement these canonical
JSON source references: `validate_d165_closeout` always rechecks the required
manifest and sidecar bytes, so whitespace, order, or content drift in a
committed fixture is not silently accepted. The floor's exact file bytes are
bound by the finalized manifest's aggregate-floor attachment as described
above.

Every `independent_ratios[]` record is the sidecar independent-ratio record
plus `cell_id` and `component`. `component` is `absolute` or `comparative`.
The census must contain each of the four cell identities exactly twice, once
per component. The close-out builder reads the operands again from the floor
artifact rather than trusting the sidecar copy.

Every `comparative_common_mode_ratios[]` record has exactly:

| Field | Type | Unit | Meaning |
|---|---|---:|---|
| `cell_id` | nonempty string | none | Matching floor and sidecar cell. |
| `component` | string | none | Exact value `comparative`. |
| `status` | `complete` or `refused` | none | Whether the required replay result exists and is authenticated. |
| `ratio_id` | string | none | Exact value `attribution_dominance_ratio_common_mode.v1`. |
| `point_unguarded_floor_j` | finite number or null | J | Sidecar replay point floor when complete; null when refused. |
| `common_mode_corner_widened_unguarded_floor_j` | finite number or null | J | Sidecar common-mode corner floor when complete; null when refused. |
| `ratio` | finite number or null | dimensionless | R_cm when complete; null when refused. |
| `threshold` | number | dimensionless | Exact value `2.0`. |
| `comparison` | string | none | Exact value `greater_than_or_equal`. |
| `passes` | Boolean or null | none | `ratio >= 2.0` when complete; null when refused. |
| `refusal_reason` | string or null | none | Null when complete; a named stop reason when refused. |

## Branch and stop rules

Branch A requires all eight ordinary ratios and all four comparative R_cm
values to be complete and at least 2.0. Both prose licenses are true.

Branch B requires all twelve values to be complete and at least one value to
be below 2.0. Both prose licenses are false. A completed mix of passing and
failing cells therefore selects B, not a stop.

The neither branch is selected when a result cannot be
truthfully completed. The
builder sets both `all_*_pass` fields and `branch` to null, both licenses to
false, and `refusal_reason` to the first deterministic reason. Stop conditions
are:

- a zero ordinary or comparative denominator;
- a missing, duplicate, or extra sidecar cell relative to the four floor
  cells;
- missing or extra schema keys;
- a non-finite physical value or ratio;
- a bracket digest mismatch or an unauthenticated shared-edge bound;
- a derived split or replay result that does not reproduce;
- any of the three close-out source identities or SHA-256 digests failing to
  match the supplied source object.
- `manifest_lacks_replay_sidecar`: `evidence.dominance_replay_sidecar` is
  absent or lacks one of `path`, `sha256`, `schema_version`, or `sidecar_id`.
- `replay_sidecar_digest_mismatch`: the supplied replay-sidecar file bytes do
  not hash to the attachment's `sha256`.
- `replay_sidecar_identity_mismatch`: the attachment's `sidecar_id` or
  `schema_version` differs from the replay sidecar's own field.
- `floor_member_census_mismatch`: a sidecar cell's block count, unique
  extraction-spec block-id census, positioned member map, or `delta_j` differs
  from its sealed floor comparative block census.
- `floor_cell_unresolved`: a contrast arm has a null or unusable finalized
  `floor_cell_id`, lacks its presence-coupled eleven-field
  `floor_stack_identity`, or fails the sealed floor-side selector recheck.
- `cell_not_common_mode`: a resolved floor cell or its sidecar cell lacks the
  required common-mode replay shape.
- `finalized_manifest_id_mismatch`: the supplied UTF-8 JSON bytes are decoded
  into a finalized-manifest mapping, and `manifest_id` is not the value
  recomputed from that decoded mapping by
  `analysis_manifest_v3.calculate_manifest_id`.
- `floor_artifact_source_hash_mismatch`: the supplied floor bytes differ from
  the aggregate floor artifact sealed by the finalized manifest.
- `closeout_input_malformed`: an arms or floor-cell structure needed for floor
  binding is malformed rather than merely unresolved, including a floor `cells`
  array that is not a list of exactly four unique cell objects.
- `closeout_input_malformed: source.census_or_block_membership` or
  `closeout_input_malformed: closeout.independent_ratios`: an unhashable JSON
  element prevents a required set/map census at the named entry path.

**Refusal precedence.** After the byte-to-mapping decode, source checks run in
this order: finalized-manifest mapping type; `manifest_id` presence and
recomputation with `calculate_manifest_id`; the remaining finalized-manifest
fields; floor schema and artifact identity; manifest-sealed floor-byte digest;
sidecar attachment presence, digest, and identity; sidecar schema and replay;
floor/sidecar cell alignment; contrast-arm floor binding; and finally the
positioned, count-checked floor-member census. A non-mapping manifest cannot be
hashed, so its mapping-type failure necessarily comes first. Otherwise,
`finalized_manifest_id_mismatch` masks every later refusal: no field of an
unauthenticated manifest is read as authority. The code accumulates reasons and
surfaces only the first reason in this order. Only after these source checks does
the builder compute the eight ordinary and four common-mode records and their
close-out census.

Each named attachment failure is a stop: it selects neither branch, leaves both
prose licenses false, and records that exact name as `refusal_reason`.

A floor artifact with other than four unique complete cells, where each complete
cell carries the `absolute` and `comparative` components the builder reads,
cannot support the required eight-record ordinary census. The source
precondition is `closeout_input_malformed`; this is a neither-branch stop, not
branch B.

When the floor cannot support the twelve-record census, or a source's
schema/identity reference cannot be formed, the builder writes no close-out: the
CLI exits 2 and prints `d165_dominance_closeout_refused: <reason>` where
`<reason>` is the same first precedence-ordered stop reason a refusal record
would have carried. A refusal record is written only when all twelve records can
be truthfully built.

`validate_d165_closeout` decodes its three required source-byte arguments, then
rejects missing or extra keys, a census other than
eight ordinary plus four comparative common-mode records, non-finite completed
values, inconsistent ratios or pass flags, incorrect branch fields, source
operand/result drift, a canonical source-hash mismatch, a manifest or sidecar
file-byte digest mismatch, or a floor byte digest different from the one sealed
by the manifest. Validation is fail-closed: an empty error list is required
before a close-out can be consumed.
