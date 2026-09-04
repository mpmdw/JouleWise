```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R1 adopts the already frozen D-123 member universes and adds a cell-refusing reported-energy artifact; R2 exposes the named clock-anchor contrast term, not deterministic_bounds.total, through a versioned claim field and closes the decode/prefill rendering vocabulary; R3 places a small authenticated result projection in front of the unreviewed transfer capture and renders its composed edge-residual bound conservatively.",
  "workspace": {
    "base_requested": "9cab7f6e",
    "base_mode": "exact",
    "head_start": "9cab7f6eee5c13d50846b1af04c197ad39fb0789",
    "head_end": "9cab7f6eee5c13d50846b1af04c197ad39fb0789",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-paper-i/02-blind-fable-contract-seat.md",
    "docs/process_traces/2026-09-04-paper-i/03-consult-opus-contracts.md"
  ],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 3,
      "nit": 0
    },
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "Consume the generator's exact D-123 member universes and refuse per cell; do not choose a new admission basis"
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "title": "Name the clock-anchor contrast term as the claim-side disclosure and add a symmetric, conservative gamma token family"
      },
      {
        "id": "R3",
        "severity": "should_fix",
        "title": "Publish a content-addressed transfer result whose public quantity is explicitly a composed edge-residual bound"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "9cab7f6eee5c13d50846b1af04c197ad39fb0789"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\).*9cab7f6eee5c13d50846b1af04c197ad39fb0789$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "Read the scout, registry, D-117/D-123/D-165/D-166, both v5 floor generators, floor extraction, claim artifact/evaluator, and the unreviewed transfer producer",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Contracts compared at detached head 9cab7f6e; no measurement or mutation outside WRITE_SCOPE."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Contracts compared at detached head 9cab7f6e"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --no-index --check /dev/null docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "These are proposed contracts. The lead must ratify them and amend the registry before the three implementation seats treat them as authority.",
      "needs": "Adopt or amend R1-R3, then issue each seat with its narrow implementation write scope."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests were run under the prompt's preflight rule; this seat changed documentation only.",
      "needs": "Each future supplier seat owns the single acceptance test specified below."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No G2-a, v5 campaign, transfer-fiducial, or other quiet-machine measurement was started; therefore no value, selected prefill length, or scientific outcome is issued here.",
      "needs": "The lead-controlled physical sequence remains the sole issuer of live values."
    }
  ]
}
```

## Findings

### R1 — D-123 reported phase energy

**Ruling.** Use one content-addressed `joulewise.reported_phase_energy.v1` artifact per alpha or beta pack. The member basis is not open: for each result cell, consume the exact ordered `reported_energy_cells[].members` list already emitted by that pack's v5 generator. `missing_or_invalid_member: refuse_reported_mean` acts at the owning cell, not as a license to shrink the list and not as a reason to suppress an independently valid sibling cell. An issued cell therefore has all 50 registered independent bundles and `admitted_independent_bundle_count = 50`; a refused cell may preserve its audit count but none of its four numeric/count tokens renders. The p42 companion registration remains in the artifact for custody but has no DS-09..DS-24 paper binding. The selected prefill cell is selected only by authenticated G2-a and prompt-pin identities, never by accepting the generator's current concrete suffix at face value.

The closed schema is:

