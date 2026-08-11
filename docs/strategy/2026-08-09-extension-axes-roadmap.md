# Extension axes roadmap — 2026-08-09

**Status: DRAFT — rankings and registry rows await Ed's review; nothing here is registered.**

**Provenance.** This document assembles workflow run `wf_d35129b8-58c`
(2026-08-09): six parallel Sol axis evaluations plus one xhigh synthesis. The
magistrate commissioned the workflow to inform H1's “one designed extension”
choice and the H2 mechanism-level axis map in `docs/strategy/HORIZONS.md`.
This is an evaluation roadmap, not a campaign authorization, evidence
promotion, or change to the research-question bank or registry.

## Reading key

- **H1 / H2:** H1 is the next-semester, ICPE-class paper: the metrology core
  plus one designed extension. H2 is the longer-horizon program that measures
  energy as a third axis for inference mechanisms, with a detection floor and
  explicit refusals attached to every result.
- **Q4:** the existing fixed-versus-marginal energy model,
  `E = fixed + prefill(prompt tokens) + decode(output tokens)`. An axis called a
  “Q4 rider” tests or refines that one thesis; it does not create a new thesis.
- **D-075:** the accepted 2026-07-17 decision that folds extension-axis work
  into existing research-question rows where possible, caps candidate
  commitments at L2, and leaves commitment authority with Ed
  (`docs/decision_log.md:3922-3974`).
- **L2 ceiling:** a same-boundary comparative result under a named workload
  and policy, with at least five strict-valid repetitions per condition,
  confidence intervals, controlled order, and an effect above the detection
  floor. It does not license universal, architecture-wide, or uncalibrated
  cross-boundary claims (`docs/contracts/claims_ladder.md`). **L0** is a
  capability smoke and **L1** is an observation on one exact stack; neither is
  a comparative efficiency result.
- **AXI:** the repository's “as-executed inference” contract family. **AXI-SA**
  is the landed burst/speculative-decode configuration, event, counter,
  denominator, and validation contract. **AXI-SC** is its pinned runtime
  feasibility verdict; a “supported AXI-SC verdict” means a runtime retains
  the mechanism, executes an identifiable path, and exposes the required real
  counters.
- **Detection floor:** the smallest energy difference the named instrument
  and boundary can resolve honestly. D-078 clause 11 found this setup
  attribution-limited, not noise-limited: phase-boundary clock anchoring adds
  about 0.7–1.0 J per member, and the effective phase-contrast bar is near
  5 J (`docs/decision_log.md:4653-4710`). “Above-floor” means the comparison
  clears the applicable governed floor; otherwise the result is “not
  resolvable.”
- **MLX / CUDA / ROCm:** MLX is the Apple-silicon runtime used on the M3 Max;
  CUDA is NVIDIA's execution platform for the 3080 Ti leg; ROCm is AMD's
  execution platform, whose low-level kernel API is often labeled HIP. The
  serving runtime and the execution backend are different identities and must
  not be conflated. **ISA** means instruction-set architecture.
- **KV cache:** the stored attention keys and values reused while decoding.
  **FFN** is the transformer feed-forward network; **MoE** is a mixture-of-
  experts FFN that routes each token through a subset of experts. **MTP** is
  native multi-token prediction using heads inside the target model. **GQA**,
  **MLA**, **SSM**, and **EAGLE** mean grouped-query attention, multi-head
  latent attention, state-space model, and an auxiliary-drafter speculative
  decoding family, respectively. **SoC** means system on a chip; **ANE** is
  Apple's Neural Engine. `J` means joules, `GiB` means gibibytes, and `K` is
  the number of speculative candidate positions proposed in a decode round.
- **Internal identifiers:** `RQ-*` and `C5-*` name research-question homes;
  `FAM-*` names a frozen analysis family that may not be pooled with another
  family. `D-nnn` points to a binding decision-log entry. `P1-*` / `P2-*`
  names are repository queue or gate identifiers, not paper sections:
  `P1-006` is the NVIDIA access/live-promotion gate and `P2-015` owns the
  applicable floor. `[ED-EXTERNAL]` means the dependency needs Ed or an
  external resource. `G10` is D-071's model/device memory-fit gate.
- **Phase labels carried from the earlier roadmap:** `PF` means post-floors
  exploratory, `NV` means the NVIDIA leg, `NS` means needs a new subsystem,
  and `PC` means post-capstone.
- **Output gates:** `C-023-OUTPUT-IDENTITY` requires exact output-token
  equivalence or an explicit divergence report for speculative-decoding
  efficiency. `C-023-QUALITY-EQUIV-QUANT` requires a predeclared quality/
  divergence rule before quantization-efficiency or quality-neutrality
  wording.
- **NEEDS-WEB:** the source evaluation could not verify the claim from durable
  local evidence. It remains an explicit research gap, not a fact or a
  commitment.

## Synthesis-ranked roadmap

The following table reproduces the synthesis order, identities, phases, and
stated reasons without re-ranking or merging entries.

| Rank | Row identity | Phase / gate | Synthesis reason |
|---:|---|---|---|
| 1 | `C5-2.5c refinement (DSpark/DFlash break-even arms)` | post-floors exploratory | Most thesis-direct result available: fixed-overhead vs acceptance-dependent break-even under Q4; landed validator already accepts realized `K <= cap` (`joulewise/axi_decode_config.py:451-508`); vendored MLX runtime runs today, needs only a per-round emission callback + adapter. |
| 2 | `C5-2.11a (kv_bits x weight-quant 2x2 rider)` | post-floors exploratory | Only proposed row that tests a Q4 interaction rather than a main effect; runnable now on mlx-lm 0.31.3 with zero runtime modification; binds `C-023-QUALITY-EQUIV-QUANT`. |
| 3 | `RQ-AXI-HYBRID-PAIR-Q4RIDER` | post-floors exploratory + gated (pair **NEEDS-WEB**) | Broadest architecture-level Q4 stress test that respects the D-078 clause 11 attribution limit; clean named pair unverified. |
| 4 | `C5-2.5b refinement (realized-K proposal-work)` | post-floors exploratory | Enriches Q4 coefficients with observed proposal work; same campaign as rank 1. |
| 5 | `C5-2.5d refinement (lookup contamination control)` | post-floors exploratory | Mandatory control traveling with rank 1, not standalone science. |
| 6 | `C5-1.1-DENSE-MOE-PAIR-RIDER` | post-floors exploratory + gated (MoE MLX artifact **NEEDS-WEB**) | Paper-relevant conditional-compute contrast; pair confounding caps its language; Mac-only (MoE exceeds 12 GiB CUDA cap). |
| 7 | `MOEXBATCH-EVENTSV2-RIDER` | post-floors exploratory + gated (pair + static-batch adapter) | Implements the existing D-070 MoE×BATCH candidate (`docs/decision_log.md:3810-3812`); double-gated. |
| 8 | `C5-2.5a refinement (cross-method contrast)` | post-capstone | Keep deferred per D-075; refine wording only. |
| 9 | `RQ-AXI-ATTN-CONTEXT-SLOPE-AMEND` | post-floors exploratory + gated | Cheap but largely duplicates `RQ-KV-GROWTH` / `C5-1.2` territory. |
| 10 | `C5-1.8 within-runtime kernel-path amendment` | NVIDIA leg + gated (`P1-006`; vLLM controls **NEEDS-WEB**) | Genuinely better causal control than the stack-vs-stack rider, but live CUDA is not repo-proven. |
| 11 | `C5-3.3 structured requested-vs-resolved provenance rider` | post-capstone intake, capture-now amendment | Cheap instrument future-proofing, not a paper result; never add `rocm` to `RuntimeBackend`. |
| 12 | `C5-2.15 (contextual-sparsity CUDA)` | NVIDIA leg + gated | Runtime, artifact, and 12 GiB fit all **NEEDS-WEB**. |
| 13 | `C5-2.5c/MTP arm activation` | needs-new-subsystem + gated (AXI-SC supported verdict) | Already preserved contingently at `docs/research_question_bank.md:898-906`; watch, do not schedule. |
| 14 | `C5-2.5a/MTP-LOCUS` | post-capstone + needs-new-subsystem | Meaningful only after both mechanism families execute. |
| 15 | `C5-2.5e (head/depth policy)` | needs-new-subsystem + gated | Premature before any executable native-MTP arm. |
| 16 | `C5-2.16 (density-counter association)` | NVIDIA leg + gated | Counters matter only after sparse execution exists. |
| 17 | `C5-1.13 (sparse Mac pair)` | needs-new-subsystem + gated | No verified Mac skipping runtime; ID collides with `docs/research_question_bank.md:685-686` (“not a new C5-1.13 thesis”) — do not mint. |
| 18 | `C5-3.3 CUDA/ROCm named-unit replication` | post-capstone + needs-new-subsystem | New hardware + telemetry subsystem; lowest capstone return per cost; already framed by existing `C5-3.3`. |

