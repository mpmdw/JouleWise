# Checkpoint metrics spec

Status: draft. Scope: suite checkpoint metrics, affine envelope gates, and
machine-readable analysis outputs derived from strict-valid suite bundles. The
shipped `envelope_gate.v1` artifact in `joulewise/envelope_gate.py` (PR #23) is
the first concrete instance of this checkpoint-artifact class; the
`suite_checkpoint.v1` sketch below remains a draft shape for later
checkpoints.

## Purpose

Checkpoint metrics turn suite bundles into small, auditable go/no-go artifacts
before expensive campaigns run. They are not new measurement primitives. They
consume strict-valid suite bundles that also contain reducer-emitted
`summary_metrics.json.suite_metrics`. Strict validation alone does not
guarantee checkpoint readiness because `suite_metrics` remains optional for
historical compatibility.

The first concrete consumer is the affine smoke envelope gate queued as the
P2-010 remainder: emit `envelope_validated` or
`envelope_failed([codes])`, exclude sentinel-tagged items from level
denominators, and report E1-E4 gates with E5 advisory until the smoke size can
support it.

## Inputs

Required bundle inputs:

- `suite_manifest.json`: canonical effective manifest, hash-linked through the
  config and metadata.
- `events.jsonl`: suite, block, level, and item markers inside the measured
  sampling window.
- `outputs/suite_items.jsonl`: item status, prompt source, BOS presence,
  prompt token hash, response hash/text, stop reason, token counts, and token
  timestamps.
- `summary_metrics.json`: whole-request metrics plus optional
  `suite_metrics`.

Required campaign inputs:

- A list of bundle paths or an experiment manifest whose members can be
  resolved to bundle paths.
- Expected suite profile and effective manifest hash.
- Optional floor artifact once P2-015 lands. Before that, floor-dependent
  gates must report `floor_source: none_pending_P2-015` or equivalent.

## Output artifact

Checkpoint tools should write one deterministic JSON artifact per analysis run,
preferably outside the immutable run bundle unless the artifact is produced by
a formally defined post-hoc analysis command. Determinism applies to semantic
fields for the same inputs; if wall-clock provenance such as `generated_at` is
included, consumers must ignore it for equality, or the timestamp must live in
a separate run log.

Suggested shape:

```json
{
  "schema_version": "suite_checkpoint.v1",
  "checkpoint_id": "affine_smoke_envelope_v1",
  "verdict": "envelope_validated",
  "failure_codes": [],
  "advisory_codes": [],
  "suite_profile": "affine_smoke_v1",
  "suite_manifest_sha256": "...",
  "bundle_ids": ["..."],
  "strict_valid_bundle_count": 5,
  "floor_source": "none_pending_P2-015",
  "sentinel_excluded_count": 10,
  "levels": [
    {
      "level_id": "L01",
      "distinct_item_count": 8,
      "execution_count": 40,
      "status_counts": {"succeeded": 40},
      "malformed_count": 0,
      "capped_count": 0,
      "correct_count": null,
      "identifiability": "identifiable",
      "energy_gross_j": null,
      "checks": {"E1": "pass", "E2": "pass"}
    }
  ],
  "provenance": {
    "tool": "joulewise-affine-envelope-gate",
    "version": "draft",
    "generated_at": "YYYY-MM-DDTHH:MM:SSZ"
  }
}
```

The exact field list may change during implementation, but the artifact must
make denominator choices explicit. In particular, `distinct_item_count` and
`execution_count` must both be visible whenever repeated bundles are involved.

## Metric rules

- Whole-suite `gross_energy_j` and `energy_request_j` remain request-window
  metrics.
- Suite item, block, and level energies remain gross-only attribution evidence.
- Item windows are not independent energy replicates. Repeated whole-suite
  bundles are the uncertainty unit unless an analysis plan explicitly says
  otherwise.
- Per-item token-normalized energy claims are out of scope.
- `below_floor` is a reducer/analysis outcome, not a runtime item status.
- Effects below `max(floor_abs_j, floor_cmp_j)` are `not_resolvable`, not
  "no effect."

## Affine envelope gates

Draft gate vocabulary:

- `E1_level_shape_valid`: every non-sentinel level has the expected distinct
  item count and manifest grouping.
- `E2_stop_distribution_valid`: emitted-token and stop-reason distributions do
  not show a level-specific output-length artifact large enough to invalidate
  the controlled envelope.
- `E3_status_distribution_valid`: malformed/runtime-failed items are absent or
  below the predeclared tolerance; malformed counts are reported even when the
  checkpoint remains usable.
- `E4_sentinel_exclusion_valid`: items tagged `sentinel` are excluded from
  level denominators and reported separately.
- `E5_correctness_guard_advisory`: correctness denominator guard is reported
  when scorer annotations are available, but smoke sizing may yield
  `not_evaluable`.

`E5` must not silently become a pass. If the smoke suite lacks enough scored
distinct items for energy-per-correct, it reports `not_evaluable`.

## Acceptance criteria

- Consumes only strict-valid suite bundles with reducer-emitted
  `suite_metrics`.
- Fails closed on manifest hash mismatch, wrong suite profile, missing
  `suite_metrics`, malformed `outputs/suite_items.jsonl`, or missing item
  annotations required by the specific checkpoint.
- Emits one machine-readable verdict: `envelope_validated` or
  `envelope_failed`.
- Includes all failure codes that fired, not only the first one.
- Keeps sentinel accounting separate from level denominators.
- Records whether floor gates were applied, pending, or not applicable.
- Does not modify run bundles unless a sanctioned post-hoc mutation rule is
  added later.

## Rationale

The suite substrate already preserves enough evidence to re-derive these
checkpoint judgments. A separate checkpoint artifact avoids bloating
`summary_metrics.json` with workload-specific logic while still giving campaign
operators a crisp gate before quiet-window time is spent.

Rejected alternatives:

- Put affine-specific gates directly in the reducer. Rejected because it would
  make the generic reducer own workload semantics.
- Treat item windows as the sample size. Rejected by the existing analysis
  plans and pseudo-replication rule.
- Store only a prose verdict in a run report. Rejected because later scripts and
  reviewers need machine-readable failure codes.

## Revisit triggers

- P2-015 floor calibration lands.
- Full affine scored ladder is promoted from deferred to active.
- A checkpoint needs accuracy/correctness semantics that cannot be represented
  in sidecars without a manifest schema change.
