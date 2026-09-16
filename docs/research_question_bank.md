# Research Question Bank

Candidate research questions the instrument can answer, beyond the named
set in `PROJECT_STATUS.md`. Populated from council sessions C-003/C-004
(2026-07-07; see `docs/council_log.md` for positions and votes). Promotion
out of the bank requires: a named RQ slot in `PROJECT_STATUS.md`, a data
plan that does not displace queue ranks above it, and (post P1-001) scope
fit. Killed ideas stay recorded with their cause of death.

Canonical live index: `docs/research_question_registry.md`. The registry is
the current index for aliases, status, claim ceilings, owners, and gates; this
bank remains the historical and deliberative record.

## Current capstone boundary — 2026-09-04

This bank is broader than the capstone. Its older “today,” “after Window A,”
and tier labels remain deliberation history, not the current paper promise.
The controlling row-by-row map is
`docs/research_question_coverage-2026-09-04.md`, derived from the fresh paper
and research-question audit together with D-164 through D-171.

Evidence already on disk answers only diagnostic, descriptive, or mechanism
subquestions. None of it is eligible for a production claim. The retained
set covers `RQ-SHORT-PREFILL-RESOLVABILITY`, the mechanism portion of
`RQ-METHOD-FLOOR`, the limited evidence-preservation capability
`RQ-AUDITABLE-EVIDENCE`, partial observed cases for `C5-1.5`, `C5-1.10`, and
`C5-1.11`, and the four narrow feasibility or smoke rows
`RQ-QWEN25-SMOKE`, `RQ-QWEN35-SMOKE`,
`RQ-TWO-MODEL-ACTIVE-NONCLAIM`, and `RQ-MLX-KV-REPLAY`.

The next governed collection chain can answer only two registered capstone
rows: `RQ-ATTRIBUTION-DOMINANCE`, the primary question, and `C5-1.1` at its
fixed Qwen3 8B-versus-1.7B pairwise ceiling. That chain is not one literal
window: G2-a, a desk day, and G2-b precede the claim-bearing `_v5` alpha and
beta floor windows and gamma contrast, and D-168 close-out follows them.
The post-campaign transfer fiducial tests a limitation diagnostically but is
not itself a registry row and cannot support a claim.

Every other bank or registry identifier is cut from the capstone while
remaining available for later work at its existing status and claim ceiling.
In particular, the `_v6` scored leg, the unresolved D-163 model ladder, and
all previously unrouted questions remain outside this paper. D-169 and D-171
change how eligible windows may be operated without the researcher at the
keyboard; they do not turn planned work into collected data. D-170 requires
executed evidence or a code-path proof for artifact-production premises; it
does not upgrade any research answer.

## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)

- **Q4 Fixed-vs-marginal energy model** — fit
  `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` per
  target/model/quantization; predicts which workloads flatter which
  devices and enables compositional split-energy prediction (predict
  split-run energy from monolithic coefficients + transfer measurements,
  validate on a subset) — the method that makes Q1 answerable at scale.
  Subsumes the prefill-scaling-exponent question. L3 wording requires AP-1
  in `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q5 Ranking stability** — do within-machine rankings survive workload
  changes (prompt/output/quantization regimes), or where do they flip?
  Cross-device extension is hardware-gated. Uses the 2M matrix directly
  as a substrate; rank wording follows AP-3 in
  `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q6 Boundary sensitivity** — do conclusions change when measured at
  platform rails vs AC wall power? (Gated on the wall meter, P1-003/R-007;
  reframes calibration as a research result.)

## Methodology centerpiece (deliberately NOT a numbered RQ — C-003 vote)

- **Detection floor / noise floor**: the smallest idle-subtracted energy
  difference each target/telemetry backend can honestly resolve. Observed
  motivation: idle baseline stddev (5.4 W) exceeded its mean (3.5 W) in
  the first real capture. Pairs with the reducer feature all council
  members converged on: **phase/item identifiability flags** (windows with
  fewer than N samples report a flag, not a bare joule value).

## Banked (viable, not yet promoted)

- **Dark silicon / rail utilization**: what fraction of a SoC's rails does
  a runtime energize? (Measured: ANE at 0.0 W through 512 tokens of MLX
  decode — the most quotable standalone finding to date.)
- **CPU:GPU energy division by phase**: does the rail mix shift between
  compute-bound prefill and memory-bound decode? Upstream of split
  economics.
- **KV-growth decode drift**: does per-token energy rise with sequence
  position? Valid only in CHUNKED form — token cadence (~4 ms) far
  outruns the power sampler (~113 ms); no per-token joule claims.
- **Cooldown recovery as thermal characterization**: recovery time vs
  preceding run intensity; cap-hit rates (observed: one 305 s cap-hit vs a
  117 s recovery in the first flagship experiment).
- **Failure frontier**: structured `unsupported` bundles as data — which
  model/quant/context combinations fit, fail, or throttle. Competitors
  discard their failures.
- **Cold-start / keep-warm energy**: model-load joules and the reload-vs-
  resident breakeven. Needs sampling outside the current measured window
  (harness extension).
