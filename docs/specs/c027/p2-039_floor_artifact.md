# P2-039 Executable Detection-Floor Artifact Specification

Status: ADJUDICATED 2026-07-09 (C-028) — rulings in `ADJUDICATION.md` in this directory AMEND this spec wherever they conflict with its body text

## 1. Purpose, authority, and outcome

P2-039 turns the accepted D-054 false-effect guard into a deterministic,
versioned artifact that P2-015 can produce and the future P2-037 claim engine
can consume. It is an `[AGENT]` prerequisite: P2-015 may run its named SMOKE
preconditions, but it must not collect claim-facing floor cells until this
spec's guard rule and artifact contract have been lead-adjudicated and landed.

**Validator boundary (v1).** The v1 validator validates schema, arithmetic re-derivation, identity-hash recomputation, and claim-readiness invariants; it does not yet bind source provenance to actual bundle bytes or the frozen campaign order log. That binding lands with the typed loader in the pre-P2-015 integration unit, and until then floor artifacts are not claim-consumable. The existing fences remain: no CLI integration and no `reduce.py` hooks.

Authority, in descending order for this specification:

1. D-054 and its 2026-07-09 C-027 amendment in `docs/decision_log.md`.
2. The P2-039 and P2-015 rows in `TASK_QUEUE.md`.
3. `docs/phase_2/detection_floor.md`, especially its estimator, economics,
   condition mapping, comparative-floor, and error-budget sections.
4. Accepted C-027 dispositions STA-4 and RIG-6, including
   `docs/reviews/c027/lens-stats.md` finding 4 and
   `docs/reviews/c027/lens-rigor.md` finding 6.
5. D-062 for pre-data freezing, technical replacement, and no
   outcome-dependent confirmatory top-ups.

This specification makes six binding implementation choices, subject only to
lead adjudication of this DRAFT:

1. The small-sample multiplier is
   `g(n) = max(1, sqrt(9 / (n - 1)))`; it is 1.5 at `n=5` and 1.0 at
   the default target `n=10`.
2. The output schema is `joulewise.detection_floor_artifact.v1`; it contains
   one claim-facing cell per
   `backend x metric x window_class x condition_family`, with both floor
   components, complete source hashes, calculation records, regime evidence,
   and a named transport group.
3. An ABBA block delta is
   `delta_b = ((B1 + B2) - (A1 + A2)) / 2`, in joules and signed `B - A`.
4. A floor never transports across a different stack identity. Within one
   exact stack it may transport only through a predeclared group whose
   measured power and duration ranges bracket the consumer and whose cadence,
   observer, interpolation, and drift evidence is at least as adverse as the
   consumer's. All source-cell maxima are composed, even when they come from
   different cells.
5. Reusable math, schema validation, artifact loading, and floor resolution
   live in `joulewise/detection_floor.py`; `joulewise/cli.py` supplies a thin
   `floor-artifact` command group. No calculation logic lives in `scripts/`.
6. P2-037 receives a validated `FloorResolution`; it does not parse arbitrary
   artifact JSON or select a floor row itself.

## 2. Normative estimator and frozen small-sample guard

### 2.1 Absolute false-effect floor

For `n` strict-valid, bundle-clustered scalar observations `E_i` in one exact
cell:

```text
E_bar              = sum(E_i) / n
r_i                = E_i - E_bar
s_r                = sample_standard_deviation(r_i), denominator n - 1
prediction_abs_j   = t_0.975,n-1 * s_r * sqrt(1 + 1/n)
unguarded_abs_j    = max(max_i(abs(r_i)), prediction_abs_j)
floor_abs_j        = g(n) * unguarded_abs_j
```

The implementation must reuse the existing stdlib-only
`joulewise.aggregate.student_t_critical_95` table. The calculation record must
store the actual critical value used. No intermediate value is rounded;
rendering may round, but the JSON number is the binary64 result serialized by
Python's standard JSON encoder.

### 2.2 Comparative false-effect floor

For `n` strict-valid ABBA block deltas `delta_i`:

```text
delta_bar          = sum(delta_i) / n
s_delta            = sample_standard_deviation(delta_i), denominator n - 1
prediction_cmp_j   = abs(delta_bar)
                     + t_0.975,n-1 * s_delta * sqrt(1 + 1/n)
unguarded_cmp_j    = max(max_i(abs(delta_i)), prediction_cmp_j)
floor_cmp_j        = g(n) * unguarded_cmp_j
```

This implements D-054 exactly. Bootstrap output, if added later, is
diagnostic-only and cannot replace either formula or appear in
`floor_abs_j`, `floor_cmp_j`, or `floor_gate_j`.

### 2.3 Guard factor decision

The frozen rule is:

```text
n_ref = 10

g(n) = sqrt((n_ref - 1) / (n - 1))  when 5 <= n < n_ref
g(n) = 1                             when n >= n_ref
```

Equivalently, for all `n >= 5`, `g(n) = max(1, sqrt(9/(n-1)))`.

Required values, calculated rather than looked up, are:

| n | g(n) |
|---:|---:|
| 5 | 1.5000000000000000 |
| 6 | 1.3416407864998738 |
| 7 | 1.2247448713915890 |
| 8 | 1.1338934190276817 |
| 9 | 1.0606601717798212 |
| >=10 | 1.0000000000000000 |

