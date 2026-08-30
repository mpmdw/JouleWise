# Fable seat — workload design (Fable 5, fresh instance, read-only). Verbatim: first answer, then the option-(b) addendum.

# Fable 5 seat — workload consult verdict (blind, read-only)

**Recommendation (one paragraph).** Keep the *shape* of the current design — one pinned prompt per arm, greedy, EOS suppressed, exactly 512 decode tokens, ten A/B/B/A blocks, floor per cell — because that shape is what makes the paper's headline (the resolution bound and the two-gate decision) defensible to a metrologist: the workload is a known signal, and every number in `detection_floor.py`, `analysis_manifest_v3.py`, and the paper's §4–§6 is built on a per-cell, fixed-shape energy difference. What Ed is reacting to is the *content*, and the content is genuinely silly: the decode prompt is the string `"JouleWise synthetic prompt token sequence."` tokenized and repeated to 128 tokens (`joulewise/adapters/mlx_runtime.py:56,1107–1116`), and the prefill prompt is `"The plan remains easy to audit."` ×35 (`generate_configs.py:449–451`). Replace both with pinned, real, license-clean text — a single long-form instruction prompt for decode and a 512-token public-domain passage for prefill — rendered identically for both models (same-family pair ⇒ byte-identical `tokenizer.json`, so token IDs are identical by construction), hash-pinned exactly as the p256 candidate already is, and report **J per request at the declared cap as the registered quantity and J per output token as a derived column** (the field `energy_output_token_j` already exists in every summary). This costs no night time (a member's inference is 2–6 s inside a ≈160 s member slot) and no new machinery; and because D-164 re-mints every floor for the new model pair anyway, the "new family generation" penalty for changing workload bytes is already being paid. Do *not* adopt natural stopping, multi-prompt suites, or a mixed profile for `_v5`; those are `_v6` extensions that need a new estimator or an unproven mint path. One number-driven amendment: move the prefill arm from 256 to **512** prompt tokens, because the ≥3-record rule, not the effect size, is the binding constraint on the small model.

---

## 0. Facts from the tree that the four answers rest on

| Quantity | Value | Source |
|---|---|---|
| Decode workload | `prompt_tokens=128, output_tokens=512`, greedy `temp=0.0`, `suppress_eos=True`, no chat template | `generate_configs.py:683–688`; `mlx_runtime.py:294–303, 895–899`; `workloads.py:3–5` |
| Decode prompt content | seed string repeated/truncated to 128 token IDs | `mlx_runtime.py:56, 1107–1116` |
| Prefill arm | `PREFILL_PROMPT_TEXT` = 35× one sentence + final sentence, pinned by SHA and token-ID identity, `output_tokens=512` | `generate_configs.py:449–452, 690–695` |
| Design | `N_BLOCKS=10`, 4 members/block, 40/arm, 80 science members, ABBA, Holm α=0.05 m=2 | `generate_configs.py:92–95`; D-139 A2; D-157 |
| 1.5B decode (a10 r01) | phase 50.04 J, request 51.44 J, **0.1005 J/output-token**, 265 tok/s, decode 1.93 s, TTFT 0.135 s | `runs_window_a10_20260725/p2015-df-ph-decode-abs-r01/summary_metrics.json` |
| 7B decode (7bfloor r01) | phase 192.27 J, request 199.46 J, **0.3896 J/output-token**, 83.7 tok/s, decode 6.10 s, TTFT 0.283 s | `runs_window_7bfloor_20260729/sw7bfloor-df-ph-decode-abs-r01/summary_metrics.json` |
| 128-tok prefill phase | 1.5B 1.59 J; 7B 7.69 J; contrast delta 5.809930 J | same bundles; D-122 |
| Decode floor (diagnostic) | composed cell gate **7.377086 J** (absolute 3.592 / comparative 7.377, max never sum) | D-084 |
| "~1 J" in the brief | that is the *timing* term: per-member decode edge-shift bound 0.94 J (1.5B) / 1.37 J (7B); clock-anchor bound 0.37 / 0.25 J; point-scatter floors 0.29–0.49 J vs corner-widened 2.2–3.15 J | summaries above; paper §3 |
| Practical bar for phase contrasts | ≈ 5 J (= F + claim-side B, two separate gates) | D-078 cl.11; D-083; feasibility synthesis |
| Resolvability rule | ≥3 powermetrics records overlapping the phase; record spacing ≈ 0.121 s (observed 8.2–8.3 Hz vs 10 Hz requested); 37/50 128-token 1.5B prefill phases failed | paper §6; `summary_metrics.json` `median_sample_interval_s` |
| Night arithmetic | 40-member decode ABBA ≈ 106.7 min core; 40-member prefill ABBA ≈ 109.4 min; contrast pack ≈ 5.2 h; floor pack ≈ 6.3–6.5 h; fixed per-night overhead 70–84 min | feasibility CONSULT-RESPONSE:234–238; D-163 ruling |
| Member slot | ≈ 160 s wall per member (106.7 min / 40), of which inference is 2–6 s; the rest is 30 s idle baseline + cooldown (≤300 s cap) + admission | derived; `SAMPLING.idle_seconds=30`; paper §5 |
| Harness capability already present | suite items with `output_policy ∈ {fixed_budget_exact, natural_eos}`, per-item `response_sha256`, `capped` status, determinism gate compares suites item-by-item | `suite.py:44,141`; `determinism_gate.py:1–9,58`; `mlx_runtime.py:511,534` |
| Harness capability NOT present | `benchmark_import` is a *deferred* manifest section (schema sketched, no producer); suite per-item energies are gross-only attribution evidence, headline phase energy is suite-total; v3 validator pins 4 slots/2 contrasts/10 blocks/80 members | `suite.py:597,712`; `reduce.py:2643–2647`; D-163 |
| Content sensitivity at fixed shape | an **open registered question** (RQ-CONTENT-SENTINEL, AP-6, expected null, untested) | registry |
| New pair (survey rec.) | Qwen3-1.7B-4bit / Qwen3-8B-4bit, byte-identical `tokenizer.json` (`aeb13307…`), hybrid-thinking moot under raw prompt + forced 512 | `JouleWise-wt-panel2/.../00-SURVEY.md §0` |

Assumptions I could not verify from the tree are marked **[A]** below.

## 1. The options, each against the six criteria

**Common to every option:** the paper's headline is *not* "7B costs more than 1.5B"; it is the resolution bound and whether the two contrasts clear it (Table 3) plus the identical-condition null. The workload is the known signal that makes those tests interpretable. Any option that turns the workload into a random variable moves the science from "bound on the instrument" to "estimate of a population", and the floor machinery has no estimator for the latter.

### (a) Keep fixed-length synthetic (current)
- **Determinism:** bit-exact today (greedy, EOS suppressed, fixed 512; D-074 repeat-equality). Unchanged.
- **Block pairing:** exact; same prompt in all four members of all ten blocks.
- **Floor arithmetic:** decode delta ≈ 142 J vs gate 7.38 J (≈19×); prefill p256 delta projected 11.6 J vs ≈5 J bar (2.3×). Fine.
- **Prefill resolvability:** **marginal for the small model** — 1.5B TTFT 0.135 s at 128 tokens ⇒ ≈0.27 s at 256 **[A: proportional scaling, supported by the 128→4096 check within 3.3% in the feasibility trace]**, i.e. 2–3 records at 0.121 s spacing. 37/50 failed at 0.12 s; at 0.27 s I expect a material refusal rate, not zero. 7B at ≈0.57 s ⇒ 4–5 records, safe.
- **Night:** as ruled; contrast ≈ 5.2 h, floors ≈ 6.4 h each.
- **Sentence the paper can print:** "For a fixed synthetic 128-token prompt and exactly 512 greedy tokens, token-generation energy differed by Δ J (interval), clearing the cell's bound of F J." Honest, but a reader asks "what was the prompt?" and the answer is a repeated harness string. That is Ed's objection and it is legitimate — it also makes the content-sensitivity limitation (RQ-CONTENT-SENTINEL) *look* worse than it is.

### (b) Fixed pinned set of real benchmark items, cap on `max_new_tokens`, energy per query and per token
Two sub-cases that behave completely differently:
- **(b-fixed)** items run under `fixed_budget_exact` (EOS suppressed, exactly 512 tokens). Determinism: bit-exact. Pairing: exact if every block uses the same item set. Floor: same as (a) if one item per member; if k items per member in a suite bundle, energy per member scales ×k (fine), but the mint/analysis chain has only ever been smoked on single-prompt bundles (D-158/D-162) — the suite path through `whole_window`/floor extraction is a **[A] unproven** production risk with a one-day window. Resolvability: prefill of each item is a separate short phase; the suite-total prefill is a union of k sub-0.3 s intervals, each individually failing the 3-record rule unless the item prompt is ≥ ~400 tokens. Night: +2–6 s per extra item per member — negligible. Sentence: "On k pinned GSM8K items (SHA …), at a fixed 512-token budget…" Reads well; per-token column is trivially derived (denominator fixed).
- **(b-cap)** items run under `natural_eos` with a cap. Determinism: greedy so still bit-exact per item **[A: MLX greedy at batch 1 is repeat-stable — the D-074 battery shows it for forced budgets; natural-stop was never gated]**, but any single-token divergence changes length and the determinism gate refuses the block — a correct refusal, but a lost night. Pairing: the two models emit different lengths ⇒ the ABBA delta is a delta of *different amounts of work*; Gate 1 compares it to a floor built for fixed work. Floor: the identical-condition null still holds per model, but the contrast estimand is no longer "same work, different model". Resolvability: unchanged from (b-fixed). Night: shorter answers ⇒ less energy per member; a 60-token answer at 1.5B is ≈6 J decode, dangerously near the 7.38 J gate. Sentence: only "per query at cap C, with lengths L_A, L_B reported" — the per-token quantity becomes a ratio of two measured things, whose interval composition the v3 manifest does not register.

### (c) Same prompt set, natural stopping
Everything in (b-cap) plus no cap: length confound is total. The only honest handling is a slope estimand, E = a + b·T per model, contrasting b — exactly the paper's §3 "workload response" row (T ∈ {128…2048}, 8 bundles/level, n=40) but as a *contrast*. That is a regression, not an ABBA block difference: no floor exists for it, no Holm slot, no validator. New estimator + new generation + council + cold gate. Not a one-day change. Determinism: bit-exact only if greedy holds over hundreds of tokens; a divergence at token 300 in one repeat kills the block. Sentence: "per-token marginal energy b differed…" — a good sentence for a *different* paper (RQ-SHAPE-ENERGY / Q4).

### (d) Small mixed profile (short chat / long-form / code)
Determinism: fine under `fixed_budget_exact`, fragile under natural stop. Pairing: fine within a block. Floor: the short-chat cell (say 64 tokens ⇒ ≈6 J at 1.5B) sits *at* the 7.38 J decode gate — it would refuse by design, which is either the point (attribution dominance) or a wasted third of the night. Resolvability: each category's prefill is short. Night: three profiles ⇒ three floor cells per model ⇒ 3× floor nights (≈19 h of floors alone). Sentence: three sentences, one per category, with C5-W.1's Token-Shape Sufficiency Null as the framing — again a different paper (jw_mixed_v1, banked). Not for `_v5`.

### (e) Standard-length "same question to both models"
This is (a) with real content, and it is the right reading of Ed's sentence. Determinism: bit-exact (same rules as (a)). Pairing: exact. Floor: unchanged. Resolvability: unchanged from (a) unless the prompt is lengthened (see §3). Night: unchanged. Sentence: "Both models received the identical pinned question (SHA …, N tokens under the shared tokenizer) and generated exactly 512 greedy tokens; token-generation energy differed by Δ J (interval), above the cell bound F J; per output token, x vs y J." That is a sentence a reader understands and a metrologist accepts, because the signal is still known.

## 2. The confound and the pre-registered quantity

Energy is affine in generated tokens (paper §3 row 1 fits exactly this; 1.5B 0.100 J/token, 7B 0.390 J/token from retained bundles). Three consequences:

1. **The registered quantity must be the phase energy per request at a declared, forced cap** — `phase_energy_j.decode` with `output_tokens=512`, `eos_suppressed=true`. This is the quantity the floor is built for and Gate 1 tests. Per-token at a forced cap is the same number divided by 512; print it as a derived column (Table 2 already has "J per output token"), and say so.
2. **Under natural stop, per-token is the only defensible headline, and it is a different estimand** (a slope or a ratio with a measured denominator). If ever adopted, pre-register: the cap C, the realized-length distribution as a reported result (the C-004 EOS-bias rule: short/refusal answers looking cheap must be visible, never hidden), and the ratio's interval composition. Per-query under natural stop is never a fair model contrast; it is an operational-cost number (C5-W.2 territory).
3. **Declare the cap either way.** For `_v5`: "512 output tokens, forced; EOS suppressed; greedy" — the cap is the design, not a truncation.

## 3. Concrete `_v5` freeze

- **Pair:** Qwen3-1.7B-4bit / Qwen3-8B-4bit per the survey (Ed's pick); tokenizer byte-identical, so one prompt ⇒ identical token IDs for both arms; `chat_template_applied:false`, `enable_thinking: not_applicable` pinned in the model stanza.
- **Decode arm:** one pinned real prompt. My preference is a self-authored long-form instruction (public domain by construction, no license or contamination note needed) that genuinely warrants ≥512 tokens — e.g. "Explain, step by step and with worked numbers, how a laptop's power-monitoring counter can misattribute energy between prompt processing and token generation…" — so forced 512 tokens is not babble. If Ed wants a *named* benchmark item: one MT-Bench "writing" item (Apache-2.0) is the cleanest; GSM8K/MMLU items are short-answer and would be forced to babble past ~100 tokens, which is worse than synthetic. Realized prompt length is recorded, not padded; `planned_prompt_tokens` = the realized count under the pinned tokenizer (the harness already refuses on mismatch, `cli.py:1184–1190`). Greedy, `suppress_eos=True`, 512 tokens. **One prompt per block, identical across all 10 blocks** — distinct-prompt suites are `_v6`.
- **Prefill arm: 512 prompt tokens, not 256.** Arithmetic: small-model TTFT at 128 tokens is 0.135 s ⇒ ≈0.27 s at 256, ≈0.54 s at 512 **[A: proportional]**; at 0.121 s record spacing that is 2–3 vs 4–5 overlapping records. The paper's own negative result says 37/50 failed at 2 records. Effect size at 512 ≈ 4 × 5.81 ≈ 23 J vs ≈5 J bar (≈4.6×; **[A: extrapolated, no long-prompt large-model corpus exists**, as the paper §6 already discloses for 256]). Cost: +0.3 s per member. Content: a pinned public-domain passage (e.g. a Project Gutenberg paragraph) trimmed to exactly 512 tokens under the shared tokenizer, pinned by text SHA and token-ID list exactly as `prefill_prompt_candidate.json` does now. Keep `output_tokens=512` on the prefill members (as today) so decode floors from the same members remain usable.
- **Registered quantities:** `phase_energy_j.decode` and `phase_energy_j.prefill` per request at the forced cap (Holm m=2 family unchanged, D-139 A2); `energy_output_token_j` and J per prompt token as derived columns.
- **Night arithmetic (contrast night):** 10 blocks × 2 arms × 4 members = 80 science members; per-member slot ≈160 s ⇒ decode arm ≈107 min, prefill arm ≈110 min (inference 2–6 s of each slot, so the workload change moves this by < 5 min total); + 3 references + pre/post brackets + fixed overhead ≈ 70–84 min ⇒ **≈5.2 h**, identical to `_v4`. Floor nights ≈ 6.3–6.5 h per model, also unchanged — and they must be re-collected for the new pair regardless of workload, which is why the workload change is free *now* and expensive later.
- **Desk cost:** prompt authoring + tokenizer trim + SHA pins + generator constants (`PROMPT_SENTENCE`, `prefill_family_definition`, `workload_for`) + `analysis_manifest_v5` sibling values + D-074 repeat-equality on the new pair. Inside D-164's ≈2 Sol-days; adds hours, not days.

**Strongest counter-argument to my recommendation.** Changing content at fixed shape buys *nothing measurable*: on a dense transformer the per-token compute is content-independent, so the energy numbers will be the same to within the floor whether the prompt is a harness string or a Gutenberg paragraph — the project's own registry says exactly this (RQ-CONTENT-SENTINEL, expected null). The synthetic prompt is redistribution-safe, tokenizer-portable, and already pinned; a "real" prompt invites the reader to think the paper measured something about *that question*, which it did not, and the prefill p256→p512 change discards D-122's Ed-ruled sizing and the paper's already-written "Why 256 prompt tokens" section. The honest reply: the change is for the reader, not the instrument — and the p512 move is for the instrument (the 3-record rule), not the reader. If Ed prefers to keep D-122's 256, the decode-content swap alone still answers his objection at zero cost.

## 4. Which registered RQs each option answers

- **(a) / (e) fixed-shape single prompt:** RQ-ATTRIBUTION-DOMINANCE (the capstone primary; needs the fixed-shape null and floors); C5-1.1 in its permitted pairwise form; RQ-SHORT-PREFILL-RESOLVABILITY (the printed negative result, re-tested at the new length); RQ-MAC-BASELINES (per-profile baselines). (e) additionally makes C5-I.5 (prompt-template sensitivity) and RQ-CONTENT-SENTINEL *statable* as limitations with a real-content reference point, but does not answer them.
- **(b-fixed) pinned benchmark items at fixed budget:** all of the above plus C5-I.1 (external benchmark energy signatures) at L1 only, and RQ-HUMANEVAL-IMPORT-SMOKE / RQ-EXTERNAL-MARKED-RUNNER as capability claims; correctness stays quarantined (C-004/C-014), so C5-1.9 and C5-I.2 remain unanswered.
- **(b-cap) / (c) natural stop:** C5-W.2 (thinking/emitted-token inflation — moot for a non-thinking pair), RQ-SHAPE-ENERGY and Q4's per-token slope if run as a regression, RQ-ENERGY-VARIANCE only under sampling (not greedy). They do **not** answer RQ-ATTRIBUTION-DOMINANCE cleanly because the contrast no longer holds work fixed.
- **(d) mixed profile:** C5-W.1 (Token-Shape Sufficiency Null, AP-4), C5-W.3 (category ranking stability), RQ-SESSION-SHAPE, RQ-ORDER-POSITION — the jw_mixed_v1 programme, banked, multi-night, not the paper.

Net: only (a)/(e) and (b-fixed) serve the paper's registered primary question; (e) is (a) with content a reader can respect, and the prefill length should be set by the resolvability count, which is the one place the current design is actually thin.

---

# Fable 5 seat — addendum: option (b) developed as the leading path

Read-only; facts re-verified against the tree before writing. Assumptions I could not verify are marked **[A]**.

## New facts that bear on (b)

| Fact | Source |
|---|---|
| Qwen3-1.7B-4bit and Qwen3-8B-4bit are now mirrored locally; `tokenizer.json` SHA-256 identical (`aeb13307…`) | `ls /Users/edr/jw_models/mlx-community/`; `shasum` |
| Qwen3 chat template contains `enable_thinking` and `<think>` handling (4116-char template on the mirrored 4B) | `Qwen3-4B-4bit/tokenizer_config.json` |
| The harness has **no chat-template code anywhere** (`grep chat_template\|apply_chat_template\|enable_thinking joulewise/` → nothing) | tree |
| But suite items may carry `prompt_token_ids` (ids-native, D-046), so a template can be rendered at the desk and the *token IDs* pinned; the adapter never needs the template | `suite.py:590–600`; `mlx_runtime.py:429–447` |
| `output_policy: natural_eos` already routes to `suppress_eos=False` for suite items; the forced-512 path is only the non-suite branch | `mlx_runtime.py:511` vs `:294–303` |
| Item status `capped` (emitted == cap) exists; determinism gate accepts `succeeded`/`capped` but refuses a status mismatch or hash mismatch across repeats | `suite.py:141`; `determinism_gate.py:58,454,591` |
| `scoring.*` and `benchmark_import` are **deferred** manifest sections: validated as absent, no producer, no consumer | `suite.py:597, 706–712` |
| Only scorer in the tree: `score_response` for the affine ladder (exact integer) | `workloads.py:109` |
| Suite per-item energies are gross-only attribution evidence; headline `phase_energy_j` is suite-total via multi-interval pairing | `reduce.py:2643–2647` |
| AP-5 / C5-1.9: energy-per-correct = window energy / correct count **only after** a binomial guard (lower bound ≥3 correct), correctness quarantined (C-004), malformed items count as incorrect (D-047.6) | `docs/contracts/analysis_plans.md:220–235` |
| General "joules per solved task" is **killed** (C-003/C-004, RQ-INTELLIGENCE-PER-JOULE); the controlled ladder is the surviving minimal form | bank:80; registry |
| v3 analysis manifest pins 4 slots / 2 contrasts / 10 blocks / 80 members; D-162 found a new admission-path family costs 7–10 Sol-days | D-163 ruling; D-162 |

## (i) The defensible pre-registered quantity

Three quantities, in strict order of claim strength:

1. **Registered, claim-gated:** `phase_energy_j.decode` per member, where a member is *the pinned k-item set attempted under cap C* (suite-total). The ABBA block difference of this quantity is exactly what `abba_delta` and the floor cell machinery already take; Gate 1 compares it with the cell floor, Gate 2 with zero. Estimand in words: "energy to attempt this fixed question set under this cap on 8B minus 1.7B." Under greedy decoding the realized token count per model is a *constant of the design* (same every repeat), so this is a fixed-work contrast after all — just fixed by the model's own stop behaviour rather than by force. That is the key reason (b) survives the floor arithmetic where (c) does not.
2. **Derived, labelled:** J per emitted token = suite energy / realized emitted tokens (the denominator is deterministic and recorded per item; `energy_output_token_j` already exists). Print both models' realized token totals next to it; the ratio's interval is the energy interval scaled by a constant.
3. **Labelled co-outcome, never a gate:** `E_suite / n_correct` per model, "on this pinned set". Under greedy decoding `n_correct` is not a sample from anything — it is a property of the set — so the AP-5 binomial guard has nothing to bound at the block level; keep the guard's *spirit* as a design rule: choose k so the expected weaker-model correct count is ≥3 (else the ratio is `not estimable`, the AP-5 wording). Its uncertainty interval is the energy interval divided by the constant. Never contrast the two ratios through Gate 1/2; the registered contrast is quantity 1.

Interaction with the floor: the floor cell is (model, workload); the null ABBA and the absolute repeats must run *the same suite*, which the re-minted `_v5` floor packs would do anyway. Duration rises from 2–6 s to ≈10–30 s per member (numbers below); the bracket pulse envelope must cover that window or members refuse `duration_outside_calibrated_envelope` **[A: envelope bounds in the current acceptance edition not checked]**.

Per-item outcome classes, pre-registered: `correct` / `incorrect` / `truncated` (status `capped` *and* no parsable final answer) / `malformed` (parsable-format failure, counted as incorrect per D-047.6). Report the full 4-way table per model. Prefill: per-item prompt processing (~100–200 tokens, 0.1–0.2 s) fails the ≥3-record rule item by item, and I could not verify whether the multi-interval union is counted per interval or per union **[A]** — so the paper's prefill contrast should stay the separate pinned-passage arm (p512, my first answer §3). Holm m=2 family is then: decode-suite contrast + prefill-passage contrast. D-139 A2 survives unchanged.

## (ii) Benchmark choice

| Candidate | Deterministic scorer | License / pinning | Fits a few-hundred-token cap (non-thinking) | Small-vs-large spread in one family | Verdict |
|---|---|---|---|---|---|
| **GSM8K** (test split, `#### N` gold) | exact-match on final number after normalisation (strip commas/`$`, compare as rational) — trivially pinnable | MIT **[A: verify at pin time]**; hash-manifested subset per the C-005/C-015 rule | yes: non-thinking answers run ~80–250 tokens | Qwen3-1.7B vs 8B non-thinking: a real gap is expected **[A: I could not verify figures from the tree; treat any number as unverified until a shakedown run]** | **Use it** |
| MMLU / ARC / BoolQ (letter answers) | exact-match, easiest scorer | MIT/CC | answers are 1–5 tokens ⇒ decode energy ≈0.1–0.5 J per item, i.e. *at the floor*; the workload becomes prefill-dominated | large | **No** for a decode contrast |
| HumanEval / MBPP | requires code execution — sandbox, timeouts, nondeterministic environment; the bank already limits these to "prompt exemplars only" | MIT | yes | moderate | No |
| MATH / MATH-500 | LaTeX equivalence checking is not "pinned trivial" | MIT | often > 400 tokens | large | No for `_v5` |
| MT-Bench | judge-scored | Apache-2.0 | n/a | n/a | No |
| **In-repo `affine_mod_ladder_v1`** | exact integer, already in `workloads.py`; seed-derived ⇒ contamination-free by construction | internal | yes (16-token answers) | designed difficulty axis | **Use as the control leg** if a second leg is affordable; otherwise pin it as the `_v6` follow-on — this is literally the C-004 design |

GSM8K is the only external set that gives a deterministic checker, a decode-heavy answer that fits a cap, and a plausible in-family spread. Pin: `openai/grade-school-math` test split at a named commit, a selection rule (e.g. SHA-ordered first k of item ids), `selected_item_ids_sha256`, `canonical_subset_json_sha256`, `prompt_template_sha256`, and per-item `prompt_token_ids` — the deferred `benchmark_import` sketch in `suite.py` already names every field.

## (iii) Distinct questions per block; bit-exact repeats

- **k = 8 items per member, the same 8 in every member of every block.** The block is the repeat unit; the item set is part of the condition. Varying items across blocks would fold item variation into the block scatter and make the floor cell ill-defined (which "workload" does the null calibrate?). If Ed wants coverage, raise k (16) rather than vary sets.
- **Cap C = 384 tokens per item** (natural EOS below it). Rationale: comfortably above expected non-thinking GSM8K lengths, so truncation is an exception not a mode; a tighter cap (256) would bias against the longer-writing 8B (trap v-4).
- **Order:** pinned per manifest (`ORDER_POLICY_MANIFEST`), identical in every member; serial execution with per-item markers is what `reduce.py` already assumes.
- **Bit-exact repeats:** greedy (`temp=0.0`) on MLX at batch 1 gave repeat-equality in the D-074 battery for forced budgets; the same property makes the stop point identical, so each item's `response_sha256`, emitted count and status are constants **[A: never demonstrated for natural-stop runs on this pair — G2 on the shakedown night must show 4 identical suite hashes before the transaction]**. Any divergence flips a status or hash and the determinism gate refuses the block — a correct refusal that costs a night, which is why the shakedown check is non-optional.
- **Thinking off, pinned by IDs not by flag:** render each prompt at the desk with the tokenizer's chat template, `enable_thinking=False` (Qwen3 inserts an empty `<think>\n\n</think>` block), record `chat_template_sha256`, `enable_thinking=false`, `rendered_prompt_sha256`, and pin the resulting `prompt_token_ids`. Because `tokenizer.json` is byte-identical across the pair, both models receive identical IDs; **verify the two repos' `chat_template` strings hash-equal [A: only the 4B template was inspected]**. The adapter then runs ids-native and needs no template code. Do not rely on `/no_think` in the user turn — it is a soft directive, not a pinned setting.
- **Model self-terminates in thinking anyway?** With thinking disabled by template the model cannot open a `<think>` block legitimately; if it emits `<think>` tokens regardless, the item is `malformed` by rule, and the rate is reported.

## Harness code path (what exists vs. what must be built)

Exists at runtime: suite bundles, `natural_eos` + `capped`, ids-native prompts, per-item hashes/markers, determinism gate over suites. Missing on the *claim path*: (1) a GSM8K scorer + `scoring.*` producer/consumer (deferred today); (2) `benchmark_import` producer; (3) the outcome table in the analysis manifest (`analysis_manifest_v5` sibling — already required by D-164); (4) proof that suite bundles pass floor extraction, the arm-readiness/mint path and `whole_window` end to end — never smoked (D-158/D-162 used single-prompt bundles); (5) bracket-envelope coverage for 10–30 s members. D-162 priced a new admission-path family at 7–10 Sol-days; D-164 budgeted ≈2. Honest estimate: **+5–8 Sol-days over the D-164 plan, so the transaction night moves from ≈09-01/02 to ≈09-06/09** **[A: estimate]**.

Night arithmetic (contrast night): 80 members; inference per member ≈ 8 items × ~150 tokens: 1.7B ≈ 1200 tok / 265 tok/s ≈ 4.5 s (+8 prefills), 8B ≈ 1200 / 84 ≈ 14 s (up to ~37 s if every item hits the 384 cap). Member slot stays ≈160 s (idle baseline + cooldown dominate) ⇒ decode arm ≈ 110–115 min, prefill-passage arm ≈ 110 min, +references/brackets/overhead ⇒ **≈5.3–5.5 h**, i.e. unchanged within noise. Energies: 1.7B suite decode ≈ 1200 × 0.10 ≈ 120 J, 8B ≈ 1200 × 0.39 ≈ 470 J **[A: per-token rates borrowed from Qwen2.5 1.5B/7B]**; Δ ≈ 350 J against a decode gate of order 7 J — Gate 1 is not in doubt; the design's science is entirely in the co-outcome table and the per-token column.

## (iv) Honest sentence and the RQ it answers

> "On eight pinned GSM8K items (subset SHA …), each model decoded greedily with thinking disabled under a 384-token cap. Attempting the set cost the 8B model Δ J more token-generation energy than the 1.7B model (interval […], above the cell's bound of F J); per emitted token, x vs y J over N₈ and N₁.₇ tokens. On this set the 8B model answered a/8 correctly with t₈ truncations, the 1.7B model b/8 with t₁.₇, so energy per solved item was p vs q J — a property of this pinned set on this machine and software stack, not a capability or efficiency ranking."

Registry/bank mapping: the bank's efficiency-vs-quality question is **C5-1.9 "energy per correct answer" (AP-5, C-004/C-014 quarantine)**; its general form **RQ-INTELLIGENCE-PER-JOULE is killed**. The GSM8K leg is C5-1.9's *ecological* variant and also lands on **C5-I.1** (external benchmark energy signatures, "no benchmark capability or accuracy claim") and **C5-I.2** (difficulty strata — n/a for GSM8K, no labels). Binding riders: **C-023-OUTPUT-IDENTITY** (fixed output count is not fixed work; here output counts differ by design and must be printed) and the **C-004 EOS-bias rule** (short wrong answers look cheap; the stop-reason table is part of the result). **RQ-ATTRIBUTION-DOMINANCE** is still served by the null blocks and the prefill arm; the decode-suite contrast is too far above the floor to exercise it — that was already true of the 512-token synthetic design.

## (v) Trap list

1. **Contamination.** GSM8K is almost certainly in Qwen3 pre-training; the bank rules such sets "shape, not correctness". Pre-register accuracy as a set property; forbid "8B is better at math". Mitigation: pair with the affine control leg (`_v6` if not now), and prefer a perturbed/held-out variant (GSM-Symbolic-style) if a license-clean pinned one is available **[A]**.
2. **Thinking-mode blowups.** Without a pinned `enable_thinking=False` rendering, Qwen3 emits hundreds of `<think>` tokens and hits the cap on every item — energy becomes "cap × rate" and accuracy collapses to truncations. Pin the rendered IDs; count any `<think>` emission as `malformed`.
3. **Answer-format parsing.** Pin the extractor (last `#### N` or last number in the final line; normalise commas, `$`, trailing period; compare as rationals); pre-register `unparsable ⇒ incorrect` (D-047.6). Publish the extractor's SHA and the raw responses (they are already bundle bytes).
4. **Cap-truncation bias against the large model.** Larger models write longer solutions; a tight cap truncates them first, tagging them incorrect *and* pinning their energy at the cap. Set C above the expected length distribution (384 here), report truncation rate as its own class, and never fold truncations into "incorrect" in the headline.
5. **EOS-bias in energy.** A model that gives up early is cheap per query; per-token and the stop-reason table are what keep the energy sentence honest.
6. **Nondeterminism under natural stop.** One diverging token changes length and status ⇒ block refused. Shakedown repeat-equality on the full suite is the gate (D-162 G2).
7. **Per-item phase claims.** Item prefill windows are 1–2 records: no per-item prefill joules, ever (RQ-SHORT-PREFILL-RESOLVABILITY). Per-item *decode* windows (~0.5–2 s, 4–15 records) are attribution evidence only (`reduce.py:2643`), not independent replicates.
8. **Template drift.** Two repos, two `tokenizer_config.json`; hash both templates and refuse on mismatch — the determinism gate's five tokenizer keys cannot see it (survey §0).
9. **Envelope coverage.** 8B members at the cap can run ~40 s; the bracket pulses must cover that duration or members refuse.
10. **Schedule.** The missing scorer/import/manifest/mint-path proof is the real cost; it is desk work, but it lands on the mint path, which D-157 R-2 says must refuse rather than tolerate an unvalidated family.

## Comparison set, one line each

(a) synthetic fixed-shape: strongest metrology, weakest reader; (e) real content, fixed shape: (a) with a defensible prompt, zero code; **(b) as above: fixed-work-by-determinism contrast plus a labelled outcome table — the most interesting paper, at +5–8 Sol-days and one shakedown-proved gate**; (c) natural stop without a fixed set: no estimator, not for `_v5`; (d) mixed profile: three floor cells, ~3× floor nights, `_v6`.

If Ed takes (b), my recommendation is (b) for the decode arm with k=8 GSM8K items at C=384, the pinned-passage p512 prefill arm kept as the second Holm slot, the affine ladder registered as the follow-on control leg, and the transaction night re-dated honestly rather than squeezed.