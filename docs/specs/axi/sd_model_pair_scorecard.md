# AXI-SD dense/MoE model-pair scorecard and quantization ladder

Status: **PRE-REGISTERED PROPOSAL — no model pair is selected and D-016 is
not amended.** Owner of the final pair decision: Ed, with the advisor input
required by D-016. This document is desk-work only; it authorizes no model
download, campaign, quiet-Mac use, or claim.

Authority: [AXI handoff S-D](../../axi-handoff.md#s-d--model--quantization-artifact-groundwork-desk-work),
[D-016](../../decision_log.md#d-016-benchmark-model-selection),
[D-070](../../decision_log.md#d-070-architectural-axes-extension-agenda-axi-scope-claim-posture-batch-axis-rulings),
[C-023-QUALITY-EQUIV-QUANT](../../research_question_registry.md), and the
binding [AXI xhigh consult S-D ruling](../../process_traces/2026-07-15-axi-xhigh-consult/response.md#positions).

## 1. Pre-registration boundary and status vocabulary

This scorecard must be frozen before any dense/MoE or quantization energy
result is collected or inspected. Candidate discovery, artifact inspection,
runtime load smokes, memory-fit smokes, and quality-only evaluation may occur
before the freeze; they may not use energy as a selection input. The eventual
freeze receipt must record this document's Git blob hash, the completed
scorecard, the quality-manifest hash, runtime/environment identity, and the
artifact-manifest hashes.

Every cell uses exactly one of these values:

| Value | Mechanical meaning |
|---|---|
| `PASS` | The cited receipt supplies the required value and satisfies the rule. |
| `FAIL(<reason>)` | The cited value violates the rule. |
| `NEEDS-VERIFICATION` | No adequate receipt exists. This is non-passing, not partial credit. |
| `NOT-APPLICABLE` | The criterion does not apply to the declared selection track. |

An unresolved fact never inherits a model-card claim, a repository name, or a
value remembered from public discussion. It remains `NEEDS-VERIFICATION`.
Hashes and revisions must be copied from locally inspected artifacts or APIs;
none may be reconstructed from memory.

There are two separate selection tracks:

1. `d016-cross-target`: this scorecard supplements, and never subsets,
   D-016. It must satisfy all-primary-target execution, the 8 GB fit rule as
   ratified by Ed, the KV-per-token/transfer-range criterion, open-weight
   license and mirroring, the same-family size-axis preference or an explicit
   D-016 disposition of it, and D-016's closure receipts. Passing the
   preselection card makes a pair only `scorecard-eligible`; it does not make
   the pair D-016-finalized.
2. `axi-mac-only`: may be considered only after Ed explicitly permits a
   separate AXI pair. It is evaluated on the same scorecard, but runtime and
   memory gates cover the named Mac stack only. It does not close or weaken
   D-016 and cannot support a cross-target claim.

For `d016-cross-target`, final promotion additionally requires a closure
receipt citing: P1-001 supervisor scope notes; successful Mac MLX and CUDA
loads as required by D-016's minimum closure evidence; successful
load/generation on every additional primary target/runtime, including the
GGUF/llama.cpp path; exact artifact paths and immutable revisions for every
primary runtime; the selected quantization; and a KV-size table row that
reports bytes/token and payload sizes across the planned transfer-length
range. The receipt must show how that range is both small enough to span
multiple transfer cells and large enough to exercise the interconnect under
D-016. Because D-016 does not yet state numeric bounds for "interesting
range," that disposition is Ed-owned and must be cited rather than invented
here.

## 2. Frozen estimand and matching rule

The primary estimand is the within-family difference between one dense model
and one MoE model with similar **active inference parameter capacity**, under
the same tokenizer, output policy, runtime build, quantization recipe,
workload manifest, and measurement boundary. It is a pair-specific
architecture contrast, capped at L2 by D-070; it is not a general claim that
MoE is more or less efficient than dense inference.

### 2.1 Active-parameter calculation

The calculation is based on an auditable tensor-path ledger and measured
routing, not a model name's rounded `A<n>B` label or a self-reported config.
Every unique tensor loaded for inference must occur exactly once in this
exhaustive class enum:

| Class | Included tensors | Activity treatment |
|---|---|---|
| `embeddings` | Token and learned position/type embeddings. | Always-active module capacity. |
| `attention` | Query/key/value/output projections and any learned attention parameters. | Always active. |
| `dense_mlp` | Non-expert feed-forward projections, including biases. | Always active. |
| `expert_mlp` | One identified routed expert's feed-forward tensors. | Active only when that expert is actually dispatched. |
| `router` | Router/gate projections, learned routing biases, and group-selection tensors. | Always active. |
| `shared_experts` | Expert tensors executed for every token regardless of routing. | Always active. |
| `norms` | All learned normalization weights and biases. | Always active. |
| `head` | Untied output heads and other loaded inference heads. | Always active. |

Optimizer state and files not loaded by the inference graph are outside the
inference inventory. A loaded tensor that cannot be assigned to exactly one
class is `FAIL(unclassified_tensor)`; an assignment to multiple classes is
`FAIL(duplicate_classification)`. Tied tensors have one canonical path and
alias paths. The ledger records tensor path, aliases, shape, dtype, scalar
count, class, layer, expert ID where applicable, and the source-code/module
path that justifies the class. Class subtotals plus tied-alias reconciliation
must equal the runtime-loaded unique tensor total.

Let `A` be the unique parameter total for `embeddings`, `attention`,
`dense_mlp`, `router`, `norms`, and `head`; `S_l` the `shared_experts` total in
MoE layer `l`; and `E_lj` the `expert_mlp` total for routed expert `j` in layer
`l`.

Routing is derived on the frozen probe suite `axi-sd-router-probe-v1`. That
suite is exactly the prompt-token sequences of all 256 items in
`axi-sd-quality-screen-v1`, ordered by ascending item ID and capped at the
first 512 prompt tokens per item. It is run as teacher-forced prefill at batch
1 with no generated tokens and no cache reuse. The two suite manifests and
token-ID digest must be frozen before any candidate probe runs.

For every probe token and MoE layer, the receipt records the post-constraint
set of experts actually dispatched after group selection, capacity handling,
fallbacks, dropped-token handling, and every routing stage. Pre-router logits
and self-reported `top_k` are diagnostics only. Define `R_lx` as the actual
dispatched expert set for probe token `x`, `k_l^probe = max_x |R_lx|`, and:

```text
routed_capacity_l = max_x(sum_{j in R_lx}(E_lj))
```

This deterministic maximum over observed valid dispatch combinations replaces
the earlier "largest valid combination" rule. Empty, truncated, or
unreconciled routing traces are `FAIL(routing_probe_incomplete)`. A config that
claims a different top-k from measured dispatch is recorded as a discrepancy
and cannot override the trace.

The scorecard value is a module-capacity count:

```text
P_active_dense = P_inference_total_dense

P_active_moe = A
             + sum_l(S_l)
             + sum_l(routed_capacity_l)
```

The following counting rules are binding:

- Shared experts are always included; they are never hidden inside a rounded
  advertised active-parameter figure.
- Router/gate parameters are included in `A`. A loaded auxiliary inference
  head is classified as `head`, not silently excluded.
- Tied tensors are counted once by storage identity. Untied embedding and
  output-head tensors are counted separately.
- KV cache, activations, allocator reservations, and runtime buffers are not
  parameters; they belong in the memory gate instead.
- For equal-sized experts, the measured routed term reduces to
  `k_l^probe * E_l`. Grouped, unequal, multi-stage, capacity-limited, or
  dynamic routers use the measured maximum above; no config-only shortcut is
  permitted.
- An incomplete probe trace has exactly the
  `FAIL(routing_probe_incomplete)` disposition defined above; it is never
  `NEEDS-VERIFICATION`. Unknown shared-expert execution or a missing
  exhaustive tensor ledger remains `NEEDS-VERIFICATION` and cannot pass G3.
- The receipt must include the inventory script revision, source artifact
  revision, tensor-path ledger, per-class subtotals (`A`, every `S_l`, every
  `E_lj`, every `k_l^probe`), routing-probe manifest/digest, total inference
  parameters, and reconciliation to the runtime-loaded tensor total.

Define the symmetric active mismatch:

```text
d_active = 2 * abs(P_active_dense - P_active_moe)
           / (P_active_dense + P_active_moe)
```

The primary active-match gate is `d_active <= 0.30`. The threshold may not be
widened after quality, memory, or energy results are known.

### 2.2 Matched-total fallback is a different estimand

If no active-matched pair passes, a same-family pair with symmetric total
parameter mismatch `d_total <= 0.10` may be proposed only as
`matched-total/different-estimand`. Its estimand is an architecture contrast
at similar stored model capacity, while conditional compute is intentionally
unmatched. It must have a separate pair ID, analysis row, figure label, and
claim sentence. It may not be pooled with, renamed as, or silently substituted
for the active-matched contrast.

## 3. Fixed comparison identity

### 3.1 Family, tokenizer, and tuning state

Both arms must have:

- the same declared release family and generation;
- byte-identical tokenizer files and special-token maps, proved by the
  tokenizer-subtree manifest hash;
- the same base versus instruction-tuned state; and
- the same chat template bytes, BOS/EOS insertion, and prompt token IDs.

A shared brand with differing tokenizer or template hashes is `FAIL`, not
"close enough." Prompt token IDs for every quality and campaign item must be
materialized and hash-bound.

### 3.2 Runtime and quantization identity

Within each target cell, both arms use the same runtime package/build, backend,
device, load flags, kernel policy, cache dtype, and generation flags. The
candidate set uses one frozen recipe set, `axi-sd-selection-quant-set-v1`,
across **all pairs**. It is not chosen pair-by-pair:

| Runtime cell | Frozen candidate-set recipe |
|---|---|
| MLX | BF16 source; affine groupwise INT4 weights; group size 64; FP16 scales/bias terms. |
| GGUF/llama.cpp | Same BF16 source; `Q4_0` weight type; block size 32. |
| vLLM/CUDA | Same BF16 source; AWQ W4A16; group size 128; zero-point enabled; FP16 activations. |

For every runtime, the semantic module policy is identical: quantize weight
matrices classified as `attention`, `dense_mlp`, `expert_mlp`, or
`shared_experts`; retain `embeddings`, `router`, `norms`, and `head` in BF16;
retain all biases in BF16. Tied embedding/head storage follows the embedding
rule. The converter executable revision, package/environment lock, rounding
mode, scale/bias storage convention, and ordered module-path allowlist are
filled once in the candidate-set freeze manifest before **any** candidate is
converted, quality-screened, or memory-tested. They then apply to every pair.
A tensor shape or runtime that cannot implement this frozen recipe yields
`FAIL(selection_recipe_unsupported)`; it does not permit a recipe change.

For `d016-cross-target`, this identity is checked separately for MLX, GGUF /
llama.cpp, and vLLM-loadable CUDA artifacts. Cross-format bytes need not be
identical, but within each runtime the dense and MoE artifacts must derive from
the frozen source revisions by the same semantic recipe. For `axi-mac-only`,
only the pinned MLX cell is in scope. A pair of unrelated community
conversions at the same advertised bit width does not pass recipe identity.

Canonicalize the completed candidate-set recipe manifest as UTF-8 JSON with
sorted keys and no insignificant whitespace, then record its SHA-256 as
`selection_recipe_digest`. G4 through G10 are joined by this exact key:

```text
selection_join_key = (
  selection_recipe_digest,
  dense_artifact_root_digest,
  moe_artifact_root_digest,
  runtime_environment_digest,
  output_policy_digest,
  selection_evidence_plan_digest
)
```

The hash-bound selection-evidence plan maps each evidence role to its own
frozen workload digest (`runtime_smoke`, `routing_probe`, `quality_screen`,
and `memory_fit`), so G9 and G10 need not pretend to use the same workload.
Every G4–G10 receipt must carry the identical join key for its pair/runtime
cell plus its evidence-role name and workload digest. The latter must equal
the matching entry in the joined plan. Quality or memory evidence produced
from a different artifact, recipe, runtime, output policy, plan, or role-bound
workload digest is non-joining and cannot pass the card.

### 3.3 Output policy

Selection and quality screening use `axi-sd-greedy-eos128-v1`:

| Field | Frozen value |
|---|---|
| decoding | greedy; sampling disabled |
| output cap | `max_new_tokens = 128` |
| minimum output | zero additional tokens |
| termination | first model EOS or the 128-token cap |
| stop strings | none beyond the tokenizer's frozen EOS set |
| batch mode | singleton, no prompt cache reuse |
| state | fresh request state; identical system prompt and chat template |

Temperature/top-p/top-k values must be absent when the runtime supports a
sampling-disabled mode; a runtime that requires inert values must record those
exact values in normalized config. For every pair, report output-token count,
stop reason, output-token SHA-256, and dense/MoE exact-token-identity rate.
Fixed output policy is not fixed decoded work, so divergence is always visible.

## 4. Hard-gate scorecard

Complete the following card for each candidate pair. G1–G11 must be `PASS`
before the pair can enter the selection ranking. G12 is the post-ranking,
Ed-owned finalization gate: until it passes, a winner remains a proposal and
D-016 remains open. G4–G10 additionally fail unless their receipts carry one
identical §3.2 `selection_join_key`.

| ID | Gate | Mechanical pass rule | Required receipt |
|---|---|---|---|
| G1 | Family/tuning | Same release generation and same base/instruct state. | Source configs and model-card snapshots at exact revisions. |
| G2 | Tokenizer/template | Tokenizer-subtree and chat-template hashes are byte-identical; all prompt-token hashes match. | Per-file SHA-256 manifest and tokenization receipt. |
| G3 | Active match | Exhaustive tensor ledger and fixed routing probe follow §2.1 and `d_active <= 0.30`. | Ledger, routing trace, inventory output, and reconciliation totals. |
| G4 | Runtime parity | Both arms load and generate in the identical pinned runtime cell(s), with identical flags except artifact path/model architecture; join key matches G5–G10. | Environment lock, join key, and successful load/generation receipts. |
| G5 | Candidate-set quant recipe | The one §3.2 recipe set is used across every candidate; join key matches G4/G6–G10. | Candidate-set recipe manifest/digest, converter logs, and join key. |
| G6 | Output policy | Normalized configs equal `axi-sd-greedy-eos128-v1`; prompt-token hashes and join key match. | Config, output-policy digest, and join key. |
| G7 | Artifact identity | Every source and derived artifact has an exact immutable revision and per-file SHA-256 manifest; joined root digests match G4–G10. | Artifact manifests, root hashes, and join key. |
| G8 | License/mirror | License permits academic benchmarking and local mirroring; both immutable local mirrors verify the joined artifact digests. | License snapshot/hash, mirror verification receipt, and join key. |
| G9 | Quality band | The frozen quality screen in §4.1 passes on the joined artifacts/workload. | Quality manifest, raw item scores, deterministic summary, and join key. |
| G10 | Memory headroom | **PROPOSED-FOR-ED:** every target required by the track passes the ratified §4.2 rule on the joined artifacts and fixed shape. | Ed ruling, per-target peak-memory/load receipt, and join key. |
| G11 | D-016 KV/transfer range | For `d016-cross-target`, exact KV bytes/token and payloads across planned transfer lengths satisfy Ed's recorded "interesting range" disposition; Mac-only track is `NOT-APPLICABLE`. | Hash-bound KV-size table, derivation, transfer-length cells, and Ed disposition. |
| G12 | D-016 closure | For `d016-cross-target`, all D-016 closure evidence in §1 is complete and D-016 records the selection; for Mac-only, Ed's separate-pair authorization and claim boundary are recorded. | D-016/Ed ruling plus supervisor, load, artifact, and KV receipts named in §1. |

### 4.1 Pair quality-band rule

Before model outputs are produced, freeze an `axi-sd-quality-screen-v1`
manifest with 256 license-compatible, answer-keyed items: 64 each from four
declared strata.
The manifest must contain exact item IDs and content hashes, prompt-token
hashes, deterministic answer normalization, and a binary `0/1` scorer; no LLM
judge or post-output item exclusion is allowed. The four strata and their
source revisions must be named in that manifest before either candidate runs.

For model `m`, `Q_m` is the unweighted mean of the four stratum accuracies.
The pair passes G9 only if:

```text
abs(Q_dense - Q_moe) <= 0.05
and
max_s(abs(Q_dense,s - Q_moe,s)) <= 0.10
```

Both arms must complete all 256 items under §3.3. Any invalid/missing item is
scored zero for that arm. Report the point values, paired item table, exact
token identity rate, output lengths, and stop-reason distribution. This is a
selection comparability band, not a capability or intelligence claim.

### 4.2 Memory-headroom rule

**Status: PROPOSED-FOR-ED; not a ratified D-016 threshold.** D-016 requires
8 GB fit with KV headroom but owns the final constants and measurement rule.
G10 cannot be marked `PASS` unless Ed accepts this proposal or records a
replacement rule in D-016. Candidate results may not be used to choose between
thresholds.

Proposed fixed fit shape `axi-sd-memory-fit-shape-v1` is batch 1, an exact
8,192-token prompt, and **exactly 128** greedily decoded tokens, with an empty
KV cache at request start and no prefix/prompt cache reuse. The `memory_fit`
role overrides only the natural-EOS termination in
`axi-sd-greedy-eos128-v1`: MLX masks every frozen EOS token ID with a
hash-bound logits processor through decode step 127; llama.cpp uses
`--ignore-eos -n 128`; and vLLM uses
`SamplingParams(ignore_eos=True, min_tokens=128, max_tokens=128)`. The exact
runtime mechanism, normalized arguments, and MLX processor source hash are
recorded in the joined selection-evidence plan before any smoke. A runtime
that stops for EOS or any other non-error stop before token 128 yields
`FAIL(memory_probe_short_decode)`; its shorter peak is never accepted.

The exact 8,192 prompt token IDs and SHA-256 are frozen in the workload
manifest before any memory smoke. The smoke begins before model load and ends
after completion of decode token 128. No CPU offload, swap, expert streaming,
or target-specific layer dropping is allowed.

For target `t`, proposed `C_t` is the runtime-usable device/unified-memory
capacity recorded immediately before load, capped at 8 GiB for each D-016
8 GB-class target. Proposed `M_peak,t` is the maximum total resident memory
attributable to the inference process from load start through completion,
including weights, KV, activations, workspaces, and allocator reservations.
The pre-output fit manifest must name and version the target-specific
allocator/device counter; the same counter and sampling cadence apply to every
candidate on that target. The receipt records the complete time series, not
only a reported maximum.

The proposed decision rule is:

```text
H_t = C_t - M_peak,t
PASS iff H_t >= max(1 GiB, 0.15 * C_t)
```

The proposal uses three fresh-process load/generation smokes and the worst
`M_peak,t`. The receipt records joined artifact digests, weight bytes,
context/KV settings, counter/cadence, target identity, each peak, failures,
and any allocator warnings. A raw quantized-weight size that exceeds the
ratified allowed peak is `FAIL(weight_lower_bound)` without a smoke. The
Mac-only track uses the named Mac's actual `C_t`; the 15%/1 GiB reserve applies
there only if Ed ratifies it for that track as well.

## 5. Selection algorithm and fallback hierarchy

Energy is absent from the algorithm.

1. Obtain Ed's G10 memory-rule ruling, then mark G1–G11 from joined receipts.
   `NEEDS-VERIFICATION` is non-passing.
2. Partition candidates by declared track. Do not use Mac evidence to pass a
   D-016 CUDA/GGUF cell.
3. Retain only active-matched candidates with G1–G11 all `PASS` (or
   `NOT-APPLICABLE` only where the card explicitly permits it).
4. Rank survivors by the ascending tuple
   `(d_active, worst_t(M_peak,t / C_t), abs(Q_dense - Q_moe), pair_id)`.
   The final lexical `pair_id` element makes ties deterministic.
5. Present the first survivor and all receipts to Ed. The ranking is a
   proposal; Ed still owns D-016 and the separate-pair decision. The pair is
   not final until G12 passes.
6. If there is no survivor, request the Ed decision in §7. Do not widen a
   threshold.
7. Only after explicit Ed option-D authorization may the
   `matched-total/different-estimand` fallback be scored with G1–G11 and
   ranked by
   `(d_total, worst memory ratio, quality gap, pair_id)`.
8. If neither estimand has an eligible pair, record `no_eligible_pair`; do not
   promote the least-bad failure.

## 6. Candidate shortlist — desk application

Every entry below is an explicitly `NEEDS-VERIFICATION` discovery hypothesis
from model-release names recalled without primary receipts. The names do not
assert current availability. Repository IDs, existence of matching tuning
variants, architecture figures, tokenizer equality, licenses, revisions,
runtime support, artifacts, and hashes all remain unverified. Approximate
advertised counts are conditional arithmetic inputs only, not accepted facts.

| Pair ID | Dense / MoE discovery hypothesis | Active-match precheck | G1–G2 | G3 | G4–G8 | G9 | G10 | G11 | G12 | Current disposition |
|---|---|---|---|---|---|---|---|---|---|---|
| `olmo-1b__olmoe-1b7b` | `NEEDS-VERIFICATION`: AllenAI OLMo 1B generation / OLMoE named as 1B-active, 7B-total; exact repositories and matching variants unverified. | `NEEDS-VERIFICATION`: recalled names suggest about 1B vs 1B active; expert count, measured dispatch, and shared-expert layout unverified. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` for all five gates and the common join key. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION`; a conditional roughly 7B total does not establish 4-bit fit. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` | **Unscored discovery hypothesis; not selected.** |
| `qwen3-4b__qwen3-30b-a3b` | `NEEDS-VERIFICATION`: Qwen3 names 4B / 30B-A3B; exact repositories, availability, and matching instruction/base variants unverified. | `NEEDS-VERIFICATION`: recalled names suggest about 4B vs 3B active, near the 0.30 gate; measured dispatch and shared experts unverified. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` for all five gates and the common join key. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION`; if approximately 30B total is verified, 4-bit weight arithmetic alone is about 15 GB and would imply `FAIL(weight_lower_bound)` for D-016. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` | **Unscored discovery hypothesis illustrating the potential D-016 conflict; not selected.** |
| `qwen1.5-4b__qwen1.5-moe-a2.7b` | `NEEDS-VERIFICATION`: Qwen1.5 names 4B / MoE-A2.7B; exact repositories, availability, and matching instruction/base variants unverified. | `NEEDS-VERIFICATION`: recalled names suggest about 4B vs 2.7B active; if exhaustive measurement confirms those values, `d_active` is about 0.39. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION`; becomes `FAIL(active_mismatch)` only if measured §2.1 values confirm the conditional calculation. | `NEEDS-VERIFICATION` for all five gates and the common join key. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION`; a recalled roughly 14B total does not establish 8 GB fit or failure. | `NEEDS-VERIFICATION` | `NEEDS-VERIFICATION` | **Unscored discovery hypothesis with a likely primary-gate rejection if counts verify; not selected.** |

No row currently passes the scorecard, so the ranking tuple is intentionally
not computed. In particular, public availability of a model does not establish
MLX + GGUF + vLLM parity, a local mirror, a license receipt, or an 8 GB fit.

`NEEDS-VERIFICATION` matched-total discovery hypotheses, evaluable only if Ed
authorizes the different estimand, are an OLMo-named dense model near 7B total
against an OLMoE-named model near 7B total, and a Qwen1.5-named 14B dense model
against a Qwen1.5-MoE-A2.7B-named model recalled as roughly 14B total. Existence,
availability, counts, and family/tokenizer/tuning compatibility all require
primary receipts. Each must be labeled `matched-total/different-estimand` even
if it later passes.

## 7. Ed decision required — D-016 8 GB-fit conflict

> **DECISION OWNER: Ed. No option is selected by this document.**
>
> **Memory-rule subdecision required before scoring G10:** ratify, revise, or
> reject §4.2's proposed `axi-sd-memory-fit-shape-v1`, capacity/peak semantics,
> and `max(1 GiB, 15%)` reserve. Until that ruling is recorded, every G10 cell
> remains `NEEDS-VERIFICATION`; this proposal does not amend D-016.
>
> If the best active-matched pair cannot pass D-016's all-primary-target and
> ratified 8 GB-headroom gates, choose exactly one of these four paths:
>
> **Option A — preserve D-016 and authorize a separate `axi-mac-only` pair
> (recommended, matching the xhigh consult).** D-016 retains its cross-target
> comparability and 8 GB promise; AXI can still test an active-matched pair on
> the available large-memory Mac. Costs: AXI needs a distinct pair ID,
> artifacts, AP row, and Mac-only claim boundary, and the rider is not
> automatically "free inside 2M." If that pair is not already in the 2M
> matrix, any quiet-Mac work must be separately queued after Window A.
>
> **Option B — explicitly amend D-016.** Benefit: one unified dense/MoE pair
> and matrix can serve AXI and the baseline program, avoiding a second
> Mac-only pair/campaign. Costs: the amendment must state which all-target,
> 8 GB, or size-axis rule changes; update the decision log and every dependent
> matrix/manifest; and accept the resulting loss or narrowing of the original
> cross-target comparison. Existing provisional Qwen2.5-1.5B evidence does not
> justify the amendment by itself; advisor/supervisor scope is still required.
>
> **Option C — defer the dense/MoE pair (`no_eligible_pair`).** Benefit: D-016,
> Window A, and the capstone's hardware budget remain unchanged, with no weak
> fallback forced into the matrix. Cost: AXI records instrument support or a
> structured feasibility result only; there is no characterized dense/MoE
> energy contrast in the current capstone unless Ed later reopens it before
> the prospective freeze.
>
> **Option D — explicitly authorize
> `matched-total/different-estimand`.** Benefit: a storage-matched pair may be
> feasible where active matching is not, preserving a narrow architecture
> comparison. Costs: it answers stored-capacity matching, not active-compute
> matching; it needs a separate pair ID, AP family, figures, and claim wording;
> and it does not close D-016 unless it independently passes every D-016 gate
> including G12. Authorization of A or B never implies authorization of D.
>
> **Recommendation:** choose A if no D-016-compatible active-matched pair
> survives. Choose C if the extra Mac-only campaign is not worth its budget.
> Use D only by separate explicit ruling; total matching can never silently
> replace the active-matched result.

## 8. C5-1.12 quantization ladder

This ladder is independent of the dense/MoE decision. Its proposed subject is
the provisionally evidenced D-016 small model family,
`Qwen2.5-1.5B-Instruct`, because
[D-016 records](../../decision_log.md#d-016-benchmark-model-selection) a
specific working MLX 4-bit artifact and receipt. That cited community artifact
is discovery evidence, not automatic ladder lineage: the ladder must derive
every level from one newly frozen source revision. The ladder's source
revision and all derived hashes are `NEEDS-VERIFICATION`; this document
invents none.

### 8.1 Frozen levels and recipe

Preferred ladder ID: `c5-1.12-qwen2.5-1.5b-mlx-bf16-q8-q4-v1`.

| Level | Weight representation | Common-recipe requirement | Current state |
|---|---|---|---|
| `BF16` | Unquantized BF16 reference converted or copied from the one frozen source revision. | Same MLX runtime and module graph as quantized levels. | `NEEDS-VERIFICATION` |
| `Q8_G64` | 8-bit weights, group size 64. | Same converter revision, scale/bias convention, module allowlist, skipped modules, and source tensors as Q4; only bit width differs. | `NEEDS-VERIFICATION` |
| `Q4_G64` | 4-bit weights, group size 64. | Same recipe as Q8 except bit width. | `NEEDS-VERIFICATION` |

The converter package version, source commit, full semantic quantization
config, quantized and skipped module lists, output config, and conversion log
must be hash-bound. If the pinned runtime cannot produce or load one level
under this recipe, record `unsupported_ladder(<level>, <reason>)`. Do not
replace it after results with a community artifact or a different group size.
A pre-freeze capability check may prospectively reduce the design to the
two-level `BF16`/`Q4_G64` ladder; after the freeze, missing Q8 is a structured
failure, not a redesign.

All levels use `axi-sd-greedy-eos128-v1`, the same prompt-token hashes, cache
dtype, runtime build, workload shapes, warm/cold-state policy, and measurement
boundary. C5-1.12's eventual replication count and effect-size/floor decision
belong to AP-QUANT and D-062 after P2-015; this artifact spec does not freeze
`n` or authorize energy runs.

### 8.2 Mirror and hash plan

For both the pair scorecard and quant ladder:

1. Resolve every remote repository to an immutable commit/revision and save a
   metadata snapshot (repository ID, resolved revision, retrieval time,
   license path/hash, file list, sizes, LFS object IDs where present).
2. Mirror source snapshots read-only under
   `/Users/edr/jw_models/axi/source/<repo_slug>/<revision>/` and derived MLX
   levels under `/Users/edr/jw_models/axi/derived/<ladder_id>/<level>/`.
3. Hash each regular file with SHA-256. Build the artifact root digest from
   the SHA-256 of UTF-8 lines sorted by POSIX relative path, each formatted
   `<file_sha256>  <relative_path>\n`. Symlinks are forbidden.
4. Copy the completed immutable trees to a second local/offline mirror chosen
   by Ed. Record its absolute path/device identity and independently recompute
   the root digest; a same-filesystem alias does not count as a second mirror.
5. Before every quality or energy run, recompute both the per-file manifest
   and root digest. Any mismatch is `artifact_identity_fail` and blocks the
   run. The eventual repository receipt stores manifests and hashes, not
   model weights.

No path in this plan is evidence until its verification receipt exists.

### 8.3 C-023 quality-equivalence gate and reporting

The equivalence workload is the named frozen suite
`axi-sd-quality-screen-v1` from §4.1, using the identical 256 item IDs,
content hashes, answer keys, prompt-token hashes, scorer, and output policy.
Run it once per quant level before opening any energy result. `BF16` is the
reference. For each lower-precision level `q`, calculate paired item-score
differences `D_i = score_q,i - score_BF16,i`.

The preferred three-level ladder has `m = 2` prospectively selected
comparisons (`Q8_G64 - BF16` and `Q4_G64 - BF16`). The two-level capability
fallback has `m = 1` (`Q4_G64 - BF16`) only if it is declared before the
ladder freeze. Family-wise one-sided alpha is `0.05`, allocated by Bonferroni:
`alpha_q = 0.05 / m`. No level may be selected or dropped using output,
quality, memory, or energy results; a post-freeze missing level is a failed
level and does not reduce `m`.

For each comparison, generate 10,000 stratified bootstrap means. Within every
resample, draw 64 items with replacement from each stratum using PCG64 seed
`20260715` and the level order `Q8_G64`, then `Q4_G64`. Sort the 10,000 means
ascending and use the Type-1 inverse-empirical-CDF lower quantile: the
1-indexed order statistic at `ceil(alpha_q * 10000)` (rank 250 when `m=2`,
rank 500 when `m=1`). Before any model output, the suite manifest must record
the bootstrap script SHA-256, exact PRNG/library name and version, item order,
draw order, and this quantile convention. A future receipt cannot choose them.

Level `q` is quality-equivalent only if both conditions hold:

```text
lower_(1-alpha_q)_bound(mean(D_i)) > -0.02
and
min_s(Q_q,s - Q_BF16,s) >= -0.05
```

Invalid/missing items score zero; there is no item dropping or margin change
after outputs or energy are observed. Report for every level:

- overall and per-stratum scores with paired differences and the frozen gate;
- exact output-token identity rate against BF16;
- per-item token edit distance, output-token counts, and stop reasons; and
- the quality disposition: `exact-output-equivalent`,
  `quality-equivalent-output-divergent`, or `quality-not-equivalent`.

Only a level that passes may support the phrase "quality-equivalent
quantization efficiency" within this named screen and stack. The whole ladder
may be called quality-equivalent only if every frozen lower-precision level
passes. Exact token identity supports the cleanest matched-work comparison. A
passing but token-divergent level must be labeled
`quality-equivalent-output-divergent`. A failing level supports only a
descriptive quality/energy trade-off; it cannot be called an energy-efficiency
improvement.

### 8.4 AP-level workload, selection, and multiplicity binding

AP-QUANT must bind its energy workload to
`c5-1.12-quant-energy-v1`, a deterministic 32-item subset of
`axi-sd-quality-screen-v1`: within each of the four strata, select the eight
items with the lexicographically smallest content SHA-256 values. Freeze the
resulting item IDs, content/prompt-token hashes, order, output policy, and
suite digest before any quant output. This rule prevents quality or energy
outcomes from selecting the energy workload and makes the relationship
between the quality screen and campaign explicit. Quality equivalence remains
scoped to `axi-sd-quality-screen-v1`; the energy claim remains scoped to its
named 32-item subset and current MLX stack.

The AP-QUANT primary endpoint is gross decode energy per request. Its only
primary contrasts are each frozen lower-precision level versus BF16 on the
same item. They form one family of size `m` and use Bonferroni family-wise
alpha `0.05/m`; there is no outcome-selected best quant, pairwise level-vs-
level primary claim, or alpha recycling after a failed quality gate. A
level's energy contrast is claim-eligible only if its §8.3 quality gate passes
and its exact output divergence on the 32-item energy suite is reported.
Power, time, throughput, and the decomposition below are predeclared
secondary/descriptive outputs, not extra primary selections. P2-015 floors
and D-062 still own effect-size resolvability and final `n`; they may yield
`not_resolvable` but may not alter the frozen levels, family, workload, or
multiplicity rule.

For any passing level, C5-1.12 reports gross decode energy, elapsed decode
time, mean decode power, throughput, and output divergence. Decompose the
energy difference from BF16 symmetrically:

```text
Delta_E_power = (P_q - P_ref) * (T_q + T_ref) / 2
Delta_E_time  = (T_q - T_ref) * (P_q + P_ref) / 2
Delta_E_total = Delta_E_power + Delta_E_time
```

This is an exact two-factor decomposition of `P_q*T_q - P_ref*T_ref`; it does
not assign causality to power or duration. Gross energy within the named
boundary is primary. Any idle-subtracted value is a labeled within-device
secondary view under D-067.

## 9. MOE-BATCH claim wording gate

The mechanism label is conditional on auditable routing evidence. A routing
receipt must, for every request and emitted token, expose layer-indexed routed
expert IDs (or equivalent expert-load counters), measured dispatched-slot
count, shared-expert execution, and enough request/timestamp identity to join
the evidence to the batch lifecycle. Configuration values are diagnostics.
Validation must reconcile actual dispatched slots and aggregate expert loads
to token/layer/request counts, including dropped or capacity-limited routes.

- If that receipt passes, AP-MOE-BATCH may test and describe an association
  between static batch size and **observed expert routing/load distribution**
  for the named pair. It still cannot generalize MoE serving efficiency.
- If routing evidence is absent or unauditable, rename the row and claim to
  **"static-batch-size interaction for the named dense/MoE model pair."** The
  observable interaction may use energy, latency, memory, output, and batch
  identity, but the words `routing diversity`, `expert activation diversity`,
  `router mechanism`, and equivalent mechanistic claims are forbidden.

This naming decision is made from the routing receipt before energy results,
not from whether an interaction is detected.

## 10. Freeze checklist

The unresolved proposal and §7 choices may be presented to Ed now. A model
selection may be called frozen/final only when every item below is present:

- declared track and Ed ruling where `axi-mac-only` is proposed;
- Ed's explicit §4.2 memory-rule ruling;
- completed G1–G11 ranking card with no `NEEDS-VERIFICATION` values, followed
  by G12 before any pair is called final;
- exhaustive tensor-path classification ledger and fixed routing-probe receipt
  including shared experts and measured complex-router dispatch;
- D-016 KV bytes/token, transfer-range table/disposition, supervisor scope,
  Mac/CUDA and all-other-primary-target load/generation, artifact, and final
  closure receipts for the cross-target track;
- exact source/derived revisions, manifests, root hashes, licenses, and two
  verified mirror locations;
- one candidate-set quant recipe/digest across every pair, pinned
  runtime/environment, and a common G4–G10 `selection_join_key`;
- frozen output-policy and prompt-token hashes;
- frozen `axi-sd-quality-screen-v1` manifest and passing pair quality result;
- worst-of-three memory receipts with Ed-ratified headroom;
- deterministic ranking tuple and explicit estimand label.

The independent quantization ladder in §8 and MOE-BATCH claim track in §9
retain their own prospective gates, but neither is a prerequisite for G12 or
D-016 model-pair finalization.

Failure to complete the checklist yields `no_selection_yet`; it does not
authorize filling gaps from energy observations or changing D-016.