Synthesis identity rules are binding here. Axis-1 `C5-2.5c` and the native-MTP
`C5-2.5c/MTP` proposal are separate frozen-family arms of one registry row
(`FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT`) and must never be pooled.
`C5-2.5a/MTP-LOCUS` extends rather than duplicates deferred `C5-2.5a`. The two
`C5-3.3` proposals distinguish present-day provenance capture from future
cross-vendor science.

The synthesis's top three remain, in order: (1) the DSpark/DFlash `C5-2.5c`
break-even refinement, because it gives the clearest fixed-overhead-versus-
acceptance curve on a runtime that runs today; (2) `C5-2.11a`, because it is
the only proposed interaction test; and (3) `RQ-AXI-HYBRID-PAIR-Q4RIDER`,
because it conditionally tests whether Q4 coefficients transport from runtime
knobs to architecture differences without claiming module attribution.

The synthesis says the following are not worth promoting now:
`C5-1.13` (no substrate and an ID collision), `C5-2.15` / `C5-2.16`
(doubly **NEEDS-WEB** and otherwise only a `C5-1.8` stack shadow), `C5-2.5e`
and `C5-2.5a/MTP-LOCUS` (premature behind an unschedulable upstream event),
and `C5-3.3` CUDA/ROCm replication (already framed; hardware uncommitted).
`RQ-KV-POOL-OBSERVABLES` remains disposed under the 2026-07-17 ruling.

The lane enrichment scores remain their recorded outputs: medium for
DSpark/DFlash, architecture/attention, native MTP, sparse FFN, and unified
kernel/runtime; low for KV-cache management. The synthesis recorded a
dissenting re-weighting — it would raise `C5-2.5c` and `C5-2.11a` and lower
attention-slope and near-term MTP value — but did not alter the lane scores.

## Axis 1 — DSpark and DFlash speculative decoding

### Summary

The landed AXI-SA event model already represents both methods arithmetically.
Its event validator checks each round's observed `tokens_proposed` against a
cap rather than requiring equality (`joulewise/axi_decode_config.py:451-508`),
so DSpark's variable-K confidence scheduling and DFlash's fixed-K block
verification both fit. The accepted-prefix/bonus split maps to
`tokens_accepted` / `target_emitted_count` under
`docs/specs/axi/sa_burst_decode_contract.md`.

The remaining strain is descriptive. `SpeculationPolicy` has no realized-K,
confidence-threshold, block-size, or drafter-forward-work fields. For DFlash,
`tokens_proposed` therefore means positions submitted to verification, not all
full-block proposal compute. `AxiDecodeEmission` also has no `proposal_source`,
so a DSpark hybrid round cannot separate lookup and model drafting. Pure-mode
runs with lookup disabled preserve the present schema. Under whole-machine
powermetrics and the contract's group/request-scope assignment, drafter energy
cannot be split from target energy in any case.

The vendored `/Users/edr/code/mlx-dspark-vendor` clone (`mlx_dspark` v0.4.2)
implements `dspark`, `dflash`, `lookup`, and `baseline` modes through a direct
Python API and an OpenAI-compatible server. Its `GenResult` aggregates record
committed burst length, not accepted draft length, so a claim-ready adapter
needs a structured per-round callback inside the vendor loop; parsing summary
or verbose text would corrupt accepted-token accounting.

This axis is not a new registry area. D-075 already placed riders
`C5-2.5a`–`d` in `docs/research_question_bank.md:863-915`, and the registry's
`C5-2.5` row records `2.5c` as primary, `2.5b` secondary, `2.5d` mandatory,
and `2.5a` deferred. This lane refines those rows; it does not mint replacements.

### Harness difficulty

Already landed: the AXI-SA burst-decode contract; the denominator rules in
`docs/contracts/token_normalization.md` (gross J/committed token is primary;
J/accepted token is diagnostic); `SpeculationPolicy`, event validation,
aggregation, and the `AxiRuntimeResult` sink
(`joulewise/axi_decode_config.py`, `joulewise/schemas.py`,
`joulewise/controller.py`, `joulewise/interfaces.py:287-304`). Variable K needs
no contract change.

New work would be:

1. a vendor-side per-round trace/callback in `speculative_generate` and
   `dflash_generate`;
2. a JouleWise adapter producing real AXI emissions (the current
   `joulewise/adapters/mlx_runtime.py` emits flattened token events, while only
   `joulewise/adapters/mock_spec_runtime.py` emits AXI events); and
3. explicit initial target-prefill and end-of-sequence truncation handling so
   `emitted = accepted + target_emitted` remains true.

An instrumentation proof is bench-scale. A claim-ready pure-mode DSpark and
DFlash adapter with exact output-identity checks is multi-session. Hybrid
source attribution or drafter/target energy splitting would require a
successor contract or new subsystem and is outside the landed contract.

### Feasibility — Mac/MLX versus CUDA

**Mac/MLX:** grounded today. The vendored MLX/Apple-silicon clone exposes
direct API entry points (`speculative_generate`, `dflash_generate`, pair
loaders) and all four modes (`server.py` `MODES`). Pair selection still must
clear D-074's conditional Qwen3-4B posture plus memory and floor gates.

**3080 Ti / CUDA:** no grounded DSpark/DFlash implementation. The vendor tree
is MLX-only; `config.py` rejects vLLM “speculators” layouts, and
`joulewise/adapters/vllm_runtime.py` has no speculative-decode configuration or
AXI path. Whether a maintained CUDA DSpark/DFlash implementation exists, fits
12 GiB, and exposes counters is **NEEDS-WEB**. vLLM's own speculative decoding
could be studied only as a different mechanism, separately labeled and never
pooled with MLX coefficients; its current API and observability are also
**NEEDS-WEB**. AMD/other implementations are not grounded.

The identification web memo was lost to temporary-file cleanup. Upstream
provenance and CUDA availability therefore remain **NEEDS-WEB**; only the
vendored MLX tree is durable local evidence. D-073's M3 Max primary plus
3080 Ti fleet and D-070/D-073's broad-instrument, narrow-claim posture still
permit an MLX-only mechanism study.

### Draft candidate registry wording

> **Draft — `C5-2.5c (existing D-075 rider — refine, do not mint new)`.**
> **Question:** “For output-identical, single-request MLX decoding on the M3
> Max, at what observed acceptance behavior does pure DSpark or DFlash first
> reduce gross request energy relative to its own speculation-off baseline?”
> **Ceiling:** “L2 causal language for the pinned machine/runtime/model/prompt
> strata only, floor-qualified, with distinct rows per mechanism;
> `C-023-OUTPUT-IDENTITY` binding via exact token IDs.”
> **Forbidden upgrade:** “No serving-level, cross-hardware,
> cross-model-family, or universal ‘speculation saves energy’ claim.”

> **Draft — `C5-2.5b (existing rider — refine)`.**
> **Question:** “Within each pinned method, how do observed verified-candidate
> count, accepted-prefix length, and committed burst size relate to latency
> and gross energy?”
> **Ceiling:** “L2 within-support association over observed K values; DFlash
> full-block drafter work reported separately from AXI verified positions.”
> **Forbidden upgrade:** “No general optimal-K law, no extrapolation beyond
> observed caps, no reading `tokens_proposed` as total DFlash proposal-side
> compute.”