Defense against “too lax”: the base estimator already widens at small `n`
through both the `t` critical value and the one-new-observation factor. At
`n=5`, this policy then adds another 50% to the larger of the prediction
component and largest observed false effect. It is intentionally more severe
than merely using the correct `t_4` value.

Defense against “arbitrary”: the factor is not tuned to observed calibration
values. It is the square root of the residual-degrees-of-freedom deficit
relative to the already accepted/default `n=10` design point. It decreases
monotonically, joins exactly to 1 at `n=10`, and has no operator-selected
constant after data. The factor is still an operational conservatism rule; it
must not be described as a tolerance-bound, percentile-coverage, confidence,
or power guarantee.

For `n < 5`, the calculator may emit the unguarded components as smoke
diagnostics, but the guarded floor and claim-facing `floor_gate_j` are null and
the cell is `smoke_only`. A cell-specific plan may require more than five
units: in particular, a suite cell designated by the plan as requiring
`n=10` remains `smoke_only` at `n=5`, even though `g(5)` is calculable.

The guard is applied once, after the `max` in the D-054 estimator. It is not
applied separately to residuals, standard deviations, ABBA members, or the
final `max(floor_abs_j, floor_cmp_j)`.

## 3. ABBA block contract

### 3.1 Exact delta

One block has executed positions `A1, B1, B2, A2`. For the selected metric:

```text
delta_b = mean(B1, B2) - mean(A1, A2)
        = (E_B1 + E_B2 - E_A1 - E_A2) / 2
```

The sign is always `B - A`. For calibration, A and B are aliases of one
identical condition, so the expected physical effect is zero. Equal position
spacing makes the estimator cancel an additive linear-in-position drift: A
and B both have mean position 2.5. The formula does not claim to remove
nonlinear thermal hysteresis; that is why the observed block deltas feed the
false-effect floor.

### 3.2 Block validity

`abba_delta()` must refuse a block unless all of the following are true:

- there are exactly four distinct bundle IDs in executed A/B/B/A order;
- all four bundles pass the repository's current strict validator and have
  succeeded summaries;
- all four have the same config hash, stack identity, metric selector,
  measurement boundary, workload/prompt provenance, sampler, output policy,
  and condition-family definition hash; only the plan/order alias differs;
- the executed-order record is present in the hash-pinned campaign log and
  agrees with the hash-pinned calibration plan; and
- the selected metric is finite in every member.

The builder fails the cell on a bad block; it never silently drops the block.
A technically invalid run may be replaced only under a replacement rule that
was frozen in the calibration plan before execution, consistent with D-062.
The artifact records both the invalid bundle reference and the replacement
reference. Outcome-dependent replacement is forbidden.

### 3.3 Consumers

The immediate consumer of `abba_delta()` is the P2-039 comparative-floor
calculator. P2-037 consumes the resulting `floor_cmp_j` through the resolver
interface in Unit 7; it does not recompute the calibration ABBA deltas.
P2-037 may later reuse the public `abba_delta()` helper for a real ABBA
condition contrast, but that is an engine decision outside this specification.

## 4. Calibration-plan input contract

The one-command build consumes a pre-data plan with schema
`joulewise.floor_calibration_plan.v1`. P2-039 implements a validator for this
input because the output is not reproducible if bundle grouping, item
clustering, condition mapping, minimum `n`, or transport membership is supplied
interactively.

Each plan cell must declare:

- stable `cell_id` and the output key (`backend`, `metric`, `window_class`,
  `condition_family_id`, and condition-family definition SHA-256);
- `use_role`: `primary_claim_gate`, `smoke_only`, or
  `staleness_sentinel`;
- `minimum_claim_n`, frozen before data;
- an absolute observation selector and ordered bundle IDs;
- ordered ABBA block IDs with four labeled bundle IDs each;
- an exact stack-identity definition;
- a `transport_group_id` plus the complete predeclared set of consumer
  condition families; and
- paths, IDs, and expected schema versions for the order manifest and campaign
  log. Their actual byte hashes are calculated into the output after execution.

Scalar request and phase paths use `cluster_reducer: "single"`. Suite item or
level paths must use either one exact predeclared item/level position or
`cluster_reducer: "mean"` over a frozen list of IDs within each bundle. The
result is one scalar per bundle. Individual items inside one bundle never
increase `n`; this is the executable no-pseudoreplication fence from
`detection_floor.md`.

The command has no `--guard-factor`, `--drop-block`, `--minimum-n`,
`--transport`, or metric-path override. Those choices belong in the plan and
are hash-pinned before data.

## 5. Versioned floor-artifact schema

### 5.1 Canonical top-level shape

The schema ID is exactly `joulewise.detection_floor_artifact.v1`. The following
is the normative JSON shape. Angle-bracketed values are metavariables; every
shown key is required, `absolute` or `comparative` may be null only under the
status rules below, and unrecognized keys are rejected at every level.

