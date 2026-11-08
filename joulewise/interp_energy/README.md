# Fixed-token replay (desk tool, provisional native path)

This implements the Stage 0 replay primitive from
[`interp-weight-edit-energy.md`](../../docs/research-audits/2026-11-07/interp-weight-edit-energy.md).
It is synthetic/desk software evidence only. It does not launch telemetry,
schedule a measurement window, edit weights, or run an energy analysis.

Run a tiny causal-attention model without MLX (requires NumPy):

```sh
python3 -B scripts/interp_energy/forced_decode.py --dry-run --output /tmp/synthetic-replay.jsonl
```

For a later authorized native software session, supply an existing local mlx-lm
safetensors directory and JSON arrays of exact prompt/continuation IDs:

```sh
python3 -B scripts/interp_energy/forced_decode.py \
  --model /path/to/local/model --prompt-tokens /path/to/prompt.json \
  --tokens /path/to/fixed-continuation.json --top-k 5 \
  --prefill-chunk-size 512 --output /path/to/new-replay.jsonl
```

The loader is local-only, with offline flags and a local-only tokenizer. No
hub identifiers or model downloads are supported. `--prompt TEXT` is an
alternative to `--prompt-tokens`; it uses raw encoding with
`add_special_tokens=False`, without applying a chat template. For a paired
experiment, save the actual baseline prompt IDs, including its special tokens,
and reuse those IDs in both arms. Output files are created exclusively.

The Python API accepts already-loaded models, including in-process weight edits:

```python
from joulewise.interp_energy.forced_decode import MLXBackend, replay

result = replay(
    model, prompt_ids, fixed_continuation_ids,
    model_weights_sha256=current_weights_digest, vocab_size=vocab_size,
    backend=MLXBackend(), top_k=5, prefill_chunk_size=512,
)
result.write_jsonl(output_stream)
```

The caller must supply the digest of the **current** weights after every edit,
using the same hashing convention across arms. This is explicitly marked
`caller-asserted`. The CLI instead hashes every root-level `*.safetensors` file,
then hashes a canonical JSON manifest of sorted filenames, byte counts and
file SHA-256 digests. The manifest is in the header, along with the config file's
SHA-256. This is an on-disk weights identity, not proof about later in-memory
mutations. No model name is substituted for a weights hash.

The loop calls `model.eval()` and materializes parameters before timing. Every
replay obtains a fresh `mlx_lm.models.cache.make_prompt_cache(model)`, preserving
model-specific cache implementations. It prefills `prompt[:-1]` in fixed-size
chunks; step zero feeds `prompt[-1]` and scores `forced[0]`; step i feeds
`forced[i-1]` and scores `forced[i]`. Each decode call is `[1, 1]`. No sampled or
argmax token is ever fed back, no EOS terminates replay, and no cache is reused,
trimmed or explicitly quantized. Like ordinary generation, the final forced
token is emitted/scored but remains outside the cache. The footer's
`cache_input_token_count` counts logical consumed IDs, not allocated cache slots.

JSONL has a `replay` header, one `token` row per fixed token, and a `complete`
footer. Missing footers indicate incomplete output. Every row carries model,
prompt, continuation and replay-policy hashes. Token hashes are SHA-256 over
compact JSON integer arrays (e.g. `[1,2]`, no whitespace/newline). Match prompt,
continuation, vocabulary, runtime versions and policy across arms. Only the
weights identity should vary for a weight-only comparison; the loop does not
adjudicate experimental validity or enforce model topology/dtype equivalence.

Per-token fields include consumed/forced IDs, logical context length, monotonic
nanosecond forward start/completion, diagnostic completion, forward duration,
argmax agreement, the forced token's full-vocabulary normalized natural-log
probability, top-k token IDs/log-probabilities, and forced-token top-k membership.
`top_k` is clipped to vocabulary size. The forced token is scored even when
outside top-k. Tied top-k boundary membership is backend-defined; selected ties
are displayed in token-ID order. Use one backend/runtime version across arms.
No random operation occurs in replay; deterministic outputs assume a
deterministic inference model/backend. Timestamps naturally differ across runs.

MLX forward completion evaluates logits **and all cache states** so lazy work
does not spill past the timestamp. Prefill materializes cache state and discards
lazy logits. Diagnostics run after each completed forward, using float32 on MLX
and float64 normalization in the NumPy reference; JSON serialization and file
writes run after replay. Diagnostic kernels, sorting and host bookkeeping still
add work between forwards. This synchronous instrumented loop does not reproduce
mlx-lm's asynchronous pipeline timing, and whole-loop energy includes diagnostics.
Keep this policy identical across arms and assess its overhead in the later
A/A pilot before making a switching-channel bound. No energy claim follows from
these tests.

Run targeted modules individually:

```sh
python3.13 -B -m unittest tests.interp_energy.test_forced_decode -v
python3.13 -B -m unittest tests.interp_energy.test_reference -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
```

The NumPy tests skip when NumPy is absent. The native tests are gated on MLX and
mlx-lm package availability and require a functioning Metal device; they build
a tiny llama from configuration, with no weights download. The lead must run
that native module outside this sandbox in an authorized software session. It
checks greedy `generate_step` parity, full-forward forced scores, exact A/A
repetition, tie repeatability, and cache offsets. Native hybrid/Qwen3.5 support
and real-model local loading remain unverified; their model-specific caches are
passed through without substitution. Any later real-model or measurement gate
remains with the lead.