> **Draft — `C5-2.5d (existing mandatory contamination control — refine)`.**
> **Question:** “How much do DSpark results change when n-gram lookup
> proposals are disabled, and can lookup-only behavior be reported as a
> separate diagnostic configuration?”
> **Ceiling:** “L2 run-level comparison across pure-DSpark, lookup-only, and
> hybrid configurations; mixed-mode runs stay aggregate diagnostics unless
> the schema gains proposal-source labels.”
> **Forbidden upgrade:** “No source-specific acceptance or energy attribution
> from hybrid traces under the current schema; no pooled ‘DSpark drafter
> efficiency’ figure containing lookup rounds.”

> **Draft — `C5-2.5a (existing deferred rider — keep deferred)`.**
> **Question:** “Under identical target, tokenizer, output identity, workload,
> and floor-qualified protocol, how do DSpark and DFlash differ in gross energy
> per committed token and mechanism diagnostics?”
> **Ceiling:** “L2 comparison on the pinned Apple/MLX support only;
> accepted-token energy remains a diagnostic denominator per
> `docs/contracts/token_normalization.md`.”
> **Forbidden upgrade:** “No algorithm-wide superiority claim, no CUDA
> generalization, no claim that whole-machine measurement isolates drafter
> energy from verifier energy.”

### Risks

- Attribution is request/group-level only; there is no drafter-versus-target
  energy split or hybrid proposal-source attribution. Pure-mode runs mitigate
  the latter.
- Vendor mode defaults and auto-calibration can move the treatment. Mode,
  lookup enablement, confidence threshold, verified-candidate cap, block size,
  cap-controller policy, sampling, prefix caching, and artifacts must all be
  frozen; “DSpark variable-K” is a configuration family, not one treatment.
- Exact token-ID equality must establish output identity per run. Vendor
  greedy-tie caveats prevent assuming losslessness from an upstream claim.
- Claim runs need the vendor commit, dependency lock, model hashes, local
  compatibility-patch identity (`VENDOR_PATCH_NOTES.md`), and exact pair
  receipts.
- Incomplete events, output mismatch, instrumentation overhead above floor,
  or a non-qualifying anchor void the affected claim under D-078.
- Because the web memo is missing, every upstream-provenance and CUDA claim
  beyond the vendored MLX tree remains **NEEDS-WEB**.

## Axis 2 — Architecture and attention variants

### Summary

The landed AXI-SA machinery can ask named-pair whole-request and coarse
prefill/decode architecture questions today. It cannot attribute energy to
attention versus FFN modules. D-078 clause 11 found a permanent phase-absolute
floor refusal, a roughly 0.7–1.0 J clock-anchor misattribution envelope per
member, and an effective phase-contrast bar near 5 J. Per-module attribution
would need a module-phase contract, runtime kernel hooks, and an architecture
manifest, yet production forwards would still lack the temporal
identifiability needed to decompose their energy.

No clean single-axis model pair is verified. A Qwen3-family 4B dense versus
30B-A3B-class MoE pair is the strongest same-family option, but total
parameters, depth, routing, and training still differ. GQA-versus-MLA and
sliding-window contrasts are cross-family or cross-generation; the token-
normalization contract therefore limits them to descriptive wording or J/char
and J/byte companion denominators. Every specific MLX-artifact availability
claim is **NEEDS-WEB**.

Most of the territory already has a home: `RQ-AXI-HYBRID-PAIR`, the
attention/context-slope rider on `RQ-KV-GROWTH`, `C5-1.1`, `C5-1.9`, and
MoE×BATCH. D-070's single-Q4-thesis posture and D-075's fold-in rule therefore
call for riders, not new theses. The lane rates enrichment medium: hybrid and
dense/MoE comparisons are real Q4 coefficient stress tests; attention variants
add less because their askable signal overlaps `C5-1.2` / `RQ-KV-GROWTH` and
clean pairs are unverified.

### Harness difficulty

Already covered: request-scoped `events.v2` and `request_roster.v1`
(`EVENT_TOP_KEYS`, `EVENT_SEMANTICS_VERSION` in
`joulewise/axi_decode_config.py`); per-phase `phase_energy_j` integration and
decode duration/throughput/burst and `phase_identifiability` surfaces in
`joulewise/schemas.py`; `gross_energy_j` and
`batch_group_gross_energy_j`, with no per-request division of group energy
(`docs/contracts/token_normalization.md:82-87`); reducer 0.6.2 as the only
claim-eligible AXI mint (`docs/specs/axi/sa_burst_decode_contract.md:31`); and
stack-identity slots for kernel/attention implementation “where known.”

Needed surface: a typed architecture identity containing mechanism, query and
KV head counts, trained window, expert topology, SSM type, source-config
digest, and fallback-path evidence. `ModelConfig` currently records only
name/family/source/revision/weight format/context window
(`joulewise/schemas.py:714`), while the AXI extension records batch and
speculation. Named-pair work also needs selection receipts and an analysis
plan; MoE×BATCH needs the queued static-batch MLX adapter.

Sizing from the lane: architecture sidecar plus load smoke is bench work;
normalized identity and a named-pair/context-slope plan are each session-sized;
claim-bearing Mac/CUDA campaigns are multi-session. Attention-versus-FFN
attribution is a new subsystem and remains structurally unidentifiable under
D-078 clause 11, so it is not recommended at any size.

### Feasibility — Mac/MLX versus CUDA

**Mac/MLX:** named-pair whole-request and prefill/decode contrasts can use the
existing M3 Max / MLX / powermetrics stack. A 4B dense versus
30B-A3B-class MoE pair fits the 128 GiB unified-memory machine conceptually,
but the MoE MLX artifact, matched quantization recipe, and G10 fit are
**NEEDS-WEB**. The MoE side exceeds the 3080 Ti's 12 GiB cap, making this a
Mac-only pair.

An MLA contrast needs a small real MLX port and is **NEEDS-WEB**; it would be
cross-family and therefore descriptive or J/char. A same-lineage
Mistral/Gemma pair whose trained attention masks truly differ is
**NEEDS-WEB**; cache-allocation knobs cannot be relabeled as trained
sliding-window attention. `RQ-AXI-HYBRID-PAIR` already marks controlled
SSM-hybrid pair availability **NEEDS-WEB** (`docs/research_question_registry.md`
row 83). No fleet-executed sparse-attention kernel path is established: a
sparse-labeled checkpoint using a dense fallback is not a sparse-attention
experiment, and runtime support is **NEEDS-WEB** on MLX and CUDA.

**3080 Ti / CUDA:** dense cross-checks may fit, but the MoE arm does not.
Pair-specific CUDA artifacts and sparse/MLA kernel paths remain
**NEEDS-WEB**. D-073 defines the 128 GiB M3 Max and 12 GiB 3080 Ti as the
primary fleet, with Jetson optional and non-cap-setting.

The missing DSpark/DFlash web memo does not bear on this axis; the vendored
clone and `docs/process_traces/2026-07-17-dspark-dflash-smoke/` were checked
only as surviving context.

### Draft candidate registry wording

> **Draft — `RQ-AXI-HYBRID-PAIR-Q4RIDER`.**
> **Question:** “For one predeclared hybrid(SSM/attention)-vs-pure-transformer
> named pair, do gross fixed, prefill, and decode Q4 coefficients differ across
> governed shapes?”
> **Ceiling:** “L2 pair-specific Q4 stress test (rider on existing
> `RQ-AXI-HYBRID-PAIR` home).”
> **Forbidden upgrade:** “No architecture-class efficiency claim, no causal
> SSM-mechanism attribution, no coefficient transport beyond the named pair.”