```json
{
  "schema_version": "joulewise.detection_floor_artifact.v1",
  "artifact_id": "<stable plan-supplied id>",
  "calibration_scope": "window_a|window_b_revalidation|smoke",
  "method": {
    "method_id": "d054_false_effect_guard.v1",
    "confidence": 0.95,
    "t_critical_source": "joulewise.aggregate.student_t_critical_95.v1",
    "absolute_formula": "max(max_abs_residual_j,t_critical*sample_stddev_j*sqrt(1+1/n))",
    "comparative_formula": "max(max_abs_delta_j,abs(mean_delta_j)+t_critical*sample_stddev_j*sqrt(1+1/n))",
    "abba_delta_formula": "(B1+B2-A1-A2)/2",
    "small_sample_guard": {
      "rule_id": "residual_df_ratio_to_n10.v1",
      "formula": "max(1,sqrt((10-1)/(n-1)))",
      "reference_n": 10,
      "minimum_n": 5,
      "maximum_guarded_n_exclusive": 10,
      "frozen_before_calibration": true
    }
  },
  "provenance": {
    "calibration_plan": {
      "plan_id": "<id>",
      "sha256": "<64 lowercase hex>"
    },
    "order_manifest": {
      "manifest_id": "<id>",
      "sha256": "<64 lowercase hex>"
    },
    "campaign_log": {
      "sha256": "<64 lowercase hex>"
    },
    "implementation": {
      "project_commit": "<40 lowercase hex>",
      "project_tree_state": "clean",
      "python_package": "joulewise"
    }
  },
  "cells": [
    {
      "cell_id": "<stable id>",
      "key": {
        "backend": "<telemetry backend>",
        "metric": "<canonical metric path>",
        "window_class": "request|phase|item|level|session",
        "condition_family_id": "<stable id>",
        "condition_family_sha256": "<64 lowercase hex>"
      },
      "eligibility": {
        "use_role": "primary_claim_gate|smoke_only|staleness_sentinel",
        "minimum_claim_n": "<integer >= 5>",
        "status": "claim_ready|smoke_only|incomplete|stale",
        "claim_usable": "<boolean>",
        "reason_codes": ["<stable reason code>"]
      },
      "idle_drift_guard": {
        "method": "p2_015_prediction_guard_v1",
        "guard_w": "<finite nonnegative number>",
        "n_bundles": "<integer >= 2>",
        "bundle_sha256": ["<64 lowercase hex>"],
        "cell_id": "<same stable cell id>",
        "artifact_sha256": "<64 lowercase hex>"
      },
      "floor_abs_j": "<finite nonnegative number|null>",
      "floor_cmp_j": "<finite nonnegative number|null>",
      "floor_gate_j": "<finite nonnegative number|null>",
      "absolute": {
        "n": "<integer>",
        "mean_j": "<finite number>",
        "residuals_j": ["<finite number>"],
        "sample_stddev_j": "<finite nonnegative number>",
        "max_abs_residual_j": "<finite nonnegative number>",
        "t_critical": "<finite positive number>",
        "prediction_component_j": "<finite nonnegative number>",
        "unguarded_floor_j": "<finite nonnegative number>",
        "guard_factor": "<finite number >= 1|null when n < 5>",
        "guarded_floor_j": "<finite nonnegative number|null when n < 5>",
        "bundle_observations": [
          {
            "bundle_id": "<metadata.run_id>",
            "bundle_sha256": "<64 lowercase hex>",
            "config_sha256": "<64 lowercase hex>",
            "metric_value_j": "<finite number>"
          }
        ]
      },
      "comparative": {
        "n_blocks": "<integer>",
        "mean_delta_j": "<finite number>",
        "block_deltas_j": ["<finite number>"],
        "sample_stddev_j": "<finite nonnegative number>",
        "max_abs_delta_j": "<finite nonnegative number>",
        "t_critical": "<finite positive number>",
        "prediction_component_j": "<finite nonnegative number>",
        "unguarded_floor_j": "<finite nonnegative number>",
        "guard_factor": "<finite number >= 1|null when n_blocks < 5>",
        "guarded_floor_j": "<finite nonnegative number|null when n_blocks < 5>",
        "blocks": [
          {
            "block_id": "<stable id>",
            "executed_labels": ["A", "B", "B", "A"],
            "members": [
              {
                "position": "A1|B1|B2|A2",
                "bundle_id": "<metadata.run_id>",
                "bundle_sha256": "<64 lowercase hex>",
                "config_sha256": "<64 lowercase hex>",
                "metric_value_j": "<finite number>"
              }
            ],
            "delta_j": "<finite number>"
          }
        ]
      },
      "source_regime": {
        "stack_identity": {
          "stack_identity_sha256": "<64 lowercase hex>",
          "measurement_boundary_id": "<D-018 boundary id>",
          "target_unit_id": "<physical unit id>",
          "hardware_fingerprint_sha256": "<64 lowercase hex>",
          "os_build": "<exact string>",
          "runtime_backend": "<exact string>",
          "runtime_version": "<exact string>",
          "model_artifact_sha256": "<64 lowercase hex>",
          "tokenizer_artifact_sha256": "<64 lowercase hex>",
          "telemetry_backend": "<exact string>",
          "telemetry_version": "<exact string>",
          "rail_manifest_sha256": "<64 lowercase hex>",
          "sampler_config_sha256": "<64 lowercase hex>"
        },
        "stress_observed": {
          "mean_power_w_min": "<finite nonnegative number>",
          "mean_power_w_max": "<finite nonnegative number>",
          "window_duration_s_min": "<finite positive number>",
          "window_duration_s_max": "<finite positive number>",
          "p95_sample_gap_s_max": "<finite positive number>",
          "bracketing_sample_gap_s_max": "<finite positive number>",
          "cadence_ratio_min": "<finite nonnegative number>",
          "bound_terms": {
            "clock_anchor_bound_s": {
              "applicability": "required|not_applicable|unknown",
              "maximum": "<finite nonnegative number|null>"
            },
            "interpolation_bound_j": {
              "applicability": "required|not_applicable|unknown",
              "maximum": "<finite nonnegative number|null>"
            },
            "idle_drift_bound_j": {
              "applicability": "required|not_applicable|unknown",
              "maximum": "<finite nonnegative number|null>"
            }
          }
        }
      },
      "transport_group_id": "<stable id>",
      "provenance": {
        "absolute_calibration_cell_id": "<id|null>",
        "comparative_calibration_cell_id": "<id|null>",
        "bundle_ids": ["<unique bundle id>"],
        "bundle_sha256s": ["<64 lowercase hex in bundle_ids order>"]
      }
    }
  ],
  "transport_groups": [
    {
      "transport_group_id": "<stable id>",
      "rule_id": "same_stack_componentwise_worst_case.v1",
      "backend": "<telemetry backend>",
      "metric": "<canonical metric path>",
      "window_class": "request|phase|item|level|session",
      "stack_identity_sha256": "<64 lowercase hex>",
      "source_cell_ids": ["<cell id>"],
      "allowed_consumer_condition_families": [
        {
          "condition_family_id": "<stable id>",
          "condition_family_sha256": "<64 lowercase hex>"
        }
      ],
      "composed_floor_abs_j": "<finite nonnegative number>",
      "composed_floor_cmp_j": "<finite nonnegative number>",
      "composed_floor_gate_j": "<finite nonnegative number>",
      "stress_envelope": {
        "mean_power_w_min": "<finite nonnegative number>",
        "mean_power_w_max": "<finite nonnegative number>",
        "window_duration_s_min": "<finite positive number>",
        "window_duration_s_max": "<finite positive number>",
        "p95_sample_gap_s_max": "<finite positive number>",
        "bracketing_sample_gap_s_max": "<finite positive number>",
        "cadence_ratio_min": "<finite nonnegative number>",
        "bound_term_maxima": {
          "clock_anchor_bound_s": "<finite nonnegative number|null>",
          "interpolation_bound_j": "<finite nonnegative number|null>",
          "idle_drift_bound_j": "<finite nonnegative number|null>"
        }
      }
    }
  ]
}
```

