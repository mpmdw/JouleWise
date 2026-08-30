# 01 — Sol seat (gpt-5.6-sol, xhigh, read-only, codex MCP; thread 01a04b3c-332d-7082-ad61-445aaf1658c8)

Verbatim. Round 1 answers the original brief; round 2 answers the addendum.

## Round 1 (original four questions)

Freeze `_v5` on a **ten-prompt, real, immutable HumanEval-derived roster with equal work**: one prompt assigned to each ABBA block, rendered to exactly 256 input tokens, followed by exactly 512 greedy output tokens with EOS stopping suppressed and thinking pinned off. Reuse the same block-to-prompt map in both contrasts, retain `n=10`, Holm `m=2`, and the existing 80-member design. Make gross joules per query the primary estimand and joules per generated token secondary. This best balances recognizable work with determinism, pairing, phase visibility, and honest interpretation. The tree does not contain the proposed newer model pair, HumanEval source bytes, `_v5` floors, or `_v5` timing scouts, so those must be frozen before the campaign rather than inferred from Qwen2.5.

## 1. Workload options

### Current quantitative baseline

The present `_v3` generator specifies:

- 10 ABBA blocks per contrast.
- Two repeats of each model per block: `A, B, B, A`.
- Two contrasts, producing  
  `10 blocks × 2 contrasts × 2 models × 2 repeats = 80` science bundles.
- Decode arm: 128 input tokens, 512 output tokens.
- Proposed prefill arm: 256 input tokens, 512 output tokens.
- Greedy decoding, one workload repetition, one warm-up.
- Sampling at 10 Hz, 30 seconds idle, 5 seconds warm-up.
- Budget: `168 + 130 + 12 = 310 minutes`, or 5 h 10 min.

The older measured planning anchors are 92.7 seconds per 1.5B bundle and about 97 seconds per 7B bundle. Therefore:

- One contrast's science members:  
  `10 × 2 × (92.7 + 97) = 3,794 s = 63.23 min`.
- Both contrasts:  
  `7,588 s = 126.47 min`.

Those values are useful arithmetic checks, not forecasts for D164's unspecified newer pair.

Also, the brief's "about 1 J floor" is only a shorthand for phase-edge attribution uncertainty: about `31 ms × 33 W ≈ 1 J`. The operative clearable contrast was nearer 5 J in D122's planning. The historical 256-token prefill projection was 11.619860 J, or 2.32 times that practical bar. Actual `_v5` floors do not yet exist.

### (a) Keep the present fixed synthetic prompt

- **Determinism:** Easiest option. Exact prompt and exact output length minimize variation, but `_v5` still must pass the bit-exact repetition gate for every `(model, prompt)` cell.
- **Pairing:** Perfect equal-work pairing. Each ABBA member executes the identical request.
- **Floor clearance:** Strong for decode because 512 tokens sustain the signal. Historical Qwen2.5 planning values were approximately 51.1 J and 192 J per member, with a diagnostic model contrast of 146.730349 J. None transfers to D164's models.
- **Prefill resolution:** The 256-token prompt is plausible, but no relevant p256 corpus exists. Every new-model prompt cell must demonstrate at least three overlapping power records.
- **Night length:** Current structural budget is exactly 310 minutes.
- **Honest paper sentence:**  
  "On this M3 Max/MLX/powermetrics stack, for one frozen synthetic 128-input/512-output request, model B used Δ J more gross decode energy per request than model A; this result does not generalize to natural queries."

This is the safest metrology choice but the weakest reader-facing workload.

### (b) Fixed real-prompt set

