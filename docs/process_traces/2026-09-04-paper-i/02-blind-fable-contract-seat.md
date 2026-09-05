# PAPER-I blind Fable seat: three contract rulings (2026-09-04)

Blind seat at `9eef8584`. Auto-loaded: global/project `CLAUDE.md`, memory index; state docs unread. `$OUT` unset; written here. Inputs: scout 01, registry, D-117/123/165/166, analysis engine, extraction, floor, bundle reader, frozen renderer, pulse fiducial, kernel, draft-v1.

Principle: **suppliers issue strings, renderers copy bytes.** Numbers are issued as float plus producer-formatted string. A renderer may CROSS-CHECK a recomputation (STOP_FILL on disagreement) but never SUPPLIES a missing value.

## R1. `joulewise.reported_phase_energy.v1` (D-123 supplier)

One artifact per role, two cells each, read-only over the extraction artifact.

```
schema_version; campaign_role "alpha"|"beta"
source {extraction_artifact_sha256, whole_window_verdict_sha256, whole_window_status(=="passed"), frozen_semantics_sha256, plan_id}
cells[] cell_id(==extraction cell_id) phase metric(startswith "phase_energy_j.")
        member_basis "extraction_admitted_members" bundle_ids[sorted] excluded_slots n_planned
        n_admitted_bundles(==extraction n_admitted==len(bundle_ids))
        mean_j_per_request = mean of admitted members' metric_value_j; consistency{floor_mean_j_equal}
        interval{composition_rule "t95_repeat_half_width_plus_deterministic_terms", t_critical_95,
                 sample_stddev_j, repeat_half_width_j=t*s/sqrt(n),
                 deterministic_terms{anchor_shift_bound_max_j, whole_window_drift_allowance_j},
                 deterministic_total_j(sum; allowance once, D-102), lower_j, upper_j = mean -/+ (half_width+total)}
        per_token{status "issued"|"refused", refusal_reason, denominator_kind "observed_prompt_tokens"|"observed_output_tokens",
                  denominator_source ("workload_observed.token_count-output_token_count" | ".output_token_count"),
                  denominator_total(int), denominator_uniform, prompt_pin_sha256, value_j_per_token = sum(J)/sum(tokens)}
        rendered{mean_j,lower_j,upper_j: 2 decimals half-even; value_j_per_token: 4 decimals; n}
pre_registered bool; artifact_sha256 (canonical JSON, sorted keys)
```

Whole-artifact refusal: digest/status failure, member-basis or floor-mean inequality, n mismatch. Per-cell `per_token` refusal only (mean still issues): a prefill member lacking the four agreeing count surfaces (`bundle_read.py:1043`), a decode member with `output_token_count != 512` (D-166), or no pin. Per-token is point-only. Composition rule and denominator policy must be in the pack pre-registration, else `pre_registered=false` and Table 2 stays STOP_FILL (D-123 cl.1).

Binding: DS-09/13/17/21 -> `rendered.mean_j (lower_j, upper_j)`; DS-10/14/18/22 -> `rendered.value_j_per_token` or STOP_FILL; DS-12/16/20/24 -> `n_admitted_bundles`. Row rule: "MEASURED; cells[cell_id].rendered.<field>; STOP_FILL on refusal, `pre_registered=false`, or extraction sha differing from the floor artifact's source." `[PREFILL_LENGTH]` from the G2-a record.

Fixture `tests/fixtures/reported_phase_energy/`: synthetic extraction, 2 cells x 50 members with observed counts, passed verdict, existing floor fixture. Test: 20 values byte-exact vs golden; extraction/floor digests unchanged; one member count removed -> per_token refused, mean unchanged; one extraction byte changed -> whole refusal. Waits: all values; prefill cell_id. Conflict: scout wanted whole-artifact refusal on denominator ambiguity; per-cell ruled (DS-09/DS-10 are separate rows). Inference risk: a renderer averaging members or reading `floor.mean_j`.

## R2. Gamma claim renderer and VERDICT tokens

**Claim-side bound B = decision-interval half-width = t_critical_95*SE_total + deterministic_bounds.total** (`estimators.py:485-495`): the smallest |estimate| whose interval excludes zero. Not the deterministic total alone; never a gate (draft-v1:196, 200 hold). Producer issues `claim_evaluation.claim_side_bound{value_j, definition:"decision_interval_half_width", terms{t_critical_95,SE_total,deterministic_total}}`; if the engine change misses the mint, a sidecar `joulewise.claim_side_bound.v1` bound to the verdict sha issues it as post-registration disclosure. Renderer cross-checks value == (upper-lower)/2 within 1e-9 J. Lifting `[B_decode_claim_J]` SUPPLIER_UNKNOWN needs a dated registry addendum.

Tokens: every registered `*_decode_*` token gains a twin with stem `prefill_p[PREFILL_LENGTH]` in place of `decode` (PG-01..05); NEW `V_<stem>_floor_gate`, `V_<stem>_direction_gate`, `V_<stem>_verdict` for both stems (DS-30/31/32, PG-06/07/08). L = `collection_prefill_tokens` from the authenticated `joulewise.g2a_prefill_selection.v1`; the renderer composes `ctr-d117-prefill-p<L>-qwen3-1p7b-vs-qwen3-8b` and requires that exact id. Max of both arms' extraction `operative_floor_j` must equal `floor.active_floor_j`, else STOP_FILL.

