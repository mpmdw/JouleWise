# RQ exploration — Fable seat (basis: Paper C exists)

Assumed Paper-C facts, cited as PC-n:
PC-1 labelled attribution floor ≈1 J per phase; effective contrast bar ≈5 J; per-token resolution = bar/N.
PC-2 timing widening dominates scatter (R≥2): longer windows beat more reps.
PC-3 Q4 coefficients `E = fixed + a·p + b·d` fitted per model/quant with held-out shapes; session composition and prefix crossover resolved.
PC-4 decode is bandwidth-bound at near-flat power (≈23–28 W from 1.5B to 122B-A10B); energy differences are decode TIME.
PC-5 chunked KV-growth slope and context-nonlinearity onset known per model.
PC-6 token-shape sufficiency (category/content collapse to token counts at fixed shape) resolved.
PC-7 sampling energy variance decomposed into length vs residual.
PC-8 prefill resolvable only at ≥3 records (~0.34 s); short prefill printed `not resolvable`.
PC-9 quantization split (watts vs time), keep-warm breakeven, 128 GB failure frontier.
Levels: 512-token decode ≈47 J (1.5B), ≈192 J (7B), ≈304 J (122B-A10B); bar 5 J ⇒ ≈10 mJ/token over 512 tokens, ≈2.4 over 2048.
Window ≈3.5 h ≈ 80 members at ≤8B, ≈40 at 100B-class. Sizes are 4-bit MLX unless stated; NEEDS-WEB = runtime support unverified.

## Questions (bank "New questions" row format)

- **RQ-NEXT-BYTES-LAW Bytes-touched-per-token decode law:** Across dense and MoE at fixed quant, is decode energy/token one linear function of bytes read per token (active weights + KV), with resident-but-inactive bytes costing nothing? Ceiling L2/L3 via predeclared one-covariate fit + held-out model. Extends C5-1.1 (lifts its 4–6-point cap).
  Mechanism: PC-4 ⇒ E/token = P·bytes/BW_eff; resident size enters only if effective bandwidth drops (expert scatter, paging).
  Design: Qwen3 1.7B/4B/8B/14B/32B dense, Qwen3-30B-A3B, Qwen3.5-122B-A10B, Qwen3-Next-80B-A3B; p=256, d=2048; 14B held out. Math: 10%-of-47 J ≈ bar at d=512; at d=2048 resolution ≈1.3%. Windows: 3. Risk: quant group-size drift across sizes; per-prompt expert-load imbalance (record router stats).

- **RQ-NEXT-TOPK-KNOB Router top-k as an active-bytes dial:** Within one MoE artifact, does overriding top-k (4/8/16 on Qwen3-30B-A3B) move decode energy/token in proportion to active bytes with resident bytes fixed? Ceiling L2 work-matched, never output-matched. NEW.
  Mechanism: identical weights and KV; only experts loaded per token vary — the cleanest active-vs-resident isolation.
  Design: k∈{4,8,16}, p=256, d=1024, n=10; predicted +≈50 J per doubling ≫ 5 J. Windows: 1. Risk: top-k override surface (NEEDS-WEB); shared-expert term fixed; quality forbidden.

- **RQ-NEXT-MIXER-3B Attention mixer at matched ~3B active:** At one problem profile, do MLA (DeepSeek-V2-Lite 16B-A2.4B), GQA (Qwen3-30B-A3B), Gated-DeltaNet hybrid (Qwen3-Next-80B-A3B) and KDA hybrid (Kimi-Linear-48B-A3B) differ in decode slope vs position and prefill scaling with context? Ceiling L2 named-quadruplet, no class generalization. Extends RQ-AXI-HYBRID-PAIR; the D-041 KDA arm.
  Mechanism: GQA KV read grows linearly with context; MLA compresses it; delta/linear state is constant — the slope IS the mixer signature (PC-5).
  Design: p∈{512, 8K, 32K}, d=512, byte-matched roster per tokenizer; slopes normalized to each model's p=512 level. Math: 32K KV read ≈ weight bytes for GQA ⇒ tens of J over 512 tokens; hybrids ≈0. Windows: 3. Risk: MLX support for Kimi/DeepSeek-V2 (NEEDS-WEB); totals differ — pairs with BYTES-LAW.