### 5.2 Required schema invariants

The stdlib validator is authoritative even when optional `jsonschema` is not
installed. It must enforce at least these cross-field rules:

- Cell keys and cell IDs are unique. Transport-group IDs are unique and every
  cell references one existing group.
- Every SHA is lowercase hex of the stated length. Every number is finite;
  booleans are not accepted as numbers. Energies, durations, gaps, standard
  deviations, and bounds that are defined nonnegative cannot be negative.
- `n == len(residuals_j) == len(bundle_observations)` and
  `n_blocks == len(block_deltas_j) == len(blocks)`. Each block has exactly four
  members with positions and labels in A1/B1/B2/A2 order.
- The validator recomputes every residual, block delta, mean, sample standard
  deviation, prediction component, unguarded floor, guard factor, guarded
  floor, and cell floor. Stored values must match within
  `max(1e-12, 1e-12 * abs(expected))`.
- If both components are numeric, `floor_gate_j` equals
  `max(floor_abs_j, floor_cmp_j)`. It is null if either component is null.
- `claim_ready` requires `use_role == primary_claim_gate`, both components
  numeric, both `n` values at least `minimum_claim_n`, every source bundle
  strict-valid, no required regime/bound term unknown, and a complete transport
  group. `claim_usable` is true if and only if status is `claim_ready` and the
  cell is not stale.
- `smoke_only`, `incomplete`, and `stale` cells are never returned as usable by
  the resolver, even if they contain numeric diagnostics.
- A bound term with `applicability == required` has a numeric maximum;
  `not_applicable` has null; `unknown` has null and prevents claim readiness.
  Gross request and current gross phase/item/level metrics mark idle drift
  `not_applicable`; idle-subtracted request metrics mark it `required`.
- The exact stack-identity object, excluding its own hash field, is hashed with
  domain `joulewise.stack_identity.v1`; the result must equal
  `stack_identity_sha256`.
- Every transport group's source cells have the group's backend, metric,
  window class, and stack hash. Its three composed floors and every stress
  envelope value are recomputed from all source cells under Unit 6.
- A claim-facing artifact requires a clean 40-hex project commit. Smoke
  artifacts may record `project_tree_state: dirty`, but the state is never
  omitted or inferred as clean.

### 5.3 Bundle and artifact hashes

Each `bundle_sha256` pins the complete bundle bytes, not only its summary. The
builder walks all regular files below the bundle, rejects symlinks and special
files, sorts relative POSIX paths, and builds records
`{"path": ..., "sha256": ..., "size_bytes": ...}`. It then computes:

```text
sha256(
  UTF8("joulewise.calibration_bundle.v1") || NUL ||
  UTF8(canonical_json(file_records))
)
```

`canonical_json` uses sorted object keys, separators `(',', ':')`, UTF-8, and
no NaN/Infinity. This deliberately aligns with the existing bundle-pack file
manifest semantics while giving one compact per-bundle pin.

