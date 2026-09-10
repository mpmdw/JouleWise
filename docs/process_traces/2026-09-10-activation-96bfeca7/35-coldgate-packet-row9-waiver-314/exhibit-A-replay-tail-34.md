# 34 — PR #314 full-suite replay at final head beb808bc, alone, single process (no shards), started 05:52:48 PDT, finished 07:31:40 PDT 2026-09-10

Command: `cd /Users/edr/code/JouleWise-wt-ref-gate && git checkout -q --detach beb808bc && python3 -m unittest discover -s tests > replay-beb808bc.log 2>&1` (process rc recorded, not a pipeline).

```text
beb808bcc4d7d65f4648980c0c356f6dda6b5cb6
FAIL: test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce (test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce)
Ran 5668 tests in 5930.030s
FAILED (failures=1, skipped=109)
rc=1
```

The single failure is the pre-existing LOCAL-ONLY failure reproduced on a clean main checkout (078a13a4) on this host at 05:05 PDT (record 19 root cause: the controller fixture sleeps through its post-idle capture against a real deadline — the sleeping-sentinel class of PR #310 / consult 87 — so on a loaded host the capture times out); GitHub CI is green at main 078a13a4 and at the PR head beb808bc (18 jobs; only the gate-ledger job awaits the PR body). Cure lane FIXTURE-SENTINEL-CONTROLLER-01 registered (kernel branch bookkeeping/2026-09-10-kernel-lanes). Row-9 disposition: cold gate 35.
