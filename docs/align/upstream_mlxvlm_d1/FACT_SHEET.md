# D1 fact sheet: mlx-vlm `qwen4_exp` drops QSA sparse attention in left-padded batches

This sheet is for Ed to learn from and then write his own issue and PR text. Nothing here is meant to be pasted, and nothing has been posted to GitHub.

**Target.** `Neywa-Labs/mlx-vlm` (formerly `Blaizzy/mlx-vlm`), main `5cdc659b` (2026-11-05). For every file involved, this commit is identical to PyPI `mlx-vlm 0.7.12`.

**Kit files** (this directory):

| file | what it is |
|---|---|
| `repro_minimal.py` | Standalone reproducer. Needs only `pip install mlx-vlm`. Exit status 1 = bug present. |
| `fix.diff` | The fix: one file, 3 hunks, +11/-16. Applies cleanly to `5cdc659b` (`git apply --check`). |
| `test_qwen4_exp_ragged_qsa.py` | Regression test in the repo's pytest conventions. Proposed home: `mlx_vlm/tests/test_cache.py`. |
| `WALKTHROUGH.md` | Line-by-line explanation of the diff and the test. |
| `evidence/` | Raw outputs behind every number below: reproducer runs, test runs, the in-situ test run and the bitwise non-regression check, plus the scripts that produced them. `evidence/fix_plus_test_in_test_cache.diff` is the exact two-file change verified in situ: the fix, plus the test placed in `test_cache.py` using that module's `parametrize` alias. It also applies cleanly to `5cdc659b`. |

**Verification environment.** Apple M4, macOS 15.7.9, Python 3.13.18, mlx 0.32.4.

**Independent check.** A second AI reviewer, briefed separately with the code but not with these conclusions, re-derived the bug and reviewed the fix. Its findings:

- **Mutation test:** with only path A put back to the original code, the `[attention]` test fails; with path B put back, both fail. Each parameter therefore guards its path.
- **Path probes:** a one-row batch cache with leftover left padding, and verify blocks of 2, 3 and 4 tokens, all match single requests to ≤ 5e-7 after the fix.
- **Result:** no correctness or regression issue found. Its wording, test and fact-sheet corrections are incorporated here (§9 Q2, Q6, Q7, Q11; §10).

---

## 1. The bug in three sentences

When any row of a batch is left-padded, each Qwen Sparse Attention (QSA) layer in `qwen4_exp` still computes its sparse block selection during decode and multi-token speculative verify. It then throws the selection away and attends densely to every key. Every row whose visible context has reached the sparse regime (2052 or more tokens on the released config), including the unpadded row, then produces different logits from the same request served alone, and from the transformers reference. The divergence is silent and compounds token by token.

## 2. What QSA is

Qwen3.8-Flash-Next is a hybrid model: of its 48 layers, 36 are Gated DeltaNet and 12 use Qwen Sparse Attention (QSA).

In a QSA layer, a small "indexer" works per query:

1. It groups the query's visible keys into blocks of `indexer_compress_ratio = 4` tokens.
2. It summarizes each block with its mean index key, normalized and rotated.
3. It scores every block against the query's index heads as the sum over heads of `relu(q·k)`.
4. It keeps the top `indexer_budget / compress_ratio = 2048 / 4 = 512` blocks, plus the incomplete "tail" block that contains the query.

Attention then runs over only those tokens. With 512 or fewer complete blocks (2051 or fewer visible tokens), every block is kept and QSA equals ordinary causal attention. From 513 complete blocks on (2052 or more visible tokens), it is genuinely sparse: each QSA layer attends to at most 2051 keys, whatever the context length.

## 3. The exact code path at `5cdc659b`

Path prefixes: `q4` = `mlx_vlm/models/qwen4_exp/language.py`, `q35` = `mlx_vlm/models/qwen3_5/language.py`, `sv` = `mlx_vlm/models/qwen3_5/speculative_verifier.py`, `kern` = `mlx_vlm/models/qwen4_exp/qsa_kernel.py`.

### 3.1 How a ragged batch reaches attention

