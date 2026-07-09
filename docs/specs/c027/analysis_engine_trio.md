# C-027 Analysis Engine Trio Specification

Status: DRAFT pending lead adjudication (C-027 spec wave)

Queue scope: P2-042 (frozen analysis manifest), P2-037 (contrast/claim
engine), and P2-041 (campaign verdict split). These are one design because the
manifest freezes the inferential choices, the campaign runner reports whether
the planned evidence was collected, and the analysis engine alone decides
whether a registered claim is supported.

This file is an implementation specification, not a new statistical authority.
Named decisions D-053, D-054, D-057, and D-062 win over older contract prose.
The implementation session must resolve the deviations and lead questions near
the end of this file before changing a rule marked **LEAD**.

## 0. Purpose, authority, and non-goals

### 0.1 Required outcome

The landed path is:

```text
generated configs + order_manifest.json
  -> frozen analysis_manifest.json (P2-042)
  -> campaign collection verdict + claim-input readiness (P2-041)
  -> strict-valid bundles + P2-039 floor artifact
  -> paired/block analysis + multiplicity + sensitivity checks
  -> claim_verdicts.json (P2-037)
  -> claims_lint claim-index mode
  -> Phase-4 claims-index row
```

The words have deliberately different scopes:

- **collection usable** means the expected raw evidence was produced and the
  bundle passed collection-integrity checks;
- **ready for claim analysis** means the planned bundle set and reducer-level
  evidence fields are present, not that any effect is supported;
- **claim outcome** is one of the five P2-037 outcomes after contrast,
  uncertainty, floor, multiplicity, and sensitivity evaluation;
- **publishable** is not a machine verdict anywhere in the new path.

### 0.2 Binding authorities

The implementation must compose, in this order:

1. D-053: claim-bearing inference is on a registered paired/block or named
   model contrast; the complete contrast family and exact Holm/BH denominator
   are frozen before execution; LOO is mandatory at `n <= 10`; randomization
   checks respect the realized assignment mechanism.
2. D-054: the active floor is `max(floor_abs, floor_cmp)` for a matching
   backend, metric, window class, and transport regime; stochastic variance and
   deterministic bounds remain distinct; unknown terms cap claims.
3. D-057: reducer evidence reasons are stable machine vocabulary; drift is a
   deterministic bound unless an explicit distributional model says otherwise;
   cap hits and unknown inputs fail closed; one bundle is not estimable.
4. D-062: confirmatory `n` is fixed before pack effects are observed;
   technically invalid replacements follow a frozen rule; any
   outcome-dependent top-up permanently demotes the affected contrast to
   exploratory.
5. `docs/contracts/analysis_plans.md`, `claims_ladder.md`,
   `measurement_methodology.md` section “Statistical Protocol,” and
   `token_normalization.md`, except where their older text conflicts with a
   named decision above.
6. C-027 review B4 and STATS findings 1, 2, 3, 9, 10, and 11. The three
   numeric counterexamples in Section 7 are acceptance fixtures, not examples
   that may be approximated away.

### 0.3 Fences

- This is `[AGENT]` design and implementation work. It starts no campaign,
  hardware run, powermetrics session, detection-floor capture, or quiet-window
  work.
- It does not reinterpret the six existing corpus bundles as modern
  confirmatory evidence. Those bundles may be consumed only by mechanics tests
  and the RPT-001 vertical slice, with `evidence_class = "legacy_l1"` and a
  visible `legacy_l1_mechanics_only` limitation.
- It does not calculate P2-039 floors, select the small-sample guard factor, or
  invent a floor transport rule. It pins the P2-039 consumer interface and
  fails closed if the producer does not satisfy it.
- It does not replace `joulewise.aggregate`. The current aggregator remains a
  descriptive one-condition aggregate; it must not be called the claim engine.
- It does not add a mixed model “just in case.” A named model contrast is added
  only with a real dependence structure and a frozen registry revision.
- It does not silently exclude outliers, quality-flagged bundles, incomplete
  pairs, or failed randomization checks.

### 0.4 Premise corrections found during design

These are implementation facts, not optional commentary:

1. `generate_matrix.py` emits every matrix member with `repetitions = 1`.
   `run_campaign.py` invokes those configs independently. The D-014 cooldown
   gate in `controller.run_experiment` therefore does **not** run between those
   matrix members. Until a campaign-level cooldown owner lands, P2-041 must
   return `not_ready_for_analysis` for affected confirmatory contrasts with
   reason `campaign_cooldown_evidence_missing`; it must not infer a clean gate
   from a missing `cooldown_cap_hit` field.
2. D-053 is accepted, but `analysis_plans.md` and
   `measurement_methodology.md` still say “pending ratification.” D-053 wins.
3. D-062 invalidates the outcome-dependent top-up language still present in
   AP-1 through AP-5 and several campaign packs. D-062 wins. A mechanically
   detected top-up is a demotion even if the old prose appears to permit it.
4. Phase-4 plan prose still uses marginal-CI separation and an ambiguous “no
   measurable difference” category. The P2-037 five-outcome evaluator wins;
   Phase-4 prose must be synchronized before its claims-index mode is enabled.

## 1. Shared vocabulary and interface invariants

### 1.1 Closed sets

The following strings are schema vocabulary. Changing them requires a schema
version bump; changing a D-057 reason additionally requires a decision-log
amendment.

| Concept | Values |
|---|---|
| manifest freeze | `frozen` |
| entry role | `condition`, `drift_sentinel_start`, `drift_sentinel_end` |
| multiplicity method | `holm`, `benjamini_hochberg`, `exploratory_none` |
| analysis role | `primary`, `secondary`, `exploratory` |
| sampling design | `fixed_n`, `two_look_alpha_spending` |
| collection verdict | `usable`, `partial`, `blocked`, `invalid` |
| claim-input readiness | `ready_for_analysis`, `not_ready_for_analysis`, `not_assessed` |
| claim outcome | `not_estimable`, `not_resolvable`, `unresolved`, `direction_supported`, `equivalent` |
| sensitivity status | `not_required`, `clean`, `concern`, `not_run` |
| evidence class | `current`, `legacy_l1` |

`two_look_alpha_spending` is schema-reserved for a future specifically approved
campaign. P2-042 emits `fixed_n`; P2-037 must reject an alpha-spending manifest
whose maximum `n`, look boundaries, and spending function are not all present.

### 1.2 Identifier rules

All identifiers use lowercase ASCII `[a-z0-9_-]`, are stable under rerun, and
contain no timestamps or absolute paths.

For the existing Slice-2M generator:

```text
condition baseline: cond-2m-<workload>
condition sentinel: cond-2m-drift-sentinel-<start|end>
cell baseline:      cell-2m-<model_tag>-<workload>
cell sentinel:      cell-2m-<model_tag>-drift-sentinel-<start|end>
block:              block-2m-<model_tag>-r<two-digit-rep>
entry:              entry-2m-<model_tag>-r<two-digit-rep>-<workload-or-sentinel-position>
sentinel link:      sentinel-2m-<model_tag>-r<two-digit-rep>
```

`block_id` is semantic and must not be derived from the mutable numeric
`block_index` in `order_manifest.json`. Adding a second model tag changes some
numeric block indexes but must not change the first model’s semantic IDs.

Contrast IDs state the arithmetic direction:

```text
ctr-ap2-<model_tag>-<metric_tag>-<condition_b>-minus-<condition_a>
```

The estimator is always `B - A`. A consumer must never infer direction from
array order alone.

### 1.3 Hash and canonicalization rule

Every frozen JSON artifact uses the same identity rule:

1. Remove its top-level identity field (`manifest_id` or
   `claim_verdicts_id`).
2. Serialize the remaining object with Python-equivalent
   `json.dumps(value, sort_keys=True, separators=(",", ":"),
   ensure_ascii=False)` and UTF-8 encode it.
3. SHA-256 the bytes and prefix the lowercase hex digest with `am-` or `cv-`.
4. Emit the human-readable file with pinned insertion order, two-space indent,
   `ensure_ascii=False`, and exactly one trailing newline.

The identity is semantic-canonical; the file-byte SHA-256 is recorded by
downstream consumers separately. Self-hashing never includes the identity
field, avoiding a circular hash definition.

## 2. Component A — P2-042 frozen analysis manifest

### A1. Output and ownership

`scripts/generate_matrix.py` emits `analysis_manifest.json` in the same
directory as `order_manifest.json`. The output schema is
`joulewise.analysis_manifest.v1`.

File targets:

- new `configs/analysis_registry/slice_2m_ap2.v1.json`: machine-readable AP-2
  registry template;
- new `joulewise/analysis_manifest.py`: dataclasses/validation,
  canonicalization, ID calculation, and Slice-2M builder helpers;
- modify `scripts/generate_matrix.py`: construct and write the manifest;
- minimally modify `scripts/run_campaign.py` in this landing so both manifest
  filenames are excluded from config discovery; no verdict semantics land in
  this compatibility shim;
- modify `scripts/claims_lint.py`: explicit `analysis-registry` mode checks the
  template against the AP-2 row;
