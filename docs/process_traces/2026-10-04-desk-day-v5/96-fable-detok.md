FINAL PASS: FAIL

Cold final pass on PR #480 (`33b68dfd`, parent `b2ff2f36`), Fable 5.1, 2026-10-05.
Scope read: `git diff b2ff2f36..33b68dfd`, `joulewise/adapters/mlx_runtime.py`, installed
mlx-lm 0.31.3 `tokenizer_utils.py` and `generate.py::stream_generate`, and the consumers of
tokenizer/generator identity. Checkout untouched (`git status` clean); scratch in
`/tmp/dd5-fable-dt/`. No Metal, no powermetrics, no model run.

The mechanism itself is sound (questions 1 and 2 pass). The change fails on question 4: it
turns one existing test red and silently renames a pinned identity field.

## Findings

### F1 — BLOCKER — an existing test is red at this commit
- Where: `tests/test_suite_control_parity.py:523` (`SuiteControlParityTests::test_backend_outcomes_are_independently_pinned`),
  caused by `joulewise/adapters/mlx_runtime.py:544` (and `:466`).
- Evidence: `pytest tests/test_mlx_runtime_detokenizer.py tests/test_mlx_runtime.py tests/test_suite_control_parity.py`
  → `1 failed, 50 passed`. The test pins the generator record exactly:
  expected `{'name': 'mlx_lm.stream_generate', 'version': 'literal-mlx-1'}`, observed the same
  plus `'detokenizer': {'path': 'fallback', 'reason': 'not_prepared'}`.
- Why it matters: the PR adds a key to a record another test pins as exact, and did not update
  that test. I ran only these three files; other exact-shape pins on `workload_provenance.generator`
  outside them are not excluded by this pass.
- Second point from the same output: that test injects a tokenizer without calling `prepare()`,
  so the record says `not_prepared`. That value is honest, but the pinned test must be updated
  deliberately, not by loosening the comparison.

### F2 — MAJOR — the recorded tokenizer identity class is renamed on the optimized path
- Where: `joulewise/adapters/mlx_runtime.py:352` and `:364` replace `self._tokenizer` with an
  instance of a local subclass `PreparedTokenizerWrapper`; `_tokenizer_identity` at `:1288`
  records `type(tokenizer).__name__`. That record is emitted at `:385` (identity projection),
  `:469` and `:547` (workload provenance).
- Evidence (probe `/tmp/dd5-fable-dt/probe_class.py`, using the PR's own fixtures):
  - optimized path: `'class': 'PreparedTokenizerWrapper'`
  - fallback path:  `'class': 'TokenizerWrapper'`
  Before this change both were `TokenizerWrapper`.
- Consumers that compare this field:
  - `joulewise/identity_pins.py:2476-2477` — the live stack identity is compared for equality
    against the frozen receipt; a difference raises `readiness_identity_environment_dirty`.
    All 9 committed receipts (`configs/campaigns/*/identity_pin_projection.receipts/projection-0001.json`)
    pin `"class": "TokenizerWrapper"`. The four v5 packs have no committed receipt in this
    checkout, so the next mint would pin the new name instead.
  - `joulewise/analysis_engine/inputs.py:2912` — observed identity vs the manifest arm pin;
    a difference excludes the rows as `config_hash_mismatch`. Pins with `TokenizerWrapper`:
    `joulewise/analysis_manifest_v3.py:109,161`, `configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json`.
  - `joulewise/determinism_gate.py:88` — `class` is one of the tokenizer identity keys, so
    bundles from before and after this change disagree on tokenizer identity.
- Limits of what I verified: the rename itself is run and observed; the comparison sites are
  read, not executed end to end against a real receipt.
- Why it matters: the tokenizer did not change, but its recorded identity does, and it now
  also differs between the optimized and fallback paths. Nothing in the diff says this is
  intended, no pin was updated, and no new test asserts the tokenizer record at all.
- Smallest fix: keep the recorded class equal to mlx-lm's wrapper class (for example give the
  subclass the base class's `__name__`/`__qualname__`, or have `_tokenizer_identity` report the
  mlx-lm base class), and add a test asserting the tokenizer identity record is equal on the
  optimized and fallback paths. The path taken is already recorded under `generator.detokenizer`,
  which is the right home for it.