- **Determinism:** Strong if the exact source bytes, prompt renderer, tokenizer identity, item order, and output cap are frozen. Run the bit-exact gate item-by-item.
- **Pairing:** Use one prompt per block, shared by all four ABBA positions and by both contrasts. Prompt then acts as a paired block stratum rather than an uncontrolled source of scatter.
- **Floor clearance:** Exact 512-token output preserves the sustained decode signal. Content can still change model delta and scatter, so new per-cell floors remain mandatory.
- **Prefill resolution:** Render every prompt to exactly 256 tokens. Require all ten prompts on both models to produce at least three positive-overlap records; four or more gives one-record margin.
- **Night length:** Still 80 science bundles and the same 310-minute planning envelope if there is one prompt per block and no extra item loop.
- **Honest paper sentence:**  
  "Across a frozen ten-item HumanEval-derived roster, with each request rendered to exactly 256 input tokens and each model forced to emit exactly 512 greedy tokens, model B used Δ J more gross decode energy per query than model A; no accuracy or broader coding-performance claim is made."

This is my recommendation.

### (c) Natural stopping on real prompts

- **Determinism:** Greedy natural EOS can be bit-exact, but the gate must match response hashes, stop status, and realized output exactly. A capped run and a naturally completed run are not interchangeable.
- **Pairing:** Prompts remain paired, but different output lengths between models mean the comparison is no longer equal work. Unequal member durations also weaken the exact midpoint symmetry assumed by ABBA; the recorded timestamps must be retained.
- **Floor clearance:** Short outputs may fall near the cell floor. A 512-token cap protects only worst-case duration, not minimum signal.
- **Prefill resolution:** Input processing can remain fixed at 256 tokens, but prompt-specific overlap counts must still pass. Natural decode duration does not rescue an unresolvable prefill phase.
- **Night length:** At most the fixed-cap science duration, but expected duration cannot be stated until the roster and new models are scouted.
- **Honest paper sentence:**  
  "Across the frozen roster under greedy natural stopping capped at 512 tokens, model B used Δ J more gross energy per completed query and emitted ΔT more tokens; the energy difference therefore includes model stopping behavior and is not an equal-work efficiency comparison."

This is ecologically attractive but creates the principal confound the campaign is supposed to avoid.

### (d) Small mixed workload profile

- **Determinism:** Gate every item independently. The existing `jw_mixed_v1` is deterministic in shape: 48 internal synthetic items across chat, code, JSON, multilingual, reasoning, and summarization, all with 512 input and 256 output tokens. Its frozen subset SHA is  
  `952cb8ef7db6f421486606e650530b341205296d6999a3d75839639bc3cc2363`.
- **Pairing:** A defensible 10-block design needs one frozen item per block and fixed category weights. Multiple items inside each bundle alter duration and the estimand; items must not be treated as independent `n`.
- **Floor clearance:** Category- and shape-specific signals can differ. A pooled floor cannot be transported across prompt shapes.
- **Prefill resolution:** Longer 512-token prompts should help, but eligibility remains an observed overlap-count condition, not an inference from token count.
- **Night length:** One fixed item per block preserves the 80-member structure. A `k`-item suite loop changes science time approximately in proportion to `k` and has not been budgeted.
- **Honest paper sentence:**  
  "For the predeclared weighted mix of ten fixed requests, model B used Δ J more gross energy per request than model A; this is an aggregate workload-profile result, and no category-specific ranking is claimed."

This improves breadth, but the existing profile is synthetic and its 512/256 shape does not match the proposed p256/512 campaign without a new profile and new floors.

### (e) Standardize length while asking the same recognizable question

- **Determinism:** Excellent when the exact question, padding rule, output policy, and tokenizer are pinned.
- **Pairing:** Excellent equal-work comparison.
- **Floor clearance:** Exact 512-token output should be comfortably measurable if the model contrast is material, but absolute member energy alone does not prove that `|B−A|` clears its floor.
- **Prefill resolution:** Exact 256-token input is the right candidate, subject to the three-overlap scout gate.
- **Night length:** Same 80 members and 310-minute envelope.
- **Honest paper sentence:**  
  "For the single frozen HumanEval question rendered to exactly 256 input tokens and exactly 512 greedy output tokens, model B used Δ J more gross energy than model A; the estimate applies only to this question and length."

