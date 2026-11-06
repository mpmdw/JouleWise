# Retroactive executing review: b29c25c59, `joulewise/adapters/mlx_runtime.py`

- **Commit:** `b29c25c59ad57787faae4e939578dea01c5682a6` ("ALIGN pilot 4 build: seeded sampling at published Qwen3 thinking settings, 120 s episode guard, ...", Sol 6.1 xhigh build, 2026-11-03)
- **Reviewer:** Opus 5.5, retroactive executing review (non-author), 2026-11-05
- **Label:** retroactive. The original review papers are on the measurement Mac and could not be reached.
- **Scope:** only the hunks in `joulewise/adapters/mlx_runtime.py`, the single registered number-bearing path this commit touches (checked against `configs/b6/registration/acceptance.json`). The 120 s episode guard lives in the ALIGN endpoint and session code, not in this file, so it is out of scope.
- **Re-executed at:** integration lane head `c8ef6b2f6` (`origin/lane/2026-11-05-align-v4-integration`). Between the commit and the lane head the only change to this file is `0ba413d40` (`prefill_prompt` hook). That change does not touch the sampler or seed lines.
- **Environment:** M4 Air, Metal GPU (`Device(gpu, 0)`), venv `/private/tmp/jwsol/venv-mlx` (mlx 0.31.2, mlx-lm 0.31.3, transformers 5.22.1, tokenizers 0.23.3). Models were random-weight tiny `llama` and tiny hybrid `qwen3_next` (gated-delta plus attention) with a local WordLevel vocabulary. Nothing was downloaded.

## 1. Hunks and behaviour change

1. `_generate(...)` gains two keyword-only parameters, both defaulting to `None`: `sampler_policy: dict | None` and `per_turn_seed: int | None`.
2. When `sampler_policy is not None` (opt-in), the following runs inside the `generation_setup` window, after `reconcile_prompt` and before `_suppress_eos`:
   - it builds the sampler with `_sampler_for_generation(sampler_policy)`;
   - it checks that `per_turn_seed` is an exact `int` in `[0, 2**64)` and raises `ValueError` otherwise (this rejects `bool`, `float` and `None`);
   - it calls `mx.random.seed(per_turn_seed)` through `_resolve_mlx_core()`;
   - it records `per_turn_seed` in the sampler provenance.
3. When `sampler_policy is None` (legacy), the greedy sampler is still built at its original position: after the `prefill` phase_start event and before `try:`. The new `if sampler_policy is None:` guard sits there.
4. `_sampler_for_generation(policy=None)`: if a policy is given, it calls `make_sampler(temp=..., top_p=..., top_k=..., min_p=...)` with no fallback and returns provenance `{"kind": "categorical", ..., "constructor_kwargs": {...}}`. The greedy feature-detection path below it is unchanged.

The only production caller is `joulewise/align/apple/endpoint.py:702` at the lane head. It passes `sampler_policy`/`per_turn_seed` only when `self.sampler is not None`. In that case the policy has already passed `validate_policy` (`joulewise/align/apple/sampling.py`), which requires exactly the keys `{temperature, top_p, top_k, min_p}`, `temperature > 0`, finite values in range, and an integer `top_k >= 0`. The seed comes from `turn_seed(episode_seed, turn_index)`, which is the first 64 bits of a SHA-256.

## 2. What was executed

Scripts are in `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/retro_b29/`. Three versions of the adapter module are loaded side by side from `git show`:
- `mlx_parent.py` (`b29c25c59^`);
- `mlx_commit.py` (`b29c25c59`);
- `mlx_lane.py` (`c8ef6b2f6`).

Each script wraps the real `mlx_lm` in a recording proxy that logs `make_sampler` and `stream_generate` calls. It also spies on `mx.random.seed`. The tick clock is deterministic, so event timestamps can be compared exactly.

### 2.1 `test_retro_b29.py` (tiny llama): 14/14 OK

```
JW_REPO=/Users/edr/code/CapstoneProject/jw-wt/retro-b29c25c59 \
  /private/tmp/jwsol/venv-mlx/bin/python test_retro_b29.py      # Ran 14 tests in 0.533s  OK
```

