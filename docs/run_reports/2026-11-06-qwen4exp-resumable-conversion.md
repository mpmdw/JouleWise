# Qwen4 experimental resumable canonical conversion — 2026-11-06

Base: `97d780d59` (`lane/2026-11-07-qwen4exp-mbp-live`). Scope: MISSING-9.

The canonical converter now maintains an atomic progress journal. It binds the
profile and conversion layout, pinned package versions, exact model module and
converter digests, and the complete input receipt. Completed weight shards and
completed PLE source-record spans carry chunked output digests plus the source
digests they consumed. Resume verifies those records, discards only an
unjournalled partial shard/span, and removes the journal before producing the
ordinary deterministic manifest.

Review fix (2026-11-06): `manifest.json` is now written atomically (sibling
`.tmp`, fsync, rename, directory fsync) before the journal is removed. An
interrupt between the two used to leave a complete manifest beside a
"running" journal; resume then hashed the old manifest (and any interrupted
`.tmp` journal) into the new inventory. Resume now removes leftover `.tmp`
files, and when `manifest.json` exists it checks the manifest's identity
(format, pins, profile, grouping, PLE format, module, digest scheme, inputs,
shard plan) and re-verifies every payload digest: a complete manifest is kept
and the journal removed; a partial one is rebuilt; a mismatch is refused.
The same check finishes an artifact whose journal was already removed (the
wrapper interrupted before its receipt). Test:
`ValidationRound1Test.test_converter_resume_finishes_a_written_manifest`.

The live wrapper exposes `convert --resume`. Only interruption-style exits
leave a resumable journal; an ordinary exception marks the journal failed, so
the existing preserve-and-use-a-new-artifact-name rule remains in force.

## Verification

- `python3 -m unittest tests.test_qwen4exp_mbp_live.SourceTests.test_conversion_preserves_recipe_and_writes_external_raw_sums tests.test_qwen4exp_mbp_live.SourceTests.test_conversion_resume_uses_existing_interrupted_artifact`: 2 passed.
- `python3 -m unittest tests.align.test_qwen4_exp_canonical`: 32 skipped because MLX is unavailable in the sandbox.
- `python3 -m unittest tests.test_qwen4exp_mbp_live`: 28 passed, 4 skipped, 1 environment error because numpy is unavailable.
- `python3 -m py_compile scripts/align_convert_qwen4_exp.py`: passed.
- `python3 -m unittest discover -s tests`: stopped manually after about nine
  minutes in a known long analysis test; before the stop it had reported one
  failure in the dependency-poor sandbox and the MLX group had skipped.

The lead must run on the pinned native Mac environment:

```sh
python3.13 -B -m unittest tests.align.test_qwen4_exp_canonical.CanonicalParityTest.test_converter_resume_is_byte_identical_at_every_durable_boundary
python3.13 -B -m unittest tests.test_qwen4exp_mbp_live
python3.13 -B -m unittest discover -s tests
```

The first command interrupts the tiny fixture after every completed shard/PLE
boundary and in the middle of a PLE record span, resumes each attempt, and
compares exact `manifest.json` bytes plus every output digest with a clean run.