This is good metrology, but ten distinct pinned prompts are preferable because one question cannot support even limited workload breadth.

## 2. Output-length confounding and preregistration

For the recommended equal-work design, preregister:

1. **Primary:** paired ABBA mean difference in gross joules per completed fixed-budget query.
2. **Secondary:** gross joules per generated token.
3. **Separate phase result:** prompt-processing joules per query, with joules per input token as a descriptive normalization.
4. Report realized input/output counts, stop reasons, duration, and capped fraction even though they should be invariant.

Joules per token should not be the primary estimand. It does not remove fixed overhead, prefill cost, KV-cache behavior, content effects, or duration-dependent attribution. The old 1.5B timing illustrates the problem: a member took about 92.7 seconds even though 512-token generation itself took only about 2.05 seconds.

If natural stopping is chosen instead, preregister gross joules per completed query as the ecological primary and joules per realized output token as a secondary diagnostic. The paper must explicitly say that the comparison includes stopping behavior. Do not select whichever normalization looks better after collection.

## 3. Concrete `_v5` profile

### Frozen workload

- **Source:** OpenAI HumanEval, using immutable vendored source bytes and a recorded SHA-256.
- **Selection rule:** Traverse canonical task order and select the first ten prompts that fit within a predeclared raw-token allowance, leaving enough room for the fixed wrapper and deterministic padding.
- **Number of prompts:** 10 total.
- **Block assignment:** one distinct prompt per block; the same block map applies to both model arms and both contrasts.
- **Input:** exactly 256 tokens under the shared production tokenizer.
- **Padding:** deterministic code-comment padding only; no semantic content added after the benchmark prompt and no truncation.
- **Output:** exactly 512 greedy tokens, with EOS suppression or equivalent exact-budget control.
- **Thinking:** disabled and pinned off.
- **Sampling:** temperature-free greedy operation; no sampler seed is treated as a replicate.
- **Claims:** energy only; no correctness, pass@k, coding ability, or capability claim.

### Pairing and determinism

Each prompt appears in one block as:

`A1(prompt_i), B1(prompt_i), B2(prompt_i), A2(prompt_i)`

The present determinism tool recognizes repetition groups named like `__rN`; current `a1/a2` run identifiers do not obviously satisfy that convention. `_v5` should either use explicit repetition-compatible IDs or run a separate two-repeat determinism pilot for every model/prompt cell. Exact normalized config, package/runtime/model/tokenizer identities, response status, response text, and response SHA must agree.

### Prefill scout gate

Before freezing the night:

- Both new models × all 10 prompts must have at least three positive-overlap power records during prefill.
- Record the minimum overlap count and count margin relative to three.
- A four-record minimum is preferable but is not the current formal gate.
- Do not infer p256 eligibility by doubling the historical p128 duration. Historical p128 results were:
  - 1.5B: 37 of 50 attempts had only two overlaps and failed.
  - 7B: all 50 passed, with 33 having three overlaps and 17 having four.
- New models, prompt alignment, and runtime can change those counts.

### Night arithmetic

The frozen structure remains:

- `10 blocks × 2 contrasts × 4 members = 80` science bundles.
- General two-contrast science time for new-model member durations `s_A` and `s_B`:  
  `40 × (s_A + s_B)` seconds.
- Old Qwen2.5 anchors produce `40 × (92.7 + 97) = 7,588 s`, or 126.47 minutes.
- The full current envelope, including calibration, references, bound work, idle cadence, and margin, is 18,600 seconds or 310 minutes.

D164's new model pair and scout timings are absent from the inspected tree. Therefore, 310 minutes is a design envelope, not a validated `_v5` runtime. Recompute the member terms from scouts before the night is scheduled.

### Strongest counterargument

The proposed workload is still artificial: deterministic padding and forced 512-token completion deliberately trade ecological validity for metrological control. A code-only roster cannot support conclusions about chat, summarization, reasoning, accuracy, or ordinary natural stopping. The design is defensible only if the paper calls it a frozen energy probe rather than "representative AI use." A natural-EOS or mixed-suite study should be a separate follow-up with its own floors and estimands.

