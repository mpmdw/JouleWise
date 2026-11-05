# Walkthrough: the D1 fix and its regression test, line by line

Read this alongside `fix.diff` and `test_qwen4_exp_ragged_qsa.py`. All line numbers refer to `mlx_vlm/models/qwen4_exp/language.py` at mlx-vlm main `5cdc659b` (the "before" file) unless they say otherwise. `FACT_SHEET.md` has the background: what QSA is, the history and the numbers.

## 0. Vocabulary you need first

- **QSA indexer.** The small module that picks which 4-token key blocks each query may attend to. It runs in two steps:
  - `select_from_projected()` (`:878`) scores the blocks and returns a `selection` object: the chosen block ids per query, the query end positions, each row's left padding, and so on.
  - `build_mask(selection)` (`:1042-1081`) turns that selection into a boolean mask over the key axis, shaped `[batch, 1, queries, keys]`.
- **Left padding.** In a batch, shorter prompts are padded on the left with dummy tokens, so that all rows end at the same column. The cache records each row's pad count in `cache.left_padding`. A batch where any row has padding is called **ragged**.
- **The `"left_padded_decode"` string.** For a one-token decode step on a ragged cache, Qwen3.5's mask builder does not return a boolean array. It returns this string instead (`qwen3_5/language.py:278-292`, the return is at `:291`). The string tells the attention code: "call the special ragged helper `_qwen3_5_left_padded_attention`" (`qwen3_5/language.py:878-940`). That helper slices each row's pads off its keys and runs plain dense attention. Its `mask` argument (`:885`) is never read.
- **Two decode paths.**
  - **The attention module.** `Qwen4ExpAttention.__call__` (`:1091` onward). Decode uses it when the model's `lm_head` is quantized in a format the batch-invariant forward does not support. For example, a 6-bit head fails `supports_optimized_affine_head`, which accepts 4-, 5- and 8-bit affine heads only.
  - **The batch-invariant forward.** `Qwen4ExpBatchInvariantForward._qsa_attention` (`:1827-1956`). This is the default for decode, and it is the *only* path for MTP speculative verify (`_speculative_verify`, `:2184-2218`).
- **The dispatcher.** `dispatch_qsa_attention(..., causal=..., mask=...)` (`qsa_kernel.py:349-396`). With `causal=False` it always picks the plain path: masked scaled-dot-product attention (`qsa_kernel.py:222-223`, plan `DENSE_MASKED`). With `causal=True` it may pick a fast Metal kernel that knows nothing about padding. That is why every padded call below must pass `causal=False`.

The whole bug, in one sentence: on a ragged cache, both paths compute `selection`, then hand the call to the ragged helper, which attends to every key and ignores the selection.

The whole fix, in one sentence: on a ragged cache, both paths instead use `build_mask(selection)` as the attention mask and take the existing `causal=False` masked path. That mask already accounts for each row's left padding.

---

## 1. `fix.diff`, hunk 1: the attention module (`Qwen4ExpAttention.__call__`)

Context lines 1099-1107, unchanged:

```python
selection = self.indexer.select(x, cache, position_ids)
if selection is None:
    return super().__call__(...)
```

`select()` returns `None` only for a 1-token step whose whole key history fits the budget, which means no row can be sparse yet. Dense attention is then exactly right. The parent call also handles `"left_padded_decode"` correctly in that case, so it stays.

```python
        standard_causal_mask = mask is None or (
            isinstance(mask, str) and mask == "causal"
        )
```

Unchanged. `True` when the incoming mask adds nothing beyond plain causality: either there is no mask (one-token decode, no padding), or the mask is the string `"causal"`.

Removed lines 1112-1122:

```python
-        if isinstance(mask, str) and not standard_causal_mask:
-            # Qwen3.5 owns specialized string modes such as
-            # ``left_padded_decode``. ...
-            return super().__call__(x, mask=mask, cache=cache, ...)
```

**This is the bug on this path.** At this point `selection` has already been computed. Returning `super().__call__` sends the call to `Qwen3_5Attention.__call__`, which sees `"left_padded_decode"`, sets `mask = None` (`qwen3_5/language.py:1011`), and calls the dense ragged helper. `selection` is never used. The only string other than `"causal"` that can reach this line is `"left_padded_decode"`. Its only producer is `qwen3_5/language.py:291`, and Qwen4's mask builders otherwise return `None`, `"causal"` or an array. So the branch had exactly one effect: dropping the selection on ragged decode.