- **RQ-NEXT-MIXER-120B 128 GB-class mixer triplet:** Do GLM-4.5-Air (full GQA, 106B-A12B), gpt-oss-120b (alternating sliding-window 128, 5.1B active, MXFP4) and Qwen3.5-122B-A10B (hybrid — verify) differ in prefill energy/prompt-token at 16K–128K and in decode slope? Ceiling L2. Extends C5-1.2 + RQ-AXI-HYBRID-PAIR.
  Mechanism: sliding window caps KV read; prefill is quadratic for full attention, linear for banded/linear layers.
  Design: p∈{2K,16K,64K,128K}, d=512, n=8; frontier recorded (PC-9). Math: 128K prefill ≈ minutes at ≈40 W ⇒ kJ ≫ bar. Windows: 4. Risk: quant formats differ — within-model slopes only.

- **RQ-NEXT-SPEC-SURFACE Speculative-decoding break-even surface from coefficients:** Can spec-on energy be predicted as target-verify steps + drafter steps from the two models' PC-3 coefficients, and where is break-even acceptance for 8B/32B/70B targets with 0.6B/1.7B drafters? Ceiling L2/L3 (predicted vs measured, held-out pair). Extends C5-2.5c.
  Mechanism: PC-4 ⇒ a batched verify step costs ≈ one decode step in bytes; break-even acceptance ≈ f(bytes_draft/bytes_target).
  Design: greedy (output-identical, so C-023-OUTPUT-IDENTITY holds by construction), d=1024, n=10; Llama-3.3-70B ≈40 GB, ≈10 tok/s ⇒ ≈1.5 kJ/512 tokens, 20% effects ≈300 J. Windows: 3. Risk: observed acceptance accounting.

- **RQ-NEXT-MTP Native multi-token prediction vs external draft:** At output identity, joules per committed token for native MTP heads (Qwen3-Next / Qwen3.5) vs draft-model vs baseline? Ceiling L2, separate family FAM-AXI-SPEC-NATIVE-MTP. Extends C5-2.5c MTP arm; contingent on an MLX MTP surface (NEEDS-WEB; AXI-SC was `unsupported` in July). Windows: 1 if supported.

- **RQ-NEXT-KVQ-SURFACE KV quantization × context surface:** Does kv_bits∈{16,8,4} save energy equal to (KV-byte saving × PC-5 slope) minus a fixed dequant term, on Qwen3-32B and Qwen3.5-122B at 2K/16K/64K? Ceiling L2, no quality-neutrality without divergence report. Extends C5-2.11.
  Math: 32B fp16 KV ≈262 KB/token ⇒ 17 GB per step at 64K ≈ weight bytes; halving ⇒ ≈25% ≈100 J over 512 tokens; net sign flips at short context. Windows: 3. Risk: 64K prefill on 122B near frontier.

- **RQ-NEXT-PHASE-CROSSOVER The prefill/decode crossover length p\*:** For each model, at what prompt length does prefill energy equal 512-token decode energy, and is p\*/d constant within a family (a device roofline signature)? Ceiling L2/L3 (predict p\* for held-out model). NEW; stands on PC-3, PC-4, PC-8.
  Mechanism: prefill is compute-bound (FLOPs ∝ active·p), decode bandwidth-bound; their per-token ratio is the machine's FLOP/byte ratio, model-invariant at fixed quant.
  Design: 4 models × p∈{512,1K,2K,4K,8K}, n=10; 8B at 4K ≈ 200–250 J each phase. Windows: 2. Risk: prefill_step_size confound (next row).

- **RQ-NEXT-PREFILL-CHUNK Prefill chunk size as an energy knob:** Does prefill energy/prompt-token fall with chunk size and saturate where GPU utilization saturates? Ceiling L2. NEW; only a labelled prefill floor (PC-1, PC-8) makes this prefill-only effect claimable.
  Design: prefill_step_size∈{256,512,2048,8192}, p=8K, 8B and 32B, n=10; ≈100 J prefill, 10% clears. Windows: <1.

- **RQ-NEXT-BATCH-KNEE Static-batch decode knee:** Does decode energy/token fall as 1/B until B×KV bytes ≈ weight bytes (predicted from PC-5), while prefill energy/token stays flat? Ceiling L2. Extends C5-2.2 Mac leg (AXI-SB `supported`).
  Design: B∈{1,2,4,8,16}, 8B and 30B-A3B, p=d=512; per-sequence 200 J → ≈40 J at B=8. Windows: 2.

