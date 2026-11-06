# P10 review: qwen4_exp expert streaming (commit 30928600c)

Reviewer: Claude Opus 5.5 (subagent), 2026-11-06. Read-only review. Nothing was pushed.
Reference behaviour: the canonical module at the parent commit 65763077a and docs/align/qwen4_exp_port/canonical.md.

## Verdict: ADMIT_WITH_FIXES. Not fit for Saturday as-is.

The record layout and the per-row maths match the canonical resident path. I checked this by tracing the code and with an executed probe. The default resident path is behaviourally unchanged (traced).

The streaming forward has one blocking defect, F1. In a token-major loop, LRU thrash re-reads experts. Each re-read creates a new array that the lazy graph keeps alive until the next layer syncs. The result is unbounded host memory and terabytes of reads per prefill. On the 128 GB MBP, a forward pass of about 512 tokens or more risks running out of memory or swapping. A 2048-token prefill chunk certainly will.

The streamed 48-layer gold validation does not use this path. The gold adapter is pinned to the parent commit 65763077a, and its own unit converter builds resident experts. The only effect on gold is the pin rebind (F2).

## Findings

| # | Sev | Location | Failure scenario | Fix |
|---|---|---|---|---|
| F1 | CRITICAL | joulewise/align/models/qwen4_exp.py:1650-1660 (with get() at 1614-1637) | Prefill of T tokens makes T*k get() calls in token order. The working set (≈ every one of the 512 experts) exceeds the per-layer capacity of 91 at 32 GiB, so most calls miss. Each miss allocates a new 7.5 MiB pair. The pairs evicted from the LRU stay alive through the unevaluated `rows` graph until the next layer's `np.asarray(indices)`. Executed sim: T=512 gives 2.9k-4.3k misses, so 22-31 GiB read and kept per layer. T=2048 (mlx-lm's default prefill chunk) gives 11.5k-17k misses, so 84-125 GiB per layer and 4-6 TiB per chunk across 48 layers. The result is running out of memory or swap on 128 GB, and the doc's claim that "eviction drops the only MLX arrays" is false within a call. | Dedupe per call: `uniq, inv = np.unique(flat_i, return_inverse=True)`, then one get() per unique expert and one batched `[n_e,H] @ gu.T` per expert over its rows. Then un-permute and reshape (B,L,k,H). Optionally run `mx.eval(y)` before returning. The transient is then at most 512 x 7.5 MiB = 3.75 GiB per layer, and reads are at most the unique count. Document that transient on top of cache_gb. |
| F2 | HIGH (process) | scripts/align_convert_qwen4_exp.py:53; docs canonical.md:283 | MODULE_SHA256 changes from f4ec75d… to cba1bda… (verified by shasum). The mbp-live lane converter pins f4ec75d, and the gold adapter pins COMMIT 65763077a (MODULE_SHA256 f4ec75d in tests/test_qwen4_gold_canonical_adapter.py:27). If P10 is merged before Saturday, an artifact converted on one side fails `load_verified_model` ("artifact module … is not the pinned module"). The gold evidence would then also attest a different module sha from the one converted. | Keep P10 out of the pinned canonical module until Saturday's conversion and gold are done. Otherwise merge first, rebind the gold adapter COMMIT/MODULE_SHA256 and the mbp-live converter, and re-run the canonical fixture. |
| F3 | MEDIUM | tests/align/test_qwen4_exp_expert_streaming.py:80-85 | There is no native coverage of StreamingFusedSwitchGLU or of `convert(expert_streaming_cache_gb>0)`. The "Metal" test is `assertTrue(True)` and claims the canonical fixture covers it, but test_qwen4_exp_canonical.py never mentions expert_streaming. The CPU test writes its own records and never exercises the converter or the forward. | Add a native test. Convert the tiny fixture with `--profile bf16 --expert-streaming-cache-gb <tiny>`, load it through `load_verified_model`, and compare with the resident bf16 artifact on prefill, stepwise decode and padded batch, with a cache small enough to force eviction. Delete the placeholder. |
| F4 | MEDIUM | qwen4_exp.py:1644 (docstring "exact-quality"); docs expert_streaming.md | Streamed bf16 uses per-row gemv and the resident path uses gather_mm. The rounding points are the same, but the fp32 accumulation order can differ, so streamed and resident logits are not guaranteed to be bit-identical. A harness that asserts equality fails spuriously. | Call the path "same rounding points, kernel-order differences" and compare it with the existing bf16 bound (or tie-aware argmax), never with equality. |
| F5 | LOW | scripts/align_convert_qwen4_exp.py:524-527 | The profile check runs after `output.mkdir`, so a non-bf16 profile leaves an empty output dir. The rerun then fails with "output directory must not exist". | Move the check before mkdir. Also refuse negative values. |
| F6 | LOW | qwen4_exp.py:1597-1612 | The reader ignores `format`, `experts` and `size_bytes`. A future q8 record file (the doc invites one) would be decoded as bf16 garbage without an error. A truncated file fails only when it reaches a tail expert, possibly hours into a run. | At construction, require format == "bf16" and fstat size == experts * bytes_per_expert. |
| F7 | LOW | scripts/align_convert_qwen4_exp.py:584-589 | A checkpoint in the HF fused serialization (`experts.gate_up_proj`, which `sources()` supports) gives a one-entry inventory, so `gu[1]` raises IndexError. That happens only after every resident shard has been written. The released checkpoint is per-expert, so this does not apply to it. | Check that the entries are `kind=="expert"` before writing anything. Otherwise support the fused layout by row slices. |
| F8 | LOW | qwen4_exp.py:1604 | The 48 fds are never closed, so a process that reloads the model leaks 48 fds per load. The OrderedDict is not thread-safe if two threads run forwards on one model. | Add close() and `__del__`, and document single-threaded use (or add a lock). |
| F9 | LOW | qwen4_exp.py:1615-1622, 1639 | Counters count every (token, slot) access, prefill included, and have no reset. A hit rate computed from them will not match the doc table's per-token decode model. | Count per unique expert per call, split prefill and decode, and add reset(). |
| F10 | INFO | docs expert_streaming.md:34-36 | Affine q8 group-64 with a bf16 scale and bias is 3.98 MiB per expert (95.6 GiB in total), not 3.87 MiB (92.8 GiB). 3.87 counts only one of scale and bias. The projected q8 rows move by about 3%. | Correct the arithmetic. |
| F11 | INFO (ops) | convert() streaming branch | A streaming conversion needs the full bf16 checkpoint (~360 GB) and ~345 GB of output on disk at the same time. That fits only on the external SSD, not the 1 TB internal streaming-gold plan. Each verified load re-hashes another 180 GiB. Expert bytes are read hours after `_check_unchanged`, which is the same residual window as lazy=True. | Plan the disk use. Note the residual window in the docs. |