Added:

```python
+        # The parent's ``left_padded_decode`` path is dense and ignores masks.
+        # build_mask() already offsets each row's blocks by its left padding
+        # and hides the pad columns, so it is the whole mask for that step.
+        left_padded_decode = isinstance(mask, str) and mask == "left_padded_decode"
```

The comment states the reason for the change, and the line gives the condition a name. `isinstance(mask, str)` comes first: comparing an `mx.array` with a string using `==` would not give a plain `bool`.

```python
         sparse_candidate = selection.zero_padding and standard_causal_mask
         qsa_mask = None if sparse_candidate else self.indexer.build_mask(selection)
```

Unchanged. On a ragged cache, `selection.zero_padding` is `False` (it is computed from the same `left_padding` at `:906-908`). So `sparse_candidate` is `False`, and `build_mask(selection)` runs. `qsa_mask` is therefore always an array on this path.

```python
         if qsa_mask is not None:
-            if standard_causal_mask:
+            if standard_causal_mask or left_padded_decode:
                 mask = qsa_mask
```

Before, a string mask could never get here. Now `"left_padded_decode"` gets the same treatment as `None` and `"causal"`: the QSA mask *replaces* the incoming mask. Replacing, rather than AND-ing, is correct because `build_mask` already encodes everything the string stood for. Look at `build_mask`:

- `:1053-1057`: the selected token columns are `left_padding + block * 4 + {0,1,2,3}`, so blocks are counted from each row's first real token, not from column 0.
- `:1070-1073`: the incomplete "tail" block starts at `left_padding + complete_blocks * 4` and ends at the query.
- `:1074-1076`: for rows that are not yet sparse, the mask is `left_padding <= key < query_end`. That is causal attention with the pads hidden.
- `:1077-1080`: each row and query gets the sparse version only if it has more complete blocks than the budget allows.

Pad columns are therefore `False` in every case. That is exactly what the dense ragged helper achieved by slicing them off.

The `elif isinstance(mask, mx.array)` branch below is unchanged: it ANDs explicit array masks, as before.

Lines after the hunk, unchanged but load-bearing:

- `_prepare_projected_qkv(..., None if sparse_candidate else mask)`: `sparse_candidate` is `False`, so our array mask is passed. That function trims it to the current key length (`qwen3_5/language.py:1081-1090`; for a batch cache, `cache._idx + L`). It also appends this step's keys and values to the cache, exactly once, just as the parent did.
- `dispatch_qsa_attention(..., causal=standard_causal_mask, mask=mask)`: `standard_causal_mask` is `False` for `"left_padded_decode"`, so the dispatcher chooses `DENSE_MASKED` (`qsa_kernel.py:222-223`). That plan runs masked SDPA over the padded keys with our mask. The fast Metal kernel, which has no notion of padding, is never chosen for padded rows.

**Net effect of hunk 1:** a ragged decode step through the attention module now attends to the selected blocks and the tail, as the reference does. All other inputs follow exactly the same lines as before.

---

## 2. `fix.diff`, hunk 2: which branch the batch-invariant forward takes

Some context from `_qsa_attention` first:

- `:1828-1829` sets `standard_causal = padding_info is None or padding_info[1] == 0`, meaning "this cache has no left padding". This is the value hunk 2 reads.
- `:1845-1869` splits wide unpadded calls into pairs. It requires `standard_causal`, so it never fires for ragged caches.

```python
         projected = self._linear(attention.indexer.index_qk_proj, hidden_states)
-        if hidden_states.shape[1] > 2 or (
-            isinstance(mask, str) and mask == "left_padded_decode"
-        ):
+        # Batches with any left padding skip this branch: _attention() would
+        # send them to the dense ragged helper, which ignores the QSA mask.
+        if hidden_states.shape[1] > 2 and standard_causal:
             qsa_mask = attention.indexer.from_projected(projected, cache, position_ids)
             ...merge qsa_mask into mask...
             return self._attention(attention, hidden_states, mask, cache, position_ids, None)
```

