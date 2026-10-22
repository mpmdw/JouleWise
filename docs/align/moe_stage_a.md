# MoE Stage A: routing beyond counts

Status: implementation in progress; synthetic validation is not hardware evidence.
No real model download, rented GPU, or live power collection is part of this lane.

Stage A asks whether aggregate router statistics separate benign and sabotage
episodes beyond logged token, turn, and tool-call counts. A negative Stage A
result is the pipeline's stop condition for the routing direction. Stage B,
which asks whether routing is visible in electrical power, requires hardware.
Power can count hidden work; it cannot identify reasoning inside one forward pass.

## Model topology

The published [Qwen/Qwen3-30B-A3B config](https://huggingface.co/Qwen/Qwen3-30B-A3B/blob/d47d535f78ec44bd57128f8e8aeba17eeb0285ea/config.json),
checked 2026-10-22, declares `model_type=qwen3_moe`,
`num_hidden_layers=48`, `num_experts=128`, `num_experts_per_tok=8`,
`decoder_sparse_step=1`, and `mlp_only_layers=[]`.
The recorder must discover actual sparse blocks and read their gate topology;
these published values are not constants imposed on other models.

## Backend capture paths

HF transformers permits forward hooks on each Qwen3-MoE, Qwen2-MoE, or Mixtral
sparse block's gate. The shared `RouterLog` orders rows by processed token,
then by actual MoE layer, and tags each row prefill or decode. A generation's
last sampled token need not have been forwarded through the model yet; captured
forwarded-token counts therefore need not equal server completion counts.

[vLLM v0.21.0 routing replay](https://docs.vllm.ai/en/v0.21.0/training/routed_experts_replay/)
documents `--enable-return-routed-experts` (offline:
`enable_return_routed_experts=True`). It exposes request-level
`prompt_routed_experts` and per-completion `routed_experts` arrays in
token/layer/top-k order. An adapter would join each request to its episode/turn,
append prompt and generation rows with their phase labels, and validate topology
and counts. Prefix-cache sentinel IDs, missing/preempted capture, and speculative
token trimming need flags. Pin the serving version and verify capture coverage;
older versions may need instrumentation at the fused router's selected IDs.

llama.cpp's [MoE graph construction](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-graph.cpp)
has the selected-expert tensor produced by top-k routing. A C++ graph evaluation
callback (`cb_eval`), or a small backend patch if fusion hides that tensor, would
copy actual selected IDs to host and join microbatch token positions, sequence
IDs, and layer IDs to requests. Its ordinary completion API does not supply
a shared `RouterLog`. Capture requires backend synchronization and correct
treatment of cached prompts and speculative forwards. Do not infer routes from
model text or expert load totals.

## Analysis contract

Entropy is normalized by log(number of experts). Load imbalance is the mean
per-layer population coefficient of variation. Reuse measures expert-set overlap
between adjacent selected tokens; reuse distance excludes each expert's first
selection. Phase filtering must happen before sequence statistics are calculated.

Permutation inference preserves label counts within each task group. Exact
enumeration applies through 100,000 arrangements; larger spaces require Monte
Carlo error below 0.005 at p=0.05, a tenth of that conventional significance level.
Routing, metadata, and combined classifiers must share held-out task groups.
