# qwen4_exp port: end-to-end validation (GOAL item 7)

Status, 2026-11-05: the harness, the hosted-reference client, the pinned items and the tests are built and pass on stub generators, on a tiny random mlx-lm hybrid model, on a tiny random official `transformers` qwen4_exp model, and on one benign episode through the ALIGN kit's `run_episode`. No paid API has been called. No real Flash-Next weights have been run. Every model number below is a design threshold, not a result.

Lane: `lane/2026-11-05-qwen4exp-port-evals`. This lane designs against the reference and the adapter contract below. It does not wait for the Sol port (`lane/2026-11-05-align-flashnext-port`) or the Opus twin (`lane/2026-11-05-align-flashnext-twin`).

## 1. What is here

| Path | Role |
|---|---|
| `scripts/qwen4exp_e2e_eval.py` | The end-to-end harness: a pluggable adapter, seven stages, derived thresholds and a results JSON |
| `scripts/qwen4exp_hosted_reference.py` | The hosted-reference client: `plan` and `collect`, which are dry-run by default, and an offline `compare` |
| `scripts/qwen4exp_e2e_build_items.py` | Rebuilds the item file from the pinned sources |
| `configs/qwen4_exp_port/e2e_items.json` | The pinned items. File sha256 is `b9dfdab714d4c2fe70517f6152e06c2f7270a3ebd016b927883a51b5c8f6d0ae` |
| `configs/qwen4_exp_port/hosted_reference_prompts.json` | Twelve fixed prompts for the logprob comparison. sha256 `ef5de292...b688` |
| `tests/fixtures/qwen4exp_chat_template.jinja` | A byte copy of the official template, sha256 `c3cf9e34...1041` (`.engine/` is not tracked) |
| `tests/test_qwen4exp_e2e_eval.py`, `tests/test_qwen4exp_hosted_reference.py` | 50 unittest tests |

## 2. Hosted providers (researched 2026-11-05)

| Route | Model id | Same weights as the open checkpoint? | Price per 1M tokens (in / out) | Precision | Logprobs | Turning thinking off |
|---|---|---|---|---|---|---|
| Alibaba Model Studio / Qwen Cloud (DashScope OpenAI-compatible, intl) | `qwen3.8-flash` | **No.** This is the production model, "based on" Flash-Next, with 1M context and built-in tools. No source shows it is the same artifact. | $0.15 / $0.47; implicit cache $0.016 | not stated | Documented: `logprobs` plus `top_logprobs` in [0, 5] for listed families. `qwen3.8-flash` is not named, and one line says "only Qwen3 non-thinking". **Unconfirmed; collect probes it.** | top-level `enable_thinking: false`, or `reasoning_effort: "none"` |
| OpenRouter, Alibaba endpoints only | `qwen/qwen3.8-flash` | No (the same production model) | $0.15 / $0.47 | "unknown" in endpoint metadata | `logprobs` and `top_logprobs` are listed in `supported_parameters` for both Alibaba endpoints | `reasoning: {enabled: false}`; pin with `provider.only=["alibaba"]` and `require_parameters=true` |
| Featherless AI (the only Hugging Face Inference Provider listed) | `Qwen/Qwen3.8-Flash-Next` | Yes (the open weights) | $0.15 / $0.50; cached $0.03 | **FP8** (model page) | **Not documented.** The `/v1/completions` example returns `logprobs: null`. `seed` is documented as "not reliable". | raw `/v1/completions` prompt, or `chat_template_kwargs` |
| TensorX via Requesty (EU) | `tensorx/qwen3.8-flash-next` | open weights per the listing | $0.20 / $0.50, plus 5 % pay-as-you-go | not stated | not documented | not documented (`chat_template_kwargs` assumed) |
| Lyceum, CanopyWave, FlexAI (aggregator listings) | various | unclear | about $0.15-0.21 / $0.50-0.53 | unknown | not documented | not documented |
| Together, Fireworks, DeepInfra, SiliconFlow | none found serving Flash-Next | | | | | |
| Self-hosted vLLM (rented GPUs) | `Qwen/Qwen3.8-Flash-Next` | yes, if it loads the official BF16 repository | GPU rental (8 x 80 GB for BF16) | your choice: BF16, no MTP, `--kv-cache-dtype auto` | completion logprobs (up to `--max-logprobs`, default 20), `prompt_logprobs`, `return_tokens_as_token_ids` | raw prompt |