What the old condition sent into this "upper branch":

| call | old route | what `_attention` then did |
|---|---|---|
| unpadded, more than 2 tokens | upper | per-query masked SDPA. Correct; this branch was built for this case |
| **ragged, 1 token** (`"left_padded_decode"`) | upper | `qsa_mask` built, but the string is not merged (`:1876` only merges `None`/`"causal"`/arrays). `_attention` sees the string and calls the dense ragged helper (`speculative_verifier.py:97-112`). **Selection dropped.** |
| **ragged, more than 2 tokens** (verify) | upper | `qsa_mask` merged into the boolean array. `_attention` sees `length > 1` and calls the dense ragged helper (`speculative_verifier.py:104-112`), which ignores the array. **Selection dropped.** |
| ragged, exactly 2 tokens | lower | correct already (see hunk 3) |

The new condition keeps only the first row in the upper branch. Every ragged call now takes the "lower" selection path at `:1895-1956`, which ragged 2-token verify already used correctly. `standard_causal` here is still the padding-based value from `:1829`. The variable is reassigned only later, at `:1915`, so this line reads the right value.

Why the lower path is right for ragged calls:

- `:1895-1913`: if `select_from_projected` returns `None`, or the whole key history fits the budget, it calls `_attention(... mask ...)` with the original mask. For a ragged cache that is the dense ragged helper, which is exact here because no row can be sparse. For the prefix-fits case this route is bitwise identical to the old one: the old upper branch also ended in the same helper, and the helper ignored the extra mask.
- Otherwise it builds `qsa_mask`, merges it (hunk 3), and calls `dispatch_qsa_attention(..., causal=standard_causal, ...)` with `standard_causal = selection.zero_padding = False`. That is `DENSE_MASKED`: masked SDPA with the QSA mask.

The indexer is still updated exactly once per call. The old branch did it through `from_projected`, which calls `select_from_projected`; the new route calls `select_from_projected` directly.

---

## 3. `fix.diff`, hunk 3: merging the string mask in the lower path

```python
         standard_causal = selection.zero_padding
         sparse_candidate = standard_causal
         qsa_mask = None if sparse_candidate else attention.indexer.build_mask(selection)
         if qsa_mask is not None:
-            if standard_causal:
+            if standard_causal or (
+                isinstance(mask, str) and mask == "left_padded_decode"
+            ):
                 mask = qsa_mask
             elif isinstance(mask, mx.array):
                 ...AND / additive bias, unchanged...
```

Before hunk 2, a ragged one-token call never reached this code, so `mask` here was never the string. Now it can be. Without this change, the string would fall through both branches and reach `_prepare_projected_qkv` and SDPA as a string. As in hunk 1, `build_mask` already encodes the causal bound and the pads, so it replaces the string. Ragged calls with more than 2 tokens arrive with a boolean array and take the unchanged `elif` (AND).

A reviewer may notice that `standard_causal` is always `False` inside `if qsa_mask is not None:`, because `qsa_mask` is built only when `sparse_candidate` (equal to `standard_causal`) is `False`. That pre-existing dead condition is left untouched to keep the diff minimal. Two equivalent refactors are available if a maintainer prefers:

- `if not isinstance(mask, mx.array): mask = qsa_mask`;
- naming the string test as a local `left_padded_decode`, as hunk 1 does.

---

## 4. Why nothing else changes (the safety argument)

Every changed line is reachable only when the batch cache has left padding:

- **Single requests** use `QSAKVCache`, which has no `left_padding`. So `_qwen3_5_left_padding_info` returns `None`, `standard_causal` and `zero_padding` are `True`, and the mask is never `"left_padded_decode"`. Hunk 1's new name is `False`, hunk 2's condition reduces to the old `shape[1] > 2`, and hunk 3's new disjunct is `False`.
- **Equal-length batches** (`BatchQSAKVCache` with all pads 0): `_qwen3_5_left_padding_info` gives a maximum of 0, so the code behaves as in the single-request case. `_create_qwen3_5_attention_mask` returns `None` for one-token decode (`qwen3_5/language.py:288-289`), and `_create_qwen4_exp_attention_mask` returns `None` or `"causal"` (`:1564-1582`).
- **Multi-row prefill** of a ragged batch runs row by row on the unpadded rows (`:1624-1711`), so it never sees padding. A one-row cache that still has left padding, or a call that captures hidden states, skips that split and reaches the attention module with a boolean array mask. That path already merged the QSA mask and used masked SDPA, and it is unchanged.
- **Ragged steps while every row still fits the budget** go to the same dense ragged helper as before (hunk 2 notes). That holds whenever some row has zero padding, the normal case after a merge or filter. If every row were padded, a step whose padded length exceeds the budget while no row's visible length does would now use masked SDPA: still dense, rounding-level only.

