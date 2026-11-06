# Retroactive executing review: dc2204dba, `joulewise/adapters/mlx_runtime.py` hunks

- **Reviewer:** Opus 5.5. This is a retroactive executing review by a non-author, dated 2026-11-05. The original review papers live on the measurement Mac and could not be reached.
- **Commit:** `dc2204dba1e0512e17ff264be4f2498b04d0cbb0`. Its subject is "ALIGN pilot 3 build: per-episode prompt-cache reuse, ..." and it was built by Sol 6.1.
- **Parent:** `8510e77b2a1493eb9a591f5dd20cacd6a8190caf`.
- **Scope:** the commit's `joulewise/adapters/mlx_runtime.py` hunks (+17/-1), the registered number-bearing path. Surrounding code was read at `dc2204dba` and at the integration lane head `c8ef6b2f6` (`origin/lane/2026-11-05-align-v4-integration`).
- **Not in scope:** `joulewise/align/apple/prompt_cache.py`, which was read and exercised as the only caller, and the later adapter commits `b29c25c59` and `0ba413d40`, which have their own rows. At the lane head those two commits sit on top of these hunks. The legacy differential below was also re-run there.

## 1. What changed

`MlxRuntimeAdapter._generate` gains four keyword-only parameters. All of them default to "off":

| Parameter | Default | Effect when set |
|---|---|---|
| `setup_metadata: dict \| None` | `None` | Passed as the `phase_start/generation_setup` event metadata. It is also spread *after* `requested_output_tokens`/`eos_suppressed` into the `phase_end/generation_setup` metadata. |
| `reconcile_prompt: callable \| None` | `None` | Called as `prompt = reconcile_prompt(prompt_token_ids)` inside the generation_setup window, before EOS suppression. Its return value replaces the prompt fed to `stream_generate`. |
| `cache_accounting: bool` | `False` | Adds `cached_tokens = prompt_tokens - len(prompt)` and `prefill_tokens = len(prompt)` to the `phase_start/prefill` metadata, and sets `_GenerationRecord.prefill_tokens = len(prompt)`. |
| `stream_options: dict \| None` | `None` | Copied into `stream_kwargs`. `max_tokens` is then forced and `sampler` is set if one exists. This is how `prompt_cache` reaches `mlx_lm.stream_generate`. |

`_GenerationRecord` gains `prefill_tokens: int | None = None`.

There is one caller of the new parameters, `joulewise/align/apple/endpoint.py@dc2204dba` (l.395-400). It passes all four only when `self.cache_policy == "episode_prefix"`. The default policy is `"full_prompt_each_turn"` (l.206), so legacy callers send nothing. The two in-adapter callers, `run_workload` (l.450) and `_run_suite_item` (l.660), also pass none of the new parameters.

When none of the parameters is set, the code differs from the parent in four ways:

- `_event(..., None)` replaces `_event(...)`, which produces the same `metadata or {}`;
- `**({})` is spread into a dict literal;
- `dict({})` is built and then `["max_tokens"]` is set, instead of the literal `{"max_tokens": ...}`; the key order stays `max_tokens`, then `sampler`;
- two `if` checks are skipped, and `prefill_tokens=None` is stored on the record.

## 2. What was executed

I made my own clone at `/Users/edr/code/CapstoneProject/jw-wt/retro-dc2204dba`, created with `git clone --shared` from the survey clone and with origin set to GitHub. It was checked out at `dc2204dba`, and also at `c8ef6b2f6` where noted. The parent adapter was extracted with `git show dc2204dba^:joulewise/adapters/mlx_runtime.py > mlx_runtime_parent.py` and loaded side by side as a separate module.

Test scripts are archived in `/private/tmp/jwsol/v4-retro-review-dc2204dba/`:

- `test_retro_dc2204dba_mock.py`, 12 tests;
- `test_retro_dc2204dba_native.py`, 3 tests on real MLX.

Environment:

- `TMPDIR` was set to the session scratchpad.
- `RETRO_PARENT` pointed to the extracted parent adapter.
- `PYTHONPATH=.:tests:<scratch>/retro`.