## 4. Research-question mapping

| Option | Research questions it can answer | Required limitation |
|---|---|---|
| (a) Synthetic fixed prompt | `RQ-ATTRIBUTION-DOMINANCE`, `RQ-METHOD-FLOOR`, `RQ-MAC-BASELINES`, pairwise portion of `C5-1.1` | One workload only; no real-task or broad scaling claim |
| (b) Fixed real-prompt set | Same core questions; `C5-I.1`; `RQ-HUMANEVAL-IMPORT-SMOKE` for HumanEval | Energy only; no accuracy, pass@k, or capability conclusion |
| (c) Natural stopping | Core pairwise questions; `C5-I.1`; possibly `C5-W.2` only for a reasoning model with an explicit fixed-budget comparator | Energy includes output-length and stopping-policy effects; greedy repeats do not answer `RQ-ENERGY-VARIANCE` |
| (d) Mixed profile | Core metrology; `RQ-SHAPE-ENERGY`; potentially `C5-W.1` with shape-matched AP-4 controls and `C5-W.3` for preregistered category ranking | Items are workload breadth, not independent sample size; pooled results do not license category claims |
| (e) Same recognizable question, fixed length | Core pairwise questions; `C5-I.1`; HumanEval smoke if externally sourced | A single question cannot support workload/category generalization |

`RQ-SESSION-SHAPE` requires an actual session or holdout design; `C-023-COEFF-TRANSPORT` requires the Q4 synthetic-to-real prediction protocol; `RQ-CONTENT-SENTINEL` requires its five-condition AP-6 design. None is answered merely by replacing the current prompt.

The unresolved freeze items are the exact newer model pair, source archive and SHA, ten selected task IDs, tokenizer-rendered fit, EOS-suppression behavior, p256 overlap scouts, new per-cell floors, and new-model member timings. Until those exist, the workload recommendation is design-complete but not night-ready.

---

## Round 2 — Addendum — SOL verdict on the leading benchmark path

Adopt **GSM8K with natural EOS capped at 512 tokens**, not forced-length HumanEval, as the scored headline workload. Freeze 80 test questions into ten disjoint eight-question blocks; run each block in `A/B/B/A` order for Qwen3-1.7B-4bit and Qwen3-8B-4bit. This produces a recognizable fixed-budget result, enough distinct questions for a meaningful labelled correctness denominator, and block-level energy windows comfortably larger than individual short-answer windows. Keep the dedicated p256 prefill contrast separate. The benchmark arm needs a prospective `_v5` analysis-plan amendment because natural-EOS resident-suite gross energy is not the current fixed-512 decode cell.

### Proposed frozen profile

- Models:
  - `mlx-community/Qwen3-1.7B-4bit`, revision `3b1b1768f8f8cf8351c712464f906e86c2b8269e`.
  - `mlx-community/Qwen3-8B-4bit`, revision `545dc4251c05440727734bcd94334791f6ab0192`.
- Both are Apache-2.0, dense Qwen3 models with the same 151936 model vocabulary and tokenizer file SHA-256:  
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`.
- Benchmark: GSM8K test split, 1,319 items, MIT-licensed.
- Selection: sort all test questions by `sha256(question_text)` and take the first 80; freeze source commit/archive hash, item hashes, order, and license hash.
- Blocking: distribute those 80 in hash order round-robin into ten disjoint blocks of eight.
- Prompt: one user message, no system message:

  > Solve the problem. Show concise reasoning. End with exactly one line of the form `#### <number>`. Do not continue after that line.