- tests in `tests/test_analysis_manifest.py`,
  `tests/test_generate_matrix.py`, and the config-discovery portion of
  `tests/test_run_campaign.py`.

The registry template is preferable to hard-coded contrast lists in the
generator: it is reviewable JSON, is hashed into the frozen artifact, and can
be linted against AP-2. It is not a second policy authority; on conflict the AP
contract and named decisions win, and lint fails until the template is
updated.

### A2. Exact top-level JSON shape

No unlisted key is permitted in v1. Nullable means JSON `null`, not omission.

```json
{
  "schema_version": "joulewise.analysis_manifest.v1",
  "manifest_id": "am-<64 lowercase hex>",
  "freeze_status": "frozen",
  "design": {
    "design_id": "slice_2m_ap2_v1",
    "analysis_plan_ids": ["AP-2"],
    "unit_of_analysis": "paired_block",
    "difference_orientation": "condition_b_minus_condition_a",
    "sampling_plan": {
      "design": "fixed_n",
      "planned_n_blocks": 5,
      "freeze_basis": "generator_design_before_bundle_execution",
      "allowed_replacement_reasons": [
        "bundle_incomplete",
        "run_failed",
        "strict_invalid",
        "unsupported_before_measurement"
      ]
    },
    "randomization": {
      "scheme": "deterministic_rotation",
      "exchangeability": "none",
      "seed": 2000005
    }
  },
  "source": {
    "generator": "scripts/generate_matrix.py",
    "registry_template": {
      "path": "configs/analysis_registry/slice_2m_ap2.v1.json",
      "sha256": "<64 lowercase hex>"
    },
    "order_manifest": {
      "path": "order_manifest.json",
      "sha256": "<64 lowercase hex>"
    },
    "ap_rows": [
      {
        "plan_id": "AP-2",
        "path": "docs/contracts/analysis_plans.md",
        "section_sha256": "<64 lowercase hex>",
        "family_id": "FAM-2M-SHAPE-CONTRASTS",
        "claim_role": "primary",
        "selection_scope": "<verbatim AP field value>",
        "multiplicity_rule": "<verbatim AP field value>"
      }
    ]
  },
  "entries": [],
  "sentinel_links": [],
  "families": [],
  "contrasts": []
}
```

The AP section hash covers the exact UTF-8 bytes from the `### AP-2` heading
through the final row of its Field/Value table, including one terminating
newline. The snapshot fields make the historical freeze intelligible if the
contract later changes. Generation fails if the AP row cannot be parsed or the
template disagrees with its `plan_id`, base `family_id`, `claim_role`, or
named multiplicity method.

### A3. Entry object

Every generated config, including both sentinels, has exactly one entry:

```json
{
  "entry_id": "entry-2m-qwen25-1p5b-r01-short_short",
  "config": "qwen25-1p5b-r1-short_short.json",
  "config_sha256": "<sha256 of exact config bytes>",
  "run_id": "qwen25-1p5b-r1-short_short",
  "model_tag": "qwen25-1p5b",
  "planned_rep_index": 1,
  "role": "condition",
  "condition_id": "cond-2m-short_short",
  "cell_id": "cell-2m-qwen25-1p5b-short_short",
  "block_id": "block-2m-qwen25-1p5b-r01",
  "sentinel_link_id": "sentinel-2m-qwen25-1p5b-r01",
  "order_index": 2,
  "position_in_block": 2
}
```

For sentinels, `role`, `condition_id`, `cell_id`, and `entry_id` use the
start/end form from Section 1.2. `sentinel_link_id` remains non-null. Entry
order is exactly `order_manifest.executed_order`; this preserves the executed
design while the semantic IDs remain independent of ordinal block numbering.

Validation rules:

- `config` is a basename, exists beside the manifest, and its bytes match
  `config_sha256`;
- config `run_id`, model tag, repetition tag, workload name, and sentinel tags
  agree with the entry;
- `(entry_id, config, run_id)` are each unique;
- every condition cell has exactly `planned_n_blocks` distinct block IDs;
- a block has one entry for each of the four baseline conditions and exactly
  one start and one end sentinel;
- `order_index` and `position_in_block` match the linked order manifest;
- no config is omitted and no non-config sidecar is treated as a config.

### A4. Sentinel linkage object

Each model-tag/repetition block has exactly one link:

```json
{
  "sentinel_link_id": "sentinel-2m-qwen25-1p5b-r01",
  "block_id": "block-2m-qwen25-1p5b-r01",
  "start_entry_id": "entry-2m-qwen25-1p5b-r01-drift-sentinel-start",
  "end_entry_id": "entry-2m-qwen25-1p5b-r01-drift-sentinel-end",
  "linked_condition_entry_ids": [
    "entry-2m-qwen25-1p5b-r01-short_short",
    "entry-2m-qwen25-1p5b-r01-long_short",
    "entry-2m-qwen25-1p5b-r01-short_long",
    "entry-2m-qwen25-1p5b-r01-mid_mid"
  ],
  "diagnostic": "end_minus_start"
}
```

`linked_condition_entry_ids` is in manifest workload order, not execution
order. The sentinel delta is a drift diagnostic/covariate, not a claim-bearing
contrast and not part of a Holm denominator. Missing or invalid sentinels are
recorded by P2-037 and trigger the AP-2 disqualifier; they are never silently
replaced by a position covariate.

### A5. Frozen families and exact AP-2 contrast enumeration

D-053 says a family is local to an estimand. That rule is more specific than
AP-2’s older prose suggesting one combined family across request and phase
metrics. Therefore v1 creates one family instance per
`model_tag x metric/window` with six pairwise contrasts, not one 24-test
family. The base AP family ID is retained for traceability.

The four v1 confirmatory metric/window definitions are:

| `metric_tag` | metric | window class | unit | family `m` |
|---|---|---|---|---:|
| `gross_request` | `gross_energy_j` | `gross_request` | `J` | 6 |
| `idle_request` | `energy_request_j` | `idle_subtracted_request` | `J` | 6 |
| `gross_prefill` | `phase_energy_j.prefill` | `gross_phase` | `J` | 6 |
| `gross_decode` | `phase_energy_j.decode` | `gross_phase` | `J` | 6 |

The six ordered pairs are frozen in this order:

1. `long_short - short_short`
2. `short_long - short_short`
3. `mid_mid - short_short`
4. `short_long - long_short`
5. `mid_mid - long_short`
6. `mid_mid - short_long`

Crossing the four metric rows with these six pairs produces exactly 24
claim-bearing contrasts per model tag. Mean power, TTFT, and token-ratio
companions named descriptively in AP-2 are **not** silently added to this
confirmatory set; they remain exploratory unless the registry template and AP
row prospectively enumerate them. P2-037 nevertheless implements the generic
token-ratio estimands in B8 for other frozen registries.

One family object is:

```json
{
  "family_id": "FAM-2M-SHAPE-CONTRASTS",
  "family_instance_id": "fam-2m-qwen25-1p5b-gross_request",
  "plan_id": "AP-2",
  "claim_role": "primary",
  "metric_tag": "gross_request",
  "multiplicity": {
    "method": "holm",
    "alpha": 0.05,
    "q": null,
    "m": 6
  },
  "contrast_ids": [
    "ctr-ap2-qwen25-1p5b-gross_request-long_short-minus-short_short",
    "ctr-ap2-qwen25-1p5b-gross_request-short_long-minus-short_short",
    "ctr-ap2-qwen25-1p5b-gross_request-mid_mid-minus-short_short",
    "ctr-ap2-qwen25-1p5b-gross_request-short_long-minus-long_short",
    "ctr-ap2-qwen25-1p5b-gross_request-mid_mid-minus-long_short",
    "ctr-ap2-qwen25-1p5b-gross_request-mid_mid-minus-short_long"
  ]
}
```

### A6. Contrast object

Every contrast object has exactly these keys:

```json
{
  "contrast_id": "ctr-ap2-qwen25-1p5b-gross_request-long_short-minus-short_short",
  "plan_id": "AP-2",
  "family_instance_id": "fam-2m-qwen25-1p5b-gross_request",
  "claim_role": "primary",
  "metric": {
    "name": "gross_energy_j",
    "metric_tag": "gross_request",
    "window_class": "gross_request",
    "unit": "J",
    "ratio_estimand": null
  },
  "estimator": "paired_block_mean_difference_t_v1",
  "condition_a_id": "cond-2m-short_short",
  "condition_b_id": "cond-2m-long_short",
  "cell_a_id": "cell-2m-qwen25-1p5b-short_short",
  "cell_b_id": "cell-2m-qwen25-1p5b-long_short",
  "block_ids": [
    "block-2m-qwen25-1p5b-r01",
    "block-2m-qwen25-1p5b-r02",
    "block-2m-qwen25-1p5b-r03",
    "block-2m-qwen25-1p5b-r04",
    "block-2m-qwen25-1p5b-r05"
  ],
  "hypothesized_direction": "two_sided",
  "equivalence": null,
  "mde": null,
  "floor_selector": {
    "backend": "from_bundle",
    "metric": "gross_energy_j",
    "window_class": "gross_request",
    "condition_families": ["short_short", "long_short"],
    "combine": "max_all_floor_abs_and_floor_cmp",
    "transport": "require_explicit_applicable_rule"
  }
}
```

