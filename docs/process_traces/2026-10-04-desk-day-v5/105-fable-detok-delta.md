FINAL PASS: PASS

Cold, delta-limited final pass on PR #480 at `a668bdfe` (previous head `33b68dfd`, parent
`b2ff2f36`), Fable 5.1, 2026-10-05. Scope read: `git diff 33b68dfd..a668bdfe` (3 files, +82/−3),
the surrounding code in `joulewise/adapters/mlx_runtime.py`, the earlier ruling
`fable-detok.md`, and the installed mlx-lm 0.31.3 `tokenizer_utils.py`. Checkout untouched
(`git status --porcelain` empty at the end); scratch in `/tmp/dd5-fable-dt2/`. No Metal, no
powermetrics, no sudo, no launchctl, no model run. `mlx` was never imported by my probes.

F1, F2 and F4 are closed. The recorded tokenizer identity is byte-identical to the parent on
every path I could construct. The fix adds nothing inside a measured window. No blocking or
major finding; three notes below.

## Rulings on the earlier findings

### F1 (was BLOCKER) — CLOSED
- `tests/test_suite_control_parity.py:523-529` now pins the generator record with the new key
  spelled out exactly: `{"name", "version", "detokenizer": {"path": "fallback", "reason": "not_prepared"}}`.
  The comparison is still `assertEqual` on the whole record, so it was updated, not loosened.
- Evidence: `pytest tests/test_mlx_runtime_detokenizer.py tests/test_mlx_runtime.py tests/test_suite_control_parity.py`
  → `53 passed, 11 subtests passed` (was `1 failed, 50 passed`).
- The earlier ruling left open whether other tests pin the generator record exactly. I ran eight
  more files that touch the MLX adapter or its records: `test_mock_adapters`, `test_identity_pins`,
  `test_cli`, `test_analysis_inputs`, `test_gensuite`, `test_generate_g2a_probe_inputs`,
  `test_summarize_g2a_prefill_probe`, `test_d117_contrast_v5_pack` → `252 passed, 170 subtests passed`.
- Not run (time budget): `test_analysis_finalizer`, `test_arm_readiness_evidence_t0`,
  `test_d117_gamma_d139a2_families`, and the rest of the suite. These three mention the MLX
  adapter by name; the round-2 diff does not change any record they could see relative to
  `33b68dfd` except the tokenizer class going back to the parent value.

### F2 (was MAJOR) — CLOSED
- Mechanism: the local subclass carries a class attribute
  `_joulewise_tokenizer_identity_class = wrapper_class` (`mlx_runtime.py:361`), and
  `_tokenizer_identity` reads it with `vars(type(tokenizer)).get(...)` and records that class's
  `__name__` (`:1294-1301`). `vars(type(...))` looks only at the tokenizer's own class
  dictionary, so the lookup never goes through the wrapper's attribute forwarding to the
  Hugging Face tokenizer, and a tokenizer of any other class falls through to `type(tokenizer)`
  exactly as the parent did.
- Earlier probe rerun (`/tmp/dd5-fable-dt/probe_class.py`) on this checkout: optimized path
  `'class': 'TokenizerWrapper'`, fallback path `'class': 'TokenizerWrapper'` (was
  `PreparedTokenizerWrapper` on the optimized path).
- Byte comparison against the real parent source, not a simulation
  (`/tmp/dd5-fable-dt2/probe_parent_bytes.py`): I extracted `b2ff2f36:joulewise/adapters/mlx_runtime.py`
  to scratch, loaded it as a second module, and drove both adapters with the PR's fixtures. For
  each path I compared the JSON bytes (`sort_keys=True`) of the tokenizer record from the three
  places it is emitted — identity projection (`:395`), single-workload provenance (`:479`),
  suite provenance (`:557`) — plus the full identity projection, the full workload provenance
  with only `generator.detokenizer` removed, and the output artifacts.

  | path | live class at head | recorded class | byte-equal to parent (8 comparisons) |
  |---|---|---|---|
  | optimized (BPE, exact wrapper) | `PreparedTokenizerWrapper` | `TokenizerWrapper` | 8/8 |
  | fallback: unsupported detokenizer class | `TokenizerWrapper` | `TokenizerWrapper` | 8/8 |
  | fallback: custom wrapper subclass | `CustomWrapper` | `CustomWrapper` | 8/8 |
  | fallback: tokenizer that is not a wrapper | `LocalTokenizer` | `LocalTokenizer` | 8/8 |
  | unprepared (tokenizer injected, no `prepare()`) | `TokenizerWrapper` | `TokenizerWrapper` | 8/8 |

  Total mismatches: 0. So the only difference from the parent in any emitted record is the
  added `generator.detokenizer` key (and `detokenizer` in prepare metadata).
- Same check with the real mlx-lm 0.31.3 `TokenizerWrapper` and detokenizer classes, loaded in
  isolation (`/tmp/dd5-fable-dt2/probe_real_wrapper.py`): optimized (BPE), fallback
  (`NaiveStreamingDetokenizer`), and a forced construction failure. Parent and head tokenizer
  records are byte-equal on all three, and all three equal each other:
  `{"backend": "mlx", "class": "TokenizerWrapper", "identifier": ..., "revision": ..., "vocab_size": 3}`.
  The replacement object still passes `isinstance(..., TokenizerWrapper)`.
