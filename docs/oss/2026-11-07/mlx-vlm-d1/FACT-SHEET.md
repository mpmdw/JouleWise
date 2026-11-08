# D1 fact sheet: mlx-vlm `qwen4_exp` ignores QSA sparse attention in left-padded batches

Facts for Ed to read and then put into his own words. Nothing here is meant to be pasted upstream, and nothing has been posted.

**Read-only status.** This kit was prepared on 2026-11-07 without running, building, installing or importing any upstream code. All numbers below come from JouleWise's runs on 2026-11-05 against `5cdc659b` (evidence at JouleWise `f1e0f6673`, `docs/align/upstream_mlxvlm_d1/evidence/`). They carry over to today's pin only because the relevant files are byte-identical (§1). Ed's run in RUN-ME.md is the first run at the new pin.

---

## 0. Pins

| what | value |
|---|---|
| Upstream repo | `Neywa-Labs/mlx-vlm`. `github.com/Blaizzy/mlx-vlm` resolves to the same repo: on 2026-11-07, `git ls-remote` on both names returned the same HEAD. |
| Pinned upstream commit | `a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4` (main on 2026-11-07; "Merge pull request #2685", Lucas Newman, 2026-11-07 01:03 +0100) |
| Latest release | PyPI `mlx-vlm 0.7.12` (2026-11-04), tag `v0.7.12` = `7230940302cbe602054650f18a2f77db945bc57a` |
| Reference implementation | `huggingface/transformers` tag `v5.22.1` (`446a570e62b04a89ea001604ada7366baac2ea67`), `src/transformers/models/qwen4_exp/modeling_qwen4_exp.py` |
| JouleWise source kit | `docs/align/upstream_mlxvlm_d1/` at `f1e0f6673`. The same files are at `origin/port/qwen4-exp-mlx` = `9452a2bb4`. |
| Read-only clone used | `/private/tmp/jwoss-ro/mlx-vlm-d1/src` (`--depth 50 --no-checkout`; read with `git show` and `git grep` only) |

Path prefixes used below, all at `a54f1a0d`:

- `q4` = `mlx_vlm/models/qwen4_exp/language.py`
- `q35` = `mlx_vlm/models/qwen3_5/language.py`
- `sv` = `mlx_vlm/models/qwen3_5/speculative_verifier.py`
- `kern` = `mlx_vlm/models/qwen4_exp/qsa_kernel.py`
- `tf` = the transformers file above at `v5.22.1`

## 1. Re-check against current main (2026-11-07)

