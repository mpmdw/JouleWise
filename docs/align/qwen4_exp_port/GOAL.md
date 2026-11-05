# GOAL: a complete, validated MLX port of Qwen3.8-Flash-Next (`qwen4_exp`)

Owner: laptop lead (Opus 5.5), set by Ed on 2026-11-05: "make that a major separate goal and branch of joulewise - i want to spend significant tokens on it ... don't stop til you've architected tested and validated a whole" port. Long-lived branch: `port/qwen4-exp-mlx`.

## Why
- Qwen3.8-Flash-Next is the strongest open model that fits on the 128 GB M3 Max measurement Mac (Artificial Analysis Progress Index v1: 320, against 303 for Qwen3.8-27B and 225 for Qwen3-Next-80B). ALIGN / SHADE-Arena needs agents capable enough to attempt deception.
- MLX has no merged support: ml-explore/mlx-lm PR #1788 has been open since 2026-08-26 and has known defects. A correct, tested port is a real upstream contribution.

## Architecture in scope (text path)
Gated DeltaNet layers; Qwen Sparse Attention (QSA) with its indexer; hyper-connection residual streams; a 512-expert MoE (10 routed plus 1 shared); a sharded n-gram PLE embedding (about 51B parameters, at layer 1); norms with any `1 + w` folding; and MTP, only if correctness needs it. Vision is out of scope for v1.

## Authority
The official reference is `transformers` 5.22.1 `models/qwen4_exp`, with the official config and checkpoint `Qwen/Qwen3.8-Flash-Next`: 131 shards, 360 GB bf16. Community PR #1788 is read-only context and is never executed.

## Definition of done (all must hold)
1. **Two independent implementations.** A Sol 6.1 port (`lane/2026-11-05-align-flashnext-port`) and an Opus 5.5 twin (`lane/2026-11-05-align-flashnext-twin`), built blind to each other.
2. **Gold parity on tiny configs.** Every layer type is present. MLX matches transformers on a full prefill and on stepwise decoding with the cache: fp32 max abs logit difference ≤ 1e-4, bf16 within a stated, justified bound. Also: MLX prefill equals stepwise; batch-1 equals left-padded; KV trim plus re-prefill equals fresh; the DeltaNet state snapshot and restore is exact; quantized vs unquantized falls within the quantization bound.
3. **Differential.** The Sol and twin ports agree with each other on shared tiny weights. Every disagreement is resolved against the reference.
4. **One canonical module**, converged in mlx-lm house style (`mlx_lm/models/qwen4_exp.py` layout), loaded by JouleWise through the pinned mlx-lm 0.31.3 `model_file` hook (no pin bump), with its sha256 pinned.
5. **Real-weight layer parity.** For each layer type (DeltaNet, QSA, the MoE block, the n-gram PLE layer, embeddings and head), load the official weights for that layer from selected shards and compare MLX and torch reference outputs on identical hidden-state inputs, within a stated tolerance. This runs on the laptop or the Mac, layer by layer.
6. **Memory: a hardware constraint, not a goal (Ed, 2026-11-05).** The measurement Mac has 128 GB unified memory, with about 115.4 GB GPU working set by default. During measurement nothing may swap, because swapping invalidates energy data. Within that limit, run the HIGHEST precision that fits: page the n-gram table from disk and choose the core-model bits by measurement. The memory model reports resident bytes and must match measurement within 10 %.
7. **Real-model validation on the Mac.** The streaming conversion is reproducible, with a sha256 manifest. Coherence and NLL on fixed texts; a tool-call round trip through the real template; a fixed set of benchmark items whose behaviour is consistent with the model card; and, if a hosted reference exposes logprobs, a top-k logprob comparison on fixed prompts.
8. **Performance.** It reuses mlx-lm's Metal gated-delta kernels where they apply, with an efficient QSA indexer and MoE `gather_qmm`. Prefill and decode tok/s are measured at each `reasoning_effort` and recorded against the targets set in phase P5.
9. **Review.** Adversarial component review looped until two rounds find nothing new; one Fable 5.1 cold pass (a major checkpoint); Ed's `/code-review ultra` on the canonical PR.
10. **Upstream package.** mlx-lm-style tests (a `test_models.py` entry), convert support, docs and a draft PR text. **The PR to ml-explore/mlx-lm is opened only with Ed's go.**

## Phases
- P1: build the two ports (running).
- P2: gold parity plus differential.
- P3: converge to the canonical module.
- P4: real-weight layer parity.
- P5: performance kernels.
- P6: memory and paging.
- P7: Mac validation.
- P8: review loops, Fable, ultrareview.
- P9: upstream.

The status log is appended below as phases complete.

## Status log
- 2026-11-05: goal set. P1 is running: the Sol port and the Opus twin (a workflow: build, then 4 component reviewers, then a fixer), plus the engine-feasibility static review and the weights-logistics plan. Official shard layout: individual layers sit in about 3 shards (~10 GB); the n-gram embedding (layer 1) spans about 35 shards (~100 GB bf16).
- 2026-11-05: Ed reframed memory as a constraint, not a target. Proposed: dedicate the measurement MacBook Pro for about 2 days (ALIGN paused). With the full bf16 checkpoint on its SSD, P4 becomes full 48-layer real-weight parity, alongside on-box conversion and end-to-end runs. Awaiting the SSD size and the go.