- A multi-row prefill runs row by row on the unpadded rows, then merges the caches (`q4:1624-1711`). Two kinds of call skip that split: a one-row batch cache that still has left padding, and a call that captures hidden states (`hidden_sink`). Both reach `Qwen4ExpAttention` with a boolean array mask, which merges the QSA mask and uses masked SDPA. That was already correct before the fix and is unchanged.
- For a one-token decode on a batch cache with any left padding, the mask is not an array. `_create_qwen3_5_attention_mask` returns the string `"left_padded_decode"` (`q35:278-292`, return at `q35:291`), and `_create_qwen4_exp_attention_mask` defers to it (`q4:1564-1582`). For multi-token calls on a padded cache, the mask is a boolean array.
- Which forward runs (`q35:1872-1892`):
  - Decode uses `Qwen4ExpBatchInvariantForward` when `_supports_batch_invariant_decode()` is true (`q4:2106-2111`). That covers an unquantized head, or a 4-, 5- or 8-bit affine head with fp16/bf16 scales and compatible shapes (`quantized_verifier.py:1647-1661`).
  - Otherwise decode goes through `Qwen4ExpModel` and `Qwen4ExpAttention`. Examples: a 6-bit or 3-bit head, an mxfp4/nvfp4 head, a quantized tied embedding.
  - MTP speculative verify always uses the batch-invariant forward (`_speculative_verify`, `q4:2184-2218`).

### 3.2 Where the selection is computed and where it is discarded

**Path A: the attention module (`Qwen4ExpAttention.__call__`, `q4:1091`).**

- Computed: `selection = self.indexer.select(x, cache, position_ids)` at `q4:1099`.
- Discarded: `q4:1112-1122`. For any string mask other than `"causal"`, the code returns `super().__call__(...)`. The comment there reads: "Qwen3.5 owns specialized string modes such as `left_padded_decode`. The indexer state is already updated; delegate only the Q/K/V attention path to the parent."
- What the parent then does:
  - `Qwen3_5Attention.__call__` sets `mask = None` and calls `_qwen3_5_left_padded_attention` (`q35:1007-1015`).
  - That helper (`q35:878-940`) slices each row's pads off its keys and runs dense SDPA with `mask=None` (`q35:921`, `q35:934`).
  - Its `mask` parameter (`q35:885`) is never read.

**Path B: the batch-invariant forward (`Qwen4ExpBatchInvariantForward._qsa_attention`, `q4:1827-1956`).**

- Routing: `if hidden_states.shape[1] > 2 or mask == "left_padded_decode"` (`q4:1871-1873`).
- Computed: `qsa_mask = attention.indexer.from_projected(...)` (`q4:1874`). This computes the selection and builds its mask.
- Discarded:
  - **One-token ragged decode.** The merge at `q4:1876-1885` handles only `None`, `"causal"` or array masks, so the string survives. `self._attention(...)` (`q4:1886`) then sees `"left_padded_decode"`, sets `mask = None` (`sv:97-101`), and calls the same dense ragged helper (`sv:104-112`).
  - **Ragged verify of 3 or more tokens.** The QSA mask *is* merged into the boolean array. But `_attention` sends every `length > 1` call to the ragged helper (`sv:104`), which ignores the array.
- Not affected: ragged verify of exactly 2 tokens already takes the lower selection path (`q4:1895-1956`) with `causal=False`, which is masked SDPA (`kern:222-223`). That is correct.

**Why the unpadded row is affected too.** The string mode and the padding check (`q4:1828-1829`) are decided per batch, not per row. One padded row sends the whole batch, in every QSA layer, to the dense helper.

## 4. Why that is wrong (transformers 5.22.1 reference)

Cited file: `transformers/models/qwen4_exp/modeling_qwen4_exp.py` as installed by `transformers==5.22.1`.

- **`:711-713`.** The indexer takes each query's visible keys from the attention mask, which already excludes padding. Its comment says the mask "is never None here" and "already gives us the valid indices".
- **`:721-726`.** For every batch row and every query, blocks are formed from that query's own visible tokens: `local_visible_indices`, then `num_complete_blocks = len // compress_ratio`. Left padding therefore shifts block boundaries per row, and nothing depends on the other rows.
- **`:749`.** `scores.topk(min(self.block_topk, num_complete_blocks))` keeps 512 blocks per query.
- **`:754`.** The incomplete tail block is always kept.
- **`:847-852`.** `Qwen4ExpTextAttention.forward` always combines the selection mask with the causal/padding mask ("Combine both masks (they are never None …)"). There is no exception for padded batches or for decode.

So in the reference, a row's output depends only on that row's tokens, and a ragged batch must equal the single requests. mlx-vlm's own indexer agrees: `build_mask` offsets blocks by each row's left padding. A test removed in #2276 (see §8) showed the padded-row mask equals the single-row mask. Only the attention call drops it.

## 5. The fix, and why it is correct, complete and safe

`fix.diff` changes `q4` only. The line-by-line version is in `WALKTHROUGH.md`.