- The requested test exists: `tests/test_mlx_runtime_detokenizer.py:230`
  (`test_tokenizer_identity_matches_parent_on_optimized_and_fallback_paths`) asserts the record
  and its JSON bytes on parent-like, optimized and fallback adapters at all three emission sites.
- Consumers named in the earlier ruling (`identity_pins.py` receipt comparison, the analysis
  manifest arm pin, the determinism gate's `class` key) all read this record; since the record
  is now unchanged, the nine committed receipts pinning `"class": "TokenizerWrapper"` and the
  manifest pins stay valid. Read, not executed end to end against a real receipt, as before.
- Repo-wide search for another place that records the tokenizer's class name: only
  `scripts/axi_sc_spec_decode_spike.py:632`, which loads its own tokenizer and does not use
  this adapter.

### F4 (was LOW) — CLOSED
- `mlx_runtime.py:344-351`: the template construction is now inside `try/except Exception`; a
  failure records `{"path": "fallback", "reason": "detokenizer_construction_failed", "error": "<Type>: <message>"}`
  and returns with the original tokenizer left in place, so generation takes the parent's path.
- Evidence: `test_construction_failure_records_fallback_and_preserves_generation` (`:262`) passes,
  and my real-class probe with a tokenizer lacking `vocab` gave `prepare ok: True`, the live
  tokenizer still the original `TokenizerWrapper`, and the fallback record above.

## Anything new inside the measured windows — NO
- The `try/except` runs in `prepare()`, after `end_s` is taken (`:295`), so `load_wall_time_s`
  is unaffected, and before any generation phase exists.
- The identity lookup (one dictionary `.get` on the class) runs when the result record is
  assembled, after `_generate` has returned (`:449` then `:479`; `:557` after the suite control
  loop). It is not between any phase start/end pair.
- `_generate`, the event stream and the `detokenizer` property body are untouched by this delta.
  The class attribute adds nothing to the per-generation `copy.copy` + `reset()`: it lives on
  the class, not in the instance dictionary that is copied, and the object copied is the
  detokenizer, not the wrapper.
- Construction-failure path: generation tries the construction again inside prefill, as the
  parent would have. That is parent behaviour, and the path is recorded.

## F3 — I agree with accepting it as a recorded limitation
The determinism gate still projects the generator record to `name` and `version`
(`determinism_gate.py:629-632`), so it treats a fallback bundle and an optimized bundle as the
same generator. Text and token counts are identical on both paths; only prefill time and energy
differ (55–65 ms of construction on fallback). Accepting this is reasonable because the path is
written into every result (`generator.detokenizer.path`), so an analysis can refuse or split a
mixed set when it needs to. One condition I could not check: in this checkout the limitation is
not written down anywhere in tracked docs (a search for "detokenizer" outside code finds only
two August drafts). If the record lives in the PR body or a records file outside this commit, I
was not permitted to read it. If it is recorded nowhere, record it before the first window that
compares prefill energy across runs.

## Notes (not blocking)

### N1 — NOTE — the recorded `error` text can name the wrong cause
- Where: `mlx_runtime.py:349`, together with mlx-lm 0.31.3 `TokenizerWrapper.__getattr__`.
- Observed: when a detokenizer constructor raises `AttributeError`, Python retries the
  `detokenizer` property through the wrapper's `__getattr__`, which raises a second
  `AttributeError`. The record then reads
  `"AttributeError: 'TokenizerWrapper' object has no attribute '_detokenizer'"` whatever the
  real missing attribute was (seen in my real-class probe, where the true cause was a tokenizer
  without `vocab`). Other exception types are recorded faithfully. The `reason` field is still
  correct; only the free-text diagnosis can mislead.

### N2 — NOTE — the new identity test simulates the parent
- `tests/test_mlx_runtime_detokenizer.py:240` builds its "parent" by patching
  `_prepare_detokenizer` to a no-op. That is a fair stand-in, and my probe against the actual
  parent source agrees with it, but the test would not notice a future change to
  `_tokenizer_identity` itself, because both sides go through the same function. The hard-coded
  `expected` dictionary on `:232-238` is what really pins the value.

### N3 — NOTE — carried over from F5, unchanged by this delta
- Resident memory at the `prepare_end` snapshot includes the vocabulary map for the adapter's
  lifetime; the unsupported-detokenizer fallback still builds one detokenizer in `prepare()` and
  discards it. Neither is inside a measured generation phase.

## What was and was not verified
- Run and observed: the three earlier test files (53 passed); eight further files (252 passed);
  the earlier class probe; the parent-source byte comparison (5 paths × 8 comparisons, 0
  mismatches); the real mlx-lm wrapper probe (3 paths).
- Read, not executed: the receipt and manifest comparison sites; the position of the changed
  lines relative to phase events.
- Not done: the whole test suite; any run on real hardware or with a real model.