- Apply the pinned Qwen3 chat template with `enable_thinking=False`.
- Sampling: greedy, temperature 0.
- Output: `natural_eos`, `max_new_tokens=512`, `suppress_eos=False`.
- Outcomes: `correct`, `incorrect`, or `truncated_before_answer`; also retain `malformed`, cap-hit, emitted-token count, stop reason, and final-answer token position.
- No retries for a bad answer. Only predeclared technical-invalid bundles are replaced.
- "How close" means whether a valid final answer appeared before the cap and at which emitted-token position—not subjective partial credit.

The upstream GSM8K commit/archive and Qwen3 chat-template byte hash are not present in the inspected checkout and therefore remain freeze obligations, not numbers I can honestly supply.

### (i) Joules per solved problem

For model \(m\), block \(i=1,\ldots,10\), and energy repeat \(r=1,2\), let:

- \(E_{mir}\) be gross energy for the resident eight-question block.
- \(\bar E_{mi}=(E_{mi1}+E_{mi2})/2\).
- \(C_{mij}\in\{0,1\}\) be deterministic correctness for question \(j\) in block \(i\).
- \(T_{mij}\) be runtime-observed output tokens.

Preregister:

\[
J/query_m=\frac{\sum_i\bar E_{mi}}{80}
\]

\[
J/token_m=\frac{\sum_i\bar E_{mi}}{\sum_{i,j}T_{mij}}
\]

\[
accuracy_m=\frac{\sum_{i,j}C_{mij}}{80}
\]

\[
J/solved_m=\frac{\sum_i\bar E_{mi}}{\sum_{i,j}C_{mij}}
\]

`J/solved` is the operational ratio: energy spent on **all** 80 attempts divided by successful answers. It properly charges wrong and truncated attempts rather than reporting only the energy of questions the model happened to solve.

Do not use mean itemwise `energy/correct`: individual short GSM8K item windows may have only one or two power samples at the observed 8.82–8.91 Hz cadence. Energy belongs to the eight-item block window; per-query energy is the block total divided by eight.

Pairing and inference:

- Primary energy difference uses the ten paired block differences  
  \((\bar E_{Li}-\bar E_{Si})/8\).
- Uncertainty for `J/solved` resamples the ten paired blocks, preserving their eight-question clusters.
- Accuracy uses 80 distinct questions. The A1/A2 and B1/B2 repeats are not additional accuracy trials.
- Report the paired outcome table: both correct, small-only, large-only, neither.
- Accuracy is descriptive and cannot exclude a block, trigger a top-up, select questions, or gate the energy result.

Floor and denominator gates remain separate:

1. The block-energy contrast must exceed the dedicated same-profile operative floor, `max(floor_abs_j, floor_cmp_j)`, plus any applicable claim-side bar.
2. AP-5's binomial lower-bound guard must support at least three correct distinct items for each reported denominator.
3. If the floor fails, energy is `not resolvable` even if accuracy differs.
4. If the correctness guard fails, `J/solved` is `not estimable` while energy/query, energy/token, and labelled accuracy still report.
5. The ratio itself is never compared directly with a joule floor; it inherits numerator eligibility and the correctness guard.

The energy family can retain Holm `m=2` only if accuracy and `J/solved` remain preregistered descriptive co-outcomes. Confirmatory inference for them requires a separately frozen AP-5 family.

### (ii) Benchmark choice

| Benchmark | Deterministic outcome | License/provenance in tree | Length and pair suitability | Verdict |
|---|---|---|---|---|
| **GSM8K** | Pinned final-number exact match | MIT; 1,319 test items; tree already recommends a SHA-selected 50-item subset | Concise non-thinking reasoning should usually fit 512; small/large spread is plausible but unverified | **Primary choice** |
| HumanEval | Deterministic unit tests only after Python, sandbox, timeout, extraction, and checker hashes are pinned | MIT; 164 tasks; tree proposes 32-item subsets and 256/512 completions | Code often fits 512; likely size spread, but execution adds a large checker surface | Strong follow-up, not first scored night |
| MMLU | Exact multiple-choice letter | Tree records MIT on Hugging Face | Outputs are extremely short, encouraging format/chance effects and weak item windows | Useful accuracy probe, weak energy headline |
| BBH | Task-specific exact match | Tree records MIT | Some concise tasks fit; heterogeneous scorers and prompt formats complicate one frozen profile | Possible second benchmark |
| MT-Bench | No objective deterministic score; normally judge-based | License not verified in the inspected tree | Long conversational answers, judge dependence | Reject for this campaign |