The output JSON is written with sorted keys, two-space indentation, UTF-8, and
one trailing newline. The builder also writes `<output>.sha256`, containing the
lowercase SHA-256 of the exact artifact bytes plus a newline. Neither absolute
paths nor a generation timestamp appear in the artifact, so the same inputs,
implementation version, and commit produce byte-identical output.

## 6. Conservative regime-transport rule

### 6.1 No cross-stack transport

`stack_identity_sha256` includes physical target/unit, hardware fingerprint,
OS build, runtime and version, model artifact, tokenizer artifact, telemetry
backend and version, rail manifest, sampler configuration, and measurement
boundary. Any difference is a `stack_mismatch` refusal. In particular, a floor
measured on the 1.5B model does not silently gate the 122B model, even on the
same Mac and telemetry backend. A runtime, OS, model revision, rail, requested
sampling configuration, or physical-unit change also requires a matching
calibration cell or a new, separately adjudicated bridge rule.

This is intentionally stricter than treating “powermetrics on the same Mac” as
one regime. RIG-6 found no evidence for cross-stack portability, so a numeric
inflation would manufacture identifiability rather than recover it.

### 6.2 Same-stack predeclared transport

Within one exact stack, a consumer may use an exact cell or a predeclared
transport group only when all checks below pass. Let `S` be every source cell
named in the group; sources cannot be selected after seeing their floors.

The composed floor is:

```text
F_abs(S)  = max_s in S(s.floor_abs_j)
F_cmp(S)  = max_s in S(s.floor_cmp_j)
F_gate(S) = max(F_abs(S), F_cmp(S))
```

The composed stress envelope is the synthetic worst-case corner:

```text
P_min     = min_s(s.mean_power_w_min)
P_max     = max_s(s.mean_power_w_max)
D_min     = min_s(s.window_duration_s_min)
D_max     = max_s(s.window_duration_s_max)
G_p95     = max_s(s.p95_sample_gap_s_max)
G_bracket = max_s(s.bracketing_sample_gap_s_max)
R_min     = min_s(s.cadence_ratio_min)
B_k       = max_s(s.bound_term[k].maximum) for each applicable known term k
```

Maxima may come from different source cells. This composition is deliberate:
the resolver cannot choose the low floor from one cell and the favorable drift
or cadence evidence from another.

For all bundles contributing to a consumer contrast, compute a consumer stress
summary with minima/maxima in the same direction. Transport is allowed only if:

```text
consumer.backend               == group.backend
consumer.metric                == group.metric
consumer.window_class          == group.window_class
consumer.stack_identity_sha256 == group.stack_identity_sha256
consumer condition id+hash is in allowed_consumer_condition_families
consumer.mean_power_w_min      >= P_min
consumer.mean_power_w_max      <= P_max
consumer.window_duration_s_min >= D_min
consumer.window_duration_s_max <= D_max
consumer.p95_sample_gap_s_max  <= G_p95
consumer.bracketing_gap_s_max  <= G_bracket
consumer.cadence_ratio_min     >= R_min
consumer bound k maximum       <= B_k for every applicable term k
```

The consumer must also pass the existing D-054/D-057 minimum cadence, sample,
clock, and interpolation gates independently. Passing transport does not waive
those gates.

The resolver refuses with a stable reason if a consumer term is absent or
unknown, if power or duration lies outside the measured bracket, if cadence or
any deterministic bound is worse, if the condition family was not
predeclared, if any source cell is stale/not claim-ready, or if any invariant
differs. It does not extrapolate a floor as a function of watts or seconds and
does not add an ad hoc transport margin.

Deterministic error-budget bounds remain separate from the false-effect floor,
as D-054 requires. They are used here to decide whether transport is valid and
are still consumed separately by P2-037. They are not added into
`floor_abs_j`, `floor_cmp_j`, or stochastic variance.

### 6.3 Stable transport reason codes

The v1 resolver uses this closed set:

```text
artifact_hash_mismatch
artifact_schema_invalid
cell_missing
cell_not_claim_ready
cell_stale
condition_not_predeclared
stack_mismatch
power_outside_calibrated_envelope
duration_outside_calibrated_envelope
cadence_harder_than_calibration
clock_anchor_harder_than_calibration
interpolation_harder_than_calibration
drift_harder_than_calibration
consumer_term_unknown
transport_group_incomplete
```

Adding a reason is an additive schema-compatible change; changing the meaning
of an existing reason or weakening a check requires a new transport rule ID.

## 7. Module, CLI, and P2-037 integration

### 7.1 Calculator home and public surface

The implementation lives in `joulewise/detection_floor.py` because both the
CLI and P2-037 need the same typed, pure behavior. A script-only implementation
would force the claim engine to shell out or duplicate statistical and schema
policy.

Required public functions/types:

```python
small_sample_guard_factor(n: int) -> float
absolute_false_effect_floor(values_j: Sequence[float]) -> FloorEstimate
abba_delta(a1_j: float, b1_j: float, b2_j: float, a2_j: float) -> float
comparative_false_effect_floor(block_deltas_j: Sequence[float]) -> FloorEstimate
validate_floor_plan(value: Mapping[str, object]) -> list[str]
derive_floor_artifact(plan: Mapping[str, object], observations: FloorInputs) -> dict
validate_floor_artifact(value: Mapping[str, object]) -> list[str]
load_floor_artifact(path: Path, expected_sha256: str) -> FloorArtifact
resolve_floor(artifact: FloorArtifact, request: FloorRequest) -> FloorResolution
```

