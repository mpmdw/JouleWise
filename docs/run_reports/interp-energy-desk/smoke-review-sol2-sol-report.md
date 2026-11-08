**HOLD.** Found isolation escapes, unenforced shutdown/deadline limits, and false-PASS gaps in packet and projection checks.

Changed only:

- [Witness tests](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-review-sol2/tests/align/test_smoke_review_sol2.py)
- [Review report](/Users/edr/code/CapstoneProject/jw-wt/sol-smoke-review-sol2/docs/align/v4/w1-smoke-review-sol2.md)

Committed locally as `9a2519def` and `8b62a9633` on `align/2026-11-08-w1-smoke-review-sol2`. Working tree clean; nothing pushed.

Separate `python3.13 -B -m unittest` runs:

| Module | Result |
|---|---|
| `tests.align.test_w1_prequal` | 34 tests; 2 meter failures |
| `tests.align.test_w1_smoke` | 19 OK |
| `tests.align.test_v4_prequal` | 36 OK; 3 skipped |
| `tests.align.test_smoke_review_sol2` | 14 tests; 13 intentional property failures |

Clean-clone PREQUAL with `--w1-next w1 --jobs 1` **failed in 440.3 seconds**. WP22 passed its full 20-test run with one existing expected failure.

The meter failures came from unavailable process enumeration: `pkill: Cannot get process list`. Native DC salvage remains unverified.

Next: repair isolation and cleanup first, settle projection-source schemas, then rerun the witnesses and native MBP smoke. Full commands, findings and limitations are in the report.