The tree contains no Qwen3-1.7B/8B GSM8K or HumanEval accuracy measurements. A plausible spread is therefore an assumption based on the 4.8× weight-size gap, not a measured prior. Use a disjoint development subset only to check template operation and gross cap-hit rate; do not select claim questions by observed model success.

### (iii) Blocks and bit-exact repeats

Use **eight distinct questions per block, 80 unique questions total**.

Why not one per block:

- Ten unique questions make accuracy move in 10-point steps.
- AP-5's denominator can easily become `not estimable` for the small model.
- A single naturally short answer may be below phase/item resolution.

Each ABBA block executes the identical ordered eight-item roster:

`A1(block_i), B1(block_i), B2(block_i), A2(block_i)`

Greedy natural EOS remains deterministic in principle: EOS position is part of the deterministic token stream. The existing gate must prove:

- A1 equals A2 item-for-item in response SHA, status, stop reason, and emitted tokens.
- B1 equals B2 under the same rule.
- `succeeded` versus `capped` mismatch refuses the repetition group.
- Template bytes, template arguments, rendered prompt-token hashes, tokenizer, model, MLX packages, sampler, and maximum budget match.

The survey's planning rates are 231 tok/s for 1.7B and 49 tok/s for 8B, not measurements on this campaign. At the full 512-token cap:

- Small: `8 × 512 / 231 = 17.73 s` decode per block member.
- Large: `8 × 512 / 49 = 83.59 s`.
- Ten ABBA blocks:  
  `10 × 2 × (17.73 + 83.59) = 2,026 s = 33.8 min` maximum decode generation.

Natural EOS should reduce that, but the actual distribution is unknown. The current 310-minute two-contrast budget cannot simply be reused because it was derived for different models and one forced-length request per member. Scout and recompute the full wall budget.

Only the 40 benchmark-arm bundles run GSM8K. The other 40 retain a dedicated, newly rendered p256 prefill workload. Running the eight-item benchmark suite in both contrasts would double benchmark executions from 320 to 640 without adding accuracy information.

### Harness change required

Today's single-workload path always calls `_generate(..., suppress_eos=True)` and never applies a chat template. It is unsuitable unchanged.

The suite path is closer:

- `natural_eos` already selects `suppress_eos=False`.
- Emitting exactly the budget already records `status=capped`, `stop_reason=length`.
- Response text, response SHA, emitted token IDs, and item status already exist.

The missing load-bearing step is chat rendering. `_prompt_for_suite_item()` currently calls raw `_encode(prompt_text, add_special_tokens=True)`. The benchmark path must instead:

1. Load the chat template from the pinned model revision.
2. Hash its exact bytes.
3. Call `apply_chat_template` with the pinned message list, `add_generation_prompt=True`, and `enable_thinking=False`.
4. Assert identical rendered prompt-token IDs for both same-tokenizer model arms.
5. Record template hash, arguments, thinking state, rendered-token hash, and measured token count in runtime provenance.
6. Include those fields in normalized-config/determinism comparison.

Natural EOS creates real length variance; it does not itself weaken bit-exactness. That variance is part of the workload and must appear in token counts, stop distributions, cap-hit rates, energy/query, and energy/token.

### (iv) Paper sentence and RQ

