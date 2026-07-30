# Related-work sweep — mechanism-level energy literature and candidate contrasts (2026-07-30)

**Origin:** delegated literature/landscape sweep, 2026-07-30 — Fable subagent
under the magistrate's 7B-floor-window session
(`abec37a6-31cd-4c56-a8a8-9448acaf12be`), agent `a83c5494c5a4c4533`. This file is the
agent's final deliverable message, extracted verbatim from the session
transcript; the raw JSONL transcript and the intermediate raw related-work
capture are session-scoped scratch and are deliberately NOT committed.

**Status:** desk research, not project evidence. Nothing here is a JouleWise
measurement, a claim, or a ratified decision. Adopted items become queue rows
or decision-log entries in their own right; see `TASK_QUEUE.md` intake batch
2026-07-30.

---

All verification done. Here is the deliverable.

---

# Mechanism-level energy literature sweep — reachability map for JouleWise

## (i) Mechanism-by-mechanism energy literature summary

**Attention variants (GQA / MLA / linear / delta / hybrid)**
- [arXiv 2605.11999](https://arxiv.org/abs/2605.11999) — GQA vs MLA vs Gated DeltaNet vs Mamba2 decode energy on H200. Key: decode draws only 137–300 W on a 700 W GPU across all variants (bandwidth-saturated before power-limited); clock locking recovers up to **32% of decode energy**; the linear/hybrid pattern shows heavy prefill recouped by cheap decode, **halving total request energy vs GQA** at production batch sizes.
- [Kimi Linear / KDA, arXiv 2510.26692](https://arxiv.org/abs/2510.26692) — KDA (finer-gated DeltaNet) + MLA hybrid, 48B-A3B released; **75% KV-cache reduction, up to 6× decode throughput at 1M context**. Throughput/memory claims only — no measured energy.
- Implied effect shape: full attention's J/token grows with context (KV reads); linear layers' does not. Nobody has published the on-device energy-vs-context *slope*.

**Speculative decoding**
- [arXiv 2504.17674](https://arxiv.org/abs/2504.17674) (Energy Considerations of LLM Inference; full numbers via HTML) — spec decode: **−29.14% energy at batch ≤16, +25.65% at batch 128** (verify overhead dominates when compute-saturated). Combined optimizations: up to 73% total reduction.
- [TokenPowerBench, arXiv 2512.03024](https://arxiv.org/html/2512.03024v1) — J/token, J/response metrics; corroborates ~29% small-batch savings.
- [Survey 2411.13157](https://arxiv.org/abs/2411.13157) — latency-only; **no energy numbers** in the survey. Batch-1 on-device (the regime where spec decode should help most) has *no published energy measurement anywhere I found*.

**Multi-token prediction (MTP)**
- No measured energy results found at all — only speedup claims (2–3×, e.g. [FastMTP](https://openreview.net/forum?id=J7xDwZSyI4), [vLLM MTP docs](https://docs.vllm.ai/en/latest/features/speculative_decoding/mtp/)). Open checkpoints with MTP heads: [MiMo-7B](https://deepwiki.com/XiaomiMiMo/MiMo/2.2-multiple-token-prediction), DeepSeek-V3, Qwen3-Next.

**MoE (routing, expert count, shared experts)**
- [arXiv 2606.21428](https://arxiv.org/abs/2606.21428) — **the one Apple-silicon paper**: OLMoE-1B-7B vs Llama-3.2-1B on M2 Pro + Jetson. MoE = **2.1× energy/token on Jetson**, ~10% behind on M2 Pro; **routing itself is <9% of MoE-block compute** — the penalty is total-parameter footprint, dispatch, KV pressure.
- [arXiv 2504.17674](https://arxiv.org/abs/2504.17674) — MoE **+54.24% energy vs dense OLMo-1B at matched active params** (A100-class).
- [Where Do the Joules Go, arXiv 2601.22076](https://arxiv.org/html/2601.22076v1) — opposite regime: MoE **3.56× less energy** than dense of similar *total* params (H100/B200, vLLM, large batch). The dense-baseline convention (matched-active vs matched-total) flips the sign — a point of genuine confusion the literature hasn't resolved cleanly.

**KV cache (size, quantization, paging)**
- [KVQuant 2401.18079](https://arxiv.org/pdf/2401.18079), [SKVQ 2405.06219](https://arxiv.org/pdf/2405.06219), [KV-compression review 2508.06297](https://arxiv.org/html/2508.06297v1) — 4.8× compression, latency wins, up to ~7× theoretical speedup at 200k ctx — **all memory/latency; zero measured J/token anywhere**. 2601.22076 shows KV pressure raises energy/token 1.5–2.1× indirectly (batch limiting).

**Weight quantization**
- [arXiv 2504.03360](https://arxiv.org/pdf/2504.03360) (edge), [Price of Prompting 2407.16893](https://arxiv.org/pdf/2407.16893) — 4-bit gains **1.35–2.95×** total energy vs unquantized; one edge benchmark shows Llama-3.2-1B fp16=159 J/tok, q8=76, q4≈84 (q4 *worse* than q8 — dequant-bottleneck anomaly worth testing). Caveat everywhere: savings require hardware-native low-precision paths.

## (ii) Concrete measurable pairs (runtime status)

| Contrast | Arm A | Arm B | 4-bit size | Runtime status |
|---|---|---|---|---|
| Spec decode on/off | Qwen2.5-7B (or Qwen3-8B) alone | same + 0.5B/0.6B draft | ~4.4 GB | **Verified**: `mlx_lm.generate --draft-model` exists ([issue #250](https://github.com/ml-explore/mlx-lm/issues/250), [#1132](https://github.com/ml-explore/mlx-lm/issues/1132)) |
| Weight quant ladder | model-4bit | same model 8bit / bf16 | 4–16 GB | **Verified** (mlx-community ships all levels) |
| KV-cache quant | `--kv-bits 4` | fp16 cache | same model | **Verified**: kv quantization in mlx-lm ([mlx-examples #1075](https://github.com/ml-explore/mlx-examples/commit/85ffd2c)) |
| MoE vs dense (matched active, same family) | mlx-community/Qwen3-30B-A3B-4bit (**verified exists**) | Qwen3-4B-4bit | ~17 GB vs ~2.3 GB | Qwen3-MoE runs widely in mlx-lm (checkpoint verified; arch file not individually confirmed — *low risk*) |
| MoE vs dense (lit-comparable) | OLMoE-1B-7B (`olmoe.py` **verified in mlx-lm**) | OLMo-2-1B / Llama-3.2-1B | ~4 GB | Verified arch file; replicates 2606.21428's exact pair |
| Hybrid delta-attention | mlx-community/Kimi-Linear-48B-A3B-Instruct-4bit (**verified exists**; `kimi_linear.py` **verified in mlx-lm**) | Qwen3-30B-A3B (full-attn MoE, similar active) | ~27 GB | Cross-model confound; long-context stability in MLX **unverified** |
| Hybrid GDN | mlx-community/Qwen3-Next-80B-A3B-Instruct-4bit (**verified exists**; `gated_delta.py` in mlx-lm) | Qwen3-30B-A3B | ~45 GB | **Unverified** end-to-end |
| MoE top-k knob | Qwen3-30B-A3B, `num_experts_per_tok=8` | same checkpoint, k=4 (config edit) | same weights | **Unverified but mechanically plausible** — single-mechanism, same-weights knob |
| MTP | MiMo-7B-Base (heads in checkpoint) | — | — | **Not reachable**: no MLX MTP support (vLLM only) |
| RWKV / RecurrentGemma / Zamba | — | — | — | **Not in mlx-lm** — drop |

## (iii) Ranked reachable claims — effect/floor arithmetic

Baseline: 7B-4bit decode = 0.376 J/tok, 1.5B = 0.098 J/tok (JouleWise measured). Floor: 6–14 J now, ~2–5 J after tightening. Workload 512–8192 tok.

| Rank | Contrast | Effect estimate | Δ at feasible workload | Effect/floor (14 J) |
|---|---|---|---|---|
| 1 | Weight quant 4b vs 8b (7B) | +60–90% J/tok (bandwidth ∝ bytes) → Δ≈0.22–0.34 J/tok | ×2048 tok ≈ **450–700 J** | **~35–50×** |
| 2 | Spec decode on/off (7B+0.5B) | ±10–30% → Δ≈0.04–0.11 J/tok | ×2048 ≈ **80–230 J** | **~6–16×** |
| 3 | MoE vs dense matched-active | +30–100% of ~0.1–0.15 J/tok dense | ×2048 ≈ **60–300 J** | **~5–20×** |
| 4 | KV-quant 4b vs fp16, long ctx | Qwen2.5-7B KV ≈57 KB/tok fp16 → ~9.6% of decode bandwidth at 8k ctx; save ~75% of it ≈ 3.5% avg over 0→8k | ×8192 ≈ **~100 J** (concentrated late — phase resolution helps) | **~7×** at full 8k; marginal below 4k |
| 5 | Hybrid-linear vs full-attn: J/tok-vs-context slope | GQA slope from KV reads; linear ~flat; tens of % at 16–32k ctx | context-sweep design, per-point Δ ≥ 50–100 J | ~5–10× (**runtime risk**) |
| 6 | MoE top-k slope (same weights) | expert-FFN energy ~∝ k; maybe 20–40% of J/tok | ×2048 ≈ 100–250 J | ~10× (**mechanism knob unverified**) |
| — | MTP | — | — | **unreachable** (no runtime) |

All effect estimates except row 1's bandwidth scaling are extrapolations from server-class literature — flagged as such; that gap is the point.

## (iv) What each claim says that the literature can't

1. **Spec decode**: "On batch-1 unified-memory inference, speculative decoding changes decode energy by X% ± CI" — first *measured* on-device energy verdict incl. the **sign** (all lit is server GPU batch sweeps; mlx overhead could plausibly flip it — issue #250 hints the spec-decode step is slower).
2. **Quantization**: CI-bounded J/token-vs-bits curve on Apple silicon, adjudicating the q4>q8 anomaly the edge literature reports without error bars.
3. **MoE**: whether the +54% matched-active GPU penalty survives unified memory, phase-resolved — direct extension of 2606.21428 (M2 Pro, one pair, coarse) with the sign-flip (matched-active vs matched-total) pinned down on one instrument.
4. **KV quant**: the first measured energy number of any kind — lit has only memory/latency.
5. **Attention slope**: on-device d(J/tok)/d(context) for hybrid-delta vs full attention — 2605.11999 is H200-only and whole-request.

## Top-3 recommended first campaigns

1. **Speculative decoding on/off (Qwen2.5-0.5B→7B, models already characterized)** — cleanest single-mechanism ABBA in existence (identical target weights, flag-toggled), verified runtime, open sign question, 6–16× floor clearance.
2. **Weight-quant ladder (Qwen 7B/8B at 4/8/16-bit)** — 35–50× floor clearance, checkpoints trivially available, and it calibrates the bytes-moved→joules model every other campaign's predictions rest on.
3. **MoE vs dense matched-active (Qwen3-30B-A3B vs Qwen3-4B, plus the OLMoE/OLMo-2 lit-replication pair)** — settles the matched-active vs matched-total sign flip on unified memory and directly extends the only existing Apple-silicon result.

Sources: [2605.11999](https://arxiv.org/abs/2605.11999) · [2504.17674](https://arxiv.org/abs/2504.17674) · [2606.21428](https://arxiv.org/abs/2606.21428) · [2411.13157](https://arxiv.org/abs/2411.13157) · [2510.26692](https://arxiv.org/abs/2510.26692) · [2601.22076](https://arxiv.org/html/2601.22076v1) · [2512.03024](https://arxiv.org/html/2512.03024v1) · [2504.03360](https://arxiv.org/pdf/2504.03360) · [2401.18079](https://arxiv.org/pdf/2401.18079) · [2405.06219](https://arxiv.org/pdf/2405.06219) · [mlx-lm models](https://github.com/ml-explore/mlx-lm/tree/main/mlx_lm/models) · [mlx-lm #250](https://github.com/ml-explore/mlx-lm/issues/250) · [mlx-lm #1132](https://github.com/ml-explore/mlx-lm/issues/1132) · [mlx-examples #1075](https://github.com/ml-explore/mlx-examples/commit/85ffd2c96a45a8cb900f95a2ded61d858d673399)