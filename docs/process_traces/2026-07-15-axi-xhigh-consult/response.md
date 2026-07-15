## Positions

1. S-A should introduce versioned burst semantics without changing existing metric identities.

- Preserve existing `token` events as singleton emissions. Add a new request-scoped emission event for burst-capable bundles; do not silently reinterpret one `token` event as N tokens.
- Record a bundle-level event-semantics version in `metadata.json`, distinct from the reserved config schema v0.2. All new spec-on, spec-off, and batch controls should use the new event version, including B=1 controls.
- Advance the reducer version and retain an exact compatibility arm for stored reducer-0.4.2 bundles. Otherwise bumping the current version would make existing current-era bundles require re-reduction, contrary to D-066.
- Do not change `energy_output_token_j` or `inter_token_throughput_tokens_s` in place. The former remains historically idle-subtracted; the latter remains valid only when every emission has a genuine per-token timestamp.

The counter contract should be:

| Field | Frozen meaning |
|---|---|
| `tokens_proposed` | Candidate token positions actually submitted to target verification; excludes unfilled slots and target correction/bonus tokens. |
| `tokens_accepted` | Proposed draft/MTP tokens committed unchanged to the output; excludes target-origin correction/bonus tokens. |
| `emitted_count` | All output tokens committed at that decode step: accepted candidates plus target-origin tokens. Must match captured output-token evidence. |
| `acceptance_rate` | `sum(tokens_accepted) / sum(tokens_proposed)`, never a mean of step/request rates. Null when proposals total zero. |

For spec-off, all three speculation counters should be null, not zero. For a speculation-enabled request that happens to propose zero tokens, proposed/accepted are zero and rate is null. Native MTP uses the same counter definitions.

Draft identity needs a discriminator:

- `speculation.mode`: `off`, `draft_model`, or `native_mtp`.
- `draft_model_identity`: required and fully stack-identified for `draft_model`; null otherwise.
- Native MTP identity is the target artifact hash plus the recorded MTP/head configuration. A null draft model alone cannot distinguish native MTP from spec-off.

Each decode-emission event should carry, inside the existing `metadata` object:

- `request_id`
- request-local event and decode-step ordinals
- `emitted_count`, `tokens_proposed`, `tokens_accepted`, and `target_emitted_count`
- optional emitted token IDs or a hash linked to the request output artifact
- optional `batch_group_id` and `scheduler_step_id`, which must not replace `request_id`

Validate `emitted_count = tokens_accepted + target_emitted_count` and rollup consistency against request output IDs, stop reason, and output-policy counts.

For metrics:

- The primary spec-on/off estimand is paired gross request energy, with gross J per committed output token as the token-normalized companion.
- Gross J per accepted draft token is a mechanism-yield diagnostic for speculation-enabled arms only. It is undefined for spec-off and must not be used as the on/off efficiency denominator.
- `inter_token_throughput_tokens_s` should be null whenever a burst lacks individual token timestamps. Add burst-safe metrics such as `decode_phase_output_throughput = committed_tokens / request_decode_duration`, emission-event rate, and burst-size distribution. If a first-to-last emission-span metric is added, give it a new name and freeze its censoring rule.
- Request energy must remain equally or more salient than token ratios under the token-normalization contract.

The current P2-042 implementation cannot simply be extended in place: `joulewise.analysis_manifest.v1` is AP-2-specific and hard-codes `energy_request_j` plus `runtime_observed_output_tokens`. Add a sibling/generic manifest version while leaving AP-2 v1 byte-identical. AP-SPEC must freeze:

- `gross_energy_j` as numerator
- committed-output and accepted-draft denominators separately
- aggregation form and zero/null rules
- exact pairing fields
- output-identity gate
- floor selector
- claim disposition on divergence

C-023-OUTPUT-IDENTITY should become a cross-bundle gate, not merely a single-bundle validator check. The bundle validator proves count/hash integrity; the analysis gate compares paired spec-on/off outputs while allowing only the frozen speculation fields to differ between configs. Recommended report states are `exact_token_match`, `text_match_token_divergent`, `output_divergent`, and `unassessable`. Only exact token identity supports the clean “effect of speculative decoding on matched decoded work” claim. A predeclared quality-equivalence design may support a differently worded quality-matched claim, but it does not erase token divergence.

2. The continuous-ready constraint is directionally right but incomplete unless reducers and output artifacts become request-aware too.

Critical requirements:

- Emit one event per request per scheduler tick. A single batch event containing a list of request IDs would recreate run-scoped semantics.
- Pair lifecycle and phase events by `(request_id, phase)`, not global FIFO. Equal timestamps are allowed; request-local ordinals establish order.
- A succeeded bundle requires a terminal lifecycle outcome for every admitted request. Failed bundles may retain incomplete requests, but must record failure/cancellation explicitly.
- Add a request-indexed output artifact analogous to suite items. One `response.txt` cannot support output identity, stop reasons, or counts for B requests.
- Record configured and realized batch sizes separately and never infer either from event count.
- Keep request identity separate from static batch-group identity and future dynamic scheduler-step identity.
- For synchronized static batches, duplicate request phase windows must be unioned for group phase energy. The current reducer sums same-named windows and would overcount synchronized B-request phases by approximately B.
- Do not divide overlapping power-trace energy among requests without an attribution model. Static AP-BATCH should use group gross energy; future continuous mode should use session gross energy per total committed token at offered load, while per-request events supply latency and lifecycle evidence.
- Request submission may precede prefill and requests may overlap arbitrarily. No validator may require a shared prefill or decode boundary.

The typed batch policy belongs in normalized config identity—mode, requested B, synchronization/admission policy—not only runtime metadata. This should be an additive scoped v0.1 extension or another AXI-specific version; it must not consume config schema v0.2, which D-008 reserves for split runs.

3. Recommended S-0 advisor wording:

> Unless a figure explicitly states otherwise, JouleWise uses gross measured energy within the named measurement boundary as the headline basis. Gross energy retains the idle, model-residency, and runtime overhead present during the measured interval, so comparisons across devices, configurations, and split versus monolithic execution use gross energy. Idle-subtracted energy is reported separately as a within-device secondary view of activity above the measured idle baseline; it is not used to rank devices or configurations. In Q4, the fixed term is estimated from the gross-energy workload sweep and is not set equal to measured idle energy.

Every table/figure should label both basis and boundary, for example `Gross energy — M3 Max / powermetrics SoC rails`. Avoid calling gross rail energy “full-system” or “wall” energy.

4. Stream-specific execution traps:

- S-A/S-E currently form a sequencing cycle: S-A forbids any spec bundle before denominator freeze and exits with a mock spec bundle, while AP-SPEC is assigned to later S-E. Move the minimal AP-SPEC/manifest/identity-gate freeze into the front of S-A; S-E can complete the statistical design later.
- S-B should use a structured verdict. `supported` requires true B>1 execution—not a Python loop over B singleton calls—plus per-request output IDs/counts, stop reasons, timestamps, and request-scoped event hooks. If mlx-lm batches but lacks observability, record `unsupported_for_joulewise(event_observability)` and do not mint the Mac registry leg. Memory-fit range is a separate field, not runtime-support semantics.
- S-C should distinguish runtime generation support from claim-instrumentable support. If proposal/acceptance counters are unavailable, record that limitation even if text generation works. Native MTP and external draft-model legs should not be pooled into one contrast family.
- S-D should pre-register selection before energy results: same family/tokenizer, identical runtime and quantization recipe, fixed output policy, active-parameter calculation including shared experts/router top-k, artifact revisions/hashes, quality-band rule, memory headroom, and fallback hierarchy. A total-parameter-matched fallback is a different estimand and must be labeled as such.
- MOE×BATCH cannot claim “expert-activation diversity” unless the runtime exposes auditable routing/expert-activation evidence. Without it, the allowed claim is only a batch-size interaction for one named dense/MoE pair.
- S-E AP-BATCH should use five counterbalanced blocks, each containing all B values, rather than five unstructured repetitions per B. Use a fixed, balanced roster of distinct equal-shape requests; duplicating one prompt B times suppresses routing diversity and may trigger reuse artifacts.
- Fit the all-B affine model as the primary test, with a predeclared lack-of-fit rule. A data-selected breakpoint should be secondary/exploratory or use a frozen candidate set with multiplicity-aware inference. The intercept is an estimated affine intercept, not directly measured idle or a uniquely identified residency cost.
- Record B=16 memory failure as a structured outcome. Do not silently drop it and refit B≤8 as though the original AP succeeded.
- C5-2.2 retains a latency-bound requirement. Static batching can report request TTFT/latency under synchronized admission, but it cannot support coalescing, scheduler-optimum, or offered-load claims from C5-2.6.

5. Standing-contract audit:

- The obvious idle-primary conflicts in `token_normalization.md`, the current `energy_request_j` ratio path, and C5-1.1’s idle-subtracted wording are already superseded by D-067. Align them without redefining stored fields.
- A hard confirmatory `n=5` conflicts with D-062 unless Window-A variance/MDE evidence supports it. Treat n=5 as provisional. If Ed fixes the budget at 25 runs, freeze n=5 and accept `not resolvable`/L1 outcomes; never top up after observing effects.
- AP-BATCH’s batch-group window has no clearly matching P2-015 floor cell. Freeze a conservative transport rule from an equal-or-harder gross-request floor, or add an independent batch-group calibration cell before claim-bearing execution.
- D-016 still requires the selected benchmark models to run across primary targets and fit 8 GB targets. A matched-active-parameter MoE may fail that hard gate because total weights determine fit. If so, the AXI Mac dense/MoE pair must be a separate selection, or D-016 needs an explicit amendment.
- “AP-5 rides inside 2M at zero extra cost” is true only if that exact pair is already part of the cross-target 2M matrix. Otherwise it changes the baseline model set or adds quiet-Mac work.
- The all-five-axes commitment is missing complete AP ownership for quantization, reasoning-length variance, and MOE×BATCH. D-053 forbids L2 execution without those frozen rows. S-E should add AP-QUANT, AP-REASON/VARIANCE, and AP-MOE-BATCH or create explicit follow-on owners before AXI closes.
- No additional outcome-level contradiction with D-066–D-070 was found.

## Disagreements

- I disagree with treating “joules per accepted token” as the headline spec-on/off efficiency measure. Spec-off has no accepted-draft denominator. Use matched gross request energy and gross J per committed output token for the comparison; retain J per accepted draft token as a spec-only mechanism diagnostic.
- I disagree with mutating AP-2 manifest v1 or the existing inter-token field. Both have frozen identities; sibling versioned semantics are cheaper and safer.
- I disagree with a binary S-B verdict that calls batch execution “supported” when per-sequence evidence is unavailable. That is runtime capability but JouleWise instrumentation failure.
- I disagree with silently substituting total-parameter matching for active-parameter matching. It changes the scientific question.
- I disagree with promising a confirmatory breakpoint and fixed n=5 before floors. Both would violate the existing prospective-selection discipline.

## Open questions

- Will Ed permit a separate Mac-only AXI dense/MoE pair if no pair satisfies D-016’s all-target/8-GB gates? Recommendation: preserve D-016 and create the separate AXI selection.
- Is exact token identity the primary C-023 equivalence gate, with quality-equivalent divergent outputs as a secondary AP? Recommendation: yes.
- Is n=5 an immutable resource cap or a provisional design value? Recommendation: provisional until P2-015; if immutable, accept unresolved outcomes without top-up.
- Can a Window-A gross-request floor conservatively dominate every AP-BATCH group window? Recommendation: require an explicit duration/cadence/drift transport check; otherwise add a batch-specific calibration cell.
- Does the selected MoE runtime expose expert-routing evidence? If not, rename MOE×BATCH around the observable interaction rather than the unobserved mechanism.

## Recommendation

Execute after audit/adoption clearance in this order:

1. Land S-0 using the paragraph above and basis+boundary labels everywhere.
2. Begin S-A with one contract freeze covering event semantics, counter invariants, draft/MTP identity, request lifecycle, legacy dispatch, the AP-SPEC denominator object, and the C-023 report schema.
3. Implement the new manifest/registry version before the mock adapter. Then land reader/reducer/validator changes, followed by the mock spec bundle.
4. Run S-B’s verdict spike. Mint the Mac-batching row only on full JouleWise support.
5. Build S-D’s pre-data model scorecard and present the D-016/separate-pair choice to Ed.
6. Complete S-E with AP-BATCH, AP-SPEC, AP-QUANT, AP-REASON/VARIANCE, AP-5/MoE, and AP-MOE-BATCH. Freeze final n, floor mappings, multiplicity families, breakpoint disposition, and exact forbidden upgrades after P2-015.
7. Run S-C only against the landed S-A contract; retain the vLLM leg as PROVISIONAL until live NVIDIA contact.
8. Keep every AXI measurement behind Window A and the quiet-Mac gate.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Completed the read-only AXI design challenge; recommended versioned burst/request semantics, gross matched-output spec estimands, executable output-identity gating, continuous-safe lifecycle rules, revised sequencing, and resolution of D-016/D-062/AP ownership traps.","pathspec":[],"verification":["git rev-parse HEAD: cae50e59cd8843eb48f9aedf7aaedd8ebb2d50ff","git status --short --branch: clean main tracking origin/main","Reviewed docs/axi-handoff.md, D-066..D-070, token normalization, analysis plans/manifest, research bank/registry, bundle event/reducer/schema surfaces, claims/floor contracts, and D-016/D-062"],"flags":["no_edits","read_only_discussion"]}