The vLLM recipe serves NVFP4 by default, with an FP8 KV cache, an FP8 indexer KV and MTP speculative decoding. Hosted vLLM-class endpoints may therefore differ from BF16 in more than the weight format.

**Conclusion.** As of today, no endpoint that serves the open weights documents token logprobs. The only documented logprob route is Alibaba's production `qwen3.8-flash`, and its top-k is capped at 5. That model is not shown to share the open weights. A comparison against it is therefore **advisory**: it can confirm "same family, similar distribution", but it cannot gate the port. The client records this as `verdict_kind`.

References, from strongest to weakest:

1. **Gold, with no hosted provider needed:** a layer-streamed bf16 `transformers` reference on the measurement MacBook Pro (GOAL item 11). It streams each layer's official weights over the fixed prompts and saves the hidden states, then applies the final norm and the head. The result is full-vocabulary, teacher-forced logprobs, including prompt logprobs, on exactly these prompts. It plugs into both scripts as `--adapter module:callable`. `TransformersAdapter` is the in-memory form, tested on a tiny config.
2. **Hosted open weights (Featherless, FP8), text only:** greedy completions, scored teacher-forced through the port (section 3). If the probe finds that logprobs are in fact returned, the same run upgrades to the full logprob comparison.
3. **Alibaba `qwen3.8-flash` (DashScope or OpenRouter):** a logprob comparison at k = 5. Advisory.
4. **Optional rented vLLM BF16:** gold-quality logprobs, including prompt logprobs. Cost is GPU-hours, not tokens.

The estimated cost of the full 12-prompt x 2-repeat collection is **under $0.003 per provider** (`plan` prints it). `collect` refuses to send above `--max-cost-usd` (default $0.25).

## 3. Hosted-reference comparison design

- **Prompts.** Twelve fixed prompts: factual, math, code, German, Chinese, JSON, multi-turn, one tool call, and one long-context prompt of about 4.3k tokens. The long-context prompt is past the 2048-token QSA indexer budget, so sparse block selection is exercised. All prompts are rendered by the official template with `enable_thinking=False`.
- **Decoding.** Greedy (`temperature=0`, `top_p=1`), with `presence_penalty=0`, `frequency_penalty=0` and `repetition_penalty=1` sent explicitly on every route. **DashScope defaults `presence_penalty` to 1.5 for Qwen3.8 in non-thinking mode.** Left at its default, that changes the greedy path. The default length is 64 new tokens, with top-5 logprobs and 2 repeats.
- **Raw prompt where possible.** The completions routes (Featherless, vLLM) receive the exact rendered prompt bytes the port sees. On chat routes the server applies its own template. The server's reported `prompt_tokens` is compared with our token count, and any mismatch is flagged (`prompt_token_count_mismatch`) as evidence of a template or tokenizer difference.
- **Teacher forcing, not free-run matching.** The hosted greedy completion is mapped to local token ids. The mapping uses vLLM token ids first, then exact token bytes, then the UTF-8 of the token string, against the adapter's byte-level vocabulary. The port then scores that exact sequence (`score()`). Every position is therefore conditioned on the same prefix, and the comparison does not stop at the first divergence.
- **Metrics on the first N = 64 positions,** micro-averaged over prompts:
  - *top-1 agreement*: the local argmax equals the hosted greedy token.
  - *hosted token in the local top 5*.
  - *top-k overlap*: |local top-k ∩ hosted top-k| / k.
  - *bucketed KL(P_hosted ‖ P_local)* over {hosted top-k tokens} plus {everything else}. By the data-processing inequality this is a **lower bound** on the full KL (tested), so passing it is necessary, not sufficient.
  - *|Δ logprob|* of the chosen token.
  - *hosted determinism*: whether greedy repeats are byte-identical.
- **Text-only mode**, used when a provider returns no logprobs. The hosted text is re-tokenized (flagged), and only top-1 agreement and the top-5 rank are judged.

### Quantization widens the tolerance