This was checked bitwise. `evidence/nonreg.py` compared before and after on single requests, equal-length batches and short ragged batches: fp32 and bf16, both decode paths, verify blocks of 2 and 3 tokens. The arrays are identical (see `FACT_SHEET.md`).

---

## 5. The regression test, line by line (`test_qwen4_exp_ragged_qsa.py`)

```python
import mlx.core as mx
import numpy as np
import pytest

from mlx_vlm.generate.ar import _make_cache
from mlx_vlm.tests.test_models import build_config, model_case
```

These are the same imports `mlx_vlm/tests/test_cache.py` already has (its lines 41-46 and 87). `model_case` returns a fresh deep copy of a test case from `mlx_vlm/tests/model_cases.json`. `build_config` turns a dict into the model's config dataclass. `_make_cache` is what `BatchGenerator` uses to turn a model's per-request caches into batch caches with given left padding.

```python
@pytest.mark.parametrize("decode_path", ["batch_invariant", "attention"])
def test_qwen4_exp_ragged_batch_matches_single_requests(decode_path):
```

The test runs twice, once per decode path, because the fix touches both. The parameter values become the test ids: `[batch_invariant]` and `[attention]`.

```python
    from mlx_vlm.models import qwen4_exp
```

This is a local import, matching the repo's own fixtures (for example `mistral_large4_language` in `test_cache.py` and `flint_model` in `test_models.py`).

```python
    fields = model_case("qwen4_exp")["config"]["text_config"]
    fields["indexer_n_heads"] = 16
```

This reuses the repo's own tiny `qwen4_exp` case: 2 layers (DeltaNet + QSA), `indexer_budget=8`, `indexer_compress_ratio=4`. That follows CONTRIBUTING: "Specialized tests reuse case configs". The single override matters. With one indexer head, a block's score is `relu(q·k)`, which is exactly 0 for about half the blocks. Several blocks then tie at 0, and `argpartition` may break the tie differently in a padded row, whose score array is longer. Sixteen heads make an exact-zero tie very unlikely (all 16 dot products would have to be negative), so the selection is unique. The test then checks the bug, not the tie order. `model_case` returns a deep copy, so changing it does not leak into other tests.

```python
    mx.random.seed(17)
    lm = qwen4_exp.LanguageModel(build_config(qwen4_exp, fields, "TextConfig"))
    lm.eval()
```

Seeding makes the random weights deterministic. Only the language model is built; no vision tower is needed. `lm.eval()` puts the model in inference mode, as the neighbouring `test_qwen3_5_single_row_decode_retains_batch_cache` does. MLX modules start in training mode, and the Gated DeltaNet layers choose their Metal kernel with `use_kernel=not self.training` (`qwen3_5/language.py:1241`). Without `eval()` the test would run a code path that real inference does not use.

```python
    if decode_path == "attention":
        lm._supports_batch_invariant_decode = lambda: False
```

`LanguageModel.__call__` uses the batch-invariant forward for decode only when `_supports_batch_invariant_decode()` returns `True` (`qwen3_5/language.py:1872-1892`). Overriding it on this instance forces decode through `Qwen4ExpAttention.__call__`, the path a 6-bit head would take. Verify still uses the batch-invariant forward in both variants, because `speculative_verify_logits` always does.

```python
    prompts = [list(range(1, 15)), list(range(20, 31))]
    indexer = lm.model.layers[lm.model.fa_idx].self_attn.indexer
    assert (len(prompts[1]) + 1) // indexer.compress_ratio > indexer.block_topk
```

