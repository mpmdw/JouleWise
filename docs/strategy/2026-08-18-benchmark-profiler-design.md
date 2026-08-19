# Benchmark-prompt workload profiler: pilot design memo

**Status:** desk design only; no inference or quiet-machine capture was run.

## Recommendation

Use the **GSM8K test split** as the first benchmark-prompt workload-profiler
family. A benchmark item whose source bytes, renderer, chat template, and decode
policy are pinned is a fixed prompt. The primary unit is **gross request energy
per completed item** under that policy, not energy per correct answer and not a
synthetic fixed-token workload. Accuracy is a quarantined annotation only.

**Important tokenizer result: the cross-model prompt-token matching problem
vanishes for the present Qwen pair.** The local Qwen2.5-1.5B-Instruct-4bit and
Qwen2.5-7B-Instruct-4bit tokenizers have identical `tokenizer.json` bytes
(`sha256:a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf`),
identical vocabulary size (151,643; `len(tokenizer)=151,665`), special tokens,
and chat template. They emitted identical IDs for an empty string, a plain
GSM-style prompt, and a 43-token rendered chat prompt. The two
`tokenizer_config.json` files differ in bytes, but not in the observed encoding
behavior. Thus any byte-identical rendered GSM8K prompt has exactly the same
prompt-token count on both stacks. A future cross-tokenizer comparison would need
a token-count-matched subset; this same-Qwen-tokenizer comparison does not.
Realized output lengths may still differ by model and remain part of the item cost.

## 1. Benchmark choice

### Primary: GSM8K test, as a frozen-subset import

The candidate source is the OpenAI `grade-school-math` repository's
`grade_school_math/data/test.jsonl`. This is never a live benchmark fetch:
before pilot, record the upstream repository commit, URL, retrieval time, license
notice, file SHA-256, line count, and normalized-newline policy; cache the
received bytes read-only. Define source IDs as `gsm8k_test_0000` through
`gsm8k_test_{N-1:04d}` in byte-file line order. These are reproducible import
locators, not alleged upstream identifiers.

GSM8K is the first choice because it is a single small JSONL test file, is
versionable/citable once commit-pinned, has short English grade-school-math
questions, and has a bounded natural answer instruction. It supplies a recognizable
natural workload without making an accuracy claim. Its prompt-length distribution
should suit a modest M3 Max window, subject to the data gate below.

The public reference answer is never injected. Freeze these canonical messages:

```text
system: You are a careful grade-school math solver.
user: Solve this problem. Return only the final numeric answer, with no explanation.

{question bytes exactly as imported}
assistant: [generation begins]
```

Render with the checked Qwen chat template and retain rendered UTF-8 bytes,
token IDs, and hashes. Decode policy: greedy (`temperature=0`, `top_p=1`), normal
EOS, `max_new_tokens=64`, no tools, retrieval, retries, answer-aware stops, or
forced padding. A completed item is a successfully captured request with terminal
reason and response bytes. EOS, cap, malformed, and incorrect statuses are
recorded; the primary energy-per-completed-item analysis does not silently delete
them.

This is a new profiler purpose, not a revision of frozen v2. D-041 historically
favored HumanEval as a first *plumbing* import because long completions clear an
item floor readily. Here, short natural prompts and bounded answer instructions
are the object of study; HumanEval stays a useful plumbing smoke. MMLU is not the
first profiler target because subject-specific templates, choice labels, and
heterogeneous subsets add formatting/category confounding.

### Criteria and gates

The frozen import needs source commit/file hash/license/line map, renderer and
template bytes, and tokenizer artifact hashes. Every selected prompt must fit with
a 64-token reserve; each stratum needs at least four eligible items and at least
three strata must be populated. The import has no reference answer in the request
and no stochastic decoding. GSM8K may occur in model training, affecting
correctness, EOS, and response length. That does not invalidate a descriptive
claim about energy spent completing pinned requests, but it rules out novelty or
generalization claims. If it fails these gates, select a separately versioned,
single-file, short-answer fallback; never mix it into GSM8K.

## 2. Executed tokenization analysis

Using `/Users/edr/code/JouleWise/.venv/bin/python` and local-only
`transformers.AutoTokenizer`, I loaded:

* `/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`
* `/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit`

The shared relevant artifact hashes are:

| Artifact | SHA-256 (both stacks) |
|---|---|
| `tokenizer.json` | `a8506e7111b80c6d8635951a02eab0f4e1a8e4e5772da83846579e97b16f61bf` |
| `vocab.json` | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |
| `merges.txt` | `8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5` |
| `special_tokens_map.json` | `76862e765266b85aa9459767e33cbaf13970f327a0e88d1c65846c2ddd3a1ecd` |
| `added_tokens.json` | `58b54bbe36fc752f79a24a271ef66a0a0830054b4dfad94bde757d851968060b` |

This checks actual local artifacts and encoder behavior, not just family labels.
The future pack generator must repeat equality checks across every rendered source
item and refuse a mismatch.

### Distribution result: pending source bytes, not inferred

I attempted retrieval to `$TMPDIR` with
`curl --fail --location --max-time 30`. It failed before transfer with
`curl: (6) Could not resolve host: raw.githubusercontent.com`. No GSM8K cache was
found in the main repository or standard local cache locations inspected.

Therefore **there are no honest prompt-token distribution statistics, realized
stratum counts, or exact candidate item IDs in this memo.** They are not estimated
from remembered GSM8K values. Ed must authorize/provide a commit-pinned file before
selection; the exact procedure is:

1. Strictly parse JSONL; retain line number, raw question UTF-8 bytes, and per-line
   SHA-256. Refuse malformed records and duplicate hashes.
2. Render the pinned prompt and compute both tokenizers' IDs. Refuse a mismatch,
   context-limit violation, or unstable byte re-render.
3. Emit `n`, min, max, mean, SD, p05/p25/p50/p75/p95, and a 16-token histogram of
   rendered prompt-token counts. These are the required distribution statistics.
4. Create four strata from empirical prompt-token quartiles. Break ties by
   `(prompt_tokens, line_sha256)`; freeze the numeric half-open ranges and counts.
5. Within each stratum, sort by
   `sha256("gsm8k-profiler-v1" || line_sha256)` and select the first four records.
   The first selected record in each stratum becomes the null-block anchor.

The proposed candidate matched subset is **16 exact items, four per empirical
prompt-token quartile**. Its IDs become exact only after authenticated source bytes
arrive. It is automatically prompt-token matched across this Qwen pair; no
post-hoc cross-model matching or tokenizer adjustment is allowed.

## 3. Pilot design

The pilot is sizing and instrument characterization, not a result campaign. It
measures item-level energy variance, the identical-item comparative-null floor,
prompt-length/energy slope and residual, cap/EOS and output-length behavior, and
actual request duration. These size the frozen production design; they may not be
used to choose more favorable benchmark items.

The unit is one completed benchmark-item request with gross request energy over
the pinned boundary. Secondary fields are prompt/emitted tokens, wall time, mean
power, terminal status, response hash, order position, preceding item, resident
model state, and thermal/power trace metadata. `J / emitted token` is secondary:
prompt counts are exactly matched in this Qwen pair, while outputs can legitimately
differ.

### First pilot: one stack, 16 items, four item-null ABBA blocks

Run the 1.5B stack first; it learns workload/floor shape before any 7B spend.

| Component | Design |
|---|---|
| Main items | 16: four deterministic selections per empirical prompt-token stratum |
| Main observations | Each item once; random order constrained so no stratum is adjacent more than twice |
| Null anchors | First selected item in each stratum |
| Item-level floor | Four identical-item ABBA blocks: `A=item`, `B=same item`, `B=same item`, `A=same item`; retain signed `mean(A)-mean(B)` |
| Total requests | 16 main + 4 blocks × 4 = **32** |
| Decode policy | Pinned chat bytes; greedy, `temperature=0`, `top_p=1`, normal EOS, `max_new_tokens=64`; no retry substitution |
| Repeats | ABBA members are deliberate floor observations, never independent item content; item/block are random effects in sizing |

The null uses precisely the same item and policy in all A/B slots, exposing actual
item-level capture/order/thermal noise. Within-block ABBA cancels first-order
linear drift. It does not pretend distinct questions are exchangeable. This future
floor family is separate from D-117 v2 because boundary and length mixture differ.

### Wall-time estimate (no inference performed)

The repo's 2026-07-29 probe reports 512 generated tokens in 2.05 s (1.5B) and
6.40 s (7B): about 250 and 80 decode tokens/s. At the 64-token cap, decode-only
upper bounds are ~0.26 s and ~0.80 s, before TTFT/prompt prefill. Natural answers
will usually be shorter, hence recorded rather than assumed.

