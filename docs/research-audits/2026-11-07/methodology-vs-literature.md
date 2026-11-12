# Our methodology against the literature: new experiments for the measurement Mac

Research track, 2026-11-07. Final durable record.

- **Base:** `origin/main` at `bd7a3efcd`. Lanes read: `lane/2026-11-06-v4-r1-integrated`, `lane/2026-11-07-qwen4exp-mbp-live`, `lane/2026-11-06-sol-qwen4exp-maxfit4`, `lane/2026-11-05-qwen4exp-port-perf`, `lane/2026-10-28-bytes-pass2-open`.
- **Inputs:** two seat reports (seat 1 Fable, seat 2 Opus; verbatim in Appendices A and B), one synthesis that checked every seat disagreement against the repo, the GitHub API (read-only) or the source, and two independent novelty checks per proposed experiment.
- **User request this answers:** "don't just review the research, set it against our methodology and see if there's anything new/interesting that arises for use of that machine; also research what could be achievable re porting Qwen Next and possibly upstreamed."
- **Blinding:** no `jw-b5-*`, `night-*`, night-custody, night-archive or `restricted/` path was read, listed or opened by any seat, the synthesis, the checks or this write-up. The only measured numbers quoted are public non-claim instrument results: the BYTES known-bytes slot fill (`docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md`) and the Block 5 meter qualification text (`configs/campaigns/v5_claim_25g83/registration_block5.md`). No Block 5 or BYTES outcome was seen or inferred. No weights were loaded, no community code was run, nothing was posted to GitHub.

---

## 1. Executive summary

1. **On evidence discipline we are ahead of the field.** No surveyed study bounds phase-edge attribution error, runs identical-condition null quads that test the floor, preregisters and blinds the analysis, or recomputes independently. ML.ENERGY runs each benchmark once; MLPerf Power has no repeat or variance rule; registered reports exist only in software-engineering venues.
2. **Our weak point is the claim boundary and the unvalidated gain of `powermetrics`, and we are less weak there than either seat thought.** BYTES already measures decode at three boundaries (rails, DC input, rest = DC − rails), and the public known-bytes test put about three quarters of memory-traffic energy outside the rails (rest 29.6 ± 8.4 pJ/B vs rails 9.2 ± 2.1 pJ/B). What is still open is phase dependence and an independent read path.
3. **The most valuable Mac-night is the instrument night (idea 1), unrun since the 09-16 prospectus ruled it in.** Its core, a width- and phase-swept energy-conservation test of `powermetrics` against an inline DC meter, has no published precedent on Apple silicon. Both novelty checks agree. Two of its five legs are partly anticipated: the DC − rails gap tracking data movement (an M4 Max forum post, no external meter) and the generation-length-1 prefill trick (Ruf & Detyniecki, HotCarbon 2026).
4. **Two experiments cost no Mac time and have hard registration deadlines.** Idea 2 (agent energy at the machine boundary, from SMC PDTR/PSTR streams ALIGN already logs) must be registered before BYTES stage 1 on 12 Nov. Idea 3 (two-channel physical audit of hidden reasoning tokens) must be registered before D held-out unblinding. Caveat: pilots 4-10 ran Qwen3-30B-A3B under protocol v3, so the Qwen3.8-27B version of idea 2 depends on W1.
5. **No proposed experiment is wholly refuted, but one headline claim is.** Idea 10's claim that the energy-time transfer κ lies in [0.7, 1) is contradicted on CUDA by Dutta et al. (EACL Findings 2026): their κ runs from about −0.1 to +1.2, and their Qwen3-8B/0.6B pair, the pair we proposed, used more energy at ≤1.19× speedup. The residual question (the energy sign of speculative decoding on Apple unified memory) survives, but native MTP has no MLX path and is blocked.
6. **Five ideas are partly anticipated, and their novelty is narrower than first pitched:**
   - idea 5: the sustained MacBook curve is already published (blog-level; Notebookcheck shows this exact chassis holding steady);
   - idea 6: the control tax on SHADE-Arena is already priced in dollars;
   - idea 8: the decode-DVFS mechanism is established on NVIDIA;
   - idea 9: the attention-regime ordering is shown on H200;
   - idea 1, legs (c) and (d).

   In each case the publishable residual is the Apple-silicon, DC-metered, phase-resolved number plus a mechanism test (bytes model, rail/DC split, verdict identity).
7. **Several quantitative predictions are probably wrong, and the checks say so.** We should register them two-sided rather than drop them:
   - idea 5's ≤0.05 %/°C (GPU leakage literature implies 0.08-0.25 %/°C);
   - idea 8's "Low Power Mode costs <15 % throughput" (community data show 28-50 % decode loss, and the M3 Pro's Low Power Mode did not cap the GPU at all);
   - idea 2's ≤30× decode/prefill ratio (a rough M3 Max estimate is 30-70×);
   - Flash-Next's "context slope ≈ 0" (its QSA indexer still reads O(L/4) block keys).