The two prompts have 14 and 11 tokens, so the batch has left padding `[0, 3]`. QSA keeps `block_topk = 8 // 4 = 2` complete blocks. A query is sparse once it sees more than 2 complete blocks, that is at least 12 tokens. At the first decode step the short row sees 11 + 1 = 12 tokens, which is 3 blocks, more than 2. The `assert` documents this, and it fails loudly if someone later changes the shared JSON case so that the test would silently stop exercising sparse attention. The long row is sparse from the first step too (15 tokens).

```python
    def run(rows, cache):
        width = max(map(len, rows))
        ids = [[0] * (width - len(r)) + r for r in rows]
        positions = [[0] * (width - len(r)) + list(range(len(r))) for r in rows]
        lm(mx.array(ids), cache=cache, position_ids=mx.array(positions))
```

This prefills the batch. Each row is left-padded with token 0. Each row's positions are `0..n-1` for its real tokens, and the pad positions hold 0. The pad positions are never used, because prefill runs row by row on the unpadded slice. Passing `position_ids` explicitly mirrors what `BatchGenerator` forwards, and it keeps `LanguageModel`'s internal RoPE state (`_position_ids`, `_rope_deltas`) out of the test. For a single row, `width - len(r)` is 0, so the same code serves the single-request runs.

```python
        logits = []
        for step in range(3):
            tokens = mx.full((len(rows), 1), 40 + step)
            positions = mx.array([[len(r) + step] for r in rows])
            logits.append(lm(tokens, cache=cache, position_ids=positions).logits)
```

Three one-token decode steps, all with the same fixed tokens (teacher forcing). The batch and the single runs therefore see identical inputs, and any difference comes from the model. Each row's position is its own real length plus the step. These calls produce the `"left_padded_decode"` mask in the ragged case.

```python
        block = mx.array([[43, 44, 45]] * len(rows))
        logits.append(lm.speculative_verify_logits(block, cache, lambda x: x)[3])
        return mx.concatenate(logits, axis=1)
```

A 3-token speculative verify block, as MTP decoding sends it. The sampler `lambda x: x` returns the raw logits, which are the 4th element of the returned tuple. This covers the ragged multi-token path of hunk 2. The result has shape `[rows, 6, vocab]`: 3 decode steps plus 3 verify positions.

```python
    actual = run(prompts, _make_cache(lm, [0, 3]))
    for row, prompt in enumerate(prompts):
        expected = run([prompt], lm.make_cache())
        np.testing.assert_allclose(
            np.array(actual[row : row + 1]), np.array(expected), atol=1e-5, rtol=1e-5
        )
```

- `actual`: the ragged batch, with the batch cache that `BatchGenerator` would build (`_make_cache(lm, [0, 3])`).
- `expected`: each prompt alone, with the ordinary single-request cache (`lm.make_cache()`).
- The assertion: each batch row must match its single-request run. This includes row 0, which has no padding, because the bug changed every row of a ragged batch.

The tolerance is `1e-5` in fp32. The fixed code is within about 3e-7, and the bug produces about 1e-1. The test suite's `conftest.py` sets `MLX_ENABLE_TF32=0`, so fp32 matmuls are true fp32. `np.testing.assert_allclose` is used instead of `mx.allclose(...).item()` because on failure it prints the largest difference, which makes a failure easy to read.

**Before the fix**, both parameters fail: about 1e-1 off, with 100% of row 0's logits mismatched. **After**, both pass. Numbers are in `FACT_SHEET.md`.

---

## 6. `repro_minimal.py` in one paragraph

It uses the same tiny model as the test, written out inline so that it needs nothing but `pip install mlx-vlm`, and the same `run()` routine. It sets `MLX_ENABLE_TF32=0` before importing MLX, as the test suite's `conftest.py` does, so its fp32 threshold also holds on GPUs whose fp32 matmuls would otherwise run at TF32. It also calls `lm.eval()`. It runs each decode path, prints per row the largest logit difference between the ragged batch and the single-request runs for the decode steps and for the verify block, and adds an equal-length batch as a control. It exits 1 if any ragged difference exceeds `1e-4`. The control shows that padding is the trigger: equal-length batches are exact before and after the fix.
