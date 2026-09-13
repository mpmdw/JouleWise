# Record 38 — full-suite replay on the follow-up merge candidate (ledger row 9 evidence, FINAL)

Tree `/Users/edr/code/JouleWise-wt-paper-n` @ 4cb214ad = main 76a2f2a7 + the follow-up branch. Command (lead, unpiped to `/private/tmp/claude-501/-Users-edr-code-JouleWise/5add607a-5532-41b4-8bc1-451a6a7aa48c/scratchpad/replay-4cb214ad.log`, venv Python 3.13.1): `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 scripts/shard_tests.py --workers 4 --split`, 17:14–17:54 PDT.

Exact tail:
```text
SHARD SUMMARY index=1/4 modules=52 tests=1037 failures=0 errors=0 skipped=7 result=PASS
SHARD SUMMARY index=2/4 modules=61 tests=1311 failures=0 errors=0 skipped=75 result=PASS
SHARD SUMMARY index=3/4 modules=59 tests=1952 failures=0 errors=0 skipped=18 result=PASS
SHARD SUMMARY index=4/4 modules=61 tests=1748 failures=1 errors=0 skipped=3 result=FAIL
WORKERS SUMMARY shards=4 modules=233 tests=6048 failures=1 errors=0 skipped=103 failed_shards=4 result=FAIL
REPLAY_RC=1
```

One failure, not caused by this branch: `tests.test_issue_calibration_acceptance_generation.DerivationChainSkeletonTests.test_window_exhausted_refuses_next_slot_and_aborts_once` asserts `"d03" not in str(python)` over a stringified command that embeds a random temporary directory; this run's directory was `tmpd03esrhb`. The assertion is a pre-existing fixture defect (substring over an arbitrary path), unrelated to the paper files this branch touches. Module re-run at the bench at the same head:
```text
Ran 114 tests in 57.168s

OK
```

Queued as FLAKY-TMPDIR-SUBSTRING-01 (assert on the recovered slot list, not on the whole command string). `FAIL:`/`ERROR:` census over the log: 1 (the flake above).
