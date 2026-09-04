# Qwen3 `_v5` floor-generator fix round 1

Date: 2026-09-03  
Seat: Sol, implementation fix round 1  
Branch: `feat/2026-09-02-v5-floor-generator`  
Required head at intake: `4e742b5b554dca64e1db9c22396851ad2e42fb0e`  
Observed head at intake: `4e742b5b554dca64e1db9c22396851ad2e42fb0e`  
Disposition: **COMPLETE — focused verification green**

## Finding → cure → test

| Finding | Cure in both floor generators | Regression / closure test |
|---|---|---|
| PFP-001 | The bound prompt ladder must have exactly the eight issued top-level keys; its schema is `joulewise.g2a_prefill_prompt_ladder.v1`; its sentence is `PROMPT_SENTENCE`; and the selected rung's `prefill_tokens` and `repeat_count` must be non-boolean integers, with a positive repeat count. | A SHA-rebound `repeat_count: true` rung with a self-consistent method refuses; a SHA-rebound ladder missing `prompt_sentence` refuses. Both counterexamples run against ALPHA and BETA. |
| F1 | The SHA-verified selection record is parsed with duplicate-key/non-finite rejection. Its schema must be `joulewise.g2a_prefill_selection.v1`, status must be `selected` or `refused`, and `collection_prefill_tokens` must be 512. Each semantic mismatch has a named refusal code. | The fixture now carries the minimal valid three-field record. SHA-rebound wrong-schema and wrong-token records refuse in both generators with `selection_record_schema_version_invalid` and `selection_record_collection_prefill_tokens_mismatch`. |
| F4 | No production retyping was needed: each floor registration is required to stay exactly equal to the contrast generator's canonical registration. | Separate ALPHA and BETA tests assert `floor.dominance_criterion_registration() == contrast.dominance_criterion_registration()`. A temporary 1.99 mutant fails the assertion. |
| Report wording | The original seat text remains intact. A dated addendum corrects finding 5's authority wording and records the magistrate-required p42 provenance sentence verbatim. | Diff inspection confirms an append-only landing-report change. |

## Focused verification tail

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_d117_contrast_v5_pack
```

Final-head output tail:

```text
......................................
----------------------------------------------------------------------
Ran 38 tests in 10.531s

OK
```

`git diff --check` also exited 0 with no output.

## Refuter probe replay

The authority probes used fresh `TemporaryDirectory` bundles, rewrote the
bound JSON, and recomputed the bound SHA fields (plus the selection authority
record ID where applicable). The dominance probe copied the ALPHA generator
to a temporary tree, changed only the first registered threshold to `1.99`,
loaded that copy against the unchanged contrast generator, and ran the exact
object-equality assertion.

| Probe | ALPHA observation | BETA observation / test result |
|---|---|---|
| Boolean `repeat_count`, self-consistent `generation_method` | `REFUSED prefill_prompt_pin_invalid: prompt realization` | `REFUSED prefill_prompt_pin_invalid: prompt realization` |
| Ladder `prompt_sentence` deleted, SHA rebound | `REFUSED prefill_prompt_pin_invalid: prompt_ladder` | `REFUSED prefill_prompt_pin_invalid: prompt_ladder` |
| Wrong selection schema, SHA and record ID rebound | `REFUSED selection_record_schema_version_invalid` | `REFUSED selection_record_schema_version_invalid` |
| Dominance threshold `1.99` in a temporary copy | `test_threshold_1p99_is_caught ... FAIL` | Equality diff reports mutant `1.99` versus canonical `2.0`; `Ran 1 test`, `FAILED (failures=1)` |

Observed authority-refusal output:

```text
bool repeat_count [d117_floor_qwen3-1p7b_v5]: REFUSED prefill_prompt_pin_invalid: prompt realization
bool repeat_count [d117_floor_qwen3-8b_v5]: REFUSED prefill_prompt_pin_invalid: prompt realization
ladder prompt_sentence deleted [d117_floor_qwen3-1p7b_v5]: REFUSED prefill_prompt_pin_invalid: prompt_ladder
ladder prompt_sentence deleted [d117_floor_qwen3-8b_v5]: REFUSED prefill_prompt_pin_invalid: prompt_ladder
wrong selection schema [d117_floor_qwen3-1p7b_v5]: REFUSED selection_record_schema_version_invalid
wrong selection schema [d117_floor_qwen3-8b_v5]: REFUSED selection_record_schema_version_invalid
```

Observed threshold-mutant failing-test tail:

```text
test_threshold_1p99_is_caught (__main__.ThresholdMutationProbe.test_threshold_1p99_is_caught) ... FAIL

======================================================================
FAIL: test_threshold_1p99_is_caught (__main__.ThresholdMutationProbe.test_threshold_1p99_is_caught)
----------------------------------------------------------------------
AssertionError: ... 'threshold': 1.99 ... != ... 'threshold': 2.0 ...

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```

The first threshold-harness setup attempt derived `REPO_ROOT` from the shallow
temporary path and stopped during import on a missing temporary readiness
registry, before running the mutation assertion. The corrected harness pinned
the temporary module's read-only repository root to this checkout; the output
above is the actual mutation-test result.

## Scope and residual state

All repository writes stayed within the four paths in `WRITE_SCOPE`. No pack
generation, hardware collection, commit, push, merge, or out-of-scope
bookkeeping write was performed. Production pack generation remains gated on
the issued G2-a bundle under the magistrate ruling recorded in the landing
report.
