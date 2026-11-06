# Block 5 STEP 5 — parallel mint authentication

Date: 2026-11-06 (UTC)

## Scope and evidence boundary

This change is code-and-synthetic-test work only. It did not open any experiment,
night-custody, night-archive, or restricted-data path. The starting attribution
(954 s of 1,205 s in driver CPU) is the operator-supplied measurement; it was not
re-measured in this checkout because this environment contains no experiment data.

## Changes

1. The generalized block-5 mint now schedules the two independent producer
authentication programs through the existing ordered `pack_map` process pool. Each
worker receives the already-loaded input manifest and the process-local producer
authority it needs. Successful results are consumed in pinset order; a failed or
untransportable worker is recomputed at that producer's original serial position.
Thus refusal order and partial authentication registration retain the serial
contract (`scripts/mint_floor_artifact_generalized.py`, `_authenticate_v2_inputs`
and `_authenticate_block5_pack`).
2. The driver loads the block-5 input manifest once before dispatch. Workers receive
that mapping directly (and expand it against their private producer capability)
rather than reopening the manifest. This
removes the per-producer manifest load without introducing a path-derived cache.
3. The run's success-only grammar-verdict memo is now one of the worker-shipped
memos, including when the verified derivation store is off. Only a consumed,
successful, deadline-clean outcome merges memo entries into the driver
(`joulewise/analysis_member_pool.py`).
4. An authentication session now memoizes path normalization. Repeated reads of
the same path retain all byte reads, hashes, strict-grammar checks/memo hits, and
read-count registration, but perform `Path.resolve(strict=False)` once per session
identity (`joulewise/authentication_io.py`). No archive containment check was
weakened.

## Equality and focused verification

All checks used repository synthetic fixtures.

* `python3 -m unittest tests.b5_analysis.test_pack_parallel tests.b5_analysis.test_producer_parallel tests.b5_analysis.test_small_fixes.SourcesManifestOncePerHandleTests tests.b5_analysis.test_auth_recorder_and_verdict_memo.MemoRegistration` — **PASS**, 18 tests. The pack tests compare workers=1 and workers=3 values, authentication records, grammar memo contents, first refusal, partial census, and deadline accounting with `assertEqual`.
* `python3 -m unittest tests.test_mint_floor_artifact_generalized tests.b5_analysis.test_frozen_files` — **PASS**, 87 tests, 2 skipped. This covers generalized mint authentication and frozen-source guards.
* `python3 -m py_compile scripts/mint_floor_artifact_generalized.py joulewise/analysis_member_pool.py joulewise/b5_analysis/archive.py joulewise/authentication_io.py` — **PASS**.

The new equality assertions specifically compare the serial and worker-shipped
grammar memo dictionaries, not merely their outputs. The path-normalization test
performs four authenticated reads, asserts one `Path.resolve`, and asserts the
registered read count remains four.
* `python3 -m unittest tests.b5_analysis.test_result_equivalence` — **PASS**, 90 tests, 4 skipped. This is the driver-level output/record equality suite.

* `python3 -m unittest discover -s tests` — **INCOMPLETE**. The canonical suite was interrupted after 13 minutes while a pre-existing long fiducial refit ran in `test_auth_capability_bridge`; it had also printed one failure before that point, but `unittest` had not yet emitted the failure identity. Focused equality and mint suites above completed green.
