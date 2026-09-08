# 21g — Full-suite replays for PR #295 (ledger row 9)

Written 1788867571 2026-09-08 04:39:31 PDT by activation 784a764e. Logs excerpted verbatim under `21g-replays/` (full logs are ~7.6k lines each and
stayed in the activation's scratch). This PR is docs-only: `git diff --stat main...HEAD -- '*.py' tests/ joulewise/ scripts/` is empty.

## Replay 1 — stale branch head 82622e70 (superseded; kept for the record)
`21g-replays/replay-branch-82622e70-summary.txt`. Result FAIL: failures=4 errors=1 over 5269 tests. The branch was based on
d8ad6c15, BEFORE the T0-ACID-CLOCK-01 fix merged at e4ce8b3b, so `test_arm_readiness_evidence_t0…reaches_go` errored with the
exact pre-fix signature ("T-0 RAW anchor span exceeds 3600000000000 ns"). That is what row 9's "integration tree, not the stale
branch" clause exists for; origin/main (a969e526) was merged into the branch at 260f997b and the replay re-run.

## Replay 2 — integration head 260f997b (the evidence of record)
`21g-replays/replay-integration-260f997b-summary.txt`. Exact tail:

```
WORKERS SUMMARY shards=4 modules=206 tests=5271 failures=2 errors=0 skipped=109 failed_shards=3,4 result=FAIL
replay rc=1 end=2026-09-08 04:38:26
```

The two failures, both environmental and neither in a file this PR touches:

1. `test_paper_round7_artifacts.ReplayAgainstRetainedCorporaTests.test_both_producers_are_byte_identical` — the test runs
   `scripts/paper_excursion_decomposition.py` as a subprocess; that script globs `BACKUP_ROOTS`
   (`/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup`, script line 83–85), and directory access to that iCloud
   path blocks indefinitely on this machine tonight (5 s alarm probes time out; a stalled child showed 0.25 s CPU over 37 min with
   leaf frame `__opendir2 → __open_nocancel`). In both replays the lead terminated only its own stalled child after verifying
   ancestry to pid 83086 (`21b-rehearsal-20260909-bench/pass3-icloud-stall-integration-replay.txt`), which is what makes the test
   fail. The same module PASSED in joulewise-53's replay of PR #296 earlier tonight (its scratch log: `MODULE PASS
   tests.test_paper_round7_artifacts tests=67 … seconds=611.396`), when iCloud answered. Reported to joulewise-53 (tests lane).
2. `test_run_campaign.IdleAdmissionCoreVerdictTests.test_missing_final_attempt_telemetry_fails_closed` — load-sensitive. Same
   code as main. Under the full suite at load ~12 it failed (3 of the class's tests failed in replay 1, 1 in replay 2); the class
   alone on 260f997b failed 2 of 68 (`integration.log` excerpt in the summary file); the single test alone PASSED with
   `strict_valid: True, validation_problems: ()` (evaluate_member wrapped to print its verdict). joulewise-53's PR #296 replay
   passed the module (`MODULE PASS tests.test_run_campaign tests=281`).

Isolation run on the pre-merge head 50485a03 (`21g-replays/isolation-50485a03-tail.txt`, rc 1) reproduced the acid error and
the idle-admission flake before the merge; its purpose was classification only.

## Disposition
No failure is attributable to this PR. The iCloud stall and the idle-admission load sensitivity are environmental findings for
the code/tests lane (joulewise-53), recorded here so the receipt is honest; nothing in the arm-time sequence depends on either.