## Traced vs executed

Executed (pure numpy, `nice -n 19 taskpolicy -b`, no MLX):
- `python3 -m unittest tests.align.test_qwen4_exp_expert_streaming`: 3/3 OK. Its coverage is limited (F3).
- Scratch probe (scratchpad/p10/probe.py). It used a numpy per-expert bf16 safetensors fixture (keys in shuffled order, two shards), the real `conv.sources` and `conv.tensor_chunks`, and the converter's streaming write loop copied verbatim. Read back through the production `ExpertStream` (exec'd from source with a fake mx), gate, up and down were bit-exact (`layout_round_trip_exact True`).
- An LRU simulation of get()'s control flow at the released shape (91 per layer, 512 experts, top-10, uniform and zipf-0.8 routing) gave the miss and retention figures in F1.
- The module sha256 equals cba1bda… and the parent's equals f4ec75d….

Traced only:
- Per-row maths, (B,L,k,H) ordering, rounding points, and the dtype chain (bf16 → f32 → bf16 is exact).
- mx.array copies numpy, so there is no aliasing. Each layer owns its cache, so there is no cross-layer staleness.
- The resident path is unchanged, and the strict load works with the switch_mlp tensors omitted.
- `__file__` resolves to the artifact under both `load_verified_model` and the mlx-lm model_file hook.
- The gold adapter is pinned to the parent commit and constructs `DecoderLayer(args, i)`, which is compatible.
- MLX 1-D matmul is assumed to be supported (to be confirmed natively).

## Native tests for the lead (after the analysis finishes)
1. The existing canonical suite at this head: `tests/align/test_qwen4_exp_canonical.py`. This covers resident-path non-regression and the pin test.
2. New streaming fixture test (F3): tiny fixture → bf16 streaming conversion (cache sized to 1-2 experts per layer) → `load_verified_model`. Compare with the resident bf16 artifact on (a) full prefill, (b) stepwise decode, (c) a left-padded batch of 2, all within the bf16 bound and tie-aware. Then check (d) counters, and (e) `mx.get_active_memory()` peak during a T≥256 prefill. Before the F1 fix (e) should show growth that scales with misses; after it, (e) should be bounded by cache plus at most 3.75 GiB per layer at the real shape (scale accordingly for the fixture).
3. After the F1 fix, a real-weight smoke test on the external SSD only. Use one 512-token prompt at a 32 GiB cache, and record peak memory, bytes_read, and wall time before any long-text NLL run.
4. If F2 is resolved by merging: the gold adapter tests with a rebound COMMIT/MODULE_SHA256, and the mbp-live converter pin test.
