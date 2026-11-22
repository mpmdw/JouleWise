# Pointer timestamp grammar on Python 3.14

## Finding and fix

The pointer parser constrained offset syntax but delegated clock ranges to
`datetime.fromisoformat`. The existing malformed-timestamp test failed on
Python 3.14.6 with `ARM_ORDER` because the parser accepted `24:00:00`. The
new timestamp grammar test reproduced acceptance with a synthetic deadline
and failed on the same interpreter before the fix.

`scripts/gen_current.py` now checks clock ranges in the shared timestamp
grammar before calling `datetime.fromisoformat`. `run_state_items status`
and `run_state_add add` use the same function. Calendar checks, UTC bounds,
and conversion of valid timestamps retain the existing implementation.

## Verification

- The 32 `tests.test_gen_current.RenderTests` passed on Python 3.13.18 and
  3.14.6. The grammar table checks accepted epochs and `INVALID_TIME`
  refusals. The original regression also passed on both interpreters.
- A broader synthetic subset of 83 tests across `test_gen_current`,
  `test_run_state_items`, and `test_run_state_add` passed on both local
  interpreters. Direct CLI probes checked valid timestamps and exit 2 with
  `INVALID_TIME` for `24:00:00` and compact offsets. A rejected fixture add
  preserved the source and did not create an output.
- Local verification used synthetic fixtures. Standard GitHub CI runs the
  canonical shards. The path-filtered `gen-current-py314` workflow runs the
  synthetic rendering tests with Python 3.14 and no installed project
  dependencies.

## Handoff

Check the draft PR's CI results and route the Tier 1 cross-family review.
The draft gate ledger records verification that has yet to run.

`NEEDS_SPEC`: none for the timestamp grammar.