An equivalence registry replaces `equivalence: null` with
`{"margin": <positive base-unit number>, "method": "tost_v1"}`. A rank/MDE
registry replaces `mde: null` with a positive base-unit threshold and a named
source. A ratio registry uses the B8 ratio object; it never relies on the
already-divided summary field without denominator audit.

### A7. Emission point and freeze behavior

The generator sequence is normative:

1. validate the base config;
2. write/update all expected config files;
3. build and write `order_manifest.json`;
4. read the final config set and exact order-manifest bytes;
5. parse and validate the AP-2 registry template and AP-2 contract row;
6. build, self-validate, and write `analysis_manifest.json`;
7. print both manifest paths only after both writes succeed.

The builder sees the complete directory, so invoking the generator for model A
then model B yields the same final two-model manifest as B then A. The manifest
may be regenerated while no bundle from its config set exists. Once
`run_campaign` records its `manifest_id`, a changed manifest is a different
campaign design; the runner refuses to append to the old campaign log or reuse
existing matching bundles under the new ID.

The implementation should use temp-file-plus-`os.replace` for each manifest.
Cross-file atomicity is not promised, so P2-041 always verifies the order hash
inside the analysis manifest before execution. A process killed between the two
writes leaves a mismatch that fails closed on restart.

### A8. Determinism obligations

- no creation time, hostname, current Git revision, absolute path, directory
  iteration order, or random value appears;
- model tags sort lexicographically; repetitions sort numerically; entries use
  realized order; links use `(model_tag, rep)`; families use
  `(model_tag, metric-template-order)`; contrasts use the frozen pair order;
- config hashes cover exact emitted bytes; the order hash covers exact emitted
  bytes; the registry/AP hashes cover the sources specified above;
- same inputs produce byte-identical configs, order manifest, and analysis
  manifest, including when model generator invocations are reversed;
- any changed AP snapshot, registry template, config bytes, order, fixed `n`,
  or contrast enumeration changes `manifest_id`.

### A9. P2-042 tests, including mutation tests

Required tests:

1. one-model output has 30 entries, 5 sentinel links, 4 family instances, and
   24 contrasts; two-model output has 60, 10, 8, and 48 respectively;
2. every emitted config has one and only one `cell_id`, `block_id`, and
   `condition_id` entry;
3. sentinel links point to exact start/end entries and all four condition
   entries in the block;
4. the exact 24 IDs for one model equal the cross-product in A5;
5. each family’s stored `m` equals the length of its complete `contrast_ids`;
6. byte identity holds across reruns and reversed model-generation order;
7. `run_campaign.discover_configs` ignores both manifest sidecars;
8. stale/missing/tampered configs, AP-row hash mismatch, order hash mismatch,
   duplicate IDs, and a non-frozen status fail validation.

Mutation-style requirements (the test must fail against each mutation):

- delete `block_id` from one entry;
- link an end sentinel from the next repetition;
- remove one contrast while leaving `m = 6`;
- duplicate a `contrast_id` in two families;
- derive `block_id` from numeric `block_index` and then add a second model;
- omit the order-manifest hash comparison;
- allow generation time or invocation order to alter bytes;
- let `analysis_manifest.json` be discovered as a benchmark config.

## 3. Component B — P2-037 contrast and claim engine

### B1. Module and CLI layout

Use a small package so statistical policy does not accrete into
`aggregate.py` or `run_campaign.py`:

```text
joulewise/analysis_engine/
  __init__.py          public analyze_claims entry point
  inputs.py            manifest/floor validation, BundleReader access, strict checks
  estimators.py        paired means, ratios, metrology-aware intervals
  distributions.py     Student-t CDF/quantile support, exact sign-flip enumeration
  multiplicity.py      Holm and BH with frozen m
  sensitivity.py       LOO family recomputation and randomization checks
  claims.py            five-outcome evaluator and reason precedence
  artifact.py          claim_verdicts.v1 validation, canonical ID, serialization
joulewise/analysis_manifest.py  shared P2-042 manifest model/validator
```

Add a CLI subcommand:

```text
python3 -m joulewise analyze-claims \
  --analysis-manifest <config-dir>/analysis_manifest.json \
  --runs-root runs/ \
  --floor-artifact analysis/floors/<artifact>.json \
  --output analysis/claim_verdicts.json
```

The command is a pure, deterministic derivation. It does not execute a
benchmark, mutate a bundle, rewrite a floor artifact, or edit a claims index.
It exits `0` when a structurally valid artifact is written, even if every
scientific outcome is `not_resolvable`; scientific null/negative outcomes are
not process failures. It exits `2` on invalid/mismatched inputs and writes no
artifact. An optional `--legacy-l1-mechanics` flag is test/RPT-001-only and
forces the artifact-level limitation described in B13.

### B2. Inputs and closed bundle-set audit

Required inputs are exactly:

1. a valid frozen `joulewise.analysis_manifest.v1`;
2. a runs root containing the registered bundles and any scientifically
   matching extra/replacement bundles;
3. a valid P2-039 floor artifact satisfying B3.

For each registered entry, `inputs.py`:

- resolves `<runs-root>/<run_id>` only; path traversal and alternate basenames
  are rejected;
- calls the existing shared strict path (`validate_bundle(..., strict=True)`)
  and reads data through `BundleReader`; no new JSON/event/trace parser is
  permitted;
- requires summary status `succeeded` for a numeric point;
- verifies config bytes/hash and scientific identity against the manifest;
- records every missing, invalid, failed, waived, or nonnumeric point rather
  than dropping it;
- re-derives runtime token counts and stop/output-policy evidence when the
  estimand is token-normalized.

The engine also scans the runs root for configs with the same complete
scientific identity (hardware, boundary/backend, runtime, model artifact,
quantization, tokenizer, workload condition, sampler/output policy, and matrix
tags) but a run ID not registered in the manifest. This closed-set scan is
mandatory for D-062. An explicit list of hand-picked bundle paths that can omit
top-ups is not an accepted confirmatory input mode.

Unrelated bundles are ignored. Scientifically matching unregistered bundles
are classified under B11, never silently ignored.

### B3. P2-039 floor-artifact consumer interface

P2-039 owns its full schema and calculations. P2-037 requires at least this
versioned interface:

```json
{
  "schema_version": "joulewise.detection_floor.v1",
  "artifact_id": "df-<stable id>",
  "freeze_status": "frozen",
  "guard_factor": {
    "n_5_to_9": 1.0,
    "frozen_before_calibration_effects": true
  },
  "rows": [
    {
      "floor_row_id": "DF-RQ-GROSS-MID:<regime-id>",
      "status": "eligible",
      "backend": "powermetrics",
      "boundary_label": "<exact D-018 label>",
      "metric": "gross_energy_j",
      "window_class": "gross_request",
      "condition_family": "mid_mid",
      "regime": {
        "stack_id": "<stable stack identity>",
        "duration_range_s": [0.0, 0.0],
        "requested_sampling_hz": 0.0,
        "observed_cadence_range_s": [0.0, 0.0],
        "power_range_w": [0.0, 0.0]
      },
      "transport_rule": {
        "rule_id": "<stable rule>",
        "verdict": "direct",
        "allowed_consumer_regimes": ["<stable regime id>"]
      },
      "floor_abs_j": 0.0,
      "floor_cmp_j": 0.0,
      "floor_gate_j": 0.0,
      "n_abs_bundles": 10,
      "n_cmp_blocks": 10,
      "error_budget": {
        "stochastic_terms": [],
        "deterministic_bound_terms": [],
        "unknown_terms": []
      },
      "bundle_ids": [],
      "bundle_sha256s": []
    }
  ]
}
```

The numeric guard factor shown is a type placeholder, not a ruling that it is
`1.0`; P2-039 must freeze the actual positive value before calibration data.
The floor validator enforces `floor_gate_j == max(floor_abs_j, floor_cmp_j)`
within a pinned absolute floating tolerance of `1e-12` J.

For a contrast, resolve every condition family named by `floor_selector`.
Each selected row must match backend, boundary, metric, window class, and an
explicit `direct` or `transported` applicability verdict for the consumer
regime. Ambiguous, missing, smoke-only, stale, unknown, or cross-regime rows do
not match. The active floor is:

```text
F = max(all selected floor_abs_j values,
        all selected floor_cmp_j values)
```

Both term classes must participate. Deleting the comparative side is a gate
failure even if the absolute floor exists. The artifact records every selected
row ID and the computed `F`.

### B4. Paired/block estimator and degrees of freedom

For each registered difference contrast and block `i`, obtain exactly one
numeric point from cell A and cell B and calculate:

```text
d_i = y_Bi - y_Ai
d_bar = mean(d_i)
s_d = sample standard deviation(d_i)
n = number of complete registered blocks
df = n - 1
SE_repeat = s_d / sqrt(n)
repeat_point_CI95 = d_bar +/- t_(0.975, df) * SE_repeat
```

