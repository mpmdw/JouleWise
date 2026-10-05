# Block-4 lane X9 round 2 (Sol 6.1 high): adapt the legacy G10 tests to addendum D

Worktree: /Users/edr/code/JouleWise-wt-dd5-x9 (branch `lane/2026-10-05-b4-x9`, round 1 committed as 57944785). Scratch /tmp/dd5-x9/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal.

Round 1 (report `/Users/edr/night-archive/desk-day-v5/sol-x9-r1.md`) moved G10 after `a2`'s expiry check and before `s1`'s T-0, and added the measured-offset preflight. Its flag F1: the legacy G10 tests in `tests/test_t0_anchor_positive_control.py` and `tests/test_v5_block4_x1.py` (6 failures, 31 errors) encode the old `a1` placement. Their runners also do not handle the fixed R0 collector, and their fixtures lack the sizing and placement bindings.

Adapt them to the new contract:
- runners answer the preflight collector with a schema-true quorum inside the band;
- fixtures bind `a2` expiry and the `s1` boundary;
- sizing fixture support.

Do not weaken any refusal. A test that asserted the old placement now asserts the new one, and keeps an equivalent negative. First run both modules at the round-1 parent bda1c180 in a scratch clone or `git stash`-free copy (for example `git worktree add /tmp/dd5-x9/base bda1c180`). Report which failures were already present there, as the round-1 report hints for one test. Fix only what this lane changed, plus any baseline failure that is a stale fixture in these two files.

Run `tests.test_t0_anchor_positive_control tests.test_v5_block4_x1 tests.test_v5_block4_x9 tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 tests.test_v5_qualification_plan tests.test_v5_s1_qualification tests.test_harvest_v5_qualification tests.test_v5_block4_composed tests.test_v5_block4_clock`. Do not start the canonical suite. Finish in this turn.

WRITE_SCOPE: ["tests/test_t0_anchor_positive_control.py", "tests/test_v5_block4_x1.py", "tests/fixtures/v5_qualification/**"]
