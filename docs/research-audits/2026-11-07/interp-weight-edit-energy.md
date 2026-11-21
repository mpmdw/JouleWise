# Interp × energy: surgical weight edits, power and performance

**Status.** Design study, not a registration. No Mac time is committed by this document. Written 2026-11-07 by the laptop lead (Opus 5.5) from two blind design seats (Fable 5.1 and Opus 5.5, reports verbatim in Appendix A) and 36 novelty and physics checks: each of the 18 seat ideas was attacked once by a Fable 5.1 checker and once by an Opus 5.5 checker. The checks are kept verbatim in the companion file `interp-weight-edit-energy-checks.md`. The lead re-opened the key external sources in this session (marked **[L]** below) and re-read every repo line cited.

**Why it exists.** Ed, 2026-11-07: "im mainly interested in interp work, wrt the recent 'gpt 6 astra can natively edit model weights' type research theres an interesting intersection between how surgical weight alterations change power consumption AND performance - but power feels like an increasingly difficult signal to pull out of the noise of machines running so many things". `docs/research/AGENDA.md` (§ "Interp × energy") points here.

**Priority.** This is a new line and is banked behind what Ed already ranked: measurement-Mac experiments 1 and 2 first, 3 and 4 banked (`docs/research/AGENDA.md`, PR #698), BYTES stage 1 (12 Nov), the ALIGN windows and the Paper 1 freeze. Stage 0 below is desk work only; nothing here asks for a Mac window before those.

**Source marks.** **[L]** = opened by the lead in this session. **[S1]**/**[S2]** = opened by seat 1 (Fable) or seat 2 (Opus). **[C]** = opened by at least one check (the check that opened it is named in the checks file). **UNVERIFIED** = nobody in this run opened it. **[estimate]** = arithmetic or judgement, not a measurement. Repo lines are at `origin/main` @ `20413903b` unless a branch is named. Two sibling audits are not on main yet: `research-program.md` (PR #695, identical on `origin/research/2026-11-07-research-program`) and `methodology-vs-literature.md` (PR #698, identical on `origin/research/2026-11-07-methodology-vs-literature`), both under `docs/research-audits/2026-11-07/`; their line numbers refer to those branches.

---

## 0. Executive summary (for Ed)

1. **Your reference is real.** It is a blog post, not a paper: Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming", 2 Nov 2026, https://rikiyat.github.io/blog/weight-space-programming/ **[L]**. GPT-6 Astra edited a *different* model, Qwen3.5-0.8B. It traced looping to one direction written by the MLPs of layers 15 and 19 and subtracted it from 64 output columns in each: 131,072 weights, 0.016% of the model. With a 50-forward-pass budget, MATH-500 rose from 7.9% to 48.1% (GSM8K 13.8 → 67.1%, IFEval 21.0 → 62.3%), and the share of MATH-500 answers hitting the 32,768-token cap fell from 93.0% to 33.1%. The 10- and 25-pass budgets barely moved looping (87.2%, 86.4%). The authors say editing "could remove an obstacle that hid an ability, but it could not add an ability the model lacked"; Gemma 3 270M, which rarely loops, did not improve. The post reports no energy, power or latency numbers. Critique: Goedecke calls the procedure "basically the Heretic abliteration playbook" and "exactly what a competent human researcher could have and would have done" **[L]**. An independent rerun of the authors' released diff (Coletti, Hugging Face card) **[L]** found MATH-500 7.4% (93% cap hits) → 50.2% (32%) with thinking on, but **base with thinking off already scores 45.8% at 32% cap hits**: against the base model's best setting the edit gains +4.3 points [1.9, 6.8]. The diff and the edited weights are public.

2. **What is physically plausible.** A weight edit can move energy through three channels: **(b) behaviour** (how many tokens, at what context length), **(c) structure** (bytes moved, kernels launched, experts or rows touched), and **(a) switching** (bit-toggle power at identical work), plus a second-order coupling of (a) into clock frequency. For surgical edits (rank-one/ROME, direction ablation and abliteration, steering folded into weights, Astra) the ranking is **(b) ≫ (c) = 0 ≫ (a)**. The Astra edit should cut tokens per problem from about 30.8k to 13-16k and tokens per correct answer by about 12-15× (arithmetic from the published rates, §1.2). Its fixed-token switching effect is at most about 3 × 10⁻⁵ of energy under a deliberately generous bound and more likely 10⁻⁶ or below (§1.1).

3. **What our rig can and cannot see.**
   - **Behaviour-mediated energy: trivially.** A 15k-token difference is about 1-2 kJ per problem against a token-identical replay floor of about 2-3 J (§2).
   - **Structural edits** (requantization, structured pruning, top-k): percent-level and already inside the BYTES and RQ-NEXT-TOPK-KNOB lineages.
   - **Statistics-changing edits** (large-fraction zeroing, outliers, sorted weights): unknown on Apple silicon. NVIDIA GEMM moves up to about 40-67% between extreme fills, but our decode is memory-bound and 85% of the known-bytes GPU-rail contrast was stall time. This is the one genuinely open physics question here.
   - **Surgical edits at fixed tokens: not detectable.** The best affordable design bounds them at about 0.04-0.1% of episode energy (16-64 replay pairs). Detecting a 10⁻⁵ effect would need about 95,000 pairs. The honest deliverable is a bound. The one surgical case a bound could conceivably reach is a projection folded into every residual writer (abliteration-style), because it touches about a third of the streamed bytes.

4. **Your noise caveat, answered.** It bites only where we would not look anyway. Background load is not the binding problem: under randomized interleaving it becomes variance, and in the known-bytes hour the daemons' asymmetry between arms was 0.2% of the rails half-width (`KB-SLOT-FILL.md:81`). What binds is (i) the *size* of the switching effect for surgical edits, and (ii) the possibility that Apple's software rails are modelled from activity, frequency and voltage, in which case they cannot see operand data at fixed activity at all. Intel's RAPL fix did exactly that ("falls back to a model-based approach, such that same instructions with different data or operands can not be distinguished", PLATYPUS **[L]**), and the Zeus Apple-silicon README says IOReport energy values "are believed to be model-based estimates derived from utilization, frequency, and voltage" **[L]**. So any switching claim needs the KM003C DC meter as arbiter. A "DC moves, rail flat" outcome would itself be a publishable instrument result about the meter every Mac energy paper uses.

5. **Single best first experiment: ASTRA-2CH**, a two-channel decomposition of the published Astra edit (Stage 1, §4). One MBP window, delivered as a magistrate kit after a desk Stage 0:
   - **Behaviour channel:** free-running on about 40 MATH-500 problems with paired seeds, four arms: base thinking-on, edited thinking-on, base thinking-off, base thinking-on with an 8k cap.
   - **Physics channel:** about 12 edited-arm sequences replayed token by token, teacher-forced, through both weight sets in ABBA order, with an A/A′ null. This gives a bound on the switching residual.
   - **Positive control and instrument check:** a graded synthetic zero/random/sorted fill ladder at fixed shape, read on the GPU rail, IOReport and the DC meter.

   Expected outcome: about 1-2 kJ per problem between base and edited thinking-on, almost all explained by tokens plus a context term; a switching residual equivalent to zero within about 0.1%; and the comparison that matters for interp: **does the edit buy accuracy at a joule price relative to simply turning thinking off?** Ask: Ed's approval to download Qwen3.5-0.8B (about 1.6 GB bf16) and the authors' diff. It also needs a teacher-forced decode loop, which the repo does not have (the ALIGN endpoint is pinned greedy: `joulewise/align/apple/endpoint.py:273-276 @ cda28a5ef`).

6. **What not to do.** Per-head energy attribution (10-100× below the floor). Router-temperature edits (softmax is monotonic, so the top-k set does not change). Standalone DVFS-coupling or tamper-fingerprint nulls (predetermined by regime or by construction). Building a lock-in instrument before measuring the noise spectrum it is meant to beat.

7. **Payoff for interp.** The defensible paper is "energy audits the *work* and the *precision* of a model and is blind to its *weights*, with a measured bound on the last clause", plus the first metered energy-capability frontier of an interp weight edit (the checks found none published). That joins ALIGN's finding that the instrument is a work counter that is blind to intent (`research-program.md:375`).

---

## 1. The energy channels, with literature numbers

At fixed kernel shapes, E = ∫ (P_static(T, V) + Σ α·C·V²·f) dt. An edit can change E through:

| Channel | Mechanism | Literature numbers | Our rig | Edits that use it |
|---|---|---|---|---|
| **(a) switching** | activity factor α at fixed instructions and time | ALUPower (Lucas & Juurlink, MASCOTS 2016): one kernel 155-257 W "depending on the processed values" [S1, C]. Bhalachandra et al. 2022 (arXiv 2212.08805): up to 67% on A100 DGEMM **[L]**. Gregersen, Patel, Choukse 2024 (arXiv 2409.18324): GEMM power changes by "almost 40%" with value distribution, bit similarity, placement and sparsity; bit flips are hypothesized, not shown **[L]**. Power-capped A100: zeros 295 vs randn 257 TFLOPS (H. He, thonking.ai) [S2, C] | 85% of the known-bytes GPU-rail contrast is the GPU powered while stalled; GPU frequency matched to 0.08 MHz across arms (`KB-SLOT-FILL.md:63,72-76`). Decode is memory-bound, so the data-dependent share of decode energy should sit well below compute-bound GEMM spans [estimate] | zeroing, pruning in place, outlier injection, requantization; surgical edits only as a bound |
| **(a) on Apple silicon** | software-visible data dependence | Hot Pixels (Taneja et al., arXiv 2305.12784) **[L]**: IOReport via a modified SocPowerBuddy at 10 ms. M1 Air iGPU: Hamming distance r = −0.971 with power, −0.951 with frequency; Hamming weight −0.963 / −0.961. M1 Air CPU add-1 vs add-0: 2.85 GHz / 11.7 W vs 2.88 GHz / 12.0 W. Fan-cooled M1 MBP and Mac mini are "usually frequency constrained": leakage shows in power and temperature, not frequency (MBP add-1 vs add-0: 12.86 vs 12.83 W). RX 6600 full Hamming-weight sweep: 97.5-98.1 W (about 0.6%). Chawla et al. (arXiv 2306.16391): data-dependent SMC power keys on M1/M2, AES key bytes recovered from user space **[L]**; per a check reading the full text, the IOReport PCPU channel showed no data dependence [C] | No published characterization of matmul or LLM kernels on Apple GPUs was found (several searches, not exhaustive). Whether our GPU rail is measured or modelled is unknown | the S1 ladder (§3) |
| **(a) in DRAM** | I/O and core current depend on bit values | Ghose et al., SIGMETRICS 2018 (arXiv 1807.05102): DRAM power "strongly depends on the data value", 50 DDR3L modules **[L]**; all-ones reads draw on average 39.2% (up to 91.6%) more than all-zeros [S2, C, full text] | LPDDR5 on the M3 Max uses low-swing signalling terminated to ground; DBI and scrambling on Apple's controller are unknown. A plausible LPDDR5 effect is 0.003-0.006 J/GB [C, estimate], below the DC contrast resolution | DRAM fill study (banked) |
| **(b) behaviour** | number of forward passes and their context length | Astra: cap hits 93.0 → 33.1% **[L]**. ASC (Azizi et al., arXiv 2507.04742): up to 67.43% shorter CoT, 2.73× wall-clock on an 8B, an inference-time vector, no energy measured **[L]**. ThinkEdit (arXiv 2503.22048, EMNLP 2025): about 4% of heads, about 0.2% of parameters, *fixes overly short* reasoning, +3.34% accuracy **[L]**. Luo et al. (arXiv 2609.29707, Blackwell): per-token energy differs by less than 1% between thinking modes while thinking emits 21-75% more tokens **[L]**. Wu et al. (NeurIPS 2026 workshop): a prefill + decode + KV-context law, R² = 0.961, preferred over token-count-only models **[L]** | ALIGN Qwen3-30B-A3B 4-bit: in-context decode e = 0.495-0.667 J/token (`research-program.md:113`), bare decode about 0.18 J/token (`:249`, citing RECORD 7e06863b:39). Planning figure: 512-token decode ≈ 47 J at 1.5B, about 0.09 J/token (`docs/research_question_bank.md:1616`). PC-4: decode is bandwidth-bound at near-flat 23-28 W, so decode energy differences are decode time (`:1608`) | every edit that changes what the model says: loop removal, refusal removal, length steering, P-DoS-style length attacks |
| **(c) structure** | bytes, kernels, routing count | KB coefficients (rotate minus repeat, 32 MiB latency-bound dispatches): GPU rail 0.00879 ± 0.00010, rails 0.0092 ± 0.0021, DC 0.0389 ± 0.0072, rest 0.0296 ± 0.0084 J/GB (`KB-SLOT-FILL.md:20-23`); transfer to bandwidth-bound decode is a stated limit (`:77`) | Unstructured zeros in dense MLX kernels change neither bytes nor FLOPs. In MLX affine 4-bit a zero weight is not code 0, so "zeroing" a 4-bit tensor may not produce zero operands [C]. A runtime SAE hook adds about 1.07 GB of bf16 reads per hooked layer for a 65,536-wide SAE at d = 4,096 [S2, arithmetic]. An unmerged LoRA adds kernels *and* fp32 A/B bytes [C] | structured pruning, requantization, top-k, runtime hooks |
| **(d) coupling** | switching power → DVFS → time | Hertzbleed (x86) [C]; Hot Pixels (passively cooled Apple parts) **[L]** | Sustained decode pins the M3 Max GPU near 1,380 MHz with idle_ratio 0.0 at about 22 W (`docs/research_question_bank.md:122-134`), the frequency-constrained regime, so coupling is predicted null on the MBP and sign-inverted on the fanless Air | a covariate, not an experiment |

### 1.1 How big can the switching term be for a surgical edit?

ΔE/E ≲ f_bytes × |Δα/α| × s_dd, where f_bytes is the share of streamed bytes the edit touches, |Δα/α| the change in toggle activity within them, and s_dd the data-dependent share of the power on that boundary [S2's bound; the checks agree on its order]. Two settings bracket it [estimate]:
- **Generous:** the touched bytes swing the full extreme-fill range (|Δα/α| ≈ 0.4, the Gregersen span) and half of the power is data-dependent (s_dd = 0.5), so ΔE/E ≲ 0.2 f.
- **Statistics-preserving:** a small dense perturbation leaves zero fraction, Hamming weight and transition density nearly unchanged (|Δα/α| ≲ 10⁻²), so ΔE/E ≲ 5 × 10⁻³ f. Even this is an upper bound; the checks expect far less for projections that only nudge low mantissa bits.

| Edit | f_bytes | Generous bound | Statistics-preserving bound | Notes from the checks |
|---|---|---|---|---|
| Astra (2 × 64 columns of `down_proj`) | 1.6 × 10⁻⁴ | 3 × 10⁻⁵ (≈ 0.08 J on a 2.5 kJ problem) | 8 × 10⁻⁷ | sub-0.1 mW expected |
| ROME, one `down_proj` in a 7B | about 0.7% [C] | 1.4 × 10⁻³ | 3.5 × 10⁻⁵ | 0.4-3.5 mW if every touched bit flipped [C] |
| Abliteration over all residual writers | about 0.3 [C] | not meaningful | 1.5 × 10⁻³ | 19-155 mW (0.2-1.5% of the GPU rail) only if every touched bit flipped; realistic ≪ 0.1 mW because a one-direction projection keeps the value distribution [C]. Still the best case for any non-null, so it is the primary surgical arm in Stage 2 |
| Zero-ablating one head (activation) | about 1/(12·H·L) of MACs, ≈ 8 × 10⁻⁵ for L = H = 32 [C] | about 1 mW | — | 0.1-0.5 mW in prefill, less in decode [C] |
| 50% unstructured zeros in one `down_proj` | about 0.3-1% of bytes | — | — | 1-10 mW [C], **not** seat 1's 0.1-1 W |
| 50% zeros across all MLP weights | about 0.6 | — | — | unknown on Apple; the useful positive control |

Two checks independently found seat 1's single-matrix positive control (0.1-1 W) too large by one to two orders. A positive control has to be large and graded: whole-model ladders, not one matrix.

### 1.2 How big is the behaviour term for Astra?

From the published rates only, with the cap at 32,768 tokens and L the mean length of an answer that does not hit the cap [estimate]:

| L (tokens) | Base tokens per problem | Edited tokens per problem | Tokens per correct, base / edited |
|---|---|---|---|
| 3,000 | 30,684 | 12,853 | 388k / 26.7k = 14.5× |
| 5,000 | 30,824 | 14,191 | 390k / 29.5k = 13.2× |
| 8,000 | 31,034 | 16,198 | 393k / 33.7k = 11.7× |

At 0.05-0.15 J/token for a 0.8B bf16 model [estimate; fit fresh coefficients, because the ALIGN 0.18-0.67 J/token figures are for a 30B-A3B MoE at about 12k context and do not transfer], a capped base problem is about 1.6-5 kJ and the base-edited difference about 0.8-2.5 kJ per problem. The ">2× J per correct" headline is arithmetic before any joule is measured; the meter adds the *context* term and the residual, not the ratio.

Qwen3.5-0.8B is a hybrid: 6 of 24 layers are full attention (2 KV heads, head dim 256) and 18 are Gated DeltaNet [C, HF config]. KV is about 12 KB/token, about 0.39 GB at 32k against about 1.6 GB of bf16 weights per step, so the late-token premium is at most about 25% at the cap [C, estimate]. The "metered frontier differs from a tokens-only frontier" effect is therefore modest on this model and larger on full-attention models.

### 1.3 Ranking for interp edits

Behaviour (10% to 3,000% of per-task energy) ≫ structure (1-50%) ≫ statistics-changing switching (0.1-10% in compute-bound kernels on NVIDIA; unknown on Apple decode) ≫ surgical switching (≤ 3 × 10⁻³ % for Astra-class edits; a crude bound of ≤ 0.15% for projections folded into every residual writer, likely far less).

---

## 2. The noise question, head-on

### 2.1 Measured floors

| Design / boundary | Floor | Source |
|---|---|---|
| Free-running agent episode against the frozen token model | residual SD 19-58 J on 2-4 kJ (1-2%) | `research-program.md:27,105-112` |
| Token-identical replay, whole episode | about 2 J per measurement; pair-difference SD 2.97 J on about 2.7 kJ (0.11%); K = 7 sessions σ_w 4.67 J | `research-program.md:28,114` |
| Between-session step | 8-9 J (−0.41%), not attributable | `research-program.md:154` |
| Fixed-token 50 J decode members | SD 0.21 J; absolute floor 2.94-3.59 J; comparative floor 6.80-7.38 J; attribution about 1 J; practical clearable phase contrast about 5 J | `df-ph-decode-floor-mint1.json`; `PROJECT_STATUS.md:100-105` |
| Known-bytes interleaved microbenchmark, one hour R,C,C,R | GPU rail ±1.05 × 10⁻⁴ J/GB ≈ ±11 mW at 106.5 GB/s (about 0.1% of about 10 W); rails ±0.22 W; DC ±0.77 W; rest ±0.89 W | `KB-SLOT-FILL.md:10,20-23,77` (conversion by the lead) |
| Background daemons in that hour | arm asymmetry 4.5 × 10⁻⁶ J/GB = 0.2% of δΔ_rails | `KB-SLOT-FILL.md:81` |
| DVFS nuisance | benign ALIGN residuals correlate +0.79 to +0.92 with GPU clock | `research-program.md:153` |
| powermetrics cadence | asked 100 ms, delivered about 130 ms | `KB-SLOT-FILL.md:84`; `joulewise/powermetrics_fiducial.py:66` |

Two cautions about these floors:
- **The KB half-width is not a statistical SE.** The reading rule sums worst-case terms, edges plus a baseline term T × (|P_pre − P_post|/2 + 2 se_idle), "summed, not in quadrature" (`docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md:110-118`). Its drift part grows with call length, so extrapolating it as 1/√T, as seat 2 did ("about 0.1% per √hour"), is an assumption until the noise spectrum is measured.
- **Floors are absolute, not relative.** The 0.11% replay figure is 2.97 J on a 2.7 kJ episode. On a small model with a few-hundred-joule replay the same 2-3 J is 0.5-1%. Size replay units in joules (≥ 2 kJ, e.g. a capped 32k-token Astra problem) or size n from an A/A′ pilot at the real unit energy.

### 2.2 Power analysis

Paired design, two-sided α = 0.05, power 0.8: MDE = 2.80 σ_d / √n. With σ_d = 2.97 J on a 2.7 kJ unit:

| Pairs n | MDE (J) | MDE (relative) |
|---|---|---|
| 8 | 2.94 | 0.109% |
| 11 | 2.51 | 0.093% |
| 16 | 2.08 | 0.077% |
| 28 | 1.57 | 0.058% |
| 64 | 1.04 | 0.038% |
| 256 | 0.52 | 0.019% |

- Equivalence (TOST, true difference 0, power 0.8): ±0.1% needs 11 pairs; ±0.05% needs 42.
- Detecting a true effect of 10⁻⁴ needs about 950 pairs; 3 × 10⁻⁵ about 10,500; 10⁻⁵ about 95,000.
- Fixed-token 50 J members: statistically 0.19-0.63 J at n = 10-20 (member SD 0.21-0.5 J), but the attribution floor of about 1 J and the minted comparative floor of 6.8-7.4 J dominate. They see structural edits (≥ 2-10% of member energy), not surgical ones.
- Free-running data cannot isolate the physics channel below the token model's 1-2% residual. Hence teacher-forced replay.

### 2.3 Expected effects against the floors

| Effect | Expected size | Best floor | Verdict |
|---|---|---|---|
| Astra behaviour (tokens) | 0.8-2.5 kJ per problem (30-70%) | 2-3 J | ≫ floor; noise irrelevant |
| Precision 8 → 4 bit at fixed tokens | tens of % (decode time at flat power, PC-4) | 2-3 J | ≫ floor; also visible on a stopwatch |
| Top-k doubling on 30B-A3B | about +50 J per doubling (`docs/research_question_bank.md:1632-1640`) | 5 J bar | resolvable; already banked |
| 50% zeros across all MLP weights, bf16, fixed tokens | unknown on Apple; plausibly 0.1-few % | 0.04-0.1% (replay), ±11 mW (GPU rail) | the open question; Stage 1 block P |
| 50% zeros in one matrix | 1-10 mW | ±11 mW per 25-min arm | at or below floor |
| Astra-class surgical edit, fixed tokens | ≤ 3 × 10⁻⁵, likely ≤ 10⁻⁶ | 0.04-0.1% | 25-1,000× below; report a bound |
| Abliteration across all residual writers, fixed tokens | ≤ 1.5 × 10⁻³ by the crude bound, likely ≪ 10⁻⁴ | 0.04-0.1% | within reach of 64+ pairs only if the crude bound is near the truth; the best case for a non-null |
| Expert identity at B = 1, fixed k | ≈ 0 (byte-symmetric) | — | predicted null; already registered as the B = 1 arm of RQ-NEXT-ROUTING×BATCH |

### 2.4 Structural ways to beat the noise

1. **Remove behaviour by teacher forcing.** Replay a fixed token sequence through both weight sets, *token by token with the KV cache*, computing and discarding the logits. A batched teacher-forced forward pass is prefill physics (compute-bound, different kernels) and measures the wrong regime. The repo has no forced-token path (`joulewise/` has none; the ALIGN endpoint is pinned greedy), so this is a build item, not a reuse.
2. **Interleave.** Randomized ABBA/BAAB order makes slow drift and daemons variance rather than bias. Keep the quiet-Mac regime (display off; RUN_STATE 206) and the contention monitor (0.05 CPU-s/s per process, `joulewise/hazards/contention.py:11`).
3. **Lock-in by in-process weight swapping: promising, unproven.** Keep both versions of only the edited tensors resident and swap references on a pseudo-random schedule; demodulate the rails and the KM003C (50 Hz) against the swap log. The case for it rests on the noise spectrum, which nobody has measured: the KB anchor is already an ABBA design at about 0.1% per hour, and the thermal-mismatch argument is numerically small (a 1% contrast on a 10 W rail is 0.1 W, about 0.05-0.1 K, worth 0.004-0.025% of power at the 0.08-0.25 %/°C leakage literature value, itself a discrete-GPU figure; `methodology-vs-literature.md:28`) [C]. If built, the checks' design rules apply:
   - use a bi-phase (Manchester-coded) m-sequence; an NRZ PRBS has spectral content down to near DC and overlaps the drift band;
   - use 1-2 s chips; at about 130 ms records, dropping edge samples costs about 26-52% of data at 0.5 s chips and 6-13% at 2 s;
   - run A/A′ (same content, two buffers) and content-swap nulls, plus a **chip-length sweep** (0.5/1/2/4 s), because a per-edge DVFS or first-touch transient is a bias ∝ 1/T_chip that neither null sees;
   - force `mx.eval` and sync at each swap, never let `mx.compile` capture the weights, and log per-chip GPU frequency and token latency.
4. **Isolate boundaries.** Use the GPU rail for on-die effects and the DC meter, about 70× coarser, for DRAM and fabric effects; report DC − rails as an outcome. Log GPU frequency and residency, SMC temperatures and fan RPM; on an actively cooled part extra switching power should go to temperature and fan, not frequency (Hot Pixels).
5. **Use large, graded positive controls** (§1.1): whole-model zero/sorted/outlier ladders in bf16, so a null on a surgical edit comes with demonstrated sensitivity.
6. **Check instrument validity first.** Before reading any switching result off a software rail, show that the rail responds to operand data at matched frequency, with the DC meter as arbiter. Pre-register three outcomes: rail and DC both move; DC moves and rail is flat (the rail is modelled); both flat at the extreme (Apple data dependence is below the floor).
7. **Report equivalence bounds** (TOST with a stated MDE), not "chance-level classification".

Bottom line: everything except surgical switching is above the noise with designs we already run. Surgical switching is below any floor we can afford, so it is reported as a bound.

---

## 3. Ranked idea table

Eighteen ideas (nine per seat). "Checks" gives the Fable and the Opus checker's refutation vote. Ranks weigh relevance to Ed's question, expected information, novelty after the checks, and cost.

| Rank | Idea (seat) | Checks (Fable / Opus) | Novelty verdict (checks) | Physics verdict (checks) | Disposition |
|---|---|---|---|---|---|
| 1 | **Two-channel decomposition**: fixed-token replay vs free-running (S2) | not refuted / not refuted | High after reframing: no published work splits an interp edit's energy into token and physics channels | Physics channel near-certain null, so the headline "≥ 95% via tokens" is near-tautological; report the absolute bound instead. The 4-bit zeros arm produces no zeros (MLX affine codes); use LoRA with B = 0 as the pure kernel control; replace the SAE arm with the inference-time ablation hook of the same direction; noise floor does not transfer to small models; teacher forcing must be built; cost 1-2 Mac-days, not 0.3-0.5 | **Core of ASTRA-2CH (Stage 1)** |
| 2 | **EDIT-FRONTIER**: J per correct before and after the Astra edit (S1) | not refuted / not refuted | Narrow: the >2× headline is arithmetic (about 12× tokens per correct). New: first energy number for this edit, the fixed-token residual, and the comparators the blog omits | Coefficients wrong for a 0.8B hybrid; KV-slope term needed; accuracy counts, not joules, limit J/correct precision; must run bf16 (4-bit can round away a 64-column edit); cost 2-4 Mac-nights at the 32k cap unless trimmed | **Merged into ASTRA-2CH**, adding base thinking-off and a budget-cap arm |
| 3 | **Energy-capability frontiers** of compute-allocation edits (S2) | not refuted / not refuted | No metered frontier for interp edits found; the comparator must be the token + context law (Wu et al.), not tokens only | ThinkEdit is length-*raising* (miscast as a shortening lever); ASC is an inference-time vector (folding needs a bias term); cap-conditional; 4-7 Mac-nights realistic | **Stage 2 registered headline** |
| 4 | **S1**: Apple-GPU data-dependent energy ladder (S2) | not refuted / not refuted | No Apple matmul/GEMV characterization found; arm list largely ports Gregersen | Rails may be modelled, so DC must arbitrate; KM003C is on the MBP, not the Air; the fanless Air inverts the sign (Hot Pixels); bf16 rounding makes the 10⁻³ rank-one arm an A/A′; GO rule as written would kill case "DC moves, rail flat" | **Stage 1 block P**, reframed as an instrument-validity gate on the MBP |
| 5 | **ENTROPY-DIAL**: Apple's data-dependent GPU power coefficient (S1) | not refuted / not refuted | Mechanism pre-empted (ALUPower, Gregersen, toggle-aware compression); Apple calibration and the rails-vs-rest split are new | "Monotone" contradicted by prior work; exponent features did not help in ALUPower; statistics must be defined on packed 4-bit nibbles; "predict any edit" is vacuous because real edits sit at the random-statistics operating point; GEMV is memory-bound, so the GPU rail sees the smaller half | **Merged into S1**; drop the edit-predictor framing |
| 6 | **Toggle model**: joules per bit transition (S2) | not refuted / not refuted | Calibrated coefficient on Apple LLM weight streams is new | Held-out real-edit validation is vacuous (both ≈ 0); use function-preserving re-encodings instead: MLX affine q → 15 − q with s → −s, β → β + 15s is bit-exact and flips nibble Hamming weight; hidden-unit permutations move Hamming distance at fixed outputs; compute Hamming distance at several strides; DBI may fold patterns | **Stage 2 H4**, only if block P shows a non-null |
| 7 | **LOCKIN-SWAP** (S1) | not refuted / not refuted | Method new; null near-certain | 10 mW bound does not follow from an 11 mW SE (95% upper ≈ 20-25 mW); positive control 1-2 orders too large; KB floor earned with 12.6-min calls, not 2-4 s chopping | **Instrument**, gated on the noise-PSD measurement in Stage 0 |
| 8 | **PRBS lock-in** (S2) | not refuted / not refuted | Narrow | Claimed gain over ABBA unsupported until the PSD is measured; thermal-mismatch rationale negligible; daemon bursts are in-band; use bi-phase codes and a chip-length sweep | **Merged with 7**; same gate |
| 9 | **JOULE-MAP**: per-component energy on Apple GPU (S1) | not refuted / not refuted | Partly pre-empted by CLEAR (arXiv 2510.02810 **[L]**: component-level energy, attention costs more per FLOP) and HYMELL; new: in-situ removal on unified memory, per layer, rails/rest split, long context | J/FLOP and J/GB collinear at B = 1; skip arms shorten the run (static × Δt confound); MoE skips change routing unless forced; "stable across prompts" near-tautological; 50 J members are too small for one-layer skips | **Banked** as the "price list" for count × price accounting |
| 10 | **Unlogged self-modification** leaves an energy signature (S2) | not refuted / not refuted | Closest prior: Gargiulo & Kulp (arXiv 2609.00309 **[L]**: H200, about 10 MHz external probe, diluted-LoRA evasion caught 48-88%, ≥ 98% with a rescue rule); detection half is E2 relabelled | Training is cheaper per token than in-context decode on this rig (prefill 0.045-0.063 J/token); Astra's "pass" was a batch of up to 512 generations; CPU-side edits escape the GPU-rail residual; closed-form edits are energy-free | **Fold into ALIGN E2** as a dose type (dose in joules), after Paper 1 |
| 11 | **PRECISION-TAMPER** (S1) | not refuted / not refuted | Magnitude known; substitution audits exist (Cai et al.; model equality testing; TOPLOC); energy as the detector is new | A plain 8 → 4-bit swap is visible on a stopwatch; only a timing-masked arm tests energy; dense pruning keeps bytes; expert collapse at fixed k keeps bytes; KB coefficients are latency-bound and should not size the effect | **Banked** as an ALIGN specificity control with a timing-masked arm |
| 12 | **ABLATION-ARTIFACT**: zero vs mean vs resample ablation (S1) | not refuted / not refuted | Nobody has measured energy of ablation styles | Predicted ordering wrong (constant mean rows also cut toggles: zero ≤ mean < resample); per-head effect 10-100× below floor; downstream activation shifts correlate with importance (needs a patched-downstream arm); cost understated 3-15× | **Banked**; per-layer prefill grid only if block P is non-null |
| 13 | **Blinded tamper-detection challenge** (S2) | not refuted / not refuted | Surgical null nearly predictable; HAMLOCK is the closest analogue | Three copies per class cannot separate chance from weak detection; "outlier injection" in 4-bit groups becomes mass zeroing; artifact-format leakage would make edits detectable for the wrong reason | **Banked** behind block P; reshape as equivalence bounds plus a dose ladder |
| 14 | **MODEL-ID** (S1) | not refuted / not refuted | Positive half trivial; null half true by construction if rails are modelled | Must state whether a null is an instrument limit or a physics limit; free decode sees edits only through behaviour | **Banked**; see §5 on the UniGuard citation |
| 15 | **DRAM data dependence** at the DC boundary (S2) | not refuted / not refuted | New for LPDDR5, Apple and a system boundary | Likely 0.003-0.006 J/GB vs a ~0.010-0.014 J/GB comparison floor; the summed bound does not shrink with time; DBI or scrambling can null it for unrelated reasons; zero fills risk residency tricks | **Banked** for instrument night #3 as a sign/ordering pilot with a replicate-variance estimator |
| 16 | **Energy reveals routing** (MoE, Flash-Next) (S2) | not refuted / not refuted | No published power channel for routing (Kulp's MATS stream proposes one) | Router temperature is a no-op on top-k membership; B = 1 identity is byte-symmetric; the Flash-Next n-gram table is a token readout; union-of-experts effect at B > 1 is real but obvious | **Banked**: B = 1 null as a TOPK-KNOB rider; Flash-Next SSD stall energy with experiment 4 |
| 17 | **ROUTER-EDIT** (S1) | **refuted** / not refuted | The B = 1 null is already predeclared in RQ-NEXT-ROUTING×BATCH (`docs/research_question_bank.md:1720-1726`) | No physical channel at B = 1 with resident experts (reuse distance about 1.7 GB ≫ SLC) | **Merged** into RQ-NEXT-ROUTING×BATCH and RQ-NEXT-TOPK-KNOB |
| 18 | **DVFS-COUPLE** (S1) | **refuted** / not refuted | Null predetermined: fan-cooled M-series hold max frequency; the cited "0.03 GHz at 12 W" is an M1 Air *CPU* result | tok/s barely depends on GPU clock in memory-bound decode | **Covariate log only** (frequency, residency, fan RPM, die temperature, DC − rails) in every arm |

---

## 4. Staged plan with go/no-go criteria

### Stage 0: desk (0 Mac time; about 2-4 desk days; on the Air after BYTES stage 1 on 12 Nov; Sol implements, lead reviews)
- **Prediction memo**: per edit family, the predicted ΔE in each channel and the equivalence margins, committed before any measurement.
- **Harness**: a token-by-token teacher-forced decode loop on `mlx_lm` (KV cache kept; logits computed and discarded); in-process weight swap; an edit kit (apply the authors' Astra diff with hash check; fold a direction W′ = W − r rᵀ W; bf16 zeroing, sorting and outlier ladders; LoRA with B = 0; an inference-time directional-ablation hook).
- **Runtime checks** (after Ed approves the download): `mlx_lm` loads dense Qwen3.5-0.8B (the `qwen3_5` model type is already in the pinned stack for Qwen3.8-27B; the dense 0.8B is unverified); a 20-problem smoke on the Air reproduces the cap-hit drop (software validation only, no energy claim); decode tok/s for sizing.
- **Noise spectrum**: PSD of the GPU rail and the DC meter under steady decode, from a non-restricted 20-min capture. This decides whether a lock-in instrument is worth building.

**Go/no-go to Stage 1:** (i) teacher-forced outputs bit-identical between A and A′, and identical token streams across weight sets; (ii) the edited model's cap-hit rate on the smoke is within ±10 points of the published 32-33%, otherwise stop and diagnose (dtype, runtime); (iii) no recompilation or reload per swap; (iv) projected Stage 1 runtime fits one window (≤ 12.4 h). **Publishable:** nothing alone; it freezes the predictions.

### Stage 1: ASTRA-2CH, the single best first experiment (one MBP window; KM003C inline; a magistrate kit)
| Block | Contents | Size [estimate] |
|---|---|---|
| P: instrument gate and positive control | fixed-shape bf16 GEMM (prefill-like) and a ≥ 1 GB weight-ring GEMV (decode-like); fills random, all-zero (explicitly written), constant non-zero, sorted rows, 50% unstructured zeros, A/A′; dispatch time must match across fills; GPU rail, IOReport, DC; frequency and residency | 60-90 min |
| F: behaviour channel | 40 MATH-500 problems (fixed seeded subset); arms base thinking-on, edited thinking-on, base thinking-off, base thinking-on capped at 8k; Astra sampling (T 0.6, top-p 0.95, top-k 20, presence 1.5); one sample per problem per arm, seeds paired per problem; arm order randomized within problem blocks; tokens, J per problem (GPU rail, rails, DC), correctness, cap hits | about 2.6M decode tokens |
| T: physics channel | 12 edited-arm sequences (capped and uncapped mix; TOST at ±0.1% needs about 11 pairs at the ALIGN pair SD) teacher-forced through base and edited weights in ABBA order; A/A′ (base vs a byte-identical copy); positive control: a subset of the same sequences through a bf16 copy with 50% zeros across all MLP weights | about 1M forced tokens |

At 150-250 tok/s that is about 4-7 h of decode; if Stage 0 measures under 100 tok/s, cut F to 30 problems and drop the 8k arm.

**Registered predictions:** edited thinking-on uses 40-55% of base thinking-on tokens per problem; between-arm ΔJ is explained by a fitted prefill + decode + context model to within 10%; J per correct differs by about 12-15× (cap-conditional; the base arm will have about 3 correct of 40, so its interval is wide); edited thinking-on vs base thinking-off: a few points of accuracy at roughly equal tokens (both near 32% cap hits per the HF rerun), so J per correct roughly equal; fixed-token |ΔE| < 0.1% (TOST) with the point estimate ≤ 3 × 10⁻⁵.

**Go/no-go to Stage 2:** (i) A/A′ pair SD ≤ 0.15% of unit energy; (ii) block P classifies the rail (both move / DC only / neither) and the whole-MLP zeroing control shows the predicted sign, or is reported as a bound; (iii) F reproduces the behaviour shift (edited cap-hit rate ≤ 45%); (iv) the token + context model explains ≥ 90% of between-arm ΔE; (v) thermal level 0 throughout and GPU frequency matched across T arms. **Publishable:** a non-claim pilot; a short note is possible ("the energy cost of a published interp weight edit is behavioural; its switching residual is below X%").

### Stage 2: registered experiment (2-4 Mac-nights plus about a week of desk; after the ALIGN D windows and the Paper 1 freeze)
- **H1 frontier:** J per correct across edit strength (the released Astra diff scaled by α ∈ {0, 0.25, 0.5, 0.75, 1}, plus our own direction ablation), an ASC-style concise direction (disclosed as a runtime hook or bias), and ThinkEdit re-derived for Qwen as the length-raising arm; ≥ 2 models (the hybrid Qwen3.5-0.8B and a full-attention dense model; optionally Qwen3-30B-A3B for MoE routing shifts); reported per cap; comparator the token + context law.
- **H2 bound:** fixed-token |ΔE| < 0.1% (TOST) for every surgical edit, with graded positive controls from block P. The primary surgical arm is a direction projected out of every residual writer (the best case for a non-null, §1.1); the Astra diff and a ROME-style rank-one edit are secondary.
- **H3 share:** ≥ 90-95% of ΔE explained by the token + context model, as an aggregate share with a CI, defined only for arms with |ΔE| > 5%.
- **H4 (optional) toggle coefficient:** function-preserving re-encodings and unit permutations as calibration, only if block P gave "both move" or "DC only".
- **Go/no-go:** hypotheses frozen before unblinding; edit codes blinded; public deviation log. **Publishable:** a workshop paper (interp, efficiency or safety); stronger if the frontier holds on two models and H4 resolves an Apple coefficient.

### Banked (later; no Mac time requested)
JOULE-MAP price list (sampled module-type arms, forced routing, batch axis for J/FLOP); ABLATION-ARTIFACT per-layer prefill grid; PRECISION-TAMPER with a timing-masked arm as an ALIGN specificity control; unlogged self-edit as an E2 dose type (dose in joules, an energy-free closed-form arm, a CPU/DC second score); DRAM fill ordering on instrument night #3 with a replicate-variance estimator; the B = 1 router null as a TOPK-KNOB rider; Flash-Next SSD stall energy with experiment 4; MODEL-ID and the blinded tamper challenge as equivalence bounds behind block P.

---

## 5. What we could not verify

**Ed's reference.** Found and opened (§0). Still open: there is no arXiv version or peer review, and no OpenAI statement about the model was found [S1]. The authors' own Hugging Face repo (`RikiyaT/Qwen3.5-0.8B-weight-space-programming`) and the logs repo (`github.com/RikiyaT/lm_understand-logs`, opened by checks [C]) were not re-opened by the lead; the diff's licence (CC BY 4.0 / MIT) is as reported by a check. Several checks reported "not found" for the Astra reference only because their search budget ran out; the lead's direct open supersedes them. A claim that OpenAI halted a "GPT-6.1 Astra" appeared only in search snippets and is **UNVERIFIED**.

**Conflict resolved: UniGuard.** One MODEL-ID check called seat 1's UniGuard link a misattribution. The lead opened arXiv 2311.16684: "A Unified Hardware-based Threat Detector for AI Accelerators" (Yan, Qiu, Zhang, 2023) does monitor power on FPGA AI accelerators and reports 94.0% attack-detection accuracy **[L]**. Seat 1's citation stands.

**Apple-specific unknowns.** Whether the powermetrics/IOReport GPU energy on the M3 Max is measured or modelled ("believed to be model-based" is the strongest statement found); whether Apple's memory controller enables LPDDR5 DBI or scrambles data; whether GPU.zip-style hardware compression applies to Metal compute buffers that hold MLX weights; whether the IOReport DRAM channel exists on the MBP's macOS version, and the macOS 27 Energy Model entitlement hazard (`methodology-vs-literature.md:49`).

**Model and runtime unknowns.** `mlx_lm` support for the dense Qwen3.5-0.8B; its decode tok/s on the M3 Max; whether it is already on the MBP (one check said so; nothing in the repo confirms it, so assume a download); whether the 64-column edit survives MLX quantization (plan bf16).

**Literature not opened by anyone in this run (UNVERIFIED):** MIT sign-magnitude weight-tuning thesis / ASSCC'19; "Energy per Successful Goal" (arXiv 2605.22883); Brier, Clavier, Olivier CPA (CHES 2004); DeepSniffer (ASPLOS 2020); TokenPowerBench; NPUMoE (arXiv 2604.18788); Rinberg et al. (arXiv 2511.02620); MobiEdit (arXiv 2506.13772); the Hertzbleed S&P 2023 follow-up paper itself; Cinà et al. sponge-poisoning details beyond the abstract; most press coverage of Astra beyond The Register and R&D World [C]. Pekhimenko et al.'s toggle-aware compression (HPCA 2016) was opened by one check and not by another; Kraken (arXiv 2603.02891) was read by abstract or HTML only.

**Coverage.** Many checks ran out of web-search budget and fell back to direct fetches of papers they already knew. "No prior work found" claims are therefore weaker than a full sweep. Re-sweep before any registration, at least for: energy of model editing or steering; data-dependent GPU power on Apple silicon; SAE and steering inference cost.

**Repo facts relied on but not re-derived:** the RECORD lines behind the ALIGN coefficients (`research-program.md:105-114,249`), and the check-reported prefill and bare-decode ranges (RECORD af17111e:55). Every other repo line cited here was re-read by the lead.

---

## Appendix A. Seat reports, verbatim

The two seat reports follow exactly as returned to the workflow. Each seat's idea list is reproduced from the same return value, serialized as indented JSON (content unchanged).

---

### A.1 Seat 1 (Fable 5.1), verbatim report

# Weight edits, energy and interpretability on the JouleWise rig (Fable seat, 2026-11-07)

Research and design only. No code run, no weights downloaded, no files written to the repo, nothing posted. Repo citations are to `/Users/edr/code/CapstoneProject/jw-wt/handoff` (HEAD detached at `9406e49a2`) unless a branch is named. Every web source listed under "Sources opened" was fetched in this session; items I could not open are marked UNVERIFIED. My own numbers are tagged **[estimate]** or **[derived]**.

Storage note for the orchestrator: Ed asked that this material be stored in the future-research docs. I wrote nothing (rules). The natural home is `docs/research-audits/2026-11-07/` beside `research-program.md` (on `origin/research/2026-11-07-research-program`), with a row in `docs/research_question_bank.md` (bank header lines 1-12 say promotion needs a named RQ slot, a data plan and scope fit). Ed's "1 and 2 most, 3 and 4 bank for later" is about the previously proposed experiment list; this brief is a new line and should be banked as such, not inserted ahead of E1/E2.

## 0. Ed's reference, verified

"GPT-6 Astra can natively edit model weights" is real and traceable. It is the MIT CSAIL write-up **"Sparks of Weight-Space Programming"** (Rikiya Takehi, Jayden Teoh, Alex Zhang, Omar Khattab; blog post dated 2026-11-02; no arXiv id, no venue, not peer reviewed; I found no OpenAI statement). The claims that matter for us:

- Astra edited **Qwen3.5-0.8B** by tracing reasoning loops to one direction written by the MLPs of layers 15 and 19 and subtracting it from 64 output columns in each: **131,072 weights, 0.016 %** of the model. MATH-500 rose 7.9 % → 48.1 %, GSM8K 13.8 % → 67.1 %, IFEval 21.0 % → 62.3 %, and the fraction of MATH-500 answers hitting the 32,768-token cap fell **93.0 % → 33.1 %**. Gemma 3 270M could not be improved (6.8 → 7.7 at best); the page says editing can remove an obstacle but not add an ability. The page reports no energy or inference-cost numbers.
- Sean Goedecke's critique: the Qwen fix is "essentially a steering or abliteration workflow" (write looping/non-looping pairs, find the contributing weights, cut them down, test), which a competent researcher could do; the game-identification result is L2 norms per input cell.
- Simon Willison reproduced the weight-*reading* experiment with Qwen 3.8 27B (17 GB Q4_K_M GGUF, LM Studio, laptop): 3 of 4 games identified, 46-65 min per attempt.

Two consequences. First, the headline edit is physically an **abliteration-class, rank-one-per-column change to two matrices**: the kind of edit whose first-order energy effect at fixed tokens should be near zero (section 1a). Second, its real energy effect is enormous and runs entirely through **behaviour**: the cap-hit rate falling 93 % → 33 % means thousands fewer decode tokens per problem. On our rig that is kilojoules against a 2 J replay floor. This is the shape of the whole brief: for surgical edits, tokens dominate, switching power is a bound, and memory traffic/precision sits in between.

## 1. Physics: by which channels can a weight edit change energy?

**(a) Data-dependent switching at fixed FLOPs.** The literature says the effect is large between *extreme* operand distributions and is driven by bit toggling, not value:

- GPUs: ALUPower (Lucas & Juurlink, MASCOTS 2016): "the power consumption of one kernel varies between 155 and 257 Watt depending on the processed values." Gregersen, Patel & Choukse (arXiv 2409.18324; A100 main, H100/V100/RTX 6000 checks): GEMM input patterns change power "by up to 38 %"; "input data with highly similar bits uses less power"; "matrix sparsity decreases GEMM power"; zeroing either MSBs or LSBs reduces power; FP16 tensor-core is the most power-hungry type; runtime was "consistent to a microsecond-level" across inputs, so this is a pure power effect, not a speed effect. Bhalachandra et al. (arXiv 2212.08805): "power variations of up to 67 %" on an A100 DGEMM from values, positions and uniqueness alone. NVIDIA's CUTLASS measurement guidelines concede it: "all-zero or low-entropy data may lead to decreased dynamic power draw"; fixed-power tests are "highly sensitive to the data fill pattern, particularly for narrow precisions"; fixed-frequency tests are not.
- Accelerators: MAC switching energy is modelled from the Hamming distance of successive partial sums (Fang, Zhang & Huang, arXiv 2511.17123: up to 58.6 % energy reduction by weight selection at 2-3 % accuracy cost, systolic-array model). An MIT sign-magnitude weight-tuning thesis/ASSCC'19 paper reports ~61 % toggle reduction and ~35 % PE power reduction (UNVERIFIED: snippet only).
- Apple silicon: this is the key fact for Ed's caveat. Hot Pixels (Taneja et al., arXiv 2305.12784, USENIX Sec '23) read power, frequency and temperature on M1/M2 **without privileges through IOReport** (modified SocPowerBuddy) and found on the M1 MacBook Air iGPU that Hamming distance of successive outputs correlates −0.971 with power and −0.951 with frequency, and Hamming weight −0.963/−0.961; on the CPU, add-1 vs add-0 steady states differed by 0.3 W at ~12 W and 0.03 GHz. On an RX 6600 the whole HW-driven span was 97.5-98.1 W at a ~100 W limit, i.e. ~0.6 %. Chawla et al. (arXiv 2306.16391) show SMC power keys on M1/M2 are data-dependent enough to recover AES key bytes from user space. So the channel exists on our chip family, is visible in software telemetry, and, on power- or thermally-limited parts, **couples into frequency and therefore performance** (Hot Pixels' core observation). The M3 Max at decode-level GPU power is probably not at a limit, but this has to be measured, not assumed.

What this means for a *surgical* edit: the spans above are between all-zeros and random fills, i.e. order-unity changes in operand entropy over the whole matrix. A rank-one or abliteration edit changes every element of one or two matrices by a few percent without changing their bit entropy; a MEMIT edit spreads a small Δ across the MLP weights of ~6 layers (memit.baulab.info: "modifying the MLP weights of a range of critical layers", GPT-J layers {3..8}; ROME is "a rank-one modification of the MLP weights of a single layer"). **[estimate]** If the edited matrix is ~1 % of weight bytes streamed per decode token and the whole-model GPU draw is 10-20 W, the matrix's dynamic share is ~0.1-0.2 W; even an entropy swing of the "random → zeros" kind would move it by ≤ 50 mW, and an entropy-preserving edit by ≪ 1 mW. The switching channel is therefore a **null hypothesis with a bound** for interp-style edits, and a real effect only for edits that *target* entropy: zeroing (pruning, zero-ablation), bit-width changes, code redistribution after requantization.

**(b) Behaviour.** Our own coefficients: bare decode ~0.18 J/token, in-context hidden decode 0.49-0.67 J/token (`research-program.md:113,249`), against token-identical replays repeating to ~2 J (`:28`). One hundred tokens of changed output is 20-70 J, 10-35× the replay floor. Astra's loop fix removes thousands of tokens per problem. Refusal-direction edits (Arditi et al., arXiv 2406.11717: a single residual-stream direction mediates refusal in 13 chat models up to 72B) change answer length by hundreds of tokens. MoE router edits change expert choice. **This channel dominates by two to four orders of magnitude for any edit that changes what the model says, and must be removed by teacher forcing before (a) or (c) can be seen at all.** The repo already names forced-token decode as the convention for two-arm contrasts (`methodology-vs-literature.md:791`).

**(c) Memory traffic and sparsity.** Decode on unified memory is weight-streaming. The known-bytes test gives the per-byte coefficients: GPU rail 0.00879 ± 0.00010 J/GB, rails 0.0092 ± 0.0021, DC input 0.0389 ± 0.0072, rest 0.0296 ± 0.0084 (`KB-SLOT-FILL.md:20-23` on main), with the stated limit that the 32 MiB dispatch was latency-bound (`:77`) and 85 % of the GPU-rail contrast is stall time (`:72-76`). Quantization changes bytes per token at first order and changes the dequant kernel; structured pruning (heads, neurons, layers) removes FLOPs and bytes; **unstructured pruning does neither on dense MLX kernels** (Wanda, arXiv 2306.11695, makes no speed or energy claim; it zeroes weights in place), so Wanda-style pruning on our rig acts only through channel (a), which is a clean way to isolate (a) with a large effect. MoE routing edits keep bytes/token fixed at fixed top-k but change locality and can collapse to a few experts.

**Ranking for interp edits: (b) ≫ (c) ≫ (a).** (a) is dominant only in the designed cases (zeroing, precision), which is exactly where it becomes a measurement artifact for interp (section 4).

## 2. Edit families and their expected channels

| Family | What changes physically | (a) switching | (b) behaviour | (c) bytes/FLOPs |
|---|---|---|---|---|
| ROME / MEMIT (rank-one, rank-k on MLP out weights, 1-6 layers) | dense small Δ to 1-6 matrices | ≪ 1 mW [estimate]; null predicted | small unless the fact is on-path; length changes possible | none |
| Head/neuron/layer ablation | zero-ablation: zeros in a slice; mean-ablation: constants | **real**: zeros cut toggles; mean constants also lower entropy | large if function matters | none (masked), or first-order if the slice is physically removed |
| Unstructured pruning (Wanda, SparseGPT) | 30-60 % zeros, same shape | **real, largest clean (a) effect available** | moderate | none on dense kernels |
| Structured pruning | fewer rows/heads/layers | some | moderate | **first order** |
| SAE-feature ablation | runtime hook (adds compute) or folded rank-one projection | folded: ≈ null; hooked: adds a kernel | moderate-large | hooked: extra FLOPs/bytes |
| Steering folded into weights (abliteration: project a direction out of write matrices) | dense small Δ, entropy preserved | ≈ null | **large** (refusal/loop length) | none |
| Fine-tune / LoRA merge | dense small Δ everywhere | ≈ null | large | none (merged); LoRA unmerged adds bytes |
| Quantization / requantization | code width, scales, kernel | **real** (narrow precisions are most fill-sensitive, per CUTLASS) | small | **first order** |
| Model-authored edits (Astra-type) | so far: abliteration-class, 0.016 % of weights | ≈ null | **enormous** (cap hits 93 → 33 %) | none |

## 3. Detectability and a power analysis

Noise anchors (verified in the repo):
- ALIGN whole-episode: token-identical replays ~2 J on 2-4 kJ episodes (`research-program.md:28`); pair-difference SD 2.97 J, 2.1 J per measurement (`:114`); frozen-model residual SD 19-58 J per task pair (`:27`).
- Block-5 fixed-token members: 0.29-0.49 J repeatability on ~50 J points, attribution floor ~1 J, practical clearable phase contrast ~5 J (`PROJECT_STATUS.md:100-105`).
- Known-bytes interleaved microbenchmark: GPU rail resolved to ± 0.0001047 J/GB over an R,C,C,R hour (`KB-SLOT-FILL.md:22`). **[derived]** Two R calls streamed 2 × 2,394,112 × 32 MiB ≈ 160,700 GB in ≈ 1,518 s of active dispatch (t_R = 317 µs, `:28`), so the half-width is ≈ 16.8 J, about **11 mW of mean GPU-rail power over ~25 min per arm**. The DC-input half-width is 70× wider (0.0072 J/GB), so the switching channel is a GPU-rail measurement; the DC channel is for whole-machine behaviour effects.

Paired minimum detectable effect, α = 0.05 two-sided, power 0.8: δ ≈ 2.8 σ_d/√n.

| Design | σ_d | n | MDE | Comment |
|---|---|---|---|---|
| Whole-episode free-running replay (ALIGN) | ~3 J | 28 | ~1.6 J | ≈ 3-9 decode tokens; any behaviour change is detected; useless for (a)/(c) unless teacher-forced |
| Fixed-token 50 J decode member, ABBA | 0.3-0.5 J, floor 1 J | 10 pairs | ~0.4 J statistical, **~1-5 J practical** | 2-10 % of member energy: sees quantization and structured pruning, not surgical edits |
| Isolated-layer GEMV microbench, KB-style interleave | from KB | ~25 min/arm | **~10 mW GPU rail** [derived] | sees 50 % zeroing (expected 0.1-1 W [estimate]); bounds rank-one edits |
| Same with lock-in weight swap (below) | TBD at stage 0 | 1 h | expected ≤ 10 mW; the 1/f-rejecting design should do better | the stage-0 go/no-go measures this |

How to beat the noise structurally:
1. **Lock-in modulation.** Keep both versions of the edited matrix resident as `mx.array`s and swap the layer's weight pointer every block of B tokens (period chosen ≫ the ~130 ms powermetrics interval and the GPU DVFS settle; ~2-4 s blocks, so 0.12-0.25 Hz), with teacher-forced tokens so FLOPs, bytes and outputs are identical. Demodulate the GPU-rail trace against the known square wave; drift from thermals and daemons is concentrated at low frequency and is rejected. Essential control: an **A-A′ arm** (two copies of the *unedited* weights swapped the same way) to measure the placement/cache artifact of swapping itself; the result is the A/B contrast minus the A/A′ contrast. The KM003C at 50 Hz (`methodology-vs-literature.md:67,732`) is the better reference clock for the demodulator; powermetrics at 100 ms (delivered ~130 ms, `KB-SLOT-FILL.md:83`) is the rail channel.
2. **Interleaved microbenchmarks.** Run only the edited layer's GEMV on recorded real activations, edited vs unedited, in KB geometry with time-matched dispatches. Infrastructure exists: fenced matmul pulses (`joulewise/powermetrics_fiducial.py:1556`), KB reader and harvest, contention monitor at 0.05 CPU-s/s per process (`joulewise/hazards/contention.py:11`).
3. **Many-repeat replays** buy 1/√n; from 3 J, 28 pairs reach 1.6 J; 100 pairs 0.8 J. Diminishing against the 1 J attribution floor, so prefer designs 1-2.
4. **Thermal gating and frequency logging.** Hot Pixels shows data-dependent power moves DVFS. Record GPU frequency from powermetrics in every arm and report Δfrequency beside ΔP; CUTLASS's point that fixed-frequency tests are fill-insensitive means a frequency shift would itself be a finding (an edit that changes tok/s through power).
5. **Rail vs DC.** Use the GPU rail for (a), DC input plus battery term for (b) and whole-machine effects (host-side CPU work, SSD), consistent with the KB finding that three quarters of memory-traffic energy falls outside the rails (`:72-76`).

Ed's caveat, answered: the machine noise is low-frequency and mostly on the CPU rail; the switching signal can be moved to a chosen band on the GPU rail with the workload itself as the modulator. What cannot be beaten is the *size* of the surgical-edit switching effect, which is probably below even a lock-in floor. That is a publishable bound, not a failure.

## 4. Interp payoffs

1. **Energy as a per-component attribution signal.** Ablate a head/neuron/layer at fixed (teacher-forced) tokens and read ΔJ/token. The honest payoff is a **where-do-the-joules-go map** (attention vs MLP vs router vs lm_head vs KV traffic) on consumer silicon, which nobody has published for Apple GPUs. The caution is important for interp practice: **zero-ablation has a physical energy signature unrelated to function** (zeros cut toggles, section 1a), so an "energy importance" score would systematically favour zero-ablation over mean- or resample-ablation. Experiment 2 below measures that artifact directly; it is a methodological result interp people can use.
2. **Energy fingerprints of covert weight tampering.** The ALIGN result is that *hidden work* leaves a signature (residual 1-2 % of episode energy; `research-program.md:375`). A static backdoor that fires only on a trigger leaves **no** signature at fixed tokens unless it changes routing, length, or precision. So energy detects behavioural tampering (extra reasoning, different lengths, MoE collapse) and precision/sparsity tampering (a requantized or pruned substitute model), not surgical weight edits. The external literature agrees in spirit: UniGuard (arXiv 2311.16684) detects anomalous inference on FPGA accelerators from power side channels at 94 %, and Kimpson, Baker & Graham (arXiv 2610.07476; A100) show power alone bounds hidden compute weakly (β = 1.16 worst case, ≥ 0.41 under matched-energy evasion) but re-execution at an observed operating point tightens it to β = 0.059. Our seeded identical-work replays are the re-execution regime (`methodology-vs-literature.md:402-441`, idea 3). Framing for a paper: "energy audits the *work* and the *precision* of a model, and is blind to its *weights*", with a measured bound on the last clause.
3. **Joint energy-performance frontiers of edits.** The Astra loop-fix is a Pareto improvement (accuracy up, tokens down); abliteration of refusal likely raises energy per prompt; quantization lowers J/token but may raise tokens to a correct answer. Our rig can produce the first *measured* J-per-correct-answer frontier of weight edits on a laptop, with blinding and floors. The MvL cites an "Energy per Successful Goal" metric (arXiv 2605.22883) as the comparator; UNVERIFIED by me.

## 5. Staged plan

**Stage 0: desk microbenchmarks on the M4 Air (feasibility, 0 Mac-nights, ~2-3 Air-days).** Build an edit kit for a small MLX model already pinned in the repo's prompt plans (Qwen3-1.7B class; Qwen3.5-0.8B if Ed approves a download): rank-one/abliteration projection, Wanda-style zeroing of one `down_proj`, requantization to a different bit width; a teacher-forced decode harness on `mlx_lm` (`joulewise/adapters/mlx_runtime.py:280` is the load path); the lock-in weight-swap loop with A-A′ control; a software demodulator reading powermetrics (no KM003C on the Air). The Air is passively cooled and, per Hot Pixels, thermally constrained, so it leaks through frequency: use it only to validate software and signs, never for numbers. **Go/no-go:** (i) the demodulator recovers a planted contrast (random vs zero fill of the same matrix) with the predicted sign; (ii) A-A′ is within the floor; (iii) teacher-forced outputs are bit-identical across arms; (iv) no model-load or memory artifact when swapping. **Publishable:** nothing by itself; it fixes the floor estimate in the preregistration.

**Stage 1: quiet-Mac pilot (0.3-0.5 Mac-night or one quiet day, `DIAGNOSTIC_NO_PACK` style, KM003C inline).** Qwen3-8B 4-bit or Qwen3-30B-A3B. Three arms, all ABBA: (A) abliteration or ROME edit at fixed tokens (predicted null, report the bound); (B) 50 % zeroing of one layer at fixed tokens (predicted positive, 0.1-1 W [estimate]); (C) free-running edited vs unedited on ~50 reasoning prompts (predicted large, tracks tokens at 0.18-0.67 J/token). Plus a first per-layer energy map at fixed tokens (zero vs mean ablation). **Go/no-go:** lock-in floor ≤ 20 mW GPU rail in 20 min; B detected at ≥ 5σ; A's bound ≤ 1 % of the layer's share; C's ΔJ within 20 % of the token-count prediction; GPU frequency unchanged across arms or the shift quantified. **Publishable:** a workshop note (interp or ML-systems/energy): "surgical weight edits are energy-invisible at fixed tokens to X mW; zero-ablation is not; the behaviour channel is Y J per edit".

**Stage 2: registered experiment (1-2 Mac-nights).** Preregister three hypotheses with blinded arm labels, floors from stage 1, thermal gates, and a public deviation log: H1 (frontier) J-per-correct-answer of an Astra-class loop-fix edit reproduced by abliteration on Qwen3.5-0.8B (the blog says full logs are on GitHub; UNVERIFIED) or of the public refusal-direction edit on a Qwen3 chat model; H2 (switching bound) lock-in on the edited matrices, with the synthetic entropy dial (idea 7) as the calibration curve; H3 (attribution artifact) zero- vs mean- vs resample-ablation energy at fixed tokens across ≥ 3 prompt sets. **Publishable:** strong if H1 shows a ≥ 2× J-per-correct improvement with H2 null, i.e. the first measured demonstration that a 0.016 %-weight edit's energy effect is entirely behavioural; the Apple-GPU switching coefficient from idea 7 is independently citable (ALUPower-for-Apple-silicon).

## Sources opened (all fetched this session)
- Takehi, Teoh, Zhang, Khattab, "Sparks of Weight-Space Programming", https://rikiyat.github.io/blog/weight-space-programming/ (blog, 2026-11-02; no arXiv found)
- Goedecke, https://www.seangoedecke.com/llms-are-not-superhuman-at-reading-and-writing-neural-network-weights/
- Willison, https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/
- Lucas & Juurlink, ALUPower, MASCOTS 2016, https://depositonce.tu-berlin.de/items/f6f95245-1fea-41d7-8a84-8f83c4d6a84a (abstract; full PDF at core.ac.uk returned 403)
- Gregersen, Patel, Choukse, arXiv 2409.18324 (abs + HTML)
- Bhalachandra et al., arXiv 2212.08805 (abs)
- NVIDIA CUTLASS GEMM measurement guidelines, https://docs.nvidia.com/cutlass/4.7.0/media/docs/cpp/gemm_performance_measurement_methodology_guidelines.html
- Fang, Zhang, Huang, arXiv 2511.17123 (abs)
- Taneja et al., Hot Pixels, arXiv 2305.12784 (abs + ar5iv full text, first 100k chars); USENIX slides PDF not text-readable (UNVERIFIED)
- Chawla et al., arXiv 2306.16391 (abs)
- Meng et al., ROME arXiv 2202.05262 (abs); MEMIT arXiv 2210.07229 (abs) and https://memit.baulab.info/
- Arditi et al., arXiv 2406.11717 (abs; the weight-orthogonalization detail is from my knowledge of the paper, not re-verified)
- Sun et al., Wanda, arXiv 2306.11695 (abs)
- Zweiger et al., SEAL, arXiv 2506.10943 (abs)
- Kimpson, Baker, Graham, arXiv 2610.07476 (abs) and the MATS page
- Yan, Qiu, Zhang, UniGuard, arXiv 2311.16684 (abs)
- Batina et al., CSI NN (search result only; UNVERIFIED)
- UNVERIFIED, not opened: MIT sign-magnitude thesis/ASSCC'19; PowerPruning arXiv 2303.13997; Energy per Successful Goal arXiv 2605.22883; Hertzbleed and PLATYPUS (not cited).

Repo files read: `docs/research-audits/2026-11-07/research-program.md` (origin/research/2026-11-07-research-program), `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md` (origin/main), `docs/research-audits/2026-11-07/methodology-vs-literature.md` (origin/research/2026-11-07-methodology-vs-literature), `PROJECT_STATUS.md`, `joulewise/adapters/powermetrics.py`, `joulewise/adapters/mlx_runtime.py`, `joulewise/external/km003c_usb.py`, `joulewise/powermetrics_fiducial.py`, `joulewise/hazards/contention.py`, `docs/research_question_bank.md`. No restricted or sealed path was touched.

#### Seat 1 (Fable 5.1) IDEAS (verbatim content, indented JSON)

```json
[
 {
  "title": "LOCKIN-SWAP: lock-in weight-swap bound on the switching channel of surgical edits",
  "claim": "At teacher-forced, token-identical decode, a ROME/MEMIT or abliteration edit changes GPU-rail power by less than ~10 mW (null with a bound), measured by alternating edited/unedited copies of the edited matrices in-process at ~0.1-0.25 Hz and demodulating the rail trace, with an A-A' same-weights swap as the placement control.",
  "design": "Both weight versions resident as mx.arrays; swap the layer's weight reference every 2-4 s block of forced tokens; square-wave reference from the swap log, KM003C 50 Hz as timing; powermetrics GPU rail at 100 ms; ABBA over blocks; A-A' control arm; log GPU frequency per block. Floor from the known-bytes anchor: ~11 mW over ~25 min per arm (derived from KB-SLOT-FILL.md:22,28).",
  "detectability": "Expected effect <1 mW [estimate], so the deliverable is the bound. Positive control: the same loop with a 50 % zeroed matrix (expected 0.1-1 W).",
  "cost": "Stage 0 on the M4 Air 1-2 Air-days (software only); stage 1 ~20-40 min of quiet MBP time per model."
 },
 {
  "title": "ABLATION-ARTIFACT: the physical energy cost of zero- vs mean- vs resample-ablation",
  "claim": "Zero-ablation of heads/neurons lowers energy per token at fixed tokens by cutting bit toggles, independently of the component's functional importance; mean- and resample-ablation do not. An energy-based importance score would therefore be biased toward zero-ablation.",
  "design": "Pick 8-16 heads/neurons spanning high and low functional importance (by logit-difference or activation patching). For each, three ablation styles at teacher-forced tokens, ABBA with null quads, GPU rail + DC. Report dJ/token per style and its correlation with functional importance.",
  "detectability": "Per-head effect ~1/(layers x heads) of GPU draw: likely 1-10 mW for zero-ablation, so needs the LOCKIN-SWAP microbench or many repeats; per-layer zeroing is at the 0.1-1 W level and visible in 50 J members.",
  "cost": "Rides on LOCKIN-SWAP infrastructure; ~0.3 Mac-night for a full layer x style grid."
 },
 {
  "title": "EDIT-FRONTIER: joules per correct answer before and after an Astra-class loop-fix edit",
  "claim": "A 0.016 %-weight abliteration-class edit that removes reasoning loops (Qwen3.5-0.8B, MATH-500 7.9 to 48.1 %, cap-hits 93 to 33 %) changes energy per correct answer by more than 2x, and the whole change is explained by token counts at the ALIGN decode coefficients (0.18-0.67 J/token); the fixed-token residual is within the replay floor.",
  "design": "Reproduce or obtain the public edit (blog says logs are on GitHub; UNVERIFIED) or substitute an open abliteration edit; 50-100 prompts, free-running, blinded arm labels, ABBA, DC + rails; then re-run the same outputs teacher-forced in both weight sets to separate behaviour from switching.",
  "detectability": "Thousands of tokens per problem difference = kJ-scale vs 2 J replay floor; trivially detectable. The interesting number is the fixed-token residual.",
  "cost": "1 Mac-night at 0.8B-8B scale; half a night if the model is small. Needs a model download Ed approves."
 },
 {
  "title": "JOULE-MAP: per-component energy attribution of a transformer on Apple GPU",
  "claim": "At fixed tokens, the per-layer and per-module (attention, MLP, router, lm_head, KV traffic) energy shares of decode on unified memory can be measured to a few percent and are stable across prompt sets; MLP weight streaming dominates and attention's share grows with context as the ALIGN sequence design predicts.",
  "design": "Layer-skip and module-skip arms (identity bypass, teacher-forced), KB-style interleaving, GPU rail for compute and DC/rest for traffic, three context lengths. Compare with FLOP and byte counts to get J/FLOP and J/GB per module.",
  "detectability": "Whole-layer skip is ~1/36 of GPU draw (hundreds of mW), well above the 50 J-member floor; module splits need the microbench.",
  "cost": "~0.5 Mac-night per model; desk analysis on the Air."
 },
 {
  "title": "PRECISION-TAMPER: energy fingerprint of covert precision or sparsity substitution",
  "claim": "Replacing a declared model with a requantized (e.g. 8-bit to 4-bit), pruned, or expert-collapsed variant changes J/token at fixed tokens by more than 5 % and is detectable from the GPU rail and DC input in a single replay, while a surgical weight edit of the same model is not: energy audits precision and work, not weights.",
  "design": "Blinded substitution arms at fixed tokens; thresholds frozen from stage-1 null quads; scored with the ALIGN five-term residual plus a bytes term. Links to KB coefficients (GPU 0.00879, DC 0.0389 J/GB) for the predicted size.",
  "detectability": "Bytes per token halve on 8 to 4-bit; expected tens of percent of decode energy vs ~1 % residual; surgical edits predicted null.",
  "cost": "~0.3 Mac-night; registration text reuses ALIGN v3/v4 machinery."
 },
 {
  "title": "ROUTER-EDIT: MoE routing edits as an energy channel",
  "claim": "Edits to router weights that change expert selection (bias toward a subset, or collapse) change decode energy at fixed tokens and fixed top-k through cache locality and expert-weight residency, measurable on Qwen3-30B-A3B; routing diversity has an energy cost.",
  "design": "Teacher-forced decode with router logits perturbed to span routing entropy from collapse to uniform; log expert ids per token; GPU rail + DC; relate dJ/token to expert-switch rate and unique-expert count per window.",
  "detectability": "Expert-switch-driven traffic differences are GB-scale per 1k tokens, so tens of J per 1k tokens [estimate]; detectable in 50 J members.",
  "cost": "~0.3 Mac-night; small runner hook to override routing."
 },
 {
  "title": "ENTROPY-DIAL: the data-dependent GPU power coefficient of Apple silicon",
  "claim": "For a fixed-shape FP16/4-bit GEMV on the M3 Max GPU, mean power is a monotone function of operand bit entropy (zero fraction, Hamming distance of consecutive weight words, exponent spread), with a span of 10-40 % between all-zero and random fills, and the fitted coefficient predicts the energy effect of any weight edit from its weight statistics alone.",
  "design": "Synthetic weight matrices at controlled zero fraction, Hamming distance and exponent spread, same shape and dispatch count; KB geometry interleaving; GPU rail + frequency; fit dP against the three statistics; validate on real edited matrices from LOCKIN-SWAP.",
  "detectability": "Extreme-fill spans are 155-257 W on datacenter GPUs and 38-67 % in GEMM; even 1 % of a 10 W kernel is 100 mW, 10x the KB floor.",
  "cost": "Stage 0 on the Air for shape and sign; one quiet MBP day for the calibration. This is the ALUPower-for-Apple-silicon result and is independently publishable."
 },
 {
  "title": "DVFS-COUPLE: does weight entropy change tokens per second on the M3 Max?",
  "claim": "Hot Pixels shows data-dependent power shifts frequency on power- or thermally-limited Apple parts; under sustained LLM decode on the M3 Max, operand entropy changes GPU frequency and tok/s by less than 1 %, so switching power does not leak into performance on our rig (or it does, which makes energy and latency non-separable for edits).",
  "design": "ENTROPY-DIAL matrices run for 10-20 min sustained; log powermetrics GPU frequency and dispatch rate; compare against the thermal journal; repeat near the thermal gate boundary.",
  "detectability": "Frequency is reported directly; 0.03 GHz shifts were visible on an M1 Air at 12 W.",
  "cost": "Rides on ENTROPY-DIAL; +20 min per fill."
 },
 {
  "title": "MODEL-ID: can a power trace tell which weights are running? (banked)",
  "claim": "At fixed tokens, GPU-rail traces distinguish precision and sparsity variants of a model with high accuracy but cannot distinguish surgical edits (MEMIT, abliteration) from the base, giving a measured limit of power-trace model identification on consumer hardware.",
  "design": "Blinded classifier over replays of base vs k variants; chance-level for surgical edits is the expected result; links to Kimpson et al.'s re-execution regime and UniGuard.",
  "detectability": "Follows from PRECISION-TAMPER and LOCKIN-SWAP results; mostly desk analysis.",
  "cost": "0 extra Mac time if the above run; banked until then."
 }
]
```

---

### A.2 Seat 2 (Opus 5.5), verbatim report

## Interp × energy: how surgical weight edits change energy and performance (Opus seat)

I did research and design only. I ran no code except python arithmetic for the power analysis, loaded no weights and posted nothing. I created no worktree, so there is nothing to remove. I read the repo with `git show` from the canonical clone `/Users/edr/code/CapstoneProject/jw-wt/handoff`: `origin/main` @ `8a603bb22`, `origin/research/2026-11-07-research-program` (written "RP" below) and `origin/research/2026-11-07-methodology-vs-literature` ("MVL"). I did not open any Block-5, `night-*`, night-custody, night-archive or `restricted/` path. The design study's planned home is `docs/research-audits/2026-11-07/interp-weight-edit-energy.md` (`docs/research/AGENDA.md:24-25` @ origin/main).

### Bottom line
1. **Ed's reference exists, but as a blog post, not a peer-reviewed paper.** "Sparks of Weight-Space Programming" is by Takehi, Teoh, Zhang and Khattab (MIT CSAIL), dated 2 Nov 2026, at https://rikiyat.github.io/blog/weight-space-programming/ (opened). It names the model "GPT-6 Astra". I found no arXiv ID.
   - **Headline:** Astra edited 131,072 weights (0.016%) of Qwen3.5-0.8B by removing a "looping" direction that two MLP layers write. MATH-500 rose from 7.9% to 48.1%. The share of answers hitting the 32,768-token cap fell from 93.0% to 33.1%, using 50 forward passes.
   - **Limits the authors state:** the work is very early; editing "could not add an ability the model lacked"; Gemma 3 270M did not improve.
   - **A critique (opened):** S. Goedecke calls it "basically the Heretic abliteration playbook".
   - **Why it matters here:** this is exactly Ed's intersection. A 0.016% edit cut output length by tens of thousands of tokens per problem. Nearly all of its energy effect is behavioural.
2. **Which physics channel dominates.** In order of size:
   - behaviour (tokens, context length, tool calls);
   - bytes and structure;
   - data-dependent switching from edits that change weight statistics (zeros, outliers, re-quantization);
   - data-dependent switching from edits that preserve those statistics (about 0).

   For surgical edits (rank-one/MEMIT, direction ablation, steering folded into weights, ThinkEdit-style head edits, Astra's edit), I predict the fixed-token effect is at most about 1e-5 of energy **[estimate]**. That is about 100x below our best end-to-end floor. Measuring it directly would take about 95,000 replay pairs, so it is unmeasurable on any laptop. Surgical edits change energy almost entirely by changing what the model decides to compute.
3. **Ed's noise caveat holds for the whole-machine (DC) boundary, and much less for the GPU rail in an interleaved design.**
   - In the same known-bytes session, the contrast half-width converts to about ±0.011 W on the GPU rail, ±0.22 W on all rails and ±0.77 W at DC input. The GPU rail is about 20x sharper than all rails and 70x sharper than DC (`KB-SLOT-FILL.md:20-22` @ origin/main, with my conversion).
   - Background activity (daemons, agents drawing 8-47 W at idle per `docs/design/block6_collection_draft.md:367`) mostly sits on the CPU and the rest of the system. Under a randomized arm schedule it adds variance, not bias: the daemons' asymmetry between known-bytes arms was 0.2% of the rails half-width (`KB-SLOT-FILL.md:81`).
   - The real bias risks are things that move with the arm: temperature, DVFS state and buffer addresses. Second-scale pseudo-random (PRBS) lock-in, an A/A' null and content-swap counterbalancing remove them.
4. **Reframe toward two measurable programs plus a safety link.**
   - **(A) "Compute-allocation circuits":** interp edits that change how much the model computes (looping, verbosity, reasoning length). Measure their joint energy-capability frontier.
   - **(B) A two-channel decomposition:** fixed-token replay versus free-running, with a registered equivalence bound on the physics channel and positive controls.
   - **Safety:** energy witnesses the *process* of editing (unlogged gradient steps or forward-pass probing) and its behavioural consequences, not the edited weights. This extends ALIGN directly.
5. **Staged plan:**
   - Stage 1: microbenchmarks on the M4 Air. No Mac time, no model weights.
   - Stage 2: a by-day pilot on the measurement Mac (MBP), about half a day.
   - Stage 3: a registered experiment of 2-3 Mac-nights, run after the ALIGN D windows and the Paper 1 freeze.

   None of this displaces Mac experiments 1-2 or BYTES stage 1 (12 Nov).

### 1. Physics: how a weight edit can change energy
E = ∫(P_static(T,V) + Σ α·C·V²·f) dt at fixed kernel shapes. An edit can move E through three channels:
- **(a)** the activity factor α, at fixed instructions and timing;
- **(b)** the number and context length of forward passes (behaviour);
- **(c)** bytes moved, kernels launched and cache locality (structure and routing).

There is also a second-order coupling: (a) changes temperature or DVFS state, which changes time (Hertzbleed; Hot Pixels).

**Channel (a): literature numbers (all opened).**
- Gregersen, Patel and Choukse 2024 (arXiv:2409.18324): changing GEMM input data at fixed shapes changes GPU power by "almost 40%". The cause is attributed to bit flips. The abstract page does not name the GPU; a secondary summary says A100.
- Bhalachandra et al. 2022 (arXiv:2212.08805): up to 67% power variation for A100 DGEMM with different matrix values.
- Horace He 2024 (thonking.ai): on an A100 capped at 330 W, all-zero inputs ran at 295 TFLOPS against 257 for randn. The mechanism is fewer transistor flips, so less power-cap throttling.
- Ghose et al., SIGMETRICS 2018 (arXiv:1807.05102): on DDR3L, reading an all-ones cache line uses 39.2% more power on average (up to 91.6%) than an all-zeros line. The number of ones matters far more than toggling. Transfer to LPDDR5 is unknown.
- Apple silicon:
  - Chawla et al. (arXiv:2306.16391): SMC power keys (PHPC, PSTR, PDTR and others) are data-dependent but update only about once per second. A key-byte attack needed about 1 million traces; the TVLA t-score for all-0s vs all-1s on PHPC was 20.94.
  - Hot Pixels (Taneja et al., arXiv:2305.12784): on a passively cooled M1 Air iGPU, higher Hamming weight *lowered* steady-state frequency and power (r = −0.96) through thermal throttling.
  - GPU.zip (IEEE S&P 2024): software-transparent compression creates data-dependent DRAM traffic on Apple GPUs. Whether it applies to the Metal compute buffers that hold MLX weights is not stated. I would guess textures only (UNVERIFIED).
- **Novelty:** I found no published data-dependent energy characterization of matmul or LLM kernels on Apple GPUs.

**Channel (a): our hardware.**
- In memory-bound decode, the GPU rail is dominated by power drawn while stalled. 85% of the known-bytes GPU-rail contrast was the GPU staying powered while it waited on memory (`KB-SLOT-FILL.md:76`). So the data-dependent share of decode energy should be well below the 38-67% compute-bound GEMM figures.
- About three quarters of marginal memory-traffic energy lies outside the rails (rest 0.0296 J/GB against DC 0.0389, `KB-SLOT-FILL.md:22-23,76`). Any DRAM bit-pattern effect would therefore show only at DC/rest.
- **The decisive point:** data-dependent power depends on the *statistics* of operand streams (zero fraction, Hamming weight, bit-transition density), not on which particular values appear. An edit that preserves those statistics has an expected energy change of about 0 even with perfect instruments.
- Rough bound: ΔE/E ≲ f_bytes_touched × |Δα/α| × s_dd **[estimate]**. Plugging in Astra 1.6e-4, ThinkEdit 2e-3 and one ROME MLP matrix at 1e-3 to 1e-2 bytes touched, |Δα/α| ≲ 1e-2 for a statistics-preserving change, and s_dd ≤ 0.4 gives ≤ about 1e-5 to 4e-5.
- Edits that change the statistics (unstructured zeroing, outliers, clipping, format changes) could reach 0.1-10%. That is my estimate. It should be larger in bf16, where a zero is an all-zero bit pattern, than in MLX affine 4-bit, where a pruned zero becomes a mid-range code (my inference).

**Channel (b): behaviour.** In-context decode costs 0.49-0.67 J/token and bare decode about 0.18 J/token (`docs/research-audits/2026-11-07/research-program.md:249` on RP). Late tokens cost more because of the attention terms in the sequence design (`research-program.md:105` on RP). Edit-driven length changes in the literature:
- Astra: about 0.6 × 32,768 ≈ 20k fewer tokens per problem, and the most expensive ones **[estimate]**.
- Activation-Steered Compression (Azizi et al., arXiv:2507.04742): up to 67.43% shorter chain of thought with accuracy maintained, and a 2.73x wall-clock speedup on an 8B model. It reports no energy.
- P-DoS (Gao et al., arXiv:2410.10760): a single poisoned fine-tune sample takes output from 0.5K to 16K tokens (32x).
- ThinkEdit (EMNLP 2025, arXiv:2503.22048): editing about 4% of heads (0.2% of parameters) fixes overly short reasoning, so energy goes up along with accuracy.

**Channel (c): structure.**
- Removing structure saves energy roughly linearly in bytes; BYTES and known-bytes supply the coefficients.
- MoE router or expert edits change which bytes are read and the cache locality.
- Runtime interp hooks are expensive. One 65,536-wide SAE on d = 4,096 is 537M parameters, about 1.07 GB at 16-bit per hooked layer. That is about 20-25% of an 8B 4-bit model's bytes per token (arithmetic). The same feature ablation folded into the weights costs nothing.

**Ranking:** behaviour (10% to 3,000%) ≫ structure (1-50%) ≫ statistics-changing (a) (0.1-10%) ≫ surgical (a) (≤0.001%).

### 2. Edit families

| Family | Bytes or kernels | Weight statistics | Physics channel (fixed tokens) | Behaviour channel | Interp value |
|---|---|---|---|---|---|
| ROME/MEMIT rank-one edits | same | preserved | ≈0 | small, prompt-local | low for energy |
| Direction ablation folded into weights (Arditi et al.: W′ = W − r̂r̂ᵀW over all residual writers, arXiv:2406.11717) | same | preserved | ≈0 | can be large (refusal, looping, verbosity) | **high**: compute-allocation directions |
| Feature ablation via an SAE | runtime hook adds bytes; folded projection adds none | preserved if folded | hook +5-25%; folded ≈0 | varies | runtime "interp tax" makes a clean positive control |
| Steering folded into weights or bias (contrastive weight steering, Fierro & Roger arXiv:2511.05408) | same | preserved | ≈0 | large for length-related behaviours | high |
| Fine-tune deltas (merged LoRA, backdoors) | same | nearly preserved | ≈0 | trigger-dependent; P-DoS shows 32x | safety |
| Unmerged LoRA | adds kernels | — | +1-5%? **[estimate]** at batch 1 | — | control |
| Unstructured pruning | same with dense kernels | changed (zeros) | 0.1-10% **[estimate]** | capability loss | positive control |
| Structured pruning, expert removal | fewer | — | ∝ bytes | capability loss | frontier |
| Quantization | ∝ bits | changed | large | small | a BYTES topic, not interp |
| Model-authored (SEAL arXiv:2506.10943: SFT self-edits; Astra: direct writes) | the result is like one of the rows above | — | as above | as above | **the editing process itself costs compute**: an ALIGN witness |

### 3. Detectability and power analysis
**Noise anchors:**
- **Free-running agent episodes:** a frozen token-count energy model leaves 19-58 J residual SD on 2-4 kJ episodes, about 1-2% (`research-program.md:27` on RP).
- **Token-identical replays:**
  - about 2 J per replay (`:28`);
  - pair-difference SD 2.97 J, or 2.1 J per measurement, about 0.11% (`:114`);
  - between-session offset σ_w 4.67 J (`:114`);
  - an unexplained step of 8-9 J (−0.41%) between sessions (`:154`).
- **DVFS:** benign residuals correlate +0.79 to +0.92 with GPU clock (`:153`).
- **Short runs:** about 0.29-0.49 J repeatability on about 50 J points, with an attribution floor near 1 J (`PROJECT_STATUS.md:100-105` @ origin/main).
- **Microbenchmark (known-bytes):** GPU rail 0.00879 ± 0.00010 J/GB, rails ± 0.0021, DC ± 0.0072 (`KB-SLOT-FILL.md:20-22`). That came from one 3,559 s session of four calls in R, C, C, R order, about 750 s each (`:10`). Per 315 µs dispatch it is about ±0.011 W against a GPU rail of about 10 W, roughly 0.1% (`:76`). A power-rise contrast of 0.144 W was resolved (`:61`), and GPU frequency matched across arms to within 0.08 MHz (`:63`).
- **Instruments:** `powermetrics` delivers about 130 ms records when asked for 100 ms (`KB-SLOT-FILL.md:84`). The KM003C samples at 50 Hz; SMC PDTR is logged at 1 Hz (MVL `methodology-vs-literature.md:67`). The KM003C clock-fit bound is 10-17 ms (`:51`).
- **Thermal and access hazards:** leakage sensitivity is likely 0.08-0.25 %/°C (`:28`). The IOReport entitlement hazard on macOS 27 is noted at `:49`.

**Minimum detectable effects** (paired, two-sided α = 0.05, power 0.8, MDE = 2.8·σ_d/√n):
- **Fixed-token replay**, σ_d = 0.11%:

  | Pairs | MDE |
  |---|---|
  | 8 | 0.109% |
  | 16 | 0.077% |
  | 64 | 0.038% |
  | 256 | 0.019% |

  - An equivalence test (TOST) at a ±0.1% margin needs about 11 pairs; at ±0.05%, about 42.
  - Detecting a true 1e-4 effect needs about 950 pairs; 1e-5 needs about 95,000.
- **PRBS lock-in on the GPU rail:** about 0.1% per hour, scaling as 1/√T. Reaching 0.03% takes about 10 h, and 0.01% is out of reach.
- **DC boundary:** about 70x worse for effects the rails can see. Use it only for DRAM bit-pattern hypotheses.
- **Free-running comparisons:** cannot isolate the physics channel below about 1-2% per episode, because the token model's residual is 19-58 J. Hence fixed-token replay.

**How to beat the noise structurally:**
1. **Use the GPU rail** for compute-side effects; it is insulated from CPU daemons.
2. **Use fixed-token (teacher-forced) replay** to remove the behaviour channel. The estimand is then "energy on a fixed token path".
3. **Run in-process PRBS lock-in.** Keep both versions of the edited tensors resident (weights, scales and biases) and swap references between kernel calls or decode steps on an m-sequence with 0.5-2 s chips; the seed is held by a blinder. Demodulate against the reference convolved with the 130 ms boxcar.
   - The chip length is short against the thermal and DVFS drift band, so a 0.4 °C arm mismatch, worth 0.03-0.1% in ABBA blocks, disappears.
   - A pseudo-random schedule avoids aliasing with periodic timers.
   - Background load becomes uncorrelated variance.
4. **Run nulls:** A/A' (identical content in two buffers) and content-swap counterbalancing cancel address and system-level-cache effects.
5. **Log covariates:** GPU active frequency, residency and SMC temperatures, and test that the demodulated frequency difference is zero.
6. **On the Air:** it is passively cooled, so measure energy per operation rather than power, and keep the duty cycle low (the Hot Pixels mechanism).
7. **Repeats help only when interleaved.** Session steps and σ_w do not average down within one arm.

### 4. Interp payoffs (an honest assessment)
- **Energy as per-component attribution at fixed tokens.** For dense models this is degenerate. If ablation is done by zeroing, ΔJ is about 0. If it is done by skipping the component, ΔJ is just that component's bytes and FLOP cost, which can be computed without a meter.
  - It becomes informative only where computation is conditional: MoE routing, SSD/n-gram paging in Flash-Next, activation-sparse kernels. There, energy is a physical readout of routing. MoEcho (CCS 2025, arXiv:2508.15036) shows routing leaks prompts through microarchitectural channels; a power or SSD-traffic channel is plausible but not yet demonstrated.
  - At the behaviour level, "which components control compute spend" (ThinkEdit's ~4% of heads, Astra's looping direction) is real interpretability, and energy adds the weighting by context length.
- **Energy fingerprints of covert tampering.** Physics predicts no fingerprint for surgical edits at fixed tokens.
  - When the auditor can read the weights, a hash beats any side channel.
  - Energy matters where the auditor controls the meter but not the software or logs, which is ALIGN's threat model. There it witnesses (i) the compute spent finding and making an edit (SEAL SFT steps; Astra's 50 forward passes), (ii) behaviour changes such as P-DoS-style length attacks, and (iii) byte or structure changes.
  - Weight-based sponge attacks (sponge poisoning: Cinà et al., Information Sciences 2025; SkipSponge, up to 13%, arXiv:2402.06357) work by defeating zero-skipping accelerators. Apple's dense kernels give them little to exploit beyond whatever data-dependent α exists, which Stage 1 measures.
  - This matches ALIGN's "power counts work; it is blind to what a token says" (`research-program.md:343` on RP).
- **Joint energy-performance frontiers.** This is the strongest payoff. No measured energy frontier of interp weight edits turned up in my searches (3 searches, not exhaustive).

### 5. Staged plan

| Stage | Contents | Cost | Go/no-go | Publishable? |
|---|---|---|---|---|
| 0, desk | A prediction memo: operand statistics and predicted ΔE per edit family; register the equivalence margins; specify the MLX swap harness | ~1 day | Prediction table committed | No; it is the registration's backbone |
| 1, M4 Air | Ideas 1 and 2 on synthetic matrices only | ~0.5-1 Air-day to build (Sol implements, lead reviews) plus 6-10 h of runs; 0 Mac. Run after BYTES stage 1 so it does not perturb the Air's analysis role | GO if the A/A' null is within ±0.1% in ≤1 h **and** a positive control reaches ≥0.5%. If every positive control is null at ±0.1%, report "Apple GPU data-dependence <0.1%" (itself a contrast with the A100 literature), drop the physics arms and keep the behaviour frontier | A tech note only if Apple's effect is large |
| 2, MBP by day | Idea 3, plus ideas 1 and 2 replicated with the KM003C. Delivered as a kit to the magistrate | 0.3-0.5 Mac-day | GO if replay σ_d ≤ 0.15%, positive controls are detected with the predicted sign, the A/A' null passes, and the behaviour arm shows ≥10% ΔJ per answer | Non-claim pilot |
| 3, registered | Ideas 4 and 6, optionally 7 (H1-H5 below). Blinded edit codes and PRBS key | 2-3 Mac-nights plus ~1 week desk, after the ALIGN D windows and the Paper 1 freeze | Hypotheses frozen before unblinding | A workshop paper (interp, efficiency or safety); with H5, a section of the ALIGN paper; a full paper if the toggle model (idea 5) generalizes across M3 Max and M4 and the frontier holds on ≥2 models |

Stage 3 hypotheses:
- **H1:** for surgical edits, the fixed-token |ΔE| is below 0.1% (TOST).
- **H2:** statistics-changing and byte-changing edits match their predictions.
- **H3:** for compute-allocation edits, ≥95% of ΔE is explained by tokens and context.
- **H4:** a blinded analyst using energy alone classifies surgical edits at chance and structural edits above chance.
- **H5:** unlogged self-edit compute is detected.

### 6. Source status
**Opened:**
- rikiyat.github.io (Astra blog post); seangoedecke.com critique
- arXiv 2409.18324 (Gregersen et al.); 2212.08805 (Bhalachandra et al.); thonking.ai (Horace He)
- arXiv 1807.05102 and its ar5iv page (Ghose et al.)
- arXiv 2306.16391 and its v2 HTML (Chawla et al.); ar5iv 2305.12784 (Hot Pixels)
- hertzbleed.com; hertzbleed.com/gpu.zip
- arXiv 2006.03463 (sponge examples, EuroS&P 2021); 2203.08147 (sponge poisoning); 2402.06357 (SkipSponge); 2410.10760 (P-DoS)
- arXiv 2503.22048 (ThinkEdit); 2507.04742 (ASC); 2506.10943 (SEAL)
- arXiv 2202.05262 (ROME, NeurIPS 2022); 2210.07229 (MEMIT); 2406.11717 and its HTML (Arditi et al.)
- arXiv 2511.05408 (Fierro & Roger); 2312.11514 (LLM in a flash, ACL 2024); 2508.15036 (MoEcho); 2401.13575 (EM architecture extraction on a Jetson Nano)

**UNVERIFIED (not opened):**
- press coverage of Astra (emergent.sh, shiftdelete, cellcog, extrapolator, techjacksolutions, explainx, datacamp, The Register);
- the Kiran Sur blog;
- venue claims for MEMIT (ICLR 2023), Hot Pixels (S&P 2024?) and SEAL (NeurIPS 2025);
- that GPU.zip compression is limited to textures;
- hardware-Trojan power-fingerprinting papers (concept only, none cited).

### 7. Open questions
1. Which small dense model already on the MBP can be used, so that no download is needed?
2. Is IOReport readable on the Air's macOS version without an entitlement?
3. Can the KM003C stay inline during by-day Stage 2?
4. Should H5 (self-edit compute) join ALIGN E2 as an extra dose type rather than a separate night?

#### Seat 2 (Opus 5.5) IDEAS (verbatim content, indented JSON)

```json
[
 {
  "title": "S1: Apple-GPU data-dependent energy ladder (M4 Air desk microbenchmark)",
  "claim": "On Apple GPUs, energy per operation depends on operand statistics (zero fraction, Hamming weight, bit transitions) by at least 0.5% in compute-bound bf16 GEMM, and by less in memory-bound 4-bit quantized matrix-vector products. Perturbations that preserve the statistics (rank-one, sign flips, code permutations with the same histogram) are null within ±0.1%. I found no published characterization for Apple GPU matmul: Hot Pixels used an AND kernel on an M1, and Chawla et al. used CPU AES read through SMC keys.",
  "design": "Synthetic matrices only; no model weights. Kernels: bf16 GEMM 4096² (prefill-like) and an MLX 4-bit quantized matvec 4096×14336 (decode-like). Arms against a randn reference: all-zero, constant, low Hamming weight, 10% and 50% unstructured zeros, sorted rows, rank-one perturbation with ||ΔW||/||W|| in {1e-3, 1e-2, 1e-1}, sign flips, int4 code permutation with the same histogram, 1% outlier injection. Each arm runs in-process against the reference through PRBS buffer swapping (idea 2), with A/A' and content-swap nulls. Readout: IOReport GPU energy (no sudo) plus powermetrics GPU rail; log GPU frequency, residency and SMC temperatures. Duty cycle at most 30%, because the Air is passively cooled (Hot Pixels: on an M1 Air, higher Hamming weight brings more throttling).",
  "cost": "0 Mac-nights. About 0.5-1 Air-day to build (Sol implements, lead reviews) plus 6-10 h of unattended runs. Schedule after BYTES stage 1 (12 Nov).",
  "detectability": "Positive controls: the A100 literature reports 38-67% for GEMM, so even a 1% Apple effect would be about 10x the GPU-rail floor of about 0.1% per hour (KB-SLOT-FILL.md:21,76). Surgical arms are predicted at 1e-5 or below, so they can only be bounded. GO if the A/A' null is within ±0.1% in 1 h or less and a positive control reaches 0.5% or more."
 },
 {
  "title": "PRBS lock-in by in-process weight swapping (instrument method)",
  "claim": "Alternating edited and unedited tensors inside one process on a pseudo-random binary schedule with 0.5-2 s chips moves the contrast above the thermal and DVFS drift band. Background load (daemons, idle agents at 8-47 W) becomes variance uncorrelated with the reference. The method should reach about 0.1% of GPU-rail power per hour and beat 750 s ABBA blocks, because it removes temperature mismatch between arms (leakage 0.08-0.25 %/°C, methodology-vs-literature.md:28).",
  "design": "Keep both versions of only the edited tensors resident (weight, scales and biases for quantized layers). Swap references between decode steps or kernel calls, avoid compiled graphs that capture the weights, and timestamp every swap. A blinder holds the m-sequence seed. Demodulate the GPU rail (powermetrics, about 130 ms records), IOReport and the KM003C at 50 Hz by cross-correlation with the reference convolved with the sampling boxcar, dropping edge samples. Nulls: A/A' (the same content in both buffers) and content-swap (the edited content in buffer 1 for half the run and buffer 2 for the other half). Measure the sensitivity-versus-time curve and compare it with ABBA blocks in the known-bytes shape.",
  "cost": "Built as part of S1. Reused on the MBP in Stage 2 for about 1-2 h of a by-day slot.",
  "detectability": "Anchor: in one roughly 1 h R,C,C,R known-bytes session, the GPU-rail half-width was ±1.05e-4 J/GB, about ±0.011 W on roughly 10 W. Rails were ±0.22 W and DC ±0.77 W in the same session (KB-SLOT-FILL.md:10,20-22,76). Expect about 0.1% per √hour on the GPU rail. Reaching 0.03% takes about 10 h; 0.01% or below is infeasible."
 },
 {
  "title": "Two-channel decomposition of edit energy: fixed-token replay vs free-running (MBP pilot)",
  "claim": "For surgical edits, at least 95% of the per-task |ΔE| comes through the token channel, and the fixed-token physics channel is equivalent to zero within ±0.1% (TOST). Positive controls that change bytes or produce zeros show the predicted sign and size.",
  "design": "One small dense 4-bit model already on the MBP. Arms:\n- A/A' null;\n- direction ablation folded into every residual writer (W' = W − r r^T W) along a verbosity or looping direction;\n- 50% unstructured zeroing of one MLP block, in bf16 and in 4-bit;\n- 10% attention-head removal (bytes positive control);\n- unmerged rank-16 LoRA (kernel-count positive control);\n- a runtime SAE hook against the same feature ablation folded into the weights.\nPhysics channel: teacher-forced decode of the unedited model's token sequences through each arm, ABBA order with 16 pairs per arm, KM003C inline, GPU rail as the primary readout. Behaviour channel: free-running on about 30 prompts per arm, recording energy and tokens per task, attributed with the ALIGN sequence design [1, P, D, (C+P)D + D²/2, CP + P²/2]. Delivered as a magistrate kit.",
  "cost": "About 0.3-0.5 Mac-day by day, with quiet guards on and no ALIGN conflict, plus about 1 desk day.",
  "detectability": "Replay pair-difference SD is 2.97 J on about 2.7 kJ, or 0.11% (research-program.md:114 on the research-program branch). The MDE is 0.077% at n = 16 and 0.038% at n = 64, and TOST at ±0.1% needs about 11 pairs. Behaviour effects of 10-70% are visible in single tasks. Inferring the physics channel from free-running data is limited to about 1-2% by the token model's 19-58 J residual (research-program.md:27), which is why replay is needed."
 },
 {
  "title": "Energy-capability frontiers of compute-allocation edits (registered headline)",
  "claim": "Interp weight edits aimed at compute allocation move joules per correct answer by tens of percent, mostly through tokens and context length. The targets are the looping direction (as in Astra's Qwen3.5-0.8B edit: 0.016% of weights, cap-hitting answers 93.0% to 33.1%), the concise-reasoning direction from Activation-Steered Compression folded into weights (up to 67% shorter chain of thought), and ThinkEdit's short-reasoning heads. The metered frontier (DC plus GPU rail) differs from a tokens-only frontier because late tokens cost more. My 3 searches (not exhaustive) found no measured energy frontier for interp weight edits.",
  "design": "At least 2 models: a small dense reasoning model, and Qwen3-30B-A3B for the MoE case. Use 3-5 edit strengths per family plus the unedited model, on a MATH-500 subset and one agentic task set. Registered metrics: accuracy, tokens, J per task, J per correct answer, and the share explained by the token model. Edit codes are blinded, and arm order is ABBA within each prompt. Our own direction ablation reproduces the Astra-style edit, so Astra itself is not needed.",
  "cost": "2-3 Mac-nights plus about 1 week of desk work, after the ALIGN D windows and the Paper 1 freeze.",
  "detectability": "Large: an expected |ΔE| of 10-70% per task against per-task noise of about 1-2%. The sample size is set by accuracy precision (about 100 or more prompts per arm), not by energy."
 },
 {
  "title": "Toggle model: joules per bit transition on Apple silicon",
  "claim": "A two-parameter model (energy per bit transition in the weight stream, energy per zero operand) calibrated on synthetic ladders predicts the fixed-token energy change of held-out real edits within its interval. That turns any proposed edit into a numerical prediction before it is measured.",
  "design": "For every arm in S1 and in the decomposition pilot, compute operand-stream statistics in software (zero fraction, Hamming weight, Hamming distance between consecutive words in the kernel's streaming order). Regress the lock-in ΔE on the change in those statistics. Validate on held-out edits and on a second quantization format, and replicate on the M3 Max and the M4.",
  "cost": "Desk only beyond S1 and the pilot: about 1 day.",
  "detectability": "Depends on S1. Calibration needs at least one positive control of 0.5% or more; otherwise the result is an upper bound on energy per transition."
 },
 {
  "title": "Blinded tamper-detection challenge (safety null with positive controls)",
  "claim": "Using only fixed-token energy, a blinded analyst classifies surgically edited versus unedited models at chance, and edits that change bytes, structure or zeros above chance. So energy is not a fingerprint of covert surgical tampering; when the auditor can read the weights, a weight hash is the right tool. Energy witnesses compute, as in ALIGN's 'power counts work; it is blind to what a token says'.",
  "design": "A blinder applies one of {none, rank-one knowledge edit, refusal-direction orthogonalization, merged-LoRA backdoor, 2% outlier injection, 10% head removal} to copies of one model. The analyst receives only lock-in or replay energy against a reference copy and applies a pre-registered decision rule. At least 3 blinded copies per class.",
  "cost": "Rides on Stage 3, adding about 0.5 night.",
  "detectability": "Predicted null for the surgical classes: an effect of 1e-5 or below against a 0.04-0.1% floor. Positive classes are expected at 1% or more."
 },
 {
  "title": "Unlogged self-modification leaves an energy signature (ALIGN extension)",
  "claim": "If an agent edits weights without logging it, the ALIGN residual detects the editing compute once it exceeds roughly the in-context decode cost of about 512 tokens (about 250-340 J). The edit can be gradient-based (SEAL-style SFT self-edits) or gradient-free (Astra-style probing with about 50 forward passes). The edited weights themselves stay energy-invisible.",
  "design": "Reuse the E2 confirm-and-inject harness. At blinded doses, benign episodes run hidden LoRA SFT steps, or K forward passes over a probe set, on a small model between turns. Score against the frozen thresholds and fit a dose-response curve. Add a logged-edit control in which the edit compute appears in the log.",
  "cost": "About 1 Mac-night once E2's harness exists, plus about 1-2 desk days. It could instead be folded into E2 as an extra dose type.",
  "detectability": "E2 estimate: 512 or more decode-token equivalents are detected and 256 is marginal (research-program.md:249 on the research-program branch). Compute-bound training steps cost more per token than decode, so a few hundred training tokens should already cross the threshold [estimate]."
 },
 {
  "title": "DRAM data dependence at the DC boundary vs IOReport's DRAM model (banked; joins instrument night #3)",
  "claim": "If LPDDR5 I/O energy depends on streamed bit patterns, the KM003C/rest boundary will show a difference in J/GB between all-zero, random and all-one weight streams at matched bytes. IOReport's counter-based dram channel will not, because it is a model blind to data values, as Ghose et al. found for DRAM power models.",
  "design": "Inside the banked instrument night: use the known-bytes rotate geometry with three bit-pattern fills, read the KM003C, IOReport dram and the rails, and lock in on the fill pattern.",
  "cost": "About 1-2 extra hours inside the instrument night.",
  "detectability": "The DC half-width is 0.0072 J/GB per hour against a 0.039 J/GB coefficient (KB-SLOT-FILL.md:22). Only effects of roughly 40% or more of DRAM-traffic energy are resolvable in an hour. Ghose et al. found 39% on DDR3L; LPDDR5 is unknown."
 },
 {
  "title": "Energy reveals routing: conditional-compute readout in MoE and Flash-Next (banked)",
  "claim": "In MoE and SSD-paged models, fixed-token energy depends on which experts or table rows are used. Router edits and expert ablations therefore have a measurable physics channel, and energy becomes a physical readout of routing. The privacy corollary: MoEcho shows routing leaks prompts through microarchitectural channels, and a power or SSD-traffic channel has not been demonstrated.",
  "design": "On Qwen3-30B-A3B, apply router-temperature edits and expert ablations at fixed tokens, measuring J/token plus DRAM and cache proxies. On Flash-Next with the paged n-gram table, measure energy per lookup at DC.",
  "cost": "About 0.5-1 Mac-night, after Flash-Next live validation.",
  "detectability": "Changes in expert locality move bytes from DRAM or SSD; I expect at least 1% at DC, which is easily detectable."
 }
]
```