### 2.1 Existing suites at dc2204dba

```
PYTHONPATH=.:tests python3.13 -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer \
    tests.align.test_pilot3_cache tests.align.test_apple_endpoint
PYTHONPATH=.:tests /private/tmp/jwsol/venv-mlx/bin/python -m unittest (same modules)
```

Both runs passed: **72 tests, OK** on homebrew python3.13 and on the pinned venv (mlx 0.31.2, mlx-lm 0.31.3, transformers 5.22.1, `Device(gpu, 0)`). All pilot-3 cache tests in the tree are synthetic. Native coverage of the opt-in path comes from 2.3.

### 2.2 Mock lane: parent and commit side by side, plus probes of the new parameters

```
RETRO_PARENT=<scratch>/retro/mlx_runtime_parent.py PYTHONPATH=.:tests:<scratch>/retro \
    python3.13 -m unittest -v test_retro_dc2204dba_mock        # and with the venv interpreter
```

Result: **12/12 OK on both interpreters, at both `dc2204dba` and `c8ef6b2f6`.**

**`LegacyDifferential`** drives the parent and the commit through public legacy entry points. Both use the same fakes, and the clock advances 1 ms per read, so every event's timestamp and order are checked. The scenarios are:

- `run_workload` on a text prompt, an underrun with a native `finish_reason="stop"`, zero emitted tokens, and synthetic-ID prompts;
- `run_suite` over ID, text and synthetic items with fixed-budget and natural-EOS policies, including a mid-suite `stream_generate` exception.

The comparison covers the full `asdict` of every `RuntimeResult`: events, artifacts, provenance and token records. It also covers the exact kwargs handed to `stream_generate`, with key order (always `["max_tokens", "sampler"]`), the EOS set seen during each call, and the tokenizer's EOS set afterwards. Every field of a direct `_generate` call matches for `suppress_eos` True and False, and the new `prefill_tokens` is `None`. EOS is restored after a stream exception in both versions.

**Sensitivity check.** I re-ran the differential against two mutated parents:

- `mut1` prepends `prompt_cache: None` to the stream kwargs: FAILED (7 failures);
- `mut2` adds one key to the generation_setup metadata: FAILED (8 failures).

The differential therefore does detect changes to stream kwargs and to event metadata.

**`OptInProbes`** covers the following:

- `reconcile_prompt` runs strictly between the generation_setup start and end timestamps, and receives the full ID list.
- The delta is what `stream_generate` receives, with kwargs `["prompt_cache", "max_tokens", "sampler"]`.
- Prefill metadata is `(prompt_tokens, cached_tokens, prefill_tokens) = (5, 3, 2)`.
- The record keeps the full `prompt_token_ids` and `prompt_tokens`.
- If `reconcile_prompt` raises, the error propagates, EOS is untouched (suppression has not happened yet), and `stream_generate` is never called.
- If the stream raises while the new options are set, EOS is restored.
- The caller's `stream_options` dict is not mutated, and `max_tokens` in `stream_options` is overridden by the adapter's value.
- Four documented observations produced these outputs:

```
[observe] over-long delta gives cached_tokens = -1
[observe] str prompt with cache_accounting: -8 10
[observe] phase_start metadata after in-setup mutation: {'pre': 1, 'written_during_setup': True}
[observe] phase_end generation_setup metadata with colliding keys: {'requested_output_tokens': -1, 'eos_suppressed': 'SHADOWED'}
```

### 2.3 Native lane: real MLX on Metal with random tiny weights

There are no downloads and no study data. Two models were built in-process with seed 2204:

- **llama:** 2 layers, `KVCache`, which is trimmable;
- **qwen3_next hybrid:** 4 layers, `ArraysCache` + `KVCache`, which is untrimmable. This is the same recipe as `tests/align/test_r0_mlx_native.py`.

Both use a 64-word WordLevel tokenizer wrapped in `TokenizerWrapper`. The real `mlx_lm.stream_generate` sits behind a pass-through recorder.

