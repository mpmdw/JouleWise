# Paper claim-side deterministic widening (D-178)

Status: adopted, 2026-09-08. Schema: `joulewise.claim_side_bound.v2`.
Owner: `joulewise/analysis_engine/claim_side_bound.py`. This contract governs
copying and checking estimator provenance; it grants no paper placement.
X6/X7 remain `PROPOSED_STOP_FILL`. Their renderer follows S2 in a later seat.

## Quantity and symbols

For an absolute paired-energy contrast, let n be the number of included
complete blocks, i index those blocks, and k index the recorded deterministic
kinds. Let a_ik and b_ik be the nonnegative arm bounds for kind k in block i,
and c_ik its optional explicitly recorded contrast bound. Define

```text
d_ik = c_ik, if recorded; otherwise a_ik + b_ik
B_k  = (1/n) sum_i d_ik
B    = sum_k B_k
I    = [L, U] = estimator.metrology_aware_CI95
D    = [L - B, U + B] = deterministic_bounds.decision_interval
```

`estimate_paired_blocks` owns that construction and `PairedEstimate` carries
its results; `claim_verdicts.json` is the serialized authority. B is the
complete deterministic widening, not the anchor component alone. The named
components can include interpolation, idle drift, clock-anchor movement and
whole-window drift. Their complete recorded list travels with B, including
`E_clock_anchor_shift_bound_j` (required even when its bound is zero).

For `mean_of_request_ratios` and `ratio_of_totals`, the corresponding existing
ratio estimator owns normalization/propagation and serializes B and I/D in
the author-supplied B8 metric unit `J/token`. The formulas above define the
absolute-energy estimator, not a new ratio estimator. S3 performs no division by tokens and no estimator arithmetic.
The meanings and algorithms remain in `analysis_engine/estimators.py` and the
[comparison protocol](../paper/protocol/prospective-comparison-protocol.md).
Term-sum and interval arithmetic validation belong to `validate_claim_verdicts`.

## Closed wire and copy rules

The top-level object has exactly `schema_version`, `claim_verdicts_sha256`
(lowercase SHA-256 of the exact verdict bytes), and `contrasts` (nonempty list).
Rows appear in verdict order, one for every verdict contrast. Each row has
exactly these fields:

| Field | Authority / rule |
|---|---|
| `contrast_id` | Verdict contrast ID; nonempty string, unique, registered in finalized manifest |
| `source_cell_ids` | Ordered concatenation defined below |
| `floor_artifact_id` | Supplied authenticated floor artifact's nonempty `artifact_id` |
| `deterministic_widening_total` | Copy of verdict `deterministic_bounds.total`, finite nonnegative JSON number |
| `unit` | Copy of verdict `metric.unit`; B8 verdict metric vocabulary owned by `ratio.validate_metric_unit_and_ratio`: `J` with null ratio or `J/token` with an exact valid B8 mapping |
| `estimator_id` | Copy of verdict `estimator.name`, nonempty string; owner validates registration |
| `ratio_estimand` | Verbatim object copy of verdict `metric.ratio_estimand`; null for absolute J contrasts. Any per-token unit (`unit != "J"`) requires the exact six-key B8 mapping checked by the shared unit/ratio validator through `ratio.validate_ratio_estimand`: `form`, `numerator_metric`, `denominator`, `denominator_unit`, `tokenizer_scope`, `output_policy_scope`. Estimand kind is read from `["form"]` (`mean_of_request_ratios` or `ratio_of_totals`), never a bare string |
| `deterministic_terms` | Exact ordered copy of verdict `deterministic_bounds.terms`: nonempty list of exact `{name, bound}` objects; unique nonempty names and finite nonnegative numeric bounds |
| `metrology_aware_CI95` | Copy of verdict `estimator.metrology_aware_CI95` |
| `decision_interval` | Copy of verdict `deterministic_bounds.decision_interval` |

The B8 manifest author supplies `metric.unit`; `analysis_manifest.py` requires
`J/token` for ratio estimands and `J` with null ratio for absolute contrasts.
S3 copies accepted units verbatim. The AP-SPEC v2 estimand units
`J/committed_output_token` and `J/accepted_draft_token` belong to the separate
v2 manifest path rejected by `analyze-claims`; there is no AP-SPEC-to-B8 unit
conversion. Those units, invented units, empty/non-string units, `J` with a
ratio mapping, and `J/token` with null ratio all refuse with
`paper_claim_side_bound_unit_mismatch`.

