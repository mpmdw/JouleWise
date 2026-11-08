**ADMIT-WITH-FIXES.** F6 retains smoke wrappers in lazily imported functions after prepare. Thread witnesses also demonstrate same-process interference. No new HOLD path was demonstrated in the fresh-process CLI; failed-main-arm exit 1 is consistent with its callers.

Changed files: [report](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-delta4-sol1/docs/align/v4/W1-SMOKE-DELTA4-sol1.md) and [witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-delta4-sol1/tests/align/test_smoke_delta4_sol1.py).

Using `TMPDIR=/private/tmp python3.13 -B -m unittest -v`:

- `tests.align.test_smoke_delta3_sol1`: 16 passed.
- `tests.align.test_smoke_delta3_sol2`: 15 passed.
- `tests.align.test_smoke_delta4_sol1`: 8 passed, 4 intentional finding assertions failed.

Compileall and whitespace checks passed. Total test time: 6.2 minutes.

Commits: `1b402857f`, `008c28f82`, on `align/2026-11-08-smoke-delta4-sol1`. Tree clean; nothing pushed.

Next: scope the F6 wrapper and rerun witnesses. In-process API support remains a lead question; native hardware validation remains unverified.