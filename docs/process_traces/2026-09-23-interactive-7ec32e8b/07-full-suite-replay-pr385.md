# 07 — Full-suite replay on PR #385 (branch chore/2026-09-23-codex-sol6-pin)

Run by the interactive Fable session on the branch worktree at 89d89396 (records included), `scripts/shard_tests.py --workers 8 --split`, machine shared with two consult seats and this session. Exact tail:

```
SHARD SUMMARY index=1/8 modules=1 tests=48 failures=0 errors=0 skipped=0 result=PASS
SHARD SUMMARY index=2/8 modules=34 tests=676 failures=0 errors=0 skipped=1 result=PASS
SHARD SUMMARY index=3/8 modules=34 tests=1009 failures=0 errors=0 skipped=2 result=PASS
SHARD SUMMARY index=4/8 modules=36 tests=951 failures=0 errors=0 skipped=46 result=PASS
SHARD SUMMARY index=5/8 modules=37 tests=945 failures=0 errors=0 skipped=4 result=PASS
SHARD SUMMARY index=6/8 modules=36 tests=1180 failures=0 errors=0 skipped=5 result=PASS
SHARD SUMMARY index=7/8 modules=36 tests=1212 failures=0 errors=0 skipped=11 result=PASS
SHARD SUMMARY index=8/8 modules=36 tests=849 failures=0 errors=1 skipped=34 result=FAIL
WORKERS SUMMARY shards=8 modules=250 tests=6870 failures=0 errors=1 skipped=103 failed_shards=8 result=FAIL
exit=1
```

## The one error

```
11800:ERROR: test_g4_real_ruled_census_pgrep_dialect (test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect) (pattern='powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)')
11801-G4 kills M10: a construct pgrep rejects or silently never matches.
11802-----------------------------------------------------------------------
11803-Traceback (most recent call last):
11804-  File "/Users/edr/code/JouleWise-wt-sol6/tests/test_arm_readiness_evidence_t0.py", line 2750, in test_g4_real_ruled_census_pgrep_dialect
11805-    reported = {int(line.split(" ", 1)[0]) for line in lines}
11806-                ~~~^^^^^^^^^^^^^^^^^^^^^^^
11807-ValueError: invalid literal for int() with base 10: 'import'
11808-
```

Cause (bench): the test runs the REAL ruled census (`pgrep -fl` dialect) against the live process table. This interactive session's own shell commands carried multi-line `python3 -c` programs in their argv, so one pgrep output line began with `import` where a pid was expected and the parser raised `ValueError`. Not caused by the diff. The same module re-run with no seat alive and no multi-line command in flight:

```

OK

```

## Lane handed to the magistrate: CENSUS-MULTILINE-ARGV-01

The census parser must tolerate a process whose argv contains newlines (continuation lines in `pgrep -fl` output): treat any line not starting with a pid as a continuation of the previous entry, and count that entry once. Today such a process makes the census RAISE instead of refuse or pass; at t0 that is a needless refusal, at a bench test a false failure. Regression: a fixture pgrep output with a two-line entry beginning `import`. Not claim-bearing; routine tier.