1. **Path A** (`q4:1109-1129`). The early return for string masks is gone. `"left_padded_decode"` now gets the same treatment as `None`/`"causal"`: `mask = self.indexer.build_mask(selection)`. Then `dispatch_qsa_attention(causal=False)` picks `DENSE_MASKED` (masked SDPA).
2. **Path B, routing** (`q4:1870-1873`). Only unpadded calls (`standard_causal`) of 3 or more tokens use the `_attention` branch. Every padded call takes the existing lower path, which ragged 2-token verify already used correctly.
3. **Path B, merge** (`q4:1915-1926`). In that lower path, `"left_padded_decode"` is replaced by the QSA mask, as in 1.

**Why it is correct.** `build_mask(selection)` (`q4:1042-1081`) is already the complete per-row mask for a padded batch:

- selected blocks start at `left_padding + 4·block` (`q4:1053-1057`; the block starts at `q4:915`);
- the tail starts at `left_padding + 4·complete_blocks` (`q4:1070-1073`);
- rows not yet sparse get `left_padding <= key < query_end` (`q4:1074-1080`).

Pad columns are always `False`, and the causal bound is built in. Masked SDPA over the padded keys with this mask therefore computes exactly the reference's attention set. `causal=False` keeps the padding-unaware Metal kernel out of these calls (`kern:222-223`).

**Why it is complete.** Every way a QSA layer can see a left-padded cache is now covered:

- one-token decode on path A (fix 1);
- one-token decode on path B (fixes 2 and 3);
- verify of 3 or more tokens (fix 2);
- 2-token verify (already correct);
- multi-row prefill (row by row on unpadded rows), and multi-token calls with an array mask on path A (already masked; unchanged).

Ragged steps in which no row is sparse yet still use the same dense helper as before. The helper is exact there, and those outputs are bitwise unchanged.

One caveat. That holds when at least one row has zero padding, which is the normal case: merging gives the longest row zero padding, and `filter` trims the padding the rows share. If every row were padded, a step whose padded length exceeds the budget while no row's visible length does would now take masked SDPA instead of the helper. That is still dense attention, so only rounding changes.

**Why it is safe for single requests and equal-length batches.** The new conditions are true only when the cache has left padding:

- A single-request `QSAKVCache` has no `left_padding`. The padding info is `None`, and the mask is never `"left_padded_decode"`.
- An equal-length `BatchQSAKVCache` has maximum padding 0. `_create_qwen3_5_attention_mask` returns `None` for decode (`q35:288-289`), and `_create_qwen4_exp_attention_mask` returns `None` or `"causal"`.

For those inputs every changed line evaluates exactly as before. A bitwise check confirms it (§6.5).

**Cost.** No new kernel. Before the fix, each padded step ran dense attention over each row's unpadded keys; it now runs masked SDPA over the padded keys, which is the same O(context) work. The extra cost is one boolean mask build per QSA layer per padded step, and path B already built and discarded that mask. Not benchmarked on real weights (§9, Q3).

## 6. Before / after numbers

### 6.1 `repro_minimal.py`

Tiny random fp32 model: the repo's own `qwen4_exp` test case, with 16 indexer heads. Prompts of 14 and 11 tokens (padding `[0, 3]`), 3 decode steps, then a 3-token verify.

Before: main `5cdc659b`, and PyPI 0.7.12 gives identical output. **Exit 1.**

```
max |logit(batch) - logit(single request)|   ragged row 0 (pad 0)   ragged row 1 (pad 3)   equal-length control
decode, batch-invariant path (default)         8.7e-02                1.0e-01                1.9e-07
  then a 3-token verify                        9.5e-02                1.5e-01                2.1e-07
decode, attention-module path                  8.7e-02                1.0e-01                2.4e-07
  then a 3-token verify                        9.5e-02                1.5e-01                2.9e-07
FAIL: the ragged batch differs from single requests
```

After: `5cdc659b` + `fix.diff`. **Exit 0.**

```
max |logit(batch) - logit(single request)|   ragged row 0 (pad 0)   ragged row 1 (pad 3)   equal-length control
decode, batch-invariant path (default)         1.9e-07                2.1e-07                1.9e-07
  then a 3-token verify                        2.1e-07                1.5e-07                2.1e-07
decode, attention-module path                  2.4e-07                2.4e-07                2.4e-07
  then a 3-token verify                        2.9e-07                2.7e-07                2.9e-07
PASS
```

### 6.2 Tests, run in a clone of mlx-vlm at `5cdc659b`

Final run: the new test placed in `tests/test_cache.py`, as in `evidence/fix_plus_test_in_test_cache.diff`.

```
cd mlx_vlm && pytest tests/test_cache.py tests/test_models.py tests/test_model_ops.py tests/test_speculative.py -k "qwen4 or qsa or QSA"
```

That selects every existing test whose id mentions qwen4 or QSA (30), plus the new test with its 2 parameters.