At planned `n = 5..10`, `df` is exactly `4..9`. The implementation must not
use marginal condition intervals, Welch degrees of freedom, `n_A + n_B - 2`,
normal `z`, item counts, power-sample counts, or a bootstrap percentile
interval as the primary contrast interval.

The Student-t CDF/quantile implementation must work in bare Python under D-009.
`distributions.py` may implement the regularized incomplete-beta form and a
bracketed quantile solver; tests pin common critical values and tail
probabilities. Copying the existing three-decimal critical table is acceptable
for the CI only if p-value calculations use a numerically tested CDF. All
reported values are finite JSON numbers; NaN/Infinity are structural errors.

Incomplete pairs are listed with their block and side. The engine may compute a
descriptive complete-case estimate, but a confirmatory fixed-`n` outcome is
`not_resolvable` with `fixed_n_plan_incomplete` unless a valid B11 replacement
fills the same slot. With fewer than two complete blocks, the outcome is
`not_estimable`.

### B5. When propagated metrology variance enters the interval

The primary stochastic interval is metrology-aware. It combines empirical
paired-block scatter with only explicitly stochastic, non-duplicated
metrology terms:

```text
v_i = Var_metrology(y_Bi - y_Ai)
    = v_Bi + v_Ai - 2 * cov_ABi

SE_metrology = sqrt(sum_i(v_i)) / n
SE_total = sqrt(SE_repeat^2 + SE_metrology^2)
metrology_aware_CI95 = d_bar +/- t_(0.975, n-1) * SE_total
```

The `df` remains `n - 1`. This is deliberately conservative and stable at
small `n`; v1 does not introduce a data-dependent Satterthwaite degree of
freedom.

Term policy is exact:

- `E_gross_repetition_j2` never enters `v_i`; the empirical `s_d` already owns
  repetition scatter. Adding it would double count.
- `E_idle_mean_j2` enters idle-subtracted request and derived idle-subtracted
  ratio intervals, but not gross request/phase intervals.
- another term enters only when the reducer or matching floor row labels it
  stochastic, supplies a variance in squared base units, and names its
  covariance/correlation treatment;
- per-run independent terms default to `cov_ABi = 0` only when the term schema
  says `correlation_scope = "independent_run"`;
- a paired/common calibration term may cancel only when the floor artifact
  explicitly says `contrast_treatment = "common_mode_cancel"` and the two
  bundles share the named calibration identity;
- an unknown covariance is not guessed. The term stays unknown and the claim
  fails the required error-budget gate.

Both `repeat_point_CI95` and `metrology_aware_CI95` are emitted. Claim direction
uses the metrology-aware interval.

### B6. When uncertainty remains a separate deterministic bound

Drift, interpolation/edge error, clock/anchor error expressed as energy, sensor
systematic limits without a distributional model, and any term labeled
`deterministic_bound` remain bounds. They are never squared and added to
variance.

For bound term `k`, the conservative bound on the paired mean is:

```text
B_k = mean_i(b_Aik + b_Bik)
B_total = sum_k(B_k)
decision_interval = [metrology_CI.lower - B_total,
                     metrology_CI.upper + B_total]
```

An explicit common-mode cancellation rule may replace `b_Aik + b_Bik` with
the artifact-defined residual bound. Missing/unknown required bounds make the
claim `not_resolvable`; they do not become zero.

The interpolation term has its additional D-054 gate:

```text
B_interpolation < F
and
B_interpolation < 0.5 * abs(d_bar)
```

Both inequalities are strict. The engine reports the stochastic CI,
per-term deterministic bounds, total bound, and decision interval separately.
Calling the expanded decision interval a confidence interval is forbidden.

### B7. Randomization checks that respect the design

The manifest, not the analyst, says whether a randomization check is
applicable.

- `deterministic_rotation` + `exchangeability = none` (the current Slice-2M
  design): status `not_required`; no permutation p-value is invented.
- `paired_label_swap_within_block`: with at least six exchangeable blocks,
  enumerate all `2^n` sign flips of the paired deltas at `n <= 20`. The exact
  two-sided p-value is the fraction whose absolute mean is at least the
  observed absolute mean, using a `1e-15` comparison tolerance.
- fewer than six exchangeable blocks: status `not_run`, reason
  `randomization_check_insufficient_blocks`; the t interval remains primary
  and the artifact carries the required caveat.
- stratified designs enumerate/sign-flip only within the manifest’s named
  exchangeable strata and combine the same frozen contrast statistic.
- global label shuffles, order-index shuffles, and permutations across model,
  session, unit, or nonexchangeable block boundaries are invalid.

The randomization check is sensitivity evidence, not a substitute estimator.
If it is applicable and disagrees with an otherwise adjusted t-test decision,
the five-way point outcome remains recorded, but
`claim_ready_for_l2_l3 = false` and reason
`randomization_sensitivity_disagrees` is added pending explicit adjudication.

### B8. Token-ratio estimands

A ratio contrast must freeze one of these objects in its manifest:

```json
{
  "form": "mean_of_request_ratios",
  "numerator_metric": "energy_request_j",
  "denominator": "runtime_observed_output_tokens",
  "denominator_unit": "token",
  "tokenizer_scope": "same_identity_required",
  "output_policy_scope": "same_policy_required"
}
```

or:

```json
{
  "form": "ratio_of_totals",
  "numerator_metric": "energy_request_j",
  "denominator": "runtime_observed_output_tokens",
  "denominator_unit": "token",
  "tokenizer_scope": "same_identity_required",
  "output_policy_scope": "same_policy_required"
}
```

Rules:

1. Runtime-observed counts are exact observed denominators. Config fallback,
   mixed source, missing stop reason, missing output-policy label, or tokenizer
   identity mismatch makes the governed ratio not estimable for L2/L3.
2. With `mean_of_request_ratios`, compute each request ratio `R_i = E_i/T_i`,
   pair those ratios by block, and use B4. A numerator variance becomes
   `Var(R_i) = Var(E_i)/T_i^2`. This estimand weights requests equally.
3. With `ratio_of_totals`, compute `sum(E_i)/sum(T_i)` separately by condition
   and difference them. Preserve energy/token covariance by a delete-one-block
   joint jackknife; do not divide a marginal mean energy by a marginal mean
   token count. The jackknife standard error is
   `sqrt((n-1)/n * sum((theta_-i - mean(theta_-))^2))`, with Student-t
   `df=n-1`. Add independent numerator metrology contribution as
   `sum(v_Ei)/(sum(T_i)^2)` on each side, with declared paired covariance.
4. If all denominators are identical, both point estimands coincide; the
   artifact still reports the predeclared form.
5. Output stores base SI `J/token`; presentation may render `mJ/token` with an
   explicit factor of 1000. Request energy remains the primary reader-facing
   metric per D-058.

The two ratio forms answer different questions. The engine never chooses the
one with the narrower interval after seeing data.

### B9. Holm and Benjamini-Hochberg policy

For each structurally complete frozen family:

- compute a two-sided Student-t p-value for a directional difference;
- compute `max(p_lower, p_upper)` for a TOST equivalence contrast;
- retain the frozen `m` even when some family members are missing or not
  estimable; missing p-values never shrink the denominator;
- sort finite p-values by `(p, contrast_id)` for deterministic ties.

Holm adjusted p-values are:

```text
p_adj_(i) = min(1, max_{j<=i}((m - j + 1) * p_(j)))
```

Benjamini-Hochberg adjusted p-values are:

```text
p_adj_(i) = min(1, min_{j>=i}(m * p_(j) / j))
```

with monotonicity enforced in reverse rank order. Holm rejects at stored
`alpha`; BH discovers at stored `q`. `exploratory_none` emits raw p-values and
no confirmatory rejection. A family whose enumerated contrast count differs
from `m`, whose IDs differ from the family list, or whose method/alpha/q differs
from the frozen manifest is invalid as a whole.

Adjusted rejection is necessary but not sufficient for
`direction_supported`; floor and deterministic-bound rules also must pass.

### B10. Leave-one-block-out verdict table

At full-data `n <= 10`, LOO is mandatory for every claim-bearing contrast.
Implement it as a family-wide jackknife replicate:

1. for each block used by the contrast, omit that block from every family
   contrast that uses it;
2. recompute estimators, metrology terms, floor status, p-values, and the full
   frozen-`m` multiplicity adjustment;
3. run the five-outcome evaluator again;
4. store the result under the original contrast.

Each LOO row contains:

```json
{
  "omitted_block_id": "block-2m-qwen25-1p5b-r01",
  "n_blocks": 4,
  "df": 3,
  "estimate": 0.0,
  "metrology_aware_ci95": {"lower": 0.0, "upper": 0.0},
  "decision_interval": {"lower": 0.0, "upper": 0.0},
  "floor_status": "above_floor",
  "raw_p": 0.0,
  "adjusted_p": 0.0,
  "outcome": "direction_supported",
  "influence_triggers": []
}
```

An omitted point is influential when it changes any of:

- estimate sign;
- floor status;
- adjusted rejection or equivalence decision;
- five-way outcome;
- estimate by more than `0.25 * active_threshold`, where the active threshold
  is the frozen MDE for rank/MDE-gated claims and otherwise `F`.

All triggers are reported. No LOO row replaces the headline fixed-`n` result.
A sign/floor/adjusted-verdict/outcome trigger sets
`claim_ready_for_l2_l3 = false`; a magnitude-only trigger sets
`sensitivity_status = concern` and requires a claims-index caveat but does not
mechanically alter the five-way outcome. At `n > 10`, LOO status is
`not_required`.

### B11. D-062 fixed-n audit, replacements, and permanent demotion

The engine derives the planned slots from the frozen manifest, not from how
many bundles happen to exist.

A technically invalid replacement is allowed only when all conditions hold:

1. the replacement config contains exactly one tag
   `analysis-replacement-of=<entry_id>` and one tag
   `analysis-replacement-reason=<allowed-code>`;
2. the reason is in the manifest’s frozen replacement list;
3. the original entry is collection-invalid (`incomplete`, failed status,
   strict-invalid, or unsupported before a measured result exists), not merely
   statistically inconvenient or near-floor;
4. after removing `run_id` and the two replacement tags, the replacement’s
   scientific config identity equals the original’s;
5. the replacement fills the original `block_id`/cell slot and does not create
   a sixth analysis block;
6. only one successful replacement fills a slot.

Idle contamination, cooldown cap hit, an influential observation, a wide CI,
a below-floor effect, an unexpected direction, or failed equivalence is not a
technical-invalid replacement reason.

`top_up_detected = true` when any scientifically matching unregistered bundle
is not a valid replacement, a valid original is replaced, the number of
analysis blocks exceeds planned `n`, or a post-effect manifest revision adds
slots. For every affected contrast:

- set `confirmatory_status = "demoted_exploratory"` permanently;
- retain and report the original registered fixed-`n` analysis regardless of
  direction;
- optionally report the pooled/top-up analysis under a separate
  `exploratory_pooled` object with no nominal confirmatory coverage language;
- set `claim_ready_for_l2_l3 = false` and reason
  `outcome_dependent_top_up`;
- never re-promote on a later rerun or convenience manifest.

The artifact records original, replacement, and top-up bundle IDs and the rule
that classified each. A reader can therefore reconstruct the demotion without
trusting prose.

### B12. Five-outcome claim evaluator

The evaluator is fail-closed and uses this precedence.

#### `not_estimable`

Use when the registered estimand itself cannot be calculated: fewer than two
complete blocks, missing/nonfinite metric, zero/missing runtime denominator,
unmatched paired units, invalid ratio form, or structurally invalid
manifest/floor input. The artifact may contain descriptive points but no
contrast CI.

#### `not_resolvable`

Use when an estimate exists but the evidence cannot support the registered
claim, including:

- fixed planned `n` is incomplete after allowed replacements;
- any required window evidence precheck fails or is unknown;
- cooldown/idle evidence required for the metric is missing or disqualifying;
- the matching floor row is missing, stale, smoke-only, ambiguous, or
  inapplicable under transport;
- either `floor_abs` or `floor_cmp` is missing;
- a directional point effect has `abs(estimate) <= F`;
- interpolation or another required deterministic term fails its magnitude
  gate;
- an equivalence margin is not strictly greater than `F`;
- an error-budget term or covariance required by the metric is unknown.

#### `unresolved`

Use after estimability and resolution gates pass when the registered
direction/equivalence is not supported: the decision interval includes zero,
Holm/BH does not reject/discover, a valid equivalence interval is not wholly
inside its margin, or TOST does not pass. No directional or “no difference”
claim follows.

#### `direction_supported`

Use only for a registered directional/difference contrast when all of these
hold:

- `abs(estimate) > F`;
- metrology-aware CI and the deterministic-bound-expanded decision interval
  exclude zero with the same sign;
- the frozen multiplicity rule rejects/discovers the contrast;
- every required input/gate is known and passes.

The artifact records `direction = "positive"` or `"negative"` under the
manifest’s `B - A` orientation. This outcome does not by itself authorize L2/L3
if D-062 demotion or a verdict-changing sensitivity concern is present.

#### `equivalent`

Use only for a predeclared TOST equivalence contrast when:

- margin `M > F`;
- the metrology-aware CI and decision interval both lie wholly inside
  `[-M, +M]`;
- adjusted TOST passes under the frozen family rule;
- every required input/gate is known and passes.

There is no generic `no_difference` outcome. A near-zero estimate without the
predeclared equivalence gate is `not_resolvable` or `unresolved`.

### B13. Exact claim-verdict artifact shape

The output file is `joulewise.claim_verdicts.v1`:

```json
{
  "schema_version": "joulewise.claim_verdicts.v1",
  "claim_verdicts_id": "cv-<64 lowercase hex>",
  "engine": {
    "implementation": "joulewise.analysis_engine",
    "algorithm_version": "1",
    "difference_orientation": "condition_b_minus_condition_a"
  },
  "inputs": {
    "analysis_manifest": {
      "manifest_id": "am-<id>",
      "file_sha256": "<hex>"
    },
    "floor_artifact": {
      "artifact_id": "df-<id>",
      "file_sha256": "<hex>"
    },
    "runs_root_label": "runs",
    "evidence_class": "current",
    "limitations": []
  },
  "bundle_audit": [],
  "sampling_audit": {
    "design": "fixed_n",
    "planned_n_blocks": 5,
    "registered_blocks": [],
    "valid_replacements": [],
    "unregistered_matching_bundles": [],
    "top_up_detected": false,
    "demoted_contrast_ids": []
  },
  "families": [],
  "contrasts": []
}
```

Each `bundle_audit` row has `bundle_id`, relative path, entry/slot linkage,
config and summary hashes, strict status/problems, summary status,
window-precheck status/reasons, token/stop/policy provenance when applicable,
replacement classification, and inclusion status. Paths are relative labels,
never machine-absolute paths.

Each family row has frozen method/alpha/q/`m`, enumerated IDs, finite-test
count, raw ordering, adjusted p-values, missing-test IDs, and structural
status.

Each contrast row has, in this order:

- frozen identity/AP/family/role/metric/conditions;
- bundle/block inclusion and exclusion audit;
- sampling/demotion status;
- estimator name, `n`, `df`, point estimate, `s_d`, `SE_repeat`,
  `SE_metrology`, `SE_total`, repeat CI, metrology-aware CI;
- named deterministic terms, total, and decision interval;
- floor row IDs, `floor_abs`, `floor_cmp`, active `F`, and transport verdict;
- raw/adjusted multiplicity evidence;
- randomization check;
- LOO table and sensitivity status;
- `claim_evaluation` with `outcome`, `direction`, ordered `reason_codes`,
  `claim_ready_for_l2_l3`, and `claim_level_ceiling`.

Reason arrays are sorted by the evaluator’s precedence, then lexicographically
within a precedence class. Empty/unknown values are explicit `null`; keys are
not conditionally omitted. This makes downstream lint stable.

With `--legacy-l1-mechanics`, `inputs.evidence_class` is `legacy_l1`,
`limitations` contains exactly `legacy_l1_mechanics_only`, every contrast has
`claim_ready_for_l2_l3 = false`, and `claim_level_ceiling = "L1"` regardless
of numeric output. The flag refuses any bundle outside the frozen six legacy
identities.

### B14. Stable reason-code surface

Reducer reasons are copied verbatim from `window_evidence_precheck`, including:

```text
insufficient_in_window_samples
cadence_ratio_unrecorded
cadence_ratio_below_threshold
clock_bound_unrecorded
clock_bound_exceeds_quarter_window
interpolation_bound_unrecorded
drift_term_unknown
cooldown_cap_hit
```

The engine adds this v1 closed set:

```text
analysis_manifest_invalid
analysis_manifest_not_frozen
order_manifest_hash_mismatch
config_hash_mismatch
bundle_missing
bundle_strict_invalid
bundle_status_not_succeeded
metric_missing_or_nonfinite
paired_block_incomplete
insufficient_complete_blocks
fixed_n_plan_incomplete
window_evidence_precheck_missing
campaign_cooldown_evidence_missing
idle_window_suspect
idle_window_suspect_unknown
floor_artifact_invalid
floor_row_missing
floor_row_ambiguous
floor_row_stale
floor_transport_inapplicable
floor_abs_missing
floor_cmp_missing
effect_not_above_floor
interpolation_bound_exceeds_floor
interpolation_bound_exceeds_half_effect
deterministic_bound_obscures_direction
required_error_term_unknown
required_covariance_unknown
runtime_token_denominator_required
stop_reason_required
output_policy_required
tokenizer_identity_mismatch
multiplicity_family_incomplete
multiplicity_not_rejected
equivalence_margin_not_above_floor
equivalence_not_supported
randomization_check_insufficient_blocks
randomization_sensitivity_disagrees
loo_verdict_influential
loo_magnitude_influential
outcome_dependent_top_up
legacy_l1_mechanics_only
```