```
RETRO_PARENT=... PYTHONPATH=.:tests:<scratch>/retro /private/tmp/jwsol/venv-mlx/bin/python \
    -m unittest -v test_retro_dc2204dba_native
```

Result: **3/3 OK at both `dc2204dba` and `c8ef6b2f6`.**

**N1, legacy differential on real MLX.** Parent and commit were compared for both models, prompt lengths 6 and 38, `suppress_eos` True and False, and 24 output tokens. The full `_GenerationRecord` matches between versions: events (on a FakeClock), output token IDs, text and stop condition. The `stream_generate` kwargs are `["max_tokens", "sampler"]` in both, and the tokenizer's EOS set is restored to `{1}`.

**N2, opt-in episode cache.** This test wires the adapter with `EpisodePromptCache` exactly as `endpoint.py@dc2204dba` does, over four turns:

- t1: cold;
- t2: the previous prompt, plus the output, plus 3 new IDs;
- t3: an exact repeat;
- t4: a prompt that diverges mid-prefix.

Each turn is compared with a fresh legacy, cache-free generation of the same full prompt.

| model | turn | prompt | cached | fed | rebuilt | trimmed | greedy IDs == fresh | max abs logprob diff |
|---|---|---|---|---|---|---|---|---|
| llama KVCache | t1_cold | 10 | 0 | 10 | no | 0 | yes | 0.0 |
| | t2_extend | 25 | 22 | 3 | no | 0 | yes | 1.43e-6 |
| | t3_repeat | 25 | 24 | 1 | no | 13 | yes | 1.43e-6 |
| | t4_rewind | 13 | 5 | 8 | no | 32 | yes | 0.0 |
| qwen3_next hybrid | t1_cold | 10 | 0 | 10 | no | 0 | yes | 0.0 |
| | t2_extend | 21 | 18 | 3 | no | 0 | yes | 1.43e-6 |
| | t3_repeat | 21 | 0 | 21 | **yes** | 0 | yes | 0.0 |
| | t4_rewind | 13 | 0 | 13 | **yes** | 0 | yes | 0.0 |

The following hold on every turn:

- prefill-event `cached_tokens + prefill_tokens == len(prompt)`;
- the event counts equal the cache's own `cached_prompt_tokens` and `prefill_tokens`;
- `record.prefill_tokens == fed`, and fed is at least 1;
- `record.prompt_token_ids` is the full prompt;
- `stream_generate` received `prompt_cache`.

Untrimmable hybrid caches rebuild whole, as the ruling requires.

Random tiny models collapse toward repeated tokens (1-4 distinct IDs per turn). The logprob comparison is therefore the stronger evidence: with cache reuse, the full next-token distributions agree with full re-prefill to within float32 rounding (≤1.43e-6).

**N2b, error handling.** I corrupted the episode ledger after one turn. The next turn raises `ValueError: cache_offset_mismatch` from inside `reconcile_prompt`, before any native call, and the tokenizer EOS set is unchanged.

### 2.4 Cost of the added code on the legacy path (timeit, python3.13)

- `dict(None or {})` plus the key set costs 117 ns, against 55 ns for the old literal.
- `**(None or {})` in the setup metadata literal costs 113 ns, against 79 ns.

The extra work is about 100 ns per generation call. About 30 ns falls inside the generation_setup window and about 60 ns falls before `stream_generate`, which is in the prefill window. Event bytes are unchanged (2.2, 2.3 N1). This is far below the clock and power-sampling resolution, so it has no energy-relevant effect.

## 3. Findings

**No BLOCKER, HIGH or MEDIUM findings.**

**L1 (LOW): `setup_metadata` can overwrite the adapter's own `phase_end/generation_setup` keys.** In l.808-812 (dict literal at l.809-811), `{"requested_output_tokens": ..., "eos_suppressed": ..., **(setup_metadata or {})}` puts the caller's keys last. Evidence: the probe produced `{'requested_output_tokens': -1, 'eos_suppressed': 'SHADOWED'}`. The only caller's keys come from `EpisodePromptCache.prepare` minus `fed_delta_ids`. None of them collide, so the bug is not reachable today. *Fix:* spread `setup_metadata` first, or raise on overlapping keys.