```text
schema_version: "joulewise.reported_phase_energy.v1"
artifact_id: "rpe-" + 64 lowercase hex
producer: {
  implementation: "joulewise.reported_phase_energy",
  source_commit: 40 lowercase hex,
  source_sha256: 64 lowercase hex
}
inputs: {
  extraction_spec: {
    schema_version: "joulewise.detection_floor_extraction_spec.v1",
    path: nonempty pack-relative POSIX string,
    file_sha256: 64 lowercase hex,
    floor_projection_sha256: 64 lowercase hex
  },
  extraction_report: {
    schema_version: nonempty string,
    file_sha256: 64 lowercase hex,
    consumption_semantics_id: nonempty string
  },
  g2a_selection: null | {
    schema_version: "joulewise.g2a_prefill_selection.v1",
    file_sha256: 64 lowercase hex,
    collection_prefill_tokens: one of 512, 1024, 2048, 4096
  },
  prompt_pin: null | {
    schema_version: "joulewise.prefill_prompt_pin.v2",
    file_sha256: 64 lowercase hex,
    prefill_length: one of 512, 1024, 2048, 4096,
    g2a_record_sha256: 64 lowercase hex
  }
}
cells: [{
  cell_id: registered nonempty string,
  metric: "phase_energy_j.prefill" | "phase_energy_j.decode",
  status: "issued" | "refused",
  registered_member_count: integer = 50,
  admitted_independent_bundle_count: integer 0..50,
  member_admission_rule: "fixed_registered_universe_all_or_refuse.v1",
  mean_j_per_request: finite number >= 0 | null,
  interval_j_per_request: null | {
    lower_j: finite number >= 0,
    upper_j: finite number >= lower_j,
    composition_rule: "arithmetic_mean_of_member_anchor_envelope_endpoints.v1"
  },
  per_token: null | {
    value_j_per_token: finite number >= 0,
    numerator_energy_j: finite number >= 0,
    observed_token_count: positive integer,
    denominator_kind: "runtime_observed_prompt_tokens" | "runtime_observed_output_tokens",
    aggregation_rule: "ratio_of_sums_over_same_fixed_members.v1",
    token_count_source: "runtime_observed"
  },
  members: [{
    ordinal: integer 1..50,
    bundle_id: registered nonempty string,
    config_sha256: 64 lowercase hex,
    bundle_sha256: 64 lowercase hex,
    summary_sha256: 64 lowercase hex,
    metadata_sha256: 64 lowercase hex,
    whole_window_evaluation_basis_sha256: 64 lowercase hex,
    admitted: boolean,
    reasons: [closed reason-code strings],
    energy_j: finite number >= 0 | null,
    energy_interval_j: null | {lower_j: finite number >= 0, upper_j: finite number >= lower_j},
    observed_token_denominator: null | {
      kind: same closed denominator kind as parent,
      count: positive integer,
      token_count_source: "runtime_observed",
      observed_total_token_count: nonnegative integer,
      observed_output_token_count: nonnegative integer,
      prompt_realized_token_count: positive integer
    }
  }],
  refusal_reasons: [closed reason-code strings]
}]
```

`artifact_id` is `rpe-` plus SHA-256 of canonical JSON with `artifact_id` set to the empty string. Exact keys, finite-number checks, ordered unique cell/member identities, source digests, and all parent identities are mandatory. For prefill, each member denominator is `observed_total_token_count - observed_output_token_count`, must be positive, must equal `prompt_realized_token_count`, and the selected cell must equal both G2-a and prompt-pin lengths. For decode it is `observed_output_token_count` and must be positive. In both cases the summary must state `measurement_quality.token_counts_source = runtime_observed`. The point is the arithmetic mean of the 50 authenticated `point_j` values. The full descriptive measurement interval is the arithmetic mean of their `energy_anchor_shift_envelopes[/phase_energy_j/<phase>].lower_j` through the arithmetic mean of their `.upper_j`; it is not a population confidence interval. Per-token energy is `sum(point_j) / sum(observed denominator)` over those same 50 members—never the mean of per-member ratios. Every source point must equal its envelope's `point_j` and lie within its endpoints.

**Registry bindings.** For model prefix `1p7B` or `8B` and phase suffix `prefill_p[PREFILL_LENGTH]` or `decode`, bind `E_*_J_per_request -> cells[].mean_j_per_request`, `E_*_lower_J -> cells[].interval_j_per_request.lower_j`, `E_*_upper_J -> ...upper_j`, `E_*_J_per_token -> cells[].per_token.value_j_per_token`, and `N_bundles_* -> cells[].admitted_independent_bundle_count`; select by exact registered `cell_id`, not array position. Thus DS-09/13/17/21 consume point plus endpoints, DS-10/14/18/22 consume the per-token value only after denominator authentication, and DS-12/16/20/24 consume the issued count. Render energy to the paper's numeric style only after validating unrounded relations; absent/refused is `STOP_FILL`, never zero.

**Fixture and one acceptance test.** Build one synthetic two-pack fixture with four paper-bearing 50-member cells plus the two p42 custody cells; vary member energies and runtime-observed prompt/output denominators, include exact envelope endpoints, and retain a byte copy of the preexisting floor-output fixture. The one test is `test_d123_reported_phase_energy_contract_table`: table-drive alpha/beta × prefill/decode, assert all 20 exact tokens and relation checks, assert the floor artifact is byte-identical before/after, then mutate in turn a member ID, digest, endpoint, denominator source, prompt-count cross-check, and G2-a/prompt-pin join and require only the owning cell to refuse with no token emitted.

