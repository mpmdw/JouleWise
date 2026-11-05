# GOAL: a complete, validated MLX port of Qwen3.8-Flash-Next (`qwen4_exp`)

Owner: laptop lead (Opus 5.5), set by Ed on 2026-11-05: "make that a major separate goal and branch of joulewise - i want to spend significant tokens on it ... don't stop til you've architected tested and validated a whole" port. Long-lived branch: `port/qwen4-exp-mlx`.

## Why
- Qwen3.8-Flash-Next is the strongest open model that fits on the 128 GB M3 Max measurement Mac (Artificial Analysis Progress Index v1: 320, against 303 for Qwen3.8-27B and 225 for Qwen3-Next-80B). ALIGN / SHADE-Arena needs agents capable enough to attempt deception.
- CORRECTION (2026-11-05): the model IS already supported elsewhere. **mlx-vlm** (Blaizzy) supports Qwen3.8-Flash-Next text+vision (Qwen's README recommends it for Apple Silicon); **llama.cpp** merged support 2026-08-27 (PR #27742); community MLX quants exist (4-bit, 6-bit, mixed 4/8: pipenetwork, Vontra, RockTalk) and an MLX Swift implementation exists. Only the text-only **mlx-lm** PR #1788 is unmerged. The lead's earlier 'no MLX support' claim was wrong.
- Remaining contribution: (a) a verified-correctness AUDIT of the existing ports (mlx-vlm, llama.cpp) with the gold harness against the official reference on real weights, upstreaming fixes for any discrepancy found; (b) the highest-fidelity 128 GB build: 6-bit experts, everything else bf16, and the bf16 n-gram table paged from SSD, offering PLE paging upstream (mlx-vlm); (c) for JouleWise, our own port on the PINNED stack, verified, for measurement integrity.

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
11. **Gold validation on the measurement MacBook Pro (Ed, 2026-11-05: "make this one of the goals ... i'm down to wipe/offload everything on the macbook to the cloud").** Free about 450 GB+ on the MBP SSD by offloading every data root to cloud storage. The rule is verify-then-delete: sha256 must match against a second copy, and no irreplaceable measurement data is ever deleted unverified. Then download the full 360 GB official bf16 checkpoint and run FULL 48-layer real-weight parity: stream each layer's official weights through the MLX port and the transformers reference on identical inputs, with all layer types, the real n-gram table, the final norm and the head. Then convert on-box (sha256 manifest) and run the end-to-end checks of item 7. ALIGN is paused for about 2 days for this.
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
- 2026-11-05: Ed approved item 11 (offload everything on the MBP to the cloud, full bf16 on its SSD). Runbook and gold-parity harness lanes started.
- 2026-11-05: MBP SSD = 1 TB (Ed). The lead revised item 11's plan to a STREAMING gold pass: per layer group, download its shards, run gold parity, convert, then delete the bf16. Peak free disk is about 110-120 GB (converted model about 95 GB plus the largest working unit). Minimal verified offload to about 150 GB free; no wipe needed. The block-5 originals stay on-device until after the release.
- 2026-11-05 11:20Z: P1/P2, the Sol port (`lane/2026-11-05-align-flashnext-port`, e9f5ed799) PASSES native gold parity against transformers 5.22.1: fp32 max abs 6.0e-8 prefill and stepwise; bf16 0.00195; prefill==stepwise, padding, snapshot/restore and trim exact. Conversion tests 3/3, zero skips. Native tests run by the lead because the Codex sandbox has no Metal. Waiting on the Opus twin for the differential.
- 2026-11-05: **Target precision, Ed: "as close to the full fp16 as i can get".** Computed with the port's memory model from the real config at 40,960 context:
  - experts bf16: 256 GB peak; experts 8-bit: 142.9 GB. Both are impossible on 128 GB.
  - **experts 6-bit (group 64) with every other weight in native bf16: 108.0 GB weights, 112.7 GB peak**, under the 115.4 GB default GPU working set.
  - experts 5-bit: 97.6 GB peak.
  - DEFAULT: 6-bit experts, everything else bf16 (4.9B params), and the n-gram table bf16 ON DISK (102.4 GB, paged; page cache at most about 21.5 GB worst case, made of evictable file pages, not swap).
  - Pre-committed fallback: 5-bit experts if the measured peak, swap counters or headroom fail on the Mac.
  - Disk: about 210 GB, so an external NVMe is required.
  - Quantization error is measured, never assumed: per-layer quantized vs bf16 on real weights, plus end-to-end against the hosted bf16 reference.
- 2026-11-05: **P10 stretch (optional, after core validation): expert streaming.** All experts on SSD at 8-bit or bf16, with a RAM LRU cache of hot experts and the misses read on demand (M3 Max TB4 external at about 3 GB/s, internal at about 6 GB/s). The purpose is an on-device near-lossless quality reference that measures the 6-bit gap. It is NOT for ALIGN energy windows, where SSD I/O would confound energy. Reads do not wear flash. Upstreamable like PLE paging.
- 2026-11-05: Ed asked whether anyone had already ported it. The lead verified (mlx-vlm models/qwen4_exp; llama.cpp PR #27742 merged 2026-08-27; QwenLM README) and corrected the GOAL framing. The existing ports become extra differential references.
- 2026-11-05 ~12:00Z: real-weight parity of layers 2 and 3 PASSES (PR #669: fp32 rel <= 5.8e-6, identical experts; bf16 within 2x of the official error). QSA exact-zero tie rule: fix in progress. Support tracks done: perf kernels #670, e2e harness #671, upstream readiness #672, all SOUND_WITH_FIXES. For convergence: the canonical indexer must use HF-exact bf16 RoPE (cos/sin cast to model dtype; mx.fast.rope fp32 changes bf16 selection beyond ties), the router must rank fp32 probabilities, and the DeltaNet eps adapter is 1e-6/Dk. Upstream: mlx-lm forbids AI-written PR text, so Ed writes it.
- 2026-11-05: **Stack upgrade path (Ed asked about the newest MLX).** Stay on the pinned mlx 0.31.2 / mlx-lm 0.31.3 through the current anchored ALIGN series, because anchor comparability and the registered runtime identities depend on it. Upgrade at a clean boundary (e.g. the start of the Flash-Next phase) via a **bridging window**: the same anchor trajectories on the old and new stack back to back, to measure the stack energy offset. Then migrate everything, including this port (model code only; small API updates such as main mlx-lm requiring trust_remote_code for model_file). Benefits: newer fused kernels, the batch-RoPE fix, and running mlx-vlm in-stack as a cross-check.
- 2026-11-05 ~14:30Z: **P3 DONE: canonical module** (PR #675, `lane/2026-11-05-qwen4exp-canonical`, module sha256 55aecaea…). fp32 gold <= 9.8e-6 across 9 scenarios; greedy 32/32 identical; bf16 1.09x / 1.07x of the reference noise (bounds 1.25 / 1.5); maxfit 1.11x; 4,101-token sparse kernel prefill 8.2e-6; isolated components bitwise or about 1 ulp. The QSA core matches 0.485 bitwise, a torch SDPA artifact (D9). An independent reviewer fixed 2 bugs. P2 differential (Sol vs twin) agreed to float noise in fp32. Next: P4 real-weight parity of the canonical module, P8 adversarial review plus the one Fable checkpoint pass, then Eds ultrareview of #675.
- 2026-11-05 ~17:00Z: **P4 (laptop shards) + P8 round 1 done.** Real-weight parity of the canonical module on L2/L3, embed/head and the PLE shard: ADMIT, 13/13 PASS. bf16 is 1.00-1.06x the official error, and end-to-end bf16 top-1 vs the fp32 truth is 51/54 canonical vs 47/54 official. The validation workflow (numerics, systems, Fable cold pass) found 18 findings; all are fixed or corrected with fail-before/pass-after regressions (31 canonical tests). Module sha256 is now f4ec75d1…; artifact format v2. Ready for Eds `/code-review ultra 675`. Still to do: the full 48-layer gold run on the MBP (SSD arriving in about 2 days), P5 perf on the Mac, P9 upstream.