- **Legacy path is byte-identical across parent, commit and lane.** With `sampler_policy=None`, the three versions produce identical results for all of the following: the full event list (timestamps, types, phases, messages, metadata), output token ids, text, stop condition, `prefill_tokens`, sampler provenance (`{'kind':'greedy','temperature':0.0,'pinned':True,'api':'mlx_lm.make_sampler','parameter':'temp'}`) and the ordered call log (`[make_sampler(temp=0.0), stream_generate(max_tokens, sampler)]`). There are no `mx.random.seed` calls. The greedy sampler is still built in the prefill window. EOS is restored afterwards.
- Passing a stray `per_turn_seed` without a policy is ignored: no reseed and greedy provenance.
- Greedy output does not depend on ambient RNG state (tested with ambient seeds 1, 2 and 3).
- **Opt-in determinism.**
  - With the same `per_turn_seed`, the token streams are identical even when the ambient seed changes between runs (999 vs 424242).
  - Different turn seeds give different streams, and both differ from greedy.
  - Example: seed s gives `[58,58,...,56,34,...]`, seed s' gives `[12,12,...,21,1,1,...]`, greedy gives `[43,...]`.
- **No hidden RNG consumption.** `_generate(policy, seed=2**64-1, suppress_eos=False)` gives exactly the same tokens as a manual reference: `mx.random.seed(s)` followed by `mlx_lm.stream_generate(..., sampler=make_sampler(temp=.6, top_p=.95, top_k=20, min_p=0))`. The run makes exactly one seed call and one `make_sampler` call, with the published kwargs, and the seed call comes before `stream_generate`.
- The seed is applied inside the `generation_setup` window (phase order: tokenize start/end, then generation_setup start/end). Provenance records `kind: categorical`, `per_turn_seed` and `constructor_kwargs`.
- The sampled and greedy event skeletons (type, phase, message, metadata) are identical. Only timestamps and tokens differ.
- **Seed validation.**
  - `-1`, `2**64`, `True`, `None`, `1.0` and `"1"` each raise `ValueError`. None of them calls `mx.random.seed` or `stream_generate`, and EOS is not left suppressed.
  - `0`, `2**63` and `2**64-1` are accepted by the native nanobind `mx.random.seed` and recorded.
- Adapter-level edge probes for unvalidated policies: see LOW-1.
- Cost probe: `make_sampler` takes 0.17 us for greedy and 0.32 us for categorical; `mx.random.seed` takes 0.23 us.

### 2.2 `test_retro_b29_hybrid.py` (tiny qwen3_next hybrid): 2/2 OK

```
JW_REPO=... /private/tmp/jwsol/venv-mlx/bin/python test_retro_b29_hybrid.py   # Ran 2 tests in 1.134s  OK
```

- The legacy path is identical across parent, commit and lane for 4 prompts. The prompts produce 4 distinct greedy streams, with 1 to 4 distinct token ids each over 40 tokens.
- Seeded sampling reproduces across the commit and lane module versions, even with ambient RNG perturbed, for 3 turn seeds of 64 tokens each.

### 2.3 `probe_eos_leak.py`

```
parent legacy AdapterFailure eos after failure: set()
lane legacy AdapterFailure eos after failure: set()
lane policy AdapterFailure eos after failure: {1}
```

### 2.4 Repo suites

- At the reviewed commit (a worktree of my clone at `b29c25c59`):
  - `python -m unittest tests.align.test_pilot4 tests.align.test_apple_endpoint tests.align.test_pilot3_cache tests.align.test_apple_sampler`: 37 tests OK.
  - `PYTHONPATH=tests python -m unittest test_mlx_runtime test_mlx_runtime_detokenizer`: 51 tests OK.
- At the lane head `c8ef6b2f6`:
  - Same mlx_runtime suites: 51 OK.
  - `tests.align.test_r0_mlx_native`, the real Metal tiny hybrid: 1 OK in 93.9 s.
  - `tests.align.test_pilot4`, `test_apple_endpoint`, `test_apple_sampler` and `test_pilot3_cache`: OK.
  - `tests.align.test_cache_checkpoint`: 3 subtest errors, `ValueError: unverified_xml_template:qwen3_5_moe` in `test_real_122b_policy_and_runtime_agree_and_unknown_hybrids_fail_closed`. They come from the XML-family gate in `xml_tool_calls.validate_model_family` meeting the #657 test. They are **not related to this commit's hunks** (see Observations).

## 3. Findings

No BLOCKER, HIGH or MEDIUM findings.