**Do not decide now.** Do not choose a numeric mean, endpoint, token denominator, selected prefill length, or alternate/partial member population; do not turn the descriptive envelope into an inferential CI; do not change floor bytes or floor admission semantics. **Existing-contract conflict:** the registry/scout statement that the member basis is undefined is stale against both v5 generators, which already freeze three 50-member `reported_energy_cells`. The output schema and interval/denominator reduction remain genuinely missing. The scout's proposed whole-artifact refusal is unnecessarily broader than the existing per-cell `missing_or_invalid_member` contract and should not be adopted.

### R2 — gamma claim rendering

**Ruling.** Do not alias the Table 3 claim-side bound to `deterministic_bounds.total`. Instead issue `joulewise.claim_verdicts.v2`, retaining v1 fields and adding this exact closed object to every contrast:

```text
claim_side_bound: {
  role: "claim_measurement_uncertainty_bound",
  source_term_name: "E_clock_anchor_shift_bound_j",
  value_j: finite number >= 0,
  composition_rule: "exact_named_contrast_deterministic_term.v1",
  single_count_discipline_rule_id: "attribution_floor_plus_claim_side_bound.v1"
}
```

The validator requires exactly one `deterministic_bounds.terms[]` member named `E_clock_anchor_shift_bound_j`, bit-for-bit numeric equality between its `bound` and `claim_side_bound.value_j`, the existing authenticated v2 input chain and content ID, and no equality requirement to `deterministic_bounds.total`. This promotes the separately registered claim-measurement role to a named output while preserving that the full total—anchor plus interpolation and any other registered deterministic terms—alone expands the decision interval. Changing strict v1 in place is forbidden.

For decode, retain the registered estimate/endpoints/magnitude/floor/bound/clearance/shortfall/ratio/sum tokens and add `[C_decode_sizing_signed_clearance_J]`, `[OUTCOME_decode_floor_gate]`, `[OUTCOME_decode_direction_gate]`, and `[VERDICT_decode]`. For the selected prefill arm add the exact symmetric family:

```text
[E_prefill_p[PREFILL_LENGTH]_contrast_signed_J_per_request]
[E_prefill_p[PREFILL_LENGTH]_contrast_lower_J]
[E_prefill_p[PREFILL_LENGTH]_contrast_upper_J]
[M_prefill_p[PREFILL_LENGTH]_contrast_abs_J_per_request]
[F_claim_prefill_p[PREFILL_LENGTH]_armwise_max_J]
[B_prefill_p[PREFILL_LENGTH]_claim_J]
[C_prefill_p[PREFILL_LENGTH]_floor_clearance_J]
[S_prefill_p[PREFILL_LENGTH]_floor_shortfall_J]
[R_prefill_p[PREFILL_LENGTH]_effect_x_floor]
[S_prefill_p[PREFILL_LENGTH]_joint_J]
[C_prefill_p[PREFILL_LENGTH]_sizing_signed_clearance_J]
[OUTCOME_prefill_p[PREFILL_LENGTH]_floor_gate]
[OUTCOME_prefill_p[PREFILL_LENGTH]_direction_gate]
[VERDICT_prefill_p[PREFILL_LENGTH]]
```

Bindings are exact: estimate is `estimator.estimate` with B-minus-A orientation; lower/upper are `deterministic_bounds.decision_interval.{lower,upper}`; magnitude is `abs(estimate)`; claim floor is the externally cross-checked maximum of the two exact arm `floor_gate_j` values; `B` is `claim_side_bound.value_j`; floor clearance/shortfall compare magnitude with `F`; `S_joint = F+B`; sizing signed clearance is `magnitude-S_joint`. DS-29 binds decode `B`; DS-30/31/32 bind the three decode outcome tokens; DS-33 binds the prefill `F`; PG-01 binds the signed prefill estimate, PG-02 both endpoints, PG-04 must print `S_joint` and sizing signed clearance, PG-05 `B`, and PG-06/07/08 the three prefill outcome tokens. Unrounded values decide all relations; formatting occurs last.