- **RQ-NEXT-ROUTING×BATCH MoE routing concentration under batching:** At B>1, do tokens routed to shared experts amortize weight reads so that per-request energy tracks router concentration, with a predicted null at B=1 (expert ≫ SLC, no reuse)? Ceiling L2. Extends D-070 MOE×BATCH.
  Design: Qwen3-30B-A3B, B∈{1,4,16}, rosters engineered for concentrated vs dispersed routing, router stats logged. Windows: 2. Risk: MLX router hook.

- **RQ-NEXT-EPCA-LEVELS Energy per correct answer vs published difficulty:** At fixed shape with natural EOS under a cap, does energy per correct answer rise across MATH levels 1–5, and is the rise fully explained by emitted-token count (PC-6/PC-7)? Ceiling L2, correctness quarantined, never "difficulty causes energy". Extends C5-1.9/C5-I.2.
  Difficulty axis: MATH per-item level (published). Design: Qwen3-8B, 32B, 30B-A3B; thinking off/on as arms; 32 items/level. Math: level-window energy ≈ hundreds of J ≫ bar; the binomial guard (±17% at 32 items) dominates. Windows: 3. Risk: contamination (shape-only), cap hits under thinking.

- **RQ-NEXT-EPCA-MECHANISM Energy per correct answer across mechanisms at one profile:** On the same MATH strata, dense 32B vs MoE 30B-A3B vs hybrid 80B-A3B vs 122B-A10B at matched accuracy band — which mechanism buys a correct answer cheapest, and is the ordering level-stable? Ceiling L2 named set. Extends C5-1.9. Windows: 3 (shares rosters). Risk: predeclare accuracy bands, never post hoc.

- **RQ-NEXT-COEFF-LAW Coefficient scaling law:** Do the PC-3 coefficients (fixed, a, b) follow a law in (active bytes, KV bytes/token, resident bytes) across the BYTES-LAW panel, predicting a held-out model's held-out shape within the bar? Ceiling L3 through AP-1 holdout machinery only. NEW; extends Q4/C-023-COEFF-TRANSPORT. Windows: 0 extra (rides BYTES-LAW + PHASE-CROSSOVER).

- **RQ-NEXT-RESIDENT-IDLE Does resident memory cost idle power:** Is the fixed term a function of resident bytes (65–100 GB resident vs none), or is LPDDR5 self-refresh contents-blind (predicted null)? Ceiling L2. Extends C5-1.7.
  Math: 30 s idle ⇒ 1 W = 30 J; resolution ≈0.03 W. Windows: <1. Risk: macOS compression at high residency.

- **RQ-NEXT-FRONTIER-235B The 128 GB frontier:** Does Qwen3-235B-A22B at 3-bit (~100 GB) run, and does its energy/token sit on the BYTES-LAW line or above it (paging)? Ceiling L1/L2 frontier point. Extends C5-1.10. Windows: 1.

- **RQ-NEXT-ROOFLINE-DEVICE Second device as roofline falsifier:** On a 3080 Ti (912 GB/s, 12 GiB, board boundary), do BYTES-LAW and p\*/d rescale by the device's byte/FLOP ratio? Ceiling L2 per boundary; L4 only with calibration. Extends C5-2.7/Q6. Fits: Qwen3 1.7B/4B/8B. Windows: NV-gated, 2.

## What one week (~30 windows) buys
1. BYTES-LAW + COEFF-LAW + FRONTIER-235B (4 windows): the scaling law that turns Paper C into a predictive model.
2. PHASE-CROSSOVER + PREFILL-CHUNK (3): the roofline signature p\*/d — cheapest falsifiable prediction.
3. MIXER-3B + MIXER-120B (7): the north-star mechanism paper (KDA/linear/MLA/sliding).
4. SPEC-SURFACE + BATCH-KNEE + ROUTING×BATCH (7): dynamic-execution axes predicted from static coefficients.
5. KVQ-SURFACE + EPCA-LEVELS/MECHANISM (9): the applied paper; TOPK-KNOB and RESIDENT-IDLE fill gaps.

## Three boldest
1. TOPK-KNOB: one artifact, one dial — MoE active cost isolated without a family confound.
2. PHASE-CROSSOVER: p\*/d as a machine constant, predicted for a held-out model, then a held-out device — a roofline you can measure in joules.
3. ROUTING×BATCH: routing entropy as an energy knob — WHAT is asked changes joules through the router, not token count, and only under batching.
