# Synthetic continuation evidence

`test_epoch_continuation.py` builds disposable committed ledgers with
`tests.fixtures.epoch_bootstrap.build.build_derivation_ledger`. The continuation
JSON is produced by `issue_epoch_continuation.prepare-candidate` during each
test, then deliberately altered and resealed for authentication counterexamples
and the previously issued systematic-failure case. Only fixture byte pins are temporarily registered; acceptance bytes and
the issued acceptance registry remain unchanged.

The three `s9-*.json` witnesses were emitted independently by
`scripts/epoch_equivalence_check.py` in the S9 checkout for the same builder's
terminal twelve-slot session. Only `reference_envelope.acceptance_path` was
made repository-relative. PASS uses twelve `0.025` values; the level FAIL uses
one value one level-screen quantum above the operative and eleven exactly on
it; the bracket FAIL uses one value equal to level minus bracket minus
`0.000000000000001` and eleven exactly on the level screen. The tests derive
both comparators from the acceptance registry.

Run `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py`
for the expression cuts. They replace compiled function copies only, run one
killing test each, restore the original functions, and verify source-file
SHA-256 equality after each cut. These are synthetic software checks, not
live-night evidence.

The round-three cuts also remove the ledger completeness checks and required
anchor exclusion detail, restore the systematic-failure acknowledgment
exemption, and remove the preparer's systematic-night refusal. The completeness
counterexample starts from an honest nine-row FAIL and forges a six-row PASS;
the loader must refuse the three hidden finalized rows. Separate cuts cover
slot/attempt equality and observations missing from the session index.

`build.py` supplies the same tool-produced fixture to the writer and G2-a
integration tests. The writer CLI test installs a continuation pin only in
its disposable copied runtime and runs the synthetic sampler.

Run `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/writer_mutation_cuts.py`
for the writer, G2-a delegation and diagnostic-registration cuts. Each cut
runs one test in a subprocess, restores the exact source bytes in `finally`,
and checks all affected source SHA-256s before continuing. Run this command
alone, without another test run or writer using the checkout.