Renderings (one string per token, copied verbatim everywhere; 2-decimal J, signed estimate keeps its sign; comparisons on exact floats; if rounding equalizes printed operands, add decimals to 6, then STOP_FILL):
- floor gate: `cleared: |Δ| = m J exceeds the cell floor F = f J` iff |est|>F, `effect_not_above_floor` absent, outcome not in {not_estimable, not_resolvable}; `not cleared: |Δ| = m J does not exceed the cell floor F = f J` iff |est|<=F and the code present; any other combination STOP_FILL.
- direction gate: `cleared: the interval [l, u] lies on the registered <positive|negative> side of zero` iff outcome==direction_supported and direction==hypothesized_direction; else `not cleared: <phrase>` by reason: zero inside -> `the interval [l, u] includes zero`; `deterministic_bound_obscures_direction` -> `the deterministic bound obscures the sign`; `multiplicity_not_rejected` -> `the Holm test did not reject`; opposite -> `the observed direction is opposite to the registered one`.
- verdict: direction_supported & claim_ready -> `supported: the larger model uses more energy per request (B − A > 0)` (negative symmetric); direction_supported & !claim_ready -> `direction observed, claim withheld (ceiling L1: <codes>)`; unresolved/not_resolvable/not_estimable -> `unresolved`/`not resolvable`/`not estimable`; equivalent -> STOP_FILL.
- REFUSAL retained cells, byte-exact as paper-G registered: `not evaluated — required token-generation verdict absent` / `… prompt-processing …` when the OR-01 governing reason is that absence; `not evaluated — stopped before comparison: <issued reason>` for an earlier stop. Stage and reason come from the OR-01 evidence, never from ratios.

Fixture `tests/fixtures/results_fill_gamma/`: two contrasts (decode, prefill-p2048), four floor cells, G2-a record L=2048, OR-01 stub; cases: supported, floor-refused, direction-refused, bound absent or != half-width, verdict absent, malformed id, code/number disagreement. Test: table-driven byte-exact strings per token per case; STOP_FILL for each refusal case; no `[PENDING]`, `[FILL:*]`, `[VALUE]`, `[PREFILL_LENGTH]` survives. Waits: all values; L. Inference risks: computing B from the interval; gates from numbers without codes or codes without numbers; verdict from D-165 dominance; rounding; parsing L from an id.

## R3. `joulewise.transfer_fiducial_capture.v1` and TR-01

```
schema_version; diagnostic true; claim_bearing false (both literal)
protocol{commanded_gap_s, run_count_registered, run_count_observed, estimator_id(==pulse protocol id in force),
         estimator_revision_sha256, pre_registration_sha256}
session_bound{b_fiducial_s(ledger lexeme), receipt_id, receipt_sha256}
runs[]{run_id, bundle_sha256, gap_start_edge{residual_lower_s,residual_upper_s,status}, gap_end_edge{...},
       fit_status, reasons[](registered diagnostic reasons only)}
largest_edge_residual_s = max over runs and edges of max(|lower|,|upper|)  (B_fiducial's rule)
comparison{residual_s, bound_s, excess_s=residual-bound, supported: residual_s<=bound_s}
verdict "supported"|"not_supported"|"inconclusive"; reasons[]
rendered{residual_ms,bound_ms,excess_ms: 1 decimal}; artifact_sha256
```

`inconclusive` iff any run unfitted or run counts differ; else from `comparison.supported`. Renderer cross-checks verdict vs comparison and max vs runs. TR-01 sentence (identical in all nine slots):
- supported: `In the post-campaign inserted-gap check, the largest fitted edge residual was R ms against the session's pulse-derived bound of B ms, so that bound is supported for inference-shaped load; this diagnostic result bears no claim.`
- not_supported: `… was R ms, exceeding the session's pulse-derived bound of B ms by X ms, so that bound is not supported for inference-shaped load; issued floors and verdicts stand under their stated transfer assumption; this diagnostic result bears no claim.`
- inconclusive: `In the post-campaign inserted-gap check the gap edges could not be fitted (<registered reason>), so the transfer check is inconclusive; this diagnostic result bears no claim.`
Row rule: "MEASURED; verdict + rendered.{residual_ms,bound_ms,excess_ms}; STOP_FILL if diagnostic!=true, claim_bearing!=false, estimator_id not in force, bound != ledger lexeme, verdict disagrees with comparison, or sha mismatch; branch selection never removes this placement."

Fixture `tests/fixtures/results_fill_transfer/`: protocol-arithmetic example (0.022 s <= 0.030067931757111657 s, non-measurement), not_supported (0.041 s), inconclusive. Test: three fixtures -> nine identical copies; mutations (claim_bearing true, diagnostic false, verdict `exceeds_bound`, verdict/comparison disagreement, estimator id, bound, digest) -> STOP_FILL. Waits: the capture (after final G3); TR-01 is on the fill critical path. Conflicts: sibling `exceeds_bound` vs registry "not-supported" (registry wins); `b_pulse_s` vs ledger `b_fiducial_s` (ledger wins). Inference risks: recomputing the max or `supported`; a bound sourced outside `session_bound`; a "not yet collected" sentence is unregistered and needs a ruling.