The exact outcome renderings for these registered positive contrasts are:

- floor pass: `passes — |estimate| > armwise cell floor`; floor fail: `does not pass — |estimate| ≤ armwise cell floor`; unavailable: `not evaluated — <issued reason>`;
- direction pass: `passes — the fully composed interval lies wholly above zero`; direction fail: `does not pass — the fully composed interval does not lie wholly above zero`; unavailable: `not evaluated — <issued reason>`;
- verdict when and only when outcome is `direction_supported`, direction is `positive`, `claim_ready_for_l2_l3` is true, ceiling is at least L2, both renderer gates pass, and Holm says rejected: `supported — Qwen3-8B used more <phase> energy per request than Qwen3-1.7B under the registered comparison`;
- `not_estimable`: `not supported — not estimable (issued reasons: <semicolon-joined reason_codes>)`; `not_resolvable`: `not supported — not resolvable (issued reasons: <semicolon-joined reason_codes>)`; `unresolved`: `not supported — unresolved under the registered gates` plus ` (issued reasons: ...)` when nonempty; an otherwise `direction_supported` but non-ready result: `not supported at the paper's claim level (issued reasons: <semicolon-joined reason_codes>)`. `equivalent` is structurally invalid for these directional, equivalence-null contrasts and is `STOP_FILL`.

The reason list preserves authenticated artifact order and prints raw registered codes rather than inventing causal prose. Under D-166, an issued reducer refusal with overlap count below 3 renders through `not_resolvable_sample_count`; a resolvable count of 3–4 must instead render `not supported — below the pre-registered count floor of 5 (reducer result remained resolvable at observed overlap count <n>)`. The renderer may use that sentence only from authenticated count/status fields; it never infers the branch from a missing claim verdict. Paper-G refusal behavior remains byte-exact: if the verdict exists, use the same `[VERDICT_*]`; if it is the issued missing item use `not evaluated — required token-generation verdict absent` or `not evaluated — required prompt-processing verdict absent`; if evaluation never began use `not evaluated — stopped before comparison: <issued reason>`.

**Fixture and one acceptance test.** Use one synthetic content-addressed claim-verdict-v2 family with decode and symbolic prefill contrasts, authenticated alpha/beta floors, G2-a selection and prompt pin set to fixture-only 2048, and variants for supported, floor fail, zero-crossing direction fail, D-166 counts 2 and 4, absent verdict, bad bound term, and wrong/duplicate contrast ID. The one test is `test_gamma_result_contract_table`: assert byte-exact DS-29..DS-33 and PG-01..PG-08 outputs and all repeated DS-32/PG-08 placements for every variant; assert every arithmetic/cross-artifact relation; require `STOP_FILL` for absent, unauthenticated, inconsistent, duplicate, equivalence, or unresolved-G2-a inputs, with no pending metatoken surviving.

**Do not decide now.** Do not choose `[PREFILL_LENGTH]`, any estimate/bound/floor/endpoint, any outcome, a Holm result, reason codes, D-165 branch, or a paper claim. D-165 ratios remain independent close-out evidence and never select a gamma verdict. **Existing-contract conflicts:** equating `B` with `deterministic_bounds.total` contradicts the registry, draft, and artifact guide; equating it directly with an unnamed term still fails the current named-field guard, hence v2. The adapter contract does already settle its source as `E_clock_anchor_shift_bound_j`. Also, DS-28's current binding to floor-only clearance conflicts with its `F+B; signed clearance` column; it must use the new joint sum and sizing-clearance token pair, and PG-04 must use the same rule.

### R3 — TRANSFER-FIDUCIAL-01 result rendering

**Ruling.** Do not make the paper renderer depend on the unreviewed capture's entire verbose shape. Ratify a closed, content-addressed public projection `joulewise.transfer_fiducial_result.v1`, mechanically derived from and hash-bound to the capture:

```text
schema_version: "joulewise.transfer_fiducial_result.v1"
result_id: "tfr-" + 64 lowercase hex
diagnostic_protocol_id: "TRANSFER-FIDUCIAL-01"
diagnostic: true
claim_bearing: false
source_capture: {
  schema_version: "joulewise.transfer_fiducial_capture.v1",
  file_sha256: 64 lowercase hex,
  source_commit: 40 lowercase hex,
  fit_source_commit: 40 lowercase hex,
  plan_sha256: 64 lowercase hex,
  pre_data_receipt_sha256: 64 lowercase hex,
  estimator_revision: nonempty string,
  estimator_source_sha256: 64 lowercase hex,
  bundle_sha256: [{bundle_id: nonempty string, sha256: 64 lowercase hex}]
}
largest_inserted_gap_edge: null | {
  bundle_id: nonempty string,
  edge: "falling_gap_edge" | "rising_gap_edge",
  fitted_residual_interval_s: {lower: finite number, upper: finite number >= lower},
  effective_clock_anchor_bound_s: finite number >= 0,
  composed_absolute_residual_bound_s: finite number >= 0
}
pulse_derived_timing_bound_s: finite number >= 0 | null
support_outcome: "supported" | "not_supported" | "not_evaluated"
reason_codes: [closed ordered unique strings]
```

`result_id` uses the same empty-ID canonical-JSON hash rule as R1. For every accepted source run edge, recompute `composed_absolute_residual_bound_s = max(abs(lower), abs(upper)) + effective_clock_anchor_bound_s`; require exactly the registered run census and two named edges per run; select the maximum unrounded value with deterministic tie-break `(bundle order, falling before rising)`. `supported` is valid iff the reason list is empty and the maximum is `<=` the authenticated pulse bound; `not_supported` iff it is `>`; `not_evaluated` iff an authentication/schema/coverage refusal exists, in which case no comparison is inferred and nullable quantities reflect what was actually authenticated. All duplicated summary fields in the source capture must replay to this projection exactly.

The single `[TRANSFER_FIDUCIAL_RESULT]` token supplies every TR-01 placement. Convert seconds to fixed six-decimal seconds only after the unrounded comparison. Exact prose is:

- supported: `Diagnostic only: the largest composed inserted-gap edge-residual bound was <R> s, no greater than the session pulse-derived timing bound of <B> s; this supports applying that timing bound to the studied inference boundary, but it does not mint a floor or license a claim.`
- not supported: `Diagnostic only: the largest composed inserted-gap edge-residual bound was <R> s, exceeding the session pulse-derived timing bound of <B> s; this does not support applying that timing bound to the studied inference boundary and does not mint a floor or license a claim.`
- not evaluated: `Diagnostic only: the inserted-gap transfer comparison was not evaluated (issued reasons: <semicolon-joined reason_codes>); applying the session pulse-derived timing bound to the studied inference boundary remains unestablished.`

The renderer writes that one byte-identical sentence to all nine Abstract/Section 7/Section 10 A/B/Refusal placements; outcome-branch selection cannot remove it.

**Fixture and one acceptance test.** Build one fixture family from the candidate's non-measurement protocol arithmetic (`0.022 s <= 0.030067931757111657 s`), a `0.031 s` not-supported case, and an authenticated-refusal case, each with ten bundles/twenty exact edge records and source digests. The one test is `test_transfer_result_contract_table`: replay the projection and exact sentence for all three outcomes, assert nine byte-identical copies, then mutate capture/plan/receipt/estimator/bundle digests, edge census, maximum, outcome, diagnostic flags, and comparison equality and require `STOP_FILL` at all nine sites.

**Do not decide now.** Do not issue the actual residual, bound, support outcome, selected workload stratum, or transfer claim; do not generalize beyond the studied inference boundary; do not let this diagnostic mint a floor or alter gamma/D-165 outcomes. **Existing-contract conflict:** the sibling branch's `residual_transfer_s` is the maximum of per-edge radii after adding clock-anchor uncertainty, not a raw fitted residual, so both that name and TR-01's current “largest fitted ... residual” wording are materially ambiguous. Its `verdict = exceeds_bound|inconclusive` can be losslessly mapped to `support_outcome = not_supported|not_evaluated`, but the public projection must add the content ID, bundle digests, explicit largest-edge witness, and unambiguous composed-bound name before the renderer consumes it.

## Residual risk

This consult validates contract fit by source inspection only. It does not establish that every future reason code has an ideal reader-facing paraphrase; the proposed conservative renderer deliberately exposes authenticated codes until such a closed prose map is separately registered. The live G2-a selection, reported means, gamma verdicts, and transfer result remain measurement-owned and unissued.
