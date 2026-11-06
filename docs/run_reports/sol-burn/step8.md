# Block 5 step 8: eliminate the duplicate finalization pass

Date: 2026-11-06.  Scope: synthetic fixtures only.  No experiment, custody,
archive, or restricted-data locator was accessed.

## Profile / static trace

The full S10 synthetic driver did not reach step 8 within this session, and no
checkpoint was present in the checkout or `/tmp`, so this is the permitted
static-path analysis plus a timed production-finalizer fixture.  Step 8 first
copies the dominance sidecar into finalization custody
(`joulewise/b5_analysis/dry_run.py:806-827`) and then invokes the finalizer
(`joulewise/b5_analysis/dry_run.py:1244-1271`).

Before this change, `scripts/finalize_analysis_manifest.py:main` always called
`_preflight_other_inputs` before `stage_dominance_replay_sidecar`.  The
preflight deliberately calls the complete finalizer with the sidecar omitted,
waits for the expected missing-sidecar refusal, and additionally repeats the
basis/floor/arm checks (`scripts/finalize_analysis_manifest.py:135-185`).  Main
then calls the complete finalizer again with the sidecar.  For step 8 the
sidecar is already below `custody_root`; staging authenticates it and returns
the same path without calling `_write_append_only`
(`scripts/finalize_analysis_manifest.py:98-105`).  Thus the first full pass
cannot protect a write in the production step-8 path.

## Change

`_sidecar_staging_can_write` classifies the existing distinction already made
by `stage_dominance_replay_sidecar`.  External sidecars retain the two-pass
write-before-validation protection exactly.  An already-custodied sidecar now
performs sidecar authentication followed by one complete finalization pass.
There is no memo across trust boundaries, no relaxed validation, and no output
construction change.

The focused tests prove both routes: an external locator still makes two calls
to `finalize_prospective_analysis_manifest_v3`, while a custodied locator makes
one; both pass the identical prebuilt `_block5_inputs` object to the final
call.  Predicate boundary tests cover inside/outside custody.  The existing
real CLI suite continues to cover append-only staging, malformed sidecars,
symlinks, occupied outputs, and refusal-without-custody behavior.

## Numbers

On this container, a one-shot `finalization_case` fixture timed in-process with
`time.perf_counter` took **3.768 s** with the old behavior forced by mocking the
new predicate to `True`, versus **2.399 s** on the new custodied path: **1.369 s
saved, 36.3% lower wall time, 1.57x throughput**.  Each run used a newly built
synthetic fixture and the real finalization implementation.  Absolute output
digests are not compared across those two timing fixtures because each fixture
has a different temporary custody path; equality is instead established at
the call boundary by the tests above and by the unchanged finalizer call.

This is a component measurement, not a full step-8 or under-90 projection.
The gain in a full S10 step depends on the share spent in the duplicated
finalizer pass; the optimization removes exactly one of two full finalizer
traversals while retaining sidecar validation and staging preparation.

## Verification

- `python3 -m unittest tests.test_finalize_analysis_manifest.Block5FinalizerContinuationTests`
  — 6 tests passed in 2.784 s.
- `python3 -m unittest tests.test_finalize_analysis_manifest.FinalizeSidecarCLITests.test_documented_finalize_stages_real_common_mode_sidecar`
  — 1 test passed in 11.415 s (13.550 s shell wall including interpreter/test startup).

