# Retroactive executing review: 0ba413d40, `joulewise/adapters/mlx_runtime.py` hunks

- **Commit:** `0ba413d40fbadeac03d619cda7c030a11eb24394`, "ALIGN: checkpoint and restore hybrid prompt caches at turn boundaries" (ALIGN #657).
- **Label:** RETROACTIVE. The original review papers are on the measurement Mac and could not be reached. This review was written afterwards and is non-author.
- **Reviewer:** Opus 5.5 (executing lens), 2026-11-05, on the M4 Air analysis box: mlx 0.31.2, mlx-lm 0.31.3, native Metal.
- **Scope:** only the hunks in `joulewise/adapters/mlx_runtime.py`, which is a registered number-bearing path. Callers in `align/apple/endpoint.py`, `prompt_cache.py` and `workload.py` were read and run only to work out when the hunks become active.
- **Blob identity:** the file is byte-identical across the commit, the integration lane head and the trial head, so this review covers all three.

| rev | `mlx_runtime.py` blob |
|---|---|
| `0ba413d40^` | `2fa9d24cd585…` |
| `0ba413d40` | `7487a42cedd7…` |
| `origin/lane/2026-11-05-align-v4-integration` = `c8ef6b2f6` | `7487a42cedd7…` |
| `v4-trial` = `b49bace62` | `7487a42cedd7…` |

## 1. What the hunks change

All changes are in `MlxRuntimeAdapter._generate`.

1. **New parameter.** A keyword-only parameter `prefill_prompt: Any | None = None` is added between `reconcile_prompt` and `sampler_policy`. It comes after `*`, so no positional argument shifts.
2. **`fed_prompt_tokens` captured early.** `fed_prompt_tokens = len(prompt) if cache_accounting else None` is now computed after `prefill_metadata` is built and before the `phase_start prefill` event.
   - `_GenerationRecord.prefill_tokens` now uses this value. Before, it used `len(prompt)` evaluated at return time.
   - On the legacy path `prompt` is never reassigned between those two points, so the value is the same.
3. **Hook call.** Inside the `try:` that surrounds native generation, after `phase_start prefill` and before `stream_generate`, the adapter runs `prompt = prefill_prompt(prompt)` when the hook is set.
   - The hook's work (the boundary prefill plus the snapshot copy) therefore falls inside the measured prefill window. Native prefill ends at the first token.
   - The token counts in the prefill `phase_start` metadata and in the record include both the boundary part and the native part.

The only production caller is `MlxEndpoint.chat`. It passes the hook for every `cache_policy == "episode_prefix"` turn as `lambda delta: self._episode_cache.prefill_checkpoint(delta, cache_metadata)`. When no checkpoint is planned, `prefill_checkpoint` returns `delta` itself (the same object). The single-prompt and suite paths (`mlx_runtime.py:450` and `:660`) never pass the hook.

## 2. What was executed

Setup:
- Checkouts I made myself:
  - `/Users/edr/code/CapstoneProject/jw-wt/retro-0ba413d40` (detached at `0ba413d40`)
  - `/Users/edr/code/CapstoneProject/jw-wt/retro-0ba413d40-lanehead` (detached at `c8ef6b2f6`, later at `b49bace62`)
- Python: `P=/private/tmp/jwsol/venv-mlx/bin/python`.
- Review scripts are archived in `/private/tmp/jwsol/v4-retro-review-0ba413d40/`, with sha256 values in §6.
- The parent and commit versions of `mlx_runtime.py`, and the parent `prompt_cache.py`, were exported with `git show` to `src/` and loaded side by side as separate modules.

### E1. Existing suites at each revision

```
$P -B -m unittest tests.align.test_cache_checkpoint tests.align.test_cache_checkpoint_native \
  tests.test_mlx_runtime tests.align.test_apple_endpoint tests.align.test_pilot3_cache \
  tests.test_suite_control_parity [tests.align.test_budget_apple]
PYTHONPATH=tests $P -B -m unittest tests.test_mlx_runtime_detokenizer
```

| rev | result |
|---|---|
| `0ba413d40` | 77 OK, detokenizer 8 OK. The native gate printed `bulk_max_abs=0.0`, bitwise, in fp32 and bf16. |
| `c8ef6b2f6` (lane head) | 108 run, **3 errors**, all in `test_real_122b_policy_and_runtime_agree_and_unknown_hybrids_fail_closed` (`unverified_xml_template:qwen3_5_moe`). This is an interaction between #659 and #657 tests and does not involve `mlx_runtime`. It is fixed by `b49bace62`. |
| `b49bace62` (trial head) | 109 OK, including my probe E4. |

### E2. Adapter-level legacy identity and hook behaviour (fake native, ticking clock)

Command, from the commit checkout and from the lane-head checkout:

```
cd /private/tmp/jwsol/v4-retro-review-0ba413d40
PYTHONPATH=<checkout> $P -B -m unittest test_retro_657_adapter -v
```

Result: 12/12 OK at `0ba413d40`, `c8ef6b2f6` and `b49bace62`.

How the harness works:
- The clock advances by 1.0 on every `now()` call. Any added or removed clock read would therefore shift every later timestamp.
- The fake `mlx_lm` records each native prompt and its kwargs.
- Each comparison checks `pickle(asdict(record), native calls, final clock value, restored EOS ids)`.

Checks:
- **Parent and commit match byte for byte with no hook** in 7 scenarios:
  - plain
  - `suppress_eos` with suite item fields
  - `prepare_prompt`
  - `cache_accounting` with `reconcile_prompt` and `stream_options`
  - seeded categorical sampler (real `mx.random.seed`)
  - `max_tokens` cut
  - zero emitted tokens
- **Explicit `prefill_prompt=None` equals omitting it.**
- **Native-fault path:** with an exception at token 1, the exception, the native calls, the clock value and the EOS restore are all the same in parent and commit.
- **Signature:** the parameter list is the parent's plus `prefill_prompt`, which is KEYWORD_ONLY with default None.
- **Identity hook (`lambda p: p`) is byte-identical to no hook** in all 7 scenarios. This models the lane-head anchor path, where the endpoint always passes the lambda.
- **Hook placement:**
  - Clock stamps were setup_end=4, prefill_start=5, hook=6, prefill_end=7, so the hook runs strictly inside the prefill window.
  - The hook receives the reconciled delta, and native receives what the hook returns.
  - `phase_start prefill` metadata shows `prefill_tokens=2` and `cached_tokens=4`. Both are computed before the hook.
  - `record.prefill_tokens=2`, the pre-hook count. Without the `fed_prompt_tokens` hunk it would have been 1.
- **With `cache_accounting=False` and a hook,** `prefill_tokens` stays `None`.
- **Hook raises** (`ValueError`, or `KeyboardInterrupt` as a BaseException): the exception propagates, native is never called, and the tokenizer's `eos_token_ids` is restored by the existing `finally`.
- **Hook returns `[]`:** the adapter passes the empty prompt to native without checking it (see F5).
- **Sampled RNG:** the RNG state seen inside native generation is identical with no hook and with an identity hook, so the hook draws no random numbers.

CPU overhead (`bench_overhead.py`, 15 interleaved rounds of 5000 calls, GC off, fake native). Median ns per `_generate`:

| run | parent | commit | commit + identity hook |
|---|---|---|---|
| 1 | 39451 | 40193 | 40851 |
| 2 | 41929 | 42200 | 43006 |

- The differences (≤ about 1.4 µs) are well inside the run-to-run spread (min to max is about 15 µs).
- Real prefill windows last milliseconds to seconds.
- This box is not a quiet measurement host, so these numbers bound the overhead; they are not a calibrated energy measurement.

### E3. Native Metal: real `mlx_lm.stream_generate` through `_generate`, tiny random-weight `qwen3_next`

```
PYTHONPATH=<checkout> $P -B -m unittest test_retro_657_native -v
```

Setup:
- Hybrid cache: KVCache plus ArraysCache, in fp32 and bf16.
- vocab 256, seed 11, no downloads.
- Two-turn episode:
  - Turn 1 prompt: 1300 closed tokens plus a 3-token generation preamble.
  - The re-render drops the preamble, so turn 2 rewinds into the recurrent layers.
  - Turn 2 adds 40 tokens. `max_tokens=8`.
- Arms:
  - **A:** parent runtime + parent `prompt_cache`, no hook (pre-#657 anchor). Run twice (A, A2) to confirm the run repeats exactly.
  - **B:** commit runtime, limit 0, no hook.
  - **C:** commit runtime, limit 0, endpoint-style `prefill_checkpoint` hook (lane-head anchor path).
  - **D:** commit runtime, limit 2, hook plus `plan_checkpoint` (opt-in path).

Results. The script was run against the `prompt_cache.py` at each revision; the runtime blob is the same in all three.

- **A = A2 (repeatable), and A = B = C bitwise** at `0ba413d40`, `c8ef6b2f6` and `b49bace62`, in fp32 and bf16. The comparison covers:
  - output token ids for both turns
  - record `prefill_tokens` and the prefill `phase_start` metadata
  - the event sequence
  - all final native cache arrays

  For the anchor arm, turn 2 is `cache_rebuilt=True` with `prefill_tokens=1351`.
- **D mechanics (correct):**
  - Turn 1: boundary 1300; `record.prefill_tokens=1303`, the full fed delta including the boundary part.
  - Turn 2: `cache_checkpoint_restore_count=1`, no rebuild, `cached=1300`, `prefill_tokens=51` (the anchor fed 1351).
  - Event phase sequence is the same as C.
- **D numerics compared with C:**

  | tree | fp32 tokens | fp32 final state | bf16 tokens | bf16 final state |
  |---|---|---|---|---|
  | `0ba413d40` (step 512, default stream, no `wired_limit` in the hook) | equal | max_abs 1.79e-6, not bitwise | equal | max_abs 0.015625, not bitwise |
  | `c8ef6b2f6` / `b49bace62` (step 2048, `generation_stream`, `wired_limit`) | equal | max_abs 1.43e-6, not bitwise | equal | 0.0, bitwise |

### E4. Lane-head endpoint probe: is the hook's boundary prefill covered by the deadman guard?

How it was run:
- `test_retro_657_deadman.py` was copied temporarily into the lane-head checkout as `tests/align/zz_retro_657_deadman_probe.py`, run, then removed.
- Inputs: `T.hybrid_endpoint({'model_type': 'qwen3_next'}, limit)`, with a deadman stub whose `guard()` counts how deeply it is nested, and a model spy that records `(tokens, under_guard)` for each forward pass.

Same result at `c8ef6b2f6` and `b49bace62`:

```
limit=None: calls=[(4,T),(1,T),(1,T),(5,T),(1,T),(1,T)] native fed=[[1,2,3,90],[1,2,3,8,90]] unguarded_tokens=0
limit=0:    identical to limit=None
limit=2:    calls=[(3,F),(1,T),(1,T),(1,T),(1,F),(1,T),(1,T),(1,T)] native fed=[[90],[90]] unguarded_tokens=4
```

## 3. Findings

### F1: HIGH at `0ba413d40`; RESOLVED at the integration lane head (activation is outside the hunks)

At the commit itself the hook was not actually opt-in for hybrid models:
- `EpisodePromptCache(model)` defaulted to `checkpoint_limit=2` (`DEFAULT_CHECKPOINT_LIMIT = 2`).
- `MlxEndpoint` gated the work only on `self._episode_cache.hybrid` and had no limit parameter.
- `EpisodeRuntimeAdapter` added `execution_policy.checkpoint` (limit 2) for every `qwen3_next`/`qwen3_5*` config.

Consequences for every `episode_prefix` run on a hybrid model:
- The new boundary prefill and snapshot ran inside the measured prefill window.
- The native prefill schedule changed, and with it the numerics. E3 at the commit shows bf16 state not bitwise equal to the anchor path.
- Identity metadata changed.

Evidence: at the commit, `test_cache_checkpoint.test_endpoint_records_full_work_inside_prefill_phase` asserts `cache_checkpoint_restore_count == 1` for an endpoint built only with `prompt_cache='episode_prefix'`, and `test_hybrid_policy_identity_addition_leaves_anchor_policy_unchanged` asserts identity limit 2 for `qwen3_next`.

Resolution:
- At `c8ef6b2f6`: `DEFAULT_CHECKPOINT_LIMIT = 0`, plus an explicit `hybrid_checkpoint_limit` on the endpoint and workload; `hybrid_checkpoint_policy(cfg, None|0)` returns None.
- At `b49bace62`: v3 kit members pin `hybrid_checkpoint_limit=None`.
- E3 and E4 show that limit None or 0 at the lane head gives a bitwise-identical native path, with the full delta passed to native.

Data impact: `0ba413d40` is reachable only from `origin/lane/2026-11-05-align-cache-checkpoint` and the integration lane, not from any pilot or measurement branch. Ruling 2 already covers this.

### F2: MEDIUM, opt-in path only (limit > 0), OPEN at the lane head

The boundary prefill runs outside the episode deadman's SIGALRM guard.
- `_StreamObservation` guards only `next(stream)`. `_generate` calls the hook before `stream_generate`, so the forward passes up to the closed-history boundary are not interruptible by the deadman.
- E4: 4 of 4 boundary tokens ran unguarded when limit=2. With limit None or 0 nothing ran unguarded.
- On a real model, turn 1 (or a turn after a rebuild) can push most of the prompt through this path. For example, a 30k-token first turn on the 122B model would run almost entirely unguarded.
- If the deadline passes during that prefill, the expiry is noticed only at the next `guard()` entry. That still ends the turn correctly as `episode.deadman`, but a hang inside the boundary prefill is bounded only by the runner's outer member cap.
- This arose when #657's hook was combined with the later deadman/thermal work. The commit's own endpoint had no deadman.
- Fix, either of:
  - (a) In the endpoint, wrap the lambda as `with self.deadman.guard() if self.deadman else nullcontext(): return self._episode_cache.prefill_checkpoint(...)`. The endpoint's existing `except DeadmanExpired` already drops the cache and records `episode.deadman`, and `_generate`'s `finally` restores EOS (E2).
  - (b) The ruling-4 relocation below.

Not a blocker for R0 or the v4 series, which run limit 0 per ruling 2. **Fix before arming any cell with limit > 0.**

### F3: LOW, RESOLVED at the lane head (outside the hunks)

At the commit, the hook's manual prefill used `step_size=512`, the default stream and no `wired_limit`, while native `generate_step` uses 2048, `generation_stream` and `wired_limit`. This gave a different chunk schedule and residency behaviour within the same measured window.
- `c8ef6b2f6` aligned all three (`PREFILL_STEP_SIZE=2048`, `with wired_limit(...), mx.stream(generation_stream)`, `mx.clear_cache()` per chunk).
- E3: the bf16 state difference from the anchor path went from 0.015625 to bitwise equal.

### F4: LOW / informational, opt-in path

A checkpoint run is not numerically identical to a non-checkpoint run, even on turn 1, because the prompt is split at the closed-history boundary. E3 at the lane head still shows fp32 max_abs 1.43e-6. Tokens matched on the tiny model, but that does not guarantee they match on a real model.
- This is correct as designed, because the policy is recorded in identity (`execution_policy.checkpoint`, fallback `checkpoint_then_whole_cache_rebuild_on_untrimmable_rewrite`).
- Cells with limit > 0 must be treated as a separate execution identity and never pooled with limit 0 or None. Ruling 2 handles this for v4.

### F5: LOW, adapter contract

`_generate` does not validate the hook's return value. An empty list, `None` or another bad type would be passed straight to `stream_generate`; E2 shows `[]` being forwarded. The only implementation, `prefill_checkpoint`, guarantees at least one token remains (`0 <= count < len(delta)`, else `cache_checkpoint_boundary_invalid`), so nothing is affected today.
- Optional hardening: inside the hook branch, raise if the returned prompt is empty.
- Only the opt-in branch is affected; the legacy path stays byte-identical.

### F6: INFO, legacy-path identity CONFIRMED

When `prefill_prompt` is omitted or `None`, the following are byte-identical to the parent (E2):
- events, timestamps and the number of clock reads
- token streams
- `prefill_tokens`
- native call arguments
- error paths

With the lane-head anchor configuration (episode_prefix, hybrid, limit None or 0, identity hook passed), the native Metal path is bitwise identical to the pre-#657 parent (E3: tokens, counts, events, final cache arrays). Added CPU work is a `len()` and an `is not None` test, with any cost below benchmark noise.

This is the boundary test that ruling 4 requires: the anchors' runtime path is unchanged when the limit is None or 0.

### Note on ruling 4 (hook relocation; analysis, not executed)

The endpoint already installs `_StreamObservation` as `runtime._mlx_lm` for every turn, which is the existing per-turn substitution and not a new monkeypatch.
- Its `stream_generate` is a lazy generator. It first runs inside `_generate`'s prefill window, and it receives the native `prompt` argument.
- Doing the boundary prefill there, at the start of the generator and under `deadman.guard()`, would keep the same measured window.
- It would also fix F2.
- It would make both `mlx_runtime.py` hunks unnecessary: `_generate`'s `prompt` would no longer be reassigned, so `len(prompt)` at return would naturally be the full fed delta.
- If the lead wants to restore `mlx_runtime.py` to blob `2fa9d24cd`, this is a viable path. It would need a re-run of E2, E3 and E4 against it.

## 4. Verdict

**ADMIT_WITH_FIXES**

- The `mlx_runtime.py` hunks are correct.
- The path that does not opt in is byte- and bitwise-identical to the parent, at the adapter level (E2) and natively on Metal (E3).
- They are admitted as they stand for every run with `hybrid_checkpoint_limit` None or 0, which covers all v3 anchors, R0 and the v4 series under ruling 2.
- Required before any cell with limit > 0 is armed: fix F2 (put the boundary prefill under the deadman guard, either in the endpoint lambda or by the ruling-4 relocation) and re-run E4.
- F1 and F3 are already resolved on the integration lane. F5 is optional hardening.

## 5. Proposed `configs/b6/executing_reviews.json` row

The `paper` must start with `/Users/edr/night-archive/` (`tests/b6/test_audit_record_fixes.py`). The lead should copy this paper there: I did not write under `~/night-*`. The proposed path is below.

```json
{
 "commit": "0ba413d40fbadeac03d619cda7c030a11eb24394",
 "number_bearing_paths": [
  "joulewise/adapters/mlx_runtime.py"
 ],
 "change": "ALIGN #657 hybrid prompt-cache checkpoint: keyword-only prefill_prompt hook and pre-hook prefill_tokens in MlxRuntimeAdapter._generate (retroactive)",
 "executing_reviews": [
  {
   "reviewer": "Opus 5.5, retroactive executing review (non-author; original papers unreachable on measurement Mac)",
   "covered": "0ba413d40 mlx_runtime.py hunks (blob 7487a42ce, byte-identical at integration c8ef6b2f6 and v4-trial b49bace62); ADMIT_WITH_FIXES: legacy/limit None|0 path byte- and native-bitwise identical to parent; F2 deadman coverage of opt-in boundary prefill must be fixed before any limit>0 cell",
   "paper": "/Users/edr/night-archive/align-v4/retro-reviews/v4-retro-review-0ba413d40.md"
  }
 ]
}
```

## 6. Artifacts

`/private/tmp/jwsol/v4-retro-review-0ba413d40/` (sha256):

```
394caeaea109e502a6c0e25d19209b4c2bb93704e80084f83e42df6f7c8d31c0  test_retro_657_adapter.py
ed11518397734be213a21a7817c5a7b07dfd42d6c8bab155520786e0f119f2a6  test_retro_657_native.py
84de6b49edc215cfb2dd08d498fe839f8b13a0853e930fe150f2ea1f8271e612  test_retro_657_deadman.py
e51beb955b9d34372ecf348819c7a28dd929447e2561a538f903d3e42105191e  bench_overhead.py
953e6fec990c1d7e0702a8abb199a55f179e50d28854f4b62d0e95302dde0c45  src/mlx_runtime_parent.py   (git show 0ba413d40^:...)
20c5a423e5617103cf4a5bb2575fe313d3385f1aa25ba679174785fad74e701b  src/mlx_runtime_commit.py   (git show 0ba413d40:...)
c5345252a8d2fc89bd3a0380ae86311b06d38fcfe1fa6887dc7022bf4864107b  src/prompt_cache_parent.py  (git show 0ba413d40^:...)
```

Process note: while checking the row schema, I ran a single top-level `ls` of `/Users/edr/night-archive` before noticing that `~/night-*` is off-limits for this task. Nothing was read or written there beyond that directory listing.