> **Draft — `C5-1.1-DENSE-MOE-PAIR-RIDER`.**
> **Question:** “Within one gate-passing family under exact tokenizer identity,
> how do gross request and decode-phase energy differ between one dense and one
> MoE artifact at matched shapes and quantization?”
> **Ceiling:** “L2 named-pair characterization; scaling claims stay under
> `C5-1.1`'s existing model-count rule (no covariate fits on 4–6 points).”
> **Forbidden upgrade:** “No active-parameter scaling law, routing-mechanism
> claim, or MoE-class efficiency claim from one pair.”

> **Draft — `RQ-AXI-ATTN-CONTEXT-SLOPE-AMEND`.**
> **Question:** “Across predeclared named GQA/MLA/sliding-window artifacts, how
> do within-artifact decode-phase context slopes differ descriptively above the
> phase floor?”
> **Ceiling:** “L2 named-artifact boundary-labeled characterization (amendment
> to the existing rider on `RQ-KV-GROWTH`); cross-tokenizer results require
> J/char/J/byte or descriptive-only language.”
> **Forbidden upgrade:** “No attention-vs-FFN energy fraction, no causal
> mechanism ranking, no per-token claims below cadence/floor limits.”

> **Draft — `MOEXBATCH-EVENTSV2-RIDER`.**
> **Question:** “For the selected dense/MoE pair, does static batch size change
> batch-group gross energy and prefill/decode phase structure differently
> between the two architectures?”
> **Ceiling:** “L2 named-pair static-batch interaction on
> `batch_group_gross_energy_j` (rider on the D-070 MoE×BATCH candidate).”
> **Forbidden upgrade:** “No per-request energy allocation within a batch
> group, no continuous-serving claim, no MoE-serving-efficiency
> generalization.”

### Risks

- Architecture, tokenizer, training data, total size, and quantization can
  travel together. Without a valid pair, the result falls back to descriptive
  stack-versus-stack wording. Every pair/port claim remains **NEEDS-WEB**.
- A phase contrast must clear roughly 5 J. Smaller prefill/decode shifts are
  unclaimable; module-level attribution is structurally unavailable.
- Architecture identity and executed-kernel/fallback evidence are not
  normalized. Sparse/MLA MLX kernel support is unverified; the MoE leg is
  Mac-only; MoE×BATCH also waits for a static-batch MLX adapter.

## Axis 3 — Native multi-token prediction

### Summary

Native MTP is contract-ready but runtime-blocked. AXI-SA already represents it
as `speculation.mode = native_mtp`, with `NativeMTPIdentity` fields for head
count, draft depth, head configuration, and target SHA-256 plus the null-draft-
identity invariant (`joulewise/axi_decode_config.py:181-241`). Reducer and
rollup validation key on speculation mode (`joulewise/schemas.py`). The frozen
family `FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT` is separate from all
`draft_model` arms and may never be pooled
(`docs/specs/axi/sa_burst_decode_contract.md:866,1879`;
`docs/contracts/analysis_plans.md:155`). Denominator rules are already in
`docs/contracts/token_normalization.md:44-60`.

The pinned runtime is the blocker. AXI-SC records
`unsupported_for_joulewise(native_mtp_generation)` for mlx-lm 0.31.3: there is
no native-MTP entry point, and the Qwen3.5 sanitizer strips every `mtp.*`
weight from the one local MTP-advertising artifact (about 65 GiB). A config
advertising heads is therefore candidate-artifact metadata, not proof that the
heads executed (`docs/specs/axi/sc_spec_decode_verdict.md:125-146,304`).

The revisit test is already specified: a successor pin must retain the heads,
execute an identifiable native path, and supply real AXI-SA counters. Only
then would an MLX adapter need to emit per-step `tokens_proposed`,
`tokens_accepted`, and decode emissions. The `C5-2.5` denominator ruling also
already exists: gross J/committed-output-token is the on/off efficiency
measure; J/accepted-MTP-token is a spec-on-only mechanism-yield diagnostic.
The MTP arm of `C5-2.5c` is explicitly contingent on a supported AXI-SC
verdict (`docs/research_question_bank.md:898-906`).

DSpark and DFlash rank ahead for the Mac leg because their vendored MLX code
runs today and needs only counter emission. The vendor README identifies both
as EAGLE-family auxiliary drafters consuming target hidden states, not native
MTP. Native MTP remains scientifically distinct but schedule-unreliable: keep
the dated contingency, instrument DSpark/DFlash first, and reopen MTP only
after a cheap successor-pin AXI-SC probe passes all gates.

### Harness difficulty

Already landed: `SpeculationPolicy` and `NativeMTPIdentity`; actual proposed
and accepted-token semantics and one decode emission per step
(`docs/specs/axi/sa_burst_decode_contract.md:333,390`); reducer/rollup checks
(`joulewise/schemas.py:1991-2147`); the frozen family and Holm multiple-testing
registry (`sa_burst_decode_contract.md:866,1879`;
`analysis_plans.md:155`); `C-023-OUTPUT-IDENTITY`; mock/native-MTP fixtures;
and the AXI-SC fail-closed probe and revisit conditions
(`sc_spec_decode_verdict.md:288-310`).

If an upstream runtime exposes hooks, a real MLX adapter producing
`AxiDecodeEmission` is session-sized, and a successor API probe update is
bench-sized. If counters must be extracted from a runtime fork, the adapter is
a new subsystem. Per-head/depth diagnostics beyond frozen identity would be a
multi-session successor-contract surface. No schema, reducer, or analysis-plan
change is needed for the basic arm.

### Feasibility — Mac/MLX versus CUDA

**Mac/MLX:** not feasible on mlx-lm 0.31.3. The package has no native-MTP
generation path and strips `mtp.*` weights. Whether a newer pin retains and
executes MTP heads is **NEEDS-WEB**. The 2026-07-30 desk sweep
(`docs/run_reports/2026-07-30-sweep-mechanisms.md`) identified MiMo-7B
(checkpoint heads but no MLX MTP support; vLLM only), DeepSeek-V3, and
Qwen3-Next (an approximately 45 GiB MLX 4-bit artifact exists, but end-to-end
execution and MTP retention are **NEEDS-WEB**). These are desk-research leads,
not project evidence.

**3080 Ti / CUDA:** the 12 GiB D-073 cap excludes the 65 GiB Qwen3.5 artifact
and DeepSeek-V3-class models. The sweep says vLLM advertises MTP support, but a
MiMo-7B-class quantized fit and real counters under 12 GiB are **NEEDS-WEB**.
That is the only plausibly reachable non-Mac cell, and it would no longer be
the requested Mac/MLX leg. AMD/other support is outside the D-073 fleet,
unsupported by repository evidence, and **NEEDS-WEB**.

The brief's `dflash-dspark-web.md` was absent. Repository process traces and
the vendored clone substitute only for the DSpark/DFlash contrast; all web-only
MTP facts remain **NEEDS-WEB**.

### Draft candidate registry wording

> **Draft — `C5-2.5c/MTP (arm activation, not a new row)`.**
> **Question:** “On one AXI-SC-supported MLX stack, does native MTP change
> gross request energy and gross J/committed-output-token versus spec-off at
> exact matched output?”
> **Ceiling:** “L2, named stack/artifact pair.”
> **Forbidden upgrade:** “No claim before a supported successor AXI-SC
> verdict; no generic MTP, serving, cross-hardware, or quality conclusion from
> one artifact/runtime pair;
> `FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT` never pooled with `draft_model`
> arms.”

> **Draft — `C5-2.5e`.**
> **Question:** “Within one frozen native-MTP artifact/runtime, do
> prospectively fixed head/depth policies change gross energy and
> accepted-proposal yield?”
> **Ceiling:** “L2, policy-specific, prospective design only.”
> **Forbidden upgrade:** “No use of `head_count` or configured `draft_depth`
> as proposed-token accounting (only realized candidate positions submitted
> to verification count); no post-hoc policy subsetting or cross-identity
> pooling.”

> **Draft — `C5-2.5a/MTP-LOCUS`.**
> **Question:** “Under a prospective cross-mechanism design, does drafter locus
> (native heads vs EAGLE-family auxiliary drafter) change whole-stack
> break-even behavior at matched output?”
> **Ceiling:** “L2, named mechanism pairs, deferred like `C5-2.5a` (NS).”
> **Forbidden upgrade:** “No component-level drafter-energy attribution or
> ‘zero-cost self-drafting’ language — self-drafting removes a separate
> artifact, not necessarily its compute/residency cost; no pooling of
> native-MTP and `draft_model` families.”