Each interval is exactly `{lower, upper}`, finite JSON numbers, lower ≤ upper.
Booleans, null numeric fields, numeric strings, NaN/infinity, duplicate object
keys, extra/missing keys and v1 sidecars refuse. This is never issued under v1.
Any per-token quantity (`unit != "J"`) under `claim_side_bound_j` or any
substitute J-typed `_j`/`_J` row key refuses the closed schema; changing its
unit to J also refuses. The closed schema disallows these substitute keys
for absolute quantities too; no renderer or J-typed placement is added here.

Equality of every copied numeric field means **the identical JSON numeral
bytes**, including exponent spelling, trailing zeros and signed zero. `4`,
`4.0`, and `4e0` are distinct tokens. Decimal values that round to the same
binary float are still distinct. Object whitespace/key order need not match;
list order and all copied values must match. Parsed mappings are not accepted
by the producer's verdict argument or either validator byte argument.

The parser preserves numeral tokens; serialization emits them unchanged.
The producer emits compact JSON with the listed insertion order and a trailing
newline, deterministically. No CI ± B computation takes place in production
or validation. In particular D may never be fed back as I and widened again.
Optional `claim_side_bound_diagnostics` uses `fsum`/`isclose` with relative and
absolute tolerance 1e-12 solely to describe arithmetic discrepancies. Neither
its success nor its failure participates in validation or grants.

## Join

For each contrast, traverse `claim_verdicts.contrasts[].floor.resolutions` in
recorded order, then each resolution's `source_cell_ids` in recorded order.
Every status must be `exact` or `transported`; every resolution has a nonempty
list of distinct cells present in `floor_artifact.cells[].cell_id`; `exact`
has one cell. Concatenate without sorting or deduplicating. A cell repeated in
different resolutions remains repeated. Injectivity is keyed on
`(estimand kind, ordered cell list)`, with null kind for absolute J and
`ratio_estimand["form"]` for per-token contrasts. Refuse two contrast IDs only
when both kind and the complete ordered concatenation coincide. An absolute-J
contrast and its per-token companion may share cells: they describe different
estimands over the same arms. Different ratio forms may likewise share cells;
a different unit alone does not exempt a duplicate kind/cell pair.

The finalized v3 manifest registers contrast IDs and
`floor_estimator_registration`; it does **not** have a contrast-level
`source_cell_ids` key. S3 neither adds that key nor changes the manifest schema.
The verdict owner checks the manifest-to-resolution semantics upstream.

## API, custody roles and refusal boundary

```python
raw = produce_claim_side_bound(verdict_bytes,
    finalized_manifest=validated_manifest, floor_artifact=authenticated_floor)
codes = validate_claim_side_bound(raw, claim_verdicts_raw=verdict_bytes,
    finalized_manifest=validated_manifest, floor_artifact=authenticated_floor)
```

The producer returns bytes or raises `ClaimSideBoundRefusal` with `.code`.
The validator returns a tuple of private diagnostics (empty means copy-valid).
Neither operation authenticates files, reads paths, nor makes an issuance
claim. Inputs must have passed their owning validators before production use.
A verdict with absent numerical results or unusable resolutions cannot produce
a sidecar; that refusal is not an empirical negative result.

[Paper supply custody](paper_supply_custody.md) owns the authenticated inputs:
`CLAIM_VERDICTS`, `CLAIM_SIDE_BOUND`, `FINALIZED_MANIFEST`, `FLOOR_ARTIFACT`,
`FLOOR_ACCEPTANCE`, their inventory, receipt and authenticated source census.
`claim-evidence.v1` is registered through this producer's validator. The gate
validates the disk manifest and verdict owner, compares the sidecar to a fresh
producer projection of the exact authenticated verdict bytes, checks embedded
floor byte equality and the accepted floor, then reruns `evaluate_claim` using
**only verdict fields**. Per-subject current/confirmatory/outcome/L2 grant rules
remain owned by the custody seam. Sidecar values never enter `evaluate_claim`.
The census pins the producer, validator and complete module (including parser,
serializer, helpers and constants). Changing them invalidates old receipts.
No supply role is promoted from fixture mode and no renderer is added here.