| | existing qwen4/QSA tests (30) | new test `[batch_invariant]` | new test `[attention]` |
|---|---|---|---|
| before (`5cdc659b`) | 30 passed | **FAILED**: 384/384 logits of the unpadded row mismatch, max \|Δ\| 0.133 | **FAILED**: same, max \|Δ\| 0.133 |
| after (+ `fix.diff`) | 30 passed | passed | passed |

- **The kit's standalone `test_qwen4_exp_ragged_qsa.py`**, dropped into `mlx_vlm/tests/`, behaves the same way: before, 2 failed with max \|Δ\| 0.133; after, 2 passed (`evidence/standalone_test_file.txt`).
- **CI test-group validation** (the lint job's script): OK. No new test file, so `.github/workflows/tests.yml` needs no change.
- **Lint:** pre-commit's pinned black 26.3.1, isort 5.13.2 (`--profile=black`) and autoflake 2.2.1 report no changes on `language.py` and `test_cache.py`.
- **Peak RSS** of these runs: 0.46 to 0.58 GB.
- **Full `tests/test_cache.py`** with the fix and the test in place: **686 passed** in 7 min 50 s, peak RSS 0.52 GB. This run predates adding `lm.eval()` to the test; the selection run above includes it.

### 6.3 Against the transformers reference

This uses the audit harness (`scripts/audit_mlxvlm/t1_ragged.py`), config C: a tiny checkpoint saved by transformers 5.22.1 in the real layout, with prompts of 20 and 17 tokens. Cells are max \|Δlogit\| against the reference.

| fp32 | decode steps 1-4 | 3-token verify |
|---|---|---|
| single request (any version) | ≤ 6.6e-7 | ≤ 5.4e-7 |
| ragged rows, before | **0.069 to 0.19** | **0.065 to 0.12** |
| ragged rows, after, batch-invariant path | ≤ 6.2e-7 | ≤ 7.7e-7 |
| ragged rows, after, attention-module path | ≤ 6.6e-7 | ≤ 7.0e-7 |

In bf16, the ragged rows were off by about 0.14 before the fix. After it, they show the same error against the fp32 reference as single requests do in bf16: 1.6e-2 for one prompt, 2.5e-2 for the other.

### 6.4 Through `BatchGenerator`

`BatchGenerator` is the engine behind `batch_generate` and the server. This run uses `scripts/audit_mlxvlm/t1_batchgen.py`, greedy decoding, 7 new tokens, config C, fp32.

| row | before | after |
|---|---|---|
| ragged row 0 (no padding) | 5/7 tokens match the reference, max \|Δlogprob\| 0.077 | 7/7, 3.5e-7 |
| ragged row 1 (pad 3) | 6/7, 0.061 | 7/7, 4.1e-7 |
| single requests, equal-length control | 7/7, ≤ 4.1e-7 | same |

### 6.5 Bitwise non-regression (`evidence/nonreg.py`; per-array results in `evidence/nonreg_summary.txt`)

40 logit arrays were computed before and after the fix, over these combinations:

- fp32, and bf16 with a head dimension the Metal kernel accepts;
- both decode paths;
- verify blocks of 2 and of 3 tokens;
- single requests, equal-length batches, short ragged batches (never sparse) and long ragged batches.

**All 32 non-long-ragged arrays are bitwise identical.** Only the 8 long-ragged arrays changed. They moved from about 0.1 off the single requests to about 3e-7 in fp32. The models ran in eval mode.

**Honest bf16 caveat.** In bf16, the fixed ragged rows are not bitwise equal to single requests:

- Single requests use the indexed Metal sparse kernel; padded rows use masked SDPA, because the kernel has no notion of padding.
- The two differ by about 1 bf16 ulp per logit (3.9e-3 at logit scale 0.9).
- In the tiny model, 1 of 14 positions had a near-tie flip (7.6e-2, argmax changed).
- Equal-length batches remain bitwise identical to single requests.

Bitwise bf16 parity for ragged rows would need padded rows to run the indexed kernel too. One possible route, suggested in review but not prototyped: group rows by padding, as the ragged helper's fallback loop does, and slice off their pad columns so the kernel sees unpadded keys. That is a follow-up, not part of this fix.

## 7. Who is affected

- **`mlx_vlm.server` with continuous batching.** Requests of different prompt lengths share a batch and are left-padded, which is the normal case. As soon as any row reaches 2052 visible tokens, that row's QSA layers attend densely instead of sparsely. Typical sources are long chats, agent or tool loops, and documents. The longest, unpadded row is the most likely to cross that threshold.
- **`batch_generate`** with prompts of different lengths.
- **Batched MTP speculative decoding on ragged batches.** Verify blocks of 3 or more tokens drop the selection, and so do the one-token decode steps around them.
- **Both decode paths.** Before the fix, deployments with unquantized, 4-, 5- or 8-bit affine heads (batch-invariant path) and with 6-bit, mxfp4 or nvfp4 heads (attention-module path) were equally affected.
- **Not affected:** single-request `generate` and CLI runs, equal-length batches, and steps in which no row has reached 2052 tokens (dense attention is exact there).
- **Affected releases:** every release with Qwen4 continuous batching, `v0.7.0rc0` (2026-08-31) through `v0.7.12` (2026-11-04). `v0.6.17` predates continuous batching for QSA.

## 8. History, and a correction to "introduced by #2126"

The behavior predates #2126. A maintainer may well know this, so get it right:

| PR | merged | what it did to ragged QSA decode |
|---|---|---|
| **#2032** (lucasnewman) "Add Qwen3.8-Flash-Next support" | 2026-08-26 | Initial port. The selection is not applied for `"left_padded_decode"`, with an explicit comment: *"The specialized left-padded decode path remains dense. It is uncommon, and preserving its row-specific cache semantics is preferable to applying an incorrectly aligned sparse mask."* At that point the indexer was not padding-aware, and the README said QSA was "not yet wired into continuous batching". It was a documented shortcut that nobody could reach. |
| **#2056** (lucasnewman) "Add continuous batching support for Qwen3.8-Flash-Next" | 2026-08-27 | Made the indexer padding-aware (`block_starts = left_padding + …`), and added `test_left_padded_qsa_mask_matches_singleton_rows`, which showed the padded mask equals the single-row mask. **That removed the comment's stated reason**, but the dense fallback and the comment stayed. Its ragged decode test `test_left_padded_batched_qsa_decode_matches_singleton_rows` (prompts of 10 and 12 tokens, budget 8, ratio 2, so sparse at decode) compared **only argmax**, with the comment "Ragged decode deliberately uses batched kernels, whose reduction order can differ slightly…". **D1 has been reachable from here on.** |
| **#2126** (Blaizzy) "Optimize Qwen4 QSA cache reuse and batched parity" | 2026-09-04 | Added the batch-invariant decode path, which also drops the selection for ragged decode and for padded verify of 3 or more tokens. It replaced the "remains dense" comment with "delegate only the Q/K/V attention path to the parent", which reads as if the selection should still apply. The PR body says "QSA selection follows the Transformers … semantics" and "Ragged, masked, decode, short-context, and unsupported cases retain the dense reference path". Its exact-parity evidence is equal-length only: the `array_equal` test uses two 10-token prompts, and the real-model table uses 16K batches. The body also mentions "a separate B=4 run with four distinct prompts" that matched. It does not say whether those prompts had equal token counts. Ragged rows at 16K would have hit this path and failed parity, so the prompts were probably of equal length. That is an inference, not a fact. The argmax-only ragged test was kept. |
| **#2127** (Blaizzy) "Add GLM-5 Next support" | 2026-09-09 | Refactored path B into `_qsa_attention` (today's code). Same behavior. |
| **#2276** (Blaizzy) "Reduce test suite and drive model tests from JSON cases" | 2026-09-18 | Deleted `test_qwen4_exp.py`, including both ragged tests. **Main has no ragged QSA test today.** |

**Fair one-line framing:**

- a dense fallback for ragged QSA decode, originally a documented shortcut (#2032);
- whose justification #2056 removed when it made the mask padding-aware and turned on continuous batching;
- which #2126 carried into the new batch-invariant decode path, replacing the disclosure comment;
- with tests that checked only argmax (#2056) or equal-length batches (#2126), and that #2276 later deleted.

Avoid saying "#2126 introduced it".

## 9. Questions a maintainer might ask, and the honest answers

**Q1. "Dense ragged decode was intentional. See the old comment, and #2126 says ragged keeps the dense reference path."**
It was intentional in #2032, for a reason that no longer holds: the mask "would be incorrectly aligned". #2056 made the mask padding-aware and tested it. Dense ragged decode gives a different result from the transformers reference and from the same request served alone, and with continuous batching it is the common server case rather than an "uncommon" one. If you prefer to keep it dense for speed, it should at least be documented, because a request's output then depends on which other requests share its batch.

**Q2. "Why not make the indexed Metal kernel padding-aware instead?"**
That would be the faster and bitwise-exact long-term fix. It might not even need kernel changes: grouping rows by padding and slicing off the pad columns could let the existing kernel run on unpadded keys. That has not been prototyped. This PR is the minimal correctness fix, and it uses the module's existing `DENSE_MASKED` plan, which ragged 2-token verify already uses. Happy to try the kernel version as a follow-up.

**Q3. "What is the performance impact?"**
Attention stays O(context) per padded step: dense attention on unpadded keys before, masked SDPA on padded keys after. The added work is one boolean mask build per QSA layer per padded step, and path B already built that mask and discarded it. **Not measured on real weights.** If asked: compare tokens/s of `batch_generate` on two prompts of about 3000 and 2990 tokens, before and after the fix, on a machine that fits the model.

**Q4. "Does this change single-request or equal-length outputs?"**
No. Those outputs are bitwise identical before and after: 32 arrays across fp32 and bf16, both decode paths and verify widths of 2 and 3 (§6.5). The changed conditions require left padding.

**Q5. "Why does the unpadded row change?"**
The ragged mode is chosen per batch (§3.2). One padded row sends every row through the dense helper.

**Q6. "Is the ragged output now exactly equal to single requests?"**
In fp32, within about 3e-7. In bf16 it is within about 1 ulp but not bitwise, because single requests use the indexed kernel and padded rows use masked SDPA (§6.5). In the tiny model, one of 14 positions had a near-tie argmax flip. #2056's own ragged test already accepted reduction-order differences for ragged batches. Expect this to be the main discussion point, though: #2126 was explicitly about bitwise singleton parity. The honest framing is that this PR fixes the semantics, meaning which keys are attended, and that bitwise bf16 parity for ragged rows is a separate optimization (Q2).

**Q7. "Why 16 indexer heads in the test? Could it be flaky?"**
With 1 head, `relu` produces many exact-zero scores, and `argpartition` may order the tied blocks differently in a padded row, whose score array is longer. Sixteen heads make an exact-zero tie very unlikely. The test runs in fp32 (`conftest.py` disables TF32) with tolerance 1e-5 against an observed 3e-7, and the bug produces about 1e-1. It calls `lm.eval()`, as the neighbouring Qwen3.5 test does, so the DeltaNet layers use their inference kernels (`q35:1241`).

**Known limit of the test.** In fp32 with `head_dim=16` the indexed Metal kernel is never selected: it needs fp16/bf16 and `head_dim % 32 == 0`. So the test would not catch a future change that routes padded rows into that kernel, which ignores padding. A bf16 logits test cannot separate that bug from bf16 noise (§6.5). If a maintainer asks, an assertion on the chosen execution plan (`select_qsa_execution_plan`) for padded calls would cover it.

**Q8. "Why delete the delegation to the parent for other string masks?"**
There are no other string masks. The only producer is `q35:291` (`"left_padded_decode"`), and Qwen4's mask builders otherwise return `None`, `"causal"` or an array. The delegation's only effect was dropping the selection.

**Q9. "In hunk 3, `standard_causal` is always False inside `if qsa_mask is not None`."**
Correct. That dead condition was already there, and it was kept to keep the diff minimal. `if not isinstance(mask, mx.array):` would be an equivalent simplification.

**Q10. "Does this fix Eagle3/DFlash on ragged batches?"**
No. `speculative_verify=True` routes Qwen4 into the Qwen3.5 verifier, a separate known problem (#2581, open PR #2630). This fix covers QSA's own decode and the MTP verifier.

**Q11. "And ragged speculative rollback, where rows accept different numbers of draft tokens?"**
Not touched. Qwen4 inherits `requires_uniform_batch_acceptance = True` from the Qwen3.5 `LanguageModel` (`q35:1472`), so batched MTP accepts the same count for every row and never reaches a ragged rollback today. Open PR #2197 concerns that ragged-rollback code in Qwen3.5 (its description reports an `AttributeError` on `c.keys`). The review found that on `BatchQSAKVCache` a ragged commit silently skips the per-row trim instead of raising. Either way it is unreachable from Qwen4's MTP and independent of this fix.

**Q12. "Do you have a real-model reproduction?"**
Not in this kit. The evidence is tiny random models, plus a comparison with the transformers reference at ≤ 7.7e-7. On the real config the trigger is 2052 or more visible tokens in any row of a ragged batch.

**Q13. "How did you find it?"**
During a numerical audit of mlx-vlm's `qwen4_exp` against the official transformers implementation, done for a research project that needs a faithful Flash-Next port on Apple Silicon. Ragged-batch parity was the one failing scenario.

**Q14. "Did you use AI tools?"**
Answer truthfully. The audit, reproducer, fix and test were drafted with an AI coding assistant (Claude). Ed reviewed them, re-ran them, and can explain every line (see `WALKTHROUGH.md`).

**Q15. "Why put the test in `test_cache.py` rather than `test_models.py`?"**
`test_cache.py` is the "batched attention" module. It already holds `test_qwen3_5_single_row_decode_retains_batch_cache` and `test_mistral_large4_batch_cache_matches_independent_requests`, and it imports everything the test needs. The repo's contributor skill (`skills/skills/contributing/SKILL.md`) prefers `test_models.py`. Either is fine; move it if asked. In `test_models.py` it would need `from mlx_vlm.generate.ar import _make_cache`.

**Q16. "`build_mask` writes block −1 to negative token indices."**
Known and harmless (static audit N2). `−1` appears only when a query has fewer complete blocks than the budget, and then `use_sparse` is False and the causal mask replaces the selection (`q4:1077-1080`). This PR does not change that, but it does rely on `build_mask` in more places.

## 10. Related open items: mention, or avoid duplicating

- **#2345** (closed, unmerged; pierre427). "Fix Qwen3.5 batched decode skipping the left-padding mask after a right-padded prefill". A different bug in the same `left_padded_decode` machinery: stale host copies of `left_padding`. lucasnewman closed it in favor of his own model-side fix, **#2357** (merged 2026-09-24): "I'd prefer to fix this on the model side…". Lesson: maintainers prefer model-side fixes, and they may rewrite a fix themselves. This fix is model-side.
- **#2197** (open PR; gaineyllc). Ragged speculative *rollback* on `BatchQSAKVCache` crashes on `c.keys`. Complementary to this fix; no overlapping code.
- **#2581** (open issue) and **#2630** (open PR; selimfedakar). DFlash/Eagle3 verify on qwen4_exp goes through the Qwen3.5 verifier. Different path. #2630 edits `q4` around lines 2001-2100, not this fix's hunks.
- **#2521** (open PR). Opt-in batch-invariant decoding for dense Qwen3.5. Adds `supports_batch_invariant = False` to Qwen4's `LanguageModel`; no overlap.
- **#2039** (closed, unmerged). An earlier Qwen4 continuous-batching cache fix, superseded by #2056.
- **NEY-130.** The maintainers' internal Linear ticket, cited in #2126: batch-invariant quantized GEMM, which would allow removing the row-wise prefill workaround. It is unrelated to D1. Do not cite it as related, and note that Ed cannot see it.
- **The audit's other findings** (F1: transformers-saved `indexed_attention` configs rejected; P5: padded batch without a cache; P3: top-k tie order). Keep these out of this issue and PR; they would be separate issues later.
- **Possible separate problem, found in review, not confirmed end to end.** In APC "prepare/finalize" right-padded prefill, `Qwen4ExpModel`'s row split replaces each cache with a merged one (`q4:1702-1710`). That drops the pending `_right_padding`, so `finalize()` leaves the right-pad tokens in the cache. A direct probe showed the right-padded row off by 5.5e-2, both before and after this fix. This matches the static audit's P4. It was not reproduced through `BatchGenerator`. Keep it out of this PR; it could become its own issue after confirmation.
- **Duplicate search** (read-only, 2026-11-05) for "qwen4 left_padded_decode", "QSA ragged", "QSA padding", "qwen4_exp batch", "Flash-Next batch", "sparse attention padded" and "qwen4 continuous batching": **no existing report of D1.**

## 11. Contribution logistics

### What the repo says

- **CONTRIBUTING.md:**
  - fork, then open a PR against `main`;
  - "If you've added code that should be tested, add tests";
  - "Every PR should have passing tests and at least one review";
  - run pre-commit;
  - "Issues: … clear and has sufficient instructions to be able to reproduce".
  - Nothing about AI-assisted contributions.
- **`.pre-commit-config.yaml`:** black 26.3.1, isort 5.13.2 (`--profile=black`), autoflake 2.2.1 (remove unused imports).
- **No issue templates and no PR template.** GitHub's community profile lists `issue_template` and `pull_request_template` as null, and there is no organization `.github` repo.
- **The repo's own agent skills** (`skills/skills/`) say more than CONTRIBUTING does:
  - `reproducible-github-issues/SKILL.md` gives the expected issue structure: Summary, Environment, Model, Reproduction, Expected, Actual, Logs, Inputs. Its quality bar: "a maintainer can run one command … and see the same failure". `repro_minimal.py` meets it.
  - `contributing/SKILL.md` covers tests (prefers `test_models.py`; no standalone `test_<feature>.py`), running pre-commit as the last step before pushing, and perf evidence for performance-sensitive changes.
- **CI** (`.github/workflows/tests.yml`, "Test PRs"):
  - A lint job: `pre-commit run --all-files`, plus a check that every `tests/test_*.py` file is assigned to exactly one CI group. **A new test file must be added to `tests.yml`**, which is one reason to put the test into `test_cache.py`.
  - Four test groups on GitHub runners: `interfaces` (ubuntu); `training-ops` (macos-15, includes `test_cache.py`); `models` (macos-15, includes `test_models.py` and `test_speculative.py`, plus distributed tests); `media` (macos-15).
- **Bot** (`pr-contributor-reminder.yml`): comments when commits are not GitHub-"Verified", and when pre-commit or tests fail. Maintainers have asked outside contributors to sign and force-push, as in #2039. **Ed should set up commit signing (SSH or GPG) before pushing.**

### What recent outside contributions look like

From read-only `gh api` on the last 60 closed PRs:

- **Most outside fixes are merged by lucasnewman**, each with a single approval. In the sample, time to merge ran from under 1 day to 12 days: #2658 and #2643 took about 1 day; #2625, #2624 and #2616 took 4 to 5; #2587 took 9; #2563 took 12.
- **Common branch names:** `fix/<topic>` or `fix-<topic>`, for example `fix/interpolate-spatial-dims` and `fix-max-completion-tokens`.
- **Typical PR body:** Problem/What, Change/Fix, Tests/Testing, with before/after evidence, and "Fixes #N" when an issue exists. #2625 "Fixes #2532", #2643 "Fixes #2642" and #2624 "Fixes #2496" all followed an issue. #2616 and #2563 were merged without one.
- **The lead maintainer (Blaizzy) has redirected unsolicited PRs to issues:** "please open a issue first" (#1512), and "please open a issue with a reproducible example, then we can ideate on a solution together" (#1466, #1054). Those PRs carry the repo's **"AI Slop"** label.

### Recommendation

1. **Issue first, then the PR within about a day.**
   - The behavior was once documented as intentional (#2032).
   - #2126's text can be read as "ragged stays dense".
   - The lead maintainer prefers that conversation in an issue, and the issue stands even if the maintainers choose another fix (compare #2345 and #2357).
   - Put `repro_minimal.py`'s output (§6.1) and the code path (§3.2) in the issue. Then open the PR with "Fixes #N", and say you are glad to adjust the approach.
2. **Branch:** `fix/qwen4-exp-ragged-qsa-decode` on Ed's fork.
3. **Commits:** one signed commit with `language.py` and the test placed in `test_cache.py`.
4. **Before pushing:** `pre-commit run --files mlx_vlm/models/qwen4_exp/language.py mlx_vlm/tests/test_cache.py`, then `cd mlx_vlm && python -m pytest -q tests/test_cache.py -k "qwen4 or qsa"`.
5. **Expected checks:** lint (pre-commit and the test-group check), the four test groups, one approving review, and bot comments only if something is unsigned or failing.
6. **AI disclosure.** No written rule requires it, but disclosure is the visible norm:
   - The repo ships agent skills for Claude Code, Codex and Gemini.
   - Merged PRs carry lines such as "AI assistance: Codex assisted with implementation and regression testing." (#2328, merged by lucasnewman).
   - The maintainers use an "AI Slop" label for low-effort AI PRs.

   **Ed should write the issue and PR text himself, and add a one-line disclosure** along the lines of #2328's. Per our GOAL notes, mlx-lm (ml-explore) forbids AI-written PR text outright. mlx-vlm has no such rule, but writing it himself is the safe practice either way.

## 12. Re-running everything

Scratch space is `/private/tmp/jwd1kit`. The mlx-vlm clone at `5cdc659b` is `/private/tmp/jwmlxvlm-main` (branch `fix-qwen4-ragged-qsa` has the fix and the in-situ test, uncommitted), and `/private/tmp/jwd1kit/base` is a pristine worktree of `5cdc659b`. The venv is `/private/tmp/jwsol/venv-mlxvlm` (mlx-vlm 0.7.12, mlx 0.32.4). Its pytest comes from `/private/tmp/jwd1kit/pydeps` and its linters from `/private/tmp/jwd1kit/lintdeps`, both installed with `pip --target`, so the venv itself was not modified.

```bash
V=/private/tmp/jwsol/venv-mlxvlm/bin/python
KIT=/Users/edr/code/CapstoneProject/jw-wt/port-qwen4-exp/docs/align/upstream_mlxvlm_d1
cd $KIT
# reproducer: released package, then the fixed clone
PYTHONPATH= $V repro_minimal.py                                  # exit 1
PYTHONPATH=/private/tmp/jwmlxvlm-main $V repro_minimal.py        # exit 0
# tests before and after: evidence/rerun_all.sh (final run) and evidence/run_tests.sh (first run); the paths inside point at the scratch trees
cd /private/tmp/jwd1kit/base && git apply --check $KIT/fix.diff  # clean
```