### Risks

1. Every result needs a fresh runtime pin and AXI-SC verdict; upstream MLX may
   add or silently remove both MTP paths and weight retention.
2. The leg cannot be scheduled, only watched, because it depends on an
   upstream runtime event.
3. Native MTP and DSpark/DFlash are adjacent but contractually separate frozen
   families. Cross-family pooling is forbidden.
4. Accepted MTP tokens, committed output tokens, burst size, and configured
   head-count × draft-depth are four different quantities; only runtime-
   observed counters are legal.
5. The 65 GiB local artifact exceeds the CUDA cell and leaves limited Mac
   headroom. Smaller-artifact fit and MLX reachability are **NEEDS-WEB**.
6. A config field such as `mtp_num_hidden_layers` is not execution evidence;
   conversion/sanitization demonstrably strips the heads.
7. A gross on/off ablation cannot isolate per-head component energy.

## Axis 4 — KV-cache management

### Summary

The 2026-07-17 evaluation already harvested the measurable space into four
registry candidates: `C5-2.11` for on-device quantized-KV energy, `C5-2.12`
for bounded-window KV marginal slope, `C5-2.13` for serialized prompt-cache
crossover, and `C5-2.14` for cache policy as a Q4 coefficient rider. The flat-
pool idea `RQ-KV-POOL-OBSERVABLES` was explicitly disposed because correlation
cannot support allocator-design inference
(`docs/process_traces/2026-07-17-extension-axes/roadmap-synthesis.md:71`).

The new information is experiment-design precision, not a new question.
Installed mlx-lm 0.31.3 exposes `kv_bits`, `kv_group_size`,
`quantized_kv_start`, and `max_kv_size` on the public generation path, but:

- rotating plus quantized KV is not implemented
  (`RotatingKVCache.to_quantized` raises `NotImplementedError`,
  `cache.py:551-552`);
- speculative generation silently removes `max_kv_size`
  (`generate.py:709-713`); and
- model-owned `make_cache()` implementations, such as Gemma-3's per-layer
  rotating caches, bypass `max_kv_size`.

The flat-pool direction remains disposed. MLX allocator readings
(`mx.core.get_active_memory`, `get_cache_memory`, `get_peak_memory`,
`set_cache_limit`, `set_wired_limit`, mlx 0.31.2) support observation-grade
correlation only; a causal allocator A/B would require runtime modification
outside capstone scope. The vendored DSpark clone also records a measured
0.99× null for its preallocate-versus-concatenate allocator contrast
(`model.py:67-74`).

There is no paged/block-table cache class in MLX's full cache inventory. A
true paged-KV comparison therefore needs vLLM on the 3080 Ti or a llama.cpp
leg. The present vLLM integration is fixture-first, so this is runtime work
plus **NEEDS-WEB**, not simple harness glue. The lane's verdict is: keep the
flat-pool row disposed; prioritize the four existing riders; at most attach one
non-canonical 2×2 interaction rider to `C5-2.11`. Lane enrichment is low.

### Harness difficulty

Cache identity is not covered by the landed AXI-SA surface: “cache” appears
zero times across `docs/contracts/token_normalization.md`,
`joulewise/axi_decode_config.py`, and `joulewise/schemas.py` in the lane's
inspection.

1. **Config identity (session-sized):** add a frozen `CachePolicy`, patterned
   after `SpeculationPolicy` / `BatchPolicy`
   (`joulewise/axi_decode_config.py:216-298`), with requested and realized
   cache class/mode, `kv_bits`, `kv_group_size`, `quantized_kv_start`,
   `max_kv_size`, rotating keep, and a per-layer realized-cache-class digest.
   The digest is necessary because model-owned `make_cache()` can override the
   request. Parse it beside batch/speculation in `joulewise/schemas.py:924-970,
   1073-1082` and validate it beside the existing speculation check
   (`axi_decode_config.py:650-665`) through additive/versioned dispatch, not a
   silent change to frozen v1. Cache policy is run/request identity, so no new
   event counter is required.
2. **Allocator sidecar (session-sized):** the MLX adapter already snapshots
   active/cache/peak memory during prepare and cleanup
   (`joulewise/adapters/mlx_runtime.py:_memory_snapshot`, about lines 731-745).
   Measured-window sampling still needs overhead characterization.
3. **Persistence/replay (multi-session):** the Stage 3.0.1 spike already
   performs fresh-process save/load/trim with exact replay and about 0.02%
   cache-byte prediction error (`scripts/spike_mlx_prompt_cache.py` and
   `docs/stream_logs/2026-07-07-kv-spike-301/spike_report_1024.json`,
   `replay_supported`). Claim-grade integration is not a new subsystem.
4. **Paged KV or allocator modification:** new subsystem, fenced by D-070's
   single-Q4 posture.

### Feasibility — Mac/MLX versus CUDA

**Mac/MLX:** quantized and evicting/rotating legs are runnable now without
runtime modification. In mlx-lm 0.31.3 the public generate path exposes the
four cache controls (`generate.py:299-345,657-714`);
`models/cache.py:15-40` dispatches prompt-cache construction;
`cache.py:43-111` saves, loads, and trims caches; public `batch_generate` uses
`BatchKVCache`; and the server path uses `LRUPromptCache` (`PromptTrie` remains
internal). Installed MLX 0.31.2 exposes the allocator readings and limits.

The verified constraints are binding: quantized and rotating caches cannot be
combined; speculation drops `max_kv_size`; and model-owned cache builders can
bypass it. A quantized-KV design must use the default `KVCache` path and may
not combine eviction or speculative decoding in the same cell.

**3080 Ti / CUDA:** vLLM PagedAttention is the only identified true paged
route. The repository's vLLM integration is fixture-first and awaits live
promotion (`TASK_QUEUE.md`, approximately row 351); neither vLLM nor llama.cpp
is installed locally. Qwen3-4B fit under vLLM's 12 GiB limit and llama.cpp
cache portability are **NEEDS-WEB** plus a node probe. AMD has no adapter and
is outside the D-073 fleet.

Upstream MLX “flat KV pool” roadmap claims are **NEEDS-WEB** because the
referenced web memo is missing. The vendored DSpark tree grounds only its
0.99× allocator null and `--kv-bits 8` usage.

### Draft candidate registry wording

> **Draft — `C5-2.11a`.**
> **Question:** “Does KV-cache quantization's gross-energy effect interact with
> weight precision in a frozen MLX 2×2 (`kv_bits` × weight-quant) long-context
> design on the pinned primary model?”
> **Ceiling:** “L2, named MLX/model/workload cells only; rider attached to
> `C5-2.11`, not a standalone row.”
> **Forbidden upgrade:** “No quality-neutrality, cross-runtime, or main-effect
> claim without output-divergence reporting (`C-023-QUALITY-EQUIV-QUANT`),
> complete 2×2 cells, and floor clearance; no combination with rotating cache
> or speculative-decoding cells (both incompatible with quantized KV in
> installed mlx-lm 0.31.3, `cache.py:551-552` / `generate.py:709-713`).”

### Risks

1. D-078 clause 11 makes the instrument attribution-limited at about 1 J, with
   an effective bar near the floor plus roughly 5 J claim-side. Short-context
   cache deltas may be unresolvable; designs need long contexts where KV
   bandwidth matters and remain floor-gated on P2-015.
2. Quantized KV changes logits. `C-023-QUALITY-EQUIV-QUANT`-style output-
   divergence evidence is mandatory before efficiency wording. Eviction
   changes outputs by construction, so adjacent `C5-2.12` contrasts must be
   work-matched and chunked, never called output-matched or per-token-
   attributed.
3. Quantized+rotating is unavailable, speculative decode drops
   `max_kv_size`, and model-owned `make_cache()` overrides requests. Realized
   cache classes must be recorded or mislabeled cells can validate silently.