| Private refusal code | Trigger |
|---|---|
| `paper_claim_side_bound_shape_invalid` | Invalid bytes/schema/types/keys/numbers/intervals or incomplete source shape |
| `paper_claim_side_bound_numeral_unparseable` | A source numeral exceeds Decimal's representable exponent range (including `0e9999999999999999999` and `1e-9999999999999999999`); producer raises the structured refusal and validator returns it |
| `paper_claim_side_bound_reader_digest_mismatch` | Sidecar digest differs from raw verdict SHA-256 |
| `paper_claim_side_bound_contrast_mismatch` | Unregistered/duplicate source ID, or sidecar ID/order/coverage differs |
| `paper_claim_side_bound_cell_mismatch` | Invalid/refused resolution, wrong floor cell, or changed ordered concatenation |
| `paper_claim_side_bound_join_not_injective` | Two verdict contrasts share both estimand kind and ordered concatenation |
| `paper_claim_side_bound_lineage_mismatch` | Sidecar names a different floor artifact |
| `paper_claim_side_bound_unit_mismatch` | Unit/ratio disagreement or sidecar unit/estimand/estimator differs from verdict |
| `paper_claim_side_bound_anchor_missing` | Verdict terms lack the required anchor kind |
| `paper_claim_side_bound_copy_mismatch` | A bound, component, or interval differs, including numeral spelling |

`paper_claim_side_bound_arithmetic_diagnostic` is diagnostic-only, not a
refusal. These private codes are not professor-facing empirical sentences.

## Clause-to-test map and counterfactuals

Tests are `tests.test_claim_side_bound.ClaimSideBoundTests` unless noted.
Each mutation begins with an accepted copy control, then alters one boundary.
`tests/fixtures/paper_custody/run_kills.py --s3` independently removes the
relevant check (or corrupts the producer) and requires an assertion failure;
an import error or unrelated exception is not counted as a kill. The runner
executes **21 mutations over 10 distinct guards** (including two producer
sites). Eleven mutations share the exact-copy guard and two share the ordered
cell-copy guard; the count describes data coverage, not 21 independent guards.

| Mutation / counterfactual without the guard | Regression |
|---|---|
| Anchor alone (1) would replace B (4) | `test_anchor_only_substitution` |
| A kind could disappear while B stayed fixed | `test_dropped_kind` |
| Block sum (8) would replace mean-based B (4) | `test_sum_for_mean` |
| Arm bounds would override explicit contrast bounds (18 vs 4) | `test_precedence_flip` |
| D would masquerade as I | `test_decision_fed_as_ci95` |
| D would be expanded a second time by B | `test_double_widen` |
| Edited D and matching edited B would pass coherent arithmetic | `test_edited_interval_matching_scalar` |
| CI and decision endpoints could both be shifted coherently | `test_ci_recomputed_from_decision` |
| 1e-13 scalar drift would pass tolerance | `test_drift_1e13` |
| Wrong expansion sign would pass | `test_sign_flip` |
| Reordered or deduplicated cell lists would pass | `test_permuted_cells`, `test_deduplicated_cells` |
| Cells from a refused resolution would pass | `test_refused_resolution` |
| Missing anchor would produce a sidecar | `test_anchor_required` |
| Contrasts of the same estimand kind could alias the same ordered join | `test_join_injective` |
| A B8 per-token metric would be labelled J or placed in a J-typed cell | `test_ratio_in_j_cell` |
| Absolute/per-token companions or different ratio forms would be incorrectly refused | `test_companion_estimands_share_ordered_cells` |
| Removing only unit membership admits invented/AP-SPEC units with valid mappings; bare/incomplete B8 estimands could pass | `test_b8_unit_vocabulary_through_both_apis`, `test_ratio_requires_exact_b8_object` |
| Extreme exponents would leak `decimal.InvalidOperation` through either API | `test_extreme_exponents_refuse_through_both_apis` |
| Boolean would serve as a numeric bound | `test_bool_rejected` |
| Float normalization would erase byte-level drift | `test_numeral_bytes_not_numeric_equality` |
| Producer could substitute anchor for total | `test_copy_only_control` |
| Ready flag could issue unsupported or demoted subjects | `tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast` |
| A rounded negative bound or reversed high-precision interval could pass | `test_source_number_domains_do_not_round_before_validation` |
| Sidecar changes could reach claim reevaluation | `test_gate_reevaluates_verdicts_with_real_copy_validator` (upstream custody boundaries mocked) |

Synthetic controls establish software behavior only; no live gate is claimed.

## Follow-ups

- `UNIT-VOCAB-SHARED-01`: Wire `ratio.validate_metric_unit_and_ratio` into manifest and verdict validation; their acceptance is unchanged in S3.