8. **Flash-Next makes the boundary matter for ALIGN.** The n-gram table is host-side, at about 16 row lookups per token, so CPU and storage work is invisible to the turn-owned GPU-rail estimand. The FN addendum must name a DC (PDTR/KM003C) or IOReport boundary. The SSD-tier experiment (idea 4) is the most novel Flash-Next science: no public implementation reports energy. As designed, though, it conflates the storage tier with serial QD1 `pread`, and `F_NOCACHE` does not evict pages already in the buffer cache.
9. **Upstream: verification and small fixes, not a competing port.** The order is:
   1. mlx-vlm D1 (left-padded QSA selection dropped; kit at `f1e0f6673`; still reproduces);
   2. a verification package for mlx-lm #1788 (label `await verification`, idle since 10-04);
   3. a small model-agnostic mlx-lm PR for #1924 (silent quant-map drop).

   For Qwen3-Next itself, mlx-lm `main` already has the model. What is missing upstream is an MTP head plus recurrent-state rollback (PR #990 has been stalled with "changes requested" since March), a chunked gated-delta prefill kernel and a fused head_dim-256 prefill SDPA. All are candidate contributions, but each is multi-week. mlx-lm prohibits AI-written posts, so Ed writes every upstream word.
10. **Proportionality.** Our custody machinery is far heavier than the field's, while the two questions a reviewer asks first (gain and boundary) are the ones still open. The next engineering should go to ideas 1 and 2, not more guards.

---

## 2. Decisions for Ed

These are numbered for reply. Each says what I recommend and what the novelty checks changed.

1. **Mac time: approve one instrument night (idea 1)** at the next quiet non-ALIGN slot, or by day if the guards pass. It needs no frozen pack, and real weights only for small models in one optional segment. It is the prerequisite for ideas 4, 7 and 9.
   - *Changed by the checks:*
     - Before the reader is built, confirm the MBP's macOS version and its IOReport channel list. macmon's README says that on macOS 27 the Energy Model counters can stop updating for processes without a private entitlement.
     - Write the reader in-house, using zeus-apple-silicon and macmon as references only.
     - Test conservation on the summed energy of each pulse train, not per pulse: at 10-20 ms widths the KM003C clock-fit bound (10-17 ms) and GPU DVFS ramp dominate.
     - Make legs (d) and (e) optional.
   - Then choose how many of the remaining Mac-nights to queue behind ALIGN R1, W1 and D1-D5. **My order after the checks is 4, 6, 8, 7, 5, 9, 10**, replacing the synthesis's 4-10. Idea 5 drops because its headline bound is likely falsified, its sustained curve is anticipated and its cost is about double. Idea 7 drops because half of it is answerable from sealed BYTES data after unblinding at zero Mac cost.
   - I register ideas 2 and 3 myself before their deadlines (BYTES stage 1, 12 Nov; D held-out unblinding) and tell you after.
2. **Upstream, first filing:** file the mlx-vlm D1 issue and fix PR in your own words. The kit is commit `f1e0f6673` on `port/qwen4-exp-mlx`: a minimal repro, a +11/−16 fix, logit error 0.15 → ≤3e-7. It still reproduces: `qwen4_exp/language.py` has not changed since 10-13, and there is no matching issue or PR.
3. **Upstream, mlx-lm #1788:** do you want to offer a verification package, in your own words? It would contain transformers-pinned tiny-checkpoint logits, real-weight per-layer parity, and a read-only analysis of the disputed red test (bisected to `ac83bb4`). Separately, do you want a small model-agnostic PR for issue #1924 (warn when a quant override matches no module)? We never run the #1788 branch either way.
4. **Flash-Next energy windows:** choose between:
   - (a) freeing about 110 GB on the MBP internal SSD for a q4-table plus 4-bit-expert measurement build, which stays inside ruling 20 and gives idea 4 its resident control arm;
   - (b) daytime-only external-SSD arms on the borrowed SN7100 under the drafted external-volume amendment.

   I recommend (a) as primary and (b) as a secondary arm.
   - *Changed by the checks:* the core plus the q4 table is about 105 GB against roughly 82 GB free plus the 40 GiB floor. Idea 4 also needs three small code additions before its night:
     - a resident (anonymous-memory) table path;
     - a concurrent-`pread` arm beside the serial one;
     - a purge or `mincore` protocol so the uncached arm really is physical.
5. **Only if you want idea 8 (power modes):** extend the sudoers rule to allow `pmset -c powermode 1`, with the existing restore trap. This is an Ed-physical step; `powermode 1` was tested and refused. *Changed by the checks:* first let me run a 10-minute GPU-frequency pilot (Auto vs Low Power, synthetic Metal load, no weights). Oakley found Low Power capped the GPU on M4 Pro but did nothing to the GPU on M3 Pro. If the M3 Max behaves like the M3 Pro, the Low Power arm is a null by construction and the sudoers change is not worth making.
6. **Physical setup:** keep the KM003C inline through the ALIGN D windows. It refuses nothing, costs about 0.25 % of one core, and adds 50 Hz turn-level resolution beside the 1 Hz PDTR stream ALIGN already records. The Flash-Next boundary and ideas 2 and 6 need it.
7. **No action needed (for information):** I am dropping idea 10's κ-band claim as refuted and parking speculative/MTP decoding. It returns only if an MTP head plus recurrent-state rollback exists on our stack. That code would itself be an upstream contribution to mlx-lm, but it is multi-week runtime work, not a qualification day.

---

## 3. Synthesized report

This is the synthesis as written: two seat reports, with every disagreement and every load-bearing claim checked against the repo, the GitHub API (read-only) or the source. Section 4 records what the per-experiment novelty checks changed afterwards.

### 3.0 Bottom line

1. **Evidence discipline: we are ahead of the field.** The seats agree, and the sources confirm it. Nothing surveyed bounds phase-edge attribution error, runs identical-condition null quads that test the floor, preregisters and blinds the analysis, or recomputes independently.
   - ML.ENERGY runs each benchmark once.
   - MLPerf Power sets no repeat or variance rule.
   - Registered reports exist only in software-engineering venues (ESEM, MSR).
2. **Our weak point is the boundary, but we are less weak than both seats said.**
   - Block 5's claim boundary is the `powermetrics` CPU+GPU+ANE rail. Apple's man page says these values are "estimated and may be inaccurate" and "should not be used for any comparison between devices" (verified).
   - **Both seats missed this:** BYTES already measures decode at three boundaries for 10 models: rails, DC input (KM003C plus battery term) and rest = DC − rails.
   - **Both seats also missed this:** the known-bytes stream test has already run (2026-10-30/31; public non-claim slot fill, `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md`). It measured memory-traffic energy (bytes from DRAM minus the same work from cache), in J/GB:

     | Boundary | Energy per GB |
     |---|---|
     | Rails | 0.0092 ± 0.0021 |
     | GPU rail | 0.00879 ± 0.00010 |
     | DC | 0.0389 ± 0.0072 |
     | Rest | 0.0296 ± 0.0084 |

     So about three quarters of memory-traffic energy lands outside the rails, which supports the seats' worry with our own number. What remains open is phase dependence (BYTES is decode-only at a 2,048-token prompt) and an independent read path.
3. **The cheapest high-value experiment is still unrun, and it is two arms, not one.** The 09-16 prospectus (`docs/process/research_plan_2026-09-16.md`) ruled in two `DIAGNOSTIC_NO_PACK` arms:
   - the IOReport "Energy Model" cross-check;
   - a generation-length-1 boundary-free prefill check.

   Neither ran: no IOReport reader exists in the codebase, and no run report mentions either arm. Seat 2 named only the first. Together they test the paper's own stated applicability assumption: the paper draft (line 53) says transfer of the pulse bound to inference load is "an applicability assumption, not a result".
4. **ALIGN episodes already carry a machine boundary. Both seats missed this.**
   - ALIGN windows log SMC PDTR (DC-in), PSTR (system total) and the battery term at 1 Hz (`joulewise/hazards/smc.py`). They print PSTR − rails as the "unassigned power residual".
   - PDTR is validated against the KM003C: PDTR = 0.955 × meter + 2.3 W, r = 0.9975 on 20 s bins (registration_block5 §5.8; re-verified for this write-up at line 3546 of `configs/campaigns/v5_claim_25g83/registration_block5.md` on `bd7a3efcd`).
   - So the agent machine-boundary decomposition needs no new night or hardware. It is analysis.
5. **Flash-Next makes the boundary matter for ALIGN.**
   - The n-gram table is host-side and never GPU-resident (canonical port).
   - Per-token lookups are about 16: mlx-vlm #2045 counts 65,545 cold misses on a 4K prefill, about 4,096 × 16.
   - That is CPU and storage work the turn-owned GPU-rail estimand cannot see, so FN-vs-D comparisons are biased in FN's favour unless the FN addendum (FN-Q, PENDING) names a DC (PDTR/KM003C) or IOReport boundary.
   - The fidelity build ("maxfit", about 211 GB) cannot sit on the internal disk (51-115 GB free historically), and ruling 20 refuses external volumes in windows. The practical *measurement* build is therefore a q4-PLE plus 4-bit-expert artifact on the internal disk. It also gives the resident-table control arm the SSD-tier experiment needs.
6. **Upstream.** The achievable path is verification and fixes, not a competing port. In order:
   - mlx-vlm D1: ready, and still reproduces on current code.
   - A verification package for mlx-lm #1788.
   - A small mlx-lm PR for issue #1924's silent quant-map drop.

### 3.1 How the two seats compare

| Topic | Seat 1 (Fable) | Seat 2 (Opus) | Resolution (verified) |
|---|---|---|---|
| Boundary weakness | Rail excludes memory; ρ is request-level only | Same, plus the forum M4 Max gap | Both right for Block 5. BYTES already has a rest boundary, and the known-bytes test puts about 76% of memory-traffic energy in rest. The ρ study is re-scoped to prefill and context. |
| IOReport cross-check | Not mentioned | Top recommendation, unrun | Verified unrun. The generation-length-1 arm is also unrun. Both are folded into idea 1. |
| SSD tier for Flash-Next | External SN7100; mixed bf16/q8/q4 tables | Internal SSD; one q4 table in three serving modes | Seat 2's single-artifact design is identical work; seat 1's is not. Internal is primary (ruling 20); external is a daytime secondary arm under the drafted amendment. |
| Unowned agent share | ≥25% of machine energy | <10% of gross energy | Protocol planning figures (decode about 11 tok/s on D, 0.2-3 s tool waits) favour <10%. Registered as a two-sided band. |
| Speculative decoding | Energy saving ≥70% of the speedup fraction | Energy saving < speedup | Compatible. One claim: 0.7 ≤ κ < 1 (idea 10). AXI-SC found native MTP had no usable generation surface on the pinned stack, so this waits for stack B. *(Later refuted as a law by the novelty checks; see section 4.)* |
| Hybrid / context | Qwen3-Next-80B vs Qwen3-30B-A3B | Full attention vs Qwen3.8-27B (a `qwen3_5`-family hybrid) vs Flash-Next | Merged. Seat 2's "Flash-Next flat beyond 2,051 tokens" is corrected: our port's sparse-decode dispatch defaults to 8,192 KV (canonical item 4). |
| Monitor energy | Information-access arms | Re-read vs prefix-cached vs end of episode | Merged into one 2×2 (idea 6). Energy ratios use pilot and W1 transcripts only; D held-out episode energies are outcome-bearing until unblinding. |
| #1788 flake | "Our tie/rounding findings likely explain it" | Not discussed | Unverified hypothesis. The reporter bisected the red to the +1-fold commit `ac83bb4`. The author (M3 Max, MLX 0.31.2 and 0.32.0, 30 seeds, worst 9.7e-7) and a second user (M3 Pro, MLX 0.32.3) cannot reproduce it. |
| mlx-vlm D1 | Listed among audit findings | "No existing issue or PR" | Verified. `qwen4_exp/language.py` last changed 2026-10-13 (#2273), before the D1 repro at `5cdc659b` (11-05). #2126 kept explicit masks for ragged batches. No matching issue or PR found. |

### 3.2 Where we are stronger or weaker than standard practice (verified sources)

**Stronger**

- **Phase-edge error.**
  - Yang et al. show nvidia-smi on A100/H100 averages only the last 25 ms of each 100 ms update. Their fixes cut mean error from 39.27% to 4.89%. Our varied-gap pulse schedule is the same remedy, formalised. **But** nobody, including us, has measured `powermetrics`' own duty cycle (idea 1).
  - TokenPowerBench and "From Prompts to Power" report no phase-edge error budget. These two were carried from seat 2 and not re-opened.
- **Preregistration, blinding and independent recompute.**
  - Hoefler & Belli (SC'15, 120 papers) and Mytkowicz et al. (ASPLOS'09, 133 papers, none handled measurement bias) describe the state of practice.
  - No ML-energy registered report was found.
- **Agent attribution.**
  - Luo et al. (arXiv:2609.29707, also a NeurIPS 2026 workshop poster) work at whole-run granularity: GPU-only telemetry misses 41-45% of system energy, and an agent uses 63× serving energy per token. Qwen3.8-27B is our D model.
  - A-LEMS (energy per successful goal) reports GPU dynamic energy at 83.8% of agentic EpG locally.
  - The KAIST HPCA 2026 department page reports 136.6× energy per query and GPU idle up to 54.5% in tool phases.
  - Our turn-owned tiling is finer than any of them.
- **Laptop confounds.**
  - MLPerf Power excludes battery devices.
  - Tummalapalli et al. ran their only laptop (RTX 4050) on battery. Our battery float plus battery term handles what they skip.
- **Apple practice.**
  - GreenBench, IPW and Apple vs Oranges use `powermetrics` alone. IPW's own platform page warns that GPU-only Apple energy is "badly understated" for ANE workloads.
  - GreenBench's abstract reports 0.47 W CPU+GPU package power during sustained inference of 3-9B models at up to 175 tok/s. That is below our idle-admission bar (p95 combined processor power ≤ 1 W), so it is more likely a sampler artifact than a finding. The abstract states 8-12 W system power without saying how it was measured.

**Weaker**

- **The claim boundary.** Block 5's claim boundary is the rails. MLPerf requires whole-system measurement. BYTES partly fixes this; Block 5 does not.
- **Gain is unvalidated.** No public study validates `powermetrics` gain on any M-series chip.
- **The forum M4 Max report** (Mac Studio, one poster, no replies): GPU rail +65 W against PDTR +179 W. The poster used PDTR, not an inline meter, and attributes the gap to on-chip SRAM data movement (about 5 pJ/B), a different quantity from our DRAM-traffic 38.9 pJ/B at DC. Idea 1 separates the two using IOReport's `dram` and `gpu_sram` channels; zeus-apple-silicon confirms both exist, at about 1 mJ, without root.
- **Time resolution.**
  - Records arrive about every 129 ms; 37 of 50 short diagnostic prefills were not resolvable (WO-4/Q9).
  - The meter and battery edge term is τ ≈ 2.3 s (BYTES §7), so DC-boundary phase splits need phases ≥ about 12 s.
  - At the processor's large prefill step, BYTES saw the battery discharge for 1.2-2.1 s after every Qwen3.5-122B prefill-to-decode step: the 140 W adapter is exceeded at peak, so the battery term is load-bearing for big models.
- **Order.** Block 5 runs a fixed A/B/B/A order, "not randomized" (analysis_plan_block5 line 378). New packs should randomize each block's orientation (A/B/B/A or B/A/A/B) at no cost.
- **External validity.** One unit and one stack (Maricq et al., OSDI'18). SiliconBench found one upstream bump broke 3 of 10 Apple stacks. Batch 1, one prompt.
- **Gated energy is reference-state energy.** v4 says so itself ("ordinary production agents do not make these pauses"). The pauses also cost time: ruling 1(f) "will probably bind on hardware" (LEAD-RULINGS-2), with the G0 cap at 600-1,200 s.
- **Proportionality.** Our custody machinery is far heavier than the field's, while the two things a reviewer asks first (gain and boundary) are the ones still open. Spend the next engineering there (ideas 1 and 4), not on more guards.

### 3.3 Literature claims this rig can test (verified wording)

1. **Speculative decoding.** Dutta et al. used an A5000 with CodeCarbon at 1 s and batch 1. The synthesis could not confirm the EACL venue; the novelty checks later did (EACL Findings 2026).
   - Vanilla decoding "can sometimes be more energy-efficient".
   - Qwen3-8B: 0.91× on GSM-8k and 0.67× on CNN-DM.
   - Llama-70B on CNN-DM: 0.61-0.65×.
   - On MLX, the best EAGLE-3 speedup was 1.05× on an M3 Ultra (mlx-lm discussion #890).
   - Tested by idea 10.
2. **SSD offload of MoE experts** (Kyung, Yun & Ahn, IEEE CAL, arXiv:2508.06978). This is *modeled*, not measured, with flash at 102.4 pJ/b (110.8 pJ/b for the whole path). Results: 3.8-12.5× for Mixtral and 4.7-9.8× for DeepSeek-R1. The small-batch and edge "win" holds only if flash read energy falls about 10×. Tested by idea 1 (measured J/bit) and idea 4, stage 2.
3. **Engram.** A 100B table in host DRAM costs at most 2.8% throughput on an H800. An NVMe tier is proposed but untested, and energy is not discussed. Tested by idea 4.
4. **Wu et al.** At batch 1 with a cached prefix, a decode token costs about 335× a prefill token (about 115× uncached). The KV-context term does not amortize with batch size. Tested by idea 2 (the BYTES ratio) and idea 9.
5. **Luo et al.** The 41-45% GPU-only miss, <1% per-token difference between thinking modes, and 63× agent vs serving. Tested by ideas 2 and 3.
6. **Ma et al.** (PPAM 2026, H200). Power caps barely affect decode; locking the SM clock recovers up to 32% of decode energy; Gated DeltaNet and Mamba2 pay no prefill penalty. Tested by ideas 8 and 9.
7. **Chkir et al.** MHA steepest; GQA+SWA nearly constant with context; no hybrid tested. Tested by idea 9.
8. **Huang & Niu** (NeurIPS 2026 workshop). On mlx-lm a quantized KV cache forces unfused prefill, costing 256 KiB/token against a 92 KiB/token cache saving. Tested by idea 9 (KV arm).
9. **Benazir & Lin.** Lower bit-width is not always faster on Apple silicon because of dequantisation overhead; no energy measured in the abstract. Tested by idea 7 (bits arm).
10. **Tummalapalli et al.** The iPhone 16 Pro plateaus 41.5% below peak throughput. Seat 1's "halves within two iterations" is wrong; the decline is about 27% within three iterations. No MacBook was measured. Tested by idea 5.
11. **Kimpson, Baker & Graham.** Matched-energy strategies hide at least 41% of compute from analogue power. Re-executing declared work tightens this to 5.9%. Tested by idea 3.
12. **Arike et al.** The "less-is-more" effect for monitors, and extract-and-evaluate (EaE). The abstract does not say how cost was measured; the checks found it is API dollars (section 5.5 of the paper). Tested by idea 6.

### 3.4 Flash-Next (qwen4_exp): what is achievable, and what can go upstream

**State on 2026-11-07, verified:**

- **mlx-lm #1788.**
  - Open since 08-26; one community approval (08-29); label `await verification` added 08-29 by a maintainer; merge state blocked; 23 comments; idle since 10-04.
  - Open threads:
    - a seed-1234 hash-constant fix and load check (merged into the branch);
    - sje397's report that `test_qwen4_exp` is red at head (prefill vs stepwise 1.07e-3 against atol 1e-4; green at `365170c`, red by `ac83bb4`), which the author and another user cannot reproduce;
    - community quantized checkpoints failing to load.
  - mlx-lm `main` has `qwen3_next.py` and `longcat_flash_ngram.py`, which holds its n-gram tables as resident `nn.Embedding`, so a paged store would be new. It has no `qwen4_exp`.
  - Latest releases: mlx-lm 0.32.2 (10-16) and mlx 0.32.4. Issue #1924 (silent quant-map drop) is open; #1798 is closed as fixed.
  - CONTRIBUTING allows AI-written code with disclosure, but **prohibits AI-written posts** (PR descriptions, issues, replies).
- **mlx-vlm** (now Neywa-Labs).
  - #2032 (qwen4_exp) merged 08-26.
  - #2045 (external PLE storage) merged 08-28: a Q4 table of about 30 GB; 71.68 GB active with the PLE outside; on an M2 Ultra, 19.04 tok/s decode and a 217.8 tok/s 4K prefill in which 65,545 cold misses spent 9.68 s.
  - #2126 (batched parity, 09-04).
  - DFlash defects: issue #2581 and PR #2630, both open.
  - No AI clause in CONTRIBUTING and no PR template.
- **llama.cpp #27742** merged 08-27, with host-side row indices into a 97.7 GiB table.
- **Ours.**
  - The canonical module passes 31 tests at fp32 parity ≤ 1e-5.
  - Real-weight parity passes for layers 2 and 3 (fp32 rel ≤ 5.8e-6).
  - The fidelity build ("maxfit") has 6-bit experts, everything else bf16, and the bf16 PLE (102.4 GB) on disk. It peaks at 112.7 GB at 40,960 tokens against the 115.4 GB working set, needs about 211 GB of disk, and has a 97.6 GB 5-bit-expert fallback ("maxfit5"). It runs on the borrowed SN7100, which is DRAM-less and has no host memory buffer through USB4.

**Achievable contributions, in order:**

1. **mlx-vlm D1 fix.** Left-padded batches drop the QSA sparse selection. The kit is commit `f1e0f6673` on `port/qwen4-exp-mlx`: repro, a +11/−16 fix, max |dlogit| 0.15 → ≤ 3e-7. Ed files it in his own words.
2. **A verification package for #1788**, which is what its label asks for. It would hold transformers-pinned tiny-checkpoint logits, real-weight per-layer parity, and a read-only analysis of the red test: whether the `ac83bb4` +1 fold interacts with the test's random-init norms, or a near-tie in the router or QSA. Our tie diagnostics can check the second on our own module. We never run the PR branch, and Ed writes every word posted.
3. **A small mlx-lm PR for #1924**: warn or raise when a per-module quant override matches no module, with matched/total counts. It is model-agnostic and a good first mlx-lm contribution. Seat 2's "one open PR for a new contributor" limit (#1749) was not verified.
4. **Later, a bf16/q8 option for mlx-vlm's `ple_storage.py`.** The #2045 text says it keeps "the requested bit width and mode", so read the file before offering. Also later: a paged n-gram store for mlx-lm, once #1788 lands.
5. **The scientific contribution none of the three implementations report: measured energy of SSD-tier conditional memory** (idea 4).

**Not realistic:** a competing full-model PR. Every upstream piece also needs a port from mlx-lm 0.31.3 to 0.32.x. The GOAL's planned bridging window (anchors on old and new stacks back to back) covers the measurement side. Register seat 1's claim for it: the offset exceeds the U3 bar of 3 × max(2.97 J, 0.11% of pair energy).

### 3.5 Consequences now, whatever is chosen

1. Run the instrument night before any further boundary-dependent claim.
2. Before 12 Nov, the lead registers (lead-owned prereg ruling, public deviation log):
   - the BYTES descriptive prefill/decode per-token ratio;
   - the idea-7 predictions, so they stay blind to BYTES' DC outcomes.
3. The FN addendum names a PDTR/KM003C or IOReport boundary and the internal q4 measurement build.
4. New packs randomize each block's orientation.
5. Idea 5's β_T (energy per °C) is the evidence-based route to shorter G0/G1 waits. The checks found this payoff is unlikely; see section 4.

### 3.6 Corrected, dropped or unverified (synthesis stage)

**Corrected**

- GreenBench system power: seat 1 said "assumed". The abstract reports it as a finding; the method is not stated. A novelty check that opened the HTML body found the 8-12 W is estimated from thermal specs (a fixed 10 W), so seat 1 was right in substance.
- Tummalapalli: seat 1's "halves within two iterations" is wrong; it is a 41.5% plateau.
- Kyung: the range is 3.8-12.5× (Mixtral) and 4.7-9.8× (DeepSeek-R1), not 4.7-12.5×. The edge exception is conditional on about 10× better flash.
- Seat 2's MDE "80-370 tokens" was not found. CHAIR gives model misfit of 53-73 token-equivalents (or 1.2-1.7% of E) against an instrument floor of about 10 tokens (30 at 3σ). The principle (misfit, not the meter, limits detection) is verified.
- Seat 2's Flash-Next threshold of 2,051 tokens: our port dispatches sparse decode at 8,192 KV by default.
- Seat 2's "about 86 GB resident" for the q4-PLE build: by mlx-vlm's figures it is about 102 GB. It fits, but must be confirmed by the fit probe.

**Unverified (dropped from claims)**

- Arike et al. "API dollars": the checks later confirmed the cost basis is API USD per transcript, on MLE-Sabotage only.
- Seat 1's #1788 flake explanation.
- Seat 2's b_fiducial ≈ 30 ms, "8 refused attempts / 37 h dry runs", and mlx-lm #1749.

**Carried from the seats, not re-opened in the synthesis:** Hähnel, Dauner, Khan, Jay, JouleSort, Zhuang, the Zeus NSDI paper, Vellaisamy, Zine, Zähl, Fernandez, Krupp, Jin et al., AgentStop, Apple vs Oranges, From Prompts to Power, TokenPowerBench, AI Energy Score, Hydra, StarCoder2 quantization, Alfarizy (EmergentMind summary only), CoIn, the CoT-monitorability paper, Bielik. The novelty checks later opened Hähnel, Dauner, Fernandez, AgentStop, Apple vs Oranges, TokenPowerBench and CoIn.

**Opened in the synthesis:**

- arXiv 2608.28667, 2609.29707 and the matching NeurIPS 170717 page, 2508.06978 (abstract and HTML), 2601.07372, 2602.09113, 2601.21112, 2312.02741, 2603.23640, 2608.25096, 2605.11999, 2508.08531, 2506.04301, 2605.22883.
- NeurIPS 170701 (Wu et al.), 171195 (Huang & Niu) and 139658 (SiliconBench).
- The MATS page for Kimpson et al.
- Apple forum thread 819927, the `powermetrics` man page, the zeus-apple-silicon README, the IPW platform page, the KAIST EE page, mlx-lm discussion #890.
- GitHub API: mlx-lm #1788 (comments, reviews, timeline), #1924, #1798, CONTRIBUTING, the models directory and `longcat_flash_ngram.py`; Neywa-Labs/mlx-vlm #2032, #2045, #2126, #2630, #2581, the `qwen4_exp` tree, CONTRIBUTING and the commit history of `language.py`; llama.cpp #27742.

---

## 4. What the novelty checks changed

Each experiment got two independent novelty and feasibility checks. Both checkers ran out of web-search budget early and worked from direct fetches of known URLs, so "no prior work found" is weaker evidence than it would be after a full search. The cross-cutting results:

1. **Citation disputes, resolved.**
   - *Kyung et al.*: both checks marked it UNVERIFIED because it is not in `docs/report_src/references.csl.json`. It exists: arXiv:2508.06978, opened by seat 1 and by the synthesis. **Action:** add it to the bibliography before any preregistration cites its 110.8 pJ/b.
   - *Kimpson et al.*: the checks could not find it. The synthesis opened it, but it is a MATS research page, not a peer-reviewed paper. Cite it as such.
   - *Luo et al.*: one check could not locate it; the other opened arXiv:2609.29707 (2× RTX PRO 6000 Blackwell, Qwen3.8-27B, IPMI at 1 Hz). Verified.
   - *PDTR = 0.955 × meter + 2.3 W*: one check could not find this in the repo. It is at `registration_block5.md` line 3546 (verified for this write-up). Register its fit range with it, because the 2.3 W intercept matters for idle-level unowned segments.
2. **Model mismatch for ALIGN-transcript ideas (2, 3, 6).** Pilots 4-10 ran Qwen3-30B-A3B 4-bit under protocol v3. Qwen3.8-27B episodes exist only once W1 runs. Pilot-based lines must carry the right model name, and 27B claims are W1-dependent.
3. **The time channel in idea 3 rests on the ratio of prefill power to decode power (about 1.8 on this Mac, from the pilot-1 record), not on seconds per token.** An attacker with two knobs (prefill inflation plus context inflation) can in principle null both channels. The registration must include that mixed attack class, and turn duration must come from the trusted power trace, not from harness timestamps.
4. **Several "first" claims are platform firsts, not phenomenon firsts:** ideas 5, 8 and 9. Frame them as Apple-silicon, DC-metered, phase-resolved measurements with a mechanism test.
5. **IOReport's DRAM channel is a third boundary for ideas 1 and 7.** zeus-apple-silicon reads it without sudo on M1-M4. M3 Max is not individually listed, GPU SRAM is absent on M5, and the macOS 27 entitlement hazard applies. Split rest into DRAM-model energy versus conversion loss and fans, and use the split as the first published check of Apple's DRAM energy model against an inline meter.
6. **Qwen-Next porting and upstream (from checks 4, 9 and 10).**
   - mlx-lm `main` already ships `qwen3_next.py` with `gated_delta` Metal kernels (generic, plus a packed Dk=128 variant). Its `sanitize` strips `mtp.*` weights.
   - Native Qwen MTP is stalled. PR #990 has been open since 2026-03-13 with "changes requested". #1532, #1740 and #1543 were closed in its favour on 2026-08-21.
   - Since #1109 (v0.31.2), speculative decoding raises on non-trimmable caches (ArraysCache). Hybrid Gated-DeltaNet targets therefore cannot use even draft-model speculation until recurrent-state snapshot and rollback exist.
   - A test-backed, head-only MTP PR plus state rollback is a credible upstream route, but it is multi-week.
   - On the pinned mlx-lm 0.31.3, gated-delta prefill is a recurrent kernel that loops sequentially over T. MLX 0.31.2 also has no fused head_dim-256 prefill SDPA, so Qwen3-Next's 12 attention layers materialise full score matrices.
   - A chunked gated-delta prefill kernel and a fused head_dim-256 SDPA are therefore upstreamable. Check MLX ≥ 0.32 first. They are also measurable before and after (idea 9's "kernel-path-labelled context terms"). Until then, hybrid-prefill energy results describe mlx-lm's kernels, not the architecture.
   - Our port's I/O path fits as a follow-up to mlx-vlm #2045: per-row `MADV_WILLNEED` prefetch (2.8× faster than serial faults in our bench), `F_NOCACHE` pread and fault counters.
   - Choosing the QSA dense/sparse dispatch thresholds by measured *energy* crossover rather than M4 latency would be a small, novel, upstreamable improvement.
   - Draft-model speculation observability is cheaper than AXI-SC assumed. `GenerationResponse.from_draft` plus the one-non-draft-token-per-round structure rebuilds per-round accepted length with a thin wrapper.

---

## 5. Proposed experiments: novelty verdicts, ranked by novelty × value / cost

**Scoring.**

- **Novelty (N, 1-3)** comes from the two checks. 3 means survives intact; 2 means partly anticipated; 1 means the headline was refuted and only a residual survives.
- **Value (V, 1-3)** is what the result does for the paper, ALIGN or Flash-Next.
- **Cost (C)** is Mac-nights, re-estimated by the checks where they disagreed with the original figure. Desk-only work counts as 0.25.
- **Score = N × V / C.**

Ideas 2 and 3 top the list because they cost no Mac time, not because they are the most important science. Among Mac-night experiments the order is 1, 4, 6, 8, 7, 5, 9, 10.

| Rank | Idea | Verdict (two checks) | Closest prior work (opened by the checks) | What survives | Feasibility notes | C (Mac-nights) | N × V / C |
|---|---|---|---|---|---|---|---|
| 1 | **2. Agent energy at the machine boundary + BYTES riders** | Survives, partly anticipated (2/2 not refuted) | [Luo et al. 2609.29707](https://arxiv.org/abs/2609.29707); [AgentStop 2605.15206](https://arxiv.org/abs/2605.15206); [KAIST 2506.04301](https://arxiv.org/abs/2506.04301); [Wu et al.](https://neurips.cc/virtual/2026/170701) | First metered DC-boundary decomposition of local agent episodes on unified memory: ρ across episodes, unowned share, CPU-rail energy inside tool spans. Also decides whether the five-term residual needs a sixth (gap/tool) term. | Pilots 4-10 are Qwen3-30B-A3B (v3); 27B lines need W1. Confirm the pilots logged SMC before registering. 1 Hz SMC cannot tile 0.2-3 s segments, so DC applies only to episode totals. KAIST's 54.5% is a *time* share, so the "reverse of the server finding" framing is not like for like. Use Wu's 115× (uncached) as the comparator, not 335×. ≤30× may be falsified (estimate 30-70×). ρ < 0.85 is near-certain, so report intervals, not a bound. | 0 (desk) | 2 × 3 / 0.25 = 24 |
| 2 | **3. Two-channel physical audit of hidden tokens** | Survives (2/2 not refuted) | [CoIn 2505.13778](https://arxiv.org/abs/2505.13778); [Gargiulo & Kulp 2609.00309](https://arxiv.org/abs/2609.00309); [Gu et al. 2502.07776](https://arxiv.org/abs/2502.07776) | No work treats *stripping* of reasoning tokens as the threat, or uses physical energy plus trusted time as two detectors with an attack grid. | The mechanism is the P_prefill/P_decode ratio (≈1.8 on this Mac), so restate it. Add the two-knob mixed attack and a structural channel (turn t+1 prompt = turn t context + outputs). Time from the trusted power trace only. Thermal/DVFS inflates the time residual's s_t, so stratify by thermal state. With m ≈ 12-14 benign trajectories the minimum FPR is ≈0.07, so Bonferroni at α/2 may be unattainable; prefer a joint Mahalanobis score. Check which build produced D: unclosed-reasoning turns logged hidden_tokens = 0 before the fix. | 0 (desk) | 2.5 × 2 / 0.25 = 20 |
| 3 | **1. Instrument night** | Survives for (a)(b)(e); (c)(d) partly anticipated (2/2 not refuted) | [Dauner et al., HotCarbon 2026](https://hotcarbon.org/assets/2026/paper-46.pdf); [Apple forum 819927](https://developer.apple.com/forums/thread/819927); [Ruf & Detyniecki, HotCarbon 2026](https://hotcarbon.org/assets/2026/paper-17.pdf); [Yang et al. 2312.02741](https://arxiv.org/abs/2312.02741) | (a) No published validation of `powermetrics` energy conservation against an external meter. (b) No documented IOReport edge-displacement behaviour. (c) Narrower: the DC − rails gap was shown informally on an M4 Max (PDTR, one workload), so frame (c) as a meter-boundary replication of Petar_M's ≈5 pJ/B and ≈2.7 pJ/FLOP. (d) Generation-length-1 is Ruf's method; only the closure test is ours. | macOS 27 IOReport entitlement hazard ([macmon](https://github.com/vladkens/macmon)): check the MBP OS first. 10-20 ms pulses are not resolvable per pulse, so test train-level E_pm/E_DC. Hold the bytes/FLOP mix fixed in pulses. Measure poller self-load. Control display, PMIC and battery path in the gap. No storage rail exists, so SSD J/bit is a residual of only ≈0.4-0.5 W at QD1. The 20 GB scratch file must respect the disk guard. Build the reader in-house, not from community code. The 0.5 Air-day reader build is optimistic. Rank (a)(b)(c); (d)(e) optional. | 1 | 2.5 × 3 / 1 = 7.5 |
| 4 | **4. SSD-tier conditional memory (Flash-Next PLE)** | Survives (2/2 not refuted) | [mlx-vlm #2045](https://github.com/Blaizzy/mlx-vlm/pull/2045); [EdgeMoE 2308.14352](https://arxiv.org/abs/2308.14352); [Engram 2601.07372](https://arxiv.org/abs/2601.07372); [TF-Engram 2607.07388](https://arxiv.org/abs/2607.07388) | First energy measurement of a conditional-memory table served from storage, the first on unified memory, a prefill estimand, a DC-vs-rail split and a bitwise-identical ladder. EdgeMoE (decode, +1.1% to +17%, Jetson) is the only energy analogue. | No resident arm exists in code, so arm A needs a new anonymous-memory path. `F_NOCACHE` does not evict buffer-cache pages, so purge or check `mincore` before each C member. Serial QD1 `pread` makes arm C measure syscalls (1,399 ms vs 36-38 ms cold mmap in our bench), so add a concurrent arm. Stall-vs-bytes is untestable with one prompt, so vary concurrency or the dedupe ratio. Memory for arm A is ≈108-118 GB. Disk is ≈105 GB vs ≈82 GB free. Decode ≤10% and GPU-rail <10% are near-certain passes. Price the 25% prefill bar from stall time. Stage 2 (bf16 experts ≈240 GB) is external-only and a separate prereg. | 1.5 | 3 × 2.5 / 1.5 = 5 |
| 5 | **6. Oversight tax (monitor energy)** | Survives, partly anticipated (2/2 not refuted) | [Control Tax 2506.05296](https://arxiv.org/abs/2506.05296); [SHADE-Arena 2506.15740](https://arxiv.org/html/2506.15740); [Arike et al. 2601.21112](https://arxiv.org/abs/2601.21112) | Monitor cost on SHADE is published in USD (Control Tax App. K: $20-$120), and SHADE's own monitor is M1. New: the control tax in joules on the machine running both agent and monitor; energy ÷ token ratio (the long-context attention term); verdict identity under prefix caching on MLX; co-resident bandwidth interference. | Claims (ii) and (iii) are mostly token arithmetic, so compute them from transcripts before spending a night and run only the arms that are not already determined. M4 keeps tool *results*, so the CoT share may be <50%. Monitor thinking off. Cached vs re-prefilled greedy output can diverge on MLX, so define identity on the parsed score. Pilots are a 30B-A3B agent. The 27B secondary monitor will not fit the same night. Pilot transcripts are under `night-*` custody, so the lead or magistrate must assemble them. | 1 (+1) | 2 × 2 / 1 = 4 |
| 6 | **8. DVFS power modes by phase** | Survives, partly anticipated (2/2 not refuted) | [Ma et al. 2605.11999](https://arxiv.org/abs/2605.11999); [Oakley, Eclectic Light](https://eclecticlight.co/2025/01/06/power-modes-and-apple-silicon-gpus/); [bishal.io M1 Max](https://bishal.io/blog/six-local-models-m1-max-llama-cpp-vs-mlx/); [llama.cpp #4167](https://github.com/ggml-org/llama.cpp/discussions/4167) | No energy-per-token measurement of macOS power modes for LLMs, with or without phases. The NVIDIA decode-DVFS "free lunch" may *not* transfer to unified memory: community data show Low Power cutting decode more than prefill. Register two-sided (H1 NVIDIA analogue vs H2 UMA coupling). | Low Power on M3 Pro did not cap the GPU, so run a 10-minute M3 Max GPU-frequency pilot first. High Power changes neither clock nor SoC power on M4 Pro (fan only), so it is a rails null and a fan effect at DC; report it as descriptive. Sudoers: `powermode 1` refused, an Ed-physical change. Admission rules need a pack-local deviation. Release-after-switch suppresses the High Power mechanism. The 27B arm likely exceeds one night, so trim it. | 1 | 2 × 2 / 1 = 4 |
| 7 | **7. Rail share by phase + bits arm** | Survives, narrowed (2/2 not refuted) | [TokenPowerBench 2512.03024](https://arxiv.org/html/2512.03024); [Delavande et al. 2601.22362](https://arxiv.org/html/2601.22362v1); [Benazir & Lin 2508.08531](https://arxiv.org/abs/2508.08531) | Component-vs-machine share by phase is defined in TokenPowerBench but never reported. No per-phase 4- vs 8-bit energy on MLX. Sealed BYTES data already hold (c)-decode and (a) at p2048, so the 2 nights buy only the long-prompt regime. | (b) cannot meaningfully fail as banded: the coefficient is ±28% (≈±0.07 in ρ) against a ±0.05 band; derive the band or make (b) descriptive. A ≥12 s prefill needs 6k-20k tokens, so KV and chunked prefill confound the bits contrast and decode context. Fan power lives in rest (a sign confound for (a)). The τ ≈ 2.3 s edge sits at the largest power step. ρ clashes with BYTES' resident coefficient, so rename it. Runs take ≈11-13 h, tight for 2 nights. **Register stage A (mine BYTES after unblinding) before 12 Nov regardless.** | 2 (stage A: 0) | 2 × 2.5 / 2 = 2.5 |
| 8 | **5. Thermal sensitivity atlas** | Survives, partly anticipated (2/2 not refuted) | [Price et al. 1407.8116](https://arxiv.org/abs/1407.8116); [ContraCollective blog](https://contracollective.com/blog/apple-silicon-sustained-throughput-thermal-throttling-m4-m5-pro-m5-max-2026); [Notebookcheck M3 Max 16"](https://www.notebookcheck.net/Apple-MacBook-Pro-16-2023-M3-Max-Review-M3-Max-challenges-HX-CPUs-from-AMD-Intel.766414.0.html); [Tummalapalli 2603.23640](https://arxiv.org/abs/2603.23640) | No fixed-work energy-per-token β_T on Apple silicon or any laptop, and none at two boundaries on one unit. Best new angle: rail-vs-DC β_T with fan RPM regressed out, as a leakage/gain check of `powermetrics`. The 60-minute curve is anticipated: blog-level 4 h M5 Max curves exist, and Notebookcheck shows this chassis "completely stable". | The ≤0.05 %/°C bound is likely falsified (K20 fit gives 0.08-0.25 %/°C), so expect "gates stay". Power hinges on the hot-cold lever, so register a minimum ΔT_slow (≈25 °C). The heat-soaked arm will fail the `thermal_pressure='nominal'` admission rule and needs an exemption. DVFS mixes frequency into β_T, so record clocks. "DC β_T ≤ rail β_T" is fragile if fans stay at their floor, so replace it with a fan-regressed residual test. Cost is ≈2-3 nights, not 1-1.5. | 2.5 | 1.5 × 2 / 2.5 = 1.2 |
| 9 | **9. Context term across attention regimes + KV quant** | Partly anticipated (2/2 not refuted) | [Ma et al. 2605.11999](https://arxiv.org/abs/2605.11999); [Chkir et al. 2608.25096](https://arxiv.org/abs/2608.25096); [Mitra et al. 2507.12442](https://arxiv.org/html/2507.12442v3) | The ordering (GQA > GDN hybrid; hybrid prefill cheaper at 16-32K) is shown on H200 including BS=1. Still new: a quantitative bytes-read slope model, an active-matched MoE pair, the first sparse-indexer (QSA) energy, KV quantization by phase, and a direct feed of D's context × decode coefficient into the residual. | Hybrid prefill on pinned mlx-lm uses a sequential GDN kernel plus unfused hd256 attention, so label results by kernel path. The KV arm's prefill penalty is fixed by `quantized_kv_start = 0`, so add a fused-prefill arm. Flash-Next's slope is not ≈0 (indexer O(L/4)); use an absolute bound instead of a ratio. Adjacent hybrid levels sit near the floor, so pair extremes or use 512-1024 forced tokens. Qwen3-30B-A3B max_pos is 40,960, so cap the top cell. A thermal carry-over confound needs per-run cooldown. Cost is likely ≈4-6 nights. | 4 | 1.5 × 2 / 4 = 0.75 |
| 10 | **10. Speculative / MTP decoding energy** | **Headline refuted** (1 refuted, 1 not refuted but κ band contradicted) | [Dutta et al. 2602.09113](https://arxiv.org/abs/2602.09113); [Fernandez et al. 2504.17674](https://arxiv.org/abs/2504.17674); [mlx-lm #890](https://github.com/ml-explore/mlx-lm/discussions/890); [mlx-lm #990](https://github.com/ml-explore/mlx-lm/pull/990); [mlx-lm #1109](https://github.com/ml-explore/mlx-lm/pull/1109) | κ spans ≈−0.1 to +1.2 on CUDA, and our proposed Qwen3-8B/0.6B pair raised energy. Residual: the first DC-metered energy sign on Apple unified memory; rail-vs-DC κ (κ = 1 + ln(P_A/P_B)/ln(t_A/t_B)); the width of the "faster but more energy" band in acceptance length; native MTP energy (none published anywhere). | Pair 1 likely stays under the 1.2× gate, so κ cannot be estimated; use a 32B/70B target or K as the manipulated variable. Native MTP has no MLX path, `qwen3_next` strips `mtp.*`, and #1109 forbids speculation on ArraysCache, so this is multi-week build work (also an upstream candidate). Token identity is not guaranteed (batched-verify kernel ties), so pre-register a refusal-rate ceiling. κ noise is amplified about 5.5× at 1.2× speedup. L* is only a between-prompt regression. | 3+ (blocked) | 1 × 1.5 / 3 = 0.5 |

---

## 6. Experiment specifications (synthesis text, with check amendments)

Each block gives the synthesis's claim, rationale, design and cost unchanged, followed by **check amendments** to apply before registration.

### Idea 1. Instrument night: does powermetrics conserve energy, do IOReport counters beat it at phase edges, and where do the missing watts go

**Claim.** Five claims, each with its own falsifier.

- **(a)** At 100 ms cadence, `powermetrics` conserves energy. For commanded GPU pulses 10-1000 ms wide at varied phase, record power × support ÷ the KM003C's above-baseline DC energy is constant across widths within ±2%. A width-dependent deficit, like nvidia-smi's 25%-of-interval window, falsifies it.
- **(b)** Cumulative IOReport Energy Model counters read at the runtime's own phase stamps give a boundary-attribution term at least 5× smaller than the pulse-fit fiducial bound. A counter update period of 100 ms or more falsifies it.
- **(c)** Repeating the known-bytes rotate-vs-repeat probe, IOReport's `dram` channel reproduces the published rest coefficient (29.6 ± 8.4 pJ/B), and `dram` + `gpu_sram` explain at least 50% of the DC − rails gap during streaming kernels. Otherwise falsified.
- **(d)** A generation-length-1 request's energy minus one decode step equals the boundary-derived prefill allocation within the cell's attribution floor. This is the prospectus's boundary-free check.
- **(e)** Random 16 KiB `F_NOCACHE` reads from the internal SSD cost at least 0.33 nJ/bit at the DC boundary, at least 3× Kyung et al.'s modeled 110.8 pJ/b. Falsified below that.

**Why our rig.** Only this rig has all of the following at once:

- the in-window pulse detector;
- the rate-aware clock anchor;
- the KM003C plus battery term, time-anchored to the members;
- SMC PDTR/PSTR;
- a published known-bytes coefficient to check against.

Both 09-16 prospectus diagnostic arms are still unrun, and the experiment tests the paper's own stated applicability assumption (draft line 53). No published study validates `powermetrics`; Yang et al.'s nvidia-smi study is the template. IOReport gives `dram` and `gpu_sram` channels without root.

**Design.** A `DIAGNOSTIC_NO_PACK` window. No frozen pack is touched and no outcome-bearing data is produced, so it needs no blinding group. It can run by day if the quiet guards pass.

Segments:

1. The existing base-two varied-gap pulse schedule at widths {10, 20, 50, 100, 200, 1000} ms. `powermetrics` runs at {50, 100, 200} ms in separate captures, beside a 1 kHz IOReport poller (built on the Air first) and the KM003C with the SMC battery term.
2. Inference-like transitions: 59 repetitions of a 2 s matmul burst followed by 30 ms periodic kernels.
3. The known-bytes geometry (32 MiB, rotate vs repeat), plus 8 arithmetic-intensity levels × 60 s, run A/B/B/A on adjacent levels with a 180 s settle.
4. Generation-length-1 requests on Qwen3-1.7B/8B at the pinned prompt.
5. Internal-SSD random reads at QD1 and QD8 at 4 rates, plus sequential reads, on a 20 GB scratch file.

Estimands:

- r(width) = E_pm / E_DC, with a t-interval over at least 3 captures;
- the IOReport step period and the edge-displacement distribution per channel;
- an OLS fit of P_DC − P_rails on bandwidth, with FLOP rate as a second regressor;
- the IOReport-explained fraction;
- the d=1 closure residual against the floor;
- SSD J/bit, idle-subtracted, with the CPU-rail share separated.

Floor: capture-to-capture repeatability, with the KM003C clock-fit bound (10-17 ms) as a separate term. No new gates.

**Cost.** 1 Mac-night or one quiet day, plus about 0.5 Air-day for the IOReport reader.

**Check amendments.**

1. ML.ENERGY already reports sub-millisecond IOReport updates, so (b)'s update-period falsifier will pass trivially. Tighten it to the edge-displacement-to-fiducial-bound ratio.
2. Test (a) on train-level energy at 10-20 ms widths, with a fixed bytes/FLOP mix kernel. Use the IOReport GPU counter as a third witness to separate DVFS-ramp physics from sampling artefacts.
3. Cite Petar_M (forum 819927) and the HN video breakdown (GPU 133 W, DRAM 18 W, fabric 28 W; the video itself is unopened) in (c). Cite Ruf & Detyniecki in (d).
4. Check the MBP's macOS version and its channel list. On macOS 27, plan the AppleCLPC fallback.
5. Measure the self-load of the poller and of `powermetrics` at 50 ms.
6. Make (d) and (e) optional. (e)'s falsifier is weak, because a DC figure including SoC controller, fabric and syscalls will almost surely clear 3× a NAND-level model. Add Kyung (arXiv:2508.06978) to the bibliography.
7. Delete the scratch file within its segment, and check free space against the 40 GB disk guard.

### Idea 2. Agent energy at the machine boundary, from data we already record, plus two BYTES riders

**Claim.** For Qwen3.8-27B SHADE-Arena episodes on the M3 Max:

- (i) Unowned segments (harness, tool execution, inter-turn) hold less than 10% of gross DC-input episode energy. This is the reverse of the server finding that GPUs idle 54.5% of agent time. Seat 1's alternative, ≥25%, is registered as the rival.
- (ii) The rails' share of episode DC energy is below 0.85, so the GPU-rail ALIGN estimand misses at least 15% of machine energy. This is the laptop analogue of Luo et al.'s 41-45%.
- (iii) For every model BYTES can resolve, the decode/prefill per-token energy ratio is at most 30× at rails, against Wu et al.'s 335× (cached) and 115× (uncached) on GPUs at batch 1.

Each is falsified if its value lies outside the bound.

**Why our rig.**

- ALIGN windows already log SMC PDTR, PSTR and the battery term at 1 Hz, and print PSTR − rails as the "unassigned power residual".
- PDTR tracks the KM003C (0.955 × meter + 2.3 W, r = 0.9975).
- Turn-owned segment tiling is exact.
- The model family is Luo et al.'s.
- BYTES already holds the 2,048-token prefill phases for 10 models.

**Design.** No new collection. All lines are descriptive and registered before unblinding.

1. Per episode, on pilots 4-10 (if their SMC stream exists) and on W1, never the D held-out pool: integrate PDTR plus the battery term over the episode and over its owned and unowned segments. Report the unowned share, the episode ρ (rails ÷ DC) and the CPU-rail energy inside tool spans, with 90% window-clustered bootstrap intervals.
2. A BYTES rider, registered before stage-1 unblinding on 12 Nov: the per-model prefill/decode per-token ratio at rails. Unresolvable prefill cells print as refused. No DC split for prefill (τ ≈ 2.3 s).
3. Reasoning vs answer per-token decode energy with the context term held fixed. This is outcome-bearing for D, so it is computed only after D unblinding.

**Cost.** 0 (desk).

**Check amendments.**

1. Pilots 4-10 are Qwen3-30B-A3B (v3). Label pilot lines by model; 27B lines are W1-dependent. Confirm per pilot that PDTR, PSTR, B0AC and B0AV were journaled (a structure probe of custody dirs, done by the lead or magistrate).
2. (i): compute segment shares from the 10 Hz rails. Apply DC only to episode totals, with the unowned DC share by difference with an uncertainty. Restate the rival as an energy share: KAIST gives a time share. SHADE-Arena tools are in-process Python, so (i) partly reflects the benchmark.
3. (ii): register the numerator (rails = CPU+GPU+ANE vs GPU only) and the boundary (PDTR + battery vs PSTR vs KM003C). Report ρ with its load dependence rather than as a one-sided bound.
4. (iii): use Wu's 115× uncached as the comparator, name prefill length and context, and expect many small-model cells to be refused.
5. Rider (3) has low novelty: Luo already found per-token energy flat across thinking modes.
6. R0 found Qwen3.8-27B at about 11 nats/token on the SHADE prompt. Atypical W1 episodes could bias the unowned share toward zero.

### Idea 3. Two-channel physical audit of hidden reasoning tokens (ALIGN analysis rider)

**Claim.** The attack: strip H reasoning tokens from the log and inflate the logged prefill or context counts so the 5-term energy prediction matches measured energy. Against it:

- (a) the energy-only residual detects at about its false-positive rate;
- (b) a separately registered time-residual channel restores detection power to at least 0.8 at H = 1,024 on D.

Falsified if energy-only already reaches 0.8 against the matched attack, or if the time channel adds less than 0.2 power.

**Why our rig.**

- Seeded identical-work replays put us in Kimpson et al.'s re-execution threat model, where hidden compute falls from ≥0.41 to 0.059.
- We have exact token logs, turn timing and turn-owned energy.
- Model misfit (53-73 token-equivalents), not the instrument (about 10 tokens), limits detection, so the lever is channel design.
- Duration is deliberately kept out of the energy residual, which makes it an independent second detector.

**Design.** No new collection.

- Register before D held-out unblinding; run after registration-grade unblinding.
- Tamper D1-Dn benign and sabotage logs synthetically on the known-H grid {0, 128, 256, 512, 1024, 2048}, in three attack classes: strip only; strip plus prefill inflation; strip plus context inflation.
- Frozen leave-one-trajectory-out benign fits for energy and for time.
- Scores: energy-only, time-only, and a Bonferroni two-channel score.
- Estimands: detection curves and H50/H90 per attack class, from a window-cluster bootstrap (chair ruling 2).

**Cost.** 0.

**Check amendments.**

1. **Restate the lever.** An energy-matched prefill cover leaves a time residual of E_H × (1/P_decode − 1/P_prefill). With P_prefill/P_decode ≈ 1.8 here, H = 1,024 leaves roughly 10-25 s unexplained. Condition the power prediction on the ratio measured from the frozen benign fits.
2. **Add a fourth attack class:** the optimal mixed prefill + context inflation. It can null both channels whenever 1/P_dec lies between 1/P_pre and 1/P_ctx. Add the structural consistency channel (re-tokenisation; turn t+1 prompt = turn t context + outputs).
3. Context inflation likely matches time as well as energy (both memory-bound), and is bounded by the 40,960 cap. State that its H50 may come from a plausibility bound.
4. Take duration from the trusted trace (active-segment onset and offset), not harness timestamps. Stratify by thermal state or restrict to precheck-eligible members.
5. Statistics:
   - minimum empirical FPR ≈ 1/(m+1) ≈ 0.07 with m ≈ 12-14;
   - register a joint Mahalanobis score as the primary or secondary;
   - drop the "independent" wording, because the channels share thermal noise;
   - expect wide H90 with about 3 windows.
6. Check whether D logs predate the `ended_in_unclosed_reasoning` fix.
7. Explain why an energy/time audit matters when direct re-execution comparison of token counts is unavailable.

### Idea 4. SSD-tier conditional memory: Flash-Next's n-gram table resident vs page-cached vs uncached, with computation bitwise identical

**Claim.** With identical tokens and computation, serving the q4 n-gram table by uncached `F_NOCACHE` reads from the internal SSD, instead of from resident memory:

- raises DC-input energy per 4K prefill by at least 25%;
- raises energy per decode token by at most 10%;
- puts less than 10% of the excess in the GPU rail;
- produces an excess that scales with lookup stall time, not bytes read.

A warm page cache (mmap) is within the floor of resident. Falsified if the prefill excess is at or below the floor, or if the rails capture most of the excess.

**Why our rig.**

- 128 GB holds both the resident and the paged layout of one artifact.
- On unified memory the SSD is the only offload tier.
- The KM003C and PDTR see SSD and CPU power; the GPU rail does not.
- Our `NgramTable` already has mmap/`F_NOCACHE` modes and fault counters.
- All public implementations report latency only.

**Design.** One measurement build: a q4 n-gram table (mlx-vlm group-32 layout) plus 4-bit experts, about 100 GB internal; confirm with the fit probe.

Arms:

- A: resident;
- B: mmap, warm page cache;
- C: `pread` with `F_NOCACHE`;
- D (daytime only, secondary): C served from the external SN7100.

Request: a 4,096-token varied-n-gram prompt plus 256 greedy decode tokens.

Blocks:

- A vs C: 10 quads, randomized orientation;
- A vs B: 5 quads;
- A/A: 5 null quads.

Per-member token identity is the identical-work check. Estimands: ΔE_prefill and ΔE per decode token at DC + battery and at the rails, with covariates for lookups, faults, bytes, `mincore` residency and stall time. Its own blinding group with two-stage unblinding: open arm A, fix the stall-time prediction from idea 1's SSD J/bit, then open B and C.

Stage 2 (conditional): P10 expert streaming vs resident maxfit, as an energy-quality frontier against the L3 bf16 reference.

**Cost.** 1-1.5 Mac-nights after Flash-Next live validation and freeing internal disk; +1 day for the external arm; +1 night for the conditional streaming stage.

**Check amendments.**

1. Arm A needs a new resident path, the off-GPU numpy table. An in-MLX-tree resident table (about 97 GB) exceeds the wired limit. Consider locking only the about 65k touched rows (about 1 GB of pages); LPDDR refresh does not depend on content.
2. `F_NOCACHE` does not evict pages already in the buffer cache. Purge between members, check with a non-touching mmap and `mincore`, or keep a second table copy (+30 GB disk).
3. The serial QD1 `pread` loop confounds tier with submission strategy. Add a concurrent `pread` / `F_RDADVISE` arm, or pre-register C as a pessimistic serial bound. Re-time arm C on the Air with a synthetic full-size table (no weights needed).
4. Stall-vs-bytes needs leverage: vary I/O concurrency or prefetch, or use 2-3 prompts with different dedupe ratios.
5. Replace the fixed 25% bar with a stall-time-priced prediction. Excess fraction ≈ (P_stall/P_compute) × (t_stall/t_compute) ≈ 0.25 × 1.07 from mlx-vlm's figures, so the bar is borderline.
6. "Rails capture the excess" must name GPU only vs GPU+CPU, because the Python loop sits on the CPU rail.
7. Run A/A first to learn the token-identity refusal rate.
8. Arm D: the bus-powered enclosure adds bridge-chip load at DC, so give it its own idle baseline.
9. Stage 2 is a separate preregistration (bf16 experts about 240 GB; ExpertStream is unreviewed cloud output).

### Idea 5. Thermal sensitivity atlas, evidence-based gate relaxation, and the first sustained-load MacBook curve

**Claim.**

- At fixed work, rail-boundary decode energy per token changes by less than 0.05%/°C of slow-sensor temperature over R ± 3 °C. Then |β_T|90 × δ_slow < 0.1·s_r, and G1 and the holds can be relaxed without bias.
- At the DC boundary β_T is larger, because fan power enters.
- In 60 minutes of continuous Qwen3.8-27B decode on AC, throughput falls less than 5%, against 41.5% on an iPhone 16 Pro.

Falsified if |β_T|90 × δ_slow ≥ 0.1·s_r, if DC β_T ≤ rail β_T, or if the loss exceeds 5%.

**Why our rig.**

- The SMC die/heatsink classifier, G0 machinery, battery float and the KM003C/PDTR put fan power inside the boundary.
- R1's U5 measures β_T for D only.
- Ruling 1(f) "will probably bind on hardware".
- Tummalapalli et al. measured no MacBook.

**Design.**

- Designed start states (precooled; at R; heat-soaked after 20 minutes of load), reusing R1 machinery.
- A/B/B/A on (cold, hot) with identical seeded requests for Qwen3-1.7B, Qwen3-8B and Qwen3.8-27B 8-bit: 6 quads per model, plus 3 A/A nulls at R.
- β_T = dE/dT_slow at both boundaries, with the all-corner slope interval.
- One 60-minute sustained segment with battery float. Any relaxation goes in the deviation log.

**Cost.** 1-1.5 Mac-nights (checks: about 2-3).

**Check amendments.**

1. Expect the 0.05%/°C bound to be falsified: Price et al.'s K20 fit implies 0.08-0.25%/°C. Make the β_T atlas the deliverable, and accept "gates stay" as a likely outcome. Check against s_r first: relaxation needs s_r > 30·|β_T|.
2. Register a minimum hot-cold lever (ΔT_slow ≥ 25 °C) as an admission condition. Regress on in-window mean temperature, not arm labels. Split β_T into a power term and a time term (DVFS).
3. The heat-soaked arm will fail `thermal_pressure='nominal'` admission, so register an exemption.
4. Replace "DC β_T > rail β_T" with a fan-RPM-regressed residual test. Log fan RPM and pin the power mode.
5. Reframe the sustained curve as an energy-per-token-over-time curve at DC with float verified. Do not call it "first": blog-level MacBook curves exist, and Notebookcheck shows this exact chassis stable. Treat the iPhone figure as context only. Run 60 minutes as back-to-back seeded requests with KV reset.
6. Log ambient temperature as a covariate.
7. Consider 2 models (1.7B + 27B) to keep cost near 2 nights.

### Idea 6. The oversight tax: energy of AI-control monitors on SHADE-Arena transcripts

**Claim.**

- (i) An 8B monitor that re-reads the full transcript every turn costs at least 20% of the monitored 27B agent's episode energy.
- (ii) Prefix-cached incremental monitoring cuts that by at least 4×, with identical verdicts.
- (iii) An end-of-episode action-only monitor costs less than half of a CoT+action monitor.

Falsified if full re-read costs less than 10%, if caching saves less than 2×, or if action-only costs ≥0.5× CoT+action.

**Why our rig.**

- Agent and monitor run on the same machine.
- Monitoring is prefill-dominated.
- Prefix-cache machinery exists for both KVCache and hybrid ArraysCache models.
- 128 GB allows co-residence.
- No published work measures monitor energy.

**Design.**

- Inputs: pilot 4-10 and W1 transcripts as fixed inputs (D held-out only after unblinding).
- Monitors: Qwen3-8B 4-bit (primary) and Qwen3.8-27B 8-bit (secondary), greedy.
- Arms:
  - M1: per-turn full re-read;
  - M2: per-turn incremental with prefix cache;
  - M3: end of episode, CoT+actions;
  - M4: end of episode, actions only;
  - optional M5: extract-and-evaluate.
- Blocks: A/B/B/A on (M1, M2) and on (M3, M4), 10 transcripts each, plus 5 A/A nulls. Verdict identity is the M1/M2 identical-work check.
- Estimands: E_monitor / E_agent at rails and DC, E(M2)/E(M1) and E(M4)/E(M3). AUC is context only.
- Live co-resident variant: +1 night.

**Cost.** 1 Mac-night, +1 for the co-resident variant.

**Check amendments.**

1. Cite Control Tax (USD on SHADE-Arena, App. K) and Arike's USD frontier as the cost-basis predecessors. SHADE-Arena's own turn-by-turn monitor *is* M1.
2. Pre-register the token-arithmetic predictions for (ii) and (iii) from transcripts. Make the headline estimand the measured energy ratio ÷ token ratio (the long-context attention term), plus co-resident interference. Report E_monitor/E_agent per agent model (30B-A3B pilots vs 27B W1), not pooled.
3. Keep monitor thinking off with a short score, or score from logits.
4. Define identity on the parsed score and log logit drift.
5. Render the transcript as a single user text so the Qwen3 template does not strip prior reasoning.
6. M4 (`actions_only`) keeps tool results, so check token shares first.
7. The 27B secondary monitor goes to M3/M4 only, or gets its own night.
8. Co-resident interference is recoverable only as E(both) − E(agent alone) − E(monitor alone) with replayed inputs.
9. Pilot transcripts sit under `night-*` custody, so only the lead or magistrate assembles them.

### Idea 7. Rail share by phase (the prefill extension of BYTES), with a bits arm

**Claim.**

- (a) The rails' share of the machine's extra energy is higher in prefill than in decode: ρ_prefill − ρ_decode > floor.
- (b) Decode ρ is predicted within ±0.05 by the published known-bytes coefficients plus a conversion term from idea 1.
- (c) On Qwen3-8B, decode energy per token falls at least 35% from 8-bit to 4-bit, while prefill energy per token falls less than 10% or rises.

Each is falsified by the opposite sign or a miss larger than its band.

**Why our rig.** No other Apple-silicon rig has an inline DC meter plus the battery term time-anchored to the rail sampler. BYTES covers decode at three boundaries, but only at a 2,048-token prompt. The known-bytes test gives an independent predictor.

**Design.**

- Cells: Qwen3-8B 4-bit and 8-bit, Qwen3-30B-A3B 4-bit, Qwen3.8-27B 8-bit. The prompt length per model gives prefill ≥12 s (≥5τ), plus 1,024 forced decode tokens.
- Blocks: 10 absolute repeats plus 10 null quads per cell, orientation randomized. The bits contrast adds 8 quads of 8-bit vs 4-bit.
- Code change: phase-level `meter_joins`.
- Estimands: ρ per phase at DC + battery, Δρ, and per-phase energy-per-token ratios for bits.
- Predictions registered before BYTES stage 1 (12 Nov).

**Cost.** 2 Mac-nights, after idea 1.

**Check amendments.**

1. **Stage A at zero Mac cost:** BYTES' sealed data already hold (c)-decode (Qwen3-8B 8-bit vs 4-bit) and 2,048-token prefill energy at both boundaries. Register (a) and (c) at p2048 as post-unblinding analyses before 12 Nov. The Mac-nights then buy only the long-prompt regime.
2. (b): the coefficient's ±28% half-width alone gives ≈±0.07 in ρ. It is a rotate-minus-repeat contrast measured in a latency-bound regime, which the slot fill names as a transfer limit, and it partly duplicates BYTES H2's ε_rest. Derive the band from δ, or make (b) descriptive.
3. Hold prompt length fixed across the bits pair. Recompute the KV bytes read per decode token at long context (Qwen3-8B KV ≈147 KB/token, so ≈1.5 GB/step at 10k). Consider a matched-context decode arm at 2,048.
4. Log fan RPM: fan power in rest pushes ρ_prefill down, the opposite sign to (a).
5. Assign the battery edge conservatively at the prefill→decode step, the largest power step in the run.
6. Rename ρ, which clashes with BYTES' resident-bytes coefficient.
7. Add the IOReport DRAM channel as a third boundary (pre-qualify on the Air).

### Idea 8. DVFS policy energy by phase: Low Power vs Automatic vs High Power mode

**Claim.** In memory-bound decode:

- High Power raises energy per token ≥3% for <2% speed gain;
- Low Power cuts energy per token ≥10% for <15% throughput loss.

In compute-bound prefill the ordering reverses. Falsified by opposite signs in decode.

**Why our rig.**

- R1 already runs a High Power A-B-A.
- The powermode restore trap, per-bundle record and arm refusal exist.
- Phase-resolved energy separates the decode and prefill predictions.
- No published Apple power-mode LLM measurement exists.

**Design.**

- Free first step: read Auto vs High Power rails energy per decode token from R1's A-B-A legs.
- Arms: {LP, Auto, HP}, in quads Auto/HP/HP/Auto and Auto/LP/LP/Auto with a G0-style release after every switch. 8 quads per pair per model, plus Auto/Auto nulls.
- Models: Qwen3-8B 4-bit and Qwen3.8-27B 8-bit, 8k prompt, 512 decode tokens.
- Prerequisites: a sudoers extension for Low Power Mode and a pack-local deviation from the `low_power_mode=false` admission rule.

**Cost.** 1 Mac-night.

**Check amendments.**

1. Run a 10-minute M3 Max GPU-frequency pilot (Auto vs LP) first. Oakley: LP capped the GPU on M4 Pro, but there was "no change in GPU frequency or power use" on M3 Pro.
2. **Register two-sided:**
   - H1, the NVIDIA analogue: decode tolerant, prefill hurt;
   - H2, unified-memory coupling: decode loses more than prefill.

   Community data: llama.cpp #4167 LPM tg −28% to −39% vs pp −22% to −27%; M1 Max and M5 Max dense decode about −50% under LP.
3. High Power changes neither clock nor SoC power on M4 Pro. Report it descriptively per boundary: rails null, fan watts at DC. The release-after-switch design suppresses High Power's only mechanism; add a warm-start arm if it matters.
4. Sudoers `powermode 1` was tested and refused, so this is an Ed-physical change. Invert the arm refusal per leg rather than bypassing it.
5. Read back `pmset -g` after each switch, and record GPU frequency residency.
6. Model leg position, because LP legs cool the chassis.
7. Trim the 27B to 4 quads per pair, or drop its LP arm.
8. Fix the DC power path (USB-C through the KM003C) and the charge state across all arms.

### Idea 9. The context term across attention regimes: full GQA vs Gated-DeltaNet hybrid vs hybrid with sparse QSA, plus quantized KV

**Claim.**

- Decode energy per token rises with context, and the slopes order full-GQA MoE (Qwen3-30B-A3B) > DeltaNet hybrids (Qwen3-Next-80B-A3B, Qwen3.8-27B) > Flash-Next.
- Flash-Next's slope is ≈0 beyond its sparse-decode dispatch threshold (8,192 KV in our port).
- Slope ratios match the ratios of KV-plus-state bytes read per token within 25%.
- Hybrid prefill energy per prompt token is sub-linear in context.
- KV arm (30B-A3B, 16k-32k): a quantized KV cache raises prefill energy >20% and lowers decode energy per token <10%.

Falsified if Flash-Next's slope is ≥ half the 27B's, if the bytes model misses by >25%, or if the KV signs reverse.

**Why our rig.**

- No batch-1 unified-memory numbers exist.
- 128 GB holds 32k-40k contexts for all three regimes.
- The 30B-A3B and Next-80B are an active-matched MoE pair already on disk.
- Qwen3.8-27B is the ALIGN D model.
- Our port has the QSA kernel.

**Design.**

- Cells: each model × context {2k, 8k, 16k, 32k, 40k}, with 256 forced decode tokens and thinking off.
- Blocks: A/B/B/A on adjacent context levels, 6 per pair, plus 6 null quads at 2k and at 32k.
- KV arm: fp16 vs 8-bit vs 4-bit KV at 16k and 32k on 30B-A3B, 6 quads per cell.
- Estimands: OLS slope with the all-corner interval and a curvature check; E_prefill per prompt token vs context; KV energy ratios per phase.
- The Flash-Next stage runs later on idea 4's q4 build, table resident.

**Cost.** 2 Mac-nights, +0.5 for the KV arm, +1 for the Flash-Next stage (checks: likely about 4-6 in total).

**Check amendments.**

1. Do not present the ordering as the result; Ma et al. show it on H200 including BS=1. The novelty is the quantitative bytes model, the matched MoE pair, QSA energy, KV quantization by phase and D's coefficient for the residual.
2. Label hybrid prefill results by kernel path: sequential GDN kernel plus unfused hd256 attention on pinned mlx-lm. Optionally measure before and after a chunked GDN kernel, which is an upstream deliverable.
3. KV arm: `quantized_kv_start = 0` switches every chunk after the first to the unfused path. Add an arm with `quantized_kv_start` = prompt length (fused prefill, quantized decode). Note that the bytes model predicts about a 40% decode-byte cut at 32k on 30B-A3B, which contradicts "<10%"; register which hypothesis is meant. Plan for the score-matrix memory spike (≈4 GiB per layer-chunk).
4. Flash-Next: the indexer scores all L/ratio pooled keys each step, so the slope is small, not zero. Use an absolute bound in J per 1k context tokens. The 8,192 kink is our dispatch policy (an M4 latency crossover), not the architecture. Flash-Next may also be dispatch-bound (≈4,100 kernels per step).
5. Order is 30B (96 KiB/token) > 27B (≈64 KiB/token, unverified) > Next (24 KiB/token + ≈75 MB state) > Flash-Next.
6. Pair extreme levels for hybrids or use 512-1024 forced tokens.
7. Cap the top cell at ≈40,448 (30B-A3B max_pos 40,960).
8. Cool down per run against thermal carry-over.
9. Run a timing pilot for Next-80B 40k prefill.
10. ArraysCache has no `to_quantized`, so the KV arm stays on 30B-A3B.

### Idea 10. Speculative and MTP decoding energy with outputs held token-identical

**Claim (refuted as a law; see verdict).** With greedy verification, κ = ln(E_A/E_B) / ln(t_A/t_B) satisfies 0.7 ≤ κ < 1. Below an acceptance-length break-even L*, speculative decoding raises energy per output token. κ is estimated only where speedup ≥1.2×.

**Why our rig.** Greedy speculative decoding is lossless, so the arms do identical work. MLX verification is not free (best EAGLE-3 1.05×, mlx-lm #890). We have 100 ms rails, the DC meter and phase floors, against CodeCarbon at 1 s on CUDA.

**Design.**

- A = target alone; B = target plus drafter.
- Pairs: Qwen3-8B 4-bit with a small drafter (mlx-lm draft-model path wrapped for per-round observability), and Qwen3.8-27B 8-bit with native MTP once stack B exposes it.
- 10 A/B/B/A quads per model across code, prose and structured prompts, plus 5 A/A nulls. Token identity is checked per member.
- Estimands: decode energy per output token at rails and DC, accepted length, κ, L*.

**Cost.** 2 Mac-nights plus 1 stack-B qualification day, after the bridging window (checks: blocked; multi-week build for MTP).

**Check amendments.**

1. Drop the universal κ band. Dutta et al. measured κ from about −0.1 to +1.2, and the exact Qwen3-8B/0.6B pair raised energy at ≤1.19× speedup.
2. Pre-register instead:
   - the sign and magnitude of the energy ratio on MLX;
   - rail κ vs DC κ (static platform power pushes DC κ toward 1);
   - the width of the κ < 0 band in acceptance length;
   - optionally, a 32B/70B 4-bit target, to test Dutta's "larger gap saves more".
3. Per-round observability needs only a thin wrapper over `from_draft`, not a fork.
4. Native MTP is blocked: there is no MLX generation path, `qwen3_next`/`qwen3_5` strip `mtp.*`, #990 is stalled, and since #1109 speculation raises on ArraysCache. An MTP head plus recurrent-state rollback is multi-week work, but also an upstream candidate.
5. Pre-register a token-identity refusal-rate ceiling, or truncate at first divergence.
6. κ noise is ≈5.5× the energy-ratio noise at 1.2×, so pre-specify a minimum |ln t ratio|.
7. Treat L* as exploratory: it can only come from a between-prompt regression.

---

## Appendix A. Seat 1 report (Fable), verbatim

# Our methodology against the literature: new experiments for the measurement Mac

Fable seat, research track 2026-11-07. Sources: `origin/main` at `ca2d1ee97` (README, `configs/campaigns/v5_claim_25g83/registration_block5.md`, `docs/analysis/b5/DEVIATION-LOG.md`, `CANONICAL.md`, `docs/glossary_measurement_terms.md`, `docs/paper/draft-v1.md` §8, run reports of 2026-07/08 and 2026-11), `docs/align/pilot_protocol_v4.md` and the thermal/SMC/energy-residual docs on `lane/2026-11-06-v4-r1-integrated`, the council FINAL-DESIGN, and the Flash-Next port docs on `lane/2026-11-06-qwen4exp-port-r2`, `lane/2026-11-05-qwen4exp-port-perf` and `lane/2026-11-07-qwen4exp-mbp-live`. Every external source cited below was opened (abstract page or full text) unless marked UNVERIFIED. Nothing under `jw-b5-*`, `night-*`, `night-custody`, `night-archive` or `restricted/` was opened; no model weights were loaded; no worktree was created; no commit was made.

## 0. What our method is, in one paragraph

Block 5 measures gross processor-rail energy (`powermetrics` CPU+GPU+ANE, one ~130 ms interval-average record per requested 100 ms) of one model execution per run, split into prefill and decode by overlap integration, with a per-cell attribution floor that propagates calibrated phase-edge timing bounds (commanded GPU pulses, a bracketed pre/post calibration, a ≤5 ms clock bound) through the energy integral; a detection floor from 10 absolute repeats and 10 null A/B/B/A quads per cell; a reference workload (18-member NEG-8 corpus plus start/mid/end triplets) for drift; idle admission (p95 CPU busy ≤0.5, p95 processor power ≤1 W), battery float, clock-frequency and agent-census hazards at the arm; a KM003C inline USB-C meter at the DC input (50 Hz) plus the SMC battery term as a recorded whole-machine diagnostic; sealed registration, structure-only harvests during the block, a release event, an independent standard-library recompute compared leaf by leaf against the heavy pipeline within blind-fixed bars, and a public deviation log. ALIGN v4 adds, for SHADE-Arena agent episodes, a 1 Hz SMC thermal sidecar with a model-free sensor classifier, a start gate G0 and per-turn gate G1 referenced to the episode's own start, decode holds for heavy cells, turn-owned GPU-rail energy beside gross energy, a five-term energy residual detector, and a token-identical ABBA/BAAB contrast deciding whether per-turn gates stay.

## 1. Where we are stronger and weaker than standard practice

### 1.1 Stronger

| Dimension | Standard practice (source) | Ours |
|---|---|---|
| Phase-edge timing | Hähnel et al. (RAPL short code paths) and Dauner et al. (sampling-frequency effects) are the only close ancestors; ML.ENERGY (Chung et al., NeurIPS D&B 2025, [arXiv:2505.06371](https://arxiv.org/abs/2505.06371)) and MLPerf Power (Tschand et al., HPCA 2025, [arXiv:2410.12032](https://arxiv.org/abs/2410.12032)) report whole-run energy; TokenPowerBench and Ruf & Detyniecki split phases without an error budget (paper draft §8). | In-window pulse calibration, bracketed bounds, a per-cell attribution floor that gates the claim. No published LLM energy study does this. |
| Preregistration and blinding | Registered-report tracks exist in software engineering (ESEM, ICSME 2025, MSR 2026/2027 calls, [MSR 2026](https://2026.msrconf.org/track/msr-2026-registered-reports)) but not in systems/architecture venues; the paired-MDE preregistration of Zhuang et al. (paper ref 26) is the only energy-adjacent analog. MLPerf Power standardises rules, not blinding. | Sealed hash-pinned registration, structure-only harvests, release event, independent recompute with blind-fixed bars, a deviation log. Stronger than anything in the surveyed literature. |
| Repetition and variance | Typical LLM energy papers use 3 repetitions and report "modest" variability (Zähl et al., [arXiv:2608.00008](https://arxiv.org/abs/2608.00008)), or 10 repeats and a CoV (Zine et al., [arXiv:2607.09172](https://arxiv.org/abs/2607.09172), ~9,000 runs). Maricq et al. (OSDI '18, [usenix](https://www.usenix.org/conference/osdi18/presentation/maricq)) showed from 900k data points on 835 servers that identical hardware differs run to run and server to server. | 20 units per cell split into repeats and null quads, a detection floor per cell, reference drift members, and the explicit "independence is a modelling assumption" caveat. |
| Environment and hazards | MLPerf Power: SPEC-approved analyzer, 60 s minimum collection, whole-SoC boundary, mobile/battery devices "a future goal" (Tschand et al. §III-A, IV-D). Most LLM papers state a warm-up prompt and nothing else. | Clock-frequency gate (|f| ≤ 3.63 ppm), boot-session check, idle admission, battery float with the SMC battery term, agent census, thermal state, Spotlight and update pauses, an external-volume refusal. We treat the battery that MLPerf declines to handle. |
| Thermal control | Tummalapalli et al. ([arXiv:2603.23640](https://arxiv.org/abs/2603.23640)) and Ma et al. (PPAM 2026, [arXiv:2605.11999](https://arxiv.org/abs/2605.11999)) treat throttling as a finding; no one controls it as a nuisance at matched tokens. | G0/G1/holds referenced to a window-local idle state, a model-free SMC classifier (die vs heatsink class, t63, τc), designed start states in R1 to estimate β_T. Unique. |
| Whole-machine term | GPU-only telemetry misses 41-45% of system energy on an agent workload (Luo et al., [arXiv:2609.29707](https://arxiv.org/abs/2609.29707)); CodeCarbon-class estimators err by up to 40% against a wall meter (Fischer, [arXiv:2509.22092](https://arxiv.org/abs/2509.22092)); GreenBench on an M4 Pro reports 0.47 W package power and *assumes* 8-12 W system power (Kannan et al., [arXiv:2608.28667](https://arxiv.org/abs/2608.28667)). | An inline DC meter at 50 Hz plus the SMC battery term, time-anchored to the members' clock, with ρ = ΔE_rail/ΔE_machine per member (registration §5.8). Nobody else on Apple silicon has this. |
| Agent energy attribution | A-LEMS proposes energy per successful goal and finds orchestration, not per-call cost, drives overhead (Panigrahy et al., [arXiv:2605.22883](https://arxiv.org/abs/2605.22883)); KAIST's HPCA 2026 study reports 136.6× energy per query for a 70B agent vs one-shot QA and GPUs idle up to 54.5% of the time in tool phases ([KAIST EE page](https://ee.kaist.ac.kr/en/research-achieve/professor-minsoo-rhus-team-first-reveal-the-hidden-power-cost-of-ai-agents/), paper [arXiv:2506.04301](https://arxiv.org/abs/2506.04301)). | Turn-owned vs unowned segments, prefill/decode/tool per turn, gross printed beside owned, and a residual detector with calibrated false-positive rates. Finer attribution than any agent-energy paper. |

### 1.2 Weaker, or simply narrower

1. **Claim boundary excludes memory.** Our registered number is the CPU+GPU+ANE rail. On unified memory, decode is bandwidth-bound (the port's own perf notes: 5.8 GB/token weight traffic), so DRAM and fabric energy, which the rail excludes, is plausibly the dominant decode cost. MLPerf's boundary is the whole SoC "including any peripherals that cannot be powered down" (Tschand et al. §IV-A); GreenBench's package-vs-system gap (0.47 W vs 8-12 W) is the same problem seen from the other side. Our ρ term exists but is request-level only, diagnostic, and never phase-resolved (registration §5.8: "phase-level figures are not produced in block 5").
2. **Gain is unvalidated.** The paper draft says so (§7, §8). Khan et al. and Jay et al. validate RAPL gain against wall power; no public study validates `powermetrics` gain on any M-series chip (my search found forum anecdotes only: an M1 reading 48 W package against 92 W at the wall, undocumented). The KM003C can test rail-vs-DC *dynamic* gain but not the rail's own absolute accuracy; a sealed physical model would require Apple's rail map, which does not exist publicly.
3. **Short measured intervals.** Block 3's measured requests were 11-23 s; MLPerf requires 60 s of power data and loops the workload to get it (§IV-A). Our floors make short phases honest, but a reader used to MLPerf will see the prefill cell (≥3 records of ~130 ms) as thin.
4. **Workload realism.** One 42-token prompt, batch 1, a fresh process per member. Fernandez et al. ([arXiv:2504.17674](https://arxiv.org/abs/2504.17674)) show optimisation effects depend on workload geometry; Vellaisamy et al. (IISWC 2026, [arXiv:2608.28044](https://arxiv.org/abs/2608.28044)) show token-normalised energy can fall while request energy rises. Our estimand is clean but its external validity is small; the ALIGN episodes are the realistic workload and they are GPU-rail only.
5. **One physical unit, one stack.** Maricq et al. is the standing objection; SiliconBench ([NeurIPS 2026](https://neurips.cc/virtual/2026/poster/139658)) found an upstream library update broke three of ten Apple-silicon stacks, which is exactly the "stack as instrument" risk the GOAL's bridging-window idea addresses but which we have never measured.
6. **Gating makes reference-state energy, not production energy.** The protocol says so itself (v4: "ordinary production agents do not make these pauses"). The literature's throughput-collapse results (iPhone 16 Pro halves within two iterations; Tummalapalli et al.) mean our gated numbers are a lower bound on a real sustained agent's energy per token, and we have no ungated comparison cell.
7. **Proportionality.** Set against 3-repeat, CoV-reporting practice, our custody and arm machinery is far heavier than the field's, while the two things the field would ask first (gain validation and a memory-inclusive boundary) are the ones we do not have. That supports the 11-06 "proportionate care" direction: keep blinding and prereg fidelity, spend the next engineering on ρ and the boundary rather than on more guards.

## 2. Claims in the literature our rig could test or overturn

1. **"Speedup is not energy saving" for speculative decoding.** Dutta et al. (EACL Findings 2026, [arXiv:2602.09113](https://arxiv.org/html/2602.09113)): on an A5000 with CodeCarbon at 1 s sampling, vanilla decoding was sometimes more energy-efficient than CoGA/DyGA, Qwen3 models showed little saving, Llama-70B used *more* energy with SD. At batch 1 on unified memory the arithmetic is different (verifying k tokens costs about the same weight bytes as one), and Qwen3.8 ships an MTP head. Our phase floors and token-identical greedy pairs can settle this for the local regime.
2. **"SSD offloading of MoE weights is harmful for energy" (up to ~12× per token vs HBM).** Kyung, Yun and Ahn (IEEE CAL, [arXiv:2508.06978](https://arxiv.org/abs/2508.06978)) is a quantitative analysis for datacenter parts; FlashMoE ([arXiv:2601.17063](https://arxiv.org/abs/2601.17063)) measures only latency and hit rate on a desktop. Flash-Next pages a 51B n-gram table (and, as a stretch, experts) from an external SSD on a consumer machine; the enclosure is bus-powered from the Mac, so the KM003C sees its draw. No one has measured this.
3. **"Per-token energy is unchanged by thinking; only token volume changes."** Luo et al. report <1% per-token difference thinking on/off on Blackwell GPUs with Qwen3.8-27B. We run the same model family at batch 1 and can test whether the result holds when the KV cache grows across 4k-token reasoning turns on a bandwidth-bound device (the ALIGN residual's context × decode term predicts it should not).
4. **"Hybrid recurrent architectures have no prefill penalty and flat decode energy with context."** Ma et al. (H200, large batch) and Chkir et al. ([arXiv:2608.25096](https://arxiv.org/abs/2608.25096): MHA steep, GQA+SWA near constant; no hybrid tested). Qwen3-Next-80B-A3B (3 GDN : 1 attention; design paper [arXiv:2608.30320](https://arxiv.org/abs/2608.30320)) and Qwen3-30B-A3B (full GQA) are both on disk; nobody has batch-1 unified-memory numbers.
5. **"GPU-only telemetry misses 41-45% of agent energy" and "GPUs idle 54.5% of agent time."** On a laptop the tool runs on the same CPU rail, so "idle" is CPU work. Our rail split plus the DC meter quantifies the laptop version of both claims.
6. **Monitoring cost.** Arike et al. ([arXiv:2601.21112](https://arxiv.org/abs/2601.21112)) place filtering monitors on a cost-performance Pareto frontier, where cost is API price; SHADE-Arena (Kutasov et al., [arXiv:2506.15740](https://arxiv.org/abs/2506.15740)) reports AUC only. No one has measured the energy of oversight. A local monitor on our rig makes the "oversight tax" a joule quantity.
7. **"Quantizing the KV cache costs on-device agents context"** (Huang & Niu, NeurIPS 2026 SLM-Agents workshop, [neurips.cc](https://neurips.cc/virtual/2026/171195)): on mlx-lm the fused kernel rejects quantized caches, prefill materialises a 256 KiB/token score matrix against a 92 KiB/token cache saving. That memory result predicts an energy sign flip (prefill up, decode down) that our phase split can see.
8. **"Lower precision is not always faster on Apple silicon"** (Benazir & Lin, [arXiv:2508.08531](https://arxiv.org/abs/2508.08531): dequantisation overhead; M2 Ultra/Max, M4 Pro; no energy). Energy per phase versus bit-width is the missing experiment.
9. **"Package power approximates machine energy on Apple silicon."** GreenBench's 30-40× efficiency claim against datacenter GPUs rests on an assumed system power. Our ρ, phase-resolved and across models, is the first direct measurement and could overturn the assumption.
10. **"Batching is the main lever"** (87% per-token reduction, Chkir; 3.2× system efficiency, Luo; 6.3× at short context, Vellaisamy). All datacenter. At batch 1 on a laptop the idle floor is ~0.3 W, so amortisation is tiny for the machine but may be large for the GPU rail; the AXI-SB B=2/4 Metal probes already proved feasibility. Relevant to local multi-agent scheduling (parallel sub-agents, parallel monitors).

## 3. Flash-Next (qwen4_exp): what is achievable, and what can be upstreamed

**Verified upstream state (2026-11-07).**
- [mlx-lm PR #1788](https://github.com/ml-explore/mlx-lm/pull/1788): open since 2026-08-26, retitled "Add Qwen3.8-Flash-Next (qwen4_exp) support", one community approval, maintainer comment that it is large and will take time, label "await verification". Review threads: RMSNorm `+1` folded at load (done), n-gram hash seed defaulted to 0 instead of 1234 (fixed with a load-time constants check), `test_qwen4_exp` failing for one reporter at head on a prefill-vs-stepwise tolerance that the author cannot reproduce (unresolved), community quantized checkpoints failing on shard names and per-layer quant keys, MTP and vision dropped, author's verification peak ~111 GB on an M3 Ultra, 128 GB users running with expert offload. Related [issue #1924](https://github.com/ml-explore/mlx-lm/issues/1924) (per-module quantization map inert after `sanitize` renames) is open; PR #1482 removed the silent fallback.
- mlx-lm `main` has `qwen3_next.py` built on the `gated_delta` kernel and drops `mtp.` weights ([raw file](https://raw.githubusercontent.com/ml-explore/mlx-lm/main/mlx_lm/models/qwen3_next.py)); no `qwen4_exp.py` on main.
- mlx-lm [CONTRIBUTING](https://github.com/ml-explore/mlx-lm/blob/main/CONTRIBUTING.md): tests must fail on main; `new_model.md` template; model file named after `model_type`; LoRA entry in `tuner/utils.py`; a `tests/test_models.py` entry; benchmark main vs branch if performance is affected; AI-generated code allowed with disclosure and full understanding; **AI-written PR descriptions, issues and replies are prohibited** (so Ed writes every upstream text).
- mlx-vlm: the Blaizzy URL now resolves to `Neywa-Labs/mlx-vlm`; `mlx_vlm/models/qwen4_exp/` exists with `language.py`, `ple_storage.py`, `qsa_kernel.py`, `fp8.py`, a README noting the 360 GB bf16 checkpoint and group size 32 for PLE quantisation; the top-level README does not list Flash-Next.
- llama.cpp [PR #27742](https://github.com/ggml-org/llama.cpp/pull/27742) merged 2026-08-27: host-side n-gram hashing, the 97.7 GiB table written straight to an mmap'd file, q4_1 table 30.5 GiB.
- Ours (`canonical.md`, `perf.md`, `port_r2_adoption.md`, `mbp_live.md`): one module, fp32 gold parity ≤1e-5 on every scenario, bf16 within the reference's own noise, 31 tests, snapshot/restore and prompt-cache round trips bitwise; a block-sparse prefill Metal kernel for QSA (3.4× dense at 16k, flat to 40k), fused `gate_up_proj` through `gather_qmm`, a paged `NgramTable` (mmap or `F_NOCACHE` pread, dedupe, fault counters); maxfit profile 6-bit experts, all else bf16, 112.7 GB peak against the 115.4 GB working set, bf16 table (102.4 GB) on disk; M3 Max targets ≥30 tok/s decode and ≥400 tok/s prefill, measured so far only on the M4 Air; Saturday live validation on the borrowed SN7100 (DRAM-less, no HMB through the USB4 bridge, so random-read latency for PLE gathers is the named risk).

**What is achievable.**
1. A validated, pinned, measurement-grade port on our stack: already most of the way (gold parity, differential, converter, memory model). The remaining risk is physical: the 2.7 GB margin under the wired limit with a ≤21.5 GB evictable page cache competing in the same unified memory, and PLE gather latency over USB4. Both are measurable Saturday; the pre-committed fallback (maxfit5, 97.6 GB) is right.
2. Findings worth upstreaming regardless of which PR lands, because each is a correctness fact with a reproducible test: fp32 router ranking (bf16 ties are common at scale: 8 of 54 rows at layer 2), fp32 rounded-once sigmoid/silu at the reference's sites, the PLE gate divisor (sqrt(2560) rounds to 50.5 in bf16 and moves 36% of gate values), HF-exact bf16 RoPE in the indexer, the deterministic QSA tie rule, the n-gram hash-buffer check at load, the `+1` norm fold, and the left-padded-batch QSA selection bug (mlx-vlm audit D1) and bf16 router/gating findings (P1, P2). The unresolved prefill-vs-stepwise flake on #1788 looks like exactly the tie/rounding class we characterised; a deterministic explanation plus a test is the most valuable single contribution to that PR.
3. Model-agnostic pieces that can go to mlx-lm as their own small PRs, which is how maintainers prefer large models to arrive: the paged n-gram table storage (compare with mlx-vlm's `ple_storage.py` first and upstream to whichever lacks it), the head_dim-256 block-sparse prefill kernel (check whether MLX ≥0.32 added a fused prefill SDPA at head_dim 256 before offering it), and the #1924 diagnostic (warn/raise when a quant map matches no module, with matched/total counts).
4. A quality artifact nobody has published: measured 6-bit-expert vs bf16 gap on real weights, per layer and end to end (NLL, top-k agreement), and the same against the llama.cpp GGUF as a third reference.

**What is not realistic.** A competing full-model PR to mlx-lm; maintainers already have #1788 and will not review two. The route is contributions onto #1788's branch and separate component PRs, with Ed authoring all prose. Our module also targets mlx-lm 0.31.3; upstream main is 0.32.x, so any upstream piece needs an API port (the GOAL's bridging-window plan already covers the measurement side of that upgrade).

## 4. New experiments

Ten experiments are in `ideas`. A Mac-night is one unattended window (≤44,640 s, about 12.4 h) plus its daytime prep. The ones that need the external SSD mounted (idea 2) conflict with council ruling 20 (no external volume during windows) and are therefore daytime, DC-boundary studies or need an amendment; the SSD study on the pilot-10 lane already drafted that amendment. Common design conventions: forced-token (teacher-forced) decode wherever two arms would otherwise emit different tokens, so the work is identical except for the treatment; A/B/B/A quads for every two-arm contrast; null quads of each arm for the detection floor; the request-level and, once implemented, phase-level ρ from the KM003C beside every rail number.

Priority order by novelty per night: (1) rail share ρ across phases, (2) the SSD paging tax, (5) the oversight tax, (4) speculative/MTP energy at batch 1, (3) hybrid-attention flatness, then the rest.

## 5. Sources opened

MLPerf Power [arXiv:2410.12032](https://arxiv.org/abs/2410.12032) (abstract and HTML §III-IV); ML.ENERGY [arXiv:2505.06371](https://arxiv.org/abs/2505.06371); Zeus NSDI '23 [usenix](https://www.usenix.org/conference/nsdi23/presentation/you); Maricq et al. OSDI '18 [usenix](https://www.usenix.org/conference/osdi18/presentation/maricq); Fischer, CodeCarbon ground-truthing [arXiv:2509.22092](https://arxiv.org/abs/2509.22092); Dutta et al., speculative decoding energy [arXiv:2602.09113](https://arxiv.org/html/2602.09113); Kyung et al., SSD MoE offloading [arXiv:2508.06978](https://arxiv.org/abs/2508.06978); FlashMoE [arXiv:2601.17063](https://arxiv.org/abs/2601.17063); SHADE-Arena [arXiv:2506.15740](https://arxiv.org/abs/2506.15740); Arike et al., monitor information access [arXiv:2601.21112](https://arxiv.org/abs/2601.21112); GreenBench [arXiv:2608.28667](https://arxiv.org/abs/2608.28667); Tummalapalli et al., edge sustained load [arXiv:2603.23640](https://arxiv.org/abs/2603.23640); A-LEMS [arXiv:2605.22883](https://arxiv.org/abs/2605.22883); Krupp et al., web agents (AAAI 2026 AISI) [arXiv:2511.04481](https://arxiv.org/abs/2511.04481); Luo et al., Blackwell agent profiling [arXiv:2609.29707](https://arxiv.org/abs/2609.29707); Jin, Wei, Brooks, energy cost of reasoning [arXiv:2505.14733](https://arxiv.org/abs/2505.14733); Fernandez et al. [arXiv:2504.17674](https://arxiv.org/abs/2504.17674); Kim et al., KAIST HPCA 2026 [arXiv:2506.04301](https://arxiv.org/abs/2506.04301) and [KAIST EE page](https://ee.kaist.ac.kr/en/research-achieve/professor-minsoo-rhus-team-first-reveal-the-hidden-power-cost-of-ai-agents/) (the 136.6×, 9.2× and 54.5% figures come from the department page, not the abstract); Chkir et al., energy scaling across attention architectures [arXiv:2608.25096](https://arxiv.org/abs/2608.25096); Vellaisamy et al., IISWC 2026 [arXiv:2608.28044](https://arxiv.org/abs/2608.28044); Zine et al., vLLM configurations [arXiv:2607.09172](https://arxiv.org/abs/2607.09172); Zähl et al., consumer GPU [arXiv:2608.00008](https://arxiv.org/abs/2608.00008); Ma et al., Illusion of Power Capping (PPAM 2026) [arXiv:2605.11999](https://arxiv.org/abs/2605.11999); AgentStop [arXiv:2605.15206](https://arxiv.org/abs/2605.15206); Intelligence per Watt [arXiv:2511.07885](https://arxiv.org/abs/2511.07885); Qwen3.8-Next design [arXiv:2608.30320](https://arxiv.org/abs/2608.30320); Hübner et al., Apple vs Oranges [arXiv:2502.05317](https://arxiv.org/abs/2502.05317); Benazir & Lin [arXiv:2508.08531](https://arxiv.org/abs/2508.08531); Huang & Niu, Prefill Ceiling [neurips.cc](https://neurips.cc/virtual/2026/171195); SiliconBench [neurips.cc](https://neurips.cc/virtual/2026/poster/139658); MSR 2026 registered reports [msrconf.org](https://2026.msrconf.org/track/msr-2026-registered-reports); mlx-lm PR #1788, issue #1924, CONTRIBUTING, `qwen3_next.py`; mlx-vlm `qwen4_exp` tree and README; llama.cpp PR #27742.

UNVERIFIED (not opened; HTTP 403): the Preprints.org manuscript 202605.0855 on Apple-silicon energy estimation without `powermetrics`; Benazir & Lin's POMACS 2025 version at ACM (the arXiv version was opened instead). Khan et al., Jay et al., Hähnel et al., Dauner et al., JouleSort and Zhuang et al. are cited from the paper draft's reference list and were not re-opened in this session.

---

## Appendix B. Seat 2 report (Opus), verbatim

## JouleWise methodology against the literature: new experiments for the measurement Mac (Opus seat, 2026-11-07)

### 0. Bottom line

1. **On boundary timing and evidence discipline, our method is ahead of standard practice.** No paper I found does any of the following:
   - bounds the error in placing the prefill/decode boundary;
   - runs identical-condition A/B/B/A nulls that test the floor itself;
   - preregisters and blinds its analysis;
   - checks every number with an independent recompute.

   The big benchmarks either measure one run, or report no uncertainty, or don't split phases at all.
2. **Our weakest point is the claim boundary itself.** `powermetrics` CPU+GPU+ANE is an Apple energy *model*. Apple's own man page says it is "estimated and may be inaccurate" and "should not be used for any comparison between devices". The one instrument we have at the machine's real input, the KM003C meter, is registered as "never a claim number". MLPerf Power requires full-system wall measurement.

   Two pieces of evidence say rail-only energy misses a lot:
   - On Blackwell, GPU-only telemetry misses 41-45 % of system energy. That study used Qwen3.8-27B, the same model as our ALIGN D cell.
   - On an M4 Max, one developer reports a 65 W `powermetrics` GPU rise against a 179 W rise in DC input (a single, unconfirmed report).
3. **The cheapest high-value experiment is still unrun.** The 2026-09-16 prospectus ranked an IOReport counter cross-check and a sampler-cadence sweep as its top literature recommendation. Nothing on `main` implements it.
   - IOReport gives cumulative energy counters with 1 mJ resolution and no root. They include DRAM and GPU SRAM channels, which `powermetrics combined_power` leaves out.
   - It needs no model weights and about one Mac-night.
   - It would test the paper's own primary stated limitation: whether the pulse-derived timing bound transfers to real inference load.
   - It could make short prefill phases resolvable.
4. **Flash-Next changes what has to be measured.** About 16 random n-gram row reads per token from a 102 GB bf16 table paged from SSD is CPU and storage energy. The ALIGN estimand (turn-owned GPU-rail energy) cannot see it.
   - The FN addendum needs a DC-input boundary (KM003C) or the IOReport CPU and DRAM channels. Without one, FN-vs-D comparisons are biased in FN's favour.
   - Disk is a second problem. The maxfit artifact is about 211 GB, internal free space has run 51-115 GB, and no external volume may be mounted during windows. So an FN energy window needs either a Q4 PLE plus lower-bit experts on the internal disk, or a ruling that puts the model volume inside the boundary.
5. **There is an open research gap the port lets us fill.**
   - Engram (DeepSeek) showed that a 100B n-gram table in host DRAM costs at most 2.8 % throughput on an H800. It proposed an NVMe tier but did not test it, and it says nothing about energy.
   - On unified memory there is no host-DRAM tier: SSD is the only offload tier.
   - mlx-vlm already ships a memory-mapped Q4 PLE store, with latency evidence only (65,545 cold misses cost 9.68 s in a 4K prefill on an M2 Ultra).
   - The first measured energy of SSD-tier conditional memory, with computation held bitwise identical across arms, is something only this rig can do: 128 GB, a meter at the DC input, and rails that exclude storage.
6. **For ALIGN, the detection limit is the token model, not the meter.**
   - Our own planning figures put the instrument floor at about 2-30 tokens, against a model-misfit MDE of 80-370 tokens for the 30B.
   - Kimpson et al. show that power alone weakly constrains hidden compute against an adversary who matches energy (at least 41 % of declared capacity can be hidden). With re-execution of declared work the bound tightens to 5.9 %.
   - Our seeded identical-work replays are that re-execution. Duration, which is deliberately kept out of the residual, is the natural second channel.
7. **Upstream: verification evidence is the most achievable contribution, not a new port.**
   - mlx-lm PR #1788 (qwen4_exp) has been blocked under `await verification` since 08-29, with no activity since 10-04.
   - mlx-vlm and llama.cpp both merged qwen4_exp support in late August. mlx-vlm already has external PLE storage, but only in Q4 or nvfp4.
   - Achievable now: (a) our mlx-vlm D1 fix, where a ragged-batch QSA computes the sparse selection and then discards it, which I found no existing report of; (b) a verification package for #1788 (transformers-pinned tests plus real-weight per-layer parity); (c) later, a bf16/q8 extension of mlx-vlm's PLE store.

### 1. What I compared

These are the elements of our method, read from `origin/main` and the R1 lane:

- **Primary boundary.** `powermetrics` processor rails (CPU+GPU+ANE combined), requested at 100 ms; records actually arrive about every 129 ms.
- **Phase energy.** Energy is assigned by record-overlap integration. A phase needs at least 3 records, and the p42 prefill is registered as expected unresolvable.
- **Timing calibration.**
  - An in-window GPU pulse train: 59 pulses on a base-two varied-gap schedule.
  - A rate-aware clock anchor.
  - A pre/post bracket with a 9.724 ms screen; the bracket refuses a window above 10.164835 ms.
- **Detection floor.** The floor is the maximum of an absolute component and a comparative component. It uses every joint corner of the member intervals, a small-sample factor g(n), and a drift allowance A_k. The identical-condition A/B/B/A null tests the floor itself.
- **Admission and quiet guards.**
  - A 180 s settle, then a 30 s idle baseline (CPU-busy p95 ≤ 0.5; combined power p95 ≤ 1 W).
  - A contention monitor, an agent census, and OS quieting (Spotlight, Photos agents).
- **Battery.** The battery must float, not charge. Assist is flagged and gets its own sensitivity line, never an exclusion.
- **Thermal.** An SMC die/heatsink classifier and G0/G1 gates with holds (ALIGN v4).
- **Drift.** A NEG-8 reference corpus: start triplet, midpoint, end triplet.
- **Whole-machine meter.** The KM003C at the USB-C DC input (50 Hz Vbus×Ibus) plus the battery term −B0AC×B0AV. It gives ρ = ΔE_rail / ΔE_machine, which is descriptive only.
- **Analysis discipline.**
  - Sealed registration and plan, a blind dry run, and an independent standard-library recompute with a comparator whose bars were fixed blind.
  - A public deviation log (DLE-0 to DLE-3).
  - BYTES uses two-stage unblinding.
- **ALIGN.** A 5-term token-model energy residual on SHADE-Arena episodes with Qwen3.8-27B 8-bit, including a known-H tamper test.
- **Flash-Next.** 6-bit experts, everything else bf16, and the bf16 n-gram PLE table paged from SSD.

### 2. Where we are stronger or weaker than standard practice

| Area | Standard practice (sources) | JouleWise | Verdict |
|---|---|---|---|
| Phase split and boundary error | TokenPowerBench tags each sample with the active phase and integrates. It reports no error bars and does not say how straddling samples are assigned. "From Prompts to Power" (32,500 measurements) says outright that it does not measure prefill and decode separately. ML.ENERGY works per steady-state response. | Boundary uncertainty is calibrated in-window with a bounded fit and a rate-aware clock. Short phases get a printed refusal. | **Stronger.** Nobody else bounds phase-edge reassignment. |
| Sampler aliasing | Yang et al. find nvidia-smi on A100/H100 averages only 25 ms of every 100 ms. Their fixes are phase-shifted delays and repeated trials, which cut mean error from 39.27 % to 4.89 %. | The varied-gap pulse schedule is the same remedy in a more formal form. **But** we have never measured the duty cycle or impulse response of `powermetrics` itself. | Stronger in design; **the gap is untested** (idea 1). |
| Repetition and variance | ML.ENERGY: "not able to run the benchmark multiple times". MLPerf Power sets no variance or repeat requirement. The AI Energy Score runs 10 repetitions but reports no interval. | Kept-unit t-intervals, worst-case floors, A/A nulls, Holm correction, and refusals. | **Stronger.** |
| Prereg, blinding, recompute | Hoefler & Belli found the state of practice "lacking" in a 120-paper sample. Mytkowicz et al. found that none of 133 papers handled setup bias. Registered reports exist in software engineering (ESEM, MSR). I found no ML-energy registered report. | Sealed plans, a blind dry run, an independent recompute, and a deviation log. | **Much stronger**, at a large cycle-time cost (8 refused attempts in B5; dry runs that took up to about 37 h before the D-188 rewrite). |
| Boundary validity | MLPerf Power requires full-system measurement with SPEC-certified analyzers (e.g. the Yokogawa WT310) at wall AC, and loops any run shorter than 60 s. Most LLM work is GPU-only: ML.ENERGY (Zeus/NVML), the AI Energy Score (GPU-only scoring), From Prompts to Power. Fischer finds CodeCarbon underestimates by 20-30 %. | Rails (an Apple model) are the claim boundary. The KM003C at DC input (after the adapter, not certified) is descriptive. The battery term is included. | **Mixed.** We are better than GPU-only work because we have two boundaries. We are weaker than MLPerf because the stronger boundary never carries a claim, and AC adapter loss is excluded. |
| Apple-specific practice | GreenBench, IPW and "Apple vs Oranges" all use `powermetrics` alone. IPW notes that GPU-only Apple energy is "badly understated" for ANE workloads. Apple vs Oranges confirms that signal-triggered samples cover the whole interval. | Rails plus SMC PDTR/PSTR, the KM003C and the battery term. Desk check: PDTR = 0.955 × meter + 2.3 W (r = 0.9975). | **Stronger.** I found no published Apple LLM-energy study with an inline DC meter. |
| Laptop confounds | MLPerf excludes mobile and battery devices. The sustained-load edge study equilibrates to ΔT < 2 °C over 60 s, drops run 1, and ran its laptop **on battery**. | Battery float is required and assist is flagged; the power mode is pinned; the display is asleep; Spotlight and Photos are paused; an SMC thermal classifier with gates. | **Stronger.** It is also expensive: the G0 cap of 600-1,200 s is now what limits W1. |
| Time resolution | Zeus and NVML read hardware energy counters at window edges. zeus-apple-silicon reads IOReport counters at 1 mJ and warns of quantization below about 10 ms. | 129 ms interval averages. The p42 prefill is unresolvable, and 37 of 50 diagnostic short prefills failed the resolvability rule. | **Weaker.** Counter reads at the runtime's own phase stamps may remove most of this (idea 1). |
| Order and carryover | Mytkowicz et al. recommend randomizing the setup. | A fixed A/B/B/A order. GAMMA states it is "not randomized". ALIGN discloses an asymmetry between what precedes A members and what precedes B members. | **Weaker.** For new packs, randomizing each block's orientation (A/B/B/A or B/A/A/B) would make carryover estimable at no cost. |
| External validity | MLPerf: 60 systems. ML.ENERGY: 40 models. Chung et al.: 1,858 configurations. | One machine, one OS build, one stack. Batch 1, greedy, a fixed 42-token prompt. Intervals cover a single window, though Block 6 replications address between-window variation. | **Weaker by design**, and it is disclosed. Batch 1 is the honest regime for local agents. |
| Floor conservatism | GUM-style combined uncertainty is the norm in metrology. | Worst-case corner enumeration with refusal above n = 16. The diagnostic corner-widened floors were 6-11× the point-only floors (2.2-3.2 J against 0.29-0.49 J). | **A choice, not a flaw.** It risks "not resolvable" on most contrasts. Keep printing the point-only floor beside the widened one. |
| Agent and monitor energy | Agent energy is measured per task or per successful goal (EpG: GPU dynamic energy is 83.8 % of agentic EpG locally). Luo et al.: an agent spends 63× the energy per output token of saturated serving. I found no measured energy for control monitors. | Turn-owned energy is tiled exactly against the episode, with token-level design rows. | **Stronger in attribution.** The ALIGN rail-only estimand misses CPU, DRAM and storage work. |

### 3. Claims in the literature this rig could test or overturn

1. **GreenBench (abstract):** an M4 Pro draws "~0.47 W of CPU+GPU package power during sustained inference" of 3-9B models at up to 175 tok/s. That is implausible for GPU decode. Any non-claim desk capture on an M3 Max would check the order of magnitude, though the chip differs. (I could read only the abstract; the PDF did not parse.)
2. **Apple developer forum, M4 Max (one user, no reply):** the GPU rail misses about two-thirds of the DC-input rise, attributed to data movement (about 5 pJ/B and 2.7 pJ/FLOP). Tested by idea 2 and by BYTES' H2 rest line, P̄_rest = c + ε_rest·BW + λ·P̄_rails.
3. **Kyung, Yun & Ahn (modeled, not measured):** SSD offload of MoE experts raises per-token energy 4.7-12.5×, assuming a flash read cost of 102.4 pJ/b. They say offload might pay off only at batch < 3 or on edge devices. Tested by ideas 2 and 4: a measured system-level J/bit, and expert streaming at batch 1.
4. **Engram:** a 100B table in host DRAM costs at most 2.8 % throughput (H800, PCIe). The NVMe tier is proposed but untested, and energy is not discussed. Tested by idea 3.
5. **Wu et al. (measured energy law):** at batch 1 with a cached prefix, a decode token costs about 335× a prefill token. The context term does not amortize with batch size, and the same functional form fits dense, MoE and quantized models. On the M3 Max, prefill is far slower relative to decode, so I predict a much smaller ratio. Tested by idea 11, using BYTES' recorded but unanalysed 2,048-token prefills and ALIGN's turn rows.
6. **Luo et al. (Qwen3.8-27B on Blackwell):** GPU-only telemetry misses 41-45 % of system energy; thinking-mode per-token energy differs by less than 1 %; an agent spends 63× the energy per output token of saturated serving. Our D cell is the same model. Tested by ideas 6 and 11.
7. **Dutta et al.:** speculative decoding can raise energy (0.61-0.65× savings factor for Llama-70B on CNN-DM), savings scale with speedup at a slope that depends on the model pair, and overheads take 6-10 % of runtime. On MLX, verification is not free: the best EAGLE-3 prototype reached 1.05× (mlx-lm discussion #890). Tested by idea 5, with outputs held identical.
8. **Ma et al. (H200):** memory-bound decode ignores power caps, and locking the SM clock recovers up to 32 % of decode energy. The Apple analogue is Low Power Mode and High Power Mode, for which I found no measurements. Tested by idea 10.
9. **Quantization direction disagrees across studies.**
   - StarCoder2: quantization *increased* energy because throughput fell.
   - TokenPowerBench: FP8 cuts energy by about 30 %.
   - Hydra: quantization lowers memory traffic and energy, with non-monotonic effects on power.

   BYTES (Qwen3-8B 4-bit against 8-bit) already tests this on unified memory.
10. **Alfarizy et al.:** OLMoE uses 2.1× the energy per token of an active-matched dense model on Jetson. They could not measure energy on the M2 Pro because of tooling. BYTES' "active or resident" verdict tests this on Apple.
11. **Tummalapalli et al.:** an iPhone 16 Pro loses about 41.5 % of throughput under sustained load, and nobody has measured a MacBook. Tested by idea 8.
12. **Kimpson et al.:** β ≥ 0.41 of compute can be hidden from analogue power under matched-energy strategies, and β drops to 0.059 when the verifier can re-execute declared work. Tested by idea 6.
13. **SHADE-Arena:** sabotage success depends on a hidden scratchpad. CoIn audits hidden token counts with embedding hash trees (up to 94.7 %). An energy residual is a *physical* audit of hidden-token count, tested by idea 6.

### 4. The new experiments, ranked (details are in `ideas`)

| Rank | Idea | Mac-nights | Gate |
|---|---|---|---|
| 1 | Instrument night: `powermetrics` transfer function and IOReport counters (idea 1), together with where the missing watts go (idea 2) | 1-1.5 | No weights. Can run by day if the machine is quiet. |
| 2 | Two-channel physical audit of hidden tokens (ALIGN analysis) | 0 | Register before the held-out pool is unblinded |
| 3 | Agent energy decomposition and the prefill/decode ratio | 0 | Register before BYTES stage 1 (12 Nov). KM003C on D windows needs a ruling. |
| 4 | SSD-tier conditional memory: Flash-Next PLE resident, paged, or uncached | 1-1.5 | After FN live validation; needs internal disk space |
| 5 | Thermal sensitivity atlas and gate relaxation | 1-1.5 | It pays for itself if the gates can be relaxed |
| 6 | Monitoring tax for AI-control monitors | 1 (+1 co-resident) | Uses recorded transcripts |
| 7 | Context term across attention regimes | 1.5-2 | Uses the QSA kernel |
| 8 | DVFS power-mode energy by phase | 1 | Needs a sudoers extension and a pack-local deviation |
| 9 | Speculative decoding with outputs held identical | 2 | Needs stack B with the observability contract |
| 10 | Expert streaming at batch 1 | 1 | Conditional on an external-SSD ruling (bf16 experts are about 193 GB) |

The total is about 10-12 Mac-nights. ALIGN R1, W1 and D1-D5 have priority on the Mac, so the instrument night and the analysis riders come first.

### 5. Flash-Next (qwen4_exp): what is achievable and what can go upstream

**State as of 11-07, read-only GitHub API:**

| Project | State |
|---|---|
| mlx-lm #1788 | Open. Label `await verification`; merge state blocked; 23 comments; idle since 10-04. mlx-lm `main` has no qwen4_exp, but it does have `longcat_flash_ngram.py`, a precedent for n-gram tables kept as module parameters. Issue #1798 (gated-delta readout scale) was closed as already fixed on `main`. |
| mlx-vlm (now `Neywa-Labs/mlx-vlm`) | qwen4_exp merged 08-26 (#2032). Also merged: MTP, continuous batching, a QSA kernel, and external PLE storage (#2045, 08-28, Q4 affine g32 and nvfp4 only, row-addressable memory-mapped store). On an M2 Ultra with 128 GB, #2045 reports 19.04 tok/s decode and a 217.8 tok/s 4K prefill, in which 65,545 cold misses took 9.68 s. Open: DFlash defects (issue #2581, PR #2630). I found no issue or PR covering our D1 ragged-QSA defect. |
| llama.cpp | #27742 merged 08-27. |

**Our port:**
- The canonical module passes 31 tests. fp32 logit differences are at most 1e-5 against transformers 5.22.1.
- Real-weight parity passes for layers 2 and 3, and the bf16 L3 reference exists.
- Mac validation waits for the SSD, Sunday to Tuesday.

**Achievable upstream contributions, in order:**
1. **mlx-vlm D1 fix.** The fix, a test and full evidence are ready in `docs/align/upstream_mlxvlm_d1/`. It is small, correct (exact parity restored, ≤ 7.7e-7 fp32), and touches a user path (`BatchGenerator`). Ed files it. A grep of mlx-vlm's CONTRIBUTING found no AI clause, but the PR templates are UNVERIFIED.
2. **A verification package for #1788.** It would contain transformers-pinned tiny-checkpoint logits in the official layout, plus real-weight per-layer parity on the official bf16 weights (GOAL items 5 and 11). That is exactly what the label asks for.
   - Ed writes every comment himself: mlx-lm prohibits AI-written posts.
   - We never run #1788's code, so we hand over tests and do not report results on their branch.
3. **A bf16/q8 extension of mlx-vlm's PLE store.** Our `NgramTable` already does f32/bf16/q8/q4 rows, F_NOCACHE pread, fault counters and residency accounting. This is a medium-effort follow-up.
4. **A separate mlx-lm PR, only if #1788 stalls further.**
   - The PR limit (#1749) is likely one open PR for a new contributor.
   - mlx-lm `main` needs mlx ≥ 0.32.3, so the work needs a main-branch venv.
   - Ed must understand every line.
5. **An energy result, not code:** idea 3 would be the first measured energy of SSD-tier conditional memory. None of the three implementations report energy.

**Blockers:**
- The SSD delivery.
- The SN7100 is DRAM-less and sits behind a USB4 bridge (no host memory buffer), so random PLE reads will be slower than the drive's specification.
- Internal disk space for any FN energy window.

**Arithmetic:**
- From `ngram_size` 3 and `heads_per_ngram` 8, there are 16 lookups per token. That matches mlx-vlm's 65,545 misses ≈ 4,096 × 16.
- The 51B-parameter size implies rows of about 160 bf16 values, i.e. 320 B. On a cold read a 16 KiB page can amplify that up to about 51×.

### 6. Consequences that apply now, whatever experiments are chosen

1. Run the instrument night (ideas 1+2) before anything else depends on the boundary or the floor. It has been overdue since 09-16.
2. The FN addendum must name a DC or IOReport boundary and an internal-disk plan. Consider a Q4 PLE (about 26-30 GB, as in mlx-vlm), which would also allow a resident-PLE control arm.
3. Decide before the D1 freeze whether the KM003C rides on ALIGN D windows. It refuses nothing, and its reader costs about 0.25 % of one core.
4. Before BYTES' 12 Nov stage-1 unblinding, register two descriptive lines: the prefill/decode per-token ratio, and rest-energy against bytes.
5. New packs: randomize each block's orientation, A/B/B/A or B/A/A/B (lean, no new gate).
6. Proportionate care: idea 5's β_T answer is the evidence-based route to cutting G0/G1 wait time, which now limits W1 under ruling 1(f).

### 7. Sources opened

**Energy measurement and benchmarking**
- MLPerf Power: https://arxiv.org/html/2410.12032v2
- ML.ENERGY benchmark: https://arxiv.org/html/2505.06371v2
- Where Do the Joules Go? (abstract): https://arxiv.org/abs/2601.22076
- Yang et al., nvidia-smi sampling: https://arxiv.org/html/2312.02741v3
- Fischer, CodeCarbon validation: https://arxiv.org/html/2509.22092v1
- From Prompts to Power: https://arxiv.org/html/2511.05597v1
- TokenPowerBench: https://arxiv.org/html/2512.03024
- AI Energy Score: https://huggingface.github.io/AIEnergyScore
- How Hungry is AI?: https://arxiv.org/abs/2505.09598v6
- Vellaisamy et al., request and token energy costs: https://arxiv.org/abs/2608.28044
- The Illusion of Power Capping in LLM Decode: https://arxiv.org/abs/2605.11999
- Hydra (abstract): https://arxiv.org/abs/2608.25053
- StarCoder2 quantization (abstract): https://arxiv.org/abs/2411.12758
- Dutta et al., speculative-decoding energy: https://arxiv.org/html/2602.09113v1
- Edge LLM inference under sustained load: https://arxiv.org/html/2603.23640

**Apple silicon**
- GreenBench (abstract): https://arxiv.org/abs/2608.28667
- Apple vs Oranges: https://arxiv.org/html/2502.05317v1
- Intelligence per Watt: https://arxiv.org/abs/2511.07885v2
- IPW platform support: https://hazyresearch.stanford.edu/intelligence-per-watt/benchmarking/platform-support/
- Apple developer forum, M4 Max discrepancy: https://developer.apple.com/forums/thread/819927
- `powermetrics` man page: https://keith.github.io/xcode-man-pages/powermetrics.1.html
- SMC power side channel: https://arxiv.org/abs/2306.16391
- macpow: https://docs.rs/macpow
- zeus-apple-silicon: https://github.com/ml-energy/zeus-apple-silicon
- Bielik speculative decoding on MLX: https://arxiv.org/abs/2604.16368
- mlx-lm discussion #890: https://github.com/ml-explore/mlx-lm/discussions/890

**Offloading, MoE and conditional memory**
- SSD offloading considered harmful: https://arxiv.org/html/2508.06978v1
- LLM in a Flash: https://arxiv.org/abs/2312.11514
- Engram paper: https://arxiv.org/html/2601.07372v1
- Engram repository: https://github.com/deepseek-ai/Engram
- Alfarizy et al., MoE on edge (EmergentMind summary): https://www.emergentmind.com/papers/2606.21428

**Agents, monitoring and verification**
- Luo et al., agent inference on Blackwell: https://neurips.cc/virtual/2026/170717
- Wu et al., prefill/decode/context energy law: https://neurips.cc/virtual/2026/170701
- Energy per Successful Goal: https://arxiv.org/abs/2605.22883
- Kimpson et al., power and covert compute: https://matsprogram.org/research/can-power-draw-constrain-covert-compute-limits-of-analogue-verification-for-ai-governance
- SHADE-Arena: https://arxiv.org/abs/2506.15740v2
- CoT monitorability: https://arxiv.org/abs/2507.11473
- CoIn: https://arxiv.org/abs/2505.13778
- Dauner & Socher (ScienceDaily report): https://www.sciencedaily.com/releases/2025/06/250619035520.htm

**Method and preregistration**
- Hoefler & Belli: https://evaluate.inf.usi.ch/node/366
- Mytkowicz et al.: https://evaluate.inf.usi.ch/node/4.html
- ESEM registered reports track: https://conf.researchr.org/track/esem-2022/esem-2022-registered-reports

**GitHub, read-only API (no comments posted)**
- ml-explore/mlx-lm: PR #1788, issue #1798, contents of the models directory.
- Neywa-Labs/mlx-vlm: PRs #2032, #2045, #2630; issue #2581; the qwen4_exp README and `ple_storage.py`.
- ggml-org/llama.cpp: PR #27742.

**UNVERIFIED (not opened, or blocked):**
- Jay et al., CCGrid 2023, comparison of software power meters (HAL blocked).
- The Zeus NSDI paper (cited only through ML.ENERGY).
- The KM003C's accuracy specification.
- The 3.56× MoE figure attributed to Chung et al. (not in the abstract).
- Any mlx-vlm PR-template AI policy.

### 8. Scope and blinding

- **What I read, from origin:**
  - `README.md`, `CANONICAL.md`, the top of `RUN_STATE.md`, and the 11-07 RESUME.
  - The B5 registration (§0.2-0.5, §5.8), the B5 analysis plan (intro, §8), and `DEVIATION-LOG.md`.
  - Paper draft v1 (sections 1-6).
  - `pilot_protocol_v4.md`, `energy_residual.md` and `SSD-ALWAYS-ATTACHED-STUDY.md`, all on the R1 lane.
  - `block6_machine_test.md`, `bytes_pack_design.md`, and the 09-16 prospectus (relevant parts).
  - The qwen4_exp GOAL, canonical, upstream, perf, expert_streaming, mbp_live and mlx-vlm audit docs.
- **Blinding:** I did not read, list or open any `/Users/edr/jw-b5-*`, `/Users/edr/night-*`, night-custody, night-archive or `restricted/` path. No B5 value was seen or inferred. All the numbers I quote are instrument, diagnostic or planning figures from public docs.
- **Hardware and code:** I did not touch the MBP, loaded no weights, executed no community code, and created no worktree, files or commits.
