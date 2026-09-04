```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Floor lineage is a missing authorization invariant at the canonical claim boundary; the branch-local repair left a sibling verdict bypass.",
  "workspace": {
    "base_requested": "4f6b23ba064616db737ae711e6873beafec7c270",
    "base_mode": "exact",
    "head_start": "4f6b23ba064616db737ae711e6873beafec7c270",
    "head_end": "4f6b23ba064616db737ae711e6873beafec7c270",
    "upstream_end": "4f6b23ba064616db737ae711e6873beafec7c270",
    "branch": "feat/2026-09-04-gamma-claim-renderer"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-gamma-renderer/05-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "result": "REDESIGN_REQUIRED",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Floor lineage is enforced as branch-local rendering policy instead of source authorization",
        "file_line": "joulewise/results_fill_gamma.py:522-526",
        "text": "The canonical claim validator authenticates the embedded floor bytes but does not bind copied resolutions to authenticated cells; the renderer performs that join after deriving a verdict and expressly emits the verdict when the join fails.",
        "cure_shape": "Make the cross-artifact cell join part of one pre-render authorization seam and pass only authorized projections to all render branches."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n 'SCHEMA_VERSION = \"joulewise\\.detection_floor_artifact\\.v2\"|def authenticate_floor_artifact_bytes|def validate_floor_artifact|def validate_claim_verdicts\\(|if not lineage_valid|result\\[token_names\\[-1\\]\\] = verdict' joulewise/detection_floor.py joulewise/analysis_engine/inputs.py joulewise/analysis_engine/artifact.py joulewise/results_fill_gamma.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/results_fill_gamma.py:523:    if not lineage_valid:",
          "joulewise/results_fill_gamma.py:525:            result[token_names[-1]] = verdict",
          "joulewise/results_fill_gamma.py:643:    result[token_names[-1]] = verdict",
          "joulewise/analysis_engine/artifact.py:945:def validate_claim_verdicts(",
          "joulewise/analysis_engine/inputs.py:868:def authenticate_floor_artifact_bytes(",
          "joulewise/detection_floor.py:98:SCHEMA_VERSION = \"joulewise.detection_floor_artifact.v2\"",
          "joulewise/detection_floor.py:4148:def validate_floor_artifact("
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)if not lineage_valid:.*result\\[token_names\\[-1\\]\\] = verdict.*def validate_claim_verdicts.*def authenticate_floor_artifact_bytes.*def validate_floor_artifact"
      }
    }
  ],
  "flags": []
}
```

## Findings

### F1 — blocker — floor lineage is not an authorization invariant

#### Q1 — Structural cause and the repository's floor proof

“Floor-lineage authorization” means more than validating a self-consistent copy of a floor inside `claim_verdicts`. The authority for the floor of a named cell is the exact `joulewise.detection_floor_artifact.v2` object (`joulewise/detection_floor.py:98`): its closed cell schema carries `cell_id`, `eligibility`, `floor_abs_j`, `floor_cmp_j`, `floor_gate_j`, the cell key, source regime, and provenance (`joulewise/detection_floor.py:1831-1852`). Its relevant digest spine includes `condition_family_sha256`; component `bundle_sha256`/`config_sha256` and `whole_window_evaluation_basis_sha256`; calibration-plan, order-manifest, campaign-log, extraction, and bundle-set hashes; and `stack_identity_sha256` (`joulewise/detection_floor.py:1863-1966,2009-2034`). `validate_floor_artifact` checks the closed schema, re-computes the floor mathematics and compositions, and validates those provenance bindings (`joulewise/detection_floor.py:4148-4250`; component digest enforcement at `:3425-3518`).

The claim carrier binds that floor artifact as exactly `{artifact_id, file_sha256, embedded_bytes_base64}` (`joulewise/analysis_engine/artifact.py:90-91`). `authenticate_floor_artifact_bytes` computes SHA-256 over the exact decoded bytes, compares `file_sha256`, strictly parses without duplicate keys, calls `validate_floor_artifact`, checks `artifact_id`, reopens launch-lineage receipts when present, and returns the authenticated cells/root set (`joulewise/analysis_engine/inputs.py:868-942`). `validate_claim_verdicts` already invokes that function on the embedded bytes (`joulewise/analysis_engine/artifact.py:994-1055`), but it retains only the root IDs and then validates the claim-side floor copies against one another (`:2165-2700`); it never proves that an `exact` resolution's `source_cell_ids` and three floor values equal the named authenticated cell.

That missing cross-artifact invariant is why both attacks can be re-content-addressed while `validate_claim_verdicts(...) == []`. Round 1 put the join in `_source_bound_floor` (`joulewise/results_fill_gamma.py:396-472`), downstream of source validation and inside per-contrast rendering. `_render_contrast` derives a partial/refusal verdict first (`:501-520`) and its failed-lineage branch then deliberately emits that verdict (`:522-526`); the supported numeric branch was repaired, but the sibling outcome branch retained authority. This is not merely a missed conditional: raw claim data, authorization, and emission coexist in one branchy function, so every new outcome site can accidentally become another authorization site.