`FloorEstimate`, `FloorInputs`, `FloorArtifact`, `FloorRequest`, and
`FloorResolution` are frozen dataclasses or equivalently immutable typed
objects. The pure math functions do no I/O. Bundle extraction and strict
validation are orchestration around the pure derivation; they must use the
existing `BundleReader` and current strict bundle validator rather than a
second interpretation of bundle semantics.

### 7.2 CLI shape

`joulewise/cli.py` adds one nested command group:

```text
python3 -m joulewise floor-artifact build PLAN.json \
  --runs-dir RUNS_DIR \
  --campaign-log CAMPAIGN_LOG.jsonl \
  --output FLOOR_ARTIFACT.json

python3 -m joulewise floor-artifact validate FLOOR_ARTIFACT.json \
  --expected-sha256 HEX \
  [--runs-dir RUNS_DIR]

python3 -m joulewise floor-artifact print-schema [--output PATH]
```

`build` performs plan validation, strict validation of every referenced
bundle, campaign-order verification, bundle hashing, metric extraction,
calculation, artifact validation, atomic output write, and sidecar-hash write.
It refuses to overwrite either output unless `--replace` is supplied. Replace
uses a same-directory temporary file plus `os.replace`; partial output is not
left behind.

`validate` always verifies the expected artifact SHA and all structural/math
invariants. When `--runs-dir` is supplied it also resolves every bundle ID,
recomputes its complete-bundle hash, re-extracts metric values, and re-derives
the artifact in memory. The re-derived semantic body must equal the stored
body. Source bundles are never rewritten.

Exit codes are 0 for success, 2 for invalid/refused input or failed
verification, and 3 for an unexpected operational failure. Success prints one
machine-parseable line containing artifact ID, cell count, artifact SHA-256,
and output path. Diagnostics go to stderr. The CLI exposes no statistical
override.

### 7.3 P2-037 interface boundary

P2-037 must receive a `FloorRequest` containing:

```text
backend
metric
window_class
condition_family_id
condition_family_sha256
stack_identity_sha256
consumer stress summary (the Unit 6 fields)
```

The resolver returns exactly:

```text
status: exact | transported | refused
artifact_id
artifact_sha256
source_cell_ids
transport_group_id
transport_rule_id
floor_abs_j: number | null
floor_cmp_j: number | null
floor_gate_j: number | null
reason_codes: tuple[str, ...]
```

For `exact` or `transported`, P2-037 uses `floor_gate_j` as the D-054 floor
input and records every provenance field in its analysis artifact. An observed
absolute effect clears the floor only when `abs(effect_j) > floor_gate_j`;
equality does not clear it. P2-037 still applies contrast intervals,
multiplicity, leave-one-out, propagated variance, deterministic bounds, and
the claim ladder separately.

For `refused`, all three floor values are null. P2-037 maps that fact into its
own fail-closed claim verdict; this specification does not design that engine
or its full verdict precedence.

## 8. File targets and implementation units

1. `joulewise/detection_floor.py`
   - pure D-054 math and guard;
   - ABBA validation/delta;
   - plan and artifact validators;
   - canonical hashing helpers;
   - immutable artifact loader and transport resolver.
2. `joulewise/cli.py`
   - nested `floor-artifact` parser and thin I/O/orchestration handlers;
   - reuse current strict bundle validation and `BundleReader`.
3. `tests/test_detection_floor.py`
   - unit, schema, tamper, transport, and hand-math tests.
4. `tests/test_cli.py`
   - parser, exit-code, atomic-write, deterministic-rebuild, and no-override
     coverage for the three CLI verbs.
5. `tests/fixtures/detection_floor/absolute_n5.json`
   - Unit 9.1 source values and expected calculation record.
6. `tests/fixtures/detection_floor/abba_n5.json`
   - Unit 9.2 five complete blocks and expected calculation record.
7. `tests/fixtures/detection_floor/artifact_v1.json`
   - one internally valid, claim-ready v1 artifact composed from the two hand
     fixtures, using stable synthetic hashes and regime evidence.
8. `docs/phase_2/detection_floor.md` and `docs/decision_log.md`
   - implementation landing must promote the adjudicated numeric guard and
     transport rule into the owning authority. This DRAFT spec alone does not
     amend accepted D-054.

No new dependency is permitted. Optional `jsonschema` may cross-check the
generated schema in one skipped-when-unavailable test, but bare-Python CI must
fully validate artifacts.

## 9. Hand-computed fixtures and test obligations

### 9.1 Fixture A: absolute floor, n=5

Input bundle-clustered energies:

```text
E = [10, 10, 10, 10, 20] J
n = 5
t_0.975,4 = 2.776
```

By hand:

```text
mean(E) = 12 J
residuals = [-2, -2, -2, -2, 8] J
sum((r_i - mean(r))^2) = 80 J^2
s_r = sqrt(80 / 4) = sqrt(20) = 4.472135954999580 J
max(abs(r_i)) = 8 J

prediction_abs_j
  = 2.776 * sqrt(20) * sqrt(1 + 1/5)
  = 13.599567051932203 J

unguarded_abs_j = max(8, 13.599567051932203)
                = 13.599567051932203 J

g(5) = sqrt(9/4) = 1.5

floor_abs_j = 1.5 * 13.599567051932203
            = 20.399350577898304 J
```

