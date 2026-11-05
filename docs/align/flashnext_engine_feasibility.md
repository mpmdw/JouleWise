# Flash-Next engine feasibility — 2026-11-05

**Verdict: plausible on this Mac at a purpose-built mixed quantization, but not
qualified for Window 1 today.** First desk candidate: **routed/shared experts
3-bit/group-64; n-gram table 4-bit/group-32; other quantizable matrices
8-bit/group-64; router unquantized; norms/convolutions unquantized.** This is
`e3_ple4_other8` in the scripts. Estimated text weights are 90.145 GB, and a
provisional full-context peak is 103.393 GB. Those numbers are arithmetic, not
a load result. Three-bit expert quality is an open gate. Do not substitute a
REAP/pruned-expert artifact and call it the original 512-expert model.

Retain the council's W1 roster until the desk checks, integration gates, R1,
re-sizing, and prospective protocol-v4 amendment pass. If they pass before W1
freezes, Flash-Next can replace a declared new-model cell; do not silently add a
twentieth member or inherit Next's thermal class, timings, or calibration.
Qwen3.8-27B 8-bit is the first fallback. More detail is below.

## Authority and evidence limits

This is the explicitly requested engine desk lane, based on
`origin/lane/2026-11-05-align-pilot9-benign` at
`c9a0a39437614176bf4e14ff1565a6e4537328fb`. The source ruling was read with:

```sh
git show origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN.md
```

Its §1(a) says Flash-Next is “not admitted on the pinned stack; not proved
physically impossible.” Its §§2.1–2.2 and B1/B2/B7 own the anchor, history,
parser, and cache gates. This report proposes an additional engine route; it
does not install a new scientific ruling. D-016/D-074 require artifact and
runtime evidence; D-023 keeps authority in the owning contracts/checklists.
The user explicitly excluded coordination-state edits and the full suite.
No state kernel task was registered.

Only clone-local text and allowed Git objects were inspected. No network,
external home-directory paths, `restricted/` trees, measurement roots, Block-5
pipeline, PR imports/installations, or hardware experiments were used. AA
Progress Index v1 scores **320 / 303 / 225** are the user's dated research
inputs for Flash-Next / Qwen3.8-27B / Qwen3-Next, not independently verified
rankings here. An index is not evidence of deception attempts on SHADE.

Local evidence:

| Input | Identity / limitation |
|---|---|
| `.engine/mlx-lm-pr1788/` | Supplied as eauchs `add-qwen4-exp` at `2097324`; full commit must be resolved and authenticated at the approved desk. Directory labeling alone does not prove Git ancestry. |
| `mlx_lm/models/qwen4_exp.py` | SHA-256 `d6470a2131a64ff37024dfffd2b5bc8c3f4db625f0f3b1ceec7fe346852c1a87` |
| `mlx_lm/models/cache.py` | `c64e81d97bc6425afa155b65625ddb4a9bb8fac17b164ab519559abe4c5e9323` |
| `mlx_lm/utils.py` | `a653ed112e3b59df1a7dfc227dcb2c944b6e6846aaadba8b7e208c6aa3b7a78a` |
| `.engine/hf-flashnext/config.json` | `889658f2508e8c61d409b02e70e0d78d8d4452ec65aaafbe129805d213d2e74b`; copied to `tests/fixtures/align_flashnext_config.json` for CI without `.engine`. |
| Both staged `chat_template.jinja` files | Byte-identical; SHA-256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041` |
| Flash-Next README and `pr1788-comments.md` | Model author's architecture description and third-party reports, not independently reproduced reference logits. |
| `.engine/hf-qwen38/` | Config/tokenizer/template/generation files exist; the promised README is absent. Council text supplies the quoted card settings. |

All engine file:line references below are relative to
`.engine/mlx-lm-pr1788/`, at this snapshot.

## 1. Architecture review

| Card architecture | Port implementation and assessment |
|---|---|
| 48 layers; 12 repetitions of 3 DeltaNet + 1 QSA | `models/qwen4_exp.py:94–100,782–813`: explicit `layer_types`, with interval fallback; config has 36 recurrent and 12 full layers. |
| Gated DeltaNet, QK 16 × 128, V 48 × 128 | `:410–494`: split QKV/Z/A/B projections, depthwise width-4 convolution, Q/K normalization/scaling, gated delta update, sigmoid gated RMSNorm and output projection. `models/gated_delta.py:610` initializes the recurrent matrix in FP32. This matches the card's dimensions; the card alone cannot certify the normalization constants/kernel arithmetic. |
| QSA, Q 24 × 256; KV 2 × 256; partial RoPE 64 | `:346–405`: doubled Q projection includes sigmoid output gate, Q/K norms, 64-dimensional partial RoPE; remaining head channels pass through. Ordinary text positions are represented on one axis; image/video mRoPE is not implemented. |
| QSA indexer: 4 query heads, 1 key head, dim 128, blocks of 4; 2048-token budget | `:209–343`: stores raw indexer keys, mean-pools complete micro-blocks, normalizes/rotates, sums ReLU dot products over heads, selects 512 complete blocks, unions each query's partial block. It masks candidate blocks by each query's past, then intersects the attention mask with causal visibility (`:385–403`). The previous all-masked/future-token problem has a visible tail-union fix (`:328–343`). At most 2048 selected complete-block tokens plus up to 3 tail tokens; it does not keep only 2048 KV tokens in memory. |
| Four gated residual streams, rank 320 | `:533–554,799–813,870`: streamwise RMS statistics; low-rank elementwise read gates; averaged read across four streams; scalar write gates per stream; final mixer without injection. Broad card correspondence, not a proof of the `/hc`, mean, or factor-2 constants against official forward code. |
| Bigram/trigram PLE at layer 2, dim 2560 | `:591–688,718–777,790–795`: 16 heads of dim 160, prime head vocabularies, padded into 128 shards; signed-int64 XOR hashing with EOS boundaries; seed 1234. One-based `ple_layer_ids=[2]` selects decoder index 1. PLE key/query gating, value projection, and width-4/dilation-3 convolution are present. `:1177–1189` checks checkpoint hash constants, a useful fail-closed repair. |
| 512 experts, 10 routed + one shared, intermediate 640 | `:500–527`: top-10 logits, selected-set FP32 softmax, weighted SwitchGLU, separately sigmoid-gated shared expert. `:1141–1158` splits fused HF gate/up weights along the output axis and maps the down projection. Counts match; expert routing/tie behavior still needs reference evidence. |

**Omissions:** `sanitize` drops vision and MTP (`:1119–1125`), and neither has a
module in the forward graph. Vision is unnecessary for text-only SHADE tool
use; reject image/video requests rather than feeding visual placeholders to a
text-only model. MTP is a speed feature for this use: ordinary next-token
inference can use the main LM without the auxiliary prediction head. Its
absence removes speculative acceleration; do not claim an MTP throughput or
assume speculative sampling has been verified. Text-only card capability
still needs validation on the converted main weights.

### Ranked correctness and execution risks

1. **High / confirmed reachable corruption if enabled — KV quantization loses
   QSA state.** `_AttnCache` at `models/qwen4_exp.py:901` inherits
   `KVCache.to_quantized` (`models/cache.py:383–392`), which returns a plain
   `QuantizedKVCache` without `indexer`. `generate.py:293–300` replaces cache
   entries with it. `qwen4_exp.py:872` subsequently passes no indexer history:
   new keys alone cannot select the historical blocks at the true offset.
   Forbid `kv_bits`, rotating/max-KV substitutions and draft decoding. Small
   tests below the indexer budget can conceal this error.
2. **High / confirmed converter incompatibilities — artifact provenance is
   part of correctness.** The `1 + weight` fold depends on an HF prefix
   (`qwen4_exp.py:1115,1166`). Flat oMLX/raw-norm or pre-fold-era conversions
   can therefore load with wrong scaling. Global PLE `weight_scale` is not
   handled by `sanitize`; strict loading should reject it, not discard it.
   Per-module quant overrides match post-sanitize paths literally
   (`utils.py:388–403`); checkpoint-prefixed overrides miss. Do not patch by
   guessing a format from a filename or stripping an unknown parameter.
   Use authenticated official HF inputs and a fresh conversion under this
   exact revision, or require a fully specified conversion receipt.
3. **High / confirmed unsupported input lane — raw left padding.** The model
   itself warns at `qwen4_exp.py:847–848`. PLE hashes physical `ids` and updates
   history (`:650–687,853–868`) without replacing padded IDs by EOS; its short
   convolution is not pad-masked (`:742–777`). Attention padding support does
   not fix PLE. Use batch 1/unpadded prompts, or the tested right-pad →
   finalize path used by BatchGenerator. Prove that the production server
   actually takes that path; concurrency=1 alone is not such proof.
4. **High for checkpoint lane / confirmed generic disk-restore gap.** Private
   cache classes `_AttnCache`, `_BatchAttnCache`, `_LayerCache`
   (`qwen4_exp.py:901,926,1027`) are not in the `models.cache` registry used by
   `load_prompt_cache` (`cache.py:79–82`, `globals()[class_name]`). Generic
   save may also encounter unused `None` slots. Do not claim persistent
   round trips work. In-memory restoration into fresh `model.make_cache()`
   instances is a separate, testable route.
5. **High if an attention-only rewind is used / otherwise safe refusal.**
   `_LayerCache` inherits non-trimmability (`cache.py:146,594`);
   `trim_prompt_cache` refuses the entire hybrid list atomically (`:88–110`).
   Existing `EpisodePromptCache.prepare` rebuilds on this condition, which
   preserves correctness but can be slow. Cache-checkpoint must save all
   recurrent slots: Delta convolution + FP32 matrix, PLE convolution + last
   two IDs; trim KV **and raw QSA keys** (`qwen4_exp.py:906–910`), restore the
   saved recurrent boundary, and re-feed. KV offsets alone prove too little.
6. **Medium, unresolved numerical issue — prefill vs stepwise.** The thread
   reports ~`1.07e-3` on one setup; the author reports <`1e-6` on M3 Max and
   another tester passes at MLX 0.32.3. No reproduction here. The 600k-token
   8-bit testimony predates the norm-fold change, and that artifact was
   retired rather than revalidated. Do not treat it as current-head evidence.
   Run many seeds, block boundaries, EOS and causality tests on the actual
   installed versions; report max error, RMS, KL and argmax agreement.
7. **Medium, reference-equivalence uncertainty.** QSA top-k ties and masked
   rows (`:286–343`), int64 hash overflow/modulo (`:669–687`), residual gate
   constants (`:546–554`), normalization folding and fused expert splitting
   need a trusted implementation comparison. Internal exactness tests can
   pass with a consistently wrong port. The official reference forward code
   and trusted logits are not staged; independent teacher-forced reference
   comparison remains a qualification gate.
8. **High execution risk / not itself a mathematical defect — dense QSA
   intermediates and host synchronization.** `:282–317` builds query × block
   scores and query × full-token masks; `:709–714` repeatedly materializes
   shard indices on the host and loops through touched shards. Sparse
   selection is not a specialized sparse-attention kernel. Memory, TTFT and
   thermal behavior must be measured, especially at the context cap.

There is another conversion trap: `utils.py:885–886` tests divisibility by
the **global** group size before consulting a per-module recipe. N-gram rows
are 160 wide, so a group-64 global default can leave this 51B table
unquantized even if a recipe requests group 32. The conversion helper uses
global group **32**, then explicit per-module group-64 overrides elsewhere.
Audit the saved map and loaded byte census; a successful process exit is not
proof of the intended recipe.

## 2. Memory model

Reproduce with only our stdlib code:

```sh
python3.13 -B -m scripts.align_flashnext_memory
```

`scripts/align_pilot_kit.py:40` pins **40,960** tokens. Batch size is 1.
GB below means `10**9` bytes; the reported working set is **115.4 GB =
107.5 GiB**. The 128 GB physical label is nominal; record `hw.memsize` and
`mx.device_info()` rather than interchanging GB and GiB at the desk.

For hidden size H=2560 and expert intermediate I=640, routed matrices are
`48 × 512 × 3HI = 120,795,955,200` elements. Attention/QSA includes doubled
Q for the output gate, K/V/O and indexer QK. Delta weights include QKV, Z,
A/B and output projections. Residual mixers count both branches per layer
and the final mixer. The n-gram count reconstructs all 16 prime vocabularies
and shard padding from the config, without importing the port.

| Component | Parameters, B | Ideal GB at 8b | 6b | 4b | 3b |
|---|---:|---:|---:|---:|---:|
| Routed experts | 120.795955 | 120.796 | 90.597 | 60.398 | 45.298 |
| Shared experts + shared gates | 0.236052 | 0.236 | 0.177 | 0.118 | 0.089 |
| Routers | 0.062915 | 0.063 | 0.047 | 0.031 | 0.024 |
| Attention + QSA indexers/norms | 0.617358 | 0.617 | 0.463 | 0.309 | 0.232 |
| DeltaNet weights/norms/conv | 2.086510 | 2.087 | 1.565 | 1.043 | 0.782 |
| Hyper connections | 0.640625 | 0.641 | 0.480 | 0.320 | 0.240 |
| Token embedding + LM head | 1.271398 | 1.271 | 0.954 | 0.636 | 0.477 |
| PLE projections/norms/conv | 0.032840 | 0.033 | 0.025 | 0.016 | 0.012 |
| N-gram table | 51.200246 | 51.200 | 38.400 | 25.600 | 19.200 |
| **Implemented text total** | **176.943900** | **176.944** | **132.708** | **88.472** | **66.354** |
| MTP, card's rounded estimate, **excluded** | ~4 | ~4 | ~3 | ~2 | ~1.5 |

The first table is an ideal bit-packing lower bound, including hypothetical
quantization of small tensors. MTP's exact independent tensor inventory is
**not derivable** from this config: it specifies one full-attention layer and
shared embeddings, but not every auxiliary tensor or ownership of shared
weights. The card's rounded 4B is shown explicitly as an estimate, never added
to resident text. Vision is also excluded. The 35 public hash-buffer integers
add only 280 bytes; alignment/headers and allocator costs are outside this
parameter census.

Practical affine estimates add BF16 scale + bias, `4 / group_size` bytes per
matrix element. Group 64 applies except group 32 for the 160-wide n-gram
table. Norms/conv/scalars stay BF16; router storage is conservatively budgeted
FP32 (actual BF16 would save ~0.126 GB). Quantization cannot shrink the FP32
recurrent matrix. Expert activity affects compute, not the resident 512-expert
weight budget.

| Recipe | Weights GB incl. quant metadata | + cache + assumed 12 GB workspace | Assessment |
|---|---:|---:|---|
| Uniform 8-bit eligible matrices | 191.390 | 204.638 | Exceeds physical memory |
| Uniform 6-bit eligible matrices | 147.171 | 160.419 | Exceeds physical memory |
| Uniform 4-bit eligible matrices | 102.951 | 116.199 | Above working set under this reserve |
| Uniform 3-bit eligible matrices | 80.841 | 94.089 | Memory candidate; quantizes sensitive matrices too |
| Experts 4, all embeddings/other matrices 8 | 130.874 | 144.122 | Does not fit |
| Experts 3, all embeddings/other matrices 8 | 115.745 | 128.993 | Does not fit |
| Experts 4, n-gram 4, other matrices 8 | 105.274 | 118.522 | Insufficient planning margin |
| **Experts 3, n-gram 4, other matrices 8** | **90.145** | **103.393** | **First candidate; quality unproved** |

The 12 GB workspace is a **planning assumption**, inclusive of the following
arrays and allocator/transient room; do not add them a second time. It is not
an upper bound. The published 4-bit download size (111,546,653,418 bytes,
council V3) and ~111 GB reported M3 Ultra peak are different observables from
this purpose-built text-only recipe. Different precision maps, excluded
components and loaders can explain differences, but no staged shard headers
establish the actual explanation. Do not subtract guessed vision/MTP bytes
from that download and call the result a measured resident set.

At 40,960 tokens, BF16 KV is
`12 × T × 2(K,V) × 2 heads × 256 × 2 bytes = 1,006,632,960 B`.
Raw QSA keys add `12 × T × 128 × 2 = 125,829,120 B`; sparsification does not
remove them. Delta matrices add `36 × 48 × 128 × 128 × 4 = 113,246,208 B`,
constant in T. Delta conv history adds 2,211,840 B; PLE conv/history 184,336 B.
**Total cache: 1,248,104,464 B = 1.248 GB.** FP32 attention/indexer caches would
add another 1.132 GB. A full second cache adds another 1.248 GB; a recurrent-only
checkpoint adds ~0.116 GB. Limit checkpoint count; immutable copies are not free.

With chunk 512 at the end of the context, one QSA head-score tensor is
83.89 MB, a full-token bool keep mask 20.97 MB, and output logits are
254.28 MB BF16 or 508.56 MB FP32. A materialized 24-head attention-score
tensor is **2.013 GB FP32 per layer in flight**; fused SDPA behavior determines
whether/how much appears. Multiple temporaries and lazy lifetimes can overlap.
An unchunked 40,960-token call can make logits alone **20.34 GB BF16 /
40.68 GB FP32**, QSA head scores 6.71 GB, a mask 1.68 GB, and hypothetical
dense attention scores 161.06 GB. Never use full-cap unchunked prefill.
The script models short exactness prefill separately from cap-sized chunked
capacity checks. Start chunk 512; a different chunk is a new pinned policy.

### Can the n-gram table stay on CPU / mmap?

Architecturally yes: only 16 selected rows of width 160 are needed per token,
with 2560 output values. Approximate table reads per token including group-32
metadata are **1600 B at Q4**, **2880 B at Q8**, or **5120 B BF16**, plus
5.12 KB BF16 / 10.24 KB FP32 gathered output. This is cheap in bandwidth.
Cold random faults are not cheap: 16 distinct 16-KiB pages would be ~256 KiB
per token before readahead/boundary effects, and synchronization/CPU dispatch
can dominate. Shard-level materialization would be much larger still.

**This port implements no explicit CPU weight-offload policy.** Its NumPy
operations move *indices* to the host; `self.shards[s](...)` executes through
MLX's selected stream. On unified memory, mmap is a loading mechanism, not a
guarantee that pages never become GPU-resident/wired or count against total
memory. Sustained prefill can touch all 128 shards; mmap cannot be budgeted as
zero resident bytes. An explicit CPU gather/dequant path could transfer only
the selected output vectors, but needs compatible CPU kernels, scheduling,
equivalence tests and cold/warm latency evidence. It is an additional engine
change, outside this unmodified-PR proposal. No feasibility claim here assumes
it exists; no wired-limit change is recommended.

## 3. Deferred exactness scripts

`scripts/align_flashnext_exactness.py` is deliberately lazy: module import and
`--help` use stdlib only. Before importing MLX it requires `--approved-desk`, an
Apple Silicon Mac, an isolated venv, exact Python/package pins, full commit
identity, and a complete installed `mlx_lm` Python-source hash inventory.
It also hard-checks the three reviewed port/cache/loader hashes above and
rejects importing directly from `.engine`. Real model inputs additionally
require a complete authenticated artifact manifest. These are desk execution
gates, not a request to run it in this session.

Tiny configuration retains all architectural features: 4 layers (3 recurrent
and 1 QSA), PLE on layer 2, four residual streams, sharded bigram/trigram
tables, routed/shared experts, and an indexer budget of 8. Default lengths
7/8/9/20/23/70 cross sparse activation, block alignment and convolution history;
an EOS inside the input tests hash reset. Use seeds 0–29 for qualification.

The script compares full prefill with single-token feeding and chunks 3/4/7/512;
perturbs the last token to test earlier-position causality; compares unpadded
batch-1 against a heterogeneous batch with raw left padding; tests right-pad
prefill/finalize/decode; copies every cache state into fresh private-class
instances; verifies generic hybrid trim refuses without changing state;
then trims attention/indexer and restores recurrent state at a saved boundary
before re-feeding the original and an alternate suffix. It also tries native
disk persistence and tests whether KV quantization preserves the indexer.

Known unsupported paths remain **FAIL**, with nonzero exit and retained JSON.
No xfail turns them into a green qualification. The lead may exclude only
provably unreachable paths: raw-left-pad input, disk persistence, and KV
quantization. Every supported-path failure blocks admission. For real models,
use lengths 2047/2048/2049/2053 (crosses the actual QSA budget), on a fresh
process per invocation. This is teacher forcing on deterministic synthetic
IDs, not a capability claim. Cap prefill uses the separate chunked desk probe.

Tiny default tolerance is `atol=rtol=1e-4`. Record the initial real-model run
with the same tolerance. A separate BF16 diagnostic at `atol=1e-2,rtol=1e-4`
can characterize a failure; it **does not erase the first failure or itself
authorize a relaxed exactness bar**. Review KL, argmax, margins, dtype and
kernel/version sensitivity against a trusted reference before ruling on it.

## 4. Two environments and endpoint integration

The current Apple path is **in-process**, not HTTP
(`joulewise/align/apple/endpoint.py:1–5`). Merely selecting a different server
URL is not an implemented kit feature. Preserve that fact when designing the
v4 lane:

| Role | Launch and identity |
|---|---|
| Anchors / existing contrast | Existing absolute Python from the existing `.venv`, running the unchanged pilot member worker/session path. `env/mac-measurement-lock.txt`: Python 3.13.1, mlx/metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1. Preserve exact member JSON/spec, weights/revision, template, seeds, cache path, sampler and timing. Do not move historical anchors to HTTP to obtain isolation. |
| Flash-Next cell | Second immutable venv, e.g. kit-local `.venv-flashnext`, with the full `2097324…` PR revision installed as a wheel; initial proposed MLX/metal **0.32.3** (thread's tested combination), transformers **5.12.1**, Python **3.13.1**, other dependencies explicitly locked. This combination is proposed, not tested. Staged `setup.py:12` requires MLX >=0.32.1: do not force it into the old 0.31.2 environment based on earlier thread reports. |
| New-cell HTTP endpoint | Kit subprocess argv must begin with that cell's absolute venv Python: `python -m mlx_lm.server --model ABS_SNAPSHOT --host 127.0.0.1 --port 8091 --decode-concurrency 1 --prompt-concurrency 1 --prefill-step-size 512 --prompt-cache-size 1 --chat-template-args '{...}'`. `server-command` prints the exact argv with effort/history fields; it never launches. Use one model process at a time, no draft/KV quantization, no trust-remote-code flag, no default-template replacement. |
| Other new models on old stack | Their worker uses the old absolute Python. If a new HTTP mode is chosen for them, it needs separate pins/validation; it does not change the existing anchors. Old server CLI support must be checked independently—do not pass new-only flags to 0.31.3. |

Kit launch should use `subprocess.Popen(argv, env=explicit_env, cwd=frozen_repo)`
with no shell, no global venv activation, no shared `PYTHONPATH`; use bounded
readiness probes, pin PID/argv and returned runtime identity before the episode,
and terminate/wait for that child before switching cells. Start server/load
before neutral warmup and G0, and before the episode attribution stamp. No
second model copy may remain in the runner. Set HF offline flags after download.
Use the same approved native generation worker instead of HTTP if necessary to
retain phase traces; the second venv can isolate the whole member process.

**HTTP is only a desk/debug route until production provenance is implemented.**
The generic OpenAI client cannot replace native phase/token records needed by
ALIGN attribution. New-cell server/worker integration must expose exact prompt,
emitted and consumed IDs; cache class/offset/checkpoint records; effort/template
policy; parser version; phase/hold events; and stream completion/accounting.
Test that path under real templating and right-padded batching. B1/B2 (XML and
`reasoning_content`) remain prerequisites; this lane does not edit the endpoint.
In particular, the Qwen template expects structured tool arguments as objects,
not a JSON string iterated as a mapping. Avoid rendering both raw XML in content
and a duplicate structured tool call.

Do not reuse the current kit's single global version map for the new cells.
`align_pilot_kit.py:255` copies one `runtime_versions`; its unit `stack_identity`
is unobserved at generation time. In a **new v4 schema/sidecar** preserve the
legacy file and add `runtime_stacks: {anchor_v1: {...}, flashnext_pr1788: {...}}`
and per-unit `runtime_stack_id` + observed `stack_identity`. Each map records
absolute interpreter, Python/build/ABI, macOS/device, MLX/metal/mlx-lm versions,
full mlx-lm commit and clean checkout receipt, wheel hashes, `pip freeze` lock
digest and complete installed source inventory. A package version alone cannot
distinguish a PR fork. Per-unit pins also bind weights/config/tokenizer/template/
generation files, source revision, conversion recipe/map/command/seed, immutable
artifact inventory, parser/history/cache policy and server arguments. Refuse
an unknown stack, observed mismatch, missing entry or a source hash difference.
Do not alter an existing identity schema without its consumer update/review.

Protocol v4 must pre-register both stacks and per-unit assignment, the engine
fork/omissions, supported input/cache paths, exact quantization and quality
thresholds, context/chunk/concurrency, reasoning effort/sampler, seed domain,
token budgets/deadman, startup/warmup placement, thermal gates/holds and
attribution, support-path exactness ruling, model selection/fallback order and
qualification deadline. R0/R1 are selection data; freeze the chosen policy and
recompute span/fit/disk before registration's cold gate. No post-outcome
precision/effort switching, pooling across engines, or claim that AA score
differences isolate the model independently of engine/quantization.

## 5. One approved daytime desk session

This session is **future work**, on the measurement Mac after the long analysis
job finishes and with no window armed. No powermetrics, energy campaign,
detection-floor collection or R1 quiet work runs through this agent lane.
Close other model/agent loads before timing; reserve a separate clean quiet
session for R1. Keep every result immutable. The commands below are recipes
for that later session, not commands executed here.

1. **Stage and authenticate, 30–60 minutes excluding transfer.** Record Mac15,9,
   chip/memory, `hw.memsize`, `mx.device_info()`, wired-limit readback and
   initial swap. Resolve the source to a full `2097324…` commit in a separate
   reviewed checkout; check `git rev-parse HEAD`, clean tracked/untracked
   status, and the source SHA-256 values above. Review/build that source into
   the new venv only now. Keep the old venv untouched. Pin every wheel/version
   and hash the installed code against the reviewed checkout; no editable
   import from `.engine`, no remote custom code.
2. **Acquire one candidate.** Prefer a directly published original-512-expert
   artifact only if its complete revision, tensor headers, quantization map,
   norm-fold/hash-seed provenance and file SHA-256 manifest can be authenticated.
   No such mixed candidate's immutable revision is staged, so none is invented
   here. Otherwise download the official BF16 source at an independently
   verified immutable HF revision, or transfer an approved conversion from a
   larger machine. A future connected desk could use
   `hf download Qwen/Qwen3.8-Flash-Next --revision FULL_HF_SHA --local-dir RAW`,
   followed by a publisher/lead-authenticated file manifest check. HF download
   metadata should be outside the sealed model inventory or deliberately
   included and then frozen. Do not use `main`, a short ref, or a filename as
   identity. Observe a local inventory with the helper, then authenticate it
   against the upstream receipt; self-hashing alone is not authentication.
3. **Convert if required.** Use the helper's `convert` with recipe
   `e3_ple4_other8` and authenticated **unquantized** original input. It calls
   lazy `load`, group-32-global `quantize_model`, and shard-donating `save`.
   It rejects re-quantization, an existing destination and custom model code.
   Audit every saved per-module key/bits/group and strict-load in a **fresh**
   process. Original BF16 text alone is ~354 GB on disk; vision/MTP add more.
   Raw source + output + operational free-space reserves may exceed this Mac's
   disk. Lazy conversion is not proved to peak below 128 GB; if disk or memory
   fails, preserve the report and convert elsewhere. Do not promise a model
   download/conversion plus all tests fits one day without known transfer speed.
4. **Tiny exactness first, ~10–20 minutes budget.** Run 30 seeds and retain all
   failure records. Do not load the 90-GB model until supported-path results
   are satisfactory. The script does not patch the fork or register its private
   caches in the generic serializer.
5. **Real quality/rates/cap screen, ~60–120 minutes budget.** Freeze a public
   SHADE system/user/tool-prompt text giving ≥2049 tokens, hash it, and score
   exactly 2048 teacher-forced next-token positions. NLL ≤3.0 nats/token is the
   council's gross loader sanity bar; also compare the same positions against
   a trusted high-precision/reference export (target degradation ≤0.1 nats/token,
   proposed for prospective registration). The latter reference is absent
   here and remains mandatory. Run visible-answer coherence, then generated
   XML tool request → schema-typed local multiplication → real-template tool
   response → generated final answer for **low/medium/xhigh**. Record prompt/
   output IDs, text, close/cap reason, prefix rewrite count, prefill/decode
   tok/s, MLX peak, process RSS, swap. The helper exercises a harmless local
   function, not a SHADE success trial; B1's separate `task.call_tool` tests
   and the real SHADE benign rehearsal are still required.
6. **Real exactness, ~30–90 minutes budget.** Use 2047/2048/2049/2053 to cross
   sparse selection. Retain the strict run; diagnose BF16 discrepancies
   separately. Run a trusted forward reference on identical ids/weights to
   rule out a shared wrong implementation. If the reference is unavailable,
   report the gate pending. Never manufacture reference logits with this port.
7. **Cap/decode/episode rehearsal and adjudication, ~60–90 minutes.** The helper
   chunk-prefills all 40,960 synthetic tokens and checks real cache offsets;
   its ordinary effort probes measure decode/prefill on the same short task.
   It does not force EOS suppression to manufacture a long decode or finish
   a SHADE episode. Separately run long-context decode with prompt+admitted
   output ≤40,960 and the council's long-decode repetition check; run both
   benign SHADE pairs at each effort under the actual B1/B2 integration. Record
   early EOS, closed reasoning, state-changing actions and the ≤20% unclosed /
   median ≤2048 reasoning-token bars from §2.2 of FINAL-DESIGN. Run the real
   HTTP roundtrip if HTTP is proposed for production; trace identity is a gate.

The budgets above are planning estimates, not measured throughput; stop the
daytime desk after ~5–7 hours if gates remain unresolved and retain D as W1's
model. No unfinished gate becomes a pass at the deadline.

All execution is module-style from this repo. Example commands use shell
variables for **approved desk locations only**; they are not current-session
path authorizations:

```sh
# NEWPY is the new venv's absolute Python. PINS and MANIFEST are authenticated.
# Every OUT below must be a distinct, nonexistent file.
python3.13 -B -m scripts.align_flashnext_desk inventory --model "$MODEL" --output "$OBSERVED_MANIFEST"
"$NEWPY" -B -m scripts.align_flashnext_exactness --approved-desk --pins "$PINS" --seeds 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29 --output "$TINY_OUT"
"$NEWPY" -B -m scripts.align_flashnext_desk convert --approved-desk --pins "$PINS" --model "$RAW" --artifact-manifest "$RAW_MANIFEST" --destination "$MODEL" --recipe e3_ple4_other8 --output "$CONVERT_OUT"
"$NEWPY" -B -m scripts.align_flashnext_desk probe --approved-desk --pins "$PINS" --model "$MODEL" --artifact-manifest "$MANIFEST" --nll-text "$NLL_TEXT" --nll-sha256 "$NLL_SHA" --chunk 512 --context 40960 --repeats 3 --decode-tokens 4096 --output "$PROBE_OUT"
"$NEWPY" -B -m scripts.align_flashnext_exactness --approved-desk --pins "$PINS" --model "$MODEL" --artifact-manifest "$MANIFEST" --lengths 2047,2048,2049,2053 --output "$REAL_OUT"
python3.13 -B -m scripts.align_flashnext_desk server-command --python "$NEWPY" --model "$MODEL" --port 8091 --effort xhigh
```

`PINS` is JSON with `mlx_lm_commit` (full 40 hex, starting `2097324`),
`python_version`, `package_versions` (exact versions for all dependencies;
at least mlx/metal/mlx-lm/numpy/transformers/tokenizers/jinja2/safetensors),
and `mlx_lm_python_sha256` (every installed `.py`, relative to installed
`mlx_lm/`). Independently verify its full source commit/cleanliness and wheel
receipt before sealing it. The script compares the installed version and full
Python source inventory; it cannot cryptographically authenticate a claim about
Git ancestry without that receipt. Model `MANIFEST` has `files: {relative_path:
sha256}` for **all** files in a materialized snapshot. Missing, extra, changed,
symlinked, restricted or empty inventories fail. The source checkout/wheel,
native MLX binary wheels and their hashes belong in the registration inventory
as well. No valid filled `PINS` or model manifest can be produced from the
unexecuted source staging alone.

### Quantization decision rule (proposed; freeze before the desk)

Choose the most precise **qualified** recipe within the memory/time envelope,
not the fastest raw score or a low-effort run selected after seeing outcomes:

1. Supported-path exactness, hash/key/norm checks and trusted-reference quality
   comparison pass; NLL ≤3.0 and ≤0.1-nat degradation on the frozen corpus.
   No corruption/repetition or unsupported tool-call format; ≥95% tool
   envelopes parse in the actual benign rehearsal, zero closed-reasoning
   history rewrites, and at least one meaningful state-changing action per
   pair. The calculator probe alone cannot satisfy these capability bars.
2. Measured load, warm/cold prefill, cap decode, and checkpoint peaks stay
   **≤103.86 GB** (90% of 115.4), with **zero swap growth**, stable identity,
   no memory errors, and system memory pressure acceptable. Record MLX and
   system metrics: RSS alone misses GPU-wired pages. The helper's memory
   guard covers MLX/swap, not a complete OS pressure assessment. Do not raise
   wired limits to turn failure into success. Recheck the nominal physical
   memory headroom from observed `hw.memsize` and non-model residency.
3. Select effort in xhigh → medium → low order under the council's predeclared
   cap/closed-reasoning rule. Prefer the highest effort that fits and acts.
   Use the measured rates and benign episode duration to fill R1 slots and
   demonstrate the member/span law fits; do not set an invented universal
   tok/s bar or import an Ultra's rates onto this Max.
4. Screen mixed E3/PLE4/other8 first. If it passes and measured margin allows,
   screen E4/PLE4/other8 next; promote only if it independently passes all bars.
   Uniform Q4 is also a separate artifact and is not presumed to fit. Uniform
   Q3 is a last quality-screen candidate if the mixed recipe misses memory;
   it does not get admission by footprint alone. Reject CPU/mmap-offload and
   pruned-expert variants from this decision unless separately pre-registered.
5. Any failure or missing reference/identity/integration evidence leaves
   Flash-Next out of W1. No trial on sealed measurements; no changing an
   already-frozen calibration population.

## 6. Fallback order and how to load

This is an **operational readiness** ranking among the named alternatives,
not a fabricated current capability leaderboard. All still need the council's
full-context/tool/thermal qualification; historical small-context runs do not
satisfy it.

| Order | Model and load route | Evidence and remaining gate |
|---|---|---|
| 1 | **Qwen3.8-27B 8-bit**, `mlx-community/Qwen3.8-27B-8bit` @ `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`; existing 0.31.2/0.31.3 environment; `mlx_lm.load(ABS_SNAPSHOT)` selects `qwen3_5`, text-only sanitizer. | Council primary D, 29.532-GB whole artifact; staged config confirms architecture and affine 8/64. Same XML/history fixes as Flash-Next. Effort ladder before switching to its 4-bit fallback @ `10c35caafbb80f7dc6a7a432cdd11af10a6d4818`. User's index 303 makes this the strongest supplied capability fallback. |
| 2 | **Qwen3.5-122B-A10B 4-bit**, `mlx-community/Qwen3.5-122B-A10B-4bit` @ `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`; existing stack, `qwen3_5_moe` text path. | Council F reserve; repo's `docs/design/bytes_pilot/SUMMARY.md:26` records 71.5-GB MLX peak at ~2.5k, not the cap. XML parser and R1 screen remain. This readiness rank does not assert it is more capable than the absent newer alternatives. |
| 3 | **gpt-oss-120b**, known artifact `mlx-community/gpt-oss-120b-MXFP4-Q8`; native `gpt_oss` on the existing stack handles MXFP4 experts and Q8 other tensors. Download at a newly verified full revision, then `mlx_lm.load(ABS_SNAPSHOT)`. | Repo summary records 63.4-GB resident / 64.3-GB MLX peak at ~2.5k. Artifact was deleted and is not treated as on disk. Raw-text greedy output repeated quote characters: use its **Harmony** chat/tool format and parser, not Qwen XML. A revision and current template/tool rehearsal are missing; requires a separate cell policy. |
| Unqualified alternative | **Nemotron 3.5 Bolt** | No matching config, model card, immutable artifact or tokenizer is staged or found in the bounded repo evidence. `models/nemotron_h.py` exists on the pinned stack, but that does not prove this named release has compatible architecture/state layouts. If independently confirmed `model_type=nemotron_h` with matching fields, use an authenticated MLX affine quant under a separately qualified stack; otherwise a supported, pinned GGUF/llama.cpp engine would be another route. Size/active count, context memory and tooling cannot be asserted here. |
| Unqualified alternative | **Ling-3.0-flash** | No matching model evidence staged. The PR snapshot has architecture-specific mapping `('bailing_hybrid','BailingMoeV3ForCausalLM') → bailing_moe_v3` (`utils.py:59–61`), whereas the old stack's `bailing_moe_linear` implements a different hybrid. Do not infer this release's loader from its brand. Confirm its actual config and matching MoE/KDA/state/template implementation before choosing a second-venv MLX or pinned GGUF route. Feasibility and rank remain unknown. |

The offline evidence cannot honestly rank the last two as “feasible today.”
The next exact step is the approved daytime **tiny-model** run with authenticated
runtime pins, then one authenticated mixed artifact. Until then the supported
recommendation is **D 8-bit for W1, Flash-Next mixed E3/PLE4/other8 as a gated
candidate**, with all live labels PROVISIONAL.