### F3 — LOW — the determinism gate does not see which detokenizer path a bundle took
- Where: `joulewise/determinism_gate.py:89,632` projects the generator record to `("name", "version")`.
- Effect: a bundle that fell back (55–65 ms of detokenizer construction inside prefill) and one
  that did not compare as identical generators. Text and token counts are the same either way;
  only prefill energy differs. If a mixed set must be refused, a consumer has to read
  `generator.detokenizer.path` explicitly. Not blocking.

### F4 — LOW — a failing detokenizer construction now escapes `prepare()` uncaught
- Where: `joulewise/adapters/mlx_runtime.py:344` (`template = self._tokenizer.detokenizer`) has no
  guard, unlike the `load` call above it, which returns a structured `AdapterResult`.
- Effect: an exception that used to surface during generation now propagates out of `prepare()`
  as a raw exception. Unlikely for the supported stack.

### F5 — NOTE — small shifts outside the measured windows
- `load_wall_time_s` does not move: `end_s` is taken at `:295`, before `_prepare_detokenizer()` at `:299`.
- The `prepare_end` memory snapshot (`:319`) is taken after the template is built, and the
  vocabulary map now lives for the adapter's lifetime instead of one generation, so resident
  memory at `prepare_end` rises by the size of that map.
- In the unsupported-detokenizer fallback, `prepare()` still builds one detokenizer and discards it.
- I did not trace whether the controller stamps or meters a phase around `prepare()`; if it does,
  the construction time moves into that phase.

## The four questions

1. **Work left inside prefill or decode — PASS.** `stream_generate` reads `tokenizer.detokenizer`
   once, on the first `next()`, after `phase_start prefill` (`generate.py:697`). On the optimized
   path that read is now a shallow copy plus `reset()`. Measured on the real mlx-lm 0.31.3
   `BPEStreamingDetokenizer` with a synthetic 151,643-entry vocabulary: about 4 microseconds
   (3.7–4.1 µs over 20,000 repetitions), against the 55–65 ms it replaces. The `isinstance`
   check at `generate.py:685` passes for the subclass, so no second wrapper is built. `_generate`
   is untouched: no event added, removed or reordered. The byte decoder table is built once per
   class, now in `prepare()`.

2. **State carried between generations — PASS.** `reset()` rebinds all four pieces of stream
   state (`offset`, `_unflushed`, `text`, `tokens`); the copy shares only `tokenmap`, which
   `add_token` and `finalize` read and never write, and the boolean `clean_spaces`. The base class
   declares `__slots__` while the BPE class also has a `__dict__`; `copy.copy` carries both
   (checked on the real class). Test (`/tmp/dd5-fable-dt/real_equiv.py`): 800 random token
   sequences across both `clean_up_tokenization_spaces` settings, including split multi-byte
   characters, buffered single spaces, out-of-range ids and a deliberately half-fed sibling copy;
   segments, final text, token list, offset and unflushed buffer all matched — 24 sequences against
   a freshly constructed detokenizer, the rest against a second reset copy; 0 mismatches; template
   state and map unchanged afterwards. The replacement wrapper copies every underscore field;
   non-underscore attributes live on the shared Hugging Face tokenizer. EOS suppression rebinds
   `_eos_token_ids` rather than mutating the set.

3. **Fallback honest and recorded — PASS, with F3.** Three fallback reasons
   (`tokenizer_api_unavailable`, `unsupported_tokenizer_wrapper`, `unsupported_detokenizer_class`)
   plus the `not_prepared` default are written to prepare metadata (`:314`) and both workload
   provenance sites (`:466`, `:544`); exact-class checks (`type(...) is`) keep subclasses on the
   old behavior. `cleanup()` resets the record (`:977`).

4. **Anything else stamped, timed or reduced that moves — FAIL.** F1 and F2.

## To pass
- Update `tests/test_suite_control_parity.py:523` for the new generator key (F1).
- Keep the recorded tokenizer class stable, or state the rename as intended and update every pin
  that carries it; add a test on the tokenizer identity record for both paths (F2).