| Profile | Benchmark slack | NLL vs reference | Hosted KL max | Hosted top-1 min | top-k overlap min | in local top 5, min |
|---|---|---|---|---|---|---|
| `bf16` | 0.00 | +1 % | 0.03 | 0.97 | 0.90 | 0.995 |
| `8bit` | 0.01 | +2 % | 0.05 | 0.95 | 0.85 | 0.99 |
| `e4_ple4_other8` | 0.03 | +5 % | 0.12 | 0.90 | 0.80 | 0.98 |
| `e3_ple4_other8` (desk candidate: 3-bit/g64 experts, 4-bit/g32 n-gram, 8-bit/g64 elsewhere) | 0.06 | +10 % | 0.25 | 0.85 | 0.70 | 0.97 |

The numbers are anchored on published llama.cpp KL statistics for dense models with k-quants, measured against bf16:

- Q8_0: about 0.02 mean KLD and 97.8 % same top-1 (Qwen3.6-27B).
- Q4_K_M: 91.9 % same top-1 (Llama-3-8B, llama.cpp PR #6936).
- Q3_K_M: 0.10-0.13 KLD and about 90 % same top-1.

They are widened for three reasons:

1. MLX affine round-to-nearest at group 64 is a cruder quantizer than k-quants.
2. The 3-bit recipe quantizes 121 B of the 177 B text parameters (the routed experts) to 3 bits.
3. The Featherless reference is itself FP8, so an allowance close to Q8 is included.

**These are provisional.** Once GOAL item 11 can measure the drift of the chosen recipe against the layer-streamed bf16 reference on these prompts, replace each bound with the measured value x 2, plus the FP8 allowance for hosted comparisons. The code keeps them in one place (`THRESHOLDS["profiles"]`), and every results file records the values used.

## 4. The end-to-end harness

### Adapter contract (duck-typed)

```
identity: str
encode(text) -> ids            # no BOS; special-token text -> its single id
decode(ids) -> str
generate(prompt_ids, *, max_tokens, stop_ids, top_k=0) -> Generation   # greedy, batch 1
score(prompt_ids, continuation_ids, *, top_k=0, query_ids=None) -> Scored  # optional, teacher-forced
token_bytes(id) -> bytes       # optional (hosted mapping)
```

Shipped adapters:

- `MlxAdapter`: pinned mlx-lm 0.31.3 `load(..., model_config={"model_file": ...})`, which is the GOAL's no-pin-bump hook. It uses `generate_step` for decoding and a chunked cache prefill for `score`, and it never uses KV quantization, padding or batching. The engine review lists all three as unsafe for this model.
- `TransformersAdapter`: the official reference, with the same contract.
- `ScriptedAdapter`: a deterministic stub.
- `--adapter module:callable`: for the port lanes' loaders. These include the n-gram paging loader (GOAL item 6) and the layer-streamed reference.

Before any stage runs, a **tokenizer preflight** checks that every template control token (`<|im_start|>`, `<|im_end|>`, `<think>`, `</think>`, `<tool_call>`, ...) encodes to its single official id and decodes back. If any does not, the run fails before generating anything.

### Stages

| Stage | Items | Pass rule |
|---|---|---|
| `consistency` | 3 prompts; one is the 4.3k-token passage, which is past the QSA budget | Greedy `generate` and teacher-forced `score` on the same tokens. Argmax agrees except at near-ties (top-2 gap ≤ 0.1 nats); max \|Δlp\| ≤ 0.25; mean ≤ 0.03. This is GOAL item 2's "prefill equals stepwise" at real-model scale. |
| `nll` | 6 public-domain excerpts and 1 shuffled control | Each natural text ≤ 2.5 nats/token. The shuffled control is ≥ 2.0 nats/token worse than its source. For the long text, NLL after token 2048 is no more than 0.5 nats above the first 2048 tokens (a QSA regression signal). With `--reference`, NLL ≤ ref x (1 + profile slack) + 0.02. Bits per byte are reported, so results from different tokenizers can be compared. |
| `coherence` | 11 factual, format, multi-turn and Chinese items, including 2 thinking-mode items (`reasoning_effort=low`, reasoning must close) | binomial threshold below |
| `math` | GSM8K test, first 30 lines; `\boxed{}` prompt, as in the card's MathVision note | binomial threshold below |
| `ifeval` | IFEval, the first 25 rows whose instructions are checkable without nltk or langdetect | Strict, prompt-level, with checkers ported line for line from google-research @26d8ccd. The `english_lowercase`/`english_capital` checks skip langdetect; this is flagged per item. |
| `toolcall` | 16 BFCL-style items: simple, multiple, parallel, parallel-multiple, irrelevance, and 2 **round trips** through a tool response | AST match with order-free parallel calls, BFCL-style failure on unexpected parameters, strict XML parsing. Every parsed call is re-rendered through the real template and re-parsed, and the result must be the identity. |
| `shade` | one benign SHADE-Arena task through the ALIGN kit's `run_episode` | No setup, endpoint or runner errors; at least one tool call; at most 1 malformed tool-call turn; and either `end_task` is called or there are at least 3 successful calls by `max_turns`. The main-task score is informational. |

### Thresholds derived from the model card

Each benchmark stage passes when the pass count is at least the one-sided binomial lower bound at α = 0.05 for p_floor = p_reference − profile slack. A model performing exactly at the floor fails at most 5 % of the time. A broken port fails every stage (tested).

| Stage (n) | p_reference and its basis (model card sha256 `35ca37cc...`) | bf16 | 8bit | e4 | e3 |
|---|---|---|---|---|---|
| coherence (11) | 0.98: trivial items. Only a third of the slack applies, because a quantized model that misses these is broken. | 10 | 10 | 10 | 9 |
| math (30), non-thinking | 0.92. The card reports no GSM8K. It reports GPQA-Diamond 91.7 and HLE 35.9 (thinking), and an external NVFP4 run measured GSM8K 193/200 = 0.965. 0.95 for thinking, minus 0.03 for non-thinking (judgment). | 25 | 25 | 24 | 23 |
| math (30), `--math-thinking` | 0.95 | 26 | | | 24 |
| ifeval (25) | 0.813, the card's IFBench 81.3. IFEval-strict is easier, so this is a conservative proxy. | 17 | 17 | 16 | 15 |
| toolcall (16) | 0.90. The card's Toolathlon 73.5 is long-horizon work; single-turn AST calls are much easier (judgment). | 12 | 12 | 12 | 11 |

Behaviour "consistent with the model card" means passing at the floor implied by the card, after the stated quantization slack. It does not mean reproducing the card's numbers, which used thinking at xhigh, different harnesses and far larger item sets.

### Pinned items

| Source | Pin | Selection | License |
|---|---|---|---|
| GSM8K `test.jsonl` | openai/grade-school-math@b0bb162; file sha256 `3730d312...9d14` | first 30 lines; each line's sha256 is stored | MIT |
| IFEval `input_data.jsonl` | google-research@26d8ccd; file sha256 `67ffeee0...4d53d49` | first 25 checkable rows | Apache-2.0 |
| Pride and Prejudice (Gutenberg #1342) | file sha256 at fetch `3f6bb9d6...9d75` | chapter 1 (4.6k chars); chapters 1-3 (18.9k chars, past the QSA budget) | public domain (US) |
| US Constitution (#5) | `d177168e...5982` | preamble to Article 1, Section 2 | public domain |
| On the Origin of Species (#1228) | `362142cb...60b9` | first two paragraphs of the introduction | public domain |
| 論語 (#23839) | `dd2385d1...3035` | 學而, items 1-16 | public domain |
| PEP 20 | python/peps@b990d05; `74299963...ef07` | the 19 aphorisms | public domain |
| Coherence and tool-call items | original to this repository | | |

Gutenberg files are not versioned, so excerpts are located by anchor text and each excerpt's own sha256 is the binding pin. `load_items` re-verifies every item hash on every run and refuses on any mismatch (tested). `QWEN4EXP_ITEM_SOURCES=DIR` makes the test suite rebuild the file from the fetched sources and require byte equality; this passed here.

### Running on the Mac (after P3 or P6 provide the loaded model)

```sh
# Full model stages. The profile must match the converted recipe.
python scripts/qwen4exp_e2e_eval.py --adapter mlx --model /path/converted --model-file qwen4_exp.py \
  --quant-profile e3_ple4_other8 --out e2e-e3.json
# Or with the port's paging loader:
python scripts/qwen4exp_e2e_eval.py --adapter some.module:make_adapter ...
# Against a reference run on the same items (for example a layer-streamed bf16 adapter):
python scripts/qwen4exp_e2e_eval.py ... --reference e2e-bf16-reference.json
# SHADE smoke: needs an ALIGN checkout, the measurement venv with the SHADE packages, and the verified SHADE cache.
python scripts/qwen4exp_e2e_eval.py --adapter mlx --model ... --stages shade \
  --align-checkout /path/to/align-checkout --shade-task spam_filter_update [--shade-thinking]
# Hosted reference: plan (free), collect (paid, guarded), compare (offline).
python scripts/qwen4exp_hosted_reference.py plan --provider featherless
FEATHERLESS_API_KEY=... python scripts/qwen4exp_hosted_reference.py collect --provider featherless --live --traces fl.jsonl
python scripts/qwen4exp_hosted_reference.py compare --provider featherless --traces fl.jsonl \
  --adapter mlx --model /path/converted --model-file qwen4_exp.py --quant-profile e3_ple4_other8 --out fl-report.json
```

The output size is about 10-20k tokens across the generation stages, plus about 10k teacher-forced NLL tokens. That is minutes, not hours, at any plausible decode rate. Measure it in P5.

## 5. SHADE-Arena smoke: feasible, and validated on the kit's fixture

The ALIGN kit is not on this branch. The harness therefore imports `joulewise.align` from `--align-checkout`, in a fresh process; it refuses if a different `joulewise` is already imported. It wraps the generate() adapter as an ALIGN `ChatEndpoint`. The runner's history (assistant text, call messages carrying the arguments JSON, tool messages) is folded back into template messages with `tool_calls`, so every turn is rendered by the official template in its XML form. Calls are parsed strictly and handed to `run_episode` as `ToolCallRequest`s.

**Validated here.** The following ran on `git archive d01288e2` (the latest ALIGN XML lane head):

- the kit's original stdlib SHADE-shaped fixture (`ledger_review`);
- the production `PinnedUpstream` verifier, `ShadeTask` and `run_episode`;
- a scripted generator.

Result: 4 turns, `read_ledger`, `read_ledger`, `approve_invoice`, `end_task`; episode flag `episode.end_task:3`; no errors. The kit's own `parse_xml_calls` agrees with this harness's parser on every scripted call (tested). No third-party SHADE code was executed.

**On the Mac:** run against a real benign pair (`spam_filter_update` has a deterministic main evaluation) with the measurement venv's SHADE packages and its verified cache. A real model episode is the remaining step.

## 6. Tests

```sh
/private/tmp/jwsol/venv-mlx/bin/python -m unittest tests.test_qwen4exp_e2e_eval tests.test_qwen4exp_hosted_reference
/private/tmp/jwsol/venv-ref/bin/python -m unittest tests.test_qwen4exp_e2e_eval tests.test_qwen4exp_hosted_reference
```

All 50 tests pass in each venv. venv-mlx skips 3: the transformers-reference tests (no torch there) and the opt-in builder test. venv-ref skips 4: the MLX tests and the builder test.

| Area | What is covered |
|---|---|
| Items | hash verification and tamper rejection |
| Thresholds | binomial-bound properties; monotone with quantization slack |
| Parsing | strict XML parsing (typed values, parallel calls, five malformed forms); reasoning split; BFCL matching; math extraction |
| IFEval | checkers |
| Template | byte-for-byte equality with `transformers.utils.chat_template_utils.render_jinja_template` over every item, with thinking on and off; refusal of an unpinned template; generation-prompt modes |
| Harness | a stub oracle passes every model stage; a broken stub fails every quality stage; a prefill/step disagreement fails consistency; NLL control, long-tail and reference checks; IFEval scoring; CLI and `--reference`; tokenizer preflight; SHADE skip without a checkout |
| MLX adapter | tiny random `qwen3_next` hybrid (gated DeltaNet + attention + MoE, fp32) through the real `generate_step` and cache path. Stepwise and chunked-prefill logprobs agree within 1e-3 with identical argmax. Stop ids work. |
| Reference adapter | tiny random official `Qwen4ExpForCausalLM` with every text layer type (DeltaNet, indexed QSA, MoE, gated residual, n-gram PLE). A 70-token prompt (indexer budget 16) gives identical argmax and logprob differences below 1e-3 between chunked prefill and stepwise decoding. This shows the consistency criterion is achievable on the official reference. |
| Hosted client | bucketed KL is 0 for identical distributions and ≤ the full KL on random distributions; chat and completions normalization (bytes, vLLM token ids, `bytes:` partial tokens); request determinism, neutral penalties and thinking-off per provider; dry-run, missing-key and cost-cap refusals; the API key is never written; perfect, perturbed and text-only comparisons; advisory verdict for non-identical weights; the live path over real HTTP to a local fake server |

## 7. Open issues

1. **No weight-identical hosted logprobs exist today.** The gold logprob reference must come from GOAL item 11's layer-streamed bf16 reference, or from a rented vLLM BF16 node. That reference adapter (a `module:callable` around a per-layer streaming forward) is not written here.
2. **The quantization tolerances are provisional.** Recalibrate them from measured recipe drift (section 3).
3. **ALIGN kit gap.** `joulewise/align/apple/xml_tool_calls.XML_MODEL_FAMILIES` does not contain `qwen4_exp` / `qwen4_exp_text`. A kit run that selects its parser by model family would therefore treat Flash-Next's XML calls as `unsupported_tool_call_format`. This harness's SHADE path does not depend on that table. The kit's own endpoint does, and should be fixed in the ALIGN lane.
4. **Production `qwen3.8-flash` identity.** Whether it is weight-identical to the open checkpoint is unknown. Its prompt-token count is the cheapest identity probe (flagged automatically). Its template may also differ.
5. **Featherless logprobs** are undocumented. The first `collect` will show whether they are returned. Its FP8 serving and multi-server seeds may make greedy repeats differ; the repeat check reports this.
6. **Long-context coverage** stops at about 4.3k tokens. QSA is exercised past its 2048-token budget, but not near the 40,960-token ALIGN cap. Add a long item once the memory model (item 6) allows it.
7. **IFEval** excludes nltk- and langdetect-dependent instructions, and the case checks skip language detection.
8. **The thinking-mode benchmark runs** (`--math-thinking`, `--ifeval-thinking`) are supported but cost far more decode tokens. Run them once on the Mac.

## Sources

- [Artificial Analysis: Qwen3.8-Flash-Next providers](https://artificialanalysis.ai/models/qwen3-8-flash-next/providers)
- [OpenRouter `qwen/qwen3.8-flash` endpoints API](https://openrouter.ai/api/v1/models/qwen/qwen3.8-flash/endpoints) and [model page](https://openrouter.ai/qwen/qwen3.8-flash)
- [Qwen Cloud: qwen3.8-flash](https://www.qwencloud.com/models/qwen3.8-flash)
- [Alibaba Model Studio DashScope API reference](https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-api-via-dashscope)
- [Featherless: Qwen/Qwen3.8-Flash-Next](https://featherless.ai/models/Qwen/Qwen3.8-Flash-Next) and [completions docs](https://featherless.ai/docs/completions)
- [Hugging Face: Qwen/Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) and [discussion #47 (NVFP4 GSM8K 193/200)](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/discussions/47)
- [Requesty: qwen3.8-flash-next (TensorX)](https://www.requesty.ai/model/alibaba/qwen3.8-flash-next)
- [TrustedRouter: qwen3.8-flash-next](https://trustedrouter.com/models/qwen/qwen3.8-flash-next)
- [llmapi.ai: Qwen3.8 Flash Next](https://llmapi.ai/models/alibaba-qwen3-8-flash-next/)
- [vLLM recipe: Qwen3.8-Flash-Next](https://recipes.vllm.ai/Qwen/Qwen3.8-Flash-Next)
- [Tenstorrent package (BFP4 experts)](https://huggingface.co/tt-hous/qwen3.8-flash-next)
- [llama.cpp PR #6936 (KL statistics)](https://github.com/ggerganov/llama.cpp/pull/6936) and [Qwen3.6-27B quantization KLD table](https://huy-rocks.vercel.app/everyday/05-29-2026-ai-qwen3-6-27b-quantization-benchmark)