The fixture test uses the displayed full expected result with relative/absolute
tolerance `1e-12`. It also proves that the factor is applied after, not inside,
the D-054 maximum.

### 9.2 Fixture B: comparative ABBA floor, n=5 blocks

Executed energy values, in joules:

| Block | A1 | B1 | B2 | A2 | `(B1+B2-A1-A2)/2` |
|---|---:|---:|---:|---:|---:|
| b1 | 100 | 101 | 103 | 102 | 1 |
| b2 | 100 | 99 | 101 | 102 | -1 |
| b3 | 100 | 102 | 104 | 102 | 2 |
| b4 | 100 | 98 | 100 | 102 | -2 |
| b5 | 100 | 101 | 101 | 102 | 0 |

Therefore:

```text
deltas = [1, -1, 2, -2, 0] J
delta_bar = 0 J
sum((delta_i - delta_bar)^2) = 10 J^2
s_delta = sqrt(10 / 4) = sqrt(2.5) = 1.581138830084190 J
max(abs(delta_i)) = 2 J

prediction_cmp_j
  = abs(0) + 2.776 * sqrt(2.5) * sqrt(1 + 1/5)
  = 4.808173041811203 J

unguarded_cmp_j = max(2, 4.808173041811203)
                = 4.808173041811203 J

floor_cmp_j = g(5) * unguarded_cmp_j
            = 1.5 * 4.808173041811203
            = 7.212259562716805 J
```

The fixture separately tests sign: swapping the A and B labels negates every
block delta but leaves this symmetric false-effect floor unchanged. Reordering
members without matching A/B/B/A provenance is a validation failure, not a
different estimate.

### 9.3 Mandatory test matrix

Implementation is incomplete until tests prove all of the following:

1. Guard values for every `n=5..10`, exact join at ten, rejection of invalid
   integer/boolean `n`, and smoke-only behavior below five.
2. Both hand fixtures match every intermediate and final value above.
3. Comparative mean shift is included as `abs(mean_delta_j)`; a nonzero-mean
   fixture fails if an implementation accidentally centers deltas first.
4. A/B/B/A cancels a constructed linear position drift; wrong order,
   duplicate bundles, nonfinite values, unequal condition hashes, or missing
   executed-order evidence fails closed.
5. Item/level selectors yield one cluster scalar per bundle and never count
   item rows as `n`.
6. Unknown keys, wrong schema/method/guard IDs, uppercase/malformed hashes,
   NaN/Infinity, negative bounds, duplicate cell keys, inconsistent lengths,
   stored/recomputed math mismatches, and a wrong `floor_gate_j` are rejected.
7. A valid artifact round-trips through JSON and reserializes byte-identically.
   Tampering any source bundle file causes `validate --runs-dir` to return 2.
8. Build refuses a non-strict or unsuccessful bundle and never leaves a
   partial artifact. Existing output is preserved without `--replace`.
9. An exact same-stack request resolves. A predeclared same-stack condition
   inside all envelopes resolves as `transported` and returns maxima composed
   across all source cells.
10. A transport test places the largest floor, worst cadence, longest-duration
    drift, and widest power endpoint in different source cells; the group must
    compose all of them rather than choose one favorable source.
11. Separate mutation-style tests trigger every Unit 6.3 refusal reason,
    including 1.5B-versus-122B model hash mismatch, power unbracketed on either
    side, shorter and longer duration escape, worse cadence, worse/unknown
    drift, stale source, and an unregistered condition family.
12. Loading with the wrong artifact SHA refuses before cell lookup. The
    `FloorResolution` exact/transported/refused shape is locked for P2-037.
13. `python3 -m joulewise floor-artifact build ...` re-derives a fixture
    artifact from strict-valid synthetic bundles in one command; `validate`
    with and without `--runs-dir` and `print-schema` have pinned stdout,
    stderr, and exit codes.
14. The canonical repository suite remains green:
    `python3 -m unittest discover -s tests`.

## 10. Fences and acceptance

- Implement `detection_floor.md`; do not replace its estimator, add a
  percentile-UCB/bootstrap primary floor, reinterpret the guard as formal
  coverage, or fold error-budget bounds into stochastic variance.
- `n` means strict-valid bundles for absolute cells and strict-valid blocks for
  comparative cells. Never raw samples, phases, items, levels, or ABBA members.
- Do not collect quiet-machine calibration data, run powermetrics, or claim a
  live floor in P2-039. Those are lead-controlled `[QUIET-MAC]` P2-015 tasks.
- No operator discretion after data: no CLI math overrides, silent exclusions,
  selective transport sources, or outcome-dependent additions. Technical
  replacements follow the frozen plan; D-062 demotion governs any later
  outcome-dependent top-up.
- Missing `floor_abs_j`, `floor_cmp_j`, required bounds, hashes, or transport
  evidence fails closed for L2/L3. Numeric zero is never substituted for
  unknown.
- Do not redesign P2-037. P2-039 supplies only the validated resolution
  interface and provenance needed by that future engine.
- Do not broaden cross-boundary claims. Transport requires the same D-018
  measurement boundary; wall/PD bridge-model calibration remains separate.
- Raw calibration bundles, campaign log, order manifest, and plan are immutable
  evidence. The floor artifact is a derived file and must be reproducible from
  them.

P2-039 implementation acceptance is all of:

1. lead adjudicates the guard and transport decisions before floor data;
2. the package module, plan/artifact validators, CLI, and fixtures land;
3. one command deterministically derives the valid fixture artifact;
4. hand math and transport refusal tests pass;
5. the full suite passes; and
6. the owning decision/design docs are amended with the accepted numeric guard
   and transport rule. Only then may P2-015 proceed beyond its SMOKE row.

## 11. DEVIATIONS / OPEN QUESTIONS

### 11.1 Explicit specification completions

- `detection_floor.md` currently requires but does not numerically define the
  `5 <= n < 10` multiplier. Unit 2.3 fills that deliberate P2-039 gap; until
  lead adjudication and promotion into D-054, it remains a draft proposal, not
  a retroactive rule.
- `detection_floor.md` names ABBA block deltas but does not give their exact
  equation. Unit 3 fixes the sign and drift-canceling contrast without changing
  the D-054 comparative estimator.
- The design doc says to map a consumer to cells whose duration, cadence, and
  drift stress is no easier, but RIG-6 correctly found that stack/power/duration
  transfer was not identified. Unit 6 makes that prose executable and refuses
  cross-stack transfer rather than guessing an inflation.
- The artifact presents one consumer-facing row with both floors even though
  the campaign table lists separate absolute and comparative calibration
  activities. This is a representation completion required by the binding
  `max(floor_abs_j, floor_cmp_j)` claim gate, not a change to either estimator.

### 11.2 Conflicts and premise errors requiring lead visibility

1. D-054's C-027 amendment settles the economics wording: 170 bundles is the
   minimum Window-A request/phase subset; 180-340 includes Window-B. It does
   not establish that those bundles cover every materially different model
   stack. Because this spec forbids cross-stack transport, a plan covering both
   1.5B and 122B claim regimes needs direct floor cells for both, or must cap
   the uncovered stack. If the current 170-340 table counted only one such
   stack, its claim-coverage premise and possibly its bundle total are
   incomplete. P2-039 must not silently rewrite that accepted economics table;
   the lead must adjudicate the P2-015 stack list and revised count before
   collection.
2. `docs/contracts/analysis_plans.md` and parts of the 2M/Window-B prose still
   contain outcome-dependent “near-floor top-up” language. Accepted D-062 wins:
   fixed `n` is frozen before observing a pack's effects, and any
   outcome-dependent top-up permanently demotes that contrast to exploratory.
   The owning AP-EDIT task must repair those texts; P2-039 neither preserves nor
   relies on the stale rule.
3. The phase-2 exit checklist still calls 2M “UNBLOCKED,” while the newer queue
   gates P2-015 beyond SMOKE on P2-038/P2-039 and orders P2-006 after floors.
   The queue and active C-027 decision state win. This spec does not edit the
   checklist status because P2-039 is not the status-authority reconciliation
   task.

### 11.3 Open lead adjudications, with implementation defaults fixed here

- The lead must name the actual P2-015 stack identities and condition-family
  IDs before data. The implementation default is refusal for every unnamed
  stack/condition; there is no wildcard.
- The lead must decide whether the additional per-stack floor cells change the
  accepted campaign economics or cap claims on uncovered stacks. The
  implementation default is claim capping, never silent transport.
- Promotion location is not open: accepted choices must be appended to D-054
  and reflected in `detection_floor.md`. The remaining question is adjudication,
  not where the rule lives.

## 12. CHECKS PERFORMED

- Read `RUN_STATE.md` sections `ACTIVE_STOP_CARD`, Current Project Status,
  Known Workspace State, and What Is Next; no active stop card exists.
- Read the Current Queue and Do-Not-Do-Yet portions of `TASK_QUEUE.md`; P2-039
  is the named `[AGENT]` pre-P2-015-beyond-SMOKE task.
- Ran Mission M0 intake from `docs/agent_playbook.md` and inspected the
  source-of-truth map and planning-reflection requirements.
- Read D-054 including its C-027 170-versus-180 amendment, D-057's bound
  semantics, D-062's fixed-n rule, and D-056's distinct campaign-order
  provenance.
- Read `docs/phase_2/detection_floor.md` estimator, cell list, economics,
  condition mapping, ABBA, revalidation, error-budget, propagation, and claim
  gate sections.
- Read C-027 review section 3 B8, the STA-4/RIG-6 dispositions,
  `lens-stats.md` finding 4, and `lens-rigor.md` finding 6.
- Inspected current `joulewise.aggregate` t-critical behavior, `BundleReader`,
  CLI structure, suite floor seam, campaign order log, bundle-pack hashing,
  schemas, tests, and the future P2-037 queue interface.
- Recomputed the guard sequence for `n=5..10`:
  `[1.5, 1.3416407864998738, 1.224744871391589,
  1.1338934190276817, 1.0606601717798212, 1.0]`.
- Recomputed both hand fixtures independently with the repository's 2.776
  `t_4` value: absolute `20.399350577898304 J`; comparative
  `7.212259562716805 J`.
- Checked `git status --short --branch`: branch `c027-spec-wave`; no changed
  paths were reported. Git emitted only sandbox `/tmp/xcrun_db` warnings.
- Attempted to create this specification at its required path; the write was
  rejected because the session filesystem is read-only. The target file remains
  absent and no bookkeeping files were changed.
- This is a docs-only specification run; no quiet-machine measurement,
  production calibration, or canonical test-suite run was performed.
```