4. Flat-pool/allocator work has a causal gap that only a runtime-modification
   A/B can close. Re-minting `RQ-KV-POOL-OBSERVABLES` without intervention
   capability would contradict the 2026-07-17 ruling and D-041/D-070.
5. The paged leg lacks live vLLM promotion; 12 GiB fit and llama.cpp
   portability remain **NEEDS-WEB**.
6. The missing web memo leaves all upstream-roadmap claims **NEEDS-WEB**.

## Axis 5 — Sparse feed-forward networks beyond MoE routing

### Summary

This axis covers activation sparsity or “ReLU-fication” and contextual
sparsity in the Deja Vu / PowerInfer family. It is conceptually distinct from
the existing dense/MoE rows, but Apple-silicon feasibility is unproved. The
inspected mlx-lm Qwen3 model in the vendored environment uses conventional
dense gate/up/down projections, so zero activations do not skip computation
and cannot create the proposed energy mechanism. Current upstream MLX,
mlx-lm, llama.cpp/Metal, and ProSparse/PowerInfer-Metal support is
**NEEDS-WEB**. The surviving local evidence is
`docs/process_traces/2026-07-17-dspark-dflash-smoke/` and the vendored clone;
the earlier identification web memo is missing.

The clone `/Users/edr/code/mlx-dspark-vendor` is EAGLE-family speculative
decoding (`README` lines 6 and 22), not FFN sparsity. These axes must not be
conflated.

Sparse FFN also does not reduce to `C5-1.1` (active-parameter scaling across
dense/MoE, bank line 591) or `C5-1.9` (MoE versus dense energy per correct
answer, bank line 689). Those hold sparsity fixed within each model; token-
conditioned neuron activation and predictor overhead are new questions.

Identifiability is shadow-only. The instrument can observe whole-request and
phase-window gross energy, tokens/s, and J/committed-token under AXI-SA. Real
compute skipping could move decode-window energy and throughput, but there is
no per-layer or per-operation view. Runtime density counters would be
structural metadata that can license an L2 whole-window contrast; they can
never support “joules per layer.” Without a verified skipping runtime, the
axis collapses into the stack-versus-stack shadow already partly covered by
`C5-1.8`.

### Harness difficulty

Already landed: request lifecycle, prefill/decode windows, emitted-token
counts, gross energy and gross J/committed-token normalization
(`docs/contracts/token_normalization.md`, `joulewise/schemas.py`), plus AXI-SA
speculation and batch identities/counters (`SpeculationPolicy`, `BatchPolicy`
in `joulewise/axi_decode_config.py`). There is no sparsity condition,
provenance, or counter surface. The only AXI-emitting adapter is the non-live
fixture `joulewise/adapters/mock_spec_runtime.py`; the live
`joulewise/adapters/mlx_runtime.py` has none.

- A black-box sparse-versus-forced-dense comparison needs a sparsity condition
  and provenance identity plus an adapter for an existing external sparse
  runtime. This is session-to-multi-session work, conditional on the runtime
  existing.
- Runtime-observed activation density, selected-neuron counts, predictor
  overhead counters, and their validation are multi-session.
- Sparse Metal kernels or a PowerInfer-like MLX runtime are a new subsystem,
  outside the D-078 no-instrument-program spirit and the P1-first posture.

Powermetrics exposes CPU/GPU/ANE rails, never layers or operators
(`joulewise/adapters/powermetrics.py`); harness work cannot buy per-layer
attribution.

### Feasibility — Mac/MLX versus CUDA

**Mac/MLX:** not demonstrated. The inspected Qwen3 model file uses dense
gate/up/down projections. The vendored DSpark/DFlash clone is speculative
decoding, not sparse FFN. Current contextual-sparsity support in MLX/mlx-lm and
activation-sparsity support in llama.cpp/Metal are **NEEDS-WEB** because the
identification memo no longer exists.

**3080 Ti / CUDA:** the plausible nearer-term route because PowerInfer and
Deja Vu reference implementations target CUDA. Repository currency,
Ampere/12 GiB compatibility, and usable sparse-trained artifacts are all
**NEEDS-WEB**. D-073 names the 3080 Ti as the authorized CUDA target.

**AMD/other:** support is **NEEDS-WEB** and outside the ratified fleet; it would
route through cross-ISA row `C5-3.3` (`docs/research_question_bank.md:1027`).
Jetson is optional under D-073 and does not define the fleet.

### Draft candidate registry wording

> **Draft — `C5-1.13`.**
> **Question:** “Does the same sparse-trained artifact consume less gross
> request/decode-window energy when a pinned Mac runtime verifiably skips
> inactive FFN work versus a forced-dense execution path?”
> **Ceiling:** “L2 same-artifact, stack-conditioned pair on the named M3 Max /
> powermetrics SoC-rail boundary; conditional row — inert until a compute-
> skipping Mac runtime is verified (**NEEDS-WEB**).”
> **Forbidden upgrade:** “No ‘activation zeros reduce FLOPs/energy’ claim
> without runtime-skip evidence; no architecture-general or runtime-agnostic
> sparsity claim. NOTE: bank lines 685-686 already use the phrase ‘not a new
> C5-1.13 thesis’ for the D-075 kernel rider — mint this ID with an explicit
> disambiguating note or renumber.”

> **Draft — `C5-2.15`.**
> **Question:** “On the 3080 Ti, does contextual-sparsity execution (predictor
> + sparse FFN, PowerInfer/Deja-Vu-class) beat forced-dense execution in gross
> energy per request and per committed token at matched output?”
> **Ceiling:** “L2, one runtime/one artifact/one device; predictor overhead
> reported as part of the measured whole, never subtracted out.”
> **Forbidden upgrade:** “No general PowerInfer/Deja Vu efficiency claim, no
> architecture-class claim, no claim net of predictor overhead.”

> **Draft — `C5-2.16`.**
> **Question:** “At fixed token shape, does runtime-reported selected-neuron/
> head density explain residual per-request energy or throughput variance
> across prompts?”
> **Ceiling:** “L2 association only, with density counters ingested as
> structural metadata (runtime-reported, not instrument-observed).”
> **Forbidden upgrade:** “No causal per-layer energy attribution (‘joules per
> layer’), no content-general claim, no treatment of runtime counters as
> measured energy evidence.”

### Risks

- The axis needs both a fleet runtime that really skips work and compatible
  sparse-trained artifacts. Both remain **NEEDS-WEB**.
- The central scientific failure is mistaking activation zeros for avoided
  compute. Dense kernels over sparse activations produce no skipping effect.
- Shadow-only identifiability leaves predictor overhead, output divergence,
  and kernel-path changes inside the one whole-request observable.
- `C5-1.13` collides with the bank's D-075 wording at lines 685-686; the
  synthesis therefore says **do not mint** it.
- Without runtime counters this becomes ordinary `C5-1.8` stack-versus-stack
  work and adds no new askable question, limiting P1/P2 value to a labeled
  candidate rather than a measurable program.

## Axis 6 — Unified kernel APIs and shared runtime logic

### Summary

The evaluation splits this axis in two. A real NVIDIA-versus-AMD or unified-
kernel claim is post-capstone and currently unreachable: D-073 fixes the fleet
at a 128 GiB M3 Max plus a 12 GiB 3080 Ti (Jetson optional), and the repository
has neither AMD hardware nor an AMD telemetry adapter.

The reachable reduction is narrower and scientifically cleaner: on the
3080 Ti, hold the runtime, CUDA execution backend, silicon, artifact,
scheduler, and telemetry boundary fixed while changing only an observed
kernel path — for example attention-backend selection, CUDA graph capture
on/off, or Triton-generated versus vendor kernels. On the current single-
vendor fleet this is “same runtime and backend, different kernel path,” not
“different backend.” A true CUDA-versus-ROCm experiment requires AMD silicon.