Claim-grade individual-request overhead dominates: comparable D-117 members were
92.7 s for 1.5B and estimated 97 s for 7B, including idle, arm, settle,
calibration, and teardown. Until a profiler timing smoke proves otherwise:

| Estimate | 1.5B | 7B, if later authorized |
|---|---:|---:|
| One captured item | ~93 s | ~97 s |
| Four-member identical-item ABBA block | ~6.2 min | ~6.5 min |
| 32 request members only | ~49.4 min | ~51.7 min |
| With D-117-like staging/calibration allowance | ~2.7 h | ~2.75 h |
| With 20% operational margin | ~3.2 h | ~3.3 h |

The final two rows are conservative extrapolations from another fixed-output pack,
not measurements. One 1.5B pilot fits the usual 2–4 h compact-window envelope;
the 7B profile should wait for the frozen production decision.

### What freezes after pilot

Produce one pilot receipt/report with raw bundle pointers and stratum-wise energy
and wall-time summaries; robust prompt-token slope/residual plus stratum
sensitivity; completed/capped/malformed/EOS and emitted-token distributions; four
ABBA deltas and floor input; item variance after prompt-length adjustment; and
actual request duration. Then freeze source hash, renderer, tokenizer hashes,
selected IDs, strata, policy, boundary, estimator, floor recipe, order generator,
replication count, and exclusion vocabulary before production. If length span,
cap rate, or floor makes the slope unresolved, refuse the claim or create a new
versioned family—do not mutate this one.

## 4. Modular integration, without touching frozen v2

Create a future `benchmark_profiler` pack family with an immutable import receipt
and its own absolute/comparative floors. Do not borrow a synthetic v2 floor merely
because the Mac is the same: D-117 floors belong to their pinned boundary.

| New work | General machinery reused |
|---|---|
| Strict JSONL importer; source commit/file-hash/license receipt; local cache and line-ID map | Bundle custody, content/model/runtime provenance, validation, backup/receipt flow |
| Renderer, distribution/stratifier, selection receipt, byte re-render check | Prompt provenance, token/stop/response hashes, item markers/windows, order/cache metadata |
| Greedy response status and optional answer scorer isolated from energy eligibility | Status vocabulary, raw response retention, reducer pipeline |
| Identical-item ABBA generator and profile-specific floor extractor | ABBA/common-mode concepts and floor discipline, but a new workload-bound floor row |
| Item-energy/length-covariate profiler reducer | Frozen analysis manifests, validity gates, gross/phase energy fields |

This extends D-040/D-041's generic suite mechanism rather than adding bespoke
inference plumbing. The generator must refuse a live URL, source-hash mismatch,
duplicate ID, tokenizer mismatch, unpinned template, or a requested write inside
an existing frozen family.

## 5. Risks and limits

* **Contamination:** training exposure can affect answer content/length; disclose
  it, but energy per completed pinned request remains a valid descriptive claim.
* **Greedy length variance:** greedy removes sampling variance, not item/model
  length variation. The item unit absorbs it; identical-item ABBA cancels it
  within the floor block, not between questions.
* **Length confounding:** prompt length likely dominates prefill and may correlate
  with wording/difficulty. Stratify, model the token slope, and do not call raw
  across-item means a difficulty effect.
* **Output coupling:** do not condition primary energy on correctness. Report cap
  status and emitted tokens rather than hiding format failures.
* **Per-token scope:** it is a derived view, not a replacement for item energy.
  Cross-tokenizer work needs a frozen matched subset; unmatched per-item analyses
  legitimately include tokenizer cost.
* **Source/template drift:** URL movement, Unicode/newline normalization, or a
  chat-template upgrade changes the prompt and must fail closed on its receipt.
* **Resolution/cost:** natural answers may have sub-second compute while capture
  remains costly; an item-level floor is mandatory and below-floor is an honest
  refusal, not permission to pool unlike items.
* **Repeated-item effects:** record cache state and schedule ABBA blocks; never
  reuse their responses as independent main observations.

## Open questions for Ed

1. Can Ed authorize/provide a specific commit-pinned GSM8K test file so the
   distribution receipt and exact 16 IDs can be generated?
2. Is a 1.5B-only first pilot approved (recommended), with a 7B pack generated
   after freeze, or should both stacks be funded despite doubling the budget?
3. Should cap-terminated responses remain in the headline `completed` estimand
   (recommended, with disclosed rate), or define EOS-only completion separately?
4. Does Ed want the proposed final-number/no-chain-of-thought prompt, or a
   natural-reasoning prompt with a larger cap? The latter is a different family.