**LEAD:** adopting these as stable machine vocabulary requires a D-057
amendment in the implementation landing. Until that amendment is recorded,
code must not improvise alternate spellings.

### B15. `claims_lint` and Phase-4 claims-index consumption

Extend `scripts/claims_lint.py`; do not create a competing claims linter.

Add explicit mode and arguments:

```text
--mode claim-index
--claims-index docs/phase_4/claims_index.md
--claim-verdict-dir analysis/
```

The mode is skipped when the claims-index file does not yet exist unless
explicitly requested. Once Phase 4 creates the file, CI invokes the mode
explicitly.

The Phase-4 table gains these machine columns while retaining figure/script
provenance:

| Field | Requirement |
|---|---|
| `claim_id` | stable human claim ID |
| `claim_text` | one sentence, wording matching the outcome |
| `ladder_level` | `L0` through `L4` |
| `AP_id` | frozen AP row |
| `contrast_id` | exact ID in a verdict artifact |
| `verdict_artifact` | repository-relative JSON path |
| `verdict_sha256` | exact file hash |
| `engine_outcome` | copied five-way outcome |
| `claim_role` | copied role |
| `editorial_status` | existing `supported`, `weak`, `refuted`, or `out-of-data` |
| `figures` / `script_function` / `dataset_filter` | existing regeneration chain |
| `bundle_manifest_ids` | frozen analysis/floor/bundle linkage |
| `caveat` | required for every non-clean sensitivity, demotion, legacy, or lower-level row |

Hard linter rules:

- artifact schema/hash/ID validate and `contrast_id` exists exactly once;
- AP, role, outcome, manifest ID, and floor artifact ID equal the artifact;
- L2/L3 `supported` requires outcome `direction_supported` or `equivalent`,
  `claim_ready_for_l2_l3 = true`, non-exploratory role, no D-062 demotion, and
  ceiling at least the claimed level;
- `refuted` is allowed only when a frozen directional hypothesis exists and a
  supported direction is opposite it; `unresolved` is not “refuted”;
- `not_estimable`/`not_resolvable` cannot be `supported` and must use
  `out-of-data` or `weak` with the exact artifact reason surfaced;
- `unresolved` cannot carry directional prose or `supported`;
- a `legacy_l1` artifact may populate only L0/L1 rows and must include the
  exact caveat `legacy_l1_mechanics_only`;
- changing a verdict JSON without updating its claims-index hash fails CI.

The linter checks structure and exact linkage; it emits a warning, not a hard
semantic judgment, for whether free-form claim wording faithfully expresses
“unresolved” or “not resolvable.” Human review still owns prose judgment.

### B16. P2-037 tests, including mutation tests

Core tests:

1. all worked fixtures in Section 7;
2. exact paired `df = n-1` for `n = 5..10` and pinned t critical/CDF values;
3. incomplete blocks are listed and do not turn into unpaired samples;
4. stochastic metrology terms widen the primary CI; gross repetition variance
   is not double-counted; deterministic bounds remain separate;
5. floor selection matches exact regimes, takes every named max, and rejects
   missing/ambiguous/stale transport;
6. exact within-block sign flips at `n >= 6`, correct not-run result below six,
   and deterministic-rotation not-applicable behavior;
7. Holm and BH adjusted p-values against hand-calculated families, including
   ties, missing p-values with frozen `m`, and equivalence p-values;
8. family-wide LOO recomputes adjustment and every trigger;
9. mean-of-ratios and ratio-of-totals differ on varying-denominator data and
   match their hand calculations;
10. D-062 valid replacements fill a slot; invalid replacements/top-ups demote,
    preserve the original fixed-`n` result, and never re-promote;
11. artifact bytes/ID are deterministic and contain no absolute paths;
12. claim-index lint accepts a correctly linked supported row and rejects every
    invalid status/outcome/demotion/hash combination.

Required mutation tests (each mutant must make at least one test red):

- replace paired differences with difference of marginal means/intervals;
- use `df = n_A + n_B - 2` or `z = 1.96`;
- ignore `E_idle_mean_j2` in the ratio fixture;
- add `E_gross_repetition_j2` a second time;
- convert drift/interpolation bounds to variances;
- delete the `floor_cmp` comparison or use `min(floor_abs, floor_cmp)`;
- change either interpolation `<` gate to presence-only;
- permute labels globally instead of within exchangeable blocks;
- omit LOO, or recompute one contrast without family multiplicity;
- reduce Holm/BH `m` when a family member is not estimable;
- choose mean-of-ratios vs ratio-of-totals after observing denominators;
- accept configured token counts or mixed tokenizer identity;
- pool a top-up while retaining confirmatory status;
- call an unresolved or below-floor effect `direction_supported`;
- let a missing/unknown gate input pass;
- allow an L2/L3 claims-index row to point at legacy-L1 mechanics output.

## 4. Component C — P2-041 campaign verdict split

### C1. Scope boundary

`run_campaign.py` answers two pre-analysis questions only:

1. Was the expected evidence collected in usable bundles?
2. Are the registered bundle set and reducer-level evidence inputs ready to be
   handed to P2-037?

It does not calculate a contrast, floor gate, p-value, multiplicity result,
equivalence result, or reader-facing claim. Therefore the positive second
verdict is named `ready_for_analysis`, not `claim_supported` or `publishable`.

### C2. Member classification split

Replace the single `quality_flags`/`usable` conflation with:

- `collection_integrity_flags`: status failure, strict invalidity, prompt-hash
  mismatch/error, missing expected bundle, malformed summary, config/manifest
  mismatch;
- `claim_evidence_flags`: reducer precheck reasons, cooldown cap state,
  metric-specific idle suspicion/unknown state, and missing planned slots.

`idle_window_suspect` and a reducer precheck failure do not erase raw evidence
or make a strict-valid succeeded bundle collection-invalid. They make the
affected claim inputs not ready. A prompt-hash mismatch remains a collection
integrity failure because scientific workload identity is wrong.

Waivers remain visible and never support claim readiness. An all-waived
campaign is `invalid` for collection and `not_ready_for_analysis`.

### C3. Exact collection verdict rules

Given expected manifest members and existing waiver behavior:

1. `blocked`: at least one expected member is missing or incomplete;
2. `invalid`: any unwaived member has a collection-integrity failure, or no
   unwaived usable member exists;
3. `partial`: at least one member is collection usable and at least one other
   member is explicitly waived, with no missing or unwaived-invalid member;
4. `usable`: every expected member is collection usable and none is waived.

This preserves the safety character of the old verdict while removing its
publication claim. Exit status remains operational: `blocked`/`invalid` or an
execution failure returns nonzero; `usable` and waiver-only `partial` may return
zero. Claim-input readiness does not change the campaign process exit code.

### C4. Exact readiness rules

`claim_readiness.verdict` is:

- `not_assessed` when no analysis manifest exists or it has no claim-bearing
  contrasts. This is the required result for an otherwise clean arbitrary
  one-bundle campaign;
- `not_ready_for_analysis` when a manifest exists but any rule below fails;
- `ready_for_analysis` only when every registered contrast has the complete
  planned bundle slots and reducer-level inputs needed for P2-037.

For each registered contrast, readiness requires:

1. valid frozen analysis manifest and matching order/config hashes;
2. collection verdict `usable` (waived evidence is not claim evidence);
3. all planned fixed-`n` blocks present, with one usable A and B member;
4. the metric-specific `window_evidence_precheck` object exists and has
   `eligible = true` for every member/window used;
5. all embedded stable reasons are empty;
6. `cooldown_cap_hit` is explicitly false where a cooldown gate was required;
   true fails, and missing/`null` fails unless a manifest-declared first-run
   exemption applies;
7. for idle-subtracted metrics, `idle_window_suspect` is explicitly false and
   drift evidence is known; true or unknown fails;
8. for gross request/phase metrics, idle-drift and idle-suspicion evidence are
   not required (STA-5); shared thermal/cooldown evidence still applies;
9. token-ratio contrasts have runtime-observed count source, stop reason,
   output-policy label, and tokenizer identity;
10. no unregistered scientifically matching bundle/top-up is present without
    valid replacement tags.

P2-041 does not require the floor artifact. Floor readiness and claim outcome
belong to P2-037. Console text and JSON must say that explicitly.

### C5. Rename and summary migration

The current helper/object is an evidence precheck, not a claim evaluator.

Required rename:

```text
_window_claim_eligibility -> window_evidence_precheck
_windows_claim_eligibility -> windows_evidence_precheck
summary.claim_eligibility -> summary.window_evidence_precheck
```

The new summary object must be metric-specific after P2-040:

```json
{
  "gross_request": {},
  "idle_subtracted_request": {},
  "phase": {},
  "item": {},
  "block": {},
  "level": {}
}
```

New reducers write only `window_evidence_precheck`. `BundleReader` and strict
comparison accept the legacy field for the frozen six legacy bundles and map
it to an internal precheck with `source_field = "claim_eligibility"`; that
mapping never yields `ready_for_analysis` and carries
`legacy_precheck_not_claim_evaluator`. Current-era bundles with only the old
field are not ready and must be re-reduced. Update
`docs/contracts/run_bundle_layout.md`, schema tests, and strict additive-field
tolerance in the same landing.