This refines the existing D-075 `C5-1.8` kernel-provenance rider
(`docs/research_question_bank.md:679-687`). That rider's llama.cpp-CUDA versus
vLLM comparison is stack-versus-stack, confounded by scheduler and artifact
format. A within-runtime kernel-path contrast removes those confounds and is a
better causal control under Q4. It remains gated on `P1-006` live promotion
(`TASK_QUEUE.md` E6/A23, currently gated `[ED-EXTERNAL]`) and **NEEDS-WEB**
confirmation that vLLM on Ampere exposes stable, selectable, and observed
kernel/graph controls.

The instrument-support half already lives in the `C5-3.3` D-075 backend-
provenance rider: record CUDA/Metal/HIP targets and kernel-library identities
now. The cheap, paper-safe action is structured requested-versus-resolved
provenance, not a new thesis and not `C5-1.13`. The missing DSpark/DFlash web
memo did not affect this lane.

### Harness difficulty

Already covered in `joulewise/schemas.py`: `RuntimeBackend` values
`mock/mlx/vllm/llama_cpp/hailo`; `TelemetryBackend` values
`mock/powermetrics/nvidia_smi/jetson_rails/wall_meter`; and
`HardwareTarget` requiring both (lines 207-221 and 764-784).
`DraftModelIdentity` carries runtime backend/version
(`joulewise/axi_decode_config.py:144-170`). The stack-provenance table in
`docs/contracts/token_normalization.md` already asks for runtime/version and
kernel/library “where known,” but kernel provenance is free-form, and serving
runtime is not separated from execution backend.

Needed surface and size:

1. **Structured kernel identity (session):** runtime name/version/build,
   execution API (`metal/cuda/rocm/unknown`), requested and resolved attention
   backend, graph-capture mode, and kernel-library IDs, each labeled
   `observed`, `requested_only`, or `unavailable`. A CLI flag is never an
   observed identity.
2. **Execution-backend vocabulary (bench):** a separate execution-backend
   field plus a `rocm_smi`-class telemetry enum. Do not add `rocm` to
   `RuntimeBackend`; that would conflate a serving stack with its execution
   backend and destroy the intended control.
3. **vLLM population (session, then multi-session when live-verified):** record
   resolved identities from the adapter.
4. **AMD telemetry adapter (new subsystem, hardware-gated):** raw custody,
   parser, boundary semantics, and floors.
5. **llama.cpp gap (new subsystem today):** although enum-listed,
   `joulewise/adapters/__init__.py` resolves only MLX and vLLM, so the current
   `C5-1.8` llama.cpp leg is not runnable through the harness.

Additive metadata is cheap under D-066/D-070; telemetry adapters are not.

### Feasibility — Mac/MLX versus CUDA

**Mac/MLX:** the MLX and powermetrics adapters are end-to-end and record
MLX/mlx-lm/transformers versions plus artifact identity. The repository exposes
no alternate MLX execution backend or selectable kernel path, so the Mac leg
is provenance capture only. Any MLX cross-vendor portability claim is
**NEEDS-WEB**.

**3080 Ti / CUDA:** remote vLLM runtime, nvidia-smi telemetry, and SSH transport
exist in code; `joulewise/adapters/__init__.py` lists implemented runtime
backends `mock/mlx/vllm` and telemetry backends
`mock/powermetrics/nvidia_smi`. But `P1-006` telemetry access remains gated
`[ED-EXTERNAL]` and P2-005/2K live promotion remains open, so no live 3080 Ti
JouleWise run is repository-proven. llama.cpp-CUDA has no resolver branch.
Stable selectable and observable vLLM attention-backend, CUDA-graph, and
Triton-versus-vendor controls on Ampere are **NEEDS-WEB**.

**AMD/other:** impossible on the current fleet. It needs an AMD unit, a mature
runtime and kernel path (vLLM-on-ROCm, llama.cpp-HIP, and Triton-AMD are all
**NEEDS-WEB**), and a new characterized telemetry subsystem. `C5-3.3` already
frames the post-capstone cross-ISA study around the adapter contract.

### Draft candidate registry wording

> **Draft — `C5-1.8 within-runtime kernel-path amendment (second rider on C5-1.8; per the D-075 precedent this is an amendment, NOT a new C5-1.13 thesis)`.**
> **Question:** “On the 3080 Ti with one vLLM (or llama.cpp) build, model
> artifact, scheduler policy, workload, and telemetry boundary held fixed, do
> predeclared and runtime-observed kernel/attention/graph-capture modes produce
> an above-floor gross-energy contrast?”
> **Ceiling:** “L2 named-stack, same-silicon characterization; gated on
> `P1-006` live promotion plus **NEEDS-WEB** confirmation of selectable,
> observable kernel controls on Ampere.”
> **Forbidden upgrade:** “No ‘energy belongs to the kernel layer’ language, no
> runtime-agnostic kernel claim, no CUDA-to-ROCm or cross-vendor portability
> claim; no result admitted when resolved kernel identity, artifact identity,
> output equivalence, or scheduler policy is uncontrolled (requested flags are
> never observed identity).”

> **Draft — `C5-3.3 backend-provenance rider — extend the EXISTING D-075 candidate (bank ~line 1033) with structured requested-vs-resolved semantics; pure instrument-support, no characterized claim`.**
> **Question:** “Do new bundles record enough observed runtime, execution-
> backend (CUDA/Metal/HIP), kernel-library, attention-backend, graph-mode, and
> telemetry identity — with `observed` / `requested_only` / `unavailable`
> status — that a future audited CUDA/ROCm replication can reuse today's
> Mac/NVIDIA corpus without rerunning it?”
> **Ceiling:** “L0 smoke / L1 feasibility only; instrument-support row, no
> characterized energy claim ever.”
> **Forbidden upgrade:** “No NVIDIA-vs-AMD efficiency statement, no kernel-API
> ranking, no claim that recorded provenance demonstrates backend equivalence;
> adding `rocm` to `RuntimeBackend` is forbidden — execution backend is a
> separate field from serving-runtime identity.”

> **Draft — `C5-3.3 CUDA/ROCm named-unit replication rider — minted now as explicitly DEFERRED post-capstone (hardware-gated)`.**
> **Question:** “For one named runtime build and one artifact on named NVIDIA
> and AMD units with separately boundary-characterized telemetry, do the Q4
> fixed and marginal energy terms differ across the two backend stacks?”
> **Ceiling:** “L2 named-unit, boundary-qualified characterization under D-070;
> unreachable until AMD hardware plus a new characterized telemetry adapter
> exist.”
> **Forbidden upgrade:** “No vendor-class winner, no ‘unified kernel API’
> causal attribution, no scheduler-portability generalization from one unit
> per vendor or from non-commensurate telemetry boundaries
> (powermetrics/nvidia-smi/ROCm-tool boundaries are not automatically
> comparable).”

### Risks

- Kernel-mode flags can also change allocation, graph capture, compilation,
  warmup, and scheduler behavior. Requested backends may silently fall back,
  so only runtime-observed resolved identity is admissible.
- Compilation and graph caches contaminate warm/cold comparisons. Version
  churn can change defaults under identical config text, making exact build
  identity load-bearing.
- Effects below the roughly 1 J attribution limit may yield only “not
  resolvable.”
- llama.cpp versus vLLM remains stack-versus-stack and retains `C5-1.8`'s
  ceiling. Single-vendor data cannot support cross-vendor wording.
- An AMD campaign would compete with the paper-first priority and violate
  D-075's no-new-thesis posture absent a separate Ed hardware/scope commitment.
- Adding `rocm` to `RuntimeBackend` would permanently conflate the identities
  the experiment needs kept separate.
- vLLM Ampere controls, vLLM/llama.cpp/Triton AMD maturity, and AMD hardware
  availability all remain **NEEDS-WEB**.

## Promotion criteria and fold-in boundaries

Promotion means Ed has approved a precise amendment to
`docs/research_question_bank.md` and the corresponding current-state note in
`docs/research_question_registry.md`. It does not mean the row is scheduled or
that it contains claim-bearing evidence. Before any promoted row can support
an experiment, it also needs a predeclared analysis plan, exact stack and
artifact identity, the applicable detection floor, strict-valid evidence, and
the row's named output-equivalence gate.