> "On one M3 Max using MLX and powermetrics SoC rails, across a frozen hash-selected 80-item subset of GSM8K's 1,319-item test split, with the pinned Qwen3 chat template, greedy decoding, thinking disabled, and natural EOS capped at 512 new tokens, Qwen3-1.7B-4bit solved \(c_S/80\) and Qwen3-8B-4bit solved \(c_L/80\); their resident eight-query blocks averaged \(e_S\) and \(e_L\) J/query and \(p_S\) and \(p_L\) J/emitted-token, while the paired block-energy difference \(\Delta\) [cleared/did not clear] its registered floor. Gross joules per solved problem were \(r_S\) and \(r_L\) only where the AP-5 denominator guard passed; these are fixed-subset, fixed-budget outcomes on a contaminated benchmark, not intelligence per joule."

Primary RQ mapping:

- **`C5-1.9`** — energy per correct answer under a controlled envelope, governed by AP-5 and the C-004/C-014 quarantine.
- This campaign answers only the energy-per-correct limb. It does not answer C5-1.9's MoE-versus-dense or designed-difficulty-ladder limbs without a campaign-specific AP-5 amendment.
- **`C5-I.1`** is the companion external-benchmark energy-signature question.
- It does not revive killed **`RQ-INTELLIGENCE-PER-JOULE`**.
- It does not answer **`C5-W.2`**, because thinking is disabled and there is no thinking-on comparator.

### (v) Trap list

1. **Contamination:** GSM8K and HumanEval are heavily contaminated. Freeze source provenance and call correctness a subset outcome, not evidence of general reasoning ability.
2. **Thinking blowups:** Pin `enable_thinking=False`; fail or quarantine unexpected `<think>` delimiters. Do not mix `/no_think` and template kwargs opportunistically.
3. **Parser flexibility:** Pin one checker before execution. Recommended rule: final line must match `#### <canonical-number>`; no post-hoc "helpful" extraction.
4. **Malformed responses:** Natural EOS without the required marker is incorrect/malformed, not silently rescued.
5. **Cap classification:** Cap reached without a valid final marker is `truncated_before_answer`. A valid marker before a later cap hit can still score, with `cap_hit=true` reported.
6. **Large-model cap bias:** The 8B model may reason more verbosely and hit 512 more often. Report cap-hit rate and final-answer position by model; describe correctness strictly as "under this budget."
7. **Length confounding:** A lower-energy model may simply emit fewer tokens. Always publish query, token, emitted-length, and stop-reason results together.
8. **Pseudo-replication:** ABBA repeats improve energy estimation; they do not turn 80 deterministic questions into 320 accuracy trials.
9. **Floor transport:** Forced-512 single-request floors do not transfer to natural-EOS eight-item suite blocks.
10. **Per-item energy:** Short items may fail the three-overlap rule. Infer energy from block windows, not unsupported item joules.
11. **Ratio instability:** Low correct counts make `J/solved` explode. Honor AP-5's guard and print `not estimable`.
12. **Outcome-dependent redesign:** Do not add easier questions, enlarge the cap, or top up blocks after seeing accuracy.
13. **Template drift:** `prompt_template_id` metadata alone is insufficient; actual template bytes, arguments, and rendered token IDs must be hash-bound.
14. **Resident-suite meaning:** `J/query` is block gross energy divided by eight—an amortized resident-model query cost, not eight independently isolated cold requests.

### Comparison set retained

| Option | Role after addendum |
|---|---|
| (a) Fixed synthetic forced-512 | Metrology control; strongest determinism, no task-quality result |
| **(b) Frozen scored GSM8K, natural EOS ≤512** | **Headline recommendation** |
| (c) Unscored real prompts with natural stopping | Retains length realism but wastes the deterministic outcome opportunity |
| (d) Mixed chat/code/reasoning profile | Breadth follow-up; heterogeneous scoring prevents one clean `J/solved` endpoint |
| (e) One standardized question | Useful sentinel, but correctness has effective `n=1` and no defensible efficiency-quality denominator |

Tree-state note: the named model-panel survey file is absent from the current main checkout, but its tracked contents were recoverable from Git commit `934ef09b`; the model revisions, sizes, tokenizer hash, and planning rates above come from that survey.