- **Energy-per-correct-answer vs difficulty** (C-004): instrumented by the
  `affine_mod_ladder_v1` scored workload profile (see below). Claim shape
  pinned by the council: "energy per correct answer rises as accuracy
  falls under a controlled per-attempt energy envelope" — difficulty is
  DESIGNED to hold token budget approximately constant, and observed
  token/stop-reason distributions must be reported to verify residual
  EOS/output-length effects are negligible (wrong-answers-terminate-early
  would bias the curve's magnitude). NOT "difficulty causes energy."
  Amendment 2026-07-08 (C-014): before any scored campaign, an
  envelope-validation smoke gate must show level-invariant emitted-token
  and stop-reason distributions; energy/correct also requires the binomial
  guard in AP-5 (`docs/contracts/analysis_plans.md`). The full 64-level
  scored campaign is deferred until C5-1.9 has a claims-index/figure
  consumer.
- **Speculative-decoding energy**: joules per accepted token with/without
  a draft model. Needs runtime support + quality-equivalence controls.
- **Power-mode Pareto**: energy-latency tradeoff across OS power modes;
  wait until power mode is a first-class config/environment field.
- **Deferred (C-003/C-004 unanimous): general joules-per-solved-task /
  intelligence-per-joule** — drags in accuracy-evaluation policy before
  the measurement dataset matures, and sits in Intelligence per Watt's
  lane where JouleWise is least differentiated. The quarantined ladder
  profile above is the minimal version that survives.

## Instrument expansions adopted by C-004 (queue P2-009 / P2-010)

- **P2-009 rich telemetry (land FIRST — zero capture cost):** parse the
  already-captured-but-discarded plist fields — per-cluster E/P-core DVFS
  residency histograms, per-core frequencies/idle/parking, GPU
  freq/dvfm_states/idle_ratio/sw-requested-vs-achieved state, vendor
  combined_power as a cross-check — plus per-bundle environment snapshots
  (battery/charger state, Low Power Mode, memory pressure, load, display
  state; all sudo-free). Evidence this matters: decode pins the GPU at
  1380 MHz / idle_ratio 0.0 / ~22 W, and the contaminated idle window was
  mechanically visible in `gpu.idle_ratio` (first half at 13 W / 1363 MHz
  before true idle) — parsing it turns our contamination anecdote into an
  automated idle-quality gate. Opt-in `rich_telemetry` tier later: the
  `tasks` sampler (per-process attribution — the direct answer to
  background contamination), disk/network samplers.
- **P2-010 scored workload suite v1:** `affine_mod_ladder_v1` per the
  C-004 design (seed-deterministic SHA-256-derived modular recurrences;
  difficulty = iteration count with prompt shape and answer length fixed;
  exact-integer scoring; levels `{1, 2, 4, 8, 16, 32, 64}`, 16 items/level;
  suite-per-bundle with item/level marker events; level-window energy
  primary; per-item flagged unidentifiable below minimum samples;
  correctness lives in stdlib `joulewise/workloads.py`, scored by the
  reducer so summaries stay re-reducible). Quarantine rules (C-004):
  one optional workload profile, correctness as annotation, no
  "difficulty causes energy" claims. Amendment 2026-07-08 (C-014):
  P2-010 splits into P2-010a suite substrate and P2-010b smoke ladder;
  the full scored ladder remains deferred as above.
  Amendment 2026-07-08 (D-047.1): the level set is the ratified
  powers-of-two set above, not a linear 1..64 sweep.

# Suite architecture v2, benchmark interop, and capability map (Council C-015, 2026-07-08)

## Suite mechanism

C-015 adopts one suite mechanism for benchmark breadth: a suite CAMPAIGN is
`B` whole-suite bundles x `k` distinct items; each suite bundle executes
its `k` items once (`r_within = 1`).
Replication is the count of whole-suite bundles (`B >= 5`, top-up to
`B = 10` near the floor). Item windows inside one bundle are breadth and
attribution evidence, not independent `n` (D-038/AP rules).

Within-bundle repeats are reserved for sentinel items. They estimate
order/cache/thermal effects and same-session repeatability; they never
inflate `n` (C-015). There are no per-item micro-cooldowns by default:
back-to-back execution is a named session ecology, not a flaw. Order
rotates round-robin or Latin-square across bundles, with `item_index`,
`block_index`, `position`, `prev_item`, `prefix_group`, and `order_seed`
recorded (C-015).

Split a suite into balanced blocks when measured wall time exceeds roughly
10-15 minutes or when drift sentinels / floor identifiability degrade.
The first default is `k = 24`; mature panels may use `k = 48` only after
Window A floors and drift checks are clean (C-015). Throughput arithmetic:
`suite_items_per_hour = 3600 * k / (load + idle + cooldown + k * item_runtime)`,
which buys roughly 3-15x item coverage versus one-item bundles, while
`B` remains the `n` and items remain breadth (C-015).

Architectural line: after P2-010a, no workload expansion gets bespoke
marker/window plumbing. New benchmarks are manifests plus generators.
`affine_mod_ladder_v1`, `jw_mixed_v1`, `q4_l3_shape_grid_v1`, the content
sentinel, and benchmark imports are all profiles of the same suite
manifest, marker, and window mechanism (C-015).

## Minimal substrate scope

P2-010a is capped to the minimal generic substrate (C-015): suite/item/block/level
markers, `BundleReader.item_windows()`, source/category/output-policy
fields, per-item token/stop/response hashes, order/cache metadata, manifest
validation, and the per-item validity/status model below. Future
`docs/contracts/run_bundle_layout.md` fields for suite/item/block/level
markers and per-item outputs land with implementation, not in this docs batch
(C-015).

P2-010a status enum:

- `succeeded`
- `malformed`
- `capped`
- `runtime_failed`
- `below_floor`
- `excluded_from_claim`

Aggregation rules (C-015): a block or suite remains claim-usable when the
predeclared aggregation level has enough `succeeded` item windows, paired
markers validate, strict bundle validation passes, and failed/excluded
items are reported rather than silently dropped. `below_floor` items may
contribute only to block/suite-level windows, not item-level joule claims.
`malformed`, `capped`, and `runtime_failed` items remain provenance and
failure-frontier evidence but do not enter numeric claim denominators
unless an AP row predeclares that status as part of the endpoint.
`excluded_from_claim` is an explicit analysis decision with a reason and
does not make the surrounding strict-valid bundle unusable by itself.

Deferred from P2-010a (C-015): scorers, import-specific fields, and rich
difficulty machinery until suite profiles need them.

## `suite_manifest` field sketch

Trimmed P2-010a substrate scope (C-015):

```yaml
schema_version
suite_id
suite_profile
suite_revision
suite_seed
generator:
  name
  version
  parameters_hash
analysis_contract:
  independent_unit
  primary_window_class
  allowed_aggregation_levels
execution_policy:
  order_policy
  within_bundle_repeats
  cooldown_policy
  cache_policy
  warmup_policy
  default_output_policy
source_manifest:
  source_id
  source_kind
  revision
  subset_id
  subset_sha256
  license
  contamination_note
items:
  - item_id
    item_type
    category
    difficulty:
      axis
      value
      scale
      label
      source
      quarantine_note
    shape:
      planned_prompt_tokens
      planned_output_tokens
      prompt_level
      decode_level
    source:
      source_item_id
      source_sha256
      prompt_template_id
      license
      contamination_note
    grouping:
      condition_id
      block_id
      level_id
      prefix_group_id
    output_policy
    status_policy
    tags
markers:
  suite_start_event
  suite_end_event
  block_start_event
  block_end_event
  level_start_event
  level_end_event
  item_start_event
  item_end_event
outputs:
  per_item_response_hash
  per_item_token_count
  per_item_stop_reason
  per_item_status
```

Amendments 2026-07-08 (D-044/D-045/D-046): the sketch is historical and
receives these additive pins. `outputs` gains `per_item_response_text`,
with response text carried in `outputs/suite_items.jsonl` (D-045.8).
`markers` and `outputs` are optional in authored manifests, materialized
to pinned defaults, validated when present, and included in the canonical
effective-manifest hash (D-044/D-045.3). Items gain an additive,
mutually-exclusive `prompt_token_ids` source for ids-native sentinels,
with per-item prompt identity using the D-033 token-ID hash
(D-045.5/D-046).

Deferred fields (C-015): `scoring.scorer_id`,
`scoring.expected_answer_hash`, `scoring.correctness_quarantine`, import-
specific source fields, and richer grouping/difficulty structures such as
`pair_id` and `holdout_role` until a profile and AP row need them.
AP-5's smoke-ladder acceptance already requires level-window energy, so
the deferral condition is met at birth (verification catch, C-015).

## Difficulty metadata rule

Difficulty is first-class quarantined item metadata (C-015):
`{axis, value, scale, label, source}`. Shape is not difficulty:
`q4_l3_shape_grid_v1` prompt/decode cells stay under `shape`, not
`difficulty`. Difficulty metadata enables stratified analysis and envelope
checks; it never licenses "difficulty causes energy" or
intelligence-per-joule wording, and the C-004 quarantine composes.

## Benchmark import

`benchmark_import` is a thin source-to-suite manifest that composes with
the C-005 frozen-subset discipline: hash-manifested subsets, never
"latest split" (C-015). Field sketch:

```text
schema_version
manifest_id
suite_profile
source_benchmark:
  source_id
  name
  upstream_url
  citation
  license_id
  license_text_sha256
  redistribution_policy
  revision_or_commit
  retrieval_date
  source_archive_sha256
  source_split
contamination:
  note
  known_public_benchmark
  intended_use
  prohibited_claims
subset:
  selection_rule
  selection_rule_sha256
  selector_version
  selected_item_ids
  selected_item_ids_sha256
  canonical_subset_json_sha256
prompt_mapping:
  prompt_template_id
  prompt_template_sha256
  source_fields_used
  render_policy
  rendered_prompt_sha256_policy
  output_policy
expected_answer:
  source_field
  stored_as
  expected_answer_sha256
  quarantine: true
  scorer_allowed: false
items:
  suite_item_id
  source_item_id
  source_row_sha256
  source_position
  type_label
  difficulty_label
  difficulty_source
  category
  level
  prompt_template_id
  expected_answer_sha256
  license_override
  contamination_override
  shape_hints
  tags
```

First target: HumanEval as a plumbing smoke import, not a difficulty or
accuracy paper (C-015). Rationale: MIT license, small recognizable corpus,
contamination is explicit and quarantined, 256/512-token code completions
clear the observed ~9 Hz item-window floor more plausibly than one-letter
answers, and `difficulty_label = none/source_not_provided` is acceptable
for a plumbing smoke. MMLU and tinyBenchmarks are rejected as first import
targets because they drag the project toward short-answer score estimation
or benchmark-score estimation. FLORES is the second import target for
tokenizer/multilingual science (C5-W.4/C5-I.3), not the first plumbing
target (C-015).

Claims unlocked by imports (C-015): L0 "JouleWise can freeze and execute an
external benchmark subset as suite items with auditable provenance"; L1
"on a named stack/boundary/output policy, external-shaped items produced
observed item/subset energy and token/stop distributions"; L2 only after an
AP row and repeated strict-valid bundles. Never claim accuracy, pass@k,
capability, benchmark-score standing, or intelligence per joule from this
layer (C-015/C-004).

## Export / energy layer

C-015 adopts a marker-emitting shim for export. The external harness owns
prompts, generation semantics, accuracy artifacts, and metric artifacts.
JouleWise owns power capture, bundle assembly, marker validation, and
energy reduction. The full contract lives in
`docs/contracts/adapter_contracts.md`.

P2-022 is a verdict-shaped feasibility spike (C-015) with verdicts:

- `external_markers_supported`
- `partial(<limitation>)`
- `external_markers_unsupported`

(contract home: docs/contracts/adapter_contracts.md)

P2-022 inherits D-035 subprocess isolation and D-036 computed-verdict
discipline. Its scope is pinned to energy-layer feasibility only (C-015):
3+ marked items, external result artifact hashed, strict bundle valid, no
accuracy interpretation, no leaderboard join, no pass@k-energy ratio, and
no general adapter framework. Any L2 energy comparison from the shim needs
strict bundles, repeated runs, same or calibrated boundary, and an AP row
(C-015).

## Kill / defer

Kill or defer:

- leaderboard integration.
- live dataset fetching.
- "latest split" support.
- JouleWise accuracy scoring beyond quarantined annotation.
- external judge calls, retries, pass@k, or benchmark-score normalization.
- full adapter per harness as the first export path.
- generation-callable wrapper as the first export path.
- MMLU/tinyBenchmarks as first import.
- public energy model-card leaderboard before cross-lab replication.
- per-item uncertainty treated as independent replication.
- any intelligence-per-joule ratio.

## New questions

Interop questions adopted by C-015:

- **C5-I.1 External benchmark energy signatures:** Do imported benchmark
  families have distinguishable energy profiles after matching token shape
  and output policy? Ceiling L2, no capability claim.
- **C5-I.2 Published-difficulty strata vs energy:** Do source-provided
  difficulty or published accuracy strata correlate with energy/stop
  behavior? Ceiling L1 association unless preplanned repeated-bundle L2;
  never "difficulty causes energy."
- **C5-I.3 FLORES tokenizer fertility tax:** For semantic-matched vs
  token-matched FLORES items, how much energy follows tokenizer fertility
  by script/language? Ceiling L2.
- **C5-I.4 Harness overhead floor:** For external harnesses, when does
  harness/process overhead dominate item energy? Ceiling L1/L2
  measurement-method result.
- **C5-I.5 Prompt-template energy sensitivity:** For the same external
  item, how much does canonical vs JouleWise-rendered prompt format change
  energy? Ceiling L2.

Architecture-unlocked candidates, recorded post-2O/post-floor and not
promised campaign work (C-015):

- **Session-shape energy:** does a realistic mixed session cost what
  fixed+prompt+decode coefficients predict, or is there a session overhead
  term?
- **Order-position effects:** how much does energy drift by item position
  after controlling for shape and category?
- **Cache/prefix economics:** what is the joule benefit of prefix reuse,
  resident model state, or prompt-cache warmth versus cold independent
  requests?
- **Reload-vs-resident scheduling:** at what item/session length does
  suite-style batching dominate one-request bundles in total energy and
  wall time?

## Capability map by claim ceiling

### Today

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can JouleWise produce auditable local-LLM energy evidence? | L0/L1 | "The harness can execute `<target/runtime/telemetry>` and preserve config, metadata, events, raw power trace, raw telemetry, outputs, and reducer summary in a strict-valid run bundle." | Existing Mac/MLX/powermetrics bundles; strict bundle layout. | Strict validation proves re-derivation of recorded evidence, not independent hardware rerun. |
| What did Qwen2.5-1.5B consume on the M3 Max for the 512-output-token smoke workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under `<workload/output policy>`, Qwen2.5-1.5B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-06 2I: about 47 J gross, about 94 ms TTFT, about 257 tok/s, gross CV 1.4%. | Idle-subtracted result is contaminated in rep 1; use gross for the cleanest current instrument result. |
| What did Qwen3.5-122B-A10B consume on the same workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under the same 512-output-token workload, Qwen3.5-122B-A10B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-07: about 304 J gross, about 270 ms TTFT, about 46 tok/s, gross CV 0.3%. | L1 only; n=3 is below comparative protocol. |
| Did the two observed models demonstrate active-parameter scaling? | No; L1 hypothesis only | "The two observed Mac/MLX/powermetrics points are consistent with a fixed/marginal decode-time hypothesis, but they do not support an active-parameter scaling claim." | 122B addendum and claims-ladder downgrade. | Model size, architecture, quantization, and runtime details are confounded. |
| Are short prefill phase joules resolvable at current powermetrics cadence? | L1 "not resolvable" | "On `M3 Max / MLX / powermetrics`, short-prefill phase energy for `<~94 ms window>` is not resolvable at the observed sampling cadence and must not be reported as a standalone joule result." | Observed about 8.8-8.9 Hz; Phase 4 says about 94 ms prefill has fewer than one sample. | Sampler cadence remains near current observed rate. |
| Can same-machine MLX KV replay preserve token identity and size prediction? | L1 feasibility result | "On this M3 Max / mlx-lm stack, prompt-cache replay was supported for `<prompt length>`: resumed greedy decode matched monolithic tokens and measured cache size was within `<delta>` of the KV-size prediction." | Stage 3.0.1: 1024/2048 prompt cache, 64/64 tokens identical, +0.018%/+0.009% size delta. | Same machine/same venv only; not cross-machine portability. |

### After Window A

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| What is the detection floor per metric/window? | L1 methodology result | "For `<target/backend/metric/window class>`, differences below `<floor>` J are not resolvable; supported comparisons use `max(floor_abs_j, floor_cmp_j)`." | P2-015 calibration. | Calibration machine state is representative of later quiet campaigns. |
| What are per-profile Mac baselines? | L1 per condition | "On `M3 Max / MLX / powermetrics`, `<model>` under `<profile>` observed `<energy_request_j>`, `<gross J>`, `<mJ/output-token>`, `<TTFT>`, and `<throughput>` with 95% t-intervals over n=5." | 2M: `short_short`, `long_short`, `short_long`, `mid_mid`. | Output-token denominator and output policy must be runtime-observed/pinned. |
| Does workload shape change request energy on one stack? | L2 | "Within `M3 Max / MLX / powermetrics`, `<profile A>` differed from `<profile B>` for `<model>` by `<effect>` on `<metric/window>`, with n=5 per condition, CIs, manifest order, and effect above floor." | 2M + AP-2. | Drift sentinels and block-position metadata LANDED 2026-07-08 (PR #15). |
| Is prefill/decode power asymmetry visible at long context? | L2 | "Within `M3 Max / MLX / powermetrics`, `long_short` and `short_long` differed in gross phase-window power/energy structure by `<effect>`, above the Window A floor; short-prefill windows remain not resolvable." | 2M/AP-2. | Phase claims are gross-only until phase-idle modeling exists. |
| Do same-boundary efficiency rankings flip across 2M profiles? | L2 | "Within `M3 Max / MLX / powermetrics`, `<condition A>` ranked above `<condition B>` for `<metric>` on `<shape>` only where rank gap exceeded comparison MDE; otherwise the result is an unresolved tie." | 2M + AP-3. | Two-model/four-shape grid may produce unresolved ties rather than rank claims. |
| Do rail/DVFS signatures differ by phase? | L2 structural, not absolute rail truth | "Within `M3 Max / MLX / powermetrics`, rich telemetry showed `<GPU/CPU/ANE/DVFS>` structure differed between `<phase/profile>` and `<phase/profile>`; the claim is about modeled-rail structure, not full-system watts." | 2M with P2-009 rich telemetry. | Powermetrics rails are modeled SoC subsystems, not wall power. |

### After Window B + substrate

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can Q4 fit fixed + prompt + decode energy terms? | L3 | "For `<target/model/quant/policy>`, the categorical model `E = fixed + prompt_level + decode_level` predicted held-out cells `(512,256)` and `(4096,512)` within `<error>` after floor and residual checks." | P2-019 `q4_l3_shape_grid_v1`, AP-1. | Holdouts may fail or effects may be below floor, forcing L1/L2 downgrade. |
| Do rankings stay stable on the full shape grid? | L2 | "Within the same boundary, `<model/quant/runtime A>` ranked above `<B>` on `<shape/metric>` only where rank gap exceeded comparison MDE; otherwise unresolved tie." | Window B grid + AP-3. | Rank gaps may be smaller than MDE. |
| Does synthetic prompt content matter at fixed shape? | L2 | "At equal shape, `<content condition>` differed from repeated-seed control by `<delta>` on request energy, with n sized from Window A and above floor." | P2-020 content sentinel, AP-6. | Realized shape/stop policy must stay matched. |
| Does category explain energy beyond token counts? | L2 | "On the common `512/256 fixed_budget_exact` stratum, category residual after controlling for shape was `<delta>`; equivalence/null only if the residual CI lies entirely within ±2% of request energy AND the 2% margin exceeds max(floor_abs_j, floor_cmp_j) (AP-4 gate)." | `jw_mixed_v1` identification core after P2-010a; AP-4. | Small category deltas may be below floor. |
| Does natural-EOS "thinking" inflate reasoning-model energy? | L2 | "For `<reasoning model>`, natural-EOS reasoning requests consumed `<delta>` more request energy than fixed-budget controls, attributable to observed emitted-token/stop-reason distributions, not hidden correctness filtering." | `jw_mixed_v1` natural-EOS pilot. | Output-length inflation must be observed cleanly; no accuracy/judge claim. |
| Is multilingual tokenizer fertility an energy tax? | L2 | "For `<script/language>`, semantic-matched energy differed from token-matched controls by `<delta>`; token-matched null/effect reported separately." | `jw_mixed_v1` multilingual legs; FLORES after HumanEval smoke. | Source licensing and tokenizer-shape matching must be exact. |
| Energy per correct answer under controlled envelope? | L2, only after P2-010b/full scored run | "On the controlled affine ladder, `<model class>` observed `<energy_per_correct>` at `<level band>` only where level-window energy cleared floor and the correctness denominator guard passed; no intelligence-per-joule claim." | P2-010a substrate + P2-010b smoke + later scored campaign; AP-5. | Envelope validation and binomial guard can force `not estimable`. |
| External marked-runner energy layer? | L1/L2 with AP row | "External harness `<X>` version `<Y>` reported metric artifact `<Z>`; JouleWise measured energy for the same marked item/subset windows." | P2-022 shim spike, then AP-covered repetitions only. | Harness markers must pair, stay inside measured windows, and preserve hashed result artifacts. |
| HumanEval import smoke? | L0/L1 | "JouleWise froze and executed a HumanEval subset as suite items with auditable provenance and observed item/subset energy under a named output policy." | P2-023 after P2-022. | Plumbing smoke only; no pass@k, accuracy, or coding-capability interpretation. |

P2-022 shim and P2-023 HumanEval rows are post-2M + substrate (Window B not required).

### Hardware-gated

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Does split inference reduce energy? | L2 boundary-labeled; stronger with wall calibration | "For `<device pair/link/model/shape>`, split total energy `<prefill + serialize + transfer + deserialize + decode>` was `<less/greater>` than the better monolithic reference by `<delta>`, with boundaries named and calibration status stated." | Phase 3 split; Q1/F4/F5. | Cross-boundary sums are descriptive unless calibrated. |
| How sensitive is split energy to link speed? | L2 | "For `<payload/model/pair>`, changing `<1GbE/2.5GbE/10GbE>` changed transfer energy/time by `<delta>` and moved/did not move the crossover within the measured range." | P1-004 links + transfer bench. | Link throughput must be measured, not assumed. |
| What is the split energy-latency Pareto frontier? | L2 | "Within `<comparison set>`, `<configuration>` is Pareto-frontier because no measured alternative had both lower energy/token and lower `<latency metric>`." | Phase 3 + F6. | Latency metric choice must be fixed per figure. |
| Does measurement boundary change conclusions? | L2; L4 only with replication | "For `<condition pair>`, the conclusion under platform rails `<matched/flipped>` under `wall_meter AC` by `<delta>`." | P1-003 wall meter; Q6/F11. | Wall-meter synchronization/export quality. |
| Do KV-size predictions match measured transfer economics? | L2 | "For `<runtime/model/link>`, analytic KV size predicted serialized payload within `<error>` and transfer energy/GiB within `<interval>`." | P1-004 + P1-006; C5-2.3. | Runtime cache format must be portable or explicitly scoped. |
| Do device rankings generalize beyond one machine? | L2 within boundary; L4 with second unit/calibration | "Across named `<units/stacks>`, `<finding>` replicated under stated workloads and boundaries; cross-boundary quantitative ranking uses named calibration bundles." | P1-006 devices, second unit, wall/USB-C, cross-lab. | Unit-to-unit variance may dominate current floors. |
| Local-vs-datacenter full-system crossover? | Scenario result, not measured-equivalent cloud claim | "Under documented external datacenter-energy assumptions and local `wall_meter AC` measurement, local request energy was `<less/greater>` than the modeled remote alternative for `<workload>`." | Wall meter + network leg; C5-2.9. | Cloud-side energy remains assumption-based, not measured by JouleWise. |

C-015 records three unscheduled cheap campaigns as a select-after-floors
shortlist, not stealth scope: C5-1.6 sampler ABBA, C5-1.12 quantization
benefit decomposition, and C5-1.8 runtime energy attribution. Queue row
P2-024 owns the post-Window-A selection.


# Hardware-gated research agenda — steelmanned potential (Council C-005)

Drafted 2026-07-07 by council C-005 (session shape B; see
`docs/council_log.md` C-005 for positions, adjudications, and dissents).
Format follows `docs/research_question_bank.md`: candidate questions, not
promotions — promotion still requires a named RQ slot in
`PROJECT_STATUS.md`, a data plan that does not displace queue ranks, and
scope fit. IDs here are `C5-<tier>.<n>` to avoid colliding with Q1-Q6.

Every question below survived a devil's-advocate (examiner) round; the
scoping is deliberate, not decorative. Standing kills re-affirmed and
inherited by everything here: no per-token joule claims (~9 Hz sampler vs
~4 ms token cadence — chunked windows only), no unqualified absolute-joule
claims from modeled rails, no general intelligence-per-joule, claim
wording "on this M3 Max / MLX / powermetrics" until a second unit or lab
exists, and present-tense capability claims only for landed code (P2-010 scored suite is QUEUED,
not landed (D-014/P2-011 aggregation and P2-009 telemetry LANDED 2026-07-07)).
(Amendment 2026-07-08: the P2-010 substrate + affine core + generator
engine are now LANDED (PRs #17-#20, D-044..D-047); still not landed:
envelope-gate script, real-tokenizer manifests, all suite campaigns.)

## Why this instrument matters (steelman preamble, examiner-scoped)

**Auditability is the differentiator, not topic novelty.** Energy
benchmarks exist (MLPerf Power; TokenPowerBench; ML.ENERGY-style
datacenter work) — what does not exist is local-inference joules/token
that a skeptic can re-derive: JouleWise publishes self-contained bundles
where config, raw power trace, vendor telemetry, event log, and outputs
are preserved and `validate-bundle --strict` proves the summary re-reduces
identically from raw evidence. Energy tables are otherwise unauditable at
exactly the step that matters.

**Energy per request is becoming the binding constraint on local AI.**
Battery, thermal envelope, and sustained throughput all reduce to joules
per completed request. Latency says whether a local model feels fast
once; `energy_request_j` with uncertainty says whether it can run all day.
The instrument already resolves this at CV 0.3-1.4% across repetitions.

**Apple-Silicon unified memory is a clean window into the memory-bound
decode regime.** The measured 1.5B vs 122B-MoE pair showed energy/token
numerically aligning with the active-parameter ratio while decode power
stayed nearly flat (~23.5 → ~27.5 W). That is hypothesis-generating, not
a scaling result (see C5-1.1), but it demonstrates that the instrument can
see the shape of the regime that throughput benchmarks cannot.

**Negative results are structured data.** did-not-fit, throttle,
contaminated-idle, and cap-hit outcomes produce complete `unsupported` or
quality-flagged bundles. Competitors discard their failures; here the
feasibility frontier is itself a reportable dataset (this is how a
negative Hailo verdict stays a finding).

**The benchmark can referee efficiency claims.** Quantization, runtime,
and architecture "efficiency" claims mix latency, memory, and energy with
no common accounting. Typed configs + one reducer + named measurement
boundaries make within-boundary refereeing possible today and boundary-
labeled cross-target comparisons possible with planned hardware.

**Q4's fixed-vs-marginal model turns benchmark data into engineering
budgets.** `E = fixed + prefill(p) + decode(d)` per target/model/quant
lets an app team budget a workload distribution (an agent session, a RAG
pipeline) from benchmark coefficients — the bridge from instrument to
battery-life engineering.

**The split study is a first-of-kind edge measurement.** Prefill/decode
disaggregation is argued from datacenter throughput; nobody has measured
the ENERGY crossover on local links with both-end power sampling and
per-stage decomposition (prefill/serialize/transfer/deserialize/decode).
Either verdict — crossover exists or doesn't in range — is publishable.
(Examiner note, recorded as standing tension: this is also the most
hardware-gated item in the agenda; the feasibility-first Phase 3 ladder
is the mitigation.)

**The infrastructure outlives any single result.** Every future target is
forced through the same contract (config → bundle → strict re-reduction →
boundary-named summary). The M3 Max numbers are the demo; the reusable
referee is the contribution.

## TIER 1 — answerable with current hardware (M3 Max alone)

Landed software (P2-009 rich telemetry, P2-011 uncertainty
aggregation, 2M campaign tooling — all 2026-07-07) is available;
queued software (P2-010 scored suite) is assumed where noted; no new
hardware. (Amendment 2026-07-08: the suite substrate/ladder-core/
generators are landed, PRs #17-#20; campaign execution still pending.) Throughput reality: ~30-75 bundles/hour makes n=10-20 designs
cheap.

- **C5-1.1 Active-parameter energy scaling (the honest version of the
  122B observation).** Does decode energy/token scale with active rather
  than total parameters across dense and MoE models on one pinned stack?
  Measure on the named M3 Max / MLX / powermetrics SoC-rail boundary:
  gross decode-window joules, mean power, and throughput across 4-6 model
  points (dense 1.5B/7B/14B bridge + ≥2 MoE), same quant recipe, pinned MLX
  version, fixed shapes, n≥5 interleaved; fit gross mJ/token ~ active_params
  (+ total-param/KV covariates) with intervals. Any idle-subtracted result is
  a labeled within-device secondary sensitivity view, not the scaling
  headline (D-067).
  Hardware: now. Methodology: runtime is part of the condition — rerun
  after MLX updates as a separate condition. Threat: model families
  differ in more than active params; the dense bridge and quant pinning
  carry the inference. Who cares: efficient-ML and MoE architecture
  researchers; local-inference benchmark authors. Amendment 2026-07-08
  (C-014): with 4-6 model points, this supports descriptive L2 pairwise
  contrasts only unless the model set grows enough for a predeclared
  one-covariate fit; never fit active+total+KV covariates on 4-6 model
  points.

- **C5-1.2 Context-length energy scaling.** Where does measured energy
  stop being linear in prompt length? Measure: prefill/decode energy over
  prompt 128→8192 (fixed decode 64/256), n≥5; unsupported cells recorded.
  Hardware: now. Methodology: chunked windows; short-prompt prefill
  reported "unresolved at sampler resolution", never 0.03 J-style point
  claims. Threat: SoC boundary underrepresents unified-memory traffic —
  directional bias for long-context (examiner #11); flag pending Q6
  calibration. Who cares: long-context model teams, serving researchers.

- **C5-1.3 Phase-resolved compute-vs-memory signatures (uses landed P2-009 telemetry).**
  Does the rail mix and DVFS residency shift between compute-bound
  prefill and memory-bound decode, and how does the shift move with model
  size/quant? Measure: per-phase CPU:GPU energy division, GPU
  frequency/dvfm residency, idle_ratio across the 2M matrix. Hardware:
  now. Methodology: promotes the banked "CPU:GPU division by phase" item
  with the telemetry that makes it cheap. Threat: modeled rails — claims
  are about STRUCTURE (ratios, shifts), not absolute rail watts. Who
  cares: Apple/Metal/MLX performance engineers, systems-paper authors.

- **C5-1.4 DVFS residency as a throttling early-warning (uses landed P2-009 telemetry).**
  Do residency histograms and idle_ratio drift predict throttling before
  energy/throughput visibly degrade under sustained inference? Measure:
  20-60 min sustained blocks; per-rep energy, residency, cap-hit rates,
  recovery slopes; n≥5 blocks. Hardware: now. Methodology: cooldown-gate
  records and interleaving separate warmup, drift, and throttling.
  Threat: one chassis/ambient; report as within-target characterization.
  Who cares: laptop-inference tool builders, mobile/edge systems
  researchers, thermal-management teams.

- **C5-1.5 Cooldown-recovery curves and the energy tail (promotes banked
  item).** Recovery time and excess idle joules vs preceding run
  intensity; is the tail material to honest energy/request accounting?
  Measure: post-run recovery traces after an intensity ladder; time-to-
  baseline, cap-hit rate, excess joules; n≥5. Hardware: now. Threat:
  ambient sensitivity — record environment snapshots (P2-009). Who
  cares: on-device serving teams, benchmark methodology authors.

- **C5-1.6 Sampling-strategy energy overhead (power-gated).** Does
  temperature/top-p/beam sampling cost measurable energy beyond
  deterministic decoding at fixed output length? Measure: greedy vs
  sampled at fixed decode caps, recorded stop reasons; PRECONDITION:
  measured detection floor first; n≥10 paired ABBA. Hardware: now.
  Threat: plausibly below floor at n=5 — the null ("sampler choice is
  energy-free at this resolution") is the likely and still-reportable
  result. Who cares: runtime maintainers, generation-defaults tuning.

- **C5-1.7 Keep-warm vs reload breakeven (promotes banked cold-start
  item; harness extension).** Model-load joules, resident idle-power
  delta, cold-vs-warm TTFT → breakeven interarrival time per
  model/quant. Measure: load-window sampling (extension: measure outside
  current window), idle-resident deltas, n≥5. Hardware: now. Threat:
  idle-resident delta may be near the detection floor for small models;
  report identifiability. Model-load/warmup trace capture was reviewed and
  DEFERRED by C-015 (R2 items 14-15); it must land before any C5-1.7
  corpus. Who cares: desktop-assistant and agent-framework teams,
  serverless-inference researchers.

- **C5-1.8 Runtime energy attribution.** How much of measured inference
  energy belongs to the runtime, not the model? Same model artifact
  (where format permits) across MLX vs llama.cpp-Metal vs ollama on the
  same machine. Measure: energy/token, power, TTFT, rail mix over a
  shared shape grid, n≥5; artifact hashes and versions pinned. Hardware:
  now. Methodology: where formats force different artifacts (MLX vs
  GGUF), the comparison is stack-vs-stack, stated as such. Threat:
  version churn — this question is BUILT on the pinning discipline
  rather than wounded by it. Who cares: runtime maintainers, local-LLM
  users, model publishers choosing release formats.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. On the 3080 Ti, same model artifact where format
  permits: llama.cpp-CUDA vs vLLM (TensorRT-LLM gated on Ampere-support
  verification) — how much energy variance tracks kernel-library identity vs
  runtime scheduler? Ceiling: **L2 stack-vs-stack**. Forbidden upgrade: **no
  `belongs to the kernel layer` language when artifacts/formats differ; no
  runtime-agnostic kernel claims**. This is an amendment to C5-1.8, not a new
  C5-1.13 thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-1.9 MoE-vs-dense energy per correct answer, quarantined (needs
  P2-010).** Under the controlled-envelope ladder, do MoE and dense
  models at similar quality bands differ in energy per correct answer?
  Measure: affine_mod_ladder_v1 level-window energy + exact scoring;
  token/stop-reason distributions reported (EOS-bias audit). Hardware:
  now. Methodology: C-004 quarantine binds — correctness is an
  annotation; claim template "on this controlled ladder", never
  intelligence-per-joule. Who cares: MoE architecture teams, benchmark-
  methodology reviewers.

- **C5-1.10 The failure frontier as an energy dataset (promotes banked
  item).** Which model × quant × context cells fit, fail, swap, or
  throttle on 128 GB unified memory — with pre-failure energy and memory
  pressure recorded? Measure: full matrix including structured
  `unsupported` bundles, env snapshots. Hardware: now. Threat: one
  memory configuration; frame as the 128 GB-class frontier. Who cares:
  model release engineers, hardware buyers, benchmark authors.

- **C5-1.11 Dark-silicon rail utilization, systematized (promotes banked
  item; needs P2-009).** What fraction of the SoC's rails does each
  runtime/model pair energize (ANE-dark being the first quotable
  instance)? Measure: per-rail energy share and residency by phase
  across the runtime grid of C5-1.8. Hardware: now. Threat: modeled
  rails — report utilization structure, cross-checked against vendor
  combined_power. Who cares: accelerator vendors, runtime implementers.

- **C5-1.12 Quantization benefit decomposition, Mac leg.** For MLX quant
  variants of one family (4/8-bit), how much energy benefit is lower
  power vs shorter time? Measure: decode energy, mean power, throughput
  per quant at fixed shapes, n≥5. Hardware: now (extends to Tier 2 for
  CUDA/GGUF legs). Threat: quant recipes change outputs — greedy-diff
  and report divergence. Who cares: quantization researchers, edge
  deployment teams.

## Workload/query-set expansion (first-class topic, Tier 1 hardware)

Today's workloads are single-prompt fixed-shape grids plus the queued
affine ladder. (Amendment 2026-07-08: the affine ladder CORE is landed,
PRs #17-#20; the envelope-gate script and smoke campaign remain queued.) The council's workload lens designed the expansion; the
examiner frame was applied up front: at fixed token shape, most category
differences may collapse into token counts — that null is itself a
publishable result, named here the **Token-Shape Sufficiency Null**.

**Category taxonomy and expected energy mechanisms.** Six categories,
each with a mechanistic reason energy could differ and an honest
distinguishability call:
chat/instruction (high output-length variance under natural EOS; expected
NULL at fixed shape — the ecological baseline); code generation
(decode-heavy, distinct stop-reason behavior; near-null at fixed budget
unless tokenizer throughput differs on code tokens); summarization/
long-context (prefill-heavy, KV growth — YES, distinguishable via prefill
energy/TTFT/phase mix); reasoning/CoT (thinking-token inflation on
reasoning models — YES, the category effect most likely to be large,
directly measurable on the already-benchmarked Qwen3.5-122B); structured
JSON extraction (early valid-close stops make short answers cheap —
collapses at fixed envelope; probes EOS bias); multilingual (tokenizer
fertility differs sharply by script — YES when semantically matched,
expected null when token-matched; run BOTH, the pair separates fertility
from semantics).

**Realistic-vs-synthetic discipline (hybrid, both by design).**
Deterministic seed-derived synthetic profiles are the CONTROLS
(reproducible, shape-matched, redistribution-safe); pinned realistic
exemplars are the ecological probes (licensing/contamination/tokenizer
caveats recorded per source). Every realistic category runs in two modes:
`fixed_budget_exact` (greedy, EOS suppressed, fixed max_tokens — the
headline category-at-fixed-shape comparison) and `natural_eos` (greedy,
EOS allowed, stop reasons recorded — the operational-cost view). EOS-bias
rule inherited from C-004: natural termination is a workload property,
not a fairness control; wrong/short/refusal answers looking energy-cheap
must be visible in stop-reason distributions, never hidden.

**Sources to pin (hash-manifested frozen subsets, never "latest split"):**
LMSYS-Chat-1M for chat SHAPE distributions (terms-gated, not for
redistribution — derive synthetic shapes from it); HumanEval/MBPP-style
code prompts (MIT, contaminated — prompt exemplars only, no accuracy
claims); public-domain/government texts + synthetic needle controls for
summarization; GSM8K/MMLU-style items for reasoning shapes (MIT on HF,
contaminated — shape not correctness); synthetic fixed-schema records for
JSON; FLORES-200 for multilingual (CC BY-SA, parallel sentences enable
the semantic-matched leg). Where licenses are uncertain, synthetic wins.

**Concrete recommendation — `jw_mixed_v1` (adopt as the first official
workload expansion).** Amendment 2026-07-08 (C-014): this supersedes the
C-005 fixed-budget-full-first sequencing; the C-005 category/source
discipline otherwise remains intact. Phase 1 is the identification core:
all 6 categories at the common-shape identification stratum, `512/256`
`fixed_budget_exact`, synthetic + realistic where licensing is clean.
Phase 2 is a natural-EOS pilot with >=4 items/category on reasoning, JSON,
chat, and multilingual. Phase 3 is the full category panels, gated on
above-floor structure from Phases 1-2. The original full panel remains the
expansion target after the gate: 6 categories x 8 items = 48 items per
target/model/quant, n=5, categories interleaved round-robin, with the
C-005 category shapes (chat 512/256; code 4x512/256 + 4x1024/512;
summarization 4096/256; reasoning 512/512; JSON extraction 1024/128;
multilingual FLORES 8 languages semantic-matched then token-matched
512/256; ~240 bundles = 3-8 hours per target/model/quant at observed
throughput) unless the Phase 1/2 gate amends them. Harness needs (all additive): `workload_profile.category` +
`source_manifest` + sha256 + per-item `output_policy` fields; category as
a campaign-matrix axis alongside shape (never instead of it); per-item
stop reason/emitted-token/response hash in outputs; reuse P2-010a item
windows + identifiability flags; aggregation waits on P2-011. Out of
scope stays out: no accuracy evals, no judges, no retries — correctness
only as quarantined annotation. Category claims follow AP-4 in
`docs/contracts/analysis_plans.md`.
Amendment 2026-07-08 (D-046 and deferred-binding B6 disposition):
`jw.multiling` synthetic is phase-1 control material, not a C5-W.4 FLORES
replacement; the FLORES 6-vs-8 language count and token-matched
substitution decision are deferred to the FLORES/source session.

**Questions it unlocks (Tier 1):**

- **C5-W.1 Does category explain energy beyond token counts?** Paired
  synthetic controls vs realistic exemplars at identical shape; either a
  category effect or the Token-Shape Sufficiency Null — both reportable.
  Threat: small deltas need the detection floor first (examiner #2). The
  reportable comparison is AP-4 in `docs/contracts/analysis_plans.md`,
  using the common-shape stratum and the predeclared equivalence margin
  from C-014. Who cares: benchmark authors, app engineers budgeting
  features.
- **C5-W.2 Does thinking-token inflation dominate reasoning-model request
  energy?** Fixed-budget vs natural-EOS on the reasoning flagship;
  measures the energy price of "thinking" as output-length inflation.
  Who cares: reasoning-model teams, agent builders choosing modes.
- **C5-W.3 Is category energy-ranking stable across models and quants?**
  The workload-axis analogue of Q5; do code/long-context/reasoning flip
  the ordering? Who cares: procurement, model-selection tooling.
- **C5-W.4 Tokenizer fertility as an energy tax.** Semantic-matched vs
  token-matched multilingual pairs isolate joules attributable to
  tokenizer choice per script. Who cares: multilingual deployment,
  tokenizer designers.


## TIER 2 — unlocked by already-planned hardware gates

Gates by name: P1-006 device access (owned RTX 3050; Jetson Orin Nano),
the 3080 Ti borrow window (Phase 3 interconnect sweep only), P1-003 wall
meter decision (R-007), P1-004 network topology (1GbE / 2.5GbE / optional
10GbE).

- **C5-2.1 Quantization decomposition, cross-stack.** C5-1.12 extended
  to llama.cpp-CUDA/vLLM on the 3050: is the time-vs-watts split of
  quantization benefit hardware-dependent? Gate: P1-006. Threat:
  nvidia-smi board boundary ≠ SoC boundary — within-target decomposition
  first, cross-target only boundary-labeled. Who cares: quantization and
  runtime teams.

- **C5-2.2 Batch size and the prefill/decode energy split.** Does
  static batching reshape gross energy/request and the phase split under
  an interactive latency bound? Measure: B in {1,2,4,8,16}, group gross
  energy and gross joules/request within the named target/telemetry
  boundary, latency distribution, and structured memory-fit failures.
  The Mac leg is MINTED (2026-07-16: AXI-SB verdict `supported` on pinned
  mlx-lm 0.31.3, lead-run B∈{2,4} live probes with full per-request
  observability — `docs/specs/axi/sb_static_batch_verdict.md`); execution
  still requires the follow-on batch adapter row, P2-015 floors, and its own
  scheduled quiet-Mac block. The serving-style leg remains gated on P1-006.
  Continuous batching is a post-capstone extension (D-070).
  Who cares: serving researchers, scheduler developers.

- **C5-2.3 Predicted-vs-measured KV economics.** Does the analytic
  kv-size model predict serialized cache size, transfer energy, and
  deserialize energy? Measure: transfer joules/GiB both ends over
  payload ladder 16 MiB-2 GiB per link; deserialize windows; predicted
  vs actual deltas calibrate the model. Gates: P1-004 links + any second
  node (P1-006). Methodology: both-end sampling, clock-offset bounds
  flagged; this is the instrument's designed home turf. Who cares:
  disaggregated-inference researchers, KV-cache system builders.

- **C5-2.4 KV-cache quantization end-to-end.** Does q8_0 cache save
  energy after serialize/deserialize overhead, or only bytes? Gates:
  P1-006 + P1-004 (llama.cpp cache portability spike verdict). Who
  cares: llama.cpp maintainers, KV-compression researchers.

- **C5-2.5 Speculative decoding joules per ACCEPTED token (promotes
  banked item).** With/without draft model at output equivalence.
  Measure: total joules, acceptance rate, joules/accepted-token, n≥5.
  Gate: runtime support (MLX or 3050 stack). Methodology: the
  accepted-token denominator is the trap the harness's token accounting
  defuses. Who cares: speculative-decoding researchers, runtime teams.

  **2026-07-17 DSpark/DFlash candidate riders (D-075).** These remain
  riders on C5-2.5, not four independent theses; every effect is floor-gated
  and `C-023-OUTPUT-IDENTITY` is binding. Evidence for all four:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

  - **C5-2.5a — cross-method contrast.** Status: **candidate (deferred
    rider)**; earliest phase: **NS**. At matched target model, quantization,
    prompt roster, and output equivalence, do a fixed-K block-diffusion
    drafter (DFlash) and a variable-K confidence-scheduled drafter (DSpark)
    differ in gross request energy and gross J/committed-output-token on the
    same MLX stack? Ceiling: **L2**. Forbidden upgrade: **No cross-method
    efficiency generalization beyond the measured target/runtime/tokenizer
    pair; accepted-draft J/token stays a mechanism diagnostic, never the
    on/off efficiency denominator (token_normalization.md D-037 rider).** It
    stays out of the committed standalone set until a prospective
    cross-mechanism design is affordable.

  - **C5-2.5b — proposal-work secondary.** Status: **candidate**; earliest
    phase: **PF**. Is proposal length an energy knob: holding drafter and
    target fixed, does gross J/committed-output-token vary systematically
    with realized mean proposed-K (DFlash block-size sweep 8/16 vs DSpark's
    dynamic schedule), i.e. does per-round proposed work enter the Q4
    coefficients? Ceiling: **L2**. Forbidden upgrade: **No claim that
    K-scheduling saves energy in general; result scoped to one
    runtime/target/boundary, and realized per-round tokens_proposed must be
    runtime-observed, never inferred from the configured cap.**

  - **C5-2.5c — primary Q4 break-even rider.** Status: **candidate**;
    earliest phase: **PF**. Drafter-overhead economics: at what aggregate
    acceptance rate does spec-on gross energy break even with spec-off for
    each drafter class (block-diffusion vs semi-autoregressive vs native MTP
    if a supported runtime lands), at matched output? Ceiling: **L2**.
    Forbidden upgrade: **No serving-system or cross-hardware generalization
    from one pair; the MTP arm is contingent on an AXI-SC supported verdict
    and is a separate frozen family (FAM-AXI-SPEC-NATIVE-MTP), never pooled
    with draft_model arms.**

  - **C5-2.5d — mandatory contamination control.** Status: **candidate**;
    earliest phase: **PF**. Hybrid-lookup contamination bound: how much does
    mlx-dspark's drafter-free n-gram lookup path (on by default) shift
    measured gross energy and acceptance accounting vs `--no-lookup-drafts`,
    quantified as an attribution-contamination diagnostic? Ceiling: **L2
    (diagnostic/methods row)**. Forbidden upgrade: **No mechanism-yield or
    efficiency claim from mixed-origin rounds; the row exists to justify the
    mode pin, not to rank lookup vs drafter.**

- **C5-2.6 Energy-optimal request coalescing under a latency bound.**
  Replayed arrival traces × coalescing windows → joules/request vs
  p95 latency Pareto. Gate: P1-006. Who cares: edge gateways, serving
  schedulers.

- **C5-2.7 Device perf/W rankings with runtime held constant (extends
  Q5, doesn't duplicate it).** Same llama.cpp build/model/quant across
  M3 Max / 3050 / Orin (+3080 Ti in window): do rankings survive
  workload changes when the RUNTIME variable is removed? Gates: P1-006,
  borrow window. Threat: boundary heterogeneity — ranking claims are
  per-boundary until wall-calibrated (C5-2.9). Who cares: hardware
  reviewers, edge procurement.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. When the runtime is held constant (same llama.cpp
  build/model/quant) across M3 Max Metal and 3080 Ti CUDA, does recorded
  kernel-layer identity (attention kernel, BLAS backend, graph mode) explain
  residual energy structure beyond device? Ceiling: **L2 within each
  measurement boundary; per-boundary only until wall-calibrated (C5-2.9)**.
  Forbidden upgrade: **no cross-vendor kernel-API efficiency ranking; no
  cross-device winner across heterogeneous boundaries**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.8 Placement-policy optimality from Q4 coefficients.** Can
  fitted fixed+marginal coefficients + measured transfer costs choose
  the energy-optimal prefill/decode placement, validated against
  measured splits? Gates: full Phase 3 set (P1-006, P1-004, borrow
  window). Methodology: modeled-vs-measured labeled; composite bundles.
  Who cares: disaggregated-serving and placement-policy researchers.

- **C5-2.9 Local-vs-datacenter crossover economics (survivor of the
  carbon-label kill).** When is a local request energy-cheaper than
  shipping it out — full-system watts, transfer included, datacenter
  side as DOCUMENTED published-figure assumptions, never measured-
  equivalent? Gates: P1-003 wall meter (+P1-004 for transfer leg).
  Methodology: the wall meter is what makes the local side full-system
  honest; boundary-directional bias (examiner #11) is why SoC rails
  alone can't carry this. Who cares: sustainability-of-ML community,
  enterprise local-vs-cloud deciders.

- **C5-2.10 Boundary-directional bias quantification (elevates Q6).**
  Not just "does the boundary change conclusions" but WHICH comparisons
  flip: memory-heavy vs compute-heavy conditions should diverge
  rail-vs-wall differently. Gate: P1-003. Methodology: pairs with
  C5-1.2/C5-2.3 threat notes; turns their caveat into a measured
  correction. Who cares: every downstream consumer of cross-target
  numbers; measurement-methodology reviewers.

- **C5-2.11 On-device quantized-KV energy.** Status: **candidate**;
  earliest phase: **PF**. Does quantized KV cache (`kv_bits` 8/4, mlx-lm)
  reduce gross request energy for long-context decode on-device, or only
  memory footprint? Ceiling: **L2, per-boundary, MLX-scoped; un-gated variant
  of C5-2.4 (no transfer leg, runnable on the D-073 fleet now)**. Forbidden
  upgrade: **No byte-saving-equals-energy-saving claim (inherits C5-2.4's
  ban); no cross-runtime generalization from MLX alone; no quality-neutrality
  claim without C-023-style output-equivalence evidence**. Attachments:
  C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.12 Bounded-window KV marginal-slope rider.** Status:
  **candidate**; earliest phase: **PF**. Does a bounded evicting window
  (`RotatingKVCache` via `max_kv_size`) flatten the marginal J/token slope
  over long generations versus an unbounded step-growing `KVCache`? Ceiling:
  **L2 in chunked windows only (RQ-KV-GROWTH discipline: token cadence
  outruns power sampling)**. Forbidden upgrade: **No per-token joule claims
  below the cadence/sampling floor; no output-equivalence assumption —
  eviction changes generations, so contrasts are work-matched, never
  output-matched**. This is an amendment under C5-1.2/RQ-KV-GROWTH, not an
  independent thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.13 Serialized prompt-cache crossover rider.** Status:
  **candidate**; earliest phase: **PF**. Is save+load+replay of a serialized
  prompt cache energy-cheaper than re-prefill at prompt length N on the same
  machine, and where is the crossover? Ceiling: **L2 same-machine,
  same-stack (promotes answered-L1 RQ-MLX-KV-REPLAY to an energy claim)**.
  Forbidden upgrade: **No cross-machine or cross-stack portability claim
  (RQ-MLX-KV-REPLAY's existing ban); no generalization beyond the measured
  prompt-length ladder**. This is an amendment under RQ-CACHE-PREFIX and
  RQ-MLX-KV-REPLAY, not an independent thesis. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.14 Q4 cache-policy coefficient rider.** Status: **candidate**;
  earliest phase: **PF**. Do KV-cache-policy contrasts move the fitted Q4
  coefficients in the predicted direction (marginal per-token term down
  under quantized KV, fixed term unchanged)? Ceiling: **L2; L3 only through
  Q4/AP-1's existing holdout machinery (D-070 clause 5)**. The candidate
  rider itself remains capped at L2. Forbidden upgrade: **No new-thesis
  framing — this is a Q4 stress test, not a KV-energy model; no
  coefficient-direction claim below P2-015 detection floors**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

## TIER 3 — requiring new acquisitions (hardware class + rough cost tier)

- **C5-3.1 Machine-to-machine variance / generalizability floor.** A
  second M-series unit (used M1/M2/M4, ~$500-1500) answers the
  examiner's sharpest structural attack: which Tier-1 findings replicate
  on a second box, and what is unit-to-unit variance relative to the
  detection floor? Also unlocks chassis-thermal comparisons (Air vs Pro
  fanless/fanned envelopes). This is the cheapest purchase that converts
  "on this M3 Max" claims into population claims.

- **C5-3.2 Battery-path energy and modeled-rail validation.** A USB-C PD
  power analyzer (~$100-300) measures DC input on battery-excluded runs
  and cross-checks powermetrics' modeled rails at a second physical
  boundary — a cheap partial answer to the modeled-vs-measured attack,
  complementary to the AC wall meter.

- **C5-3.3 Cross-ISA NPU/SoC comparison.** AMD Ryzen-AI mini-PC and/or
  Snapdragon-X laptop (~$800-2000 each): do the dark-silicon and
  active-param-scaling structures hold beyond Apple's stack? Requires
  one new telemetry adapter per platform (the adapter contract is the
  deliverable that makes this tractable).

  **2026-07-17 backend-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **PC**. Record kernel/backend build provenance
  (CUDA/Metal/HIP target, kernel library ids) in all bundles now so a
  post-capstone AMD/ROCm replication leg is comparable without re-running the
  NVIDIA/Mac corpus. Candidate-rider ceiling: **L1 feasibility**; the parent
  row's separate L4 replication posture is not an intake upgrade. Forbidden
  upgrade: **no NVIDIA-vs-AMD efficiency claim from single
  units or heterogeneous boundaries; no cross-ISA claim before a
  platform-specific adapter study**. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-3.4 Phone-class edge inference.** One flagship phone
  (~$800-1200) + llama.cpp/MLX-swift: the actual battery-constrained
  edge story. Honest note: telemetry access on phones is the hard part;
  a feasibility verdict (possibly `unsupported`) is itself the
  publishable first result, exactly like Hailo.

- **C5-3.5 Cross-lab replication (zero hardware, the credibility
  acquisition).** A second lab runs the frozen suite from published
  bundles + configs. Gates every public-facing application (leaderboard,
  standard, audit service); costs coordination, not money.

## Unexpected-applications shortlist (beyond papers)

Ranked by usefulness × lowest extra work; every public-facing one carries
the internal-first ladder from the examiner round.

1. **Prompt/template energy profiler** — product engineers measure the
   joule cost of system-prompt/RAG-template variants; ~3-8 person-days
   (prompt-matrix configs + diff report); rides per-request joules +
   phase attribution. Available now.
2. **Attach-a-bundle power-bug repro** — runtime maintainers receive
   "model got slow/hot" reports as reproducible bundles; ~5-10 days
   (issue template + doc); rides bundle completeness. Available now;
   mundane and high-leverage.
3. **CI energy-regression gates** for MLX/llama.cpp — nightly pinned-host
   run fails on mJ/token regressions; ~5-15 days; rides strict
   validation + config hashing. PRECONDITIONS (examiner): measured
   detection floor as the threshold unit, env snapshots (P2-009),
   baseline-refresh policy across OS updates.
4. **Vendor/press claim audit** — "efficient" claims answered with
   boundary-named measured bundles; ~5-10 days. Defensible as "on this
   boundary, this workload"; overclaims if framed as absolute device
   energy without wall calibration.
5. **Practitioner energy model cards / leaderboard** — joules/token with
   uncertainty next to quality scores; ~5-10 days internal. Ladder:
   internal table → published methodology → cross-lab public table
   (C5-3.5); public version is KILLED until then.
6. **OS/driver/runtime update forensics** — before/after bundles detect
   power-behavior regressions from macOS/MLX updates (DVFS residency
   makes it mechanistic); ~5-15 days; stronger with landed P2-009 rich telemetry.
7. **Teaching instrument** — a measurement-methodology lab course (idle
   subtraction, boundaries, uncertainty, negative results) with bundles
   as graded artifacts; ~5-12 days.
8. **Bundle contract as a standards contribution** — the run-bundle
   layout + boundary table + strict validator packaged as a proposed
   artifact format for edge-LLM energy (MLPerf-Power-adjacent); ~15-30
   days. Export the methodology; do not claim to BE the standard.

Deferred/killed applications: carbon LABELS (needs wall meter + grid
assumptions; see C5-2.9 for the surviving question), battery-runtime
estimates without system-level calibration, local-vs-cloud ROUTING as a
product (cloud side unmeasurable today).

## New questions 2026-09-16 (Astra exploration)

**Basis: Paper C already exists.** This is Ed's 2026-09-16 prospective
research premise: the instrument is validated, the `_v5` phase-energy
paper is published, and the entire Tier 1 mechanism bank is answered.
The questions below spend those answers on second-order predictions and
interventions. They do not reopen the shape grid, KV-growth curve, content
sentinel, session-composition study, variance study, or basic model ladder.
This premise is not a change to today's [coverage map](research_question_coverage-2026-09-04.md),
[claims status](../CLAIMS_STATUS.md), or [current paper](paper/draft-v2-skeleton.md).
`RQ-D-A01`–`RQ-D-A16` are bank-local proposal identifiers, not new canonical
registry rows or promoted campaigns. Each extension names its existing owner.

**Paper-C facts consumed below.** These labels identify the assumed published
answers, including their intervals and limits; no direction or numerical
coefficient is invented where the brief supplies none.

- **PC-F:** `_v5` establishes the admitted phase-allocation method, its
  labelled floors, and refusal rules (`RQ-METHOD-FLOOR`,
  `RQ-SHORT-PREFILL-RESOLVABILITY`, `RQ-ATTRIBUTION-DOMINANCE`).
- **PC-S:** the shape grid supplies fixed/prefill/decode coefficients and
  their validated domain (`Q4`, `RQ-SHAPE-ENERGY`, `C5-1.2`, `C5-1.3`).
- **PC-M:** the active-size contrasts, quantization decomposition, and
  memory-fit frontier are known (`C5-1.1`, `C5-1.10`, `C5-1.12`), without
  turning the old two-model observation into a scaling law.
- **PC-K:** context-associated decode costs and exact prefix/cache-policy
  economics are known (`RQ-KV-GROWTH`, `RQ-CACHE-PREFIX`).
- **PC-W:** fixed-shape content/category residuals, token-fertility effects,
  and natural-output-length effects are known (`RQ-CONTENT-SENTINEL`,
  `C5-W.1`, `C5-W.2`, `C5-I.3`). A measured null stays bounded to its domain.
- **PC-E:** session composition, order, recovery, and stochastic energy
  distributions are known (`RQ-SESSION-SHAPE`, `RQ-ORDER-POSITION`,
  `C5-1.5`, `RQ-ENERGY-VARIANCE`).
- **PC-Q:** the controlled-envelope energy/correct result and denominator
  guard are known (`C5-1.9`, AP-5); they confer no general capability claim.

**Concrete model shelf, checked against primary sources on 2026-09-16.**
The dense ladder is Qwen3-4B/8B/14B/[32B](https://huggingface.co/Qwen/Qwen3-32B)
plus [Llama-3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct),
using pinned 4-bit MLX conversions. Sparse points include
[Qwen3-30B-A3B](https://huggingface.co/Qwen/Qwen3-30B-A3B),
[DeepSeek-V2-Lite/Chat](https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite)
(16B total/2.4B active, MLA), and
[Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B)
(Gated DeltaNet/full-attention hybrid plus MoE). The latter's
[local smoke](run_reports/2026-07-07-flagship-qwen35-122b.md) already established
load/generation feasibility at about 68.9 GB peak; its historical energy
numbers remain barred from claim use. Qwen3-4B is only an approximate
active-size comparator for A3B; its architecture and training remain different.

The attention shelf adds Gemma-3-27B-IT (local sliding windows plus global
layers; [MLX implementation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/gemma3_text.py)),
[Kimi-Linear-48B-A3B-Instruct](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct)
(KDA/MLA hybrid), and
[Nemotron-H-8B-Base-8K](https://research.nvidia.com/labs/adlr/nemotronh/)
(Mamba-2/attention hybrid). Upstream MLX has
[Kimi Linear](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/kimi_linear.py),
[DeepSeek V2](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/deepseek_v2.py),
and [Nemotron-H](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/nemotron_h.py)
implementations. This is source-level candidacy, not an exercised JouleWise
support verdict. Pin conversion, runtime, cache representation, and actual
context/batch support before scheduling. KDA, Gated DeltaNet, and Mamba-2
are distinct mechanisms; none is a synonym for the others.

Weight-only arithmetic at four bits is `parameters / 2` bytes: 32B ≈ 16 GB,
70B ≈ 35 GB, 30B ≈ 15 GB, 48B ≈ 24 GB, 122B ≈ 61 GB, before scales,
unquantized tensors, caches, scratch, and the OS. These are plausible
128 GB-resident candidates at bounded shapes, not promises of every long
context fitting. Record actual peak and swap; never change wired-memory
limits to rescue a cell. Use one large model at a time unless co-residency
is the registered intervention. MLX is the Mac execution leg; existing
vLLM adapters do not establish a native Mac or live second-device result.
All proposed workloads here are text-only; disable vision processing and
record which non-text weights remain loaded.

**Common measurement and budget convention.** Gross request energy and
admitted long-phase allocations on `M3 Max / MLX / powermetrics SoC rails`
are primary. Follow the brief's approximately 1 s cadence, not the old
smokes' approximately 9 Hz. A phase needs at least three overlapping records
and every applicable duration/coverage gate; a short phase is unresolved.
The standing attribution scale is about 1 J. The source describes an effective
phase-contrast bar around 5 J after claim-side widening; use **6 J as a
conservative planning example**, not as a newly issued floor. Every actual
cell needs its own floor and claim interval. With `N` observed output tokens,
`1/N` J/token describes the attribution scale and `6/N` the example claim
bar: at N=1024, 0.98 and 5.86 mJ/token; at N=2048, 0.49 and 2.93; at
N=4096, 0.24 and 1.46. These are averages over measured windows, never
instantaneous token measurements. Summing separately bounded windows also
sums their uncertainty; concatenation does not erase internal phase edges.
For two contrast terms use a conservative 12 J planning bar unless their
joint timing construction justifies less. No `1/sqrt(n)` erasure of shared
attribution error. Sub-floor is `not resolvable`, not equivalence.

Budgets below count calibrated collection **windows**, each provisionally
60–120 minutes including brackets, admission, and recovery. `F` = new-cell
floor/null/observability window; `C` = frozen paired/factorial contrasts;
`H` = held-out validation window. Each C/H cell needs at least five independent
whole-suite bundles, with interleaving and day/order blocks; items and tokens
are not independent n. Fix n before outcomes, informed by PC-E. An F window
may contain several cells only if the frozen manifest and time budget fit.
Desk implementation and support gates are additional calendar time, not
hidden inside a window estimate. Keep the north star's 3× projected-floor
screen and reserve 20–25% of the week for refusals. At 4–5 windows/day,
one week offers 28–35 windows, not enough for this entire portfolio.

The [north star](strategy/HORIZONS.md) supplies the mechanism agenda.
As the [fence audit](strategy/2026-08-06-impressiveness-roadmap.md) explains,
D-041 owns benchmark interop and correctness quarantine; D-070/D-075 and
the AXI contracts own mechanism observability and attribution limits.
These candidates do not amend either fence. Every proposed runtime change,
scored-source extension, and second-device path needs its own later admission.

- **RQ-D-A01 Resident capacity versus active work:** Does increasing
  resident-but-unread weight storage change the energy predicted from
  Paper C's active-work coefficients before memory pressure begins? Ceiling L2.

  **Status/Paper C:** Extension of `C5-1.1` and `C5-1.10`; consumes PC-M
  and PC-S. **Mechanism:** residency consumes capacity but need not create
  repeated weight reads; crossing a pressure boundary can cause compression,
  migration, or faults. This separates the two physical interventions.
  **Design:** run Qwen3-32B-4bit at 2048/2048 with 0/24/48 GB of separately
  materialized, retained, unread weight buffers; load/touch outside measurement
  and confirm residency/no swap. Repeat a smaller two-level intervention on
  the 122B MoE within its measured headroom. Use the 4B/A3B near-active pair,
  32B/122B, and 70B only as external prediction checks, not causal matches.
  Hold executed graph, tokens, cache, and quantization fixed within each pair.
  **Claim/budget:** request or long decode Δ >6 J gives >2.93 mJ/token over
  2048 tokens; resident-idle and pressure results stay separate. 10 windows
  = 2F+6C+2H (2–3 days). **Difficulty:** none. **Risk:** a lazy or compressed
  buffer is not resident RAM; powermetrics cannot isolate DRAM-refresh joules.
  A null bounds this residency intervention, not all total-parameter effects.

- **RQ-D-A02 Function-preserving expert locality:** Can changing only
  expert storage and dispatch order explain MoE energy residuals left by
  Paper C's active-parameter result? Ceiling L2 on the named implementation.

  **Status/Paper C:** NEW; follows `C5-1.1`, PC-M and PC-W.
  **Mechanism:** identical expert arithmetic can require different gathers,
  contiguous reads, and launches. Relabel experts with the inverse router
  mapping, or sort/unsort dispatched token-expert pairs, preserving function.
  **Design:** Qwen3-30B-A3B-4bit first, Qwen3.5-122B-A10B-4bit replication;
  frozen code/JSON/reasoning-shaped token paths, 2048/2048, batch 1 and 4.
  Compare native versus locality-ordered dispatch at identical routed IDs,
  probabilities, quantized weights, output IDs, and numerical tolerance.
  Instrument actual expert IDs/dispatch counts; a configuration label is
  insufficient. Reordering support is proposed runtime work, not landed.
  **Claim/budget:** >6 J/decode window = >2.93 mJ/output-token at batch 1;
  for batch 4, >6/(4×2048)=0.73 mJ/committed token across the group.
  12 windows = 2F+8C+2H (3 days). **Difficulty:** none. **Risk:** added sorting
  and tracing can dominate; count their energy and validate trace perturbation.
  Claim dispatch-layout effects, never an expert's individual joules.

- **RQ-D-A03 The expert-union batching penalty:** Does the union of
  experts touched by a batch predict whether batching reverses Paper C's
  single-request dense-versus-sparse ordering? Ceiling L2; prospective Q4
  holdouts only.

  **Status/Paper C:** Extension of `C5-1.1`, `C5-2.2`; consumes PC-M,
  PC-W and PC-E. **Mechanism:** overlapping routes permit weight reuse;
  disjoint routes enlarge the batch working set despite equal active
  parameters per token. **Design:** Qwen3-30B-A3B and 122B MoE, with Qwen3-32B
  dense control; identical frozen request multiset partitioned into batches
  of 1/2/4 by a precomputed routing trace, either high or low route overlap.
  Match shape and position, rotate partitions, preserve each request's output
  and clear prefix caches. Train an expert-byte-union predictor on two shape
  cells; reserve a third cell and an unseen partition for validation.
  **Claim/budget:** compare high-minus-low grouping benefits across batch
  sizes; conservative interaction bar 12 J/group = 1.46 mJ/token for
  4×2048 outputs. 14 windows = 3F+8C+3H (3–4 days). **Difficulty:** none.
  **Risk:** grouping changes padding or cache reuse unless controlled; unique
  expert count alone misses repeated fetches. No general MoE scaling law.

- **RQ-D-A04 A held-out byte-and-work energy model:** Can a model of
  weight/KV work and phase duration predict large-model energy beyond Paper C's
  validated additive-shape domain? Ceiling L3 only through Q4/AP-1.

  **Status/Paper C:** Extension of `Q4`, `C5-1.1`, `C-023-COEFF-TRANSPORT`;
  consumes PC-S, PC-M and PC-K. **Mechanism:** weight reuse per batch and
  growing state reads alter arithmetic intensity; compute and memory stalls
  determine duration, which interacts with gross power. **Design:** calibrate
  one predeclared traffic correction on the Qwen3-4B/8B/14B/32B family at
  4-bit, context 2K/8K and batch 1/4; hold out 4K context, batch 2, and all
  32B outcomes in the model-transfer leg. Test Llama-70B and A3B/122B as
  explicit out-of-family challenges, not added fit covariates. Derive tensor
  bytes from runtime shapes/quant metadata; distinguish compulsory-byte lower
  bounds from measured bandwidth. Compare against frozen Paper-C predictions.
  Predict duration from declared shapes and operations; held-out measured
  duration, power, and energy cannot enter the predictor or tune its fit.
  **Claim/budget:** N=4096 makes a 6 J prediction residual 1.46 mJ/token;
  require joint prediction-plus-measurement intervals, not just a small RMSE.
  16 windows = 3F+9C+4H (4 days). **Difficulty:** none. **Risk:** traffic is
  not directly observed DRAM energy, and family changes confound transfer.
  No active+total+KV multivariate fit to a handful of model points.

- **RQ-D-A05 Attention-state crossover at a fixed problem profile:**
  Do known context costs predict where the same retrieval-and-answer profile
  changes energy ordering across GQA, MLA, sliding-window, and hybrid models?
  Ceiling L2 named-pair characterization, not architecture causality.

  **Status/Paper C:** Extension of `RQ-AXI-HYBRID-PAIR`, `RQ-KV-GROWTH`,
  `Q5`; consumes PC-K, PC-S and PC-W. **Mechanism:** GQA state grows with
  context; MLA changes its representation; local attention bounds some
  histories; KDA/SSM stores recurrent state while remaining global layers
  still grow. **Design:** Qwen3-32B, DeepSeek-V2-Lite-Chat, Gemma-3-27B-IT,
  Kimi-Linear-48B-A3B, plus Nemotron-H-8B within its 8K limit; all 4-bit,
  batch 1. Use the same frozen retrieval/summary texts and answer policy at
  2K/8K, with 4K held out; a separate tokenizer-specific fixed-shape leg
  audits fertility. Observe real cache layouts: an MLA-labelled model that
  materializes expanded K/V is a different condition. Freeze the crossover
  prediction before held-out runs. **Claim/budget:** >6 J/request or admitted
  decode = >5.86 mJ/token over 1024 outputs. 18 windows = 5F+9C+4H
  (4–5 days). **Difficulty:** none; retrieval distance is workload geometry.
  **Risk:** training, base/instruct status, MoE, and quality differ; report
  pairs separately. This design cannot isolate an architecture-class effect.

- **RQ-D-A06 Recurrent-state prefill scheduling:** Does changing the
  prefill chunk schedule of a hybrid model move the predicted prefill/decode
  crossover without changing its recurrence or answers? Ceiling L2.

  **Status/Paper C:** NEW; extends the design space around
  `RQ-AXI-HYBRID-PAIR`; consumes PC-S and PC-K. **Mechanism:** chunking trades
  parallel matrix work, recurrent-state handoffs, scratch traffic, and kernel
  launches while preserving the same mathematical sequence computation.
  **Design:** Kimi-Linear-48B-A3B and Qwen3.5-122B-A10B at 4-bit;
  Qwen3-32B GQA control. At 8K/32K prompts and 1024 outputs compare pinned
  256/1024/4096-token prefill chunks, keeping attention masks, position IDs,
  cache policy, weights, and precision fixed. Validate state/output identity;
  predict 16K held-out performance. A chunk setting is not a KDA on/off switch.
  **Claim/budget:** phase Δ >6 J; a prefill/decode compensation comparison
  needs the joint bound, conservatively 12 J = 11.72 mJ per 1024 outputs.
  12 windows = 3F+6C+3H (3 days). **Difficulty:** none. **Risk:** numerical
  accumulation or cache rebuilding may change outputs; report a changed
  algorithm if equivalence fails. No joules per recurrent update.

- **RQ-D-A07 Weight compression × state compression:** Are weight
  quantization and KV quantization energy savings additive, or does one
  remove the bottleneck that made the other useful? Ceiling L2.

  **Status/Paper C:** Extension of `C5-2.11`, `C5-2.14`, `C5-1.12`;
  consumes PC-M and PC-K. **Mechanism:** both compete to reduce memory
  traffic, but unpacking and cache-update compute can become dominant.
  **Design:** Qwen3-32B at weight 4/8-bit × KV 4/8-bit, 8K/32K contexts,
  batch 1, output 2048; Llama-70B-4bit validates the predicted long-context
  branch without promising its 8-bit scratch headroom. Use one source
  revision per model, fixed replay paths for work matching, and separate
  natural-generation output/quality checks. Freeze the difference-of-differences
  before collection. **Claim/budget:** interaction >12 J = >5.86 mJ/token
  at 2048; individual gains require their own >6 J gates. 10 windows =
  2F+6C+2H (2–3 days). **Difficulty:** none. **Risk:** quantized paths need
  not produce identical answers, and some cache classes reject quantization.
  Byte savings alone are not efficiency or quality-neutrality evidence.

- **RQ-D-A08 Acceptance distribution versus acceptance mean:** At the
  same aggregate acceptance rate, do speculative decoding's burst pattern
  and context length predict a different energy break-even? Ceiling L2.

  **Status/Paper C:** Extension of `C5-2.5b/c`, not another on/off pilot;
  consumes PC-S, PC-K, PC-E and PC-W. **Mechanism:** verification width,
  rollback, and repeated target-weight reads depend on the distribution of
  accepted prefixes, not just accepted/proposed totals. **Design:** fixed
  Qwen3-32B-4bit target with tokenizer-compatible
  [Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) and 4B draft
  candidates, after support/identity gates; off versus proposal caps 2/4/8,
  contexts 2K/8K, 2048 committed outputs. Train on the runtime-observed
  proposed/accepted/committed histograms of one frozen roster; predict a
  held-out roster with matched mean acceptance but different burst spread.
  Select that roster from disjoint non-energy traces before the energy plan
  freezes; never select it by the resulting energy difference.
  Natural differences yield conditional prediction, not randomized acceptance
  causality. **Claim/budget:** >6 J/request = >2.93 mJ/committed token;
  never divide the on/off headline by accepted-draft tokens alone.
  12 windows = 2F+7C+3H (3 days). **Difficulty:** none. **Risk:** current
  AXI-SC unsupported verdict persists until a new exercised counter-complete
  path exists; drafter and lookup work must remain in the numerator.

- **RQ-D-A09 MTP's state-sharing dividend:** Does native multi-token
  prediction change the context-dependent verification cost predicted for
  an external drafter on the same target? Ceiling L2, software-gated.

  **Status/Paper C:** Extension of `C5-2.5c`; consumes PC-S, PC-K and PC-M.
  **Mechanism:** native heads may reuse target representations whereas a
  separate drafter needs its own weights/state; both still pay verification
  and rejected-work costs. **Design:** Qwen3.5-122B-A10B-4bit target, native
  heads on/off, then a separately qualified
  [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)-4bit draft candidate with
  verified tokenizer compatibility; context 2K/8K, 2048 committed tokens,
  held-out 4K.
  Keep target bytes and verified outputs fixed; record actual head execution,
  proposals, acceptance, state copies, and rollback. Fit separate mechanism
  families, never pool MTP and external-draft rounds.
  **Claim/budget:** contrast >6 J = >2.93 mJ/token; difference between
  context-dependent benefits >12 J = >5.86 mJ/token. 12 windows = 3F+6C+3H
  (3 days), **zero until support gates pass**. **Difficulty:** none.
  **Risk:** the [official model card](https://huggingface.co/Qwen/Qwen3.5-122B-A10B)
  documents MTP serving elsewhere, but [MLX source](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/models/qwen3_5.py)
  strips MTP weights. This is a runtime-development candidate, not a currently
  runnable Mac claim; a vLLM leg needs suitable second-device memory and gates.

- **RQ-D-A10 Difficulty-conditioned crossover between resident models:**
  Does Paper C's controlled energy/correct ordering predict which large
  resident model is cheapest per correct answer in unseen published
  difficulty strata at a fixed token envelope? Ceiling conditional L2.

  **Status/Paper C:** Extension of `C5-1.9` and `C5-I.2`; consumes PC-Q,
  PC-W and PC-M. **Mechanism:** at a matched attempt envelope, energy/correct
  is attempt energy divided by empirical success probability; an ordering
  can reverse through that denominator without extra arithmetic per attempt.
  **Design:** Qwen3-32B, Llama-70B, Qwen3-30B-A3B and 122B MoE at 4-bit;
  freeze a licensed MATH subset, balanced by source subject and published
  level. Use within-tokenizer 2048/2048 envelopes, no question truncation,
  a fixed answer-extraction policy, and reported padding/EOS effects. Keep
  the same semantic item panel across models; reserve items and a level band
  for prediction. External scoring is hashed, deterministic, and quarantined.
  **Claim/budget:** if 32 attempts yield 16 correct, a 6 J aggregate energy
  difference contributes 6/16=0.375 J/correct; with four correct it contributes
  1.5 J/correct. These are energy-only sensitivities, not ratio thresholds:
  compose correctness uncertainty and AP-5's binomial guard; zero or weak
  denominators are not estimable. 16 windows = 4F+8C+4H (4 days).
  **Difficulty:** original MATH Levels 1–5, `{axis,value,scale,label,source}`
  preserved from the [dataset paper](https://arxiv.org/html/2103.03874v2),
  never token length or this model's score. **Risk:** contamination and forced
  answers. Extending AP-5 to this source requires a prospective policy ruling;
  D-041 alone licenses only energy beside external scores, not this ratio.

- **RQ-D-A11 Difficulty-conditioned execution residuals:** After applying
  Paper C's length and content corrections, can routing or acceptance traces
  predict residual energy on unseen published-difficulty strata? Ceiling L2.

  **Status/Paper C:** Extension of `C5-I.2`, `RQ-ENERGY-VARIANCE`;
  consumes PC-W, PC-E and PC-Q. **Mechanism:** dense fixed-shape inference
  follows nearly the same graph, whereas changed expert access or speculative
  rejection changes executed work; the source's difficulty label does no
  physical work itself. **Design:** Qwen3-32B dense control, Qwen3-30B-A3B
  and 122B MoE; frozen MATH levels/items, 2048/2048 per-tokenizer envelope,
  fixed seeds and matched stop policy. Capture paths once, then replay the
  identical paths under native and function-preserving grouped dispatch
  from A02. Predict held-out-level residuals from observed routes; an optional
  A08-supported leg adds acceptance traces. Hold score use to annotation.
  **Claim/budget:** level-block residual >6 J over 8×2048=16384 outputs is
  >0.37 mJ/token only if the whole-block bound is 6 J; eight separately
  bounded 6 J items instead imply 48/16384=2.93 mJ/token. 12 windows =
  3F+6C+3H (3 days). **Difficulty:** MATH's published Levels 1–5, as A10.
  **Risk:** observational label mediation is not causal difficulty evidence;
  only the dispatch intervention identifies an execution-policy effect.

- **RQ-D-A12 Context × batch phase inversion:** Can Paper C's separate
  context and phase costs predict where batching reverses the prefill/decode
  energy split for large resident dense and sparse models? Ceiling L2;
  L3 prediction only through a prospective Q4/AP-1 extension.

  **Status/Paper C:** Extension of `C5-2.2`, `Q4`; consumes PC-S, PC-K
  and PC-M. **Mechanism:** batching amortizes weight reads but enlarges
  concurrent KV/state and changes matrix utilization; the dominant resource
  can therefore change differently in prefill and decode. **Design:**
  Qwen3-32B, Llama-70B, Qwen3-30B-A3B and 122B MoE, 4-bit; context
  2K/8K/16K × static batch 1/2/4, 1024 outputs/request. Fix request multiset,
  cache coldness, output policy, and prefill chunking; train on the matrix
  edges, hold out interior combinations. Freeze latency constraints and
  retain memory-fit failures. **Claim/budget:** prefill and decode each
  need their own phase gate; a context-by-batch interaction >12 J/group
  equals >3 J/request on the group-average basis or >2.93 mJ/output-token
  for batch 4×1024: 12/4=3 J/request and 12/4096=2.93 mJ/token.
  16 windows = 4F+8C+4H (4 days). **Difficulty:** none. **Risk:** static
  batching is not continuous serving; unequal completion lengths create
  a different workload. No allocation of batch energy to individual requests.

- **RQ-D-A13 Prefix reuse × verification-state reuse:** Are the energy
  benefits of prefix caching and speculative decoding composable once draft
  and target state have to be initialized together? Ceiling L2.

  **Status/Paper C:** Extension of `RQ-CACHE-PREFIX`, `C5-2.5`,
  `RQ-SESSION-SHAPE`; consumes PC-K and PC-E. **Mechanism:** target-cache
  reuse skips known prefill work, but a drafter may rebuild its prefix or
  transfer/duplicate state; that changes the acceleration's fixed cost.
  **Design:** A08's Qwen3-32B/0.6B pair with full observability; prefix cache
  cold/warm × speculation off/on, shared prefix 2K/8K, identical 512-token
  suffix and 2048 committed outputs. Pin both caches' identities separately;
  include draft preparation inside the end-to-end measured service interval.
  Train at 1/4/8 prefix reuses and predict held-out reuse count 2 from
  Paper-C coefficients plus one measured draft-initialization term.
  **Claim/budget:** interaction
  >12 J/request = >5.86 mJ/output-token, with request-total evidence primary
  if a warm prefill is unresolved. 10 windows = 2F+6C+2H (2–3 days).
  **Difficulty:** none. **Risk:** a target-warm/draft-cold comparison can
  silently change cache ecology; hybrid recurrent-state rollback may not be
  supported, so the first experiment uses the dense target.

- **RQ-D-A14 Energy compensation that a request total hides:** Can two
  execution policies have an unresolved total-energy difference yet a
  resolvable, predictively useful exchange between prefill and decode? Ceiling L2.

  **Status/Paper C:** NEW synthesis of `Q4` and `RQ-METHOD-FLOOR`;
  consumes PC-F and PC-S. **Mechanism:** cache representation or prefill
  scheduling may spend extra work once to reduce later reads; a real phase
  exchange must survive the opposite-signed reassignment caused by moving
  a shared phase boundary. **Design:** take one predeclared A06 chunk pair
  or A07 cache pair on Qwen3-32B, 16K prompt and outputs 512/2048/4096.
  Predict the total-energy break-even output length from long-phase contrasts;
  reserve one output length. Propagate the *same* admissible boundary through
  both phases and the conserved request total, rather than treating phase
  errors as independent. **Claim/budget:** illustrative +20 J prefill and
  −20 J decode clears a 6 J bar for each phase, but 0 J total is unresolved;
  −20/2048=−9.77 mJ/token is a window-average decode change. A 1 J exchange
  cannot be attributed. 8 windows = 2F+4C+2H (2 days).
  **Difficulty:** none. **Risk:** this measures phase-policy consequences,
  not attention/FFN module shares; timing covariance can manufacture apparent
  compensation. This is the strongest use of the instrument's labelled floor.

- **RQ-D-A15 Transport the mechanism, not the fitted joules:** Does a
  bandwidth/compute-normalized model trained on this Mac predict held-out
  shapes on a second device after only a small local calibration? Ceiling
  L3 per target; L4 only for an independently replicated scoped finding.

  **Status/Paper C:** Extension of `C5-3.1`, `C5-2.7`, `Q4`; consumes
  PC-S, PC-M and PC-K. **Mechanism:** a device change perturbs effective
  bandwidth and compute throughput, offering an external falsifier for the
  byte/work explanation rather than merely another ranking table.
  **Design:** prefer a second 128 GB M-series Mac for the same 32B/70B/122B
  artifacts and pinned MLX source; calibrate two registered shapes, freeze
  the transport rule, then test six unseen context/batch combinations.
  A CUDA/vLLM alternative starts with Qwen3-4B/8B models that actually fit;
  kernel/runtime differences make it a separate stack-transport study, not
  a pure hardware intervention. **Claim/budget:** each target mints its own
  bound; if both illustrative bars are 6 J, a cross-target residual contrast
  needs a conservative 12 J = 2.93 mJ/token over 4096 outputs. 16 windows
  across devices = 4F+6C+6H (4 days at the combined 4–5/day budget).
  **Difficulty:** none. **Risk:** two different chips are not unit-to-unit
  population sampling; SoC and board joules cannot be ranked without boundary
  calibration. A second device supplies a mechanism perturbation, not truth
  about every device in its class.

- **RQ-D-A16 Architecture-dependent state-transfer placement:** Does
  replacing full-history KV with latent or recurrent state move the
  energy-optimal prefill/decode placement predicted from Paper C's local costs?
  Ceiling L2 measured placements; L3 only after held-out split validation.

  **Status/Paper C:** Extension of `C5-2.3`, `C5-2.8`, `Q1`;
  consumes PC-S, PC-K and PC-E. **Mechanism:** state representation changes
  serialization, link bytes, and reconstruction, potentially shifting a
  compute advantage's break-even; hybrid global layers retain growing state.
  **Design:** two memory-sufficient Macs, same MLX build and 4-bit weights;
  Qwen3-32B GQA, DeepSeek-V2-Lite MLA, Kimi-Linear-48B-A3B hybrid.
  Compare monolithic and offline split at 8K/32K prompts, output 2048;
  predict held-out 16K placement at measured 1/2.5GbE rates. Prove full
  cache/state export, import, and greedy identity first; raw transfer alone
  is not split inference. Account both endpoints' idle/resident intervals.
  **Claim/budget:** if each endpoint's transfer interval carries a 6 J bar,
  the transfer sum alone carries 12 J = 5.86 mJ/output-token; a difference
  from an independently bounded 6 J monolithic reference can require 18 J
  = 8.79 mJ/token, plus any other composed terms. 18 windows across devices
  = 6F+8C+4H (4–5 days), after portability and cross-device timing gates.
  **Difficulty:** none; same semantic task and separate token-shape controls.
  **Risk:** incompatible state formats or below-floor network stages can
  kill the placement claim; no module-energy inference from smaller payloads.

**What one week of windows buys (ranked; alternatives, not additive promises):**

1. **A04 + A14:** 16+8=24 windows, 6 reserve in a 30-window week; one held-out prediction story plus its phase-compensation explanation, if both runtime paths pass desk gates.
2. **A02 + A03:** 12+14=26 windows, 7 reserve in a 33-window week; a routing-layout intervention plus an expert-union prediction, if audited dispatch exists first.
3. **A10 + A11:** 16+12=28 windows, 7 reserve in a 35-window week; a difficulty-transfer paper only after the AP-5/source ruling; otherwise retain energy and external scores separately.
4. **A08 + A13:** 12+10=22 windows, 6 reserve in a 28-window week; speculative burst and prefix-state interactions after observability support; A09 waits for executable MTP.
5. **A15 or A16:** 16 or 18 windows plus at least 5 reserve; a second device buys coefficient transport or state-placement falsification, not both full studies or automatic generalization.

## New questions 2026-09-16 (Fable exploration)

**Basis: Paper C already exists** — the same premise as the Astra section
above. `RQ-NEXT-*` are bank-local proposal identifiers, not registry rows.
Sizes are 4-bit MLX unless stated. **NEEDS-WEB** marks a runtime-support fact
the seat could not verify; it is a prerequisite, never an assumption. Window
counts are the seat's, sized at ≈3.5 h of capture per window (≈80 members at
≤8B, ≈40 at the 100B class); the research plan rescales them.

**Paper-C facts consumed (PC-n):** PC-1 labelled attribution floor ≈1 J per
phase, effective contrast bar ≈5 J, per-token resolution = bar/N. PC-2 timing
widening dominates scatter (R≥2): longer windows beat more repetitions. PC-3
coefficients `E = fixed + a·p + b·d` (p prompt tokens, d decode tokens) fitted
per model/quant with held-out shapes; session composition and prefix crossover
resolved. PC-4 decode is bandwidth-bound at near-flat power (≈23–28 W from
1.5B to 122B-A10B), so decode energy differences are decode *time*. PC-5
chunked KV-growth slope and context-nonlinearity onset known per model. PC-6
token-shape sufficiency (category/content collapse to token counts at fixed
shape) resolved. PC-7 sampling energy variance decomposed into length vs
residual. PC-8 prefill resolvable only at ≥3 records (~0.34 s); shorter
prefill prints `not resolvable`. PC-9 quantization split (watts vs time),
keep-warm break-even, 128 GB failure frontier. Planning levels: 512-token
decode ≈47 J (1.5B), ≈192 J (7B), ≈304 J (122B-A10B); bar 5 J ⇒ ≈10 mJ/token
over 512 tokens, ≈2.4 mJ/token over 2048.

- **RQ-NEXT-BYTES-LAW Bytes-touched-per-token decode law:** Across dense and
  MoE at fixed quant, is decode energy/token one linear function of bytes read
  per token (active weights + KV), with resident-but-inactive bytes costing
  nothing? Ceiling L2/L3 via a predeclared one-covariate fit plus a held-out
  model. **Extension** of `C5-1.1` (lifts its 4–6-point cap).
  **Mechanism:** PC-4 ⇒ E/token = P·bytes/BW_eff; resident size enters only if
  effective bandwidth drops (expert scatter, paging). **Design:** Qwen3
  1.7B/4B/8B/14B/32B dense, Qwen3-30B-A3B, Qwen3.5-122B-A10B,
  Qwen3-Next-80B-A3B; p=256, d=2048; 14B held out. 10% of 47 J ≈ bar at d=512;
  at d=2048 resolution ≈1.3%. Windows: 3. **Difficulty:** none. **Risk:** quant
  group-size drift across sizes; per-prompt expert-load imbalance (record
  router statistics). Qwen3-Next-80B-A3B runtime support: NEEDS-WEB.

- **RQ-NEXT-TOPK-KNOB Router top-k as an active-bytes dial:** Within one MoE
  artifact, does overriding top-k (4/8/16 on Qwen3-30B-A3B) move decode
  energy/token in proportion to active bytes with resident bytes fixed? Ceiling
  L2, work-matched never output-matched. **NEW.** **Mechanism:** identical
  weights and KV; only experts loaded per token vary — the cleanest
  active-vs-resident isolation. **Design:** k∈{4,8,16}, p=256, d=1024, n=10;
  predicted ≈+50 J per doubling ≫ 5 J. Windows: 1. **Difficulty:** none.
  **Risk:** top-k override surface in MLX (NEEDS-WEB); shared-expert term
  fixed; quality claims forbidden.

- **RQ-NEXT-MIXER-3B Attention mixer at matched ~3B active:** At one problem
  profile, do MLA (DeepSeek-V2-Lite 16B-A2.4B), GQA (Qwen3-30B-A3B),
  Gated-DeltaNet hybrid (Qwen3-Next-80B-A3B) and KDA hybrid (Kimi-Linear-48B-A3B)
  differ in decode slope vs position and prefill scaling with context? Ceiling
  L2 named quadruplet, no class generalization. **Extension** of
  `RQ-AXI-HYBRID-PAIR`; the D-041 KDA arm. **Mechanism:** GQA KV read grows
  linearly with context; MLA compresses it; delta/linear state is constant —
  the slope IS the mixer signature (PC-5). **Design:** p∈{512, 8K, 32K}, d=512,
  byte-matched roster per tokenizer; slopes normalized to each model's p=512
  level. 32K KV read ≈ weight bytes for GQA ⇒ tens of J over 512 tokens;
  hybrids ≈0. Windows: 3. **Difficulty:** none. **Risk:** MLX support for
  Kimi-Linear and DeepSeek-V2 (NEEDS-WEB; the Astra section found upstream
  source files — source-level candidacy, not exercised support); totals differ
  across models — pairs with BYTES-LAW.

- **RQ-NEXT-MIXER-120B 128 GB-class mixer triplet:** Do GLM-4.5-Air (full
  GQA, 106B-A12B), gpt-oss-120b (alternating sliding-window 128, 5.1B active,
  MXFP4) and Qwen3.5-122B-A10B (hybrid — verify) differ in prefill
  energy/prompt-token at 16K–128K and in decode slope? Ceiling L2.
  **Extension** of `C5-1.2` + `RQ-AXI-HYBRID-PAIR`. **Mechanism:** a sliding
  window caps KV read; prefill is quadratic for full attention, linear for
  banded/linear layers. **Design:** p∈{2K,16K,64K,128K}, d=512, n=8; frontier
  recorded (PC-9). 128K prefill ≈ minutes at ≈40 W ⇒ kJ ≫ bar. Windows: 4.
  **Difficulty:** none. **Risk:** quant formats differ — within-model slopes
  only; GLM-4.5-Air and gpt-oss-120b MLX support: NEEDS-WEB.

- **RQ-NEXT-SPEC-SURFACE Speculative-decoding break-even surface from
  coefficients:** Can speculation-on energy be predicted as target-verify
  steps + drafter steps from the two models' PC-3 coefficients, and where is
  break-even acceptance for 8B/32B/70B targets with 0.6B/1.7B drafters? Ceiling
  L2/L3 (predicted vs measured, held-out pair). **Extension** of `C5-2.5c`.
  **Mechanism:** PC-4 ⇒ a batched verify step costs ≈ one decode step in bytes;
  break-even acceptance ≈ f(bytes_draft/bytes_target). **Design:** greedy
  (output-identical, so `C-023-OUTPUT-IDENTITY` holds by construction), d=1024,
  n=10; Llama-3.3-70B ≈40 GB, ≈10 tok/s ⇒ ≈1.5 kJ/512 tokens, 20% effects
  ≈300 J. Windows: 3. **Difficulty:** none. **Risk:** observed-acceptance
  accounting; the AXI-SC speculative path was `unsupported` in July — a
  counter-complete MLX path is a prerequisite (NEEDS-WEB).

- **RQ-NEXT-MTP Native multi-token prediction vs external draft:** At output
  identity, joules per committed token for native MTP heads (Qwen3-Next /
  Qwen3.5) vs a draft model vs baseline? Ceiling L2, separate family
  `FAM-AXI-SPEC-NATIVE-MTP`. **Extension** of the `C5-2.5c` MTP arm.
  Contingent on an MLX MTP surface (NEEDS-WEB; the Astra section reports the
  MLX source strips MTP weights). Windows: 1 if supported. **Difficulty:** none.

- **RQ-NEXT-KVQ-SURFACE KV quantization × context surface:** Does
  kv_bits∈{16,8,4} save energy equal to (KV-byte saving × PC-5 slope) minus a
  fixed dequantization term, on Qwen3-32B and Qwen3.5-122B at 2K/16K/64K?
  Ceiling L2, no quality-neutrality without a divergence report. **Extension**
  of `C5-2.11`. **Design:** 32B fp16 KV ≈262 KB/token ⇒ 17 GB per step at 64K
  ≈ weight bytes; halving ⇒ ≈25% ≈100 J over 512 tokens; the net sign flips at
  short context. Windows: 3. **Difficulty:** none. **Risk:** 64K prefill on
  122B near the frontier; quantized-cache support per model class (NEEDS-WEB).

- **RQ-NEXT-PHASE-CROSSOVER The prefill/decode crossover length p\*:** For
  each model, at what prompt length does prefill energy equal 512-token decode
  energy, and is p\*/d constant within a family (a device roofline signature)?
  Ceiling L2/L3 (predict p\* for a held-out model). **NEW**; stands on PC-3,
  PC-4, PC-8. **Mechanism:** prefill is compute-bound (FLOPs ∝ active·p),
  decode bandwidth-bound; their per-token ratio is the machine's FLOP/byte
  ratio, model-invariant at fixed quant. **Design:** 4 models ×
  p∈{512,1K,2K,4K,8K}, n=10; 8B at 4K ≈200–250 J per phase. Windows: 2.
  **Difficulty:** none. **Risk:** prefill_step_size confound (next row).

- **RQ-NEXT-PREFILL-CHUNK Prefill chunk size as an energy knob:** Does prefill
  energy/prompt-token fall with chunk size and saturate where GPU utilization
  saturates? Ceiling L2. **NEW**; only a labelled prefill floor (PC-1, PC-8)
  makes this prefill-only effect claimable. **Design:**
  prefill_step_size∈{256,512,2048,8192}, p=8K, 8B and 32B, n=10; ≈100 J
  prefill, 10% clears. Windows: <1. **Difficulty:** none.

- **RQ-NEXT-BATCH-KNEE Static-batch decode knee:** Does decode energy/token
  fall as 1/B until B×KV bytes ≈ weight bytes (predicted from PC-5), while
  prefill energy/token stays flat? Ceiling L2. **Extension** of the `C5-2.2`
  Mac leg (AXI-SB `supported`). **Design:** B∈{1,2,4,8,16}, 8B and 30B-A3B,
  p=d=512; per-sequence 200 J → ≈40 J at B=8. Windows: 2. **Difficulty:** none.

- **RQ-NEXT-ROUTING×BATCH MoE routing concentration under batching:** At B>1,
  do tokens routed to shared experts amortize weight reads so that per-request
  energy tracks router concentration, with a predicted null at B=1 (expert ≫
  system-level cache, no reuse)? Ceiling L2. **Extension** of D-070 MOE×BATCH.
  **Design:** Qwen3-30B-A3B, B∈{1,4,16}, rosters engineered for concentrated vs
  dispersed routing, router statistics logged. Windows: 2. **Difficulty:**
  none. **Risk:** MLX router hook (desk implementation prerequisite).

- **RQ-NEXT-EPCA-LEVELS Energy per correct answer vs published difficulty:**
  At fixed shape with natural EOS under a cap, does energy per correct answer
  rise across MATH levels 1–5, and is the rise fully explained by emitted-token
  count (PC-6/PC-7)? Ceiling L2, correctness quarantined, never "difficulty
  causes energy". **Extension** of `C5-1.9`/`C5-I.2`. **Design:** Qwen3-8B,
  32B, 30B-A3B; thinking off/on as arms; 32 items/level. Level-window energy ≈
  hundreds of J ≫ bar; the binomial guard (±17% at 32 items) dominates.
  Windows: 3. **Difficulty:** MATH per-item level, `{axis,value,scale,label,
  source}` preserved from the dataset paper. **Risk:** contamination
  (shape-only claims), cap hits under thinking; extending AP-5 to MATH needs a
  prospective policy ruling (see `RQ-D-A10`).

- **RQ-NEXT-EPCA-MECHANISM Energy per correct answer across mechanisms at one
  profile:** On the same MATH strata, dense 32B vs MoE 30B-A3B vs hybrid
  80B-A3B vs 122B-A10B at a matched accuracy band — which mechanism buys a
  correct answer cheapest, and is the ordering level-stable? Ceiling L2 named
  set. **Extension** of `C5-1.9`. Windows: 3 (shares EPCA-LEVELS rosters).
  **Difficulty:** as EPCA-LEVELS. **Risk:** predeclare accuracy bands, never
  post hoc.

- **RQ-NEXT-COEFF-LAW Coefficient scaling law:** Do the PC-3 coefficients
  (fixed, a, b) follow a law in (active bytes, KV bytes/token, resident bytes)
  across the BYTES-LAW panel, predicting a held-out model's held-out shape
  within the bar? Ceiling L3 through AP-1 holdout machinery only. **NEW**;
  extends `Q4`/`C-023-COEFF-TRANSPORT`. Windows: 0 extra (rides BYTES-LAW +
  PHASE-CROSSOVER). **Difficulty:** none.

- **RQ-NEXT-RESIDENT-IDLE Does resident memory cost idle power:** Is the fixed
  term a function of resident bytes (65–100 GB resident vs none), or is LPDDR5
  self-refresh contents-blind (predicted null)? Ceiling L2. **Extension** of
  `C5-1.7`. 30 s idle ⇒ 1 W = 30 J; resolution ≈0.03 W. Windows: <1.
  **Difficulty:** none. **Risk:** macOS memory compression at high residency.

- **RQ-NEXT-FRONTIER-235B The 128 GB frontier:** Does Qwen3-235B-A22B at
  3-bit (~100 GB) run, and does its energy/token sit on the BYTES-LAW line or
  above it (paging)? Ceiling L1/L2 frontier point. **Extension** of `C5-1.10`.
  Windows: 1. **Difficulty:** none. **Risk:** 3-bit MLX conversion availability
  (NEEDS-WEB).

- **RQ-NEXT-ROOFLINE-DEVICE Second device as roofline falsifier:** On a
  3080 Ti (912 GB/s, 12 GiB, board boundary), do BYTES-LAW and p\*/d rescale by
  the device's byte/FLOP ratio? Ceiling L2 per boundary; L4 only with
  calibration. **Extension** of `C5-2.7`/`Q6`. Fits: Qwen3 1.7B/4B/8B.
  Windows: NV-gated, 2. **Difficulty:** none. Outside an Apple-only plan.

**What one week (~30 seat-windows) buys, ranked:** (1) BYTES-LAW + COEFF-LAW +
FRONTIER-235B (4): the scaling law that turns Paper C into a predictive model.
(2) PHASE-CROSSOVER + PREFILL-CHUNK (3): the roofline signature p\*/d, the
cheapest falsifiable prediction. (3) MIXER-3B + MIXER-120B (7): the north-star
mechanism paper. (4) SPEC-SURFACE + BATCH-KNEE + ROUTING×BATCH (7):
dynamic-execution axes predicted from static coefficients. (5) KVQ-SURFACE +
EPCA-LEVELS/MECHANISM (9): the applied paper; TOPK-KNOB and RESIDENT-IDLE fill
gaps. **Three boldest:** TOPK-KNOB (one artifact, one dial), PHASE-CROSSOVER
(p\*/d as a machine constant predicted for a held-out model), ROUTING×BATCH
(routing entropy as an energy knob, only under batching).

## Cross-seat dedupe 2026-09-16

Each row pairs an Astra `RQ-D-A*` with a Fable `RQ-NEXT-*` that isolates the
same physical mechanism. "Stronger" means the design that identifies the
mechanism with fewer confounds or a sharper predeclared prediction; the
magistrate retires the weaker id later. Unpaired ids are listed after the
table.

| Astra | Fable | Shared mechanism | Stronger, and why |
|---|---|---|---|
| RQ-D-A01 | RQ-NEXT-RESIDENT-IDLE (+ the resident-bytes term of BYTES-LAW) | Resident-but-unread bytes vs bytes actually read: does residency cost joules before memory pressure? | **A01.** Same model with 0/24/48 GB of unread retained buffers is a within-artifact intervention; RESIDENT-IDLE only measures the idle term. Keep RESIDENT-IDLE's 30 s idle read as a rider inside A01's floor window. |
| RQ-D-A03 | RQ-NEXT-ROUTING×BATCH | Expert-route overlap within a batch permits weight reuse; disjoint routes enlarge the working set. | **A03** for the identification (dense 32B control, predictor trained on two cells, held-out third cell and unseen partition). Adopt Fable's predeclared B=1 null as an extra arm — it is the sharper falsifier. |
| RQ-D-A04 | RQ-NEXT-BYTES-LAW + RQ-NEXT-COEFF-LAW | Energy as a function of bytes moved (weights + KV) per token, transported to a held-out model. | **BYTES-LAW/COEFF-LAW** as the first law: one covariate, eight models, one held-out model — it directly lifts `C5-1.1`'s cap and cannot overfit. A04's duration predictor and out-of-family challenges (70B, A3B) become the second leg once the one-covariate law stands or fails. |
| RQ-D-A05 | RQ-NEXT-MIXER-3B + RQ-NEXT-MIXER-120B | KV-read growth with context differs by mixer (GQA linear, MLA compressed, linear/delta constant, sliding-window capped). | **MIXER-3B.** Matching ≈3B active removes the size confound A05 carries (32B dense vs 16B-A2.4B vs 27B vs 48B-A3B). Take A05's held-out-context prediction step (freeze the crossover before the held-out run) into MIXER-3B. |
| RQ-D-A06 | RQ-NEXT-PREFILL-CHUNK | Prefill chunk size trades matrix parallelism against state hand-offs and launches. | **PREFILL-CHUNK first** (dense 8B/32B, <1 window, saturation curve); A06's hybrid leg with output-identity validation and held-out 16K prediction rides afterwards, if the hybrids are supported. |
| RQ-D-A07 | RQ-NEXT-KVQ-SURFACE | KV-byte saving vs a fixed dequantization cost. | **KVQ-SURFACE** as the first-order surface: it predicts the saving from the PC-5 slope. A07's weight×KV interaction is the second leg. |
| RQ-D-A08 | RQ-NEXT-SPEC-SURFACE | A verify step costs ≈ one decode step in bytes; break-even acceptance follows from drafter/target bytes. | **SPEC-SURFACE first**: it predicts break-even from PC-3 coefficients with a held-out pair (L3). A08 (burst distribution at matched mean acceptance) is a second-order question that needs SPEC-SURFACE's surface to exist. Both need the counter-complete speculative path (NEEDS-WEB). |
| RQ-D-A09 | RQ-NEXT-MTP | Native MTP heads reuse target state; an external drafter carries its own weights. | Equivalent; both blocked on an MLX MTP surface. Keep **A09** as the design record (target, head on/off, qualified draft candidate named). |
| RQ-D-A10 | RQ-NEXT-EPCA-LEVELS | Energy per correct answer across published MATH levels at a fixed token envelope. | **EPCA-LEVELS** asks the mechanism question (is the rise fully explained by emitted tokens, PC-6/PC-7); A10's frozen licensed subset, deterministic quarantined scoring, and the AP-5 policy prerequisite are carried in as its protocol. |
| RQ-D-A11 | RQ-NEXT-EPCA-MECHANISM | Residual energy across mechanisms on the same strata. | **A11** identifies an execution-policy effect only via A02's dispatch intervention; EPCA-MECHANISM is a cheaper named-set comparison sharing EPCA-LEVELS rosters. Run EPCA-MECHANISM first; A11 after A02 exists. |
| RQ-D-A12 | RQ-NEXT-BATCH-KNEE | Batching amortizes weight reads until B×KV bytes ≈ weight bytes. | **BATCH-KNEE first**: a point prediction of the knee from PC-5 in 2 windows. A12 adds the context axis and the phase split with a held-out interior — the extension. |
| RQ-D-A15 | RQ-NEXT-ROOFLINE-DEVICE | A second device rescales the byte/FLOP ratio and falsifies the mechanism. | **ROOFLINE-DEVICE** runs on owned hardware (3080 Ti) with a specific rescaling prediction; A15 prefers a second Mac. Both outside the Apple-only plan. |

**Unpaired.** Astra only: A02 (function-preserving expert locality), A13
(prefix × verification-state reuse), A14 (phase compensation hidden by a
request total), A16 (state-transfer placement). Fable only: TOPK-KNOB (no
Astra design turns the router's k), PHASE-CROSSOVER (p\*/d as a roofline
constant), FRONTIER-235B (a frontier point; related to A01's pressure arm and
`C5-1.10`, not the same question).

## Literature and best practices 2026-09-16

Source: the literature seat (`rq-literature-fable.md`, 2026-09-16; every entry
verified by fetching the page or PDF). One correction it made to its brief:
`docs/paper/draft-v1.md` §A.2 commands `powermetrics` at 100 ms (~10 Hz
observed), not ~1 s.

### Best practices, item by item (seat §2)

| Practice (source) | JouleWise |
|---|---|
| Analyzer ≤1% uncertainty, calibrated yearly, fixed ranges (SPEC methodology https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf; MLPerf checker https://github.com/mlcommons/power-dev/blob/master/compliance/check.py) | **Not done**: software counter, no gain calibration; Apple calls the values "estimated and may be inaccurate"; `draft-v1.md` §7 admits no wall check. **Weaker**; the field's first question. |
| Clock sync (MLPerf: NTP, 800 ms tolerance) | **Stronger**: in-window pulse fiducials, rate-aware clock model, refusal on active NTP correction (`draft-v1.md` §2). Sub-100 ms bound vs 800 ms. |
| Sampling cadence vs phase length (Dauner https://hotcarbon.org/assets/2026/paper-46.pdf; Yang https://arxiv.org/abs/2312.02741; Hähnel http://www.sigmetrics.org/greenmetrics/2012/papers/Hahnel.pdf) | **Partly**: resolvability rule <3 records → `not resolvable` (`draft-v1.md` §1); edge smear characterised by pulses (§A.3). **Not done**: `powermetrics` internal update period / stale reads uncharacterised — Dauner's NVML finding is the analogue. |
| Repetitions ≥30 (Cruz https://luiscruz.github.io/2021/10/10/scientific-guide.html), 10–20 (Illusion https://arxiv.org/abs/2605.11999), CI stopping rule (Wilkins https://doi.org/10.1145/3632775.3662830) | **Differently**: n=10 ABBA blocks in the diagnostic contrast (`CLAIMS_STATUS.md` §2), pre-registered n with a one-way prior ratchet; repetition attacks the smaller term by design. Defensible; state why n is fixed rather than adaptive. |
| Warm-up (Cruz 5 min; Illusion 3 iterations) | **Done for calibration** (3 warm-up pulses, `draft-v1.md` §A.3.4). Inference warm-up member: no stated rule found in the draft — make it explicit. |
| Thermal control (SPEC ambient ≥20 °C, ±0.5 °C sensor, 4 samples/min; Watt Counts <65 °C cool-down https://arxiv.org/abs/2604.09048; Illusion logs die temperature) | **Differently**: cooldown gate ≤300 s to ≤1.10× reference power, "nominal thermal pressure", environment snapshots (`draft-v1.md` §3, §5). No ambient sensor, no die temperature. **Weaker on record, stronger on gating.** |
| Idle: measure as its own interval, never subtract (SPEC); report gross + marginal | **Done**: gross headline, idle-subtracted labelled secondary, phase energy gross-only (`draft-v1.md` §4). |
| Counterbalancing / drift (Georges; Mytkowicz) | **Stronger**: ABBA with midpoint evidence and a separate drift allowance (`draft-v1.md` §5). Nobody in the seat's related-work list does this. |
| Uncertainty reporting | **Stronger**: cell resolution bound + separate directional interval + printed refusal (`draft-v1.md` §4). Only AgentStop, Watt Counts, Bench360 and Illusion report any CI. |
| Tracker overhead (Khan https://dl.acm.org/doi/10.1145/3177754; Cao https://aclanthology.org/2020.sustainlp-1.19/; NAACL 2025 https://arxiv.org/abs/2502.05610) | **Not done**: `powermetrics` sampler overhead at 100 ms not reported. Cheap to add. |
| Pre-registration (Zhuang et al. https://arxiv.org/abs/2605.28873) | **Stronger and unique in energy work**: frozen packs, hashes, freeze receipts (`docs/paper/protocol` §P.4). |
| Artifacts (ACM v1.1 via https://sigir.org/general-information/acm-sigir-artifact-badging/; ICPE 2026 AE https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/: Zenodo DOI, README with time estimates) | **Partly**: code open, evidence archive pending, FLOOR-BIND-01 limits third-party re-derivation (`draft-v1.md` §9). Target Available + Functional; Results Validated cannot be claimed at submission. |

### Duplicates — cite and reposition (seat §3)

- **The 1.7B-vs-8B decode contrast:** model-size scaling is published on GPUs
  (ML.ENERGY https://arxiv.org/abs/2505.06371, Watt Counts
  https://arxiv.org/abs/2604.09048) and on Apple silicon (Silicon Showdown
  https://arxiv.org/abs/2605.00519, GreenBench https://arxiv.org/abs/2608.28667).
  Keep it as the decision-rule demonstration only, with those citations.
- **C5-1.1:** Fernandez et al. (https://aclanthology.org/2025.acl-long.1563/;
  OLMoE up to 54% *more* energy than dense OLMo-1B) and ML.ENERGY v3
  (https://arxiv.org/abs/2601.22076; Qwen3-30B-A3B 3.56× lower J/token than
  Qwen3-32B) already conflict on kernels, so stack-conditioned pairwise is the
  honest framing, as C-014 caps it.
- **C5-1.12:** Arya & Simmhan (https://arxiv.org/abs/2506.09554; INT8 can cost
  more than FP16) and ML.ENERGY FP8 show non-monotone quantization results;
  cite, do not re-measure as a headline.
- **C5-2.5:** Fernandez already shows the batch-size sign flip (speculative
  decoding −29% at batch ≤16, +26% at batch 128).

### Novel (seat §3)

- **RQ-ATTRIBUTION-DOMINANCE:** no paper quantifies energy moved by phase-edge
  placement; the closest (Hähnel) is CPU-path scale. Illusion and Ruf &
  Detyniecki avoid the boundary by construction (separate operations;
  generation length = 1).
- **RQ-SHORT-PREFILL-RESOLVABILITY** as a printed negative with a record-count
  rule is new for Apple silicon and dovetails with Dauner.
- The pre-registered floor with refusal semantics is unique here.
- **C5-1.3** (per-phase power asymmetry) is known on GPUs (Splitwise
  https://arxiv.org/abs/2311.18677, Illusion) but unmeasured with a calibrated
  boundary on a unified-memory SoC — future characterisation, not a claim.
- **Reviewer questions we cannot yet answer:** (1) gain vs wall power under
  this load (Cao/Jay show 17–20% load-dependent gaps; `Q6` is cut); (2)
  `powermetrics` update granularity and whether 100 ms interval averages
  alias; (3) why not isolate prefill with generation length = 1 (the 1-token
  arm is a cheap falsifier we do not run); (4) sampler overhead; (5) one unit,
  one stack, pulse-to-inference transfer untested (Future Work #1 is the right
  test).
- **The one change that most raises citation-worthiness:** an
  independent-read-path cross-check — read the IOReport "Energy Model"
  cumulative counters (Zeus's Apple interface
  https://github.com/ml-energy/zeus-apple-silicon; 1 mJ, arbitrary instants, no
  sudo) at the runtime's own phase edges in the same window, and compare each
  phase's counter delta with the `powermetrics` interval integral against the
  cell floor. Caveat to print: both paths are Apple's model, so it tests
  read-path and time-base independence, not physics. Run it as a post-`_v5`
  diagnostic-window arm; do not touch the frozen pack. Runner-up: a
  generation-length-1 prefill-isolation arm (Ruf's design) as a boundary-free
  falsifier. Both are ruled into the research plan's Phase 0 desk day.

### Cite these (seat §4)

1. Tschand et al., MLPerf Power, HPCA 2025, https://arxiv.org/abs/2410.12032 — external-analyzer rules, 60 s minimum, ranging; the benchmark-rules baseline we translate.
2. SPEC Power and Performance Methodology 2025, https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf — ≤1% uncertainty, ambient ≥20 °C, idle as its own interval.
3. Chung et al., ML.ENERGY Benchmark, NeurIPS 2025, https://arxiv.org/abs/2505.06371 — steady-state per-token method, no repetitions.
4. You et al., Zeus, NSDI 2023, https://www.usenix.org/conference/nsdi23/presentation/you — energy-window abstraction; Apple backend chose IOReport.
5. Jay et al., CCGrid 2023, https://doi.org/10.1109/CCGrid57682.2023.00020 — software meters vs wall: load-dependent gap.
6. Cao et al., SustaiNLP 2020, https://aclanthology.org/2020.sustainlp-1.19/ — software estimates 20% off, twice the spread.
7. Khan et al., RAPL in Action, TOMPECS 2018, https://dl.acm.org/doi/10.1145/3177754 — counter-mechanics checklist.
8. Hähnel et al., 2012, http://www.sigmetrics.org/greenmetrics/2012/papers/Hahnel.pdf — edge alignment to counter updates; nearest ancestor.
9. Dauner et al., HotCarbon 2026, https://hotcarbon.org/assets/2026/paper-46.pdf — sampling frequency vs counter update.
10. Yang et al., SC24-W, https://arxiv.org/abs/2312.02741 — nvidia-smi samples 25% of runtime.
11. Ma et al., Illusion of Power Capping, 2026, https://arxiv.org/abs/2605.11999 — strongest phase methodology; counter cross-check.
12. Ruf & Detyniecki, HotCarbon 2026, https://hotcarbon.org/assets/2026/paper-17.pdf — 1-token prefill isolation; boundary-free alternative.
13. Niu et al., TokenPowerBench, AAAI 2026, https://arxiv.org/abs/2512.03024 — phase tagging without an error budget.
14. Patel et al., Splitwise, ISCA 2024, https://arxiv.org/abs/2311.18677 — prefill/decode power asymmetry.
15. Patel et al., POLCA, ASPLOS 2024, https://arxiv.org/abs/2308.12908 — boundary read visually from DCGM traces.
16. Fernandez et al., ACL 2025, https://aclanthology.org/2025.acl-long.1563/ — MoE, speculative, batching sign flips; for C5-1.1/C5-2.5.
17. Javat & Kazakov, Silicon Showdown, 2026, https://arxiv.org/abs/2605.00519 — `powermetrics` vs NVML boundary mismatch.
18. Pham et al., AgentStop, CAIS 2026, https://arxiv.org/abs/2605.15206 — `powermetrics` 100 ms with CIs; nearest Apple methodology.
19. Kannan et al., GreenBench, 2026, https://arxiv.org/abs/2608.28667 — Apple LLM energy at 2 s, no anchoring; cautionary comparator.
20. Zhuang et al., Paired-MDE, 2026, https://arxiv.org/abs/2605.28873 — pre-registered detectable effect (accuracy, not energy).

Not verified by the seat: `_v5` block counts per cell; an inference warm-up
rule in the draft; the ACM badging page (403; SIGIR mirror used).