### Proposed D-075 fold-in, subject to Ed's review

The synthesis directs **refine, do not mint** for the present intake:

- Amend the existing bank riders `C5-2.5a`–`d` at approximately lines
  870-915 for ranks 1, 4, 5, and 8. Update registry row `C5-2.5` and its
  binding `C-023-OUTPUT-IDENTITY` note; do not create four new canonical rows.
- Attach `C5-2.11a` beneath existing bank row `C5-2.11` at approximately line
  966 and update the existing registry `C5-2.11` /
  `C-023-QUALITY-EQUIV-QUANT` notes. It is a rider, not a standalone ID.
- Attach `RQ-AXI-HYBRID-PAIR-Q4RIDER` to existing
  `RQ-AXI-HYBRID-PAIR`; attach the attention/context-slope amendment to
  existing `RQ-KV-GROWTH` / `C5-1.2`.
- Attach the dense/MoE rider to existing `C5-1.1`; attach the MoE×BATCH rider
  jointly to `C5-1.1` and `C5-2.2`, implementing D-070's already-recorded
  candidate rather than creating a new thesis.
- Amend the existing `C5-1.8` kernel rider near bank lines 679-686 and the
  existing `C5-3.3` backend-provenance rider near line 1033. Preserve serving
  runtime and execution backend as separate identities.
- Mint **no new canonical row IDs** from this evaluation.

If Ed accepts that fold-in, the synthesis proposes a future decision-log
sentence under the next free ID, to be verified at intake rather than guessed:
“Extension-axis re-evaluation (2026-08-09) recommends existing-row refinements
for C5-2.5, C5-2.11, RQ-AXI-HYBRID-PAIR, dense/MoE × batch, and kernel/backend
provenance; runtime-unsupported sparse/MTP/AMD work remains deferred or
NEEDS-WEB; no new thesis, campaign, hardware, or scope commitment created.”

### What must be true for each ranked proposal

| Rank | Promotion bar into the bank / registry |
|---:|---|
| 1 | Refine existing `C5-2.5c` only after Ed accepts the pure-method break-even wording. Execution additionally needs a pinned vendor commit and patch/dependency/model identities, a structured per-round callback, a real AXI adapter, exact token-ID output identity, and floor-qualified pure DSpark and DFlash arms. |
| 2 | Attach `C5-2.11a` to existing `C5-2.11` only after Ed accepts the interaction design. Execution needs typed requested-and-realized cache identity, a complete frozen 2×2, long-context cells, no rotating/speculative combination, `C-023-QUALITY-EQUIV-QUANT` divergence evidence, and floor clearance. |
| 3 | Amend existing `RQ-AXI-HYBRID-PAIR` only when a clean named hybrid/pure pair with matching tokenizer, quantization, fit, and executed-kernel identities is locally verified; pair availability is **NEEDS-WEB**. The plan must stay whole-request/coarse-phase and pair-specific. |
| 4 | Refine existing `C5-2.5b` as the rank-1 campaign's secondary only; it needs the same real event adapter and must distinguish verified positions, accepted prefix, committed burst, and DFlash's extra proposal work. |
| 5 | Refine existing `C5-2.5d` as rank 1's mandatory control only; pure-DSpark, lookup-only, and hybrid modes must be frozen, and hybrid results remain aggregate unless a successor contract adds proposal-source identity. |
| 6 | Attach the rider to existing `C5-1.1` only after a same-lineage dense/MoE MLX pair, matched quantization, tokenizer identity, memory fit, and architecture/fallback identity are verified. The MoE artifact remains **NEEDS-WEB** and the claim stays a named-pair Mac result. |
| 7 | Attach jointly to existing `C5-1.1` / `C5-2.2` only after rank 6's pair exists and the static-batch MLX adapter emits live events.v2 group evidence. No per-request allocation of batch-group energy is allowed. |
| 8 | Preserve existing `C5-2.5a` as deferred. Promote wording, not a campaign, only after a prospective cross-mechanism design is affordable and output, tokenizer, target, workload, floor, and mechanism diagnostics are matched. |
| 9 | Amend existing `RQ-KV-GROWTH` / `C5-1.2` only after named GQA/MLA/sliding-window artifacts and their real executed attention paths are verified (**NEEDS-WEB**). Cross-tokenizer comparisons must remain descriptive or use J/char/J/byte, and no module fraction may be inferred. |
| 10 | Amend existing `C5-1.8` only after `P1-006` live promotion and **NEEDS-WEB** confirmation that a pinned Ampere runtime exposes selectable and runtime-observed attention/kernel/graph modes. Artifact, output, scheduler, telemetry boundary, and warm/cold policy must be fixed. |
| 11 | Extend the existing `C5-3.3` provenance rider only after Ed accepts the additive requested-versus-resolved identity contract. It remains L0/L1 instrument support, not an energy question, and `rocm` must not be added to `RuntimeBackend`. |
| 12 | Do not fold now. `C5-2.15` first needs a maintained contextual-sparsity CUDA runtime, a compatible sparse artifact, 12 GiB Ampere fit, real skipping, and whole-stack predictor accounting; all are **NEEDS-WEB**. |
| 13 | Do not mint. Activate the already-preserved `C5-2.5c` MTP contingency only after a successor AXI-SC verdict proves retained heads, an identifiable execution path, and real counters. Keep its frozen family separate from draft-model arms. |
| 14 | Do not fold now. `C5-2.5a/MTP-LOCUS` requires both native MTP and EAGLE-family mechanisms to execute under a prospective matched-output design; it stays post-capstone and cannot claim component energy. |
| 15 | Do not fold now. `C5-2.5e` requires an executable native-MTP arm and runtime-observed counters before any prospectively fixed head/depth policy study is meaningful. |
| 16 | Do not fold now. `C5-2.16` needs a real sparse runtime plus validated selected-neuron/head counters; until then there is no density association to register. Counters remain structural metadata, not measured energy. |
| 17 | Do not mint. A sparse Mac row needs a verified same-artifact skipping-versus-forced-dense path, and the proposed ID collides with D-075's existing “not a new C5-1.13 thesis” wording. Renumbering would itself require Ed's ruling. |
| 18 | Do not fold now. Future CUDA/ROCm replication requires committed AMD hardware, a new characterized telemetry adapter, mature pinned runtime/kernel paths, and boundary comparability. Existing `C5-3.3` already holds the framing. |

Ranks 12-18 therefore remain outside the bank and registry at this intake.
The native-MTP activation in rank 13 is already preserved contingently at
`docs/research_question_bank.md:898-906`; ranks 14-15 are premature; ranks
12, 16, and 17 lack a verified compute-skipping substrate; and rank 18
duplicates existing `C5-3.3` framing while demanding uncommitted hardware.

### Open verification gaps carried forward

The synthesis groups the unresolved web checks as follows; none may be silently
converted into a fact:

1. Clean MLX hybrid/pure, dense/MoE, and GQA/MLA/sliding-window artifact pairs
   with tokenizer, quantization, and fit controls — gates ranks 3, 6, 7, and 9
   (**NEEDS-WEB**).
2. DSpark/DFlash upstream provenance and any maintained CUDA implementation —
   gates ranks 1, 4, 5, and 8 (**NEEDS-WEB**). The identification memo was
   lost; the vendored clone is the available lane-attested external evidence.
3. A successor mlx-lm native-MTP path with retained heads and counters, plus
   MiMo-class 12 GiB vLLM fit — gates ranks 13-15 (**NEEDS-WEB**).
4. Selectable and runtime-observed vLLM kernel/graph controls on Ampere, plus
   sparse runtime/artifact support — gates ranks 10, 12, and 16
   (**NEEDS-WEB**).
5. AMD hardware, runtime, and telemetry maturity — gates rank 18
   (**NEEDS-WEB**).

The next mechanical action is an Ed ruling packet with accept/defer/reject
boxes for each proposed amendment. No edit to the research-question bank,
registry, or decision log should precede that ruling.