- **The code path is unchanged.** Main moved from `5cdc659b` (the old kit's base) to `a54f1a0d` in 2 merges. Those changed 5 files: `processing_muse_glimmer.py`, `server/app.py`, `server/audio.py`, `tests/test_processors.py` and `tests/test_server.py`. None is on the D1 path.
- **The relevant files are byte-identical.** Blob ids at `a54f1a0d`:

  | file | blob |
  |---|---|
  | `q4` | `9a9bee24` |
  | `q35` | `e595e886` |
  | `sv` | `44790ad7` |
  | `kern` | `b1d003e7` |
  | `tests/test_cache.py` | `f2872509` |
  | `tests/test_models.py` | `1763d90f` |
  | `generate/ar.py` | `f7176a12` |
  | `tests/conftest.py` | `01ce798e` |

  The first four are also identical in the `v0.7.12` tag, so the released package has the bug.
- **The patches apply cleanly.** `fix.diff`, `test_only.diff` and `fix_plus_test.diff` were each checked with `git apply --cached --check` against a temporary index of `a54f1a0d`. `fix.diff` matches JouleWise's old `fix.diff` line for line, apart from the full-length blob ids in its `index` line. Also checked: `test_only.diff` plus `fix.diff` gives exactly `fix_plus_test.diff`.
- **Line numbers were re-checked.** Every file:line below was re-read at `a54f1a0d`. Two corrections to the old fact sheet:
  - `requires_uniform_batch_acceptance = True` is at `q35:1473`, not 1472.
  - The neighbour test `test_qwen3_5_single_row_decode_retains_batch_cache` is at `test_cache.py:1771`.
- **No duplicate report exists.** A read-only `gh search` on 2026-11-07 found no report of D1. Terms searched: `left_padded_decode`, `QSA ragged`, `QSA padding`, `qwen4_exp batch`, `Flash-Next batch`, `qwen4 continuous batching`, `sparse attention padded`, `qwen4_exp`, `qwen4`, `Qwen3.8`, `ragged`, `sparse attention`, `indexer`, `batched parity`. I also scanned every issue and PR opened since 2026-11-04.
  - #2518 (identical prompts, B=2 and B=4) involves no padding; it is not D1.
  - #2682 (41-model sweep) does not mention qwen4.
- **No open PR touches D1's hunks.** Open PRs that edit `q4`:

  | PR | `q4` hunks |
  |---|---|
  | #2630 | lines 2001-2100 |
  | #2521 | around line 2062 |
  | #2206 (Blaizzy, CONFLICTING, last updated 2026-09-18) | lines 9-27, 2026 and 2086-2147 |
  | #2148 (stale base) | `BatchQSAKVCache.filter`, `Qwen4ExpModel.__call__` |

  D1 changes `q4:1109-1129`, `q4:1868-1876` and `q4:1916-1922`.
- **New since the old kit:** issue #2692 and PR #2693 (both opened 2026-11-07, both open) would add "sign your commits" to CONTRIBUTING.md.
- **Main has no ragged-QSA test today.** `git grep` at `a54f1a0d` finds none.

## 2. The problem

- Qwen3.8-Flash-Next (`qwen4_exp`) has 48 layers: 36 Gated DeltaNet layers and 12 Qwen Sparse Attention (QSA) layers. A QSA layer works like this:
  1. An indexer splits each query's visible keys into blocks of `indexer_compress_ratio = 4` tokens.
  2. It keeps the top `indexer_budget / compress_ratio = 2048 / 4 = 512` blocks, plus the partial tail block.
  3. Attention then covers only those tokens.
- **When it becomes sparse.** Up to 2051 visible tokens, every block is kept and QSA equals plain causal attention. From 2052 visible tokens (`(512 + 1) × 4`), it is truly sparse: `use_sparse = complete_counts > block_topk` at `q4:1077`.
- **What goes wrong.** Suppose any row of a batch is left-padded. Then during one-token decode and during MTP speculative verify of 3 or more tokens, each QSA layer computes the sparse selection and throws it away. It then attends densely to every visible key.
- **Who sees it.** Every row with 2052 or more visible tokens gets logits that differ from the same request served alone, and from transformers. That includes the unpadded row. Nothing raises an error, and the difference compounds token by token.
- **Affected setups:**
  - `mlx_vlm.server` with continuous batching, where requests of different lengths share a batch;
  - `batch_generate` with prompts of different lengths;
  - batched MTP speculative decoding on ragged batches;
  - both decode paths. One is the batch-invariant forward: unquantized heads, or 4-, 5- or 8-bit affine heads with fp16/bf16 scales and biases and compatible shapes (`mlx_vlm/models/quantized_verifier.py:1647-1661`, `supports_optimized_affine_head`). The other is the attention module, used for every other head, for example 6-bit, mxfp4 or nvfp4.
- **Not affected:** single requests and CLI `generate`, equal-length batches, and steps in which no row has 2052 visible tokens yet (dense attention is exact there).
- **Affected releases** (from the 2026-11-05 audit; only `v0.7.12` was re-checked today): `v0.7.0rc0` through `v0.7.12`.

## 3. Minimal repro (`repro_d1.py`)

- **What it needs:** only `mlx-vlm` and `mlx`. It downloads no weights and needs no network.
- **What it builds:** a tiny random fp32 `qwen4_exp` text model. It has the repo's test-case shape, with `indexer_budget=8` and `compress_ratio=4`, so QSA turns sparse at 12 visible tokens. It uses 16 indexer heads to avoid exact-zero score ties.
- **What it runs:** two prompts of 14 and 11 tokens (left padding `[0, 3]`), run as one batch and as single requests. Each run does 3 decode steps, then a 3-token speculative verify. It runs once per decode path, plus an equal-length control batch.
- **What it reports:** exit 1 if any ragged |Δlogit| exceeds 1e-4, otherwise exit 0.

Output on 2026-11-05 (mlx 0.32.4, Apple M4, Python 3.13.18). Before: `5cdc659b`; PyPI 0.7.12 printed identical output. **Exit 1.**

```
max |logit(batch) - logit(single request)|   ragged row 0 (pad 0)   ragged row 1 (pad 3)   equal-length control
decode, batch-invariant path (default)         8.7e-02                1.0e-01                1.9e-07
  then a 3-token verify                        9.5e-02                1.5e-01                2.1e-07
decode, attention-module path                  8.7e-02                1.0e-01                2.4e-07
  then a 3-token verify                        9.5e-02                1.5e-01                2.9e-07
FAIL: the ragged batch differs from single requests
```

After: `5cdc659b` + `fix.diff`. **Exit 0.** Every cell is between 1.5e-07 and 2.9e-07 and the script prints `PASS`.

## 4. Root cause, with upstream file:line at `a54f1a0d`

### 4.1 How a ragged decode is signalled

- `_create_qwen3_5_attention_mask` (`q35:278-292`) returns the string `"left_padded_decode"` at `q35:291` for a one-token step on a batch cache with any left padding.
- `_create_qwen4_exp_attention_mask` (`q4:1564-1582`) hands that case on to it.
- Multi-token calls on a padded cache get a boolean array mask instead.
- Decode routing is at `q35:1872-1892`:
  - the batch-invariant forward (path B) runs when `_supports_batch_invariant_decode()` (`q4:2106-2111`) is true;
  - otherwise decode goes through `Qwen4ExpAttention` (path A).
- MTP verify always uses path B: `_speculative_verify`, `q4:2184-2218`.

### 4.2 Path A: `Qwen4ExpAttention.__call__`

1. The selection is computed at `q4:1099`: `selection = self.indexer.select(x, cache, position_ids)`.
2. It is then discarded at `q4:1112-1122`. Any string mask other than `"causal"` returns `super().__call__(...)`. The comment there reads: "Qwen3.5 owns specialized string modes such as `left_padded_decode`. The indexer state is already updated; delegate only the Q/K/V attention path to the parent."
3. The parent is `Qwen3_5Attention.__call__`. It sets `mask = None` at `q35:1010-1011` and calls `_qwen3_5_left_padded_attention` (`q35:1012-1014`).
4. That helper (`q35:878-940`) takes a `mask` parameter (`q35:885`) and never reads it. It slices each row's pad columns off and runs dense attention. The Metal fast path at `q35:899` is `_qwen3_5_ragged_decode_attention`, defined at `q35:759`. The fallback calls SDPA with `mask=None` at `q35:921` and `q35:934`.

### 4.3 Path B: `Qwen4ExpBatchInvariantForward._qsa_attention` (`q4:1827-1956`)

- **The branch at `q4:1871-1873`:** `if hidden_states.shape[1] > 2 or (isinstance(mask, str) and mask == "left_padded_decode")`.
  - It computes the selection mask at `q4:1874` (`from_projected`).
  - **One-token ragged decode:** the merge at `q4:1876-1885` handles only `None`, `"causal"` or arrays, so the string survives. `self._attention(...)` (`q4:1886`) then sets `mask = None` (`sv:97-101`) and calls the same dense helper (`sv:104-112`).
  - **Ragged verify of 3 or more tokens:** the QSA mask *is* merged into the boolean array. But `_attention` sends every call with `length > 1` to the dense helper (`sv:104`), which ignores the array.
- **Ragged verify of exactly 2 tokens is already correct.** It takes the lower path (`q4:1895-1956`) with `causal=False`, which selects `DENSE_MASKED` (`kern:222-223`), i.e. masked SDPA.

### 4.4 Why the unpadded row is affected too

The padding check (`q4:1828-1829`) and the string mask are decided once per batch, not per row. One padded row therefore sends every row, in every QSA layer, to the dense helper.

### 4.5 Why the selection is valid for padded rows

`build_mask` (`q4:1042-1081`) is already padding-aware:

- selected blocks start at `left_padding + 4·block` (`q4:1053-1057`), and the indexer's block starts at `q4:915`;
- the tail starts at `left_padding + 4·complete_blocks` (`q4:1070-1073`);
- rows that are not yet sparse get the plain causal window `[left_padding, query_end)` (`q4:1074-1080`).

So the only fault is that the attention call drops the mask.

## 5. What the reference does (transformers `v5.22.1`)

- `tf:711-713`: the indexer reads each query's visible keys from the attention mask, which already excludes padding.
- `tf:721-726`: for every batch row and query, blocks are formed from that query's own visible tokens: `num_complete_blocks = len // compress_ratio`.
- `tf:749`: `scores.topk(min(self.block_topk, num_complete_blocks))`.
- `tf:754`: the tail block is always kept.
- `tf:847-852`: `Qwen4ExpTextAttention.forward` always combines the selection mask with the causal and padding mask. There is no exception for padded batches or for decode.

So in the reference, a row's output depends only on that row's tokens, and a ragged batch must equal the same requests served alone.

## 6. Proposed fix (`fix.diff`: 1 file, 3 hunks, +11/-16)

1. **Path A** (`q4:1109-1129`):
   - Remove the early return for string masks.
   - Treat `"left_padded_decode"` like `None`/`"causal"`: `mask = self.indexer.build_mask(selection)`.
   - `dispatch_qsa_attention(..., causal=False)` then picks `DENSE_MASKED`, i.e. masked SDPA over the padded keys.
2. **Path B, routing** (`q4:1868-1876`):
   - Only unpadded calls of 3 or more tokens keep the `_attention` branch: `hidden_states.shape[1] > 2 and standard_causal`.
   - Every padded call takes the lower path. Ragged 2-token verify already used that path correctly.
3. **Path B, merge** (`q4:1916-1922`): in the lower path, replace `"left_padded_decode"` with the QSA mask, as in 1.

**Unchanged behaviour:**

- Single requests: `QSAKVCache` has no left padding, so the mask is never `"left_padded_decode"`.
- Equal-length batches: their maximum padding is 0, so decode gets `None`, `q35:288-289`.
- Ragged steps in which no row is sparse yet: `select_from_projected` returns `None` (`q4:902-903`), or the key-length guard at `q4:1898-1913` returns early. Both still go to the dense helper.

On 2026-11-05, 32 of 40 logit arrays were bitwise identical before and after the fix: fp32 and bf16, both decode paths, verify widths 2 and 3, and the single, equal-length and short-ragged cases. Only the 8 long-ragged arrays changed, from about 0.1 off to about 3e-7 off in fp32.

Line-by-line explanation: `WALKTHROUGH.md` at JouleWise `f1e0f6673` (command in RUN-ME.md).

## 7. The test

- **What it is:** one function, `test_qwen4_exp_ragged_batch_matches_single_requests`, parametrized over `decode_path` ∈ {`batch_invariant`, `attention`}. It uses the repo's `qwen4_exp` model case with `indexer_n_heads=16`, `mx.random.seed(17)` and `lm.eval()`.
- **What it does:** prefills 14- and 11-token prompts as a ragged batch, then runs 3 decode steps and a 3-token `speculative_verify_logits`. It checks each row against the single request with `assert_allclose(atol=1e-5, rtol=1e-5)`.
- **Where it goes:** `test_only.diff` adds it to `mlx_vlm/tests/test_cache.py`, between lines 1807 and 1808: after `test_qwen3_5_single_row_decode_retains_batch_cache` and before `test_hashes_and_dependencies`. It uses that module's existing `parametrize` alias (`test_cache.py:1592`) and its imports: `_make_cache` (line 45) and `build_config`/`model_case` (line 87).
  - Adding no new file means no CI group change: the lint job requires every `tests/test_*.py` file to be listed in a `tests.yml` group.
  - `test_cache.py` runs in CI group `training-ops` (macos-15).
  - The repo's contributing skill prefers `test_models.py`; moving it there is possible if asked.
- **Results on 2026-11-05 at `5cdc659b`:**

  | | new test (both parameters) | existing qwen4/QSA tests selected by `-k "qwen4 or qsa or QSA"` |
  |---|---|---|
  | before the fix | **2 FAILED**: 384/384 elements of the unpadded row mismatch, max \|Δ\| 0.133 | 30 passed |
  | after the fix | 2 passed | 30 passed |

  The full `tests/test_cache.py` passed with the fix (686 tests, 7 min 50 s). Pre-commit (black 26.3.1, isort 5.13.2, autoflake 2.2.1) reported no changes.
- **Optional route:** `test_qwen4_exp_ragged_qsa.py` is the same function as a standalone file.

## 8. Risk

- **Nothing re-run at the new pin.** All results are from `5cdc659b` and mlx 0.32.4. They carry over by blob identity (§1), not by execution. mlx 0.32.4 is still the newest release on PyPI.
- **bf16 is not bitwise equal to single requests.**
  - Single requests use the indexed Metal sparse kernel. Padded rows use masked SDPA, because that kernel has no notion of padding.
  - The 2026-11-05 runs measured about 1 bf16 ulp per logit (3.9e-3 at logit scale 0.9). In the tiny model, 1 of 14 positions flipped its argmax on a near-tie.
  - Equal-length batches stay bitwise identical to single requests.
  - #2126 was about bitwise singleton parity, so expect this to be the main discussion point. The fix corrects which keys are attended to. Bitwise bf16 parity for ragged rows would need a padding-aware kernel path, for example grouping rows by padding and slicing off the pad columns. That has not been prototyped.
- **Performance was not measured on real weights.**
  - Before the fix, sparse-regime ragged steps used the dense helper. On Metal with fp16/bf16 that helper is a custom kernel that reads only each row's unpadded columns through strides (#2510).
  - After the fix, those steps run masked SDPA over all key columns, pads included. They also build one boolean mask of shape `[B, 1, L, key_len]` per QSA layer per step; the real model has 12 QSA layers.
  - The extra work grows with total padding. A suggested measurement: `batch_generate` tokens/s on two prompts of about 3000 and 2990 tokens, before and after the fix.
  - Ragged long-context decode stays O(context) per step either way. Single requests use the sparse kernel.
- **Edge case: every row padded.** If all rows are padded and the padded length is past the budget while no row's visible length is, a step takes masked SDPA instead of the helper. That is still dense attention, so only rounding changes. The normal case has at least one unpadded row, because merging and `filter` remove shared padding.
- **The test does not exercise the Metal sparse kernel.** In fp32 with `head_dim=16` the kernel is never selected: it needs fp16/bf16 and `head_dim % 32 == 0`. So the test would not catch a future change that routes padded rows into it. An assertion on `select_qsa_execution_plan` (`kern:209`) could cover that if asked.
- **Pad-row block index.** `build_mask` scatters block −1 for queries with fewer complete blocks than the budget. This is harmless, because `use_sparse` is False there and the causal window replaces the selection (`q4:1077-1080`). The fix relies on `build_mask` in more places, but does not change it.
- **Maintainers may rewrite the fix.** Precedent: #2345 was closed in favour of the maintainer's own model-side #2357. This fix is model-side.
- **Out of scope; keep these out of the thread:**
  - Eagle3/DFlash verify on qwen4_exp (#2581, #2630);
  - ragged speculative rollback (#2197; unreachable from Qwen4 MTP because `q35:1473` forces uniform acceptance);
  - the audit's F1 (`indexed_attention` configs), P5 (padded batch without a cache), P3 (top-k tie order) and P4 (APC right-padding, unconfirmed).

## 9. History

The dates and authors were re-checked on 2026-11-07 with read-only `gh`.

| PR | merged | author | fact |
|---|---|---|---|
| #2032 "Add Qwen3.8-Flash-Next support" | 2026-08-26 | lucasnewman | Added the comment "The specialized left-padded decode path remains dense. It is uncommon, and preserving its row-specific cache semantics is preferable to applying an incorrectly aligned sparse mask." At that point the indexer was not padding-aware. |
| #2056 "Add continuous batching support for Qwen3.8-Flash-Next" | 2026-08-27 | lucasnewman | Made the indexer padding-aware. Added `test_left_padded_qsa_mask_matches_singleton_rows` and `test_left_padded_batched_qsa_decode_matches_singleton_rows`; the ragged decode test compared **argmax only**. D1 has been reachable since this PR. |
| #2126 "Optimize Qwen4 QSA cache reuse and batched parity" | 2026-09-04 | Blaizzy | Added the batch-invariant path, which drops the selection the same way. Replaced the "remains dense" comment with "delegate only the Q/K/V attention path to the parent". Its exact-parity evidence is equal-length only. |
| #2127 "Add GLM-5 Next support" | 2026-09-09 | Blaizzy | Refactored path B into today's `_qsa_attention`. Behaviour unchanged. |
| #2276 "Reduce test suite and drive model tests from JSON cases" | 2026-09-18 | Blaizzy | Removed `mlx_vlm/tests/test_qwen4_exp.py`, including both ragged tests. |

Accurate framing: the dense fallback began as a documented shortcut (#2032). #2056 removed its stated reason, and #2126 carried it into the new path. The tests that could have caught it checked argmax only, or equal-length batches, and were later deleted. Avoid saying "#2126 introduced it".

## 10. Notes for Ed's own text (facts, not wording)

- **Repo norms.** CONTRIBUTING has no AI rule. The visible norm is a one-line disclosure in the style of #2328. The maintainers use an "AI Slop" label. Blaizzy has redirected unsolicited PRs to "open an issue first".
- **Issue structure.** The repo's `skills/skills/reproducible-github-issues/SKILL.md` expects Summary, Environment, Model, Reproduction, Expected, Actual.
- **Value claim.** Do not claim that Qwen's README recommends mlx-vlm; that is unverified. The defensible claim is that mlx-vlm is the only MLX runtime for Flash-Next.
- **Real-model evidence.** None exists: there is no real-weight reproduction. The trigger on the real config is a ragged batch in which some row has 2052 or more visible tokens.
- **Commit signing.** A bot flags unsigned commits, and #2692/#2693 propose making signing a rule. Set up signing before pushing.
- **Commit trailers.** Keep JouleWise's Co-Authored-By and Claude-Session trailers off the upstream commit.

## 11. Independent static re-review (2026-11-07, read-only)

A second pass re-read every file:line in §4-§7 from `git show` at `a54f1a0d` and the transformers blob at `446a570e`, without running anything. Verdict: **ready-with-caveats**.

- **Bug confirmed from the code.** The chain q35:291 → q4:1112-1122 → q35:1010-1014 → q35:878-940 (mask parameter unread, dense SDPA or ragged kernel) holds for path A; q4:1871-1893 → sv:97-112 holds for path B, where `length > 1 or left_padded_decode` at sv:104 sends every padded call of 1 or 3+ tokens to the same helper. The reference merges the selection into the mask unconditionally (tf:847-852).
- **Patches verified on a temporary index** (`GIT_INDEX_FILE` + `read-tree` + `apply --cached --check`, also `--whitespace=error`): all three apply; `test_only.diff` then `fix.diff` writes tree `52657af1`, identical to `fix_plus_test.diff`; the post-image blobs are `2f6bc280` (q4) and `0e05ed60` (test_cache.py), matching the diffs' `index` lines. `fix.diff` equals the JouleWise f1e0f6673 `fix.diff` apart from the index line; the repro and test bodies equal their JouleWise originals.
- **Fix reasoning re-derived.** After the fix every padded call reaches `dispatch_qsa_attention(..., causal=False)`, which is `DENSE_MASKED` (kern:222-223) with the padding-aware `build_mask` output; `_prepare_projected_qkv` only trims the mask to the key length (q35:1081-1090), the same route the already-correct 2-token padded verify uses. Unpadded calls meet none of the new conditions (`standard_causal` at q4:1829 is True; the string mask is only produced when max padding > 0, q35:286-291), so their code is unchanged.
- **Test re-derived.** Prompts of 14 and 11 tokens with `indexer_budget=8`, `compress_ratio=4` give `block_topk=2`; at the first decode step both rows have 3 complete blocks, so both are sparse while the batch is dense before the fix, and 384 = 6 positions × 64 vocab is the expected mismatch count for row 0. `decode_path="attention"` reaches path A only for the three decode steps; the verify always uses path B (q4:2184-2210). The repro's `TextConfig` keys all exist with compatible defaults (`indexer_kv_heads=1`, `mtp_num_hidden_layers=1`, `ple_layer_ids=[]`).
- **Caveats carried into Ed's text.** (1) Test placement: the repo's `skills/skills/contributing/SKILL.md` asks for a class in `test_models.py`; the kit puts the function in `test_cache.py`, where the other 30-odd qwen4/QSA batch-cache tests already live (`test_models.py` has one). Expect a possible request to move it. (2) bf16 is about 1 ulp off, not bitwise (§8). (3) Performance on real weights is unmeasured (§8). (4) The CI "Validate test groups" step (tests.yml:38-61) rejects any `tests/test_*.py` not listed in a group, so the standalone test file must not be committed.
- **Kit edits made by this pass.** RUN-ME §0 `__init__.py` description corrected (it imports most of the package, not three modules); RUN-ME step 5 now checks the two post-patch blob ids with `git hash-object` and treats the `diff -u` as informational; RUN-ME §8 asks Ed to `pip freeze` the pre-existing `/private/tmp/jwsol` venv before trusting it; RUN-ME §9 gained the matching mismatch rule; `repro_d1.py` header made precise about the docstring; this section added; `SHA256SUMS` regenerated.

## Static review

Reviewer verdict (independent read-only static review, 2026-11-07): **ready-with-caveats**. Nothing upstream was executed, built, installed or imported; the kit has not been run (status UNRUN).

Review text as relayed to the lead by the workflow. The relay cut the text off partway through, so it ends mid-sentence; any corrections the reviewer made are already in the kit files above.

```text
VERDICT: ready-with-caveats

Static review of /private/tmp/jwoss-ro/mlx-vlm-d1/kit/ against upstream a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4 (read via `git show` on /private/tmp/jwoss-ro/mlx-vlm-d1/src and /private/tmp/jwoss-ro/mlx-vlm-d1/ref/tf; nothing executed, installed or imported).

WHAT WAS VERIFIED
- Bug is real as described. Every file:line in the fact sheet re-read and correct: q35:291 produces "left_padded_decode"; q4:1112-1122 returns to the parent; q35:1010-1014 sets mask=None and calls `_qwen3_5_left_padded_attention` (q35:878-940), whose `mask` parameter (q35:885) is never read. Path B: q4:1871-1893 keeps the string through the merge, sv:97-101 nulls it, sv:104 sends every `length > 1 or left_padded_decode` call to the same dense helper. Ragged 2-token verify takes the lower path with causal=False → DENSE_MASKED (kern:222-223), so it is already correct. Padding decision is per batch (q4:1828-1829). `build_mask` (q4:1042-1081) is padding-aware. Reference merges unconditionally (tf:847-852; indexer at tf:711-756).
- Patches apply to a54f1a0d: checked on a temporary index (`GIT_INDEX_FILE` + `read-tree` + `apply --cached --check`, also `--whitespace=error`). fix.diff, test_only.diff, fix_plus_test.diff all apply; test_only + fix writes tree 52657af1 == fix_plus_test tree; post-image blobs 2f6bc280 (language.py) and 0e05ed60 (test_cache.py) match the diffs' index lines. fix.diff equals JouleWise f1e0f6673's fix.diff apart from the index line; repro and test bodies equal their JouleWise originals.
- Fix addresses the root cause: after the fix every padded call reaches `dispatch_qsa_attention(..., causal=False)` → DENSE_MASKED with the padding-aware mask; `_prepare_projected_qkv` only trims the mask to key length (q35:1081-1090), the same route the already-correct 2-token padded verify uses. Unpadded calls meet none of the new conditions (`standard_causal` True at q4:1829; string mask only when max padding > 0, q35:286-291) so their code is unchanged. Hunk 2 uses `standard_causal` which is in scope at q4:1829.
- Test fails-before/passes-after by derivation: block_topk = 8/4 = 2; rows of 14 and 11 tokens both have 3 complete blocks at the first decode step → sparse singly, dense batched before the fix; 384 = 6 positions × 64 vocab matches the recorded mismatch count. `decode_path="attention"` reaches path A for decode only; verify always uses path B (q4:2184-2210). Imports/aliases exist at test_cache.py:45, :87, :1592; `lm.model.fa_idx` (q4:1598), `self_attn.indexer`, `indexer.block_topk` (q4:824) exist. Repro's TextConfig keys exist with compatible defaults (indexer_kv_heads=1 required and defaulted; mtp_num_hidden_layers=1; ple_layer_ids=[]).
- RUN-ME sandbox: fresh clone with `core.hooksPath=/dev/null`, fresh venv under /Users/edr/code/CapstoneProject/jw-wt/, offline env after install, `[test]` extra exists in pyproject (setuptools backend, no setup.py), version.py = "0.7.12", requirements as described, CI runs test_cache.py from the
[relayed excerpt ends here]
```