**LOW-1: adapter-level policy handling relies on caller validation.** The comment "Record the constructor arguments after validation" refers to validation in `sampling.validate_policy`, not in the adapter. A caller that passes a raw policy directly to `_generate` sees the following (all executed):
- `temperature=0` yields an argmax sampler labelled `kind: "categorical"`. Its tokens equal greedy.
- Extra keys such as `repetition_penalty` are dropped silently. `constructor_kwargs` shows they were not applied.
- A missing key raises a bare `KeyError`.
- A `TypeError` from `make_sampler` surfaces as a bare `TypeError`, not as `AdapterFailure(sampler_pin_unverified)`.

The only production caller always validates, and `validate_policy` requires the exact key set and `temperature > 0`, so no current run is affected. Suggested hardening, optional and not required for admission: call `validate_policy` or an equivalent at the top of the policy branch, and wrap `make_sampler` errors in `_raise_sampler_pin_failure`.

**LOW-2: sampler construction sits in different measurement windows for the two arms.** Opt-in builds the sampler and seeds the RNG inside `generation_setup`. Legacy still builds the greedy sampler inside the `prefill` window, which keeps the legacy bytes unchanged. The measured cost is 0.3 to 0.6 us in total. That is energetically negligible and far below the phase-boundary timestamp resolution, so this is informational only. It should be kept in mind if anyone compares the prefill and setup windows of greedy and sampled arms at microsecond scale.

**LOW-3: process-global RNG.** `mx.random.seed` sets MLX's global key. Reproducibility therefore assumes that nothing else draws from the global key between the seed and the first sample. The endpoint already documents sequential in-process turns. The reference-parity test confirms that `mlx_lm.stream_generate` and the adapter make no extra draws. If a future thermal, warmup or probe path ever ran MLX random ops concurrently, seeded streams would shift. This is not observed at present.

### Measurement-identity assessment

For runs that did not opt in (`sampler_policy=None`), the commit changes no token stream, no event bytes or ordering, no sampler provenance, no MLX call sequence and no RNG state. This was shown by executing parent, commit and lane side by side on two architectures. Opt-in runs add one `mx.random.seed` call (about 0.2 us) and build the sampler in setup. They are reproducible from the recorded `per_turn_seed`, independent of ambient RNG state.

### Observations outside the delta (not counted against this commit)

- **Pre-existing in parent and kept on purpose for byte identity: the legacy path leaks EOS on a sampler pin failure.** In the legacy path `_sampler_for_generation()` runs after `_suppress_eos()` but outside the `try/finally`. A pin failure (`AdapterFailure`) therefore leaves `tokenizer.eos_token_ids = set()` (probe 2.3). The opt-in path added by this commit builds its sampler before `_suppress_eos` and does not leak. Low impact, because a pin failure aborts the run. If it is fixed later, it needs a cited rebind and a byte-identity test.
- **Lane-head test failure in `tests.align.test_cache_checkpoint` (3 subtests, `unverified_xml_template:qwen3_5_moe`).** This is an integration conflict between the XML-family gate and the #657 hybrid-cache test fixture (`qwen35_122b_config.json`). It is unrelated to b29c25c59 and should go to the integration lane / WP5 CI-green owner.

## 4. Verdict

**ADMIT.** The opt-in sampling and seeding are correct and deterministic, and the input checks are tight. The legacy path is byte-identical to the parent. The LOW items are defence-in-depth notes and are not required fixes.

## 5. Proposed `configs/b6/executing_reviews.json` row

`test_audit_record_fixes` requires every new row's paper path to start with `/Users/edr/night-archive/`. The lead must copy this paper from `/private/tmp/jwsol/v4-retro-review-b29c25c59.md` to the archive path below before the row lands. The reviewer did not touch `night-*` paths.

```json
{
 "commit": "b29c25c59ad57787faae4e939578dea01c5682a6",
 "number_bearing_paths": [
  "joulewise/adapters/mlx_runtime.py"
 ],
 "change": "ALIGN pilot 4 build: opt-in seeded categorical sampling in pinned MLX adapter (Sol 6.1); retroactive review",
 "executing_reviews": [
  {
   "reviewer": "Opus 5.5, retroactive executing review (non-author), 2026-11-05",
   "covered": "b29c25c59^..b29c25c59 (joulewise/adapters/mlx_runtime.py hunks), re-executed at lane/2026-11-05-align-v4-integration c8ef6b2f6",
   "paper": "/Users/edr/night-archive/align-v4/retro-reviews/b29c25c59-opus-REPORT.md"
  }
 ]
}
```