**L2 (LOW): a non-empty `setup_metadata` dict is stored by reference in the `phase_start/generation_setup` event.** `_event` stores `metadata or {}`. Any mutation the caller makes during `reconcile_prompt` therefore appears retroactively in the start event. Evidence: `{'pre': 1, 'written_during_setup': True}`. The endpoint passes an empty dict at call time, which `or {}` replaces with a fresh dict; the probe `test_observe_empty_setup_metadata_is_not_aliased` confirms the start event stays `{}`. Not reachable today, but fragile. *Fix:* `dict(setup_metadata or {})`.

**L3 (LOW): `cache_accounting` does not validate its inputs.** `cached_tokens = prompt_tokens - len(prompt)` assumes two things: that `prompt` is a token sequence (a `str` gives a character count; observed `-8/10`), and that `reconcile_prompt` returned a suffix no longer than the prompt (an over-long return gives `cached_tokens = -1`). The only caller guarantees both: `EpisodePromptCache.prepare` checks `represented_ids + delta == prompt_ids`, and the endpoint's `prepare_prompt` returns an ID list. *Fix:* raise when `cache_accounting` is set and `prompt` is a `str`, or `len(prompt)` is not in `[1, prompt_tokens]`.

**I1 (INFO):** `_GenerationRecord.prefill_tokens` has no consumer at `dc2204dba` or at `c8ef6b2f6`; the endpoint reads the cache metadata instead. It is harmless and stays `None` on legacy paths.

**I2 (INFO):** In the opt-in path, cache reconciliation (prefix compare, trim or `make_prompt_cache`) is timed inside the `generation_setup` window. The fed prefill is then smaller than `prompt_tokens`, so consumers must use the `prefill_tokens` and `cached_tokens` fields. This is the documented intent (code comment l.798-799 and the e1308804 ruling). It changes the work per phase only for runs that set `prompt_cache: episode_prefix`, and that setting is recorded in the hashed policy.

**Measurement identity.** For runs that did not opt in, I found no change to token streams, event bytes, stream kwargs, EOS handling, or sampler construction. This was checked on fakes and on real MLX, and at both the commit and the integration lane head. Runs that opt in differ from full re-prefill by at most float32 rounding in logprobs (≤1.43e-6 on these models). On the turns tested, the greedy token IDs are identical.

## 4. Verdict

**ADMIT.** The hunks are opt-in, the legacy path is byte-identical in every executed check, and the opt-in path is correct for both trimmable and untrimmable caches. L1-L3 are optional hardening for future callers. None of them is reachable from code at `dc2204dba` or `c8ef6b2f6`, and none is needed for admission.

## 5. Proposed `configs/b6/executing_reviews.json` row

The paper path follows the `/Users/edr/night-archive/` prefix required by `tests/b6/test_audit_record_fixes.py`. Before the row lands, the lead must copy this file (`/private/tmp/jwsol/v4-retro-review-dc2204dba.md`) to that path; this review did not write under `night-*`. WP5's acceptance condition is that the cited paper exists.

```json
{
 "commit": "dc2204dba1e0512e17ff264be4f2498b04d0cbb0",
 "number_bearing_paths": [
  "joulewise/adapters/mlx_runtime.py"
 ],
 "change": "ALIGN pilot 3 build: opt-in per-episode prompt-cache hooks in mlx_runtime._generate (Sol 6.1); retroactive review",
 "executing_reviews": [
  {
   "reviewer": "Opus 5.5, retroactive executing review (non-author; original papers on measurement Mac unreachable), 2026-11-05",
   "covered": "8510e77b2..dc2204dba (joulewise/adapters/mlx_runtime.py hunks); legacy differential re-run at integration c8ef6b2f6",
   "paper": "/Users/edr/night-archive/align-v4/retro-reviews/dc2204dba-REVIEW.md"
  }
 ]
}
```