Do not retain a private alias named `_window_claim_eligibility`; tests must
grep/import the new name so the misleading term actually retires.

### C6. Cooldown provenance gap — premise correction and open question

This is a blocking design fact for the existing Slice-2M path:

1. `generate_matrix.py` deliberately emits each interleaved condition as a
   separate config with `workload_profile.repetitions = 1`.
2. `run_campaign.py` launches a separate `joulewise run` process for each
   config.
3. The accepted D-014 cooldown gate is implemented only inside
   `controller.run_experiment`, between repetitions of one config where
   `repetitions > 1`.
4. Therefore the controller gate never runs between the independent matrix
   configs, and their absent `cooldown_cap_hit` fields mean **not measured**, not
   “gate recovered.”

Required v1 behavior: for every confirmatory contrast whose paired blocks were
collected through this path, P2-041 returns `not_ready_for_analysis` with
`campaign_cooldown_evidence_missing`. P2-037 repeats the fail-closed check and
cannot be overridden by the campaign’s collection-usability verdict. A
manifest-declared first-run exemption may apply only to the first physical run
in a session; it does not exempt all `repetitions = 1` configs.

**OPEN QUESTION / LEAD:** assign one of these before real matrix claim
readiness is possible:

- implement a campaign-level D-014 recovery gate in `run_campaign.py`, with
  raw cooldown evidence and a tri-state result attached to the following
  manifest entry; or
- redesign execution so interleaving and semantic block identity survive while
  one controller-owned experiment runner performs the between-member gates.

Merely writing `cooldown_cap_hit = false`, sleeping a fixed interval, or
inferring recovery from start/end sentinels is not an acceptable resolution.
Until an owner and implementation land, the collection may be `usable`, but
confirmatory claim inputs remain not ready.

### C7. Exact campaign-verdict v2 JSON shape

The final campaign log row becomes:

```json
{
  "schema_version": "joulewise.campaign_verdict.v2",
  "record_type": "campaign_verdict",
  "status": "verdict",
  "timestamp": "<operational log timestamp>",
  "analysis_manifest": {
    "manifest_id": "am-<id>",
    "file_sha256": "<hex>",
    "validation": "valid"
  },
  "collection": {
    "verdict": "usable",
    "reasons": [],
    "categories": {
      "usable": [],
      "waived": [],
      "failed": [],
      "missing": []
    }
  },
  "claim_readiness": {
    "verdict": "not_ready_for_analysis",
    "reasons": ["campaign_cooldown_evidence_missing"],
    "required_contrast_ids": [],
    "ready_contrast_ids": [],
    "not_ready_contrasts": [],
    "note": "This verdict checks analysis inputs only; P2-037 decides claim outcomes."
  },
  "sampling_audit": {
    "design": "fixed_n",
    "planned_n_blocks": 5,
    "registered_bundle_ids": [],
    "unregistered_matching_bundle_ids": [],
    "valid_replacements": [],
    "top_up_suspected": false
  },
  "members": []
}
```

`analysis_manifest` is `null` when readiness is `not_assessed`.
`not_ready_contrasts` rows contain `contrast_id`, affected member IDs, and
ordered stable reasons. Member rows contain separate collection and
claim-evidence classifications.

The timestamp is allowed here because `campaign_log.jsonl` is an operational
append-only log, not a deterministic derived artifact. It is not copied into
the P2-037 result identity.

Console output becomes:

```text
COLLECTION VERDICT:
  verdict: usable
CLAIM-INPUT READINESS:
  verdict: not_ready_for_analysis
  reason: campaign_cooldown_evidence_missing
  note: P2-037 decides statistical claim outcomes.
```

### C8. Retirement path for `publishable`

- Delete `publishable` from `verdict_for`, console text, taxonomy, tests, and
  current documentation examples.
- Rename the helper to `collection_verdict_for`; add a separate
  `claim_readiness_for`.
- Existing log rows are immutable historical evidence. A legacy log reader
  maps `verdict = "publishable"` only to
  `collection.verdict = "usable"` and
  `claim_readiness.verdict = "not_assessed"`, with migration reason
  `legacy_publishable_meant_collection_usable_only`.
- Never map old `publishable` to `ready_for_analysis`,
  `direction_supported`, `equivalent`, or a Phase-4 `supported` row.
- The test currently named
  `test_verdict_block_content_for_publishable_campaign` becomes a one-bundle
  regression test: collection `usable`, readiness `not_assessed`, no string
  `publishable` in stdout or the new JSON.

### C9. P2-041 tests, including mutation tests

Required tests:

1. one strict-valid succeeded bundle with no analysis manifest is collection
   `usable` and readiness `not_assessed`;
2. a complete manifest set with clean metric-specific prechecks is
   `ready_for_analysis` in a synthetic fixture that explicitly supplies
   cooldown evidence;
3. cap hit true, required cap state unknown, or a stable reducer reason makes
   only readiness fail while preserving collection usability;
4. the current interleaved `repetitions = 1` matrix path yields collection
   `usable` but readiness `not_ready_for_analysis` with
   `campaign_cooldown_evidence_missing`;
5. idle suspicion true/unknown blocks idle-subtracted readiness but not gross
   request readiness;
6. prompt hash mismatch remains collection invalid;
7. missing planned member is collection blocked and readiness not ready;
8. any waiver prevents full readiness; all-waived remains invalid;
9. analysis/order/config hash mismatch fails closed;
10. unregistered matching bundle is surfaced as suspected top-up;
11. legacy v1 log mapping never upgrades claim readiness;
12. new summary field migration and current-era old-field failure are tested;
13. `publishable` is absent from current code paths and v2 taxonomy.

Required mutation tests:

- mark one bundle ready despite `window_evidence_precheck.eligible = false`;
- ignore `cooldown_cap_hit` or treat null as false;
- treat all independent `repetitions = 1` matrix configs as first-run-exempt;
- make gross request require idle drift;
- let idle suspicion poison collection usability instead of metric readiness;
- mark a one-bundle/no-manifest campaign ready;
- let a waiver support readiness;
- discover `analysis_manifest.json` as a config;
- preserve the old `publishable` verdict or map it to a supported claim.

## 5. Interfaces pinned between the three components

| Producer | Consumer | Pinned contract |
|---|---|---|
| P2-042 | P2-041 | manifest schema/ID, entry/config/order linkage, planned slots, contrast IDs, metric-specific required windows |
| P2-042 | P2-037 | complete frozen families, exact `m`, block/cell/condition identity, estimator orientation, ratio/equivalence/MDE/floor selectors |
| P2-041 | P2-037 | campaign log is audit context only; P2-037 revalidates bundles and does not trust a positive readiness verdict as proof |
| P2-039 | P2-037 | versioned floor rows, exact metric/window/regime transport, both floor terms, error-budget term classifications |
| reducer/P2-040 | P2-041 and P2-037 | `window_evidence_precheck`, stable reasons, metric-specific drift rules, joint-edge interpolation bound, runtime token precedence |
| P2-037 | claims_lint/Phase 4 | deterministic `claim_verdicts.v1`, artifact hash, exact outcome/role/demotion/ceiling, bundle/manifest provenance |

P2-037 always re-runs structural validation, strict bundle validation, and
reason/floor checks. P2-041’s positive readiness is useful operator feedback,
not a security boundary and not a cached statistical decision.

## 6. File-target summary

### P2-042

- `configs/analysis_registry/slice_2m_ap2.v1.json` (new)
- `joulewise/analysis_manifest.py` (new)
- `scripts/generate_matrix.py`
- minimal sidecar exclusion in `scripts/run_campaign.py`
- `scripts/claims_lint.py`
- `tests/test_analysis_manifest.py` (new)
- `tests/test_generate_matrix.py`
- `tests/test_run_campaign.py`

### P2-041

- `scripts/run_campaign.py`
- `joulewise/reduce.py` (rename seam; metric behavior itself remains P2-040)
- `joulewise/schemas.py`
- `joulewise/bundle_read.py` and `joulewise/cli.py` strict migration allowance
- `docs/contracts/run_bundle_layout.md`
- `tests/test_run_campaign.py`
- `tests/test_uncertainty_p2029.py`
- `tests/test_schemas.py`, `tests/test_bundle_read.py`, and strict CLI tests

### P2-037

- new `joulewise/analysis_engine/` package from B1
- `joulewise/cli.py` and CLI tests
- `scripts/claims_lint.py`
- `docs/phase_4/claims_index.md` only when the first real index row is created;
  no placeholder “supported” row
- new `tests/test_analysis_engine.py`,
  `tests/test_analysis_multiplicity.py`,
  `tests/test_analysis_claims.py`, and
  `tests/test_claims_index_lint.py`
- shared fixtures under `tests/fixtures/analysis/`; no live bundle is modified

## 7. Normative worked fixtures

### 7.1 Paired contrast defeats marginal-interval reasoning

Input, paired by block:

```text
A = [100, 200, 300, 400, 500]
B = [101, 201, 301, 401, 501]
d = B - A = [1, 1, 1, 1, 1]
n = 5, df = 4, t_.975,4 = 2.776
```

Expected:

```text
estimate = 1 J
s_d = 0 J
SE_repeat = 0 J
repeat_point_CI95 = [1, 1] J
metrology_aware_CI95 = [1, 1] J when no added stochastic term exists
```

Each marginal half-width is approximately `196.292842 J`; marginal overlap is
irrelevant. A mutant using marginal intervals must fail this fixture.

### 7.2 Zero-width request ratio must widen under propagated variance

Five requests each have `E = 10 J`, exact runtime-observed `T = 100` output
tokens, and independent numerator metrology variance `1 J^2`.

```text
R_i = E_i/T_i = 0.1 J/token = 100 mJ/token
repeat-point scatter = 0
Var(mean R) = (5 * 1 J^2 / 100^2) / 5^2
            = 1 / (5 * 100^2)
SE_total = sqrt(1/5) / 100
         = 0.004472135955 J/token
half-width = 2.776 * SE_total
           = 0.012414649411 J/token
```

Expected metrology-aware result:

```text
0.100000 +/- 0.01241465 J/token
100.00 +/- 12.41 mJ/token
CI = [87.58535, 112.41465] mJ/token
```

The repeat-point CI `[100, 100] mJ/token` is also emitted but cannot be used as
the claim interval. A mutant that leaves propagated variance as detached
metadata fails.

### 7.3 The recorded 4 J interpolation bound fails the floor/effect gate

A 4-second window sampled at 1 Hz at constant 8 W has adequate sample count and
cadence in the reviewed code and records a 4 J one-edge interpolation
sensitivity. For the C-027 counterexample, let:

```text
active floor F = max(floor_abs=1 J, floor_cmp=1 J) = 1 J
claimed paired effect = 2 J
allowed interpolation bound must be below min(F, abs(effect)/2)
                                    = min(1 J, 1 J)
                                    = 1 J
observed bound = 4 J
```

Expected:

```text
outcome = not_resolvable
reasons include interpolation_bound_exceeds_floor
reasons include interpolation_bound_exceeds_half_effect
```

Presence of a numeric bound is not eligibility. After P2-040 fixes joint-edge
perturbation, the same constant-power geometry may produce an 8 J conservative
bound; that also fails. This fixture pins the gate, not the old under-bound.

### 7.4 False-effect guard arithmetic remains a P2-039 fixture

For absolute energies `[10,10,10,10,20]`, residuals are
`[-2,-2,-2,-2,8]`, sample residual standard deviation is
`sqrt(20) = 4.472135955`, and the unguarded one-new-observation term at `n=5`
is approximately `13.59956705 J`. P2-039 multiplies by its prospectively
frozen `5 <= n < 10` guard factor. P2-037 only validates/consumes the result;
it must not recompute with a factor chosen after seeing these values.

## 8. Landing and verification plan

### 8.1 Recommended order

Keep the requested order, with prerequisites made explicit:

1. **P2-042 first.** Land the schema/validator/template, deterministic
   generator output, exact AP-2 contrast set, and the minimal run-campaign
   sidecar-discovery shim. This gives both later components one stable input.
2. **P2-041 second.** Land the verdict split and migration on top of the
   manifest. It can correctly report `not_ready_for_analysis` before P2-037
   exists. Do not imply that the positive readiness verdict is a claim.
3. **P2-037 third.** Land the pure analysis package, P2-039 consumer, artifact,
   and claims-index lint integration.

Repository-order prerequisites still apply: P2-040 must supply the corrected
metric-specific precheck/joint-edge/token behavior, and P2-039 must freeze its
numeric guard factor and artifact schema before P2-037 is accepted. AP-EDIT
must synchronize D-053/D-062 prose before a real confirmatory manifest is
frozen. If those prerequisites are not ready, P2-042 may land against synthetic
schema fixtures, but no real campaign manifest is declared execution-ready.

An alternate `P2-042 -> P2-037 -> P2-041` order was rejected because it leaves
the live campaign runner emitting the known misleading `publishable` verdict
for longer and makes the engine’s input semantics harder for operators to see.

### 8.2 Per-landing verification

Each code landing runs focused tests plus:

```text
python3 -m unittest discover -s tests
python3 scripts/claims_lint.py --mode ap --mode registry --mode analysis-registry
```

After P2-037 adds the Phase-4 mode, also run a synthetic claims-index fixture:

```text
python3 scripts/claims_lint.py --mode claim-index \
  --claims-index <synthetic-index> \
  --claim-verdict-dir <synthetic-artifacts>
```

No implementation landing is complete on unit-test count alone. Its run report
must list the mutation operators exercised and show that each named mutant made
a targeted test fail.

### 8.3 Acceptance cut line

The trio is implementation-complete only when:

- generated matrices carry a deterministic, frozen, complete registry;
- a one-bundle campaign can no longer be called publishable or ready for
  confirmatory analysis;
- a current-era manifest/bundle/floor fixture flows end to end to a
  deterministic five-outcome artifact;
- the three numeric fixtures match Section 7;
- every confirmatory family preserves its frozen denominator under missing
  data;
- a simulated top-up permanently demotes while retaining original fixed-`n`
  output;
- claims-index lint refuses an L2/L3 row that lacks a clean linked artifact;
- the six real bundles, if used in the vertical slice, remain visibly
  `legacy_l1_mechanics_only`.

## 9. Deviations and open questions for lead adjudication

### 9.1 Deviations already ruled by named decisions

These should be corrected, not re-decided:

1. Clear “pending ratification” on the D-053 amendments in
   `analysis_plans.md` and `measurement_methodology.md`.
2. Replace outcome-dependent top-up language in AP rows/packs with D-062
   fixed-`n` and permanent demotion.
3. Replace Phase-4 marginal-CI/no-difference prose with the five-way evaluator.
4. Rename `claim_eligibility` to `window_evidence_precheck`; it never was a
   complete claim gate.
5. Retire `publishable` as current machine vocabulary.

### 9.2 **LEAD** decisions required before implementation closes

1. **AP-2 family split.** This spec follows D-053’s local-estimand rule and
   uses four six-test family instances per model. AP-2 currently reads like
   one 24-test family. Ratify the split (recommended) and amend AP-2, or direct
   one combined `m=24` family. Implementers may not choose opportunistically.
2. **Campaign-level cooldown owner.** Either add a cooldown gate/provenance
   path between `repetitions=1` matrix configs, or accept that generated-matrix
   claim readiness remains fail-closed. This is outside a verdict-only patch
   but blocks real confirmatory readiness. See C6.
3. **D-057 vocabulary amendment.** Ratify the B14 engine/campaign reason codes
   or provide a revised closed set before code lands.
4. **P2-039 exact schema alignment.** Confirm that its producer schema exposes
   the B3 minimum fields and explicit covariance/contrast treatment. If its
   names differ, amend this spec and P2-039 together; do not add heuristic
   aliases.
5. **AP-2 confirmatory metrics.** This spec freezes gross request,
   idle-subtracted request, gross prefill, and gross decode. Mean power, TTFT,
   and token ratios stay exploratory. Ratify or enumerate them prospectively
   with their own estimand-local families.
6. **Sensitivity consequence.** This spec blocks L2/L3 on verdict-changing LOO
   or randomization disagreement, while magnitude-only LOO influence requires
   a caveat. Ratify this conservative policy or state the exact alternate
   claim ceiling.

### 9.3 Deferred without blocking the v1 trio

- named mixed/hierarchical models for future real nested dependence;
- group-sequential analysis beyond the schema-reserved D-062 option;
- automatic natural-language verification of a claim sentence;
- cross-boundary model contrasts until calibration manifests exist;
- item-window energy BH inference, which D-053/AP-5 keeps exploratory without
  a repeated-bundle/block design;
- changing the primary t interval after Phase-4 bootstrap sensitivity. Any
  change is a prospective decision and algorithm-version bump.

## CHECKS PERFORMED

- Read the targeted run-state/queue/M0/source-of-truth material and confirmed
  the stop card is cleared and the worktree began clean.
- Read D-014, D-037, D-038, D-053, D-054, D-057, D-058, D-059, and D-062;
  the analysis-plans, claims-ladder, token-normalization, measurement-method,
  run-bundle, and detection-floor contracts; C-027 B4/disposition; and all
  cited STATS findings/counterexamples.
- Inspected the cited generator, campaign runner, reducer precheck/token paths,
  aggregator propagation path, shared BundleReader/strict validator, schema,
  claims linter, controller cooldown runner, and targeted tests.
- Independently recomputed: paired CI `[1,1]`; marginal half-width
  `196.292842 J`; ratio SE `0.004472135955 J/token` and half-width
  `12.414649 mJ/token`; the 4 J interpolation-vs-floor/effect failure; and the
  unguarded `13.599567 J` small-`n` false-effect guard example.
- Static/design checks only. No hardware or campaign command was run, no
  corpus bundle was modified, and no legacy result was promoted above L1.