#### Q2 — Is R2/the amendment the cause?

R2 is materially underspecified at this boundary. Its operative four clauses name B, its carrier, `F+B`, the symmetric family, and prose (`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:13-17`), but never names `inputs.floor_artifact`, `joulewise.detection_floor_artifact.v2`, `file_sha256`, `artifact_id`, `authenticate_floor_artifact_bytes`, or the source-cell equality join. The amendment changes only the B carrier and its `claim_verdicts_sha256` join (`docs/process_traces/2026-09-04-paper-i/07-magistrate-rulings-addendum.md:3-4`).

That omission contributed to the first miss, despite the adopted design text saying F is the “externally cross-checked” arm maximum and requiring authenticated alpha/beta floors (`docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md:254-265`). It does not excuse the second miss: execution B1 already specified the exact cell/value join (`docs/process_traces/2026-09-04-gamma-renderer/02-refuter-execution.md:7-11`), and fix round 1 promised it would hold “before rendering any claim result” (`docs/process_traces/2026-09-04-gamma-renderer/03-sol-fix-round-1-report.md:24-38`). The recurrent cause is therefore both a compacted ruling that failed to make the authorization input explicit and an implementation shape that allowed a local exception after the requirement was known.

Replacement clause, proposed verbatim:

> **R2-FL-1 — FLOOR-LINEAGE AUTHORIZATION (REPLACEMENT).** Before any gamma token, row, repeated placement, gate outcome, or verdict is rendered, the renderer MUST decode `claim_verdicts.inputs.floor_artifact.embedded_bytes_base64` and authenticate the exact `joulewise.detection_floor_artifact.v2` bytes with `authenticate_floor_artifact_bytes(raw, expected_sha256=file_sha256, expected_artifact_id=artifact_id)`. For each decode and selected-prefill `exact` arm resolution, `source_cell_ids` MUST name exactly one distinct cell in those authenticated bytes; that cell MUST be claim-ready and claim-usable with no reason codes, and the resolution's `floor_abs_j`, `floor_cmp_j`, and `floor_gate_j` MUST equal the authenticated cell fields exactly; the only authorized F is the maximum of the two authenticated `floor_gate_j` values. A validated refused resolution authorizes only its refusal state and registered reasons and never a numeric floor. Any byte, schema, artifact-ID, eligibility, cell-ID, component, or gate mismatch is terminal for the affected contrast and leaves every output for that contrast `STOP_FILL`, including `not_estimable`, `not_resolvable`, and `unresolved`; neither a claim-side copy nor a self-consistently re-content-addressed `claim_verdicts.v1` object can authorize a floor.

#### Q3 — Class-ending cure and its one test

Put the source-cell join in the canonical pre-render authorization path, not in an emitter. The smallest durable implementation is to extend `validate_claim_verdicts` where it already holds `authenticated_floor.value` (`joulewise/analysis_engine/artifact.py:1042-1055`): index the cells once, validate every v3 exact resolution against them, and return a named validation error on any mismatch. `render_gamma_contract` already makes that validator a global prerequisite at `joulewise/results_fill_gamma.py:684-689`, before either `_render_contrast` call at `:738-753`; after the change, remove the `lineage_valid` rendering branch and let renderers receive only a normalized/immutable authorized contrast projection (F derived from authenticated cells), never raw floor mappings plus a boolean. Thus numeric tokens, gate phrases, partial outcomes, and verdicts all cross the same seam, and no renderer branch can waive it.

The ONE regression should be `test_gamma_floor_lineage_authorization_rejects_sibling_outcome_mutation`. Starting from the valid not-estimable gamma fixture, mutate only the selected-prefill claim-side resolution/component/gate copies from the authentic floor to a different finite F, repair its claim-side aggregates/evaluation/content ID so it remains internally self-consistent, and leave `embedded_bytes_base64`, `file_sha256`, and `artifact_id` unchanged. The current head demonstrates RED because canonical validation remains `[]` and PG-08 renders a verdict; GREEN requires a named floor-lineage validation error and the public renderer to leave every selected-prefill token/row/placement `STOP_FILL`. This single composed counterfactual is discriminating: digest-only tests cannot catch it, and placing it against the canonical seam makes the sibling outcome site irrelevant.

#### Q4 — Ruling row (four sentences)

**R2-FL-1 — ADOPT:** adopt the replacement clause above as a clarification of R2's already-adopted external-floor cross-check, not as a new artifact schema. Direct the fix to the canonical `validate_claim_verdicts` authorization boundary and prohibit renderer-local authorization exceptions. Acceptance is the single re-content-addressed selected-prefill/not-estimable sibling mutation, which must make validation nonempty and every affected public output `STOP_FILL`. The R2 sidecar amendment otherwise remains unchanged.

## Residual risk

This was a structural, fixture-only inspection; no test was needed to establish a claim beyond the already-executed B1/F1 counterfactuals. The canonical validator change should be limited to the v3 armwise floor contract (the `_V3_FLOOR_KEYS` path) and checked against historical v1 readers so the cure does not retroactively impose v3 source-cell semantics on older artifact shapes.
